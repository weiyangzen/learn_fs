# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-common.h

## Purpose
Defines common utilities for the GlusterFS I/O framework: negative-errno result handling, synchronization barriers, and configurable thread-pool startup/wait helpers.

## APIs, Types, and Functions
Result macros convert syscall-style results into framework `res` values: `gf_errno_check()`, `gf_ret_check()`, `gf_res_errno()`, `gf_res_errno0()`, `gf_res_err()`, `gf_res_ptr()`, `gf_check()`, `gf_succeed()`, and `gf_res_combine()`. `gf_io_lock()` and `gf_io_unlock()` abort on impossible pthread-lock failures. `gf_io_sync_t` stores mutex/cond, timeout, retry/phase/pending counts, opaque data, and result. Thread-pool types include `gf_io_thread_pool_t`, `gf_io_thread_t`, setup/main callbacks, and `gf_io_thread_pool_config_t` with name, CPU affinity, signals, count, stack, scheduling priority, first id, timeout, and retries. APIs are `gf_io_sync_start()`, `gf_io_sync_done()`, `gf_io_sync_wait()`, `gf_io_thread_pool_start()`, and `gf_io_thread_pool_wait()`.

## Control Flow, State, and Persistence
Errors are normalized at call sites and logged with source location. Synchronization objects coordinate worker startup/shutdown phases with retries and timeout. Thread pools maintain a list of worker records under mutex until all threads terminate.

## Dependencies and Integration
Depends on pthreads, errno, urcu compiler hints, logging, libglusterfs message IDs, common-utils, and compat errno. Used by `gf-io.h`, legacy and io_uring engines, and other threaded components.

## Risks and Test Signals
Risks include passing positive errno values, treating negative results as standard errno incorrectly, deadlocks in sync barriers, scheduler priority portability, and CPU-affinity gaps. Test signals include result-conversion unit tests, timeout/retry synchronization tests, thread naming/priority failure injection, and worker startup/cleanup leak checks.
