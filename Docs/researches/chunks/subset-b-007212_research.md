# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 6067-12059

## Scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.3.4. It starts in the tail of `org.apache.hadoop.fs.CommonConfigurationKeysPublic`, then covers complete public API entries for `ContentSummary`, `CreateFlag`, `FileAlreadyExistsException`, `FileChecksum`, `FileContext`, and `FileStatus`, and continues through the first large portion of `FileSystem`.

The source is API metadata, not Java method bodies. Control flow and persistence notes below are therefore derived from documented contracts, abstract/default method markers, overload relationships, builder hooks, and class/interface relationships visible in the JDiff file.

## Purpose

The covered API surface defines the core Hadoop filesystem client contract. It exposes:

- public configuration keys for KMS client caches, secure random generation, shell behavior, credential providers, sensitive config redaction, HTTP logs, tags, shutdown hook timeout, Prometheus, and HTTP idle timeout;
- content and quota reporting through `ContentSummary`;
- file creation semantics through `CreateFlag`;
- canonical filesystem metadata objects through `FileStatus` and `FileChecksum`;
- the newer `FileContext` API over `AbstractFileSystem`, with URI-aware path resolution and per-context defaults;
- the legacy and still central `FileSystem` abstract base class, including filesystem discovery, caching, path qualification, read/write/list/delete primitives, optional advanced features, statistics, builders, and service-token integration.

The JDiff file itself exists under `dev-support/jdiff`, so its immediate role is release/API compatibility documentation. The APIs it describes are production contracts used by Hadoop clients, HDFS, local filesystems, object-store connectors, and compatibility tools.

## Important APIs, Types, and Functions

### `CommonConfigurationKeysPublic` tail

The chunk begins inside `CommonConfigurationKeysPublic` and lists public constants for:

- KMS encrypted key cache size, low watermark, refill thread count, expiry, timeout, and failover retry/backoff settings;
- secure random algorithm, implementation, and device file path settings;
- shell warnings and safe-delete limits;
- HTTP log and idle-timeout settings;
- credential provider path, clear-text fallback, password-file key, and sensitive-key redaction settings;
- deprecated `HADOOP_SYSTEM_TAGS` and `HADOOP_CUSTOM_TAGS`, replaced by `HADOOP_TAGS_SYSTEM` and `HADOOP_TAGS_CUSTOM`;
- service shutdown hook timeout;
- Prometheus enablement.

These are all static public constants, mostly documented as matching `core-default.xml` entries. Their risk is compatibility: downstream code and configuration files may refer to the exact constant names and property keys.

### `ContentSummary`

`ContentSummary` extends `QuotaUsage` and implements `Writable`. It stores summarized counts and sizes for a directory or file, including length, directory count, file count, snapshot length/count/space, erasure-coding policy, quota display fields, and storage-type quota display.

Constructors are documented as deprecated in favor of `ContentSummary.Builder`; the three-argument constructor historically set `spaceConsumed` equal to `length`, while builder use makes both explicit. Public formatting methods include `getHeader()`, `getSnapshotHeader()`, `getHeaderFields()`, `getQuotaHeaderFields()`, multiple `toString(...)` overloads for quota, human-readable, storage-type, and snapshot-exclusion options, plus `toSnapshot(boolean)`.

### `CreateFlag`

`CreateFlag` is an enum describing create/open-write behavior. Documented combinations include `CREATE`, `APPEND`, `OVERWRITE`, `CREATE|APPEND`, `CREATE|OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`. Invalid combinations include `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`.

Validation APIs are static: `validate(EnumSet)`, `validate(path, pathExists, EnumSet)`, and `validateForAppend(EnumSet)`. They enforce whether a path may be created, appended to, or overwritten, and throw `HadoopIllegalArgumentException` or `IOException` on invalid states.

### `FileAlreadyExistsException` and `FileChecksum`

`FileAlreadyExistsException` is an `IOException` used when a target already exists and the operation is not configured to overwrite it.

`FileChecksum` is an abstract `Writable` for file checksums. Subclasses must provide `getAlgorithmName()`, `getLength()`, and `getBytes()`. The base API also exposes `getChecksumOpt()`, `equals()`, and `hashCode()`, with equality defined by algorithm and byte value.

### `FileContext`

`FileContext` implements `PathCapabilities` and provides the newer filesystem API over `AbstractFileSystem`. It is URI namespace aware and maintains per-context state: default filesystem, working directory, umask, and user identity (`UserGroupInformation`).

Factory methods build contexts from an `AbstractFileSystem`, default configuration, local filesystem URI, explicit URI, or supplied `Configuration`. Core methods include:

- path and context state: `getFSofPath()`, `setWorkingDirectory()`, `getWorkingDirectory()`, `getUgi()`, `getHomeDirectory()`, `getUMask()`, `setUMask()`, `resolvePath()`, `makeQualified()`;
- file and directory operations: `create(...)`, `create(Path)` builder, `mkdir()`, `delete()`, `open()`, `truncate()`, `setReplication()`, `rename()`;
- metadata operations: `setPermission()`, `setOwner()`, `setTimes()`, `getFileChecksum()`, `setVerifyChecksum()`, `getFileStatus()`, `msync()`, `getFileLinkStatus()`, `getLinkTarget()`, `getFsStatus()`;
- symlinks: `createSymlink()`, `resolve()`, `resolveIntermediate()`, with detailed final-component behavior and target-resolution rules for fully qualified, partially qualified, relative, and absolute targets;
- listing and lifecycle: `listStatus()`, `listLocatedStatus()`, `listCorruptFileBlocks()`, `deleteOnExit()`, `util()`;
- global `AbstractFileSystem` statistics helpers;
- ACL and xattr operations;
- snapshot operations;
- storage policy operations;
- `openFile(Path)` builder, path capability checks, server defaults, and multipart uploader builder.

`FileContext` defines `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`. The Javadocs explicitly note that `DEFAULT_PERM` is retained for compatibility after HADOOP-9155 because older versions used directory-style executable defaults for files.

### `FileStatus`

`FileStatus` is the serializable client-side metadata record for a filesystem entry. It implements `Writable`, `Comparable`, `Serializable`, and `ObjectInputValidation`. Constructors cover minimal metadata, no-symlink filesystems, symlink targets, boolean attribute triples, explicit attribute sets, and copy construction.

State exposed by getters includes length, file/directory/symlink kind, block size, replication, modification/access times, permission, ACL/encryption/erasure-coding/snapshot flags, owner, group, path, and symlink target. `attributes(acl, crypt, ec, sn)` converts booleans to an attribute flag set; `NONE` is the shared empty attribute set.

Ordering, equality, and hash code are path-based. A raw-object `compareTo(Object)` exists specifically for binary compatibility per HADOOP-14683. `readFields()` and `write()` are deprecated in favor of direct protobuf conversion through `PBHelper`, but remain public for compatibility.

### `FileSystem`

`FileSystem` is an abstract `Configured` class implementing `Closeable`, `DelegationTokenIssuer`, and `PathCapabilities`. The covered portion exposes the central legacy filesystem contract.

Important static factory/discovery APIs include `get(...)`, `newInstance(...)`, `getDefaultUri()`, `setDefaultUri()`, `getLocal()`, `newInstanceLocal()`, `closeAll()`, `closeAllForUGI()`, and `getFileSystemClass()`. `get(URI, Configuration)` may return cached instances unless `fs.$SCHEME.impl.disable.cache` is true; `newInstance(...)` always returns a new initialized object. `getFileSystemClass()` scans service-loaded implementations and configuration bindings.

Core identity and path APIs include `initialize()`, `getScheme()`, abstract `getUri()`, `getCanonicalUri()`, `canonicalizeUri()`, `getDefaultPort()`, `getCanonicalServiceName()`, deprecated `getName()`/`getNamed()`, `makeQualified()`, and protected `checkPath()`.

The covered I/O contract includes many overloads and hooks:

- block locations and server defaults: `getFileBlockLocations(...)`, `getServerDefaults(...)`;
- open APIs: `open(Path)`, `open(Path, int)`, `open(PathHandle)`, `open(PathHandle, int)`;
- path handles: `getPathHandle()` and protected `createPathHandle()`;
- create APIs: multiple `create(...)` overloads, the abstract full-parameter create method, flag/checksum create overloads, protected `primitiveCreate()`, `primitiveMkdir()`, and `createNonRecursive(...)`;
- append and concat: `append(...)` overloads, abstract append-with-buffer/progress, and optional `concat()`;
- namespace mutation: abstract `rename(Path, Path)`, protected rename-with-options, `truncate()`, abstract `delete(Path, boolean)`, deprecated `delete(Path)`, `deleteOnExit()`, `cancelDeleteOnExit()`, and protected `processDeleteOnExit()`;
- existence and metadata helpers: `exists()`, deprecated `isDirectory()`, deprecated `isFile()`, deprecated `getLength()`, `getContentSummary()`, `getQuotaUsage()`, quota setters, abstract `listStatus()`, filtered/glob/list-located/list-files/list-iterator APIs, `getHomeDirectory()`, abstract working directory accessors, and `getInitialWorkingDirectory()`;
- local copy helpers: `copyFromLocalFile()`, `moveFromLocalFile()`, `copyToLocalFile()`, `moveToLocalFile()`, `startLocalOutput()`, and `completeLocalOutput()`;
- closure and capacity/defaults: `close()`, `getUsed()`, deprecated `getBlockSize()`, default block size and default replication methods;
- filesystem metadata: abstract `getFileStatus()`, `msync()`, symlink support, checksums, status/capacity, permissions, owners, times, snapshots, ACLs, xattrs, storage policies, trash roots, path capabilities, and multipart/builder APIs.

Statistics APIs are split between deprecated synchronized global maps/lists (`getStatistics()`, `getAllStatistics()`, `getStatistics(scheme, cls)`) and modern `StorageStatistics` / `GlobalStorageStatistics`. Static `clearStatistics()` and `printStatistics()` remain available.

## Control Flow

For `FileContext`, the intended flow is: construct a context from configuration or an explicit default filesystem; qualify or resolve user paths using the context default filesystem and working directory; locate the bonded `AbstractFileSystem` for the path; then delegate the actual operation to that filesystem. Builder APIs defer filesystem mutation until `build()` is called. The `create(Path)` builder explicitly says `FileContext` verifies builder parameters and then calls `AbstractFileSystem#create`.

For symlink operations, intermediate path components are transparently resolved in most calls, while the final component is treated specially for delete, delete-on-exit, rename, `getLinkTarget()`, and `getFileLinkStatus()`. Create and mkdir expect the final component not to exist; most other operations follow the final symlink.

For `FileSystem` acquisition, `get(URI, conf)` follows a cache-first path unless disabled by `fs.$SCHEME.impl.disable.cache`; `newInstance(...)` bypasses the cache. Initialization happens after construction through `initialize(URI, Configuration)`, and subclasses overriding it must call the superclass.

For `FileSystem` write operations, simple overloads funnel toward fuller methods with default buffer sizes, replication, block size, permission, flags, progress callback, and checksum options. The abstract full create method is the real subclass contract, while `primitiveCreate()` and `primitiveMkdir()` exist so `FileContext` can pre-apply umask and pass absolute permissions during the transition from `FileSystem` to `FileContext`.

For builders, `createFile()` and `appendFile()` return `FSDataOutputStreamBuilder`; `openFile()` returns `FutureDataInputStreamBuilder`. The protected `openFileWithOptions()` methods are the real execution hooks. The base implementation performs a blocking `open(...)` call and wraps the result in a `CompletableFuture`, so asynchronous-looking APIs may still execute synchronously unless overridden.

For lifecycle, `deleteOnExit()` records paths on an instance; cached instances are closed during clean JVM shutdown, which then processes recursive deletion. `close()` releases locks, processes delete-on-exit paths, and removes the instance from the cache if cached. `closeAll()` and `closeAllForUGI()` operate over cached instances.

## State and Persistence Behavior

This chunk defines public API state rather than storage internals.

`FileContext` state is per object: default filesystem, working directory, umask, and UGI. It also participates in global `AbstractFileSystem` statistics and has a shutdown hook priority for cleanup behavior. `setWorkingDirectory()` deliberately stores the path as a prefixing rule rather than following symlinks to an inode, which is important in a distributed namespace with multiple roots.

`FileStatus` is a persistent/wire-facing metadata record. Its `Writable` methods still exist but are deprecated in favor of protobuf conversion. Serialized status must preserve path, type, symlink, permission, owner/group, timestamps, block metadata, and attribute flags. Java object deserialization invokes `validateObject()`.

`ContentSummary` is a `Writable` content/quota summary. Its public persistence surface includes both legacy constructor semantics and newer builder-derived fields, especially the distinction between logical length and space consumed.

`FileSystem` has significant global and instance state implied by the API:

- a cache of filesystem instances keyed by URI/user/config context;
- per-instance configuration, URI identity, delete-on-exit path list, checksum verification/write flags where supported, working directory in legacy implementations, and statistics;
- global storage statistics and deprecated global statistics maps;
- static symlink enablement toggles;
- service-loader-discovered implementation classes and configuration-based scheme bindings;
- delegation-token service names derived from canonical URI and port when a filesystem issues its own tokens.

Actual file, directory, ACL, xattr, snapshot, quota, storage-policy, and trash persistence is delegated to filesystem implementations such as HDFS, local filesystems, and object-store connectors.

## Dependencies and Integration Points

The APIs depend heavily on Hadoop Common types:

- `Configuration`, `Configured`, and `CommonConfigurationKeysPublic` for runtime defaults;
- `Path`, `PathHandle`, `PathFilter`, `RemoteIterator`, `BlockLocation`, `FsStatus`, `FsServerDefaults`, `StorageType`, `BlockStoragePolicySpi`, and stream builders for filesystem operations;
- `FSDataInputStream`, `FSDataOutputStream`, `FutureDataInputStreamBuilder`, `FSDataOutputStreamBuilder`, and `MultipartUploaderBuilder` for I/O;
- `FsPermission`, `AclStatus`, ACL entries, and xattr flags for metadata;
- `UserGroupInformation`, `DelegationTokenIssuer`, and token service naming for security;
- `AbstractFileSystem` and `DelegateToFileSystem` as `FileContext` and builder integration points;
- `ServiceLoader` and `fs.$SCHEME.impl` configuration bindings for filesystem implementation discovery;
- `PBHelper` for protobuf-compatible `FileStatus` serialization.

The covered constants integrate with `core-default.xml` and with components such as KMS clients, shell commands, HTTP servers, credential providers, shutdown hooks, metrics, and config redaction. The API also preserves multiple deprecated methods and fields because external applications compile against this surface.

## Risks and Edge Cases

The JDiff file is generated compatibility metadata. A missing, renamed, visibility-changed, or deprecation-changed member can break downstream source or binary compatibility even if implementation behavior is unchanged.

`ContentSummary` constructor compatibility is subtle because legacy constructors may imply `spaceConsumed == length`, while builder code can separate those values. Output formatting has many boolean options whose meanings are easy to invert; the x-option documentation says false includes snapshot calculations and true excludes them.

`CreateFlag` combinations control destructive behavior. Incorrect validation around `APPEND`, `OVERWRITE`, or `CREATE` can cause accidental overwrite, failed append, or non-atomic create behavior.

`FileContext` path resolution differs from Unix working-directory semantics. The working directory is a prefix, not an inode reference, and relative paths with schemes are illegal. Symlink final-component behavior differs by operation, so clients and filesystem implementations must agree on whether links are followed or operated on directly.

`FileSystem.get()` caching is a common source of state leakage. Callers expecting isolated checksum flags, working directories, delete-on-exit lists, statistics, or credentials may need `newInstance(...)` or cache-disabling configuration. Conversely, overuse of uncached instances can bypass shared lifecycle cleanup.

`deleteOnExit()` is best-effort and can make JVM shutdown slow or unreliable on remote/object stores. The documentation warns that clean shutdown is not guaranteed and that existence/deletion costs can dominate shutdown time.

Many `FileSystem` operations are optional with default `UnsupportedOperationException`, no-op, null, true, or empty-statistics behavior. Examples include append, concat, truncate, symlinks, checksums, ACLs, xattrs, snapshots, storage policies, multipart upload, and path handles. Generic clients must probe capabilities or handle unsupported operations.

Several deprecated convenience methods (`isFile`, `isDirectory`, `getLength`, `getReplication`, old statistics APIs) perform extra status calls or expose older semantics. The docs explicitly discourage repeated `exists()`/`getFileStatus()` patterns because they may trigger redundant HDFS RPCs.

`FileStatus` equality and ordering are path-based, not based on full metadata. Code using `Set<FileStatus>` or sorted collections can silently collapse entries with the same path but different metadata snapshots.

The base `openFileWithOptions()` wraps a blocking open in a `CompletableFuture`; clients must not assume nonblocking behavior unless a specific filesystem documents an override. Unknown mandatory open-file options are specified to raise `IllegalArgumentException`.

## Test Signals

Compatibility checks should diff this JDiff output against adjacent Hadoop Common versions and flag changes in public classes, method signatures, visibility, abstract/final/static flags, checked exceptions, fields, implemented interfaces, and deprecation strings.

`CreateFlag` tests should cover every documented valid and invalid combination, including path-exists and path-missing cases for create, append, overwrite, append-new-block, sync-block, and lazy-persist options.

`ContentSummary` tests should cover builder construction, legacy constructors, equality/hash behavior, header fields, quota fields, human-readable output, storage-type quota output, snapshot-inclusive/exclusive output, erasure-coding policy display, and writable/protobuf interoperability where applicable.

`FileStatus` tests should cover constructors with and without symlinks, attribute boolean-to-set conversion, default permission/owner/group behavior for nulls, path-based equality/ordering, raw-object `compareTo(Object)` binary compatibility, protobuf conversion, deprecated `Writable` read/write, and object validation after Java serialization.

`FileContext` tests should exercise default, local, explicit URI, explicit `AbstractFileSystem`, and explicit configuration factories; working-directory qualification; invalid relative-with-scheme paths; umask application; server-default propagation; create builder build-time validation; symlink target resolution cases; ACL/xattr/snapshot/storage-policy dispatch; `hasPathCapability()` delegation; and statistics collection.

`FileSystem` tests should cover cached versus uncached acquisition, cache disablement via `fs.$SCHEME.impl.disable.cache`, `closeAll()` and `closeAllForUGI()`, service-loader filesystem discovery, canonical URI/default port behavior, token service naming, path qualification/checking, all simple-to-full overload funnels for create/open/append/list/copy, and correct subclass abstract-method dispatch.

Lifecycle tests should verify delete-on-exit registration/cancellation/processing, close removing cached instances, best-effort behavior when paths disappear before shutdown, and performance/failure behavior on slow remote filesystem deletes.

Optional-feature tests should assert default unsupported/no-op/null behavior and implementation overrides for append, concat, truncate, symlinks, checksums, ACLs, xattrs, snapshots, storage policies, path handles, multipart upload, `msync()`, and builder-based open/create/append.

Performance-sensitive tests should detect redundant RPC patterns around `exists()`, `isFile()`, `isDirectory()`, and repeated `getFileStatus()` calls, and should validate lazy/on-demand behavior of `listStatusIterator()` for filesystems that override it.

## Cross-Chunk Notes

The chunk starts after the beginning of `CommonConfigurationKeysPublic`, so the final per-file report should combine this with the previous chunk for the full constants class. It also stops inside `FileSystem` immediately after the `LOG` field begins, so subsequent chunks must supply the remaining fields, nested classes, and methods before drawing conclusions about the complete `FileSystem` API.
