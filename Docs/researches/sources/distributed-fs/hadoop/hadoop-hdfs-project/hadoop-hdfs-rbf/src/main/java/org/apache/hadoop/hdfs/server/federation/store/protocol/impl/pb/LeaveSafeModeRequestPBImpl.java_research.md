<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/LeaveSafeModeRequestPBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/LeaveSafeModeRequestPBImpl.java

## Purpose
Protobuf-backed implementation of the abstract `LeaveSafeModeRequest` state-store/admin request. The request carries no user fields; its value is the message type itself, used to ask a Router to leave safe mode.

## APIs, Types, and Functions
Implements `PBRecord` with `getProto()`, `setProto(Message)`, and `readInstance(String)`. It wraps `LeaveSafeModeRequestProto`, its builder, and `LeaveSafeModeRequestProtoOrBuilder` through `FederationProtocolPBTranslator`.

## Control Flow, State, and Persistence
Construction starts with an empty translator or an existing proto. `getProto()` builds the current protobuf, `setProto()` swaps in an incoming protobuf, and `readInstance()` decodes a base64 serialized instance through the shared translator. There is no record persistence or request-local state beyond the protobuf translator.

## Dependencies and Integration
Used by Router admin client/server protobuf translators and by `RouterStateManager.leaveSafeMode()`. It depends on generated `HdfsServerFederationProtos` classes and the common PB serialization contract.

## Risks and Test Signals
The class has no field validation, so correctness depends on RPC method routing and translator type safety. Test signals are safe-mode admin tests and server-side translator tests that round-trip empty leave-safe-mode requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/LeaveSafeModeRequestPBImpl.java -->
