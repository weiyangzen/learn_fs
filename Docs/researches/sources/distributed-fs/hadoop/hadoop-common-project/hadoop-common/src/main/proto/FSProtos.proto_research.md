# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/FSProtos.proto

## Purpose
`FSProtos.proto` defines stable private protobuf records for common filesystem metadata. It encodes permissions, file status fields, and local filesystem path handles used by Hadoop common filesystem APIs.

## Important APIs, types, and functions
Messages are `FsPermissionProto`, `FileStatusProto`, and `LocalFileSystemPathHandleProto`. `FileStatusProto` defines `FileType` values `FT_DIR`, `FT_FILE`, `FT_SYMLINK` and `Flags` bits for ACL, encryption, erasure coding, and snapshots. Fields cover path, length, permission, owner, group, times, symlink target, replication, block size, encryption data, erasure-coding data, and flags.

## Control flow
This is a schema file. Serialization is handled by generated Java classes; Java converters populate optional metadata fields from `FileStatus`-like objects and consumers inspect presence/defaults during deserialization.

## State and persistence
The schema defines wire and serialized state. Optional fields allow sparse metadata. Field numbers are stable and comments reserve compatibility with HDFS status field IDs even though cross-serialization is not promised.

## Dependencies and integration points
It generates `org.apache.hadoop.fs.FSProtos` and integrates with `FileStatus`, `PBHelper`, and `LocalFileSystemPathHandle`. It is part of Hadoop's private stable protobuf surface.

## Risks and test signals
Risks include changing required fields or field numbers, misinterpreting unset optional fields as defaults, and incompatibility if encryption or EC opaque bytes change format. Test signals include protobuf compatibility tests, `FileStatus` round-trips, local path-handle serialization tests, and clients reading older messages without newer optional fields.
