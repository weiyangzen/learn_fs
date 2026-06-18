# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/serializer/TestWritableSerialization.java

## Purpose
`TestWritableSerialization` validates Hadoop Writable serialization, Configurable propagation, and Java serialization of a `WritableComparator` subclass.

## Important APIs, Types, and Functions
The tests use `SerializationTestUtil`, `Text`, `TestGenericWritable.FooGenericWritable`, `Baz`, `CONF_TEST_KEY`, `CONF_TEST_VALUE`, `JavaSerialization`, `DataOutputBuffer`, `DataInputBuffer`, and nested `TestWC extends WritableComparator implements Serializable`.

## Control Flow
`testWritableSerialization()` round-trips a `Text`. `testWritableConfigurable()` sets a configuration value, creates a configurable generic writable fixture, then round-trips `Baz` and asserts equality plus non-null configuration on the result. `testWritableComparatorJavaSerialization()` manually serializes and deserializes `TestWC` through `JavaSerialization` and compares equality.

## State and Persistence
State is an in-memory static `Configuration` and byte buffers. No files are created.

## Dependencies and Integration Points
The file integrates Writable serialization, Configurable object initialization, Java object serialization, and comparator serializability.

## Risks and Edge Cases
The static `Configuration` is mutated in one test and shared across the class. `TestWC` equality depends only on `val`, and the default constructor gives a different value to ensure deserialized state is actually read.

## Test Signals
Signals are equal round-tripped `Text` and `Baz`, configuration propagation into deserialized configurable writables, and Java serialization preserving custom comparator field state.
