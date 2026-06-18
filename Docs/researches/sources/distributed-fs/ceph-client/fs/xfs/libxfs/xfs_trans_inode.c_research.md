# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_inode.c

Purpose: Provides transaction helpers for joining, timestamping, logging, and rolling XFS inodes.

Important APIs, types, and functions: Exports `xfs_trans_ijoin`, `xfs_trans_ichgtime`, `xfs_trans_log_inode`, and `xfs_trans_roll_inode`.

Control flow: `xfs_trans_ijoin` requires an exclusive inode lock, initializes the inode log item if needed, records commit-time unlock flags, clears per-transaction dirty flags, and adds the item to the transaction. `xfs_trans_ichgtime` updates ctime and optionally mtime, atime, and creation time under the inode lock. `xfs_trans_log_inode` marks the transaction dirty, sets the log item dirty bit, bumps i_version on the first log in the transaction when configured, and ORs requested inode log flags. Rolling logs core changes, rolls the transaction, and rejoins the inode.

State and persistence: State is transient until commit: inode log item flags, dirty masks, lock-release flags, VFS timestamps, and i_version. Persistence occurs through transaction commit and inode log item precommit/flush paths.

Dependencies and integration points: Depends on inode log items, VFS timestamp/i_version helpers, transaction item lists, inode locking assertions, and stale inode guards.

Risks and test signals: Risks include joining unlocked/stale/already-associated inodes, missing i_version updates, dirty flag loss across rolls, and timestamp changes without core logging by callers. Test metadata operations that roll transactions, i_version-enabled mounts, concurrent inode modification assertions, fsync/recovery of timestamps, and stale inode paths.
