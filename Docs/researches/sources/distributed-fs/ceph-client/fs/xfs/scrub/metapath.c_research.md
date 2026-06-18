<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/metapath.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/metapath.c

Purpose: Scrubs and repairs metadata-directory paths for metadir-enabled XFS filesystems, ensuring expected names under the metadata tree point to the correct incore metadata inode.

Important APIs, types, and functions: `struct xchk_metapath` stores scrub context, final component name, directory update structure, owned path string, parent directory inode and lock flags, transaction reservations, parent-pointer args, and scratch attr args. Public functions are `xchk_setup_metapath()`, `xchk_metapath()`, and under repair `xrep_metapath()`. Setup helpers select paths for realtime group metadata, quota directory/files, and probe requests.

Control flow: Setup rejects non-metadir filesystems and invalid generation fields, maps `sm_ino` selector values to specific metadata inodes and parent directories, installs the live child inode, and records the expected final path component. Scrub allocates an empty transaction, locks parent and child without deadlocking, looks up the name in the parent directory, and marks the child corrupt if the name is missing or points to a different inode. Repair ensures parent pointers can be stored if enabled, computes link/unlink reservations, repeatedly tries to create the correct link, removes any wrong dirent target, and handles races where the dirent changes between attempts.

State and persistence: Scrub is read-only aside from transient locks. Repair persists directory entry additions/removals and optional parent pointer updates through transactions, and can remove a bogus dirent even if the alleged child inode is missing.

Dependencies and integration points: Depends on metadir, quota, realtime group metadata inodes, directory lookup/add/remove helpers, parent pointer support, transaction reservations, inode locking, and repair transaction commit/cancel helpers. It is a final repair stage after metadata inode contents have been repaired.

Risks and test signals: Risks include deadlocks between parent/child ILOCKs, removing a valid dirent during concurrent repair, parent pointer mismatch, missing metadata inodes, and repair ordering before child metadata is stable. Test probe selector, every quota and realtime selector, missing parent directory, missing/wrong/correct dirent, bogus alleged child inode, parent-pointer present/absent cases, concurrent dirent replacement returning EAGAIN/EEXIST, and no repair on non-metadir filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/metapath.c -->
