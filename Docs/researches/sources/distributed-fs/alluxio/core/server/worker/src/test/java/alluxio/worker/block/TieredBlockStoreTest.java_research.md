## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/TieredBlockStoreTest.java

**Purpose:** Extensive tests for `TieredBlockStore`, covering local block storage lifecycle, locking, move/free-space behavior, allocation edge cases, reserved space, pinned blocks, and failed storage removal.

**Important APIs:** Exercises `pinBlock`, `commitBlock`, `abortBlock`, `moveBlock`, `removeBlock`, `freeSpace`, `requestSpace`, `createBlock`, `createBlockWriter`, `hasBlockMeta`, `hasTempBlockMeta`, `getBlockStoreMeta`, `getBlockStoreMetaFull`, and `removeInaccessibleStorage`.

**Control flow:** Setup reloads configuration, creates a default two-tier MEM/SSD layout, metadata manager, lock manager, block store, iterator, and test dirs. Tests use helpers to create temp or committed block files, then perform operations and assert metadata plus physical temp/commit path presence.

**State and persistence:** Uses real temp files in tier directories, committed/temp metadata, lock manager state, pinned block state, and directory capacity accounting. Failed-storage test deletes a directory and checks store meta shrinkage.

**Dependencies and integration:** Depends on allocator/evictor configuration, block iterator notifications, `EvictionPlan`, `Evictor`, retry/concurrency utilities, `FileUtils`, and Alluxio exception messages.

**Risks:** This is a high-blast-radius component. Regressions can corrupt block files, violate lock safety, overuse reserved bytes, move blocks into full destinations, evict pinned/locked data, or misreport failed storage.

**Test signals:** Broad coverage of success paths, same-location no-op, tier move full errors, concurrent free-space calls, pinned/locked eviction failures, request-space failures, medium-aware allocation, relaxed versus forced placement, reserved-space moves, duplicate blocks, wrong-session errors, and inaccessible directory cleanup.
