# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_parent.c

Purpose: Implements parent pointer xattr validation, hashing, transactional updates for create/remove/rename, extraction from attrs, lookup, and repair set/unset helpers.

Important APIs: `xfs_parent_namecheck`, `xfs_parent_valuecheck`, `xfs_parent_hashval`, `xfs_parent_hashattr`, `xfs_parent_addname`, `xfs_parent_removename`, `xfs_parent_replacename`, `xfs_parent_from_attr`, `xfs_parent_lookup`, `xfs_parent_set`, and `xfs_parent_unset`. It also defines `xfs_parent_args_cache`.

Control flow: name validation rejects incomplete attrs and delegates filename component validation. Value validation requires the parent feature, exact `struct xfs_parent_rec` size, local value storage, and valid parent directory inode. Hashing combines the directory name hash with parent inode bits to distinguish hardlink parents. Update helpers ensure the child attr fork exists and extents are read, initialize `xfs_da_args` with `XFS_ATTR_PARENT` and logged operation flags, fill parent records from directory inode generation, and call attr set/remove/replace. Repair helpers sanity-check inputs and invoke immediate attr updates without an existing transaction.

State and persistence: parent pointers are stored as local extended attributes in the child attr fork. The value records parent inode and generation; names are directory entry names. Transactional helpers keep parent pointers consistent with directory mutations.

Dependencies and integration: integrates with attr, dir hash/name validation, deferred attr items, transaction space, inode health marking, parent-pointer feature checks, and repair code.

Risks and test signals: missing attr forks on parent-enabled filesystems are corruption; ENOSPC during parent pointer creation risks namespace inconsistency; hardlink hash collisions and rename replacement correctness matter. Tests should cover create/unlink/rename/hardlink with parent pointers, attr scrub/repair, invalid parent attrs, noattr-fork corruption, and logged attr recovery.
