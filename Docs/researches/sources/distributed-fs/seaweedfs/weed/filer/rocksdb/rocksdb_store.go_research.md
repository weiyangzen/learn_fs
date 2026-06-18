# sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_store.go

## Purpose

`rocksdb/rocksdb_store.go` implements a RocksDB-backed filer metadata store behind the `rocksdb` build tag. It was read as a complete 335-line file.

## Important APIs, Types, and Functions

`RocksDBStore` owns a DB path, `gorocksdb.DB`, and option wrappers. It implements filer store CRUD, directory deletion, prefixed listing, no-op transactions, key generation helpers, and `Shutdown`. `enumerate` is the shared prefix-scan loop.

## Control Flow

Initialization creates the directory, checks writability, configures RocksDB, Bloom filters, dynamic level compaction, and TTL compaction filter, then opens the DB. Entry keys are `md5(dir) + name`; listing scans from a hashed directory prefix plus optional start/prefix, decodes values, and invokes callbacks. Folder child deletion scans the directory prefix into a write batch.

## State and Persistence Behavior

Metadata persists in RocksDB. Directory ordering is achieved by key layout under a hashed directory prefix. Transactions are no-ops; operations are direct puts/deletes/batches.

## Dependencies and Integration Points

Depends on `gorocksdb`, SeaweedFS filer entry serialization, `weed_util.TestFolderWritable`, `filer_pb.ErrNotFound`, and `TTLFilter`.

## Risks and Edge Cases

Directory hash collisions are theoretically possible because only the hash and file name are stored, not the directory string. `enumerate` handles iterator errors but uses raw key/value data while iterating. TTL cleanup depends on compaction.

## Test Signals

`rocksdb_store_test.go` covers create/find/list root, empty root, benchmarks inserts, and prefixed listing.
