# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpufreq-info.c

## Purpose
Implements `cpupower frequency-info`, reporting cpufreq driver, policy, limits, current frequency, governors, related/affected CPUs, statistics, boost state, EPP, latency, and AMD pstate performance capabilities.

## Important APIs, Types, and Functions
Important helpers include `count_cpus`, `proc_cpufreq_output`, `print_duration`, `get_boost_mode_x86`, `get_boost_mode_generic`, `get_freq_kernel`, `get_freq_hardware`, `get_hardware_limits`, `get_driver`, `get_policy`, `get_available_governors`, `get_affected_cpus`, `get_related_cpus`, `get_freq_stats`, `get_epp`, `get_latency`, `get_perf_cap`, `debug_output_one`, and command entry `cmd_freq_info`.

## Control Flow, State, and Persistence
`cmd_freq_info` parses exactly one output-specific option, with `--human` and `--no-rounding` as modifiers. If no CPU mask was supplied it selects global `base_cpu`; `--proc` rejects `--cpu`. It iterates selected CPUs, skips offline CPUs using sysfs, and invokes the selected getter. The default debug mode aggregates many getters. The file reads live sysfs/MSR data only and persists nothing.

## Dependencies and Integration Points
Depends on libcpupower cpufreq APIs, `helpers/sysfs.h`, global CPU masks and `cpupower_cpu_info` from `helpers.h`, MSR/AMD helper routines, and gettext macros. It integrates with main option parsing through `builtin.h` and global `cpus_chosen`.

## Risks and Test Signals
Linked-list cleanup is fragile because some loops advance list pointers before calling put functions, potentially losing the head if the put routine expects it. `get_freq_stats` divides by `total_time` without an explicit zero guard. Hardware frequency and boost queries require root/MSR support on many systems. Validate option exclusivity, offline CPU handling, sysfs-only non-x86 behavior, AMD pstate output, Intel turbo ratio output, and `--proc` compatibility.
