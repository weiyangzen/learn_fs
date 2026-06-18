# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCMBean.java

Purpose: JMX interface for Router RPC server/client activity.

Important APIs and types: exposes proxy/processing operation counts and averages, active/observer proxy counts, failure counters, retry counters, Router failure counters, RPC server queue/connections, RPC client connection-pool stats, JSON connection details, per-namespace available handlers, async caller pool JSON, and permit rejection/acceptance metrics.

Control flow: no implementation.

State and persistence: no state in the interface. Implementations read mutable metrics counters and live RPC server/client state.

Dependencies and integration points: implemented by `FederationRPCMetrics` and registered by `FederationRPCPerformanceMonitor` as a StandardMBean.

Risks: values mix counters, gauges, averages, and JSON strings, so clients must interpret each correctly. Tests should assert getter values after simulated monitor events and verify JSON-producing methods tolerate missing RPC client internals.
