# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsStore.java

Purpose: thread-safe in-memory aggregation store for worker and client metrics reported to the metrics master. It maps selected instance metrics to cluster counters and supports clearing/resetting metric state.

Important APIs/types/functions: `putWorkerMetrics`, `putClientMetrics`, `initMetricKeys`, `clear`, `getLastClearTime`, `incrementUfsRelatedCounters`, and nested `ClusterCounterKey`. `ClusterCounterKey` combines `MetricsSystem.InstanceType` and metric name for the counter lookup map.

Control flow: worker/client heartbeats enter through `put*Metrics`; empty or null-source batches are ignored. `putReportedMetrics` walks reported metrics and only processes `MetricType.COUNTER`. Known counters are incremented by delta value; unknown client counters are ignored; worker UFS read/write counters are expanded into per-UFS and aggregate cluster counters. `initMetricKeys` pre-registers the counter mappings and cache-hit-rate gauge.

State and persistence: state is in `mClusterCounters` and `mLastClearTime`, protected by a read/write lock. Report ingestion uses the read lock while `clear` takes the write lock, decrements all cluster counters to zero, updates clear time from the injected `Clock`, and calls `MetricsSystem.resetAllMetrics`. There is no journal persistence.

Dependencies/integration: depends on Dropwizard `Counter`, Alluxio `MetricsSystem`, `MetricKey`, `MetricInfo` tags, and `LockResource`. It receives worker/client data via `DefaultMetricsMaster` and affects cluster metrics exported through sinks and RPCs.

Risks: UFS-specific metrics assume the aggregate all-UFS counter was initialized before ingest, otherwise `mClusterCounters.get(...).inc` can null-dereference. Counter values are cast from double to long. `clear` resets the global metrics system, so callers must coordinate it with updater/sink lifecycle as the class comment warns.

Test signals: `MetricsStoreTest` should cover initialization, counter deltas, client-vs-worker behavior, UFS per-tag aggregation, clear-time updates, and reset behavior. Additional useful cases include missing UFS tags, ingest before `initMetricKeys`, concurrent put/clear, and non-counter metric filtering.
