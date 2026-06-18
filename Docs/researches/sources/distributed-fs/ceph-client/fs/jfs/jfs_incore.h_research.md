# sources/distributed-fs/ceph-client/fs/jfs/jfs_incore.h

Purpose: defines the in-memory JFS inode and superblock private structures and their lock/flag helpers.

Important APIs and types: `struct jfs_inode_info` embeds VFS inode state plus JFS-specific fields: fileset/mode2, saved ownership, inode extent PXD, ACL/EA descriptors, creation time, directory index counter, imap pointer, commit flags, active AG, anonymous transaction list state, locks, and a union for file xtree root, directory table/dtree root, or symlink inline data. `struct jfs_sb_info` stores mount flags, metadata inodes, log, geometry, aggregate ID, log/fsck/ait PXDs, UUIDs, commit state, inode generation/stamp, block map, NLS table, and mount overrides. Helpers include `JFS_IP`, `JFS_SBI`, `jfs_dirtable_inline`, `isReadOnly`, lock macros, cflag bit helpers, and lock subclass enums.

Control flow: inline helpers provide object lookup and policy checks used throughout JFS. `jfs_dirtable_inline` controls whether directory indexes are stored in `i_dirtable` or external xtree pages; `isReadOnly` treats absence of a journal/log as read-only for metadata mutation paths.

State and persistence behavior: this header separates persistent mirrors (`i_xtroot`, `i_dtroot`, `i_dirtable`, `ixpxd`, ACL/EA descriptors) from runtime-only state (`commit_mutex`, `rdwrlock`, `xattr_sem`, cflags, active AG, anonymous tlock list fields). `jfs_sb_info` carries mount-session state and fields copied from or written back to disk metadata.

Dependencies and integration: depends on Linux mutex/rwsem/bitops/uuid APIs and JFS type, xtree, and dtree layouts. It is included by nearly every JFS implementation file and is the bridge between VFS `struct inode`/`super_block` and JFS internals.

Risks and edge cases: the union overlays very different persistent formats; code must select fields according to file type. Lock subclass usage matters for lockdep and for avoiding deadlocks between normal inodes, imap, and dmap. Commit flags such as `COMMIT_Dirtable`, `COMMIT_Stale`, and `COMMIT_Synclist` drive later writeback behavior and can cause persistence bugs if missed.

Test signals: inode allocation/read/write of regular files, directories, symlinks, inline EA updates, directory index migration, lockdep coverage for nested inode/map locks, lazy commit behavior, and read-only mount mutation rejection.
