# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.2.xml lines 12106-17958

## Scope

This chunk is part of the generated JDiff API description for Hadoop Common 2.10.2. It starts inside the tail of `org.apache.hadoop.fs.FilterFileSystem`, continues through a large portion of the public `org.apache.hadoop.fs` API, covers FTP, permissions, ViewFS, and HA protocol packages, and ends at the beginning of `org.apache.hadoop.io.AbstractMapWritable`.

The source is XML API metadata, not executable Java source. The useful code research signal is therefore the public and protected compatibility surface: classes, interfaces, constructors, fields, method signatures, checked exceptions, deprecation state, and embedded Javadoc contracts. Runtime behavior below is inferred from these API contracts and from the relationships expressed by inheritance, implemented interfaces, and declared exceptions.

## Purpose

The chunk documents Hadoop Common's client-side filesystem abstraction surface. It covers stream contracts for seekable and positioned reads, output stream sync semantics, server default metadata, filesystem status and storage accounting, path normalization and URI resolution, local and FTP filesystem implementations, permission and ACL types, extended attribute encoding, trash policy extension points, and ViewFS mount-table forwarding.

It also documents high-availability control APIs. The HA package section defines fencing configuration errors, failover errors, the pluggable `FenceMethod` interface, the `HAServiceProtocol` state-transition protocol, RPC helper wrappers, and `HAServiceTarget` descriptors that bind service, health-monitor, ZKFC, and fencing endpoints.

Because this is a JDiff baseline, its purpose is also compatibility tracking. Public signatures in this XML represent API contracts that downstream filesystem implementations, shell commands, RPC clients, HA controllers, and application code may compile against.

## Important APIs, Types, and Data

The first part is the end of `FilterFileSystem`. It forwards many `FileSystem` operations to a wrapped `FileSystem` field `fs`, with an optional `swapScheme` field. Covered methods include local-output completion, space usage, default block size and replication, server defaults, status lookup, `msync`, access checks, symlink operations, checksum access, checksum verification/write toggles, ownership, permissions, primitive create/mkdir, snapshots, ACLs, xattrs, storage policy operations, trash roots, and `createFile`/`appendFile` builders.

`FsConstants` defines common scheme and URI constants: local filesystem URI, FTP scheme, ViewFS URI and scheme, and the maximum symlink traversal count. These constants anchor scheme dispatch and symlink-resolution limits across implementations.

`FSDataInputStream` wraps an input stream and implements the Hadoop read interfaces: `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `ByteBufferPositionedReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `CanUnbuffer`, and `StreamCapabilities`. Its methods expose seek/get-position, positioned reads into byte arrays and `ByteBuffer`, full reads, alternate-source seeking, enhanced pooled `ByteBuffer` reads and release, readahead/drop-behind hints, file descriptor access, unbuffering, and capability queries.

`FSDataOutputStream` wraps an `OutputStream` and implements `Syncable`, `CanSetDropBehind`, and `StreamCapabilities`. It exposes write position, close, `sync`, `hflush`, `hsync`, drop-behind, and capability queries. `FSDataOutputStreamBuilder` is the fluent creation/append builder with `permission`, `bufferSize`, `replication`, `blockSize`, `recursive`, `progress`, `create`, `overwrite`, `append`, `checksumOpt`, and abstract `build`.

`FSInputStream`, `Seekable`, and `PositionedReadable` define the lower-level seek and positioned-read contracts. `FSInputStream` supplies validation and default positioned-read/readFully behavior over abstract `seek`, `getPos`, and `seekToNewSource`. `PositionedReadable` explicitly states that positioned reads should not change the current file offset and are expected to be thread-safe, while warning that some filesystems do not satisfy that requirement.

`FsServerDefaults` is a `Writable` carrying client-visible defaults such as block size, bytes per checksum, write packet size, replication, file buffer size, data-transfer encryption, trash interval, checksum type, key provider URI, and default storage policy ID. `FsStatus` is a `Writable` capacity/used/remaining record. `GlobalStorageStatistics` is an enum singleton registry for `StorageStatistics`, with get/put/reset/iterator operations. `StorageStatistics` defines a named statistics provider with scheme lookup, long-stat iteration, tracked-stat lookup, and reset.

`GlobFilter` combines glob pattern evaluation with an optional user `PathFilter`. `InvalidPathException`, `ParentNotDirectoryException`, `UnsupportedFileSystemException`, and `FSError` are filesystem error types for invalid paths, parent type violations, unsupported schemes, and severe local filesystem errors.

`LocalFileSystem` extends `ChecksumFileSystem` and wraps a raw local filesystem, adding checksum behavior, symlink support, local copy operations, and checksum-failure reporting. `RawLocalFileSystem` extends `FileSystem` and exposes direct local file operations: path-to-`File` mapping, URI/initialization, open, append, create, non-recursive create, output stream creation with mode, rename including a Windows empty-directory special case, truncate, delete, list, mkdir variants, working directory/home directory, status, local-output movement, file status, owner/permission/time mutation, and symlink methods.

`LocatedFileStatus` extends `FileStatus` with block location arrays and preserves equality, ordering, and hash semantics. `QuotaUsage` records namespace and space quota usage, including per-`StorageType` quotas and consumption, output headers, human-readable formatting, and storage-type headers. `StorageType` models storage media, including default and empty-array constants, transient/quota/movable predicates, list helpers, quota-supporting and movable type lists, and parsing from integer or string.

`Path` is the central path/URI value type. It offers string, URI, component, and parent/child constructors; static helpers to strip scheme/authority, merge paths, and detect Windows absolute paths; URI conversion; filesystem resolution from a `Configuration`; absolute/root/name/parent/suffix queries; equality, hash, comparison, depth; a deprecated `makeQualified(FileSystem)` overload; and separator/current-directory/Windows constants.

`StreamCapabilities` defines string capability keys for `hflush`, `hsync`, `readahead`, `dropbehind`, `unbuffer`, `readbytebuffer`, and positioned `preadbytebuffer`. `StreamCapabilitiesPolicy` centralizes policy behavior for unbuffering and the not-implemented message. `Syncable` defines `hflush` visibility-to-new-readers semantics and `hsync` fsync-like durability semantics, with legacy `sync` deprecated in favor of `hflush`.

`Trash` and `TrashPolicy` define pluggable delete-to-trash behavior. `Trash` is the user-facing accessor for moving paths to appropriate trash, checkpointing, expunging, locating current trash directories, and obtaining a superuser emptier runnable. `TrashPolicy` is the extension point, with old and new initialization contracts, enabled checks, move/checkpoint/delete operations, current trash root lookup with path-sensitive handling for encryption zones, emptier creation, and factory methods driven by `fs.trash.classname`. It stores protected `fs`, `trash`, and `deletionInterval` state.

`XAttrCodec` converts xattr byte values between raw bytes and display/input strings using text, hex (`0x`), and base64 (`0s`) conventions. `XAttrSetFlag` validates create/replace semantics against whether an xattr currently exists.

`FTPFileSystem` extends `FileSystem` for the `ftp` scheme. It exposes initialization, default port, open, create, delete, URI, list, file status, mkdirs, rename, working directory, home directory, and working-directory mutation. Constants cover FTP configuration keys for user, host, port, password, data connection mode, transfer mode, default buffer/block sizes, and a same-directory rename constraint. `FTPException` wraps lower-level failures in a runtime exception.

The `org.apache.hadoop.fs.permission` package covers permissions and ACLs. `AccessControlException` is the permission-denied exception. `AclEntry` exposes type, optional name, permission action, scope, stable string conversion, ACL spec parsing, individual entry parsing, and ACL string rendering. `AclEntryScope` and `AclEntryType` are enum surfaces. `AclStatus` exposes owner, group, sticky bit, entries, optional permission, equality/hash/string behavior, and effective-permission calculation. `FsAction` models read/write/execute bit combinations with implication, intersection, union, complement, and symbol lookup. `FsPermission` is a `Writable` for user/group/other actions plus sticky/ACL/encrypted bits, with short/octal/string conversions, umask application and configuration, immutable construction, defaults for files/directories/cache pools, and value parsing.

`NotInMountpointException`, `ViewFileSystem`, and `ViewFs` define the client-side mount table APIs. `ViewFileSystem` implements the classic `FileSystem` surface and delegates operations through configured mount points, including append/create/delete/list/open/rename/truncate, ACLs, xattrs, snapshots, server defaults, checksum toggles, child filesystems, mount-point listing, and trash-root logic. `ViewFs` implements the `AbstractFileSystem` version with similar forwarding plus token aggregation, name validation, link status, storage policies, and detailed mount-table configuration docs for `viewfs:///` and `fs.viewfs.mounttable.*`.

The HA section defines `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException`. `FenceMethod` validates fencing arguments and attempts to fence an `HAServiceTarget`, returning true, false, or throwing bad-configuration errors. `HAServiceProtocol` exposes health monitoring, transitions to active/standby/observer, status lookup, and a `versionID` field. `HAServiceProtocolHelper` wraps static RPC calls and unwraps `RemoteException` into specific exceptions. `HAServiceTarget` supplies service, health-monitor, and ZKFC addresses; a configured `NodeFencer`; fencing preflight checks; HA and ZKFC proxies; transition-target state; fencing parameter maps; and feature flags for automatic failover and Observer support.

`org.apache.hadoop.ha.protocolPB` declares protobuf/RPC bridge interfaces `HAServiceProtocolPB` and `ZKFCProtocolPB`, each combining the generated protobuf blocking service interface with `VersionedProtocol`. `org.apache.hadoop.http.lib` contributes package documentation for configurable HTTP filter initializers such as `StaticUserWebFilter`. The chunk ends immediately after the `AbstractMapWritable` class header and its implemented `Writable`/`Configurable` interfaces begin.

## Control Flow

For filesystem streams, the common read path starts at `FileSystem.open`, which returns `FSDataInputStream`. Sequential consumers call normal `DataInputStream` reads and may move the cursor with `seek`. Random readers call `PositionedReadable.read` or `readFully`, which should leave the stream offset unchanged. Implementations can route byte-array positioned reads through `FSInputStream` defaults, but must preserve EOF, offset validation, and thread-safety expectations. Enhanced read paths can use `ByteBuffer` or pooled `ByteBuffer` methods, followed by `releaseBuffer`; `unbuffer` releases cached resources when supported.

For writes, callers either use legacy `FileSystem.create`/`append` paths or the `FSDataOutputStreamBuilder`. The builder accumulates permission, buffer, replication, block size, recursive-parent, progress, create/overwrite/append, and checksum options before `build` validates and creates or appends the file. Once a stream exists, `hflush` makes user-buffered data visible to new readers, while `hsync` asks the implementation to push data toward storage durability. `sync` is kept for compatibility but is deprecated.

`FilterFileSystem`, `LocalFileSystem`, `RawLocalFileSystem`, `FTPFileSystem`, `ViewFileSystem`, and `ViewFs` all sit on the filesystem dispatch path. `FilterFileSystem` generally forwards calls to its wrapped filesystem. `LocalFileSystem` layers checksum behavior over a raw implementation. `RawLocalFileSystem` maps Hadoop `Path` values to local `File` operations. `FTPFileSystem` translates the core filesystem verbs to FTP operations and warns that create streams must be closed before other FTP APIs are used. ViewFS resolves a mount-table path to a target filesystem and target path, then forwards the operation to that target.

Trash control flow is policy-driven. `Trash.moveToAppropriateTrash` resolves symlinks or mount points to pick the volume-specific trash root, then delegates to the configured `TrashPolicy`. Policies initialize from configuration and filesystem, decide whether trash is enabled, move paths, create checkpoints, delete old checkpoints, and return an emptier runnable. The newer path-aware trash-directory API exists because encryption zones and mount-specific roots can make a single home-directory trash location invalid.

ACL and permission flow runs through value parsing and validation before filesystem mutation. `AclEntry.parseAclSpec` and `parseAclEntry` convert user-facing ACL strings into structured entries. `FsAction` bit operations support effective-permission calculations. `FsPermission` converts between symbolic/octal/short forms and applies umasks before creation or mutation. `XAttrSetFlag.validate` gates xattr creation or replacement based on current existence.

ViewFS mount resolution is the most important namespace control flow in this chunk. A `viewfs:///` or authority-specific URI selects a mount table from `fs.viewfs.mounttable.*` configuration. Operations resolve the incoming `Path` against link entries, fallback roots, or merge-link concepts documented in the API text, then forward the actual filesystem call. Trash-root methods add special handling to keep trash inside mount points when configured and to support local trash roots for encryption zones, snapshots, cloud-store containers, and fallback mounts.

HA control flow is event and RPC driven. A controller monitors a service by calling `monitorHealth` and `getServiceStatus`; unhealthy active services can trigger failover. State changes are requested through `transitionToActive`, `transitionToStandby`, or `transitionToObserver`, each receiving `StateChangeRequestInfo` and throwing `ServiceFailedException`, `AccessControlException`, or `IOException` on failure. Fencing control flow first calls `checkFencingConfigured`, then attempts configured `FenceMethod` instances in order through a `NodeFencer`, using `HAServiceTarget` endpoint and parameter data. `HAServiceProtocolHelper` is used when clients need RPC exception unwrapping.

## State and Persistence Behavior

Most state described here is client-side object state or serialized metadata rather than persistent implementation code. `FSDataInputStream` and `FSDataOutputStream` wrap underlying streams and expose current stream position. Readahead, drop-behind, unbuffer, and capability state depend on the underlying stream implementation and may be unsupported.

`FsServerDefaults`, `FsStatus`, `FsPermission`, and `QuotaUsage` are value objects that cross API boundaries. `FsServerDefaults`, `FsStatus`, and `FsPermission` implement `Writable`, so field ordering and compatibility matter for Hadoop serialization. Permission and quota objects may represent persistent filesystem metadata, but this XML only records their public accessors and conversions.

`Path` values persist as normalized URI-like names. Scheme, authority, path, Windows handling, and separator constants are compatibility-sensitive because they feed filesystem resolution, equality, ordering, and configuration lookup.

`TrashPolicy` persists policy configuration in object fields: filesystem, trash path, and deletion interval. Actual trash contents and checkpoints are filesystem data created under current trash directories. Path-aware trash roots are important for encryption zones and mount tables because a rename into a single global trash directory may be illegal or semantically wrong.

`GlobalStorageStatistics` acts as a process-wide registry of `StorageStatistics` instances. Individual statistics providers can expose mutable counters and reset behavior; the registry API implies global visibility inside a JVM.

`ViewFileSystem` and `ViewFs` keep their mount table in client memory, initialized from `Configuration`. The mount table itself is configuration-derived state, while the target filesystems hold the persistent data. `getChildFileSystems`, `getMountPoints`, delegation token collection, trash-root listing, and close all depend on that mounted-target set.

HA target state is a mixture of configuration and transient transition intent. `HAServiceTarget` exposes addresses and fencing configuration as target metadata and stores a transition-target HA status. Service state itself persists in the remote HA service, while the protocol methods are RPC operations that request transitions or report current state.

## Dependencies and Integration Points

The filesystem API depends heavily on `org.apache.hadoop.conf.Configuration`, `Path`, `FileSystem`, `AbstractFileSystem`, `FileStatus`, `BlockLocation`, `ContentSummary`, `QuotaUsage`, `FsServerDefaults`, `FsStatus`, `RemoteIterator`, `Options.ChecksumOpt`, `CreateFlag`, `Progressable`, and Java IO/NIO classes.

Stream APIs integrate with optional Hadoop capability interfaces: `ByteBufferReadable`, `ByteBufferPositionedReadable`, `HasEnhancedByteBufferAccess`, `CanSetDropBehind`, `CanSetReadahead`, `CanUnbuffer`, `HasFileDescriptor`, `Seekable`, `PositionedReadable`, `Syncable`, and `StreamCapabilities`. The string-based capability model is intentionally open so external filesystems can advertise their own capabilities.

Permission and security integration points include `FsPermission`, `FsAction`, ACL entries/status, `AccessControlException`, `org.apache.hadoop.security.AccessControlException`, and delegation token collection from ViewFS targets. XAttr APIs integrate with shell, HTTP, and JSON display/input paths through `XAttrCodec`.

Local filesystem classes integrate with the host OS filesystem, local file permissions and timestamps, symlink support, checksum side files, local output staging, and platform-specific Windows rename behavior. FTP integration depends on FTP connection configuration keys and remote-server semantics, including restrictions around concurrent streams and same-directory operations.

ViewFS integrates with Hadoop configuration keys under `fs.viewfs.mounttable.*`, `FsConstants`, mount-table utility classes referenced by Javadoc, target filesystems such as HDFS/local/S3-style stores, delegation tokens, trash policy selection, encryption-zone behavior, snapshots, and storage policy APIs.

HA APIs integrate with Hadoop IPC/RPC, protobuf service interfaces, `VersionedProtocol`, `HAServiceProtocolProtos`, `ZKFCProtocolProtos`, `NodeFencer`, ZooKeeper Failover Controller endpoints, service health monitors, fencing scripts or implementations, and access-control enforcement on HA service RPCs.

`org.apache.hadoop.http.lib` package docs integrate with web UI filter initialization through the `hadoop.http.filter.initializers` configuration property.

## Risks and Edge Cases

This is a compatibility surface. Removing or changing public/protected methods, checked exceptions, return types, field constants, deprecation state, or `Writable` field semantics can break downstream Hadoop filesystem implementations, clients, shell tools, and HA controllers.

The chunk starts inside `FilterFileSystem` and ends just after `AbstractMapWritable` begins. A final per-file report must merge adjacent chunks before treating either type as fully covered.

Positioned reads are explicitly expected to be thread-safe and not mutate the current offset, but the docs warn not all filesystems satisfy this. HBase-like consumers can be exposed to subtle data races or position leaks if an implementation routes positioned reads through shared seek/read state without synchronization.

Flush and sync names are easy to misuse. `hflush` is a visibility contract for new readers; `hsync` is closer to fsync but still allows device cache ambiguity. Implementations that advertise `StreamCapabilities.HFLUSH` or `HSYNC` without honoring these differences can mislead durability-sensitive applications.

Builder defaults are compatibility-sensitive. `FSDataOutputStreamBuilder` does not create missing parents unless `recursive()` is selected. `overwrite(false)` must fail on existing files at build time. Optional append support can differ by filesystem.

Path handling has cross-platform traps: URI escaping, scheme/authority stripping, Windows drive prefixes, root detection, parent calculation, and merge semantics. Equality and comparison depend on normalized path representation, so small normalization changes can alter caches and map keys.

Local filesystem behavior depends on platform support for permissions, timestamps, symlinks, and Windows rename corner cases. Raw local operations also bridge Hadoop permission objects to host filesystem modes, which may be lossy.

FTP has blocking and semantic limitations. The API docs state that a create stream must be closed before other FTP APIs are used or calls may block. Append is explicitly unsupported. Rename is constrained by same-directory behavior, and remote status/listing semantics may differ from HDFS-like filesystems.

Trash behavior is risky around symlinks, ViewFS mount points, encryption zones, snapshots, cloud-storage roots, and fallback mounts. Moving to a trash root outside the correct volume can fail, cross encryption-zone boundaries, or put deleted data in an unexpected account/container.

Permission and ACL parsing must preserve stable string forms and effective-permission semantics. `FsPermission` has normal permission bits plus sticky, ACL, and encrypted bits; conversions through short/octal/string forms can lose information if callers choose the wrong method.

XAttr text encoding must distinguish raw text from quoted text, hex, and base64 prefixes. Invalid encodings or mismatched create/replace flags should fail before mutating filesystem metadata.

ViewFS forwards operations to heterogeneous target filesystems. Not every target supports snapshots, xattrs, ACLs, storage policies, symlinks, checksums, truncation, or delegation tokens. Mount resolution must preserve exceptions such as access denied, not found, unresolved links, unsupported filesystems, and parent-not-directory conditions.

HA failover correctness depends on health checks, access control, fencing configuration, fencing parameter construction, and RPC exception unwrapping. A false positive fencing result can leave split-brain risk; a false negative can block availability. Observer transitions add another state path that older services or targets may not support.

## Test Signals

Useful validation for this chunk includes:

- JDiff/API compatibility checks comparing Hadoop Common public signatures, deprecation tags, fields, and exceptions against the 2.10.2 baseline.
- Serialization round-trip tests for `FsServerDefaults`, `FsStatus`, and `FsPermission`, including old/new constructor combinations and optional storage policy/key provider fields.
- Stream contract tests for seek/getPos, positioned reads that preserve current offset, `readFully` EOF behavior, `ByteBuffer` and enhanced buffer reads, `releaseBuffer`, `unbuffer`, readahead/drop-behind hints, and capability strings.
- Output stream tests for builder option propagation, recursive parent creation, overwrite false failures, append support/unsupported behavior, checksum options, progress callbacks, `hflush`, `hsync`, `sync`, close, position tracking, and advertised capabilities.
- `Path` tests for URI construction, parent/child resolution, scheme/authority stripping, `mergePaths`, Windows absolute detection, root/name/parent/suffix behavior, equality, ordering, depth, and filesystem resolution from configuration.
- Local filesystem tests for raw path conversion, checksum layering, copy to/from local, checksum failure reporting, owner/permission/time mutation, symlink create/status/target, truncate, Windows rename cases, local output staging, and close behavior.
- Quota and storage tests for `QuotaUsage` formatting, human-readable output, per-storage-type quota/consumption, storage type parsing, movable/quota-supporting type lists, and global statistics registry put/get/reset/iteration.
- Permission tests for `FsAction` implication/and/or/not, `FsPermission` short/octal/string conversion, umask application and configuration, sticky/ACL/encrypted bits, ACL spec parsing, stable ACL strings, `AclStatus.getEffectivePermission`, and access-control exception propagation.
- XAttr tests for text, quoted text, hex, and base64 encode/decode paths; invalid input; and create/replace validation when an xattr exists or does not exist.
- Trash tests for disabled trash, already-in-trash paths, checkpoint and expunge, configured policy factory selection, old and new initialization paths, path-aware trash roots, encryption-zone paths, snapshots, symlinks, ViewFS mount points, fallback mounts, and all-users trash-root listing.
- FTP filesystem tests for configuration-derived connection details, open/create/delete/list/status/mkdir/rename/working-directory behavior, unsupported append, same-directory rename constraints, and the requirement to close create streams before invoking other APIs.
- ViewFS tests for mount-table initialization from default and authority-specific configuration, link resolution, fallback paths, child filesystem and mount point listing, operation forwarding across heterogeneous targets, delegation token aggregation, trash roots inside mount points, ACL/xattr/snapshot/storage-policy forwarding, and exception preservation.
- HA tests for health monitoring, state transitions to active/standby/observer, status lookup, access denial, service failure propagation, helper unwrapping of remote exceptions, fencing preflight validation, ordered fencing method attempts, fencing parameter maps, separate health monitor addresses, ZKFC proxy creation, auto-failover flags, and Observer support flags.

## Cross-Chunk Notes

The preceding chunk is needed for the beginning of `FilterFileSystem`, including the class declaration and methods before `completeLocalOutput`. The following chunk is needed for the body of `org.apache.hadoop.io.AbstractMapWritable` and the rest of the `org.apache.hadoop.io` package.

This document intentionally stays at the chunk level. It should be merged with the other chunks for `Apache_Hadoop_Common_2.10.2.xml` before any final per-file report draws conclusions about the full JDiff baseline.
