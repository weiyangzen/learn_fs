# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithLocal.java

## Purpose
Local-filesystem integration tests for `RollingFileSystemSink`, using `RollingFileSystemSinkTestBase` to validate writes, pre-existing files, append/roll suffixes, and error handling.

## Important APIs, Types, And Functions
Extends `RollingFileSystemSinkTestBase` and uses `initMetricsSystem()`, `doWriteTest()`, `doAppendTest()`, `preCreateLogFile()`, `assertMetricsContents()`, and `MockSink.errored`.

## Control Flow
Tests use the method directory URI as sink base path. Normal and silent writes publish metrics and assert contents. Existing-file tests pre-create current-hour log files and expect the sink to create suffixed files when append is disabled. Failure tests make the directory non-writable before publishing and then inspect whether the mock sink reports an error depending on `ignore-error`.

## State And Persistence Behavior
Filesystem state is created under the per-method local test directory and cleaned by the base class. Directory writability is restored in `finally` blocks. `MockSink.errored` is reset before failure assertions.

## Dependencies And Integration Points
Exercises the sink through the real metrics system and local Hadoop `FileSystem`, with host-based log file names and actual file permissions.

## Risks
Permission behavior can differ by platform or privileged user. The method `testSilentExistingWrite()` passes `ignoreErrors=false` despite its name/comment, so its behavior matches non-silent existing write rather than an ignore-error variant.

## Test Signals
Expected signals are valid metrics contents, one file for fresh writes, two or three files when pre-existing names force suffixes, propagated errors for non-writable directories, and no `MockSink.errored` when ignore-error is enabled.
