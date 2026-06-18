# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/sysfs.c

## Purpose
Implements cpupower sysfs helpers for CPU online state, cpuidle per-state attributes, cpuidle driver/governor strings, and legacy scheduler tunable stubs.

## Important APIs, Types, and Functions
Important APIs are `sysfs_read_file`, `sysfs_is_cpu_online`, `sysfs_idlestate_file_exists`, `sysfs_idlestate_read_file`, `sysfs_is_idlestate_disabled`, `sysfs_idlestate_disable`, `sysfs_get_idlestate_latency`, `sysfs_get_idlestate_usage`, `sysfs_get_idlestate_time`, `sysfs_get_idlestate_name`, `sysfs_get_idlestate_desc`, `sysfs_get_idlestate_count`, `sysfs_get_cpuidle_governor`, `sysfs_get_cpuidle_driver`, `sysfs_get_sched`, and `sysfs_set_sched`.

## Control Flow, State, and Persistence
Helpers build paths under `/sys/devices/system/cpu/`, read numeric/string files, trim string newlines, and write `disable` values for idle states. `sysfs_is_cpu_online` treats missing `cpuX/online` as online for kernels without CPU hotplug. `sysfs_get_idlestate_count` counts contiguous `stateN` directories. Scheduler helpers return `-ENODEV`, reflecting removed or unsupported knobs. State changes are limited to cpuidle disable sysfs writes.

## Dependencies and Integration Points
Depends on Linux CPU/cpuidle sysfs layout and is used by libcpuidle wrappers, idle/frequency commands, and helper CPU state routines.

## Risks and Test Signals
`sysfs_idlestate_disable` writes `sizeof(disable)` bytes from a text buffer, which can include extra NUL bytes instead of string length. Numeric parsing does not always reset errno. State counting assumes contiguous indices. Test hotplug/no-hotplug kernels, missing cpuidle, unsupported disable files, read-only sysfs, current_governor_ro fallback, and string allocation/free behavior.
