# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCPerformanceMonitor.java

Purpose: `RouterRpcMonitor` implementation that records Router RPC processing/proxy timings, per-nameservice metrics, failure counters, and registers the Federation RPC JMX bean.

Important APIs and types: thread locals `START_TIME` and `PROXY_TIME`; fields for `Configuration`, `RouterRpcServer`, `StateStoreService`, `FederationRPCMetrics`, per-nameservice `NameserviceRPCMetrics`, JMX `ObjectName`, and executor; methods `init`, `close`, `resetPerfCounters`, `startOp`, `proxyOp`, `proxyOpComplete`, failure callbacks, permit callbacks, and `getRPCMetrics`.

Control flow: `init` creates global metrics, creates nameservice metrics for all configured namespaces plus `"concurrent"`, creates a one-thread executor, and registers a `FederationRPCMBean`. `startOp` records receive time; `proxyOp` records proxy-start time and adds processing time; `proxyOpComplete` records proxy latency on success, excluding concurrent namespace from global proxy metrics but including matching per-namespace metrics. Failure callbacks increment global and, where available, per-namespace counters.

State and persistence: metrics and thread-local timestamps are in-memory only. JMX registration lives until `close` or reset. The executor currently exists for stats logging capacity but is not used by the shown code.

Dependencies and integration points: consumed by Router RPC server instrumentation. It integrates with `FederationRPCMetrics`, `NameserviceRPCMetrics`, `DefaultMetricsSystem`, MBeans, configured nameservices, and Router RPC monitor callbacks.

Risks: thread locals must be set in the correct order; missing `startOp` or `proxyOp` yields skipped latency. Dynamic nameservices created after init are not in the per-namespace map. `close` unregisters only the MBean and shuts down executor; nameservice metrics are not explicitly unregistered here. Tests should verify timing callbacks, concurrent namespace treatment, reset behavior, JMX registration, and failures for unknown namespaces.
