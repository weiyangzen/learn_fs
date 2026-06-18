<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Deserializer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Deserializer.java

## Purpose
`Deserializer<T>` defines Hadoop's stream-based object deserialization contract for HDFS and MapReduce serialization frameworks.

## Important APIs and Types
The interface exposes `open(InputStream)`, `deserialize(T reuse)`, and `close`. Implementations may reuse the provided object or allocate a new one when the argument is null.

## Control Flow
Clients open the deserializer on an input stream, repeatedly call `deserialize`, then close it. The contract explicitly says deserializers are stateful but must not buffer input because other producers may read from the same stream between calls.

## State and Persistence
Implementations usually hold stream wrappers and reusable object state. The interface itself has no state. Deserialized objects are produced from the stream format owned by each `Serialization`.

## Dependencies and Integration Points
It pairs with `Serializer` and `Serialization`, and is used by `DeserializerComparator`, `JavaSerialization`, `WritableSerialization`, and `SerializationFactory`.

## Risks and Edge Cases
Implementations that buffer ahead can corrupt mixed stream consumers. Reuse semantics are optional, so callers cannot assume object identity. `close` closes the underlying stream according to this contract.

## Test Signals
Tests should verify open/deserialize/close lifecycle, object reuse behavior per implementation, no read-ahead across object boundaries, error propagation, and close cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Deserializer.java -->
