# sources/distributed-fs/ceph-client/drivers/platform/x86/hdaps.c

Purpose: implements the IBM/Lenovo ThinkPad Hard Drive Active Protection System driver for older models with the HDAPS accelerometer at ISA I/O ports `0x1600..0x162f`. It exposes raw position, variance, temperatures, keyboard/mouse activity, calibration, and axis inversion through sysfs and registers a polled input device reporting `ABS_X`/`ABS_Y` tilt relative to a rest calibration.

Important APIs/types/functions: `hdaps_device_init()` performs the hardware command sequence and latch waits; `__device_refresh_sync()`, `__hdaps_read_pair()`, and `hdaps_readb_one()` serialize port access through `hdaps_mtx`; `hdaps_mousedev_poll()` feeds input events; `DEVICE_ATTR()` entries implement `position`, `variance`, `temp1`, `temp2`, `keyboard_activity`, `mouse_activity`, `calibrate`, and `invert`; `hdaps_whitelist` uses DMI callbacks to gate loading and set default inversion.

Control flow: module init checks the DMI whitelist, reserves the ISA port range, registers a `platform_driver`, creates a simple platform device, creates sysfs files, calibrates, configures a polled input device, then registers it. Reads issue a synchronous refresh, sample ports, update `km_activity`, complete the device transaction, and apply optional axis inversion. Resume re-runs hardware initialization; exit unregisters input, sysfs, platform objects, and I/O region.

State and persistence: module globals hold the platform device, input device, `hdaps_invert`, latest keyboard/mouse activity, and rest calibration. The `invert` module parameter and writable sysfs file affect runtime readings but are not persisted by the driver; calibration is runtime-only.

Dependencies and integration: depends on DMI, platform bus, input polling, sysfs, x86 port I/O, and PM sleep hooks. Integration is hardware-specific and intentionally blocked on unsupported DMI systems.

Risks: direct port I/O has tight timing and only coarse error reporting. `hdaps_invert_store()` calls `hdaps_calibrate()` without taking `hdaps_mtx`, unlike other calibration paths. DMI ordering matters because prefix-like product strings could match broader models. Test signals are module load on whitelisted ThinkPads, sysfs read/write behavior, input event stability, suspend/resume reinitialization, and failure-path cleanup when device init or input registration fails.
