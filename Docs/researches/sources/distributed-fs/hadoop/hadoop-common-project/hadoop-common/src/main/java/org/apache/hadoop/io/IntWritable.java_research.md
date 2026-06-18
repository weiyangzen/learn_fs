# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/IntWritable.java

Purpose: `IntWritable` is Hadoop's stable `WritableComparable` wrapper for a Java `int`, used as a serialized key or value in Hadoop IO, SequenceFile, MapReduce, and RPC-facing data structures.

Important APIs and types: the mutable `value` field is managed through constructors, `set(int)`, and `get()`. `readFields(DataInput)` reads one four-byte integer and `write(DataOutput)` writes one four-byte integer. `equals`, `hashCode`, `compareTo`, and `toString` implement value semantics. Nested `Comparator` extends `WritableComparator` to compare serialized forms directly with `readInt`.

Control flow: normal object serialization is a direct `readInt`/`writeInt` pair. Sorting can bypass object creation through the registered raw comparator, which reads the two integer values from byte slices and returns the same ordering as `compareTo`.

State and persistence: the only state is the mutable primitive value. Persistence is Hadoop Writable binary format: exactly four bytes in `DataOutput` order. Static initialization registers the optimized comparator globally with `WritableComparator`.

Dependencies and integration points: depends on `WritableComparable` and `WritableComparator`. It is a common key type for SequenceFile/MapFile and MapReduce sort/shuffle paths where raw comparators matter for performance.

Risks and test signals: risks are low but include mutation after insertion into hash collections, comparator misuse with slices shorter than four bytes, and hash distribution matching integer identity. Tests should check binary round trips, raw comparator ordering for negative/positive/boundary values, equality/hash consistency, and registration with `WritableComparator.get`.
