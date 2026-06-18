# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveEntry.java

## Purpose
`CacheDirectiveEntry` pairs a cache directive's configuration with its runtime statistics for list responses.

## Important APIs, types, and functions
The constructor stores `CacheDirectiveInfo` and `CacheDirectiveStats`. Getters expose both.

## Control flow
There is no behavior beyond construction and getters.

## State and persistence behavior
State is two final references. No local persistence occurs.

## Dependencies and integration points
It is public/evolving and used by `CacheDirectiveIterator` and NameNode cache directive list RPCs.

## Risks and test signals
Tests should verify info/stats preservation and behavior with null values if RPC layers permit them. The object does not enforce invariants between requested directive fields and reported stats.
