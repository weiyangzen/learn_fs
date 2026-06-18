# sources/distributed-fs/ceph-client/drivers/video/backlight/adp8870_bl.c

## Purpose
This I2C driver supports ADP8870 WLED backlight control, five-zone ambient-light adjustment, PWM assignment, and optional independent LED sink registration.

## Important APIs, types, and functions
`struct adp8870_bl` contains client, backlight, optional LED array, platform data, lock, cached daylight max, revision, and current brightness. `struct adp8870_led` represents LED class devices with workqueue-backed I2C updates. Key functions include `adp8870_read/write/set_bits/clr_bits`, `adp8870_led_probe/remove`, `adp8870_bl_set`, `adp8870_bl_setup`, ALS sysfs accessors, `adp8870_probe/remove`, and PM callbacks.

## Control flow
Probe validates SMBus byte-data, platform data, and manufacturer ID, registers a raw backlight, optionally creates ALS sysfs attributes, programs sink selection, PWM selection, five brightness/dim levels, trip/hysteresis thresholds, comparator control, fade law/rates, and enables standby/backlight/dim mode. Brightness below max disables comparator auto mode and writes manual max current; max restores cached daylight max and reenables auto mode. Optional LEDs are registered after backlight setup.

## State and persistence
Runtime state records cached brightness and daylight max plus optional LED state. Hardware register programming persists until removal, suspend, or chip reset. LED brightness updates are deferred through work structs.

## Dependencies and integration points
It integrates with I2C SMBus, backlight core, LED class, platform data, sysfs, and PM. It exposes module/device tables for I2C matching.

## Risks and test signals
Risks include large platform-data surface, unhandled return from optional LED probe, sink conflicts, sysfs writes without strong range checks, and revision-specific `GDWN_DIS` behavior. Test signals include manufacturer mismatch, five ALS zones, PWM assignment, LED conflict/unwind, brightness 0/manual/max, suspend/resume, and I2C fault injection.
