# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/led.c

## Purpose

`led.c` provides RTL8188EE software LED control for the rtlwifi LED framework. It turns the configured LED pin on or off by manipulating LEDCFG registers and maps high-level link/power LED actions to those pin operations.

## Important APIs And Functions

`rtl88ee_sw_led_on()` handles `LED_PIN_GPIO0` and `LED_PIN_LED0` by setting or clearing `REG_LEDCFG2` bit 7 depending on open-drain configuration; unsupported pins are ignored. `rtl88ee_sw_led_off()` reverses the operation and, for `LED_PIN_LED0`, writes a sequence that clears LED state and sets bit 3. `_rtl88ee_sw_led_control()` maps `LED_CTL_POWER_ON`, `LED_CTL_LINK`, and `LED_CTL_NO_LINK` to LED-on, maps `LED_CTL_POWER_OFF` to LED-off, and ignores TX/RX/site-survey/start-to-link/no-link variants. `rtl88ee_led_control()` is the public wrapper.

## Control Flow

Callers such as `hw.c` invoke `rtl88ee_led_control()` when media status, RF power state, or card disable state changes. The public wrapper selects the software LED path; the private dispatcher chooses on/off behavior from the action enum; the pin helpers write MMIO registers through `rtl_write_byte()` after reading current `REG_LEDCFG2` state where needed.

## State And Persistence Behavior

The persistent state is hardware LED configuration in `REG_LEDCFG2` and `rtlpriv->ledctl.led_opendrain`. The selected pin is stored in `rtlpriv->ledctl.sw_led0`, initialized elsewhere. There is no timer or blinking state in this file.

## Dependencies And Integration Points

The file depends on `wifi.h`, `reg.h`, `led.h`, `enum rtl_led_pin`, `enum led_ctl_mode`, and raw MMIO helpers. It is integrated by `hw.c` for init, media status, RF power state, and power-off LED updates.

## Risks And Test Signals

Unsupported LED actions intentionally no-op, so users expecting blink-on-traffic behavior will not see it here. Register semantics differ between open-drain and non-open-drain boards; wrong OEM/board configuration can invert LED behavior. Tests should verify LED on/off register writes for both open-drain modes, link/no-link/power-off action mapping, and no unintended register changes for ignored actions or unsupported pins.
