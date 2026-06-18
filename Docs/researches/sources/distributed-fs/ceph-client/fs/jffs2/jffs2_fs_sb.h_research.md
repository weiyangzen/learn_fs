# sources/distributed-fs/ceph-client/fs/jffs2/jffs2_fs_sb.h

## Purpose
`jffs2_fs_sb.h` defines mount options and `struct jffs2_sb_info`, the filesystem-wide JFFS2 control structure. It tracks MTD geometry, space accounting, eraseblock lists, GC state, inode caches, write-buffer state, xattr state, summaries, and OS-private superblock linkage.

## Important APIs, Types, And Functions
Important definitions are `JFFS2_SB_FLAG_RO`, `JFFS2_SB_FLAG_SCANNING`, `JFFS2_SB_FLAG_BUILDING`, `struct jffs2_mount_opts`, and `struct jffs2_sb_info`. The superblock fields include `mtd`, size counters, reservation thresholds, `blocks`, `nextblock`, `gcblock`, all eraseblock lists, `erase_completion_lock`, `alloc_sem`, inode-cache hash state, `erase_free_sem`, write-buffer fields under `CONFIG_JFFS2_FS_WRITEBUFFER`, `summary`, `mount_opts`, and xattr indexes.

## Control Flow
`jffs2_do_fill_super()` initializes geometry, lists, hash size, flash setup, mount scan, and root inode. Allocation, write, erase, and GC paths update counters and move `jffs2_eraseblock` objects through the lists declared here. Mount options override compression behavior and reserved-pool sizing.

## State And Persistence Behavior
The structure is volatile but mirrors persistent flash state: used/dirty/free/unchecked/bad sizes are derived from scan and maintained as nodes are written, obsoleted, erased, and marked bad. Write-buffer fields hold pending bytes not yet durable on NAND-like media.

## Dependencies And Integration Points
It depends on Linux locks, workqueues, timers, wait queues, lists, and rwsems. Almost every JFFS2 subsystem receives a `struct jffs2_sb_info *c`, making this the primary integration object.

## Risks And Test Signals
Space accounting and list membership invariants are critical; drift can cause ENOSPC loops, unsafe erases, or data loss. Tests should validate mount scan accounting, reservation thresholds, GC transitions across every block list, remount and write-buffer flushing, xattr memory accounting, and compression mount-option overrides.
