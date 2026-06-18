# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/mperf_monitor.c

## Purpose
Implements the x86 APERF/MPERF monitor named `Mperf`, reporting C0 percentage, Cx percentage, and average frequency in MHz.

## Important APIs, Types, and Functions
Important functions are `mperf_get_tsc`, `get_aperf_mperf`, `mperf_init_stats`, `mperf_measure_stats`, `mperf_get_count_percent`, `mperf_get_count_freq`, `mperf_start`, `mperf_stop`, `init_maxfreq_mode`, `mperf_register`, and `mperf_unregister`. It can read APERF/MPERF through AMD RDPRU or MSRs.

## Control Flow, State, and Persistence
Registration requires `CPUPOWER_CAP_APERF` and a max-frequency mode. It prefers invariant TSC as reference on Intel and some AMD systems, otherwise uses cpufreq hardware max. Start/stop snapshot timestamps, TSC, APERF, and MPERF per CPU; callbacks compute residency and average frequency from deltas. AMD may bind the process to each CPU before reads to reduce skew.

## Dependencies and Integration Points
Depends on MSR/RDPRU access, cpufreq hardware limits, CPU vendor/capability discovery, monitor framework globals, and root access unless RDPRU path is sufficient.

## Risks and Test Signals
Division by zero is possible if MPERF or TSC deltas are zero during very short measurements or failed reads. Validity tracking uses OR at stop, so partial reads may pass. Max-frequency fallback can fail without cpufreq. Test Intel/AMD, RDPRU-capable AMD, Xen/no MSR access, short intervals, offline CPUs, and comparison to known workload frequency.
