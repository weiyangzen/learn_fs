# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/DefaultBlockIterator.java

Purpose: Event-driven `BlockIterator` backed by one `SortedBlockSet` per storage directory. It ranks blocks with the configured `BlockAnnotator` and supports eviction, promotion, and tier alignment queries.

Important APIs: Constructor initializes per-dir sets from `BlockMetadataManager`; `getIterator`, `getIntersectionList`, `getSwaps`, and `aligned` implement ranked traversal and comparisons; `getListeners` returns an internal `AbstractBlockStoreEventListener`.

Control flow: Initialization creates a set for each directory and inserts existing block IDs. Access and commit events call `blockUpdated`; remove events call `blockRemoved`; client and worker moves transfer the previous sort field to the new location. Iterator creation gathers directory locations under the requested location, refreshes dirty offline locations, creates ordered iterators, and merge-sorts them.

State and persistence: Maintains concurrent maps of directory locations to sorted sets and dirty offline locations. State is memory-only and reconstructed from metadata on startup.

Dependencies and integration: Depends on `BlockMetadataManager`, `StorageTier`, `StorageDir`, `SortedBlockSet`, `BlockAnnotator`, and Guava iterators. It is consumed by tier management tasks through `BlockMetadataManager.getBlockIterator()`.

Risks and test signals: Moving a block preserves the old sort field, so access recency may not change on moves. Offline refresh is synchronized but per-dir sets are concurrently updated. Tests should cover listener registration, storage loss, moved block ordering, LRFU lazy refresh, merged iteration across multiple dirs, filtered swaps, and alignment boundary comparisons.
