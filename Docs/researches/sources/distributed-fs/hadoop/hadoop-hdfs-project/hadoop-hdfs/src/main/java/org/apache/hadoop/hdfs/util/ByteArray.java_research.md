<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ByteArray.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ByteArray.java

## Purpose
`ByteArray` wraps a `byte[]` so byte content, not object identity, can be used for equality and hash-based map/set keys.

## APIs and Types
The public API is constructor `ByteArray(byte[])`, `getBytes()`, `hashCode()`, and `equals(Object)`.

## Control Flow
`hashCode` lazily caches `Arrays.hashCode(bytes)` when the cached field is zero. `equals` type-checks and compares with `Arrays.equals`.

## State and Persistence
State is the original mutable byte array reference and cached hash int. There is no copying or persistence.

## Dependencies and Integration
It depends only on `Arrays` and Hadoop audience annotations. It is a lightweight utility for internal byte-key maps.

## Risks
The wrapper is unsafe if the underlying array is mutated after construction or after hash caching; equality and hash code can diverge from map bucket placement. Arrays whose actual hash is zero cause recomputation each call. `getBytes` exposes the mutable reference.

## Test Signals
Tests should cover equal-content arrays, different content, non-`ByteArray` comparison, hash caching behavior, and mutation-after-insertion hazards documented by failing/expected behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ByteArray.java -->
