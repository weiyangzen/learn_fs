## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorTestBase.java

**Purpose:** Shared fixture and assertion library for allocator strategy tests.

**Important APIs:** Defines default MEM/SSD/HDD tier topology and helpers `before`, `resetManagerView`, `assertTempBlockMeta` overloads, `getMetadataEvictorView`, `assertAllocationAnyDirInTier`, `assertAllocationAnyDirInAnyTierWithMedium`, and `assertAllocationInSpecificDir`.

**Control flow:** Setup disables reviewer rejection through `MockReviewer`, creates a default multi-tier configuration, builds `BlockMetadataManager`, and initializes common `BlockStoreLocation` targets. Assertions request allocations, check presence/absence, validate size and target location, and may add committed blocks to consume capacity.

**State and persistence:** Uses temporary directories and in-memory metadata. Some assertions add `DefaultBlockMeta` to dirs to simulate consumed space.

**Dependencies and integration:** Supports `GreedyAllocatorTest`, `MaxFreeAllocatorTest`, `RoundRobinAllocatorTest`, and contract tests. Depends on tier setup utilities, metadata view, reviewer configuration, storage dir/view APIs, and Alluxio constants.

**Risks:** Shared expected capacities and locations encode allocator assumptions; if tier topology changes, many strategy tests need coordinated updates. It mutates global configuration.

**Test signals:** Provides reusable checks for allocation success/failure, concrete directory choice, medium-aware allocation, and view reset behavior.
