<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/metrics.rs -->
## sources/cloud-native/nydus/utils/src/metrics.rs

### Purpose
This module centralizes Nydus runtime metrics for error events, storage backends, blob cache activity, and RAFS filesystem IO. It provides globally registered metric sets addressable by filesystem or backend id, plus atomic counters and JSON export helpers used by the HTTP metrics surface.

### APIs, Types, and Control Flow
Important public types are `StatsFop`, `InodeStatsCounter`, `InodeIoStats`, `AccessPattern`, `FsIoStats`, `FopRecorder`, `Metric`, `BasicMetric`, `BackendMetrics`, and `BlobcacheMetrics`. `FsIoStats::new()` registers an `Arc<FsIoStats>` in `FS_METRICS`, initializes default switches, and records global operation totals through `fop_update()`. Per-file accounting is enabled by toggles and initialized through `new_file_counter()`. `FopRecorder` is an RAII guard: `settle()` starts a failed operation by default, `mark_success()` records success and byte size, and `Drop` performs the final metrics update.

### State, Dependencies, and Integration
Global registries are `RwLock<HashMap<String, Arc<_>>>` values for filesystem, backend, and blobcache counters. Most numeric fields use relaxed `AtomicU64` counters through `BasicMetric`; mutable maps use `RwLock`; blobcache underlying file names use `Mutex<HashSet<String>>`. Export functions serialize with `serde_json` and return `nydus_api::http::MetricsError`. Integration points include `crate::logger::ErrorHolder`, `crate::InodeBitmap`, RAFS FUSE/virtiofs FOP accounting, backend read paths, and blobcache prefetch/cache-hit tracking.

### Risks and Test Signals
Counters are approximate under relaxed atomics, which is acceptable for metrics but not for sequencing. `AccessPattern::record_access_time()` uses a load-then-store race, so concurrent first reads can overwrite each other. `FopRecorder` counts failures if not marked successful, so early returns are handled but forgotten `mark_success()` calls skew results. Tests cover size and latency bucket selection, per-inode updates, access pattern idempotency, global export ambiguity with multiple ids, blobcache/backend lifecycle, duration saturation, and failure recording.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/metrics.rs -->
