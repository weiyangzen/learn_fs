<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteManyFiles.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteManyFiles.java


## Purpose
Scale test for renaming and recursively deleting a directory containing many files with a deliberately small bulk-delete page size.


## Important APIs, Types, and Functions
ITestS3ADeleteManyFiles, DELETE_PAGE_SIZE, createScaleConfiguration(), and testBulkRenameAndDelete(). It disables filesystem caching, removes bucket overrides, disables experimental AWS throttling, and sets BULK_DELETE_PAGE_SIZE to 50.


## Control Flow
The test creates count files under src, measures rename(srcDir, finalDir), verifies recursive source emptiness and destination file count, then measures delete(finalDir, recursive=true) and verifies the final parent is empty.


## State and Persistence Behavior
S3 object state moves from srcParent/src to finalParent/final and then to deleted. The test audits listStatus/listFiles counts and specific first/middle/last filenames to catch partial operations.


## Dependencies and Integration Points
Depends on S3AFileSystem, S3ATestUtils.createFiles/lsR, ContractTestUtils rm/timers, filenameOfIndex(), and AssertJ assertions.


## Risks and Test Signals
Primary risks are scale configuration too high for MAX_THREADS, S3 throttling, and delete pagination regressions. Strong test signals include exact object counts, path existence checks, and rename/delete throughput logs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteManyFiles.java -->
