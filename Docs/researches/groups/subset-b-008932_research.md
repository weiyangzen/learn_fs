# Research: subset-b-008932

Grouped research for the TiKV server status, tablet snapshot, TTL, storage configuration, storage error, test engine, and lock wait context files in subset B. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/status_server/mod.rs -->
# sources/storage-engines/tikv/src/server/status_server/mod.rs

## Purpose

This module implements TiKV's HTTP status server. It exposes operational endpoints for metrics, readiness, configuration inspection and online update, profiling, log level changes, region metadata, resource groups, gRPC pause/resume, in-memory-engine inspection, async task traces, failpoints in failpoint builds, and forced partition ranges. It is also responsible for optional TLS wrapping and certificate common-name authorization on sensitive endpoints.

## Important APIs, Types, And Functions

`StatusServer<R>` owns the status runtime, shutdown channel, bound address, `ConfigController`, raft router, `SecurityConfig`, optional `ResourceGroupManager`, `GrpcServiceManager`, optional `RegionCacheMemoryEngine`, and `ForcePartitionRangeManager`. `new` builds a dedicated Tokio runtime with status-server thread naming and system hooks. `start` binds `AddrIncoming`, records the real local address, conditionally wraps incoming sockets with TLS, and calls `start_serve`. `stop` signals graceful shutdown and waits up to three seconds for the runtime.

Endpoint helpers include `get_config`, `update_config`, `update_config_from_toml_file`, `get_engine_type`, `change_log_level`, `metrics_to_resp`, `handle_ready_request`, `dump_heap_prof_to_resp`, `dump_cpu_prof_to_resp`, `get_cmdline`, `get_symbol_count`, `get_symbol`, `dump_region_meta`, `handle_get_all_resource_groups`, `handle_dumple_cached_regions`, `dump_async_trace`, and force partition range add/remove/dump helpers. `decode_json` converts flat JSON objects into string-valued config changes and rejects arrays or non-object roots. `make_response` centralizes status/body construction.

TLS support is split through `ServerConnection`, `check_cert`, `tls_acceptor`, `tls_incoming`, and `TlsIncoming<S>`. The TLS accept loop reloads certificate context when SSL creation or handshake errors suggest the underlying files may have changed.

## Control Flow

`start_serve` captures the shared server dependencies, builds a Hyper `make_service_fn`, and handles every request in a `service_fn`. The handler records method and path, optionally handles failpoint routes first, decides whether certificate authorization is needed, dispatches on `(method, path)`, and records request duration using a normalized path label of `unknown` for misses. Most handlers return `hyper::Result<Response<Body>>` and convert domain errors into HTTP status codes and text bodies.

Configuration flow is `POST /config` -> collect body -> `decode_json` -> `ConfigController::update` or `update_without_persist` based on the `persist` query parameter. `PUT /config/reload` asks the controller to reload from the TOML file and intentionally tolerates non-online items according to the hosting-platform comment.

Profiling flow is `GET /debug/pprof/heap` -> heap profile temp file -> optional `jeprof` SVG transform. CPU profiling parses `seconds` and `frequency`, detects protobuf output by content type, waits through `GLOBAL_TIMER_HANDLE.delay`, and delegates single-profile enforcement and report generation to `profile.rs`.

Region and debug endpoints bridge to runtime subsystems: `dump_region_meta` asks the raft extension router for region metadata and serializes it as JSON; resource groups are flattened into debug settings; cached in-memory regions are collected from `RegionCacheMemoryEngine` under a read lock and sorted by range.

## State And Persistence Behavior

The server stores only runtime state: its Tokio runtime, optional shutdown receiver, bound address, and cloned handles to other subsystems. Persistent changes happen through `ConfigController::update` when `persist=true`; with `persist=false`, changes are applied in memory only. `update_config_from_toml_file` reads the configured TOML source. Force partition ranges mutate `ForcePartitionRangeManager` with a fixed TTL of 3600 seconds. TLS certificate state includes a local `cert_last_modified_time` used to decide whether to reload the `SslContext`.

## Dependencies And Integration Points

The module integrates Hyper/Tokio for HTTP serving, OpenSSL/tokio-openssl for TLS, Prometheus dumping, TiKV config management, raftstore metadata querying through `RaftExtension`, resource control, service-manager gRPC controls, in-memory region cache, failpoints, active async tracing, and TiKV security common-name matching. Metrics are emitted through `STATUS_REQUEST_DURATION`; readiness is sourced from `GLOBAL_SERVER_READINESS`.

## Risks And Edge Cases

Sensitive endpoints are protected only when TLS certificate common-name allowlists are configured; `/metrics`, `/status`, `/config` GET, and CPU profile GET bypass certificate checks by design. `decode_json` accepts only flat scalar JSON values, so nested online config updates are impossible through this path unless represented as dotted keys. `get_symbol` accepts arbitrary posted addresses and resolves them in-process, which is operationally useful but sensitive. TLS reload occurs only after handshake/setup errors, not proactively. Force partition range errors include misspelled messages and always add ranges with 3600-second TTL. Unknown paths are collapsed for metrics cardinality, but real route labels for dynamic `/region/<id>` are not normalized before the route match unless unknown.

## Test Signals

The module has broad unit/integration tests: status and metrics endpoints, config get/update with persist and non-persist modes, failpoint endpoints with and without the feature, TLS common-name authorization, heap and CPU profiling, pprof symbol resolution, gzip metrics, log-level update, engine type reporting, gRPC pause/resume error behavior with dummy manager, readiness verbose JSON, and in-memory-engine cached-region dumping.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/status_server/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/status_server/profile.rs -->
# sources/storage-engines/tikv/src/server/status_server/profile.rs

## Purpose

This module backs the status server's profiling endpoints. It creates one-shot heap profiles, runs bounded CPU profiles, normalizes thread names in pprof output, reads generated files, and optionally converts heap profiles to SVG through an embedded `jeprof` script.

## Important APIs, Types, And Functions

`dump_one_heap_profile` creates a `NamedTempFile` and calls `tikv_alloc::dump_prof` or the test stub. `start_one_cpu_profile` enforces at most one concurrent CPU profile through `CPU_PROFILE_ACTIVE`, starts a `pprof::ProfilerGuard`, waits for a caller-supplied future, then emits either protobuf or flamegraph SVG bytes. `ProfileRunner<I, T>` is a generic future wrapper that pairs `on_start`, an async end condition, and `on_end` cleanup/report generation. `read_file` reads a path into bytes, and `jeprof_heap_profile` spawns Perl with embedded `jeprof.in` and the current TiKV executable. `extract_thread_name` strips numeric suffixes and normalizes spaces/underscores to dashes.

## Control Flow

CPU profiling starts by checking the global mutex-protected active flag. The profile guard is constructed with frequency and a blocklist for common system libraries. When the end future resolves, `on_end` clears the active flag through `defer!`, builds the pprof report with a frames post-processor, and serializes the selected format. If the end future fails, that error wins over report generation. Heap profiling is simpler: create temp file, dump allocator profile, return the file for the HTTP layer to read or post-process.

## State And Persistence Behavior

The only durable side effect is temporary profile file creation; the `NamedTempFile` lifetime controls cleanup. CPU profile concurrency is process-global state in `CPU_PROFILE_ACTIVE`. `jeprof_heap_profile` runs a child process and captures stdout/stderr without persisting the SVG itself.

## Dependencies And Integration Points

The module depends on `pprof`, protobuf encoding through `pprof::protos::Message`, `tikv_alloc`, `tempfile`, regex normalization, and `tikv_util::defer`. It is consumed by `status_server/mod.rs` for `/debug/pprof/heap` and `/debug/pprof/profile`.

## Risks And Edge Cases

Only one CPU profile can run process-wide; concurrent requests return `Already in CPU Profiling`. The active flag is cleared only after `on_end`, so panics in that path would risk wedging profiling. `jeprof_heap_profile` assumes Perl can run and that the embedded script accepts `/dev/stdin`; this may be environment-sensitive. Thread name normalization is regex based and can leave unfamiliar names unchanged.

## Test Signals

Tests validate thread-name extraction for common TiKV thread prefixes and verify that a second CPU profile request is rejected while the first is active. The heap dump function is stubbed in tests to avoid requiring heap profiling support.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/status_server/profile.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/tablet_snap.rs -->
# sources/storage-engines/tikv/src/server/tablet_snap.rs

## Purpose

This module implements sending and receiving tablet snapshots for raftstore v2. Unlike older snapshot transfer that creates new files, tablet snapshots transfer engine data in its original file form and can reuse receiver-side cached SST files by comparing previews. It also enforces transfer rate limiting, handles encrypted file metadata, integrates with raftstore snapshot managers, and provides the worker runner for snapshot send/receive tasks.

## Important APIs, Types, And Functions

Constants define the protocol sizes: `PREVIEW_CHUNK_LEN` is 1 KiB, `PREVIEW_BATCH_SIZE` is 256, `FILE_CHUNK_LEN` is 1 MiB, and `USE_CACHE_THRESHOLD` is 4 MiB. `EncryptedFile` abstracts plain or decrypted file reads. `SnapCacheBuilder` lets a tablet registry build a checkpointer cache for a region; `NoSnapshotCache` disables it.

`RecvTabletSnapContext` parses the first stream message, derives `TabletSnapKey`, extracts IO type from raft snapshot data, and holds the receiving guard that prevents duplicate receives. `recv_snap_imp` implements the receive protocol; `recv_snap` wraps it in gRPC sink success/failure behavior and feeds the raft router on success. `cleanup_cache`, `is_sst_match_preview`, `accept_one_file`, and `accept_missing` handle receiver-side cache validation, file writes, checksums, and encryption key import.

On the sender side, `build_one_preview`, `find_missing`, `send_missing`, and `send_snap` implement the preview, missing-file negotiation, chunk streaming, checksum trailer, and final receiver acknowledgement. `TabletRunner<B, R>` is the `Runnable` task processor for raftstore snapshot tasks. `copy_tablet_snapshot` is a test/export helper that copies tablet snapshot files locally while preserving encryption metadata.

## Control Flow

The protocol begins with a head message containing the raft snapshot message. If sender-side SST bytes exceed the cache threshold, the sender sets `use_cache`, streams preview metadata for SST files, and waits for the receiver's missing-file list. The receiver optionally builds a cache checkpoint for the region, scans existing files, validates SST candidates by size, leading bytes, and trailing bytes, deletes stale/unmatched files, and returns the missing names. The sender streams missing SSTs plus all non-SST files in file chunks, accumulating a CRC64 digest over file names and data. It then sends an explicit end message containing the checksum, closes its sink, and waits for the receiver to close.

The receiver writes chunks into a temporary receive directory using `create_new`, validates per-file sizes, syncs each file, commits encryption metadata if present, validates the final checksum, syncs the directory, and atomically renames the temp directory to the final receive path. `RecvTabletSnapContext::finish` feeds the saved raft message into the raft router after files are persisted.

`TabletRunner::run` rejects old v1 receive tasks, bounds concurrent tablet receives and sends with counters from `TabletSnapManager`, constructs gRPC clients with current snapshot config, spawns async send/receive jobs on its internal runtime, refreshes rate-limit config on config events, and calls task callbacks with success or error.

## State And Persistence Behavior

Snapshot receive state is represented by a temporary directory and a final receive directory under `TabletSnapManager`, plus receiving/sending atomic counters. Successful receive persists snapshot files through `fs::rename`; encryption key metadata is linked before rename and cleaned after success or rename failure. Sender completion calls `finish_snapshot` through a deferred context and deletes the generated snapshot after a successful send. IO type is set with `WithIoType` so underlying filesystem accounting sees replication or load-balance work.

## Dependencies And Integration Points

This file integrates `kvproto` tablet snapshot messages, `grpcio` duplex streaming, raftstore `TabletSnapManager` and `SnapManager`, engine checkpointers through `TabletRegistry`, encryption key managers/importers, TiKV limiter and config tracker, gRPC security manager, snapshot metrics, and raft router feeding through `RaftExtension`. It consumes server `Config` fields such as concurrent snapshot limits, gRPC stream windows, keepalive, compression, and `snap_io_max_bytes_per_sec`.

## Risks And Edge Cases

The protocol is strict: unexpected message variants, chunks with repeated file names after the first chunk, size overrun, checksum mismatch, nonempty stream after end, and duplicate final paths all abort the stream. Cache reuse relies on first and last 1 KiB previews, so it is an optimization guard rather than a cryptographic identity check. Receiver-side temp directory cleanup deletes existing temp paths and encryption metadata. Encryption mismatch is fatal if a chunk carries a key but receiver encryption is disabled. `find_missing` has a TODO about Titan files and currently classifies only normal files and `.sst` names. Counters must be decremented in all async completion paths to avoid blocking future snapshot work.

## Test Signals

The visible file includes the local `copy_tablet_snapshot` helper for test/export builds. Runtime test hooks and failpoints include receive network error and finish-receiving snapshot. The task runner's validation callback path exposes current config for tests. Protocol invariants are encoded as explicit errors, which provides strong failure signals even when full integration tests live elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/tablet_snap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/transport.rs -->
# sources/storage-engines/tikv/src/server/transport.rs

## Purpose

This module adapts TiKV's `RaftClient` to raftstore's `Transport` trait so raftstore can send raft messages without depending directly on the server raft client implementation.

## Important APIs, Types, And Functions

`ServerTransport<T, S>` wraps `RaftClient<S, T>`, where `T: RaftExtension` and `S: StoreAddrResolver`. `new` constructs the wrapper, `Clone` delegates to the underlying client clone, and the `Transport` implementation exposes `send`, `set_store_allowlist`, `need_flush`, and `flush`.

## Control Flow

`send` forwards a `RaftMessage` to `raft_client.send`. Success is returned unchanged; failure reason is wrapped as `raftstore::Error::Transport`. Allowlist and flushing methods are direct pass-throughs.

## State And Persistence Behavior

The wrapper owns no persistent state beyond the cloned raft client. Any batching, connection state, allowlist state, or pending messages live in `RaftClient`.

## Dependencies And Integration Points

This is the integration boundary between `crate::server::raft_client`, store address resolution, `tikv_kv::RaftExtension`, and raftstore's transport abstraction.

## Risks And Edge Cases

The module intentionally hides raft-client-specific errors behind raftstore transport errors, so downstream code receives less structured detail. Flush semantics depend entirely on `RaftClient::need_flush` and `flush`; this adapter adds no additional synchronization.

## Test Signals

No local tests are present. Coverage is expected through raftstore/server integration tests that exercise raft message delivery, allowlists, and flush behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/transport.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/ttl/mod.rs -->
# sources/storage-engines/tikv/src/server/ttl/mod.rs

## Purpose

This is the TTL server module facade. It declares the TTL checker and TTL compaction filter submodules and re-exports the public types used by the wider server and storage configuration code.

## Important APIs, Types, And Functions

Exports are `TtlCheckerTask`, `TtlChecker`, `check_ttl_and_compact_files`, and `TtlCompactionFilterFactory`. There is no local logic beyond module wiring.

## Control Flow

Consumers import through `server::ttl` instead of depending on the submodule paths. The config manager uses `TtlCheckerTask`; RocksDB setup can use `TtlCompactionFilterFactory`.

## State And Persistence Behavior

No state is stored in this module.

## Dependencies And Integration Points

This facade integrates `ttl_checker.rs` and `ttl_compaction_filter.rs` with server-level module naming.

## Risks And Edge Cases

The only risk is API surface drift: changes to submodule exports must be reflected here or downstream imports will break.

## Test Signals

No local tests are present; behavior is covered through the re-exported modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/ttl/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/ttl/ttl_checker.rs -->
# sources/storage-engines/tikv/src/server/ttl/ttl_checker.rs

## Purpose

This module implements a timer-driven worker that scans region ranges for SST TTL properties and manually compacts fully expired files in the default column family. It also supports online updates to the scan interval.

## Important APIs, Types, And Functions

`Task::UpdatePollInterval(Duration)` is the worker control message. `TtlChecker<E, R>` holds a `KvEngine`, a `RegionInfoProvider`, and the current poll interval. `Runnable::run` updates the interval and the interval gauge. `RunnableWithTimer::on_timeout` performs a complete region scan round. `check_ttl_and_compact_files` reads TTL properties for a range and compacts expired files one at a time.

## Control Flow

`on_timeout` starts at an empty key and repeatedly calls `region_info_provider.seek_region` with a callback that scans up to 10 regions, reports start/end keys through an `mpsc` channel, and increments processed-region metrics. For each returned range, it converts region keys to data keys and calls `check_ttl_and_compact_files` with `exclude_l0=true`. It continues from the previous end key until an empty end key or no regions remain, then increments the finish metric, sleeps 40 seconds to let metrics be scraped, and resets the processed-region gauge.

`check_ttl_and_compact_files` gets range TTL properties from the engine. Empty properties count as `empty`; no expired files count as `skip`; expired files are compacted with `compact_files_cf(CF_DEFAULT, vec![file], None, 0, exclude_l0)`, with a two-second sleep between files.

## State And Persistence Behavior

The checker keeps only poll interval and cloned engine/provider handles. Persistent effects are RocksDB compactions that remove expired RawKV data and rewrite SST state. Metrics track interval, processed regions, action classes, and compaction duration.

## Dependencies And Integration Points

It depends on engine TTL properties and manual compaction APIs, raftstore `RegionInfoProvider`, TiKV worker traits, `UnixSecs`, and server TTL metrics. `StorageConfigManger` schedules `UpdatePollInterval` when online config changes.

## Risks And Edge Cases

Errors from `seek_region`, receiving from the callback channel, TTL property reads, and compaction are logged and counted, but the checker continues scanning where possible. `seek_region` callback communication is synchronous through a channel; if callback behavior changes, deadlock risk should be considered. The 40-second metrics sleep blocks the worker thread after each round. Expiration decisions use file-level max expire timestamp, so files with any unexpired entries are skipped.

## Test Signals

No local tests are present in this file. Test signals are mainly metrics and integration behavior through engines that expose TTL properties and compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/ttl/ttl_checker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/ttl/ttl_compaction_filter.rs -->
# sources/storage-engines/tikv/src/server/ttl/ttl_compaction_filter.rs

## Purpose

This module defines a RocksDB compaction filter factory and filter for removing expired RawKV entries during compaction.

## Important APIs, Types, And Functions

`TtlCompactionFilterFactory<F: KvFormat>` implements RocksDB's `CompactionFilterFactory`. It inspects input table TTL properties and creates a `TtlCompactionFilter<F>` only when at least one input table may contain expired entries. `TtlCompactionFilter<F>` stores the current timestamp and accumulated expired count/size. Its `featured_filter` decides whether each key/value should be kept or removed. Drop updates Prometheus counters in batches.

## Control Flow

Factory creation reads `RocksTtlProperties` from input table user-collected properties and computes `min_expire_ts`. If all table min-expire timestamps are in the future, no filter is installed. Otherwise a filter named `ttl_compaction_filter` is returned. During compaction, the filter ignores non-value records, non-data keys, and non-raw key modes. It decodes raw values; expired values with `expire_ts <= self.ts` are removed and counted, decode errors are logged and counted as `ts_error`, and all other values are kept.

## State And Persistence Behavior

The filter removes expired entries from RocksDB output during compaction. Per-filter counters are local until `Drop`, then increment global `TTL_EXPIRE_KV_SIZE_COUNTER` and `TTL_EXPIRE_KV_COUNT_COUNTER`. It records `ts` once at filter creation, so a long compaction uses a stable expiration cutoff.

## Dependencies And Integration Points

It integrates RocksDB raw compaction filter traits, TiKV API version key/value decoding through `KvFormat`, `keys::DATA_PREFIX_KEY`, raw TTL timestamp helpers, Rocks TTL table properties, and TTL checker action metrics.

## Risks And Edge Cases

The factory skips filter creation based on table-level min expiration. Incorrect or absent TTL properties can delay cleanup. Decode errors keep the value to avoid data loss but emit error metrics and logs. Only raw-mode data keys are affected, so transactional or metadata keys are protected by key-mode checks.

## Test Signals

No local tests are present. Expected coverage comes from RocksDB compaction filter integration and RawKV TTL tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/ttl/ttl_compaction_filter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/config.rs -->
# sources/storage-engines/tikv/src/storage/config.rs

## Purpose

This module defines TiKV storage configuration, defaults, validation, API-version interpretation, flow-control settings, shared block-cache construction, IO-rate-limit construction, and max-ts safety settings.

## Important APIs, Types, And Functions

`EngineType` selects `RaftKv` or `RaftKv2` with a serde alias for `partitioned-raft-kv`. `Config` is an `OnlineConfig` structure containing data path, engine type, scheduler sizing, pending write and memory quotas, reserve space, async prewrite, API version and TTL flags, TTL polling, transaction status cache capacity, flow control, block cache, IO rate limit, background recovery window, and max-ts config.

`Config::validate_engine_type` canonicalizes data paths and resolves engine type from existing data directories. `Config::validate` clamps scheduler concurrency, validates API/TTL combinations, worker pool size, IO rate-limit mode, memory quota, and max-ts settings. `api_version` maps numeric config and TTL flag into `kvproto::kvrpcpb::ApiVersion`; `set_api_version` performs the reverse.

`FlowControlConfig::write_into_metrics` exports flow-control settings. `BlockCacheConfig::build_shared_cache` creates an LRU cache with adjusted shard bits, priority pool ratios, strict-capacity flag, and optional jemalloc nodump allocator. `IoRateLimitConfig::build` creates an `IoRateLimiter` and sets priorities for all IO types. `MaxTsConfig::validate` checks drift/cache-sync relation and invalid-update action.

## Control Flow

Default config derives scheduler worker pool size from CPU quota, using 8 workers for at least 16 cores and otherwise clamping between 1 and 4. Validation first resolves engine type against existing RocksDB or tablet data directories to avoid starting with an incompatible engine. It then checks scheduler, API, IO, memory, and max-ts invariants, mutating some values to safe bounds with warnings.

Block cache construction computes capacity from configured size or fallback, reduces shard bits when capacity cannot support the default shard count, attaches an allocator when requested and available, and creates a shared Rocks cache. IO rate-limit construction sets a global rate and all priority classes, while validation rejects unsupported modes and corrects unsafe `Other` and GC priorities.

## State And Persistence Behavior

This file defines configuration data, not runtime persistence. Validation mutates the in-memory config before use. Config persistence is handled by `ConfigController` outside this file. Built caches and IO limiters become runtime resources owned by database/server setup.

## Dependencies And Integration Points

It integrates `online_config`, RocksDB cache/resource options, filesystem IO limiter types, protobuf API version, global TiKV defaults for RocksDB/tablet subdirectories, CPU quota detection, and server flow-control metrics. `storage/config_manager.rs` applies the online portions to live components.

## Risks And Edge Cases

Existing data directories override configured engine type; if both v1 and v2 data directories exist, validation fails. API V2 requires TTL enabled. `scheduler_worker_pool_size` has a dynamic upper bound based on CPU quota. Block cache fallback exists for tests when TiKV config was not validated. Unsupported memory allocator names only warn and fall back. `MaxTsConfig` rejects a max drift less than or equal to cache sync interval to avoid stale max-ts decisions.

## Test Signals

Tests cover storage config validation, engine type resolution from existing data directories including the conflict case, and block-cache shard-bit adjustment across capacities.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/config_manager.rs -->
# sources/storage-engines/tikv/src/storage/config_manager.rs

## Purpose

This module applies online storage configuration changes to live TiKV components: RocksDB/shared block cache, TTL checker worker, flow controller, transaction scheduler, IO rate limiter, and concurrency manager max-ts behavior.

## Important APIs, Types, And Functions

`StorageConfigManger<E, K, L>` stores a configurable database handle, TTL checker scheduler, flow controller, transaction scheduler, and concurrency manager. `new` wires those dependencies. The `ConfigManager` implementation provides `dispatch`, which consumes a `ConfigChange` and applies recognized changes.

## Control Flow

`dispatch` checks for known changes in priority order. For `block_cache.capacity`, it sets shared block cache capacity and updates the RocksDB CF metric. For `ttl_check_poll_interval`, it schedules `TtlCheckerTask::UpdatePollInterval`. For `flow_control`, it updates the flow controller config, toggles RocksDB `disable_write_stall` on all CFs when `enable` changes, and enables/disables the controller. For `scheduler_worker_pool_size`, it scales the scheduler pool. For `memory_quota`, it updates scheduler memory capacity. For `io_rate_limit`, it fetches the global limiter, applies max bytes per second, and iterates all `IoType` values to apply changed priorities. For `max_ts`, it updates invalid max-ts action and drift allowance in the concurrency manager.

## State And Persistence Behavior

All effects are in-memory runtime changes. Persistence of config files is handled before or around this manager by the online config controller. Some changes mutate external shared state immediately, including RocksDB options, scheduler pools, limiter settings, and concurrency-manager policy.

## Dependencies And Integration Points

The manager bridges `online_config`, TiKV `ConfigurableDb`, engine traits, filesystem global IO limiter, TTL worker scheduling, transaction scheduler, lock manager type parameters, flow controller, and concurrency manager. It relies on `ALL_CFS` and `CF_DEFAULT` for RocksDB CF updates and metrics.

## Risks And Edge Cases

The manager uses an `else if` chain for several top-level modules, so only the first matching branch among block cache, TTL interval, flow control, scheduler pool size, and memory quota is applied in that chain for a single `dispatch` call. IO rate limit and max-ts are handled afterward independently. Several runtime update calls use `unwrap`, so scheduling failure or CF config failure can panic. Missing global IO limiter returns an error. Priority conversion can fail and propagate.

## Test Signals

No local tests are present. Coverage should come from online config tests that update storage fields and assert side effects on scheduler, flow controller, IO limiter, and RocksDB options.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/config_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/errors.rs -->
# sources/storage-engines/tikv/src/storage/errors.rs

## Purpose

This module centralizes storage-layer error representation and conversion to TiKV client-facing protobuf errors, error codes, metrics tags, and shared error handles.

## Important APIs, Types, And Functions

`ErrorInner` enumerates storage errors, wrapping KV, transaction, engine, IO, closed, busy, key-size, CF, TTL, deadline, API-version, and key-mode cases. `Error` is a boxed wrapper around `ErrorInner` with broad `From` conversions. `ErrorCodeExt` maps storage errors to structured TiKV error codes. `ErrorHeaderKind` classifies region-header protobuf errors and provides metric strings.

Conversion helpers include `get_error_kind_from_header`, `get_tag_from_header`, `extract_region_error_from_error`, `extract_region_error`, `extract_committed`, `extract_key_error`, `extract_kv_pairs`, `map_kv_pairs`, `map_kv_pair_entries`, and `extract_key_errors`. `SharedError` wraps `Arc<Error>` for sharing non-cloneable errors and can be converted back to owned `Error` only when uniquely referenced.

## Control Flow

Region error extraction pattern-matches nested storage/KV/transaction/MVCC errors to recover raftstore request headers, max timestamp not synced, flashback not prepared, invalid max-ts update, scheduler busy, GC busy, closed, and deadline exceeded cases. Key error extraction maps lock, conflict, already-exist, lock-not-found, transaction-not-found, deadlock, commit-ts-expired, commit-ts-too-large, assertion failed, and primary mismatch errors into `kvrpcpb::KeyError`; unknown cases become abort strings.

MVCC debug info for selected key errors is attached by `add_debug_mvcc_for_key_error`, which removes default-CF values before embedding to reduce response size. Pair mapping functions convert nested per-key `Result` values into protobuf pairs with per-entry errors where needed.

## State And Persistence Behavior

There is no persisted state. The module constructs protobuf error values and shared error wrappers. `SharedError` uses reference counting to allow one error to be passed to multiple waiters or responses.

## Dependencies And Integration Points

This file integrates error-code definitions, `kvproto` error and kvrpc protobufs, storage KV/MVCC/transaction errors, deadline utilities, transaction timestamp/key/value types, and storage command kinds. It is a key boundary between internal execution failures and client protocol responses.

## Risks And Edge Cases

The nested pattern matches are precise and can miss new error variants unless updated. Some conversions include formatted debug strings for compatibility, which may be relied on by older clients. `SharedError::try_from` fails if multiple references remain; callers that require owned errors must ensure uniqueness. Debug MVCC info intentionally strips values, which is good for response size but means diagnostics are incomplete.

## Test Signals

Tests cover write-conflict key-error conversion, transaction-lock-not-found conversion with and without MVCC debug info, and commit-ts-expired conversion with and without MVCC debug info.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/kv/mod.rs -->
# sources/storage-engines/tikv/src/storage/kv/mod.rs

## Purpose

This module is the storage KV facade. It re-exports `tikv_kv` and exposes the local `TestEngineBuilder` used by tests.

## Important APIs, Types, And Functions

`pub use tikv_kv::*` makes TiKV KV engine traits, types, and helpers available through `crate::storage::kv`. `mod test_engine_builder` declares the local test builder. `pub use test_engine_builder::TestEngineBuilder` exposes it.

## Control Flow

There is no runtime logic. This is import/export wiring.

## State And Persistence Behavior

No state is stored in this module.

## Dependencies And Integration Points

This facade connects the storage module namespace to the external/internal `tikv_kv` crate and the RocksDB test-engine builder.

## Risks And Edge Cases

Because it glob re-exports `tikv_kv`, namespace changes in that crate can affect downstream imports through `storage::kv`. The local builder is always compiled as part of the module, though it is test-oriented.

## Test Signals

Behavior is covered through modules importing `storage::kv` and through `test_engine_builder.rs` tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/kv/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/kv/test_engine_builder.rs -->
# sources/storage-engines/tikv/src/storage/kv/test_engine_builder.rs

## Purpose

This module provides `TestEngineBuilder`, a small builder for constructing temporary RocksDB-backed `RocksEngine` instances in tests with selectable path, column families, IO limiter, API version, and block-cache behavior.

## Important APIs, Types, And Functions

`TestEngineBuilder` fields are optional path, optional CF list, optional `IoRateLimiter`, and API version. Builder methods are `new`, `path`, `cfs`, `api_version`, `io_rate_limiter`, `build`, `build_with_cfg`, and `build_without_cache`. `do_build` creates CF options from `DbConfig`, `BlockCacheConfig`, shared CF resources, per-CF option builders, DB resources/options, and then opens `RocksEngine::new`.

## Control Flow

If no path is supplied, RocksDB receives the duplicated `TEMP_DIR` empty path default. If no CF list is supplied, all CFs are opened. `build_without_cache` sets block cache capacity to zero before constructing shared cache resources. Per-CF option creation handles default, lock, write, and raft CFs specially and falls back to default Rocks CF options for unknown names. Engine type is always `EngineType::RaftKv`.

## State And Persistence Behavior

The builder creates real RocksDB engine state at the supplied path or default temp path. Tests that pass a temp directory can close and reopen to verify persistence. The builder itself is consumed on build.

## Dependencies And Integration Points

It integrates RocksDB engine types, engine traits CF constants, filesystem IO limiter, protobuf API version, storage block-cache config, and the main TiKV `DbConfig` option builders. It is exposed through `storage::kv::TestEngineBuilder`.

## Risks And Edge Cases

The default path is an empty string duplicated from rocksdb_engine, so callers should pass explicit temp directories when isolation matters. The builder always uses `RaftKv` option paths even if tests request API V2; API version affects CF options but not engine type. Unknown CF names receive default CF options, which may not mimic production tuning.

## Test Signals

Tests verify base CRUD, linear behavior, CF statistics, reopen persistence, perf statistics, max-skippable-internal-keys error propagation, read perf delete-skip counters, and prefix-seek behavior around tombstones in the write CF.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/kv/test_engine_builder.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/lock_manager/lock_wait_context.rs -->
# sources/storage-engines/tikv/src/storage/lock_manager/lock_wait_context.rs

## Purpose

This module holds shared state and callbacks for a lock-waiting `AcquirePessimisticLock` request. It guarantees that the request's storage callback is invoked at most once while coordinating wakeup, cancellation, timeout/deadlock errors, and the race where a resumed request re-enters lock waiting.

## Important APIs, Types, And Functions

`PessimisticLockKeyCallback` is called when a blocked key finishes or is canceled before enqueueing. `CancellationCallback` is called by lock-manager timeout/deadlock handling. `LockWaitContextInner` stores the final `StorageCallback`. `LockWaitContextSharedState` stores optional inner callback state, `LockWaitToken`, blocked key, atomic cancellation flag, and one-shot channels for passing an external cancellation error across the resume/enqueue race. `LockWaitContext<L>` wraps shared state, `LockWaitQueues<L>`, and `allow_lock_with_conflict`.

Public methods include `new`, `get_shared_states`, `get_callback_for_first_write_batch`, `get_callback_for_blocked_key`, and `get_callback_for_cancellation`. Internal `finish_request` performs the single completion path.

## Control Flow

When a request first waits, a context is created with a token and callback. The first-write-batch callback is currently a no-op boolean callback that unwraps success. The blocked-key callback calls `finish_request` as `Executed` unless the queue reports cancellation before enqueueing. The cancellation callback calls `finish_request` as `Canceled`.

For executed completions, `finish_request` tells the lock manager to remove the wait token. For cancellations, it sets `is_canceled`, attempts to remove the entry from `LockWaitQueues`, and if the entry is absent assumes the request has been popped and resumed; in that race it stores the cancellation error through `external_error_tx` and returns without taking the final callback. When a later enqueue sees `is_canceled`, it can consume `get_external_error` and finish as canceled before enqueueing. Normal completion takes `ctx_inner` exactly once and either fails the whole request when `allow_lock_with_conflict` is false or returns a one-element pessimistic-lock result when conflicts are allowed.

## State And Persistence Behavior

State is in-memory only. The core persistence property is callback ownership: `ctx_inner: Mutex<Option<...>>` is taken once to prevent duplicate RPC responses. The cancellation flag uses release/acquire ordering. The external error channel is one-shot and consumed in the rare cancellation/resume race.

## Dependencies And Integration Points

The module integrates storage callbacks and process results, pessimistic lock result types, lock manager token allocation/removal, `LockWaitQueues`, transaction keys, and `SharedError`. It is used by scheduler/lock-manager paths that queue, wake, or cancel pessimistic-lock waiters.

## Risks And Edge Cases

The most important edge case is documented in the file: a waiter can be popped for wakeup, encounter the lock again, and race with timeout cancellation. The atomic canceled flag plus external error handoff prevents the waiter from being re-enqueued forever. `finish_request` uses `unwrap` on expected ownership and conversion invariants, so misuse can panic. Double-calling a callback after completion is expected to do nothing only in paths that return early before taking consumed state.

## Test Signals

Tests create mock lock wait contexts, verify first-write-batch callback does not finish the request, verify blocked-key errors complete and drop the response channel, verify late cancellation after completion does not produce a second response, and verify cancellation removes a queued lock-wait entry and returns the expected lock error.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/lock_manager/lock_wait_context.rs -->
