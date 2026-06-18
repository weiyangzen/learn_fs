# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewerForAcl.java

## Purpose
`TestOfflineImageViewerForAcl` validates OIV handling of fsimages containing HDFS ACL metadata through WebImageViewer, XML writer, and delimited writer.

## Important APIs, Types, And Functions
It uses `MiniDFSCluster`, `DistributedFileSystem`, `FSImageTestUtil`, `WebImageViewer`, `WebHdfsFileSystem`, `AclStatus`, `AclTestHelpers.aclEntry`, `PBImageXmlWriter`, `PBImageDelimitedTextWriter`, and secure SAX parser helpers.

## Control Flow
`createOriginalFSImage()` enables ACLs, creates directories/files with no ACLs, default ACLs, access ACLs, and multiple named ACL entries, stores expected `AclStatus` objects, saves namespace, and records the fsimage. Tests start WebImageViewer and compare `GETACLSTATUS` through WebHDFS for each path, verify invalid-path HTTP 404, parse XML output for well-formedness, and inspect delimited permissions for the ACL `+` suffix.

## State, Persistence, And Dependencies
Static state includes the generated fsimage and a map of expected ACL statuses. The fsimage is deleted in `AfterAll`.

## Integration Points
This tests ACL persistence from NameNode metadata into fsimage, OIV XML export, OIV delimited permission formatting, and WebImageViewer's WebHDFS ACL endpoint.

## Risks
The delimited writer test infers ACL presence from whether the path name contains "noacl", which is compact but naming-sensitive. XML test checks parseability rather than exact ACL contents. WebHDFS status equality depends on `AclStatus.equals` semantics.

## Test Signals
Signals include exact `AclStatus` equality, HTTP 404 for invalid ACL path, successful SAX parsing, and ACL-mark suffixes in delimited permission fields.
