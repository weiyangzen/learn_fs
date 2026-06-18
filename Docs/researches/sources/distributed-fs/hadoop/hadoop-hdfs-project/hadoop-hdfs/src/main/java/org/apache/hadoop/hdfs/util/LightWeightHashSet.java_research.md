<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightHashSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightHashSet.java

## Purpose
`LightWeightHashSet` is a memory-conscious non-thread-safe hash set backed by a power-of-two bucket array and singly linked collision chains. It disallows null elements and supports polling/removing batches.

## APIs and Types
It implements `Collection<T>`. Public APIs include constructors with capacity/load factors, `size`, `isEmpty`, `getCapacity`, `contains`, `getElement`, `add`, `addAll`, `remove`, `pollN`, `pollAll`, `pollToArray`, `iterator`, `clear`, `toArray`, `containsAll`, `removeAll`, and diagnostics. `LinkedElement<T>` stores element, next pointer, and cached hash.

## Control Flow
Adds validate non-null, compute bucket index by `hash & mask`, reject duplicates by hash/equality scan, prepend a linked element, increment size/modification, and resize if above threshold. Removes unlink matching bucket entries and shrink if below threshold. Poll methods remove arbitrary bucket-order elements. Iterators scan buckets and are fail-fast using a modification epoch, with iterator `remove` supported.

## State and Persistence
State includes bucket array, capacity, hash mask, initial capacity, size, load factors, thresholds, and modification count. Resize rehashes existing linked elements into a new bucket array. No persistence or synchronization.

## Dependencies and Integration
It depends on Java collections and SLF4J. `LightWeightLinkedSet` extends it to preserve insertion order.

## Risks
Not thread-safe. `contains(Object)` casts unchecked to `T`; incompatible key types can throw `ClassCastException`. `toArray(T[])` does not null-terminate when the supplied array is larger than size, diverging from the `Collection` contract. Poll loops assume internal size/capacity consistency. Poor hash distribution degrades to bucket scans.

## Test Signals
Tests should cover load-factor expansion/shrink, duplicate add, null rejection, contains/getElement, arbitrary poll counts including zero/all, iterator fail-fast and remove, clear resets capacity, `toArray` contract including oversized arrays, and collision-heavy elements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightHashSet.java -->
