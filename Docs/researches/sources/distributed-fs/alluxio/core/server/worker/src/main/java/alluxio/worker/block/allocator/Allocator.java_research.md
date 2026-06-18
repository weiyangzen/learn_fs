## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/Allocator.java

### Purpose
`Allocator` is the public API for choosing a storage directory for new or moved blocks from a metadata view and location constraint.

### Important APIs and Types
- `Allocator.Factory.create(BlockMetadataView)` instantiates the configured allocator class from `WORKER_ALLOCATOR_CLASS`.
- `allocateBlockWithView(long blockSize, BlockStoreLocation location, BlockMetadataView view, boolean skipReview)` returns a `StorageDirView` or null.

### Control Flow
Factory validates the view and uses `CommonUtils.createNewClassInstance` with a `BlockMetadataView` constructor. Implementations evaluate location wildcards, available bytes, medium constraints, and optional `Reviewer` acceptance. `skipReview` is used after deterministic frees or forced locations.

### State and Persistence
The interface itself holds no state and persists nothing. Implementations typically keep the latest metadata view and a reviewer.

### Dependencies and Integration Points
Created by `TieredBlockStore` and `BlockMetadataManager` legacy evictor emulation. The allocator chooses dirs used by `TieredBlockStore.createBlockMetaInternal`, `requestSpace`, and move logic.

### Risks
- Misconfigured allocator class fails at runtime during worker/block metadata initialization.
- Returning null is part of normal no-space flow; callers must decide when to evict or throw.
- Reviewer logic is currently coupled to allocator interface, with a TODO to refactor.

### Test Signals
`AllocatorContractTest`, allocator-specific tests, and `ReviewerFactoryTest` cover factory defaults and allocation contracts.
