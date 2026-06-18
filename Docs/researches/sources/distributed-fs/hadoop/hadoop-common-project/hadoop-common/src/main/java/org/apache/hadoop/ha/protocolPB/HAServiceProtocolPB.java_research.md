# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolPB.java

Purpose: Marker interface binding generated protobuf `HAServiceProtocolService.BlockingInterface` to Hadoop `VersionedProtocol` with the HA service protocol name and version.

Important APIs and types: `HAServiceProtocolPB extends HAServiceProtocolService.BlockingInterface, VersionedProtocol`, annotated with Kerberos server principal, `@ProtocolInfo(protocolName = "org.apache.hadoop.ha.HAServiceProtocol", protocolVersion = 1)`, and public/evolving audience metadata.

Control flow: No method bodies. Hadoop RPC uses this interface to identify protocol version and dispatch generated protobuf service methods through translators.

State and persistence: No state.

Dependencies and integration points: Used by client-side and server-side HA service protocol translators and by `HAServiceTarget` proxy construction. Depends on generated HA service protobufs and Hadoop IPC protocol metadata.

Risks: Protocol name/version changes are wire-compatibility changes. Because annotations drive Kerberos and RPC behavior, incorrect metadata breaks authentication or client/server negotiation.

Test signals: Compile coverage, protobuf RPC integration tests, secure-cluster tests, and protocol version negotiation tests cover this file.
