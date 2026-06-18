# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/protocolPB/TestFSSerialization.java

## Purpose
Verifies serialization round trips for filesystem metadata, especially `FileStatus` boolean feature flags for ACL, encryption, and erasure coding.

## Important APIs, Types, and Functions
The file tests Hadoop writable serialization via `FileStatus.write` and `readFields` using `DataOutputBuffer` and `DataInputBuffer`, plus protobuf conversion through `PBHelper.convert(FileStatus)` and `PBHelper.convert(FileStatusProto)`. `checkFields` compares all important `FileStatus` fields.

## Control Flow
`testWritableFlagSerialization` iterates all eight combinations of `acl`, `crypt`, and `ec` flags. For each combination it builds a `FileStatus`, writes it to a data buffer, reads into a fresh `FileStatus`, checks object equality, and verifies individual fields. `testUtilitySerialization` builds a `FileStatus` with an immutable `FsPermission`, converts to `FileStatusProto`, converts back, and applies the same equality/field checks.

## State and Persistence
State is entirely in-memory buffers and protobuf objects. No filesystem calls are made; `Path` values are synthetic.

## Dependencies and Integration Points
This test targets the protocol bridge between filesystem Java objects and protobuf/writable encodings used by Hadoop RPC and persisted metadata exchange. It depends on `FSProtos.FileStatusProto`, `PBHelper`, `FileStatus`, `Path`, and `FsPermission`.

## Risks and Edge Cases
Flag loss during serialization is the primary risk. The writable test covers all flag combinations, while the protobuf test covers a representative unflagged status. It does not cover symlink fields beyond null, directory statuses, or protobuf preservation of ACL/encryption/EC flags if those are set.

## Test Signals
Passing tests indicate that core `FileStatus` fields survive writable and protobuf round trips, and that ACL/encryption/erasure-coded booleans are not dropped by writable serialization.
