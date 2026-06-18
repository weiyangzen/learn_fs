# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultStorageDirTest.java

Purpose: broad unit coverage for `DefaultStorageDir` initialization, committed/temp block accounting, capacity checks, cleanup, and location conversion.

Important APIs and helpers: setup builds a `DefaultStorageTier`, directory, block meta, and temp block meta. Helpers create block files, assert empty metadata, and verify cleaned storage directories. Tests cover initialization from existing files, inappropriate file/dir deletion, oversized block rejection, byte counters, getters, block/temp metadata add/remove/get, temp resizing, session cleanup, and `toBlockStoreLocation()`.

Control flow and state: initialization scans real directory contents and reconstructs committed block metadata when file sizes fit capacity. Runtime tests mutate in-memory maps for committed blocks and temp blocks, assert available/committed byte transitions, enforce duplicate and no-space exceptions, and remove only temp blocks belonging to a cleanup session.

Dependencies and integration: depends on `DefaultStorageTier`, `DefaultBlockMeta`, `DefaultTempBlockMeta`, `BlockStoreLocation`, `ExceptionMessage`, Guava `Sets`, `BufferUtils`, and filesystem temp directories.

Risks and test signals: strong signal for storage directory invariants and failure messages, but tests rely on exact global constants and exception text. Concurrency is not covered; behavior is single-threaded metadata mutation plus filesystem initialization.
