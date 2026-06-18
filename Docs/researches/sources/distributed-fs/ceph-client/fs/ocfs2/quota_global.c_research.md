# sources/distributed-fs/ceph-client/fs/ocfs2/quota_global.c

## Purpose
`quota_global.c` implements OCFS2 operations over the clustered global quota files. It bridges the VFS quota core, the generic qtree quota format, OCFS2 journaling, and OCFS2 cluster locks so user/group quota limits and aggregate usage can be shared safely across mounted nodes.

## Important APIs, types, and functions
The file exports the qtree format adapter `ocfs2_global_ops`, physical quota I/O helpers `ocfs2_validate_quota_block`, `ocfs2_read_quota_phys_block`, `ocfs2_quota_read`, and `ocfs2_quota_write`, global quota locking helpers `ocfs2_lock_global_qf` and `ocfs2_unlock_global_qf`, info operations `ocfs2_global_read_info` and `ocfs2_global_write_info`, the synchronization primitive `__ocfs2_sync_dquot`, deferred drop worker `ocfs2_drop_dquot_refs`, and the VFS `dquot_operations` table `ocfs2_quota_operations`. Central state is `struct ocfs2_mem_dqinfo`, its embedded qtree info, global quota inode pointer, qinfo lock resource, delayed sync work, and cached global quota inode buffer.

## Control flow
Quota enablement calls `ocfs2_global_read_info`, which opens the global system inode, locks it shared, reads the global info block under the quota-info lock, initializes qtree geometry, and schedules periodic sync work. Reads and writes bypass page cache and translate logical quota offsets through `ocfs2_extent_map_get_blocks`; writes require an active journal transaction and update inode size/version metadata. `ocfs2_acquire_dquot` exclusively locks the global quota file, reads or creates the qtree entry, increments the clustered use count, extends the global file if a new qtree path is needed, then creates the node-local dquot entry. `ocfs2_mark_dquot_dirty` writes local deltas normally, but synchronizes immediately to the global file when administrator-set fields need cluster-wide visibility. `ocfs2_release_dquot` decrements global use count and releases the local slot entry, deferring work if called from the downconvert thread.

## State and persistence
Persistent state lives in global user/group quota system files: qtree blocks, global quota info, disk dquot records, use counts, limits, usage, and grace times. Runtime state tracks original local usage in `struct ocfs2_dquot`, dirty `DQ_LASTSET` bits, delayed sync cadence, global inode lock nesting count, and the `dquot_drop_list`. Global changes are journaled and guarded by OCFS2 inode, allocation, and qinfo cluster locks.

## Dependencies and integration points
The file depends on Linux quota/qtree code, OCFS2 system files, extent maps, inode cluster locks, qinfo DLM locks, journaling, metadata ECC, workqueues, and local quota helpers from `quota_local.c`. It plugs into superblock quota callbacks via `quota_read`, `quota_write`, and `dquot_operations`.

## Risks and test signals
High-risk areas are lock ordering between `dqio_sem`, dquot locks, inode cluster locks, `ip_alloc_sem`, and qinfo locks; extending qtree files outside transactions; delayed sync during unmount; downconvert-thread deferral; and preserving administrator-set quota fields while merging usage deltas. Test signals include multi-node quota limit updates, first acquire of a previously nonexistent ID, release of last reference, periodic sync under active I/O, quota disable while sync work is pending, qtree block allocation failure, recovery after node death, and fault injection around journal credit exhaustion.
