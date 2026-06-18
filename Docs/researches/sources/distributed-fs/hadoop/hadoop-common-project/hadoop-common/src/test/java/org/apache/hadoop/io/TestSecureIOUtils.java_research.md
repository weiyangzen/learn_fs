<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSecureIOUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSecureIOUtils.java

## Purpose
Tests secure file opening helpers that enforce expected owner/group when native IO is available, and creation behavior for existing files.

## Important APIs, Types, and Functions
Uses `SecureIOUtils.openForRead`, `openFSDataInputStream`, `openForRandomRead`, forced secure variants, `createForWrite`, `SecureIOUtils.AlreadyExistsException`, `NativeIO.isAvailable`, `FileSystem.getLocal(conf).getRaw()`, and JUnit lifecycle/timeout annotations.

## Control Flow and State
`makeTestFile()` creates three target files under `target/`, writes `hello`, and records real owner/group from local raw filesystem status. Unrestricted and correctly restricted reads must close successfully. Incorrect restriction assumes native IO availability, then tries invalid user ownership for input stream, FSDataInputStream, and random read, expecting `IOException`. `testCreateForWrite()` asserts creating over an existing file fails. `removeTestFile()` deletes all three files.

## Dependencies and Integration Points
Integrates Java files, Hadoop raw local filesystem ownership, native IO availability, and secure open wrappers used by localizer and security-sensitive code.

## Risks and Test Signals
Risks include platform-specific owner/group behavior, native library availability gating, octal permission semantics, and cleanup failures. Signals are successful opens for null/real owners, expected IO failures for invalid owner under native IO, and `AlreadyExistsException` for existing create.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSecureIOUtils.java -->
