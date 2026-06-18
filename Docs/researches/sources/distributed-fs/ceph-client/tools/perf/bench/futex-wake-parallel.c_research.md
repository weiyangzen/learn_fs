# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex-wake-parallel.c

Purpose: measures latency when multiple waker threads concurrently call `futex_wake()` on a shared futex to wake a blocked population.

Important APIs/types/functions: if `HAVE_PTHREAD_BARRIER` is absent, `bench_futex_wake_parallel()` reports the benchmark disabled. Otherwise, `block_threads()` creates pinned waiters, `wakeup_threads()` starts waker threads behind a barrier, `waking_workerfn()` times each `futex_wake()`, and `do_run_stats()`/`print_summary()` aggregate latency and wake counts.

Control flow: parse thread/waker counts, validate divisibility, set `nwakes = nthreads / nwakers`, create blocked waiters for each repeat, broadcast them into `futex_wait()`, sleep briefly, launch synchronized wakers, join all waiters, record per-run stats, and print summary.

State and persistence: static shared futex, blocked worker array, pthread barrier, condition variables, stats, and params. Runtime only; no persistent files except optional futex bucket sysctl adjustment.

Dependencies and integration: depends on pthread barriers, futex wrappers, perf CPU maps, mutex/cond wrappers, stats, and bench repeat.

Risks: fixed sleeps and scheduling can affect whether all waiters are blocked. The benchmark requires thread count divisible by waker count. Plain `done` only stops repeats on signal. Barrier availability gates the whole file.

Test signals: builds with/without pthread barrier, `--threads` divisible/nondivisible by `--nwakers`, shared/private futexes, bucket changes, repeat count, and wake-count warning paths.
