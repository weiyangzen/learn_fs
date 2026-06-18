# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml lines 17994-24297

## Scope

This chunk is a JDiff public API snapshot for Apache Hadoop Common 2.8.3. The range starts at the tail of `org.apache.hadoop.io.FloatWritable`, covers most of the `org.apache.hadoop.io` serialization and binary-file API surface, the `org.apache.hadoop.io.compress` codec contracts, TFile helper APIs, serializer registrations including Avro serializers, log/metrics appenders and legacy metrics package documentation, and ends inside `org.apache.hadoop.metrics.spi.AbstractMetricsContext.close`. It is metadata and Javadoc, not implementation code, but it records public signatures, inheritance, deprecation state, exceptions, and file/stream format contracts that downstream compatibility depends on.

## Purpose

The central purpose of this slice is to define Hadoop Common's stable data interchange layer:

- `Writable`, `WritableComparable`, primitive writable wrappers, `Text`, map writables, object/generic writables, raw comparators, factories, and utility methods describe Hadoop's compact `DataInput`/`DataOutput` serialization protocol for MapReduce keys, values, RPC payloads, and persisted files.
- `SequenceFile`, `MapFile`, and `SetFile` document binary container formats used for flat key/value data, sorted file-backed maps, and sets.
- `WritableUtils`, `Text`, `MD5Hash`, and `WritableComparator` provide low-level byte encodings, zero-compressed integers, raw byte comparison, hashing, UTF-8 handling, and clone/read/write helpers.
- `org.apache.hadoop.io.compress` defines codec lookup, compression/decompression stream lifecycle, compressor pools, splittable compression, and direct `ByteBuffer` decompression.
- `org.apache.hadoop.io.file.tfile` exposes TFile compression/comparator constants and binary search/string/vint utilities.
- `org.apache.hadoop.io.serializer` and `.avro` expose Java, Writable, and Avro serialization adapters.
- The tail documents legacy log4j event counting and the deprecated original metrics API, including Ganglia emission and the SPI base context.

## Important APIs, Types, and Functions

### Writable Core

- `Writable` is the root serialization contract with `write(DataOutput)` and `readFields(DataInput)`. The docs explicitly tell implementers to reuse storage during deserialization where possible.
- `WritableComparable` extends `Writable` and `Comparable`, with a warning that `hashCode()` must be stable across JVM instances because Hadoop uses hashes for key partitioning.
- Primitive wrappers in this chunk include the end of `FloatWritable`, plus complete `IntWritable`, `LongWritable`, `ShortWritable`, `VIntWritable`, and `VLongWritable` entries. They expose default/value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `NullWritable` is a singleton zero-byte writable with `get()`, no-op `readFields`/`write`, and stable comparison/equality behavior for empty keys or values.
- `VersionedWritable` and `VersionMismatchException` support version-checked writable payloads; the chunk records them as part of the API list even though the most relevant details sit in the omitted middle of the `Text`/writable run.
- `GenericWritable` wraps one of a fixed set of `Writable` classes returned by subclass `getTypes()`. It is also `Configurable`, so configuration is propagated to wrapped configurable instances before deserialization.
- `ObjectWritable` serializes polymorphic objects by writing class identity and can handle `Writable`, `String`, primitives, and arrays. Its overload with `allowCompactArrays` distinguishes RPC/internal use from persisted/inter-cluster output where older cluster interoperability matters.
- `WritableFactories` and `WritableFactory` let non-public writable classes register construction hooks so `ObjectWritable` and related reflection paths can instantiate them.

### Collections and Comparators

- `MapWritable` extends `AbstractMapWritable` and implements `Map`, exposing normal map operations plus `readFields`/`write`. It tracks writable key/value classes for serialization.
- `SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap`, adding `comparator`, `firstKey`, `lastKey`, `subMap`, `headMap`, and `tailMap` over `WritableComparable` keys.
- `RawComparator<T>` compares serialized byte slices directly and also extends `Comparator`.
- `WritableComparator` implements `RawComparator` and `Configurable`. It provides global comparator registration via `define`, comparator lookup via `get(Class, Configuration)`, object comparison, optimized byte-slice comparison, byte parsing helpers (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`), and byte hashing/comparison. Registered comparators must be thread-safe.

### Text and Binary Utilities

- `Text` stores UTF-8 bytes and extends `BinaryComparable`. It exposes raw buffer access (`getBytes`, `getLength`), exact copy (`copyBytes`), byte-position search (`find`), Unicode scalar access (`charAt`), setters from strings, byte arrays, ranges, and other `Text`, append/clear operations, bounded `readFields(DataInput, maxLength)`, static `skip`, known-length reads, and string/UTF-8 byte conversion helpers.
- `Text.clear()` keeps the backing byte array for performance, which is a memory-retention and data-lifetime behavior callers must understand.
- `MD5Hash` is a writable comparable fixed-length MD5 wrapper with constructors from hex strings and byte arrays, stream/byte/string/UTF8 digest helpers, thread-local digester creation, `halfDigest`, `quarterDigest`, and hex `setDigest`.
- `MultipleIOException` bundles several `IOException` instances and has a static factory that returns a convenient `IOException`.
- `WritableUtils` provides compressed byte/string arrays, normal string arrays, clone/cloneInto, zero-compressed `writeVInt`/`writeVLong` and `readVInt`/`readVLong`, range-checked VInt reads, VInt sign/size decoding, enum read/write, `skipFully`, `toByteArray`, and `readStringSafely(maxLength)`.

### File Formats

- `SequenceFile` exposes default compression config and many `createWriter` overloads for `FileSystem`, `FileContext`, `FSDataOutputStream`, path creation options, replication, block size, metadata, progress, and compression codec/type. Many legacy overloads are deprecated in favor of `createWriter(Configuration, Writer.Option...)`.
- `SequenceFile.SYNC_INTERVAL` is the public sync marker interval. The Javadoc describes the shared header (`SEQ` magic/version, key class, value class, compression flags, codec, metadata, sync marker) and the three formats: uncompressed, record-compressed values, and block-compressed key/value length and data blocks. Block format uses zero-compressed integer lengths.
- `MapFile` is a sorted file-backed map directory with `data` and `index` files, constants `DATA_FILE_NAME` and `INDEX_FILE_NAME`, static `rename`, `delete`, and `fix` to rebuild corrupt indexes. The index is loaded fully into memory.
- `SetFile` extends `MapFile` as a file-backed key set.

### Compression

- `CompressionCodecFactory` maps file names, codec names, class names, and configured codec class lists to `CompressionCodec` instances/classes, and exposes `removeSuffix` and a diagnostic `main`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases. Input streams implement `Seekable`, expose `resetState()` for repositioned underlying streams, but default `seek` and `seekToNewSource` are unsupported. Output streams distinguish `finish()` from `close()` so compressed data can be finalized without closing the wrapped stream.
- `Compressor` and `Decompressor` model `Deflater`/`Inflater` style state machines: `setInput`, `needsInput`, dictionary handling, byte counters, `finish`/`finished`, produce/consume methods, `reset`, and `end`. `Decompressor` explicitly supports concatenated streams via `finished()` plus `getRemaining()`.
- `CompressorStream` and `DecompressorStream` provide concrete stream wrappers with protected compressor/decompressor, buffers, closed/eof state, and lifecycle methods.
- `BlockCompressorStream` and `BlockDecompressorStream` wrap block-oriented compression with explicit block headers and compression overhead sizing.
- `CodecPool` manages reusable compressor/decompressor instances and leased counts; this creates a shared resource lifecycle around codec use.
- `DefaultCodec` implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`; `GzipCodec` extends it with gzip-specific stream and direct decompressor creation; `BZip2Codec` exposes codec streams and codec extension behavior.
- `DirectDecompressionCodec` and `DirectDecompressor` add direct `ByteBuffer` decompression for native or zero-copy paths.
- `SplitCompressionInputStream` records adjusted split start/end; `SplittableCompressionCodec` creates split-aware streams for input split boundaries.

### TFile and Serializers

- `TFile` exposes supported compression algorithms and comparator construction with constants for `gz`, `lzo`, `none`, memory comparison, and Java class comparators.
- TFile `Utils` mirrors VInt/VLong/string helpers and lower/upper bound binary search functions for indexed blocks.
- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` represent TFile metadata block errors.
- `JavaSerialization`, `JavaSerializationComparator`, and `WritableSerialization` integrate Java object serialization and Hadoop `Writable` serialization with the `Serialization` extension point.
- Avro serializers include marker `AvroReflectSerializable`, `AvroReflectSerialization` with `AVRO_REFLECT_PACKAGES`, abstract `AvroSerialization` with `AVRO_SCHEMA_KEY`, and `AvroSpecificSerialization`. Reflect serialization accepts classes in configured packages or implementing the marker interface.

### Logging and Metrics

- `EventCounter` is a log4j `AppenderSkeleton` that counts fatal, error, and warn events for metrics exposure.
- `org.apache.hadoop.metrics` package docs define the legacy metrics model: context, record, metric names, tags, buffered updates, timer-based updater callbacks, and `ContextFactory` attributes loaded from `hadoop-metrics.properties`.
- `GangliaContext` extends deprecated `AbstractMetricsContext` and sends legacy metrics via UDP/Ganglia XDR formatting. It exposes protected XDR helpers, buffer/offset, `metricsServers`, and `datagramSocket`, and is deprecated in favor of `metrics2` Ganglia sinks.
- `AbstractMetricsContext` begins here as a deprecated SPI base implementing `MetricsContext`, with `init`, factory attribute lookup/table extraction, context/factory accessors, synchronized `startMonitoring`, `stopMonitoring`, `close`, and `isMonitoring`. The source range stops while documenting `close`, so later methods/fields are outside this chunk.

## Control Flow and State Behavior

This XML does not include implementation bodies, but the API contracts imply several important flows:

- Writable deserialization is pull-based: caller constructs or obtains an instance, then `readFields` mutates it from `DataInput`; serialization pushes object state to `DataOutput`.
- `ObjectWritable` and `GenericWritable` add type dispatch. `ObjectWritable` writes class identity into the stream, while `GenericWritable` writes a compact type code selected from `getTypes()`. Configuration is part of the deserialization setup for configurable wrapped values.
- `SequenceFile.createWriter` chooses a writer implementation from compression type and codec. Records then flow through uncompressed, record-compressed, or block-compressed layouts, with sync markers enabling reader resynchronization.
- `MapFile.fix` reads an existing `data` file and regenerates `index` entries unless `dryrun` is true. Normal `MapFile` use assumes sorted insertion and in-memory index loading.
- Compressor/decompressor streams are state machines: write/read methods feed buffers, `finish` drains final compressed data, `resetState` prepares reuse after stream repositioning or new blocks, and `end` releases native or codec-specific resources.
- Legacy metrics are buffered: `MetricsRecord.update()` stores data in an internal table, and context monitoring periodically emits records. `startMonitoring`/`stopMonitoring`/`close` control a background timer/emitter lifecycle.

## Persistence and Compatibility

- Writable encodings, VInt/VLong formats, `Text` length-prefixed UTF-8, `ObjectWritable` class names, `SequenceFile` headers, MapFile `data`/`index` directory layout, TFile constants, and codec suffix mappings are all persistent or wire-visible compatibility contracts.
- The `ObjectWritable.writeObject(..., allowCompactArrays)` documentation explicitly warns that compact arrays are appropriate for RPC/internal same-version usage but not persisted files or inter-cluster exchange.
- `SequenceFile` documents multiple historical file variants and deprecated writer overloads, so tests and migrations must preserve old overload behavior or intentionally route them to the option-based writer.
- Compression stream behavior is part of persistence: `finish()` must finalize compressed bytes without closing the underlying stream, and decompressor `getRemaining()` determines concatenated stream handling.
- `Text.clear()` does not wipe or free the backing byte array, which affects memory persistence and potential exposure of stale bytes through `getBytes()`.
- Legacy metrics and Ganglia APIs are deprecated but still public in this Hadoop version; removal or behavior changes would break older deployments using `hadoop-metrics.properties`, log4j appenders, or Ganglia factory attributes.

## Dependencies and Integration Points

- Core Java I/O: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `Closeable`, `File`, `FileChannel`, `WritableByteChannel`, `ByteBuffer`, sockets, and Java collections.
- Hadoop configuration and filesystem: `Configuration`, `Configurable`, `FileSystem`, `FileContext`, `Path`, `FSDataOutputStream`, `Options.CreateOpts`, and `Progressable`.
- Hadoop serialization extension points: `Serialization`, serializer/deserializer comparators, `WritableFactory`, reflection utilities, and Avro specific/reflect integrations.
- Compression integrations: Hadoop `CompressionCodec`, native/default codecs, direct decompression, split-aware input processing, and codec discovery from configuration and filename suffixes.
- Logging/metrics dependencies: Apache Commons Logging for cleanup logging, log4j for `EventCounter`, and the legacy Hadoop metrics `ContextFactory`/`MetricsContext` API plus Ganglia UDP/XDR emission.

## Risks and Edge Cases

- Binary compatibility risk is high: small changes in VInt/VLong, `Text`, `ObjectWritable`, `SequenceFile`, MapFile, or codec stream formats can make old data unreadable.
- API compatibility risk is high because this is a JDiff public API file; deprecated overloads still matter to downstream code.
- `ObjectWritable` class-name based deserialization and factory-based instantiation can fail when classes move, are not on the target classpath, or are non-public without a registered factory.
- Raw comparators must be thread-safe when globally registered and must match object-level `compareTo` semantics or sorting/partitioning can corrupt MapReduce behavior.
- `WritableComparable.hashCode()` instability across JVMs can mispartition data.
- `MapFile` loads indexes entirely into memory, so oversized keys or too dense indexes can cause memory pressure; corrupt index repair depends on correct key/value classes.
- `Text.getBytes()` returns the backing array, not an exact-length or immutable copy; callers must respect `getLength()` and avoid retaining stale data from `clear()`.
- Codec lifecycle bugs, especially missing `finish`, failing to return compressors/decompressors to `CodecPool`, or mutating decompressor input before `needsInput()`, can cause data corruption, native memory leaks, or corrupted concatenated stream handling.
- `CompressionInputStream.seek` is unsupported by default despite implementing `Seekable`; callers must only rely on seek behavior for codecs that explicitly support it.
- Legacy metrics/Ganglia APIs are deprecated; new code should prefer metrics2, but compatibility code still has to honor old configuration attributes and UDP packet encoding.

## Test Signals

Useful tests or validation signals for code governed by this API snapshot include:

- Round-trip serialization tests for every primitive writable, `NullWritable`, `Text`, `MapWritable`, `SortedMapWritable`, `GenericWritable`, `ObjectWritable`, `MD5Hash`, VInt/VLong boundaries, enum/string arrays, and `readStringSafely` maximum length failures.
- Golden-file compatibility tests for `SequenceFile` uncompressed, record-compressed, and block-compressed formats, including sync marker recovery, metadata, deprecated `createWriter` overloads, and codec selection.
- MapFile tests for sorted writes, index loading, `rename`, `delete`, and `fix`/`dryrun` behavior on missing or corrupt indexes.
- Comparator tests comparing raw byte comparator results against object `compareTo`, plus concurrency tests for registered `WritableComparator` instances.
- UTF-8 tests for `Text.charAt`, byte-position `find`, invalid/trailing bytes, `clear` memory behavior, bounded reads, and known-length reads.
- Compression tests for block and stream codecs, direct decompression, split compression boundaries, concatenated compressed streams, `finish` without closing underlying streams, `resetState`, `end`, and `CodecPool` lease accounting.
- Serializer tests for Java, Writable, Avro specific, and Avro reflect package/marker acceptance.
- Legacy metrics tests for `EventCounter` counts, `ContextFactory` property loading, buffered update emission, synchronized start/stop/close semantics, and Ganglia XDR field formatting/config attributes.
