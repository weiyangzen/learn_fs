# sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store_kv.go

## Purpose

`leveldb2_store_kv.go` adds generic KV operations to the sharded LevelDB2 store. It distributes KV keys across the same fixed set of databases by using the last byte of the raw key.

## Important APIs, Types, and Functions

The public methods are `KvPut`, `KvGet`, and `KvDelete`. `bucketKvKey` maps a key to `int(key[len(key)-1]) % dbCount`.

## Control Flow

Each method derives the partition from the raw key, then performs a LevelDB put/get/delete in that partition. Missing keys map to `filer.ErrKvNotFound`; other errors include the partition number in the message.

## State and Persistence Behavior

KV state is spread across the same LevelDB partitions as metadata, but partitioning is by last key byte rather than directory hash. Values are stored as raw bytes without compression or TTL.

## Dependencies and Integration Points

The file depends on LevelDB2's opened partition slice and the filer KV contract. It supports metadata offset and other auxiliary state for LevelDB2-backed filers.

## Risks and Edge Cases

`bucketKvKey` panics on an empty key because it indexes `key[len(key)-1]`. Distribution depends entirely on the last byte, so structured keys with a constant suffix can hot-spot one DB. KV keys can collide with metadata keys within a partition if prefixes are not disciplined.

## Test Signals

Tests should include binary KV round trips across multiple suffixes, missing keys, empty-key rejection or panic behavior, partition distribution, and collision assumptions.
