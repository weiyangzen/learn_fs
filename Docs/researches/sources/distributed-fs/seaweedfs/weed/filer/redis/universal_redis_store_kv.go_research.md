# sources/distributed-fs/seaweedfs/weed/filer/redis/universal_redis_store_kv.go

## Purpose

`redis/universal_redis_store_kv.go` adds generic key/value methods to the original Redis store. It was read as a complete 42-line file.

## Important APIs, Types, and Functions

`KvPut` performs `SET` with no expiration, `KvGet` performs `GET` and maps `redis.Nil` to `filer.ErrKvNotFound`, and `KvDelete` performs `DEL`.

## Control Flow

The flow is direct Redis command execution with simple error wrapping for puts and deletes.

## State and Persistence Behavior

KV data persists under raw stringified keys in the same Redis logical DB as metadata. No namespace prefix is applied in this v1 implementation, so callers must avoid collisions with path keys.

## Dependencies and Integration Points

Depends on `redis.UniversalClient`, `context`, and SeaweedFS `filer` KV error conventions.

## Risks and Edge Cases

Binary keys and values are converted through `string`; Redis supports this, but namespace collisions remain possible. There is no transaction or TTL support here.

## Test Signals

Generic store tests should cover put/get/update/delete and missing-key mapping to `ErrKvNotFound`.
