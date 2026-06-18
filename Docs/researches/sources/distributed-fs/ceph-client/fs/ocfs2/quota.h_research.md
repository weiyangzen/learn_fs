# sources/distributed-fs/ceph-client/fs/ocfs2/quota.h

Purpose: declares OCFS2 quota in-memory structures and the internal quota API for global/local quota files, quota recovery, dquot synchronization, and quota block validation.

Important APIs and types: `struct ocfs2_dquot` embeds the generic VFS `struct dquot` and tracks local quota-file offset, physical block, quota chunk, global reference count, last globally synced space/inode usage, and deferred-drop list membership. `struct ocfs2_mem_dqinfo` describes one quota type, including flags, local chunk/block counts, global quota inode and lock, cached quota inode buffers, local info buffers, qtree info, delayed sync work, and recovery info. `struct ocfs2_quota_recovery` and `struct ocfs2_recovery_chunk` track chunks and bitmaps that need recovery. Exported APIs cover quota recovery begin/finish/free, quota read/write, global info read/write, dquot sync/release, global quota locking, quota block validation and physical reads, local dquot create/release/write, deferred dquot reference dropping, and VFS quota operation/format registrations.

Control flow: quota users initialize and modify generic dquots, then OCFS2 syncs local quota deltas to global quota files under `dqi_gqlock`. Recovery code records quota chunks needing repair for a slot and completes them when quotas are enabled or recovery finishes. Delayed work periodically syncs dquots according to `dqi_syncms`, and deferred drop work releases dquot references outside sensitive paths.

State and persistence: runtime state lives in `ocfs2_dquot`, `ocfs2_mem_dqinfo`, cache objects, locks, delayed work, and recovery lists. Persistent state lives in global and local quota files whose on-disk structures are defined in `ocfs2_fs.h`, including local chunks, local dquot delta records, global qtree records, and quota trailers with block checks.

Dependencies and integration: depends on Linux quota and qtree APIs, slab caches, lists, lock resources, OCFS2 superblock state, and the VFS dquot layer. Namespace code in `namei.c` calls quota initialization and inode/space allocation or rollback during create, symlink, and link-related updates.

Risks: quota synchronization is cluster-sensitive because local deltas and global usage must remain consistent across node crashes. Lock ordering around global quota files can deadlock if mixed with inode or journal locks incorrectly. Recovery bitmaps must match local quota chunks exactly or leak/duplicate usage. Deferred dquot drops must not race with quota shutdown.

Test signals: user and group quota enable/disable tests, multi-node quota allocation and release stress, crash recovery with dirty local quota files, delayed sync behavior, dquot cache lifetime tests, quota block checksum validation, ENOSPC/EDQUOT rollback in create/symlink paths, and VFS quota operation conformance tests.
