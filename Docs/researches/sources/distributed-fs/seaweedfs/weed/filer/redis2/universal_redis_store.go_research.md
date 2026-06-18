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
