## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockWorkerMetricsTest.java

**Purpose:** Verifies worker block metric gauges registered by the block worker metrics layer, especially cache-related counters visible through `MetricsSystem`.

**Important APIs:** Uses metric keys/gauge lookup through the metrics registry and validates cached block metric behavior after manipulating block worker/store state.

**Control flow:** The test constructs or mocks a block worker/store environment, obtains gauges by metric name, triggers cache-relevant state, and reads gauge values directly from the metric registry.

**State and persistence:** No durable persistence. Runtime state is metric registration plus in-memory block/store counters; failures generally indicate stale gauge functions or missing metric registration.

**Dependencies and integration:** Integrates with Codahale metrics, Alluxio `MetricKey`, `MetricsSystem`, and block worker/store metadata. These gauges feed operational monitoring and worker health visibility.

**Risks:** Metrics tests can be order-sensitive because metric registries are process-global. Gauge values must reflect live store state rather than captured snapshots, otherwise monitoring can silently drift.

**Test signals:** Provides a focused regression signal that block worker metrics remain registered and compute expected cache counts.
