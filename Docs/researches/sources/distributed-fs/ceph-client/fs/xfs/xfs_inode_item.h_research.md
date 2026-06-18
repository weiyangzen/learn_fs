# sources/distributed-fs/ceph-client/fs/xfs/xfs_inode_item.h

## Purpose
`xfs_inode_item.h` declares the in-memory inode log item, its clean-state helper, public lifecycle/abort functions, format conversion helper, and slab cache. The full 62-line header was read.

## Important APIs, Types, and Functions
`struct xfs_inode_log_item` embeds the generic log item, back pointer to `struct xfs_inode`, lock flags, per-transaction dirty flags, `ili_lock`, last flushed fields, currently logged fields, last flush LSN, and commit sequence numbers for fsync/datasync optimization. `xfs_inode_clean` returns true when there is no inode item or no logged inode fields.

The header declares `xfs_inode_item_init`, `xfs_inode_item_destroy`, `xfs_iflush_abort`, `xfs_iflush_shutdown_abort`, `xfs_inode_item_format_convert`, and the slab cache `xfs_ili_cache`.

## Control Flow
Transactions initialize and use the inode log item to track dirty inode state. Flush and shutdown paths call the abort helpers to clear logging/flush state safely. Recovery can call the format converter for old 32-bit inode log format records.

## State and Persistence Behavior
The log item is runtime state that controls when inode changes are present in the journal, pinned, written to inode cluster buffers, and safe to consider clean. Commit sequence numbers persist only in memory and optimize data integrity sync decisions.

## Dependencies and Integration Points
The header is consumed by inode cache, inode core operations, transaction code, log recovery, AIL push, and buffer writeback. It depends on XFS log item, inode, mount, buffer, and log format structures.

## Risks and Edge Cases
`ili_lock` is the synchronization point between dirtying, flushing, and completion even though those paths hold different inode locks. Callers must not treat `xfs_inode_clean` as equivalent to no pending writeback unless they also understand pin/flush state. Destroy requires no attached buffer and no AIL membership.

## Test Signals
Signals include lifecycle creation/destruction, dirty-to-clean transitions through commit and buffer iodone, abort behavior with and without attached buffers, shutdown abort while flushing, `xfs_inode_clean` behavior for no item and empty fields, and old-format log recovery conversion.
