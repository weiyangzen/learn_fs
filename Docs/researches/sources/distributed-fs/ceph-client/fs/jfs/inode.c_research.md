# sources/distributed-fs/ceph-client/fs/jfs/inode.c

## Purpose
Connects JFS disk inodes/extents to Linux inode and address-space operations: load, dirty/commit, evict, map/allocate blocks, buffered/direct I/O callbacks, and truncate.

## Important APIs, types, and functions
`jfs_iget()`, `jfs_commit_inode()`, `jfs_write_inode()`, `jfs_evict_inode()`, `jfs_dirty_inode()`, `jfs_get_block()`, `jfs_aops`, `jfs_direct_IO()`, `jfs_truncate_nolock()`, and `jfs_truncate()`.

## Control flow
Lookup reads a disk inode and installs file, dir, symlink, or special inode operations. Dirty writeback flushes the journal for clean-listed inodes or commits true dirty inodes under `commit_mutex`. Block mapping records not-recorded extents for writes, maps existing extents for reads/writes, or allocates through extent helpers when creating. Failed extending writes trim page cache and truncate extra blocks. Truncation loops transactionally because `xtTruncate()` may be partial.

## State and persistence behavior
State includes Linux inode fields, JFS commit flags, xtree extents, page cache buffers, quotas, and journal state. Persistence occurs through transaction commits, extent allocation/recording, inode free, and journal flushes.

## Dependencies and integration points
Depends on VFS inode/page-cache/writeback/direct-I/O APIs, JFS disk inode manager, extent tree, imap, transaction manager, dmap allocator, quotas, and operation tables.

## Risks and test signals
Test sparse/preallocated files, not-recorded extent reads/writes, direct I/O failure cleanup, fsync/writeback durability, unlink eviction, truncate partial pages, fast symlink bounds, and read-only remount races.
