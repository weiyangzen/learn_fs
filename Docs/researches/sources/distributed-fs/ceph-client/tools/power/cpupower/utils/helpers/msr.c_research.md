# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/msr.c

## Purpose
Provides x86 MSR read/write helpers and Intel turbo ratio lookup for cpupower.

## Important APIs, Types, and Functions
Key APIs are `read_msr`, `write_msr`, and `msr_intel_get_turbo_ratio`. The code knows MSR constants for perf status, misc enables, and Nehalem turbo ratio limit, though only the turbo ratio constant is used here.

## Control Flow, State, and Persistence
`read_msr` and `write_msr` open `/dev/cpu/<cpu>/msr`, seek to the MSR index, transfer an unsigned long long, close the descriptor, and return 0 or -1. `msr_intel_get_turbo_ratio` checks `CPUPOWER_CAP_HAS_TURBO_RATIO` before reading `MSR_NEHALEM_TURBO_RATIO_LIMIT`. No persistent state is kept, but writes would mutate processor MSR state.

## Dependencies and Integration Points
Depends on x86 builds, global `cpupower_cpu_info`, the kernel `msr` driver, root privileges for many MSRs, and callers in boost/frequency/monitor code.

## Risks and Test Signals
Uses `lseek(..., SEEK_CUR)` on a fresh descriptor, equivalent to absolute from zero but less explicit than `SEEK_SET`. Errors do not preserve detailed errno for callers. Test missing msr module, non-root access, nonexistent CPUs, unsupported MSRs, and turbo ratio reporting on supported Intel models.
