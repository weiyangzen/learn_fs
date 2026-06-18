# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableWithoutDefaultNS.java

## Purpose

`TestRouterMountTableWithoutDefaultNS.java` verifies Router behavior when default nameservice fallback is disabled. It checks synthetic ancestor metadata for submounts, failure for paths with no location or submount, recursive content summary over nested mount points, all-location discovery, and content-summary location selection. The source was read as a complete 268-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `StateStoreDFSCluster`, `RouterContext`, `MountTableResolver`, `RouterClientProtocol`, `RouterRpcServer`, `RemoteLocation`, `RouterResolveException`, `NoLocationException`, `ContentSummary`, and mount-table admin protocols. Helpers are `globalSetUp`, `clearMountTable`, `addMountTable`, and `writeData`.

## Control Flow

Global setup starts a two-namespace state-store/admin/RPC router cluster with `DFS_ROUTER_DEFAULT_NAMESERVICE_ENABLE=false`. Tests add mount entries and force resolver cache reload. `testGetFileInfoWithSubMountPoint` asserts `/testdir` returns synthetic directory info when `/testdir/1` is mounted. `testGetFileInfoWithoutSubMountPoint` expects `RouterResolveException` for unrelated `/testdir2`. Content-summary tests write data directly to namespace filesystems and request summaries at ancestor paths. Location tests check `getAllLocations` and `getLocationsForContentSummary` over nested mount hierarchies and expect `NoLocationException` for unrelated roots.

## State and Persistence Behavior

Mount entries persist through the state store and are cleared after each test. File data is created directly in namespace filesystems and deleted in `finally` blocks. Default namespace fallback remains disabled for the class lifetime.

## Dependencies and Integration Points

This suite targets Router path resolution without fallback, synthetic mount ancestors, recursive content-summary aggregation, nested mount-table traversal, and direct router RPC protocol helper methods.

## Risks and Edge Cases

The test creates a mount with nameservice `ns2` in `testGetAllLocations` even though the cluster has two namespaces; this is acceptable for resolver map traversal but would be unsafe for live filesystem operations. `writeData` writes one byte per loop iteration, making large file creation slower but deterministic. No-default namespace behavior must distinguish ancestor-with-submount from unrelated missing path.

## Test Signals

Signals are non-null synthetic `HdfsFileStatus` for ancestors, `RouterResolveException`/`NoLocationException` for unrelated paths, exact content summary file counts and lengths, and expected remote destination paths for nested content-summary locations.
