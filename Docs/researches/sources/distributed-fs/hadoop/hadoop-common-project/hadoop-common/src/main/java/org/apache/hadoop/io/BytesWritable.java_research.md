<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BytesWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BytesWritable.java

Purpose: resizable byte sequence usable as a Hadoop key or value. It separates logical length from backing-array capacity and orders bytes lexicographically.

Important APIs, types, and functions: constructors can alias an input byte array. `copyBytes()` returns an exact copy, while `getBytes()` exposes backing storage. `getLength()`, `setSize()`, `getCapacity()`, `setCapacity()`, and `set()` manage storage. `readFields()` reads an int length then bytes. `write()` writes length then valid bytes. `toString()` emits hex pairs. Nested `Comparator` skips the four length bytes in serialized form and compares payload bytes.

Control flow: resizing grows capacity to roughly 1.5 times requested size capped at `Integer.MAX_VALUE - 8`. Reads clear old size, allocate/grow, and fill the valid range.

State and persistence: state is logical size and byte array. Serialized form is four-byte length plus payload.

Dependencies and integration points: extends `BinaryComparable` and registers an optimized `WritableComparator`.

Risks and test signals: constructors and `getBytes()` expose mutable backing arrays. `setSize()` lacks explicit negative validation, so negative size paths should be tested. Tests should cover capacity growth/shrink, copy versus alias semantics, serialized comparator, empty values, large sizes, and hex output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BytesWritable.java -->
