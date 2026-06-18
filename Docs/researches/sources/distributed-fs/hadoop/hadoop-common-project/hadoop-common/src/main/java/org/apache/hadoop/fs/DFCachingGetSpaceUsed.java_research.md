## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DFCachingGetSpaceUsed.java

Purpose: `DFCachingGetSpaceUsed` is a fast but approximate `CachingGetSpaceUsed` implementation. It assumes the whole mount belongs to HDFS and that no two HDFS data directories share the same disk, then reports used space from `DF`.

Important APIs and types: the constructor accepts a `CachingGetSpaceUsed.Builder`, initializes the superclass, and creates a `DF` with the builder path and interval. The only behavior override is `refresh()`, which assigns `used` from `df.getUsed()`.

Control flow, state, and persistence: all caching, threading, interval, jitter, and `used` state are inherited from `CachingGetSpaceUsed`. This class only refreshes the inherited atomic usage value. It does not persist usage estimates.

Dependencies and integration: it is selected through `fs.getspaceused.classname` configuration and integrates local disk accounting with HDFS/MapReduce callers that prefer a cheap mount-wide estimate over recursive `du`.

Risks and test signals: the core risk is semantic inaccuracy when other data shares the volume or multiple data dirs share a disk. Tests should use mocked or temporary `DF` behavior where possible and verify that builder interval/path are honored, refresh updates inherited state, and the class behaves acceptably when `DF` construction or access fails in the environment.
