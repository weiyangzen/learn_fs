# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/HadoopExecutors.java

Purpose: `HadoopExecutors` is a factory class for Hadoop executor services that add task exception logging, plus a bounded shutdown helper.

Important APIs/types/functions: factory methods create cached, fixed, scheduled, single-thread, and single-thread scheduled executors. Hadoop variants return `HadoopThreadPoolExecutor` or `HadoopScheduledThreadPoolExecutor`; single-thread variants delegate to JDK `Executors` to preserve exact wrapper semantics. `shutdown(ExecutorService, Logger, long, TimeUnit)` performs graceful then forced shutdown.

Control flow: factory methods mirror JDK executor parameters. Shutdown returns for null, calls `shutdown`, waits once, calls `shutdownNow` if needed, waits a second time, logs success or error, handles interruption by logging and forcing shutdown, and rethrows unexpected exceptions.

State and persistence behavior: no class state. Created executor instances own runtime queues and threads.

Dependencies and integration points: depends on Java concurrent executors and SLF4J logger supplied by callers. Used wherever Hadoop wants standard executor construction with better exception logging.

Risks: fixed thread pools use unbounded `LinkedBlockingQueue`, which can grow without backpressure. Cached pools can create unbounded threads like JDK cached pools. Shutdown does not restore interrupt status after catching `InterruptedException`. Log message spelling has a minor typo but no behavioral impact.

Test signals: tests should verify factory types, exception logging via subclasses, shutdown graceful/forced paths, null shutdown no-op, and interruption handling.
