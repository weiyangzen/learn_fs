# sources/distributed-fs/ceph-client/fs/nfs/io.c

## Purpose
`io.c` implements the inode-level synchronization that prevents NFS buffered I/O and direct I/O from running against the same file in incompatible modes. It is a small but central data-path helper used by file read/write and direct I/O code to serialize mode transitions using `inode->i_rwsem` and the `NFS_INO_ODIRECT` inode flag.

## Important APIs, Types, And Functions
The exported API is `nfs_start_io_read()`, `nfs_end_io_read()`, `nfs_start_io_write()`, `nfs_end_io_write()`, `nfs_start_io_direct()`, and `nfs_end_io_direct()`. `nfs_start_io_read()` obtains a killable read lock and ensures direct I/O is blocked; if direct I/O is active, it upgrades through a write lock, clears `NFS_INO_ODIRECT`, waits for in-flight direct I/O via `inode_dio_wait()`, then downgrades. `nfs_start_io_write()` takes the write lock and blocks direct I/O. `nfs_start_io_direct()` does the inverse: it ensures `NFS_INO_ODIRECT` is set, syncing the mapping to drain buffered data before downgrading to a shared lock. `nfs_block_buffered()` is the local helper that sets the direct-I/O flag and calls `nfs_sync_mapping()`.

## Control Flow And Integration Points
Buffered reads can run concurrently under a shared `i_rwsem` lock once the inode is not in direct-I/O mode. Buffered writes take the exclusive lock and therefore serialize with buffered reads and direct I/O transitions. Direct I/O similarly uses a shared lock while active, but only after an exclusive transition that sets `NFS_INO_ODIRECT` and flushes cached data. The public functions are declared in `internal.h` and called by the NFS file/direct I/O paths.

## State And Persistence Behavior
The persistent state is the `NFS_INO_ODIRECT` bit in `struct nfs_inode::flags`. It represents the current I/O mode barrier, not a permanent mount setting. The start functions hold `i_rwsem` until the paired end function runs. `nfs_block_buffered()` also pushes dirty page-cache state to the server before direct I/O proceeds.

## Dependencies
The file depends on VFS inode locking, NFS inode state, `nfs_sync_mapping()`, killable rwsems, direct-I/O wait helpers, and the inline `nfs_file_block_o_direct()` from `internal.h`.

## Risks And Edge Cases
The main risk is unmatched start/end calls, which would leak `i_rwsem` locks. Interruptible lock acquisition returns errors and callers must stop the I/O path. Mode transitions are subtle: direct I/O must not start without flushing buffered data, and buffered I/O must not start without waiting for direct I/O completion. Write paths also interact with truncate serialization via the exclusive lock.

## Test Signals
Exercise mixed buffered and `O_DIRECT` reads/writes on the same file, concurrent direct writers and buffered readers, interrupted tasks waiting for `i_rwsem`, writeback behavior during direct transitions, and lockdep under stress. xfstests direct I/O and mmap/writeback cases are especially relevant.
