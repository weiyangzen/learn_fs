# sources/distributed-fs/ceph-client/drivers/leds/leds-da903x.c

Purpose: legacy platform-data LED/vibrator driver for Dialog/Marvell DA9030 and DA9034 PMIC MFD children.

Important APIs/types/functions: `struct da903x_led` stores LED class device, parent MFD device, PMIC id, and platform flags. `da903x_led_set()` maps LED ids to PMIC registers and brightness encodings. Probe consumes `struct led_info` platform data, validates `pdev->id`, registers the classdev on the parent, and stores driver data.

Control flow: brightness writes branch by DA9030/DA9034 id. DA9030 LED outputs encode enable and inverted 3-bit PWM; DA9030 vibrator toggles a misc-control enable bit. DA9034 LEDs scale `LED_FULL` to a 0x5f range and optionally apply ramp flag; DA9034 vibrator writes the raw even brightness value. Remove unregisters the classdev.

State and persistence: no software cache beyond id/flags. Hardware register state persists until overwritten or PMIC reset. No devm classdev registration is used, so unregister is explicit.

Dependencies/integration: depends on DA903x MFD register access via `da903x_write()`, platform ids from DA903x headers, and board platform data for names/triggers/flags.

Risks: probe silently returns success when platform data is missing, yielding no LED. Brightness scaling and bit inversions are chip-specific. Invalid platform ids fail. No locking is local, relying on parent MFD access serialization.

Test signals: platform-device id coverage for each DA9030/DA9034 output, register-value checks for OFF/ON/PWM extremes, missing platform data behavior, and unregister on remove.
