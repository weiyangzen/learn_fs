# sources/cloud-native/soci-snapshotter/integration/metrics_test.go

Purpose: validates metrics endpoint exposure and key snapshotter metrics for overlay fallback, FUSE failures/counts, background fetch, and local mount failures.

Important APIs and flow: `TestMetrics` checks TCP and Unix metrics endpoints. `TestOverlayFallbackMetric` compares fallback counts for complete indexes, sparse indexes, corrupted zTOCs, and invalid index strings across content stores. `TestFuseOperationFailureMetrics` builds manipulated but deserializable zTOCs to trigger FUSE file-read/failure metrics. `TestFuseOperationCountMetrics` confirms FUSE operation metrics appear after the configured wait duration, not immediately. `TestBackgroundFetchMetrics` checks background queue and span-fetch metrics after a pull/run. `buildIndexByManipulatingZtocData` rewrites zTOC metadata, injects new zTOCs and a new index into content store, and returns the new digest.

State and persistence: mutates content-store blobs, starts snapshotter with metrics configs, runs containers to trigger FUSE paths, and scrapes Prometheus-format metrics.

Dependencies and integration: uses config metrics options, SOCI/store helpers, zTOC marshal/unmarshal, content injection utilities, curl, and common metric-name constants.

Risks and test signals: strong coverage for operational observability and fallback detection. Timing-sensitive metrics tests rely on sleep/wait durations; corrupted zTOC tests depend on selected metadata producing deterministic FUSE failures.
