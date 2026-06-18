# subset-b-007360 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/SerializationFactory.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/SerializationFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Serializer.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/Serializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/WritableSerialization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/WritableSerialization.java

## Purpose

`WritableSerialization` adapts Hadoop's `Writable` interface into the generic serializer/deserializer framework. It accepts any class assignable to `Writable` and delegates binary encoding to `Writable.write(DataOutput)` and decoding to `Writable.readFields(DataInput)`.

## Important APIs, control flow, and state

`accept(Class<?>)` returns `Writable.class.isAssignableFrom(c)`. `getSerializer()` creates a `WritableSerializer`, whose `open()` wraps the target stream in a `DataOutputStream` if needed, `serialize()` calls `w.write(dataOut)`, and `close()` closes the wrapped output. `getDeserializer()` creates a `WritableDeserializer`, which stores the target class and configuration. Its `deserialize(Writable w)` reuses the supplied instance when non-null or constructs a fresh instance with `ReflectionUtils.newInstance(writableClass, getConf())`, then calls `readFields(dataIn)`.

Mutable state is per serializer/deserializer instance: the bound data stream and, for deserialization, the target `Class<?>`. There is no persistent data beyond bytes written to caller-provided streams.

## Dependencies and integration points

The class depends on `Writable`, `DataInputStream`, `DataOutputStream`, `Configured`, and `ReflectionUtils`. It is the first default serialization in `SerializationFactory`, so it is the dominant path for Hadoop IPC and file formats that exchange `Writable` values.

## Risks and test signals

Closing closes the underlying stream, which is correct for the interface but important for callers sharing streams. Deserialization requires a no-argument constructible writable unless an instance is supplied. Reusing an instance means old fields must be fully overwritten by `readFields()`. `TestWritableSerialization` covers round-trip behavior, configurable writables, and interaction with Java serialization for `WritableComparator`; `TestSerializationFactory` validates lookup through the factory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/WritableSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroReflectSerializable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroReflectSerializable.java

## Purpose

`AvroReflectSerializable` is a marker interface. Classes implement it to opt into Hadoop's Avro reflect serializer without relying on package-level configuration.

## Important APIs, control flow, and state

The interface declares no methods and has no state. Its only behavior is via `AvroReflectSerialization.accept(Class<?>)`, which returns true for classes assignable to this interface.

## Dependencies and integration points

The integration point is `AvroReflectSerialization`, which uses this marker together with `avro.reflect.pkgs`. It is public and evolving so external classes can use it as a stable opt-in signal for Hadoop's serialization framework.

## Risks and test signals

The marker gives broad reflective serialization privileges to a class. Classes still need to be compatible with Avro reflect schema generation. Test coverage is indirect through `TestAvroSerialization.testReflect()` and related reflect package and inner-class tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroReflectSerializable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroReflectSerialization.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroReflectSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroSerialization.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroSpecificSerialization.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/serializer/avro/AvroSpecificSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/WrappedIO.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/WrappedIO.java

## Purpose

`WrappedIO` is a public, unstable, reflection-friendly facade over newer Hadoop filesystem APIs. It lets downstream libraries compile against older Hadoop versions while dynamically invoking APIs such as bulk delete, `openFile()`, path/stream capabilities, enclosing roots, and positioned ByteBuffer reads when available.

## Important APIs, control flow, and state

All methods are static and the class has no mutable state. Bulk delete methods create a `BulkDelete` from a `FileSystem`, use try-with-resources, and convert checked IO exceptions to `UncheckedIOException` through `FunctionalIO.uncheckIOExceptions()`. Capability probes call `PathCapabilities.hasPathCapability()` or `StreamCapabilities.hasCapability()`, returning false for IO failures or non-capable objects. `fileSystem_openFile()` configures a `FutureDataInputStreamBuilder` with read policy, file status, length, and arbitrary options, then blocks on `FutureIO.awaitFuture(builder.build())`. `byteBufferPositionedReadable_readFully()` requires `ByteBufferPositionedReadable`; availability recursively unwraps `FSDataInputStream` and checks `StreamCapabilities.PREADBYTEBUFFER`.

## Dependencies and integration points

The dynamic counterpart is `DynamicWrappedIO`, which loads these static methods through `DynMethods`. Filesystem contract tests and external storage libraries use this layer to access cloud-optimized open options and bulk delete without hard linkage to newer APIs.

## Risks and test signals

The wrapper intentionally maps some checked IO failures to unchecked exceptions or false capability probes, so callers must understand which errors are observable. Bulk delete is non-atomic and idempotence can delete newly recreated objects under retried paths. ByteBuffer availability depends both on interface type and capability declaration. `TestWrappedIO` covers class resolution, method lookup, open-file behavior, ByteBuffer positioned reads, filesystem IO statistics access, and missing-class fallback behavior; bulk delete contract tests exercise the delete wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/WrappedIO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/WrappedStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/WrappedStatistics.java

## Purpose

`WrappedStatistics` is the reflection-friendly facade over Hadoop `IOStatistics`, `IOStatisticsSnapshot`, and `IOStatisticsContext` APIs. It exposes only static methods and uses broad `Object`/`Serializable` signatures so callers can use reflection without linking directly to every statistics type.

## Important APIs, control flow, and state

The class provides type probes, snapshot creation and retrieval, JSON and filesystem load/save, map extraction for counters/gauges/minimums/maximums/means, thread context get/set/reset/snapshot/aggregate, and pretty string conversion. Most snapshot operations validate with private `requireIOStatisticsSnapshot()` and then invoke `applyToIOStatisticsSnapshot()`. `iostatisticsSnapshot_retrieve()` delegates to `IOStatisticsSupport.retrieveIOStatistics()` and returns null when no statistics are available. Context operations use `IOStatisticsContext.getCurrentIOStatisticsContext()` and `setThreadIOStatisticsContext()`.

The class has no local state. Persistence is explicit when snapshot JSON is saved through `IOStatisticsSnapshot.serializer().save()` or loaded back from a filesystem/path.

## Dependencies and integration points

`DynamicWrappedStatistics` loads this class reflectively. The facade depends on Hadoop filesystem statistics classes, `FunctionRaisingIOE`, `Tuples`, preconditions, and IO statistics logging/support helpers.

## Risks and test signals

Because arguments are intentionally loose, wrong types raise `IllegalArgumentException` or `ClassCastException` depending on the method. Null snapshot handling is not uniform: retrieval can return null, while many snapshot accessors require a real `IOStatisticsSnapshot`. Thread context APIs affect thread-local or inherited execution behavior, so tests must isolate contexts. `TestWrappedStatistics` covers snapshot creation, null and wrong-type inputs, JSON and local save/load, context interaction, metric extraction, missing reflected methods, and casting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/WrappedStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/DynamicWrappedIO.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/DynamicWrappedIO.java

## Purpose

`DynamicWrappedIO` is the dynamic binding layer for `WrappedIO`. It locates the wrapper class and selected static methods at runtime using Hadoop's `DynMethods`, then exposes typed methods that either invoke the bound API or fall back to older behavior.

## Important APIs, control flow, and state

Construction loads `org.apache.hadoop.io.wrappedio.WrappedIO`, sets `loaded`, and binds methods for bulk delete, `fileSystem_openFile`, path and stream capability probes, and ByteBuffer positioned reads. `requireAllMethodsAvailable()` is a test helper. Public methods call `checkAvailable()` when the API is mandatory, `available()` when false fallback is acceptable, and `extractIOEs()` to surface checked IO failures from reflective invocation. `openFile()` uses the singleton instance; `openFileOnInstance()` prefers reflected `fileSystem_openFile()` with read policies and file status, otherwise calls classic `fs.open(path)`.

State is immutable after construction: the loaded flag and unbound method handles. The singleton `INSTANCE` gives callers a shared default binding.

## Dependencies and integration points

This class integrates downstream storage code with `WrappedIO` and is tested under `TestWrappedIO` and bulk-delete contract tests. It depends on `BindingUtils`, `DynMethods`, `FileSystem`, `FileStatus`, `FSDataInputStream`, `Path`, and `ByteBuffer`.

## Risks and test signals

Method signatures must match exactly. A notable risk is the binding for `byteBufferPositionedReadable_readFullyAvailable`: the wrapped method returns `boolean`, while this class loads it with `Void.class`, so method availability depends on `BindingUtils` behavior around primitive/boxed return matching and should be covered by `testAllMethodsFound()` and `testByteBufferPositionedReadable()`. Missing classes or methods intentionally degrade to false/unavailable or classic `open()`, but mandatory invocations throw `UnsupportedOperationException`. Reflection can also wrap runtime exceptions, so IO extraction tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/DynamicWrappedIO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/DynamicWrappedStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/DynamicWrappedStatistics.java

## Purpose

`DynamicWrappedStatistics` dynamically binds the static methods in `WrappedStatistics` so libraries can use IO statistics features when present and degrade when absent.

## Important APIs, control flow, and state

The constructor loads `org.apache.hadoop.io.wrappedio.WrappedStatistics` and binds methods for type probes, IOStatisticsContext operations, snapshot creation/aggregation/retrieval/load/save/JSON conversion, metric map extraction, and pretty printing. `ioStatisticsAvailable()` and `ioStatisticsContextAvailable()` check representative bindings. Most public operations either return false when unavailable for probes or call `checkIoStatisticsAvailable()`/`checkIoStatisticsContextAvailable()` before invoking the reflected method.

The object stores only the immutable loaded flag and method handles. It has no singleton; callers instantiate it as needed, including with alternate class names for tests.

## Dependencies and integration points

It depends on `DynMethods`, `BindingUtils`, `IOStatistics`, `IOStatisticsSource`, `FileSystem`, `Path`, and `Serializable`. It is the dynamic counterpart to `WrappedStatistics` and is used heavily by `TestWrappedStatistics`.

## Risks and test signals

Return type and parameter signatures must stay synchronized with `WrappedStatistics`. Some accessors such as `iostatistics_counters()` do not check availability before invocation, so callers should probe before use or expect reflective unavailable failures. Type looseness means errors may appear as `ClassCastException`, `IllegalArgumentException`, `UncheckedIOException`, or `UnsupportedOperationException` depending on the target method. Tests cover loaded and missing classes, missing context methods, snapshot serialization, context aggregation, statistics extraction, and casting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/DynamicWrappedStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.io.wrappedio.impl` as implementation and testing support for wrapped IO.

## Important APIs, control flow, and state

It contains no executable code or state. It applies `@InterfaceAudience.LimitedPrivate("testing")` and `@InterfaceStability.Unstable` to the implementation package.

## Dependencies and integration points

The package contains `DynamicWrappedIO` and `DynamicWrappedStatistics`, which are used by tests and compatibility callers. The descriptor depends only on Hadoop classification annotations.

## Risks and test signals

The risk is API expectation drift: classes in this package are not promised as stable public APIs even though they are useful for compatibility tests. Package-level annotation behavior is indirectly validated by compilation and javadoc/classification checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/package-info.java

## Purpose

This package descriptor defines the role of `org.apache.hadoop.io.wrappedio`: dynamic access to filesystem operations absent from older Hadoop releases.

## Important APIs, control flow, and state

It contains no runtime logic or state. The documentation states that public classes in the package export methods to be loaded by reflection and that tests should use reflection to guarantee the compatibility surface remains stable.

## Dependencies and integration points

The package holds `WrappedIO` and `WrappedStatistics`. It is annotated `@InterfaceAudience.Public` and `@InterfaceStability.Evolving`, so it is a deliberate public compatibility layer rather than a private helper.

## Risks and test signals

The main risk is changing method names or signatures and breaking reflection clients. `TestWrappedIO` and `TestWrappedStatistics` explicitly check method resolution and missing-method behavior, which are the right package-level signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/AlignmentContext.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/AlignmentContext.java

## Purpose

`AlignmentContext` is an IPC extension point for carrying state identifiers between Hadoop RPC clients and servers. It lets implementations reject or coordinate calls when client and server state are too far apart.

## Important APIs, control flow, and state

The interface defines server-to-client response state methods (`updateResponseState`, `receiveResponseState`), client-to-server request state methods (`updateRequestState`, `receiveRequestState`), `getLastSeenStateId()`, and `isCoordinatedCall(protocolName, method)`. Implementations own all state; this interface only specifies where request and response protobuf headers are updated or inspected.

## Dependencies and integration points

It uses `RpcRequestHeaderProto` and `RpcResponseHeaderProto`. `Client` attaches an alignment context to each call, passes it to `ProtoUtil.makeRpcRequestHeader()`, and updates it when a successful response arrives. `Server` and protobuf RPC engines expose builders and server construction paths that accept an alignment context.

## Risks and test signals

Incorrect implementation can cause stale reads, unnecessary rejections, or inconsistent client state. `receiveRequestState()` can throw `IOException`, so server request admission paths must handle alignment failures. Test signals should cover header field propagation, threshold-based rejection, successful response state updates, and coordinated versus uncoordinated methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/AlignmentContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/AsyncCallLimitExceededException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/AsyncCallLimitExceededException.java

## Purpose

`AsyncCallLimitExceededException` signals that the client-side asynchronous RPC call limit has been exceeded.

## Important APIs, control flow, and state

It is a simple `IOException` subclass with a message constructor and `serialVersionUID`. `Client.checkAsyncCall()` throws it when asynchronous mode is enabled and `asyncCallCounter.incrementAndGet()` exceeds `ipc.client.async.calls.max`.

## Dependencies and integration points

It integrates directly with `Client` asynchronous RPC mode. Application code can catch it as an `IOException` and drain or wait for outstanding async responses before issuing more calls.

## Risks and test signals

`Client.checkAsyncCall()` increments before throwing, and the caller's catch path releases the async call only when async call checking is enabled. Tests should verify counter accounting at limit boundaries, exception type propagation through async callers, and recovery after completing outstanding futures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/AsyncCallLimitExceededException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CallQueueManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CallQueueManager.java

## Purpose

`CallQueueManager<E extends Schedulable>` abstracts Hadoop IPC server call queue operations across different `BlockingQueue` and `RpcScheduler` implementations. It supports priority-aware queues, client backoff, failover-triggering overflow exceptions, and live queue replacement.

## Important APIs, control flow, and state

The constructor parses scheduler priority levels and capacity weights, creates a scheduler via reflection, creates a backing queue via reflection, and stores two atomic queue references: `putRef` for producers and `takeRef` for handlers. Queue operations delegate to those refs. `put()` honors client backoff by consulting `scheduler.shouldBackOff()`, while `addInternal()` converts full-queue `IllegalStateException` into `CallQueueOverflowException.DISCONNECT` or `.FAILOVER` depending on failover configuration. `getPriorityLevel()`, `addResponseTime()`, and user-level priority setters delegate to the scheduler, with special handling for `DecayRpcScheduler`.

`swapQueue()` is the key state transition. It stops the old scheduler, creates the new scheduler and queue, updates server failover config, switches `putRef` first so new calls go to the replacement queue, waits until the old queue is repeatedly empty, then switches `takeRef` and installs the new scheduler.

## Dependencies and integration points

It is used by `Server` as the IPC call admission queue. It integrates with `FairCallQueue`, `RpcScheduler`, `DecayRpcScheduler`, `Schedulable`, `UserGroupInformation`, `CommonConfigurationKeys`, `RetriableException`, `StandbyException`, and `RpcServerException`.

## Risks and test signals

The two-reference swap prevents losing calls but can spin while waiting for old queue drain; interrupted sleeps make the empty check fail and retry. Reflection constructor selection must match queue/scheduler signatures. Overflow behavior changes client outcome: keepalive/error, disconnect/fatal, or failover/fatal. Capacity weights must match priority levels and be positive. `TestCallQueueManager` covers capacity, empty consumption, FCQ compatibility, scheduler-without-FCQ, swap under contention, constructor exceptions, overflow exceptions, and failover enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CallQueueManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CallerContext.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CallerContext.java

## Purpose

`CallerContext` is an immutable auditing context attached to Hadoop RPC calls. It carries a context string and optional signature so servers can log coarse-grained caller information.

## Important APIs, control flow, and state

The immutable object stores `context` and a defensive-copy `signature`. `isContextValid()` requires a non-empty context. `toString()` renders `context` and, when present, `:` plus the UTF-8 signature. Equality includes both context and signature, while `hashCode()` only includes context through `HashCodeBuilder`.

The nested `Builder` appends raw fields, key/value fields, or key/value only if absent. It validates the field separator against tab, newline, and equals. The current context is held in an `InheritableThreadLocal` via holder idiom methods `getCurrent()` and `setCurrent()`.

## Dependencies and integration points

Caller context is serialized in RPC headers (`RPCCallerContextProto`) and reconstructed in `Server`. Constants define common audit field names such as client IP, port, client ID, call ID, real user, and proxy user port.

## Risks and test signals

The `appendIfAbsent()` check is substring-based on `key + ":"`, so keys embedded in values could produce false positives. Signature bytes are copied on set/get, but `Builder.getSignature()` returns the builder's internal array to the private constructor, relying on builder usage discipline. Thread-local inheritance can leak context into child threads if not cleared. `TestCallerContext` covers append behavior, append-if-absent behavior, and builder construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CallerContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/Client.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/Client.java

## Purpose

`Client` is Hadoop's core writable IPC client. It multiplexes RPC `Writable` requests over reusable socket connections, handles connection setup, SASL negotiation, pings, retries, asynchronous responses, alignment context propagation, and response demultiplexing by call ID.

## Important APIs, control flow, and state

Static thread-locals carry explicit call IDs, retry counts, external handlers, async response futures, and asynchronous mode. Each `Client` has a generated UUID-style `clientId`, a `ConcurrentMap<ConnectionId, Connection>`, `putLock` to prevent new connections after stop, `emptyCondition` for shutdown, socket factory, response value class, configuration, reference count, and async call counter/limit.

`call()` creates a `Call`, attaches any `AlignmentContext`, obtains or creates a `Connection`, checks async limits, serializes and queues the request, and either returns a synchronous response from `CompletableFuture.get()` or stores a handled async future in `ASYNC_RPC_RESPONSE`. Failures are wrapped with remote address context unless they are already `RemoteException` or `SaslException`.

`Connection` owns the socket, `IpcStreams`, active call table, retry policy, auth protocol, ping settings, receiver thread, and a separate request-sender thread connected by a fair `SynchronousQueue`. Setup resolves DNS changes, creates sockets with TCP options, optionally binds Kerberos clients to a local address, connects with retry policy, writes the Hadoop RPC header, negotiates SASL, wraps streams, writes the connection context, starts the receiver, and then sends serialized call buffers through the sender thread. The receiver reads length-prefixed response buffers, validates client IDs, removes matching calls, updates alignment state on success, completes futures, or closes the connection on fatal errors. Shutdown interrupts receiver/sender/connecting threads, closes streams and SASL state, removes the connection conditionally from the map, and completes outstanding calls exceptionally.

`ConnectionId` is the pool key over address, protocol, UGI ticket, timeout, retry policy, ping, idle time, and TCP options. Its hash uses hostname and port rather than resolved IP so `setAddress()` can update DNS changes without changing the map key hash.

## Dependencies and integration points

`Client` is used by `ProtobufRpcEngine`, `ProtobufRpcEngine2`, and `ClientCache`. It integrates with `Server` wire protocol constants, `RpcWritable`, `ProtoUtil`, `SaslRpcClient`, `UserGroupInformation`, `RetryPolicy`, tracing spans, `NetUtils`, `CallerContext` indirectly through server headers, and `AlignmentContext`.

## Risks and test signals

Concurrency is the main risk: active calls must be inserted before setup, request sending must avoid partial socket writes on caller interruption, and connection removal must be conditional so a newer replacement is not removed. Async call counting must decrement on completion and on send/setup failures; exceeding the limit throws `AsyncCallLimitExceededException`. Response handling assumes a success header has a matching call; unexpected or duplicate call IDs could cause null dereference. SASL fallback must reject SIMPLE fallback when security requires it. `IpcStreams.readResponse()` enforces positive and maximum response length and handles pre-rpcv9 errors. Existing broader IPC tests, `ClientCache` usage in RPC engines, async RPC tests, SASL tests, and alignment-context integration tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/Client.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ClientCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ClientCache.java

## Purpose

`ClientCache` provides shared `Client` instances keyed by `SocketFactory` for Hadoop RPC engines. It avoids creating independent connection pools for every proxy while reference counting users.

## Important APIs, control flow, and state

The cache stores `Map<SocketFactory, Client>`. `getClient(conf, factory, valueClass)` is synchronized: it creates a `Client` if absent or increments the existing client's ref count, then returns it. Convenience overloads use the default socket factory and `ObjectWritable` response class. `stopClient(Client)` decrements the client ref count under the cache lock, removes it when count reaches zero, and then calls `client.stop()` outside the lock. `clearCache()` stops all cached clients and clears the map for tests.

## Dependencies and integration points

`ProtobufRpcEngine` and `ProtobufRpcEngine2` use this cache for client reuse. It depends on `Client`, `SocketFactory`, `ObjectWritable`, `Writable`, and Hadoop configuration.

## Risks and test signals

The key excludes `Configuration` and response `valueClass`, so the first client created for a socket factory controls timeouts and value class for later users. The comment calls out the tradeoff: reuse connection pools while accepting global-ish IPC configuration. Clear-cache is unsynchronized, so it should remain test-only or externally serialized. RPC engine lifecycle tests and client reference count tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ClientCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ClientId.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ClientId.java

## Purpose

`ClientId` provides UUID-based 16-byte identifiers for IPC clients and conversion helpers between byte arrays and canonical UUID strings.

## Important APIs, control flow, and state

`getClientId()` generates a random UUID and writes its most and least significant bits into a 16-byte array. `toString(byte[])` returns empty string for null/empty arrays, validates length 16 otherwise, reconstructs MSB/LSB with big-endian byte shifting, and returns `UUID.toString()`. `toBytes(String)` returns empty bytes for null/empty strings or parses the UUID string into a 16-byte array. `getMsb()` and `getLsb()` expose the big-endian halves for retry cache integration.

The class is stateless.

## Dependencies and integration points

`Client` uses it to generate client IDs. `RetryCache` uses the 16-byte constraint and MSB/LSB helpers. Server response headers echo client IDs for validation.

## Risks and test signals

Only null or zero-length IDs are treated as empty; any non-empty non-16-byte array fails precondition checks. `toBytes()` relies on `UUID.fromString()` and will throw for invalid strings. Tests should check round trips, empty handling, byte-order stability, and retry-cache key compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ClientId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CostProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CostProvider.java

## Purpose

`CostProvider` is the pluggable cost model used by `DecayRpcScheduler` to convert `ProcessingDetails` into a numeric scheduling cost.

## Important APIs, control flow, and state

The interface defines `init(String namespace, Configuration conf)` and `getCost(ProcessingDetails details)`. Implementations decide whether cost is constant, weighted by queue/lock/processing time, or based on other timing details.

## Dependencies and integration points

`DecayRpcScheduler.parseCostProvider()` loads implementations from `ipc.cost-provider.impl` or port-scoped variants, initializes the selected provider, and calls `getCost()` for completed calls in `addResponseTime()`. `DefaultCostProvider` is the fallback.

## Risks and test signals

Bad cost providers can starve users, overflow counters, or return zero/negative costs that change scheduler behavior. Tests should cover provider loading, namespace fallback, weighted providers, zero-cost calls, and no-request windows; `TestDecayRpcScheduler` includes weighted-cost provider cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CostProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DecayRpcScheduler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DecayRpcScheduler.java

## Purpose

`DecayRpcScheduler` is a priority scheduler for Hadoop IPC. It tracks per-identity call cost, periodically decays historical cost, and maps heavier users to lower-priority queues. It also exports scheduler metrics and can optionally trigger client backoff based on queue response times.

## Important APIs, control flow, and state

Construction validates priority levels, parses decay factor, period, thresholds, identity provider, cost provider, service users, response-time backoff settings, and top-user metric count. It initializes atomic arrays for current and previous response time windows, creates detailed metrics, schedules a daemon `TimerTask`, registers a namespace-specific `MetricsProxy`, and computes the initial scheduling cache.

Completed calls flow through `addResponseTime()`: the identity provider extracts a user identity, the cost provider computes cost from `ProcessingDetails`, `addCost()` updates decayed/raw per-user counters and totals, detailed metrics record queue and processing time, and current-window response arrays are updated. Periodically `decayCurrentCosts()` multiplies each decayed cost by the decay factor, removes zero-cost identities, recomputes total decayed/raw cost split by service users, swaps an unmodifiable scheduling cache, and updates response-time averages. `getPriorityLevel()` uses the cache or computes a level from identity cost divided by total decayed non-service-user cost. Service users always map to priority 0; test-visible static priorities can override computed levels.

Metrics are exposed through `DecayRpcSchedulerMXBean` and `MetricsSource`: scheduling decisions, decayed call volumes, unique identities, top callers, response times, raw/service-user totals, and detailed per-priority metrics. `stop()` unregisters the metrics proxy and shuts down detailed metrics.

## Dependencies and integration points

It is created by `CallQueueManager` and intended to work with `FairCallQueue`. It depends on `IdentityProvider`, `CostProvider`, `ProcessingDetails`, `DecayRpcSchedulerDetailedMetrics`, Metrics2, MBeans, Jackson JSON, `UserGroupInformation`, and `RpcMetrics` time-unit configuration.

## Risks and test signals

All identities are treated as strings in service-user checks; custom providers returning non-string identities would break casts. Threshold count must be `numLevels - 1`; response-time threshold count must be `numLevels`. The decay timer is daemon and uses a weak reference, but explicit `stop()` is still needed to unregister metrics. `MetricsProxy.getInstance()` replaces delegates for the same namespace, so multiple schedulers under one namespace share a proxy. Backoff checks lower-or-equal priority indexes up to the caller's level and may reject lower-priority calls when high-priority response times exceed thresholds. `TestDecayRpcScheduler` covers invalid levels, parsing period/factor/thresholds, accumulation, decay, priority, periodic decay, initialization NPE prevention, weighted cost providers, zero-cost/no-request cases, and service users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DecayRpcScheduler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DecayRpcSchedulerMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DecayRpcSchedulerMXBean.java

## Purpose

`DecayRpcSchedulerMXBean` is the JMX management contract for `DecayRpcScheduler` metrics.

## Important APIs, control flow, and state

The interface exposes scheduling decision JSON, call-volume JSON, unique identity count, total call volume, average response time per priority, and completed response counts from the last window. It has no implementation state.

## Dependencies and integration points

`DecayRpcScheduler` implements it directly, and `DecayRpcScheduler.MetricsProxy` registers an MBean per namespace while delegating to the active scheduler through a weak reference.

## Risks and test signals

The JSON-returning methods can return error strings when serialization fails, so JMX clients should not assume valid JSON unconditionally. Proxy default values are returned when the delegate is gone. `TestDecayRpcScheduler` and metrics2 tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DecayRpcSchedulerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DefaultCostProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DefaultCostProvider.java

## Purpose

`DefaultCostProvider` is the fallback cost model for `DecayRpcScheduler`. It assigns every completed call a constant cost of 1.

## Important APIs, control flow, and state

`init()` is a no-op. `getCost(ProcessingDetails)` ignores the details and returns 1. The class has no mutable state.

## Dependencies and integration points

`DecayRpcScheduler.parseCostProvider()` returns this provider when no configured provider is found. It depends only on `Configuration` and `ProcessingDetails` through the `CostProvider` interface.

## Risks and test signals

Constant cost treats all RPC methods equally regardless of lock, queue, or processing time. This is simple and predictable but can underweight expensive operations. `TestDecayRpcScheduler` default accumulation/decay/priority tests implicitly cover this provider; weighted provider tests cover the alternative path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DefaultCostProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DefaultRpcScheduler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DefaultRpcScheduler.java

## Purpose

`DefaultRpcScheduler` is a no-op scheduler implementation used when priority scheduling is disabled or unnecessary.

## Important APIs, control flow, and state

`getPriorityLevel()` always returns 0, `shouldBackOff()` always returns false, `addResponseTime()` does nothing, `stop()` does nothing, and the constructor ignores priority levels, namespace, and configuration. There is no state.

## Dependencies and integration points

It implements `RpcScheduler` and can be constructed reflectively by `CallQueueManager` using the `(int, String, Configuration)` signature.

## Risks and test signals

All calls share one priority level from the scheduler's perspective, so any priority queue beneath it receives no scheduler-driven differentiation. `TestCallQueueManager.testSchedulerWithoutFCQ()` and server default queue configurations are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DefaultRpcScheduler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ExternalCall.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ExternalCall.java

## Purpose

`ExternalCall<T>` adapts a `PrivilegedExceptionAction<T>` into a `Server.Call` so work initiated outside the normal RPC request path can run through IPC handler and response machinery.

## Important APIs, control flow, and state

The class stores an action, an `AtomicBoolean done`, result, and error. Subclasses provide `getRemoteUser()`. `run()` executes the action, stores the result, and calls `sendResponse()`, or calls `abortResponse(t)` on failure. Completion is signaled through overridden `doResponse(Throwable, RpcStatusProto)`, which records any error, sets `done`, and notifies waiters. `get()` waits until completion and returns the result or throws `ExecutionException`.

## Dependencies and integration points

It extends `Server.Call`, uses `RpcStatusProto`, and depends on `UserGroupInformation`. It is intended for postponed or externally triggered server-side calls that still need handler accounting and response notification.

## Risks and test signals

`waitForCompletion()` catches `InterruptedException` from `wait()` and only rethrows if `Thread.interrupted()` is true after the catch, which clears interrupt status and can make interruption handling subtle. `notify()` wakes one waiter, which matches expected single `get()` use but is not a broadcast. Since `run()` catches `Throwable`, severe errors are routed to `abortResponse()`. Tests should cover success, action failure, postponed response completion, interruption, and remote user propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ExternalCall.java -->
