# subset-b-008925 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/histogram.rs -->
# sources/storage-engines/tikv/src/coprocessor/statistics/histogram.rs

## Purpose
Implements the coprocessor statistics histogram used for TiDB/TiKV analyze results. It incrementally receives already-sorted encoded datum bytes and builds a bounded bucket representation that can be serialized into `tipb::Histogram`.

## Important APIs, Types, and Functions
`Bucket` stores cumulative `count`, inclusive `lower_bound`/`upper_bound`, `repeats` for the upper bound, and optional per-bucket `ndv`. `Histogram` stores global `ndv`, `buckets`, `per_bucket_limit`, and `buckets_num`. `Histogram::new` starts with limit 1. `Histogram::append` is the public mutation path. `merge_buckets` halves bucket count by folding adjacent buckets and doubling `per_bucket_limit`. `From<Bucket>` and `From<Histogram>` convert internal state to protobuf `tipb` structures.

## Control Flow
`append` assumes each new item is greater than or equal to the current maximum. If it equals the last bucket upper bound, it only increments the current bucket count and repeat count, preserving the invariant that one value does not span buckets. New distinct values increment global `ndv`. If the bucket vector is at capacity and the last bucket is full, neighboring buckets are merged before insertion. The value is appended to the last bucket if it still has capacity; otherwise a new bucket is created with cumulative count inherited from the previous bucket.

## State and Persistence Behavior
All state is in memory until converted to `tipb::Histogram`. Bucket counts are cumulative rather than per-bucket, so readers must subtract previous bucket counts to recover bucket-local counts. `with_bucket_ndv` controls whether bucket `ndv` is maintained; global `ndv` is always updated for distinct append values.

## Dependencies and Integration Points
Depends on `tipb::{Histogram,Bucket}` for output and TiDB datum encoding in tests. This is part of `coprocessor::statistics` and is consumed by analyze/statistics code that must feed sorted encoded values.

## Risks and Edge Cases
The sorted-input contract is critical and not enforced. Supplying out-of-order bytes corrupts bounds and NDV semantics. `buckets_num == 0` would make `append` try to unwrap an empty last bucket after merge/capacity checks, so callers should avoid zero bucket counts. Merge logic uses cumulative-count rewrites and `mem::swap`, making off-by-one or odd bucket-count regressions high risk.

## Test Signals
`test_histogram` covers bucket creation, merges, repeated values, NDV, and per-bucket limits. `test_buckets_limit` covers single-bucket merge behavior. Tests exercise encoded TiDB `Datum::I64` values but do not cover zero bucket count or unsorted input.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/histogram.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/mod.rs -->
# sources/storage-engines/tikv/src/coprocessor/statistics/mod.rs

## Purpose
Declares the statistics submodules used by the legacy coprocessor analyze path.

## Important APIs, Types, and Functions
Exports `analyze`, `analyze_context`, `cmsketch`, `fmsketch`, and `histogram` as public modules. There are no local functions or data types.

## Control Flow
No runtime control flow exists in this file. Its effect is compile-time module wiring.

## State and Persistence Behavior
No state is stored here. Persistence behavior belongs to child modules and any protobuf structures they produce.

## Dependencies and Integration Points
Integrates TiKV's coprocessor statistics package into the crate namespace so callers can reference `coprocessor::statistics::*` modules. It directly enables histogram, count-min sketch, FM sketch, and analyze logic to be compiled and exported.

## Risks and Edge Cases
Renaming or removing a module here breaks downstream imports and feature composition. Because this is a module barrel, risk is mostly accidental API-surface change.

## Test Signals
No direct tests. Coverage comes from tests in child modules such as `histogram.rs` and from higher-level analyze tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/tracker.rs -->
# sources/storage-engines/tikv/src/coprocessor/tracker.rs

## Purpose
Tracks lifecycle timing, storage scan statistics, perf context counters, slow logs, read-flow metrics, and execution details for legacy coprocessor requests.

## Important APIs, Types, and Functions
`TrackerState` models a strict request lifecycle from `Initialized` through `Tracked`. `Tracker<E>` stores request context, request tag, timing accumulators, storage statistics, slow-log threshold, scan process time, optional bucket metadata, and engine type marker. Public transition methods include `on_scheduled`, `on_snapshot_finished`, `on_begin_all_items`, `on_begin_item`, `on_finish_item`, `on_finish_all_items`, and collectors for storage stats and scan process time. `get_item_exec_details` and `get_exec_details` build legacy and v2 `kvrpcpb::ExecDetails`. `FutureTrack` integration maps future polling to item begin/finish. `Drop` fast-forwards partially completed trackers so metrics are still emitted.

## Control Flow
Normal flow is initialize, schedule, retrieve snapshot, build handler, process one or more items, then finish all items. Each transition asserts the previous state. Item processing starts perf observation and finishes by reporting perf metrics to TLS tracker tokens. `track` emits slow logs when processing plus suspend time exceeds threshold, records histograms/counters, collects read flow for select/index tags, and reports MVCC read activity to `MVCC_READ_TRACKER` using perf context skipped-key counters.

## State and Persistence Behavior
State is transient per request. Effects persist only through metrics registries, TLS coprocessor metrics, slow logs, and MVCC read tracker observations. `Drop` mutates state to close unfinished lifecycles and may log deadline-exceeded warnings if the request deadline has passed.

## Dependencies and Integration Points
Depends on engine perf context traits, `kvproto` exec detail protobufs, `pd_client::BucketMeta`, tracker TLS APIs, coprocessor metrics, `ReqContext`, `ReqTag`, storage `Statistics`, and MVCC read tracking. It is a bridge between coprocessor request execution and observability.

## Risks and Edge Cases
Most public transition methods use `unreachable!` on invalid order, so callers must preserve lifecycle ordering. `Drop` can emit metrics for failed or abandoned paths, which is intentional but can obscure partial execution if interpreted as successful work. Perf context TLS is keyed by `ReqTag`; missing new tags would panic or omit metrics unless added to `with_perf_context`. Time conversions cast nanoseconds to `u64`, which is practically safe but relies on request durations remaining bounded.

## Test Signals
`test_track` checks read-flow collection only for select-like tags and validates bucket-level stats are collected for query traffic but not analyze traffic. There is limited direct coverage of state-machine invalid paths, slow-log fields, exec detail construction, deadline logging, and MVCC read tracker integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/tracker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor_v2/config.rs -->
# sources/storage-engines/tikv/src/coprocessor_v2/config.rs

## Purpose
Defines configuration for the v2 plugin-based coprocessor framework.

## Important APIs, Types, and Functions
`Config` is `Clone`, `Debug`, `Serialize`, `Deserialize`, `PartialEq`, and `Default`. Its only field is `coprocessor_plugin_directory: Option<PathBuf>`, deserialized with serde defaults and kebab-case names.

## Control Flow
No runtime control flow exists here. `Endpoint::new` consumes this config and starts plugin hot reloading only when the directory is present.

## State and Persistence Behavior
The config itself is in-memory after deserialization. It controls persistent filesystem interaction indirectly by selecting a plugin directory for dynamic libraries.

## Dependencies and Integration Points
Uses `serde_derive` macros from the crate root and standard `PathBuf`. Integrated by `coprocessor_v2::Endpoint` and the broader TiKV config system.

## Risks and Edge Cases
An absent directory disables coprocessor plugins. A configured directory causes TiKV to create/watch/load dynamic libraries from that path, so config validation and operational permissions matter.

## Test Signals
No direct tests. Behavior is indirectly covered by endpoint and plugin registry tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor_v2/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor_v2/endpoint.rs -->
# sources/storage-engines/tikv/src/coprocessor_v2/endpoint.rs

## Purpose
Provides the request endpoint for the plugin-based raw coprocessor framework. It dispatches `RawCoprocessorRequest` messages to dynamically loaded plugins and translates plugin/storage failures into protobuf responses.

## Important APIs, Types, and Functions
`Endpoint` holds an optional `Arc<PluginRegistry>`. `Endpoint::new` initializes the registry and starts hot reloading if a plugin directory is configured. `handle_request` returns a ready future containing `RawCoprocessorResponse`. `handle_request_impl` validates plugin availability, plugin name, semver constraint, constructs `RawStorageImpl`, converts request ranges to Rust ranges, and invokes `plugin.on_raw_coprocessor_request`. `extract_region_error` recovers region errors wrapped inside plugin `Other` errors.

## Control Flow
Requests are synchronously evaluated into a result, then wrapped in `std::future::ready`. Disabled plugin support returns a response error. Missing plugin names and semver parse/mismatch failures become string errors. Plugin errors that contain storage region errors are promoted to `region_error`; other plugin failures become response `error`.

## State and Persistence Behavior
Endpoint state is the shared plugin registry. Request handling does not mutate endpoint state but plugins may mutate raw storage through `RawStorageImpl` methods. Response data is plugin-provided opaque bytes.

## Dependencies and Integration Points
Depends on `coprocessor_plugin_api`, `kvproto::kvrpcpb`, `semver`, v2 config/registry/raw storage modules, and TiKV `Storage`. It is the service boundary between RPC handling and plugin code.

## Risks and Edge Cases
Plugin calls run in-process and can perform arbitrary plugin logic. Version constraints are request-controlled and must parse under semver. The future is ready, so any plugin work performed before returning can block the caller's execution context. Region-error extraction depends on plugin errors preserving the storage result in the expected `Any` payload.

## Test Signals
No direct tests in this file. Plugin registry and raw storage adapters have their own tests, but endpoint dispatch/version/error paths appear lightly covered.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor_v2/endpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor_v2/mod.rs -->
# sources/storage-engines/tikv/src/coprocessor_v2/mod.rs

## Purpose
Documents and wires TiKV's v2 plugin-based coprocessor framework.

## Important APIs, Types, and Functions
Declares private modules `config`, `endpoint`, `plugin_registry`, and `raw_storage_impl`; publicly re-exports `Config` and `Endpoint`.

## Control Flow
No runtime control flow exists in this module root. It establishes compile-time visibility and public API boundaries.

## State and Persistence Behavior
No local state. Child modules manage dynamic plugin state, filesystem watching, and raw storage access.

## Dependencies and Integration Points
The module-level docs describe the framework as distinct from the legacy fixed-function coprocessor and inspired by HBase/BigTable coprocessors. Public re-exports are consumed by server/config layers that instantiate the v2 endpoint.

## Risks and Edge Cases
Keeping `plugin_registry` and `raw_storage_impl` private limits external coupling. Changing re-exports would alter the public crate API.

## Test Signals
No tests here; coverage comes from child modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor_v2/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor_v2/plugin_registry.rs -->
# sources/storage-engines/tikv/src/coprocessor_v2/plugin_registry.rs

## Purpose
Loads, indexes, hot-reloads, and exposes dynamic coprocessor plugin libraries. It validates plugin ABI/build compatibility before constructing plugin instances.

## Important APIs, Types, and Functions
`PluginLoadingError` distinguishes dylib load failures, semver parse errors, rustc/target/API mismatches, and reload attempts. `PluginRegistry` wraps `Arc<RwLock<PluginRegistryInner>>` plus an optional filesystem watcher. Public methods load/unload plugins, start hot reloading, query by name/path, update paths, and list names. `PluginRegistryInner` stores `loaded_plugins: HashMap<String, (OsString, Arc<LoadedPlugin>)>` and `library_paths: HashSet<OsString>`. `LoadedPlugin::new` loads symbols, validates `BuildInfo`, constructs the plugin through `PLUGIN_CONSTRUCTOR_SYMBOL`, and intentionally leaks the `Library`. `LoadedPlugin` implements `CoprocessorPlugin` by delegation.

## Control Flow
`start_hot_reloading` creates the directory, starts one notify watcher thread if needed, registers the directory, and preloads existing library files. Create events attempt load; remove/write events warn that already-loaded code remains running; rename events update the stored path. `load_plugin` rejects any exact path previously loaded, constructs `LoadedPlugin`, records the path permanently in `library_paths`, and indexes by plugin name.

## State and Persistence Behavior
Registry state is in memory. Dynamic libraries are intentionally never unloaded from process memory because Rust/dylib plugin safety requires stable code and vtables. Unloading removes the name mapping but the path remains in `library_paths`, preventing reload from the same exact path. Filesystem state is watched but not authoritatively reconciled after deletion/overwrite.

## Dependencies and Integration Points
Depends on `libloading`, `notify`, `semver`, and `coprocessor_plugin_api` ABI symbols. `Endpoint` calls `get_plugin` for request dispatch. The plugin directory is configured by `coprocessor_v2::Config`.

## Risks and Edge Cases
Unsafe dynamic loading is central: symbol signatures and plugin ABI must match. Leaking libraries avoids unload hazards but means long-running processes retain code and memory. Path identity is exact and not canonicalized, so `./x.so` and `x.so` differ. Hot reload ignores load errors and cannot replace a loaded plugin on write/delete, which is operationally important. Duplicate plugin names overwrite previous loaded name entries while old library code remains leaked.

## Test Signals
Tests load the example plugin, verify registry lookup/path listing, path update, unload behavior, and hot-reload create/rename/remove behavior with sleeps for debounced notify. Tests do not cover duplicate names, relative path aliases, API mismatch, or semver parse failure in plugin metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor_v2/plugin_registry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor_v2/raw_storage_impl.rs -->
# sources/storage-engines/tikv/src/coprocessor_v2/raw_storage_impl.rs

## Purpose
Adapts TiKV `Storage` into the `coprocessor_plugin_api::RawStorage` trait exposed to v2 coprocessor plugins.

## Important APIs, Types, and Functions
`RawStorageImpl<'a, E, L, F>` stores a per-request `Context` and borrowed `Storage`. It implements async raw operations: `get`, `batch_get`, `scan`, `put`, `batch_put`, `delete`, `batch_delete`, and `delete_range`. `PluginErrorShim` converts TiKV storage errors and canceled callbacks into plugin errors.

## Control Flow
Read operations clone the request context, call storage raw read methods with an empty column family string, await the result, and convert kv pairs using `extract_kv_pairs`. Mutations create a paired callback/future, invoke the storage raw write API, then await callback completion and map both synchronous and callback errors. `scan` uses `usize::MAX` as limit, `key_only=false`, and forward order.

## State and Persistence Behavior
The adapter does not own persistent state. Mutating methods persist data through TiKV raw storage. It clones context per call to preserve request region/API metadata.

## Dependencies and Integration Points
Depends on `api_version::KvFormat`, `async_trait`, plugin API types, `kvproto::Context`, TiKV `Storage`, and lock manager traits. It is created by `Endpoint::handle_request_impl` for each plugin request.

## Risks and Edge Cases
`scan` can request an unbounded range with `usize::MAX`, so plugin-controlled ranges can be expensive. All operations use an empty CF string, which relies on storage raw API defaults. Error mapping only special-cases key-not-in-region and timeout; other storage errors are wrapped in `PluginError::Other` with a boxed `storage::Result<()>`, which endpoint later inspects for region errors.

## Test Signals
Async tests cover put/get/overwrite/delete, batch put/get/delete, scan ordering, missing keys, and delete range under API v2 test storage. Tests do not cover timeout, region errors, cancellation, large scans, or non-default CF behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor_v2/raw_storage_impl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/import/duplicate_detect.rs -->
# sources/storage-engines/tikv/src/import/duplicate_detect.rs

## Purpose
Scans MVCC write records to detect duplicate keys during Lightning/import workflows, returning duplicate key/value/commit-ts batches through `DuplicateDetectResponse`.

## Important APIs, Types, and Functions
`DuplicateDetector<S: Snapshot>` owns a snapshot, write-CF iterator, `key_only` flag, validity flag, and `min_commit_ts`. `new` builds encoded lower/upper bounds over `CF_WRITE` and seeks to the start key. `try_next` returns batches capped by `MAX_SCAN_BATCH_COUNT`. `move_to_next_import_key`, `collect_current_key_duplicate`, `skip_lock_and_rollback`, `skip_all_version`, and `make_kv_pair` implement MVCC traversal. It implements `Iterator<Item = DuplicateDetectResponse>`.

## Control Flow
The detector scans write CF entries ordered by encoded user key and commit timestamp. It only starts duplicate collection when it sees a commit ts greater than `min_commit_ts`. For a key, the first put above the threshold is remembered, subsequent put versions are emitted as duplicate pairs, and traversal stops for that key once an older non-import version or delete is encountered. Rollback and lock records are skipped. If value materialization is requested and the write has no short value, the default CF value is loaded by start_ts.

## State and Persistence Behavior
The detector is read-only over a snapshot. It advances a single iterator and marks itself invalid after the first error so streaming stops cleanly. Responses carry either pairs or a key error.

## Dependencies and Integration Points
Uses engine traits `CF_WRITE`, `CF_DEFAULT`, MVCC `Key`, `TimeStamp`, `WriteRef`, `WriteType`, TiKV snapshots, and importer protobufs. `ImportSstService::duplicate_detect` wraps it in a server-streaming RPC after obtaining an async snapshot.

## Risks and Edge Cases
It treats unexpected delete/rollback/lock as errors when the first import-version record above `min_commit_ts` is not a put. Missing default-CF value for a long value is a hard RocksDB error. Error conversion includes a typo in "unkown" and maps many kv errors to a generic RocksDB message. Correctness depends on MVCC key ordering and commit-ts semantics.

## Test Signals
Tests cover base duplicate detection, incremental `min_commit_ts` behavior, rollback/delete handling, long values, and expected ordering. They use transactional test storage and compare emitted batches. Key-only mode and iterator `next` error responses are less directly covered.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/import/duplicate_detect.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/import/ingest.rs -->
# sources/storage-engines/tikv/src/import/ingest.rs

## Purpose
Contains shared ingest orchestration for SST import RPCs: request suspension, conflict latching, write-stall admission, snapshot/term acquisition, file existence checks, and raft-backed ingest writes.

## Important APIs, Types, and Functions
`IngestLatch` serializes in-flight SST ingestion per `(cf_name, path)`. `SuspendDeadline` uses an `AtomicU64` physical timestamp to reject import requests temporarily. `check_write_stall` detects region/tablet availability and write-CF ingest slowdown. `async_snapshot` obtains an engine snapshot and converts storage errors to region protobuf errors. `ingest_files_impl` validates API version, obtains snapshot term, checks SST files exist, and sends `Modify::Ingest` writes. Public `ingest` performs suspension/admission/latch logic then delegates.

## Control Flow
`ingest` first rejects if suspended. Under `ingest_admission_guard`, it checks write stall and attempts to acquire all SST latches. Partial latch acquisition is rolled back and returns file conflict. `ingest_files_impl` checks importer API version, awaits raft snapshot, verifies local SST files after snapshot to avoid retry races, sets the request term from snapshot extension, and issues `engine.async_write`; `wait_write` maps the write stream result to a response error if needed. Latches are released after the async ingest attempt.

## State and Persistence Behavior
`IngestLatch` and `SuspendDeadline` are in-memory service state. Successful ingestion persists SST contents through raft/engine `Modify::Ingest`. The importer controls file existence and API-version metadata. Metrics are incremented through `pb_error_inc` and importer error counters.

## Dependencies and Integration Points
Depends on `SstImporter`, raftstore v2 `StoreMeta`, local tablets, TiKV engine async snapshot/write APIs, importer protobufs, and `raft_writer::wait_write`. Called by both single-file `ingest` and `multi_ingest` RPC handlers in `sst_service.rs`.

## Risks and Edge Cases
Latch release must happen after all paths, and this file handles that manually after await. Write-stall rejection differs between raftstore v1 and v2/import mode. File existence after snapshot intentionally returns stale command to make retries safe, but can confuse clients if files are externally removed. `acquire_lock(meta).unwrap_or(false)` suppresses path conversion errors into conflict-like behavior.

## Test Signals
No direct tests in this file. Behavior is exercised indirectly by import service integration tests elsewhere and by raft writer tests for `wait_write`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/import/ingest.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/import/mod.rs -->
# sources/storage-engines/tikv/src/import/mod.rs

## Purpose
Defines the import module boundary for TiDB Lightning/BR SST import support and common RPC error/metric helpers.

## Important APIs, Types, and Functions
Declares internal modules `duplicate_detect`, `ingest`, `raft_writer`, and `sst_service`. Re-exports `sst_importer::{Config, Error, Result, SstImporter, TxnSstWriter}` and `ImportSstService`. `make_rpc_error` converts debug-printable errors into gRPC unknown statuses. `send_rpc_response!` records RPC duration, increments error metrics, and sends success/failure to a sink. `pb_error_inc` classifies `errorpb::Error` variants into importer metric labels.

## Control Flow
RPC handlers use `send_rpc_response!` to normalize response sending and duration recording. Store-region errors are classified by `pb_error_inc` for metrics. There is no service control flow here beyond helper macro expansion.

## State and Persistence Behavior
No local persistent state. Metrics are updated through `IMPORT_RPC_DURATION` and `IMPORTER_ERROR_VEC`.

## Dependencies and Integration Points
Integrates gRPC (`grpcio`), kvproto region errors, sst importer metrics/types, and the concrete `ImportSstService`. This is the public import facade for the crate.

## Risks and Edge Cases
`make_rpc_error` uses debug formatting and always maps to UNKNOWN, which can be unfriendly to clients. Macro users must pass consistent label/timer variables. `pb_error_inc` has a fixed classification list; new region error variants fall into `unknown` until updated.

## Test Signals
No direct tests. Metric classification and macro behavior are covered only through RPC paths that invoke them.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/import/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/import/raft_writer.rs -->
# sources/storage-engines/tikv/src/import/raft_writer.rs

## Purpose
Provides asynchronous raft/engine write helpers for import apply paths, including per-region concurrency throttling when writing through thread-local engines.

## Important APIs, Types, and Functions
`wait_write` awaits the first `WriteEvent` from an async write stream and returns success only for `Finished(Ok(()))`. `ThrottledTlsEngineWriter` owns a shared `Inner` map from region id to semaphores and exposes unsafe `write<E>`, `try_gc`, and test inspection helpers. `MAX_CONCURRENCY_PER_REGION` defaults to 16.

## Control Flow
`write` records queue time, creates or reuses a region semaphore, waits for a permit, obtains the thread-local engine through `with_tls_engine`, calls `engine.async_write`, waits for completion, records apply duration and bytes, and releases the permit by dropping it. `try_gc` removes semaphore entries whose strong count shows no in-flight writer references.

## State and Persistence Behavior
The writer stores only throttle state in memory. Persistent effects are the engine writes performed by `WriteData`. It assumes the runtime worker threads have registered an engine in TLS.

## Dependencies and Integration Points
Depends on `tikv_kv::Engine`, `WriteData`, `WriteEvent`, `with_tls_engine`, tokio semaphores, importer metrics, and storage errors. `ImportSstService::do_apply` uses it to apply downloaded KV files with bounded region-level concurrency.

## Risks and Edge Cases
`write` is unsafe because the caller must guarantee the TLS engine has type `E` or compatible layout. `wait_write` treats progress events before `Finished` as unexpected errors, so async write streams used here must emit only the expected terminal event. Semaphore maps can grow by region until periodic GC runs. If a semaphore is closed, writes fail with a boxed error.

## Test Signals
Tests compare applied engine state to a mirror engine, verify per-region concurrency throttling under failpoints, and verify GC removes idle region workers. Coverage strongly targets throttling correctness and TLS-engine apply behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/import/raft_writer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/import/sst_service.rs -->
# sources/storage-engines/tikv/src/import/sst_service.rs

## Purpose
Implements the gRPC `ImportSst` service that powers TiDB Lightning/BR physical import: upload/download/apply/ingest SST or KV files, compact ranges, detect duplicates, suspend imports, and manage force-partition ranges.

## Important APIs, Types, and Functions
`ImportSstService<E>` stores config manager, local tablets, engine, resizable import runtime, `SstImporter`, download limiter, ingest latches, raft-entry limits, region info accessor, throttled raft writer, optional raftstore-v2 store meta/resource manager, suspend deadline, memory limit, and force partition range manager. `RequestCollector` batches `Modify` operations into `WriteData` while deduplicating write-CF keys by latest commit ts and default-CF exact encoded keys. Helper functions include `check_import_resources`, `transfer_error`, `convert_join_error`, `check_local_region_stale`, `prepare_write`, and `download_request_dispatcher`. The `impl_write!` macro implements streaming transactional and raw write RPCs.

## Control Flow
`new` builds a runtime with TLS engine hooks, starts importer mode checks, writer GC, config tick, and adjusts worker count. Upload streams require a meta first chunk, create an importer file, resource-check, append data chunks, then finish. Download variants validate request shape, resource-check, locate tablet, build encryption/resource limiting options, and call importer download functions. Apply downloads KV files, rewrites them, feeds `RequestCollector`, drains batches through `ThrottledTlsEngineWriter`, and joins in-flight write tasks. Ingest/multi-ingest delegate to `ingest.rs`. Duplicate detect obtains a snapshot then streams detector responses. Switch mode handles singleton RocksDB config changes or range-scoped v2 import-mode markers. Force partition add/remove updates manager state and add triggers targeted compactions around range boundaries.

## State and Persistence Behavior
The service owns long-lived runtime/config/importer/throttle/suspend/latch state. Persistent effects include uploaded local files, downloaded/re-written SST files, raft-applied KV writes, ingested SST files, compactions, mode/range markers in importer state, and force-partition ranges with TTL. Metrics record RPC counts/durations, upload chunks, apply/download queueing, errors, and RocksDB config gauges.

## Dependencies and Integration Points
Integrates `grpcio`, kvproto `import_sstpb`, local tablets, raftstore region access, raftstore-v2 store meta, resource control, encryption metadata, external storage through `sst_importer`, RocksDB compaction traits, and TiKV storage error translation. It is the central service boundary for physical import clients.

## Risks and Edge Cases
Resource gating rejects on abnormal disk status or high memory pressure after a jittered sleep to avoid retry storms. `RequestCollector` must prevent duplicated write-CF keys in a raft request because resolved-ts observer can panic; it sets `avoid_batch` UUID behavior. Apply chunks are split at half the raft-entry size with extra wire-size accounting, but huge individual modifies can still produce larger single requests by design for liveness. `prepare_write` filters non-put/delete write records and tags Lightning physical import writes for CDC ignore behavior. Several RPCs spawn background tasks, so cancellation semantics depend on stream/task behavior. Batch download validation is strict about region/epoch/cf/end-key consistency, with special allowance for write+default mix only on latest-MVCC path. `duplicate_detect` unwraps `DuplicateDetector::new`, so construction errors could panic in the task.

## Test Signals
Unit tests cover `RequestCollector` dedup/filter/batching behavior, raft request size limits, huge-write liveness, write/default CF semantics, and `check_local_region_stale` epoch cases. Other behavior is covered indirectly in importer/integration tests. Direct gaps include resource-pressure paths, suspend RPC bounds, download variants, force partition compaction side effects, and duplicate detector construction failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/import/sst_service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/lib.rs -->
# sources/storage-engines/tikv/src/lib.rs

## Purpose
Crate root for the TiKV server library in this source tree. It defines crate-level docs, feature gates, macro imports, public modules, and version logging helpers.

## Important APIs, Types, and Functions
Public modules are `config`, `coprocessor`, `coprocessor_v2`, `import`, `read_pool`, `server`, and `storage`. `tikv_version_info` returns a formatted multiline version string using Cargo/build environment variables plus optional build time. `tikv_build_version` returns `CARGO_PKG_VERSION`. `log_tikv_info` logs a welcome message and each nonempty line of version info.

## Control Flow
At runtime, only the helper functions execute. Version info pulls compile-time env vars with fallbacks, trims feature text, and logs line by line. The rest is compile-time crate setup and module exposure.

## State and Persistence Behavior
No mutable state is stored here. Version helpers expose build metadata embedded at compile time and write to TiKV logs.

## Dependencies and Integration Points
Imports macros from `fail`, `serde_derive`, `more_asserts`, and `tikv_util`; enables several nightly Rust features. Public modules expose the researched coprocessor and import subsystems.

## Risks and Edge Cases
The crate depends on nightly features including `min_specialization`, `deadline_api`, and `type_alias_impl_trait`; compiler upgrades can affect build stability. Missing build env vars produce explicit fallback strings. Module visibility changes here have crate-wide API impact.

## Test Signals
No direct tests in this file. Version functions are simple but could be smoke-tested by asserting package version and fallback formatting. Most coverage comes from public child modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/lib.rs -->
