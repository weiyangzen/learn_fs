## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSystemImpl.java

Purpose: Central metrics service implementation that loads configuration, registers sources/sinks, samples sources on a timer, publishes buffers to sinks, and exposes control/system metrics.

Important APIs/types/functions: Implements `MetricsSystem`, `MetricsSource`, and `MetricsSystemMXBean`. Key methods: `init`, `start`, `stop`, source/sink `register`, callback registration, `sampleMetrics`, `publishMetrics`, `publishMetricsNow`, `configure*`, `getMetrics`, and `shutdown`.

Control flow: `init` increments ref count and starts unless standby. `start` invokes callbacks, loads config, configures sinks/sources/system tags, and schedules a daemon timer. Timer events sample filtered sources into a `MetricsBuffer`, include self metrics, and publish through sink adapters. Stop cancels timer, stops adapters, clears config, and invokes callbacks.

State and persistence: Maintains source/sink maps for active/all instances, callbacks, collector, metrics registry, injected tags, config maps, monitoring flag, timer, period, logical time, MBean name, self-source, and mini-cluster ref count. State is synchronized and in-memory.

Dependencies/integration: Uses `MetricsConfig`, adapters, annotation builder, `DefaultMetricsSystem`, Hadoop `MBeans`, hostname lookup, mutable system stats, filters, and sinks.

Risks/test signals: Lifecycle idempotency, ref-count shutdown, callback exception handling, config errors, period GCD calculation, source/sink re-registration after restart, and immediate publish should be tested. Timer concurrency and self-metrics inclusion are key integration risks.
