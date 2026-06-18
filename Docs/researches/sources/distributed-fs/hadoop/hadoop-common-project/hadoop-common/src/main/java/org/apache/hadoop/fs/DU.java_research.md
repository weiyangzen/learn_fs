## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DU.java

Purpose: `DU` is a `CachingGetSpaceUsed` implementation backed by the Unix `du -sk` command. It reports recursive disk usage for a configured path and logs refresh failures instead of surfacing them to periodic callers.

Important APIs and types: the visible-for-testing constructor accepts path, interval, jitter, and initial usage. The public builder constructor extracts those values from `CachingGetSpaceUsed.Builder`. `refresh()` invokes the nested `DUShell`, whose `getExecString()` returns `du -sk <dir>` and whose parser reads the first tab-separated size field.

Control flow, state, and persistence: `CachingGetSpaceUsed` owns cached usage state and scheduling. `DU.refresh()` runs the shell command and sets usage to kilobytes times 1024. Parser errors or command failures are logged as warnings and leave prior cached state intact. There is no durable persistence.

Dependencies and integration: this is the more precise alternative to `DFCachingGetSpaceUsed` for HDFS data directories. It depends on `Shell`, `Configuration`, and the inherited cache machinery.

Risks and test signals: risks include platform dependence, inaccessible paths, `du` output shape, tabs vs spaces, huge values, and stale cached usage after failures. Tests should cover parser behavior, failure logging without state corruption, initial usage, builder wiring, and the `main` path through `GetSpaceUsed.Builder`.
