<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/AsyncDataService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/AsyncDataService.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/AsyncDataService.java` provides the asynchronous data-operation executor used by the NFSv3 gateway, currently for write-back tasks. The source was read as a complete 141-line file for this report.

## Important APIs, Types, and Functions

`AsyncDataService` owns a `ThreadPoolExecutor` with one core thread, four max threads, 60-second keepalive, a `LinkedBlockingQueue`, and `SubjectInheritingThread` factory. Package-private methods include `execute`, `shutdown`, and `writeAsync`. Nested `WriteBackTask` wraps an `OpenFileCtx` and calls `executeWriteBack()`.

## Control Flow

`writeAsync` creates a `WriteBackTask` and schedules it through synchronized `execute`. Worker threads run `OpenFileCtx.executeWriteBack()` and log any thrown `Throwable` so the executor thread survives.

## State and Persistence Behavior

Executor and thread group state are process-local. Durable effects are HDFS writes performed by `OpenFileCtx`, not by the executor itself.

## Dependencies and Integration Points

It integrates Java concurrency utilities, Hadoop `SubjectInheritingThread` for security context propagation, and NFS write-management classes.

## Risks and Edge Cases

The unbounded queue can accumulate work, `shutdown` does not await termination despite the comment, and callers must ensure only one write-back task per file is queued or executing.

## Test Signals

Write-path tests in `TestWrites`, out-of-order write tests, executor shutdown tests, and failure-injection tests around `OpenFileCtx.executeWriteBack()` validate this component.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/AsyncDataService.java -->
