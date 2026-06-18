# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestLargeBlockReport.java

Purpose: This integration test validates that very large DataNode block reports are rejected or accepted according to the RPC maximum data length configuration.

Important APIs/types/functions: `IPC_MAXIMUM_DATA_LENGTH`, `MiniDFSCluster`, `BPOfferService.getActiveNN`, `DatanodeProtocolClientSideTranslatorPB.blockReport`, `BlockReportContext`, `BlockListAsLongs.decodeLongs`, and `StorageBlockReport`.

Control flow: Each test configures the IPC length limit, starts a one-DataNode cluster, obtains the active NameNode proxy and current storage ID, constructs a fake six-million-block report using old-style long-list decoding, and invokes `blockReport`. The low-limit case expects the RPC to fail; the high-limit case expects the call to complete.

State and persistence behavior: The block report content is synthetic and not intended to represent persisted blocks. The persistent state under test is RPC framing/deserialization acceptance rather than NameNode block map mutation.

Dependencies and integration points: It exercises Hadoop IPC server request-size checks, protobuf deserialization path tolerance, DataNode protocol block-report RPC, and MiniDFSCluster block-pool registration setup.

Risks and test signals: The rejection test intentionally avoids asserting exception type or message because server disconnect details are log-dependent. Runtime and memory pressure are risks due to constructing enormous report payloads.
