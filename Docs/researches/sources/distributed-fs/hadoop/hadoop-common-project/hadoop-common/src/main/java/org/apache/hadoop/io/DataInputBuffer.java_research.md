<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputBuffer.java

Purpose: reusable `DataInputStream` over a byte array without allocating a new `ByteArrayInputStream` for each read.

Important APIs, types, and functions: nested `Buffer` extends `ByteArrayInputStream` and exposes `reset(input,start,length)`, `getData()`, `getPosition()`, and `getLength()`, with optimized `read`, `read(byte[],off,len)`, `skip`, and `available`. Outer `DataInputBuffer` exposes reset and position/length accessors.

Control flow: callers reset the buffer to a byte range and then use normal `DataInput` methods inherited from `DataInputStream`.

State and persistence: state is the referenced byte array, current position, mark, and count. It aliases caller-provided input.

Dependencies and integration points: common utility for writable serialization, comparators, and map writable copy logic.

Risks and test signals: `getLength()` returns the absolute count index, not necessarily the logical length when start is non-zero. Tests should cover non-zero starts, EOF behavior, skip bounds, readFully through `DataInputStream`, and aliasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputBuffer.java -->
