# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForXAttr.java

## Purpose
`TestOfflineImageViewerForXAttr` verifies WebImageViewer support for listing and retrieving xattrs from fsimage metadata.

## Important APIs, Types, And Functions
It uses `MiniDFSCluster`, `DistributedFileSystem`, `FSImageTestUtil`, `WebImageViewer`, `WebHdfsFileSystem`, `XAttrHelper`, `JsonUtil`, HTTP connections, and Apache Commons IO stream reading.

## Control Flow
Setup creates `/dir1` with two user xattrs, saves namespace, precomputes expected JSON for `user.attr1`, and records the fsimage. Tests start WebImageViewer and call HTTP endpoints for `LISTXATTRS`, `GETXATTRS` with no parameters, invalid xattr parameter, valid parameter, uppercase name with `encoding=TEXT`, and missing xattr. One test uses `WebHdfsFileSystem` APIs to list names, get one xattr, get uppercase-name xattr, and get a map for both names.

## State, Persistence, And Dependencies
State is the generated fsimage and expected JSON string. All endpoint tests are read-only.

## Integration Points
This checks fsimage xattr persistence through WebImageViewer's WebHDFS-compatible HTTP surface and WebHDFS client wrappers.

## Risks
The test expects case-insensitive handling for xattr namespace/name in at least some paths. JSON equality is exact for selected xattr output. HTTP response-code semantics distinguish bad request for malformed names and forbidden for absent attributes, so behavior changes may need careful compatibility review.

## Test Signals
Signals include HTTP OK/BAD_REQUEST/FORBIDDEN codes, response bodies containing both xattr names, exact JSON for a selected xattr, WebHDFS API name/value equality, and map values for both attributes.
