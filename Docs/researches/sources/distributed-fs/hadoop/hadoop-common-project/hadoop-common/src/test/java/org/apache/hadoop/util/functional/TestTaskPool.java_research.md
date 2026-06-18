# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/functional/TestTaskPool.java

Purpose: Parameterized tests for Hadoop `TaskPool`, covering sequential and executor-backed execution with failure handling, suppression, stop-on-failure, abort, revert, and failure callbacks. The file was pulled from S3A-style task pool tests.

Important APIs/types/functions: Tests use `TaskPool.foreach(items).executeWith(submitter)` and builder options `suppressExceptions()`, `stopOnFailure()`, `abortWith()`, `revertWith()`, `onFailure()`, and `stopAbortsOnFailure()`. `PoolSubmitter` adapts `ExecutorService` to `TaskPool.Submitter`. Fixtures `Item`, `BaseCounter`, `CounterTask`, and `FailureCounter` track committed/aborted/reverted/failed state and controlled IO failures.

Control flow: Parameter source runs each test with thread counts `0`, `1`, `3`, `8`, and `16`; zero threads means direct execution with no submitter. Setup creates 16 items and, for positive thread counts, a daemon fixed pool. Simple invocation commits all items. Failure tests use a task that throws on invocation `8` and vary builder policy: continue through failures, stop fast, abort uncommitted work, revert committed work, suppress or propagate exceptions, and stop aborts on abort failure. Parallel tests use at-least assertions where concurrency can schedule extra work after a failure.

State and persistence behavior: Each test recreates `items`, counters, and optionally an executor. Item flags are volatile because parallel worker threads mutate them. Teardown shuts down the thread pool but does not await termination; tests rely on `TaskPool.run()` to complete submitted work before returning or throwing.

Dependencies and integration points: Depends on Hadoop `TaskPool`, Guava-shaded `ThreadFactoryBuilder`, Java executors/futures/streams, JUnit parameterized tests, SLF4J, and Hadoop test helpers. TaskPool is a reusable utility for batch operations that need rollback/abort behavior.

Risks: Parallel scheduling makes exact invocation counts brittle; the test accounts for this with `isParallel()` branches. Failure callback stores only the last item/exception and is not deeply asserted beyond count in most cases. Shutdown without await could leave lingering threads if a regression returns before work settles.

Test signals: Boolean run success/failure, propagated `IOException` when suppression is absent, invocation counts or minimum counts, item state invariants for committed/failed/aborted/reverted work, and single failure callback invocation are the core signals.
