<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestUTF8.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestUTF8.java

## Purpose
Tests deprecated `UTF8` writable behavior, modified UTF byte conversion, IO compatibility with `DataInput.readUTF`, null-character encoding, supplementary Unicode decoding, and invalid/truncated UTF-8 diagnostics.

## Important APIs, Types, and Functions
Uses `UTF8` constructor, `UTF8.getBytes`, `writeString`, `readString`, `fromBytes`, `TestWritable.testWritable`, `DataInputStream.readUTF`, `StringUtils.byteToHexString`, and `GenericTestUtils.assertExceptionContains`.

## Control Flow and State
Random strings are generated from arbitrary `char` values for 10,000 iterations. Writable and IO tests round-trip through Hadoop buffers and Java modified UTF. `testNullEncoding()` verifies embedded null is encoded as standard UTF-8 in the stored payload after the two-byte length prefix. Supplementary-plane test uses a surrogate pair and validates four UTF-8 bytes and round trip. Invalid tests assert `UTFDataFormatException` messages for illegal bytes, illegal five-byte sequence, and truncated four-byte sequence.

## Dependencies and Integration Points
Protects deprecated `UTF8` compatibility for old writable data and older APIs, while checking modern strict UTF-8 error behavior.

## Risks and Test Signals
Risks are deprecated API behavior drift, random generation including unusual surrogate values, exact hex snippets in error messages, and modified-vs-standard UTF distinction. Signals are 10k writable/IO round trips, exact hex for supplementary character, and exception text for invalid/truncated sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestUTF8.java -->
