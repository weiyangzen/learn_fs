## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContextDeleteOnExit.java

Purpose: validates `FileContext.deleteOnExit(Path)` registration, global shutdown-hook installation, finalizer execution, and cleanup of registered paths.

Important APIs/types/functions: `FileContext.getLocalFSFileContext`, `FileContext.deleteOnExit`, static `FileContext.DELETE_ON_EXIT`, static `FileContext.FINALIZER`, `ShutdownHookManager`, `FileContextTestHelper`, and `createFile`/`exists` helpers from `FileContextTestHelper`.

Control flow: setup obtains local `FileContext`; teardown deletes the test root. `testDeleteOnExit` creates two files and one nested path, registers each with delete-on-exit, checks that the global map has one context entry containing the expected paths, verifies the shutdown hook exists, then runs `FileContext.FINALIZER` directly and asserts the map is empty and paths are gone.

State and persistence: creates local files under the FileContext test root and mutates static global delete-on-exit state. Direct finalizer invocation resets that state for the tested context.

Dependencies/integration points: integrates FileContext with Hadoop's `ShutdownHookManager`, local filesystem deletion, and static finalization behavior used at JVM shutdown.

Risks and test signals: because static `DELETE_ON_EXIT` is global, test isolation is important. Failures can indicate hook registration changes, incorrect map cleanup, or recursive delete semantics regressions.
