<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcClient.java

## Purpose
`RouterRpcClient` is the router-to-NameNode RPC engine. It owns connection pooling, reflective protocol invocation, failover/retry behavior, observer-read routing, concurrent fan-out, fairness permits, caller-context propagation, result post-processing, and monitoring hooks used by higher-level router protocols.

## Important APIs, Types, and Functions
The constructor creates a `ConnectionManager`, concurrent-call executor, retry policy, fairness controller, observer-read settings, proxy-user behavior, and active state-id freshness tracking. Connection and health APIs expose counts and JSON for connection pools, executor pool, and fairness permit counters.

Core invocation APIs are `invokeSingle` by namespace, block, block pool, or `RemoteLocationContext`; `invokeSequential`; `invokeAll`; and multiple `invokeConcurrent` overloads returning maps or `RemoteResult` lists. Lower-level helpers include `invokeMethod`, `invoke`, `handlerInvokeException`, `handleInvokeMethodIOException`, `handlerAllNamenodeFail`, `postProcessResult`, `processException`, `processExceptionMsg`, `getCleanException`, `getOrderedNamenodes`, `isObserverReadEligible`, `isNamespaceStateIdFresh`, `acquirePermit`, `releasePermit`, and `refreshFairnessPolicyController`. `ExecutionStatus` packs failover, observer-use, and completion flags.

## Control Flow
For a single namespace call, the client gets the remote UGI, acquires a fairness permit for the namespace, determines whether the reflected method is read-only and observer eligible, orders NameNodes from the resolver, resolves method parameters from `RemoteMethod`, invokes `invokeMethod`, and releases the permit. `invokeMethod` iterates candidate NameNodes, gets/reuses a connection for the current user and RPC address, augments caller context with client IP/port/id/call id/real user, invokes the method reflectively, updates active NameNode state and metrics on success, and handles IO failures by marking failover, observer fallback, unavailable observers, retriable cache rotation, or clean remote exceptions.

Sequential calls iterate `RemoteLocationContext`s in resolver order, localize remote exception messages from destination paths to federated source paths, and stop only when expected result class/value conditions are met. Concurrent calls acquire the global concurrent fairness permit, capture current `Server.Call` and `CallerContext`, create callables per location or per NameNode when standby fan-out is requested, run them with `executorService.invokeAll`, convert futures into `RemoteResult`s including timeout and execution exceptions, then optionally require all responses in `postProcessResult`.

Observer reads are enabled per namespace by XOR-like default/override logic. A read method must carry `@ReadOnly(activeOnly=false)`, the namespace state id must be fresh unless refresh is disabled, and the current call must include a client state id before observers are listed first. Calls to active NameNodes refresh the last-active timestamp.

## State and Persistence Behavior
The client maintains runtime state only: connection pools, executor threads, retry policy, fairness controller, accepted/rejected permit counters, observer-read override set, active state-id refresh accumulators, and monitor references. It persists no durable state. It updates resolver caches for active/unavailable NameNodes and can rotate resolver caches on no-namenode failures. Shutdown closes connection manager, executor, and fairness controller.

## Dependencies and Integration Points
Dependencies include `Router`, `ActiveNamenodeResolver`, `FederationNamenodeContext`, `ConnectionManager`, `ConnectionContext`, `RemoteMethod`, `RemoteLocationContext`, `RemoteResult`, Hadoop IPC `CallerContext`/`Server`, HA exceptions, retry policies, `RouterRpcMonitor`, `RouterClientMetrics`, `RouterRpcFairnessPolicyController`, `RouterStateIdContext`, and HDFS/IPC configuration keys.

## Risks
Reflective invocation makes method signatures and parameter mapping in `RemoteMethod` critical. Connection pooling is per user plus NameNode and may grow with user cardinality. Concurrent calls can overload the fixed executor; overload is surfaced as `StandbyException` so clients may fail over to another router. `invokeAll` returns true if any location succeeds, which is appropriate only for selected operations. `postProcessResult(requireResponse=true)` must distinguish partial success from total failure correctly. Observer reads depend on state-id freshness; stale state can route reads to active NameNodes, while incorrect freshness could expose stale observer data. Exception message rewriting uses string replacement and can mis-map unusual paths. Fairness permits must be released on every path.

## Test Signals
Tests should cover client configuration transformation, executor queue mode and overload handling, connection UGI/proxy-user selection, retry/failover decisions for standby/unavailable/remote exceptions, active NameNode update on failover success, observer-read eligibility and override logic, state-id freshness, sequential expected class/value semantics, exception localization, concurrent timeout and execution-exception results, require-response behavior, standby fan-out location mapping, fairness permit accept/reject counters and release paths, caller-context transfer to worker threads, resolver cache rotation, clean exception reconstruction, and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcClient.java -->
