<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHeartbeatService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHeartbeatService.java

## Purpose
`RouterHeartbeatService` periodically publishes the router's liveness, state, admin address, and state-store version view into the federation state store. Other routers and admin tools use these `RouterState` records to discover router status.

## Important APIs, Types, and Functions
It extends `PeriodicService`. `periodicInvoke` calls `updateStateStore`. `updateStateAsync` starts a daemon `SubjectInheritingThread` for asynchronous update. `updateStateStore` builds `RouterState`, adds `StateStoreVersion` from membership and mount-table cached records, sets the admin address according to heartbeat-with-IP configuration, and sends `RouterHeartbeatRequest` to `RouterStore.routerHeartbeat`. `getStateStoreVersion` scans cached records for the maximum modification time.

## Control Flow
Initialization reads `DFS_ROUTER_HEARTBEAT_STATE_INTERVAL_MS` and configures the periodic interval. Each tick checks router id and state-store availability, builds a heartbeat record from router runtime state, resolves version timestamps, chooses host:port or ip:port admin address, submits the heartbeat, and logs success or failure.

## State and Persistence Behavior
The service persists router heartbeat records in the state store via `RouterStore`; it keeps no independent durable state. Version values are inferred from cached record stores and default to `-1` if unavailable. The method is synchronized to avoid overlapping updates from periodic and async paths.

## Dependencies and Integration Points
Dependencies include `Router`, `RouterStore`, `StateStoreService`, `MembershipStore`, `MountTableStore`, `CachedRecordStore`, `RouterState`, `StateStoreVersion`, `StateStoreUtils`, `RouterHeartbeatRequest`, and `RouterHeartbeatResponse`.

## Risks
Heartbeat quality depends on state-store driver readiness and cached record freshness. If record stores are not `CachedRecordStore`, version stays `-1`. Admin address formatting differs based on configuration and can affect discoverability. Exceptions are logged but do not fail the periodic service, so monitoring must inspect heartbeat freshness.

## Test Signals
Tests should cover interval initialization, unavailable state store paths, null router id, heartbeat request fields, admin address IP-vs-host behavior, cached version extraction, failed heartbeat response logging, async thread creation, and synchronization under concurrent updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHeartbeatService.java -->
