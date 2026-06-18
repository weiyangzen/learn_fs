# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/led.h

## Purpose
Declares the RTL8723BE LED-control functions implemented in `led.c`.

## Important APIs, Types, And Functions
The exported API consists of `rtl8723be_sw_led_on()`, `rtl8723be_sw_led_off()`, and `rtl8723be_led_control()`. The first two operate on explicit `enum rtl_led_pin`; the dispatcher accepts higher-level `enum led_ctl_mode`.

## Control Flow
No control flow in the header. It allows `hw.c` and operation-table setup code to call LED functions for power and link events.

## State And Persistence
No state is stored. Implementations mutate LED hardware registers and `rtlpriv->ledctl`-selected pins.

## Dependencies And Integration Points
Depends on rtlwifi/mac80211 hardware and LED enums. Included by `hw.c` and `led.c`.

## Risks
Prototype mismatch would break LED callback binding. Pin-mode semantics remain in implementation and board data, not in the header.

## Test Signals
Build success and successful link/power LED callback execution are sufficient header-level signals.
