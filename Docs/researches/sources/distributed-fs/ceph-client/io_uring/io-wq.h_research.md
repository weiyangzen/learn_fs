# sources/distributed-fs/ceph-client/io_uring/io-wq.h

## Purpose
The header defines io-wq public types, flags, cancellation results, and worker-pool APIs used by io_uring core and cancellation paths.

## Important APIs, Types, And Functions
- Work flags: `IO_WQ_WORK_CANCEL`, `IO_WQ_WORK_HASHED`, `IO_WQ_WORK_UNBOUND`, `IO_WQ_WORK_CONCURRENT`, and `IO_WQ_HASH_SHIFT`.
- `enum io_wq_cancel` distinguishes pending cancellation success, running cancellation signal, and not found.
- `struct io_wq_hash` holds a shared refcounted hash serialization bitmap and wait queue.
- `struct io_wq_data` passes shared hash and owner task to `io_wq_create()`.
- Public APIs cover create/exit/enqueue/hash/cancel/affinity/max-workers and worker sleep/running hooks.
- `io_wq_current_is_worker()` identifies current io-wq worker context.

## Control Flow
Inline helpers check hashed work flags, drop hash refs, and provide no-op worker scheduler hooks when `CONFIG_IO_WQ` is disabled.

## State And Persistence
`io_wq_hash` persists across pools through refcounting. Work flags persist in `io_wq_work->flags` and drive queue selection, cancellation, and hash serialization.

## Dependencies And Integration Points
It depends on refcounting and `io_uring_types.h`. It is included by eventfd, cancellation, worker-pool implementation, and core request paths.

## Risks And Edge Cases
The upper 8 flag bits encode hash keys, so flag layout must remain synchronized with `io-wq.c`. `io_wq_current_is_worker()` relies on PF_IO_WORKER and `worker_private`, so scheduler integration must set/clear that pointer correctly.

## Test Signals
Builds with and without `CONFIG_IO_WQ`, async worker execution tests, eventfd async-only notification tests, and cancellation tests validate this interface.
