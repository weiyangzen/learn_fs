# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/time_bench.c

Purpose: Provides reusable in-kernel timing and concurrent benchmark support for page-pool benchmarks.

Important APIs/types/functions: Implements `time_bench_PMU_config()`, `time_bench_calc_stats()`, `time_bench_loop()`, `time_bench_print_stats_cpumask()`, and `time_bench_run_concurrent()`. Uses TSC records from `time_bench.h`, wall-clock `timespec64`, optional perf/PMU counters, completions, atomics, CPU masks, and kthreads.

Control flow: `time_bench_loop()` initializes a record, calls a benchmark callback that wraps its own `time_bench_start/stop`, calculates stats, and logs per-call cycles and nanoseconds. Concurrent support spawns one kthread per selected CPU, pins each task, waits until all are ready, releases them with a completion, waits for completion counters to drop, then stops kthreads. PMU config attempts to create raw perf counters on the current CPU.

State and persistence behavior: Keeps static `perf_events[]` with saved perf_event pointers but does not use it in default page-pool benchmarks. Per-run state is held in `time_bench_record`, `time_bench_sync`, and `time_bench_cpu` structures. Output persists only in kernel logs.

Dependencies and integration points: Tightly paired with `time_bench.h` and benchmark modules. Depends on x86-like TSC helpers from the header, kernel timekeeping, kthreads, and perf events if PMU is enabled.

Risks: Comments mark PMU configuration as broken. TSC helpers are architecture-specific. `time_bench_run_concurrent()` returns immediately on kthread creation failure without stopping already-created tasks. Division logic requires loop counts under 2^32 and over 1000 for loop stats.

Test signals: Log lines with `Type:<name> Per elem:` and optional PMU IPC lines are consumed by `test_bench_page_pool.sh` and by humans comparing cycles/ns.
