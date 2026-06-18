# sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-common.c

## Purpose
`gf-io-common.c` implements shared synchronization and thread-pool infrastructure for the newer GlusterFS I/O framework. It provides monotonic timed barriers, thread creation/configuration, naming, signal masking, optional CPU affinity, priority setup, and pool teardown.

## Important APIs, Types, and Functions
- `gf_io_sync_start()`, `gf_io_sync_done()`, `gf_io_sync_wait()`: create and operate a multi-party sync/barrier object with timeout and retry handling.
- `gf_io_thread_pool_start()`, `gf_io_thread_pool_wait()`: create, initialize, join, and destroy thread pools.
- `gf_io_thread_name()`, `gf_io_thread_mask()`, `gf_io_thread_affinity()`: configure per-thread name, signal mask, and Linux CPU pinning.
- `gf_io_thread_attr_priority()`, `gf_io_thread_attr()`: build pthread attributes for stack size and optional scheduler priority.
- Internal `gf_io_thread_init()` and `gf_io_thread_main()`: run the three-phase startup handshake before invoking engine-specific setup/main callbacks.

## Control Flow
`gf_io_sync_start()` records a monotonic absolute timeout, initializes mutex and condition variable, and sets count/pending/phase. `gf_io_sync_done()` decrements pending and either signals completion or waits for all participants, then destroys the sync object for the waiter. `gf_io_sync_wait()` acts as a reusable phase barrier: the last participant resets pending to count, increments phase, and broadcasts; others wait for phase change.

Thread-pool start initializes the pool, creates a sync object with `num_threads + 1` participants, starts pthreads, then steps through creation, configuration, and engine-specific setup phases. Each worker stores a thread-local `gf_io_thread_t`, configures name/mask/affinity, calls the pool config setup function, and then runs the config main function. On startup failure, created threads are timed-joined and the pool is destroyed.

## State and Persistence
State is in-memory only: sync counters, phase, result, timeout, thread list, pthread ids, pool mutex, and thread-local `gf_io_thread`. Thread names and scheduler attributes are process-visible runtime state.

## Dependencies and Integration Points
Uses pthreads, `CLOCK_MONOTONIC` condition variables, `CLOCK_REALTIME` timed joins on Linux, `urcu/uatomic.h`, Gluster logging/check helpers, list utilities, and the `gf_io_thread_pool_config_t` callback contract from `gf-io-common.h`. It is called by `gf-io.c` to start worker threads for an active engine.

## Risks and Edge Cases
- Timeout retry exhaustion calls `GF_ABORT()` when retries are zero.
- Variable-length `pthread_t ids[cfg->num_threads]` requires a sane nonzero thread count.
- Priority setup may fail without privileges; callers need to surface errors cleanly.
- Affinity indexing fails if fewer CPUs are set than requested threads.
- Startup has several phases; wrong pending counts can deadlock.

## Test Signals
Tests should cover sync success, timeout/retry accounting, error propagation through barriers, startup failure cleanup, pool wait teardown, thread naming limits, disabled/null CPU affinity, and signal mask behavior.
