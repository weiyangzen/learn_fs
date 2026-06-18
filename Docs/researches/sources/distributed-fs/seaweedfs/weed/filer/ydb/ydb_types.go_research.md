# sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_types.go

## Purpose

`ydb/ydb_types.go` defines YDB row types, table creation options, and query formatting helpers. It was read as a complete 65-line file.

## Important APIs, Types, and Functions

`FileMeta` holds `DirHash`, `Name`, `Directory`, and `Meta`; `FileMetas` is a slice alias. `FileMeta.queryParameters` builds query parameters including optional `expire_at`. `YdbStore.createTableOptions` builds schema, TTL, primary key, and partitioning options. `withPragma` formats query templates with table path prefix.

## Control Flow

TTL parameter is optional: positive `ttlSec` becomes a uint32 optional value, otherwise null. Table creation sets TTL mode to seconds since Unix epoch and partitions by `dir_hash` and `name`.

## State and Persistence Behavior

Defines YDB persistent schema: primary key `(dir_hash, directory, name)`, `meta` bytes, and `expire_at` TTL column.

## Dependencies and Integration Points

Depends on YDB table/types/options APIs and is used by `ydb_store.go` and `ydb_store_kv.go`.

## Risks and Edge Cases

`queryParameters` stores `ttlSec` directly as `expire_at`, but YDB TTL mode expects Unix epoch seconds; callers passing relative TTL seconds can expire rows unexpectedly. Query formatting must not expose untrusted prefixes.

## Test Signals

Needed tests should validate table options, TTL semantics, and generated query parameters.
