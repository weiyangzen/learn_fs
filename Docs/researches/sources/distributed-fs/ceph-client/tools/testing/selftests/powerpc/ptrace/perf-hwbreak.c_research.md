# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/perf-hwbreak.c

## Purpose
`perf-hwbreak.c` stress-tests perf hardware breakpoints/watchpoints on powerpc. It covers read/write modes, exclude_user behavior, DAWR-length ranges, overlap semantics, multiple breakpoints, and process versus system-wide event placement.

## Important APIs, Types, and Functions
Important helpers are `perf_event_attr_set()`, process/cpu/system-wide perf open wrappers, fd control helpers, `breakpoint_test()`, `perf_breakpoint_supported()`, `dawr_supported()`, `runtestsingle()`, `runtest_dar_outside()`, multi-DAWR test functions, `get_nr_wps()`, `runtest()`, and `perf_hwbreak()`.

## Control Flow and State
The test first probes breakpoint and DAWR support, discovers online CPUs/watchpoint capacity, and raises fd limits for system-wide runs. Single tests open a disabled breakpoint, enable it around deterministic reads/writes, read counts, and compare against expected hits. Overlap tests watch subranges and verify no/partial/full overlap counts. Multi-watchpoint tests open pairs on same or different addresses and in process or per-CPU modes. State includes perf fds, volatile watched globals, CPU affinity masks, and watchpoint counts.

## Dependencies and Integration Points
It uses `perf_event_open`, `PERF_TYPE_BREAKPOINT`, `linux/hw_breakpoint.h`, powerpc `PPC_PTRACE_GETHWDBGINFO` probing, CPU affinity/sysinfo APIs, and kselftest reporting.

## Risks and Test Signals
Risks are noisy counts from compiler optimizations, CPU hotplug reducing available CPUs, privilege restrictions for system-wide perf, and hardware differences in DAWR overlap semantics. Strong signals are exact expected counts for read/write/exclude combinations and correct multi-watchpoint behavior.
