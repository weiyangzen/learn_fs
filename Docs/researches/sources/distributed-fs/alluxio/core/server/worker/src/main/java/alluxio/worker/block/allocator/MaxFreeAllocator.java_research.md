## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/MaxFreeAllocator.java

### Purpose
`MaxFreeAllocator` is the default-style allocator that chooses the directory with the most free space within the highest acceptable tier for any-tier allocations, while respecting location and medium constraints.

### Important APIs and Types
- Constructor stores metadata view and reviewer.
- `allocateBlockWithView` updates the current view and delegates to `allocateBlock`.
- `allocateBlock` handles any-tier/any-dir, any-dir-in-tier, and specific-dir cases.
- `getCandidateDirInTier` returns the dir in a tier with maximum available bytes greater than or equal to requested size.

### Control Flow
Any-tier allocation scans tiers in order. For each tier, it chooses the maximum-free candidate dir matching medium and capacity; if accepted by reviewer or review is skipped, it stops. If reviewer rejects that tier’s best dir, it moves to lower tiers rather than trying second-best dirs in the same tier. Any-dir-in-tier chooses the max-free dir in that tier and applies review. Specific-dir returns the dir if it has enough bytes and skips review.

### State and Persistence
State is the current metadata view and reviewer. It persists nothing and does not mutate metadata.

### Dependencies and Integration Points
Created through `Allocator.Factory` by `TieredBlockStore`. Works with `BlockMetadataAllocatorView` and `BlockMetadataEvictorView` snapshots and reviewer implementations.

### Risks
- For any-tier allocations, reviewer rejection of the max-free dir skips other viable dirs in the same tier.
- Not thread-safe due to mutable `mMetadataView`.
- Specific-dir allocations bypass reviewer, so forced moves/expansions can ignore buffer policies.

### Test Signals
Allocator contract tests cover allocation semantics. Reviewer factory tests validate default reviewer/allocator wiring.
