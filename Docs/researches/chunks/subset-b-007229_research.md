# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 24760-31093

## Scope

This chunk is the fifth slice of the Hadoop Common 3.3.6 JDiff public API XML. It starts at the end of `org.apache.hadoop.io.SequenceFile`, then covers a large part of the public `org.apache.hadoop.io` serialization surface, the public compression codec/stream contracts under `org.apache.hadoop.io.compress`, erasure coding schema metadata, TFile helper APIs, serializer adapters, a Log4J event counter, and the early metrics2 API through the beginning of `MetricsRegistry`.

The source is generated API metadata rather than implementation code. The research therefore treats classes, methods, fields, docs, exceptions, inheritance, and interface contracts as the authoritative public compatibility surface.

## Purpose

The APIs in this chunk support Hadoop's binary data and observability foundations:

- SequenceFile and Writable APIs define Hadoop's native binary record format, primitive/value wrappers, raw comparators, variable-length integer encoding, and factories used by MapReduce, RPC, SequenceFile, MapFile, and many file formats.
- Compression APIs define how codecs create compressor/decompressor streams, how codec instances are discovered by filename or class name, how codec resources are pooled, and how splittable compression exposes adjusted split boundaries.
- TFile and serializer APIs expose lower-level sorted binary container helpers and pluggable serialization bridges for Java serialization, Writable serialization, and Avro reflection/specific serialization.
- Metrics2 APIs define the public producer/collector/sink contracts used by daemons to emit metrics records, tags, counters, gauges, JSON/string representations, filters, annotations, and a default metrics-system singleton.

## Important APIs, Types, And Functions

### SequenceFile Tail

The chunk opens with deprecated `SequenceFile.createWriter(...)` overloads for constructing writers over a `FileSystem`/`Path` or raw `FSDataOutputStream`, with key/value classes, `CompressionType`, optional `CompressionCodec`, metadata, and optional `Progressable`. The deprecation text directs callers to `createWriter(Configuration, Writer.Option...)`.

`SequenceFile.SYNC_INTERVAL` remains a public constant documenting the default sync-point spacing of 100 KB. The class documentation in this slice is especially important because it fixes the public binary format contract:

- common header fields include magic/version, key class, value class, compression booleans, codec class, metadata, and sync marker;
- uncompressed and record-compressed records store record length, key length, key bytes, and value bytes, with record compression applying only to values;
- block-compressed records group counts, compressed key-length blocks, key blocks, value-length blocks, and value blocks, with sync markers every block;
- key/value lengths in compressed blocks use zero-compressed integer encoding.

### `org.apache.hadoop.io`

This chunk covers core Writable and comparable types:

- `SetFile extends MapFile` is a file-backed key set with a protected constructor.
- `ShortWritable`, `VIntWritable`, and `VLongWritable` are mutable `WritableComparable` wrappers with constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `SortedMapWritable extends AbstractMapWritable implements SortedMap` exposes a Writable sorted map with default/copy constructors, sorted-map views (`firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`, `comparator`) and full map operations plus `readFields`/`write`.
- `Stringifier<T> extends Closeable` converts objects to and from string form through `toString(T)`, `fromString(String)`, and `close`, all allowed to raise `IOException`.
- `Text extends BinaryComparable implements WritableComparable` is Hadoop's mutable UTF-8 string type. It exposes byte ownership and length (`copyBytes`, `getBytes`, `getLength`), UTF-8 character lookup (`charAt`), substring search (`find`), multiple `set` overloads from strings, bytes, and other `Text`, append/clear, serialization helpers, static UTF-8 encode/decode/validate routines, static string read/write helpers with optional max length, `bytesToCodePoint`, `utf8Length`, and `DEFAULT_MAX_LEN`.
- `TwoDArrayWritable` serializes a two-dimensional array of a configured `Writable` value class through `set`, `get`, `toArray`, `readFields`, and `write`.
- `VersionedWritable` writes and reads a version byte around a Writable payload. Subclasses override `getVersion`; `VersionMismatchException` reports expected versus found versions.
- `Writable` is the base binary serialization interface with `write(DataOutput)` and `readFields(DataInput)`. Its docs define the reuse contract: deserialization should overwrite existing object state.
- `WritableComparable<T>` combines `Writable` and `Comparable<T>` for keys that can be serialized and sorted.

Comparator and factory helpers are also public:

- `WritableComparator implements RawComparator, Configurable` provides registry lookup (`get`), registry override (`define`), key construction (`newKey`), object and raw-byte comparison, byte hashing, primitive reads from byte arrays, and variable-length integer reads. Constructors allow key class, configuration, and instance creation behavior.
- `WritableFactories` registers optional `WritableFactory` instances and creates `Writable` objects through registered factories or reflection.
- `WritableFactory` exposes `newInstance()`.
- `WritableUtils` supplies compressed byte-array/string IO, string arrays, cloning through serialization, variable-length integer and long encoding/decoding, range-checked VInt reads, enum read/write, `skipFully`, `toByteArray`, and `readStringSafely`.

### `org.apache.hadoop.io.compress`

The compression package exposes three related layers: codec discovery, codec contracts, and stream/compressor state machines.

Codec discovery and constants:

- `CodecConstants` publishes standard filename extensions for default, bzip2, gzip, lz4, passthrough, snappy, and zstandard codecs.
- `CompressionCodecFactory` is constructed from `Configuration`; it can list and set codec classes, locate codecs by `Path`, full class name, or short name, return codec classes by name, remove suffixes, print via `toString`, and run a command-line `main`. `LOG` is a public logger field.
- `CodecPool` leases compressors/decompressors for a codec, optionally with configuration, returns them, and exposes leased compressor/decompressor counts. This is the public resource-pooling surface for native and Java codec state.

Codec and stream contracts:

- `CompressionCodec` defines output/input stream factories with and without existing `Compressor`/`Decompressor`, factory methods for compressor/decompressor types and instances, and `getDefaultExtension`.
- `SplittableCompressionCodec extends CompressionCodec` adds a split-aware `createInputStream` accepting seekable input, decompressor, start/end offsets, and `READ_MODE`, returning `SplitCompressionInputStream`.
- `DirectDecompressionCodec` and `DirectDecompressor` expose direct-buffer decompression for codecs that can bypass byte-array streams.
- `CompressionInputStream extends InputStream implements Seekable, IOStatisticsSource`; it wraps an input stream, exposes `resetState`, passthrough seek methods, position, optional new-source seeking, IO statistics, and `maxAvailableData`.
- `CompressionOutputStream extends OutputStream implements IOStatisticsSource`; it wraps an output stream and defines `finish`, `resetState`, flush/close/write behavior, and IO statistics.
- `Compressor` accepts input and optional dictionaries, reports input/output byte counts, supports `finish`/`finished`, compresses into caller buffers, resets, ends native resources, and can be reinitialized from `Configuration`.
- `Decompressor` mirrors that state machine for input, dictionaries, finished state, decompression, remaining input, reset, and native-resource cleanup.
- `CompressorStream` and `DecompressorStream` are base stream adapters with protected compressor/decompressor fields, buffers, closed/eof flags, reset/close behavior, and lower-level `compress`/`decompress` hooks.
- `BlockCompressorStream` and `BlockDecompressorStream` adapt compressors into block formats; constructors accept buffer and compression-overhead sizing, and their docs emphasize writing input lengths before compressed payloads.
- `SplitCompressionInputStream` stores adjusted split start/end offsets via setters and getters for codecs that need to align reader boundaries.

Concrete codecs in this slice:

- `DefaultCodec implements Configurable, CompressionCodec, DirectDecompressionCodec` and provides the default deflate-style streams, compressor/decompressor types, direct decompressor creation, and default extension.
- `GzipCodec extends DefaultCodec` overrides stream creation, compressor/decompressor creation and types, direct decompressor creation, and default extension.
- `BZip2Codec implements Configurable, SplittableCompressionCodec`; it supports regular and split-aware input streams, output streams with optional compressors, compressor/decompressor factories, default extension, and `writeHeader`.
- `PassthroughCodec implements Configurable, CompressionCodec`; it publishes `CLASSNAME`, `OPT_EXTENSION`, and `DEFAULT_EXTENSION`, and creates pass-through streams while still presenting the normal codec contract.

### Erasure Coding Metadata

`ECSchema implements Serializable` represents erasure coding policy schema metadata. It can be built from a map or from codec name, data-unit count, parity-unit count, and extra options. Public accessors expose codec name, extra options, number of data units, and parity units. Equality, hash code, and `toString` are part of the compatibility surface. Public map keys are `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.

The chunk also contains package markers for `org.apache.hadoop.io.erasurecode.coder.util` and `org.apache.hadoop.io.erasurecode.grouper` without public classes in this slice.

### TFile And Raw Comparison

`MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are `IOException` subclasses used by TFile metadata operations.

`RawComparable` exposes byte-array comparison material through `buffer()`, `offset()`, and `size()`.

`TFile` publishes compression and comparator names (`COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, `COMPARATOR_MEMCMP`, `COMPARATOR_JCLASS`), builds comparators from comparator names with `makeComparator`, lists supported compression algorithms, and has a command-line `main`.

`org.apache.hadoop.io.file.tfile.Utils` supplies TFile-specific variable-length integer and long encoding, string IO, and binary-search helpers `lowerBound`/`upperBound` over arrays of `RawComparable` or generic objects with comparators.

### Serialization Adapters

`JavaSerialization implements Serialization`, `WritableSerialization extends Configured implements Serialization`, and `AvroSerialization extends Configured implements Serialization` are public adapter classes for Hadoop's serialization plugin layer. Their JDiff entries in this chunk mostly expose constructors and inheritance, so the important surface is compatibility with the broader `Serialization` contract from adjacent chunks.

`JavaSerializationComparator extends DeserializerComparator` exposes a constructor for comparing Java-serialized values.

Avro support includes:

- `AvroReflectSerializable`, a marker interface for types opting into reflect serialization;
- `AvroReflectSerialization extends AvroSerialization` with `AVRO_REFLECT_PACKAGES`, a configuration property for package allow-listing;
- `AvroSpecificSerialization extends AvroSerialization`, for Avro generated/specific records;
- `AvroSerialization.AVRO_SCHEMA_KEY`, the configuration key for schema material.

### Log Metrics

`EventCounter extends org.apache.log4j.AppenderSkeleton` is a Log4J appender for counting logging events. Its public surface is the default constructor, `append(LoggingEvent)`, `close()`, and `requiresLayout()`.

### `org.apache.hadoop.metrics2`

The metrics2 surface in this chunk defines record production, collection, sink delivery, filtering, formatting, and lifecycle control:

- `AbstractMetric implements MetricsInfo`; it wraps metric metadata and exposes `name`, `description`, `info`, numeric `value`, `type`, visitor dispatch through `visit(MetricsVisitor)`, equality, hash code, and `toString`.
- `MetricsInfo` is the metadata interface with `name()` and `description()`.
- `MetricsTag implements MetricsInfo` wraps `MetricsInfo` and a string value; it exposes name/description/info/value and value-based object methods.
- `MetricsVisitor` is a visitor for typed metric values, with `gauge` overloads for int, long, float, and double, and `counter` overloads for int and long.
- `MetricsCollector` creates records by name or `MetricsInfo`, returning `MetricsRecordBuilder`.
- `MetricsRecordBuilder` is a fluent builder for tags, arbitrary metric adds, context, counters, gauges of all primitive numeric widths represented here, parent collector access, and `endRecord`.
- `MetricsRecord` is the immutable record view with timestamp, name, description, context, tags, and iterable metrics.
- `MetricsSource` emits records through `getMetrics(MetricsCollector, boolean all)`.
- `MetricsSink extends MetricsPlugin` receives records through `putMetrics(MetricsRecord)` and flushes buffered output.
- `MetricsPlugin` initializes from `SubsetConfiguration`.
- `MetricsFilter extends MetricsPlugin` exposes four acceptance checks for names, tags, record names, and full records.
- `MetricsSystem implements MetricsSystemMXBean`; it can register and unregister sources/sinks/callbacks, publish metrics immediately, and shut down. The MXBean interface exposes start/stop, start/stop metrics MBeans, and `currentConfig`.
- `MetricsException extends RuntimeException` has constructors for message, cause, and message plus cause.
- `MetricsJsonBuilder extends MetricsRecordBuilder` and `MetricStringBuilder extends MetricsRecordBuilder` format records into JSON or delimited strings while supporting the same tag/counter/gauge builder calls. `MetricStringBuilder` additionally exposes `add(String, Object)` and `tuple(String, Object)`.

Annotations and filters:

- `org.apache.hadoop.metrics2.annotation.Metric` and `Metrics` are annotation interfaces for individual metrics and groups.
- `GlobFilter` and `RegexFilter` extend `AbstractPatternFilter` and compile patterns to `com.google.re2j.Pattern`; GlobFilter is explicitly named as usable from metrics config files.

Metrics2 library classes at the end of the chunk:

- `DefaultMetricsSystem` is a singleton enum facade used by daemon processes. It exposes `initialize(prefix)`, `instance()`, `shutdown()`, `setMiniClusterMode(boolean)`, and `inMiniClusterMode()`, plus enum `values`/`valueOf`.
- `Interns` creates interned `MetricsInfo` and `MetricsTag` instances by metadata/value.
- `MetricsRegistry` starts in this chunk. It is constructed from a record name or `MetricsInfo`, exposes registry `info`, synchronized `get` and `getTag`, and creates mutable counters/gauges/stats/rates/quantiles through `newCounter`, `newGauge`, `newQuantiles`, `newStat`, and `newRate` overloads.

## Control Flow

Writable control flow is object-reuse oriented. Callers allocate a `Writable`, then repeatedly call `readFields(DataInput)` to overwrite its existing state; writers call `write(DataOutput)` to emit the current state. `VersionedWritable` adds a version byte before subclass fields and raises `VersionMismatchException` when the serialized version does not match the expected one.

`Text` control flow is byte-buffer based rather than Java `String` based. Mutators replace or append UTF-8 byte content, `charAt` and `find` scan encoded bytes, static helpers encode/decode and validate UTF-8, and bounded `readString`/`readStringSafely` protect callers from oversized serialized strings.

Raw sorting flow uses `WritableComparator`: comparators can be looked up from the static registry, constructed for a key class, and used either on already-deserialized `WritableComparable` objects or directly on serialized byte ranges. The primitive byte readers and VInt readers are support routines for comparator implementations that avoid object allocation.

Compression flow is stream and state-machine driven. A codec creates a compressor/decompressor or receives one leased from `CodecPool`; it wraps caller streams in `CompressionOutputStream` or `CompressionInputStream`; callers feed bytes through stream methods; `finish`, `finished`, `resetState`, `reset`, and `end` separate flush/completion, reuse, and native-resource cleanup. Split-aware codecs additionally adjust start/end offsets through `SplitCompressionInputStream` so distributed readers can begin at codec-safe boundaries.

Codec discovery flow starts with a `Configuration`-backed `CompressionCodecFactory`, resolves a codec from a path suffix or configured codec name/class, then optionally strips suffixes through `removeSuffix`. TFile and SequenceFile consumers depend on these discovery and extension contracts to choose readers/writers.

Metrics flow begins when sources are registered with `MetricsSystem` or `DefaultMetricsSystem`. A collector asks a `MetricsSource` for metrics; sources build one or more records through `MetricsRecordBuilder`; records carry tags and `AbstractMetric` values; sinks receive immutable `MetricsRecord` instances and flush them. Visitors and JSON/string builders provide alternate render paths. Filters accept or reject names, tags, or records before delivery.

## State And Persistence Behavior

SequenceFile, Writable, TFile, and compression streams are persistence-facing APIs. SequenceFile's documented header and record layouts are durable on-disk compatibility contracts. Writable implementations persist their fields directly to `DataOutput` and restore them from `DataInput`; changing field order, encoding, or comparator behavior breaks stored data and shuffle/sort compatibility.

Primitive Writable wrappers hold one mutable primitive value. `SortedMapWritable` persists both map content and the class-id mapping inherited from `AbstractMapWritable`. `TwoDArrayWritable` persists array dimensions and nested Writable values. `Text` maintains a mutable UTF-8 byte array and length; `getBytes()` exposes internal storage while `copyBytes()` returns a defensive copy.

`WritableFactories` and `WritableComparator` maintain process-wide registries. Factory/comparator registration changes object construction and sort behavior globally for a class, so tests and long-running daemons must avoid accidental cross-test or cross-component leakage.

Compression classes keep mutable native or heap state in compressors, decompressors, stream buffers, closed/eof flags, counters, configuration references, and codec-pool lease tables. `CodecPool` explicitly tracks leased compressors and decompressors, making failure to return resources observable through leased-count methods and potentially expensive for native codecs.

`ECSchema` is serializable metadata state: codec name, data/parity unit counts, and extra options. It is likely persisted in erasure coding policy metadata outside this XML slice, so equality and key names are compatibility-sensitive.

Metrics2 state is mostly runtime state. `MetricsRegistry` owns mutable metric and tag registries; `DefaultMetricsSystem` owns the singleton metrics system and mini-cluster mode flag; `MetricsSystem` owns registered sources, sinks, and callbacks. Metrics records are snapshots for delivery, while builders and mutable metrics are transient construction/update surfaces.

## Dependencies And Integration Points

The `org.apache.hadoop.io` APIs depend on Java IO (`DataInput`, `DataOutput`, `IOException`), Hadoop configuration, filesystem streams, `Progressable`, compression codecs, and comparator/factory registries. These APIs integrate with SequenceFile, MapFile/SetFile, TFile, MapReduce key sorting, shuffle serialization, RPC payloads, and many configuration-serialized values.

Compression APIs integrate with `Configuration`, `Path`, `Seekable`, `IOStatisticsSource`, native codec implementations, direct byte buffers, split readers, SequenceFile block/record compression, MapReduce input splitting, and TFile compression selection. `BZip2Codec` is notable because it is splittable; gzip/default codecs are normal stream codecs, with default/gzip also exposing direct decompression hooks.

Serializer adapters integrate with Hadoop's `Serialization` framework, `Configured`, Java object serialization, Writable types, and Avro reflection/specific record handling. The Avro classes depend on configuration keys to choose schema and package eligibility.

Metrics2 integrates with Apache Commons Configuration (`SubsetConfiguration`), Log4J for `EventCounter`, SLF4J loggers in formatting/factory classes, RE2J pattern compilation in filters, JMX through `MetricsSystemMXBean`, daemon startup through `DefaultMetricsSystem.initialize`, and downstream sinks configured by the metrics system.

## Risks And Compatibility Notes

- The deprecated `SequenceFile.createWriter` overloads remain public and can still be used by older callers. Compatibility must preserve their behavior while nudging new code to `Writer.Option` APIs.
- SequenceFile format details in this XML are durable. Any mismatch in sync interval, header fields, compression flags, metadata encoding, or block layout can strand existing files.
- `Text.getBytes()` exposes the backing byte array. Callers must use `getLength()` and avoid assuming unused capacity is valid string data.
- Variable-length integer encoding in `WritableUtils`, `WritableComparator`, and TFile `Utils` is shared wire-format logic. Small arithmetic changes can break deserialization, raw comparison, and binary search ordering.
- `WritableComparator.define` and `WritableFactories.setFactory` mutate global registries. Tests and embedded runtimes can become order-dependent if registrations are not isolated.
- Compression resources may hold native memory. `Compressor.end`, `Decompressor.end`, stream `close`, and `CodecPool.returnCompressor`/`returnDecompressor` are operationally significant, not just cleanup niceties.
- Split compression is contract-sensitive: incorrect adjusted start/end offsets can duplicate or drop records in distributed reads.
- `CodecPool` leased counts are a direct signal for leaks; resource leaks may not show as Java heap growth if native codec buffers are involved.
- Metrics2 builders use fluent no-op/default-style base classes in parts of the API; custom builders/sinks must implement all relevant overloads or silently lose values of some numeric type.
- `DefaultMetricsSystem` is global singleton state. Mini-cluster mode and shutdown behavior can leak between tests or embedded clusters if not reset.
- Pattern filters use RE2J, not Java's regex engine, so syntax/performance behavior follows RE2J semantics.

## Test Signals

Useful validation for code touching APIs represented by this chunk includes:

- SequenceFile round trips for uncompressed, record-compressed, and block-compressed files, including metadata, sync seeking, and old deprecated writer overloads.
- Writable serialization/deserialization compatibility tests for `ShortWritable`, `VIntWritable`, `VLongWritable`, `Text`, `SortedMapWritable`, `TwoDArrayWritable`, and `VersionedWritable` mismatch handling.
- Raw comparator tests that compare serialized byte ranges against object-level comparison for representative key classes and VInt/VLong encodings.
- Factory and comparator registry tests that verify explicit registration, default reflective construction, and isolation/reset behavior in test suites.
- Compression codec tests for stream round trips, `finish` versus `close`, reset/reuse, direct decompression, codec discovery by suffix/name/class, `CodecPool` lease counts returning to zero, and BZip2 split-boundary correctness.
- TFile utility tests for VInt/VLong encoding, string IO, comparator construction, and lower/upper-bound behavior with raw and object comparators.
- Serialization plugin tests for Java, Writable, and Avro reflect/specific serializers under configured schema/package settings.
- Metrics2 tests for source registration, immediate publish, record building with all counter/gauge numeric overloads, tag propagation, sink flush, filter acceptance/rejection, JSON/string output, singleton shutdown, and mini-cluster mode behavior.
