# sources/distributed-fs/ceph-client/io_uring/futex.c

## Purpose
`futex.c` implements io_uring futex wait, waitv, wake, cancellation, and per-ring futex data caching.

## Important APIs, Types, And Functions
- `struct io_futex` stores user address, expected value, mask, futex flags, waitv count, and waitv unqueued state.
- `struct io_futex_data` wraps a single `futex_q` and request pointer.
- `struct io_futexv_data` stores ownership bit and flexible wait vector.
- `io_futex_prep()` and `io_futexv_prep()` validate SQEs and set inflight tracking.
- `io_futex_wait()`, `io_futexv_wait()`, and `io_futex_wake()` issue waits/wakes.
- `io_futex_cancel()` and `io_futex_remove_all()` integrate with generic cancellation.
- `io_futex_cache_init/free()` manage the per-ring allocation cache.

## Control Flow
Single futex wait prep validates flags, value, and mask. Issue allocates cached wait data under submit lock, initializes `futex_q`, calls `futex_wait_setup()`, and if successfully queued adds the request to `ctx->futex_list` and skips immediate completion. Wake callbacks set result zero, assign task-work completion, and queue completion.

Waitv prep allocates a vector, parses userspace waitv entries, and stores async data. Issue calls `futex_wait_multiple_setup()`, handles immediate errors, successful queueing, or races where a wake occurred during setup. Cancellation unqueues the futex or claims waitv ownership, removes the request from the hlist, sets `-ECANCELED`, and queues task work.

## State And Persistence
Per-ring state includes `ctx->futex_cache` and `ctx->futex_list`. Request async data holds futex queue/vector data until wake, cancel, or immediate failure. Inflight tracking ensures file/task exit cancellation can find queued waits.

## Dependencies And Integration Points
The file depends on kernel futex internals, io_uring task-work completion, generic cancellation helpers, allocation cache, submit locking, and `REQ_F_ASYNC_DATA` ownership.

## Risks And Edge Cases
Wait requests complete asynchronously and must remain discoverable for cancellation. Waitv uses an ownership bit to serialize wake and cancel completions. A zero mask is invalid for single wait. `futex_wait_multiple_setup()` can both queue and race with wake, requiring special `futexv_unqueued` handling. Cache objects must be returned exactly once.

## Test Signals
Tests should cover wait/wake success, wrong expected values, invalid flags/masks, cancellation while queued, cancellation racing wake, waitv immediate wake index, file/task exit cancellation, cache cleanup, and strict wake returning zero for zero wake count.
