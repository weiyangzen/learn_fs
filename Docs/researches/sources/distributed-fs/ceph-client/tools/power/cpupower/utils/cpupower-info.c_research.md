# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower-info.c

## Purpose
Implements the generic `cpupower info` command, currently focused on Intel energy performance bias reporting.

## Important APIs, Types, and Functions
Important pieces are option table `set_opts`, `print_wrong_arg_exit`, and `cmd_info`. The only supported option is `--perf-bias`/`-b`, which calls `cpupower_intel_get_perf_bias` after checking root privileges and `CPUPOWER_CAP_PERF_BIAS`.

## Control Flow, State, and Persistence
The command rejects POWER machines by uname, initializes locale, parses options, defaults the selected CPU mask to `base_cpu`, then iterates selected online CPUs and prints `perf-bias`. It reads `/sys/devices/system/cpu/cpuX/power/energy_perf_bias` via helper code and does not persist anything.

## Dependencies and Integration Points
Depends on `helpers/helpers.h`, `helpers/sysfs.h`, global CPU masks, global `cpupower_cpu_info`, and the main dispatcher. It complements `cpupower-set.c` for the write side.

## Risks and Test Signals
The default `params.params = 0x7` does not correspond to only defined bitfields and then early returns when `perf_bias` is not set, making default `cpupower info` effectively a no-op. Test unsupported architectures, non-root invocation, CPUs offline, unsupported perf-bias capability, and successful per-CPU reads.
