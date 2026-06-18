# sources/distributed-fs/ceph-client/drivers/thermal/thermal_helpers.c

## Purpose
`thermal_helpers.c` contains shared thermal-core helper logic for trend detection, temperature reads, cooling-device target aggregation, and thermal-zone parameter accessors.

## Important APIs, Types, and Functions
Key APIs are `get_tz_trend`, `thermal_trip_is_bound_to_cdev`, `__thermal_zone_get_temp`, `thermal_zone_get_temp`, `thermal_cdev_update`, `thermal_cdev_update_nocheck`, `thermal_zone_get_slope`, and `thermal_zone_get_offset`. Exported APIs include trip/cdev binding checks, public temperature reads, and slope/offset access.

## Control Flow
Temperature reads go through `tz->ops.get_temp` under the zone lock. If thermal emulation is active, emulated temperature replaces the hardware value only when the real value is below the critical trip, preventing emulation from hiding critical heat. Cooling updates scan all `cdev->thermal_instances`, choose the deepest non-`THERMAL_NO_TARGET` state, call the cdev `set_cur_state` operation, then notify netlink, statistics, debugfs, and trace consumers.

## State and Persistence Behavior
The file mutates no persistent storage directly, but it updates live thermal/cooling state through driver callbacks and `cdev->updated`. Emulated temperature is read from `tz->emul_temperature`; statistics and debug state are updated in other modules.

## Dependencies and Integration Points
It depends on `thermal_core.h`, `thermal_trace.h`, guard-based zone/cdev locking, trip descriptors, thermal notifiers, debugfs hooks, and cooling-device statistics. It is central glue between governors, thermal-zone drivers, and cooling-device implementations.

## Risks and Edge Cases
Incorrect locking can race with governor binding or cdev state changes. Emulation must never suppress critical readings. `thermal_zone_get_temp` converts invalid sentinel temperatures to `-ENODATA`, so callers must handle that separately from driver read failures.

## Test Signals
Unit or KUnit coverage for trend fallback, emulation below/above critical trips, invalid temperature handling, deepest-state selection across multiple instances, and notification/statistics calls after state changes.
