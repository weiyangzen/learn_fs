# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/SortedBlockSet.java

Purpose: Concurrent sorted collection mapping block IDs to annotator fields while preserving deterministic identity for duplicate sort values.

Important APIs: `getSortField`, `put`, `remove`, `size`, `getAscendingIterator`, and `getDescendingIterator`. The inner `SortedBlockSetEntry` compares by sorted field and then change index.

Control flow: `put` uses `ConcurrentHashMap.compute` per block ID to remove the old entry, assign a new change index, insert a new entry, and update the last-sort map. Iterators transform sorted-set entries into block ID and field pairs.

State and persistence: Holds a `ConcurrentSkipListSet`, a concurrent block-to-change-index/field map, and an atomic change index. All state is in memory.

Dependencies and integration: Used by `DefaultBlockIterator` per directory. Depends on Alluxio `Pair`, Guava `Iterators`, and Java concurrent collections.

Risks and test signals: Removal logs a warning when a block is absent; duplicate fields depend on change index uniqueness. Tests should cover update replacement, concurrent per-block updates, iterator ordering, duplicate sorted fields, and remove-after-move behavior.
