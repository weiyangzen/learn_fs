# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroReflectSerialization.java

## Purpose

`AvroReflectSerialization` is the Hadoop `Serialization` implementation for Avro reflect types. It accepts classes that either implement `AvroReflectSerializable` or live in a configured package list under `avro.reflect.pkgs`.

## Important APIs, control flow, and state

`accept(Class<?>)` lazily initializes a synchronized `Set<String>` of configured package names, then checks the marker interface or the class package name. `getReader(Class<Object>)` creates a `ReflectDatumReader`, `getWriter(Class<Object>)` creates a `ReflectDatumWriter`, and `getSchema(Object)` uses `ReflectData.get().getSchema(t.getClass())`.

The only mutable state is the cached package set. It is initialized once per serialization instance and is not refreshed if the configuration changes after first use.

## Dependencies and integration points

It extends `AvroSerialization<Object>` and depends on Avro reflect classes: `ReflectData`, `ReflectDatumReader`, and `ReflectDatumWriter`. It is part of `SerializationFactory` defaults after `WritableSerialization` and `AvroSpecificSerialization`.

## Risks and test signals

Package matching is exact and uses trimmed configured names; subpackages are not automatically included unless listed. Primitive or array classes may have no package, so `accept()` safely guards `c.getPackage() != null`. Runtime exceptions wrap Avro reader construction failures. `TestAvroSerialization` covers reflect package configuration, primitive/array accept handling, inner classes, and marker-based reflect round trips.
