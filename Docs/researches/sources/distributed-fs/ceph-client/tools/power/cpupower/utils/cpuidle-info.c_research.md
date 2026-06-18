# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpuidle-info.c

## Purpose
Implements `cpupower idle-info`, reporting cpuidle driver/governor and per-CPU idle state names, descriptions, latency, residency, usage, and accumulated time.

## Important APIs, Types, and Functions
Important functions are `cpuidle_cpu_output`, `cpuidle_general_output`, `proc_cpuidle_cpu_output`, `cpuidle_exit`, and `cmd_idle_info`. It calls libcpuidle APIs such as `cpuidle_state_count`, `cpuidle_state_name`, `cpuidle_state_desc`, `cpuidle_state_latency`, `cpuidle_state_residency`, `cpuidle_state_usage`, `cpuidle_state_time`, `cpuidle_get_driver`, and `cpuidle_get_governor`.

## Control Flow, State, and Persistence
`cmd_idle_info` parses `--silent` and `--proc`, rejects multiple output modes, defaults the CPU mask to `base_cpu`, prints general driver/governor data for normal mode, then loops selected CPUs and skips offline entries. `--proc` emits a legacy `/proc/acpi/processor`-style layout. The file only reads sysfs-backed cpuidle state and does not persist data.

## Dependencies and Integration Points
Depends on libcpuidle, `helpers/sysfs.h`, global CPU mask/base CPU state, and gettext helpers. It shares selection semantics with other cpupower subcommands.

## Risks and Test Signals
`cpuidle_exit(int fail)` ignores its argument and always exits failure, which is acceptable only for current error paths. The hard-coded `max_allowed_cstate` in proc output is synthetic. Validate kernels without cpuidle, offline CPUs, disabled-state visibility, silent mode, proc compatibility output, and memory ownership for returned state strings.
