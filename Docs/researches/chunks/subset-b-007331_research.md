# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 12317-18734

## Scope and Purpose

This chunk is part of Hadoop 0.20.2's JDiff XML API snapshot, not implementation source. It records public/protected API surface, signatures, inheritance, deprecation metadata, exceptions, fields, and Javadoc excerpts for a large section of `org.apache.hadoop.io`, `org.apache.hadoop.io.compress`, `org.apache.hadoop.io.compress.bzip2`, `org.apache.hadoop.io.compress.zlib`, and the beginning of `org.apache.hadoop.io.file.tfile`.

The chunk starts in the middle of `org.apache.hadoop.io.SequenceFile.Reader` and ends in the middle of `org.apache.hadoop.io.file.tfile.TFile.Reader.Scanner.Entry`. The merge lane should treat this as a partial XML range that needs neighboring chunks for complete per-file/package context.

## API Areas Covered

### SequenceFile Reader/Sorter/Writer

The visible `SequenceFile.Reader` methods expose read-side metadata and cursor operations for sequence-format key/value files:

- Type and file metadata: `getKeyClassName()`, `getKeyClass()`, `getValueClassName()`, `getValueClass()`, `isCompressed()`, `isBlockCompressed()`, `getCompressionCodec()`, `getMetadata()`.
- Record access: `next(Writable key)`, `next(Writable key, Writable val)`, `next(Object key)`, `getCurrentValue(Writable)`, `getCurrentValue(Object)`, and raw access with `createValueBytes()`, `nextRaw(DataOutputBuffer, ValueBytes)`, `nextRawKey(DataOutputBuffer)`, `nextRawValue(ValueBytes)`.
- Positioning: `seek(long)`, `sync(long)`, `syncSeen()`, `getPosition()`.
- Lifecycle: synchronized `close()`.

`SequenceFile.Reader.next(DataOutputBuffer)` is deprecated in favor of `nextRaw(DataOutputBuffer, SequenceFile.ValueBytes)`. The reader contract distinguishes exact positions returned by `SequenceFile.Writer.getLength()` from arbitrary positions that must use `sync(long)`.

`SequenceFile.Sorter` describes sorting and merging of sequence files using either key/value classes or a `RawComparator`. It exposes merge fan-in and memory controls (`setFactor`, `getFactor`, `setMemory`, `getMemory`), progress reporting (`setProgressable`), sort entry points, several merge overloads, `cloneFileAttributes`, and `writeFile`. Its Javadoc stresses efficient `Writable.readFields(DataInput)` implementations for sort performance.

`SequenceFile.Sorter.RawKeyValueIterator` is the raw merge iterator contract: `next()` sets up current key/value, `getKey()` returns a `DataOutputBuffer`, `getValue()` returns `SequenceFile.ValueBytes`, `getProgress()` exposes byte progress, and `close()` releases streams.

`SequenceFile.Sorter.SegmentDescriptor` models a merge segment with offset, length, and path. It supports sync checking, input preservation/deletion control, raw key/value advancement, key retrieval, ordering via `Comparable`, and overridable cleanup. The default cleanup closes the file handle and deletes the file unless preservation is selected.

`SequenceFile.ValueBytes` abstracts raw sequence values, with methods to write uncompressed bytes, write already-compressed bytes, and report stored size. `writeCompressedBytes` explicitly does not compress uncompressed values.

`SequenceFile.Writer` exposes constructors for file creation with filesystem, configuration, key/value classes, optional replication/block-size/progress/metadata parameters. It exposes class/codec metadata, `sync()`, synchronized `close()`, synchronized typed and object `append`, `appendRaw`, and synchronized `getLength()`. Protected serializer fields are part of the public XML surface: `keySerializer`, `uncompressedValSerializer`, and `compressedValSerializer`.

### SetFile and SortedMapWritable

`SetFile` is a file-backed set of keys implemented as a `MapFile` specialization. The reader extends `MapFile.Reader` with constructors using a set path and optional `WritableComparator`, plus `seek`, `next`, and `get` for `WritableComparable` keys. The writer extends `MapFile.Writer`; the old constructor without `Configuration` is deprecated, and active constructors include `Configuration`, `FileSystem`, path/name, element class or comparator, and `SequenceFile.CompressionType`. `append(WritableComparable)` requires keys to be strictly increasing.

`SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap`. The XML exposes default and copy constructors and the normal sorted-map operations (`comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`) plus mutable map operations and `Writable` serialization (`readFields`, `write`). Keys are `WritableComparable`; values are `Writable`.

### String, Text, UTF8, VersionedWritable, and Variable Integer Writables

`Stringifier` is a `Closeable` object/string conversion contract with `toString(Object)`, `fromString(String)`, and `close()`, all IOException-capable.

`Text` is the primary UTF-8 byte-backed Hadoop string type. It extends `BinaryComparable` and implements `WritableComparable`. Constructors accept no args, `String`, `Text`, and byte arrays. Key behavior:

- Raw storage: `getBytes()` returns the backing bytes and `getLength()` gives the valid byte length.
- UTF-8 traversal/search without creating Java strings: `charAt(int)`, `find(String)`, `find(String, int)`.
- Mutation: `set(String)`, `set(byte[])`, `set(Text)`, `set(byte[], int, int)`, `append(byte[], int, int)`, and `clear()`.
- Serialization: `readFields(DataInput)`, `write(DataOutput)`, and static `skip(DataInput)`.
- Encoding helpers: static `decode` overloads with optional replacement behavior, static `encode` overloads, `readString`, `writeString`, `validateUTF8`, `bytesToCodePoint(ByteBuffer)`, and `utf8Length(String)`.
- Equality/hash and `toString()` are public API.

The `Text` Javadoc states its length is serialized with zero-compressed encoding and that it includes byte-level comparison and UTF-8 validation utilities. `Text.Comparator` extends `WritableComparator` with a raw byte `compare` optimized for `Text`.

`TwoDArrayWritable` is a `Writable` wrapper for a matrix of instances of a specified class. It provides constructors with value class and optional initial matrix, `toArray`, `set`, `get`, `readFields`, and `write`.

`UTF8` is deprecated and replaced by `Text`, but remains in the public API. It implements `WritableComparable` with constructors from `String`/`UTF8`, mutable setters, raw byte/length access, read/write/skip, compare/equality/hash/toString, and static byte/string helpers. `UTF8.Comparator` provides a raw `WritableComparator`.

`VersionedWritable` is a base `Writable` that embeds version checking. Subclasses provide `getVersion()`. Its `write` and `readFields` participate in version serialization/validation. `VersionMismatchException` records expected/found version bytes and has `toString()`.

`VIntWritable` and `VLongWritable` are `WritableComparable` wrappers for variable-length encoded integers/longs. They expose default/value constructors, `set`, `get`, read/write, equals/hash, `compareTo`, and `toString`. These integrate with the zero-compressed integer utilities documented later in `WritableUtils`.

### Writable Core, Factories, Names, and Utilities

`Writable` is the base Hadoop serialization interface with `write(DataOutput)` and `readFields(DataInput)`. The documentation emphasizes compact, high-speed serialization for network and persistent storage, and asks implementations to provide no-arg constructors because deserialization commonly constructs an empty instance and then calls `readFields`.

`WritableComparable` combines `Writable` and `Comparable`; the docs identify it as the typical MapReduce key interface.

`WritableComparator` implements `RawComparator` for `WritableComparable`s. It has protected constructors, a synchronized static comparator registry (`get`, `define`), `getKeyClass()`, `newKey()`, object comparison, typed `WritableComparable` comparison, and raw byte comparison. Static helpers parse primitive values from byte arrays (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`) and provide `compareBytes`/`hashBytes`. The raw `compare(byte[],...)` hook is the main performance extension point for sort-intensive paths.

`WritableFactories` is a synchronized registry for `WritableFactory` instances, used so non-public writables can be constructed by `ObjectWritable`. It supports `setFactory`, `getFactory`, and `newInstance` with or without `Configuration`. `WritableFactory` itself has only `newInstance()`.

`WritableName` maps writable classes to stable external names and aliases. It supports synchronized `setName`, `addName`, `getName`, and `getClass(name, conf)`. Its role is preserving compatibility when writable implementation classes are renamed.

`WritableUtils` is a final utility class. It provides compressed byte-array and string read/write/skip helpers, string-array helpers, `displayByteArray`, serialization-based `clone`, deprecated `cloneInto` in favor of `ReflectionUtils.cloneInto`, variable-length integer/long encoding and decoding (`writeVInt`, `writeVLong`, `readVInt`, `readVLong`, `isNegativeVInt`, `decodeVIntSize`, `getVIntSize`), enum read/write by string name, `skipFully`, and `toByteArray(Writable[])`.

### Compression Package

`BlockCompressorStream` and `BlockDecompressorStream` adapt `CompressorStream`/`DecompressorStream` for block-based codecs. The compressor writes blocks containing uncompressed length plus length-prefixed compressed chunks; the decompressor reads corresponding block data and supports `resetState`.

`BZip2Codec` implements `CompressionCodec` but only supports stream creation without explicit compressor/decompressor objects. Methods that require `Compressor` or `Decompressor` instances, including `createCompressor`, `createDecompressor`, and the overloads accepting these objects, are documented as unsupported and throw `UnsupportedOperationException`. The default extension is `.bz2`.

`CodecPool` is a static pool for reusable codec resources: `getCompressor`, `getDecompressor`, `returnCompressor`, and `returnDecompressor`.

`CompressionCodec` defines the generic codec contract: output stream creation, input stream creation, compressor/decompressor type discovery, compressor/decompressor construction, and default extension discovery.

`CompressionCodecFactory` is configuration-driven. It constructs from `Configuration`, exposes codec class listing and setting, resolves a codec for a `Path`, removes codec suffixes, supports a diagnostic `main`, and has an Apache Commons Logging `LOG` field.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases. Input streams wrap protected `InputStream in`, close, read single bytes, and reset state. Output streams wrap protected final `OutputStream out`, close/flush, declare abstract byte-array `write`, `finish`, and `resetState`. The output stream intentionally makes byte-array write abstract to avoid leakage to the underlying stream.

`Compressor` and `Decompressor` are Deflater/Inflater-like state machines. Compressor methods include `setInput`, `needsInput`, `setDictionary`, byte counters, `finish`, `finished`, `compress`, `reset`, and `end`. Decompressor mirrors input/dictionary/finished/decompress/reset/end plus `needsDictionary`. The documented control flow is caller-driven: provide input when `needsInput()` is true, drain with `compress`/`decompress`, call `finish` for compression termination, and call `reset` for reuse or `end` for final disposal.

`CompressorStream` and `DecompressorStream` own protected compressor/decompressor instances, buffers, and closed/eof flags. They implement write/read loops, compression/decompression helpers, finish/reset/close, skip/available for decompression, and disabled mark/reset behavior. Protected constructors allow subclasses to directly set the underlying stream.

`DefaultCodec` implements both `Configurable` and `CompressionCodec`; `GzipCodec` extends it and supplies gzip-specific stream/compressor/decompressor behavior. `GzipCodec.GzipInputStream` and `GzipCodec.GzipOutputStream` bridge Java gzip/deflater streams into Hadoop `CompressionInputStream`/`CompressionOutputStream`, overriding read/write/close/finish/flush/skip/reset operations.

### BZip2 and Zlib Adapters

`BZip2Constants` is a public historical constants interface. It includes algorithm constants and a public static `rNums` array; the Javadoc explicitly marks this as a FIXME because public mutable array access could be modified by malicious code.

`BZip2DummyCompressor` and `BZip2DummyDecompressor` implement the compressor/decompressor interfaces as dummy adapters for BZip2, matching the earlier `BZip2Codec` limitation.

`CBZip2InputStream` and `CBZip2OutputStream` are raw bzip2 stream implementations without file header characters. They expose read/write/finish/flush/close behavior, output block-size helpers, and many protected compression constants. Their documentation warns about large memory use, encourages early close to release memory, says instances are not thread-safe, and notes a TODO to update to BZip2 1.0.1. `CBZip2OutputStream.chooseBlockSize(long)` helps select block sizes, and output construction supports default 900k or specified block size.

`BuiltInZlibDeflater` and `BuiltInZlibInflater` wrap `java.util.zip.Deflater`/`Inflater` to implement Hadoop `Compressor`/`Decompressor`, with synchronized `compress`/`decompress`.

`ZlibCompressor` and `ZlibDecompressor` are Hadoop zlib implementations. Both expose synchronized state operations for input, dictionary, finish/finished, compression/decompression, byte counters, reset, and end. Constructors allow explicit compression level/strategy/header/direct-buffer size for compressors and header/direct-buffer size for decompressors.

`ZlibCompressor.CompressionHeader` supports `NO_HEADER`, `DEFAULT_HEADER`, and `GZIP_FORMAT`; `ZlibDecompressor.CompressionHeader` also supports `AUTODETECT_GZIP_ZLIB`. `CompressionLevel` has `NO_COMPRESSION`, `BEST_SPEED`, `BEST_COMPRESSION`, and `DEFAULT_COMPRESSION`. `CompressionStrategy` has `FILTERED`, `HUFFMAN_ONLY`, `RLE`, `FIXED`, and `DEFAULT_STRATEGY`.

`ZlibFactory` chooses native or built-in zlib implementations from `Configuration`. It checks native availability and returns compressor/decompressor classes or instances.

### TFile Start

`ByteArray` is a final adapter that wraps a `BytesWritable`, a whole `byte[]`, or a byte-array slice as a `RawComparable`, exposing `buffer`, `offset`, and `size`. `RawComparable` defines the same byte-range access contract and delegates actual ordering to external `RawComparator` implementations.

`MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are IOException subclasses for TFile metadata block access failures.

`TFile` is a type-less key/value container. Keys are bytes limited to 64KB; value length is practically disk-limited. Features include block compression, named metadata blocks, sorted or unsorted keys, and seek by key or file offset. Public constants name compression algorithms (`gz`, `lzo`, `none`) and comparators (`memcmp`, Java class prefix). Public static helpers create comparators, list supported compression algorithms, and dump file info via `main`.

`TFile.Reader` wraps an `FSDataInputStream`, file length, and `Configuration`. It is `Closeable` and provides comparator metadata, sorted status, entry count, first/last keys, entry comparator, raw comparator, named metadata block streams, near-record/key lookup by offset, and scanner creation over whole file, byte ranges, key ranges, and record-number ranges. Older scanner overloads are deprecated in favor of explicit `createScannerByKey` overloads.

`TFile.Reader.Scanner` is a closeable cursor over a range. It can be constructed over byte offsets or raw key bounds. Cursor operations include `seekTo`, `lowerBound`, `upperBound`, `rewind`, `seekToEnd`, `advance`, `atEnd`, `entry`, and `getRecordNum`. The docs repeatedly state that entries returned by previous `entry()` calls are invalidated by cursor movement or close.

The chunk ends inside `TFile.Reader.Scanner.Entry`. Visible entry methods include `getKeyLength`, combined `get(BytesWritable key, BytesWritable value)`, key copying to `BytesWritable` or user byte arrays, `writeKey(OutputStream)`, `getKeyStream()`, `getValue(BytesWritable)`, `writeValue(OutputStream)`, `getValueLength()`, and `getValue(byte[])`. Value access is single-pass: the value is not cached and repeated value reads without moving the cursor cause exceptions. `getValueLength()` requires a separate `isValueLengthKnown()` test, but that method is outside this chunk.

## Control Flow and State Behavior

The XML describes several stateful cursor and stream contracts:

- `SequenceFile.Reader` is synchronized for close, class resolution, value retrieval, typed next calls, raw next, seek, sync, and position. State includes current file offset, last-read key/value, sync-marker status, compression/metadata configuration, and open stream lifecycle.
- `SequenceFile.Writer` is synchronized for close, appends, raw appends, and length retrieval. Writer state includes serializers, compression codec, sync points, current output length, and file metadata.
- `SequenceFile.Sorter` controls a multi-stage flow: read input segments, optionally delete inputs, sort/merge through `RawKeyValueIterator`, then write records to a cloned or supplied writer. Segment descriptors own file-handle and temporary-file cleanup behavior.
- Writable classes serialize and deserialize themselves through `DataOutput`/`DataInput`, with no external schema beyond class name/name alias and encoded byte layout.
- Compression streams are pull/push state machines around reusable compressor/decompressor instances. Callers and streams must honor `needsInput`, `finished`, `resetState`, `close`, and `end` semantics.
- TFile readers own an indexed, compressed, seekable file view. Scanners own an implicit cursor; entries are views into the scanner and are invalidated by cursor movement. Entry value data is stream-like and only readable once per cursor position.

## Persistence and Compatibility

This chunk is dominated by persistent binary compatibility contracts:

- `Writable`, `WritableComparable`, `WritableComparator`, `WritableFactories`, and `WritableName` define how Hadoop serializes objects, instantiates them during deserialization, compares raw serialized keys, and preserves class-name compatibility after renames.
- `Text`, `UTF8`, `VIntWritable`, `VLongWritable`, and `WritableUtils` document precise byte encodings such as UTF-8 with zero-compressed length and variable-length integer/long encodings.
- `SequenceFile.Reader`/`Writer` and `SetFile` APIs govern on-disk sequence/set/map file compatibility, including metadata, compression type, sync points, raw key/value paths, and sorted key invariants.
- Compression codecs and streams define compressed bytes emitted into sequence files and TFiles, including block-compression wrappers and gzip/bzip2/zlib format variants.
- TFile declares persistent layout expectations: typed as bytes, optional sorting, block compression, metadata blocks, indexes proportional to block counts, and configurable chunk/buffer sizes.

## Dependencies and Integration Points

The APIs integrate with:

- Hadoop filesystem/configuration: `FileSystem`, `Path`, `FSDataInputStream`, `Configuration`.
- Hadoop IO primitives: `Writable`, `WritableComparable`, `WritableComparator`, `RawComparator`, `BytesWritable`, `DataOutputBuffer`, `SequenceFile.Metadata`.
- Hadoop utility hooks: `Progress`, `Progressable`, `ReflectionUtils`, `Configurable`.
- Java IO and NIO: `Closeable`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, `ByteBuffer`, `CharacterCodingException`, `MalformedInputException`.
- Java compression: `Deflater`, `Inflater`, gzip stream adapters, and zlib wrappers.
- Logging and diagnostics: `CompressionCodecFactory.LOG` and `main` methods on codec/TFile utilities.
- MapReduce sorting paths: `WritableComparable` keys, raw comparators, `SequenceFile.Sorter`, and efficient `readFields`.

## Risks and Edge Cases

- This is JDiff XML, so it records signatures and docs, not implementation bodies. Control-flow details are inferred from API contracts and Javadoc.
- The chunk starts and ends mid-API; neighboring chunks are required for complete `SequenceFile.Reader` and `TFile.Reader.Scanner.Entry` coverage.
- Public deprecations visible here require migration care: `SequenceFile.Reader.next(DataOutputBuffer)`, `SetFile.Writer(FileSystem, String, Class)`, `UTF8`, `WritableUtils.cloneInto`, and older TFile scanner overloads.
- `SetFile.Writer.append` requires strictly increasing keys; violating this breaks sorted set/map-file semantics.
- Raw comparator performance is critical; default `WritableComparator.compare(byte[],...)` deserializes objects and can allocate heavily.
- `WritableName` aliases and `WritableFactories` are compatibility-sensitive global registries; incorrect mappings can make existing persistent files unreadable.
- BZip2 codec object-based compressor/decompressor APIs are documented as unsupported and throw `UnsupportedOperationException`.
- `BZip2Constants.rNums` is public mutable array state flagged as a security risk in the docs.
- BZip2 streams warn about high memory usage, need early close to release memory, and are not thread-safe.
- TFile readers use `FSDataInputStream.seek()+read()` rather than true multi-threaded positioned reads; multiple scanners over one reader serialize actual I/O.
- TFile scanner entries become invalid after cursor movement/close; value data is not cached and repeated value reads at one cursor position throw exceptions.
- `Text.getBytes()` and `UTF8.getBytes()` expose raw backing arrays where only the declared length is valid; callers must not treat the full array as logical content.
- UTF-8 helpers have replacement-vs-exception modes; tests must cover malformed input and buffer position side effects from `bytesToCodePoint`.

## Test Signals

Useful validation targets for implementation or compatibility tests derived from this API chunk:

- SequenceFile round trips for uncompressed, record-compressed, and block-compressed files; validate metadata, codec reporting, raw reads, sync/seek semantics, and `getLength()` positions.
- SequenceFile sorter tests for custom `RawComparator`, merge fan-in, memory limits, progress reporting, temporary segment cleanup, and delete-input behavior.
- SetFile writer/reader tests for strict key ordering, comparator-based lookup, deprecated constructor compatibility, and compression type coverage.
- Writable serialization tests for no-arg construction, `WritableFactories` custom factories, `WritableName` alias lookup, `VersionedWritable` mismatch handling, and raw comparator equivalence to object comparison.
- Text/UTF8 tests for raw byte length, append/set slice behavior, malformed UTF-8 replacement and exception modes, zero-compressed length serialization, `skip`, `find`, `charAt`, and comparator ordering.
- WritableUtils tests for compressed byte/string arrays, enum read/write, `skipFully`, variable-length integer size/sign boundaries, and serialization clone behavior.
- Compression tests for `CodecPool` reuse, `CompressionCodecFactory` path suffix resolution, stream `finish` vs `close`, reset behavior, gzip bridge behavior, and unsupported BZip2 compressor/decompressor methods.
- BZip2/zlib tests for block-size boundaries, memory/resource close behavior, header variants, native zlib factory fallback, byte counters, and dictionary/needs-input state transitions.
- TFile tests for sorted/unsorted modes, metadata block duplicate/missing exceptions, byte/key/record scanner ranges, scanner cursor invalidation, single-pass value access, value-length-known handling, and compression algorithms `none`, `lzo`, and `gz`.
