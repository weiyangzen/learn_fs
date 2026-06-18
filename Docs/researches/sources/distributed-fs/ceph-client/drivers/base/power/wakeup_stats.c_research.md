# sources/distributed-fs/ceph-client/drivers/base/power/wakeup_stats.c

## Purpose
This file creates a dedicated sysfs class for per-wakeup-source statistics. It mirrors selected `struct wakeup_source` counters and timing fields as attributes under generated `wakeupN` devices.

## Important APIs, Types, And Functions
The key entry points are `wakeup_source_sysfs_add()`, `pm_wakeup_source_sysfs_add()`, `wakeup_source_sysfs_remove()`, and the `postcore_initcall()` `wakeup_sources_sysfs_init()`. Attribute handlers expose `name`, `active_count`, `event_count`, `wakeup_count`, `expire_count`, `relax_count`, `active_time_ms`, `total_time_ms`, `max_time_ms`, `last_change_ms`, and `prevent_suspend_time_ms`.

## Control Flow And State
`wakeup_sources_sysfs_init()` creates the global `wakeup` class. `wakeup_source_device_create()` allocates a `struct device`, initializes it, sets class/parent/groups/release callback, stores the wakeup source as driver data, marks PM not required, assigns a stable name `wakeup%d` from `ws->id`, and calls `device_add()`. Removal unregisters `ws->dev`. Time attributes compute live active time by adding `ktime_get() - ws->last_time` when `ws->active`, and autosleep prevention time when `ws->autosleep_enabled`.

## Dependencies And Integration Points
This file depends on the wakeup source lifecycle in `wakeup.c`, the device core, sysfs attribute groups, ktime, and the `device_set_pm_not_required()` marker so generated stats devices do not get their own PM sysfs burden.

## Risks And Test Signals
Risks include missing class initialization, lifetime coupling between `ws` and generated stats device, unprotected reads of fields updated under `ws->lock`, and stale `ws->dev` if add/remove ordering is wrong. Test signals include class presence, one `wakeupN` per registered source, correct parent links for device-associated sources, attribute monotonicity during active events, and clean device removal on wakeup source unregister.
