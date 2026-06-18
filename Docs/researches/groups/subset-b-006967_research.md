# subset-b-006967 research

Grouped source-tree-aligned research for Ceph RGW RADOS coroutine helper tools and D3N local data cache code. Each section is delimited for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_tools.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_tools.cc

## Purpose

Implements concrete `_send_request()` specializations for small RGW RADOS coroutine helpers declared in `rgw_cr_tools.h`. These wrappers let coroutine code create users, fetch user and bucket metadata, update bucket lifecycle configuration, and retrieve bucket sync policy handlers through the existing RGW admin, SAL, lifecycle, and bucket-service APIs.

## Important APIs, Types, and Functions

The file specializes `RGWUserCreateCR::Request::_send_request`, `RGWGetUserInfoCR::Request::_send_request`, `RGWGetBucketInfoCR::Request::_send_request`, `RGWBucketLifecycleConfigCR::Request::_send_request`, and `RGWBucketGetSyncPolicyHandlerCR::Request::_send_request`. `RGWUserCreateCR` builds an `RGWUserAdminOpState` from `rgw_user_create_params` and calls `RGWUserAdminOp_User::create()`. The metadata helpers call `store->ctl()->user->get_info_by_uid()`, `store->load_bucket()`, `RGWLC::set_bucket_config()`, and `store->ctl()->bucket->get_sync_policy_handler()`.

## Control Flow and Data Flow

User creation reads the `rgw_user_max_buckets` config default, copies user-facing fields into an admin op state, maps the optional key type string to S3 or Swift constants, applies default bucket/user quota limits when requested, and invokes the admin create operation with `RGWNullFlusher` and `null_yield`. User-info and bucket-info coroutines are direct read-through calls that fill their result objects. Lifecycle setup first obtains `RGWLC` from `store->getRados()`, fails with `-EIO` when lifecycle support is not initialized, and then submits bucket attrs plus an `RGWLifecycleConfiguration`. Sync-policy retrieval forwards optional zone and bucket scope into the bucket service and stores the returned `RGWBucketSyncPolicyHandlerRef`.

## State and Persistence Behavior

This file does not own durable state, but several calls mutate RGW metadata. `RGWUserAdminOp_User::create()` persists user info, keys, caps, suspension/system flags, max-bucket limits, and optional quota records. `RGWLC::set_bucket_config()` persists lifecycle config against bucket metadata and lifecycle infrastructure. The get-info, load-bucket, and sync-policy handler calls only read cluster metadata into coroutine result objects.

## Dependencies and Integration Points

The implementation depends on `RGWStore`/RADOS store access from `rgw_cr_rados.h`, user admin operation state from `rgw_user.h` and `rgw_op.h`, bucket loading through SAL, lifecycle service `RGWLC`, zone/bucket sync services, and Ceph logging/error helpers. Callers are other RGW coroutine flows that need a coroutine object instead of directly invoking admin or service APIs; sync policy use is visible in data sync and bilog trimming code.

## Risks and Edge Cases

`params.key_type` treats only the literal `"swift"` as Swift and defaults every other non-empty value to S3, so invalid strings are not rejected here. The default max-buckets config is read as `int64_t` and stored as `int32_t`, which relies on configured values fitting the narrower type. User creation applies quota defaults only when the corresponding config values are non-negative. In lifecycle setup, negative `set_bucket_config()` results are logged, but the code returns `-ret`; because Ceph APIs conventionally return negative errno values, this can flip an error into a positive value. `params.bucket` is a raw pointer and must remain valid for the coroutine call. These helpers use `null_yield`, so they are not passing an external yield context into the underlying operations.

## Test Signals

Useful coverage includes user creation with generated and supplied keys, Swift key type, invalid key-type strings, explicit and default max-bucket limits, quota defaults enabled/disabled, exclusive create conflicts, user-info miss/hit paths, tenant-qualified bucket loading, lifecycle service missing, lifecycle set failures preserving expected error sign, and sync policy retrieval for zone-scoped, bucket-scoped, and global calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_tools.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_tools.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_tools.h

## Purpose

Declares a compact set of typed coroutine request/result wrappers for RGW RADOS control-plane operations. The header gives coroutine code strongly typed parameter structs while delegating scheduling and result storage to `RGWSimpleAsyncCR` and `RGWSimpleWriteOnlyAsyncCR`.

## Important APIs, Types, and Functions

`rgw_user_create_params` carries user identity, display/email fields, access/secret key material, key type, caps, generated-key, suspension, max-bucket, system, exclusive, and quota flags. `RGWUserCreateCR` is a write-only coroutine alias over those params. `rgw_get_user_info_params` and `RGWGetUserInfoCR` return `RGWUserInfo`. `rgw_get_bucket_info_params`, `rgw_get_bucket_info_result`, and `RGWGetBucketInfoCR` return a `std::unique_ptr<rgw::sal::Bucket>`. `rgw_bucket_lifecycle_config_params` and `RGWBucketLifecycleConfigCR` pass a bucket pointer, attrs, and lifecycle config for mutation. `rgw_bucket_get_sync_policy_params`, `rgw_bucket_get_sync_policy_result`, and `RGWBucketGetSyncPolicyHandlerCR` wrap bucket sync policy lookup.

## Control Flow and Data Flow

The header itself contains no executable flow. Each alias instantiates the generic simple coroutine framework with a params type and, for read-style calls, a result type. Callers construct the coroutine with an async processor and params; the `.cc` file then specializes the request send path to translate those params into RGW service calls.

## State and Persistence Behavior

All structs are in-memory request/result carriers. Persistent behavior is controlled by the implementations: user creation and lifecycle config mutate RGW metadata, while user-info, bucket-info, and sync-policy coroutines populate result structs. Ownership is explicit for bucket lookup results through `unique_ptr`; lifecycle input uses a borrowed `rgw::sal::Bucket*`.

## Dependencies and Integration Points

The header depends on `rgw_cr_rados.h` for coroutine templates, `rgw_tools.h` and `rgw_lc.h` for RGW utility and lifecycle types, and `services/svc_bucket_sync.h` for `RGWBucketSyncPolicyHandlerRef`. It is included by coroutine-oriented RGW RADOS code and is used by sync-related components such as bilog trimming and data sync when they need bucket sync policy handlers.

## Risks and Edge Cases

Defaults in `rgw_user_create_params` are behaviorally significant: keys are generated by default, users are not suspended/system users by default, quota defaults are applied by default, and creation is non-exclusive unless requested. `key_type` is represented as a free-form string instead of an enum, leaving validation to implementation or callers. `max_buckets` is optional and falls back to cluster config. The lifecycle params store a raw bucket pointer, so object lifetime must cover coroutine execution. Result structs rely on the generic coroutine framework allocating and exposing result storage before `_send_request()` runs.

## Test Signals

Compile-time tests should instantiate every alias and verify expected result ownership types. Runtime tests should exercise default param behavior, explicit overrides, optional zone/bucket sync policy combinations, missing bucket/user results, lifecycle config writes with valid attrs, and pointer lifetime assumptions for lifecycle bucket inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_tools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_d3n_datacache.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_d3n_datacache.cc

## Purpose

Implements the local L1 data-cache backing store for RGW D3N. The cache writes whole RADOS object chunks to files under a configured persistent path, tracks cached chunks in memory, services cache-hit reads through `D3nL1CacheRequest`/AIO integration, and evicts cached files by LRU or random policy when configured capacity is exhausted.

## Important APIs, Types, and Functions

`D3nCacheAioWriteRequest::d3n_libaio_prepare_write_op()` prepares an async file write by opening the digest-named cache file, allocating a copy of the bufferlist data, and filling an `aiocb`. `D3nDataCache::init()` initializes capacity, path, eviction policy, optional startup directory eviction, directory creation/permissions, and libaio tuning. `d3n_io_write()` provides a synchronous file-write path and inserts a cache-map entry. `d3n_libaio_create_write_request()` submits async writes, `d3n_libaio_write_cb()` bridges SIGEV_THREAD completion into the cache object, and `d3n_libaio_write_completion_cb()` records the completed chunk and updates capacity/LRU state. `put()` deduplicates writes, evicts as needed, and starts async population. `get()` validates a cache-map entry against an on-disk file of the requested length and refreshes its LRU position. `random_eviction()` and `lru_eviction()` remove entries and delete backing files.

## Control Flow and Data Flow

Initialization normalizes `rgw_d3n_l1_datacache_persistent_path` to a trailing slash, optionally removes existing directory contents when `rgw_d3n_l1_evict_cache_on_start` is enabled, creates the directory when absent, and maps `rgw_d3n_l1_eviction_policy` to LRU or random. Cache population starts in `put()`: the RADOS object id is hashed with `D3nL1CacheRequest::generate_oid_digest()`, existing cached/outstanding writes are skipped, capacity is checked against `free_data_cache_size - outstanding_write_size + freed_size`, and evictions run until enough room appears. The async write request owns a copied buffer; completion erases the outstanding marker, allocates `D3nChunkDataInfo`, inserts it into `d3n_cache_map`, subtracts bytes from free capacity, subtracts bytes from outstanding size, inserts the chunk at the LRU head, and deletes the request object. Reads call `get()` with the original RADOS oid and requested length; a hit requires an in-memory map entry plus an on-disk file whose `stat()` size exactly matches the requested length.

## State and Persistence Behavior

Durable cache contents are plain files named by digest under `cache_location`. They are persistent across daemon restart only as files; the in-memory index is not rebuilt from disk during `init()`, so old files are either removed at startup when configured or left orphaned until external cleanup. Runtime state includes `d3n_cache_map`, `d3n_outstanding_write_list`, two mutexes, `free_data_cache_size`, `outstanding_write_size`, and the LRU `head`/`tail` chain. The destructor repeatedly calls `lru_eviction()` until no LRU entries remain, deleting known cache files and metadata but not scanning for orphan files.

## Dependencies and Integration Points

This implementation depends on POSIX file APIs (`open`, `fopen`, `fwrite`, `aio_write`, `stat`, `remove`, `posix_fadvise`), C++ filesystem APIs, Ceph config/logging, `bufferlist`, `D3nL1CacheRequest`, and `rgw_d3n_datacache.h`. The cache object is allocated from `RGWRados::init_rados()` when `use_datacache` is set. D3N store selection happens in `rgw_sal.cc` when `rgw_d3n_l1_local_datacache_enabled` is true, the max chunk size equals object stripe size, and Beast async/yield support is enabled. Cache writes are triggered from `get_obj_data::flush()` after RADOS read completion when the result is at most `rgw_get_obj_max_req_size` and no bypass flag was set. Cache reads are dispatched through `rgw::Aio::d3n_cache_op()`.

## Risks and Edge Cases

The async write completion path does not call `aio_error()` or `aio_return()`, so failed or partial async writes may be indexed as successful. `D3nCacheAioWriteRequest` cleanup assumes `cb` is allocated and closes `fd` even when it may be `-1`; early prepare failures can leak or dereference depending on how far initialization progressed. Lock ordering is inconsistent: `get()` takes `d3n_cache_lock` then `d3n_eviction_lock`, while `lru_eviction()` takes `d3n_eviction_lock` then `d3n_cache_lock`, creating a deadlock risk. `random_eviction()` removes map entries without updating the LRU chain, so later LRU operations can see stale pointers after random eviction. Empty-cache `random_eviction()` returns `size_t(-1)`, but `put()` only treats zero as eviction failure. Existing persistent files are not indexed on startup. File paths are digest-derived but still share one flat directory, so very large caches can stress directory operations. There is no checksum validation beyond size match, so stale or corrupted local files can be served if the digest name and length match.

## Test Signals

Tests should cover directory creation and startup eviction, invalid or unwritable cache path handling, LRU and random eviction under capacity pressure, capacity accounting with outstanding writes, duplicate `put()` suppression, cache-hit read only after async completion, stale file size mismatch removal, partial/failed `aio_write()` behavior, concurrent `get()` plus eviction lock ordering, random eviction followed by LRU destruction, restart behavior with orphan persistent files, and integration reads for full uncompressed/unencrypted chunks versus bypassed partial, compressed, or encrypted reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_d3n_datacache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_d3n_datacache.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_d3n_datacache.h

## Purpose

Declares the D3N RGW data-cache structures and the `D3nRGWDataCache<T>` wrapper that overrides RADOS object-iteration reads to consult the local file cache. It is both the cache object's public contract and the template hook that changes RGW read behavior when the D3N backend is selected.

## Important APIs, Types, and Functions

`D3nChunkDataInfo` describes one cached chunk: Ceph context, size, access time, address, digest oid, completion flag, and LRU links. `D3nCacheAioWriteRequest` owns a pending file write (`oid`, copied data buffer, file descriptor, `aiocb`, back-pointer to `D3nDataCache`, and context). `D3nDataCache` declares cache maps, outstanding write tracking, locks, capacity counters, cache path, `get()`, `put()`, sync and async write helpers, completion callback, eviction functions, `init()`, and inline LRU list operations. `D3nRGWDataCache<T>` derives from an RGW RADOS implementation and overrides `get_obj_iterate_cb()` while leaving `init_rados()` as a pass-through.

## Control Flow and Data Flow

The template `get_obj_iterate_cb()` preserves the normal head-object flow: it applies the atomic test, serves inline head data from `astate->data` when possible, and otherwise schedules a normal librados read. For non-head objects, it builds a librados read op and obtains a RADOS ref. It bypasses cache population when the read is not from offset zero, when logical size differs from accounted size, or when compression/encryption attrs are present. If the read is cacheable, it calls `d->rgwrados->d3n_data_cache->get(oid, len)`. A hit schedules `rgw::Aio::d3n_cache_op()` so data is read from the local cache file; a miss schedules a normal librados read, after which `get_obj_data::flush()` can populate the cache.

## State and Persistence Behavior

The header declares in-memory cache ownership and intrusive LRU list state. `D3nDataCache` owns `D3nChunkDataInfo` entries and deletes them through eviction/destruction. `D3nCacheAioWriteRequest` owns allocated write buffers and the `aiocb`. File persistence is implemented in the `.cc` file; the header exposes `cache_location` so AIO read code can locate digest-named files.

## Dependencies and Integration Points

The header depends on `rgw_rados.h`, curl headers indirectly used by RGW, POSIX signal/unistd headers, Ceph context and LRU helpers, `rgw_common.h`, and `rgw_d3n_cacherequest.h`. It integrates with `get_obj_data`, `RGWObjState`, `rgw_get_rados_ref()`, `librados::ObjectReadOperation`, `rgw::Aio::librados_op()`, `rgw::Aio::d3n_cache_op()`, and object attrs `RGW_ATTR_COMPRESSION` and `RGW_ATTR_CRYPT_MODE`. `rgw_sal.cc` instantiates `D3nRGWDataCache<RGWRados>` for the `"d3n"` store path.

## Risks and Edge Cases

`get_obj_iterate_cb()` dereferences `astate` in the non-head path to inspect attrs and sizes, so callers must supply valid object state. Cacheability is intentionally narrow: only full, offset-zero, uncompressed, unencrypted non-head chunks are eligible. The cache hit path trusts `D3nDataCache::get()` to validate local file presence and length, but not content integrity. The inline LRU helpers are not internally synchronized and must be called under the correct lock. `D3nChunkDataInfo::dump()` and `D3nDataCache::add_io()` are declared here but not implemented in the paired `.cc`, indicating either dead declarations or implementations elsewhere; they should be checked during build/link changes. `D3nCacheAioWriteRequest` destructor assumes `cb` is non-null and resets `cb->aio_buf`, so partially constructed request cleanup is fragile.

## Test Signals

Read-path tests should cover head-object inline data, head-object RADOS fallback, non-head cache miss and later population, non-head cache hit through `d3n_cache_op`, bypass for partial reads, size/accounted-size mismatch, compression attrs, encryption attrs, RADOS ref failures, `flush()` errors after cache reads, and ordering through AIO ids based on logical object offset. Cache-structure tests should validate LRU head/tail operations, destructor eviction, async request cleanup, and build/link coverage for declared helper methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_d3n_datacache.h -->
