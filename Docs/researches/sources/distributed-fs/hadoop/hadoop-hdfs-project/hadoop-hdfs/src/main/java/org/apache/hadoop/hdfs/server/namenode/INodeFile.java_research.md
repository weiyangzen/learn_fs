<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFile.java

## Purpose

`INodeFile` is the NameNode namespace object for HDFS files. It combines inode metadata from `INodeWithAdditionalFields` with file-specific block layout, block ownership, snapshot state, under-construction state, quota accounting, content-summary accounting, and block reclamation. It implements both `INodeFileAttributes` for snapshot metadata views and `BlockCollection` for integration with block management.

## Important APIs and Types

The nested `HeaderFormat` packs preferred block size, block layout/redundancy, and storage policy into a single `long`. It distinguishes contiguous replicated files from striped erasure-coded files by a layout bit and stores either replication or EC policy id in the remaining redundancy bits. Constructors validate that any existing `BlockInfo` entries match the file block type. Important mutators include `toUnderConstruction`, `toCompleteFile`, `setFileReplication`, `setStoragePolicyID`, `addBlock`, `concatBlocks`, `removeLastBlock`, `truncateBlocksTo`, and `clearFile`. Query APIs include `getBlocks`, `getBlocks(snapshot)`, `computeFileSize`, `storagespaceConsumed`, `computeQuotaUsage`, and `computeContentSummary`.

## Control Flow, State, and Persistence

The file's durable state is the inherited inode id/name/permission/times plus `header`, `blocks`, and optional features. Snapshot behavior is mediated by `FileWithSnapshotFeature` and `FileDiffList`: `recordModification` creates or updates file diffs before live metadata changes, `getSnapshotINode` retrieves historical attributes, and `getBlocks(snapshot)` can return block arrays saved during truncate. Under-construction behavior is stored as a `FileUnderConstructionFeature`; completion checks block UC states and, for committed last blocks, validates expected locations or striped internal block count. Destruction and subtree cleanup add quota deltas, collect deleted blocks, clear ACL/features, remove snapshot diffs, and remember removed under-construction file ids.

## Dependencies and Integration Points

This class sits at the intersection of namespace, snapshots, block management, erasure coding, storage policy, ACL/XAttr storage, and visitor traversal. It uses `BlockManager` when concatenating blocks to adjust replication, `BlockStoragePolicySuite` for storage-type quota, `ErasureCodingPolicyManager` for striped layout validation, and snapshot classes such as `FileDiff`, `FileDiffList`, and `Snapshot`.

## Risks and Test Signals

Risks concentrate around packed-header compatibility, replicated versus striped branch behavior, snapshot/truncate block retention, and quota deltas when blocks exist both in current state and snapshots. Important tests should cover header encoding for replication/EC/storage policy, completing UC files with committed last blocks, concat replication updates, delete/truncate with snapshots, EC storage policy suitability, storage-space accounting for incomplete striped blocks, and block retention when snapshots reference earlier arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFile.java -->
