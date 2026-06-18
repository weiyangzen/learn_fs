<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsTime.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsTime.java

## Purpose

JUnit 5 tests for `NfsTime` millisecond-to-second/nanosecond conversion and XDR round-trip equality. The source was read as a complete 46-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class TestNfsTime`, `public void testConstructor()`, `public void testSerializeDeserialize()`.

## Control Flow

Constructs `NfsTime(1001)`, checks seconds/nseconds, serializes to XDR, deserializes from read-only wrapper, and asserts equality.

## State and Persistence Behavior

Test-only state is local to each test method. No persistent files are created.

## Dependencies and Integration Points

Direct dependencies include `Assertions`, `XDR`, `Test`. Integration points are JUnit 5, AssertJ where used, and the Hadoop NFS classes under test.

## Risks and Edge Cases

Coverage is narrow but protects the time encoding consumed by NFS attrs and WCC structures.

## Test Signals

This file itself is a test signal; additional coverage should include negative/malformed XDR and more edge cases around cache expiry or file handle contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsTime.java -->
