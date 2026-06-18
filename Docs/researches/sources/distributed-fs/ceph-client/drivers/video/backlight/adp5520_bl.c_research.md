# sources/distributed-fs/ceph-client/drivers/video/backlight/adp5520_bl.c

## Purpose
This platform driver controls ADP5520/ADP5501 WLED backlights behind the ADP5520 MFD and optionally exposes ambient-light-zone tuning registers through sysfs.

## Important APIs, types, and functions
`struct adp5520_bl` stores the parent MFD device, platform data, a sysfs lock, cached daylight maximum, device id, and current brightness. Main functions are `adp5520_bl_set`, `adp5520_bl_get_brightness`, `adp5520_bl_setup`, `adp5520_show/store`, `adp5520_bl_probe`, `adp5520_bl_remove`, and PM suspend/resume handlers. Backlight ops implement update and get brightness.

## Control flow
Probe requires platform data, registers a raw backlight, creates ALS sysfs attributes when ambient sensing is enabled, programs daylight/office/dark max and dim thresholds, configures comparator/fade/control registers, enables the backlight in dim mode, and updates brightness. Manual brightness below max disables auto ambient adjustment and writes `DAYLIGHT_MAX`; max brightness restores cached daylight max and enables auto adjustment.

## State and persistence
The cache tracks daylight max while sysfs can mutate ALS registers. `current_brightness` tracks dim transitions. Hardware register settings remain in the PMIC until reprogrammed or reset.

## Dependencies and integration points
It depends on the ADP5520 MFD helper API, platform data, the backlight class, sysfs attributes, and PM callbacks.

## Risks and test signals
Risks include OR-accumulated register errors hiding the first failure source, sysfs values without range validation, missing platform data, and cache/register divergence for daylight max. Test signals include ALS enabled/disabled probe paths, sysfs read/write for all six attributes, suspend/resume, brightness zero/manual/max behavior, and MFD read/write fault injection.
