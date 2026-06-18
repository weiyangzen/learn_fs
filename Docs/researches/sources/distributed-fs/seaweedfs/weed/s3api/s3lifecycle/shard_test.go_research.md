# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/shard_test.go

## Purpose
This file tests the `ShardID` keyspace partition helper used by lifecycle readers.

## Important APIs and test cases
The tests call `ShardID` and compare results to `ShardCount`. Cases include empty strings, ordinary bucket/key pairs, nested object keys, Unicode strings, and empty object keys.

## Control flow and state behavior under test
`TestShardIDInRange` ensures all sampled inputs map into `[0, ShardCount)`. `TestShardIDDeterministic` calls the same bucket/key twice and requires identical output. `TestShardIDDistinctFromBucket` hashes one key across sixteen bucket names and expects at least four distinct shards as a coarse distribution check.

## Dependencies and integration points
The tests live in the lifecycle package and do not mock anything. They protect code that assigns reader tasks and shard cursors.

## Risks and gaps
The distribution test is intentionally statistical and small; it would not catch all skew patterns. It also does not pin exact shard IDs, which is good for implementation flexibility but means accidental remapping could pass unless range/distribution stayed plausible.

## Test signals
The tests confirm the minimum stable-contract properties: bounded output, deterministic mapping, and bucket name participation in the hash.
