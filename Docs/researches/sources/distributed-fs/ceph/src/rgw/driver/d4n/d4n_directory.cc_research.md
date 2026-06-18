# sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_directory.cc

## Purpose

`d4n_directory.cc` implements the Redis-backed metadata directories used by the RGW D4N filter. The file turns `CacheObj` and `CacheBlock` records from `d4n_directory.h` into Redis hashes and sorted sets, provides optional connection-pool execution, and exposes bucket/object/block directory primitives that `rgw_sal_d4n.cc` and `d4n_policy.cc` use to find cached objects, list cache-visible bucket contents, update dirty and host metadata, and remove stale cache entries.

The implementation is not a generic Redis wrapper. It encodes D4N-specific key formats, field ordering, pipelined command behavior, and Ceph error conventions. Most methods return `0` on success, negative errno-style values on failures, and log through `ldpp_dout()`.

## Important APIs and functions

- `async_exec()` and `initiate_exec` dispatch Boost.Redis `connection::async_exec()` on the connection executor while keeping the shared connection alive through `boost::asio::consign()`.
- `redis_exec()` runs a Redis request either under an RGW `optional_yield` yield context or synchronously through `ceph::async::use_blocked`.
- `redis_exec_cp()` acquires a connection from `RedisPool`, executes the request, releases it, and rethrows after release on exceptions.
- `redis_exec_connection_pool()` chooses between a directory-specific `redis_pool` and the legacy shared connection, logging when the shared connection is used.
- `check_bool()` normalizes string boolean representations accepted by directory setters and update paths.
- `BucketDirectory` wraps bucket-level sorted-set keys. Its methods use Redis `EXISTS`, `ZADD`, `ZREM`, lexicographic `ZRANGE`, `ZSCAN`, `ZRANK`, and `UNLINK`.
- `ObjectDirectory` wraps object-level hash metadata and per-object/version sorted-set state. It implements `build_index()`, `exist_key()`, `set()`, `get()`, `copy()`, vector and single `del()`, `update_field()`, sorted-set helpers, and `incr()` for a `_versioned_epoch` key.
- `BlockDirectory` wraps cache-block hashes and block-local sorted-set helpers. It implements single and vector `set()`, single and vector `get()` variants, `copy()`, deletion, host removal, field update, and sorted-set helpers.
- `Pipeline::execute()` runs a queued Boost.Redis request built by directory methods in pipeline mode.

## Control flow

All directory operations follow the same broad flow: build a D4N key, construct a Boost.Redis `request`, execute it through a shared connection or pool, check `boost::system::error_code`, parse typed or generic Redis responses, then return `0`, Redis-derived negative error, `-ENOENT`, or `-EINVAL`.

Bucket operations are simple sorted-set calls. `BucketDirectory::zadd()` ignores the caller-provided `score` and always writes a `ZADD ... CH 0 member`, indicating bucket membership is stored lexicographically rather than by a meaningful numeric score. `zrange()` uses `ZRANGE key start stop BYLEX` and optionally `LIMIT offset count`. `zscan()` parses the generic RESP3 aggregate response manually, filling members from alternating member/score positions. One important control-flow issue is that `next_cursor` is passed by value, so callers do not receive the parsed cursor even though the method assigns it internally.

Object hash operations use `bucketName + "_" + objName` as the key. `set()` writes all object metadata fields with `HSET`: object and bucket names, creation time, dirty flag, underscore-delimited hosts, etag, object size, user id, and display name. `get()` uses `HMGET` with the same field order and assigns by `ObjectFields`. The sorted-set methods on `ObjectDirectory` operate against the same object index; D4N uses these sets for object versions or creation-time ordered dirty entries depending on call site.

Block hash operations use `bucketName + "_" + objName + "_" + blockID + "_" + size` as the key. `set_values()` serializes the block fields in `BlockFields` order, including block id, version, delete marker, size, global LFUDA weight, embedded object metadata, dirty flag, hosts, etag, object size, user id, and display name. `set()` and vector `set()` write hashes through `HSET`, optionally batching commands. Single `get()` uses `HMGET` into a typed optional vector. The templated vector `get<N>()` builds a response type with `N` optional vector slots, executes a batch of `HMGET`s, and parses tuple slots with compile-time iteration. The non-template vector `get()` issues `HGETALL` commands and manually walks the generic RESP3 stream.

`BlockDirectory::remove_host()` performs a read-modify-write on the underscore-delimited `hosts` field: it reads the field, erases a substring matching the requested host, trims leading or trailing underscores, deletes the whole block hash if no host remains, and otherwise writes the modified host string back. This is not atomic across concurrent clients.

`Pipeline` is a lightweight batching helper. Directory methods with a `Pipeline*` parameter append commands to its request when `pipeline_mode` is active and skip response validation until `execute()`.

## State and persistence behavior

The persistent state is Redis metadata, not Ceph objects themselves. The cache data blocks live behind `rgw::cache::CacheDriver`; this file stores the directory that lets RGW find those blocks.

Redis key layouts are embedded directly:

- Bucket directory: the bucket id string itself is a Redis sorted set key.
- Object directory hash: `bucketName_objName`.
- Object version epoch: `bucketName_objName_versioned_epoch`.
- Block directory hash: `bucketName_objName_blockID_size`.
- Hosts fields: underscore-delimited host strings, later split into `std::unordered_set<std::string>`.

Object and block hashes overwrite all stored fields on `set()`. `update_field()` can append to `hosts` or normalize `dirty`, then writes one field. `copy()` uses Redis `COPY` and `HSET` in a `MULTI`/`EXEC` sequence to duplicate metadata and rewrite object/bucket identity fields, but comments note that the method is not compatible with Ubuntu systems, likely because of Redis command/version availability.

Deletion uses Redis `UNLINK`, so removal is asynchronous on the Redis server. Vector deletion and vector set are pipelined but do not validate per-key effects.

## Dependencies and integration points

The file depends on Boost.Asio, Boost.Redis, Boost.Algorithm string splitting, Ceph async blocked completions, Ceph logging, and `optional_yield`. The data types and class declarations come from `d4n_directory.h`.

Primary consumers are:

- `rgw_sal_d4n.cc`, which uses `BucketDirectory`, `ObjectDirectory`, and `BlockDirectory` for D4N filter operations such as list, read, write, delete, copy, multipart completion, and bucket cleanup.
- `d4n_policy.cc`, which uses `BlockDirectory` during LFUDA eviction and dirty-object cleaning, uses `ObjectDirectory` to remove cleaned object/version entries, and uses `BucketDirectory` to remove bucket index entries.
- `D4NFilterDriver::initialize()` creates the directories, creates or configures a Redis connection/pool, and passes these objects to the policy/filter layer.

The Boost version conditional in `RedisPool::acquire()` lives in the header but affects this implementation because directory methods may run against pooled connections initialized lazily there.

## Risks and edge cases

- Redis key construction is delimiter based and unescaped. Bucket names, object names, or host strings containing underscores can collide or parse incorrectly. Host removal uses substring erase, so removing `host1` can affect `host10` or any occurrence embedded in another host token.
- `BucketDirectory::zscan()` accepts `next_cursor` by value, so scan pagination state is lost.
- `ObjectDirectory::del()` and `BlockDirectory::del()` check response values before checking `ec`; an errored response can be inspected before the error branch.
- Several paths use `.value().value()` on optional Redis responses without checking `has_value()`, so missing hashes/fields can throw and be mapped to `-EINVAL` rather than `-ENOENT`.
- `BlockDirectory::get(const std::vector<CacheBlock>&)` non-template overload bypasses `redis_exec_connection_pool()` and directly uses `redis_exec(conn, ...)`, so it ignores the configured connection pool.
- The templated `BlockDirectory::get<N>()` is explicitly instantiated for `N=100`; callers with other batch sizes need a visible instantiation or header definition. It also assumes `responses.size()` covers `blocks.size()`.
- `update_field()` performs an existence test then a separate update. Concurrent deletion or updates between those calls can race.
- `remove_host()` is a non-atomic read-modify-write and does not use Redis transactions or Lua, so two clients can lose each other's host updates.
- `BucketDirectory::zadd()` ignores its `score` argument, unlike object/block `zadd()`, which may surprise call sites expecting score semantics.
- Empty responses are treated inconsistently: some methods return `-ENOENT`, others return `-EINVAL`, and `zrevrange()` returns success with an empty vector.
- `CacheObj::size` is declared without an initializer in the header; callers must initialize it before `set()` serializes it.

## Test signals

Useful tests should cover Redis command semantics with a real or fake Redis endpoint:

- Round-trip `ObjectDirectory::set()`/`get()` and `BlockDirectory::set()`/`get()` for all fields, including dirty/delete marker parsing and host-list splitting.
- Key-collision cases for object names and host strings containing underscores.
- `BucketDirectory::zrange()` lexicographic pagination and `zscan()` cursor propagation; the current by-value cursor should be caught.
- Pipelined `BlockDirectory::set()` and `ObjectDirectory::zadd()` followed by `Pipeline::execute()`.
- `remove_host()` behavior for first, middle, last, missing, substring, and final-host deletion cases.
- Connection pool operation under concurrent calls, including release on Redis exception.
- Missing-key and missing-field behavior to verify errno mapping rather than uncaught optional access.

No dedicated unit test file for `d4n_directory.cc` was found in the local source subset. Observable integration signals appear in D4N SAL paths and performance counters for D4N cache behavior.
