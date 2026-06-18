# sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/metrics_test.go

Purpose: validates metrics registration/export and individual recorder functions.

Important fixtures/APIs: `mockExporter`, `resetMetricsForTest`, `Register`, `Export`, and all metric recorder functions.

Control flow and state: tests reset global registry, exporter, `sync.Once`, and counter vectors. They verify only the first exporter is registered, `Export` invokes it once, nil exporter is tolerated, and counters are updated with expected label values.

Dependencies and integration points: Prometheus `testutil.ToFloat64`, sync.Once, time-based duration calculations, and testify require.

Risks and test signals: tests prove global reset is needed for deterministic unit tests. They do not assert registry text output or high-cardinality behavior.
