# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/QuickSort.java

## Purpose
`QuickSort` implements Hadoop's indexed introspective quicksort for `IndexedSortable` collections, with insertion sort for tiny ranges and heapsort fallback for deep recursion.

## Important APIs, Types, And Functions
It implements `IndexedSorter`. Public APIs are `sort(IndexedSortable,int,int)` and `sort(IndexedSortable,int,int,Progressable)`. Important helpers are `getMaxDepth`, `fix`, and `sortInternal`. A static `HeapSort` instance is the fallback sorter.

## Control Flow
Sorting reports progress once per `sortInternal` entry when a reporter is supplied. Ranges shorter than 13 are insertion-sorted. Larger ranges use median-of-three pivot setup, three-way partitioning that groups values equal to the pivot at both ends, and recursion on the smaller side first while iterating on the larger side to limit stack depth. If depth drops below zero, heapsort handles the range.

## State And Persistence
The sorter has no per-sort mutable state outside the call stack. It mutates the caller's indexed collection through `swap`.

## Dependencies And Integration Points
It depends on `IndexedSorter`, `IndexedSortable`, `HeapSort`, `Progressable`, and Hadoop annotations. It is useful for sortable views where copying into arrays is undesirable.

## Risks
Comparator consistency is mandatory. `getMaxDepth` rejects nonpositive ranges; callers passing equal bounds into `sort` can trigger an exception. Progress callbacks inside sorting can introduce latency or reentrancy concerns.

## Test Signals
Tests should cover empty/single ranges, duplicate-heavy data, already sorted and reverse data, fallback triggering through adversarial comparators, progress callback invocation, and sort correctness over custom indexed containers.
