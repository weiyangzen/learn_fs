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
