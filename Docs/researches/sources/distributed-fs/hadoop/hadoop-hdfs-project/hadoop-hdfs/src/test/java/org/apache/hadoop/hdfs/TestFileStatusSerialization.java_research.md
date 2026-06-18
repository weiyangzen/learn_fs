# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusSerialization.java

## Purpose
Verifies compatible serialization between `HdfsFileStatus`, `FileStatus`, HDFS protobuf status, generic FS protobuf status, Java serialization, and Writable serialization, with special attention to 2.x `FsPermission` flag compatibility.

## APIs and Control Flow
`baseStatus()` builds an `HdfsFileStatusProto` with file metadata, permissions, owner/group, times, replication, block size, and flags. `checkFields` compares core `FileStatus` properties. `testFsPermissionCompatibility` iterates legacy-compatible flag values, converts through `PBHelperClient`, qualifies paths, checks ACL/encryption/EC bits, writes via `DataOutputBuffer`, reads via `DataInputBuffer`, and verifies flag preservation. `testJavaSerialization` round-trips an `HdfsFileStatus` through `ObjectOutputStream/ObjectInputStream`. `testCrossSerializationProto` serializes each HDFS file type into `FileStatusProto`, checks aligned fields, and parses back to ensure unknown fields survive.

## State, Dependencies, Integration
The test is pure serialization state with no cluster. It depends on protobuf classes, `PBHelperClient`, `DataInputBuffer`, `DataOutputBuffer`, `FsPermission`, and Java object serialization. It integrates HDFS-specific file status wire compatibility with the common FS status schema.

## Risks and Test Signals
High-value signals are byte-level proto round trips and permission-extension bit checks. Risks are ordinal coupling between proto enum values, deprecated permission extension behavior, and accidental loss of unknown fields during schema evolution.
