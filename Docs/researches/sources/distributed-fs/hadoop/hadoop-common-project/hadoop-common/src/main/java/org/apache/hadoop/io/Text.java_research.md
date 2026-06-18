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
