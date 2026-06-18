# Research: subset-b-006957

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/rgw_sal_d4n.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/d4n/rgw_sal_d4n.cc

## Purpose

`rgw_sal_d4n.cc` implements the D4N Storage Abstraction Layer filter for RGW. It wraps another `rgw::sal::Driver` and intercepts bucket, object, read, write, delete, copy, and multipart-complete operations so RGW can use a local SSD cache plus Redis-backed D4N directories before falling back to the underlying store.

The implementation has two cache modes. Read-cache behavior caches object heads and data blocks fetched from the backend and maintains Redis block/object/bucket directory entries for later hits. Write-cache behavior writes data and head metadata into the cache as dirty entries, records dirty-object state through the policy driver, and defers backend persistence to D4N recovery/flush mechanisms outside this file. The filter also honors cache-only requests indicated through the filter object/bucket state, returning `-ENOENT` or `-EINVAL` instead of silently using the backend when the request is meant to target only cache contents.

## Important APIs and Functions

`D4NFilterDriver::initialize()` creates the Redis connection, `ObjectDirectory`, `BlockDirectory`, `BucketDirectory`, LFUDA `PolicyDriver`, SSD cache driver, and optional Redis connection pool. It parses `rgw_d4n_address`, starts `boost::redis::connection::async_run()`, initializes the next driver, initializes the SSD driver, and calls the cache policy init with the wrapped backend driver.

`D4NFilterDriver::get_user()`, `get_bucket()`, `load_bucket()`, `get_object()`, and `get_atomic_writer()` are the wrapping entry points. They return `D4NFilterUser`, `D4NFilterBucket`, `D4NFilterObject`, and `D4NFilterWriter` wrappers around the next SAL object. `shutdown()` cancels the Redis connection executor, releases cache/directory/policy objects, then shuts down the next driver.

`D4NFilterBucket::list()` merges D4N cached listing state with backend listing state. When `d4n_writecache_enabled` is true, it scans Redis bucket sorted sets through `BucketDirectory::zscan()` or `zrange()`, resolves versions through `ObjectDirectory::zrevrange()`/`zrank()`, fetches head blocks through `BlockDirectory::get()`, builds `rgw_bucket_dir_entry` values marked with storage class `CACHE`, then either returns cache-only results or merges them with `next->list()`.

`D4NFilterBucket::remove()` lists all versions with `return_blocks` enabled, deletes cached head/version/data directory entries in pipelined batches, invalidates dirty objects through the policy driver, removes object and bucket sorted-set entries, and finally delegates bucket removal to the backend. `check_empty()` treats any bucket-directory presence as non-empty before asking the backend.

`D4NFilterObject::get_obj_attrs_from_cache()`, `check_head_exists_in_cache_get_oid()`, and `get_obj_attrs()` are the head-object cache path. They use block directory entries to locate a cached head, increment/decrement policy refcounts around SSD cache attribute reads, translate D4N cache xattrs such as mtime, object size, epoch, version id, source zone, multipart flag, namespace, bucket name, and dirty flag into SAL object state, and cache backend head attrs on a miss.

`D4NFilterObject::set_attrs_from_obj_state()`, `calculate_version()`, `set_attr_crypt_parts()`, `set_head_obj_dir_entry()`, and `set_data_block_dir_entries()` encode RGW object state into D4N metadata. `set_head_obj_dir_entry()` is central: it writes latest, null-version, and version-specific Redis block entries depending on bucket versioning and dirty/clean state, updates object-version sorted sets, and updates bucket listing sorted sets.

`D4NFilterObject::D4NFilterReadOp` implements read-through caching. `prepare()` validates conditional headers against cached attrs on hits or prepares the backend and caches the head on misses. `iterate()` aligns requested ranges to `rgw_max_chunk_size`, tries cached data blocks through the policy/cache driver, checks Redis directory versions and host lists, drains already-issued async reads, and falls back to backend iteration with `D4NFilterGetCB`. `flush()` orders async cache read results, sends data to the client callback, decrements refcounts, and can populate copy destination cache blocks.

`D4NFilterObject::D4NFilterReadOp::D4NFilterGetCB::handle_data()` is the backend-read callback. It trims ranged responses before sending to the client, accumulates backend data into `rgw_max_chunk_size` chunks, calls policy eviction, writes SSD cache entries, and batch-updates block directory entries for source and copy-destination objects when `flush_last_part()` marks the stream complete.

`D4NFilterObject::D4NFilterDeleteOp::delete_obj()` implements cache-aware delete semantics. It distinguishes absent heads, cached delete markers, dirty versus clean cached objects, versioned versus non-versioned buckets, simple deletes versus version-id deletes, cache-only requests, and backend delegation. Dirty versioned simple deletes create a cached delete marker; version-id deletes can promote the second-latest Redis version entry to latest; clean deletes generally remove D4N metadata/cache state then delegate to the backend.

`D4NFilterWriter::prepare()`, `process()`, and `complete()` implement write-cache and read-cache write-through behavior. In write-cache mode, `process()` writes chunks directly to the cache and marks them dirty; `complete()` evaluates conditional headers, records block directory entries, writes a cached head object, updates dirty-object tracking, and invalidates a previous dirty head for overwrite cases. When write-cache is disabled, writes go to `next`, but the completed head is still cached as clean metadata.

`D4NFilterObject::copy_object()` and `D4NFilterMultipartUpload::complete()` handle higher-level object operations. Copy can route multipart/read-only cases to the backend but otherwise reads source data through the filter and populates destination cache state. Multipart completion delegates full assembly to the backend and caches only the completed head with a multipart marker.

The C ABI factory `newD4NFilter()` constructs a `D4NFilterDriver` from an existing next driver and a `boost::asio::io_context`.

## Control Flow

Initialization flows from `newD4NFilter()` to the constructor and `initialize()`. The constructor sets up the SSD cache partition from `rgw_d4n_l1_datacache_persistent_path` and `rgw_d4n_l1_datacache_disk_reserve`. `initialize()` wires the async Redis connection and directory/policy/cache objects before normal RGW SAL operations begin. All subsequent operations pass through wrapper objects and either use D4N state or delegate to the next SAL driver.

Read flow first loads/caches head metadata. `prepare()` calls `get_obj_attrs_from_cache()`. On a head hit, it validates multipart/part-number behavior, conditional time/etag headers, and returns without opening the backend except for multipart cases that require backend part layout. On a miss, it prepares the backend read, loads object state, calculates a version, writes an empty head cache entry with attrs, updates the policy, and records the head in Redis directories.

Data read flow is chunk-oriented. `iterate()` expands requested ranges to cache chunk boundaries, checks policy key existence and refcounts for each data block key, issues cache async reads when available, and flushes in offset order. If a block is missing, version-mismatched, or only known on remote hosts, it drains prior cache reads and falls back to backend iteration for the remaining aligned range. Backend callback data is both forwarded to RGW and written into the local cache, with block directory entries written at end-of-stream.

Write flow depends on `d4n_writecache_enabled`. In write-cache mode, `prepare()` chooses/generates the version and may locate a previous dirty head for invalidation. `process()` writes data chunks to SSD cache and policy metadata with dirty state. `complete()` performs conditional request checks against current attrs, cleans up newly written cache blocks on precondition failure, writes block-directory entries, writes head attrs, updates Redis latest/null/version entries, and records the dirty object in policy state. With write-cache disabled, `prepare()`/`process()`/`complete()` delegate the data write to the backend and then cache a clean head.

Delete flow first resolves the cached head. If there is no D4N head and no delete marker, cache-only requests fail and normal requests delegate to the backend. If a D4N head exists, clean cached entries remove local D4N metadata/cache state and then call backend delete unless cache-only. Dirty entries are handled in D4N state: non-versioned deletes remove latest/null heads and sorted-set entries; versioned simple deletes add a dirty delete marker; version-id deletes remove version entries and may promote another version as latest.

Bucket listing flow builds a cache-side list only when write-cache is enabled because dirty cached objects must be visible to list operations. It handles prefix scans, delimiter common prefixes, version listing, markers, and truncation markers, then merges sorted cache and backend objects while preferring cache entries when names match.

## State and Persistence Behavior

Persistent/local cache data is split across the SSD cache driver and Redis directory/policy state. SSD cache keys are built from URL-encoded bucket id, version, object name, optional block offset, and block length. Head entries use the cache block prefix without offset/length and carry attrs only. Data entries store object bytes and generally have empty attrs except dirty markers set for write-cache data blocks.

Redis `BlockDirectory` stores `CacheBlock` records for heads and data blocks. Head records use latest object names, explicit `_:null_` names for null versions, or `get_oid()` names for version-specific entries. Data records use object oid, block id, size, version, dirty flag, and host list. `ObjectDirectory` keeps ordered sets of versions per object, with scores based on mtime for dirty entries. `BucketDirectory` keeps sorted object names per bucket for listing dirty/cache-visible entries.

Version state is synthetic for non-versioned objects. The code uses backend instance ids when present, `"null"` for suspended/non-versioned semantics, and randomly generated 32-character alphanumeric strings for cache-only non-versioned dirty versions. `calculate_version()` can use `RGW_ATTR_ID_TAG` for non-versioned backend objects. Correct use of the object version is critical because it is embedded in cache keys and directory entries.

Dirty state is persisted in D4N policy metadata and cache attrs. Dirty object heads carry `RGW_CACHE_ATTR_DIRTY`, policy `update_dirty_object()` records bucket/user/etag/size/mtime/object key, and delete markers are represented as zero-size dirty head entries with `RGW_CACHE_ATTR_DELETE_MARKER`. Clean cache entries can be lazily evicted; dirty entries must be invalidated or flushed by D4N policy mechanisms.

The filter stores some per-object process-local state: `version`, `prefix`, `dest_object`, `dest_bucket`, `multipart`, `delete_marker`, `exists_in_cache`, `load_from_store`, `attrs_read_from_cache`, and `cache_request`. `D4NFilterReadOp` stores async throttle state, ordered completed read results, current output offset, and `blocks_info` for refcount cleanup. These values are not durable and must be rebuilt per operation.

## Dependencies and Integration Points

This file depends on RGW SAL filter classes, RGW object/bucket/user abstractions, `rgw_aio_throttle`, D4N Redis directory classes, D4N cache policy, SSD cache driver, Redis connection/pool support, Ceph bufferlists and attrs, RGW ACL decoding, RGW perf counters, and global RGW configuration. It uses `g_conf()`/`dpp->get_cct()->_conf` for D4N address, Redis pool size, local RGW address, cache path/reserve, max chunk size, get-object window size, and write-cache enablement.

The integration boundary with the wrapped backend is explicit through `next`. Backend operations still provide authoritative data for misses, multipart assembly, read-only writes, clean deletes, bucket creation, and fallback list results. D4N therefore acts as a coherent filter rather than a standalone store.

The Redis/directory integration is performance- and correctness-critical. `Pipeline` is used for some multi-command head/listing updates, while other sequences are individual calls. The policy driver mediates cache eviction, key existence, refcounts, read/write update timestamps, dirty-object tracking, and dirty invalidation. The SSD driver stores actual cached bytes and attrs.

RGW request semantics are preserved by reimplementing conditional header checks, versioning rules, delete markers, multipart part-number handling, ACL owner extraction, object lock attrs passed through writer complete, and list delimiter/marker behavior. Any divergence here can surface as S3 API incompatibility even if cache storage itself works.

## Risks and Edge Cases

The most important risk is divergence between Redis directories, SSD cache keys, policy metadata, and backend object state. Many operations update several systems without a single transaction. Comments in the code call out cleanup/revert gaps after cache writes and directory failures. A failed `put()` after directory changes, a failed directory `set()` after SSD writes, or a process crash mid-update can leave stale or orphaned cache state.

Versioning semantics are complex and high risk. The code special-cases latest heads, `_:null_` entries, versioned bucket entries, suspended versioning, delete markers, and simple versus version-id deletes. Bugs can make stale dirty data visible, hide backend versions, create incorrect list markers, or promote the wrong version after delete.

The listing implementation depends on Redis sorted-set scan/range behavior, string ordering, marker comparisons, and ad hoc escaping for object names beginning with `_`. There are several subtle truncation paths, especially with delimiters, prefix scans, and `list_versions`. Tests should target marker continuation and duplicate suppression between cache and backend results.

Refcount handling is fragile. Reads increment policy refcounts before cache reads and decrement in `flush()`/`drain()`. Errors in callback handling, early returns, missing `aio` initialization, or unmatched entries in `blocks_info` can leak refcounts or allow eviction of in-flight blocks.

Cache-only request behavior must remain strict. Some paths return `-ENOENT`, others `-EINVAL`, and delete/cache cleanup paths may delete local cache data without backend involvement. API callers need consistent mapping between the custom cache request header and SAL behavior.

There are visible bug-prone idioms. Some error checks use assignment mixed with comparison, such as `if ((ret = blockDir->del(dpp, blocks, y) < 0))`, which assigns a boolean result rather than the real return code. Several paths log failures but continue, and some Redis transaction retry comments mention watched keys without an obvious transaction wrapper in this file. The code also relies on `dynamic_cast` to D4N wrapper types for destination objects and buckets.

Remote-cache support is incomplete. Data-block directory host lists can show remote copies, but `iterate()` only logs TODOs for remote retrieval and falls back to backend when no local host remains. Delete has a TODO for sending delete requests to remote cache nodes.

## Test Signals

High-value tests should exercise D4N initialization failures for malformed `rgw_d4n_address`, Redis connection pool configuration, and shutdown cleanup. Unit tests or integration tests should validate cache key construction, head attr encode/decode, version calculation, dirty-object metadata, and policy refcount update symmetry.

Read tests should cover head hit, head miss, data block hit, partial block hit followed by backend fallback, ranged reads crossing chunk boundaries, zero-size objects, conditional headers, multipart `partNumber`, encrypted object crypt-parts attrs, and cache-only misses. Tests should assert perf counter hit/miss increments where available.

Write tests should cover write-cache enabled and disabled modes, overwrite invalidation of prior dirty entries, precondition failure cleanup, suspended versioning, non-versioned `"null"` behavior, versioned writes, object-lock retention attrs, and failures in cache put/policy eviction/directory set. Copy-object tests should cover cache-destination population and multipart fallback.

Delete tests should cover clean cached deletes with backend delegation, dirty non-versioned deletes, dirty versioned simple deletes producing delete markers, version-id deletes promoting a previous version, cache-only deletes, delete marker reads, and data-block directory/cache cleanup. Bucket tests should cover cache-only list, merged cache/backend list, prefix/delimiter/list-versions markers, bucket removal with dirty objects, and `check_empty()` when only D4N cache entries exist.

The strongest regression suite would run RGW S3 semantics against a real Redis plus SSD cache path with forced fault injection between SSD, policy, and directory updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/rgw_sal_d4n.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/rgw_sal_d4n.h -->
# sources/distributed-fs/ceph/src/rgw/driver/d4n/rgw_sal_d4n.h

## Purpose

`rgw_sal_d4n.h` declares the D4N RGW SAL filter classes. The filter wraps an existing RGW `Driver`, `User`, `Bucket`, `Object`, `Writer`, and `MultipartUpload` so D4N can add cache/directory behavior while preserving the standard SAL interface expected by RGW operations.

The header is the contract for the implementation in `rgw_sal_d4n.cc`. It exposes D4N-specific driver accessors, object cache state helpers, writer and multipart wrappers, and two inline cache-key helpers used to keep head and data block keys consistent.

## Important APIs and Types

`get_cache_block_prefix(Object* object, const std::string& version)` builds the base cache key from URL-encoded bucket id, version, and object name separated by `CACHE_DELIM`. `get_key_in_cache(prefix, offset, len)` extends that prefix with data-block offset and length. These helpers encode the cache namespace used by the D4N implementation and policy driver.

`D4NFilterDriver` derives from `FilterDriver`. Its private state owns the Redis connection, SSD `CacheDriver`, D4N `ObjectDirectory`, `BlockDirectory`, `BucketDirectory`, `PolicyDriver`, an `io_context` reference, saved yield context, and optional `RedisPool`. Its public overrides cover initialization, user/bucket/object wrapping, bucket loading, atomic writer creation, and shutdown. Accessors expose the cache, directories, policy, Redis connection, and pool to wrapped buckets/objects/writers.

`D4NFilterUser` is a thin `FilterUser` wrapper. It stores a `D4NFilterDriver*` but does not declare additional user overrides in this header.

`D4NFilterBucket` derives from `FilterBucket`. It stores the D4N driver pointer, cache-only request state, a flag requesting block-directory capture during listing, and a `dir_blocks` map used during bucket removal. It overrides object construction, listing, removal, creation, emptiness checks, and multipart upload creation. `set_cache_request()` marks bucket operations as cache-only.

`D4NFilterObject` derives from `FilterObject`. It stores driver linkage and D4N object-operation state: cache version, cache prefix, backend `rgw_obj`, copy destination object/bucket, multipart/delete-marker booleans, cache existence/load flags, attr cache-read flag, and cache-only request flag. It overrides copy, state loading, attr mutation, attr fetching, read/delete op creation, existence, and mtime/name access. It also declares D4N helper methods for cache attrs, version calculation, directory updates, delete markers, cache deletion, and copy destination access.

`D4NFilterObject::D4NFilterReadOp` derives from `FilterReadOp`. It contains nested `D4NFilterGetCB`, which derives from `RGWGetDataCB` and mediates backend-read callback data so it can be sent to the client and written to D4N cache blocks. The read op tracks the source object, client callback, D4N callback, AIO throttle, completed cache reads, output offset, and block offset/length metadata for refcount cleanup. It overrides `prepare()`, `iterate()`, and `get_attr()`.

`D4NFilterObject::D4NFilterDeleteOp` derives from `FilterDeleteOp` and overrides `delete_obj()` so object deletes can be served from or applied to D4N state before delegating to the backend.

`D4NFilterWriter` derives from `FilterWriter`. It stores driver/object pointers, the request `DoutPrefixProvider`, atomic writer flag, yield context, write-cache mode, current D4N version, and previous cached head key. It overrides `prepare()`, `process()`, and `complete()`, and provides `is_atomic()`, `get_dpp()`, and `set_cache_request()`.

`D4NFilterMultipartUpload` derives from `FilterMultipartUpload` and overrides `complete()` to cache completed multipart head metadata after backend multipart completion.

## Control Flow and Integration

The driver is the root wrapper. RGW loads the filter through the factory in the `.cc` file, calls `initialize()`, then receives wrapper objects from normal SAL factory methods. Every wrapper retains a pointer back to `D4NFilterDriver`, allowing bucket/object/writer code to access shared cache and directory state without extending the generic SAL interfaces.

Bucket operations use `D4NFilterBucket` to wrap objects and multipart uploads, making object-level reads/writes/deletes D4N-aware even when constructed from a bucket. Bucket list and remove are declared as full overrides because cache-visible dirty objects affect bucket contents independently of the backend.

Object operations are split between public SAL overrides and D4N helper APIs. Public overrides preserve RGW dispatch compatibility. Helper APIs express the internal D4N lifecycle: discover cached head, populate object state from attrs, calculate cache version, create/delete metadata entries, update data-block directories, and delete cache entries.

Read operations are wrapped one level deeper. `D4NFilterObject::get_read_op()` returns `D4NFilterReadOp`, which itself contains a callback wrapper for backend data. This gives the filter control both before a read starts and as backend data streams through RGW post-processing.

Writer operations similarly wrap the backend writer. The header keeps writer construction tied to an existing `Writer` from `next`, so D4N can either delegate to the backend or write data into cache depending on runtime configuration.

## State and Persistence Behavior

The header defines process-local ownership and references, not durable state itself. Durable D4N state lives behind the declared `CacheDriver`, Redis directories, and `PolicyDriver`. The shape of in-memory state still matters because it determines how one SAL operation carries cache context across subcalls.

`D4NFilterDriver` owns cache/directory/policy objects for the process lifetime. Buckets, objects, read ops, delete ops, writers, and multipart wrappers hold raw driver pointers and therefore depend on driver lifetime outliving active operations.

`D4NFilterObject` carries per-operation and per-object wrapper state. `version` and `prefix` connect head operations with data-block operations. `dest_object`/`dest_bucket` let copy-object reads fill destination cache state. `multipart` alters read and copy behavior because multipart object data is generally read from the backend while only the head is cached. `delete_marker`, `exists_in_cache`, `load_from_store`, `attrs_read_from_cache`, and `cache_request` alter fallback semantics.

`D4NFilterReadOp` state tracks async cache reads and cache-policy refcount cleanup. `blocks_info` maps output ids to cache block offsets and lengths, allowing `flush()` and `drain()` to update policy state after cache reads complete.

## Dependencies and Integration Points

The header depends on RGW SAL base and filter interfaces, RGW roles, dout logging, AIO throttling, SSD and Redis cache drivers, D4N directory and policy APIs, Boost.Asio, Boost.Redis, and `fmt`. It uses `boost::redis::connection` directly and exposes it through the driver, binding D4N to Redis as the directory/control plane.

The filter integrates with RGW through standard virtual methods rather than new external APIs. This is important because S3 operations, admin operations, and backend drivers interact with it as a normal SAL implementation. Cache-only behavior is exposed internally through `set_cache_request()` on bucket/object/writer wrappers and is expected to be triggered by request handling code outside this header.

The cache-key helpers integrate with constants from D4N cache/directory headers, especially `CACHE_DELIM`, and with RGW URL encoding. Any caller constructing keys must use these helpers or exactly preserve their format to avoid orphaning cache blocks.

## Risks and Edge Cases

Raw driver pointers in wrappers make lifetime ordering important. Active read callbacks, writers, or multipart wrappers must not outlive `D4NFilterDriver::shutdown()` because the driver resets cache and directory objects.

The header exposes many mutable object flags through simple setters/getters. The correctness of cache-only requests, backend fallback, version selection, and copy-object behavior depends on callers setting these flags in the right order. There is no type-level distinction between clean cached objects, dirty cached objects, delete markers, cache-only requests, and backend-loaded objects.

The cache key format encodes bucket id, version, name, offset, and length as strings. Changes to URL encoding, delimiter rules, or version generation affect compatibility with already persisted cache entries. Object names beginning with `_` receive special handling in the `.cc` file, so tests should include names that stress that convention.

`D4NFilterGetCB` stores a pointer to an `optional_yield` rather than owning one. Callback lifetime and sequencing must ensure the pointed-to yield remains valid while backend data is handled.

Several wrapper constructors use `static_cast` or expect that the wrapped `Object*` is actually a `D4NFilterObject`. Incorrect construction through a non-D4N path could cause invalid casts or lost cache behavior.

## Test Signals

Header-level tests should focus on integration behavior visible through the declared interfaces: wrapping returns D4N-specific buckets/objects/writers, cache-key helpers produce stable escaped keys, cache-only flags propagate to object/writer behavior, and driver accessors return initialized cache/directory/policy objects.

Compile-time and ABI checks should catch signature drift against RGW SAL virtual interfaces, especially `copy_object()`, `complete()` for writers and multipart uploads, read/delete op methods, and `get_atomic_writer()`. Runtime tests should exercise wrapper lifetime through shutdown while no active operations remain.

Behavioral coverage belongs mostly to `rgw_sal_d4n.cc`, but cases should be designed around the state fields declared here: versioned/non-versioned objects, delete markers, copy destinations, multipart heads, `load_from_store`, `attrs_read_from_cache`, and `cache_request`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/d4n/rgw_sal_d4n.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/daos/rgw_sal_daos.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/daos/rgw_sal_daos.cc

## Purpose

`rgw_sal_daos.cc` implements an RGW SAL backend for DAOS/CORTX DS3. It maps RGW users, buckets, objects, object metadata, multipart uploads, and basic placement/zone abstractions onto the `ds3_*` C API. The file is explicitly a partial backend: basic user/bucket/object/multipart paths are implemented, while many RGW features return `DAOS_NOT_IMPLEMENTED_LOG()`.

The code acts as a bridge between Ceph RGW's SAL contracts and DS3 handles. It serializes Ceph metadata such as `RGWUserInfo`, `RGWBucketInfo`, `rgw_bucket_dir_entry`, attrs maps, object versions, multipart upload info, and compression metadata into DS3 user, bucket, object, upload, and part info buffers.

## Important APIs and Functions

`DaosStore::initialize()` and `finalize()` manage DS3 process and pool connectivity. Initialization calls `ds3_init()`, accepts `DER_ALREADY`, reads the `daos_pool` config value, and calls `ds3_connect()`. Finalization disconnects `ds3` and calls `ds3_fini()`.

User APIs include `DaosStore::get_user()`, `get_user_by_access_key()`, `get_user_by_email()`, `DaosUser::load_user()`, `store_user()`, `read_user()`, `get_encoded_info()`, `merge_and_store_attrs()`, `remove_user()`, and `create_bucket()`. User info is encoded into `DaosUserInfo` and persisted with `ds3_user_set()`, read with `ds3_user_get()` or indexed lookup helpers, and removed with `ds3_user_remove()`. `store_user()` performs a simple object-version check with `objv_tracker.read_version`.

Bucket APIs include `DaosStore::list_buckets()`, `load_bucket()`, `get_bucket()`, and `DaosBucket::open()`, `close()`, `get_encoded_info()`, `put_info()`, `load_bucket()`, `remove()`, `remove_bypass_gc()`, `merge_and_store_attrs()`, `set_acl()`, `get_object()`, `list()`, `list_multiparts()`, and `get_multipart_upload()`. Bucket metadata is encoded as `DaosBucketInfo` and stored via DS3 bucket info calls. Listing decodes DS3 object or multipart upload info into RGW list results.

Object metadata APIs include `DaosObject::load_obj_state()`, `set_obj_attrs()`, `get_obj_attrs()`, `modify_obj_attrs()`, `delete_obj_attrs()`, `get_dir_entry_attrs()`, `set_dir_entry_attrs()`, and `mark_as_latest()`. The backend stores RGW dir entries and attr maps in DS3 object info xattrs, decoding `rgw_bucket_dir_entry` first and optional attrs after it.

Object data APIs include `DaosObject::lookup()`, `create()`, `close()`, `write()`, `read()`, `get_read_op()`, `DaosReadOp::prepare()`, `read()`, `iterate()`, `get_attr()`, `get_delete_op()`, `DaosDeleteOp::delete_obj()`, and `delete_object()`. They open/create DS3 object handles, use `ds3_obj_read()`/`ds3_obj_write()` for byte IO, use `ds3_obj_destroy()` for deletes, and provide a synchronous read-iterate implementation that reads the requested range then calls the RGW callback once.

`DaosAtomicWriter` implements put-object writes. `prepare()` creates the object, `process()` writes incoming buffers at offsets and accumulates total bytes, and `complete()` builds a `rgw_bucket_dir_entry`, handles object-lock default retention attrs, writes encoded metadata/attrs, and calls `mark_as_latest()` for versioned buckets.

Multipart APIs include `DaosMultipartUpload::init()`, `abort()`, `get_meta_obj()`, `list_parts()`, `complete()`, `cleanup_orphaned_parts()`, `get_info()`, `get_writer()`, and `DaosMultipartWriter::prepare()`, `process()`, `complete()`. Upload init creates a DS3 upload entry with encoded dirent, attrs, and `multipart_upload_info`. Part writers write DS3 parts and store encoded `RGWUploadPartInfo` plus attrs. Completion validates part numbers, etags, sizes, and compression metadata, computes the multipart etag, creates the final object, reads each DS3 part, writes concatenated data into the final object, stores final metadata/attrs, marks latest if versioned, then removes the upload.

Zone/placement APIs are minimal. `DaosZoneGroup` resolves placement targets and tiers from in-memory zone config. `DaosZone` returns the current zonegroup/id/name and always reports writable. `DaosStore::valid_placement()` and `get_compression_type()` delegate to zone params. Role, OIDC, lifecycle, restore, sync, quota, usage, and metadata-listing APIs are mostly stubs.

The C ABI factory `newDaosStore()` constructs a `DaosStore` for RGW dynamic loading.

## Control Flow

Startup begins with RGW loading `newDaosStore()`, then calling `initialize()`. DS3 must be initialized and connected to the configured DAOS pool before users, buckets, or objects can be opened. Shutdown calls `finalize()` to disconnect and finalize DS3.

User creation/update flow reads any existing DS3 user, compares object versions, builds old access-id arrays for update semantics, encodes `DaosUserInfo`, and calls `ds3_user_set()`. Bucket creation is routed through `DaosUser::create_bucket()`: it tries `store->load_bucket()`, returns existing bucket metadata when present, or fills `RGWBucketInfo` defaults and calls `ds3_bucket_create()`.

Bucket operations open DS3 bucket handles lazily and idempotently. `load_bucket()` reads and decodes DS3 bucket info, then forces default placement to `default/STANDARD`. `list()` calls `ds3_bucket_list_obj()` with prefix, delimiter, marker, and version-listing flags, decodes entries, filters invisible entries unless listing versions, and sorts unless unordered results are allowed.

Object reads go through `DaosReadOp::prepare()` followed by `read()` or `iterate()`. For versioned buckets without an explicit version, prepare sets the object instance to `DS3_LATEST_INSTANCE`, reads metadata, populates etag attr, object key, and size. `iterate()` opens the object, reads the full requested inclusive range into a bufferlist, and hands it to the RGW callback.

Object writes go through `DaosStore::get_atomic_writer()`. `prepare()` creates the DS3 object. Each `process()` writes the provided buffer at the specified offset and adds to `total_data_size` on success. `complete()` constructs metadata and attr state, persists it with `set_dir_entry_attrs()`, and for versioned buckets updates DS3 latest linkage after downgrading the previous latest object's flags.

Multipart upload flow creates an upload index entry with a generated id, writes parts through DS3 part handles, stores part metadata at part complete, and later completes by listing and validating all parts. Unlike some backends that compose server-side references, this implementation reads every part into RGW memory buffers and writes a newly created final DS3 object sequentially.

## State and Persistence Behavior

The durable state is in DAOS/DS3. `DaosStore` holds the process `CephContext` and `ds3` connection handle. `DaosBucket` holds a DS3 bucket handle `ds3b` that is opened lazily and closed in the destructor. `DaosObject` holds a DS3 object handle `ds3o` that is opened/created lazily and closed in the destructor. Multipart writers hold DS3 part handles and close them in their destructor.

User metadata is encoded as `DaosUserInfo` into `ds3_user_info.encoded`, with access key ids separately exposed through `access_ids`. Bucket metadata is encoded as `DaosBucketInfo` into `ds3_bucket_info.encoded`. Object metadata is encoded as `rgw_bucket_dir_entry` followed by an attrs map into `ds3_object_info.encoded`. Multipart upload metadata is encoded as dirent, attrs, and `multipart_upload_info`; part metadata is encoded as `RGWUploadPartInfo` and attrs.

Versioning support is partial and DS3-specific. Versioned writes set `FLAG_VER | FLAG_CURRENT` and call `mark_as_latest()`, which opens any existing latest object, changes its flags to `FLAG_VER`, then calls `ds3_obj_mark_latest()` on the current object. If a versioned read has no instance, `DaosReadOp::prepare()` sets `DS3_LATEST_INSTANCE`. The delete path explicitly lists versioning TODOs and does not fully implement RGW delete marker semantics.

Object attrs are stored as part of DS3 object info, not separate omap entries. `set_obj_attrs()`, `modify_obj_attrs()`, and `delete_obj_attrs()` read the existing dirent/attrs, mutate the attr map, and rewrite the encoded DS3 object info. `load_obj_state()` only sets size, accounted size, mtime, existence, and etag attr from dirent metadata.

Bucket and object handles are process-local resources. `open()` and `close()` are idempotent, and destructors call close with null dpp. Most methods assume a live `store->ds3` connection and do not try to reconnect after failure.

## Dependencies and Integration Points

The implementation depends on `rgw_sal_daos.h`, Ceph encoding/bufferlist APIs, RGW bucket/object/compression helpers, RGW SAL base types, `std::filesystem` headers, and the C DS3 API: `ds3_init`, `ds3_connect`, user/bucket/object/upload/part operations, and DS3 constants such as `DS3_MAX_ENCODED_LEN`, `DS3_MAX_BUCKET_NAME`, `DS3_MAX_KEY_BUFF`, `DS3_LATEST_INSTANCE`, and multipart id prefixes.

RGW integration is through SAL virtual methods. Admin/user paths use `DaosUser`; bucket and object S3 paths use `DaosBucket`, `DaosObject`, and writer/read/delete op classes; multipart S3 paths use `DaosMultipartUpload` and `DaosMultipartWriter`; notifications return `DaosNotification`; Lua returns `DaosLuaManager`.

Placement integration is minimal and mostly in-memory. `DaosZoneGroup` and `DaosZone` rely on zone params available on the store, but multisite, sync policy, period metadata, service-map registration, lifecycle, restore, usage logging, quota, rate limiting, and metadata listing are not fully implemented.

The implementation returns DS3 error codes directly in many paths while mapping a few specific cases to RGW errors, such as multipart upload `-ENOENT` to `-ERR_NO_SUCH_UPLOAD` and invalid multipart inputs to S3-style errors. Consistent error-code translation is an integration concern.

## Risks and Edge Cases

Feature coverage is the largest risk. Many SAL methods return `DAOS_NOT_IMPLEMENTED_LOG()`, including user stats/usage, bucket stats/quota/index repair, chown, transitions/cloud restore, omap helpers, copy object, Swift versioning, roles, OIDC, append writer, lifecycle/restore, sync, metadata listing, service map, and usage logging. RGW configurations that expect these features will fail or degrade.

Delete and versioning semantics are incomplete. `DaosDeleteOp::delete_obj()` deletes a DS3 object by key and comments that versioning, delete params, empty directories, and missing-file handling are TODOs. This can diverge from S3/RGW behavior for versioned buckets, delete markers, conditional deletes, and lifecycle expiration.

Read and multipart completion are synchronous and potentially memory-heavy. `DaosReadOp::iterate()` reads the entire requested range into one bufferlist before invoking the callback. Multipart completion reads every part into memory one at a time and writes it to the final object, rather than using server-side composition or streaming callbacks. Large objects and high concurrency need stress testing.

Metadata buffer handling relies on fixed `DS3_MAX_ENCODED_LEN` buffers. Large attrs, ACLs, multipart metadata, compression metadata, or user/bucket info can exceed the fixed buffer and cause DS3 failures or truncated/undecodable metadata depending on DS3 behavior.

There are correctness issues worth inspecting. `DaosReadOp::get_attr()` returns `-ENODATA` when `get_dir_entry_attrs()` succeeds because it checks `if (!ret) return -ENODATA;`, which appears inverted. `DaosBucket::set_acl()` builds updated attrs but does not persist them with `put_info()`. `DaosBucket::merge_and_store_attrs()` calls `put_info(dpp, y, ceph::real_time())`, passing `optional_yield` where the signature's second parameter is `bool exclusive`, relying on implicit conversion or compile behavior. Some string copies use `strncpy()` without explicit null termination. `DaosMultipartWriter::complete()` checks `if (ret == ENOENT)` instead of `-ENOENT`.

Concurrency/atomicity is limited. `DaosAtomicWriter` comments that concurrent writes need unique ids or DAOS transactions. User versioning has a simple read-version check, but object writes, metadata rewrites, multipart completion, and latest-version promotion are not transactional at the RGW semantic level.

Error handling often logs and returns raw DS3 codes, but cleanup on partial multipart completion, failed final object writes, or failed metadata updates is limited. `DaosMultipartUpload::complete()` can create/write a final object before metadata or upload removal fails.

## Test Signals

Basic backend tests should cover DS3 initialization/finalization, missing or invalid `daos_pool`, user create/load/update/remove, access-key and email lookup, bucket create/load/list/remove, bucket ACL persistence expectations, and bucket list markers/prefix/delimiter/common prefixes.

Object tests should cover create/write/read/iterate/load state, attr set/modify/delete/get, etag propagation, zero-length writes, missing object lookup, fixed-buffer overflow behavior for large attrs, object expiration attr decoding, and handle idempotent open/close/destructor paths.

Versioning tests should cover versioned write/latest lookup, overwriting latest, reading explicit and latest instances, non-versioned `"null"` instance clearing, and known delete gaps. Tests should make failures explicit so unsupported versioning semantics do not appear accidentally supported.

Multipart tests should cover upload init id uniqueness, part write/complete/list, complete validation for missing parts, wrong order, etag mismatch, too-small parts, compression metadata consistency, final etag calculation, final object metadata, upload removal, abort, and error cleanup. Large multipart tests should measure memory behavior during part concatenation.

Feature-gating tests should assert expected `-ENOTSUP` or not-implemented returns for unsupported SAL methods, including quota/stats/usage, copy object, lifecycle, cloud transition, OIDC/roles, append writer, and metadata listing. Integration tests should verify RGW surfaces these failures predictably rather than crashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/daos/rgw_sal_daos.cc -->
