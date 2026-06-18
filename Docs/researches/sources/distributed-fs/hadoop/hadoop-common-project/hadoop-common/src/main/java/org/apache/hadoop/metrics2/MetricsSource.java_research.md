## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSource.java

Purpose: Public source contract for snapshotting metrics into a collector.

Important APIs/types/functions: `getMetrics(MetricsCollector collector, boolean all)` emits records and metrics. `all` requests all metrics instead of only changed values.

Control flow: `MetricsSystemImpl.sampleMetrics` invokes sources through `MetricsSourceAdapter`, which injects tags and catches source exceptions.

State and persistence: Interface only; source objects own their own counters, gauges, and registries.

Dependencies/integration: Sources are registered directly or created from annotations by `MetricsSourceBuilder`.

Risks/test signals: Source exceptions are logged and swallowed by the adapter, so tests should assert system sampling continues after failures.
