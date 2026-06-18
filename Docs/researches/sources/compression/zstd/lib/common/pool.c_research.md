# sources/compression/zstd/lib/common/pool.c

## Purpose
`pool.c` implements zstd's internal thread pool used by multi-threaded compression. With `ZSTD_MULTITHREAD` enabled it provides a bounded job queue, worker lifecycle management, dynamic thread limits, and custom allocator support. Without multithreading it compiles to a synchronous single-context fallback.

## Important APIs, Types, and Functions
`POOL_job` stores a `POOL_function` and opaque pointer. `POOL_ctx_s` stores custom memory hooks, thread handles, `threadCapacity`, `threadLimit`, circular queue indices and size, busy-count state, mutexes, condition variables, and shutdown flag. Public entry points are `ZSTD_createThreadPool()`, `POOL_create()`, `POOL_create_advanced()`, `POOL_free()`, `POOL_joinJobs()`, `ZSTD_freeThreadPool()`, `POOL_sizeof()`, `POOL_resize()`, `POOL_add()`, and `POOL_tryAdd()`. Internal helpers include the worker `POOL_thread()`, `POOL_join()`, `POOL_resize_internal()`, `isQueueFull()`, and `POOL_add_internal()`.

## Control Flow, State, and Persistence
Creation allocates and zeroes the context, allocates a circular queue of `queueSize + 1` entries, initializes synchronization primitives, allocates thread handles, and starts workers. Worker threads wait while the queue is empty or the busy count has reached `threadLimit`, pop one job under the mutex, signal pushers, execute outside the lock, decrement `numThreadsBusy`, and signal completion. `POOL_add()` blocks while full; `POOL_tryAdd()` returns 0 if full. `POOL_joinJobs()` waits until no queued or running jobs remain. `POOL_free()` sets shutdown, broadcasts both conditions, joins created threads, destroys synchronization objects, and frees allocations. The non-threaded fallback executes jobs immediately through a static `g_poolCtx`.

## Dependencies and Integration Points
The file depends on zstd custom allocation (`allocations.h`, `ZSTD_customCalloc()`, `ZSTD_customFree()`), `zstd_deps.h`, `debug.h`, `pool.h`, and, in threaded builds, `threading.h`. It is used by zstd multi-threaded compression contexts to schedule block compression and related background work while preserving a common API for single-threaded builds.

## Risks and Test Signals
Concurrency risks include blocking forever if jobs never signal completion, resizing to a smaller `threadLimit` while queued work exists, shutdown with non-empty queues, and caller lifetime bugs for `opaque` data because jobs may run asynchronously. `POOL_resize_internal()` can leave `threadLimit` expanded even if creating an additional thread fails. Useful tests cover queue size zero semantics, blocking and nonblocking add behavior, `POOL_joinJobs()` after many jobs, resizing up and down during activity, custom allocator failure injection, `POOL_free(NULL)`, and parity with the non-threaded immediate-execution fallback.
