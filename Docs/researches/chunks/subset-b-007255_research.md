# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.22.0.xml lines 12016-18218

## Scope and Purpose

This chunk is a JDiff XML API descriptor for Hadoop Core 0.22.0, not executable Java source. It captures the public/protected API surface for the tail of `org.apache.hadoop.io` and the beginning of `org.apache.hadoop.io.compress`. The described code is Hadoop's binary serialization, ordered file, text encoding, comparator, and compression plumbing used by MapReduce, RPC, filesystem data formats, and command-line utilities.

The chunk starts inside `IOUtils.copyBytes` overloads and finishes inside `GzipCodec`, so it should be merged with adjacent chunks for whole-file package boundaries. Within this slice, the main themes are:

- stream copy/cleanup helpers;
- primitive and compound `Writable` implementations;
- sorted persistent file containers (`MapFile`, `SetFile`, `SequenceFile`);
- raw comparators and writable factory/clone utilities;
- UTF-8 byte-oriented text handling;
- compression codec abstractions and stream wrappers.

## Important APIs, Types, and Functions

### `org.apache.hadoop.io` utilities and primitive writables

- `IOUtils` methods visible at the start of the chunk include `copyBytes(InputStream, OutputStream, Configuration[, boolean])`, `readFully`, `skipFully`, `cleanup`, `closeStream`, and `closeSocket`. They centralize stream transfer, exact-byte reads/skips, and best-effort cleanup that deliberately suppresses cleanup-time `IOException`s.
- `IOUtils.NullOutputStream` is a `/dev/null` style `OutputStream` with byte-array and single-byte `write` overloads.
- `LongWritable`, `VIntWritable`, and `VLongWritable` are mutable numeric `WritableComparable` wrappers. They expose default/value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `LongWritable.Comparator` and `LongWritable.DecreasingComparator` extend `WritableComparator` to compare serialized longs directly, including descending order.
- `NullWritable` is a singleton-like marker value with `get`, no-op serialization, constant comparison/equality behavior, and a raw comparator.
- `MultipleIOException` groups multiple `IOException` instances via `getExceptions` and static `createIOException`.

### Persistent ordered files

- `MapFile` models a directory-backed sorted key/value map with public constants `INDEX_FILE_NAME` and `DATA_FILE_NAME`, plus static `rename`, `delete`, `fix`, and `main`. Its Javadoc records the important persistence model: a map directory contains a full `data` file and a smaller in-memory `index` file containing a fraction of sorted keys.
- `MapFile.Reader` is a synchronized, closeable lookup/scan API over a `MapFile`. It has modern construction via `Path`, `Configuration`, and `SequenceFile.Reader.Option[]`, plus deprecated `FileSystem/String` constructors. It exposes key/value class accessors, `open`, `createDataFileReader`, `reset`, `midKey`, `finalKey`, `seek`, `next`, `get`, two `getClosest` overloads, and `close`.
- `MapFile.Writer` is the append side. It has many deprecated constructor forms plus an option-based constructor, static options for key class, comparator, value class, compression, and progress callback, index interval accessors/mutators, `append`, and `close`. Appends require sorted keys, and the index interval controls sparse index density.
- `SetFile`, `SetFile.Reader`, and `SetFile.Writer` specialize `MapFile` as a key-only ordered set. The writer appends strictly increasing keys; the reader supports `seek`, `next`, and exact `get`.

### Writable maps, object wrappers, and factories

- `MapWritable` and `SortedMapWritable` extend `AbstractMapWritable` and implement `Map`/`SortedMap` style APIs. They expose copy constructors, map mutation/query methods, and `readFields`/`write`. These types persist heterogeneous writable keys and values by pairing data with class-id metadata inherited from `AbstractMapWritable`.
- `ObjectWritable` wraps arbitrary declared classes for Hadoop serialization/RPC. It records a declared class and instance value, has `get`, `getDeclaredClass`, `set`, `toString`, instance `readFields`/`write`, static `writeObject` overloads with optional declared class/configuration, static `readObject` overloads, `loadClass`, and `Configurable` methods.
- `Writable`, `WritableComparable`, `RawComparator`, `WritableComparator`, `WritableFactory`, `WritableFactories`, and `WritableUtils` define the serialization comparison substrate. `WritableComparator` provides class-specific comparator registration/lookup, object comparison fallback, optimized raw byte comparison, byte hashing, and primitive decoders such as `readInt`, `readLong`, `readVLong`, and `readVInt`.
- `WritableFactories` has synchronized `setFactory`/`getFactory` and `newInstance` helpers so non-public writable classes can be instantiated during deserialization.
- `WritableUtils` covers compressed byte/string arrays, normal string arrays, enum string serialization, writable cloning via serialization, variable-length integer/long encoding and decoding, full skipping, conversion of writables to byte arrays, and bounded `readStringSafely`.

### Hashing and text

- `MD5Hash` is a 16-byte `WritableComparable` digest wrapper. It can be built from strings or bytes, read/written from data streams, computed from byte arrays or streams via static `digest` overloads, exposed as raw bytes, summarized via `halfDigest`/`quarterDigest`, compared, stringified, and parsed back with `setDigest`. `MD5Hash.Comparator` compares serialized digests.
- `Text` is Hadoop's mutable UTF-8 byte string and extends `BinaryComparable`. It stores raw UTF-8 bytes plus a byte length, supports construction from `String`, `Text`, or bytes, byte copying/raw access, byte-position `charAt` and `find`, multiple `set` overloads, `append`, `clear`, `toString`, serialization, equality/hash, static UTF-8 `decode`/`encode`, `readString`/`writeString`, validation, code-point extraction, and `utf8Length`.
- `Text.Comparator` and legacy `UTF8.Comparator` provide raw byte comparators for UTF-8 values.
- `Stringifier<T>` is a closeable serializer-to-string abstraction with `toString`, `fromString`, and `close`.

### SequenceFile

- `SequenceFile` is the main flat binary key/value persistence API. Static methods get/set default compression type in `Configuration` and create `Writer` instances. Most older `createWriter` overloads are explicitly deprecated in favor of `createWriter(Configuration, Writer.Option...)`.
- `SequenceFile.CompressionType` is an enum for the file compression modes documented in this chunk: uncompressed, record-compressed, and block-compressed.
- `SequenceFile.Metadata` is a `TreeMap<Text,Text>` wrapper with constructors, `get`, `set`, `getMetadata`, serialization, equality, hash, and string conversion.
- `SequenceFile.Reader` has constructors for option-based, file-based, and stream/range-based reads. Static options include `file`, `stream`, `start`, `length`, and `bufferSize`. It exposes file/class/compression/metadata introspection, object and writable `next` APIs, raw key/value reads, `createValueBytes`, `seek`, `sync`, `syncSeen`, `getPosition`, `getCurrentValue`, `close`, and `toString`.
- `SequenceFile.Writer` is closeable and supports option-based construction through static `file`, `bufferSize`, `stream`, `replication`, `blockSize`, `progressable`, `keyClass`, `valueClass`, `metadata`, and `compression` options. It exposes key/value class and codec introspection, `sync`, `append` overloads, `appendRaw`, `getLength`, and synchronized `close`.
- `SequenceFile.Sorter`, `RawKeyValueIterator`, `SegmentDescriptor`, and `ValueBytes` support external sorting and merging of sequence files. The sorter configures merge factor, memory, and progress callbacks; sorts paths; returns raw iterators; merges segments; clones writer attributes; and writes merged output.

### Secure IO

- `SecureIOUtils.openForRead` and `createForWrite` expose owner-aware local file access APIs. They depend on `java.io.File`, `FileInputStream`, `FileOutputStream`, and Unix owner/group validation strings. `AlreadyExistsException` is a nested `IOException` used by creation paths when a target already exists.

### Compression package

- `CompressionCodec` defines the core codec contract: create compression/decompression streams with or without pooled `Compressor`/`Decompressor` instances, report compressor/decompressor classes, create compressor/decompressor instances, and return the default filename extension.
- `CompressionCodecFactory` discovers/configures codecs from `Configuration`, supports `getCodecClasses`/`setCodecClasses`, resolves codecs by `Path` extension or class name, removes suffixes, has a diagnostic `main`, and carries a commons-logging `LOG` field.
- `CodecPool` is a global compressor/decompressor reuse pool with `getCompressor(codec[, conf])`, `getDecompressor(codec)`, `returnCompressor`, and `returnDecompressor`.
- `CompressionInputStream` and `CompressionOutputStream` are base stream wrappers around protected `in`/`out`. They define lifecycle hooks (`resetState`, `finish`), position/seek methods for input, and close/flush/write behavior for output.
- `Compressor` and `Decompressor` model zlib-like state machines: set input/dictionary, check input/dictionary needs, finish/finished state, compress/decompress into caller buffers, report counters/remaining bytes, reset, end, and for compressors, `reinit(Configuration)`.
- `CompressorStream` and `DecompressorStream` adapt those state machines to Java streams. Their protected fields include the codec state object, a byte buffer, and closed/eof flags; methods drive compression/decompression, reset state, close, and ordinary stream reads/writes.
- `BlockCompressorStream` and `BlockDecompressorStream` specialize the stream wrappers for block-based algorithms. The compressor writes uncompressed block lengths followed by one or more length-prefixed compressed chunks; the decompressor reads those blocks back and can reset state.
- `BZip2Codec` implements `SplittableCompressionCodec`. It provides BZip2 input/output streams and a split input stream with start/end offsets plus `READ_MODE`; its compressor/decompressor pooling methods are documented as unsupported/dummy.
- `DefaultCodec` implements `Configurable` and `CompressionCodec`, bridging Hadoop `Configuration` to default compressor/decompressor types and stream creation. `GzipCodec` extends it and overrides output stream creation plus compressor creation/type methods visible in this chunk.

## Control Flow and Data Flow

The JDiff descriptor exposes call contracts rather than method bodies, but the API shapes reveal the key flows:

- Writable serialization is a two-phase contract: producers call `write(DataOutput)`, consumers allocate or factory-create an instance and call `readFields(DataInput)`. Comparators either deserialize objects or use raw byte helpers to avoid allocation.
- `ObjectWritable` adds a dynamic type envelope around that contract: it writes declared class metadata, then value data, and reads by loading classes through `Configuration`-aware logic.
- `MapFile` writes sorted key/value pairs to a data `SequenceFile` and periodically writes keys to an index file. Readers load the sparse index, binary-search/seek near a target key, then scan the data stream to satisfy `seek`, `get`, `next`, and `getClosest`.
- `SetFile` follows the same path but stores only keys, with `NullWritable` or equivalent empty value behavior implied by the set abstraction.
- `SequenceFile.Writer` writes a header with key/value classes, compression flags, codec class, metadata, and sync marker, then records or blocks. `sync` creates seekable recovery points; `getLength` returns positions suitable for reader `seek`.
- `SequenceFile.Reader` parses the header, selects decompression behavior from compression flags and codec metadata, iterates object or raw records, supports split-aligned `sync`, and exposes `syncSeen` for callers that need split boundaries.
- `SequenceFile.Sorter` reads raw key/value segments, compares keys with a `RawComparator`, spills/merges segments under memory and factor limits, and writes sorted sequence output while optionally deleting temporary segment files through `SegmentDescriptor.cleanup`.
- Compression stream flow is state-machine driven. A caller obtains a codec from the factory, may obtain a reusable compressor/decompressor from `CodecPool`, wraps an input/output stream, pushes bytes through `write` or `read`, then calls `finish`/`close` and returns codec state objects to the pool.
- Splittable BZip2 reads use `createInputStream(seekableIn, decompressor, start, end, readMode)` to align with compressed block boundaries and report progress either continuously or at block boundaries.

## State and Persistence Behavior

- `Writable` instances are mutable and stateful; callers are expected to reuse objects in tight loops. `readFields` overwrites object state, so stale state must be cleared or fully replaced by implementations.
- `MapWritable` and `SortedMapWritable` persist both map entries and class mappings, enabling heterogeneous writable maps across process boundaries.
- `Text` stores byte arrays that may have extra capacity beyond `getLength()`. `getBytes()` exposes the backing array, while `copyBytes()` returns exact-size data. This distinction matters for persistence and comparisons.
- `MD5Hash` persists fixed-length 16-byte digest state and exposes string parsing/formatting for stable identifiers.
- `VersionedWritable` writes a version byte before subclass data, and `VersionMismatchException` signals incompatible serialized versions.
- `MapFile` persistence is directory based: `data` is authoritative, `index` is derived/sparse. `fix` can recreate the index from data and returns valid-entry counts or `-1` when no fix is needed.
- `SequenceFile` persistence includes a magic/version header, key/value class names, compression flags, codec class, metadata, sync marker, and one of three record layouts. Block-compressed files batch key lengths, keys, value lengths, and values into separate compressed blocks.
- Compression objects have lifecycle state: input buffers, dictionaries, byte counters, finished flags, and native resources. `reset` reuses state, while `end` releases resources. `CodecPool` preserves reusable instances globally.
- `CompressionInputStream` tracks maximum available data and stream position semantics; `DecompressorStream` tracks eof/closed flags; `CompressorStream` tracks closed state and an internal buffer.

## Dependencies and Integration Points

- Core Java dependencies include `java.io` streams/data streams/files, `java.net.Socket`, `java.security.MessageDigest`, `java.nio.ByteBuffer`, `java.util` collections, `java.lang.Enum`, and `Comparable`.
- Hadoop dependencies include `Configuration`, `Configurable`, `FileSystem`, `Path`, `FSDataInputStream`, `FSDataOutputStream`, `Progressable`, `Progress`, `ReflectionUtils`, `BinaryComparable`, `DataOutputBuffer`, serializer interfaces, and compression interfaces.
- Commons Logging appears in `IOUtils.cleanup` and `CompressionCodecFactory.LOG`.
- `SequenceFile` and `MapFile` integrate tightly with Hadoop filesystem implementations, MapReduce intermediate/output storage, sorted data maintenance, split processing, and compression codec configuration.
- `WritableComparator.define`, `WritableFactories.setFactory`, `CompressionCodecFactory.setCodecClasses`, and `CodecPool` are global or configuration-backed extension points. Incorrect registration can affect many readers/writers in the same JVM.
- Deprecated constructors and factory overloads preserve compatibility with older Hadoop APIs while steering new code to option-based `Reader`/`Writer` construction.

## Risks and Edge Cases

- The source is an API XML snapshot. It omits implementation details such as exact validation, synchronization internals, and exception paths; final research for the whole source should merge adjacent chunks and, if needed, compare with Java source.
- Many APIs are mutable and reusable for performance. Bugs often come from retaining references to reused `Writable`, `Text`, raw byte buffers, compressor input buffers, or exposed backing arrays.
- `IOUtils.copyBytes` overloads differ in whether they close streams. Misusing the close flag can leak streams or close caller-owned streams unexpectedly.
- `WritableUtils` variable-length integer encoding is wire-format critical. Boundary values around one-byte ranges, negative values, and malformed first bytes are compatibility-sensitive.
- `readStringSafely` only reads the vint when encoded length is invalid, leaving subsequent bytes for caller handling; callers must account for stream position after exceptions.
- `MapFile.Writer` and `SetFile.Writer` require sorted/strictly increasing keys. Appending out-of-order keys can corrupt lookup assumptions.
- `MapFile` index files are memory-resident on read. Large keys or a small index interval can create high heap pressure.
- `SequenceFile` has multiple legacy writer constructors and compression modes. Interoperability depends on preserving header metadata, sync positions, and raw value behavior across all modes.
- `SequenceFile.Writer.getLength()` may return a synchronized block position rather than the exact last appended key location under block compression; split/seek callers must accept reading an earlier key.
- `SequenceFile.Sorter` performance depends heavily on raw comparator efficiency and `Writable.readFields` avoiding allocations.
- Compression pooling requires disciplined return/reset/end behavior. Returning an object still referenced by a stream or failing to return/reset pooled native codecs can cause data corruption, leaks, or cross-call contamination.
- BZip2 codec methods with compressor/decompressor arguments are explicitly documented as unsupported in this version, despite the generic `CompressionCodec` interface requiring them.
- Secure file APIs depend on platform ownership semantics; behavior can differ across local filesystems, Unix permissions, and unsupported platforms.

## Test Signals

Useful tests for this API surface should include:

- Round-trip serialization tests for `LongWritable`, `VIntWritable`, `VLongWritable`, `NullWritable`, `MD5Hash`, `Text`, `MapWritable`, `SortedMapWritable`, `ObjectWritable`, `VersionedWritable`, and metadata maps.
- Comparator parity tests proving raw `WritableComparator` results match object `compareTo`, including `LongWritable.DecreasingComparator`, `Text.Comparator`, `MD5Hash.Comparator`, and boundary byte encodings.
- `WritableUtils` boundary tests for vint/vlong sizes, negative encodings, malformed/truncated input, compressed byte/string arrays, enum serialization, `skipFully`, and `readStringSafely` maximum-length failures.
- `IOUtils` tests for full-read/full-skip EOF behavior, copy buffer sizing, and stream close/no-close variants.
- `Text` UTF-8 tests for invalid byte sequences, code point boundaries, byte-position `find`, `append`, capacity-vs-length behavior, and static encode/decode validation.
- `MapFile`/`SetFile` tests for ordered append enforcement, sparse index lookup, `getClosest` before/after behavior, index rebuild via `fix`, empty file `midKey`, final key retrieval, and deprecated constructor compatibility.
- `SequenceFile` tests for all compression modes, option-based and deprecated writer construction, metadata persistence, raw/object reads, sync/seek/split behavior, appendRaw, `getLength` under block compression, sorting/merging, and segment cleanup/preserve behavior.
- Compression tests for codec discovery by extension/class name, suffix removal, default extensions, stream close/finish/reset behavior, pool reuse and reinitialization, block-compression framing, BZip2 split reads, and unsupported BZip2 compressor/decompressor operations.
- Secure IO tests for owner/group validation, already-existing output paths, missing files, and platform-specific permission behavior.

## Cross-Chunk Notes

- The chunk begins after earlier `IOUtils.copyBytes` overloads and likely after the start of the `IOUtils` class. Adjacent prior chunk research is needed for full `IOUtils` coverage.
- The chunk ends inside `GzipCodec`; adjacent next chunk research is needed for remaining gzip input/decompressor methods and later compression classes.
- Because this file is generated JDiff XML, whole-file merge should preserve the distinction between documented API contract and implementation behavior inferred from Hadoop conventions.
