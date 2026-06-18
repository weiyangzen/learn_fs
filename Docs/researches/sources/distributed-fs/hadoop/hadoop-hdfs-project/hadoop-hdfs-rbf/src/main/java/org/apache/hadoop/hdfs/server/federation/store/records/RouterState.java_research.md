<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/RouterState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/RouterState.java

## Purpose
State Store schema for Router registrations and heartbeat state.

## APIs, Types, and Functions
Factory methods create initialized records and populate address, start time, service status, version, and compile info. Abstract fields include address, date started, state-store version, status, version, compile info, and admin address. Shared methods include `getRouterId()`, `like()`, `validate()`, router-address ordering, expiration/deletion support, and `isExpired()`.

## Control Flow, State, and Persistence
Primary key is router `address`. Validation requires an address unless the status is `INITIALIZING`. Expiration mutates status to `EXPIRED` and returns true for commit. Deletion is controlled by static class-level timeout.

## Dependencies and Integration
Used by `RouterHeartbeatService`, router registration stores, and admin/query APIs. Depends on `RouterServiceState`, `FederationUtil` build metadata helpers, `StateStoreVersion`, and PB storage via `RouterStatePBImpl`.

## Risks and Test Signals
`compareTo()` compares addresses directly and assumes non-null when comparing two router records. Static expiration/deletion settings affect all router records. `TestRouterHeartbeatService` is a key signal for version, heartbeat, and persisted state behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/RouterState.java -->
