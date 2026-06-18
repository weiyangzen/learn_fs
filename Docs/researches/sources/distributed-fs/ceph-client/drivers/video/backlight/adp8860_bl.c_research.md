# sources/distributed-fs/ceph-client/drivers/video/backlight/adp8860_bl.c

## Purpose
This I2C driver controls ADP8860/ADP8861/ADP8863 WLED backlights and optional independent current-sink LEDs.

## Important APIs, types, and functions
`struct adp8860_bl` stores I2C client, backlight, optional LED array, platform data, lock, cached ALS max, revision, brightness, and feature flags. `struct adp8860_led` wraps LED classdev plus deferred I2C work. Main routines are SMBus helpers, `adp8860_led_probe/remove`, `adp8860_bl_set`, `adp8860_bl_setup`, ALS sysfs show/store functions, `adp8860_probe/remove`, and PM suspend/resume.

## Control flow
Probe validates SMBus byte-data support and platform data, reads manufacturer/revision, derives supported ambient/gdwn behavior, registers the backlight, optionally creates ALS sysfs attributes, initializes backlight sink assignments and comparator thresholds, enables standby/backlight/dim bits, updates brightness, and optionally registers independent LEDs. LED brightness writes run in workqueue context because I2C can sleep.

## State and persistence
Driver state tracks current brightness, cached daylight max, LED objects, feature flags, and register writes. Hardware ALS/backlight/LED registers persist until suspend/remove or reset.

## Dependencies and integration points
It depends on I2C SMBus, platform data definitions, the backlight core, LED class, workqueues, and PM. Kconfig selects LED support for this driver.

## Risks and test signals
Risks include platform-data-only configuration, LED/backlight sink assignment conflicts, partial LED registration unwind, unchecked return from optional `adp8860_led_probe`, sysfs writes with limited validation, and device variant feature differences. Test signals include all supported IDs, ALS on/off, LED registration conflicts, brightness 0/max/manual transitions, ambient zone sysfs, suspend/resume, and SMBus failure injection.
