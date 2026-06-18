# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAllResolver.java

## Purpose

`TestRouterAllResolver` verifies multiple-destination mount-table behavior for destination orders that write directories to all namespaces and distribute files across namespaces. It covers `HASH_ALL`, `RANDOM`, and `SPACE` mount points through real filesystem operations.

## Important APIs, types, and functions

The suite uses `StateStoreDFSCluster`, `MultipleDestinationMountTableResolver`, `RouterContext`, `FileSystem`, `DistributedFileSystem`, `MountTableManager`, `MountTable`, `DestinationOrder`, state-store add/get mount-table protocol records, and `TestFileTruncate.checkBlockRecovery()`. Helpers include `testAll()`, `assertDirsEverywhere()`, `assertFilesDistributed()`, `createTestFile()`, `appendTestFile()`, `listRecursive()`, and `createMountTableEntry()`.

## Control flow

`setup()` starts a two-namespace non-HA cluster with Router admin and RPC, registers namenodes, creates three mount entries pointing each namespace to the same mount path, and opens Router and namespace filesystems. `testHashAll()`, `testRandomAll()`, and `testSpaceAll()` all call `testAll(path)`.

`testAll()` creates a directory tree and asserts every directory exists in every namespace. It creates files at multiple depths and asserts the federated view sees all files while namespace views split files across subclusters. It then tests append, truncate with block recovery, subtree delete, and final cleanup deletion, checking directory replication and file distribution after each phase.

## State and persistence behavior

Mount-table entries are persisted in the state store and caches are explicitly refreshed. Files and directories are real HDFS mini-cluster data. The expected invariant is directory fanout to all destinations and file placement according to resolver policy.

## Dependencies and integration points

This is an end-to-end integration point for mount-table state, multiple-destination resolution, Router filesystem operations, append/truncate/delete semantics, and namespace-level filesystem consistency.

## Risks and test signals

The distribution assertion only requires each namespace to receive at least one file when files exist; it does not require exact balance. The test is strong at catching operations that fail to propagate directories or delete consistently across namespaces.
