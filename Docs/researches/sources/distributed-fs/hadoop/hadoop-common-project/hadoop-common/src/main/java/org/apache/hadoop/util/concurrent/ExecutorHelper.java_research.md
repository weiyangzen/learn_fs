# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/ExecutorHelper.java

Purpose: `ExecutorHelper` provides shared after-execute exception extraction for Hadoop executor subclasses.

Important APIs/types/functions: package-private `logThrowableFromAfterExecute(Runnable, Throwable)` logs debug context, handles JDK behavior where `afterExecute` receives null for failed `Future` tasks, and logs any extracted throwable at warn.

Control flow: if throwable is null and the runnable is a completed `Future`, it calls `get` to surface `ExecutionException`, interruption, or other throwables. Interruptions re-interrupt the current thread. Non-null throwable is logged.

State and persistence behavior: stateless except logging.

Dependencies and integration points: called by `HadoopThreadPoolExecutor` and `HadoopScheduledThreadPoolExecutor`.

Risks: calling `Future.get()` in `afterExecute` is guarded by `isDone`, but custom Future implementations could still behave unexpectedly. Warnings expose task exception details. Package-private scope limits reuse.

Test signals: tests should submit failing `Runnable`/`Callable` tasks to Hadoop executors and verify exceptions are logged and interrupt status is restored after interrupted `get`.
