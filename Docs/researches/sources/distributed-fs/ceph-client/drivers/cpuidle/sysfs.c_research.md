<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/sysfs.c

## Purpose

`sysfs.c` exposes cpuidle global controls and per-CPU/per-state statistics through sysfs. It provides governor selection, current driver reporting, per-state counters, user disable toggles, and optional s2idle counters.

## Important APIs, Types, And Functions

Global attributes are `available_governors`, `current_driver`, `current_governor`, and read-only governor fallback. Per-device objects use `struct cpuidle_device_kobj`; per-state objects use `struct cpuidle_state_kobj`. Exported helpers include `cpuidle_add_interface()`, `cpuidle_add_sysfs()`, `cpuidle_add_device_sysfs()`, and their remove counterparts. State attributes expose name, desc, latency, residency, power, usage, rejected, time, disable, above, below, default_status, and s2idle usage/time when available.

## Control Flow

The global CPU root gets a `cpuidle` group. Each CPU gets a `cpuidle` kobject, then state subdirectories and optionally a driver subdirectory for multiple-driver builds. Writes to `current_governor` call `cpuidle_switch_governor()`. Writes to state `disable` require `CAP_SYS_ADMIN`, set or clear the user disable bit, and reset the device poll-time cache.

## State And Persistence Behavior

Kobjects include completions so removal waits for release. Sysfs disable persists in `state_usage.disable` until changed or the device is reinitialized. Time values are reported in microseconds from nanosecond accounting.

## Dependencies And Integration Points

It integrates with CPU subsystem devices, kobjects, sysfs ops, cpuidle locks, governor lists, driver locks, capabilities, and optional suspend/multiple-driver configs.

## Risks And Test Signals

Risks include kobject lifetime leaks, lock inversions during governor changes, exposing writable state to unprivileged users, and stale driver pointers in multiple-driver sysfs. Test by CPU online/offline, switching governors from sysfs, toggling state disables, removing drivers, and checking no kobject warnings appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/sysfs.c -->
