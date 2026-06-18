# sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.c` is the central Linux thermal subsystem implementation. It registers the thermal class, governors, thermal zones, and cooling devices; runs the zone update loop; handles trip crossing, polling, hardware trip windows, critical shutdown, cdev binding, PM transitions, hwmon/debug/netlink integration, and exported registration APIs. The source was read as a complete 1921-line file.

## Important APIs, Types, and Functions

Major exported APIs include `thermal_register_governor()`, `thermal_unregister_governor()`, `thermal_zone_device_set_policy()`, `thermal_zone_device_enable()`, `thermal_zone_device_disable()`, `thermal_zone_device_update()`, `thermal_cooling_device_register()`, `thermal_of_cooling_device_register()`, `devm_thermal_of_cooling_device_register()`, `thermal_cooling_device_unregister()`, `thermal_cooling_device_update()`, `thermal_zone_get_crit_temp()`, `thermal_zone_device_register_with_trips()`, `thermal_tripless_zone_device_register()`, `thermal_zone_device_unregister()`, `thermal_zone_get_zone_by_name()`, `thermal_pm_prepare()`, and `thermal_pm_complete()`. Important internal functions include `thermal_set_governor()`, `__thermal_zone_device_update()`, `thermal_zone_handle_trips()`, `thermal_trip_crossed()`, `thermal_bind_cdev_to_trip()`, `thermal_zone_init_complete()`, and `thermal_init()`.

## Control Flow

`thermal_init()` initializes debugfs/netlink, creates the `thermal_events` workqueue, registers built-in governors from the linker table, and registers the thermal class. Zone registration validates inputs, allocates a flexible `thermal_zone_device` with trip descriptors, initializes trip lists, binds a governor, creates sysfs/hwmon/thresholds, registers the device, adds the zone to `thermal_tz_list`, binds existing cooling devices, performs an initial update, emits notifications, and creates debugfs state. The update loop locks the zone, reads temperature, handles transient and repeated read failures, updates trace/netlink state, moves trip descriptors between high/reached/invalid lists, notifies userspace/debugfs, invokes critical or hot callbacks, sets hardware low/high trip windows, lets thresholds adjust them, calls the governor `manage()` hook, updates debug stats, and schedules polling if needed. Cooling-device registration validates ops, allocates IDs/state, registers the class device, creates debugfs, adds it to `thermal_cdev_list`, and binds it to existing zones. Unregister paths unbind instances, remove debugfs/hwmon/sysfs, unregister devices, wait for release completions, and free IDs/memory. PM prepare marks zones suspended and cancels polling; PM complete queues immediate resume work that reinitializes zones and updates governors.

## State and Persistence Behavior

Global runtime state includes IDAs for zone/cdev IDs, `thermal_tz_list`, `thermal_cdev_list`, `thermal_governor_list`, `def_governor`, suspend state, and the workqueue. Per-zone state includes trip descriptors and sorted lists, mode, temperatures, passive count, governor data, thermal instances, polling work, user thresholds, and debugfs data. Per-cdev state includes current maximum state, thermal instance bindings, sysfs/debugfs state, and stats. None of this is file-persistent; it is rebuilt at boot/module load.

## Dependencies and Integration Points

The core integrates with Linux device class/sysfs, IDA, workqueues, PM notifications, reboot/hardware protection, hwmon (`thermal_hwmon.h`), generic netlink, tracepoints, threshold support, debugfs, Device Tree helper APIs in other files, and governor implementations declared through `THERMAL_GOVERNOR_DECLARE()`. Drivers in this subset call into this file through thermal-zone and cooling-device APIs.

## Risks and Edge Cases

This file is concurrency-sensitive: list locks, per-zone locks, cdev locks, completion ordering, and PM work replacement must remain consistent. Repeated temperature read failures back off then disable a zone, which can be dangerous if a zone has critical trips. Trip list relocation must correctly handle invalid trips, hysteresis, and dynamic trip temperature changes. Governor unregister assumes zones have valid governor pointers in list iteration. Binding creates sysfs links/files and must unwind exactly. `thermal_zone_get_zone_by_name()` returns a raw pointer without taking a device reference. PM prepare/complete interactions wait for in-flight resume work to avoid stale locks.

## Test Signals

Thermal core tests should cover zone/cdev registration/unregistration, duplicate and failed cdev binding, all trip types crossing upward/downward, hysteresis and dynamic trip updates, polling and `-EAGAIN` recheck behavior, governor switching and unregister, cooling-device max-state shrink, PM prepare/complete, critical trip hardware protection, hwmon/debugfs/netlink notifications, and the thermal testing module's synthetic zones.
