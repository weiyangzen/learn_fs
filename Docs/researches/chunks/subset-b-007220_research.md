# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml lines 12117-18225

## Scope

This chunk is a generated JDiff API snapshot for Hadoop Common 3.3.5, not executable implementation source. It begins inside `org.apache.hadoop.fs.FileSystem` extended-attribute documentation and continues through complete or partial public API entries for `FileSystem`, `FileUtil`, `FilterFileSystem`, `FSBuilder`, `FsConstants`, stream classes, filesystem metadata/value classes, local filesystem implementations, multipart upload handles, `Path`, quota/storage/capability APIs, `Trash`, and the opening of `TrashPolicy`.

The XML records API compatibility metadata: class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, deprecation state, and Javadoc contracts. The merge lane must combine this chunk with adjacent chunks before making whole-file claims about `FileSystem` or `TrashPolicy`, because this chunk starts and ends in the middle of those classes.

## Purpose and major API surface

`FileSystem` is represented from xattr/storage/trash/statistics/builder methods through its class documentation. The visible API covers `listXAttrs`, `removeXAttr`, storage policy setters/getters, trash root discovery, path capability probing, implementation-class lookup via service loading, deprecated scheme-indexed statistics, global storage statistics, file create/append builders, asynchronous `openFile` builders for `Path` and `PathHandle`, protected `openFileWithOptions` execution hooks, and multipart uploader builder creation. Fields include default-FS keys, the shared `LOG`, shutdown-hook priority, trash/user-home prefixes, and per-instance `statistics`.

`FileUtil` is a static helper collection for converting `FileStatus` values to `Path`s, recursive delete and delete-on-exit, symlink target reads, filesystem-to-filesystem/local copy overloads, shell-path conversion including secure shell paths, disk usage, zip/tar extraction, local symlink/chmod/chown/permission helpers, portable read/write/execute checks, temp file creation, file replacement, checked wrappers around `File.listFiles()` and `File.list()`, manifest classpath jar creation, jar wildcard expansion, filesystem comparison, and convenience `write` overloads for bytes, line iterables, and char sequences through `FileSystem` or `FileContext`.

`FilterFileSystem` wraps an underlying `FileSystem` in protected `fs` with optional `swapScheme`. Its API mirrors the classic `FileSystem` surface and delegates URI handling, qualification, open/create/append/concat, path handles, listing, rename/delete/truncate, local copy staging, usage/defaults/status, permission/owner/time changes, symlinks, checksums, snapshots, ACLs, xattrs, storage policies, trash roots, builder APIs, protected open-file option hooks, and path capability checks.

`FSBuilder<S,B>` defines the generic builder contract used by filesystem operations. It has typed optional `opt()` and mandatory `must()` overloads for strings, primitives, and string arrays, plus `build()`. The key semantic distinction is that unsupported optional keys may be ignored, while unsupported mandatory keys are expected to make `build()` fail with `IllegalArgumentException`.

`FsConstants` exposes filesystem constants for local, FTP, viewfs, viewfs-overload target implementation patterns, viewfs type, and symlink traversal limits. These constants bind API consumers to Hadoop's scheme names and path-resolution guardrails.

`FSDataInputStream` is a buffered `DataInputStream` wrapper implementing `Seekable`, `PositionedReadable`, byte-buffer readable interfaces, file-descriptor access, readahead/drop-behind controls, enhanced byte-buffer access, unbuffering, `StreamCapabilities`, byte-buffer positioned reads, vectored reads, and `IOStatisticsSource`. `FSDataOutputStream` wraps an `OutputStream` as a `DataOutputStream`, implements `Syncable`, drop-behind, stream capabilities, IO statistics, and `Abortable`, and exposes `getPos`, `hflush`, `hsync`, `abort`, and nested-stream statistics behavior.

`FSDataOutputStreamBuilder` is the abstract create/append builder for `FSDataOutputStream`. It tracks filesystem, permission, buffer size, replication, block size, recursive parent creation, progress callback, create/overwrite/append flags, checksum options, generic optional/mandatory options inherited from `AbstractFSBuilderImpl`, and abstract `build()`. Its docs explicitly prefer implementation-agnostic option keys over `instanceof`-based filesystem branching.

`FSInputStream` is the abstract seekable input base for filesystem streams. It requires `seek`, `getPos`, and `seekToNewSource`, supplies positioned read validation, `readFully` loops, and a `toString` that can include `IOStatisticsSource` data from subclasses.

`FsServerDefaults` and `FsStatus` are value/serialization APIs. Server defaults expose block size, checksum bytes, write packet size, replication, file buffer size, data-transfer encryption, trash interval, checksum type, key provider URI, and default storage policy ID. `FsStatus` implements `Writable` for capacity, used, and remaining filesystem space.

`FutureDataInputStreamBuilder` extends `FSBuilder<CompletableFuture<FSDataInputStream>, ...>` for async-capable open operations and accepts an optional `FileStatus` hint. `Options.OpenFileOptions` provides the standard open-file option keys for length, split start/end, buffer size, read policy, and supported read-policy values such as adaptive, default, random, sequential, vector, and whole-file.

`GlobalStorageStatistics`, `StorageStatistics`, and `StorageType` expose storage telemetry and storage-media APIs. Global statistics are synchronized `get`, `put`, `reset`, and iteration operations keyed by name. `StorageStatistics` is an abstract named statistics source with long-statistic iteration, individual lookup, tracking checks, and reset. `StorageType` enumerates storage media behavior through transient, quota-supporting, movable, parsing, and filtered-list APIs.

`GlobFilter`, `PathFilter`, `Path`, `PathHandle`, and `InvalidPath*` APIs cover path matching, naming, validation, serialization, and stable/opaque references. `Path` constructors accept strings, URIs, and parent/child forms; methods strip scheme/authority, merge paths, detect Windows absolute paths, resolve owning filesystems, inspect path structure, compare/equal/hash paths, qualify paths, and validate deserialized objects. `PathHandle` serializes opaque file references to byte arrays/byte buffers and can fail later through `InvalidPathHandleException` if encoded constraints no longer hold.

`LocalFileSystem` and `RawLocalFileSystem` are local implementations. `LocalFileSystem` is a checksumed wrapper over a raw filesystem and exposes local path conversion, local copy methods, checksum failure handling, and symlink support. `RawLocalFileSystem` is the direct `file:` implementation with open/create/append/createNonRecursive, local output stream hooks, concat/rename/truncate/delete/list/mkdir/status, working directory, owner/permission/times using platform commands, path handles, symlink APIs, and path capability checks.

`LocatedFileStatus`, `PartialListing`, `PartHandle`, and `MultipartUploader` support listing and upload workflows. `LocatedFileStatus` extends `FileStatus` with block locations and constructors including ACL/encryption/erasure-coded flags and generic attr flags. `PartialListing` represents one batch of a potentially multi-batch listing and may rethrow a stored `RemoteException` on `get()`. `PartHandle` is the opaque serializable multipart part reference. `MultipartUploader` is an async API for start, part upload, complete, abort, and best-effort abort-under-path operations, and also advertises IO statistics.

`PositionedReadable`, `Seekable`, `ReadOption`, `StreamCapabilities`, `StreamCapabilitiesPolicy`, and `Syncable` define stream contracts. Positioned reads must not alter the current stream offset and are documented as thread-safe requirements, though not all filesystems satisfy them. Vectored reads attach futures to file ranges and may leave stream position undefined. Stream capabilities use lowercase string constants for optional features such as `hflush`, `hsync`, readahead, drop-behind, unbuffer, byte-buffer reads, IO statistics, vectored IO, abortable streams, and IO statistics contexts. `Syncable` separates `hflush` visibility from `hsync` disk-flush semantics.

`QuotaUsage` is a directory quota value class with namespace quota/count, space consumed/quota, per-`StorageType` quotas/consumption, availability checks, equality/hash behavior, CLI header/format helpers, human-readable and storage-type string output. `Trash` is a configured facade around pluggable trash policies, with constructors for default or explicit filesystem, mount/symlink-aware `moveToAppropriateTrash`, `moveToTrash`, checkpoint, expunge, immediate expunge, emptier runnable, and current trash directory lookup. `TrashPolicy` starts at the end of this chunk and includes old/new initialization contracts plus abstract enablement, move, checkpoint, delete checkpoint, and a truncated `deleteCheckpointsImmediately` declaration.

## Control flow and behavioral contracts

The XML has no executable control flow, but the Javadoc captures API-level flow. `FileSystem.openFile(Path|PathHandle)` returns a builder; preconditions and actual open may be deferred to `build()`. Protected `openFileWithOptions` is the implementation hook called by the builder and `DelegateToFileSystem`; the base contract performs a blocking `open(Path, int)` but wraps the outcome in a `CompletableFuture`, so callers must evaluate the future to observe failures. Mandatory unknown open options produce `IllegalArgumentException`; unsupported path handles may fail immediately or when the future is evaluated.

Create and append flow is builder-driven. `FileSystem.createFile(path)` creates an `FSDataOutputStreamBuilder` that overwrites by default, while `appendFile(path)` sets up append. The builder accumulates permission, buffer, replication, block size, progress, recursive parent creation, create/overwrite/append flags, checksum options, and generic options before `build()` asks the filesystem to create or append. Missing parent creation is opt-in via `recursive()`.

`FilterFileSystem` is a delegation flow. Its public surface is intentionally broad because it must pass through new `FileSystem` APIs to its wrapped filesystem. The `FileSystem` docs warn maintainers that adding public/protected methods requires updating `FilterFileSystem`, `ChecksumFileSystem`, HAR tests, and path capability behavior; in particular, `FilterFileSystem.hasPathCapability()` must return false for newly probed capabilities unless support is intentionally known.

`FileUtil.copy` has recursive and destructive behavior. When `deleteSource` is true, source deletion happens as each subtree is copied; a mid-copy failure may leave the source tree partially deleted. Destination-directory handling can return false rather than throw if `mkdirs(dst)` fails. Overwrite only applies to files, not file-over-directory or directory-over-file mismatches.

`FSDataInputStream` delegates capability-specific calls to its wrapped stream. It supports seek and positioned reads, pooled byte-buffer reads, byte-buffer positioned reads, vectored reads, readahead, drop-behind, unbuffer, and IO statistics only when the nested stream supports the relevant interfaces or policies. `FSDataOutputStream` similarly delegates sync, drop-behind, abort, and statistics behavior to the wrapped stream and exposes unsupported-operation paths when unavailable.

`MultipartUploader` flow is explicitly asynchronous and stateful: `startUpload(Path)` returns an upload handle, `putPart()` can run out of order or in parallel and must close the supplied input stream after reading, `complete()` takes a non-empty map of part numbers to handles and returns a `PathHandle`, and `abort()`/`abortUploadsUnderPath()` clean up pending uploads. Abort-under-path is best effort and may miss uploads when listing is eventually consistent.

`Path` flow normalizes URI-like path strings but with unescaped elements and Hadoop-specific handling. FileSystem resolution uses `Path.getFileSystem(Configuration)`, qualification uses filesystem URI and working directory, and deserialization runs `validateObject()` to reject malicious or invalid object streams without a URI.

`Trash.moveToAppropriateTrash()` resolves symlinks or mount points to the actual volume, gets the filesystem for the fully qualified resolved path, and moves the original path into the trash root for that volume. `TrashPolicy.initialize(Configuration, FileSystem)` supersedes the older home-directory based initializer because trash placement cannot always assume `/user/$USER` under HDFS encryption zones.

## State, persistence, and side effects

The JDiff file itself is persistent API metadata used by compatibility checks. Runtime state described by this chunk belongs to the Hadoop APIs, not to the XML.

Persistent filesystem effects include xattr removal/listing, storage policy updates, file create/append/open, multipart uploads, local and remote copy, recursive delete, symlink creation, chmod/chown/permission changes, owner/time updates, directory creation, concat, rename, truncate, trash movement/checkpointing/expunge, path-handle validation, and quota/statistics reporting. Many APIs throw `IOException` and some optional operations throw `UnsupportedOperationException`.

Process-level state appears in statistics and caches. `FileSystem` has per-instance `statistics`, deprecated static statistics maps, global storage statistics, shutdown hook priority, and constants used by shutdown/trash behavior. `GlobalStorageStatistics` is synchronized and stores named providers; `StorageStatistics` objects can reset tracked counters.

Local filesystem state is especially platform-sensitive. `RawLocalFileSystem` maps Hadoop `Path` objects to `java.io.File`, uses host file permissions, can call shell/platform utilities for owner and permission changes, and returns unsorted local listings because it relies on Java `File.list()`. `FileUtil` helpers can create/delete local files, expand archives, generate classpath jars, replace files, and register recursive delete-on-exit work.

Stream state includes current input/output positions, optional read-ahead/drop-behind hints, pooled byte buffers that must be released, unbuffered resources, and vectored read futures attached to ranges. `PositionedReadable.readVectored()` documents that stream position after the call is undefined and that file mutation during a vectored read produces undefined mixed data.

Value classes store serializable metadata snapshots. `FsServerDefaults`, `FsStatus`, `LocatedFileStatus`, `QuotaUsage`, `PartHandle`, and `PathHandle` carry state across process or RPC boundaries; handles are intentionally opaque and may encode constraints checked on later access.

## Dependencies and integration points

These APIs integrate with Hadoop Common filesystem types including `Path`, `FileSystem`, `FileContext`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `FutureDataInputStreamBuilder`, `PathHandle`, `PartHandle`, `UploadHandle`, `MultipartUploaderBuilder`, `RemoteIterator`, `FileRange`, `FsStatus`, `FsServerDefaults`, `BlockStoragePolicySpi`, `StorageStatistics`, `GlobalStorageStatistics`, `StorageType`, `Options`, `CreateFlag`, and `ReadOption`.

Permission, security, and metadata integration points include `FsPermission`, `FsAction`, ACL entry/status classes, `XAttrSetFlag`, `AccessControlException`, `Configuration`, `Configured`, `Progressable`, `IOStatisticsSource`, `IOStatistics`, `ByteBufferPool`, `DataChecksum.Type`, and `RemoteException`.

Java and platform dependencies include `URI`, `File`, `FileDescriptor`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `ByteBuffer`, `EnumSet`, `CompletableFuture`, `IntFunction`, `Iterator`, `Map`, `List`, `Collection`, `Set`, `Serializable`, `Comparable`, `Closeable`, and local shell/platform command behavior for symlink, chmod, chown, archive extraction, and Windows path/permission handling.

Compatibility tooling depends on the structured XML attributes more than implementation code. Any public/protected signature, visibility, deprecation, exception, field, or documentation-contract change in this source API surface can affect JDiff comparisons between Hadoop releases.

## Risks and compatibility notes

This chunk is line-bounded and partial at both ends. It should not be used alone to summarize all of `FileSystem` or `TrashPolicy`; adjacent chunks are needed for complete class coverage.

Builder option handling is compatibility-sensitive. Optional keys may be ignored, but mandatory keys must fail if unsupported or invalid. Filesystem-specific builders must recognize standard `Options.OpenFileOptions` keys even when values are ignored, or generic callers can break.

Asynchronous APIs may still perform blocking work in default implementations. `openFileWithOptions()` returns a `CompletableFuture`, but the base contract performs the open call synchronously before returning a completed/failing future. Callers and tests should not assume background execution unless a concrete filesystem documents it.

Positioned and vectored reads have subtle consistency and concurrency risks. The API requires thread-safe positioned reads, while warning that not all implementations satisfy this. Vectored reads can block normal reads, leave current position undefined, and return undefined data if the file changes during the operation.

`FileUtil` deletion/copy helpers can leave partial results. Recursive delete returns false after partial deletion, and copy with `deleteSource` can delete subtrees as work progresses. Cleanup logic must not assume atomic copy/delete semantics.

Local filesystem behavior varies by platform. Windows path handling, symlink privilege failures, permission checks, execute-bit semantics on directories, unsorted listings, and shell command availability can change behavior even though the public API is stable.

Opaque handles and multipart uploads encode implementation-specific state. `PathHandle` and `PartHandle` equality/serialization must remain stable enough for retries, but `InvalidPathHandleException` is expected when encoded constraints no longer match. Multipart abort-under-path is explicitly best effort and can miss uploads under eventually consistent listing systems.

Trash behavior depends on filesystem resolution, mount points, symlinks, encryption zones, configured policy, and user trash roots. The older `TrashPolicy.initialize(conf, fs, home)` is deprecated because it assumes a home-rooted trash layout that is not always valid.

## Test signals

JDiff validation should confirm the XML remains well-formed and preserves all class/interface boundaries in this line range, including the partial `FileSystem` and partial `TrashPolicy` entries. API compatibility tests should check signatures, visibility, exceptions, field names, and deprecation strings for the covered methods.

Filesystem contract tests should exercise `FileSystem` xattr/storage-policy/trash-root APIs, `hasPathCapability`, global/per-instance statistics, `createFile`, `appendFile`, `openFile(Path)`, `openFile(PathHandle)`, open options, multipart uploader creation, and default unsupported-operation paths.

Wrapper tests should run core operations through `FilterFileSystem` and verify delegation for URI handling, path qualification, open/create/append/list/delete/rename/truncate, local copies, defaults/status, permissions, symlinks, checksums, snapshots, ACLs, xattrs, storage policies, trash roots, builders, and path capability behavior.

Stream tests should cover seek/getPos/readFully, byte-buffer reads, byte-buffer positioned reads, readahead/drop-behind, file descriptor availability, pooled buffer release, unbuffer policy, stream capability strings, IO statistics fallback behavior, hflush/hsync, abortable output streams, and vectored read edge cases.

Local utility tests should cover recursive delete of files/directories/symlinks, partial-failure behavior, archive extraction, secure shell path conversion, chmod/chown/setPermission portability, Windows symlink privilege return code, null-safe listing wrappers, classpath jar generation with environment-variable and wildcard expansion, and write helpers for `FileSystem` and `FileContext`.

Value-object tests should cover `Path` normalization and Windows absolute path detection, deserialization validation, `PathHandle` and `PartHandle` byte serialization/equality, `LocatedFileStatus` block-location equality/hash behavior, `FsStatus` writable round trips, `FsServerDefaults` getters, `QuotaUsage` string/header formatting with storage types, and `StorageType` parsing/filtering.

Trash tests should cover disabled trash, already-in-trash returns, mount/symlink-aware `moveToAppropriateTrash`, checkpoint creation, old checkpoint deletion, immediate expunge, emptier runnable creation for superuser-style cleanup, encryption-zone-aware `TrashPolicy.initialize(conf, fs)`, and legacy initializer compatibility.
