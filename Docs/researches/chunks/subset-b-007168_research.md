# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 17995-24293

## Purpose

This chunk is part of the generated JDiff API description for Hadoop Common 2.8.0. It is public API metadata rather than executable Java implementation. The useful research signal is the compatibility contract: packages, classes, interfaces, inheritance, implemented interfaces, constructors, methods, fields, visibility, checked exceptions, deprecation text, and embedded Javadocs.

The range starts inside the tail of `org.apache.hadoop.io.IOUtils`, covers most of the core `org.apache.hadoop.io` serialization and container APIs, covers the public compression codec framework in `org.apache.hadoop.io.compress`, covers TFile API metadata, serialization provider markers, legacy log/metrics surfaces, and ends inside the beginning of `org.apache.hadoop.metrics.spi.MetricsRecordImpl`.

## Important APIs and Types

### `org.apache.hadoop.io`

- The chunk begins with `IOUtils` stream helpers: `copyBytes` overloads, `wrappedReadForCompressedData`, `readFully`, `skipFully`, cleanup/close helpers that ignore cleanup-time `IOException`, socket close helpers, `writeFully` for `WritableByteChannel` and positional `FileChannel`, and `listDirectory`. These APIs centralize defensive I/O loops, short-write handling, and cleanup behavior.
- `LongWritable`, `ShortWritable`, `VIntWritable`, and `VLongWritable` are mutable primitive wrappers implementing `WritableComparable`. They expose value constructors, `set`, `get`, `readFields`, `write`, equality, hash, comparison, and string conversion.
- `MapFile` is a file-backed sorted map stored as a directory containing `data` and `index` files. Public constants name those files. Static helpers support rename, delete, command-line entry, and `fix(...)`, which can rebuild a corrupt index by scanning `data` and optionally dry-running.
- `SetFile` is the set variant of `MapFile`.
- `MapWritable` and `SortedMapWritable` extend `AbstractMapWritable` and implement Java `Map`/`SortedMap` with `Writable` keys and values. They expose copy constructors, normal map operations, and `Writable` serialization methods. `SortedMapWritable` additionally exposes comparator, first/last key, and head/sub/tail map views over `WritableComparable` keys.
- `MD5Hash` is a `WritableComparable` wrapper for 16-byte MD5 digests. It provides string/byte constructors, static `read`, `digest` overloads, `getDigester`, `getDigest`, `set`, `setDigest`, `halfDigest`, `quarterDigest`, comparison, equality, hash, and string conversion. `MD5_LEN` is the public digest-length constant.
- `MultipleIOException` aggregates multiple `IOException` instances and can convert a list into either a single `IOException`, a wrapper, or null depending on list contents.
- `NullWritable` is a singleton zero-byte `WritableComparable`, used where a key or value position exists in the API but no payload is needed.
- `ObjectWritable` is a polymorphic `Writable` and `Configurable` wrapper. It serializes class identity plus instances for `Writable`, `String`, primitives, and arrays. Its `allowCompactArrays` option is documented for RPC/internal use, while persisted or inter-cluster files should avoid compact arrays for compatibility.
- `RawComparator` extends `Comparator` with byte-range comparison so sort and shuffle paths can compare serialized records without full object creation.
- `SequenceFile` is the binary key/value file container API. This chunk exposes default compression-type accessors, a modern `createWriter(Configuration, Writer.Option...)`, many deprecated writer overloads, FileSystem/FileContext/raw-output writer creation, compression codec selection, metadata/progress/block-size/replication/create-parent options, and `SYNC_INTERVAL`. The Javadoc documents the common header and three storage formats: uncompressed, record-compressed values, and block-compressed key/value blocks.
- `Stringifier<T>` is a closeable conversion interface for serializing objects to strings and restoring them from strings.
- `Text` is Hadoop's mutable UTF-8 byte string. It exposes constructors from string, `Text`, and byte arrays; raw byte access with separate length; byte-position search; code-point access; set/append/clear; bounded read/write methods; static skip, encode/decode, UTF-8 validation, read/write string helpers, `bytesToCodePoint`, `utf8Length`, and `DEFAULT_MAX_LEN`.
- `TwoDArrayWritable` persists rectangular or ragged two-dimensional arrays of a configured `Writable` value class.
- `VersionedWritable` prefixes writable payloads with a version byte and validates versions through `VersionMismatchException`.
- `Writable` defines the core Hadoop binary serialization contract: `write(DataOutput)` and `readFields(DataInput)`. The docs require `readFields` to fully overwrite object state, not merge with previous state.
- `WritableComparable` combines `Writable` and `Comparable` for values that can be serialized and sorted.
- `WritableComparator` is the comparator registry and raw-comparison base. It can construct keys, register custom comparators with `define`, compare objects or serialized bytes, and parse primitive/vint values directly from byte arrays.
- `WritableFactories` and `WritableFactory` allow custom construction of non-public or special `Writable` classes, including configuration-aware instantiation.
- `WritableUtils` provides compressed byte/string helpers, string arrays, writable cloning/copying, variable-length integer/long encoding and decoding, range-checked vint reads, enum serialization by name, full skipping, byte-array conversion, and safe bounded string reads.

### `org.apache.hadoop.io.compress`

- `BlockCompressorStream` and `BlockDecompressorStream` adapt block-oriented compressors to Hadoop compression streams. Blocks include uncompressed length followed by one or more length-prefixed compressed chunks; decompression can reset state.
- `BZip2Codec` implements `Configurable` and `SplittableCompressionCodec`. It can use native bzip2 or pure Java depending on configuration. The docs warn that pure-Java mode does not implement `Compressor`/`Decompressor` methods that accept those objects, and splittable reads force pure-Java mode.
- `CodecPool` is the process-level pool for reusable `Compressor` and `Decompressor` instances, with get/return calls and leased compressor/decompressor counts.
- `CompressionCodec` defines the common codec contract: create compression/decompression streams with or without pooled codec state, expose compressor/decompressor classes, create state instances, and provide a default filename extension.
- `CompressionCodecFactory` discovers configured codecs, maps file extensions and class names to codecs, removes codec suffixes from filenames, exposes codec-class configuration helpers, logs through `LOG`, and has a command-line entry point.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream wrappers with protected underlying stream fields. Input streams expose `resetState`, position, seek, and alternate-source seeking. Output streams expose `finish` and `resetState` in addition to flush/close/write behavior.
- `Compressor` and `Decompressor` model zlib-style state machines. They manage input buffers, dictionaries, byte counters, finish/finished state, reset/end, reinitialization, remaining input, and decompression output loops.
- `CompressorStream` and `DecompressorStream` are concrete stream adapters that own a compressor/decompressor, byte buffer, closed/eof flags, and read/write/skip/available/close/reset behavior.
- `DefaultCodec` is the default configurable codec and also implements `DirectDecompressionCodec`.
- `DirectDecompressionCodec` and `DirectDecompressor` define decompression into direct `ByteBuffer` instances.
- `GzipCodec` extends `DefaultCodec` with gzip-specific stream and codec-state creation.
- `SplitCompressionInputStream` and `SplittableCompressionCodec` define split-aware compressed reads. Codecs may adjust requested compressed start/end offsets to block or algorithm boundaries, and `READ_MODE` controls whether position is reported continuously or at block boundaries.

### `org.apache.hadoop.io.file.tfile`

- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are checked exceptions for named TFile metadata blocks.
- `RawComparable` identifies a comparable byte range through `buffer`, `offset`, and `size`; an external `RawComparator` supplies the comparison semantics.
- `TFile` is a byte-oriented key/value container with type-less keys and values, 64 KB key limit, block compression, named metadata blocks, sorted or unsorted keys, and seeking by key or file offset. Public constants identify compression algorithms (`gz`, `lzo`, `none`) and comparator naming (`memcmp`, Java class prefix). `makeComparator`, `getSupportedCompressionAlgorithms`, and `main` are exposed.
- `Utils` contains TFile-local helpers for vint/vlong and string serialization plus binary-search style `lowerBound`/`upperBound` operations over lists and arrays using raw comparators.

### Serialization, Logging, and Legacy Metrics Packages

- `org.apache.hadoop.io.serializer` includes `JavaSerialization`, `JavaSerializationComparator`, and `WritableSerialization`. These are provider classes for Hadoop's serialization framework, including comparator support for Java-serialized values and the configured writable serializer.
- `org.apache.hadoop.io.serializer.avro` includes marker/interface and provider classes for Avro reflection and specific-record serialization. `AvroSerialization` exposes `AVRO_SCHEMA_KEY`; `AvroReflectSerialization` exposes `AVRO_REFLECT_PACKAGES`.
- `org.apache.hadoop.ipc.protocolPB` and `org.apache.hadoop.log` appear as package markers in this range.
- `org.apache.hadoop.log.metrics.EventCounter` is a Log4J `AppenderSkeleton` exposing `append`, `close`, and `requiresLayout`, used to count logging events for metrics.
- `org.apache.hadoop.metrics` package documentation describes the original Hadoop metrics API: `MetricsContext`, `MetricsRecord`, `Updater`, `ContextFactory`, and factory attributes such as `period`, `servers`, and class names. It is deprecated in favor of `metrics2`.
- `org.apache.hadoop.metrics.ganglia.GangliaContext` is a deprecated `AbstractMetricsContext` implementation that emits metrics to Ganglia servers over UDP. It exposes `close`, `emitMetric`, metadata lookup helpers for units/slope/tmax/dmax, XDR encoding helpers, and protected state for buffer, offset, server list, and datagram socket.
- `org.apache.hadoop.metrics.spi.AbstractMetricsContext` is the deprecated SPI base for the old metrics system. It manages context initialization, factory attributes, monitoring start/stop/close, record creation, updater registration, all-record retrieval, abstract `emitRecord`, optional `flush`, internal table `update`/`remove`, and period parsing. `CompositeContext` extends it as a deprecated composite implementation.
- The chunk ends inside `MetricsRecordImpl`, after its constructor, `getRecordName`, tag setters for string/integer types, `removeTag`, and the beginning of metric setters. The rest of `MetricsRecordImpl` is outside this mapped range.

## Control Flow

The `Writable` family defines the core serialization flow: callers allocate or reuse mutable objects, invoke `readFields` to fully replace prior state from a `DataInput`, and invoke `write` to emit a stable binary representation. Primitive writables write fixed or variable-length encodings. Map writables must serialize both class metadata and entry payloads so readers can reconstruct heterogeneous `Writable` key/value types.

`ObjectWritable` adds a polymorphic serialization flow. The writer records the declared class and payload, with special handling for primitive types, strings, arrays, and writable implementations. The reader loads classes through the provided `Configuration`, constructs instances through normal reflection or `WritableFactories`, then reads the payload. The compact-array flag changes wire format and is therefore reserved for compatibility-bounded contexts.

`SequenceFile` writer creation flows through either the modern options API or legacy overloads. The selected file system/context, output path/stream, key and value classes, compression type, codec, metadata, buffering, replication, block size, create flags, and progress callbacks determine the writer. At persistence time every file has a header with version, key/value classes, compression flags, codec, metadata, and sync marker. Records are then written uncompressed, record-compressed, or block-compressed; readers use the header and sync markers to bridge all supported formats.

`MapFile` builds on `SequenceFile` semantics by requiring sorted key insertion into a `data` file and a smaller in-memory `index` file. The `fix` path scans existing data and can rebuild the index, with dry-run mode to report without mutation.

`Text` control flow is byte-oriented rather than Java `String` oriented. Search and `charAt` operate on UTF-8 byte positions to avoid string allocation. Decode/encode can either replace malformed input or throw `CharacterCodingException`. Bounded read/write methods and `readStringSafely` provide defensive length checks before allocating.

Compression control flow is state-machine driven. A codec creates streams and optional reusable compressor/decompressor state. Callers feed input only when `needsInput()` is true, keep buffers stable until the codec has consumed them, call `finish()` to drain output, and call `reset()`/`end()` when reusing or releasing native state. Block streams add block-length framing, while split-aware codecs may adjust requested start/end offsets before returning a `SplitCompressionInputStream`.

Legacy metrics control flow starts with a `ContextFactory` creating and initializing an `AbstractMetricsContext`. Monitoring starts a timer, registered `Updater` callbacks update `MetricsRecordImpl` instances, records update or remove rows in the context's internal metric table, and each period calls subclass `emitRecord` followed by optional `flush`. Ganglia output converts metric records into XDR-like UDP datagrams for configured servers.

## State and Persistence Behavior

Most `org.apache.hadoop.io` classes in this chunk are mutable value objects. Their serialized form is compatibility-critical because Hadoop RPC, SequenceFile, MapFile, TFile, and many persisted metadata paths depend on stable read/write behavior. Reusing instances is normal, so `readFields` implementations must clear old state before reading new state.

`Text` stores an internal byte array plus a logical length. `getBytes()` can expose capacity beyond the valid range; `copyBytes()` returns an exact-length copy. `clear()` does not release the backing array, so retained buffers can preserve memory until reset with an empty byte array or smaller value.

`MapFile` persists data under a directory with `data` and `index` children. The index is read fully into memory, so key size and index interval affect memory footprint. `fix` can mutate persistent index state unless `dryrun` is true.

`SequenceFile` persists format, compression, class names, metadata, sync markers, and record blocks. Changing headers, sync intervals, compression semantics, or variable-length integer formats would break readers and sort/shuffle tooling.

`WritableComparator`, `WritableFactories`, and `CodecPool` expose process-wide registries/pools. These are not durable persistence, but they are global JVM state and can affect subsequent comparisons, object construction, or codec reuse.

Compression stream objects keep transient state: underlying stream, buffers, compressor/decompressor instances, eof/closed flags, adjusted split boundaries, and byte counters. Native compressors and decompressors require explicit return to `CodecPool` or `end()` to avoid leaks.

TFile persists byte keys/values, compressed blocks, metadata blocks, comparator identity, and compression algorithm names. Its public constants and comparator-name parsing are part of the on-disk interpretation contract.

The old metrics SPI stores transient in-process metric records, updater lists, periods, monitoring state, and output buffers. Ganglia integration sends UDP datagrams but does not persist local durable state.

## Dependencies and Integration Points

- Core I/O APIs depend on Java `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `Closeable`, `Socket`, `ByteBuffer`, `WritableByteChannel`, `FileChannel`, `File`, `FilenameFilter`, `MessageDigest`, and Hadoop `Configuration`.
- File container APIs integrate with `org.apache.hadoop.fs.FileSystem`, `FileContext`, `Path`, `FSDataOutputStream`, `Options.CreateOpts`, `Progressable`, compression codecs, raw comparators, and Hadoop sort/shuffle code paths.
- Serialization APIs integrate with `Configured`, Hadoop `Serialization`, Java serialization, writable serialization, Avro reflection/specific serialization, and class loading through `Configuration`.
- Compression APIs integrate with native codec libraries, pure-Java fallbacks, Hadoop codec discovery configuration, `CodecPool`, split input processing for MapReduce, direct `ByteBuffer` decompression, and filesystem filename extension matching.
- TFile integrates with raw byte comparators, codec names, compression algorithms, metadata blocks, binary search utilities, and command-line dump tooling.
- Legacy metrics APIs integrate with Apache Commons Logging, Log4J, Ganglia UDP servers, `ContextFactory` attributes, `MetricsContext`, `MetricsRecord`, `Updater`, old SPI `OutputRecord`, and the newer `metrics2` package through deprecation guidance.

## Risks and Edge Cases

- This is generated JDiff XML, not implementation. It should be treated as public-contract evidence. Any mismatch with Java source or bytecode would affect API compatibility analysis.
- The chunk starts inside `IOUtils` and ends inside `MetricsRecordImpl`; adjacent chunks are required before making final whole-class conclusions for those two classes.
- Silent cleanup helpers intentionally ignore `IOException`; using them outside exception cleanup can hide primary failures or resource leaks.
- `ObjectWritable` class-name based deserialization can fail if classes are absent, renamed, not public, or not registered with a factory. Compact array encoding is explicitly unsafe for long-lived persisted files shared with older clusters.
- `Writable` object reuse makes stale state a common bug if `readFields` does not fully overwrite collections, buffers, or optional fields.
- Raw comparators must agree with object comparators. Divergence can corrupt sort order in MapReduce shuffle, SequenceFile sorting, MapFile indexes, or TFile binary searches.
- `Text` uses byte offsets, not Java character indexes. Invalid UTF-8, trailing bytes, `getBytes()` capacity exposure, and `clear()` retaining memory are common correctness and memory-footprint traps.
- `SequenceFile` and `MapFile` depend on stable binary encodings, class names, sync markers, and sorted-key assumptions. Appending out-of-order keys or changing compression metadata can make files unreadable or indexes incorrect.
- `MapFile` index files are loaded entirely into memory; high-cardinality files with large keys or small index intervals can create memory pressure.
- Compression state machines require careful buffer ownership. The docs warn that input buffers must remain unmodified until `needsInput()` says more input is needed. Violating that can corrupt native and non-native decompression/compression.
- Codec pooling can leak native resources or corrupt future operations if compressors/decompressors are returned while still in use, not reset, or mixed with incompatible configurations.
- BZip2 behavior depends on native versus pure-Java mode. Splittability is only available in pure-Java mode, while compressor/decompressor object methods may throw `UnsupportedOperationException` in that same mode.
- Split compression offsets are advisory. Codecs may change start/end to align with block boundaries, so callers must use adjusted offsets for progress and split accounting.
- TFile keys are limited to 64 KB while values are practically storage-limited. Comparator names, compression algorithm availability, and metadata block uniqueness need validation.
- Old metrics and Ganglia APIs are deprecated. They still represent compatibility surface, but new integration should use `metrics2`. UDP Ganglia emission can drop data, and timer/updater concurrency can expose stale or partially updated records if implementations are careless.

## Test Signals

- API compatibility tests should verify all public/protected signatures, inheritance, implemented interfaces, checked exceptions, fields, constants, and deprecation text for this chunk against the Hadoop Common 2.8.0 baseline.
- Writable tests should round-trip `LongWritable`, `ShortWritable`, `VIntWritable`, `VLongWritable`, `NullWritable`, `Text`, `MapWritable`, `SortedMapWritable`, `TwoDArrayWritable`, `VersionedWritable`, `MD5Hash`, and `ObjectWritable`, including reused-instance `readFields` cases.
- Variable-length encoding tests should cover `WritableUtils.writeVInt/writeVLong/readVInt/readVLong`, sign and length decoding, boundary values, range-checked reads, malformed lengths, and `readStringSafely` maximum-size rejection.
- Comparator tests should compare object-level and raw-byte ordering for primitive writables, `Text`, MD5 hashes, TFile raw comparables, and custom comparators registered through `WritableComparator.define`.
- `Text` tests should cover UTF-8 validation, malformed encode/decode with replace true/false, byte-position `find`, `charAt` on valid and trailing bytes, max-length reads/writes, `copyBytes` versus `getBytes`, `clear` memory behavior, and `bytesToCodePoint` buffer-position mutation.
- `ObjectWritable` tests should cover primitives, strings, arrays, `Writable` classes, nulls, configured class loading, non-public writable factory registration, compact-array on/off compatibility, and missing-class failures.
- SequenceFile tests should create and read uncompressed, record-compressed, and block-compressed files; assert header metadata, sync markers, key/value class handling, deprecated and options-based writer paths, raw output writers, FileContext create flags, and codec selection.
- MapFile/SetFile tests should cover sorted insertion assumptions, index loading, rename/delete, corrupt index repair with dry-run and mutation paths, and behavior with large keys or dense indexes.
- IOUtils tests should cover full reads/skips across short-returning streams, EOF failures, short channel writes, positional file-channel writes, compressed-data read error wrapping, cleanup ignoring exceptions, and directory-listing IO failures.
- Compression tests should cover codec discovery by extension/name/class, codec suffix removal, stream finish/reset/close, compressor/decompressor state transitions, dictionary paths, concatenated streams through `finished` plus `getRemaining`, `CodecPool` lease counts, direct decompression, and resource release.
- BZip2 tests should explicitly cover native and pure-Java modes, unsupported compressor/decompressor methods in pure-Java mode, split input streams, adjusted start/end offsets, and continuous versus block read modes.
- TFile tests should cover supported compression names, comparator construction for `memcmp` and Java-class comparators, metadata block duplicate/missing exceptions, sorted and unsorted reads, key-size limits, offset/key seeks, and lower/upper bound helpers.
- Serialization-provider tests should verify Java, writable, and Avro serialization selection through configuration, including Avro schema and reflect-package keys.
- Metrics tests should cover old metrics context initialization, period parsing, updater registration/removal, record creation constraints, update/remove row matching by tags, start/stop/close idempotence, Ganglia units/slope/tmax/dmax configuration, UDP datagram encoding, and `EventCounter` appender counting.

## Cross-Chunk Notes

The preceding chunk is needed for the beginning of `IOUtils` and possibly package-level context before line 17995. The following chunk is needed for the remainder of `MetricsRecordImpl`, including the rest of metric mutation, update/remove behavior, and any subsequent SPI classes.

This document is intentionally chunk-scoped. The final per-file research document should merge this with the other chunks for `Apache_Hadoop_Common_2.8.0.xml` before drawing conclusions about the complete JDiff baseline.
