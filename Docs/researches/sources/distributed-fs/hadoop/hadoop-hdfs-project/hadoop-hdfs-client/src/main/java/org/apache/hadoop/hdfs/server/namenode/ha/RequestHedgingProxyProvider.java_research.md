# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RequestHedgingProxyProvider.java

Purpose: `RequestHedgingProxyProvider<T>` sends an initial RPC concurrently to all configured NameNode proxies and uses the first successful response, then sticks to that proxy until failover is requested. It is designed for HA setups where the active should respond while standbys throw `StandbyException`.

Important APIs/types/functions: extends `ConfiguredFailoverProxyProvider`. `getProxy()` builds a wrapper dynamic proxy around `RequestHedgingInvocationHandler`. The handler maintains `targetProxies` and volatile `currentUsedProxy`. It captures Hadoop RPC call ID/retry/external-handler context before submitting worker calls and restores/clears call state in the parent thread. `performFailover()` records the currently used proxy in `toIgnore` and rebuilds the handler on the next `getProxy()`.

Control flow: first invocation double-checks `currentUsedProxy`. If more than one target remains, it creates a fixed thread pool, submits one callable per target, and returns the first successful result from `CompletionService`. Failed results are unwrapped and collected; one failure is rethrown directly and multiple failures are wrapped in `MultiException`. Subsequent invocations call only `currentUsedProxy`. With one target, it invokes directly without a thread pool. `toIgnore` removes the previously active proxy after failover.

State and persistence behavior: maintains an in-memory wrapper `currentUsedHandler`, volatile `toIgnore`, and per-handler active proxy. No durable state. Each first hedged invocation creates and shuts down an executor.

Dependencies and integration points: integrates with Hadoop RPC `Client` call identity, `RPC.getConnectionIdForProxy`, `RemoteException`, `StandbyException`, and `MultiException`. It relies on configured socket timeouts because concurrent calls can otherwise block.

Risks and test signals: mutating `targetProxies.remove(toIgnore)` alters the handler's map and can leave no valid proxies after repeated failovers. `performFailover()` assumes a current handler/proxy exists. Hedged calls amplify load and require correct call ID propagation. Tests should cover first-success selection, all-standby failures, single-target optimization, failover ignore behavior, no-target error, connection ID before and after selection, and executor shutdown on exceptions.
