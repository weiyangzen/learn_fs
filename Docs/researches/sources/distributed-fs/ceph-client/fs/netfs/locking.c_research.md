<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/locking.c -->
# sources/distributed-fs/ceph-client/fs/netfs/locking.c

## Purpose
Coordinates buffered and direct IO exclusion for network filesystems using inode `i_rwsem` and the netfs inode `NETFS_ICTX_ODIRECT` flag. It lets parallel operations of the same class proceed while switching classes waits for outstanding work and flushes page cache state.

## Important APIs, Types, And Functions
Exports `netfs_start_io_read()`, `netfs_end_io_read()`, `netfs_start_io_write()`, `netfs_end_io_write()`, `netfs_start_io_direct()`, and `netfs_end_io_direct()`. Internal helpers are `netfs_inode_dio_wait_interruptible()`, `netfs_block_o_direct()`, and `netfs_block_buffered()`.

## Control Flow
Buffered read starts with a shared `i_rwsem` lock and succeeds quickly if no direct-IO mode is active. If direct IO is active, it upgrades via exclusive lock, clears `NETFS_ICTX_ODIRECT`, waits for outstanding DIO, then downgrades to shared. Buffered write takes exclusive first, blocks direct IO similarly, and downgrades. Direct IO does the inverse: shared fast path when direct mode is already set; otherwise exclusive lock, set `NETFS_ICTX_ODIRECT`, unmap page cache, wait for writeback, then downgrade.

## State And Persistence
No persistent state. Runtime state is `NETFS_ICTX_ODIRECT`, `inode->i_rwsem`, inode DIO count, and mapping dirty/writeback state.

## Dependencies And Integration Points
Used by filesystem read/write/direct-IO entry points before invoking netfs helpers. Depends on generic inode DIO helpers, `filemap_fdatawait()`, and `unmap_mapping_range()`.

## Risks
Deadlock risk is controlled by documented lock assumptions, but callers must pair start/end correctly. Interruptible waits can return `-ERESTARTSYS`. Direct-IO transition must handle writeback errors and clear `ODIRECT` on failure.

## Test Signals
Stress mixed buffered reads, buffered writes, direct IO, truncate, and mmap writeback. Verify lock pairing with lockdep and that page-cache flush failures propagate from direct-mode transition.
