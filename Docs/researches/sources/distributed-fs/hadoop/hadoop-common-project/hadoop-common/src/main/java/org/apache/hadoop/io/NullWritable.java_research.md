# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/NullWritable.java

Purpose: `NullWritable` is Hadoop's singleton zero-byte `WritableComparable`, used when a key or value position is semantically empty but APIs require a Writable object.

Important APIs and types: `get()` returns the single private instance. `readFields` and `write` are no-ops. `compareTo` always returns zero, `equals` accepts any `NullWritable`, `hashCode` returns zero, and `toString` returns `(null)`. Nested `Comparator` asserts both serialized lengths are zero and returns equality.

Control flow: all serialization paths consume or emit no bytes. Static initialization registers the raw comparator with `WritableComparator`, so sort paths can compare zero-length serialized values without instantiation.

State and persistence: no per-instance state exists. Persistent representation is empty. Singleton construction keeps object identity stable for normal use, though equality is type-based rather than identity-based.

Dependencies and integration points: integrates with Hadoop Writable APIs and MapReduce jobs that use no meaningful key or value, for example output values where only keys matter.

Risks and test signals: risks are mostly API misuse: expecting payload bytes, using assertions as runtime validation for serialized length, or relying on object identity after reflective construction. Tests should cover singleton access, zero-byte round trip, comparator behavior with zero lengths, equality/hash semantics, and use as a MapReduce key/value placeholder.
