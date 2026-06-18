# subset-b-008832 research

Grouped research for TiKV `engine_tirocks`, `engine_traits`, and engine trait conformance tests. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/properties/range.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/properties/range.rs

Purpose: Implements TiRocks table-property collection and range-estimation support for TiKV split checks, approximate size/key accounting, and MVCC fallback estimates.

Important APIs and control flow: `SizeProperties`, `RangeOffsets`, `RangeProperties`, `RangePropertiesCollector`, and `RangePropertiesCollectorFactory` encode per-SST user properties under `tikv.total_size`, `tikv.size_index`, and `tikv.range_index`. Collector `add` accounts put entries and Titan blob indexes, advances cumulative size/key offsets, and inserts range points at configured size/key distances. `RangePropertiesExt for RocksEngine` reads memtable stats plus SST user properties to implement approximate keys, sizes, and split-key sampling; if write-CF range properties fail, key estimation falls back to MVCC properties via `get_range_entries_and_versions`.

State, persistence, and dependencies: State is persisted as RocksDB/TiRocks user-collected table properties inside SSTs, with backward decode support for older v2 `SizeProperties`. Dependencies include `codec`, `engine_traits`, TiRocks table-property APIs, Titan blob index decoding, TiKV key wrappers, and the MVCC property decoder.

Integration points, risks, and test signals: Integrated by CF options that install the collector factory and by split/check logic through `RangePropertiesExt`. Risks include malformed property bytes, unsorted or sparse offset points, inaccurate Titan blob size accounting, old CFs lacking range properties, large split-key sampling bias, and panics from invalid range ordering or UTF-8 file-name assumptions in logging. Tests exercise offset math, excluded range extraction, Titan blob index sizing, and MVCC fallback entry/version aggregation after flush.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/properties/range.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/properties/table.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/properties/table.rs

Purpose: Adapts TiRocks table-property collections and user-collected property maps to the engine-trait property abstraction.

Important APIs and control flow: `RocksUserCollectedProperties` is a transparent wrapper over TiRocks `UserCollectedProperties`; `get` returns raw property values and `approximate_size_and_keys` decodes `RangeProperties` to compute range distance. `RocksTablePropertiesCollection` wraps `OwnedTablePropertiesCollection` and iterates user-collected properties until the callback returns false. `RocksEngine::properties_of_tables_in_range` resolves the CF handle, calls TiRocks `properties_of_tables_in_range`, and returns the owned collection.

State, persistence, and dependencies: The state being read is persisted per-SST table metadata, not live memtable data. It depends on TiRocks builtin table property collections and the local range property decoder.

Integration points, risks, and test signals: This is the shared utility used by range, TTL, MVCC, and table property queries. Risks include the `unsafe` transparent transmute, extra allocation of range tuples, missing CF errors, and API drift: this file's implementation surface uses a user-collected-properties collection shape while the adjacent `engine_traits/src/table_properties.rs` in this snapshot declares a `TableProperties`-oriented collection. Tests are indirect through range/TTL/MVCC property callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/properties/table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/properties/ttl.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/properties/ttl.rs

Purpose: Collects and queries raw-key TTL expiration bounds from TiRocks SST user properties for default-CF RawKV data.

Important APIs and control flow: `encode_ttl` and `decode_ttl` store `tikv.max_expire_ts` and `tikv.min_expire_ts`. `TtlPropertiesExt for RocksEngine` scans table properties in a range, decodes TTL properties, and returns file-name/property pairs while skipping tables without TTL metadata. `TtlPropertiesCollector<F>` filters for put entries, TiKV data-key prefix, and raw key mode, decodes `RawValue`, and updates min/max expiration timestamps before finish writes properties if any TTL was seen.

State, persistence, and dependencies: TTL bounds are persisted in SST user properties and depend on `api_version::KvFormat`, `keys::DATA_PREFIX_KEY`, TiRocks table-property collectors, and engine-trait TTL structures.

Integration points, risks, and test signals: Used by RawKV TTL scans and GC/compaction estimation. Risks include decode failures being logged but ignored, only default-CF validity, missing TTL properties on preexisting SSTs, UTF-8 assumptions for file names, and source-version skew: this adapter uses zero as the empty sentinel while the adjacent trait file defines optional TTL bounds. Tests cover API V1ttl/API V2 encoding behavior, min/max handling, non-put exclusion, and empty/no-TTL error paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/properties/ttl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/snapshot.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/snapshot.rs

Purpose: Implements the engine-trait `Snapshot`, `Iterable`, and `Peekable` APIs on top of TiRocks snapshots.

Important APIs and control flow: `RocksSnapshot` stores an `Arc<Snapshot<'static, Arc<Db>>>`. `new` captures a DB snapshot. Internal `get` builds TiRocks `ReadOptions`, applies `fill_cache`, calls `get_pinned`, and maps found/not-found/status into `Result<Option<RocksPinSlice>>`. `iterator_opt` converts engine-trait iterator options, resolves the CF handle, and creates a `RocksSnapIterator`.

State, persistence, and dependencies: Snapshot state is a shared pinned TiRocks snapshot view of the DB at creation time; reads do not persist new data. It depends on local iterator option conversion, CF handle resolution, pinned slices, and status conversion.

Integration points, risks, and test signals: Used by TiKV read paths needing a stable view while writes continue. Risks include lifetime erasure around `'static`, stale CF handles if a CF is dropped, pinned-slice ownership, and option gaps because only `fill_cache` is mapped for point reads. Shared snapshot tests verify point reads, CF reads, and read consistency after later puts/deletes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/status.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/status.rs

Purpose: Converts between TiRocks status objects and the engine-trait error/status model.

Important APIs and control flow: `to_engine_trait_status` maps TiRocks `Code`, `SubCode`, `Severity`, and optional byte state into `engine_traits::Status`. `r2e` wraps TiRocks status as `Error::Engine`. `e2r` maps engine-trait errors back to TiRocks status, using `kIOError` for non-engine errors.

State, persistence, and dependencies: No persistent state is held; this is an error boundary between TiRocks and generic TiKV engine users.

Integration points, risks, and test signals: Used throughout TiRocks adapters for `map_err(r2e)` and callback error conversion. Risks include enum drift, `unreachable!` if TiRocks exposes a new max/sentinel variant unexpectedly, lossy conversion of non-engine errors to IO errors, and UTF-8 lossiness for TiRocks state bytes. Test signals are mostly compile-time exhaustiveness plus any runtime engine error assertions in trait tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/status.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/util.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/util.rs

Purpose: Provides TiRocks engine construction helpers, CF reconciliation, slice transforms, perf-level conversions, and CF handle lookup.

Important APIs and control flow: `new_engine` builds defaults with statistics; `new_engine_opt` validates Titan/non-Titan option consistency, requires default CF, creates missing DBs, lists existing CFs, loads latest options, preserves existing `level_compaction_dynamic_level_bytes`, opens with missing CF support when needed, and destroys discarded non-default CFs. `FixedSuffixSliceTransform`, `FixedPrefixSliceTransform`, and `NoopSliceTransform` implement TiRocks prefix extraction. `to_rocks_perf_level`, `to_engine_perf_level`, and `cf_handle` bridge engine traits to TiRocks.

State, persistence, and dependencies: This file mutates persistent DB directory and column-family metadata. It depends on TiRocks builders, Titan builders, loaded CF options, `Env`, `Statistics`, and local option wrappers.

Integration points, risks, and test signals: Used by tests and constructors to open TiRocks-backed `RocksEngine`. Risks include accidental CF drops when desired CF lists are wrong, dangerous dynamic-level-byte changes, default CF omission, Titan option mismatches, slice-transform panics if called outside domain, and path/CF race conditions during open. Tests cover CF diffs, creating/opening/reordering/dropping CFs, preserving data, and retaining dynamic-level-byte settings.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/write_batch.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/write_batch.rs

Purpose: Implements engine-trait write batches for TiRocks, including multi-batch splitting for large TiKV writes.

Important APIs and control flow: `WriteBatchExt for RocksEngine` creates `RocksWriteBatchVec`. `RocksWriteBatchVec` holds the engine, a vector of TiRocks `WriteBatch` instances, save-point indexes, and the active batch index. `check_switch_batch` starts a new sub-batch when multi-batch writing is enabled and the active batch reaches 16 keys. `write_opt` chooses `write_multi` or single `write`; `should_write_to_engine` uses either batch-count or total-count thresholds. `Mutable` methods resolve default/CF handles and append put/delete/range-delete commands.

State, persistence, and dependencies: Batched commands are in memory until `write_opt` persists them through TiRocks with translated write options. Save points track only the sub-batch index stack and clear later sub-batches during rollback.

Integration points, risks, and test signals: Used by TiKV apply/write paths and shared write-batch tests. Risks include atomicity assumptions around multi-batch writes, save-point behavior across sub-batches, memory retention after large batches, merging batches with different split boundaries, and no memtable insert hint support. Tests verify flush thresholds in pipeline and multi-batch modes, persisted writes, clear behavior, and merge count/sub-batch shape.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/write_batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/Cargo.toml -->
# sources/storage-engines/tikv/components/engine_traits/Cargo.toml

Purpose: Defines the `engine_traits` crate package metadata, optional features, and dependency boundary for TiKV's generic storage-engine abstraction.

Important APIs and control flow: Features expose `failpoints` and `testexport`. Dependencies include shared TiKV crates for collections, encryption, error codes, filesystem rate limiting, keys, protobufs, Raft, logging, tracking, utilities, and transaction types. Dev dependencies add `rand` and `toml`.

State, persistence, and dependencies: The manifest persists no runtime state, but its dependency graph enforces the important design rule that `engine_traits` should not depend on RocksDB/TiRocks concrete bindings.

Integration points, risks, and test signals: All engine implementations and generic users depend on this crate. Risks include accidentally introducing concrete engine dependencies, feature skew with implementor crates, or nightly feature requirements in `lib.rs` constraining toolchains. Test signals are workspace build resolution, feature-specific builds, and conformance tests from `engine_traits_tests`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/cf_defs.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/cf_defs.rs

Purpose: Defines canonical TiKV column-family names and helper mappings for data CF indexing.

Important APIs and control flow: Constants include `CF_DEFAULT`, `CF_LOCK`, `CF_WRITE`, `CF_RAFT`, `LARGE_CFS`, `ALL_CFS`, `DATA_CFS`, and `DATA_CFS_LEN`. `data_cf_offset` treats empty CF as default and returns the index in `DATA_CFS`; `offset_to_cf`, `name_to_cf`, and `is_data_cf` provide reverse and validation helpers.

State, persistence, and dependencies: No runtime state is stored. These constants align engine metadata, flush-state arrays, range accounting, and tests.

Integration points, risks, and test signals: Used widely by KvEngine, flush/apply persistence, range estimates, and test constructors. Risks include panics from unknown CFs in `data_cf_offset`, array-index assumptions if CF sets change, and treating empty string as default in only some APIs. Tests in `cf_names` and many CF-specific scenarios exercise these constants.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/cf_defs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/cf_names.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/cf_names.rs

Purpose: Declares the minimal trait for engines that can report their column-family names.

Important APIs and control flow: `CfNamesExt::cf_names` returns the engine's CF names as borrowed string slices.

State, persistence, and dependencies: State comes from the implementing engine's column-family registry or manifest; this trait only exposes it.

Integration points, risks, and test signals: Required by `KvEngine`, compaction helpers, delete-range helpers, and tests that iterate all CFs. Risks are ordering expectations, missing default CF, and stale CF lists after drops. Shared tests check default-only and `ALL_CFS` name exposure.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/cf_names.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/cf_options.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/cf_options.rs

Purpose: Defines generic access to column-family options and Titan CF options.

Important APIs and control flow: `CfOptionsExt` associates an implementation-specific `CfOptions` type and exposes `get_options_cf` and `set_options_cf`. `CfOptions` provides getters/setters for write buffer count, L0 slowdown/stop triggers, compaction trigger, pending compaction limits, block cache capacity, Titan CF options, target file size, auto-compaction toggles, write-stall behavior, SST partitioner factory, and max compactions.

State, persistence, and dependencies: Implementations typically read/write live engine option state and may persist changes depending on backend behavior. It depends on `TitanCfOptions` and `SstPartitionerFactory`.

Integration points, risks, and test signals: Used by configuration reload, flow control, compaction scheduling, and cache resizing. Risks include string option names accepted by `set_options_cf`, backend-specific unsupported settings, lifetime of partitioner factories, and live mutation hazards. Signals are backend-specific option tests and runtime config update tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/cf_options.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/checkpoint.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/checkpoint.rs

Purpose: Abstracts engine checkpoint creation and database merge behavior.

Important APIs and control flow: `Checkpointable` associates a `Checkpointer`, creates one with `new_checkpointer`, and defines `merge` for combining DBs. `Checkpointer::create_at` writes a checkpoint to an output directory with optional Titan output directory and log-size flush threshold.

State, persistence, and dependencies: Checkpoints persist engine files to new directories, potentially involving SST, MANIFEST, WAL, and Titan blob state.

Integration points, risks, and test signals: Used by backup, snapshot, tablet, and migration workflows. Risks include incomplete flush before checkpoint, encryption metadata mismatches, Titan path handling, and merge conflicts. Shared encrypted checkpoint tests reopen the checkpoint and verify data plus key-manager cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/checkpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/compact.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/compact.rs

Purpose: Defines generic manual compaction operations and compaction event metadata used by TiKV.

Important APIs and control flow: `ManualCompactionOptions` carries exclusivity, max subcompactions, bottommost-level force, and bottom-level range-overlap checking. `CompactExt` exposes auto-compaction status, range compaction across all CFs or one CF, file compaction by range or explicit file list, and range validation. `CompactedEvent` exposes compacted key ranges, byte-decline calculations, output level labels, and CF names.

State, persistence, and dependencies: Compaction rewrites persistent SST layout and may affect file sizes, snapshots, and range estimates. The trait depends on `CfNamesExt` and `BTreeMap` range accounting.

Integration points, risks, and test signals: Used by region split checks, manual admin compaction, GC, and size-decline heuristics. Risks include wrong range bounds, compaction stalls, file-level compaction with L0 exclusion, event byte attribution, and compaction during snapshots. Signals are backend compaction tests and split-check behavior; this file itself has no direct tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/compact.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/compaction_job.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/compaction_job.rs

Purpose: Defines a generic view of backend compaction-job metadata.

Important APIs and control flow: `CompactionJobInfo` exposes job status, CF name, input/output file counts and paths, table-property collection view, input/output levels, elapsed time, corrupt-key count, record counts, byte totals, and backend compaction reason.

State, persistence, and dependencies: It describes a completed or in-flight compaction job and references persistent SST files, but does not mutate state itself.

Integration points, risks, and test signals: Used by event listeners, metrics, and debugging. Risks include backend-specific reason enums, stale file paths after deletion, status conversion loss, and table-property view lifetimes. Java RocksDB tests elsewhere cover similar metadata defaults; this Rust trait has implementor-driven signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/compaction_job.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/db_options.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/db_options.rs

Purpose: Defines generic database-wide option access, including rate limiting, flush behavior, Titan DB options, and WAL manifest verification.

Important APIs and control flow: `DbOptionsExt` associates `DbOptions` and provides get/set by string option pairs. `DbOptions` exposes max background jobs, rate limiter bytes and auto-tuning, flush size, flush-oldest-first, Titan DB options, and WAL manifest tracking. `TitanCfOptions` currently exposes construction and minimum blob size.

State, persistence, and dependencies: Implementations mutate live DB option state and may persist option changes through backend option files.

Integration points, risks, and test signals: Used by engine constructors, runtime config changes, and IO flow control. Risks include unsupported options, unit mismatches, option persistence drift, and Titan naming mismatch in `TitanCfOptions`. Constructor and backend option tests provide coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/db_options.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/db_vector.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/db_vector.rs

Purpose: Defines the associated byte-buffer type returned by engine reads.

Important APIs and control flow: `DbVector` is a marker trait requiring `Debug`, deref to `[u8]`, and comparison with borrowed byte slices.

State, persistence, and dependencies: Implementations may own bytes or pin backend cache memory; the trait itself holds no state.

Integration points, risks, and test signals: Used by `Peekable` for point reads from engines and snapshots. Risks are lifetime/pinning mistakes, expensive clones when implementations cannot pin, and equality semantics. Tests compare returned values to byte slices across point reads, snapshots, and write scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/db_vector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/engine.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/engine.rs

Purpose: Defines `KvEngine`, the central generic key-value storage engine trait for TiKV.

Important APIs and control flow: `KvEngine` composes read, write, iteration, options, import, SST, compaction, range/MVCC/TTL/table properties, performance, misc, and checkpoint traits. It associates a `Snapshot`, creates snapshots, syncs writes to disk, flushes metrics through `StatisticsReporter`, exposes a temporary `bad_downcast`, and has a default `can_apply_snapshot` hook.

State, persistence, and dependencies: Implementors own persistent KV state, CF metadata, snapshots, write batches, options, and metrics. The trait expresses what TiKV needs but holds no state itself.

Integration points, risks, and test signals: This is the primary type bound throughout TiKV. Risks include an overly broad trait forcing all engines to implement every feature, concrete downcast leakage, snapshot apply hooks being backend-specific, and associated-type coupling. Shared tests instantiate `KvTestEngine` through this trait and validate core read/write/snapshot/iterator/SST behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/engines.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/engines.rs

Purpose: Bundles the key-value and Raft engines used by a TiKV store.

Important APIs and control flow: `Engines<K, R>` stores `kv` and `raft` fields. Its constructor `new` returns the pair, and generic bounds require `K: KvEngine` and `R: RaftEngine`.

State, persistence, and dependencies: It is a lightweight owner/transport for two persistent engines; durability belongs to the contained engines.

Integration points, risks, and test signals: Used by store/bootstrap code that must pass both engines together. Risks are accidental cloning or lifecycle mismatch between KV and Raft engines. Signals are broad compile-time integration rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/engines.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/errors.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/errors.rs

Purpose: Provides the common engine error/status type shared by all engine implementations and TiKV callers.

Important APIs and control flow: `Code`, `SubCode`, and `Severity` mirror RocksDB-like status fields. `Status` stores those fields plus string state and exposes builder/getter methods. `Error` wraps engine status plus range, protobuf, IO, boxed, CF, codec, Raft log availability, compaction, and boundary errors. `ErrorCodeExt` maps variants to TiKV error codes, and conversions to Raft error and string are provided.

State, persistence, and dependencies: Error values are transient but encode persistent failure conditions such as IO, corruption, compaction, or missing entries. Dependencies include `error_code`, `raft`, `protobuf`, `thiserror`, and TiKV log wrappers.

Integration points, risks, and test signals: Used by every trait result. Risks include losing backend-specific detail inside `Status`, conflating storage and Raft errors, accidental panics from formatted keys, and changing error-code mappings that affect observability. Shared tests assert engine errors for invalid operations; Raft integrations rely on the special compaction/unavailable conversions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/file_system.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/file_system.rs

Purpose: Wraps filesystem IO inspection with the global TiKV IO rate limiter.

Important APIs and control flow: `FileSystemInspector` defines `read` and `write` admission methods. `EngineFileSystemInspector` stores an optional `IoRateLimiter`, can be constructed from global or explicit limiter, and delegates read/write requests with the current IO type; without a limiter it returns the requested byte count unchanged.

State, persistence, and dependencies: State is the optional shared rate limiter. No data is persisted, but returned allowances govern persistent IO behavior elsewhere.

Integration points, risks, and test signals: Used by engine filesystem adapters to apply IO throttling. Risks include missing limiter installation, wrong IO type context, partial allowance handling by callers, and treating returned length as actual IO completion. Signals are integration tests around rate limiting and backend filesystem behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/file_system.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/flow_control_factors.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/flow_control_factors.rs

Purpose: Declares an extension point for retrieving storage-engine flow-control factors.

Important APIs and control flow: `FlowControlFactorsExt` exposes `get_flow_control_factors_cf(&self, cf) -> Result<(u64, u64)>`, returning backend-defined factors for a CF.

State, persistence, and dependencies: State is read from backend engine metrics/options; the trait itself has no storage.

Integration points, risks, and test signals: Used by `MiscExt` supertrait bounds and write-stall/flow-control logic. Risks are unclear semantics of the returned tuple, unsupported CFs, and stale metrics. Signals come from backend flow-control tests and runtime throttling behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/flow_control_factors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/flush.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/flush.rs

Purpose: Tracks memtable flush progress and persists apply-index progress for tablet/raft recovery.

Important APIs and control flow: `SstApplyState` registers applied SST metadata by data CF, returns stale SSTs once a CF is flushed past their apply index, and deletes tracked entries. `FlushState` stores current applied index and per-CF flushed indexes. `PersistenceListener` receives memtable sealed/completed callbacks, records `(cf, apply_index, smallest_seqno)` progress, merges flushed progress by CF when flush completes, persists it through `StateStorage`, and updates `FlushState`. `StateStorage for RaftEngine` writes flushed index records into a Raft log batch and consumes it synchronously.

State, persistence, and dependencies: In-memory state includes linked flush progress, atomics, and registered SSTs. Durable state is persisted to the Raft engine as flushed indexes. Dependencies include `kvproto::SstMeta`, Raft engine traits, data CF mapping, failpoints, and panic marks.

Integration points, risks, and test signals: Used by multi-tablet recovery, WAL-disabled apply replay, and SST cleanup. Risks include assumptions about one DB writer, out-of-order flush callbacks, panics on missing progress, CF index panics, raft persistence failure unwraps, and race ordering around atomics. Tests cover `SstApplyState`; failpoints and backend flush tests are important for listener correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/flush.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/import.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/import.rs

Purpose: Abstracts ingestion of external SST files into an engine.

Important APIs and control flow: `ImportExt` associates `IngestExternalFileOptions`, ingests files into a CF with optional range and forced allow-write mode, and acquires a range latch for ingestion serialization. `IngestExternalFileOptions` controls move-files and allow-write behavior.

State, persistence, and dependencies: Ingestion moves or links external SST data into persistent engine storage and may lock a key range during the operation.

Integration points, risks, and test signals: Used by snapshot apply, import, backup restore, and range delete by writer. Risks include overlapping writes when allow-write is enabled, latch misuse, partial ingestion failures, encryption metadata, and CF/range mismatch. Signals come from backend ingestion and SST tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/import.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/iterable.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/iterable.rs

Purpose: Defines TiKV's generic iterator model for engines, snapshots, and SST readers.

Important APIs and control flow: `Iterator` supports seek, seek-for-prev, first/last, next/prev, key/value, and validity checks. `RefIterable` creates borrowing iterators for SST-style readers. `IterMetricsCollector` and `MetricsExt` expose skipped-key and block-read metrics. `Iterable` creates owned iterators and provides `scan` and `seek` helpers; `scan_impl` seeks to the start key and repeatedly invokes a callback until it returns false or the iterator ends. `iter_option` builds bounded iterator options.

State, persistence, and dependencies: Iterators hold backend cursor/snapshot state over persistent key-value data. Helpers do not persist state.

Integration points, risks, and test signals: Used by all range scans, snapshots, SST readers, and tests. Risks include invalid iterator panics, bounds misuse, inconsistent engine-vs-snapshot views, callback early termination, and metric defaults hiding backend reads. Shared iterator tests exhaust empty, forward, reverse, seek, seek-for-prev, direction changes, and miss semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/iterable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/lib.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/lib.rs

Purpose: Documents and assembles the `engine_traits` crate, TiKV's generic storage engine abstraction with no concrete RocksDB dependency.

Important APIs and control flow: The large crate-level documentation explains capabilities, design notes, porting process, and refactoring rules. The module list exports extension traits for CF names/options, compaction, DB options, file system, flush, import, misc, snapshots, SST, write batches, MVCC/range/TTL/table properties, perf context, region cache, iteration, mutation, peeking, CF constants, engine pairs, errors, options, ranges, Raft engine traits, compaction jobs, raw TTL, and utilities. It also enables nightly features used by the crate.

State, persistence, and dependencies: No runtime state is held here, but exports define the public dependency boundary and prevent direct concrete-engine coupling.

Integration points, risks, and test signals: Every generic engine user imports through this crate. Risks include API sprawl, unstable Rust feature requirements, mismatched implementor modules, and public re-export churn. Test signals are workspace compilation and the `engine_traits_tests` crate that exercises the exported contracts.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/misc.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/misc.rs

Purpose: Holds miscellaneous engine operations not yet factored into narrower traits.

Important APIs and control flow: `DeleteStrategy` selects delete-files, delete-blobs, delete-by-key, delete-by-range, or delete-by-writer with ingestion options. `StatisticsReporter` abstracts metrics collection/flush. `RangeStats` summarizes entries, MVCC versions, rows, deletes, and computes redundant keys. `MiscExt` exposes flush operations, delete-ranges across CFs, memtable stats, ingestion slowdown checks, engine size, path, WAL sync, compaction/background-work controls, existence/lock checks, stats dumps, sequence numbers, SST sizes, key counts, range stats, stall state, active memtable stats, global flush counters, and disk engine access.

State, persistence, and dependencies: Operations touch memtables, SSTs, Titan blobs, WALs, compaction state, and filesystem paths. Dependencies include `KvEngine`, write options, CF names, flow-control factors, and `Range`.

Integration points, risks, and test signals: Used throughout TiKV maintenance, admin, metrics, and apply paths. Risks include broad trait coupling, delete strategy semantics with snapshots, ingestion during writes, stale size estimates, and backend-specific no-op behavior. Shared tests cover path and sync; broader coverage is backend/integration-level.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/misc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/mutable.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/mutable.rs

Purpose: Defines synchronous mutation methods for engines.

Important APIs and control flow: `SyncMutable` provides put, put-CF, delete, delete-CF, delete-range, delete-range-CF, plus protobuf helpers that serialize messages before writing.

State, persistence, and dependencies: Implementations apply changes directly to persistent engine state or WAL/memtable state according to backend semantics.

Integration points, risks, and test signals: Used by direct write paths and tests as the default-CF counterpart to write-batch mutation. Risks include range-delete bound semantics, CF validation, protobuf serialization errors, and snapshot visibility expectations. Shared scenario tests cover all direct mutation variants and range-delete edge cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/mutable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/mvcc_properties.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/mvcc_properties.rs

Purpose: Defines MVCC statistics collected from table properties and the trait for querying them.

Important APIs and control flow: `MvccProperties` tracks timestamp bounds, row/version/put/delete counts, max row versions, TTL properties, and timestamp spans for discardable stale versions and deletes. `new` initializes extrema, and `add` merges another property set. `MvccPropertiesExt::get_mvcc_properties_cf` returns optional MVCC properties for a CF, safe point, and key range.

State, persistence, and dependencies: Implementations usually decode persisted SST user properties and may estimate discardable versions from timestamps. Dependencies include `txn_types::TimeStamp` and `TtlProperties`.

Integration points, risks, and test signals: Used by GC, compaction, region stats, and range-key fallback in TiRocks. Risks include uniform-distribution assumptions, timestamp extrema defaults, delete/stale version estimation error, and TTL merge semantics. Tests are in implementor property collectors and range fallback tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/mvcc_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/options.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/options.rs

Purpose: Defines generic read, write, and iterator option structs passed across engine implementations.

Important APIs and control flow: `ReadOptions` controls fill-cache. `WriteOptions` controls sync, no-slowdown, and WAL disabling. `SeekMode` selects total-order or prefix seek. `IterOptions` stores lower/upper key builders, prefix-same-as-start, fill-cache, timestamp hints, key-only mode, seek mode, and max skippable internal keys, with setters for slice/vector bounds and timestamp bound conversion.

State, persistence, and dependencies: Options are transient request state. Write options can affect persistence guarantees through sync and WAL behavior; iterator options affect scan visibility/performance.

Integration points, risks, and test signals: Used by point reads, iterators, write batches, and SST readers. Risks include underflow in excluded max timestamp when ts is zero, reserved-prefix-length mistakes, prefix mutation after bound construction, key-only being backend-specific, and options silently ignored by adapters. Unit tests cover timestamp hint conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/options.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/peekable.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/peekable.rs

Purpose: Defines point-read operations for engines and snapshots.

Important APIs and control flow: `Peekable` associates a `DbVector` result type and requires option-aware default-CF and CF-specific gets. Default helpers use default read options, and protobuf helpers decode returned bytes into default message instances.

State, persistence, and dependencies: Reads observe persistent or snapshot state but do not mutate it. Dependencies include `ReadOptions`, `DbVector`, and protobuf.

Integration points, risks, and test signals: Used by nearly all key-value read paths. Risks include CF mismatch, protobuf decode failures, fill-cache option propagation gaps, and snapshot consistency requirements. Shared tests cover default-CF equivalence, writes followed by reads, snapshots, and read consistency during later writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/peekable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/perf_context.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/perf_context.rs

Purpose: Abstracts backend performance-context metrics collection.

Important APIs and control flow: `PerfLevel` enumerates measurement levels and has numeric serialization support. `PerfContextExt` creates a backend `PerfContext` for a level and subsystem `PerfContextKind`. `PerfContextKind` identifies raftstore apply/store, storage commands, or coprocessor requests. `PerfContext` starts observation and reports collected metrics to Prometheus/trackers.

State, persistence, and dependencies: Perf contexts hold transient measurement counters, often backed by backend thread-local/global state. Dependencies include `tikv_util::numeric_enum_serializing_mod` and `tracker::TrackerToken`.

Integration points, risks, and test signals: Used by storage, raftstore, and coprocessor observability. Risks include global-vs-per-engine ambiguity, no-op alternate engines hiding regressions, level serialization drift, and forgotten `start_observe`. Signals are metrics tests and runtime Prometheus/tracker observations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/perf_context.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/raft_engine.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/raft_engine.rs

Purpose: Defines generic Raft log/state storage traits used alongside the KV engine.

Important APIs and control flow: `RaftEngineReadOnly` exposes store/bootstrap state, raft state, region/apply state by apply index, flushed index, dirty mark, recover state, single entry, and ranged entry fetch. `RaftEngineDebug` scans/dumps all entries and states. `RaftEngine` creates log batches, syncs, consumes batches, cleans/gcs logs, prunes old states, supports manual purge, metrics, stop, stats/size/path, and raft-group iteration. `RaftLogBatch` appends entries, writes store/region/apply/raft/recover/flushed/dirty state, reports persist size, emptiness, and merging.

State, persistence, and dependencies: This is durable Raft metadata and log storage, including per-region states and flushed-index records used by KV flush recovery. Dependencies include `kvproto` raft server messages and `raft::eraftpb::Entry`.

Integration points, risks, and test signals: Used by raftstore, recovery, log GC, and `flush.rs` persistence. Risks include apply-index lookup semantics, overwrite/delete ranges in append, large GC batching, manual purge defaults, and error conversion to Raft. Signals come from Raft engine backend tests and recovery tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/raft_engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/range.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/range.rs

Purpose: Defines a borrowed half-open key range shared across engine APIs.

Important APIs and control flow: `Range<'a>` stores `start_key` and `end_key` byte slices. `Range::new` constructs a range without validation.

State, persistence, and dependencies: The type is transient borrowed request state and persists nothing.

Integration points, risks, and test signals: Used by range deletes, ingestion, table/range property queries, memtable stats, and delete strategies. Risks include callers passing reversed bounds, ambiguous empty end-key semantics in different APIs, and lifetime misuse by implementors. Scenario tests cover delete-range inclusive/exclusive, equal bounds, and reversed-range error behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/range.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/range_properties.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/range_properties.rs

Purpose: Declares the generic range-estimation APIs engines provide for split checks and size/key accounting.

Important APIs and control flow: `RangePropertiesExt` exposes approximate keys and size over all relevant CFs or one CF, plus approximate split-key selection over all CFs or one CF. `large_threshold` is explicitly for logging large ranges.

State, persistence, and dependencies: Implementations usually combine live memtable stats with persisted SST user properties. The trait depends on `Range` and common `Result`.

Integration points, risks, and test signals: Used by region split, scheduler, and diagnostics. Risks include approximation error, missing property collectors on older SSTs, CF aggregation choices, and split-key sampling quality. TiRocks range tests exercise property math and fallback; broader split tests validate operational behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/range_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/raw_ttl.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/raw_ttl.rs

Purpose: Provides RawKV TTL timestamp helpers.

Important APIs and control flow: `ttl_current_ts` returns current Unix seconds and has a failpoint override. `ttl_to_expire_ts` maps zero TTL to `None` and nonzero TTL to `current + ttl` with saturating addition.

State, persistence, and dependencies: Helpers are stateless, but generated expiration timestamps are persisted inside encoded raw values by callers. Dependencies include failpoints and TiKV time utilities.

Integration points, risks, and test signals: Used by RawKV write paths and TTL property collection. Risks include clock skew, saturating overflow hiding very large TTLs, failpoint-only test behavior, and semantic differences between absent TTL and expire-ts zero. Tests should use failpoints for deterministic timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/raw_ttl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/region_cache_engine.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/region_cache_engine.rs

Purpose: Defines an optional region cache engine abstraction for in-memory or NVMe accelerated reads.

Important APIs and control flow: `FailedReason` explains cache snapshot failures. `RegionEvent` models split, try-load, eviction, and range eviction, with debug output hiding callback internals. `EvictReason` enumerates eviction causes. `RegionCacheEngine` creates cache snapshots for a `CacheRegion`, read timestamp, and shared sequence number, connects a disk engine, starts a hint service, and reports enablement. `RegionCacheEngineExt` handles events, cache presence, and loads. `CacheRegion` wraps encoded region bounds and provides contains, overlaps, union, and difference operations.

State, persistence, and dependencies: Cache engines own non-authoritative cached region state synchronized with disk engine sequence numbers. Dependencies include region metadata and encoded TiKV keys.

Integration points, risks, and test signals: Integrated with raftstore region events, read paths, delete-range eviction, and range hints. Risks include epoch races, boundary encoding mistakes, stale cache after split/merge/snapshot, callback lifecycle, and disabled default behavior. Unit tests cover overlap semantics; integration tests must cover cache invalidation and snapshot fallback.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/region_cache_engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/snapshot.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/snapshot.rs

Purpose: Defines the generic snapshot trait for consistent read-only engine views.

Important APIs and control flow: `Snapshot` is a marker-style trait requiring `'static`, `Peekable`, `Iterable`, `CfNamesExt`, `SnapshotMiscExt`, `Send`, `Sync`, `Sized`, and `Debug`. It provides a default `in_memory_engine_hit` hook returning false.

State, persistence, and dependencies: Implementors hold backend snapshot state that pins a read view; no new data is persisted through this trait.

Integration points, risks, and test signals: Used by TiKV read paths and shared iterator/read tests. Risks include lifetime pressure from `'static`, inability to clone snapshots directly, cache-hit reporting differences, and ensuring iterators/readers share the same snapshot view. Snapshot tests verify point-read and post-write isolation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/snapshot_misc.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/snapshot_misc.rs

Purpose: Declares miscellaneous snapshot extension behavior.

Important APIs and control flow: `SnapshotMiscExt` exposes `sequence_number`, returning the backend sequence number for the snapshot.

State, persistence, and dependencies: The sequence number represents a snapshot's persisted/logical read point; this trait stores nothing itself.

Integration points, risks, and test signals: Used by read consistency, cache engine coordination, and recovery diagnostics. Risks include backends without meaningful sequence numbers, sequence mismatch with region cache snapshots, and stale values after compaction. Tests are implementor-specific.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/snapshot_misc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/sst.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/sst.rs

Purpose: Defines generic external SST reader/writer support and file metadata.

Important APIs and control flow: `SstExt` associates reader, writer, and builder types. `SstReader` opens files with optional encryption manager, verifies checksums, and reports KV count/size. `SstWriter` puts ordered keys, writes deletion keys, reports file size, finishes to metadata, or finishes and returns a readable buffer. `ExternalSstFileReader` can reset. `SstCompressionType` parses `lz4`, `snappy`, and `zstd`. `SstWriterBuilder` configures DB/CF, in-memory mode, compression type/level, and builds writers. `ExternalSstFileInfo` exposes path, key bounds, sequence number, file size, and entry count.

State, persistence, and dependencies: Writers create persistent or in-memory SST artifacts; readers inspect them. Dependencies include encryption `DataKeyManager` and import SST metadata.

Integration points, risks, and test signals: Used by import, snapshot, backup/restore, and range-delete-by-writer. Risks include ordered-key enforcement, delete-only files, compression compatibility, encryption metadata, checksum failures, and sequence-number semantics. Shared SST tests cover empty files, forward/reverse iteration, deletes, duplicate/reverse keys, file path, bounds, entry count, and file size.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/sst.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/sst_partitioner.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/sst_partitioner.rs

Purpose: Abstracts backend SST partitioner callbacks used during compaction/output file generation.

Important APIs and control flow: `SstPartitionerRequest` describes previous/current user key and current output file size. `SstPartitionerResult` returns whether partitioning is required. `SstPartitionerContext` describes compaction mode, output level, key bounds, and next-level boundaries/sizes. `SstPartitioner` decides partitioning and trivial-move eligibility. `SstPartitionerFactory` names and creates partitioners.

State, persistence, and dependencies: Partitioners influence persistent SST output boundaries but do not persist state themselves.

Integration points, risks, and test signals: Connected through CF options and backend compaction. Risks include factory/partitioner lifetime restrictions, boundary vector alignment, trivial-move decisions that bypass desired partitioning, and backend support differences. Signals are backend compaction/partition tests and output-file shape checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/sst_partitioner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/table_properties.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/table_properties.rs

Purpose: Defines generic access to table properties and user-collected SST properties.

Important APIs and control flow: `UserCollectedProperties` can fetch raw indexed properties, compute approximate size/keys, and return MVCC properties. `TableProperties` associates user properties and exposes them plus entry count. `TablePropertiesCollection` iterates table properties until a callback stops. `TablePropertiesExt` retrieves a collection covering ranges in a CF.

State, persistence, and dependencies: Implementations read persisted SST table metadata. It depends on `MvccProperties`, `Range`, and `Result`.

Integration points, risks, and test signals: Used by range, MVCC, TTL, and diagnostics. Risks include backend API drift, partial table coverage for ranges, missing property collectors, property decode failures, and mismatches with implementors that expose only user-collected properties. Test signals are mostly indirect through property collector tests and approximate-range behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/table_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/tablet.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/tablet.rs

Purpose: Provides tablet abstractions for multi-RocksDB/tablet architecture, including latest-tablet caching and registry management.

Important APIs and control flow: `CachedTablet` wraps shared latest tablet data plus a local cache/version; `set` updates shared state and version, `latest` refreshes stale local cache, and `release` drops cache. `TabletContext` carries region id, suffix, encoded key bounds, and optional flush state. `TabletFactory` opens/destroys/exists-checks tablets. `SingletonFactory` returns one shared tablet for tests. `TabletRegistry` owns a root path, factory, and region-id map, formats/parses tablet names, computes paths, gets/defaults/removes cached tablets, loads tablets with optional creation, and iterates opened tablets releasing local caches.

State, persistence, and dependencies: Registry state is in-memory; tablet data lives under root paths managed by factories. `TabletContext::flush_state` links tablet persistence to apply-index flushing.

Integration points, risks, and test signals: Used by multi-tablet storage engines and recovery. Risks include stale local caches until `latest`, suffix/path naming collisions, loading an already-open tablet, `create=false` existence checks, broad locks during iteration, and factory-specific destroy semantics. Tests cover cache refresh, singleton behavior, registry load/update/remove/path parsing, and memory-tablet duplicate opens.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/tablet.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/ttl_properties.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/ttl_properties.rs

Purpose: Defines TTL property aggregation and range query APIs.

Important APIs and control flow: `TtlProperties` stores optional maximum and minimum expiration timestamps. `add` merges a single timestamp, `merge` updates optional extrema, and `is_some`/`is_none` report whether any TTL bound exists. `TtlPropertiesExt::get_range_ttl_properties_cf` returns per-file TTL properties for a CF and key range.

State, persistence, and dependencies: The struct is transient aggregation state, usually decoded from persisted SST properties by implementors.

Integration points, risks, and test signals: Used by RawKV TTL and MVCC property aggregation. Risks include option-vs-zero sentinel mismatches with older adapters, merging none/some incorrectly, and per-file aggregation leaving final range interpretation to callers. Unit tests cover add, merge, none/some behavior, and timestamp zero handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/ttl_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/util.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/util.rs

Purpose: Supplies key-range validation and sequence-number window utilities for write ordering and memtable flush coordination.

Important APIs and control flow: `check_key_in_range` returns `NotInRange` unless a key is within `[start,end)`, treating empty end as unbounded. Global atomics allocate write counters, memtable versions, and max synced sequence number access. `SequenceNumber::pre_write` reserves a contiguous write counter, `post_write` attaches backend sequence number and end counter, and `max` compares by sequence number. `SequenceNumberWindow::push` receives sequence numbers out of order, tracks contiguous received start counters, uses pending end-counter mapping, advances committed sequence number when all prior writes are received, and exposes committed seqno and pending count.

State, persistence, and dependencies: State is process-global atomics plus in-memory window queues/maps; committed sequence numbers represent persistence/order coordination but are not directly durable here.

Integration points, risks, and test signals: Used by asynchronous write/flush paths that need contiguous commit tracking. Risks include global counter wrap, duplicate/old sequence handling, assumptions about end-counter monotonicity, unbounded pending windows under lost notifications, and panic assertions. Tests cover out-of-order sequence receipt and benchmark high-volume window updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/write_batch.rs -->
# sources/storage-engines/tikv/components/engine_traits/src/write_batch.rs

Purpose: Defines generic write-batch creation, mutable batch commands, and batch commit semantics.

Important APIs and control flow: `WriteBatchExt` associates an engine write-batch type, exposes `WRITE_BATCH_MAX_KEYS`, and creates batches with optional capacity. `Mutable` defines put/delete/range-delete operations plus protobuf helpers. `WriteBatch` extends `Mutable` with option-aware writes, write callbacks, default writes, data size, count, emptiness, threshold checks, clear, save-point push/pop/rollback, and merge.

State, persistence, and dependencies: Implementations buffer commands in memory until `write_opt` persists them atomically or backend-specifically. Save points are in-memory rollback markers.

Integration points, risks, and test signals: Used by raft apply, transactions, and batched mutation paths. Risks include atomicity differences across implementations, unclear consequences of exceeding max keys, save-point stack errors, range-delete semantics, callback sequence counts, and merge ownership. Shared tests exercise writes across direct and batch APIs; TiRocks tests cover thresholds and merges.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits/src/write_batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/Cargo.toml -->
# sources/storage-engines/tikv/components/engine_traits_tests/Cargo.toml

Purpose: Defines the engine-agnostic conformance test crate for `engine_traits`.

Important APIs and control flow: Default features select RocksDB KV and raft-engine backends via `engine_test`. Additional features select RocksDB engine pairs or panic engines. Dependencies include encryption export, `engine_test`, `engine_traits`, panic recovery hooks, tempfile, and test utilities. Doctests are disabled for the lib target.

State, persistence, and dependencies: The manifest persists no runtime state but controls which concrete test backend is instantiated.

Integration points, risks, and test signals: This crate is the shared behavioral gate for implementors. Risks include feature combinations hiding backend failures, tests covering only basic semantics, and dependency on `engine_test` constructors. Running this crate under each feature set is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/basic_read_write.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/basic_read_write.rs

Purpose: Verifies that non-CF mutation/read APIs target the default column family.

Important APIs and control flow: The test opens an engine with `ALL_CFS`, writes `foo=bar` through `put`, and reads it through `get_value_cf(CF_DEFAULT, ...)`.

State, persistence, and dependencies: Persistent test state is one key in the default CF inside a temporary engine directory.

Integration points, risks, and test signals: Validates API equivalence between non-CF and default-CF variants. A failure indicates incorrect default CF mapping or write/read routing in an implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/basic_read_write.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/cf_names.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/cf_names.rs

Purpose: Tests column-family name reporting through `CfNamesExt`.

Important APIs and control flow: `default_names` opens a default-only engine and expects one name equal to `CF_DEFAULT`. `cf_names` opens `ALL_CFS` and checks every expected CF is present.

State, persistence, and dependencies: Test engines create temporary DB directories with selected CFs; assertions read engine metadata.

Integration points, risks, and test signals: Provides a basic signal that constructors and `cf_names` expose CF metadata consistently. It does not require ordering for all-CF engines, only membership.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/cf_names.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/checkpoint.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/checkpoint.rs

Purpose: Tests encrypted checkpoint creation and cleanup through the generic checkpoint traits.

Important APIs and control flow: The test creates a file-security config and key manager, opens an encrypted engine with all CFs, writes and syncs a key, creates a checkpoint at another path, reopens the checkpoint with the same encrypted options, verifies the key, drops engines, trashes both directories through encryption-aware cleanup, and expects the key manager file count to return to zero.

State, persistence, and dependencies: State includes encrypted DB files, checkpoint files, key-manager metadata, and temporary directories.

Integration points, risks, and test signals: Covers `Checkpointable`, `Checkpointer`, encryption metadata linking, checkpoint reopenability, and cleanup. Risks caught include missing encrypted file links, incomplete checkpoint state, and leaked key metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/checkpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/ctor.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/ctor.rs

Purpose: Tests generic engine construction behavior across basic, option-based, filesystem, and encryption rename cases.

Important APIs and control flow: Tests call `new_kv_engine` and `new_kv_engine_opt`, verify missing directories are created and writable, expect read-only directories to fail, and test encrypted DB reopen after directory rename by linking and deleting encryption metadata correctly. The renamed-dir test writes `foo=bar`, renames the DB directory, updates key-manager links, and verifies data at the new path.

State, persistence, and dependencies: Uses temporary directories, filesystem permissions, encryption key manager metadata, and persisted KV data.

Integration points, risks, and test signals: Validates constructor contracts used by all shared tests. Risks include missing directory creation, permission handling differences, CF option construction errors, and encryption metadata becoming path-stale after rename.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/ctor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/delete_range.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/delete_range.rs

Purpose: Tests invalid CF behavior for range deletes.

Important APIs and control flow: Opens a default-only engine, calls `delete_range_cf("bogus", b"a", b"b")`, and expects panic/error recovery through `panic_hook::recover_safe`.

State, persistence, and dependencies: No data should be persisted; only CF lookup/error behavior is exercised.

Integration points, risks, and test signals: Signals that implementations reject unknown CFs for range deletes rather than silently applying to default or succeeding. The test expects an unwind path, so implementations that return ordinary errors may need alignment with existing test expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/delete_range.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/iterator.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/iterator.rs

Purpose: Provides shared conformance tests for engine and snapshot iterator semantics.

Important APIs and control flow: Generic helper functions test empty iterators, forward/reverse traversal, seek-then-forward, seek-then-reverse, changing direction, `seek_for_prev`, seek misses, and seek-for-prev misses. Each helper is run against both direct engine iterators and snapshot iterators over `CF_DEFAULT`. Invalid iterator states are expected to return false for validity and to error or panic on movement/key/value access.

State, persistence, and dependencies: Each test writes small ordered key sets into temporary engines. Snapshot iterator tests rely on snapshot-created consistent views.

Integration points, risks, and test signals: This is the main behavioral signal for iterator validity, ordering, direction changes, and miss positioning. Risks include backend differences in invalid movement behavior, key/value access panics, and seek semantics at boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/iterator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/lib.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/lib.rs

Purpose: Organizes the engine-trait conformance suite and provides common temporary engine constructors.

Important APIs and control flow: The module list includes basic reads/writes, CF names, checkpoints, constructors, delete ranges, iterators, misc, read consistency, scenario writes, snapshots, SSTs, and write batches. `TempDirEnginePair` ensures the engine drops before the tempdir. `default_engine`, `multi_batch_write_engine`, and `engine_cfs` construct `KvTestEngine` instances through `engine_test`; `tempdir` creates isolated directories; `assert_engine_error` validates `Error::Engine`.

State, persistence, and dependencies: Test state is isolated in tempdirs and created through feature-selected concrete engines.

Integration points, risks, and test signals: Provides reusable setup for all shared tests. Risks include feature-selected backend behavior hiding generic contract violations and helper drop-order mistakes causing directory cleanup issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/misc.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/misc.rs

Purpose: Tests basic miscellaneous engine behavior: syncing and path reporting.

Important APIs and control flow: `sync_basic` writes `foo=bar`, calls `sync`, and reads the value back. `path` checks that `engine.path()` equals the tempdir path used to construct the engine.

State, persistence, and dependencies: Persistent state is one key plus any backend sync/WAL behavior. Path state is constructor metadata.

Integration points, risks, and test signals: Signals that `KvEngine::sync` is callable after writes and that `MiscExt::path` reports the actual DB root. It does not prove crash durability, only API success and readback.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/misc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/read_consistency.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/read_consistency.rs

Purpose: Tests snapshot and iterator read consistency while later writes and deletes occur.

Important APIs and control flow: `snapshot_with_writes` captures a snapshot after writing `a`, then verifies it does not see later key `b` and still sees deleted key `a`. `iterator_with_writes` creates an iterator after keys `a` and `c`, then verifies later inserted keys are not seen and later deletes do not alter the iterator's view. The helper is run for engine-created iterators and snapshot-created iterators.

State, persistence, and dependencies: Temporary engine state mutates after snapshots/iterators are created; expected view state is pinned by the iterator/snapshot.

Integration points, risks, and test signals: Catches implementations whose engine iterators are live cursors rather than snapshot-consistent views. Risks include backend snapshot isolation gaps and iterator invalidation after writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/read_consistency.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/scenario_writes.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/scenario_writes.rs

Purpose: Parameterizes basic write/delete/range-delete behavior across direct engine APIs, CF APIs, and write-batch APIs.

Important APIs and control flow: `WriteScenario` selects non-CF, default-CF, other-CF, and write-batch variants. `WriteScenarioEngine` routes put/delete/delete-range/get calls to the selected API and verifies non-CF/default-CF reads agree. The `scenario_test!` macro expands each scenario into six modules. Cases cover missing values, put/get, deleting absent and present keys, inclusive/exclusive range deletes, all-in-range deletes, equal begin/end no-op, and reversed range panic/recovery.

State, persistence, and dependencies: Each scenario creates a temporary all-CF engine and mutates either default or write CF; write-batch scenarios persist through `WriteBatch::write`.

Integration points, risks, and test signals: Strong signal that direct and batched mutation APIs share semantics. Risks include CF routing errors, write-batch commit omissions, range bound handling, and reversed ranges not failing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/scenario_writes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/snapshot_basic.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/snapshot_basic.rs

Purpose: Tests point reads from snapshots for default and named column families.

Important APIs and control flow: Tests write a key, take a snapshot, read existing and missing keys, then mutate the engine and verify the snapshot still returns the old value. CF-specific tests repeat the pattern for `CF_WRITE` on an all-CF engine.

State, persistence, and dependencies: Engine state changes after snapshot creation, but snapshot read state must remain fixed.

Integration points, risks, and test signals: Validates `KvEngine::snapshot`, `Snapshot + Peekable`, and CF-specific snapshot reads. Risks include snapshot views not pinning sequence numbers, named CF handle mistakes, and post-write visibility leaks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/snapshot_basic.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/sst.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/sst.rs

Purpose: Tests generic SST writer, reader, iterator, and metadata contracts.

Important APIs and control flow: Tests build SST writers through `SstWriterBuilder`, expect finishing an empty writer to return an engine error, write ordered keys and read them with `SstReader` iterators forward/reverse, verify delete-only SSTs produce invalid data iterators, reject duplicate or reverse-order keys, and validate external SST metadata such as file path, smallest/largest key, entry count, and file size. Sequence-number metadata has an ignored placeholder test.

State, persistence, and dependencies: Each test creates a temporary SST file and reads filesystem metadata. Reader/writer behavior may involve backend table format and optional encryption manager support, though these tests pass `None`.

Integration points, risks, and test signals: Covers import/backup-ready external SST semantics. Risks include incorrect ordered-key enforcement, tombstone-only iterator visibility, metadata mismatch with actual file size, delete entry counting, and untested sequence-number behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/sst.rs -->
