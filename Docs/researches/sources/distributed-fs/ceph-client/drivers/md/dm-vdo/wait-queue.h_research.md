# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/wait-queue.h

## Purpose
`wait-queue.h` defines VDO's small, callback-oriented wait queue abstraction. It is intended for VDO's thread-based resource scheduling where callers need FIFO callbacks but not Linux waitqueue sleeping, locking, priorities, or timers.

## Important APIs, Types, and Functions
`struct vdo_wait_queue` stores a tail pointer and waiter count. `struct vdo_waiter` stores the next pointer and optional callback. Function pointer types `vdo_waiter_callback_fn` and `vdo_waiter_match_fn` define notification and filtering contracts. Inline helpers include `vdo_waiter_is_waiting()`, `vdo_waitq_init()`, `vdo_waitq_has_waiters()`, and `vdo_waitq_num_waiters()`.

## Control Flow
Clients initialize a queue, embed or allocate waiters, set each waiter's callback, and enqueue when a resource is unavailable. Resource return paths call `vdo_waitq_notify_next_waiter()` or `vdo_waitq_notify_all_waiters()` to resume queued operations. Matching extraction supports moving selected waiters to a separate queue for targeted wakeups.

## State and Persistence Behavior
The queue is in-memory only. The circular-list invariant is documented in detail: empty queues have a null tail, singleton queues self-link, and multi-entry queues have the tail link point to the oldest entry. `next_waiter == NULL` is both the unqueued sentinel and the predicate used by `vdo_waiter_is_waiting()`.

## Dependencies and Integration Points
The header uses only basic Linux compiler/types support and is included by VIO pool code and other VDO components that need simple asynchronous waiter callbacks. It intentionally avoids `linux/wait.h` because the VDO model already supplies serialized thread ownership.

## Risks and Test Signals
Callers must not enqueue a waiter already on any queue and must not assume thread-safe access without external serialization. Tests should validate queue initialization, waiter waiting predicates, length accounting, FIFO order, and behavior when callbacks are supplied either per waiter or as a notification override.
