# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/RawComparator.java

Purpose: `RawComparator<T>` extends Java `Comparator<T>` with a method for comparing serialized byte representations directly, enabling Hadoop sort paths to avoid object deserialization.

Important APIs and types: the sole additional method `compare(byte[] b1, int s1, int l1, byte[] b2, int s2, int l2)` compares two objects encoded as byte ranges. Implementations also provide normal object comparison through `Comparator<T>`.

Control flow: Hadoop sorting, grouping, and lookup components can call raw comparison when they have serialized key bytes, and object comparison when actual key instances are present. Implementations must keep both orderings consistent.

State and persistence: the interface has no state and no persistence behavior. It defines a contract for consumers of serialized data.

Dependencies and integration points: depends on Java `Comparator` and references `DeserializerComparator`. It is implemented by `WritableComparator` and specialized comparators such as `IntWritable.Comparator`, `LongWritable.Comparator`, and `MD5Hash.Comparator`; MapFile and SequenceFile sorting rely on this contract.

Risks and test signals: risks include inconsistent raw/object ordering, invalid handling of offsets and lengths, and comparators reading beyond slice boundaries. Tests should compare raw and object results for the same values, exercise nonzero offsets, truncated or malformed encodings where applicable, and verify sort/group behavior with custom comparators.
