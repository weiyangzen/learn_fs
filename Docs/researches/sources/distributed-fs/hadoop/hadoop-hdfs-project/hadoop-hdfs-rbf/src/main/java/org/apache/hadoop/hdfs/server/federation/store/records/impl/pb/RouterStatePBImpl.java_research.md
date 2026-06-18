<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/RouterStatePBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/RouterStatePBImpl.java

## Purpose
Protobuf implementation of the `RouterState` registration/heartbeat record.

## APIs, Types, and Functions
Wraps `RouterRecordProto`. Accessors map address, state-store version, status, version, compile info, date started, date created/modified, and admin address. Nested `StateStoreVersion` is converted through `StateStoreVersionPBImpl`.

## Control Flow, State, and Persistence
Optional string/status setters clear fields on null. `getStateStoreVersion()` returns null when absent or injects the nested proto into a serializer-created version record. `setDateModified()` refuses updates when status is `EXPIRED`, matching `MembershipStatePBImpl` expiration semantics.

## Dependencies and Integration
Used by router heartbeat requests and router registration stores. Depends on `RouterServiceState`, `StateStoreSerializer`, `StateStoreVersionPBImpl`, generated router protos, and PB translator.

## Risks and Test Signals
`getStatus()` uses `RouterServiceState.valueOf()` and will throw on invalid stored strings. `getAdminAddress()` does not check `hasAdminAddress()`, returning default empty string if absent. Router heartbeat tests cover version embedding, expiration, and persisted router fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/RouterStatePBImpl.java -->
