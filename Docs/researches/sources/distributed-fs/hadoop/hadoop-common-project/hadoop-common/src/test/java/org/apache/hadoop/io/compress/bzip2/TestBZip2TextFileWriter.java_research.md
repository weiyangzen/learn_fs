<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBZip2TextFileWriter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBZip2TextFileWriter.java

Purpose: Unit coverage for `BZip2TextFileWriter` block-boundary behavior.

Important APIs/types/functions: fixture owns `ByteArrayOutputStream rawOut` and `BZip2TextFileWriter writer`; delimiter is a single NUL byte. Helper `getNextBlockMarkerOffsets` delegates to `BZip2Utils`.

Control flow: setup creates the in-memory writer. Teardown nulls `rawOut` and closes writer. Tests write records of size `BLOCK_SIZE`, `BLOCK_SIZE + 1`, `2 * BLOCK_SIZE`, and `2 * BLOCK_SIZE + 1`, close the writer, then assert the number of following block markers is 0, 1, 1, and 2 respectively.

State and persistence behavior: in-memory compressed bytes only. Writer is explicitly closed in tests and again in teardown.

Dependencies and integration points: tests `BZip2TextFileWriter` plus `BZip2Utils` and indirectly `CBZip2OutputStream`/`CBZip2InputStream`.

Risks and edge cases: double close may rely on idempotent stream close behavior. It checks marker count, not exact offsets. The delimiter prevents zero-length record content ambiguity.

Test signals: validates the writer's exported `BLOCK_SIZE` corresponds to actual BZip2 block creation thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBZip2TextFileWriter.java -->
