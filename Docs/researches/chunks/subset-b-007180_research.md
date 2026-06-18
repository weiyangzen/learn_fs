# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml lines 6121-12035

## Scope

This chunk is a JDiff API snapshot for Hadoop Common 2.8.3, not executable source. It covers the tail of `org.apache.hadoop.fs.FileContext`, the complete public API entries for `FileStatus`, `FileSystem`, `FileUtil`, `FilterFileSystem`, `FsConstants`, `FSDataInputStream`, and the opening of `FSDataOutputStream`. The XML records public/protected signatures, inheritance, implemented interfaces, thrown exceptions, fields, deprecation state, and Javadoc text used for compatibility reporting.

## Purpose and major API surface

`FileContext` is represented from `makeQualified` through advanced filesystem operations. The covered methods expose create/open/delete/rename/truncate, mkdir, replication, permissions, owner/group/times, checksums, file and link status, symlink creation and resolution, status listing, corrupt-block listing, located listing, delete-on-exit, statistics, ACLs, xattrs, snapshots, and storage policies. Its class-level documentation frames `FileContext` as the per-client namespace context that resolves Hadoop URI paths, default filesystem paths, working-directory-relative paths, and umask-derived permissions while leaving most server-side defaults to each filesystem implementation.

`FileStatus` is the client-side metadata carrier for a path. It implements `Writable` and `Comparable`, with constructors for plain files/directories, symlink-aware status, and copy construction. Its API exposes length, type checks (`isFile`, `isDirectory`, deprecated `isDir`, `isSymlink`), block size, replication, modification/access time, permissions, encryption state, owner, group, path, symlink target, serialization (`write`, `readFields`), comparison, equality, hashing, and stringification.

`FileSystem` is the central abstract filesystem base class extending `Configured` and implementing `Closeable`. The covered API includes factory and cache methods (`get`, `newInstance`, `getLocal`, `closeAll`, `closeAllForUGI`), URI/canonicalization handling, service names for token caches, path qualification and validation, delegation tokens, create/open/append/concat/truncate/delete/rename, mkdirs and primitive create/mkdir helpers, block locations, server defaults, listing/globbing/iterators, local copy/move helpers, working directory and home directory, status/quota/used-space queries, symlink APIs, checksum controls, permissions/owner/times, snapshots, ACLs, xattrs, storage policies, trash roots, implementation class lookup, global statistics, symlink enablement, and storage statistics. Fields in this chunk include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, and an instance `statistics` object.

`FileUtil` is a static utility collection for filesystem and local-file operations. It converts `FileStatus[]` to `Path[]`, recursively deletes files/directories and directory contents, reads symlink targets, copies among `FileSystem` instances and local files, merges files, builds shell-safe paths, computes local disk usage, unzips/untars archives, creates symlinks, chmod/chown and permission helpers, portable readability/writability/executability helpers, temp-file creation, atomic-style replacement, null-safe wrappers around `File.listFiles()` and `File.list()`, classpath jar creation, and filesystem comparison. `SYMLINK_NO_PRIVILEGE` is the exposed constant for symlink privilege failure.

`FilterFileSystem` is a concrete `FileSystem` wrapper with an underlying `fs` field and optional `swapScheme`. Its public methods mirror much of `FileSystem` and delegate behavior to the raw filesystem: URI/canonical URI, path qualification, block locations, open/create/append/concat, non-recursive create, replication, rename, truncate, delete, listings, working directory, status, mkdirs, local copies, local output staging, usage/defaults/server defaults, file status, access checks, symlinks, checksums, configuration/close, owner/times/permissions, primitive operations, child filesystems, snapshots, ACLs, xattrs, storage policy, and trash roots.

`FsConstants` defines filesystem constants: `LOCAL_FS_URI`, `FTP_SCHEME`, `MAX_PATH_LINKS`, `VIEWFS_URI`, and `VIEWFS_SCHEME`. `FSDataInputStream` wraps an `FSInputStream` in a `DataInputStream`/buffered input utility and implements seekable positioned reads, byte-buffer reads, file-descriptor access, readahead/drop-behind controls, enhanced byte-buffer reads using `ByteBufferPool`, buffer release, unbuffering, and `toString`. `FSDataOutputStream` begins at the end of the chunk as a `DataOutputStream` implementing `Syncable` and `CanSetDropBehind`; only its class declaration and first constructor are visible here.

## Control flow and behavioral contracts

Because this is JDiff XML, direct control flow is absent. The behavioral contracts are expressed as public API shape and Javadoc. `FileContext` and `FileSystem` operations consistently route through `Path`, `URI`, `Configuration`, `FsPermission`, `Options.CreateOpts`, `CreateFlag`, and filesystem-specific implementations. Many methods document RPC-specific exception surfaces (`RpcClientException`, `RpcServerException`, `UnexpectedServerException`) even when the Java signature exposes `IOException` subclasses, indicating that remote filesystem integrations must preserve exception compatibility.

Factory flow for `FileSystem` is configuration driven. Static `get` resolves the configured/default URI or the supplied URI and may return cached instances, while `newInstance` returns unique configured implementations. `closeAll` and `closeAllForUGI` manage cached instances and are tied to shutdown-hook behavior. `makeQualified`, `checkPath`, `resolvePath`, and canonical URI methods define the path-normalization flow before operations reach concrete filesystems.

File mutation flow is represented by layered overloads. High-level `create` overloads supply defaults and progress callbacks, lower-level `primitiveCreate` and `primitiveMkdir` expose absolute-permission variants, and `createNonRecursive` requires the parent to already exist. `append`, `concat`, `truncate`, `rename`, and `delete` are optional or implementation-sensitive operations; callers must interpret booleans and documented exceptions rather than assuming uniform support across local, HDFS, viewfs, FTP, or filter filesystems.

Read flow centers on `FSDataInputStream`: callers can `seek`, query `getPos`, perform positioned reads without changing stream position, `readFully`, seek to a new source replica, read into `ByteBuffer`, request readahead/drop-behind, obtain a `FileDescriptor` where supported, and release pooled buffers. The optional `UnsupportedOperationException` contracts on buffer/readahead/drop-behind operations are important integration signals for filesystem implementations.

## State, persistence, and side effects

The APIs here operate on persistent filesystem namespace and metadata: file contents, directories, symlinks, permissions, owner/group, times, ACLs, xattrs, snapshots, storage policies, replication, checksums, and trash roots. `FileStatus` itself is a serializable metadata snapshot and does not mutate the backing filesystem except through setters that alter the local status object fields.

`FileContext` carries client-side namespace state: default filesystem, working directory, and umask. `FileSystem` carries configuration, URI identity, cached global instances, statistics, storage statistics, shutdown behavior, and delete-on-exit queues. `deleteOnExit`, `cancelDeleteOnExit`, and `processDeleteOnExit` are stateful and can delete paths later at close/shutdown time, so tests and callers must isolate them carefully.

`FileUtil` has substantial local side effects. Recursive delete can partially delete on failure; archive extraction writes directory trees; chmod/chown/symlink helpers call platform facilities; `replaceFile` moves local files; `createJarWithClassPath` emits jar artifacts. Null-safe listing wrappers convert problematic `java.io.File` null returns into checked `IOException` behavior for callers.

`FilterFileSystem` persists no independent namespace data in this API snapshot. Its important state is the wrapped raw `FileSystem`; behavior, statistics, permissions, and lifecycle are expected to pass through to that delegate unless a subclass overrides.

## Dependencies and integration points

The chunk integrates heavily with Hadoop Common types: `Path`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `BlockLocation`, `FsServerDefaults`, `FsStatus`, `ContentSummary`, `QuotaUsage`, `RemoteIterator`, `PathFilter`, `Options.Rename`, `Options.ChecksumOpt`, `Options.CreateOpts`, `CreateFlag`, `BlockStoragePolicySpi`, `StorageStatistics`, `GlobalStorageStatistics`, ACL and xattr types, `FsPermission`, `AclEntry`, `AclStatus`, `XAttrSetFlag`, `Configuration`, `UserGroupInformation`, `Token`, and `ByteBufferPool`.

Java and platform integration points include `URI`, `File`, `FileDescriptor`, `InputStream`, `OutputStream`, `DataInputStream`, `DataOutputStream`, `EnumSet`, `Map`, `Collection`, `List`, `Comparable`, `Closeable`, and `Writable`. Security and remote execution concerns surface through `AccessControlException`, token service names, delegation tokens, RPC exception documentation, and UGI-scoped filesystem cache closing.

Concrete implementations are intentionally abstracted. The class docs call out local filesystem and HDFS as common implementations, while constants and APIs also account for FTP and viewfs. `FilterFileSystem` is the extension point for wrappers that adapt or decorate another `FileSystem`, so compatibility of delegated method semantics is central.

## Risks and compatibility concerns

JDiff files are consumed as compatibility baselines, so signature changes, visibility changes, exception changes, deprecation changes, and Javadoc contract drift can be compatibility risks even if implementation code compiles. The very broad `FileSystem` overload surface increases the chance of accidental binary/API incompatibility.

Path qualification and symlink resolution are high-risk areas. `FileContext` allows fully qualified, slash-relative, and working-directory-relative names, while explicitly rejecting scheme-relative names like `scheme:foo/bar`. `MAX_PATH_LINKS` signals loop protection for symlink traversal. Implementations must preserve resolution and exception behavior across local, distributed, and view filesystems.

Stateful lifecycle APIs can surprise callers. Cached `FileSystem` instances share configuration and statistics; `newInstance` intentionally avoids cache reuse; shutdown hooks and delete-on-exit can perform late deletes; `closeAllForUGI` affects all filesystems for a user. Tests should avoid order dependence and clean global state.

Optional operations are common. Append, concat, truncate, symlink operations, ACLs, xattrs, storage policies, byte-buffer reads, readahead/drop-behind, file descriptors, and snapshots can throw `UnsupportedOperationException` or filesystem-specific `IOException`. Callers and wrapper implementations must not silently assume HDFS semantics for all schemes.

`FileUtil` utilities are platform-sensitive. Symlinks, chmod/chown, shell paths, archive extraction, and local permission checks vary across operating systems and privilege contexts. Recursive deletion methods document partial deletion on failure, which is a critical cleanup risk.

## Test signals

Compatibility tests should parse this XML and confirm the presence and signatures of the covered public/protected APIs, especially overloaded `FileSystem.create`, `createNonRecursive`, `open`, `listStatus`, `globStatus`, `copyFromLocalFile`, `copyToLocalFile`, ACL/xattr/storage-policy methods, and `FSDataInputStream` byte-buffer methods.

Behavioral tests in the underlying Hadoop codebase should cover path qualification/default-FS resolution, working-directory-relative paths, symlink resolution and loop limits, filesystem cache versus `newInstance`, UGI-scoped close behavior, delete-on-exit processing, statistics clearing/printing, and token aggregation.

Filesystem integration tests should exercise local and distributed implementations through `FileSystem`, `FileContext`, and `FilterFileSystem` wrappers to verify delegation preserves URI, status, listing, permissions, checksums, snapshots, xattrs, ACLs, storage policy, and trash-root behavior.

Local utility tests should cover recursive delete success and partial-failure behavior, symlink delete semantics, null-safe local listing wrappers, archive extraction, permission helper portability, classpath jar creation, and atomic replacement behavior. Stream tests should cover positioned reads, `readFully`, `seekToNewSource`, byte-buffer reads with `ByteBufferPool`, `releaseBuffer`, `unbuffer`, and unsupported-operation paths.
