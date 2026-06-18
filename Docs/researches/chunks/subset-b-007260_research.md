# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 12475-18820

## Scope And Purpose

This chunk is a JDiff API-description slice for Hadoop 0.17.0. It starts at the tail of `org.apache.hadoop.io.ArrayWritable` documentation, covers most of the public `org.apache.hadoop.io` serialization, comparison, text, and file-container APIs, and ends in the opening public contract for `org.apache.hadoop.io.compress.GzipCodec`. The file is not executable implementation code; it is generated XML describing classes, interfaces, constructors, methods, fields, inheritance, deprecation state, and embedded Javadoc. The research below therefore treats behavior as the public API contract exposed by this release.

The dominant purpose of the chunk is to define Hadoop's low-level binary data model: `Writable` serialization, `WritableComparable` keys, raw byte comparators, reusable in-memory input/output buffers, primitive writable wrappers, text encodings, map/set/sequence file containers, object/string serialization helpers, versioned wire formats, and compression codec interfaces. These APIs are central integration points for MapReduce records, HDFS-backed persistent files, RPC object transport, sorting/merging pipelines, and compression-aware readers and writers.

The chunk boundary matters. `ArrayWritable` is only represented by trailing documentation, so its constructors and methods are not complete in this slice. `GzipCodec` is present only through its class declaration and first methods, with nested gzip stream classes and later LZO/zlib APIs outside this chunk.

## API Families Covered

### Writable Core

`Writable` is the base binary serialization contract. It exposes `write(DataOutput)` and `readFields(DataInput)` and documents the important reuse expectation: implementations should deserialize into existing storage where possible. `WritableComparable` extends `Writable` and `Comparable`, making it the expected key shape for Hadoop sorting and MapReduce keys.

`WritableComparator` implements `RawComparator` and is the registry/factory for optimized key comparisons. It can return a comparator for a key class with `get(Class)`, register an optimized comparator with `define(Class, WritableComparator)`, instantiate keys with `newKey()`, compare fully materialized `WritableComparable` objects, or compare serialized byte ranges directly. Static helpers parse fixed-width primitives and variable-length integers from byte arrays (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`), compare byte ranges lexicographically, and hash bytes.

`RawComparator<T>` extends `Comparator<T>` with `compare(byte[], int, int, byte[], int, int)`. This is the bridge between Hadoop's serialized spill/sort paths and Java object comparison. Optimized primitive comparators in this chunk (`BooleanWritable.Comparator`, `BytesWritable.Comparator`, `FloatWritable.Comparator`, `IntWritable.Comparator`, `LongWritable.Comparator`, `LongWritable.DecreasingComparator`, `MD5Hash.Comparator`, `Text.Comparator`, `UTF8.Comparator`) all plug into this raw-comparison model.

`WritableFactory` and `WritableFactories` provide class-to-factory registration and instantiation. `WritableName` maps writable classes to short names and back. These registries are stateful static integration points: they allow custom classes to avoid reflection-only construction or to preserve legacy wire names, but they also introduce global process state that can affect deserialization in tests and long-lived daemons.

`WritableUtils` is the utility surface for common wire encodings: compressed byte arrays and strings, string arrays, compressed string arrays, byte-array display, cloning and clone-into through `Configuration`, variable-length integer/long read-write helpers, enum read/write, and `skipFully`. Its variable-length integer helpers back `VIntWritable`, `VLongWritable`, `Text` length encoding, and raw comparator parsing.

### Primitive And Simple Writable Types

The chunk defines primitive wrappers that all follow the same basic shape: no-arg and value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, `toString`, and usually a raw comparator:

- `BooleanWritable` stores a boolean key/value and has a specialized raw comparator.
- `FloatWritable`, `IntWritable`, and `LongWritable` store fixed-width primitives and expose optimized comparators that parse serialized bytes directly.
- `LongWritable.DecreasingComparator` reverses both object and raw-byte ordering for descending sorts.
- `VIntWritable` and `VLongWritable` store integer values with Hadoop's variable-length encoding, reducing serialized size for smaller values.
- `NullWritable` is a singleton-like zero-length placeholder value/key. It serializes no state and is used where a key or value slot is structurally required but semantically empty.
- `BytesWritable` is a resizable byte sequence with explicit logical size versus backing capacity. It exposes raw storage with `get()`, size/capacity mutation, copy/set operations, serialization, memcmp-like sorting, MD5-front hashing per Javadoc, equality over the active byte range, and a hex `toString`.
- `MD5Hash` is a fixed-length hash writable with constructors from string/bytes, digest helpers over byte arrays/strings/input streams, half/quarter digest extraction, byte-level comparison, `setDigest`, and the public `MD5_LEN` field.

These classes are deliberately small and allocation-conscious. Their `readFields` methods mutate existing instances, and their raw comparators let sort paths avoid full object creation.

### Arrays, Maps, Generic Values, And Object Serialization

`ArrayWritable` is only partially visible at the beginning of the chunk, but the visible documentation shows its intended subclassing model: callers often subclass it to fix the element value class, especially when using it as a reducer input value.

`TwoDArrayWritable` stores a matrix of `Writable` instances of a declared class. It exposes constructors with the value class and optional initial values, `toArray()`, `set`, `get`, `readFields`, and `write`.

`MapWritable` extends `AbstractMapWritable` and implements `Map<Writable, Writable>`. It exposes normal `Map` operations plus `readFields` and `write`. `SortedMapWritable` similarly extends `AbstractMapWritable` and implements `SortedMap<WritableComparable, Writable>`, adding sorted-map range and endpoint methods (`comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`) alongside the normal map API and serialization.

`GenericWritable` wraps one of a bounded set of writable implementation classes supplied by subclass `getTypes()`. It is also `Configurable`, so deserialized wrapped values can be constructed/configured under a `Configuration`.

`ObjectWritable` serializes arbitrary declared Java objects under a declared class. It is also `Configurable` and has static `writeObject` and `readObject` helpers. It is the broadest and riskiest serialization surface in the chunk because it crosses from Hadoop's narrow `Writable` model into Java primitive, string, array, enum, and configured object handling. The declared class is part of the serialized contract and is returned by `getDeclaredClass()`.

`DefaultStringifier<T>` implements `Stringifier<T>` using `Configuration` and a target class. It converts objects to/from strings, and includes static helpers for storing/loading a single value or arrays in `Configuration` properties. This makes serialized objects part of configuration state rather than file state.

`Stringifier<T>` is the generic closeable string conversion interface with `toString(T)`, `fromString(String)`, and `close()`.

### Text And Encoding

`Text` is the primary UTF-8 string writable in this release. It stores standard UTF-8 bytes with an integer length encoded in zero-compressed format. It supports construction from Java `String`, another `Text`, or byte arrays; raw byte and length access; code-point traversal with `charAt`; substring search with `find`; setting from strings, bytes, and other `Text`; appending raw UTF-8 bytes; clearing; serialization/deserialization; bytewise UTF-8 ordering; and equality/hash behavior over content.

`Text` also exposes static helpers for UTF-8 conversion and validation: `decode`, `encode`, `readString`, `writeString`, `validateUTF8`, `bytesToCodePoint`, and `utf8Length`. The APIs distinguish replacement behavior for malformed input from strict `CharacterCodingException` / `MalformedInputException` paths.

`UTF8` is still present but deprecated in favor of `Text`. It is a `WritableComparable` string type with raw byte/length access, setters, read/write, skip, comparison, static string read/write helpers, and an optimized comparator. Its presence is a compatibility signal for old sequence files or APIs that still name `UTF8`.

### Reusable Buffers And IO Utilities

`DataInputBuffer` and `DataOutputBuffer` are reusable in-memory `DataInput`/`DataOutput` implementations. `DataInputBuffer` resets over a byte array plus start/length and reports current position and length. `DataOutputBuffer` exposes backing data and valid length, can reset to empty, and can copy bytes directly from a `DataInput`.

`InputBuffer` and `OutputBuffer` provide similar reusable byte-buffer behavior for `InputStream`/`OutputStream` rather than `DataInput`/`DataOutput`. `OutputBuffer.write(InputStream, int)` copies directly from an input stream.

`IOUtils` is the stream/socket helper surface. It contains multiple `copyBytes` overloads, `readFully`, `skipFully`, `closeStream`, and `closeSocket`. `IOUtils.NullOutputStream` discards all bytes, acting like `/dev/null`.

The control-flow pattern across these utilities is direct streaming/copying with explicit byte counts, EOF-sensitive read/skip loops, and defensive close helpers that callers can use in cleanup paths.

### Versioned Serialization And Error Aggregation

`VersionedWritable` is an abstract `Writable` base that writes/reads a version byte and compares it to subclass `getVersion()`. On mismatch, it throws `VersionMismatchException`. The documentation explicitly instructs evolving subclasses to catch version mismatches in `readFields` if they can translate old formats.

`VersionMismatchException` reports expected versus found versions. `MultipleIOException` wraps or creates an `IOException` from a list of `IOException` instances. These APIs support robust cleanup and migration behavior in storage and stream code.

## File Container APIs

### SequenceFile

`SequenceFile` is the main flat binary key/value file format described in this chunk. Its static `createWriter` overloads construct writers over `FileSystem`/`Path` or raw `FSDataOutputStream`, with configurable key/value classes, buffer size, replication, block size, compression type, codec, progress callback, and metadata. Deprecated `getCompressionType(Configuration)` and `setCompressionType(Configuration, CompressionType)` redirect users toward job-specific MapReduce configuration or explicit writer creation.

The Javadoc describes three formats:

- Uncompressed records: header, record length, key length, key bytes, value bytes, and periodic sync markers.
- Record-compressed records: same record envelope, but values are compressed.
- Block-compressed records: batches of key lengths, keys, value lengths, and values are compressed as separate blocks, with lengths encoded in zero-compressed integer format.

All formats share a header containing magic/version, key class, value class, compression booleans, codec class when enabled, file metadata, and a sync marker. `SYNC_INTERVAL` controls approximate spacing between sync points.

`SequenceFile.CompressionType` is the enum selecting none, record, or block compression. `SequenceFile.Metadata` is a `Writable` wrapper around `TreeMap<Text, Text>` with get/set, direct metadata access, serialization, equality, hash, and string conversion.

`SequenceFile.Reader` reads all SequenceFile variants. It can open an `FSDataInputStream` through a protected `openFile` hook, report key/value class names and classes, report compression mode and codec, expose metadata, close the file, read key-only records, read key/value records, read current values, create `ValueBytes`, read raw key/value records, seek to exact writer-returned positions, sync to the next marker after an arbitrary position, report whether a sync was seen, and report current byte position.

`SequenceFile.ValueBytes` is the raw-value abstraction used by raw readers/writers. It exposes `writeUncompressedBytes`, `writeCompressedBytes`, and `getSize`.

`SequenceFile.Writer` exposes constructors for all writer modes and lower-level stream parameters, then provides `getKeyClass`, `getValueClass`, `getCompressionCodec`, `sync`, `close`, typed `append(Writable, Writable)`, raw append variants, and `getLength`. Its fields include serializers for keys, uncompressed values, and compressed values, indicating integration with Hadoop's serializer framework even though this chunk only shows the API metadata.

`SequenceFile.Sorter` sorts and merges SequenceFiles using either key/value classes or an arbitrary `RawComparator`. It exposes merge factor, memory budget, progress callback, `sort`, `sortAndIterate`, `merge`, `cloneFileAttributes`, and `writeFile`. `Sorter.RawKeyValueIterator` provides the streaming sorted-run interface (`getKey`, `getValue`, `next`, `close`, `getProgress`). `Sorter.SegmentDescriptor` represents an input segment with constructors by path or explicit offset/length, metadata accessors for length and path, `ignore`, `preserveInput`, and a `doSync` flag. This is the public contract for external sorting and multi-pass merging.

### MapFile And SetFile

`MapFile` is a directory-based persistent sorted map over Hadoop files. The public fields `INDEX_FILE_NAME` and `DATA_FILE_NAME` identify the two child files. The data file stores all key/value pairs; the index file stores a fraction of keys determined by `MapFile.Writer`'s index interval and is read entirely into memory by readers. The class offers static `rename`, `delete`, `fix`, and `main`. `fix` can rebuild a corrupt index from the data file, optionally as a dry run, and returns the number of valid entries or `-1` if no fix was needed.

`MapFile.Reader` opens an existing map with a `FileSystem`, directory name, optional `WritableComparator`, `Configuration`, and a protected delayed-open constructor for subclasses. It exposes synchronized navigation and lookup: `reset`, `midKey`, `finalKey`, `seek`, `next`, `get`, `getClosest` with optional before/after behavior, and `close`. It also has protected `open` and `createDataFileReader` hooks, so subclasses can specialize the underlying `SequenceFile.Reader`.

`MapFile.Writer` creates sorted maps with key/value classes or explicit comparators, optional compression type, codec, progress callback, and configuration. It exposes static and instance index interval configuration, `append`, and `close`. The API contract requires in-order key appends; large database updates are expected to be built by copying/merging sorted versions rather than in-place modification.

`SetFile` extends `MapFile` and models a sorted persistent set by storing keys with empty values. `SetFile.Reader` extends `MapFile.Reader` and narrows operations to `seek`, key-only `next`, and key-returning `get`. `SetFile.Writer` extends `MapFile.Writer` and exposes constructors for key class/comparator and compression, plus key-only `append`.

## Compression APIs

`CompressionCodec` is the top-level codec interface. It creates compression output streams with or without a provided `Compressor`, reports the compressor type, creates compressors, creates compression input streams with or without a provided `Decompressor`, reports the decompressor type, creates decompressors, and returns a default filename extension. This interface is consumed directly by SequenceFile writers/readers and by `CompressionCodecFactory`.

`CompressionCodecFactory` is a configuration-driven codec registry and filename matcher. It constructs from `Configuration`, can list/set codec classes, find the codec for a file name, remove a codec suffix, stringify its registered set, and has a `main` entry point. It exposes a `LOG` field using Apache Commons Logging. Its public documentation describes it as a factory that finds the correct codec for a filename.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases wrapping protected final `InputStream in` and `OutputStream out`. Input streams require subclasses to implement `read(byte[], int, int)` and `resetState()`, with reset intended for cases where the underlying stream was repositioned. Output streams require `write(byte[], int, int)`, `finish()` without closing the underlying stream, and `resetState()` without resetting the underlying stream. `close` and `flush` are part of the base contract.

`Compressor` and `Decompressor` model streaming codecs after `java.util.zip.Deflater` and `Inflater`. `Compressor` accepts input, reports `needsInput`, accepts dictionaries, reports byte counts, handles `finish`/`finished`, fills output buffers via `compress`, and supports `reset` and `end`. `Decompressor` mirrors this with `setInput`, `needsInput`, dictionary support and `needsDictionary`, `finished`, `decompress`, `reset`, and `end`.

`DefaultCodec` implements `CompressionCodec` and `Configurable`, exposing all codec factory methods plus `setConf`/`getConf`. `GzipCodec` extends `DefaultCodec`; this chunk includes its constructor and overrides for stream creation, compressor/decompressor creation/type reporting, and default extension. The class doc states that it creates gzip compressors/decompressors, but nested gzip stream classes continue after the chunk boundary.

## Control Flow And Data Flow

The central data flow is object-to-bytes-to-object. Writers call `Writable.write(DataOutput)` into files, buffers, RPC streams, or compression streams. Readers reuse instances and call `readFields(DataInput)` to mutate them from serialized bytes. Comparators sit on both sides: normal object comparators compare deserialized keys, while raw comparators compare serialized byte slices during sort/merge operations.

For SequenceFiles, control flow is file-format driven. A writer emits a header, metadata, sync marker, and then records according to the selected compression mode. It returns byte positions through `getLength()` that readers can later use for exact `seek`. For non-exact positions, readers use `sync(long)` to advance to the next marker and `syncSeen()` to detect split boundaries. Raw read/write APIs move serialized key/value bytes through `DataOutputBuffer` and `ValueBytes` without materializing Java objects, which is important for sort/merge performance.

For MapFiles, control flow layers on SequenceFile. A writer appends sorted keys to the data file and periodically writes index entries. A reader loads the index into memory, binary-searches or scans to the nearest indexed key, seeks the underlying data reader, and then scans forward to the target or closest key. `fix` reconstructs index state from the data file when the index is missing or corrupt.

For Sorter APIs, the implied flow is external sort: consume one or more input SequenceFiles, use a `RawComparator` to sort records under a memory budget, spill or merge sorted segments with a configurable merge factor, and expose merged output either as a file or `RawKeyValueIterator`.

For compression, clients create streams through `CompressionCodec`, optionally reuse `Compressor`/`Decompressor` instances, push input while checking `needsInput`, drain output through `compress`/`decompress`, signal `finish`, and then reset or end codec state. `CompressionInputStream.resetState()` explicitly supports repositioning the underlying input stream, which is required by splittable readers or sync-seeking file readers that reuse buffered compression wrappers.

## State And Persistence Behavior

Most primitive and collection writables hold only in-memory object state and serialize it exactly through `DataOutput`/`DataInput`. The important persistence contract is binary compatibility: field order, length encoding, variable-length integer handling, class names, and metadata encodings become on-disk or over-the-wire state.

`BytesWritable`, `Text`, `UTF8`, `DataOutputBuffer`, and `OutputBuffer` distinguish backing capacity from valid length. Callers that consume `get()` or `getData()` must respect `getSize()` or `getLength()`; otherwise stale bytes beyond the logical end can leak into comparisons, hashes, or writes.

`MapWritable` and `SortedMapWritable` persist dynamic class mappings through `AbstractMapWritable` behavior outside this chunk. The API shape shows they must serialize both entries and enough type information for arbitrary writable keys and values. Copy constructors indicate state can be duplicated while preserving those mappings.

`DefaultStringifier.store/load` and `storeArray/loadArray` persist object state into `Configuration` properties. This is not durable file persistence by itself, but in Hadoop deployments configuration can be serialized into job submissions, so values stored through these helpers can cross process and cluster boundaries.

`SequenceFile` persists the richest state: magic/version, key/value class names, compression flags, codec class, `Metadata`, sync marker, and records. Compression choices and codec class names become part of the file's readability contract. `Metadata` persists `Text` key/value attribute pairs. `Writer.sync()` injects recovery/split points into the file; `Reader.sync()` and `syncSeen()` are the corresponding read-side persistence hooks.

`MapFile` persists a directory containing `data` and `index`. The index is derived state, but it is persisted for lookup speed and can be repaired with `fix`. Because the index is loaded fully into memory, key size and index interval are persistent design choices that affect reader memory footprint.

`SetFile` persists only set keys on top of `MapFile`, using the map container machinery with semantically empty values.

Compression codecs keep transient native or Java codec state. `reset()` allows instance reuse for a new stream; `end()` releases resources and discards unprocessed input. Mismanaging this lifecycle can leak native resources or corrupt subsequent streams if a codec instance is reused without reset.

Global static registries (`WritableComparator.define`, `WritableFactories.setFactory`, `WritableName.setName/addName`, `CompressionCodecFactory.setCodecClasses`) are mutable process state. They are integration conveniences but can make tests order-dependent if not isolated.

## Dependencies And Integration Points

This chunk sits at the intersection of Hadoop common, filesystem APIs, Java IO, and MapReduce:

- Java IO primitives: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `DataInputStream`, `DataOutputStream`, `FilterInputStream`, `FilterOutputStream`, `IOException`, `Closeable`, and sockets via `IOUtils`.
- Hadoop filesystem APIs: `FileSystem`, `Path`, and `FSDataOutputStream` for persistent SequenceFile, MapFile, and SetFile storage.
- Hadoop configuration: `Configuration` and `Configurable` are used by generic/object/string serializers, codec factories, and file readers/writers.
- Hadoop progress reporting: `Progressable` is accepted by SequenceFile and MapFile writer/sorter APIs.
- Hadoop serializer framework: `SequenceFile.Writer` exposes serializer fields, showing integration with `org.apache.hadoop.io.serializer.Serializer`.
- Compression: `CompressionCodec`, codec factories, compressor/decompressor pools or implementations, and filename suffix detection integrate with file formats and job output settings.
- MapReduce: Javadocs explicitly refer to MapReduce keys/values, reduce outputs, map output compression type, and SequenceFile output format configuration.
- Logging: `CompressionCodecFactory.LOG` uses Apache Commons Logging.
- Java NIO charset APIs: `Text` uses `ByteBuffer`, `CharacterCodingException`, and `MalformedInputException` behavior for UTF-8 encoding/decoding.
- Security-sensitive class loading/reflection: object, writable-name, writable-factory, comparator, and codec-class APIs all depend on resolving classes from serialized names or configuration.

## Risks And Edge Cases

The highest compatibility risk is binary format drift. Changing primitive encodings, `Text` length encoding, variable-length integer rules, SequenceFile headers, sync marker handling, metadata serialization, or MapFile index layout would break persisted files and cross-version jobs.

Raw comparator correctness is critical. If a comparator interprets serialized bytes differently from the corresponding object's `compareTo`, SequenceFile sorting, MapFile lookup, partitioning, grouping, and merge behavior can diverge. Descending comparators and variable-length integer comparators are especially easy to get wrong because raw byte order does not always match numeric order.

Reusable buffers expose backing arrays directly. Callers must respect logical lengths, and implementations must avoid retaining mutable caller arrays in surprising ways unless documented. `BytesWritable(byte[])` explicitly uses the input as backing storage, so external mutation can affect object state.

Text handling has malformed UTF-8 branches. Replacement versus strict decoding must remain explicit; otherwise data-cleanup behavior can hide corrupt input or unexpectedly fail old workloads. `UTF8` deprecation also creates migration risk because old files may still contain or expect the legacy class.

`ObjectWritable`, `WritableName`, `WritableFactories`, and codec class lookup can instantiate classes by name or from configuration. That is a powerful extension mechanism but raises classpath, compatibility, and security risks in environments that deserialize untrusted data or run jobs with broad classpaths.

`MapFile` requires sorted appends. Writer APIs do not model in-place updates; callers must merge sorted change lists into new map directories. Violating sorted order can make indexes incorrect and lookups unreliable. Large index keys can also create reader memory pressure because the index is loaded entirely.

SequenceFile split/seek semantics depend on sync markers and exact positions returned by writers. Arbitrary seeks must use `sync`; direct `seek` to arbitrary offsets is documented as invalid. Compression mode complicates raw reads, block boundaries, and sync behavior.

Compression stream lifecycle is another risk area. `finish()` must not close the underlying stream, `resetState()` must not reset underlying output streams, and `end()` must be called when native resources exist. Buffered decompression plus underlying stream repositioning requires correct `resetState()` implementation to avoid stale buffered bytes.

Several APIs are deprecated but still present: `UTF8`, `SequenceFile.getCompressionType`, `SequenceFile.setCompressionType`, and a deprecated `SequenceFile.Reader.next(DataOutputBuffer)` raw API. Tests and migration code should verify both compatibility and warnings/alternate paths.

The JDiff XML itself can be incomplete at chunk boundaries. Research consumers should not treat this chunk as the full definition of `ArrayWritable` or `GzipCodec`; adjacent chunks are required for those complete APIs.

## Test Signals

Strong test coverage for this API family should include binary round trips for every `Writable` in the chunk: default construction, value mutation, `write`, `readFields` into reused instances, equality, hash behavior, and `compareTo`.

Comparator tests should compare object-level and raw-byte comparator results for the same values, including boundary values: booleans, negative/zero/positive ints and longs, floats including special values if supported by implementation, variable-length integer size boundaries, empty and non-empty byte arrays, UTF-8 strings with multibyte code points, and MD5 hash ordering.

Buffer tests should verify that `getData()`/`get()` expose extra capacity but only `getLength()`/`getSize()` bytes are valid; reset should reuse storage without leaking previous logical data. `readFully`, `skipFully`, and direct copy helpers should be tested against short reads and EOF.

Text tests should cover UTF-8 encode/decode, strict malformed-input exceptions, replacement behavior, `charAt`, `find`, append, clear, static `readString`/`writeString`, `validateUTF8`, `bytesToCodePoint`, and `utf8Length`. Compatibility tests should still read/write deprecated `UTF8`.

SequenceFile tests should create and read uncompressed, record-compressed, and block-compressed files with metadata. They should validate header-derived key/value classes, codec reporting, raw and object reads, `getCurrentValue`, exact `seek` to writer positions, `sync` from arbitrary offsets, `syncSeen`, `ValueBytes`, appendRaw, `getLength`, close behavior, and deprecated raw-read compatibility.

Sorter tests should sort multiple SequenceFiles with default and custom `RawComparator`s, vary memory and merge factor settings, test `sortAndIterate`, preserve or delete input segments according to flags, and compare output ordering against object-level comparators.

MapFile and SetFile tests should append sorted keys, reject or expose failures for out-of-order keys, verify index interval effects, run lookup paths (`seek`, `get`, `getClosest` before/after, `midKey`, `finalKey`, `next`, `reset`), validate `rename`/`delete`, and rebuild a missing/corrupt index with `fix` in dry-run and real modes.

Compression tests should exercise `CompressionCodecFactory` suffix lookup and suffix removal, codec class configuration, `DefaultCodec` and visible `GzipCodec` stream creation, compressor/decompressor reuse with `reset`, dictionary branches where supported, `finish` without closing underlying streams, and `CompressionInputStream.resetState()` after repositioning input.

Global-registry tests should isolate static state for `WritableComparator`, `WritableFactories`, `WritableName`, and codec class lists. Without isolation, one test's custom registration can mask failures or change behavior in later tests.
