# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreMetaTest.java

Purpose: tests `PagedBlockStoreMeta` aggregate reporting produced from `PagedBlockMetaStore`.

Important APIs and helpers: setup configures two memory page-store directories with capacities and paths. `generatePages` creates block metadata and page metadata in a selected dir. Tests cover full block lists, no-detailed block list mode, capacity totals by tier/dir, directory paths, lost storage, used bytes, and storage tier association.

Control flow and state: pages are generated across dirs, then `getStoreMetaFull()` or `getStoreMeta()` is inspected. Detailed mode returns block lists by tier and by `BlockStoreLocation`; summary mode omits those maps but keeps counts/capacity/usage.

Dependencies and integration: depends on `CacheManagerOptions`, `PageStoreDir`, `PageInfo`, `BlockPageId`, `PagedBlockMeta`, `BlockStoreLocation`, and default paged-store tier constants.

Risks and test signals: good signal for worker storage metrics exposed to masters/clients. It assumes specific configured page-store paths and default tier/medium names.
