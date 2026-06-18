# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/cache.go

This file declares cache-related nydusd metrics as TTL-backed Prometheus gauge vectors labeled by image ref. Metrics cover partial and whole cache hits, total requests, entry count, prefetch data bytes, prefetch request count, worker count, unmerged chunks, cumulative prefetch latency, wall-clock prefetch duration, and buffered backend size.

The definitions have no control flow beyond constructing `ttl.GaugeVec` objects. They are registered by `metrics/registry` and populated by `metrics/collector/cache.go`. TTL behavior means stale image-ref labels are eventually deleted if collectors stop setting them.

State lives inside Prometheus gauge vectors and TTL label maps. Integration points include daemon cache metrics API, metrics server collection, and registry registration. Risks include image-ref label cardinality, metric names becoming part of external monitoring contracts, and the collector's duration calculation needing to match these help strings. There are no direct tests for these definitions; TTL cleanup is tested in `metrics/types/ttl`.
