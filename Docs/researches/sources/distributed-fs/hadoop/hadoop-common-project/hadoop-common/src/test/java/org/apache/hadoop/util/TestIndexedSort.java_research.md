# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIndexedSort.java

Purpose: exercises Hadoop `IndexedSorter` implementations (`QuickSort` and `HeapSort`) over integer and Hadoop `Writable`-encoded records.

Important APIs and types: `IndexedSorter.sort`, `IndexedSortable.compare/swap`, `QuickSort`, `HeapSort`, `WritableComparator`, `Text`, `DataOutputBuffer`, and `DataInputBuffer`. Helper sortables include `SampleSortable`, `MeasuredSortable`, and `WritableSortable`.

Control flow: common helpers run random, single-record, sequential, already sorted, all-equal, and writable-string sort cases. `testQuickSort` also constructs a median-of-three degenerate pattern and wraps it in `MeasuredSortable` to assert comparison count stays below an expected worst-case bound. `testHeapSort` runs the common battery without the quicksort-specific degeneration check.

State and persistence: sort state is represented by index arrays rather than moving source values. Writable state is a packed byte buffer plus offsets; sorted output rehydrates `Text` instances after index swaps.

Dependencies and integration points: validates sorters used by Hadoop components that sort external record indexes without copying payloads. It also verifies compatibility with Hadoop's binary writable comparator semantics.

Risks: off-by-one ranges, unstable index indirection, bad comparator length calculations, quicksort degeneration, or swap mistakes can silently corrupt ordered streams. Test signals compare sorted projections with Java `Arrays.sort` baselines and fail fast on excessive comparisons/swaps.
