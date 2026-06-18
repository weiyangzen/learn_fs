## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CachingGetSpaceUsed.java

Purpose: abstract base for disk-space-used estimators that cache usage and optionally refresh it in a background daemon thread.

Important APIs and types: implements `Closeable` and `GetSpaceUsed`; holds `AtomicLong used`, `AtomicBoolean running`, refresh interval, jitter, canonical directory path, and refresh thread. Subclasses implement `refresh()`. Public helpers include `getUsed`, `getDirPath`, `incDfsUsed`, `getRefreshInterval`, `getJitter`, and protected `setUsed`.

Control flow: construction canonicalizes the target path and seeds `used`. `init()` performs an immediate refresh when initial used is negative and first refresh is enabled, otherwise starts a `SubjectInheritingThread` if interval is positive. The refresh thread sleeps for interval plus random jitter, clamps to at least one millisecond, then invokes `refresh()` until `running` is false. `close()` flips running false and interrupts the thread.

State and persistence behavior: cached usage lives in memory and can be adjusted optimistically by `incDfsUsed`. Actual persistence is external filesystem state measured by subclass `refresh()`.

Dependencies and integration points: used by HDFS/MapReduce storage accounting; builder values come from `GetSpaceUsed` construction paths and common filesystem space-used configuration keys.

Risks: `refresh()` exceptions other than `InterruptedException` are not caught inside the loop, so subclass runtime exceptions can kill the background thread. Jitter uses `nextLong(-jitter, jitter)`, excluding the positive upper bound. `close()` does not join the thread, so immediate post-close assertions can race.

Test signals: cover initial negative usage behavior, interval zero disabling the thread, jitter bounds, `incDfsUsed`, non-negative `getUsed`, close/interrupt behavior, subject inheritance, and subclass refresh failure handling.
