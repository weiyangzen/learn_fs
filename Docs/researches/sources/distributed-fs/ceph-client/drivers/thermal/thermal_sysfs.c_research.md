# sources/distributed-fs/ceph-client/drivers/thermal/thermal_sysfs.c

## Purpose
`thermal_sysfs.c` builds the thermal framework sysfs ABI for thermal zones, trips, cooling devices, cooling statistics, and thermal-instance binding attributes.

## Important APIs, Types, and Functions
Zone attributes include `type`, `temp`, `mode`, `policy`, `available_policies`, `sustainable_power`, PID coefficients, slope/offset, optional `emul_temp`, and generated trip attributes. Cooling attributes include `type`, `max_state`, `cur_state`, optional `stats/*`, `trip_point`, and `weight`. Public setup/teardown APIs are `thermal_zone_create_device_groups`, `thermal_zone_destroy_device_groups`, `thermal_cooling_device_setup_sysfs`, `thermal_cooling_device_destroy_sysfs`, `thermal_cooling_device_stats_update`, and `thermal_cooling_device_stats_reinit`.

## Control Flow
Zone stores parse user input, validate it under zone locking, call driver callbacks where present, update thermal-core trip state, and trigger zone updates. `create_trip_attrs` allocates `3 * num_trips + 1` attributes and assigns names/modes based on trip flags. Cooling `cur_state_store` validates requested state, calls the cdev operation under cdev locking, and updates statistics. Statistics track time in state and transitions under a spinlock and render a transition matrix bounded by `PAGE_SIZE`.

## State and Persistence Behavior
Sysfs groups are allocated per device and freed at teardown. Cooling statistics are in-memory state attached to `cdev->stats`; reset clears counters and timestamps. Zone parameter writes mutate live `tz->tzp` values only.

## Dependencies and Integration Points
It depends on thermal core locks, governors, trips, cdev operations, jiffies/ktime, sysfs attribute groups, optional thermal emulation, and optional statistics config.

## Risks and Edge Cases
Trip writes must avoid integer overflow around `THERMAL_TEMP_INVALID`. Transition tables can exceed one page and return `-EFBIG`. `cur_state_store` updates stats but does not send netlink/debug notifications, unlike helper-driven cdev updates.

## Test Signals
Sysfs read/write tests for all zone attributes, trip temperature/hysteresis validation, policy changes, emulation behavior, cooling state bounds, stats reset/time accumulation, and large transition table handling.
