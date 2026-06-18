# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFileOperationCost.java

Purpose: Defines metrics-level cost contracts for common S3A file operations. It verifies exact or expected S3 operation counts for status, list, glob, copy-from-local, and directory probes.

Important APIs/types/functions: extends `AbstractS3ACostTest`; uses `verifyMetrics()`, `verify()`, `verifyInnerGetFileStatus()`, `interceptGetFileStatusFNFE()`, `isDir()`, `isFile()`, `StatusProbeEnum`, `PerformanceFlagEnum.Create`, and operation-cost constants such as `GET_FILE_STATUS_ON_FILE`, `LIST_STATUS_LIST_OP`, `FILE_STATUS_DIR_PROBE`, and `NO_IO`.

Control flow: setup enables create performance flag. Each test creates a known file/directory state, invokes one API (`listLocatedStatus`, `listFiles`, `listStatus`, `getFileStatus`, `globStatus`, `copyFromLocalFile`, or internal `s3GetFileStatus`), then checks IOStatistics deltas against expected operation-cost expressions. Directory probe tests explicitly exercise HEAD-only, LIST-only, no-probe, and trailing-slash key paths.

State and persistence: writes small S3 objects/directories and one local temp file for copy-from-local. Metrics are sampled around each operation by the cost-test base.

Dependencies and integration points: S3A status probing implementation, list iterators, globber, local-to-S3 upload path, IOStatistics, and performance flag handling.

Risks: these are intentionally brittle against implementation changes in probe strategy or counter naming; exact request counts can change with new optimizations; trailing-slash internal calls depend on key mapping details.

Test signals: high-value guardrail for S3 request-cost regressions and accidental extra HEAD/LIST/PUT operations.
