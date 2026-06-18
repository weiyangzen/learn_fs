<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/MockNameNodeResourceChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/MockNameNodeResourceChecker.java

Purpose: test double for `NameNodeResourceChecker` that lets tests force NameNode resource availability or exhaustion without depending on real disk state.

Important APIs/types/functions: constructor delegates to the real checker with `Configuration`; `hasAvailableDiskSpace()` returns a volatile flag; `setResourcesAvailable(boolean)` mutates the flag.

Control flow: consumers call the checker through the normal NameNode resource-monitor path. Tests flip the flag to simulate low-resource safe mode or recovery, and subsequent calls observe the new value immediately because the flag is volatile.

State and persistence: state is only the in-memory `hasResourcesAvailable` flag. It does not inspect or persist disk usage.

Dependencies and integration points: extends the production `NameNodeResourceChecker`, so it can be injected wherever the NameNode expects the real resource checker.

Risks and test signals: it bypasses real volume checks and only models a single aggregate condition. Test signal is NameNode behavior changing when `setResourcesAvailable(false/true)` is called.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/MockNameNodeResourceChecker.java -->
