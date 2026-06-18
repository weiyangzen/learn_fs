# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 6057-12223

## Scope

This chunk is a jdiff public API description for Hadoop Common 3.5.0. It starts near the end of `org.apache.hadoop.fs.CommonConfigurationKeysPublic`, covers several core `org.apache.hadoop.fs` public APIs, and ends inside the `FileSystem.create(Path, FsPermission, boolean, int, short, long, Progressable)` method documentation. The source is XML metadata generated from Java APIs, so it exposes class/interface names, signatures, exception contracts, visibility, deprecation text, and Javadoc, but not method bodies.

The covered API surface is:

- The tail of `CommonConfigurationKeysPublic`, with public configuration-key constants for TFile, caller context, IPC, security, crypto, KMS, shell, HTTP, credential providers, tags, service shutdown, Prometheus, metrics, and JMX NaN filtering.
- `ContentSummary`, `CreateFileOptionKeys`, `CreateFlag`, and `FSBuilder`.
- Stream wrappers and primitives: `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `FSError`, `FSInputStream`, `FileAlreadyExistsException`, and `FileChecksum`.
- The main `FileContext` API range from construction and path resolution through create/open/mkdir/delete/rename, symlink handling, listing, ACLs, xattrs, snapshots, storage policies, builder-based open, path capabilities, server defaults, multipart upload creation, and public constants.
- `FileStatus`, including serialization/deprecation notes and file attribute flags.
- The beginning of `FileSystem`, including instance lookup/caching, URI canonicalization, delegation token hooks, block-location APIs, server defaults, path handles, open overloads, and create overloads through the abstract permission-bearing create method.

## Purpose

The chunk documents the public filesystem contract exported by Hadoop Common. The APIs provide the common layer used by HDFS, local filesystems, object-store connectors, view filesystems, and other `FileSystem` or `AbstractFileSystem` implementations.

At a high level, the chunk defines:

- Configuration keys that external deployments and connectors depend on.
- File metadata models (`ContentSummary`, `FileStatus`, `FileChecksum`).
- Stream and builder abstractions used for data reads/writes.
- Operation contracts for create, open, delete, rename, symlink, ACL, xattr, snapshot, storage policy, and capability discovery.
- Compatibility contracts such as deprecated overloads, default methods, `Writable` serialization, `Serializable`, and binary-compatible `compareTo(Object)`.

Because this is a generated API XML, the research value is in the public contract: which methods are abstract versus defaulted, what callers may rely on, what implementors must override, and which behaviors vary by backing filesystem.

## Important APIs And Types

### `CommonConfigurationKeysPublic`

The covered tail of this constants class exposes public keys and defaults for common Hadoop behavior. The class doc says it contains publicly documented configuration keys used by common code and that callers should generally use `CommonConfigurationKeys` rather than this class directly.

Notable constant families:

- TFile I/O and filesystem input/output buffer sizing.
- Caller context enablement, maximum context size, signature size, and separator.
- IPC client and server controls: max idle time, connect timeout, max retries, retry interval, socket-timeout retries, TCP no-delay, low latency, listen queue size, idle threshold, connection kill max, server reuse-address, max connections, slow RPC logging, purge interval, socket factory, SOCKS server, and server metrics update interval.
- Security group mapping and group cache controls, including positive/negative cache seconds, warning threshold, background reload, reload threads, and shell command timeout. Some older timeout constants are explicitly deprecated in favor of newer names.
- Authentication and authorization keys: security authentication, authorization, instrumentation admin requirement, service user name, auth-to-local rules and mechanism, DNS interface/nameserver, token file/env keys, HTTP authentication type, Kerberos relogin and keytab auto-renewal, RPC protection, SASL mechanism and callback/property resolver hooks.
- Crypto and key management: codec class prefixes for AES/SM4 CTR no-padding, cipher suite, JCE provider and auto-add flag, JCEKS serialization filter, crypto buffer size, impersonation provider, key provider path, default key bit length/cipher, KMS encrypted-key cache sizing, low watermark, refill threads, expiry, client timeout, and failover retry/sleep controls.
- Secure random configuration: Java secure random algorithm, implementation, OpenSSL engine ID, and random device path.
- Shell, HTTP, credentials, secret manager, sensitivity, tags, shutdown, Prometheus, idle timeout, and JMX NaN filtering controls.

These fields are dependency anchors for `core-default.xml`, security setup, RPC behavior, object store integrations, and operational observability.

### `ContentSummary`

`ContentSummary` extends `QuotaUsage` and implements `Writable`. It stores summary information for a file or directory, including content length, file count, directory count, quotas inherited from `QuotaUsage`, snapshot counts/space, and erasure coding policy.

Important APIs:

- Deprecated constructors remain for compatibility; docs direct newer code toward `ContentSummary.Builder`.
- Getters expose length, file count, directory count, snapshot length/file/directory counts, snapshot space consumed, and erasure coding policy.
- `write(DataOutput)` and `readFields(DataInput)` preserve Hadoop `Writable` serialization.
- `equals()` and `hashCode()` define value comparison behavior.
- Static header helpers return formatted field names for summary and quota output.
- Multiple `toString(...)` overloads format summary output with quota, human-readable, storage-type, and snapshot options.
- `toErasureCodingPolicy()` and `toSnapshot(boolean)` format EC policy and snapshot data.

The control-flow contract is mostly formatting selection: flags such as `qOption`, `hOption`, `tOption`, and `xOption` determine which counters and quota fields appear and whether byte counts are humanized.

### `CreateFileOptionKeys`

This interface defines standard `createFile()` builder option keys, especially for object stores and commit-style writes.

Important options:

- `FS_OPTION_CREATE_CONDITIONAL_OVERWRITE`: defers the overwrite/existence check until stream `close()` for implementations that manifest objects at close time. If passed as a mandatory option and supported/enabled, the filesystem must omit early overwrite checks and perform an atomic existence-check-and-create at close. Unsupported mandatory use must be rejected.
- `FS_OPTION_CREATE_CONDITIONAL_OVERWRITE_ETAG`: conditional overwrite based on a non-empty ETag string returned by an ETag source. Supported stores must compare the target object's ETag and reject missing or mismatched targets. The check/create may occur at `create()` or `close()`, but must be atomic.
- `FS_OPTION_CREATE_IN_CLOSE`: declares files or objects are created in `close()` rather than in `create()` or `createFile()`.
- `FS_OPTION_CREATE_CONTENT_TYPE`: supplies a content type/file type string.

The important integration point is capability discovery: supported features should be exported as path capabilities and stream capabilities so clients can decide whether optional or mandatory builder parameters are valid.

### `CreateFlag`

`CreateFlag` is the enum contract for file creation and append semantics. The documented combinations include:

- `CREATE`: create only if absent.
- `APPEND`: append only if present.
- `OVERWRITE`: truncate/overwrite existing file.
- `CREATE|APPEND`: create if absent, append if present.
- `CREATE|OVERWRITE`: create if absent, overwrite if present.
- `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK` as additional durability/storage/write-placement semantics.

Validation methods reject invalid combinations. The docs explicitly call out `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE` as invalid and describe `validateForAppend()` as requiring `APPEND` and prohibiting `OVERWRITE`.

### `FSBuilder<S,B>`

`FSBuilder` is the generic builder interface for filesystem and file-context operations. It separates optional parameters from mandatory parameters:

- `opt(...)` sets optional options that implementations may ignore.
- `must(...)` sets required options; if unsupported or unavailable, `build()` should fail with `IllegalArgumentException`.
- `optLong`, `optDouble`, `mustLong`, and `mustDouble` exist to avoid overload ambiguity and precision loss. The older float/double/long overloads have deprecation notes where values are converted in surprising ways.
- `build()` may throw `IllegalArgumentException`, `UnsupportedOperationException`, or `IOException`.

This is central to extensible APIs such as open/create builders where object stores and specialized filesystems need extra implementation-specific options without changing every public method signature.

### `FSDataInputStream` And `FSInputStream`

`FSInputStream` is the abstract seekable positioned-read base class. It extends `InputStream` and implements `Seekable` and `PositionedReadable`. It requires subclasses to implement `seek(long)`, `getPos()`, and `seekToNewSource(long)`, and provides positioned `read` and `readFully` helpers plus argument validation. `validatePositionedReadArgs()` rejects negative positions, invalid buffer regions, and other illegal arguments.

`FSDataInputStream` wraps an `FSInputStream` in `DataInputStream` and exposes a richer capability set:

- Seek and position APIs.
- Positioned byte-array reads and `readFully`.
- `ByteBufferReadable`, `ByteBufferPositionedReadable`, enhanced byte-buffer access with `ByteBufferPool`, and `releaseBuffer`.
- Readahead/drop-behind controls.
- `CanUnbuffer`, `StreamCapabilities`, and `IOStatisticsSource`.
- Vector-read controls: minimum seek, maximum read size, and `readVectored(...)` with allocator and optional release callback.

The stream delegates most behavior to its wrapped stream. That means correctness depends on the underlying filesystem stream implementing the optional interfaces it advertises. Unsupported operations may throw `UnsupportedOperationException`.

### `FSDataOutputStream` And `FSDataOutputStreamBuilder`

`FSDataOutputStream` wraps an `OutputStream` in `DataOutputStream` and implements `Syncable`, `CanSetDropBehind`, `StreamCapabilities`, `IOStatisticsSource`, and `Abortable`.

Important methods:

- `getPos()` returns current write offset.
- `close()` closes the underlying stream.
- `hflush()` and `hsync()` expose Hadoop write durability semantics.
- `setDropBehind(Boolean)` controls cache-dropping where supported.
- `getIOStatistics()` returns nested stream stats or empty stats.
- `abort()` delegates to the wrapped stream if it is `Abortable`, otherwise throws `UnsupportedOperationException`.

`FSDataOutputStreamBuilder` extends `AbstractFSBuilderImpl<S,B>` and accumulates create/append options for a `FileSystem` path:

- File parameters: permission, buffer size, replication, block size, checksum options.
- Operational controls: recursive parent creation, progress callback, create/overwrite/append flags.
- Generic `opt`/`must` parameters inherited from the builder contract.
- `build()` creates the stream and may fail with invalid parameters or filesystem I/O errors.

The builder defaults to not creating missing parent directories. `recursive()` is the explicit opt-in for parent creation.

### `FSError`, `FileAlreadyExistsException`, And `FileChecksum`

`FSError` is an `Error` used for unexpected filesystem failures presumed to reflect native disk errors. Its severity matters: callers should not treat it like normal `IOException` flow.

`FileAlreadyExistsException` is an `IOException` raised when a target already exists and overwrite is not configured.

`FileChecksum` is an abstract `Writable` with `getAlgorithmName()`, `getLength()`, `getBytes()`, optional `getChecksumOpt()`, and equality/hash behavior based on algorithm and bytes. Filesystems that do not implement checksums can return null from higher-level checksum APIs.

## `FileContext` API Surface

`FileContext` is a higher-level user API backed by `AbstractFileSystem`. It implements `PathCapabilities` and exposes operations using `Path`, `Options`, permissions, and richer exception contracts.

### Construction And Path Context

Factory methods create contexts from:

- A supplied `AbstractFileSystem` plus `Configuration`.
- Default configuration.
- Local filesystem defaults.
- A default `URI` with default or explicit configuration.

Context state includes the default filesystem, working directory, user identity (`UserGroupInformation`), and umask. `setWorkingDirectory()` explicitly does not follow symlinks when setting the working directory; it stores the supplied logical working directory behavior used to qualify relative paths. `makeQualified()` applies default filesystem and working directory rules.

### Core Operations

`FileContext` exposes create, builder-based create, mkdir, delete, open, truncate, setReplication, rename, permission/owner/time updates, checksum, checksum verification, status lookup, access checks, symlink status/target lookup, block locations, filesystem status, symlink creation, listings, delete-on-exit, and utility resolution helpers.

The API documents many filesystem-specific exception paths:

- `AccessControlException` for authorization failures.
- `FileAlreadyExistsException` for conflicting create/rename/symlink targets.
- `FileNotFoundException` for missing paths or missing parents.
- `ParentNotDirectoryException` for invalid parent path shape.
- `UnsupportedFileSystemException` for unsupported schemes.
- RPC-related client/server/unexpected server exceptions for remote implementations.
- `InvalidPathException` and argument exceptions for invalid paths or parameters.

Several methods describe implementation-dependent semantics. `rename()` explicitly notes atomicity depends on the filesystem. `truncate()` may return `false` when a background process must finish adjusting the last block before the file can be safely reused for updates.

### Symlink Semantics

The symlink documentation is unusually detailed and is a key behavioral contract:

- Symlink permissions are ignored; target permissions determine access.
- Intermediate symlinks are generally resolved transparently.
- Final-component symlinks are operated on directly by `delete`, `deleteOnExit`, `rename`, `getLinkTarget`, and `getFileLinkStatus`.
- `create()` and `mkdir()` expect a nonexistent final component; an existing symlink is treated like an existing file or directory.
- Most other methods follow the symlink.
- Symlink targets are stored as supplied when the filesystem can store fully qualified URIs.
- Dangling symlinks are permitted.
- Fully qualified, partially qualified, relative, and absolute targets resolve differently based on the target URI and the link path context.

These rules are integration-critical for view filesystems, local filesystems, HDFS, and any connector trying to emulate POSIX-like link behavior.

### ACLs, XAttrs, Snapshots, Storage Policies, And Capabilities

The ACL methods modify, remove, replace, and read ACL state. `setAcl()` must include base entries for user, group, and others for permission-bit compatibility. XAttr methods require names prefixed by namespace, such as `user.attr`, and only return attributes visible to the logged-in user.

Snapshot methods create default or named snapshots, rename snapshots, and delete snapshots. Storage policy methods satisfy, set, unset, query, and enumerate storage policies. These are optional or implementation-specific in many filesystems.

`openFile(Path)` returns a builder whose actual open occurs during `FSDataInputStreamBuilder.build()`. `hasPathCapability(Path, String)` delegates capability checks to the bound `AbstractFileSystem`. `getServerDefaults(Path)` fetches defaults based on a path, and `createMultipartUploader(Path)` returns a builder for multipart uploads.

### Public Constants

`FileContext` exposes `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`. `DEFAULT_PERM` remains for compatibility but docs direct users to separate directory and file defaults because older behavior could create files with execute permissions.

## `FileStatus`

`FileStatus` represents client-side file metadata. It implements `Writable`, `Comparable<Object>`, `Serializable`, and `ObjectInputValidation`.

Important state and APIs:

- Constructors cover minimal metadata, non-symlink filesystems, symlink-aware metadata, boolean attribute flags, explicit `Set<AttrFlags>`, and copy construction.
- `attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts booleans to flags such as ACL, encrypted, erasure-coded, and snapshot-enabled.
- Accessors expose length, file/directory/symlink kind, block size, replication, modification/access times, permissions, owner, group, path, symlink, ACL/encryption/EC/snapshot flags.
- Mutators exist for path, symlink, and protected permission/owner/group normalization.
- Equality, hash code, and compare order are based on path. `compareTo(Object)` was restored for binary compatibility.
- `readFields()` and `write()` are deprecated in favor of PBHelper/protobuf serialization directly, but remain in the API.
- `NONE` is a shared empty attribute set for the common no-attributes case.

The persistence contract is split: legacy Hadoop `Writable` remains available, while docs push new code toward protobuf conversion. Java serialization also invokes object validation.

## `FileSystem` API Surface In This Chunk

`FileSystem` is the older abstract filesystem facade. It extends `Configured` and implements `Closeable`, `DelegationTokenIssuer`, `PathCapabilities`, and `BulkDeleteSource`.

### Instance Lookup, Caching, And URI Identity

Static factory methods include:

- `get(URI, Configuration, String)` and `newInstance(URI, Configuration, String)` to execute under a named user through UGI.
- `get(Configuration)` and `get(URI, Configuration)` for default or explicit filesystem lookup.
- `newInstance(...)` variants that always return unique, newly initialized instances.
- `getLocal()` and `newInstanceLocal()` for local filesystems.
- `closeAll()` and `closeAllForUGI()` for cached instance cleanup.

The `get(URI, Configuration)` contract documents caching control through `fs.$SCHEME.impl.disable.cache`: when enabled, lookup returns a new initialized instance without caching; otherwise it reuses a matching cached instance or creates and caches a new one. This is a major state-management behavior and affects resource lifetime, authentication context, metrics, and test isolation.

URI APIs include `getDefaultUri`, `setDefaultUri`, `initialize`, `getScheme`, abstract `getUri`, `getCanonicalUri`, `canonicalizeUri`, `getDefaultPort`, `getFSofPath`, `checkPath`, and deprecated `getName`/`getNamed`. The canonicalization contract allows implementations to normalize hostnames and default ports.

### Tokens, Children, And Delegation

`getCanonicalServiceName()` returns the service name used by token caches, or null when no own token is available. The default behavior accounts for child filesystems. `getDelegationToken()`, `getChildFileSystems()`, and `getAdditionalTokenIssuers()` let complex filesystems contribute tokens from embedded or related filesystems.

### File Operations In This Range

The chunk covers:

- Static `create(FileSystem, Path, FsPermission)` and `mkdirs(FileSystem, Path, FsPermission)` helpers that set the exact requested permission rather than applying umask. The HDFS create helper is documented as two RPCs but thread-safe, chosen over mutating umask in configuration.
- `getFileBlockLocations(FileStatus, long, long)` and `getFileBlockLocations(Path, long, long)` with default localhost behavior and detailed HDFS replicated and erasure-coded examples.
- `getServerDefaults()` deprecated in favor of `getServerDefaults(Path)`.
- `resolvePath(Path)` through symlinks or mount points.
- Abstract `open(Path, int)`, convenience `open(Path)`, and PathHandle-based open overloads.
- `getPathHandle(FileStatus, HandleOpt...)` and protected `createPathHandle(...)` for durable serializable references with validation constraints.
- Multiple `create(...)` overloads that eventually lead toward the abstract permission-bearing create method. Defaults include overwriting files unless an overload says otherwise. Overloads add overwrite flag, progress callback, replication, buffer size, block size, and permission.

The final method in this chunk is abstract and is the core implementor hook for creating a file with explicit permission, overwrite behavior, buffer size, replication, block size, and progress reporting.

## Control Flow And Behavior

The XML does not expose method bodies, but the documented API flow is clear:

- Builder APIs collect options first, then perform validation and the filesystem operation in `build()`. This makes failure timing different from immediate APIs: mandatory unsupported options, path existence checks, and I/O failures may occur at build time.
- `FileContext.create(Path, EnumSet<CreateFlag>, CreateOpts...)` validates create flags and options, resolves the target filesystem through `AbstractFileSystem`, applies umask/permissions and server defaults, and returns an `FSDataOutputStream`.
- `FileSystem.create(...)` overloads form a convenience cascade toward the abstract full-parameter create method implemented by concrete filesystems.
- Stream wrappers delegate optional behavior to wrapped streams. Capability checks and `UnsupportedOperationException` are part of normal control flow for optional interfaces.
- Path resolution distinguishes relative, absolute, slash-relative, fully qualified, symlink, and mount-point paths. `FileContext` keeps working-directory behavior as path-prefix logic rather than inode-like process state.
- Access checks are explicitly vulnerable to time-of-check/time-of-use races; docs recommend performing real filesystem actions as the desired `UserGroupInformation` instead of relying on prior access checks.
- Filesystem lookup may return cached or new instances depending on configuration, and closing cached instances invalidates them for future operations.

## State And Persistence Behavior

Important stateful behavior in this range:

- Configuration constants define process and cluster behavior for IPC, security, crypto, credential lookup, metrics, and HTTP endpoints.
- `FileSystem` maintains cached instances keyed by URI/user/config-derived identity unless caching is disabled per scheme.
- `FileContext` stores default filesystem, working directory, UGI, and umask.
- `ContentSummary`, `FileStatus`, and `FileChecksum` are metadata snapshots. Some are writable/serializable for RPC, IPC, or persistence compatibility.
- `FSDataInputStream` and `FSDataOutputStream` hold nested stream state, current positions, optional buffers, IO statistics, and capability-dependent behavior.
- `FSDataOutputStream.close()` may be the point where object-store creation is finalized for create-in-close or conditional overwrite modes.
- `deleteOnExit()` registers paths for JVM shutdown cleanup; `SHUTDOWN_HOOK_PRIORITY` controls FileContext cleanup ordering.
- ACLs, xattrs, snapshots, storage policies, owner/group/permission/time changes, replication, truncate, and create/delete/rename operations mutate persistent filesystem namespace or metadata.
- Path handles are durable serializable references whose validity depends on constraints chosen at creation time and enforcement by the filesystem.

## Dependencies And Integration Points

The chunk sits in `org.apache.hadoop.fs` but connects to many Hadoop Common modules:

- `org.apache.hadoop.conf.Configuration` and `Configured` for filesystem configuration.
- `Path`, `PathHandle`, `BlockLocation`, `FsStatus`, `FsServerDefaults`, `Options`, `StorageType`, `BlockStoragePolicySpi`, `MultipartUploaderBuilder`, and related fs model types.
- `FsPermission`, `FsAction`, `AclEntry`, and `AclStatus` for permissions and ACLs.
- `UserGroupInformation`, `AccessControlException`, `Credentials`, and `Token` for security and delegation token integration.
- `Progressable` for write progress callbacks.
- `ByteBufferPool`, `Writable`, and protobuf helper paths for serialization and buffer management.
- `IOStatistics` and `IOStatisticsSource` for stream/filesystem metrics.
- RPC exception types documented for remote filesystems.
- `StreamCapabilities` and `PathCapabilities` for optional feature discovery.
- Object-store connectors through create-in-close, conditional overwrite, ETag, multipart upload, content type, and mandatory/optional builder options.

Concrete implementors must align these contracts with HDFS, local filesystem, object stores, view/mount filesystems, and any custom scheme registered in configuration.

## Risks And Edge Cases

- The source is a public API XML, not implementation code; implementation details must be confirmed in Java sources before changing behavior.
- Public constants are compatibility-sensitive. Renaming, removing, or changing defaults can break deployed clusters and external connectors.
- Builder overloads for numeric values have historical ambiguity and precision-loss deprecations. New code should use explicit `optLong`, `optDouble`, `mustLong`, and `mustDouble`.
- Mandatory builder options must be rejected when unsupported. Silently ignoring `must()` options can corrupt commit protocols, especially conditional object-store writes.
- Conditional overwrite and ETag create options require atomic check-and-create behavior. Object stores with weak or emulated atomicity need careful documentation and tests.
- `APPEND`, `OVERWRITE`, and `CREATE` flag combinations are easy to misuse; invalid combinations must be rejected consistently across builders and classic APIs.
- `access()` checks are vulnerable to TOCTOU races and may not reflect ACL-rich authorization models unless overridden.
- `rename()` atomicity is filesystem-dependent; callers cannot assume POSIX atomic rename across all Hadoop filesystems.
- `truncate()` may complete asynchronously, signaled by a `false` return value. Callers that append or rewrite immediately must handle this.
- Symlink resolution has many path-form cases. Incorrect handling of final-component versus intermediate symlinks can break compatibility or create security bugs.
- FileSystem caching can leak resources or cross-contaminate tests if not closed or disabled deliberately.
- `FileStatus.equals()` and `hashCode()` are path-based, not full metadata-based. Using `FileStatus` as a cache key can miss metadata changes.
- Legacy `Writable` serialization remains present but deprecated for some types; mixed-version clients may still depend on it.
- Stream capability methods depend on the nested stream honestly implementing optional interfaces. Incorrect capability reporting leads to runtime `UnsupportedOperationException` or data-path failures.

## Test Signals

Useful tests for changes touching APIs in this chunk include:

- API compatibility checks against this jdiff surface, especially method signatures, visibility, exceptions, and deprecation annotations.
- Unit tests for `CreateFlag.validate()` and `validateForAppend()` covering all documented valid and invalid combinations.
- Builder tests proving `opt()` options may be ignored but `must()` unsupported options fail during `build()`.
- Tests for numeric builder overloads that verify long/double values are preserved through `optLong`, `optDouble`, `mustLong`, and `mustDouble`.
- Filesystem contract tests for create overwrite/non-overwrite, create parent behavior, append, recursive parent creation, progress callback tolerance, and checksum options.
- Object-store contract tests for create-in-close, conditional overwrite, ETag matching/mismatching/missing target, stream/path capability advertisement, and atomic close behavior.
- Stream tests for seek, positioned reads, byte-buffer reads, vectored reads, unbuffer, drop-behind, readahead, hflush/hsync, abort, and IO statistics fallback.
- `FileContext` contract tests for working directory qualification, default URI behavior, symlink resolution forms, final symlink operations, dangling symlinks, and mount-point resolution.
- Authorization tests for `access()`, ACL mutation, xattr visibility by user, and permission/owner/group update behavior.
- Snapshot and storage policy tests on filesystems that support those features, plus unsupported-operation behavior on filesystems that do not.
- `FileSystem` cache tests for default cached lookup, per-scheme cache disablement, `newInstance()` uniqueness, `closeAll()`, and `closeAllForUGI()`.
- Serialization tests for `ContentSummary`, `FileStatus`, and `FileChecksum`, including deprecated `Writable` paths where compatibility is still required.
- Block-location tests for local default behavior, HDFS replicated files, and erasure-coded files where logical block groups differ from replicated block layout.
