# sources/distributed-fs/seaweedfs/weed/filer/leveldb/leveldb_store_kv.go

## Purpose

`leveldb_store_kv.go` adds generic KV operations to the single-LevelDB filer store. It lets shared filer components persist auxiliary byte values in the same local LevelDB database.

## Important APIs, Types, and Functions

The methods are `KvPut`, `KvGet`, and `KvDelete` on `LevelDBStore`. They call LevelDB `Put`, `Get`, and `Delete` directly and wrap errors with operation-specific context. Missing keys become `filer.ErrKvNotFound`.

## Control Flow

Each KV call uses the caller-provided raw byte key without transformation. `KvGet` checks `leveldb.ErrNotFound` before wrapping other errors. Put and delete return nil on successful LevelDB writes.

## State and Persistence Behavior

KV bytes are persisted in the same LevelDB keyspace as metadata entries. Values are stored exactly as provided, without compression, TTL, namespacing, or transaction support.

## Dependencies and Integration Points

The file depends on `goleveldb` and the filer KV error contract. It is used by metadata replication offsets, caches, and other filer subsystems that only need byte-key/byte-value persistence.

## Risks and Edge Cases

The absence of a KV namespace means accidental key collisions with file metadata are possible unless callers use disciplined key prefixes. Empty values are valid because not-found is detected by LevelDB error, not value length. Deletes of missing keys are treated as successful by LevelDB.

## Test Signals

KV round-trip, overwrite, delete, missing-key, empty-value, binary-key, and collision-prefix tests would validate the intended contract.
