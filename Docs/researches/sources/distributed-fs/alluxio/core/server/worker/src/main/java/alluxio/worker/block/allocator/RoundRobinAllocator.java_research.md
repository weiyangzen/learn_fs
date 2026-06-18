# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/RoundRobinAllocator.java

Purpose: Implements the `Allocator` policy that chooses storage directories in round-robin order while preferring higher tiers first. It handles unrestricted writes, any-dir-in-tier writes, and exact-directory writes.

Important APIs: constructor seeds one iterator per tier from `BlockMetadataView`; `allocateBlockWithView` refreshes the active metadata view; private `allocateBlock` dispatches by `BlockStoreLocation`; `getNextAvailDirInTier` scans one tier for medium, space, and reviewer acceptance.

Control flow: any-tier allocations iterate tiers in metadata order, and each tier resumes from the last stored directory iterator. Exact-directory allocations skip `Reviewer` so caller-directed placement is not probabilistically rejected.

State and persistence: In-memory only. The allocator stores `mMetadataView`, a configured `Reviewer`, and per-tier iterator positions; no disk state is written. It is annotated `@NotThreadSafe`.

Dependencies and integration: Consumes `BlockMetadataView`, `StorageTierView`, `StorageDirView`, `BlockStoreLocation`, and `Reviewer.Factory`. It is used by the block store and deprecated evictors to locate space for new temp blocks or moved blocks.

Risks and test signals: Iterator state is initialized from the constructor view but the metadata view can later be replaced, so tests should cover tier/directory changes across `allocateBlockWithView`. Validate any-tier priority, per-tier round-robin fairness, medium filtering, exact-dir reviewer bypass, and reviewer rejection fallback.
