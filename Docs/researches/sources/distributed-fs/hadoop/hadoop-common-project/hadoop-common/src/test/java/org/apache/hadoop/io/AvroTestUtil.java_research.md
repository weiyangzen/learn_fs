<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/AvroTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/AvroTestUtil.java

## Purpose
Shared helper for tests that validate Avro reflection schemas and binary round trips for Hadoop writable-like classes.

## Important APIs, Types, and Functions
`testReflect(Object value, String schema)` delegates to `testReflect(Object value, Type type, String schema)`. It uses `ReflectData.get().getSchema(type)`, parses the expected schema, writes with `ReflectDatumWriter` and a direct binary encoder, then reads with `ReflectDatumReader` and a binary decoder.

## Control Flow and State
There is no persistent state. The helper first asserts schema equality, then serializes the supplied value to `ByteArrayOutputStream`, deserializes it with the same schema, and asserts value equality.

## Dependencies and Integration Points
Depends on Avro reflection APIs and JUnit assertions. Used by tests such as `TestEnumSetWritable` and `TestText` to ensure Hadoop types remain Avro-reflect compatible.

## Risks and Test Signals
Risk areas include Avro schema drift, package trust requirements, and equality semantics of reflected objects. The signal is strict schema equality plus binary round-trip equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/AvroTestUtil.java -->
