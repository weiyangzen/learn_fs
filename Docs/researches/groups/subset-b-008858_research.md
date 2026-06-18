# subset-b-008858 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/region.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/region.rs

Purpose: this raftstore worker handles region-local background jobs that must not run on the hot raft peer path: applying received snapshots, destroying stale data ranges, and asynchronously clearing peer metadata. It is a bridge between peer storage state, snapshot files, RocksDB range deletion/ingestion, coprocessor snapshot hooks, and raftstore routing callbacks.

Important APIs and types:
- `Task` has `Apply`, `Destroy`, and `ClearPeerMeta`. `Apply` carries a region id, peer id, atomic job status, and enqueue time. `Destroy` carries an encoded data range. `ClearPeerMeta` carries peer/region raft state plus merge/replication context and a lock over pending peer creation.
- `PendingDeleteRanges` is a `BTreeMap<start_key, StalePeerInfo>` that tracks logically destroyed ranges until old engine snapshots have drained. It exposes overlap draining, stale iteration by oldest snapshot sequence, and removal by start key.
- `Runner<EK, ER, R>` owns engine handles, `StoreMeta`, `SnapManager`, `CoprocessorHost`, router, pending apply queue, and pending delete ranges. It implements both `Runnable` and `RunnableWithTimer`.

Control flow:
- `run(Task::Apply)` optionally calls `pre_apply_snapshot`, appends the task to `pending_applies`, updates snap manager pending count, and calls `handle_pending_applies(false)`.
- `handle_pending_applies` preserves apply order and only runs when ingestion is unlikely to cause write stall and `KvEngine::can_apply_snapshot` accepts the current batch. Delayed tasks are retried from the timer path.
- `apply_snap` reads `RegionLocalState` and `RaftApplyState` from `CF_RAFT`, cleans overlapping data, registers the snapshot as applying, applies snapshot SSTs through `Snapshot::apply`, invokes coprocessor post hooks, writes the region state back as `PeerState::Normal`, deletes snapshot raft state, and synchronously commits the metadata update.
- `run(Task::Destroy)` inserts a delayed pending range and attempts stale cleanup. `clean_stale_ranges` deletes files first for ranges older than the oldest engine snapshot sequence, then deletes all keys and blobs, and finally removes pending range entries.
- `run(Task::ClearPeerMeta)` delegates to `clear_meta_in_kv_and_raft`; on success it sends `SignificantMsg::ReadyToDestroyPeer`, and on error it panics to avoid unsafe recreation/deletion races.

State and persistence behavior:
- Snapshot apply persistence is in `CF_RAFT`: region state and snapshot raft state are updated with `WriteOptions::sync(true)`, making the transition to normal durable before notifying peers.
- Snapshot data application mutates user CFs through snapshot ingestion/deletion strategies. Overlapping pending delete ranges are merged into the cleanup range before applying a new snapshot, protecting against stale range deletion after new data is installed.
- Delayed deletion state is only in-memory. It is an optimization and safety delay, not durable metadata; actual region/peer metadata destruction is persisted by `clear_meta_in_kv_and_raft`.
- Physical deletion uses multiple strategies: `DeleteFiles` for stale SST/blob cleanup when safe by snapshot sequence, `DeleteByRange` when configured, `DeleteByKey` for lock CF or forced cleanup, and writer/ingestion cleanup as a fallback.

Dependencies and integration points:
- Depends on `engine_traits` for KV/raft engines, write batches, range deletion, sequence numbers, and write-stall checks.
- Integrates with `SnapManager` for snapshot lifecycle registration/deregistration and temp ingest paths.
- Uses `CoprocessorHost` hooks around snapshot application: pre, post, committed, and cancel paths.
- Routes completion through `RaftStoreRouter`: `CasualMessage::SnapshotApplied` for apply results and `SignificantMsg::ReadyToDestroyPeer` for metadata clear completion.
- Scheduled by peer storage and store workers via the re-exported `RegionTask`/`RegionRunner`.

Risks and edge cases:
- Range deletion ordering is critical: overlap cleanup must precede snapshot application or stale delayed deletion could remove newly applied data.
- Several error paths intentionally panic or unwrap, especially durable apply metadata writes and peer metadata cleanup failures, because continuing can resurrect peers or corrupt overlapping regions.
- `PendingDeleteRanges::insert` panics if overlap remains; callers must drain overlaps first.
- Ingestion pressure can starve snapshot apply until compaction reduces L0 files; timer retry and metrics are the visibility mechanism.
- Delayed delete ranges are in memory, so process restart relies on durable peer metadata/region states rather than this optimization state.

Test signals:
- `test_pending_delete_ranges` covers overlap draining, stale iteration, insertion, and removal ordering.
- `test_stale_peer` validates delayed destruction waits for old snapshots and then deletes stale keys without deleting the end bound.
- `test_pending_applies` exercises write-stall deferral, snapshot generation/apply integration, coprocessor pre/post hooks, pending queue order, destroy delay behind apply pressure, and failpoint-controlled delayed apply.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/region.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/snap_gen.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/snap_gen.rs

Purpose: this worker generates raft snapshots asynchronously from KV snapshots. It offloads snapshot building to a YATP future pool, notifies the requester through a synchronous channel, and nudges raftstore so generated snapshots can be sent.

Important APIs and types:
- `SNAP_GENERATOR_MAX_POOL_SIZE` caps the intended generator pool size.
- `Task<S>::Gen` carries region id, last applied term/state, a KV snapshot, cancellation flag, notifier, load-balance marker, and destination store id.
- `SnapGenContext<EK, R>` captures the engine, snapshot manager, router, and generation start timestamp for the async job.
- `Runner<EK, R, T>` owns the engine, `SnapManager`, router, optional PD client, future pool, and a `tiflash_stores` cache.

Control flow:
- `Runner::run` handles only `Task::Gen`. It decides whether multi-file snapshots are allowed based on the destination store. Non-TiFlash targets can receive multi-file snapshots; TiFlash or unknown/error cases disable that optimization.
- Store label lookup is cached by `to_store_id`; the PD lookup treats lookup failure as TiFlash-like to avoid sending unsupported snapshot formats.
- The runner increments snapshot metrics, builds a `SnapGenContext`, records queue wait time, and spawns `ctx.handle_gen` into the future pool.
- `handle_gen` checks cancellation before doing I/O, sets the I/O type to load-balance or replication, calls `generate_snap`, updates success/failure/abort counters, and records duration.
- `generate_snap` calls `store::do_snapshot`, optionally triggers failpoints, tries to send the resulting raft snapshot to the notifier, then sends `CasualMessage::SnapshotGenerated` to the region router.

State and persistence behavior:
- This file does not persist raft metadata directly. Persistence is delegated to `store::do_snapshot` and `SnapManager`, which create snapshot files under the snapshot manager directory.
- `UnixSecs::now()` is captured at scheduling time and passed into snapshot creation, likely for snapshot metadata/file lifecycle.
- Cancellation is cooperative and checked before snapshot generation starts; there is no mid-generation cancellation in this file.

Dependencies and integration points:
- Depends on `engine_traits::KvEngine` for the source snapshot type.
- Uses `pd_client::PdClient` to inspect target store labels and avoid unsupported multi-file snapshots for TiFlash.
- Uses `file_system::WithIoType` for I/O classification.
- Integrates with raftstore via `CasualRouter` and `CasualMessage::SnapshotGenerated`; callers in apply/peer paths receive the snapshot through `SyncSender<RaftSnapshot>`.

Risks and edge cases:
- If the notifier channel is closed, generation is considered successful and only logged, because leadership may have changed and heartbeat can retry.
- Future-pool spawn failure increments failure metrics but does not notify the requester directly.
- PD label lookup failure disables multi-file snapshots for that target, a safe but possibly slower fallback.
- The `tiflash_stores` cache has no explicit invalidation in this file; store label changes may not be observed until runner restart.

Test signals:
- This file has no local test module. It is indirectly covered by `region.rs` snapshot apply tests, which schedule `SnapGenTask::Gen`, receive generated snapshots, copy them into receiving snapshots, and then apply them.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/snap_gen.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/split_check.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/split_check.rs

Purpose: this worker evaluates whether a region should split and refreshes region bucket metadata. It supports scan-based and approximate split policies, routes split requests back to the store, updates approximate size/key metadata, and processes compaction events that affect split heuristics.

Important APIs and types:
- `KeyEntry` wraps a key/value-size/CF tuple from merged CF iteration. Its ordering reverses key order so `BinaryHeap` works as a min-heap.
- `MergedIterator` merges iterators from `LARGE_CFS` over an encoded key range.
- `BucketRange`, `Bucket`, and `BucketStatsInfo` manage bucket boundaries, bucket sizes, bucket write-flow deltas, report deltas, and version retention.
- `Task<EK>` includes `SplitCheckTask`, `ApproximateBuckets`, `ChangeConfig`, `CompactedEvent`, and a test-only `Validate`.
- `Runner<EK, S>` owns either a direct engine or tablet registry, a store router implementing `StoreHandle`, a coprocessor host, and an optional region info provider.

Control flow:
- `Task::SplitCheckTask` calls `check_split_and_bucket`. The method resolves the active tablet, computes encoded scan bounds from the whole region or raw request range, builds a `SplitCheckerHost`, and exits if the host says to skip.
- For `CheckPolicy::Scan`, `scan_split_keys` iterates large CFs with `MergedIterator`, feeds entries into the split checker, accumulates accurate region size/key counts for whole-region scans, and optionally builds bucket split keys.
- For `CheckPolicy::Approximate`, the runner asks the host for approximate split keys and approximate bucket keys. On approximate split failure, it falls back to scan mode.
- Valid split keys cause approximate metadata updates and `router.ask_split` with a source string based on split reason. Empty split keys increment ignore metrics.
- `Task::ApproximateBuckets` refreshes bucket metadata without producing split keys when region buckets are enabled.
- `Task::CompactedEvent` maps compaction-declined bytes back to affected regions through `RegionInfoProvider` and reports per-region declined bytes to the router.

State and persistence behavior:
- The worker itself keeps no durable state. It reads live engine/tablet data and emits router updates.
- Bucket metadata state is held by raftstore through `refresh_region_buckets`; `BucketStatsInfo` defines how in-memory bucket stats should update, split, merge, version, and report deltas.
- `BucketStatsInfo::set_bucket_stat` preserves report deltas across metadata replacement and keeps `last_bucket_version` when buckets are cleared.
- Exact scan mode updates approximate size/key metadata with measured values only for whole-region scans, not request subranges.

Dependencies and integration points:
- Depends on coprocessor split checker implementations through `CoprocessorHost::new_split_checker_host` and `SplitCheckerHost`.
- Uses `engine_traits` iterators, tablet registry, compaction event traits, CF lists, and range property helpers.
- Uses PD bucket types (`BucketMeta`, `BucketStat`) and `pdpb::CheckPolicy`/`SplitReason`.
- Integrates with store FSM/peer code that schedules split checks after size/key threshold changes, admin split requests, bucket refreshes, and compaction events.

Risks and edge cases:
- Incorrect key encoding is dangerous: raw request ranges are encoded with transaction `Key` plus `keys::data_key`/`data_end_key`; whole-region ranges use encoded region bounds.
- Bucket update code assumes matching bucket/range lengths for partial refresh and can assert if violated.
- Scan mode can be expensive; it uses no cache fill and load-balance I/O type, but still traverses large CF data.
- Approximate mode must sanitize keys via `strip_timestamp_if_exists` and `is_valid_split_key`; invalid or unordered keys are skipped.
- Compaction declined-byte attribution depends on region info lookup and an empirical `region_split_check_diff / 16` threshold.

Test signals:
- Bucket tests cover version retention, bucket initialization, report-delta reset, split/merge metadata changes, flow preservation across bucket metadata changes, and report behavior.
- Split checker behavior is heavily exercised from coprocessor split check tests in size/key/table/half modules that instantiate `SplitCheckRunner` and schedule `SplitCheckTask`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/split_check.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/split_config.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/split_config.rs

Purpose: this file defines online configuration for load-based region splitting. It centralizes QPS, byte, sampling, balance, contained-range, and CPU overload thresholds used by the auto split controller and read-stat collectors.

Important APIs and types:
- Constants define defaults for detect times, sample count/threshold, QPS and byte thresholds, large-region thresholds, split scores, and CPU overload ratios.
- `get_sample_num()` reads the global `SPLIT_CONFIG` `VersionTrack` if installed, otherwise returns `DEFAULT_SAMPLE_NUM`.
- `SplitConfig` is `Serialize`, `Deserialize`, `PartialEq`, and `OnlineConfig`; fields use kebab-case names. Some deprecated fields are skipped for online config and serialization.
- `SplitConfigManager` wraps `Arc<VersionTrack<SplitConfig>>`, installs it into the global `SPLIT_CONFIG`, implements `ConfigManager`, and dereferences to the underlying `VersionTrack`.

Control flow:
- `SplitConfig::validate` rejects split scores outside `[0,1]`, `sample_num >= qps_threshold`, and CPU ratios outside `[0,1]`.
- `qps_threshold`, `byte_threshold`, and `region_cpu_overload_threshold_ratio` resolve optional values to defaults.
- `optimize_for` fills unset thresholds based on region size. Regions at or above 4096 MiB use higher QPS/byte thresholds and the big-region CPU ratio.
- `SplitConfigManager::dispatch` clones the incoming change, updates the tracked config using generated `OnlineConfig::update`, and logs the accepted change.

State and persistence behavior:
- Configuration is held in memory by `VersionTrack`. Runtime consumers use trackers or `get_sample_num`.
- There is no direct persistence in this file; it participates in TiKV's broader online config infrastructure.
- The global `SPLIT_CONFIG` is a process-wide pointer used by `ReadStats::default` to pick current sample size.

Dependencies and integration points:
- Used by `split_controller.rs` for split decisions and CPU collector registration changes.
- Used by `ReadStats::default` through `get_sample_num`.
- Managed through `online_config::ConfigManager` and re-exported by raftstore worker/store modules.

Risks and edge cases:
- `sample_num` must be lower than QPS threshold; invalid online changes should be rejected before they can make sampling logic ineffective.
- The global config pointer means tests and multiple managers can affect `get_sample_num` process-wide.
- `optimize_for` only fills unset optional fields; explicit user values are preserved even for very large regions.

Test signals:
- `test_static_var_after_config_change` verifies default sample count, manager installation into the static config, online update dispatch, and `get_sample_num` reflecting the updated tracked config.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/split_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/split_controller.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/split_controller.rs

Purpose: this file implements load-based split decision logic. It collects sampled read key ranges, read/write flow, optional per-region CPU records, and thread CPU usage, then chooses split keys or hot key ranges for regions whose load repeatedly exceeds configured thresholds.

Important APIs and types:
- `sample` performs distributed reservoir-style sampling without replacement across multiple key-range providers.
- `Sample` and `Samples` evaluate candidate split keys by counting query ranges left, right, or containing the key, then choose the lowest combined balance/contained score that passes configured limits.
- `Recorder` stores per-region observations over `detect_times`, tracks peer, CPU usage, and hottest key range, and produces a split key when ready.
- `RegionInfo`, `ReadStats`, and `WriteStats` aggregate per-region query counts, sampled read ranges, flow statistics, bucket flow stats, and write query stats.
- `SplitInfo` represents either a concrete split key or a start/end range for half-splitting a hot CPU range.
- `AutoSplitController` owns recorders, tracked `SplitConfig`, thread-capacity settings, recent gRPC poll CPU samples, and optional unified read pool resize notifications.
- `AutoSplitControllerContext` batches incoming stats and periodically drops retained vectors/caches.

Control flow:
- Read-side callers build `ReadStats` by adding query key ranges or flow. Per-region `RegionInfo::add_key_ranges` performs reservoir sampling bounded by current `sample_num`.
- `AutoSplitController::flush` drains batched read stats and CPU stats, records gRPC and unified read pool thread usage, and computes whether gRPC poll/unified read pool are busy.
- For each region, flush skips disabled regions via `SplitValidator`, sums QPS/bytes, observes CPU usage if available, and discards recorders when QPS, bytes, and CPU conditions are all below threshold.
- Hot regions get a `Recorder`. The controller samples key ranges across threads, records them, and after `detect_times` observations tries to produce a balanced split key.
- If normal key selection fails but CPU conditions justify fallback, candidate region ids are saved. After the loop, the highest CPU candidate is split by its hottest key range only if gRPC poll is not busy.
- `refresh_and_check_cfg` consumes config tracker updates and signals whether the region CPU collector should be registered or unregistered when the CPU threshold crosses zero.

State and persistence behavior:
- All controller state is in-memory: recorders, recent gRPC usage, stat batches, CPU caches, and sampled ranges. No durable writes occur here.
- `ReadStats::region_buckets` can accumulate `BucketStat` flow deltas to be reported elsewhere; it updates bucket metadata when newer bucket meta arrives and merges retained flow.
- `AutoSplitControllerContext::maybe_gc` clears retained buffers and CPU caches every 30 seconds to bound memory retention under bursty load.

Dependencies and integration points:
- Uses `SplitConfigManager`/`SplitConfig` for runtime thresholds and `SplitValidator` to suppress regions temporarily.
- Consumes `resource_metering::RawRecords` for per-region CPU and hottest key-range inference.
- Uses `ThreadInfoStatistics` plus TiKV thread name prefixes to measure gRPC server and unified read pool CPU usage.
- Integrated from the PD worker stats monitor, which flushes stats, handles `SplitConfigChange`, and schedules resulting `SplitInfo` work.
- Emits metrics for load, sample quality, and split outcomes.

Risks and edge cases:
- Sampling is randomized and bounded by `DEFAULT_MAX_SAMPLE_LOOP_COUNT`; under pathological empty providers it can return fewer samples and only warn.
- Candidate key evaluation rejects keys that are too imbalanced or too often contained inside request ranges, avoiding splits that would increase cross-region RPC fanout.
- CPU fallback intentionally avoids splitting when gRPC poll is busy, because splitting can increase RPC load.
- `recorders` are time-bounded by `clear`, but stale recorders can otherwise hold sampled key ranges until flush/clear removes them.
- CPU usage calculation divides summed CPU time by collected duration; zero duration maps to zero usage.

Test signals:
- Tests cover prefix sums, sample position classification, recorder readiness and collection, raw/encoded/mixed key split selection, CPU fallback ranges, sample-size behavior with empty providers, reservoir bias expectations, config refresh transition events, CPU stat collection/hottest range selection, average gRPC CPU windowing, batch receive limits, and context GC. Benchmarks cover sample evaluation, flush, and query-stat recording.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/split_controller.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/split_validator.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/split_validator.rs

Purpose: this file provides a small concurrent cache for temporarily disabling split decisions for specific regions. It is used by load-based split control to avoid repeatedly splitting regions that should be suppressed for a bounded time.

Important APIs and types:
- `SplitValidatorCore<P>` stores disabled region ids in a `crossbeam_skiplist::SkipMap<u64, Instant>`, plus capacity, GC offset, and a pluggable GC predicate.
- `SplitValidator` wraps `Arc<SplitValidatorCore<fn(...) -> bool>>` and exposes `new`, `is_disabled`, `disable`, and `enable`.
- Constants define capacity (`0x8000`), max entries scanned per GC (`0x80`), and TTL (`600s`).

Control flow:
- `disable(region_id)` inserts the current instant and then calls incremental `gc`.
- `is_disabled(region_id)` checks the skiplist; if the GC predicate says the entry is expired, it removes the entry and returns false.
- `enable(region_id)` removes the entry directly.
- `gc` tries to acquire a mutex-protected offset. If capacity is not reached and no GC round is in progress, it exits. Otherwise it scans at most `GC_ENTRY_LIMIT` entries from the offset, removes expired entries, and resets the offset when the scan reaches the end.

State and persistence behavior:
- State is entirely in-memory and shared by clone through `Arc`.
- Expiration is based on wall-clock `Instant::elapsed`; restart clears disabled state.
- The skiplist supports concurrent reads/writes, while the offset mutex bounds GC work and avoids multiple concurrent incremental scans.

Dependencies and integration points:
- Depends on `crossbeam_skiplist` for concurrent map behavior.
- Used by `AutoSplitController::flush` to skip regions marked disabled.
- Constructed and passed through PD worker code along with the auto split controller.

Risks and edge cases:
- GC only runs on `disable` and opportunistically on `is_disabled` for that key; a quiet cache can retain expired entries until later activity.
- `gc_offset` advances by `key + 1`; region id `u64::MAX` would wrap if present, although region ids are expected to stay below that.
- The TTL is fixed in this file and not online-configurable.

Test signals:
- Tests cover multi-region disable/enable, enabling absent regions, expiration via injected predicate, incremental GC offset movement and removal behavior, disable-triggered GC at capacity, and a mixed-operation benchmark over many region ids.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/split_validator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/Cargo.toml -->
# sources/storage-engines/tikv/components/resolved_ts/Cargo.toml

Purpose: this manifest defines the `resolved_ts` TiKV component crate. The crate tracks transactional changes and advances per-region resolved timestamps for CDC/stale-read related subsystems.

Important APIs and types:
- Package metadata sets crate name `resolved_ts`, edition 2021, Apache-2.0 license, unpublished version `0.0.1`.
- Feature flags proxy allocator, portability, SIMD, memory profiling, failpoints, and test-engine features down to the workspace `tikv` crate.
- Integration tests are declared as `tests/integrations/mod.rs`; failpoint tests are declared separately and require the `failpoints` feature.

Dependencies:
- Core runtime dependencies include `concurrency_manager`, `engine_traits`, `pd_client`, `raftstore`, `security`, `tikv`, `tikv_util`, `txn_types`, `grpcio`, `tokio`, `futures`, `protobuf`, `kvproto`, and `prometheus`.
- The dependency set matches the source files in this subset: `advance.rs` uses PD, gRPC, tokio, security, raftstore, and concurrency manager; `cmd.rs` uses raftstore coprocessor command batches, engine CF names, kvproto raft command types, and txn type decoders.
- Dev dependencies include RocksDB/test engines, test raftstore utilities, SST importer test utilities, and tempfile.

Control flow and integration behavior:
- The crate is part of the TiKV workspace and depends on sibling workspace crates rather than standalone published versions.
- Feature flags primarily forward to the top-level `tikv` crate, so allocator/failpoint/test-engine selection remains consistent across the workspace.

State and persistence behavior:
- The manifest itself has no runtime state. It determines which resolved-ts implementation paths and tests can compile under selected features.

Risks and edge cases:
- The failpoint test target is gated; running it without `--features failpoints` will skip or fail target selection depending on the cargo command.
- Workspace dependency versions mean compatibility is coupled to the enclosing TiKV workspace, not this crate alone.

Test signals:
- The explicit `integrations` and `failpoints` test targets indicate resolved-ts has both normal integration coverage and failpoint-driven fault-path coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/advance.rs -->
# sources/storage-engines/tikv/components/resolved_ts/src/advance.rs

Purpose: this file advances resolved timestamps asynchronously. It obtains a conservative minimum timestamp, synchronizes the concurrency manager, confirms raft leadership/quorum for target regions, and schedules resolved-ts advancement back to the endpoint worker.

Important APIs and types:
- `AdvanceTsWorker` owns a PD client, single-thread tokio runtime, scheduler, concurrency manager, steady timer, and cached last PD TSO.
- `advance_ts_for_regions` starts an async advancement cycle and later reschedules `Task::AdvanceResolvedTs` with the updated `LeadershipResolver`.
- `LeadershipResolver` caches TiKV gRPC clients, tracks region read progress, builds per-store `CheckLeaderRequest`s, and determines which regions have quorum-confirmed leadership.
- `resolve_by_raft` is an alternate leadership check path through `CdcHandle::check_leadership`.
- Helpers include `reset_check_leader_request`, `get_min_timeout`, `region_has_quorum`, and `get_tikv_client`.

Control flow:
- `advance_ts_for_regions` waits for PD TSO, caches it, updates the concurrency manager max ts, then lowers `min_ts` to the global minimum in-memory lock ts if necessary.
- The worker calls `leader_resolver.resolve(regions, min_ts, Some(interval))`; valid regions are scheduled as `Task::ResolvedTsAdvanced { regions, ts, ts_source }`.
- It then waits for either the configured interval or an external notify, enforces a minimum timeout delay, and schedules `Task::AdvanceResolvedTs` even when no regions were valid so future cycles continue.
- `LeadershipResolver::resolve` clears previous transient results, performs periodic GC, scans `RegionReadProgressRegistry` for local leader info, and builds remote check-leader requests for peer stores.
- It sends check-leader RPCs concurrently and processes them with `select_all`, so one slow/down TiKV does not block all responses. Regions become valid once responding stores satisfy joint-consensus quorum rules.
- gRPC client lookup uses PD store addresses, security manager channels, gzip compression, and cached clients. Retryable failures remove cached clients.

State and persistence behavior:
- No durable storage is written. State is runtime-only: cached clients, reusable request buffers, progress maps, valid/checking sets, and cached last PD TSO.
- Resolved-ts advancement is persisted/propagated by downstream endpoint/resolver/read-progress code after scheduled tasks run.
- `reset_check_leader_request` actively shrinks oversized reusable request buffers, preventing registry size or earlier large requests from retaining excessive memory.

Dependencies and integration points:
- Depends on PD for TSO and store addresses, `ConcurrencyManager` for max-ts and memory-lock constraints, `RegionReadProgressRegistry` for leader/read-state information, and raftstore `CdcHandle` for raft-based fallback checks.
- Uses `kvproto::tikvpb::TikvClient` `check_leader_async` RPCs and `kvrpcpb::CheckLeaderRequest/Response`.
- Schedules `crate::endpoint::Task` variants for the resolved-ts endpoint.
- Metrics track pending resolved-ts work, request sizes/counts, RPC duration, and client initialization duration.

Risks and edge cases:
- PD TSO errors are ignored for the cycle and default to zero; subsequent cycles retry. A zero or lowered timestamp should not advance beyond safety constraints.
- Leadership confirmation requires local leader info plus remote checks; missing/stale read progress or failed RPCs can delay resolved-ts advancement.
- TiFlash or stores without `check_leader` return `UNIMPLEMENTED`; the code treats this as an empty response.
- Joint consensus quorum handling must count incoming and demoting voters correctly; `region_has_quorum` separately checks both majorities.
- The resolver must be rescheduled even for empty regions, or advancement can stop.

Test signals:
- Tests cover request sizing, sending only requested regions despite a large registry, shrinking oversized request buffers on reuse, zero-region no-RPC behavior, and timeout minimum selection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/advance.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/cmd.rs -->
# sources/storage-engines/tikv/components/resolved_ts/src/cmd.rs

Purpose: this file converts raftstore observed command batches into resolved-ts change logs. It extracts transactional row-level changes from write/default/lock CF mutations so resolved-ts tracking can update locks and commits without reinterpreting full raft commands elsewhere.

Important APIs and types:
- `ChangeRow` represents decoded transactional effects: `Prewrite`, `Commit`, `OnePc`, and `IngestSsT`.
- `ChangeLog` wraps command-level outcomes: raft command error, row changes at an apply index, or admin command type.
- `ChangeLog::encode_change_log(region_id, CmdBatch)` maps observed raft commands for a region into `ChangeLog` values.
- `decode_write` and `decode_lock` parse txn write and lock records and filter unsupported/non-lock-relevant types.
- Internal `KeyOp` and `RowChange` group CF-level mutations by logical key before row encoding.
- `lock_only_filter` drops default-CF-only data from command batches when observe level is `LockRelated`.

Control flow:
- `encode_change_log` iterates a `CmdBatch` by region. Error responses become `ChangeLog::Error`; admin requests become `ChangeLog::Admin`; normal write batches are grouped and encoded into rows.
- It detects one-phase commit from `WriteBatchFlags::ONE_PC`.
- `group_row_changes` scans raft requests, records write CF puts by truncating commit timestamps from encoded keys, lock CF puts/deletes by raw key, default CF puts as unmatched defaults keyed by truncated timestamp, and `IngestSst` as a batch flag.
- After scanning, default values are attached only to keys that also had a lock or write row.
- `encode_rows` matches `(write, lock, default)` patterns into prewrite/commit/one-pc/rollback rows. Rollback commits intentionally clear commit ts; lock deletes become rollback commits with unknown start ts.
- `lock_only_filter` respects `ObserveLevel`: `None` drops the batch, `All` passes it through, and `LockRelated` retains lock CF, write CF, and ingest SST requests.

State and persistence behavior:
- This file has no persistent state. It is pure transformation over observed raft command data.
- Correctness depends on raft apply command ordering and indexes supplied by `CmdBatch`; row logs preserve the apply index for downstream resolver tracking.

Dependencies and integration points:
- Uses raftstore coprocessor `CmdBatch`, `Cmd`, and `ObserveLevel`; resolved-ts observer/endpoint code consumes `ChangeLog` and `ChangeRow`.
- Uses engine CF constants for lock/write/default filtering.
- Uses `txn_types` decoders for `WriteRef`, lock type parsing, `Lock`, `Write`, timestamps, and write batch flags.
- `ChangeLog` is re-exported by the `resolved_ts` crate and referenced by `endpoint.rs` when tracking applied changes.

Risks and edge cases:
- Unexpected row patterns panic, so grouping assumptions must match TiKV MVCC write batch generation.
- `decode_write` skips rewritten records with `gc_fence` and asserts they are overlapped rollbacks; this deliberately ignores some overlapped rollback writes.
- Only Put/Delete/Rollback write types and Put/Delete locks are relevant. Other lock types, including shared locks, are skipped.
- Default CF values are only attached when a matching lock/write mutation is present; unmatched default writes are ignored for resolved-ts tracking.
- `IngestSsT` is represented as a row marker because it can affect lock visibility outside normal row decoding.

Test signals:
- `test_cmd_encode` builds MVCC operations through TiKV test engines and verifies prewrite, commit, rollback, large default value attachment, one-pc rows, ingest SST marker behavior, and the known absence of an overlapped rollback row in one scenario.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/cmd.rs -->
