<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerializationComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerializationComparator.java

## Purpose
`JavaSerializationComparator` compares raw serialized Java-serialization keys by deserializing them and invoking their `Comparable` implementation.

## Important APIs and Types
The generic bound requires `T extends Serializable & Comparable<T>`. The constructor creates a `JavaSerializationDeserializer<T>` and passes it to `DeserializerComparator`. `compare(T o1, T o2)` delegates to `o1.compareTo(o2)`.

## Control Flow
Raw byte comparison flow is inherited: reset buffer to first slice, deserialize, reset to second slice, deserialize, then compare objects.

## State and Persistence
State lives in the superclass: an input buffer, deserializer, and reusable key references. The comparator has no additional fields.

## Dependencies and Integration Points
It integrates with `JavaSerialization`, `DeserializerComparator`, and Hadoop `RawComparator`. TFile documentation mentions Java comparator classes can be referenced with `jclass:` if they have default constructors.

## Risks and Edge Cases
It inherits performance and thread-safety costs from deserialization-based comparison. It assumes serialized objects are mutually comparable and non-null. Malformed serialized bytes produce runtime exceptions via the superclass.

## Test Signals
Tests should compare ordered serializable keys, equal keys, malformed data, null-handling expectations, constructor availability for reflective use, and repeated comparisons with object reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerializationComparator.java -->
