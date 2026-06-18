# sources/distributed-fs/seaweedfs/weed/filer/redis2/universal_redis_store_kv.go

## Purpose

`redis2/universal_redis_store_kv.go` implements Redis v2 generic KV methods. It was read as a complete 42-line file.

## Important APIs, Types, and Functions

`KvPut`, `KvGet`, and `KvDelete` execute `SET`, `GET`, and `DEL` through the v2 `getKey` namespace wrapper. Missing keys map from `redis.Nil` to `filer.ErrKvNotFound`.

## Control Flow

Each API is a single Redis command plus error conversion/wrapping.

## State and Persistence Behavior

KV values persist without TTL under `keyPrefix + string(key)`, sharing the Redis DB with metadata but reducing cross-store collisions.

## Dependencies and Integration Points

Depends on `UniversalRedis2Store.getKey`, go-redis, and filer KV error conventions.

## Risks and Edge Cases

The prefixed namespace is only as safe as caller-provided prefixes. No transaction, CAS, or TTL semantics are provided.

## Test Signals

Generic store tests should verify put/get/update/delete, missing-key errors, and prefix isolation.
