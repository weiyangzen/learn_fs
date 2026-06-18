# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveStats.java

## Purpose
`CacheDirectiveStats` reports runtime cache progress for a single cache directive.

## Important APIs, types, and functions
The nested `Builder` sets bytes needed, bytes cached, files needed, files cached, and expired flag, then builds an immutable stats object. Getters expose all values. `toString` formats the counters and expiration state.

## Control flow
There is no behavior beyond builder chaining, construction, getters, and formatting.

## State and persistence behavior
State is final counter values and `hasExpired`. No local persistence occurs.

## Dependencies and integration points
It is public/evolving and paired with `CacheDirectiveInfo` inside `CacheDirectiveEntry` for cache directive list/status APIs.

## Risks and test signals
Tests should cover builder defaults of zero/false, all setters, string output, and large counter values. The builder does not reject negative values, so validation must occur upstream if needed.
