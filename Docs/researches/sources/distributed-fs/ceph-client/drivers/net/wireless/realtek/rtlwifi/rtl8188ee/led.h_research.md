# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/led.h

## Purpose

`led.h` declares the RTL8188EE LED-control functions implemented in `led.c`.

## Important APIs

The exported functions are `rtl88ee_sw_led_on()`, `rtl88ee_sw_led_off()`, and `rtl88ee_led_control()`. The first two operate on a specific `enum rtl_led_pin`; the public control function accepts an `enum led_ctl_mode` and applies the driver’s action mapping.

## Control Flow, State, And Integration

The header has no executable flow or state. `hw.c` and the rtlwifi operation table use these declarations to control LEDs during init, link changes, RF state changes, and shutdown. State lives in `rtlpriv->ledctl` and the LEDCFG hardware register.

## Risks And Test Signals

The header’s main risk is prototype drift with `led.c` or the common rtlwifi LED ops interface. Compile tests and simple hardware LED action tests are sufficient coverage for this file.
