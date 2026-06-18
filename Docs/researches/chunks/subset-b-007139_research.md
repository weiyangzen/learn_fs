# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 12074-17935

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.10.0. It starts in the middle of `org.apache.hadoop.fs.FilterFileSystem`, covers a broad section of public Hadoop filesystem APIs, permissions, ViewFs, high-availability protocols, protocol-buffer RPC facades, the `org.apache.hadoop.http.lib` package note, and ends partway through `org.apache.hadoop.io.ArrayPrimitiveWritable`.

Because the source is generated API metadata rather than implementation code, the useful research surface is the public contract: exported classes, interfaces, constructors, methods, fields, exceptions, and documentation comments. Implementation details must be recovered from the corresponding Java sources in later lanes if needed.

## Purpose

The chunk records the stable Hadoop Common API surface for filesystem access and related services. It documents how clients create/read/write files, address paths, query filesystem status and statistics, handle permissions/ACLs/xattrs, use local/FTP/ViewFs filesystems, move files through trash, and control HA services through RPC-compatible protocols.

The JDiff file is likely used by Hadoop release tooling to compare public APIs across versions. As such, changes in this chunk are compatibility signals: new or removed methods, changed signatures, changed exceptions, or modified visibility/deprecation metadata can affect downstream Hadoop applications and filesystem implementations.

## Important APIs, Types, and Functions

### `org.apache.hadoop.fs` filesystem contracts

- `FilterFileSystem` delegates the remaining listed methods to an underlying protected `FileSystem fs`, optionally rewriting the scheme through `swapScheme`. The visible API includes usage/default queries, file status, access checks, symlink operations, checksum toggles, owner/time/permission updates, primitive create/mkdir hooks, child filesystems, snapshots, ACLs, xattrs, storage policies, trash roots, and builder-style `createFile`/`appendFile`.
- `FsConstants` exposes core URI and scheme constants such as local filesystem URI, FTP scheme, ViewFs URI/scheme, and maximum symlink traversal count.
- `FSDataInputStream` wraps an `InputStream` with `Seekable`, `PositionedReadable`, byte-buffer reads, readahead/drop-behind controls, buffer release, unbuffering, file descriptor access, stream capability probing, and position-aware reads.
- `FSDataOutputStream` wraps an `OutputStream` with position reporting, sync/hflush/hsync, drop-behind, capability probing, and close behavior.
- `FSDataOutputStreamBuilder` is the fluent construction API for create/append output streams. It carries target `FileSystem`, `Path`, permission, buffer size, replication, block size, recursive parent creation, progress callback, create/overwrite/append flags, checksum options, and final `build()`.
- `FSInputStream`, `Seekable`, and `PositionedReadable` define random-access stream semantics: seek, current position, alternate source seeking, positional reads, and full-read loops.
- `FsServerDefaults`, `FsStatus`, `StorageStatistics`, `GlobalStorageStatistics`, `StorageType`, and `QuotaUsage` expose server defaults, capacity/used/remaining statistics, process-wide storage statistics, storage media classes, and namespace/storage quota accounting.
- `Path` is the central URI-like path value type with string/URI/component constructors, scheme/authority stripping, path merging, Windows absolute-path detection, filesystem resolution, absolute/root/name/parent/suffix/depth helpers, qualification, equality, hashing, comparison, and separator constants.
- `PathFilter` and `GlobFilter` provide path inclusion predicates, with glob filtering supporting POSIX-style glob patterns and brace expansion.
- `StreamCapabilities` and `StreamCapabilitiesPolicy` define string-named stream features including `hflush`, `hsync`, `in:readahead`, `dropbehind`, `unbuffer`, byte-buffer reads, and positional byte-buffer reads.
- `Syncable` defines the flush/sync contract: legacy `sync`, `hflush`, and `hsync`.
- `Trash` and `TrashPolicy` expose pluggable trash behavior: moving to appropriate trash roots, checking enablement, checkpoints, expunge, current trash directory, and superuser emptier runnable.
- `XAttrCodec` and `XAttrSetFlag` support xattr value encoding/decoding and validation of create/replace flag sets.

### Local, FTP, and ViewFs implementations

- `LocalFileSystem` is the checksum local filesystem wrapper. Its API exposes initialization, scheme, raw filesystem access, path-to-file conversion, local copy operations, checksum failure reporting, and symlink delegation/status.
- `RawLocalFileSystem` implements the raw local filesystem API: URI initialization, open/append/create variants, non-recursive creates, renames, Windows empty-directory handling, truncate/delete/list/mkdirs, working and home directories, local-output staging, close, file status, owner/permission/time updates, and symlink status/target operations.
- `FTPFileSystem` exposes a remote FTP-backed `FileSystem` with configurable user/password/host/port/data connection/transfer mode keys. It supports open, create, delete, list/status, mkdirs, rename, working/home directories, and documents that append is unsupported and FTP streams must be closed before other API calls.
- `ViewFileSystem` implements the `FileSystem`-style client-side mount table. It resolves incoming paths to target filesystems and forwards append/create/delete/list/open/rename/truncate/block-location/checksum/status/access/ACL/xattr/default/snapshot calls.
- `ViewFs` implements the `AbstractFileSystem`-style client-side mount table. It has parallel forwarding APIs for create/delete/block locations/checksum/status/access/list/mkdir/open/truncate/rename/symlink/owner/permission/replication/times/ACL/xattr/snapshot/storage-policy operations and adds delegation-token aggregation and name validation.
- `NotInMountpointException` marks operations that cannot be performed because a path is not inside a mount point.

### Permissions, ACLs, and security-related types

- `org.apache.hadoop.fs.permission.AccessControlException` is retained as a deprecated compatibility exception; the docs direct users to `org.apache.hadoop.security.AccessControlException`.
- `AclEntry` models one ACL entry with type, optional name, permission, scope, stable string conversion, parsing of ACL specs/entries, and list-to-string conversion.
- `AclEntryScope` and `AclEntryType` are enums for ACL scope and entry type; `AclEntryType` includes stable string output.
- `AclStatus` is immutable ACL status for a path, exposing owner, group, sticky bit, ordered entries, base `FsPermission`, and effective permission computation.
- `FsAction` models read/write/execute combinations with `implies`, `and`, `or`, `not`, string lookup, and symbolic representation.
- `FsPermission` models Unix-style file/directory permissions, sticky/ACL/encryption bits, string and short encodings, `Writable` serialization, umask application, configuration-backed umask get/set, defaults for directories/files/cache pools, and parsing from Unix symbolic strings.

### High availability and RPC protocol metadata

- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` are HA-specific `IOException` subclasses for fencing, failover, health, and state-transition failures.
- `FenceMethod` defines HA fencing plugins with `checkArgs(String)` and `tryFence(HAServiceTarget, String)`.
- `HAServiceProtocol` defines monitor and state transition RPCs: `monitorHealth`, `transitionToActive`, `transitionToStandby`, `transitionToObserver`, and `getServiceStatus`. Its methods raise service-failure, access-control, health-check, and generic IO exceptions as appropriate.
- `HAServiceProtocolHelper` provides static wrappers around the HA protocol calls and documents that it unwraps `RemoteException` into specific exceptions.
- `HAServiceTarget` represents an HA admin target. It exposes service, health-monitor, and ZKFC addresses; fencing configuration and fencer access; HA and ZKFC proxy construction; fencing parameter injection; auto-failover status; and Observer-state support.
- `HAServiceProtocolPB` and `ZKFCProtocolPB` are PB RPC facades implementing generated protobuf blocking interfaces plus Hadoop `VersionedProtocol`.

### `org.apache.hadoop.io` start

- `AbstractMapWritable` is the base class for `MapWritable` and `SortedMapWritable`. It maintains per-instance class-id mappings rather than static maps, supports synchronized addition/copy, exposes class/id lookups, carries a `Configuration`, and serializes/deserializes those mappings through `Writable`.
- `ArrayFile` is a `MapFile` specialization for dense integer-to-value mappings.
- The chunk begins `ArrayPrimitiveWritable`, showing constructors for empty read-time instances, known primitive component type, and object-backed construction. Its complete API continues after this chunk.

## Control Flow

The file does not contain executable control-flow bodies, but the API contracts imply several recurring flows.

Filesystem read flow starts with a `Path`, resolves a `FileSystem` or `AbstractFileSystem`, opens an `FSDataInputStream`, and then uses sequential reads, positioned reads, seek/getPos, byte-buffer reads, optional readahead/drop-behind hints, and stream capability checks. Implementations may redirect the request through wrappers such as `FilterFileSystem`, checksum-aware `LocalFileSystem`, raw local IO, FTP, or ViewFs mount resolution.

Filesystem write flow uses either direct create/append overloads or `FSDataOutputStreamBuilder`. Builder state accumulates permissions, buffer size, replication, block size, progress callbacks, parent creation, create/overwrite/append flags, and checksum options before `build()` asks the target filesystem to create or append. Output streams then expose position, close, hflush/hsync/sync, drop-behind, and capability checks.

Metadata flow is path-driven. Status, content/quota usage, ACL, xattr, storage policy, checksum, block locations, permissions, ownership, and timestamp operations all accept `Path` and may raise `IOException` or more precise access/not-found/unsupported exceptions. `FilterFileSystem`, `ViewFileSystem`, and `ViewFs` act as forwarding layers that preserve these contracts while delegating to the target filesystem.

ViewFs flow is client-side mount resolution. Configuration entries under `fs.viewfs.mounttable.*` define links from a view namespace to one or more backing filesystems. `resolvePath` maps a view path to a target path, then the operation is executed on the backing filesystem. The docs note in-memory client-side state and describe merge mounts, while also noting merge mounts are not implemented in this documented version.

Permission flow uses `FsAction` and `FsPermission` for mode bits and `AclEntry`/`AclStatus` for extended ACL semantics. ACL text is parsed into entries, entries are converted to stable strings, and effective permissions can be computed from ACL status plus optional mode bits.

Trash flow constructs a configured `TrashPolicy`, tests whether trash is enabled, resolves an appropriate trash directory for the path/filesystem, moves entries to trash, and optionally creates/deletes checkpoints or returns a periodic emptier runnable.

HA admin flow operates through `HAServiceTarget` and `HAServiceProtocol`. Admin code builds proxies to a target service, optional health-monitor endpoint, or ZKFC; monitors health; requests state transitions; checks current status; and invokes configured fencing methods during failover. Helper methods wrap RPC calls and translate remote exceptions.

`AbstractMapWritable` serialization flow records per-instance class-to-byte and byte-to-class mappings, writes them through `Writable`, and reconstructs them during `readFields` so nested `MapWritable` values can carry their own dynamic class tables.

## State and Persistence Behavior

The JDiff XML itself is a persisted API artifact. It preserves the release's public type signatures, deprecation state, visibility, thrown exceptions, and doc comments for compatibility checking.

Runtime state described by the APIs is mostly held by implementations:

- `FilterFileSystem` stores the wrapped `FileSystem` and optional scheme swap.
- Stream classes hold wrapped input/output streams and maintain logical positions; they may also propagate read-ahead, drop-behind, unbuffer, and sync behavior to the underlying stream if supported.
- Builder instances hold pending create/append options until `build()`.
- `Path`, `FsStatus`, `FsServerDefaults`, `LocatedFileStatus`, `QuotaUsage`, ACL entries/statuses, and permissions are value objects used in client and server metadata exchange.
- `GlobalStorageStatistics` stores process-wide named `StorageStatistics` instances and can reset them.
- `StorageStatistics` instances hold filesystem or `FileContext` counters and expose long-statistic iteration.
- `TrashPolicy` holds the selected `FileSystem`, trash path, and deletion interval; concrete policies perform persistence by moving files and writing checkpoints in the filesystem namespace.
- `ViewFileSystem`/`ViewFs` maintain an in-memory client-side mount table initialized from configuration and delegate persistence to target filesystems.
- `FTPFileSystem` keeps connection/configuration state for a remote FTP endpoint. The docs warn that open FTP streams block other API calls until closed.
- `FsPermission` implements `Writable`, so permission state is persisted over Hadoop binary serialization and encoded as shorts/octal strings.
- `AbstractMapWritable` persists dynamic class-id mappings in the serialized `Writable` payload.

## Dependencies and Integration Points

This API surface integrates with the rest of Hadoop Common:

- Core configuration through `org.apache.hadoop.conf.Configuration`, especially filesystem defaults, umask, FTP settings, and ViewFs mount-table entries.
- Filesystem value and service types such as `Path`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `ContentSummary`, `QuotaUsage`, `FsStatus`, `FileChecksum`, `BlockStoragePolicySpi`, `FsServerDefaults`, and `RemoteIterator`.
- Permission and security packages: `org.apache.hadoop.fs.permission.*` and `org.apache.hadoop.security.AccessControlException`.
- IO abstractions and serialization: Java `InputStream`/`OutputStream`/`DataInput`/`DataOutput`, Hadoop `Writable`, and `Configurable`.
- Stream feature interfaces such as `CanSetReadahead`, `CanSetDropBehind`, `CanUnbuffer`, byte-buffer read interfaces, and sync interfaces referenced by capability names.
- Local platform behavior via `RawLocalFileSystem`, Java `File`, file descriptors, chmod/chown command behavior, symlink support, and Windows path/rename handling.
- Remote filesystem behavior through FTP configuration keys and Apache Commons Net style FTP concepts implied by data connection and transfer modes.
- ViewFs mount table utilities and constants referenced by docs: `FsConstants`, `Constants`, and `ConfigUtil`.
- HA management modules: `NodeFencer`, `ZKFCProtocol`, `HAServiceStatus`, `HAServiceProtocol.StateChangeRequestInfo`, protobuf-generated service interfaces, and Hadoop IPC `VersionedProtocol`.
- HTTP UI filter integration via package documentation for `hadoop.http.filter.initializers`, including `StaticUserWebFilter`.

## Risks and Edge Cases

- This is generated API metadata, not source implementation. It can identify public contracts but cannot prove forwarding correctness, locking, validation, resource cleanup, or exception ordering.
- The chunk starts and ends mid-class. `FilterFileSystem` methods before line 12074 and most of `ArrayPrimitiveWritable` after line 17935 must be merged from adjacent chunks for a complete per-file report.
- `FilterFileSystem`, `LocalFileSystem`, `RawLocalFileSystem`, `ViewFileSystem`, and `ViewFs` all expose similar operations; compatibility depends on wrappers preserving semantics and exceptions of the delegated filesystem.
- Symlink handling spans support detection, create, link status, link target, and resolution. Implementations that partially support symlinks can diverge in `getFileStatus` versus `getFileLinkStatus` behavior.
- Positioned reads and seekable streams have strict argument validation and end-of-file behavior. The API exposes both partial reads and `readFully`, so callers and implementations must not conflate them.
- Byte-buffer read and unbuffer capabilities are optional. Callers must use `hasCapability` or tolerate unsupported behavior.
- `FSDataOutputStreamBuilder` has interacting create/overwrite/append flags; invalid flag combinations or missing parent behavior are likely compatibility-sensitive.
- FTP streams are explicitly serialized by connection behavior: a stream must be closed before other APIs or calls can block. This is a major operational risk for code that treats FTP like a normal concurrent filesystem.
- `RawLocalFileSystem` exposes platform-specific behavior, including Windows absolute paths, Windows empty-directory rename handling, local chmod/chown/timestamp commands, and local symlink behavior.
- ViewFs mount tables are client-side and configuration-driven. Bad link configuration, operations outside mount points, unimplemented merge mounts, and cross-filesystem rename/delete semantics are important edge cases.
- ACL and permission string conversion has both regular and stable forms. Tests need to ensure stable strings do not change across releases, because downstream tools may persist or compare them.
- `FsPermission.getUMask` still documents deprecated umask-key compatibility and decimal interpretation; config migration can produce subtle permission changes.
- XAttr encoding/decoding depends on selected `XAttrCodec` and shell/XML string representations; invalid encodings and create/replace flag validation need explicit coverage.
- HA transition APIs are no-ops if already in the target state, but failures can arise from service state, access control, health checks, or IO/RPC failures. Admin tools must distinguish these exception classes.
- `HAServiceTarget.getHealthMonitorAddress()` can split health RPCs from the main service RPC address. Incorrect target implementations can silently put health checks back on the overloaded main RPC path.
- `AbstractMapWritable` limits class ids to 1..127 per instance; maps with too many distinct `Writable` classes or inconsistent class tables are serialization risks.

## Test Signals

Useful tests for this chunk should focus on API contract compatibility and representative implementation behavior:

- JDiff/API compatibility checks that compare method signatures, exceptions, visibility, deprecation tags, constructors, and public/protected fields against expected Hadoop 2.10.0 output.
- `FSDataInputStream` and `FSInputStream` tests for seek/getPos, positional reads, `readFully`, EOF behavior, invalid read arguments, byte-buffer reads, alternate source seeking, unbuffering, and capability names.
- `FSDataOutputStream` and builder tests for create, overwrite, append, recursive parent creation, permission/buffer/replication/block-size/checksum propagation, hflush/hsync/sync, close, and drop-behind.
- Local and raw local filesystem tests for path-to-file conversion, checksum failure reporting, symlink status/target, owner/permission/time updates, mkdirs/delete/truncate/rename, working directory, and Windows-specific path/rename behavior.
- FTP filesystem tests for configuration-derived authority/user/password/port, open/create/delete/list/status/mkdir/rename, unsupported append, and enforcement that unclosed streams block or prevent subsequent FTP operations.
- ViewFs and ViewFileSystem tests for mount-table initialization, default and authority-specific tables, path resolution, operations through mount points, operations outside mount points, child filesystem listing, delegation-token aggregation, and documented non-support for merge mounts.
- Permission tests for `FsAction` algebra, `FsPermission` short/octal/symbolic encodings, sticky/ACL/encrypted bits, umask configuration including deprecated keys, `Writable` round trips, and default permissions.
- ACL tests for parsing ACL specs and entries, stable string conversion, ACL status immutability/order, and effective-permission computation with and without explicit permission arguments.
- XAttr tests for text/hex/base64 encode/decode paths, invalid encodings, list/get/set/remove operations through filesystem wrappers, and `XAttrSetFlag.validate` create/replace behavior.
- Trash tests for appropriate trash root resolution across symlinks or mount points, disabled trash, already-in-trash paths, checkpoint creation/deletion, current trash directory lookup, and superuser emptier scheduling.
- Storage/quota/statistics tests for `FsStatus` writable round trips, global statistics put/get/reset/iteration, storage type parsing/movable/quota-support lists, and quota string/header formatting.
- HA tests for monitor health, active/standby/observer transitions, status retrieval, helper unwrapping of remote exceptions, fencing argument validation, fencing parameter injection, health-monitor address selection, ZKFC proxy creation, auto-failover flags, and Observer support.
- `AbstractMapWritable` tests for per-instance class map serialization, nested `MapWritable`, copy constructors, id/class lookup, configuration propagation, and failure around the 127-class limit.
