# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend2.java

## Purpose

`TestFileAppend2.java` extends append coverage with permission checks, append-to-new-block behavior, concurrent random append workloads, and small append checksum recalculation. The complete 580-line file was read.

## Important APIs, Types, and Functions

Key APIs are `FileSystem.append`, `DistributedFileSystem.append(EnumSet<CreateFlag>)`, `CreateFlag.NEW_BLOCK`, `FsPermission`, `UserGroupInformation.createUserForTesting`, `AccessControlException`, `SubjectInheritingThread`, `LocatedBlock`, and `HdfsClientConfigKeys` timeout settings. The nested `Workload` class removes random paths from a shared pool, appends random lengths, waits for NameNode length visibility, validates bytes, and returns paths to the pool. Helpers include `testComplexAppend` and `testAppendLessThanChecksumChunk`.

## Control Flow

`testSimpleAppend` creates a file, writes 186 bytes, appends through 607 bytes, then appends the rest and validates contents. It also verifies append to a missing file and POSIX-style permission behavior where write permission on the file, not parent write permission, controls append. `testSimpleAppend2` repeats using `APPEND|NEW_BLOCK` and validates the resulting many small block sizes. `testComplexAppend` creates 50 files with random replication, starts 10 worker threads, and performs many small appends against random files. `testAppendLessThanChecksumChunk` writes 200 bytes, appends 300 bytes, hflushes while open, and reads the partial file to catch checksum overwrite mistakes below the default 512-byte checksum chunk.

## State and Persistence Behavior

State under test is file length and content across repeated close/reopen append cycles, per-file permissions, shared test path pool, and block boundaries introduced by `NEW_BLOCK`.

## Dependencies and Integration Points

The file integrates DFS permissions, UGI-authenticated filesystem instances, DataNode handler concurrency, client socket/write timeouts, NameNode metadata length updates, and `AppendTestUtil` content verification.

## Risks and Edge Cases

Risks include `getPos` returning zero on append streams, append permission accidentally depending on parent directory write permission, corrupt checksum after sub-chunk append, and races in shared workload bookkeeping or NameNode length propagation.

## Test Signals

Signals include full-file byte validation, expected `FileNotFoundException` and `AccessControlException`, exact `NEW_BLOCK` block sizes, worker `globalStatus`, file length equality after each append, and successful partial-read while an append stream remains open.
