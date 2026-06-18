# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAttrOp.java

## Purpose
`FSDirAttrOp` centralizes Namenode namespace attribute mutations for permissions, owners, timestamps, replication, quotas, storage policies, and preferred block size reads. It is a static helper around `FSDirectory`, `FSPermissionChecker`, and `BlockManager`, separating checked client-facing operations from `unprotected*` edit-log replay or already-locked mutation routines.

## Important APIs, Types, And Functions
- Public/static operation entry points include `setPermission`, `setOwner`, `setTimes`, `setReplication`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicies`, `getStoragePolicy`, `getPreferredBlockSize`, and `setQuota`.
- Replay/internal helpers include `unprotectedSetPermission`, `unprotectedSetOwner`, `unprotectedSetTimes`, `unprotectedSetQuota`, `unprotectedSetReplication`, and `unprotectedSetStoragePolicy`.
- The implementation works with `INodesInPath`, `INode`, `INodeFile`, `INodeDirectory`, `QuotaCounts`, `StorageType`, `BlockStoragePolicy`, `BlockInfo`, and directory XAttrs for inherited storage policy state.

## Control Flow
Checked mutators reject reserved paths when relevant, resolve the path with a write `DirOp`, run owner/write/superuser checks, mutate while holding `FSDirectory`'s write lock, then log the corresponding edit record if state changed. `setOwner` has nuanced owner/group authorization: non-superusers may not change owner and may only set groups they belong to. `setReplication` verifies the target replication with `BlockManager`, skips non-files and striped files, updates quotas before increasing and after decreasing replication, and updates each block's replication in the block manager. Storage policy changes validate the policy ID/name, reject copy-on-create policies on existing files, and store directory policies through `BlockStoragePolicySuite` XAttrs.

## State And Persistence Behavior
Persistent state changes are inode permission bits, user/group fields, mtime/atime, directory quota features, file replication, block manager replication metadata, and storage policy IDs or storage-policy XAttrs. Edit-log records are emitted with `logSetPermissions`, `logSetOwner`, `logTimes`, `logSetReplication`, `logSetStoragePolicy`, `logSetQuota`, and `logSetQuotaByStorageType`. Snapshot-aware mutation uses `iip.getLatestSnapshotId()` and `recordModification` where required.

## Dependencies And Integration Points
This file integrates with `FSDirectory` locking/path resolution/quota accounting, `BlockManager` replication and storage policy suites, `FSDirXAttrOp` for directory storage policy XAttr replacement/removal, `SnapshotManager` access-time capture policy, and `FSEditLog` persistence. It is called by higher-level `FSNamesystem` RPC handlers and edit-log loading code.

## Risks And Edge Cases
Important risks are quota deltas during replication changes, copy-on-create storage policies being incorrectly changed after creation, access-time precision skipping needed updates, storage-type quota feature gating, and mutation of snapshot-protected paths. Replication explicitly returns `null` for striped files, so callers must not interpret that as a successful EC replication update.

## Test Signals
Useful tests cover chmod/chown edit logging only on real changes, non-superuser owner/group denial, timestamp precision behavior, quota reset/don't-set semantics including root quota reset, storage-type quota disabled errors, setting/unsetting directory storage policies through XAttrs, copy-on-create policy rejection, and replication quota/block-manager updates for increasing/decreasing replication.
