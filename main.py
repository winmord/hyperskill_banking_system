import random
import sqlite3


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
conn.commit()
card_id = int(0)


def get_luhn_checksum(number):
    card_digits = list(int(x) for x in number)
    for i in range(len(card_digits)):
        if i % 2 == 0:
            card_digits[i] *= int(2)
        if card_digits[i] > 9:
            card_digits[i] -= 9

    checksum = int(0)
    digits_sum = sum(card_digits)
    while (digits_sum + checksum) % 10 != 0:
        checksum += 1

    return checksum


class Card:
    def __init__(self):
        self.card_number = "400000"
        self.pin = ""
        self.balance = int(0)

    def create_card(self):
        for _ in range(9):
            self.card_number += str(random.randrange(0, 9))
        self.card_number += str(get_luhn_checksum(self.card_number))
        for _ in range(4):
            self.pin += str(random.randrange(0, 9))
        print("Your card has been created")
        print("Your card number:")
        print(self.card_number)
        print("Your card PIN:")
        print(self.pin)

    def set_card(self, number, card_pin, card_balance):
        self.card_number = number
        self.pin = card_pin
        self.balance = card_balance

    def verify_card(self, in_card_number, in_pin):
        return in_card_number == self.card_number and in_pin == self.pin


main_menu = """1. Create an account
2. Log into account
0. Exit"""

login_menu = """1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit"""

while True:
    print(main_menu)
    action = input(">")
    print()

    card = Card()

    if action == "0":
        print("Bye!")
        break
    elif action == "1":
        card.create_card()
        cur.execute('INSERT INTO card VALUES ({}, {}, {}, {})'.format(card_id,
                                                                      card.card_number,
                                                                      card.pin,
                                                                      card.balance))
        conn.commit()
        card_id += int(1)
        print()
    elif action == "2":
        print("Enter your card number:")
        card_number = input(">")
        print("Enter your PIN:")
        pin = input(">")
        print()
        cur.execute('SELECT * FROM card WHERE number = {}'.format(card_number))
        card_info = cur.fetchone()

        if not(card_info is None) and card_number == card_info[1] and pin == card_info[2]:
            card.set_card(card_info[1], card_info[2], card_info[3])
            print("You have successfully logged in!")
            print()

            while True:
                print(login_menu)
                login_action = input(">")
                print()

                if login_action == "5":
                    print("You have successfully logged out!")
                    print()
                    break
                elif login_action == "4":
                    cur.execute('DELETE FROM card WHERE number = {}'.format(card.card_number))
                    conn.commit()
                    print("The account has been closed!")
                    print()
                    break
                elif login_action == "3":
                    print("Transfer")
                    print("Enter card number:")
                    transfer_number = input(">")
                    if card.card_number == transfer_number:
                        print("You can't transfer money to the same account!")
                        print()
                        continue
                    if str(get_luhn_checksum(transfer_number[:len(transfer_number) - int(1)])) != transfer_number[-1]:
                        print("Probably you made a mistake in the card number. Please try again!")
                        print()
                        continue
                    cur.execute('SELECT id FROM card WHERE number = {}'.format(transfer_number))
                    if len(cur.fetchall()) == 0:
                        print("Such a card does not exist.")
                        print()
                        continue
                    print("Enter how much money you want to transfer:")
                    transfer_sum = int(input(">"))
                    if transfer_sum > card.balance:
                        print("Not enough money!")
                        print()
                    else:
                        card.balance -= transfer_sum
                        cur.execute(
                            'UPDATE card SET balance={} WHERE number = {}'.format(card.balance, card.card_number))
                        conn.commit()
                        cur.execute(
                            'UPDATE card SET balance=balance + {} WHERE number = {}'.format(transfer_sum,
                                                                                            transfer_number)
                                    )
                        conn.commit()
                        print("Success!")
                        print()
                elif login_action == "2":
                    print("Enter income:")
                    income_sum = int(input())
                    card.balance += income_sum
                    cur.execute('UPDATE card SET balance={} WHERE number = {}'.format(card.balance, card.card_number))
                    conn.commit()
                    print("Income was added!")
                    print()

                elif login_action == "1":
                    print("Balance: {}".format(card.balance))
                    print()
                elif login_action == "0":
                    action = "0"
                    break
                else:
                    continue
        else:
            print("Wrong card number or PIN!")
            print()

        if action == "0":
            print("Bye!")
            break
    else:
        continue
