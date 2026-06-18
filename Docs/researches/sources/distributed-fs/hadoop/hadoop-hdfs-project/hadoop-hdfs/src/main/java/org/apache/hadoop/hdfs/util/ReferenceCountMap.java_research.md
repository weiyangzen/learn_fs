<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReferenceCountMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReferenceCountMap.java

## Purpose
`ReferenceCountMap` deduplicates equal instances while maintaining a reference count on the canonical stored instance.

## APIs and Types
Generic type `E` must implement `ReferenceCounter`, which supplies `getRefCount`, `incrementAndGetRefCount`, and `decrementAndGetRefCount`. Public APIs include `put`, `remove`, `getReferenceCount`, `getUniqueElementsSize`, testing-visible `getEntries`, and `clear`.

## Control Flow
`put` uses `ConcurrentHashMap.putIfAbsent`; if an equivalent entry exists, it increments and returns that canonical value, otherwise increments the new key and returns it. `remove` looks up an equivalent value, decrements it, and removes the map entry when the count reaches zero. `getEntries` snapshots keys into an immutable list.

## State and Persistence
State is a `ConcurrentHashMap<E,E>` plus mutable counters inside values. No persistence. Despite concurrent map use, the class comment says it is not thread-safe because counter operations and remove races are not atomic as a compound operation.

## Dependencies and Integration
It depends on Java concurrent maps, shaded Guava `ImmutableList`, and Hadoop annotations. It is meant for memory deduplication of ref-counted internal objects.

## Risks
Key equality/hash must remain stable while stored. Concurrent put/remove can race counter updates. Removing an absent key is silent. Negative ref counts are possible if `ReferenceCounter` permits them or remove is overcalled.

## Test Signals
Tests should cover canonical instance return, duplicate increments, removal decrement and final map removal, absent removal, key mutation hazards, `getEntries` snapshot, and concurrent race behavior if usage evolves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReferenceCountMap.java -->
