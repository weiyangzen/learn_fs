# sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_store_kv.go

## Purpose

`ydb/ydb_store_kv.go` implements generic KV operations on top of the YDB metadata table schema. It was read as a complete 82-line file.

## Important APIs, Types, and Functions

`KvPut` maps a raw key into directory/hash/name via `abstract_sql.GenDirAndName`, creates `FileMeta`, and runs `upsertQuery`. `KvGet` runs `findQuery` and scans `meta`. `KvDelete` runs `deleteQuery`.

## Control Flow

Each operation uses `store.DB.Query().Do` with idempotent execution and table query parameters. Missing reads return `filer.ErrKvNotFound`.

## State and Persistence Behavior

KV data persists in the base YDB table path, not bucket-specific tables. TTL is zero for KV puts.

## Dependencies and Integration Points

Depends on YDB query sessions, table parameter types, `abstract_sql.GenDirAndName`, `FileMeta`, and shared query templates.

## Risks and Edge Cases

KV methods bypass `doTxOrDB`, so they do not join `YdbStore` transactions. They also use only `store.tablePathPrefix`, not per-bucket routing.

## Test Signals

Generic KV tests are needed for put/get/update/delete, missing keys, transaction expectations, and binary key/value behavior.
