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
