# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.2.xml lines 12097-18158

## Scope

This chunk is a generated JDiff API snapshot for Apache Hadoop Common 3.2.2. It starts in the tail of `org.apache.hadoop.fs.FileUtil`, covers a large public/protected portion of `org.apache.hadoop.fs`, then covers `org.apache.hadoop.fs.ftp`, high-availability APIs under `org.apache.hadoop.ha`, protobuf-facing HA protocol bridge interfaces, the package note for `org.apache.hadoop.http.lib`, and the beginning of `org.apache.hadoop.io` through the start of `DefaultStringifier.toString(T)`.

Because this is JDiff XML, the research surface is the compatibility contract rather than method bodies: package membership, class/interface inheritance, implemented interfaces, public/protected method signatures, fields, checked exceptions, deprecation markers, and embedded Javadocs. The chunk begins and ends inside classes, so the merge lane must combine it with neighboring chunks for complete `FileUtil` and `DefaultStringifier` coverage.

## Purpose

The `FileUtil` tail provides convenience helpers for local-file replacement, safer directory listing wrappers, classpath-manifest jar creation, jar wildcard expansion, filesystem comparison, and simple whole-file writes through either `FileSystem` or `FileContext`.

The main `org.apache.hadoop.fs` section documents client-facing file system abstractions and concrete local implementations. It includes the `FilterFileSystem` delegation wrapper, stream wrappers for positioned reads and synchronized writes, builder APIs for output streams, path representation and validation, local/raw-local filesystem behavior, status/quota/statistics models, storage-type metadata, capability queries, trash policy extension points, path/upload handle tokens, xattr codecs, and exception types.

The `org.apache.hadoop.fs.ftp` section exposes an FTP-backed `FileSystem` using Apache Commons Net, with the standard Hadoop `FileSystem` lifecycle and operations adapted to remote FTP semantics.

The `org.apache.hadoop.ha` section defines the public contract used by Hadoop high-availability frameworks and admin commands: fencing methods, HA service health/state transitions, helper wrappers for RPC exception unwrapping, HA service targets, and failure exception types.

The `org.apache.hadoop.io` section begins the Hadoop serialization layer: map class-id metadata, primitive and writable arrays, byte-sequence comparables, bloom-backed map file declaration, primitive writable values, byte buffer pools, compressed lazy-inflation writables, and `DataOutput` to `OutputStream` adaptation.

## Important APIs, Types, and Functions

### File Utilities

- `FileUtil.replaceFile(File src, File target)` moves a source file to a target path and throws `IOException` on failure.
- `FileUtil.listFiles(File)` and `FileUtil.list(File)` wrap Java `File` listing calls so invalid directories, unreadable directories, or I/O problems surface as exceptions instead of ambiguous `null`.
- `FileUtil.createJarWithClassPath(...)` creates a small jar with a manifest classpath. The documented purpose is to bypass platform command-line length limits, expand environment variables before manifest insertion, and expand `*` jar wildcards because jar manifests do not support wildcard classpath entries.
- `FileUtil.getJarsInDirectory(String[, boolean])` expands a directory or wildcard path into jar URLs, returning an empty list when no local directory or jars exist.
- `FileUtil.compareFs(FileSystem, FileSystem)` compares filesystem identity.
- The overload family `FileUtil.write(...)` writes byte arrays, iterable text lines, or one `CharSequence` to a `Path` through `FileSystem` or `FileContext`, creating or overwriting the destination and returning the filesystem/context. Text overloads support explicit `Charset` and UTF-8 defaults.
- `FileUtil.SYMLINK_NO_PRIVILEGE` is a public constant related to symlink privilege handling.

### FileSystem Wrappers and Streams

- `FilterFileSystem` extends `FileSystem` and contains a protected `fs` delegate plus a `swapScheme` field. Its constructors accept no delegate or a wrapped `FileSystem`; almost all operations forward to the contained filesystem.
- Delegated `FilterFileSystem` operations include initialization, URI/canonical URI handling, path qualification/checking, block locations, open/create/append/concat, non-recursive create, replication, rename/truncate/delete, listing variants, working directory/home, status, local copy helpers, default block size/replication/server defaults, file status, msync/access, symlinks, checksums, permissions/owner/times, snapshots, ACLs, xattrs, storage policies, trash roots, output stream builders, and path capability checks.
- `FsConstants` defines public constants for local, FTP, ViewFs, maximum symlink path links, ViewFs overload scheme implementation naming, and ViewFs/ViewFs-overload type strings.
- `FSDataInputStream` extends `DataInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `CanUnbuffer`, and `StreamCapabilities`. It exposes `seek`, `getPos`, positioned `read`, positioned `readFully`, `seekToNewSource`, `ByteBuffer` reads, enhanced zero-copy buffer reads with `ByteBufferPool`, `releaseBuffer`, `unbuffer`, `getFileDescriptor`, cache hints, and `hasCapability`.
- `FSDataOutputStream` extends `DataOutputStream` and implements `Syncable`, `CanSetDropBehind`, and `StreamCapabilities`. It tracks position, wraps a stream with optional `FileSystem.Statistics`, supports `hflush`, `hsync`, `setDropBehind`, close, and capability queries.
- `FSDataOutputStreamBuilder<B,S>` is an abstract fluent builder bound to a `FileSystem` and `Path`. It captures permission, buffer size, replication, block size, recursive parent creation, progress callback, `CreateFlag`s, checksum options, optional config keys, mandatory config keys, and ends at abstract `build()`.

### FileSystem Data Models and Path APIs

- `FSError` represents unexpected filesystem errors presumed to reflect disk errors.
- `FSInputStream` is the older seekable positioned-readable base stream. It declares `seek`, `getPos`, `seekToNewSource`, positional `read`, argument validation, and `readFully` helpers.
- `FsServerDefaults` carries server-provided defaults: block size, bytes per checksum, write packet size, replication, file buffer size, data-transfer encryption, trash interval, checksum type, key provider URI, and default storage policy id.
- `FsStatus` implements `Writable` for capacity, used, and remaining bytes on a filesystem.
- `GlobalStorageStatistics` is a singleton-like enum registry with synchronized `get`, `put`, `reset`, and `iterator` methods for named `StorageStatistics` providers.
- `StorageStatistics` is an abstract per-`FileSystem`/`FileContext` statistics object with a name, optional scheme, long-stat iterator, lookup by key, tracking check, and reset hook.
- `GlobFilter` implements `PathFilter` for POSIX glob patterns with brace expansion and optional user filter composition.
- `InvalidPathException`, `InvalidPathHandleException`, `ParentNotDirectoryException`, `UnsupportedFileSystemException`, and `UnsupportedMultipartUploaderException` encode specific path, handle, directory-parent, filesystem-scheme, and multipart-uploader failures.
- `LocatedFileStatus` extends `FileStatus` with block locations, constructors covering ACL/encryption/erasure-coded flags or `FileStatus.AttrFlags`, lazy protected `setBlockLocations`, and equality/hash/compare behavior inherited around path identity.
- `Path` implements `Comparable`, `Serializable`, and `ObjectInputValidation`. It can be built from parent/child strings or paths, URI, or scheme/authority/path components, and exposes URI conversion, filesystem resolution, absolute/root/name/parent/suffix/depth queries, path merging, Windows absolute-path detection, qualification, equality/hash/compare, and deserialization validation.
- `PathFilter.accept(Path)` is the generic filtering hook used by globbing and list operations.
- `PathHandle`, `PartHandle`, and `UploadHandle` are opaque serializable references backed by `ByteBuffer` bytes plus default `toByteArray()` serialization; they represent path entities, multipart part IDs, and multipart upload IDs respectively.
- `PositionedReadable` defines thread-safe positional read methods that must not change the stream offset, while warning that not all filesystems meet that contract.
- `Seekable` defines `seek(long)` and `getPos()` for streams.
- `QuotaUsage` stores file/directory counts, namespace quota, space consumed/quota, storage-type quota and consumption, type-quota availability checks, equality/hash, and formatted quota output headers/strings.
- `ReadOption` is an enum for filesystem read options.
- `StorageType` is an enum of supported storage media with helpers for transient, movable, quota-supporting, list, parse-by-index/string, `DEFAULT`, and `EMPTY_ARRAY`.
- `XAttrCodec` encodes and decodes extended-attribute byte values as text, hex (`0x`), or base64 (`0s`) strings for display and command/HTTP input.
- `XAttrSetFlag.validate(String, boolean, EnumSet)` validates create/replace xattr semantics against whether the target xattr already exists.

### Local and FTP File Systems

- `LocalFileSystem` extends `ChecksumFileSystem`, exposes the `file` scheme, wraps a raw local filesystem, converts `Path` to `File`, copies to/from local paths, reports checksum failures by moving bad files aside on the same device, and supports local symlink operations.
- `RawLocalFileSystem` extends `FileSystem` and implements direct host-filesystem operations: URI/init, path conversion, `PathHandle` open, create/append, output-stream creation with modes and permissions, non-recursive create, concat, rename, Windows empty-directory rename handling, truncate, recursive delete, unsorted listing via Java `File`, directory creation, working directory/home, status, local-output staging, close, file status, owner/permission/time changes via host commands, symlink operations, and path capabilities.
- `FTPException` wraps FTP errors as runtime exceptions.
- `FTPFileSystem` extends `FileSystem` for the `ftp` scheme. It supports default-port lookup, URI/init, open, create, delete, list, file status, mkdirs, rename, and working-directory/home behavior. Append is explicitly documented as unsupported, and a stream returned from `create` must be closed before other APIs are used or subsequent calls may block.
- FTP public constants include logging, default buffer/block sizes, configuration prefixes for user/password/host/port/data connection mode/transfer mode, and an error string requiring same-directory operations.

### Capabilities, Sync, and Trash

- `StreamCapabilities.hasCapability(String)` lets streams advertise lower-case capability strings. Public constants cover `hflush`, `hsync`, `in:readahead`, `dropbehind`, and `unbuffer` behavior by reference to the corresponding interfaces.
- `StreamCapabilitiesPolicy.unbuffer(InputStream)` implements the standard policy for invoking `CanUnbuffer.unbuffer()` and exposes a message for unsupported unbuffer implementations.
- `Syncable.hflush()` makes written bytes visible to new readers; `Syncable.hsync()` is a stronger POSIX-like flush toward disk.
- `Trash` is a configured facade over pluggable `TrashPolicy` implementations. It can choose the correct trash volume for symlinks or mount points, move paths to trash, create checkpoints, expunge old checkpoints, immediately empty trash, return an emptier runnable, and resolve the current trash directory for a path.
- `TrashPolicy` is the abstract extension point for trash behavior. It has old and new initialization signatures, enabled checks, move/checkpoint/delete/empty operations, current-trash-directory APIs, an emptier runnable, factory methods based on `fs.trash.classname`, and protected state for `fs`, `trash`, and `deletionInterval`. The newer APIs avoid assuming trash always lives under `/user/$USER`, which matters for HDFS encryption zones.

### High Availability APIs

- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` represent invalid fencing configuration, failed failover, failed health checks, and failed state transitions.
- `FenceMethod` lets operators plug in vendor/device-specific fencing. It validates configured arguments with `checkArgs(String)` and attempts fencing with `tryFence(HAServiceTarget, String)`, returning success/failure while allowing runtime configuration failures.
- `HAServiceProtocol` defines health monitoring, transitions to active/standby/observer, service status retrieval, access-control and I/O exceptions, and public `versionID`.
- `HAServiceProtocolHelper` wraps static calls to the protocol and unwraps remote exceptions into specific exception types for `monitorHealth`, `transitionToActive`, `transitionToStandby`, and `transitionToObserver`.
- `HAServiceTarget` represents the target used by client-side HA admin commands. It supplies the service IPC address, optional health-monitor address, ZKFC address, fencer, fencing preflight check, service/health/ZKFC proxies, transition-target state, fencing parameters for scripts, auto-failover flag, and observer-state support flag.
- `HAServiceProtocolPB` and `ZKFCProtocolPB` are protobuf RPC bridge interfaces extending generated blocking interfaces plus `VersionedProtocol`.

### Hadoop IO Types

- `AbstractMapWritable` implements `Writable` and `Configurable`. It maintains per-instance class-to-id and id-to-class metadata for `MapWritable`/`SortedMapWritable`, with class IDs in the range 1 through 127, synchronized add/copy hooks, configuration accessors, and `write`/`readFields`.
- `ArrayFile` extends `MapFile` and is documented as a dense file-based mapping from integers to values.
- `ArrayPrimitiveWritable` wraps primitive arrays in a `Writable` without per-element object allocation and without copying the underlying array. It supports declared component-type constructors, `get`, component-type queries, `set`, and serialization hooks.
- `ArrayWritable` stores arrays of same-class `Writable` elements, exposes the value class, conversion to strings/object arrays, set/get, and `Writable` serialization. Its Javadoc recommends subclassing for reducer input types.
- `BinaryComparable` is an abstract byte-sequence comparable requiring `getLength()` and `getBytes()`, with byte-wise compare overloads, equality, and hash semantics tied to `WritableComparator.compareBytes/hashBytes`.
- `BloomMapFile` extends `MapFile`, declares bloom metadata constants, and exposes static `delete(FileSystem, String)` for deleting a bloom map file.
- `BooleanWritable`, `ByteWritable`, and `BytesWritable` implement `WritableComparable` semantics for boolean, byte, and resizable byte-sequence values. They expose mutable setters/getters, `readFields`/`write`, equality/hash/compare, and string rendering.
- `ByteBufferPool` allocates or reuses `ByteBuffer` instances with `getBuffer(boolean direct, int length)` and returns them through `putBuffer(ByteBuffer)`. The Javadoc says returned capacity may exceed the request but must be at least one byte.
- `org.apache.hadoop.io.Closeable` is a deprecated alias extending `java.io.Closeable`.
- `CompressedWritable` is an abstract `Writable` base whose final `readFields` and `write` methods store data compressed and lazily inflate it. Subclasses implement protected `readFieldsCompressed` and `writeCompressed`; field accessors must call `ensureInflated()`.
- `DataOutputOutputStream` adapts any `DataOutput` to an `OutputStream`, returning the original object when it already implements `OutputStream`, otherwise wrapping writes through `DataOutput`.
- The visible start of `DefaultStringifier` shows it implements `Stringifier`, has a `(Configuration, Class)` constructor, and exposes `fromString(String)` plus the beginning of `toString(T)`, both throwing `IOException`.

## Control Flow

This XML has no executable control flow, but the documented APIs imply key runtime paths:

- File utility writes open/create the destination through `FileSystem` or `FileContext`, overwrite existing content, write the supplied bytes/text, then return the same handle for fluent use or caller confirmation.
- Manifest-jar creation receives a classpath, resolves environment variables using platform-specific syntax, expands terminal jar wildcards, writes a manifest jar in the chosen working/target directory context, and returns the generated jar path plus wildcard metadata.
- `FilterFileSystem` normal control flow is delegation: public `FileSystem` calls enter the wrapper, path/URI scheme adjustments may be applied, and the contained `fs` performs the real operation. Subclasses alter behavior by overriding selected methods while inheriting pass-through behavior for the rest.
- Stream reads use `FSDataInputStream` to dispatch seek, positional read, byte-buffer read, zero-copy read, cache hint, unbuffer, and capability operations to the wrapped stream if it supports the needed interface. `PositionedReadable` calls are expected not to mutate current stream offset.
- Stream writes use `FSDataOutputStream` to track current position, pass data to the wrapped stream, update statistics, and delegate `hflush`/`hsync`/drop-behind/capability calls when supported.
- `FSDataOutputStreamBuilder` accumulates create/append state through fluent setters, stores optional and mandatory keys in its internal options configuration, and finally calls `build()` in a concrete subclass. Mandatory keys create an integration contract: downstream filesystem implementations should fail or reject unknown mandatory options rather than silently ignore them.
- `Path` construction normalizes URI-like path strings, parent/child combinations, or URI components; later calls convert to URI, resolve the owning `FileSystem` via `Configuration`, qualify relative paths, and validate deserialized state before use.
- Local filesystem operations translate Hadoop `Path` values to Java `File` values, then call host filesystem primitives or shell commands for permissions/ownership/timestamps. `LocalFileSystem` layers checksum handling over `RawLocalFileSystem`; raw local operations bypass checksum sidecar behavior.
- Trash deletion flow resolves the correct filesystem/volume for the path being deleted, checks whether trash is enabled or the item is already in trash, renames into a current trash directory, and later checkpoint/expunge operations rotate or delete trash checkpoints. The policy API allows encryption-zone-aware trash locations.
- FTP flow initializes connection information from URI/configuration, then performs remote open/create/delete/list/status/mkdir/rename operations. Its create-stream rule serializes interaction: callers must close the stream before invoking other methods to avoid blocking.
- HA management flow has health monitors call `monitorHealth()` and `getServiceStatus()`, admin/failover logic call transition methods with `StateChangeRequestInfo`, and fencing logic check and try configured `FenceMethod` implementations in order through a `HAServiceTarget`.
- `HAServiceTarget` proxy methods choose the main address or optional health-monitor address, while fencing parameter generation exposes target metadata to script-style fencers by environment variable naming conventions.
- `Writable` flow in `org.apache.hadoop.io` is the standard `write(DataOutput)`/`readFields(DataInput)` round trip. Map/array/binary/writable values mutate in memory through setters and persist themselves to Hadoop binary streams when asked.
- `CompressedWritable` flow is intentionally lazy: `readFields` stores compressed bytes, field readers call `ensureInflated`, inflation invokes subclass `readFieldsCompressed`, and `write` invokes subclass `writeCompressed` while preserving the compressed-copy optimization for large objects.

## State and Persistence Behavior

The JDiff XML persists release API metadata for compatibility checking. It does not itself store Hadoop runtime data.

`FileUtil` methods mutate the host or target filesystem: `replaceFile` changes directory entries; listing helpers observe filesystem state; manifest-jar creation creates a local jar; write helpers create or overwrite files. These operations are durable at the target filesystem unless the underlying implementation is ephemeral or fails partway through.

`FilterFileSystem` stores protected mutable wrapper state: the delegate `FileSystem` and optional scheme swap. Its persistence behavior is inherited from the delegate; the wrapper itself is process-local.

`FSDataInputStream` and `FSInputStream` maintain stream cursor state, while positioned-read APIs promise not to alter that cursor. `FSDataOutputStream` maintains write position and potentially updates `FileSystem.Statistics`. `hflush` and `hsync` have different durability/visibility semantics: `hflush` is about reader visibility, while `hsync` pushes data closer to disk persistence.

`FSDataOutputStreamBuilder` stores pending creation state in memory until `build()`: target filesystem/path, permission, buffer size, replication, block size, recursive flag, progress callback, flags, checksum options, optional options, and mandatory option keys.

`FsServerDefaults`, `FsStatus`, `LocatedFileStatus`, `QuotaUsage`, `Path`, storage type values, xattr codec values, and handle interfaces are data carriers. Some are serializable or `Writable`; compatibility depends on preserving serialized forms and semantic equality, especially for `Path`, `PathHandle`, `PartHandle`, `UploadHandle`, and status/quota objects.

`RawLocalFileSystem` and `LocalFileSystem` persist changes directly in the local filesystem. Important durable effects include create/append/truncate/delete/rename, directory creation, owner/group/permission changes, timestamps, symlink creation, checksum-bad-file relocation, and local-output staging completion.

`Trash` and `TrashPolicy` persist soft deletions as filesystem renames into trash directories and later checkpoint directories. `deletionInterval` controls expiration behavior; current trash location may vary by source path for encryption-zone compatibility.

`FTPFileSystem` persists changes on the remote FTP server. State also includes process-local connection/session behavior, working directory, and configuration-derived credentials/host/transfer-mode settings.

HA APIs represent distributed service state rather than direct storage. Transition methods can change the active/standby/observer role of a service. Fencing methods can have severe external side effects such as killing processes, revoking storage access, or power control. `HAServiceTarget` fencing parameters are transient data passed to fencers or scripts.

`AbstractMapWritable` persists a per-instance class-id map alongside contents so nested or varied writable maps can deserialize class metadata without static global maps. `ArrayPrimitiveWritable`, `ArrayWritable`, `BooleanWritable`, `ByteWritable`, `BytesWritable`, `FsStatus`, and `CompressedWritable` all persist through `DataOutput`/`DataInput`. `BytesWritable` distinguishes logical length from backing capacity; callers using `getBytes()` observe the backing array and must respect `getLength()`.

`ByteBufferPool` owns process-local reusable buffers; returning buffers controls memory reuse but is not durable. `DataOutputOutputStream` stores no durable state beyond forwarding writes to the wrapped `DataOutput`.

## Dependencies and Integration Points

This chunk depends heavily on Java standard APIs: `java.io.File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `FileDescriptor`, checked I/O exceptions, URI, `ByteBuffer`, collections, `EnumSet`, `InetSocketAddress`, and serialization interfaces.

Key Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configured` for filesystem initialization, trash policy selection, FTP setup, output builder options, HA proxy creation, and IO stringification setup.
- `org.apache.hadoop.fs.FileSystem`, `FileContext`, `FileStatus`, `BlockLocation`, `Path`, `FsPermission`, `AclStatus`, `CreateFlag`, `Options.ChecksumOpt`, `Options.HandleOpt`, and `BlockStoragePolicySpi` as the central filesystem contracts.
- `org.apache.hadoop.util.Progressable` for create/write progress callbacks.
- Stream capability interfaces such as `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `CanUnbuffer`, `StreamCapabilities`, and `Syncable`.
- `org.apache.hadoop.io.Writable`, `WritableComparable`, `WritableComparator`, `ByteBufferPool`, `MapFile`, and `Stringifier` for Hadoop binary serialization and comparison.
- HDFS and distributed-filesystem features surfaced through generic `FileSystem` APIs: snapshots, ACLs, xattrs, encryption-zone-aware trash, erasure-coded file status flags, storage policies, storage type quotas, and path handles.
- FTP integration through Apache Commons Net and SLF4J logging.
- HA integration with `AccessControlException`, `NodeFencer`, `ZKFCProtocol`, `HAServiceStatus`, generated protobuf service interfaces, and Hadoop IPC `VersionedProtocol`.
- The `hadoop.http.filter.initializers` configuration key documented by the `org.apache.hadoop.http.lib` package note.

## Risks and Edge Cases

- The chunk begins mid-`FileUtil`; earlier methods and fields are not visible here. It also ends mid-`DefaultStringifier`; later methods and docs must come from the next chunk.
- JDiff shows API signatures and documentation, not implementations. Exact exception ordering, validation behavior, concurrency, resource cleanup, stream wrapping, and remote call details require implementation-source validation.
- `FileUtil.list` and `listFiles` intentionally convert ambiguous Java `null` results into exceptions. Callers migrating from raw Java APIs must handle checked `IOException` and access-denied cases.
- Manifest classpath jar creation is platform-sensitive: environment variable syntax differs between Windows and non-Windows platforms, Windows variables are case-insensitive, and wildcard expansion only covers `.jar`/`.JAR` entries.
- Whole-file `FileUtil.write` helpers overwrite existing files. They are convenient but risky for callers expecting append, atomic replace, or partial-write rollback.
- `FilterFileSystem` inherits the delegate's semantics. Subclasses that override only some methods can accidentally leak unsupported behavior, wrong scheme/authority, or inconsistent capability reporting through inherited pass-through methods.
- `PositionedReadable` documents thread-safety as required but also warns not all implementations satisfy it. Consumers such as HBase-style random readers should verify the concrete filesystem.
- `FSDataInputStream` enhanced byte-buffer access requires correct buffer release. Missing `releaseBuffer` calls can leak pooled or direct buffers.
- `StreamCapabilities` uses lower-case strings instead of enums. Typos or unrecognized capability names silently depend on implementation policy.
- `hflush` and `hsync` are often confused. Tests and callers need to distinguish reader visibility from stronger sync semantics.
- `Path` accepts URI-like strings with normalization and Windows-specific absolute path handling. Edge cases include drive letters, authority-less absolute paths, root paths with no parent, deserialization attacks, and deprecated `makeQualified(FileSystem)`.
- `LocatedFileStatus` equality/hash are path-based, so changes in block locations, ACL/encryption/erasure flags, or metadata do not necessarily affect equality.
- `RawLocalFileSystem.listStatus` notes that ordering is not guaranteed because it relies on Java `File.list()`.
- `RawLocalFileSystem` owner/permission/time updates depend on host commands or platform capabilities, creating portability and permission risks.
- `LocalFileSystem.reportChecksumFailure` moves files aside on the same device; failure to move should not be confused with successful quarantine.
- FTP append is unsupported, create streams can block other APIs until closed, and remote FTP operations often have weaker atomicity and consistency than HDFS/local operations.
- Trash behavior is rename-based and may fail across volumes or encryption zones unless the path-aware trash directory APIs are used.
- `TrashPolicy.initialize(conf, fs, home)` is deprecated because it assumes a home-based trash location; implementations should prefer the two-argument initialization plus path-aware current-trash lookup.
- HA fencing can be destructive by design. Bad fencing parameters or script environment generation can kill the wrong process or affect the wrong node.
- `HAServiceTarget.getHealthMonitorAddress()` may route monitoring to a separate lifeline RPC server; failover tests must cover both null and non-null cases.
- `AbstractMapWritable` supports at most 127 distinct classes per map instance. Large heterogeneous maps can exceed the id range.
- `ArrayPrimitiveWritable` does not copy the underlying array. External mutation after wrapping can change serialized output.
- `BytesWritable.getBytes()` exposes backing capacity, not just logical contents. Callers must use `copyBytes()` when they need an exact-length immutable-ish copy.
- `CompressedWritable` requires all field accessors in subclasses to call `ensureInflated()`. Forgetting this creates stale/uninitialized field reads.
- `org.apache.hadoop.io.Closeable` remains as a deprecated compatibility alias and should not be removed even though `java.io.Closeable` is preferred.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks that all public/protected methods, fields, deprecation markers, abstract/final/static/synchronized attributes, and checked exceptions in this chunk remain stable for Hadoop Common 3.2.2 compatibility.
- `FileUtil` tests for replacing files, invalid/unreadable directory listing exceptions, empty-list behavior, classpath manifest jar generation, environment expansion, wildcard jar expansion, filesystem comparison, and overwrite semantics for byte/text writes through both `FileSystem` and `FileContext`.
- `FilterFileSystem` tests with a tracing delegate to prove calls forward correctly, preserve exceptions, expose raw filesystem, handle URI/scheme qualification, close the delegate, and report capabilities from the wrapped filesystem.
- Stream tests for `FSDataInputStream` seek/getPos, positional reads not changing offset, `readFully` EOF behavior, byte-buffer read/release, readahead/drop-behind unsupported behavior, unbuffer policy, file descriptor availability, and `hasCapability` string handling.
- Stream output tests for `FSDataOutputStream` position accounting, statistics updates, close delegation, `hflush`/`hsync` propagation, drop-behind handling, and capability reporting.
- Builder tests for every fluent setter, create/overwrite/append flags, recursive parent behavior, checksum options, optional versus mandatory option propagation, and concrete `build()` failure on unknown mandatory keys.
- `Path` tests for constructor variants, URI conversion, parent/name/root/depth/suffix behavior, Windows absolute path detection, `mergePaths`, deprecated and current qualification, filesystem resolution through `Configuration`, equality/hash/compare, and `validateObject` rejecting invalid deserialized state.
- Local filesystem tests for raw versus checksumed behavior, path-to-file conversion, create/append/truncate/delete/rename, Windows rename edge cases, unsorted listing tolerance, mkdirs idempotence, working directory behavior, status/capacity, permission/owner/time updates, symlink support, path handles, and checksum-failure quarantine.
- Status/quota/statistics tests for `FsStatus` writable round trips, `FsServerDefaults` constructor/getter coverage, `LocatedFileStatus` block location and attr flag behavior, `QuotaUsage` type quotas and formatted headers, `StorageStatistics` lookup/reset behavior, and global statistics registry synchronization.
- `GlobFilter` tests for POSIX glob syntax, brace expansion, invalid pattern exceptions, and composition with a user `PathFilter`.
- Handle tests for `PathHandle`, `PartHandle`, and `UploadHandle` byte-buffer and byte-array serialization plus equality semantics.
- XAttr tests for text/hex/base64 encode/decode, invalid encodings, quoted text handling, and `XAttrSetFlag.validate` create/replace combinations.
- Trash tests for disabled trash, already-in-trash behavior, path-aware trash root resolution, encryption-zone-aware trash directory behavior, checkpoint creation, expunge, immediate emptying, and factory selection through `fs.trash.classname`.
- FTP tests with a controlled FTP server for initialization from URI/config, open/create close discipline, append unsupported errors, delete/list/status/mkdir/rename, working directory/home behavior, and credentials/port/transfer-mode config keys.
- HA tests for fencing argument validation, ordered fencing success/failure, script parameter map generation, health monitor address fallback, proxy creation, transition methods, observer support flag, auto-failover flag, exception unwrapping in `HAServiceProtocolHelper`, and protobuf bridge compatibility.
- IO serialization tests for `AbstractMapWritable` class-id persistence and 127-class limit, primitive array writable no-copy behavior, `ArrayWritable` homogeneous element round trips, `BinaryComparable` ordering/hash consistency, `BooleanWritable`/`ByteWritable`/`BytesWritable` comparison and writable round trips, byte buffer pool direct/non-direct allocation and return, `CompressedWritable` lazy inflation, and `DataOutputOutputStream` wrapping/non-wrapping cases.

## Cross-Chunk Notes

The previous chunk is required to complete `org.apache.hadoop.fs.FileUtil`, because this range starts after the `createLocalTempFile` method documentation has already begun. The next chunk is required to complete `org.apache.hadoop.io.DefaultStringifier`, because this range stops at the opening metadata for `toString(T)`.
