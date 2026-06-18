# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockSortedField.java

Purpose: Marker-style public API for values that can sort blocks for eviction and management decisions.

Important APIs: Extends `Comparable<BlockSortedField>` and has no methods of its own.

Control flow: Annotators produce these fields, `SortedBlockSet` stores them, and `DefaultBlockIterator` compares them through `BlockOrder`.

State and persistence: Interface only. Concrete field values are in-memory ranking metadata.

Dependencies and integration: Implemented by `LRUAnnotator.LRUSortedField` and `LRFUAnnotator.LRFUSortedField`.

Risks and test signals: Implementations must keep `compareTo`, `equals`, and `hashCode` coherent enough for sorted sets. Tests should include equal score collisions and mixed-type rejection.
