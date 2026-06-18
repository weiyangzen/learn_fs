# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.2.xml lines 17959-24282

## Scope

This chunk is a JDiff API slice for Hadoop Common 2.10.2. It covers the public and protected API declarations, signatures, deprecation markers, constants, and embedded JavaDoc for the core `org.apache.hadoop.io` serialization package and the beginning of `org.apache.hadoop.io.compress`. It does not expose method bodies, so control-flow and persistence notes below are derived from API contracts and documented file/stream formats rather than direct implementation statements.

The covered API surface starts at the tail of `AbstractMapWritable`, then spans writable containers and primitive wrappers, raw comparators, text and binary utilities, map/sequence file helpers, object/string serialization helpers, and compression stream/codec abstractions through `DefaultCodec`.

## Purpose

The `org.apache.hadoop.io` portion defines Hadoop's low-level binary data model. `Writable` and `WritableComparable` are the serialization and key-comparison contracts used by MapReduce, `SequenceFile`, `MapFile`, RPC helpers such as `ObjectWritable`, and utility APIs that serialize data into `DataInput`/`DataOutput`. The package favors reusable mutable objects, compact wire formats, raw byte comparators, and explicit class/type metadata where polymorphism is required.

The chunk also documents persistent file container APIs. `SequenceFile` is the flat binary key/value container with uncompressed, record-compressed, and block-compressed formats. `MapFile`, `ArrayFile`, `SetFile`, and `BloomMapFile` layer indexed or membership-optimized access patterns over sequence-style data files. These APIs integrate with Hadoop `FileSystem`, `FileContext`, `Path`, `Configuration`, `Progressable`, and compression codecs.

The `org.apache.hadoop.io.compress` portion defines the streaming compression abstraction used by `SequenceFile`, file input/output paths, and codec lookup by file suffix. Codecs create compression/decompression streams, compressors, and decompressors; stream wrappers manage finish/reset/close semantics; and `CodecPool` reuses potentially native compressor instances.

## Important APIs, Types, and Functions

### Writable contracts and primitive wrappers

- `Writable` is the base binary serialization protocol. Implementations write fields to `DataOutput` and read them back from `DataInput`, reusing storage where practical. The documentation recommends static `read(DataInput)` constructors for convenience.
- `WritableComparable` combines `Writable` and `Comparable` and is the standard key contract. The JavaDoc explicitly warns that `hashCode()` must be stable across JVM instances because Hadoop uses it for key partitioning.
- Primitive wrappers include `BooleanWritable`, `ByteWritable`, `ShortWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, `DoubleWritable`, `VIntWritable`, and `VLongWritable`. Each provides constructors, `set`, `get`, `readFields`, `write`, equality, hash, comparison, and string conversion. `VIntWritable` and `VLongWritable` store values in Hadoop's variable-length zero-compressed integer format.
- `NullWritable` is a singleton no-data writable for empty keys or values. Its serialization methods have no data payload.
- `VersionedWritable` prepends/validates an implementation version byte. `VersionMismatchException` is thrown when the serialized version differs from `getVersion()`, enabling explicit compatibility handling in evolving writable classes.

### Binary, text, and array data

- `BinaryComparable` defines ordering over representative byte arrays via abstract `getBytes()` and `getLength()`. Its default comparison delegates to `WritableComparator.compareBytes`, with equality and hash based on valid byte ranges.
- `BytesWritable` is a mutable byte sequence usable as key or value. It distinguishes logical length from backing capacity, supports exact copies via `copyBytes()`, exposes backing storage via `getBytes()`, and deprecates `get()`/`getSize()` in favor of `getBytes()`/`getLength()`.
- `Text` stores UTF-8 data with mutable backing bytes. It supports byte-level search, Unicode scalar lookup without materializing a `String`, append/set/copy operations, max-length guarded reads/writes, static UTF-8 encode/decode, string read/write helpers, UTF-8 validation, code point decoding, and `utf8Length`. `clear()` leaves the backing byte array allocated for reuse.
- `ArrayPrimitiveWritable` wraps primitive Java arrays without copying and serializes them in an optimized wire format without per-element objects. It records/validates component type and supports known-type wrappers.
- `ArrayWritable` and `TwoDArrayWritable` serialize arrays or matrices of a single `Writable` class. `ArrayWritable` includes a `String[]` constructor and documentation showing that reducer inputs often need a subclass fixing the value class.
- `EnumSetWritable` wraps an `EnumSet`, implements `Configurable`, and requires an element type when the wrapped value is null or empty. It exposes collection operations plus writable read/write.

### Map-like writables and polymorphic serialization

- `AbstractMapWritable` is the base for map writables. It carries class-to-byte-id and id-to-class mappings per map instance so nested `MapWritable<Writable, MapWritable>` structures can serialize their type tables without relying on static maps. IDs are limited to 1..127, so an instance can contain at most 127 distinct classes.
- `MapWritable` implements `Map<Writable, Writable>` semantics with writable serialization and copy construction.
- `SortedMapWritable` implements `SortedMap<WritableComparable, Writable>` with sorted-map navigation (`firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`) plus writable serialization.
- `GenericWritable` wraps one of a fixed set of writable classes returned by subclass-provided `getTypes()`. It is intended for cases where multiple value types share a common key type in MapReduce. Its JavaDoc emphasizes it is more compact than `ObjectWritable` because it avoids writing the class name for every record.
- `ObjectWritable` writes polymorphic values with declared class information. It handles `Writable`, `String`, primitive types, and arrays of those types. Its `allowCompactArrays` flag is documented as safe for RPC/internal intra-cluster uses but not for persisted inter-cluster files that require cross-version exchange.
- `WritableFactories` and `WritableFactory` register constructors for non-public writable classes so `ObjectWritable` and reflection-style deserialization can instantiate them. `WritableFactories.newInstance` optionally accepts `Configuration`.
- `DefaultStringifier` and `Stringifier<T>` convert serializable objects to/from strings, using Hadoop serialization plus base64 in the default implementation. Static helpers store/load single objects or arrays in `Configuration` keys.

### File container APIs

- `SequenceFile` provides the core flat binary key/value file format. The chunk exposes default compression type getters/setters and many `createWriter` overloads, including modern option-based creation and deprecated legacy overloads taking `FileSystem`, `Path`, buffer sizes, replication, block size, `Progressable`, `FSDataOutputStream`, metadata, `FileContext`, and create flags/options.
- `SequenceFile.SYNC_INTERVAL` is the documented interval between sync markers.
- The SequenceFile documentation specifies a common header containing magic/version, key/value class names, compression flags, compression codec class, metadata, and a sync marker.
- The three documented SequenceFile record layouts are uncompressed records, record-compressed records where only values are compressed, and block-compressed records where key lengths, keys, value lengths, and values are grouped into compressed blocks with sync per block.
- `MapFile` is a directory-backed map with `data` and `index` files. The index holds a sampled fraction of keys and is read entirely into memory. Entries must be added in order, and large updates are expected to create a new sorted version rather than mutate in place.
- `MapFile.rename`, `MapFile.delete`, and `MapFile.fix` operate on `FileSystem` paths. `fix` can rebuild a corrupt index from data, with a dry-run mode and a return count of valid entries or `-1` when no fix is needed.
- `ArrayFile` is a dense integer-to-value file mapping, `SetFile` is a file-based key set, and `BloomMapFile` adds dynamic Bloom filters for fast negative membership checks over `MapFile`-like content.

### Comparison, hashing, and writable utilities

- `RawComparator<T>` compares serialized byte ranges directly without materializing objects.
- `WritableComparator` implements `RawComparator` and `Configurable`. It can register optimized comparators with `define`, obtain comparators with `get`, create new keys, compare serialized byte ranges by deserializing as a default fallback, compare natural `WritableComparable` objects, and provide static byte parsing helpers for primitive values and variable-length integers.
- Static `WritableComparator.compareBytes` performs lexicographic binary ordering; `hashBytes` computes byte hashes.
- `WritableUtils` provides compressed byte/string array helpers, string read/write helpers, object cloning through serialization, deprecated `cloneInto`, variable-length integer read/write/size/sign helpers, enum read/write, skip helpers, byte-array aggregation, and safe string reads with maximum length.
- `IOUtils` provides stream copy overloads, exact read/skip loops, compressed-read exception wrapping, cleanup/close helpers for streams/sockets, `FileChannel` write loops, directory listing that preserves IOExceptions, file/channel fsync helpers, and `readFullyToByteArray`.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`, returning the original object when it is already an `OutputStream`.
- `MultipleIOException` wraps a list of `IOException` instances and has a convenience factory.
- `MD5Hash` is a writable comparable 16-byte digest wrapper with constructors from hex strings or bytes, static digest helpers over byte arrays, strings, UTF8, and streams, thread-local digester creation, half/quarter digest projections, hex parsing, and natural ordering.

### Compression APIs

- `CompressionCodec` defines the codec contract: create compression/decompression streams, create or identify `Compressor`/`Decompressor` types, and advertise a default file extension.
- `CompressionCodecFactory` discovers codecs from `io.compression.codecs`, Java `ServiceLoader`, and defaults such as gzip/deflate. It looks codecs up by path suffix, canonical class name, or case-insensitive aliases derived from short class names with and without the `Codec` suffix.
- `CodecPool` is a global reusable pool for compressors and decompressors, with lease counters per codec. The API supports reinitializing compressors with `Configuration`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases. They deliberately make core bulk read/write abstract to avoid leaking through to the underlying stream. Input streams implement `Seekable` but base `seek` and `seekToNewSource` are unsupported; `resetState()` is the repositioning hook.
- `Compressor` and `Decompressor` model `Deflater`/`Inflater`-style state machines: set input, check whether more input or a dictionary is needed, compress/decompress into caller buffers, query byte counters or remaining input, finish, reset, and end.
- `CompressorStream` and `DecompressorStream` wrap `Compressor`/`Decompressor` instances around output/input streams and expose fields for the codec object, work buffer, closed/eof state, plus protected hooks such as `compress`, `decompress`, `getCompressedData`, and `checkStream`.
- `BlockCompressorStream` and `BlockDecompressorStream` are block-based stream wrappers, contrasting with stream-based compression algorithms.
- `BZip2Codec` implements `SplittableCompressionCodec` and `Configurable`. It uses native bzip2 if available, otherwise a pure-Java implementation. The JavaDoc notes pure-Java mode does not implement `Compressor`/`Decompressor` methods and that split input is currently supported only in pure-Java mode.
- `DefaultCodec` implements `CompressionCodec` and `DirectDecompressionCodec`, exposing deflate-style stream creation and direct decompressor creation.

## Control Flow

Writable control flow is caller-driven and object-reuse oriented. Producers call `write(DataOutput)` in a deterministic field order; consumers instantiate or reuse an object and call `readFields(DataInput)` in the matching order. Containers such as arrays, maps, object wrappers, and enum sets first encode enough type/length metadata to reconstruct contents, then delegate per-element payloads to nested writable implementations.

Comparator control flow has two paths. Generic comparison deserializes byte ranges into writable key objects and uses natural `compareTo`. Optimized comparison overrides raw byte comparison and uses utilities such as `compareBytes`, `readInt`, `readVLong`, or `hashBytes` to avoid object allocation in sort-heavy paths like `SequenceFile.Sorter` and MapReduce shuffle/sort.

Text and byte wrappers expose a deliberate split between backing storage and logical length. Callers needing speed can use raw arrays and lengths; callers needing an exact independent value must call copy helpers. `Text` read/write uses zero-compressed length prefixes, and max-length overloads provide guardrails for untrusted or bounded inputs.

File container flow for `SequenceFile` is: create a writer with configuration, path/stream, key/value classes, compression type, optional codec, metadata, and filesystem options; write records using one of the documented layouts; insert sync markers; later create readers/sorters outside this chunk to consume the shared format. `MapFile` write flow requires sorted key insertion, with index creation as a sampled subset of data keys. Recovery flow for `MapFile.fix` scans data to rebuild index state.

Compression stream flow is state-machine based. A compression stream accepts uncompressed bytes, feeds a `Compressor`, drains compressed bytes to the underlying stream, and `finish()` flushes codec state without closing the underlying stream. A decompression stream reads compressed data, feeds a `Decompressor`, returns uncompressed bytes, and uses `needsInput`, `finished`, `getRemaining`, and `resetState` to handle stream boundaries, concatenated streams, and repositioning.

Codec lookup flow in `CompressionCodecFactory` is configuration- and classpath-driven: discover codec classes, build suffix/name maps, then select a codec by file extension or name alias. `CodecPool` adds lifecycle flow around codecs: borrow compressor/decompressor, use it in streams, return it for reuse, and track leaked leases via count methods.

## State and Persistence Behavior

Most writable classes are mutable value holders. Persistent state is whatever their `write` methods emit to `DataOutput`; in-memory state is often a backing array, logical length, wrapped object, enum element type, or map of nested writable keys/values. The API repeatedly signals that deserialization should reuse existing storage where possible.

`AbstractMapWritable`, `MapWritable`, and `SortedMapWritable` persist per-instance class ID tables along with entries. That avoids static global type maps and enables nested map writables, but the byte ID range constrains each map instance to 127 distinct classes.

`ObjectWritable` persists declared class names and object payloads, with a compatibility-sensitive compact array mode. Because its class names are serialized per value, it is flexible but can be expensive and creates classloading dependencies at read time through `ObjectWritable.loadClass(Configuration, className)`.

`DefaultStringifier` persists serialized object bytes as base64 strings inside `Configuration`, so objects stored there are subject to Hadoop serialization availability, class compatibility, and configuration propagation semantics.

`SequenceFile` persistence is explicitly specified in the JavaDoc. The header stores class names, compression flags, codec class, metadata, and sync marker. Record and block layouts store lengths, keys, values, compressed values, or compressed grouped blocks. These formats are durable compatibility contracts for Hadoop data files.

`MapFile` persistence is directory based with fixed `DATA_FILE_NAME` and `INDEX_FILE_NAME` constants. The full data file stores all key/value pairs; the index is an in-memory-loaded sampled key map. `MapFile.fix` is the documented repair path when index persistence is corrupt or missing.

Compression classes hold transient codec state: buffers, open/closed flags, eof flags, compressor/decompressor native state, and pool lease state. Codec streams do not themselves define durable file headers except through the codec algorithms and container formats using them.

## Dependencies and Integration Points

- Java core I/O and NIO: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `FilenameFilter`, `FileChannel`, `ByteBuffer`, and charset exceptions.
- Hadoop configuration and reflection: `Configuration`, `Configurable`, serialization factory APIs referenced by `DefaultStringifier`, and object construction through `WritableFactories`.
- Hadoop filesystem APIs: `FileSystem`, `FileContext`, `Path`, `FSDataOutputStream`, `Options.CreateOpts`, `CreateFlag`, and `Seekable`.
- Hadoop MapReduce data paths: `WritableComparable` key contracts, `SequenceFile` readers/writers/sorters, `MapFile` indexed storage, and MapReduce partitioning via stable `hashCode`.
- Hadoop compression: `CompressionCodec`, codec implementations, `Compressor`, `Decompressor`, `DirectDecompressionCodec`, `SplittableCompressionCodec`, and `CodecPool`.
- External/native components: bzip2 native library selection through `io.compression.codec.bzip2.library`, Java `ServiceLoader` codec discovery, and default Java/native deflate-style codec support through `DefaultCodec`.
- Logging and cleanup: `IOUtils.LOG`, cleanup helpers, and exception aggregation through `MultipleIOException`.

## Risks and Edge Cases

- JDiff exposes signatures and docs, not method bodies. Any implementation-specific behavior beyond the documented contracts should be verified in the Java source before making code changes.
- Writable compatibility depends on exact field order and encoding. Adding fields, changing variable-length encodings, or altering class-name serialization can break persisted SequenceFiles, MapFiles, RPC payloads, or configuration-serialized values.
- `WritableComparable.hashCode()` must be deterministic across JVMs. Using `Object.hashCode()` or process-specific identity hashes can silently break partitioning and grouping.
- `BytesWritable.getBytes()` and `Text.getBytes()` expose backing arrays whose valid data is limited by `getLength()`. Treating the whole capacity as data can leak stale bytes or corrupt comparisons.
- `Text.clear()` does not free or zero the backing byte array. This is good for reuse but risky for memory retention or accidental exposure of previous contents through raw backing-array access.
- `MapFile` indexes are read entirely into memory, so very large or poorly sampled indexes can create memory pressure. Key classes used in indexes should remain compact.
- `MapFile` requires sorted/in-order additions. Out-of-order writes can produce unreadable or semantically corrupt maps even if the data file is syntactically valid.
- `AbstractMapWritable` supports only 127 distinct classes per instance because IDs are bytes in range 1..127.
- `ObjectWritable` class-name based polymorphism is flexible but costly and sensitive to classloader/configuration differences. Compact array mode is explicitly unsafe for inter-cluster or persisted exchange with differing software versions.
- `DefaultStringifier.storeArray` documents `IndexOutOfBoundsException` for empty arrays, so callers must special-case empty configuration values.
- Codec pooling requires return discipline. Failing to return compressors/decompressors can leak native resources; returning an object still in use can corrupt concurrent streams.
- BZip2 behavior differs between native and pure-Java modes. In pure-Java mode, compressor/decompressor interface methods with explicit objects may throw `UnsupportedOperationException`; split reads force pure-Java mode.
- `CompressionInputStream` advertises `Seekable`, but base `seek` and `seekToNewSource` throw unsupported operation. Callers must not assume all compressed streams are truly seekable.
- `Decompressor.setInput` requires the input byte buffer remain unmodified until `needsInput()` says it is safe, which is easy to violate in zero-copy or pooled-buffer callers.
- `readFullyToByteArray(DataInput)` reads until EOF and warns that infinite inputs never return; callers need bounded inputs for untrusted streams.

## Test Signals

- Writable round-trip tests should cover each primitive wrapper, `NullWritable`, `BytesWritable`, `Text`, `ArrayPrimitiveWritable`, `ArrayWritable`, `TwoDArrayWritable`, `EnumSetWritable`, `MapWritable`, `SortedMapWritable`, `GenericWritable`, `ObjectWritable`, `MD5Hash`, and version mismatch behavior.
- Compatibility tests should verify existing serialized bytes for variable-length integers, `Text`, `SequenceFile` headers, record-compressed and block-compressed records, `MapFile` data/index directories, and `ObjectWritable` compact vs non-compact arrays.
- Comparator tests should compare object-level and raw byte-level ordering for primitive writables, `BytesWritable`, `Text`, `MD5Hash`, and custom optimized `WritableComparator` registrations.
- Boundary tests should exercise zero-length and oversized byte/text values, max-length guarded text reads/writes, invalid UTF-8 with replace true/false, `Text.charAt` on invalid/trailing byte positions, and `BytesWritable` length/capacity resizing.
- Map writable tests should include nested maps, copy constructors, class table growth, and rejection or failure behavior when distinct class counts exceed the byte-id limit.
- `IOUtils` tests should cover short reads/writes, EOF handling in `readFully`/`skipFully`, close-on-copy behavior, cleanup of multiple streams, directory listing IOExceptions, fsync of files and directories, and bounded use of `readFullyToByteArray`.
- `MapFile.fix` tests should create missing/corrupt indexes, verify dry-run behavior, validate returned entry counts, and ensure sorted key assumptions are enforced.
- SequenceFile tests should create writers through both option-based and legacy overloads, with none/record/block compression, metadata, sync interval behavior, `FileSystem` and `FileContext` creation paths, and codec round trips.
- `DefaultStringifier` tests should store/load objects and arrays in `Configuration`, including empty-array rejection and serialization failure propagation.
- Compression tests should cover codec discovery from configuration and `ServiceLoader`, suffix/name/alias lookup, suffix removal, compressor/decompressor pool lease counts, pool return/reset behavior, stream `finish` without close, stream `resetState`, unsupported base seeking, concatenated decompressor streams, and BZip2 native vs pure-Java/splittable mode differences.
