# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractVectoredRead.java

Purpose: classic S3A input-stream contract and metrics tests for vectored reads, with Analytics Accelerator disabled.

Important APIs/types/functions: extends `AbstractContractVectoredReadTest`, parameterized by buffer type. `createConfiguration()` disables AAL. Tests cover 416/EOF handling, min-seek/max-merged-read configuration propagation/defaults, close/unbuffer cancellation, vectored-vs-normal read statistics, and multiple vectored reads. Helper `getTestFileSystemWithReadAheadDisabled()` creates an uncached FS with readahead 0 and small vector thresholds.

Control flow: EOF test opens with an artificially extended length and verifies futures fail with `EOFException`. Cancellation tests start vectored reads, close/unbuffer, expect `InterruptedIOException`, then verify subsequent reads can succeed. Statistics tests compare coalesced vectored reads against individual `readFully()` calls, checking input policy, object stream closure, HTTP GET counts, byte counters, and FS-level aggregation.

State and persistence: creates vector-read test files inherited from the contract suite; uses temporary uncached filesystems for config-specific checks.

Dependencies and integration: Hadoop `FileRange`, `FSDataInputStream.readVectored`, S3A input stream/policy, open-file options, IOStatistics, and contract vector helpers.

Risks: asynchronous future timing and cancellation can race. Exact counter values depend on range coalescing and stream implementation.

Test signals: extensive integration coverage for vectored read correctness, configuration propagation, cancellation, coalescing, and statistics.
