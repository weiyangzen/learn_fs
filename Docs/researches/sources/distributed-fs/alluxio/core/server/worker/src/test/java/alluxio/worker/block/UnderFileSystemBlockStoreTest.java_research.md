## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UnderFileSystemBlockStoreTest.java

**Purpose:** Tests `UnderFileSystemBlockStore`, the access-control and reader factory layer for UFS-resident blocks.

**Important APIs:** Exercises `acquireAccess`, duplicate access handling, `releaseAccess`, `createBlockReader`, no-cache option handling, session cleanup, and reader close behavior.

**Control flow:** Setup creates a temporary file, mocked local block store, a `NoopUfsManager` mount, and `OpenUfsBlockOptions` with max UFS read concurrency. Tests acquire up to the configured concurrency, reject duplicate/session-over-limit cases, release and reacquire, create readers over a real file, verify no-cache metadata, clean session access records, and close readers.

**State and persistence:** Runtime state is access tracking by session/block and reader lifecycle. The UFS file is real; local block store is mocked.

**Dependencies and integration:** Integrates UFS manager mounts, open options, local block store, `BlockReader`, temporary files, and exception types such as duplicate block/not found paths.

**Risks:** Access leaks can permanently exhaust UFS concurrency for a block. Cleanup must release all session-held access. Reader creation must honor no-cache and block metadata options.

**Test signals:** Covers concurrency caps, duplicate acquisition, release, reader creation/data, no-cache behavior, cleanup by session, and reader close.
