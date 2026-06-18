# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMultipleNNPortQOP.java

## Purpose
This security integration test verifies that a NameNode exposed on multiple RPC ports can apply different SASL quality-of-protection values and communicate the established QOP through block tokens for DataNode data transfer.

## Important APIs, Types, And Functions
The class extends `SaslDataTransferTestCase`. `setup` creates a secure config with auxiliary RPC ports `12001`, `12101`, and `12201`, maps ingress ports to authentication, integrity, and privacy QOPs, sets service RPC separately, and enables NameNode QOP sending. Tests are `testAuxiliaryPortSendingQOP`, `testMultipleNNPort`, and `testMultipleNNPortOverwriteDownStream`. `getHandshakeSecret` decodes `BlockTokenIdentifier` from `DFSTestUtil.getBlockToken`, and `doTest` writes/reads files and checks block locations.

## Control Flow
Tests start a secure three-DataNode cluster, create client URIs for each auxiliary port, and remove the server-side resolver from client configuration. The handshake test confirms the primary port does not include a handshake secret while auxiliary ports do. The port/QOP test performs file operations through each QOP-specific URI and inspects each DataNode's `SaslDataTransferServer.getNegotiatedQOP`. The overwrite test enables downstream QOP override and checks DataNode SASL client/server QOP state.

## State And Persistence
State includes port-to-QOP resolver configuration, block-token handshake message bytes, SASL server negotiated QOP, SASL client target QOP, and file/block placement state. There is no restart persistence; the focus is live negotiation and token contents.

## Dependencies And Integration Points
It integrates NameNode auxiliary RPC ports, `IngressPortBasedResolver`, `HADOOP_RPC_PROTECTION`, HDFS block tokens, `SaslDataTransferServer`, DataNode SASL clients, `FileSystem.get(URI, conf)`, and downstream encryption/QOP override keys.

## Risks
The test uses fixed ports, so parallel test environments can collide. It assumes exact QOP string mappings (`auth`, `auth-int`, `auth-conf`) and that at least two DataNodes appear in upstream positions when downstream QOP is overwritten. Security config ordering is important because service RPC must not resolve to an auxiliary client port.

## Test Signals
Signals include empty handshake secret on the primary port, non-empty secrets on auxiliary ports, successful file reads and three-host block locations for all QOPs, exact DataNode negotiated QOP strings, and downstream override causing at least two target QOPs to become `auth`.
