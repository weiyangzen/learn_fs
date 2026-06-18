# sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_store.go

## Purpose

`ydb/ydb_store.go` implements a YDB-backed filer metadata store with optional per-bucket tables. It was read as a complete 518-line file.

## Important APIs, Types, and Functions

`YdbStore` owns the YDB driver, bucket folder/prefix settings, partitioning options, max list chunk, and a cached bucket-table map. It implements initialization, query execution helper `doTxOrDB`, entry CRUD, listing, transactions, bucket-aware hooks, table creation/deletion, prefix resolution, and shutdown.

## Control Flow

Initialization opens YDB using env credentials and DSN, sets defaults, derives table path prefix, and ensures tables. Entry upsert encodes metadata, optional-gzips it, resolves bucket/table prefix, and executes query templates with parameters. Listing loops in chunks up to `maxListChunk`, switching inclusive/exclusive start query as needed and updating `startFileName`. Bucket hooks create/drop bucket-specific tables.

## State and Persistence Behavior

Metadata persists in YDB tables with TTL column support and partitioning settings. Optional bucket mode routes bucket subtrees to separate tables and caches verified bucket table existence.

## Dependencies and Integration Points

Depends on YDB SDK driver/query/table APIs, env auth, SeaweedFS filer entry serialization, bucket-aware interface, abstract SQL constants, and query/type helper files.

## Risks and Edge Cases

`BeginTransaction` uses table transactions while `doTxOrDB` checks for `query.Transaction`, so transaction integration appears type-inconsistent. Bucket prefix detection depends on configured buckets folder and cached table existence. List prefix uses SQL `LIKE`.

## Test Signals

`ydb_store_test.go` contains a disabled generic store test. Live YDB integration should cover bucket tables, transactions, TTL, chunked listing, and KV methods.
