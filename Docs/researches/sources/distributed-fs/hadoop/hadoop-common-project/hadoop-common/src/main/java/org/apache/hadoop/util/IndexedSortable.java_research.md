# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IndexedSortable.java

## Purpose

`IndexedSortable` abstracts a collection whose items can be compared and swapped by integer index, allowing sort algorithms to operate without knowing the underlying storage layout.

## Important APIs, Types, And Functions

It declares `compare(int i, int j)` with `Comparator`-style semantics and `swap(int i, int j)`.

## Control Flow, State, And Persistence

The interface has no state. Implementations own the indexed data and must keep compare/swap consistent across the sorted range.

## Dependencies And Integration Points

It is limited-private to MapReduce and pairs with `IndexedSorter`, `HeapSort`, and other sort algorithms in Hadoop's spill/sort code.

## Risks And Test Signals

Bad compare consistency or swap implementation corrupts sorter behavior. Tests should validate sorter algorithms against implementations with duplicate keys, equal records, and side-effect-sensitive storage.
