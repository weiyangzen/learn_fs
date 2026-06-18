# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/led.h

## Purpose
`led.h` exposes the RTL8192EE LED control functions to the rest of the chip driver.

## Important APIs, Types, And Functions
It declares `rtl92ee_sw_led_on`, `rtl92ee_sw_led_off`, and `rtl92ee_led_control`, all operating on `struct ieee80211_hw` and using rtlwifi LED enums.

## Control Flow
There is no implementation here. Callers use direct pin-level on/off functions when they know the LED pin, or `rtl92ee_led_control` for high-level LED actions.

## State And Persistence Behavior
The header stores no state. State is in `rtlpriv->ledctl` and GPIO registers managed by `led.c`.

## Dependencies And Integration Points
It requires the includer to know `struct ieee80211_hw`, `enum rtl_led_pin`, and `enum led_ctl_mode`. It is included by `hw.c` and `led.c`.

## Risks
The narrow declaration surface is low risk, but any signature change must be coordinated with driver ops and callers.

## Test Signals
Build success and LED action smoke tests through `rtl92ee_led_control` cover this header.
