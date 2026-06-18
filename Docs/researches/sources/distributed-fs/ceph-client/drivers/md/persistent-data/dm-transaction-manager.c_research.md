<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.c

## Purpose
Implements the transaction manager that enforces immutable persistent metadata updates. It coordinates block allocation, copy-on-write shadowing, reference-count changes through a space map, prefetching for non-blocking clones, and the two-phase commit protocol used by dm metadata formats.

## Important APIs, Types, And Functions
`struct dm_transaction_manager` stores whether it is a clone, a pointer to the real manager, the block manager, the space map, a shadow table of blocks already copied in this transaction, and a prefetch set. `struct shadow_info` and the hash/rbtree buckets record shadowed block locations so repeated shadow requests can be optimized.

Public APIs include `dm_tm_create_non_blocking_clone()`, `dm_tm_destroy()`, `dm_tm_pre_commit()`, `dm_tm_commit()`, `dm_tm_new_block()`, `dm_tm_shadow_block()`, `dm_tm_read_lock()`, `dm_tm_unlock()`, `dm_tm_inc()`, `dm_tm_inc_range()`, `dm_tm_dec()`, `dm_tm_dec_range()`, `dm_tm_with_runs()`, `dm_tm_ref()`, `dm_tm_block_is_shared()`, `dm_tm_get_bm()`, `dm_tm_issue_prefetches()`, `dm_tm_create_with_sm()`, and `dm_tm_open_with_sm()`.

`__shadow_block()` allocates a new block, decrements the original, reads the original, allocates a zeroed writable destination, copies data, and returns the new writable block. `dm_tm_shadow_block()` first asks the space map whether children need ref increments and avoids re-shadowing blocks already shadowed in the same transaction when safe.

## Control Flow
Normal creation/open uses `dm_sm_metadata_init()` plus `dm_tm_create()` to form the cyclic transaction-manager/metadata-space-map pair. New blocks are allocated from the space map, write-locked zeroed through the block manager, and recorded as shadows. Shadowing checks whether the original is shared. If the block is already shadowed and child increments are not needed, it write-locks the existing block; otherwise it copies to a new block and records the new location.

Commit is two-phase. `dm_tm_pre_commit()` commits the space map and flushes all dirty metadata except the caller's superblock. The caller then write-locks and updates the superblock. `dm_tm_commit()` wipes the shadow table, unlocks the superblock, and flushes again, making the root update durable after all dependent metadata.

Non-blocking clones support fast-path reads by using `dm_bm_read_try_lock()` against the real manager and queueing prefetch requests on `-EWOULDBLOCK`; mutating operations on clones return `-EWOULDBLOCK` or BUG for void mutators.

## State And Persistence
The shadow table is per-transaction runtime state and is cleared only at commit or destroy. Persistent state changes are mediated by the space map and dirty block-manager buffers. `dm_tm_with_runs()` coalesces adjacent block references for efficient range inc/dec. The manager's correctness depends on the space map's committed/current snapshots.

## Dependencies And Integration Points
This file depends on block manager, generic and concrete space maps, internal hash helper, Linux mutex/hash/rbtree/slab/export APIs, and device-mapper logging. Btrees, arrays, and space maps all call into this manager for copy-on-write and refcounts.

## Risks
Commit ordering is data-integrity critical: the superblock/root must not be made durable before the metadata it references. Shadowing implicitly decrements the original, so callers must not keep using the original writable path afterward. If child references are not incremented when a shared internal node is copied, later deletion can free live children. The shadow table can silently fail insertion under memory pressure, which is safe but may cause redundant shadows and extra space use.

## Test Signals
Tests should verify two-phase commit ordering under simulated write failures, repeated shadow requests in one transaction, shared-block child increment behavior, new-block allocation rollback on write-lock failure, non-blocking clone prefetch behavior, range coalescing with `dm_tm_with_runs()`, and open/create integration with metadata space maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.c -->
