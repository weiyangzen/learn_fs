# sources/distributed-fs/ceph-client/drivers/leds/leds-wm8350.c

Purpose: LED class driver for WM8350 current-sink LEDs. It maps LED brightness to a hardware current-limit table and manages the ISINK and DCDC regulators needed to drive the LED.

Important APIs, types, and functions: the `isink_cur[]` table lists supported current levels. `wm8350_led_enable()` enables ISINK then DCDC; `wm8350_led_disable()` disables DCDC then ISINK and attempts rollback on ISINK disable failure. `wm8350_led_set()` scales `LED_FULL` brightness to `max_uA_index`, sets current limit, and enables/disables supplies. Probe validates platform data, gets regulators, computes max current index, and registers the LED.

Control flow: probe requires `wm8350_led_platform_data`, obtains `led_isink` and `led_vcc`, initializes classdev name/default trigger/suspend flag, detects current enabled state, computes the nearest supported max current, and registers. Brightness off disables regulators; nonzero brightness updates current and enables power.

State and persistence: `enabled` tracks regulator state, and `value` stores current brightness under `value_lock`. Shutdown forces off and disables supplies. Remove unregisters and disables.

Dependencies and integration points: WM8350 PMIC platform data, regulator framework, LED class, platform device lifecycle.

Risks and test signals: validate max current boundary handling, regulator enable/disable rollback paths, current index scaling at low brightness, suspend/resume flag behavior, shutdown off behavior, and platform-data absence.
