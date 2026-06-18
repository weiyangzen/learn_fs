# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAdmin.java

## Purpose

`TestRouterAdmin` tests the programmatic Router admin protocol through `RouterClient`, `MountTableManager`, `NameserviceManager`, and `RouterAdminServer`. It focuses on state-store mutations for mount-table and disabled-nameservice records plus permission checks around nameservice management.

## Important APIs, types, and functions

The class uses `StateStoreDFSCluster`, `RouterContext`, `StateStoreService`, `MountTable`, `MountTableManager`, `NameserviceManager`, `RouterClient`, request/response protocol records, `DisabledNameserviceStoreImpl`, `MountTableStoreImpl`, and `ActiveNamenodeResolver`. `setUpMocks()` uses Mockito spies and reflection to replace the Router RPC server and RPC client so destination validation can return controlled `HdfsFileStatus` maps.

## Control flow

`globalSetUp()` starts a state-store-backed Router with admin and RPC enabled, registers two active nameservices, refreshes caches, and installs mocks. `testSetup()` synchronizes mock mount-table records into the state store before each test and resets the admin client.

Mount-table tests add entries, reject duplicates, preserve read-only and destination order flags, remove entries, update destinations, list all entries, fetch a single entry, and call `RouterAdminServer.verifyFileInDestinations()`. Nameservice tests disable and enable `ns0`, assert disabled set contents, reject unknown nameservices, and exercise authorization by running requests as normal users or kerberos-style superuser principals.

## State and persistence behavior

This suite directly persists and reloads `MountTable` and disabled-nameservice records through the state store. Cache refreshes via `stateStore.loadCache()` are explicit and part of the test contract. Mocked RPC destination checks isolate admin validation from real HDFS paths.

## Dependencies and integration points

It integrates the Router admin RPC server, state-store protocol records, mount-table resolver persistence, disabled nameservice store, active namenode resolver registration, and Hadoop `UserGroupInformation` authorization.

## Risks and test signals

The reflection-based RPC server replacement is brittle if Router internals change. The tests are strong at catching admin protocol and state-store regressions, but they do not exercise the CLI parsing layer; that is covered by `TestRouterAdminCLI`.
