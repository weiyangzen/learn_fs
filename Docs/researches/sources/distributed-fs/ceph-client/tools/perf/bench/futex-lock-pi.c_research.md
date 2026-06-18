# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex-lock-pi.c

Purpose: benchmarks priority-inheritance futex lock/unlock throughput, either contending on one global PI futex or using one futex per worker.

Important APIs/types/functions: `bench_futex_lock_pi()` sets up the run. `create_threads()` allocates/pins workers and chooses shared versus per-worker futex. `workerfn()` loops `futex_lock_pi()`, sleeps briefly while holding the lock, and `futex_unlock_pi()`. `print_summary()` reports ops/sec and bucket state.

Control flow: options configure buckets, threads, runtime, multi-futex mode, shared/private futex, mlockall, and silent mode. The run defaults threads to online CPUs, initializes stats/barriers, starts workers, sleeps runtime, toggles done, joins, frees per-worker futexes in multi mode, and reports.

State and persistence: global static `global_futex`, worker array, params, barrier state, and stats. No persistent files; optional futex hash bucket sysctl write is performed through helper if requested.

Dependencies and integration: depends on PI futex syscalls, perf CPU map affinity, pthreads, mutex/cond wrappers, stats, and futex helper declarations.

Risks: PI futex support and permissions vary by kernel. Shared `done` is unsynchronized. The 1 microsecond sleep intentionally changes lock hold time and may dominate on some systems. Multi mode changes benchmark from contention to mostly syscall cost.

Test signals: single and multi futex modes, shared/private flags, custom bucket setting, no-PI-support behavior, and throughput under varying thread counts.
