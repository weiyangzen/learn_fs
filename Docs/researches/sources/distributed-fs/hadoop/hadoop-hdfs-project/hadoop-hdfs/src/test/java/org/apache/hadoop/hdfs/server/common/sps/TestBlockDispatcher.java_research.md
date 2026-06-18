# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/sps/TestBlockDispatcher.java

Purpose: this test validates a retry-path detail in SPS `BlockDispatcher`: when SASL block movement fails due to `InvalidEncryptionKeyException`, the dispatcher must clear the cached data-encryption key before retrying.

Important APIs and types: `BlockDispatcher`, `BlockMovingInfo`, `SaslDataTransferClient`, `DataEncryptionKeyFactory`, `InvalidEncryptionKeyException`, `ExtendedBlock`, `Token<BlockTokenIdentifier>`, `DatanodeInfo`, `StorageType`, and a fake `Socket`.

Control flow: the test constructs source/target DataNodes, a block movement command, a `CountingKeyFactory`, and an `InvalidKeySaslClient` whose `socketSend` always throws `InvalidEncryptionKeyException` while counting attempts. A custom `BlockDispatcher` overrides `newSocket` to return `FakeSocket`. The call to `moveBlock` is expected to throw after retry; assertions require one key clear and two SASL send attempts.

State and persistence: there is no persistent state. Counters in fake collaborators capture retry behavior. The fake socket uses in-memory byte streams and no network connection.

Dependencies and integration points: the test sits at the data-transfer/SPS boundary, where storage policy satisfaction moves blocks between DataNodes and must handle encrypted data-transfer key expiry. It verifies `BlockDispatcher` retry side effects without requiring a real cluster or real SASL negotiation.

Risks: because the SASL client always throws, the test only validates the invalid-key retry path, not successful second-attempt movement. It also assumes exactly two attempts for this error class.

Test signals: failures mean encryption-key cache invalidation or retry count changed, which can affect block movement under encrypted data transfer.
