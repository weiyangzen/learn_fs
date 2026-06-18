<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUnbuffer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUnbuffer.java

Purpose: Tests `FSDataInputStream.unbuffer()` behavior for HDFS TCP readers and capability policy failures.
Important APIs/types/functions: `TestUnbuffer`, `testUnbufferClosesSockets()`, `testOpenManyFilesViaTcp()`, and `testUnbufferException()`.
Control flow: Tests disable short-circuit reads to force TCP block readers, create files in MiniDFSCluster, read bytes, call `unbuffer()`, inspect `PeerCache`, and reopen/read many streams. The exception test mocks a stream that advertises unbuffer capability but does not implement `CanUnbuffer`.
State and persistence behavior: State includes a dedicated DFS client context peer cache, open input streams, and MiniDFSCluster namespace. Cleanup closes streams and clusters in finally blocks.
Dependencies and integration points: Integrates HDFS block readers, `PeerCache`, client context configuration, `FSDataInputStream`, `StreamCapabilitiesPolicy`, and Mockito.
Risks and edge cases: Socket-cache assertions depend on disabled short-circuit reads and long cache timeouts. The 500-open test is resource-sensitive. Mocked capability behavior must match policy strings.
Test signals: Signals are peer cache size changes after unbuffer, successful many-stream reads without socket exhaustion, and expected `UnsupportedOperationException` text for a buggy stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUnbuffer.java -->
