# sources/distributed-fs/ceph-client/drivers/thermal/thermal_debugfs.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/thermal_debugfs.c` implements debugfs observability for the thermal subsystem. It records cooling-device state transitions/residency and thermal-zone mitigation episodes/trip statistics under `/sys/kernel/debug/thermal`. The source was read as a complete 968-line file.

## Important APIs, Types, and Functions

Important types are `struct thermal_debugfs`, `struct cdev_debugfs`, `struct cdev_record`, `struct tz_debugfs`, `struct tz_episode`, and `struct trip_stats`. Public functions called by the core include `thermal_debug_init()`, `thermal_debug_cdev_add()`, `thermal_debug_cdev_state_update()`, `thermal_debug_cdev_remove()`, `thermal_debug_tz_add()`, `thermal_debug_tz_trip_up()`, `thermal_debug_tz_trip_down()`, `thermal_debug_update_trip_stats()`, `thermal_debug_tz_remove()`, and `thermal_debug_tz_resume()`.

## Control Flow

Initialization creates `thermal/cooling_devices` and `thermal/thermal_zones` debugfs directories. Cooling-device add allocates a debug object, initializes hash buckets for transitions and durations, records the initial state, and creates files for `trans_table`, `time_in_state_ms`, `clear`, and `total_trans`. State updates compute old-state residency, create/update transition records keyed by old/new state, update current state, and increment totals. Thermal-zone add allocates per-zone episode state and a `mitigations` seq file. Trip-up starts an episode if needed, records crossed trip IDs and start timestamps. Trip-down finds the trip in the active stack, closes its duration, and closes the episode when the last active trip drops. Periodic update stats maintain max, min, and running average temperatures. Resume closes any in-progress mitigation episode so post-resume handling starts cleanly.

## State and Persistence Behavior

All state is debug-only, in memory, and attached to the cdev or thermal zone. Cooling-device records are hash lists of transition counts and state residency durations. Thermal-zone records are a list of mitigation episodes with flexible per-trip stats. Removing a cdev/zone detaches the pointer under the object lock, frees lists, removes debugfs directories, and frees memory. State is not persistent across reboot, unregister, or debugfs removal.

## Dependencies and Integration Points

It depends on debugfs, seq_file helpers, ktime, lists, mutexes, and thermal core private structures. It is called synchronously from core registration, cdev state updates, trip crossing paths, zone updates, unregister, and resume.

## Risks and Edge Cases

Debugfs must not destabilize thermal control. Allocation failures are intentionally tolerated by leaving debugfs absent. Lock ordering with thermal zone/cdev locks matters when clearing debugfs pointers. The trip-crossed stack can see reordered or dynamically changed trips; the code handles missing downward matches by ignoring them. Cooling transition IDs pack two 16-bit states, so extremely large state IDs could truncate in display logic. The cdev clear path resets records but leaves current state/timestamp behavior important for later duration accounting.

## Test Signals

Signals include debugfs tree creation, cooling-device transition table and residency output after cdev state changes, clear-file behavior, mitigation episode output after synthetic trip crossings, unregister cleanup with no use-after-free under lockdep/KASAN, and resume closing active mitigation episodes.
