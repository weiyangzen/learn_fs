# sources/distributed-fs/ceph-client/io_uring/cancel.c

## Purpose
`cancel.c` implements io_uring cancellation by userdata, file, opcode, sequence, task, ring, and exit state. It coordinates cancellation across io-wq, poll, waitid, futex, timeout, deferred, uring_cmd, iopoll, and task-work paths.

## Important APIs, Types, And Functions
- `io_async_cancel_prep()` parses `IORING_OP_ASYNC_CANCEL` SQEs.
- `io_async_cancel()` issues async cancellation and completes the cancel request.
- `io_sync_cancel()` implements registered synchronous cancel with optional timeout.
- `io_cancel_req_match()` centralizes match criteria.
- `io_try_cancel()` attempts io-wq, poll, waitid, futex, and timeout cancellation.
- `io_cancel_remove()` and `io_cancel_remove_all()` remove requests from subsystem hlist queues using subsystem-specific callbacks.
- `io_uring_try_cancel_requests()` and `io_uring_cancel_generic()` drive broad cancellation during ring teardown, task exit, or exec.

## Control Flow
Async cancel prep validates reserved fields and mutually exclusive flags, then records userdata, fd, or opcode. Execution builds `io_cancel_data`, optionally resolves a normal or fixed file, and calls `__io_async_cancel()`. That routine first tries the current task context, then scans all task contexts attached to the ring under `ctx->tctx_lock` for io-wq work.

Synchronous cancel copies `io_uring_sync_cancel_reg`, validates pads/flags, resolves file references, tries cancellation, and if work is already running waits on `ctx->cq_wait` while repeatedly retrying until completion, timeout, signal/task-work error, or no matching request remains.

Exit/teardown cancellation sets `in_cancel`, starts io-wq exit, drops task context refs, iterates rings or SQPOLL contexts, drains local work, cancels deferred/poll/waitid/futex/uring_cmd/timeouts, and waits until inflight counters reach zero before cleaning or freeing task context.

## State And Persistence
Cancellation uses `ctx->cancel_seq` to avoid repeatedly matching the same request during `ALL` scans, request `cancel_seq_set/work.cancel_seq`, per-task inflight counters, `tctx->in_cancel`, wait queues, subsystem request lists, and `ctx->uring_lock`/`completion_lock`/`timeout_lock`. It changes request flags to canceled, posts failed completions, or signals running workers.

## Dependencies And Integration Points
The file depends on io-wq, task context tracking, fixed-file lookup, poll, waitid, futex, timeout, SQPOLL, uring_cmd, wait/local task work, and ring locking. It is a shared utility used by operation cancel, ring release, task exit, and exec cleanup.

## Risks And Edge Cases
Concurrency and ownership dominate risk. Running io-wq work may only be signaled and returns `-EALREADY`. Fixed files must be revalidated when locks are dropped. Linked timeouts require `timeout_lock` for safe matching. Broad cancellation must not deadlock with deferred task-run or SQPOLL ownership. Sequence matching must prevent infinite counting during cancel-all loops.

## Test Signals
io_uring cancellation tests should cover cancel by userdata, fd, fixed fd, opcode, any/all, running vs pending work, poll/timeouts/futex/waitid/uring_cmd requests, sync cancel timeout, task exit, exec, SQPOLL, and deferred task-run rings.
