# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex-requeue.c

Purpose: benchmarks `futex_cmp_requeue()` latency by blocking threads on one futex and requeueing them to another.

Important APIs/types/functions: `bench_futex_requeue()` orchestrates repeated runs. `block_threads()` creates CPU-pinned waiters. `workerfn()` waits on the first futex. `print_summary()` aggregates requeue latency and number of requeued tasks.

Control flow: parses threads, wake/requeue counts, shared/private, mlockall, silent, and bucket options. For each repeat, it starts waiters behind a barrier, sleeps to let them block, times `futex_cmp_requeue()`, joins workers, records stats, and resets for the next repeat.

State and persistence: uses static futex words, thread array, condition state, stats, and params. No persistent files except optional kernel futex bucket sysctl adjustment via helper.

Dependencies and integration: futex wrappers including cmp-requeue, perf CPU maps, pthreads, mutex/cond, stats, and bench repeat.

Risks: correctness depends on waiters actually being queued before requeue; the fixed sleep is a heuristic. Requested wake/requeue values are adjusted for thread count. Shared `done` only affects signal interruption. Kernel futex semantics differ for private/shared flags.

Test signals: varied `--nwakes`/`--nrequeues`, repeat counts, private/shared, divisible and boundary thread counts, and verifying all waiters exit after requeue/wake.
