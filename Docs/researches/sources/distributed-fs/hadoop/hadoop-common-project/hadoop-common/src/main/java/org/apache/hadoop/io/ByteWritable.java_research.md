<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteWritable.java

Purpose: writable comparable wrapper for a single signed byte with an optimized raw comparator.

Important APIs, types, and functions: `set()`, `get()`, `readFields()`, `write()`, `equals()`, `hashCode()`, `compareTo()`, and `toString()` implement byte value behavior. Nested `Comparator` compares the first serialized byte at each offset and is registered statically.

Control flow: serialized form is one byte. Ordering is signed-byte numeric order.

State and persistence: one byte field, persisted as one byte.

Dependencies and integration points: integrates with Hadoop sort/shuffle via `WritableComparator`.

Risks and test signals: raw comparator ignores lengths and assumes valid one-byte serialized values. Tests should cover negative/positive ordering, round trip, comparator registration, and equals/hash consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteWritable.java -->
