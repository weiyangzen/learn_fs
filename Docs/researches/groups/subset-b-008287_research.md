# Research: subset-b-008287

Work item `subset-b-008287` covers the RustFS scanner crate files under `sources/object-store/rustfs/crates/scanner/src/`. The sections below preserve source paths exactly so the reconciliation lane can split them into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/data_usage_define.rs -->
# sources/object-store/rustfs/crates/scanner/src/data_usage_define.rs

## Purpose

`data_usage_define.rs` defines the scanner's data-usage cache model, size/replication/tier accounting helpers, persisted cache paths, scan checkpoint metadata, and cache load/save behavior. It is the main in-crate bridge between `rustfs_data_usage` aggregate types and scanner-specific persistence rules. The file also re-exports core data-usage types (`DataUsageInfo`, `DataUsageEntry`, `DataUsageHash`, `BucketUsageInfo`, etc.) so the scanner crate can expose the data-usage API through `lib.rs`.

## Important APIs, Types, and Functions

- Constants and paths:
  - `DATA_USAGE_ROOT`, `DATA_USAGE_CACHE_NAME`, `DATA_USAGE_SCAN_CHECKPOINT_VERSION`.
  - `DATA_USAGE_BUCKET`, `DATA_USAGE_OBJ_NAME_PATH`, `DATA_USAGE_BLOOM_NAME_PATH`, and `BACKGROUND_HEAL_INFO_PATH` are `LazyLock<String>` values built from the meta bucket and bucket metadata prefix.
  - Internal object names include `.usage.json`, `.bloomcycle.bin`, `.usage-cache.bin`, and `.bloomcycle.bin`.
- Accounting types:
  - `TierStats` tracks size, versions, and latest object count per storage tier. `from_object_info` converts an `ObjectInfo` into one version of tier usage.
  - `AllTierStats` merges and populates tier maps.
  - `SizeSummary` accumulates object/version/delete-marker totals, replication status sizes/counts, per-target replication stats, and per-tier stats.
  - `ReplTargetSizeSummary` is the per-replication-target portion of `SizeSummary`.
- Checkpoint types:
  - `DataUsageScanCheckpointReason` serializes as snake_case values `runtime`, `objects`, `directories`, and `unknown`.
  - `DataUsageScanCheckpoint` records `version`, `resume_after`, and `reason`; `new` stamps the current checkpoint version.
  - `DataUsageCacheInfo` includes bucket/cache metadata, lifecycle and replication configs, failed-object counts, old `scan_resume_after`, and newer structured `scan_checkpoint`.
- `DataUsageCache` is the central cache structure:
  - `replace` and `replace_hashed` insert entries and wire parent child references.
  - `find`, `find_children_copy`, `root`, and `root_hash` are lookup helpers.
  - `flatten`, `size_recursive`, and `dui` collapse child trees into aggregate usage information.
  - `copy_with_children`, `delete_recursive`, `search_parent`, `is_compacted`, `force_compact`, `reduce_children_of`, `total_children_rec`, and `merge` maintain or reduce cache tree state.
  - `marshal_msg` and `unmarshal` use MessagePack via `rmp_serde` for scanner cache persistence.
  - `load` and `save` handle object-store persistence with timeouts, retries, fallback paths, backup writes, logging, and metrics.
- `DataUsageCacheStorage` is an async trait placeholder for storage-specific cache load/save implementations, but this file does not provide a concrete implementation.

## Control Flow

Cache mutation starts with hashed path insertion. `replace_hashed` inserts the entry by `DataUsageHash::key()` and, when a parent is present, ensures the parent entry exists and records the child hash. Read-side aggregation starts at a found entry, recursively `flatten`s descendants, merges their `DataUsageEntry` counters, and clears children from the returned aggregate so callers receive a compact summary rather than a tree.

`dui` converts an arbitrary cached path plus a bucket list into a `DataUsageInfo`: it flattens the requested path for global totals, then flattens each bucket for per-bucket `BucketUsageInfo`, including histograms and replication target details when present.

Compaction follows two paths. `force_compact` triggers only when cache length reaches a caller-provided limit; it may compact a very large top-level child list, then retains only reachable nodes from the top entry. `reduce_children_of` computes recursive child pressure, collects internal nodes with `add`, sorts candidates by object count, and replaces selected subtrees with compacted flat entries until enough children have been removed. It uses saturating subtraction to avoid underflow when one candidate removes more children than the remaining target.

`load` resets the receiver to default, attempts the main cache object up to five times, and tries a `.bkp` object between retries. The lower-level `try_load_inner` first reads from `RUSTFS_META_BUCKET/<bucket-meta-prefix>/<name>`, then falls back to `DATA_USAGE_BUCKET/<name>` for compatibility. Not-found and decode failures return empty cache without hard failure; quorum, faulty disk, full disk/storage, slowdown, and timeout are treated as retryable; other storage errors are returned.

`save` serializes to MessagePack, writes the main object under the bucket metadata prefix with the configured cache-save timeout and two retries, then attempts a `.bkp` write with timeout capped at five seconds and no retries. Main save failure is returned; backup save failure is logged but not fatal.

## State and Persistence Behavior

The cache is an in-memory `HashMap<String, DataUsageEntry>` keyed by data-usage hash strings, plus `DataUsageCacheInfo` metadata. Parent-child links are duplicated inside `DataUsageEntry.children`; callers must keep those links consistent when replacing or deleting nodes. `find_children_copy` has the side effect of creating an empty cache entry for missing hashes.

Scanner cache persistence uses MessagePack, while the higher-level scanner data-usage snapshot in `scanner.rs` uses JSON. The cache loader is intentionally optimistic and lock-free because scanner data is background-maintained. It handles old serialized forms by defaulting missing `scan_resume_after` and `scan_checkpoint` fields. Save metrics are registered once and emitted with labels for main vs backup cache and result states success/error/timeout.

Checkpoint fields support partial scan resume in `scanner_folder.rs`: `scan_resume_after` is the older simple marker, while `scan_checkpoint` adds version and stop reason. This file owns the serialized schema and compatibility defaults, not the scan-resume algorithm itself.

## Dependencies and Integration Points

- Re-exports and composes `rustfs_data_usage` types.
- Reads object metadata from `rustfs_ecstore::store_api::ObjectInfo` and object-store IO via `ObjectIO`.
- Persists through `rustfs_ecstore::config::com::save_config` and object readers.
- Uses lifecycle and replication config types in `DataUsageCacheInfo`, with `TRANSITION_COMPLETE` and `storageclass::STANDARD` used for tier accounting.
- Uses `runtime_config::scanner_cache_save_timeout()` for save timeout behavior.
- Emits `metrics` counters/histograms and structured `tracing` warnings.
- Used heavily by `scanner_io.rs` and `scanner_folder.rs` for namespace scanning, partial caches, checkpointing, and cache merging.

## Risks and Edge Cases

- Cache parent-child consistency is manual; direct map edits can orphan entries or leave stale child references.
- `find_children_copy` mutates missing paths by inserting a default entry, which can surprise callers expecting a pure read.
- `SizeSummary::actions_accounting` appears to call `tier_stats.add(...)` without assigning the returned `TierStats`; because `TierStats::add` returns a new value rather than mutating `self`, existing tier entries may not be updated as intended.
- Load treats deserialization failures as empty cache rather than surfacing corruption, so bad cache data may silently trigger full rebuild behavior.
- Lock-free cache load/save means readers can observe stale or partially superseded scanner data; backup and retry logic mitigate but do not provide transactional persistence.
- The compatibility fallback path in `try_load_inner` reads from two locations. Future path changes must keep this dual lookup in mind to avoid losing existing deployments.
- Backup save is best-effort. A successful main write followed by failed backup write is considered success.
- Compaction chooses candidates by object count, not size or operational value; compacting small-object internal nodes first may not minimize memory in all workloads.

## Test Signals

The module has focused unit tests for data-usage merging, defaulting old serialized cache info, cache tree mutation, recursive copy/delete, missing-child lookup side effects, cache path classification, cache save timeout environment behavior, retry save success and timeout failure, and compaction candidate/underflow behavior. These tests signal that compatibility with older serialized cache shapes, bounded save behavior, and compaction correctness are important maintenance contracts.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/data_usage_define.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/error.rs -->
# sources/object-store/rustfs/crates/scanner/src/error.rs

## Purpose

`error.rs` defines the scanner crate's shared error enum. It keeps scanner-specific failures independent from lower-level object-store errors while still allowing standard IO and JSON serialization failures to flow through with `From` conversions.

## Important APIs, Types, and Functions

- `ScannerError` is `#[non_exhaustive]`, `Debug`, and `thiserror::Error`.
- Variants:
  - `Config(String)` for configuration failures.
  - `Io(std::io::Error)` via `#[from]`.
  - `Serialization(serde_json::Error)` via `#[from]`.
  - `Other(String)` for miscellaneous scanner failures.
  - `PartialCache(Box<DataUsageCache>)` for a scan that stopped after producing usable partial data.

## Control Flow

The enum is consumed by scanner routines that return `Result<_, ScannerError>`. `scanner.rs` uses it for the `run_data_scanner` return type, while `scanner_folder.rs` uses `Other`, `Io`, and `PartialCache` during directory traversal and budget/cancellation handling. `PartialCache` is a control-flow-bearing error: callers can inspect the boxed cache and preserve progress instead of treating the scan as a complete failure.

## State and Persistence Behavior

The only state carried directly by this file is the `DataUsageCache` boxed inside `PartialCache`. That cache may include resume markers and checkpoint metadata defined in `data_usage_define.rs`. Persistence is handled by the receiving scanner/cache code, not by the error type.

## Dependencies and Integration Points

- Depends on `thiserror` for display/error implementations.
- Depends on `serde_json` and `std::io` through conversion variants.
- Depends on `crate::data_usage_define::DataUsageCache` for partial scan propagation.
- Re-exported by `lib.rs` as `rustfs_scanner::ScannerError`.

## Risks and Edge Cases

- `Other(String)` is flexible but unstructured; callers cannot reliably match specific scanner failure causes unless a dedicated variant exists.
- `PartialCache` as an error can be mishandled by generic error logging paths, losing useful partial progress unless callers explicitly match it.
- Because the enum is non-exhaustive, downstream crates must include wildcard matches. That is good for forward compatibility but limits exhaustive handling outside the crate.

## Test Signals

This file has no direct unit tests. Behavior is indirectly exercised by `scanner_folder.rs` tests that expect `ScannerError::PartialCache` when budgets interrupt directory scanning, and by scanner paths that convert IO/serialization failures.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/lib.rs -->
# sources/object-store/rustfs/crates/scanner/src/lib.rs

## Purpose

`lib.rs` is the scanner crate root. It declares scanner submodules, exposes the public API surface used by other RustFS crates, and tracks coarse scanner activity with an atomic work-unit counter.

## Important APIs, Types, and Functions

- Module declarations:
  - Public modules: `data_usage_define`, `error`, `runtime_config`, `scanner`, `scanner_budget`, `scanner_folder`, `scanner_io`, and `sleeper`.
- Re-exports:
  - All public items from `data_usage_define`.
  - `ScannerError`.
  - Runtime config entry points: `apply_scanner_runtime_config`, `scanner_runtime_config_status`, and `validate_scanner_runtime_config`.
  - `rustfs_common::last_minute`.
  - `scanner::init_data_scanner`.
  - `DynamicSleeper`, `SCANNER_IDLE_MODE`, and `SCANNER_SLEEPER`.
- Activity tracking:
  - `current_scanner_activity() -> u64` reads `SCANNER_ACTIVE_WORK_UNITS`.
  - `ScannerActivityGuard::new()` increments the counter.
  - `Drop for ScannerActivityGuard` decrements with saturating behavior through `fetch_update`.

## Control Flow

Other crates initialize background scanner work through the re-exported `init_data_scanner`. Runtime configuration is validated/applied through re-exported functions from `runtime_config.rs`. Internal scanner tasks create `ScannerActivityGuard` values around active work; when guards drop, the global counter is decremented. This gives observers a simple measure of active scanner work without coupling to individual task implementations.

## State and Persistence Behavior

The only crate-root state is `SCANNER_ACTIVE_WORK_UNITS: AtomicU64`. It is process-local, relaxed-ordering telemetry and is not persisted. Persistence of scanner cycles, background heal state, and data-usage snapshots is delegated to `scanner.rs` and `data_usage_define.rs`.

## Dependencies and Integration Points

- Provides the public namespace for scanner consumers, including integration tests that import `rustfs_scanner::scanner::init_data_scanner`.
- Integrates with `runtime_config`, `sleeper`, and data-usage definitions by re-exporting their stable entry points.
- `ScannerActivityGuard` is used in `scanner.rs` around scan cycles and backend data-usage saving.

## Risks and Edge Cases

- `ScannerActivityGuard` is crate-private, so external consumers can observe but not mark scanner work. That keeps the counter scoped but means all internal work sites must remember to use the guard.
- Relaxed atomic ordering is suitable for approximate telemetry but not for synchronization decisions.
- The crate has `unreachable_pub` warnings enabled; exported module contents should be intentional because public module declarations can expose more than the curated re-export list.

## Test Signals

There are no direct tests in `lib.rs`. Activity behavior is indirectly covered when scanner tests run guarded operations, but there is no explicit test asserting `current_scanner_activity` increments/decrements.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/runtime_config.rs -->
# sources/object-store/rustfs/crates/scanner/src/runtime_config.rs

## Purpose

`runtime_config.rs` resolves, validates, applies, and reports scanner runtime configuration. It merges defaults, persisted server config, scanner compatibility config, environment variables, and deployment-specific default overrides into a single `ScannerRuntimeConfig`. It also updates the global scanner sleeper so pacing changes take effect in scanner loops.

## Important APIs, Types, and Functions

- `ScannerRuntimeConfigSource` identifies where a value came from: `Env`, `Config`, `ScannerCompatConfig`, or `Default`.
- `ScannerRuntimeConfig` stores resolved scanner settings: speed, delay, max wait, idle mode, startup delay, cycle interval, bitrot cycle, cycle budget, cache save timeout, scan concurrency, yield cadence, and alert thresholds.
- `ScannerRuntimeConfigError::InvalidValue` reports invalid persisted config with key, value, and reason.
- `ScannerRuntimeConfigValue<T>` and `ScannerRuntimeConfigStatus` expose status with both value and source for each setting.
- Global state:
  - `SCANNER_DEFAULT_CYCLE_SECS: AtomicU64` stores optional deployment-specific default cycle override.
  - `SCANNER_RUNTIME_CONFIG: LazyLock<RwLock<ScannerRuntimeConfig>>` stores the current resolved config.
- Public/crate APIs:
  - `set_scanner_default_cycle_secs`.
  - `lookup_scanner_runtime_config`.
  - `validate_scanner_runtime_config`.
  - `apply_scanner_runtime_config`.
  - `refresh_scanner_runtime_config_from_global`.
  - `current_scanner_runtime_config`.
  - `scanner_runtime_config_status`.
  - Accessors such as `scanner_cycle_interval`, `scanner_start_delay`, `scanner_bitrot_cycle`, `scanner_cache_save_timeout`, concurrency getters, and alert threshold getters.

## Control Flow

Validation first rejects non-default scanner or heal config targets, then validates persisted values independent of environment overrides. This prevents an invalid saved config from being hidden by a valid environment variable.

Resolution follows a consistent precedence pattern. Environment variables win first; persisted scanner config is next; compatibility locations such as scanner bitrot config may be used where supported; defaults and speed-derived values fill the rest. Cycle interval resolution is more nuanced: explicit `RUSTFS_SCANNER_CYCLE` wins, then persisted scanner cycle, then explicit start delay, then deployment default cycle override, then the selected speed preset's cycle interval.

Budget settings interpret zero counts as disabled. Cache save timeout is clamped to at least one second. Bitrot cycle parsing supports immediate deep scan (`0`, `true`, `on`, `yes`), disabled periodic deep scan (`false`, `off`, `no`, `disabled`), or a seconds value.

`apply_scanner_runtime_config` validates persisted config, resolves values, updates `SCANNER_SLEEPER` with delay/max-wait/idle/yield settings, and stores the resolved config behind the RwLock. `refresh_scanner_runtime_config_from_global` repeats that process from the global server config at scanner cycle boundaries.

## State and Persistence Behavior

This module does not persist config itself; it reads `rustfs_config::server_config` values and process environment. The resolved config is cached process-locally in `SCANNER_RUNTIME_CONFIG`. Runtime refreshes can alter sleeper behavior without restarting the scanner. `scanner_runtime_config_status` serializes both values and source tags for observability.

The default cycle override is process-global and is used by `scanner.rs` to apply single-disk defaults. It is stored as an atomic seconds value where zero means no override.

## Dependencies and Integration Points

- Pulls config keys, defaults, and `ScannerSpeed` from `rustfs_config`.
- Updates `sleeper::SCANNER_SLEEPER`, so pacing decisions in scanner traversal observe resolved runtime config.
- Consumes `ScannerCycleBudgetConfig` from `scanner_budget.rs`.
- Used by `scanner.rs` for cycle interval, bitrot cycle, start delay, scan budget, and cache save timeout.
- Used by `data_usage_define.rs` for cache-save timeout.
- Emits structured parse warnings through `tracing`.

## Risks and Edge Cases

- Environment parsing is intentionally more forgiving for some env values than persisted config parsing. For example invalid env delay falls back to the speed-derived delay but still reports source as env; operators need logs/status to notice the fallback.
- `SCANNER_RUNTIME_CONFIG` write failures are silently ignored in `apply_resolved_runtime_config` if the RwLock is poisoned/unavailable; callers receive `Ok` after sleeper update even if cached status is not updated.
- The default cycle override is global mutable process state. Tests use serial execution around environment/default mutations; production code must avoid racing updates except during startup/default configuration.
- Persisted config target validation only allows default targets. Adding per-target scanner config would require explicit design changes here.
- Scanner compatibility config for bitrot is lower precedence than heal config, but still reported distinctly as `scanner_compat_config`; consumers should not assume all config-sourced values are from the same subsystem.

## Test Signals

Tests cover env-over-config precedence, persisted value validation despite env overrides, heal bitrot precedence over scanner compatibility config, source reporting, invalid speed/delay/target rejection, bounded delay parsing, env fallback for excessive delay, cache timeout status, pacing override status, and subsecond max-wait reporting. The tests use `serial_test` and `temp_env`, which signals the global environment/config state is intentionally mutable and must be isolated.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/runtime_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/scanner.rs -->
# sources/object-store/rustfs/crates/scanner/src/scanner.rs

## Purpose

`scanner.rs` owns the scanner runtime loop. It configures deployment defaults, decides startup and inter-cycle delays, elects a single scanner through a namespace lock, runs namespace scans with budget cancellation, persists cycle/background-heal/data-usage state, and emits scanner metrics. It is the orchestration layer above cache definitions, folder scanning, scanner IO, runtime config, and sleeper behavior.

## Important APIs, Types, and Functions

- Runtime setup and loop:
  - `init_data_scanner(ctx, storeapi)` configures defaults, refreshes runtime config, and spawns the background scanner task.
  - `run_data_scanner(ctx, storeapi)` acquires the leader lock, restores cycle state, runs one immediate cycle, then repeats after randomized delays.
  - `run_data_scanner_cycle` performs one scan cycle and handles metrics, background heal mode, budget partials, and state persistence.
- Timing helpers:
  - `randomized_cycle_delay_for` applies +/-10% jitter with a one-second floor.
  - `initial_scanner_delay_for_startup` skips startup delay when there are buckets and either the usage cache is cold or active replication rules exist.
  - `read_data_usage_config_for_startup`, `persisted_usage_cache_is_cold_for_startup`, and `initial_scanner_startup_usage_state` inspect existing usage state before deciding startup delay.
- Default configuration:
  - `ScannerMaintenanceFeatures` records lifecycle/replication/inspection-failure signals.
  - `detect_scanner_maintenance_features` scans bucket lifecycle and replication configs.
  - `configure_scanner_defaults` applies single-disk defaults: slowest speed and a 24-hour cycle only when no maintenance feature requires regular scans.
- Background heal:
  - `BackgroundHealInfo` serializes bitrot scan start time/cycle and current scan mode.
  - `read_background_heal_info` and `save_background_heal_info` persist this JSON state.
  - `get_cycle_scan_mode`, `background_heal_info_for_scan_start`, `should_reset_bitrot_start`, and `background_heal_info_for_scan_complete` choose and record normal vs deep healing.
- Persistence:
  - `store_data_usage_in_backend` receives `DataUsageInfo` snapshots and writes `.usage.json` plus periodic `.bkp`.
  - Cycle state is read/written at `DATA_USAGE_BLOOM_NAME_PATH`; new format stores `next` as eight little-endian bytes followed by marshaled `CurrentCycle`.
- Observability:
  - Emits scan cycle complete/partial metrics, current scan mode, cycle config, and structured logs.
  - Uses `ScannerActivityGuard` around cycle work and backend usage saves.

## Control Flow

Startup calls `configure_scanner_defaults`, initializes the global sleeper, refreshes runtime config, then spawns a loop. Before the first cycle, the spawned task inspects buckets and persisted usage cache. If cache is cold with buckets, or active replication exists with buckets, it skips startup delay; otherwise it sleeps a randomized delay based on explicit start delay or scanner cycle interval.

`run_data_scanner` obtains a write namespace lock on `RUSTFS_META_BUCKET/leader.lock`. Lock creation or contention logs and returns `Ok(())`, so only the elected node proceeds. It restores `CurrentCycle` from `.bloomcycle.bin`, supporting both the old eight-byte `next` format and the newer `next + marshaled CurrentCycle` format. It runs one immediate cycle after lock acquisition, then loops with cancellation-aware randomized sleep.

`run_data_scanner_cycle` refreshes runtime config, records configured cycle/bitrot/budget metrics, publishes current cycle state, reads background heal info, chooses scan mode, and starts a `store_data_usage_in_backend` task receiving `DataUsageInfo` updates from `nsscanner`. It constructs a `ScannerCycleBudget` child token and passes it to `storeapi.nsscanner`. If `nsscanner` returns because a budget elapsed, the cycle is marked partial, source/reason metrics are emitted, current scan mode is cleared, and `cycle_info.current` is reset to idle without advancing `next`. Other scan errors emit failed completion metrics. Successful cycles emit success metrics, complete deep-scan background-heal state if needed, advance `cycle_info.next`, append completion time, trim recent completions, publish metrics, and persist cycle state.

`store_data_usage_in_backend` drains usage snapshots from a channel until closed or canceled. For each snapshot it reads the existing persisted `.usage.json`; if both timestamps exist and the incoming snapshot is not newer, it skips saving to avoid overwriting fresher state. Every eleventh attempt writes a backup first, then writes the main JSON and refreshes in-memory bucket usage on success.

## State and Persistence Behavior

Process-local state includes runtime config, scanner activity, current metrics, and background task lifetimes. Persisted scanner state includes:

- `.usage.json`: JSON `DataUsageInfo`, updated from scanner output.
- `.usage.json.bkp`: periodic backup written by `store_data_usage_in_backend`.
- `.bloomcycle.bin`: cycle number and marshaled `CurrentCycle`.
- `.background-heal.json`: JSON `BackgroundHealInfo`, skipped entirely for ErasureSD setups.

Partial budget cycles do not advance `cycle_info.next`; they publish idle current-cycle state and rely on lower-level partial cache/checkpoint behavior to resume usage work. Completed cycles retain only a bounded list of recent completion timestamps using `data_usage_update_dir_cycles()`.

## Dependencies and Integration Points

- Depends on `runtime_config.rs` for start delay, cycle interval, bitrot cycle, budget config, and runtime refresh.
- Depends on `scanner_budget.rs` to bound cycles by duration/object/directory budgets.
- Depends on `scanner_io::ScannerIO` for `storeapi.nsscanner`.
- Depends on `scanner_folder` for update-cycle retention and heal selection probability.
- Uses `rustfs_ecstore` for bucket listing, metadata locks, lifecycle/replication configs, config persistence, and `ECStore`.
- Uses `rustfs_common::metrics` for cycle metrics and scan modes.
- Uses `tokio` tasks/channels/timers and `CancellationToken`.
- Lifecycle integration tests call `init_data_scanner`, and unit tests in this file exercise timing, budget mapping, stale snapshot protection, and background-heal state transitions.

## Risks and Edge Cases

- Lock contention and lock creation errors return `Ok(())`, so external callers may see no error even when this node did not scan.
- Startup delay skips for active replication to recover failed-status objects quickly; incorrect replication feature detection can affect scan latency.
- Cycle state decode failure logs and continues with the parsed `next` prefix or default state, which may lose recent completion history.
- `store_data_usage_in_backend` protects only timestamped snapshots. If timestamps are missing, stale overwrite protection does not apply.
- Backup writes in `store_data_usage_in_backend` are based on attempt count, not elapsed time or data size.
- A budget-elapsed partial cycle returns without awaiting the backend saver task explicitly; channel closure and task completion depend on sender/drop behavior in the scan path.
- Single-disk default cycle behavior depends on lifecycle/replication inspection. Inspection failure preserves regular speed-based cycles to avoid missing maintenance work.

## Test Signals

Tests cover randomized delay bounds, startup delay skip/keep cases, cycle budget env configuration, zero budget disabling, budget cancellation/drop behavior, partial reason/source metric mapping, idle marking after partial cycles, stale snapshot preservation, cycle interval precedence, MinIO env aliases, single-disk default cycle decisions, bitrot/deep-scan mode selection, background-heal start/complete transitions, and recent completion retention. These tests signal that operational timing, partial-cycle semantics, and persistence ordering are the highest-risk contracts.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/scanner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/scanner_budget.rs -->
# sources/object-store/rustfs/crates/scanner/src/scanner_budget.rs

## Purpose

`scanner_budget.rs` implements per-cycle scanner budgets. It turns optional runtime limits for duration, object count, and directory count into a cancellation token that scanner traversal can observe. It also records the first budget reason that stopped a cycle.

## Important APIs, Types, and Functions

- `ScannerCycleBudgetConfig` contains optional `max_duration`, `max_objects`, and `max_directories`.
- `ScannerCycleBudgetReason` identifies `Runtime`, `Objects`, or `Directories` and maps to/from compact `u8` codes.
- `ScannerCycleBudget` contains:
  - A child `CancellationToken`.
  - An atomic reason code.
  - Configured limits.
  - Atomic counters for scanned objects and started directories.
- Main methods:
  - `new(parent, config) -> Arc<Self>` creates the child token and spawns a duration timer when needed.
  - `token()` clones the child token.
  - `budget_elapsed()` and `reason()` expose stop state.
  - `max_duration`, `max_objects`, `max_directories` expose configured limits for logging/metrics.
  - `try_start_directory()` increments directory starts and rejects/cancels once the limit is exceeded.
  - `record_object_scanned()` increments object count and cancels once the limit is reached.

## Control Flow

The budget starts uncanceled with reason code `BUDGET_REASON_NONE`. If a runtime duration is configured, `new` spawns a Tokio task that races parent cancellation, child cancellation, and `sleep(duration)`. If the sleep wins, it atomically records `Runtime` and cancels the child token.

Traversal code calls `try_start_directory` before entering directories and `record_object_scanned` after object scans. Directory budget allows exactly `max_directories` starts; the first attempt beyond the limit records `Directories`, cancels the child token, and returns false. Object budget cancels when the count reaches `max_objects`. `compare_exchange` ensures only the first budget reason wins if multiple limits are reached concurrently.

Dropping `ScannerCycleBudget` cancels the child token, which releases waiters without marking a budget reason.

## State and Persistence Behavior

Budget state is entirely in memory and per cycle. The child cancellation token is derived from the scanner parent token, so parent shutdown cancels budgeted work. No state is persisted by this module. `scanner.rs` reads the final reason for metrics and partial-cycle logging, while lower-level scanner traversal uses the token to stop work.

## Dependencies and Integration Points

- Uses `tokio::time::sleep` and `tokio_util::sync::CancellationToken`.
- Config is resolved in `runtime_config.rs`.
- `scanner.rs` creates a budget for each cycle and maps reasons to common metrics.
- `scanner_folder.rs` and `scanner_io.rs` observe the token and call directory/object budget methods while scanning.

## Risks and Edge Cases

- Counters use relaxed atomics; this is appropriate for budget telemetry/cancellation but not for exact cross-thread sequencing.
- Object budget cancels when `objects >= max_objects`, whereas directory budget rejects after `directories > max_directories`. That means object limit permits exactly N scanned objects and then cancels, while directory limit returns false for the N+1 start.
- Duration timer is a spawned task per budget. Dropping the budget cancels its token and should let the timer task exit, but excessive short-lived budgets still create task churn.
- Because only the first reason wins, later exceeded limits are not visible in metrics.

## Test Signals

Unit tests assert runtime duration cancels the child token and records `Runtime`, object budget cancels after reaching the configured limit, and directory budget rejects the first directory beyond the configured limit while recording `Directories`. `scanner.rs` adds tests for drop cancellation and metric reason/source mapping.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/scanner_budget.rs -->
