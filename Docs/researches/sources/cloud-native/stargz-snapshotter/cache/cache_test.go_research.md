# sources/cloud-native/stargz-snapshotter/cache/cache_test.go

Purpose: Tests the `BlobCache` contract for directory-backed and memory-backed caches.

Important APIs tested: `NewDirectoryCache`, `NewMemoryCache`, `BlobCache.Add`, `Writer.Commit`, `BlobCache.Get`, and `Reader.ReadAt`.

Control flow: `TestDirectoryCache` runs the shared suite twice: once with enough memory LRU entries and once with a one-entry memory LRU to force disk fallback. `TestMemoryCache` runs the same suite against the in-memory implementation. `testCache` adds blobs by SHA-256 key, commits them, and runs hit or miss checks. `hit` validates whole-blob and partial reads. `miss` expects `Get` to fail for absent keys.

State and persistence: Directory tests create and clean temporary cache directories. `SyncAdd` is true so disk commit completion is deterministic during tests.

Dependencies and integration: Uses only package-level cache APIs plus SHA-256 helpers; this is a black-box style contract test.

Risks covered: Empty payloads, duplicate writes, multiple blobs, partial `ReadAt`, and memory cache eviction are covered. The tests do not cover direct mode, pass-through mode, async commit, close behavior, `FadvDontNeed`, key length assumptions, or concurrent accesses.

Test signals: Good baseline confidence for the cache interface, especially that directory cache still works after memory LRU eviction.
