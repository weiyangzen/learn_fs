# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/AbstractSTestS3AHugeFiles.java

Purpose: abstract ordered scale-test suite for creating, validating, reading, vectored-reading, renaming, encryption-checking, deleting, and dumping statistics for huge S3A files.

Important APIs/types/functions: extends `S3AScaleTestBase`; subclasses provide `getBlockOutputBufferName()` and may override multipart/encryption/vector-buffer hooks. Configuration sets multipart partition size, socket buffers, vector active reads, user agent, fast upload buffer, and disables FS caching. Tests are alphanumerically ordered (`test_010` through `test_900`). Key helpers include `assumeHugeFileExists`, `listFile`, `renameFile`, `deleteHugeFile`, and getters for generated paths/sizes.

Control flow: setup derives scale directory, source/destination paths, upload block size, partition size, and file size. Create test deletes leftovers, writes deterministic blocks with `CountingProgressListener`, logs progress/statistics, closes stream, and validates multipart/single PUT counters and gauges. Later tests assert status/etag, perform positioned and vectored reads, sequentially read whole file, verify encryption hooks before/after rename, rename there and back, clean up, and dump FS IOStatistics.

State and persistence: deliberately keeps huge file across ordered tests by disabling per-test directory cleanup; final cleanup removes source/dest/test path. Uses live S3 object data and FS/stream statistics.

Dependencies/integration: S3A scale configuration, multipart upload, block output stream stats, open-file builder, vectored IO, byte-buffer pools, encryption hooks, and contract utilities.

Risks: order dependence means partial runs rely on `assumeHugeFileExists`; large object operations are time/cost sensitive; timeout and file-size divisibility are enforced; subclass hooks can change visibility/encryption expectations.

Test signals: upload progress without failures, exact stream/FS counters/gauges, file length and etag consistency, read validation, timing/bandwidth logs, successful rename, and cleanup completion.
