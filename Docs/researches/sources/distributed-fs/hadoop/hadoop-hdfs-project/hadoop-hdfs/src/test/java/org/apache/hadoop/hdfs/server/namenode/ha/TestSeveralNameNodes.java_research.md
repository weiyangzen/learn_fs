# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestSeveralNameNodes.java

Purpose: stress-tests an HA cluster with three NameNodes under continuous failover while multiple clients create and verify linked lists of files.

Important APIs and types: `HAStressTestHarness`, `MiniDFSCluster`, `HdfsClientConfigKeys.Failover`, `MultithreadedTestUtil.TestContext`, `RepeatingTestThread`, `FileSystem`, `FSDataOutputStream`, and `FSDataInputStream`.

Control flow: the test configures the harness for three NameNodes, starts a failover thread every second, increases client failover attempts, and starts NN0 as active. It creates three `CircularWriter` threads under separate directories. Each writer repeatedly creates files named by index and writes the next index as a byte until it reaches length 50, then reads the chain back to ensure every referenced file exists. The outer test waits up to 100 seconds for all writers to signal completion and fails with thread state if any remain.

State and persistence behavior: namespace mutations are simple create/delete-like writes under separate directories, but they are performed while active service moves among three NNs. The file content acts as a small persisted pointer to the next expected path.

Dependencies and integration points: integrates with the HA stress harness's failover thread and failover FileSystem client, plus Hadoop's multithreaded test context for exception propagation.

Risks and test signals: risks include client retry exhaustion, failed create/open during multi-NN failover, namespace inconsistency visible to later reads, and three-NN bugs hidden by two-NN tests. Completion of all writers and full traversal of every circular-list directory are the core signals.
