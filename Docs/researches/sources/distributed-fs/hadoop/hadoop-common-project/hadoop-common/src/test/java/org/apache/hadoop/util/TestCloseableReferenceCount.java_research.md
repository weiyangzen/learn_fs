<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCloseableReferenceCount.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCloseableReferenceCount.java

## Purpose

`TestCloseableReferenceCount.java` validates reference-count transitions for a closeable resource guard.

## Important APIs, Types, and Functions

It tests `CloseableReferenceCount.reference`, `unreference`, `unreferenceCheckClosed`, `setClosed`, `isOpen`, and `getReferenceCount`.

## Control Flow

Tests create a fresh counter, increment references, decrement references, set closed, and assert open/closed state and reference counts. Closed references are expected to throw `ClosedChannelException`.

## State and Persistence Behavior

State is the in-memory reference count and closed flag. No persistence exists.

## Dependencies and Integration Points

It extends `HadoopTestBase` and integrates with Java `ClosedChannelException` and resource lifecycle patterns in Hadoop utilities.

## Risks and Edge Cases

Correctness depends on atomicity in the implementation under concurrent use, although this test is mostly single-threaded. Underflow and close-while-referenced behavior are important risks.

## Test Signals

Signals include initial count, increment/decrement behavior, boolean return from final unreference, closed flag transitions, and exception on referencing a closed counter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCloseableReferenceCount.java -->
