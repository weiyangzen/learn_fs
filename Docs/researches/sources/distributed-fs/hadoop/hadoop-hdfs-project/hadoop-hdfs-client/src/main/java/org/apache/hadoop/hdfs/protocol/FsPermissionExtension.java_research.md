# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/FsPermissionExtension.java

## Purpose
`FsPermissionExtension` is a deprecated HDFS-private subclass of `FsPermission` that encodes ACL, encryption, and erasure-coded flags in high bits while preserving base permission compatibility.

## APIs and Behavior
One constructor wraps a base `FsPermission` and explicit booleans; another decodes the high bits from a short. `toExtendedShort()` ORs permission bits with ACL, encrypted, and EC flags. `getAclBit()`, `getEncryptedBit()`, and `getErasureCodedBit()` expose flags. Equality and hash code intentionally delegate to the base class.

## State, Dependencies, and Integration
The class integrates with `HdfsFileStatus.convert`, which uses it to preserve redundant flags for compatibility with older applications. The preferred source of these attributes is now `FileStatus`.

## Risks and Test Signals
Equality ignores extension flags through superclass behavior, which can hide differences. Tests should cover bit encode/decode, compatibility with plain `FsPermission`, assertions in `HdfsFileStatus.convert`, and deprecation-safe behavior for old clients.
