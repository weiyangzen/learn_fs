<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thermal.h -->
# sources/distributed-fs/ceph-client/include/linux/thermal.h

## Purpose
declares the kernel thermal framework API: thermal trips, zone operations, cooling-device operations, registration helpers, notification events, OF registration, and disabled-config stubs.

## Important APIs, Types, and Functions
The file is 362 lines and exports these visible symbol families: types/enums `thermal_zone_device`, `thermal_cooling_device`, `thermal_instance`, `thermal_debugfs`, `thermal_attr`, `thermal_trend`, `thermal_notify_event`, `thermal_trip`, `cooling_spec`, `thermal_zone_device_ops`, `thermal_cooling_device_ops`, `thermal_zone_params`, `device`; macros/constants `__THERMAL_H__`, `THERMAL_CSTATE_INVALID`, `THERMAL_NO_LIMIT`, `THERMAL_WEIGHT_DEFAULT`, `THERMAL_TEMP_INVALID`, `THERMAL_TRIP_FLAG_RW_TEMP`, `THERMAL_TRIP_FLAG_RW_HYST`, `THERMAL_TRIP_FLAG_RW`; function-like macros `THERMAL_TRIP_PRIV_TO_INT`, `THERMAL_INT_TO_TRIP_PRIV`; inline helpers `devm_thermal_of_zone_unregister`, `thermal_zone_device_unregister`, `thermal_zone_device_update`, `thermal_cooling_device_register`, `thermal_of_cooling_device_register`, `devm_thermal_of_cooling_device_register`, `thermal_cooling_device_unregister`, `thermal_zone_get_temp`, `thermal_zone_get_slope`, `thermal_zone_get_offset`, `thermal_zone_device_id`, `thermal_zone_device_enable`, `thermal_zone_device_disable`, `thermal_pm_prepare`, and 1 more; external prototypes `devm_thermal_of_zone_unregister`, `ERR_PTR`, `for_each_thermal_trip`, `thermal_zone_for_each_trip`, `thermal_zone_set_trip_temp`, `thermal_zone_get_crit_temp`, `thermal_zone_device_unregister`, `thermal_zone_device_id`, `thermal_zone_device_update`, `thermal_of_cooling_device_register`, `devm_thermal_of_cooling_device_register`, `thermal_cooling_device_update`, `thermal_cooling_device_unregister`, `thermal_zone_get_temp`, and 8 more.

## Control Flow
Drivers register zones with trips and `thermal_zone_device_ops`, register cooling devices with `thermal_cooling_device_ops`, and the framework polls or updates temperatures, evaluates trips, binds cooling instances, calls governors, notifies events, and exposes sysfs/hwmon interfaces. OF helpers bind device-tree-described sensors and cooling devices.

## State and Persistence Behavior
Thermal zones and cooling devices are device-model objects with IDs, type strings, ops, private data, trip tables, cooling instances, locks, stats, and optional debugfs state. Trip values and hysteresis may be writable when flags allow it.

## Dependencies and Integration Points
It depends on devices, OF, mutex/list/sysfs/workqueue, UAPI thermal types, and optional CONFIG_THERMAL/CONFIG_THERMAL_OF/CONFIG_THERMAL_DEBUGFS code. Direct includes are `linux/of.h`, `linux/idr.h`, `linux/device.h`, `linux/sysfs.h`, `linux/workqueue.h`, `uapi/linux/thermal.h`.

## Risks and Edge Cases
Bad trip temperatures, hysteresis, or cooling-state bounds can overheat hardware or throttle too aggressively. Disabled-config stubs return ERR_PTR/-ENODEV and must be handled by drivers. Power allocator parameters require coherent units.

## Test Signals
Run thermal selftests, OF probe tests, sysfs trip read/write checks, cooling-device bind/unbind and state transitions, suspend/resume notifications, emulated temperature tests, and CONFIG_THERMAL=n builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thermal.h -->
