# sources/distributed-fs/ceph-client/drivers/thermal/gov_bang_bang.c

## Purpose
Thermal governor implementing two-point hysteresis control, primarily for binary cooling devices such as fans. It turns cooling on when a trip is crossed upward and off when crossed downward below the hysteresis threshold.

## Important APIs, Types, and Functions
- `bang_bang_set_instance_target()` sets instance target to 0/1, marks it initialized, and updates the cdev without extra checks.
- `bang_bang_trip_crossed()` applies upward/downward target to all instances bound to the crossed trip.
- `bang_bang_manage()` initializes uninitialized instances according to current zone temperature and trip thresholds.
- `bang_bang_update_tz()` clears `governor_data` after cdev binding and resume so initialization is repeated.
- Declares `thermal_gov_bang_bang`.

## Control Flow
The governor reacts to trip-crossing notifications under the thermal-zone lock and directly updates all cooling instances on that trip. On manage, it runs only once per binding/resume epoch and initializes uninitialized non-hot/non-critical trip instances based on whether the current temperature is above the trip descriptor threshold.

## State and Persistence
It uses each thermal instance's `target` and `initialized` state. `tz->governor_data` is used as a boolean "initialization done" flag, reset on bind/resume.

## Dependencies and Integration Points
Depends on thermal core internals (`thermal_core.h`), trip descriptors, thermal instances, and `thermal_cdev_update_nocheck()`.

## Risks and Edge Cases
- Designed for binary cooling; it only expects targets 0 and 1 and logs unexpected existing states.
- Skips HOT and CRITICAL trips, so it must be paired with other critical safety handling.
- Correct hysteresis behavior depends on trip-crossing events and descriptor thresholds from the thermal core.

## Test Signals
Tests should cover upward/downward crossings, initial manage with current temperature above/below threshold, reset after bind/resume, ignored hot/critical trips, and cdev update calls.
