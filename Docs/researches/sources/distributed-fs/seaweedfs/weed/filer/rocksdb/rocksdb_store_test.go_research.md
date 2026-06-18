# sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_store_test.go

## Purpose

`rocksdb/rocksdb_store_test.go` tests and benchmarks the RocksDB filer store under the `rocksdb` build tag. It was read as a complete 185-line file.

## Important APIs, Types, and Functions

Tests include `TestCreateAndFind`, `TestEmptyRoot`, `BenchmarkInsertEntry`, and `TestListDirectoryWithPrefix`.

## Control Flow

Tests create a temporary RocksDB store, attach it to a `filer.Filer`, create entries through filer APIs, and assert find/list results. The prefix test creates bucket-style paths and verifies listing `/bucket1` by prefix and listing the child directory.

## State and Persistence Behavior

State is persisted to a test temp directory and cleaned by `t.TempDir`. Filer-level parent directory creation is involved in create/list tests.

## Dependencies and Integration Points

Depends on SeaweedFS `filer`, `pb.ServerDiscovery`, `util.FullPath`, and Go testing.

## Risks and Edge Cases

The tests do not exercise TTL compaction, delete-folder batching, hash collisions, KV operations, or iterator error paths.

## Test Signals

Good signal for basic create/find, empty directory listing, insert allocation benchmark, and prefixed listing behavior.
