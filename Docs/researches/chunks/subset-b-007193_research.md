# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.2.xml lines 6125-12096

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.2.2. It begins inside the tail of `org.apache.hadoop.fs.ContentSummary`, then covers complete public API metadata for `CreateFlag`, `FileAlreadyExistsException`, `FileChecksum`, `FileContext`, `FileStatus`, and `FileSystem`. It then enters `FileUtil` and covers its public API through the beginning of `createLocalTempFile(File, String, boolean)`, where the line range ends mid-method documentation.

The source is generated compatibility metadata rather than implementation source. The research surface is therefore the Hadoop public/protected API contract: type names, inheritance, implemented interfaces, fields, method signatures, checked exceptions, static/final/abstract/synchronized markers, deprecations, and embedded Javadocs.

## Purpose

The visible `ContentSummary` tail documents command-output formatting for namespace and quota summaries. It exposes string and header rendering paths for directory count, file count, content size, quota, storage-type quota, human-readable units, and snapshot-exclusion behavior.

`CreateFlag` defines file creation and append semantics shared by `FileContext`, `FileSystem`, builders, and lower-level filesystem implementations. It validates combinations such as `CREATE`, `APPEND`, `OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`.

`FileAlreadyExistsException` is the public checked exception used when an operation targets an existing file or directory and overwrite semantics are not enabled.

`FileChecksum` is the abstract serializable checksum contract for files. It identifies the checksum algorithm, byte length, byte value, and checksum options, and defines equality based on algorithm and value.

`FileContext` is Hadoop's higher-level filesystem interface and the documented successor-style API for per-client file state. It binds a default `AbstractFileSystem`, working directory, user identity, and umask, then exposes create, open, mkdir, delete, rename, truncate, listing, symlink, ACL, xattr, snapshot, storage-policy, and capability operations across URI-addressed filesystems.

`FileStatus` is the client-side metadata record for a file, directory, or symlink. It carries path, length, replication, block size, timestamps, permissions, owner/group, symlink target, and attribute flags for ACL, encryption, erasure coding, and snapshot support. It is comparable, Java-serializable, Hadoop-`Writable`, and validates object deserialization.

`FileSystem` is the long-standing abstract base class for Hadoop filesystems. It is implemented by local, HDFS, object-store, and third-party filesystems and defines URI resolution, instance caching, path qualification, create/open/append/delete/list APIs, metadata mutation, checksums, ACLs, xattrs, snapshots, storage policies, trash roots, statistics, storage statistics, path capabilities, and builder entry points.

The visible `FileUtil` portion provides static bridge utilities for converting `FileStatus` arrays to paths, deleting local trees, copying between local and Hadoop filesystems, adapting paths for shell commands, unpacking archives, creating symlinks, changing permissions/owners, and performing platform-independent local permission checks.

## Important APIs, Types, and Functions

### ContentSummary Tail

- `hashCode()` is present at the chunk start, indicating `ContentSummary` participates in value-style comparison.
- `getHeader(boolean qOption)` returns formatted summary headers. Without quota it covers directory count, file count, and content size; with quota it adds quota and remaining quota fields.
- `getHeaderFields()` and `getQuotaHeaderFields()` expose the column names used by summary output.
- `toString()` overloads render the summary with combinations of quota output, human-readable units, storage-type quota output, snapshot exclusion, and explicit `StorageType` lists.

### CreateFlag and Exceptions

- `CreateFlag` is a public enum. Normal enum methods `values()` and `valueOf(String)` are exposed.
- `validate(EnumSet)` checks for invalid flag combinations and throws `HadoopIllegalArgumentException`.
- `validate(Object path, boolean pathExists, EnumSet flag)` applies create-operation semantics to a path and whether it exists, throwing `IOException` and `HadoopIllegalArgumentException`.
- `validateForAppend(EnumSet)` requires `APPEND` and rejects `OVERWRITE` for append operations.
- The documented valid combinations include create-if-absent, append-if-present, overwrite-if-present, create-or-append, create-or-overwrite, sync block, lazy persist, and append-to-new-block. Invalid combinations include `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`.
- `FileAlreadyExistsException` extends `IOException` and has no-arg and message constructors.

### FileChecksum

- `FileChecksum` is abstract and implements `Writable`.
- Abstract methods `getAlgorithmName()`, `getLength()`, and `getBytes()` define the checksum identity and bytes.
- `getChecksumOpt()` returns an `Options.ChecksumOpt` when available.
- `equals(Object)` returns true only when checksum algorithms and values match; `hashCode()` accompanies that equality contract.

### FileContext

- `FileContext` implements `PathCapabilities`.
- Static factory overloads create contexts from an `AbstractFileSystem`, default config, local filesystem, default `URI`, explicit `Configuration`, or both URI and configuration.
- `getFSofPath(Path)` resolves an absolute or fully qualified path to an `AbstractFileSystem`, throwing `UnsupportedFileSystemException` or `IOException`.
- Working-directory APIs are `setWorkingDirectory(Path)` and `getWorkingDirectory()`. The Javadocs emphasize that working-directory resolution is prefix-based and does not follow symlinks like Unix inode current directories.
- Identity and defaults include `getUgi()`, `getHomeDirectory()`, `getUMask()`, and `setUMask(FsPermission)`.
- Path handling includes `resolvePath(Path)` for following symlinks and mount points, and `makeQualified(Path)` for filling in default filesystem and working-directory context.
- Core mutation APIs include `create(Path, EnumSet<CreateFlag>, CreateOpts...)`, builder `create(Path)`, `mkdir(Path, FsPermission, boolean)`, `delete(Path, boolean)`, `truncate(Path, long)`, `setReplication(Path, short)`, `rename(Path, Path, Rename...)`, `setPermission`, `setOwner`, `setTimes`, `createSymlink`, and delete-on-exit registration.
- Read and status APIs include `open(Path)`, `open(Path, int)`, `getFileStatus(Path)`, `getFileLinkStatus(Path)`, `getLinkTarget(Path)`, `getFileChecksum(Path)`, `getFsStatus(Path)`, `listStatus(Path)`, `listCorruptFileBlocks(Path)`, and `listLocatedStatus(Path)`.
- Utility and statistics APIs include `util()`, `resolve(Path)`, `resolveIntermediate(Path)`, `getStatistics(Path)`, `clearStatistics()`, `printStatistics()`, and `getAllStatistics()`.
- Metadata extension APIs include ACL methods (`modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, `getAclStatus`) and xattr methods (`setXAttr`, flagged `setXAttr`, `getXAttr`, all/named `getXAttrs`, `removeXAttr`, `listXAttrs`).
- Snapshot APIs include default-name and explicit-name `createSnapshot`, `renameSnapshot`, and `deleteSnapshot`.
- Storage policy APIs include `satisfyStoragePolicy`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, and `getAllStoragePolicies`.
- `hasPathCapability(Path, String)` delegates capability checks to the bonded `AbstractFileSystem`.
- Public fields include `LOG`, compatibility `DEFAULT_PERM`, preferred `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`.

### FileStatus

- `FileStatus` implements `Writable`, raw `Comparable`, `Serializable`, and `ObjectInputValidation`.
- Constructors cover empty deserialization, compact status without permissions, status without symlink support, status with symlink, status with boolean ACL/encryption/erasure flags, status with a set of attributes, and a copy constructor.
- `attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts booleans into an attribute-flag set.
- Accessors expose length, file/directory/symlink classification, block size, replication, modification time, access time, permission, ACL flag, encryption flag, erasure-coded flag, snapshot-enabled flag, owner, group, path, and symlink target.
- Mutators include `setPath(Path)`, protected `setPermission`, protected `setOwner`, protected `setGroup`, and public `setSymlink(Path)`.
- `isDir()` is final and deprecated in favor of `isFile()`, `isDirectory()`, and `isSymlink()`.
- `compareTo(FileStatus)` and `compareTo(Object)` compare file statuses; the object overload was restored for binary compatibility by HADOOP-14683.
- `equals(Object)` and `hashCode()` are path-name based.
- `readFields(DataInput)` and `write(DataOutput)` encode as protobuf but are deprecated in favor of using `PBHelper` and protobuf serialization directly.
- `validateObject()` supports Java deserialization validation, and `NONE` is a shared empty attribute set.

### FileSystem

- `FileSystem` extends `Configured` and implements `Closeable`, `DelegationTokenIssuer`, and `PathCapabilities`.
- Static lookup APIs include `get(Configuration)`, `get(URI, Configuration)`, `get(URI, Configuration, String user)`, `newInstance(...)`, `newInstanceLocal(Configuration)`, `getLocal(Configuration)`, `getNamed(String, Configuration)` deprecated, `getDefaultUri(Configuration)`, and `setDefaultUri(...)`.
- Instance lifecycle and identity include protected constructor, `initialize(URI, Configuration)`, abstract `getUri()`, default `getScheme()`, protected `getCanonicalUri()`, `canonicalizeUri(URI)`, `getDefaultPort()`, `getCanonicalServiceName()`, deprecated `getName()`, `close()`, `closeAll()`, and `closeAllForUGI(UserGroupInformation)`.
- URI and path checks include static protected `getFSofPath(Path, Configuration)`, `makeQualified(Path)`, and protected `checkPath(Path)`.
- Creation APIs include static permission-preserving `create(FileSystem, Path, FsPermission)`, many `create(...)` overloads with overwrite, buffer size, replication, block size, progress, checksum options, and permission, `primitiveCreate`, non-recursive creation overloads, `createNewFile`, and builder `createFile(Path)`.
- Directory APIs include static `mkdirs(FileSystem, Path, FsPermission)`, instance `mkdirs(Path)`, abstract `mkdirs(Path, FsPermission)`, `primitiveMkdir`, and `primitiveMkdir(Path, FsPermission)`.
- Read and append APIs include multiple `open(...)` overloads, builder-related `getPathHandle` and `createPathHandle`, append overloads, and builder `appendFile(Path)`.
- Block and server-default APIs include `getFileBlockLocations(FileStatus, long, long)`, `getFileBlockLocations(Path, long, long)`, `getServerDefaults()`, and `getServerDefaults(Path)`.
- Mutating filesystem APIs include abstract `rename(Path, Path)`, protected option-based `rename(Path, Path, Rename...)`, `concat`, `truncate`, abstract recursive `delete`, deprecated one-argument `delete`, `setReplication`, `setPermission`, `setOwner`, `setTimes`, quotas, ACLs, xattrs, snapshots, storage policies, and `msync()`.
- Delete-on-exit APIs are `deleteOnExit(Path)`, `cancelDeleteOnExit(Path)`, and protected `processDeleteOnExit()`.
- Status and listing APIs include `exists`, deprecated `isDirectory`, deprecated `isFile`, deprecated `getLength`, `getContentSummary`, `getQuotaUsage`, abstract `listStatus(Path)`, filtered and multi-path `listStatus` overloads, `globStatus` overloads, `listLocatedStatus`, protected filtered `listLocatedStatus`, `listStatusIterator`, `listFiles`, `getFileStatus`, and `getFileLinkStatus`.
- Local copy APIs include `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, `moveToLocalFile`, `startLocalOutput`, and `completeLocalOutput`.
- Symlink APIs include `createSymlink`, `supportsSymlinks`, `getLinkTarget`, `resolveLink`, static `areSymlinksEnabled()`, and static `enableSymlinks()`.
- Checksum and verification APIs include `getFileChecksum(Path)`, `getFileChecksum(Path, long)`, `setVerifyChecksum(boolean)`, and `setWriteChecksum(boolean)`.
- Status/statistics APIs include `getStatus()`, `getStatus(Path)`, `getUsed()`, `getUsed(Path)`, block-size and replication defaults, static synchronized legacy statistics accessors, `clearStatistics()`, `printStatistics()`, per-instance `getStorageStatistics()`, and static `getGlobalStorageStatistics()`.
- Trash and capability APIs include `getTrashRoot(Path)`, `getTrashRoots(boolean)`, `hasPathCapability(Path, String)`, and static `getFileSystemClass(String, Configuration)`.
- Public fields include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and protected instance `statistics`.

### FileUtil Segment

- `stat2Paths(FileStatus[])` and `stat2Paths(FileStatus[], Path)` convert statuses to paths, with the second overload returning the supplied default path when stats are null.
- `fullyDeleteOnExit(File)` recursively registers local files for JVM-exit deletion.
- `fullyDelete(File)` and `fullyDelete(File, boolean)` delete local files/directories recursively. Their symlink behavior is explicitly documented: deleting a symlink does not delete the target, whether the target is a file or directory.
- `readLink(File)` returns a symlink target or empty string if not a symlink or inaccessible.
- `fullyDeleteContents(File)` and its permission-granting overload delete the contents of a directory without deleting the directory itself; if the argument is a symlink to a directory, contents of the target directory are deleted.
- Deprecated `fullyDelete(FileSystem, Path)` delegates recursive remote deletion use cases toward `FileSystem.delete(Path, boolean)`.
- `copy(...)` overloads move data between `FileSystem` instances, arrays of source paths, a `FileStatus` source, local `File`, and local destination `File`, with delete-source and overwrite options where available.
- `makeShellPath(...)` and `makeSecureShellPath(File)` convert local filenames to shell-compatible paths, with the secure variant intended to avoid script injection attacks.
- `getDU(File)` computes local disk usage with a basic implementation.
- `unZip(InputStream, File)` and `unZip(File, File)` extract ZIP data to a directory.
- `unTar(InputStream, File, boolean)` and `unTar(File, File)` extract `.tar`, `.tar.gz`, and `.tgz` archives; the stream overload can throw `IOException`, `InterruptedException`, and `ExecutionException`.
- `symLink(String, String)` creates a local symlink and returns zero on success; Windows security failures are documented to return code 2 with a warning.
- `chmod` overloads change file permissions with optional recursion.
- `setOwner(File, String, String)` changes local file owner/group and requires at least one of user or group to be non-null.
- `setReadable`, `setWritable`, `setExecutable`, `canRead`, `canWrite`, and `canExecute` provide platform-independent wrappers over Java `File` permission APIs, especially for Windows.
- `setPermission(File, FsPermission)` sets local permissions, using Java primitives instead of forking when group and other bits match.
- The chunk ends at the start of final static `createLocalTempFile(File basefile, String prefix, boolean isDeleteOnExit)`.

## Control Flow

The XML document has no executable control flow, but its API contracts imply several important operational paths.

`CreateFlag` validation is a gate before create/append calls mutate filesystem state. A caller chooses an `EnumSet`; validation checks illegal combinations, then path-existence-specific validation decides whether the operation creates, appends, overwrites, or fails with an exception.

`FileContext` factory methods establish default filesystem resolution and configuration first. Each path operation then qualifies or resolves the path, selects the owning `AbstractFileSystem`, applies user/umask defaults where relevant, and dispatches to the filesystem-specific implementation. The create builder path defers verification and filesystem mutation until `FSDataOutputStreamBuilder.build()` is invoked.

`FileContext` path resolution distinguishes fully qualified URIs, slash-relative paths resolved against the default filesystem, and working-directory-relative paths resolved by prefixing the FileContext working directory. The Javadocs explicitly reject relative paths with a scheme such as `scheme:foo/bar`.

`FileStatus` acts as a data transfer object. Filesystem implementations populate it, callers inspect flags and metadata, collection code compares it by path, and legacy serialization flows through protobuf-backed `readFields`/`write` while newer code should use `PBHelper` directly.

`FileSystem.get(URI, Configuration)` has explicit cache control flow: if `fs.$SCHEME.impl.disable.cache` is true, it creates and initializes a new instance without caching; otherwise it returns a matching cached instance or creates, initializes, caches, and returns a new one. `newInstance(...)` bypasses cache reuse and always returns a unique object.

`FileSystem.initialize(URI, Configuration)` is the required setup hook after construction. Subclasses overriding it must call the superclass implementation, while deciding whether to alter configuration before the call and whether to call before or after subclass setup.

`FileSystem` create/open/list/delete operations mix abstract hooks and default convenience wrappers. For example, convenience `open(Path)` routes to buffer-size overloads, `mkdirs(Path)` routes to `mkdirs(Path, FsPermission)`, and many local-copy methods route through `FileUtil.copy`-style behavior.

`FileSystem.rename(Path, Path, Rename...)` documents overwrite and type-compatibility rules separately from the abstract boolean `rename(Path, Path)`. The option-based implementation is explicitly non-atomic by default; atomicity is filesystem-specific.

Delete-on-exit flow registers paths on an instance, removes them with `cancelDeleteOnExit`, and recursively processes remaining paths when the `FileSystem` is closed or a cached filesystem is closed by the JVM shutdown hook.

Listing flow is split between eager arrays (`listStatus`), sorted globbing (`globStatus`), block-location-bearing iterators (`listLocatedStatus`, `listFiles`), and on-demand remote iteration (`listStatusIterator`). Implementations are encouraged to override iterator-based methods for efficiency.

`FileUtil` local delete flow treats symlinks differently depending on whether deleting the link itself or deleting contents through a link. Copy flow can optionally delete sources after successful transfer, so error ordering matters to avoid data loss. Archive extraction and permission APIs delegate to local filesystem and shell/platform mechanisms.

## State and Persistence Behavior

This JDiff file persists the 3.2.2 API shape for compatibility checks. It does not persist Hadoop runtime state.

`ContentSummary` instances represent filesystem-derived counts, quotas, and storage-type usage. The visible methods persist nothing themselves but define stable textual output that downstream tools and tests may parse.

`FileContext` carries process-local client state: default `AbstractFileSystem`, working directory, user identity, and umask. It also exposes statistics and delete-on-exit behavior. Filesystem operations invoked through it persist data or metadata in the target filesystem: file bytes, directories, permissions, ownership, timestamps, ACLs, xattrs, snapshots, quotas, storage policies, and symlinks.

`FileStatus` is both runtime metadata and a serialization boundary. It is Java-serializable and `Writable`, but its `Writable` methods are deprecated in favor of protobuf conversion. Its equality/hash state is path-only, while its payload contains much richer metadata. Attribute flags compact ACL, encryption, erasure coding, and snapshot capability state into a set.

`FileSystem` has both global and instance state. Global state includes cached filesystem instances keyed by URI/user/configuration behavior, global shutdown hooks, symlink enablement, service-loaded implementation classes, and global storage/statistics registries. Instance state includes configuration, URI identity, working directory in implementations, delete-on-exit path sets, per-instance storage statistics, protected legacy `statistics`, and any implementation-specific clients or connections.

`FileSystem.close()` is a state transition: after close, methods on the filesystem and streams created from it have undefined behavior. It also releases resources, processes delete-on-exit paths, and removes cached instances when applicable.

`FileUtil` primarily manipulates local filesystem state. Recursive deletion and archive extraction can partially mutate directories on failure. Permission helpers alter local file modes/ownership. `fullyDeleteOnExit` registers process-exit cleanup in JVM-local state rather than durable metadata.

## Dependencies and Integration Points

This chunk integrates with Java platform APIs such as `URI`, `File`, `IOException`, `FileNotFoundException`, `InvalidObjectException`, `DataInput`, `DataOutput`, `InputStream`, `Closeable`, `Serializable`, `ObjectInputValidation`, `EnumSet`, `Collection`, `List`, `Map`, `Set`, `ServiceLoader`, and `ExecutionException`.

Hadoop configuration and security integration points include `Configuration`, `Configured`, `UserGroupInformation`, `AccessControlException`, `DelegationTokenIssuer`, token service names, and `SecurityUtil`.

Hadoop filesystem integration points include `Path`, `PathFilter`, `PathCapabilities`, `PathHandle`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `AbstractFileSystem`, `LocalFileSystem`, `RawLocalFileSystem`, `FsStatus`, `FsServerDefaults`, `BlockLocation`, `BlockStoragePolicySpi`, `StorageType`, `StorageStatistics`, `GlobalStorageStatistics`, `RemoteIterator`, `ContentSummary`, `QuotaUsage`, `FileChecksum`, and the `Options` nested types for create options and rename options.

Permission and metadata integration points include `FsPermission`, ACL entry/status types under `org.apache.hadoop.fs.permission`, xattr namespace/flag handling, snapshot-capable filesystems, storage policy implementations, and protobuf helpers referenced as `PBHelper`.

`FileSystem` implementation discovery depends on configuration keys, service loading, scheme bindings, URI canonicalization, and filesystem-specific default ports. Its documented behavioral baseline is HDFS: the class Javadoc says that if HDFS differs from the written documentation or external filesystem spec, HDFS behavior is normative.

`FileUtil` bridges Hadoop `FileSystem` APIs with local `java.io.File`, shell path handling, archive formats, and OS-specific permission/symlink behavior.

## Risks and Edge Cases

- This chunk starts inside `ContentSummary`; the earlier fields, constructors, and accessors for the class are outside this range and must be merged from the previous chunk before producing a complete class report.
- This chunk ends inside `FileUtil.createLocalTempFile`; later parameters, full documentation, subsequent methods, fields, and class closing metadata are outside this range.
- JDiff gives signatures and Javadocs, not implementation. Exact cache keys, synchronization, exception text, retry behavior, stream handling, ACL/xattr validation, and object-store-specific semantics require implementation-source verification.
- `ContentSummary.toString` output is a compatibility surface. Changing spacing, headers, or inclusion/exclusion of snapshot and storage-type fields can break shell tooling and golden-output tests.
- `CreateFlag` combinations are easy to misuse. `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE` are invalid, while `CREATE|APPEND` and `CREATE|OVERWRITE` intentionally mean different things when the path exists.
- `FileContext.setWorkingDirectory` is prefix-based and does not follow symlinks. Code expecting Unix current-directory inode semantics can resolve paths differently after symlink changes.
- `FileContext.create(Path)` builder does not mutate filesystem state until `build()`; code that assumes validation at builder construction can miss delayed failures.
- Many `FileContext` methods list RPC client/server and unexpected-server exception cases in the Javadocs. Remote filesystems can fail with transport or server-side failures beyond local `IOException` subclasses.
- `FileStatus.equals` and `hashCode` use only path names. Two statuses for the same path but different timestamps, permissions, encryption flags, or lengths compare equal, which can surprise set/map users.
- `FileStatus.readFields` and `write` remain for binary/API compatibility but are deprecated. New code should avoid depending on their serialized wire format unless compatibility requires it.
- `FileSystem.get` returns cached instances unless caching is disabled. Shared cached instances can leak mutable state such as working directory, statistics, or delete-on-exit registrations across callers.
- `FileSystem.newInstance` avoids cache sharing but requires explicit close discipline to avoid resource leaks.
- Subclasses overriding `initialize` must call superclass initialization. Failure can break statistics, configuration, URI setup, or cache/service-name behavior.
- `FileSystem.getScheme()` default throws `UnsupportedOperationException`; implementations that do not override it may fail capability or builder code expecting a scheme.
- `FileSystem.rename(Path, Path)` atomicity is implementation-specific, and the option-based default implementation is documented as non-atomic. Applications needing atomic commit must validate the target filesystem.
- `FileSystem.setReplication` defaults to returning true for filesystems without replication support, possibly bypassing existence checks. Callers cannot interpret true as proof that replication changed.
- Deprecated `exists`, `isFile`, `isDirectory`, and `getLength` convenience checks can cause redundant RPCs and time-of-check/time-of-use races if used before a later operation.
- Delete-on-exit can significantly extend JVM shutdown, especially on remote filesystems or object stores, and clean shutdown is not guaranteed.
- `globStatus` has distinct null-vs-empty behavior depending on whether the pattern contains a glob and whether a non-glob path exists.
- ACL, xattr, snapshot, storage-policy, append, truncate, concat, checksum, and symlink APIs are optional or filesystem-specific. Default implementations may throw `UnsupportedOperationException`.
- Static symlink enablement in `FileSystem` is global process state. Tests or applications that toggle it can affect unrelated code.
- `FileUtil.fullyDeleteContents` follows symlink-to-directory targets when deleting contents, unlike `fullyDelete` which deletes the symlink itself. This difference is security-sensitive.
- `FileUtil.copy` with `deleteSource=true` must only remove the source after successful copy; partial failures can otherwise lose data or leave duplicate data.
- `FileUtil.makeShellPath` and `makeSecureShellPath` are sensitive to platform quoting and script injection risks. Callers should prefer the secure variant for untrusted paths.
- Archive extraction methods must guard against path traversal, overwrites, partial extraction, and interrupted external tar execution. The Javadocs identify command interruption and task submission failures for tar streams.
- Windows permission APIs differ from Unix. `setExecutable(false)` on a directory does not prevent file create/delete/rename within that directory on Windows.

## Test Signals

Useful tests for this API surface should include:

- JDiff/API compatibility checks ensuring all public/protected methods, fields, deprecations, visibility, final/static markers, exceptions, and implemented interfaces in this chunk remain stable.
- `ContentSummary` golden-output tests for every visible `toString` overload, human-readable formatting, quota and non-quota headers, storage-type lists, and snapshot-exclusion flag behavior.
- `CreateFlag` validation tests for every documented valid and invalid combination, append-specific validation, path-exists and path-missing branches, and exception types.
- `FileChecksum` tests for equality/hashCode by algorithm and bytes, checksum option propagation, `Writable` round trips in concrete implementations, and mismatched algorithm/value cases.
- `FileContext` factory tests for default config, explicit URI/config, local filesystem, and direct `AbstractFileSystem` construction, including unsupported scheme failures.
- `FileContext` path resolution tests for fully qualified URIs, slash-relative paths, working-directory-relative paths, illegal relative-with-scheme paths, symlink and mount-point resolution, and default FS selection.
- `FileContext` mutation tests for create options, delayed builder validation, mkdir parent creation, delete recursive behavior, truncate true/false completion behavior, rename overwrite semantics, permissions with umask, ownership, timestamps, checksums, and setVerifyChecksum behavior.
- `FileContext` metadata tests for ACL replacement/removal, xattr namespace and flag handling, snapshot create/rename/delete, storage policy set/unset/query, corrupt-block listing, located status listing, and path capability delegation.
- `FileStatus` tests for every constructor family, default permission/owner/group substitution on nulls, attribute flag conversion, file/directory/symlink classification, symlink target behavior, path-only equality/hashCode, compareTo object compatibility, `toString`, copy constructor, Java deserialization validation, and deprecated protobuf-backed `Writable` serialization.
- `FileSystem` cache tests for `get` vs `newInstance`, cache disabling through `fs.$SCHEME.impl.disable.cache`, close removal from cache, closeAll, closeAllForUGI, UGI-specific lookup, and resource cleanup.
- `FileSystem` subclass contract tests ensuring `initialize` calls superclass, URI canonicalization fills default ports, `checkPath` rejects foreign schemes/authorities, canonical service names work with tokens, and `getFileSystemClass` discovers service-loaded implementations.
- `FileSystem` operation tests for create overloads, primitive create/mkdir, non-recursive create, open overloads, append optional support, concat optional support, setReplication default semantics, rename type/overwrite cases, truncate unsupported and async-completion cases, recursive delete, and delete-on-exit processing.
- Listing tests for `listStatus` ordering assumptions, filter behavior, multi-path behavior, corrupt-block iterator, glob syntax and null/empty return behavior, located status block locations, lazy `listStatusIterator`, and recursive `listFiles`.
- Local copy tests for copy/move from local, copy/move to local, raw local filesystem option avoiding CRC files, local temp output workflow, delete-source ordering, overwrite behavior, and failure cleanup.
- Metadata tests for content summary, quota usage and quota setters, block-size/default-replication defaults, file status vs link status, link target resolution, checksum-by-length behavior, verify/write checksum toggles, fs status, used space, and `msync`.
- Statistics tests for legacy synchronized statistics methods, `clearStatistics`, `printStatistics`, per-instance `getStorageStatistics`, and global storage statistics registration.
- Trash/capability tests for per-path trash root, all-users trash roots, default capability false behavior, and filesystem-specific capability overrides.
- `FileUtil` tests for `stat2Paths` null/default handling, recursive delete symlink semantics, partial-delete false returns, permission-granting delete path, `readLink` empty-string behavior, local and cross-filesystem copy variants, shell path escaping, disk-usage calculation, ZIP/TAR extraction including interrupted tar, local symlink return codes, chmod/setOwner wrappers, Windows permission differences, and `setPermission` no-fork optimization.

## Cross-Chunk Notes

The previous chunk is required to complete `ContentSummary`. The next chunk is required to complete `FileUtil`, starting from the rest of `createLocalTempFile(File, String, boolean)` and continuing through any later utility methods and package metadata. The final reconciled file-level report should avoid treating this chunk's `FileUtil` coverage as complete.
