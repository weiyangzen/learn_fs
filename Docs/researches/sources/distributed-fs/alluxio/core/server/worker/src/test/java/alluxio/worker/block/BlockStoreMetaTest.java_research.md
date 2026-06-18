## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockStoreMetaTest.java

**Purpose:** Tests `DefaultBlockStoreMeta` aggregation over worker storage. It validates block listings, directory/tier capacities, used bytes, and full-vs-summary metadata behavior after committing test blocks.

**Important APIs:** Covers `getBlockList`, `getCapacityBytes`, `getCapacityBytesOnDirs`, `getCapacityBytesOnTiers`, `getNumberOfBlocks`, `getUsedBytes`, `getUsedBytesOnDirs`, and `getUsedBytesOnTiers`.

**Control flow:** Setup creates default tiered metadata, repeatedly caches ten committed blocks into the first MEM directory, then constructs both normal and full store meta objects. Tests independently traverse `StorageTier` and `StorageDir` structures to build expected maps.

**State and persistence:** Test helper writes temp files and commits metadata, so store meta derives from real committed block accounting. Full meta includes detailed block and directory-location maps; non-full meta omits heavyweight block lists while preserving capacity/usage totals.

**Dependencies and integration:** Depends on `TieredBlockStoreTestUtils.cache`, Alluxio configuration, `Pair`, and storage meta classes. Its output shape is consumed by worker registration and heartbeat paths.

**Risks:** Incorrect aggregation can misreport worker capacity to masters, skew allocation, or hide blocks during registration. Full and non-full modes must diverge only where intended.

**Test signals:** Strong map-level checks for block IDs, total capacity, per-dir/per-tier capacity, committed block count, and used-byte accounting.
