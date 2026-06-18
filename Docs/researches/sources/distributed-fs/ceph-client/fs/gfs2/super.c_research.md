# sources/distributed-fs/ceph-client/fs/gfs2/super.c

## Purpose
`super.c` supplies GFS2 superblock operations and mount-state transitions: journal descriptor management, read-write activation, statfs accounting, freeze/thaw, sync, inode eviction, writeback integration, mount option display, and unmount cleanup.

## Important APIs, Types, And Functions
Key exported helpers are `gfs2_jindex_free`, `gfs2_jdesc_find`, `gfs2_jdesc_check`, `gfs2_make_fs_rw`, `gfs2_make_fs_ro`, `gfs2_statfs_init`, `gfs2_statfs_change`, `update_statfs`, `gfs2_statfs_sync`, `gfs2_freeze_func`, `free_local_statfs_inodes`, and `find_local_statfs_inode`. The VFS-facing `gfs2_super_ops` wires in `.alloc_inode`, `.free_inode`, `.write_inode`, `.dirty_inode`, `.evict_inode`, `.put_super`, `.sync_fs`, `.freeze_super`, `.freeze_fs`, `.thaw_super`, `.statfs`, `.drop_inode`, and `.show_options`.

`enum evict_behavior` describes whether an evicted inode should be deleted locally, skipped, or deferred. The file also serializes dinode fields with `gfs2_dinode_out`.

## Control Flow
Read-write activation invalidates the local journal glock, verifies journal sequence knowledge, initializes quota, and sets `SDF_JOURNAL_LIVE`. Read-only transition flushes delete work, destroys daemon threads, syncs quota/statfs, performs two log flushes to commit metadata and revokes, waits for log empty, and cleans quota.

Statfs has a fast path that combines master and local statfs deltas under `sd_statfs_spin`, plus a slow path that asynchronously locks rgrps and totals verified rgrp counts. Syncing statfs locks the master statfs inode, starts a transaction, folds local deltas into master, and clears the local buffer.

Freeze first freezes the VFS, then obtains journal locks and the freeze glock to verify all journals have clean unmount headers. Thaw reacquires the shared freeze glock and calls VFS thaw. Inode eviction distinguishes linked inodes from unlinked dinodes, verifies bitmap type before reading deleted dinodes, upgrades iopen glocks when this node is final opener, and deallocates xattrs, file blocks, exhash directories, and dinode blocks.

## State And Persistence
Persistent state includes journal index inodes, local/master statfs files, dinodes, quota changes, and journal log contents. Important flags are `SDF_JOURNAL_LIVE`, `SDF_NORECOVERY`, `SDF_FROZEN`, `SDF_FREEZE_INITIATOR`, `SDF_KILL`, and `SDF_EVICTING`. Eviction updates on-disk dinodes, writes back glock metadata address spaces, and records deleted inode formal numbers to avoid stale lookups.

## Dependencies And Integration Points
This file integrates VFS superblock operations, GFS2 glocks, journaling, quota, rgrp, xattr deallocation, directory deallocation, recovery, sysfs cleanup, and debugfs. It relies on freeze glocks for cluster-wide freeze semantics and on journal glocks to avoid freezing over dirty recoverable journals.

## Risks And Test Signals
High-risk paths include unmount while recovery is active, freeze retries during journal recovery, evicting unlinked inodes under memory pressure, journal-live races during withdrawal, and statfs divergence between local and master files. Signals include xfstests freeze/thaw and unlink tests, multi-node recovery tests, dirty inode writeback under journaled-data mode, statfs slow/fast comparisons, and clean unmount log headers after remount read-only.
