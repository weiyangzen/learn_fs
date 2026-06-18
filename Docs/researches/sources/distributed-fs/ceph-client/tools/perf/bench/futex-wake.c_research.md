# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex-wake.c

Purpose: measures latency for waking blocked futex waiters in batches from one main thread.

Important APIs/types/functions: `bench_futex_wake()` is the entry point. `block_threads()` creates CPU-pinned waiters. `workerfn()` waits on the shared futex. `print_summary()` reports average wake latency and average wake count.

Control flow: parse thread count, `nwakes`, private/shared, buckets, mlockall, and silent options. For each repeat, create and release waiters into `futex_wait()`, sleep to allow queueing, time repeated `futex_wake()` calls until all requested threads are woken, join workers, update stats, and print per-run/summary output.

State and persistence: static shared futex, worker thread array, condition variables, stats, and params. No files are persisted; optional futex bucket helper may alter kernel sysctl for the run.

Dependencies and integration: futex wrappers, perf CPU map affinity, pthreads, mutex/cond, stats, bench repeat, and optional `mlockall`.

Risks: queueing readiness uses a fixed sleep after condition broadcast. Wake counts can differ from requested counts due to races or signals. Shared `done` is signal-set and read in loops.

Test signals: varied `--threads` and `--nwakes`, shared/private modes, repeat counts, mlockall, bucket setting, and warning when fewer waiters wake than expected.
