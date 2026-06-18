# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSnapshotPathINodes.java

Purpose: Tests `INodesInPath` resolution for normal paths, snapshot paths, deleted snapshot files, newly added files after snapshots, modified files after snapshots, and short-circuit behavior when no snapshottable directories exist.

Important APIs and functions: Class setup starts a 3-DN MiniDFSCluster and caches `FSDirectory`/`DistributedFileSystem`; reset recreates `file1` and `file2`. Helpers include `getSnapshot`, `assertSnapshot`, `assertINodeFile`, and `getNumNonNull`. Tests use `INode.getPathComponents`, `INodesInPath.resolve`, `hdfs.allowSnapshot`, `createSnapshot`, `deleteSnapshot`, `disallowSnapshot`, and `FSDirSnapshotOp.checkSnapshot`.

Control flow: Normal path tests verify component/inode lengths and path strings. Snapshot tests resolve paths containing `/.snapshot/<name>/...`, verify `.snapshot` component handling, snapshot root index, null inode for bare `.snapshot`, and invalid path failures. Deletion/addition/modification tests compare snapshot and current inode resolution after mutating files post-snapshot.

State and persistence behavior: State is in-memory namespace inode tree with snapshot features, snapshot roots, file diffs, deleted inode references, modification timestamps, and latest/path snapshot IDs. No restart serialization is exercised.

Dependencies and integration points: Integrates `SnapshotManager`, `Snapshot`, `INodeDirectory`, `INodeFile`, `INodesInPath`, HDFS snapshot APIs, `DFSTestUtil`, and Mockito for verifying no interactions in the no-snapshot short-circuit case.

Risks: Snapshot path resolution is subtle because `.snapshot` is a virtual component that may not correspond to a real inode, and negative indexes are used to inspect trailing components. Incorrect latest/path snapshot ID handling can break permission checks, mutation routing, or content lookup.

Test signals: Signals include exact inode array lengths, correct snapshot flags and IDs, `Snapshot.Root` at the expected index, null last inode for bare `.snapshot` or missing snapshot file, preserved modification time for snapshot file, changed current file modification time, expected `FileNotFoundException`s, and zero interactions when there are no snapshottable directories.
