# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/JsonUtil.java

## Purpose

`JsonUtil.java` is the WebHDFS JSON serialization utility for turning HDFS protocol objects, filesystem status objects, quota objects, ACL/XAttr objects, snapshots, block locations, checksums, storage policies, server defaults, and exceptions into the response shape expected by WebHDFS and related HTTP clients. The source was read as a complete 800-line file for this report.

## Important APIs, Types, and Functions

The class is a static utility around a shared Jackson `ObjectMapper`. Public entry points include overloaded `toJsonString(...)` methods for `Token`, `Exception`, `HdfsFileStatus`, `DirectoryListing`, `LocatedBlocks`, `ContentSummary`, `QuotaUsage`, `MD5MD5CRC32FileChecksum`, `AclStatus`, XAttr lists, `BlockStoragePolicy`, `FsServerDefaults`, snapshot reports, `SnapshottableDirectoryStatus[]`, `SnapshotStatus[]`, `BlockLocation[]`, `FsStatus`, `ErasureCodingPolicyInfo[]`, and trash-path `Collection<FileStatus>`. Important map helpers include `toJsonMap(HdfsFileStatus)`, `getEcPolicyAsMap(ErasureCodingPolicy)`, datanode/location/block conversion helpers, quota/type-quota conversion, erasure-coding policy conversion, and the visible-for-testing `toJsonMap(BlockLocation)`.

## Control Flow

Each public serializer performs a null check, builds Java `Map`, `Object[]`, or list structures with stable key names, then calls either `toJsonString(String,Object)` or `ObjectMapper.writeValueAsString`. Nested HDFS objects are flattened recursively: located blocks contain block tokens, block metadata, storage types, datanode locations, and cached locations; directory listings wrap arrays under `FileStatuses.FileStatus`; ACL entries are converted to stable strings; XAttrs are encoded according to the requested `XAttrCodec`; snapshot diff reports walk entry lists and convert byte paths to strings. For several older WebHDFS contracts the method wraps data under a top-level class-like key such as `FileStatus`, `LocatedBlocks`, `AclStatus`, or `RemoteException`.

## State and Persistence Behavior

The class owns no durable state. The only long-lived runtime state is the static `ObjectMapper` and the reusable `EMPTY_OBJECT_ARRAY`. All serialized data is derived from caller-supplied in-memory protocol/model objects. It indirectly exposes persisted HDFS state such as inode metadata, quotas, block locations, erasure-coding policy, snapshot data, cache information, and token/checksum bytes, so field names and omitted/null fields are part of the WebHDFS compatibility surface.

## Dependencies and Integration Points

Direct dependencies include Hadoop filesystem classes, HDFS protocol types, ACL/XAttr helpers, datanode/block metadata types, `RemoteException`, token classes, Guava `ImmutableMap`, Jackson `ObjectMapper`, and utility converters such as `DFSUtilClient` and `StringUtils`. The main integration point is WebHDFS/HttpFS response generation and exception handling, especially `ExceptionHandler`, WebHDFS operations returning file status/listing/block/checksum/quota/snapshot data, and clients that parse Hadoop's documented JSON field names.

## Risks and Edge Cases

Compatibility is the primary risk: changing wrapper names, key names, null-versus-empty-array behavior, octal permission formatting, symlink/path encoding, or erasure-coding fields can break clients. Several `writeValueAsString` calls swallow `IOException` and return `null`, so serialization failures can become ambiguous empty responses. The static mapper is safe only because it is configured before use and not mutated in request paths. `ParamFilter` can alter request parameter casing, but this class must preserve response key casing. Large directory listings, block reports, or snapshot diff arrays can allocate large object arrays before serialization.

## Test Signals

Useful tests include golden JSON tests for WebHDFS status/listing/checksum/quota/ACL/XAttr/snapshot responses, null and empty-array behavior tests, erasure-coding policy round-trip checks, exception JSON shape checks through `ExceptionHandler`, and compatibility tests against documented WebHDFS examples. Existing visible test hook `toJsonMap(BlockLocation)` signals direct unit coverage for block location conversion.
