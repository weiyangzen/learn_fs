# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SequenceFile.java

## Purpose

`SequenceFile.java` implements Hadoop's binary flat-file container for ordered key/value records. It is the central IO format used by older MapReduce paths and by `MapFile`, `SetFile`, sort/merge utilities, and raw key/value pipelines. The class is a static namespace with nested `Writer`, `Reader`, compression-specific writer subclasses, metadata support, raw value abstractions, and an external sorter/merger.

The file supports three on-disk layouts under a common `SEQ` header: uncompressed records, record-compressed values, and block-compressed key/value groups. It also preserves compatibility with legacy sequence file versions, older `UTF8` class-name encoding, and the `WritableName` alias mechanism.

## Important APIs, types, and functions

- `CompressionType` selects `NONE`, `RECORD`, or `BLOCK`; `getDefaultCompressionType()` and `setDefaultCompressionType()` bind this to `io.seqfile.compression.type`.
- `createWriter(Configuration, Writer.Option...)` is the preferred constructor surface. Deprecated overloads adapt legacy `FileSystem`, `FileContext`, stream, replication, block size, progress, codec, and metadata signatures into `Writer.Option` values.
- `ValueBytes`, `UncompressedBytes`, and `CompressedBytes` allow raw sorting and merging without materializing application value objects. `CompressedBytes` can copy compressed bytes or inflate them with the configured codec.
- `Metadata` serializes a `TreeMap<Text,Text>` after version 6 headers and provides copy-out access via `getMetadata()`.
- `Writer` writes headers, records, sync markers, serializers, stream capabilities, and append-mode validation. Its options include `file`, `stream`, `bufferSize`, `replication`, `blockSize`, `appendIfExists`, `keyClass`, `valueClass`, `metadata`, `progressable`, `compression`, and `syncInterval`.
- `RecordCompressWriter` overrides `append()` and `appendRaw()` to compress only values.
- `BlockCompressWriter` buffers key lengths, keys, value lengths, and values, compresses each block independently, and emits a sync marker at each block flush.
- `Reader` parses headers, resolves key/value classes, configures decompressors/deserializers, reads object and raw records, supports lazy value decompression for blocks, `seek()`, `sync()`, checksum-skip behavior, and exposes metadata and compression details.
- `Sorter` performs external sort and merge over sequence files using raw comparators, temp segment indexes, priority-queue merging, and `RawKeyValueIterator`.

## Control flow

Writer creation first resolves options, selects the writer subclass by compression type, opens or reuses the output stream, and calls `init()`. `init()` creates key/value serializers from `SerializationFactory`, configures codecs and compressors, opens serializers over `DataOutputBuffer` instances, then either writes a fresh header or emits a sync marker for append mode. Append mode opens a header-only reader against the existing file, checks key/value classes, sequence-file version, compression type, and codec class, adopts existing metadata and sync bytes, and appends to the file.

Uncompressed and record-compressed appends serialize key and value into a shared buffer, check that the key length is non-negative, write a sync marker when the sync interval has elapsed, then write record length, key length, and payload bytes. Record compression resets the codec stream per value. Block compression serializes keys and values into separate buffers, stores variable-length key/value lengths, and calls `sync()` once the configured block byte threshold is reached; block `sync()` writes the sync marker, record count, compressed key lengths, compressed keys, compressed value lengths, and compressed values.

Reader initialization seeks to the requested start, calculates the read end, parses the magic/version and version-dependent class-name encoding, reads compression flags, codec class, metadata, and sync bytes, then constructs deserializers and codec streams unless it is a header-only temporary reader. Non-block reads use `readRecordLength()` to skip sync markers and detect EOF, then load key/value bytes into buffers. Block reads call `readBlock()`, validate the sync marker, load compressed key blocks immediately, and load value blocks lazily only when `getCurrentValue()` or raw value access requires them. `sync(long)` scans for the next sync hash from an arbitrary position.

The sorter runs a sort pass that reads raw records into memory-limited segments, sorts key offsets with `MergeSort` and a raw comparator, writes sorted temp segments plus an index, then repeatedly merges segments with `MergeQueue`. Merge fan-in is adjusted by `getPassFactor()` to avoid inefficient final passes. `SegmentDescriptor` opens range-limited readers, optionally ignores sync for temp files, and deletes inputs unless preservation is requested.

## State and persistence behavior

The persistent state is the sequence-file byte stream: header, class names, compression flags, codec name, metadata, sync hash, records, and optional compressed blocks. Sync markers are 4-byte escape values followed by a 16-byte hash generated from a UID and current time; they make split recovery and arbitrary-position synchronization possible. Writers own or borrow streams depending on `file` versus `stream` options, and `ownStream()` is used by `FileContext` construction.

Runtime state includes reusable data buffers, serializers/deserializers, pooled compressors/decompressors, block-buffer counts, sync positions, and raw-value buffers. `close()` returns compressors/decompressors to `CodecPool`, closes serializers/deserializers, and either closes or flushes the underlying stream depending on ownership. The reader tracks `headerEnd`, `end`, `keyLength`, `recordLength`, `syncSeen`, and block counters to coordinate raw-key, raw-value, and object reads.

## Dependencies and integration points

This file integrates with Hadoop FS APIs (`FileSystem`, `FileContext`, `FSDataInputStream`, `FSDataOutputStream`, `FutureDataInputStreamBuilder`, create/open options), configuration keys, `Writable`, `WritableComparable`, `WritableComparator`, `WritableUtils`, `Text`, `UTF8`, `WritableName`, compression codecs and codec pools, serialization factories, `ReflectionUtils`, `Progressable`, `Progress`, `MergeSort`, and `PriorityQueue`. `MapFile` and `SetFile` build their persistent data files on this format. The raw comparator hook is important for MapReduce sort paths because it avoids deserializing keys for every comparison.

## Risks and edge cases

- Sequence-file compatibility is version-sensitive. Header parsing switches from `UTF8` to `Text` class names at version 4, adds custom codecs at version 5, and metadata at version 6.
- Append mode depends on exact class identity and codec class equality; subclass-compatible serializers are not accepted.
- `Writer` assumes a `CompressionOption` is present by the time the constructor runs. The public factory prepends one, but direct internal construction must preserve that invariant.
- Block compression's lazy value decompression has coupled counters (`noBufferedKeys`, `noBufferedValues`, `valuesDecompressed`); mixing raw key-only, raw value, and object access incorrectly can misalign streams.
- `Reader.next(DataOutputBuffer)` uses recursion after checksum handling. Repeated checksum failures could recurse deeply when checksum skipping is enabled.
- `sync(long)` scans byte-by-byte for a sync hash and relies on the escape offset convention; corrupted files or false positives are handled only by sync hash equality.
- `Metadata.hashCode()` is intentionally unusable under assertions and otherwise returns a constant, so metadata should not be used as a hash-map key.
- The sorter deletes temp and optionally input files during segment cleanup; merge error paths need tests to ensure readers close and preserved inputs survive.

## Test signals

High-value tests should round-trip all compression types, custom codecs, metadata, sync intervals, stream-owned and file-owned writers, append mode, and header-only readers. Split/sync tests should seek into the middle of files and validate `syncSeen()`. Raw API tests should cover `nextRawKey()` followed by `nextRawValue()` for compressed and block-compressed files. Sorter tests should cover multi-segment sort, multi-pass merge, delete-input behavior, progress reporting, raw comparator ordering, and temp segment index cleanup. Corruption tests should cover bad magic, future version, wrong sync hash, checksum-skip configuration, missing serializers/deserializers, negative lengths, and mismatched append options.
