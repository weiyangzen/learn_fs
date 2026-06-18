# sources/distributed-fs/ceph-client/drivers/peci/sysfs.c

Purpose: Provides PECI bus and device sysfs controls: bus-wide rescan and per-device remove.

Important APIs and functions: `rescan_store()` parses a boolean and triggers `peci_controller_scan_devices()` on every PECI controller device on the bus. `remove_store()` parses a boolean, uses `device_remove_file_self()` for safe self-removal, and calls `peci_device_destroy()`. `peci_bus_groups` and `peci_device_groups` export the attribute groups used by `peci_bus_type` and `peci_device_type`.

Control flow: Writing true to the bus `rescan` attribute walks bus devices, filters controller devices by `peci_controller_type`, and rescans each controller. Writing true to a PECI device's `remove` attribute removes the sysfs file from within the write path and unregisters the device.

State and persistence: The file itself has no long-lived mutable state. Rescan can create new device children; remove transitions a child toward unregister and sets `device->deleted` in `device.c`.

Dependencies and integration points: Depends on Linux sysfs/device helpers and PECI internal bus/device types. It is wired into `core.c` and `device.c` via exported attribute-group arrays.

Risks: Rescan is best-effort and stops on the first nonzero scan error from a controller. Remove relies on `peci_device_destroy()` for double-delete protection. Boolean false writes are accepted as no-ops, which may be surprising but matches common sysfs patterns.

Test signals: Presence and permissions of `/sys/bus/peci/rescan` and device `remove`, true/false parsing, rescan creating newly available devices, repeated remove/controller-unplug races, and lockdep behavior around `DEVICE_ATTR_IGNORE_LOCKDEP`.
