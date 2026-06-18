# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.2.xml lines 6055-11996

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.8.2. It starts inside the tail of `org.apache.hadoop.fs.FileContext`, covers all of `FileStatus`, all of `FileSystem`, all of `FileUtil`, all of `FilterFileSystem`, all of `FsConstants`, all of `FSDataInputStream`, all of `FSDataOutputStream`, all of `FSError`, all of `FSInputStream`, and ends at the opening constructor metadata for `FsServerDefaults`.

The source is generated API metadata, not executable implementation. The research surface is therefore the public/protected compatibility contract: type hierarchy, implemented interfaces, constructors, method signatures, checked exceptions, final/static/abstract markers, deprecation markers, fields, and embedded Javadocs.

## Purpose

The `FileContext` tail documents the newer filesystem access facade: it resolves Hadoop URI, default-filesystem, and working-directory path names; applies umask and server-side defaults; exposes file operations; and forwards advanced features such as ACLs, xattrs, snapshots, symlinks, checksums, and storage policies to the target filesystem.

`FileStatus` is the serializable client-side metadata record for a file, directory, or symbolic link. It is the common status payload returned by `FileSystem`, `FileContext`, globbing, listing, and RPC-backed filesystem operations.

`FileSystem` is the core abstract filesystem base class. It defines instance discovery/caching, URI canonicalization, stream creation, mutation, status/listing, local copy helpers, token integration, symlink support, ACL/xattr/snapshot/storage-policy hooks, and global filesystem/storage statistics.

`FileUtil` is a static utility class for local and cross-filesystem file manipulation: recursive deletion, copy/merge, shell path conversion, archive extraction, local symlinks and permissions, temp files, replacement, directory-list wrappers, classpath jar creation, and filesystem comparison.

`FilterFileSystem` is a delegating `FileSystem` wrapper. It stores a protected raw `FileSystem` and overrides most operations to pass through to that contained filesystem, allowing subclasses to transform path schemes, add behavior, or filter calls.

`FSDataInputStream`, `FSDataOutputStream`, and `FSInputStream` define Hadoop's seekable and positioned file stream contracts. `FsConstants` captures filesystem URI/scheme constants, and `FSError` represents unexpected native filesystem errors presumed to indicate disk-level failure.

## Important APIs, Types, and Functions

### FileContext tail

- File operations in this chunk include `open(Path)`, `open(Path, int)`, `truncate(Path, long)`, `setReplication`, `rename(Path, Path, Options.Rename...)`, `setPermission`, `setOwner`, `setTimes`, `getFileChecksum`, `setVerifyChecksum`, `getFileStatus`, `getFileLinkStatus`, `getLinkTarget`, `getFsStatus`, `createSymlink`, `listStatus`, `listCorruptFileBlocks`, `listLocatedStatus`, and `deleteOnExit`.
- Advanced namespace and metadata operations include ACL mutation/status methods, xattr set/get/list/remove methods, `createSnapshot`, `renameSnapshot`, `deleteSnapshot`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, and `getAllStoragePolicies`.
- Utility/control APIs include `util()`, `resolve`, `resolveIntermediate`, static statistics accessors, `clearStatistics`, `printStatistics`, and fields `LOG`, `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`.
- The class documentation emphasizes Hadoop URI naming, default filesystem resolution, working-directory-relative paths, FileContext-held umask, and server-side defaults for home directory, initial working directory, replication, block size, buffer size, encryption, and checksum options.

### FileStatus

- `FileStatus` implements `Writable` and `Comparable`.
- Constructors cover empty construction, basic length/directory/replication/block-size/modification-time/path metadata, full metadata with access time, permission, owner, group, symlink target, and a copy constructor.
- Metadata accessors include `getLen`, `isFile`, `isDirectory`, deprecated `isDir`, `isSymlink`, `getBlockSize`, `getReplication`, `getModificationTime`, `getAccessTime`, `getPermission`, `isEncrypted`, `getOwner`, `getGroup`, `getPath`, and `getSymlink`.
- Mutation and serialization hooks include `setPath`, protected `setPermission`, protected `setOwner`, protected `setGroup`, `setSymlink`, `write(DataOutput)`, and `readFields(DataInput)`.
- Ordering/equality APIs include typed `compareTo(FileStatus)`, bridge `compareTo(Object)` retained for binary compatibility after HADOOP-14683, `equals`, `hashCode`, and `toString`. Javadocs define equality and hashing by path name.

### FileSystem

- Discovery and lifecycle APIs include static `get` overloads, `getDefaultUri`, `setDefaultUri`, `initialize`, `getScheme`, abstract `getUri`, URI canonicalization helpers, `getDefaultPort`, `getFSofPath`, `getCanonicalServiceName`, deprecated `getName`/`getNamed`, `getLocal`, `newInstance` overloads, `newInstanceLocal`, `closeAll`, `closeAllForUGI`, `close`, and `getChildFileSystems`.
- Path/service integration includes `makeQualified`, `checkPath`, `fixRelativePart`, token integration through `addDelegationTokens`, and statistics through per-filesystem `statistics`, `getStatistics`, `getAllStatistics`, `clearStatistics`, `printStatistics`, `getStorageStatistics`, and `getGlobalStorageStatistics`.
- Read and write APIs include `open`, many `create` overloads, `primitiveCreate`, `primitiveMkdir`, `createNonRecursive`, `createNewFile`, `append`, `concat`, `getFileBlockLocations`, `getServerDefaults`, and `resolvePath`.
- Namespace mutation/status APIs include `setReplication`, abstract boolean `rename`, protected option-based `rename`, `truncate`, deprecated single-argument `delete`, abstract recursive `delete`, `deleteOnExit`, `cancelDeleteOnExit`, `processDeleteOnExit`, `exists`, `isDirectory`, `isFile`, deprecated `getLength`, `getContentSummary`, `getQuotaUsage`, abstract `listStatus`, filtered/multi-path `listStatus`, `globStatus`, `listLocatedStatus`, `listStatusIterator`, and `listFiles`.
- Working directory and local-copy APIs include `getHomeDirectory`, abstract `setWorkingDirectory`, abstract `getWorkingDirectory`, `getInitialWorkingDirectory`, `mkdirs`, `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, `moveToLocalFile`, `startLocalOutput`, and `completeLocalOutput`.
- Default size/status APIs include deprecated and path-aware `getDefaultBlockSize`, deprecated and path-aware `getDefaultReplication`, `getUsed`, `getStatus`, and abstract `getFileStatus`.
- Symlink and checksum APIs include `createSymlink`, `getFileLinkStatus`, `supportsSymlinks`, `getLinkTarget`, `resolveLink`, `getFileChecksum` overloads, `setVerifyChecksum`, `setWriteChecksum`, static `areSymlinksEnabled`, and static `enableSymlinks`.
- Security/metadata extension points include `access`, `setPermission`, `setOwner`, `setTimes`, ACL methods, xattr methods, snapshot methods, storage-policy methods, and trash root discovery through `getTrashRoot` and `getTrashRoots`.
- Fields include `FS_DEFAULT_NAME_KEY`, deprecated `DEFAULT_FS`, `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, and protected per-instance `statistics`.

### FileUtil

- Recursive deletion APIs include `fullyDelete(File)`, `fullyDelete(File, boolean)`, `fullyDeleteContents(File)`, `fullyDeleteContents(File, boolean)`, and deprecated filesystem-path `fullyDelete(FileSystem, Path)`.
- Copy APIs cover filesystem-to-filesystem copies by path, path array, and `FileStatus`; local-to-filesystem and filesystem-to-local copies; delete-source and overwrite options; and `copyMerge`.
- Local utility APIs include `stat2Paths`, `readLink`, `makeShellPath` overloads, `getDU`, `unZip`, `unTar`, `symLink`, `chmod` overloads, `setOwner(File, String, String)`, portable `setReadable`, `setWritable`, `setExecutable`, `canRead`, `canWrite`, `canExecute`, and `setPermission(File, FsPermission)`.
- Atomic-ish local helpers include `createLocalTempFile`, `replaceFile`, `listFiles`, and `list`, with the listing wrappers converting null-returning `java.io.File` APIs into IOException-oriented contracts.
- Classpath/process helpers include `createJarWithClassPath` overloads, which write a manifest jar to work around command-line length limits, expand environment variables, and expand wildcard classpath entries.
- `compareFs` compares two `FileSystem` instances, and `SYMLINK_NO_PRIVILEGE` captures the Windows/local symlink privilege failure return code.

### FilterFileSystem, FsConstants, and Streams

- `FilterFileSystem` has default and raw-filesystem constructors, `getRawFileSystem`, protected fields `fs` and `swapScheme`, and pass-through overrides for URI, path, read/write, listing, local copy, status, symlink, checksum, ACL, xattr, snapshot, storage-policy, trash, and close behavior.
- `FsConstants` exposes `LOCAL_FS_URI`, `FTP_SCHEME`, `MAX_PATH_LINKS`, `VIEWFS_URI`, and `VIEWFS_SCHEME`.
- `FSDataInputStream` extends `DataInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, and `CanUnbuffer`. It exposes seek/position, positioned `read`, positioned `readFully`, alternate-source seek, `ByteBuffer` read, file descriptor access, readahead/drop-behind controls, enhanced zero-copy-style buffer reads with `ByteBufferPool`, `releaseBuffer`, `unbuffer`, and `toString`.
- `FSDataOutputStream` extends `DataOutputStream` and implements `Syncable` and `CanSetDropBehind`. It tracks output position, closes the wrapped stream, and exposes `sync`, `hflush`, `hsync`, and drop-behind control.
- `FSInputStream` extends `InputStream` and implements `Seekable` and `PositionedReadable`. It defines abstract `seek`, `getPos`, and `seekToNewSource`, plus default positioned read/readFully helpers and protected argument validation.
- `FSError` extends `Error` for unexpected native filesystem failures.
- `FsServerDefaults` begins at the end of the chunk; only the class opening, `Writable` implementation marker, and constructor start are visible here.

## Control Flow

The XML has no executable control flow, but the public contracts imply several major runtime flows.

`FileContext` and `FileSystem` path operations resolve relative names, default filesystem URIs, authorities, and working-directory state into qualified `Path` values, validate that paths belong to the target filesystem, and then call implementation-specific operations. For RPC-backed filesystems, the Javadocs repeatedly surface `RpcClientException`, `RpcServerException`, and `UnexpectedServerException` as relevant remote failure modes.

Filesystem acquisition flows through `FileSystem.get` or `newInstance`: callers provide a URI/user/configuration, Hadoop resolves the scheme to an implementation class, initializes it with URI and `Configuration`, and either reuses cached instances or returns a fresh instance. Close flows through instance `close`, process-wide `closeAll`, or user-specific `closeAllForUGI`; close also processes paths registered through `deleteOnExit`.

File creation flows through high-level convenience overloads into richer overloads carrying `FsPermission`, `EnumSet<CreateFlag>`, buffer size, replication, block size, `Progressable`, and optional checksum settings. Non-recursive create variants enforce parent-existence semantics. Append and truncate are optional or filesystem-dependent operations: truncate may return `false` to indicate asynchronous block adjustment before future writes such as append are safe.

Listing flows include eager arrays (`listStatus`), lazy remote iterators (`listStatusIterator`, `listLocatedStatus`, `listFiles`), corrupt-block iteration, and glob expansion. The Javadocs explicitly warn that ordinary listing does not guarantee sorted order, while glob results are sorted by path/name.

Local transfer flows use copy helpers to move data between local disk and Hadoop filesystems. Remote-output staging uses `startLocalOutput` to choose either the target path for local filesystems or a temporary local path for remote filesystems, then `completeLocalOutput` to publish temporary output to the final filesystem path.

`FilterFileSystem` control flow is deliberately thin: it initializes, qualifies, checks, and delegates calls to the wrapped `fs`. Subclasses can override selected methods to transform schemes or add policy while preserving the `FileSystem` contract.

Stream control flow separates sequential position from positioned reads. `FSInputStream` subclasses implement seek and current-position operations; `FSDataInputStream` wraps such streams and exposes Java data input plus Hadoop-specific seek, positioned read, readahead, drop-behind, enhanced byte buffer, and unbuffer controls. `FSDataOutputStream` wraps an output stream and exposes durable flush/sync controls.

`FileUtil` control flows are local-OS oriented. Recursive delete may partially delete and report `false`; permission helpers may use Java primitives or shell commands depending on platform and permission shape; archive extraction expands files into target directories; manifest-jar creation normalizes classpath entries, expands environment variables, and expands wildcard jars before writing a jar.

## State and Persistence Behavior

The JDiff file itself persists API metadata for release compatibility checks. It does not perform filesystem I/O.

The APIs in this chunk are persistence-sensitive. `FileStatus` is a `Writable`, so its field encoding and read/write behavior are part of Hadoop's binary compatibility surface. It carries path, length, directory/file/symlink state, replication, block size, modification/access timestamps, permissions, owner, group, optional symlink target, and encryption state.

`FileSystem` persists and mutates external filesystem state: file contents, directories, symlinks, metadata, ACLs, xattrs, snapshots, storage policies, replication, checksums, timestamps, ownership, trash roots, and delete-on-exit paths. Its static cache and statistics registries are process-local state, while actual namespace and data state live in local filesystems, HDFS, ViewFs targets, FTP, or other scheme-specific implementations.

`FileContext` state is described as namespace context comparable to Unix per-process file state: default filesystem, working directory, and umask. Server-side defaults are filesystem-owned and may vary by target path or backing service.

`deleteOnExit` stores process-local deferred deletion state. The operation requires the path to exist at registration time, and actual deletion happens during filesystem close or JVM shutdown-triggered close. This can produce late failures or partial cleanup if files change before shutdown.

`FSDataInputStream` and `FSInputStream` maintain current read offsets. Positioned reads are contractually independent of the current sequential position, while `seek` changes subsequent sequential reads. Enhanced byte-buffer reads allocate or borrow buffers from a caller-provided `ByteBufferPool`, and callers must release buffers through `releaseBuffer`.

`FSDataOutputStream` maintains output position and wraps lower-level flush/sync behavior. `hflush` and `hsync` are persistence and visibility boundaries whose durability semantics depend on the backing filesystem implementation.

`FileUtil` mutates local filesystem state through delete, chmod/chown-like operations, symlink creation, archive extraction, temp-file creation, file replacement, and manifest-jar generation. Its recursive delete operations can leave partially deleted trees, and symlink handling differs between delete variants and platforms.

## Dependencies and Integration Points

Core Java dependencies include `java.net.URI`, `java.io.Closeable`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, `File`, `FileDescriptor`, `FileNotFoundException`, `EOFException`, `IOException`, `ByteBuffer`, collections, `EnumSet`, and user/group/string primitives.

Hadoop configuration and security integration includes `org.apache.hadoop.conf.Configuration`, `Configured`, `UserGroupInformation`, delegation `Token`, `AccessControlException`, `Credentials`-style token lookup through canonical service names, and `FsAction` access checks.

Filesystem API dependencies include `Path`, `PathFilter`, `BlockLocation`, `ContentSummary`, `QuotaUsage`, `FsStatus`, `RemoteIterator`, `LocalFileSystem`, `RawLocalFileSystem`, `FileChecksum`, `BlockStoragePolicySpi`, `StorageStatistics`, `GlobalStorageStatistics`, `Options.Rename`, `Options.ChecksumOpt`, and `CreateFlag`.

Permissions and metadata integration includes `FsPermission`, `AclEntry`, `AclStatus`, xattr flags (`XAttrSetFlag` via `EnumSet`), snapshot-capable filesystems, storage policies, trash roots, and symlink exceptions such as unresolved-link behavior surfaced in FileContext docs.

Stream integration includes `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `CanUnbuffer`, `ByteBufferPool`, `ReadOption`, and `Syncable`.

Operational integration includes shell commands for chmod/symlink behavior, platform-specific Windows permission behavior, archive formats (`zip`, `tar`, `tar.gz`, `tgz`), classpath manifest rules, environment variable expansion, and command-line length workarounds.

## Risks and Edge Cases

- This chunk starts mid-`FileContext` and ends at the beginning of `FsServerDefaults`; adjacent chunks must be reconciled before making final file-wide claims about those types.
- JDiff records signatures and Javadocs, not implementation bodies. Exact locking, cache internals, statistics counters, normalization details, and default behavior require source validation.
- Rename semantics are implementation-dependent. FileContext documents overwrite behavior and parent/type failure modes, while FileSystem's protected option-based rename Javadoc says the default implementation is non-atomic.
- `truncate` returning `false` is an important asynchronous state. Clients that append or update immediately after a false result can race the backing filesystem's block adjustment.
- `listStatus` ordering is not guaranteed except for glob results. Code that relies on sorted directory listings can behave differently across filesystems.
- `FileStatus.equals` and `hashCode` are path-based, so two statuses with different metadata but the same path compare equal.
- `FileStatus.compareTo(Object)` is present for binary compatibility. Removing bridge methods or changing generic signatures can break existing compiled clients.
- Permission defaults are historically sensitive: `DEFAULT_PERM` previously caused created files to include execute bits, and the docs direct new code to `DIR_DEFAULT_PERM` or `FILE_DEFAULT_PERM`.
- `FileSystem` instance caching and process-wide `closeAll` can produce lifecycle surprises for clients that share configurations or users across libraries.
- `deleteOnExit` is deferred process-local state and may fail late; recursive deletion can be expensive or destructive if paths are wrong.
- Symlink behavior is globally gated by static symlink controls and varies by backing filesystem and platform. `FileUtil.symLink` explicitly has Windows privilege failure behavior.
- Local permission helpers have platform-specific semantics. The docs note Windows differences for read/write/execute checks and folder execute revocation.
- `FileUtil.fullyDeleteContents` follows symlinks to directories for content deletion, which is dangerous if callers assume only the link itself is affected.
- `FileUtil` archive extraction and classpath jar creation can be sensitive to path traversal, environment expansion, wildcard expansion, and platform-specific path syntax; implementation source should be checked for hardening.
- Enhanced byte-buffer reads require explicit buffer release. Leaking buffers or reusing released buffers can create memory pressure or data corruption.
- Drop-behind and readahead are optional controls and may throw `UnsupportedOperationException` or silently depend on filesystem support.
- `FSError` extends `Error`, not `Exception`; callers generally should not treat it as routine recoverable I/O.

## Test Signals

Useful validation for this API surface should include:

- FileContext tests for default filesystem resolution, working-directory-relative paths, invalid `scheme:relative` paths, umask/default permission selection, open/truncate/rename/delete semantics, RPC exception wrapping, and server-side default use.
- FileContext metadata tests for ACL replacement and mutation, xattr namespaces and visibility filtering, snapshots, storage policies, symlink status vs target status, checksum retrieval, and delete-on-exit behavior.
- FileStatus golden serialization tests covering file, directory, symlink, encrypted status, null permission/owner/group defaults, copy construction, `readFields` mutation, path-based equality/hash, and both typed and bridge `compareTo` methods.
- FileSystem cache/lifecycle tests for `get`, `newInstance`, `getLocal`, `closeAll`, `closeAllForUGI`, canonical service names, child filesystems, storage statistics, and per-scheme implementation lookup.
- FileSystem operation tests for all create overload families, non-recursive create parent failures, append optional behavior, concat, truncate true/false completion paths, replication, rename overwrite/non-overwrite behavior, recursive delete, and create-new-file collision behavior.
- Listing and glob tests for missing files, filters, multi-path list calls, unsorted ordinary listings, sorted glob results, corrupt-block iterators, located status block locations, lazy iterator behavior, and recursive `listFiles`.
- Local copy tests for delete-source, overwrite, multiple sources, raw local filesystem copy-to-local mode, `startLocalOutput`/`completeLocalOutput`, and failure cleanup.
- Symlink/checksum/access tests for `supportsSymlinks`, `createSymlink`, `getFileLinkStatus`, `getLinkTarget`, `resolveLink`, global symlink enablement, checksum verification/write flags, and `access(Path, FsAction)`.
- FileUtil tests for recursive delete partial-failure reporting, symlink-to-directory deletion semantics, copy and copyMerge, shell path conversion, disk-usage calculation, zip/tar extraction, symlink privilege failures, chmod/chown behavior, portable read/write/execute checks, temp-file creation, replace-file behavior, and IOException-producing list wrappers.
- FileUtil classpath jar tests for Windows and Unix environment variable expansion, case-insensitive Windows environment lookup, wildcard jar expansion, target directory handling, and manifest classpath length behavior.
- FilterFileSystem tests verifying delegation for every overridden method, raw filesystem exposure, URI/scheme swapping, close propagation, ACL/xattr/snapshot/storage-policy forwarding, and child filesystem behavior.
- Stream tests for seek bounds, positioned read not changing current position, `readFully` EOF behavior, `seekToNewSource`, `ByteBuffer` reads, enhanced buffer release discipline, file descriptor exposure, readahead/drop-behind unsupported behavior, `unbuffer`, output `getPos`, `hflush`, `hsync`, `sync`, and close propagation.
