# sources/distributed-fs/ceph-client/fs/ocfs2/namei.h

Purpose: declares the OCFS2 namespace and orphan-management interface used outside `namei.c`.

Important APIs and types: the header exports `ocfs2_dir_iops` for directory inode operations, `ocfs2_get_parent()` for NFS/export dentry parent lookup, and orphan helpers for deleting, creating, adding, removing, and moving orphaned inodes. It also defines `OCFS2_DIO_ORPHAN_PREFIX` and its length, which establish the persistent `dio-` orphan-name convention for direct-I/O orphan entries.

Control flow: callers use the exported orphan helpers when an inode must survive temporarily without a normal directory name, especially append direct I/O and delayed creation paths. The API contract passes locked inodes, journal handles, dinode buffers, and flags indicating direct-I/O orphan naming.

State and persistence: this header has no storage, but its prototypes expose persistent orphan state changes in `OCFS2_ORPHANED_FL`, `OCFS2_DIO_ORPHANED_FL`, orphan slot fields, and per-slot orphan directory entries.

Dependencies and integration: consumers depend on `struct ocfs2_super`, `handle_t`, `struct inode`, `struct dentry`, and `struct buffer_head` from the OCFS2 and kernel journaling layers. The interface ties namespace code to file-write, truncate, recovery, and export paths.

Risks: prototype drift would break lock/journal ownership assumptions in callers. The DIO orphan prefix is part of an on-disk naming convention; changing it would break cleanup of existing direct-I/O orphan entries.

Test signals: build coverage across OCFS2 files, append-DIO orphan recovery, NFS export parent lookup, orphan create/move/delete paths, and crash-recovery tests that inspect orphan directory names.
