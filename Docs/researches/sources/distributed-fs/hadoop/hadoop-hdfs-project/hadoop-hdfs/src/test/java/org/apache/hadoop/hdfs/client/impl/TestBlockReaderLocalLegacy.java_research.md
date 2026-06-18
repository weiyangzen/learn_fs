<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalLegacy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalLegacy.java

Purpose: Regression tests for the legacy short-circuit local block reader path and legacy DataNode local path RPC behavior.

Important APIs/types/functions: `getConfiguration` enables short-circuit reads, legacy `BlockReaderLocal`, block-local-path access user, disabled domain socket data traffic, and short retry windows. Tests use `DFSInputStream.tcpReadsDisabledForTesting`, `MiniDFSCluster`, `ClientDatanodeProtocol.getBlockLocalPathInfo`, `DFSUtilClient.createClientDatanodeProtocolProxy`, and `BlockLocalPathInfo`.

Control flow: `setupCluster` globally disables TCP reads for testing and domain socket path validation. `testStablePositionAfterCorruptRead` corrupts the only replica and verifies failed direct-buffer reads leave `position` and `limit` unchanged. `testBothOldAndNewShortCircuitConfigured` enables legacy and short-circuit settings together, closes the socket directory, and confirms reads still succeed. `testBlockReaderLocalLegacyWithAppend` captures a block generation stamp, appends one byte, then verifies local path info returns the new generation stamp for the original block handle.

State and persistence behavior: Creates temporary NameNode/DataNode storage, HDFS files, corrupted replicas, and appended block state. The append test persists a new generation stamp and validates that the DataNode resolves current metadata rather than stale client state.

Dependencies and integration points: Integrates `DistributedFileSystem`, NameNode block-location RPCs, DataNode client protocol, block tokens, and legacy local path access configuration.

Risks: Global `tcpReadsDisabledForTesting` is not reset here and can affect co-located tests if the test framework reuses JVM state. Native domain socket availability controls part of coverage. The socket-directory-close scenario is intentionally brittle and validates fallback semantics.

Test signals: Passing tests indicate legacy local reads preserve buffer state on checksum exceptions, coexist with newer short-circuit configuration, and expose up-to-date block generation stamps after append.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalLegacy.java -->
