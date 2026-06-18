# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 12113-18228

## Scope

This chunk is a JDiff API description for Apache Hadoop Common 3.3.6. It is not executable implementation source; it records public and protected API signatures, inheritance, fields, checked exceptions, deprecation state, and Javadoc-derived behavioral contracts. The slice starts inside `org.apache.hadoop.fs.FileSystem` and continues through filesystem utility, stream, path, local filesystem, statistics, quota, capability, and trash APIs under `org.apache.hadoop.fs`.

Because the source is API XML, the "control flow" below is the documented call/delegation flow and object lifecycle promised to callers and implementors.

## Purpose

The chunk captures the central Hadoop filesystem API surface used by clients, filesystem implementors, wrappers, tests, and downstream projects. It documents:

- Extension points for `FileSystem` and its forwarding wrapper `FilterFileSystem`.
- Local filesystem implementations (`LocalFileSystem`, `RawLocalFileSystem`) and file utility helpers (`FileUtil`).
- Stream contracts for seeking, positional reads, vectored reads, buffering, sync/flush, stream capabilities, and IO statistics.
- Builder APIs for input/output stream creation and generic option negotiation.
- Persistent value objects for paths, file status with block locations, quotas, server defaults, filesystem capacity, storage types, path handles, and multipart handles.
- Integration contracts for ACLs, xattrs, snapshots, storage policies, multipart upload, trash handling, and global statistics.

## Important APIs, Types, and Functions

### `FileSystem` tail section

The chunk begins with the extended API tail of `org.apache.hadoop.fs.FileSystem`. It covers ACL/xattr continuations and then documents xattr accessors (`getXAttr`, `getXAttrs`, `listXAttrs`, `removeXAttr`) where names must include a namespace prefix such as `user.attr`; unsupported implementations may throw `UnsupportedOperationException`.

Storage policy methods (`satisfyStoragePolicy`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, `getAllStoragePolicies`) expose HDFS-oriented placement policy controls through the common API. Trash methods (`getTrashRoot`, `getTrashRoots`) define default user trash location behavior, and `hasPathCapability(Path, String)` gives implementors a path-scoped feature probe with a base default of false.

Static discovery/statistics APIs include `getFileSystemClass(scheme, conf)`, which scans service-loaded filesystem implementations and configuration bindings, deprecated synchronized global `Statistics` accessors, `clearStatistics`, `printStatistics`, symlink toggles, `getStorageStatistics`, and `getGlobalStorageStatistics`.

Builder entry points (`createFile`, `appendFile`, `openFile(Path)`, `openFile(PathHandle)`, protected `openFileWithOptions`, and `createMultipartUploader`) define newer extensible creation/open flows. The documented default for `openFileWithOptions` performs a blocking `open(Path, int)` but returns the result in a `CompletableFuture`; subclasses can override for truly asynchronous behavior.

The class doc is a critical integration warning: public/protected API additions must be reflected through `FilterFileSystem`, `ChecksumFileSystem`, and tests such as `TestFilterFileSystem.MustNotImplement` and `TestHarFileSystem`. It also says Hadoop treats HDFS behavior as the normative filesystem contract when Javadocs and specification disagree.

### `FileUtil`

`FileUtil` is a static utility collection for local and cross-filesystem operations. It converts `FileStatus[]` to `Path[]`, recursively deletes files/directories (`fullyDelete`, `fullyDeleteContents`, delete-on-exit registration), reads symlink targets, copies among `FileSystem`, `FileContext`, and `java.io.File`, and writes bytes/text to filesystem paths.

Important platform-sensitive APIs include `makeShellPath`, `makeSecureShellPath`, `symLink`, `chmod`, `setOwner`, `setReadable`, `setWritable`, `setExecutable`, `canRead`, `canWrite`, and `canExecute`. The XML specifically notes Windows differences and symlink privilege return code `SYMLINK_NO_PRIVILEGE`. Archive helpers (`unZip`, `unTar`) and classpath helpers (`createJarWithClassPath`, `getJarsInDirectory`) support process launch and unpacking workflows.

Operational risks in this API include partial deletion/copy results: several methods return false after partial work rather than guaranteeing all-or-nothing behavior, and recursive copy with `deleteSource=true` may delete source subtrees as they are copied.

### `FilterFileSystem`

`FilterFileSystem` wraps a contained `FileSystem` in the protected `fs` field and forwards almost the full `FileSystem` API surface. The chunk lists forwarding for URI qualification, path checking, block locations, open/create/append/concat/delete/rename/truncate, status/listing operations, local copy helpers, working directory, space usage, defaults, ACLs, xattrs, snapshots, symlinks, checksums, permissions/times/owners, storage policies, builder APIs, path capabilities, and trash roots.

This class is a compatibility chokepoint. New methods in `FileSystem` must either be passed through here or deliberately listed as unsupported by tests. The `swapScheme` field indicates wrapper-level URI scheme substitution support. `hasPathCapability` has special documented expectations from `FileSystem`: wrappers must avoid claiming capabilities that the filter cannot safely provide.

### Builder interfaces and constants

`FSBuilder<S, B>` defines `opt` and `must` option setting for string, boolean, int, long, double, and string-array values, plus `build`. The Javadoc records the HADOOP-18724 compatibility problem: overloaded long/double/float variants can bind unexpectedly, so explicit `optLong`, `optDouble`, `mustLong`, and `mustDouble` were added. Older float/double overloads are deprecated or forward through long paths with precision loss. Mandatory options must cause `build()` to throw `IllegalArgumentException` when unsupported.

`FSDataOutputStreamBuilder` extends Hadoop's abstract builder implementation for creating or appending `FSDataOutputStream` objects. It manages permission, buffer size, replication, block size, recursion, progress callbacks, create/overwrite/append flags, checksum options, generic options, and final `build`. The default policy is non-recursive parent creation unless `recursive()` is set.

`FutureDataInputStreamBuilder` specializes builders for asynchronous input stream creation, returning `CompletableFuture<FSDataInputStream>` and accepting an optional `FileStatus` hint via `withFileStatus`.

`FsConstants` provides shared identifiers for local filesystems, FTP, viewfs, maximum symlink resolution count, and viewfs overload patterns.

### Stream and IO APIs

`FSDataInputStream` wraps an `FSInputStream` in a `DataInputStream` and implements a wide set of optional interfaces: `Seekable`, `PositionedReadable`, byte-buffer readable variants, file descriptor access, drop-behind/readahead controls, enhanced byte-buffer access, unbuffering, stream capability probing, and IO statistics. It exposes `seek`, `getPos`, positional `read`, `readFully`, alternate-source seek, byte-buffer reads, buffer release, `unbuffer`, `hasCapability`, IO statistics extraction, and vectored read parameters and execution.

`FSDataOutputStream` wraps `OutputStream` in `DataOutputStream` and implements `Syncable`, `CanSetDropBehind`, `StreamCapabilities`, `IOStatisticsSource`, and `Abortable`. It exposes position, close, capability probing, `hflush`, `hsync`, drop-behind, IO statistics, and abort. `abort` is delegated to the wrapped stream only if it implements `Abortable`; otherwise it raises `UnsupportedOperationException`.

`FSInputStream` is the abstract seekable/positioned base. It requires `seek`, `getPos`, and `seekToNewSource`, supplies positional read/readFully helpers, and offers `validatePositionedReadArgs` to enforce nonnegative positions and buffer bounds. Its `toString` may include subclass IO statistics if implemented.

`Seekable` is the minimal `seek`/`getPos` contract. `PositionedReadable` defines thread-safe positional read and readFully contracts, while warning that not all filesystem implementations satisfy thread safety. Its default vectored-read API reads ranges asynchronously via `FileRange.setData(CompletableFuture)`, may make the post-call stream position undefined, may mix data if the file changes during operation, and may block normal reads during execution.

`StreamCapabilities` standardizes lower-case capability strings for stream features: `hflush`, `hsync`, readahead, drop-behind, unbuffer, byte-buffer reads, positioned byte-buffer reads, IO statistics, vectored IO, abortable streams, and IO statistics context. `StreamCapabilitiesPolicy.unbuffer(InputStream)` centralizes the policy for invoking `CanUnbuffer`.

`Syncable` defines `hflush` for making client-buffered data visible to new readers and `hsync` for fsync-like persistence toward disk, with the exact filesystem semantics delegated to the Hadoop filesystem specification.

### Status, statistics, and quota types

`FsServerDefaults` is a `Writable` value object carrying server default block size, bytes per checksum, write packet size, replication, file buffer size, encryption flag, trash interval, checksum type, key provider URI, and default storage policy ID.

`FsStatus` is a `Writable` capacity snapshot with capacity, used, and remaining byte counters.

`GlobalStorageStatistics` is an enum singleton-style registry with synchronized `get`, `put`, `reset`, and iterator methods over named `StorageStatistics` instances. `StorageStatistics` itself is an abstract per-filesystem or per-context statistics provider with name, optional scheme, long-statistic iterator, `getLong`, `isTracked`, and `reset`. Values need not be a consistent point-in-time snapshot.

`QuotaUsage` stores namespace and storage-space quota usage for directories. It exposes counts, quotas, type-specific quota and consumption by `StorageType`, equality/hash behavior, and CLI-style string/header formatting including human-readable and storage-type modes. Protected setters and builder constructors indicate instances are normally populated by builders or subclasses.

`StorageType` is an enum for storage media. It exposes transient/movable/type-quota support checks, list helpers, parsing by int/string, a default type, and an empty array constant.

### Path, handles, and listing

`Path` is the core serializable, comparable URI-like name for files/directories. Constructors accept parent/child strings, `Path` combinations, raw strings, `URI`, and scheme/authority/path components. Static helpers strip scheme/authority, merge paths while preserving the first path's scheme/authority, and detect Windows absolute drive paths. Instance methods expose URI conversion, filesystem resolution from `Configuration`, absolute/root/name/parent/suffix/depth checks, equality/hash/compare, deprecated `makeQualified(FileSystem)`, and deserialization validation to reject malicious object streams without a URI.

`PathFilter` is the single-method inclusion predicate used by listing/globbing. `GlobFilter` implements it using POSIX glob patterns with brace expansion and can compose with a user filter.

`PathHandle` and `PartHandle` are opaque serializable references represented as byte buffers, with default `toByteArray` and required `bytes`/`equals` methods. `PathHandle` can include enough metadata to validate later path access independent of subsequent filesystem mutations; `InvalidPathHandleException` is thrown when encoded constraints no longer hold. `PartHandle` identifies a multipart upload part.

`PartialListing` represents one page of directory/listing results, or a stored remote exception. Its `get()` behaves like a future result: it returns the list or throws the captured `IOException`. Multiple partial listings may need to be combined for a full directory listing.

`LocatedFileStatus` extends `FileStatus` with block locations. Constructors cover wrapping an existing status, explicit status fields, ACL/encryption/erasure-coded booleans, and attribute flag sets. Equality, ordering, and hash code remain path-based, while `getBlockLocations` warns that HDFS replicated and erasure-coded files may have different `BlockLocation` formats.

### Local filesystem APIs

`LocalFileSystem` extends `ChecksumFileSystem` and represents the checksummed local filesystem. It initializes with a URI/configuration, reports scheme `file`, exposes the raw filesystem, maps `Path` to `File`, handles local copy shortcuts, reports checksum failures by moving files to a bad-file directory on the same device, and supports symlink creation/status/targets.

`RawLocalFileSystem` extends `FileSystem` and implements direct local filesystem operations without checksum wrapping. It provides path-to-file conversion, URI/initialization, `open` by `Path` or `PathHandle`, append/create/createNonRecursive variants, protected output stream creation with optional mode, concat, rename, Windows-specific empty destination directory handling, truncate, delete, unsorted list status based on `File.list()`, existence, mkdir helpers, working directory, status, local output staging, close/toString, file status, owner/permission/time mutation, path handles, symlinks, link status/target, and path capability probing.

The local APIs depend heavily on `java.io.File`, process-level OS commands for owner/permission changes, and platform-specific behavior around Windows permissions, symlinks, ordering, and rename semantics.

### Multipart upload and trash

`MultipartUploader` is a closeable, IO-statistics-capable interface for multipart/cross-node uploads. It uses `CompletableFuture` for `startUpload`, `putPart`, `complete`, `abort`, and best-effort `abortUploadsUnderPath`. Parts may be uploaded in any order or parallel. `putPart` must close the input stream after reading. `complete` accepts a non-empty map of part numbers to part handles and returns a path handle. `abortUploadsUnderPath` may be unsupported (`-1`) and can miss entries with eventually consistent listings.

`Trash` is a configured wrapper around filesystem trash policy. Constructors accept `Configuration` or `(FileSystem, Configuration)`. `moveToAppropriateTrash` resolves symlinks/mount points to move deleted paths into the trash for the actual volume, `isEnabled` reports policy status, `moveToTrash` moves a path when enabled and not already trashed, and this chunk ends at `checkpoint`.

## Control Flow and Lifecycle

The primary documented flows are:

- `FileSystem` discovery: `Path.getFileSystem(conf)` resolves a `FileSystem`; `FileSystem.getFileSystemClass(scheme, conf)` can trigger service loading and configuration lookup for implementations.
- Builder-based open/create: callers obtain builders from `FileSystem.createFile`, `appendFile`, or `openFile`; optional and mandatory options are set on `FSBuilder`; `build()` validates mandatory support and performs the filesystem operation. The default open path routes through `openFileWithOptions`, which by default calls blocking `open(Path, int)` and exposes the result through a `CompletableFuture`.
- Wrapper delegation: `FilterFileSystem` receives caller operations and forwards them to its contained `fs`, preserving behavior unless subclasses override. This makes it the required integration point for any new `FileSystem` method.
- Local file IO: `LocalFileSystem` layers checksum behavior over a raw local filesystem; `RawLocalFileSystem` maps Hadoop `Path` values to `java.io.File` and performs open/create/delete/list/rename/permission operations against the host OS.
- Stream use: input streams support seek, positioned reads, byte-buffer reads, vectored reads, optional unbuffer/readahead/drop-behind, and capability probes. Output streams support position, flush/sync, drop-behind, optional abort, and IO statistics.
- Multipart upload: `startUpload` returns an upload handle, zero or more `putPart` calls produce part handles, `complete` assembles parts into a file and returns a path handle, and `abort` or `abortUploadsUnderPath` cleans up pending uploads.
- Trash flow: delete clients can call `moveToAppropriateTrash`, which resolves the actual volume for symlinks/mount points and then moves content to that volume's trash root if enabled.

## State and Persistence Behavior

Persistent or state-bearing elements include:

- `Path` values are serializable and validate their URI during deserialization.
- `PathHandle` and `PartHandle` serialize opaque byte identifiers and rely on equality semantics supplied by implementations.
- `FileSystem.statistics` is a protected per-instance statistics field, while deprecated global `Statistics` maps and `GlobalStorageStatistics` provide process-wide state. Global registry operations are synchronized.
- `StorageStatistics` values can be reset and may not represent a stable snapshot while iterating.
- `FSDataOutputStream` tracks position and delegates persistence semantics to `hflush`/`hsync`; `hsync` is fsync-like but still subject to device caching.
- `FsStatus`, `FsServerDefaults`, and `QuotaUsage` are value snapshots of capacity/default/quota state, with `FsStatus` and `FsServerDefaults` implementing Hadoop `Writable`.
- `FileUtil.fullyDelete`, `FileUtil.copy`, `RawLocalFileSystem.delete`, `rename`, and `Trash.moveToTrash` mutate filesystem contents and may leave partial state on failure.
- `MultipartUploader` persists temporary upload state between `startUpload`, `putPart`, and `complete`/`abort`; cleanup may be best effort and eventually consistent for some backends.
- `RawLocalFileSystem` maintains working directory state and may use process/OS-level commands for permissions and ownership.

## Dependencies and Integration Points

This API surface depends on Java core IO/NIO/concurrency (`java.io`, `java.net.URI`, `java.nio.ByteBuffer`, `CompletableFuture`, `Iterator`, collections), Hadoop configuration and IPC (`Configuration`, `RemoteException`), Hadoop filesystem types (`Path`, `FileStatus`, `BlockLocation`, `Options`, `PathHandle`, `UploadHandle`, `MultipartUploaderBuilder`), permissions/security (`FsPermission`, `FsAction`, `AclStatus`, `AccessControlException`), checksum and utility types (`DataChecksum.Type`, `Progressable`, `ByteBufferPool`), and statistics (`IOStatistics`, `IOStatisticsSource`).

Key integration points are downstream filesystem implementations, `FilterFileSystem` wrappers, `ChecksumFileSystem`, HDFS-specific behavior, object-store filesystems, viewfs, local OS filesystems, CLI/status formatting, multipart upload implementations, and test suites which enforce method forwarding or unsupported declarations.

## Risks and Edge Cases

- The chunk is generated API XML; it describes contracts but not implementation details. Behavioral research should be reconciled with Java sources before making code changes.
- The source slice starts mid-`FileSystem` and ends mid-`Trash`; adjacent chunks are needed for complete class coverage.
- `FileSystem` API evolution is high risk because wrappers and downstream shims must be updated together.
- `FSBuilder` overloads can silently coerce floating-point values through long paths; callers needing cross-version correctness should pass strings explicitly or use explicit long/double methods.
- `FilterFileSystem` can accidentally over-advertise capabilities if it forwards or claims path capabilities incorrectly.
- Positional-read thread safety is required by contract but explicitly not met by all filesystems; this affects HBase-style consumers.
- Vectored reads have undefined position after completion, undefined results during concurrent file mutation, and may block regular reads.
- Local filesystem behavior varies by platform: Windows symlink privileges, permission bits, execute semantics, path drive handling, `File.list()` ordering, and rename/delete edge cases are all documented hazards.
- Recursive delete/copy utilities and trash/multipart cleanup are not transactional and may leave partially mutated state.
- `GlobalStorageStatistics` and deprecated `FileSystem.Statistics` are process-wide mutable registries; tests must clear/reset to avoid cross-test contamination.
- `StorageStatistics` iterators do not promise point-in-time consistency.
- Multipart aborts under a path are best effort and may miss uploads under eventually consistent listings.

## Test Signals

Useful test coverage implied by this API chunk includes:

- API compatibility/JDiff checks against `Apache_Hadoop_Common_3.3.6.xml` for signature, visibility, exception, field, deprecation, and doc-contract drift.
- `FilterFileSystem` forwarding tests for every new `FileSystem` method, plus negative tests where wrappers must not claim unsupported path capabilities.
- Builder tests for optional vs mandatory options, unsupported mandatory option failures, long/double overload behavior, recursive parent creation, append/create/overwrite flags, checksum options, and asynchronous open futures.
- Stream tests for seek/getPos, positional read preserving current offset, EOF behavior, byte-buffer reads, vectored reads, unbuffer/drop-behind/readahead, capability string lower-casing, abort fallback, and IO statistics exposure.
- Local filesystem tests across Unix and Windows for symlinks, permissions, chmod/chown fallbacks, rename/delete/truncate, unsorted listings, working directory handling, path handles, checksum failure quarantine, and file status for links.
- Value-object serialization and equality tests for `Path`, `PathHandle`, `PartHandle`, `FsStatus`, `FsServerDefaults`, `LocatedFileStatus`, `QuotaUsage`, and storage type parsing.
- Multipart uploader lifecycle tests for out-of-order/parallel parts, input stream closure, complete with non-empty handles, abort, unsupported path-wide abort, and IO statistics availability.
- Trash tests for disabled trash, already-in-trash paths, symlink or mount-point volume resolution, checkpoint behavior in the adjacent chunk, and filesystem-specific trash roots.
