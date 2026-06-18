# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/MergeSort.java

## Purpose

`MergeSort` implements the core merge-sort algorithm for integer index arrays using a comparator over reusable `IntWritable` wrappers.

## Important APIs, Types, And Functions

The constructor accepts a `Comparator<IntWritable>`. `mergeSort(int[] src, int[] dest, int low, int high)` recursively sorts ranges. Internal `swap()` exchanges destination entries.

## Control Flow, State, And Persistence

For ranges shorter than seven, it uses insertion sort. Larger ranges recursively sort halves from destination to source, skips merging if already ordered, otherwise merges sorted halves back into destination. The instance holds the comparator and two reusable `IntWritable` objects; no persistence.

## Dependencies And Integration Points

It depends on `IntWritable`, `Comparator`, and MapReduce-limited APIs. It is used by sort code that manipulates integer pointer/index arrays rather than records directly.

## Risks And Test Signals

Reusable `IntWritable` fields make instances not thread-safe. Tests should cover stable merge behavior if expected by callers, insertion-sort threshold, already-sorted fast path, duplicate keys, reverse order, subrange sorting, and comparator side effects.
