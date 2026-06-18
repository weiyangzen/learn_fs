# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/avro/Record.java

## Purpose
`Record` is a simple public POJO used by Avro reflection serialization tests.

## Important APIs, Types, and Functions
The class exposes one public integer field `x`, defaulting to 7. `hashCode()` returns `x`, and `equals(Object)` compares class equality and `x` value.

## Control Flow
There is no active control flow beyond equality checks. Test code mutates `x` and uses equality after serialization round trips.

## State and Persistence
State is the public `x` field. Persistence is only through external serializers in tests.

## Dependencies and Integration Points
It lives in the Avro serializer test package so `AvroReflectSerialization.AVRO_REFLECT_PACKAGES` can include its package name and accept it for reflection serialization.

## Risks and Edge Cases
The public mutable field and no-arg default shape are intentionally simple for Avro reflection. Equality rejects subclasses through exact class comparison.

## Test Signals
The main signal is equality after Avro reflection serialization when `x` is changed from its default.
