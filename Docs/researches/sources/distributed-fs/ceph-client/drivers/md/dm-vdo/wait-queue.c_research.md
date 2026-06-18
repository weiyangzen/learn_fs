# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/wait-queue.c

## Purpose
`wait-queue.c` implements VDO's lightweight callback wait queue. It provides FIFO enqueue, dequeue, transfer, selective extraction, and notification operations for VDO resources such as VIO pools without using Linux wait queues.

## Important APIs, Types, and Functions
The file implements `vdo_waitq_enqueue_waiter()`, `vdo_waitq_transfer_all_waiters()`, `vdo_waitq_notify_all_waiters()`, `vdo_waitq_get_first_waiter()`, `vdo_waitq_dequeue_matching_waiters()`, `vdo_waitq_dequeue_waiter()`, and `vdo_waitq_notify_next_waiter()`. The underlying data structure is a circular singly linked FIFO represented by a tail pointer and a length.

## Control Flow
Enqueue checks that a waiter is not already linked, then either self-links it as the first entry or splices it after the tail and advances the tail pointer. Dequeue returns the oldest waiter, updates the circular link or empties the queue, clears the waiter's `next_waiter`, and decrements length. Notify operations dequeue entries then invoke either an explicit callback or the waiter's stored callback.

## State and Persistence Behavior
All state is volatile and in-memory. `transfer_all_waiters()` can splice two queues in constant time by swapping head links and moving length, then reinitializes the source. `notify_all_waiters()` first transfers to a local queue, preventing callbacks that re-enqueue waiters from creating an infinite loop over newly added entries.

## Dependencies and Integration Points
The implementation depends on VDO assertions and status codes plus the declarations in `wait-queue.h`. It is integrated by VIO pools and other VDO resource allocators that operate on specific VDO workqueue threads and therefore do not need kernel waitqueue locking semantics.

## Risks and Test Signals
Risks are list corruption from double enqueue, incorrect tail/head splicing, callbacks re-entering queue operations, and length drift. Tests should cover empty/single/multiple enqueue-dequeue sequences, transfer into empty and non-empty queues, notify-all with callbacks that enqueue new waiters, and matching extraction preserving relative order for matched and unmatched entries.
