# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/LongWritable.java

Purpose: `LongWritable` is Hadoop's stable `WritableComparable` wrapper for a Java `long`, providing binary serialization and optimized raw comparison for long-valued keys and values.

Important APIs and types: mutable `value` is controlled by constructors, `set(long)`, and `get()`. `readFields`/`write` use `DataInput.readLong` and `DataOutput.writeLong`. `compareTo`, `equals`, `hashCode`, and `toString` provide object semantics. Nested `Comparator` reads long values directly from serialized bytes; `DecreasingComparator` reverses both object and raw byte ordering.

Control flow: serialization writes or reads one eight-byte value. Default sort paths use the registered `Comparator`. Callers needing descending order can explicitly use `DecreasingComparator`, which swaps operands before delegating to the normal comparator.

State and persistence: state is a single mutable `long`. Persistent representation is exactly eight bytes. Static initialization registers the ascending comparator as the default for `LongWritable`.

Dependencies and integration points: integrates with `WritableComparable`, `WritableComparator`, SequenceFile/MapFile ordering, and MapReduce sort/grouping. It is also used internally by `MapFile` index entries to store byte positions.

Risks and test signals: notable risk is `hashCode()` truncating to the low 32 bits, which is compatible but collision-prone for patterned long values. Mutation after map/set insertion has the usual mutable-key hazard. Tests should cover round trips, raw and object comparison equivalence, decreasing comparator behavior, boundary values, and hash/equality consistency.
