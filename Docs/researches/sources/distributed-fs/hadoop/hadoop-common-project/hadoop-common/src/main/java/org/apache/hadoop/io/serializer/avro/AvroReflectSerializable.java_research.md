# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroReflectSerializable.java

## Purpose

`AvroReflectSerializable` is a marker interface. Classes implement it to opt into Hadoop's Avro reflect serializer without relying on package-level configuration.

## Important APIs, control flow, and state

The interface declares no methods and has no state. Its only behavior is via `AvroReflectSerialization.accept(Class<?>)`, which returns true for classes assignable to this interface.

## Dependencies and integration points

The integration point is `AvroReflectSerialization`, which uses this marker together with `avro.reflect.pkgs`. It is public and evolving so external classes can use it as a stable opt-in signal for Hadoop's serialization framework.

## Risks and test signals

The marker gives broad reflective serialization privileges to a class. Classes still need to be compatible with Avro reflect schema generation. Test coverage is indirect through `TestAvroSerialization.testReflect()` and related reflect package and inner-class tests.
