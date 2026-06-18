# sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_store_kv.go

## Purpose

`rocksdb/rocksdb_store_kv.go` provides generic KV operations for the RocksDB filer store. It was read as a complete 48-line file.

## Important APIs, Types, and Functions

`KvPut` writes with `db.Put`, `KvGet` uses `db.GetBytes`, mapping nil to `filer.ErrKvNotFound`, and `KvDelete` deletes with RocksDB write options.

## Control Flow

Each method performs one RocksDB operation and wraps errors with KV-specific context.

## State and Persistence Behavior

KV data persists under raw byte keys in the same RocksDB database as metadata. There is no namespace separation from `md5(dir)+name` metadata keys.

## Dependencies and Integration Points

Depends on `RocksDBStore` options/DB and filer KV error conventions.

## Risks and Edge Cases

Raw KV keys can collide with metadata key layout if callers use arbitrary bytes. No transaction support or TTL behavior is applied.

## Test Signals

The generic `store_test` suite exercises KV put/get/update for stores that use it; RocksDB-specific tests in this subset do not directly cover KV delete/missing.
