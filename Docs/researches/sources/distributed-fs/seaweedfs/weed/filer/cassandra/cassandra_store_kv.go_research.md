# sources/distributed-fs/seaweedfs/weed/filer/cassandra/cassandra_store_kv.go

## Purpose
This file implements SeaweedFS KV operations on top of the original Cassandra `filemeta` table.

## Important APIs, Types, and Functions
- `KvPut` inserts value bytes into `filemeta` with TTL 0.
- `KvGet` selects `meta` and maps missing or empty data to `filer.ErrKvNotFound`.
- `KvDelete` deletes the row.
- `genDirAndName` pads keys to eight bytes and base64 encodes the first eight bytes as directory and the remaining bytes as name.

## Control Flow and State
Every operation converts a byte key to `(directory,name)`. Put is a Cassandra insert/upsert. Get scans metadata into a byte slice. Delete removes by directory/name.

## State and Persistence Behavior
KV values share the `filemeta` table with metadata rows. The first eight key bytes determine the partition, while remaining bytes determine the clustering/name component. Values are raw bytes.

## Dependencies and Integration Points
It uses gocql, filer KV errors, and the Cassandra session owned by `CassandraStore`.

## Risks and Edge Cases
- The `KvGet` error branch returns `ErrKvNotFound` only when the error is not `gocql.ErrNotFound`, then falls through for `ErrNotFound` and relies on empty data; this is easy to misread and should be tested.
- Short keys are zero-padded.
- KV rows can collide with metadata rows if encoded directory/name overlap real paths.

## Test Signals
Tests should cover missing keys, empty values, overwrites, binary/short keys, and delete behavior. No local tests are listed.
