## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/MaxFreeAllocatorTest.java

**Purpose:** Tests `MaxFreeAllocator`, the default allocator that chooses the directory with the most available space within the requested location constraints.

**Important APIs:** Exercises `MaxFreeAllocator.allocateBlockWithView` through direct scenarios and base helper assertions.

**Control flow:** Setup sets allocator class to `MaxFreeAllocator`; teardown reloads configuration. Tests allocate under multiple capacity-consumption patterns and verify the chosen directory follows max-free ordering. Base tests cover any-dir-in-tier, medium-aware any-tier, and specific directory behavior.

**State and persistence:** Uses temporary tier directories and metadata view state. Capacity is manipulated by adding committed metadata in helper methods.

**Dependencies and integration:** Extends `AllocatorTestBase` and is tied to the configured default allocator expected by `AllocatorFactoryTest`.

**Risks:** Available-byte calculations must include pinned/locked filtering from the view where applicable. Directory removal or capacity accounting errors can cause suboptimal or invalid choices.

**Test signals:** Covers max-free selection, capacity boundaries, and common allocator contract paths for the default strategy.
