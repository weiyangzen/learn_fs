<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestNNWithQJM.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestNNWithQJM.java

Purpose: Integration tests for a NameNode using Quorum Journal Manager as its edits directory.

Important APIs/types/functions: `MiniJournalCluster`, `MiniDFSCluster`, `NameNode.format`, `ExitUtil`, `DFS_NAMENODE_NAME_DIR_KEY`, `DFS_NAMENODE_EDITS_DIR_KEY`, `manageNameDfsDirs(false)`, and `RemoteException` fencing assertions.

Control flow: Each test starts JournalNodes in `startJNs` and stops them after. `testLogAndRestart` configures local image dir plus QJM edits dir, starts a zero-DataNode cluster, creates a directory, restarts the NameNode, verifies persistence, writes another directory, restarts again, and verifies both edits. `testNewNamenodeTakesOverWriter` formats one NN, copies its image dir to a second NN, starts the first, writes an edit, starts the second against the same quorum, verifies it sees the edit, then verifies the old NN is fenced when it tries to write. `testMismatchedNNIsRejected` formats QJM with one namespace, reformats only local storage, and expects restart against old JournalNodes to fail.

State and persistence behavior: Persists NameNode image directories, QJM edit logs, copied namespace state, and directory creation edits. It deliberately creates namespace mismatch and writer-fencing scenarios.

Dependencies and integration points: Exercises NameNode startup/restart, QJM shared edits, JournalNode namespace validation, edit persistence, and fencing semantics.

Risks: `testNewNamenodeTakesOverWriter` leaves `cluster.shutdown()` commented in `finally`, relying on process/test cleanup. Tests inspect exception text and use global `ExitUtil.disableSystemExit`.

Test signals: Passing means QJM edits survive restarts, a new NameNode can recover and take over the writer role, old writers are fenced, and mismatched local/QJM namespaces are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestNNWithQJM.java -->
