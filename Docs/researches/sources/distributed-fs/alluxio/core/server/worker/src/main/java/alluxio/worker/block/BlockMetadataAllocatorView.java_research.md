# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataAllocatorView.java

Purpose: `BlockMetadataAllocatorView` exposes a narrowed metadata view for block allocation decisions.

Important APIs are constructor and `initializeView`. Control flow delegates common view setup to `BlockMetadataView` through the constructor, then `initializeView` iterates all storage tiers from the metadata manager, creates `StorageTierAllocatorView` for each tier with the configured reserved-space behavior, appends it to `mTierViews`, and indexes it by tier alias.

State and persistence are in-memory view objects over `BlockMetadataManager`; no durable state. Dependencies include block metadata manager/view base classes, storage tier metadata, and allocator-specific tier view classes. Integration points are block allocators that need read-only tier/dir capacity information while placing blocks. Risks are low but view freshness depends on when callers initialize/rebuild it, and reserved-space inclusion changes allocator-visible capacity. No direct tests in this subset.
