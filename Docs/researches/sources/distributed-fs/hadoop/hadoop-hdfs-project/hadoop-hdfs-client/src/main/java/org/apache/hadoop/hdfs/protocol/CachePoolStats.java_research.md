# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolStats.java

## Purpose
`CachePoolStats` reports aggregate cache usage for a cache pool.

## Important APIs, types, and functions
The nested `Builder` sets bytes needed, bytes cached, bytes over limit, files needed, and files cached. `build()` creates the stats object. Getters expose each counter, and `toString` formats all counters.

## Control flow
There is no behavior beyond builder chaining, construction, getters, and formatting.

## State and persistence behavior
State is final aggregate counters. No local persistence occurs.

## Dependencies and integration points
It is public/evolving and paired with `CachePoolInfo` in `CachePoolEntry` for cache pool list/status APIs.

## Risks and test signals
Tests should cover builder defaults, all setter paths, large values, string output, and over-limit reporting. Negative values are not checked here, so producer-side validation is needed.
