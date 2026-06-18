# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptedTransfer.java

## Purpose
Tests encrypted DataTransferProtocol behavior for reads, writes, appends, checksum operations, key expiry, DataNode pipeline recovery, cipher negotiation, and trusted-channel bypass. It is parameterized to run with normal encrypted transfer and with `TestTrustedChannelResolver`, where trusted peers skip normal encryption-key use.

## Important APIs and Types
Important APIs include `DFS_ENCRYPT_DATA_TRANSFER_KEY`, block access tokens, `DFS_DATA_ENCRYPTION_ALGORITHM_KEY`, cipher-suite configuration, `FileSystem.getFileChecksum`, `DFSClient.shouldEncryptData`, `DFSClient.clearDataEncryptionKey`, `DFSClient.connectToDN`, and `DFSOutputStream.getPipeline`. It uses `SaslDataTransferServer`, `DataTransferSaslUtil`, `BlockTokenSecretManager`, `DataEncryptionKey`, `InvalidEncryptionKeyException`, `LocatedBlock`, and `SystemErasureCodingPolicies`.

## Control Flow
`writeUnencryptedAndThenRestartEncryptedCluster` first writes plaintext data to an unencrypted cluster, records its checksum, restarts the same storage with encrypted transfer enabled, and returns a client whose config must discover encryption from the NameNode. Read tests validate checksum preservation and log evidence for RC4/AES/default negotiation. Long-lived-client tests restart NameNode/DataNode or let block-token keys expire, then confirm transparent key refresh. Invalid-key tests spy on `DFSClient` to verify stale keys are cleared and retried for both replicated and striped checksum paths. Write tests vary DataNode counts, test append, trigger block transfer during append, and force pipeline recovery after stopping a pipeline DataNode.

## State, Persistence, Dependencies, Integration
State includes block tokens, data encryption keys, transfer cipher config, DataNode token-secret managers, and stored HDFS blocks reused across cluster restarts. Dependencies are MiniDFSCluster, Mockito, log capture, EC policy setup for striped checksum coverage, and low retry/key lifetimes for expiry tests. Integration points span DFSClient, DataNode SASL negotiation, checksum retrieval, append pipeline recovery, and trusted-channel resolver configuration.

## Risks and Test Signals
Signals include preserved file contents/checksums after enabling transfer encryption, expected SASL/cipher log lines, explicit verification that invalid keys clear the cached encryption key, and pipeline replacement after a stopped DataNode. Risks are timing sensitivity around key expiry and log-string assertions; the trusted-channel parameter prevents false assumptions that every successful transfer used encryption keys.
