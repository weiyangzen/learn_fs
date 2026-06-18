# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 6041-12112

## Scope

This chunk is generated JDiff compatibility metadata for Apache Hadoop Common 3.3.6. It starts inside `org.apache.hadoop.fs.CommonConfigurationKeysPublic`, covers several complete public API entries in `org.apache.hadoop.fs`, and ends inside the `org.apache.hadoop.fs.FileSystem#getXAttr(Path, String)` declaration.

The source is not implementation code. The useful research surface is the public and protected API contract: class names, inheritance, implemented interfaces, constructors, fields, method overloads, parameter and return types, exceptions, visibility, abstract/final/static flags, deprecation markers, and embedded Javadocs.

## Purpose

The first part of the chunk documents public Hadoop Common configuration keys. These constants bind runtime behavior to `core-default.xml` and user configuration for security group caching, shell group lookup timeouts, Kerberos, RPC protection, crypto codecs and key providers, KMS client caches and failover, secure random providers, safe shell deletion limits, HTTP logs and idle timeouts, credential providers, sensitive-key filtering, tag metadata, service shutdown, Prometheus support, and IPC server metrics scheduling.

The `ContentSummary`, `CreateFlag`, `FileAlreadyExistsException`, and `FileChecksum` entries define core value and validation contracts used by file creation, quota/content accounting, and checksum reporting. They sit beneath both classic `FileSystem` and newer `FileContext` APIs.

The largest part of the chunk covers `FileContext`, `FileStatus`, and the first large portion of `FileSystem`. These are Hadoop's main client-side filesystem contracts. `FileContext` exposes a URI-aware, default-filesystem-aware user interface backed by `AbstractFileSystem`; `FileSystem` exposes the older abstract filesystem base with global cache semantics, URI canonicalization, stream creation/opening, metadata operations, listing, local-copy helpers, symlinks, checksums, status, ACLs, snapshots, storage policies, xattrs, and deletion-on-exit. `FileStatus` is the serializable metadata carrier shared by these APIs.

## Important APIs, Types, and Functions

### Configuration Keys

`CommonConfigurationKeysPublic` fields in this chunk are public static final constants that external callers and downstream modules can rely on. They include:

- Security group cache controls: `HADOOP_SECURITY_GROUPS_CACHE_BACKGROUND_RELOAD_DEFAULT`, `HADOOP_SECURITY_GROUPS_CACHE_BACKGROUND_RELOAD_THREADS`, `HADOOP_SECURITY_GROUPS_CACHE_BACKGROUND_RELOAD_THREADS_DEFAULT`, `HADOOP_SECURITY_GROUP_SHELL_COMMAND_TIMEOUT_KEY`, and deprecated `HADOOP_SECURITY_GROUP_SHELL_COMMAND_TIMEOUT_SECS` aliases.
- Core security identity and authorization keys: `HADOOP_SECURITY_AUTHENTICATION`, `HADOOP_SECURITY_AUTHORIZATION`, `HADOOP_SECURITY_INSTRUMENTATION_REQUIRES_ADMIN`, `HADOOP_SECURITY_SERVICE_USER_NAME_KEY`, `HADOOP_SECURITY_AUTH_TO_LOCAL`, `HADOOP_SECURITY_AUTH_TO_LOCAL_MECHANISM`, DNS interface/nameserver keys, token files, and HTTP authentication type.
- Kerberos and SASL controls: minimum seconds before relogin, keytab auto-renewal flag, `HADOOP_RPC_PROTECTION`, and `HADOOP_SECURITY_SASL_PROPS_RESOLVER_CLASS`.
- Crypto and key-provider controls: codec class keys, AES CTR no-padding defaults, cipher suite, JCE provider, JCEKS serial filter, crypto buffer size, impersonation provider, key-provider path, default key bit length, and default cipher.
- KMS client tuning: encrypted-key cache size, low watermark, refill thread count, expiry, timeout, failover retry count, and failover sleep bounds.
- Secure random and shell/http/service controls: Java secure random algorithm, secure random implementation and device path, missing-default-FS shell warning, safe delete limit, HTTP logs, credential provider path/fallback/password file, sensitive config keys, system/custom tags, service shutdown timeout, Prometheus flag, HTTP idle timeout, and IPC server metrics update runner interval.

Two tag constants, `HADOOP_SYSTEM_TAGS` and `HADOOP_CUSTOM_TAGS`, are deprecated in favor of `HADOOP_TAGS_SYSTEM` and `HADOOP_TAGS_CUSTOM`. The group shell command timeout `*_SECS` constants are deprecated in favor of `*_KEY` and `*_DEFAULT`.

### Content and Creation Contracts

`ContentSummary` extends `QuotaUsage` and implements `Writable`. Visible constructors are retained for compatibility but their Javadocs point callers toward `ContentSummary.Builder`. Accessors expose length, file count, directory count, snapshot length/file/directory counts, snapshot space consumption, and erasure coding policy. Formatting methods include static header helpers and multiple `toString(...)` overloads for quota output, human-readable output, storage-type quota display, and snapshot-inclusive or snapshot-exclusive output. `toSnapshot(boolean)` formats snapshot counts.

`CreateFlag` is an enum API for create/append semantics. Static validators check invalid combinations generally, for create with path existence, and for append. Javadocs define legal combinations such as `CREATE`, `APPEND`, `OVERWRITE`, `CREATE|APPEND`, `CREATE|OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`, while explicitly rejecting `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`.

`FileAlreadyExistsException` is the typed `IOException` for operations whose target already exists and is not configured for overwrite.

`FileChecksum` is an abstract `Writable` exposing algorithm name, checksum byte length, raw checksum bytes, optional `Options.ChecksumOpt`, and equality/hash behavior based on algorithm and value.

### FileContext

`FileContext` implements `PathCapabilities` and provides factory methods for default, local, URI-specific, `Configuration`-specific, and `AbstractFileSystem`-specific contexts. It has protected `getFSofPath(Path)` routing to the backing `AbstractFileSystem`.

The visible operations include working directory and umask state (`setWorkingDirectory`, `getWorkingDirectory`, `getUMask`, `setUMask`), user identity (`getUgi`), home directory lookup, path resolution and qualification, file create through both direct `FSDataOutputStream` and `FSDataOutputStreamBuilder`, mkdir, delete, open, truncate, set replication, rename, permission/owner/time setters, checksum and checksum verification controls, file and link status, symlink creation and target lookup, filesystem status, list status and located status iterators, corrupt block listing, delete-on-exit, symlink resolution helpers, and filesystem statistics inspection.

It also exposes advanced metadata and policy operations: ACL modification/removal/replacement/status, xattr set/get/list/remove, snapshot create/rename/delete, storage policy satisfy/set/unset/get/list, builder-based `openFile`, path capability checks, server-default lookup by path, and multipart uploader creation.

Public constants include `LOG`, compatibility `DEFAULT_PERM`, separate `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`.

### FileStatus

`FileStatus` implements `Writable`, `Comparable`, `Serializable`, and `ObjectInputValidation`. Constructors cover legacy metadata without symlinks, metadata with symlink path, metadata with boolean attributes, metadata with an attribute set, a no-arg constructor, and a copy constructor.

The API exposes length, file/directory/symlink classification, deprecated `isDir()`, block size, replication, modification/access times, permission, ACL/encryption/erasure-coding/snapshot-enabled flags, owner, group, path, symlink, setters for path and symlink, protected defaulting setters for permission/owner/group, comparison, equality, hash, string rendering, protobuf-backed `readFields`/`write` methods deprecated in favor of PBHelper/protobuf use, and `validateObject`.

`FileStatus.attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts booleans to an attribute flag set. `NONE` is a shared empty attribute set for the common case.

### FileSystem

`FileSystem` is abstract, extends `Configured`, and implements `Closeable`, `DelegationTokenIssuer`, and `PathCapabilities`. The chunk covers its protected constructor and a large part of its public/protected/static contract.

Instance acquisition and lifecycle APIs include `get(URI, Configuration, String)`, `get(Configuration)`, `get(URI, Configuration)`, `newInstance(...)` overloads, `getLocal`, `newInstanceLocal`, `closeAll`, and `closeAllForUGI`. Javadocs specify the important cache behavior: `get(URI, Configuration)` may return a cached instance unless `fs.$SCHEME.impl.disable.cache` is true, while `newInstance` always creates a unique instance.

URI and identity methods include `getDefaultUri`, `setDefaultUri`, `initialize`, `getScheme`, abstract `getUri`, protected `getCanonicalUri`, protected `canonicalizeUri`, protected `getDefaultPort`, protected static `getFSofPath`, `getCanonicalServiceName`, deprecated `getName`, deprecated `getNamed`, `makeQualified`, and protected `checkPath`.

Data path APIs include static permission-preserving `create(FileSystem, Path, FsPermission)` and `mkdirs(FileSystem, Path, FsPermission)`, multiple `open(Path)` and `open(PathHandle)` overloads, `getPathHandle` with protected `createPathHandle`, many `create(...)` overloads, abstract full-argument `create`, `primitiveCreate`, `primitiveMkdir`, `createNonRecursive` overloads, non-atomic `createNewFile`, append overloads including append-to-new-block, `concat`, replication getters/setters, abstract boolean `rename`, protected option-based rename, `truncate`, abstract recursive delete, deprecated single-argument delete, delete-on-exit registration/cancellation/processing, existence/type/length helpers, content summary and quota usage, quota setters, list/glob/located status APIs, local/remote copy and move helpers, local-output staging, close, used/block-size/default-block/default-replication helpers, file status, and metadata synchronization via `msync`.

The latter visible part covers `fixRelativePart`, symlink create/status/target/resolve support, checksum lookup for whole files and prefix ranges, checksum verification/write toggles, filesystem capacity status, permission/owner/time setters, snapshots, ACLs, and the beginning of xattr support (`setXAttr` overloads and the start of `getXAttr`).

## Control Flow

The XML itself has no executable control flow, but the API contracts imply several important flows.

Configuration flow starts with keys from `CommonConfigurationKeysPublic` being read from `Configuration` and `core-default.xml`, then consumed by security, HTTP, KMS, crypto, shell, service, and metrics subsystems. The constants are compatibility anchors: downstream code compiles against these names and expects the runtime configuration files to use the same string values.

File creation flow validates `CreateFlag` combinations first, then routes through `FileContext#create` or `FileSystem#create`. `FileContext` applies its umask and server-default logic before invoking the target `AbstractFileSystem`; `FileSystem` exposes compatibility helpers such as `primitiveCreate` for the FileSystem-to-FileContext transition. Builder-based create delays final validation and filesystem mutation until `build()`.

Path routing flow in `FileContext` resolves working-directory-relative and slash-relative paths using a default filesystem and the context working directory. It then selects an `AbstractFileSystem` with `getFSofPath` and delegates operations. In `FileSystem`, `checkPath`, URI canonicalization, and scheme/authority matching guard whether a path belongs to an instance.

Filesystem lookup flow differs between cached and uncached APIs. `FileSystem.get(...)` can return a cached initialized instance keyed by scheme/authority/user/config behavior; `newInstance(...)` always creates a unique instance. `closeAll` and `closeAllForUGI` close cached instances and can invalidate objects still referenced by callers.

Read flow uses `open(Path, bufferSize)` or builder-based `openFile(Path)`; path-handle reads use a durable serializable handle and may verify constraints encoded when the handle was created. Block-location flow maps a file range to physical hosts for distributed filesystems or a default localhost block for simpler filesystems.

Write flow uses create, append, concat, truncate, replication, and checksum options. `truncate` has an asynchronous completion signal: `true` means immediately reusable, while `false` means a background block-length adjustment is still running.

Metadata flow uses `FileStatus` and `ContentSummary` as carriers. List/glob/located-status methods return arrays or `RemoteIterator`s; ACL, xattr, snapshot, and storage-policy methods mutate or retrieve metadata on the underlying filesystem, with unsupported implementations allowed to throw `UnsupportedOperationException`.

Delete-on-exit flow registers paths on a `FileSystem` instance and processes them when the instance closes or a clean JVM shutdown closes cached filesystems. This makes correctness depend on cache use and lifecycle ordering.

## State and Persistence Behavior

This JDiff file persists the 3.3.6 API signature set for compatibility comparison. It does not store Hadoop runtime state, but many APIs in the range define stateful or durable behavior.

`FileContext` stores process-local user-facing state: default filesystem, working directory, umask, and UGI. Its Javadocs emphasize that working directory behavior is prefix-based rather than inode-based, so setting the working directory does not resolve symlinks the way a Unix process directory might.

`FileSystem` has process-global cache state behind `get(...)` and static close operations. Cached instances share lifecycle and delete-on-exit processing; unique `newInstance(...)` objects bypass the cache. `initialize(URI, Configuration)` is the transition point between construction and ready-for-use state, and subclasses overriding it must call the superclass.

Persistent filesystem state is changed by create, append, concat, truncate, rename, delete, mkdir, set replication, set permission, set owner, set times, symlink creation, snapshot operations, ACL mutation, xattr mutation, storage-policy changes, and quota changes. Some operations are optional or implementation-dependent, especially append, concat, truncate, symlinks, ACLs, xattrs, snapshots, and storage policies.

`FileStatus`, `ContentSummary`, and `FileChecksum` are value carriers with serialization or equality contracts. `FileStatus` retains protobuf-backed `Writable` methods for compatibility but deprecates them in favor of PBHelper/protobuf direct use. `ContentSummary` inherits quota state from `QuotaUsage` and adds snapshot and erasure-coding fields. `FileChecksum` equality depends on both algorithm and byte value.

Configuration-key state is externalized in `Configuration` and core XML files. Security and crypto settings are especially durable from an operator perspective because they affect authentication, key provider selection, credential fallback, random source selection, group lookup cache behavior, and KMS failover behavior.

## Dependencies and Integration Points

This chunk depends on Java platform types such as `URI`, `DataInput`, `DataOutput`, `IOException`, `FileNotFoundException`, `InvalidObjectException`, arrays, collections, enums, and `Serializable`/`ObjectInputValidation`.

Key Hadoop dependencies include `org.apache.hadoop.conf.Configuration`, `org.apache.hadoop.conf.Configured`, `org.apache.hadoop.fs.Path`, `AbstractFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, stream builders, `RemoteIterator`, `BlockLocation`, `BlockStoragePolicySpi`, `FsServerDefaults`, `FsStatus`, `MultipartUploaderBuilder`, `PathHandle`, `Options.*`, `PathCapabilities`, `QuotaUsage`, `StorageType`, `ParentNotDirectoryException`, `UnsupportedFileSystemException`, `UnresolvedLinkException`, `InvalidPathHandleException`, and `InvalidPathException`.

Security integration points include `UserGroupInformation`, `AccessControlException`, delegation token issuance, token service-name construction, Kerberos relogin settings, RPC protection, SASL property resolution, group mapping, impersonation provider selection, and credential-provider configuration.

Permission and metadata integration points include `FsPermission`, `AclStatus`, ACL entry lists, xattr name/value maps, snapshot management, storage policies, erasure-coding and encryption status, and PBHelper/protobuf serialization for `FileStatus`.

Operational integration points include `core-default.xml`, HTTP/logging/Prometheus settings, shutdown hook management, shell command behavior, KMS client caches and failover, secure random implementation selection, and IPC server metrics update scheduling. `FileContext.LOG` uses SLF4J.

## Risks and Edge Cases

- The chunk begins and ends inside larger class declarations. Adjacent chunks are required for complete `CommonConfigurationKeysPublic` and `FileSystem` coverage.
- JDiff metadata omits method bodies. Exact cache keys, synchronization, exception mapping, path normalization, flag validation, and filesystem-specific behavior require implementation-source review.
- Public configuration constants are compatibility-sensitive. Renaming, removing, or changing string values can silently break operator configuration, security behavior, and downstream compilation.
- Deprecated aliases remain part of the public API. Removing `*_SECS`, `HADOOP_SYSTEM_TAGS`, `HADOOP_CUSTOM_TAGS`, `FileSystem#getName`, `FileSystem#getNamed`, `FileStatus#isDir`, or deprecated `FileStatus` Writable methods can break binary or source compatibility.
- `CreateFlag` validation is safety-critical. Accepting `APPEND|OVERWRITE` or mishandling `CREATE|APPEND`/`CREATE|OVERWRITE` changes data-loss behavior.
- `SYNC_BLOCK` Javadocs warn that callers still need `Syncable#hsync()` after each write for true synchronous behavior. Misunderstanding this flag can produce durability gaps.
- `LAZY_PERSIST` depends on transient storage availability and may not behave consistently across filesystems.
- `ContentSummary` output has many option combinations. Snapshot inclusion/exclusion, storage-type quota display, and human-readable formatting are easy to regress in CLI-visible output.
- `FileContext` working directories are prefix-based and do not follow symlinks. Code expecting Unix inode-like current-directory semantics may resolve paths differently.
- `FileSystem.get(...)` cache behavior can leak stale configuration, credentials, delete-on-exit registrations, or lifecycle state across callers if cache disabling and `newInstance` are used incorrectly.
- `closeAll` and `closeAllForUGI` can invalidate cached instances still held by application code.
- `initialize(...)` override ordering matters. Subclasses that fail to call `super.initialize` or mutate configuration incorrectly can break statistics, caching, and URI setup.
- URI canonicalization may add default ports or canonicalize hosts. Token service names and cache keys can change if this logic is inconsistent.
- `checkPath` performs scheme/authority matching and subclasses may vary; case sensitivity and authority normalization are common cross-filesystem pitfalls.
- `createNewFile` is explicitly not atomic by default, so it is unsafe as a distributed lock primitive unless overridden atomically.
- `rename` atomicity is filesystem-dependent, and the option-based default implementation is documented as non-atomic.
- `truncate` returning `false` means clients must wait before appending or otherwise updating the file. Ignoring this can corrupt workflow assumptions.
- `setReplication` returns true even when replication is unsupported in the default implementation, so callers cannot always infer that storage replication changed.
- `getFileBlockLocations` has edge semantics for null file status, ranges beyond EOF, replicated files, and erasure-coded logical block groups.
- `PathHandle` references depend on stored constraints; stale or moved files may throw `InvalidPathHandleException`.
- `FileStatus` equality and hash are path-based, not full metadata-based. Collections keyed by `FileStatus` may ignore changes to length, owner, permission, or attributes.
- `FileStatus` permissions default to all-access when unavailable. Consumers must not assume a permissive value means the backing filesystem actually enforces those permissions.
- ACL and xattr APIs may be unsupported. Callers must handle `UnsupportedOperationException` as well as `IOException`.
- XAttr names must include a namespace prefix such as `user.`. Validation differences can create compatibility problems with HDFS documentation and CLI behavior.
- Delete-on-exit only runs for clean shutdown or close processing; non-cached filesystems and abnormal termination need explicit cleanup.

## Test Signals

Useful validation for this API surface should include:

- JDiff/API compatibility checks that all fields, classes, constructors, methods, overloads, visibility flags, abstract/static/final markers, exception declarations, and deprecation strings in lines 6041-12112 remain stable.
- Configuration tests that load representative keys from `core-default.xml`, verify deprecated aliases still map as expected, and cover security group cache reload settings, Kerberos relogin/renewal, RPC protection, crypto/key-provider settings, KMS cache/failover, credential fallback, sensitive-key filtering, HTTP idle/log settings, service shutdown, Prometheus, and IPC metrics scheduling.
- `CreateFlag` tests for every documented valid and invalid combination, including path-exists versus path-missing cases and append-specific validation.
- `ContentSummary` tests for constructor compatibility, builder equivalence, getters, equality/hash, headers, quota fields, human-readable formatting, storage-type display, snapshot fields, erasure-coding policy, and `Writable` round trips inherited through the class.
- `FileChecksum` tests for algorithm/length/bytes/checksum option reporting, equality/hash behavior, and filesystem checksum null handling.
- `FileContext` tests for every factory overload, default URI handling, local context creation, working directory legal/illegal forms, prefix-based relative resolution, umask application, path qualification, UGI exposure, and unsupported filesystem failures.
- `FileContext` operation tests for create builder and direct create, mkdir parent behavior, delete recursion, open buffer sizes, truncate true/false completion, replication, rename overwrite semantics, permission/owner/time setters, checksum verify toggles, file/link status, symlink creation/target lookup, list iterators, corrupt block listing, delete-on-exit, statistics, ACLs, xattrs, snapshots, storage policies, server defaults, path capabilities, `openFile`, and multipart uploader creation.
- `FileStatus` tests for all constructors, attribute flag conversion, getters, setters, symlink behavior, path-based compare/equality/hash, deprecated `isDir`, protobuf-backed deprecated read/write compatibility, Java object validation, and copy-constructor behavior.
- `FileSystem` cache tests for `get` versus `newInstance`, cache-disable configuration, user-specific lookup, closeAll/closeAllForUGI lifecycle behavior, local filesystem factories, and behavior after cached instances are closed.
- URI and path tests for default URI get/set, `initialize` superclass requirements, `getScheme` defaults, canonical URI/default port behavior, canonical service name/token integration, deprecated `getName`/`getNamed`, `makeQualified`, and `checkPath` mismatch failures.
- Data operation tests for all visible `open`, `open(PathHandle)`, `getPathHandle`, create overloads, primitive create/mkdir, non-recursive create parent failures, non-atomic `createNewFile`, append overloads including append-to-new-block, concat unsupported/default behavior, replication default behavior, rename option semantics and atomicity expectations, truncate asynchronous completion, recursive delete, exists/isDirectory/isFile/getLength helpers, quota/content summary, listing/globbing/located status, local copy/move helpers, local-output staging, close, used/default block/default replication, and `msync`.
- Metadata tests for symlink support, checksum range and full-file lookups, checksum verification/write flags, filesystem status by root/path, permission/owner/time setters, snapshot lifecycle, ACL merge/remove/replace/status, and xattr set/get behavior at the chunk boundary.
