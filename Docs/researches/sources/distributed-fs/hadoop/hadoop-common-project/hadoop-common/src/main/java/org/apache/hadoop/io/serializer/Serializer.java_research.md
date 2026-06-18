# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Serializer.java

## Purpose

`Serializer<T>` is Hadoop's small stateful contract for writing typed objects to an `OutputStream`. It abstracts concrete encodings such as Writable and Avro while letting callers obtain implementations through `SerializationFactory`.

## Important APIs, control flow, and state

The interface exposes `open(OutputStream)`, `serialize(T)`, and `close()`. Implementations are expected to bind to an output stream in `open()`, serialize one or more objects through `serialize()`, and release/close resources in `close()`. The class comment states that serializers are stateful but must not buffer output because other producers may write to the same stream between serialize calls.

There is no local persistence or code flow beyond the contract. Runtime state is wholly implementation-specific, usually a wrapped `DataOutputStream`, Avro `BinaryEncoder`, or similar stream adapter.

## Dependencies and integration points

The interface is paired with `Deserializer<T>` and implemented by `WritableSerialization.WritableSerializer` and `AvroSerialization.AvroSerializer` in this work item. It is consumed through `Serialization<T>.getSerializer()` and `SerializationFactory.getSerializer()`.

## Risks and test signals

The key risk is lifecycle misuse: serializing before `open()`, reusing after `close()`, or buffering in a way that violates stream interleaving assumptions. Test signals come from concrete implementation tests such as `TestWritableSerialization`, `TestAvroSerialization`, and factory lookup tests.
