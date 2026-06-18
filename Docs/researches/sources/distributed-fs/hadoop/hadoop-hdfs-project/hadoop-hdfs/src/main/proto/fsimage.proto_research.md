# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/fsimage.proto

## Purpose

`fsimage.proto` defines the protobuf on-disk layout for HDFS filesystem image files. It describes the file summary, namesystem metadata, inode records, under-construction files, directory children, inode references, snapshots and snapshot diffs, string table, delegation-token secret manager state, cache manager state, and erasure-coding policy state. The source was read as a complete 353-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.fsimage`, Java outer class `FsImageProto`, and imports `hdfs.proto`, `acl.proto`, and `xattr.proto`. Top-level messages include `FileSummary`, `NameSystemSection`, `INodeSection`, `FilesUnderConstructionSection`, `INodeDirectorySection`, `INodeReferenceSection`, `SnapshotSection`, `SnapshotDiffSection`, `StringTableSection`, `SecretManagerSection`, `CacheManagerSection`, and `ErasureCodingSection`. Nested inode messages model files, directories, symlinks, ACL features, compact XAttrs, quotas by storage type, under-construction features, references, snapshots, and diffs.

## Control Flow

The file comment defines the FSImage grammar: magic header, repeated sections, file summary, and trailing summary length. Sections contain delimited protobuf messages, and large/repeated entities are streamed within section boundaries rather than always held in one top-level message. Loaders read the summary/index, seek to sections, then decode each section according to its declared name. Savers write sections and finish with `FileSummary`.

## State and Persistence Behavior

This schema is the persistent HDFS namespace image format. It stores namespace IDs, generation stamps, block IDs, transaction ID, rolling upgrade time, inode IDs, inode type-specific metadata, block lists, ACL/XAttr compact encodings, quotas, directory child relationships, references for snapshots, snapshot metadata/diffs, string interning table, delegation keys/tokens, cache directives/pools, and erasure-coding policies. The file uses compact fixed-width encodings for permissions, ACL entries, and XAttr names to keep images small and tied to the string table.

## Dependencies and Integration Points

It integrates with NameNode FSImage save/load code, edit-log replay, namespace recovery, snapshot subsystem, ACL/XAttr features, delegation token secret manager, cache manager, erasure coding, and the string table. It depends on common block/storage, ACL, and XAttr protobuf definitions.

## Risks and Edge Cases

This is a durable on-disk compatibility contract. Field number changes, required/optional changes, compact bit-layout mistakes, section-name changes, or summary/index corruption can make a namespace image unreadable. Large directory entries must stay within protobuf message size limits, noted explicitly for `DirEntry`. Snapshot diff sections combine fixed metadata with variable repeated records, so section-boundary parsing must match writer counts. Permission/ACL/XAttr compact encodings depend on exact bit allocation and string table IDs.

## Test Signals

Tests should cover FSImage save/load round trips across files, directories, symlinks, ACLs, XAttrs, snapshots, under-construction files, quotas, cache directives, delegation tokens, erasure coding, and rolling upgrades. Compatibility tests should load older FSImage files, validate section indexes and compression codecs, exercise large directories near message-size limits, and compare namespace checksums before and after save/load.
