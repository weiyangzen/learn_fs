# subset-b-008830 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/config.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/config.rs

Purpose: defines the serializable RocksDB/Titan configuration enums and serde adapters used by TiKV's RocksDB engine layer.

Important APIs/types/functions: `LogLevel`, `CompressionType`, `BlobRunMode`, `compression_type_level_serde`, `compression_type_serde`, `checksum_serde`, `prepopulate_block_cache_serde`, and numeric serde modules for compaction priority, rate limiter mode, compaction style, and recovery mode. `From` and `TryFrom<ConfigValue>` bridge online configuration values to RocksDB/Titan raw enums.

Control flow: deserializers normalize strings, validate enum names and fixed compression-per-level length, then return RocksDB enum values. `BlobRunMode::from_str` accepts both user-facing kebab-case and Titan internal `k*` spellings.

State and persistence behavior: this module holds no runtime state, but its encodings govern persisted config files and online config mutation payloads.

Dependencies/integration: depends on `rocksdb`, `serde`, `online_config::ConfigValue`, and `tikv_util::numeric_enum_serializing_mod`; consumed by higher-level TiKV config structs and option builders.

Risks: panics on non-string `ConfigValue` inputs for compression/blob mode conversions; compatibility depends on keeping spelling aliases stable. Fixed seven-level compression validation will reject any future RocksDB level-count change.

Test signals: unit tests cover compression-per-level TOML serialization, invalid length, and invalid value handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/db_options.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/db_options.rs

Purpose: wraps RocksDB database and Titan database option objects behind `engine_traits` option traits.

Important APIs/types/functions: `RocksDbOptions`, `RocksTitanDbOptions`, `DbOptionsExt for RocksEngine`, `DbOptions for RocksDbOptions`, and `TitanCfOptions for RocksTitanDbOptions`. The wrappers expose raw conversion, deref access, rate limiter mutation, write-buffer-manager flush controls, Titan option installation, WAL manifest verification, and background job inspection.

Control flow: `RocksEngine::get_db_options` snapshots raw options from the live DB; `set_db_options` forwards string option pairs to RocksDB. Mutators check optional RocksDB subcomponents such as rate limiter and write buffer manager and return errors if absent.

State and persistence behavior: changes affect live DB behavior and, for options RocksDB persists in manifests or option files, future recovery semantics. Rate limiter and write buffer manager mutations alter shared runtime state.

Dependencies/integration: bridges `engine_traits::{DbOptions, DbOptionsExt, TitanCfOptions}` to `rocksdb::{DBOptions, TitanDBOptions}`.

Risks: missing subcomponents produce runtime errors; deref exposes raw option methods, so callers can bypass trait-level invariants. `set_db_options` relies on RocksDB string validation.

Test signals: no local tests in this file; coverage is indirect through engine construction, import, flush, and Titan tests in neighboring modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/db_options.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/db_vector.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/db_vector.rs

Purpose: adapts `rocksdb::DBVector` to the engine abstraction's owned byte-vector trait.

Important APIs/types/functions: `RocksDbVector`, `from_raw`, `DbVector` impl, `Deref<Target=[u8]>`, `Debug`, and `PartialEq<&[u8]>`.

Control flow: values returned by RocksDB reads are wrapped with `from_raw`; callers dereference to bytes without copying. Debug formatting delegates to the byte slice.

State and persistence behavior: the wrapper owns the read value materialized by RocksDB. It does not persist state and has no mutation behavior.

Dependencies/integration: used by `RocksEngine` `Peekable` methods as `type DbVector`; depends on `engine_traits::DbVector` and `rocksdb::DBVector`.

Risks: equality is implemented for `&[u8]` only, so other comparisons rely on deref coercion. Debug output dumps raw bytes, which may be verbose or sensitive in logs.

Test signals: no direct tests; read/get tests in `engine.rs` validate behavior through dereferencing and equality checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/db_vector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/decode_properties.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/decode_properties.rs

Purpose: provides shared binary decoding primitives for RocksDB user-collected table properties.

Important APIs/types/functions: `IndexHandle`, `IndexHandles`, `IndexHandles::{new, into_map, add, encode, decode}`, and `DecodeProperties::{decode, decode_u64, decode_handles}`.

Control flow: `IndexHandles::encode` writes a sequence of key length, key bytes, handle size, and handle offset using TiKV number encoding. `decode` reads until the buffer is exhausted. `DecodeProperties` implementations expose keyed property blobs and typed helpers.

State and persistence behavior: the encoded format is stored in SST user properties and must remain compatible for range and MVCC property readers.

Dependencies/integration: used by `properties.rs` and `mvcc_properties.rs`; integrates RocksDB `UserCollectedProperties` with TiKV codec APIs.

Risks: malformed lengths can produce decode errors; duplicate keys overwrite earlier handles because decoding inserts into a `BTreeMap`. Format changes would break old SST metadata unless fallback logic is maintained.

Test signals: no direct tests here; exercised by range and MVCC property tests that encode/decode handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/decode_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/encryption.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/encryption.rs

Purpose: adapts TiKV's data key manager to RocksDB's encrypted environment interface.

Important APIs/types/functions: `get_env`, `WrappedEncryptionKeyManager`, `EncryptionKeyManager` impl, `convert_file_encryption_info`, and `convert_encryption_method`.

Control flow: `get_env` returns the existing base environment when no key manager exists; otherwise it builds a key-managed encrypted RocksDB env around a provided or default base env. RocksDB calls are forwarded to `DataKeyManager` and converted into RocksDB encryption info.

State and persistence behavior: encryption metadata is managed by `DataKeyManager`; RocksDB file creation, lookup, deletion, and link operations route through this wrapper, affecting how SST/WAL files are encrypted on disk.

Dependencies/integration: used by crate-level `get_env` in `lib.rs`, then layered with file-system inspection. Depends on `encryption`, `kvproto::encryptionpb`, and `rocksdb::EncryptionKeyManager`.

Risks: conversion must stay exhaustive with protobuf and RocksDB method enums; file link/delete forwarding must match RocksDB lifecycle expectations or encrypted file metadata can leak or go stale.

Test signals: no direct tests in this file; exercised indirectly by env construction and encrypted RocksDB deployments.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/encryption.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/engine.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/engine.rs

Purpose: implements the core `KvEngine`, `Iterable`, `Peekable`, and `SyncMutable` traits for a RocksDB-backed TiKV engine.

Important APIs/types/functions: `RocksEngine`, `new`, `as_inner`, `get_sync_db`, `support_multi_batch_write`, optional tablet lifetime tracing, and trait methods for snapshot, WAL sync, iterator creation, get, put, delete, and delete range.

Control flow: construction wraps `rocksdb::DB` in `Arc`, records multi-batch support, optionally registers trace lifetime data, and creates an ingest `RangeLatch`. Reads convert engine options to Rocks read options and fetch from default or named CF. Writes resolve CF handles and call RocksDB writable methods.

State and persistence behavior: owns the shared DB handle; snapshots hold point-in-time views; mutations persist through RocksDB WAL/SST mechanisms. `ingest_latch` coordinates ingestion with compaction-filter writes.

Dependencies/integration: central type re-exported by `lib.rs` and extended by many sibling modules.

Risks: `bad_downcast` panics on mismatched types; iterator and CF operations fail at runtime for missing CFs. Trace-lifetime parsing assumes tablet path naming.

Test signals: unit and proptest coverage validates get/put/delete/scan/snapshot behavior and Rocks/Titan equivalence under random operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/engine_iterator.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/engine_iterator.rs

Purpose: wraps RocksDB iterators in the engine abstraction and exposes iterator perf counters.

Important APIs/types/functions: `RocksEngineIterator`, `from_raw`, `RocksIterMetricsCollector`, `MetricsExt`, and `engine_traits::Iterator` methods.

Control flow: seek operations translate engine calls to RocksDB `SeekKey`; movement calls guard against invalid iterators unless `nortcheck` is enabled; key/value access asserts validity in checked builds.

State and persistence behavior: holds a RocksDB iterator over an `Arc<DB>` and reads a consistent Rocks iterator view according to the read options used during construction. No persistent state is modified.

Dependencies/integration: created by `RocksEngine::iterator_opt`; metrics pull from RocksDB thread-local `PerfContext`.

Risks: invalid iterator movement returns errors or panics depending on feature flags; callers must respect iterator validity before accessing key/value. Metrics are thread-local and only meaningful when perf context is configured.

Test signals: iterator behavior is exercised by scan/seek tests in `engine.rs` and delete-range tests in `misc.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/engine_iterator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/event_listener.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/event_listener.rs

Purpose: implements RocksDB event listeners for metrics, IO-type attribution, background-error handling, SST recovery scheduling, and persistence progress callbacks.

Important APIs/types/functions: `RocksEventListener`, `resolve_sst_filename_from_err`, `RocksPersistenceListener`, and `rocksdb::EventListener` callbacks for flush, compaction, ingestion, background errors, stalls, memtable seal, and flush completion.

Control flow: begin callbacks tag current IO type; completion callbacks increment metrics and reset IO type. Background errors ignore recoverable no-space flush/compaction errors, optionally schedule SST recovery for corruption/IO errors, reset status on accepted recovery, or panic after setting corruption panic marks. Persistence callbacks convert memtable/flush metadata into `PersistenceListener` events.

State and persistence behavior: mutates global metrics, IO-type thread state, critical-error counters, panic marks, and external persistence progress storage.

Dependencies/integration: hooks into RocksDB option event listeners, TiKV scheduler, file-system IO limiter, and raftstore persistence tracking.

Risks: SST filename regex only captures a slash plus word `.sst`, so unusual paths may not recover. Background panic policy is intentionally severe.

Test signals: tests cover SST filename extraction and persistence listener sequencing across flushes and merged memtables.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/event_listener.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/file_system.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/file_system.rs

Purpose: wraps TiKV file-system IO inspection/rate limiting in a RocksDB environment.

Important APIs/types/functions: `get_env` and `WrappedFileSystemInspector<T>`.

Control flow: `get_env` starts from a provided or default RocksDB env, builds an `EngineFileSystemInspector` from an optional IO limiter, and creates an inspected RocksDB env. The wrapper forwards read/write byte requests and converts errors between engine and RocksDB representations.

State and persistence behavior: does not own durable state, but every RocksDB file read/write through the env can update limiter statistics and be throttled or accounted.

Dependencies/integration: layered after encryption by crate-level `get_env`; used by DB options during engine construction. Depends on `engine_traits`, `file_system`, and RocksDB env wrappers.

Risks: the wrapper only exposes read/write inspection; other filesystem operations rely on base env behavior. Incorrect IO type attribution from listeners would affect statistics classification.

Test signals: `test_inspected_compact` validates flush and compaction read/write accounting ranges against a test limiter.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/file_system.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/flow_control_factors.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/flow_control_factors.rs

Purpose: exposes RocksDB flow-control inputs through `engine_traits::FlowControlFactorsExt`.

Important APIs/types/functions: `get_cf_num_files_at_level`, `get_cf_num_immutable_mem_table`, and `get_cf_pending_compaction_bytes` for `RocksEngine`.

Control flow: each method resolves a column-family handle and delegates to utility functions reading RocksDB properties.

State and persistence behavior: read-only runtime inspection of LSM state; no persistent data is modified.

Dependencies/integration: used by flow-control and ingestion logic to reason about write pressure, L0 file count, immutable memtables, and compaction debt.

Risks: values are optional because RocksDB properties can be missing or unsupported; callers must handle `None`. CF lookup errors propagate.

Test signals: import tests use `get_cf_num_files_at_level` to assert preconditions around L0 ingestion placement.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/flow_control_factors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/flow_listener.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/flow_listener.rs

Purpose: sends storage-flow events derived from RocksDB flush, ingestion, compaction, tablet creation, and tablet destruction.

Important APIs/types/functions: `FlowInfo`, `FlowListener::{new, clone_with, on_created, on_destroyed}`, and `EventListener` callbacks.

Control flow: flush and L0 ingestion compute table data/index/filter bytes and send `Flush`. Non-L0 ingestion sends `Compaction`. Completed compactions distinguish L0-to-non-L0, L0 intra-compaction, and generic compaction events, computing input or reclaimed bytes from table properties and file sets.

State and persistence behavior: maintains a shared channel sender and a region id tag; emits runtime accounting events but does not persist state directly.

Dependencies/integration: consumed by TiKV flow control logic and tablet lifecycle code; depends on RocksDB event metadata and `collections::hash_set_with_capacity`.

Risks: send failures are ignored, so downstream flow accounting can silently miss events. File-name conversion failures skip individual files. Failed compactions are ignored.

Test signals: no direct tests in this file; behavior is typically observed through flow-control integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/flow_listener.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/import.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/import.rs

Purpose: implements external SST ingestion for `RocksEngine`.

Important APIs/types/functions: `ImportExt for RocksEngine`, `ingest_external_file_cf`, `acquire_ingest_latch`, and `RocksIngestExternalFileOptions`.

Control flow: optional ranges acquire `ingest_latch` to serialize with compaction-filter operations when `allow_write` is used. The method resolves the CF, sets move-files and allow-write options, records allow-write metrics, calls optimized RocksDB ingestion, and records blocked/non-blocked duration depending on whether a memtable flush fallback occurred.

State and persistence behavior: moves external SST files into RocksDB, potentially modifies LSM state and WAL-independent data visibility. The latch protects range-local consistency during concurrent writes.

Dependencies/integration: used by snapshot apply, delete-by-writer in `misc.rs`, SST writer builders, and flow-control metrics.

Risks: allow-write ingestion is concurrency-sensitive; incorrect range locking can race compaction-filter writes. Metrics labels contain unusual whitespace in the source string and should be verified by Prometheus users.

Test signals: `test_ingest_multiple_file` builds two external SSTs, forces existing L0 state, and ingests both files successfully.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/import.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/lib.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/lib.rs

Purpose: crate root for TiKV's RocksDB engine implementation and public re-export surface.

Important APIs/types/functions: module declarations, broad `pub use` exports, raw RocksDB perf exports, `flow_control_factors`, `raw`, and crate-level `get_env`.

Control flow: compile-time module wiring mirrors `engine_traits`; `get_env` first applies optional encryption env wrapping, then applies file-system inspection/rate limiting and returns a RocksDB env.

State and persistence behavior: no direct durable state, but exported modules implement persistence. Env composition determines encryption and IO-limiter behavior for future DB file operations.

Dependencies/integration: central integration point for downstream TiKV crates; exposes both abstraction implementations and selected raw RocksDB APIs during ongoing engine abstraction migration.

Risks: broad re-exports can leak raw RocksDB types and make abstraction boundaries harder to enforce. Env wrapper order is significant: encryption wraps base env before file-system inspection.

Test signals: no direct tests; all sibling module tests compile through this crate root.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/logger.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/logger.rs

Purpose: routes RocksDB info-log messages into TiKV structured logging.

Important APIs/types/functions: `RocksdbLogger`, `TabletLogger`, and `RaftDbLogger`, each implementing `rocksdb::Logger`.

Control flow: `logv` maps RocksDB log levels to TiKV `crit`, `error`, `warn`, `info`, or `debug` macros. `TabletLogger` prefixes each message with a tablet name; raft DB logs use raft-specific targets.

State and persistence behavior: no persistent state except `TabletLogger`'s tablet name string. Affects observability, not RocksDB data.

Dependencies/integration: installed into RocksDB options elsewhere; depends on `rocksdb::Logger` and `tikv_util` logging macros.

Risks: unknown log levels are ignored. Raw RocksDB log text is passed through, so noisy logs or sensitive paths may surface in TiKV logs.

Test signals: no direct tests; behavior is observable through RocksDB logging integration in runtime deployments.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/logger.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/misc.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/misc.rs

Purpose: implements miscellaneous engine operations: flushing, range deletion strategies, memtable/LSM stats, WAL sync, background work control, DB existence/lock checks, and engine statistics.

Important APIs/types/functions: `MAX_DELETE_COUNT_BY_KEY`, private `delete_all_in_range_cf_by_ingest`, `delete_all_in_range_cf_by_key`, and `MiscExt for RocksEngine`.

Control flow: flush methods resolve CF handles and configure RocksDB `FlushOptions`. Range deletion dispatches by `DeleteStrategy`: delete files, delete Titan blobs, range tombstones, key-by-key deletes, or generated delete SST ingestion. Delete-by-writer collects keys, switches to SST writer after a threshold, then ingests the delete SST with optional range locking.

State and persistence behavior: mutates memtables, WAL, SST files, blob files, range tombstones, and background/manual compaction state. Some deletes sync WAL when required.

Dependencies/integration: relies on iterator, write batch, import, SST writer, RocksDB properties, and metrics modules.

Risks: delete-file/blob strategies can expose old blob indexes if misused; Titan paths require key-only iteration. Background-work pause toggles global manual-compaction state shared by DB instances.

Test signals: tests cover range deletion strategies, delete-file/blob behavior, prefix-bloom delete range case, and oldest-memtable flush selection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/misc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/mvcc_properties.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/mvcc_properties.rs

Purpose: encodes, decodes, and queries MVCC table properties stored in RocksDB SST user properties.

Important APIs/types/functions: property-name constants, `RocksMvccProperties::{encode, decode}`, and `MvccPropertiesExt for RocksEngine::get_mvcc_properties_cf`.

Control flow: encoding writes timestamps, row/version/delete counts, stale/delete timestamp ranges, and TTL properties into `UserProperties`. Decoding reads required fields and supplies compatibility defaults for older SSTs missing delete/stale fields. Querying aggregates decoded table properties for a range, skipping tables whose minimum timestamp is newer than the safe point.

State and persistence behavior: defines the on-SST metadata format used by GC, split heuristics, and stats. It does not mutate DB data.

Dependencies/integration: used by `properties.rs` collectors and range stats; depends on `engine_traits::MvccProperties`, `txn_types::TimeStamp`, and TTL property helpers.

Risks: missing required properties abort aggregation with `None`; compatibility defaults can over-approximate old data. Safe-point filtering is table-level, not entry-level.

Test signals: collector tests in `properties.rs` validate MVCC encoding/decoding for transactional and RawKV modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/mvcc_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/options.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/options.rs

Purpose: converts engine-trait read, write, and iterator options into RocksDB raw option objects.

Important APIs/types/functions: `RocksReadOptions`, `RocksWriteOptions`, `build_read_opts`, and `TsFilter`.

Control flow: read conversion sets fill-cache; write conversion sets sync, no-slowdown, WAL disable, and disables memtable insert hints. Iterator conversion configures fill-cache, max skippable internal keys, Titan key-only, total-order or prefix seek modes, adaptive readahead, timestamp table filtering, and lower/upper bounds.

State and persistence behavior: options are per-operation and do not persist state. They affect cache pollution, WAL durability, iterator table pruning, and RocksDB read/write behavior.

Dependencies/integration: consumed by `engine.rs`, `engine_iterator.rs`, write-batch code, and MVCC timestamp-aware scans.

Risks: timestamp filtering hard-codes `tikv.min_ts` and `tikv.max_ts` property names. Decode failures in table filter fall through to include the table, preserving correctness but weakening pruning.

Test signals: no direct tests here; exercised through iterator scans, raft log fetches, MVCC property tests, and query paths using timestamp hints.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/options.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/perf_context.rs

Purpose: exposes RocksDB perf-context collection through the engine abstraction.

Important APIs/types/functions: `PerfContextExt for RocksEngine`, `RocksPerfContext`, `RocksPerfContext::new`, and `PerfContext` trait methods `start_observe` and `report_metrics`.

Control flow: callers construct a context for a `PerfLevel` and `PerfContextKind`, call `start_observe` to reset/apply perf settings, then call `report_metrics` with tracker tokens to report captured counters through `PerfContextStatistics`.

State and persistence behavior: operates on RocksDB thread-local perf context and tracker metrics only; no DB data is persisted or modified.

Dependencies/integration: thin facade over `perf_context_impl::PerfContextStatistics`, used by storage, coprocessor, and raftstore request paths.

Risks: metrics are only meaningful if start/report bracket the correct work on the same thread. Disabled perf level makes collection a no-op.

Test signals: implementation logic is tested in `perf_context_impl.rs` field operation tests; runtime correctness is integration-level.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context_impl.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/perf_context_impl.rs

Purpose: captures RocksDB read/write perf counters, reports them to Prometheus and request trackers, and provides instant delta helpers.

Important APIs/types/functions: default perf flag sets, `ReadPerfContext`, `WritePerfContext`, `PerfContextStatistics`, `PerfContextFields`, `PerfStatisticsInstant`, `ReadPerfInstant`, and `WritePerfInstant`.

Control flow: `start` resets RocksDB perf context and applies default flags or explicit level. `report` branches by kind: raftstore write paths observe write latency histograms and tracker fields; storage/coprocessor read paths capture counters, update trackers, accumulate, and periodically flush counters every two seconds.

State and persistence behavior: maintains in-memory accumulated read counters and last flush timestamp. No durable DB state changes.

Dependencies/integration: depends on raw RocksDB perf APIs, Prometheus metrics, TiKV trackers, and `engine_traits::PerfContextKind`.

Risks: uses thread-local RocksDB perf data; cross-thread reporting is invalid. Large metric label lists make drift with RocksDB API possible. `PerfStatisticsInstant` is intentionally `!Send`/`!Sync`.

Test signals: tests validate arithmetic derivations and mutable field access for read perf contexts.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context_impl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context_metrics.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/perf_context_metrics.rs

Purpose: declares Prometheus metrics and static metric label wrappers for RocksDB perf context and SST ingestion timing.

Important APIs/types/functions: `PerfContextType`, `PerfContextTimeDuration`, `CFName`, `IngestType`, `IngestExternalFileTimeDuration`, `From<&str> for CFName`, and lazy static metrics including apply/store histograms, storage/coprocessor counters, ingestion histograms, and allow-write counters.

Control flow: metric macros generate typed label accessors; `CFName::from` normalizes common upper/lower CF names and defaults unknown names to `default`.

State and persistence behavior: owns process-global metric registrations and local auto-flush histogram wrappers. No DB state is persisted.

Dependencies/integration: used by `perf_context_impl.rs` and `import.rs`; depends on `prometheus`, `prometheus_static_metric`, and `lazy_static`.

Risks: unknown CF labels collapse to `default`, which can hide new CFs. Metric registration names and buckets become compatibility surface for monitoring dashboards.

Test signals: no direct tests; metric usage is exercised by perf-context reporting and external-file ingestion paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/properties.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/properties.rs

Purpose: implements SST table-property formats and collectors for range size/key estimates, Titan blob size estimation, MVCC statistics, RawKV TTL stats, and range stats.

Important APIs/types/functions: `SizeProperties`, `UserProperties`, `UserCollectedPropertiesDecoder`, `RangeOffsets`, `RangeProperties`, `RangePropertiesCollector`, factories, `MvccPropertiesCollector`, raw/txn MVCC factories, `get_range_stats`, and Titan compression-factor globals.

Control flow: range collectors count entry sizes/keys and insert offset points after size/key distance thresholds. Titan blob indexes are decoded and adjusted by smoothed compression factor and max blob size. MVCC collectors validate data keys, split timestamps, count rows/versions/puts/deletes/stale versions, build row indexes, and encode final user properties.

State and persistence behavior: writes compact binary metadata into SST user properties; global atomics/smoother influence Titan size estimates. Query functions aggregate persisted table properties.

Dependencies/integration: consumed by split checking, GC/statistics, iterator table filters, and `range_properties.rs`.

Risks: corrupt keys/properties degrade to errors or counters; table-property approximations can drift, especially with Titan compression estimates. RawKV mode depends on API v2 value decoding.

Test signals: extensive tests cover range estimates, blob indexes, range stats, transactional MVCC, RawKV TTL/deletes, and blob entry size estimation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/raft_engine.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/raft_engine.rs

Purpose: implements raft-engine traits over RocksDB for legacy/default raft log persistence.

Important APIs/types/functions: `RaftEngineReadOnly`, `RaftEngineDebug`, `RaftEngine`, and `RaftLogBatch` impls for `RocksEngine`/`RocksWriteBatchVec`; private `gc_impl` and `append_impl`.

Control flow: small raft log fetches use point gets; larger fetches scan key ranges, validate indexes, respect `max_size`, and distinguish compacted vs unavailable entries. Batches append serialized entries, optionally delete overwritten gaps, persist raft/store/bootstrap/recover state, consume with optional sync, clean group data, and iterate region states.

State and persistence behavior: stores raft logs and metadata in default CF under raft key encodings; writes flow through Rocks write batches and WAL sync according to caller options.

Dependencies/integration: ties `keys`, protobuf raft/kvproto messages, `engine_traits::RaftEngine`, and Rocks write batches together.

Risks: raftstore-v2-only methods intentionally panic because this backend is not used for them. Fetch logic asserts strict sequential indexes and returns compacted/unavailable errors based on gaps.

Test signals: no local tests in this file; covered by raftstore and engine trait integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/raft_engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/range_properties.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/range_properties.rs

Purpose: implements high-level range size/key estimation and split-key selection for `RocksEngine`.

Important APIs/types/functions: `RangePropertiesExt for RocksEngine`, including approximate keys, approximate size, per-CF variants, and split-key selection.

Control flow: key estimates prefer write-CF range properties and fall back to MVCC range stats. Size estimates sum large CFs and tolerate missing lock-CF range properties for old versions. Split-key selection chooses the largest CF by approximate size, gathers internal range-property sample keys, downsamples large sets, sorts, and picks evenly spaced keys.

State and persistence behavior: read-only aggregation of memtable stats and SST user properties; no DB mutation.

Dependencies/integration: depends on `MiscExt` property access, `RangeProperties::decode`, `get_range_stats`, TiKV CF constants, and logging wrappers.

Risks: estimates are approximate and can be wrong with stale or missing table properties. Large-threshold logging decodes properties with `unwrap`, assuming prior decode success. Sampling can miss ideal split points.

Test signals: property decoding and split source data are tested in `properties.rs`; this file has no direct tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/range_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/raw.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/raw.rs

Purpose: temporarily re-exports selected raw `rocksdb` crate APIs through `engine_rocks`.

Important APIs/types/functions: public re-exports for options, cache, compression/checksum enums, compaction filters/options, event/listener types, env, rate limiter, table property collectors, write buffer manager, perf context, and RocksDB CLI helper functions.

Control flow: no runtime logic; this is compile-time namespace forwarding.

State and persistence behavior: no direct state. Consumers can use re-exported raw types to configure RocksDB state and persistence indirectly.

Dependencies/integration: supports downstream crates during engine abstraction migration so they need not depend directly on `rocksdb`.

Risks: broad raw API exposure weakens abstraction boundaries and can make later backend swaps harder. Re-export list must track RocksDB crate API changes.

Test signals: no direct tests; compile-time users across TiKV validate that required raw symbols remain exported.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/raw.rs -->
