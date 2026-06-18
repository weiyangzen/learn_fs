# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestDowngradeSyncable.java

Purpose: verifies `hflush()` and `hsync()` can be downgraded from unsupported failures to ignored operations while updating IO statistics.

Important APIs/types/functions: extends `AbstractS3ACostTest`; `createConfiguration()` removes bucket override for `DOWNGRADE_SYNCABLE_EXCEPTIONS` and sets it true. Tests use `FSDataOutputStream.hflush()`/`hsync()` and assert `OP_HFLUSH`/`OP_HSYNC` counters on stream and FS statistics.

Control flow: each test records initial FS counter, writes one byte, calls the sync method, checks stream counters, closes stream, then checks FS-level merged counter.

State and persistence: creates one output file per method path and updates IOStatistics.

Dependencies and integration: S3A output stream sync downgrade option, cost-test base, and statistics assertions.

Risks: relies on stats being merged only after close. If sync downgrade defaults change, configuration setup is critical.

Test signals: integration coverage for compatibility behavior with APIs expecting Syncable output streams.
