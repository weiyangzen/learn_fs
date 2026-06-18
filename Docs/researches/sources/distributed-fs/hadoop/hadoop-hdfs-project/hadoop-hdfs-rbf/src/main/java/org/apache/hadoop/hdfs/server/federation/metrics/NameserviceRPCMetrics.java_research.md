# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NameserviceRPCMetrics.java

Purpose: metrics2 implementation for RPC activity scoped to a single nameservice.

Important APIs and types: annotated `@Metrics(name = "NameserviceRPCActivity")`; constant prefix `NameserviceActivity-`; fields `nsId`, `MetricsRegistry`, `MutableRate proxy`, and counters for proxy ops, failures, permit rejected, and permit accepted. Static `create` registers a metrics source, using a random undefined suffix for empty nameservice names.

Control flow: increment methods update specific counters. `addProxyTime` records proxy latency and increments proxy-op count. Getter methods expose counts and last proxy average. `getNsId` returns the registered prefixed ID.

State and persistence: in-memory metrics source registered with `DefaultMetricsSystem`. State resets when unregistered or process restarts.

Dependencies and integration points: created by `FederationRPCPerformanceMonitor` and exposed through `NameserviceRPCMBean`; used for per-namespace visibility distinct from aggregate `FederationRPCMetrics`.

Risks: empty nameservice IDs create random metric names, which can make tests and dashboards unstable. No reset/unregister method is defined in this class. Tests should verify registration naming, counter increments, proxy average updates, and permit accepted/rejected counters.
