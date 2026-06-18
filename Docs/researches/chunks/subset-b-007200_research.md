# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.4.xml lines 12096-18157

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.2.4. It starts inside the tail of `org.apache.hadoop.fs.FileUtil`, covers a broad run of `org.apache.hadoop.fs` public and protected APIs, includes the FTP filesystem package, the core `org.apache.hadoop.ha` high-availability interfaces, protocol-buffer bridge interfaces for HA/ZKFC RPC, and the beginning of `org.apache.hadoop.io` through the opening constructor of `DefaultStringifier`.

The source is generated compatibility metadata rather than implementation source. The relevant research surface is the release API contract: type names, inheritance, implemented interfaces, method signatures, checked exceptions, visibility, abstract/final/static attributes, deprecation markers, public/protected fields, and embedded Javadocs. Exact algorithms, private fields, and private helper flow must be validated in Java sources when implementation-level detail is required.

## Purpose

The `org.apache.hadoop.fs` portion defines Hadoop Common's filesystem abstraction boundary. It includes utility helpers (`FileUtil` tail), filesystem wrappers (`FilterFileSystem`), URI and scheme constants (`FsConstants`), stream contracts (`FSDataInputStream`, `FSDataOutputStream`, `FSInputStream`, `Seekable`, `PositionedReadable`, `Syncable`, `StreamCapabilities`), builder-style file creation (`FSDataOutputStreamBuilder`), path modeling (`Path`, `PathFilter`, `PathHandle`), local filesystem implementations (`LocalFileSystem`, `RawLocalFileSystem`), quota and storage accounting (`QuotaUsage`, `FsStatus`, `FsServerDefaults`, `StorageStatistics`, `GlobalStorageStatistics`, `StorageType`), trash policy plumbing, xattr conversion, and multipart upload handle types.

The `org.apache.hadoop.fs.ftp` portion exposes an FTP-backed `FileSystem` implementation built around Apache Commons Net. It maps Hadoop `FileSystem` operations onto FTP concepts and documents important limitations such as single-stream blocking and unsupported append.

The `org.apache.hadoop.ha` portion defines client-side and service-side contracts for Hadoop high availability. It covers health monitoring, state transitions to active/standby/observer, fencing method configuration and execution, HA target metadata, helper wrappers for RPC exception unwrapping, and typed exceptions for fencing, failover, health, and service transition failures.

The `org.apache.hadoop.io` portion starts the Writable ecosystem in this file segment. It documents map type registration support, writable arrays and primitive arrays, binary comparison, simple writable scalar types, byte-buffer pooling, compressed writable lazy inflation, and a `DataOutput` to `OutputStream` adapter.

## Important APIs, Types, and Functions

### File Utilities and Filesystem Wrappers

- `FileUtil` tail includes `createLocalTempFile(File, String, boolean)`, `replaceFile(File, File)`, checked wrappers for `File.listFiles()` and `File.list()`, `createJarWithClassPath(...)`, `getJarsInDirectory(...)`, `compareFs(FileSystem, FileSystem)`, and multiple `write(...)` overloads for `FileSystem` and `FileContext`. The write helpers cover raw `byte[]`, line iterables with explicit `Charset`, a single `CharSequence` with explicit charset, and UTF-8 defaults.
- `FileUtil.SYMLINK_NO_PRIVILEGE` remains public, indicating Windows or platform-specific symlink failure reporting is part of the API.
- `FilterFileSystem` extends `FileSystem` and delegates almost the whole filesystem surface to a wrapped `FileSystem` stored in protected field `fs`. It exposes constructors with and without a raw filesystem, `getRawFileSystem()`, URI/canonicalization hooks, path qualification/checking, open/create/append/concat/delete/rename/truncate/list/mkdir/status methods, local copy helpers, checksum toggles, symlink APIs, snapshots, ACLs, xattrs, storage policies, trash roots, builder factories, and `hasPathCapability`.
- `FilterFileSystem.swapScheme` is a protected field used by wrapper implementations that need to present a different scheme from the underlying filesystem.

### Core Filesystem Streams and Builders

- `FSDataInputStream` extends `DataInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `CanUnbuffer`, and `StreamCapabilities`. It exposes seeking, position reporting, positional `read` and `readFully`, source switching, byte-buffer reads via `ByteBufferPool`, buffer release, unbuffering, capability checks, file descriptor access, and readahead/drop-behind controls.
- `FSInputStream` is the lower-level abstract seekable positioned input stream. It declares `seek`, `getPos`, and `seekToNewSource`, provides positioned `read` and `readFully` helpers, and includes `validatePositionedReadArgs`.
- `FSDataOutputStream` extends `DataOutputStream` and implements `Syncable`, `CanSetDropBehind`, and `StreamCapabilities`. Constructors accept an `OutputStream`, filesystem statistics, and optional start position. Public methods expose `getPos`, `close`, `hflush`, `hsync`, drop-behind, capability checks, and `toString`.
- `FSDataOutputStreamBuilder<B,S>` is a fluent builder around file creation and append. It carries a `FileSystem`, `Path`, permission, buffer size, replication, block size, recursive flag, progress callback, create/overwrite/append flags, checksum options, optional and mandatory named options, and `build()` returning the stream type. Its `opt` and `must` overloads accept booleans, ints, floats, doubles, strings, and string arrays, so filesystem-specific options can be preserved as typed configuration keys and mandatory-key sets.
- `Syncable` defines `hflush()` and `hsync()` semantics. `StreamCapabilities` defines string capability names for `hflush`, `hsync`, `in:readahead`, `dropbehind`, and `in:unbuffer`. `StreamCapabilitiesPolicy.unbuffer(InputStream)` centralizes optional unbuffer dispatch and exposes a standard not-implemented message.

### Path, Handles, Status, and Filters

- `Path` models filesystem names as URI-like slash-separated paths. Constructors cover string parent/child combinations, `Path` parent/child combinations, raw strings, `URI`, and explicit scheme/authority/path triples. Static helpers strip scheme/authority, merge paths while preserving the first path scheme and authority, and detect Windows absolute paths.
- `Path` instance APIs expose URI conversion, filesystem resolution from `Configuration`, absolute/root/name/parent/depth queries, suffixing, string/equality/hash/ordering behavior, deprecated `makeQualified(FileSystem)`, and `validateObject()` to reject invalid deserialized paths. Public constants include `SEPARATOR`, `SEPARATOR_CHAR`, `CUR_DIR`, and host `WINDOWS`.
- `PathFilter.accept(Path)` is the simple predicate extension point used by listing/glob APIs. `GlobFilter` implements this contract using POSIX glob patterns with brace expansion and can compose a user filter.
- `PathHandle`, `PartHandle`, and `UploadHandle` are opaque serializable handle interfaces. Each exposes default `toByteArray()`, abstract `bytes()` returning a `ByteBuffer`, and `equals(Object)`. `PathHandle` references filesystem entities with optional validation metadata, while `PartHandle` and `UploadHandle` identify multipart upload parts and upload IDs.
- `InvalidPathException`, `InvalidPathHandleException`, and `ParentNotDirectoryException` define path-specific failures. `InvalidPathHandleException` is tied to path-handle constraints failing after filesystem mutation.
- `LocatedFileStatus` extends `FileStatus` with block locations. Constructors cover wrapping an existing status, explicit status fields, ACL/encryption/erasure-coded booleans, or generic `FileStatus.AttrFlags`. It exposes `getBlockLocations`, protected lazy `setBlockLocations`, and path-based comparison/equality/hash behavior.
- `Options` is a final grouping class for filesystem operation options. Nested option types are outside this chunk, but APIs in this segment reference `Options.HandleOpt` and `Options.ChecksumOpt`.

### Local, Raw Local, and FTP Filesystems

- `LocalFileSystem` extends `ChecksumFileSystem` and wraps a raw local filesystem. It exposes scheme `file`, `getRaw`, `pathToFile`, copy-to/from-local operations, checksum-failure quarantine via `reportChecksumFailure`, and symlink APIs.
- `RawLocalFileSystem` extends `FileSystem` and maps Hadoop paths directly to `java.io.File`. It exposes path conversion, URI initialization, open by path or `PathHandle`, append, create and non-recursive create variants, protected output-stream construction with permissions, concat, rename, truncate, delete, unsorted `listStatus`, mkdir helpers, working directory/home directory state, status, local-output staging, owner/permission/time mutation through platform commands, path handles, symlinks, and path capability checks.
- `ReadOption` is an enum marker for read behavior. `Seekable` defines `seek(long)` and `getPos()`.
- `FTPFileSystem` extends `FileSystem` with scheme `ftp`. It has initialization from URI/configuration, default port lookup, open/create/delete/list/status/mkdir/rename/working-directory/home-directory APIs, and config constants for user, host, port, password, data connection mode, and transfer mode. The create Javadoc warns that the returned stream must be closed before using other APIs or calls can block; append is documented as unsupported.
- `FTPException` wraps lower-level failures in an unchecked runtime exception.

### Capacity, Quota, Storage, and Trash

- `FsServerDefaults` is a `Writable` carrying default block size, checksum bytes, write packet size, replication, file buffer size, encryption-transfer flag, trash interval, checksum type, key provider URI, and default storage policy ID.
- `FsStatus` is a `Writable` with capacity, used, and remaining bytes.
- `QuotaUsage` stores namespace and space quota consumption plus per-`StorageType` quota/consumption. It has protected constructors/mutators for builder use, public getters, type-quota availability checks, equality/hash, formatted headers, human-readable and storage-type-aware string output, and protected formatting helpers.
- `GlobalStorageStatistics` is an enum singleton-style registry exposing `get(String)`, `put(String, StorageStatistics)`, `reset()`, and iteration over registered `StorageStatistics`.
- `StorageStatistics` is an abstract named statistics source with `getScheme`, iterator over long statistics, `getLong(String)`, `isTracked(String)`, and `reset`.
- `StorageType` is an enum with helper classification methods for transience, quota support, movability, list views, parser overloads, and public `DEFAULT` and `EMPTY_ARRAY` fields.
- `Trash` is a configured facade over `TrashPolicy`. It can move paths to the appropriate trash, check enablement, create checkpoints, expunge old or all checkpoints, return a superuser emptier `Runnable`, and resolve current trash directories per path.
- `TrashPolicy` is the abstract policy extension point. It supports deprecated home-directory initialization and newer initialization that avoids assuming `/user/$USER`, specifically to handle encryption-zone rename constraints. It defines enablement, move-to-trash, checkpoint create/delete, immediate delete, per-path trash directory resolution, emptier creation, factory methods keyed by `fs.trash.classname`, and protected state `fs`, `trash`, and `deletionInterval`.

### XAttrs and Unsupported Features

- `XAttrCodec` encodes and decodes xattr byte values for shell, HTTP, and JSON presentation. `decodeValue(String)` recognizes hex prefixes `0x`/`0X`, base64 prefixes `0s`/`0S`, quoted text, and unquoted text. `encodeValue(byte[], XAttrCodec)` emits quoted text, hex, or base64.
- `XAttrSetFlag.validate(String, boolean, EnumSet)` enforces create/replace semantics for xattr updates.
- `UnsupportedFileSystemException` and `UnsupportedMultipartUploaderException` are checked `IOException` subclasses used when a scheme lacks a filesystem or multipart uploader implementation.

### High Availability APIs

- `FenceMethod` defines operator-configured fencing implementations. `checkArgs(String)` validates configured arguments at startup, and `tryFence(HAServiceTarget, String)` attempts to stop another node from making progress, returning a boolean and allowing runtime configuration failure.
- `HAServiceProtocol` defines `monitorHealth`, `transitionToActive`, `transitionToStandby`, `transitionToObserver`, and `getServiceStatus`. Methods can throw service-specific failures, access control failures, and `IOException`. Public `versionID` documents the initial protocol version.
- `HAServiceProtocolHelper` wraps HA RPC calls and unwraps `RemoteException` into more specific exceptions for monitor and state transition operations.
- `HAServiceTarget` represents a target for HA admin commands. It supplies IPC address, optional health-monitor address, ZKFC address, fencer, preflight fencing validation, HA/ZKFC proxies with timeouts, desired transition target state, fencing parameters, auto-failover flag, and observer support flag. `addFencingParameters(Map)` documents how shell fencing receives entries as environment variables prefixed with `target_`.
- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` encode failure categories for HA control paths.
- `HAServiceProtocolPB` and `ZKFCProtocolPB` are protocol-buffer bridge interfaces that extend generated blocking service interfaces and `VersionedProtocol`, making protobuf RPC services part of the public compatibility surface.

### Writable and IO Types

- `AbstractMapWritable` implements `Writable` and `Configurable`, maintaining a class-to-byte-id registry for map-like writables. APIs include protected `addToMap(Class, byte)`, `getClass(byte)`, `getId(Class)`, `copy(Writable)`, configuration getters/setters, and serialization hooks.
- `ArrayFile` extends `MapFile`; this chunk only shows its constructor.
- `ArrayPrimitiveWritable` stores Java primitive arrays as a `Writable`, with constructors for no-arg read, declared component type, or initial array. It exposes the stored array, actual and declared component types, declared-type checks, mutation, and serialization.
- `ArrayWritable` stores arrays of `Writable` values with a declared value class. It exposes `getValueClass`, `toStrings`, `toArray`, `set`, `get`, and serialization.
- `BinaryComparable` is a base comparable over byte sequences. Subclasses provide `getLength` and `getBytes`; the class supplies byte-wise `compareTo`, equality, and hash behavior.
- `BloomMapFile` appears as a namespace class with public constants `BLOOM_FILE_NAME` and `HASH_COUNT`, plus a static `delete(FileSystem, String)` helper.
- `BooleanWritable`, `ByteWritable`, and `BytesWritable` are `WritableComparable` implementations for boolean, byte, and byte-array data. The scalar types expose constructors, set/get, read/write, equality/hash, comparison, and string conversion. `BytesWritable` extends `BinaryComparable`, distinguishes logical length from capacity, exposes backing-array and exact-copy access, deprecated `get()`/`getSize()` aliases, resizing and capacity changes, range-copy mutation, serialization, equality/hash, and hex string rendering.
- `ByteBufferPool` defines direct-buffer lifecycle methods `getBuffer(boolean direct, int length)` and `putBuffer(ByteBuffer)`.
- `org.apache.hadoop.io.Closeable` is deprecated in favor of `java.io.Closeable`.
- `CompressedWritable` is an abstract `Writable` base that stores compressed serialized bytes and lazily inflates fields. Final `readFields` and `write` wrap abstract protected `readFieldsCompressed` and `writeCompressed`; subclasses must call `ensureInflated()` before field access.
- `DataOutputOutputStream.constructOutputStream(DataOutput)` returns the original object if it is already an `OutputStream`, otherwise wraps a `DataOutput`. The adapter exposes `write(int)`, `write(byte[], int, int)`, and `write(byte[])`.
- The chunk ends at the beginning of `DefaultStringifier`, showing that it implements `Stringifier` and has a constructor taking `Configuration` and `Class`; the rest of that class is outside this range.

## Control Flow

The XML has no runtime control flow, but the API contracts imply several important execution paths.

Filesystem calls often flow from high-level `FileSystem` clients through wrappers. `FilterFileSystem` receives operations, applies wrapper path/URI behavior such as `swapScheme` or canonicalization, and delegates to its raw filesystem. Subclasses can override individual operations while leaving the rest of the surface delegated.

Stream reads flow through `FSDataInputStream` to an underlying stream that may implement optional interfaces. Seek and positioned reads are part of the stable contract; byte-buffer reads use `ByteBufferPool` and require explicit `releaseBuffer`; `unbuffer()` routes through capability policy so implementations that support releasing OS/socket buffers can do so without every caller hard-coding concrete stream types.

File creation flows through direct `FileSystem.create` overloads or through `FSDataOutputStreamBuilder`. Builder calls accumulate flags, permissions, buffering, replication, block sizing, checksums, progress callbacks, and optional/mandatory implementation-specific options. `build()` is the point where the configured filesystem interprets these settings and returns an output stream.

Path resolution flows from raw strings or URIs into normalized `Path` values, then into `getFileSystem(Configuration)` for scheme resolution. `PathHandle`-based reads add an extra validation flow: the handle bytes encode constraints, and opening with a stale or mismatched handle can raise `InvalidPathHandleException`.

Trash operations flow through `Trash` into a configured `TrashPolicy`. The newer policy methods take a deleted path when resolving the trash directory, which is important when HDFS encryption zones prevent rename across zone boundaries. Checkpoint and expunge APIs separate current trash movement from old-checkpoint cleanup.

HA control flow is health-monitor driven. A framework calls `monitorHealth`; unhealthy active services may trigger failover. Transition calls carry `StateChangeRequestInfo` and move services between active, standby, and observer states. If failover requires fencing, an `HAServiceTarget` supplies fencing configuration and parameters; configured `FenceMethod` implementations are checked at startup and tried in order at runtime.

Writable control flow follows Hadoop serialization conventions. `write(DataOutput)` emits durable type/value state, and `readFields(DataInput)` reconstructs mutable objects. `CompressedWritable` modifies this flow by reading compressed bytes first and delaying field materialization until `ensureInflated()` is called. `AbstractMapWritable` persists class/id mappings so heterogeneous writable maps can deserialize their entry types.

## State and Persistence Behavior

This JDiff file persists API metadata for compatibility checking. It does not persist Hadoop runtime state itself.

The APIs described here do manage or expose several kinds of runtime state. `FilterFileSystem` holds a wrapped filesystem and optional scheme substitution. `RawLocalFileSystem` and `FTPFileSystem` maintain URI, configuration, and working-directory state. `FSDataInputStream` and `FSDataOutputStream` track stream position and may update `FileSystem.Statistics`. Builder instances hold mutable pre-build option state.

`Path` is serializable and includes `validateObject()` to defend against invalid deserialized objects. `PathHandle`, `PartHandle`, and `UploadHandle` are explicit durable byte handles, but their contents are opaque and filesystem-defined. Their equality semantics are part of correctness because handles may be used as replayable references.

`FsServerDefaults`, `FsStatus`, `ArrayPrimitiveWritable`, `ArrayWritable`, `BooleanWritable`, `ByteWritable`, `BytesWritable`, `AbstractMapWritable`, and `CompressedWritable` use `Writable` serialization. Compatibility depends on stable field order, class-id mapping rules, byte ordering, capacity/length handling, and lazy compression behavior.

Quota and storage APIs expose snapshots of filesystem accounting state. `QuotaUsage` combines namespace count, namespace quota, disk space consumed, space quota, and per-storage-type quota/consumption. `StorageStatistics` and `GlobalStorageStatistics` expose mutable process-level counters that can be reset. `FsStatus` and `FsServerDefaults` carry filesystem-reported capacity/default snapshots.

Trash state is filesystem-resident: moving to trash renames or copies paths into policy-defined trash directories, checkpoint creation creates durable checkpoint directories, and expunge removes old or all checkpoints. Policy selection is configuration-driven through `fs.trash.classname`.

HA APIs are mostly remote-control contracts, but `HAServiceTarget` stores target state such as desired transition target status and exposes derived fencing parameter maps. The target addresses, fencer, and ZKFC proxy state integrate local admin clients with remote services.

## Dependencies and Integration Points

This chunk depends heavily on Java standard library APIs: `File`, `URI`, `IOException`, `AccessControlException`, `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `DataInputStream`, `DataOutputStream`, `FileDescriptor`, `ByteBuffer`, `Charset`, `Serializable`, `ObjectInputValidation`, collections, `EnumSet`, `Iterator`, and network socket addresses.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration`, `Configured`, and `Configurable` for filesystem initialization, trash policy setup, builder options, HA proxies, and writable configuration propagation.
- `org.apache.hadoop.fs.FileSystem`, `FileContext`, `FileStatus`, `BlockLocation`, `BlockStoragePolicySpi`, `RemoteIterator`, `CreateFlag`, `Options.ChecksumOpt`, `Options.HandleOpt`, and permission/ACL classes.
- Stream optional-capability interfaces such as `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, and `CanUnbuffer`.
- `org.apache.hadoop.util.Progressable` for create/append progress callbacks and `org.apache.hadoop.util.DataChecksum.Type` for server defaults.
- Hadoop security through `org.apache.hadoop.security.AccessControlException` in HA methods and owner/group/permission operations in local filesystems.
- HA support classes outside this chunk: `HAServiceStatus`, `HAServiceProtocol.StateChangeRequestInfo`, `HAServiceProtocol.HAServiceState`, `NodeFencer`, and `ZKFCProtocol`.
- Protocol-buffer generated services under `org.apache.hadoop.ha.proto.*` and IPC `VersionedProtocol`.
- Hadoop IO base interfaces `Writable`, `WritableComparable`, and `Stringifier`.
- Apache Commons Net for `FTPFileSystem`, as documented by the class Javadoc.
- SLF4J through `FTPFileSystem.LOG`.

## Risks and Edge Cases

- The chunk begins mid-method metadata in `FileUtil` and ends mid-class in `DefaultStringifier`; neighboring chunks are required for complete class-level reports.
- JDiff signatures do not show private implementation details. Behavior such as permission handling, atomic rename guarantees, path normalization edge cases, symlink support, trash checkpoint naming, and compressed byte layout require implementation-source validation.
- `FileUtil.createJarWithClassPath` must expand environment variables and wildcards before writing manifests. Platform differences are explicit: `%VAR%` on Windows, `$VAR` otherwise, and case-insensitive environment lookup on Windows.
- `FileUtil.listFiles` and `list` convert null-returning Java file APIs into checked exceptions or empty lists. Tests must distinguish invalid directory, unreadable directory, no entries, and I/O error.
- `FilterFileSystem` has a very wide delegation surface. Missing one overridden method can bypass wrapper policy for ACLs, xattrs, storage policies, snapshots, trash roots, path capabilities, or path handles.
- `FSDataInputStream` advertises thread-safe positioned reads through `PositionedReadable`, but the Javadocs warn that not all implementations satisfy the requirement. This matters for HBase-like consumers.
- Byte-buffer access requires callers to release buffers. Failure to call `releaseBuffer` can leak pooled direct buffers or pin resources.
- `StreamCapabilities.hasCapability` is string-keyed. Typos, case mismatches, or unsupported optional features can lead to false capability assumptions.
- `FSDataOutputStreamBuilder` separates optional and mandatory options. Filesystems must reject unknown mandatory keys but may ignore optional ones; incorrect handling can silently drop caller requirements.
- `Path` compatibility is sensitive to URI escaping, Windows drive parsing, root/relative handling, serialization validation, and deprecated `makeQualified(FileSystem)` behavior.
- `PathHandle`, `PartHandle`, and `UploadHandle` expose opaque bytes. Equality and byte-buffer immutability are important because callers may persist or compare handles across processes.
- `RawLocalFileSystem.listStatus` is explicitly unsorted because it relies on Java `File.list()`. Tests and callers must not assume deterministic order.
- Local owner and permission mutation shell out to platform commands such as `chown` and `chmod`; behavior varies by OS, privileges, and filesystem support.
- FTP streams can block other operations until closed. Append is unsupported despite being part of the inherited filesystem surface.
- Trash per-path resolution exists because encryption-zone renames can fail across zones. Older `getCurrentTrashDir()` without a path can be wrong in those deployments.
- HA transition and fencing methods are remote and operationally risky. Incorrect fencing configuration can allow split-brain, while over-aggressive fencing can stop healthy nodes.
- `HAServiceTarget.addFencingParameters` maps values into shell-fencing environments. Key normalization and untrusted values need careful handling by shell-based fencers.
- `AbstractMapWritable` uses byte IDs for classes. ID collisions or failure to persist mappings correctly can corrupt heterogeneous map deserialization.
- `BytesWritable.getBytes()` exposes the backing array, and only the range `0..getLength()-1` is valid data. Callers that serialize or compare full capacity can read stale bytes.
- `BytesWritable` preserves old deprecated aliases `get()` and `getSize()` for compatibility; removing them would break existing consumers.
- `CompressedWritable` subclasses must call `ensureInflated()` before field access. Omitting that in accessors can expose uninitialized/default fields after deserialization.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks that all classes, interfaces, fields, overloads, visibility, exceptions, and deprecation markers in this chunk remain stable for Hadoop Common 3.2.4 compatibility.
- `FileUtil` tests for temp-file creation and delete-on-exit flagging, replacement failure modes, `list`/`listFiles` null-to-exception behavior, classpath jar manifest creation with Windows and Unix environment expansion, wildcard jar expansion, and all `write` overloads for `FileSystem` and `FileContext`.
- `FilterFileSystem` delegation tests covering ordinary file operations plus less common surfaces: ACLs, xattrs, snapshots, storage policies, symlinks, path handles, trash roots, builder factories, checksums, and path capability queries.
- Stream tests for seek/getPos, positioned read argument validation, `readFully` EOF behavior, byte-buffer read/release, unbuffer dispatch, readahead/drop-behind pass-through, hflush/hsync, capability strings, close semantics, and statistics position updates.
- Builder tests for fluent self-type returns, default values, create/overwrite/append flag combinations, checksum options, optional versus mandatory option storage, typed option serialization into `Configuration`, and filesystem rejection of unknown mandatory options.
- `Path` tests for construction from strings/URIs/components, parent-child resolution, normalization, Windows absolute parsing, scheme/authority stripping, merge semantics, `getFileSystem`, parent/name/root/depth queries, equality/order/hash, serialization validation, and deprecated qualification compatibility.
- Handle tests for `PathHandle`, `PartHandle`, and `UploadHandle` byte serialization, equality, immutability expectations, stale-handle rejection, and multipart upload resume behavior where supported.
- Local filesystem tests for raw path conversion, unsorted listing tolerance, create/append/truncate/rename/delete semantics, recursive delete failures, mkdir permission application, symlink create/status/target, owner/permission/time mutation, path capabilities, checksum failure quarantine, and Windows empty-directory rename handling.
- FTP tests with a controlled FTP server for initialization from config, authentication, open/create blocking until close, unsupported append, delete/list/status/mkdir/rename semantics, working directory handling, data connection mode, transfer mode, and default port logic.
- Quota/storage tests for `QuotaUsage` builder-derived values, per-storage-type quota/consumption, formatted headers, human-readable output, equality/hash, `FsStatus` and `FsServerDefaults` writable round trips, storage-type parsing/classification, and statistics registry reset/iteration.
- Trash tests for enabled/disabled policy behavior, move-to-trash return values for already-in-trash paths, checkpoint creation, old checkpoint deletion, immediate expunge, emptier runnable behavior, factory class loading, and encryption-zone-aware per-path trash locations.
- XAttr tests for hex/base64/quoted/unquoted decode, encode prefixes, invalid input exceptions, create/replace validation, and null or empty values.
- HA tests for health monitor exceptions, active/standby/observer transition no-op behavior when already in state, access-control propagation, helper unwrapping of remote exceptions, fencer argument validation, ordered fencing success/failure behavior, fencing parameter environment mapping, optional health-monitor address routing, ZKFC proxy creation, auto-failover flag, and observer support flag.
- Writable tests for golden serialized bytes and round trips for `ArrayPrimitiveWritable`, `ArrayWritable`, `BooleanWritable`, `ByteWritable`, `BytesWritable`, `FsStatus`, `FsServerDefaults`, and `AbstractMapWritable`; include class-id registry preservation, backing-array versus logical-length behavior, byte-wise comparison, and compressed lazy inflation.
- `ByteBufferPool` tests for direct/non-direct requests, minimum capacity handling, reuse after `putBuffer`, and robustness against caller-mutated buffer position/limit.
- `DataOutputOutputStream` tests for returning an existing `OutputStream` unchanged, wrapping plain `DataOutput`, and correct byte forwarding for single-byte and array writes.

## Cross-Chunk Notes

The preceding chunk is required to complete `FileUtil`; this chunk starts after the method name for `createLocalTempFile` has already appeared. The following chunk is required to complete `DefaultStringifier` and the rest of `org.apache.hadoop.io`. The merge lane should preserve this document as the line-range-specific research note and synthesize final per-file conclusions only after all chunks for `Apache_Hadoop_Common_3.2.4.xml` are available.
