# sources/cloud-native/buildkit/cache/contenthash/checksum.go

Purpose: computes and caches stable content digests for files, directories, symlinks, and filtered path sets inside BuildKit cache refs. It underpins cache keys for filesystem inputs and copy/filter operations.

Important APIs/types/functions: public `Checksum`, `GetCacheContext`, `SetCacheContext`, `ClearCacheContext`, `CacheContext`, `ChecksumOpts`, and `Hashed`. Internal core includes `cacheManager`, `cacheContext`, `HandleChange`, `Checksum`, `includedPaths`, `shouldIncludePath`, `wildcardPrefix`, `lazyChecksum`, `scanChecksum`, `checksum`, `needsScan`, `scanPath`, `getFollowLinksCallback`, `prepareDigest`, and path/key conversion helpers.

Control flow: `Checksum` obtains a per-ref cache context from a small LRU keyed by origin metadata, enables Windows backup privileges when needed, then delegates. Simple lookups use `lazyChecksum`, which first tries a read-only radix-tree hit and only scans the mounted snapshot on misses. Filtered or wildcard checks call `includedPaths`, which ensures root scan state, resolves symlink prefixes, iterates radix keys, applies include/exclude matchers, computes missing per-record digests, and hashes selected path/digest pairs. `HandleChange` updates the radix tree from fsutil change streams and marks parent directories dirty.

State and persistence behavior: cache state is an immutable radix tree serialized as vtproto `CacheRecords` under metadata key `buildkit.contenthash.v0`. Directories have separate header (`/dir/`) and recursive content (`/dir`) records. Dirty transactions are committed to the tree and saved either synchronously through `SetCacheContext` or asynchronously after checksum updates. Hardlink updates use `linkMap`; parent directory digests are invalidated through `dirtyMap`.

Dependencies and integration points: integrates BuildKit cache refs/mountables, snapshot local mounting, session groups, fsutil change notifications, patternmatcher include/exclude semantics, cachedigest hashing, hashicorp immutable radix/LRU, and OCI digests. `filehash.go`, `path.go`, and OS shims provide digest and traversal primitives.

Risks: symlink handling is security-sensitive and cache-correctness-sensitive; both `rootPath` and `getFollowLinksCallback` must preserve root confinement and `FollowLinks` semantics. Async saves can lag tests or shutdown. Incorrect dirty propagation causes stale directory digests. Include/exclude wildcard behavior must match fsutil copy behavior. `cacheManager.Checksum` currently returns `nil` digest/error on `GetCacheContext` error, which is a suspicious failure mode.

Test signals: `checksum_test.go` covers symlink scan regressions, non-lexical symlinks, hardlinks, wildcard and include/exclude behavior, broken symlinks, persistence, directory updates, unordered files, and helper cache-manager setup. `path_test.go` validates secure symlink resolution. Benchmarks cover vtproto marshal/unmarshal of persisted records.
