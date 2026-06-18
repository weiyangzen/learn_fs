# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableCacheRefreshSecure.java

## Purpose

`TestRouterMountTableCacheRefreshSecure.java` repeats core mount-table cache propagation checks with security configuration enabled. It ensures add, remove, update, and stopped-router refresh behavior work when Router refresh-cache services, admin RPC, heartbeat, and ZooKeeper-backed state store run in secure mode. The source was read as a complete 342-line JUnit 5 test.

## Important APIs, Types, and Functions

The file uses `SecurityConfUtil.initSecurity`, `TestingServer`, `MiniRouterDFSCluster`, `StateStoreZooKeeperImpl`, `StateStoreDriver`, `RouterStore`, `MountTableManager`, `RouterContext`, `MountTable`, and add/remove/update/get state-store protocols. Key methods are `setUp`, `destory`, `tearDown`, `clearEntries`, `testMountTableEntriesCacheUpdatedAfterAddAPICall`, `testMountTableEntriesCacheUpdatedAfterRemoveAPICall`, `testMountTableEntriesCacheUpdatedAfterUpdateAPICall`, and `testCachedRouterClientBehaviourAfterRouterStoped`.

## Control Flow

Class setup starts embedded ZooKeeper, builds a secure refresh-cache/admin/RPC/heartbeat router configuration, creates a two-namespace MiniRouterDFSCluster with the same security resource, starts cluster and routers, obtains a random router and mount manager, and waits for router registration. Each test mutates a mount-table entry through the manager, iterates all started routers, and verifies their admin views. The stopped-router test stops one non-primary router and verifies a subsequent add reaches all remaining started routers.

## State and Persistence Behavior

Secure cluster and router registration state are class-level static resources. Mount-table records are stored in ZooKeeper and cleared after each test. Router cache refresh state is observed through each router's admin client. Class teardown closes ZooKeeper and shuts down the cluster.

## Dependencies and Integration Points

The test integrates secure Hadoop configuration, ZooKeeper federation store, router registration, mount-table refresh RPCs, and admin APIs. It is the secure counterpart to the non-secure cache refresh test but does not include timeout/client-expiration subtests.

## Risks and Edge Cases

The teardown method name is misspelled `destory` but annotated correctly. Secure setup is heavy and can be sensitive to security resource cleanup. The update test compares some expected values through `updatedMountTable` while iterating routers, so it mainly proves store update plus per-router entry count/source path.

## Test Signals

Signals include every started router reporting exactly one added entry, zero entries after removal, updated destination namespace/path after update, and two entries on remaining routers after one router is stopped and another entry is added.
