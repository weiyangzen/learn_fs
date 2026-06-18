# subset-b-000490 grouped research

This grouped report covers the Alluxio worker block allocator, annotator, evictor, IO, management, metadata, reviewer, file-master client, and gRPC read/write files listed for `subset-b-000490`. Each section preserves the source path so the reconciliation step can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/RoundRobinAllocator.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/RoundRobinAllocator.java

Purpose: Implements the `Allocator` policy that chooses storage directories in round-robin order while preferring higher tiers first. It handles unrestricted writes, any-dir-in-tier writes, and exact-directory writes.

Important APIs: constructor seeds one iterator per tier from `BlockMetadataView`; `allocateBlockWithView` refreshes the active metadata view; private `allocateBlock` dispatches by `BlockStoreLocation`; `getNextAvailDirInTier` scans one tier for medium, space, and reviewer acceptance.

Control flow: any-tier allocations iterate tiers in metadata order, and each tier resumes from the last stored directory iterator. Exact-directory allocations skip `Reviewer` so caller-directed placement is not probabilistically rejected.

State and persistence: In-memory only. The allocator stores `mMetadataView`, a configured `Reviewer`, and per-tier iterator positions; no disk state is written. It is annotated `@NotThreadSafe`.

Dependencies and integration: Consumes `BlockMetadataView`, `StorageTierView`, `StorageDirView`, `BlockStoreLocation`, and `Reviewer.Factory`. It is used by the block store and deprecated evictors to locate space for new temp blocks or moved blocks.

Risks and test signals: Iterator state is initialized from the constructor view but the metadata view can later be replaced, so tests should cover tier/directory changes across `allocateBlockWithView`. Validate any-tier priority, per-tier round-robin fairness, medium filtering, exact-dir reviewer bypass, and reviewer rejection fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/RoundRobinAllocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockAnnotator.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockAnnotator.java

Purpose: Defines the policy interface for assigning sortable metadata to blocks so eviction and tier management can rank blocks without depending directly on a specific algorithm.

Important APIs: `Factory.create()` instantiates the configured class from `PropertyKey.WORKER_BLOCK_ANNOTATOR_CLASS`; `updateSortedField` updates one block at the current logical time; `updateSortedFields` updates a batch for offline schemes; `isOnlineSorter` tells iterators whether lazy full-order refresh is needed.

Control flow: Implementations are called from block-store event listeners during access, commit, move, or lazy iterator creation. Online algorithms update per event, while offline algorithms can refresh a list before iteration.

State and persistence: The interface persists no state itself. Implementations such as LRU and LRFU keep logical clocks and score values in memory only.

Dependencies and integration: Uses `BlockSortedField` and `Pair<Long,T>`, plus Alluxio configuration and reflection utilities. `DefaultBlockIterator` is the primary consumer.

Risks and test signals: Generic type safety is weak because callers often use raw `BlockAnnotator`. Tests should verify configured class construction, online/offline behavior, and batch update semantics for algorithms used by tier management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockAnnotator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockIterator.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockIterator.java

Purpose: Provides the abstraction for ordered block traversal used by eviction, promotion, alignment, and swap calculations.

Important APIs: `getIterator` returns block IDs for a location and order; `getIntersectionList` builds a bounded ordered intersection candidate list; `getSwaps` returns paired block IDs to swap between locations; `aligned` detects tier overlap; `getListeners` exposes store event listeners that keep iterator state current.

Control flow: Management tasks query this interface for ranked blocks and pass filters for pinned, locked, or otherwise non-evictable blocks. Implementations may be event-driven (`DefaultBlockIterator`) or evictor-emulated (`EmulatingBlockIterator`).

State and persistence: Interface only. Implementations own in-memory ranking state and do not persist ordering to disk.

Dependencies and integration: Integrates with `BlockStoreLocation`, `BlockOrder`, `BlockStoreEventListener`, and `Pair`. Tier management depends heavily on `getSwaps` and `aligned`.

Risks and test signals: The filter function returns true for blocks to exclude in current implementations, so call sites need clear tests to avoid inverted predicates. Exercise empty locations, any-tier locations, reverse order, and partial intersections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockOrder.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockOrder.java

Purpose: Small enum that standardizes natural and reverse ordering for block sorted fields.

Important APIs: Values are `NATURAL` and `REVERSE`; `reversed()` returns the opposite; `comparator()` returns a raw `Comparator<Comparable>` for sorted-field comparisons.

Control flow: Iterator implementations use the enum to pick ascending or descending per-directory iterators and to compare boundary blocks for tier alignment.

State and persistence: Stateless enum with no persistence.

Dependencies and integration: Used by `DefaultBlockIterator`, `EmulatingBlockIterator`, `AlignTask`, `PromoteTask`, `SwapRestoreTask`, and `TierManagementTaskProvider`.

Risks and test signals: Raw comparator typing can hide class-cast issues until runtime. Test reverse pairing, comparator direction, and illegal/default cases only through enum exhaustiveness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockOrder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockSortedField.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockSortedField.java

Purpose: Marker-style public API for values that can sort blocks for eviction and management decisions.

Important APIs: Extends `Comparable<BlockSortedField>` and has no methods of its own.

Control flow: Annotators produce these fields, `SortedBlockSet` stores them, and `DefaultBlockIterator` compares them through `BlockOrder`.

State and persistence: Interface only. Concrete field values are in-memory ranking metadata.

Dependencies and integration: Implemented by `LRUAnnotator.LRUSortedField` and `LRFUAnnotator.LRFUSortedField`.

Risks and test signals: Implementations must keep `compareTo`, `equals`, and `hashCode` coherent enough for sorted sets. Tests should include equal score collisions and mixed-type rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockSortedField.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/DefaultBlockIterator.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/DefaultBlockIterator.java

Purpose: Event-driven `BlockIterator` backed by one `SortedBlockSet` per storage directory. It ranks blocks with the configured `BlockAnnotator` and supports eviction, promotion, and tier alignment queries.

Important APIs: Constructor initializes per-dir sets from `BlockMetadataManager`; `getIterator`, `getIntersectionList`, `getSwaps`, and `aligned` implement ranked traversal and comparisons; `getListeners` returns an internal `AbstractBlockStoreEventListener`.

Control flow: Initialization creates a set for each directory and inserts existing block IDs. Access and commit events call `blockUpdated`; remove events call `blockRemoved`; client and worker moves transfer the previous sort field to the new location. Iterator creation gathers directory locations under the requested location, refreshes dirty offline locations, creates ordered iterators, and merge-sorts them.

State and persistence: Maintains concurrent maps of directory locations to sorted sets and dirty offline locations. State is memory-only and reconstructed from metadata on startup.

Dependencies and integration: Depends on `BlockMetadataManager`, `StorageTier`, `StorageDir`, `SortedBlockSet`, `BlockAnnotator`, and Guava iterators. It is consumed by tier management tasks through `BlockMetadataManager.getBlockIterator()`.

Risks and test signals: Moving a block preserves the old sort field, so access recency may not change on moves. Offline refresh is synchronized but per-dir sets are concurrently updated. Tests should cover listener registration, storage loss, moved block ordering, LRFU lazy refresh, merged iteration across multiple dirs, filtered swaps, and alignment boundary comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/DefaultBlockIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/EmulatingBlockIterator.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/EmulatingBlockIterator.java

Purpose: Adapter that exposes deprecated `Evictor` ordering through the newer `BlockIterator` interface.

Important APIs: Constructor accepts `BlockMetadataManager` and `Evictor`; `getIterator` builds a best-effort eviction plan and extracts ordered move or evict block IDs; intersection, swap, and alignment APIs return empty or false because they cannot be derived from old evictors.

Control flow: `initEvictorConfiguration` computes per-tier reserved-space thresholds from configured high and low watermarks. `getIterator` invokes `freeSpaceWithView` against a fresh `BlockMetadataEvictorView`, extracts `toMove` source IDs if present or `toEvict` IDs otherwise, and reverses for reverse order.

State and persistence: Keeps the metadata manager, evictor, and an in-memory `mReservedSpaces` map. No persistent state.

Dependencies and integration: Depends on deprecated `Evictor`, `EvictionPlan`, `BlockMetadataEvictorView`, tier association, and watermark properties. It also forwards listeners if the evictor implements `BlockStoreEventListener`.

Risks and test signals: The adapter assumes plan list order reflects eviction order and cannot support tier alignment. Tests should cover watermark validation, ANY_TIER reservation accumulation, reverse order, null plan handling expectations, and listener forwarding for old evictors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/EmulatingBlockIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/LRFUAnnotator.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/LRFUAnnotator.java

Purpose: Implements LRFU block ranking, combining recency and frequency through an attenuated combined recency-frequency score.

Important APIs: `updateSortedField` increments a logical clock for one access; `updateSortedFields` refreshes a batch at the same clock for offline ordering; `isOnlineSorter` returns false; nested `LRFUSortedField` compares by CRF value.

Control flow: On an update, a missing field starts with CRF 1. Existing fields decay by `pow(1 / attenuation, interval * step)` and add 1 for the new access. Offline batch update uses the current clock without incrementing per block.

State and persistence: Stores an `AtomicLong` logical clock. Sort fields store clock and CRF in memory only.

Dependencies and integration: Reads `WORKER_BLOCK_ANNOTATOR_LRFU_STEP_FACTOR` and `WORKER_BLOCK_ANNOTATOR_LRFU_ATTENUATION_FACTOR`. Used by `DefaultBlockIterator` as an offline annotator requiring lazy total-order refresh.

Risks and test signals: Bad step or attenuation configuration can skew ordering. Equality and hash code ignore clock and use only CRF, relying on `SortedBlockSet` change indexes for tie-breaking. Tests should cover decay math, batch refresh stability, equal CRF ties, and low/high factor boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/LRFUAnnotator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/LRUAnnotator.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/LRUAnnotator.java

Purpose: Implements simple LRU ranking by assigning monotonically increasing logical clock values to accessed or committed blocks.

Important APIs: `updateSortedField` increments the clock and returns a new `LRUSortedField`; `updateSortedFields` sets a batch to the current clock; `isOnlineSorter` returns true; nested `LRUSortedField` compares by clock.

Control flow: Each observed block access gets a larger clock and therefore sorts later under natural order. Management tasks use natural order for cold blocks and reverse order for hot blocks.

State and persistence: Maintains an in-memory `AtomicLong` clock and transient sort fields only.

Dependencies and integration: Used through `BlockAnnotator` by `DefaultBlockIterator`, commonly as the default online orderer.

Risks and test signals: Clock values are process-local and reset on restart, so startup ordering depends on metadata scan order until accesses arrive. Tests should cover monotonic update, compare/equality behavior, and merged per-dir ordering after access events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/LRUAnnotator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/SortedBlockSet.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/SortedBlockSet.java

Purpose: Concurrent sorted collection mapping block IDs to annotator fields while preserving deterministic identity for duplicate sort values.

Important APIs: `getSortField`, `put`, `remove`, `size`, `getAscendingIterator`, and `getDescendingIterator`. The inner `SortedBlockSetEntry` compares by sorted field and then change index.

Control flow: `put` uses `ConcurrentHashMap.compute` per block ID to remove the old entry, assign a new change index, insert a new entry, and update the last-sort map. Iterators transform sorted-set entries into block ID and field pairs.

State and persistence: Holds a `ConcurrentSkipListSet`, a concurrent block-to-change-index/field map, and an atomic change index. All state is in memory.

Dependencies and integration: Used by `DefaultBlockIterator` per directory. Depends on Alluxio `Pair`, Guava `Iterators`, and Java concurrent collections.

Risks and test signals: Removal logs a warning when a block is absent; duplicate fields depend on change index uniqueness. Tests should cover update replacement, concurrent per-block updates, iterator ordering, duplicate sorted fields, and remove-after-move behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/SortedBlockSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/AbstractEvictor.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/AbstractEvictor.java

Purpose: Deprecated base implementation for eviction policies, providing recursive cascading eviction across storage tiers.

Important APIs: Constructor takes `BlockMetadataEvictorView` and `Allocator`; `freeSpaceWithView` builds an `EvictionPlan`; protected `cascadingEvict` selects candidate blocks and recursively moves them down-tier or evicts from the last tier; subclass API is `getBlockIterator`.

Control flow: The evictor first checks whether a directory already has requested space. If not, it scans blocks in policy order, accumulates candidate blocks per directory, picks the directory with maximum reclaimable space, then tries to allocate each candidate in the next tier. Failed next-tier allocation triggers recursive eviction; last-tier candidates are evicted.

State and persistence: Keeps mutable metadata view and allocator references. It marks projected moves in `StorageDirEvictorView` during plan generation and clears marks before returning.

Dependencies and integration: Depends on `BlockMetadataEvictorView`, storage views, `Allocator`, `EvictionDirCandidates`, `EvictionPlan`, and `BlockTransferInfo`. Used by deprecated `LRUEvictor` and by `EmulatingBlockIterator`.

Risks and test signals: Not thread-safe and deprecated. BEST_EFFORT can return a plan even when guaranteed space is not reached. Tests should cover recursive cascading, stale block removal from iterators, mark cleanup, exact/any location handling, and null plan behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/AbstractEvictor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/BlockTransferInfo.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/BlockTransferInfo.java

Purpose: Immutable transfer-order value object describing a block move or a two-block swap.

Important APIs: `createMove`, `createSwap`, getters for source/destination locations and block IDs, `isSwap`, and `toString`.

Control flow: Move instances set destination block ID to an invalid sentinel; swap instances include both IDs. `BlockTransferExecutor` branches on `isSwap` to perform one or two moves and enable reserved space for swaps.

State and persistence: Thread-safe immutable fields only. No persistence.

Dependencies and integration: Used by eviction plans and tier-management tasks as the common transfer command structure.

Risks and test signals: The sentinel value is `-1`, so negative real block IDs would be invalid elsewhere. Tests should verify move versus swap classification, location preservation, and executor behavior for each type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/BlockTransferInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/EvictionDirCandidates.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/EvictionDirCandidates.java

Purpose: Helper for deprecated evictors that groups candidate blocks by directory and tracks which directory can provide the most space.

Important APIs: `add`, `candidateSize`, `candidateBlocks`, and `candidateDir`.

Control flow: Each added block appends to that directory's candidate list, updates accumulated candidate bytes, then computes candidate capacity as added bytes plus current available bytes. The max directory becomes the eviction target.

State and persistence: In-memory `Map<StorageDirEvictorView, Pair<List<Long>,Long>>`, max byte count, and selected directory. Not thread-safe and not persisted.

Dependencies and integration: Used inside `AbstractEvictor.cascadingEvict`.

Risks and test signals: Candidate selection assumes directory availability is stable while candidates are gathered. Tests should cover empty candidates, multiple dirs, tie behavior, and candidate list order preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/EvictionDirCandidates.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/EvictionPlan.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/EvictionPlan.java

Purpose: Data container listing block transfers and block removals required to free space.

Important APIs: Constructor validates non-null move and evict lists; `toMove`, `toEvict`, `isEmpty`, and `toString`.

Control flow: Evictors append to the contained mutable lists while building a plan. Callers then execute moves and evictions in order.

State and persistence: Stores caller-provided lists and exposes them directly. Thread-safe annotation applies to object reference safety, not immutability of list contents.

Dependencies and integration: Uses `BlockTransferInfo`, `Pair<Long,BlockStoreLocation>`, and Guava preconditions. Consumed by block store eviction and emulated iterators.

Risks and test signals: Direct list exposure means later mutations affect the plan. Tests should cover empty plan semantics, null rejection, and execution behavior when move and evict lists are both populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/EvictionPlan.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/Evictor.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/Evictor.java

Purpose: Public deprecated eviction policy interface for producing plans that free worker block-store space.

Important APIs: `Mode` enum with `BEST_EFFORT` and `GUARANTEED`; `Factory.create` instantiates configured `WORKER_EVICTOR_CLASS`; overloaded `freeSpaceWithView` methods produce an `EvictionPlan`.

Control flow: Callers provide requested free bytes, a location range, and a `BlockMetadataEvictorView`. Guaranteed mode may return null if no feasible plan exists; best-effort returns the maximum possible plan.

State and persistence: Interface only. Implementations maintain policy state in memory.

Dependencies and integration: References `LocalBlockStore`, `Allocator`, `BlockMetadataEvictorView`, and `BlockStoreLocation`. Retained for compatibility and emulation.

Risks and test signals: Deprecated in favor of annotator-backed iteration. Tests should verify factory configuration, guaranteed versus best-effort semantics, and invalid location handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/Evictor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/LRUEvictor.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/LRUEvictor.java

Purpose: Deprecated LRU evictor implementation backed by an access-ordered `LinkedHashMap`.

Important APIs: Constructor preloads evictable existing blocks; `getBlockIterator` returns a snapshot in LRU order; event callbacks update or remove IDs from the LRU map.

Control flow: Access and local commit insert into the access-ordered map, moving entries to the tail. Remove and lost events delete entries. `AbstractEvictor` consumes the snapshot iterator from least to most recently used.

State and persistence: Maintains a synchronized access-ordered map in memory. The map is rebuilt from metadata when the evictor is constructed.

Dependencies and integration: Extends `AbstractEvictor`, consumes storage evictor views, and can be wrapped by `EmulatingBlockIterator`.

Risks and test signals: Snapshot iteration may lag concurrent events, and the implementation is marked not thread-safe despite a synchronized map. Tests should cover preload filtering, event updates, remove callbacks, and order after repeated accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/LRUEvictor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/package-info.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/package-info.java

Purpose: Package documentation for deprecated block evictor implementations.

Important APIs: No executable APIs. The package-level docs identify the eviction package role.

Control flow: None at runtime.

State and persistence: None.

Dependencies and integration: The package contains `Evictor`, `AbstractEvictor`, `LRUEvictor`, `EvictionPlan`, `BlockTransferInfo`, and helper classes that older block store paths or emulation paths may still reference.

Risks and test signals: Because the package is deprecated, tests should focus on compatibility coverage rather than new feature expansion. Build signals are package Javadoc and import correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/BlockStreamTracker.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/BlockStreamTracker.java

Purpose: Static event hub for block reader and writer open/close events.

Important APIs: `registerListener`, `unregisterListener`, `readerOpened`, `readerClosed`, `writerOpened`, and `writerClosed`.

Control flow: Store reader and writer wrappers call the open/close methods, which synchronously notify all registered `BlockClientListener`s.

State and persistence: Holds a static `CopyOnWriteArrayList` of listeners. No persisted state.

Dependencies and integration: Feeds `DefaultStoreLoadTracker`, which uses stream activity to pause background management transfers.

Risks and test signals: Listener callbacks run inline and can delay close/open paths if expensive. Tests should cover registration removal, multiple listeners, open/close symmetry, and no concurrent modification failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/BlockStreamTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/MetricAccountingBlockReader.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/MetricAccountingBlockReader.java

Purpose: Decorates a `BlockReader` to increment cache read byte metrics for every read path.

Important APIs: Overrides `read`, `getChannel`, `transferTo`, `getLength`, `isClosed`, `getLocation`, `toString`, and `close`.

Control flow: `read` counts bytes remaining in the returned `ByteBuffer`; wrapped channel counts successful `read` byte counts; `transferTo` counts non-EOF byte counts. Other methods delegate.

State and persistence: Holds one delegate reader. Metrics are emitted to `MetricsSystem`; no local persistence.

Dependencies and integration: Uses `MetricKey.WORKER_BYTES_READ_CACHE`, Netty `ByteBuf`, and Java NIO channels. It integrates with block reader creation paths that want cache metrics.

Risks and test signals: ByteBuffer position/limit assumptions determine counted bytes. Tests should cover EOF `-1`, partial channel reads, transferTo EOF, close delegation, and that counting does not double count across APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/MetricAccountingBlockReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/StoreBlockReader.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/StoreBlockReader.java

Purpose: Local file block reader wrapper that emits stream tracking events for committed block reads.

Important APIs: Constructor opens the block path from `BlockMeta`; `close` sends a close event then delegates to `LocalFileBlockReader.close`.

Control flow: For positive session IDs, construction calls `BlockStreamTracker.readerOpened`; close calls `readerClosed`. Internal or non-session reads skip tracking.

State and persistence: Holds session ID and block metadata. It reads the committed block file path but does not alter metadata.

Dependencies and integration: Extends `LocalFileBlockReader`, consumes `BlockMeta`, and feeds `DefaultStoreLoadTracker` through `BlockStreamTracker`.

Risks and test signals: Close must be called exactly once by callers to avoid stale load-tracker state; repeated close behavior depends on superclass. Tests should cover tracked versus untracked session IDs and exception behavior around close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/StoreBlockReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/StoreBlockWriter.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/StoreBlockWriter.java

Purpose: Local file block writer wrapper that emits stream tracking events for temp block writes.

Important APIs: Constructor opens the temp path from `TempBlockMeta`; `close` sends writer close events and delegates to `LocalFileBlockWriter.close`.

Control flow: Positive session IDs produce `writerOpened` on construction and `writerClosed` on close. Internal writes skip tracking.

State and persistence: Holds temp block metadata and writes to the temp block file path through the superclass.

Dependencies and integration: Extends `LocalFileBlockWriter`, consumes `TempBlockMeta`, and feeds load detection through `BlockStreamTracker`.

Risks and test signals: If writer construction succeeds but close is missed, background management may see stale load. Tests should cover event ordering, session filtering, and close delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/StoreBlockWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/AbstractBlockManagementTask.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/AbstractBlockManagementTask.java

Purpose: Shared base for background block management tasks, wiring common store, metadata, load, executor, and transfer-executor dependencies.

Important APIs: Constructor stores dependencies and creates a `BlockTransferExecutor` using `WORKER_MANAGEMENT_BLOCK_TRANSFER_CONCURRENCY_LIMIT`.

Control flow: Concrete tasks call `mTransferExecutor` to execute generated move or swap orders.

State and persistence: Holds references for a single task instance. No persistence.

Dependencies and integration: Used by tier tasks `AlignTask`, `PromoteTask`, and `SwapRestoreTask`.

Risks and test signals: The eviction view is captured at task creation, so long-running tasks may act on stale metadata. Tests should verify configured concurrency is passed and concrete task constructors wire dependencies correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/AbstractBlockManagementTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockManagementTask.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockManagementTask.java

Purpose: Minimal interface for background worker block management jobs.

Important APIs: `run()` returns a `BlockManagementTaskResult`.

Control flow: `ManagementTaskCoordinator` obtains implementations from providers and runs them on the coordinator thread.

State and persistence: Interface only.

Dependencies and integration: Implemented by tier management tasks and returned by `ManagementTaskProvider`.

Risks and test signals: Implementations should be idempotent enough for repeated coordinator loops. Tests should check task result reporting for progress and no-progress cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockManagementTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockManagementTaskResult.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockManagementTaskResult.java

Purpose: Aggregates per-operation results for one management task run.

Important APIs: `addOpResults`, `getOperationResult`, `noProgress`, and `toString`.

Control flow: Tasks merge `BlockOperationResult`s by `BlockOperationType`. The coordinator checks `noProgress` to decide whether to sleep after failures or backoffs.

State and persistence: In-memory `HashMap` of operation type to mutable result. Not thread-safe and not persisted.

Dependencies and integration: Used by all management tasks and coordinator logging/backoff logic.

Risks and test signals: `noProgress` returns true when total operations equal failures plus backoffs; an empty result also returns true because counts are zero. Tests should cover empty, partial success, all failure, and merged multi-operation results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockManagementTaskResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockOperationResult.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockOperationResult.java

Purpose: Counter container for one management operation class.

Important APIs: Constructors, `mergeWith`, `opCount`, `failCount`, `backOffCount`, and `toString`.

Control flow: Transfer and removal execution paths create results; task result aggregation mutates them via `mergeWith`.

State and persistence: Holds integer counters in memory. No persistence and no synchronization.

Dependencies and integration: Used by `BlockTransferExecutor`, `SwapRestoreTask`, and `BlockManagementTaskResult`.

Risks and test signals: Counters can be merged repeatedly and mutate the receiving instance. Tests should cover merge arithmetic and no-progress interpretation in the parent result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockOperationResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockOperationType.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockOperationType.java

Purpose: Enumerates operation categories emitted by block management tasks.

Important APIs: Enum values are `ALIGN_SWAP`, `PROMOTE_MOVE`, `SWAP_RESTORE_REMOVE`, `SWAP_RESTORE_FLUSH`, and `SWAP_RESTORE_BALANCE`.

Control flow: Tasks use these keys to add results to `BlockManagementTaskResult`.

State and persistence: Stateless enum.

Dependencies and integration: Ties result reporting to `AlignTask`, `PromoteTask`, and `SwapRestoreTask`.

Risks and test signals: Comments reference task classes without imports and do not affect runtime. Tests should assert task result buckets use the expected enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockOperationType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockTransferExecutor.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockTransferExecutor.java

Purpose: Executes lists of block move and swap orders concurrently while backing off from active user IO.

Important APIs: Constructor wires executor, block store, load tracker, concurrency limit, and partitioner; `executeTransferList` optionally accepts an exception handler; private `executeTransferPartition` performs each transfer.

Control flow: Empty lists return an empty result. Non-empty lists are partitioned, submitted via `ExecutorService.invokeAll`, and partition counters are aggregated. Each transfer is skipped if `loadDetected` sees activity at source or destination; moves call `LocalBlockStore.moveBlock`; swaps perform two moves with reserved space enabled.

State and persistence: Holds service dependencies only. Operations mutate block-store metadata and underlying block files through `LocalBlockStore`.

Dependencies and integration: Consumes `BlockTransferInfo`, `AllocateOptions`, `Sessions`, `StoreLoadTracker`, and `BlockTransferPartitioner`. Used by all concrete tier tasks.

Risks and test signals: TODO notes missing location locks, so concurrent partitions can collide. Swap is not guaranteed atomically. Tests should cover partition aggregation, backoff counting, interrupt handling, exception callback invocation, and swap reserved-space behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockTransferExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockTransferPartitioner.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockTransferPartitioner.java

Purpose: Greedily partitions block transfers for concurrent execution, preferring groups that share exact source or destination locations.

Important APIs: `partitionTransfers`; private `findTransferBucketKey`; private `balancePartitions`; enum `TransferPartitionKey`.

Control flow: It picks source or destination as a bucket key based on how many transfers have exact locations and how distinct those locations are. If no exact locations exist, it returns one partition. If too many buckets exist, it greedily balances them by transfer count.

State and persistence: Stateless beyond local collections. No persistence.

Dependencies and integration: Used only by `BlockTransferExecutor`.

Risks and test signals: Balancing ignores block sizes and does not prevent all read/write conflicts. Tests should cover source-key, destination-key, no-key, tie by distinct count, partition-limit balancing, and stable handling of any-dir locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockTransferPartitioner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/DefaultStoreLoadTracker.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/DefaultStoreLoadTracker.java

Purpose: Detects active worker load by tracking open block reader and writer clients per precise storage location.

Important APIs: Constructor registers with `BlockStreamTracker`; `loadDetected`; `clientOpened`; `clientClosed`; private `locationValid`.

Control flow: Opens add clients to a concurrent set by location. Closes schedule delayed removal after `WORKER_MANAGEMENT_LOAD_DETECTION_COOL_DOWN_TIME`, leaving a cool-down window. `loadDetected` checks tracked locations that belong to any queried location range.

State and persistence: Maintains a concurrent map from exact `BlockStoreLocation` to client sets and a single-thread scheduled executor. State is in memory and can be stale if close events are lost.

Dependencies and integration: Implements `StoreLoadTracker` and `BlockClientListener`; receives events from `BlockStreamTracker`; used by `ManagementTaskCoordinator` and `BlockTransferExecutor`.

Risks and test signals: No unregister/close method appears here for the listener or scheduler. Tests should cover precise-location validation, delayed close removal, any-tier queries, concurrent clients, and stale close error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/DefaultStoreLoadTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/ManagementTaskCoordinator.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/ManagementTaskCoordinator.java

Purpose: Background coordinator that repeatedly chooses and runs block management tasks such as tier alignment, swap restoration, and promotion.

Important APIs: Constructor wires block store, metadata manager, load tracker, and eviction-view supplier; `start`; `close`; private `initializeTaskProviders`, `getNextTask`, and `runManagement`.

Control flow: A daemon runner loop optionally backs off when worker load is detected, asks providers in priority order for a task, runs the selected task on the coordinator thread, logs results, and sleeps after no-progress runs. `close` shuts down the task executor and interrupts the runner.

State and persistence: Holds a runner thread, fixed task executor, provider list, and service references. No persistent state.

Dependencies and integration: Reads management backoff and thread-count config. Currently initializes `TierManagementTaskProvider`; tasks use the same executor for transfer partitions.

Risks and test signals: Provider order creates implicit priority. Exceptions are logged and loop continues. Tests should cover start/close lifecycle, load backoff, no-task sleep, no-progress sleep, provider priority, and interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/ManagementTaskCoordinator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/ManagementTaskProvider.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/ManagementTaskProvider.java

Purpose: Factory interface for management subsystems that can supply the next pending task.

Important APIs: `getTask()` returns a `BlockManagementTask` or null.

Control flow: `ManagementTaskCoordinator` queries providers in order until one returns a task.

State and persistence: Interface only.

Dependencies and integration: Implemented by `TierManagementTaskProvider`.

Risks and test signals: Null is the no-work signal, so implementations must avoid returning null for transient failures without intentional backoff. Tests should verify coordinator priority and null handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/ManagementTaskProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/StoreLoadTracker.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/StoreLoadTracker.java

Purpose: Abstraction for detecting user IO activity on worker storage locations.

Important APIs: `loadDetected(BlockStoreLocation... locations)`.

Control flow: Transfer execution and coordinator loops call this before background work to avoid interfering with user activity.

State and persistence: Interface only.

Dependencies and integration: Implemented by `DefaultStoreLoadTracker`; consumed by `BlockTransferExecutor` and `ManagementTaskCoordinator`.

Risks and test signals: Varargs semantics mean callers can check multiple locations in one decision. Tests should cover implementations with exact, tier, and any-tier location ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/StoreLoadTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/AlignTask.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/AlignTask.java

Purpose: Swaps blocks between adjacent tiers so hotter or higher-ranked blocks reside in upper tiers and colder blocks move down.

Important APIs: `run`; private `generateSwapTransferInfos`.

Control flow: For each tier intersection, it requests paired swap lists from `BlockIterator.getSwaps` using upper-tier natural order and lower-tier reverse order, filtered by evictability. It generates location-aware swap transfer infos, sorts both sides by location, and executes swaps. Resource exhaustion during swap marks `TierManagementTaskProvider` to run swap restoration.

State and persistence: Per-run transient lists only. Actual moves are executed through `LocalBlockStore`, affecting metadata and files.

Dependencies and integration: Uses `BlockMetadataManager`, `BlockMetadataEvictorView`, `BlockTransferExecutor`, `BlockOrder`, `BlockTransferInfo`, and `ResourceExhaustedRuntimeException`.

Risks and test signals: Sorting source and destination lists independently by location can pair blocks differently than the iterator returned. Tests should cover equal list sizes, filter behavior, resource-exhausted callback, generated swap locations, and partial transfer failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/AlignTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/PromoteTask.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/PromoteTask.java

Purpose: Moves highly ranked blocks from lower tiers to adjacent upper tiers until configured range or quota limits are reached.

Important APIs: `run`; private `getTransferInfos`.

Control flow: For each tier intersection, it iterates lower-tier blocks in reverse order, computes the upper tier projected used ratio, stops at `WORKER_MANAGEMENT_TIER_PROMOTE_QUOTA_PERCENT`, and creates move transfer infos up to `WORKER_MANAGEMENT_TIER_PROMOTE_RANGE`.

State and persistence: Per-run transfer list and byte projection only. Moves mutate block store through the transfer executor.

Dependencies and integration: Uses block iterator ordering, metadata tier capacity, evictor view block metadata, `BlockTransferExecutor`, and management configuration.

Risks and test signals: The projection adds selected block sizes after checking quota, so a selected block can push usage above quota. Tests should cover quota boundaries, missing metadata, empty lower tiers, promote range limits, and transfer result aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/PromoteTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/SwapRestoreTask.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/SwapRestoreTask.java

Purpose: Restores reserved swap space after alignment swaps fail or consume too much reserved capacity.

Important APIs: `run`; private `getSwapRestorePlan`; private `getBalancingTransfersList`.

Control flow: The restore plan cascades bytes beyond reserve down tiers, removing blocks from the last tier and moving blocks down from higher tiers. After removals and flush transfers, balancing scans each directory whose available bytes are below reserved bytes and moves cold blocks to sibling dirs with enough surplus.

State and persistence: Uses transient plan lists and storage view mark accounting. Removals and moves mutate block store metadata and files.

Dependencies and integration: Uses `LocalBlockStore`, `BlockMetadataEvictorView`, `StorageTierAssoc`, `StorageDirEvictorView`, `BlockIterator`, `BlockTransferExecutor`, and internal sessions.

Risks and test signals: Balancing does not evict if no sibling has room and may leave reserved space unrecovered. Tests should cover cascading math, last-tier removals, sibling balance mark accounting, missing metadata, and partial failure counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/SwapRestoreTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/TierManagementTaskProvider.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/TierManagementTaskProvider.java

Purpose: Chooses the next tier-management task to run: swap restore, alignment, promotion, or none.

Important APIs: Constructor wires services; static `setSwapRestoreRequired`; `getTask`; private `findNextTask`; enum `TierManagementTaskType`.

Control flow: Swap restore has first priority when enabled and flagged. Otherwise it builds a fresh evictor view, checks each adjacent tier pair for misalignment, then checks promotion eligibility based on high-tier used ratio and lower-tier evictable blocks.

State and persistence: Holds service references and a static boolean swap-restore flag. No persistence.

Dependencies and integration: Used by `ManagementTaskCoordinator`; creates `AlignTask`, `PromoteTask`, and `SwapRestoreTask`.

Risks and test signals: Static swap-restore flag is process-global and not synchronized. Provider decisions depend on current block iterator ordering and evictor view freshness. Tests should cover task priority, disabled feature flags, quota thresholds, no evictable lower blocks, and flag reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/TierManagementTaskProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultBlockMeta.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultBlockMeta.java

Purpose: Thread-safe metadata for a committed Alluxio worker block.

Important APIs: Static `commitPath`; constructors from explicit fields or `TempBlockMeta`; getters for block ID, location, size, path, and parent directory.

Control flow: The temp-block constructor reads the committed file length after the data file has moved, so metadata size reflects actual disk contents.

State and persistence: Immutable references and size. The committed block persists as a numeric file directly under the storage directory path.

Dependencies and integration: Uses `StorageDir`, `StorageTier`, `BlockStoreLocation`, `PathUtils`, and `File`. Stored in `DefaultStorageDir` committed block maps.

Risks and test signals: Size accuracy depends on file move ordering. Tests should cover commit path construction, medium-aware location, temp-to-committed conversion after file creation, and immutability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultBlockMeta.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultStorageDir.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultStorageDir.java

Purpose: Concrete storage-directory metadata container tracking committed blocks, temp blocks, per-session temp ownership, capacity, reserved bytes, available bytes, and committed bytes.

Important APIs: `newStorageDir`, `initializeMeta`, block/temp add/remove/get APIs, `resizeTempBlockMeta`, `cleanupSessionTempBlocks`, `getSessionTempBlocks`, `toBlockStoreLocation`, and byte getters.

Control flow: Startup creates the directory, scans direct children, preserves numeric committed block files as `DefaultBlockMeta`, deletes invalid files, and deletes non-temp subdirectories. Adding committed or temp blocks reserves space; removing reclaims space; temp resize only grows. Session cleanup removes listed temp blocks and reclaims their space.

State and persistence: In-memory maps mirror disk files. Committed blocks are numeric files under the storage dir; temp blocks live under the configured tmp folder. Atomic byte counters track capacity accounting, including reserved space.

Dependencies and integration: Used by `DefaultStorageTier`, metadata manager, allocator and evictor views. Depends on Alluxio config, exceptions, file utilities, and Guava sets.

Risks and test signals: Class is not thread-safe even though byte counters are atomic; callers must synchronize at higher layers. Startup deletes unexpected paths. Tests should cover disk scan cleanup, capacity with reserved bytes, duplicate block rejection, temp session maps, resize growth, session cleanup partial lists, and committed/temp byte accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultStorageDir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultStorageTier.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultStorageTier.java

Purpose: Concrete storage-tier container for configured storage directories, tier capacity aggregation, and lost-storage tracking.

Important APIs: `newStorageTier`, `initStorageTier`, `checkEnoughMemSpace`, getters for ordinal, alias, capacity, available bytes, directories, lost storage, and `removeStorageDir`.

Control flow: Initialization reads configured paths, quotas, and medium types, expands worker data directories, applies reserved bytes when multi-tier alignment is enabled, creates each `DefaultStorageDir`, records failures as lost storage, deletes temp directories, and validates single memory-tier tmpfs capacity on Linux.

State and persistence: Holds directory map and lost-storage path list in memory. It initializes and cleans real filesystem storage directories.

Dependencies and integration: Uses Alluxio configuration templates, storage tier association, path/file utilities, shell mount inspection, and OS utilities. Created by metadata manager during worker startup.

Risks and test signals: Misconfigured quota/medium lists reuse last configured value for extra paths. Initialization can delete temp directories and invalid storage contents. Tests should cover multi-dir config, initialization failure recording, reserved-byte injection, tmpfs size validation, and remove-storage-dir behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultStorageTier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultTempBlockMeta.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultTempBlockMeta.java

Purpose: Metadata for an uncommitted worker block file owned by a session.

Important APIs: Static `tempPath`; getters for size, path, ID, location, parent dir, commit path, session ID; `setBlockSize`.

Control flow: Temp paths are built from storage dir, configured temp folder, `sessionId % SUB_DIR_MAX`, and a file name containing hex session ID plus block ID. Commit path points to the final numeric committed block file.

State and persistence: Keeps mutable temp block size in memory. The temp file persists on disk until commit, abort, or cleanup.

Dependencies and integration: Used by `DefaultStorageDir`, `StoreBlockWriter`, and block store write paths. Reads temp folder configuration statically.

Risks and test signals: Static config values are captured when the class loads. Tests should cover path format, subdirectory distribution, size growth, location medium, and commit path consistency with `DefaultBlockMeta`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultTempBlockMeta.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirAllocatorView.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirAllocatorView.java

Purpose: Limited storage-directory view for allocators.

Important APIs: Constructor and override `getAvailableBytes`.

Control flow: If the parent tier view is using reserved space, available bytes are computed as capacity minus committed bytes; otherwise it returns the directory's available bytes. This lets internal moves use reserved capacity while normal allocations do not.

State and persistence: View over live `StorageDir`; no independent persistence.

Dependencies and integration: Created by `StorageTierAllocatorView` and consumed by allocators such as `RoundRobinAllocator`.

Risks and test signals: The local `reservedBytes` variable is unused, and available-byte semantics differ sharply based on `mUseReservedSpace`. Tests should cover both reserved and normal modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirAllocatorView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirEvictorView.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirEvictorView.java

Purpose: Limited storage-directory view for evictors and management planners, including projected move-in and move-out accounting.

Important APIs: `getAvailableBytes`, `getEvictableBlocks`, `getEvitableBytes`, `clearBlockMarks`, `isMarkedToMoveOut`, `markBlockMoveIn`, and `markBlockMoveOut`.

Control flow: Available bytes are adjusted by projected move-out bytes minus move-in bytes. Evictable block lists and bytes filter the underlying directory's blocks through `BlockMetadataEvictorView.isBlockEvictable`.

State and persistence: Maintains in-memory sets of block IDs marked to move in/out and their byte totals. Underlying directory state persists separately.

Dependencies and integration: Created by `StorageTierEvictorView`; used by deprecated evictors and swap-restore balancing.

Risks and test signals: Class is not synchronized; duplicate marks are ignored by sets. There is a typo-like API name `getEvitableBytes`. Tests should cover mark accounting, clearing marks, duplicate marks, filtering pinned/locked blocks, and projected availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirEvictorView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirView.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirView.java

Purpose: Abstract restricted view over a `StorageDir` shared by allocator and evictor views.

Important APIs: Abstract `getAvailableBytes`; getters for reserved, index, capacity, committed bytes, parent tier view, medium, and location; `createTempBlockMeta`.

Control flow: Subclasses decide availability semantics, while common methods delegate to the underlying directory. `createTempBlockMeta` creates metadata without inserting it into the directory.

State and persistence: Holds references to underlying dir and tier view. No independent persistence.

Dependencies and integration: Base for `StorageDirAllocatorView` and `StorageDirEvictorView`.

Risks and test signals: Exposes temp metadata creation even to view users, so callers must still add metadata through store paths. Tests should cover location construction and subclass availability differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierAllocatorView.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierAllocatorView.java

Purpose: Allocator-facing tier view that wraps each underlying storage directory with an allocator view.

Important APIs: Constructor taking `StorageTier` and `useReservedSpace`.

Control flow: Construction iterates the tier's storage dirs, creates `StorageDirAllocatorView` for each, and stores them by directory index.

State and persistence: View over live tier state; no persistence.

Dependencies and integration: Used by block metadata allocator views passed to `Allocator` implementations.

Risks and test signals: The view captures the directory set at construction and may not reflect later lost-storage changes. Tests should cover reserved-space flag propagation and directory indexing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierAllocatorView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierEvictorView.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierEvictorView.java

Purpose: Evictor-facing tier view that wraps each directory with a `StorageDirEvictorView` tied to a block metadata evictor view.

Important APIs: Constructor and `getBlockMetadataEvictorView`.

Control flow: Construction creates one evictor dir view per underlying storage dir and stores it by index.

State and persistence: View state only, plus reference to the owning evictor view. No persistence.

Dependencies and integration: Used by `BlockMetadataEvictorView`, deprecated evictors, and management planners.

Risks and test signals: Like allocator tier views, it snapshots the directory set. Tests should cover evictor-view reference preservation and directory wrapper creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierEvictorView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierView.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierView.java

Purpose: Abstract restricted view over a `StorageTier` for allocator and evictor consumers.

Important APIs: Constructors with optional reserved-space mode; `getDirViews`, `getDirView`, `getTierViewAlias`, and `getTierViewOrdinal`.

Control flow: Subclasses populate the protected `mDirViews` map with appropriate directory view types.

State and persistence: Holds underlying tier reference, directory-view map, and reserved-space flag. No independent persistence.

Dependencies and integration: Base class for `StorageTierAllocatorView` and `StorageTierEvictorView`.

Risks and test signals: `getDirViews` exposes the mutable values collection of the map. Tests should cover alias/ordinal delegation and directory retrieval by index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/UnderFileSystemBlockMeta.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/UnderFileSystemBlockMeta.java

Purpose: Immutable metadata for a block read directly from an under filesystem.

Important APIs: Constructor from session ID, block ID, and `Protocol.OpenUfsBlockOptions`; getters for session, block ID, UFS path, file offset, block size, mount ID, no-cache flag, and user.

Control flow: The constructor copies all relevant fields from the proto options, after which read paths can use the metadata without depending on the mutable request object.

State and persistence: Immutable in-memory state only. It references UFS path and mount IDs but does not persist data.

Dependencies and integration: Used by UFS block read paths and UFS input stream management.

Risks and test signals: The Javadoc contains a garbled proto class reference, but runtime uses `Protocol.OpenUfsBlockOptions`. Tests should cover field copying, no-cache behavior downstream, and offset/size boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/UnderFileSystemBlockMeta.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/AcceptingReviewer.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/AcceptingReviewer.java

Purpose: Reviewer implementation that disables review rejection by accepting every proposed allocation.

Important APIs: `acceptAllocation` always returns true.

Control flow: Allocators call this after finding candidate dirs when review is not skipped.

State and persistence: Stateless.

Dependencies and integration: Implements `Reviewer`; can be selected via `WORKER_REVIEWER_CLASS`.

Risks and test signals: No behavior risk besides disabling buffer protection. Tests should verify it accepts dirs regardless of capacity state supplied by the allocator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/AcceptingReviewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/ProbabilisticBufferReviewer.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/ProbabilisticBufferReviewer.java

Purpose: Reviewer that probabilistically rejects allocations as a directory approaches configured hard and soft free-space limits, preserving expansion buffer.

Important APIs: Constructor reads hard and soft byte limits; package-visible `getProbability`; `acceptAllocation` compares probability to `ThreadLocalRandom`.

Control flow: Directories above soft limit are always accepted; at or below hard limit are rejected; between limits a linear probability is calculated from available bytes and capacity.

State and persistence: Stores hard and soft limits in memory. No persistence.

Dependencies and integration: Used by `RoundRobinAllocator` through `Reviewer.Factory` unless skipped. Reads worker reviewer configuration.

Risks and test signals: Randomness makes acceptance nondeterministic; tests should focus on `getProbability` and inject repeated trials only statistically. Validate soft <= hard normalization, boundary probabilities, and allocator retry after rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/ProbabilisticBufferReviewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/Reviewer.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/Reviewer.java

Purpose: Public experimental policy interface for accepting or rejecting allocator placement decisions.

Important APIs: `acceptAllocation(StorageDirView)` and nested `Factory.create()` using `WORKER_REVIEWER_CLASS`.

Control flow: Allocators ask the reviewer after a candidate directory satisfies location and space constraints. False means the allocator should try another candidate.

State and persistence: Interface only; implementations decide local state. No persistence contract.

Dependencies and integration: Used by `Allocator` implementations, especially `RoundRobinAllocator`.

Risks and test signals: Factory reflection errors surface at allocator construction. Tests should cover configured class creation and allocation behavior when reviewer rejects all candidates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/Reviewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/file/FileSystemMasterClient.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/file/FileSystemMasterClient.java

Purpose: Worker-side master client wrapper for file-system-master worker RPCs.

Important APIs: `getRemoteServiceType`, `getServiceName`, `getServiceVersion`, `afterConnect`, `getFileInfo`, `getPinList`, and `getUfsInfo`.

Control flow: After connecting, it creates a blocking gRPC stub. RPC methods use `retryRPC`; `getPinList` applies the configured worker-master periodic RPC deadline.

State and persistence: Holds the blocking stub after connect. No local persistence.

Dependencies and integration: Extends `AbstractMasterClient`; talks to `FileSystemMasterWorkerServiceGrpc`; used by worker components for pin lists, file info, and UFS mount info.

Risks and test signals: Stub is null before connection and refreshed after reconnect. Tests should cover retry wrapper behavior, deadline application for pin list, proto-to-wire conversion for file info, and service identity constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/file/FileSystemMasterClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/AbstractWriteHandler.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/AbstractWriteHandler.java

Purpose: Base gRPC write-stream handler for block or file write implementations, providing serialized request processing, buffering backpressure, error handling, flush, completion, cancellation, and metrics.

Important APIs: `write`, `writeDataMessage`, `onCompleted`, `onCancel`, `onError`, `getLocation`, and abstract hooks `createRequestContext`, `completeRequest`, `cancelRequest`, `cleanupRequest`, `flushRequest`, `writeBuf`, and `getLocationInternal`.

Control flow: Incoming messages acquire a semaphore bounded by `WORKER_NETWORK_WRITER_BUFFER_SIZE_MESSAGES` and run on a `SerializingExecutor`. First message creates the context; command messages flush or delegate to `handleCommand`; chunk messages wrap data in `NioDataBuffer` and call `writeData`. Completion calls subclass completion then sends optional content hash and offset. Errors set context error, run cleanup, and optionally notify the client.

State and persistence: Holds volatile request context, response observer, serializing executor, semaphore, and user info. Subclasses perform actual persistence to block or file storage.

Dependencies and integration: Used by concrete worker gRPC write handlers; integrates with `WriteRequestContext`, metrics counters/meters in the context, `DataBuffer`, gRPC observers, and slow-write logging.

Risks and test signals: `writeDataMessage` bypasses context initialization if called with data before a regular request context exists, relying on caller protocol. The semaphore is released in executor tasks, so executor rejection paths need coverage. Tests should cover offset validation, flush response offset, cancellation cleanup, notify-client flag behavior, buffer release, slow-write logging threshold, and metric increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/AbstractWriteHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockReadHandler.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockReadHandler.java

Purpose: gRPC server-side stream observer for block read requests, including flow control, data-buffer production, optional block promotion, response serialization, metrics, and cleanup.

Important APIs: `onNext`, `onError`, `onCompleted`, `onReady`, `tooManyPendingChunks`, `createRequestContext`, and inner `DataReader` methods `runInternal`, `completeRequest`, `getDataBuffer`, `openBlock`, `replyError`, `replyEof`, and `replyCancel`.

Control flow: The first request creates and validates a `BlockReadRequestContext`, initializes queued and received offsets, and submits a `DataReader`. Later offset-received messages update flow-control state and may restart reading. `DataReader` loops while ready and under in-flight byte limits, opens the block lazily, reads chunk data using PAGE or FILE transfer paths, queues serialized responses, and marks EOF when requested bytes are exhausted or short read occurs. EOF, cancel, or error complete the request and close or abort temp blocks as appropriate.

State and persistence: Holds a volatile read context protected by a `ReentrantLock`, data reader executor, serializing executor, response observer, worker reference, domain-socket flag, pooled-buffer flag, and block-store type. Actual data comes from block files or UFS readers through `DefaultBlockWorker`.

Dependencies and integration: Uses `DefaultBlockWorker`, `BlockReader`, `AllocateOptions`, `DataMessageServerStreamObserver`, Netty buffers, metrics, `BlockReadRequestContext`, and worker network config. Promotion uses the top storage tier alias from `WORKER_STORAGE_TIER_ASSOC`.

Risks and test signals: Context can be null in some error paths, and flow control depends on client offset acknowledgements. Buffer retain/release correctness is critical. Tests should cover invalid request bounds, executor rejection, onReady restart, cancellation before/after reader start, PAGE and FILE buffer paths, pooled and unpooled modes, promote failures, temp block commit/abort behavior, EOF short reads, and metrics decrement on completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockReadHandler.java -->
