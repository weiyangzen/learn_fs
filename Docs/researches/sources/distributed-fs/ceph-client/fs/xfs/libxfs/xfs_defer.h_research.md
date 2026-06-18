# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_defer.h

## Purpose
`xfs_defer.h` defines the generic deferred-operation interface used by XFS metadata subsystems. It declares pending-work containers, operation callback tables, resource-capture structures, public finish/cancel/recovery APIs, and the pause/barrier controls used to order deferred work.

## Important APIs, Types, And Functions
`struct xfs_defer_pending` links one batch of deferred work, its work-item list, logged intent item, logged done item, callback table, item count, and flags. `XFS_DEFER_PAUSED` marks a batch that should be carried forward without finishing. `struct xfs_defer_op_type` is the provider contract: create/abort intent, create done, finish item, optional finish cleanup, cancel item, recover work, and relog intent.

The header declares operation providers such as `xfs_bmap_update_defer_type`, refcount/rmap providers, extent-free providers, attr, and exchmaps. `struct xfs_defer_resources` captures buffers and inodes that must survive transaction rolls. `struct xfs_defer_capture` stores deferred ops, transaction flags, reservations, log reservation, and held resources for recovery continuation. Public functions include add, finish, cancel, move, capture/continue/abort, recovery start/finish, cache init/destroy, item pause/unpause, and barrier insertion.

## Control Flow
The inline `xfs_defer_add_item()` appends a work item to a pending batch and increments its count. All higher-level flow is implemented in `xfs_defer.c`: callers add work during a permanent-reservation transaction, finish rolls and processes the list, and recovery can capture then continue lists in later transactions.

## State And Persistence
The header describes in-memory structures whose intent/done pointers refer to persistent log items. The resource capture arrays persist references, not on-disk data, across transaction boundaries. Counts and flags drive whether batches are appended, paused, or split by barriers.

## Dependencies And Integration Points
It depends on XFS transaction, log item, btree cursor, buffer, and inode types. Provider declarations tie it to bmap, rmap, refcount, allocation, attr, and exchange-map subsystems. Parent pointer rename paths rely on the five-inode capture limit documented here.

## Risks
Callback implementations must obey the semantics documented by the type table. A provider that fails to cancel items, update unfinished work before `-EAGAIN`, or relog intents correctly can break recovery. The fixed resource limits (`XFS_DEFER_OPS_NR_INODES`, `XFS_DEFER_OPS_NR_BUFS`) are part of correctness assumptions for complex renames and should not be exceeded by future operations without widening the structure and tests.

## Test Signals
Build tests should cover all provider declarations under feature combinations. Runtime signals include mixed deferred-op chains, barriers separating adjacent same-type work, paused/unpaused batches, recovery capture with held inodes and buffers, and provider-specific cancellation after injected failures.
