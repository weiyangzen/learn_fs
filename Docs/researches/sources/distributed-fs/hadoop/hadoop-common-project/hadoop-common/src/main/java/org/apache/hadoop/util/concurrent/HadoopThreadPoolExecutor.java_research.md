# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/HadoopThreadPoolExecutor.java

Purpose: `HadoopThreadPoolExecutor` extends `ThreadPoolExecutor` to add debug execution logging and reliable task exception logging.

Important APIs/types/functions: constructors mirror superclass variants for queue, thread factory, and rejected execution handler. `beforeExecute` logs debug context. `afterExecute` delegates to superclass and then `ExecutorHelper.logThrowableFromAfterExecute`.

Control flow: normal `ThreadPoolExecutor` scheduling and lifecycle are unchanged; hooks only observe and log.

State and persistence behavior: all runtime state is inherited; this class adds only static logging.

Dependencies and integration points: created by `HadoopExecutors` cached/fixed factory methods.

Risks: final class cannot be subclassed for additional behavior. Logging uncaught task exceptions does not retry or propagate to submitters beyond normal `Future` semantics. Queue/thread limits come from caller/factory choices.

Test signals: tests should submit failing execute and submit tasks and assert exception extraction/logging, plus verify custom factories/handlers are honored.
