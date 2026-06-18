<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClose.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClose.java

Purpose: Checks close semantics for an HDFS output stream: writes after close must fail with `ClosedChannelException`, while repeated close calls must be harmless.

Important APIs, types, and functions: `MiniDFSCluster`, `FileSystem.get`, `FileSystem.create`, `OutputStream.write`, `OutputStream.close`, and `ClosedChannelException`.

Control flow: The test starts a default MiniDFSCluster, creates `/test`, writes `"foo"`, closes the stream, attempts another write and expects `ClosedChannelException`, then calls `close` a second time and expects no failure. The cluster is shut down in a `finally` block.

State and persistence behavior: The only persisted HDFS state is a small created file. The test is about client stream lifecycle state after close, not file content or restart persistence.

Dependencies and integration points: Integrates Hadoop `FileSystem` stream creation with HDFS client output stream state and Java channel-style close exception behavior.

Risks: This is a narrow behavior test. It does not assert file length or bytes; it only verifies post-close stream API behavior.

Test signals: Success means the client refuses writes after close with the specific expected exception and tolerates idempotent close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClose.java -->
