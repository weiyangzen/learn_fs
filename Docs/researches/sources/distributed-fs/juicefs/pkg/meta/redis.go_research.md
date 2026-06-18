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
