# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/BlockPageId.java

## Purpose
`BlockPageId` specializes cache `PageId` for pages that belong to Alluxio blocks. It encodes block ID and block size into the page file ID so page stores without page metadata can recover block metadata.

## Important APIs, Types, and Functions
`fileIdOf()` formats `paged_block_%016x_size_%016x`; `tempFileIdOf()` uses size `-1` as a temp placeholder. `parseBlockId()` and `parseBlockSize()` recover metadata from file IDs. `newTempPage()` creates temp pages. `downcast()` converts a generic `PageId` into a `BlockPageId`. Equality ignores block size for two `BlockPageId`s and compares block ID plus page index.

## Control Flow, State, and Persistence
The encoded file ID is persisted as the page-store file identity. On commit, temp file IDs are rewritten to final file IDs carrying real block size. The object caches parsed `blockId` and `blockSize` in final fields.

## Dependencies and Integration Points
It depends on `PageId`, regex parsing, and `Preconditions`. It is central to `PagedBlockWriter`, `PagedBlockReader`, `PagedBlockStoreDir`, and `PagedBlockMetaStore`.

## Risks and Test Signals
Risks include equality/hash-code compatibility with ignored block size, parsing unsigned negative block IDs, rejecting negative parsed block sizes, and string interning. Tests should cover temp IDs, final IDs, negative/large block IDs, invalid file IDs, downcast from plain `PageId`, and equality/hash behavior.
