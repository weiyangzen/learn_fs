# sources/distributed-fs/ceph-client/drivers/hwmon/applesmc.c

## Purpose
This platform hwmon driver talks directly to Apple SMC I/O ports on Intel-based Apple machines. It exposes SMC key metadata, temperatures, fan control, accelerometer input, ambient light, and keyboard backlight control where the machine supports those keys.

## Important APIs, Types, And Functions
The global `smcreg` structure caches SMC key count, fan count, temperature key index, feature flags, and an array of `struct applesmc_entry` records containing key, length, type, flags, and validity. Low-level transport is implemented by `wait_status()`, `send_byte()`, `send_command()`, `read_smc()`, and `write_smc()` against ports `0x300` and `0x304`. Public internal key helpers are `applesmc_get_entry_by_index()`, `applesmc_get_entry_by_key()`, `applesmc_read_key()`, `applesmc_write_key()`, and `applesmc_read_s16()`.

Subsystem-facing functions include dynamic sysfs node creation through `applesmc_create_nodes()`, fan speed/manual handlers, temperature label/input handlers, input polling via `applesmc_idev_poll()`, LED keyboard backlight handling via `applesmc_brightness_set()` and a workqueue, and PM resume/restore hooks.

## Control Flow And State
Module init first requires a DMI whitelist match, claims the SMC I/O region, registers a platform driver/device, initializes the SMC register cache with retry, creates info/fan/temp sysfs files, then conditionally creates accelerometer, light sensor, keyboard backlight, and hwmon device resources. `applesmc_init_smcreg_try()` reads `#KEY`, allocates or refreshes the cache, discovers fan count, binary-searches key ranges for temperature keys, and checks feature keys.

Runtime operations serialize SMC I/O with `smcreg.mutex`. Key metadata is lazily cached by index. Temperature index state and feature flags persist for the module lifetime. Backlight brightness is remembered in `backlight_state` and re-written on resume. Accelerometer calibration stores `rest_x/rest_y` in memory only. Sysfs `key_at_index` is a global selector for several metadata files.

## Dependencies And Integration Points
The driver uses raw x86 I/O port access, DMI matching, platform devices, hwmon legacy registration, hwmon sysfs attributes, input polling, LED class devices, workqueues, and PM callbacks. It is not a normal discoverable bus driver; the DMI whitelist and I/O port reservation gate loading.

## Risks
The driver is highly timing-sensitive and depends on undocumented SMC status behavior. Global singleton state means one device instance is assumed. Dynamic sysfs creation has many staged failure paths, so cleanup ordering is important. The light sensor data length is cached in a static local and assumes the left/right formats remain compatible. Fan writes and keyboard backlight writes directly affect platform hardware.

## Test Signals
Important tests are DMI rejection, I/O region conflict handling, SMC command timeout/error paths, key-cache lookup and binary-search bounds, dynamic sysfs creation cleanup failures, temperature key enumeration, fan manual/output writes, accelerometer input registration and calibration, LED workqueue behavior, and resume restoring keyboard backlight state.
