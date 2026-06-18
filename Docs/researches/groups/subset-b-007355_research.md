# subset-b-007355 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SequenceFile.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SequenceFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SetFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SetFile.java

## Purpose

`SetFile.java` provides a file-backed sorted set abstraction by specializing `MapFile` with `NullWritable` values. It stores only ordered keys in the public API while relying on the underlying `MapFile` index/data structure and `SequenceFile` storage.

## Important APIs, types, and functions

- `SetFile` extends `MapFile` and has no public top-level constructor.
- `SetFile.Writer` extends `MapFile.Writer`; constructors accept a key class or `WritableComparator`, directory name, `FileSystem`, `Configuration`, and `SequenceFile.CompressionType`.
- `Writer.append(WritableComparable key)` appends the key paired with `NullWritable.get()`.
- `SetFile.Reader` extends `MapFile.Reader`; constructors accept the directory and optional comparator.
- `Reader.seek()`, `Reader.next(WritableComparable key)`, and `Reader.get(WritableComparable key)` expose set-style membership and iteration over keys.

## Control flow

Writes are delegated to `MapFile.Writer`, which enforces sorted key insertion and manages index/data files. `SetFile.Writer.append(key)` simply forwards `append(key, NullWritable.get())`. Reads delegate `seek()` and `next(key, NullWritable.get())` to `MapFile.Reader`; `get(key)` seeks to the candidate key and reads it into the same key object when present.

## State and persistence behavior

There is no independent state beyond the inherited `MapFile` writer/reader state. On disk, a set is a `MapFile` directory containing sorted keys and `NullWritable` values. The strict key ordering requirement is inherited from `MapFile.Writer`; violating it should fail in the underlying writer path.

## Dependencies and integration points

The class depends on `MapFile`, `NullWritable`, `WritableComparable`, `WritableComparator`, `SequenceFile.CompressionType`, `FileSystem`, `Path`, and `Configuration`. It is an adapter for code that wants set semantics while reusing MapFile's sorted storage and lookup facilities.

## Risks and edge cases

- `Reader.get(key)` mutates and returns the same key object supplied by the caller; callers must not expect an independent object.
- The writer requires strictly increasing keys; duplicate or out-of-order keys are a `MapFile` correctness issue.
- The deprecated constructor silently creates a new default `Configuration`, which can miss caller-specific serializers, codecs, or filesystem settings.
- Type safety is raw-era Hadoop style: incorrect key/comparator combinations fail at runtime.

## Test signals

Tests should write sorted keys, verify iteration, seek, exact `get()`, missing-key behavior, compression handling, and enforcement of out-of-order or duplicate appends. Compatibility tests should check both comparator and key-class constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SetFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ShortWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ShortWritable.java

## Purpose

`ShortWritable.java` is Hadoop's mutable `WritableComparable` wrapper for a Java `short`. It serializes as a fixed two-byte big-endian `DataOutput.writeShort()` value and supplies object and raw-byte comparison support.

## Important APIs, types, and functions

- `ShortWritable()` and `ShortWritable(short)` construct empty or initialized values.
- `set(short)` and `get()` mutate and read the wrapped primitive.
- `readFields(DataInput)` and `write(DataOutput)` implement fixed-width binary serialization.
- `equals()`, `hashCode()`, `compareTo()`, and `toString()` provide value semantics.
- Nested `Comparator` extends `WritableComparator` and compares serialized shorts using `readUnsignedShort()` then casting to `short`.
- The static initializer registers the optimized comparator with `WritableComparator.define()`.

## Control flow

Serialization and deserialization are single primitive operations. Object comparison reads the two instance fields and returns `-1`, `0`, or `1`. Raw comparison decodes two bytes from each serialized key, casts them to signed shorts, and applies the same ordering without object allocation.

## State and persistence behavior

The only mutable state is `private short value`. Persisted form is exactly two bytes. The hash code is the signed short widened to `int`, so it is stable across JVMs.

## Dependencies and integration points

This class depends on the `WritableComparable` contract and `WritableComparator` utilities. It can be used as a MapReduce key/value and benefits from the registered raw comparator in sort paths.

## Risks and edge cases

- The raw comparator must preserve signed short ordering; the implementation reads unsigned bytes then casts to `short`, which is intentional.
- There is no null handling in `compareTo()`.
- Mutability means instances used as keys in Java collections can break collection invariants if mutated after insertion.

## Test signals

Tests should round-trip boundary values (`Short.MIN_VALUE`, `-1`, `0`, `1`, `Short.MAX_VALUE`), compare object and raw comparator ordering, verify hash/equality, and confirm serialized length is two bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ShortWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Sizes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Sizes.java

## Purpose

`Sizes.java` is a constants holder for common binary byte sizes. It avoids repeated magic numbers for powers of two and selected MiB multiples.

## Important APIs, types, and functions

- `Sizes` is `final` and contains only public static final integer constants.
- Constants run from `S_0`, `S_256`, `S_512`, `S_1K` through `S_32M`, plus `S_5M` and `S_10M`.
- Larger constants are built by left-shifting the previous constant, preserving compile-time constant behavior.

## Control flow

There is no executable control flow beyond class initialization of constants.

## State and persistence behavior

There is no mutable state and no serialization. Constants are inlined by Java compilers where used.

## Dependencies and integration points

The class only depends on Hadoop classification annotations. It is a small public evolving utility for IO and configuration code that needs readable byte-size constants.

## Risks and edge cases

- Javadoc comments for `S_2K`, `S_4K`, `S_8M`, `S_16M`, and `S_32M` contain wording mistakes about KiB/MiB labels, though the numeric constants are correct.
- Values are `int`; this file intentionally stops far below integer overflow.

## Test signals

Compile-time or unit checks can assert key values such as `S_1K == 1024`, `S_1M == 1048576`, `S_5M == 5 * S_1M`, and `S_10M == 10 * S_1M`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Sizes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SortedMapWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SortedMapWritable.java

## Purpose

`SortedMapWritable.java` implements a writable `SortedMap` whose keys are `WritableComparable` and whose values are `Writable`. It extends `AbstractMapWritable` to serialize a compact class-id table before the map entries and uses a `TreeMap` for natural key ordering.

## Important APIs, types, and functions

- `SortedMapWritable<K extends WritableComparable<? super K>>` implements `SortedMap<K, Writable>`.
- Constructors initialize an empty `TreeMap` or copy another `SortedMapWritable`.
- Map and sorted-map methods delegate to `instance`: `firstKey`, `lastKey`, `headMap`, `tailMap`, `subMap`, `entrySet`, `keySet`, `values`, `put`, `putAll`, `remove`, `size`, and related queries.
- `put()` registers both key and value classes with `AbstractMapWritable.addToMap()`.
- `readFields()` reads the class-id table, entry count, then byte class ids and object payloads using `ReflectionUtils.newInstance()`.
- `write()` emits the class-id table, entry count, class ids, and serialized key/value payloads.

## Control flow

Writes first call `super.write(out)` so the class-id registry is persisted. They then write the number of entries and iterate in sorted-key order, writing one byte id plus object bytes for each key and value. Reads reverse the process: `super.readFields(in)` loads the registry, then the entry count drives a loop that instantiates key and value classes by id, calls `readFields()`, and inserts into the `TreeMap`.

## State and persistence behavior

The mutable state is the `TreeMap` plus class-id mappings inherited from `AbstractMapWritable`. Persisted data includes enough class metadata for heterogeneous writable values and keys, but ordering after read is determined by the natural ordering of key objects. The deserializer does not clear `instance` before loading entries, so reading into a reused object can retain preexisting entries if not cleared externally.

## Dependencies and integration points

This class depends on `AbstractMapWritable`, `Writable`, `WritableComparable`, `ReflectionUtils`, and Java `SortedMap`/`TreeMap`. It is the sorted variant of Hadoop map-writable containers and integrates with standard `Writable` serialization pipelines.

## Risks and edge cases

- `comparator()` always returns `null`, so custom comparators are not serialized or preserved.
- Reusing an object for `readFields()` without `clear()` can merge old and new state.
- `in.readInt()` entry count is not validated for negative or excessive values before looping.
- Class ids are bytes; correctness relies on `AbstractMapWritable` registry consistency.
- Mutating key objects after insertion can corrupt `TreeMap` ordering.

## Test signals

Tests should cover sorted iteration order, copy construction, heterogeneous writable values, class-id preservation across serialization, empty maps, equality/hash behavior, sub-map views, and read-into-reused-instance behavior. Negative or corrupted entry counts are useful fuzz cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SortedMapWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Stringifier.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Stringifier.java

## Purpose

`Stringifier.java` defines a small closeable interface for converting objects to and from string representations. Hadoop uses this style where objects need to be stored in text-only carriers such as configuration values.

## Important APIs, types, and functions

- `Stringifier<T>` extends `java.io.Closeable`.
- `toString(T obj)` converts an object to its string form.
- `fromString(String str)` restores an object from a string form.
- `close()` releases implementation resources and can throw `IOException`.

## Control flow

The interface has no implementation control flow. Implementations define encoding, decoding, and resource cleanup behavior.

## State and persistence behavior

State depends entirely on implementations. The interface implies a persisted textual representation, but does not prescribe format, versioning, character set, null handling, or schema.

## Dependencies and integration points

The only runtime dependency is `IOException` and `Closeable`; annotations mark it public and stable. Implementations commonly integrate with Hadoop serializers or base64-like encodings for configuration persistence.

## Risks and edge cases

- The method name `toString(T)` can be confused with `Object.toString()` but has checked `IOException`.
- Round-trip guarantees are not specified, so callers must know implementation-specific compatibility rules.
- Null input/output semantics are not defined by the interface.

## Test signals

Implementation tests should verify round-trip behavior, malformed input errors, close idempotence, null handling, and compatibility of strings stored across versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Stringifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Text.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Text.java

## Purpose

`Text.java` is Hadoop's mutable UTF-8 byte string type. It stores string content as standard UTF-8 bytes, serializes length with Hadoop variable-length integers, compares at the byte level, and provides utility functions for UTF-8 encoding, decoding, validation, search, and code-point traversal.

## Important APIs, types, and functions

- `Text` extends `BinaryComparable` and implements `WritableComparable<BinaryComparable>`.
- Constructors accept empty, `String`, another `Text`, or a byte array.
- `getBytes()`, `copyBytes()`, `getLength()`, and `getTextLength()` expose raw storage and logical character count.
- `set(String)`, `set(byte[])`, `set(Text)`, `set(byte[], int, int)`, `append()`, and `clear()` mutate content.
- `charAt(int)` and `find(String, int)` operate on byte positions without fully converting the backing buffer.
- `readFields()`, bounded `readFields(in, maxLength)`, `readWithKnownLength()`, `write()`, and bounded `write(out, maxLength)` implement serialization.
- Nested `Comparator` skips the variable-length size prefix and compares raw UTF-8 bytes; it is registered with `WritableComparator`.
- Static utilities include `encode`, `decode`, `readString`, `writeString`, `validateUTF8`, `bytesToCodePoint`, and `utf8Length`.

## Control flow

String construction encodes through a thread-local UTF-8 `CharsetEncoder` configured to report malformed input by default, temporarily switching to replacement when requested. `set(byte[], start, len)` and `append()` grow the backing array through `ensureCapacity()` and mark cached `textLength` unknown. Serialization writes a vint byte length and then the active bytes. Deserialization reads the vint length, optionally checks a maximum, ensures capacity, and reads bytes directly.

`find()` encodes the search string once, scans the source byte buffer for the first byte, and then compares target bytes in-place using buffer marks. `validateUTF8()` is a small finite-state machine over leading and trailing bytes, including checks for overlong forms, surrogate ranges, and code points above U+10FFFF. `bytesToCodePoint()` uses lookup tables to decode from the current `ByteBuffer` position and advances that buffer by the code-point byte length.

## State and persistence behavior

The object stores `byte[] bytes`, active byte `length`, and cached `textLength` in UTF-16 code units. `getBytes()` exposes the backing array, including unused capacity, while `copyBytes()` returns an exact copy. `clear()` resets logical length but keeps allocated memory; `set(new byte[0])` releases the buffer to the shared empty array. Persisted form is vint length followed by raw UTF-8 bytes.

## Dependencies and integration points

`Text` depends on `WritableUtils` for vint encoding and skipping, `WritableComparator` and `BinaryComparable` for byte ordering and hashing, Java NIO charset encoders/decoders, and Avro's `@Stringable`. It is used throughout Hadoop for class names, metadata, configuration-like strings, map keys, and sequence-file headers.

## Risks and edge cases

- `getBytes()` exposes mutable internal storage; callers must respect `getLength()`.
- `charAt(position)` accepts a byte offset, not a Java character index, and returns `-1` for trailing bytes or invalid positions.
- `ensureCapacity()` allocates a new array and does not copy existing data; callers must copy when preserving content, as `append()` does.
- Bounded `readFields(in, maxLength)` rejects `newLength >= maxLength`, so the maximum is exclusive despite wording that may imply inclusive.
- `validateUTF8()` does not explicitly check that the final state returns to lead-byte state after an incomplete trailing sequence, which is a boundary worth testing.
- Static thread-local encoders/decoders are temporarily reconfigured for replacement mode and then reset; exception paths could leave configuration changed if future edits remove the reset behavior.
- `decode()` defaults to replacement, while `validateUTF8()` is strict; callers must choose deliberately.

## Test signals

Tests should cover ASCII, multibyte, surrogate pairs, malformed byte sequences, overlong encodings, incomplete sequences, `charAt()` on lead/trailing/out-of-range positions, `find()` with byte offsets, serialization limits, exact versus backing bytes, `clear()` memory retention, comparator ordering against `BinaryComparable`, and `utf8Length()` for valid and invalid surrogate pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Text.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/TwoDArrayWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/TwoDArrayWritable.java

## Purpose

`TwoDArrayWritable.java` is a writable wrapper for a rectangular or ragged two-dimensional matrix of `Writable` values of one declared class.

## Important APIs, types, and functions

- Constructors take a `Class valueClass` and optionally a `Writable[][]`.
- `set()` and `get()` replace or return the internal matrix.
- `toArray()` builds a Java two-dimensional array with component type `valueClass` using reflection.
- `readFields()` reads row count, per-row lengths, instantiates values with `valueClass.newInstance()`, and reads each value.
- `write()` emits row count, row lengths, and each element payload.

## Control flow

Serialization writes matrix shape first so the reader can allocate all rows before reading cells. Deserialization constructs empty row arrays, then loops through every coordinate, creates a new `valueClass` instance, calls `readFields()`, and stores it. `toArray()` creates a two-dimensional reflective array whose first dimension is the row count and then replaces each row with an array sized to the corresponding row length.

## State and persistence behavior

State is the declared value class and mutable `Writable[][] values`. Persisted form stores no class name, so the reader must be constructed with the same `valueClass` used for writing. Ragged row lengths are preserved.

## Dependencies and integration points

The class depends on `Writable`, Java reflection `Array`, and the deprecated zero-argument `Class.newInstance()` pattern. It is a generic container for writable matrices in Hadoop serialization paths.

## Risks and edge cases

- There is no no-argument constructor, so frameworks must know the value class at construction time.
- Deserialization does not validate negative row counts or row lengths.
- `valueClass.newInstance()` requires an accessible no-argument constructor and wraps reflection failures as unchecked `RuntimeException`.
- Null `values`, null rows, or null cells cause `NullPointerException` during write or `toArray()`.
- The class stores raw `Class`, so type safety is runtime-only.

## Test signals

Tests should cover empty matrices, ragged matrices, round-trip with a simple writable, `toArray()` component type and row lengths, missing default constructor failures, null element failures, and corrupted negative dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/TwoDArrayWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/UTF8.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/UTF8.java

## Purpose

`UTF8.java` is the deprecated predecessor to `Text`. It stores strings as UTF-8 bytes with a 16-bit unsigned length prefix, supports legacy sequence-file class-name decoding, and preserves older Hadoop serialization compatibility.

## Important APIs, types, and functions

- `UTF8` implements `WritableComparable<UTF8>`.
- Constructors accept empty, `String`, or another `UTF8`.
- `set(String)` encodes with `writeString()` into a thread-local `DataOutputBuffer`, then copies the bytes after the two-byte length prefix.
- `readFields()` reads an unsigned short length and then bytes; `write()` writes a short length and raw bytes.
- `toString()` decodes legacy UTF-8 with replacement-style error logging; `toStringChecked()` throws `UTFDataFormatException` on malformed input.
- Static utilities include `getBytes`, `fromBytes`, `readString`, `writeString`, `utf8Length`, and manual character read/write helpers.
- Nested `Comparator` compares serialized UTF8 values after skipping the two-byte length prefix and is registered with `WritableComparator`.

## Control flow

Encoding computes UTF-8 byte length, rejects strings above `0xffff` bytes, writes a two-byte length, then writes one-, two-, three-, or four-byte encodings, handling supplementary code points through surrogate pairs. Decoding reads the unsigned byte length, then manually reconstructs characters into a `StringBuilder`, including surrogate pair generation for four-byte code points. `toString()` catches malformed input, logs a warning, and returns the lossy decoded buffer content; `toStringChecked()` propagates malformed input.

## State and persistence behavior

State is a mutable byte array plus active length. Persisted form is two-byte unsigned length followed by UTF-8 bytes, limiting encoded data to 65535 bytes. `getBytes()` returns the backing array, not an exact copy. A static `DataInputBuffer` is used by `fromBytes()`, while per-thread output buffers are used for encoding.

## Dependencies and integration points

The class depends on `WritableComparator`, `WritableUtils`, `DataInputBuffer`, `DataOutputBuffer`, and SLF4J logging. It is deprecated in favor of `Text` but remains integrated with `SequenceFile.Reader` for versions before block-compression-era headers.

## Risks and edge cases

- The 64 KiB encoded-length limit makes it unsuitable for large strings.
- Static `IBUF` makes `fromBytes()` synchronized; bypassing synchronization would be unsafe.
- Manual UTF-8 handling is legacy and less robust than `Text`'s NIO-backed utilities.
- `toString()` can hide malformed data by logging and returning a partial/lossy string; `toStringChecked()` is safer for validation.
- The class exposes internal mutable bytes and is itself mutable, so key usage in maps requires care.

## Test signals

Tests should cover compatibility with historical serialized forms, boundary lengths near 65535 bytes, malformed sequences for checked and unchecked decoding, supplementary code points, raw comparator ordering, `skip()`, and round-trip conversion through `getBytes()`/`fromBytes()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/UTF8.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VIntWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VIntWritable.java

## Purpose

`VIntWritable.java` is a mutable `WritableComparable` wrapper for an `int` serialized with Hadoop's zero-compressed variable-length integer encoding.

## Important APIs, types, and functions

- Constructors create empty or initialized wrappers.
- `set(int)` and `get()` mutate and read the primitive.
- `readFields()` delegates to `WritableUtils.readVInt()`.
- `write()` delegates to `WritableUtils.writeVInt()`.
- `equals()`, `hashCode()`, `compareTo()`, and `toString()` provide value semantics.

## Control flow

All serialization logic is delegated to `WritableUtils`; object comparison is direct integer comparison with explicit ternary return values.

## State and persistence behavior

The only mutable state is `private int value`. Persisted size ranges from one to five bytes depending on value magnitude and sign. Hash code is the integer value itself, stable across JVMs.

## Dependencies and integration points

The class depends on `WritableComparable` and `WritableUtils`. Unlike several fixed-width writables, it does not register a custom raw comparator in this file, so generic comparator paths may deserialize objects unless another comparator is supplied.

## Risks and edge cases

- Variable-length encoding does not preserve numeric ordering lexicographically, so raw byte comparison would be wrong unless decoded.
- Mutability creates the usual key-in-collection risk.
- Javadoc says one to five bytes, which is correct for int values through `WritableUtils.writeVLong()`.

## Test signals

Tests should cover round-trips for `Integer.MIN_VALUE`, negative threshold values, `-112`, `-111`, `0`, `127`, `128`, and `Integer.MAX_VALUE`, plus equality, hash, comparison, and encoded size expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VIntWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VLongWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VLongWritable.java

## Purpose

`VLongWritable.java` is a mutable `WritableComparable` wrapper for a `long` serialized with Hadoop's zero-compressed variable-length integer encoding.

## Important APIs, types, and functions

- Constructors create empty or initialized wrappers.
- `set(long)` and `get()` mutate and read the primitive.
- `readFields()` delegates to `WritableUtils.readVLong()`.
- `write()` delegates to `WritableUtils.writeVLong()`.
- `equals()`, `hashCode()`, `compareTo()`, and `toString()` provide value semantics.

## Control flow

Serialization and deserialization are delegated to `WritableUtils`; comparison reads the two long fields and returns `-1`, `0`, or `1`.

## State and persistence behavior

State is a single mutable `long`. Persisted size ranges from one to nine bytes. `hashCode()` truncates to the low 32 bits, which is stable but collision-prone for values that differ only in high bits.

## Dependencies and integration points

The class depends on `WritableComparable` and `WritableUtils`. It is useful where compact long storage matters, such as counters, offsets, or sequence metadata.

## Risks and edge cases

- The class javadoc says values take between one and five bytes, which is incorrect for long values; `WritableUtils.writeVLong()` can emit up to nine bytes.
- No raw comparator is registered here; bytewise comparison of encoded vlongs would not match numeric ordering.
- Hash truncation is compatible with old Hadoop behavior but weak for partitioning high-bit-heavy values.

## Test signals

Tests should cover round-trips and encoded sizes for `Long.MIN_VALUE`, `Long.MAX_VALUE`, `-113`, `-112`, `127`, `128`, large high-bit values, comparison ordering, and hash collision expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VLongWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VersionMismatchException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VersionMismatchException.java

## Purpose

`VersionMismatchException.java` is the checked exception thrown when serialized data carries a version byte that does not match the current `VersionedWritable` implementation's expected version.

## Important APIs, types, and functions

- The class extends `IOException`.
- Constructor stores expected and found version bytes.
- `toString()` returns a human-readable mismatch message.

## Control flow

There is no complex control flow. `VersionedWritable.readFields()` and `SequenceFile.Reader` create this exception when they detect incompatible versions.

## State and persistence behavior

The exception stores two private bytes: `expectedVersion` and `foundVersion`. It is not itself a serialized data format, and it does not define `serialVersionUID`.

## Dependencies and integration points

The class depends on `IOException` and is referenced by `VersionedWritable` and sequence-file version checks. It is part of Hadoop IO's compatibility signaling.

## Risks and edge cases

- The constructor does not call `super(message)`, so `getMessage()` may be null even though `toString()` is informative.
- Stored bytes can display as signed values for versions above 127.
- There are no accessors for expected/found versions.

## Test signals

Tests should assert `toString()` content, behavior when caught as `IOException`, and callers' handling of mismatched version bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VersionMismatchException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VersionedWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VersionedWritable.java

## Purpose

`VersionedWritable.java` is a base class for writable records with a leading version byte. Subclasses can evolve their payloads while checking compatibility during deserialization.

## Important APIs, types, and functions

- `getVersion()` is abstract and returns the current implementation version byte.
- `write(DataOutput)` writes the version byte.
- `readFields(DataInput)` reads a version byte and throws `VersionMismatchException` if it differs from `getVersion()`.

## Control flow

Subclasses normally call `super.write(out)` before writing their own fields and `super.readFields(in)` before reading the rest of their payload. If versions differ, `readFields()` throws before subclass fields are read.

## State and persistence behavior

The base class has no fields. Persisted state is one leading byte supplied by `getVersion()`. Subclasses define all subsequent persisted fields and may catch `VersionMismatchException` if they implement migration logic.

## Dependencies and integration points

It depends on `Writable`, `DataInput`, `DataOutput`, and `VersionMismatchException`. It is a simple compatibility hook for Hadoop IO types that predate richer schema evolution systems.

## Risks and edge cases

- Only exact version equality is accepted by the base implementation; compatible older versions require subclass override or exception handling.
- A single signed byte limits version representation and can display awkwardly above 127.
- Forgetting to call `super.write()` or `super.readFields()` breaks the format contract silently.

## Test signals

Tests should define a small subclass, assert version byte round-trip, mismatch exception behavior, and subclass payload read/write ordering around the superclass calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VersionedWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WeakReferencedElasticByteBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WeakReferencedElasticByteBufferPool.java

## Purpose

`WeakReferencedElasticByteBufferPool.java` is a thread-safe `ElasticByteBufferPool` variant that stores pooled heap and direct `ByteBuffer` instances through `WeakReference`s. It lets the JVM reclaim buffers that are no longer strongly referenced while still reusing live buffers by nearest sufficient capacity.

## Important APIs, types, and functions

- The class extends `ElasticByteBufferPool`.
- `directBuffers` and `heapBuffers` are `TreeMap<Key, WeakReference<ByteBuffer>>` pools keyed by capacity and insertion time.
- `getBuffer(boolean direct, int length)` removes cleared weak references, finds the smallest buffer with capacity at least `length`, removes it from the pool, and returns it or allocates a new buffer.
- `putBuffer(ByteBuffer buffer)` clears the buffer and inserts it with a unique `(capacity, System.nanoTime())` key.
- `release()` clears both pools.
- `getCurrentBuffersCount(boolean isDirect)` is visible for tests.

## Control flow

All public methods are synchronized. `getBuffer()` chooses the direct or heap tree, prunes entries whose weak reference has been cleared, looks up `ceilingEntry(new Key(length, 0))`, removes that entry if present, and returns the referent when still live. If no entry or no referent remains, it allocates a new direct or heap buffer. `putBuffer()` clears the returned buffer and loops until it finds a unique nanosecond key before inserting a weak reference.

## State and persistence behavior

State is in-memory only and may shrink asynchronously when the garbage collector clears weak references. Direct and heap buffers are tracked separately. Returned buffers are cleared before pooling, so position and limit reset to capacity. The pool does not persist data and does not guarantee that a returned buffer remains available for later reuse.

## Dependencies and integration points

The class depends on `ElasticByteBufferPool` and its `Key` ordering, Java `ByteBuffer`, `WeakReference`, `TreeMap`, and Hadoop annotations. It integrates where Hadoop code wants elastic buffer reuse without retaining direct-buffer memory strongly.

## Risks and edge cases

- Each `getBuffer()` prunes the whole tree with `removeIf`, which can be O(n) under large pools.
- Weak references make reuse nondeterministic and GC-sensitive; performance tests should not assume stable hit rates.
- `putBuffer(null)` would fail; callers must only return real buffers.
- If system clock/nanotime granularity is poor, `putBuffer()` can loop, though the code expects this to be rare.
- `release()` only removes pool references; callers holding buffers keep them alive.

## Test signals

Tests should verify direct/heap separation, nearest-greater capacity selection, buffer clearing on return, pool count visibility, `release()`, GC-cleared weak reference pruning, and multi-threaded get/put safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WeakReferencedElasticByteBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Writable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Writable.java

## Purpose

`Writable.java` defines Hadoop's core binary serialization contract. Implementations write their fields to `DataOutput` and restore them from `DataInput`, usually reusing object storage for efficiency.

## Important APIs, types, and functions

- `write(DataOutput out)` serializes all fields.
- `readFields(DataInput in)` deserializes all fields into the current object.
- Javadoc documents the default-constructor pattern and optional static `read(DataInput)` factory convention.

## Control flow

The interface itself has no implementation. Serialization control flow is defined by each writable type, and callers must invoke methods in matching write/read order.

## State and persistence behavior

State is implementation-specific. The contract is positional binary persistence with no built-in schema, version, or class metadata. Object reuse during `readFields()` is encouraged.

## Dependencies and integration points

It depends only on Java `DataInput`, `DataOutput`, and `IOException`. It is the base contract for Hadoop MapReduce keys/values, sequence files, map files, object serialization helpers, and many IO utilities.

## Risks and edge cases

- Implementations must maintain exact read/write field ordering; there is no automatic validation.
- The interface has no default versioning or null handling.
- Reusing objects in `readFields()` can leave stale state if implementations forget to clear removed fields.
- Types used reflectively need accessible no-argument constructors even though the interface cannot enforce that.

## Test signals

Every writable implementation should have round-trip tests, compatibility fixtures for serialized bytes, corrupted/truncated input tests, and reuse tests that read multiple records into the same instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Writable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableComparable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableComparable.java

## Purpose

`WritableComparable.java` combines Hadoop's `Writable` binary serialization contract with Java's `Comparable` ordering contract. It is the standard interface for Hadoop keys.

## Important APIs, types, and functions

- `WritableComparable<T>` extends `Writable` and `Comparable<T>`.
- It declares no additional methods.
- Javadoc emphasizes stable `hashCode()` across JVM instances because Hadoop partitioning often uses key hashes.

## Control flow

There is no local control flow. Implementations must supply serialization plus `compareTo()`.

## State and persistence behavior

State is implementation-specific. Persisted bytes must be consistent with comparison semantics where raw comparators or sorting are involved.

## Dependencies and integration points

The interface integrates with `WritableComparator`, `RawComparator`, MapReduce sort/shuffle, partitioning, `SequenceFile.Sorter`, and collection-like writable containers.

## Risks and edge cases

- Bad `compareTo()`/`equals()`/`hashCode()` consistency can corrupt sort, grouping, partitioning, or Java collection behavior.
- The interface cannot enforce deterministic hash codes; implementers must avoid identity-based defaults.
- Mutable keys can break sorted collections or partitioning if mutated after use.

## Test signals

Implementation tests should verify serialization round-trip, comparison transitivity, equality/hash consistency, deterministic hash across instances, and raw comparator equivalence when a raw comparator exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableComparable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableComparator.java

## Purpose

`WritableComparator.java` is Hadoop's comparator registry and default comparison implementation for `WritableComparable` keys. It supports optimized raw-byte comparisons for sort-heavy paths while falling back to object deserialization and `compareTo()`.

## Important APIs, types, and functions

- Static `comparators` maps key classes to registered `WritableComparator` instances.
- `get(Class, Configuration)` returns a registered comparator, forces class initialization to trigger static registrations, or creates a generic comparator with reusable key instances.
- `define(Class, WritableComparator)` registers optimized comparators; registered comparators must be thread-safe.
- Constructors optionally create reusable `key1`, `key2`, and `DataInputBuffer` for generic raw comparisons.
- `compare(byte[], int, int, byte[], int, int)` deserializes both keys and delegates to `compare(WritableComparable, WritableComparable)`.
- `compare(WritableComparable, WritableComparable)` delegates to natural ordering.
- Static byte helpers parse unsigned short, int, float, long, double, vint/vlong, compute hashes, and compare bytes lexicographically with unsigned byte ordering.

## Control flow

Comparator lookup first checks the registry. If no comparator is present, it loads and initializes the key class because many writable classes register comparators in static initializers. If still absent, it constructs a generic comparator that reuses two key instances and a shared `DataInputBuffer`. Raw comparison resets the buffer over the first byte slice, reads into `key1`, resets over the second, reads into `key2`, clears the buffer reference, then compares the two objects.

## State and persistence behavior

Global state is the concurrent comparator registry. Individual generic comparators hold mutable reusable keys and buffer, which makes them efficient but not thread-safe for concurrent raw comparisons unless externally synchronized or overridden. Registered optimized comparators are expected to be thread-safe. The comparator itself persists nothing.

## Dependencies and integration points

This class depends on `RawComparator`, `Configurable`, `Configuration`, `ReflectionUtils`, `DataInputBuffer`, and Java `ConcurrentHashMap`. It is used by `SequenceFile.Sorter`, `MapFile`, MapReduce sort and grouping, and primitive writable static comparator registrations.

## Risks and edge cases

- The generic comparator mutates shared `key1`, `key2`, and `buffer`, so a generic comparator instance is unsafe for concurrent `compare(byte[],...)` calls.
- Registered optimized comparators are global and later registrations replace earlier ones.
- `get()` applies the newly supplied configuration to the shared comparator instance, which can affect other users of that comparator.
- `readVInt(byte[], start)` casts `readVLong()` to int without range validation, unlike `WritableUtils.readVInt(DataInput)`.
- Byte helper methods assume enough bytes are available except where `readVLong()` checks length.

## Test signals

Tests should cover comparator registration and class initialization, generic comparator equivalence to object comparison, optimized primitive comparators, unsigned byte ordering, byte parser big-endian behavior, concurrent lookup, configuration propagation, and malformed variable-length integer byte arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableFactories.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableFactories.java

## Purpose

`WritableFactories.java` is a global registry that lets Hadoop construct `Writable` instances through explicit factories rather than public constructors. It is mainly for non-public writable classes or classes needing custom instantiation.

## Important APIs, types, and functions

- `CLASS_TO_FACTORY` is a `ConcurrentHashMap<Class, WritableFactory>`.
- `setFactory(Class, WritableFactory)` registers a factory.
- `getFactory(Class)` returns a registered factory or null.
- `newInstance(Class<? extends Writable>, Configuration)` uses a factory when present, sets configuration on `Configurable` results, or falls back to `ReflectionUtils.newInstance()`.
- `newInstance(Class<? extends Writable>)` delegates with null configuration.

## Control flow

Instantiation first looks up the class in the registry. If a factory exists, it creates the object and applies configuration if the result implements `Configurable`. Without a factory, `ReflectionUtils.newInstance()` performs reflective construction and configuration.

## State and persistence behavior

The only state is the static concurrent factory registry. It persists for the JVM lifetime and is not serialized. Registrations can be replaced by later calls.

## Dependencies and integration points

The class depends on `WritableFactory`, `Writable`, `Configurable`, `Configuration`, `ReflectionUtils`, and `ConcurrentHashMap`. It integrates with object deserialization paths such as `ObjectWritable` and any code that needs configurable writable instantiation.

## Risks and edge cases

- Global mutable registration can affect unrelated code in the same JVM.
- Raw `Class` keys and values provide limited compile-time type safety.
- A factory returning the wrong writable type is not checked locally.
- `setFactory(c, null)` effectively stores a null value attempt, which `ConcurrentHashMap` rejects with `NullPointerException`; removal is not supported.

## Test signals

Tests should verify factory use, fallback reflection, `Configurable.setConf()` application for factory-created objects, replacement registrations, non-public constructors, and wrong/null factory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableFactories.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableFactory.java

## Purpose

`WritableFactory.java` defines the factory interface used by `WritableFactories` to construct writable instances.

## Important APIs, types, and functions

- `newInstance()` returns a new `Writable`.
- Javadoc links the interface to `WritableFactories`.

## Control flow

The interface has no implementation control flow. Callers invoke it when a factory has been registered for a writable class.

## State and persistence behavior

State depends on implementations. Factories may be stateless singletons or capture construction context, but the interface does not prescribe persistence.

## Dependencies and integration points

It depends only on `Writable` and Hadoop annotations. It integrates with `WritableFactories` and deserialization code needing factory-based construction.

## Risks and edge cases

- The interface does not accept a `Configuration`; configuration is applied after construction only if the result implements `Configurable`.
- It does not declare checked exceptions, so construction failures must be unchecked.
- Implementations must return a fresh instance unless documented otherwise.

## Test signals

Tests should focus on implementations: fresh-instance behavior, compatibility with `WritableFactories.newInstance()`, configuration injection after construction, and failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableName.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableName.java

## Purpose

`WritableName.java` maps writable classes to stable short names and alternate names so serialized files can survive Java class renames or use compact legacy aliases.

## Important APIs, types, and functions

- Static maps `NAME_TO_CLASS` and `CLASS_TO_NAME` hold aliases.
- Static initialization registers `NullWritable` as `null`, `LongWritable` as `long`, `UTF8` as `UTF8`, and `MD5Hash` as `MD5Hash`.
- `setName(Class<?>, String)` sets the canonical short name and reverse mapping.
- `addName(Class<?>, String)` adds an alternate lookup-only name.
- `getName(Class<?>)` returns a registered name or the Java class name.
- `getClass(String, Configuration)` resolves an alias or falls back to `conf.getClassByName()`, wrapping `ClassNotFoundException` in `IOException`.

## Control flow

Class-to-name lookup is a synchronized map read with fallback to `Class.getName()`. Name-to-class lookup is a synchronized alias read with fallback class loading via the supplied `Configuration`. `setName()` updates both maps, while `addName()` only updates name-to-class.

## State and persistence behavior

The alias maps are static mutable JVM-global state. Persisted data elsewhere, especially old sequence files and object-writable formats, may contain either aliases or full class names. Alias registration changes future serialization and lookup behavior but does not rewrite existing data.

## Dependencies and integration points

The class depends on `Configuration` for class loading and several writable types for default aliases. `SequenceFile.Reader` uses it to resolve key/value class names read from headers.

## Risks and edge cases

- Global synchronized maps can be changed by any code in the JVM, affecting all readers/writers.
- `setName()` can overwrite aliases without conflict checks.
- `getClass()` assumes `conf` is non-null; callers passing null risk `NullPointerException`.
- Alias collisions can make historical data resolve to the wrong class.

## Test signals

Tests should cover default aliases, custom aliases, alternate names, fallback class loading, missing class error wrapping, alias overwrite behavior, and sequence-file compatibility with renamed classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableName.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableUtils.java

## Purpose

`WritableUtils.java` is a static utility class for Hadoop writable serialization. It provides compressed byte/string helpers, UTF-8 string arrays, cloning, zero-compressed variable-length integer encoding, enum serialization, byte skipping, writable-to-byte-array conversion, and bounded safe string reads.

## Important APIs, types, and functions

- `readCompressedByteArray()`, `writeCompressedByteArray()`, and `skipCompressedByteArray()` handle GZIP-compressed byte arrays with an int byte-length prefix and `-1` null sentinel.
- `readCompressedString()` and `writeCompressedString()` adapt compressed byte arrays to UTF-8 strings.
- `writeString()`, `readString()`, string-array, and compressed-string-array helpers use int lengths and UTF-8 bytes.
- `clone()` and deprecated `cloneInto()` copy writables through `ReflectionUtils`.
- `writeVInt()`, `writeVLong()`, `readVInt()`, `readVLong()`, `readVIntInRange()`, `isNegativeVInt()`, `decodeVIntSize()`, and `getVIntSize()` implement Hadoop's zero-compressed integer format.
- `readEnum()` and `writeEnum()` serialize enum names through `Text`.
- `skipFully()` loops until a requested number of bytes is skipped or throws.
- `toByteArray(Writable...)` serializes one or more writables into a byte array backed by `DataOutputBuffer`.
- `readStringSafely()` reads a vint length, enforces bounds, and decodes through `Text`.

## Control flow

Compressed writes GZIP the supplied bytes into a temporary `ByteArrayOutputStream`, write compressed length, then compressed payload. Reads allocate the compressed byte array, inflate into a `ByteArrayOutputStream`, and return decompressed bytes. Variable-length integer writes emit one byte for values in `[-112, 127]`; otherwise they write a sign/length marker and the non-leading-zero bytes of the one's-complemented negative or positive value. Reads decode marker size, accumulate bytes big-endian, and invert for negative encodings.

`readVIntInRange()` validates bounds after reading a vlong and reports specific lower/upper errors. `skipFully()` repeatedly calls `skipBytes()` until progress stops or the target is reached. `readStringSafely()` validates length before allocating the byte array, unlike several older unbounded string helpers.

## State and persistence behavior

The class has no mutable static state. It defines several binary formats used across Hadoop. Vint/vlong encodings are persistent compatibility contracts for `Text`, `SequenceFile` blocks, `VIntWritable`, and `VLongWritable`. Compressed byte helpers use GZIP and int length prefixes distinct from `Text`'s vint-prefixed strings.

## Dependencies and integration points

Dependencies include `Writable`, `DataInput`, `DataOutput`, `Text`, `ReflectionUtils`, `Configuration`, `DataOutputBuffer`, `GZIPInputStream`, `GZIPOutputStream`, and UTF-8 charset support. The utilities are heavily used by Hadoop IO containers, sequence-file block compression, map files, and primitive writable wrappers.

## Risks and edge cases

- Several older string/array readers allocate directly from unvalidated int lengths; corrupted inputs can cause negative-size or large-allocation failures.
- `readCompressedByteArray()` sizes its temporary output buffer using compressed length, which is not a decompressed bound.
- `writeCompressedByteArray()` returns a compression percentage but callers should not rely on it for correctness.
- `toByteArray()` returns `DataOutputBuffer.getData()`, whose backing array may be larger than the serialized length; callers expecting exact length can be surprised.
- `readString()` uses `new String(buffer, "UTF-8")` rather than `StandardCharsets.UTF_8`, though behavior is stable.
- Vint/vlong encodings are not lexicographically ordered by numeric value.

## Test signals

Tests should cover null and empty compressed arrays/strings, large and malformed compressed payloads, string arrays with nulls, vint/vlong boundary values and encoded sizes, out-of-range vint errors, `skipFully()` on short inputs, enum round-trips, clone behavior for configurable writables, `toByteArray()` length semantics, and safe string reads rejecting negative or excessive lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/AlreadyClosedException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/AlreadyClosedException.java

## Purpose

`AlreadyClosedException.java` defines an `IOException` subtype thrown when code attempts to use a closed Hadoop compressor or decompressor.

## Important APIs, types, and functions

- `AlreadyClosedException` extends `IOException`.
- The constructor accepts a message and passes it to `IOException`.

## Control flow

There is no local control flow beyond exception construction. Compressor/decompressor implementations throw it from their own state checks after close/end operations.

## State and persistence behavior

The exception stores only standard `Throwable` message/cause state inherited from `IOException`. It has no serialization contract beyond Java exception serialization and no `serialVersionUID`.

## Dependencies and integration points

It depends on `IOException` and is documented against Hadoop `Compressor` and `Decompressor` interfaces. It gives callers a specific checked exception type for closed-resource misuse.

## Risks and edge cases

- The class name is precise, but the javadoc contains a typo: "decopressor".
- There is no cause-taking constructor, so wrappers must use `initCause()` if they need causal chaining.
- Callers catching only generic `IOException` may not distinguish closed-state bugs from IO failures.

## Test signals

Tests should verify compressor/decompressor methods throw this exception after close/end, message contents are preserved, and repeated close/end calls follow the intended idempotence or failure contract of each implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/AlreadyClosedException.java -->
