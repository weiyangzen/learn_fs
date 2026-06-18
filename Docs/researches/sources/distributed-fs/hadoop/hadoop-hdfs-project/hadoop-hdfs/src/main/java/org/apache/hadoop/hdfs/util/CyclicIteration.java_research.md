<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/CyclicIteration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/CyclicIteration.java

## Purpose
`CyclicIteration` provides an `Iterable` over a `NavigableMap` that starts after a supplied key, wraps to the first entry, and stops after each entry has been returned once.

## APIs and Types
The public API is constructor `(NavigableMap<K,V>, K startingkey)` and `iterator()`. The private `CyclicIterator` implements `Iterator<Map.Entry<K,V>>`.

## Control Flow
Construction stores the map and an exclusive `tailMap(startingkey, false)`, or nulls for empty maps. The iterator starts from the tail iterator, falls back to the full map iterator when the tail is exhausted, remembers the first returned entry, and stops when the next candidate equals that first entry. `remove` is unsupported.

## State and Persistence
State is iterator-local plus references to live map views. No persistence. Iteration reflects the underlying map view behavior and is not explicitly fail-fast beyond the map's own iterators.

## Dependencies and Integration
It depends on Java collections and Hadoop audience/stability annotations. It is suitable for round-robin-style scans over sorted maps.

## Risks
Concurrent map modification follows underlying iterator semantics. If `startingkey` is null, behavior depends on map comparator/null support. Entry equality is used to detect wrap completion, so unusual entry equality implementations may matter.

## Test Signals
Tests should cover empty map, start before first, start at existing key, start between keys, start after last, single-entry map, unsupported remove, and concurrent modification behavior for the chosen map implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/CyclicIteration.java -->
