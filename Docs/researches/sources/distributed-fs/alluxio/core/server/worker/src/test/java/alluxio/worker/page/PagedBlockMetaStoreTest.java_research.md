# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockMetaStoreTest.java

Purpose: tests `PagedBlockMetaStore` block/page bookkeeping, reset, listeners, sticky allocation, and allocation side effects.

Important APIs and helpers: setup builds worker page-store dirs from `CacheManagerOptions`. Tests cover adding pages to blocks across dirs, removing last pages and blocks, reset, remove listeners, sticky allocation for existing block file IDs, and ensuring `allocate` alone does not add files or blocks. `RandomAllocator` supplies non-deterministic backing allocation.

Control flow and state: pages are added through `addBlock` and `addPage`, then store metadata and per-dir cached page counters are asserted. Removing all pages for a block deletes block metadata and triggers listeners. Sticky allocation records the directory once a block exists, then repeated allocations for that file ID return the same dir.

Dependencies and integration: depends on `PagedBlockStoreDir`, `PagedBlockMeta`, `PagedBlockStoreMeta`, `PageInfo`, `Allocator`, and worker page-store configuration.

Risks and test signals: strong signal for metadata consistency and listener behavior. It does not validate persisted page bytes, only metadata-level page accounting.
