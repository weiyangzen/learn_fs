<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RouterHeartbeatRequestPBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RouterHeartbeatRequestPBImpl.java

## Purpose
PB implementation of `RouterHeartbeatRequest`, carrying a `RouterState` record into the State Store heartbeat path.

## APIs, Types, and Functions
Wraps `RouterHeartbeatRequestProto`. `getRouter()` converts nested `RouterRecordProto` to `RouterStatePBImpl`; `setRouter(RouterState)` accepts a `RouterStatePBImpl` and stores its proto.

## Control Flow, State, and Persistence
Heartbeat code builds or updates a `RouterState`, sets it into the request, and sends it to the state store. The request is transient, but the nested router record contains persistent router address, status, version, compile info, timestamps, admin address, and state-store version.

## Dependencies and Integration
Depends on `RouterState`, `RouterStatePBImpl`, generated `RouterRecordProto`, and the PB translator. It is exercised by `RouterHeartbeatService` and router registration stores.

## Risks and Test Signals
`setRouter()` silently ignores non-PB implementations instead of throwing, which can produce an empty request if serializer configuration diverges. `TestRouterHeartbeatService` and router registration tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RouterHeartbeatRequestPBImpl.java -->
