# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultStorageDir.java

Purpose: Concrete storage-directory metadata container tracking committed blocks, temp blocks, per-session temp ownership, capacity, reserved bytes, available bytes, and committed bytes.

Important APIs: `newStorageDir`, `initializeMeta`, block/temp add/remove/get APIs, `resizeTempBlockMeta`, `cleanupSessionTempBlocks`, `getSessionTempBlocks`, `toBlockStoreLocation`, and byte getters.

Control flow: Startup creates the directory, scans direct children, preserves numeric committed block files as `DefaultBlockMeta`, deletes invalid files, and deletes non-temp subdirectories. Adding committed or temp blocks reserves space; removing reclaims space; temp resize only grows. Session cleanup removes listed temp blocks and reclaims their space.

State and persistence: In-memory maps mirror disk files. Committed blocks are numeric files under the storage dir; temp blocks live under the configured tmp folder. Atomic byte counters track capacity accounting, including reserved space.

Dependencies and integration: Used by `DefaultStorageTier`, metadata manager, allocator and evictor views. Depends on Alluxio config, exceptions, file utilities, and Guava sets.

Risks and test signals: Class is not thread-safe even though byte counters are atomic; callers must synchronize at higher layers. Startup deletes unexpected paths. Tests should cover disk scan cleanup, capacity with reserved bytes, duplicate block rejection, temp session maps, resize growth, session cleanup partial lists, and committed/temp byte accounting.
