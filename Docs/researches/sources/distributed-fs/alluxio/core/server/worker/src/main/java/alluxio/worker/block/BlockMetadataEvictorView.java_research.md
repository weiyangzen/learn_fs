## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataEvictorView.java

### Purpose
`BlockMetadataEvictorView` is a narrowed, non-thread-safe view over `BlockMetadataManager` for eviction and allocation decisions. It materializes tier and directory views while filtering block metadata access through evictability rules so eviction logic does not need to understand pinned inodes, locked blocks, or blocks already marked for movement in the current view.

### Important APIs and Types
- `BlockMetadataEvictorView(BlockMetadataManager, Set<Long> pinnedInodes, Set<Long> lockedBlocks)` snapshots pinned file ids and locked block ids.
- `initializeView()` wraps each `StorageTier` as a `StorageTierEvictorView`.
- `getDirs(BlockStoreLocation)` returns all directory views whose locations belong to the requested tier/dir/medium wildcard.
- `clearBlockMarks()` clears per-directory move-in/move-out markings.
- `isBlockPinned`, `isBlockLocked`, `isBlockMarked`, and `isBlockEvictable` compose the filtering rules.
- `getBlockMeta(long)` returns metadata only when the block is currently evictable.

### Control Flow
Construction delegates to `BlockMetadataView`, which immediately calls `initializeView`; after that the constructor fills pinned and locked sets. This ordering is acceptable because `initializeView` only builds wrapper objects and does not use the filter sets. Evictors call `getDirs` to scope candidates, use `isBlockEvictable` to guard deletion, and use `getBlockMeta` to avoid accidentally exposing protected blocks.

### State and Persistence
The class holds in-memory snapshots of pinned inodes and locked blocks and in-memory tier/dir views. It persists nothing directly. Physical block deletion and metadata mutation happen later through `TieredBlockStore` and `BlockMetadataManager`.

### Dependencies and Integration Points
It depends on `BlockId.getFileId` to map block ids to file ids, metadata wrappers in `alluxio.worker.block.meta`, and the underlying `BlockMetadataManager` for live capacity and block metadata. `TieredBlockStore.getUpdatedView` creates this view during free-space eviction, and allocators may receive it at construction time.

### Risks
- The class is explicitly not thread-safe; callers must build and use it under higher-level metadata/eviction synchronization.
- It snapshots pinned and locked state. Long-lived instances can become stale, which is why `TieredBlockStore` rebuilds it before freeing space.
- The TODO notes unallocatable space is not yet filtered, so allocator/evictor consumers still rely on later allocation checks.

### Test Signals
`BlockMetadataViewTest` exercises tier lookup, tier-below behavior, available bytes, `getBlockMeta`, and pinned/locked filtering. Eviction behavior is indirectly tested by `TieredBlockStore` and allocator tests.
