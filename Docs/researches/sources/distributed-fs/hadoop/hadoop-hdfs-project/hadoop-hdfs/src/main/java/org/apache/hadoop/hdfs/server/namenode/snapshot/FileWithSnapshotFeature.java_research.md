# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileWithSnapshotFeature.java

## Purpose

`FileWithSnapshotFeature` attaches snapshot state to an `INodeFile`. It tracks file diffs, distinguishes files deleted from the current namespace but retained by snapshots, detects file changes between snapshots, and coordinates quota, ACL, replication, and block cleanup when snapshots or current files are removed.

## Important APIs, Types, And Functions

Important state is `FileDiffList diffs` and `isCurrentFileDeleted`. Key methods include `deleteCurrentFile`, `getMaxBlockRepInDiffs`, `changedBetweenSnapshots`, `cleanFile`, `clearDiffs`, `updateQuotaAndCollectBlocks`, and `collectBlocksAndClear`.

## Control Flow

Current-file deletion records a modification against the prior snapshot when needed, marks the feature deleted, computes old quota, and calls `collectBlocksAndClear`. Snapshot deletion updates the prior snapshot ID and asks the diff list to delete the target diff. Change detection compares file lengths at earlier/later points and, if equal, compares snapshot metadata copies. Block/quota cleanup builds a distinct set of blocks across current file, removed diff, and remaining diffs when snapshot attributes exist, releases ACL references, combines snapshot blocks, updates replication factors to the maximum required by current and remaining snapshots, and records quota delta.

## State And Persistence Behavior

The durable state is the `FileDiffList` and each diff's snapshot attributes/size/blocks. `isCurrentFileDeleted` is in-memory state implied by file location and snapshot ownership, not a standalone FSImage field in this class. Cleanup can clear file blocks when no current file and no diffs remain, null snapshot block arrays, and update replication-factor changes in collected block updates.

## Dependencies And Integration Points

The feature integrates with `INodeFile` mutation and deletion, `FileDiffList`, `AclStorage`, block storage policies, quota accounting, `BlockInfo`, `SnapshotDiffInfo`, FSImage formats, and block manager update flows.

## Risks And Edge Cases

Quota accounting must consider distinct block references and storage policy type quotas. Metadata comparison can miss changes if snapshot copies are not recorded at the correct time. Replication factors may need to remain elevated because a snapshot copy still needs a higher replication than the current file. `collectBlocksAndClear` must distinguish max snapshot size from current size and avoid deleting blocks retained by the latest snapshot block array.

## Test Signals

Tests should cover deleted-current-file retention by snapshots, metadata-only changes, length changes, replication changes across snapshots, ACL release, storage policy quota deltas, block collection beyond max snapshot size, and snapshot deletion when the final diff is removed.
