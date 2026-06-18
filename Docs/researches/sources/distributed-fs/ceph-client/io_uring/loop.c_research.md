<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/loop.c -->
# sources/distributed-fs/ceph-client/io_uring/loop.c

## Purpose
`loop.c` implements a ring-local loop runner used when `ctx->loop_step` is installed. It lets an io_uring context execute repeated step callbacks from `io_uring_enter()` while waiting for CQ progress, running task work/local work, handling signals, and flushing CQ overflow.

## Important APIs, Types, and Functions
- `io_run_loop()` is the exported entry point used by `io_uring_enter()` when `io_has_loop_ops(ctx)` is true.
- `__io_run_loop()` drives repeated `ctx->loop_step(ctx, &lp)` callbacks until the callback returns `IOU_LOOP_STOP`.
- `io_loop_nr_cqes()` computes how far the current CQ tail is from `lp.cq_wait_idx`.
- `io_loop_wait_start()`, `io_loop_wait_finish()`, and `io_loop_wait()` update `ctx->cq_wait_nr`, set task state, schedule if no local/CQ/check work is pending, and restore state.

## Control Flow
`io_run_loop()` first checks `io_allowed_run_tw(ctx)` to ensure task_work may run, then locks `ctx->uring_lock` and calls `__io_run_loop()`. Each iteration verifies `loop_step` still exists, calls it with an `iou_loop_params` instance, stops on `IOU_LOOP_STOP`, rejects unknown return values, optionally waits until `cq_wait_idx` is reached, runs pending task work outside the mutex, handles signals, runs local io_uring work while locked, and flushes CQ overflow if needed.

## State and Persistence Behavior
The module does not own persistent data beyond fields in `io_ring_ctx`: `loop_step`, `rings->cq.tail`, `cq_wait_nr`, local work queues, and `check_cq`. `struct iou_loop_params` carries the step callback's CQ wait hint for the current iteration only.

## Dependencies and Integration Points
It depends on `io_uring.h` for ring locking, task-work helpers, CQ overflow flushing, and `io_allowed_run_tw()`, plus `wait.h` for `IO_CQ_WAKE_INIT`. The integration point is the early branch in `io_uring_enter()`, which diverts normal submit/wait behavior to `io_run_loop()`.

## Risks and Edge Cases
- `loop_step` can disappear while entering the loop; this returns `-EFAULT`.
- Waiting releases `uring_lock`, so callback state must tolerate concurrent wakeups and ring changes.
- Signal pending returns `-EINTR`.
- Unknown callback return values are treated as `-EINVAL`.
- CQ overflow must be flushed while locked to keep loop wait decisions accurate.

## Test Signals
Tests should install a loop step that continues, stops, waits for CQ tail movement, observes task work, handles signals, and triggers CQ overflow. Negative tests should cover missing `loop_step` and invalid callback return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/loop.c -->
