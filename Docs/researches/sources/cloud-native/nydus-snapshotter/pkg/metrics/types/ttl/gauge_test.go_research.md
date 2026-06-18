# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/ttl/gauge_test.go

This test file validates TTL gauge cleanup behavior. It shortens `defaultCleanUpPeriod`, creates a one-label gauge with a three-second TTL, sets two label values, collects metrics to confirm both exist, waits, refreshes one label value, verifies both remain in the internal map before cleanup, waits again, and confirms only the refreshed label remains. It then collects metrics and later verifies the map is empty after cleanup.

The test exercises `WithLabelValues`, `Set`, internal expiration tracking, Prometheus collection, and cleanup deletion. It uses sleeps and goroutines, so it is timing-sensitive but covers the intended stale-label lifecycle.

Coverage gaps include multi-label gauge vectors, label values containing commas, cleanup goroutine lifecycle, concurrent `Set` and cleanup under heavier load, and `DeleteLabelValues` correctness with more than one label. The test mutates the package-level cleanup period, which can affect other tests if run in the same process.
