# sources/distributed-fs/ceph-client/fs/sync.c

## Purpose
This file implements high-level VFS synchronization interfaces: global `sync`, per-superblock `syncfs`, per-file `fsync`/`fdatasync`, and range-based `sync_file_range`.

## Important APIs, Types, and Functions
Exports are `sync_filesystem()`, `vfs_fsync_range()`, `vfs_fsync()`, and `sync_file_range()`. System call entry points include `sync`, `syncfs`, `fsync`, `fdatasync`, `sync_file_range`, compat `sync_file_range`, and architecture-ordered `sync_file_range2`. Helpers include `ksys_sync()`, `emergency_sync()`, `sync_inodes_one_sb()`, and `sync_fs_one_sb()`.

## Control Flow and State
`sync_filesystem()` requires the superblock unmount semaphore to be held. It skips read-only filesystems, starts inode writeback, calls `->sync_fs(wait=0)`, submits block-device writeback, waits on inode writeback, calls `->sync_fs(wait=1)`, then waits on the block device. `ksys_sync()` parallelizes global writeback by waking flusher threads first, then iterates superblocks for inode and filesystem metadata sync and finally syncs all block devices in nowait and wait modes. `syncfs(fd)` locks the referenced superblock, calls `sync_filesystem()`, and returns either sync failure or the advanced writeback error sequence for that file.

Per-file flow checks `file->f_op->fsync`, syncs lazytime metadata unless datasync, then delegates to the filesystem. `sync_file_range()` validates flags and range arithmetic, tolerates out-of-addressable-range starts on 32-bit page-cache systems, limits supported inode types, and performs optional wait-before, write/flush, and wait-after phases.

## Persistence, Dependencies, and Integration
This code depends on writeback, block-device sync, errseq reporting, fd lookup helpers, address-space writeback, and filesystem `file_operations`/`super_operations`. It does not persist metadata itself; it orders and delegates persistence to filesystem and block layers.

## Risks and Test Signals
Risk areas include returning stale or lost writeback errors, arithmetic overflow in ranges, unsupported file types, lock ordering with `s_umount`, and assumptions that `sync_file_range` is data-only and does not flush volatile disk caches. Test signals include fstests for fsync/syncfs error reporting, writeback error injection, 32-bit compat syscall tests, block-device failure tests, and tracing that confirms `->sync_fs` wait phases run in the intended order.
