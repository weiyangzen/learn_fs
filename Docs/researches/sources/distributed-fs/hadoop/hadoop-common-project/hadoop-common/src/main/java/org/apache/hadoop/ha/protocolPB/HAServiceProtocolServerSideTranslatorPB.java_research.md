<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolServerSideTranslatorPB.java

Purpose: server-side protobuf RPC adapter for `HAServiceProtocolPB`. It receives generated protobuf requests, calls the native `HAServiceProtocol` implementation, and converts Hadoop HA status and transition request metadata back into protobuf responses.

Important APIs, types, and functions: constructor stores the `HAServiceProtocol` delegate. `monitorHealth()`, `transitionToActive()`, `transitionToStandby()`, `transitionToObserver()`, and `getServiceStatus()` implement the protobuf blocking interface. `convert(HAStateChangeRequestInfoProto)` maps protobuf request-source enums into `HAServiceProtocol.RequestSource`. `getProtocolVersion()` and `getProtocolSignature()` expose Hadoop RPC version negotiation.

Control flow: each RPC method catches `IOException` from the HA service and wraps it in protobuf `ServiceException`. State-changing calls convert `reqInfo` before delegating. Status calls translate `HAServiceStatus.State` into `HAServiceStateProto`, set readiness, and include `notReadyReason` only when active transition is not allowed.

State and persistence: the translator has no persisted state. It only caches immutable empty response protobufs and a reference to the live HA service. Persistent HA state changes happen in the wrapped server, not here.

Dependencies and integration points: integrates Hadoop HA service interfaces with protobuf RPC engine types, `RPC` protocol metadata, `ProtocolSignature`, and generated `HAServiceProtocolProtos`.

Risks and test signals: unknown request-source enum values are logged and converted to null, so downstream service handling must tolerate or reject null request info. Tests should cover every HA state, readiness reason propagation, IOException-to-ServiceException wrapping, observer transitions, and protocol-name mismatch failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolServerSideTranslatorPB.java -->
