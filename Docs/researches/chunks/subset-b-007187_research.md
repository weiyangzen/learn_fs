# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml lines 6131-12080

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.1.2, not implementation source. It starts inside the tail of `org.apache.hadoop.fs.CreateFlag`, fully covers `FileAlreadyExistsException`, `FileChecksum`, `FileContext`, `FileStatus`, `FileSystem`, and `FileUtil`, then ends inside the beginning of `FilterFileSystem`.

The research surface is the public and protected compatibility contract: class names, inheritance, implemented interfaces, constructors, method signatures, checked exceptions, public/protected fields, static/final/abstract/synchronized flags, deprecation markers, and embedded Javadocs. Runtime algorithms must be confirmed against Java implementation files, but this XML is authoritative for the release API snapshot used by JDiff.

## Purpose

The covered APIs define Hadoop Common's core filesystem client surface.

`CreateFlag` describes creation and append semantics for file creation APIs: create, append, overwrite, sync blocks, lazy persistence, and appending into a new block. The visible tail documents validation helpers and invalid flag combinations.

`FileAlreadyExistsException` is the checked I/O exception used when an operation targets an existing path and overwrite semantics were not requested.

`FileChecksum` is the abstract checksum value contract for files. It is serializable through Hadoop `Writable`, exposes algorithm name, checksum length, raw bytes, checksum options, equality, and hashing.

`FileContext` is Hadoop's newer filesystem facade, modeled as per-client filesystem state. It carries a default `AbstractFileSystem`, user identity, working-directory resolution, and umask, and exposes high-level operations for creation, deletion, listing, status, symlinks, ACLs, xattrs, snapshots, and storage policies.

`FileStatus` is the client-side metadata record for a file, directory, or symlink. It stores length, type, replication, block size, times, permission, owner, group, path, symlink target, and attribute flags for ACL, encryption, erasure coding, and snapshot support.

`FileSystem` is the older abstract base class for local, distributed, object-store, and third-party filesystems. It defines instance caching, URI qualification, initialization, stream creation/opening, directory and metadata operations, local-copy helpers, statistics, trash, storage policies, and builder APIs.

`FileUtil` is a static utility class for local and cross-filesystem file processing: deletion, copying, shell path conversion, disk usage, archive extraction, symlinks, chmod/chown/permission portability, temp-file creation, replacement, listing wrappers, and classpath-manifest jar creation.

The visible `FilterFileSystem` portion defines a `FileSystem` wrapper that delegates operations to a raw underlying `FileSystem`, useful for layered filesystem behavior.

## Important APIs, Types, and Functions

### CreateFlag Tail

- `validate(Object path, boolean pathExists, EnumSet flag)` validates create semantics and throws `IOException` or `HadoopIllegalArgumentException`.
- `validateForAppend(EnumSet flag)` requires `APPEND` and rejects `OVERWRITE`.
- Documented flags include `CREATE`, `APPEND`, `OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`.
- Invalid combinations are `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`.

### FileAlreadyExistsException and FileChecksum

- `FileAlreadyExistsException` extends `IOException` and has empty and message constructors.
- `FileChecksum` implements `Writable` and declares abstract `getAlgorithmName()`, `getLength()`, and `getBytes()`.
- `getChecksumOpt()` returns `Options.ChecksumOpt`.
- `equals(Object)` is defined around algorithm and checksum value equality; `hashCode()` completes the value contract.

### FileContext

- Factory methods build contexts from an `AbstractFileSystem`, default config, local FS, `URI`, or explicit `Configuration`.
- Path and identity APIs include `getFSofPath(Path)`, `setWorkingDirectory(Path)`, `getWorkingDirectory()`, `getUgi()`, `getHomeDirectory()`, `getUMask()`, `setUMask(FsPermission)`, `resolvePath(Path)`, and `makeQualified(Path)`.
- File operations include `create(Path, EnumSet<CreateFlag>, Options.CreateOpts...)`, `mkdir(Path, FsPermission, boolean)`, `delete(Path, boolean)`, `open(Path)`, `open(Path, int)`, `truncate(Path, long)`, `setReplication(Path, short)`, and `rename(Path, Path, Options.Rename...)`.
- Metadata and link operations include `setPermission`, `setOwner`, `setTimes`, `getFileChecksum`, `setVerifyChecksum`, `getFileStatus`, `getFileLinkStatus`, `getLinkTarget`, `getFsStatus`, and `createSymlink`.
- Listing APIs return `RemoteIterator` for `listStatus`, `listLocatedStatus`, and `listCorruptFileBlocks`.
- Lifecycle and utilities include `deleteOnExit(Path)`, `util()`, protected symlink-resolution helpers, and static statistics helpers.
- Security and namespace extensions include ACL mutation/read APIs, xattr mutation/read/list/remove APIs, snapshot create/rename/delete, and storage policy set/unset/get/list.
- Public fields include `LOG`, compatibility `DEFAULT_PERM`, preferred `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`, plus `SHUTDOWN_HOOK_PRIORITY`.

### FileStatus

- Implements `Writable`, `Comparable`, `Serializable`, and `ObjectInputValidation`.
- Constructors cover no-arg deserialization, basic metadata, metadata without symlink support, symlink targets, boolean attribute triples, explicit attribute sets, and copy construction.
- Static `attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts booleans into a set of attribute flags; `NONE` is the shared empty attribute set.
- Accessors expose length, `isFile()`, `isDirectory()`, deprecated `isDir()`, `isSymlink()`, block size, replication, modification/access time, permissions, ACL/encryption/erasure-coded/snapshot flags, owner, group, path, and symlink target.
- Protected setters normalize permission, owner, and group defaults; public setters exist for path and symlink.
- `compareTo(FileStatus)`, binary-compatible `compareTo(Object)`, `equals(Object)`, and `hashCode()` are path-based.
- `readFields(DataInput)` and `write(DataOutput)` are deprecated in favor of `PBHelper` and protobuf serialization; `validateObject()` supports Java deserialization validation.

### FileSystem

- Extends `Configured`, implements `Closeable` and `DelegationTokenIssuer`, and has a protected constructor.
- Static acquisition and cache APIs include `get(URI, Configuration, String)`, `get(Configuration)`, `get(URI, Configuration)`, `newInstance(...)`, `newInstanceLocal(Configuration)`, `closeAll()`, and `closeAllForUGI(UserGroupInformation)`.
- Default filesystem helpers include `getDefaultUri(Configuration)`, `setDefaultUri(Configuration, URI/String)`, `getLocal(Configuration)`, deprecated `getNamed`, deprecated `getName`, and `getFileSystemClass(String, Configuration)`.
- Initialization and URI APIs include `initialize(URI, Configuration)`, `getScheme()`, abstract `getUri()`, `getCanonicalUri()`, `canonicalizeUri(URI)`, `getDefaultPort()`, `checkPath(Path)`, `makeQualified(Path)`, and protected `getFSofPath(Path, Configuration)`.
- Token integration is via `getCanonicalServiceName()`, whose default behavior uses URI and port when the filesystem has its own tokens.
- Stream and creation APIs include abstract `open(Path, int)`, `open(Path)`, `open(PathHandle)`, `open(PathHandle, int)`, `getPathHandle(FileStatus, HandleOpt...)`, protected `createPathHandle(...)`, many `create(...)` overloads, `primitiveCreate`, `primitiveMkdir`, `createNonRecursive`, `createNewFile`, `append(...)`, and builder APIs `createFile(Path)` and `appendFile(Path)`.
- Mutation APIs include `mkdirs`, `concat`, `setReplication`, `rename`, `truncate`, `delete`, `deleteOnExit`, `cancelDeleteOnExit`, `processDeleteOnExit`, permission/owner/time setters, ACLs, xattrs, snapshots, storage policy operations, and symlink operations.
- Query APIs include block locations, server defaults, resolve path, content summary, quota usage, status/link status, existence/type/length helpers, listings, globbing, located listings, recursive file listings, home/working directory, checksums, filesystem capacity status, used bytes, block size/default block size/default replication, trash roots, storage statistics, and global statistics.
- Public fields include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and protected per-instance `statistics`.

### FileUtil

- `stat2Paths(...)` converts `FileStatus[]` to `Path[]`, optionally returning a default path when stats are null.
- Deletion utilities include `fullyDeleteOnExit(File)`, `fullyDelete(File)`, `fullyDelete(File, boolean)`, deprecated `fullyDelete(FileSystem, Path)`, `fullyDeleteContents(File)`, and `fullyDeleteContents(File, boolean)`.
- Copy utilities cover filesystem-to-filesystem, multi-source filesystem copy, `FileStatus`-based copy, local-to-filesystem, and filesystem-to-local overloads with delete-source and overwrite options.
- Shell/local utilities include `readLink(File)`, `makeShellPath(...)`, `makeSecureShellPath(File)`, `getDU(File)`, `symLink(String, String)`, `chmod(...)`, `setOwner(File, String, String)`, permission and access wrappers, `setPermission(File, FsPermission)`, `createLocalTempFile`, `replaceFile`, `listFiles(File)`, and `list(File)`.
- Archive and classpath helpers include `unZip(InputStream/File, File)`, `unTar(InputStream, File, boolean)`, `unTar(File, File)`, `createJarWithClassPath(...)`, and `getJarsInDirectory(...)`.
- `SYMLINK_NO_PRIVILEGE` is the public return-code constant for Windows symlink privilege failure.

### FilterFileSystem Beginning

- Constructors allow empty construction or wrapping a raw `FileSystem`.
- `getRawFileSystem()` exposes the wrapped filesystem.
- Visible overrides/delegations include `initialize`, URI/canonicalization, qualification/checking, block locations, `resolvePath`, `open(Path, int)`, `open(PathHandle, int)`, `createPathHandle`, `append`, `concat`, and the beginning of `create(...)`.

## Control Flow

The XML itself has no executable control flow, but the APIs define several important runtime paths.

`FileContext` path handling first qualifies relative or slash-relative paths using its default filesystem and working directory, then routes the operation to the `AbstractFileSystem` returned by `getFSofPath`. Symlink and mount-point resolution is explicit in `resolvePath`, while `setWorkingDirectory` is documented as string-prefix resolution rather than Unix inode-relative state.

`FileContext.create` and `FileSystem.create` both depend on `CreateFlag` and option validation. The API distinguishes "create if absent", "append if present", and "overwrite existing" semantics; invalid flag combinations fail before or during the actual filesystem operation. Permission flow applies umask for normal creation, while static `FileSystem.create(fs, file, permission)` and `mkdirs(fs, dir, permission)` intentionally set the exact requested permission after creation to avoid thread-unsafe configuration mutation.

`FileSystem.get(URI, Configuration)` follows a cache decision path: if `fs.$SCHEME.impl.disable.cache` is true, construct and initialize a new instance without caching; otherwise return a matching cached instance or create, initialize, cache, and return a new one. `newInstance(...)` variants always construct unique instances. `close()`, `closeAll()`, and `closeAllForUGI()` release cached resources and process delete-on-exit queues.

`FileSystem.initialize` is a required superclass-forwarding hook for subclasses. Subclasses may alter configuration before or after calling the superclass, but callers rely on initialization completing before use.

Read flow opens `FSDataInputStream` by path or, if supported, by `PathHandle`. The `PathHandle` path checks encoded constraints such as path, content identity, or metadata stability; unsupported filesystems throw `UnsupportedOperationException`.

Listing and glob flow uses eager arrays for `listStatus`/`globStatus` and remote iterators for `listLocatedStatus`, `listStatusIterator`, `listFiles`, `FileContext.listStatus`, and related APIs. The docs explicitly warn that some iterator flows do not guarantee sorted order.

Metadata extension flow for ACLs, xattrs, snapshots, and storage policies is exposed on both `FileContext` and `FileSystem`. The default `FileSystem` contract often permits `UnsupportedOperationException`, while HDFS-backed implementations are expected to provide behavior.

`FileUtil` deletion flow distinguishes symlink deletion from target deletion for `fullyDelete(File)`, but `fullyDeleteContents(File)` follows a symlink to a directory and deletes the target directory contents. Copy flow composes source and destination `FileSystem` handles, paths or local files, delete-source semantics, overwrite policy, and `Configuration`.

`FilterFileSystem` control flow is delegation: wrapper methods should validate/qualify through the wrapper where required and forward actual operations to the raw filesystem. The chunk ends before the full delegation surface is visible.

## State and Persistence Behavior

This JDiff file persists API metadata for compatibility checking. It does not store live Hadoop runtime state.

`FileContext` contains client-side, in-memory state: default filesystem, working directory, user/group identity, umask, delete-on-exit registrations, and statistics access. Its operations mutate remote filesystem namespace state through the selected `AbstractFileSystem`: file contents, directories, symlinks, permissions, ACLs, xattrs, snapshots, storage policies, ownership, timestamps, replication, and truncation.

`FileStatus` is a serializable metadata value object. Its `Writable` stream methods remain for compatibility but are deprecated in favor of protobuf conversion. Equality, ordering, and hashing are path-based, which means metadata changes on the same path do not change equality identity.

`FileChecksum` is a `Writable` value contract. Durable equality depends on both algorithm name and raw bytes, while `getChecksumOpt()` connects a checksum value back to checksum configuration.

`FileSystem` has substantial process-local global state: cached filesystem instances, global statistics, global storage statistics, symlink enablement, default filesystem configuration keys, shutdown hooks, and delete-on-exit queues. Individual instances maintain configuration and protected `statistics`. Persistent effects are delegated to concrete filesystems and may be local disk state, HDFS namespace/block state, object-store objects, or third-party backend state.

`FileUtil` is mostly stateless, but many methods produce durable local or filesystem side effects: recursive deletion, permission and owner changes, symlink creation, archive extraction, temp-file creation, file replacement, copy, and optional source deletion. `createJarWithClassPath` creates a small manifest jar and returns paths describing generated and unexpanded wildcard entries.

`FilterFileSystem` stores a raw wrapped `FileSystem` reference. Its durable behavior should mirror the wrapped filesystem unless the filter subclass modifies semantics.

## Dependencies and Integration Points

The chunk is centered on `org.apache.hadoop.fs` and integrates with:

- Java core types: `URI`, `File`, `IOException`, `FileNotFoundException`, `DataInput`, `DataOutput`, `Serializable`, `ObjectInputValidation`, collections, streams, and concurrency exceptions for untar helpers.
- Hadoop configuration and identity: `Configuration`, `Configured`, `UserGroupInformation`, `AccessControlException`, and delegation-token service naming.
- Hadoop filesystem primitives: `Path`, `AbstractFileSystem`, `FileSystem`, `LocalFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `PathHandle`, `RemoteIterator`, `BlockLocation`, `FsStatus`, `FsServerDefaults`, `ContentSummary`, `QuotaUsage`, `BlockStoragePolicySpi`, `StorageStatistics`, and `GlobalStorageStatistics`.
- Hadoop permission and metadata APIs: `FsPermission`, `AclStatus`, ACL entry lists, xattr set flags, checksum options, and create/rename/handle options.
- Hadoop utility APIs: `Progressable`, `Writable`, `PBHelper`, `NetUtils`, `SecurityUtil`, service discovery through `ServiceLoader`, and logging through SLF4J or Commons Logging.
- HDFS-specific behavior: block locations, replication, erasure-coded logical block groups, snapshots, xattrs, storage policies, and HDFS as the documented normative behavior source when docs disagree with implementation.

Integration-sensitive points are filesystem plugin discovery by URI scheme, caching keyed by URI/user/configuration behavior, statistics registration, token canonical service naming, and the compatibility bridge between `FileSystem` and newer `FileContext`/`AbstractFileSystem` APIs.

## Risks and Edge Cases

- This chunk begins and ends mid-class. The previous chunk is required for complete `CreateFlag`; the next chunk is required for complete `FilterFileSystem`.
- JDiff does not show method bodies. Exact cache keys, permission application, path normalization, retry behavior, RPC details, and exception messages require Java implementation review.
- `CreateFlag` combinations are easy to misuse. In particular, `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE` must fail, while `CREATE|APPEND` and `CREATE|OVERWRITE` have different existence semantics.
- `FileContext.setWorkingDirectory` does not follow symlinks like a Unix process working directory. Code that assumes inode-like working directory behavior can resolve later relative paths differently than expected.
- `FileStatus.equals` and `hashCode` are path-based. Caches keyed by `FileStatus` can miss metadata changes if they assume equality covers length, permission, timestamps, or file type.
- `FileStatus.readFields`/`write` are deprecated but public. Removing or changing their protobuf-backed format would break old clients and serialized compatibility.
- `FileSystem.get` returns cached shared instances unless cache is disabled. Closing a shared instance can break other users; using `newInstance` avoids sharing but increases resource usage.
- `FileSystem.close()` makes later use of the instance and its streams undefined. Tests and applications must avoid reusing streams after filesystem closure.
- `FileSystem.initialize` overriding is fragile because subclasses must call the superclass. Skipping it can corrupt cache/statistics/configuration setup.
- `getFileBlockLocations` has special behavior for nonexistent paths, zero-length regions, default local locations, and HDFS erasure-coded logical block groups. Consumers must handle null, empty arrays, and logical rather than physical block semantics.
- Many optional APIs default to `UnsupportedOperationException`: path handles, symlinks, ACLs, xattrs, snapshots, and storage policies depend on concrete filesystem support.
- Trash-root defaults are user-home based, while object stores and multi-root filesystems may override them. Delete-to-trash code must not hardcode `/user/$USER/.Trash`.
- Global statistics APIs are synchronized and some are deprecated in favor of `GlobalStorageStatistics`; both old and new stats may need validation during compatibility work.
- `FileUtil.fullyDelete` can leave partial deletion on failure. `fullyDeleteContents` follows directory symlinks and deletes target contents, unlike `fullyDelete` symlink handling.
- `FileUtil.readLink` returns an empty string both for non-symlinks and errors, collapsing distinct states.
- `FileUtil.makeSecureShellPath` exists because shell path conversion can otherwise permit script injection. Callers should use the secure variant for untrusted local paths.
- `FileUtil.unTar(InputStream, ...)` can throw `InterruptedException` and `ExecutionException`, suggesting asynchronous or shell-backed extraction paths that must be tested under interruption and command failure.
- Windows behavior is explicitly different for symlink privilege failures, chmod/access checks, and executable permission revocation on directories.
- `createJarWithClassPath` expands environment variables and wildcards differently on Windows versus Unix-like systems. Manifest classpath behavior can diverge from process classpath behavior.

## Test Signals

Useful validation for this API surface should include:

- JDiff/API compatibility tests ensuring all visible classes, constructors, methods, fields, deprecations, and checked exceptions remain stable.
- `CreateFlag` validation tests for every documented create/append/overwrite combination, including invalid mixed append/overwrite cases and `APPEND_NEWBLOCK`, `SYNC_BLOCK`, and `LAZY_PERSIST` preservation.
- `FileChecksum` tests for algorithm/byte equality, hash code consistency, checksum option exposure, and `Writable` round trips in concrete checksum subclasses.
- `FileContext` tests for default/local/URI/config factories, UGI propagation, working-directory resolution, invalid relative-with-scheme paths, umask application, create/mkdir/delete/open/truncate/rename behavior, symlink resolution, delete-on-exit, and statistics.
- `FileContext` metadata tests for ACL merge/remove/replace/read, xattr set/get/list/remove with namespaces and flags, snapshots, storage policies, checksum verification flags, and unsupported-filesystem failure modes.
- `FileStatus` tests for all constructor variants, null permission/owner/group defaults, attribute flag conversion, deprecated `isDir`, symlink target behavior, path-based equality/ordering/hash code, Java deserialization validation, and deprecated `Writable` serialization compatibility.
- `FileSystem` cache tests for default URI selection, scheme implementation loading, `fs.$SCHEME.impl.disable.cache`, user-specific `get`, `newInstance` uniqueness, `closeAll`, `closeAllForUGI`, and use-after-close behavior.
- `FileSystem` operation tests for path qualification/checking, canonical URI/default port handling, token canonical service names, open/create/append overloads, nonrecursive create, path handles and invalid handles, mkdirs, concat, replication, rename options, truncate return semantics, delete/delete-on-exit, glob/list/listFiles ordering expectations, and local copy helpers.
- HDFS-specific signals for block locations, including replicated files and erasure-coded logical block groups, plus snapshots, xattrs, storage policies, ACLs, and trash roots.
- `FileUtil` tests for symlink-safe recursive deletion, partial deletion failure reporting, `fullyDeleteContents` symlink-to-directory behavior, cross-filesystem copy with overwrite/delete-source options, local copy direction, shell path conversion and secure escaping, disk usage, zip/tar extraction, Windows symlink privilege code, chmod/chown/access wrappers, permission setting without forking when possible, temp-file lifecycle, replacement behavior, and list/listFiles throwing `IOException` instead of returning null.
- `createJarWithClassPath` tests for long classpaths, manifest classpath generation, environment expansion on Windows and Unix syntax, wildcard expansion for `.jar` and `.JAR`, target directory handling, and returned path array contract.
- `FilterFileSystem` delegation tests in the next merged report should verify raw filesystem initialization, URI qualification, open/append/create delegation, path-handle delegation, and statistics/close behavior across the full class.

## Cross-Chunk Notes

The previous chunk must supply the beginning of `org.apache.hadoop.fs.CreateFlag`, including enum constants not fully visible here. This chunk closes `CreateFlag` and then covers the major filesystem API classes through most of line 12080.

The next chunk must continue `org.apache.hadoop.fs.FilterFileSystem` from its `create(Path, FsPermission, boolean, int, ...)` method onward. Any final per-file report should avoid treating this chunk's `FilterFileSystem` notes as complete until that adjacent slice is merged.
