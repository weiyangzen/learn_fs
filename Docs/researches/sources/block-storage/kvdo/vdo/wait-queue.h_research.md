# File Research: sources/block-storage/kvdo/vdo/wait-queue.h

## Purpose
Defines intrusive wait-queue data structures and APIs. The file documents the circular-list representation and provides inline helpers for initialization and simple state queries.

## Public Types
- `struct wait_queue`: queue tail pointer plus length.
- `waiter_callback`: callback invoked when a waiter is notified.
- `waiter_match`: predicate used to extract matching waiters.
- `struct waiter`: intrusive queue node with `next_waiter` and optional per-waiter callback.

## Public API
- Inline helpers:
  - `is_waiting()`
  - `initialize_wait_queue()`
  - `has_waiters()`
  - `count_waiters()`
- Queue operations:
  - `enqueue_waiter()`
  - `notify_all_waiters()`
  - `notify_next_waiter()`
  - `transfer_all_waiters()`
  - `get_first_waiter()`
  - `dequeue_matching_waiters()`
  - `dequeue_next_waiter()`
  - `get_next_waiter()`

## Dependencies
Includes `compiler.h` and `type-defs.h`.

## Notes
The implementation is intentionally compact: the queue owns no waiter memory and uses the waiters’ embedded `next_waiter` links.
