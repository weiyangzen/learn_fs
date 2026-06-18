<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/FloatWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/FloatWritable.java

Purpose: writable comparable wrapper for float values with an optimized raw comparator.

Important APIs, types, and functions: `set()`, `get()`, `readFields()`, `write()`, `equals()`, `hashCode()`, `compareTo()`, and `toString()` implement float value behavior. Nested `Comparator` reads serialized floats via `WritableComparator.readFloat()` and compares with `Float.compare()`.

Control flow: serialized form is four bytes in `DataOutput` float format. Ordering follows `Float.compare`.

State and persistence: one float field.

Dependencies and integration points: registered with `WritableComparator` for Hadoop sorting.

Risks and test signals: like `DoubleWritable`, `equals()` uses `==`, so NaN and signed-zero semantics differ from comparator/hash behavior. Tests should cover NaN, signed zero, raw comparator, round trip, and comparator registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/FloatWritable.java -->
