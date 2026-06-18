# sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.c

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.c` implements XFS symlink read, create, and inactive cleanup behavior. It handles inline symlink data, remote symlink blocks, quota and parent pointer integration, directory updates, transaction reservation/commit/cancel paths, and corruption detection for invalid symlink lengths or fork data. The source was read as a complete 362-line file for this report.

## Important APIs, Types, and Functions

The externally declared functions are `xfs_readlink`, `xfs_symlink`, and `xfs_inactive_symlink`. The important internal helper is `xfs_inactive_symlink_rmt`, which frees remote symlink blocks and converts the unlinked inode away from symlink mode before truncation. The implementation uses `struct xfs_icreate_args`, `struct xfs_dir_update`, `struct xfs_trans`, `struct xfs_dquot`, parent pointer args, `XFS_SYMLINK_MAXLEN`, `XFS_DINODE_FMT_LOCAL`, and tracepoints `trace_xfs_readlink`, `trace_xfs_symlink`, and `trace_xfs_inactive_symlink`.

## Control Flow

`xfs_readlink` rejects shutdown mounts and zapped data forks, locks the inode shared, validates a nonzero symlink length within `XFS_SYMLINK_MAXLEN`, copies inline data when the data fork is local, or delegates to `xfs_symlink_remote_read` for remote symlink contents. Corrupt cases mark the inode sick and return `-EFSCORRUPTED`.

`xfs_symlink` validates shutdown state and target length, allocates quota records, decides whether the target fits inline or needs remote blocks, starts parent pointer bookkeeping, allocates an inode-create transaction, locks the parent directory, rejects directories with `XFS_DIFLAG_NOSYMLINKS`, allocates and creates the symlink inode, joins the parent to the transaction, attaches dquots, writes the target with `xfs_symlink_write_target`, creates the directory child entry, marks the transaction synchronous for sync/dirsync mounts, commits, releases dquots, unlocks inodes, and returns the created inode. Error paths cancel transactions, finish parent args, release dquots, finish and release partially created inodes, and avoid double-unlocking the parent.

`xfs_inactive_symlink` validates length and returns immediately for inline symlinks because inode freeing removes local fork data. Remote symlinks call `xfs_inactive_symlink_rmt`, which allocates an itruncate transaction, locks and joins the inode, sets disk size to zero, changes VFS mode to regular file to avoid writing a zero-length symlink, logs core changes, truncates remote symlink blocks, commits, frees in-memory extent descriptors, and unlocks.

## State and Persistence Behavior

Symlink target bytes persist either in the inode data fork or in remote filesystem blocks. Creation persists inode metadata, quota attachments, parent pointer metadata when enabled, target data, and the directory entry atomically through XFS transactions. Inactive cleanup persists remote block freeing and inode core changes before memory-only extent descriptor cleanup. Corruption state is recorded in inode health by `xfs_inode_mark_sick`.

## Dependencies and Integration Points

The file depends on XFS inode, bmap, quota, directory, transaction, parent pointer, deferred-op, health, remote symlink, and trace infrastructure. VFS inode operations call into it through `xfs_iops.c`; inactive inode processing calls `xfs_inactive_symlink` from `xfs_inode.c`. It integrates with quota accounting, parent pointers, directory updates, synchronous mount semantics, and log transaction reservation classes.

## Risks and Edge Cases

Target length validation is strict: zero-length symlinks are treated as corruption during read/inactive and too-long targets return `-ENAMETOOLONG` during create. Inline symlink reads require non-null `if_data`; otherwise the inode is marked sick. Remote symlink cleanup assumes extents have been read and that symlink blocks fit the expected one or two extents. Error-path lock ownership changes after `xfs_trans_ijoin` are subtle, and parent pointer/quota resources must be released on every exit.

## Test Signals

Test signals include creating and reading inline and remote symlinks, rejecting too-long targets, enforcing `nosymlinks`, symlink creation under user/group/project quotas, parent-pointer enabled filesystems, sync/dirsync mounts, crash-recovery around symlink creation, corruption tests for bad lengths and missing inline data, and inactive cleanup tests that verify remote blocks are freed.
