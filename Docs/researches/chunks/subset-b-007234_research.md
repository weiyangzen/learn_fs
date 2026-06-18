# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 12224-18113

## Scope

This chunk is part 3 of the JDiff XML API description for Hadoop Common 3.5.0. It starts in the documentation body for `org.apache.hadoop.fs.FileSystem.create(Path, FsPermission, boolean, int, short, long, Progressable)`, continues through the remainder of `FileSystem`, and then covers complete API entries for `FileUtil`, `FilterFileSystem`, `FsConstants`, `FsServerDefaults`, `FsStatus`, `FutureDataInputStreamBuilder`, `GlobFilter`, `GlobalStorageStatistics`, `InvalidPathException`, `InvalidPathHandleException`, `LocalFileSystem`, `LocatedFileStatus`, `MultipartUploader`, `OpenFileOptions`, `Options`, `ParentNotDirectoryException`, `PartHandle`, and `PartialListing`. It ends inside the deprecated `Path.makeQualified(FileSystem)` method documentation, with the rest of `Path` continuing in the next chunk.

The source is generated API metadata rather than executable implementation. It records public/protected signatures, inheritance, exceptions, visibility, abstract/default status, deprecation notes, fields, and Javadocs. Research here therefore focuses on public API contracts, implementation obligations for Hadoop filesystem providers, and behavior exposed to callers.

## Purpose

The chunk documents the central Hadoop filesystem API layer. The `FileSystem` tail defines the user-facing and implementation-facing contract for creation, append, rename, delete, listing, status lookup, local copy helpers, working directories, checksum and symlink handling, ACL/xattr/snapshot/storage-policy APIs, path capabilities, stream builders, async open, multipart upload creation, and bulk delete creation. The later classes define utility and wrapper APIs around those operations, local filesystem behavior, serializable filesystem metadata, async/multipart option constants, path/listing exceptions, and path-construction behavior.

This section is especially important for compatibility because `FileSystem` is a base class used by HDFS, `LocalFileSystem`, `FilterFileSystem`, object-store connectors, view filesystems, and third-party filesystems. Its class documentation warns that new public/protected APIs must be mirrored or consciously blocked by wrappers such as `FilterFileSystem` and tested by compatibility tests such as `TestFilterFileSystem.MustNotImplement`.

## Important APIs And Types

### `FileSystem` tail

The chunk contains the remainder of `FileSystem` beginning with create overloads:

- `create(...)` overloads accept `Path`, optional `FsPermission`, overwrite booleans or `EnumSet<CreateFlag>`, buffer size, replication, block size, `Progressable`, and optional `Options.ChecksumOpt`.
- `primitiveCreate(...)` and `primitiveMkdir(...)` are protected transition hooks used by `FileContext` after applying umask-derived absolute permissions.
- `createNonRecursive(...)` variants create without making missing parents.
- `createNewFile(Path)` creates a zero-length file but documents that the default implementation is not atomic.
- `append(...)` variants support optional buffer size, progress callback, and `appendToNewBlock`; append is optional and may throw `UnsupportedOperationException`.
- `concat(Path, Path[])`, `setReplication(Path, short)`, abstract `rename(Path, Path)`, protected option-bearing `rename(Path, Path, Options.Rename...)`, `truncate(Path, long)`, and `delete(Path, boolean)` define core mutating operations. Rename atomicity is implementation-dependent, and the protected option-bearing rename default is explicitly non-atomic.
- Status and listing APIs include `exists`, deprecated `isDirectory`/`isFile`, deprecated `getLength`, `getContentSummary`, `getQuotaUsage`, quota setters, `listStatus`, `listStatusBatch`, `listCorruptFileBlocks`, `globStatus`, `listLocatedStatus`, `listStatusIterator`, and recursive `listFiles`.
- Path context APIs include `getHomeDirectory`, `setWorkingDirectory`, `getWorkingDirectory`, `getInitialWorkingDirectory`, and `fixRelativePart`.
- Local transfer APIs include `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, `moveToLocalFile`, `startLocalOutput`, and `completeLocalOutput`.
- Filesystem metadata APIs include `getUsed`, `getBlockSize`, `getDefaultBlockSize`, `getDefaultReplication`, abstract `getFileStatus`, `msync`, `access`, `getStatus`, and `getStatus(Path)`.
- Symlink/checksum APIs include `createSymlink`, `getFileLinkStatus`, `supportsSymlinks`, `getLinkTarget`, `resolveLink`, `getFileChecksum(Path)`, `getFileChecksum(Path,long)`, `setVerifyChecksum`, and `setWriteChecksum`.
- Security and metadata mutation APIs include `setPermission`, `setOwner`, `setTimes`, snapshot create/rename/delete, ACL mutation and lookup, xattr mutation and lookup, storage-policy APIs, trash root lookup, and path capability probing.
- Static/global APIs include `getFileSystemClass`, `getStatistics` overloads, `getAllStatistics`, `clearStatistics`, `printStatistics`, `areSymlinksEnabled`, `enableSymlinks`, `getStorageStatistics`, and `getGlobalStorageStatistics`.
- Builder/newer APIs include `createDataOutputStreamBuilder`, `createFile`, `appendFile`, `openFile(Path)`, `openFile(PathHandle)`, protected `openFileWithOptions(...)` for `Path` and `PathHandle`, `createDataInputStreamBuilder`, `getEnclosingRoot`, `createMultipartUploader`, and `createBulkDelete`.

Important fields in this tail are public constants `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and protected instance `statistics`. `LOG` is explicitly called out as widely used in Hadoop FS code and tests and must be changed with care.

### `FileUtil`

`FileUtil` is a static utility collection for local files, Hadoop `FileSystem` paths, archives, permissions, process classpaths, and small write helpers. Important APIs include:

- `stat2Paths(...)` converts `FileStatus[]` to `Path[]`, with an overload that returns a default path when statuses are null.
- Recursive local deletion helpers `fullyDeleteOnExit`, `fullyDelete(File)`, `fullyDelete(File, boolean)`, `fullyDeleteContents(...)`, and deprecated `fullyDelete(FileSystem, Path)`. The docs distinguish regular files, symlinks to files, symlinks to directories, and recursive directory deletion; partial deletion is possible when false is returned.
- `readLink(File)` reports symlink targets or an empty string on errors/non-links.
- `copy(...)` overloads copy between filesystems, from local files into filesystems, and from filesystems to local files. The recursive copy contract warns that when `deleteSource` is true, source directories may be partially deleted if the operation fails mid-tree.
- Local file and shell helpers include `isRegularFile`, `makeShellPath`, `makeSecureShellPath`, `getDU`, `symLink`, `chmod`, `setOwner`, `setReadable`, `setWritable`, `setExecutable`, `canRead`, `canWrite`, `canExecute`, and `setPermission`.
- Archive helpers `unZip(...)` and `unTar(...)` accept streams/files and target directories; untar may throw `InterruptedException` and `ExecutionException` for command/task failures.
- `createLocalTempFile` creates a temp file adjacent to a base file and optionally registers delete-on-exit.
- `replaceFile`, safe `listFiles(File)`, and safe `list(File)` wrap fragile `java.io.File` APIs so callers get exceptions rather than nulls.
- `createJarWithClassPath(...)` builds a manifest-only classpath jar and expands environment variables and wildcard jar entries; this is primarily for platform command-line length limits.
- `getJarsInDirectory(...)`, `compareFs`, eight `write(...)` overloads for `FileSystem`/`FileContext`, byte arrays, lines, char sequences, charset/UTF-8, `rename`, `maybeIgnoreMissingDirectory`, and `checkFSSupportsEC`.

The `SYMLINK_NO_PRIVILEGE` constant is exposed for symlink creation results.

### `FilterFileSystem`

`FilterFileSystem` extends `FileSystem` and wraps another `FileSystem` in protected field `fs`, with optional protected `swapScheme`. The class doc says it passes all requests to the contained filesystem unless subclasses override behavior. The chunk lists pass-through implementations for initialization, URI/canonical URI handling, path qualification, path checking, block locations, path resolution, open/create/append/concat, path handles, listing, delete, rename, truncate, copy, status/defaults, symlink/checksum behavior, metadata mutation, ACL/xattr/snapshot/storage-policy APIs, builder APIs, async open, enclosing root, and path capability probing.

This wrapper is a major integration point. Any new `FileSystem` API must be considered for pass-through, explicit unsupported behavior, and capability reporting. The `FileSystem` class doc in this chunk specifically warns that `FilterFileSystem#hasPathCapability(Path, String)` must return false for newly probed capabilities unless the wrapper truly supports them.

### Filesystem constants and serializable metadata

`FsConstants` exposes constants for local, FTP, and viewfs schemes, maximum symlink path links, and the viewfs-overload target implementation pattern.

`FsServerDefaults` implements `Writable` and transports server-provided defaults to clients. It has constructors for block size, bytes per checksum, write packet size, replication, file buffer size, encrypted transfer, trash interval, checksum type, key provider URI, default storage policy id, and snapshot-trash-root enablement. Getters expose each value, and `write(DataOutput)`/`readFields(DataInput)` define Hadoop serialization.

`FsStatus` also implements `Writable` and stores filesystem capacity, used bytes, and remaining bytes, with getters plus `write`/`readFields`.

`LocatedFileStatus` extends `FileStatus` and adds `BlockLocation[]`. Constructors wrap an existing `FileStatus` or build full file metadata with block locations. `getBlockLocations`, `setBlockLocations`, `compareTo`, `equals`, and `hashCode` define how block locality participates in status objects.

`PartialListing<T>` represents one batch of a listing. It stores the listed `Path` and either a `List<T>` result or a `RemoteException`; `get()` behaves like a future by returning the list or throwing the recorded exception.

### Async open, multipart upload, and option constants

`FutureDataInputStreamBuilder` extends `FSBuilder<CompletableFuture<FSDataInputStream>, FutureDataInputStreamBuilder>`. `build()` returns a `CompletableFuture` and may throw argument, unsupported, or I/O errors before or while constructing the future. `withFileStatus(FileStatus)` is optional advisory input that implementations may use or ignore. Its docs explain the `opt` versus `must` builder contract: optional unknown options may be ignored; mandatory unknown/unsupported options must trigger `IllegalArgumentException`.

`MultipartUploader` is an async interface for object-store-style multipart writes. It exposes:

- `startUpload(Path)` returning `CompletableFuture<UploadHandle>`.
- `putPart(Path, InputStream, int partNumber, UploadHandle, long length)` returning `CompletableFuture<PartHandle>`.
- `complete(Path, Map<Integer, PartHandle>, UploadHandle)` returning `CompletableFuture<PathHandle>`.
- `abort(Path, UploadHandle)` returning `CompletableFuture<Void>`.
- `abortUploadsUnderPath(Path)` returning `CompletableFuture<Integer>` and warning that stores may leave partial uploads after application failure; callers should expect eventual cleanup.

`PartHandle` is a serializable opaque multipart part identifier. It provides default `toByteArray()`, abstract `bytes()`, and abstract `equals(Object)`.

`OpenFileOptions` defines standard option keys for `openFile()` and related builders: file length, split start/end, buffer size, footer cache, read policy, standard-option set, read policy values for adaptive, Avro, columnar, CSV, default, HBase, JSON, ORC, Parquet, random, sequential, vector, whole-file, the set of all read policies, and the EC policy option.

`Options` is a final public namespace class for filesystem operation options. Nested types are not in this chunk, but many APIs in this chunk refer to `Options.Rename`, `Options.ChecksumOpt`, `Options.HandleOpt`, and `Options.OpenFileOptions`.

### Filters, statistics, exceptions, local filesystem, and path prefix

`GlobFilter` implements `PathFilter` for POSIX glob patterns with brace expansion and optional user-supplied filter. Constructors throw `IOException` for invalid patterns; `hasPattern()` reports whether the input contained glob syntax; `accept(Path)` applies the filter.

`GlobalStorageStatistics` is modeled as a final enum and stores global `StorageStatistics` instances. `get`, `put`, `reset`, and `iterator` are synchronized. `put` creates or returns statistics by name through a provider and may throw runtime exceptions if the provider returns null or a statistic with the wrong name.

`InvalidPathException` extends `HadoopIllegalArgumentException` for invalid path strings or filesystem-specific invalidity. `InvalidPathHandleException` extends `IOException` for `PathHandle` constraints that no longer hold. `ParentNotDirectoryException` extends `IOException` when a specified parent is not a directory.

`LocalFileSystem` extends `ChecksumFileSystem`. The API exposes initialization, `file` scheme reporting, raw filesystem access, `pathToFile(Path)`, copy-to/from-local behavior, checksum failure reporting, symlink support, symlink creation, link status, and link target lookup.

The chunk begins `Path`, which implements `Comparable<Path>`, `Serializable`, and `ObjectInputValidation`. It includes constructors from parent/child strings and paths, raw strings, URIs, and scheme/authority/path components. Static helpers strip scheme/authority, merge paths while preserving the first path's scheme/authority, and detect Windows absolute path strings. Instance methods in this chunk cover `toUri`, resolving a `FileSystem` from configuration, absolute/root/name/parent checks, optional parent lookup, suffixing, `toString`, equality, hash, comparison, depth, and the deprecated `makeQualified(FileSystem)` signature whose documentation continues past this chunk boundary.

## Control Flow And Behavioral Contracts

Most control flow is described as delegation, default implementation, or implementation responsibility:

- `FileSystem` overloads normalize caller convenience into lower-level operations: create variants funnel toward permission/create-flag/checksum-aware creation; append overloads add default buffer/progress/new-block options; deprecated status helpers are wrappers around `getFileStatus`; listing APIs either materialize arrays or return `RemoteIterator`/partial batches.
- `FileSystem` mutators intentionally expose weaker, implementation-dependent guarantees. `rename` and `createNewFile` default implementations are not necessarily atomic; append and truncate may be unsupported or asynchronous; set-replication may return success even on filesystems that do not implement replication.
- `deleteOnExit`, `cancelDeleteOnExit`, and `processDeleteOnExit` provide VM-lifetime cleanup flow. These APIs are stateful, and cleanup runs later against queued paths.
- `FileUtil.copy` recursively walks/copies source trees, optionally deleting source items as it progresses. Failure after partial progress can leave both source and destination in mixed states.
- `FilterFileSystem` control flow is wrapper delegation: most calls are forwarded to `fs`, with path/URI scheme adaptation available via `swapScheme`.
- `FutureDataInputStreamBuilder` and multipart upload APIs are asynchronous control-flow contracts. Some validation may fail immediately, while actual stream creation/upload completion is represented by `CompletableFuture`.
- `PartialListing.get()` defers remote listing failure until the consumer asks for the batch result.
- `GlobalStorageStatistics` serializes access to the global registry with synchronized methods.
- `Path` construction and helper methods normalize URI/path representations and compare paths by their string/URI identity.

## State And Persistence Behavior

The visible state contracts include:

- `FileSystem.statistics` and static/global statistics registries persist counters across filesystem operations and tests. Static `getStatistics`, `clearStatistics`, and `printStatistics` operate on shared state.
- `FileSystem` tracks working directory state per instance. Relative paths are resolved against that state through qualification/fixup helpers.
- `deleteOnExit` registers paths for later deletion and must coordinate with shutdown hooks (`SHUTDOWN_HOOK_PRIORITY` is public).
- `setVerifyChecksum` and `setWriteChecksum` toggle per-filesystem checksum behavior where implementations honor them.
- `FsServerDefaults`, `FsStatus`, and `LocatedFileStatus` are metadata value objects with Hadoop `Writable` or inherited serialization semantics. Changing field order or serialization would break wire/storage compatibility.
- `MultipartUploader` persists upload sessions externally in backing stores through `UploadHandle` and `PartHandle`. The docs explicitly warn that partial uploads may remain after application failure and may require cleanup.
- `PartHandle` byte serialization is opaque; callers must not interpret it beyond equality/round-trip use.
- `OpenFileOptions` constants are persistent API strings used in builder parameter maps and path capability discovery.
- `GlobalStorageStatistics` keeps JVM-global named statistics and must guard consistency when providers create entries.
- `Path` is serializable and validates deserialized objects via `ObjectInputValidation` in later `Path` methods outside this chunk; this chunk already establishes the serializable path object surface.

## Dependencies And Integration Points

This chunk depends heavily on Hadoop common types:

- Filesystem model: `Path`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `ContentSummary`, `QuotaUsage`, `FsStatus`, `FsServerDefaults`, `BlockStoragePolicySpi`, `PathHandle`, `UploadHandle`, `PartHandle`, `BulkDelete`, and builders.
- Permissions/security: `FsPermission`, `AclEntry`, `AclStatus`, `FsAction`, `AccessControlException`, owner/group strings, and xattr flags.
- I/O and serialization: `FSDataInputStream`, `FSDataOutputStream`, `DataInput`, `DataOutput`, `Writable`, `InputStream`, `RemoteIterator`, `CompletableFuture`, and `Progressable`.
- Configuration and runtime: `Configuration`, `URI`, `UserGroupInformation`-related context from adjacent APIs, `DataChecksum.Type`, SLF4J logging, and Java local file APIs.
- Wrapper and compatibility layers: `FileContext`, `AbstractFileSystem`, `ChecksumFileSystem`, `FilterFileSystem`, `LocalFileSystem`, HDFS, object-store connectors, viewfs, and third-party filesystem implementations.

Key integration points are capability probing (`hasPathCapability`, builder `must` options, `checkFSSupportsEC`), wrapper propagation (`FilterFileSystem`), object store semantics (`CreateFileOptionKeys` from the previous chunk plus multipart/open-file options here), and compatibility with external projects called out in the `FileSystem` docs such as HBase and Hive shims.

## Risks And Edge Cases

- The chunk starts and ends mid-API documentation. Merge must join this with adjacent chunk reports for complete `FileSystem.create(...)` and `Path.makeQualified(...)` docs.
- JDiff XML may include generated or misspelled parameter names, such as `FilterFileSystem.primitiveMkdir` showing `abdolutePermission`; research consumers should treat it as API metadata evidence, not source-of-truth implementation spelling without checking Java source.
- `FileSystem` API changes can break wrappers. `FilterFileSystem`, `ChecksumFileSystem`, HAR tests, and downstream shims must be updated when new methods or capabilities are introduced.
- Several operations return booleans rather than throwing for all failures (`delete`, `rename`, `setReplication`, copy helpers), creating ambiguity between unsupported, absent, and partial-success states.
- Non-atomic defaults for `createNewFile` and option-bearing `rename` can surprise callers expecting POSIX/HDFS semantics.
- Recursive delete/copy utilities can leave partial state on failure, especially with `deleteSource=true`, permission adjustment, or symlink handling.
- Symlink handling is security-sensitive. `FileUtil` distinguishes deleting symlinks from deleting targets for `fullyDelete`, but `fullyDeleteContents` follows symlinks to directories and deletes target contents.
- Archive extraction helpers (`unZip`, `unTar`) and shell helpers (`symLink`, `chmod`, `setOwner`, shell path construction) carry platform, permission, subprocess, and path-injection risks; `makeSecureShellPath` exists to reduce script injection risk.
- Async builders and multipart uploads split validation/completion timing across immediate exceptions and future failures. Partial uploads can leak storage if abort/cleanup is not called after failures.
- `OpenFileOptions` strings are public compatibility surface. Renaming or changing accepted values would break clients that pass options through generic builders.
- `GlobalStorageStatistics` is synchronized but JVM-global; tests must clear/reset state to avoid cross-test interference.
- `Path` constructors and Windows path detection are portability-sensitive, especially around URI scheme/authority, relative paths, and drive-letter interpretation.

## Test Signals

Useful tests and validation signals for this API area include:

- JDiff/API compatibility checks should detect signature, visibility, exception, deprecation, and constant changes in this XML.
- `FileSystem` contract tests should cover create/createNonRecursive/primitiveCreate permission semantics, append support flags, rename overwrite behavior and atomicity claims, delete return values, truncate completion behavior, listing/glob/status behavior, checksum toggles, symlink support, ACL/xattr/storage-policy support, and path capability reporting.
- Wrapper tests should assert `FilterFileSystem` delegates every supported `FileSystem` method and deliberately returns false/unsupported for unimplemented capabilities. The class doc explicitly references `TestFilterFileSystem.MustNotImplement`.
- Local filesystem tests should cover `LocalFileSystem` scheme, raw filesystem conversion, symlink behavior, checksum failure reporting, and local copy direction semantics.
- `FileUtil` tests should exercise symlink deletion versus target deletion, partial recursive copy/delete failure behavior, permission fallback, archive extraction, classpath jar creation with wildcards/environment variables, safe list wrappers, and `maybeIgnoreMissingDirectory` behavior for inconsistent listings.
- Serialization round-trip tests are needed for `FsServerDefaults`, `FsStatus`, `LocatedFileStatus`, `PartHandle` implementations, and adjacent `Path` serialization validation.
- Async builder tests should distinguish optional and mandatory options, immediate validation exceptions, future-completion exceptions, `withFileStatus` advisory behavior, and `OpenFileOptions` read-policy handling.
- Multipart uploader tests should cover start/put/complete/abort flow, part-number ordering, invalid handle failures, cleanup under a path, and leaked multipart state after simulated application failure.
- Statistics tests should verify per-filesystem statistics, global storage statistics registration/reset/iteration, and no cross-test state bleed after `clearStatistics`/`reset`.
