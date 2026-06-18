# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForErasureCodingPolicy.java

## Purpose
`TestOfflineImageViewerForErasureCodingPolicy` validates delimited OIV output for inherited and explicit erasure coding policy metadata.

## Important APIs, Types, And Functions
It uses `MiniDFSCluster`, `DistributedFileSystem`, `FSImageTestUtil`, `OfflineImageViewerPB`, `DFSTestUtil.readResoucePlainFile`, and the delimited writer `-ec` option.

## Control Flow
Image setup starts a 10-DataNode cluster, enables RS-6-3 and RS-3-2 policies, creates directories with EC policies plus nested subdirectories/files, creates a replicated directory tree, saves namespace, and records the fsimage. The test runs OIV with `-p Delimited -ec`, reads the output file, extracts path and field 12 EC policy values, and compares the path-policy CSV against `testErasureCodingPolicy.csv`.

## State, Persistence, And Dependencies
State is the generated fsimage, temp NameNode directory, and delimited output file. Expected output is a checked-in resource.

## Integration Points
This checks NameNode EC policy inheritance as represented in fsimage and emitted by OIV's delimited exporter.

## Risks
Expected resource output is sensitive to traversal order and policy display strings. The local variable `delemiter` is misspelled but harmless. The test assumes the EC policies exist with exact names.

## Test Signals
The main signal is exact equality between extracted path/policy lines and the resource file.
