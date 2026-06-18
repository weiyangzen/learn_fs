# subset-b-007868 Research

Grouped source research for SeaweedFS filer reader/cache streaming, Redis/RocksDB/SQLite/Tarantool/TiKV/YDB filer stores, remote storage mapping, S3 IAM configuration, and S3 authorization regression tests. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/reader_cache.go -->
# sources/distributed-fs/seaweedfs/weed/filer/reader_cache.go

## Purpose

`reader_cache.go` implements an in-process chunk reader cache used by filer reads to deduplicate and prefetch volume-server chunk downloads. It was read as a complete 276-line file.

## Important APIs, Types, and Functions

`ReaderCache` owns a `chunk_cache.ChunkCache`, a `LookupFileIdFunctionType`, a bounded `downloaders` map, and a limit. `SingleChunkCacher` owns one fileId download, its pooled buffer, completion/error state, `done` signal, and wait group. Main APIs are `NewReaderCache`, `MaybeCache`, `ReadChunkAt`, `UnCache`, `destroy`, `startCaching`, and `readChunkAt`.

## Control Flow

`MaybeCache` walks future `ChunkView` intervals, skips existing/in-cache chunks, creates a `SingleChunkCacher`, starts it in a goroutine, waits only until the goroutine has begun, and records it. `ReadChunkAt` first waits on an existing cacher, falls back to the persistent chunk cache, evicts the oldest completed cacher when at capacity, then starts one shared download.

## State and Persistence Behavior

Downloaded data is held in memory allocated through `mem.Allocate`; optional persistence into `chunkCache.SetChunk` happens only when `shouldCache` is true. Completion time is stored atomically for eviction. `destroy` waits for active readers before freeing memory.

## Dependencies and Integration Points

It integrates with `ChunkView`/interval reader logic, `wdclient` fileId lookup, `util_http.RetriedFetchChunkData`, SeaweedFS chunk cache, and pooled memory. The shared download intentionally uses `context.Background()` so one request cancellation does not abort other readers waiting for the same chunk.

## Risks and Edge Cases

Risk concentrates around lock ordering, `done` always closing, memory frees after concurrent reads, and the `n=0, err=nil` path that must fall back to `chunkCache`. A lookup/download failure is shared by all waiters. Eviction only removes completed downloaders, so a full map of active downloads can temporarily block new prefetches.

## Test Signals

Covered by `reader_cache_test.go`: cancellation while waiting, fallback cache reads, partial offsets, downloader cleanup, lookup errors, in-flight deduplication, and one cancelled reader not cancelling the shared download for others.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/reader_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/reader_cache_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/reader_cache_test.go

## Purpose

`reader_cache_test.go` exercises `ReaderCache` and `SingleChunkCacher` concurrency behavior without requiring real volume-server HTTP fetches. It was read as a complete 545-line file.

## Important APIs, Types, and Functions

`mockChunkCacheForReaderCache` implements the chunk cache methods needed by `ReaderCache`: `ReadChunkAt`, `SetChunk`, `IsInCache`, and max-cache-size reporting. Tests include `TestReaderCacheContextCancellation`, `TestReaderCacheFallbackToChunkCache`, `TestReaderCacheMultipleReadersWaitForSameChunk`, `TestReaderCachePartialRead`, `TestReaderCacheCleanup`, `TestSingleChunkCacherLookupError`, `TestSingleChunkCacherContextCancellationDuringLookup`, `TestReaderCacheDownloaderDedup`, and `TestSingleChunkCacherOneReaderCancelsOthersContinue`.

## Control Flow

Most tests pre-populate the mock cache to avoid HTTP, then call `ReadChunkAt` concurrently. The more direct `SingleChunkCacher` tests provide blocking lookup functions and use channels to force reads to wait, cancel, or resume.

## State and Persistence Behavior

State is in-memory test data plus atomic hit/lookup counters. The tests verify that cached byte slices are reused, hit counts increase, and concurrent reader goroutines complete without hanging.

## Dependencies and Integration Points

The file depends on `testing`, `context`, `sync`, `atomic`, and the production reader cache API. It validates the contract expected by streaming code that may have multiple readers waiting on the same fileId.

## Risks and Edge Cases

The tests target regressions where a request context cancellation aborts a shared download, `done` is not closed, duplicate network lookups are started for one fileId, or offset reads return zero bytes without falling back.

## Test Signals

This file is itself the primary test signal for `reader_cache.go`; it is especially strong for concurrency ordering and weak for actual HTTP/decryption/gzip fetch success because those are intentionally not mocked end-to-end.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/reader_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/reader_pattern.go -->
# sources/distributed-fs/seaweedfs/weed/filer/reader_pattern.go

## Purpose

`reader_pattern.go` classifies reads as sequential or random so higher-level reader code can decide whether to cache whole chunks or fetch requested ranges. It was read as a complete 41-line file.

## Important APIs, Types, and Functions

`ReaderPattern` stores `isSequentialCounter` and `lastReadStopOffset` atomically. `NewReaderPattern` initializes the tracker. `MonitorReadAt(offset, size)` compares the new read offset with the previous stop offset. `IsRandomMode` returns true when the counter is negative. `ModeChangeLimit` caps drift at 3.

## Control Flow

Sequential adjacent reads increment the counter until the positive cap; non-adjacent reads decrement it until the negative cap. `IsRandomMode` then uses only the sign.

## State and Persistence Behavior

All state is transient per reader and atomic for concurrent read monitoring. Nothing is stored on disk or in the filer store.

## Dependencies and Integration Points

It depends only on `sync/atomic` and feeds reader cache/stream decisions documented by comments: streaming reads cache first chunks, random reads fetch only ranges.

## Risks and Edge Cases

The heuristic is intentionally simple, so interleaved concurrent reads can swing the counter and short bursts of random access may flip mode. The cap prevents overflow but not misclassification.

## Test Signals

No direct test is listed in this subset. Useful tests would exercise adjacent reads, gaps, backwards reads, and concurrent calls around the `ModeChangeLimit` boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/reader_pattern.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis/redis_cluster_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis/redis_cluster_store.go

## Purpose

`redis/redis_cluster_store.go` registers and initializes the original Redis cluster filer store. It was read as a complete 42-line file.

## Important APIs, Types, and Functions

`RedisClusterStore` embeds `UniversalRedisStore`. `init` appends it to `filer.Stores`. `GetName` returns `redis_cluster`. `Initialize` reads `addresses`, `password`, `useReadOnly`, and `routeByLatency`; `initialize` creates a `redis.NewClusterClient`.

## Control Flow

Startup sets defaults for read-only and latency routing, builds cluster options, and assigns the universal Redis client used by entry and KV methods.

## State and Persistence Behavior

The file owns no data schema itself; persistence is in Redis keys managed by `UniversalRedisStore`.

## Dependencies and Integration Points

Depends on `github.com/redis/go-redis/v9`, `filer.Stores`, and `util.Configuration`. It integrates the common Redis backend with SeaweedFS store discovery.

## Risks and Edge Cases

No ping or connection validation occurs during initialize, so misconfiguration surfaces on first operation. Cluster read-only/latency routing can affect consistency expectations for metadata reads.

## Test Signals

No direct test in this subset. Store-suite coverage would need a live Redis Cluster with directory create/list/delete and KV operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis/redis_cluster_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis/redis_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis/redis_store.go

## Purpose

`redis/redis_store.go` registers the original single-node Redis filer store. It was read as a complete 36-line file.

## Important APIs, Types, and Functions

`RedisStore` embeds `UniversalRedisStore`. `GetName` returns `redis`. `Initialize` reads `address`, `password`, and `database`; `initialize` creates a `redis.NewClient`.

## Control Flow

The file is startup glue only: `init` registers the store, configuration is converted into Redis options, and later filer operations use the embedded universal implementation.

## State and Persistence Behavior

The connection points at one Redis DB. Metadata keys are full paths and directory children are stored in Redis sets by `universal_redis_store.go`.

## Dependencies and Integration Points

Depends on `go-redis/v9`, SeaweedFS `filer` registration, and `util.Configuration`.

## Risks and Edge Cases

Initialization does not validate the server. There is no username/TLS/key-prefix support in this v1 file, so deployments needing those must use newer Redis store variants.

## Test Signals

No direct test in this subset. Functional evidence should come from generic filer store tests against a real Redis instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis/redis_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis/universal_redis_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis/universal_redis_store.go

## Purpose

`redis/universal_redis_store.go` implements the original Redis metadata store shared by single-node and cluster Redis stores. It was read as a complete 218-line file.

## Important APIs, Types, and Functions

`UniversalRedisStore` owns a `redis.UniversalClient`. It implements `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryEntries`, unsupported `ListDirectoryPrefixedEntries`, no-op transaction methods, `genDirectoryListKey`, and `Shutdown`.

## Control Flow

Entries are encoded with `Entry.EncodeAttributesAndChunks`, optionally gzipped for many chunks, and stored at the full path with Redis TTL. Parent directory membership is tracked separately in a Redis set whose key is `dir + "\x00"`. Listing loads all set members, filters by start name, sorts client-side, applies limit, fetches each entry, skips missing children, and lazily removes expired entries.

## State and Persistence Behavior

Metadata and KV data persist in Redis. Directory children are eventually consistent with entry keys because insert/delete update two independent Redis records and transactions are no-ops.

## Dependencies and Integration Points

Integrates with `filer.Entry` encode/decode, `filer_pb.ErrNotFound`, `util.MaybeGzipData`, `glog`, and `redis.UniversalClient`.

## Risks and Edge Cases

Large directories are expensive because `SMembers` loads the full set and sorting is client-side. Partial failures can leave stale directory set entries. TTL cleanup happens during list scans and may not remove directory references until a list occurs.

## Test Signals

No direct tests in this subset. Needed signals include create/find/delete, large directory listing, TTL expiration, stale child cleanup, and Redis outage behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis/universal_redis_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis/universal_redis_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis/universal_redis_store_kv.go

## Purpose

`redis/universal_redis_store_kv.go` adds generic key/value methods to the original Redis store. It was read as a complete 42-line file.

## Important APIs, Types, and Functions

`KvPut` performs `SET` with no expiration, `KvGet` performs `GET` and maps `redis.Nil` to `filer.ErrKvNotFound`, and `KvDelete` performs `DEL`.

## Control Flow

The flow is direct Redis command execution with simple error wrapping for puts and deletes.

## State and Persistence Behavior

KV data persists under raw stringified keys in the same Redis logical DB as metadata. No namespace prefix is applied in this v1 implementation, so callers must avoid collisions with path keys.

## Dependencies and Integration Points

Depends on `redis.UniversalClient`, `context`, and SeaweedFS `filer` KV error conventions.

## Risks and Edge Cases

Binary keys and values are converted through `string`; Redis supports this, but namespace collisions remain possible. There is no transaction or TTL support here.

## Test Signals

Generic store tests should cover put/get/update/delete and missing-key mapping to `ErrKvNotFound`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis/universal_redis_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_cluster_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_cluster_store.go

## Purpose

`redis2/redis_cluster_store.go` registers the second-generation Redis cluster store. It was read as a complete 48-line file.

## Important APIs, Types, and Functions

`RedisCluster2Store` embeds `UniversalRedis2Store`. It registers as `redis_cluster2`, reads `addresses`, `username`, `password`, `keyPrefix`, `useReadOnly`, `routeByLatency`, and `superLargeDirectories`, and creates a `redis.NewClusterClient`.

## Control Flow

Initialization configures cluster routing options, assigns the universal client, stores the key prefix, and loads the super-large-directory skip list.

## State and Persistence Behavior

Actual metadata layout is handled by `UniversalRedis2Store`: prefixed entry keys and lexicographic sorted-set directory indexes except for configured super-large directories.

## Dependencies and Integration Points

Depends on go-redis cluster options, filer store registration, and `util.Configuration`.

## Risks and Edge Cases

There is no initialization ping. Super-large-directory bypass means those parents will not maintain a Redis directory index; behavior must match external assumptions for listing or separate indexing.

## Test Signals

No direct tests here. Redis cluster integration should include key-prefix isolation, username auth, read-only routing, and super-large-directory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_cluster_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_sentinel_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_sentinel_store.go

## Purpose

`redis2/redis_sentinel_store.go` registers the Redis v2 Sentinel-backed filer store. It was read as a complete 48-line file.

## Important APIs, Types, and Functions

`Redis2SentinelStore` embeds `UniversalRedis2Store`. `GetName` returns `redis2_sentinel`. `Initialize` reads Sentinel addresses, `masterName`, username/password, database, and key prefix. `initialize` creates a `redis.NewFailoverClient` with retry/read/write timeouts.

## Control Flow

On startup it constructs failover options and stores the client/key prefix for universal entry and KV methods.

## State and Persistence Behavior

Persistent data follows the v2 schema in `universal_redis_store.go`. The sentinel client handles master discovery and failover externally.

## Dependencies and Integration Points

Uses go-redis failover options and SeaweedFS store registration/configuration.

## Risks and Edge Cases

`loadSuperLargeDirectories` is not called here, so `superLargeDirectoryHash` remains nil; map lookup is safe but configured super-large-directory behavior is unavailable for Sentinel v2. Failover consistency depends on Redis Sentinel and client behavior.

## Test Signals

No direct tests. Integration should exercise failover, key-prefix isolation, listing, and missing-server errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_sentinel_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_store.go

## Purpose

`redis2/redis_store.go` registers the second-generation single-node Redis store with username, key-prefix, super-large-directory, and optional mTLS support. It was read as a complete 81-line file.

## Important APIs, Types, and Functions

`Redis2Store` embeds `UniversalRedis2Store`. `Initialize` reads address, username/password, database, key prefix, super-large directories, and mTLS certificate paths. `initialize` creates `redis.Options`, optionally builds `tls.Config`, then assigns the client and directory settings.

## Control Flow

When mTLS is enabled, the file loads client cert/key, reads CA PEM, parses host name for `ServerName`, and installs TLS 1.2+ config before creating the Redis client.

## State and Persistence Behavior

The file only owns connection and namespace setup; entry persistence is in the v2 universal store.

## Dependencies and Integration Points

Depends on `crypto/tls`, `crypto/x509`, `os.ReadFile`, `net.SplitHostPort`, `glog.Fatalf`, go-redis, and SeaweedFS config.

## Risks and Edge Cases

mTLS failures call `glog.Fatalf`, terminating the process instead of returning errors. Invalid host:port also exits. No connection ping is performed.

## Test Signals

Needed tests include mTLS config error paths, key-prefix isolation, username auth, and super-large-directory listing semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis2/redis_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis2/universal_redis_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis2/universal_redis_store.go

## Purpose

`redis2/universal_redis_store.go` implements Redis metadata storage with key prefixes and sorted-set directory indexes. It was read as a complete 242-line file.

## Important APIs, Types, and Functions

`UniversalRedis2Store` owns `Client`, `keyPrefix`, and `superLargeDirectoryHash`. It implements no-op transactions, entry CRUD, directory child delete/list, unsupported prefixed listing, key prefixing via `getKey`, super-large-directory helpers, and `Shutdown`.

## Control Flow

Entry values are encoded and optionally gzipped, then stored by prefixed full-path key with Redis TTL. Directory membership uses a sorted set key `dir + "\x00"` and `ZAddNX` with score 0; listing uses `ZRangeByLex` with inclusive/exclusive start names and server-side count, then fetches each entry and removes expired or missing children.

## State and Persistence Behavior

Metadata and directory indexes persist in Redis. Key prefixing isolates multiple stores sharing one DB. Super-large directories skip directory-index maintenance and child deletion/listing shortcuts.

## Dependencies and Integration Points

Depends on go-redis sorted-set lex operations, `filer.Entry` serialization, SeaweedFS errors, gzip helpers, and `glog`.

## Risks and Edge Cases

Entry and directory-index writes are not atomic. Super-large-directory bypass can make ordinary `ListDirectoryEntries` unable to enumerate those children. TTL is partly handled by Redis key expiration and partly by lazy index cleanup.

## Test Signals

No direct test in subset. Important coverage includes lexicographic pagination, `includeStartFile`, key-prefix collisions, TTL cleanup, stale directory entries, and super-large-directory configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis2/universal_redis_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis2/universal_redis_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis2/universal_redis_store_kv.go

## Purpose

`redis2/universal_redis_store_kv.go` implements Redis v2 generic KV methods. It was read as a complete 42-line file.

## Important APIs, Types, and Functions

`KvPut`, `KvGet`, and `KvDelete` execute `SET`, `GET`, and `DEL` through the v2 `getKey` namespace wrapper. Missing keys map from `redis.Nil` to `filer.ErrKvNotFound`.

## Control Flow

Each API is a single Redis command plus error conversion/wrapping.

## State and Persistence Behavior

KV values persist without TTL under `keyPrefix + string(key)`, sharing the Redis DB with metadata but reducing cross-store collisions.

## Dependencies and Integration Points

Depends on `UniversalRedis2Store.getKey`, go-redis, and filer KV error conventions.

## Risks and Edge Cases

The prefixed namespace is only as safe as caller-provided prefixes. No transaction, CAS, or TTL semantics are provided.

## Test Signals

Generic store tests should verify put/get/update/delete, missing-key errors, and prefix isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis2/universal_redis_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/ItemList.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis3/ItemList.go

## Purpose

`redis3/ItemList.go` implements a Redis-backed batched name list over SeaweedFS skiplist primitives for very large directory-child indexes. It was read as a complete 506-line file.

## Important APIs, Types, and Functions

`ItemList` owns a `skiplist.SkipList`, batch size, Redis client, and key prefix. Core methods are `WriteName`, `DeleteName`, `ListNames`, `RemoteAllListElement`, `ItemAdd`, and many node helpers such as `NodeAddMember`, `NodeRangeBeforeExclusive`, `NodeDeleteAfterExclusive`, and `NodeScanInclusiveAfter`.

## Control Flow

`WriteName` finds the greater-or-equal skiplist node, avoids duplicates, prefers adding to the previous node if there is capacity, splits a full node around the new name, can merge into the next node for reverse-order inserts, or creates a new node. `DeleteName` removes leading-key or in-batch names, deletes empty nodes, and merges adjacent batches when combined size is below the batch limit. `ListNames` starts at the relevant node and scans nodes in order.

## State and Persistence Behavior

The skiplist structure and each node's Redis sorted set persist separately. Node member keys are `prefix + elementPointer + "m"`, while skiplist elements are saved by `SkipListElementStore`. Mutations set skiplist change flags used by serialization.

## Dependencies and Integration Points

Depends on `github.com/seaweedfs/seaweedfs/weed/util/skiplist` and Redis sorted-set lex/count operations. It is used by Redis3 directory-child helpers.

## Risks and Edge Cases

The split/merge logic is complex and uses many independent Redis commands, so interrupted updates can leave skiplist metadata and node member sets inconsistent. `DeleteName` assumes `nextNode.Reference()` can be used when merging, which requires careful nil handling.

## Test Signals

Only a Redis benchmark is listed in this subset. Strong tests should cover ascending/reverse inserts, duplicates, node split boundaries, delete-leading-key, delete-middle, merge, empty-list cleanup, and start-from listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/ItemList.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/item_list_serde.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis3/item_list_serde.go

## Purpose

`redis3/item_list_serde.go` serializes and deserializes `ItemList` skiplist metadata. It was read as a complete 75-line file.

## Important APIs, Types, and Functions

`LoadItemList(data, prefix, client, store, batchSize)` builds an `ItemList`, unmarshals `skiplist.SkipListProto`, and restores max levels plus start/end level references. `HasChanges` exposes the skiplist dirty flag. `ToBytes` marshals current skiplist level references back to protobuf.

## Control Flow

Loading returns an empty list when no bytes exist. On protobuf errors, it logs and still returns an initialized list. Serialization appends non-nil start and end references until the first nil.

## State and Persistence Behavior

This file persists only the skiplist header/references, not node sorted-set members. The caller stores the bytes at the directory-list Redis key.

## Dependencies and Integration Points

Depends on Redis client type, SeaweedFS skiplist package, `proto.Marshal`/`Unmarshal`, and `glog`. It supports `kv_directory_children.go`.

## Risks and Edge Cases

Corrupt serialized bytes are logged but not returned as an error, which can make a bad directory index look like an empty or partially initialized list. Node-member data can diverge from serialized head/tail references.

## Test Signals

Needed tests should round-trip empty and populated lists, corrupt data, nil references, and compatibility after skiplist proto changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/item_list_serde.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/kv_directory_children.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis3/kv_directory_children.go

## Purpose

`redis3/kv_directory_children.go` manages Redis3 directory-child indexes using `ItemList` plus distributed locks. It was read as a complete 139-line file.

## Important APIs, Types, and Functions

`insertChild`, `removeChild`, `removeChildren`, and `listChildren` operate on a directory-list key. `maxNameBatchSizeLimit` is one million names per list node.

## Control Flow

Writes acquire a Redsync mutex at `key + "lock"`, load the serialized `ItemList`, mutate it, and store the serialized header back if changed. `removeChildren` locks, lists all names while invoking a deletion callback, then removes all skiplist elements. `listChildren` performs unlocked read-only list traversal.

## State and Persistence Behavior

Directory state persists as one serialized skiplist header key plus per-node Redis keys. Insert/remove are protected by distributed locks; list is lock-free and may see concurrent changes.

## Dependencies and Integration Points

Depends on Redis3 `UniversalRedis3Store.redsync`, `ItemList`, `SkipListElementStore`, Redis, and `glog`. `UniversalRedis3Store` calls these functions from entry insert/delete/list paths.

## Risks and Edge Cases

Lock acquisition failures fail metadata writes. `mutex.Unlock()` errors are ignored. `removeChildren` does not delete the serialized header key itself in this file, leaving cleanup expectations to callers or overwritten state.

## Test Signals

Only `kv_directory_children_test.go` benchmarks raw Redis sorted-set insertion. Needed tests should cover concurrent insert/delete, list start positions, lock failure, and complete child cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/kv_directory_children.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/kv_directory_children_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis3/kv_directory_children_test.go

## Purpose

`redis3/kv_directory_children_test.go` is a microbenchmark for Redis sorted-set child-name insertion. It was read as a complete 27-line file.

## Important APIs, Types, and Functions

`BenchmarkRedis` starts `tempredis`, creates a Unix-socket Redis client, and repeatedly calls `ZAddNX` against `/yyy/bin` with generated names.

## Control Flow

The benchmark starts an ephemeral Redis server, defers termination, creates a go-redis client, and loops `b.N` times inserting names.

## State and Persistence Behavior

State is temporary Redis data in the tempredis server. No production metadata store is initialized.

## Dependencies and Integration Points

Depends on `github.com/stvp/tempredis`, go-redis, `testing`, and `strconv`. It is loosely related to Redis3 directory child indexing but does not call `ItemList`.

## Risks and Edge Cases

This is performance-only and does not verify correctness, cleanup, locking, skiplist serialization, or concurrent behavior.

## Test Signals

Useful as a low-level sorted-set throughput signal. It should be supplemented by functional Redis3 store tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/kv_directory_children_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_cluster_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_cluster_store.go

## Purpose

`redis3/redis_cluster_store.go` registers the Redis3 cluster store. It was read as a complete 45-line file.

## Important APIs, Types, and Functions

`RedisCluster3Store` embeds `UniversalRedis3Store`. `GetName` returns `redis_cluster3`. `Initialize` reads cluster addresses, password, `useReadOnly`, and `routeByLatency`. `initialize` creates a go-redis cluster client and initializes `redsync` with a goredis pool.

## Control Flow

Startup configures cluster routing, assigns the shared client, then creates the distributed-lock manager required by Redis3 directory-child mutations.

## State and Persistence Behavior

Metadata state is handled by `UniversalRedis3Store` and skiplist child indexes. Redsync uses the same Redis client for lock keys.

## Dependencies and Integration Points

Depends on go-redis cluster, `go-redsync/redsync/v4`, `goredis/v9`, filer store registration, and util configuration.

## Risks and Edge Cases

No startup ping is performed. Distributed lock behavior in Redis Cluster depends on key slot placement and redsync configuration; directory-list lock keys must be reachable consistently.

## Test Signals

No direct tests. Integration should cover directory mutation under cluster, read-only routing interactions, and lock behavior during failover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_cluster_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_sentinel_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_sentinel_store.go

## Purpose

`redis3/redis_sentinel_store.go` registers the Redis3 Sentinel store. It was read as a complete 49-line file.

## Important APIs, Types, and Functions

`Redis3SentinelStore` embeds `UniversalRedis3Store`. `GetName` returns `redis3_sentinel`. Initialization reads Sentinel addresses, master name, username/password, and DB, creates a failover client, and initializes Redsync.

## Control Flow

Startup configures go-redis failover retry/read/write timeouts and attaches a Redsync pool to the failover client.

## State and Persistence Behavior

Persistent state uses Redis3 entry keys and skiplist directory indexes; lock state is transient Redis lock keys.

## Dependencies and Integration Points

Depends on go-redis failover, Redsync, filer registration, and util config.

## Risks and Edge Cases

Failover can interrupt multi-command skiplist updates. The file does not validate the connection during initialize. Lock semantics during master promotion should be tested.

## Test Signals

No direct tests. Needed coverage includes Sentinel failover during insert/delete/list, lock acquisition failure, and metadata recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_sentinel_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_store.go

## Purpose

`redis3/redis_store.go` registers the Redis3 single-node store with optional mTLS and Redsync locking. It was read as a complete 84-line file.

## Important APIs, Types, and Functions

`Redis3Store` embeds `UniversalRedis3Store`. `Initialize` reads address, password, database, and mTLS paths. `initialize` optionally creates TLS config, constructs `redis.NewClient`, and initializes `redsync`.

## Control Flow

With mTLS enabled, it loads client cert/key, CA certs, parses the Redis host, and sets TLS 1.2+ options before constructing the client. Otherwise it creates a plain Redis client. Both branches create the lock manager.

## State and Persistence Behavior

Connection and distributed lock state are configured here; metadata persistence is delegated to Redis3 universal/skiplist files.

## Dependencies and Integration Points

Depends on TLS/x509 libraries, go-redis, Redsync goredis adapter, `glog.Fatalf`, and SeaweedFS configuration.

## Risks and Edge Cases

Configuration errors terminate the process via `Fatalf`. There is no username or key-prefix support in this Redis3 single-node variant. Startup does not ping Redis.

## Test Signals

Needed tests include mTLS success/failure, redsync initialization, and directory child operations through the full Redis3 store.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/redis_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/skiplist_element_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis3/skiplist_element_store.go

## Purpose

`redis3/skiplist_element_store.go` persists skiplist elements for Redis3 directory-child indexes. It was read as a complete 63-line file.

## Important APIs, Types, and Functions

`SkipListElementStore` implements `skiplist.ListStore` with `SaveElement`, `DeleteElement`, and `LoadElement`. `newSkipListElementStore` binds a prefix and Redis client.

## Control Flow

Elements are marshaled with protobuf and stored at `Prefix + id`. Loading gets the Redis value, returns nil for missing keys, unmarshals, and normalizes protobuf "nil" references back to Go nil pointers.

## State and Persistence Behavior

Each skiplist element is a separate Redis key. This state must stay consistent with the serialized list header and per-node member sorted sets.

## Dependencies and Integration Points

Depends on Redis, SeaweedFS skiplist protobuf types, `proto.Marshal`/`Unmarshal`, and `glog`.

## Risks and Edge Cases

Marshal errors are logged but the code still calls `Set` with whatever data was produced. Missing elements return nil without distinguishing corruption from deletion. Context is always `Background`, ignoring request cancellation.

## Test Signals

Needed tests should cover save/load/delete, malformed protobuf data, nil-reference normalization, and interaction with `ItemList` split/merge operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/skiplist_element_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/universal_redis_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis3/universal_redis_store.go

## Purpose

`redis3/universal_redis_store.go` implements Redis3 filer metadata storage, replacing simple directory sets with locked skiplist-backed child indexes. It was read as a complete 203-line file.

## Important APIs, Types, and Functions

`UniversalRedis3Store` owns a `redis.UniversalClient` and `redsync.Redsync`. It implements no-op transactions, `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryEntries`, unsupported prefixed listing, `genDirectoryListKey`, and `Shutdown`.

## Control Flow

Entry bytes are encoded, optionally gzipped, and stored at full-path keys with TTL. Inserts call `insertChild` for the parent. Deletes remove a possible child-list key for the path, delete the entry key, then call `removeChild`. Folder deletion calls `removeChildren`, deleting each child entry and nested list key through a callback. Listing calls `listChildren`, fetches each entry, lazily deletes expired entries, and stops on callback false or limit.

## State and Persistence Behavior

Redis stores entry keys plus directory-list skiplist data. Directory mutations are protected by Redsync, but entry writes and index writes are not one atomic transaction.

## Dependencies and Integration Points

Depends on `ItemList`, Redis3 child helpers, SeaweedFS entry serialization, gzip helpers, filer errors, and `glog`.

## Risks and Edge Cases

Partial insert/delete failures can leave entries and child indexes inconsistent. Expired entries are removed with `ZRem`, but Redis3 child indexes are not simple sorted sets, so this cleanup path may not match the actual index schema.

## Test Signals

No full store tests in this subset. Needed coverage includes CRUD, large directory listing, TTL cleanup, stale index cleanup, lock contention, and folder child deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/universal_redis_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/universal_redis_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/redis3/universal_redis_store_kv.go

## Purpose

`redis3/universal_redis_store_kv.go` implements Redis3 generic KV operations. It was read as a complete 42-line file.

## Important APIs, Types, and Functions

`KvPut`, `KvGet`, and `KvDelete` map to Redis `SET`, `GET`, and `DEL`. Missing keys map to `filer.ErrKvNotFound`.

## Control Flow

Each method executes one Redis command against `string(key)` with basic error wrapping.

## State and Persistence Behavior

KV values persist without TTL in the same Redis namespace as metadata. Unlike Redis2 KV, no key prefix is applied.

## Dependencies and Integration Points

Depends on Redis universal client, context, and filer KV conventions.

## Risks and Edge Cases

Raw key namespace can collide with metadata paths or directory-list keys. No lock or transaction is used for KV operations.

## Test Signals

Generic KV store tests should cover put/get/update/delete, missing-key mapping, and binary key/value round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/redis3/universal_redis_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/remote_mapping.go -->
# sources/distributed-fs/seaweedfs/weed/filer/remote_mapping.go

## Purpose

`remote_mapping.go` reads, inserts, and deletes remote-storage mount mappings stored inside the filer. It was read as a complete 125-line file.

## Important APIs, Types, and Functions

`ReadMountMappings`, `InsertMountMapping`, `DeleteMountMapping`, `addRemoteStorageMapping`, and `removeRemoteStorageMapping` operate on `/etc/remote/mount.mapping` protobuf content.

## Control Flow

Read opens a filer client, reads the mapping file, treats not-found as empty content, and unmarshals mappings. Insert/delete read current content through `WithFilerClient`, modify the protobuf map, marshal, and save it back with `SaveInsideFiler`.

## State and Persistence Behavior

Mappings persist as a serialized `remote_pb.RemoteStorageMapping` file inside the filer metadata namespace. Updates are read-modify-write and not locally transactional.

## Dependencies and Integration Points

Depends on filer gRPC clients, `ReadInsideFiler`, `SaveInsideFiler`, `DirectoryEtcRemote`, `remote_pb`, and protobuf serialization.

## Risks and Edge Cases

Concurrent insert/delete operations can overwrite each other. `addRemoteStorageMapping` ignores unmarshal errors and starts from an empty map, which can discard corrupt existing content. Delete returns unmarshal errors.

## Test Signals

Remote storage tests in this subset cover lookup behavior, not mapping read-modify-write. Needed tests should cover not-found, corrupt protobuf, concurrent update, and save failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/remote_mapping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/remote_storage.go -->
# sources/distributed-fs/seaweedfs/weed/filer/remote_storage.go

## Purpose

`remote_storage.go` loads remote storage configurations and mount mappings, then resolves filer paths to remote storage clients. It was read as a complete 185-line file.

## Important APIs, Types, and Functions

Constants are `REMOTE_STORAGE_CONF_SUFFIX` and `REMOTE_STORAGE_MOUNT_FILE`. `FilerRemoteStorage` owns a prefix trie of mount rules and a `storageNameToConf` map. APIs include `NewFilerRemoteStorage`, `LoadRemoteStorageConfigurationsAndMapping`, `FindMountDirectory`, `FindRemoteStorageClient`, `GetRemoteStorageClient`, `UnmarshalRemoteStorageMappings`, `ReadRemoteStorageConf`, and `DetectMountInfo`.

## Control Flow

Loading lists `DirectoryEtcRemote`, parses `mount.mapping`, unmarshals `*.conf` files into `RemoteConf`, and maps mount dirs into a trie with a trailing slash. Lookup uses prefix matching; `FindMountDirectory` keeps the last prefix match to return the longest mount. Client lookup resolves the storage name through `remote_storage.GetRemoteStorage`.

## State and Persistence Behavior

Runtime state is in-memory trie and config map. Persistent state lives as protobuf files inside filer metadata.

## Dependencies and Integration Points

Depends on SeaweedFS filer APIs, remote protobufs, `remote_storage` client factory, `ptrie`, gRPC helpers, and protobuf serialization.

## Risks and Edge Cases

Mount paths are stored as `dir + "/"`, so the mount root itself does not match as a child path. Loading returns nil early on a non-conf file. `DetectMountInfo` uses map iteration for prefix selection, so longest-prefix behavior is not guaranteed there.

## Test Signals

`remote_storage_test.go` validates child matching and longest-prefix wins for `FindMountDirectory`. Additional tests should cover config loading, bad protobuf, client factory failures, and `DetectMountInfo` longest-prefix behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/remote_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/remote_storage_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/remote_storage_test.go

## Purpose

`remote_storage_test.go` verifies path matching behavior for `FilerRemoteStorage`. It was read as a complete 70-line file.

## Important APIs, Types, and Functions

Tests are `TestFilerRemoteStorage_FindRemoteStorageClient` and `TestFilerRemoteStorage_FindMountDirectory_LongestPrefixWins`.

## Control Flow

The tests build an in-memory `FilerRemoteStorage`, insert `RemoteConf` and mount rules directly, then resolve several paths through `FindRemoteStorageClient` or `FindMountDirectory`.

## State and Persistence Behavior

No filer persistence is used. The tests exercise only in-memory trie and config map state.

## Dependencies and Integration Points

Depends on `remote_pb`, SeaweedFS `util.FullPath`, and `testify/assert`.

## Risks and Edge Cases

The first test confirms that the exact mount directory does not match because rules are stored with a trailing slash and only descendants match. The second protects longest-prefix selection for overlapping mounts.

## Test Signals

Good signal for path-prefix semantics. It does not cover config file loading, remote client construction, mapping protobuf read/write, or `DetectMountInfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/remote_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_store.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_store_kv.go

## Purpose

`rocksdb/rocksdb_store_kv.go` provides generic KV operations for the RocksDB filer store. It was read as a complete 48-line file.

## Important APIs, Types, and Functions

`KvPut` writes with `db.Put`, `KvGet` uses `db.GetBytes`, mapping nil to `filer.ErrKvNotFound`, and `KvDelete` deletes with RocksDB write options.

## Control Flow

Each method performs one RocksDB operation and wraps errors with KV-specific context.

## State and Persistence Behavior

KV data persists under raw byte keys in the same RocksDB database as metadata. There is no namespace separation from `md5(dir)+name` metadata keys.

## Dependencies and Integration Points

Depends on `RocksDBStore` options/DB and filer KV error conventions.

## Risks and Edge Cases

Raw KV keys can collide with metadata key layout if callers use arbitrary bytes. No transaction support or TTL behavior is applied.

## Test Signals

The generic `store_test` suite exercises KV put/get/update for stores that use it; RocksDB-specific tests in this subset do not directly cover KV delete/missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_store_test.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_ttl.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/rocksdb/rocksdb_ttl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/s3iam_conf.go -->
# sources/distributed-fs/seaweedfs/weed/filer/s3iam_conf.go

## Purpose

`s3iam_conf.go` parses, serializes, and validates S3 IAM configuration protobufs. It was read as a complete 56-line file.

## Important APIs, Types, and Functions

`ParseS3ConfigurationFromBytes[T proto.Message]` unmarshals JSON protobuf with unknown-field discard and partial allowed. `ProtoToText` marshals a proto message as indented JSON with unpopulated fields. `CheckDuplicateAccessKey` rejects duplicate access keys across different identities.

## Control Flow

Parsing and marshaling are thin wrappers around `protojson`. Duplicate checking builds an access-key-to-identity map and allows reuse only when the identity name is the same.

## State and Persistence Behavior

The file does not persist directly; it transforms bytes used by S3 configuration stored elsewhere.

## Dependencies and Integration Points

Depends on `iam_pb.S3ApiConfiguration`, `protojson`, `proto.Message`, and the filer/S3 configuration load path.

## Risks and Edge Cases

`AllowPartial` and `DiscardUnknown` make parsing tolerant, which can hide config mistakes. Duplicate access keys within the same named identity are allowed.

## Test Signals

`s3iam_conf_test.go` covers round-trip JSON protobuf serialization and duplicate access-key validation across identities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/s3iam_conf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/s3iam_conf_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/s3iam_conf_test.go

## Purpose

`s3iam_conf_test.go` verifies S3 IAM configuration JSON/protobuf conversion and duplicate access-key validation. It was read as a complete 183-line file.

## Important APIs, Types, and Functions

`TestS3Conf` builds an `iam_pb.S3ApiConfiguration`, calls `ProtoToText`, parses it with `ParseS3ConfigurationFromBytes`, and asserts fields. `TestCheckDuplicateAccessKey` table-tests unique keys, same identity duplicate keys, and cross-identity duplicate keys.

## Control Flow

The tests construct configs in memory and compare exact field values or expected error strings.

## State and Persistence Behavior

No external persistence is used; a bytes buffer holds serialized config.

## Dependencies and Integration Points

Depends on `iam_pb`, S3 action constants, `testify/assert`, and production config helpers.

## Risks and Edge Cases

The tests do not cover malformed JSON, unknown fields, partial messages, duplicate credentials inside one identity with different secret keys, or writer errors.

## Test Signals

Good regression signal for config round-trip and cross-user access-key collision prevention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/s3iam_conf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/sqlite/doc.go -->
# sources/distributed-fs/seaweedfs/weed/filer/sqlite/doc.go

## Purpose

`sqlite/doc.go` documents the SQLite filer store package. It was read as a complete 7-line file.

## Important APIs, Types, and Functions

There are no functions or types. The package comment explains that `modernc.org/sqlite` is large and the package is compiled only in `make full_install`.

## Control Flow

No runtime control flow exists.

## State and Persistence Behavior

No state is defined here; SQLite persistence is implemented in `sqlite_store.go`.

## Dependencies and Integration Points

The file declares package `sqlite` and serves as documentation for build inclusion.

## Risks and Edge Cases

Documentation can drift from build tags or install targets if those change.

## Test Signals

Compile/package documentation coverage only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/sqlite/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/sqlite/sqlite_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/sqlite/sqlite_store.go

## Purpose

`sqlite/sqlite_store.go` registers a SQLite filer metadata store using the shared abstract SQL implementation. It was read as a complete 82-line file.

## Important APIs, Types, and Functions

`SqliteStore` embeds `abstract_sql.AbstractSqlStore`. It registers as `sqlite`, reads `dbFile`, configures create-table and upsert SQL, and `initialize` opens the `modernc.org/sqlite` driver.

## Control Flow

Initialization sets `SupportBucketTable`, installs a MySQL-style SQL generator with SQLite-compatible templates, opens and pings the DB, restricts max open connections to one, and creates the default table.

## State and Persistence Behavior

Metadata persists in a SQLite table with `(dirhash, name)` primary key, directory text, and meta blob. `WITHOUT ROWID` reduces storage overhead.

## Dependencies and Integration Points

Depends on build tags `(linux || darwin || windows) && sqlite`, `database/sql`, `modernc.org/sqlite`, `abstract_sql`, and SeaweedFS store registration.

## Risks and Edge Cases

Single open connection avoids SQLite concurrency issues but limits throughput. Reusing `mysql.SqlGenMysql` with SQLite templates requires care around quoting and generated queries.

## Test Signals

No SQLite-specific tests in this subset. Generic abstract SQL store tests are needed for CRUD, listing, bucket tables, and KV behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/sqlite/sqlite_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/sqlite/sqlite_store_unsupported.go -->
# sources/distributed-fs/seaweedfs/weed/filer/sqlite/sqlite_store_unsupported.go

## Purpose

`sqlite/sqlite_store_unsupported.go` is an unsupported-platform placeholder for the SQLite store. It was read as a complete 9-line file.

## Important APIs, Types, and Functions

It contains only an empty `init` function and a commented-out store registration.

## Control Flow

When its build constraints match, no SQLite store is registered.

## State and Persistence Behavior

No state or persistence is available.

## Dependencies and Integration Points

It exists to make package builds work when the SQLite driver is not supported or not enabled.

## Risks and Edge Cases

The build expression is restrictive and should be checked when adding GOOS/GOARCH support. Users may expect SQLite but get no registered store if tags/platform do not match.

## Test Signals

Compile coverage under unsupported build conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/sqlite/sqlite_store_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/store_test/test_suite.go -->
# sources/distributed-fs/seaweedfs/weed/filer/store_test/test_suite.go

## Purpose

`store_test/test_suite.go` defines a reusable filer-store conformance test. It was read as a complete 71-line file.

## Important APIs, Types, and Functions

`TestFilerStore(t, store)` inserts nested directories and 2000 files, tests paginated directory listing, and tests KV put/get/update. `makeEntry` creates directory or file entries.

## Control Flow

The suite inserts entries directly into a store, lists `/a/b/c` first with limit 3 and then continuing from the returned last file name, and verifies KV overwrites.

## State and Persistence Behavior

State is whatever backend the caller provides. The test assumes lexicographic file names `f00000...` and persistent KV values.

## Dependencies and Integration Points

Used by backend tests such as Tarantool and disabled YDB tests. Depends on `filer.FilerStore`, `util.FullPath`, and `testify/assert`.

## Risks and Edge Cases

It does not test delete, transactions, TTL, prefixed listing, missing-key behavior, or callback errors. Direct `InsertEntry` may bypass higher-level filer parent creation behavior.

## Test Signals

Good shared signal for basic insert/list pagination and KV updates across stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/store_test/test_suite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/stream.go -->
# sources/distributed-fs/seaweedfs/weed/filer/stream.go

## Purpose

`stream.go` streams filer entry content from inline bytes or volume-server chunks, implements sequential chunk streaming, and provides `ChunkStreamReader`. It was read as a complete 532-line file.

## Important APIs, Types, and Functions

Key APIs are `JwtForVolumeServer`, `HasData`, `IsSameData`, `NewFileReader`, `PrepareStreamContentWithThrottler`, `PrepareStreamContentWithPrefetch`, `StreamContent`, `writeZero`, `ChunkStreamReader` constructors, `Read`, `ReadAt`, `Seek`, `Close`, and `VolumeId`. `CacheInvalidator` allows failed chunk reads to invalidate lookup caches.

## Control Flow

Streaming builds `ChunkView` intervals for a requested range, resolves each fileId with retry/backoff, and returns a closure that writes zero-filled gaps and streams chunks with optional throttling. On zero-byte fetch failure it can invalidate cached locations, re-lookup, and retry if locations changed. `ChunkStreamReader` lazily fetches whole chunk views into an internal buffer for read/seek/read-at operations.

## State and Persistence Behavior

State is transient: JWT signing config is loaded once, stream closures hold lookup URL maps, and `ChunkStreamReader` holds current buffer/offset. No metadata persistence occurs.

## Dependencies and Integration Points

Depends on filer protobuf chunks, `wdclient` lookup, security JWT generation, HTTP chunk streaming helpers, stats metrics, throttling utilities, and `ViewFromChunks`.

## Risks and Edge Cases

`IsSameData` sorts chunk slices in place, mutating callers. `ChunkStreamReader.doRead` loops until the caller buffer is full and may return `io.EOF` after partial copy behavior that deserves scrutiny. Retry logic only retries when no bytes were written.

## Test Signals

`stream_prefetch_test.go` and `stream_benchmark_test.go` cover prefetch and sequential benchmarks. Additional tests should cover `ChunkStreamReader` seeks, zero gaps, in-place chunk sorting, and lookup retry failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/stream_benchmark_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/stream_benchmark_test.go

## Purpose

`stream_benchmark_test.go` benchmarks sequential streaming versus pipe-based prefetch streaming under synthetic latency. It was read as a complete 317-line file.

## Important APIs, Types, and Functions

`TestMain` initializes the global HTTP client. Helpers include `mockMasterClientForBenchmark`, `createMockVolumeServer`, `benchmarkConfig`, `setupBenchmark`, `runSequentialBenchmark`, and `runPrefetchBenchmark`. Benchmarks are `BenchmarkStreamSequential`, `BenchmarkStreamSequentialVerify`, `BenchmarkStreamPrefetch`, and `BenchmarkStreamPrefetchVerify`.

## Control Flow

The benchmark creates random chunk data, serves it from `httptest.Server` with optional request latency and range support, maps fileIds to URLs, and repeatedly prepares and runs sequential or prefetch stream closures to `io.Discard`.

## State and Persistence Behavior

State is in-memory chunk data and mock URL maps; no filer store is involved.

## Dependencies and Integration Points

Depends on production streaming APIs, `util_http.InitGlobalHttpClient`, `httptest`, `filer_pb.FileChunk`, and the `wdclient` lookup interface.

## Risks and Edge Cases

Benchmarks include preparation/lookup work inside timed loops, so results measure more than pure streaming. Random data generation is outside timed sections. Verification checks only size, not byte-by-byte equality.

## Test Signals

Useful performance signal for chunk counts, chunk sizes, latency, and prefetch width. Functional signal is limited to no-error and output length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/stream_benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/stream_prefetch.go -->
# sources/distributed-fs/seaweedfs/weed/filer/stream_prefetch.go

## Purpose

`stream_prefetch.go` implements concurrent chunk prefetch streaming using `io.Pipe` to overlap network fetches while preserving response order. It was read as a complete 274-line file.

## Important APIs, Types, and Functions

`chunkPipeResult` tracks one prefetched chunk, its pipe reader, fetch error, bytes written, completion channel, and URL snapshot. `streamChunksPrefetched` is the main pipeline. `retryWithCacheInvalidation` mirrors sequential retry behavior for failed zero-byte fetches.

## Control Flow

The function creates a local cancellable context, a bounded result channel, and a semaphore sized by `prefetchAhead`. A producer walks chunk views in file order, starts fetch goroutines that stream into pipe writers, and sends results in order. The consumer reads each pipe in order, zero-fills gaps, waits for fetch completion, handles retries, updates metrics/throttling, cancels on error, drains remaining pipes, and writes trailing zeroes.

## State and Persistence Behavior

State is transient goroutine, channel, pipe, and pooled copy-buffer state. No data is persisted.

## Dependencies and Integration Points

Depends on `retriedStreamFetchChunkData`, `ChunkView`, `CacheInvalidator`, `urlSlicesEqual`, stats counters, write throttler, and SeaweedFS memory pool.

## Risks and Edge Cases

Deadlock/leak prevention depends on closing pipes, draining results, and waiting on producer/fetch goroutines. Retrying after partial writes is intentionally avoided. `fileId2Url` is read-only during the pipeline.

## Test Signals

`stream_prefetch_test.go` covers ordering, fallback to sequential, cancellation, ranges, oversized prefetch count, and concurrent streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/stream_prefetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/stream_prefetch_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/stream_prefetch_test.go

## Purpose

`stream_prefetch_test.go` validates pipe-based prefetch streaming behavior with mock volume servers. It was read as a complete 365-line file.

## Important APIs, Types, and Functions

Helpers include `testMasterClient`, `noopJwt`, `createTestServer`, and `makeChunksAndServer`. Tests cover in-order delivery, single chunk, fallback to sequential for `prefetchAhead <= 1`, context cancellation, range requests, prefetch count larger than chunk count, and concurrent downloads.

## Control Flow

Tests create random chunk data, serve it over `httptest.Server` with range support, map fileIds to URLs, call `PrepareStreamContentWithPrefetch`, execute the returned stream closure, and compare byte slices or sizes.

## State and Persistence Behavior

State is in-memory chunk maps, URL maps, and request counters. No filer store or volume server persistence is used.

## Dependencies and Integration Points

Depends on streaming APIs, `filer_pb.FileChunk`, `wdclient.LookupFileIdFunctionType`, `httptest`, and Go concurrency primitives.

## Risks and Edge Cases

The cancellation test accepts prepare-time cancellation as expected and logs if all chunks were requested, so it is a softer leak/backpressure signal. Failure retry paths are only indirectly represented by the mock invalidator.

## Test Signals

Strong functional signal for ordering, range correctness, and concurrent use. Additional tests should force fetch failure and URL cache invalidation success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/stream_prefetch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tarantool/doc.go -->
# sources/distributed-fs/seaweedfs/weed/filer/tarantool/doc.go

## Purpose

`tarantool/doc.go` documents the Tarantool filer store package. It was read as a complete 7-line file.

## Important APIs, Types, and Functions

There are no executable declarations beyond package `tarantool`. The comment notes the Tarantool library is large and enabled through `make full_install`.

## Control Flow

No runtime control flow exists.

## State and Persistence Behavior

No persistence is implemented here; see `tarantool_store.go` and `_kv.go`.

## Dependencies and Integration Points

Documentation-only integration with build/install expectations.

## Risks and Edge Cases

The comment can drift if build tags or install targets change.

## Test Signals

Compile/package documentation only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tarantool/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store.go

## Purpose

`tarantool/tarantool_store.go` implements a Tarantool-backed filer metadata store behind the `tarantool` build tag. It was read as a complete 324-line file.

## Important APIs, Types, and Functions

`TarantoolStore` owns a `pool.ConnectionPool`. It registers as `tarantool`, initializes pool instances, implements no-op transactions, entry CRUD, folder child deletion, directory listing, and `Shutdown`. Constants include `tarantoolSpaceName = "filer_metadata"`.

## Control Flow

Initialization parses comma-separated addresses, timeout, and reconnect settings, creates pool instances, connects, and pings. Inserts encode metadata, optional-gzip it, compute an absolute TTL epoch, and perform a CRUD upsert. Finds use CRUD get with read/replica preferences. Listing and folder deletion call Tarantool stored functions.

## State and Persistence Behavior

Metadata persists in Tarantool space `filer_metadata` with fields including directory, name, TTL, and data. Directory indexing/deletion behavior relies on Tarantool-side schema/functions.

## Dependencies and Integration Points

Depends on `go-tarantool/v2`, `crud`, `pool`, SeaweedFS filer serialization, and `filer_pb.ErrNotFound`.

## Risks and Edge Cases

Correctness depends on external Tarantool schema and stored functions being installed. Type assertions on returned rows can fail at runtime. Transactions are no-ops in Go.

## Test Signals

`tarantool_store_test.go` gates the generic store suite behind `RUN_TARANTOOL_TESTS=1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store_kv.go

## Purpose

`tarantool/tarantool_store_kv.go` implements generic KV operations for the Tarantool store. It was read as a complete 94-line file.

## Important APIs, Types, and Functions

`tarantoolKVSpaceName` is `key_value`. `KvPut` upserts key/value rows, `KvGet` reads the `value` field with replica preferences and maps missing/shape mismatches to `filer.ErrKvNotFound`, and `KvDelete` deletes by key.

## Control Flow

All operations use Tarantool CRUD requests through the connection pool. Get parses the nested `crud.Result.Rows` shape and validates the value is a string.

## State and Persistence Behavior

KV state persists in Tarantool space `key_value`. Values are converted to strings for storage and back to bytes on read.

## Dependencies and Integration Points

Depends on Tarantool CRUD, pool routing, and filer KV error semantics.

## Risks and Edge Cases

Binary values pass through Go strings and depend on Tarantool field type compatibility. Runtime row shape/type changes produce errors. No TTL or transaction support is provided.

## Test Signals

The generic store suite invoked by Tarantool tests covers KV put/get/update, but not delete or missing-key behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store_test.go

## Purpose

`tarantool/tarantool_store_test.go` wires the Tarantool store into the shared filer store test suite. It was read as a complete 23-line file.

## Important APIs, Types, and Functions

`TestStore` checks `RUN_TARANTOOL_TESTS`; if enabled, it initializes a `TarantoolStore` at `127.0.1:3303` with user/password `client` and calls `store_test.TestFilerStore`.

## Control Flow

The test skips by default, requiring external Docker/test environment setup. When enabled, it opens a live store and runs shared CRUD/list/KV assertions.

## State and Persistence Behavior

State is in the external Tarantool instance and is not isolated by this file beyond whatever the environment provides.

## Dependencies and Integration Points

Depends on build tag `tarantool`, environment variable gating, and the shared `store_test` suite.

## Risks and Edge Cases

Hardcoded address/credentials and external state can make tests flaky or destructive if not run in the expected Docker setup.

## Test Signals

Provides integration coverage only when explicitly enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tikv/tikv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/tikv/tikv.go

## Purpose

`tikv/tikv.go` is a package documentation/placeholder file for the TiKV filer store. It was read as a complete 6-line file.

## Important APIs, Types, and Functions

There are no runtime declarations beyond package `tikv`. The comment notes the build works without TiKV tag and `make full_install` enables the store.

## Control Flow

No control flow.

## State and Persistence Behavior

No state; persistence lives in `tikv_store.go`.

## Dependencies and Integration Points

Documentation-only build integration.

## Risks and Edge Cases

Comment drift relative to build tags/install process.

## Test Signals

Compile/package documentation only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tikv/tikv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tikv/tikv_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/tikv/tikv_store.go

## Purpose

`tikv/tikv_store.go` implements a TiKV-backed transactional filer metadata store behind the `tikv` build tag. It was read as a complete 466-line file.

## Important APIs, Types, and Functions

`TikvStore` owns a `txnkv.Client`, `onePC`, `batchCommitSize`, and `keyPrefix`. It implements filer store CRUD, folder-child batch deletion, prefixed listing, transactions, `TxnWrapper`, key hashing helpers, and `Shutdown`.

## Control Flow

Initialization configures TiKV security, PD addresses, key prefix, one-phase commit, and batch delete size. Entry keys are `keyPrefix + sha1(dir) + name`. Operations get a transaction from context or create one, run the operation, and auto-commit unless participating in an outer transaction. Directory deletion scans by prefix and deletes in batches. Listing iterates lexicographic keys, filters start/include/prefix, lazily deletes expired entries, and invokes callbacks.

## State and Persistence Behavior

Metadata persists in TiKV under hashed directory prefixes. Transactions are real TiKV transactions when `BeginTransaction` is used; otherwise each operation creates and commits its own transaction.

## Dependencies and Integration Points

Depends on `tikv/client-go/v2/txnkv`, TiKV security config, SeaweedFS entry serialization, `filer_pb.ErrNotFound`, and `glog`.

## Risks and Edge Cases

`isNotExists` checks `err.Error() == "not exist"`, which is brittle. Directory hash collisions are possible in theory. `KvPut` in the companion file does not apply keyPrefix. TTL cleanup during list calls `DeleteEntry` while iterating in a transaction, which can interact with transaction context.

## Test Signals

No TiKV-specific tests in this subset. Needed coverage includes transaction commit/rollback, batch deletion, prefix listing, TTL cleanup, key prefixing, and missing-key errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tikv/tikv_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tikv/tikv_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/tikv/tikv_store_kv.go

## Purpose

`tikv/tikv_store_kv.go` implements generic KV operations for the TiKV store. It was read as a complete 49-line file.

## Important APIs, Types, and Functions

`KvPut`, `KvGet`, and `KvDelete` use `store.getTxn(ctx)` and `TxnWrapper.RunInTxn` to set/get/delete keys. Missing gets map through `isNotExists` to `filer.ErrKvNotFound`.

## Control Flow

Each operation either joins an existing transaction from context or opens and commits its own transaction.

## State and Persistence Behavior

KV data persists under raw keys passed by the caller, unlike metadata keys that use `store.getKey` keyPrefix. This can be intentional global KV behavior or a namespace inconsistency.

## Dependencies and Integration Points

Depends on TiKV `txnkv.KVTxn`, `TikvStore` transaction wrapper, and filer KV errors.

## Risks and Edge Cases

No keyPrefix is applied here, so multiple stores sharing TiKV can collide. Missing-key detection uses brittle string matching. No TTL or CAS semantics.

## Test Signals

Generic store tests should cover put/get/update/delete and transaction integration; explicit prefix isolation tests are advisable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/tikv/tikv_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/topics.go -->
# sources/distributed-fs/seaweedfs/weed/filer/topics.go

## Purpose

`topics.go` defines filer paths used for SeaweedFS topic metadata and system logs. It was read as a complete 7-line file.

## Important APIs, Types, and Functions

Constants are `TopicsDir = "/topics"`, `SystemLogDir = TopicsDir + "/.system/log"`, and `TopicConfFile = "topic.conf"`.

## Control Flow

No runtime control flow.

## State and Persistence Behavior

The constants identify filer namespace locations where other components store topic configuration and logs.

## Dependencies and Integration Points

Used by topic/log features outside this subset as stable path contracts.

## Risks and Edge Cases

Changing these constants would be a metadata compatibility break for existing topic data.

## Test Signals

Compile-time references and integration tests in topic components should protect these path constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/topics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/doc.go -->
# sources/distributed-fs/seaweedfs/weed/filer/ydb/doc.go

## Purpose

`ydb/doc.go` documents the YDB filer store package. It was read as a complete 7-line file.

## Important APIs, Types, and Functions

No executable declarations beyond package `ydb`. The comment notes the YDB SDK is large and the store is enabled by `make full_install`.

## Control Flow

No runtime flow.

## State and Persistence Behavior

No state; YDB persistence is implemented in other package files.

## Dependencies and Integration Points

Documentation-only integration with build/install expectations.

## Risks and Edge Cases

Comment drift as build tags or install targets evolve.

## Test Signals

Compile/package documentation only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_queries.go -->
# sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_queries.go

## Purpose

`ydb/ydb_queries.go` defines YDB SQL query templates for filer metadata and KV operations. It was read as a complete 73-line file.

## Important APIs, Types, and Functions

Constants include `upsertQuery`, `deleteQuery`, `findQuery`, `deleteFolderChildrenQuery`, `listDirectoryQuery`, and `listInclusiveDirectoryQuery`. Each embeds `PRAGMA TablePathPrefix("%v")` and typed YDB parameter declarations.

## Control Flow

No Go runtime flow beyond constant use. `withPragma` in `ydb_types.go` formats these templates with a concrete table prefix before execution.

## State and Persistence Behavior

Queries operate on `abstract_sql.DEFAULT_TABLE`, using `(dir_hash, directory, name)` keys, `meta`, and optional `expire_at`.

## Dependencies and Integration Points

Depends on abstract SQL default table naming and YDB query syntax. Used by `YdbStore` entry and KV methods.

## Risks and Edge Cases

`LIKE prefix+"%"` semantics may treat SQL wildcard characters in prefixes specially. Template formatting must never accept untrusted table prefixes.

## Test Signals

YDB integration tests should cover upsert/find/delete/list inclusive/exclusive, prefix listing with special characters, and folder child deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_queries.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_store.go

## Purpose

`ydb/ydb_store.go` implements a YDB-backed filer metadata store with optional per-bucket tables. It was read as a complete 518-line file.

## Important APIs, Types, and Functions

`YdbStore` owns the YDB driver, bucket folder/prefix settings, partitioning options, max list chunk, and a cached bucket-table map. It implements initialization, query execution helper `doTxOrDB`, entry CRUD, listing, transactions, bucket-aware hooks, table creation/deletion, prefix resolution, and shutdown.

## Control Flow

Initialization opens YDB using env credentials and DSN, sets defaults, derives table path prefix, and ensures tables. Entry upsert encodes metadata, optional-gzips it, resolves bucket/table prefix, and executes query templates with parameters. Listing loops in chunks up to `maxListChunk`, switching inclusive/exclusive start query as needed and updating `startFileName`. Bucket hooks create/drop bucket-specific tables.

## State and Persistence Behavior

Metadata persists in YDB tables with TTL column support and partitioning settings. Optional bucket mode routes bucket subtrees to separate tables and caches verified bucket table existence.

## Dependencies and Integration Points

Depends on YDB SDK driver/query/table APIs, env auth, SeaweedFS filer entry serialization, bucket-aware interface, abstract SQL constants, and query/type helper files.

## Risks and Edge Cases

`BeginTransaction` uses table transactions while `doTxOrDB` checks for `query.Transaction`, so transaction integration appears type-inconsistent. Bucket prefix detection depends on configured buckets folder and cached table existence. List prefix uses SQL `LIKE`.

## Test Signals

`ydb_store_test.go` contains a disabled generic store test. Live YDB integration should cover bucket tables, transactions, TTL, chunked listing, and KV methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_store_kv.go

## Purpose

`ydb/ydb_store_kv.go` implements generic KV operations on top of the YDB metadata table schema. It was read as a complete 82-line file.

## Important APIs, Types, and Functions

`KvPut` maps a raw key into directory/hash/name via `abstract_sql.GenDirAndName`, creates `FileMeta`, and runs `upsertQuery`. `KvGet` runs `findQuery` and scans `meta`. `KvDelete` runs `deleteQuery`.

## Control Flow

Each operation uses `store.DB.Query().Do` with idempotent execution and table query parameters. Missing reads return `filer.ErrKvNotFound`.

## State and Persistence Behavior

KV data persists in the base YDB table path, not bucket-specific tables. TTL is zero for KV puts.

## Dependencies and Integration Points

Depends on YDB query sessions, table parameter types, `abstract_sql.GenDirAndName`, `FileMeta`, and shared query templates.

## Risks and Edge Cases

KV methods bypass `doTxOrDB`, so they do not join `YdbStore` transactions. They also use only `store.tablePathPrefix`, not per-bucket routing.

## Test Signals

Generic KV tests are needed for put/get/update/delete, missing keys, transaction expectations, and binary key/value behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_store_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_store_test.go

## Purpose

`ydb/ydb_store_test.go` is a placeholder integration test for the YDB store. It was read as a complete 20-line file.

## Important APIs, Types, and Functions

`TestStore` contains an `if false` block that would initialize `YdbStore` against local YDB and run `store_test.TestFilerStore`.

## Control Flow

As written, the test never executes the store initialization or suite.

## State and Persistence Behavior

No state is created unless the guard is changed. The commented setup targets `grpc://localhost:2136/?database=local`.

## Dependencies and Integration Points

Depends on build tag `ydb` and the shared store test suite, but currently provides no runtime coverage.

## Risks and Edge Cases

The disabled test can hide regressions in a complex backend. Hardcoded local settings need an explicit environment gate similar to Tarantool.

## Test Signals

No active test signal. Converting the guard to an environment variable would enable optional integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_types.go -->
# sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_types.go

## Purpose

`ydb/ydb_types.go` defines YDB row types, table creation options, and query formatting helpers. It was read as a complete 65-line file.

## Important APIs, Types, and Functions

`FileMeta` holds `DirHash`, `Name`, `Directory`, and `Meta`; `FileMetas` is a slice alias. `FileMeta.queryParameters` builds query parameters including optional `expire_at`. `YdbStore.createTableOptions` builds schema, TTL, primary key, and partitioning options. `withPragma` formats query templates with table path prefix.

## Control Flow

TTL parameter is optional: positive `ttlSec` becomes a uint32 optional value, otherwise null. Table creation sets TTL mode to seconds since Unix epoch and partitions by `dir_hash` and `name`.

## State and Persistence Behavior

Defines YDB persistent schema: primary key `(dir_hash, directory, name)`, `meta` bytes, and `expire_at` TTL column.

## Dependencies and Integration Points

Depends on YDB table/types/options APIs and is used by `ydb_store.go` and `ydb_store_kv.go`.

## Risks and Edge Cases

`queryParameters` stores `ttlSec` directly as `expire_at`, but YDB TTL mode expects Unix epoch seconds; callers passing relative TTL seconds can expire rows unexpectedly. Query formatting must not expose untrusted prefixes.

## Test Signals

Needed tests should validate table options, TTL semantics, and generated query parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_account_collapse_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/auth_account_collapse_test.go

## Purpose

`s3api/auth_account_collapse_test.go` protects S3 IAM account ownership behavior for account-less identities. It was read as a complete 131-line file.

## Important APIs, Types, and Functions

Tests are `TestAccountForUnscopedIdentity`, `TestUnscopedIdentitiesGetDistinctAccounts`, `TestCheckAccessByOwnershipDeniesNonOwner`, `TestUnscopedIdentityAccountResolvesByName`, and `TestUnscopedIdentityReusesConfiguredAccount`.

## Control Flow

Tests reset the memory store, write temporary JSON configs, initialize IAM, look up identities by access key, and assert account IDs/display names. Ownership access is tested with an in-memory `BucketRegistry` and HTTP requests carrying `AmzAccountId`.

## State and Persistence Behavior

Temporary config files and in-memory IAM/account stores are used. The tests verify synthesized accounts are registered and do not collapse to admin except for conventional admin/empty identity.

## Dependencies and Integration Points

Depends on IAM config loading, memory account store, S3 bucket ownership checks, AWS S3 owner type, and S3 constants/errors.

## Risks and Edge Cases

Regressions here can make non-admin unscoped users inherit admin ownership or fail ACL owner resolution. Tests do not cover persistent IAM stores.

## Test Signals

Strong regression coverage for account isolation, owner access denial, account-name lookup, and configured-account reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_account_collapse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_copy_source_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/auth_copy_source_test.go

## Purpose

`s3api/auth_copy_source_test.go` verifies authorization of the source object in S3 CopyObject flows. It was read as a complete 304-line file.

## Important APIs, Types, and Functions

`newCopyRequest` builds destination PUT requests with `X-Amz-Copy-Source`. Tests cover auth disabled, nil identity denial, admin bypass, prefix-scoped identities, IAM integration receiving source resource, IAM allow, versionId propagation, presigned URL session token preservation, and preservation of the copy-source header.

## Control Flow

Tests construct `IdentityAccessManagement` instances directly, often with `MockIAMIntegration`, then call `AuthorizeCopySource(req, identity, sourceBucket, sourceObject, versionId)` and inspect returned S3 errors plus captured synthetic request fields.

## State and Persistence Behavior

State is in-memory IAM identity configuration and request objects. Tests assert the original destination request is not mutated when a synthetic GET request is built for source authorization.

## Dependencies and Integration Points

Depends on IAM action resolution, STS/IAM integration hooks, S3 constants/errors, HTTP request handling, and copy-source parsing semantics.

## Risks and Edge Cases

The covered regressions include authorizing only the destination, dropping STS session tokens from presigned URLs, losing `versionId`, mutating the original PUT, or omitting `X-Amz-Copy-Source` from policy condition evaluation.

## Test Signals

Strong focused regression signal for CopyObject source authorization and STS/IAM behavior. Additional tests could cover URL-encoded source keys and malformed copy-source headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_copy_source_test.go -->
