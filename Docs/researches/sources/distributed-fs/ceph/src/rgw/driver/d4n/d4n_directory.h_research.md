# sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_directory.h

## Purpose

`d4n_directory.h` declares the Redis-backed directory API for D4N cache metadata. It defines the metadata records used to describe cached S3 objects and cache blocks, the directory classes that persist those records in Redis, a small Redis connection pool, and a pipeline helper for batching Redis commands. This header is the contract consumed by the D4N SAL filter and cache policy implementation.

## Important APIs and types

- `SeqContainer` is a C++20 concept requiring `push_back(value_type)`. It constrains `BlockDirectory::set_values()` so the implementation can serialize metadata into either `std::vector<std::string>` or `std::list<std::string>`.
- `RedisPool` owns a deque of shared Boost.Redis connections, lazily starts each connection with `async_run()`, blocks callers when the pool is empty, and returns connections through `release()`.
- `ObjectFields` and `BlockFields` enumerate the expected order of Redis `HMGET` fields for object and block hashes. The implementation indexes response vectors with these enum values.
- `CacheObj` stores D4N object metadata: S3 object name, bucket name/id as used by callers, creation time string, dirty flag, set of cache host addresses, etag, total object size, owner user id, and display name.
- `CacheBlock` embeds a `CacheObj` and adds block id, object version, delete marker flag, block size, and LFUDA global weight.
- `Directory` is a base class that carries an optional `std::shared_ptr<RedisPool>` and exposes `set_redis_pool()`.
- `Pipeline` wraps a Boost.Redis `request` and exposes `start()`, `execute()`, `is_pipeline()`, and `get_request()`.
- `BucketDirectory`, `ObjectDirectory`, and `BlockDirectory` declare the Redis operations implemented in `d4n_directory.cc`.

## Control flow and API shape

The header organizes D4N metadata at three levels:

1. `BucketDirectory` handles bucket membership/order using sorted-set operations. Its methods operate on a `bucket_id` string key and members.
2. `ObjectDirectory` handles whole-object metadata and object-level sorted-set operations keyed by a `CacheObj`.
3. `BlockDirectory` handles per-block metadata, block hash lookup, vectorized/pipelined bulk operations, and host removal.

Each concrete directory stores a shared `boost::redis::connection` passed at construction. The base `Directory` can later be configured with a `RedisPool`; implementation code chooses the pool if present and otherwise uses the shared connection.

Most public methods accept `const DoutPrefixProvider* dpp` for logging/config access and `optional_yield y` for either asynchronous/yielded or blocked completion. Methods that mutate sorted sets or hashes generally return `int` status. The policy layer and SAL layer use those return codes directly in RGW operation control flow.

`Pipeline` is intentionally simple: callers call `start()`, pass the pipeline to directory methods that support it, and then call `execute()` to submit the accumulated request. The header exposes `request& get_request()`, so batching logic is not encapsulated from callers.

## State and persistence contract

The header defines the in-memory representation of Redis-persisted D4N state:

- Object hash fields correspond to `ObjectFields`.
- Block hash fields correspond to `BlockFields`.
- Block metadata reuses `CacheObj::dirty` and `CacheObj::hostsList` to record block dirty state and block locations.
- `CacheBlock::globalWeight` is explicitly tied to LFUDA policy.

The persistence key format is private in `ObjectDirectory::build_index()` and `BlockDirectory::build_index()` declarations, but callers must populate `CacheObj` and `CacheBlock` fields consistently because the implementation derives Redis keys from those fields. `CacheObj::size` and several strings have no default semantic value, so uninitialized or empty fields can produce invalid directory rows.

`RedisPool` state is runtime-only. It tracks the Asio context, Redis config, pooled connections, mutex, condition variable, and whether connections have been started. The pool starts connections lazily on first `acquire()` rather than in the constructor.

## Dependencies and integration points

This header depends on Ceph RGW common types (`rgw_common.h`, `rgw_asio_thread.h`, `DoutPrefixProvider`, `optional_yield`), Boost.Asio, Boost.Redis, C++ threading primitives, and C++20 concepts.

Integration points include:

- `rgw_sal_d4n.h` includes this header to store directory members on `D4NFilterDriver` and to expose getters for filter objects/readers/writers.
- `d4n_policy.h` includes this header so policies can update block/object/bucket directory state during eviction and cleaning.
- `rgw_sal_d4n.cc` configures Redis connection pooling and passes the pool to directories.
- `d4n_directory.cc` relies on `ObjectFields` and `BlockFields` order matching the hard-coded Redis field vectors.

## Risks and edge cases

- `RedisPool::acquire()` can block indefinitely when all connections are checked out. It calls `maybe_warn_about_blocking(dpp)` if a `DoutPrefixProvider` is available, but there is no timeout or cancellation path for waiters.
- `RedisPool::cancel_all()` only iterates over connections currently in `m_pool`. Connections checked out at destruction time are not canceled by this method.
- `RedisPool::current_pool_size()` returns an `int` from a `size_t`, which can truncate very large pools.
- `RedisPool` has a typo in `m_aquire_release_mtx`; harmless but visible API maintenance noise.
- `PolicyDriver` and directory users rely on raw pointers and shared connections, so lifetime order matters. Directories must not outlive their Redis connection.
- `CacheObj::size` has no default initializer, unlike most bool fields. Using a default-constructed `CacheObj` with `set()` can serialize an indeterminate size.
- The field enums are order-sensitive. Adding, removing, or reordering fields in the implementation without updating these enums will silently corrupt parsing.
- `Pipeline` holds a single `request` and mutable mode flag without locking; it is not thread-safe.

## Test signals

Tests should compile consumers against this header with C++20 concept support and Boost.Redis version variants. Behavioral tests should validate:

- Lazy connection startup and release/blocking behavior in `RedisPool`.
- `cancel_all()` behavior with checked-in and checked-out connections.
- Object/block field enum alignment against serialized `HMGET` order.
- Default construction of `CacheObj` and `CacheBlock` before serialization.
- Pipeline append/execute lifecycle and rejection or behavior of reuse after `execute()`.

No direct header-specific tests were found in the local search. The strongest integration signal is construction and configuration in `D4NFilterDriver::initialize()` plus broad use by `rgw_sal_d4n.cc` read/write/delete/list flows.
