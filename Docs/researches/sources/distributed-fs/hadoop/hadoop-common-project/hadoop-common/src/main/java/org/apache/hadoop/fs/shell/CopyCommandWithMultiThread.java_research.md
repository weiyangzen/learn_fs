# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CopyCommandWithMultiThread.java

Purpose: adds optional bounded thread-pool execution to `CommandWithDestination` file copies for commands such as `cp`, `get`, and `put`.

Important APIs and types: `setThreadCount()`, `setThreadPoolQueueSize()`, visible-for-testing getters, `processArguments()`, `isMultiThreadNecessary()`, and override `copyFileToTarget()`. Internal state is `threadCount`, `threadPoolQueueSize`, and `ThreadPoolExecutor executor`; `DEFAULT_QUEUE_SIZE` is 1024.

Control flow: option parsers call setters. `processArguments()` initializes an executor only when `threadCount > 1` and there are multiple source paths or a single recursable source. It then runs normal destination processing and waits for executor termination. `copyFileToTarget()` either executes synchronously or submits a task that calls the superclass and reports `IOException` through `displayError()`.

State and persistence: executor state exists only during one command run. Persistent effects are inherited copy writes. Queue backpressure uses `ArrayBlockingQueue` and `CallerRunsPolicy`, so traversal threads may perform copies directly when the queue is full.

Dependencies and integration: extends `CommandWithDestination`, uses inherited recursion and target mapping, and wraps only file copy calls. The command traversal and directory creation still occur in the caller thread.

Risks: worker task exceptions are displayed but not rethrown from `waitForCompletion()`, so exit-code behavior depends on `displayError()` side effects and can be subtle. Concurrent copies share command instance fields inherited from `CommandWithDestination`; target `PathData` values are passed per task, but inherited output/error streams and filesystem clients must tolerate concurrency. Interrupted waits call `shutdownNow()` and restore interrupt status.

Test signals: cover invalid/zero/negative thread and queue options, single-file no-thread optimization, recursive directory enabling threads, queue fallback behavior, worker exception exit-code accounting, and interrupted wait handling.
