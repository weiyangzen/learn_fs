# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/async.h

## Purpose
`async.h` declares the GlusterFS asynchronous worker framework built on URCU wait-free queues/stacks and process signals. It exposes initialization, shutdown, thread-count adjustment, and an inline `gf_async()` enqueue-or-run helper.

## Important APIs, Types, and Functions
- `gf_async_t`: queued work item containing a callback and `cds_wfcq_node`.
- `gf_async_worker_t`: worker control record with async self-job, available stack node, pthread id, numeric id, and running flag.
- `gf_async_queue_t`: cache-line-aligned URCU wait-free queue head/tail.
- `gf_async_control_t`: global controller with queue, available worker stack, worker table, pthread barrier, signal masks/handlers, pid, max thread count, packed running/stopping counts, and enabled flag.
- `gf_async_init()`, `gf_async_fini()`, `gf_async_adjust_threads()`: lifecycle declarations.
- `gf_async(async, cbk)`: inline submit helper.

## Control Flow
When `gf_async_ctrl.enabled` is false, `gf_async()` invokes the callback synchronously. When enabled, it sets `async->cbk`, initializes the queue node, enqueues it into the global wait-free queue, and if the queue was previously empty sends `GF_ASYNC_SIGQUEUE` to the process to wake the leader worker.

## State and Persistence
State is runtime-only and process-wide in `gf_async_ctrl`. Worker counts are packed into a 32-bit field with high 16 bits for running and low 16 bits for stopping. Signal handlers/masks are saved in the controller for restoration.

## Dependencies and Integration Points
Depends on URCU `wfcqueue`/`wfstack`, pthreads, signals, common-utils logging/abort helpers, and Gluster context initialization. It integrates with code that wants asynchronous callback execution without each caller owning a thread pool.

## Risks and Edge Cases
- It uses `SIGALRM` and `SIGVTALRM`; conflicts with other process users of those signals can break scheduling.
- Enqueued `gf_async_t` storage must outlive asynchronous execution.
- `kill()` failure in the wake path is fatal via `gf_async_fatal()`.
- Counts are limited to 16-bit subfields, though public max is 128 threads.

## Test Signals
Test disabled synchronous execution, enabled enqueue wake behavior, signal-handler installation/restoration in implementation, worker count adjustment boundaries, queue-empty wake decisions, and object lifetime discipline for stack-allocated async items.
