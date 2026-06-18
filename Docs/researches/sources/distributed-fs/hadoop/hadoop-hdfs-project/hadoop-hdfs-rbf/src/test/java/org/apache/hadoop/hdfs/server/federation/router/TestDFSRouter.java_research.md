# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDFSRouter.java

## Purpose
This test validates default `DFSRouter` configuration values and cleanup of stale namespace state-id context entries when a nameservice is disabled/expired.

## Important APIs, Types, and Functions
It uses `DFSRouter.getConfiguration()`, FedBalance config keys `SCHEDULER_JOURNAL_URI` and `WORK_THREAD_NUM`, `Router`, `RouterRpcServer`, `RouterStateIdContext`, `MockResolver`, `createNamenodeReport()`, and `FEDERATION_STORE_MEMBERSHIP_EXPIRATION_MS`.

## Control Flow
`testDefaultConfigs()` asserts the scheduler journal URI defaults to `hdfs://localhost:8020/tmp/procedure` and worker threads default to 10. `testClearStaleNamespacesInRouterStateIdContext()` configures a router with mock active/file resolvers, short membership expiration, and safemode disabled; registers two active namespaces; touches both namespace state ids; disables one namespace; verifies the map remains size 2 before router start; starts the router and waits; then asserts the state-id map shrinks to one.

## State and Persistence
State is router configuration, `MockResolver` namespace registrations/disabled set, and the in-memory `RouterStateIdContext` namespace id map. No external persistence is used.

## Dependencies and Integration Points
The test integrates `DFSRouter` defaults, router initialization/startup, mock resolvers, membership expiration config, and the periodic stale namespace cleanup in router RPC state-id tracking.

## Risks and Test Signals
The stale cleanup test uses `Thread.sleep(3000)` around a two-second expiration, so it is timing-sensitive. Passing tests signal expected command-line router defaults and that starting the router activates background cleanup of disabled namespace state ids.
