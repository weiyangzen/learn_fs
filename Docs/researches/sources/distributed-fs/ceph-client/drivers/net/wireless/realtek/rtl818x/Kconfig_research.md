# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/Kconfig

## Purpose

`rtl818x/Kconfig` declares the legacy Realtek 818x mac80211 drivers: PCI/CardBus `RTL8180` for RTL8180/8185/8187SE and USB `RTL8187` for RTL8187/8187B, plus optional LED support for RTL8187.

## Important APIs, Types, and Functions

Symbols are `RTL8180`, `RTL8187`, and `RTL8187_LEDS`. `RTL8180` depends on `MAC80211 && PCI` and selects `EEPROM_93CX6`; `RTL8187` depends on `MAC80211 && USB` and also selects `EEPROM_93CX6`; `RTL8187_LEDS` is a bool enabled when LED class and mac80211 LED support are compatible.

## Control Flow

Selecting either driver exposes build rules under `rtl818x/`. Help text documents representative hardware and warns that Linksys WUSB54GC variants map to different drivers depending on revision.

## State and Persistence Behavior

Persistent state is the kernel config selection. Runtime driver behavior is in the selected child modules, not this file.

## Dependencies and Integration Points

The file links the rtl818x family to mac80211, PCI/USB buses, and the 93cx6 EEPROM helper. LED support is conditional on `MAC80211_LEDS` and `LEDS_CLASS` linkage mode.

## Risks and Edge Cases

The broad device descriptions can invite selecting the wrong driver for similarly branded hardware. `RTL8187_LEDS` has a linkage constraint so built-in/module combinations should be checked when changing dependencies.

## Test Signals

Use config combinations for built-in and modular `RTL8180`, `RTL8187`, `MAC80211_LEDS`, and `LEDS_CLASS`; confirm `EEPROM_93CX6` is selected and no unmet dependency warnings appear.
