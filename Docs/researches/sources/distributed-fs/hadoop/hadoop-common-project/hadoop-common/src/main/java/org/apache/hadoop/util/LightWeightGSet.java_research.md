# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightGSet.java

## Purpose

`LightWeightGSet` is a low-memory hash set with key-based retrieval. Elements store their own singly linked collision pointer through `LinkedElement`, avoiding wrapper node allocations.

## Important APIs, Types, And Functions

`LinkedElement` declares `setNext()` and `getNext()`. Main APIs implement `GSet`: `get()`, `contains()`, `put()`, `remove()`, `values()`, `iterator()`, `clear()`, plus diagnostics `toString()` and `printDetails()`. Static helpers include `actualArrayLength()` and `computeCapacity()`. `SetIterator` is fail-fast unless tracking is disabled.

## Control Flow, State, And Persistence

The constructor rounds the backing array size to a power of two and computes `hash_mask`. `put()` validates element/link type, removes any equal existing element, and inserts at the bucket head. `remove()` unlinks from the bucket chain and clears the element next pointer. Iteration walks buckets and chains while checking a modification counter. State is in-memory bucket array, size, modification count, and cached values view.

## Dependencies And Integration Points

It depends on `GSet`, Hadoop `HadoopIllegalArgumentException`, `StringUtils`, `Preconditions` indirectly through callers, and runtime memory sizing. HDFS metadata structures use it where entry count is high and allocation overhead matters.

## Risks And Test Signals

Elements must implement `LinkedElement` correctly and cannot belong to two `LightWeightGSet` chains using the same next field. The class is not thread-safe. Tests should cover replacement, null rejection, bad element type, collision chains, iterator fail-fast/remove, clear, capacity rounding, and memory-percentage capacity math.
