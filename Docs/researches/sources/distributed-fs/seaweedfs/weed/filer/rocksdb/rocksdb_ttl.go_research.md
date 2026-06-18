# sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_ttl.go

## Purpose

`rocksdb/rocksdb_ttl.go` defines a RocksDB compaction filter that removes expired filer entries. It was read as a complete 46-line file.

## Important APIs, Types, and Functions

`TTLFilter` stores `skipLevel0`. `NewTTLFilter` returns the filter. `Filter` decodes a `filer.Entry` and removes it if `TtlSec` is positive and `Crtime + TtlSec` is before now. `Name`, `SetIgnoreSnapshots`, and `Destroy` satisfy the RocksDB filter interface.

## Control Flow

The filter skips level 0 by default to reduce write stalls, then applies decode-and-expiration checks during compaction at higher levels.

## State and Persistence Behavior

It affects persisted RocksDB metadata by removing expired entries during compaction. It does not update parent directory references because RocksDB directory membership is implicit in key layout.

## Dependencies and Integration Points

Depends on `gorocksdb.CompactionFilter`, `filer.Entry` decode, and `time`.

## Risks and Edge Cases

Expired data can remain until compaction reaches eligible levels. Decode failures keep data. The current time check during compaction makes expiration nondeterministic in tests.

## Test Signals

No direct TTL filter test in this subset. Useful tests require forcing compaction and verifying expired/non-expired entries.
