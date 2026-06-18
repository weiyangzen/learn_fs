<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockDispatcher.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockDispatcher.java

Purpose: `BlockDispatcher` performs a single Storage Policy Satisfier block-replica movement by connecting to a target DataNode and issuing a DataTransferProtocol `replaceBlock` request.

Important APIs and functions: the constructor captures socket timeout, I/O buffer size, and whether to connect to DataNodes by hostname. `moveBlock` takes `BlockMovingInfo`, SASL client, `ExtendedBlock`, socket, data-encryption-key factory, and access token. `sendRequest` wraps `Sender.replaceBlock`; `receiveResponse` consumes `IN_PROGRESS` responses until a terminal response and validates it through `DataTransferProtoUtil.checkBlockOpStatus`. `newSocket` is visible for testing.

Control flow and state: the dispatcher is mostly immutable. `moveBlock` connects to the target xfer address, sets read timeout to `socketTimeout * 5`, performs SASL negotiation, sends the replace request naming the source DataNode and target storage type, waits for terminal response, and returns success. One `InvalidEncryptionKeyException` is retried after clearing the encryption key and creating a new socket. `BlockPinningException` is treated as success because pinned blocks should not be retried.

Persistence and dependencies: no local persistence. It affects block placement by asking a target DataNode to copy/replace a replica. Dependencies include DataTransferProtocol `Sender`, SASL/encryption token machinery, `BlockStorageMovementCommand.BlockMovingInfo`, `StorageType`, and network utilities.

Integration points: SPS mover tasks use this class to satisfy storage policies and report `BlockMovementStatus` to tracking code.

Risks and test signals: socket ownership is transferred to the method and always closed. Retry is limited to one encryption-key refresh. Treating pinning as success is intentional but can mask policy non-compliance if callers expect a physical move. Tests should mock successful terminal response, repeated `IN_PROGRESS`, encryption key retry, block pinning, protocol failure status, socket timeout, and hostname versus IP target selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockDispatcher.java -->
