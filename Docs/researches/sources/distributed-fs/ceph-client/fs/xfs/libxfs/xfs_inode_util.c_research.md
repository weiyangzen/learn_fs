# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_util.c

Purpose: Provides inode utility operations: user-visible flag translation, inheritance during inode creation, inode initialization, link-count changes, and maintenance of the per-AG unlinked inode lists.

Important APIs: `xfs_flags2diflags`, `xfs_flags2diflags2`, `xfs_ip2xflags`, `xfs_get_initial_prid`, `xfs_inode_init`, `xfs_iunlink`, `xfs_iunlink_remove`, `xfs_droplink`, `xfs_bumplink`, and `xfs_inode_uninit`. Private helpers manage flag inheritance and unlinked-list bucket/backref updates.

Control flow: flag conversion maps FS_XFLAG bits to XFS dinode flags with mode-specific filtering and preserves internal bits such as PREALLOC, REFLINK, BIGTIME, and NREXT64. `xfs_inode_init` sets link counts, ownership, project inheritance, timestamps, fork format, inherited flags, optional attr fork creation for xattrs/parent pointers, and logs the inode. Unlinked insertion reads the AGI, validates the target bucket, updates the next inode backref, logs this inode's `di_next_unlinked`, and points the bucket at the new inode. Removal clears this inode's pointer, updates the next inode's backref, then either patches the previous inode or bucket head.

State and persistence: mutates dinode flags, timestamps, project ids, fork formats, link counts, attr fork presence, superblock attr feature bit, AGI unlinked buckets, and inode `di_next_unlinked`. In-core `i_prev_unlinked` provides a back pointer for efficient removal but on-disk remains singly linked.

Dependencies and integration: depends on transaction logging, AGI buffer access, inode allocation/free, bmap and fork helpers, health marking, quota/project inheritance, parent pointer feature checks, and VFS inode helpers.

Risks and test signals: unlinked-list corruption is high impact because it affects crash recovery and inode freeing. Risk areas include AGI lock ordering, stale inode-cache lookups, ENOLINK reloads, link count pinning, and inherited hint validation. Tests include O_TMPFILE, unlink under crash/recovery, high-AG-count workloads, project inheritance, parent-pointer inode creation, and corrupt AGI bucket fuzzing.
