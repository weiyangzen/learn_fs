## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataView.java

### Purpose
`BlockMetadataView` is the abstract base for read-only-ish metadata projections consumed by allocators and evictors. It builds and refreshes tier view objects from a `BlockMetadataManager` while preserving tier ordering and tier alias lookup.

### Important APIs and Types
- Constructors accept a `BlockMetadataManager` and optional `useReservedSpace` flag.
- `getTierView(String)` validates and returns a `StorageTierView`.
- `getTierViews()` exposes an unmodifiable ordered list.
- `getNextTier(StorageTierView)` and `getTierViewsBelow(String)` support tier traversal.
- `initializeView()` is implemented by concrete views.
- `refreshView()` clears and rebuilds the projection in-place.

### Control Flow
Construction stores the manager and reserved-space flag, then calls subclass `initializeView`. Consumers can refresh the same view object after metadata changes; refresh clears tier lists and alias maps before reinitializing them.

### State and Persistence
State is an in-memory list/map of `StorageTierView` wrappers. It persists nothing and makes no metadata mutations. The reserved-space flag is consumed by concrete dir/tier views that calculate available bytes.

### Dependencies and Integration Points
Subclasses include `BlockMetadataEvictorView` and `BlockMetadataAllocatorView`. Allocators use this API to reason about capacity without directly touching `StorageTier` internals.

### Risks
- The constructor invokes an abstract method, so subclass initialization must not depend on subclass fields that are assigned after `super(...)`.
- It is not synchronized and assumes its backing metadata manager is guarded externally.
- `getTierViewsBelow` returns a `subList` view, so callers should not assume independent snapshot semantics.

### Test Signals
`BlockMetadataViewTest` validates alias lookup, tier lists, below-tier behavior, refresh-compatible comparisons with manager tiers, and exception paths.
