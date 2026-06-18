# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3AOpenCost.java

Purpose: integration tests for `openFile()` cost, stream statistics, checksum disabling, supplied file length semantics, EOF behavior, positioned reads, and vectored reads across Classic, Prefetch, and Analytics stream implementations.

Important APIs/types/functions: `ITestS3AOpenCost` extends `AbstractS3ACostTest`; setup writes a fixed text file, stores `FileStatus` and length, and detects stream type with `S3ATestUtils.streamType`. Helpers include `openFile`, `assumeNoPrefetching`, `assumeNotAnalytics`, `assertS3StreamClosed`, and `assertS3StreamOpen`. Tests use open-file options for length, read policy, footer cache, and buffer size, plus IOStatistics assertions for `ACTION_FILE_OPENED`, `ACTION_HTTP_GET_REQUEST`, and `ACTION_HTTP_HEAD_REQUEST`.

Control flow: the class verifies opening with a status from another filesystem avoids initial IO, reads trigger stream opens, checksum validation is disabled, shorter supplied lengths truncate reads, longer lengths produce EOF behavior, and read/readFully/positioned/vectored reads past EOF differ by stream implementation. Several tests skip when prefetching or Analytics invalidates the Classic assumptions.

State and persistence: creates a small real S3 object per test. Stream state is tracked through FS/stream IOStatistics and inner `S3AInputStream` open/closed flags.

Dependencies/integration: S3A open-file builder, stream type selection, S3A input stream internals, Hadoop `FileRange` vectored IO, futures for vectored ranges, and checksum configuration.

Risks: assertions are stream-implementation-specific; Analytics may issue HEAD where Classic would not; counters update only on stream close.

Test signals: exact metric/statistic diffs, EOF exceptions, `-1` reads past EOF, stream open/closed assertions, and vectored future failure checks.
