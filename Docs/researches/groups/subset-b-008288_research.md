# subset-b-008288 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/scanner_folder.rs -->
# sources/object-store/rustfs/crates/scanner/src/scanner_folder.rs

## Purpose
Implements the recursive bucket data scanner used by RustFS to build and refresh `DataUsageCache` entries from disk layout. The file owns folder traversal, object accounting, lifecycle and replication side effects, scanner-driven heal admission, checkpoint/resume handling for partial scans, failed-object backoff, compaction of large data-usage trees, and scanner alert metrics for pathological object or folder layouts.

## Important APIs, types, and functions
- `scan_data_folder(...)` is the entry point called by disk-level scanner IO. It validates the bucket cache name, builds a `FolderScanner`, scans the bucket root, finalizes cache timestamps and checkpoints on success, and returns `ScannerError::PartialCache` with progress when cancellation or budget exhaustion interrupts a scan after useful work.
- `FolderScanner` carries the scan root, old/new/update `DataUsageCache` instances, healing mode and probability, failed-object TTL state, disk quorum, update channel, current-path updater, cycle budget, local disk handle, and `DynamicSleeper`.
- `FolderScanner::scan_folder(...)` is the recursive traversal engine. It reads directory entries, distinguishes existing and new cached folders, computes object size summaries through `ScannerIODisk::get_size`, recursively scans child folders, compacts cache subtrees, emits partial updates, tracks resume hints, and optionally scans abandoned cache children for healing.
- `ScannerItem` describes one filesystem item being interpreted as object metadata. It stores bucket, prefix, object name, file type, lifecycle/replication configs, healing flags, and helpers such as `object_path`, `transform_meta_dir`, `apply_actions`, `heal_actions`, `heal_replication`, `enqueue_heal`, and alerting helpers.
- `CachedFolder`, `QueuedFolder`, `FolderResumeMatch`, `FolderResumeOrder`, and `FolderScanSource` support deterministic child ordering and resume semantics across new and existing folders.
- Helpers such as `data_usage_update_dir_cycles`, `heal_object_select_prob`, `scanner_yield_every_n_objects`, `should_yield_after_object`, `should_log_failed_object`, `should_alert_excessive_versions`, `set_scan_checkpoint`, and `checkpoint_reason_from_budget` bind runtime configuration and budget state to scanner behavior.
- Heal admission helpers build bucket/object `HealChannelRequest`s, send low-priority object heals or required high-priority abandoned-child heals, map admission outcomes to metrics, and treat high-priority rejection as a scanner error.

## Control flow
`scan_data_folder` creates a current-path updater for the bucket disk path, chooses whether healing is eligible based on erasure mode and cache `skip_healing`, calculates heal probability and disk quorum, and then calls `scan_folder` on the bucket root. A successful scan force-compacts the cache, stamps `last_update`, preserves `next_cycle`, clears old resume hints/checkpoints, records checkpoint clearing metrics when needed, and closes the current-path updater. On cancellation, it preserves completed root progress when present, compacts it, sets a checkpoint reason from the budget, and returns a partial cache.

`scan_folder` starts by enforcing cancellation and directory budget limits. It remembers whether the target entry was already compacted, collects abandoned children from the old cache, opens the physical directory, and iterates entries. Missing directories, entries disappearing during traversal, symlink loops, and symlinked directories are treated as skip/warn conditions rather than fatal scanner failures. Directories become `CachedFolder`s split into existing or new work depending on old-cache membership. Files become `ScannerItem`s and are passed to the local disk `get_size` implementation; skip-file errors are ignored, while other failures increment per-entry `failed_objects`, add the path to `new_cache.info.failed_objects`, and are sampled for logging.

Object accounting accumulates `SizeSummary` into the current `DataUsageEntry`, increments object counts, records budget object progress, sleeps proportionally through `DynamicSleeper`, and periodically yields plus sends partial updates based on the configured object interval. In erasure mode, finding object metadata stops descent into subdirectories under that object. Once the directory is read, child folders are optionally compacted when there are too many children, ordered according to checkpoint or legacy resume hints, and recursively scanned. Existing compacted folders are reused on cycles that do not require refresh, while refreshed compacted folders get a reduced object-heal probability divisor.

If old-cache children were abandoned and healing remains enabled, the scanner uses `list_path_raw` over the disk set to find partially agreed metadata and queues high-priority bucket/object heal requests for missing or inconsistent objects. Any found abandoned object subtree is rescanned so the rebuilt cache includes it. Finally, the folder result is written into `new_cache`, small or object-only subtrees may be flattened into compacted entries, child sets are reduced past the compaction threshold, and `update_cache` is synchronized for live progress reporting.

`ScannerItem::apply_actions` runs after metadata has been decoded into `ObjectInfo` versions. Without lifecycle config it only performs heal and replication accounting for each version. With lifecycle config it evaluates `Evaluator` events, dispatches expiry or transition work, batches noncurrent version deletes through `GLOBAL_ExpiryState.enqueue_by_newer_noncurrent`, accounts retained versus expired sizes depending on enqueue success, queues replication heals, and emits excessive version/count alerts on retained versions.

## State and persistence behavior
The scanner works from an old persisted `DataUsageCache` and constructs a new cache, while `update_cache` is a streaming snapshot for partial progress. The new cache persists folder entries keyed by `DataUsageHash`, root metadata such as `last_update`, `next_cycle`, lifecycle/replication config references, `scan_resume_after`, `scan_checkpoint`, and `failed_objects`. Failed object entries are retained with timestamps so repeated broken metadata is skipped for `RUSTFS_DATA_USAGE_FAILED_OBJECT_TTL_SECS`, capped by `RUSTFS_DATA_USAGE_FAILED_OBJECTS_MAX`.

Partial scans persist progress by returning `ScannerError::PartialCache`; callers save that partial cache. Checkpoints use `DATA_USAGE_SCAN_CHECKPOINT_VERSION` plus a resume path and reason, while successful scans clear both checkpoint and legacy resume fields. Compaction can replace a subtree with a flat `DataUsageEntry`, reducing memory and serialized cache size for small, object-only, or extremely broad trees.

Lifecycle and heal behavior also mutates external queues: expiry work is enqueued into lifecycle expiry state, transition work into lifecycle transition handling, free versions into `GLOBAL_ExpiryState`, replication repair into bucket replication queues, and heal candidates into the global heal channel. These are side effects of scanning rather than changes to the data-usage cache itself.

## Dependencies and integration points
This file is tightly coupled to `data_usage_define` cache types, `scanner_budget`, `scanner_io::ScannerIODisk`, and `sleeper::DynamicSleeper`. It integrates with RustFS common metrics/current-path reporting, heal admission channel, EC store lifecycle evaluator and expiry/transition operators, bucket versioning and replication configuration, metacache raw listing, disk APIs, storage errors, object metadata `ObjectInfo`, `rustfs_filemeta` metadata resolution, and path helpers for bucket/object parsing.

## Risks and edge cases
The recursion is complex and depends on correct cache hash/parent relationships; bugs can lose children, double-count compacted entries, or resume at the wrong point after partial scans. The abandoned-child heal branch spawns a raw listing task and drains three channels, so missed close/cancel cases can hang scans or over-queue high-priority heals. Scanner side effects are best effort for low-priority heals and lifecycle queues; accounting deliberately differs depending on enqueue success, so queue saturation changes data-usage totals for expiring versions. Failed-object caching prevents retry storms but can hide recovery until TTL expiry. The object heal selection formula divides by `object_heal_prob_div`, so that divisor must stay nonzero. Alert thresholds and compaction thresholds are runtime-sensitive and can create noisy logs or large cache entries if misconfigured.

## Test signals
The in-file tests cover failed-object TTL and pruning, replication-stat eligibility, lifecycle action accounting only on enqueue success, pending accounting semantics, replication and heal admission metric mapping, alert thresholds from environment, yield interval behavior, budget reason to checkpoint reason mapping, resume-order rotation and stale hint detection, failed-object log sampling, inline-heal compatibility env parsing, heal request construction, deep-scan cooldown downgrade, high-priority admission error text, ignored symlink directories, abandoned-child listing completion, directory-budget partial scans, compacted-parent partial updates, partial cache generation on budget cancel, invalid checkpoint ignore metrics, resume hints across new and existing folders, and successful scan clearing of resume state.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/scanner_folder.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/scanner_io.rs -->
# sources/object-store/rustfs/crates/scanner/src/scanner_io.rs

## Purpose
Provides the scanner IO orchestration layer that connects the high-level object store, erasure sets, individual disks, and folder scanner. It schedules scanner work across pools, sets, disks, and buckets with configurable concurrency limits, streams merged data-usage updates, loads and saves scanner cache files, and translates disk scans into complete or partial outcomes.

## Important APIs, types, and functions
- `ScannerIO` is implemented for `ECStore` and exposes `nsscanner(ctx, budget, updates, want_cycle, scan_mode)`, the top-level scanner cycle entry point.
- `ScannerIOCache` is implemented for `SetDisks` and exposes `nsscanner_cache(...)`, which scans all buckets for one erasure set and publishes `DataUsageCache` snapshots.
- `ScannerIODisk` is implemented for `Disk` and exposes `nsscanner_disk(...)` plus `get_size(ScannerItem)`.
- `ScannerDiskScanOutcome` differentiates `Complete(DataUsageCache)` from `Partial(DataUsageCache)`, allowing callers to persist progress when budgets or cancellation stop a scan.
- Concurrency and metrics helpers include `scanner_concurrency_limit`, `scanner_max_concurrent_set_scans`, `scanner_max_concurrent_disk_scans`, queue/active gauge recorders, wait histograms, `SetScanActiveGuard`, `DiskBucketScanActiveGuard`, `DiskBucketScanGaugeReset`, and `BucketDriveFailureGuard`.
- Cache helpers include `cache_root_entry_info`, `apply_bucket_result_to_cache`, `bucket_result_should_publish_immediately`, `send_cache_root_entry_info`, and `persist_and_publish_cache_snapshot`.
- `SCANNER_SKIP_FILE_ERROR` is the sentinel string used by disk size collection to signal that a filesystem entry should be skipped without counting as a scanner failure.

## Control flow
`ECStore::nsscanner` lists buckets, resets scanner gauges and publishes an empty update when there are no buckets, calculates the number of erasure sets, resolves the set-scan concurrency limit, and spawns one scanner task per set behind a semaphore. Each set task records permit wait time, updates queued/active gauges, invokes `SetDisks::nsscanner_cache`, and records the first non-cancelled set error while allowing other sets to finish. A separate updater task periodically merges available set caches into a `DataUsageInfo` stream every 30 seconds and sends a final merge when all set tasks finish. The result is successful if any set produced a cache with `last_update`; otherwise the first set error is returned.

`SetDisks::nsscanner_cache` obtains online disks and healing state, loads the previous root cache from `DATA_USAGE_CACHE_NAME`, initializes a new root cache, shuffles bucket order, and queues uncached buckets before cached buckets so missing data is discovered early. It preloads existing bucket entries into the root cache and tracks which preloaded buckets have already been published. A cache publisher task saves and sends snapshots periodically, immediately publishes first results for not-yet-published buckets, and saves a final root cache with `next_cycle = want_cycle` when all bucket results are done.

For each online disk, a worker receives bucket jobs from a shared receiver, waits for the disk-scan semaphore, loads the bucket-specific cache at `bucket/.usage-cache`, patches cache identity and healing flags, and spawns a small update-forwarding task that converts folder-level `DataUsageEntry` updates into root-level `DataUsageEntryInfo` messages. It then calls `Disk::nsscanner_disk`. Complete outcomes publish the bucket root and save the bucket cache. Partial outcomes save the partial bucket cache, publish its root entry even after cancellation, and continue to the next bucket. Non-cancelled scan errors are logged; if a prior cache changed, it is saved defensively.

`Disk::get_size` accepts only `xl.meta` paths, reads metadata using disk APIs, maps missing object/version metadata to the skip sentinel, transforms the scanner item from metadata-path form to object-path form, loads `FileMeta`, resolves file info versions, creates `ObjectInfo` values, initializes tier stats, fetches object lock config, delegates lifecycle/heal/replication accounting to `ScannerItem::apply_actions`, enqueues free versions for expiry, and returns a `SizeSummary`.

`Disk::nsscanner_disk` records drive scan metrics, fetches lifecycle and replication config for the bucket, resolves the object-store handle and disk-set inventory needed by folder healing, identifies the local disk, and calls `scan_data_folder` with the global `SCANNER_SLEEPER`. It maps success to `Complete`, `ScannerError::PartialCache` to `Partial`, and other errors to storage errors while emitting complete or partial drive metrics and using a failure guard to count failed drives.

## State and persistence behavior
There are two persisted cache layers. The set/root cache is stored as `DATA_USAGE_CACHE_NAME` and aggregates bucket root entries for a set. Each bucket cache is stored under `bucket/DATA_USAGE_CACHE_NAME` and contains the detailed data-usage tree for that bucket. Periodic and immediate snapshot persistence ensures consumers see progress during long scans. Partial bucket caches are explicitly saved so budget-limited scans can resume from checkpoints generated by `scanner_folder.rs`.

Runtime state includes queued/active scan gauges, first-error tracking, merged set results, publish-once tracking for bucket entries, `last_update` timestamps for detecting changed snapshots, and per-bucket cache identity fields. Healing state from `SetDisks::get_online_disks_with_healing` is copied into bucket cache info so folder scans can suppress object healing when a disk set is already healing.

## Dependencies and integration points
This layer integrates `ECStore`, `SetDisks`, `Disk`, `ObjectIO`, bucket listing APIs, metadata-system lookups for lifecycle, object lock, and replication config, bucket target lookup, global tier config, storage-class constants, disk inventory through `StorageAdminApi`, object-store handle resolution, `FileMeta`, bucket versioning, lifecycle expiry state, metrics emitters, Tokio semaphores/channels/tasks, cancellation tokens, and `scan_data_folder` from `scanner_folder.rs`.

## Risks and edge cases
The orchestration relies on spawned tasks and channels closing in the right order; leaked senders or a hung disk scan can delay final snapshot publishing. The shared bucket receiver is protected by a mutex, so workers fetch one bucket at a time before doing concurrent scans. Concurrency limits must handle zero available work; the code resets gauges in empty paths, but any future early return should preserve that hygiene. A set scan is considered successful if any result has `last_update`, which intentionally tolerates partial set failures but can hide degraded coverage unless metrics and logs are monitored. `SCANNER_SKIP_FILE_ERROR` is string-matched across modules, so changing the sentinel text without a stronger typed error would break skip classification. `get_size` depends on `xl.meta` path shape and bucket versioning lookups; malformed metadata is skipped or logged depending on failure stage.

## Test signals
Tests verify first-error preservation, final scanner result success when any set succeeds, final error when all sets fail, concurrency limit capping and zero-work behavior, saturating atomic decrements, environment-controlled set and disk concurrency limits, cross-platform `xl.meta` path detection, missing metadata returning the skip sentinel, root-entry flattening, partial root entry sending after cancellation, bucket-result cache replacement and immediate/deferred publish behavior, and publish-once tracking for preloaded and newly discovered buckets.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/scanner_io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/sleeper.rs -->
# sources/object-store/rustfs/crates/scanner/src/sleeper.rs

## Purpose
Defines scanner throttling for RustFS data scans. It centralizes scanner speed presets, idle-mode enablement, runtime refresh from environment/configuration, proportional work-time backoff, fixed folder-level pacing, yield interval configuration, and metrics reporting for throttle configuration and actual sleeps.

## Important APIs, types, and functions
- `SCANNER_SLEEPER` is a global `LazyLock<DynamicSleeper>` initialized from `RUSTFS_SCANNER_SPEED` and `RUSTFS_SCANNER_IDLE_MODE`; it records throttle config at initialization.
- `SCANNER_IDLE_MODE` is an `AtomicBool` gate that lets runtime configuration skip all scanner sleeps when disabled.
- `DynamicSleeper` wraps shared `SleeperParams` containing a sleep factor and max sleep under `RwLock`s. Clones share the same mutable throttle parameters.
- `DynamicSleeper::sleep_folder()` sleeps for `MIN_SLEEP * factor`, capped by max sleep, for folder-level gaps.
- `DynamicSleeper::timer()` returns a `SleepTimer`; `SleepTimer::sleep()` computes `elapsed_work_time * factor`, clamps it to at least `MIN_SLEEP` and at most max sleep, then sleeps.
- `DynamicSleeper::update`, `refresh_from_env`, and `update_from_runtime_config` update throttle parameters and idle mode, then record metrics.
- `scanner_default_speed`, `set_scanner_default_speed`, `scanner_speed_from_env_or_default`, `scanner_env_config`, and speed-code helpers manage the default speed preset and env parsing.
- `scanner_yield_every_n_objects()` reads `RUSTFS_SCANNER_YIELD_EVERY_N_OBJECTS` with the RustFS default.

## Control flow
At startup, `SCANNER_SLEEPER` reads the configured scanner speed and idle mode, stores idle mode in the global atomic, builds a `DynamicSleeper` using the speed preset's `sleep_factor` and `max_sleep`, and records the throttle config including the current yield interval. Folder scanning calls `sleep_folder` before opening or processing a folder. Object scanning creates a timer before metadata work and calls `SleepTimer::sleep` after work or after handled object-size failures. Both sleep paths first check `SCANNER_IDLE_MODE`, then skip sleep when factor is zero or max sleep is zero.

Runtime reconfiguration can call `refresh_from_env` or `update_from_runtime_config`; both replace the shared factor/max-sleep values so all clones see new pacing. `update_from_runtime_config` also writes idle mode and records the supplied yield interval, making it the bridge from higher-level scanner runtime config into throttle metrics.

## State and persistence behavior
The file has no persistent storage. State is process-local: `SCANNER_DEFAULT_SPEED_PRESET` stores a default speed code, `SCANNER_IDLE_MODE` stores whether sleeping is enabled, and each `DynamicSleeper` stores shared `RwLock`-protected throttle parameters. Sleep durations are reported to `global_metrics().record_scanner_throttle_sleep`, and configuration is reported through `record_scanner_throttle_config`.

## Dependencies and integration points
It depends on `rustfs_config` for speed presets, default idle mode, default yield interval, and environment variable names; `rustfs_utils` for typed env reads; `rustfs_common::metrics::global_metrics`; Tokio time for async sleeps; and standard atomics/locks for low-overhead shared runtime state. `scanner_folder.rs` uses `DynamicSleeper` directly, while `scanner_io.rs` passes the global `SCANNER_SLEEPER` into disk folder scans.

## Risks and edge cases
Because `RwLock` poisoning is recovered through `into_inner`, a panic while updating parameters will not permanently block scans, but it may expose partially updated factor/max-sleep pairs if future edits split updates differently. `SCANNER_IDLE_MODE` is global rather than per-sleeper, so one runtime refresh changes sleep enablement for all scanner users. `SleepTimer::sleep` enforces a minimum 1 ms delay for any nonzero factor, even for very fast operations, while `sleep_folder` can be below or equal to that computed base only after factor multiplication and max-sleep capping. Tests that change environment and global defaults require serialization to avoid cross-test contamination.

## Test signals
Tests cover preset factors and max sleeps for fastest/default/slowest, `update` changing parameters, explicit runtime-config updates applying factor/max/idle mode, env refresh applying speed and idle mode, default-speed override when speed env is unset, fastest mode never sleeping, and idle-mode-off skipping sleep. The tests use `serial_test`, `temp_env`, and Tokio paused time for deterministic global/env behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/src/sleeper.rs -->
