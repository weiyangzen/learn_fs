# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.2.xml lines 11997-17973

## Chunk Scope

- Work item: `subset-b-007174`
- Source chunk: `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.2.xml`, lines 11997-17973
- Parent file role: JDiff XML snapshot of the public Apache Hadoop Common 2.8.2 API surface. This file is metadata for API compatibility reports, not runtime Hadoop source.
- Chunk shape: this slice starts in the tail of `org.apache.hadoop.fs.FsServerDefaults`, covers many public filesystem, permission, ViewFS, HA, protocolPB, and IO APIs, and ends mid-definition in `org.apache.hadoop.io.IntWritable`.

## Purpose

This chunk records the public API contract for Hadoop Common 2.8.2 across core filesystem abstractions, client-side namespace virtualization, high-availability management primitives, and the beginning of the Hadoop `Writable` serialization library. JDiff consumes this XML to compare releases, detect binary/source API additions or removals, and render compatibility documentation.

The XML does not implement behavior directly. Its functional value is the shape of the exported API: class/interface names, inheritance, visibility, method signatures, fields, exceptions, deprecation markers, and selected Javadoc text. Downstream build, release, and compatibility tooling relies on this metadata staying aligned with the compiled Hadoop Common artifacts for the same release.

## Important APIs, Types, And Functions

The visible `org.apache.hadoop.fs` portion includes:

- `FsServerDefaults`, ending in this chunk, exposes client-visible server defaults such as block size, checksum bytes, packet size, replication, file buffer size, encrypted-transfer flag, trash interval, checksum type, key-provider URI, and default storage policy ID.
- `FsStatus` is a `Writable` capacity/used/remaining-space value object with `write` and `readFields` serialization methods.
- `GlobalStorageStatistics` is a singleton enum registry for `StorageStatistics` instances. Its `get`, `put`, `reset`, and `iterator` methods are synchronized, so the public contract includes global mutable statistics registration.
- `GlobFilter` implements `PathFilter` for POSIX-style glob patterns with brace expansion and optional user-supplied filter composition.
- `LocalFileSystem` extends `ChecksumFileSystem` and wraps local filesystem operations with checksum handling. It exposes `getScheme`, `getRaw`, `pathToFile`, local copy helpers, checksum-failure quarantine, and symlink support.
- `LocatedFileStatus` extends `FileStatus` by carrying `BlockLocation[]` information and preserving comparison/equality behavior.
- `Path` is Hadoop's URI-like filesystem path abstraction. It includes path construction from strings, URIs, and parent/child pairs; normalization helpers; `getFileSystem(Configuration)` resolution; path inspection; string/equality/hash/comparison behavior; `depth`; and deprecated `makeQualified(FileSystem)`.
- `PathFilter`, `PositionedReadable`, `Seekable`, and `Syncable` define extension contracts for filtering paths, positional reads, stream seeking, and flush/sync semantics. `PositionedReadable` explicitly documents thread-safety expectations and warns that not all implementations satisfy them.
- `QuotaUsage` stores namespace and storage-space quota usage, including per-`StorageType` quota/consumption APIs and formatted output helpers for shell-style reporting.
- `RawLocalFileSystem` extends `FileSystem` and exports local file operations: open, append, create, non-recursive create, rename, truncate, delete, list, mkdir, working directory handling, status, local-output staging, close, owner/permission/time mutations, and symlink APIs.
- `StorageStatistics` is an abstract statistics source keyed by name/scheme with iterators over long-valued counters, lookup, tracking checks, and reset.
- `StorageType` models supported storage media and exposes default/empty constants, transient/movable/quota flags, list helpers, and parsing from integer or string.
- `Trash` and abstract `TrashPolicy` define pluggable trash behavior, including moving paths to the appropriate volume's trash, checkpoints, expunge, superuser emptier runnable, and path-specific trash directory lookup for encryption-zone correctness.
- `XAttrCodec` and `XAttrSetFlag` define extended-attribute string/byte encodings and CREATE/REPLACE validation.

Other filesystem-related packages in this chunk include:

- `org.apache.hadoop.fs.ftp.FTPException` and `FTPFileSystem`, an Apache Commons Net-backed `FileSystem` with `ftp` scheme, URI/working-directory methods, open/create/delete/list/status/mkdir/rename operations, FTP config key constants, and a warning that create streams must be closed before other APIs are used.
- `org.apache.hadoop.fs.permission.AccessControlException`, deprecated in favor of `org.apache.hadoop.security.AccessControlException`; `AclEntry`, `AclEntryScope`, `AclEntryType`, `AclStatus`; `FsAction`; and `FsPermission`. Together these model ACL entries, ACL status, permission bits, sticky/ACL/encrypted extended bits, umask configuration, default file/dir/cache-pool permissions, symbolic parsing, and `Writable` serialization of permissions.
- `org.apache.hadoop.fs.viewfs.NotInMountpointException`, `ViewFileSystem`, and `ViewFs`. `ViewFileSystem` implements the legacy `FileSystem` API, while `ViewFs` implements `AbstractFileSystem`; both expose a client-side mount-table filesystem with broad forwarding APIs for create/open/delete/list/status/checksum/block-location/access, ACLs, xattrs, snapshots, storage policies, delegation tokens, and mount-point introspection.

The HA portion includes:

- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` as checked exceptions for HA management failure modes.
- `FenceMethod`, the operator/plugin extension point for validating fencing arguments and attempting to fence an `HAServiceTarget`.
- `HAServiceProtocol`, the RPC-facing protocol for `monitorHealth`, `transitionToActive`, `transitionToStandby`, and `getServiceStatus`, plus a `versionID` field.
- `HAServiceProtocolHelper`, which wraps HA RPC calls and unwraps `RemoteException` into specific exceptions.
- `HAServiceTarget`, an abstract service endpoint descriptor with IPC, health-monitor, and ZKFC addresses; fencer lookup; fencing configuration validation; proxy creation; fencing parameter maps; and auto-failover flag.
- `org.apache.hadoop.ha.protocolPB.HAServiceProtocolPB` and `ZKFCProtocolPB`, protobuf-backed protocol interfaces that extend generated blocking services and `VersionedProtocol`.

The `org.apache.hadoop.io` portion starts the Writable/data-structure library:

- `AbstractMapWritable` is the base for map writables. It carries class-to-byte-ID mappings with IDs in the 1-127 range, supports copy, `Configurable`, and `Writable` read/write.
- `ArrayFile`, `ArrayPrimitiveWritable`, and `ArrayWritable` cover dense file-based integer-to-value maps and optimized array serialization for primitive arrays or homogeneous `Writable[]` values.
- `BinaryComparable` defines byte-backed ordering, equality, and hashing for writable-comparable byte sequences.
- `BloomMapFile` adds dynamic Bloom-filter acceleration around `MapFile` and exposes `BLOOM_FILE_NAME`, `HASH_COUNT`, and `delete`.
- Primitive and byte wrappers include `BooleanWritable`, `BytesWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, and the beginning of `IntWritable`. These expose constructors, `set`/`get`, `readFields`, `write`, comparison, equality, hashing, and string formatting.
- `ByteBufferPool` and `ElasticByteBufferPool` define reusable `ByteBuffer` allocation/release, with the elastic implementation synchronizing `getBuffer` and `putBuffer` while caching buffers without a documented hard maximum.
- `CompressedWritable` is an abstract lazy-inflating compressed `Writable`: final public `readFields`/`write` wrap subclass-provided `readFieldsCompressed`/`writeCompressed`, and field access must call `ensureInflated`.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`.
- `DefaultStringifier` serializes arbitrary objects through Hadoop serialization into strings and configuration entries, with helpers for single values and arrays.
- `EnumSetWritable` wraps `EnumSet` with `Writable` and `Configurable` support, requiring element type information when the set is null or empty.
- `GenericWritable` wraps one of a fixed set of configured `Writable` classes more compactly than `ObjectWritable`; subclasses provide `getTypes()`, and configuration is passed to configurable wrapped values before deserialization.

## Control Flow

The JDiff XML has no runtime control flow, but it represents several behavioral flows:

1. Filesystem clients construct `Path` instances, resolve them to a `FileSystem` or `AbstractFileSystem`, then call operations such as `open`, `create`, `delete`, `listStatus`, `mkdirs`, `rename`, `setOwner`, ACL/xattr methods, snapshot methods, or storage-policy methods.
2. Local filesystem implementations map `Path` to `java.io.File`, enforce working-directory and parent-creation rules, perform local IO, optionally manage checksum side files, and report `FsStatus`/`FileStatus` metadata.
3. Trash operations choose a `TrashPolicy` from configuration, resolve the correct trash location for the path's real filesystem or encryption zone, move a deletion target into trash, checkpoint current trash, and expunge old checkpoints.
4. ViewFS initializes an in-memory mount table from `fs.viewfs.mounttable.*` configuration, resolves incoming paths against mount links, and forwards the requested operation to the target filesystem. Its API surface must preserve the behavior of both `FileSystem` and `AbstractFileSystem` callers while hiding the mount table indirection.
5. HA management code creates an `HAServiceTarget`, obtains protocol proxies, monitors health, requests state transitions, and invokes fencing methods when a failed active service must be prevented from continuing. Helper calls normalize remote exception handling for callers.
6. Writable serializers write type or value metadata to `DataOutput` and reconstruct objects from `DataInput`. Collection wrappers (`AbstractMapWritable`, `ArrayWritable`, `EnumSetWritable`, `GenericWritable`) add class/type metadata around payload values, while primitive writables use compact fixed encodings.

## State And Persistence Behavior

The XML file itself is static release metadata and persists only the API description. The APIs it describes expose several stateful subsystems:

- `GlobalStorageStatistics` is global mutable process state. Its synchronized registry methods create, return, iterate, and reset statistics objects by name.
- `StorageStatistics` objects expose live counter state that does not necessarily represent a single point-in-time snapshot.
- `FsStatus`, `FsPermission`, ACL objects, quota usage, and many `Writable` wrappers are serializable API state. Compatibility depends on preserving wire formats for `readFields`/`write`.
- `RawLocalFileSystem`, `LocalFileSystem`, and `FTPFileSystem` mutate persistent external storage through create, append, rename, truncate, delete, mkdir, permission, owner, and timestamp operations.
- `Trash` and `TrashPolicy` persist deletion targets as renamed filesystem entries under trash directories and create/delete checkpoint directories. Path-specific trash handling matters for HDFS encryption zones because cross-zone rename is not allowed.
- `ViewFs` and `ViewFileSystem` keep the mount table in client memory, while target filesystems hold all durable file data and metadata. Their configuration-derived mapping is stateful from the client's perspective but not itself persisted by ViewFS.
- HA APIs describe service state transitions between active and standby, health status, fencing configuration, and RPC proxy state. Fencing methods can intentionally mutate external cluster/process/storage state.
- `CompressedWritable` keeps compressed data until lazy inflation, so objects have a compressed/uncompressed lifecycle that subclasses must honor by calling `ensureInflated`.
- `BytesWritable` exposes its backing byte array through `getBytes`; callers must respect `getLength()` because capacity can exceed logical data length.

## Dependencies And Integration Points

- JDiff tooling depends on this XML schema and on the file matching the compiled Hadoop Common 2.8.2 public API.
- Filesystem APIs depend heavily on `org.apache.hadoop.conf.Configuration`, `FileSystem`, `AbstractFileSystem`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `RemoteIterator`, `Path`, `FsPermission`, `FsAction`, `Progressable`, `DataChecksum.Type`, and Java `URI`, `File`, `DataInput`, and `DataOutput`.
- `LocalFileSystem` integrates with `ChecksumFileSystem` and a raw local filesystem. `RawLocalFileSystem` is the direct bridge from Hadoop paths to local OS files.
- `FTPFileSystem` depends on Apache Commons Net for FTP transport and uses Hadoop configuration keys for host, port, user, and password resolution.
- Permission and ACL classes integrate with Hadoop shell, NameNode/client metadata APIs, `RemoteException` unwrapping, and the newer `org.apache.hadoop.security.AccessControlException`.
- `TrashPolicy` integrates with configuration key `fs.trash.classname`, filesystem home/trash layout, and encryption-zone-aware deletion behavior.
- ViewFS integrates with mount-table configuration under `fs.viewfs.mounttable.*`, `ConfigUtil`, `Constants`, and `FsConstants`, then forwards to target schemes such as HDFS, local, S3-compatible filesystems, or other Hadoop filesystems.
- HA protocol interfaces integrate with Hadoop IPC, generated protobuf services, `VersionedProtocol`, `NodeFencer`, `ZKFCProtocol`, and service-specific implementations such as HDFS NameNode HA.
- IO wrappers integrate with Hadoop's `Writable`, `WritableComparable`, `WritableComparator`, `Configurable`, serialization framework, `MapFile`, sequence files, and MapReduce key/value transport.

## Risks And Edge Cases

- This chunk starts and ends inside classes. It begins after the first `FsServerDefaults` constructor lines and ends mid-`IntWritable`, so merge/reconciliation must combine adjacent chunks for complete class-level conclusions.
- Because this is compatibility metadata, omissions or stale signatures can mislead release tooling even if the runtime source is correct. Constructors, thrown exceptions, visibility, abstract/final/static flags, and deprecation text are all part of the effective report.
- `PositionedReadable` documents thread-safety as required but also warns that some filesystems do not satisfy it. Consumers such as HBase can rely on this contract and fail when an implementation violates it.
- `Path` mixes URI semantics with Hadoop-specific normalization and Windows absolute-path handling. Cross-platform changes risk breaking equality, qualification, or filesystem resolution.
- `RawLocalFileSystem` and `LocalFileSystem` expose many local mutation paths. Edge cases include non-recursive create, Windows empty-destination-directory rename behavior, symlink target/status differences, and checksum-failure quarantine behavior.
- Trash handling is subtle around symlinks, mount points, and HDFS encryption zones. Using the older no-argument `getCurrentTrashDir()` can produce a wrong location for encrypted paths.
- ViewFS has a large forwarding surface. Missing path resolution, failure to preserve exceptions, or inconsistent behavior between `ViewFileSystem` and `ViewFs` can affect ACLs, xattrs, snapshots, storage policies, checksums, delegation tokens, and mount-point operations.
- FTP streams have a documented blocking hazard: a stream returned by `create` must be closed before other `FTPFileSystem` APIs are used.
- `AccessControlException` in `fs.permission` is deprecated but still present for compatibility and remote exception unwrapping; removing it would break older clients.
- ACL effective-permission calculation has backward-compatibility behavior for old NameNodes requiring the caller to pass `FsPermission`.
- `FsPermission` has fixed short and extended-short encodings for sticky, ACL, and encrypted bits. Incorrect serialization or parsing changes can corrupt metadata interpretation.
- `AbstractMapWritable` only has byte IDs 1 through 127 per map instance. Workloads with too many distinct contained classes can exceed the design limit.
- `ArrayPrimitiveWritable` does not copy the underlying primitive array; external mutation can change serialized output.
- `BytesWritable.getBytes()` exposes backing storage whose capacity can exceed logical length, and deprecated `get`/`getSize` remain in the API for compatibility.
- `ElasticByteBufferPool` intentionally has no maximum cache size, which can retain memory under workloads that return many large buffers.
- `GenericWritable` depends on subclass `getTypes()` ordering because the wire format stores compact type identifiers. Reordering allowed classes can break compatibility.

## Test And Validation Signals

- JDiff validation: compare this XML against the Hadoop Common 2.8.2 compiled jars and generated Javadocs to ensure signatures, deprecations, inheritance, and exceptions match.
- API compatibility tests: run JDiff or equivalent checks from 2.8.x neighboring releases and verify expected changes for filesystem, ViewFS, HA, and IO classes.
- Filesystem contract tests: exercise `FileSystem`/`AbstractFileSystem` operations for local, raw local, FTP where configured, and ViewFS mount-table forwarding, including create/open/delete/rename/list/status/truncate/symlink paths.
- Path tests: cover URI construction, parent/child resolution, Windows path detection, root/parent/depth behavior, qualification, equality, and string round trips.
- Positioned-read tests: verify concurrent positional reads do not alter stream position for implementations claiming the contract.
- Trash tests: validate disabled trash, already-in-trash behavior, checkpoint/expunge, mount point and symlink resolution, and encryption-zone path-specific trash directory selection.
- Permission and ACL tests: round-trip `FsPermission` through `Writable`, parse octal and symbolic modes, apply umask, preserve sticky/ACL/encrypted bits, parse ACL specs, and compute effective permissions with both new and old NameNode-compatible paths.
- ViewFS tests: mount multiple target filesystems, verify mount-point introspection, forwarding of ACL/xattr/snapshot/storage policy calls, delegation-token aggregation, and consistent behavior between `ViewFileSystem` and `ViewFs`.
- HA tests: simulate health monitor calls, active/standby transitions, access-control failures, remote exception unwrapping, invalid fencing configs, fencing method ordering, and auto-failover proxy lookup.
- Writable tests: round-trip primitive writables, `BytesWritable` length/capacity behavior, array wrappers, enum sets including empty/null cases with element type, compressed lazy inflation, `GenericWritable` subclass type mappings, and `AbstractMapWritable` class-ID serialization.

## Notes For Merge/Reconciliation

- This is a chunk-level report only for `subset-b-007174`; no final per-file report was produced.
- The previous chunk is needed for the start of `FsServerDefaults`; the next chunk is needed for the rest of `IntWritable` and later `org.apache.hadoop.io` APIs.
- Keep this report under `Docs/researches/chunks/`. The final source-tree-aligned per-file document should be produced later by the merge/reconciliation lane after all chunks for `Apache_Hadoop_Common_2.8.2.xml` are available.
