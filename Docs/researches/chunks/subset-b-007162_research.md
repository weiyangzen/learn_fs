# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml lines 17987-24376

## Purpose

This chunk is part of the generated Hadoop Common 2.7.2 JDiff API description. It is not implementation code; it records the public API contract emitted for compatibility comparison: packages, classes, interfaces, constructors, methods, fields, visibility, inheritance, implemented interfaces, checked exceptions, deprecation state, and Javadoc text.

The covered API surface runs from the tail of `org.apache.hadoop.io.Text` through core `Writable` APIs, compression codecs and streams, TFile metadata utilities, Hadoop serialization adapters, legacy metrics SPI/Ganglia/log4j metrics support, and the beginning of the metrics2 mutable metrics library. The line range starts in the middle of `Text` and ends in the middle of `MutableQuantiles`, so those two entries are partial for this chunk.

## API Inventory

### `org.apache.hadoop.io` tail and writable core

- The chunk begins inside `Text`, covering UTF-8 byte/string conversion and serialization operations: `toString`, `readFields(DataInput)`, bounded `readFields(DataInput,int)`, `skip(DataInput)`, `readWithKnownLength`, `write(DataOutput)`, bounded `write(DataOutput,int)`, equality/hash, static `decode` and `encode` overloads, static `readString`/`writeString` overloads, UTF-8 validation, `bytesToCodePoint`, `utf8Length`, and `DEFAULT_MAX_LEN`. The class doc describes standard UTF-8 storage with zero-compressed integer lengths and byte-level comparison/traversal utilities.
- `TwoDArrayWritable` is a `Writable` wrapper for `Writable[][]` matrices. It stores the element class and exposes constructors, `toArray`, `set`, `get`, `readFields`, and `write`.
- `VersionedWritable` is an abstract `Writable` base that writes and verifies an implementation version byte. Subclasses implement `getVersion()` and are expected to handle `VersionMismatchException` in custom `readFields` logic when evolving serialized formats.
- `VersionMismatchException` extends `IOException` and reports mismatches between a serialized version byte and the current `VersionedWritable#getVersion()`.
- `VIntWritable` and `VLongWritable` are `WritableComparable` wrappers around variable-length encoded `int` and `long` values. They expose default/value constructors, `set`, `get`, `readFields`, `write`, equality/hash, typed `compareTo`, and `toString`.
- `Writable` defines the base Hadoop binary serialization contract: `write(DataOutput)` and `readFields(DataInput)`. The docs emphasize that `readFields` must completely overwrite object state because Hadoop commonly reuses instances during deserialization.
- `WritableComparable` combines `Writable` and Java `Comparable` for sortable serialized records.
- `WritableComparator` implements `RawComparator` and `Configurable`. It exposes comparator lookup/registration through `get` and `define`, key instantiation through `newKey`, object and raw-byte `compare` paths, byte-array comparison/hash helpers, and primitive readers (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`) used by raw comparators.
- `WritableFactories` maintains per-class `WritableFactory` registrations and can create new `Writable` instances with or without a `Configuration`.
- `WritableFactory` is the one-method factory interface returning a new `Writable`.
- `WritableUtils` is the static helper collection for compressed byte arrays and strings, string arrays, byte-array display, writable cloning/copying, zero-compressed VInt/VLong read/write and sizing, enum serialization by string name, exact skipping, conversion of writables to byte arrays, and bounded `readStringSafely`.

### `org.apache.hadoop.io.compress`

- `BlockCompressorStream` extends `CompressorStream` for block-oriented compression. It writes blocks as uncompressed length plus one or more length-prefixed compressed chunks, supports configurable buffer size and compression overhead, and exposes `write`, `finish`, and protected `compress`.
- `BlockDecompressorStream` extends `DecompressorStream` for the matching block-oriented decode path. It exposes constructors with explicit/default buffers, protected `decompress`, protected `getCompressedData`, and `resetState`.
- `BZip2Codec` implements `Configurable` and `SplittableCompressionCodec`. It supports configuration accessors, output/input stream creation with optional compressor/decompressor instances, split input stream creation with start/end/read-mode arguments, compressor/decompressor factory methods, and default extension reporting.
- `CodecPool` leases and returns reusable `Compressor` and `Decompressor` instances, including overloads for compressor acquisition with `Configuration`. It exposes leased compressor/decompressor counts, which are useful for leak checks.
- `CompressionCodec` is the base codec interface for creating compression output/input streams, identifying and creating compressor/decompressor implementations, and reporting the default filename extension.
- `CompressionCodecFactory` discovers configured codec classes and maps codecs by path extension, class name, and user-friendly name. It also exposes `setCodecClasses`, suffix removal, a CLI `main`, and `LOG`.
- `CompressionInputStream` extends `InputStream` and implements `Seekable`. It wraps an underlying `InputStream`, exposes `resetState`, position/seek methods, `seekToNewSource`, and `maxAvailableData`.
- `CompressionOutputStream` extends `OutputStream`, wraps an underlying `OutputStream`, and defines the compression-stream lifecycle through `finish` and `resetState` in addition to `close`, `flush`, and byte-array `write`.
- `Compressor` is the stream compressor interface modeled after `Deflater`: `setInput`, `needsInput`, `setDictionary`, byte counters, `finish`, `finished`, `compress`, `reset`, `end`, and `reinit(Configuration)`.
- `CompressorStream` is a concrete `CompressionOutputStream` backed by a `Compressor`, output buffer, and closed flag. It exposes write/compress/finish/reset/close behavior and a single-byte `write`.
- `Decompressor` is the stream decompressor interface modeled after `Inflater`: `setInput`, `needsInput`, `setDictionary`, `needsDictionary`, `finished`, `decompress`, `getRemaining`, `reset`, and `end`.
- `DecompressorStream` is a concrete `CompressionInputStream` backed by a `Decompressor`, buffer, EOF flag, and closed flag. It exposes single-byte and byte-array reads, protected decompress/data-fetch hooks, stream checks, reset, skip, availability, close, and mark/reset behavior.
- `DefaultCodec` implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`, providing default compression stream/decompressor factories and direct decompressor creation.
- `DirectDecompressionCodec` marks codecs that can produce a `DirectDecompressor` for direct `ByteBuffer` decompression.
- `DirectDecompressor` defines `decompress(ByteBuffer src, ByteBuffer dst)`.
- `GzipCodec` extends `DefaultCodec` and overrides stream, compressor/decompressor, direct decompressor, type, and extension methods for gzip.
- `SplitCompressionInputStream` is an abstract `CompressionInputStream` for compressed ranges whose start/end may be adjusted to codec boundaries. It exposes protected setters and public `getAdjustedStart`/`getAdjustedEnd`.
- `SplittableCompressionCodec` extends `CompressionCodec` with split-aware `createInputStream(InputStream,Decompressor,long,long,READ_MODE)`. The docs explain that this is for codecs that can decompress from arbitrary positions and therefore support parallel processing of compressed input splits.

### `org.apache.hadoop.io.file.tfile`

- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are `IOException` types for TFile named metadata block conflicts and missing blocks.
- `RawComparable` exposes a byte-array slice through `buffer`, `offset`, and `size` so external raw comparators can compare byte ranges without object conversion.
- `TFile` is documented as a type-less byte key/value container with block compression, named metadata blocks, sorted or unsorted keys, and key/file-offset seeking. This chunk exposes static `makeComparator`, `getSupportedCompressionAlgorithms`, `main`, constants `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, `COMPARATOR_MEMCMP`, and `COMPARATOR_JCLASS`. Its docs also describe key size limits, chunked values, index memory footprint, configuration knobs for chunk and FS buffer sizes, and performance guidance.
- `Utils` contains TFile support helpers: variable-length integer/long read/write, Text-format string read/write, and lower/upper-bound binary search overloads for sorted collections and raw comparable data.

### `org.apache.hadoop.io.serializer`

- `JavaSerialization` is a serialization adapter for Java `Serializable` objects.
- `JavaSerializationComparator` extends `DeserializerComparator` for comparing Java-serialized objects through deserialization.
- `WritableSerialization` extends `Configured` and provides `Serialization` for Hadoop `Writable` types, delegating actual object data to each writable's `write`/`readFields` methods.
- `AvroReflectSerializable` is a marker interface for classes eligible for Avro reflect serialization.
- `AvroReflectSerialization` extends `AvroSerialization` and exposes `AVRO_REFLECT_PACKAGES`, the configuration key for package allow-listing. The docs state that classes are accepted when they implement the marker interface or are in configured packages.
- `AvroSerialization` is the configured base for Avro serialization providers and exposes `AVRO_SCHEMA_KEY`.
- `AvroSpecificSerialization` extends `AvroSerialization` for Avro specific classes.

### Legacy metrics and log metrics

- `EventCounter` extends log4j `AppenderSkeleton`. It counts log events by level and exposes appender lifecycle methods `append`, `close`, and `requiresLayout`.
- `GangliaContext` extends `AbstractMetricsContext` to emit legacy metrics to Ganglia over UDP. It exposes `close`, `emitMetric`, metadata helpers (`getUnits`, `getSlope`, `getTmax`, `getDmax`), XDR encoders (`xdr_string`, `xdr_int`), and state fields for the byte buffer, current offset, configured metric servers, and datagram socket.
- `AbstractMetricsContext` is the legacy metrics SPI base. It implements `MetricsContext`, initializes from `ContextFactory`, reads attributes and attribute tables, starts/stops monitoring, creates records, registers/unregisters periodic `Updater`s, exposes all buffered records, emits records through an abstract `emitRecord`, optionally flushes after each period, updates/removes internal metric rows, and manages the monitoring period through `getPeriod`, protected `setPeriod`, and `parseAndSetPeriod`.
- `CompositeContext` extends `AbstractMetricsContext` as a context that can fan metrics out to multiple child contexts.
- `MetricsRecordImpl` implements legacy `MetricsRecord`. It stores tags and metrics, supports typed `setTag` overloads for string/int/long/short/byte, `removeTag`, typed `setMetric` overloads for int/long/short/byte/float, typed `incrMetric` overloads for the same numeric types, and delegates `update`/`remove` back to its `AbstractMetricsContext`.
- `MetricValue` wraps a `Number` as either absolute or incremental, with `ABSOLUTE`, `INCREMENT`, `isIncrement`, `isAbsolute`, and `getNumber`.
- `NoEmitMetricsContext`, `NullContext`, and `NullContextWithUpdateThread` are no-output metrics contexts. `NoEmitMetricsContext` preserves records for polling, `NullContext` is the default do-nothing context, and `NullContextWithUpdateThread` samples periodically without emitting so pollers such as JMX see updated values.
- `OutputRecord` is the emitted legacy metrics record view. It exposes tag/metric names, individual tag/metric lookup, and copy accessors for the underlying tag and metric maps.
- `Util.parse(String,int)` parses space/comma-separated host or host:port metrics server specs, defaulting to localhost with a supplied port.

### `org.apache.hadoop.metrics2`

- `AbstractMetric` is the immutable metrics2 metric base implementing `MetricsInfo`. It exposes metric name/description/info, abstract `value`, abstract `type`, visitor dispatch, equality/hash, and string conversion.
- `MetricsCollector` creates `MetricsRecordBuilder`s by record name or `MetricsInfo`.
- `MetricsException` is the runtime wrapper for metrics failures, with message, cause, and message-plus-cause constructors.
- `MetricsFilter` is a metrics2 plugin that accepts or rejects names, tags, tag iterables, and whole metrics records.
- `MetricsInfo` supplies immutable name and description metadata for metrics and tags.
- `MetricsPlugin` initializes metrics framework plugins from `SubsetConfiguration`.
- `MetricsRecord` is an immutable timestamped metrics snapshot with record name, description, context, unmodifiable tag collection, and immutable metric iterable.
- `MetricsRecordBuilder` is the fluent builder API for metrics records. It adds tags, prebuilt metric/tag objects, context, integer/long counters, integer/long/float/double gauges, and returns the parent collector or ends the record.
- `MetricsSink` consumes `MetricsRecord`s through `putMetrics` and `flush`.
- `MetricsSource` publishes metrics through `getMetrics(MetricsCollector, boolean all)`.
- `MetricsSystem` implements `MetricsSystemMXBean` and provides source registration/unregistration, immediate publishing, and shutdown.
- `MetricsSystemMXBean` controls metrics system start/stop, MBean start/stop, and exposes current config text.
- `MetricsTag` is an immutable tag implementing `MetricsInfo`, with name/description/info/value accessors and equality/hash/string behavior.
- `MetricsVisitor` receives typed gauge and counter values for integer, long, float, and double metrics.
- `Metric` and `Metrics` are annotation interfaces used by the metrics2 annotation-based source machinery.
- `GlobFilter` and `RegexFilter` extend `AbstractPatternFilter`, compiling glob or regex strings to `Pattern`s.
- `DefaultMetricsSystem` is an enum singleton facade exposing `values`, `valueOf`, `initialize`, `instance`, and `shutdown`.
- `Interns` interns metrics metadata and tags through `info` and `tag` overloads to reduce duplicate object allocation.
- `MetricsRegistry` owns mutable metrics and tags for a source. It exposes registry metadata, metric/tag lookup, counter/gauge factory overloads, quantile/stat/rate factory overloads, synchronized sample addition by metric name, context tagging, tag addition with optional override, synchronized snapshot emission, and `toString`.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` define and implement monotonically increasing mutable counters. Concrete classes expose `incr`, delta `incr`, typed `value`, and `snapshot`.
- `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong` define and implement mutable gauges. Concrete classes expose typed `value`, `incr`, delta `incr`, `decr`, delta `decr`, `set`, and `snapshot`.
- `MutableMetric` is the abstract mutable metric base with abstract `snapshot(builder, all)`, convenience `snapshot(builder)`, changed-flag management through `setChanged`/`clearChanged`, and `changed`.
- The chunk ends inside `MutableQuantiles`, showing its interval-based constructor, synchronized `snapshot`, synchronized `add(long)`, `getInterval`, static `quantiles`, protected `previousSnapshot`, and the beginning of documentation for online estimates over a stream of long values.

## Control Flow and State

This XML records public contract rather than executable control flow. The main control-flow obligations are therefore encoded in method contracts and lifecycle pairs:

- Writable objects are written to `DataOutput` and read back from `DataInput`; reusable object instances must have all relevant state replaced in `readFields`.
- `Text`, `WritableUtils`, `VIntWritable`, and `VLongWritable` share the zero-compressed variable-length integer convention. Readers consume length prefixes and then bounded byte/string payloads; writer methods return encoded lengths where documented.
- Raw comparison flows in `WritableComparator` avoid object materialization where possible: callers pass two serialized byte ranges, helper methods parse primitive values directly, and typed comparators can fall back to object `compare`.
- Compression output flows from codec-created streams to `Compressor` instances, `finish`, and close/reset. Decompression flows from codec-created streams through `Decompressor`, repeated `needsInput`/`setInput`/`decompress` cycles, and reset/end cleanup. Split codecs may adjust requested input start/end positions before returning a stream.
- TFile contracts describe a block-oriented key/value container with optional sorted-key lookup, metadata blocks, and configurable chunking/buffering. The API surface in this chunk is primarily static utilities and constants, while the docs describe the larger reader/writer flow.
- Legacy metrics flow from `MetricsRecordImpl` mutation to `update`/`remove` calls on `AbstractMetricsContext`; contexts periodically call registered `Updater`s, convert internal rows to `OutputRecord`s, call subclass `emitRecord`, and then `flush`.
- Metrics2 flow is builder/collector oriented. A `MetricsSource` emits records to a `MetricsCollector`; records are built with `MetricsRecordBuilder`; mutable metrics and registries snapshot changed or all metrics into builders; sinks receive immutable `MetricsRecord`s.

Stateful APIs in this chunk include writable object payloads, codec pools and leased compressor/decompressor counts, stream buffers and closed/EOF flags, TFile comparator/compression configuration, metrics context tables and update thread state, Ganglia UDP buffer/socket state, metrics registry maps/tags, mutable metric values, changed flags, and quantile snapshots.

## Persistence and Serialization

The `org.apache.hadoop.io` portion is explicitly about Hadoop's binary persistence contract. `Writable` implementors persist state through `write(DataOutput)` and restore through `readFields(DataInput)`. `VersionedWritable` adds a version byte to serialized forms and raises `VersionMismatchException` on incompatible input. `Text` and `WritableUtils` use zero-compressed lengths and UTF-8 bytes; bounded read/write methods and `readStringSafely` are guardrails for oversized serialized data.

Compression stream APIs transform persisted or network byte streams but do not themselves define durable object formats except for block compressor stream framing. TFile is a durable container format with compressed data blocks, metadata blocks, indexes, key/value bytes, and configuration-dependent chunking/buffering. Serialization adapters bridge Java serialization, Hadoop Writables, and Avro reflect/specific formats.

Legacy metrics and metrics2 APIs mostly represent runtime telemetry state. `MetricsRecordImpl`, `OutputRecord`, `AbstractMetric`, `MetricsTag`, `MetricsRecord`, `MetricsRegistry`, and mutable metrics model current or snapshotted metrics rather than durable storage. Emission to Ganglia is network transmission, not local persistence.

## Dependencies and Integration Points

- Writable APIs integrate with Java `DataInput`/`DataOutput`, Hadoop `Configuration`, `RawComparator`, reflection-based instantiation, and downstream storage/RPC formats that rely on stable byte encodings.
- Compression APIs integrate with `InputStream`/`OutputStream`, `Seekable`, `Configuration`, codec implementations, native and pure-Java compressor/decompressor backends, direct `ByteBuffer` decompression, and split input processing in MapReduce-style readers.
- `BZip2Codec`, `GzipCodec`, and `DefaultCodec` are selected by `CompressionCodecFactory` through configured classes, filename extensions, class names, or codec names.
- TFile integrates with compression codecs, raw comparators, filesystem streams, and configuration keys controlling chunk and buffer sizes.
- Serializer classes integrate with Hadoop's `Serialization` framework, Java serialization, `Writable` implementations, Avro reflect/specific classes, and schema/package configuration keys.
- Legacy metrics integrate with `ContextFactory`, `MetricsContext`, `MetricsRecord`, `Updater`, log4j appenders, Ganglia UDP/XDR protocol expectations, and polling consumers such as `MetricsServlet` or JMX-style readers.
- Metrics2 integrates with `SubsetConfiguration`, metrics sources, sinks, collectors, builders, visitors, filters, MXBeans, annotations, interned metadata, and mutable metric registries.

## Risks and Edge Cases

- The source is generated JDiff metadata. It is strong evidence for the published Hadoop Common 2.7.2 API surface but does not prove implementation behavior, private state layout, or runtime bugs.
- The chunk boundaries are partial: `Text` starts before line 17987 and `MutableQuantiles` continues after line 24376. Consumers should merge adjacent chunk research before making whole-class claims for those two types.
- Writable deserialization is mutation-based. A `readFields` implementation that leaves stale fields behind can corrupt reused objects. Bounded text/string APIs are important for defending against malformed or oversized serialized inputs.
- Variable-length integer encodings must preserve exact byte compatibility. Off-by-one errors in first-byte sign/length decoding can break persisted data, sort order, and cross-version RPC/storage compatibility.
- Raw comparators depend on serialized byte layout. Changing a writable's encoding without updating comparators can produce inconsistent sorting or grouping.
- Compression codecs have lifecycle-sensitive resources. Failing to `finish`, `reset`, return pooled compressors/decompressors, or call `end` can leak native state or corrupt concatenated streams. Split compression requires careful start/end adjustment or readers may miss or duplicate records.
- Codec discovery by extension/name can be ambiguous if configured codecs overlap. Factory tests should confirm intended precedence and suffix removal.
- TFile performance and memory use depend on block size, chunk size, compression choice, and index cardinality. The docs warn about random-access costs for large blocks and index memory growth with many blocks or metadata blocks.
- Legacy metrics contexts are synchronized in several mutation paths but still depend on periodic background updates and global configuration. Null/no-emit contexts can hide missing metrics output in production if selected unexpectedly.
- Ganglia emission uses UDP and manual XDR buffer encoding; truncation, bad offsets, server spec parsing, and socket lifecycle are likely failure points.
- Metrics2 mutable metrics use changed flags and snapshot filtering. Forgetting to set or clear the changed flag can omit updates or repeatedly emit unchanged values. Counter/gauge synchronization differs by concrete class and overload, so concurrent updates should be tested under expected source usage.
- Filter and annotation APIs are extension points. Misconfigured glob/regex filters or metrics annotations can silently suppress records.

## Test Signals

- API compatibility checks should assert all documented classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, visibility, deprecation markers, and checked exceptions in this line range remain stable for Hadoop Common 2.7.2.
- Writable tests should cover `Text` UTF-8 encode/decode/validation, bounded reads/writes, zero-length and malformed input, `WritableUtils` VInt/VLong boundary values, enum round trips, exact skip failures, `readStringSafely` negative/oversized lengths, `WritableFactories` configured construction, and `WritableComparator` raw primitive reads/comparisons.
- Versioned writable tests should verify matching version reads, mismatched version exceptions, and subclass handling of old serialized versions.
- Compression tests should cover codec factory lookup by path/name/class, pooled compressor/decompressor lease/return counts, stream `finish`/`close`/`resetState`, block framing round trips, direct decompression where supported, split BZip2 reads with adjusted start/end offsets, concatenated decompressor streams, and resource cleanup after exceptions.
- TFile tests should exercise comparator creation, supported compression algorithm names, metadata block duplicate/missing exceptions, variable-length utilities, lower/upper-bound searches, and documented configuration effects on chunk/buffer sizing.
- Serialization tests should cover Java serializable acceptance, writable serialization/deserialization, Avro reflect package/marker acceptance, Avro schema configuration, and comparator behavior over serialized payloads.
- Legacy metrics tests should cover context initialization attributes, period parsing, updater registration/removal, start/stop monitoring idempotence, record tag/metric mutation by type, absolute versus incremental values, `update`/`remove` row matching, no-emit and null context behavior, Ganglia server parsing, XDR encoding, socket close, and log4j event counting by level.
- Metrics2 tests should cover immutable metric/tag equality, record builder fluent chaining, collector/source/sink interactions, filter decisions for names/tags/records, plugin initialization, metrics system registration/unregistration/shutdown, MXBean operations, interned metadata identity, registry duplicate/override tag behavior, counter/gauge mutation and snapshot output, changed-flag semantics, and quantile add/snapshot behavior once adjacent chunks provide the full class entry.
