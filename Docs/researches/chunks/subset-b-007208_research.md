# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml lines 24647-30892

## Research scope

This chunk is a JDiff XML public API snapshot for Apache Hadoop Common 3.3.3, not Java implementation source. The range begins inside `org.apache.hadoop.io.WritableComparator`, covers the remainder of core `org.apache.hadoop.io` serialization helpers, compression stream/codec contracts, erasure-code schema metadata, TFile public helpers, Hadoop serializer bindings, log metrics, most of the metrics2 public API and mutable metric library, metrics sinks, selected metrics utilities, and then ends inside the opening of `org.apache.hadoop.net.AbstractDNSToSwitchMapping`. Findings below are based on class/interface signatures, visibility, inheritance, fields, declared exceptions, constants, and embedded Javadocs.

## Purpose

The slice documents Hadoop Common's public contracts for binary serialization, compressed I/O, type-specific serializer registration, and metrics export. The `org.apache.hadoop.io` APIs provide the low-level `Writable` comparison, factory, and variable-length encoding utilities that support RPC, sequence files, TFile, and other on-disk/wire formats. The compression package defines reusable codec, compressor, decompressor, split-compression, direct-buffer decompression, stream wrapper, codec discovery, and resource-pooling abstractions used by filesystem, MapReduce, and storage readers.

The later packages document how Hadoop publishes observability data: immutable metric records and tags, mutable metric sources, record builders, visitors, filters, default metrics-system lifecycle, MBean registration, caches for sparse-update sinks, and concrete file/Graphite/HDFS/StatsD sink entry points. The final net package lines start the topology mapping base class used by Hadoop's rack-awareness layer.

## Important APIs and types

`WritableComparator` is the tail of the class from the previous chunk. This range includes the protected constructor accepting key class, `Configuration`, and instance-creation behavior; static comparator lookup and registration through `get(...)` and `define(...)`; `Configurable` methods; key allocation with `newKey()`; object and raw-byte `compare(...)` overloads; byte lexicographic comparison; byte hashing; primitive byte-array readers; and VInt/VLong byte-array decoders. The API exists so compare-heavy paths can avoid deserializing whole keys when an optimized raw comparator is available. Registered comparators are documented as thread-safe.

`WritableFactories` and `WritableFactory` provide a global factory registry for `Writable` implementations, especially non-public writable classes that `ObjectWritable` cannot instantiate directly through ordinary reflection. `setFactory`, `getFactory`, and `newInstance` are the main surface, with configuration-aware instantiation where available.

`WritableUtils` is a final utility holder for Hadoop's `Writable` wire-format helpers. It covers compressed byte arrays and strings, plain UTF string read/write, string arrays, debug display of byte arrays, serialization-based clone helpers, VInt/VLong writing and reading, bounded integer decoding with `readVIntInRange`, encoded-size and sign helpers, enum serialization by string name, exact skipping, serialization of multiple writables to a byte array, and guarded string reading through `readStringSafely`. `cloneInto` remains in the public API but is deprecated in favor of `ReflectionUtils.cloneInto`.

The `org.apache.hadoop.io.compress` package defines the primary compression contracts. `CompressionCodec` is the central codec interface: it creates compression/decompression streams, exposes compressor/decompressor classes, allocates compressor/decompressor instances, and supplies a default filename extension. `DirectDecompressionCodec` adds direct `ByteBuffer` decompression support through `DirectDecompressor`, while `SplittableCompressionCodec` creates `SplitCompressionInputStream` instances for compressed data ranges.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases that wrap `InputStream`/`OutputStream`, surface underlying `IOStatistics`, and define reset/finish behavior. `CompressorStream` and `DecompressorStream` adapt `Compressor` and `Decompressor` state machines to stream reads and writes, with fields for the codec object, buffers, EOF/closed state, and close/reset handling. `BlockCompressorStream` and `BlockDecompressorStream` add block framing semantics, compressing no more than a configured block and decoding framed compressed blocks.

`Compressor` and `Decompressor` are stateful codec engines. They accept input buffers, optional dictionaries, report bytes read/written or remaining compressed data, expose `needsInput`, `needsDictionary`, `finish`, `finished`, `reset`, and `end`, and perform byte-buffer style `compress`/`decompress` calls. `Compressor.reinit(Configuration)` lets pooled compressors be reused with new settings.

Concrete codec-facing classes in this range include `BZip2Codec`, `DefaultCodec`, `GzipCodec`, and `PassthroughCodec`. `BZip2Codec` also implements split decompression via a `READ_MODE`-like read-mode parameter. `DefaultCodec` and `GzipCodec` expose direct decompressor creation. `PassthroughCodec` is a special no-transform codec with configurable extension constants. `CodecConstants` records default filename suffixes for default, bzip2, gzip, lz4, passthrough, snappy, and zstandard codecs.

`CodecPool` is the global compressor/decompressor lease pool. It returns codec-specific compressor/decompressor instances, accepts them back through `returnCompressor` and `returnDecompressor`, and exposes leased-resource counts for tests or diagnostics. `CompressionCodecFactory` discovers codecs from `io.compression.codecs`, Java `ServiceLoader`, and built-ins; resolves codecs by path suffix, class name, short name, alias, or class; removes codec suffixes from filenames; and has a small `main` test utility.

`ECSchema` in `org.apache.hadoop.io.erasurecode` is a value object for erasure-code policy shape. It can be built from a map of options or from codec name, data-unit count, parity-unit count, and optional extras. It exposes constants for option keys, getters, `toString`, `equals`, and `hashCode`.

The TFile section contains checked exception types `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist`, `RawComparable` for byte-array backed comparison, `TFile` public constants and helpers, and `Utils` variable-length encoding/search helpers. `TFile.makeComparator` creates raw comparators from comparator names, `getSupportedCompressionAlgorithms` lists accepted compression labels, and public constants identify `gz`, `lzo`, `none`, `memcmp`, and Java-class comparator prefixes. `Utils` duplicates TFile-specific VInt/VLong and string encoding plus lower/upper-bound binary-search helpers over lists and arrays.

The serializer package records bindings for Java object serialization and Writable serialization. `JavaSerialization`, `JavaSerializationComparator`, and `WritableSerialization` expose public constructors, while docs note Java serialization support for `Serializable` and Writable serialization that delegates to the `Writable` methods. The Avro serializer package includes marker `AvroReflectSerializable`, `AvroReflectSerialization` with the `AVRO_REFLECT_PACKAGES` configuration key, abstract/base `AvroSerialization` with `AVRO_SCHEMA_KEY`, and `AvroSpecificSerialization` for Avro `SpecificRecord` types.

`EventCounter` in `org.apache.hadoop.log.metrics` is a Log4J appender that counts warning, error, and fatal events. Its API has `append`, `close`, and `requiresLayout`, making it a bridge from logging events into metrics-style counters.

The `org.apache.hadoop.metrics2` package defines the metrics framework core. `AbstractMetric` is the immutable metric value base with `MetricsInfo`, numeric value, `MetricType`, visitor dispatch, equality/hash/toString. `MetricsInfo`, `MetricsTag`, `MetricsRecord`, `MetricsCollector`, `MetricsRecordBuilder`, `MetricsVisitor`, `MetricsSink`, `MetricsSource`, `MetricsPlugin`, `MetricsFilter`, `MetricsException`, `MetricsSystem`, and `MetricsSystemMXBean` form the main publication contract. Builders accept tags, immutable metrics, counters, gauges across primitive numeric types, context tags, parent collector navigation, and fluent `endRecord`. Visitors receive typed callbacks for gauges and counters.

`MetricsJsonBuilder` and `MetricStringBuilder` are concrete `MetricsRecordBuilder` implementations for textual dumps. They consume the same builder calls as sinks/sources but render records to JSON or delimited strings.

Metrics annotations are represented by marker annotation types `Metric` and `Metrics`. Filter implementations in `metrics2.filter` include `GlobFilter` and `RegexFilter`; both compile user patterns to `com.google.re2j.Pattern` and plug into the `MetricsFilter` acceptance contract.

The `metrics2.lib` package supplies source-side mutable metric state. `DefaultMetricsSystem` is a singleton-style enum with initialize/instance/shutdown and mini-cluster mode controls. `Interns` interns `MetricsInfo` and `MetricsTag` objects. `MetricsRegistry` owns a record's metadata, tags, and mutable metrics; it creates typed counters and gauges, quantiles, stats, rates, aggregated rates, and rolling averages; adds samples by metric name; sets context; tags records with optional override behavior; and snapshots all mutable metrics into a `MetricsRecordBuilder`.

The mutable metric hierarchy includes `MutableMetric` with changed-flag lifecycle and conditional snapshotting; `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` for monotonic counters; `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong` for increment/decrement/settable gauges; `MutableStat` for sample statistics with optional extended stats and min/max reset; `MutableRate`, `MutableRates`, and `MutableRatesWithAggregation` for rates keyed by protocol methods or named samples; `MutableQuantiles` for scheduled rolling quantile estimation; and `MutableRollingAverages` for thread-local rolling averages with explicit close and test-only validity configuration.

The sink package exposes concrete metrics output plugins. `FileSink`, `GraphiteSink`, `RollingFileSystemSink`, and `StatsDSink` implement `MetricsSink` and close/flush behavior where appropriate. `RollingFileSystemSink` has the richest public state and behavior: source name, error policy, append policy, base path, roll interval, random roll offset interval, next-flush calendar, static test hooks for force flushing and supplied configuration/filesystem, constructors including a testing constructor, roll-interval parsing, initial and subsequent flush-time scheduling, metric writing, flushing, and close. `StatsDSink` writes metrics lines to a StatsD daemon and exposes `writeMetric` for individual line emission.

`metrics2.util.MBeans` registers/unregisters Hadoop-standard JMX object names, optionally with extra properties, and can extract `service` and `name` components from `ObjectName`. `MetricsCache` keeps latest record state for sinks that cannot consume sparse updates, optionally caching tag values for later lookup and limiting record count per name. `Servers.parse` turns space/comma separated host or host:port specs into socket addresses, defaulting null input to localhost plus the caller-supplied port.

The chunk ends after the constructors and start of `getConf` for `org.apache.hadoop.net.AbstractDNSToSwitchMapping`, an abstract `DNSToSwitchMapping` and `Configurable` base. The visible constructors support unconfigured construction and construction with a cached `Configuration`; the constructor doc explicitly says it does not call `setConf`, so subclasses that derive state in `setConf` must call it themselves.

## Control flow and behavior

Writable comparison follows a two-tier path. If a class has an optimized comparator registered in `WritableComparator.define`, callers can compare serialized bytes directly with `compare(byte[], int, int, byte[], int, int)`. Otherwise, the default path constructs two key instances, deserializes with `Writable.readFields`, and compares via natural ordering. The byte helper methods support raw comparator implementations that parse primitive fields or VInts without constructing objects.

Writable factory lookup is registry-driven. Callers ask `WritableFactories.newInstance` for a class, the registry returns a configured factory when one exists, and reflection/fallback creation is implied for ordinary public writables. This supports deserialization paths where the encoded type is known but the constructor is not public.

Compression control flow is stream and state-machine based. A codec creates a stream around an existing input/output stream and either obtains a fresh or pooled `Compressor`/`Decompressor`. Compression callers repeatedly set input, check `needsInput`, call `compress`, call `finish`, and observe `finished`; decompression callers set input or let `DecompressorStream` refill compressed data, then call `decompress` until output is produced, EOF is reached, or a dictionary is required. `resetState` makes a stream reusable for a new compressed member, while `end` releases native or external resources owned by a codec engine.

Codec discovery and file matching flow through `CompressionCodecFactory`: construction reads configured codec classes and discovered implementations, builds extension/name/class maps, then `getCodec(Path)` selects by filename suffix. Name-based lookups support canonical class names, simple names, and configured aliases. Splittable readers call the `SplittableCompressionCodec` overload with start/end offsets and read mode, after which `SplitCompressionInputStream` may adjust the effective range.

Metrics control flow has source, builder, collector, and sink stages. A `MetricsSource.getMetrics` call receives a `MetricsCollector`; the source adds records and uses `MetricsRecordBuilder` to add tags, context, counters, and gauges. Mutable metrics snapshot into the builder, optionally only when `changed`. A `MetricsSystem` registers sources and sinks, can publish immediately, and shuts down at process stop. Sinks consume immutable `MetricsRecord` instances through `putMetrics` and eventually `flush` or `close`.

Mutable rate/stat control flow accumulates samples in source-side objects, then emits a snapshot. `MutableStat` tracks sample count/sum and optional extended statistics; `MutableQuantiles` maintains an online estimator and periodically rolls previous snapshots; `MutableRollingAverages` gathers thread-local state before snapshotting. Aggregated rates initialize from protocol methods or explicit names, creating per-method metrics lazily or during initialization.

Rolling file sink behavior is time-window based. Initialization reads base path, source, append/error settings, roll interval, random offset, security keytab/principal keys, and filesystem configuration. `setInitialFlushTime` computes an initial roll point with random offset; `updateFlushTime` advances by whole intervals while preserving that offset. `putMetrics` writes records under a GMT interval directory to a host/source-specific log file, using append when allowed and supported or sequence-suffixed files when append is disabled or unavailable.

## State and persistence behavior

Writable and TFile utilities define persistent wire formats: compressed byte arrays/strings, VInt/VLong encodings, enum names, string arrays, TFile key strings, and raw comparator byte ranges. Any change to these encodings would affect RPC compatibility, sequence/TFile data, and persisted metadata readers. `WritableComparator`'s comparator registry and `WritableFactories`' factory registry are process-global mutable state; registered entries affect all subsequent deserialization/comparison paths in the JVM.

Compression streams persist data to the wrapped output stream in codec-specific format and read it from the wrapped input stream. Codec engine objects are stateful and often native-resource backed; `reset`, `reinit`, `finish`, `finished`, and `end` determine whether pooled instances can safely be reused. `CodecPool` itself is global mutable process state that tracks leased compressor/decompressor objects.

`ECSchema` is a serializable-style value object for erasure-code policy metadata, but this XML range only exposes ordinary constructor/getter/equality APIs. Its option keys and equality/hash behavior are important because schemas may be used in policy maps, configuration, logs, and RPC payloads.

Metrics framework state is split between immutable published records and mutable source registries. `MetricsRegistry` owns tags and mutable metrics for a source; each mutable metric tracks a changed flag or accumulated statistics until snapshot. `DefaultMetricsSystem` is a singleton lifecycle manager and mini-cluster mode flag holder. `MBeans` registers external JVM MBean state under Hadoop's standard object-name convention.

Sink persistence depends on destination. `FileSink` writes to a local file or stream; `GraphiteSink` writes over a network connection to Graphite; `StatsDSink` emits StatsD line protocol to a daemon; and `RollingFileSystemSink` writes durable metrics logs through Hadoop `FileSystem`, commonly HDFS. Rolling file sink fields such as `basePath`, `nextFlush`, `allowAppend`, `ignoreError`, and static supplied test hooks directly shape where records are stored, when files roll, and whether write failures propagate.

`MetricsCache` is an in-memory state store for sink-side reconstruction of full records from sparse updates. `Servers.parse` is stateless. `AbstractDNSToSwitchMapping` stores a `Configuration` reference in subclasses/base state, but the visible constructor notes it does not invoke subclass configuration logic automatically.

## Dependencies and integration points

This chunk depends on Hadoop core interfaces including `Configuration`, `Configurable`, `Writable`, `WritableComparable`, `RawComparator`, `Path`, `IOStatistics`, metrics interfaces, and `FileSystem`. It also uses Java platform types such as `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `ByteBuffer`, `Class`, `Map`, `Collection`, `Calendar`, `Date`, `Closeable`, `ObjectName`, and socket address parsing.

Compression APIs integrate with codec implementations for zlib/default, gzip, bzip2, passthrough, lz4, snappy, and zstandard. The XML exposes suffix constants for several codecs even when their implementation classes are outside this range. `CompressionCodecFactory` integrates with configuration key `io.compression.codecs` and Java service discovery. `CodecPool` integrates with all codecs that expose reusable compressor/decompressor objects.

TFile integrates with raw byte comparators, Hadoop `Text`-compatible string encoding, and compression algorithm names. Serializer bindings integrate with Java `Serializable`, Hadoop `Writable`, and Avro reflect/specific classes, with configuration keys controlling Avro schema and reflect package acceptance.

Metrics APIs integrate with Hadoop daemons and libraries that expose sources through annotations, mutable registries, or direct `MetricsSource` implementations. Sinks integrate with Apache Commons Configuration `SubsetConfiguration`, Log4J appenders, JMX/MBeanServer, Graphite, StatsD, local files, and Hadoop `FileSystem` targets such as HDFS, local FS, S3-compatible filesystems, or any configured filesystem. `RollingFileSystemSink` additionally integrates with Kerberos by reading configured keytab/principal keys and with filesystem append semantics.

The partial net package entry integrates with `DNSToSwitchMapping`, which is the rack-resolution interface used by HDFS, YARN, and cluster placement logic, though the full mapping API lies outside this chunk.

## Risks and edge cases

- Raw comparator correctness is high risk. A custom `WritableComparator.compare(byte[], ...)` must match object-level `compareTo` exactly, handle VInt/VLong offsets correctly, and be thread-safe if registered globally.
- `WritableComparator` fallback comparison deserializes two key objects, which can be expensive in sort-heavy code and can fail if factories or constructors are unavailable.
- `WritableFactories` and comparator registration are global mutable state, so tests and plugins can leak behavior across unrelated code in the same JVM.
- VInt/VLong boundaries, negative encodings, encoded-size calculation, and `readVIntInRange` bounds are compatibility-critical. Off-by-one errors can corrupt data or allow oversized allocations.
- Compression objects are stateful. Returning a compressor/decompressor to `CodecPool` without reset/reinit discipline, continuing to use a returned object, or missing `end` on non-pooled objects can cause data corruption or native-resource leaks.
- `CompressionInputStream.seek` and `seekToNewSource` are documented as unsupported in the base class; callers must not assume arbitrary compressed streams are seekable unless using a split-aware codec contract.
- Splittable compression changes effective start/end offsets after stream creation. Record readers must use `getAdjustedStart` and `getAdjustedEnd` rather than the originally requested byte range.
- `PassthroughCodec` intentionally does not transform data, so code that treats every codec as reducing or validating compressed format may mis-handle it.
- `CodecPool` leased-count APIs are useful for detecting leaks; nonzero counts after jobs/tests indicate compressors or decompressors were not returned.
- `ECSchema` equality and option maps can be sensitive to missing required keys, extra options, and map mutability. Callers should avoid mutating option maps after construction unless implementation defensively copies them.
- TFile comparator names and compression labels are stringly typed. Unsupported algorithms, missing Java comparator classes, or inconsistent raw comparator ordering can make files unreadable or incorrectly sorted.
- Java serialization is fragile across class evolution and should not be assumed compatible with Writable/Avro serializers. Avro reflect package configuration and schema keys control which classes are accepted.
- Metrics builder APIs are fluent but order-sensitive for record construction. Missing `endRecord`, wrong context tags, duplicate metric names, or forgotten `changed` flags can produce incomplete or stale metrics.
- Metrics filters can exclude by name, tag, tag collection, or whole record. Misconfigured glob/regex patterns may silently suppress operational data.
- RollingFileSystemSink's Javadoc warns that the documented `ignore-error` behavior is subtle: failures may be swallowed or propagated depending on configuration, so operators/tests must validate actual behavior for their setting.
- Rolling file append support varies by filesystem. When append is unavailable, concurrent daemons on one host rely on source names and sequence suffixes; when append is enabled on HDFS, insufficient datanodes can make appended data unreadable even after a successful append call.
- Rolling file directory names use GMT interval boundaries and randomized initial offsets. Tests should not rely on local timezone or exact roll time without controlling clocks/random offsets.
- StatsD and Graphite sinks depend on network availability and formatting conventions; metric names/tags containing unexpected punctuation can affect downstream parsing.
- `AbstractDNSToSwitchMapping(Configuration)` does not call `setConf`, so subclass constructors that assume `setConf` side effects may be partially initialized.

## Test signals

Useful tests for code using or changing this API surface should include:

- Comparator compatibility tests that compare raw-byte and object-level `WritableComparable` ordering over normal, empty, negative, and malformed inputs.
- Registry isolation tests for `WritableComparator.define` and `WritableFactories.setFactory`, including non-public writable construction and cleanup between tests.
- VInt/VLong golden-vector tests for boundary values around one-byte encodings, negative encodings, maximum/minimum int/long, encoded sizes, and range-check failures.
- WritableUtils tests for compressed byte arrays/strings, null or empty strings where supported, string arrays, enum round trips, `skipFully` EOF behavior, and clone compatibility.
- Codec stream tests for write/finish/close/reset lifecycle, dictionary handling, EOF behavior, byte counters, IOStatistics passthrough, and native-resource cleanup.
- CodecPool leak tests that lease and return compressors/decompressors and assert leased counts return to zero.
- CompressionCodecFactory tests for configured codecs, service-loaded codecs, default built-ins, suffix selection, class-name/simple-name lookup, alias lookup, and suffix removal.
- Splittable codec tests that create streams over nonzero start/end offsets and assert adjusted boundaries are used by record readers.
- ECSchema tests for construction from maps and explicit arguments, required key validation, extra option preservation, equality/hashCode stability, and log-friendly string output.
- TFile utility tests for VInt/VLong/string golden encodings, lower/upper-bound behavior with duplicates and edge positions, comparator creation from `memcmp` and Java-class names, and supported compression algorithm names.
- Serializer tests covering Java, Writable, Avro reflect, and Avro specific acceptance/rejection rules, schema configuration, and comparator behavior for serialized Java objects.
- EventCounter tests that append warning/error/fatal events and verify counted metrics without requiring a layout.
- Metrics source tests that register with `MetricsSystem`, build records with tags/context/counters/gauges, snapshot mutable metrics only when expected, and publish immediately to a test sink.
- Mutable metric tests for changed-flag lifecycle, counter monotonicity, gauge increment/decrement/set, `MutableStat` extended stats and min/max reset, rate aggregation, quantile estimator rolling, rolling-average thread-local collection, and `close` cleanup.
- Metrics filter tests for glob and regex acceptance across names, tags, tag sets, and full records.
- Sink tests for FileSink output formatting, Graphite connection failure behavior, StatsD line formatting and close behavior, and RollingFileSystemSink roll scheduling, sequence suffix selection, append/no-append modes, GMT directory naming, Kerberos key lookup, and failure propagation under both ignore-error settings.
- MBeans tests for object-name construction with and without extra properties, service/name extraction, duplicate registration handling, and unregister idempotence.
- MetricsCache tests for sparse update reconstruction, tag inclusion/exclusion behavior, lookup by name/tags, and max-record eviction behavior.
- Servers.parse tests for null input, comma/space combinations, default ports, explicit ports, IPv6 or invalid host specs where supported, and whitespace trimming.
- AbstractDNSToSwitchMapping subclass tests that verify configuration is cached but subclass-specific `setConf` logic is only run when explicitly invoked.
