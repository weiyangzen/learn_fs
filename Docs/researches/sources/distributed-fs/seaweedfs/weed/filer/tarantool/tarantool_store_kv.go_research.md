# sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store_kv.go

## Purpose

`tarantool/tarantool_store_kv.go` implements generic KV operations for the Tarantool store. It was read as a complete 94-line file.

## Important APIs, Types, and Functions

`tarantoolKVSpaceName` is `key_value`. `KvPut` upserts key/value rows, `KvGet` reads the `value` field with replica preferences and maps missing/shape mismatches to `filer.ErrKvNotFound`, and `KvDelete` deletes by key.

## Control Flow

All operations use Tarantool CRUD requests through the connection pool. Get parses the nested `crud.Result.Rows` shape and validates the value is a string.

## State and Persistence Behavior

KV state persists in Tarantool space `key_value`. Values are converted to strings for storage and back to bytes on read.

## Dependencies and Integration Points

Depends on Tarantool CRUD, pool routing, and filer KV error semantics.

## Risks and Edge Cases

Binary values pass through Go strings and depend on Tarantool field type compatibility. Runtime row shape/type changes produce errors. No TTL or transaction support is provided.

## Test Signals

The generic store suite invoked by Tarantool tests covers KV put/get/update, but not delete or missing-key behavior.
