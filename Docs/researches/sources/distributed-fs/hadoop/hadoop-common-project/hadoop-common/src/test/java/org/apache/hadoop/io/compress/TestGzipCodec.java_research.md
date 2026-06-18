<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestGzipCodec.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestGzipCodec.java

Purpose: Focused tests for resettable `GzipCodec` output streams, gzip member concatenation via reset, write overload coverage, and idempotent finish/reset behavior.

Important APIs/types/functions: fixture creates `GzipCodec` with `new Configuration(false)`. Constants `DATA1` and `DATA2` are small UTF-8 strings. Tests use `CompressionOutputStream`, `CompressionInputStream`, `GZIPInputStream`, `DataOutputBuffer`, and `DataInputBuffer`.

Control flow: `testSingleCompress` writes one string, finishes/closes, and verifies Java `GZIPInputStream` reads it. `testResetCompress` writes `DATA1`, finishes, calls `resetState`, writes `DATA2`, finishes/closes, then reads through Hadoop `CompressionInputStream` and expects concatenated content. `testWriteOverride` writes a full byte array, a random slice, and a single byte, then replays the random seed while reading to verify all output. `testIdempotentResetState` calls `finish` and `resetState` repeatedly without extra data and asserts only the original payload appears.

State and persistence behavior: in-memory buffers only. Random seed is logged and immediately reused for verification in `testWriteOverride`.

Dependencies and integration points: integrates `GzipCodec`, Hadoop compression streams, Java gzip stream compatibility, UTF-8 encoding, and Hadoop data buffers.

Risks and edge cases: `testWriteOverride` relies on a random slice length that may be zero; the assertion still follows generated length. The tests do not cover native zlib path selection directly; broader `TestCodec` handles that.

Test signals: verifies Hadoop gzip output is Java-readable, reset creates readable multi-member gzip data, write overloads are implemented, and repeated finish/reset calls do not emit empty extra members.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestGzipCodec.java -->
