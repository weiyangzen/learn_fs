# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOrderedSnapshotDeletionGc.java

Purpose: Tests `SnapshotDeletionGc`, the background cleanup path for ordered snapshot deletion.

Important APIs/types/functions: enables ordered deletion and sets `DFS_NAMENODE_SNAPSHOT_DELETION_ORDERED_GC_PERIOD_MS` to 10 ms. Helpers include `exist`, `waitForGc`, `createSnapshots`, and `doEditLogValidation`, which counts `OP_DELETE_SNAPSHOT` edit-log records using `FSImageTestUtil.countEditLogOpTypes`.

Control flow: `testSingleDir` creates snapshots `s0/s1/s2`, deletes `s2` and `s1` out of order, verifies they are marked deleted and renamed, sleeps to confirm they are not GCed while `s0` remains, then deletes `s0` and waits for GC to remove the marked snapshots. It validates five delete-snapshot edit-log ops: three user deletes plus two GC deletes. `testMultipleDirs` creates 10 snapshottable dirs with random snapshot counts, shuffles all snapshot paths, deletes them, waits for GC, and validates restart/replay without fixed op count.

State and persistence behavior: after edit-log validation the cluster restarts with GC delayed for a long period, ensuring replayed edits alone leave snapshot count zero.

Dependencies and integration points: integrates ordered deletion marker assertions from `TestOrderedSnapshotDeletion`, FSImage/NNStorage edit files, edit-log op counting, and background GC scheduling.

Risks and test signals: strong coverage of delayed deletion ordering and edit-log persistence. Random multi-dir case broadens coverage but intentionally avoids deterministic edit count.
