# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.4.xml lines 18158-24453

## Scope And Purpose

This chunk is a JDiff public API slice for Hadoop Common 3.2.4. It is not runtime implementation code; it is an XML description of exported Java packages, classes, interfaces, fields, method signatures, deprecation status, exceptions, and embedded Javadocs. The covered range starts in the tail of `org.apache.hadoop.io.DefaultStringifier`, spans most of the public `org.apache.hadoop.io` serialization and file-container API surface, covers `org.apache.hadoop.io.compress`, includes `org.apache.hadoop.io.erasurecode.ECSchema`, and begins the `org.apache.hadoop.io.file.tfile` APIs through the start of `Utils.upperBound`.

The main purpose of this slice is API compatibility documentation. Downstream checks can compare these signatures and docs against other Hadoop versions to detect binary/source compatibility changes in writable serialization, SequenceFile/MapFile/TFile containers, compression codec plumbing, and erasure-coding schema configuration.

## API Surface Covered

The chunk covers these package regions:

- `org.apache.hadoop.io`: `DefaultStringifier` tail, primitive writable wrappers, map and sorted-map writables, object and generic writables, raw comparators, sequence/map/set files, UTF-8 `Text`, versioned writable support, writable factories, and writable utility methods.
- `org.apache.hadoop.io.compress`: block and stream compressor/decompressor streams, concrete codecs for bzip2/default/gzip, codec constants, codec discovery and pooling, compression/decompression interfaces, direct decompression interfaces, and splittable compression contracts.
- `org.apache.hadoop.io.erasurecode`: immutable public `ECSchema` configuration holder.
- Empty package markers for `org.apache.hadoop.io.erasurecode.coder.util` and `org.apache.hadoop.io.erasurecode.grouper`.
- `org.apache.hadoop.io.file.tfile`: TFile metadata exceptions, raw byte-range comparison interface, top-level `TFile` constants and helpers, and `Utils` variable-length integer/string helpers. The chunk stops inside the `upperBound` method declaration, so the remainder of that method and following TFile utility APIs are cross-chunk dependencies.

## Important Types And APIs

The writable primitive wrappers `DoubleWritable`, `FloatWritable`, `IntWritable`, `LongWritable`, `ShortWritable`, `VIntWritable`, and `VLongWritable` expose the standard Hadoop `WritableComparable` pattern: default and value constructors, `set`, `get`, `readFields(DataInput)`, `write(DataOutput)`, equality, hash code, comparison, and `toString`. Fixed-width wrappers serialize Java primitive values directly, while `VIntWritable` and `VLongWritable` use Hadoop variable-length integer encoding to reduce storage for small values.

`DefaultStringifier<T>` bridges Hadoop `Serialization` to string form using base64-encoded serialized object bytes. Its static helpers store/load single objects and arrays in `Configuration` keys. Empty arrays are explicitly risky because `storeArray` documents `IndexOutOfBoundsException` when the array is empty.

`ElasticByteBufferPool` is a synchronized `ByteBufferPool` implementation that returns either direct or heap buffers and caches released buffers. Its documented policy is simple and unbounded: return the smallest cached buffer with at least the requested capacity and do not enforce a maximum cache size.

`EnumSetWritable<E>` wraps nullable or empty `EnumSet`s while preserving element type when required. It implements both `Writable` and `Configurable`; constructors and `set` require a non-null `elementType` when the value is null or empty. This makes type metadata part of the serialized state contract.

`GenericWritable` is an abstract configurable polymorphic wrapper for a bounded set of writable implementation classes. Subclasses must return a constant `Class[]` from `getTypes()`. `ObjectWritable` is a broader polymorphic wrapper that writes an instance with its class name and supports arrays, strings, primitives, and regular `Writable`s. `WritableFactories` and `WritableFactory` let non-public writable classes be constructed by factory rather than public zero-argument constructor, which matters for `ObjectWritable` deserialization.

`MapWritable` and `SortedMapWritable` adapt Java `Map` and `SortedMap` APIs to writable key/value serialization through `AbstractMapWritable`. Both expose collection views and standard mutation methods plus `readFields`/`write`. `SortedMapWritable` adds `comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, and `tailMap`.

`NullWritable` is a singleton writable comparable for empty keys or values. Its `readFields` and `write` are intentionally no-op, while `get()` returns the singleton instance.

`MD5Hash` is a 16-byte writable comparable digest value. It supports construction from hex string or byte array, static digest helpers for byte arrays, byte-array slices, byte-array arrays, strings, `UTF8`, and `InputStream`, thread-local `MessageDigest` creation, half and quarter digest projections, binary serialization, and hex parsing through `setDigest`.

`MultipleIOException` aggregates multiple `IOException`s and provides `createIOException(List)`, allowing cleanup or batch operations to surface several failures as one checked exception.

`Writable` and `WritableComparable` define the core serialization contract. `Writable.readFields` emphasizes storage reuse on deserialization, and `WritableComparable` documents the distributed-systems requirement that `hashCode()` be stable across JVM instances because Hadoop uses it for key partitioning.

`RawComparator<T>` compares serialized byte slices directly. `WritableComparator` implements the default object-based and byte-slice comparison path, allows registration of thread-safe optimized comparators via `define`, creates key instances, and exposes byte parsing helpers such as `compareBytes`, `hashBytes`, `readInt`, `readLong`, `readDouble`, `readVLong`, and `readVInt`.

`WritableUtils` groups serialization helpers: compressed byte arrays/strings/string arrays, plain string arrays, byte-array display, writable clone/cloneInto, zero-compressed `writeVInt`/`writeVLong` and `readVInt`/`readVLong`, range-checked VInt reads, VInt sign/size helpers, enum read/write as string, fully skipping a `DataInput`, conversion of writables to a byte array, and `readStringSafely` with maximum encoded-size validation.

`IOUtils` exposes stream and file utility methods: several `copyBytes` overloads, compressed-data read wrapper, `readFully`, `skipFully`, cleanup/close helpers, socket close, channel write loops, directory listing that preserves IO errors, file/channel `fsync`, exception wrapping with path and method diagnostics, and `readFullyToByteArray`. The older `cleanup(Log, Closeable...)` overload is deprecated in favor of SLF4J `cleanupWithLogger`.

`MapFile`, `SetFile`, and `SequenceFile` are file-container APIs. `MapFile` is a directory with `data` and `index` files and exposes `rename`, `delete`, and index repair through `fix`. `SetFile` is a key-only specialization of `MapFile`. `SequenceFile` documents binary key/value flat files with uncompressed, record-compressed, and block-compressed formats, a common header, sync markers, metadata, compression codec selection, default compression type helpers, many legacy `createWriter` overloads, a modern `createWriter(Configuration, Writer.Option...)`, and `SYNC_INTERVAL`.

`Text` is Hadoop's mutable UTF-8 byte sequence. It supports raw byte access, exact byte copying, byte length, scalar-codepoint traversal without creating a `String`, substring search, multiple setters from string/text/byte ranges, append, clear, bounded and unbounded deserialization/serialization, UTF-8 encode/decode helpers with optional replacement, static read/write string helpers with maximum-length variants, UTF-8 validation, codepoint extraction from `ByteBuffer`, and encoded-length computation.

`TwoDArrayWritable` serializes a matrix of writable instances for a configured element class. `VersionedWritable` prefixes writable data with a version byte and throws `VersionMismatchException` when input version does not match `getVersion()`, giving evolving writable classes an explicit compatibility hook.

## Compression APIs And Integration

The compression package defines a layered streaming model:

- `CompressionCodec` creates compression/decompression streams, compressor/decompressor instances, advertises required implementation classes, and returns the default extension.
- `Compressor` and `Decompressor` are state-machine interfaces modeled after `Deflater` and `Inflater`. They use `setInput`, `needsInput`, optional dictionaries, byte counters or remaining-byte reporting, finish/finished/reset/end, and `compress` or `decompress` calls.
- `CompressionOutputStream` and `CompressionInputStream` are abstract stream wrappers. Output streams must implement `write(byte[], int, int)`, `finish`, and `resetState`; input streams expose reset-state behavior and position/seek-related methods.
- `CompressorStream`, `BlockCompressorStream`, `DecompressorStream`, and `BlockDecompressorStream` provide stream wrappers around those state machines. Block streams write or read length-prefixed compressed blocks and are intended for block-oriented algorithms.
- `DirectDecompressionCodec` and `DirectDecompressor` add direct `ByteBuffer` decompression for codecs that can bypass heap-copy flows.
- `SplittableCompressionCodec` and `SplitCompressionInputStream` define compressed-input range reading. Codecs may adjust requested start/end offsets to block boundaries, which is central to parallel processing of compressed Hadoop inputs.

Concrete/public codec entries in this range include `BZip2Codec`, `DefaultCodec`, and `GzipCodec`. `BZip2Codec` is configurable and splittable; its docs state that it can use a native bzip2 library or a pure-Java implementation, that pure-Java mode does not implement `Compressor`/`Decompressor` methods with explicit compressor/decompressor arguments, and that splittability is available only in pure-Java mode. `DefaultCodec` implements direct decompression in addition to normal codec creation, and `GzipCodec` specializes default behavior for gzip.

`CodecConstants` lists standard filename extensions for default, bzip2, gzip, LZ4, Snappy, and Zstandard codecs. `CodecPool` is a global pool for reusing possibly native compressor/decompressor instances and exposes leased-instance counts. `CompressionCodecFactory` discovers codecs through `io.compression.codecs` and Java `ServiceLoader`, resolves codecs by file suffix, class name, or case-insensitive alias, removes suffixes, and has a diagnostic `main`.

## TFile And Erasure Coding APIs

`ECSchema` is a final serializable value object for erasure coding schema data. It can be built from a full options map or from codec name, data unit count, parity unit count, and optional extra options. Public constants identify the option keys for codec name, number of data units, and number of parity units. Equality, hash code, and string output are part of the public surface, so schema identity and logging representations are compatibility-sensitive.

`MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are checked TFile metadata exceptions. `RawComparable` describes a byte array, offset, and size triple used with external raw comparators. The docs explicitly put semantic compatibility responsibility on applications: two raw comparables must be compared with a comparator that understands both byte ranges.

`TFile` is a byte-oriented key/value container. It supports type-less keys and values, 64 KB key limit, unrestricted value length in practice, block compression, named metadata blocks, sorted or unsorted keys, and seeking by key or file offset. Public constants name compression algorithms (`gz`, `lzo`, `none`) and comparator naming conventions (`memcmp`, Java class comparator prefix). `makeComparator` builds raw comparators from names, `getSupportedCompressionAlgorithms` returns accepted compression algorithm names, and `main` dumps TFile information.

TFile's embedded docs are unusually operational. They document memory footprint from per-block codecs, temporary key/value buffering, data-block index cost as `(56 + AvgKeySize) * NumBlocks`, and metadata-block index cost as `(40 + AvgMetaBlockName) * NumMetaBlock`. Configuration knobs include `tfile.io.chunk.size`, `tfile.fs.output.buffer.size`, and `tfile.fs.input.buffer.size`. Performance guidance weighs block size, sequential versus random reads, compression ratios, gzip CPU cost relative to LZO, and the lack of true multithreaded reading when scanners share one `FSDataInputStream`.

`org.apache.hadoop.io.file.tfile.Utils` in this chunk exposes TFile-specific variable-length integer/string helpers. Its `writeVInt` delegates conceptually to `writeVLong`; `writeVLong` documents a different encoding family from `WritableUtils`, using first-byte ranges for 1 to 9 byte signed encodings. `readVInt`, `readVLong`, `writeString`, `readString`, and `lowerBound` are fully visible. The chunk ends at the `upperBound` declaration before its parameters and docs are complete.

## Control Flow And Data Flow

The XML itself has no executable control flow beyond the sequence of JDiff declarations. The documented runtime flows are these:

- Writable serialization is symmetrical: constructors or factory-created instances are populated by `readFields(DataInput)` after data was produced by `write(DataOutput)`. Mutable implementations are expected to reuse storage on reads where possible.
- Polymorphic serialization flows through `GenericWritable` type tables, `ObjectWritable` class-name records, and `WritableFactories` for non-public classes. Deserialization therefore depends on class availability, configuration, and factory registration.
- Raw comparison flows either deserialize two writable values and call natural ordering, or optimized comparators compare serialized byte slices directly. `WritableComparator.define` changes the comparator selected for a key class globally.
- SequenceFile writer creation flows through either a modern option-list API or many legacy overloads that choose filesystem, path or output stream, key/value classes, compression type, codec, progress, metadata, replication, block size, and create flags. Readers are documented as format bridges across uncompressed, record-compressed, and block-compressed files.
- Compression streams repeatedly accept input, check `needsInput`, compress/decompress into caller buffers, and finish/reset/end codec state. Codec pools lease and return compressor state; failure to return instances changes memory/native-resource behavior.
- Splittable compression flows from a seekable compressed stream and requested compressed offsets to adjusted block-aligned offsets and a `SplitCompressionInputStream` that reports positions according to the read mode.
- TFile lookup and scan behavior depends on block indexes, meta-block indexes, comparator choice, compression algorithm, and shared stream seek/read sequencing.

## State And Persistence Behavior

The JDiff XML persists API metadata only. The APIs it describes are deeply stateful:

- Writable instances hold mutable field state and serialize it to `DataOutput`; callers must keep read/write order stable across versions.
- `DefaultStringifier.store/load` persists serialized objects or arrays into Hadoop `Configuration` entries, so configuration becomes a transport/storage layer for object state.
- `ElasticByteBufferPool`, `CodecPool`, `WritableComparator` registrations, `WritableFactories`, and thread-local `MD5Hash` digesters are process-level state caches or registries.
- `IOUtils.copyBytes`, `fsync`, `listDirectory`, and close helpers touch files, sockets, channels, and streams. `fsync` is a durability boundary and has platform-specific behavior for directories.
- `MapFile` persists data and index files in a directory; `fix` can recreate an index and can run as a dry run. `SequenceFile` persists binary records, headers, sync markers, compression metadata, and user metadata. `TFile` persists compressed data blocks, metadata blocks, indexes, and comparator/compression settings.
- Compressor and decompressor instances have lifecycle state: input buffers, dictionaries, counters, finished flags, remaining compressed bytes, reset state, and native resources released by `end`.
- `ECSchema` carries erasure-code layout state that integrates with higher-level HDFS erasure-coding policy logic outside this chunk.

## Dependencies And Integration Points

This API slice depends on core Java I/O and NIO (`DataInput`, `DataOutput`, streams, channels, `ByteBuffer`, `FileChannel`), collections, reflection/class loading, `MessageDigest`, and character-coding APIs. Hadoop dependencies include `Configuration`, `Configurable`, `FileSystem`, `FileContext`, `Path`, `Options.CreateOpts`, `Progressable`, `SerializationFactory` and serialization interfaces, `ByteBufferPool`, `BinaryComparable`, `UTF8`, `AbstractMapWritable`, and compression implementation classes outside this XML slice.

Integration points include MapReduce key/value serialization and partitioning, SequenceFile and MapFile data exchange, TFile readers/writers, HDFS and other `FileSystem` implementations, native compression libraries, Java `ServiceLoader` codec discovery, job configuration properties such as default SequenceFile compression type and `io.compression.codecs`, and erasure-code schema consumers.

Because this is a public API report, source and binary compatibility are central integration concerns. Method overloads marked deprecated still appear in the public contract and may be used by older callers. Comparator encodings, writable byte formats, SequenceFile headers, TFile variable-length integer formats, and codec aliases are storage-format or wire-format contracts rather than ordinary helper details.

## Risks And Edge Cases

- The range begins mid-`DefaultStringifier` and ends mid-`Utils.upperBound`; final analysis for those two classes needs adjacent chunk reconciliation.
- Serialization compatibility is fragile. Changing field order, VInt encoding, `Text` length bounds, or class names used by `ObjectWritable` can break persisted data and distributed RPC/data exchange.
- `WritableComparable.hashCode()` must be stable across JVM processes. Implementations using identity-based or randomized hash behavior can corrupt partitioning behavior.
- `WritableComparator.define` requires thread-safe comparators but does not encode enforcement in the signature. A non-thread-safe raw comparator can cause sort/group instability under parallel use.
- `ElasticByteBufferPool` documents no maximum cache size. Long-running processes can retain large direct or heap buffers if workload sizes spike.
- `CodecPool` requires disciplined return of compressors/decompressors. Missing returns leak pooled/native resources and distort leased-count diagnostics.
- `BZip2Codec` behavior changes by native versus pure-Java mode: splittability forces pure-Java, while compressor/decompressor-argument methods can throw `UnsupportedOperationException` in pure-Java mode.
- `Decompressor.setInput` requires input buffers to remain unmodified until `needsInput()` permits modification. Violating this can produce data corruption without a type-system signal.
- `IOUtils.cleanup*` intentionally ignores `Throwable`, which is appropriate for exception cleanup but risky if used on the main success path.
- `IOUtils.readFullyToByteArray` warns that infinite `DataInput` never returns; callers need bounded input when reading untrusted or streaming data.
- `Text.getBytes()` returns the backing array, not an exact-length copy. Callers must honor `getLength()` or use `copyBytes()` to avoid stale trailing data.
- `MapFile` indexes are read entirely into memory and key implementations should stay small. Large keys or many index entries increase heap pressure.
- TFile shared-stream reads are documented as effectively sequential even with multiple scanners, which can surprise callers expecting parallel random access.
- TFile compression choices affect CPU and random-access behavior; large blocks help sequential reads but hurt random access and index memory tradeoffs.
- `ECSchema` constructors from maps depend on required option names and value validity; invalid unit counts or missing options are likely handled in implementation outside this XML but should be validated by consumers.

## Test Signals

Useful validation for this chunk includes:

- JDiff/XML parsing checks that every visible class, interface, method, field, deprecation flag, exception, and package boundary is well-formed; include boundary tests for this chunk's partial start/end classes.
- Serialization round-trip tests for all primitive writables, `EnumSetWritable` including null and empty sets with element type, `MapWritable`, `SortedMapWritable`, `TwoDArrayWritable`, `VersionedWritable`, `ObjectWritable`, and `GenericWritable` subclasses.
- Compatibility tests for `WritableUtils` VInt/VLong sizes, sign handling, range validation, enum string encoding, safe string maximum lengths, and TFile `Utils` variable-length integer/string encodings.
- Comparator tests for object comparison versus raw byte-slice comparison, optimized comparator registration, stable `hashBytes`, and byte parsing helpers.
- `Text` tests for malformed UTF-8 replacement versus exception behavior, maximum-length read/write enforcement, `charAt` on invalid positions/trailing bytes, `find`, append, clear, backing-array length semantics, and codepoint traversal.
- File-container tests for SequenceFile writer overloads, default compression configuration, metadata persistence, sync interval behavior, uncompressed/record-compressed/block-compressed read interoperability, MapFile rename/delete/fix dry-run and repair behavior, and SetFile key-only semantics.
- IO utility tests for short reads/writes, EOF behavior in `readFully` and `skipFully`, close cleanup swallowing behavior, `wrapException` preserving important exception types, directory listing IO failures, and file/channel `fsync` behavior across supported platforms.
- Compression tests for codec factory discovery by config and `ServiceLoader`, suffix and alias lookup, codec pool lease/return counters, compressor/decompressor reset and finish state, direct `ByteBuffer` decompression, concatenated streams via `getRemaining`, and splittable bzip2 adjusted offsets.
- TFile tests for supported compression names, comparator name parsing, metadata-block duplicate/missing exceptions, sorted and unsorted key behavior, seek-by-key and seek-by-offset, block-size and chunk-size configuration, index memory scaling, and concurrent scanner behavior over a shared reader.
- Erasure-code schema tests for constructors from maps and explicit arguments, extra-option preservation, equality/hash-code stability, and string output suitable for logs.
