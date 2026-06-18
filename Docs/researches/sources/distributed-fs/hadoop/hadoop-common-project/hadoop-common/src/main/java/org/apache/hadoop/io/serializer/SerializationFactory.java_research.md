# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/SerializationFactory.java

## Purpose

`SerializationFactory` is the configurable selector for Hadoop's `Serialization` implementations. It reads `io.serializations` from a `Configuration`, instantiates each configured class, and returns the first implementation whose `accept(Class<?>)` method matches a requested type. The default stack is `WritableSerialization`, `AvroSpecificSerialization`, and `AvroReflectSerialization`, which makes legacy Hadoop `Writable` types and Avro records available without explicit configuration.

## Important APIs, control flow, and state

The constructor calls `conf.getTrimmedStrings(CommonConfigurationKeys.IO_SERIALIZATIONS_KEY, defaults)` and invokes private `add()` for each class name. `add()` uses `Configuration.getClassByName()` and `ReflectionUtils.newInstance()` so custom serialization classes receive the same configuration through Hadoop's configurable instantiation path. `getSerializer(Class<T>)` and `getDeserializer(Class<T>)` are thin wrappers over `getSerialization(Class<T>)`, which scans the `serializations` list in order and returns the first match.

The only persistent state is the in-memory ordered `List<Serialization<?>>`. Ordering matters because broad serializers can shadow later serializers. Missing serialization class names are logged as warnings and skipped, so a bad optional serializer does not prevent the factory from being usable for later entries.

## Dependencies and integration points

The factory integrates with `DefaultStringifier`, `SequenceFile`, `ReflectionUtils.copy()`, and tests under `org.apache.hadoop.io.serializer`. It depends on `CommonConfigurationKeys.IO_SERIALIZATIONS_KEY`, the `Serialization` interface family, Avro serializers, `WritableSerialization`, and `ReflectionUtils`.

## Risks and test signals

Risks are mostly configuration and ordering related: invalid class names are silent beyond logging, unchecked casts assume configured classes really implement `Serialization`, and a broad `accept()` implementation can capture types intended for a later serializer. `TestSerializationFactory` covers unset, empty, invalid, trimmed, serializer, and deserializer lookup behavior; `TestWritableName`, `DefaultStringifier`, and `SequenceFile` tests exercise downstream integrations.
