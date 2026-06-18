<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/RunnableCallable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/RunnableCallable.java

## Purpose
`RunnableCallable` adapts either a `Runnable` or a `Callable<?>` so it can be scheduled or invoked through either Java concurrency interface.

## Important APIs, Types, And Functions
The class implements `Callable<Void>` and `Runnable`. It has two constructors, one accepting a non-null `Runnable` and one accepting a non-null `Callable<?>`, validated by `Check.notNull`. `call()` invokes the wrapped runnable or callable and always returns null. `run()` invokes the runnable directly or calls the callable and wraps checked exceptions in `RuntimeException`. `toString()` returns the wrapped class simple name.

## Control Flow
`SchedulerService.schedule(Runnable, ...)` wraps a runnable in `RunnableCallable`, then treats it as a callable for instrumentation and fixed-delay scheduling.

## State And Persistence
Each instance stores exactly one delegate. There is no persistence or shared state.

## Dependencies And Integration Points
It depends on `java.util.concurrent.Callable` and Hadoop `Check`. It bridges the scheduler service API overloads.

## Risks
Exceptions from callable execution are preserved in `call()` but wrapped in `run()`, so callers may see different exception types depending on invocation path. `toString()` assumes a delegate exists, which constructors enforce.

## Test Signals
Tests should verify runnable and callable invocation, null rejection, checked exception wrapping in `run`, checked exception propagation in `call`, and `toString` delegate naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/RunnableCallable.java -->
