# sources/distributed-fs/seaweedfs/weed/filer/redis3/universal_redis_store_kv.go

## Purpose

`redis3/universal_redis_store_kv.go` implements Redis3 generic KV operations. It was read as a complete 42-line file.

## Important APIs, Types, and Functions

`KvPut`, `KvGet`, and `KvDelete` map to Redis `SET`, `GET`, and `DEL`. Missing keys map to `filer.ErrKvNotFound`.

## Control Flow

Each method executes one Redis command against `string(key)` with basic error wrapping.

## State and Persistence Behavior

KV values persist without TTL in the same Redis namespace as metadata. Unlike Redis2 KV, no key prefix is applied.

## Dependencies and Integration Points

Depends on Redis universal client, context, and filer KV conventions.

## Risks and Edge Cases

Raw key namespace can collide with metadata paths or directory-list keys. No lock or transaction is used for KV operations.

## Test Signals

Generic KV store tests should cover put/get/update/delete, missing-key mapping, and binary key/value round trips.
