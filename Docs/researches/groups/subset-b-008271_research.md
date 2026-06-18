# subset-b-008271 Research

Grouped code research for the requested RustFS object-capacity and observability files. Each section preserves the source path in its title and is bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/capacity_manager.rs -->
# sources/object-store/rustfs/crates/object-capacity/src/capacity_manager.rs

## Purpose
Implements the hybrid capacity cache used by RustFS capacity reporting. It combines scheduled full scans, write-triggered refreshes, per-disk dirty tracking, and singleflight refresh coordination so capacity queries can avoid repeatedly walking every data directory.

## Important APIs, Types, and Functions
Key configuration helpers expose environment-driven durations and limits such as `get_scheduled_update_interval`, `get_write_trigger_delay`, `get_max_files_threshold`, symlink settings, and dynamic timeout bounds. `CachedCapacityConfig` caches env reads in production and refreshes them in tests. `CachedCapacity`, `CapacityUpdate`, `DiskCapacityUpdate`, and `DataSource` are the core payloads. `HybridStrategyConfig` controls scheduled and write-triggered behavior. `HybridCapacityManager` owns the async cache, write-frequency buckets, dirty disk set, per-disk cache, cache-completeness flag, and `RefreshState`. Public entry points include `get_capacity_manager`, `create_isolated_manager`, `start_background_task`, `update_capacity`, `record_write_operation_with_scope_token`, `needs_fast_update`, `refresh_or_join`, and `spawn_refresh_if_needed`.

## Control Flow
Writes update a rolling 60-second bucket array and may consume a `Uuid` scope token from `capacity_scope`. `needs_fast_update` checks cache freshness, write frequency, and debounce delay. Refreshes are deduplicated: joiners subscribe to a `watch` channel while holding the mutex, while the leader runs the supplied future, catches panics, updates the cache on success, emits metrics, then publishes the result. Background work starts two Tokio tasks, one for scheduled refresh attempts and one for runtime summaries.

## State and Persistence
All state is in memory: an optional global singleton, `RwLock`-protected capacity cache, dirty disk set, per-disk cache, and write buckets. Disk cache completeness is only set after a full per-disk update covers the expected disk count. Dirty disks are cleared after successful scoped updates. No on-disk persistence exists, so restart resets capacity state.

## Dependencies and Integration
Integrates with `scan::refresh_capacity_with_scope`, `capacity_scope` scope registries, `rustfs_config` env constants, `rustfs_utils` env parsing, and `rustfs_io_metrics::capacity_metrics`. It is meant to be called by admin/object-store paths that need cached used-capacity values and by write paths that can propagate dirty disk scope tokens.

## Risks
Production env config is cached once, so runtime env changes are ignored outside tests. Full and scoped refresh correctness depends on stable `(endpoint, drive_path)` keys. If a full scan has partial errors, per-disk cache replacement is suppressed, preventing unsafe subset refresh but also delaying incremental optimization. The global singleton can make tests or embedded runtimes order-sensitive unless isolated managers are used.

## Test Signals
Tests cover env defaults and overrides, cache updates, write frequency windows, future-bucket filtering, fast-update debounce, disabled write triggers, concurrent access, singleflight joiners, background spawn deduplication, dirty scope token handling, global dirty scope draining, per-disk subset total recomputation, and config defaults.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/capacity_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/capacity_scope.rs -->
# sources/object-store/rustfs/crates/object-capacity/src/capacity_scope.rs

## Purpose
Provides temporary disk-scope propagation for capacity refreshes. Storage/write-side code can associate affected disks with a `Uuid` token, and the capacity manager later consumes that token to mark only those disks dirty. It also supports a global dirty scope queue for paths that cannot pass a token directly.

## Important APIs, Types, and Functions
`CapacityScopeDisk` identifies a disk by `endpoint` and `drive_path`. `CapacityScope` is a vector of those disk keys. `record_capacity_scope` stores or merges a scope for a token. `take_capacity_scope` removes and returns a scope if it has not expired. `record_global_dirty_scope` adds disks to a global `HashSet`, and `drain_global_dirty_scopes` atomically drains that set. Internal helpers include TTL pruning, hard-limit eviction by oldest timestamp, and duplicate-aware scope merging.

## Control Flow
The token registry is lazily initialized with `OnceLock<Mutex<HashMap<Uuid, CapacityScopeEntry>>>`. New token records trigger pruning only after the soft limit and enforce the hard limit by evicting oldest entries. Repeated records for the same token merge unique disks and refresh `recorded_at`. Taking a token removes it first, then rejects stale entries older than five minutes.

## State and Persistence
All state is process-local memory. The token registry has a soft limit of 2,048 and hard limit of 4,096 entries; both protect against unbounded leak when write scopes are never consumed. Global dirty scopes are a set, so duplicate disk records collapse.

## Dependencies and Integration
Depends only on std collections/synchronization and `uuid`. It is consumed by `capacity_manager` for scoped dirty tracking and by write paths that can record capacity-impacting disk scopes.

## Risks
TTL is based on `Instant`, so delayed consumers silently lose stale scope and fall back to unscoped behavior. HashSet ordering means drained global dirty scopes are nondeterministic. A poisoned mutex is recovered with `into_inner`, which keeps the service running but may retain partially mutated state.

## Test Signals
Tests cover record/take round trips, one-time token consumption, merging duplicate disks for a token, hard-limit enforcement, poison recovery for both registries, global dirty scope deduplication, and drain semantics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/capacity_scope.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/lib.rs -->
# sources/object-store/rustfs/crates/object-capacity/src/lib.rs

## Purpose
Defines the public module boundary for the `object-capacity` crate. It exposes capacity manager internals, dirty-scope propagation, scan logic, and shared types while keeping the external public re-export surface small.

## Important APIs, Types, and Functions
The crate declares `capacity_manager`, `capacity_scope`, `scan`, and `types` modules. It publicly re-exports `scan_used_capacity_disks` for tooling/benchmarks and `CapacityDiskRef` plus `CapacityScanSummary` for caller-facing scan inputs and outputs.

## Control Flow
There is no runtime control flow in this file. Its behavior is compile-time module wiring and selective re-export.

## State and Persistence
No state is stored here. State lives in `capacity_manager` singletons and scope registries.

## Dependencies and Integration
This file is the integration point external crates use to call the scan API without importing private result types. Making modules public also allows internal RustFS crates to reach manager and scope APIs directly.

## Risks
Because all modules are `pub`, more implementation detail is exposed than the minimal re-exports suggest. Future refactors need to account for downstream users importing module paths directly.

## Test Signals
No tests are defined here; compile-time use by dependent crates and module-level tests in the child modules validate the wiring.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/scan.rs -->
# sources/object-store/rustfs/crates/object-capacity/src/scan.rs

## Purpose
Implements the filesystem scanning path behind capacity refreshes. It computes used bytes and file counts across one or more disk roots, supports exact and sampled estimates, handles partial disk failures, and produces per-disk updates for incremental dirty-disk refreshes.

## Important APIs, Types, and Functions
`scan_used_capacity_disks` is the public summary API. `calculate_data_dir_used_capacity_report` parallelizes per-disk scans and aggregates a `CapacityScanReport`. `select_capacity_refresh_disks` decides whether a manager can refresh only dirty disks. `refresh_capacity_with_scope` converts scan reports into `CapacityUpdate`. Internal structures include `DiskScanOutcome`, `DiskCapacityScanResult`, `SymlinkTracker`, and `ProgressMonitor`.

## Control Flow
Disks are scanned via a futures stream with `buffer_unordered` and a maximum concurrency of four. Each disk scan calls `get_dir_size_async`, which runs a blocking `WalkDir` traversal in `spawn_blocking`. For each regular file, it updates exact prefix bytes until `max_files_threshold`; after that, it samples overflow files by `sample_rate` and estimates total size. Progress checks run every 512 files and can terminate with timeout or stall detection. If sampling data exists when a timeout occurs, the function returns a fallback estimate instead of failing.

## State and Persistence
The scanner itself is stateless across calls. It reads capacity config from `capacity_manager` helpers and returns in-memory scan summaries. Partial traversal or metadata failures are recorded in the result and influence whether per-disk cache updates can be committed.

## Dependencies and Integration
Uses `walkdir`, Tokio blocking tasks, `futures` streams, capacity metrics, and tracing. It integrates with `HybridCapacityManager` by selecting refresh scopes and returning `CapacityUpdate` values with per-disk cache replacement or dirty-disk clearing metadata.

## Risks
Sampling can under- or over-estimate when overflow files differ significantly from sampled files. Symlink tracking records targets but relies on `WalkDir` for actual traversal behavior; path cycles and depth limits deserve operational scrutiny. A dirty subset refresh with partial errors is rejected, so repeated disk-specific failures can keep dirty state uncleared.

## Test Signals
Tests cover empty, single-file, multi-file, nested directory, nonexistent path, partial multi-disk success, full-versus-dirty disk selection based on complete cache state, and Unix symlink inclusion/exclusion under env-controlled follow settings.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/scan.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/types.rs -->
# sources/object-store/rustfs/crates/object-capacity/src/types.rs

## Purpose
Defines shared data structures for capacity scanning. It separates public API summaries from crate-internal scan result details.

## Important APIs, Types, and Functions
`CapacityDiskRef` is the caller-provided disk identity with `endpoint` and `drive_path`. `CapacityScanResult` is crate-private and carries `used_bytes`, `file_count`, `sampled_count`, `is_estimated`, `scan_duration`, and `had_partial_errors`. `with_partial_errors` marks an internal result after aggregation detects failures. `CapacityScanSummary` is the public equivalent used by external tooling. The `From<CapacityScanResult>` implementation maps all fields to the public type.

## Control Flow
No complex control flow exists. The file provides constructors through derived defaults and a single conversion path.

## State and Persistence
All structures are value types with no persistence. `CapacityDiskRef` derives `Hash` and equality traits, enabling use in sets/maps when needed.

## Dependencies and Integration
Only depends on `std::time::Duration`. `scan.rs` creates and converts these values, while `lib.rs` re-exports the public disk reference and summary types.

## Risks
`file_count` and `sampled_count` are `usize`, which is natural in Rust but can be platform-width dependent for serialized or FFI callers if added later. Public `CapacityScanSummary` exposes `Duration`, so JSON or stable wire formats would require another DTO.

## Test Signals
No direct tests are present, but scan tests validate field semantics such as exact byte counts, file counts, estimates, and partial error propagation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/Cargo.toml -->
# sources/object-store/rustfs/crates/obs/Cargo.toml

## Purpose
Declares the `rustfs-obs` crate metadata, features, and dependency graph for RustFS observability. The crate covers logging, metrics, tracing, runtime telemetry, profiling, and log cleanup.

## Important APIs, Types, and Functions
This TOML file has no Rust APIs, but it controls feature-gated availability. Default features are empty. `gpu` enables `nvml-wrapper`; `pyroscope` enables `jemalloc_pprof` and `pyroscope`. Platform-specific pyroscope dependencies are limited to macOS and Linux GNU x86_64.

## Control Flow
Cargo resolves workspace-shared dependencies and optional features. Tokio is enabled with runtime, sync, fs, time, and macros for library code, while dev-dependencies use full Tokio for examples/tests.

## State and Persistence
No runtime state. It influences build artifacts and dependency inclusion.

## Dependencies and Integration
Internal RustFS dependencies include audit, common, config, ecstore, iam, io-metrics, notify, security-governance, storage-api, and utils. External dependencies include OpenTelemetry, tracing, tracing-subscriber, tracing-appender, metrics, compression crates (`flate2`, `zstd`), sysinfo, crossbeam, glob, serde, and dial9 Tokio telemetry.

## Risks
The crate is broad and can pull substantial dependency weight when optional features are enabled. Feature compatibility across platform-specific profiling dependencies needs CI coverage. Workspace dependency versions must remain compatible across telemetry and metrics crates.

## Test Signals
`tempfile` and `temp-env` support filesystem and environment tests. The examples under `examples/` exercise configuration and dial9 integration paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/config.toml -->
# sources/object-store/rustfs/crates/obs/examples/config.toml

## Purpose
Provides an example observability configuration table for local use. It documents typical OTLP endpoint, stdout, sampling, metrics interval, service identity, environment, logger level, and local logging toggles.

## Important APIs, Types, and Functions
No executable API. The `[observability]` keys correspond to `OtelConfig` fields: `endpoint`, `use_stdout`, `sample_ratio`, `meter_interval`, `service_name`, `service_version`, `environments`, `logger_level`, and `local_logging_enabled`.

## Control Flow
No control flow. Consumers would parse the TOML into an application config, but the current `config.rs` primarily reads env variables rather than this file directly.

## State and Persistence
The file is static sample configuration. It does not alter runtime behavior unless explicitly loaded by an example or application.

## Dependencies and Integration
Acts as documentation for the observability crate and should stay aligned with `OtelConfig` env-backed fields and naming conventions.

## Risks
Some names appear older than current `OtelConfig` field names, such as `environments` versus `environment` and `local_logging_enabled` versus the current local logging fields. If users copy this file, stale keys may not be honored by current config loaders.

## Test Signals
No tests reference this TOML in the inspected files. Its value is mostly as operator-facing sample material.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/server.rs -->
# sources/object-store/rustfs/crates/obs/examples/server.rs

## Purpose
Demonstrates initializing observability and emitting trace/log/metric data from a Tokio program. It simulates a service run and a `put_object` operation with spans and histogram records.

## Important APIs, Types, and Functions
`main` calls `rustfs_obs::init_obs` with a local OTLP endpoint, creates a tracing span, logs lifecycle messages, and calls `run`. `run` and `put_object` are annotated with `#[instrument(fields(bucket, object, user))]`. Both use `opentelemetry::global::meter("rustfs")` and an `s3_request_duration_seconds` histogram.

## Control Flow
The async main initializes telemetry, enters a top-level span, sleeps briefly, invokes `run`, then exits. `run` records a duration metric and calls `put_object`, which records another duration metric and sleeps to simulate work.

## State and Persistence
State is local and transient. The `_guard` returned by `init_obs` is kept alive for the example duration so telemetry providers can flush on drop. Exported telemetry may persist in the configured collector.

## Dependencies and Integration
Uses `rustfs_obs`, OpenTelemetry global meter, Tokio time, and tracing macros. It integrates with whatever exporters `init_obs` configures.

## Risks
`init_obs` returns a `Result`, but the example stores it directly without handling failure; if initialization fails, `_guard` is an error value and telemetry may not be active. Repeated histogram construction inside functions is acceptable for demos but not ideal for hot paths.

## Test Signals
This is an example rather than a unit test. It can be run manually against a collector at `http://localhost:4318` to verify log/span/metric export.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9.rs -->
# sources/object-store/rustfs/crates/obs/examples/test_dial9.rs

## Purpose
Provides a lightweight manual test for dial9 Tokio runtime telemetry configuration. It verifies default enabled state and prints the env-derived config.

## Important APIs, Types, and Functions
Uses `rustfs_obs::dial9::{Dial9Config, is_enabled}`. `main` checks `is_enabled`, constructs `Dial9Config::from_env`, prints fields such as output directory, file prefix, max size, rotation count, S3 bucket/prefix, and sampling rate, then conditionally asserts default-disabled behavior.

## Control Flow
The example runs three logical checks: default state, config loading, and validation. If dial9 is already enabled through the environment, it skips assertions that assume disabled defaults.

## State and Persistence
No session is initialized and no telemetry file is written. It only reads environment variables and prints results.

## Dependencies and Integration
Integrates with the crate-root dial9 re-export from `telemetry::dial9`. Intended to be invoked through `cargo run -p rustfs-obs --example test_dial9`.

## Risks
It uses console output and assertions rather than structured test harness assertions. Unicode status symbols are present in output, which is harmless for terminals but not important to behavior.

## Test Signals
Manual signal is successful completion and printed PASS lines. It documents env variables needed for enabled dial9 runs and S3 options.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_full.rs -->
# sources/object-store/rustfs/crates/obs/examples/test_dial9_full.rs

## Purpose
Exercises the full dial9 lifecycle, including session initialization, async workload generation, and guard drop cleanup.

## Important APIs, Types, and Functions
Imports `Dial9Config`, `init_session`, and `is_enabled`. The async `main` reads config, calls `init_session().await`, checks `guard.is_active()`, spawns three Tokio tasks that sleep and print iterations, then drops the guard.

## Control Flow
If dial9 is disabled, the example prints enable instructions and exits successfully. When enabled, it reports config, initializes a session, runs concurrent async tasks to generate runtime activity, and tests cleanup by dropping the guard. `Ok(None)` is treated as a nonfatal writer failure case.

## State and Persistence
When enabled and initialized, dial9 likely writes telemetry artifacts under the configured output directory. The guard owns session lifecycle and cleanup.

## Dependencies and Integration
Depends on Tokio task spawning and time, plus the crate dial9 module. It is useful for validating dial9 integration in a real runtime rather than just config parsing.

## Risks
The summary prints PASS lines even if `init_session` returns an error; this is suitable for exploratory examples but could mislead if used as CI. It does not inspect output files.

## Test Signals
Manual signals include config printout, session initialization result, guard activity state, task completion, and absence of runtime errors.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_full.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_s3.rs -->
# sources/object-store/rustfs/crates/obs/examples/test_dial9_s3.rs

## Purpose
Manually validates dial9 S3 configuration handling. It focuses on bucket and prefix fields under default and environment-derived configs.

## Important APIs, Types, and Functions
Uses `Dial9Config::default`, `Dial9Config::from_env`, and `is_enabled`. It asserts default S3 bucket and prefix are `None`, prints the `RUSTFS_RUNTIME_DIAL9_ENABLED` env var, and displays configured S3 upload state.

## Control Flow
The example first checks default config, then reports enabled state, then loads environment config. If dial9 is disabled, it skips S3-specific enabled assertions and prints instructions. If enabled, it prints whether S3 upload is active and any bucket/prefix values.

## State and Persistence
No dial9 session is started and no S3 upload occurs. It only reads configuration.

## Dependencies and Integration
Integrates with dial9 config parsing through the `rustfs_obs` crate-root re-export. It documents required environment variables for S3 testing.

## Risks
The example validates config presence but not credentials, upload permissions, object key formation, or network behavior. As with other examples, console PASS output is manual-test oriented.

## Test Signals
Assertions ensure default S3 fields are absent. Manual output confirms env-derived S3 settings when dial9 is enabled.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_s3.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_simple.rs -->
# sources/object-store/rustfs/crates/obs/examples/test_dial9_simple.rs

## Purpose
Provides the smallest dial9 configuration smoke test. It reads environment state, prints the parsed config, and confirms base path calculation.

## Important APIs, Types, and Functions
Uses `Dial9Config::from_env`, `Dial9Config::base_path`, and `is_enabled`. It prints enabled flag, output directory, file prefix, max file size, rotation count, and sampling rate.

## Control Flow
The async main performs three sequential checks: environment enabled state, config loading, and base-path calculation. It does not initialize a telemetry session.

## State and Persistence
No files are written. Runtime state is limited to local config values parsed from environment variables.

## Dependencies and Integration
Depends on the dial9 module re-export from `rustfs_obs`. It can be run with env variables to confirm parser behavior before running the full session example.

## Risks
It is not a real integration test of writer creation, rotation, S3 upload, or runtime event capture. It only proves the config API can be called.

## Test Signals
Successful completion and printed config values are the expected signal. The example documents env vars for enabling full dial9 functionality.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_simple.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/compress.rs -->
# sources/object-store/rustfs/crates/obs/src/cleaner/compress.rs

## Purpose
Contains compression-only helpers for old log files. It intentionally separates archive creation from source deletion so a failed or partial compression cannot remove the original log.

## Important APIs, Types, and Functions
`CompressionOptions` carries algorithm, gzip/zstd levels, zstd worker count, fallback policy, and dry-run flag. `CompressionOutput` describes the archive path, codec used, input bytes, and output bytes. `compress_file` dispatches to gzip or zstd, with optional zstd-to-gzip fallback. Internal helpers include `compress_gzip`, `compress_zstd`, `compress_with_writer`, and `archive_path`.

## Control Flow
Compression first computes the target `<filename>.<ext>` archive path. If it already exists, the helper returns success metadata for idempotency. Dry-run returns planned output without creating files. Real compression writes to `archive.tmp`, flushes and finishes the encoder, optionally copies Unix permission bits, then atomically renames the temp file into place.

## State and Persistence
The persistent output is a `.gz` or `.zst` archive next to the source file. Incomplete temp archives are best-effort removed on writer failure. Source files are never deleted in this module.

## Dependencies and Integration
Uses `flate2` for gzip, `zstd` for zstd/zstdmt, std file I/O, and tracing. `cleaner::core` invokes it from serial and parallel cleanup paths.

## Risks
Existing archives are trusted as successful prior output even if corrupted or incomplete from an earlier external process. Atomic rename is local-filesystem safe but can fail across unusual mount behavior. Zstd multithreading may consume more CPU when many outer parallel workers are also active.

## Test Signals
No local tests are in this file, but cleaner integration tests exercise compression-enabled deletion paths indirectly where configured. Core metrics and log events expose compression success/failure.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/compress.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/core.rs -->
# sources/object-store/rustfs/crates/obs/src/cleaner/core.rs

## Purpose
Implements the log cleanup service: scan matching logs, choose retention victims, optionally compress them, securely delete originals, expire old compressed archives, and emit metrics.

## Important APIs, Types, and Functions
`LogCleaner` is the immutable service object. `LogCleaner::builder` returns `LogCleanerBuilder`; `cleanup` runs one pass. Important internals include `select_files_to_process`, `select_expired_compressed`, `parallel_stealing_compress`, `serial_compress_and_delete`, `secure_delete`, and `delete_files`. The builder exposes retention, size, age, dry-run, exclusion, compression, zstd, and parallel-worker settings.

## Control Flow
`cleanup` exits early for missing directories, scans via `scanner::scan_log_directory`, sorts regular logs by modification time, selects files by keeping newest generations and enforcing size limits, then compresses/deletes either serially or with work-stealing workers. Compressed archives are separately expired by age. Metrics counters/histograms/gauges are emitted for deletion, freed bytes, compression duration, and stealing success.

## State and Persistence
The cleaner has no mutable in-memory state between passes. Persistent effects are deletion of selected files, optional archive creation, and deletion of expired archives. Dry-run returns projected counters without mutation.

## Dependencies and Integration
Uses scanner, compressor, cleaner types, crossbeam channel/deque/thread utilities, `metrics`, tracing, and global metric name constants. It is re-exported by `cleaner::mod` and likely used by telemetry rolling-log setup.

## Risks
Retention selection treats `keep_files` as a maximum retained count despite some comments saying minimum. Invalid glob patterns are silently ignored. Parallel compression falls back to serial only on worker panic, not on individual compression failures. Dry-run metrics may look like real deletion if consumers do not distinguish logs.

## Test Signals
Tests in `mod.rs` cover oldest deletion by size, keep-file enforcement, ignoring unrelated files, scanner counts, dry-run non-mutation, and suffix matching. Core also has explicit symlink refusal and Windows retry logic for deletion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/core.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/mod.rs -->
# sources/object-store/rustfs/crates/obs/src/cleaner/mod.rs

## Purpose
Defines the cleaner subsystem module boundary and documents the cleanup lifecycle. It re-exports the public `LogCleaner` API while keeping scanner/compressor/core internals organized.

## Important APIs, Types, and Functions
Declares private `compress`, `core`, and `scanner` modules plus public `types`. Re-exports `core::LogCleaner`. The module-level documentation explains scan, selection, compression, deletion, and archive expiration stages.

## Control Flow
No production control flow is implemented here beyond module wiring. The embedded tests construct cleaners and call cleanup behavior in integration-style scenarios.

## State and Persistence
No module-level state exists. Tests create temporary directories and files to validate filesystem effects.

## Dependencies and Integration
This file is the public entry point for observability log cleanup. Callers can import `rustfs_obs::LogCleaner` after crate-level re-export. Tests use `tempfile`, std file I/O, and `scanner::scan_log_directory`.

## Risks
The documentation says the cleaner preserves a minimum number of files, while tests and core behavior enforce `keep_files` as a ceiling on retained files. That semantic mismatch should be clarified for operators.

## Test Signals
Tests validate size-based cleanup, count-based cleanup, unrelated-file isolation, scanner matching, dry-run behavior, and suffix matching. They provide useful regression coverage for retention semantics and file selection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/scanner.rs -->
# sources/object-store/rustfs/crates/obs/src/cleaner/scanner.rs

## Purpose
Scans a log directory once and classifies matching files as regular logs or already-compressed archives. It is the cleaner pipeline's first safety boundary.

## Important APIs, Types, and Functions
`LogScanResult` contains `logs` and `compressed_archives`. `scan_log_directory` takes directory, pattern, active filename, match mode, glob exclusions, minimum age, empty-file deletion, and dry-run flags. `is_excluded` checks filenames against compiled glob patterns.

## Control Flow
The scanner performs a shallow `read_dir` pass. Missing directories produce an empty result. It uses `symlink_metadata` so symlinks are not followed, skips non-regular files, skips the active log file, applies exclusions, recognizes compressed suffixes, strips archive suffixes for logical matching, optionally deletes empty regular logs, applies age gating to regular logs only, then appends `FileInfo` to the appropriate vector.

## State and Persistence
Normally read-only, but it can delete zero-byte regular log files during scan when enabled. In dry-run mode it logs intent instead. It returns metadata snapshots with size and modified time.

## Dependencies and Integration
Uses std filesystem APIs, `glob::Pattern`, tracing, and `CompressionAlgorithm::compressed_suffixes`. `core::cleanup` consumes its scan result for retention selection.

## Risks
The scan is non-recursive, so nested log layouts are ignored. Empty-file deletion happens before the main cleanup metrics counters in `core`, so separate accounting may be needed if operators care. Files can change after metadata snapshot, creating normal filesystem race conditions mitigated later by secure deletion.

## Test Signals
Tests in `cleaner::mod` validate scanner matching and ignoring unrelated files. Comments explicitly call out symlink safety and avoiding TOCTOU from metadata calls.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/scanner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/types.rs -->
# sources/object-store/rustfs/crates/obs/src/cleaner/types.rs

## Purpose
Defines lightweight shared types for the cleaner pipeline: file matching modes, compression algorithms, default worker count, and discovered file metadata.

## Important APIs, Types, and Functions
`FileMatchMode` supports prefix and suffix matching, with parsing from config strings and display. `CompressionAlgorithm` supports gzip and zstd, accepts full names and extension aliases, reports archive extensions and compressed suffixes, and implements `FromStr`, `Default`, and display. `default_parallel_workers` clamps CPU count into 4..=8. `FileInfo` carries path, size, and modified timestamp.

## Control Flow
Parsing is permissive for config (`from_config_str` falls back to defaults) and strict for `FromStr` (invalid values error). Archive suffix helpers centralize `.gz` and `.zst` recognition.

## State and Persistence
No mutable state. `FileInfo` is a metadata snapshot used by later cleanup stages.

## Dependencies and Integration
Uses observability constants from `rustfs_config`, `num_cpus`, std formatting, paths, and time. Scanner, compressor, and core all depend on these types.

## Risks
Permissive config parsing can hide typos by silently falling back to defaults. The worker clamp uses at least four workers even on small machines, which improves concurrency tests but may be aggressive in constrained deployments.

## Test Signals
Tests validate compression algorithm parsing for names and aliases, fallback behavior for config parsing, and strict `FromStr` rejection of invalid values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/config.rs -->
# sources/object-store/rustfs/crates/obs/src/config.rs

## Purpose
Builds RustFS observability configuration from environment variables. It covers OTLP endpoints and headers, signal enablement, profiling, stdout behavior, local rolling log settings, and cleaner retention/compression policy.

## Important APIs, Types, and Functions
`OtelConfig` is the main serializable/deserializable config struct. `OtelConfig::extract_otel_config_from_env` reads all env-backed settings and applies defaults. `OtelConfig::new` and `Default` call that function. `AppConfig` wraps `OtelConfig` for application-level config. `is_production_environment` checks the environment string against the production constant.

## Control Flow
An explicit endpoint argument takes priority over `RUSTFS_OBS_ENDPOINT`. If no endpoint is configured, `use_stdout` is forced true to preserve visible logs. Log directory is only set when the env var is non-empty. `log_keep_files` is normalized so zero falls back to the default. Profiling export reads a canonical env var with a legacy alias fallback.

## State and Persistence
The file stores no global state. It reads process environment each time config is constructed. Resulting config can drive telemetry setup and log cleaner scheduling.

## Dependencies and Integration
Depends heavily on `rustfs_config` constants and `rustfs_utils` env parsing helpers. `global::init_obs` and telemetry modules consume `OtelConfig`.

## Risks
Many fields are `Option<T>` even after defaults are applied, so downstream code must handle `None` for any manually constructed config. Sample TOML naming can drift from env-backed field names. Header parsing is not performed here, so invalid header strings fail later.

## Test Signals
Tests cover profiling export default disabled behavior, legacy alias support, and canonical env precedence over the legacy alias using a process-wide mutex to avoid env-test races.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/error.rs -->
# sources/object-store/rustfs/crates/obs/src/error.rs

## Purpose
Defines observability error types used by global initialization and telemetry backend setup.

## Important APIs, Types, and Functions
`GlobalError` wraps failures such as setting the global metrics recorder, setting the global guard, missing guard initialization, metrics/system errors, PID/process/core-count/GPU errors, log-send failure, timeout, and telemetry initialization. `TelemetryError` captures exporter build failures, metrics recorder install failure, subscriber init failure, I/O errors, and permission errors. `From<std::io::Error>` maps I/O into `TelemetryError::Io`.

## Control Flow
There is no active control flow except `From` conversions and `thiserror` formatting. `#[from]` conversions allow `?` propagation from underlying setup functions.

## State and Persistence
No state or persistence. Errors carry strings and source error conversions.

## Dependencies and Integration
Depends on `thiserror`, `metrics::SetRecorderError`, Tokio `SetError`, `Arc<Mutex<OtelGuard>>`, and the crate `Recorder`. Used by `global.rs` and telemetry initialization modules.

## Risks
Several variants store only `String`, losing typed source errors and backtrace context. `SendFailed` and `Timeout` use static strings, so callers need external context for detailed diagnostics.

## Test Signals
No direct tests. Compile-time use in `global.rs` tests and telemetry initialization paths validates conversion compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/global.rs -->
# sources/object-store/rustfs/crates/obs/src/global.rs

## Purpose
Provides crate-level observability initialization and global guard management. It also centralizes metric-name constants for log cleaner monitoring.

## Important APIs, Types, and Functions
`GLOBAL_GUARD` stores an `Arc<Mutex<OtelGuard>>` in a Tokio `OnceCell`. `OBSERVABILITY_METRIC_ENABLED` stores the one-time metrics-enabled flag. Public APIs include `observability_metric_enabled`, `init_obs`, `init_obs_with_config`, `set_global_guard`, and `get_global_guard`. Internal `set_observability_metric_enabled` logs when a conflicting second value is attempted.

## Control Flow
`init_obs` builds `AppConfig` from an optional endpoint and delegates to `init_obs_with_config`, which calls `telemetry::init_telemetry`. Setting the global guard logs initialization and fails if the cell is already set. Getting the guard returns `NotInitialized` when absent.

## State and Persistence
State is process-global and one-shot. Dropping the returned or stored `OtelGuard` controls telemetry flushing and shutdown, but this module itself does not persist anything.

## Dependencies and Integration
Uses config, error, telemetry initialization, Tokio `OnceCell`, tracing, and the metrics constants consumed by cleaner/core and dashboards. It is re-exported from crate `lib.rs`.

## Risks
Global one-time initialization can make repeated tests or embedded runtimes order-sensitive. `init_obs_with_config` returns a guard but does not set it globally; callers must explicitly call `set_global_guard` if global retrieval is needed. A mutex around guard shutdown can serialize access.

## Test Signals
Tests verify uninitialized guard errors, cleaner metric namespace prefixes, README/dashboard content for cleaner metrics, documented `init_obs_with_config` signature, and dashboard deployment references.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/global.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/lib.rs -->
# sources/object-store/rustfs/crates/obs/src/lib.rs

## Purpose
Defines the public boundary for the `rustfs-obs` crate. It wires observability submodules and re-exports the user-facing initialization, config, logging, metrics runtime, schema, cleaner, and telemetry types.

## Important APIs, Types, and Functions
Modules include `cleaner`, `config`, `error`, `global`, `logging`, public `metrics`, and `telemetry`. Re-exports include `init_obs`, `init_obs_with_config`, `OtelConfig`, `AppConfig`, `GlobalError`, `LogCleaner`, logging redaction helpers, metrics schema and runtime controller types, `OtelGuard`, `Recorder`, and `telemetry::dial9`.

## Control Flow
No runtime control flow is implemented. This file only determines what downstream crates can import from `rustfs_obs`.

## State and Persistence
No state here. Global state lives in `global.rs`; telemetry provider lifecycle lives under `telemetry`.

## Dependencies and Integration
This is the integration facade for RustFS services. Consumers can initialize observability, start metrics runtime scheduling, access metric schemas, run log cleanup, and use dial9 runtime telemetry through this crate root.

## Risks
The broad re-export surface couples external callers to many internal metrics runtime types, making refactors more expensive. The private `telemetry` module still exposes selected types and dial9, so public API stability depends on those modules.

## Test Signals
Doc examples in the module comment compile as documentation examples where enabled. Child modules provide most behavioral test coverage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/logging.rs -->
# sources/object-store/rustfs/crates/obs/src/logging.rs

## Purpose
Defines log redaction policy and helper functions to prevent secrets and sensitive principal identifiers from being emitted in observability logs.

## Important APIs, Types, and Functions
`REDACTED_LOG_VALUE` is the replacement string. `LOGGING_REDACTION_RULES` lists sensitive fields such as access key, authorization, client secret, secret key, session token, and token. `validate_logging_redaction_rules` delegates to security-governance validation. `is_sensitive_log_field` checks fields case-insensitively. `redacted_log_value` preserves empty strings and redacts non-empty values; `redacted_optional_log_value` maps optional values. `MaskedAccessKey` is re-exported from `rustfs_utils`.

## Control Flow
Redaction checks trim and compare field names against the rule list. Helper functions are pure and do not mutate state.

## State and Persistence
No runtime state. The policy is a static slice of `RedactionRule` values.

## Dependencies and Integration
Integrates with `rustfs_security_governance` for rule validation and `rustfs_utils` for access-key masking. Tests inspect source files across the workspace to enforce logging governance patterns.

## Risks
Static field-name matching can miss nested, renamed, or semantically secret fields not in the rule list. The generic `token` rule may redact benign fields named token, but that is a deliberate conservative choice.

## Test Signals
Tests validate policy, case-insensitive detection, empty-value preservation, access key masking, absence of old unmasked logging patterns in auth/protocol/startup/telemetry/audit/notify code, and allowed low-level stderr exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/logging.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/audit.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/audit.rs

## Purpose
Adapts audit target statistics into Prometheus metrics using the crate's audit metric descriptors.

## Important APIs, Types, and Functions
`AuditTargetStats` carries `target_id`, `failed_messages`, `queue_length`, and `total_messages`. `collect_audit_metrics` returns three metrics per target: failed messages, queue length, and total messages, each labeled with `target_id`.

## Control Flow
The collector returns an empty vector for empty input. Otherwise it preallocates `stats.len() * 3`, clones the target id into a `Cow<'static, str>`, and pushes metrics created from descriptors with the target label.

## State and Persistence
Stateless. It converts caller-provided snapshots into metric values and does not retain history.

## Dependencies and Integration
Uses `PrometheusMetric` and descriptors from `crate::metrics::schema::audit`. Intended for metrics endpoints or runtime collectors that can assemble audit subsystem stats.

## Risks
Target IDs become metric labels, so high-cardinality target naming can increase Prometheus load. Counts are cast to `f64`, which is standard for Prometheus text metrics but can lose integer precision at very large values.

## Test Signals
Tests cover two-target metric count and label lookup, plus empty input returning no metrics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/audit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/bucket.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/bucket.rs

## Purpose
Adapts per-bucket usage and quota statistics into Prometheus metrics using the node-bucket metric descriptors.

## Important APIs, Types, and Functions
`BucketStats` carries bucket `name`, `size_bytes`, `objects_count`, and `quota_bytes`. `collect_bucket_metrics` emits three metrics per bucket: usage bytes, objects total, and quota bytes, each labeled by `bucket`.

## Control Flow
Empty input returns an empty vector. Non-empty input preallocates `buckets.len() * 3`, clones each bucket name into a `Cow`, and pushes descriptor-backed `PrometheusMetric` values. Zero quota is still emitted as a metric value.

## State and Persistence
Stateless snapshot conversion. It does not query storage directly or persist previous values.

## Dependencies and Integration
Uses `PrometheusMetric`, `report_metrics` in tests, and descriptors from `crate::metrics::schema::node_bucket`. HTTP metrics handlers or background collectors should populate `BucketStats` from storage/admin sources.

## Risks
Bucket names are metric labels, so very large bucket counts increase cardinality. Values are converted from `u64` to `f64`, which can lose exact precision above 2^53. The collector trusts callers to provide consistent quota semantics.

## Test Signals
Tests verify metric count and labels for multiple buckets, quota reporting, empty input, explicit zero-quota output, and `BucketStats::default` values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/bucket.rs -->
