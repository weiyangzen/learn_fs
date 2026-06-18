# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolEntry.java

## Purpose
`CachePoolEntry` pairs cache pool configuration with runtime cache pool statistics for list responses.

## Important APIs, types, and functions
The constructor stores `CachePoolInfo` and `CachePoolStats`. Getters expose both.

## Control flow
There is no behavior beyond construction and getters.

## State and persistence behavior
State is two final references. No local persistence occurs.

## Dependencies and integration points
It is public/evolving and used by `CachePoolIterator` and NameNode cache pool listing RPCs.

## Risks and test signals
Tests should verify info/stats preservation and caller behavior if either reference is null. Invariants between pool limits and over-limit stats are enforced elsewhere.
