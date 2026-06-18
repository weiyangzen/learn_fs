# sources/distributed-fs/ceph-client/drivers/thermal/gov_fair_share.c

## Purpose
Thermal governor that distributes throttling across cooling devices according to trip level and instance weights.

## Important APIs, Types, and Functions
- `get_trip_level()` counts how many trip thresholds are at or below the current temperature and traces the highest crossed trip.
- `fair_share_throttle()` computes each instance target as a fraction of cdev max state using trip level, total trips, and weight share.
- `fair_share_manage()` applies throttling for every non-hot/non-critical valid trip.
- Declares `thermal_gov_fair_share`.

## Control Flow
During manage under the zone lock, the governor computes a global trip level, then for each eligible trip sums instance weights and counts instances. It sets each instance target proportionally. If no weights are configured, it divides evenly by instance count.

## State and Persistence
State is stored in thermal instance `target` fields and cdev state after updates. The governor has no private persistent data.

## Dependencies and Integration Points
Uses thermal core trip descriptors, instance lists, cdev max state, thermal tracepoints, and `thermal_cdev_update_nocheck()`.

## Risks and Edge Cases
- If a trip has zero instances, no updates occur; if total weight is zero, divisor uses instance count.
- The formula uses `tz->num_trips`, so hot/critical trips still affect denominator even though skipped for updates.
- Integer division truncates target states.

## Test Signals
Tests should verify weighted and unweighted distribution, trip-level calculation, no-trip-crossed level zero, hot/critical filtering, and trace/update calls.
