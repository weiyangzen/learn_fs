# sources/distributed-fs/ceph-client/fs/btrfs/file.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/file.h` is the public header for Btrfs regular-file operations and file extent mutation helpers implemented in `file.c`. It exposes the VFS file operations table and the cross-subsystem APIs used by inode writeback, reflink, ioctl encoded I/O, tree logging, truncation, hole punching, NOCOW checks, and delalloc discovery. The source was read as a complete 51-line file for this report.

## Important APIs, Types, and Functions

The header declares `extern const struct file_operations btrfs_file_operations`, which binds Btrfs regular inodes to VFS read, write, mmap, fsync, fallocate, ioctl, remap, splice, and llseek handlers.

Extent mutation APIs are `btrfs_drop_extents()`, `btrfs_replace_file_extents()`, and `btrfs_mark_extent_written()`. They operate on `struct btrfs_trans_handle`, `struct btrfs_root`, `struct btrfs_inode`, `struct btrfs_path`, `struct btrfs_drop_extents_args`, and `struct btrfs_replace_extent_info` contracts defined elsewhere.

Write and file lifecycle APIs are `btrfs_sync_file()`, `btrfs_do_write_iter()`, `btrfs_release_file()`, `btrfs_dirty_folio()`, `btrfs_fdatawrite_range()`, `btrfs_write_check()`, and `btrfs_buffered_write()`. NOCOW/delalloc helpers are `btrfs_check_nocow_lock()`, `btrfs_check_nocow_unlock()`, and `btrfs_find_delalloc_in_range()`.

The header forward-declares Linux and Btrfs types including `file`, `extent_state`, `kiocb`, `iov_iter`, `inode`, `folio`, encoded I/O args, drop/replace extent args, roots, paths, inodes, and transaction handles.

## Control Flow

This file has no executable control flow. It describes the callable edges into `file.c`: VFS enters through `btrfs_file_operations`, ioctl encoded write code enters `btrfs_do_write_iter()`, inode and reflink code enter extent dropping/replacement helpers, writeback and page-cache paths use dirty-folio and fdatawrite helpers, and NOCOW callers pair `btrfs_check_nocow_lock()` with `btrfs_check_nocow_unlock()` when the lock check succeeds.

## State and Persistence Behavior

No state is stored in the header itself. The declared functions mutate durable Btrfs metadata such as file extent items, inode items, delayed refs, and tree-log records, and they manipulate runtime state such as folio flags, extent-state bits, ordered extents, qgroup reservations, and file-private llseek caches. The header is therefore a transaction- and locking-sensitive interface even though it contains only declarations.

## Dependencies and Integration Points

The header includes only `<linux/types.h>` and relies on forward declarations to reduce include coupling. It is consumed by Btrfs inode, reflink, ioctl, tree-log, direct-I/O, and other file-related code that needs regular-file operations without including the full `file.c` implementation.

Integration points include VFS file operations, Btrfs transactions, ordered extents, file extent B-tree items, reflink extent replacement, encoded I/O, buffered write delayed allocation, fsync/tree-log, and SEEK_DATA/SEEK_HOLE delalloc detection.

## Risks and Edge Cases

The risk in this header is contract visibility. Several declarations require strict caller discipline: `btrfs_replace_file_extents()` expects locked ranges and returns an open transaction on success; `btrfs_check_nocow_lock()` must be balanced by unlock only on positive return; `btrfs_dirty_folio()` receives cached extent state ownership; and `btrfs_drop_extents()` depends on correctly initialized argument structures. Type forward declarations hide details, so compile-time checking cannot enforce most lifetime and locking rules.

## Test Signals

Compile coverage across Btrfs users is essential. Behavioral signals should come from the implementation users: reflink clone/dedupe tests, inline extent writeback, prealloc-to-written conversion, buffered and encoded writes, fsync/log replay, mmap dirtying, NOCOW NOWAIT paths, fallocate/punch-hole/zero-range, and SEEK_DATA/SEEK_HOLE with delalloc. Static analysis and lockdep are useful for checking that callers honor transaction, inode-lock, mmap-lock, and NOCOW lock pairing contracts.
