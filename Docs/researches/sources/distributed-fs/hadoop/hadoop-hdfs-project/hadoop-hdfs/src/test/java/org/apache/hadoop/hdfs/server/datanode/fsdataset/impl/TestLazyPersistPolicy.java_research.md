<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistPolicy.java

Purpose: compact tests for HDFS lazy-persist storage-policy metadata propagation and persistence. It verifies the policy is absent by default, present when creating a lazy-persist file, and survives both edit-log replay and FsImage checkpoint/restart.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `getClusterBuilder`, `makeTestFile`, HDFS client `getFileInfo`, `HdfsFileStatus.getStoragePolicy`, `LAZY_PERSIST_POLICY_ID`, `cluster.restartNameNode`, `SafeModeAction.ENTER/LEAVE`, and `fs.saveNamespace`.

Control flow: each test starts the shared lazy-persist cluster builder, creates a zero-length test file either with or without lazy-persist enabled, then stats the file through the client. The default case asserts the storage policy ID differs from `LAZY_PERSIST_POLICY_ID`. The propagation case asserts equality immediately after creation. The edit-log case restarts the NameNode with edits replay and checks the policy remains. The FsImage case enters safe mode, saves namespace, leaves safe mode, restarts the NameNode, and checks the stored policy again.

State and persistence behavior: state under test is NameNode inode storage policy metadata, not DataNode replica placement. The policy must be serialized in edit logs and FsImage and exposed through `HdfsFileStatus`.

Dependencies and integration points: integrates the lazy-persist file-creation helper, HDFS client protocol file status, NameNode restart, safe mode, and namespace checkpoint persistence.

Risks: because files are zero-length, the tests isolate metadata but do not validate RAM_DISK placement or lazy writer behavior. They depend on `LazyPersistTestCase` constants matching the cluster's configured policy IDs.

Test signals: failures identify storage-policy propagation bugs, edit-log serialization regressions, FsImage serialization regressions, or accidental defaulting of normal files to lazy persist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistPolicy.java -->
