# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreDirTest.java

Purpose: tests `PagedBlockStoreDir` wrapping of a `PageStoreDir` for block-aware counters, eviction, temp pages, commit, and abort.

Important APIs and helpers: setup creates a local page-store dir with FIFO eviction. Tests cover root path, dir index, `BlockStoreLocation`, number of blocks, cached bytes, page put idempotence, page delete idempotence, evictor updates, temp-page add/commit, and temp-page abort.

Control flow and state: committed page operations update per-block page counts and byte counts. Temp page operations record temp file IDs without counting committed blocks until `commit(fileId)`, while `abort(fileId)` clears temp state and page-store temporary data.

Dependencies and integration: depends on `LocalPageStoreDir`, `PageStoreOptions`, `PageInfo`, `BlockPageId`, `BlockPageEvictor`, and `PagedBlockStoreMeta` default tier/medium constants.

Risks and test signals: strong signal for dir-local accounting and temp-to-committed transitions. It does not cover multi-dir allocation or disk-full errors.
