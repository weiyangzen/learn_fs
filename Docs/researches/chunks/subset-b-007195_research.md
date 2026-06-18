# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.2.xml lines 18159-24459

## Scope

This chunk is generated JDiff API metadata for Apache Hadoop Common 3.2.2. It starts inside the tail of `org.apache.hadoop.io.DefaultStringifier`, then covers a large part of the public `org.apache.hadoop.io` API, the visible `org.apache.hadoop.io.compress` package, `org.apache.hadoop.io.erasurecode.ECSchema`, empty erasure-code subpackages, and the beginning of `org.apache.hadoop.io.file.tfile` through `Utils.upperBound`.

The source is not implementation code. The research surface is the compatibility contract captured by the XML: public/protected type names, inheritance, implemented interfaces, method signatures, constructors, exceptions, fields, static/final/synchronized markers, deprecation status, and embedded Javadoc. Runtime behavior below is inferred from the API contracts and docs in this slice.

## Purpose

The `org.apache.hadoop.io` section defines Hadoop's core serialization and binary data model. `Writable` and `WritableComparable` are the central serialization contracts used by RPC, MapReduce keys and values, sequence files, map files, and many filesystem-side metadata types. Primitive wrappers such as `IntWritable`, `LongWritable`, `FloatWritable`, `DoubleWritable`, `ShortWritable`, `VIntWritable`, and `VLongWritable` make primitive values serializable, comparable, and usable as Hadoop keys.

The same package also provides higher-level serialization helpers and containers. `Text` is Hadoop's mutable UTF-8 byte-string type. `ObjectWritable`, `GenericWritable`, `MapWritable`, `SortedMapWritable`, `EnumSetWritable`, `TwoDArrayWritable`, and `NullWritable` support polymorphic, collection, enum-set, matrix, and sentinel-value serialization. `WritableComparator`, `WritableFactories`, and `WritableUtils` provide comparator registration, reflective/factory construction, byte-level comparison, compressed string/byte helpers, variable-length integer encoding, enum encoding, and clone/copy helpers.

The file-oriented APIs in this chunk expose legacy Hadoop binary file formats. `SequenceFile` is the flat binary key/value container with record, block, and no-compression modes and sync points. `MapFile` layers an indexed sorted map directory over sequence files, and `SetFile` specializes that pattern for keys only.

The `org.apache.hadoop.io.compress` section defines Hadoop's codec abstraction and stream model. `CompressionCodec`, `Compressor`, `Decompressor`, `CompressionInputStream`, `CompressionOutputStream`, `CompressorStream`, `DecompressorStream`, block stream variants, concrete default/gzip/bzip2 codecs, split-compression support, direct `ByteBuffer` decompression, codec discovery by filename/class/name, and `CodecPool` reuse are the public integration points for compressed input and output.

The erasure-code and TFile sections expose smaller contracts. `ECSchema` is a value object describing codec name, data/parity unit counts, and extra codec options. TFile APIs describe a block-compressed byte key/value container with named metadata blocks, sorted/unsorted modes, seek support, raw byte comparators, compression constants, and utility encodings.

## Important APIs, Types, and Functions

### Stringification and Primitive Writables

- `DefaultStringifier<T>` tail includes `toString(T)`, `fromString(String)`, `close()`, and static `store`, `load`, `storeArray`, and `loadArray` helpers. The docs say values are serialized through Hadoop `Serialization` implementations, base64 encoded, and stored in `Configuration` keys.
- `Stringifier<T>` defines the generic object/string conversion lifecycle: `toString(T)`, `fromString(String)`, and `close()`, all capable of forwarding `IOException`.
- `DoubleWritable`, `FloatWritable`, `IntWritable`, `LongWritable`, and `ShortWritable` implement `WritableComparable` with default and value constructors, `set`, `get`, `readFields(DataInput)`, `write(DataOutput)`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `VIntWritable` and `VLongWritable` mirror the fixed-width integer wrappers but persist values in Hadoop's variable-length integer format.
- `NullWritable` is a singleton `WritableComparable` with no serialized payload. `get()` returns the single instance, and `readFields`/`write` are no-op style hooks for APIs that require a writable key or value type.
- `MD5Hash` is a `WritableComparable` wrapper around a 16-byte digest. It can be constructed empty, from a hex string, or from bytes; it can digest byte arrays, strings, input streams, and arrays of byte arrays; it exposes `halfDigest`, `quarterDigest`, `setDigest`, `getDigest`, `read`, `write`, comparison, and string conversion.

### Writable Containers and Polymorphism

- `Writable` is the base contract: `write(DataOutput)` serializes fields, and `readFields(DataInput)` deserializes them in the same order. The docs emphasize compact, efficient binary serialization.
- `WritableComparable<T>` combines `Writable` with `Comparable<T>` for sortable key types.
- `GenericWritable` is an abstract wrapper for one of a fixed set of writable classes. Subclasses must implement protected `getTypes()` to return the allowed class array; the wrapper carries the selected instance and implements `Configurable`.
- `ObjectWritable` is a polymorphic writable for a `Writable`, `String`, primitive, primitive wrapper, enum, array, or null. It records the declared class, exposes static `writeObject` and `readObject` helpers with optional declared-class and configuration parameters, and has `loadClass(Configuration, String)` for class resolution.
- `MapWritable` extends `AbstractMapWritable` and implements `Map<Writable, Writable>` behavior with `clear`, membership checks, key/value/entry views, `put`, `putAll`, `remove`, `size`, `isEmpty`, `equals`, `hashCode`, `toString`, and explicit `write`/`readFields`.
- `SortedMapWritable` extends `AbstractMapWritable` and exposes `SortedMap` operations such as `comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, and `tailMap`, plus the same writable map serialization surface.
- `EnumSetWritable<E extends Enum<E>>` wraps an `EnumSet`, implements `Writable` and `Configurable`, and preserves `elementType` when the set is null or empty. Constructors and `set(EnumSet, Class)` require an element type for null/empty values.
- `TwoDArrayWritable` stores a two-dimensional array of writable instances for a configured value class and exposes `toArray`, `set`, `get`, `write`, and `readFields`.
- `VersionedWritable` writes and reads a version byte around subclass state and throws `VersionMismatchException` when serialized data does not match the current implementation version.
- `MultipleIOException` wraps a list of `IOException` instances and has `createIOException(List)` to return either a single exception or a combined one.

### IO Utilities, Comparators, and Factories

- `IOUtils` provides stream and channel helpers: `copyBytes` overloads for `InputStream`/`OutputStream` and `Configuration`, bounded copies, `readFully`, `skipFully`, `wrappedReadForCompressedData`, `cleanup`, `cleanupWithLogger`, close helpers for streams/sockets, `writeFully` for `WritableByteChannel` and positioned `FileChannel`, `listDirectory`, `fsync(FileChannel, boolean)`, `fsync(File)`, `wrapException`, and `readFullyToByteArray`.
- `ElasticByteBufferPool` implements `ByteBufferPool` with synchronized `getBuffer(boolean direct, int length)` and `putBuffer(ByteBuffer)`. Its docs state it creates buffers as needed, caches returned buffers, returns the smallest cached buffer large enough for a request, and does not enforce a maximum cache size.
- `WritableComparator` is the central raw comparator implementation for writable keys. It can be obtained with `get(Class)` or `get(Class, Configuration)`, configured, registered via `define(Class, WritableComparator)`, instantiate keys with `newKey`, compare objects or serialized byte ranges, compare/hash raw bytes, and parse primitive or vint/vlong values from byte arrays.
- `RawComparator<T>` adds binary `compare(byte[], int, int, byte[], int, int)` to normal object comparison so sorting code can compare serialized key bytes without object allocation.
- `WritableFactories` maintains class-to-`WritableFactory` registrations and constructs new writable instances with or without a `Configuration`. This supports non-public writable classes and avoids assuming every type has a public no-arg constructor.
- `WritableUtils` supplies compressed byte-array/string helpers, string and string-array serialization, byte-array display, `clone` and `cloneInto` by serializing through buffers, vint/vlong read/write and size helpers, enum read/write by name, `skipFully`, `toByteArray(Writable[])`, and `readStringSafely(DataInput, int)` with maximum encoded-length validation.

### SequenceFile, MapFile, and Text

- `SequenceFile` has public static helpers to get/set default compression type and many `createWriter` overloads. The overloads support writer option objects, filesystem/path-based creation, replication, block size, progress callbacks, metadata, compression type, codec, raw key/value classes, and stream-based writers.
- `SequenceFile.SYNC_INTERVAL` is the documented default byte distance between sync points. The class docs describe sequence files as flat binary key/value files with record compression, block compression, sync markers for seeking/splitting, metadata, and append/read/write patterns.
- `MapFile` exposes static `rename(FileSystem, String, String)`, `delete(FileSystem, String)`, `fix(FileSystem, Path, Class, Class, boolean, Configuration)`, and `main(String[])`, plus public `INDEX_FILE_NAME` and `DATA_FILE_NAME`. Its docs define it as a file-based map from keys to values backed by a data file and an index file.
- `SetFile` extends `MapFile` and represents a file-based set of keys.
- `Text` extends `BinaryComparable` and stores UTF-8 bytes. It has constructors from empty, `String`, `Text`, and `byte[]`; raw and copied byte accessors; length and code-point access; substring search; several `set` overloads; `append`; `clear`; string conversion; `readFields`, `readFields(DataInput, int)`, `skip`, `readWithKnownLength`; `write` overloads with optional max length; equality/hash; UTF-8 `decode` and `encode`; static string read/write helpers with maximum sizes; UTF-8 validation; `bytesToCodePoint`; `utf8Length`; and `DEFAULT_MAX_LEN`.

### Compression APIs

- `CompressionCodec` is the main codec contract. It creates `CompressionOutputStream` and `CompressionInputStream` instances with optional pooled `Compressor`/`Decompressor`, returns compressor/decompressor classes, creates compressor/decompressor objects, and exposes a default filename extension.
- `DefaultCodec`, `GzipCodec`, and `BZip2Codec` are concrete configurable codecs. `DefaultCodec` also implements `DirectDecompressionCodec`; `GzipCodec` extends `DefaultCodec`; `BZip2Codec` supports `SplittableCompressionCodec` by creating a `SplitCompressionInputStream` for a compressed byte range and read mode.
- `CodecConstants` provides public filename extension constants for default, bzip2, gzip, lz4, snappy, and zstandard codecs.
- `CompressionCodecFactory` discovers codecs from `io.compression.codecs`, Java `ServiceLoader`, and the configuration. It can list codec classes, set codec classes, find a codec by `Path`, class name, short name, or class object, remove suffixes, print its extension map, and run a small `main`.
- `CodecPool` is a global compressor/decompressor reuse pool. It leases compressors/decompressors for a codec, accepts them back with return methods, and exposes leased compressor/decompressor counts.
- `Compressor` and `Decompressor` are stream-state interfaces. They accept input buffers and optional dictionaries, report whether more input or dictionaries are needed, report bytes read/written or remaining bytes, finish/finished state, compress/decompress into caller buffers, reset for reuse, end resources, and in the compressor case `reinit(Configuration)`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases with protected underlying `in`/`out`, `close`, byte read/write hooks, `finish`, `flush`, `resetState`, and positional methods. `CompressionInputStream.seek` and `seekToNewSource` are documented as unsupported in this base class.
- `CompressorStream` and `DecompressorStream` bind a stream to a `Compressor` or `Decompressor`, maintain a byte buffer and closed/eof state, and implement write/read, compress/decompress loops, reset, skip/available, mark/reset behavior, and close.
- `BlockCompressorStream` and `BlockDecompressorStream` specialize the stream wrappers for block-oriented compressed payloads, including block-size and compression-overhead constructors, `compress`, `decompress`, `getCompressedData`, and state reset.
- `DirectDecompressionCodec` creates a `DirectDecompressor`; `DirectDecompressor.decompress(ByteBuffer, ByteBuffer)` defines direct buffer decompression without copying through byte arrays.
- `SplitCompressionInputStream` stores adjusted start/end positions for a compressed split. `SplittableCompressionCodec` creates such streams using a `READ_MODE` enum, start, and end offsets.

### Erasure Coding and TFile

- `ECSchema` stores erasure-code schema information. Constructors accept an options map or explicit codec name, data units, parity units, and extra options. Public fields name the canonical option keys: `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`. Accessors expose codec name, extra options, data units, parity units, string representation, equality, and hash code.
- `org.apache.hadoop.io.erasurecode.coder.util` and `org.apache.hadoop.io.erasurecode.grouper` appear as empty packages in this XML slice.
- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are checked TFile metadata block exceptions, both extending `IOException`.
- `org.apache.hadoop.io.file.tfile.RawComparable` exposes `buffer()`, `offset()`, and `size()` so external raw comparators can compare a byte range without wrapping or copying.
- `TFile` exposes comparator and format constants: `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, `COMPARATOR_MEMCMP`, and `COMPARATOR_JCLASS`. Static methods include `makeComparator(String)`, `getSupportedCompressionAlgorithms()`, and `main(String[])` for dumping TFile information.
- `TFile` docs define a byte key/value container with block compression, named metadata blocks, sorted or unsorted keys, seek by key or file offset, configurable chunk size and filesystem buffer sizes, and memory usage driven by block and metadata indexes.
- `org.apache.hadoop.io.file.tfile.Utils` provides an alternate TFile-specific variable-length integer encoding, string read/write in Text format, and generic `lowerBound`/`upperBound` binary-search helpers over lists with caller-supplied comparators.

## Control Flow

The XML has no executable flow, but the APIs imply several important runtime paths.

Writable serialization flows are symmetric. A writer calls `write(DataOutput)` in a type-specific order; the reader constructs an instance through a no-arg constructor, `WritableFactories`, `ObjectWritable`, or a containing type, then calls `readFields(DataInput)` in the same order. Comparability is layered on top through object `compareTo` or raw byte comparison with `RawComparator`/`WritableComparator`.

Polymorphic serialization writes enough type metadata to rebuild the runtime value. `GenericWritable` restricts that metadata to an allowed class table returned by `getTypes()`. `ObjectWritable` writes declared-class information and then dispatches to special handling for writables, strings, primitive types, arrays, enums, or null values. Read paths use configuration-aware class loading and object construction.

Text and string helper flows are length-prefixed. `Text` and `WritableUtils` read a vint length, validate or bound it where required, then consume UTF-8 bytes. `Text.validateUTF8`, `bytesToCodePoint`, and max-length overloads are the guard rails for malformed or oversized input.

SequenceFile writer construction is option-heavy but converges on creating a writer with configured key/value classes, destination stream/path, compression mode, optional codec, filesystem metadata, replication/block settings, and progress reporting. Record writes produce binary key/value records with periodic sync markers; block-compressed writers batch records into compressed blocks; raw writers accept pre-serialized key/value buffers.

MapFile operation is directory-oriented. A map contains a data sequence file and an index file. `rename` and `delete` operate on that directory layout, and `fix` reconstructs a missing or corrupt index by scanning the data file and writing a new index for the supplied key/value classes.

Compression output flow is: a codec creates or receives a `Compressor`, wraps the destination in a `CompressionOutputStream`, accepts uncompressed bytes, calls the compressor until bytes are emitted, and finalizes with `finish()` before close. Compression input reverses this by feeding compressed bytes into a `Decompressor`, emitting uncompressed bytes until `finished`, `needsInput`, or EOF state is reached. Block streams add block headers and block-level refill/flush boundaries.

Codec pooling flow is lease-and-return. Callers request a compressor/decompressor from `CodecPool`, use it with a codec-created stream, reset or finish the stream, then return the codec object. The leased-count APIs make pool misuse visible in tests and diagnostics.

Codec discovery flow maps configuration and service-loaded codec classes to filename extensions and aliases. `CompressionCodecFactory.getCodec(Path)` chooses by file suffix, while class-name and short-name methods support direct lookup.

Split compression flow is available only for codecs implementing `SplittableCompressionCodec`. The caller provides an input stream, decompressor, start/end byte offsets, and read mode; the returned `SplitCompressionInputStream` may adjust the effective start and end to codec-specific record boundaries.

TFile flow writes byte keys and values into data blocks, optionally compresses each block, maintains a block index and metadata-block index, and supports lookup by key or file offset. Comparator creation selects raw byte comparison either by the built-in memcmp comparator or by a Java comparator class prefix.

## State and Persistence Behavior

This JDiff file persists the Hadoop 3.2.2 API surface for compatibility comparison. It does not persist runtime Hadoop state, but many listed APIs define durable binary formats.

Every `Writable` type has serialized state. Primitive writable state is a single primitive value. VInt/VLong state is encoded using Hadoop's vint/vlong format, so byte compatibility depends on preserving the exact variable-length encoding. `Text` persists a length and UTF-8 bytes, not a Java `String` object. `MD5Hash` persists fixed 16-byte digest state. `NullWritable` persists no data and relies on singleton identity.

Container writables persist both structure and contained values. `MapWritable` and `SortedMapWritable` must persist enough class-id metadata through `AbstractMapWritable` to deserialize heterogeneous writable keys and values. `EnumSetWritable` must preserve the enum element type when the set is null or empty. `TwoDArrayWritable` persists matrix dimensions and each cell's writable state. `VersionedWritable` persists a version byte and rejects mismatches.

`ObjectWritable` and `GenericWritable` persist class identity. This creates compatibility pressure around class renames, classloader behavior, primitive/array encoding, and declared-class versus runtime-class distinctions. `WritableFactories` and `Configurable` hooks make construction depend on process-local registration and configuration rather than only reflection.

SequenceFile, MapFile, SetFile, and TFile define on-disk formats. SequenceFile state includes header metadata, key/value classes, compression type, codec identity, sync markers, and serialized records or blocks. MapFile state is split across data and index files inside a directory. TFile state includes data blocks, optional compression, key/value byte payloads, metadata blocks, and indexes; its docs call out memory cost proportional to block and metadata index counts.

Compression streams carry mutable, non-durable stream state such as input/output buffers, closed/eof booleans, compressor/decompressor objects, byte counters, pending input, dictionaries, and adjusted split bounds. The compressed bytes they produce are durable and must remain readable by the matching codec and format readers.

`CodecPool` has process-global state: available and leased compressor/decompressor instances. Returning objects correctly affects memory, native resource lifetime, and test isolation. `ElasticByteBufferPool` similarly has synchronized in-memory buffer caches with no maximum cache size.

`ECSchema` is an immutable-style value object from the visible API: codec name, data/parity counts, and extra options define durable erasure-coding policy metadata when embedded into higher-level HDFS state.

## Dependencies and Integration Points

These APIs sit on Java core I/O, NIO, reflection, collections, and security primitives: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `FileChannel`, `WritableByteChannel`, `ByteBuffer`, `MessageDigest`, `Comparator`, `Map`, `SortedMap`, `EnumSet`, and exception types.

Hadoop configuration and filesystem integration appears throughout. `DefaultStringifier`, `GenericWritable`, `ObjectWritable`, `WritableComparator`, `WritableFactories`, compression codecs, `CompressionCodecFactory`, `MapFile.fix`, and `SequenceFile.createWriter` depend on `org.apache.hadoop.conf.Configuration`. File-format helpers integrate with `FileSystem`, `Path`, `FSDataInputStream`, `FSDataOutputStream`, replication/block-size settings, progress callbacks, and Hadoop codec configuration.

MapReduce and shuffle integration depends on `WritableComparable`, `RawComparator`, `WritableComparator`, `Text`, primitive writable keys, and `SequenceFile`. Sorting and grouping can compare serialized bytes directly, so raw comparator behavior is a performance and correctness boundary.

Compression integrates with native or Java codec implementations behind the `Compressor` and `Decompressor` interfaces. Extension constants and `CompressionCodecFactory` connect file naming conventions to runtime codec choice. `SplittableCompressionCodec` integrates compressed files with input split planning.

TFile integrates the IO, compression, raw comparison, and utility encoding layers. It accepts compression algorithm names compatible with `TFile.Writer`, uses raw comparators for sorted keys, uses Text-style string encoding in utilities, and uses block indexes for seek behavior.

The JDiff file itself integrates with Hadoop's dev-support compatibility tooling. Changes in this XML are signals for public API additions, removals, signature changes, deprecations, and documentation shifts between Hadoop releases.

## Risks and Edge Cases

Binary compatibility is the main risk. Changing method signatures, constructors, field names, checked exceptions, implemented interfaces, or visibility in these APIs can break downstream Hadoop applications, file readers, RPC clients, MapReduce jobs, or codec plugins compiled against 3.2.2.

Serialization compatibility is more fragile than source compatibility. Reordering `write`/`readFields`, changing vint/vlong encoding, changing Text length checks, modifying ObjectWritable class encoding, or changing MapWritable class-id behavior can make existing files unreadable or produce subtle cross-version failures.

Raw comparators are correctness-critical. A comparator that orders serialized bytes differently from object `compareTo` can corrupt sort order, MapFile indexes, SequenceFile sort outputs, TFile sorted-key behavior, or MapReduce partition/group assumptions.

Length-prefixed readers need strict bounds. `Text.readString`, `WritableUtils.readStringSafely`, compressed byte-array readers, and TFile string/vint decoders can be exposed to malformed or hostile input; negative lengths, oversized lengths, truncated streams, and invalid UTF-8 are important failure modes.

Compression pooling can leak resources. Forgetting to return compressors/decompressors, returning ended objects, using objects after return, or failing to reset dictionaries and buffers can cause native memory leaks, data corruption, or nondeterministic test failures. The leased-count methods are intended test signals for this.

Split compression is codec-sensitive. A wrong adjusted start/end boundary can duplicate or omit records in split reads. Base `CompressionInputStream` seeking is unsupported, so callers must use split-aware codecs rather than assuming arbitrary seekability.

`ElasticByteBufferPool` has intentionally unbounded cache growth. Workloads with diverse large buffer sizes can retain substantial heap or direct memory after the peak has passed.

`ObjectWritable` and `WritableFactories` depend on class names, classloaders, and factory registration. Missing classes, renamed packages, non-public constructors without factories, or different configuration classloaders can break deserialization.

`MapFile.fix` can rebuild indexes but cannot recover missing or corrupt data records. Supplying the wrong key/value classes or comparator semantics can create an index that is syntactically present but semantically wrong.

TFile docs note tradeoffs around block size, compression, and buffering. Too-small blocks increase index memory and compressor flush overhead; too-large blocks hurt random access; poor compression choices waste CPU or storage. The documented single-threaded seek/read behavior means multiple scanners over one TFile may serialize I/O even when reading different DFS blocks.

## Test Signals

API compatibility tests should compare this JDiff output against expected public surface: class/interface presence, inheritance, implemented interfaces, constructor and method signatures, checked exceptions, public fields, static/final/synchronized flags, deprecation markers, and package docs.

Writable round-trip tests should serialize and deserialize every primitive wrapper, `Text`, `MD5Hash`, `NullWritable`, `EnumSetWritable` including null/empty sets, `MapWritable`, `SortedMapWritable`, `TwoDArrayWritable`, `GenericWritable` subclasses, `ObjectWritable` values for writable/string/primitive/array/enum/null cases, and `VersionedWritable` mismatch failures.

Comparator tests should verify object comparison and raw byte comparison agree for primitive writables, `Text`, `MD5Hash`, vint/vlong values, and any registered optimized comparator. Byte parsing helpers in `WritableComparator` and `WritableUtils` need boundary cases for negative values, minimum/maximum widths, and malformed encodings.

IO utility tests should cover short reads/writes, EOF during `readFully` and `skipFully`, bounded copy closure behavior, cleanup swallowing exceptions while logging where appropriate, `fsync` on files/directories, exception wrapping, and `readFullyToByteArray` behavior on finite streams.

File-format tests should write and read SequenceFiles with no compression, record compression, block compression, metadata, sync seeking, raw writers, and several key/value classes. MapFile/SetFile tests should cover index creation, rename/delete, corrupt or missing index repair, and wrong-class failure paths. TFile tests should cover compression algorithms, sorted and unsorted keys, metadata block duplicate/missing exceptions, key/file-offset seeks, comparator creation, and configured chunk/buffer sizes.

Compression tests should cover codec discovery by extension, canonical class name, short name, and configured codec list; stream round trips for Default, Gzip, and BZip2 codecs; compressor/decompressor pool lease counts before and after return; reset/reuse behavior; dictionary needs; block stream boundaries; direct `ByteBuffer` decompression; and bzip2 split reads with adjusted start/end positions.

Erasure-code schema tests should cover constructors from option maps and explicit parameters, preservation of extra options, equality/hashCode, string output for logs, and validation behavior in higher-level consumers that interpret `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.
