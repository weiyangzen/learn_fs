# sources/distributed-fs/ceph-client/drivers/video/backlight/backlight.c

## Purpose
`backlight.c` implements the Linux backlight class core. It provides `/sys/class/backlight` devices, common brightness/power attributes, registration helpers, display blanking notifications, PM integration, uevents, and OF lookup helpers.

## Important APIs, types, and functions
Public exports include `backlight_notify_blank`, `backlight_notify_blank_all`, `backlight_device_set_brightness`, `backlight_force_update`, `backlight_device_register`, `backlight_device_unregister`, `devm_backlight_device_register`, `devm_backlight_device_unregister`, `backlight_device_get_by_type`, `backlight_device_get_by_name`, `of_find_backlight_by_node`, and `devm_of_find_backlight`. Attribute handlers implement `bl_power`, `brightness`, `actual_brightness`, `max_brightness`, `scale`, and `type`.

## Control flow
Class initialization runs at `postcore_initcall`. Drivers register a backlight with ops and properties. Sysfs stores validate and update requested brightness/power under `ops_lock`, call driver `update_status`, and emit change events. `actual_brightness` either calls driver `get_brightness` or returns cached brightness. Display blanking adjusts `use_count` and toggles `BL_CORE_FBBLANK`, while suspend/resume toggles `BL_CORE_SUSPENDED` for drivers opting into core PM.

## State and persistence
Each `backlight_device` owns props, ops pointer, update/ops locks, use count, and list entry. A global list protected by `backlight_dev_list_mutex` supports enumeration and blank-all notifications. State is runtime-only but surfaced to userspace through sysfs.

## Dependencies and integration points
It integrates with the Linux device/class model, sysfs, kobject uevents, devres, OF phandles, display drivers, optional PMAC backlight global state, and all low-level backlight drivers.

## Risks and test signals
Risks include stale ops during unregister, global list reference lifetime, `backlight_device_get_by_type` returning without taking a reference, brightness event generation after failed set, blanking use-count correctness, and OF lookup defer behavior. Test signals include sysfs ABI tests, concurrent unregister and sysfs access, blanking multiple displays, suspend/resume, devm cleanup, OF deferred probe, and uevent source checks.
