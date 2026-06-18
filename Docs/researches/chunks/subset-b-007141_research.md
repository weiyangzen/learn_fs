# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 24233-30540

## Scope

This chunk is part 5 of the Hadoop Common 2.10.0 JDiff API snapshot. It starts at the tail of `org.apache.hadoop.io.compress.GzipCodec`, covers complete API sections for split compression streams, TFile metadata utilities, Hadoop serialization adapters, old and new metrics APIs, metrics sinks, network topology/socket helpers, and the start of the deprecated `org.apache.hadoop.record` package. The range ends inside the `RecordOutput` interface after `writeInt`, so the record output contract continues in the following chunk.

Because this is a JDiff XML file, it records public/protected API surface, inheritance, deprecation, method signatures, exceptions, fields, and embedded Javadoc. It does not contain Java method bodies. Control flow and persistence notes below are therefore inferred from the exposed contracts and documented behavior, not from implementation statements.

## Purpose

The source file is a compatibility and documentation artifact for Hadoop Common's public API. It lets release tooling compare API signatures across Hadoop versions and helps downstream consumers understand which classes, methods, constants, and deprecations are visible in Hadoop Common 2.10.0.

This chunk concentrates on infrastructure APIs used by storage formats, serialization, monitoring, network placement, and legacy record I/O. The most active parts are the `metrics2` APIs and sinks, the TFile byte-container helpers, and network topology mapping contracts. Several older APIs are preserved but explicitly deprecated in favor of newer systems: `org.apache.hadoop.metrics.*` and `org.apache.hadoop.metrics.spi.*` point users to `metrics2`, and `org.apache.hadoop.record.*` points users to Avro.

## Important APIs, Types, and Functions

### Split compression and TFile

- `org.apache.hadoop.io.compress.GzipCodec` exposes `createDirectDecompressor()` and `getDefaultExtension()` in this tail, confirming gzip codec integration with direct decompression and default suffix discovery.
- `SplitCompressionInputStream` extends `CompressionInputStream` and carries an adjusted compressed-stream range. Its constructor accepts an input stream plus requested `start` and `end`; protected `setStart()`/`setEnd()` let codec implementations adjust the range; `getAdjustedStart()` and `getAdjustedEnd()` expose the post-adjustment offsets to callers.
- `SplittableCompressionCodec` extends `CompressionCodec` and adds `createInputStream(InputStream seekableIn, Decompressor decompressor, long start, long end, READ_MODE readMode)`. The contract is for codecs that can decompress from arbitrary compressed offsets, with `READ_MODE` controlling position reporting.
- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are TFile metadata exceptions for duplicate or missing meta blocks.
- `RawComparable` models a byte-array slice with `buffer()`, `offset()`, and `size()`, to be compared by an external `RawComparator`.
- `TFile` documents Hadoop's typed-less key/value file container: block compression, named meta blocks, sorted or unsorted keys, seek by key or file offset, key size limited to 64KB, and value size limited practically by storage. It exposes `makeComparator(String)`, `getSupportedCompressionAlgorithms()`, `main(String[])`, compression constants `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, and comparator constants `COMPARATOR_MEMCMP`, `COMPARATOR_JCLASS`.
- `Utils` provides TFile support routines: variable-length integer encoding/decoding (`writeVInt`, `writeVLong`, `readVInt`, `readVLong`), Text-style string encoding (`writeString`, `readString`), and generic `lowerBound`/`upperBound` binary search helpers with and without explicit comparators.

### Serialization adapters

- `JavaSerialization` implements `Serialization` for Java `Serializable` classes and is marked experimental.
- `JavaSerializationComparator` extends `DeserializerComparator`; it deserializes objects with Java serialization and compares them through `Comparable`.
- `WritableSerialization` extends `Configured` and implements `Serialization`, delegating to `Writable.write(DataOutput)` and `Writable.readFields(DataInput)`.
- The package doc records the integration point: `io.serializations` selects the configured `Serialization` implementations that can create `Serializer` and `Deserializer` instances.
- `org.apache.hadoop.io.serializer.avro.AvroReflectSerializable` is a marker interface for Avro reflection serialization.
- `AvroReflectSerialization`, `AvroSerialization`, and `AvroSpecificSerialization` provide Avro-backed serialization classes. `AvroReflectSerialization` exposes `AVRO_REFLECT_PACKAGES` for configured package acceptance, while `AvroSerialization` exposes `AVRO_SCHEMA_KEY`.

### Log and metrics v1

- `org.apache.hadoop.log.metrics.EventCounter` is a Log4J `AppenderSkeleton` that counts events by log level. It exposes `append(LoggingEvent)`, `close()`, and `requiresLayout()`.
- `org.apache.hadoop.metrics` has package-level API documentation for reporting performance metric information, but the active class definitions in this chunk are mostly in deprecated SPI packages.
- `org.apache.hadoop.metrics.ganglia.GangliaContext` extends `AbstractMetricsContext` and is deprecated in favor of `org.apache.hadoop.metrics2.sink.ganglia.GangliaSink30`. It sends metrics via UDP datagrams to configured Ganglia servers, with public/protected fields for XDR buffer state, server list, and socket. It exposes `emitMetric`, `getUnits`, `getSlope`, `getTmax`, `getDmax`, `xdr_string`, and `xdr_int`.
- `org.apache.hadoop.metrics.spi.AbstractMetricsContext` is the deprecated v1 SPI root. It manages context initialization, factory attributes, monitoring lifecycle, record creation, updater registration, buffered record updates/removal, emission, flushing, timer period parsing, and access to all records.
- Deprecated v1 SPI helpers include `CompositeContext`, `MetricsRecordImpl`, `MetricValue`, `NoEmitMetricsContext`, `NullContext`, `NullContextWithUpdateThread`, `OutputRecord`, and `Util.parse`.

### Metrics2 core and builders

- `AbstractMetric` is an immutable metric with `MetricsInfo`, `value()`, `type()`, visitor dispatch, equality, hash, and string conversion.
- `MetricsCollector` builds records by name or `MetricsInfo`.
- `MetricsException` is the runtime wrapper for metrics failures.
- `MetricsFilter` accepts or rejects names, tags, tag collections, and records.
- `MetricsInfo` exposes immutable metric/tag metadata: `name()` and `description()`.
- `MetricsJsonBuilder` and `MetricStringBuilder` extend `MetricsRecordBuilder` to render metrics as JSON or delimited strings while supporting tags, context, counters, gauges, parent collector access, and `toString()`.
- `MetricsPlugin` defines plugin initialization with `SubsetConfiguration`.
- `MetricsRecord` is an immutable snapshot with timestamp, name, description, context, tags, and metric iterable.
- `MetricsRecordBuilder` is the fluent interface for adding tags, pre-made metrics, context, int/long counters, int/long/float/double gauges, ending records, and returning the parent collector.
- `MetricsSink` consumes `MetricsRecord` objects and flushes buffered output.
- `MetricsSource` exposes `getMetrics(MetricsCollector, boolean all)`.
- `MetricsSystem` registers/unregisters sources and callbacks, publishes metrics immediately, and shuts down. `MetricsSystemMXBean` exposes start/stop, metrics MBean lifecycle, and current configuration through JMX.
- `MetricsTag` is immutable grouping metadata with `MetricsInfo` plus a string value.
- `MetricsVisitor` is the double-dispatch visitor for int/long/float/double gauges and int/long counters.

### Metrics2 annotation, filters, registry, and mutables

- `@Metric` and `@Metrics` annotation interfaces mark single metrics and metric groups.
- `GlobFilter` and `RegexFilter` extend `AbstractPatternFilter` and compile glob or regex patterns for metrics filtering.
- `DefaultMetricsSystem` is an enum singleton facade exposing `initialize(String)`, `instance()`, and `shutdown()`.
- `Interns` interns `MetricsInfo` and `MetricsTag` instances through `info()` and `tag()` overloads.
- `MetricsRegistry` owns a record name or `MetricsInfo`, looks up metrics and tags, creates counters, gauges, quantiles, stats, rates, rates with aggregation, rolling averages, records tags, adds samples by metric name, sets context, snapshots all mutable metrics into a builder, and stringifies the registry.
- `MutableMetric` is the base mutable metric with `snapshot(builder, all)`, changed-flag management, and `changed()`.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` model monotonic counters with `incr()` overloads, value accessors, and snapshots.
- `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong` model gauges with `incr`, `decr`, `set`, value accessors, and snapshots.
- `MutableQuantiles` estimates quantiles for long streams and exposes `add`, `snapshot`, `stop`, `getInterval`, `getEstimator`, `setEstimator`, static `quantiles`, and protected `previousSnapshot`.
- `MutableRate`, `MutableRates`, `MutableRatesWithAggregation`, `MutableRollingAverages`, and `MutableStat` support latency/throughput statistics. The docs call out important concurrency semantics: `MutableRates` synchronizes all access and can contend, while `MutableRatesWithAggregation` uses per-thread local state and can lose samples produced by threads that die before the next snapshot. `MutableStat.add(numSamples, sum)` can preserve means while producing inaccurate variance for large aggregated batches.

### Metrics2 sinks and utilities

- `FileSink`, `GraphiteSink`, and `StatsDSink` implement `MetricsSink` and `Closeable`, with `init(SubsetConfiguration)`, `putMetrics`, `flush`, and `close`. `StatsDSink` also exposes `writeMetric(String)` and documents StatsD line shape plus configuration keys.
- `RollingFileSystemSink` implements `MetricsSink` and `Closeable` for filesystem-backed rolling metric logs. It exposes testable constructors, `init`, `getRollInterval`, `updateFlushTime`, `setInitialFlushTime`, `putMetrics`, `flush`, and `close`; protected/static fields include `source`, `ignoreError`, `allowAppend`, `basePath`, roll intervals, `nextFlush`, `forceFlush`, `hasFlushed`, `suppliedConf`, and `suppliedFilesystem`.
- `RollingFileSystemSink` integrates with Hadoop `FileSystem`, supports local/HDFS/S3-style paths, creates time-interval directories in GMT, supports optional append, random roll offsets to spread load, secure Kerberos properties, and error-swallowing behavior through `ignore-error`.
- `MBeans` registers and unregisters standard Hadoop MBeans under `hadoop:service=<serviceName>,name=<nameName>` and can extract service/name parts from an `ObjectName`.
- `MetricsCache` caches dense sink-side records for sinks that do not support sparse updates. It supports fixed-capacity construction, `update` overloads, and `get`.
- `Servers.parse` parses comma/space-separated server specs into socket addresses.

### Network APIs

- `AbstractDNSToSwitchMapping` is the base class for rack/topology mapping and implements Hadoop configuration support. It exposes `isSingleSwitch`, diagnostic `getSwitchMap`, `dumpTopology`, script-policy checks, and static `isMappingSingleSwitch`.
- `CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping`, caches hostname/IP-to-switch results, exposes the raw mapping field, supports `resolve`, `getSwitchMap`, `reloadCachedMappings()` overloads, `isSingleSwitch`, and `toString`.
- `ConnectTimeoutException` extends `SocketTimeoutException` for `NetUtils.connect` timeout failures.
- `DNSToSwitchMapping` is the pluggable topology interface: `resolve(List<String>)`, `reloadCachedMappings()`, and `reloadCachedMappings(List<String>)`.
- `ScriptBasedMapping` extends `CachedDNSToSwitchMapping`, supports constructors for default/raw/configuration-backed mappings, exposes `NO_SCRIPT`, and delegates configuration to a script-based raw mapper.
- `SocksSocketFactory` extends `SocketFactory` and implements `Configurable`; it creates sockets through an optional SOCKS proxy and implements equality/hash based on proxy/config state.
- `StandardSocketFactory` extends `SocketFactory` for normal sockets.
- `TableMapping` extends `CachedDNSToSwitchMapping`, is configurable, and reloads mappings from a table file.

### Deprecated record I/O

- `BinaryRecordInput` and `BinaryRecordOutput` implement `RecordInput`/`RecordOutput`, expose constructors over streams and `DataInput`/`DataOutput`, thread-local `get(...)` factories, primitive read/write methods, buffer read/write, and record/vector/map start/end methods.
- `Buffer` is a deprecated byte-sequence value type used by record I/O. It exposes constructors over no bytes, a byte array, or a byte range; `set`, `copy`, `get`, `getCount`, `getCapacity`, `setCapacity`, `reset`, `truncate`, `append` overloads, `hashCode`, `compareTo`, `equals`, encoding-aware `toString`, and `clone`.
- `CsvRecordInput` and `CsvRecordOutput` provide CSV-backed record serialization with primitive, string, buffer, record, vector, and map methods.
- `Index` is the vector/map deserialization iterator, with `done()` and `incr()`.
- `Record` is the abstract generated-record base class implementing `WritableComparable` and `Cloneable`. It requires tagged `serialize`, tagged `deserialize`, and `compareTo`, and supplies untagged `serialize`, untagged `deserialize`, `write(DataOutput)`, `readFields(DataInput)`, and `toString`.
- `RecordComparator` extends `WritableComparator`, requires raw byte comparison, and exposes synchronized static `define(Class, RecordComparator)` for optimized record comparators.
- `RecordInput` defines the full tagged deserialization contract for primitive values, strings, `Buffer`, record boundaries, vector boundaries, and map boundaries.
- `RecordOutput` begins in this chunk and defines tagged serialization for `writeByte`, `writeBool`, and `writeInt` before the chunk boundary. The remainder of `RecordOutput` is outside this range.

## Control Flow

The XML is structured as a package/class/member stream. JDiff consumers read each `<package>`, then nested class/interface declarations, constructors, methods, fields, implemented interfaces, exceptions, parameters, deprecation markers, and documentation blocks. For this chunk, the effective flow is API enumeration rather than executable control flow.

At the API-contract level, common runtime flows exposed here are:

- Split compression callers select a `SplittableCompressionCodec`, request a `SplitCompressionInputStream` for compressed offsets, then inspect adjusted start/end offsets because codecs may shift boundaries to valid compression block positions.
- TFile users choose compression/comparator constants, create/read TFile data blocks and meta blocks through APIs documented elsewhere in the XML, use `RawComparable` slices for raw key comparison, and use `Utils` to encode compact integer/string metadata and perform sorted-index searches.
- Serialization users configure `io.serializations`; Hadoop asks each `Serialization` implementation whether it accepts a class, then obtains serializers/deserializers. Writable serialization delegates to `Writable`; Java serialization and Avro variants integrate with their respective object models.
- Metrics2 sources push current values into a `MetricsCollector`/`MetricsRecordBuilder`; mutable metrics snapshot changed or all values into builders; the `MetricsSystem` publishes records to configured sinks; sinks flush or close their output targets.
- Network topology mapping resolves hostnames to rack paths through raw, cached, script, or table-backed `DNSToSwitchMapping` implementations. Cache reload calls invalidate all or selected entries.
- Deprecated record objects serialize and deserialize by walking record boundaries, primitive fields, buffers, vectors, and maps. `Index` controls vector/map iteration on read, and `RecordComparator` allows byte-level comparison without full object construction.

## State and Persistence Behavior

Most state described by this chunk is API-level or in-memory:

- `SplitCompressionInputStream` retains adjusted range state for callers that split compressed inputs.
- TFile's persistent format is explicitly documented: key/value bytes, compressed data blocks, named meta blocks, sorted/unsorted key support, block indexes, meta-block indexes, and configurable chunk/input/output buffer sizes. The documented memory footprint scales with compressed block codecs, temporary key/value buffers, data-block index count, and meta-block index count.
- TFile `Utils` encodes variable-length integers and strings into persistent binary form. Any incompatible change to these encodings would break on-disk compatibility.
- `MetricsRegistry` and the mutable metrics classes hold live process metrics: changed flags, counters, gauges, quantile estimators, rolling windows, rate maps, and last-snapshot statistics.
- `MutableQuantiles`, `MutableRollingAverages`, `MutableRatesWithAggregation`, and `MutableStat` maintain internal sample history or thread-local aggregation, so snapshot timing affects emitted values.
- `RollingFileSystemSink` writes persistent metric log files through `FileSystem` and has state for base path, roll interval, next flush time, append behavior, and supplied testing filesystem/configuration. It also documents HDFS append and file-size visibility limitations.
- `GangliaContext`, `GraphiteSink`, and `StatsDSink` emit metrics to external systems; their durable state lives outside Hadoop once packets or lines are accepted by those systems.
- `CachedDNSToSwitchMapping` stores an in-memory host-to-switch cache and exposes diagnostic copies; `TableMapping` reloads file-backed mappings.
- `Buffer` owns mutable byte-array capacity/count state. `Record` bridges deprecated record serialization with Hadoop `Writable` persistence through `write` and `readFields`.

## Dependencies and Integration Points

- Compression APIs depend on `CompressionCodec`, `CompressionInputStream`, `Decompressor`, `DirectDecompressor`, and codec-specific split/read-mode behavior.
- TFile APIs integrate with `java.io.DataInput/DataOutput`, `java.util.Comparator`, `RawComparator`, Hadoop `Text`-style byte strings, compression codecs, and Hadoop `Configuration` keys `tfile.io.chunk.size`, `tfile.fs.output.buffer.size`, and `tfile.fs.input.buffer.size`.
- Serialization APIs integrate with Hadoop `Writable`, `Serialization`, `Serializer`, `Deserializer`, `RawComparator`, Avro reflect/specific APIs, and the `io.serializations` configuration property.
- Metrics v1 integrates with Log4J, Ganglia UDP/XDR, `ContextFactory`, `MetricsRecord`, updater callbacks, and the deprecated `org.apache.hadoop.metrics` package.
- Metrics2 integrates with Apache Commons Configuration `SubsetConfiguration`, JMX through `MetricsSystemMXBean` and `MBeans`, sinks, sources, collectors, records, visitors, annotations, filters, and mutable metric registries.
- Filesystem metrics sinks depend on Hadoop `FileSystem`, `Path`, `Configuration`, optional Kerberos keytab/principal properties, append support, and the semantics of the destination filesystem.
- Network helpers integrate with Hadoop `Configurable`, `Configuration`, `SocketFactory`, Java `Proxy`, `Socket`, `SocketAddress`, DNS resolution, external topology scripts, and table mapping files.
- Deprecated record I/O integrates with `WritableComparable`, `WritableComparator`, `DataInput/DataOutput`, Java collections for vectors/maps, generated record classes, and Avro migration guidance.

## Risks and Edge Cases

- This XML is generated API metadata. Research consumers must not infer private implementation behavior from it; method-body details, synchronization internals, resource cleanup, and error paths are absent unless documented in Javadoc or signature flags.
- The chunk begins mid-class (`GzipCodec`) and ends mid-interface (`RecordOutput`). Merge/reconciliation must combine adjacent chunks before treating the source-file research as complete.
- `SplittableCompressionCodec` explicitly allows start/end offsets to change. Callers that continue using requested offsets instead of `getAdjustedStart()`/`getAdjustedEnd()` can duplicate or skip decompressed data around split boundaries.
- TFile's documented concurrency limitation says multiple scanners on the same TFile may serialize actual I/O because implementation uses `seek()+read()`. Random-access and multi-threaded readers need tests around shared stream behavior.
- TFile `Utils` variable-length integer encoding is a compatibility boundary. Boundary values near one-, two-, three-, and wider-byte transitions should be preserved exactly.
- Java serialization is marked experimental and compares through deserialized `Comparable` objects, which can be slow, classloader-sensitive, and unsafe for untrusted data.
- Deprecated metrics v1 and record APIs remain public. Removing or changing signatures would break compatibility even if users are expected to migrate to `metrics2` or Avro.
- `MutableRatesWithAggregation` documents that samples can be lost when short-lived threads exit before snapshot. It should not be used where every event must be counted exactly.
- `MutableStat.add(numSamples, sum)` warns that variance may be inaccurate for large aggregate batches even when the mean is correct.
- `RollingFileSystemSink` has filesystem-specific risks: append may not be supported, HDFS append requires enough data nodes, file sizes may not update until close, and `ignore-error` can hide write failures when set to its permissive behavior.
- `RollingFileSystemSink` exposes static testing hooks (`forceFlush`, `hasFlushed`, `suppliedConf`, `suppliedFilesystem`), which are useful for tests but can create global-state coupling if misused.
- Topology mapping depends on DNS, scripts, or mapping files. Cache reload semantics must be exercised, especially selected-node reloads.
- SOCKS and standard socket factories implement equality/hash behavior; misconfigured proxy state could affect factory reuse in connection caches.
- Deprecated record CSV/binary APIs rely on tagged field names for XML/CSV-style formats and on `Index` iteration for collections. Generated records must keep read/write order and comparator definitions consistent.

## Test Signals

- JDiff/API tests should verify that this XML remains parseable across chunk boundaries and that class/interface/member names, deprecation text, visibility, static/final flags, exceptions, and implemented interfaces are preserved.
- Compression tests should cover split gzip-adjacent codec behavior where codecs adjust start/end, `READ_MODE` differences, direct decompressor creation, and default extension reporting.
- TFile tests should cover supported compression names, raw comparator creation, duplicate/missing meta block exceptions, VInt/VLong round trips at all documented boundary ranges, string encoding round trips, and lower/upper-bound results with duplicate keys.
- Serialization tests should exercise `io.serializations` selection for Writable, Java Serializable, Avro reflect marker classes, Avro reflect package configuration, and Avro specific classes.
- Metrics2 tests should validate builder chaining, tags/context propagation, source-to-sink publication, immediate `publishMetricsNow`, shutdown behavior, JMX lifecycle, filters, annotations, and visitor dispatch for each primitive metric type.
- Mutable metrics tests should cover changed-flag snapshots, all-vs-changed snapshots, counter monotonicity, gauge set/incr/decr, quantile estimator snapshots/stopping, rolling-average window eviction, rate aggregation under multiple threads, and `MutableStat` min/max reset.
- Sink tests should cover file, Graphite, StatsD, and rolling filesystem output, including flush/close idempotence, invalid configuration, HDFS/local paths, roll interval parsing, roll offset scheduling, append/no-append behavior, Kerberos property requirements, and `ignore-error` behavior.
- MBean and metrics cache tests should verify canonical object names, unregister handling, sparse update densification, capacity behavior, and server-spec parsing.
- Network tests should cover cache hits/misses, full and partial cache reloads, script-disabled `NO_SCRIPT` behavior, table reload behavior, single-switch detection, socket factory proxy creation, equality/hash semantics, and connect-timeout exception propagation.
- Record I/O tests should cover binary and CSV primitive round trips, `Buffer` capacity/count/truncate/append/clone/compare behavior, vector/map `Index` iteration, generated `Record.write/readFields` compatibility, and `RecordComparator.define` lookup behavior.

## Cross-Chunk Notes

Adjacent chunks are required for a complete view of this XML source. `subset-b-007140` contains the earlier part of `GzipCodec` and preceding Hadoop Common APIs. `subset-b-007142` continues the remainder of `RecordOutput` and subsequent packages. The merge lane should retain this document's note that all behavior here is API-contract research from JDiff XML rather than implementation-level Java code.
