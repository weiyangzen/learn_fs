## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/GreedyAllocator.java

### Purpose
`GreedyAllocator` is a simple non-thread-safe allocator that returns the first directory in tier/dir iteration order that can fit the requested block and passes review.

### Important APIs and Types
- Constructor takes an initial `BlockMetadataView` and creates a `Reviewer`.
- `allocateBlockWithView` swaps in the provided view and delegates to private `allocateBlock`.
- `allocateBlock` handles any-tier/any-dir, any-dir-in-tier, and specific-dir locations.

### Control Flow
For any-tier requests, it iterates tiers in view order and dirs in dir order, respecting medium constraints and available bytes, and returns the first accepted dir. For any-dir-in-tier, it scans only that tier. For specific-dir requests, it skips reviewer checks and returns the dir if capacity is sufficient.

### State and Persistence
State is the current metadata view and reviewer. It persists nothing and makes no metadata changes; callers later create temp metadata in the selected dir.

### Dependencies and Integration Points
Can be configured by `WORKER_ALLOCATOR_CLASS` and used by `TieredBlockStore`. Reviewer acceptance integrates with allocation policy extensions such as probabilistic buffer review.

### Risks
- First-fit behavior can concentrate allocations in early dirs/tiers and cause imbalance.
- Not thread-safe; `mMetadataView` is mutated per call.
- Specific-dir allocations bypass reviewer by design.

### Test Signals
Allocator contract/base tests exercise expected allocation behavior. Reviewer tests cover factory interaction.
