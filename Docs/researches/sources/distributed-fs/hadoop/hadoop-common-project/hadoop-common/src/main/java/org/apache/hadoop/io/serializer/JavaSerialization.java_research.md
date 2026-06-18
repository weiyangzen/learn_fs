<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerialization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerialization.java

## Purpose
`JavaSerialization` is an experimental Hadoop `Serialization` implementation for Java `Serializable` objects using `ObjectInputStream` and `ObjectOutputStream`.

## Important APIs and Types
`JavaSerializationDeserializer` opens an `ObjectInputStream` with stream-header reading disabled and reads objects with `readObject`. `JavaSerializationSerializer` opens an `ObjectOutputStream` with stream-header writing disabled, calls `reset` before each `writeObject`, and closes the stream. The outer class accepts any class assignable to `Serializable`.

## Control Flow
Serialization writes each object without a per-stream Java serialization header and resets back-reference state before writing to avoid cross-object reference retention. Deserialization ignores any reuse object and always returns the next object read from the stream, wrapping `ClassNotFoundException` as `IOException`.

## State and Persistence
Serializer and deserializer instances hold object stream wrappers. The persisted format is Java native serialization objects without stream headers at this layer, which assumes the surrounding framework provides record boundaries and compatible stream handling.

## Dependencies and Integration Points
It implements Hadoop `Serialization<Serializable>`, produces `Serializer`/`Deserializer` pairs, and is paired with `JavaSerializationComparator` for comparable serializable keys.

## Risks and Edge Cases
Java serialization is unstable across class evolution, can be unsafe for untrusted data, and is marked experimental/unstable. Suppressing stream headers means these objects are not standalone standard Java serialization streams. Reuse is ignored, potentially increasing allocations. `IOException(e.toString())` loses the original `ClassNotFoundException` cause.

## Test Signals
Tests should cover round trips for simple serializable classes, multiple objects in one stream, object reference reset behavior, class-not-found handling, close behavior, compatibility with comparator deserialization, and rejection/acceptance by `Serializable` assignability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/JavaSerialization.java -->
