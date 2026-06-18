# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProvider.cc

## Purpose
This file implements the sharded, cache-backed metadata provider used by QuarkDB file and container services. It distributes metadata ids over 16 shards, each with its own qclient and `MetadataProviderShard`, and aggregates cache controls/statistics.

## Important APIs, Types, and Functions
The constructor creates a `folly::IOThreadPoolExecutor(16)`, then builds `kShards` qclients from `QdbContactDetails` and one shard per qclient. `retrieveContainerMD()`, `retrieveFileMD()`, cache drops, existence checks, and cache insertions delegate to `pickShard(id)`. `setFileMDCacheNum()` and `setContainerMDCacheNum()` divide global capacity by shard count, preserving `UINT64_MAX` as unlimited. `aggregateStatistics()` sums cache stats. `getFileMDCacheStats()` and `getContainerMDCacheStats()` aggregate shard stats and mark the result enabled. `pickShard()` uses id modulo `kShards`.

## Control Flow
The provider is a thin dispatcher. Every operation computes the target shard from the id and forwards. Cache size changes iterate all shards. Statistics iterate all shards and sum their counters.

## State and Persistence Behavior
The provider owns the executor, qclients, and shards. It does not persist metadata directly; shards fetch from QuarkDB and cache objects. Member declaration order intentionally keeps the executor before qclients so continuations cannot outlive their executor during destruction.

## Dependencies and Integration Points
It depends on `MetadataProviderShard`, `QdbContactDetails`, qclient construction options, and folly executors. It is owned by `QuarkFileMDSvc` and shared with `QuarkContainerMDSvc`.

## Risks and Test Signals
Capacity division truncates remainders, so small global limits below 16 become zero per shard. Modulo sharding assumes stable id distribution and fixed shard count. Tests should cover construction with contact details, forwarding to expected shards, unlimited cache size, small cache sizes, aggregated statistics including in-flight counts, and destruction ordering under pending futures.
