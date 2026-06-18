<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestTextNonUTF8.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestTextNonUTF8.java

## Purpose
Tests `Text` construction from non-UTF8 bytes and preservation of raw bytes.

## Important APIs, Types, and Functions
Uses `Text(byte[])`, `Text.validateUTF8(byte[])`, `Text.getBytes`, `MalformedInputException`, and `Arrays.equals`.

## Control Flow and State
The test creates a byte array of repeated `0xff`, constructs `Text`, calls `validateUTF8` expecting a malformed-input path, asserts the local `nonUTF8` flag remains false, and asserts `Text.getBytes()` matches the original bytes.

## Dependencies and Integration Points
Validates `Text` can hold arbitrary bytes even when validation rejects them. This matters for legacy or corrupt data paths where raw bytes must be preserved until explicitly decoded.

## Risks and Test Signals
The `nonUTF8` flag name/value is confusing because it is initialized false and remains false after catching `MalformedInputException`. The meaningful signal is raw byte preservation in `Text`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestTextNonUTF8.java -->
