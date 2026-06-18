# sources/distributed-fs/ceph/src/rgw/rgw_redis_driver.h

## Purpose

Declares the Redis/Valkey cache driver implementation for RGW's cache-driver abstraction.

## Important APIs, Types, and Functions

`RedisDriver` derives from `CacheDriver` and overrides partition/free-space, initialization, put/get, async put/get, append, delete, rename, attribute CRUD, restore stub, and shutdown behavior. It owns a Boost.Redis connection, partition info, free-space counters, a private `redis_response` bundle, `redis_aio_handler`, and helpers for Redis-backed AIO operations.

## Control Flow and Data Flow

Callers interact through the `CacheDriver` interface. The driver prefixes keys with the partition location, stores object bytes in a `data` hash field, stores attrs as additional hash fields, and uses Asio/Boost.Redis for both coroutine/blocking style and AIO callbacks.

## State and Persistence Behavior

The class holds connection and local accounting state. Redis holds the cache contents; the header does not expose any durability or eviction policy. `restore_blocks_objects()` is a no-op returning success.

## Dependencies and Integration Points

Depends on Boost.Redis, Boost.Asio, filesystem, RGW cache driver definitions, RGW common types, and Ceph async completion. It is selected by cache-driver setup code for Redis/Valkey-backed D4N cache.

## Risks and Edge Cases

The constructor creates the connection but does not connect until `initialize()`. `redis_aio_handler` detects GET operations by searching the request payload for `"HGET"`, which is brittle. Captured references in AIO lambdas require caller-provided buffers/attrs/keys to outlive operation execution. `outstanding_write_size` is declared but unused in the implementation.

## Test Signals

Compile and interface-conformance tests, lifecycle tests around initialize/shutdown, AIO lifetime tests, partition prefixing, no-op restore behavior, and driver selection with invalid Redis endpoint configuration.
