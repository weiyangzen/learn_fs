# sources/distributed-fs/ceph-client/drivers/leds/leds-max8997.c

Purpose: LED class driver for MAX8997 flash/movie LEDs under the MAX8997 MFD.

Important APIs/types/functions: `struct max8997_led` stores parent device, LED class device, enable flag, platform ID, mode, and mutex. `max8997_led_set_mode()` programs flash/movie/pin-control mode and max brightness. `max8997_led_enable()` toggles boost. `max8997_led_set_current()` writes mode-specific current registers. `mode` sysfs attribute exposes mode selection.

Control flow: probe uses `pdev->id` as LED number, names the LED, installs brightness and mode sysfs handlers, applies platform-data mode/brightness if present, initializes mutex, and registers the LED. Brightness writes set current and boost enable for nonzero values, or current zero and boost off for zero.

State and persistence: software caches `enabled` and `led_mode`; hardware current, mode, and boost bits live in MAX8997 registers. Platform data can define initial state.

Dependencies and integration: depends on MAX8997 MFD/private register helpers, platform data, LED class, and sysfs attribute groups.

Risks: brightness callback is non-blocking but performs I2C register updates and has no mutex around brightness path, while mode sysfs uses a mutex. `name` is a stack buffer assigned to `cdev.name` before registration; LED core must copy or use it immediately, otherwise this would be unsafe. Unsupported mode leaves max brightness zero.

Test signals: mode sysfs strings, current register programming per mode and LED ID, boost enable transitions, platform-data initial mode/brightness clamping, and concurrent mode/brightness operations.
