<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2Utils.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2Utils.java

Purpose: Test utility for locating BZip2 block marker offsets after the first block in a compressed file or stream.

Important APIs/types/functions: final utility class with private constructor. Public overloads `getNextBlockMarkerOffsets(Path, Configuration)` and `getNextBlockMarkerOffsets(InputStream)` return `List<Long>` offsets.

Control flow: path overload resolves the filesystem, opens the file, and delegates to stream overload. Stream overload wraps raw input in `CBZip2InputStream` with `READ_MODE.BYBLOCK`, repeatedly calls `skipToNextBlockMarker`, records `getProcessedByteCount`, and returns offsets.

State and persistence behavior: no persistent state. It closes the input wrapper and path-opened stream through try-with-resources.

Dependencies and integration points: integrates with `CBZip2InputStream`, `SplittableCompressionCodec.READ_MODE.BYBLOCK`, Hadoop `Path`/`FileSystem`, and test writer-generated data.

Risks and edge cases: intended for tests and exposes offsets according to CBZip2 processed-byte accounting. It omits the first block by design and returns only following block markers.

Test signals: used by BZip2 tests to assert expected number and positions of block boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2Utils.java -->
