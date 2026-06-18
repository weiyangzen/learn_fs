# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex-hash.c

Purpose: stresses Linux futex user-address hashing by issuing many failing `FUTEX_WAIT` calls across per-thread futex arrays.

Important APIs/types/functions: `bench_futex_hash()` is the entry point. `workerfn()` loops over `params.nfutexes` and calls `futex_wait()` with an unmatched expected value. `toggle_done()` stops workers and records runtime. `print_summary()` reports average ops/sec and futex hash bucket setting.

Control flow: options configure buckets, threads, runtime, futexes per thread, shared/private mode, silent mode, and `mlockall`. The benchmark defaults threads to online CPUs, pins each worker, starts them behind a condition barrier, sleeps for runtime seconds, toggles `done`, joins, aggregates per-thread throughput, and frees futex arrays.

State and persistence: global bench timing variables are defined here. Static `params`, `done`, `futex_flag`, startup barrier state, and stats hold runtime state. No files persist.

Dependencies and integration: depends on futex wrappers, perf CPU maps, pthread affinity, mutex/cond wrappers, stats, `mlockall`, and futex bucket sysctl helper in `futex.c`.

Risks: expected failures check `errno` after futex wrapper return; wrapper semantics must match. Plain `done` is shared across threads and signal path. High thread/futex counts can consume memory and alter scheduler behavior.

Test signals: private/shared modes, custom buckets, mlockall, silent output, high CPU-count scaling, and expected EAGAIN/EWOULDBLOCK failure behavior.
