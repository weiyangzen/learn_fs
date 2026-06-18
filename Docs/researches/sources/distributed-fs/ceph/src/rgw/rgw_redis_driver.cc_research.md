# sources/distributed-fs/ceph/src/rgw/rgw_redis_driver.cc

## Purpose

Implements an RGW D4N/L1 cache backend backed by Redis or Valkey using Boost.Redis. It stores cached object data and attributes as Redis hashes under a partition-location prefix and supports synchronous and AIO-style operations.

## Important APIs, Types, and Functions

`build_attrs()` converts SAL attrs to alternating field/value strings. `async_exec()` and `redis_exec()` adapt Boost.Redis async execution to Ceph optional-yield or blocked completion. `RedisDriver::initialize()` starts the Redis connection. Data methods include `put()`, `get()`, `append_data()`, `delete_data()`, `rename()`, `get_attrs()`, `set_attrs()`, `update_attrs()`, `delete_attrs()`, `get_attr()`, `set_attr()`, `get_async()`, `put_async()`, and `shutdown()`. `resolve_valkey_data_dir()` and `get_free_space()` inspect Redis `CONFIG GET dir` and filesystem free space.

## Control Flow and Data Flow

Writes build `entry = partition_info.location + key`, convert attrs, optionally add the `data` field, and issue `HSET`. Reads issue `HGETALL`, return `-ENOENT` on empty hashes, append the `data` field to the output bufferlist, and convert all other fields back to attrs. Appends read the existing `data` field and rewrite the concatenated value. Deletes wrap `HSTRLEN` and `DEL` in `MULTI/EXEC` and add the removed data length back to local `free_space`. AIO methods enqueue Redis HGET/HSET operations through RGW `Aio` using callbacks that place results back into the throttle.

## State and Persistence Behavior

Persistent cache state is stored in Redis hashes. `free_space` and `outstanding_write_size` are process-local counters; `free_space` is decremented/incremented by operations but initialized only to zero in the constructor in this file. Redis data dir is discovered dynamically by `CONFIG GET dir`, then host filesystem space is checked against partition reserve size.

## Dependencies and Integration Points

Depends on Boost.Redis/Asio, Ceph async blocked completion, RGW cache driver interfaces, SAL attrs, bufferlists, and `rgw_d4n_l1_datacache_address`. Integrates as a `CacheDriver` implementation for D4N data cache.

## Risks and Edge Cases

Offset and length parameters in `get()`/`get_async()` are ignored; the full `data` field is returned. Several optional Redis response accesses call `.value().value()` and can throw on missing optional values. `delete_attrs()` passes alternating attr field/value output to `HDEL`, but Redis `HDEL` expects field names only. `get_async()`/`put_async()` use `aio->get()` for both reads and writes. The file contains `std::clog` debug prints in `resolve_valkey_data_dir()`. `append_data()` rewrites whole values and is race-prone. Local `free_space` arithmetic can underflow because it starts at zero and is not synchronized.

## Test Signals

Cover connection address parsing, Redis command errors, missing keys/attrs/data fields, binary attribute round trips, offset reads, append races, delete free-space accounting, `HDEL` field behavior, AIO read/write callback result and data propagation, shutdown cancellation, `CONFIG GET dir` disabled or malformed, and filesystem reserve calculations.
