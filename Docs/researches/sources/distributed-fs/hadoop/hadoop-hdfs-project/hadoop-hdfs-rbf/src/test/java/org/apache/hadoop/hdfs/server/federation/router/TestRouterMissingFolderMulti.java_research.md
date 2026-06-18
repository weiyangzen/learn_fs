# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMissingFolderMulti.java

## Purpose

`TestRouterMissingFolderMulti.java` validates Router listing and content-summary behavior for a multi-destination `HASH_ALL` mount when folders exist everywhere, nowhere, or in only one subcluster. The source was read as a complete 182-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `MockNamenode`, `Router`, `MultipleDestinationMountTableResolver`, `MembershipNamenodeResolver`, `DestinationOrder.HASH_ALL`, `FileSystem`, `ContentSummary`, and federation helpers `createMountTableEntry`, `getFileSystem`, and `registerSubclusters`. Test methods are `testSuccess`, `testFileNotFound`, and `testOneMissing`.

## Control Flow

Setup creates active mock namenodes `ns0` and `ns1`, starts a router with state-store/admin/RPC and partial listing disabled, configures membership and file resolvers, and registers subclusters. `testSuccess` writes ten files through the router and expects listing and content summary counts to match. `testFileNotFound` creates only the mount and expects `FileNotFoundException` for listing and content summary under a missing child path. `testOneMissing` writes files directly to only `ns0`, then accesses through the router and expects successful listing/summary rather than failure from the missing `ns1` folder.

## State and Persistence Behavior

State is held in mock namenode filesystems and router mount-table/resolver caches. All mocks and the router are stopped after each test. There is no durable persistence beyond the in-memory state store.

## Dependencies and Integration Points

The test targets multi-destination resolver behavior, partial-list policy, router filesystem list/status aggregation, and content-summary aggregation across mock namenodes.

## Risks and Edge Cases

The core edge case is distinguishing all destinations missing from one destination missing. The test forces `DFS_ROUTER_ALLOW_PARTIAL_LIST=false` but still expects one-missing success for existing data, so changes to missing-location semantics can break it. It does not cover more than two destinations or stale cache updates.

## Test Signals

Signals are exact file counts for success, `FileNotFoundException` when no subcluster has the path, and successful ten-entry listing plus ten item summary when only one namespace contains the folder.
