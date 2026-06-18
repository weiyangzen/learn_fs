<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBlockDecompressorStream.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBlockDecompressorStream.java

Purpose: Tests block decompression stream EOF and IO exception behavior using fake identity compressor/decompressor implementations.

Important APIs/types/functions: `testRead1`, `testRead2`, helper `testRead(int bufLen)`, and `testReadWhenIoExceptionOccure`. Uses `BlockCompressorStream`, `BlockDecompressorStream`, `FakeCompressor`, and `FakeDecompressor`.

Control flow: `testRead` optionally prefixes a 4-byte block-size header, closes a `BlockCompressorStream` without writing payload, asserts compressed output length is `bufLen + 4`, then reads through `BlockDecompressorStream` and expects `-1`. The IO exception test creates a file and wraps a `FileInputStream` whose `read()` always throws, then asserts `BlockDecompressorStream.read()` propagates an IOException containing `"File blocks missing"` rather than returning EOF.

State and persistence behavior: mostly in-memory byte arrays. One temporary file named `testReadWhenIOException` is created in the working directory and deleted in `finally`.

Dependencies and integration points: tests Hadoop block compression stream framing and read behavior independent of real codecs. Uses Java `ByteBuffer` to encode an integer prefix.

Risks and edge cases: fixed working-directory file name may collide in parallel test execution. The test name has a typo. Fake decompressor behavior is not representative of all decompressor state machines.

Test signals: ensures empty block streams return EOF cleanly and underlying IO errors are not swallowed as `-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBlockDecompressorStream.java -->
