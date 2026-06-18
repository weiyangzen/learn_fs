<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_inactive.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_inactive.c

Purpose: Removes an inode's entire attribute fork during inode inactivation, including invalidating remote attribute value buffers and truncating attr fork blocks safely.

Important APIs and functions: Public `xfs_attr_inactive` orchestrates transaction allocation, inode locking, attr tree invalidation, truncation, and fork removal. Helpers `xfs_attr3_rmt_stale`, `xfs_attr3_leaf_inactive`, `xfs_attr3_node_inactive`, and `xfs_attr3_root_inactive` walk leaf/node structures and stale remote value buffers.

Control flow: The public function first checks for an attr fork under shared lock, allocates an attr invalidation transaction, upgrades to exclusive inode lock, joins the inode, and if attr blocks exist, invalidates the attr tree while leaving the root. It truncates all but the root, invalidates the root buffer, truncates to zero, removes the attr fork, and commits. On cancellation or even when no persistent removal occurs, it zaps the in-core attr fork before dropping the lock.

State and persistence: Persists deletion of attr fork extents and inode fork metadata through transactions. Remote attr value buffers are never logged, so they are marked stale before block unmapping. The root block is reinitialized before truncation so a crash during removal sees an empty leaf instead of entries pointing at freed remote blocks.

Dependencies and integration: Uses attr leaf/node parsers, bmap read/truncate, buffer invalidation, transaction rolling, quota assumptions, attr geometry, and health marking for corrupt dir/attr forks.

Risks: Recursive node traversal must respect `XFS_DA_NODE_MAXDEPTH`; corrupt magic or empty/invalid structures mark the attr fork sick. Transaction rolling and buffer release ordering avoid holding buffers across log operations. A failure still destroys in-core attr fork state, so callers must tolerate loss of cached fork after errors.

Test signals: Inactivation of shortform, leaf, node, and remote-value attrs; crash-recovery during attr fork removal; corrupt attr tree depth/magic; remote value stale buffer invalidation; and failure paths confirming in-core fork zapping and no buffer lock leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_inactive.c -->
