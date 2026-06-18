<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBZip2Codec.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBZip2Codec.java

Purpose: Focused tests for `BZip2Codec.createInputStream` with explicit start/end offsets and `SplittableCompressionCodec.READ_MODE` behavior.

Important APIs/types/functions: test fixture creates `Configuration`, `FileSystem`, `BZip2Codec`, pooled `Decompressor`, and a temporary `.bz2` path. Helpers include `newCompressionStream`, `newAlternatingByteArray`, `assertCasesWhereReadDoesNotAdvanceStream`, `assertReadingAtPositionZero`, `assertReadingPastEndOfBlock`, `assertReadingWithContinuousMode`, and `assertRead`.

Control flow: setup creates local test path and obtains a decompressor from `CodecPool`; teardown returns it and deletes the file. The main test writes three BZip2 blocks with `BZip2TextFileWriter`, finds later block marker offsets through `BZip2Utils`, then opens split streams over different starts. In `BYBLOCK` mode it asserts initial position, read argument validation, unchanged positions on invalid/zero reads, block-boundary position reporting, and EOF. In `CONTINUOUS` mode it verifies reading from 0 or header length produces all data and leaves position at the header.

State and persistence behavior: writes a temporary compressed file under `test.build.data` or `target/data/TestBZip2Codec/input/test.txt.bz2`. Decompressor is pooled and explicitly returned. No long-lived persistence remains if teardown succeeds.

Dependencies and integration points: integrates with `BZip2Codec`, `SplitCompressionInputStream`, `SplittableCompressionCodec.READ_MODE`, `CodecPool`, `FSDataInputStream`, Hadoop `Path`/`FileSystem`, `BZip2TextFileWriter`, `BZip2Utils`, Guava `Bytes.concat`, Commons IO `IOUtils`, and AssertJ exception assertions.

Risks and edge cases: relies on deterministic block sizes from the test writer. Position semantics differ between `BYBLOCK` and `CONTINUOUS`, and the test documents current behavior including continuous mode not updating position after reads. Teardown assumes `tempFile` exists.

Test signals: validates split alignment, block marker positions, EOF, invalid read arguments, zero-length read behavior, and continuous-mode compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBZip2Codec.java -->
