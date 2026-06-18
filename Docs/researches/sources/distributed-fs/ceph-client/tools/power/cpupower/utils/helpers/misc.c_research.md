# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/misc.c

## Purpose
Implements miscellaneous cpupower helpers for boost support/control, Intel perf bias, EPP, AMD pstate mode detection/control, CPU online/offline mask population, and human-readable frequency printing.

## Important APIs, Types, and Functions
Important APIs are `cpufreq_has_x86_boost_support`, `cpupower_set_intel_turbo_boost`, `cpupower_intel_get_perf_bias`, `cpupower_intel_set_perf_bias`, `cpupower_set_epp`, `cpupower_set_amd_pstate_mode`, `cpupower_amd_pstate_enabled`, `cpufreq_has_generic_boost_support`, `get_cpustate`, `print_online_cpus`, `print_offline_cpus`, `print_speed`, and `cpupower_set_generic_turbo_boost`.

## Control Flow, State, and Persistence
Boost support is selected from CPU capability flags: AMD CPB via MSR or PCI, AMD pstate via sysfs/CPPC, Intel IDA via `intel_pstate/no_turbo`, otherwise generic `/sys/devices/system/cpu/cpufreq/boost`. Per-CPU writes target sysfs files. CPU-state helpers clear and repopulate global masks from `cpus_chosen`. No files are created, but sysfs writes change live kernel policy.

## Dependencies and Integration Points
Depends on `helpers.h`, `helpers/sysfs.h`, cpufreq APIs, `cpupower_intern.h` for sysfs read/write helpers, MSR helpers, AMD helpers, and global CPU info/masks.

## Risks and Test Signals
Several mallocs in print helpers are not freed, though command lifetime is short. `print_speed` with rounding disabled has no branch for exactly 1000 or 1000000 kHz edge values. Sysfs writes use fixed buffer lengths rather than string length. Validate Intel/generic boost paths, AMD pstate mode, EPP writes, offline CPU reporting, and frequency formatting boundaries.
