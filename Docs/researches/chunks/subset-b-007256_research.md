# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.22.0.xml lines 18219-24654

## Scope

This chunk is a generated JDiff API snapshot for Hadoop Core 0.22.0, not implementation code. It starts inside the public API entry for `org.apache.hadoop.io.compress.GzipCodec`, then covers compression stream/splitting APIs, the `org.apache.hadoop.io.file.tfile` package, native I/O wrappers, serialization providers including Avro integration, logging helpers, the metrics framework and providers, network topology/socket factories, and most of the deprecated Hadoop Record I/O runtime. It ends inside the long package-level Record I/O design document while describing binary serialization of integral values, so adjacent chunks are needed for the remainder of that package doc.

The XML records public/protected API compatibility metadata: packages, classes/interfaces, inheritance, implemented interfaces, constructors, methods, parameters, exceptions, fields, visibility, static/final/abstract/native/synchronized flags, deprecation state, and embedded Javadoc contracts. Research conclusions below are based on those signatures and docs, not on method bodies.

## Purpose and major API surface

The compression portion exposes `GzipCodec` factory methods for input streams, decompressors, decompressor type lookup, and default extension lookup. `GzipCodec.GzipOutputStream` bridges a `DeflaterOutputStream` into Hadoop's `CompressionOutputStream` shape with `write`, `flush`, `finish`, `resetState`, and `close`. `SplitCompressionInputStream` and `SplittableCompressionCodec` define the contract for codecs that can decompress a compressed stream from adjusted split boundaries, returning adjusted start/end offsets and supporting `READ_MODE` values for continuous versus block-aware reads.

`org.apache.hadoop.io.file.tfile` describes TFile, a container of typeless byte key/value pairs with block compression, named meta blocks, optional sorted keys, key/file-offset seeks, and memory usage tied to compression buffers plus data/meta indexes. Constants name supported compression algorithms (`none`, `lzo`, `gz`) and comparators (`memcmp`, Java-class comparator prefix). `TFile.makeComparator`, `getSupportedCompressionAlgorithms`, and `main` expose comparator creation, algorithm discovery, and file information dumping.

`TFile.Reader` is the read entry point. It reports comparator name, sortedness, entry count, first/last keys, entry/key comparators, and meta blocks, and creates scanners over the whole file, byte ranges, key ranges, or record-number ranges. It can map compressed-block offsets to nearby record numbers and sample keys. `TFile.Reader.Scanner` is cursor-based and supports seek, rewind, seek-to-end, lower/upper bounds by raw byte slices or `RawComparable`, forward advance, current entry access, record-number lookup, and close. `TFile.Reader.Scanner.Entry` exposes key/value copying into `BytesWritable` or user buffers, direct key/value streaming, length checks, output-stream writes, comparison by raw bytes or `RawComparable`, equality, and hash code.

`TFile.Writer` creates TFiles over `FSDataOutputStream` with minimum block size, compression, comparator, and `Configuration`. It supports direct append from byte arrays, staged key/value append streams, and named meta-block creation with default or explicit compression. Its docs state the writer must be closed to finish and release resources, and meta block names must be unique.

`org.apache.hadoop.io.file.tfile.Utils` supplies shared variable-length integer encoding/decoding, string encoding as `VInt` length plus Text bytes, and lower/upper-bound binary searches over `List` or array slices. `Utils.Version` serializes a major/minor version as two shorts, compares versions, tests compatibility, exposes fixed serialized size, and is recommended for applications layered on TFile. `MetaBlockAlreadyExists`, `MetaBlockDoesNotExist`, and `RawComparable` round out meta-block errors and raw byte range comparison.

`org.apache.hadoop.io.nativeio` exposes POSIX-facing JNI wrappers. `Errno` enumerates POSIX error values. `NativeIO` reports native availability and wraps `open(2)`, `fstat(2)`, and `chmod(2)`, with public `O_*` flag constants. `NativeIO.Stat` returns owner, group, and mode plus `S_IF*`, `S_IS*`, and user permission constants. `NativeIOException` carries an `Errno` and formats native failures.

`org.apache.hadoop.io.serializer` covers serialization provider implementations. `JavaSerialization` accepts Java `Serializable` classes and returns Java serializer/deserializer instances. `JavaSerializationComparator` compares objects through Java deserialization. `WritableSerialization` is a `Configured` provider for Hadoop `Writable`s. The package doc positions this as a framework for pluggable serialization mechanisms used by subsystems such as MapReduce.

`org.apache.hadoop.io.serializer.avro` integrates Avro. `AvroReflectSerializable` is a tag interface for reflect serialization. `AvroSerialization` is the configured base with schema, datum writer, and datum reader hooks and `AVRO_SCHEMA_KEY`. `AvroReflectSerialization` accepts tagged classes or classes in configured packages (`AVRO_REFLECT_PACKAGES`) and returns reflect schemas/readers/writers. `AvroSpecificSerialization` handles Avro `SpecificRecord` classes.

`org.apache.hadoop.log` includes the deprecated `EventCounter` Log4J appender shim and `LogLevel`, a command-line/runtime log-level changer with `main` and `USAGES`. `EventCounter` extends the metrics JVM event counter, indicating older logging metrics APIs are being bridged.

`org.apache.hadoop.metrics` and provider packages define the original Hadoop metrics API. `FileContext` writes metrics records to a configured file, with init, start/stop monitoring, emit, flush, file name, period, and property constants. `GangliaContext` sends metrics to Ganglia over UDP, maintains an XDR buffer, server list, socket, and helpers for XDR strings/ints, units, slope, `tmax`, and `dmax`; `GangliaContext31` adapts emission for Ganglia 3.1.x.

`org.apache.hadoop.metrics.spi` is the service-provider implementation layer. `AbstractMetricsContext` manages context attributes, records, updaters, monitoring lifecycle, periodic update/remove flows, period parsing, emit, flush, and close. `CompositeContext` fans metrics operations to subcontexts. `MetricsRecordImpl` stores tags and absolute/incremental metrics, provides typed tag/metric setters and incrementers, and updates/removes buffered rows in its context. `MetricValue` wraps a number plus absolute/increment flag. `NoEmitMetricsContext`, `NullContext`, and `NullContextWithUpdateThread` provide disabled or no-output contexts. `OutputRecord` exposes copies and lookup views of emitted tags/metrics. `Util.parse` parses server specifications.

`org.apache.hadoop.net` supplies DNS-to-rack mapping and socket factories. `DNSToSwitchMapping` resolves host/IP lists to rack paths. `CachedDNSToSwitchMapping` wraps a raw mapping with caching. `ScriptBasedMapping` is configurable and implements rack resolution through an external script. `SocksSocketFactory` and `StandardSocketFactory` implement socket creation overloads, equality/hash behavior, and configuration support; despite the `StandardSocketFactory` doc wording, it represents standard socket creation while `SocksSocketFactory` uses a supplied or configured SOCKS proxy.

`org.apache.hadoop.record` is Hadoop Record I/O, already marked deprecated in several concrete input/output classes in favor of Avro. `RecordInput` and `RecordOutput` define primitive, string, buffer, record, vector, and map read/write hooks with tags. Binary, CSV, and XML concrete input/output classes implement those hooks. `BinaryRecordInput` and `BinaryRecordOutput` expose thread-local `get(DataInput/DataOutput)` helpers. `CsvRecordInput/Output` and `XmlRecordInput/Output` provide text and XML encodings. `Index` is the iterator-like API for deserializing maps/vectors. `Buffer` is the native Java representation of the Record I/O `buffer` type, with backing-array ownership/copying, count/capacity control, append, truncate, reset, comparison, equality, clone, and string conversion. `Record` is the abstract generated-record base and also implements `Writable`-style `write`/`readFields`, tagless serialization helpers, `compareTo`, and `toString`. `RecordComparator` extends `WritableComparator` and registers optimized comparators. `org.apache.hadoop.record.Utils` provides float/double parsing, zero-compressed variable-length integer operations, encoded-size computation, binary writes, byte lexicographic comparison, and hex support.

The trailing package-level Record I/O document explains the historical DDL system: primitive types (`byte`, `boolean`, `int`, `long`, `float`, `double`, `ustring`, `buffer`), composite `record`, `vector`, and `map`, module/include/class syntax, generated Java/C++ code, generated comparison and accessors, binary/CSV/XML encodings, and language type mappings. It explicitly lists non-goals such as serializing arbitrary C++ classes, complex linked/tree structures, built-in indexing/compression/checksums, and dynamic XML-schema object construction.

## Control flow and behavioral contracts

The XML has no executable flow, but the Javadocs define caller-visible flows. Splittable compression flow starts with a seekable compressed stream and requested `[start,end)` offsets; the codec may adjust them to block boundaries, then `getAdjustedStart()` and `getAdjustedEnd()` expose the effective range. `READ_MODE.BYBLOCK` lets codecs surface block boundaries, while continuous mode hides them from callers.

TFile write flow is stateful. A writer is constructed with stream, block/compression/comparator settings, and configuration. Callers either append complete key/value byte slices or call `prepareAppendKey()` followed by `prepareAppendValue()` to stream one entry. Meta blocks are opened through `prepareMetaBlock()`. Once `close()` is called, indexes and footer metadata are finalized; using staged streams out of order or reusing a meta-block name is an API error.

TFile read flow is scanner-driven. A reader is opened over an `FSDataInputStream` and file length, then scanners delimit a byte/key/record range and maintain an implicit cursor. `seekTo`, `lowerBound`, and `upperBound` position the cursor; `advance()` moves forward and returns whether another entry exists; `entry()` exposes a point-in-time key/value accessor. Entry APIs offer zero-copy-oriented stream writes and streams as alternatives to copying values into caller buffers.

TFile sorted-key behavior is comparator-dependent. Key range scanners, entry comparisons, and lower/upper-bound searches require a comparator compatible with the file's comparator name. `RawComparable` lets APIs pass byte-array windows without allocating key wrapper objects.

Native I/O flow is availability-gated. Callers should check `NativeIO.isAvailable()` before depending on JNI-backed calls. Native failures surface as `NativeIOException` with an `Errno`, and successful `fstat` returns a `Stat` snapshot rather than live file metadata.

Serialization framework flow is provider-selection based. Each `Serialization` implementation declares `accept(Class)` and supplies serializer/deserializer pairs. Writable serialization delegates to `Writable.readFields/write`; Java serialization delegates to JVM object serialization; Avro providers create schemas and datum readers/writers using reflect or specific strategies.

Metrics flow runs through contexts and records. Contexts initialize from a factory, create records, register periodic updaters, start monitoring, collect record updates/removals into buffered tables, emit records to providers, flush, and stop/close. Composite contexts duplicate these operations across subcontexts; null/no-emit contexts preserve update callbacks while suppressing output.

Network topology flow resolves a batch of hostnames/IP addresses to rack names. Script-based mapping is configurable and wrapped by a cache layer, so repeated host resolutions can avoid invoking the external script. Socket factory flow follows standard `SocketFactory` overloads, with SOCKS proxy behavior controlled by constructor/configuration.

Record I/O flow is translator-driven. Users write DDL files with includes, one module, and class declarations; `rcc` generates target-language classes. Generated records serialize fields sequentially through a selected `RecordOutput` and deserialize sequentially through `RecordInput`. Vector/map reading uses an `Index` whose `done()`/`incr()` methods drive collection traversal. Binary encoding serializes composite members in order and prefixes vector/map sizes; integral values use zero-compressed variable-length encoding.

## State, persistence, and side effects

The JDiff XML itself is persistent compatibility metadata. Runtime persistence described by the APIs includes compressed stream state, TFile on-disk key/value data blocks, meta blocks, indexes, version records, native file descriptors and filesystem mode bits, serialized object streams, Avro schemas, log level changes, metrics output files, Ganglia UDP datagrams, DNS-to-switch caches, socket connections, and Record I/O encoded streams.

TFile is the most storage-heavy API in this chunk. Writer state includes the output stream position, open key/value append state, minimum block size, compression algorithm, comparator identity, data-block index, meta-block index, and file footer/version metadata. Reader state includes file length, comparator, indexes, scanner ranges, current cursor, and decompression state for current blocks. Docs call out memory costs proportional to data-block and meta-block counts.

Metrics APIs maintain process state: context attributes, monitoring timer period, registered updater callbacks, per-context records, tag maps, metric maps, incremental versus absolute values, and provider resources such as file writers or UDP sockets. `stopMonitoring()` does not necessarily discard buffered data, while `close()` stops monitoring and frees buffered data/resources.

Record I/O `Buffer` exposes mutable backing-array state and capacity/count invariants. `set()` can adopt caller-supplied byte arrays while `copy()` duplicates them, so aliasing and mutation behavior differ. Generated `Record` instances persist field state and serialize through binary, CSV, or XML encodings.

Native I/O has host-dependent side effects. `open` creates file descriptors with POSIX flags; `chmod` changes mode bits; `fstat` observes owner/group/mode. These operations depend on native library loading and platform behavior.

Logging and network operations mutate external systems: `LogLevel` changes runtime logger levels; `GangliaContext` sends metrics datagrams; `FileContext` appends/flushed records to disk; socket factories create network sockets; script-based rack mapping can execute external scripts.

## Dependencies and integration points

Compression APIs integrate with `CompressionInputStream`, `CompressionOutputStream`, `CompressorStream`, `Decompressor`, Java `InputStream`/`OutputStream`, `IOException`, and codec implementations such as bzip2 that can report block boundaries.

TFile integrates with Hadoop filesystem and I/O classes including `FSDataInputStream`, `FSDataOutputStream`, `BytesWritable`, `RawComparator`, `WritableComparator`, `Text`-style string encoding, `Configuration`, `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, and Java `Comparator`/collections. Compression settings depend on Hadoop compression codec availability, including LZO and Gzip.

Native I/O depends on JNI/native libraries, Java `FileDescriptor`, POSIX open/chmod/fstat semantics, POSIX errno values, and platform-specific stat mode constants.

Serialization providers integrate with the Hadoop serialization framework, `Writable`, Java `Serializable`, `Configured`/`Configuration`, Avro `Schema`, `DatumReader`, `DatumWriter`, reflect data, and specific records.

Metrics integration points include `ContextFactory`, `MetricsContext`, `MetricsRecord`, updater callbacks, output providers, Log4J event counting, metrics JVM counters, Ganglia wire formats, files, UDP sockets, and server specification parsing.

Network APIs integrate with `Configuration`, external topology scripts, Java `SocketFactory`, `Socket`, `Proxy`, `InetAddress`, local/remote socket addresses, and Hadoop rack-awareness consumers.

Record I/O integrates with generated code from `rcc`, Hadoop `Writable` and `WritableComparable` style APIs, `DataInput`/`DataOutput`, Java `TreeMap`/`ArrayList`, XML/CSV/binary encoders, and Avro as the documented replacement path.

## Risks and compatibility notes

This is a partial line-bounded chunk. It starts after the beginning of `GzipCodec` and ends before the completion of the `org.apache.hadoop.record` package documentation, so whole-class/package conclusions for those boundaries require adjacent chunks.

TFile is compatibility-sensitive because on-disk layout, comparator naming, compression names, meta-block names, block indexes, and version compatibility are externally visible. Changes to key length limits, chunking behavior, index memory assumptions, scanner range semantics, or comparator construction can break stored-file interoperability or random-access behavior.

TFile APIs have resource-ordering risks. Writers must close to finalize data, staged append key/value streams must be used in the documented sequence, scanner/reader close invalidates behavior, and value length may be unknown unless `isValueLengthKnown()` is checked.

Splittable compression must adjust split boundaries correctly. Incorrect `start`/`end` adjustment or mismatched continuous/block reporting can cause duplicate records, skipped bytes, or failed decompression in parallel file processing.

Native I/O is optional and platform-sensitive. Code must handle unavailable JNI, unsupported flags/constants, permissions failures, and differences in owner/group/mode semantics. `NativeIOException.getErrno()` is the stable way to inspect native failures.

Metrics APIs are stateful and concurrency-sensitive. Periodic updater registration, buffered tag/metric rows, incremental metric handling, provider close/flush behavior, and composite fan-out can produce stale, duplicated, or lost metrics if lifecycle methods are misordered.

Network topology mapping depends on external DNS/script behavior and cache correctness. Bad or partial mappings can affect rack-aware placement decisions. Socket factory equality/hash behavior matters because these factories are often configured reflectively and cached.

Record I/O is deprecated in favor of Avro, but remains a public compatibility surface. Generated-code contracts, binary zero-compressed integer encoding, CSV/XML escaping, `Buffer` aliasing, comparator registration, and `Writable` integration must stay stable for legacy data and generated classes.

## Test signals

JDiff validation should verify the XML remains well-formed across this range and preserves package/class/interface boundaries, method signatures, parameter types, declared exceptions, visibility, field constants, deprecation markers, and embedded package docs.

Compression tests should cover `GzipCodec` stream/decompressor creation, gzip output `finish`/`flush`/`resetState`/`close`, splittable codec adjusted boundaries, and continuous versus block read modes on block-compressed data.

TFile tests should cover writer close/finalization, complete append and staged append paths, duplicate and missing meta-block errors, compression algorithm discovery, sorted and unsorted files, comparator creation, scanner creation by full file/byte range/key range/record range, lower/upper-bound behavior, first/last key lookup, record-number-near and key-near queries, entry buffer copies, streaming key/value access, unknown value length handling, version serialization/compatibility, and `Utils` VInt/VLong/string/binary-search helpers.

Native I/O tests should cover unavailable native libraries, successful and failing `open`, `fstat`, and `chmod`, errno propagation in `NativeIOException`, mode constant interpretation, and `Stat` owner/group/mode getters.

Serialization tests should cover provider `accept()` selection for `Writable`, `Serializable`, Avro reflect tagged/configured-package classes, and Avro specific classes; serializer/deserializer round trips; schema lookup through configuration; and comparator behavior for Java serialization.

Metrics tests should exercise context initialization from attributes, period parsing, start/stop/close lifecycle, updater registration/removal, absolute versus incremental metrics, tag removal, update/remove row behavior, output record copies, file provider append/flush, Ganglia XDR encoding and socket close, composite fan-out, and null/no-emit contexts with and without update threads.

Network tests should cover batch rack resolution, cache hits/misses around a raw mapping, script-based configuration and script failure handling, SOCKS proxy socket construction, standard socket construction, and socket factory equality/hash semantics.

Record I/O tests should cover binary/CSV/XML primitive and composite round trips, generated `Record` tag and tagless serialization/deserialization, `Index` traversal for vectors/maps, `Buffer` set/copy/append/truncate/reset/capacity/compare/clone behavior, zero-compressed integer edge cases, byte lexicographic comparison, comparator registration, and legacy generated-code compatibility against existing encoded data.
