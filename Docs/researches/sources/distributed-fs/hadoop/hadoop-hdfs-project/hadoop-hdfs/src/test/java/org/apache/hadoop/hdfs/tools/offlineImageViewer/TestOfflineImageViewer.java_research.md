# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestOfflineImageViewer.java

## Purpose
`TestOfflineImageViewer` is the broad integration test for Offline Image Viewer PB processors. It builds one rich fsimage and validates file distribution, XML rendering, WebImageViewer WebHDFS endpoints, delimited output, parallel delimited output, corruption detection, ReverseXML reconstruction, CLI option handling, and EC policy serialization.

## Important APIs, Types, And Functions
The file uses `OfflineImageViewerPB`, `PBImageXmlWriter`, `PBImageDelimitedTextWriter`, `PBImageCorruptionDetector`, `PBImageCorruption`, `OfflineImageReconstructor`, `FileDistributionCalculator`, `WebImageViewer`, `FSImageLoader`, `MiniDFSCluster`, `FSImageTestUtil`, `MD5FileUtils`, protobuf `FsImageProto`, and XML DOM/SAX helpers. It also constructs sample inode protobufs for focused delimited-entry tests.

## Control Flow
`createOriginalFSImage()` runs once, sets UTC timezone, starts a cluster with delegation tokens, ACLs, parallel image load settings, EC policies, custom EC policy options, directories, files, XML-sensitive path names, sticky-bit directory, delegation tokens, snapshots, xattrs, ACLs, and EC files. It saves namespace and records the latest fsimage. Tests then visit that fsimage with different processors, parse output, run embedded WebImageViewer HTTP/WebHDFS operations, create corrupted fsimages by XML deletion plus ReverseXML, compare expected corruption CSV resources, and perform XML round trips.

## State, Persistence, And Dependencies
Global static state includes `originalFsimage`, `tempDir`, `writtenFiles`, `dirCount`, EC file counts, added EC policy name, and timezone. Output files, SQLite/in-memory processor DB paths, XML files, corrupted image files, and MD5s live under test directories. `deleteOriginalFSImage()` deletes temp storage and restores timezone.

## Integration Points
This file integrates NameNode fsimage save/load, protobuf image sections, XML writer/reconstructor, WebHDFS-compatible read-only WebImageViewer operations, delimited text export, parallel processor behavior, EC policy metadata, xattrs/ACLs/snapshots/delegation-token sections, and corruption detector output.

## Risks
The test is large and stateful; many assertions depend on hard-coded inode IDs, generated namespace order, expected resource CSVs, and default timezone. Static `dirCount` and `writtenFiles` can accumulate if setup is rerun in the same JVM unexpectedly. Some tests use `db != ""` identity comparison for strings, which works for current literals but is fragile style. WebImageViewer tests depend on ephemeral HTTP ports and WebHDFS client behavior.

## Test Signals
Signals include processor return codes, file/directory counts, max file size, valid XML parsing, WebHDFS status equality, HTTP error codes, delimited field counts and path set equality, matching MD5 for serial/parallel delimited output, exact corruption CSV outputs, XML round-trip diffs being empty, layout-version mismatch failure, and EC policy XML fields.
