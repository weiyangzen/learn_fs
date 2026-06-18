# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml lines 5874-11915

## Scope

This chunk is a JDiff API description for Hadoop Common 2.7.2, not executable Java source. It covers the tail of `org.apache.hadoop.fs.FileContext`, then the public API metadata for core `org.apache.hadoop.fs` filesystem abstractions through the beginning of `Syncable`. The chunk includes `FileStatus`, most of `FileSystem`, `FileUtil`, `FilterFileSystem`, stream wrappers, filesystem status/default-value carriers, path/filter interfaces, local filesystem implementations, storage media enums, and the first `Syncable` methods. It ends inside `Syncable.hsync()`, so final details of that interface continue in the next chunk.

## Purpose

The file records the stable client-facing Hadoop filesystem API surface for compatibility comparison. In this range, the API describes how callers discover and instantiate filesystems, qualify and resolve paths, read and write data streams, create, append, rename, truncate, delete, list, glob, snapshot, ACL, xattr, checksum, symlink, and local-copy operations, and inspect metadata such as `FileStatus`, block locations, capacity, server defaults, and storage types.

For research purposes, this chunk is best read as a contract map. Method entries expose signatures, visibility, abstract/deprecated status, declared exceptions, and documentation promises. Implementations live in Java classes elsewhere, but this XML defines the public and protected behavior that downstream Hadoop users, filesystem implementations, and compatibility tests depend on.

## Important APIs, Types, and Functions

### FileContext tail

- `FileContext.deleteOnExit(Path)` marks an existing path for JVM-shutdown deletion and documents access-control, unsupported-filesystem, IO, and RPC-side failure modes.
- `FileContext.resolve(Path)` and `resolveIntermediate(Path)` are protected symlink-resolution helpers, with the latter resolving only components before the final path segment.
- `FileContext.getStatistics(URI)`, `clearStatistics()`, `printStatistics()`, and `getAllStatistics()` expose per-filesystem statistics keyed by URI scheme and authority.
- ACL operations `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, and `getAclStatus` define merge, removal, replacement, and read behavior for file and directory ACLs.
- XAttr operations `setXAttr`, `getXAttr`, `getXAttrs`, `removeXAttr`, and `listXAttrs` define namespaced extended-attribute access. Names must use a namespace prefix such as `user.` and visibility is permission-limited.
- `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY` expose default permission and shutdown-hook constants. The docs note `DEFAULT_PERM` is retained for compatibility after HADOOP-9155 split file and directory defaults.
- The class doc defines the `FileContext` model: default filesystem, working directory, URI-qualified/slash-relative/working-directory-relative paths, umask handling, and server-side defaults for home directory, replication, block size, buffers, encryption, and checksum options.

### Metadata carriers

- `FileStatus` implements `Writable` and `Comparable`. It carries length, type, replication, block size, modification/access times, permission, encryption state, owner, group, path, and optional symlink target.
- `FileStatus.isDir()` is deprecated in favor of `isFile()`, `isDirectory()`, and `isSymlink()`.
- `FileStatus.write(DataOutput)` and `readFields(DataInput)` make the object serializable through Hadoop's `Writable` contract.
- `FileStatus.compareTo`, `equals`, and `hashCode` are path-based according to the docs, so equality is not a full metadata comparison.
- `LocatedFileStatus` extends `FileStatus` with `BlockLocation[]`, giving listing callers file metadata plus block placement.
- `FsServerDefaults` is a writable carrier for server-side defaults: block size, bytes per checksum, write packet size, replication, file buffer size, encrypted transfer flag, trash interval, and checksum type.
- `FsStatus` is a writable capacity snapshot with `capacity`, `used`, and `remaining`.

### FileSystem core

- `FileSystem` is the abstract base class for local and distributed filesystems. It extends `Configured` and implements `Closeable`.
- Instantiation and caching are exposed through `get(URI, Configuration)`, `get(Configuration)`, `get(URI, Configuration, user)`, `newInstance(...)`, `newInstanceLocal(Configuration)`, `getLocal(Configuration)`, `closeAll()`, and `closeAllForUGI(UserGroupInformation)`.
- Default URI handling is exposed through `getDefaultUri(Configuration)` and `setDefaultUri(Configuration, URI/String)`. Scheme resolution uses configuration keys of the form `fs.<scheme>.class`.
- Filesystem identity and path binding APIs include `initialize(URI, Configuration)`, `getScheme()`, abstract `getUri()`, `getCanonicalUri()`, `canonicalizeUri(URI)`, `getDefaultPort()`, `checkPath(Path)`, `makeQualified(Path)`, `getFSofPath(Path, Configuration)`, and deprecated `getName()`/`getNamed()`.
- Creation APIs include many overloads of `create(...)`, abstract permission-aware `create(Path, FsPermission, boolean, int, short, long, Progressable)`, `create(Path, FsPermission, EnumSet<CreateFlag>, ..., ChecksumOpt)`, protected `primitiveCreate(...)`, `createNonRecursive(...)`, and `createNewFile(Path)`.
- Data mutation APIs include abstract `append(Path, int, Progressable)`, `concat(Path, Path[])`, `setReplication(Path, short)`, abstract `rename(Path, Path)`, protected option-based `rename(Path, Path, Options.Rename...)`, `truncate(Path, long)`, abstract `delete(Path, boolean)`, and deprecated single-argument `delete(Path)`.
- Lifecycle deletion APIs include `deleteOnExit(Path)`, `cancelDeleteOnExit(Path)`, and protected `processDeleteOnExit()`. The docs distinguish `FileSystem` close/JVM shutdown behavior from immediate delete.
- Query/list APIs include `exists`, `isDirectory`, `isFile`, deprecated `getLength`, `getContentSummary`, abstract `listStatus(Path)`, filtered and multi-path `listStatus` overloads, `globStatus`, `listLocatedStatus`, `listStatusIterator`, and recursive `listFiles`.
- Local copy APIs include `copyFromLocalFile`/`moveFromLocalFile` overloads, `copyToLocalFile`/`moveToLocalFile`, `startLocalOutput`, and `completeLocalOutput`.
- Default value and status APIs include `getUsed`, `getBlockSize`, `getDefaultBlockSize`, `getDefaultReplication`, `getServerDefaults`, `getFileStatus`, and `getStatus`.
- Integrity and stream behavior APIs include `getFileBlockLocations`, `getFileChecksum(Path[, length])`, `setVerifyChecksum`, and `setWriteChecksum`.
- Namespace and permission APIs include `setPermission`, `setOwner`, `setTimes`, `access(Path, FsAction)`, symlink operations, snapshot operations, ACL operations, and xattr operations.
- Static statistics APIs include synchronized `getStatistics`, `getAllStatistics`, `clearStatistics`, and `printStatistics`, plus class lookup via `getFileSystemClass`.
- Constants include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `LOG`, `SHUTDOWN_HOOK_PRIORITY`, and protected instance `statistics`.

### Utility and wrapper APIs

- `FileUtil` contains local and cross-filesystem helpers: `stat2Paths`, recursive delete helpers, symlink target read, cross-filesystem `copy`, `copyMerge`, local-to-filesystem and filesystem-to-local copy, shell-path conversion, local disk usage, zip/tar extraction, symlink/chmod/chown wrappers, portable permission checks/setters, temp-file creation, file replacement, safe `File.listFiles()` and `File.list()` wrappers, and classpath-jar creation.
- `FileUtil.fullyDelete` explicitly distinguishes symlink-to-file, symlink-to-directory, file, and normal-directory behavior. `fullyDeleteContents` deletes contents and follows a symlinked directory's target contents, a materially different contract.
- `FilterFileSystem` extends `FileSystem` and wraps another filesystem in protected `fs`, optionally transforming schemes with `swapScheme`. The class contract says it delegates all `FileSystem` methods to the contained filesystem unless subclasses override.
- `FsConstants` exposes filesystem URI/scheme constants such as local FS, FTP, viewfs, and `MAX_PATH_LINKS`.

### Streams, paths, filters, and local filesystems

- `FSDataInputStream` wraps an `FSInputStream` in `DataInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, and `CanUnbuffer`. Its contract includes seek, current position, positional read, readFully with EOF semantics, alternate-source seek, byte-buffer reads, enhanced buffer access/release, readahead/drop-behind hints, and unbuffering.
- `FSDataOutputStream` wraps `OutputStream` in `DataOutputStream`, implements `Syncable` and `CanSetDropBehind`, tracks output position, and exposes `sync`, `hflush`, `hsync`, close, and drop-behind hints.
- `FSError` is an `Error` for unexpected native filesystem failures presumed to reflect disk errors.
- `GlobFilter` implements `PathFilter` using POSIX glob patterns with brace expansion and optional user filter composition.
- `Path` represents Hadoop filesystem paths as URI-like names. Constructors support parent/child combinations, strings, URIs, and scheme/authority/path components. Helpers include scheme/authority stripping, merge, Windows absolute-path detection, URI conversion, filesystem lookup, absoluteness/root/name/parent/suffix/depth checks, qualification, and comparable/string/equality behavior. Constants include slash separator, current directory, and a `WINDOWS` flag.
- `PathFilter.accept(Path)` is the listing/globbing predicate interface.
- `PositionedReadable` defines non-mutating positional reads and readFully calls.
- `Seekable` defines cursor-changing `seek(long)` and `getPos()`.
- `ReadOption` is an enum for read options; the actual enum constants are not visible in this JDiff snippet.
- `StorageType` is an enum for storage media, with helpers for transient status, type-quota support, movability, list views, parsing by int/string, `DEFAULT`, and `EMPTY_ARRAY`.
- `LocalFileSystem` extends `ChecksumFileSystem`, exposes `getRaw()`, local path conversion, local copy overrides, checksum-failure reporting that moves files to a bad-file directory, and symlink support.
- `RawLocalFileSystem` extends `FileSystem` and implements raw local disk operations: path conversion, URI/init, open/append/create streams, non-recursive create, rename, truncate, delete, list, mkdirs, working/home directories, status, local-output staging, owner/permission/timestamp changes, symlinks, and link-status/target APIs.

## Control Flow

The XML does not contain method bodies, but the API contracts imply several important call flows.

Filesystem acquisition begins with a URI and `Configuration`. `FileSystem.get` resolves a scheme to a configured implementation class, constructs or retrieves a cached filesystem for the scheme/authority/user, then calls `initialize(URI, Configuration)`. `newInstance` variants bypass the shared cache by returning unique configured instances. Default filesystem selection flows through `fs.defaultFS`/`FS_DEFAULT_NAME_KEY`, and path qualification binds relative or slash-relative paths to the selected URI.

File creation flows from convenience `create` overloads to the abstract permission-aware creation method or protected `primitiveCreate`. The overload set collects defaults for buffer size, replication, block size, progress reporting, create flags, permissions, and checksum options. `primitiveMkdir` similarly exists to support `FileContext` after umask processing, so permissions passed there are documented as absolute.

Read flows compose `FileSystem.open` with `FSDataInputStream`. Consumers can perform sequential reads inherited from `DataInputStream`, reposition with `seek`, perform positional reads that do not necessarily change the stream cursor, use `readFully` for exact-length reads, request alternate data sources, and use byte-buffer or enhanced byte-buffer access if the implementation supports it.

Write flows compose `create` or `append` with `FSDataOutputStream`. `getPos` reports output offset; `hflush` makes client-buffered data visible to new readers; `hsync` is the durable sync contract; deprecated `sync` remains for older callers and forwards conceptually to newer flush/sync semantics.

Listing flows move from `listStatus` to filtered/multi-path convenience wrappers, glob expansion via `GlobFilter`, and located listings that attach block locations. `listStatusIterator` and `listFiles` provide iterator/recursive APIs; docs warn that iterator `hasNext()` or `next()` can surface IO failures after listing has begun.

Delete and shutdown-delete are separate flows. Immediate `delete(Path, recursive)` performs filesystem deletion. `deleteOnExit` records paths for later processing when `FileSystem` instances close during JVM shutdown; `cancelDeleteOnExit` removes that pending state; `processDeleteOnExit` performs recursive deletion of all marked paths.

Wrapper flows in `FilterFileSystem` forward almost every API call to `fs`, preserving the outer API while allowing subclasses to transform behavior. Local wrappers in `LocalFileSystem` add checksum handling over `RawLocalFileSystem`, while `RawLocalFileSystem` maps Hadoop `Path` values to `java.io.File` and local OS operations.

## State and Persistence Behavior

The XML itself is static API metadata consumed by JDiff tooling. The runtime state described by this chunk belongs to the Hadoop filesystem layer:

- `FileSystem` instances hold `Configuration`, URI identity, a protected `statistics` object, checksum verification/write flags, working directory state in implementations, and delete-on-exit registrations. Static caches and statistics tables are process-wide.
- `FileContext` holds namespace context: default filesystem, working directory, and umask. It resolves path forms against that state but depends on filesystem instances for server-side defaults and actual storage.
- `FileStatus`, `LocatedFileStatus`, `FsStatus`, and `FsServerDefaults` are serializable state snapshots. They persist over RPC or serialization through the `Writable` protocol but do not mutate filesystem storage by themselves.
- `Path` stores URI-derived path state and is used as the identity basis for many comparisons. Since `FileStatus.equals`/`hashCode` are path-based, metadata-only changes do not alter equality.
- ACLs, xattrs, snapshots, symlinks, permissions, ownership, timestamps, replication, checksums, and storage policies are persistent filesystem-side state. This chunk defines the client API and exceptions for touching that state; individual filesystem implementations define exact persistence semantics.
- `FileUtil` mutates local disk state for recursive deletion, chmod/chown, symlink creation, archive extraction, replacement, temp files, and permission changes. Some helpers can leave partial results, explicitly documented for recursive delete.

## Dependencies and Integration Points

This API surface depends on core Hadoop and Java types:

- Hadoop configuration and security: `Configuration`, `UserGroupInformation`, `AccessControlException`.
- Hadoop filesystem model: `Path`, `FileStatus`, `BlockLocation`, `ContentSummary`, `RemoteIterator`, `FsPermission`, `FsAction`, `AclStatus`, `CreateFlag`, `Options.Rename`, `Options.ChecksumOpt`, `FileChecksum`, and symlink/snapshot exception types.
- Hadoop IO utilities: `Writable`, `ByteBufferPool`, `DataChecksum.Type`, `Progressable`, stream capability interfaces, and `RemoteIterator`.
- Java platform APIs: `URI`, `File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `ByteBuffer`, `Closeable`, exceptions, arrays, lists, maps, and enum sets.
- Filesystem implementations outside this XML: local, raw local, checksum local, HDFS `DistributedFileSystem`, viewfs, FTP, and any custom implementation configured under `fs.<scheme>.class`.
- RPC-facing behavior is documented for `FileContext` listing/deletion failures, including client/server/unexpected server exception categories when filesystems are accessed over RPC.

## Risks and Edge Cases

- This is compatibility metadata. A signature or deprecation change here may be more important than a small implementation change because downstream applications and third-party filesystems compile against these contracts.
- `FileStatus.equals` and `hashCode` being path-based can surprise callers expecting length, type, permission, owner, or timestamp to participate in equality.
- `FileSystem.rename(Path, Path)` declares a simple boolean contract, while the protected `rename` with options documents non-atomic default behavior and overwrite edge cases. Implementations can vary materially in atomicity.
- `truncate(Path, long)` can return `false` to indicate asynchronous block-length adjustment. Callers must not assume the file is immediately appendable after every successful truncate call.
- `deleteOnExit` stores process-level deferred deletion state. Long-running clients can accumulate state, and shutdown deletion can recursively remove paths long after the initiating code has moved on.
- Recursive local deletion helpers document partial deletion on failure. Symlink behavior differs between `fullyDelete` and `fullyDeleteContents`, creating a sharp edge for cleanup code.
- `FileUtil.symLink`, `chmod`, `setOwner`, and shell path helpers integrate with platform commands and Windows-specific behavior. Security privileges and path quoting are likely failure points.
- XAttr APIs require namespace-prefixed names and return only attributes visible to the logged-in user. Tests must account for permission filtering rather than assuming all xattrs are visible.
- ACL `setAcl` must include base user/group/other entries for permission-bit compatibility; missing base entries are a likely validation failure in implementations.
- `FSDataInputStream` exposes optional capability interfaces. Implementations may throw `UnsupportedOperationException` for readahead, drop-behind, or enhanced byte-buffer reads.
- `FilterFileSystem` pass-through behavior means wrapper subclasses must override every operation whose semantics they need to alter, including newer ACL/xattr/snapshot/symlink methods.
- The chunk ends inside `Syncable`; any final `hsync` documentation and later filesystem APIs must be reconciled with the next chunk before making whole-file conclusions.

## Test Signals

Useful tests around this API surface should include:

- JDiff/API compatibility checks that verify constructors, method signatures, visibility, deprecation strings, exceptions, implemented interfaces, and fields for every type in this chunk.
- `FileSystem` acquisition tests for default URI resolution, scheme-to-class lookup, cached vs `newInstance` behavior, `closeAll`, `closeAllForUGI`, canonical URI/default port behavior, and user-specific lookup.
- Path qualification tests for fully qualified URIs, slash-relative paths, working-directory-relative paths, illegal relative paths with scheme, Windows absolute paths, path merge, parent/name/suffix/depth, and `Path.getFileSystem`.
- File operation contract tests for create overload defaults, create flags, checksum options, non-recursive create parent failure, append optional support, concat, rename overwrite and directory/file mismatch cases, truncate true/false behavior, delete recursive vs non-recursive, and deferred delete-on-exit cancellation.
- Listing tests for missing paths, file vs directory inputs, filters, multi-path arrays, glob syntax including braces/character classes/escaping, sorted glob results, located statuses with block locations, iterator error propagation, and recursive `listFiles`.
- Metadata tests for `FileStatus` serialization, symlink targets, encrypted flag, default permission/owner/group behavior, path-based compare/equality/hashCode, and `LocatedFileStatus` block locations.
- Permission/security tests for `access`, `setPermission`, `setOwner`, `setTimes`, ACL merge/remove/default/remove-all/set/get flows, and xattr set/get/list/remove with namespace and visibility rules.
- Stream capability tests for `FSDataInputStream` seek/position/positional read/readFully EOF semantics, byte-buffer reads, file descriptor access, readahead/drop-behind unsupported behavior, enhanced buffer release, and unbuffering.
- Output stream tests for `FSDataOutputStream.getPos`, close, `hflush` visibility to new readers, `hsync` durability semantics where supported, deprecated `sync`, and drop-behind hints.
- `FileUtil` tests for recursive delete symlink distinctions, partial-failure handling, copy/copyMerge across filesystems, local-to-FS and FS-to-local copy with delete-source and overwrite flags, archive extraction, chmod/chown return codes, portable permission checks, temp-file delete-on-exit, replace-file behavior, and safe list/listFiles IOException behavior.
- Wrapper tests for `FilterFileSystem` delegation across core, symlink, checksum, snapshot, ACL, xattr, and statistics APIs.
- Local filesystem tests for `LocalFileSystem` checksum failure handling and `RawLocalFileSystem` mapping between `Path` and `File`, mkdirs idempotence, local symlink support, ignored access-time setting, and command-based owner/permission changes.
