# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreRouterState.java

Purpose: `TestStateStoreRouterState` tests `RouterStore`, the state-store facade that records router heartbeats, exposes individual router registrations, and lists all router states. It reduces router expiration and deletion windows to two seconds via `RBFConfigKeys.FEDERATION_STORE_ROUTER_EXPIRATION_MS` and `FEDERATION_STORE_ROUTER_EXPIRATION_DELETION_MS`.

Important APIs and helpers: it uses `RouterHeartbeatRequest`, `GetRouterRegistrationRequest`, `GetRouterRegistrationsRequest`, `RouterState`, and `RouterServiceState`. The test verifies heartbeat-populated metadata, including router address, service status, build version, and `FederationUtil.getCompileInfo()`.

Control flow and state behavior: each test clears `RouterState` records. `testUpdateRouterStatus()` submits a `RUNNING` heartbeat and immediately reads the same router by address. `testRouterStateExpiredAndDeletion()` writes a running heartbeat, waits until subsequent reads report `EXPIRED`, sends another heartbeat to revive the record, waits for it to expire again, and then waits until deletion produces a record with null status. `testGetAllRouterStates()` writes two router heartbeats, reloads the cache, sorts returned records, and verifies both addresses and statuses.

Persistence and cache semantics: router heartbeats persist state-store records with last-modified timestamps that drive expiry. Reads use the router store and cache refresh where needed. The expiry test demonstrates a three-phase lifecycle: running, expired, and deleted/null-status after deletion grace.

Dependencies and integration points: the class depends on state-store protocol classes, router status/config types, `GenericTestUtils.waitFor`, and Hadoop time utilities. It uses the same state-store base fixture as the membership and mount-table tests, so it is a cross-driver behavior test when run with different state-store configurations.

Risks and test signals: the test is timing-sensitive because it polls for two-second expiry/deletion windows with three-second timeouts. It signals that heartbeat refresh must restore an expired router to running, and that disconnected-driver behavior must raise `StateStoreUnavailableException` for single get, list get, and heartbeat writes.
