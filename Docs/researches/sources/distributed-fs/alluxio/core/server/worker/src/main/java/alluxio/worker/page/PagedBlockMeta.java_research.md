# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockMeta.java

## Purpose
`PagedBlockMeta` implements block metadata for blocks stored as pages rather than a single local file.

## Important APIs, Types, and Functions
It stores block ID, block size, and `PagedBlockStoreDir`. `getBlockLocation()` returns the directory's `BlockStoreLocation`; `getPath()` returns the directory root path; `getParentDir()` is unsupported because paged dirs do not implement the old `StorageDir` contract.

## Control Flow, State, and Persistence
The object is immutable. Persistent bytes live in page-store files under the associated directory, and the metadata is tracked in `PagedBlockMetaStore`.

## Dependencies and Integration Points
It implements `BlockMeta` and is used by paged readers, writers, store metadata, and UFS fallback readers.

## Risks and Test Signals
Risks include callers expecting a single block file path or `StorageDir`; both are incompatible with paged storage. Tests should cover path/location reporting and avoid using `getParentDir()` on paged metadata.
