
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/led.c

Purpose: Implements basic software LED register manipulation and LED-action filtering for RTL8192CU USB devices.

Important APIs/functions: `rtl92cu_sw_led_on()` writes `REG_LEDCFG2` for `LED_PIN_LED0` and `LED_PIN_LED1`; `LED_PIN_GPIO0` is a no-op. `rtl92cu_sw_led_off()` writes off-state bits, honoring `rtlpriv->ledctl.led_opendrain` for LED0. `rtl92cu_led_control()` currently filters LED actions when RF is off for reasons stronger than power save, then logs the action without state-machine blinking behavior.

Control flow: LED on/off read the current LED config byte, mask the nibble associated with the selected LED, and write back hardware-specific bit combinations. `led_control` returns early for TX/RX/survey/link/power-on actions when RF-off reason indicates the device should not show active state.

State and persistence: Writes persistent LED config registers until changed or power-cycled. Reads `led_opendrain` set by HP/OEM customization in `hw.c` and `ppsc->rfoff_reason`.

Dependencies/integration: Wired into `.led_control` in `sw.c`; direct on/off helpers are available through `led.h`. Depends on `../usb.h`, `REG_LEDCFG2`, `enum rtl_led_pin`, and `enum led_ctl_mode`.

Risks: `rtl92cu_led_control()` does not call on/off helpers, so link/TX/RX blinking may be intentionally unimplemented or handled elsewhere. Incorrect open-drain handling can invert or leave LEDs stuck on certain HP boards. GPIO0 is unsupported here.

Test signals: Manual LED tests on normal and HP open-drain devices, RF-off action suppression checks, and register trace verification for LED0/LED1 on/off paths.
