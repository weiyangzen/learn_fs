# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAdminCLI.java

## Purpose

`TestRouterAdminCLI` is a broad CLI integration suite for `hdfs dfsrouteradmin` behavior. It validates command parsing, output, error messages, state-store effects, permission enforcement, quota operations, safe mode, nameservice control, cache refresh, destination lookup, call queue refresh, dump-state formatting, and batch mount-point addition.

## Important APIs, types, and functions

The test uses `RouterAdmin`, `ToolRunner`, `StateStoreDFSCluster`, `RouterContext`, `RouterClient`, `StateStoreService`, `MountTableManager`, `MountTableResolver`, `MultipleDestinationMountTableResolver`, `MountTable`, `RemoteLocation`, `DestinationOrder`, `RouterQuotaUsage`, `RBFMetrics`, `RouterClientProtocol`, `MockStateStoreDriver`, `MembershipState`, `UserGroupInformation`, `Whitebox`, and Mockito. It captures `System.out` and `System.err` with `ByteArrayOutputStream`.

## Control flow

`globalSetUp()` starts a Router with state store, metrics, admin, RPC, quota, and safemode, registers fake active nameservices, mocks quota calls, and spies the RPC server to avoid real file info checks. Tests then run CLI arrays through `ToolRunner.run(admin, argv)` and reload state-store caches before assertions.

Mount-table coverage includes `-add`, `-addAll`, `-update`, `-rm`, `-ls`, `-ls -d`, normalized trailing slashes, nested mount listing, multiple destinations, destination order variants including `LEADER_FOLLOWER`, read-only, fault-tolerant validation, owner/group/mode defaults and mutations, and permission behavior for owner, group, other, and superuser cases. Quota coverage includes `-setQuota`, `-clrQuota`, storage type quota set/clear, size-string parsing, multi-path clear, and invalid arguments. Safe mode tests cover enter/leave/get, metrics and HA service state, argument validation, and permission checks. Nameservice tests cover enable/disable and disabled-list output. Other commands cover `-refresh`, `-getDestination`, `-refreshCallQueue`, and static `RouterAdmin.dumpStateStore()`.

## State and persistence behavior

The suite persists mount-table, quota, disabled-nameservice, and membership records in the state store and repeatedly forces `MountTableStoreImpl` or `DisabledNameserviceStoreImpl` cache reloads. It also mutates process-global login user and process-global stdout/stderr, restoring them in teardown or finally blocks.

## Dependencies and integration points

This file is the highest-level admin contract for users. It bridges CLI parsing, Router admin RPC, mount-table resolver cache, quota module synchronization, safemode service, metrics, state-store driver serialization, and Hadoop security permissions.

## Risks and test signals

The test is intentionally large and sensitive to exact usage text, output formatting, command aliases, and global login-user state. It catches regressions that lower-level admin tests miss, especially parsing and user-visible errors. The mocked quota and RPC file-info paths mean it validates CLI-to-state-store behavior more than real namenode quota enforcement.
