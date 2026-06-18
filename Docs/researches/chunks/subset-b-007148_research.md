# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.2.xml lines 24283-30579

## Scope

This chunk covers a large slice of the Hadoop Common 2.10.2 public API snapshot stored as JDiff XML. It starts at the end of `org.apache.hadoop.io.compress.DefaultCodec`, covers compression interfaces, TFile utilities, serialization adapters, legacy and current metrics APIs, metrics sinks, network topology mapping helpers, socket factories, and the beginning of the deprecated `org.apache.hadoop.record` API. The range ends inside `RecordInput.readString`, so the complete `RecordInput` and later record APIs must be reconciled with the next chunk.

Because this file is generated API metadata, it does not contain method bodies. The research below describes the public contracts, state implied by exposed fields and documentation, integration points, and risks for consumers of these APIs.

## Purpose

The purpose of this XML section is to preserve the Hadoop Common public Java API for compatibility comparison. It records package names, classes/interfaces, inheritance, implemented interfaces, constructors, methods, parameters, exceptions, fields, visibility, synchronization flags, deprecation status, and Javadoc text.

The covered APIs form several subsystems:

- Compression stream creation and splittable/direct decompression contracts.
- TFile raw byte-key container metadata, compression constants, and helper encodings.
- Hadoop serialization adapters for Java serialization, Writable serialization, and Avro reflect/specific serialization.
- The deprecated Hadoop metrics v1 SPI plus the Hadoop metrics2 source/collector/sink/registry model.
- Metrics sinks that write to files, HDFS-compatible file systems, Graphite, and StatsD.
- JMX registration helpers and metrics caches.
- Network topology resolution from DNS/IP names to rack paths, including cached, script-based, and table-based implementations.
- Socket factory abstractions for standard and SOCKS sockets.
- Deprecated record I/O primitives replaced by Avro.

## Important APIs, Types, and Data

Compression APIs in `org.apache.hadoop.io.compress` include `DirectDecompressionCodec`, `DirectDecompressor`, `GzipCodec`, `SplitCompressionInputStream`, and `SplittableCompressionCodec`. `DirectDecompressionCodec.createDirectDecompressor()` returns a `DirectDecompressor` for direct `ByteBuffer` decompression. `GzipCodec` extends `DefaultCodec` and exposes standard compressor/decompressor factory methods plus `createDirectDecompressor()` and `getDefaultExtension()`. `SplitCompressionInputStream` stores adjusted compressed-stream range boundaries and exposes `getAdjustedStart()` and `getAdjustedEnd()`. `SplittableCompressionCodec.createInputStream()` accepts a seekable compressed stream, decompressor, start/end offsets, and read mode so codecs can align split boundaries to block or format constraints.

The TFile section includes `MetaBlockAlreadyExists`, `MetaBlockDoesNotExist`, `RawComparable`, `TFile`, and `Utils`. `TFile` exposes compression constants `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, comparator constants `COMPARATOR_MEMCMP` and `COMPARATOR_JCLASS`, `makeComparator()`, `getSupportedCompressionAlgorithms()`, and a dump-oriented `main()`. Its documentation describes TFile as a byte-key/byte-value container with block compression, named metadata blocks, sorted or unsorted keys, and seek by key or file offset. `RawComparable` represents a byte-array slice via `buffer()`, `offset()`, and `size()`. `Utils` provides TFile-facing variable-length integer/string encodings and lower/upper-bound binary searches with optional comparators.

Serialization APIs include `JavaSerialization`, `JavaSerializationComparator`, `WritableSerialization`, `AvroReflectSerializable`, `AvroReflectSerialization`, `AvroSerialization`, and `AvroSpecificSerialization`. The Avro package exposes configuration keys such as `AVRO_REFLECT_PACKAGES` and `AVRO_SCHEMA_KEY`, with reflect serialization applying to configured package lists or marker-interface implementors and specific serialization applying to Avro generated classes.

The legacy metrics v1 API is represented by `EventCounter`, `GangliaContext`, and `org.apache.hadoop.metrics.spi` classes. `EventCounter` is a Log4J appender that counts fatal, error, and warn events. `GangliaContext` extends `AbstractMetricsContext`, uses UDP datagrams, and exposes XDR helpers plus fields for buffer, offset, metrics servers, and datagram socket. `AbstractMetricsContext` is the SPI base that manages a buffered table of metric records, a timer period, updater callbacks, start/stop monitoring, and `emitRecord()`/`flush()` hooks. `MetricsRecordImpl` keeps tags and metrics, supports set/increment operations for primitive numeric types, and delegates `update()`/`remove()` back to its context. These metrics v1 APIs are deprecated in favor of metrics2.

The metrics2 core API includes immutable metadata/value types (`MetricsInfo`, `AbstractMetric`, `MetricsTag`, `MetricsRecord`), builders and visitors (`MetricsCollector`, `MetricsRecordBuilder`, `MetricsJsonBuilder`, `MetricStringBuilder`, `MetricsVisitor`), plugins (`MetricsPlugin`, `MetricsSource`, `MetricsSink`, `MetricsFilter`), and lifecycle control (`MetricsSystem`, `MetricsSystemMXBean`, `DefaultMetricsSystem`). Metrics are collected from `MetricsSource.getMetrics(collector, all)`, built through a fluent `MetricsRecordBuilder`, and pushed to sinks with `MetricsSink.putMetrics()` followed by optional `flush()`.

Metrics2 registry and mutable metric classes include `Interns`, `MetricsRegistry`, `MutableMetric`, `MutableCounter`, `MutableCounterInt`, `MutableCounterLong`, `MutableGauge`, `MutableGaugeInt`, `MutableGaugeLong`, `MutableQuantiles`, `MutableRate`, `MutableRates`, `MutableRatesWithAggregation`, `MutableRollingAverages`, and `MutableStat`. `MetricsRegistry` creates and stores counters, gauges, rates, quantiles, rolling averages, stats, and tags, and snapshots them into a builder. Mutable metrics track changed state so snapshots can include only changed metrics unless `all` is requested. Quantiles and rolling averages add time-windowed or interval-based state and expose test or lifecycle hooks such as `stop()`, `close()`, `setEstimator()`, and `setRecordValidityMs()`.

Metrics sinks include `FileSink`, `GraphiteSink`, `RollingFileSystemSink`, and `StatsDSink`. `RollingFileSystemSink` is the most stateful: it writes metrics logs through Hadoop `FileSystem`, rolls directories at configured intervals, supports random roll offsets, optional append, Kerberos keytab/principal configuration, source labels, ignore-error behavior, and fields for base path, roll timing, supplied test filesystem/configuration, and static flush test controls. `StatsDSink` formats metrics as StatsD lines and exposes `writeMetric()`.

Metrics utilities include `MBeans`, `MetricsCache`, and `Servers`. `MBeans.register()` uses the standard Hadoop object name pattern `hadoop:service=<serviceName>,name=<nameName>`, with helpers to extract the service/name and unregister. `MetricsCache` stores recent metric records and can include tag values in the cached record, with a max-records-per-name constructor. `Servers.parse()` and the older metrics SPI `Util.parse()` parse comma/space separated host or host:port lists.

Network APIs in `org.apache.hadoop.net` include `AbstractDNSToSwitchMapping`, `CachedDNSToSwitchMapping`, `DNSToSwitchMapping`, `ScriptBasedMapping`, `TableMapping`, `ConnectTimeoutException`, `SocksSocketFactory`, and `StandardSocketFactory`. `DNSToSwitchMapping.resolve()` maps hostnames/IPs to rack paths while preserving list order; unresolved names conventionally map to `NetworkTopology.DEFAULT_RACK`. Cached mappings support full or per-host reload. Script-based mapping delegates to a configured topology script and caches results. Table mapping reads `net.topology.table.file.name`, treating it as a whitespace-separated host-to-rack file. The socket factories provide reflection-friendly socket creation, proxy-aware SOCKS configuration, equality/hash behavior, and `Configurable` integration for `SocksSocketFactory`.

The deprecated `org.apache.hadoop.record` section begins the pre-Avro record I/O stack. `BinaryRecordInput` and `BinaryRecordOutput` read and write primitive values, strings, buffers, records, vectors, and maps, with thread-local `get()` helpers over `DataInput`/`DataOutput`. `Buffer` is a mutable byte buffer with set/copy/get/count/capacity/truncate/append/compare/equals/string/clone operations. `CsvRecordInput` and `CsvRecordOutput` provide CSV-format equivalents. `Index` is an iterator-like interface for map/vector deserialization. `Record` is an abstract generated-class base implementing `WritableComparable` and `Cloneable`, bridging tagged record serialization/deserialization to Hadoop `Writable` `write()` and `readFields()`. `RecordComparator` registers optimized raw comparators via synchronized static `define()`.

## Control Flow

The XML itself has no runtime control flow. It is generated metadata consumed by API diff tooling. Runtime flow is only inferable from API contracts.

Compression flow starts when a caller asks a codec to create compression/decompression streams or direct decompressors. For splittable codecs, the caller supplies a compressed-stream start/end range; the codec may adjust those boundaries and returns a `SplitCompressionInputStream` whose adjusted offsets can be queried later. This is the API surface that lets input formats split compressed files for parallel processing when the compression format supports arbitrary or block-aligned starts.

TFile flow is container-oriented: writers choose compression and comparator names, data is arranged as compressed blocks plus named metadata blocks and indexes, and readers use byte-slice comparators and lower/upper-bound helpers to seek by key or offset. Variable-length integer and string helpers define the on-disk encoding primitives used by TFile internals and available to users.

Metrics v1 flow is context-driven. A `ContextFactory` creates a context, records buffer tag/metric updates in an internal table, registered updaters are called at configured intervals, and the context periodically emits buffered `OutputRecord` values through implementation-specific `emitRecord()` and `flush()`. `startMonitoring()` and `stopMonitoring()` control the timer; `close()` stops monitoring and frees buffered state.

Metrics2 flow is source/sink-driven. Sources implement `getMetrics()` and populate a collector. Builders assemble tags, counters, gauges, and immutable metrics. The metrics system registers sources, callbacks, and sinks, publishes periodically or via `publishMetricsNow()`, exposes lifecycle through an MXBean, and shuts down by unregistering its control MBean. Registries and mutable metrics serve source implementations by accumulating values and snapshotting them into records.

Metrics sink flow depends on target. File and Graphite sinks initialize from a `SubsetConfiguration`, receive `MetricsRecord` objects, write or buffer output, flush, and close. Rolling file-system sink additionally computes roll times, opens per-interval log paths, rolls based on GMT interval directories and randomized offsets, and may append or sequence log files depending on filesystem support and configuration. StatsD sink converts records to line protocol and writes individual metric lines.

Network topology flow resolves hostnames through the configured mapping implementation. Cached mapping wraps a raw mapping, serves known entries from cache, and can clear all or selected entries. Script-based mapping constructs the raw script mapping from configuration, then the outer class caches script results. Table mapping reloads a host-to-rack file and returns `/default-rack` for missing entries.

Record I/O flow is generated-code driven. Generated `Record` subclasses call `startRecord`, primitive read/write methods, `startVector`/`startMap`, iterate with `Index.done()` and `Index.incr()`, then end containers. `Record.write()` and `readFields()` bridge this custom format to Hadoop `Writable` serialization.

## State and Persistence

This XML chunk persists API state rather than application data: method signatures, fields, inheritance, deprecation markers, and documentation. Runtime state described by the APIs includes several important categories.

TFile persistent state is file-backed: compressed data blocks, named metadata blocks, block indexes, meta block indexes, comparator names, compression algorithms, key ordering, and variable-length encoded values. Configuration keys such as `tfile.io.chunk.size`, `tfile.fs.output.buffer.size`, and `tfile.fs.input.buffer.size` control chunk buffering and filesystem stream buffering. The docs warn that TFile reads use seek plus read on a shared `FSDataInputStream`, so multiple scanners may serialize actual I/O even when logical reads target different DFS blocks.

Metrics v1 state is buffered in memory in `AbstractMetricsContext`: context name, factory attributes, monitoring period, registered updaters, and a table of records keyed by record name/tags. `MetricsRecordImpl` stores pending tag and metric maps and updates/removes rows in the context. `GangliaContext` keeps a UDP socket, XDR output buffer, offset, and target server list. `NoEmitMetricsContext`, `NullContext`, and `NullContextWithUpdateThread` differ mainly in whether they retain data or run updater threads without emitting.

Metrics2 state is split between immutable snapshots and mutable source-side accumulators. `MetricsRecord`, `MetricsTag`, and `AbstractMetric` represent immutable snapshot data. `MutableMetric` tracks a changed flag; counters, gauges, stats, quantiles, rates, rolling averages, and registries persist values between snapshots. `MutableQuantiles` keeps an estimator, public quantile definitions, and a previous snapshot map; `MutableRollingAverages` keeps sliding windows and thread-local state and must be closed; `MutableRatesWithAggregation` keeps per-thread local rate counts and aggregates them at snapshot time, with the documented risk that samples from short-lived threads may be lost.

Metrics sink state can be external and durable. `RollingFileSystemSink` writes metrics logs under a filesystem path, often HDFS, and rolls interval directories/files. Its static test fields (`forceFlush`, `hasFlushed`, `suppliedConf`, `suppliedFilesystem`) and protected timing/path/config fields expose a significant amount of operational state. It can append to existing files only on filesystems that support append; otherwise it creates sequenced files.

Network mapping state is cached or file/script-backed. `CachedDNSToSwitchMapping` stores host-to-rack mappings over a raw mapping and exposes cache reload hooks. `TableMapping` persists mappings in an external text file and reloads them on request. `ScriptBasedMapping` persists script configuration and derives cache behavior from its `CachedDNSToSwitchMapping` superclass.

Record API state is stream-backed and object-local. `BinaryRecordInput`/`Output` wrap input/output streams or data streams, with thread-local helpers. `Buffer` owns mutable byte-array content, count, and capacity. `RecordComparator.define()` mutates global comparator registration state through a synchronized static method.

## Dependencies and Integration Points

This chunk integrates with Hadoop Common subsystems rather than standalone code:

- Compression APIs integrate with `CompressionCodec`, `Compressor`, `Decompressor`, `CompressionInputStream`, `CompressionOutputStream`, `InputStream`, `OutputStream`, and direct `ByteBuffer` consumers. Splittable compression integrates with Hadoop input splitting and parallel file processing.
- TFile integrates with Hadoop `Configuration`, filesystem input/output streams, raw comparators, TFile reader/writer classes outside this XML range, and compression codecs such as gzip, LZO, and no compression.
- Serialization adapters integrate with Hadoop `Serialization`, `Writable`, Java `Serializable`, Avro schemas, Avro specific generated classes, and Avro reflection configuration.
- Metrics v1 integrates with `ContextFactory`, `MetricsContext`, `MetricsRecord`, `Updater`, Log4J, Ganglia UDP packets, and older servlet or JMX polling paths. Many classes are deprecated in favor of metrics2.
- Metrics2 integrates with `SubsetConfiguration`, metrics source classes, sinks, JMX through `MetricsSystemMXBean` and `MBeans`, SLF4J logging in `MetricsJsonBuilder`, filesystem APIs in `RollingFileSystemSink`, and external systems such as Graphite and StatsD.
- Network mapping integrates with Hadoop configuration keys, rack-aware schedulers and block placement code, external topology scripts, table files, Java networking, and proxy configuration.
- Record I/O integrates with generated Hadoop record classes, `WritableComparable`, `WritableComparator`, `DataInput`/`DataOutput`, and legacy jobs that predate Avro.

## Risks

- This is a compatibility baseline. Incorrect edits to this XML can create false API-diff results, hide real binary/source incompatibilities, or report spurious public API changes.
- Splittable compression boundary adjustment is correctness-sensitive. A codec that reports wrong adjusted start/end offsets can drop or duplicate decompressed records in parallel reads.
- Direct decompression with `ByteBuffer` can be sensitive to buffer position/limit semantics and native codec availability. The XML captures the API but not validation behavior.
- TFile has file-format and performance risks: key size limits, value chunk size, block size, codec selection, comparator naming, and index memory estimates all affect compatibility and resource usage. Its documented lack of true multithreaded read I/O can surprise callers using multiple scanners.
- Metrics v1 classes are deprecated but still public. Removing or changing them may break old deployments, Log4J configurations, Ganglia integrations, or polling systems that rely on retained in-memory records.
- Metrics2 mutable classes are concurrency-sensitive. Some methods are synchronized while others are not; `MutableRates` explicitly warns against high contention, and `MutableRatesWithAggregation` can lose samples from short-lived threads.
- Metrics sinks have operational risks. `RollingFileSystemSink` can silently swallow or throw file errors depending on `ignore-error`, can overload HDFS if many hosts roll simultaneously without sufficient random offset, and append behavior depends on filesystem semantics and HDFS datanode availability.
- Metrics naming and filtering affect observability. Glob/regex filters, tags as record keys, and interned metric info/tag objects can change which records are emitted or grouped.
- Network topology mapping is placement-sensitive. Returning lists out of order, failing to return a mapping for every input, stale caches, bad scripts, or malformed table files can degrade rack-aware placement and fault tolerance.
- SOCKS socket configuration affects all consumers using the factory. Equality/hash semantics matter if factories are cached, and misconfigured proxies can change connection behavior broadly.
- The record API is deprecated and replaced by Avro, but compatibility remains important for old serialized data and generated classes. Thread-local input/output helpers and global comparator registration are stateful and can be hard to reason about in containerized or long-running processes.
- The chunk ends mid-interface. The final per-file report must merge with the next chunk before claiming complete coverage of `RecordInput` or later `org.apache.hadoop.record` APIs.

## Test and Validation Signals

Validation for this XML is mostly API and subsystem compatibility oriented:

- Run the JDiff/API compatibility tooling that consumes `Apache_Hadoop_Common_2.10.2.xml` and confirm the generated report recognizes all classes, methods, fields, deprecations, and package docs in this range.
- Compile representative Hadoop Common consumers using compression codecs, direct decompression, splittable compression, TFile utilities, serialization adapters, metrics2 registries/sinks, network mapping implementations, and legacy record classes.
- Compression tests should cover gzip stream creation, direct decompressor creation when available, split-boundary adjustment, and read-mode behavior for splittable codecs.
- TFile tests should write/read sorted and unsorted files with `none`, `gz`, and available `lzo` compression, named meta blocks, comparator creation, key seeks, offset seeks, variable-length integer/string round trips, and lower/upper-bound helper edge cases.
- Serialization tests should exercise Java serialization, Writable serialization, Avro specific classes, Avro reflect package configuration, marker-interface reflect serialization, and schema-key behavior.
- Metrics v1 tests should cover updater registration, start/stop/close lifecycle, buffered record update/remove semantics, `getAllRecords()`, `EventCounter` Log4J counting, and Ganglia server parsing/XDR packet emission where legacy support is enabled.
- Metrics2 tests should cover source registration/unregistration, immediate publish, MXBean start/stop/config methods, builder output, JSON/string builders, filters, mutable counters/gauges/stats/quantiles/rates/rolling averages, changed-only versus all snapshots, and concurrent rate aggregation.
- Sink tests should write to file, Graphite, StatsD, and rolling filesystem targets, including flush/close behavior, roll interval parsing, random roll offset handling, append-disabled sequenced files, append-enabled filesystems, ignored versus thrown write errors, and secure keytab/principal configuration.
- Network mapping tests should verify one-to-one output ordering, default-rack fallback, full and selective cache reloads, script configuration changes, table-file reloads, and malformed or missing mapping file behavior.
- Socket factory tests should validate standard and SOCKS socket creation overloads, configuration-based proxy selection, equality/hash behavior, and connection timeout exception propagation.
- Legacy record tests should round-trip binary and CSV primitive values, buffers, nested records, vectors, maps, `Record.write()`/`readFields()`, `Buffer` mutation/comparison/clone behavior, and `RecordComparator.define()` registration.
