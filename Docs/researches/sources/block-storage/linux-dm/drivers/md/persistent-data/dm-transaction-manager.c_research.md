# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-transaction-manager.c

## Purpose
Implements the transaction manager that enforces immutable persistent metadata updates through copy-on-write shadowing, block reference counting, and two-phase commit.

## Main Structures
- `struct prefetch_set`: small hashed set of metadata blocks to prefetch after non-blocking lookup misses.
- `struct shadow_info`: entry in the current transaction’s shadow table.
- `struct dm_transaction_manager`:
  - clone flag and real manager pointer
  - block manager
  - space map
  - shadow hash table
  - prefetch set

## Important Behavior
- Shadow table records blocks already made writable in the current transaction. If a block is already a private shadow and not shared, later shadow requests can become direct write locks.
- `dm_tm_new_block()` allocates through the space map, zero-write-locks the new block, and records it as a shadow.
- `dm_tm_shadow_block()`:
  - checks whether the original is shared.
  - if already shadowed and not shared, returns a write lock on the original.
  - otherwise allocates a new block, decrements the original refcount, reads/copies original contents, write-locks the new block, and records the new block as a shadow.
  - returns `inc_children` to tell callers whether copied child references need reference increments.
- `dm_tm_pre_commit()` commits the space map and flushes dirty metadata.
- `dm_tm_commit()` wipes the shadow table, unlocks the caller’s superblock, and flushes again so the superblock lands after other metadata.
- Non-blocking clones support read-only fast-path lookups via `dm_bm_read_try_lock()`. Misses add blocks to the real manager’s prefetch set and return `-EWOULDBLOCK`; mutating operations reject clones.
- `dm_tm_with_runs()` coalesces adjacent little-endian block-number values into ranges before calling inc/dec range callbacks.

## Public API Implemented
`dm_tm_create_non_blocking_clone`, `dm_tm_destroy`, `dm_tm_pre_commit`, `dm_tm_commit`, `dm_tm_new_block`, `dm_tm_shadow_block`, `dm_tm_read_lock`, `dm_tm_unlock`, `dm_tm_inc`, `dm_tm_inc_range`, `dm_tm_dec`, `dm_tm_dec_range`, `dm_tm_with_runs`, `dm_tm_ref`, `dm_tm_block_is_shared`, `dm_tm_get_bm`, `dm_tm_issue_prefetches`, `dm_tm_create_with_sm`, `dm_tm_open_with_sm`.

## Construction
`dm_tm_create_with_sm()` and `dm_tm_open_with_sm()` tie the recursive knot between transaction manager and metadata space map by first allocating the space map object, then creating the transaction manager, then creating or opening the metadata space map.

## Role in Repository
This is the central coordinator for all persistent-data structures. Btrees, arrays, bitsets, and space maps depend on it for allocation, shadowing, reference counts, locks, and commit ordering.
