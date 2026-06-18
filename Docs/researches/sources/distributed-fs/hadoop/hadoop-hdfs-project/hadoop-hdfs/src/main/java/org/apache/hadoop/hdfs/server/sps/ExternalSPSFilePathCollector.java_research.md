<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFilePathCollector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFilePathCollector.java

## Purpose

`ExternalSPSFilePathCollector` recursively scans a file-ID path for files needing storage policy satisfaction and submits work items to external SPS.

## Important APIs and types

The class implements `FileCollector`. It holds a `DistributedFileSystem`, `SPSService`, and queue limit from `DFS_STORAGE_POLICY_SATISFIER_QUEUE_LIMIT_KEY`. Core methods are `scanAndCollectFiles(long pathId)`, private recursive `processPath(Long startID, String childPath)`, `checkProcessingQueuesFree()`, and `remainingCapacity()`.

## Control flow

Construction obtains the default DFS, logging if unavailable. `scanAndCollectFiles` lazily recreates DFS if needed, converts the inode ID to a file-ID path, and calls `processPath`. `processPath` pages through `listPaths`, adds files as `ItemInfo(startID, childFileId)`, waits when the SPS processing queue is full, and recursively descends directories. If no files are found, it submits an empty completed list so the SPS hint can be removed; otherwise it marks scanning complete for the root path.

## State and persistence behavior

Runtime state is the DFS handle and queue-limit value. Persistent HDFS state is only read during directory listing; SPS service state is updated through processing queues and scan-complete markers.

## Dependencies and integration points

It depends on `DistributedFileSystem`, `DFSUtilClient.makePathFromFileId`, `DirectoryListing`, `HdfsFileStatus`, `ItemInfo`, and `SPSService`.

## Risks and test signals

Risks include deep recursion, sleeping forever when queues do not drain, continuing after interruption, ignoring directories that fail listing, and assuming the default FS is HDFS. Tests should cover file, empty directory, nested directory, paginated listing, queue backpressure, DFS initialization failure/recovery, and scan-completion semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFilePathCollector.java -->
