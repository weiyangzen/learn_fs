# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/ttl/gauge.go

This file wraps Prometheus `GaugeVec` with label-value TTL tracking. `NewGaugeVecWithTTL` creates an underlying gauge vector, records label names and TTL, initializes a map from label/value pairs to expiration times, and launches `cleanUpExpired` in a goroutine. Cleanup runs every `defaultCleanUpPeriod`, deletes expired label values from the underlying gauge, and removes map entries.

`WithLabelValues` returns a `GaugeWithTTL` wrapper containing the label values and underlying gauge. `Set` updates the expiration deadline under lock and sets the gauge value. Label identity is represented by joined label names and joined label values.

State is in-memory metric data plus the TTL map and cleanup goroutine. Integration points include cache, daemon RSS, and filesystem metrics that should age out stale labels. Risks include one cleanup goroutine per gauge vector, no stop mechanism, joined label values colliding if values contain commas, cleanup assuming one label value in `DeleteLabelValues(k.value)`, and package-level cleanup period mutation in tests. Tests cover basic expiry behavior for one-label gauges.
