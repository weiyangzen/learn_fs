# subset-b-008250 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rebalance.rs -->
# sources/object-store/rustfs/crates/ecstore/src/rebalance.rs

## Purpose

`rebalance.rs` implements RustFS ECStore pool rebalancing: it decides which pools should give up object data to restore a cluster-wide free-space ratio, persists rebalance progress in object-store metadata, starts and stops asynchronous pool workers, lists source objects by disk set, migrates each object version into the normal data-movement path, and records progress, terminal status, deferred transient failures, and source-cleanup warnings.

The file is intentionally broad. It contains production workflow code plus a large unit-test module for metadata state transitions, migration classification, retry behavior, queue manipulation, and compatibility with older serialized metadata. The core external behavior is that a rebalance operation is represented by `rebalance.bin` in the RustFS metadata bucket, while in-memory `ECStore.rebalance_meta` carries the active cancellation token and current stats snapshot.

## Important APIs, Types, and Functions

`RebalanceStats` is the per-pool progress record. It stores initial free/capacity, pending and completed bucket queues, last bucket/object, object/version/byte counters, participation flag, `RebalanceInfo`, and `RebalanceCleanupWarnings`. `update` and `update_batch` increment object/version counts and estimate on-disk bytes using erasure data/parity block counts; deleted entries and invalid data block counts add zero bytes.

`RebalanceInfo` stores start/end timestamps, last error, and a `RebalStatus` enum (`None`, `Started`, `Completed`, `Stopped`, `Failed`). `RebalanceCleanupWarnings` tracks non-fatal source cleanup delete failures separately from terminal `last_error`. `RebalanceMeta` is the persisted operation state: operation id, percent-free target, stopped time, pool stats, and skipped runtime-only fields `cancel` and `last_refreshed_at`.

`MigrationBackend` abstracts source-pool operations for tests and production `SetDisks`: `get_object_reader_for_migration`, `delete_object_for_migration`, and `move_remote_version_for_migration`. `migrate_entry_version` and its injectable-wait variant implement version-level migration handling for normal object data, delete markers, and remote-tiered versions.

`ECStore::init_rebalance_meta` computes the global percent-free goal from `StorageAdminApi::storage_info`, initializes a `RebalanceStats` entry per pool, marks only pools below the goal as participating, persists a merged metadata snapshot, and installs it in memory. `load_rebalance_meta`, `update_rebalance_stats`, `save_rebalance_stats`, and `save_rebalance_meta_with_merge` are the metadata load/save path.

`ECStore::start_rebalance` validates that decommission is not running and metadata exists, attaches a cancellation token, completes any already-satisfied pools, resolves local participating pools from endpoint topology, and spawns `rebalance_buckets` workers for local pools only. `stop_rebalance` cancels the token, marks started pools stopped, and persists a stop snapshot.

`rebalance_buckets` is the per-pool driver. It runs a periodic save task, repeatedly selects the next bucket, calls `rebalance_bucket`, defers buckets with transient entry failures once by moving them to the back of the queue, marks successful buckets done, and sends a terminal signal to the save task so metadata reaches `Completed`, `Stopped`, or `Failed`.

`rebalance_bucket` loads lifecycle/object-lock/replication configs, lists objects from every disk set in the pool, and dispatches per-entry work under a semaphore sized to the number of disk sets. `SetDisks::list_objects_to_rebalance` uses online disks, a majority listing quorum, `list_path_raw`, and `MetaCacheEntries::resolve` to feed agreed or resolved partial entries into the callback.

`rebalance_entry` is the object-level workflow. It skips directories and completed pools, resolves `FileInfo` versions, sorts newer versions first while keeping missing mod-times later, applies lifecycle data-movement skip logic, skips a final delete marker when replication is not configured, migrates each remaining version, batches stats updates, and deletes the source prefix when all versions are considered safely rebalanced.

Retry and classification helpers include `is_transient_rebalance_error`, `should_retry_rebalance_listing`, `rebalance_listing_retry_delay`, `rebalance_migration_retry_delay`, `rebalance_lock_retry_delay`, and `wait_rebalance_listing_retry`. Lock/RPC timeout-like failures get jittered exponential-ish delay capped by `REBALANCE_MIGRATION_LOCK_RETRY_CAP`; generic transient migration/listing errors use linear 250 ms increments.

Metadata merge helpers (`merge_rebalance_meta`, `merge_rebalance_pool_stats`, `merge_rebalance_bucket_lists`, `remove_rebalanced_buckets_from_queue`, `merge_rebalance_cleanup_warnings`) protect concurrent local snapshots from overwriting terminal states or losing queue/progress information.

## Control Flow

The normal lifecycle starts with `init_rebalance_meta`, which snapshots disk capacity/free space and decides pool participation against the computed cluster free-space ratio. `start_rebalance` then attaches a cancellation token and spawns one worker per local participating pool. Each pool worker periodically saves stats while processing the bucket queue.

For each bucket, `rebalance_bucket` creates one listing job per disk set. Listing callbacks acquire an entry semaphore, then spawn `rebalance_entry` tasks. The job waits for both listing completion and all entry tasks. A first hard entry error cancels the callback token and is returned. A first transient deferred outcome is returned as a bucket deferral rather than an immediate terminal failure.

For each entry, `rebalance_entry` resolves versions and processes them serially. Remote-tiered versions are moved by `decommission_tiered_object`; delete markers are recreated through `delete_object`; normal versions are read from the source pool and passed to `data_movement::migrate_object` through `rebalance_object`. Missing objects or versions are treated as ignored and cleanup-safe. Non-transient failures stop the entry. Transient failures set a prefixed last-error and ask the bucket driver to retry the bucket later.

Pool completion can happen when the bytes moved plus initial free space reaches the percent-free goal, or when the bucket queue becomes empty. Deferred transient errors intentionally block goal-based completion until the bucket later succeeds and clears the prefixed last error.

Stop flow is cooperative. `stop_rebalance` cancels the in-memory token and records `stopped_at`; workers observe cancellation through `CancellationToken`, return `OperationCanceled`, and the save task classifies that terminal signal as `Stopped`. Helper logic prevents a later completion/failure signal from overwriting an already stopped state.

## State and Persistence Behavior

The persistent object is `rebalance.bin`, written through `save_config_with_opts` and read through `read_config_with_metadata`. The file format prepends two little-endian `u16` fields (`REBAL_META_FMT`, `REBAL_META_VER`) to an `rmp_serde` MessagePack encoding of `RebalanceMeta`.

`RebalanceMeta::load_with_opts` treats an empty payload as no-op metadata, rejects payloads shorter than the four-byte header, rejects unknown format/version values, deserializes the state, and sets `last_refreshed_at` to now. `RebalanceMeta::save_with_opts` skips saving when `pool_stats` is empty, then writes the header and serialized payload.

Saves are protected by a namespace write lock on the metadata bucket/object. `save_rebalance_meta_with_merge` reloads the remote metadata under `no_lock`, merges the local snapshot, and saves the merged result. This reduces lost updates when multiple local pool workers persist progress.

Runtime-only state is deliberately not persisted. `cancel` and `last_refreshed_at` are serde-skipped, so a restarted node must reload metadata and attach a fresh cancellation token before running workers. Bucket queues, completed buckets, stats, status, end times, last errors, and cleanup warning summaries are persisted.

State transitions are conservative: terminal `Failed` and `Stopped` states are protected from being overwritten by stale `Started` or `Completed` snapshots. A changed operation id replaces the remote metadata with the local operation. Cleanup warnings merge by count max and latest timestamp.

## Dependencies and Integration Points

The module integrates with `ECStore`, `SetDisks`, `StorageAPI`, `ObjectIO`, `NamespaceLocking`, and object operations from `store_api`. It uses `StorageAdminApi::storage_info` for capacity data and `get_global_endpoints` to decide whether a participating pool is local to this process.

Object enumeration depends on `cache_value::metacache_set::list_path_raw`, `MetaCacheEntry`, `MetaCacheEntries`, and `MetadataResolutionParams`. Migration depends on `data_movement::migrate_object`, `GetObjectReader`, `ObjectOptions`, `HTTPRangeSpec`, and `ObjectInfo`.

Bucket policy/config integration appears through lifecycle, object-lock retention, and replication config lookups. Lifecycle checks call `pools::should_skip_lifecycle_for_data_movement` with `LcEventSrc::Rebal`; replication state is preserved on delete marker moves.

Operational integration includes tracing events using the `ecstore`/`rebalance` component/subsystem constants, `CancellationToken` for worker cancellation, Tokio tasks/channels/semaphores for concurrency, and RustFS error classifiers for object-not-found, version-not-found, operation-canceled, and network/host-down conditions.

## Risks and Edge Cases

`rebalance.rs` is concurrency-heavy. Multiple spawned tasks update shared metadata snapshots while periodic save tasks merge with remote metadata. The merge helpers mitigate stale writes, but correctness depends on all updates flowing through the merge path and on status precedence rules staying aligned with operational expectations.

Source cleanup is intentionally best-effort. If deleting the old source prefix fails with anything except missing object/version, the rebalance still completes the entry and records only a warning. This avoids data-loss from failed cleanup blocking progress, but it can leave duplicate source data and may require operational visibility around `cleanup_warnings`.

Transient failure handling can defer a bucket only once per pool-worker run. A second deferred pass for the same bucket becomes terminal. This avoids infinite loops but risks failing long-lived partial outages that might recover after more delay.

The free-space accounting is an estimate based on erasure layout and file size, not a fresh capacity read for every migrated object. Incorrect `FileInfo` erasure metadata or skipped/lifecycle-expired versions can affect perceived goal progress. Tests cover invalid data blocks but real skew remains operationally significant.

`load_rebalance_bucket_configs` invokes versioning config only to map errors and discards the result. That may be intentional parity with other config loading, but the unused value is a maintenance signal.

Listing uses a majority quorum and resolves partial entries. If listing returns stale or inconsistent `MetaCacheEntry` versions, migration may see not-found and classify as cleanup-safe ignored. That behavior is probably necessary for concurrent deletes, but it can mask unexpected metadata races.

`REBAL_META_FMT` and `REBAL_META_VER` are both hard-coded as `1` with comments saying they replace actual values. Any future format change must preserve backward loading or version migration explicitly.

## Test Signals

The embedded `rebalance_unit_tests` module is extensive. It covers migration branches for remote versions, delete markers, normal reader/transfer paths, not-found cleanup-safe ignores, overwrite failures, transient retries, zero-attempt normalization, data-usage-cache skipping, and failure stage reporting.

State and metadata tests cover percent-free math, pool participation, goal completion, empty-queue completion, deferred-error blocking, start validation against decommission/missing metadata, terminal event classification, stopped-state preservation, cancellation token handling, save-option application, bucket queue operations, cleanup warning preservation, metadata merge precedence, legacy metadata deserialization without cleanup warning fields, and invalid metadata load error formatting.

Retry/classification tests cover SlowDown, erasure quorum failures, I/O timeouts, disk timeout wrapping, lock/RPC timeout messages, non-transient overwrite/access-denied/not-found cases, listing retry attempt limits, listing delay scaling, migration delay scaling, and cancellation-aware listing retry waits.

The tests are mostly unit-level and helper-level. They do not appear to run a full integration rebalance over real disks, `list_path_raw`, metadata bucket persistence, or actual `data_movement::migrate_object`; those remain important integration gaps for behavior under real erasure sets and concurrent object mutation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rebalance.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rio.rs -->
# sources/object-store/rustfs/crates/ecstore/src/rio.rs

## Purpose

`rio.rs` is the ECStore read/write I/O compatibility facade over two RustFS RIO implementations. With the `rio-v2` feature it re-exports `rustfs_rio_v2`; otherwise it re-exports `rustfs_rio`. Around those exports, it provides stable helper functions for compression metadata, compression index encoding/decoding, compression/decompression reader selection, encryption/decryption reader selection, and write-pipeline composition.

The file’s main job is to let higher-level object code handle legacy streams and MinIO-compatible rio-v2 S2 streams with one interface. It also preserves legacy behavior when `rio-v2` is not enabled.

## Important APIs, Types, and Functions

`backend_name` returns `"rio-v2"` or `"legacy-rio"` according to the compile-time feature. `compression_metadata_value` returns the MinIO S2 scheme string (`klauspost/compress/s2`) under rio-v2 and the algorithm string under legacy mode.

`compression_scheme_to_algorithm` maps metadata strings to `CompressionAlgorithm`. Under rio-v2, the MinIO S2 scheme maps to the default algorithm placeholder because the v2 path routes compressed handling through S2 readers. Other strings are parsed with `CompressionAlgorithm::from_str`.

`ReadCompressionBackend` (`Legacy`, `V2`) and `compression_scheme_to_read_plan` split metadata interpretation into an algorithm plus a concrete decompressor backend. This allows v2 builds to read both new S2 metadata and older algorithm strings.

`ReadEncryptionBackend` (`Legacy`, `V2`) does the same for decryption call sites. `decrypt_reader`, `decrypt_reader_with_object_key`, `decrypt_multipart_reader`, and `decrypt_multipart_reader_with_object_key` choose between legacy nonce-based APIs and rio-v2 sequence/object-key APIs, while returning boxed `AsyncRead` trait objects.

`compression_index_storage_bytes` serializes an `Index` for metadata/storage. In rio-v2 builds it delegates to MinIO-compatible index storage bytes; otherwise it stores `Index::into_vec()`. `decode_compression_index_bytes` first tries the v2 MinIO decoder when available, then the legacy `Index::load`, then a rio-v2-only repair path that restores legacy S2 index framing headers before another legacy load attempt.

`compression_reader` creates a `CompressReader`. In rio-v2 builds it calls `CompressReader::with_encrypted_padding` when compression will be followed by encryption, so S2 streams receive padding frames suitable for encrypted MinIO-compatible layout. In legacy builds, the `encrypted` flag is ignored.

`decompression_reader` returns a boxed decompressor selected by `ReadCompressionBackend`; legacy builds ignore the backend and always use `rustfs_rio::DecompressReader`.

`WriteEncryption` is a small constructor-backed configuration object for write encryption. It supports singlepart object-key mode, singlepart key+base-nonce mode, multipart legacy key+base-nonce+part-number mode, and multipart object-key mode. The internal `WriteEncryptionMode` enum is private.

`WritePlan` composes optional compression and optional encryption around a `HashReader`. `new`, `with_compression`, `with_encryption`, and `is_passthrough` describe the plan. `apply` wraps compression first, then encryption, preserving the `HashReader::SIZE_PRESERVE_LAYER` sizing contract and passing through the caller-provided `actual_size`.

## Control Flow

Compile-time feature gates determine the underlying exported crate and many branch bodies. In a legacy build, most facade functions are thin wrappers over `rustfs_rio`. In a rio-v2 build, metadata and reader selection become compatibility decisions: MinIO S2 compression metadata maps to the v2 backend, while legacy algorithm strings still map to legacy decompression.

For reads, call sites can parse object compression metadata via `compression_scheme_to_read_plan`, build a decompressor with `decompression_reader`, and build a decryptor with the appropriate `decrypt_*` helper. The facade keeps the caller from directly depending on both rio crates in most cases.

For writes, callers build a `WritePlan`. `apply` first wraps the input `HashReader` in a compression reader if requested. It passes whether encryption is also configured so rio-v2 can add encrypted S2 padding. Then it wraps the result in the requested encryption mode. Object-key encryption modes use v2 object-key APIs when available and fall back to legacy nonce-zero APIs without the feature.

For compression index persistence and reads, `compression_index_storage_bytes` writes the format appropriate to the active feature. `decode_compression_index_bytes` is deliberately permissive: v2 MinIO format, direct legacy format, and restored-header legacy format can all decode to an `Index`.

## State and Persistence Behavior

The file itself owns no durable state. Its persistence impact is indirect through metadata and object bytes produced by compression/encryption readers. The stable metadata-facing values are compression scheme strings and serialized compression indexes.

Under rio-v2, newly written compressed metadata uses the MinIO S2 scheme string regardless of the `CompressionAlgorithm` argument. New index bytes use `minio_index_storage_bytes`. Compatibility reads still attempt to decode legacy `Index` bytes and v2 headerless/header-restored shapes.

`WritePlan::apply` preserves size metadata through `HashReader::from_reader` wrappers. This is significant because surrounding object-storage code relies on `HashReader` for checksums, sizes, and optional compression indexes.

## Dependencies and Integration Points

The module re-exports either `rustfs_rio_v2` or `rustfs_rio`, so downstream ECStore modules can import RIO types from this facade. It depends on `bytes::Bytes`, `rustfs_utils::CompressionAlgorithm`, `tokio::io::AsyncRead`, and the `HashReader`, `CompressReader`, `DecompressReader`, `EncryptReader`, `DecryptReader`, and `Index` types provided by the selected RIO crates.

The compression scheme string matches MinIO S2 metadata, making this file part of object metadata interoperability. Encryption helpers encode compatibility assumptions for legacy nonce-based encryption, rio-v2 sequence-number decryption, and object-key encryption.

## Risks and Edge Cases

The rio-v2 metadata path intentionally ignores the provided compression algorithm for `compression_metadata_value` and maps MinIO S2 to `CompressionAlgorithm::default()`. That is correct only while v2 compressed objects are S2-only; future algorithm support would need to revisit this.

Legacy fallback for object-key encryption uses a zero nonce with the object key. That preserves old API shape but is not equivalent to rio-v2 object-key semantics unless the legacy implementation expects that convention.

Reader helper return types are boxed trait objects for read-side decompression/decryption, trading dynamic dispatch for uniform call sites. Write-side `WritePlan::apply` stays in `HashReader`, so changes in `HashReader::from_reader` sizing/index behavior can affect all compressed/encrypted writes.

`restore_legacy_index_headers` synthesizes S2 framing around raw bytes and mutates the chunk length bytes after construction. That compatibility repair is low-level and easy to break if S2 index framing assumptions change.

Feature-gated behavior means a test suite run without `rio-v2` does not exercise the MinIO S2 scheme, object-key APIs, sequence-number decryptors, or encrypted padding behavior.

## Test Signals

The local test module covers `WritePlan` passthrough, compression-then-encryption multipart round trip, and under `rio-v2`, singlepart and multipart object-key encryption round trips, S2 stream emission and seekable index availability for large compressed data, skipped indexes for smaller data, small compressed encrypt/decrypt round trip, encrypted S2 padding frame insertion and 256-byte alignment, and first-read behavior for v2 decompression on small and larger buffers.

The tests provide strong signal for write-pipeline ordering and rio-v2 compatibility behavior. The visible gaps are metadata parser tests for `compression_scheme_to_algorithm`, `compression_scheme_to_read_plan`, index decode fallback paths, and read helper selection across both feature configurations.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rio.rs -->
