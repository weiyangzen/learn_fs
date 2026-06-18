# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForStoragePolicy.java

## Purpose
`TestOfflineImageViewerForStoragePolicy` validates delimited OIV output for storage policy IDs on files and directories.

## Important APIs, Types, And Functions
It uses `MiniDFSCluster`, `DistributedFileSystem`, `FSImageTestUtil`, `OfflineImageViewerPB`, `HdfsConstants` storage policy names, and `DFSTestUtil.readResoucePlainFile`.

## Control Flow
Setup enables storage policy support, creates directory trees with unspecified, ALLSSD, and HOT policies, creates files with and without ALLSSD, saves namespace, and records the fsimage. The test runs OIV Delimited with `-sp`, reads field 12 as a storage-policy integer for each non-header row, and compares generated path,id lines against `testStoragePolicy.csv`.

## State, Persistence, And Dependencies
State includes the generated fsimage, temp directory, and delimited output file. Expected output is a checked-in resource.

## Integration Points
This validates fsimage storage policy metadata and the `PBImageDelimitedTextWriter` storage-policy column.

## Risks
It depends on numeric storage policy IDs, which are more brittle than names if policy definitions change. The `ByteArrayOutputStream output` variable is unused. Traversal ordering must match the resource file.

## Test Signals
The signal is exact equality between extracted path/storage-policy-id CSV and the expected resource.
