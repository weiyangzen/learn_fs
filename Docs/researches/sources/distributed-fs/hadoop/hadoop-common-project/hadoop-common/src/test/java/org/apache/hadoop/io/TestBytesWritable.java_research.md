<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBytesWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBytesWritable.java

## Purpose
Tests `BytesWritable` dynamic sizing, hash/compare/toString semantics, zero-copy construction, and `ByteWritable` common methods.

## Important APIs, Types, and Functions
Exercises `BytesWritable.setSize`, `setCapacity`, `getCapacity`, `getLength`, `getBytes`, `copyBytes`, `hashCode`, `compareTo`, `toString`, zero-copy constructor `(byte[], length)`, and `set(byte[], offset, length)`. Also tests `ByteWritable.set`, `get`, `compareTo`, `equals`, and `toString`.

## Control Flow and State
`testSizeChange()` expands and shrinks a buffer while preserving data and length invariants. `testHash()` verifies hash ignores capacity beyond logical length. `testCompare()` checks reflexive/symmetric lexicographic ordering across several byte arrays. `testZeroCopy()` asserts constructor retains the original backing array and remains equal to copied construction after buffer expansion/reset.

## Dependencies and Integration Points
These writables are core types for sequence/map files, RPC payloads, and writable collections. Tests depend only on JUnit.

## Risks and Test Signals
Risks are logical length vs capacity confusion, zero-copy aliasing surprises, and signed-byte rendering. Signals are exact hash values, formatted hex strings, comparator ordering, and backing-array identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBytesWritable.java -->
