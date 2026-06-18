<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReadOnlyList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReadOnlyList.java

## Purpose
`ReadOnlyList` defines a minimal unmodifiable indexed iterable and utilities for binary search and adapting between `ReadOnlyList` and Java `List` views.

## APIs and Types
The interface exposes `isEmpty`, `size`, `get`, and `iterator`. `Util` provides `emptyList`, `binarySearch`, `asReadOnlyList(List)`, and `asList(ReadOnlyList)`.

## Control Flow
`binarySearch` mirrors `Collections.binarySearch` over the read-only interface. `asReadOnlyList` delegates read methods and iterator to the backing list. `asList` returns an anonymous `List` implementing only iteration, emptiness, size, get, `toArray()`, and `toString`; all mutators and many query/list-iterator operations throw `UnsupportedOperationException`.

## State and Persistence
Adapters are live views over backing lists, not snapshots. No persistence or synchronization.

## Dependencies and Integration
It depends on Java collection interfaces and Hadoop annotations. It is useful in HDFS internals that want read-only list exposure without copying.

## Risks
`asReadOnlyList` still exposes the backing list iterator, whose `remove` may mutate if supported. `asList` is only a partial `List` implementation; even harmless queries like `contains` throw. Live views reflect concurrent backing mutations. `toArray(T[])` is unsupported in `asList`.

## Test Signals
Tests should cover binary-search found/insertion cases, empty list, live-view behavior, unsupported operations, iterator mutation behavior for mutable backing lists, and `toString` formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReadOnlyList.java -->
