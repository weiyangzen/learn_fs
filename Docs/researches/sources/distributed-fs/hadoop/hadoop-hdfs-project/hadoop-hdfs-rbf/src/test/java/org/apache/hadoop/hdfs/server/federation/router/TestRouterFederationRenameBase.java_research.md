# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenameBase.java

## Purpose

`TestRouterFederationRenameBase.java` is the shared fixture for router federation rename tests. It creates a two-subcluster, six-datanode-per-subcluster federated mini-cluster, enables the rename feature, configures permissions/group mapping, optionally enables async RPC, and provides helpers for per-test path setup. The source was read as a complete 217-line Java fixture.

## Important APIs, Types, and Functions

Important APIs include `MiniRouterDFSCluster`, `RouterConfigBuilder.routerRenameOption`, `DistCpProcedure.enableForTest`, `DFS_ROUTER_FEDERATION_RENAME_MAP`, `DFS_ROUTER_FEDERATION_RENAME_BANDWIDTH`, `SCHEDULER_JOURNAL_URI`, `RouterAsyncRpcFairnessPolicyController`, and `MockResolver`. Key methods are `globalSetUp(boolean enableAsyncRpc)`, `tearDown`, `setup`, `setRouter`, `setNs`, `setNamenode`, `getRouterFileSystem`, `createDir`, `getCluster`, and `getRouterContext`.

## Control Flow

`globalSetUp` configures namenodes with caller context and the mock group mapping, starts the federated HDFS cluster, creates a DistCp journal under the second namenode, configures routers with metrics/RPC/admin/rename options, starts routers, registers namenodes, lowers datanode heartbeat expiry for faster tests, and enables `DistCpProcedure` test mode. `setup` installs mock locations, deletes old files, creates test directories, picks a random router and a nameservice, installs a special `/same` mapping with two destinations in the same namespace, and creates a random test file on the selected namenode.

## State and Persistence Behavior

The static `cluster` owns all mini-cluster state for subclasses. Instance fields cache the current router context, selected nameservice, router filesystem, namenode filesystem, and created namenode file. Router rename state includes the scheduler journal URI and feature configuration. `tearDown` shuts down the cluster and disables DistCp test mode.

## Dependencies and Integration Points

This base integrates MiniRouterDFSCluster, HDFS permission checking, group mapping, router fairness policy selection, router rename configuration, DistCp scheduler state, mock resolver locations, and datanode heartbeat configuration. Subclasses rely on its generated federated paths and file helpers.

## Risks and Edge Cases

The fixture uses a static cluster shared by subclass test methods, so cleanup in `setup` and `tearDown` is critical. The `/same` multi-destination mapping is deliberately unusual and tests must not assume one-to-one mount resolution. Async mode changes router fairness controller and handler count; code paths must remain behaviorally equivalent.

## Test Signals

Useful signals are successful router/namenode registration, available router and namenode filesystems, a created random file on the selected namespace, functioning mock `/same` locations, and successful cluster shutdown with DistCp test mode disabled.
