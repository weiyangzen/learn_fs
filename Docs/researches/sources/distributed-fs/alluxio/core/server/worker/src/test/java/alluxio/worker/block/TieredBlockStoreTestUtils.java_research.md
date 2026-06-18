## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/TieredBlockStoreTestUtils.java

**Purpose:** Shared utility class for constructing tiered-store configurations and seeding local block data in worker block tests.

**Important APIs:** Provides default tier constants, `setupConfWithMultiTier`, `setupConfWithSingleTier`, `setupDefaultConf`, `defaultMetadataManager`, `defaultMetadataManagerView`, `cache` overloads, `cache2`, `createTempBlock`, `getDefaultTotalCapacityBytes`, and `getDefaultDirNum`.

**Control flow:** Configuration helpers validate array dimensions, create directory hierarchies under a base temp dir, and set tier alias/path/quota/medium properties. Cache helpers create temp metadata, write increasing bytes through `LocalFileBlockWriter`, move temp files to committed paths, commit metadata, and optionally notify event listeners or block iterators.

**State and persistence:** Mutates global Alluxio configuration and creates real local directories/files. It also mutates `BlockMetadataManager` and `LocalBlockStore` state.

**Dependencies and integration:** Used by metadata, view, block-store, allocator, annotator, and sync tests. Depends on `PathUtils`, `FileUtils`, `BufferUtils`, `DefaultTempBlockMeta`, `LocalFileBlockWriter`, and `BlockIterator` listener contracts.

**Risks:** Because it bypasses some production store methods in `cache2`, tests using it must manually trigger listeners when iterator state matters. Global configuration mutation makes cleanup/rule discipline important.

**Test signals:** Not a test itself, but it provides deterministic tier layouts and block data for most block worker unit tests in this subset.
