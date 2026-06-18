# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockStoreDir.java

## Purpose
`PagedBlockStoreDir` adapts a page-cache `PageStoreDir` into a block-aware directory. It tracks mappings from block IDs to committed and temp pages, exposes block-store location, and rewrites temp page IDs on commit.

## Important APIs, Types, and Functions
`fromPageStoreDirs()` wraps raw dirs. `putPage()` and `putTempPage()` update block-to-page maps and delegate to the underlying dir. `scanPages()` downcasts page IDs to `BlockPageId` and rewrites returned `PageInfo` to this dir. `commit()` validates temp/final block IDs, delegates commit, converts temp page IDs to final IDs carrying block size, and moves pages from temp to committed maps. `abort()` removes temp pages and unpins. `deletePage()` updates committed mapping and unpins when last page is gone.

## Control Flow, State, and Persistence
The delegate owns physical page persistence; this class maintains in-memory block/page indexes. Commit transitions pages from temp namespace to final namespace. Abort removes temp metadata and delegates temp-file abort.

## Dependencies and Integration Points
It depends on `PageStoreDir`, `PageStore`, `PageInfo`, `BlockPageId`, `BlockPageEvictor`, `BlockStoreLocation`, and `PagedBlockMetaStore`.

## Risks and Test Signals
Risks include empty `deleteTempPage`, `getUsage()` returning empty, synchronized assumptions around non-thread-safe multimaps, and pin matching in `BlockPageEvictor`. Tests should cover scan recovery, commit rewrite, abort cleanup, delete last page unpin, page counts/bytes, and delegate failure handling.
