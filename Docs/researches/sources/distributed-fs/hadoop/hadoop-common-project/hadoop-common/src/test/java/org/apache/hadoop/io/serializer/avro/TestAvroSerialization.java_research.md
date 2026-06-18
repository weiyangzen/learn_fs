# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/avro/TestAvroSerialization.java

## Purpose
`TestAvroSerialization` validates Hadoop Avro serialization for specific records, reflection-configured POJOs, inner classes, and marker-interface reflect serializables.

## Important APIs, Types, and Functions
Tests use `AvroRecord`, `Record`, `AvroReflectSerialization.AVRO_REFLECT_PACKAGES`, `SerializationTestUtil`, `SerializationFactory`, nested `InnerRecord`, and nested `RefSerializable implements AvroReflectSerializable`.

## Control Flow
`testSpecific()` round-trips a generated specific Avro record. `testReflectPkg()` sets the reflect package configuration and round-trips `Record`. `testAcceptHandlingPrimitivesAndArrays()` asserts byte arrays and primitive byte do not get serializers. `testReflectInnerClass()` verifies reflect package matching for a nested class. `testReflect()` verifies marker-interface-based reflect serialization without package configuration.

## State and Persistence
The static `Configuration` is mutated to set reflect packages and reused across tests. Serialization state stays in memory through `SerializationTestUtil`.

## Dependencies and Integration Points
The file integrates Hadoop serialization factory lookup with Avro specific and reflect serialization modes. It tests primitive/array rejection to avoid inappropriate Avro acceptance.

## Risks and Edge Cases
Static configuration reuse can leak reflect package settings across tests, though all tests remain compatible with that setting. Equality for reflect classes compares exact class and `x`.

## Test Signals
Signals are equality after specific and reflect round trips, null serializers for unsupported primitive/array types, and successful reflect handling for nested and marker-interface classes.
