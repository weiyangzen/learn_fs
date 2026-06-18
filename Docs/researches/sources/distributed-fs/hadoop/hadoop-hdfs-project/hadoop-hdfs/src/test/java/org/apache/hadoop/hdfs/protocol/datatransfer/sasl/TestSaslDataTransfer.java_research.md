<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransfer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransfer.java

Purpose: End-to-end and unit-level coverage for SASL-protected HDFS DataTransferProtocol operation.

Important APIs/types/functions: Inherits `createSecureConfig`; uses `MiniDFSCluster`, `DFS_DATA_TRANSFER_PROTECTION_KEY`, `DFS_HTTP_POLICY_KEY`, `IGNORE_SECURE_PORTS_FOR_TESTING_KEY`, `SaslDataTransferClient`, `DataTransferSaslUtil`, `TrustedChannelResolver`, `DataEncryptionKeyFactory`, `DFSUtilClient.peerFromSocketAndKey`, and `DataNode` logs.

Control flow: QOP tests start a secure three-DataNode cluster, set client QOP to authentication/integrity/privacy, write/read a multi-block file, and verify block locations. Negative tests cover no common QOP, server SASL with no client SASL, DataNode abort when SASL is disabled under secure ports, HTTP policy rejection, HTTPS privacy acceptance, and secure-port ignore testing. Socket tests validate read timeout during SASL handshake and check trust combinations: partially trusted or untrusted channels must request an encryption key, fully trusted channels must not.

State and persistence behavior: Each test may start a MiniDFS cluster and create `/file1`. `shutdown` cleans `FileSystem` and cluster. Socket tests open local server/client sockets but do not accept full protocol handshakes.

Dependencies and integration points: Integrates Kerberos/SSL fixture, block tokens, DataTransferProtocol client/server negotiation, HTTP policy security checks, file IO, and trusted channel resolver logic.

Risks: Secure cluster startup is heavy and environment-sensitive. Some socket tests bind fixed port `10002`, which can conflict. Negative assertions inspect exception/log text.

Test signals: Passing indicates QOP negotiation works, insecure configurations are rejected, data reads succeed under all supported QOPs, timeouts are honored, and trust decisions correctly bypass or require SASL/encryption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransfer.java -->
