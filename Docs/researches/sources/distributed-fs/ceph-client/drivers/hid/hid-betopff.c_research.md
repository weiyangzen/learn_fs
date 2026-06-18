# sources/distributed-fs/ceph-client/drivers/hid/hid-betopff.c

Purpose: enables rumble force-feedback for several Betop gamepad/adaptor USB IDs whose output reports use separate bytes for left and right motors.

Important APIs/types/functions: `struct betopff_device` stores the selected output report. `hid_betopff_play()` maps 16-bit strong/weak magnitudes to bytes by dividing by 256 and writes field 2 and field 3 before `hid_hw_request(..., HID_REQ_SET_REPORT)`. `betopff_init()` finds the first input and output report, validates at least four fields with values, zeroes all report values, enables `FF_RUMBLE`, and registers a memless FF callback. `betop_probe()` optionally sets `HID_QUIRK_MULTI_INPUT` from `driver_data`, parses, starts HID with generic FF disabled, and calls `betopff_init()`.

Control flow: normal input devices are connected by `hid_hw_start(HID_CONNECT_DEFAULT & ~HID_CONNECT_FF)`. Custom FF setup occurs afterward and is intentionally not checked by probe; if FF initialization fails, the device still remains usable as an input device. Rumble calls only update the cached output report and issue a set-report.

State/persistence: the driver allocates one `betopff_device` per successful FF setup. Current rumble values persist in HID report fields and the device until changed. No sysfs or persistent configuration exists.

Dependencies/integration: uses HID report lists, input FF memless support, Linux input rumble effect format, and Betop vendor/product IDs.

Risks: the report layout is assumed rather than described by symbolic usages; if a matched adapter exposes a different first output report, field indexes 2 and 3 may be wrong. Probe ignores `betopff_init()` failure, so FF regressions may be silent except for logs. As with other memless FF drivers, allocation lifetime relies on input teardown.

Test signals: test all listed IDs in both adapter and controller modes, verify normal input remains available when FF setup fails, confirm strong/weak rumble drive field 2/3 independently, and inspect dmesg for "not enough fields" or "no values" errors.
