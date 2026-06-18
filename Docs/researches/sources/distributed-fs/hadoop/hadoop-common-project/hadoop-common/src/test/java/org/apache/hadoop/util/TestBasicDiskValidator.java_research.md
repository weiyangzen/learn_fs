<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestBasicDiskValidator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestBasicDiskValidator.java

## Purpose

`TestBasicDiskValidator.java` specializes `TestDiskChecker` to verify the `BasicDiskValidator` implementation returned by `DiskValidatorFactory`.

## Important APIs, Types, and Functions

It overrides `checkDirs(boolean isDir, String perm, boolean success)` and calls `DiskValidatorFactory.getInstance(BasicDiskValidator.NAME).checkStatus(localDir)`.

## Control Flow

The inherited `TestDiskChecker` local-directory tests call the override with directory/file and permission combinations. The override creates a temp directory or file, sets permissions using `Shell`, invokes the validator, then asserts success/failure expectations.

## State and Persistence Behavior

Temporary files/directories are created under the test build directory and deleted in `finally`. Factory instances may be cached globally by `DiskValidatorFactory`.

## Dependencies and Integration Points

It integrates with `BasicDiskValidator`, `DiskValidatorFactory`, `DiskChecker.DiskErrorException`, `Shell`, and inherited disk checker tests.

## Risks and Edge Cases

POSIX permission behavior varies by platform and user privileges. Cleanup is best-effort with `File.delete`.

## Test Signals

Signals come from inherited cases for valid directories, non-directories, unreadable/unwritable/unlistable permissions, and expected `DiskErrorException` failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestBasicDiskValidator.java -->
