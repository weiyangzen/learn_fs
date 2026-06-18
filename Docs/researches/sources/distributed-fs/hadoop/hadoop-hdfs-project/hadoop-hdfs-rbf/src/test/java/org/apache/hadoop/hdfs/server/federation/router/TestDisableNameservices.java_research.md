# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDisableNameservices.java

## Purpose
`TestDisableNameservices` verifies router behavior when a nameservice is administratively disabled. It checks request skipping, directory listing output, and metrics state reporting.

## Important APIs, Types, and Functions
The class uses `StateStoreDFSCluster`, `RouterConfigBuilder().stateStore().metrics().admin().rpc()`, `RouterClient`, `NameserviceManager.disableNameservice()`, `DisabledNameserviceStore`, `MembershipNamenodeResolver.loadCache()`, `MountTableManager.addMountTableEntry()`, `MountTableResolver.loadCache()`, router `ClientProtocol`, and `RBFMetrics.getNameservices()`.

## Control Flow
Class setup starts a two-nameservice state-store cluster with independent datanodes, reduced router handler/client threads, router admin/RPC/metrics enabled, and a simulated slow NameNode for ns0. `setupNamespace()` creates mount entries `/dirns0` and `/dirns1`, refreshes the mount-table resolver, and creates directories in each namespace plus a root-level directory in ns0. `testWithoutDisabling()` verifies `renewLease()` waits more than one second because ns0 is slow and root listing includes ns0 and ns1 content. `testDisabling()` disables ns0, reloads disabled-nameservice and membership caches, verifies `renewLease()` completes quickly, and root/listing output excludes ns0-backed content where appropriate. `testMetrics()` parses nameservice metrics and expects ns0 to report `DISABLED` while ns1 remains `ACTIVE`. After each test, disabled nameservices are re-enabled in the store.

## State and Persistence
Disabled nameservice state is stored in `DisabledNameserviceStore`; mount table and membership data are in the router state store; filesystem directories live in the mini DFS cluster. Cleanup restores disabled namespace records.

## Dependencies and Integration Points
The test integrates admin APIs, router RPC fan-out, state-store-backed disabled namespace filtering, mount table resolution, mini DFS NameNodes, slow NameNode simulation, and metrics JSON.

## Risks and Test Signals
Timing assertions depend on the slow NameNode simulation and local scheduling. Directory ordering assertions assume stable listing order. Passing tests signal that disabled nameservices are skipped for fan-out operations, removed from resolver-visible active sets, and surfaced as `DISABLED` in metrics.
