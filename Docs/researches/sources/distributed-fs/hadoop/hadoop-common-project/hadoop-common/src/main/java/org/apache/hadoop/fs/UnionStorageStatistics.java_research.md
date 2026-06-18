# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnionStorageStatistics.java

## Purpose
Combines multiple StorageStatistics instances behind one StorageStatistics view. It exposes a union iterator, first-match getLong lookup, aggregate isTracked lookup, and reset fan-out across delegates.

## Important APIs, Types, and Functions
UnionStorageStatistics extends StorageStatistics; LongStatisticIterator walks each delegate getLongStatistics(); getLong(), isTracked(), reset().

## Control Flow
Construction validates name, array, and elements. Iteration advances delegate iterators lazily; lookups scan delegates in order and return the first non-null value.

## State and Persistence Behavior
Holds only references to delegate statistics. reset mutates every delegate counter set; there is no persistence except the delegates statistics state.

## Dependencies and Integration Points
Depends on StorageStatistics and Preconditions. Used where one filesystem wants one statistics object spanning multiple internal stores.

## Risks and Test Signals
Iterator boundary logic and delegate ordering are the main risks. Test empty/single/multiple delegates, duplicate keys, reset propagation, and iterator exhaustion.
