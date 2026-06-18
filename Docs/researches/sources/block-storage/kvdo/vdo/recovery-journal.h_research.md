# File Research: sources/block-storage/kvdo/vdo/recovery-journal.h

Read completely: 313 lines.

This header documents the recovery journal design and defines `struct recovery_journal`. The long design comment explains the circular on-disk log, the `head`/`tail`/active interval, the in-memory tail block rings, the write/commit flow for VIO waiters, and the lock-counter scheme that prevents journal blocks from being reaped while referenced by active VIOs, dirty block-map pages, or slab-journal replay needs.

`struct recovery_journal` contains thread and component pointers, increment/decrement waiter queues, available-space accounting, pending decrement tracking, read-only notifier, admin state, partition pointer, block-map and slab-journal heads, last acknowledged write, tail/append/commit points, nonce/recovery count, entry capacity, free/active block lists, pending write queue, reap heads and block numbers, flush VIO, on-disk size, logical/block-map usage counters, pending write count, slab-journal commit threshold, statistics, and lock counter.

The header provides inline helpers for circular block-number mapping, check-byte computation, and increment-operation classification. It declares lifecycle, state recording, post-recovery/rebuild initialization, open, entry add, lock-reference acquire/release, drain/resume, stats, and dump APIs.

Dependencies: admin state, completion, flush/journal point/lock counter types, read-only notifier, recovery journal format, VDO layout/types, wait queues, and statistics.

Security/reliability notes: comments identify the invariants the implementation relies on: monotonic sequence numbers, reserved circular-log space, per-entry and per-page lock references, and thread-affine journal mutation.
