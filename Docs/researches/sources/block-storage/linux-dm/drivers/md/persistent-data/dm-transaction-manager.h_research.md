# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-transaction-manager.h

## Purpose
Public interface and contracts for the persistent-data transaction manager.

## Core Contract
The transaction manager scopes a metadata transaction and enforces immutability of on-disk data structures. Clients should not mutate metadata blocks directly through the block manager.

## Two-Phase Commit
1. Make all non-superblock changes, then call `dm_tm_pre_commit()` to flush them.
2. Lock and update the superblock, then call `dm_tm_commit()`, which unlocks and flushes the superblock. No other blocks should be updated during this second phase.

## Write Access
- `dm_tm_new_block()` returns a zeroed, write-locked new block.
- `dm_tm_shadow_block()` allocates and copies a block for copy-on-write mutation, drops the original reference, and tells callers if copied children need refcount increments.
- `dm_tm_read_lock()` and `dm_tm_unlock()` provide validated read access.

## Refcount Helpers
`dm_tm_inc`, `dm_tm_inc_range`, `dm_tm_dec`, `dm_tm_dec_range`, `dm_tm_ref`, `dm_tm_block_is_shared`, and `dm_tm_with_runs`.

## Non-Blocking Clone
`dm_tm_create_non_blocking_clone()` creates a fast-path read clone where mutating/blocking operations return `-EWOULDBLOCK`; missed blocks can later be prefetched with `dm_tm_issue_prefetches()` on the real manager.

## Construction Helpers
`dm_tm_create_with_sm()` and `dm_tm_open_with_sm()` create/open a transaction manager paired with a metadata space map, reserving the superblock location from allocation.
