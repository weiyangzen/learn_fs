# sources/distributed-fs/juicefs/pkg/meta/redis_bak.go

## Purpose

`redis_bak.go` implements the protobuf segment backup and restore path for `redisMeta`. It dumps Redis metadata into `pb.Batch` records grouped by segment type and reloads those records into a Redis database or hash-tagged Redis Cluster prefix.

## Important APIs, Types, and Functions

The top-level `dump` method calls `dumpFormat`, `dumpCounters`, `dumpMix`, `dumpSustained`, `dumpDelFiles`, `dumpSliceRef`, `dumpACL`, `dumpQuota`, and `dumpDirStat`. `dumpMix` scans the Redis keyspace and dispatches keys to typed handlers: `dumpNodes`, `dumpEdges`, `dumpChunks`, `dumpSymlinks`, `dumpXattrs`, and `dumpParents`. Restore is routed by `load`, with implementations such as `loadFormat`, `loadCounters`, `loadNodes`, `loadEdges`, `loadChunks`, `loadSymlinks`, `loadSustained`, `loadDelFiles`, `loadSliceRefs`, `loadAcl`, `loadXattrs`, `loadQuota`, `loadDirStats`, and `loadParents`. `prepareLoad` rejects non-empty destinations.

## Control Flow

Dump starts with small global segments, then `dumpMix` warns that Redis should be readonly for consistency and scans keys using `m.scan`. A key classification goroutine groups keys by first metadata prefix character and launches bounded errgroup workers according to `opt.Threads`. Each worker reads a batch through `MGET`, `HSCAN`, `LRANGE`, or pipelined hash/list commands, fills protobuf objects from sync pools, emits `dumpedResult`, and updates per-type counters.

Restore switches on segment type. Most load methods batch writes through Redis pipelines and flush at `redisPipeLimit`. Node attrs are written with `SET`, edges with `HSET`, chunks with `RPUSH`, symlinks with `MSET`, sustained sets with `SADD`, deleted files with `ZADD`, slice refs with `HSET`, quotas and dir stats with hashes, and parents with `HINCRBY`. `execPipe` reports the first failed command if a pipeline fails. ACL load tracks the max ACL ID under a package-level mutex and writes the ACL counter.

## State and Persistence Behavior

This file serializes the same Redis key layout used by `redis.go`, but in protobuf batches rather than JSON tree form. It preserves raw inode attr bytes and raw 24-byte slice records. It adjusts Redis-specific counters: `nextInode` and `nextChunk` are dumped as next values and loaded as last-used values; `sliceRef` is dumped with one added and loaded with one subtracted because Redis omits the implicit first reference.

## Dependencies and Integration Points

It depends on JuiceFS protobuf metadata messages, `dumpResult` and segment constants from the broader meta package, `redisMeta` key helpers, `sliceBytes`, `packQuota`, `parseQuota`, and go-redis pipelines. It complements the JSON `DumpMeta`/`LoadMeta` code in `redis.go` and provides the engine-specific implementation for generic metadata backup tooling.

## Risks and Edge Cases

The dump is not snapshot-isolated and explicitly requires a readonly Redis server for consistency. Concurrent mutations can produce mismatched nodes, edges, chunks, counters, and reference counts. Key classification assumes every scanned key with a known prefix follows the expected Redis metadata format. Corrupt slice values are logged but skipped inside chunk dumps. `loadAcl` uses package-level `maxAclId`, so concurrent independent loads in one process would share state. `prepareLoad` only checks destination emptiness; it does not validate source batch ordering beyond each load handler.

## Test Signals

Tests should cover protobuf dump/load round trips for files, directories, symlinks, xattrs, hard-link parent maps, sustained files, deleted files, slice refs, ACLs, quotas, and dir stats. Redis counter and slice-ref offset conversions need explicit assertions. Failure tests should inject corrupt chunk records, non-empty destination Redis DBs, pipeline command errors, malformed quota values, and concurrent dump mutation to document expected inconsistency behavior.
