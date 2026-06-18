<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsCreateMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsCreateMkdir.java

Purpose: Runs generic FileContext create/mkdir tests against HDFS.
Important APIs/types/functions: `TestFcHdfsCreateMkdir` extends `FileContextCreateMkdirBaseTest`, overrides `createFileContextHelper()`, and manages static MiniDFSCluster/FileContext setup.
Control flow: Before all tests, a two-Datanode HDFS cluster starts, `fc` is bound to its URI, and the current user's working directory is created. Inherited base tests exercise create and mkdir semantics; teardown delegates to the base class per test and shuts down the cluster at the end.
State and persistence behavior: Static cluster and default working directory are shared across inherited tests; filesystem mutations are cleaned by base helpers.
Dependencies and integration points: Integrates HDFS with the common FileContext create/mkdir contract tests.
Risks and edge cases: Shared static cluster means inherited tests must clean their roots. The local `defaultWorkingDirectory` is created but not overridden for base access in this class, so behavior depends on the base class's expectations.
Test signals: Signals are inherited assertions for recursive mkdir, create parent behavior, existing-path handling, and HDFS URI qualification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsCreateMkdir.java -->
