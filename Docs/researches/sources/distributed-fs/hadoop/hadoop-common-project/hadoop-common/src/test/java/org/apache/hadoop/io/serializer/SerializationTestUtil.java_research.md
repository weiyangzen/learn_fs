# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/SerializationTestUtil.java

## Purpose
`SerializationTestUtil` provides a generic round-trip helper for Hadoop serialization tests.

## Important APIs, Types, and Functions
`testSerialization(Configuration conf, K before)` builds a `SerializationFactory`, obtains a `Serializer` and `Deserializer` for `GenericsUtil.getClass(before)`, writes into `DataOutputBuffer`, reads from `DataInputBuffer`, and returns the deserialized object.

## Control Flow
The helper opens the serializer, serializes the input, closes it, resets an input buffer over the output bytes, opens the deserializer, deserializes into a null reuse object, closes it, and returns the result.

## State and Persistence
All state is in heap buffers and local serializer/deserializer instances. No files are created.

## Dependencies and Integration Points
It integrates with Hadoop `SerializationFactory`, `Serializer`, `Deserializer`, `DataOutputBuffer`, `DataInputBuffer`, and `GenericsUtil`. Tests for Writable and Avro serialization reuse it.

## Risks and Edge Cases
The method assumes the factory can resolve both serializer and deserializer; otherwise null dereferences will fail the caller. It uses the runtime class of `before`, so null inputs are unsupported.

## Test Signals
Success means factory lookup, stream lifecycle, serialized bytes, and deserialization all produce an object equal to the original in caller tests.
