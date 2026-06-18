<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolServerSideTranslatorPB.java

Purpose: server-side protobuf adapter for `ZKFCProtocolPB`. It exposes ZKFC administrative operations over protobuf RPC and delegates to the native `ZKFCProtocol` implementation.

Important APIs, types, and functions: constructor stores the `ZKFCProtocol` server. `cedeActive()` extracts `millisToCede`, `gracefulFailover()` delegates directly, and both return default empty protobuf responses. `getProtocolVersion()` and `getProtocolSignature()` support Hadoop RPC compatibility checks.

Control flow: protobuf RPC enters this translator, the translator calls the backing ZKFC server, and `IOException` is wrapped as `ServiceException`. Protocol signature rejects unknown protocol names before returning the negotiated signature.

State and persistence: no persistent state. Runtime state is the delegate reference. HA/failover state changes are owned by the delegate and external coordination systems.

Dependencies and integration points: depends on generated ZKFC protobuf messages, `RPC`, `ProtocolSignature`, and the HA failover controller service implementation.

Risks and test signals: `getProtocolSignature()` passes `HAServiceProtocolPB.class` to `ProtocolSignature.getProtocolSignature()` even though this translator implements `ZKFCProtocolPB`, which is a compatibility-sensitive point worth regression coverage. Tests should cover cede duration propagation, graceful failover delegation, exception wrapping, and protocol mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolServerSideTranslatorPB.java -->
