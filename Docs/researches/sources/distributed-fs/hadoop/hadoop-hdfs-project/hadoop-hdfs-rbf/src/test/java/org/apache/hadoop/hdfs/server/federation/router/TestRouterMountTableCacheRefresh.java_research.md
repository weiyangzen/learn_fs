# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableCacheRefresh.java

## Purpose

`TestRouterMountTableCacheRefresh.java` verifies that enabling `MountTableRefresherService` propagates mount-table cache updates to all running routers after add, remove, update, explicit refresh, router stop, timeout, and cached client expiration scenarios. It runs each parameterized case with router heartbeats using IP addresses and host names. The source was read as a complete 429-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `TestingServer`, `MiniRouterDFSCluster`, `RouterContext`, `RouterStore`, `MountTableManager`, `MountTableRefresherService`, `MountTableRefresherThread`, `RouterClient`, `STATE.STARTED`, and mount-table add/remove/update/refresh requests. Parameter data is `true` and `false` for `DFS_ROUTER_HEARTBEAT_WITH_IP_ENABLE`. Helpers include `initTestRouterMountTableCacheRefresh`, `destroy`, `clearEntries`, `getRouters`, `getNumMountTableEntries`, `getMountTableEntry`, `addMountTableEntry`, and `getMountTableEntries`.

## Control Flow

Initialization starts an embedded ZooKeeper server, a two-namespace MiniRouterDFSCluster with refresh-cache/admin/RPC/heartbeat support, ZooKeeper-backed federation store, and router store enabled. It waits for routers to register. Add/remove/update tests mutate the mount table through one router and read mount table entries from every started router's admin client. The stopped-router test populates caches, stops a non-primary router, adds another entry, and asserts remaining routers refresh. The explicit API test calls `refreshMountTableEntries`. Timeout and client-expiration tests subclass `MountTableRefresherService` to inject slow local work or count RouterClient creation/closure, then assert refresh timeout and cache eviction behavior.

## State and Persistence Behavior

Mount-table records and router registrations persist in the ZooKeeper-backed state store. RouterClient connections are cached inside `MountTableRefresherService` and expire according to `MOUNT_TABLE_CACHE_UPDATE_CLIENT_MAX_TIME`. The test destroys the cluster and ZooKeeper server after each parameterized invocation and removes mount entries in cleanup.

## Dependencies and Integration Points

This suite integrates Router admin APIs, router state registration, mount-table refresh RPCs between routers, ZooKeeper state-store driver, heartbeat address selection, timeout configuration, and cached RouterClient lifecycle.

## Risks and Edge Cases

The initialization guard reuses static state within a parameter but teardown resets it; ordering matters. Timeout coverage depends on `@Timeout(100)` and a configured 5-second refresh timeout. Cache eviction waits up to three times the configured client lifetime. A stopped router must not prevent updates from reaching started routers.

## Test Signals

Signals include all running routers seeing added/updated/removed entries, successful explicit refresh response, no hang when a refresher sleeps for one minute, and equality of RouterClient create and close counters after cache expiration.
