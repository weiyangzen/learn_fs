## sources/cloud-native/soci-snapshotter/cache/cache_test.go

Purpose: validates common `BlobCache` behavior across directory and memory implementations.

Important APIs/types/functions: `TestDirectoryCache`, `TestMemoryCache`, `testCache`, `hit`, `miss`, `testBlob`, and `digestFor`.

Control flow: tests create caches, add empty/data/multiple/duplicate blobs, commit writers, then verify full-blob and chunk `ReadAt` reads plus expected cache misses.

State and persistence: directory tests use `t.TempDir` with `SyncAdd: true` to make disk writes deterministic; memory tests use in-process buffers.

Dependencies and integration: exercises `NewDirectoryCache`, `NewMemoryCache`, writer commit, reader close, and SHA-256 digest keying.

Risks and test signals: tests do not cover async directory commits, `Direct`, `Close`, failed writes, invalid relative cache paths, concurrent writers/readers, or file descriptor cache behavior.
