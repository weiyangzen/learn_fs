<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-input.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-input.c

Purpose: This file exposes the Apple Motion Sensor as an optional polled input device that behaves like a three-axis joystick.

Important APIs and state: Module parameters `joystick` and `invert` control default enablement and X/Y inversion. `ams_input_enable()` allocates and registers a polled input device. `ams_idev_poll()` reads calibrated sensor values and reports ABS_X/Y/Z. A sysfs `joystick` attribute enables or disables the input device at runtime. `ams_input_mutex` serializes enable/disable.

Control flow: On enable, the code reads current sensor values under `ams_info.lock` and stores them as calibration offsets, allocates an input device with parent `ams_info.of_dev`, sets abs ranges and polling interval 25 ms, registers it, stores it in `ams_info.idev`, and sets global `joystick=true`. Polling reads current oriented axes, subtracts calibration, optionally inverts X/Y, reports ABS axes, and syncs. Exit removes the sysfs file and disables the input device under the mutex.

State and persistence: Input enablement and inversion are module-parameter/global state. Calibration offsets persist while the input device is active and are recalculated on each enable. There is no persistent calibration storage.

Dependencies and integration: It depends on AMS core callbacks/lock, Linux input polling APIs, sysfs device attributes, and module parameters.

Risks and test signals: `ams_input_init()` calls `ams_input_enable()` when `joystick` is set but ignores its return before creating sysfs; failure handling could leave the parameter true/false mismatch. Test enable/disable races, poll output after calibration, invert parameter changes, input registration failure injection, and sysfs removal during polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-input.c -->
