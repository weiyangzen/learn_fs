# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IndexedSorter.java

## Purpose

`IndexedSorter` is the algorithm interface for sorting an `IndexedSortable` over a half-open index range.

## Important APIs, Types, And Functions

It declares `sort(IndexedSortable s, int l, int r)` and `sort(IndexedSortable s, int l, int r, Progressable rep)`. The second form reports progress during long sorts.

## Control Flow, State, And Persistence

The interface has no state. Implementations such as `HeapSort` use only `compare()` and `swap()` to reorder the range `[l, r)`.

## Dependencies And Integration Points

It depends on `IndexedSortable` and `Progressable`, and is limited-private to MapReduce. It integrates with sort buffers where record data is not exposed as an object list.

## Risks And Test Signals

Implementations must respect range boundaries and progress callback expectations. Tests should check empty ranges, subranges, progress reporting, and no swaps outside `[l, r)`.
