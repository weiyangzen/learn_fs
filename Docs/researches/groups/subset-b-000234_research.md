# subset-b-000234 research

This grouped report covers the Nydus storage cache, cache state, worker, device, factory, and crate root files assigned to subset B. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/dummycache.rs -->
# sources/cloud-native/nydus/storage/src/cache/dummycache.rs

Purpose: provides `DummyCacheMgr` and its private `DummyCache`, a `BlobCacheMgr`/`BlobCache` implementation that does not persist cached chunks. It either reports all chunks as cached for local-disk style backends or reports none cached for remote on-demand reads, while still handling backend reads, decompression, decryption, and validation through the common `BlobCache` helper methods.

Important APIs and control flow: `DummyCacheMgr::new` captures backend, `cached` readiness behavior, and cache validation setting. `get_blob_cache` rejects ZRan blobs, obtains a backend `BlobReader`, and builds a `DummyCache` with a `NoopChunkMap`. `DummyCache::read` validates non-empty IO, uses a fast path when a single full chunk can be read directly into the destination volatile slice, otherwise allocates one temporary uncompressed buffer per user IO descriptor, calls `read_chunk_from_backend`, and scatters data with `copyv`. Prefetch APIs are intentionally inert: start/stop succeed, active is false, and actual prefetch returns `Unsupported`.

State and persistence behavior: there is no data cache or persistent state. Readiness is entirely represented by `NoopChunkMap::new(self.cached)`. `destroy` is idempotent via `AtomicBool` and shuts down the backend once.

Dependencies and integration points: integrates with `BlobBackend`, `BlobReader`, `BlobInfo`, `BlobIoVec`, `BlobIoDesc`, `BlobPrefetchRequest`, `NoopChunkMap`, volatile FUSE buffers, Nydus compression/digest/crypto helpers, and the common `BlobCache` default methods.

Risks and test signals: the unsafe slice conversion in the fast path depends on the destination slice being valid for the requested chunk size. Multi-descriptor reads only push buffers for `user_io`, so offsets passed to `copyv` must match the first descriptor assumptions. Tests cover metadata accessors, unsupported prefetch, direct and multi-buffer reads, manager destroy/gc/backend access, and validation of config wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/dummycache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/filecache/mod.rs -->
# sources/cloud-native/nydus/storage/src/cache/filecache/mod.rs

Purpose: implements `FileCacheMgr`, the local file-backed blob cache manager. It lazily creates `FileCacheEntry` values that cache either uncompressed blob data (`.blob.data`) or compressed raw blob data (`.blob.raw`) under a configured work directory, with optional cache-file encryption, prefetch workers, metrics, chunk maps, RAFS v6 metadata loading, and optional content-addressed deduplication.

Important APIs and control flow: `FileCacheMgr::new` reads filecache config, creates metrics and `AsyncWorkerMgr`, and records cache policy flags. `get_or_create_cache_entry` first checks the `blobs` map under `RwLock`, then constructs a `FileCacheEntry`, inserts it if no concurrent creator won, and records the underlying file for metrics. The `BlobCacheMgr` implementation starts workers, stops workers/backend/metrics on destroy, and garbage-collects entries whose `Arc` count shows no external users. `FileCacheEntry::new_file_cache` chooses separate metadata reader when needed, disables CAS for encrypted/raw/tarfs caches, computes blob sizes, opens or sizes the cache data file, creates the chunk map, optionally loads blob metadata, configures cache encryption, and returns a fully wired `FileCacheEntry`.

State and persistence behavior: persistent data lives in `${work_dir}/${blob_id}.blob.data` or `.blob.raw`; readiness normally lives in `${work_dir}/${blob_id}.blob.data.chunk_map` through `IndexedChunkMap`. Legacy v5/no-extended-table paths fall back to `DigestedChunkMap` wrapped in `BlobStateMap`, which is not persistent and forces validation because direct indexed readiness is unavailable. When cache raw data is enabled, expected file length uses compressed data size; otherwise uncompressed size.

Dependencies and integration points: depends on `cachedfile::FileCacheEntry`/`FileCacheMeta` for actual IO, `BlobStateMap`, `IndexedChunkMap`, `DigestedChunkMap`, `NoopChunkMap`, async worker management, runtime from `factory`, backend readers, blob feature flags, Nydus metrics, and optional `CasMgr`.

Risks and test signals: wrong file size is treated as invalid, protecting stale cache reuse but requiring cache cleanup when metadata changes. CAS is silently disabled for several modes. Direct chunk map selection affects whether `get_blob_object` and validation are available. Tests cover filecache config work_dir validation, suffix constants/path composition, and invalid regular-file work_dir; older deeper read/merge tests are present but commented out.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/filecache/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/fscache/mod.rs -->
# sources/cloud-native/nydus/storage/src/cache/fscache/mod.rs

Purpose: implements Linux `FsCacheMgr`, a `BlobCacheMgr` variant that uses a file supplied by the kernel fscache subsystem as the backing data file while reusing `FileCacheEntry` for blob cache behavior. It is Linux-only via the parent module gate and is intended for uncompressed cache mode.

Important APIs and control flow: `FsCacheMgr::new` rejects compressed cache mode, reads fscache work_dir, creates metrics and worker manager, and starts the global factory manager checker. Its cache-entry lookup/insertion mirrors `FileCacheMgr`. `check_stat` scans all entries; after all blobs report ready for the configured number of checks, it stops prefetch workers and marks metrics `data_all_ready`. `FileCacheEntry::new_fs_cache` rejects RAFS v5 without extended blob table and tarfs, requires `BlobInfo::get_fscache_file`, gets data and optional separate-meta readers, loads RAFS metadata through `FileCacheMeta`, creates a non-persistent `IndexedChunkMap`, restores readiness from sparse-file holes, and returns a direct-IO-capable entry.

State and persistence behavior: data is held by the external fscache file rather than a file opened by this module. The chunk map is opened with `persist=false`, so the temporary bitmap file is removed after mapping. `restore_chunk_map` walks the fscache file with `lseek64(..., SEEK_HOLE)` using metadata offsets and marks chunk ranges ready for allocated regions until a hole or file end is reached.

Dependencies and integration points: integrates with `BlobInfo` fscache file handles, `FileCacheMeta`, `BlobStateMap<IndexedChunkMap>`, kernel sparse-file semantics, async prefetch workers, global `BLOB_FACTORY` checker, metrics, backend readers, and optional CAS.

Risks and test signals: correctness depends on kernel `SEEK_HOLE` behavior and metadata offset-to-chunk mapping. It does not support compressed mode, tarfs, v5 no-ext-table, or blobs without blob meta info. A failed hole seek stops recovery and leaves later chunks not ready. Tests construct config, mock backend, a texture-derived ZRan blob info, an fscache file, manager init/get/gc/check/destroy paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/fscache/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/mod.rs -->
# sources/cloud-native/nydus/storage/src/cache/mod.rs

Purpose: defines the cache layer abstraction between storage backends and `BlobDevice`, plus shared logic for backend reads, decompression, decryption, digest validation, merged IO requests, chunk decompression iteration, and cache manager lifecycle. It exports dummy/file/fscache managers and the cache state module.

Important APIs and control flow: `BlobIoMergeState` groups adjacent `BlobIoDesc` entries into `BlobIoRange` requests bounded by compressed size and gap. `BlobCache` exposes blob metadata accessors, backend reader access, chunk map access, chunk-info lookup, prefetch lifecycle, direct read, and optional blob-object access. Default helpers include `read_chunks_from_backend`, which fetches one compressed range and returns `ChunkDecompressState`; `read_chunk_from_backend`, which reads/decrypts/decompresses/validates one chunk; `decompress_chunk_data`; `validate_chunk_data`; `check_digest`; and streaming-cache hook `cache_chunk_data`. `ChunkDecompressState` iterates requested chunks and handles normal, Batch, and ZRan decompression paths by caching the current batch/zran decompressed buffer.

State and persistence behavior: this file owns no persistent state but defines how cache implementations expose `ChunkMap` state and how validation is forced. `ChunkDecompressState` holds the merged compressed buffer and temporary decompressed batch/zran buffer, with index fields to avoid repeated decompression when consecutive chunks share context.

Dependencies and integration points: depends on backend `BlobReader`/`RequestSource`, FUSE volatile slices, `BlobInfo`/`BlobIoDesc`/`BlobIoRange`, compression including zran decoder, encryption helpers, digest/CRC utilities, blob compression metadata, and `RAFS_MAX_CHUNK_SIZE`.

Risks and test signals: merged reads require chunk offsets/sizes to fit the fetched buffer and enforce max decompressed size. Legacy stargz compressed size is estimated differently and validation is skipped for legacy stargz. Batch/ZRan paths depend on metadata context consistency. Tests cover IO merge state construction, issuing behavior under gap/size limits, and continuity checks through `BlobIoDesc`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/blob_state_map.rs -->
# sources/cloud-native/nydus/storage/src/cache/state/blob_state_map.rs

Purpose: implements `BlobStateMap`, a concurrency adapter over a base `ChunkMap` or `RangeMap`. Base maps know whether data is ready; this wrapper adds pending/inflight tracking so concurrent readers/prefetchers do not download the same chunk or range repeatedly.

Important APIs and control flow: `Slot` stores `Inflight`/`Complete` with a `Mutex` and `Condvar`; waiters call `wait_for_inflight` with `SINGLE_INFLIGHT_WAIT_TIMEOUT`. `ChunkMap for BlobStateMap` delegates readiness, tracks pending entries in `inflight_tracer`, and implements `check_ready_and_mark_pending`: if ready, return true; if another slot exists, wait and retry; otherwise double-check readiness, insert a slot, and return false. `set_ready_and_clear_pending` updates the base map then clears the slot. Range implementations for `IndexedChunkMap` and `BlobRangeMap` use the base map to find not-ready indices, insert slots only for still-not-ready ranges, clear ranges, and wait on inflight ranges before rechecking readiness.

State and persistence behavior: inflight state is in-memory only in `Mutex<HashMap<I, Arc<Slot>>>`. Persistence depends entirely on the wrapped map (`IndexedChunkMap`/`BlobRangeMap` are bitmap-backed; `DigestedChunkMap` is memory-only). Clearing pending notifies all waiters regardless of success or failure path.

Dependencies and integration points: wraps `IndexedChunkMap`, `BlobRangeMap`, or `DigestedChunkMap` through `ChunkIndexGetter`; exposes downcast-based `as_range_map` for indexed maps; uses `StorageError::Timeout` to report wait expiration.

Risks and test signals: timed-out slots remain until the original owner clears pending, so failed download paths must always call `clear_pending`. The double-checks close common races around slot removal and readiness updates. Tests cover million-entry indexed/digested concurrency, inflight race and timeout behavior, range readiness/pending behavior, and all-ready transitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/blob_state_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/digested_chunk_map.rs -->
# sources/cloud-native/nydus/storage/src/cache/state/digested_chunk_map.rs

Purpose: implements `DigestedChunkMap`, a compatibility `ChunkMap` for legacy RAFS images that lack a stable chunk array/index. It tracks readiness by chunk digest rather than numeric chunk index.

Important APIs and control flow: `DigestedChunkMap::new` creates an empty `RwLock<HashSet<RafsDigest>>`. `is_ready` checks whether `chunk.chunk_id()` is present. `set_ready_and_clear_pending` inserts the digest into the set. `ChunkIndexGetter` returns the digest value, allowing `BlobStateMap<DigestedChunkMap, RafsDigest>` to key inflight slots by content digest.

State and persistence behavior: all readiness state is memory-only and is lost when the process exits. Because digest hashing and set storage are heavier than bitmap indexing, the module comments explicitly restrict its role to backward compatibility.

Dependencies and integration points: depends on `RafsDigest`, `BlobChunkInfo`, `ChunkMap`, and `ChunkIndexGetter`. It is selected by `FileCacheEntry::create_chunk_map` when RAFS v5 indexing is disabled or the blob has `_V5_NO_EXT_BLOB_TABLE`.

Risks and test signals: digest-based readiness can conflate duplicate chunks by content, which is acceptable for deduplicated content but different from per-index readiness. Lock poisoning is not expected and is unwrapped. Direct tests are mostly through `BlobStateMap` performance/concurrency comparisons against `IndexedChunkMap`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/digested_chunk_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/indexed_chunk_map.rs -->
# sources/cloud-native/nydus/storage/src/cache/state/indexed_chunk_map.rs

Purpose: implements `IndexedChunkMap`, the preferred bitmap-file-backed readiness map for blobs with stable chunk indices. It supports both per-chunk `ChunkMap` operations and batch `RangeMap<u32>` operations.

Important APIs and control flow: `IndexedChunkMap::new` opens `${blob_path}.chunk_map` through `PersistMap::open`. `is_ready` fast-paths when the whole range is ready, otherwise validates the chunk id and reads its bit. `set_ready_and_clear_pending` sets the bit in `PersistMap`. `RangeMap` methods check all-ready, scan indices for readiness, return not-ready indices for `check_range_ready_and_mark_pending`, and set a range ready one bit at a time.

State and persistence behavior: state is a memory-mapped bitmap with a 4096-byte header and one bit per chunk. The `persist` constructor argument controls whether the file remains on disk after mapping. `is_persist` returns true because the implementation supports persistent state even when a caller chooses non-persistent open.

Dependencies and integration points: wraps `persist_map::PersistMap`; is wrapped by `BlobStateMap` for pending tracking; is created by filecache/fscache entry constructors; supplies `ChunkIndexGetter<Index = u32>`.

Risks and test signals: invalid chunk counts or mismatched existing file sizes return errors to avoid trusting corrupt readiness. `check_range_ready_and_mark_pending` does not validate every index before `is_chunk_ready` in the scan, so callers rely on bounded ranges. Tests cover invalid file size, zero-size initialization, header-not-ready, all-ready header, v0 header loading, bit setting, and range behavior indirectly through `BlobStateMap`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/indexed_chunk_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/mod.rs -->
# sources/cloud-native/nydus/storage/src/cache/state/mod.rs

Purpose: defines the public cache-state abstraction layer: `ChunkMap` for per-chunk readiness/pending state and `RangeMap` for batch readiness over chunk indices or data-address ranges. It re-exports concrete state map implementations used by cache managers.

Important APIs and control flow: `ChunkMap` requires `is_ready` and provides default non-pending behavior, combined `is_ready_or_pending`, unsupported defaults for pending mutation methods, `is_persist`, and optional `as_range_map`. `RangeMap` exposes all-ready checks, range readiness, pending discovery/marking, setting ranges ready, clearing pending, and waiting for ranges. Defaults return false, `enosys`, or no-op behavior unless an implementation overrides them.

State and persistence behavior: this file owns no state. It establishes contracts that implementations must honor: `check_ready_and_mark_pending` returning `Ok(false)` means the caller owns an inflight slot and must later call `set_ready_and_clear_pending` or `clear_pending`; range pending methods follow the same ownership model.

Dependencies and integration points: used by `BlobCache` implementations, `FileCacheEntry`, prefetch paths, `BlobDevice::all_chunks_ready`, and concrete maps `BlobStateMap`, `BlobRangeMap`, `DigestedChunkMap`, `IndexedChunkMap`, and `NoopChunkMap`.

Risks and test signals: unsupported defaults panic for some `ChunkMap` methods, so cache code must only call pending methods on maps wrapped by `BlobStateMap` or concrete implementations that support them. The comments document concurrency expectations but enforcement is implementation-specific. Tests live in concrete modules.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/noop_chunk_map.rs -->
# sources/cloud-native/nydus/storage/src/cache/state/noop_chunk_map.rs

Purpose: implements `NoopChunkMap`, a trivial readiness map that reports every chunk as either always ready or always not ready. It is used when the cache layer should not maintain real per-chunk state, such as dummy cache and tarfs/local-disk paths.

Important APIs and control flow: `NoopChunkMap::new(cached)` stores a boolean. `ChunkMap::is_ready` returns that boolean for any chunk. `ChunkIndexGetter` returns `chunk.id()` so it can still be wrapped by generic code if needed.

State and persistence behavior: state is only the immutable `cached` flag and has no persistence, pending tracking, or readiness mutation.

Dependencies and integration points: used by `DummyCacheMgr` to control prefetch eligibility semantics and by filecache tarfs handling through `BlobStateMap::from(NoopChunkMap::new(true))`.

Risks and test signals: because all chunks share one readiness answer, using this map in a path that expects real partial caching would produce either redundant backend reads or false cache hits. Tests cover true/false readiness and index getter behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/noop_chunk_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/persist_map.rs -->
# sources/cloud-native/nydus/storage/src/cache/state/persist_map.rs

Purpose: provides `PersistMap`, the low-level memory-mapped bitmap file used by `IndexedChunkMap` and `BlobRangeMap`. It manages file creation/opening, header validation, bit-level atomic readiness updates, all-ready accounting, and optional removal for non-persistent users.

Important APIs and control flow: `PersistMap::open` rejects zero counts, opens the file with create/truncate rules based on `create` and `persist`, computes expected header plus bitmap size, writes a header for empty files, rejects size mismatches, maps the file with `FileMapState`, repairs all-zero race-window files, validates v1 magic fields, counts ready bits unless the header says all-ready, calls `readahead`, and removes the file if `persist` is false. `set_chunk_ready` validates the index, loops with atomic compare-exchange on the containing byte, decrements `not_ready_count`, and calls `mark_all_ready` when the final bit is set. `is_chunk_ready` reads one bit using a high-bit-first mask.

State and persistence behavior: file format starts with a 4096-byte `Header` containing magic/version/all-ready fields, followed by one bit per managed item. `not_ready_count` is in-memory, derived at open. `mark_all_ready` currently syncs data but leaves header mutation commented, so all-ready persistence may require bit recount on reopen unless an existing header was already marked.

Dependencies and integration points: depends on Unix fd cloning, `FileMapState`, `AtomicU8` bitmap operations, `div_round_up`, and local `readahead`.

Risks and test signals: corrupt size/header is intentionally fatal. Atomic byte updates protect concurrent setters, but sync/header behavior is conservative. Tests in `indexed_chunk_map.rs` exercise file-size validation, new and existing headers, all-ready headers, v0 compatibility, and bit setting.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/persist_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/range_map.rs -->
# sources/cloud-native/nydus/storage/src/cache/state/range_map.rs

Purpose: implements `BlobRangeMap`, a bitmap-backed `RangeMap<u64>` for readiness of fixed-size data address ranges rather than chunk indices.

Important APIs and control flow: `BlobRangeMap::new` creates `${blob_path}.range_map`; `open` opens an existing `${workdir}/${blob_id}.range_map`. `get_range(start, count)` converts byte offsets to bitmap indices by shifting with `shift`, validates start and end indices, and returns a half-open index range. `is_range_ready` scans all bits for the computed range unless all-ready. `check_range_ready_and_mark_pending` returns the shifted start offsets for not-ready bitmap entries. `set_range_ready_and_clear_pending` sets all bits covering the requested range.

State and persistence behavior: readiness is persisted through `PersistMap` with one bit per range bucket. `shift` defines bucket size as `1 << shift`; pending state is not in this type directly and is added by `BlobStateMap<BlobRangeMap, u64>`.

Dependencies and integration points: used through `RangeMap` and `BlobStateMap::from_range_map`. It shares persistence, atomic bit setting, and all-ready accounting with `IndexedChunkMap`.

Risks and test signals: `get_range` assumes `count > 0`; otherwise `end - 1` can underflow in debug/produce invalid behavior. Capacity allocation in `check_range_ready_and_mark_pending` uses byte count as `usize`, which can be excessive for large ranges even though the returned vector is per bucket. Tests cover concurrent million-range readiness and simple check/set behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/state/range_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/worker.rs -->
# sources/cloud-native/nydus/storage/src/cache/worker.rs

Purpose: implements asynchronous cache prefetch worker infrastructure. It converts Nydus prefetch configuration into worker threads, a request channel, optional bandwidth limiting, metrics updates, and blocking handlers for blob-range and filesystem-range prefetch.

Important APIs and control flow: `AsyncPrefetchConfig::from` copies enable/thread/batch/bandwidth settings. `AsyncPrefetchMessage` carries blob-compressed prefetch, filesystem range prefetch, test ping, and rate-limiter messages. `AsyncWorkerMgr::new` creates a channel, zero-permit semaphore, retry counter, counters, and optional leaky-bucket limiter sized at least `RAFS_MAX_CHUNK_SIZE`. `start` spawns configured threads when enabled. Each thread installs a runtime with `with_runtime`, adds one semaphore permit, receives messages, applies rate limiting, and spawns blocking handlers while holding an owned semaphore token. `send_prefetch_message` increments inflight only when enabled. Stop closes the channel and wakes workers until the worker count reaches zero.

State and persistence behavior: all worker state is in-memory atomics plus the channel. `retry_times` globally limits retries for failed `BlobObject::fetch_range_compressed`; retry is scheduled on the global async runtime after one second.

Dependencies and integration points: used by filecache and fscache managers. Handlers call `BlobObject::fetch_range_compressed`, `BlobObject::prefetch_chunks`, or `BlobCache::prefetch_range`, update `BlobcacheMetrics`, and honor `BlobCache::is_prefetch_active`.

Risks and test signals: if a blob is inactive after acquiring a semaphore token, the code drops the message without an explicit token drop in that branch scope only at scope end; inflight is decremented after dispatch, not after blocking work completes. Stop relies on channel close and worker count polling. Tests cover worker start/stop and pings, disabled send behavior, inflight increment, consumed bandwidth accounting, and rate limiter delay/inflight behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/worker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/device.rs -->
# sources/cloud-native/nydus/storage/src/device.rs

Purpose: exposes public blob storage APIs used by RAFS callers: blob metadata (`BlobInfo`), chunk metadata traits, IO descriptors/vectors/ranges, prefetch requests, direct blob-object access, and `BlobDevice`, the wrapper that routes reads and prefetches to per-blob `BlobCache` objects.

Important APIs and control flow: `BlobFeatures` and `BlobChunkFlags` define compatibility, compression, encryption, tar/toc, zran, batch, and checksum flags. `BlobInfo` stores blob ids, sizes, chunk counts, compression/digest/cipher info, v6 metadata locations, ToC/meta digests, fscache file handles, and special inlined-meta path handling. `compressed_data_size` interprets layout differences across separated blobs, tar/toc, RAFS v5/v6, and tar headers. `BlobChunkInfo` abstracts chunk layout and integrity fields; `BlobIoChunk` erases concrete chunk types. `BlobIoDesc`, `BlobIoVec`, `BlobIoMerge`, and `BlobIoRange` describe and merge user/internal IO. `BlobDevice::new` asks `BLOB_FACTORY` for caches, `update` swaps cache vectors through `ArcSwap`, `read_to` wraps a `BlobIoVec` as `FileReadWriteVolatile`, `prefetch` dispatches configured and IO-derived prefetches, `fetch_range_synchronous` uses direct `BlobObject`, and `all_chunks_ready` checks cache maps.

State and persistence behavior: `BlobDevice` holds an atomically swappable `Arc<Vec<Arc<dyn BlobCache>>>` and a fixed `blob_count`. Persistent cache state is delegated to each cache. `BlobInfo` can store an fscache `File`, mutable meta path under `Mutex`, and cipher context.

Dependencies and integration points: integrates with `ConfigV2`, `BLOB_FACTORY`, FUSE zero-copy writer traits, volatile file buffers, Nydus compression/crypto/digest types, and RAFS v5 chunk extension trait.

Risks and test signals: `BlobIoVec::append` only asserts blob id equality, so tests document that same id with different index can merge. `set_prefetch_info` truncates offsets/sizes to `u32`. `read_to` assumes all descriptors target one blob. Tests cover feature validation, tarfs detection, blob info setters/layout helpers, IO chunk delegation, continuity/gap logic, large vector append, meta-id extraction, digest/toc getters, and raw id trimming.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/factory.rs -->
# sources/cloud-native/nydus/storage/src/factory.rs

Purpose: central factory for constructing and caching blob cache managers and storage backends. It selects backend implementations by config, selects cache manager type (`FileCacheMgr`, Linux `FsCacheMgr`, or `DummyCacheMgr`), owns the shared async runtime, and garbage-collects unused managers.

Important APIs and control flow: `ASYNC_RUNTIME` is a global Tokio runtime with one worker thread, up to eight blocking threads, and cache-flusher thread naming. `BlobCacheMgrKey` hashes selected config fields (`id`, backend type, cache type, prefetch config) while deriving equality over the whole `Arc<ConfigV2>`. `BLOB_FACTORY` is the global `BlobFactory`. `start_mgr_checker` starts a single periodic task that calls `BLOB_FACTORY.check_cache_stat()` every five seconds. `new_blob_cache` reads backend/cache/rafs config, reuses an existing manager under a mutex if the key matches, otherwise constructs a backend and cache manager, initializes it, inserts it, and returns `mgr.get_blob_cache(blob_info)`. `gc` asks managers to drop a target blob or unused entries and removes empty managers after a second check. `new_backend` and `new_backend_from_json` dispatch to feature-gated backend constructors.

State and persistence behavior: factory state is an in-memory mutex-protected manager map plus an atomic flag for the checker task. Cache/backend persistence is delegated to selected managers and backend implementations.

Dependencies and integration points: depends on `nydus_api` config accessors, feature-gated backend modules (`oss`, `s3`, `registry`, `localfs`, `localdisk`, `http_proxy`), cache managers, `BlobInfo`, and Tokio.

Risks and test signals: the custom hash covers fewer fields than derived equality, which is valid for `HashMap` but may reduce cache reuse if semantically identical configs differ in un-hashed fields. Holding the factory mutex while manager initialization runs can serialize slow backend setup. Tests cover default factory state, supported backend list uniqueness, and rejection of unknown backend types for config and JSON constructors.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/factory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/lib.rs -->
# sources/cloud-native/nydus/storage/src/lib.rs

Purpose: crate root for `nydus-storage`. It documents the three-layer storage design (backend, cache, device), exports public modules, defines shared RAFS sizing constants, provides a helper macro for metadata getter implementations, and defines the storage-specific error/result type.

Important APIs and control flow: exported modules are `backend`, `cache`, `device`, `factory`, `meta`, and `utils`, with test helpers gated by `cfg(test)`. `impl_getter!` expands simple value-returning getters for upper RAFS metadata types. Constants include default/max chunk sizes, max chunks per blob, and batch merge size-to-gap shift. `StorageError` covers unsupported operations, backend wait timeout, volatile-slice errors, memory overflow, non-continuous ranges, cache-index IO errors, and proxy forbidden/rate-limited cases. Its `Display` implementation provides human-readable messages. `StorageResult<T>` aliases `Result<T, StorageError>`.

State and persistence behavior: no runtime state or persistence is owned here; it establishes shared constants and error contracts consumed throughout storage.

Dependencies and integration points: imports logging, bitflags, and nydus API macros crate-wide. `StorageError` is used by cache state waiting, cache IO helpers, proxy/backends, and device paths that need non-`io::Error` storage status.

Risks and test signals: `StorageError` does not implement `std::error::Error` or automatic conversion here, so callers manually map to `io::Error` when crossing IO APIs. Tests cover display text for proxy forbidden and proxy limited variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/lib.rs -->
