# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/thloop.c

## Purpose
This workload creates one or more threads that spin in a stable `test_loop` symbol, enabling perf tests for threaded sampling, reports, and symbol aggregation.

## Important APIs, Types, And Functions
The key exported shape is `noinline void test_loop(void)`. Other functions are `thfunc()` and workload entry `thloop()`, registered with `DEFINE_WORKLOAD(thloop)`. It uses `pthread_create()`, `pthread_join()`, `calloc()`, `free()`, `signal()`, `alarm()`, and `atoi()`.

## Control Flow
`thloop()` parses duration and thread count, rejects non-positive values, installs signal handlers, allocates a `pthread_t` array, starts worker threads for indexes 1 through `nt - 1`, arms the alarm, and runs `test_loop()` on the main thread. On creation failure it sets `done` so already-started threads exit, then joins all started threads and frees memory.

## State, Dependencies, And Integration
Shared process state is the `volatile sig_atomic_t done` flag. The loop function is passed indirectly to workers, preserving a clear call target. The workload depends on pthreads and integrates with perf tests that inspect per-thread samples.

## Risks And Test Signals
The thread list uses index 0 for the main thread and starts at index 1 by design. Risks include excessive requested thread counts and scheduler variance. Success signals include clean timeout exit and perf samples attributed to `test_loop` across multiple threads.
