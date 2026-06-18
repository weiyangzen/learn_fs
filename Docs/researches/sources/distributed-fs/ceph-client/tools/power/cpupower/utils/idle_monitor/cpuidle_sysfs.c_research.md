# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpuidle_sysfs.c

## Purpose
Implements a generic cpuidle sysfs monitor plugin named `Idle_Stats`, deriving idle residency percentages from per-state `time` counters.

## Important APIs, Types, and Functions
Key functions are `cpuidle_get_count_percent`, `cpuidle_start`, `cpuidle_stop`, `fix_up_intel_idle_driver_name`, optional POWER `map_power_idle_state_name`, `cpuidle_register`, and `cpuidle_unregister`. It fills a static `cpuidle_cstates` array and monitor descriptor `cpuidle_sysfs_monitor`.

## Control Flow, State, and Persistence
Registration uses `sched_getcpu` and assumes all CPUs expose the same number of idle states. It reads names/descriptions, normalizes some Intel and POWER labels, allocates previous/current two-dimensional counter arrays, and records state callbacks. Start snapshots `cpuidle_state_time`; stop snapshots again and computes elapsed microseconds. No persistent data is written.

## Dependencies and Integration Points
Depends on libcpuidle APIs, monitor framework globals including `cpu_count`, gettext/debug helpers, and CPU naming conventions from intel_idle/powerpc drivers.

## Risks and Test Signals
`CPUIDLE_STATES_MAX` is 10 but the code does not clamp `hw_states_num`, so CPUs exposing more states could overrun `cpuidle_cstates`. Allocation failures are unchecked. Offline or heterogeneous CPUs may produce invalid reads. Test many-state systems, POWER name mapping, Intel idle names, missing cpuidle sysfs, and selected CPU subsets.
