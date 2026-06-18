## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/GreedyAllocatorTest.java

**Purpose:** Tests the placement policy of `GreedyAllocator`, which chooses the first viable directory according to tier/directory scan order.

**Important APIs:** Exercises `GreedyAllocator.allocateBlockWithView` through base assertions and direct allocation scenarios.

**Control flow:** Setup selects `GreedyAllocator` in configuration and creates the allocator from a metadata view; teardown reloads configuration. The main test fills dirs in controlled order and asserts which location is chosen or rejected. Additional tests reuse base assertions for any-dir-in-tier, any-dir-in-any-tier-with-medium, and specific-dir requests.

**State and persistence:** Uses in-memory metadata and committed block additions to consume capacity. No durable data beyond temporary test dirs.

**Dependencies and integration:** Extends `AllocatorTestBase`, uses block store locations, storage dirs/views, and Alluxio configuration.

**Risks:** Greedy policy is sensitive to directory order. Changes in `BlockMetadataEvictorView` ordering can alter placement even if capacity logic remains correct.

**Test signals:** Validates first-fit behavior, capacity rejection, tier/medium-specific constraints, and exact directory targeting for Greedy allocation.
