<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.h

## Purpose
Declares the persistent-data transaction manager API. It is the main coordination layer that clients use to allocate, read, shadow, reference-count, and commit metadata blocks safely.

## Important APIs, Types, And Functions
The opaque `struct dm_transaction_manager` owns transaction scope. Lifecycle and construction APIs are `dm_tm_destroy()`, `dm_tm_create_non_blocking_clone()`, `dm_tm_create_with_sm()`, and `dm_tm_open_with_sm()`. Commit APIs are `dm_tm_pre_commit()` and `dm_tm_commit()`, with comments specifying the two-phase protocol.

Writable block APIs are `dm_tm_new_block()` and `dm_tm_shadow_block()`. Read APIs are `dm_tm_read_lock()` and `dm_tm_unlock()`. Refcount APIs are `dm_tm_inc()`, `dm_tm_inc_range()`, `dm_tm_dec()`, `dm_tm_dec_range()`, `dm_tm_with_runs()`, `dm_tm_ref()`, and `dm_tm_block_is_shared()`. `dm_tm_get_bm()` exposes the underlying block manager, and `dm_tm_issue_prefetches()` flushes queued prefetches from non-blocking clone reads.

## Control Flow
Clients make all metadata mutations through new/shadow block calls, update structures in returned write locks, unlock through the transaction manager, and commit using pre-commit followed by a final superblock update and `dm_tm_commit()`. Fast-path clients can create a non-blocking clone that performs try-lock reads and returns `-EWOULDBLOCK` instead of sleeping.

## State And Persistence
The header documents immutable metadata semantics: shadowing copies a block and drops the original reference; `inc_children` tells callers whether copied child references need adjustment. The two-phase commit comments define the persistence ordering expected by all on-disk metadata users.

## Dependencies And Integration Points
The header depends on `dm-block-manager.h` and forward-declares `dm_space_map`. It is consumed by btree, array, bitset, and space-map implementations plus dm targets that own superblocks.

## Risks
The API is easy to misuse if callers directly access the block manager for writable metadata or unlock a partially updated superblock. Void refcount mutators must not be called on non-blocking clones. `dm_tm_new_block()` returns zeroed blocks and callers must fully initialize them before unlock to avoid stale or invalid metadata.

## Test Signals
Contract tests should cover clone behavior, commit protocol sequencing, shadow-block `inc_children` handling, read/write locking via validators, direct refcount operations, root serialization with metadata-space maps, and failure paths around allocation and flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.h -->
