# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockMetaStore.java

## Purpose
`PagedBlockMetaStore` manages page metadata and block metadata for the paged block store. It wraps `DefaultPageMetaStore`, indexes committed and temporary blocks, keeps pages of the same block in one directory, commits temp pages to final page IDs, and emits block-store events.

## Important APIs, Types, and Functions
`BlockPageAllocator` reuses the directory of an existing block before delegating allocation. `hasBlock`, `hasTempBlock`, and `hasFullBlock` query indexed state. `addPage()` downcasts/rebuilds `BlockPageId` and creates `PagedBlockMeta` as needed. `addTempPage()` requires an existing temp block and increases temp size. `addTempBlock()` registers and pins temp blocks. `commit()` converts temp metadata to committed metadata and calls `commitFile()` with temp and final file IDs. `removePage()` deletes metadata and emits `onRemoveBlock` when the last page disappears. `getStoreMeta()` and `getStoreMetaFull()` build brief/full block-store metadata.

## Control Flow, State, and Persistence
The delegate page meta store owns page state, while two `IndexedSet`s track committed and temp block metadata by block ID and dir. Commit removes temp metadata, adds committed metadata, and rewrites page file IDs. Removing the final page removes block metadata and notifies listeners. Some interface methods are currently stubbed with `null` or empty usage.

## Dependencies and Integration Points
It integrates `DefaultPageMetaStore`, `Allocator`, `HashAllocator`, `PagedBlockStoreDir`, `BlockPageId`, `BlockStoreEventListener`, `BlockStoreLocation`, and page-cache locks.

## Risks and Test Signals
Risks include stubbed `PageMetaStore` methods (`getStoreDirOfFile`, `getUsage`, `removePage(PageId, boolean)`, `getAllPagesByFileId`), locking discipline relying on callers, duplicate commit handling, and listener callbacks while under metadata lock. Tests should cover restart page scan/addPage, temp block lifecycle, commit ID rewrite, full-block detection, last-page removal events, allocator directory affinity, and unsupported method callers.
