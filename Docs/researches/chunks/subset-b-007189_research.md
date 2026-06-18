# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml - subset-b-007189

## Scope

- Source chunk: `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml` lines 17951-24252.
- This is a JDiff XML API snapshot for Apache Hadoop Common 3.1.2, not Java implementation source. It records public/protected type names, inheritance, constructors, methods, fields, deprecation markers, exceptions, parameters, and selected Javadoc text.
- The chunk starts inside `org.apache.hadoop.io.ArrayWritable` and ends inside `org.apache.hadoop.io.compress.SplitCompressionInputStream`; adjacent classes outside this range are intentionally left for neighboring chunks.

## Purpose

This chunk describes Hadoop Common's core binary serialization and compression public APIs. The main purpose is to define stable contracts for:

- `Writable` serialization, deserialization, comparison, and factory construction.
- Primitive and compound writable value wrappers used throughout Hadoop RPC, SequenceFile, MapFile, MapReduce keys and values, and configuration persistence.
- Byte and text handling utilities for Hadoop's binary formats.
- SequenceFile, MapFile, SetFile, and BloomMapFile file-format entry points.
- Compression codec abstractions, stream wrappers, codec lookup, compressor/decompressor pooling, and built-in default/gzip/bzip2 APIs.

Because this is a compatibility descriptor, the important information is the API surface and behavioral promises captured in documentation. Runtime behavior must be verified against the matching Java sources, but this chunk is sufficient to identify the exported contracts and integration points.

## Major API Areas

### Writable Core

- `Writable` defines the central binary serialization interface with `write(DataOutput)` and `readFields(DataInput)`. Implementations must read fields in the same order and representation used by `write`.
- `WritableComparable` combines `Writable` with Java `Comparable`, making writable values usable as sort keys.
- `RawComparator<T>` adds binary comparison over serialized byte ranges through `compare(byte[], int, int, byte[], int, int)`, avoiding full object materialization.
- `WritableComparator` is the main comparator framework. It provides comparator lookup/registration with `get(...)` and `define(...)`, reflective key construction via `newKey()`, object-level and raw byte comparison, byte hashing, and primitive readers such as `readInt`, `readLong`, `readVInt`, and `readVLong`.
- `WritableFactories` and `WritableFactory` provide factory registration and instantiation for writable classes, especially non-public implementations or classes that cannot be constructed directly by ordinary reflection.
- `VersionedWritable` writes and checks a version byte before subclass data; `VersionMismatchException` reports mismatches.

### Primitive Writable Types

The chunk includes writable wrappers for primitive-like scalar values:

- `BooleanWritable`, `ByteWritable`, `ShortWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, and `DoubleWritable`.
- `VIntWritable` and `VLongWritable`, which store integer and long values in variable-length Hadoop encoding.
- Each scalar wrapper exposes a default constructor, a value constructor, `set(...)`, `get()`, `readFields(DataInput)`, `write(DataOutput)`, `equals(Object)`, `hashCode()`, `compareTo(...)`, and `toString()`.

These classes are small state containers around one primitive value. Their public contract is important because Hadoop sort, shuffle, SequenceFile, and RPC paths depend on serialized byte compatibility and stable ordering.

### Byte, Text, and Binary Comparison

- `BinaryComparable` is an abstract base for byte-backed comparable objects. Subclasses implement `getBytes()` and `getLength()`, while the base provides comparison, equality, and hashing over byte ranges.
- `BytesWritable` extends `BinaryComparable` and represents a resizable byte sequence with distinct logical length and backing capacity. It exposes `copyBytes()`, `getBytes()`, `getLength()`, `setSize(int)`, `getCapacity()`, `setCapacity(int)`, `set(BytesWritable)`, `set(byte[], int, int)`, serialization, hashing, equality, and hex-style `toString()`. Deprecated aliases `get()` and `getSize()` point callers to `getBytes()` and `getLength()`.
- `Text` stores standard UTF-8 text and exposes constructors from `String`, `Text`, and `byte[]`; mutable byte operations such as `set(...)`, `append(...)`, and `clear()`; string conversion; serialization with optional maximum length; UTF-8 encode/decode helpers; validation; code point iteration helpers; and `DEFAULT_MAX_LEN`.
- `MD5Hash` is a writable/comparable MD5 value type. It supports construction from bytes or hex string, reading/writing, digest creation from byte arrays, byte array arrays, strings, and input streams, thread-local digester access, half and quarter digest projections, digest copying, hex parsing, equality, hashing, comparison, and `MD5_LEN`.

### Array, Map, Object, and Generic Writables

- `ArrayWritable` represents arrays of a single writable element class, with value-class reporting, conversion to strings/object arrays, `set(Writable[])`, `get()`, and serialization.
- `TwoDArrayWritable` generalizes the array contract to two-dimensional writable matrices.
- `MapWritable` is a writable map with ordinary `Map`-style operations: `clear`, `containsKey`, `containsValue`, `entrySet`, `get`, `put`, `putAll`, `remove`, `size`, `values`, plus `readFields` and `write`.
- `SortedMapWritable` extends the map contract with `SortedMap`-style operations such as `comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, and `tailMap`.
- `EnumSetWritable` wraps an `EnumSet`, carries element type information, implements collection operations, and is configurable through `getConf()` and `setConf(Configuration)`.
- `GenericWritable` wraps one of a fixed set of writable classes supplied by subclasses through `getTypes()`. It stores the concrete instance plus configuration and handles dynamic serialization.
- `ObjectWritable` is the polymorphic writable for `Writable`, `String`, primitive types, arrays, and declared classes. Static `writeObject(...)` and `readObject(...)` methods serialize class metadata plus values; `loadClass(...)` resolves a class name through the active configuration/classloader.
- `NullWritable` is a singleton writable with no payload, used for key or value positions that intentionally carry no data.

### File-Oriented Writable Formats

- `SequenceFile` exposes writer creation APIs and compression defaults for Hadoop's binary flat file of key/value pairs. The chunk lists many overloaded `createWriter(...)` methods, several deprecated in favor of `createWriter(Configuration, Writer.Option...)`, plus `getDefaultCompressionType`, `setDefaultCompressionType`, and `SYNC_INTERVAL`.
- `MapFile` is a directory-backed sorted key/value map built from data and index files. Exposed static helpers include `rename(FileSystem, String, String)`, `delete(FileSystem, String)`, `fix(...)` for rebuilding corrupt indexes, and constants `INDEX_FILE_NAME` and `DATA_FILE_NAME`.
- `SetFile` is a file-backed set of keys.
- `BloomMapFile` extends the MapFile model with a dynamic Bloom filter for fast negative membership checks. It exposes `delete(...)` and constants `BLOOM_FILE_NAME` and `HASH_COUNT`.

### IO Utilities and Stringification

- `IOUtils` provides stream and channel utility methods: multiple `copyBytes(...)` overloads, compressed-data read wrapping, `readFully`, `skipFully`, close/cleanup helpers, socket closing, `writeFully` for channels/file offsets, directory listing, `fsync(...)`, exception wrapping, and `readFullyToByteArray`.
- `Stringifier<T>` defines conversion between objects and string representations plus `close()`.
- `DefaultStringifier<T>` implements the stringifier contract using Hadoop serialization and provides static configuration helpers: `store`, `load`, `storeArray`, and `loadArray`.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`.
- `MultipleIOException` groups multiple `IOException` instances and exposes a convenience constructor method.
- `Closeable` exists only as a deprecated Hadoop interface in favor of `java.io.Closeable`.

### Compression APIs

- `CompressionCodec` is the central codec abstraction. It creates compression/decompression streams, creates compressor/decompressor instances, exposes compressor/decompressor implementation classes, and declares a default file extension.
- `CompressionCodecFactory` discovers codec classes from configuration `io.compression.codecs` and Java `ServiceLoader`, maps path suffixes to codecs, supports lookup by path, class name, or codec name, exposes `setCodecClasses(...)`, `getCodecClasses(...)`, `removeSuffix(...)`, and a small `main(...)` test program. It has a `LOG` field.
- `CodecPool` is a global pool for reusing compressors and decompressors. It leases objects by codec, returns them to the pool, and exposes leased compressor/decompressor counts for testing or diagnostics.
- `Compressor` defines the state machine for stream compression: `setInput`, `needsInput`, optional `setDictionary`, byte counters, `finish`, `finished`, `compress`, `reset`, `end`, and `reinit(Configuration)`.
- `Decompressor` mirrors the decompression state machine: `setInput`, `needsInput`, optional dictionary handling, `needsDictionary`, `finished`, `decompress`, `getRemaining`, `reset`, and `end`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream wrappers around input/output streams. They define close/read or close/flush/write behavior plus `resetState`; the input side also exposes `getPos`, unsupported seek hooks, and `maxAvailableData`.
- `CompressorStream` and `DecompressorStream` are concrete stream adapters around a `Compressor` or `Decompressor`. They maintain protected state fields such as `compressor`, `decompressor`, byte buffers, `closed`, and on decompression `eof`.
- `BlockCompressorStream` and `BlockDecompressorStream` handle block-oriented codecs by splitting input into chunks, writing block-compressed data, reading compressed block payloads, and resetting stream state.
- `BZip2Codec` implements configurable bzip2 streams, including split input stream creation for file splits and `.bz2` as the default extension.
- `DefaultCodec` implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`, providing default stream creation, compressor/decompressor creation, direct decompressor creation, and default extension handling.
- `GzipCodec` extends `DefaultCodec` with gzip-specific stream, compressor, decompressor, direct decompressor, and extension behavior.
- `DirectDecompressionCodec` and `DirectDecompressor` define the direct `ByteBuffer` decompression path.
- `SplitCompressionInputStream` begins in this chunk and exposes construction from an input stream plus start/end offsets and protected `setStart(long)` / `setEnd(long)` mutators. Its remaining API is outside this chunk.

## Control Flow and Behavioral Contracts

Although implementation bodies are not present, the XML documents several important control-flow protocols:

- Writable read/write flow is paired and ordered: callers invoke `write(DataOutput)` to serialize fields and `readFields(DataInput)` to mutate an existing object by reading the same representation back.
- Raw comparison flow avoids object allocation: Hadoop sort components can compare serialized byte ranges through `RawComparator` or optimized `WritableComparator.compare(byte[], ...)`.
- Variable-length integer flow uses first-byte decoding through `WritableUtils.isNegativeVInt`, `decodeVIntSize`, `readVLong`, `readVInt`, and corresponding write helpers. Callers that validate ranges use `readVIntInRange`.
- `CompressedWritable` stores compressed bytes after `readFields` and lazily inflates them. Subclasses must route field access through `ensureInflated()` and implement `readFieldsCompressed(DataInput)` / `writeCompressed(DataOutput)`.
- `GenericWritable` and `ObjectWritable` serialize class identity along with value payloads; deserialization flow includes class lookup and instance construction, so configuration/classloader availability is part of the runtime path.
- `SequenceFile.createWriter(...)` overloads funnel callers toward a writer configured by key/value classes, filesystem/path, buffer size, replication, block size, progress callback, metadata, and compression settings. Newer APIs prefer option objects.
- `MapFile.fix(...)` is a repair path that scans data and rebuilds the index for corrupt map directories.
- Compression streams follow a loop: set input on a compressor/decompressor, call `compress` or `decompress` until output is produced or more input is needed, signal `finish`, observe `finished`, then `reset` for reuse or `end` for disposal.
- `CodecPool` adds a lease/return flow around codec-created compressors and decompressors; callers must return leased objects to prevent pool accounting leaks.
- `Decompressor.finished()` plus `getRemaining()` is documented as the way to detect concatenated compressed data streams; a caller resets before processing the next stream segment.

## State and Persistence Behavior

- Every `Writable` in this chunk persists state to `DataOutput` and restores it from `DataInput`; compatibility depends on exact binary format stability.
- Primitive writable classes persist one scalar field, while variable-length wrappers persist using Hadoop zero-compressed encodings.
- `BytesWritable` and `Text` separate logical length from backing storage. Returning raw byte arrays can expose capacity beyond valid data; callers must honor `getLength()` or copy via `copyBytes()`.
- `MapWritable` and `SortedMapWritable` persist both keys and values as writable entries and must track runtime classes so heterogeneous maps can deserialize correctly.
- `EnumSetWritable` persists enum set contents plus element type, including the special need to retain element type when a value can be null or empty.
- `DefaultStringifier` persists serialized objects into `Configuration` values, making configuration keys an integration point for object state.
- `SequenceFile`, `MapFile`, `SetFile`, and `BloomMapFile` persist data to Hadoop `FileSystem` paths. MapFile has separate index and data files; BloomMapFile adds a Bloom filter file.
- Compression stream classes maintain mutable stream state: buffers, closed/eof flags, byte counters, dictionary state, remaining compressed input, and direct buffer positions.
- `CodecPool` maintains global shared state for leased and cached compressors/decompressors; misuse can have process-wide impact.

## Dependencies

The API surface depends on:

- Java core I/O: `java.io.DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `IOException`, `EOFException`, `File`, and closeable/stream contracts.
- Java NIO: `ByteBuffer`, `WritableByteChannel`, and `FileChannel`.
- Java collections and language types: `Map`, `SortedMap`, `Set`, `Collection`, `Iterator`, `EnumSet`, `Comparator`, `Class`, arrays, and primitives.
- Java security and text support through `MessageDigest`, character encoding, and UTF-8 validation/encoding behavior.
- Hadoop configuration and filesystem APIs: `org.apache.hadoop.conf.Configuration`, `Configurable`, `org.apache.hadoop.fs.FileSystem`, `Path`, and `Progressable`.
- Hadoop serialization infrastructure for `DefaultStringifier`, `ObjectWritable`, and writable cloning.
- Hadoop compression implementations and native/direct codecs behind `DefaultCodec`, `GzipCodec`, `BZip2Codec`, `Compressor`, `Decompressor`, and `DirectDecompressor`.
- Logging through `org.slf4j.Logger` in utility/factory classes.

## Integration Points

- MapReduce key/value types rely heavily on `WritableComparable`, `RawComparator`, and primitive writable wrappers for shuffle sorting and grouping.
- Hadoop RPC and IPC paths use `ObjectWritable`, `Writable`, and related factories for polymorphic request/response payloads.
- SequenceFile and MapFile users integrate with `FileSystem`, compression codecs, progress callbacks, and raw comparators.
- HDFS and filesystem clients use `IOUtils` for safe stream copying, reading, skipping, close suppression, and `fsync` operations.
- Configuration-driven features use `DefaultStringifier` and `WritableUtils` to store serialized objects or string arrays in `Configuration`.
- Compression-aware readers and writers use `CompressionCodecFactory` to infer codecs from path suffixes and configuration, then obtain stream wrappers or pooled codec instances.
- Split-aware input formats depend on `BZip2Codec` and `SplitCompressionInputStream` style APIs for compressed file splitting.
- Direct decompression integrates with consumers that operate on `ByteBuffer` rather than heap byte arrays.

## Deprecation and Compatibility Signals

- `org.apache.hadoop.io.Closeable` is deprecated in favor of `java.io.Closeable`.
- `BytesWritable.get()` and `BytesWritable.getSize()` are deprecated in favor of `getBytes()` and `getLength()`.
- Several legacy `SequenceFile.createWriter(...)` overloads are deprecated in favor of `createWriter(Configuration, Writer.Option...)`.
- `WritableUtils.cloneInto(...)` is deprecated in favor of `ReflectionUtils.cloneInto`.
- These deprecations indicate migration pressure but also compatibility obligations because the APIs remain present in the 3.1.2 surface.

## Risks and Edge Cases

- Raw byte access in `BytesWritable` and `Text` can expose unused backing capacity. Callers that ignore logical length can compare, hash, or persist garbage bytes.
- Writable deserialization mutates existing instances. Reusing an instance without clearing all fields can leak previous state if an implementation is incomplete.
- `ObjectWritable` and `GenericWritable` depend on class names and classloaders. Missing classes, incompatible declared classes, or unsafe polymorphic inputs can fail at runtime.
- Writable binary compatibility is fragile. Any change to field order, vint encoding, or comparator behavior can break stored files or distributed sort compatibility.
- Compression pooling requires disciplined return of leased objects; leaked compressors/decompressors can increase native memory pressure and distort diagnostics.
- `Compressor.end()` and `Decompressor.end()` discard pending input/state. Calling them too early can corrupt stream processing, while failing to call/return resources can leak resources.
- `Decompressor.finished()` with positive `getRemaining()` represents concatenated stream data. Readers that treat `finished()` alone as EOF can drop remaining data.
- Deprecated SequenceFile writer overloads may hide configuration defaults differently from the newer option API, so compatibility tests should cover legacy creation paths.
- `MapFile.fix(...)` is a repair utility, but rebuilding indexes from corrupt data can still preserve corrupted ordering or values if the data file itself is invalid.
- `Text` UTF-8 helpers include validation and maximum-length overloads because unbounded or invalid text inputs are a denial-of-service and correctness risk.
- This XML records signatures, not implementation. Any implementation-specific behavior, synchronization, performance characteristic, or native codec fallback must be confirmed in Java source and tests.

## Test Signals

Useful tests implied by this chunk include:

- Round-trip serialization tests for each primitive writable, `BytesWritable`, `Text`, `MD5Hash`, arrays, maps, `EnumSetWritable`, `GenericWritable`, and `ObjectWritable`.
- Comparator parity tests where object comparison equals raw serialized-byte comparison for supported writable keys.
- Boundary tests for vint/vlong encodings, including negative values, first-byte size decoding, range checks, and skip behavior.
- `BytesWritable` and `Text` tests for capacity versus logical length, copying versus raw array exposure, append/set/clear behavior, UTF-8 validation, and maximum string length enforcement.
- SequenceFile tests for old and new writer creation APIs, compression type defaults, sync interval behavior, metadata, and raw writer variants.
- MapFile/BloomMapFile tests for rename/delete/fix behavior, index/data/bloom file presence, sparse lookup, and corrupt index recovery.
- IOUtils tests for copy close semantics, exact byte reads, full skipping, cleanup exception suppression, socket close handling, channel short writes, fsync on files/directories, and exception wrapping.
- Compression tests for codec discovery by config/service loader, suffix lookup, removing suffixes, pool lease/return counts, stream close/finish/reset behavior, dictionary handling, concatenated stream processing, and direct `ByteBuffer` decompression.
- Split bzip2 tests for `createInputStream(..., start, end, READ_MODE)` and split-boundary behavior, with follow-up coverage from the next chunk for the remainder of `SplitCompressionInputStream`.

## Chunk Boundary Notes

- `ArrayWritable` is already in progress at line 17951; its earlier declaration and constructors are in the previous chunk, while this chunk includes additional constructors and all listed methods.
- `SplitCompressionInputStream` is only partially visible by line 24252; this chunk captures its constructor and protected start/end mutators, but not the full class end or any later split-compression interfaces.
- The next merge lane should combine this report with adjacent chunks before producing a final per-file research document for the full JDiff XML file.
