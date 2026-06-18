## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMetadataManagerTest.java

**Purpose:** Unit tests `BlockMetadataManager`, the in-memory model for worker tier, directory, committed block, and temporary block metadata. The suite uses a two-tier MEM/HDD configuration with explicit capacities and media types.

**Important APIs:** Exercises `createBlockMetadataManager`, `getTier`, `getDir`, `getTiers`, `getTiersBelow`, `getAvailableBytes`, `addTempBlockMeta`, `abortTempBlockMeta`, `commitTempBlockMeta`, `removeBlockMeta`, `moveBlockMeta`, `resizeTempBlockMeta`, and `getBlockStoreMeta`.

**Control flow:** `before` builds temporary tier directories via `TieredBlockStoreTestUtils.setupConfWithMultiTier`, disables tier management, then constructs metadata. Tests add temp metas, commit them into `BlockMeta`, move committed blocks through destination temp metas, and assert optional lookups or expected exceptions.

**State and persistence:** State is the metadata graph plus temp/committed block accounting inside `StorageDir`. It does not validate physical file movement directly, except through metadata-derived paths and block store aggregate counters.

**Dependencies and integration:** Depends on global Alluxio configuration, storage meta classes, `BlockStoreLocation`, Guava `ImmutableMap`, JUnit rules, and runtime exception messages. It is a foundation signal for allocators, evictors, and tiered block store behavior.

**Risks:** Global configuration mutation can leak if tests are reordered without rules. The move tests rely on destination temp metadata being removed, so regressions in move cleanup or capacity accounting would cascade into eviction and block store tests.

**Test signals:** Strong coverage of lookup, capacity aggregation, temp-to-committed lifecycle, same-dir/different-dir moves, out-of-space exception messages, resize, and tier-level store meta maps.
