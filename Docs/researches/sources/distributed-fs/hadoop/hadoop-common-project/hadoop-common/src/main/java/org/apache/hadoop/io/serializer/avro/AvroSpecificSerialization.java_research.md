# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroSpecificSerialization.java

## Purpose

`AvroSpecificSerialization` adapts Avro generated `SpecificRecord` classes into Hadoop's `Serialization` framework.

## Important APIs, control flow, and state

`accept(Class<?>)` matches classes assignable to `SpecificRecord`. `getReader(Class<SpecificRecord>)` instantiates the class with `clazz.newInstance()` and uses its schema to create a `SpecificDatumReader`. `getSchema(SpecificRecord)` returns the record instance schema, and `getWriter()` creates a `SpecificDatumWriter`.

There is no local mutable state beyond the inherited per-serializer reader/writer/stream state. Reader construction assumes the generated class is instantiable with a public no-argument constructor.

## Dependencies and integration points

It depends on Avro `SpecificRecord`, `SpecificDatumReader`, and `SpecificDatumWriter`, and it is included in the default `SerializationFactory` list before reflect serialization so generated Avro records use the specific path.

## Risks and test signals

`Class.newInstance()` can fail for generated classes without accessible no-arg constructors, and failures are wrapped in `RuntimeException`. Schema evolution is not handled locally; the record schema is the writer/reader basis. `TestAvroSerialization.testSpecific()` is the focused signal.
