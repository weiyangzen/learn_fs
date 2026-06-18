# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForContentSummary.java

## Purpose
`TestOfflineImageViewerForContentSummary` verifies WebImageViewer `GETCONTENTSUMMARY` behavior for directories, empty directories, files, symlinks, directories containing symlinks, quotas, and missing paths.

## Important APIs, Types, And Functions
It uses `MiniDFSCluster`, `DistributedFileSystem`, `FSImageTestUtil`, `WebImageViewer`, `WebHdfsFileSystem`, `ContentSummary`, `SafeModeAction`, and HTTP connections.

## Control Flow
`createOriginalFSImage()` creates a parent directory with child directories and files, sets namespace/storage quotas, records `ContentSummary` values directly from DFS for representative paths, creates symlinks to a file and directory, saves namespace, and records the fsimage. Each test starts a WebImageViewer, checks HTTP OK for a path where applicable, obtains content summary via WebHDFS, and compares selected counters with the saved DFS summary. One test verifies missing path returns HTTP 404.

## State, Persistence, And Dependencies
Static state consists of the generated fsimage and expected `ContentSummary` instances. The cluster is shut down after image generation; tests are read-only against the image.

## Integration Points
This maps NameNode content summary semantics into WebImageViewer's read-only WebHDFS API and validates quota and symlink accounting.

## Risks
The expected symlink behavior is whatever DFS returned at image-generation time, so semantic changes in symlink content summaries can require updating both production and test assumptions. Each test starts its own HTTP server, so port setup and teardown must be reliable.

## Test Signals
Signals include HTTP OK/NOT_FOUND codes and equality of directory count, file count, length, space consumed, namespace quota, and space quota.
