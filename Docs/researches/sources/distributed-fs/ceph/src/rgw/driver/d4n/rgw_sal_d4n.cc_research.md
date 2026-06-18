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
