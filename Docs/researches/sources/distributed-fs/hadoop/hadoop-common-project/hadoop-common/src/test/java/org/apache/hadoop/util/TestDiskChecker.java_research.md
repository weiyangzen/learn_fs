<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDiskChecker.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDiskChecker.java

## Purpose

`TestDiskChecker.java` validates directory creation, permission checks, local filesystem checks, and injectable disk IO providers for `DiskChecker`.

## Important APIs, Types, and Functions

It tests `mkdirsWithExistsAndPermissionCheck`, `checkDir(FileSystem, Path, FsPermission)`, local `checkDirs`, `createTempFile`, `createTempDir`, `replaceFileOutputStreamProvider`, and `DiskErrorException`. It uses Mockito for `LocalFileSystem`, `Path`, `FileStatus`, and `File`.

## Control Flow

Setup saves the static `FileIoProvider`; teardown restores it. Mock-based tests validate permission setting and existing-directory checks. Real-file tests create files/directories, apply permissions via `Shell`, call `DiskChecker.checkDir`, and expect success or `DiskErrorException` based on readability/writability/listability.

## State and Persistence Behavior

Temporary files and directories are created under the test build directory and deleted. `DiskChecker` static file IO provider is temporarily replaced and restored.

## Dependencies and Integration Points

It integrates with Hadoop `FileSystem`/`LocalFileSystem`, permissions, `Shell`, `DiskChecker`, Mockito, and JUnit timeouts.

## Risks and Edge Cases

Permission behavior varies by OS, filesystem, umask, and effective user. Static provider mutation can leak if cleanup fails.

## Test Signals

Signals include mocked method verification, exception message prefix for permission mismatch, and success/failure for directory/file and permission matrix cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDiskChecker.java -->
