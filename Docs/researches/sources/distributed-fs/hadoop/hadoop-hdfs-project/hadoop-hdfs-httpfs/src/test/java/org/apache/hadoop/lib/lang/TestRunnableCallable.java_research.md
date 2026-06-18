# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/lang/TestRunnableCallable.java

Purpose: Unit tests for `RunnableCallable`, an adapter that exposes a `Runnable` as a `Callable` and a `Callable` as a `Runnable`.

Important APIs/types/functions: nested `R`, `C`, and `CEx` fixtures; tests `runnable`, `callable`, and `callableExRun`; adapter methods `run`, `call`, and `toString`.

Control flow: each positive test constructs a fixture, wraps it, invokes both adapter entry points, and checks the fixture side-effect flag. The exception test wraps a callable that throws and asserts `run()` converts the checked exception into `RuntimeException`.

State and persistence: only in-memory boolean flags; no external persistence.

Dependencies/integration: extends `HTestCase` and uses JUnit assertions. It verifies utility behavior used by scheduler/executor-style services.

Risks and test signals: narrow but useful signal for exception bridging and display names. It uses raw `Callable`, so generic type-safety is not covered.
