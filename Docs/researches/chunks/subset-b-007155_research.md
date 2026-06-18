# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 23752-30010

## Scope

This chunk is a JDiff API descriptor slice for Hadoop Common 2.6.0. It starts inside `org.apache.hadoop.io.SequenceFile.Sorter`, covers the tail of the `org.apache.hadoop.io` package, then covers the complete visible `org.apache.hadoop.io.compress` package and the beginning of `org.apache.hadoop.io.file.tfile` through the early `Utils.Version` API. The XML is generated API metadata, not executable implementation, but it records public constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, synchronization flags, visibility, and deprecation notes consumed by compatibility tooling.

The visible package areas are:

- `org.apache.hadoop.io`: `SequenceFile` sorter/writer support, `SetFile`, primitive and collection `Writable` types, UTF-8 `Text`, writable serialization/comparison contracts, writable factories, and `WritableUtils`.
- `org.apache.hadoop.io.compress`: block/stream compression wrappers, codec contracts and discovery, compressor/decompressor pooling, direct decompression, native codec facades for bzip2/gzip/lz4/snappy/deflate, and splittable compression support.
- `org.apache.hadoop.io.file.tfile`: TFile exceptions, raw comparable byte ranges, TFile reader/scanner/writer APIs, TFile utility encoding/search helpers, and the start of version metadata.

## Purpose

The chunk preserves the public compatibility contract for Hadoop's binary I/O layer. The `org.apache.hadoop.io` portion documents the serialization primitives used by MapReduce keys and values, sequence-file storage, map/set files, byte-level comparators, and utility encodings. The compression package documents the common abstraction that lets higher layers choose codecs by file extension, configuration, or service discovery and then stream compressed or decompressed data through Hadoop filesystem and data-processing paths. The TFile portion documents a block-compressed key/value container with sorted-key, scanner, byte-range, record-number, metadata-block, and raw-byte access APIs.

Because this is a JDiff descriptor, its main runtime role is indirect: API compatibility checks compare this XML against other Hadoop releases. As a source-research artifact, it also gives a dense source-tree-aligned map of externally visible classes that downstream projects may compile against or load reflectively.

## Important APIs, Types, and Functions

### SequenceFile, SetFile, and writable contracts

- `SequenceFile.Sorter.RawKeyValueIterator` exposes raw sorted sequence-file iteration: `next()`, `getKey()` as `DataOutputBuffer`, `getValue()` as `SequenceFile.ValueBytes`, `getProgress()`, and `close()`.
- `SequenceFile.Sorter.SegmentDescriptor` describes merge-sort segments by file path, offset, and length. It supports sync checks, preservation policy, raw key/value reads, stored-key access, comparison/equality/hash behavior, and cleanup that closes and deletes intermediate files unless preservation is requested.
- `SequenceFile.ValueBytes` provides raw sequence-file value access through `writeUncompressedBytes`, `writeCompressedBytes`, and `getSize`.
- `SequenceFile.Writer` is a `Closeable` and `Syncable` writer for sequence-format files. Deprecated constructors remain visible, while the preferred option-based path exposes static `Writer.Option` factories for file, stream, buffer size, replication, block size, progress callback, key/value classes, metadata, compression type, and compression codec. It also exposes key/value class introspection, codec introspection, `sync`, deprecated `syncFs`, `hsync`, `hflush`, synchronized close/append/raw-append, current synchronized file length, and protected serializers for key and compressed/uncompressed values.
- `SetFile` extends `MapFile` as a file-backed set of keys. `SetFile.Reader` can seek, iterate, and fetch matching keys; `SetFile.Writer` appends strictly increasing `WritableComparable` keys and supports compression-aware constructors.
- `Writable` and `WritableComparable` define Hadoop's core serialization and comparable-key contracts. `Writable` requires `write(DataOutput)` and `readFields(DataInput)`; `WritableComparable` combines that contract with `Comparable` and documents the need for stable cross-JVM `hashCode` behavior.

### Primitive, text, and collection writables

- `ShortWritable`, `VIntWritable`, and `VLongWritable` are mutable `WritableComparable` wrappers around short, variable-length int, and variable-length long values. They expose constructors, `set`, `get`, `readFields`, `write`, equality/hash/compare, and string conversion.
- `ShortWritable.Comparator`, `Text.Comparator`, and `UTF8.Comparator` are byte-level `WritableComparator` optimizations for serialized key comparisons.
- `SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap` over `WritableComparable` keys and `Writable` values. It exposes sorted-map views, mutation/access methods, copy construction, and `Writable` serialization.
- `TwoDArrayWritable` serializes a two-dimensional matrix of a specified `Writable` class, with constructors, `set`, `get`, `toArray`, `readFields`, and `write`.
- `Text` stores UTF-8 bytes as a `BinaryComparable` and `WritableComparable`. It exposes constructors from string, another `Text`, or byte array; raw/copy byte access; byte length; byte-position `charAt`; UTF-8 substring search; setting/appending/clearing; stream serialization with optional maximum length; `skip`; `readWithKnownLength`; static string read/write helpers; UTF-8 encode/decode with replacement controls; UTF-8 validation; code-point extraction; `utf8Length`; and `DEFAULT_MAX_LEN`.
- `Stringifier<T>` is a closeable adapter for converting objects to and from string representations, with `IOException` on conversion failures.
- `VersionedWritable` writes and checks an implementation version byte around subclass fields; `VersionMismatchException` captures mismatched expected/current versions.

### Writable comparison, instantiation, and encoding utilities

- `WritableComparator` implements `RawComparator` and `Configurable`. It provides protected constructors for comparator subclasses, static comparator lookup/registration, object comparison, raw byte comparison, instance creation, configuration access, hash helpers, lexicographic byte comparison, and static parsers for primitive values and vint/vlong values from byte arrays.
- `WritableFactories` lets callers register a `WritableFactory` per class and create writable instances with or without `Configuration`; this supports non-public writable construction for `ObjectWritable`.
- `WritableFactory` is the single-method factory contract returning a new `Writable`.
- `WritableUtils` provides compressed byte-array/string/string-array read/write helpers, cloning via serialization, deprecated `cloneInto`, zero-compressed vint/vlong read/write, range-checked vint reading, first-byte sign/size decoding, encoded-size calculation, enum string serialization, full skipping, writable-array byte conversion, and length-bounded `readStringSafely`.

### Compression contracts and stream wrappers

- `CompressionCodec` is the central codec contract. Implementations create compression output streams and decompression input streams with or without caller-supplied `Compressor`/`Decompressor` instances, report compressor/decompressor classes, allocate new compressor/decompressor instances, and return default filename extensions.
- `CompressionInputStream` and `CompressionOutputStream` wrap input/output streams and define decompressed reads, compressed writes, reset-state behavior, current stream position, and finish/reset semantics. Mark/reset are explicitly unsupported for compression input streams in this API surface.
- `Compressor` and `Decompressor` define streaming state-machine contracts: set input and optional dictionaries, test input needs and dictionary needs, track byte counters, finish/end, compress/decompress into caller buffers, report remaining compressed input, reset, close/end, and for compressors `reinit(Configuration)`.
- `CompressorStream` and `DecompressorStream` adapt those state-machine contracts to Java streams and expose `setInputStream` for subclasses that need to swap the underlying stream.
- `BlockCompressorStream` and `BlockDecompressorStream` implement block-oriented framing over compressor/decompressor streams. Blocks contain an uncompressed length followed by one or more length-prefixed compressed data chunks; decompression can load compressed block data and reset state.

### Codec discovery, pooling, and concrete codecs

- `CodecPool` is a global reusable compressor/decompressor pool. It leases by codec, can reinitialize compressors with `Configuration`, returns instances to the pool, and reports leased compressor/decompressor counts.
- `CompressionCodecFactory` discovers codecs from the `io.compression.codecs` configuration value and Java `ServiceLoader`, stores codec classes back into configuration, resolves codecs by path extension, class name, codec name, or `Class`, removes suffixes, and exposes diagnostic extension-map and `main` helpers.
- `BZip2Codec` implements `Configurable` and `SplittableCompressionCodec`. It can use native bzip2 when available or a pure-Java implementation, but pure-Java mode does not implement compressor/decompressor object APIs. Split input streams force the pure-Java path and align reads at bzip2 block boundaries. Its default extension is `.bz2`.
- `DefaultCodec` implements the zlib/default codec path and `DirectDecompressionCodec`; `DeflateCodec` is an alias for discovery by deflate name.
- `GzipCodec` creates gzip compression/decompression streams. `GzipCodec.GzipOutputStream` bridges `DeflaterOutputStream` to Hadoop's `CompressionOutputStream` contract and exposes a protected `out` stream replacement hook.
- `Lz4Codec` and `SnappyCodec` implement `Configurable` and `CompressionCodec`; Snappy also implements `DirectDecompressionCodec`. Both expose native-code loaded/library-name checks, stream creation, compressor/decompressor allocation, and default extensions (`.lz4`, `.snappy`).
- `DirectDecompressionCodec` and `DirectDecompressor` cover ByteBuffer-based decompression. `DoNotPool` is a marker annotation for compressor/decompressor implementations that must not be pooled.
- `SplitCompressionInputStream`, `SplittableCompressionCodec`, and `SplittableCompressionCodec.READ_MODE` define split-aware compressed reads where requested start/end offsets may be adjusted to codec block boundaries. `READ_MODE` distinguishes continuous reads from blocked reads that signal end-of-block behavior.

### TFile container APIs

- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are `IOException` subclasses for named metadata-block creation and lookup failures.
- `RawComparable` describes a byte-array slice through `buffer()`, `offset()`, and `size()` so callers can compare keys without copying.
- `TFile` publishes compression names (`none`, `lzo`, `gz`), comparator names/prefixes (`memcmp`, `jclass:`), comparator construction through `makeComparator`, supported compression algorithm discovery, and a `main` information-dump entry point. Its documentation defines TFile as a typed-less byte key/value container with 64KB keys, block compression, named metadata blocks, sorted or unsorted keys, key/file-offset seeking, and configurable chunk/input/output buffer sizes.
- `TFile.Reader` wraps an `FSDataInputStream` plus known file length. It can close idempotently, report sorted state/comparator name/entry count, fetch first and last keys, return raw and entry comparators, open metadata-block streams, map file offsets to nearby record numbers or sample keys, and create scanners over full files, byte ranges, key ranges, or record-number ranges. Deprecated key-range scanner overloads remain visible beside `createScannerByKey`.
- `TFile.Reader.Scanner` is a closeable cursor over a reader range. It supports construction by record range or key range, exact seek, rewind, seek-to-end, lower/upper bound positioning, advance, end detection, current entry access, close, and current record-number lookup.
- `TFile.Reader.Scanner.Entry` models the current key/value entry. It exposes key/value length inspection, whole entry retrieval into `BytesWritable`, key/value copying to `BytesWritable`, `OutputStream`, or byte arrays, stream access for key/value data, known-value-length detection, key comparison against byte arrays or `RawComparable`, equality, and hash code.
- `TFile.Writer` wraps an `FSDataOutputStream` positioned at zero and writes block-compressed key/value entries. It supports direct byte-array append, offset/length append, streaming key append, streaming value append, and named metadata-block creation with explicit or default compression. Closing releases writer resources but intentionally does not close the underlying `FSDataOutputStream`.
- `org.apache.hadoop.io.file.tfile.Utils` provides TFile-specific variable-length integer/string encoding, decoding, and lower/upper-bound binary search helpers over lists with explicit or natural comparators.
- `Utils.Version` begins in this chunk with constructors from `DataInput` or explicit major/minor shorts, `write(DataOutput)`, major/minor accessors, and serialized size reporting.

## Control Flow

SequenceFile sorting and writing flow is staged around raw records. Sorter merge methods produce a `RawKeyValueIterator`; callers repeatedly call `next()`, then fetch a raw key and `ValueBytes`, and finally pass those records into `SequenceFile.Writer.writeFile` or append them with `appendRaw`. Segment descriptors supply per-segment raw reads and cleanup, including optional input preservation for merge intermediates. Writers are configured either through deprecated constructors or option builders, then append object or raw records, emit sync points, flush/sync the filesystem stream, report synchronized positions, and close.

Writable flow is serializer-driven. Callers write fields to `DataOutput` and reconstruct into existing instances with `readFields(DataInput)`. Comparators may instantiate writable objects and compare natural order, or bypass object creation by comparing serialized byte ranges. `WritableUtils`, `WritableComparator`, `Text`, and the variable-length writable classes provide the shared wire encodings that make these contracts compact and comparable in MapReduce shuffle, sequence files, map files, and RPC/storage paths.

Compression flow is codec-mediated. A caller resolves a `CompressionCodec` directly, through `CompressionCodecFactory`, or by path extension; leases or creates compressor/decompressor instances through the codec or `CodecPool`; wraps the underlying stream in a compression input/output stream; feeds data through compressor/decompressor state transitions; finishes or resets as needed; and returns reusable codec state to the pool. Block streams add a framing layer around stream compressors. Splittable codecs adjust requested compressed offsets and expose adjusted ranges so parallel readers can start at viable block boundaries.

TFile write flow starts with a zero-position `FSDataOutputStream`, minimum block size, compression name, optional comparator name, and configuration. Callers append full byte-array entries or open a key stream followed by a value stream. Once metadata blocks are created, no more key/value insertion is allowed. Closing finalizes container state and internal resources while leaving the filesystem stream open for the caller. TFile read flow opens with a known file length, loads index metadata, then creates scanners by full range, byte range, key range, or record-number range. A scanner positions with seeks/bounds, yields entries, advances, and closes. Entry methods then copy or stream the current key/value data.

## State and Persistence Behavior

This chunk is API metadata, but the described APIs imply several persistent wire formats. `Writable`, `Text`, `VIntWritable`, `VLongWritable`, `WritableUtils`, `VersionedWritable`, `SequenceFile.Writer`, `SetFile`, and TFile all define serialized forms that must remain readable across releases. The public JDiff signatures are therefore compatibility-sensitive even when implementation details are not present in the XML.

`SequenceFile.Writer` persists key/value class names, optional metadata, compression mode/codec, sync markers, and serialized records to a filesystem path or `FSDataOutputStream`. Its protected serializers show that object writes pass through Hadoop serializer implementations, while raw append preserves already serialized key/value bytes. `getLength()` returns a safe synchronized position, not necessarily the exact last appended key under block compression.

`SetFile` persists sorted keys as a `MapFile` variant and requires strictly increasing appended keys. Reader state is cursor-like and stream-backed.

Writable objects hold in-memory mutable primitive, text, array, or map state and serialize through `DataInput`/`DataOutput`. `Text.clear()` resets logical length without clearing the underlying byte array, so retained buffer capacity can persist in memory after logical clearing. `SortedMapWritable` persists class metadata inherited from `AbstractMapWritable` plus sorted key/value entries. `WritableFactories` and `WritableComparator` maintain process-global factory/comparator registries.

Compression state is mostly stream-local or pool-global. Compressors and decompressors carry mutable native or Java codec state until `reset`, `reinit`, `finish`, `end`, or `close`. `CodecPool` tracks leased and returned instances globally and must not pool implementations annotated with `DoNotPool`. `CompressionCodecFactory` stores configured codec class names in `Configuration` and uses extension maps for lookup.

TFile persists a block-compressed key/value container with data-block indexes, meta-block indexes, comparator metadata, version metadata, compression names, chunked values, and optional named metadata blocks. Reader/scanner/entry objects are stateful cursors over a shared `FSDataInputStream`; the TFile documentation notes that multiple scanners over the same reader serialize actual I/O because the implementation relies on `seek()+read()`. Writer exceptions during append can leave the TFile inconsistent; the documented only legitimate next call is `close()`.

## Dependencies and Integration Points

- The `org.apache.hadoop.io` APIs depend on `java.io` streams, `DataInput`, `DataOutput`, `Closeable`, Java collections, `java.nio.ByteBuffer`, `java.nio.charset` exceptions, Hadoop `Configuration`/`Configurable`, filesystem types (`FileSystem`, `Path`, `FSDataOutputStream`, `Syncable`), `Progressable`, and serializer classes.
- SequenceFile and SetFile integrate with Hadoop storage abstractions, compression codecs, progress reporting, raw comparators, and writable key/value types used by MapReduce and filesystem-backed data structures.
- `Text`, `WritableUtils`, and `WritableComparator` are cross-cutting dependencies for serialization, RPC, shuffle/sort, configuration string handling, token/service text fields, and compatibility-sensitive binary encodings.
- Compression APIs integrate with `Configuration`, `Path`, Java `ServiceLoader`, native compression libraries, Java deflater streams, direct `ByteBuffer` decompression, Hadoop split processing, and filesystem input/output streams.
- Concrete codecs are integration points for optional native libraries. BZip2 additionally integrates with pure-Java fallback behavior and split-aware processing; Snappy and LZ4 expose native availability checks.
- TFile integrates with `FSDataInputStream`, `FSDataOutputStream`, `Configuration`, `BytesWritable`, `RawComparator`, `WritableComparator`, `JavaSerializationComparator`, compression algorithms, byte-range scanning, record-number indexing, and named metadata blocks.

## Risks and Edge Cases

- The chunk starts in the middle of `SequenceFile.Sorter` and ends in the middle of `Utils.Version`. Merge tooling must combine adjacent chunks before making final per-file claims about complete class surfaces.
- Many APIs describe persistent binary formats. Changes to `WritableUtils` vint/vlong sign handling, byte order, size calculation, `Text` UTF-8 length encoding, `VersionedWritable` version checks, SequenceFile framing, or TFile encodings can corrupt stored data or break old clients.
- `SequenceFile.Writer` has deprecated constructors and deprecated `syncFs`, but they remain public compatibility obligations in Hadoop 2.6.0. Downstream code may still compile against them.
- Raw append and raw iterator APIs assume key/value bytes match declared classes and compression state. Incorrect lengths, offsets, or `ValueBytes` compressed/uncompressed handling can produce unreadable SequenceFiles.
- `SetFile.Writer.append` requires strictly increasing keys. Violating comparator order can create files that later readers search incorrectly.
- `Text.getBytes()` exposes an oversized backing array where only `getLength()` bytes are valid; callers that persist or compare the full array risk data leakage or incorrect comparisons. `clear()` also intentionally retains allocated memory.
- `WritableComparable.hashCode()` must be stable across JVMs for partitioning. Implementations with identity-based or randomized hashes can break MapReduce partitioning.
- Global registries in `WritableFactories`, `WritableComparator`, `CodecPool`, and codec discovery can make tests order-dependent if they do not isolate configuration and registered classes.
- Codec pooling is sensitive to lifecycle. Returning closed, unreinitialized, or `DoNotPool` compressor/decompressor instances can cause native crashes, data corruption, or subtle cross-stream contamination.
- Native-code codec availability is environmental. BZip2, LZ4, and Snappy behavior may vary between native and pure-Java/unavailable modes; split bzip2 intentionally uses pure-Java behavior regardless of the configured native preference.
- Compression input mark/reset are unsupported; callers expecting normal `InputStream` mark semantics will fail.
- Splittable compression offsets may be adjusted by the codec. Callers must use `getAdjustedStart()` and `getAdjustedEnd()` rather than assuming requested split boundaries.
- TFile keys are limited to 64KB while values are chunked and practically disk-limited. Unknown value lengths, chunk-size configuration, and stream-based append close ordering are important edge cases.
- TFile writer state becomes inconsistent after append I/O exceptions, and metadata-block creation forbids further key/value insertion. Recovery paths should close and discard rather than continue writing.
- TFile scanner I/O is not truly multi-threaded over one reader because shared `FSDataInputStream` seeking serializes concurrent access.

## Test Signals

- API compatibility tests should verify every public class, interface, constructor, method, field, checked exception, implemented interface, deprecation flag, synchronization flag, and visibility marker in this chunk against the intended Hadoop Common 2.6.0 baseline.
- Writable tests should round-trip `ShortWritable`, `VIntWritable`, `VLongWritable`, `TwoDArrayWritable`, `SortedMapWritable`, `VersionedWritable` subclasses, and `Text` through `DataInput`/`DataOutput`, including equality/hash/compare behavior.
- Encoding tests should cover positive and negative vint/vlong boundaries, byte-array and stream decoders, `readVIntInRange`, enum serialization, compressed string/byte-array helpers, `skipFully`, `readStringSafely`, and `Text` maximum-length enforcement.
- UTF-8 tests should cover valid and malformed byte sequences, replacement versus exception decode behavior, byte-position `charAt`, `find` without string conversion, code-point extraction, `utf8Length`, `copyBytes` versus `getBytes`, and `clear()` buffer retention.
- Comparator tests should compare object-level and raw byte-level ordering for writable primitives and `Text`, verify registered comparator lookup, and exercise byte parsers for int/long/float/double/vint/vlong.
- SequenceFile tests should write and read object and raw key/value records under no, record, and block compression; verify sync/hsync/hflush behavior; check `getLength()` as a seekable synchronized position; test sorter merge flows and segment cleanup/preserve behavior.
- SetFile tests should enforce sorted append order, seek existing and missing keys, iterate to EOF, and validate comparator-aware reader/writer constructors.
- Compression tests should verify codec factory lookup by extension/name/class/configuration and service-loaded codecs, suffix removal, codec class configuration, stream compression/decompression round trips, finish/reset behavior, mark/reset unsupported behavior, and `CompressionInputStream.getPos()`.
- CodecPool tests should cover lease/return counts, compressor reinitialization with configuration, decompressor reuse, null handling, and non-pooling behavior for `DoNotPool` implementations.
- Native codec tests should branch on environment for bzip2/lz4/snappy availability, library-name reporting, direct decompressor creation, and pure-Java bzip2 split reading.
- Splittable compression tests should verify adjusted split boundaries, continuous versus blocked read modes, and parallel split consumption for bzip2-like block codecs.
- TFile tests should write/read sorted and unsorted files with `none`, `lzo`, and `gz` where available; verify comparator construction (`memcmp` and `jclass:`); scan by full file, byte range, key range, and record-number range; exercise lower/upper bound and seek-to-end behavior; read keys/values through byte arrays, `BytesWritable`, and streams; and check known versus unknown value lengths.
- TFile metadata tests should create, duplicate, read, and miss named meta blocks, verify `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist`, and confirm no key/value appends are accepted after meta-block creation.
- TFile durability tests should validate close idempotence, underlying `FSDataOutputStream` ownership, file-length constructor requirements, version serialization, and behavior after append I/O exceptions.
