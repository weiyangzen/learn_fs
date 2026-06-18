# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCpCommand.java

## Purpose
Tests multithread and queue-size option handling for FsShell `cp`, mirroring the recursive copy behavior used by local copy commands but for filesystem-to-filesystem copies.

## Important APIs, Types, and Functions
The test uses `CopyCommands.Cp`, `CopyCommandWithMultiThread.DEFAULT_QUEUE_SIZE`, local filesystem setup, and `ThreadPoolExecutor`. Nested `MultiThreadedCp` overrides `processArguments` to assert parsed thread count, queue size, completed task count, active count, and executor termination.

## Control Flow
Class setup configures a local filesystem and working directory. Per-test setup creates randomized `fromDir` and `toDir` trees under a unique directory. Tests run default `cp`, threaded `-t 5`, invalid `-t 0`, threaded with queue `-q 256`, invalid queue `-q 0`, and a single-file copy with `-t 5`. Recursive directory copies with multithreading expect completed tasks equal generated file count; single-file/default paths expect no executor.

## State and Persistence
Temporary local filesystem state is class-scoped and deleted after all tests. Generated file content is simple repeated integer/newline data. Executor state is checked after each command completes.

## Dependencies and Integration Points
This tests the `Cp` command as a subclass of the shared multithread copy framework and ensures option parsing stays aligned with `copyToLocal`.

## Risks and Edge Cases
Random file generation can yield low or zero task counts. The test checks copy execution success and executor state, not full byte-for-byte target verification. Timeout annotations bound deadlock risk.

## Test Signals
Passing tests indicate that `cp` respects valid `-t`/`-q` settings, falls back for invalid values, avoids executor setup for simple copies, and shuts down executor work cleanly.
