# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/LazyUfsBlockLocationCacheTest.java

## Purpose
`LazyUfsBlockLocationCacheTest` validates lazy loading and invalidation of UFS block locations through the mount table.

## Important APIs, Types, and Functions
The test constructs `MasterUfsManager`, `MountTable`, `MountInfo`, and `LazyUfsBlockLocationCache`, then calls `get(blockId)`, `get(blockId, fileUri, offset)`, and `invalidate(blockId)`.

## Control Flow, State, and Persistence
A temporary local UFS is mounted at `/mnt`; the test creates a UFS file, fetches its native locations from the local `UnderFileSystem`, confirms a cold cache miss, lazily resolves locations through the Alluxio path, confirms the warm cache hit, and finally invalidates the entry.

## Dependencies and Integration Points
This links block-location caching to `UnderFileSystem.Factory`, mount-specific UFS configuration, mount resolution, and local UFS file-location APIs.

## Risks
The test assumes the local UFS returns stable file locations. It validates only one block id and one offset, so multi-block, remote UFS, and mount-resolution failure behavior are outside this file.

## Test Signals
The key signal is that cache misses do not precompute, lazy lookup matches UFS locations, cached lookup returns the same list, and invalidation clears the block id.
