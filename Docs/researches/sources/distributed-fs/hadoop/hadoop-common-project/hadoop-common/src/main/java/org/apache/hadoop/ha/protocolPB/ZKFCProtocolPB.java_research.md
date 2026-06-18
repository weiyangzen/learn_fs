<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolPB.java

Purpose: protobuf RPC protocol interface for the ZK Failover Controller. It binds the generated blocking protobuf service to Hadoop's `VersionedProtocol` and publishes security and protocol metadata.

Important APIs, types, and functions: the interface extends `ZKFCProtocolService.BlockingInterface` and `VersionedProtocol`. `@KerberosInfo` points at `hadoop.security.service.user.name`, while `@ProtocolInfo` declares protocol name `org.apache.hadoop.ha.ZKFCProtocol` and version 1.

Control flow: this file has no executable methods beyond inherited contracts. Hadoop RPC uses its annotations and type identity when creating client proxies and server endpoints.

State and persistence: no runtime or persisted state. Protocol version and name are compatibility contracts for RPC negotiation.

Dependencies and integration points: integrates generated protobuf service code, Hadoop RPC protocol discovery, Kerberos principal lookup, and the ZKFC native protocol translators.

Risks and test signals: changing the protocol name or version breaks wire compatibility. Tests should include RPC proxy construction, secure principal resolution, and server signature negotiation through the translators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolPB.java -->
