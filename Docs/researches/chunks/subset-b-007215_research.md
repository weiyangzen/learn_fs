# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 24647-30892

Chunk id: `subset-b-007215`
Source: `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml`
Line range: 24647-30892

## Research Scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.3.4, not Java implementation source. It records public and protected API shape, inheritance, declared exceptions, fields, synchronization markers, deprecation markers, and embedded Javadocs. The range starts in the middle of `org.apache.hadoop.io.WritableComparator`, covers Hadoop Writable utility APIs, compression APIs, TFile and serializer APIs, a large part of the metrics2 API and sink library, and ends at the beginning of `org.apache.hadoop.net.AbstractDNSToSwitchMapping`.

## Purpose

The chunk documents several reusable Hadoop Common surfaces:

- Writable comparison, instantiation, compact binary encoding, and safe string/enum serialization helpers.
- Stream-based compression/decompression contracts, codec discovery, codec pooling, splittable compression, direct `ByteBuffer` decompression, and concrete BZip2/GZip/default/pass-through codec wrappers.
- Erasure-code schema metadata and TFile-facing raw comparison, compression naming, and variable-length utility functions.
- Java, Writable, and Avro serialization adapters used by Hadoop's configurable serialization framework.
- Log event counting and the metrics2 framework: immutable metrics, collectors, record builders, filters, system lifecycle hooks, mutable counters/gauges/stats/rates/quantiles, output sinks, MBean registration, sparse-update caching, and server-address parsing.
- The opening of the network topology DNS-to-switch mapping base class, where configuration and single-switch topology diagnostics begin.

Because the source is an API descriptor, behavior below is inferred from signatures and Javadocs rather than method bodies.

## Important APIs, Types, and Functions

`org.apache.hadoop.io.WritableComparator` implements `RawComparator` and `Configurable`. This chunk includes its protected configuration-aware constructor and the public comparator registry and comparison helpers: `get(Class)`, `get(Class, Configuration)`, `define(Class, WritableComparator)`, `getKeyClass`, `newKey`, object and raw-byte `compare` overloads, `compareBytes`, `hashBytes`, primitive byte-array readers, and byte-array VInt/VLong readers. The key integration point is optimized raw comparison for `WritableComparable` implementations, especially sort-heavy paths such as `SequenceFile.Sorter`.

`WritableFactories` and `WritableFactory` provide factory registration for non-public or special-case `Writable` implementations. `setFactory`, `getFactory`, and `newInstance` let `ObjectWritable` and related serializers instantiate classes that reflection alone may not construct cleanly.

`WritableUtils` collects low-level Hadoop binary helpers: compressed byte arrays and strings, string arrays, plain UTF strings, byte-array display, cloning via serialization, deprecated `cloneInto`, zero-compressed `writeVInt`/`writeVLong` and `readVInt`/`readVLong`, range-checked VInt reads, VInt sign/size helpers, enum read/write, exact skipping, multi-writable byte-array packing, and bounded `readStringSafely`. Its public contract is the stable wire format used across Hadoop RPC, filesystem metadata, and older file formats.

The `org.apache.hadoop.io.compress` package in this chunk defines the core compression abstraction. `CompressionCodec` is the central streaming codec interface, with methods to create input/output streams with or without pooled compressors/decompressors, report compressor/decompressor implementation classes, allocate new codec engines, and return a default filename extension. `SplittableCompressionCodec` adds split-aware input construction for block readers that need adjusted start/end positions.

`Compressor` and `Decompressor` are stateful stream-engine contracts. They expose `setInput`, dictionary setup, progress counters or remaining-byte counters, `needsInput`, `needsDictionary`, `finish`, `finished`, `compress`/`decompress`, `reset`, `end`, and, for compressors, `reinit(Configuration)`. `DirectDecompressionCodec` and `DirectDecompressor` add direct `ByteBuffer` decompression support.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases. The input side extends `InputStream`, implements `Seekable` and `IOStatisticsSource`, carries protected `in` and `maxAvailableData`, and declares read, reset, position, unsupported seek, and statistics behavior. The output side extends `OutputStream`, implements `IOStatisticsSource`, wraps protected `out`, and defines compressed write, `finish`, `resetState`, flush/close, and statistics behavior.

`CompressorStream`, `DecompressorStream`, `BlockCompressorStream`, and `BlockDecompressorStream` are reusable stream implementations around compressor/decompressor engines. They maintain protected engine references, buffers, EOF/closed state, implement read/write loops, finish/close/reset behavior, and block-oriented compressed-data framing.

Concrete and utility compression classes include:

- `BZip2Codec`, a `Configurable` `SplittableCompressionCodec` with split-aware BZip2 streams and `.bz2` extension handling.
- `DefaultCodec`, a `Configurable` codec with direct decompression support.
- `GzipCodec`, a `DefaultCodec` subclass for gzip compressor/decompressor creation and extension handling.
- `PassthroughCodec`, a non-transforming codec with configurable extension constants for workflows that want codec plumbing without compression.
- `SplitCompressionInputStream`, which records adjusted split start/end after codec stream creation.
- `CodecConstants`, which centralizes default extensions for default, BZip2, GZip, LZ4, pass-through, Snappy, and ZStandard codecs.
- `CodecPool`, a global compressor/decompressor pool with leased-object counts and return methods.
- `CompressionCodecFactory`, which discovers codecs from `io.compression.codecs` and Java `ServiceLoader`, maps file extensions and codec names/classes to codec instances, removes suffixes, and has a small test `main`.

`ECSchema` is a serializable erasure coding schema object. Constructors accept option maps or the core tuple of codec name, data units, and parity units. Accessors expose codec name, extra options, data-unit count, parity-unit count, and standard equality/hash/string behavior. Public keys include `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.

The TFile section defines `MetaBlockAlreadyExists`, `MetaBlockDoesNotExist`, `RawComparable`, `TFile`, and `Utils`. `RawComparable` exposes backing byte array, offset, and size for raw comparator use. `TFile` declares compression constants (`gz`, `lzo`, `none`), comparator constants (`memcmp`, Java-class prefix), `makeComparator`, supported compression algorithm listing, and an inspection `main`. `Utils` provides TFile-specific VInt/VLong and string read/write helpers plus lower/upper-bound binary search overloads over comparable lists and custom comparators.

Serialization adapters include `JavaSerialization`, `JavaSerializationComparator`, `WritableSerialization`, `AvroReflectSerializable`, `AvroReflectSerialization`, `AvroSerialization`, and `AvroSpecificSerialization`. The Java and Avro classes implement or extend Hadoop's `Serialization`/`DeserializerComparator` framework. `AvroSerialization` exposes `AVRO_SCHEMA_KEY`; reflect serialization exposes `AVRO_REFLECT_PACKAGES`; `WritableSerialization` delegates to the `Writable` contract.

`EventCounter` is a Log4J `AppenderSkeleton` that counts logging events by severity and implements `append`, `close`, and `requiresLayout`.

The `org.apache.hadoop.metrics2` package supplies the core metrics model. `AbstractMetric` is an immutable metric implementing `MetricsInfo`, with `value`, `type`, visitor dispatch, equality, hash, and string conversion. `MetricsInfo`, `MetricsTag`, `MetricsRecord`, and `MetricsCollector` define immutable metadata, tag, record snapshot, and collector contracts. `MetricsRecordBuilder`, `MetricsJsonBuilder`, and `MetricStringBuilder` build records in fluent form with tags, context, counters, gauges, parent collectors, and string/JSON dump support.

Metrics lifecycle and plugin APIs include `MetricsPlugin.init(SubsetConfiguration)`, `MetricsSink.putMetrics/flush`, `MetricsSource.getMetrics`, `MetricsFilter.accepts` overloads for names/tags/tag collections/records, `MetricsSystem.register`, `unregisterSource`, callback registration, immediate publication, and shutdown, plus `MetricsSystemMXBean` start/stop/MBean lifecycle/current-config operations.

Metrics library classes in `org.apache.hadoop.metrics2.lib` provide the mutable source-side implementation layer. `DefaultMetricsSystem` is the daemon-wide singleton enum with initialize, instance, shutdown, mini-cluster mode setters, and mini-cluster mode query. `Interns` creates interned `MetricsInfo` and `MetricsTag` objects. `MetricsRegistry` creates, stores, tags, and snapshots mutable counters, gauges, quantiles, stats, rates, aggregated rates, and rolling averages.

Mutable metric classes include `MutableMetric` with changed-state tracking and conditional snapshots; `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong`; `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong`; `MutableQuantiles` with rolling interval, estimator access, previous snapshot, and `stop`; `MutableRate`; `MutableRates`; `MutableRatesWithAggregation`; `MutableRollingAverages`, which is `Closeable` and supports thread-local state collection and test-only record-validity tuning; and `MutableStat`, a synchronized sample-stat metric with extended stats, timestamp updates, bulk sample adds, single-value adds, snapshots, last-stat access, min/max reset, and snapshot timestamp.

Metrics sinks include `FileSink`, `GraphiteSink`, `RollingFileSystemSink`, and `StatsDSink`. The simple sinks implement `MetricsSink` and `Closeable` with `init`, `putMetrics`, `flush`, and `close`. `RollingFileSystemSink` writes metrics logs through `FileSystem`, rolls directories by interval, can add randomized roll offsets, writes host log files under a base path, supports append where the target filesystem does, and has protected fields for source, error handling, append behavior, base path, roll timings, next flush, static test hooks, supplied configuration, and supplied filesystem. `StatsDSink` formats records for a StatsD daemon and exposes `writeMetric`.

Metrics utilities include `MBeans.register` overloads with Hadoop's `hadoop:service=...,name=...` naming convention, `getMbeanNameService`, `getMbeanNameName`, and `unregister`; `MetricsCache`, which caches records for sinks that cannot consume sparse updates; and `Servers.parse`, which turns comma/space-separated `host` or `host:port` specifications into socket-address lists with localhost fallback.

The chunk ends at the start of `AbstractDNSToSwitchMapping`, an abstract `DNSToSwitchMapping` and `Configurable` base. The visible portion includes protected constructors, one configuration-aware constructor that explicitly does not call `setConf`, and the beginning of `getConf`.

## Control Flow and Behavior

Writable comparison flow is registry-driven. Callers ask `WritableComparator.get` for a comparator for a `WritableComparable` class; registered comparators can override raw-byte comparison. If raw comparison is not specialized, the documented default is to deserialize the byte slices into key objects using `Writable.readFields` and then call the object comparator, which normally delegates to natural `Comparable.compareTo`.

Writable instantiation flow is factory-first. Code that needs a `Writable` instance can consult `WritableFactories`; registered factories allow non-public or otherwise special classes to participate in `ObjectWritable` and generic deserialization paths.

Variable-length integer control flow is byte-header based. `WritableUtils` and TFile `Utils` write a one-byte representation for values in the small range and use leading marker bytes to indicate sign and following byte count for larger integers. Read paths interpret the first byte with sign and size helpers, then consume the required number of high-non-zero-byte-first payload bytes. Range-checked reads add a validation layer after decoding.

Compression control flow is stream and pool oriented. A codec creates streams either with newly created engines or with engines supplied by `CodecPool`. Writers feed uncompressed bytes to `CompressorStream` or block compressor streams, call `finish` to drain compressed output, and return compressors to the pool after close/reset. Readers feed compressed bytes to `DecompressorStream` or block decompressor streams, refill when `needsInput` is true, surface EOF and availability, and reset state when reused for another logical stream.

Codec discovery flow in `CompressionCodecFactory` starts from configuration and service discovery, then builds mappings by extension, canonical class name, and short name. File readers can ask for a codec by `Path`; tools can use `removeSuffix` to derive uncompressed names.

Splittable compression flow gives the codec both the seeked input stream and the requested split boundaries. The resulting `SplitCompressionInputStream` can report adjusted boundaries because some codecs need to move to compression-block-safe positions.

Metrics collection flow starts at a `MetricsSource.getMetrics` callback, where sources populate a `MetricsCollector` using `MetricsRecordBuilder`. Mutable metrics in a `MetricsRegistry` snapshot their current values into builders, optionally only when changed. Metrics filters accept or reject records by name, tags, or record contents. The `MetricsSystem` coordinates source registration, immediate publication, sink delivery, JMX lifecycle, and shutdown.

Metrics sink flow is push-based. The metrics system calls `putMetrics(record)` for each record and then `flush` as needed. File-like sinks serialize records to a stream or external service. `RollingFileSystemSink` adds roll scheduling: initial flush time is offset randomly within a configured bound, later flushes preserve that offset by adding integer roll intervals, and output moves to a new interval directory when the roll boundary passes.

MBean flow is conventional JMX registration. Hadoop code registers an object with service/name properties, optionally adding more key-value properties, and unregisters by the returned `ObjectName`.

The visible network-topology flow is only partial. `AbstractDNSToSwitchMapping` constructors store or defer configuration setup; later methods in the next chunk complete mapping, diagnostics, and single-switch policy behavior.

## State and Persistence Behavior

Most classes in this chunk are API-level wrappers over external or transient state rather than durable stores.

Writable wire state is persistent by contract. `WritableUtils`, `WritableComparator`, factory registration, serializer adapters, and TFile utilities encode data that may cross RPC boundaries or be stored in Hadoop sequence/file formats. Any incompatible change to VInt/VLong, strings, enum names, or Writable instantiation changes persisted data compatibility.

Compression state is per engine and per stream. `Compressor`/`Decompressor` instances hold input/output buffers, dictionaries, byte counters, finish flags, and native or Java codec state until `reset` or `end`. `CodecPool` adds process-global leased-object state and exposes leased counts, so missing returns can create resource leaks and skew diagnostics. `CompressionInputStream` and `CompressionOutputStream` hold the wrapped streams and expose IO statistics from underlying streams when available.

`ECSchema` is serializable metadata. Its durable identity is the codec name, data/parity unit counts, and extra options map. Equality and hash behavior make those fields relevant for configuration comparisons and policy lookups.

TFile metadata and raw comparator behavior depend on string constants for compression and comparator names. `RawComparable` instances expose borrowed byte-array ranges, so state is external to the object and can be invalidated or mutated if backing buffers are reused.

Metrics state is in mutable metrics and registries. Counters monotonically increase; gauges move up/down or can be set; stats aggregate samples, min/max, mean, and optional extended statistics; quantiles maintain rolling online estimators and previous snapshots; rolling averages keep per-name aggregate state and thread-local contributions. `MutableMetric.changed` gates sparse snapshots and must be set/cleared correctly around mutations and snapshots.

Metrics sink state varies by destination. `RollingFileSystemSink` holds configuration-derived fields and writes durable log files to a `FileSystem` path. It may create interval directories, create sequence-suffixed files when append is unavailable or disabled, append to existing files when allowed, and preserve roll timing in `nextFlush`. Static fields such as `forceFlush`, `hasFlushed`, `suppliedConf`, and `suppliedFilesystem` are visible test hooks and can affect process-wide behavior.

`MBeans` state is held in the platform MBean server under generated `ObjectName`s. `MetricsCache` keeps recent record/tag/metric values so sinks that do not support sparse updates can emit complete records even when updates contain only changed fields.

The beginning of `AbstractDNSToSwitchMapping` shows cached `Configuration` state, but the full mapping cache and diagnostics surface continue beyond this chunk.

## Dependencies and Integration Points

The IO APIs integrate with Hadoop core types such as `Configuration`, `Configurable`, `Writable`, `WritableComparable`, `RawComparator`, `DataInput`, `DataOutput`, `ObjectWritable`, `ReflectionUtils`, `Text`, `Path`, and TFile internals. Serializer adapters integrate with the Hadoop serialization SPI and with Java serialization, Writable serialization, and Avro reflect/specific classes.

Compression APIs depend on Java streams, `ByteBuffer`, Hadoop `Seekable`, Hadoop filesystem IO statistics, codec implementations such as BZip2/GZip/LZ4/Snappy/ZStandard outside this exact chunk, Java `ServiceLoader`, and configuration key `io.compression.codecs`. Native-code-backed codecs must honor `end`/`reset` contracts to avoid native resource leaks.

Erasure coding schema metadata integrates with HDFS and other erasure-code policy code that consumes codec names and unit counts.

Metrics APIs depend on `org.apache.commons.configuration2.SubsetConfiguration`, SLF4J logging, Log4J for `EventCounter`, Hadoop metrics annotations, `com.google.re2j.Pattern` for glob and regex filters, JMX `ObjectName`, `FileSystem`/`Path` for rolling file logs, network sockets for Graphite and StatsD, and quantile/stat utility classes in `org.apache.hadoop.metrics2.util`.

`RollingFileSystemSink` integrates directly with configured filesystems including HDFS, local filesystems, S3-like filesystems, and security configuration for Kerberos keytab/principal lookup. Its Javadocs explicitly call out HDFS append and file-size visibility behavior.

`AbstractDNSToSwitchMapping` integrates with `DNSToSwitchMapping`, `Configuration`, and later topology-aware block placement and rack-policy code.

## Risks and Edge Cases

- This file is generated JDiff XML. It is useful for API compatibility research but not enough to prove implementation details such as exact locking, error handling, or allocation behavior.
- `WritableComparator.define` requires registered comparators to be thread-safe. An optimized raw comparator that reuses mutable state unsafely can corrupt sort results under concurrent use.
- The default raw comparator path deserializes both keys before comparison; it is correct but expensive and can surface `readFields` compatibility bugs during sort.
- `WritableFactories` are process-global registration points. Wrong factories can instantiate incompatible classes for persisted data.
- `WritableUtils.cloneInto` is deprecated in favor of `ReflectionUtils.cloneInto`; users retaining the old API carry migration risk.
- VInt/VLong formats are compatibility-critical. Boundary values around `-112`, `127`, negative markers, and long/int range narrowing are high-risk.
- `readStringSafely` exists because unbounded string lengths are unsafe; callers that use plain string reads on untrusted input may allocate excessively or accept malformed data.
- Compression streams are stateful and close-sensitive. Failing to call `finish`, `reset`, `end`, or `CodecPool.return*` can lose trailing compressed bytes, poison reused engines, or leak native buffers.
- Dictionary support is optional and codec-specific. Callers must handle `needsDictionary` rather than assuming all streams are self-contained.
- `CompressionInputStream.seek` and `seekToNewSource` are documented as unsupported at the base level. Split readers must use codec-specific split APIs rather than assuming arbitrary seeking works.
- `SplittableCompressionCodec` can adjust requested split start/end positions, so callers must use `getAdjustedStart` and `getAdjustedEnd` for record-boundary correctness.
- `PassthroughCodec` intentionally does not transform bytes. Misconfiguration can make files look codec-managed by extension while providing no compression.
- `CompressionCodecFactory` behavior depends on classpath service discovery and configured codec classes; ambiguous extensions or missing service entries can change which codec is selected.
- TFile `RawComparable` exposes raw buffers by reference. Buffer reuse or mutation can break comparator results.
- Avro serialization depends on schema configuration and class category; reflect vs specific acceptance must match configured packages and Avro schemas.
- Metrics mutable classes mix synchronized and unsynchronized methods. `MutableStat.add` and snapshot methods are synchronized, but callers still need to respect per-metric thread-safety assumptions and registry-level concurrency.
- Bulk `MutableStat.add(numSamples, sum)` preserves mean but Javadoc warns variance can be inaccurate for large sample counts due to a single Welford step.
- Sparse metrics snapshots rely on `changed` flags. Missing `setChanged` calls produce silent under-reporting for sinks that only receive changed metrics.
- `MutableQuantiles` and `MutableRollingAverages` own background or thread-local/rolling state and expose `stop`/`close`; failure to close can leak scheduled work or stale state.
- `RollingFileSystemSink` has subtle operational behavior: `ignore-error` wording in the Javadoc says the default is true but also describes throwing behavior in a confusing way; append support varies by filesystem; sequence-suffixed files have newest-as-highest semantics; HDFS append can appear successful with too few datanodes but later fail on read; HDFS file sizes may not update until close.
- `RollingFileSystemSink` static test hooks can affect all instances in a JVM. Tests must isolate or reset them.
- StatsD and Graphite sinks depend on external daemons and network availability; metric naming must avoid collisions after hostname skipping, service naming, context, record, and metric name concatenation.
- MBean registration can collide if service/name/properties are reused without unregistering.
- `Servers.parse` has default-localhost behavior for null specs; unintended null configuration can silently target localhost.
- This chunk ends mid-`AbstractDNSToSwitchMapping`; final file synthesis must merge with the next chunk before drawing conclusions about topology cache behavior.

## Test Signals

Useful tests for code using or modifying APIs in this chunk should include:

- Writable comparator tests for registry lookup, custom raw comparator ordering, object comparator fallback, byte-array primitive readers, VInt/VLong byte-array reads, hash/lexicographic byte comparison, and thread-safety under concurrent sorts.
- Writable factory tests for non-public `Writable` classes, configuration-aware instantiation, missing factory fallback, and wrong-factory failure modes.
- `WritableUtils` compatibility tests for compressed byte/string arrays, plain string arrays, enum read/write by name, `skipFully` short streams, `toByteArray`, `readStringSafely` maximum length rejection, and VInt/VLong boundary values.
- Compression lifecycle tests for each codec class: create stream with new and pooled engines, write/read round trip, `finish` before close, reset and reuse, `end` release, dictionary-needed paths, byte counters, and leased count returning to zero in `CodecPool`.
- Split compression tests for BZip2 and any other splittable codec, validating adjusted start/end and record-boundary behavior across split edges.
- `CompressionCodecFactory` tests for configured codec classes, service-loaded codecs, extension lookup, name/class lookup, ambiguous names, suffix removal, and missing codec behavior.
- Direct decompression tests for `DefaultCodec`/`GzipCodec` direct decompressor creation and `ByteBuffer` input/output position updates.
- `PassthroughCodec` tests proving identity byte behavior and configurable/default extension handling.
- `ECSchema` tests for constructor option parsing, equality/hash, extra-option retention, invalid/missing option handling, and string output.
- TFile utility tests for raw comparator creation, supported compression algorithm names, VInt/VLong and string encoding compatibility, and lower/upper-bound behavior with duplicate keys and custom comparators.
- Serialization tests for Java, Writable, Avro reflect, and Avro specific classes, including schema-key configuration, package filtering for reflect serialization, and comparator behavior.
- Metrics record-builder tests for tag/context/counter/gauge additions, JSON/string output, visitor callbacks for all numeric types, and immutable metric/tag equality.
- Metrics registry tests for duplicate metric/tag names, counter monotonicity, gauge increment/decrement/set, changed-flag sparse snapshots, all-vs-changed snapshots, and registry context tagging.
- `MutableStat`, `MutableRate`, `MutableQuantiles`, `MutableRatesWithAggregation`, and `MutableRollingAverages` tests for concurrent adds, snapshots, min/max reset, extended stats, rolling interval rollover, close/stop cleanup, test-only validity tuning, and bulk-sample variance caveats.
- Metrics system tests for source registration/unregistration, duplicate source names, callback registration, immediate publish, shutdown idempotence, MXBean start/stop/config methods, and mini-cluster mode behavior.
- Metrics filter tests for glob/regex compilation with RE2J and acceptance/rejection by metric name, tags, tag collections, and records.
- Sink tests for `FileSink`, `GraphiteSink`, and `StatsDSink` initialization, record formatting, flush/close exception handling, hostname skipping, service-name configuration, and external-service failure behavior.
- `RollingFileSystemSink` tests for roll interval parsing and minimums, initial random offset bounds, preserved offset across rolls, base path defaulting, sequence-suffix creation when append is disabled, append-enabled behavior on append-capable filesystems, error handling under `ignore-error`, Kerberos keytab/principal configuration, HDFS-like delayed size visibility assumptions, and reset of static test hooks.
- `MBeans` tests for object-name construction, extra properties, duplicate registration, extraction of service/name fields, and unregister idempotence.
- `MetricsCache` tests for sparse update completion, tag-including and tag-excluding updates, maximum records per name eviction, and lookup by name/tag collection.
- `Servers.parse` tests for null specs, comma and whitespace separation, default port injection, explicit ports, IPv6 or malformed host strings if supported by implementation, and localhost fallback.

## Cross-Chunk Notes

This chunk starts after the declaration and earlier constructors of `WritableComparator`, so the previous chunk contains that class opening. It ends inside `AbstractDNSToSwitchMapping`; the next chunk must be consulted for the rest of topology mapping behavior, including any switch-map cache fields, resolution APIs, reload behavior, and diagnostics.
