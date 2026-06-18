# File Research: sources/block-storage/kvdo/vdo/wait-queue.c

## Purpose
Implements a small intrusive FIFO wait queue using a circular singly linked list. It supports enqueue, dequeue, notify, transfer, matching extraction, and debug iteration.

## Queue Model
`struct wait_queue` stores only:
- `last_waiter`: tail of the circular list,
- `queue_length`.

The head is `last_waiter->next_waiter`. An empty queue has `last_waiter == NULL`; a single waiter points to itself.

## Main Functions
- `enqueue_waiter()`: asserts the waiter is not already queued, then appends it at tail in O(1).
- `transfer_all_waiters()`: splices all waiters from one queue to another, preserving circular-list structure and emptying the source.
- `notify_all_waiters()`: moves the current queue to a temporary queue first, then drains it with `notify_next_waiter()` so callbacks can safely requeue waiters without causing an infinite loop.
- `get_first_waiter()`: returns the head/oldest waiter.
- `dequeue_matching_waiters()`: drains the source into an iteration queue, requeues nonmatches, collects matches, rolls back on enqueue error, then transfers matches to the caller’s matched queue.
- `dequeue_next_waiter()`: removes and returns the head/oldest waiter, clearing its `next_waiter`.
- `notify_next_waiter()`: dequeues one waiter and invokes either the supplied callback or the waiter’s own callback.
- `get_next_waiter()`: iteration helper for debug scans.

## Dependencies
Includes `wait-queue.h`, `permassert.h`, and `status-codes.h`.

## Invariants and Risks
- A waiter may be in at most one queue; `next_waiter == NULL` means not queued.
- Callback invocation happens after dequeue, so callbacks are free to requeue the waiter.
- The queue is not internally synchronized; callers must provide locking if used concurrently.
- `notify_next_waiter()` assumes a non-NULL effective callback after fallback to `waiter->callback`.
