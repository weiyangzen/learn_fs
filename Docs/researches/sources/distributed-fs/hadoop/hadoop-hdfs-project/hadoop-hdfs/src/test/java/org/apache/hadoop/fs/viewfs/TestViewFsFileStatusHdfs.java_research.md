# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsFileStatusHdfs.java

## Purpose

`TestViewFsFileStatusHdfs` verifies two HDFS-backed ViewFileSystem status behaviors: `ViewFsFileStatus` serialization/deserialization and file checksum passthrough. The serialization case protects MapReduce job submission paths that serialize `FileStatus`.

## Important APIs, types, and functions

The test uses `MiniDFSCluster`, `ViewFileSystem`, `FileSystemTestHelper`, `ConfigUtil.addLink`, `FileStatus.write/readFields`, `DataOutputBuffer`, `DataInputBuffer`, and `FileChecksum`. Paths `/tmp` and `/vfstmp` are mounted to HDFS directories.

## Control flow, state, and persistence

Cluster setup creates an HDFS working directory, configures ViewFS links, and verifies the returned filesystem class. `testFileStatusSerialziation` creates a file in raw HDFS, gets status through ViewFS, serializes it into a data buffer, reads it into a plain `FileStatus`, and compares length. `testGetFileChecksum` creates two HDFS files, compares ViewFS checksum for one with raw HDFS checksum, and asserts it differs from the other file's checksum.

## Dependencies and integration points

This covers ViewFS overlay status objects, Hadoop writable serialization, HDFS checksum calculation, and mount path translation. It is important for consumers that persist `FileStatus` across process or RPC boundaries.

## Risks and test signals

Risks include non-serializable ViewFS-specific status fields, lost file length after deserialization, checksum requests using the view path without resolving to target, or checksum collisions in the fixture. Signals are exact length equality and checksum equality/inequality comparisons.
