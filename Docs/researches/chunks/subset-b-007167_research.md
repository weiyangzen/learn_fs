# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 11999-17994

## Purpose

This chunk is generated JDiff API metadata for Hadoop Common 2.8.0. It records public compatibility contracts rather than implementation bodies. The covered region starts at `org.apache.hadoop.fs.FsStatus`, spans filesystem path/status/local-filesystem/trash/xattr APIs, FTP and viewfs filesystem adapters, permission and ACL types, high-availability service protocols, protocol-buffer bridge markers, and the beginning of `org.apache.hadoop.io` Writable utilities through the first `IOUtils.copyBytes` overloads.

The file is important as public API evidence: it captures class/interface names, inheritance, implemented interfaces, constructors, method signatures, parameter and return types, checked exceptions, public/protected fields, deprecation status, and Javadoc contracts. Consumers should use this chunk to reason about source and binary compatibility for these Hadoop Common packages, not as proof of private implementation details.

## Scope Notes

- The source slice begins in the `org.apache.hadoop.fs` package and ends inside `org.apache.hadoop.io.IOUtils`; `IOUtils` is only partially covered here.
- Several package entries are empty or marker-only in this slice: `org.apache.hadoop.fs.crypto`, `org.apache.hadoop.fs.sftp`, `org.apache.hadoop.fs.shell.find`, `org.apache.hadoop.ha.protocolPB` except protocol interfaces, and `org.apache.hadoop.http.lib`.
- The XML references nested helper types such as builders, mount points, and option classes, but this chunk often records only the outer public method surface that uses those types.

## API Inventory

### `org.apache.hadoop.fs` status, path, and filters

- `FsStatus` represents filesystem capacity, used bytes, and remaining bytes. It implements `Writable`, has a `(long capacity, long used, long remaining)` constructor, exposes `getCapacity()`, `getUsed()`, `getRemaining()`, and serializes through `write(DataOutput)` and `readFields(DataInput)`.
- `GlobalStorageStatistics` is represented as a public final enum-style singleton surface for global `StorageStatistics` registration. Its synchronized methods `get(String)`, `put(String, StorageStatisticsProvider)`, `reset()`, and `iterator()` provide a process-wide registry for filesystem/storage statistics. `put` requires provider-created statistics to be non-null and name-matched.
- `GlobFilter` implements `PathFilter` for POSIX glob patterns with brace expansion. Constructors accept a glob string alone or a glob string plus a user `PathFilter`, and may throw `IOException` for invalid patterns. `hasPattern()` exposes whether the expression contains glob syntax, and `accept(Path)` combines glob matching with the optional user filter.
- `InvalidPathException` extends `HadoopIllegalArgumentException` for invalid path strings or filesystem-specific path rejections. It accepts either just a path or a path plus reason.
- `LocatedFileStatus` extends `FileStatus` with `BlockLocation[]`. Constructors wrap an existing `FileStatus` plus locations or fully specify length, directory flag, replication, block size, modification/access times, permission, owner, group, symlink, path, and locations. Equality, comparison, and hashing are path-name based, matching `FileStatus` semantics.
- `Options` is a final holder for filesystem operation option types referenced elsewhere, such as create and checksum options.
- `ParentNotDirectoryException` is an `IOException` signaling that an expected parent path is not a directory.
- `Path` is Hadoop's URI-backed filesystem path type. Constructors combine parent/child strings or `Path` instances, create from raw strings, `URI`, or `(scheme, authority, path)` components. Static helpers strip scheme/authority, merge paths while preserving the first path's scheme/authority, and detect Windows absolute paths. Instance methods expose URI conversion, filesystem lookup via `getFileSystem(Configuration)`, absolute/root/name/parent/depth checks, suffixing, string/equals/hash/compare behavior, and a deprecated `makeQualified(FileSystem)` overload. Public constants include `/` separator values, `"."`, and `WINDOWS`.
- `PathFilter` is the single-method predicate interface `accept(Path)`.
- `PositionedReadable` defines positional read methods that do not change stream offset: `read(position, buffer, offset, length)`, `readFully(position, buffer, offset, length)`, and `readFully(position, buffer)`. The contract requires thread-safe operations but warns that not all filesystems satisfy this, and some expose intermediate seek position via `Seekable.getPos()`.
- `ReadOption` is an enum of filesystem read options.
- `Seekable` defines `seek(long)` and `getPos()` for streams with a mutable current offset; seeking past EOF is prohibited by contract.
- `StorageStatistics` is an abstract statistics base with a name, optional scheme, iterators over long statistics, lookup by key, `isTracked(String)`, and `reset()`. Values are not guaranteed to be a point-in-time snapshot.
- `StorageType` is an enum surface for storage media. It exposes `isTransient()`, `supportTypeQuota()`, `isMovable()`, list helpers for all/movable/quota-supporting types, parse helpers from int or string, and public `DEFAULT`/`EMPTY_ARRAY` constants.
- `Syncable` defines filesystem flush semantics. Deprecated `sync()` is replaced by `hflush()`. `hflush()` makes client-buffered data visible to new readers, while `hsync()` is closer to POSIX fsync and pushes data toward disk devices.

### Local, trash, xattr, and FTP filesystem APIs

- `LocalFileSystem` extends `ChecksumFileSystem` and wraps a raw local filesystem with checksum behavior. It initializes from URI/configuration, returns scheme `file`, exposes the raw filesystem, converts `Path` to `File`, copies to/from local paths, reports checksum failures by moving files to a bad-file directory on the same device, and supports symlink creation/link status/link target lookup.
- `RawLocalFileSystem` extends `FileSystem` for direct local-file access. Its surface includes static `useStatIfAvailable()`, path-to-file conversion, URI/initialization, `open`, `append`, multiple `create` and `createNonRecursive` variants, protected output-stream factories with optional `FsPermission`, `rename`, Windows empty destination directory handling, `truncate`, recursive/non-recursive `delete`, `listStatus`, one-directory mkdir helpers, `mkdirs`, working/home directory management, local-output staging, `close`, status queries, `setOwner`, `setPermission`, `setTimes`, symlink support, link status, and link target resolution.
- `Trash` is a `Configured` facade for trash behavior. It can be constructed from `Configuration` or a specific `FileSystem` plus configuration. Static `moveToAppropriateTrash` resolves symlinks/mount points to use the trash in the actual target volume. Instance methods include `isEnabled()`, `moveToTrash(Path)`, checkpoint creation, checkpoint expunge, current-trash directory lookup, emptier creation, and deletion-interval access.
- `TrashPolicy` is the pluggable trash-policy base class. It is `Configured`, can be initialized with configuration, filesystem, and home directory, has a static `getInstance` factory, and defines abstract/overridable operations for enablement, moving to trash, checkpointing, expunging, emptier creation, current trash directory, and delete interval.
- `UnsupportedFileSystemException` is an `IOException` used when no implementation exists for a requested scheme or filesystem contract.
- `XAttrCodec` is an enum for extended-attribute value encoding/decoding. Static helpers decode values from strings and encode byte arrays. It is the string/binary boundary for shell/API xattr values.
- `XAttrSetFlag` is an enum for xattr mutation modes. `validate(String, boolean xattrExists, EnumSet<XAttrSetFlag>)` checks create/replace constraints against current existence.
- `FTPException` wraps FTP-related failures in a runtime exception.
- `FTPFileSystem` extends `FileSystem` using Apache Commons Net. It reports scheme `ftp`, has a default port hook, initializes from URI/configuration, and implements `open`, `create`, unsupported `append`, `delete`, `getUri`, `listStatus`, `getFileStatus`, `mkdirs`, `rename`, working/home directory methods, and configuration-key constants for user, password, host, host port, buffer size, block size, and same-directory rename limitations. Its `create` Javadoc warns that an acquired stream must be closed before other API calls, or later calls may block.

### Permissions and ACLs

- `org.apache.hadoop.fs.permission.AccessControlException` extends `IOException` but is deprecated in favor of `org.apache.hadoop.security.AccessControlException`. Constructors support default remote-exception unwrapping, message, and cause.
- `AclEntry` is an immutable ACL element with type, optional name, permission action, and scope. It exposes getters, stable and normal string forms, equality/hash behavior, `parseAclSpec(String, boolean)`, `parseAclEntry(String, boolean)`, and `aclSpecToString(List)`. Stable string output is intended for shell output and serialization compatibility.
- `AclEntryScope` is an enum for access/default scope.
- `AclEntryType` is an enum for ACL entry type and exposes normal plus stable string representations.
- `AclStatus` is an immutable ACL status object with owner, group, sticky bit, ordered ACL entries, associated `FsPermission`, equality/hash/string behavior, and effective-permission calculation. The two-argument `getEffectivePermission(AclEntry, FsPermission)` exists for old NameNode compatibility and may throw `IllegalArgumentException` when the old-NameNode path lacks the required permission argument.
- `FsAction` is the enum of read/write/execute combinations. It exposes implication, `and`, `or`, `not`, string-to-action lookup, and each enum value's symbolic permission string.
- `FsPermission` implements `Writable` for file/directory permission bits. Constructors accept user/group/other `FsAction`s with optional sticky bit, a short mode, copy source, or octal/symbolic string. It supports immutable creation, action getters, `fromShort`, `write`, `readFields`, static `read(DataInput)`, `toShort`, `toExtendedShort` for ACL/encryption bits, equality/hash/string behavior, `applyUMask`, `getUMask(Configuration)`, sticky/ACL/encrypted-bit getters, `setUMask`, default directory/file/cache-pool permissions, and `valueOf` for Unix symbolic strings. Public constants expose permission-string length and umask keys/defaults.

### ViewFS client-side mount table

- `NotInMountpointException` extends `UnsupportedOperationException` for operations attempted outside a mount point.
- `ViewFileSystem` extends `FileSystem` and implements a client-side mount table equivalent to `ViewFs` for the classic `FileSystem` API. Its surface mirrors filesystem operations and delegates them through mount links: URI/scheme, initialize, working/home directories, status, `open`, `create`, `append`, `rename`, `delete`, directory creation, list operations, checksum and block location queries, symlink support, ACL/xattr operations, delegation tokens, child filesystem and mount-point introspection, checksum verification/write toggles, and snapshot operations.
- `ViewFs` extends `AbstractFileSystem` and implements the same mount-table concept for the `AbstractFileSystem` API. It resolves paths through in-memory mount table configuration, delegates creation/open/delete/rename/list/status/block/checksum/access/symlink/owner/permission/replication/time/ACL/xattr/snapshot/storage-policy operations, exposes mount points and delegation tokens, and validates names. Its Javadoc documents `viewfs:///` usage and `fs.viewfs.mounttable.*` configuration keys for mount links. Merge mounts are documented as not implemented.

### High availability APIs

- `BadFencingConfigurationException` is an `IOException` for invalid configured fencing methods or arguments.
- `FailoverFailedException` is a checked exception for failed service failover.
- `FenceMethod` is the operator-extensible fencing interface. `checkArgs(String)` validates configured method arguments during startup, and `tryFence(HAServiceTarget, String)` attempts to prevent the target node from making progress. Implementations may also implement `Configurable` for framework configuration injection.
- `HAServiceProtocol` is the versioned HA management protocol. It defines `monitorHealth()`, `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(StateChangeRequestInfo)`, and `getServiceStatus()`, with checked exceptions for health, service-transition, access-control, and IO failures. The protocol is meant for HA frameworks that monitor and fail over services.
- `HAServiceProtocolHelper` provides static helper wrappers around active/standby transitions, converting protocol exceptions into the expected service-failure behavior.
- `HAServiceTarget` represents a target HA service. It exposes service, health-monitor, ZKFC, and fencing addresses, fencing parameters, proxy construction with timeout/configuration, auto-failover support, ZKFC support, transition-target checks, and a delegation-token service. The target object is the integration point between HA controllers, RPC proxies, and fencing.
- `HealthCheckFailedException` extends `IOException` for failed health checks.
- `ServiceFailedException` extends `IOException` for failed HA state transitions.
- `org.apache.hadoop.ha.protocolPB.HAServiceProtocolPB` and `ZKFCProtocolPB` are protobuf bridge interfaces for the HA and ZK failover-controller RPC protocols.

### `org.apache.hadoop.io` Writable and stream utilities

- `AbstractMapWritable` is the base for map-like Writables that carry per-instance class-id maps rather than global static maps. It implements `Writable` and `Configurable`, supports class registration, class/id lookup, synchronized copy from another writable, configuration access, and serialization. The documented class-id range is 1-127, limiting each map instance to 127 distinct classes.
- `ArrayFile` extends `MapFile` as a dense file-backed mapping from integer indexes to values.
- `ArrayPrimitiveWritable` wraps primitive arrays in an optimized Writable format without per-element object creation. It can be empty for deserialization, constructed with a known component type, or wrap an existing primitive array without copying. It exposes component-type inspection, value get/set, and read/write serialization.
- `ArrayWritable` wraps arrays of a single `Writable` value class. Constructors accept the value class, value class plus values, or strings. It exposes value-class lookup, string conversion, object-array conversion, value get/set, and read/write serialization. The docs recommend typed subclasses for reducer inputs.
- `BinaryComparable` is an abstract byte-backed `Comparable`. Subclasses provide `getLength()` and `getBytes()`. It supplies bytewise `compareTo`, comparison against a raw byte range, equality, and hash code using `WritableComparator` byte helpers.
- `BloomMapFile` adds Bloom-filter-assisted lookups to `MapFile` and exposes static `delete(FileSystem, String)` plus `BLOOM_FILE_NAME` and `HASH_COUNT` constants. It is optimized for sparse MapFiles.
- `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, and `IntWritable` are primitive `WritableComparable` wrappers. Each provides default/value constructors, `set`, `get`, `readFields`, `write`, equality/hash, `compareTo`, and `toString` contracts for its primitive type.
- `ByteBufferPool` abstracts pooled `ByteBuffer` allocation and release. `getBuffer(boolean direct, int length)` returns a buffer with at least the minimum requested capacity, and `putBuffer(ByteBuffer)` returns buffers to the pool.
- `BytesWritable` extends `BinaryComparable` and implements `WritableComparable` for resizable byte sequences. It distinguishes logical length from backing capacity, can copy or expose backing bytes, has deprecated `get()`/`getSize()` aliases in favor of `getBytes()`/`getLength()`, supports size/capacity mutation, setting from another `BytesWritable` or byte range, serialization, bytewise equality/hash, and hex-pair string output.
- `org.apache.hadoop.io.Closeable` is deprecated in favor of `java.io.Closeable` and simply extends it.
- `CompressedWritable` is an abstract `Writable` base for lazily inflated compressed data. Its final `readFields` and `write` methods delegate to subclass `readFieldsCompressed` and `writeCompressed`; field-accessing subclass methods must call `ensureInflated()`.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`. Static `constructOutputStream(DataOutput)` returns the input if it is already an `OutputStream`, otherwise wraps it. It implements single-byte and byte-array `write` variants.
- `DefaultStringifier<T>` implements `Stringifier<T>` using Hadoop serialization plus Base64 strings. It can stringify/restore individual objects, close its serializer/deserializer resources, and store/load individual objects or arrays in `Configuration` keys. Array storage rejects empty arrays via `IndexOutOfBoundsException`.
- `ElasticByteBufferPool` is a synchronized `ByteBufferPool` that allocates as needed and caches released direct or heap buffers. It returns the smallest cached buffer with sufficient capacity and intentionally does not cap cache size.
- `EnumSetWritable<E>` wraps `EnumSet` in a `Writable` and `Configurable` collection. It supports null/empty sets only when an explicit element type is provided, exposes iterator/size/add/set/get, element-type lookup, serialization, equality/hash/string, and configuration access.
- `GenericWritable` wraps one of a fixed set of `Writable` classes supplied by subclass `getTypes()`. It stores a compact type index rather than a class name per record, making it more efficient than `ObjectWritable` when value types are known. It is `Configurable` and passes configuration to wrapped configurable instances before deserialization.
- `IOUtils` begins in this chunk. Covered overloads include `copyBytes(InputStream, OutputStream, int, boolean)`, `copyBytes(InputStream, OutputStream, int)`, and `copyBytes(InputStream, OutputStream, Configuration)` plus the start of the configuration/close overload. The documented behavior copies stream contents, optionally closes streams in `finally`, and uses configuration-derived buffer sizing for config-based overloads.

## Control Flow and Behavior

Most behavior in this chunk is expressed as API-level contracts. Filesystem flows are path-oriented: `Path` normalizes and resolves URI-like names, then `getFileSystem(Configuration)` or filesystem-specific methods route operations to the owning `FileSystem`. `LocalFileSystem` layers checksum handling over a raw local filesystem, while `RawLocalFileSystem` maps Hadoop `Path` objects to `java.io.File` and then performs direct local operations. `ViewFileSystem` and `ViewFs` add a client-side resolution stage: incoming paths are matched against mount-table entries, rewritten to target filesystems, and delegated.

Trash operations add an indirection before delete. `Trash.moveToAppropriateTrash` resolves symlinks or mount points so the moved item lands in the trash for the actual backing volume. `TrashPolicy` defines the control hooks for enablement, move, checkpoint, and expunge operations; concrete policy behavior is outside this chunk.

Permission and ACL APIs convert between structured objects and stable string or numeric forms. `AclEntry.parseAclSpec` and `parseAclEntry` parse shell-compatible ACL text, while `toStringStable` supports compatibility-sensitive output. `FsPermission` converts among action triples, shorts, extended shorts, symbolic strings, and configuration-backed umask values. Effective ACL permissions may depend on whether the client is talking to an old NameNode.

HA control flow is protocol-driven. HA frameworks call `monitorHealth()` repeatedly, request transitions to active or standby through `HAServiceProtocol`, and use `HAServiceTarget` to obtain RPC proxies and fencing details. `FenceMethod` implementations are checked at startup and attempted in configured order by the fencing machinery referenced by the docs.

Writable control flow is serialization-centric. Primitive writables, byte-array writables, arrays, enum sets, generic wrappers, map-writable metadata, compressed writables, and stringifiers all define how objects move through `DataInput`/`DataOutput` or configuration strings. `GenericWritable` and `AbstractMapWritable` optimize wire formats by replacing repeated class names with compact ids.

## State and Persistence

- `FsStatus`, `FsPermission`, and most `org.apache.hadoop.io` wrappers persist state through Hadoop `Writable` methods.
- `GlobalStorageStatistics` is synchronized process-global registry state; `reset()` clears all registered statistics data.
- `StorageStatistics` implementations hold mutable metric state, but iterator results are not guaranteed to be a coherent snapshot.
- `Path` is value-like URI state with equality, comparison, and hash behavior tied to normalized path representation.
- `RawLocalFileSystem` and `LocalFileSystem` maintain runtime configuration, working directory, and filesystem handles; their durable state is the host filesystem.
- `Trash` and `TrashPolicy` persist deleted items and checkpoints into filesystem trash directories, but the XML only exposes the management contract.
- `AclEntry` and `AclStatus` are immutable value objects; `FsPermission` can be serialized and can also encode ACL/encryption marker bits in extended short form.
- `ViewFileSystem`/`ViewFs` keep an in-memory mount table initialized from configuration. The mount table itself is configuration-backed rather than persisted by the objects.
- HA target/protocol objects carry runtime endpoint and fencing state; actual HA state is owned by remote services.
- `CompressedWritable` stores compressed bytes until `ensureInflated()` is needed, then materializes subclass fields.
- `DefaultStringifier` persists serialized objects into `Configuration` string values using Base64 encoding.
- `ElasticByteBufferPool` maintains an unbounded in-process cache of returned buffers.

## Dependencies and Integration Points

- Filesystem classes integrate with `FileSystem`, `AbstractFileSystem`, `FileContext`-style APIs, `Configuration`, `Path`, `FileStatus`, `BlockLocation`, `FsServerDefaults`, `FSDataInputStream`, `FSDataOutputStream`, ACL/xattr types, snapshot/storage-policy APIs, and Java `URI`/`File`.
- Local filesystem permission changes depend on OS commands such as `chmod` and `chown`, and symlink behavior depends on platform support.
- FTP support integrates with Apache Commons Net and remote FTP server semantics. Its blocking warning around open create streams is an important integration contract.
- `ViewFileSystem` and `ViewFs` depend on mount-table configuration keys under `fs.viewfs.mounttable.*`, target filesystem implementations, delegation-token collection from child filesystems, and Hadoop's symlink and snapshot contracts.
- Permission APIs integrate with HDFS NameNode ACL behavior, shell command parsing/output, `Configuration` umask keys, and `DataInput`/`DataOutput` serialization.
- HA APIs integrate with Hadoop IPC/protobuf protocol bridges, security access checks, health monitors, ZK failover controllers, fencing implementations, and delegation-token service names.
- `org.apache.hadoop.io` classes integrate with Hadoop serialization, `WritableComparator`, `MapFile`, Bloom filter utilities, `Configuration`, `SerializationFactory`, Java primitive arrays, `ByteBuffer`, and Java stream/data interfaces.

## Risks and Edge Cases

- Because this is generated API XML, it can lag or diverge from implementation source if generation inputs are stale. Treat it as compatibility metadata for the generated artifact.
- `PositionedReadable` requires thread safety but explicitly warns that some filesystem implementations do not honor it; callers like HBase depend on the stronger contract.
- `Path` string handling crosses URI normalization and Windows path parsing. Scheme/authority stripping, drive-letter handling, and relative path merging are common compatibility hazards.
- `RawLocalFileSystem.rename` and `handleEmptyDstDirectoryOnWindows` encode platform-specific rename behavior; tests must cover Windows and non-Windows semantics separately.
- `RawLocalFileSystem.delete` throws when a directory is non-empty and recursive is false; callers relying only on boolean return can miss this checked-exception path.
- `LocalFileSystem.reportChecksumFailure` moves bad files aside on the same device. Failures in that path can hide corruption handling or accidentally reuse suspect storage.
- `Trash.moveToAppropriateTrash` must resolve symlinks and mount points correctly, or deletion may move data into the wrong filesystem's trash.
- `FTPFileSystem.create` can block other API calls until the stream is closed, making resource management and exception cleanup critical.
- `AclStatus.getEffectivePermission(AclEntry, FsPermission)` has old-NameNode compatibility behavior that can throw if `permArg` is missing.
- `FsPermission.toExtendedShort()` may encode values outside normal permission ranges; consumers assuming only `00000`-`01777` can drop ACL/encryption bits.
- `GlobalStorageStatistics` and `ElasticByteBufferPool` are synchronized global or shared state surfaces; they need cleanup/reset in tests to avoid cross-test leakage.
- `ElasticByteBufferPool` intentionally lacks a maximum cache size, so workloads with varied large buffers can retain substantial memory.
- `AbstractMapWritable` has a fixed 1-127 class-id range per map instance. Serializing more distinct Writable classes than that is a hard limit.
- `ArrayPrimitiveWritable` wraps arrays without copying, so later caller mutation can change serialized or observed state.
- `BytesWritable.getBytes()` exposes backing capacity beyond logical length; callers must respect `getLength()` or use `copyBytes()`.
- `CompressedWritable` requires subclasses to call `ensureInflated()` before field access; missing calls can observe stale/uninitialized field state.
- `GenericWritable.getTypes()` must be stable and include only `Writable` classes. Reordering or changing the type list breaks serialized type indexes.
- `IOUtils.copyBytes` close behavior varies by overload and boolean flag; accidental stream closure is a common integration risk.

## Test Signals

- API compatibility checks should assert every class/interface, method signature, constructor, field, checked exception, inheritance relationship, implemented interface, and deprecation marker present in this XML slice.
- `Path` tests should cover constructor normalization, parent/child resolution, scheme/authority preservation and removal, Windows absolute path detection, root/name/parent/depth behavior, suffixing, equality/hash/compare ordering, URI conversion, and filesystem resolution.
- Local filesystem tests should cover checksum-wrapped vs raw behavior, create/append/open/truncate/delete/list/status, permission and owner setting, symlink create/status/target behavior, working-directory resolution, local-output staging, checksum failure quarantine, and platform-specific rename behavior.
- Trash tests should cover disabled trash, already-in-trash cases, move to appropriate backing volume through symlinks or viewfs mount points, checkpoint creation, expunge, emptier scheduling, and policy factory selection.
- XAttr tests should cover encode/decode formats, create-vs-replace validation, missing/existing xattr combinations, and invalid flag sets.
- FTP tests should cover URI initialization, credential/host/port configuration, stream-close requirements after create, unsupported append behavior, same-directory rename limitations, directory creation/listing/status, and remote IO exception propagation.
- Permission and ACL tests should cover stable string round trips, parsing with and without permissions, named and unnamed entries, access/default scopes, effective permissions with old and new NameNode behavior, symbolic and octal `FsPermission` parsing, umask application, extended ACL/encryption bits, Writable round trips, and deprecated access-control exception compatibility.
- ViewFS tests should cover mount-table initialization from `fs.viewfs.mounttable.*`, path resolution, root and mount-point listing, delegation to child filesystems, unsupported paths raising `NotInMountpointException`, symlink handling, ACL/xattr/snapshot/storage-policy delegation, child filesystem enumeration, and delegation token aggregation.
- HA tests should cover fencing argument validation, successful/failed/indeterminate fencing, health monitor exception paths, active/standby idempotence, service status reporting, access-control failures, proxy construction with timeouts, ZKFC address/proxy behavior, auto-failover flags, and protobuf bridge compatibility.
- Writable tests should cover serialization round trips for primitive wrappers, `FsStatus`, `FsPermission`, arrays, primitive arrays, enum sets including null/empty cases with explicit element type, `BytesWritable` length/capacity semantics, `BinaryComparable` ordering, `AbstractMapWritable` class-id limits and copy behavior, `GenericWritable` type-index stability and configuration injection, `CompressedWritable` lazy inflation, `DefaultStringifier` store/load for objects and arrays, `DataOutputOutputStream` wrapping behavior, and `ElasticByteBufferPool` direct/heap reuse ordering.
- `IOUtils` tests for this covered portion should distinguish close and non-close overloads, configuration-derived buffer sizes, exception propagation, and guaranteed close in `finally` when requested.
