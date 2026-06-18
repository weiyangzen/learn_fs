# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Truncate.java

Purpose: implements `-truncate`, reducing files to a requested length and optionally waiting for block recovery.

Important APIs and types: `processOptions()`, `processArguments()`, `processPath()`, and private `waitForRecovery()`. State includes `newLength`, `waitList`, and `waitOpt`.

Control flow: parses optional `-w`, required nonnegative length, and one or more paths. For each file, rejects directories, rejects extending to a larger length, calls `fs.truncate()`, prints immediate success when true, enqueues for recovery when false and `-w`, or prints a warning to wait manually. `waitForRecovery()` polls each file once per second until status length equals `newLength`.

State and persistence: mutates file length through filesystem truncate. Wait list is in-memory.

Dependencies and integration: uses `PathData.refreshStatus()` and `PathIsDirectoryException`.

Risks: wait loop can run indefinitely and ignores interruptions. Truncate semantics depend on filesystem support and block recovery behavior. Re-reading status after truncation can fail if file is removed concurrently.

Test signals: cover invalid lengths, negative length, directory rejection, larger-than-current rejection, immediate truncate, delayed truncate with and without `-w`, wait polling, interruption, and concurrent delete during wait.
