# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MultithreadedTestUtil.java

Purpose: utility framework for stress-testing threaded or synchronized code with coordinated test threads and deferred exception propagation.

Important APIs/types/functions: `TestContext`, `TestingThread`, and `RepeatingTestThread`, plus methods `addThread`, `startThreads`, `waitFor`, `stop`, `threadFailed`, `threadDone`, `shouldRun`, `doWork`, and `doAnAction`.

Control flow: tests create a `TestContext`, add `TestingThread` instances, start all threads, and wait or stop. Each `TestingThread` runs `doWork` inside `work`, reports thrown errors to the context, and signals completion. Repeating threads loop `doAnAction` while the context should run and the thread is not stopped.

State and persistence behavior: context maintains in-memory stopped flag, first error, all threads, and finished threads. No persistence.

Dependencies and integration points: threads extend `SubjectInheritingThread`, preserving Hadoop subject/security context. Uses Hadoop `Time` for deadlines and SLF4J logging.

Risks and test signals: errors are deferred to the coordinator, so failing worker threads become test failures. Risks include tests that forget to stop repeating threads or rely on coarse timeout behavior.
