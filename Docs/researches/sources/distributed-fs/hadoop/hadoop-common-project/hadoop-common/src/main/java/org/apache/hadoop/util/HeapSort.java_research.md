# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/HeapSort.java

## Purpose

`HeapSort` implements `IndexedSorter` using an in-place heap sort over an `IndexedSortable` index range. It is intended for MapReduce-style sort paths where data is manipulated through compare/swap callbacks.

## Important APIs, Types, And Functions

Public methods are `sort(IndexedSortable s, int p, int r)` and `sort(IndexedSortable s, int p, int r, Progressable rep)`. Internal helpers build and pop the heap using callback comparisons and swaps; the progress-aware overload periodically invokes `rep.progress()`.

## Control Flow, State, And Persistence

The algorithm builds a max heap over `[p, r)`, repeatedly swaps the root with the end, reduces heap size, and heapifies. It keeps no object state and persists nothing.

## Dependencies And Integration Points

It depends on `IndexedSorter`, `IndexedSortable`, and `Progressable`. It integrates with Hadoop sort buffers whose records are addressed indirectly rather than as Java objects.

## Risks And Test Signals

Heap sort is not stable. Bugs in range math can corrupt adjacent records because swaps are callback-driven. Tests should sort empty, singleton, already-sorted, reverse, duplicate-key, and subrange inputs, and verify progress callbacks do not change ordering.
