# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterListOpenFiles.java

## Purpose

`TestRouterListOpenFiles.java` verifies Router handling of `listOpenFiles` for single- and multi-destination mount points in both synchronous and asynchronous router RPC modes. It checks path rewriting, duplicate open-file de-duplication, and batched iteration across namespaces with overlapping inode ID ranges. The source was read as a complete 263-line parameterized JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `StateStoreDFSCluster`, `MultipleDestinationMountTableResolver`, `RouterClientProtocol`, `DFSClient`, `OpenFileEntry`, `OpenFilesIterator.OpenFilesType`, `BatchedRemoteIterator.BatchedEntries`, `RemoteIterator`, `DestinationOrder.HASH_ALL`, `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`, and `AsyncUtil.syncReturn`. Key methods are constructor/setup, `resetInodeId`, `cleanupNamespaces`, `testSingleDestination`, `testMultipleDestinations`, `testMultipleDestinationsMultipleBatches`, `runBatchListOpenFilesTest`, and `createMountTableEntry`.

## Control Flow

The parameterized class runs with `useAsync=true` and `false`. Setup starts a two-namespace state-store cluster with heartbeat/admin/RPC, monitor-namenode settings, mount-table cache update, and a small open-files response batch size. Each test resets both namespaces' inode generators, creates matching destination directories, adds a source mount, opens files directly on namespace clients, then calls router protocol or router client `listOpenFiles`. Async calls retrieve the result through `syncReturn`.

## State and Persistence Behavior

Mount-table records are added through the router admin client and router state-store caches are refreshed. Open file state is maintained by namespace `DFSClient` streams until each stream is closed. Namespaces are cleaned after each test by deleting `/` on both clients. Inode IDs are explicitly reset to create duplicate and ordered-batch scenarios.

## Dependencies and Integration Points

This test integrates router client protocol modules, async RPC bridging, mount-table path translation, open-file batched iterators, namenode inode IDs, and multi-destination resolver de-duplication.

## Risks and Edge Cases

It depends on deterministic ordering of open-file results for some assertions. Duplicate file names across namespaces should collapse to one logical entry, while different names should both appear. Batch tests intentionally make one namespace's inode IDs much larger than the other, then reverse the ordering to catch cursor bugs.

## Test Signals

Signals include one result for single-destination mounts, two distinct results for different files across namespaces, one deduplicated result for same-name files, correct rewritten source paths, and complete iteration of `3 * 2 * BATCH_SIZE` entries in both inode ordering directions.
