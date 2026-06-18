# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.2.xml lines 17974-24258

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.8.2. It starts inside the tail of `org.apache.hadoop.io.IntWritable`, covers a broad public-contract slice of `org.apache.hadoop.io`, compression, TFile, serializer, Avro serializer, log metrics, legacy metrics, Ganglia metrics, and metrics SPI APIs, then stops at the beginning of `org.apache.hadoop.metrics.spi.MetricsRecordImpl`.

The source is generated XML API metadata, not executable implementation source. The research surface is therefore the compatibility contract exposed by class/interface names, inheritance, implemented interfaces, method signatures, constructors, public/protected fields, checked exceptions, synchronization flags, deprecation markers, and embedded Javadocs.

## Purpose

The `org.apache.hadoop.io` portion defines Hadoop's core binary serialization, mutable value wrappers, raw byte comparators, map-like writable containers, text encoding helpers, file-format entry points, and utility routines used by RPC, MapReduce shuffle/sort, SequenceFile/MapFile persistence, and configuration serialization.

The `org.apache.hadoop.io.compress` portion defines the compression abstraction layer over streams, codecs, compressors, decompressors, codec discovery, object pooling, direct decompression, and split-aware compressed input. These APIs let Hadoop file formats and input splits use pluggable compression while reusing native or Java codec instances.

The `org.apache.hadoop.io.file.tfile` portion exposes TFile public constants, comparator construction, supported compression names, raw comparable keys, and utility routines for variable-length integers and sorted-array searching.

The serializer portions define Java, Writable, and Avro serialization adapters for Hadoop's `io.serializations` framework. The log and metrics portions expose legacy Log4J event counting and the deprecated pre-metrics2 metrics stack, including Ganglia emission and the SPI context used by metrics implementations.

## Important APIs, Types, and Functions

### Core `org.apache.hadoop.io`

- The chunk begins with the tail of `IntWritable`: `equals(Object)`, `hashCode()`, `compareTo(IntWritable)`, and `toString()`, confirming the value-object and ordering contract for integer writables.
- `IOUtils` exposes stream and channel helpers: `copyBytes` overloads for `InputStream` to `OutputStream` with explicit buffer size, `Configuration`, count, and close behavior; `wrappedReadForCompressedData`; `readFully`; `skipFully`; cleanup helpers that ignore close failures; `closeSocket`; full `ByteBuffer` writes to `WritableByteChannel` or positioned `FileChannel`; directory listing with explicit `IOException`; and `fsync(File)` / `fsync(FileChannel, boolean)`.
- `LongWritable`, `ShortWritable`, `VIntWritable`, and `VLongWritable` are mutable `WritableComparable` numeric wrappers with constructors, `set`, `get`, `readFields`, `write`, equality, hash, comparison, and string conversion. `VIntWritable` and `VLongWritable` use Hadoop variable-length integer encodings through `WritableUtils`.
- `MapFile` exposes outer file-level operations and constants: protected constructor, `rename`, `delete`, `fix`, `main`, `INDEX_FILE_NAME`, and `DATA_FILE_NAME`. The docs define a MapFile as a directory containing sorted key/value `data` plus an in-memory-sampled `index`.
- `SetFile` extends `MapFile` and represents a file-backed set keyed by `WritableComparable` values.
- `MapWritable` extends `AbstractMapWritable` and implements `java.util.Map`, exposing copy construction, the usual map operations, and `write` / `readFields` persistence for heterogeneous writable keys and values.
- `SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap`, adding `comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, and `tailMap` while retaining writable serialization.
- `MD5Hash` is a fixed-length 16-byte `WritableComparable` digest holder. It exposes constructors from hex string and byte array, static `read`, `digest` overloads for byte arrays, `InputStream`, `String`, and `UTF8`, thread-local `getDigester`, `halfDigest`, `quarterDigest`, `setDigest`, byte access through `getDigest`, and hex/string/compare/hash behavior. `MD5_LEN` is the stable digest length constant.
- `MultipleIOException` aggregates several `IOException` instances through `getExceptions()` and `createIOException(List<IOException>)`, returning either a single exception or an aggregate wrapper.
- `NullWritable` is the singleton empty writable. `get()` returns the singleton, `readFields` and `write` transfer no bytes, and comparison/equality/hash behavior is fixed for a zero-size value.
- `ObjectWritable` wraps arbitrary declared-class/object pairs for Hadoop serialization and implements both `Writable` and `Configurable`. It exposes object and declared-class accessors, `set`, `readFields`, `write`, `writeObject` overloads, `readObject` overloads, class loading, and configuration propagation.
- `RawComparator<T>` extends `Comparator<T>` with serialized-byte comparison: `compare(byte[], int, int, byte[], int, int)`.
- `SequenceFile` exposes outer static configuration and writer construction APIs: `getDefaultCompressionType`, `setDefaultCompressionType`, many `createWriter` overloads including `Configuration`, `FileSystem`, `Path`, key/value classes, compression type, codec, progress callback, metadata, replication, block size, buffer size, and the newer `Writer.Option...` form. `SYNC_INTERVAL` is public.
- `Stringifier<T>` is a closeable conversion contract with `toString(T)`, `fromString(String)`, and `close()`.
- `Text` is Hadoop's mutable UTF-8 string type extending `BinaryComparable` and implementing `WritableComparable`. It exposes constructors from Java `String`, another `Text`, or bytes; backing-byte access; length; Unicode-code-point `charAt`; byte-level `find`; several `set` overloads; `append`; `clear`; UTF-8 decode/encode helpers; `readString`/`writeString`; `validateUTF8`; `bytesToCodePoint`; `utf8Length`; and `DEFAULT_MAX_LEN`.
- `TwoDArrayWritable` serializes two-dimensional `Writable` arrays with value-class constructors, `toArray`, `set`, `get`, `readFields`, and `write`.
- `VersionedWritable` writes and checks a version byte through `getVersion`, `write`, and `readFields`; `VersionMismatchException` reports expected/found version conflicts.
- `Writable` is the fundamental Hadoop binary serialization interface with `write(DataOutput)` and `readFields(DataInput)`. `WritableComparable` combines `Writable` and Java `Comparable`.
- `WritableComparator` is the comparator registry and optimized raw comparator base. It exposes comparator lookup/definition, key-class construction, object and raw byte comparison, static byte comparison/hashing, primitive readers (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`), and `Configurable` support.
- `WritableFactories` and `WritableFactory` provide custom factory registration and new writable instance creation, with optional `Configuration` injection.
- `WritableUtils` centralizes compressed byte/string array helpers, simple string helpers, clone/cloneInto through serialization, variable-length integer read/write/size/range helpers, enum read/write, `skipFully`, `toByteArray`, and bounded `readStringSafely`.

### Compression APIs

- `BlockCompressorStream` and `BlockDecompressorStream` are block-oriented compression streams using `Compressor` and `Decompressor` instances. Their exposed methods cover block writes, finish, compress/decompress, compressed-data loading, and state reset.
- `BZip2Codec`, `DefaultCodec`, and `GzipCodec` expose `CompressionCodec` implementations. They create compression/decompression streams, return compressor/decompressor classes, create/reuse codec engines, expose default extensions, and in relevant cases support direct or split decompression.
- `CodecPool` leases and returns `Compressor` and `Decompressor` instances and exposes leased-count metrics. It is the integration point for reducing codec allocation and native resource churn.
- `CompressionCodec` defines the basic codec contract for stream creation, compressor/decompressor type discovery, engine creation, and default file extension.
- `CompressionCodecFactory` discovers codecs from `Configuration`, exposes static codec class getters/setters, resolves codecs by path extension, class name, or short name, removes compression suffixes, and includes a command-line `main`.
- `CompressionInputStream` and `CompressionOutputStream` are seekable/read or write stream bases with `resetState`, close/flush/finish behavior, protected wrapped stream fields, and position/seek hooks.
- `Compressor` and `Decompressor` define low-level stateful engine contracts: input/dictionary setting, needs-input or needs-dictionary status, byte counters, finish/finished status, compress/decompress calls, remaining input, `reset`, `end`, and compressor `reinit(Configuration)`.
- `CompressorStream` and `DecompressorStream` adapt the low-level engines to Java stream behavior, exposing buffered stream state, EOF/closed flags, skip/available/mark/reset support, and reset/close semantics.
- `DirectDecompressionCodec` and `DirectDecompressor` add direct `ByteBuffer` decompression for codecs that can avoid byte-array copies.
- `SplitCompressionInputStream` carries adjusted split start/end offsets for splittable compressed input. `SplittableCompressionCodec` creates such streams with `READ_MODE` and split boundaries.

### TFile and Serializer APIs

- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are TFile-specific `IOException` types for duplicate and missing metadata blocks.
- `RawComparable` exposes a raw byte buffer, offset, and size for comparator implementations that avoid object creation.
- `TFile` exposes `makeComparator`, `getSupportedCompressionAlgorithms`, `main`, and constants `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, `COMPARATOR_MEMCMP`, and `COMPARATOR_JCLASS`. The docs describe TFile as a sorted key/value file format with block compression, metadata blocks, and pluggable comparators.
- `org.apache.hadoop.io.file.tfile.Utils` exposes variable-length integer/string read/write helpers and lower/upper-bound binary searches over raw-comparable arrays and `List` ranges.
- `JavaSerialization` implements Hadoop `Serialization` using Java `Serializable`, and `JavaSerializationComparator` compares Java-serialized objects by deserializing them and applying `Comparable`.
- `WritableSerialization` implements Hadoop `Serialization` for `Writable`, delegating to `Writable.write` and `Writable.readFields`.
- `AvroReflectSerializable` is a marker interface for Avro reflect serialization. `AvroSerialization` is the abstract configured base with `AVRO_SCHEMA_KEY`. `AvroReflectSerialization` accepts configured packages through `AVRO_REFLECT_PACKAGES` or the marker interface. `AvroSpecificSerialization` targets classes generated by Avro's specific compiler.

### Logging and Legacy Metrics

- `EventCounter` is a Log4J `AppenderSkeleton` that counts fatal, error, and warn logging events. It exposes the appender lifecycle methods `append(LoggingEvent)`, `close()`, and `requiresLayout()`.
- The `org.apache.hadoop.metrics` package docs define the deprecated metrics API: contexts, records, metric names, tags, buffered updates, periodic emission, updater callbacks, and configuration through `hadoop-metrics.properties` and `ContextFactory` attributes.
- `GangliaContext` extends `AbstractMetricsContext` and is deprecated in favor of metrics2 Ganglia sinks. It exposes `close`, protected `emitMetric`, metric metadata lookup helpers `getUnits`, `getSlope`, `getTmax`, `getDmax`, XDR buffer writers `xdr_string` and `xdr_int`, and protected fields for buffer, offset, metrics server list, and datagram socket.
- `AbstractMetricsContext` is the deprecated metrics SPI base implementing `MetricsContext`. It exposes initialization from `ContextFactory`, attribute lookup/table derivation, context metadata, synchronized start/stop/close and updater registration, final `createRecord`, overridable `newRecord`, `getAllRecords`, abstract `emitRecord`, optional `flush`, protected update/remove hooks for `MetricsRecordImpl`, and period parsing/setters.
- `CompositeContext` extends `AbstractMetricsContext` as a deprecated aggregate context.
- The chunk ends immediately after the protected `MetricsRecordImpl(String, AbstractMetricsContext)` constructor. The rest of `MetricsRecordImpl` belongs to a later chunk.

## Control Flow

The XML has no executable control flow, but the API contracts imply several important flows:

- Writable values are caller-driven mutable serializers. Callers construct or reuse an instance, call `write(DataOutput)` to emit the current state, and call `readFields(DataInput)` to mutate the same instance from serialized bytes. Comparators can either deserialize objects or compare raw byte slices directly.
- Map-like writables serialize dynamic key/value classes along with entry data. `MapWritable` and `SortedMapWritable` depend on `AbstractMapWritable` class-id bookkeeping, then serialize entries and nested writable values.
- `ObjectWritable` serializes a declared class and value, then resolves classes with configuration-aware class loading during reads. Its static helpers are the bridge used by RPC-like code that must carry arbitrary primitive, string, array, or `Writable` objects.
- `Text` maintains UTF-8 bytes and logical length. Set/append mutate byte storage, string conversion decodes bytes, `charAt` and `find` operate over UTF-8-aware byte offsets, and static helpers enforce maximum lengths and UTF-8 validity for stream reads.
- SequenceFile writer creation flows through overloaded static factories into a configured writer with key/value classes, compression type, codec, filesystem path or stream, progress, metadata, and storage parameters. The newer option-based overload is the preferred compatibility direction over many deprecated positional overloads.
- Compression stream flow separates codec selection, compressor/decompressor leasing, stream wrapping, block or streaming compression, flush/finish/close, reset, and eventual engine return/end. Split-aware codecs adjust compressed input starts and ends so file-input formats can align record reads after split boundaries.
- `CompressionCodecFactory` flows from configured codec classes to extension/name/class lookup. Path-based lookup maps filename suffixes to codecs, while `removeSuffix` strips known codec extensions from logical filenames.
- TFile comparator flow creates a comparator by name, then compares either memory bytes or Java-class-specific key objects. TFile utility lower/upper bounds support binary search against sorted raw-comparable key ranges.
- Serialization framework flow reads `io.serializations`, creates a matching `Serialization`, then obtains serializers/deserializers for Java `Serializable`, Hadoop `Writable`, Avro specific, or Avro reflect classes.
- Metrics flow is buffered and periodic. User code updates a `MetricsRecord`; `AbstractMetricsContext.update` stores a row in an internal table; timer-driven monitoring invokes registered `Updater` callbacks, emits `OutputRecord` instances through subclass `emitRecord`, then calls `flush`. Removal deletes matching rows by record tags. Ganglia emission encodes metric metadata and values into XDR-formatted UDP datagrams.
- Log event counting flow is Log4J-driven: `append` is called for each logging event, and the appender updates counters for fatal/error/warn levels.

## State and Persistence Behavior

The JDiff XML persists public API metadata for compatibility checking. It does not persist Hadoop runtime data itself.

The APIs described here are highly persistence-sensitive. `Writable`, primitive writables, variable-length writables, `Text`, `MapWritable`, `SortedMapWritable`, `ObjectWritable`, `MD5Hash`, arrays, versioned writables, `SequenceFile`, `MapFile`, TFile, and serializer adapters define or expose binary formats used in files, RPC, shuffle/sort, and configuration storage. Changes to byte order, length encoding, UTF-8 validation, class-name/class-id handling, version bytes, comparator order, compression metadata, or sync intervals can break stored data and cross-version interoperability.

Several classes are mutable by design. Numeric writables, `Text`, `MD5Hash`, map writables, `ObjectWritable`, compressor/decompressor engines, compression streams, and metrics records are intended for reuse. Consumers must not retain backing arrays or mutable instances without copying when later mutation would be unsafe.

Compression state is split between reusable codec engines and stream wrappers. `Compressor` and `Decompressor` expose counters, input buffers, dictionaries, finish flags, reset, end, and reinitialization. `CodecPool` holds leased/global state and must receive returned engines to avoid native-resource and memory leaks.

File persistence appears through MapFile's `data` and `index` directory layout, SequenceFile's key/value streams and sync markers, TFile's compressed blocks and metadata blocks, and compression file extensions. `IOUtils.fsync` explicitly exists to force local file or directory metadata to durable storage where supported.

Metrics state is buffered in `AbstractMetricsContext` until periodic emission. `stopMonitoring()` stops emission but does not free buffered data, while `close()` stops monitoring and returns the context toward its initial state. Ganglia context state includes datagram socket, destination server list, XDR buffer, and offset.

Configuration state appears through `Configuration` and `Configured` integration, including default SequenceFile compression type, writable factories, `ObjectWritable` class loading, codec discovery, serializer selection through `io.serializations`, Avro reflect package lists, and legacy metrics attributes from `hadoop-metrics.properties`.

## Dependencies and Integration Points

This chunk integrates heavily with Java core APIs: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `FilenameFilter`, `Socket`, `ByteBuffer`, `FileChannel`, `WritableByteChannel`, `MessageDigest`, `Comparator`, `Map`, `SortedMap`, `Collection`, `List`, `Set`, `Closeable`, Log4J `AppenderSkeleton`/`LoggingEvent`, `DatagramSocket`, and Java serialization.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration`, `Configurable`, and `Configured` for object construction, codec setup, serializer setup, writable cloning, and metrics configuration.
- `org.apache.hadoop.fs.FileSystem` and `Path` for MapFile operations, SequenceFile writer creation, and codec lookup by path extension.
- `org.apache.hadoop.util.Progressable` for long-running writer/sort/copy style operations.
- `org.apache.hadoop.io.serializer.Serialization`, `Serializer`, `Deserializer`, and deserializer comparators for pluggable serialization.
- `org.apache.hadoop.io.compress` codecs and native codec wrappers through `CodecPool`, direct decompressors, and split-aware input streams.
- Avro specific and reflect serialization through Avro-generated classes, configured reflect packages, and schema configuration keys.
- Legacy metrics APIs through `ContextFactory`, `MetricsContext`, `MetricsRecord`, `Updater`, `OutputRecord`, Ganglia UDP/XDR formatting, and the newer `org.apache.hadoop.metrics2` replacement noted in deprecation text.

## Risks and Edge Cases

- This chunk starts inside `IntWritable` and ends at the first constructor of `MetricsRecordImpl`; adjacent chunks must be reconciled before drawing final file-wide conclusions for those classes.
- JDiff records signatures and Javadocs, not method bodies. Exact buffer sizes, synchronization internals, allocation behavior, registry maps, exception messages, and resource-cleanup order require implementation-source validation.
- Writable serialization is order- and type-sensitive. Reading with the wrong class, wrong declared type, or changed field layout can silently corrupt values or fail late.
- `readFields` mutates existing objects. Reusing objects across records is efficient but can surprise callers that store references rather than copies.
- `ObjectWritable` class-name serialization and dynamic class loading are compatibility and security-sensitive, especially when reading untrusted data or when classes differ across cluster nodes.
- `WritableComparator` raw byte readers assume valid serialized encodings. Malformed or truncated byte arrays can produce incorrect ordering or exceptions in sort paths.
- Variable-length integer encodings must preserve negative-value and size rules. Range-limited reads should reject out-of-range values rather than wrap.
- `Text` has separate byte length and string/code-point views. Invalid UTF-8, truncated multibyte sequences, maximum-length enforcement, and byte-offset `find` behavior are common boundary risks.
- `MapFile` docs require sorted key insertion and keep the index in memory. Unsorted writes, corrupt indexes, very large keys, or overly dense indexes can break lookup behavior or consume excessive memory.
- Many `SequenceFile.createWriter` overloads are deprecated in favor of option-based creation. Compatibility must preserve old overloads while keeping behavior consistent with the preferred API.
- Compression engines are stateful and often wrap native resources. Failing to reset, finish, end, or return pooled engines can leak memory, produce invalid streams, or contaminate later users with stale dictionaries/input.
- Split compression is codec-specific. Non-splittable codecs, incorrect adjusted starts, or incorrect end offsets can cause duplicate or missed records across input splits.
- BZip2, Gzip, DefaultCodec, LZO-named TFile constants, and codec factory discovery depend on optional libraries and configuration. Missing native libraries or classpath entries should fail predictably.
- `CodecPool` leased-count APIs are useful leak signals but can also reveal imbalance when callers abandon compressors/decompressors after exceptions.
- Java serialization is slower and less portable than Writable serialization, and deserializing arbitrary Java objects can be unsafe if inputs are untrusted.
- Avro reflect package configuration is broad. Misconfigured package lists can serialize unintended classes or fail to match intended reflect classes.
- Legacy metrics APIs and Ganglia context are deprecated. New development should prefer metrics2, but compatibility testing must preserve the old API surface for 2.8.2 users.
- Ganglia emission uses UDP and local XDR buffers. Packet loss, metric-name metadata configuration, buffer sizing, multicast TTL, and socket closure are operational edge cases.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks that all documented public/protected classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, synchronization markers, and deprecation markers remain stable for Hadoop Common 2.8.2.
- Writable round-trip and golden-byte tests for `LongWritable`, `ShortWritable`, `VIntWritable`, `VLongWritable`, `NullWritable`, `Text`, `MD5Hash`, `MapWritable`, `SortedMapWritable`, `ObjectWritable`, `TwoDArrayWritable`, and `VersionedWritable`.
- Comparator tests comparing object-level ordering against raw-byte ordering for numeric writables, `Text`, `MD5Hash`, `NullWritable`, custom `RawComparator` implementations, and `WritableComparator` primitive readers.
- `WritableUtils` tests for compressed byte/string arrays, variable-length integer size/sign/range behavior, enum read/write, clone/cloneInto, `skipFully`, `toByteArray`, and bounded safe string reads.
- `IOUtils` tests for short copy loops, exact-count copies, EOF handling, skip loops, close/cleanup exception swallowing, socket closure, compressed-data exception wrapping, full channel writes, directory listing errors, and file/directory `fsync`.
- `MapWritable` and `SortedMapWritable` tests for heterogeneous class-id persistence, copy construction, map view behavior, sorted-map range views, null/unsupported key handling, and class-id exhaustion cases inherited from `AbstractMapWritable`.
- `ObjectWritable` tests for primitive types, arrays, strings, nested writables, null handling, declared-class mismatches, compact-array compatibility modes, configuration/classloader propagation, and malformed class names.
- `Text` tests for UTF-8 validation, multibyte `charAt`, byte-offset `find`, append growth, clear/reset behavior, max-length enforcement, encode/decode replacement behavior, and static read/write helpers.
- SequenceFile writer-factory tests covering old positional overloads, new option overloads, compression type configuration, codec/metadata/progress propagation, replication/block/buffer parameters, and deprecation compatibility.
- MapFile and SetFile tests for directory rename/delete, corrupt index repair with dry-run and actual modes, sorted-key requirements, index interval behavior, and large-key memory pressure.
- Compression tests for compressor/decompressor lifecycle, finish/reset/end semantics, short input/output buffers, dictionaries, byte counters, `CodecPool` lease/return counts, default extensions, codec discovery by extension/name/class, suffix removal, and missing codec classes.
- Stream tests for `BlockCompressorStream`, `BlockDecompressorStream`, `CompressorStream`, `DecompressorStream`, `CompressionInputStream`, `CompressionOutputStream`, direct decompression, split adjusted start/end behavior, mark/reset support, and close idempotence.
- TFile tests for comparator creation, supported compression names, raw comparable lower/upper bounds, variable-length integer/string helpers, duplicate/missing metadata block exceptions, and command-line `main` behavior.
- Serializer tests for Java serialization, Java deserializer comparison, Writable serialization delegation, configured `io.serializations`, Avro specific serialization, Avro reflect marker/package matching, schema-key behavior, and configuration propagation.
- Log and metrics tests for Log4J appender event counting, legacy metrics context initialization from factory attributes, period parsing, updater registration/unregistration, buffered update/remove semantics, `getAllRecords`, start/stop/close behavior, Ganglia XDR integer/string formatting, UDP destination parsing, multicast attributes, and socket cleanup.

## Cross-Chunk Notes

The previous chunk owns the beginning and main body of `IntWritable`; this chunk only captures its tail methods. The next chunk should complete `MetricsRecordImpl` and the rest of `org.apache.hadoop.metrics.spi`. The merge lane should combine adjacent chunks before publishing the final per-file report for `Apache_Hadoop_Common_2.8.2.xml`.
