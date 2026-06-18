# sources/distributed-fs/ceph-client/drivers/thermal/thermal_debugfs.h

## Purpose
`thermal_debugfs.h` is the thermal core's debugfs abstraction header. It lets core code call debug lifecycle, trip, and cooling-device instrumentation unconditionally while compiling to no-ops when `CONFIG_THERMAL_DEBUGFS` is disabled.

## Important APIs, Types, and Functions
The enabled declarations cover `thermal_debug_init`, cooling-device add/remove/state update hooks, thermal-zone add/remove/resume hooks, trip up/down hooks, and `thermal_debug_update_trip_stats`. The disabled path provides matching `static inline` stubs.

## Control Flow
There is no executable flow in the header beyond compile-time selection. Thermal registration, trip crossing, resume, and cdev update paths call these hooks; the implementation file owns the debugfs directories and statistics when enabled.

## State and Persistence Behavior
This header owns no state. With debugfs enabled, the paired implementation persists in-memory debug statistics and debugfs entries for the lifetime of thermal zones and cooling devices; with the stubs there is no runtime effect.

## Dependencies and Integration Points
It depends on `struct thermal_zone_device`, `struct thermal_cooling_device`, and `struct thermal_trip` declarations from the thermal core. Integration is internal to thermal core event paths and complements netlink and trace notifications.

## Risks and Edge Cases
The risk is API drift between enabled declarations and disabled stubs; mismatched signatures would break builds only in one configuration. Debug hooks must also avoid changing core behavior, because callers ignore return values.

## Test Signals
Build with and without `CONFIG_THERMAL_DEBUGFS`; exercise zone/cdev registration and trip crossings; inspect debugfs entries in enabled builds; verify no undefined references or side effects in disabled builds.
