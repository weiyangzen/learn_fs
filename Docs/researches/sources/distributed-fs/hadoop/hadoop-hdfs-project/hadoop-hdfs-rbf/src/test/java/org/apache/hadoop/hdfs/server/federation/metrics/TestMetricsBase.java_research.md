# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestMetricsBase.java

## Purpose
`TestMetricsBase` is a reusable JUnit base for RBF metrics tests. It starts a router with state store, metrics, and HTTP enabled, seeds membership, mount-table, and router records, and exposes fixture accessors to subclasses.

## Important APIs, Types, and Functions
Setup uses `RouterConfigBuilder().stateStore().metrics().http()`, `Router`, `StateStoreService`, `MembershipStore`, and `RouterStore`. Fixture methods include `createFixtures()`, `getNameserviceStateMap(JSONObject)`, `refreshNamenodeRegistration()`, and protected getters for active/standby memberships, mount tables, routers, nameservices, router, and state store.

## Control Flow
`setupBase()` initializes and starts the router once per test instance, waits for the state store, clears all records, creates two nameservices with active and standby membership heartbeats, synchronizes mock mount-table records, adds two mock router heartbeats, refreshes caches, and pauses for metrics visibility. `testObserverMetrics()` adds an observer membership for `ns0`, reloads state-store and resolver caches, then asserts the nameservice JSON reports `OBSERVER`.

## State and Persistence
The state-store test driver holds `MembershipState`, `MountTable`, and `RouterState` records. Router caches and `MembershipNamenodeResolver` caches are explicitly refreshed. Teardown stops and closes the router.

## Dependencies and Integration Points
The class integrates federation state-store protocol requests, router metrics, router store, membership store, JSON parsing, and resolver cache loading. It is the foundation for `TestRBFMetrics` and also directly tests observer metrics behavior.

## Risks and Test Signals
The `Thread.sleep(1000)` after cache refresh is a timing buffer that can mask slow async registration. Fixture records use utility-generated stats, so metric expectations depend on those utilities. Passing tests signal state-store records are visible to metrics, observer state can win nameservice reporting, and refreshed membership registrations update both store and resolver caches.
