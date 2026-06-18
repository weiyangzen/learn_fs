# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMetrics.java

Purpose: Tests S3A instrumentation registry and stream-statistics merging into filesystem metrics.

Important APIs/types/functions: `S3AInstrumentation`, `MutableCounterLong`, `Statistic.FILES_CREATED`, `Statistic.STREAM_READ_BYTES`, `ContractTestUtils.touch()`, `ContractTestUtils.createFile()`, and `IOStatisticsLogging.ioStatisticsSourceToString()`.

Control flow: `testMetricsRegister()` touches one file and checks the registry's files-created counter equals one. `testStreamStatistics()` writes a 26-byte file, reads it to EOF, logs stream statistics, closes the stream, then asserts filesystem instrumentation and registry counters record 26 stream-read bytes.

State and persistence: creates small S3 files; metrics accumulate on the test filesystem instrumentation instance.

Dependencies and integration points: S3A instrumentation registry, stream close/merge logic, Hadoop metrics2 counters, and IOStatistics display helpers.

Risks: counters are sensitive to prior operations if the filesystem is reused unexpectedly; stream statistics merge occurs on close, so missing close would hide updates; reads must consume exactly 26 bytes.

Test signals: catches failures to register file-created metrics or merge per-stream read counters into filesystem metrics.
