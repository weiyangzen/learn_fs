# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/TimeSeriesStore.java

Purpose: lightweight in-memory store for metric time series samples keyed by metric name.

Important APIs/types/functions: constructor initializes a `ConcurrentHashMap`; `record(metric, value)` creates or updates a `TimeSeries`; `getTimeSeries()` returns an immutable copy of all stored series.

Control flow: record uses `ConcurrentHashMap.compute` so series creation and sample recording for a metric key occur atomically with respect to other updates to that key. Retrieval snapshots the current values into an immutable list without deep-copying individual `TimeSeries` objects.

State and persistence: all state is in memory under `mTimeSeries`; there is no checkpointing or journal entry. Retention and sample storage details are delegated to `alluxio.metrics.TimeSeries`.

Dependencies/integration: used by metrics master paths that collect and expose historical metrics. Depends only on `TimeSeries`, Guava `ImmutableList`, and JDK concurrent maps.

Risks: returned `TimeSeries` objects may still be mutable depending on that class's implementation, so `getTimeSeries` is only a collection snapshot. Unbounded unique metric names can grow the map indefinitely.

Test signals: `TimeSeriesStoreTest` should exercise first-record creation, repeated record for same key, multiple metric keys, immutable collection behavior, and concurrent recording semantics.
