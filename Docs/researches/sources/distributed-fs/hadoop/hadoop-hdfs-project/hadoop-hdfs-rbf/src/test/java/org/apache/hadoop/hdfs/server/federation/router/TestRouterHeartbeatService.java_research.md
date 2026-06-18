# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterHeartbeatService.java

## Purpose

`TestRouterHeartbeatService.java` validates router heartbeat publication into a ZooKeeper-backed state store, including graceful behavior when the state store is unavailable. The source was read as a complete 145-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `Router`, `RouterHeartbeatService`, `StateStoreService`, `RouterStore`, `StateStoreZooKeeperImpl`, `TestingServer`, Curator `CuratorFramework`, `GetRouterRegistrationRequest/Response`, `RouterState`, and `StateStoreVersion`. Key methods are `setup`, `testStateStoreUnavailable`, `testStateStoreAvailable`, and `tearDown`.

## Control Flow

`setup` creates a router with ID `router1`, configures state-store support with ZooKeeper driver, starts an embedded ZooKeeper server and Curator client, starts the router, and waits for the state store. The unavailable test closes Curator, stops ZooKeeper and state store, asserts the driver is not ready, then calls `updateStateStore` and expects no thrown exception. The available test refreshes caches, observes no existing router ID/version, runs a heartbeat, refreshes again, and asserts router ID and state-store version are now present.

## State and Persistence Behavior

Router registration state is persisted in ZooKeeper through the federation state store. The heartbeat writes `RouterState` including router ID and `StateStoreVersion`. Cleanup closes Curator, stops ZooKeeper, and shuts down the router.

## Dependencies and Integration Points

This test integrates Router lifecycle, state-store driver readiness, ZooKeeper driver configuration, router state manager protocols, and heartbeat update logic.

## Risks and Edge Cases

The unavailable path only checks no exception escapes; it does not verify logging or retry state. The available path assumes refresh visibility after a single heartbeat and cache refresh. Embedded ZooKeeper lifecycle issues can affect test stability.

## Test Signals

Key signals are `isDriverReady` false/true in the two scenarios, null registration before heartbeat, non-null router ID and version after heartbeat, and no exception from `updateStateStore` when the driver is down.
