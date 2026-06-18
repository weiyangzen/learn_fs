# Research: subset-b-008827

Grouped research for the source files assigned to `subset-b-008827`. Each section is source-tree aligned and bounded by the reconciliation markers required by the worker contract.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/consistency.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/consistency.rs

Purpose: implements `StorageConsistencyGuard`, an execution hook that prevents compacting unstable log-backup data. It checks that the requested `until_ts` is not newer than a durable checkpoint, then acquires a remote read lock under `v1/LOCK` for the duration of the compaction.

Important APIs and types: `StorageConsistencyGuard`, internal `CheckpointSource`, `load_storage_checkpoint`, and `load_replication_status_checkpoint`. The default checkpoint source scans `v1/global_checkpoint/*.ts`, parses 8-byte little-endian timestamps, ignores malformed non-`.ts` files, and returns the maximum valid checkpoint. The replication-status source reads `<sub_prefix>/resume-state.json` and requires a numeric `last_checkpoint`.

Control flow: `before_execution_started` optionally loads a checkpoint, rejects `until_ts > checkpoint`, warns and fails when no storage checkpoint exists, then calls `lock_for_read`. `after_execution_finished` unlocks. `on_aborted` also unlocks and logs unlock failures.

State and persistence: persists no new data except the external-storage lock record; it depends on checkpoint objects written by backup-stream components. Lock cleanup is critical because a stale lock can block writers or later compaction attempts.

Dependencies and integration: uses `ExternalStorage`, external-storage locking, `ExecHooks`, `ExecutionConfig`, `ErrorKind`, and `storage_url`. `execute::load_until_ts_from_checkpoint` delegates checkpoint loading here.

Risks: checkpoint JSON schema errors are fatal; malformed storage checkpoint files are ignored, so a deployment with only malformed `.ts` files behaves like no checkpoint. Lock release is best effort on abort, so operator cleanup may be needed after external-storage failures.

Test signals: execution tests cover checkpoint bound rejection/acceptance, lock presence during execution, lock release after success, and unlock-on-abort behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/consistency.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/mod.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/mod.rs

Purpose: declares the compact-log-backup execution-hook modules and provides shared statistic aggregation for hook implementations.

Important APIs and types: exports `checkpoint`, `consistency`, `observability`, `save_meta`, and `skip_small_compaction`; re-exports `SstCompressionType`; defines `CollectStatistic` with `LoadStatistic`, `SubcompactStatistic`, `LoadMetaStatistic`, and `CollectSubcompactionStatistic` fields.

Control flow: `CollectStatistic` is mutated by hooks as execution emits events. `update_subcompaction` accumulates load and compaction statistics from a `SubcompactionResult`; `update_collect_compaction_stat` and `update_load_meta_stat` accumulate the streaming deltas passed through `SubcompactionStartCtx`.

State and persistence: this module has only in-memory counters. Persistence is handled by hooks such as `save_meta`; observability serializes or logs the aggregate stats.

Dependencies and integration: depends on `compaction::SubcompactionResult` and the `statistic` module. It is used by `Observability` for progress reporting and Prometheus observations, and by `SaveMeta` to embed run comments in final migration metadata.

Risks: fields are private to the module, so new hooks outside this module cannot reuse the aggregator unless the API is opened. Statistics are additive deltas; if a hook updates from the wrong event or receives non-delta values, final comments and logs can overcount.

Test signals: no direct tests in this file, but `execute/test.rs` exercises `SaveMeta` and `Observability` paths that depend on these aggregations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/observability.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/observability.rs

Purpose: provides the default TTY/operator-facing `ExecHooks` implementation for compact-log-backup progress, metrics, abort logging, and async backtrace dumping.

Important APIs and types: `Observability { stats, meta_len }` implements `ExecHooks`. It consumes `BeforeStartCtx`, `SubcompactionStartCtx`, `SubcompactionFinishCtx`, `AfterFinishCtx`, and `AbortedCtx`.

Control flow: before execution it initializes `tracing_active_tree`, spawns a SIGUSR1 handler that writes `/tmp/compact-sst.dump`, records total metadata object count, and logs config and storage URL. Before each subcompaction it accumulates metadata/collector deltas and logs region, CF, time range, input count, and size. After each subcompaction it aggregates result stats, observes Prometheus histograms, computes a rough logical-byte throughput, and logs global progress. On finish it rejects empty non-sharded runs but allows empty shard matches.

State and persistence: in-memory stats only, plus optional `/tmp/compact-sst.dump` written on SIGUSR1. Prometheus histograms are process-global.

Dependencies and integration: integrates with `statistic::prom`, `storage_url`, Tokio Unix signals, TiKV logging macros, and the execution hook lifecycle.

Risks: `SignalKind::user_defined1()` and Unix signal support are platform-specific. Throughput divides by elapsed milliseconds; extremely fast compactions can produce inf/nan-like values. The empty-input policy is intentionally asymmetric for sharded vs unsharded compactions.

Test signals: indirectly covered by execution tests that rely on hook lifecycle; empty-input behavior is a likely area for targeted tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/observability.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/save_meta.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/save_meta.rs

Purpose: persists compact-log-backup output metadata. It writes batched subcompaction metadata under the compaction artifact prefix and emits a final BR-readable migration describing generated SSTs and metadata edits.

Important APIs and types: `SaveMeta`, `BatchConfig`, `MetaBatchWriter`, `CheckpointInput`, `CheckpointedSubcompaction`, `load_checkpointed_subcompactions`, and `final_artifacts_prefix`. `CheckpointedSubcompaction` canonicalizes source spans by sorting inputs, allowing checkpoint hooks to compare completed work independent of ordering.

Control flow: `before_execution_started` initializes run metadata, artifact paths, generated SST path, and the batch writer. `before_a_subcompaction_start` accumulates load/collection stats. `after_a_subcompaction_end` adds the result to `CompactionRunInfoBuilder`, updates stats, and appends the `LogFileSubcompaction` proto to the batch writer; the writer flushes when either subcompaction count or encoded bytes exceeds configured limits. `on_subcompaction_skipped` preserves already-done subcompactions in the collector. `after_execution_finished` flushes pending batches, adds JSON comments, and writes the migration.

State and persistence: writes `metas/batch_<run_uuid>_<seq>.cmeta` files and a migration under `v1/migrations`. It reads existing `.cmeta` batches for checkpoint recovery, ignoring corrupt or unreadable batches with warnings.

Dependencies and integration: integrates with `ExecHooks`, `CompactionRunInfoBuilder`, `MigrationStorageWrapper`, protobuf, `ExternalStorage`, retry wrappers, and UUIDs. It is essential for real restore because raw SST outputs alone are insufficient.

Risks: final migration write is the commit point; `.cmeta` batches from failed attempts can remain and are intentionally reused by checkpointing. Corrupt checkpoint batches are ignored, so partial external-storage corruption can cause re-execution. The writer must be initialized before subcompactions finish or it returns an explicit error.

Test signals: execution tests validate simple migration output, batched checkpoint reuse across failed attempts, small-compaction skipping persistence, and migration contents.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/save_meta.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/skip_small_compaction.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/skip_small_compaction.rs

Purpose: implements a lightweight hook that avoids executing subcompactions whose original KV payload is below a configured threshold.

Important APIs and types: `SkipSmallCompaction { size_threshold }`, constructor `new`, and its `ExecHooks::before_a_subcompaction_start` implementation.

Control flow: when a subcompaction is about to start, the hook compares `cx.subc.size` with `size_threshold`. If the size is lower, it logs the decision and calls `SubcompactionStartCtx::skip(SkipReason::NoNeedToDo)`. The execution loop then invokes `on_subcompaction_skipped` on all hooks and does not spawn the worker task.

State and persistence: no local persistence. Because it uses `NoNeedToDo`, `SaveMeta` does not add skipped subcompactions to final migration metadata; only actually executed or checkpoint-already-done work is persisted.

Dependencies and integration: depends on `ExecHooks`, `CId`, `SkipReason`, and `SubcompactionStartCtx`. It composes with other hooks through the tuple implementation in `execute/hooking.rs`.

Risks: using original KV size rather than physical compressed size is deliberate but can surprise operators comparing object sizes. Hook ordering matters when multiple hooks can call `skip`; the last write to the shared `Cell<Option<SkipReason>>` wins if multiple hooks mutate it.

Test signals: `test_filter_out_small_compactions` runs execution with this hook and verifies final persisted subcompactions all meet the threshold.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/skip_small_compaction.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/execute/hooking.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/execute/hooking.rs

Purpose: defines the hook contract for compact-log-backup execution and the context objects passed at each lifecycle point.

Important APIs and types: `ExecHooks`, `NoHooks`, `CId`, `BeforeStartCtx`, `AfterFinishCtx`, `SubcompactionStartCtx`, `SubcompactionFinishCtx`, `SubcompactionSkippedCtx`, `AbortedCtx`, and `SkipReason`. `SubcompactionStartCtx::skip` writes a skip reason into an internal `Cell`.

Control flow: execution calls `before_execution_started`, `before_a_subcompaction_start`, `after_a_subcompaction_end`, `after_execution_finished`, `on_aborted`, and `on_subcompaction_skipped` at defined points. Default trait methods are no-ops. Tuple composition runs both hooks, using `try_join` for fallible async hooks and `join` for non-fallible abort/skip hooks. `Option<T>` delegates when present.

State and persistence: no persistence; it is the in-memory extension surface. Contexts expose execution config, storage references, result metadata, runtime handles, and per-event statistics.

Dependencies and integration: used by all hook modules and by `execute/mod.rs`. It ties together `Execution`, `ExternalStorage`, `Subcompaction`, `SubcompactionResult`, and statistic deltas.

Risks: async functions in traits are allowed with a local lint exemption and do not require returned futures to be `Send`; hooks must stay compatible with how execution awaits them. Tuple hooks run fallible hook futures concurrently, so side effects can happen in both hooks even if one fails. The skip cell is mutable shared context, so hook ordering can affect the final reason.

Test signals: execution tests compose hooks such as `(SaveMeta, CompactionSpy)`, `(Blocking, StorageConsistencyGuard)`, and checkpoint/save/abort combinations, validating composition and abort semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/execute/hooking.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/execute/mod.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/execute/mod.rs

Purpose: orchestrates compact-log-backup execution: external-storage setup, metadata discovery, subcompaction collection, bounded concurrent SST compaction, hook calls, abort handling, sharding, and checkpoint loading.

Important APIs and types: `create_storage_with_gcp_v2`, `load_until_ts_from_checkpoint`, `ShardConfig`, `parse_shard_config`, `ExecutionConfig`, and `Execution<DB>`. `ShardConfig` hashes store IDs with CRC64 and exposes a stable suffix for output prefixes. `ExecutionConfig::recommended_prefix` hashes operational inputs to produce deterministic artifact prefixes.

Control flow: `run_with_storage_async` wraps `run_prepared` in Ctrl-C abort handling. `run_prepared` counts metadata, updates `shift_ts`, calls `before_execution_started`, streams metadata through `StreamMetaStorage`, collects subcompactions either from logical log files or cached physical files, lets hooks skip work, spawns `SubcompactionExec` tasks up to `max_concurrent_subcompaction`, verifies checksums, drains pending tasks, and calls `after_execution_finished`. Scheduling errors abort and drain all pending tasks.

State and persistence: this module coordinates persistence but writes through lower layers and hooks. Output paths are rooted at `out_prefix`; optional `PhysicalFileCache` stores raw physical files in memory during execution.

Dependencies and integration: depends on `compaction` collectors/executor, `storage::StreamMetaStorage`, `cache::PhysicalFileCache`, hook traits, Tokio, tracing-active-tree, `ExternalStorage`, Rocks SST traits, and BR storage protobufs.

Risks: `tokio::spawn(...).await.unwrap()` in metadata prefetch assumes spawned metadata tasks do not panic. Concurrent hook side effects can fail the whole run. Shard filtering requires parseable backupmeta names only in shard mode. `shift_ts` can be derived from metadata names and affects default-CF compaction selection.

Test signals: `execute/test.rs` covers simple execution, checkpoint reuse, consistency locks, sharding validation/union behavior, small-skip behavior, and migration output.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/execute/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/execute/test.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/execute/test.rs

Purpose: integration-style test suite for compact-log-backup execution, hooks, checkpointing, consistency locks, sharding, and metadata persistence.

Important APIs and helpers: `CompactionSpy`, `create_compaction`, `gen_builder`, `gen_store_builders`, `store_paths`, `populate_stores`, `run_exec`, `run_exec_err`, `set_metadata_store_id`, `load_migrations_by_out_prefix`, and `meta_edits_by_path`.

Control flow: tests build temporary external storage with synthetic log-backup metadata, run `Execution` in blocking tasks, receive completed `SubcompactionResult`s through channels, verify generated SST contents via `TmpStorage::verify_result`, and inspect migrations and `.cmeta` batches. The checkpoint test intentionally fails multiple attempts after a fixed number of completed subcompactions, then confirms that only committed batches are reused on a final successful run.

State and persistence: writes local-storage metadata/log files, checkpoint files, lock files, subcompaction metadata batches, and migration files. Helpers rewrite metadata store IDs to test shard safety.

Dependencies and integration: exercises `SaveMeta`, `Checkpoint`, `StorageConsistencyGuard`, `SkipSmallCompaction`, `SubcompactionExec`, `ExternalStorage`, BR protobuf metadata, and sharding config.

Risks covered: checkpoint boundary enforcement, stale lock cleanup on abort, skipped compaction persistence semantics, invalid backupmeta names in shard mode, path/metadata store-ID mismatches, and equivalence between unioned shard migrations and unsharded migration output.

Test signals: this file is itself the strongest signal for the execution stack. It validates both behavioral output and persistence artifacts, not just function-level return values.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/execute/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/lib.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/lib.rs

Purpose: crate root for the compact-log-backup component. It wires internal modules, public modules, feature gates, and public error/config exports.

Important APIs and types: public modules `test_util`, `exec_hooks`, and `execute`; re-exports `Error`, `ErrorKind`, `OtherErrExt`, `Result`, `TraceResultExt`, and `execute::ShardConfig`. Internal modules include `cache`, `compaction`, `errors`, `source`, `statistic`, `storage`, and `util`.

Control flow: no runtime flow in this file. It defines visibility boundaries: execution and hooks are exposed, while storage/source/statistic internals remain crate-private except through public APIs and test utilities.

State and persistence: none directly. Persistence functionality is rooted in `storage`, `source`, and `exec_hooks::save_meta`.

Dependencies and integration: enables nightly features `test` and `custom_test_frameworks`, indicating benchmark/test infrastructure depends on unstable Rust. The public surface is consumed by TiKV tooling or tests that run compact-log-backup.

Risks: exposing `test_util` publicly behind `#![cfg(test)]` content in the file itself can be confusing; consumers only see it in test builds. The crate root does not expose most low-level storage types, so external callers should use `execute` and hook modules rather than bypass internals.

Test signals: module-level tests are spread across the internal modules; this root’s main validation is successful crate compilation and test discovery with the enabled nightly features.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/source.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/source.rs

Purpose: loads compact-log-backup input log segments from external storage, optionally through the physical-file cache, decompresses them, and iterates encoded key/value events for compaction.

Important APIs and types: `Source`, `Record`, `Source::new`, `cache_input_refs`, `load_remote`, `load`, `Record::cmp_key`, and `Record::ts`. Internal helpers `load_compressed` and `decompress` support Zstd-compressed BR log backup data.

Control flow: `load_remote` retries reads, first attempting `PhysicalFileCache::load_part` when configured, then falling back to `read_part` on external storage. It decompresses into memory and updates physical-byte/error stats. `load` parses the decompressed event stream with `EventIterator`, periodically yields via `Cooperate`, invokes a caller callback for each key/value pair, and updates logical input stats.

State and persistence: reads remote objects only. Optional cache references are RAII guards that reserve physical files while subcompactions need their segments.

Dependencies and integration: used by `SubcompactionExec` through `compaction::Input`. Depends on `ExternalStorage`, `PhysicalFileCache`, BR compression proto, TiKV stream-event codec, transaction timestamp decoding, and `LoadStatistic`.

Risks: only Zstd compression is supported here; other compression enum values return `Unsupported`. Entire segment contents are decompressed into memory, so subcompaction sizing and cache capacity matter. Callback execution happens inline and can affect cooperative scheduling.

Test signals: tests build synthetic Zstd log files, load each segment, verify keys/values and statistics, and validate cache reference release behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/source.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/statistic.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/statistic.rs

Purpose: defines serializable statistics and Prometheus metrics for compact-log-backup loading, collection, compaction, and whole-run reporting.

Important APIs and types: `CompactLogBackupStatistic`, `LoadMetaStatistic`, `LoadStatistic`, `SubcompactStatistic`, `CollectSubcompactionStatistic`, and `prom::SerAll`. Statistic structs derive `Add` and `AddAssign` for aggregation and use kebab-case serialization.

Control flow: execution and hooks accumulate statistics as metadata is loaded, source files are read, subcompactions are collected, and SSTs are written. `prom::SerAll` serializes current process-global histograms into a map when final comments are generated by `SaveMeta`.

State and persistence: local counters are in-memory until serialized into migration comments. Prometheus histograms are registered globally and retain process-wide samples.

Dependencies and integration: used by `source`, `storage`, collectors, `execute`, `observability`, and `save_meta`. Prometheus histograms cover metadata reads, single-file loading, whole-load duration, sorting, saving, and SST writing.

Risks: process-global histograms can include samples from multiple executions in the same process. `Duration` serialization depends on Serde’s duration representation. Additive aggregation assumes each caller passes deltas rather than cumulative values.

Test signals: no direct unit tests in this file, but execution tests indirectly validate stats propagation through SaveMeta comments and Observability paths. Metric registration failures would surface at crate initialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/statistic.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/storage.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/storage.rs

Purpose: models log-backup metadata in memory, streams metadata objects from external storage, applies migration-based filters, supports sharding by backupmeta path store ID, and persists/loads compaction migrations.

Important APIs and types: constants `METADATA_PREFIX`, `DEFAULT_COMPACTION_OUT_PREFIX`, `MIGRATION_PREFIX`, `LOCK_PREFIX`, `MIGRATION_APPEND_LOCK`; `MetaFile`, `PhysicalLogFile`, `LogFile`, `LogFileId`, `Epoch`, `LoadFromExt`, `CountObjectsExt`, `StreamMetaStorage`, `VersionedMigration`, `MigrationStorageWrapper`, `name_of_migration`, `id_of_migration`, `hash_migration`, and `hash_meta_edit`.

Control flow: `StreamMetaStorage::load_from_ext` creates an external-storage prefix stream and loads migrations into `MetaEditFilters`. Its `Stream` implementation maintains ordered prefetch: it fetches object names, filters fully compacted metadata, shard-filters by parsed store ID before reading, spawns metadata loading tasks, and yields loaded `MetaFile`s in input order. `count_objects` counts metadata and optionally computes `shift_ts` from backupmeta filename ranges. `MigrationStorageWrapper::write` serializes migration append with a remote write lock.

State and persistence: reads `v1/backupmeta`, writes and reads `v1/migrations`, and uses `v1/APPEND_LOCK` for migration append coordination. Metadata edits can delete full physical files, logical spans, or entire metadata files.

Dependencies and integration: central to `execute/mod.rs`, `SaveMeta`, sharding, checkpointing, and tests. Uses BR protobufs, external storage, retry helpers, protobuf parsing, CRC64 hashing, and TiKV tracing/statistics.

Risks: backupmeta filename parsing is required for shard mode and optional shift-ts calculation. `tokio::spawn(...).await.unwrap()` in callers assumes loader tasks do not panic. Migration filters are append-only and must remain deterministic because they influence future compaction input. Hashes are integrity identifiers, not cryptographic proofs.

Test signals: tests cover backupmeta parsing, concurrent metadata loading, custom prefixes, migration filter merging/application, shift-ts counting, parse failures, and shard-related execution paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/test_util.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/test_util.rs

Purpose: supplies compact-log-backup test infrastructure for generating synthetic log files, temporary storage, expected compaction output, and result verification.

Important APIs and types: `Kv`, `LogFileBuilder`, `CompactInMem`, `RecordSorted`, `KvGen`, `KeySeed`, `TmpStorage`, `verify_the_same`, `sow`, `gen_step`, `gen_adjacent_with_ts`, `gen_min_max`, `build_many_log_files`, `save_many_log_files`, and `save_many_logs_files`.

Control flow: `LogFileBuilder` encodes stream-event key/value records into a Zstd buffer while tracking timestamps, key bounds, CRC64, entry count, and SHA256. Flush helpers combine builders into BR `Metadata` and physical log files. `TmpStorage` creates local external storage, builds backup flushes, runs subcompactions, loads migrations/subcompaction batches, and verifies generated SST files against an in-memory sorted/deduped expectation.

State and persistence: writes temporary local-storage objects and leaks the temp directory only on test panic to aid debugging. `CompactInMem` stores expected compacted KV state in a `BTreeMap`.

Dependencies and integration: used heavily by source, storage, compaction, and execution tests. Depends on Rocks SST readers/writers, external storage, BR protobufs, stream-event encoding, table row-key encoding, transaction keys, and SHA256 utilities.

Risks: helper assumptions mirror current production output, such as one SST per result and specific SST filename parts; changes in production naming or splitting require test utility updates. `CompactInMem::must_iter` panics if concurrent writes remain.

Test signals: this file is test-only and enables most higher-level behavioral validation across compact-log-backup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/test_util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/util.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/util.rs

Purpose: provides small shared helpers for cooperative async execution, unordered future selection, bounded concurrent execution, CF parsing, formatting, compression encoding, key redaction, end-key ordering, and storage URL rendering.

Important APIs and types: `Cooperate`, `Step`, `select_vec`, `ExecuteAllExt`, `execute_all_ext`, `cf_name`, `aligned_u64`, `compression_type_to_u8`, `redact`, `EndKey`, and `storage_url`.

Control flow: `Cooperate::step` returns a future that yields every configured number of operations. `select_vec` polls a vector of futures and `swap_remove`s the first ready future. `execute_all_ext` submits futures up to `max_concurrency` and gathers results with error propagation.

State and persistence: no persistence. `Cooperate` tracks only per-instance counters.

Dependencies and integration: used by source loading, execution task waiting, metadata prefix hashing, storage logging, and compaction logic that needs TiKV CF names or end-key ordering.

Risks: `select_vec` is intentionally unordered and mutates future vector order, so callers must not rely on stable completion ordering. `execute_all_ext` requires `Unpin` futures. `cf_name` maps unknown CF strings to `"ERR_CF"`, relying on downstream filtering rather than returning an error. `compression_type_to_u8` must stay in sync with `SstCompressionType` variants for stable prefix hashing.

Test signals: no direct tests here; behavior is indirectly exercised by execution scheduling, source event iteration, shard prefix generation, and compaction collection tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/Cargo.toml -->
# sources/storage-engines/tikv/components/concurrency_manager/Cargo.toml

Purpose: package manifest for TiKV’s `concurrency_manager` crate, which provides in-memory transaction lock checking and max-ts tracking.

Important APIs and types: declares crate metadata, dependencies, dev-dependencies, and two Criterion benchmark targets: `lock_table` and `update_max_ts`.

Control flow: no runtime control flow. Build behavior is shaped by dependencies: `tokio` with macros/sync/time, `crossbeam-skiplist`, `pd_client`, `txn_types`, `prometheus`, `fail`, `mockall`, and TiKV utility crates.

State and persistence: none directly; dependency selection implies all state is in-memory and metrics-based rather than on-disk.

Dependencies and integration: `crossbeam-skiplist` backs the lock table; `pd_client` supplies TSO; `txn_types` supplies keys, locks, and timestamps; `prometheus` exports gauges; `tikv_alloc` with jemalloc is available only in dev tests for memory usage.

Risks: `mockall` is a normal dependency rather than dev-only because `#[automock]` appears in library code. The crate is unpublished and workspace-bound, so versioning is internal. Benchmarks require `harness = false`.

Test signals: dev dependencies support Criterion benches, futures executor for blocking tests/benches, random workload generation, and allocator statistics for ignored memory tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/benches/lock_table.rs -->
# sources/storage-engines/tikv/components/concurrency_manager/benches/lock_table.rs

Purpose: Criterion benchmark suite for point and range lock checks in `ConcurrencyManager` with 10,000 resident in-memory locks.

Important APIs and types: constants `KEY_LEN` and `LOCK_COUNT`, helper `prepare_cm`, and benchmark functions `point_check_baseline`, `bench_point_check`, `range_check_baseline`, and `bench_range_check`.

Control flow: `prepare_cm` creates random 64-byte keys, locks each key, stores a `Lock`, then leaks the guard with `forget` so the lock remains present. Point benchmarks compare random key construction baseline against `read_key_check` plus `txn_types::check_ts_conflict`. Range benchmarks compare random range key construction against `read_range_check` over a rough tenth of the one-byte key space.

State and persistence: in-memory only. Guards are intentionally leaked for benchmark setup, so this code is not a production pattern.

Dependencies and integration: exercises `ConcurrencyManager`, `txn_types::Lock`, `TsSet`, `IsolationLevel`, Criterion, random generation, and futures `block_on` for async lock acquisition.

Risks: random duplicate keys are ignored as “really rare”; actual lock count can be slightly below target. Leaking guards avoids teardown costs but can hide drop-time behavior. Range key distribution uses single-byte bounds, unlike real encoded TiKV keys.

Test signals: provides performance signals for lock table lookups and range scans, not correctness assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/benches/lock_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/benches/update_max_ts.rs -->
# sources/storage-engines/tikv/components/concurrency_manager/benches/update_max_ts.rs

Purpose: Criterion benchmark for the fast path of `ConcurrencyManager::update_max_ts`.

Important APIs and types: `benchmark_update_max_ts` creates a manager with `ActionOnInvalidMaxTs::Error`, no TSO provider, zero drift allowance, and a pre-set max-ts limit.

Control flow: the benchmark repeatedly calls `cm.update_max_ts(new_ts, || format!("benchmark-{}", new_ts))` with `new_ts` below the configured limit. The source closure is intentionally passed to exercise the generic `IntoErrorSource` path, though on the valid fast path it should not be evaluated into an error source.

State and persistence: updates only in-memory atomics and Prometheus gauges. Repeated calls mostly become no-ops after the first successful max-ts increase because `fetch_max` preserves the current maximum.

Dependencies and integration: depends on Criterion, `txn_types::TimeStamp`, and public concurrency manager APIs.

Risks: benchmark measures a stable, non-error path and does not cover PD double-check latency, expired limits, exact request-origin checks, or panic/error actions.

Test signals: performance signal for max-ts update overhead under normal conditions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/benches/update_max_ts.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/src/key_handle.rs -->
# sources/storage-engines/tikv/components/concurrency_manager/src/key_handle.rs

Purpose: represents a per-key entry in the in-memory lock table and provides the RAII guard that serializes mutation of the lock for that key.

Important APIs and types: `KeyHandle`, `KeyHandleGuard`, `KeyHandle::new`, `KeyHandle::lock`, `with_lock`, unsafe `set_table`, `KeyHandleGuard::key`, and `KeyHandleGuard::with_lock`.

Control flow: `KeyHandle::lock` awaits an async mutex and transmutes its guard to `'static` so it can be stored together with an `Arc<KeyHandle>` in `KeyHandleGuard`. The field order ensures the mutex guard drops before the handle `Arc`. `KeyHandleGuard::drop` clears the stored `Lock`, making memory locks live only while the write path holds the guard. `KeyHandle::drop` removes its key from the parent `LockTable`.

State and persistence: in-memory `lock_store: Mutex<Option<Lock>>`; no disk persistence. `table` is an `UnsafeCell<Option<LockTable>>` set once after insertion so drop can remove the map entry.

Dependencies and integration: used by `LockTable` and exposed by `ConcurrencyManager`. Depends on Tokio async mutex for per-key serialization and parking_lot mutex for lock payload reads/writes.

Risks: relies on unsafe lifetime transmute and field-drop ordering; changing struct layout can break safety. `unsafe impl Sync` depends on disciplined access to `UnsafeCell`. Guard drop always clears locks, so callers must keep guards alive until storage write completion.

Test signals: tests verify mutual exclusion across concurrent tasks and weak-reference cleanup behavior after handles and guards drop.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/src/key_handle.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/src/lib.rs -->
# sources/storage-engines/tikv/components/concurrency_manager/src/lib.rs

Purpose: public API for TiKV transaction concurrency management. It combines an in-memory lock table with monotonic `max_ts` tracking guarded by PD-derived exact/drifted limits.

Important APIs and types: `ConcurrencyManager`, `TSOProvider`, `ActionOnInvalidMaxTs`, `AtomicActionOnInvalidMaxTs`, `InvalidMaxTsUpdate`, `MaxTsUpdateSource`, `IntoErrorSource`, `ValueDisplay`, and re-exported `KeyHandle`, `KeyHandleGuard`, `LockTable`. Prometheus gauges expose `max_ts` and `max_ts_limit`.

Control flow: `update_max_ts` ignores `TimeStamp::max`, selects an exact limit for non-TiDB checked request origins or a drifted limit otherwise, validates the update, optionally double-checks with PD TSO under timeout, reports/panics/errors based on configured action, then atomically raises `max_ts`. `set_max_ts_limit` stores monotonic exact and drifted limits. `lock_key` and `lock_keys` acquire per-key guards, sorting multi-key locks to avoid deadlock. Read checks delegate to the lock table. Global-min methods iterate lock handles.

State and persistence: all state is in-memory: atomics for max-ts and config, `AtomicCell<MaxTsLimit>`, lock table, optional TSO provider, and time provider. No disk persistence.

Dependencies and integration: integrates with PD client, request-origin protobufs, transaction locks/timestamps, failpoints, Prometheus, TiKV logging, and `LockTable`.

Risks: PD double-check is synchronous through `block_on_timeout` and can add latency on invalid paths. Safety depends on lock guards being held while memory locks should be visible. Drifted limits trade availability against false positives; exact checks for non-TiDB origins reduce that tolerance.

Test signals: unit tests cover locking order, max-ts monotonicity, exact-vs-drifted request-origin behavior, limit expiry, PD TSO double-check, panic/error/log actions, and network partition tolerance.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/src/lock_table.rs -->
# sources/storage-engines/tikv/components/concurrency_manager/src/lock_table.rs

Purpose: implements the ordered in-memory table mapping transaction keys to weak references of per-key `KeyHandle`s.

Important APIs and types: `LockTable(pub Arc<SkipMap<Key, Weak<KeyHandle>>>)`, `lock_key`, `check_key`, `check_range`, `get`, `find_first`, `for_each`, `for_each_kv`, and `remove`.

Control flow: `lock_key` creates a candidate handle and pre-locks it, inserts its weak pointer with `get_or_insert`, and either returns the candidate guard if inserted or upgrades and locks the existing handle. If an existing weak pointer cannot be upgraded, it loops until a live handle is found or inserted. Range and full-table scans upgrade weak values before inspecting lock payloads.

State and persistence: stores weak pointers in a concurrent skiplist. Actual lock data lives in `KeyHandle`; stale skiplist entries are removed by `KeyHandle::drop`.

Dependencies and integration: used by `ConcurrencyManager` for lock acquisition and read conflict checks. Depends on the local forked `crossbeam_skiplist::SkipMap`, transaction `Key` ordering, and `KeyHandle`.

Risks: weak-pointer lifecycle is subtle; stale entries can temporarily exist and force retry/skip behavior. Range scans are ordered but not snapshot-isolated across concurrent mutation. `remove` blindly removes by key and relies on correct handle lifetime.

Test signals: tests cover same-key serialization, point/range checks, full iteration, and reacquiring keys after handles drop so that table entries point to live handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/src/lock_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/tests/memory_usage.rs -->
# sources/storage-engines/tikv/components/concurrency_manager/tests/memory_usage.rs

Purpose: ignored, manual stress tests for memory behavior of the concurrency manager lock table and the forked crossbeam skiplist range iterator.

Important APIs and types: `test_memory_usage` and `stress_skipmap_range_iter`.

Control flow: `test_memory_usage` creates a huge number of random short keys across eight threads, inserts locks into a `ConcurrencyManager`, leaks guards to retain them, and prints allocator stats. `stress_skipmap_range_iter` repeatedly inserts, range-iterates, and removes keys in multiple threads while a monitor prints operation count, map length, and jemalloc allocated bytes, then observes idle memory reclamation.

State and persistence: in-memory only. Both tests intentionally retain or churn substantial memory and print diagnostics rather than asserting exact memory budgets.

Dependencies and integration: uses `tikv_alloc::fetch_stats`, `crossbeam_skiplist::SkipMap`, random keys, std threads, transaction locks, and futures `block_on`.

Risks: ignored tests are not CI daily coverage. The first test intentionally leaks guards, so it measures retained lock-table overhead rather than normal lifecycle cleanup. Memory figures depend on jemalloc and release-mode behavior.

Test signals: useful for regression investigation around lock-table amplification and skiplist range iterator leaks; not a deterministic correctness suite.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/concurrency_manager/tests/memory_usage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/Cargo.toml -->
# sources/storage-engines/tikv/components/coprocessor_plugin_api/Cargo.toml

Purpose: manifest for the `coprocessor_plugin_api` crate, which defines the ABI-facing traits and helper macros for custom TiKV coprocessor plugins.

Important APIs and types: package metadata, runtime dependencies `async-trait` and `atomic`, build dependency `rustc_version`.

Control flow: no runtime control flow. Build-time behavior comes from `build.rs`, which injects API version, target triple, and rustc version for plugin compatibility checks.

State and persistence: none directly.

Dependencies and integration: `async-trait` supports async storage trait methods without requiring `Send`; `atomic` stores allocator function pointers. The crate is unpublished and intended for workspace/internal plugin loading.

Risks: ABI compatibility is sensitive to dependency versions and Rust compiler behavior, especially because exported functions return Rust structs and trait-object pointers across dynamic library boundaries. The manifest’s version is used as `API_VERSION`.

Test signals: build script and allocator unit tests are the main direct validation paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/build.rs -->
# sources/storage-engines/tikv/components/coprocessor_plugin_api/build.rs

Purpose: emits compile-time environment variables used by plugin build information.

Important APIs and types: single `main` function that prints `cargo:rustc-env=API_VERSION`, `TARGET`, and `RUSTC_VERSION`.

Control flow: Cargo executes the build script before compiling the crate. It reads `CARGO_PKG_VERSION` through `env!`, reads `TARGET` from the environment, asks `rustc_version::version_meta()` for the short compiler version, and writes the values for use by `BuildInfo::get`.

State and persistence: no repo state. It affects compiler environment for the current build.

Dependencies and integration: integrates with `util::BuildInfo`, plugin loading compatibility checks, Cargo build-script protocol, and the `rustc_version` crate.

Risks: `std::env::var("TARGET").unwrap()` and `version_meta().unwrap()` panic if Cargo/rustc metadata is unavailable, which is acceptable under normal Cargo builds but brittle in unusual build systems.

Test signals: successful crate build validates the script. There are no direct unit tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/allocator.rs -->
# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/allocator.rs

Purpose: defines a plugin-side global allocator that forwards allocation and deallocation to TiKV’s host allocator, allowing owned Rust values to cross the plugin boundary more safely than with separate allocators.

Important APIs and types: `HostAllocatorPtr`, `HostAllocator`, `AllocFn`, `DeallocFn`, `HostAllocator::new`, `HostAllocator::set_allocator`, and the `GlobalAlloc` implementation.

Control flow: the plugin constructor receives `HostAllocatorPtr` from TiKV and calls `HOST_ALLOCATOR.set_allocator`. Later allocations call the stored host `alloc_fn`; deallocations call `dealloc_fn`. Function pointers are stored atomically.

State and persistence: process-local atomic function pointers; no persistence.

Dependencies and integration: used by the `declare_plugin!` macro, which installs `HostAllocator` as the global allocator outside tests. Depends on the `atomic` crate for `Atomic<Option<fn>>`.

Risks: allocation before `set_allocator` panics via `unwrap`; the macro must set the allocator before constructing plugin objects that allocate. Function pointer signatures and Rust `Layout` ABI must match host and plugin. Relaxed loads are used after SeqCst stores, relying on initialization ordering in the constructor path.

Test signals: unit test asserts that `Atomic<Option<AllocFn>>` is lock-free.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/allocator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/errors.rs -->
# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/errors.rs

Purpose: defines error and result types for plugin storage operations and request handling.

Important APIs and types: `PluginResult<T>` and `PluginError` variants `KeyNotInRegion`, `Timeout`, `Canceled`, and `Other(String, Box<dyn Any>)`.

Control flow: no complex flow. `Display` formats user-facing messages; `std::error::Error` is implemented for integration with ordinary Rust error handling.

State and persistence: no state. Errors carry contextual payloads, including region bounds for key-region mismatches and arbitrary boxed data for `Other`.

Dependencies and integration: used by `RawStorage` async methods and `CoprocessorPlugin::on_raw_coprocessor_request`. The `Key` alias comes from storage API re-exports.

Risks: `Other` stores `Box<dyn Any>` without `Send`/`Sync` constraints, which matches the non-`Send` storage trait but can limit cross-thread handling. Plugins are expected to encode business-logic errors into `RawResponse`; this enum is for infrastructure/storage failures.

Test signals: no direct tests; correctness is primarily API contract stability.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/lib.rs -->
# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/lib.rs

Purpose: crate root and user-facing documentation for writing TiKV custom coprocessor plugins.

Important APIs and types: exposes hidden `allocator` and `util` modules for generated macro use, declares private `errors`, `plugin_api`, and `storage_api` modules, and re-exports `PluginError`, `PluginResult`, `CoprocessorPlugin`, raw request/response aliases, `RawStorage`, and storage key/value aliases.

Control flow: no runtime flow. The doc example shows implementing `CoprocessorPlugin` and invoking `declare_plugin!`.

State and persistence: none directly.

Dependencies and integration: establishes the public API consumed by plugin crates compiled as `dylib`. Documentation emphasizes `dylib` rather than `cdylib`/`staticlib` so plugins can use TiKV’s allocator.

Risks: public API stability is ABI-sensitive because plugins are dynamically loaded. Hidden modules are still public for macro expansion, so changing them can break downstream plugin builds. The example in docs must stay aligned with trait signatures.

Test signals: doc example is marked `no_run`; no direct runtime tests here.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/plugin_api.rs -->
# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/plugin_api.rs

Purpose: defines the core trait implemented by a dynamically loaded coprocessor plugin.

Important APIs and types: `RawRequest = Vec<u8>`, `RawResponse = Vec<u8>`, and `CoprocessorPlugin: Send + Sync` with `on_raw_coprocessor_request`.

Control flow: TiKV calls `on_raw_coprocessor_request` with key ranges, raw request bytes, and a `RawStorage` handle. The plugin decodes the request, performs storage operations, and returns encoded response bytes or `PluginError`.

State and persistence: the trait itself stores no state. Plugin implementations may keep state in their struct and can use `Drop` for teardown, as noted in docs.

Dependencies and integration: depends on `storage_api::RawStorage`, `Key`, and `PluginResult`. Dynamic plugin construction is handled by `declare_plugin!` in `util.rs`, which returns a `Box<dyn CoprocessorPlugin>` as a raw trait-object pointer.

Risks: request and response formats are fully plugin-defined, so TiKV cannot validate semantic compatibility. The trait is `Send + Sync`, but storage methods use non-`Send` async_trait, so implementers must be careful about where futures are driven.

Test signals: no direct tests; ABI and trait compatibility are validated through plugin loading/build integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/plugin_api.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/storage_api.rs -->
# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/storage_api.rs

Purpose: defines low-level async storage operations exposed to coprocessor plugins.

Important APIs and types: aliases `Key`, `Value`, `KvPair`, and the `RawStorage` trait with `get`, `batch_get`, `scan`, `put`, `batch_put`, `delete`, `batch_delete`, and `delete_range`.

Control flow: plugin code calls these async methods to access the current node’s raw storage. Range methods use half-open `[start, end)` semantics. Batch methods are recommended for performance.

State and persistence: trait implementers perform real storage reads/writes/deletes; this API file stores no state itself.

Dependencies and integration: uses `async_trait(?Send)` to allow non-`Send` async futures, and `PluginResult` for infrastructure errors. It is consumed by `CoprocessorPlugin::on_raw_coprocessor_request`.

Risks: raw byte keys/values and range boundaries place correctness on plugin authors. Region errors are reported through `PluginError::KeyNotInRegion`, but callers must still choose ranges that match placement constraints. Non-`Send` async methods constrain executor integration.

Test signals: no direct tests in this file; behavior depends on TiKV’s host-side `RawStorage` implementation and plugin integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/storage_api.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/util.rs -->
# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/util.rs

Purpose: defines plugin loader symbol names, ABI signatures, build/plugin metadata structs, the `declare_plugin!` macro, and library-name conversion.

Important APIs and types: symbol constants `_plugin_create`, `_plugin_get_build_info`, `_plugin_get_plugin_info`; signatures `PluginConstructorSignature`, `PluginGetBuildInfoSignature`, `PluginGetPluginInfoSignature`; `BuildInfo`, `PluginInfo`, macro `declare_plugin!`, and `pkgname_to_libname`.

Control flow: `declare_plugin!` optionally derives plugin name/version from Cargo env vars, installs `HostAllocator` as global allocator outside tests, exports build-info and plugin-info functions, and exports `_plugin_create`, which sets the host allocator and returns a raw boxed trait object. `BuildInfo::get` reads env vars emitted by `build.rs`.

State and persistence: global allocator state is initialized during plugin creation. Metadata functions return static string references.

Dependencies and integration: central to dynamic loading by TiKV. Uses allocator internals and `CoprocessorPlugin`; host code must look up the exact exported symbols.

Risks: signatures returning Rust structs/trait objects across `extern "C"` are marked with `allow(improper_ctypes_definitions)` and comments note compatibility constraints. Only one plugin can be declared per library because symbols are fixed. `pkgname_to_libname` encodes platform naming assumptions.

Test signals: no direct tests for macro expansion here; allocator test covers one prerequisite. Plugin load tests would be the main validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/coprocessor_plugin_api/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/Cargo.toml -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/Cargo.toml

Purpose: manifest for TiKV’s vendored/forked `crossbeam-skiplist` component, a concurrent skip list used by the concurrency manager.

Important APIs and types: package metadata, features `std` and `alloc`, dependencies `crossbeam-epoch`, `crossbeam-utils`, and a renamed upstream dependency `crossbeam-skiplist-offical` for CI tracking. Test and example binary names are renamed to satisfy TiKV jemalloc checks.

Control flow: no runtime flow. Feature flags determine whether `std` and `alloc` APIs are available; disabling both is explicitly unsupported.

State and persistence: none directly; the library itself provides in-memory lock-free/concurrent data structures.

Dependencies and integration: `concurrency_manager` depends on this workspace crate for `SkipMap`. The upstream official dependency is present to keep critical bug-fix/security update visibility.

Risks: fork divergence from upstream is a maintenance risk, especially for memory reclamation and range iterator behavior. The dependency name contains a spelling typo (`offical`) that is harmless if consistently used but easy to misread.

Test signals: manifest points to base/map/set tests and simple example. Bench files in this subset compare performance against std maps and base skiplist.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/benches/btree.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/benches/btree.rs

Purpose: baseline benchmark suite using `std::collections::BTreeMap` for ordered-map operations comparable to skiplist workloads.

Important APIs and types: benchmark functions `insert`, `iter`, `rev_iter`, `lookup`, and `insert_remove`; `Map` alias to `BTreeMap`; `test::Bencher` and `black_box`.

Control flow: each benchmark generates deterministic pseudo-random `u64` keys via `wrapping_mul(17).wrapping_add(255)`. Insert and insert/remove benchmarks create a fresh map per iteration; iteration and lookup benchmarks prepopulate once and repeatedly traverse or query.

State and persistence: in-memory benchmark data only.

Dependencies and integration: uses Rust nightly `test` benchmark harness. Provides ordered-map baseline for the forked skiplist benches.

Risks: deterministic key generation can produce distribution-specific results. This baseline is single-threaded and does not model concurrent skiplist advantages. It uses the unstable `test` feature.

Test signals: performance baseline for ordered iteration, reverse iteration, lookup, insertion, and removal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/benches/btree.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/benches/hash.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/benches/hash.rs

Purpose: baseline benchmark suite using `std::collections::HashMap` for unordered map operations comparable to skiplist insertion and lookup workloads.

Important APIs and types: benchmark functions `insert`, `iter`, `lookup`, and `insert_remove`; `Map` alias to `HashMap`; `test::Bencher` and `black_box`.

Control flow: benchmarks use the same deterministic pseudo-random `u64` sequence as the BTreeMap and skiplist benches. Insert and insert/remove create fresh maps; iter and lookup use a prepopulated map.

State and persistence: in-memory benchmark data only.

Dependencies and integration: nightly `test` benchmark harness. Serves as an unordered baseline; it lacks `rev_iter` because `HashMap` has no ordered reverse traversal.

Risks: `HashMap` iteration ordering is intentionally unspecified, so iteration results are not comparable to ordered traversal semantics. The workload is single-threaded and does not represent concurrent use.

Test signals: performance baseline for hash-table insert, iterate, lookup, and remove operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/benches/hash.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/benches/skiplist.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/benches/skiplist.rs

Purpose: benchmark suite for the low-level `SkipList` API using Crossbeam epoch guards.

Important APIs and types: benchmark functions `insert`, `iter`, `rev_iter`, `lookup`, and `insert_remove`; `SkipList`, `crossbeam_epoch::pin`, `epoch::default_collector`, and entry `release`.

Control flow: each operation uses the same deterministic `u64` sequence as baseline benches. Insert creates a new skiplist per iteration and inserts under a pinned guard. Iteration and lookup prepopulate a list and release insertion entries. Remove benchmarks remove and release entries within each iteration.

State and persistence: in-memory skiplist nodes reclaimed by Crossbeam epoch mechanisms; no persistence.

Dependencies and integration: exercises the base skiplist API directly rather than the higher-level `SkipMap`. It is useful for comparing raw skiplist costs to standard maps and for noticing regressions in epoch-protected traversal/removal.

Risks: pinned guards held for a full benchmark can affect reclamation timing and may not mirror production guard scopes. Single-threaded benchmarks do not capture concurrent contention behavior. Uses unstable `test` harness.

Test signals: raw performance signal for insert, forward/reverse iteration, lookup, and insert/remove cycles in the forked skiplist.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/benches/skiplist.rs -->
