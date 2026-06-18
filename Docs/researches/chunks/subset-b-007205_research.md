# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml lines 6067-12059

## Scope And Purpose

This chunk is part of Hadoop Common's generated JDiff API description for Apache Hadoop Common 3.3.3. It is not executable source; it records public/protected API signatures, inheritance, visibility, deprecation text, checked exceptions, parameters, and Javadoc for API compatibility review. The chunk starts in the final fields of `org.apache.hadoop.fs.CommonConfigurationKeysPublic`, covers several core `org.apache.hadoop.fs` public types completely, and ends inside the public fields of `org.apache.hadoop.fs.FileSystem`.

The dominant purpose of this slice is to describe the stable filesystem API surface exposed by Hadoop Common:

- Common security/KMS/credential/HTTP/service configuration key constants.
- Filesystem metadata containers: `ContentSummary`, `FileStatus`, and `FileChecksum`.
- Creation semantics via `CreateFlag`.
- User-facing filesystem APIs: `FileContext` and `FileSystem`, including path resolution, creation, open/read, metadata, listing, symlink, ACL, xattr, snapshot, storage-policy, statistics, builder, and multipart-upload contracts.

Because this is JDiff XML, control-flow and persistence details are inferred from documented semantics, inheritance, method abstractness, default behavior descriptions, and exceptions. The implementation bodies live in the corresponding Java sources; this file is the compatibility contract consumed by API-diff tooling.

## Important APIs, Types, And Contracts

### `CommonConfigurationKeysPublic` Tail

Lines 6067-6435 complete `org.apache.hadoop.fs.CommonConfigurationKeysPublic`. The chunk lists public static final constants for:

- KMS encrypted key cache settings: `KMS_CLIENT_ENC_KEY_CACHE_SIZE`, low-watermark, refill thread count, expiry, and defaults.
- KMS client timeout/failover knobs: timeout seconds, max retries, base/max failover sleep in milliseconds.
- Secure random and crypto-related keys: Java secure random algorithm, secure random implementation, secure random device file path and default.
- Shell and deletion safety settings: missing default FS warning and safe delete file-count limit.
- HTTP observability and timeout settings: HTTP logs enabled, Prometheus enabled, HTTP idle timeout.
- Credential provider settings: credential provider path, clear-text fallback and default, credential password file, sensitive config key regex/default.
- Hadoop tagging settings: system tags, custom tags, and deprecated/replacement-looking `HADOOP_TAGS_SYSTEM` / `HADOOP_TAGS_CUSTOM`.
- Service shutdown timeout and default.

The class-level doc says this class contains publicly documented common configuration keys and should generally not be used directly, preferring `CommonConfigurationKeys`. Many constants point consumers to `core-default.xml`, making this API an integration bridge between code constants and configuration documentation.

### `ContentSummary`

`ContentSummary` extends `QuotaUsage` and implements `Writable`. It models aggregate content metrics for a file or directory.

Important API points:

- Deprecated constructors exist for binary/source compatibility; docs direct new use to `ContentSummary.Builder`.
- Count accessors include length, directory count, file count, snapshot length/counts, snapshot space consumed, and erasure coding policy.
- Static header helpers expose CLI/report formatting contracts: `getHeader(boolean)`, `getSnapshotHeader()`, `getHeaderFields()`, and `getQuotaHeaderFields()`.
- Multiple `toString` overloads drive report output: quota display, human-readable units, storage-type quota display, snapshot inclusion/exclusion, and selected storage types.
- `toSnapshot(boolean)` formats snapshot counts separately.
- `equals` and `hashCode` are part of the public contract, so changes to represented fields affect compatibility and test expectations.

The key integration point is filesystem reporting: `FileSystem.getContentSummary(Path)` returns this type, and shell/UI consumers rely on its header and string layout.

### `CreateFlag`

`CreateFlag` is a public enum whose JDiff slice exposes enum utility methods and validation helpers:

- `values()` and `valueOf(String)`.
- `validate(EnumSet<CreateFlag>)`.
- `validate(Object path, boolean pathExists, EnumSet<CreateFlag>)`.
- `validateForAppend(EnumSet<CreateFlag>)`.

Documented create semantics include `CREATE`, `APPEND`, `OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`. Invalid combinations include `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`. The append validation contract requires `APPEND` and rejects `OVERWRITE`.

This enum is a critical control surface for `FileSystem.create(...)`, `FileContext.create(...)`, builder APIs, and implementations that must enforce compatible behavior across local filesystems, HDFS, and object-store adapters.

### `FileAlreadyExistsException`

This public `IOException` subtype has default and message constructors. It is thrown when a target already exists and the operation is not configured to overwrite. The API is small but important because it distinguishes existence conflicts from generic I/O failure in create/rename code paths.

### `FileChecksum`

`FileChecksum` is an abstract `Writable` for file checksum metadata. Abstract methods define the required checksum payload:

- `getAlgorithmName()`.
- `getLength()`.
- `getBytes()`.

It also exposes `getChecksumOpt()`, `equals(Object)`, and `hashCode()`. Equality is documented as algorithm plus value equality. `FileSystem.getFileChecksum(Path)` and `getFileChecksum(Path, long)` return this type or `null` if checksums are unsupported.

### `FileContext`

`FileContext` is a public user-facing filesystem facade implementing `PathCapabilities`. Its class documentation positions it as the analogue of per-process Unix file state, with a default filesystem and umask, while server-side defaults cover home directory, replication, block size, buffer size, encryption transfer, and checksum options.

Factory and state APIs:

- `getFileContext(...)` overloads create contexts from default configuration, `URI`, `Configuration`, both URI/configuration, `AbstractFileSystem`, or user identity.
- `getLocalFSFileContext(...)` overloads create local contexts.
- `setWorkingDirectory(Path)` and `getWorkingDirectory()` maintain context-level path resolution state.
- `getUgi()`, `getHomeDirectory()`, `getUMask()`, and `setUMask(FsPermission)` expose per-context identity and permission defaults.
- Protected `getFSofPath(Path)` selects the bound `AbstractFileSystem` for absolute or qualified paths.

Core operations:

- Path normalization and resolution: `resolvePath`, `makeQualified`, `resolve`, and `resolveIntermediate`.
- Creation: stream-returning `create(Path, EnumSet<CreateFlag>, Options.CreateOpts...)` and builder-returning `create(Path)` / `createFile`-style API via `FSDataOutputStreamBuilder`.
- Directory and deletion: `mkdir`, `delete`, and `deleteOnExit`.
- Read/open: `open(Path)` and `open(Path, int)`, plus builder `openFile(Path)`.
- Mutation: `truncate`, `setReplication`, `rename`, `setPermission`, `setOwner`, `setTimes`.
- Metadata and location: `getFileStatus`, `getFileLinkStatus`, `getLinkTarget`, `getFsStatus`, `getFileChecksum`, `getServerDefaults`.
- Listing: `listStatus`, `listLocatedStatus`, `listCorruptFileBlocks`.
- Symlink creation and resolution.
- ACL and xattr methods: modify/remove/default/remove-all/set ACLs, get ACL status, set/get/list/remove xattrs.
- Snapshots: create, rename, delete.
- Storage policy: satisfy, set, unset, get, list all policies.
- Capabilities and multipart upload: `hasPathCapability(Path, String)` and `createMultipartUploader(Path)`.

Public fields include `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`. `DEFAULT_PERM` is retained for compatibility after HADOOP-9155 separated directory and file defaults.

The API is structured as a higher-level facade over `AbstractFileSystem`. Many operations mention exceptions applicable to RPC-backed filesystems, which indicates integration with HDFS and remote service implementations. Permission behavior is also significant: `FileContext` applies umask before calling lower-level primitive methods in `FileSystem` during the migration path.

### `FileStatus`

`FileStatus` is a serializable, writable, comparable metadata record for a file, directory, or symlink. It implements `Writable`, `Comparable`, `Serializable`, and `ObjectInputValidation`.

Important state exposed by constructors and accessors:

- Length, directory/file/symlink kind, block size, replication, modification time, access time.
- `FsPermission`, owner, group, path, and symlink target.
- Attribute flags for ACL, encryption, erasure coding, and snapshot-enabled state.
- Static `attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts booleans into the attribute flag set.
- Shared empty `NONE` attribute set.

Behavioral contracts:

- `isDir()` is deprecated in favor of explicit `isFile()`, `isDirectory()`, and `isSymlink()`.
- `compareTo(FileStatus)` orders by file status path; `compareTo(Object)` was restored for HADOOP-14683 binary compatibility.
- `equals(Object)` and `hashCode()` are path-based, not deep metadata equality.
- `readFields(DataInput)` and `write(DataOutput)` are deprecated in favor of PBHelper/protobuf serialization, but remain public compatibility points.
- `validateObject()` participates in Java object deserialization validation.

This type is central to almost every listing and metadata API in `FileSystem` and `FileContext`.

### `FileSystem`

`FileSystem` is an abstract public class extending `Configured` and implementing `Closeable`, `DelegationTokenIssuer`, and `PathCapabilities`. This chunk covers the constructor and a large public/protected API subset through early fields.

Instantiation, caching, and identity:

- Static `get(...)` overloads resolve a filesystem from `Configuration`, `URI`, and optionally user name.
- `newInstance(...)` overloads always return a new object, unlike cache-aware `get(...)`.
- `getLocal(Configuration)` and `newInstanceLocal(Configuration)` create local filesystem instances.
- `getDefaultUri(Configuration)` / `setDefaultUri(...)` read and mutate the configured default filesystem.
- `initialize(URI, Configuration)` is called after construction and before use; overriding implementations must call super.
- `getUri()` is abstract; `getScheme()`, `getCanonicalUri()`, `canonicalizeUri(URI)`, and `getDefaultPort()` define URI identity and default-port normalization.
- `getCanonicalServiceName()` integrates with token caches and delegation token lookup.
- `getFileSystemClass(String, Configuration)` discovers implementations through configuration and `ServiceLoader`.
- `closeAll()` and `closeAllForUGI(UserGroupInformation)` close cached instances.

Path and namespace operations:

- `makeQualified(Path)` and `checkPath(Path)` enforce that paths belong to the filesystem.
- `resolvePath(Path)` resolves symlinks or mount points.
- `fixRelativePart(Path)` aligns with `FileContext` relative path handling.
- `getFSofPath(Path, Configuration)` is a protected static helper for dispatching by path.

Read and path-handle APIs:

- Abstract `open(Path, int)` plus convenience `open(Path)`.
- `open(PathHandle)` and `open(PathHandle, int)` support durable handles with constraints.
- Final `getPathHandle(FileStatus, HandleOpt...)` validates ownership and delegates to protected `createPathHandle(...)`.
- Builder APIs: `openFile(Path)`, `openFile(PathHandle)`, and protected `openFileWithOptions(...)` methods returning `CompletableFuture<FSDataInputStream>`.

Create, append, and output APIs:

- Many convenience `create(...)` overloads supply overwrite, buffer size, replication, block size, progress, permissions, `CreateFlag` sets, and checksum options.
- The abstract create primitive is `create(Path, FsPermission, boolean, int, short, long, Progressable)`.
- Extended create with `EnumSet<CreateFlag>` and `Options.ChecksumOpt` links directly to `CreateFlag` validation and checksum configuration.
- `primitiveCreate(...)`, `primitiveMkdir(...)`, and protected rename-with-options are migration hooks for `FileContext`; docs describe them as temporary transition support.
- `createNonRecursive(...)` variants fail if the parent directory does not exist.
- `createNewFile(Path)` creates zero-length files but explicitly documents that the default implementation is not atomic.
- `append(...)` has convenience overloads plus abstract `append(Path, int, Progressable)`.
- `concat(Path, Path[])` is optional by default.
- `createFile(Path)` and `appendFile(Path)` expose `FSDataOutputStreamBuilder` builders; the create builder notes HADOOP-14384 stability/visibility caution.

Mutation and metadata:

- Abstract `rename(Path, Path)` and `delete(Path, boolean)`.
- `truncate(Path, long)` returns `true` for immediate availability or `false` when background block adjustment is needed.
- `setReplication(Path, short)` has default behavior that may return true even if replication is unsupported.
- Quota APIs: `getContentSummary(Path)`, `getQuotaUsage(Path)`, `setQuota(Path, long, long)`, and `setQuotaByStorageType(Path, StorageType, long)`.
- `getFileStatus(Path)` is abstract and is the preferred replacement for deprecated `isDirectory`, `isFile`, `getLength`, `getBlockSize`, and `getReplication`.
- `getServerDefaults()` is deprecated in favor of path-aware `getServerDefaults(Path)`.
- `getDefaultBlockSize(Path)` and `getDefaultReplication(Path)` are path-aware defaults.
- `getStatus()` / `getStatus(Path)` report capacity and usage.
- `setPermission`, `setOwner`, and `setTimes` mutate metadata.

Listing and globbing:

- Abstract `listStatus(Path)` returns non-null arrays and does not guarantee sorted order.
- Filtered and multi-path `listStatus(...)` overloads apply `PathFilter`.
- `globStatus(Path)` and `globStatus(Path, PathFilter)` define shell-style glob syntax and sorted result behavior; no-match behavior differs for glob vs non-glob patterns.
- `listLocatedStatus(Path)` and protected filtered variant return `RemoteIterator<LocatedFileStatus>`-style results with block locations.
- `listStatusIterator(Path)` supports lazy/on-demand listing and should be overridden for efficiency.
- `listFiles(Path, boolean)` recursively or non-recursively lists files with block locations.
- `listCorruptFileBlocks(Path)` is optional and may return duplicates for multi-block corruption.

Local copy/output helpers:

- `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, and `moveToLocalFile` cover local-to-filesystem and filesystem-to-local transfers, with delete-source and overwrite options.
- `copyToLocalFile(..., useRawLocalFileSystem)` can bypass local checksum side files by using `RawLocalFileSystem`.
- `startLocalOutput` and `completeLocalOutput` support writing through local temporary files for remote filesystems.

Lifecycle and persistent side effects:

- `close()` releases locks, deletes paths queued through `deleteOnExit`, removes cached instances, and leaves subsequent use undefined.
- `deleteOnExit(Path)`, `cancelDeleteOnExit(Path)`, and protected `processDeleteOnExit()` maintain a per-filesystem deferred-delete list. The docs call out shutdown uncertainty and high cost on object stores or remote filesystems.
- `getUsed()` and `getUsed(Path)` summarize consumed bytes.
- `msync()` synchronizes client metadata state for consistency-sensitive implementations such as HDFS HA.

Optional feature surfaces:

- Symlinks: `createSymlink`, `getFileLinkStatus`, `supportsSymlinks`, `getLinkTarget`, `resolveLink`, global `areSymlinksEnabled()`, and `enableSymlinks()`.
- Checksums: `getFileChecksum(Path)`, range checksum, `setVerifyChecksum`, and `setWriteChecksum`.
- Snapshots: `createSnapshot`, `renameSnapshot`, and `deleteSnapshot`.
- ACLs: `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, and `getAclStatus`.
- XAttrs: `setXAttr`, `getXAttr`, `getXAttrs`, `listXAttrs`, and `removeXAttr`.
- Storage policies: `satisfyStoragePolicy`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, and `getAllStoragePolicies`.
- Trash: `getTrashRoot(Path)` and `getTrashRoots(boolean)`.
- Capabilities: `hasPathCapability(Path, String)` defaults false unless an implementation can determine support.
- Statistics: deprecated static `getStatistics`, `getAllStatistics`, and `getStatistics(String, Class)` are synchronized and replaced by `getGlobalStorageStatistics()`. `clearStatistics()` and `printStatistics()` remain public, and `getStorageStatistics()` is per-instance.
- Multipart upload: `createMultipartUploader(Path)` returns a builder and may fail early with `IOException` or `UnsupportedOperationException`.

Fields at the end of the chunk include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, and `LOG`. The `LOG` doc warns it is widely used in `org.apache.hadoop.fs` code and tests, so changing it has broad compatibility impact.

## Control Flow And Behavioral Signals

The XML does not contain executable control flow, but the documented API flow is clear:

- Filesystem lookup flows from configuration and URI to implementation discovery, instance creation/initialization, optional cache lookup, and user-context execution through UGI-aware overloads.
- Relative paths are resolved through working directory/default filesystem state in `FileContext` or `FileSystem` before dispatching to concrete filesystem implementations.
- Convenience methods generally funnel to abstract core operations: `open(Path)` to `open(Path, int)`, many `create(...)` overloads to permission/overwrite/buffer/replication/block-size create primitives, `mkdirs(Path)` to `mkdirs(Path, FsPermission)`, and listing helpers to `listStatus` or iterator equivalents.
- Builder APIs defer operation execution until `build()`; `openFileWithOptions(...)` explicitly returns a `CompletableFuture` whose evaluation may surface unsupported path-handle behavior.
- Optional operations default to unsupported, no-op, null, false, or conservative behavior unless subclasses override them. This pattern applies to append support, concat, checksums, symlinks, snapshots, ACLs, xattrs, storage policies, multipart upload, and path capabilities.
- `FileStatus` equality/order flows through path comparison rather than all metadata fields, which affects sets, maps, sorting, and deduplication.

## State And Persistence Behavior

Stateful surfaces visible in this chunk include:

- `FileContext` stores default filesystem, umask, working directory, and UGI identity. These affect every path and permission operation made through the context.
- `FileSystem` stores configuration through `Configured`, URI identity, cached instance membership, working directory in subclasses, delete-on-exit registrations, stream handles, and per-instance storage statistics.
- Static/global `FileSystem` state includes the filesystem cache, global storage statistics, legacy statistics maps, global symlink enablement, implementation-class discovery, and shutdown-hook behavior.
- Persistent filesystem side effects include file creation/overwrite/append/truncate/delete/rename, directory creation, local copy/move, metadata changes, quota changes, ACL/xattr mutation, snapshot operations, storage policy changes, checksum verification/write settings when supported, and trash-root behavior.
- Serialization/persistence contracts are exposed by `Writable` implementations (`ContentSummary`, `FileChecksum`, `FileStatus`) and Java serialization validation in `FileStatus`. Deprecated `FileStatus` Writable methods now point to protobuf conversion but remain part of compatibility.

## Dependencies And Integration Points

This API slice integrates with:

- Hadoop configuration: `Configuration`, `CommonConfigurationKeys`, `core-default.xml`, KMS keys, credential providers, security tags, HTTP/Prometheus settings, and service shutdown settings.
- Hadoop filesystem primitives: `Path`, `AbstractFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `FutureDataInputStreamBuilder`, `MultipartUploaderBuilder`, `FsStatus`, `FsServerDefaults`, `BlockLocation`, `LocatedFileStatus`, `RemoteIterator`, `PathFilter`, `PathHandle`, and `Options`.
- Hadoop security: `UserGroupInformation`, `DelegationTokenIssuer`, delegation-token service naming, `AccessControlException`, credential-provider configuration, Kerberos/token-related constants from the immediately preceding class context.
- Hadoop permission and metadata models: `FsPermission`, `AclStatus`, `AclEntry`, `StorageType`, `BlockStoragePolicySpi`, xattr flag enums, and quota usage.
- Java platform APIs: `URI`, `IOException` and subtypes, `Serializable`, `ObjectInputValidation`, `CompletableFuture`, `ServiceLoader`, `EnumSet`, collections, and logging.
- HDFS/RPC implementations: method docs mention RPC client/server/unexpected-server exceptions for snapshots and distributed block-location behavior.
- Command-line and test consumers: `ContentSummary` formatting helpers and `FileSystem.LOG` are explicitly stable surfaces used outside implementation internals.

## Risks And Compatibility Concerns

- This XML is a compatibility artifact. Any changed signature, visibility, exception, deprecation string, or documented behavior may affect JDiff/API compatibility gates even if implementation tests pass.
- The chunk begins and ends inside classes. Merge logic must combine it with adjacent chunks to avoid losing the earlier `CommonConfigurationKeysPublic` fields and later `FileSystem` fields/nested classes.
- Many `FileSystem` methods are convenience wrappers around abstract methods. Subclass implementers depend on those delegation contracts; changing defaults can alter behavior across HDFS, local filesystems, and object stores.
- `FileSystem.get(...)` cache behavior is explicitly configurable through `fs.$SCHEME.impl.disable.cache`; cache-key changes can cause resource leaks, stale clients, or unexpected sharing across users.
- Delete-on-exit is operationally risky for remote/object stores because shutdown is not guaranteed and deletion may be slow or fail under connectivity issues.
- `createNewFile(Path)` default non-atomicity is a concurrency risk; callers needing atomic create must use stronger filesystem-specific primitives.
- Deprecated APIs are still compatibility-sensitive, especially `FileStatus.compareTo(Object)`, `FileStatus` Writable serialization, legacy `FileSystem` statistics methods, and path-unaware server/default replication/block-size methods.
- `FileStatus.equals` being path-only can surprise callers expecting metadata equality.
- Optional-operation defaults vary between unsupported exceptions, `null`, `false`, no-op, or `true` for unsupported replication. Tests must assert the documented fallback for each operation.
- ACL and xattr methods expose permission-filtered reads; implementations must avoid leaking unauthorized metadata.
- Builder APIs defer validation to `build()` or future evaluation; tests must cover both early and deferred failure modes.
- Configuration key constants are used by external deployments. Renaming or changing defaults for KMS, credential, HTTP, shutdown, and random-source settings can break cluster security or operational behavior.

## Test Signals

Useful validation signals for this API chunk include:

- JDiff or equivalent API-compatibility checks comparing Hadoop Common 3.3.3 public signatures and deprecation text.
- Unit tests for `CreateFlag.validate(...)` covering valid create/append/overwrite combinations and invalid append-overwrite combinations.
- Contract tests for `FileSystem` implementations verifying create/open/append/delete/rename/list/status behavior through both direct APIs and builder APIs.
- Cache tests for `FileSystem.get(...)`, `newInstance(...)`, `closeAll()`, `closeAllForUGI(...)`, and `fs.$SCHEME.impl.disable.cache`.
- Serialization compatibility tests for `FileStatus`, including protobuf replacement paths and legacy Writable methods while they remain public.
- Metadata tests for `FileStatus` equality, comparison, symlink flags, ACL/encryption/EC/snapshot attributes, and `ObjectInputValidation`.
- `ContentSummary` formatting tests for header fields, quota display, human-readable display, storage-type quota display, snapshot inclusion/exclusion, and erasure coding policy reporting.
- Optional-feature contract tests ensuring unsupported checksums, ACLs, xattrs, snapshots, storage policies, symlinks, multipart upload, and path capabilities fail or return defaults as documented.
- Security tests around UGI-specific filesystem acquisition, token service names, credential provider fallback keys, xattr visibility filtering, and ACL mutation.
- Integration tests for HDFS HA `msync()`, block locations, corrupt-block iteration, snapshots, quotas, and storage policies.
- Object-store/local-filesystem tests around non-atomic `createNewFile`, expensive delete-on-exit behavior, local copy checksum side files, and raw local copy mode.
