<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockTokenWrappingQOP.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockTokenWrappingQOP.java

Purpose: Verifies that, when enabled, the NameNode sends the negotiated RPC quality-of-protection value back to the client inside block access tokens for add-block, append, and block-location calls.

Important APIs, types, and functions: Extends `SaslDataTransferTestCase`; uses `createSecureConfig`, `DFS_NAMENODE_SEND_QOP_ENABLED`, `DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY`, `HADOOP_RPC_PROTECTION`, `IngressPortBasedResolver`, `DFSClient.namenode.addBlock`, `append`, `getBlockLocations`, `LocatedBlock`, `LastBlockWithStatus`, and token `decodeIdentifier().getHandshakeMsg()`.

Control flow: Parameterized tests run for `privacy -> auth-conf`, `integrity -> auth-int`, and `authentication -> auth`. `setup` creates a secure config with an auxiliary NameNode RPC port, service RPC port, ingress-port SASL resolver, block tokens, and QOP-return enabled. The client connects through the auxiliary URI. `testAddBlockWrappingQOP` creates a file and calls `addBlock`; `testAppendWrappingQOP` writes one byte before append so a last block exists; `testGetBlockLocationWrappingQOP` writes one byte and checks every returned located block token.

State and persistence behavior: The relevant state is runtime security negotiation and the handshake message embedded in issued block tokens. The tests do not check persistence; clusters are rebuilt per parameter invocation and shut down after each test.

Dependencies and integration points: Integrates Hadoop RPC SASL configuration, ingress-port-specific QOP resolution, HDFS block token issuance, NameNode client protocol methods, and DFS client connection setup through an auxiliary port.

Risks: Security configuration is sensitive to port and resolver behavior. If RPC address handling changes, the auxiliary/service RPC split may need updates. The test decodes token internals directly, so token identifier format changes would affect assertions.

Test signals: Success means every tested NameNode response that carries a block token embeds the expected negotiated QOP string for the configured protection level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockTokenWrappingQOP.java -->
