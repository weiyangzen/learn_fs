# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NameserviceRPCMBean.java

Purpose: JMX interface for per-nameservice Router RPC proxy metrics.

Important APIs and types: exposes proxy operation count/average and counters for communicate failures, standby failures, no-namenode failures, permit rejections, and permit acceptances.

Control flow: no implementation; metrics classes implement these getters.

State and persistence: no interface state.

Dependencies and integration points: implemented by `NameserviceRPCMetrics` and created by `FederationRPCPerformanceMonitor` for each configured namespace and the concurrent namespace.

Risks: per-namespace metrics only exist for nameservices known at monitor initialization. Tests should assert each getter reflects the corresponding counter in `NameserviceRPCMetrics`.
