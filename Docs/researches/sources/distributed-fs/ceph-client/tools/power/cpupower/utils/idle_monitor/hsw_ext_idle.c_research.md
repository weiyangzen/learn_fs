# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/hsw_ext_idle.c

## Purpose
Implements a Haswell-specific monitor for package C8/C9/C10 residency MSRs.

## Important APIs, Types, and Functions
Key functions are `hsw_ext_get_count`, `hsw_ext_get_count_percent`, `hsw_ext_start`, `hsw_ext_stop`, `hsw_ext_register`, and `hsw_ext_unregister`. The monitor descriptor is `intel_hsw_ext_monitor` with states `PC8`, `PC9`, and `PC10`.

## Control Flow, State, and Persistence
Registration requires Intel family 6 model 0x45. It allocates per-CPU previous/current arrays and validity flags. Start reads state MSRs for each CPU then TSC; stop reads TSC then state MSRs; percentages are residency delta divided by TSC delta. State is in static heap arrays and MSR counters.

## Dependencies and Integration Points
Depends on x86 MSR access, CPU model detection, root privileges, and monitor framework callbacks. Complements the broader SandyBridge monitor on selected Haswell systems.

## Risks and Test Signals
Only model 0x45 is recognized, so other CPUs with these MSRs may not register. `is_valid[cpu] |= !read` can mark a CPU valid if either start or stop succeeds rather than requiring both. Test matching Haswell hardware, read failures, offline CPUs, non-root filtering, and percent sanity versus turbostat.
