# sources/distributed-fs/ceph-client/fs/xfs/xfs_inode.c

## Purpose
`xfs_inode.c` implements core XFS inode operations: inode lock orchestration, directory lookup, create/tmpfile/link/remove/rename, truncate and inactivation, inode freeing and stale cluster handling, inode flush to disk buffers, unlinked-list reload, DAX/layout break helpers, and assorted inode utilities. The full 3066-line file was read.

## Important APIs, Types, and Functions
Locking APIs include `xfs_ilock`, `xfs_ilock_nowait`, `xfs_iunlock`, `xfs_ilock_demote`, `xfs_assert_ilocked`, `xfs_lock_inodes`, and `xfs_lock_two_inodes`. Lookup and namespace operations include `xfs_lookup`, `xfs_icreate`, `xfs_icreate_dqalloc`, `xfs_create`, `xfs_create_tmpfile`, `xfs_link`, `xfs_remove`, and `xfs_rename`.

Cleanup and persistence functions include `xfs_itruncate_extents_flags`, `xfs_inactive`, `xfs_inode_needs_inactive`, `xfs_ifree`, `xfs_iflush_cluster`, `xfs_log_force_inode`, and `xfs_irele`. Unlinked-list and stale-inode helpers include `xfs_iunlink_lookup`, `xfs_iunlink_reload_next`, `xfs_inode_reload_unlinked_bucket`, `xfs_inode_reload_unlinked`, `xfs_ifree_mark_inode_stale`, and `xfs_ifree_cluster`. Layout helpers include `xfs_ilock2_io_mmap`, `xfs_iunlock2_io_mmap`, `xfs_iunlock2_remapping`, `xfs_break_dax_layouts`, and `xfs_break_layouts`.

## Control Flow
The lock helpers impose XFS lock order: VFS `i_rwsem`/IOLOCK first, mapping `invalidate_lock`/MMAPLOCK second, XFS `i_lock`/ILOCK last. Multi-inode locking sorts by inode number and uses trylock/retry when earlier locked inodes are in the AIL to avoid log tail deadlocks.

Creation allocates dquots, parent-pointer context, transaction reservations, the new inode number, and the in-core inode; joins parent and child to the transaction; updates directory and parent metadata; attaches dquots; commits; and returns the new inode locked/initialized for VFS setup. Tmpfile creation allocates an unlinked inode. Link/remove/rename similarly coordinate quota attachment, parent pointers, directory operations, log reservations, AGI locking order, synchronous mount flags, and transaction commit/cancel unwinding.

Inactivation runs when an inode loses its last reference and needs persistent cleanup. It records unresolved health, skips read-only/internal/shutdown cases, cancels COW reservations, frees EOF blocks, truncates unlinked regular/directories/symlinks, removes attributes, and frees the inode from allocation metadata. Inode freeing uninitializes the inode, updates quota, removes it from unlinked lists, and can stale entire inode cluster buffers while marking all cached cluster inodes stale.

Flush paths convert dirty incore inode fields and forks into an inode cluster buffer. `xfs_iflush_cluster` nonblockingly scans all inode log items attached to a buffer, locks clean candidates, calls `xfs_iflush`, and queues the buffer for writeback through AIL push machinery.

## State and Persistence Behavior
This file is a primary persistence bridge. It commits namespace changes, link counts, inode core changes, fork truncation, attribute removal, quota accounting, unlinked-list updates, inode free state, and flushed dinodes. It mutates incore inode flags such as `XFS_ISTALE`, `XFS_IFLUSHING`, `XFS_IREMAPPING`, `XFS_IQUOTAUNCHECKED`, sickness bits, fork state, generation, nlink, dquot attachment, and transaction log item state.

Crash consistency depends on transaction reservations, log item ordering, AGI-before-AGF lock order, inode cluster buffer staling, and logging inode size before truncating blocks to avoid stale data exposure. Unlinked-list reload can reconstruct incore previous pointers after recovery finds unrecovered unlinked inodes.

## Dependencies and Integration Points
The file integrates with VFS inode locks and leases, pagecache invalidation, DAX layout breaking, XFS transactions/defer ops, directory code, parent pointers, symlinks, attributes, quota, filestreams, inode allocation/freeing, bmap/truncate, reflink COW, AGI/AGF buffers, log/AIL, inode item flushing, health marking, realtime and zoned behavior, metadata inodes, and trace/error injection infrastructure.

## Risks and Edge Cases
Lock ordering is the dominant risk: IOLOCK/MMAPLOCK/ILOCK nesting, AGI-before-AGF, inode cluster buffers locked late, and multi-inode AIL interactions must remain consistent. Namespace operations have complex unwind paths with locked inodes, dquot references, parent-pointer contexts, and temporary whiteout inodes. Inactivation must not write on read-only mounts except recovery, must not process internal metadata inodes, and must handle quotacheck and unlinked inodes correctly. Staling inode clusters must find every cached inode in the cluster or stale dirty inodes can survive incorrectly. Flush corruption checks must shut down safely before failed buffers can move the log tail incorrectly.

## Test Signals
Test signals include lockdep runs for create/link/remove/rename/exchange/whiteout/remap paths, xfstests for tmpfile and parent pointers, quota low-space retry and reservationless directory updates, unlink and unmount inactivation, crash recovery of unlinked lists and inode frees, stale inode cluster writeback, forced `xfs_iflush` error tags, DAX layout break retries, project quota inheritance failures, metadata inode lookup rejection from normal directories, and fsync/log force behavior after inode modifications.
