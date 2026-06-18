# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestNativeIoInit.java

## Purpose
`TestNativeIoInit` is a focused regression test for native I/O class initialization deadlocks, especially the static initializer interaction described by HADOOP-14451.

## Important APIs, Types, and Functions
The tests call `NativeIO.isAvailable()`, `NativeIO.POSIX.isAvailable()`, and on Windows `NativeIO.Windows.extendWorkingSetSize(100)`. Threads are `SubjectInheritingThread`s to preserve Hadoop subject context.

## Control Flow
`testDeadlockLinux()` starts two threads that touch the outer `NativeIO` class and the nested `NativeIO.POSIX` class concurrently, then joins both under a 10-second timeout. `testDeadlockWindows()` is Windows-gated and races `NativeIO.isAvailable()` against a Windows native call, swallowing expected `IOException`s from the working-set extension.

## State and Persistence
The only state is JVM class initialization state and thread execution. The test creates no files and persists nothing.

## Dependencies and Integration Points
It depends on the native I/O initialization path, `Path.WINDOWS`, JUnit timeouts, and Hadoop's subject-inheriting thread utility. It intentionally lives in a separate class so forked test execution reloads static blocks.

## Risks and Edge Cases
The signal is timeout-based; a deadlock manifests as the test exceeding its timeout rather than an assertion failure. The Windows branch only runs on Windows and ignores `IOException` from the native call because the concern is deadlock, not permission.

## Test Signals
Passing means both initialization threads finish within 10 seconds on POSIX and Windows-specific class initialization also completes without hanging.
