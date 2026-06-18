# sources/cloud-native/nydus-snapshotter/config/default.go

Purpose: populate default snapshotter configuration.

Flow: `FillUpWithDefaults` sets version, root, socket address, daemon mode, system controller address, logging level/rotation, daemon config path/recover policy/fs driver/log rotation/failover, cache GC period, metrics intervals, and then resolves nydusd/nydus-image paths. `SetupNydusBinaryPaths` uses `exec.LookPath`.

State/dependencies: reads PATH for binary discovery; no writes.

Integration points: called by main and embedded containerd plugin initialization before validation/merge.

Risks/tests: missing binaries are silently left empty for later config/launch handling. Defaults can override zero values during mergo merge, so explicit zero settings need care.
