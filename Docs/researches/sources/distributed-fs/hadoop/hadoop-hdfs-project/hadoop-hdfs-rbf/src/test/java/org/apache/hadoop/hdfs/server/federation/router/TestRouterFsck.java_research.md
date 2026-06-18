# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFsck.java

## Purpose

`TestRouterFsck.java` is an end-to-end test for the Router HTTP `/fsck` endpoint. It creates a two-namespace state-store-backed router cluster, maps two mount points to different namespaces, creates different file counts under each, and verifies federated fsck output for all paths and for a filtered path. The source was read as a complete 218-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `StateStoreDFSCluster`, `MiniRouterDFSCluster.RouterContext`, `RouterConfigBuilder.http`, `MountTableManager`, `MountTableResolver`, `MembershipStore`, `MembershipState`, Apache HTTP client classes, and `EntityUtils`. Helpers are `globalSetUp`, `clearMountTable`, `addMountTable`, and `testFsck`.

## Control Flow

Global setup starts cluster and routers with state-store/admin/RPC/HTTP enabled, captures router filesystem and HTTP address, and reads sorted namenode memberships from the state store. `testFsck` adds `/testdir` on `ns0` and `/testdir2` on `ns1`, creates one file in the first and three in the second, calls `/fsck`, asserts HTTP 200 and output delimiters/counts for both namespaces, then calls `/fsck?path=/testdir` and asserts only the one-file count remains while all active namenodes are still checked.

## State and Persistence Behavior

Mount-table records are persisted through the admin API and cache-loaded in the resolver. Files are created through the router filesystem. `clearMountTable` removes all mount-table records after each test. Membership state is read once from the router's state store for output verification.

## Dependencies and Integration Points

This test bridges Router HTTP server, `FsckServlet`/federated fsck behavior, mount-table resolution, state-store membership records, namenode web addresses, and filesystem mutations through the router.

## Risks and Edge Cases

Assertions depend on textual fsck output and active membership string formatting. The test notes HTTPS is not covered. It validates file counts and active namenode inclusion but not corrupt block reporting, permissions, unhealthy namenodes, or non-OK HTTP paths.

## Test Signals

Signals include HTTP 200 responses, `"Federated FSCK started"` and `"Federated FSCK ended"` markers, expected `Total files` counts, absence of unrelated namespace count for filtered path, and exactly two active namenode checks in output.
