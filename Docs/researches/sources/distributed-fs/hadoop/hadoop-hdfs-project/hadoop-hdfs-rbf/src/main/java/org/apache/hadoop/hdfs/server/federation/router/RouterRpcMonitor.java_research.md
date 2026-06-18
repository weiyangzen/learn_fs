# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcMonitor.java

## Purpose
`RouterRpcMonitor` is the pluggable monitoring interface used by `RouterRpcServer` and `RouterRpcClient` call paths to report router RPC activity, Namenode proxy activity, and router-local failures. It decouples the router core from the concrete metrics implementation, with the default implementation selected by `RBFConfigKeys.DFS_ROUTER_METRICS_CLASS`.

## Important APIs and Types
The interface exposes lifecycle methods `init(Configuration, RouterRpcServer, StateStoreService)` and `close()`, metrics access through `getRPCMetrics()`, operation markers `startOp()`, `proxyOp()`, and `proxyOpComplete(...)`, plus failure counters for standby, communication failure, permit rejection, client overload, not implemented calls, retries, missing Namenodes, State Store failure, safe mode, locked path, and read-only path. `proxyOpComplete` carries `nsId` and `FederationNamenodeServiceState` so metrics can distinguish active, standby, observer, or unavailable target states.

## Control Flow
`RouterRpcServer.checkOperation` calls `startOp()` before operation dispatch and uses router failure methods when safe mode or unsupported operations block a request. Lower-level proxy clients call the `proxyOp*` methods around actual Namenode forwarding. Implementations therefore see both the client-facing operation boundary and per-subcluster proxy attempts.

## State and Persistence
This interface owns no state or persistence directly. Implementations may maintain counters, histograms, or JMX state in `FederationRPCMetrics`, and may use the supplied `StateStoreService` for contextual reporting.

## Dependencies and Integration Points
Primary dependencies are Hadoop `Configuration`, `FederationRPCMetrics`, `StateStoreService`, `RouterRpcServer`, and `FederationNamenodeServiceState`. It is instantiated reflectively by `RouterRpcServer` when router metrics are enabled.

## Risks
Metrics correctness depends on every router path consistently calling the monitor. A custom implementation can impact RPC latency if it blocks in hot methods such as `startOp`, `proxyOp`, or `proxyOpComplete`. Null-monitor handling in callers must be retained because metrics can be disabled.

## Test Signals
Look for tests that enable router metrics and assert proxy success/failure counters, safe mode failures, read-only mount failures, and not-implemented calls. Custom monitor tests should verify `init` receives the router server and state store and that `close` is called during service stop.
