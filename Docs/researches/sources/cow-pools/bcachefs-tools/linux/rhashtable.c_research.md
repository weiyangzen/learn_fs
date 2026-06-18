# File Research: sources/cow-pools/bcachefs-tools/linux/rhashtable.c

## Purpose
Userspace copy/adaptation of Linux's resizable concurrent hash table implementation. It provides the core `rhashtable` and `rhltable` behavior needed by bcachefs-tools code that expects kernel hash-table APIs.

## Key Responsibilities
- Allocates normal or nested bucket tables depending on allocation size and GFP context.
- Supports RCU-style readers and asynchronous rehashing via `work_struct`.
- Grows on high load, optionally shrinks, and handles nested table conversion.
- Implements slow-path insertion, duplicate detection, rhlist collision lists, and iterator/walker APIs.
- Frees hash tables safely after canceling resize work.

## Important APIs
- `rhashtable_init()`, `rhltable_init()`
- `rhashtable_insert_slow()`
- `rhashtable_walk_enter()`, `rhashtable_walk_start_check()`, `rhashtable_walk_next()`, `rhashtable_walk_peek()`, `rhashtable_walk_stop()`, `rhashtable_walk_exit()`
- `rhashtable_free_and_destroy()`, `rhashtable_destroy()`
- `rht_bucket_nested()`, `rht_bucket_nested_insert()`

## Implementation Notes
- Uses `future_tbl` to attach a new table while readers and mutations continue across old/new tables.
- `rht_deferred_worker()` performs grow/shrink/rehash work under `ht->mutex`.
- Insertions that hit excessive chain elasticity return `-EAGAIN` and trigger rehash.
- Iterator state tracks bucket slot, skip count, and rhlist sub-node, and rewinds with `-EAGAIN` on resize.
- Nested tables are allocated in page-sized chunks to avoid very large contiguous bucket arrays.

## Dependencies
Includes kernel-compat headers for atomics, RCU, workqueues, jhash, random, error helpers, slab/vmalloc, and `linux/rhashtable.h`.

## Risks / Porting Notes
- Correctness relies on the local RCU/workqueue/bit-lock compatibility layer behaving closely enough to Linux.
- Nested-table allocation uses `GFP_ATOMIC` and `cmpxchg`; userspace portability depends on matching shim definitions.
