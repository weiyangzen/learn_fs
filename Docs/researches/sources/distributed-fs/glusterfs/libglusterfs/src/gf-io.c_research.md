# sources/distributed-fs/glusterfs/libglusterfs/src/gf-io.c

## Purpose
`gf-io.c` is the top-level runtime for the GlusterFS I/O framework. It chooses an engine (`io_uring` when built and usable, otherwise legacy), owns global operation maps/pools, batches requests, runs setup/wait/cleanup handlers, starts worker threads, and dispatches callbacks.

## Important APIs, Types, and Functions
- Global `gf_io_t gf_io` and thread-local `gf_io_worker_t gf_io_worker`.
- `gf_io_run(name, handlers, data)`: main entry point that selects an engine and runs the framework.
- `gf_io_batch_submit()`: reserves ids, fills `gf_io_op_t` slots, submits batched/chained requests, and returns ids to callers.
- `gf_io_data_wait()`: waits for a request data slot to become unchained/available, servicing worker or flush paths meanwhile.
- `gf_io_async_handler`: executes async functions and then callbacks.
- `gf_io_worker_setup()`, `gf_io_worker_main()`, `gf_io_workers_stop()`: worker lifecycle glue around engine hooks.
- `gf_io_sync()`, `gf_io_sync_wake()`: run an async function and wait synchronously for completion.

## Control Flow
`gf_io_run()` clears global state, allocates `op_map` and `op_pool` using mmap-backed locked memory, then tries engines in order. For a matching/available engine, it calls engine setup, initializes `gf_io`, runs `gf_io_main()`, invokes engine cleanup, and returns on success; otherwise it tries the next engine and eventually returns `-ENXIO`.

`gf_io_main()` optionally starts a worker pool, runs handler setup via `gf_io_sync()`, waits in `engine.wait()`, runs handler cleanup, then stops workers and joins the pool. Worker main loops call `engine.worker()` while enabled; on shutdown they call cleanup and participate in stopping other workers. In debug builds, callback and async function latency is measured and logged when above threshold.

## State and Persistence
State is in-process global memory: engine descriptor, operation id map, operation pool, worker count, shutdown flag, and per-thread worker structs. `gf_io_alloc()` uses `mmap`, `mlock`, and `MADV_DONTFORK` where available to keep critical request state resident and out of forked children.

## Dependencies and Integration Points
Integrates `gf-io-legacy`, optional `gf-io-uring`, `gf-io-common` thread pools/sync, global logging, request id helpers/macros, and external handler callbacks. It is intended to host future async I/O and timer/callback functionality while still dispatching legacy events.

## Risks and Edge Cases
- Engine order and requested `name` determine fallback behavior.
- Worker stop posts callbacks through the same engine; broken callback dispatch can block shutdown.
- `gf_io_batch_submit()` copies request operations into pooled slots and uses chain flags; submitters must preserve lifetime until copied.
- Debug latency checks assume callbacks are quick; slow callbacks can indicate deadlocks or blocking work in the callback path.
- Locked mmap may fail under memory limits, preventing framework startup.

## Test Signals
Test engine selection by name and fallback, operation pool allocation failure cleanup, batched request id assignment including chains, `gf_io_data_wait()` with worker and non-worker callers, setup/wait/cleanup handler ordering, worker shutdown propagation, and debug latency instrumentation.
