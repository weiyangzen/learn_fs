# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestNNHandlesBlockReportPerStorage.java

Purpose: This subclass runs the shared `BlockReportTestBase` scenarios while sending one block report RPC per storage, matching modern post-HDFS-2832 DataNode behavior.

Important APIs/types/functions: `BlockReportTestBase`, `sendBlockReports`, `DatanodeRegistration`, `StorageBlockReport`, `NameNodeRpcServer.blockReport`, and `BlockReportContext`.

Control flow: The override loops through the provided `StorageBlockReport[]`, wraps each entry in a singleton array, and sends each RPC with `BlockReportContext(reports.length, i, System.nanoTime(), 0L)` so the NameNode can treat them as parts of one full-report cycle.

State and persistence behavior: This file owns no setup state; all files, blocks, storage mutations, and assertions come from the base test. Its behavior changes only how report batches are transported and indexed.

Dependencies and integration points: It integrates the base block-report correctness matrix with the NameNode path for split storage reports and report-context part numbering.

Risks and test signals: Signals are inherited from `BlockReportTestBase`. Local risk is that incorrect total/index context would make the base tests fail through NameNode block-report processing rather than obvious local assertions.
