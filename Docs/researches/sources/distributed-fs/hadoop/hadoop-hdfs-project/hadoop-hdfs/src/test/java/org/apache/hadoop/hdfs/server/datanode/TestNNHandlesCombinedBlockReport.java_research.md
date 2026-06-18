# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestNNHandlesCombinedBlockReport.java

Purpose: This subclass runs `BlockReportTestBase` with legacy behavior where one DataNode sends all storage reports in a single combined block-report RPC.

Important APIs/types/functions: `BlockReportTestBase`, `sendBlockReports`, `DatanodeRegistration`, `StorageBlockReport[]`, `NameNodeRpcServer.blockReport`, and `BlockReportContext`.

Control flow: The override logs the registration and sends the complete `reports` array in one RPC with a one-part `BlockReportContext(1, 0, System.nanoTime(), 0L)`.

State and persistence behavior: All durable block, storage, and NameNode state changes are inherited from the base class. This file only controls report batching semantics and therefore tests compatibility with older logical-single-storage DataNode behavior.

Dependencies and integration points: It connects the base NameNode block-report tests to the combined-report protocol path and verifies the NameNode still accepts reports that are not split per storage.

Risks and test signals: Signals are inherited base assertions about block report correctness. The main local risk is regression in backward compatibility if combined report contexts are mishandled.
