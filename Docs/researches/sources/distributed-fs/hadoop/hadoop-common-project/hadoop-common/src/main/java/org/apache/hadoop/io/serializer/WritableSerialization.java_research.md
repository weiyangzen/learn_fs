# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/WritableSerialization.java

## Purpose

`WritableSerialization` adapts Hadoop's `Writable` interface into the generic serializer/deserializer framework. It accepts any class assignable to `Writable` and delegates binary encoding to `Writable.write(DataOutput)` and decoding to `Writable.readFields(DataInput)`.

## Important APIs, control flow, and state

`accept(Class<?>)` returns `Writable.class.isAssignableFrom(c)`. `getSerializer()` creates a `WritableSerializer`, whose `open()` wraps the target stream in a `DataOutputStream` if needed, `serialize()` calls `w.write(dataOut)`, and `close()` closes the wrapped output. `getDeserializer()` creates a `WritableDeserializer`, which stores the target class and configuration. Its `deserialize(Writable w)` reuses the supplied instance when non-null or constructs a fresh instance with `ReflectionUtils.newInstance(writableClass, getConf())`, then calls `readFields(dataIn)`.

Mutable state is per serializer/deserializer instance: the bound data stream and, for deserialization, the target `Class<?>`. There is no persistent data beyond bytes written to caller-provided streams.

## Dependencies and integration points

The class depends on `Writable`, `DataInputStream`, `DataOutputStream`, `Configured`, and `ReflectionUtils`. It is the first default serialization in `SerializationFactory`, so it is the dominant path for Hadoop IPC and file formats that exchange `Writable` values.

## Risks and test signals

Closing closes the underlying stream, which is correct for the interface but important for callers sharing streams. Deserialization requires a no-argument constructible writable unless an instance is supplied. Reusing an instance means old fields must be fully overwritten by `readFields()`. `TestWritableSerialization` covers round-trip behavior, configurable writables, and interaction with Java serialization for `WritableComparator`; `TestSerializationFactory` validates lookup through the factory.
