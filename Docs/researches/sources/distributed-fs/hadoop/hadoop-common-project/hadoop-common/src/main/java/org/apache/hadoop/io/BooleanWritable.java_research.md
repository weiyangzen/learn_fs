<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BooleanWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BooleanWritable.java

Purpose: writable comparable wrapper for boolean values with an optimized raw comparator.

Important APIs, types, and functions: `set()`, `get()`, `readFields()`, `write()`, `equals()`, `hashCode()`, `compareTo()`, and `toString()` implement boolean value behavior. Nested `Comparator` compares serialized bytes through `compareBytes()`, and the static block registers it.

Control flow: serialized form is one Java boolean. Ordering is false before true.

State and persistence: one boolean field. Persistent form is one byte as written by `DataOutput.writeBoolean()`.

Dependencies and integration points: participates in Hadoop writable sorting via `WritableComparator.define()`.

Risks and test signals: hash code returns 0 for true and 1 for false, which is valid but inverted from some conventions. Tests should cover round trip, sort order, raw comparator behavior, equals/hash consistency, and comparator registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BooleanWritable.java -->
