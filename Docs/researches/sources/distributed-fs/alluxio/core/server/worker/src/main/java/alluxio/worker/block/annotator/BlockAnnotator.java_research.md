# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockAnnotator.java

Purpose: Defines the policy interface for assigning sortable metadata to blocks so eviction and tier management can rank blocks without depending directly on a specific algorithm.

Important APIs: `Factory.create()` instantiates the configured class from `PropertyKey.WORKER_BLOCK_ANNOTATOR_CLASS`; `updateSortedField` updates one block at the current logical time; `updateSortedFields` updates a batch for offline schemes; `isOnlineSorter` tells iterators whether lazy full-order refresh is needed.

Control flow: Implementations are called from block-store event listeners during access, commit, move, or lazy iterator creation. Online algorithms update per event, while offline algorithms can refresh a list before iteration.

State and persistence: The interface persists no state itself. Implementations such as LRU and LRFU keep logical clocks and score values in memory only.

Dependencies and integration: Uses `BlockSortedField` and `Pair<Long,T>`, plus Alluxio configuration and reflection utilities. `DefaultBlockIterator` is the primary consumer.

Risks and test signals: Generic type safety is weak because callers often use raw `BlockAnnotator`. Tests should verify configured class construction, online/offline behavior, and batch update semantics for algorithms used by tier management.
