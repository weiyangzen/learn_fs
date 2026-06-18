<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_file.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_file.c

## Purpose
`vfs_file.c` implements 9p regular file operations: open, read/write dispatch, splice, mmap, fsync, and local/remote file locking.

## Important APIs, types, and functions
Important functions include `v9fs_file_open`, `v9fs_file_read_iter`, `v9fs_file_write_iter`, `v9fs_file_splice_read`, `v9fs_file_fsync`, `v9fs_file_fsync_dotl`, `v9fs_file_lock`, `v9fs_file_lock_dotl`, `v9fs_file_flock_dotl`, and `v9fs_file_mmap_prepare`. Operation tables are `v9fs_file_operations` and `v9fs_file_operations_dotl`.

## Control flow
Open converts Linux flags to legacy or dotl open modes, clones/opens a fid, optionally upgrades write-only writeback opens to read/write, uses fscache cookies, adjusts fid cache flags, and stores the fid on the open inode list. I/O chooses netfs cached or unbuffered paths based on fid mode. Dotl locks synchronize local VFS locks with server lock calls and retry blocked locks.

## State and persistence
State includes open fid references, fid mode cache flags, local lock state, netfs page cache/writeback state, and optional fscache cookie use counts. File contents live on the 9p server.

## Dependencies and integration points
It depends on p9 open/read/write/fsync/lock RPCs, netfs file helpers, VFS locking, mmap VM operations, and shared directory release.

## Risks and test signals
Risks include incorrect cache/direct transitions, write-only writeback fallback, lock rollback mismatches, mmap dirty flushing, and fsync semantics differences between legacy wstat and dotl fsync. Test signals include O_APPEND, O_DIRECT, mmap shared writes, flock/fcntl locks, interrupted blocking locks, fsync, splice, and cache modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_file.c -->
