<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/nfs3/TestFileHandle.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/nfs3/TestFileHandle.java

## Purpose

JUnit test for `FileHandle` construction and XDR serialization/deserialization. The source was read as a complete 39-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class TestFileHandle`, `public void testConstructor()`.

## Control Flow

Creates a FileHandle with id 1024, serializes it, deserializes into a new handle, and asserts the file id remains 1024.

## State and Persistence Behavior

Test-only state is local to each test method. No persistent files are created.

## Dependencies and Integration Points

Direct dependencies include `XDR`, `Test`, `assertThat`. Integration points are JUnit 5, AssertJ where used, and the Hadoop NFS classes under test.

## Risks and Edge Cases

The final assertion checks the original handle id rather than handle2, so the intended round-trip assertion appears incomplete.

## Test Signals

This file itself is a test signal; additional coverage should include negative/malformed XDR and more edge cases around cache expiry or file handle contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/nfs3/TestFileHandle.java -->
