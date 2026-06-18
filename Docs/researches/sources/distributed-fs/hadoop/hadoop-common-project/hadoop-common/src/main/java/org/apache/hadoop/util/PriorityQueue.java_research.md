# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PriorityQueue.java

## Purpose
`PriorityQueue<T>` is an old Hadoop/Lucene-style abstract min-heap. Subclasses supply ordering through `lessThan`, and the implementation provides constant-time top lookup plus logarithmic insert and pop.

## Important APIs, Types, And Functions
Subclasses call `initialize(int maxSize)` and implement `lessThan(Object,Object)`. Public operations are `put`, `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`. Internal heap maintenance lives in `upHeap` and `downHeap`.

## Control Flow
The heap is one-based: `heap[1]` is the least element. `put` appends and bubbles up. `insert` either appends, replaces the current top when full and the new element is not less than the top, or rejects the element. `pop` swaps in the last element, clears the old slot for GC, and bubbles down. `adjustTop` assumes the top object changed and only repairs downward.

## State And Persistence
Mutable state is the backing array, current size, and max size. There is no synchronization and no persistence. `clear` nulls occupied slots.

## Dependencies And Integration Points
It depends only on Hadoop annotations and Java arrays. Integrations must provide a strict, stable ordering via `lessThan`.

## Risks
Calling `put` beyond `maxSize` throws an array bounds exception. `insert` implements a bounded top-N pattern whose replacement semantics are easy to misuse. Non-transitive comparators can corrupt heap ordering, and concurrent access is unsafe.

## Test Signals
Tests should check heap ordering, bounded insertion behavior, `adjustTop` after mutating top priority, clearing GC slots, max-size overflow, duplicate/equal keys, and null behavior if subclasses allow it.
