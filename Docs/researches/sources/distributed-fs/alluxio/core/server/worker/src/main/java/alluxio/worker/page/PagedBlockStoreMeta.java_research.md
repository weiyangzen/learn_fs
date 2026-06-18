# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockStoreMeta.java

## Purpose
`PagedBlockStoreMeta` presents paged-store capacity, usage, directory, and block-location information through the `BlockStoreMeta` interface.

## Important APIs, Types, and Functions
It defines `DEFAULT_TIER`, `DEFAULT_MEDIUM`, and `DEFAULT_STORAGE_TIER_ASSOC`, reflecting that the paged store currently models one top tier/medium. Constructors build either brief metadata with only counts or full metadata with block locations. Interface methods return capacity/used bytes by tier and dir, directory paths, lost storage, block counts, block lists, and tier association.

## Control Flow, State, and Persistence
The object is an immutable snapshot assembled from `PagedBlockMetaStore`. It persists nothing. Optional block lists are only populated by the full constructor.

## Dependencies and Integration Points
It depends on Alluxio storage tier associations, `BlockStoreLocation`, `BlockStoreMeta`, `Pair`, and Guava immutable collections. It is returned by `PagedBlockStore.getBlockStoreMeta*`.

## Risks and Test Signals
Risks include single-tier assumptions, `getBlockList()`/`getBlockListByStorageLocation()` returning null in brief mode, and default medium/tier mismatch with deployments. Tests should cover brief vs full metadata, per-dir maps, empty/lost storage behavior, and master registration compatibility.
