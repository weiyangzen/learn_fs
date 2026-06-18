# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/types/types.go

This file defines JSON-facing data contracts shared by the daemon HTTP client, daemon state logic, and metrics collectors. `BuildTimeInfo` captures version metadata. `DaemonState` enumerates `UNKNOWN`, `INIT`, `READY`, `RUNNING`, `DIED`, and `DESTROYED`. `DaemonInfo` exposes helper methods for state and version. `ErrorMessage` models nydusd API errors.

`MountRequest` and `NewMountRequest` define the request body for mounting RAFS instances, always using `fs_type: "rafs"`. `FsMetrics`, `InflightMetrics`, and `CacheMetrics` mirror nydusd metrics JSON and are consumed by metrics collectors and readiness logic. Cache metrics include hit counts, prefetch state, backend buffering, and underlying cache files.

The file has no active control flow beyond trivial helpers, but it is an important integration boundary: field tags must match nydusd's API schema, and slices such as `FopHits`, `FopErrors`, `BlockCountRead`, and `ReadLatencyDist` are indexed by metrics code. Risks include schema drift, missing bounds checks before metrics indexing, and typo propagation in serialized fields. Tests indirectly validate daemon info decoding and some metrics consumers, but the full schema is not round-trip tested.
