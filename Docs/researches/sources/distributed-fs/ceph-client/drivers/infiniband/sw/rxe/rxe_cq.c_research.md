# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_cq.c

## Purpose
`rxe_cq.c` implements RXE completion queue backing storage creation, resize, posting, notification, overflow event generation, and cleanup.

## Important APIs, types, and functions
Functions are `rxe_cq_from_init()`, `rxe_cq_resize_queue()`, `rxe_cq_post()`, and `rxe_cq_cleanup()`. It uses `struct rxe_cq`, `struct rxe_cqe`, `struct rxe_queue`, `struct ib_wc`, and `struct ib_event`.

## Control flow
Creation allocates a `QUEUE_TYPE_TO_CLIENT` queue sized for `struct rxe_cqe`, creates mmap metadata for userspace when requested, marks user/kernel mode, initializes `cq_lock`, and stores the actual CQE capacity. Resize delegates to `rxe_queue_resize()` under the CQ lock and updates `ibcq.cqe` on success. Posting takes `cq_lock`, checks whether the queue is full, copies the CQE into the producer slot, advances the producer, and invokes the completion handler if notification mode matches. Overflow emits `IB_EVENT_CQ_ERR`.

## State and persistence
CQ state is the queue buffer, producer/consumer indices, user mmap info, notification flags, and CQE capacity. Completion records persist in the queue until userspace or kernel consumers poll them.

## Dependencies and integration points
The file depends on RXE queue/mmap helpers, RDMA CQ event handlers, QP completer/responder paths that post CQEs, and user mmap ABI structures.

## Risks
CQ overflow is fatal at the CQ level and must signal the event handler outside the lock. `rxe_cq_from_init()` returns immediately on mmap-info failure without cleaning the queue in this function, so callers must unwind through pool cleanup. Notification flags are cleared while holding the CQ lock before calling `comp_handler`.

## Test signals
Test user and kernel CQ creation, mmap setup failures, resize smaller/larger, posting solicited and non-solicited completions under `IB_CQ_NEXT_COMP` and `IB_CQ_SOLICITED`, CQ full event delivery, and cleanup after partial creation.
