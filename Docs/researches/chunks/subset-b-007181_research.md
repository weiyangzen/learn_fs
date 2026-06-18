# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml lines 12036-17993

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.8.3. It starts inside the public API entry for `org.apache.hadoop.fs.FSDataOutputStream`, continues through a large part of `org.apache.hadoop.fs`, `org.apache.hadoop.fs.ftp`, `org.apache.hadoop.fs.permission`, `org.apache.hadoop.fs.viewfs`, `org.apache.hadoop.ha`, and the beginning of `org.apache.hadoop.io`, and ends inside `org.apache.hadoop.io.FloatWritable`.

The source is generated compatibility metadata, not implementation source. The research surface is therefore the externally visible contract: class and interface names, inheritance, implemented interfaces, constructors, fields, method signatures, exceptions, visibility, static/final/abstract/synchronized flags, deprecation state, and embedded Javadocs.

## Purpose

The `org.apache.hadoop.fs` portion documents Hadoop's core filesystem client contracts and several concrete filesystem implementations. It covers seekable and positioned input streams, output streams with flush/sync/drop-behind hooks, server default and status records, global storage statistics, path parsing and qualification, local filesystem implementations, quota accounting, storage types, trash policies, xattr encoding, and FileSystem/FileContext-facing abstractions such as `PathFilter`, `Seekable`, `PositionedReadable`, and `Syncable`.

The `org.apache.hadoop.fs.ftp` portion exposes an FTP-backed `FileSystem` and its exception type. It adapts Hadoop filesystem calls to an FTP server with configuration keys for host, port, user, and password, but its public API also signals limited semantics such as same-directory rename restrictions.

The `org.apache.hadoop.fs.permission` portion documents filesystem authorization value objects: ACL entries and statuses, action masks, permission bits, sticky/ACL/encryption extended bits, umask handling, and access-control exceptions.

The `org.apache.hadoop.fs.viewfs` portion documents both `ViewFileSystem` and `ViewFs`, Hadoop's mount-table based namespace overlay implementations. They route filesystem calls through configured mount links and expose mount-point inspection, path resolution, trash location, ACL/xattr/snapshot/storage-policy forwarding, and delegation-token aggregation.

The `org.apache.hadoop.ha` portion documents public HA control contracts: fencing configuration and execution, health monitoring, active/standby transitions, service status polling, target address/proxy discovery, and failure exception types. The PB protocol marker interfaces identify protobuf-backed RPC protocol surfaces.

The early `org.apache.hadoop.io` portion documents Writable and serialization utilities: class-id maps for heterogeneous maps, primitive/object array wrappers, binary comparison helpers, Bloom map-file metadata, primitive Writables, byte-buffer pooling, compressed lazy Writables, stringification through Hadoop serialization, and writable wrappers for enum sets.

## Important APIs, Types, and Functions

### Core FS Streams and Records

- `FSDataOutputStream` constructors wrap an `OutputStream` with `FileSystem.Statistics` and optionally a starting position. The visible methods include `getPos()`, `close()`, deprecated-style `sync()` compatibility, `hflush()`, `hsync()`, and `setDropBehind(Boolean)`.
- `FSError` is a public `Error` for unexpected filesystem failures assumed to reflect native disk problems.
- `FSInputStream` is an abstract `InputStream` implementing `Seekable` and `PositionedReadable`. It defines abstract `seek(long)`, `getPos()`, and `seekToNewSource(long)`, plus positioned `read(...)`, validation helper `validatePositionedReadArgs(...)`, and `readFully(...)` overloads.
- `FsServerDefaults` is a `Writable` carrier for server-side defaults such as block size, checksum bytes, packet size, replication, file-buffer size, encrypted data-transfer flag, trash interval, checksum type, key-provider URI, and default storage-policy ID.
- `FsStatus` is a `Writable` capacity summary with capacity, used, and remaining byte counts.
- `LocatedFileStatus` extends `FileStatus` with block locations while preserving equality, comparison, and hash behavior from file status semantics.

### Path, Filtering, and Positioned IO

- `Path` is the central URI-like path abstraction. Constructors accept string parent/child pairs, `Path` parent/child pairs, raw strings, `URI`, and scheme/authority/path components.
- `Path` static helpers include `getPathWithoutSchemeAndAuthority(Path)`, `mergePaths(Path, Path)`, and `isWindowsAbsolutePath(String, boolean)`.
- `Path` instance methods expose URI conversion, filesystem lookup from `Configuration`, absolute/root/name/parent/suffix/depth checks, qualification against a default URI and working directory, string conversion, equality, hashing, and ordering.
- Public `Path` constants include `SEPARATOR`, `SEPARATOR_CHAR`, `CUR_DIR`, and `WINDOWS`.
- `PathFilter.accept(Path)` is the single-method filter contract; `GlobFilter` implements it with POSIX glob patterns plus an optional user filter and a `hasPattern()` query.
- `PositionedReadable` declares positioned `read` and `readFully` overloads. `Seekable` declares `seek(long)` and `getPos()`. `Syncable` declares `sync()`, `hflush()`, and `hsync()`.

### Local and Remote Filesystems

- `LocalFileSystem` extends `ChecksumFileSystem`, initializes from URI/configuration, exposes the raw wrapped filesystem, translates `Path` to `File`, handles local copy operations, reports checksum failures, and forwards symlink operations.
- `RawLocalFileSystem` extends `FileSystem` directly and exposes local operations including `open`, `append`, multiple `create` and `createNonRecursive` overloads, output stream creation with permission modes, `rename`, Windows empty-directory handling, `truncate`, `delete`, `listStatus`, mkdir helpers, home/working directory handling, status reporting, local-output staging, ownership/permission/time setters, symlink support, and link status/target access.
- `FTPFileSystem` exposes the `ftp` scheme, default port, initialization, open/create/append/delete/list/status/mkdirs/rename/working-directory operations, and FTP configuration constants such as `FS_FTP_HOST`, `FS_FTP_HOST_PORT`, `FS_FTP_USER_PREFIX`, and `FS_FTP_PASSWORD_PREFIX`.
- `UnsupportedFileSystemException`, `ParentNotDirectoryException`, `InvalidPathException`, `FTPException`, and viewfs `NotInMountpointException` provide typed failure surfaces for invalid paths, unsupported schemes, mount-table violations, and FTP failures.

### Quotas, Storage, Trash, and XAttrs

- `QuotaUsage` records file/directory count, namespace quota, space consumed, space quota, and per-`StorageType` quota/consumption. It has builder-based construction, setters used by subclasses, getters, type-quota availability checks, equality/hash, header formatting, and quota display formatting.
- `StorageStatistics` is an abstract named statistics source with a nullable scheme, iterator over long statistics, keyed long lookup, tracking checks, and reset.
- `GlobalStorageStatistics` is a singleton-style enum registry with synchronized `get`, `put`, `reset`, and `iterator` methods. `put` uses a `StorageStatisticsProvider` and validates that created statistics are non-null and correctly named.
- `StorageType` is an enum with transient, movable, and quota-support queries; parsing helpers; list helpers for movable and quota-supporting types; and `DEFAULT`/`EMPTY_ARRAY` fields.
- `Trash` wraps trash policy use for a filesystem/configuration. It supports `moveToAppropriateTrash`, `isEnabled`, `moveToTrash`, checkpointing, expunging, emptier creation, and current-trash-dir lookup.
- `TrashPolicy` is the abstract policy base with initialization by configuration and filesystem/home, enabled checks, trash movement, checkpoint create/delete, trash-dir lookup with optional path, emptier creation, and static `getInstance` factories. Protected state includes `fs`, `trash`, and `deletionInterval`.
- `XAttrCodec` encodes and decodes xattr values using named codecs. `XAttrSetFlag.validate(EnumSet<XAttrSetFlag>, boolean)` checks create/replace flag combinations against existence state.

### Permissions and ACLs

- `AccessControlException` extends `IOException` with no-arg, message, and throwable constructors.
- `AclEntry` exposes type, optional name, permission action, scope, equality/hash, string rendering, stable string rendering, ACL spec parsing, single-entry parsing, and ACL list serialization.
- `AclEntryScope` and `AclEntryType` are enums. `AclEntryType` has display and stable string forms.
- `AclStatus` exposes owner, group, sticky bit, entries, optional `FsPermission`, equality/hash, string rendering, and effective permission computation for an ACL entry, optionally with a permission argument.
- `FsAction` is an enum-style permission mask with implication, `and`, `or`, `not`, symbolic string, and `getFsAction(String)` parsing.
- `FsPermission` is a `Writable` for user/group/other actions and extended permission bits. It supports construction from actions, shorts, another permission, and symbolic strings; immutable creation; `fromShort`; read/write serialization; static `read(DataInput)`; short and extended-short conversion; umask application and configuration getters/setters; sticky/ACL/encrypted bit accessors; default permission factories; `valueOf(String)`; and public constants for max symbolic length and umask config keys.

### Viewfs Namespace Overlays

- `ViewFileSystem` extends `FileSystem` and provides the `viewfs` scheme. It initializes from a mount-table configuration, resolves paths, exposes mount points and child filesystems, and forwards broad filesystem operations to target filesystems: append/create/delete/list/open/rename/truncate/status/checksum/block locations/access/ACL/xattr/snapshot/quota/server-default/storage-setting operations.
- `ViewFs` is the FileContext-oriented counterpart. It exposes server defaults, default port, home directory, path resolution, internal create, delete, block/checksum/status/link status, filesystem status, status iterators, mkdir, open, truncate, rename internals, symlink support, owner/permission/replication/time setters, mount points, delegation tokens, name validation, ACL/xattr/snapshot/storage-policy operations, and block storage-policy lookup.
- `NotInMountpointException` preserves the offending path and operation context through its constructors and custom message.

### HA Contracts

- `FenceMethod` defines `checkArgs(String)` and `tryFence(HAServiceTarget, String)`, allowing pluggable fencing implementations with separate argument validation and execution.
- `HAServiceProtocol` declares RPC-facing methods `monitorHealth()`, `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(StateChangeRequestInfo)`, and `getServiceStatus()`. It exposes a `versionID` field for protocol compatibility.
- `HAServiceProtocolHelper` provides static wrappers around health checks and active/standby transitions, likely centralizing remote exception handling.
- `HAServiceTarget` abstracts a failover target and exposes service, health-monitor, and ZKFC addresses; fencer lookup and validation; RPC proxy creation for service/health/ZKFC protocols; fencing-parameter maps; parameter augmentation; and auto-failover availability.
- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` expose typed HA failure modes.
- `HAServiceProtocolPB` and `ZKFCProtocolPB` are protobuf protocol interfaces extending `VersionedProtocol`.

### Writable and IO Utilities

- `AbstractMapWritable` is a configurable base for maps that serialize classes via byte IDs. It supports adding mappings, reverse lookup by class or ID, copying another map's class table, `getConf`/`setConf`, and `write`/`readFields`.
- `ArrayPrimitiveWritable` wraps primitive arrays with component-type tracking, declared-component-type checks, setters, getters, and Writable serialization.
- `ArrayWritable` wraps arrays of `Writable`, including a string-array constructor, value-class access, conversion to strings/object arrays, set/get, and read/write.
- `BinaryComparable` is an abstract byte-sequence comparable with `getLength()`, `getBytes()`, byte-array comparison, equality, and hashing.
- `BloomMapFile` exposes Bloom-filter metadata constants and a static `delete(FileSystem, String)` helper for deleting a Bloom map file.
- `BooleanWritable`, `ByteWritable`, `DoubleWritable`, and the start of `FloatWritable` are primitive `WritableComparable` wrappers with zero/value constructors, `set`, `get`, `readFields`, `write`, equality, hash, comparison, and string conversion where visible.
- `ByteBufferPool` declares direct/heap buffer checkout and return. `ElasticByteBufferPool` implements it with synchronized `getBuffer(boolean, int)` and `putBuffer(ByteBuffer)`.
- `BytesWritable` extends `BinaryComparable` for mutable byte arrays. It exposes copy and backing-array access, length and capacity management, multiple `set` forms, serialization, equality/hash, and hex-like string rendering.
- `Closeable` is an `io` package interface marker in this slice.
- `CompressedWritable` is an abstract lazy compressed `Writable`. Final `readFields` stores compressed bytes; `ensureInflated()` inflates on demand; subclasses implement `readFieldsCompressed(DataInput)` and `writeCompressed(DataOutput)`; final `write` writes compressed representation.
- `DataOutputOutputStream.constructOutputStream(DataOutput)` adapts a `DataOutput` to an `OutputStream`, reusing it directly if it already is an `OutputStream`.
- `DefaultStringifier<T>` implements `Stringifier<T>` using Hadoop serialization plus base64. It converts objects to/from strings, closes underlying resources, and stores/loads single objects or arrays in `Configuration`.
- `EnumSetWritable<E>` wraps `EnumSet` with explicit element-type tracking for null or empty sets, implements `Writable` and `Configurable`, and exposes collection operations, value/element-type getters, serialization, equality/hash, string rendering, and configuration access.

## Control Flow

The XML has no runtime control flow, but the APIs imply several important execution paths.

For stream reads, callers either use `Seekable` stateful positioning (`seek`, then normal reads) or `PositionedReadable` stateless positional reads. `FSInputStream.readFully` builds on repeated positioned reads until the requested length is satisfied or an exception is raised. Implementations are expected to validate negative positions and buffer bounds before touching storage.

For output streams, clients write through `FSDataOutputStream`, query `getPos`, then choose durability semantics through `hflush`, `hsync`, or legacy `sync`. `setDropBehind(Boolean)` is an advisory cache-control path that may be ignored or forwarded by concrete streams.

Filesystem operations flow through `FileSystem` or FileContext implementations. `LocalFileSystem` wraps a checksum-aware layer over a raw local filesystem, while `RawLocalFileSystem` directly maps Hadoop paths to local `File` operations. `FTPFileSystem` maps the same abstract methods to FTP commands. `ViewFileSystem` and `ViewFs` first resolve an incoming path against the mount table, then delegate the operation to the target filesystem; mount-table failures surface as viewfs-specific exceptions.

Path handling flows from constructor normalization to URI conversion and qualification. `Path.getFileSystem(conf)` uses the path URI and configuration to resolve a `FileSystem`, while `makeQualified` fills in missing scheme/authority and resolves relative paths against a working directory.

Trash flow is policy-driven. `Trash` constructs or obtains a `TrashPolicy`, checks whether trash is enabled, moves deleted paths into a current trash directory, creates checkpoints, expunges old checkpoints, and can return a background emptier `Runnable`.

Permission and ACL parsing flow from string specs into typed `AclEntry` or `FsPermission` values. Effective ACL permission computation combines an ACL entry with group-mask or permission state, depending on the overload and whether `AclStatus` carries an `FsPermission`.

HA control flow starts with `HAServiceTarget` address/proxy discovery, runs health checks through `HAServiceProtocol.monitorHealth`, performs state transitions with `StateChangeRequestInfo`, and invokes fencing through configured `FenceMethod`/`NodeFencer` support when failover requires the old active to be isolated. Helper methods provide a static wrapper layer for common protocol calls.

Writable control flow follows Hadoop's `write(DataOutput)` and `readFields(DataInput)` convention. Primitive wrappers read/write their primitive values directly. Array wrappers include component-type or value-class metadata. `AbstractMapWritable` serializes a class-to-ID table before map entries in subclasses. `CompressedWritable` defers decompression until field access via `ensureInflated`.

## State and Persistence Behavior

This JDiff file persists the 2.8.3 public API for compatibility comparison. It does not contain Hadoop runtime state, but many documented APIs define durable or process-local state contracts.

`Path` instances persist normalized URI components in memory and are frequently serialized indirectly as strings by callers. Compatibility depends on stable normalization, equality, ordering, and qualification behavior, especially across Windows and Unix path forms.

`FsServerDefaults`, `FsStatus`, `QuotaUsage`, `FsPermission`, array Writables, primitive Writables, `BytesWritable`, `EnumSetWritable`, `AbstractMapWritable`, and `CompressedWritable` define explicit or inherited serialized forms through Writable methods. Any change to field order, encoded type IDs, component-type names, or extended permission bits can break cross-version data exchange.

`GlobalStorageStatistics` is process-global mutable state. Its registry is synchronized for `get`, `put`, `reset`, and iteration, and providers must return objects with matching names. Storage statistics are not durable by themselves, but they are integration points for metrics reporting and diagnostics.

`TrashPolicy` carries protected mutable state for the target filesystem, trash root, and deletion interval. `Trash` operations persist data by renaming/moving user files into trash directories and by creating/deleting checkpoint directories on the underlying filesystem.

`RawLocalFileSystem` persists state directly to the host filesystem: created files, appended data, permissions, owners, timestamps, symlinks, deletes, truncation, and directory creation. `LocalFileSystem` also manages checksum side files through the inherited checksum layer.

`FTPFileSystem` persists state remotely through FTP server operations. Since FTP has weaker metadata and atomicity semantics than HDFS/local filesystems, rename, append, permission, and listing behavior may differ from richer implementations.

`ViewFileSystem` and `ViewFs` generally do not own file content; their persistent behavior is delegated to target filesystems selected by the mount table. Their own state is the in-memory mount-table resolution data built during initialization from `Configuration`.

`HAServiceTarget` stores or derives target addresses, fencer configuration, fencing parameters, and auto-failover availability. State transitions persist in the HA service being controlled, not in the protocol object itself.

`DefaultStringifier` persists serialized objects into `Configuration` values as base64 strings. This makes object persistence dependent on the configured Hadoop `Serialization` implementation and class compatibility.

`ElasticByteBufferPool` keeps process-local buffer caches split by direct/heap choice and capacity. Its Javadocs explicitly say it does not cap maximum cache size, so returned buffers can be retained for reuse until the pool is discarded.

## Dependencies and Integration Points

This chunk depends heavily on Java platform types: `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `File`, `URI`, `InetSocketAddress`, `ByteBuffer`, arrays, collections, enums, `IOException`, and related exception types.

Key Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configurable` for filesystem initialization, path qualification, umask/defaults, viewfs mount tables, stringifier serialization selection, and `EnumSetWritable` configuration.
- `org.apache.hadoop.fs.FileSystem`, `FileContext`-style classes, `FileStatus`, `BlockLocation`, `FileChecksum`, `ContentSummary`, `RemoteIterator`, `FsStatus`, `FsServerDefaults`, and `BlockStoragePolicySpi` for filesystem operations.
- `org.apache.hadoop.fs.permission` types across ACL, access, and permission APIs, including `FsAction`, `FsPermission`, `AclEntry`, and `AclStatus`.
- `org.apache.hadoop.io.Writable`, `WritableComparable`, `Stringifier`, and Hadoop serialization infrastructure for durable binary/string encoding.
- `org.apache.hadoop.util.DataChecksum.Type` for server default checksum metadata.
- `org.apache.hadoop.security.AccessControlException`, delegation token types, and HA RPC protocol classes for authorization, token collection, and service control.
- `org.apache.hadoop.ipc.VersionedProtocol` and protobuf protocol interfaces for HA and ZKFC RPC compatibility.
- `org.apache.hadoop.fs.viewfs` mount-table configuration, which is the central integration point for namespace overlays.
- Apache Commons Logging in `FTPFileSystem.LOG`.

Package markers for `org.apache.hadoop.fs.crypto`, `org.apache.hadoop.fs.sftp`, `org.apache.hadoop.fs.shell.find`, and `org.apache.hadoop.http.lib` appear in this span without public classes in the listed lines.

## Risks and Edge Cases

- This chunk starts in the middle of `FSDataOutputStream` and ends in the middle of `FloatWritable`; adjacent chunks are required for complete class reports.
- JDiff metadata omits method bodies. Exact validation details, path normalization rules, FTP command behavior, viewfs resolution mechanics, HA remote exception translation, and Writable byte layouts require implementation-source review.
- `FSInputStream` implementations must keep stateful seek and stateless positioned reads coherent. Bugs can corrupt callers that mix normal reads, `seek`, and positional reads concurrently.
- `readFully` must handle short reads and EOF accurately. Returning early or swallowing EOF breaks consumers that rely on full-buffer semantics.
- `FSDataOutputStream.sync`, `hflush`, and `hsync` have distinct durability expectations in Hadoop. Filesystems that silently weaken these operations can create data-loss surprises.
- `setDropBehind(Boolean)` is advisory and nullable. Implementations and callers must tolerate unsupported cache hints and a null "restore default" value.
- `Path` has platform-sensitive Windows absolute-path handling. Changes in URI parsing, authority stripping, or qualification can break cross-platform applications and serialized path strings.
- `RawLocalFileSystem` maps Hadoop permissions and ownership to host OS behavior. Permission, symlink, truncation, and rename semantics vary across Unix and Windows.
- `handleEmptyDstDirectoryOnWindows` indicates a platform-specific rename edge case for empty destination directories; changes here can break Windows compatibility.
- `FTPFileSystem` exposes mutable remote state through a protocol with limited atomicity and metadata fidelity. Same-directory rename constraints, missing append support, partial transfers, and connection failures are high-risk paths.
- `QuotaUsage` per-storage-type accounting depends on `StorageType` support and availability checks. Callers must distinguish unset quota from unavailable consumed values.
- `GlobalStorageStatistics` is synchronized but process-global. Duplicate names, wrong provider behavior, or reset during metrics collection can affect unrelated filesystem instances.
- `StorageType.parseStorageType` has a `fallback` overload. Incorrect fallback use can hide invalid configuration.
- Trash behavior is configuration-sensitive. Disabled trash, wrong trash roots, checkpoint deletion, and cross-filesystem moves can lead to permanent deletion or unexpected storage consumption.
- `XAttrSetFlag.validate` must enforce create/replace combinations precisely; accepting contradictory flags can overwrite or fail to create attributes unexpectedly.
- ACL string parsing must preserve stable string forms for compatibility with CLI output, audit logs, and tests.
- `FsPermission` has multiple representations: symbolic string, short, extended short, sticky bit, ACL bit, encrypted bit, and umask configuration. Losing extended bits during conversion is a compatibility and security risk.
- `ViewFileSystem` and `ViewFs` must guard mount boundaries carefully. Operations such as rename, snapshot, ACL, xattr, storage policy, and trash may not be valid across target filesystems.
- Delegation-token aggregation in `ViewFs` must avoid duplicates while still collecting every target filesystem token needed by distributed jobs.
- HA fencing APIs are safety-critical. A `FenceMethod` that validates arguments but returns true without isolating the old active can permit split brain.
- HA transition methods can throw `ServiceFailedException`, `AccessControlException`, and `IOException`; callers need clear retry and failure policies.
- `HAServiceTarget.getProxy` overloads include timeout parameters. Incorrect timeout selection can make failover too slow or too eager.
- `AbstractMapWritable` uses byte IDs for classes. ID collisions or incompatible class-table evolution can break deserialization.
- `ArrayPrimitiveWritable` must reject non-primitive or mismatched component types where declared. Otherwise serialized data can be misread.
- `BytesWritable.getBytes()` and deprecated-style `get()` expose backing storage, while `copyBytes()` returns a defensive copy. Callers that ignore `getLength()` can read stale capacity bytes.
- `BytesWritable.setCapacity` and `setSize` can retain or discard backing bytes; tests should cover growth, shrinkage, and serialization length.
- `CompressedWritable.ensureInflated()` is a required precondition before field access by subclasses. Missing calls can read stale or null inflated fields.
- `DefaultStringifier` persistence is only stable when the same serialization framework and compatible item class are available when loading.
- `ElasticByteBufferPool` has no maximum cache-size policy. High-cardinality capacity requests or returning very large buffers can produce unbounded memory retention.
- `EnumSetWritable` allows null or empty values only when an element type is known. Serialization must preserve that type even when the set has no elements.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks that confirm every public/protected class, interface, field, constructor, method, exception, visibility flag, and deprecation marker in this JDiff range remains stable for Hadoop Common 2.8.3.
- `FSInputStream` tests for negative positioned reads, buffer bounds validation, short read loops in `readFully`, EOF handling, `seek/getPos` consistency, and `seekToNewSource` behavior.
- `FSDataOutputStream` tests for position tracking, close propagation, `hflush`/`hsync`/`sync` delegation, and nullable drop-behind handling.
- `FsServerDefaults` and `FsStatus` Writable round-trip tests with all fields, including key provider URI and default storage-policy ID.
- `Path` tests for all constructors, URI conversion, scheme/authority stripping, path merging, Windows absolute paths, root/parent/name/suffix/depth behavior, comparison/equality/hash, and qualification against default URI plus working directory.
- `GlobFilter` tests for simple globs, brace expansion, invalid patterns, user-filter composition, and `hasPattern`.
- `LocalFileSystem` and `RawLocalFileSystem` tests for create/open/append/delete/rename/truncate/list/mkdirs/status, checksum-failure reporting, symlink support, permission/owner/time setters, local-output staging, and Windows-specific rename behavior.
- `FTPFileSystem` integration tests with a controlled FTP server for configuration parsing, default port, open/create/delete/list/status/mkdirs/rename, working directory, unsupported append behavior if applicable, and same-directory rename restrictions.
- `QuotaUsage` tests for namespace and space quotas, per-storage-type quota/consumption, unset/unavailable states, headers, display formatting, equality, and hash code.
- `StorageStatistics` and `GlobalStorageStatistics` tests for provider validation, duplicate-name behavior, synchronized registry access, iterator snapshots, reset, keyed lookups, and scheme reporting.
- `StorageType` tests for transient/movable/quota-support flags, parsing with and without fallback, and list helpers.
- `Trash` and `TrashPolicy` tests for disabled/enabled trash, move-to-trash success and failure, current trash dir calculation, checkpoint creation/deletion, expunge, emptier scheduling, and policy selection from configuration.
- `XAttrCodec` tests for text/hex/base64 encode/decode variants and invalid values; `XAttrSetFlag.validate` tests for create/replace/existence combinations.
- Permission and ACL tests for `AclEntry` parsing and stable rendering, ACL spec list parsing, ACL status effective-permission calculations, `FsAction` algebra, `FsPermission` symbolic/short/extended-short conversions, sticky/ACL/encrypted bits, umask config migration, default factories, and Writable round trips.
- `ViewFileSystem` and `ViewFs` tests for mount-table initialization, path resolution, mount-point listing, delegation to target filesystems, cross-mount rename failures, ACL/xattr/snapshot/storage-policy forwarding, child filesystem and delegation-token aggregation, and not-in-mountpoint errors.
- HA tests for fencing argument validation, fencing success/failure propagation, health monitoring, active/standby transition calls, service status retrieval, target proxy timeout handling, fencing parameter composition, ZKFC proxy lookup, and auto-failover flags.
- Protocol compatibility tests for `HAServiceProtocol.versionID`, `HAServiceProtocolPB`, and `ZKFCProtocolPB`.
- `AbstractMapWritable` tests for class-to-ID registration, copy behavior, unknown class/ID handling, configuration propagation, and serialized class-table compatibility.
- `ArrayPrimitiveWritable` and `ArrayWritable` tests for component/value class preservation, primitive type coverage, empty arrays, string-array conversion, set/get behavior, and Writable round trips.
- `BinaryComparable` and `BytesWritable` tests for lexicographic comparison, backing-array versus copied-array behavior, length/capacity resizing, equality/hash, serialization length, and string rendering.
- Primitive Writable tests for Boolean, Byte, Double, and Float constructors, setters/getters, read/write, comparison, equality/hash, and string conversion.
- `ByteBufferPool` and `ElasticByteBufferPool` tests for direct versus heap buffers, minimum requested capacity, reuse after return, synchronized concurrent access, and large-buffer retention behavior.
- `CompressedWritable` subclass tests verifying lazy inflation, final read/write paths, repeated `ensureInflated`, and compatibility of compressed serialized bytes.
- `DataOutputOutputStream` tests for direct reuse when the `DataOutput` is already an `OutputStream` and byte/array writes through the adapter.
- `DefaultStringifier` tests for object and array store/load in `Configuration`, empty-array behavior, close idempotence, missing serialization failures, and class compatibility errors.
- `EnumSetWritable` tests for non-empty, empty, and null enum sets with element type; add/iterator/size behavior; config propagation; equality/hash; string output; and serialized round trips.

## Cross-Chunk Notes

The previous chunk is required to complete `FSDataOutputStream`; this chunk begins at its constructors and later methods after earlier class metadata. The next chunk is required to complete `FloatWritable`; this chunk includes only its constructors, `set`, `get`, `readFields`, and the opening of `write`.

Several classes referenced here have nested builders, mount-point records, providers, or protocol request/status types whose definitions are outside this exact line range. The merge lane should reconcile those adjacent definitions before producing a final per-file report for `Apache_Hadoop_Common_2.8.3.xml`.
