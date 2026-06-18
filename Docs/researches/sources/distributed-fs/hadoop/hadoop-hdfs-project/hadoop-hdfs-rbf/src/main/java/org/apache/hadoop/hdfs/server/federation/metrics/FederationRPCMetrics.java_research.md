# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCMetrics.java

Purpose: metrics2/JMX implementation for Router RPC activity.

Important APIs and types: annotated `@Metrics(name = "RouterRPCActivity")`; stores `RouterRpcServer`; maintains `MutableRate` metrics for processing/proxy time and `MutableCounterLong` counters for proxy ops, active/observer ops, failures, retries, Router failures, and permit rejection. Static `create` registers with `DefaultMetricsSystem`; `reset` unregisters.

Control flow: increment methods update counters. `addProxyTime` records proxy latency, increments active or observer counters based on `FederationNamenodeServiceState`, then increments total proxy ops. `addProcessingTime` records Router internal processing latency. Gauge getters query live server/client state such as call queue, open connections, connection pools, fairness controller JSON, and async caller pool JSON.

State and persistence: metrics are in-memory process counters/rates registered with metrics2 and JMX. They reset on process restart or explicit reset.

Dependencies and integration points: created by `FederationRPCPerformanceMonitor`, exposed through `FederationRPCMBean`, and depends on `RouterRpcServer`, RPC client internals, and fairness controller metrics.

Risks: gauge getters can throw if `rpcServer`, `getServer()`, `getRPCClient()`, or fairness controller is unavailable. `lastStat().mean()` depends on metrics2 snapshot state. Tests should drive monitor events and verify counters, active/observer split, permit metrics JSON, and registration/unregistration behavior.
