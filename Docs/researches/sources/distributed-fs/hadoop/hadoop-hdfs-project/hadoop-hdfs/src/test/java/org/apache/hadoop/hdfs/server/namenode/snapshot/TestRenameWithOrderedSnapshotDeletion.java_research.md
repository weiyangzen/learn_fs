# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestRenameWithOrderedSnapshotDeletion.java

Purpose: Tests rename restrictions when ordered snapshot deletion and snapshot trash root support are enabled.

Important APIs/types/functions: configures `DFS_NAMENODE_SNAPSHOT_DELETION_ORDERED` and `DFS_NAMENODE_SNAPSHOT_TRASHROOT_ENABLED`. Uses `DistributedFileSystem.rename`, `allowSnapshot`, `createSnapshot`, and `DFSTestUtil.createFile`. `validateRename` asserts an `IOException` message contains "are not under the same snapshot root."

Control flow: the test creates a snapshottable directory, normal directories `/dir1` and `/dir2`, files inside `/dir1` and the snapshottable subtree, then checks forbidden and allowed rename cases. Moving a file from non-snapshottable into snapshottable root fails before and after creating snapshot `s0`; moving across non-snapshottable dirs succeeds. Moving out of the snapshottable root fails, while moving within the root succeeds. Directory rename cases similarly allow outside-to-outside and within-root renames, while rejecting crossing the snapshot root boundary.

State and persistence behavior: no restart/persistence path. The state focus is live validation of rename boundary rules under ordered deletion/trashroot mode.

Dependencies and integration points: integrates FSNamesystem snapshot trashroot config, ordered deletion config, and rename precondition logic.

Risks and test signals: clear boundary-condition coverage for same-snapshot-root enforcement. It validates exception text rather than type, so message changes can break the test even if behavior remains correct.
