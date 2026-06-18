# sources/distributed-fs/ceph-client/drivers/leds/leds-gpio.c

Purpose: generic GPIO-backed LED provider supporting firmware-node children and legacy platform data, including optional platform hardware blink callbacks.

Important APIs/types/functions: `struct gpio_led_data` stores classdev, GPIO descriptor, sleep capability, blink state, and optional blink function. `create_gpio_led()` configures LED metadata, default state, flags, GPIO direction, classdev registration, and per-LED pinctrl. `gpio_leds_create()` parses DT/ACPI child nodes. `gpio_led_get_gpiod()` handles platform-data descriptor, lookup, and legacy GPIO-number paths. `gpio_led_shutdown()` turns off LEDs unless retain-at-shutdown is set.

Control flow: probe chooses platform-data flow when `pdata->num_leds` exists; otherwise it parses child nodes. Brightness callbacks use atomic or sleepable GPIO setters based on `gpiod_cansleep()`. If hardware blink is active, the next brightness set first cancels blinking through the platform callback.

State and persistence: state is GPIO output level and `blinking` flag. Default state can be ON, OFF, or KEEP. LED core flags drive suspend/resume, panic indicator, and shutdown retention. Devm registration and GPIO acquisition manage lifetime.

Dependencies/integration: GPIO descriptor and legacy GPIO APIs, property/fwnode APIs, pinctrl default selection, LED class, OF compatible `"gpio-leds"`, optional board `gpio_blink_set`.

Risks: platform-data errors for one LED can abort the entire probe, while unavailable legacy GPIOs are skipped. Hardware blink semantics depend on board callback. Default state KEEP requires readable GPIO state. Shutdown unconditionally calls `gpio_led_set()` for non-retained LEDs.

Test signals: DT and platform-data probing, active-low handling, sleepable vs non-sleepable GPIO paths, default-state keep/on/off, blink cancellation, pinctrl warnings, panic/suspend/shutdown flags.
