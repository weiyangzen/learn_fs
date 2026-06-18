# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 17936-24232

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.10.0. It starts inside the tail of `org.apache.hadoop.io.ArrayPrimitiveWritable`, covers most of the public `org.apache.hadoop.io` package API, closes that package, opens `org.apache.hadoop.io.compress`, and ends partway through `org.apache.hadoop.io.compress.GzipCodec`.

Because this file is generated API metadata rather than executable source, the research surface is the public compatibility contract: packages, classes, interfaces, inheritance, implemented interfaces, constructors, method signatures, fields, checked exceptions, deprecation markers, and embedded Javadoc. Adjacent chunks own the start of `ArrayPrimitiveWritable` and the remainder of `GzipCodec`.

## Purpose

The `org.apache.hadoop.io` portion describes Hadoop's core serialization and binary data model. It defines `Writable` and `WritableComparable`, primitive writable wrappers, byte/text containers, polymorphic writable wrappers, map/array writable containers, raw comparators, stringification helpers, file-backed key/value containers such as `MapFile` and `SequenceFile`, and utility routines for stream copying, varint encoding, UTF-8 handling, checksums/hashes, cloning, and safe string reads.

The `org.apache.hadoop.io.compress` portion describes the streaming compression abstraction used by Hadoop I/O and file formats. It defines codecs, codec discovery, compressor/decompressor pooling, compression input/output stream base classes, block compression stream variants, the compressor/decompressor state-machine interfaces, default/direct decompression hooks, and BZip2/Gzip codec APIs.

## Important APIs, Types, and Functions

### Core writable data model

- `Writable` is the base serialization contract: `write(DataOutput)` serializes object fields and `readFields(DataInput)` deserializes into reusable storage.
- `WritableComparable` combines `Writable` with `Comparable` for MapReduce keys and explicitly warns that key `hashCode()` values must be stable across JVM instances.
- Primitive wrappers include `BooleanWritable`, `ByteWritable`, `ShortWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, `DoubleWritable`, `VIntWritable`, and `VLongWritable`. They expose constructors, `set()`, `get()`, `readFields()`, `write()`, equality, hash, comparison, and string conversion.
- `VIntWritable` and `VLongWritable` store integer/long values in Hadoop's variable-length, zero-compressed encoding, tying them to `WritableUtils.readVInt()` and `WritableUtils.readVLong()`.
- `NullWritable` is a singleton no-data writable for places where a key or value position is semantically empty.

### Binary, text, and object wrappers

- `BinaryComparable` defines byte-backed comparison via abstract `getBytes()` and `getLength()`, with concrete byte comparison, equality, and hash behavior using `WritableComparator` helpers.
- `BytesWritable` is a mutable byte sequence with backing-array access, exact copy access, length/capacity mutation, byte-range `set()`, and binary-compatible serialization. Deprecated `get()` and `getSize()` point callers to `getBytes()` and `getLength()`.
- `Text` stores UTF-8 bytes with byte-level comparison and traversal. It exposes constructors from strings, bytes, and other `Text`; `copyBytes()`, `getBytes()`, `charAt()`, `find()`, range `set()`/`append()`, `clear()`, bounded `readFields()`/`write()`, static `readString()`/`writeString()`, UTF-8 `encode()`/`decode()`, `validateUTF8()`, `bytesToCodePoint()`, `utf8Length()`, and `DEFAULT_MAX_LEN`.
- `ObjectWritable` serializes a declared class plus an instance, supporting `Writable`, `String`, primitives, and arrays. Its static `writeObject()`/`readObject()` methods have configuration-aware overloads and an `allowCompactArrays` flag intended for RPC/internal use rather than persisted inter-cluster or file output.
- `GenericWritable` is a more compact wrapper for a bounded set of writable implementation classes returned by subclass-provided `getTypes()`.
- `ArrayPrimitiveWritable`, `ArrayWritable`, `TwoDArrayWritable`, `MapWritable`, `SortedMapWritable`, and `EnumSetWritable` provide writable containers for primitive arrays, homogeneous writable arrays, matrices, maps, sorted maps, and enum sets.

### File, comparator, utility, and helper APIs

- `SequenceFile` exposes default compression-type configuration and many static `createWriter()` overloads for `FileSystem`, `FileContext`, `FSDataOutputStream`, key/value classes, replication/block options, compression type, codecs, progress callbacks, metadata, create flags, and modern `Writer.Option...`. Many legacy overloads are explicitly deprecated in favor of `createWriter(Configuration, Writer.Option...)`. `SYNC_INTERVAL` is the public sync marker interval constant.
- `MapFile` exposes `rename()`, `delete()`, `fix()`, `main()`, and `INDEX_FILE_NAME`/`DATA_FILE_NAME` for directory-backed sorted key/value maps. `BloomMapFile` adds Bloom-filter membership acceleration and has `BLOOM_FILE_NAME` and `HASH_COUNT`.
- `SetFile` extends `MapFile`; in this chunk only its class shell/constructor appears, with nested reader/writer details likely elsewhere in the generated snapshot.
- `RawComparator` compares serialized objects directly from byte slices. `WritableComparator` implements `RawComparator` plus `Configurable`, provides registry access via `get()` and `define()`, object and byte-slice `compare()` hooks, byte lexicographic comparison, stable byte hashing, primitive byte-array readers, and varint readers.
- `WritableFactories` and `WritableFactory` let non-public writable implementations be instantiated by factory, which is important for `ObjectWritable`.
- `WritableUtils` groups compressed byte/string array I/O, normal string I/O, enum I/O, writable cloning, varint/vlong encode/decode helpers, varint size/sign inspection, `skipFully()`, writable array to bytes, and `readStringSafely()` length checks.
- `IOUtils` provides stream copy overloads, compressed-data read wrapping, `readFully()`, `skipFully()`, close/cleanup helpers, socket close, full `ByteBuffer` writes to channels, directory listing with exception propagation, file/channel `fsync()`, and `readFullyToByteArray()`.
- `DefaultStringifier` and `Stringifier<T>` define object-to-string round trips backed by Hadoop serializers and `Configuration` storage/load helpers.
- `CompressedWritable` defines lazy-inflated writable storage through `ensureInflated()`, subclass hooks `readFieldsCompressed()` and `writeCompressed()`, and compressed `readFields()`/`write()` wrappers.
- `MD5Hash` is a writable/comparable MD5 digest holder with constructors from hex or bytes, static digest helpers for byte arrays, `InputStream`, `String`, and deprecated `UTF8`, plus half/quarter digest projections.
- `MultipleIOException` aggregates multiple `IOException` instances and can return either one exception or a wrapper.
- `VersionedWritable` writes a version byte and checks it during read; `VersionMismatchException` reports mismatches.

### Compression APIs

- `CompressionCodec` is the codec contract for creating compression/decompression streams with or without pooled `Compressor`/`Decompressor` instances, discovering required compressor/decompressor classes, creating instances, and reporting a default filename extension.
- `CompressionCodecFactory` discovers codecs from `io.compression.codecs`, Java `ServiceLoader`, and defaults such as gzip/deflate; it looks up codecs by path suffix, canonical class name, or case-insensitive aliases, and provides `removeSuffix()`.
- `CodecPool` leases and returns reusable compressors/decompressors and exposes leased counts per codec.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases. Input implements `Seekable`, supports `getPos()`, `resetState()`, and default unsupported seek behavior; output supports `finish()` without closing the underlying stream and `resetState()` without resetting that stream.
- `Compressor` and `Decompressor` are stream-state interfaces modeled after `Deflater` and `Inflater`. They expose `setInput()`, `needsInput()`, dictionaries, `finish()`/`finished()` where relevant, byte counters for compressors, `compress()`/`decompress()`, `reset()`, `end()`, and compressor `reinit(Configuration)`.
- `CompressorStream` and `DecompressorStream` wrap compressor/decompressor instances with buffers and closed/eof state. They provide read/write loops, finish/reset/close behavior, protected compressor/decompressor hooks, skip/available, and mark/reset behavior.
- `BlockCompressorStream` and `BlockDecompressorStream` adapt block-oriented algorithms by writing uncompressed block length plus length-prefixed compressed chunks and by reading/decompressing block records.
- `BZip2Codec` implements `SplittableCompressionCodec`, has configuration accessors, normal stream creation, split stream creation with `READ_MODE`, default `.bz2` extension, and Javadocs noting native-vs-pure-Java behavior, unsupported compressor/decompressor methods in pure-Java mode, and split support being pure-Java only.
- `DefaultCodec` implements `CompressionCodec` and `DirectDecompressionCodec`; `DirectDecompressionCodec` and `DirectDecompressor` add direct `ByteBuffer` decompression. The chunk begins `GzipCodec`, showing it extends `DefaultCodec` and overrides stream and compressor/decompressor factory methods.

## Control Flow

The XML itself has no runtime control flow, but the documented APIs imply several important flows:

- Writable serialization is caller-driven: callers instantiate or reuse a writable, call `write(DataOutput)` to emit a deterministic binary representation, and call `readFields(DataInput)` to mutate an existing object from bytes. Containers such as arrays, maps, enum sets, `ObjectWritable`, and `GenericWritable` add type metadata or type indexes around nested writable values.
- Binary comparison avoids full deserialization when possible. `RawComparator.compare(byte[], int, int, byte[], int, int)` compares serialized byte ranges; `WritableComparator` defaults to deserializing into `WritableComparable` objects but allows optimized byte-level overrides and provides static byte parsing helpers for those overrides.
- Text handling keeps data in UTF-8 bytes. `Text` can search, index, validate, and compare at byte level, while string conversion happens only through explicit encode/decode methods or `toString()`. Its serialized length uses zero-compressed integer encoding.
- SequenceFile writer creation converges through a broad overload set. Older callers pass filesystem/path/key/value/compression details directly; newer callers use `Writer.Option...`. The API preserves deprecated overloads for binary/source compatibility.
- Compression streams follow a state loop. Callers feed uncompressed input to a `Compressor` with `setInput()` when `needsInput()` is true, drain compressed bytes with `compress()`, call `finish()`, and check `finished()`. Decompression mirrors this with `Decompressor.setInput()`, `decompress()`, `needsInput()`, dictionary handling, `finished()`, and `getRemaining()` for concatenated streams.
- Codec discovery is name/suffix driven: `CompressionCodecFactory` loads configured and service-discovered codec classes, builds suffix and alias maps, then returns codecs for file paths, class names, or aliases.
- Pooled compression flow leases compressor/decompressor instances from `CodecPool`, uses them with codec-created streams, resets or reinitializes them as needed, and returns them to the pool to avoid repeated native allocation.

## State and Persistence Behavior

The JDiff file itself persists API metadata for compatibility checks and release documentation. It does not store application data.

The APIs it describes are persistence-sensitive. `Writable`, `WritableComparable`, `Text`, primitive writables, `MapWritable`, `SortedMapWritable`, `ArrayWritable`, `ObjectWritable`, `GenericWritable`, `MD5Hash`, `VersionedWritable`, and `WritableUtils` define binary formats used in RPC, MapReduce shuffle/sort, SequenceFiles, MapFiles, and other Hadoop data paths. Deprecation notes matter because old serialized data and old callers may remain in production.

Several classes expose mutable backing state. `BytesWritable.getBytes()` and `Text.getBytes()` return backing arrays whose valid range is only `getLength()`. `ArrayPrimitiveWritable` explicitly wraps primitive arrays without copying. `Text.clear()` does not clear or free the backing byte array. `CompressedWritable` stores compressed data and inflates lazily on field access. These behaviors are performance-oriented but make object reuse and external mutation part of the practical state model.

Configuration persistence appears through `DefaultStringifier.store()`, `load()`, `storeArray()`, and `loadArray()`, which serialize objects into `Configuration` keys; `SequenceFile.setDefaultCompressionType()` stores a default compression enum in a `Configuration`. `WritableFactories` and `WritableComparator.define()` maintain static registries for instantiation and comparison behavior.

File persistence appears through `MapFile` and `SequenceFile`. `MapFile` documents a directory containing `data` and `index` files, and `fix()` can recreate a corrupt index from data. `SequenceFile.createWriter()` creates on-filesystem binary key/value files with optional compression, metadata, sync markers, and filesystem creation options.

Compression state is mostly stream-local or pooled. `CompressorStream`/`DecompressorStream` retain compressor/decompressor handles, buffers, closed/eof flags, and resettable codec state. `CodecPool` keeps global reusable compressor/decompressor state and leased counters.

## Dependencies and Integration Points

The APIs depend on Java `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `Socket`, `ByteBuffer`, `FileChannel`, `WritableByteChannel`, `MessageDigest`, charset coding exceptions, collections, and Java `Closeable`/`Comparator`.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configurable` for object configuration, stringification, codec discovery, comparator construction, and compressor reinitialization.
- `org.apache.hadoop.fs.FileSystem`, `FileContext`, `Path`, `FSDataOutputStream`, `Seekable`, `Options.CreateOpts`, and create flags for file-backed APIs.
- `org.apache.hadoop.util.Progressable` for legacy SequenceFile writer progress.
- `org.apache.hadoop.io.serializer.SerializationFactory`, `Serializer`, and `Deserializer` through `DefaultStringifier`.
- MapReduce/shuffle/sort consumers that require `WritableComparable` keys, stable `hashCode()` partitioning, and optimized `RawComparator` implementations.
- Compression users such as SequenceFile, codecs selected from path suffixes, splittable input formats, native compression libraries, and direct `ByteBuffer` decompression paths.
- Logging via `org.slf4j.Logger` in `IOUtils` and `CompressionCodecFactory`.

## Risks and Edge Cases

- The chunk starts and ends inside classes. A file-level summary must merge with adjacent chunks before making final claims about all `ArrayPrimitiveWritable` and `GzipCodec` methods.
- JDiff records API shape, not implementation bodies. Behavioral conclusions come from Javadocs and signatures; implementation details such as exact buffer growth policy, pool synchronization, and exception messages require source-code validation.
- Backing-array exposure in `BytesWritable`, `Text`, and `ArrayPrimitiveWritable` can leak stale bytes, allow external mutation, or retain large buffers after logical clear. Callers that need exact-length immutable content must use `copyBytes()` or copy arrays explicitly.
- Writable binary compatibility is fragile. Changing `write()`/`readFields()` order, varint encodings, enum string names, class names in `ObjectWritable`, or `VersionedWritable` version semantics can break persisted files and inter-process compatibility.
- `ObjectWritable`'s `allowCompactArrays` flag is documented as suitable for RPC/internal or intra-cluster usage and unsuitable for inter-cluster/file/persisted output. Misuse can create incompatible durable encodings.
- `WritableComparable` warns that default `Object.hashCode()` is not stable across JVMs. Any key implementation using identity hash can partition inconsistently.
- `WritableComparator.define()` requires thread-safe comparators. A stateful optimized comparator can corrupt sort/shuffle behavior under concurrent use.
- `Text` APIs use byte positions, not Java char indexes, for operations such as `find()` and `charAt()`. Invalid positions or trailing UTF-8 bytes return `-1`; mixed byte/char assumptions can produce off-by-one bugs.
- BZip2 behavior differs between native and pure-Java modes. The Javadocs say pure-Java mode does not implement `Compressor`/`Decompressor` interface paths and split input always uses pure Java, so tests must cover both configuration modes.
- Decompressor input buffer ownership is explicit: callers must not modify input bytes until `needsInput()` indicates it is safe. Violating this contract can cause corrupt decompression without a defensive copy.
- `CompressionInputStream.seek()` and `seekToNewSource()` are documented as unsupported defaults despite implementing `Seekable`; callers must not assume all compression streams are seekable unless a subclass says so.
- Codec alias lookup is case-insensitive and strips `Codec` suffixes, so alias collisions between configured/service-loaded codecs can change which codec is selected.

## Test Signals

Useful validation for this API surface should include:

- Round-trip serialization tests for every primitive writable, `BytesWritable`, `Text`, `MD5Hash`, `ArrayWritable`, `TwoDArrayWritable`, `MapWritable`, `SortedMapWritable`, `EnumSetWritable`, `ObjectWritable`, `GenericWritable`, `NullWritable`, and `VersionedWritable` success/failure cases.
- Binary compatibility tests against golden bytes for varint/vlong encodings, `Text` length encoding, primitive writables, `ObjectWritable` class metadata, and `SequenceFile`/`MapFile` data written by earlier Hadoop versions.
- Comparator tests comparing object-level and byte-level results for `BinaryComparable`, `BytesWritable`, `Text`, primitive writables, `WritableComparator`, and custom registered comparators.
- Backing-array tests proving `getBytes()` valid ranges, `copyBytes()` exact length, `Text.clear()` retention behavior, and `ArrayPrimitiveWritable` no-copy semantics.
- UTF-8 tests for malformed inputs, replacement vs exception behavior, byte-position `find()`, `charAt()` on leading/trailing bytes, maximum length enforcement, `validateUTF8()`, and `readStringSafely()` negative/oversize lengths.
- IO utility tests for partial reads/skips/writes, EOF handling, cleanup swallowing/logging behavior, socket close, directory listing exceptions, file/channel `fsync()`, and compressed-data read wrapping.
- `SequenceFile.createWriter()` tests for modern options and deprecated overloads, compression type defaults, codec selection, metadata, create-parent behavior, `FileContext` options, sync interval behavior, and progress callback compatibility.
- `MapFile.fix()` tests for missing/corrupt indexes, dry-run behavior, valid entry counts, and data/index filename expectations.
- Compression tests for codec discovery from configuration and `ServiceLoader`, path suffix lookup, alias lookup/collisions, `removeSuffix()`, codec pool lease/return counts, stream `finish()` vs `close()`, reset-state behavior after repositioning, and direct `ByteBuffer` decompression.
- BZip2 tests in native and pure-Java modes, including unsupported compressor/decompressor paths in pure-Java mode and split input boundary/progress behavior.
- Decompressor concatenated-stream tests where `finished()` plus positive `getRemaining()` triggers reset before reading the next stream.

## Cross-Chunk Notes

`subset-b-007139` should provide the opening of `ArrayPrimitiveWritable` and earlier `org.apache.hadoop.io` classes such as `AbstractMapWritable` and any nested types that precede this chunk. `subset-b-007141` should complete `GzipCodec` and continue the `org.apache.hadoop.io.compress` package. The merge lane should avoid duplicating final package-level conclusions until these adjacent chunks are reconciled.
