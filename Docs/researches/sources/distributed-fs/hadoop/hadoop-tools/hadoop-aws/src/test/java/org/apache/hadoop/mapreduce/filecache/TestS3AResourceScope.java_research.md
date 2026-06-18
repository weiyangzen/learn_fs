<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/filecache/TestS3AResourceScope.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/filecache/TestS3AResourceScope.java


## Purpose
Unit test proving S3A resources are treated as private/non-executable by distributed cache permission checks.


## Important APIs, Types, and Functions
TestS3AResourceScope defines PATH, tests two S3AFileStatus constructors, and assertNotExecutable().


## Control Flow
Each test constructs an encrypted S3AFileStatus, asserts isEncrypted(), places it in an ancestor cache map, and asserts ClientDistributedCacheManager.ancestorsHaveExecutePermissions() returns false.


## State and Persistence Behavior
No external state. The cache map is local to assertion helper.


## Dependencies and Integration Points
Depends on S3AFileStatus, ClientDistributedCacheManager package-private permission method, FileStatus, URI maps, and HadoopTestBase assertions.


## Risks and Test Signals
Risks are constructor semantic changes around encryption/private resources. Signals ensure YARN distributed cache does not treat S3A paths as public executable resources.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/filecache/TestS3AResourceScope.java -->
