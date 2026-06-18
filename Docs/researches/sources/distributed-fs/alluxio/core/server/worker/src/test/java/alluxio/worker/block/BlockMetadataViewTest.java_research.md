## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMetadataViewTest.java

**Purpose:** Tests `BlockMetadataEvictorView`, the read/filter view used by eviction and allocation logic. It verifies that view objects mirror `BlockMetadataManager` while hiding pinned or locked blocks from eviction.

**Important APIs:** Covers `getTierView`, `getTierViews`, `getTierViewsBelow`, `getAvailableBytes`, `getBlockMeta`, `isBlockEvictable`, `isBlockPinned`, `isBlockLocked`, and view equivalence with `StorageTierEvictorView`.

**Control flow:** Setup creates a default metadata manager and spies the evictor view. Tests compare view results to backing manager data, add a committed block directly to a `StorageDir`, then alter `isBlockPinned` and `isBlockLocked` spy responses to confirm filtering behavior.

**State and persistence:** The view holds pinned inode and locked block sets; it does not persist state. Test state lives in temporary tier directories and committed block metadata.

**Dependencies and integration:** Uses `BlockId.getFileId` to map block IDs to pin inodes, Mockito for selective method stubbing, and metadata view classes consumed by allocators and evictors.

**Risks:** A regression that exposes pinned or locked blocks would allow eviction of protected data. The equivalence helpers also protect directory-level available, capacity, committed, evictable block, and evictable byte calculations.

**Test signals:** Good coverage for missing tiers/blocks, tier view construction, pinned/locked filtering, and stable view equivalence after metadata changes.
