<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/protocolPB/PBHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/protocolPB/PBHelper.java

## Purpose
Converts Hadoop filesystem structures between in-memory Java objects and protobuf messages.

## Important APIs, Types, And Functions
`convert(FsPermissionProto)`, `convert(FsPermission)`, `convert(FileStatusProto)`, and `convert(FileStatus)` are the public static helpers.

## Control Flow
Permission conversion stores the short mode. FileStatus conversion switches on proto file type to set directory, symlink, or file fields; file replication is checked to fit 16 bits. Owner and group are weak-interned on proto-to-object conversion. Object-to-proto conversion sets type-specific fields, permission, owner/group, times, and flags for ACL, encryption, erasure coding, and snapshot support.

## State And Persistence
Stateless utility class. Protobuf output is a serialized compatibility format for filesystem RPC/protocol layers.

## Dependencies And Integration Points
Depends on `FSProtos`, `FileStatus`, `Path`, `FsPermission`, and `StringInterner`. Used by protobuf-based filesystem protocols.

## Risks
Replication overflow throws `IOException`; unknown file type throws `IllegalStateException`. Path and symlink are serialized via `toString`, so URI/path formatting compatibility matters. Only `FsPermission.toShort()` is preserved, not subclass create-mode metadata.

## Test Signals
Round-trip file, directory, and symlink statuses; all attribute flags; owner/group interning; replication overflow; and permission short preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/protocolPB/PBHelper.java -->
