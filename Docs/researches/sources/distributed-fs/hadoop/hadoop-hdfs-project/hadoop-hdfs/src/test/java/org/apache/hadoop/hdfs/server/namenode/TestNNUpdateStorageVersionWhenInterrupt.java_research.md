# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNUpdateStorageVersionWhenInterrupt.java

## Purpose
Regression test for `NNStorage.writeAll` when interrupted while writing VERSION files. It verifies an interrupt-induced `ClosedByInterruptException` is logged but the storage directory remains registered.

## Important APIs, Types, and Functions
- Constructs `NNStorage` from file URIs for name and edits dirs.
- Uses `StorageDirectory.getVersionFile`, Java NIO `Files.createDirectories/createFile`, and `GenericTestUtils.LogCapturer.captureLogs(NNStorage.LOG)`.
- `UpdateVersionFileThread` calls `nnStorage.writeAll()` and ignores IOExceptions.

## Control Flow
- `BeforeAll` creates one storage dir and an empty VERSION file, then starts capturing `NNStorage` logs.
- Test asserts there is one storage dir, starts the writer thread, interrupts it, waits until captured logs include `ClosedByInterruptException`, and asserts the storage dir count is still one.

## State and Persistence Behavior
- Operates on a real temporary NameNode storage directory under `GenericTestUtils.getTestDir("dfs")`.
- The important invariant is that an interrupted write does not drop the storage directory from `NNStorage`.

## Dependencies and Integration Points
- Integrates low-level storage writing, Java interrupt behavior, and logging.
- Does not start a NameNode or cluster.

## Risks and Edge Cases
- Timing-sensitive because interrupt must hit during write; wait loop depends on log output.
- The worker thread is not joined, though wait-for-log implies the write path observed interruption.
- Static storage/log capture can share state across repeated JVM runs.

## Test Signals
- Focused signal for storage robustness under thread interruption and for preserving directory membership after failed VERSION writes.
