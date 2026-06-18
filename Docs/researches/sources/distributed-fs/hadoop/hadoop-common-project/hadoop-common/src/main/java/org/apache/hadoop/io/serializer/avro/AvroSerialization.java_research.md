# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroSerialization.java

## Purpose

`AvroSerialization<T>` is the abstract base for Hadoop Avro-backed serializations. Subclasses provide schema, datum reader, and datum writer creation; the base class supplies Hadoop `Serializer<T>` and `Deserializer<T>` implementations around Avro binary encoders and decoders.

## Important APIs, control flow, and state

The abstract hooks are `getSchema(T)`, `getWriter(Class<T>)`, and `getReader(Class<T>)`. `getSerializer()` creates an inner `AvroSerializer`, which stores a `DatumWriter`, opens a `BinaryEncoder` with `EncoderFactory.get().binaryEncoder(out, encoder)`, sets the writer schema for each object, and writes the object. `close()` flushes the encoder and closes the original output stream. `getDeserializer()` creates an inner `AvroDeserializer`, which opens a `BinaryDecoder` with `DecoderFactory`, then reads into a supplied or new object via `DatumReader.read(t, decoder)`.

Mutable state is per serializer/deserializer instance: datum writer/reader, encoder/decoder, and underlying stream. `AVRO_SCHEMA_KEY` is a public private-audience constant but this base class does not itself store schemas in configuration or stream headers.

## Dependencies and integration points

Subclasses in this work item are `AvroSpecificSerialization` and `AvroReflectSerialization`. It depends on Avro `Schema`, `DatumReader`, `DatumWriter`, binary factories, and Hadoop's serializer interfaces.

## Risks and test signals

The binary stream contains data but no Hadoop-managed schema envelope, so reader/writer schema compatibility must come from the subclass and caller. Closing closes caller streams. `serialize()` sets schema per object, which supports dynamic reflected classes but can be expensive. `TestAvroSerialization` verifies specific and reflect round trips and class acceptance behavior.
