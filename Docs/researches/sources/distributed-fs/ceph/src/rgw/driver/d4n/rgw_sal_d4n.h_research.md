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
