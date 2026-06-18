# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.21.0.xml lines 12050-18346

## Research scope

This chunk is generated JDiff XML for the Hadoop Core 0.21.0 public API, not implementation source. The range starts inside `org.apache.hadoop.io.SequenceFile` at its compression and writer factory methods, covers the rest of the `org.apache.hadoop.io` package in this slice, the full visible `org.apache.hadoop.io.compress` package, and most of `org.apache.hadoop.io.file.tfile` through the beginning of `Utils.upperBound`. Conclusions are based on class/interface declarations, inheritance, implemented interfaces, visibility, deprecation metadata, method signatures, declared exceptions, fields, and embedded Javadocs.

The chunk is line-bounded. It begins after the opening of `SequenceFile` and ends before the closing text for `org.apache.hadoop.io.file.tfile.Utils`, so whole-class conclusions for those two types require adjacent chunks.

## Purpose

The covered API surface defines Hadoop's legacy binary data containers, serialization primitives, compression abstraction layer, and TFile block container. `SequenceFile`, `SetFile`, `SortedMapWritable`, `Text`, `Writable`, `WritableComparable`, `WritableComparator`, `WritableFactories`, and `WritableUtils` are foundational serialization and comparison APIs for MapReduce-era data exchange. The compression package abstracts stream codecs, reusable compressor/decompressor instances, split-aware compressed input, and default/gzip/bzip2 codecs. The TFile package exposes a sorted or unsorted byte-key/value container with block compression, named metadata blocks, range scanners, and utility encodings.

## Important APIs and types

`SequenceFile` exposes compression configuration helpers, many `createWriter` overloads, and the `SYNC_INTERVAL` constant. The documented file format has a common header containing the `SEQ` magic/version, key/value class names, compression booleans, optional codec class, metadata, and sync marker. Data can be uncompressed, record-compressed, or block-compressed; block compression separately stores compressed key lengths, keys, value lengths, and values.

`SequenceFile.CompressionType` is the enum for uncompressed, record-compressed, and block-compressed behavior. `SequenceFile.Metadata` is a `Writable` wrapper around `Text` name/value attributes with `get`, `set`, `getMetadata`, serialization, equality, hash, and string conversion.

`SequenceFile.Reader` is a synchronized closeable reader over filesystem paths or `FSDataInputStream` ranges. It reports key/value class names and classes, compression flags, codec, metadata, current position, and sync markers. It supports object/Writable reads, raw key/value reads through `DataOutputBuffer` and `ValueBytes`, `seek(long)` to writer-returned positions, and `sync(long)` to advance to the next sync marker from arbitrary offsets.

`SequenceFile.Sorter` provides external sort and merge operations for SequenceFiles. Constructors accept key/value classes or a `RawComparator`; runtime knobs include merge factor, memory budget, and `Progressable`. It can sort input paths to output paths, return a `RawKeyValueIterator`, merge `SegmentDescriptor` lists or path arrays, clone file attributes into a new writer, and write iterator records to a writer. `RawKeyValueIterator` exposes current raw key/value, progress, advancement, and close. `SegmentDescriptor` represents merge segments with offset, length, path, sync behavior, input preservation, raw key/value iteration, and cleanup that may close and delete temporary input.

`SequenceFile.ValueBytes` abstracts raw value payloads and can write uncompressed bytes, write already-compressed bytes without compressing uncompressed values, and report stored size. `SequenceFile.Writer` is a closeable writer with filesystem constructors, metadata/progress variants, class/codec getters, sync point creation, synchronized append overloads for `Writable` and object serializers, raw append, and synchronized `getLength()` values that are safe for later `Reader.seek`.

`SetFile` is a `MapFile`-backed file set. Its reader can seek, read next keys, and return a matching key or null. Its writer appends strictly increasing keys and has constructors keyed by class or comparator plus `SequenceFile.CompressionType`; the old no-configuration constructor is deprecated.

`SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap` for `WritableComparable` keys and `Writable` values. It exposes standard sorted-map views and mutations plus `Writable` serialization. `Stringifier<T>` is a closeable object/string round-trip interface.

`Text` is Hadoop's mutable UTF-8 `WritableComparable` string type. It exposes raw backing bytes and byte length, byte-position character lookup, byte-level find, string/byte/text setters, append, clear, UTF-8 read/write, equality/hash, static encode/decode helpers, static string read/write, UTF-8 validation, byte-to-codepoint conversion, and UTF-8 length calculation. `Text.Comparator` and `UTF8.Comparator` are raw `WritableComparator` implementations for byte-level comparison.

`TwoDArrayWritable`, `VIntWritable`, `VLongWritable`, `VersionedWritable`, and `VersionMismatchException` are small serialization helpers. `TwoDArrayWritable` serializes typed two-dimensional `Writable` arrays. `VIntWritable` and `VLongWritable` wrap variable-length integer encodings with setters, getters, `readFields`, `write`, equality, hash, compare, and string conversion. `VersionedWritable` prefixes serialized state with a version byte and throws `VersionMismatchException` on incompatible reads.

`Writable` and `WritableComparable` define Hadoop's core `write(DataOutput)` and `readFields(DataInput)` contract, with `WritableComparable` adding `Comparable`. `WritableComparator` centralizes raw byte and object comparison for `WritableComparable` keys, comparator registration, key instantiation, byte hashing, primitive reads from byte arrays, and variable-length integer decoding. `WritableFactories` and `WritableFactory` provide pluggable no-argument construction for `Writable` implementations. `WritableUtils` contains compressed byte/string helpers, array helpers, clone-by-serialization, deprecated `cloneInto`, vint/vlong encoding and decoding, enum serialization, exact skip, `Writable[]` to bytes, and bounded `readStringSafely`.

`BlockCompressorStream` and `BlockDecompressorStream` adapt streaming compressor interfaces to length-prefixed block formats. The compressor stream writes uncompressed block length followed by one or more length-prefixed compressed chunks; the decompressor stream reads block framing and supports `resetState`.

`CompressionCodec`, `Compressor`, and `Decompressor` are the main compression contracts. Codecs create compression/decompression streams, report compressor/decompressor classes, create codec instances, and expose default file extensions. Compressors and decompressors follow the `Deflater`/`Inflater` model: set input and dictionaries, report input/dictionary/finish states, transform buffers, expose byte counters where applicable, reset, release native resources with `end`, and for compressors reinitialize from `Configuration`.

`CompressionInputStream` and `CompressionOutputStream` are base classes for compressed streams with reset-state hooks; input streams also expose seek-like operations and position/source switching where subclasses support them. `CompressorStream` and `DecompressorStream` hold protected codec state, buffers, EOF/closed flags, and handle write/read, finish, reset, close, skip, available, mark, and reset behavior around concrete compressor/decompressor implementations.

`DefaultCodec`, `GzipCodec`, and `BZip2Codec` are concrete codec APIs. `DefaultCodec` is configurable and supplies the default compressor/decompressor implementations. `GzipCodec` specializes default behavior and has protected nested `GzipInputStream`/`GzipOutputStream` bridges around inflater/deflater streams. `BZip2Codec` implements `SplittableCompressionCodec`, supports `.bz2`, split-aware input ranges, and documents that direct `Compressor`/`Decompressor` methods are not implemented and may throw `UnsupportedOperationException`.

`CodecPool` is a global compressor/decompressor pool. It returns reusable instances for a codec, optionally reinitializing compressors with a `Configuration`, and accepts instances back through `returnCompressor` and `returnDecompressor`.

`SplitCompressionInputStream`, `SplittableCompressionCodec`, and `SplittableCompressionCodec.READ_MODE` describe compressed input that can align arbitrary requested byte ranges to codec-specific split boundaries. The read mode distinguishes continuous reading from block-boundary-aware reading, which matters for parallel processing of compressed files.

`org.apache.hadoop.io.file.tfile` defines `MetaBlockAlreadyExists`, `MetaBlockDoesNotExist`, `RawComparable`, `TFile`, `TFile.Reader`, `TFile.Reader.Scanner`, `TFile.Reader.Scanner.Entry`, `TFile.Writer`, and `Utils`. `TFile` is a byte-key/value container with optional sorting, block compression, metadata blocks, and seek by key or file offset. It exposes comparator construction, supported compression names (`none`, `lzo`, `gz`), command-line dump entry point, compression/comparator constants, and extensive tuning documentation for chunk size, filesystem buffers, block size, memory footprint, and compression choice.

`TFile.Reader` opens an `FSDataInputStream` and file length, reports comparator metadata, sorted status, entry count, first/last keys, comparators, metadata streams, nearby record/key by offset, and scanners by whole file, byte range, key range, or record-number range. Deprecated scanner overloads point callers to `createScannerByKey`.

`TFile.Reader.Scanner` is a closeable cursor over a whole file or bounded range. It supports `seekTo`, `rewind`, `seekToEnd`, `lowerBound`, `upperBound`, `advance`, `atEnd`, `entry`, and `getRecordNum`. Each move invalidates the previously returned `Entry`.

`TFile.Reader.Scanner.Entry` provides access to the current key/value. It can copy keys/values into `BytesWritable` or caller buffers, stream keys and values, write directly to an `OutputStream`, compare the entry key to byte buffers or `RawComparable`, and report equality/hash based on the pointed key/value. Value reads are single-use for a cursor position unless the cursor moves; `isValueLengthKnown()` must be checked before `getValueLength()`.

`TFile.Writer` writes an `FSDataOutputStream` positioned at zero with minimum block size, compression name, comparator name, and `Configuration`. It appends byte-array key/value pairs, supports stream-based key and value append with exact or unknown lengths, writes metadata blocks with explicit or default compression, prevents new key/value insertion after metadata block creation, releases resources on close without closing the underlying stream, and documents that an append exception leaves the TFile inconsistent except for close.

`org.apache.hadoop.io.file.tfile.Utils` provides TFile-specific variable-length integer/string encoding and generic `lowerBound`/`upperBound` binary search helpers, with comparator and natural-order overloads. The chunk ends inside the final `upperBound` Javadoc.

## Control flow and behavior

SequenceFile write flow is factory-driven. Callers choose key/value classes, filesystem path or raw `FSDataOutputStream`, compression type, optional codec, progress callback, metadata, and sometimes buffer/replication/block sizes. The writer emits the common header and then appends records according to compression mode. `sync()` inserts seekable markers; `getLength()` returns positions that a reader can later seek to safely, although block compression may position reads at the first key in the current block rather than exactly at the last appended key.

SequenceFile read flow is cursor-based. `next(key)` can skip values, `next(key, val)` materializes both, `getCurrentValue` reads the value for the last key, and raw methods separate key and value consumption for sort/merge paths. `seek(long)` requires a writer-synchronized position; `sync(long)` is the API for arbitrary offsets. `syncSeen()` tells callers whether the previous `next` crossed a sync mark.

SequenceFile sorting is an external sort/merge workflow. Inputs are read into sorted segments subject to memory limits, segment descriptors feed merge queues, merge factor controls fan-in, and temp directories hold intermediate files. `deleteInput`/`preserveInput` flags govern cleanup side effects, so callers need to understand when source or intermediate files may be removed.

Writable serialization flow is caller-managed and in-place. `readFields` implementations must fully overwrite object state from the stream; `WritableComparator` can avoid object allocation by comparing serialized byte ranges directly. `WritableFactories` provides construction hooks for deserialization frameworks that need instances before invoking `readFields`.

Compression stream flow follows Java zlib-like push/pull semantics. Output streams receive uncompressed bytes, feed a `Compressor`, write compressed bytes to the underlying stream, and require `finish()`/`close()` to flush codec state. Input streams pull compressed bytes, feed a `Decompressor`, and return uncompressed bytes until EOF. `resetState()` is the standard hook for stream reuse or boundary transitions.

Codec pooling is explicit. Callers borrow compressors/decompressors from `CodecPool`, use them with codec-created streams, and must return them when done. Failure to return pooled objects can leak native resources or reduce reuse; returning dirty state requires `reset`/`reinit` behavior to be correct.

Split compression flow lets a codec adjust requested `(start, end)` byte ranges to safe compressed-block boundaries. Clients ask for a split stream and then inspect `getAdjustedStart()` and `getAdjustedEnd()` to determine the actual covered compressed range.

TFile write flow enforces ordering and phase constraints. For sorted files, keys must obey the selected comparator. `append` writes complete key/value pairs in one call; `prepareAppendKey` and `prepareAppendValue` expose staged streams that must be closed in order and must write exactly the advertised lengths when lengths are not `-1`. Adding a metadata block ends key/value insertion. Closing finalizes internal indexes and metadata but deliberately leaves the caller-owned `FSDataOutputStream` open.

TFile read flow is scanner-based. A reader creates scanners over file, byte, key, or record ranges. Scanners maintain a cursor and invalidate previous `Entry` handles after movement. Entries allow copying or streaming current key/value data, but values are not cached and can only be consumed once per cursor position through the value-copy or value-stream APIs.

## State and persistence behavior

The XML itself persists API metadata for compatibility comparison. Runtime persistence comes from the documented file formats and `Writable` contracts.

SequenceFiles persist key/value class names, compression metadata, codec class names, user metadata, sync markers, and serialized records. This makes class names, serializer behavior, compression selection, sync interval, and metadata serialization part of the compatibility surface. `SequenceFile.Metadata`, `SortedMapWritable`, `Text`, primitive writable wrappers, array writables, and other `Writable` types persist their state to `DataOutput`/`DataInput`.

`WritableComparator`, `WritableFactories`, and `CodecPool` maintain process-local registries or pools. These are not filesystem-persistent, but they affect deserialization, comparison, and native codec reuse for the lifetime of a JVM.

Compression streams keep transient buffers, closed/EOF flags, codec state, optional native resources, byte counters, and stream positions. `Compressor.end()` and `Decompressor.end()` release resources. `CompressionInputStream.seek`/`seekToNewSource` only make sense when the wrapped stream and codec implementation can honor them.

TFile persists data blocks, meta blocks, block indexes, comparator names, compression algorithm names, and chunked values. Configuration keys such as `tfile.io.chunk.size`, `tfile.fs.output.buffer.size`, and `tfile.fs.input.buffer.size` influence memory use and value-length observability but must still produce readable files under the documented format. TFile reader/scanner state is cursor-local and invalidates entries on movement or close.

`SetFile` and `SequenceFile.Sorter` can create, merge, delete, or preserve filesystem paths. Sorter cleanup and SetFile append ordering are observable filesystem side effects rather than mere in-memory behavior.

## Dependencies and integration points

The `org.apache.hadoop.io` APIs integrate with `org.apache.hadoop.fs.FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `Path`, `Configuration`, `Progressable`, `Progress`, `RawComparator`, `DataInput`, `DataOutput`, `DataOutputBuffer`, Java collections, `Closeable`, `Comparable`, and Hadoop serializer APIs.

Compression APIs integrate with `Configuration`, Java `InputStream`/`OutputStream`, `java.util.zip`-style compressor semantics, optional native codec implementations, filesystem split processing, and file extensions used by input format detection.

TFile integrates with `FSDataInputStream`, `FSDataOutputStream`, `Configuration`, `BytesWritable`, `RawComparable`, `RawComparator`, `WritableComparator`, and Java collection binary-search patterns. Comparator names bridge language-independent byte comparison (`memcmp`) and Java class comparators (`jclass:<RawComparator class>`).

JDiff consumers depend on exact signatures, visibility, deprecation strings, exceptions, and fields in this XML. Even documentation-only API contracts such as single-use TFile values, SequenceFile seek requirements, and BZip2 unsupported compressor paths are important compatibility signals for downstream code and tests.

## Risks and edge cases

SequenceFile compatibility is sensitive to file headers, class names, serializer choice, codec availability, sync marker placement, and raw-read ordering. `Reader.seek` must only use positions returned by `Writer.getLength`; arbitrary offsets require `sync`, or readers can land inside records or compressed blocks.

SequenceFile sorting can delete inputs or temporary segments. Incorrect `deleteInput`, `preserveInput`, or cleanup handling can cause data loss or orphaned temporary files. Sort performance depends heavily on efficient key `readFields` implementations with low allocation.

`ValueBytes.writeCompressedBytes` does not compress uncompressed bytes. Callers that assume it always produces compressed output can create malformed or inefficient files.

Writable implementations must reset all mutable state in `readFields`; stale fields, mismatched vint/vlong encodings, missing factories, or incompatible comparator byte logic can break RPC, MapReduce shuffle, SequenceFile sorting, and persisted data reads.

`Text` APIs use byte offsets, not Java `char` indexes, for several operations. Invalid UTF-8, trailing-byte positions, raw backing arrays beyond `getLength()`, and oversized string reads are recurring boundary risks.

Compression APIs are resource-sensitive. Streams often need `finish()` before close, codecs may hold native state, pooled compressors must be returned, and `resetState`/`reset` must clear all prior input. BZip2 advertises split support but not direct compressor/decompressor object support in this version.

Splittable compression may adjust requested ranges. Input formats must use adjusted start/end values and handle block-boundary semantics; otherwise parallel readers can duplicate or skip data.

TFile has strict ordering and lifecycle constraints. Sorted writers require comparator-consistent key order, active key/value append streams must be closed before the next phase, value/key advertised lengths must be exact, adding metadata blocks forbids further data entries, and append exceptions leave only `close()` as a legitimate follow-up. Reader entries and scanner positions are invalidated by movement or close, and values are single-use at a cursor position.

TFile memory and performance tradeoffs are explicit: small blocks increase index memory and flush overhead, large blocks hurt random access, gzip costs more CPU than LZO, and concurrent scanners over one reader may serialize I/O because of `seek()+read()` use.

## Test signals

Useful validation for this chunk should include:

- JDiff/XML checks that class and interface boundaries, visibility, deprecation strings, declared exceptions, field names, and method signatures remain stable for the covered line range, while accounting for partial `SequenceFile` and `Utils` boundaries.
- SequenceFile tests for all compression types, metadata round trips, codec selection, raw and Writable read paths, `getLength`/`seek` interoperability, arbitrary-offset `sync`, `syncSeen`, raw value handling, and object serializer append paths.
- SequenceFile sorter tests for comparator ordering, memory/factor settings, progress callbacks, sorted output, merge fan-in, `RawKeyValueIterator` lifecycle, segment cleanup, and delete-input/preserve-input behavior.
- Writable tests for `Text` UTF-8 validation and byte-offset APIs, variable-length integer boundaries, `WritableComparator` raw primitive reads and byte comparison, `WritableFactories` construction, `SortedMapWritable` ordering/serialization, and clone-by-serialization correctness.
- Compression tests for compressor/decompressor state transitions, `finish`/`reset`/`end`, stream close behavior, block framing, partial reads/writes, codec file extensions, `CodecPool` borrow/return/reinit behavior, BZip2 unsupported compressor methods, and split input adjusted offsets.
- TFile tests for sorted and unsorted writes, key-size limits, block compression choices, metadata block creation and duplicate/missing exceptions, stream-based key/value append ordering, exact advertised lengths, append failure handling, close without closing the underlying `FSDataOutputStream`, scanner ranges by byte/key/record number, lower/upper bound behavior, single-use value reads, entry invalidation, comparator names, and utility vint/string/binary-search helpers.
