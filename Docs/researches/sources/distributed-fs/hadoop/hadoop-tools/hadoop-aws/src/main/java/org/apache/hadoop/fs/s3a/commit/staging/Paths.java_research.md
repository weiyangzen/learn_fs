# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/Paths.java

## Purpose
Path utility class for staging committers. It handles unique filename generation, local task temp directories, cluster staging upload directories, relative paths, and partition detection.

## Important APIs, Types, And Functions
`addUUID()` inserts job UUIDs before filename extensions unless already present. `getRelativePath()`, `getParent()`, and `path()` build path strings. `getLocalTaskAttemptTempDir()` allocates and caches local work dirs. `tempDirForStaging()`, `getMultipartUploadCommitsDirectory()`, and `getStagingUploadsParentDirectory()` build cluster manifest directories. `getPartitions()` derives touched partition names from task output.

## Control Flow
Staging committers create local attempt paths under allocated buffer dirs, write pending manifests under `$temp/$user/$uuid/staging-uploads`, and compute final S3 keys from relative local paths. Partitioned committers use `getPartitions()` before upload conflict checks.

## State And Persistence
Maintains a static Guava cache of temp folders keyed by UUID plus task attempt ID. Persistent paths are staging-upload directories in the cluster filesystem and local work directories.

## Dependencies And Integration Points
Depends on Hadoop `LocalDirAllocator`, local filesystem, `UserGroupInformation`, MapReduce attempt IDs, and staging constants.

## Risks
`clearTempFolderInfo()` invalidates by attempt ID while cache keys include UUID plus attempt ID, so tests should verify cleanup expectations. Relative path derivation assumes outputs are under the attempt path. UUID insertion can interact with filenames containing the UUID in parent directories.

## Test Signals
UUID insertion before extensions, local temp allocation/cache reset, cluster staging path construction, partition extraction including root outputs, directory-output rejection, and relative path behavior.
