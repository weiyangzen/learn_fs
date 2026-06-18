# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/BlockPageEvictor.java

## Purpose
`BlockPageEvictor` wraps a page-cache `CacheEvictor` and filters out pages belonging to pinned blocks. It protects blocks that are being written, committed, read, or otherwise temporarily ineligible for eviction.

## Important APIs, Types, and Functions
`evict()` delegates to `evictMatching(mIsNotPinned)`. `evictMatching()` combines caller criteria with the not-pinned predicate. `addPinnedBlock()` and `removePinnedBlock()` update the pinned set. Normal cache access notifications pass through to the delegate.

## Control Flow, State, and Persistence
State is an in-memory `Set<String>` of pinned block identifiers. Reset clears both delegate state and pinned state. There is no durable persistence.

## Dependencies and Integration Points
It integrates `CacheEvictor`, `PageId`, and paged block store directories. `PagedBlockStoreDir` uses it for temp block pinning and commit/read protection.

## Risks and Test Signals
A notable risk is that the pinned set stores `String.valueOf(blockId)`, while block page file IDs are encoded strings like `paged_block_...`; callers must pin using values that match `pageId.getFileId()` or filtering will not work. Tests should verify pinning against actual `BlockPageId` file IDs, eviction matching, and reset behavior.
