# subset-b-007611 Research

Grouped source research for the JuiceFS Redis metadata backend, Redis backup/load support, client-side caching, lock handling, batch clone tests, and slice layout helpers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis.go -->
# sources/distributed-fs/juicefs/pkg/meta/redis.go

## Purpose

`redis.go` is the main Redis-backed implementation of JuiceFS metadata. It registers the `redis`, `rediss`, and `unix` metadata engines, constructs a `redisMeta`, maps inode, directory, chunk, xattr, quota, ACL, lock, session, trash, and changelog state into Redis keys, and implements most filesystem metadata operations through Redis commands, pipelines, Lua lookup helpers, and optimistic transactions.

## Important APIs, Types, and Functions

`redisMeta` embeds `baseMeta` and stores a `redis.UniversalClient`, cluster hash-tag prefix, loaded Lua script SHAs, and optional `redisCache`. `newRedisMeta` parses URLs and query parameters, configures TLS/passwords/retry/read routing, detects standalone, Sentinel, and Cluster Redis, installs client-side cache when requested, and checks Redis server eviction policy.

Key helpers include `inodeKey`, `entryKey`, `chunkKey`, `sliceKey`, `xattrKey`, quota key helpers, `packEntry`, `parseEntry`, `packQuota`, `parseQuota`, `scan`, `hscan`, `txn`, `shouldRetry`, and `genLog`. Core metadata methods include initialization/session handling, lookup/resolve/getattr, create/link/unlink/rmdir/rename, truncate/fallocate/setattr/readlink, read/list/write/copy-file-range, xattrs, quotas, ACLs, Kerberos token storage, dump/load, clone/batch clone, detached directory handling, and `redisDirHandler` directory pagination.

## Control Flow

Construction builds a Redis client first, then the metadata object. Standalone clients are tried unless the target reports cluster mode; cluster clients use a hash-tag prefix based on DB number so multi-key operations stay in one slot. `doInit` reads or writes the `setting` JSON, creates root/trash inodes, and removes stale dir-stat or user/group quota maps when enabling those features on an existing volume.

Most mutating operations go through `txn`, which validates prefix ownership for watched keys, takes a local striped transaction lock, calls Redis `WATCH`, retries selected transient failures, converts returned `syscall.Errno` through `errNo`, and records transaction restart metrics. Individual methods load current attrs and entries, apply permission and flag checks, compute quota/stat deltas, then execute a `TxPipelined` write set. `genLog` appends changelog entries to `txnLog` and increments `txnLastLog` when the format enables changelogs.

Lookup prefers an entry cache, then optional Lua `scriptLookup`/`scriptResolve` for fast server-side path lookup when no prefix/case-insensitive mode is active, then falls back to `HGET` directory entry plus `GET` inode attr. Create, link, unlink, rmdir, and rename update directory hashes, inode attrs, parent maps for hard links, trash entries, delayed deletion queues, total inode and used-space counters, quota usage, and open-file/sustained state. Chunk writes append 24-byte slice records to per-inode chunk lists and update file length/accounting; copy-file-range and clone copy existing slice records and increment shared slice reference counts.

Cleanup and inspection flows scan Redis keyspace. They find stale sessions, release locks, delete sustained inodes, list delayed files and slices, clean leaked chunks/inodes/slice refs, compact chunks, enumerate slices for GC, and scan pending trash/deleted data. Dump/load supports a JSON-style tree dump in this file, while `redis_bak.go` supplies the protobuf segment dump/load path.

## State and Persistence Behavior

Persistent metadata is encoded directly into Redis. Inodes live at `i$inode`, directory entries at `d$parent` hash fields, chunks at `c$inode_$index` lists of 24-byte slice records, symlinks at `s$inode`, xattrs at `x$inode`, parent link counts at `p$inode`, sessions in sorted sets/hashes, sustained open-deleted inodes in per-session sets, deleted files in `delfiles`, delayed slice cleanup in `delSlices`, slice references in `sliceRef`, quotas and dir stats in dedicated hashes, ACLs in `acl`, and Kerberos tokens in `krbToken`.

Runtime state includes open-file tracking in `baseMeta`, in-memory used counters, transaction locks and metrics, ACL cache, optional Redis client-side cache, and loaded Lua SHAs. For Redis Cluster, all keys are prefixed with a common hash tag. Redis counters `nextinode` and `nextchunk` store the last allocated value, so dump/load paths adjust by one compared with engines that store the next value.

## Dependencies and Integration Points

This file depends on `github.com/redis/go-redis/v9`, Redis Sentinel/Cluster behavior, optional Redis client-side tracking, JuiceFS `baseMeta`, ACL rules, quota/stat helpers, chunk/slice helpers from `slice.go`, lock helpers from `redis_lock.go`, and dump structures. It integrates with object deletion through `deleteSlice`, `fileDeleted`, `tryDeleteFileData`, directory stat propagation, quota accounting, open-file cache invalidation, and higher-level `Meta` methods implemented by `baseMeta`.

## Risks and Edge Cases

Multi-key correctness relies on all watched keys sharing the expected prefix/hash slot. Redis transaction failures are retried only for selected transient conditions; non-idempotent operations can leave externally visible partial state when a pipeline command fails after earlier commands applied. The batch clone tests explicitly document such a partial-write risk under `sliceRef` wrong-type injection. Directory and quota counters can drift and require sync/repair paths. Trash, hard links, open deleted files, and parent maps create complex accounting paths. Lua lookup is disabled for cluster-prefixed or case-insensitive modes and must reload on `NOSCRIPT`. Key scanning in cluster mode uses the master for the prefix key and assumes the hash-tagged layout. Redis eviction policies other than `noeviction` are dangerous for metadata and only best-effort reconfigured.

## Test Signals

High-value tests should cover Redis URL modes, TLS/password handling, cluster prefix behavior, init upgrades, lookup cache/Lua fallback, each mutating filesystem path, hard links, trash and skip-trash flags, open deleted file cleanup, dir-stat and quota drift repair, changelog scan/cleanup, dump/load round trips, chunk compaction and GC scans, ACL/token handling, and Redis failure injection around transactions and pipelines. Existing companion tests focus on client-side cache invalidation and batch clone reference/accounting behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis_bak.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis_bak.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis_batchclone_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/redis_batchclone_test.go

## Purpose

`redis_batchclone_test.go` is an integration test suite for Redis `BatchClone` behavior. It verifies that Redis batch cloning handles shared chunk references, mixed file/symlink entries, duplicate names, filesystem space/inode accounting, multi-chunk files, deleted sources, and a known partial-failure mode.

## Important APIs, Types, and Functions

`newTestRedisMeta` creates a Redis metadata engine against `127.0.0.1:6379/<db>`, resets it, initializes the test format, and registers cleanup. `redisSliceRefCount` reads Redis `sliceRef` values directly. Test cases call public metadata APIs such as `Mkdir`, `Mknod`, `NewSlice`, `Write`, `Link`, `Symlink`, `Readdir`, `Lookup`, `ReadLink`, `Unlink`, `StatFS`, and `m.getBase().BatchClone`.

## Control Flow

Each test builds source and destination directories in a fresh Redis DB, creates representative entries, obtains source directory entries through `Readdir`, filters out `.` and `..`, invokes `BatchClone`, and checks cloned count plus Redis-visible side effects. Shared chunk tests hard-link two names to one source inode and require slice ref increments for both cloned files. Mixed tests verify file and symlink cloning. Duplicate-name tests pass a synthetic batch with duplicate destination names and expect one clone. Space accounting waits briefly for `StatFS` deltas to match expected aligned sizes and inode counts. The deleted-source test passes 1001 entries to exercise batching and verifies a source unlinked after listing is skipped. The partial-failure test changes `sliceRef` to the wrong Redis type and documents that a failed clone can still leave a visible destination entry and accounting changes.

## State and Persistence Behavior

Tests use Redis DBs 7, 9, and 11 through 15 and call `Reset`, so they mutate a live local Redis instance. They inspect persistent Redis hashes/lists through the production key helpers. The partial-failure test intentionally corrupts the `sliceRef` key type and expects persisted clone state to remain after failure.

## Dependencies and Integration Points

The suite depends on a local Redis server, the non-`noredis` build, JuiceFS test config/format helpers, and Redis backend implementation in `redis.go`. It is tightly coupled to Redis slice reference semantics and to `BatchClone` aggregation in `baseMeta`.

## Risks and Edge Cases

Tests are integration-style and will fail if Redis is unavailable or if the selected DBs are used concurrently by other tests. `newTestRedisMeta` resets the database, so it must never run against a non-test Redis DB. Directory listing order is not assumed except for counts. The partial-failure test is intentionally a current-behavior test, not a success guarantee; it records a consistency risk that should be revisited if Redis batch clone is made atomic.

## Test Signals

These tests provide strong signals for slice ref accounting, hard-link flattening to independent cloned files, symlink target preservation, duplicate entry filtering, multi-chunk list copying, batch boundaries above 1000 entries, and state after Redis command failures. Missing coverage includes ACL/xattr preservation in batch clone, quota enforcement, case-insensitive destinations, directories being skipped, and concurrent destination conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis_batchclone_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis_csc.go -->
# sources/distributed-fs/juicefs/pkg/meta/redis_csc.go

## Purpose

`redis_csc.go` adds optional Redis client-side caching for the Redis metadata engine. It caches inode attrs and directory entry lookups, subscribes to Redis invalidation push notifications, and hooks go-redis command processing to serve safe local reads and invalidate local entries after writes.

## Important APIs, Types, and Functions

`cachedEntry` stores an inode, entry generation term, and attr; an inode value of zero marks an in-flight lookup. `redisCache` stores the Redis client, prefix, capacity, expiry, preload count, pubsub subscription, inode LRU, entry LRU, and per-parent entry generation LRU. `newRedisCache`, `init`, `parse`, `entryName`, `entryTerm`, `bumpEntryTerm`, `HandlePushNotification`, `beforeProcess`, `afterProcess`, `ProcessHook`, `onInvalidateConnect`, `preloadCache`, and `bytesToString` are the main functions.

## Control Flow

Initialization obtains a standalone Redis client or the cluster master for the metadata prefix, installs `OnConnect`, subscribes to `__redis__:invalidate`, registers a push notification handler, and adds itself as a go-redis hook. On cache-specific reconnect, `onInvalidateConnect` purges all local caches, turns tracking off, and enables Redis `CLIENT TRACKING ON BCAST PREFIX <i-prefix> PREFIX <d-prefix>`.

For `GET i...`, `beforeProcess` returns cached inode bytes when present and not a mark; otherwise it stores an empty mark before allowing Redis access. `afterProcess` fills a marked inode cache entry from successful `GET`, removes inode cache entries after successful `SET`, and removes exact entry cache names after `HSET`/`HDEL` on directory hashes. Push invalidations remove inode cache entries or bump a directory parent generation, making older entry cache records stale without eagerly deleting every child name. `doLookup` in `redis.go` uses marks and generation comparisons to avoid filling stale directory entries. `preloadCache` optionally reads root directory entries after session creation.

## State and Persistence Behavior

All cache state is in-process and expirable. It persists no filesystem metadata and relies on Redis invalidation notifications plus TTL expiry to avoid stale reads. Entry generation terms are kept longer than entry values and are refreshed on access. The cache does not hook pipelines because `ProcessPipelineHook` returns nil.

## Dependencies and Integration Points

It depends on Redis RESP3/push notification support through go-redis, Hashicorp expirable LRU, `redisMeta.doLookup`, `doGetAttr`, and `doReaddir`, plus Redis server-side client tracking. It is configured from `newRedisMeta` query parameters `client-cache`, `client-cache-size`, `client-cache-expire`, and `client-cache-preload`.

## Risks and Edge Cases

Correctness depends on receiving invalidations for all metadata-writing connections and on generation checks preventing stale entry refills. The hook bypasses Redis only for simple `GET` inode commands, not pipelines. `bytesToString` is an unsafe zero-copy conversion, so cached byte slices must not be mutated after being returned as strings. The `DialHook` returning nil is unusual but acceptable for this hook shape. Preloading can conflict with concurrent root directory changes and is bounded by the generation checks.

## Test Signals

Tests should verify invalidation handling, TTL expiry, inode hook read-through and set invalidation, entry hook invalidation on hset/hdel, generation bump behavior, stale entry rejection while generation is active, idle generation expiry/refresh, and concurrent stale refill races. Existing `redis_csc_test.go` covers these signals against a live Redis server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis_csc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis_csc_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/redis_csc_test.go

## Purpose

`redis_csc_test.go` tests Redis client-side cache behavior for inode cache invalidation, entry cache invalidation, entry generation staleness checks, expiry, and concurrent refill safety.

## Important APIs, Types, and Functions

`mockRedisCSCMeta` creates a Redis metadata engine at `127.0.0.1:6379/10?client-cache=true`. `TestRedisCache` contains subtests for invalidation handling, cache expiration, inode hook, entry hook, entry generation invalidation, idle term expiry, term refresh on access, mark refill rules, stale entry rejection, and concurrent stale refill attempts. It uses `require` from testify and Redis push notification types.

## Control Flow

The test flushes Redis DB 10, then manipulates cache internals and Redis keys directly. It adds inode attrs or entry values into LRUs, mutates Redis with `SET`, `HSET`, and `HDEL`, sleeps where necessary for async invalidations or expiry, and asserts cache entries are removed or considered stale. Several subtests construct standalone `redisCache` instances with very short expiry to check LRU timing without Redis. The concurrency subtest starts multiple goroutines that attempt to refill an old generation mark and verifies they cannot overwrite a newer mark.

## State and Persistence Behavior

The test mutates a live local Redis database and in-memory cache objects. `FlushAll` clears the Redis instance, not only DB 10, which makes this test unsuitable for shared Redis environments. Most assertions inspect process-local LRU state rather than persisted metadata.

## Dependencies and Integration Points

It depends on Redis client-side tracking behavior, async invalidation timing, go-redis hooks from `redis_csc.go`, `Attr.Marshal`/`Unmarshal`, and the test Redis server. It validates behavior that `redis.go` relies on for `doLookup` cache marks and term checks.

## Risks and Edge Cases

Time-based sleeps make the test sensitive to slow Redis or overloaded CI. `FlushAll` can interfere with other Redis-backed tests if run in parallel. Push invalidation behavior depends on Redis server version and protocol behavior. Short expiry tests need enough margin to avoid flakes, and the current sleeps are deliberately multiples of expiry.

## Test Signals

The file gives direct evidence that cached inode reads are served through the Redis hook, `SET` invalidates inode cache, `HSET`/`HDEL` invalidate exact entry names, parent invalidation bumps terms, stale cache entries are not accepted after a term bump, refill requires an existing mark and current generation, and concurrent old-generation refills do not overwrite a newer mark.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis_csc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis_lock.go -->
# sources/distributed-fs/juicefs/pkg/meta/redis_lock.go

## Purpose

`redis_lock.go` implements BSD-style flock and POSIX byte-range locks for the Redis metadata backend. It stores lock ownership in Redis hashes and tracks which lock keys belong to the current session for stale-session cleanup.

## Important APIs, Types, and Functions

`Flock` handles whole-file shared, exclusive, and unlock operations using `lockf$inode` hashes. `Getlk` inspects POSIX range lock conflicts in `lockp$inode`. `Setlk` adds, updates, merges, splits, or removes POSIX byte-range locks through helper functions such as `loadLocks`, `updateLocks`, and `dumpLocks` from the broader package. `ListLocks` returns parsed POSIX and flock items for diagnostics.

## Control Flow

`Flock` builds an owner field from session ID and owner ID. Unlock removes that field and removes the lock key from the session's `locked$sid` set if it was the last owner. Read locks ignore locks by the same owner and conflict only with other write locks. Write locks require no other owners. Blocking locks retry on `EAGAIN` with short sleeps and return `EINTR` if the context is canceled.

`Getlk` reads all POSIX lock owners except the caller and returns the first overlapping conflicting lock when either requested or existing lock is write. `Setlk` unlocks by updating the caller's serialized lock list and deleting the owner field if empty. For read/write locks, it checks other owners for overlapping write conflicts, updates the caller's lock list, writes it back, and records the lock key in `locked$sid`. All mutations go through `redisMeta.txn` and can emit changelog records.

## State and Persistence Behavior

Flock state is persisted as `lockf$inode` hash fields `sid_owner -> "R"` or `"W"`. POSIX locks are persisted as `lockp$inode` hash fields `sid_owner -> serialized plock records`. The current session's `locked$sid` set references lock keys so stale session cleanup can release them. Lock state is metadata-only and does not alter inode attrs.

## Dependencies and Integration Points

The file depends on Redis transactions from `redis.go`, owner key formatting from `redisMeta.ownerKey`, lock serialization helpers, lock constants such as `F_RDLCK`, `F_WRLCK`, and `F_UNLCK`, and stale session cleanup in `doCleanStaleSession`. `ListLocks` integrates with user-facing lock inspection.

## Risks and Edge Cases

Blocking waits are polling-based and not fair. Unlock cleanup checks the current hash key count and may leave session lock references behind if concurrent owners change between read and transaction retry. PID reporting in `Getlk` is only meaningful for the local session; remote sessions return PID zero. Correct stale-session cleanup depends on every lock acquisition adding the lock key to `locked$sid`, which read flock currently does not do when only `HSet` is issued for read locks. Range lock correctness depends on shared helper behavior for merging and splitting lock intervals.

## Test Signals

Tests should cover shared flock compatibility, exclusive flock exclusion, self-owner replacement, blocking cancellation, stale-session lock cleanup, POSIX overlap conflicts, unlock splitting/merging, `Getlk` PID behavior for local and remote owners, and `ListLocks` parsing. Failure tests should inject transaction retries and Redis errors during lock mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/redis_lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/slice.go -->
# sources/distributed-fs/juicefs/pkg/meta/slice.go

## Purpose

`slice.go` defines the in-memory and serialized representation for JuiceFS chunk slice records. It provides helpers to encode/decode slice metadata, overlay slice writes into a logical chunk view, compact chunk state, and decide how many old slice records can be skipped during compaction.

## Important APIs, Types, and Functions

The internal `slice` type stores object slice ID, object size, object offset, logical length, logical position within a chunk, and temporary binary-tree links. `newSlice`, `read`, `cut`, and `visit` build and traverse overlay trees. `sliceBytes` is the fixed serialized size, 24 bytes. `marshalSlice`, `readSlices`, and `readSliceBuf` encode/decode Redis list values or byte buffers. `buildSlice`, `compactChunk`, and `skipSome` are the main logical-layout helpers.

## Control Flow

Each serialized record is laid out as position, slice ID, size, offset, and length. `buildSlice` replays slice records in order; each new slice cuts the current root at its start and end, keeps the covered right side as the new node's right subtree, and makes the new slice the root. An in-order visit then emits logical `Slice` ranges, inserting zero-hole records when positions skip ahead. `compactChunk` removes leading and trailing zero-hole ranges, keeps a one-byte zero if the entire compacted result is a hole, and returns starting position, compacted size, and slice list. `skipSome` avoids compacting large useful first records when doing so would not materially reduce chunk state.

## State and Persistence Behavior

This file persists no state itself, but its 24-byte format is the on-disk/on-Redis contract for chunk list entries used by `redis.go`, backup/load code, compaction, cloning, copy-file-range, and GC. Slice ID zero represents holes or zero-filled ranges rather than object data. Because serialized layout is fixed and shared across engines and dumps, any incompatible change would require migration support.

## Dependencies and Integration Points

It depends only on `pkg/utils` buffers and the public `Slice` type. Redis metadata code uses `marshalSlice` for writes, truncate, fallocate, copy, clone, compaction, and load; `readSlices` is used for reads, listing, copy, clone, dump, cleanup, and reference accounting. Protobuf backup uses `sliceBytes` to pack raw chunk slices.

## Risks and Edge Cases

Corrupt serialized lengths return nil and force callers to handle `EIO` or skip corrupted chunks. The overlay algorithm mutates temporary copies of slice records, so callers must not reuse the tree links for persistent state. Zero-length slices are dropped by `newSlice`. Very large or highly fragmented chunk histories can produce deep recursive `cut`/`visit` traversal and high memory churn. `skipSome` is heuristic and can trade compaction opportunity for avoiding unnecessary rewrite of large first slices.

## Test Signals

Tests should cover marshal/read round trips, invalid buffer length handling, overlapping writes, hole insertion, truncation-style zero records, complete-hole compaction, leading/trailing hole trimming, repeated identical slices, and `skipSome` thresholds around 1 MiB and 5x size comparisons. Integration tests should verify Redis reads, writes, copy-file-range, clone, compaction, dump/load, and GC all interpret the same layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/slice.go -->
