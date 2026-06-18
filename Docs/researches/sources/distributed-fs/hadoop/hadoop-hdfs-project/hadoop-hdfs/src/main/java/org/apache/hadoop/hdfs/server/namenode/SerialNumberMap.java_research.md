# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SerialNumberMap.java

## Purpose

`SerialNumberMap.java` is a thread-safe bidirectional map from arbitrary objects to compact positive integer serial numbers. The source was read as a complete 112-line file.

## Important APIs, Types, and Functions

The generic class `SerialNumberMap<T>` stores `t2i`, `i2t`, an atomic `current` counter starting at 1, and a maximum derived from bit length. Public APIs are `get(T)`, `get(int)`, `size`, and `toString`; package-visible helpers include `getMax` and `entrySet`.

## Control Flow

`get(T)` returns `0` for null, returns an existing serial if present, or synchronizes to allocate a new serial number, checking overflow and using `putIfAbsent` defensively. `get(int)` returns null for zero and otherwise requires an existing reverse mapping.

## State and Persistence Behavior

The map is in-memory only. Persistence is indirect through `SerialNumberManager.StringTable`, which snapshots `i2t` entries. The reverse map is the authoritative enumeration for size and snapshots.

## Dependencies and Integration Points

It uses Java concurrent maps and atomic counters and is owned primarily by `SerialNumberManager`. It supports compact encodings in NameNode metadata formats.

## Risks and Edge Cases

The maximum is `(1 << bitLength) - 1`, so bit lengths near integer limits must be kept valid by callers. Overflow rolls back the counter and throws. Missing reverse lookups throw `IllegalStateException`, which is appropriate for corrupted or inconsistent metadata but can surface during fsimage load.

## Test Signals

Tests should stress concurrent allocation of the same and different values, null handling, reverse lookup, overflow boundaries, snapshot entry-set immutability, and idempotent serial reuse.
