<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DoubleWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DoubleWritable.java

Purpose: writable comparable wrapper for double values with an optimized serialized comparator.

Important APIs, types, and functions: `readFields()`/`write()` use `DataInput.readDouble()` and `DataOutput.writeDouble()`. `set()`, `get()`, `equals()`, `hashCode()`, `compareTo()`, and `toString()` implement value behavior. Nested `Comparator` uses `WritableComparator.readDouble()` and `Double.compare()`.

Control flow: serialized form is eight bytes in `DataOutput` double format. Ordering follows `Double.compare`, including NaN and signed-zero semantics for compare.

State and persistence: one double field.

Dependencies and integration points: registered with `WritableComparator` for Hadoop sort/shuffle.

Risks and test signals: `equals()` uses `==`, so NaN is not equal to itself while `Double.compare()` treats NaN consistently for ordering; signed zero equality also differs from compare/hash expectations. Tests should cover NaN, signed zero, raw comparator, round trip, and equals/hash behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DoubleWritable.java -->
