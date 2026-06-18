# Research: sources/distributed-fs/ceph-client/tools/perf/bench/breakpoint.c

Purpose: benchmarks hardware breakpoint overhead in two scenarios: inheritable breakpoint impact on thread create/join, and repeated breakpoint disable/enable while passive or active threads exist.

Important APIs/types/functions: `breakpoint_setup()` opens a `PERF_TYPE_BREAKPOINT` event with RW one-byte watchpoint attributes. `bench_breakpoint_thread()` creates `nbreakpoints`, then `nparallel` workers repeatedly create/join `nthreads` passive futex waiters. `bench_breakpoint_enable()` creates one breakpoint, starts passive futex waiters and active spinners, then loops `PERF_EVENT_IOC_DISABLE/ENABLE`.

Control flow: options are parsed with subcmd parse-options. Missing hardware breakpoint support (`-ENODEV`) skips cleanly. Timing uses `gettimeofday()` and `timersub()`. Passive threads block on futex until a shared atomic `done`; active threads spin until `done`.

State and persistence: benchmark state is process-local static option structs and allocated arrays of threads/breakpoints. No files persist. The kernel perf_event breakpoint fd is opened and closed per run.

Dependencies and integration: depends on `perf_event_open`, Linux hardware breakpoint ABI, futex helpers, pthreads, ioctl perf event enable/disable, and global bench output format.

Risks: `repeat` is shared by parallel workers with relaxed atomic fetch-sub and may overshoot semantics under unusual values. Hardware watchpoint availability and permissions vary. Active spinner mode can burn CPU and skew system-wide measurements.

Test signals: run both breakpoint subcommands with default/simple formats, no-breakpoint hardware path, multiple breakpoints, passive/active mix, and perf_event permission failure handling.
