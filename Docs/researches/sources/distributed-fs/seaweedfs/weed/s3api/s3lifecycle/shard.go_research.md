# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/shard.go

## Purpose
This file maps lifecycle events into a fixed shard space for per-shard readers and cursors. Stable sharding lets workers divide the bucket/key keyspace and advance independent read tasks.

## Important APIs and functions
`ShardCount` is fixed at 16. `ShardID(bucket, key string) int` hashes `bucket + "/" + key` with SHA-256 and returns the top four bits of the first digest byte. `shardHashPool` is a `sync.Pool` of SHA-256 hashers to reduce allocations in the hot path.

## Control flow and state behavior
`ShardID` gets a hasher from the pool, resets it, writes bucket, separator, and key bytes, computes the digest into a stack buffer, returns the hasher to the pool, and maps to `[0, ShardCount)`. No persistent state is stored; stability comes from deterministic hashing and the constant shard count.

## Dependencies and integration points
The file depends on `crypto/sha256`, `hash`, and `sync`. It integrates with lifecycle reader task partitioning and any cursor storage keyed by shard.

## Risks and edge cases
Changing `ShardCount`, the separator, or the hash algorithm would remap all keys and could invalidate cursor ownership assumptions. Pooling hashers requires every call to reset before use, which this implementation does. Distribution is statistical; small key sets may be imbalanced.

## Test signals
`shard_test.go` checks range safety, determinism, and a basic distribution signal across different bucket names.
