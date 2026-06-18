# Research: subset-b-008948

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/backup/mod.rs -->
## sources/storage-engines/tikv/tests/integrations/backup/mod.rs

Purpose: integration coverage for TiKV backup pushdown, local external storage output, SST import restoration, raw KV API-version conversion, raw backup metadata, failure paths, commit timestamp safety, and backup during flashback.

Important APIs and helpers: `TestSuite`, `backup`, `backup_raw`, `storage_raw_checksum`, `make_local_backend`, `create_storage`, `SstImporter::create`, raft `IngestSst` commands, `SstMeta`, `calc_crc32_bytes`, `checksum_crc64_xor`, and `assert_same_files`. `assert_same_files` normalizes timestamp-bearing file names, random cipher IVs, and RocksDB session-dependent SHA fields before comparing backup output.

Control flow: tests create multi-node suites, write MVCC or raw KV data, run backup streams with `block_on(rx.collect())`, delete or restore data through direct CF deletion and importer ingestion, then run a second backup to compare logical file metadata. Raw KV tests back up from V1/V1ttl/V2 to target API versions and verify restored reads plus metadata counts/checksums. Error and edge tests cover read-only storage, async-commit/1PC min commit timestamps after backup, and backup while a region is in prepared flashback state.

State and persistence: the tests persist generated SSTs into temporary local storage, copy them into each simulated store importer, and ingest via raft command so restored RocksDB state is observable through subsequent backup or raw get calls. They also mutate cluster CF contents directly and use flashback admin commands.

Dependencies and integration points: `test_backup`, `kvproto`, `external_storage`, `engine_traits`, raft command protobufs, transaction timestamps, and TiKV coprocessor checksum. Risks include nondeterministic file metadata, file permissions skipped in docker-root runs, and API-version key encoding differences. Test signals are end-to-end backup/import equality, raw checksum parity, expected storage error responses, and absence of flashback backup errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/backup/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/gc_worker.rs -->
## sources/storage-engines/tikv/tests/integrations/config/dynamic/gc_worker.rs

Purpose: verifies validation and online updates for `GcConfig` and the GC worker IO limiter.

Important APIs: `GcConfig::validate`, `GcWorker::new/start`, `GcTask::Validate`, `ConfigController`, `Module::Gc`, `GcWorkerConfigManager`, `Scheduler<GcTask<_>>`, and `Limiter`.

Control flow: `setup_cfg_controller` builds a test Rocks engine, starts a `GcWorker` with a mock region provider, registers its config manager, and returns the scheduler plus controller. `validate` sends a `GcTask::Validate` closure to inspect worker-local config and limiter state. Tests reject `batch_keys = 0`, prove unrelated raftstore updates do not alter GC config, then update ratio, batch keys, write limit, and compaction filter. Separate tests change `gc.max-write-bytes-per-sec` through `ConfigController` and directly through the worker config manager.

State and persistence: state is in worker memory and the limiter. No durable config file is written. The IO limit transitions between infinity and finite byte-per-second speeds.

Dependencies and integration points: TiKV server GC worker, online config controller, test engine builder, raftstore mock region info, and `tikv_util::time::Limiter`. Risks include async scheduling timeouts and float equality for limiter speed. Test signals are closure assertions run inside the GC worker within three seconds.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/gc_worker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/mod.rs -->
## sources/storage-engines/tikv/tests/integrations/config/dynamic/mod.rs

Purpose: module aggregator for dynamic online-config integration tests.

Important APIs/types/functions: no functions are defined; it declares child modules `gc_worker`, `pessimistic_txn`, `raftstore`, `snap`, and `split_check`.

Control flow: Rust test discovery compiles and runs the child modules through this integration module. State and persistence are delegated to children.

Dependencies and integration points: the file wires the dynamic config suite into `tests/integrations/config/mod.rs`. The risk is simple omission: a child module removed here silently drops its tests from the integration target. Test signal is successful compilation and execution of all listed child modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/pessimistic_txn.rs -->
## sources/storage-engines/tikv/tests/integrations/config/dynamic/pessimistic_txn.rs

Purpose: validates online config behavior for the pessimistic transaction lock manager.

Important APIs: `server::lock_manager::Config`, `LockManager`, `WaiterMgrScheduler`, `DetectorScheduler`, `LockManager::config_manager`, storage dynamic config atomics, `ConfigController`, and `Module::PessimisticTxn`.

Control flow: `setup` creates and starts a `LockManager` with `TestPdClient`, mock store address resolver, and `SecurityManager`, captures waiter/deadlock schedulers, then registers the lock manager config manager. Validation helpers send scheduler closures and wait on channels. The main test sets known defaults, confirms unrelated raftstore updates are ignored, changes wait-for-lock timeout and observes both waiter timeout and deadlock TTL, then toggles pipelined/in-memory locking, wake-up delay, and in-memory size limits through atomic dynamic configs.

State and persistence: all state is runtime lock-manager state, stored in schedulers and atomic fields. No file persistence occurs; the manager is stopped at the end.

Dependencies and integration points: security setup, PD test client, lock manager wait/deadlock workers, storage dynamic config consumers. Risks include async worker start/validation races and needing exact default constants. Test signals are timeout/TTL equality and atomic values after each `update_config`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/pessimistic_txn.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/raftstore.rs -->
## sources/storage-engines/tikv/tests/integrations/config/dynamic/raftstore.rs

Purpose: exercises raftstore online configuration dispatch into a live raft batch system, including validation boundaries and async IO resizing constraints.

Important APIs: `create_raft_batch_system`, `RaftstoreConfigManager`, `VersionTrack<Config>`, `StoreMsg::Validate`, `RaftRouter`, `ApplyRouter`, `ConfigController`, `Module::Raftstore`, `Engines<RocksEngine, RocksEngine>`, `SnapManager`, `SstImporter`, and `MockTransport`.

Control flow: `start_raftstore` creates temporary Rocks engines, importer, snap manager, store meta, PD worker, split scheduler, and starts the raft batch system. The config manager uses the system refresh scheduler and shared `VersionTrack`. `validate_store` sends a control message through the raft router to inspect live store config. Tests update batch sizes, raft log GC threshold, message size, entry size, yield write size, and snap wait duration; then they try invalid minimum/maximum values and assert live config remains unchanged. IO tests reject switching between sync and async store IO modes while allowing resizing within async mode.

State and persistence: temporary RocksDB directories, raftstore worker threads, and shared `VersionTrack` hold state. Shutdown is explicit per scenario.

Dependencies and integration points: raftstore FSM, PD client, importer, snap manager, health/resource metering/service manager dummies. Risks include broad fixture construction, `MockTransport` panicking if unexpected sends occur, and validation sensitivity to raftstore constraints. Test signals are successful control-message config equality and expected update errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/raftstore.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/snap.rs -->
## sources/storage-engines/tikv/tests/integrations/config/dynamic/snap.rs

Purpose: verifies dynamic server config updates relevant to snapshot handling.

Important APIs: `ServerConfigManager`, `SnapHandler`, `SnapTask::Validate`, `SnapManager`, `RaftRouterWrap`, `VersionTrack<ServerConfig>`, `ConfigController`, `Module::Server`, and gRPC `ResourceQuota`.

Control flow: `start_server` builds a snap manager, security manager, gRPC environment, raft batch router, lazy snap worker, and server config track. It registers `ServerConfigManager`, starts the snap handler, and returns controller/worker/manager. The test updates `server.snap-io-max-bytes-per-sec` and `server.concurrent-send-snap-limit`, checks the snap manager speed limit, and validates worker config through a scheduled `SnapTask::Validate`.

State and persistence: snapshot state is temporary path backed and runtime config is stored in `VersionTrack`; no durable config file is edited.

Dependencies and integration points: raftstore snap manager, server snap worker, grpcio environment, security manager. Risks include thread scheduling timeouts and the dummy secondary config manager swallowing dispatch. Test signal is exact updated `ServerConfig` plus `SnapManager` byte limit.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/snap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/split_check.rs -->
## sources/storage-engines/tikv/tests/integrations/config/dynamic/split_check.rs

Purpose: tests online coprocessor split-check config propagation.

Important APIs: `SplitCheckRunner`, `SplitCheckTask::Validate`, `SplitCheckConfigManager`, `CoprocessorHost`, `ConfigController`, `Module::Coprocessor`, and Rocks engine creation with `CF_DEFAULT` plus `split-check-config`.

Control flow: a temporary Rocks engine is created from `cfg.storage.data_dir`; `setup` starts a lazy split-check worker with a runner and registers its config manager. The test first sends an unrelated raftstore update and validates original coprocessor config, then updates `split_region_on_table`, `batch_split_limit`, and `region_split_keys`, validating the worker sees the constructed expected config.

State and persistence: runtime worker state and a temporary RocksDB are used; no config file persistence is involved. The worker is stopped.

Dependencies and integration points: raftstore coprocessor split logic, worker scheduler, online config. Risks include one-second validation timeout and CF naming assumptions. Test signal is equality of the live split-check config after updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/dynamic/split_check.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/graceful_shutdown_config.rs -->
## sources/storage-engines/tikv/tests/integrations/config/graceful_shutdown_config.rs

Purpose: regression coverage for the server graceful shutdown timeout config.

Important APIs: `TikvConfig::default`, `server.graceful_shutdown_timeout`, `ReadableDuration::secs`, and `toml::Value::try_from`.

Control flow: one test asserts the default timeout is 20 seconds. Another mutates it to 25 seconds, serializes only the server config to TOML, and asserts the serialized table contains `graceful-shutdown-timeout`.

State and persistence: purely in-memory config serialization, no file IO.

Dependencies and integration points: TiKV config serde and TOML field naming. Risks are field rename or serde skip behavior. Test signal is default duration equality and presence of the TOML key.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/graceful_shutdown_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/mod.rs -->
## sources/storage-engines/tikv/tests/integrations/config/mod.rs

Purpose: top-level TiKV config integration suite covering TOML round trips, custom fixture deserialization, default/legacy compatibility, renamed keys, readpool behavior, and raft-engine compression threshold adjustment.

Important APIs: `TikvConfig`, `read_file_in_project_dir`, many config structs (`ServerConfig`, `RaftstoreConfig`, `DbConfig`, CF configs, `StorageConfig`, `GcConfig`, `PessimisticTxnConfig`, `CdcConfig`, `ResourceControlConfig`, etc.), `toml::{to_string_pretty, from_str}`, `compatible_adjust`, `logger_compatible_adjust`, and `validate`.

Control flow: `test_toml_serde` round-trips defaults. `test_serde_custom_tikv_config` constructs a large expected `TikvConfig`, reads `integrations/config/test-custom.toml`, optimizes split settings, compares with debug equality, and round-trips the loaded config. Later tests assert empty and section-only default TOML equals defaults, partial readpool sections preserve defaults, legacy readpool settings disable unified pool, old per-CF block-cache sizes are combined into shared cache capacity, old root log keys migrate into `[log]`, renamed server/storage keys deserialize equivalently, and raft-engine compression threshold is adjusted only when async raftstore IO is enabled and the threshold was default.

State and persistence: reads TOML fixtures from project root; otherwise in-memory serde/validation. No writes.

Dependencies and integration points: broad TiKV config schema, RocksDB/Titan/raft-engine enums, encryption/security, backup/log-backup/import/gc/cdc/resolved-ts/split/resource-control modules. Risks are high schema churn, deprecated compatibility paths, fixture drift, and equality failures from default changes. Test signals are exhaustive equality checks and explicit compatibility assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/test-cache-compatible.toml -->
## sources/storage-engines/tikv/tests/integrations/config/test-cache-compatible.toml

Purpose: fixture for backward-compatible block cache migration from legacy per-CF cache fields to shared `storage.block-cache.capacity`.

Important fields: empty standard config tables plus `rocksdb.defaultcf.block-cache-size = "1GB"`, `rocksdb.writecf.block-cache-size = "1GB"`, `rocksdb.lockcf.block-cache-size = "128MB"`, and `raftdb.defaultcf.block-cache-size = "128MB"`.

Control flow and state: consumed by `test_block_cache_backward_compatible`, which deserializes it, observes no shared capacity before compatibility adjustment, then calls `compatible_adjust(None)` and checks the shared capacity equals the sum of the four legacy cache sizes.

Dependencies and integration points: TiKV config serde and compatibility adjustment. Risk is legacy fields being removed or no longer participating in capacity synthesis. Test signal is exact summed capacity.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/test-cache-compatible.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/test-custom.toml -->
## sources/storage-engines/tikv/tests/integrations/config/test-custom.toml

Purpose: comprehensive non-default TiKV config fixture used to prove schema coverage, aliases, enum parsing, nested tables, readable units, and backward compatibility.

Important sections: root slow-log/panic/memory flags; `[log]`, `[log.file]`, readpools; `[server]` and labels; `[storage]`, max-ts, block-cache, flow-control, IO priorities; `[pd]`, `[metric]`; extensive `[raftstore]`; `[coprocessor]`; RocksDB/Titan DB and CF configs; raftdb and raft-engine; security/encryption; backup, log-backup, import, gc/auto-compaction, pessimistic-txn, cdc, resolved-ts, split, and resource-control.

Control flow and state: `test_serde_custom_tikv_config` builds the matching `TikvConfig`, loads this file, applies split optimization, and requires debug equality. It also serializes the loaded value and deserializes it again.

Dependencies and integration points: nearly every TiKV config module and several legacy names, including `pessimistic-txn.enabled`, numeric `wake-up-delay-duration`, `partitioned-raft-kv`, and nested `split.split-*` keys. Risks include fixture drift after config default changes, renamed fields, and unit parsing differences. Test signal is full-object equality plus round-trip stability.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/test-custom.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/test-default.toml -->
## sources/storage-engines/tikv/tests/integrations/config/test-default.toml

Purpose: section-only default fixture ensuring an explicit but empty TOML layout deserializes exactly to `TikvConfig::default()`.

Important sections: empty `[log]`, `[log.file]`, `[memory]`, readpool sections, `[server]`, `[storage]`, `[storage.block-cache]`, `[pd]`, `[metric]`, `[raftstore]`, `[coprocessor]`, RocksDB/Titan/CF tables, `[raftdb]`, `[raftdb.defaultcf]`, `[raft-engine]`, `[security]`, `[import]`, and `[gc]`.

Control flow and state: `test_serde_default_config` compares both empty string TOML and this fixture to defaults. It has no runtime state or persistence beyond fixture reading.

Dependencies and integration points: serde default handling for optional nested config tables. Risk is adding a required table or changing table defaults without updating default construction. Test signal is exact `TikvConfig` equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/test-default.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/test-log-compatible.toml -->
## sources/storage-engines/tikv/tests/integrations/config/test-log-compatible.toml

Purpose: legacy root-level log config compatibility fixture.

Important fields: root `log-level = "critical"`, `log-file = "foo"`, `log-format = "json"`, and `log-rotation-size = "1024MB"`, followed by otherwise empty standard sections.

Control flow and state: `test_log_backward_compatible` deserializes the fixture and first observes modern `[log]` defaults, then calls `logger_compatible_adjust()` and asserts the legacy root fields migrate into `cfg.log.level`, `cfg.log.file.filename`, `cfg.log.format`, and `cfg.log.file.max_size`.

Dependencies and integration points: logger compatibility layer and TOML serde aliases. Risks include removal of old root fields or wrong precedence when both old and new fields exist. Test signal is pre-adjustment defaults and post-adjustment legacy values.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/test-log-compatible.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/test_config_client.rs -->
## sources/storage-engines/tikv/tests/integrations/config/test_config_client.rs

Purpose: tests online config controller update parsing, validation, dispatch to module managers, config-file rewriting, and reload from TOML file.

Important APIs: `ConfigController`, `OnlineConfig`, `ConfigManager`, `ConfigChange`, `Module::Raftstore`, `RaftstoreConfig::update`, `update`, `update_config`, `get_current`, `update_from_toml_file`, and helper `change`.

Control flow: `test_update_config` applies valid changes to schedules, raftstore threshold, and max-ts drift, then verifies validation failures, unsupported fields, unknown paths, type errors, and short names leave current config unchanged. `test_dispatch_change` registers a mock raftstore manager and checks both global current config and manager-local config update. `test_write_update_to_file` creates a TOML file with comments, commented keys, similarly named nested keys, and nested Titan config, then updates several fields and compares exact rewritten bytes. `test_update_from_toml_file` writes a raftstore config file and reloads it into the controller and registered manager.

State and persistence: temporary config files are created, rewritten, synced, and read back; mock managers store state in `Arc<Mutex<_>>`.

Dependencies and integration points: online config, TOML editor behavior, raftstore config validation, file IO. Risks include exact formatting sensitivity and validation order. Test signals are exact config equality, dispatched manager state, precise rewritten file content, and reload behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/config/test_config_client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/coprocessor/mod.rs -->
## sources/storage-engines/tikv/tests/integrations/coprocessor/mod.rs

Purpose: module aggregator for coprocessor integration tests.

Important APIs/types/functions: declares `test_analyze`, `test_checksum`, and `test_select`; no runtime code.

Control flow/state: Rust test discovery runs the child modules through this file. Persistence and state are in child test fixtures.

Dependencies and integration points: parent integration test crate and `test_coprocessor` helpers used by children. Risk is accidentally dropping a module declaration and losing test coverage. Test signal is compilation and execution of the listed child modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/coprocessor/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/coprocessor/test_analyze.rs -->
## sources/storage-engines/tikv/tests/integrations/coprocessor/test_analyze.rs

Purpose: integration tests for TiKV coprocessor analyze requests over table and index data, including lock behavior and full sampling modes.

Important APIs: coprocessor `Request`, `KeyRange`, `Context`, `IsolationLevel`, tipb `AnalyzeReq`, `AnalyzeColumnsReq`, `AnalyzeIndexReq`, `AnalyzeColumnsResp`, `AnalyzeIndexResp`, `AnalyzeColumnGroup`, `AnalyzeType`, and helpers `new_analyze_*`.

Control flow: request builders encode analyze protobufs, set ranges from `ProductTable`, and assign `REQ_TYPE_ANALYZE`. Tests initialize product data, issue analyze column/index requests, deserialize responses, and assert histogram bucket counts, NDV, null counts, CM sketch rows, total sizes, TopN counts, sampling row collectors, and invalid-range errors. Lock tests run under SI and RC: SI returns lock info with empty data, while RC bypasses locks and returns empty statistics.

State and persistence: test data is committed or left locked in test storage through `init_data_with_commit`; responses are in-memory protobufs. No external files are written.

Dependencies and integration points: TiDB protobuf stats formats, MVCC isolation semantics, test table metadata, and coprocessor endpoint request handling. Risks include statistical algorithm changes, nondeterministic sampling if not controlled by fixture size, and lock behavior differences. Test signals are exact stats-field assertions and error/lock presence.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/coprocessor/test_analyze.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/coprocessor/test_checksum.rs -->
## sources/storage-engines/tikv/tests/integrations/coprocessor/test_checksum.rs

Purpose: verifies coprocessor checksum results for table and index scans.

Important APIs: `ChecksumRequest`, `ChecksumResponse`, `ChecksumAlgorithm::Crc64Xor`, `ChecksumScanOn`, `REQ_TYPE_CHECKSUM`, `SnapshotStore`, `TikvStorage`, `RangesScanner`, and helper `reversed_checksum_crc64_xor`.

Control flow: `new_checksum_request` builds SI checksum requests at `u64::MAX`. The test inserts product rows, loops over primary/table and secondary index columns, selects the matching range and scan mode, computes an expected checksum by scanning backward with `RangesScanner`, then handles the coprocessor request and compares checksum plus total KV count.

State and persistence: data lives in the in-memory/test engine; expected checksum reads a snapshot at max timestamp. No file persistence.

Dependencies and integration points: TiDB checksum protobufs, API V1 keyspace decoding, DAG storage scanner, MVCC snapshot store. Risks include scan direction, key encoding, and checksum algorithm drift. Test signal is exact checksum equality and total KV count equal to fixture row count.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/coprocessor/test_checksum.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/coprocessor/test_select.rs -->
## sources/storage-engines/tikv/tests/integrations/coprocessor/test_select.rs

Purpose: broad integration suite for DAG select coprocessor behavior: table/index scans, streaming, aggregation, ordering, limits, expressions, locks, cache hints, scan details, batch requests, index lookup, commit-ts column output, and API V2 row checksums.

Important APIs and helpers: `DagSelect`, `DagChunkSpliter`, `handle_select`, `handle_request`, `handle_streaming_select`, `ProductTable`, `ColumnBuilder`, `TableBuilder`, `SelectResponse`, `Chunk`, `Expr`, `ExprDefBuilder`, `ScalarFuncSig`, `Context`, `IsolationLevel`, `StoreBatchTask`, `StoreBatchTaskResponse`, `Lock`, TLS engine helpers, and constants `FLAG_IGNORE_TRUNCATE`/`FLAG_TRUNCATE_AS_WARNING`.

Control flow: tests initialize product table rows through helper stores/endpoints, build DAG requests with projections, filters, grouping, aggregate functions, order/limit, index scans, batch tasks, or custom contexts, then decode response chunks and compare encoded datum rows. Early tests validate chunk sizing, streaming ranges, leader-lease reads, failed read futures, scan/time details, table/index group-by and aggregates, delete visibility, filters, truncate errors/warnings, default column values, output offsets, locks, output counts, snapshot errors, coprocessor cache hits, RC reads, bucket version refresh, V2 checksum row formats, multi-region batch task result/error partitioning, nonzero process wall time, local index lookup with intermediate outputs, and `_tidb_commit_ts` placement.

State and persistence: data is committed, deleted, locked, or split across simulated raft regions; some tests mutate lock CF, region buckets, and TLS Rocks engine region info. No durable files are written.

Dependencies and integration points: coprocessor DAG executor, storage MVCC, raftstore region metadata, TiDB expression/protobuf encoding, cache/version semantics, scan statistics, and API V2 row format. Risks include many exact datum expectations, async raft timing, regional split assumptions, cache version assumptions, and lock conflict semantics. Test signals are exact row encodings, error fields, exec details, cache hit flags, lock info, and batch response classifications.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/coprocessor/test_select.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/import/mod.rs -->
## sources/storage-engines/tikv/tests/integrations/import/mod.rs

Purpose: module aggregator for import integration tests.

Important APIs/types/functions: declares `test_apply_log`, `test_sst_service`, and `util`; no functions are implemented here.

Control flow/state: Rust test discovery reaches import apply-log tests and SST service tests through this module. State and persistence are owned by child modules and shared utility helpers.

Dependencies and integration points: parent integration crate, import service tests, and utility module. Risk is module omission removing import coverage. Test signal is compilation and execution of the child modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/import/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/import/test_apply_log.rs -->
## sources/storage-engines/tikv/tests/integrations/import/test_apply_log.rs

Purpose: tests the import service `apply` path for plain log/SST-like files, rewrite rules, resource guards, write-CF transaction source tagging, and repeated application.

Important APIs: `ApplyRequest`, `LocalStorage`, `make_plain_file`, `register_range_for`, `rewrite_for`, `local_storage`, `check_applied_kvs_cf`, `new_cluster_and_tikv_import_client`, `disk::set_disk_status`, failpoints `mock_memory_usage`/`mock_memory_limit`, `Write`/`WriteRef`, and CF constants `CF_DEFAULT`/`CF_WRITE`.

Control flow: `test_basic_apply` creates a local file with four KVs, registers a subrange, applies a rewrite from `k` to `r`, and expects only in-range rewritten default-CF KVs. `test_apply_write_cf_sets_txn_source` writes a serialized MVCC `Write` into write CF, applies it, reads the rewritten key from engine, and checks the Lightning physical import bit is ORed into `txn_source`. `test_apply_full_resource` simulates almost-full disk and high memory via failpoints, expecting error responses. `test_apply_twice` applies the same file twice under different rewrite rules and verifies both rewritten outputs coexist.

State and persistence: temporary local storage files are read by import apply; data is persisted to the cluster engine and inspected through client helpers or direct engine reads. Global disk status and failpoints are reset.

Dependencies and integration points: import service, external/local storage, disk/memory guards, MVCC write encoding, CDC transaction source semantics. Risks include global failpoint cleanup, disk status leakage, and exact error text. Test signals are applied KV equality, txn source bit, and resource error messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/import/test_apply_log.rs -->
