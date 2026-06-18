# sources/distributed-fs/ceph-client/drivers/leds/blink/leds-lgm-sso.c

## Purpose
This platform driver supports the Intel Lightning Mountain Serial Shift Output controller as both a GPIO provider and an LED provider. It can drive up to 32 serial outputs, expose some pins as GPIOs, register LED class devices, and configure hardware blink or hardware-triggered outputs.

## Important APIs, Types, and Functions
Core structures are `struct sso_led_priv`, `struct sso_gpio`, `struct sso_led`, and `struct sso_led_desc`. LED callbacks include `sso_led_brightness_set()`, `sso_led_brightness_get()`, and `sso_led_blink_set()`. GPIO callbacks include `sso_gpio_request()`, `sso_gpio_free()`, `sso_gpio_dir_out()`, `sso_gpio_get()`, and `sso_gpio_set()`. Hardware setup is handled by `sso_gpio_hw_init()`, `sso_gpio_freq_set()`, `sso_register_shift_clk()`, `sso_init_freq()`, and `sso_led_hw_cfg()`. Probe/remove are `intel_sso_led_probe()` and `intel_sso_led_remove()`.

## Control Flow
Probe obtains `sso` and `fpid` clocks, enables them with a devm cleanup action, obtains a syscon regmap, initializes GPIO hardware and a gpiochip, initializes frequency tables, parses a named `ssoled` child node, and registers LED children. LED children require a GPIO descriptor and `reg`; optional properties set default trigger, suspend/shutdown retention, panic indicator, hardware blink, hardware trigger, blink rate, and default state. Brightness writes update the duty-cycle register and either drive the GPIO output or let hardware trigger state control the pin. Blink requests quantize delay to the closest supported controller frequency and enable the pin in `SSO_CON2`.

## State and Persistence
Runtime state is in `sso_led_priv` and linked `sso_led` objects. LED descriptor fields cache brightness, blink rate, selected frequency index, retention flags, and whether hardware blinking is currently active. GPIO allocation is tracked in `alloc_bitmap`. Nothing is persistent beyond the device binding, but `retain-state-*` flags influence LED core suspend/shutdown behavior.

## Dependencies and Integration Points
The driver uses clocks, syscon/regmap, GPIO consumer and provider APIs, firmware node LED properties, LED class registration, and platform OF matching for `intel,lgm-ssoled`. It registers a gpiochip named `lgm-sso` and LED class devices under device name `lgm-sso`.

## Risks and Edge Cases
The SSO controller has grouped blink encoding: group 0 pins do not get per-pin blink rate programming in `sso_led_freq_set()`. The code calls `regmap_exit()` on a syscon regmap in error/remove paths, which is unusual for regmaps not allocated by the driver and should be reviewed carefully against syscon lifetime rules. `gptc_clkrate` is set after `sso_init_freq()`, so GPTC-derived entries initially use zero unless later corrected by hardware defaults. LED parse errors unwind already registered LEDs, but list iteration during shutdown must remain safe. GPIO and LED users can contend for the same pins, so `alloc_bitmap` and firmware reservations matter.

## Test Signals
Validate gpiochip registration, GPIO output set/get, LED brightness, hardware blink rates, hardware-triggered LEDs, and retention flags. Test firmware with `ngpios`, `intel,sso-update-rate-hz`, `ssoled` children, invalid `reg`, and overlapping GPIO/LED pins. Suspend/resume and remove should leave clocks disabled and no registered LEDs or GPIOs dangling.
