<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestDecompressorStream.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestDecompressorStream.java

Purpose: Tests `DecompressorStream` read and skip behavior using an identity fake decompressor over a known ASCII string.

Important APIs/types/functions: fixture fields are `ByteArrayInputStream bytesIn`, `Decompressor decompressor`, and `DecompressorStream decompressorStream`. Tests are `testReadOneByte`, `testReadBuffer`, and `testSkip`.

Control flow: setup wraps the test string in a byte stream and creates `DecompressorStream(bytesIn, new FakeDecompressor(), 20, 13)`. One-byte test reads each character and expects `EOFException` after content. Buffer test reads chunks up to 32 bytes, validates substrings, and expects EOF on further read. Skip test skips 12 bytes, reads expected characters, skips 10 more, reads another expected character, then expects EOFException when skipping past end.

State and persistence behavior: all state is in memory and recreated before each test.

Dependencies and integration points: integrates `DecompressorStream` with `FakeDecompressor`, AssertJ assertions, and JUnit. It tests stream wrapper behavior independent from actual codec algorithms.

Risks and edge cases: `new String(buf, 0, bytesRead)` uses platform default charset, but data is ASCII. Fake decompressor returns pass-through data and does not model all production decompressor edge cases.

Test signals: validates byte reads, buffer reads, skip semantics, and EOF exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestDecompressorStream.java -->
