# sources/distributed-fs/ceph-client/drivers/thermal/gov_step_wise.c

## Purpose
Default step-wise thermal governor. It adjusts cooling-device targets incrementally based on whether the zone is above a trip threshold and the current thermal trend.

## Important APIs, Types, and Functions
- `get_target_state()` computes the next target from current cdev state, instance lower/upper limits, initialization state, trend, and throttle boolean.
- `thermal_zone_trip_update()` applies `get_target_state()` to every instance on a trip descriptor and marks cdevs for update.
- `step_wise_manage()` processes every eligible trip and then updates all cdevs.
- Declares `thermal_gov_step_wise`.

## Control Flow
Manage runs under the thermal-zone lock. For each non-hot/non-critical valid trip, it computes whether the zone should throttle and asks thermal core for the trend. Targets increase by one when heating above threshold, decrease carefully when cooling, and deactivate when below threshold and already at lower limit. After target assignment, it walks all instances and updates cooling devices.

## State and Persistence
Thermal instance `target` and `initialized` fields retain state between manage calls. Cdev `updated` is cleared under the cdev guard when a new target requires update.

## Dependencies and Integration Points
Uses thermal core internals, min/max helpers, trends from `get_tz_trend()`, cdev ops, scoped cooling-device guards, and thermal tracepoints.

## Risks and Edge Cases
- Behavior depends heavily on trend classification; noisy sensors can cause oscillating state steps.
- Initial unthrottled instances return `THERMAL_NO_TARGET`.
- HOT and CRITICAL trips are ignored for governor throttling.
- The code calls cdev `get_cur_state()` without checking return value.

## Test Signals
Tests should cover uninitialized and initialized paths, raising/dropping trends above and below thresholds, clamp to lower/upper, `THERMAL_NO_TARGET` deactivation, and two-phase update of all cdevs.
