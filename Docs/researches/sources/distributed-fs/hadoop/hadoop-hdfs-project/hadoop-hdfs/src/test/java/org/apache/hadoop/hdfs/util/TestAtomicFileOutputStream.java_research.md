# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestAtomicFileOutputStream.java

## Purpose
`TestAtomicFileOutputStream` verifies atomic write/replace semantics and cleanup behavior for `AtomicFileOutputStream`.

## Important APIs, Types, And Functions
It uses `AtomicFileOutputStream`, `DFSTestUtil.readFile`, `FileUtil`, `PathUtils`, `IOUtils`, and `PlatformAssumptions.assumeWindows`. `createFailingStream()` subclasses `AtomicFileOutputStream` to inject a `flush()` failure.

## Control Flow
Before each test, the test directory is created and emptied. `testWriteNewFile` writes to a non-existing destination and confirms the destination appears only after close. `testOverwriteFile` confirms existing destination contents remain unchanged until close, then are replaced. `testFailToFlush` injects close-time flush failure and checks the original file remains intact and the temp file is removed. `testFailToRename` runs only on Windows, makes the directory non-writable, closes the stream, and expects a native rename failure.

## State, Persistence, And Dependencies
State is local filesystem content under the test directory, including destination and temporary files. Tests mutate directory writability on Windows and restore it in finally.

## Integration Points
This tests the local durable-write primitive used by HDFS utilities for atomic file replacement.

## Risks
Rename and writability behavior is platform-specific; the Windows-only test is guarded but still depends on native error wording. Failure injection only covers `flush()`, not all possible write or close failures. Directory listing assertion assumes only destination remains after cleanup.

## Test Signals
Signals include destination existence before/after close, exact file contents before/after close, thrown `IOException` on injected failure, temp-file cleanup via directory listing, and Windows rename error text.
