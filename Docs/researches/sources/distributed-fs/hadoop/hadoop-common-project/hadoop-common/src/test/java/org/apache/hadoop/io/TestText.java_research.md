<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestText.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestText.java

## Purpose
Comprehensive unit tests for Hadoop `Text` UTF-8 string storage, encoding/decoding, writable IO, comparison, search, validation, clearing, copy/append behavior, concurrency, Avro reflection, character access, known-length reads, byte-to-codepoint conversion, UTF-8 length calculation, and raw byte setting.

## Important APIs, Types, and Functions
Uses `Text` constructors, `set`, `append`, `clear`, `encode`, `decode`, `writeString`, `readString`, `readFields`, `write`, `readWithKnownLength`, `validateUTF8`, `find`, `charAt`, `bytesToCodePoint`, `utf8Length`, `getBytes`, `getLength`, `getTextLength`, `copyBytes`, and `Text.Comparator`. Helpers generate random valid Java strings and long strings beyond `Short.MAX_VALUE`. `ConcurrentEncodeDecodeThread` repeatedly uses `WritableUtils.writeString/readString`.

## Control Flow and State
Random generation uses a fixed seed and avoids unpaired surrogates. Tests round-trip both normal and very long strings through writable serialization, static encode/decode, and Java UTF-8. Limited IO tests assert max-length enforcement. Compare tests ensure raw serialized comparator matches object comparison. Find/validate/clear/copy tests check byte offsets, buffer capacity retention, alias safety, and text length updates. Avro reflection sets the trusted packages system property. Byte/codepoint tests cover valid advancement and truncated invalid UTF. `testSetBytes()` checks raw byte array length/text length handling.

## Dependencies and Integration Points
Integrates Hadoop writable utilities, `WritableComparator`, Avro reflection helper, Guava `Bytes.concat`, Java NIO charset/bytebuffer APIs, and thread helper. `Text` is a foundational writable string type used across Hadoop storage/RPC.

## Risks and Test Signals
Risks include Unicode surrogate handling, long string length encoding, raw comparator correctness, static/global Avro property mutation, a likely typo in concurrency join calling `thread2.join()` twice, and broad exception handling in some edge tests. Signals are random round-trip equality, raw comparator parity, exact find offsets for euro sign, buffer length/capacity assertions, expected `BufferUnderflowException`, and UTF-8 length boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestText.java -->
