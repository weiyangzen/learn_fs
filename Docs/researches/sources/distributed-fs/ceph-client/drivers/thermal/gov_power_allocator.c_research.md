# sources/distributed-fs/ceph-client/drivers/thermal/gov_power_allocator.c

## Purpose
Intelligent Power Allocation thermal governor. It uses a fixed-point PID controller to compute a power budget for a thermal zone and divides that budget across cooling devices that implement the power-actor API.

## Important APIs, Types, and Functions
- `struct power_actor` stores requested, maximum, granted, extra, and weighted requested power per actor.
- `struct power_allocator_params` stores PID state, sustainable power, selected trips, actor counts/weights, and actor buffer.
- Fixed-point helpers `mul_frac()` and `div_frac()` implement FRAC_BITS arithmetic.
- `estimate_sustainable_power()`, `estimate_pid_constants()`, and `get_sustainable_power()` initialize or refresh thermal-zone power parameters.
- `pid_controller()` computes the next total power range from current temperature, control temperature, PID terms, and sustainable power.
- `divvy_up_power()` splits budget by weighted requested power and redistributes capped surplus.
- `allocate_power()` collects actor power requests, runs PID, assigns grants, and traces results.
- `get_governor_trips()` selects switch-on and control trips.
- `allow_maximum_power()` resets targets below switch-on and refreshes actor stats.
- `check_power_actors()`, `allocate_actors_buffer()`, `power_allocator_update_weight()`, and `power_allocator_update_tz()` manage actor eligibility and buffers.
- Governor hooks: bind, unbind, manage, and update.

## Control Flow
Bind allocates params, selects first/last passive or last active trip, verifies that all cooling devices on the control trip are power actors, allocates an actor buffer, creates `tzp` if missing, estimates PID constants if possible, resets PID state, and stores params in `tz->governor_data`. Manage checks the switch-on trip: below it, PID state resets and actors are allowed maximum power; above it, actor requested/max powers are collected, a PID budget is computed against `trip_max->temperature`, budget is split by weighted demand, and each actor's `power2state()` result becomes its target. Update handles cdev bind/unbind and weight changes by resizing buffers and recomputing total weight.

## State and Persistence
PID integral and previous error persist in `governor_data` while bound. `tz->tzp` may be allocated and modified, including `sustainable_power` and PID constants exposed through thermal-zone parameters. Actor buffer contents are per-manage temporary data.

## Dependencies and Integration Points
Requires cooling devices with `get_requested_power`, `state2power`, and `power2state`. It depends on thermal core trip descriptors, instance weights, thermal tracepoints, zone passive delay, and optional sysfs-updatable thermal zone parameters.

## Risks and Edge Cases
- Binding fails if any cdev on the control trip lacks power-actor callbacks.
- Sustainable power may be estimated from cooling devices' minimum powers; this is functional but may be suboptimal.
- PID constants are estimated only when threshold delta is nonzero; bad trip configuration can leave weak defaults.
- `power_allocator_update_tz()` assumes `params->trip_max` has a descriptor when bind/unbind events arrive.
- Integer fixed-point and budget clamping can truncate small effects.
- Actor count can change after binding; buffer resize failures leave actor state reset.

## Test Signals
Tests should cover trip selection for one/two/no passive trips, bind failure for non-power actors, PID output clamping, integral cutoff behavior, budget division and surplus redistribution, weight updates, switch-on below-threshold maximum-power path, and cleanup of allocated `tzp`.
