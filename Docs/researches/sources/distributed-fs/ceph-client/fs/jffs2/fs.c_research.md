# sources/distributed-fs/ceph-client/fs/jffs2/fs.c

## Purpose
`fs.c` implements core superblock/inode lifecycle operations for JFFS2: setattr, statfs, inode eviction and iget, dirty inode writeback, remount handling, new inode setup, superblock fill, GC inode fetch/release, and flash-type setup/cleanup.

## Important APIs, Types, And Functions
Key functions are `jffs2_do_setattr()`, `jffs2_setattr()`, `jffs2_statfs()`, `jffs2_evict_inode()`, `jffs2_iget()`, `jffs2_dirty_inode()`, `jffs2_do_remount_fs()`, `jffs2_new_inode()`, `jffs2_do_fill_super()`, `jffs2_gc_fetch_inode()`, `jffs2_gc_release_inode()`, `jffs2_flash_setup()`, and `jffs2_flash_cleanup()`.

## Control Flow
Setattr writes a fresh metadata node, preserving symlink targets or device numbers when needed, handles truncate/extend as metadata or hole nodes, updates VFS inode fields, and obsoletes old metadata. `jffs2_iget()` initializes in-core inode info by reading raw inode state, then installs operation tables by file type. Superblock fill rejects unsupported MTD types, aligns flash size, initializes flash-specific write-buffer/OOB handling, allocates inode-cache hash tables, mounts/scans the filesystem, obtains root inode, initializes superblock fields, and starts GC when writable. Remount stops/flushes/restarts GC based on read-only state.

## State And Persistence Behavior
Persistent state includes metadata raw inode nodes for attribute changes and new inode allocation. In-core state includes VFS inode fields, inode-cache hash table, eraseblock array, root dentry, mount options, flash geometry, GC thread state, and write-buffer setup.

## Dependencies And Integration Points
This file integrates VFS, fs_context, MTD geometry, ACL/security helpers, build/scan (`jffs2_do_mount_fs()`), readinode, write, GC background control, xattr/summary subsystems, and flash-specific setup for NAND, DataFlash, NOR write-buffer, and UBI volumes.

## Risks And Test Signals
Risk lies in error unwinding during mount, setattr preserving special-file payloads, truncate ordering without holding `f->sem` during `truncate_setsize()`, and GC fetching unlinked inodes without resurrecting deleted ones. Tests should cover mount failures at each allocation/setup step, read-only remounts, dirty inode metadata sync, symlink/device chmod/chown/truncate, root inode failures, NAND/DataFlash/UBI setups, and GC against linked and unlinked inodes.
