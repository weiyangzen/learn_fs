# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml lines 24780-31074

Chunk: `subset-b-007222`
Lines researched: 24780-31074 of generated JDiff XML for `Apache Hadoop Common 3.3.5`.

## Scope

This chunk is a line-bounded slice of Hadoop Common 3.3.5's generated JDiff API snapshot. It is not implementation source; it records public/protected API metadata: packages, class/interface names, inheritance, implemented interfaces, constructors, methods, fields, static/final/abstract/synchronized flags, visibility, checked exceptions, deprecation markers, and Javadoc text.

The slice starts inside the end of `org.apache.hadoop.io.ShortWritable`, then covers a large run of `org.apache.hadoop.io`, compression, erasure-code schema, TFile, serializer, log metrics, and metrics2 APIs. It ends at the opening method of `org.apache.hadoop.metrics2.lib.MutableGaugeInt`, so that class is incomplete in this chunk and must be reconciled with the next chunk for a full type report.

## Purpose

The `org.apache.hadoop.io` portion documents Hadoop's core serialization and comparison primitives. These APIs provide the `Writable` contract, comparable value wrappers, raw-byte comparators, factory hooks for instantiating Writables, UTF-8 text handling, variable-length integer encodings, arrays, map wrappers, and utility helpers used throughout Hadoop RPC, file formats, MapReduce shuffle/sort, and configuration serialization.

The `org.apache.hadoop.io.compress` portion documents the codec SPI and concrete codec wrappers for block, stream, gzip, bzip2, default/zlib, passthrough, and splittable compression. These APIs define how Hadoop discovers codecs, leases compressor/decompressor instances, wraps input/output streams, supports direct decompression, and handles split boundaries for compressed files.

The `org.apache.hadoop.io.erasurecode`, `org.apache.hadoop.io.file.tfile`, and serializer portions document smaller but important integration APIs: erasure coding schema descriptors, TFile constants/helpers/raw comparable interfaces, and pluggable Java/Writable/Avro serialization adapters.

The `org.apache.hadoop.metrics2` and `org.apache.hadoop.metrics2.lib` portion documents the metrics framework public surface. It defines metric values, tags, records, collectors, builders, sources, sinks, filters, visitors, plugin lifecycle, metrics system lifecycle, singleton access, registries, interned metadata, and the first mutable counter/gauge types.

## Important APIs, Types, and Functions

### Hadoop IO and Writable APIs

- `ShortWritable` is only partially visible at the chunk start. The visible tail includes `toString()` returning short values in string form and class documentation identifying it as a `WritableComparable` for shorts.
- `SortedMapWritable` extends `AbstractMapWritable` and implements `java.util.SortedMap`. It exposes default and copy constructors, sorted-map navigation (`comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`), normal map operations, `readFields(DataInput)`, `write(DataOutput)`, `equals`, and `hashCode`.
- `Stringifier<T>` extends `Closeable` and defines `toString(T)`, `fromString(String)`, and `close()`, all throwing `IOException`. It is the generic object-to-string and string-to-object conversion contract.
- `Text` extends `BinaryComparable` and implements `WritableComparable`. It stores strings as standard UTF-8 bytes and exposes constructors from `String`, `Text`, and `byte[]`; raw and copied byte access; byte length; UTF-8 scalar access via `charAt`; byte-position search via `find`; mutators `set`, `append`, and `clear`; serialization with optional max lengths; static `skip`, `readWithKnownLength`, UTF-8 `encode`/`decode`, `readString`/`writeString`, validation, code-point extraction, and `utf8Length`. `DEFAULT_MAX_LEN` is a public static final max-length constant.
- `TwoDArrayWritable` represents matrices of `Writable` instances for a declared value class. It supports construction with a value class and optional initial two-dimensional array, conversion to Java arrays, `set`, `get`, and Writable serialization.
- `VersionedWritable` is a base class for Writables with version checking. Subclasses provide `getVersion()`, and the base `write`/`readFields` contract persists/checks the version byte.
- `VersionMismatchException` carries expected/found version bytes and provides a string representation for version-read failures.
- `VIntWritable` and `VLongWritable` are `WritableComparable` wrappers for variable-length integer and long encodings. They expose default/value constructors, `set`, `get`, `readFields`, `write`, equality/hash, comparison, and string conversion.
- `Writable` defines Hadoop's simple serialization contract: `write(DataOutput)` and `readFields(DataInput)`, both throwing `IOException`. `WritableComparable<T>` combines `Writable` with `Comparable<T>`.
- `WritableComparator` is the comparator and raw-byte comparison hook for `WritableComparable` keys. It has constructors binding key classes and optional `Configuration`, static `get` and `define` registry methods, configurable support, `newKey`, object and byte-array `compare` methods, `compareBytes`, byte-array hash helpers, primitive readers (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`), and zero-compressed variable-length readers.
- `WritableFactories` holds the factory registry for classes needing non-public or custom construction. It exposes `setFactory`, `getFactory`, and `newInstance` overloads with and without `Configuration`.
- `WritableFactory` is the single-method factory interface with `newInstance()`.
- `WritableUtils` is the serialization utility class. It covers compressed byte arrays and strings, string and compressed-string arrays, display helpers, cloning into new or existing Writables, variable-length int/long read/write and size calculation, bounded int reads, enum read/write, full skipping, byte-array conversion of Writables, and safe string reads with a max length.

### Compression APIs

- `BlockCompressorStream` and `BlockDecompressorStream` are block-oriented stream adapters around `Compressor` and `Decompressor`. They add block size and compression-overhead handling, `finish`, `compress`, `decompress`, `getCompressedData`, and `resetState`.
- `BZip2Codec`, `DefaultCodec`, `GzipCodec`, and `PassthroughCodec` implement `CompressionCodec` style construction of compression streams, codec-specific compressor/decompressor types, direct decompressor support where available, configuration access, and default extensions.
- `CodecConstants` defines public extension constants for default, bzip2, gzip, lz4, passthrough, snappy, and zstandard codecs.
- `CodecPool` manages reusable `Compressor` and `Decompressor` instances. It supports leasing by codec, returning instances, and counting currently leased compressor/decompressor objects.
- `CompressionCodec` defines the codec SPI: create input/output streams with or without supplied compressor/decompressor, report compressor/decompressor classes, create instances, and return a default filename extension.
- `CompressionCodecFactory` discovers configured codec classes from `Configuration`, maps paths/names/class names to codecs, removes codec suffixes, and exposes a diagnostic `main`. It has a public SLF4J `LOG` field.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream wrappers with protected underlying `in`/`out` fields, close/flush/read/write integration, `finish`, `resetState`, seek-position stubs on input, and `getIOStatistics()`.
- `Compressor` and `Decompressor` define the low-level state machines: input/dictionary setup, input/dictionary needs, byte counters, finish/finished, compress/decompress, remaining bytes for decompression, reset, end, and compressor reinitialization with `Configuration`.
- `CompressorStream` and `DecompressorStream` are generic stream implementations with protected compressor/decompressor, buffer, eof/closed state, close/reset/skip/available/mark behavior, and protected `compress`, `decompress`, `getCompressedData`, and stream checking hooks.
- `DirectDecompressionCodec` creates `DirectDecompressor` instances, while `DirectDecompressor` exposes direct `ByteBuffer` decompression.
- `SplitCompressionInputStream` tracks adjusted split start/end offsets. `SplittableCompressionCodec` creates such streams for a requested split and declares `READ_MODE`.

### Erasure Coding, TFile, and Serialization

- `ECSchema` describes an erasure coding policy schema. Constructors accept a map or explicit codec name, data units, parity units, and extra options. Getters expose codec, extra options, data units, and parity units; equality/hash/string methods make it value-like. Public keys are `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.
- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are TFile-specific exceptions for metadata block conflicts/misses.
- `RawComparable` exposes `buffer()`, `offset()`, and `size()` for comparing raw byte slices without object conversion.
- `TFile` exposes compression and comparator constants (`COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, `COMPARATOR_MEMCMP`, `COMPARATOR_JCLASS`), supported compression algorithm lookup, comparator construction, and a `main`.
- `org.apache.hadoop.io.file.tfile.Utils` provides TFile helper encodings and searches: variable-length ints/longs, strings, and lower/upper bound binary-search helpers over comparable sequences.
- `JavaSerialization`, `JavaSerializationComparator`, and `WritableSerialization` are serializer adapter types.
- Avro integration includes the marker `AvroReflectSerializable`, `AvroReflectSerialization` with `AVRO_REFLECT_PACKAGES`, base `AvroSerialization` with `AVRO_SCHEMA_KEY`, and `AvroSpecificSerialization`.

### Logging and Metrics2 APIs

- `EventCounter` is a log4j appender-like metrics bridge with `append`, `close`, and `requiresLayout`.
- `AbstractMetric` is the immutable metric base, storing `MetricsInfo` and exposing `name`, `description`, `info`, numeric `value`, `MetricType`, visitor dispatch, equality/hash, and string conversion.
- `MetricsCollector` creates `MetricsRecordBuilder` instances with `addRecord(String)` or `addRecord(MetricsInfo)`.
- `MetricsException` is the framework runtime exception with string, cause, and string-plus-cause constructors.
- `MetricsFilter` accepts or rejects names, tags, tag collections, and records.
- `MetricsInfo` exposes immutable metric/tag metadata `name()` and `description()`.
- `MetricsJsonBuilder` and `MetricStringBuilder` are `MetricsRecordBuilder` implementations that build JSON or string dumps of metrics. They implement tag/add/context/counter/gauge methods, parent access, and `toString()`.
- `MetricsPlugin` has `init(SubsetConfiguration)`. `MetricsSink` has `putMetrics(MetricsRecord)` and `flush()`. `MetricsSource` has `getMetrics(MetricsCollector, boolean)`.
- `MetricsRecord` is an immutable metrics snapshot with timestamp, name, description, context, tags, and metrics.
- `MetricsRecordBuilder` is the fluent builder for tags, immutable metric additions, counters, gauges for int/long/float/double, context setting, parent lookup, and `endRecord`.
- `MetricsSystem` registers/unregisters sources, callbacks, publishes immediately, starts/stops metrics and MBeans, and shuts down.
- `MetricsSystemMXBean` exposes JMX lifecycle/config methods: `start`, `stop`, `startMetricsMBeans`, `stopMetricsMBeans`, and `currentConfig`.
- `MetricsTag` is an immutable tag with `MetricsInfo`, value, equality/hash, and string conversion.
- `MetricsVisitor` has callbacks for gauge and counter values across int, long, float, and double forms.
- `@Metric` and `@Metrics` are annotation types for declaring individual metrics and metrics groups.
- `GlobFilter` and `RegexFilter` compile metric filters using `com.google.re2j.Pattern`.
- `DefaultMetricsSystem` is an enum singleton API for initialization, instance lookup, shutdown, and mini-cluster mode toggles.
- `Interns` creates interned `MetricsInfo` and `MetricsTag` instances.
- `MetricsRegistry` creates and maintains mutable metrics and tags. It exposes registry info, metric/tag lookup, counter and gauge factories for int/long/float values, quantiles, stats, rates, aggregated rates, rolling averages, sample addition by name, context/tag creation with override control, snapshotting into a builder, and string conversion.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` define mutable monotonically increasing counters with increment, value, and snapshot operations. `MutableCounterInt.incr(int)` is synchronized in this snapshot; `MutableCounterLong.incr(long)` is not marked synchronized.
- `MutableGauge` is the abstract mutable gauge base with `incr` and `decr`. `MutableGaugeInt` begins at the chunk end and only its `value()` method start is included in this slice.

## Control Flow and Behavioral Contracts

The XML itself has no executable control flow, but the API contracts imply several runtime paths:

- Writable serialization flows through `write(DataOutput)` and `readFields(DataInput)`. Value classes such as `Text`, `VIntWritable`, `VLongWritable`, `SortedMapWritable`, `TwoDArrayWritable`, and versioned Writables persist their internal state into Hadoop's binary formats and reconstruct themselves from `DataInput`.
- Sorting and grouping paths can bypass object creation through `WritableComparator.compare(byte[], int, int, byte[], int, int)`, primitive byte readers, and zero-compressed integer readers. This is the hot path for file formats and shuffle/sort code using serialized keys.
- `Text` operations are byte-oriented. `find` returns byte positions, `charAt` returns Unicode scalar values without constructing a `String`, `getBytes()` exposes a backing buffer whose valid content is limited by `getLength()`, and `clear()` intentionally does not erase or free the backing byte array.
- Compression stream flow starts from `CompressionCodecFactory` resolving a codec for a path/name/class, then `CodecPool` optionally leases compressor/decompressor instances, then codec `createInputStream`/`createOutputStream` wraps the raw stream. Finish/reset/close methods coordinate codec state with underlying streams and returned pooled objects.
- Low-level `Compressor` and `Decompressor` implementations use an explicit state machine: receive input, report whether more input or a dictionary is needed, transform bytes, expose consumed/produced counts, finish or reset, and release native resources through `end`.
- Splittable compression flow uses `SplittableCompressionCodec.createInputStream` to adjust requested split boundaries into codec-valid `getAdjustedStart()`/`getAdjustedEnd()` offsets.
- TFile helpers define compact integer/string encodings and binary-search helpers used by indexed block formats.
- Metrics flow starts with `MetricsSource.getMetrics`, which emits records through a `MetricsCollector`; each record is populated by a `MetricsRecordBuilder`; sinks consume immutable `MetricsRecord` snapshots. Mutable metrics are registered in a `MetricsRegistry`, sampled with `snapshot(builder, all)`, and published through the metrics system.
- Metrics lifecycle flows through `DefaultMetricsSystem.initialize(prefix)`, source registration on `MetricsSystem`, periodic or immediate `publishMetricsNow`, sink `putMetrics`, sink `flush`, and shutdown/start/stop paths including optional JMX MBeans.

## State and Persistence Behavior

This JDiff file persists API metadata for compatibility checks. It does not persist runtime state directly.

Writable-based APIs in this chunk define durable binary state. `Text` persists a variable-length encoded byte count followed by UTF-8 bytes; `VIntWritable` and `VLongWritable` persist zero-compressed integers; `SortedMapWritable` and `TwoDArrayWritable` persist collections of nested Writables and their class identity through inherited map/array mechanisms; `VersionedWritable` persists and checks a version byte before subclass state. Golden-byte compatibility matters because Hadoop data files and RPC payloads can outlive the producing process.

`WritableFactories` and `WritableComparator` maintain process-local registries for factories and optimized comparators. These registries affect how deserialization and sort comparison instantiate or compare classes inside a JVM but are not durable.

Compression classes carry stream-local state: buffers, compressor/decompressor objects, eof/closed flags, split boundaries, and underlying input/output streams. `CodecPool` adds process-level state by tracking leased and returned compressors/decompressors. Incorrect return/reset/end behavior can leak native resources or corrupt later users of a pooled codec instance.

`ECSchema`, `MetricsTag`, and many metrics metadata objects are value-like immutable descriptors. `Interns` adds process-local interning for metrics info and tags, trading allocation reduction for cache retention.

Metrics runtime state is mostly in-memory. `MetricsRegistry` owns mutable metric objects and tags; counters are monotonically increasing, gauges can increase/decrease/set in later chunks, quantiles/stats/rates accumulate samples, and `snapshot` transfers current values into a record builder. `DefaultMetricsSystem` and `MetricsSystem` manage singleton/global lifecycle state, registered sources/sinks, callbacks, and MBean publication state.

Serializer and Avro classes describe adapter entry points. Persistence semantics are delegated to Java serialization, Hadoop Writable serialization, or Avro schemas configured through keys such as `AVRO_SCHEMA_KEY` and `AVRO_REFLECT_PACKAGES`.

## Dependencies and Integration Points

This chunk depends on JDiff/Javadoc generation semantics and the JDiff XML schema. The represented APIs integrate with:

- Java IO (`InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `Closeable`, `IOException`), NIO (`ByteBuffer`, charset exceptions), collections, comparators, patterns, and primitive wrappers.
- Hadoop `Configuration` and `Configurable` for comparator, factory, codec, compressor, serializer, and metrics plugin setup.
- Hadoop `Writable`, `WritableComparable`, `BinaryComparable`, `AbstractMapWritable`, `MetricsInfo`, `MetricsRecordBuilder`, `MetricsCollector`, `MetricsRecord`, and mutable metrics classes across package boundaries in this same API snapshot.
- Hadoop filesystem statistics through `CompressionInputStream.getIOStatistics()` and `CompressionOutputStream.getIOStatistics()`.
- Compression native libraries and codec implementations behind `Compressor`, `Decompressor`, `DirectDecompressor`, gzip, bzip2, zlib/default, passthrough, and splittable codec implementations.
- TFile data structures and block/index lookup code through raw comparable byte slices, compression constants, comparator factories, and compact encodings.
- Avro serialization through reflect/specific serialization classes and schema configuration keys.
- Metrics integrations through Apache Commons Configuration `SubsetConfiguration`, SLF4J loggers, log4j-style `EventCounter`, RE2/J regex patterns, JMX MXBeans, metrics source/sink/plugin contracts, and singleton `DefaultMetricsSystem` access.

## Risks and Compatibility Notes

- The chunk starts in the middle of `ShortWritable` and ends in the middle of `MutableGaugeInt`; whole-file reconciliation must merge adjacent chunks before claiming complete coverage of those types.
- JDiff exposes signature and documentation compatibility, not implementation details. Exact serialization byte layouts, pool locking behavior, native-code error paths, codec header formats, and metrics scheduling require implementation-source or tests to verify.
- `Text.getBytes()` exposes the backing array and is only valid up to `getLength()`. Callers that use the full array can read stale data; `clear()` also leaves the old backing bytes allocated and visible via `getBytes()`.
- `Text` method positions are byte offsets, not Java UTF-16 character indexes. Misinterpreting `find`, `charAt`, or `validateUTF8` offsets can corrupt multibyte UTF-8 handling.
- Max-length overloads on `Text.readFields`, `Text.write`, `readString`, `writeString`, and `WritableUtils.readStringSafely` are important input-boundary defenses. Callers that use unbounded reads on untrusted inputs risk excessive allocation.
- `WritableComparator` raw-byte comparison must remain consistent with object `compareTo`. Divergence causes incorrect sorted order, grouping, partitioning, or binary-search behavior.
- Factory and comparator registries are process-global. Tests or applications that register custom factories/comparators can affect unrelated code in the same JVM.
- Codec pooling requires disciplined ownership. Returning a compressor/decompressor while still in use, failing to return it, or failing to reset state can cause data corruption, leaks, or cross-stream contamination.
- `CompressionInputStream.seek` and `seekToNewSource` are present on the abstract stream, but many compressed streams are not meaningfully seekable. Callers should rely on codec/splittable capabilities rather than assuming random access.
- Direct decompression uses `ByteBuffer` and codec-specific native paths. Implementations must define buffer position/limit behavior carefully and handle unsupported direct decompression.
- `PassthroughCodec` deliberately reports a codec extension while performing no compression. Code that assumes every codec changes bytes or compression ratio may mis-handle it.
- TFile constants include `COMPRESSION_LZO`, but actual support depends on configured/native codec availability.
- Metrics filters use RE2/J patterns rather than `java.util.regex.Pattern`, which affects syntax/performance compatibility.
- `MetricsRegistry.newQuantiles` documents `MetricsException` for non-positive intervals. Registry callers should validate interval configuration before runtime registration.
- Mutable metric synchronization differs by class/method in the metadata. Concurrency assumptions should be checked against implementation, especially for high-frequency counters and registry mutation/snapshot paths.
- `DefaultMetricsSystem` is a singleton/global access point. Mini-cluster mode and shutdown can affect all metrics users in the JVM.

## Test Signals

Useful validation for the APIs represented by this chunk includes:

- XML well-formedness and JDiff compatibility checks that all class/interface start/end markers inside the slice match except the documented partial `ShortWritable` and `MutableGaugeInt` boundaries.
- Writable round-trip tests for `SortedMapWritable`, `Text`, `TwoDArrayWritable`, `VersionedWritable` subclasses, `VIntWritable`, and `VLongWritable`, including empty values, nested Writables, negative numbers, boundary variable-length encodings, and version mismatch failures.
- `Text` tests for UTF-8 multibyte characters, invalid UTF-8 validation, byte-position `find`, scalar `charAt`, append/set/copy semantics, max-length read/write enforcement, backing-array behavior of `getBytes`, and `clear()` retaining capacity.
- Comparator tests asserting `WritableComparator` raw-byte compare agrees with object `compareTo`; primitive byte readers decode known big-endian/zero-compressed sequences; custom comparator registration affects lookup; and `newKey()` uses the expected factory/configuration.
- `WritableFactories` tests for custom factory registration, `Configuration` propagation, default constructor fallback, and non-public Writable instantiation.
- `WritableUtils` golden-byte tests for compressed byte arrays/strings, string arrays, enum read/write, `skipFully`, `toByteArray`, clone/cloneInto behavior, and safe string length rejection.
- Compression tests for each codec's default extension, stream round trips, finish/flush/close ordering, reset-state reuse, dictionary-required paths where applicable, direct decompressor behavior, split-boundary adjustment, IOStatistics delegation, and malformed/truncated input handling.
- `CodecPool` tests for lease/return counts, reuse after return, reset before reuse, double return behavior, concurrent leasing, and native resource release through compressor/decompressor `end`.
- `CompressionCodecFactory` tests for configured codec classes, lookup by path/class/name, suffix removal, duplicate extensions, and absent codec handling.
- `ECSchema` tests for map and explicit constructors, required keys, extra option preservation, equality/hash stability, and string rendering.
- TFile tests for supported compression listing, comparator construction, raw comparable offsets/sizes, variable-length helper encodings, string helper encodings, and lower/upper-bound search edge cases.
- Serializer tests for Java, Writable, Avro reflect, and Avro specific adapters, including configured schemas/packages and comparator behavior for serialized Java objects.
- Metrics tests for collector/builder chaining, immutable record/tag/metric equality, JSON/string builder output shape, visitor dispatch by metric type, filter accept/reject behavior for names/tags/records, plugin initialization with subset configuration, source-to-sink publication, sink flushing, and metrics system start/stop/shutdown/JMX lifecycle.
- `MetricsRegistry` tests for duplicate metric/tag names, tag override behavior, counter/gauge creation and lookup, stat/rate/quantile registration, invalid quantile intervals, `add(name, value)` routing, snapshot with `all` true/false, and concurrent mutation while snapshotting.
- Mutable counter tests for increment-by-one, delta increments, monotonicity, value reporting, snapshot output, integer overflow behavior if defined by implementation, and thread behavior matching the synchronization contract.

## Cross-Chunk Notes

The previous chunk is needed to complete `org.apache.hadoop.io.ShortWritable`; this chunk only includes the tail of its `toString()` method and class doc before the class ends at line 24787.

The next chunk is needed to complete `org.apache.hadoop.metrics2.lib.MutableGaugeInt`; this slice stops immediately after the `value()` method declaration begins at line 31074. Later methods such as integer gauge increments, decrements, setters, and snapshot behavior are outside this mapped range.
