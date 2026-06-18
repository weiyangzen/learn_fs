# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.4.xml lines 6122-12095

## Purpose

This chunk is a JDiff-generated public API description for Apache Hadoop Common 3.2.4, not executable Java source. Its research value is the exported contract: class names, inheritance, implemented interfaces, method and constructor signatures, checked exceptions, field visibility, deprecation state, and embedded Javadoc. The span starts inside the tail of `org.apache.hadoop.fs.ContentSummary`, covers core `org.apache.hadoop.fs` creation/status/context/filesystem APIs, and ends inside the beginning of `org.apache.hadoop.fs.FileUtil`.

This is a central filesystem API slice. It documents both the older `FileSystem` abstraction and the newer `FileContext` abstraction, plus value objects and utilities that all Hadoop filesystems, HDFS clients, object stores, local filesystem code, command-line tools, and tests integrate with.

## API Inventory

### `org.apache.hadoop.fs.ContentSummary` tail

- The chunk begins after earlier `ContentSummary` declarations and includes output/formatting methods: `getErasureCodingPolicy()`, `equals(Object)`, `hashCode()`, static `getHeader(boolean)`, static `getHeaderFields()`, static `getQuotaHeaderFields()`, and multiple `toString(...)` overloads.
- The `toString` overloads format directory count, file count, content size, quotas, human-readable sizes, per-storage-type quotas, and snapshot-inclusion behavior. The five-argument overload `toString(boolean qOption, boolean hOption, boolean tOption, boolean xOption, List types)` is the complete formatter referenced by shorter overloads.
- This is a value/reporting object for content summary data; earlier fields and constructors are outside this chunk and must be reconciled with preceding chunks.

### `CreateFlag`

- `CreateFlag` is a public final enum describing file-create and append semantics.
- Static enum APIs are present: `values()` and `valueOf(String)`.
- Validation APIs are `validate(EnumSet flag)`, `validate(Object path, boolean pathExists, EnumSet flag)`, and `validateForAppend(EnumSet flag)`.
- Documented valid semantics include `CREATE`, `APPEND`, `OVERWRITE`, `CREATE|APPEND`, `CREATE|OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`.
- Invalid combinations include `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`, which raise `HadoopIllegalArgumentException`; create validation can also raise `IOException` for path-existence semantics.

### `FileAlreadyExistsException`

- `FileAlreadyExistsException` extends `java.io.IOException`.
- It has no-arg and message constructors.
- It is the create/rename-style failure used when a target already exists and overwrite behavior was not requested.

### `FileChecksum`

- `FileChecksum` is an abstract `Writable` value contract for file checksum implementations.
- Subclasses must implement `getAlgorithmName()`, `getLength()`, and `getBytes()`.
- The base API also exposes `getChecksumOpt()`, `equals(Object)`, and `hashCode()`.
- Equality is defined by checksum algorithm and checksum bytes. Serialization behavior is inherited from the `Writable` contract implemented by concrete subclasses.

### `FileContext`

- `FileContext` is a public facade implementing `PathCapabilities`. It is documented as the Unix-like per-process filesystem state analogue: default filesystem, working directory, user identity, and umask.
- Factory methods create contexts from an `AbstractFileSystem`, a default `URI`, a `Configuration`, the process default configuration, or the local filesystem. Unsupported default schemes raise `UnsupportedFileSystemException`; URI/config instantiation can raise runtime failures when a supported filesystem cannot be created or login fails.
- Path resolution and naming APIs include protected `getFSofPath(Path)`, `resolvePath(Path)`, `makeQualified(Path)`, `setWorkingDirectory(Path)`, `getWorkingDirectory()`, `getHomeDirectory()`, `getUgi()`, `getUMask()`, and `setUMask(FsPermission)`.
- Mutating namespace APIs include `create(Path, EnumSet, Options.CreateOpts...)`, `create(Path)` returning `FSDataOutputStreamBuilder`, `mkdir(Path, FsPermission, boolean)`, `delete(Path, boolean)`, `truncate(Path, long)`, `rename(Path, Path, Options.Rename...)`, `setReplication(Path, short)`, `setPermission(Path, FsPermission)`, `setOwner(Path, String, String)`, and `setTimes(Path, long, long)`.
- Data access APIs include `open(Path)`, `open(Path, int)`, `getFileChecksum(Path)`, `setVerifyChecksum(boolean)`, `getFileStatus(Path)`, `getFileLinkStatus(Path)`, `getLinkTarget(Path)`, `getFsStatus(Path)`, `listStatus(Path)`, `listLocatedStatus(Path)`, and `listCorruptFileBlocks(Path)`.
- Symlink and resolution helpers include `createSymlink(Path target, Path link, boolean createParent)`, `resolve(Path)`, and `resolveIntermediate(Path)`.
- Delete-on-exit and utility integration are exposed through `deleteOnExit(Path)` and `util()`.
- ACL APIs include `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, and `getAclStatus`.
- XAttr APIs include two `setXAttr` overloads, `getXAttr`, two `getXAttrs` overloads, `removeXAttr`, and `listXAttrs`. XAttr names must include a namespace prefix such as `user.attr`; returned xattrs are permission-filtered.
- Snapshot APIs include `createSnapshot(Path)`, `createSnapshot(Path, String)`, `renameSnapshot`, and `deleteSnapshot`.
- Storage policy APIs include `satisfyStoragePolicy`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, and `getAllStoragePolicies`.
- Capability/statistics APIs include `hasPathCapability(Path, String)`, static `getStatistics(URI)`, `clearStatistics()`, `printStatistics()`, and `getAllStatistics()`.
- Public fields include `LOG`, compatibility `DEFAULT_PERM`, preferred `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`.

### `FileStatus`

- `FileStatus` is a public client-side file metadata value object implementing `Writable`, `Comparable`, `Serializable`, and `ObjectInputValidation`.
- Constructors cover empty status, common file metadata, symlink-aware metadata, boolean attribute metadata, attribute-set metadata, and a copy constructor.
- Static `attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts ACL/encryption/erasure-coding/snapshot booleans into an attribute flag set. `NONE` is the shared empty attribute set.
- Accessors include length, file/directory/symlink classification, block size, replication, modification/access times, permission, ACL presence, encryption, erasure coding, snapshot-enabled flag, owner, group, path, and symlink target.
- Mutators are limited mostly to path/symlink plus protected normalization hooks for permission, owner, and group.
- Comparison, equality, and hash code are path-based. The `compareTo(Object)` overload is explicitly retained for binary compatibility after HADOOP-14683.
- `readFields(DataInput)` and `write(DataOutput)` are deprecated in favor of direct protobuf serialization through `PBHelper`; both document protobuf encoding. `validateObject()` supports Java serialization validation.
- `isDir()` is deprecated in favor of explicit `isFile()`, `isDirectory()`, and `isSymlink()`.

### `FileSystem`

- `FileSystem` is the abstract, configurable filesystem base class. It extends `Configured` and implements `java.io.Closeable`, `DelegationTokenIssuer`, and `PathCapabilities`.
- Static construction APIs include `get(Configuration)`, `get(URI, Configuration)`, `get(URI, Configuration, String user)`, `getLocal(Configuration)`, `newInstance(Configuration)`, `newInstance(URI, Configuration)`, `newInstance(URI, Configuration, String user)`, and `newInstanceLocal(Configuration)`.
- `get(URI, Configuration)` documents cache behavior: return an uncached new instance when `fs.$SCHEME.impl.disable.cache` is true, reuse a matching cached instance when available, or instantiate, initialize, cache, and return a new filesystem. `newInstance(...)` always returns a unique filesystem instance.
- URI/configuration APIs include `getDefaultUri`, two `setDefaultUri` overloads, `initialize(URI, Configuration)`, `getScheme()`, abstract `getUri()`, protected `getCanonicalUri()`, protected `canonicalizeUri(URI)`, protected `getDefaultPort()`, protected static `getFSofPath(Path, Configuration)`, `getCanonicalServiceName()`, deprecated `getName()`, deprecated `getNamed(String, Configuration)`, `makeQualified(Path)`, and protected `checkPath(Path)`.
- Core data and namespace APIs include many `create(...)` overloads, `primitiveCreate`, `primitiveMkdir`, `mkdirs(...)`, `createNonRecursive(...)`, `createNewFile`, `open(...)`, `append(...)`, `concat`, `rename(...)`, `truncate`, `delete(...)`, `deleteOnExit`, `cancelDeleteOnExit`, `processDeleteOnExit`, `exists`, `isDirectory`, `isFile`, `getLength`, `getFileStatus`, and `msync()`.
- Listing/search APIs include `listStatus(...)`, `listCorruptFileBlocks(Path)`, `globStatus(...)`, `listLocatedStatus(...)`, `listStatusIterator(Path)`, and recursive `listFiles(Path, boolean)`.
- File locality and server-default APIs include `getFileBlockLocations(...)`, `getServerDefaults()`, `getServerDefaults(Path)`, `getStatus()`, `getStatus(Path)`, `getUsed()`, `getUsed(Path)`, `getBlockSize(Path)`, `getDefaultBlockSize()`, `getDefaultBlockSize(Path)`, `getDefaultReplication()`, and `getDefaultReplication(Path)`.
- Local copy APIs include multiple `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, `moveToLocalFile`, `startLocalOutput`, and `completeLocalOutput`.
- Symlink APIs include `createSymlink`, `getFileLinkStatus`, `supportsSymlinks`, `getLinkTarget`, `resolveLink`, static `areSymlinksEnabled()`, and static `enableSymlinks()`.
- Checksum APIs include `getFileChecksum(Path)`, `getFileChecksum(Path, long)`, `setVerifyChecksum(boolean)`, and `setWriteChecksum(boolean)`.
- Metadata mutation includes `setReplication`, `setPermission`, `setOwner`, `setTimes`, quotas (`getContentSummary`, `getQuotaUsage`, `setQuota`, `setQuotaByStorageType`), snapshots, ACLs, xattrs, storage policy operations, trash roots, and path capabilities.
- Pluggability/statistics APIs include `getFileSystemClass(String, Configuration)`, deprecated global `getStatistics`/`getAllStatistics` APIs, `clearStatistics`, `printStatistics`, per-instance `getStorageStatistics()`, global `getGlobalStorageStatistics()`, `createFile(Path)` builder, and `appendFile(Path)` builder.
- Public/protected fields include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, widely used `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and protected per-filesystem `statistics`.

### `FileUtil` start

- The chunk begins `FileUtil`, a static local/remote filesystem utility class, but stops at the declaration of `createLocalTempFile(...)`; later chunks must complete the class.
- APIs in this slice include `stat2Paths(...)`, `fullyDeleteOnExit(File)`, `fullyDelete(File)`, `fullyDelete(File, boolean)`, `readLink(File)`, `fullyDeleteContents(File)`, `fullyDeleteContents(File, boolean)`, deprecated `fullyDelete(FileSystem, Path)`, multiple `copy(...)` overloads, `makeShellPath(...)`, `makeSecureShellPath(File)`, `getDU(File)`, `unZip(...)`, `unTar(...)`, `symLink(String, String)`, `chmod(...)`, `setOwner(File, String, String)`, platform-independent `setReadable`, `setWritable`, `setExecutable`, `canRead`, `canWrite`, `canExecute`, and `setPermission(File, FsPermission)`.
- The deletion APIs distinguish symlinks from normal directories: deleting a symlink deletes the link, not the linked file or directory. `fullyDeleteContents`, however, warns that when passed a symlink to a directory it deletes contents of the actual target directory.
- Shell/path APIs explicitly handle Windows subprocess issues and include a secure shell path variant intended to avoid script injection.

## Control Flow and Behavior

- `FileContext` operations resolve relative, slash-relative, and fully qualified `Path` values through its working directory and default `AbstractFileSystem`. Relative paths with a scheme are invalid. Once a target filesystem is selected, operations delegate to that `AbstractFileSystem`.
- `FileContext.create(Path)` returns a builder whose `build()` call performs parameter verification in `FileContext` and `AbstractFileSystem#create`, then mutates filesystem state by creating or overwriting the file.
- `FileSystem.get(...)` is the main cached factory path. It discovers/loads the implementation class for the scheme, initializes the filesystem, and reuses cached instances unless the per-scheme cache-disable key is set. `newInstance(...)` bypasses that cache path.
- `FileSystem.initialize(...)` is a subclass lifecycle hook. Implementations overriding it must call the superclass implementation before the instance is considered ready.
- `FileSystem` convenience methods layer on primitive filesystem operations. Examples in this chunk include recursive listing over `listStatus`/`listLocatedStatus`, delete-on-exit registration and later `processDeleteOnExit`, two-RPC permission-specific `create(FileSystem, Path, FsPermission)`, and local copy helpers delegating through `FileUtil`.
- `CreateFlag.validate(...)` centralizes create/append semantic checks before mutating calls are issued, preventing ambiguous append/overwrite combinations.
- `FileStatus` control flow is mostly value-object behavior: comparisons and equality use the path, while deprecated `Writable` serialization encodes/decodes a protobuf representation.
- `FileUtil` methods are procedural utilities around local filesystem mutation, shell command invocation, archive extraction, and cross-filesystem copy.

## State and Persistence

- The XML itself persists API metadata for compatibility comparison; it does not contain implementation bodies.
- `FileContext` stores client-side state: default filesystem, working directory, UGI, umask, delete-on-exit registrations, and statistics. It does not persist filesystem data directly, but its mutating APIs create, remove, or update remote/local filesystem namespace and metadata.
- `FileSystem` instances hold configuration-derived identity, URI, per-instance statistics, and possibly cached global lifecycle state. Static caches are observable through `get`, `newInstance`, `closeAll`, and `closeAllForUGI`.
- `FileSystem` mutating calls persist external filesystem effects: file contents, directories, metadata, ACLs, xattrs, quotas, snapshots, storage policies, trash roots, symlinks, and local-copy output.
- `FileStatus`, `ContentSummary`, and `FileChecksum` are serializable/reporting value objects. `FileStatus` has deprecated `Writable` protobuf serialization and Java object validation.
- `FileUtil` can persist destructive local changes via recursive deletion, permission/owner changes, symlink creation, archive extraction, and copy/delete-source operations.

## Dependencies and Integration Points

- Core dependencies are `org.apache.hadoop.conf.Configuration`, `org.apache.hadoop.fs.Path`, `AbstractFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `RemoteIterator`, `FileStatus`, `ContentSummary`, `QuotaUsage`, `FsStatus`, `BlockLocation`, `BlockStoragePolicySpi`, `StorageStatistics`, and `GlobalStorageStatistics`.
- Security integration includes `UserGroupInformation`, Hadoop `AccessControlException`, `DelegationTokenIssuer`, canonical service names for token caches, and permission/ACL classes under `org.apache.hadoop.fs.permission`.
- Error surfaces include `IOException`, `FileNotFoundException`, `FileAlreadyExistsException`, `ParentNotDirectoryException`, `UnsupportedFileSystemException`, `UnresolvedLinkException`, `InvalidObjectException`, RPC client/server exception families documented in Javadoc, and `UnsupportedOperationException` defaults for optional features.
- Pluggability flows through URI schemes, `ServiceLoader` discovery in `getFileSystemClass`, configuration keys such as `fs.defaultFS`/`FS_DEFAULT_NAME_KEY`, per-scheme cache disablement, and filesystem-specific implementations for HDFS, local filesystems, object stores, and third-party filesystems.
- Compatibility integration is broad: the `FileSystem.LOG` field is documented as widely used in `org.apache.hadoop.fs` code and tests, deprecated APIs remain for binary/source compatibility, and builder APIs are marked as temporarily reduced/stabilizing around HADOOP-14384.
- `FileUtil` integrates Java `File`, shell commands, permissions, archive streams, Hadoop `FileSystem`, and `Configuration`; behavior differs across Unix and Windows.

## Risks and Edge Cases

- This chunk is API metadata. It cannot prove implementation details beyond documented behavior; final research should reconcile this with Java source if implementation behavior is required.
- The chunk starts mid-`ContentSummary` and ends mid-`FileUtil`, so class-level conclusions for those two types are incomplete without adjacent chunks.
- `FileSystem` caching can cause lifecycle bugs when callers assume `get(...)` returns a fresh instance; `closeAll` and `closeAllForUGI` can invalidate shared cached instances.
- `FileContext` path resolution differs from Unix inode working directories: working directories are prefixed into relative paths and do not follow symlinks when set.
- Create semantics are subtle. Incorrect `CreateFlag` combinations or misuse of append/overwrite flags can cause unexpected `IOException` or `HadoopIllegalArgumentException`.
- Optional features such as ACLs, xattrs, snapshots, storage policies, symlinks, truncation, append, path handles, and capabilities may default to unsupported on some filesystems.
- Permission behavior has compatibility traps: `DEFAULT_PERM` historically gave files executable bits, so callers should prefer `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`.
- `FileStatus` equality and ordering by path can hide metadata differences when statuses for the same path differ in length, owner, ACL, encryption, or timestamps.
- Deprecated `FileStatus` `Writable` serialization and deprecated statistics APIs remain compatibility surfaces; tests should catch accidental removal or signature drift.
- `FileUtil.fullyDeleteContents` has a dangerous symlink-to-directory behavior documented in this chunk: it can delete target directory contents. Archive extraction and shell path helpers also need traversal and injection scrutiny.
- Windows-specific permission and symlink behavior differs from Unix, including `symLink` return code `2` for security-setting failure and folder execute-permission caveats.

## Test Signals

- API compatibility tests should compare JDiff output for method signatures, deprecation text, checked exceptions, implemented interfaces, and public fields for `FileContext`, `FileStatus`, `FileSystem`, and `FileUtil`.
- Factory/cache tests should cover `FileSystem.get`, `newInstance`, per-scheme cache-disable configuration, `closeAll`, and `closeAllForUGI`.
- Path-resolution tests should cover `FileContext` and `FileSystem` with fully qualified, slash-relative, working-directory-relative, illegal scheme-relative, symlink, and mount-point paths.
- Create/open/delete/rename/truncate tests should exercise `CreateFlag` validation, parent creation, overwrite/append combinations, recursive delete behavior, and cross-filesystem rename/error cases.
- Metadata tests should cover `FileStatus` path-based equality/comparison, protobuf serialization compatibility, attribute flags, deprecated `isDir()`, and `ObjectInputValidation`.
- Feature-surface tests should cover ACLs, xattrs, snapshots, quotas, storage policies, trash roots, symlinks, checksums, path capabilities, storage statistics, and unsupported-operation defaults across representative filesystems.
- Local utility tests should cover `FileUtil` recursive delete on normal files/directories and symlinks, copy with `deleteSource` and `overwrite`, shell path escaping, archive extraction, chmod/chown permission behavior, and platform-specific Windows branches.
