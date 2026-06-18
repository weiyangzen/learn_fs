# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/JsonUtilClient.java

## Purpose

`JsonUtilClient` converts WebHDFS/HttpFS JSON maps into Hadoop client objects. It is the client-side schema bridge for file status, blocks, tokens, quotas, checksums, ACLs, xattrs, snapshots, storage policies, erasure coding, server defaults, trash roots, and block locations.

## Important APIs, Types, And Functions

Important converters include `toRemoteException`, `toToken`, `toFileStatus`, `toHdfsFileStatusArray`, `toDirectoryListing`, `toDatanodeInfo`, `toLocatedBlock`, `toLocatedBlocks`, `toContentSummary`, `toQuotaUsage`, `toMD5MD5CRC32FileChecksum`, `toAclStatus`, `toXAttrs`, `toDelegationToken`, `getStoragePolicies`, `toECPolicy`, `toFsServerDefaults`, snapshot converters, `toBlockLocationArray`, and scalar helpers `getBoolean/getInt/getLong/getString/getList/getMap`.

## Control Flow

Each method expects a known JSON envelope and constructs the corresponding protocol or filesystem type. Some converters tolerate older or optional fields: datanodes can derive `ipAddr` and `xferPort` from legacy `name`, file status defaults absent `fileId` or storage policy, and server defaults provide proto-equivalent fallback values. Remote exceptions are converted to `RemoteException`, with `UnsupportedOperationException` thrown directly.

## State And Persistence

The class has no mutable persistent state. It allocates object graphs from parsed JSON maps and byte arrays. Checksum reconstruction reads serialized checksum bytes from JSON into Hadoop checksum implementations.

## Dependencies And Integration Points

It integrates tightly with `WebHdfsFileSystem` response decoding, Jackson object reading for xattr names, `DFSUtilClient`, HDFS protocol classes, token classes, ACL and permission classes, `DataChecksum`, `BlockStoragePolicy`, and erasure-coding metadata.

## Risks

Schema drift is the main risk. Many methods cast unchecked `Map`/`List`/`Number` values and will fail late if servers change field names or numeric shapes. `BlockLocation` parses `corrupt` through `Boolean.getBoolean(String)`, which checks system properties rather than normal string truth; this is a notable correctness risk. XAttr names parse a JSON-encoded string nested inside JSON, so escaping must match server output exactly.

## Test Signals

Tests need golden JSON for every WebHDFS response shape, old-server datanode compatibility, missing optional fields, unsupported-operation remote exceptions, checksum algorithm/length validation, xattr encodings, snapshot diff listings, EC policy states, storage-policy arrays, and block-location corruption flags.
