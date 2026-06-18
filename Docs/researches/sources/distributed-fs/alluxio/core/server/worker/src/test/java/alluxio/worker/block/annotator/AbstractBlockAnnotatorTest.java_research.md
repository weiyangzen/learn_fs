## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/AbstractBlockAnnotatorTest.java

**Purpose:** Abstract base tests and helpers for block eviction-order annotators/iterators.

**Important APIs:** Provides `init`, `createBlock`, `moveBlock`, `removeBlock`, `accessBlock`, `getDir`, `validateIterator`, plus common tests `testRemovedBlock` and `testMovedBlock`.

**Control flow:** `init` creates default metadata and obtains the first block iterator event listener. Helpers seed committed blocks, manually update metadata for moves/removals, and notify the listener about commit/move/remove/access events. Common tests verify iterator output before and after remove or move events.

**State and persistence:** Uses temporary tier directories and metadata. Tracks block ID to `StorageDir` in a map to drive event notifications.

**Dependencies and integration:** Used by LRU and LRFU annotator tests. Depends on `BlockIterator`, `BlockStoreEventListener`, `StorageTierAssoc`, and `TieredBlockStoreTestUtils`.

**Risks:** Helpers manually simulate events; if production event order differs, tests may not catch every integration issue. Still, they protect iterator state updates for remove and move.

**Test signals:** Common regression coverage that annotators drop removed blocks and keep moved blocks visible in natural order.
