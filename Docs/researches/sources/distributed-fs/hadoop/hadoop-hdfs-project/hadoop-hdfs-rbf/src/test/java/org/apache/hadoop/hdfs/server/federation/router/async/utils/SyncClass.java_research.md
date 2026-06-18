# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/SyncClass.java

Purpose: synchronous reference implementation for `BaseClass`, used as the behavioral oracle for `AsyncClass`.

Important APIs/types/functions: implements `BaseClass`; uses `SubjectInheritingThread`, `ExecutorService`, `Executors`, `Future`, `IOException`, and `List`. Core methods include `applyMethod`, `exceptionMethod`, foreach variants, catch/finally variants, `currentMethod`, `timeConsumingMethod`, and private `getExecutorService()`.

Control flow: `timeConsumingMethod()` sleeps or simulates delay and returns bracketed input text. `applyMethod()` prefixes the result and can throw checked/runtime exceptions for inputs 2 and 3. Foreach methods build comma-delimited output, optionally stopping at input 2 or stopping on runtime exception while recording IO exceptions. Chained methods call `applyMethod` and then additional logic. `applyCatchFinallyMethod` clears the provided resource list in a finally block. `currentMethod` submits tasks through a subject-inheriting executor, waits on futures, and aggregates values or exception messages.

State and persistence behavior: state is limited to the configured time-consuming delay and lazily created executor. There is no persistent storage. Dependencies include thread identity/security context inheritance for current-method tests. Risks include executor lifecycle, timing in tests, and exception-message coupling. Test signals are exact string outputs and thrown exception types/messages used by `TestAsyncUtil`.
