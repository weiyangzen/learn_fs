# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestLocatedFileStatusFetcher.java

Purpose: validates `LocatedFileStatusFetcher` behavior and list-call statistics against S3A directory trees.

Important APIs/types/functions: extends `AbstractS3ATestBase`; defines path filters (`EVERYTHING`, `.txt`, hidden-file filter), expected exception text constants, and a shared `HELLO` payload. Setup creates an empty directory, empty file, nested directories, and three files. `assertListCount()` reads fetcher IOStatistics and asserts `OBJECT_LIST_REQUEST`.

Control flow: single-thread and four-thread tests configure `LIST_STATUS_NUM_THREADS`, run recursive fetcher scans, and assert returned file paths and expected four list calls. File scan test passes a file path directly and expects only that file with null fetcher IOStatistics.

State and persistence: builds a fixed tree under each method path.

Dependencies and integration: old MapReduce `LocatedFileStatusFetcher`, S3A statistics extraction, path filters, and S3A listStatus/listFiles.

Risks: exact list-call counts are implementation-sensitive. Parallel fetcher behavior depends on thread count and directory layout.

Test signals: integration coverage for successful recursive located-status scanning and statistics.
