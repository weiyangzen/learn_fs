<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodesInPath.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodesInPath.java

## Purpose

`INodesInPath` represents the resolved inode chain for a path, including unresolved tail components, snapshot path state, latest snapshot ids for mutation recording, and raw-path status.

## Important APIs and Types

Key factories are `resolve`, `fromINode`, `fromINode(rootDir, inode)`, and `fromComponents`. Structural helpers include `replace`, `append`, `getExistingINodes`, `getParentINodesInPath`, `isDescendant`, and path/inode accessors. Snapshot-specific methods distinguish `getLatestSnapshotId` for non-snapshot paths from `getPathSnapshotId` for paths inside `.snapshot`.

## Control Flow, State, and Persistence

`resolve` walks components from a starting directory, records each inode, tracks whether it has entered a snapshot path, updates latest snapshot id while traversing snapshotted directories, and applies special reference-node rules using `DstReference` snapshot ids. When encountering `.snapshot/<name>`, it resolves the snapshot root and collapses the two path components into one so path components and inode array remain one-to-one for reconstruction. The object is immutable except for cached `pathname`.

## Dependencies and Integration Points

It depends on `DFSUtil`, `HdfsConstants.DOT_SNAPSHOT_DIR`, `HdfsServerConstants`, `INodeDirectory`, `DirectoryWithSnapshotFeature`, `Snapshot`, and `INodeReference`. It is used broadly by FSDirectory operations, lease handling, snapshot creation, deletion, and mutation paths needing the correct latest snapshot id.

## Risks and Test Signals

Risks include off-by-one component collapse, incorrect latest snapshot id when traversing references, raw path flag loss during replace/append, and invalid parent validation for snapshot roots. Tests should cover missing components, `.snapshot` as final component, nonexistent snapshot names, paths under snapshot roots, rename references with dst snapshots, `fromINode` for leased files, and descendant checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodesInPath.java -->
