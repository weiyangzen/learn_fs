<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/DeserializerComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/DeserializerComparator.java

## Purpose
`DeserializerComparator<T>` is a `RawComparator` base class that compares serialized byte slices by deserializing them and delegating to the normal object comparator.

## Important APIs and Types
The constructor accepts a `Deserializer<T>` and opens it on an internal `InputBuffer`. `compare(byte[], int, int, byte[], int, int)` resets the buffer to each byte slice, deserializes into reusable `key1` and `key2`, and returns `compare(key1, key2)`, which subclasses implement through `Comparator<T>`.

## Control Flow
Every raw comparison performs two deserialize operations. `IOException` from deserialization is wrapped in `RuntimeException` because `RawComparator.compare` cannot throw checked exceptions.

## State and Persistence
The comparator holds a reusable `InputBuffer`, one deserializer, and two reusable key objects. This makes instances stateful and not inherently thread-safe.

## Dependencies and Integration Points
It integrates with Hadoop `RawComparator`, `InputBuffer`, and serialization implementations such as `JavaSerializationComparator`.

## Risks and Edge Cases
Because it deserializes for every compare, it is slower than byte-native comparators for sort-heavy paths. Shared mutable `key1`/`key2` and `InputBuffer` make concurrent use unsafe. Implementations must tolerate deserializer reuse with changing buffer content.

## Test Signals
Tests should compare equivalent and ordered serialized keys, malformed byte slices, reuse of key objects across calls, runtime exception wrapping, and thread-safety assumptions if shared in sort code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/DeserializerComparator.java -->
