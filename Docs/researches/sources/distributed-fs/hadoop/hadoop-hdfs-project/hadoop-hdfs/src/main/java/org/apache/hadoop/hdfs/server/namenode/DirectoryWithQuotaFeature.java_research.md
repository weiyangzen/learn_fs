# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DirectoryWithQuotaFeature.java

## Purpose
`DirectoryWithQuotaFeature` is the `INode.Feature` attached to directories with namespace, storage-space, or per-storage-type quotas. It stores quota limits and cached usage and validates deltas before namespace changes.

## Important APIs and Types
The builder initializes default namespace quota to `Long.MAX_VALUE`, storage quota to reset/unset, type quotas to reset/unset, and initial usage namespace to one directory. Methods expose quota/usage copies, setters, `computeContentSummary`, `addSpaceConsumed2Cache`, `setSpaceConsumed`, `verifyQuota`, quota-presence checks, and string rendering.

## Control Flow
Quota verification checks namespace, storage-space, and type-space independently using `Quota.isViolated`. Content summary computation compares cached and computed storage-space only if the traversal did not yield, avoiding false warnings when the namespace may have changed mid-computation.

## State and Persistence
Quota and cached usage live in inode metadata and are persisted through inode/fsimage mechanisms outside this class. The class returns defensive `QuotaCounts` copies for public reads.

## Dependencies and Integration
It integrates with `INodeDirectory`, `QuotaCounts`, storage-type counters, snapshot content summary traversal, and HDFS quota exception types.

## Risks and Test Signals
Usage updates do not enforce quotas themselves; callers must call `verifyQuota` first. `typeSpaceString` appears to print `usage/usage` instead of `usage/quota`, making diagnostics misleading. Tests should cover all quota dimensions, unset quotas, content-summary consistency warnings, storage-type quota rendering, and quota bypass paths during image loading.
