<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBoundedByteArrayOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBoundedByteArrayOutputStream.java

## Purpose
Unit tests for `BoundedByteArrayOutputStream` capacity enforcement, reset behavior, and protected buffer replacement.

## Important APIs, Types, and Functions
Uses `BoundedByteArrayOutputStream.write`, `reset`, `reset(int)`, `getLimit`, `getBuffer`, and subclass-exposed `resetBuffer(byte[], int, int)`. Test input is a static 1024-byte random array.

## Control Flow and State
`testBoundedStream()` fills the stream to capacity, asserts contents, verifies one extra byte throws, resets, writes again, lowers the limit, and verifies an oversized write fails. `testResetBuffer()` repeats the capacity checks after swapping in a new backing buffer through a test subclass.

## Dependencies and Integration Points
The tests target the IO utility directly and depend only on JUnit and Java arrays/random data. This stream is used where Hadoop needs bounded in-memory serialization.

## Risks and Test Signals
Risks include off-by-one capacity enforcement, stale limit after reset, and incorrect backing-buffer replacement. Signals are array equality, limit values, and caught exceptions on overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBoundedByteArrayOutputStream.java -->
