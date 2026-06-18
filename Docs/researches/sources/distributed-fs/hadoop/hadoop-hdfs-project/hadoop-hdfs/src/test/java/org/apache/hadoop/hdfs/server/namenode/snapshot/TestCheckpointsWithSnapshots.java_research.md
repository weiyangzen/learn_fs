# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestCheckpointsWithSnapshots.java

Purpose: Regression test for HDFS-5433, ensuring SecondaryNameNode checkpoint reload clears stale snapshottable-directory state when the primary NameNode image no longer contains snapshots or snapshottable directories.

Important APIs/types/functions: `MiniDFSCluster`, `SecondaryNameNode`, `HdfsAdmin.allowSnapshot/disallowSnapshot`, `SnapshotManager.getNumSnapshots`, `SnapshotManager.getNumSnapshottableDirs`, and `NameNodeAdapter.saveNamespace`.

Control flow: setup deletes the MiniDFSCluster base directory. The test starts a primary NameNode and a 2NN, creates `/foo`, marks it snapshottable, creates one snapshot, and checkpoints to load that state into the 2NN. It then deletes the snapshot, disallows snapshots on `/foo`, saves a fresh namespace on the primary, and triggers another 2NN checkpoint.

State and persistence behavior: before any operations both SnapshotManagers report zero snapshots/directories. After snapshot creation primary state reports one of each, and after the first checkpoint the secondary matches. After deletion/disallow and a saved namespace, the second checkpoint must leave the secondary with zero snapshots and zero snapshottable dirs, proving reload reset both image tree and manager-side lists.

Dependencies and integration points: exercises image transfer/reload between `NameNode` and `SecondaryNameNode`, admin snapshot APIs, and snapshot manager counters.

Risks and test signals: the final counter assertions are a targeted signal for stale manager entries that could otherwise serialize invalid fsimages. It does not restart the primary from the 2NN output in this test, relying on counters as the failure proxy.
