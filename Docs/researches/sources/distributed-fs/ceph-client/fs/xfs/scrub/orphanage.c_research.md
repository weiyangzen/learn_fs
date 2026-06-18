# sources/distributed-fs/ceph-client/fs/xfs/scrub/orphanage.c

## Purpose
`orphanage.c` implements online repair support for `/lost+found`. When directory tree damage disconnects files, repair can create or reuse the orphanage, make it root-owned, and adopt orphaned files by adding directory entries, updating dotdot for directories, adding parent pointers, and invalidating stale dentries.

## Important APIs, Types, And Functions
`xrep_orphanage_create` finds or creates `/lost+found`, validates it is a directory, grabs an inode reference, and calls `xrep_chown_orphanage`. Lock helpers are `xrep_orphanage_ilock`, `xrep_orphanage_ilock_nowait`, `xrep_orphanage_iunlock`, `xrep_orphanage_iolock_two`, and `xrep_orphanage_rele`.

Adoption functions are `xrep_adoption_trans_alloc`, `xrep_adoption_compute_name`, `xrep_adoption_move`, and `xrep_adoption_trans_roll`. Internal helpers check and invalidate dcache state and compute attr-fork space for parent-pointer filesystems.

## Control Flow
Creation uses VFS dentries from the root inode, `start_creating_noperm`, and `vfs_mkdir` with mode `0750` if missing. It rejects non-directories and readonly/shutdown cases. Ownership repair allocates root dquots, creates an inode-change transaction, clears suid/sgid/sticky and realtime inheritance bits, updates uid/gid/project, logs the inode, and commits.

Adoption starts with both target and orphanage IOLOCKs. It computes worst-case block reservations for adding the orphanage entry, changing child dotdot, and adding an attr fork if parent pointers require one. It joins both inodes, reserves quota with repair override, chooses a unique numeric name, verifies no positive dcache entry conflicts, creates the name, updates orphanage and child link counts as requested, replaces dotdot for directories, adds a parent pointer when enabled, fires a directory update hook, invalidates dentries, and rolls the transaction clean.

## State And Persistence Behavior
Persistent effects include creating `/lost+found`, changing its ownership and mode bits, adding orphanage directory entries, updating directory dotdot entries, parent-pointer xattrs, link counts, timestamps, quota reservations, and logged inode state. Dcache invalidation is volatile but necessary so VFS lookup state matches repaired metadata.

## Dependencies And Integration Points
The file integrates with VFS dentry helpers, XFS quota, transactions, directory operations, parent-pointer APIs, scrub repair context, tracepoints, and callers in nlink and parent repair. It relies on `sc->orphanage` and `sc->orphanage_ilock_flags` as shared repair context.

## Risks And Edge Cases
Readonly mounts continue without orphanage. Missing root dentry, non-directory root alias, non-directory `/lost+found`, name collisions beyond 10,000 variants, dcache contradictions, attr-fork allocation failure, and quota reservation failure all abort adoption. Lock ordering is critical because scrub may already hold transactions and cannot block on IOLOCK in ordinary order.

## Test Signals
Tests should cover creating `/lost+found`, fixing ownership/project/realtime flags, adopting files and directories, parent-pointer filesystems, dcache aliases, name collisions, readonly mounts, no-space cases, and concurrent lookup/rename during adoption.
