<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDiskCheckerWithDiskIo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDiskCheckerWithDiskIo.java

## Purpose

`TestDiskCheckerWithDiskIo.java` validates the disk-IO probe path of `DiskChecker.checkDirWithDiskIo`.

## Important APIs, Types, and Functions

It defines `TestFileIoProvider` implementing `DiskChecker.FileIoProvider`, tests transient and persistent create/write errors, file naming, and helper `checkDirs`.

## Control Flow

Tests replace the file IO provider with one that can fail a configured number of create or write operations. Transient failures should be retried/ignored when eventual IO succeeds; persistent failures should throw `DiskErrorException`. File naming checks verify temporary check files are created with expected prefix/suffix patterns.

## State and Persistence Behavior

Temporary directories and probe files are created and removed. The static `DiskChecker` file IO provider is mutated and restored through the test helper path.

## Dependencies and Integration Points

It integrates with `DiskChecker.checkDirWithDiskIo`, `FileIoProvider`, `FileOutputStream`, Java NIO temp directory creation, and JUnit timeouts.

## Risks and Edge Cases

IO retry semantics are sensitive: too many retries can hide real failures, while too few can fail on transient disk issues. Static provider replacement is global.

## Test Signals

Signals include expected exceptions for persistent failures, successful transient recovery, provider invocation counts, and generated check-file naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDiskCheckerWithDiskIo.java -->
