# subset-b-008864 Research

Grouped research report for the TiKV SST importer, backup test helpers, coprocessor test fixtures, PD mock server/client crates, and raftstore-v2 test crate manifest. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/sst_writer.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/sst_writer.rs

## Purpose
This file implements SST writers used by the local SST importer to materialize incoming import batches into RocksDB SST files. It has two paths: `TxnSstWriter` for transactional KV import and `RawSstWriter` for raw KV import. The code sits between protobuf import requests (`WriteBatch`, `RawWriteBatch`, `Pair`) and the engine abstraction (`KvEngine::SstWriter`), adding TiKV key encoding, API-version checks, MVCC write records, TTL encoding, file finalization, encryption metadata handoff, and import metrics.

## Important APIs, Types, And Functions
`SstWriterType` distinguishes transactional and raw writers for diagnostics. `TxnSstWriter<E>` owns separate default-CF and write-CF SST writers plus entry/byte counters, output `ImportPath`s, `SstMeta`s, optional `DataKeyManager`, selected `ApiVersion`, and `txn_source`. `TxnSstWriter::write` validates nonzero commit timestamps, checks key mode by API version, appends commit timestamps to raw keys, and delegates to `put`. `TxnSstWriter::put` writes large values to default CF and always writes a serialized `txn_types::Write` record to write CF. `finish` closes non-empty writers, saves output files through `ImportPath::save`, and returns the matching metas.

`RawSstWriter<E>` writes raw key/value pairs only to default CF. `RawSstWriter::write` uses `match_template_api_version!` to encode raw keys and values, applies TTL only for API versions where TTL is enabled, and emits deletes via SST delete records. `RawSstWriter::finish` only emits metadata when `default_entries > 0`, although delete counts are tracked separately.

## Control Flow And State
Both writers are stateful accumulators. Each batch mutates counters and the underlying SST writer, then `finish` consumes the writer. Transactional import rejects zero commit TS before writing anything; per-pair operations use `PairOp::Put` and `PairOp::Delete`. Short transactional values are embedded into write CF records, while long values are persisted in default CF and referenced from write CF. Raw import derives an optional expire timestamp from the batch TTL and API support, then encodes `RawValue` before writing.

## Persistence And Integration Points
Persistence happens through engine-trait SST writer calls and `ImportPath::save`, which is where encrypted-file bookkeeping can be applied through `DataKeyManager`. Keys are wrapped with `keys::data_key`, so the produced SST contents are in TiKV's internal data-key namespace. The module integrates with `api_version`, `txn_types`, `engine_traits`, `kvproto::import_sstpb`, importer metrics, and importer construction methods such as `SstImporter::new_txn_writer` and `new_raw_writer`.

## Risks And Test Signals
Key-mode validation is critical for API V2: transactional import accepts Txn/TiDB key modes, raw import accepts Raw mode only. Raw TTL handling must reject TTL for API V1 without TTL support. `RawSstWriter::finish` ignores delete-only batches because it checks only `default_entries`; callers relying on delete-only raw SSTs should be aware of that behavior. Tests cover txn source propagation, short/large/delete txn writes, zero commit TS rejection, raw TTL encoding for V1ttl and V2, TTL-disabled errors, V1 raw writes, invalid V2 raw key mode, and valid/invalid V2 txn keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/sst_writer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/util.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/util.rs

## Purpose
This utility file provides filesystem preparation helpers used before SST ingestion and a small external-storage URL helper. The ingestion helpers make retryable ingestion safe when RocksDB may move, mutate, or delete the input SST during external file ingestion.

## Important APIs, Types, And Functions
`prepare_sst_for_ingestion(path, clone, encryption_key_manager)` removes any stale clone and encryption metadata, then either hard-links or copies the source SST to a clone path. On Unix it reads the source link count: if there is only one link, RocksDB should not already own the file and a hard link is safe; otherwise it copies to avoid modifying an SST that may already have been ingested. It syncs the clone file and parent directory, then links encryption metadata from original to clone when a `DataKeyManager` is present.

`copy_sst_for_ingestion` is a stricter variant that always copies, removes read-only permission from the clone if necessary, syncs the parent directory, and updates encryption metadata. `url_for` converts `ExternalStorage::url()` to a string and makes URL lookup errors printable as `ErrUrl(...)`.

## Control Flow And State
The helpers are idempotent over an existing clone path: they remove both filesystem file and key-manager entry before recreating the clone. The branch in `prepare_sst_for_ingestion` is driven by filesystem metadata and is only link-count aware on Unix. `copy_sst_for_ingestion` has no hard-link branch and always produces a separately writable file.

## Persistence And Integration Points
This code is explicitly about durable filesystem state. It uses `file_system::{remove_file, hard_link, copy_and_sync, metadata, set_permissions}` and `File::sync_all` to make both clone file contents and containing-directory metadata durable. It integrates with encryption metadata by deleting stale clone keys and then calling `DataKeyManager::link_file`.

## Risks And Test Signals
The functions call `to_str().unwrap()` and assume ordinary UTF-8 filesystem paths. Parent directory lookup is also unwrapped. Incorrect link-count assumptions can corrupt ingested SSTs because RocksDB may mutate global sequence numbers, which is why multi-link files are copied. Tests exercise hard-link first ingestion, copy after ingestion, repeated preparation, Titan SSTs, plaintext and encrypted key-manager scenarios, and the always-copy helper.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_backup/Cargo.toml -->
# sources/storage-engines/tikv/components/test_backup/Cargo.toml

## Purpose
This manifest defines the private `test_backup` crate. It is not published and exists as shared test support for TiKV backup behavior, including cluster-backed backup endpoints, raw/txn backup validation, disk snapshot backup tests, and checksum comparisons.

## Dependencies And Integration Points
The crate depends on internal workspace crates for backup execution (`backup`), raftstore test clusters (`test_raftstore`, `raftstore`), TiKV storage and coprocessor paths (`tikv`), Rocks engine traits (`engine_rocks`, `engine_traits`), API-version encoding, external local storage, and utility workers. It also uses `kvproto` and `grpcio` to call TiKV RPCs, `tidb_query_common` to scan data, `txn_types` for timestamps, `futures` channels/executors, and `crc64fast`/`rand` for checksum and temporary directory support.

## State, Persistence, And Risks
The manifest enables real integration tests rather than lightweight unit fixtures. It pulls in RocksDB-backed engines, local external storage, gRPC clients, worker threads, and raftstore clusters, so tests using this crate are stateful and timing-sensitive. The source tree has no feature flags here, meaning dependency feature selection is inherited from workspace defaults. A small formatting issue (`external_storage ={ workspace = true }`) is syntactically valid TOML but inconsistent with surrounding style.

## Test Signals
Because this is a support crate manifest, validation is compile-time and integration-test oriented: successful builds prove that backup test helpers can link against backup, raftstore, TiKV, and protobuf APIs together.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_backup/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_backup/src/disk_snap.rs -->
# sources/storage-engines/tikv/components/test_backup/src/disk_snap.rs

## Purpose
This file provides a test harness for snapshot-backup preparation over raftstore disk snapshots. It starts per-store backup gRPC services, registers a `PrepareDiskSnapObserver` with raftstore coprocessor hosts, and wraps the streaming `PrepareSnapshotBackup` protocol in ergonomic test utilities.

## Important APIs, Types, And Functions
`Node` stores an optional gRPC `Server`, the shared `PrepareDiskSnapObserver` rejector, and a backup client. `Suite` owns a `test_raftstore` server cluster, node map, and shared gRPC environment. `Suite::new_with_cfg` builds a cluster, registers observers before `cluster.run`, then starts backup services for each store. `start_backup` constructs a `backup::Service` with a disk-snapshot environment around the store router and rejector. `try_split` and `split` drive raftstore region splits for tests.

`PrepareBackup` wraps a duplex streaming sink/receiver pair. `prepare` sends `UpdateLease`, `wait_apply` sends a `WaitApply` request and waits until every requested region emits `WaitApplyDone`, `send_wait_apply` separates send from receive, `send_finalize` sends `Finish` and returns whether the last lease was valid, and `next`/`try_next` expose response polling. Assertion helpers validate raft command success or expected failures.

## Control Flow And State
The harness mutates cluster topology and streaming backup state. `prepare_backup` opens a stream to one node's backup service; calls then send typed protocol requests and synchronously block on futures. `wait_apply` tracks a `HashSet` of region IDs and removes each successful completion. `send_finalize` tolerates already-finished RPCs and uses a two-second timeout while draining responses.

## Persistence And Integration Points
Integration points include `backup::disk_snap::Env`, raftstore routers, `PrepareDiskSnapObserver`, gRPC backup service/client generation from `brpb`, and `test_raftstore` cluster control. Persistence is indirect through raftstore disk snapshot and region state rather than local files in this module.

## Risks And Test Signals
This harness is intentionally timing-sensitive: waits use blocking futures and fixed timeout behavior. `crate_node` appears misspelled but is internal. Stream finalization assumes an `UpdateLeaseResult` event appears before timeout. The assertion helpers are track-caller annotated and are the main test signals for success, generic failure, or failure message contents.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_backup/src/disk_snap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_backup/src/lib.rs -->
# sources/storage-engines/tikv/components/test_backup/src/lib.rs

## Purpose
This file exports the primary backup test harness for TiKV. `TestSuite` creates a multi-node server cluster, starts backup endpoints for each node, exposes convenience write/read APIs, schedules backup tasks, and computes reference checksums for both transactional and raw KV data.

## Important APIs, Types, And Functions
`TestSuite` contains the server cluster, one lazy backup worker per store, a TiKV gRPC client bound to the region leader, an RPC `Context`, timestamp state, a shared background worker, and the active `ApiVersion`. `new` builds a server cluster with the requested API version, configures lease-read timing, starts backup endpoints using `backup::Endpoint::new`, writes a bootstrap key, discovers leader context, and creates a `TikvClient`.

Mutation helpers include `alloc_ts`, `must_raw_put`, `must_raw_get`, `must_kv_prewrite`, `must_kv_commit`, and `must_kv_put`. Backup scheduling helpers are `backup` for MVCC backup and `backup_raw` for raw backup; both build `BackupRequest`s against a local external storage backend and schedule a `Task` on every endpoint. Validation helpers include `admin_checksum`, `raw_kv_checksum`, and `storage_raw_checksum`. `name_to_cf` decodes SST CF from file names, and `make_unique_dir` creates random subdirectories.

## Control Flow And State
The suite is cluster-backed and mutable. Timestamp allocation increments local `TimeStamp`; transactional writes perform prewrite and commit RPCs with retries; raw operations adjust `Context` API version for V1ttl compatibility and use TTL according to destination API version. Backups fan out identical requests to every backup endpoint and return a futures channel receiver for collecting `BackupResponse`s.

## Persistence And Integration Points
The harness integrates with raftstore clusters, TiKV storage snapshots, backup workers, local external storage, raw/TiKV RPCs, coprocessor checksum logic, and API-version raw-value encoding. Persistent state lives in the test cluster engines and in local backup target directories.

## Risks And Test Signals
The `retry_req!` macro uses both retry count and elapsed-time conditions; long CI delays or leader changes can affect behavior. Raw checksum scanning uses internal data-key iteration and must respect CF and upper-bound encoding. `admin_checksum` scans through `SnapshotStore` and `RangesScanner`, making it a strong reference for backup results. Assertions in `must_*` methods fail fast on region errors or RPC errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_backup/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/Cargo.toml -->
# sources/storage-engines/tikv/components/test_coprocessor/Cargo.toml

## Purpose
This manifest defines the private `test_coprocessor` crate, a shared fixture library for building TiDB DAG requests and TiKV coprocessor storage data in tests.

## Dependencies And Features
Default features forward engine selections into `test_storage`: RocksDB KV engine and raft-engine raft storage. Alternate features expose all-RocksDB and panic-engine test modes. Dependencies include `tipb` and `kvproto` protobuf types, TiDB datatype and codec crates, TiKV storage/coprocessor APIs, `test_storage`, `pd_client`, `concurrency_manager`, `resource_metering`, and utilities.

## Integration, State, And Risks
The crate is a test-only bridge between schema/request builders and real TiKV coprocessor endpoints. Its feature forwarding means test behavior depends on selected engine features, so incompatible combinations can surface as compile-time or fixture initialization failures. The crate requires Rust specialization through its source, so it is tied to nightly/feature-gated compilation used by TiKV.

## Test Signals
This manifest is validated by consumers that compile and run coprocessor tests with the desired engine feature set. Dependency drift in protobuf or TiDB datatype APIs will generally show up as builder or request-encoding compile failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/column.rs -->
# sources/storage-engines/tikv/components/test_coprocessor/src/column.rs

## Purpose
This file defines lightweight schema-column fixtures for coprocessor tests. It turns local test column descriptions into TiDB protobuf `ColumnInfo` and `FieldType` values used by table scans, index scans, row encoding, and expressions.

## Important APIs, Types, And Functions
`TYPE_VAR_CHAR` and `TYPE_LONG` are local logical type markers. `Column` stores a generated ID, local type, index role, and optional default `Datum`. `Column::as_column_info` builds `tipb::ColumnInfo`, marks primary key handle columns, and encodes default values with `datum::encode_value`. `Column::as_field_type` and `col_field_type` map local markers to TiDB field type codes (`LongLong` and `VarChar`).

`ColumnBuilder` is a chainable builder. `col_type`, `primary_key`, `index_key`, and `default` configure the column before `build` assigns a unique ID using `next_id`.

## Control Flow, State, And Dependencies
Column IDs are globally generated by the test crate's atomic ID generator. Index semantics are represented by `index`: negative means non-index, zero means primary key, and positive values group normal index columns. The module depends on TiDB datum encoding and protobuf types but does not persist data itself.

## Risks And Test Signals
`col_field_type` panics on unknown local type markers, so tests must use the provided constants. Default-value encoding uses an empty default evaluation context and unwraps encoding. The main test signal is downstream: malformed column metadata will fail DAG request execution or row decoding in coprocessor tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/column.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/dag.rs -->
# sources/storage-engines/tikv/components/test_coprocessor/src/dag.rs

## Purpose
This file provides builders for TiDB DAG coprocessor requests and a chunk splitter for decoding streaming/select results into rows of `Datum`. It lets tests express table scans, index scans, selections, projections, aggregations, ordering, limits, paging, and index lookup DAGs without hand-writing protobuf wiring.

## Important APIs, Types, And Functions
`DagSelect` stores the executor chain, output columns, order-by expressions, aggregate/group expressions, key ranges, output offsets, paging, start timestamp, and intermediate-output channels. `from(table)` creates a table-scan DAG over all records; `from_index(table, index)` creates an index scan. Builder methods add operators: `index_lookup`, `limit`, `order_by`, aggregate helpers (`count`, `sum`, `avg`, etc.), `group_by`, `where_expr`, `projection`, `desc`, `paging_size`, `key_ranges`, and `start_ts`.

`build_with` appends aggregation, TopN, and Limit executors as needed, sets flags, output offsets, intermediate channels, request type `REQ_TYPE_DAG`, serialized `DagRequest`, ranges, paging size, context, and start TS. `DagChunkSpliter` iterates over `tipb::Chunk`s, decodes row data into datums, and yields fixed column-count rows.

## Control Flow And State
`DagSelect` mutates in builder style, with executor order determined by call sequence plus final `build_with` append logic. `index_lookup` rewrites executor parents, inserts a table scan and `IndexLookUp` executor, and transfers output offsets through an `IntermediateOutputChannel`. `DagChunkSpliter::next` lazily removes chunks, decodes all datums for a chunk, then splits off row-sized groups.

## Integration Points
The module integrates `kvproto::coprocessor::Request`, `tipb` executors, TiDB datum encoding, table/key-range helpers, and the crate's `Table`, `Column`, and `offset_for_column`. It is used by tests that feed requests to a TiKV coprocessor `Endpoint`.

## Risks And Test Signals
Several paths unwrap protobuf serialization, datum decode, and number encoding. `desc` assumes the first executor is a table scan and will not work for index scans. `offset_for_column` returns zero when not found, so expression builders can silently target the first column if schema metadata is wrong. Chunk splitting removes from the front of a vector and asserts enough datums remain. Tests should validate both unary and streaming responses when using complex DAGs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/dag.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/fixture.rs -->
# sources/storage-engines/tikv/components/test_coprocessor/src/fixture.rs

## Purpose
This file builds ready-to-use coprocessor test fixtures: a canonical product table, in-memory/test-engine data insertion, committed MVCC state, read pools, quota limiters, and `Endpoint` instances.

## Important APIs, Types, And Functions
`ProductTable` wraps a `Table` with `id` as primary key and `name`/`count` sharing an index. `init_data_with_engine_and_commit` and variants initialize data into a provided engine, optionally commit it, and return `(Store<E>, Endpoint<E>, Arc<QuotaLimiter>)`. `init_data_with_details_pd_client` allows a test PD client to supply TSO values. V2 checksum variants use row codec v2 and optional checksum injection. Convenience helpers `init_data_with_commit`, `init_with_data`, `init_with_data_ext`, and `init_data_with_commit_v2_checksum` allocate a Rocks test engine internally.

## Control Flow And State
Initialization builds `StorageApiV1` from an engine and mock lock manager, wraps it in the crate's `Store`, begins a transaction, inserts all supplied rows, optionally commits, then constructs a coprocessor read pool and endpoint. Row insertion paths choose either legacy row encoding or v2 row encoding with checksum based on codec version.

## Persistence And Integration Points
The inserted state is persisted in the supplied test engine as MVCC prewrites/commits. The module integrates with `TestStorageBuilderApiV1`, `MockLockManager`, `ConcurrencyManager`, `ResourceTagFactory`, `QuotaLimiter`, `ReadPool`, and TiKV server/coprocessor configs.

## Risks And Test Signals
The product-table V2 path calls `name.unwrap()`, so V2 checksum helpers require non-null names except where callers intentionally use separate null-row helpers. Global thread-group properties are set for tests and may affect process-wide test state. The returned quota limiter is useful for tests that assert resource-limiting behavior around the endpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/lib.rs -->
# sources/storage-engines/tikv/components/test_coprocessor/src/lib.rs

## Purpose
This crate root exposes the coprocessor test fixture API. It enables specialization, declares internal modules for schema/request/storage helpers, and re-exports their public items for test code.

## Important APIs And Integration Points
Modules are `column`, `dag`, `fixture`, `store`, `table`, and `util`. The root re-export `pub use crate::{column::*, dag::*, fixture::*, store::*, table::*, util::*};` makes builder types such as `ColumnBuilder`, `TableBuilder`, `DagSelect`, `Store`, `ProductTable`, and request helpers available directly from `test_coprocessor`.

## State And Risks
The crate uses `#![feature(specialization)]` and `#![allow(incomplete_features)]`, mostly because `store.rs` implements a default generic conversion trait with specializations. That ties this test crate to TiKV's nightly-capable build configuration. There is no runtime state in the root itself; state is owned by the submodules.

## Test Signals
Failures here are compile-time: module visibility or re-export changes can break a broad set of coprocessor tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/store.rs -->
# sources/storage-engines/tikv/components/test_coprocessor/src/store.rs

## Purpose
This file implements a small transactional MVCC store wrapper for coprocessor tests. It can insert/delete table rows and indexes, commit them through `SyncTestStorageApiV1`, export committed data, and convert committed state into `SnapshotStore` or `FixtureStore`.

## Important APIs, Types, And Functions
`Insert<'a, E>` accumulates per-column legacy `Datum` values and row-v2 `ScalarValue`s. `execute_with_ctx` encodes a row key/value, prepares secondary index KVs, and prewrites them. `execute_with_v2_checksum` writes row codec v2 data, optionally with checksum. `Delete<'a, E>` computes row and index keys for a row and prewrites deletes.

`Store<E>` wraps `SyncTestStorageApiV1`, current and last committed timestamps, buffered handles to commit, and an optional PD client for TSO allocation. `begin` chooses a timestamp, `put` and `delete` prewrite mutations, `commit_with_ctx` commits all buffered handles, `export` scans committed data, `to_snapshot_store` and `to_fixture_store` expose committed views, and `insert_all_null_row` creates a row-v2 null row. `ToTxnStore` uses specialization to convert `Store` into concrete storage backends.

## Control Flow And State
All writes are two-phase: `begin` establishes `current_ts`, insert/delete prewrite mutations and record raw handles, then `commit` drains handles and updates `last_committed_ts`. Without a PD client, timestamps come from the crate's atomic `next_id`; with a PD client, `get_tso` is awaited with a five-second timeout.

## Persistence And Integration Points
The persisted state is the underlying test engine's MVCC data. Integration points include TiDB row/table codecs, `txn_types::Mutation`, `SnapshotStore`, `FixtureStore`, `GcConfig`, and the `test_storage` synchronous API.

## Risks And Test Signals
`put` assumes at least one KV and uses the first as primary. `delete` deduplicates only adjacent equal keys, so callers should pass stable rows if duplicates matter. `export` is capped at 100,000 records. The unit test `test_export` verifies commit visibility, delete behavior, ordering, duplicate deletes, and uncommitted data isolation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/table.rs -->
# sources/storage-engines/tikv/components/test_coprocessor/src/table.rs

## Purpose
This file defines table-schema fixtures for coprocessor tests. It maps named columns to IDs, builds TiDB protobuf table/index metadata, and creates table/index key ranges compatible with TiDB table encoding.

## Important APIs, Types, And Functions
`Table` stores table ID, handle column ID, ordered columns, name/ID lookup maps, and index definitions. `column_by_id`, `column_by_name`, and `Index` access columns case-insensitively. `table_info`, `columns_info`, and `index_info` build `tipb` metadata. Range helpers include `get_record_range_all`, `get_record_range`, `get_record_range_one`, `get_index_range_all`, and `get_table_prefix`.

`TableBuilder` collects columns, tracks a primary handle column, then `build` assigns a table ID, lookup maps, and index-column groups. For secondary indexes it appends the table handle to the index column list to model non-unique index entries.

## Control Flow And State
Table and column IDs are generated with the crate-global `next_id`. `add_col` updates handle selection when it sees `Column.index == 0`; if no explicit handle exists, `build` creates a synthetic handle ID. Index maps are derived from column metadata after all columns are registered.

## Persistence And Integration Points
The table object itself is in-memory metadata. It integrates with TiDB table key encoding, `tipb::{TableInfo, IndexInfo, ColumnInfo}`, and `KeyRange` protobufs consumed by `DagSelect` and coprocessor requests.

## Risks And Test Signals
`index_info` indexes directly into `self.idxs[&index]`, so invalid index IDs panic. `get_index_range_all` only encodes min/max i64 prefixes, which matches these simple fixtures but not arbitrary composite key domains. Case normalization can hide duplicate column names with different casing. Downstream test signals come from table scan/index scan correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/util.rs -->
# sources/storage-engines/tikv/components/test_coprocessor/src/util.rs

## Purpose
This file contains general coprocessor test utilities: a global test ID generator, synchronous wrappers around coprocessor endpoint handling, result protobuf decoding, streaming response collection, and column-offset lookup.

## Important APIs And Functions
`next_id` increments an `AtomicUsize` with relaxed ordering and returns an `i64`. `handle_request` blocks on `Endpoint::parse_and_handle_unary_request` and consumes the response. `handle_select` decodes the response data into `tipb::SelectResponse`. `handle_streaming_select` maps streaming endpoint responses into `tipb::StreamResponse`s while allowing a caller-provided range check. `offset_for_column` returns the index of a column ID in a `ColumnInfo` slice.

## Control Flow And State
The utilities convert asynchronous coprocessor APIs into blocking test APIs. Streaming requests are collected fully before returning, so tests can inspect the complete response vector. The ID generator is process-global across the crate and intentionally simple.

## Dependencies And Integration Points
The file integrates `tikv::coprocessor::Endpoint`, TiKV `Engine`, `kvproto::coprocessor`, protobuf message decoding, futures executors/streams, and `tipb` response types.

## Risks And Test Signals
`handle_select` and streaming decoding assert non-empty response data and unwrap protobuf merges; error responses must be tested through lower-level APIs if needed. `offset_for_column` returns `0` when a column is not found, which can mask schema mistakes by targeting the first column. Because `next_id` uses relaxed ordering, it guarantees uniqueness but not synchronization semantics, which is sufficient for these tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor_plugin/example_plugin/Cargo.toml -->
# sources/storage-engines/tikv/components/test_coprocessor_plugin/example_plugin/Cargo.toml

## Purpose
This manifest defines `example_coprocessor_plugin`, a private dynamic-library example for the coprocessor plugin API.

## Dependencies And Integration Points
The `[lib]` section sets `crate-type = ["dylib"]`, which is required for runtime plugin loading rather than normal static Rust linkage. Its only dependency is the workspace `coprocessor_plugin_api`, making it a minimal compatibility fixture.

## State, Persistence, And Risks
There is no manifest-level state or persistence. The main risk is ABI/API compatibility: because this crate builds as a dynamic library, changes in plugin declaration, exported symbols, or the plugin API surface should be caught by compiling/loading this example.

## Test Signals
Successful build proves the example can link against `coprocessor_plugin_api` as a dynamic plugin. Runtime tests must still verify that the exported plugin declaration loads as expected.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor_plugin/example_plugin/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor_plugin/example_plugin/src/lib.rs -->
# sources/storage-engines/tikv/components/test_coprocessor_plugin/example_plugin/src/lib.rs

## Purpose
This is the minimal dynamic plugin implementation for coprocessor plugin tests. It proves that the plugin API macro and trait can produce a loadable plugin library.

## Important APIs, Types, And Functions
`ExamplePlugin` is an empty `Default` type implementing `CoprocessorPlugin`. Its `on_raw_coprocessor_request` method has the expected API shape: ranges, raw request, raw storage, and `PluginResult<RawResponse>`. The implementation is `unimplemented!()`. `declare_plugin!(ExamplePlugin)` emits the plugin registration/export required by the plugin runtime.

## Control Flow, State, And Integration Points
There is no runtime state. Control reaches the plugin only if a raw coprocessor request is dispatched to it; at that point it panics because the example is intentionally not functional. It integrates solely with `coprocessor_plugin_api` and Rust's dynamic-library build mode from the manifest.

## Risks And Test Signals
The unimplemented method means this plugin should be used for loading/registration tests, not request-processing behavior. Any test that invokes the raw request hook should expect a panic or update this implementation. Build and plugin discovery are the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_coprocessor_plugin/example_plugin/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/Cargo.toml -->
# sources/storage-engines/tikv/components/test_pd/Cargo.toml

## Purpose
This manifest defines the private `test_pd` crate, a gRPC-backed mock PD server library for TiKV tests.

## Dependencies And Integration Points
The crate depends on `kvproto`, `grpcio`, `pd_client`, `security`, `tikv_util`, logging crates, `fail`, `futures`, and `tokio`/`tokio-stream`. Those dependencies match its role: serve PD, MetaStorage, and resource-manager protobuf services, support TLS/security manager binding, inject failpoints, and run async streaming handlers.

## State, Persistence, And Risks
The manifest brings in full async and gRPC stacks for tests. Runtime state lives in in-memory mockers and server instances; no persistence dependencies are declared. Because this crate simulates protocol behavior, dependency/API drift in `kvproto` or `pd_client` will surface at compile time.

## Test Signals
Successful compilation validates that the mock server implements the current PD-related protobuf traits. Integration tests use this crate to verify client reconnect, leader changes, metadata storage, retry, split, and service-GC behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/lib.rs -->
# sources/storage-engines/tikv/components/test_pd/src/lib.rs

## Purpose
This crate root exposes the mock PD server test library. It imports TiKV logging macros, declares `mocker`, `server`, and `util` modules, and re-exports the core extension trait and server wrapper.

## Important APIs And Integration Points
`pub mod mocker` exposes mocker implementations and the `PdMocker` trait. `mod server` contains the gRPC server implementation. `pub mod util` contains client-construction helpers. `pub use self::{mocker::PdMocker, server::Server};` makes the primary testing surface available to downstream tests.

## State And Risks
The root itself owns no state. The `#[macro_use] extern crate` declarations are legacy-style macro imports for `tikv_util` and `slog_global`; removing or modernizing them could affect logging macro availability in submodules.

## Test Signals
Compile failures here generally indicate module/API export breakage across test code that imports `test_pd::Server` or `test_pd::PdMocker`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/bootstrap.rs -->
# sources/storage-engines/tikv/components/test_pd/src/mocker/bootstrap.rs

## Purpose
This mocker simulates a PD server that reports an already-bootstrapped cluster when bootstrap is attempted.

## Important APIs And Functions
`AlreadyBootstrapped` implements `PdMocker`. `bootstrap` returns a `BootstrapResponse` whose header contains `ErrorType::AlreadyBootstrapped`, message `"cluster is already bootstrapped"`, and the default cluster ID. `is_bootstrapped` returns a response with the default cluster ID but `bootstrapped` set to false.

## Control Flow, State, And Integration Points
The mocker is stateless and purely response-driven. It plugs into `Server::with_case` through the `PdMocker` trait, overriding only bootstrap-related RPCs while all other calls can fall back to the default service.

## Risks And Test Signals
The deliberately inconsistent `is_bootstrapped(false)` plus bootstrap error models edge cases around bootstrap races or stale client assumptions. Tests using this mocker should assert exact PD error interpretation rather than normal cluster lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/bootstrap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/etcd.rs -->
# sources/storage-engines/tikv/components/test_pd/src/mocker/etcd.rs

## Purpose
This file implements a small in-memory, revisioned etcd-like key-value store used by the PD MetaStorage mock. It supports range/key/prefix reads, puts, deletes with tombstones, and watch streams.

## Important APIs, Types, And Functions
`Etcd` stores versioned `items` in a `BTreeMap<Key, Value>`, active subscribers, current revision, and a subscriber ID allocator. `get_key` returns the latest non-deleted value per logical key in a requested range plus the current revision. `set` allocates a new revision, notifies matching subscribers with `KvEventType::Put`, and stores a `Value::Val`. `delete` tombstones matching keys and notifies subscribers with `Delete` events carrying previous data. `watch` sends historical events from `start_rev` and registers a live mpsc subscriber.

`MetaKey` provides `next` and `next_prefix` range-bound helpers. `KeyValue`, `KvEventType`, `KvEvent`, and `Keys` are the public data wrappers used by `meta_storage.rs`.

## Control Flow And State
Every mutation increments `revision`. The backing map stores `(key, revision)` entries, so historical events remain available for watch startup. Reads chunk by logical key and choose the last revision in range, filtering tombstones. Watches use bounded Tokio mpsc channels and are retained in `subs` until `clear_subs` or store drop.

## Persistence And Integration Points
There is no disk persistence; this is process-local test state. It integrates with `MetaStorage` through an `Arc<Mutex<Etcd>>` client and returns `ReceiverStream<KvEvent>` for gRPC streaming.

## Risks And Test Signals
The store is a simplified etcd model: no compaction, transactions, leases, compare-and-swap, or subscriber removal on stream close. `set`/`delete` unwrap subscriber sends, so dropped receivers can panic. Prefix end calculation for all-`0xff` keys can shrink to an empty bound, so tests should stay in normal metadata key domains.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/etcd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/incompatible.rs -->
# sources/storage-engines/tikv/components/test_pd/src/mocker/incompatible.rs

## Purpose
This mocker simulates an incompatible PD version for batch split requests.

## Important APIs And Functions
`Incompatible` implements `PdMocker::ask_batch_split` and returns an `AskBatchSplitResponse` whose header contains `ErrorType::IncompatibleVersion`.

## Control Flow, State, And Integration Points
The mocker is stateless and overrides only `ask_batch_split`; other RPCs can fall back to the default service. It is used through the generic mock server to exercise client behavior when PD lacks or rejects a feature.

## Risks And Test Signals
Because the method returns an OK gRPC response with a PD header error, tests should verify header-error interpretation rather than transport failure handling. This mocker is narrow and should not be used to simulate general version negotiation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/incompatible.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/leader_change.rs -->
# sources/storage-engines/tikv/components/test_pd/src/mocker/leader_change.rs

## Purpose
This mocker simulates PD leader changes and a dead PD member so clients can test reconnect and leader-refresh behavior.

## Important APIs, Types, And Functions
`LeaderChange` owns a mutex-protected `Inner` containing prebuilt `GetMembersResponse`s and a `Roulette` with last-change timestamp and index. `get_leader_interval` returns the fixed two-second leader interval. `set_endpoints` builds a PD member list from bound server endpoints, appends a dead member at `127.0.0.1:65534`, and creates one response per live endpoint with a different leader. `get_members` rotates leader after the interval and returns `"not leader"` once when rotating. `get_region_by_id` also errors after the interval to force retry.

## Control Flow And State
State advances with wall-clock time. Before the interval expires, calls return the current response. Once expired, the index increments, timestamp resets, and the first call gets an error so the client updates its connection.

## Persistence And Integration Points
This is in-memory test state integrated through `PdMocker`. It uses PD protobuf `Member`/`GetMembersResponse` and the mock server's endpoint injection.

## Risks And Test Signals
Tests are timing-sensitive because behavior changes after two seconds. `get_members` indexes `inner.resps` and assumes `set_endpoints` has run before use. The dead member checks client robustness against unreachable PD addresses.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/leader_change.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/meta_storage.rs -->
# sources/storage-engines/tikv/components/test_pd/src/mocker/meta_storage.rs

## Purpose
This mocker implements PD MetaStorage RPCs over the in-memory `Etcd` emulator. It lets tests exercise metadata get/put/delete/watch behavior without a real etcd.

## Important APIs And Functions
`MetaStorage` owns `Arc<Mutex<Etcd>>`. `check_header` requires `RequestHeader.source` to be non-empty and returns an error otherwise. `meta_store_get` maps key/range requests to `Keys`, reads items and revision, and returns protobuf `KeyValue`s with a revision header. `meta_store_put` stores a key/value pair. `meta_store_delete` deletes a single key. `meta_store_watch` validates the header, opens an etcd watcher from the requested revision, and spawns a gRPC streaming task that converts put/delete events into `mpb::WatchResponse`s.

## Control Flow And State
Unary calls lock the backing store and use `block_on` for async etcd operations. Watch calls create a receiver stream and then release control to a spawned async loop that sends responses until the watcher ends. Delete events include `prev_kv` as well as event key/value.

## Persistence And Integration Points
Persistence is in-memory only through `Etcd`. The mocker integrates with the `meta_storagepb` gRPC service implementation in `server.rs` and grpcio streaming sinks.

## Risks And Test Signals
Invalid headers are surfaced as either trait errors for unary calls or `INVALID_ARGUMENT` stream failure for watch calls. The store lock is a standard mutex while etcd methods are async and then blocked on; this is acceptable for tests but not a production pattern. Watch send unwraps can panic if the client disconnects unexpectedly.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/meta_storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/mod.rs -->
# sources/storage-engines/tikv/components/test_pd/src/mocker/mod.rs

## Purpose
This module defines the extension trait and exports all PD mocker cases used by the `test_pd` server.

## Important APIs, Types, And Functions
`DEFAULT_CLUSTER_ID` is `42`. `Result<T>` is a simple `Result<T, String>` used by mocker overrides. `PdMocker` is a broad trait with default `None` implementations for PD, MetaStorage, and resource-manager RPCs. Returning `None` means the server should try the default service or report unimplemented. Returning `Some(Ok(resp))` sends a response; `Some(Err(err))` becomes a gRPC unknown error in `hijack_unary`.

The trait covers membership, TSO, bootstrap, store/region metadata, splits, cluster config, scatter, GC safe points, service GC safe points, metadata storage, resource-unit metrics, and endpoint injection. It exports `AlreadyBootstrapped`, `Incompatible`, `LeaderChange`, `MetaStorage`, `Retry`, `NotRetry`, `Service`, and `Split`.

## Control Flow And State
This file defines no concrete state beyond constants; it establishes the dispatch contract used by `server.rs`. Default `report_ru_metrics` asserts resource bucket requests are background and then returns `None`, so default service handling can continue or the server can ignore depending on RPC path.

## Risks And Test Signals
Adding new PD RPCs requires extending this trait and `server.rs`; otherwise calls will be unimplemented. The `Option<Result<T>>` dispatch model is compact but easy to misuse: `None` is fallback, not success. Tests should choose narrow mockers to override only behavior under test.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/retry.rs -->
# sources/storage-engines/tikv/components/test_pd/src/mocker/retry.rs

## Purpose
This file contains mockers for PD client retry behavior. One mocker produces transport-style retryable errors before eventual success; another returns PD header errors that should not trigger the same retry path.

## Important APIs, Types, And Functions
`Retry` stores a retry interval count and atomic call counter. `is_ok` returns true only when the count is nonzero and divisible by `retry`; otherwise it sleeps for `REQUEST_RECONNECT_INTERVAL` and returns false. It overrides `get_region_by_id` and `get_store`, returning `Err("please retry")` until the scheduled success.

`NotRetry` stores an atomic visited flag. On the first `get_region_by_id`, it returns an OK response with header `RegionNotFound`; on the first `get_store`, an OK response with header `Unknown`; later calls return empty OK responses.

## Control Flow And State
Both mockers are stateful through atomics. `Retry` simulates repeated gRPC failures and delays to give clients time to update connections. `NotRetry` simulates server-level semantic errors carried in PD response headers, not transport errors.

## Integration Points And Risks
These mockers integrate through `PdMocker` and PD protobuf response headers. `Retry::new(0)` would panic on modulo by zero, so callers must pass a positive retry interval. Shared `NotRetry` state is reused across both methods, so invoking one method first changes the other's first-call behavior.

## Test Signals
Tests should assert retry loops recover from `Retry` errors after expected attempts and that header errors from `NotRetry` are surfaced without inappropriate reconnect retry behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/retry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/service.rs -->
# sources/storage-engines/tikv/components/test_pd/src/mocker/service.rs

## Purpose
`Service` is the default in-memory PD mock implementation. It maintains basic cluster membership, store metadata, regions, leaders, bucket reports, feature-gate version, and service GC safe point state for tests that need a functional PD server.

## Important APIs, Types, And Functions
`Service` stores an ID allocator, cached members response, bootstrapped flag, store map with stats, region map, bucket map, leader map, feature-gate string, and service GC safepoint. `header` creates a default cluster response header. `add_store` and `set_cluster_version` allow tests to mutate service state. `make_members_response` builds PD members and leader from bound endpoints.

The `PdMocker` implementation supports `get_members`, bootstrap lifecycle, ID allocation, store get/list/heartbeat, region get/by-id/heartbeat, bucket reports, split/scatter/operator/config placeholders, `put_store`, GC safe point placeholder, and `update_service_gc_safe_point`.

## Control Flow And State
Bootstrap stores the initial store and region and flips `is_bootstrapped`. Heartbeats update region/leader or store stats maps. `alloc_id` uses an atomic counter and has a failpoint to simulate leader connection issues. `update_service_gc_safe_point` keeps a monotonic minimum safe point unless TTL zero resets it.

## Persistence And Integration Points
All state is in-memory. The service is the fallback handler in `PdMock` and backs most RPCs when a case mocker returns `None`. It integrates with `kvproto::pdpb` and `metapb` structures.

## Risks And Test Signals
This is intentionally incomplete compared with real PD: many responses are placeholders, some TODOs note missing cluster-ID and bootstrapped checks, and service safe point handling ignores multiple services. Header errors are returned in OK responses for not-found store/region cases. Tests should avoid relying on exact real-PD scheduling semantics beyond what this mock explicitly tracks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/split.rs -->
# sources/storage-engines/tikv/components/test_pd/src/mocker/split.rs

## Purpose
This mocker simulates PD membership responses with changing cluster IDs, mainly for split-brain or cluster-ID consistency tests.

## Important APIs, Types, And Functions
`Split` owns a mutex-protected optional `Inner` containing response variants and a current index. `set_endpoints` builds members from server endpoints and precomputes one `GetMembersResponse` per endpoint. Each response has a distinct cluster ID starting at one and uses the first member as leader. `get_members` increments the index and returns the next response cyclically.

## Control Flow And State
The mocker is initialized by `set_endpoints` after server binding. Every `get_members` call advances state, so clients observe rotating cluster IDs across membership refreshes.

## Persistence And Integration Points
State is in-memory and plugged into the PD mock server through `PdMocker`. It uses PD membership protobufs only.

## Risks And Test Signals
`get_members` unwraps `inner`, so the server must call `set_endpoints` before requests arrive. Cluster-ID rotation is artificial and should be used only for tests that intentionally validate client handling of inconsistent PD membership responses.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/mocker/split.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/server.rs -->
# sources/storage-engines/tikv/components/test_pd/src/server.rs

## Purpose
This file implements the gRPC mock PD server. It hosts PD, MetaStorage, and resource-manager services, dispatches calls to optional case-specific mockers, falls back to the default `Service`, and exposes helpers for tests to start/stop servers and build clients.

## Important APIs, Types, And Functions
`Server<C>` owns an optional grpcio server and a `PdMock<C>`. `Server<Service>::new` creates a default service-backed server. `Server::with_case` injects an `Arc<C: PdMocker>`. `with_configuration` builds the default handler, mock wrapper, TSO logical counter, and in-memory etcd client, then starts the server. `start` registers PD, MetaStorage, and resource-manager services, binds through `SecurityManager`, injects bound endpoints into handlers, and sleeps briefly for readiness. `bind_addrs` exposes actual bound addresses.

`hijack_unary` is the central dispatch helper for unary RPCs. It tries the case mocker, then default handler, maps `Ok` to successful sink responses, `Err` to gRPC UNKNOWN failures, and `None` to UNIMPLEMENTED unless the `connect_leader` failpoint rewrites it as UNAVAILABLE.

`PdMock<C>` implements `MetaStorage`, `Pd`, and `resource_manager::ResourceManager`. It implements streaming TSO, region heartbeat, bucket reporting, token bucket acquisition, and many unary PD RPCs through `hijack_unary`.

## Control Flow And State
The mock is cloneable via shared `Arc`s. TSO streaming uses an atomic logical counter with fixed physical time `42`. Region heartbeat and resource-manager streams filter incoming requests through case/default mockers and send responses only when mockers return `Some(Ok(_))`. MetaStorage watch delegates directly to the case mocker and otherwise returns unimplemented.

## Persistence And Integration Points
All server state is in-memory: default service state, optional case state, TSO counter, and etcd client. It integrates tightly with grpcio generated service traits, `security::SecurityManager`, PD client error conversion, failpoints, and protobuf service definitions.

## Risks And Test Signals
`stop` panics if the server is not started. The one-second startup sleep is coarse and can slow tests. Several PD RPCs remain `unimplemented!()`, so tests must avoid unsupported methods or extend the mock. Streaming sinks often ignore or unwrap send results, which is acceptable for controlled tests but can panic on unexpected disconnects. Correct dispatch ordering is the key behavior to validate when adding mockers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/util.rs -->
# sources/storage-engines/tikv/components/test_pd/src/util.rs

## Purpose
This file provides helper constructors for PD RPC clients pointed at mock PD server endpoints.

## Important APIs And Functions
`new_config` converts `(host, port)` tuples into a `pd_client::Config` endpoint list. `new_client` and `new_client_v2` build `RpcClient` and `RpcClientV2` using either a provided `SecurityManager` or a default insecure one. `new_client_with_update_interval` and `new_client_v2_with_update_interval` also override the client's PD membership update interval.

## Control Flow And State
The helpers are pure constructors except for allocating a default `SecurityManager`. They unwrap client creation, so construction failures are test failures.

## Integration Points And Risks
They integrate with `pd_client::{RpcClient, RpcClientV2, Config}`, `security`, and `ReadableDuration`. Endpoint strings are formatted as `host:port` without URI schemes. Tests that need TLS must pass a configured security manager.

## Test Signals
These utilities are validated indirectly by tests that start `test_pd::Server`, call `bind_addrs`, and construct clients with the returned addresses.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd_client/Cargo.toml -->
# sources/storage-engines/tikv/components/test_pd_client/Cargo.toml

## Purpose
This manifest defines the private `test_pd_client` crate, an in-memory implementation of TiKV's `PdClient` trait used by raftstore and storage tests.

## Dependencies And Integration Points
Dependencies include `pd_client`, `kvproto`, `keys`, `raft`, `txn_types`, `tikv_util`, logging, failpoints, futures, grpcio error types, and `tokio-timer`. These match the crate's role as a fake PD client that generates IDs/TSOs, tracks regions/stores, emits heartbeat responses, and simulates scheduling operators.

## State, Persistence, And Risks
There is no disk persistence. Runtime state is all in memory inside `TestPdClient` and `PdCluster`. Because the crate implements a wide `PdClient` trait, it is sensitive to trait evolution in `pd_client`. Failpoint and timer dependencies allow tests to model asynchronous and failure behavior.

## Test Signals
Compile-time validation ensures the fake client still satisfies `PdClient`. Raftstore integration tests provide behavioral coverage for scheduling, bootstrap, split/merge, TSO, GC safe point, replication mode, unsafe recovery, and bucket reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd_client/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd_client/src/lib.rs -->
# sources/storage-engines/tikv/components/test_pd_client/src/lib.rs

## Purpose
This crate root exposes the in-memory test PD client implementation.

## Important APIs And Integration Points
It imports TiKV utility macros, declares the internal `pd` module, and re-exports all public items from it. Consumers can import `TestPdClient`, scheduling helper constructors, constants such as `INIT_EPOCH_VER`, and `bootstrap_with_first_region` directly from `test_pd_client`.

## State And Risks
The root owns no state. Its main risk is broad API exposure: because it re-exports the entire `pd` module, changes inside `pd.rs` can affect downstream tests directly.

## Test Signals
Compile failures at this root usually indicate module visibility, macro import, or re-export changes that break raftstore/storage tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd_client/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd_client/src/pd.rs -->
# sources/storage-engines/tikv/components/test_pd_client/src/pd.rs

## Purpose
This file implements `TestPdClient`, a rich in-memory implementation of TiKV's `PdClient` trait. It models PD cluster metadata, stores, regions, leaders, operators, heartbeats, TSO allocation, GC safe points, replication status, bucket reports, and unsafe recovery hooks for raftstore and storage tests.

## Important APIs, Types, And Functions
Top-level helpers build PD heartbeat responses: `new_pd_change_peer`, `new_pd_change_peer_v2`, `new_split_region`, `new_pd_transfer_leader`, `new_pd_merge_region`, and `new_pd_batch_switch_witnesses`. `SchedulePolicy` controls operator repetition. `Operator` variants represent add/remove peer, transfer leader, merge, split, leave joint, joint conf change, and witness switching. `Operator::make_region_heartbeat_response` converts pending operators into PD responses, while `try_finished` checks observed region/leader state to decide whether to continue.

`PdCluster` stores all mutable metadata: cluster config, stores with heartbeat channels, regions indexed by encoded end key and ID, region stats, operators, leaders, down/pending peers, bootstrap flag, GC/min resolved timestamps, replication status, unsafe recovery reports/plans, and bucket stats. Its methods bootstrap the cluster, allocate IDs, manage stores/regions, validate stale epochs and overlaps, process heartbeats, poll scheduled heartbeat responses, and handle store heartbeat recovery plans.

`TestPdClient` wraps `PdCluster` in `Arc<RwLock<_>>`, owns timer and failure flags, TSO counter, feature gate, and service safe points. It provides many test convenience methods such as `must_add_peer`, `must_remove_peer`, `must_split_region`, `must_merge`, `transfer_leader`, `joint_confchange`, `switch_witnesses`, replication-mode configuration, TSO manipulation, and unsafe-recovery plan/report access.

## Control Flow And State
Cluster state changes mostly through `PdClient` trait methods and explicit test helpers. Bootstrap seeds the first store and region. Region heartbeats validate epochs/overlaps, update leaders and stats, and send scheduled operator responses to the leader store's channel. `handle_region_heartbeat_response` combines direct queued responses with periodic polling every 500 ms, so operators can be resent until observed as complete. TSO allocation is atomic and handles logical overflow by advancing physical time.

## Persistence And Integration Points
All state is in-memory. The client integrates with TiKV's `PdClient` trait, raft protobuf conf changes, region/store protobufs, key encoding helpers, failpoints, global timer handle, feature gates, and raftstore utility functions for peer lookup and key-in-region checks.

## Risks And Test Signals
This is a broad fake PD, not a full PD. Epoch/overlap checks approximate stale-region handling; default max-peer scheduling can add/remove peers automatically unless disabled; many `must_*` helpers spin up to 500 times with 10 ms sleeps. `set_tso` panics if asked to decrease time. `trigger_tso_failure` and failpoints model transient failures. Tests validate behavior through convenience assertions, heartbeat-response streams, region counts, leader checks, split/merge completion, store stats, bucket merges, service safe point records, and unsafe-recovery report/plan exchange.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_pd_client/src/pd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/Cargo.toml -->
# sources/storage-engines/tikv/components/test_raftstore-v2/Cargo.toml

## Purpose
This manifest defines the private `test_raftstore-v2` crate, a test support crate for TiKV's raftstore-v2 implementation and compatibility with existing raftstore test infrastructure.

## Dependencies And Features
Default features select RocksDB KV engine and raft-engine raft storage by forwarding feature flags to `raftstore`. Additional features enable all-RocksDB and panic-engine modes. Dependencies are extensive and include API versioning, causal timestamps, concurrency management, encryption export, engine traits/Rocks/test engines, filesystem, gRPC health, keys, kvproto, PD client, raft and raftstore crates with `testexport`, `raftstore-v2` with `testexport`, resolved timestamps, resource control/metering, server/service layers, security, temporary files, `test_pd_client`, `test_raftstore`, `test_util`, TiKV, utilities, Tokio, and transaction types.

## State, Persistence, And Integration Points
The manifest describes a high-integration crate that can instantiate real test engines, PD clients, raftstore services, server components, and resource-control paths. Runtime state and persistence are in the source files outside this manifest, but dependency selection here controls whether tests run against RocksDB, raft-engine, or panic engines.

## Risks And Test Signals
Because this crate bridges old and v2 raftstore test infrastructure, dependency/feature drift can create compile-time conflicts or behavior differences. The comment about preferring explicit loggers over `slog-global` signals a known test convenience tradeoff. Successful compilation with the intended features is the first signal; raftstore-v2 integration tests provide behavioral validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/Cargo.toml -->
