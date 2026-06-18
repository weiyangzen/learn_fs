# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007165`: lines 1-6052, `Docs/researches/chunks/subset-b-007165_research.md`
- `subset-b-007166`: lines 6053-11998, `Docs/researches/chunks/subset-b-007166_research.md`
- `subset-b-007167`: lines 11999-17994, `Docs/researches/chunks/subset-b-007167_research.md`
- `subset-b-007168`: lines 17995-24293, `Docs/researches/chunks/subset-b-007168_research.md`
- `subset-b-007169`: lines 24294-30693, `Docs/researches/chunks/subset-b-007169_research.md`
- `subset-b-007170`: lines 30694-36789, `Docs/researches/chunks/subset-b-007170_research.md`
- `subset-b-007171`: lines 36790-37921, `Docs/researches/chunks/subset-b-007171_research.md`

## Chunk Research

### subset-b-007165: lines 1-6052

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 1-6052

## Scope and purpose

This chunk is the first 6,052 lines of the generated JDiff XML for the public Hadoop Common 2.8.0 API. It is not executable implementation code; it is a serialized API inventory generated from Javadoc by `IncludePublicAnnotationsJDiffDoclet`. Its purpose is to preserve the public surface of Hadoop Common so compatibility tooling can compare API changes across releases. The file root declares `api` metadata, the generated timestamp, the doclet command line, classpath, sourcepath, API directory, and API name.

Within this chunk, the API coverage starts at core Hadoop exceptions and configuration, moves through crypto key provider abstractions, and then enters the primary filesystem API. The chunk ends inside the `org.apache.hadoop.fs.FileContext` class while documenting the `open(Path)` operation, so later chunks are needed for the rest of `FileContext` and following filesystem classes.

## Packages and important API surfaces

### `org.apache.hadoop`

`HadoopIllegalArgumentException` is a public Hadoop-specific subclass of `IllegalArgumentException`. The Javadoc documents it as a way to distinguish invalid argument failures thrown by Hadoop implementation code from ordinary JDK `IllegalArgumentException`s. It has a single string-message constructor and is referenced later by APIs such as `CreateFlag.validate`.

### `org.apache.hadoop.conf`

`Configurable` is the small configuration contract used across Hadoop components. It exposes `setConf(Configuration)` and `getConf()`.

`Configuration` is the dominant type in this chunk. It is public, implements `Iterable` and Hadoop `Writable`, and models Hadoop's XML-backed layered configuration system. Important API groups include:

- Construction: default, explicit `loadDefaults`, and copy construction.
- Deprecation management: `addDeprecations`, several overloaded `addDeprecation` methods, `isDeprecated`, `setDeprecatedProperties`, `dumpDeprecatedKeys`, and `hasWarnedDeprecation`.
- Resource loading: `addDefaultResource`, `addResource` overloads for classpath name, `URL`, `Path`, `InputStream`, named `InputStream`, and another `Configuration`; `reloadConfiguration` clears resource-derived state so resources are re-read on demand.
- Value lookup and mutation: `get`, `getTrimmed`, `getRaw`, `set`, `unset`, `setIfUnset`, `onlyKeyExists`, `setAllowNullValueProperties`.
- Typed conversions: `getInt`, `getInts`, `setInt`, `getLong`, `getLongBytes`, `setLong`, `getFloat`, `setFloat`, `getDouble`, `setDouble`, `getBoolean`, `setBoolean`, `setBooleanIfUnset`, `setEnum`, `getEnum`, `setTimeDuration`, `getTimeDuration`, `getTimeDurations`, `getPattern`, `setPattern`.
- Collection and prefix access: string collection/string array getters, trimmed variants, `setStrings`, `getPropsWithPrefix`, `getValByRegex`, `iterator`, `size`, `clear`.
- Secrets and credentials: `getPassword`, protected `getPasswordFromCredentialProviders`, and protected `getPasswordFromConfig`.
- Socket and networking helpers: `getSocketAddr`, `setSocketAddr`, `updateConnectAddr`.
- Class loading and plugin selection: `getClassByName`, `getClassByNameOrNull`, `getClasses`, `getClass`, `getInstances`, `setClass`, plus configurable class loader accessors.
- Local resource helpers: `getLocalPath`, `getFile`, `getResource`, `getConfResourceAsInputStream`, `getConfResourceAsReader`.
- Serialization and diagnostics: `getFinalParameters`, protected synchronized `getProps`, `writeXml(OutputStream)`, `writeXml(Writer)`, static `dumpConfiguration`, `toString`, `setQuietMode`, `main`, `readFields`, and `write`.

The `Configuration` Javadoc describes default resources `core-default.xml` and `core-site.xml`, final parameters that prevent later resources from overriding values, variable expansion from configuration, Java system properties, and environment variables with default syntax, and deprecation warning behavior. The document also indicates some lock/concurrency behavior: `addDeprecations` is documented as lockless with an atomic deprecation context swap, while methods such as `addDefaultResource`, `reloadConfiguration`, `unset`, `setIfUnset`, `getPropertySources`, `getProps`, and `setQuietMode` are synchronized in the API metadata.

`Configured` is the standard base class for implementations that carry a `Configuration`. It implements `Configurable`, has no-arg and `Configuration` constructors, and exposes `setConf`/`getConf`.

`ReconfigurationTaskStatus` is a public value/status class for live reconfiguration tasks. It exposes constructor state `(startTime, endTime, status map)`, `hasTask`, `stopped`, start/end time accessors, and a final `getStatus` map accessor. Its semantics distinguish no task, active task, and finished task state.

### `org.apache.hadoop.crypto.key`

`KeyProvider` is an abstract provider API for encryption key material. It is constructed with a `Configuration` and exposes:

- Provider metadata and creation options: `getConf`, static `options(Configuration)`, `isTransient`.
- Key lookup/listing: `getKeyVersion`, `getKeys`, `getKeysMetadata`, `getKeyVersions`, `getCurrentKey`, `getMetadata`.
- Mutating key operations: `createKey` overloads, `deleteKey`, `rollNewVersion` overloads, `flush`, and `close`.
- Utility methods: `generateKey`, `getBaseName`, `buildVersionName`, `findProvider`.
- Password-related capability messages: `needsPassword`, `noPasswordWarning`, `noPasswordError`.
- Defaults: public constants for default cipher name/value and bit length name/value.

Abstract methods and IOException declarations mark the provider boundary: implementations own persistence and remote/local storage behavior, while the API provides common naming and option conventions.

`KeyProviderFactory` is a service-loader-backed factory. It creates providers from URIs and from the configured `KEY_PROVIDER_PATH`, with `createProvider(URI, Configuration)`, static `getProviders(Configuration)`, and static `get(URI, Configuration)`.

### `org.apache.hadoop.fs`

`AbstractFileSystem` is the core implementor-facing filesystem abstraction used by `FileContext`. It is public abstract and stores protected `FileSystem.Statistics`. Important API groups include:

- Construction and lookup: subclass constructor `(URI, supportedScheme, authorityNeeded, defaultPort)`, static `createFileSystem`, static `get`, `checkScheme`, `checkPath`, `getUri`, `getUriDefaultPort`, `getUriPath`, `makeQualified`, and statistics table helpers.
- Namespace and identity: `isValidName`, `getInitialWorkingDirectory`, `getHomeDirectory`, `getCanonicalServiceName`, `equals`, `hashCode`.
- File and directory operations: `create`, abstract `createInternal`, abstract `mkdir`, abstract `delete`, `open` overloads, `truncate`, `setReplication`, `rename`, `renameInternal` overloads.
- Metadata and status: `getServerDefaults`, `resolvePath`, `getFileChecksum`, `getFileStatus`, `getFileLinkStatus`, `getFileBlockLocations`, `getFsStatus` overloads, `listStatusIterator`, `listLocatedStatus`, abstract `listStatus`, and `listCorruptFileBlocks`.
- Permission/security metadata: `setPermission`, `setOwner`, `setTimes`, ACL methods, xattr methods, checksum verification, and storage-policy methods.
- Symlinks and snapshots: `supportsSymlinks`, `createSymlink`, `getLinkTarget`, `createSnapshot`, `renameSnapshot`, `deleteSnapshot`.

The control-flow contract is explicit: applications normally use `FileContext`, which qualifies paths, selects the backing `AbstractFileSystem`, applies umask and option defaults, then delegates to the implementor API. Many public methods in `AbstractFileSystem` specify that paths must be fully qualified or belong to the filesystem. Implementations throw filesystem-specific `IOException` subclasses including `AccessControlException`, `FileAlreadyExistsException`, `ParentNotDirectoryException`, `UnresolvedLinkException`, and `UnsupportedFileSystemException`.

`AvroFSInput` adapts Hadoop `FSDataInputStream` or `FileContext`/`Path` to Avro's `SeekableInput`, with `length`, `read(byte[],off,len)`, `seek`, `tell`, and `close`.

`BlockLocation` is a mutable block metadata value object. It represents hostnames, cached hosts, names such as `IP:xferPort`, topology paths, storage IDs, storage types, offset, length, and corrupt flag. It exposes constructors for older and newer metadata combinations plus getters/setters for all fields.

`BlockStoragePolicySpi` describes block placement policy by name, preferred storage types, creation fallbacks, replication fallbacks, and whether a policy is copy-on-create/inherit-only.

Stream capability interfaces describe optional behavior:

- `ByteBufferReadable.read(ByteBuffer)` reads directly into a `ByteBuffer`, may throw `UnsupportedOperationException`, treats zero-length reads as valid, and leaves buffer positions undefined after exceptions.
- `CanSetDropBehind.setDropBehind(Boolean)` configures cache dropping.
- `CanSetReadahead.setReadahead(Long)` configures stream readahead.
- `CanUnbuffer.unbuffer()` releases buffers and possibly sockets/file descriptors.

`ChecksumException` is an `IOException` with a checksum-error position accessor.

`ChecksumFileSystem` is an abstract `FilterFileSystem` that wraps a raw filesystem and maintains sidecar checksum files client-side. It exposes checksum file naming/length helpers, checksum verification and write toggles, raw filesystem access, checksum-aware open/append/create/truncate/delete/rename/list/copy/local-output operations, and `reportChecksumFailure`. State is split between raw files and generated checksum files, so rename/delete/list/copy behavior has to preserve or hide checksum artifacts correctly.

`CommonConfigurationKeysPublic` is a public constants holder for documented common configuration keys and defaults. This chunk includes constants for native library availability, network topology scripts/mapping, default FS and local FS settings, disk usage intervals, trash behavior, protected directories, IO buffers and sequence/map file settings, caller context limits, IPC client/server tuning, RPC socket factories, socks server, hash type, group mapping and cache controls, security authentication/authorization/auth-to-local, DNS settings, SSL, Kerberos relogin, HTTP policy, RPC protection, SASL properties, crypto codec/cipher/buffer settings, impersonation provider, key provider path, KMS encrypted key cache tuning, secure random, shell warnings and safe-delete limit, and sensitive configuration key patterns. A few fields are deprecated because the setting moved to MapReduce (`IO_SORT_MB_KEY`, `IO_SORT_FACTOR_KEY`).

`ContentSummary` extends `QuotaUsage` and implements `Writable`. It is a summary value for content size/count state with constructors marked in documentation as superseded by `ContentSummary.Builder`. Accessors expose length, directory count, file count, snapshot length/counts, snapshot space consumed, equality/hash, and multiple `toString` overloads for quota display, human-readable formatting, storage type quotas, and snapshot inclusion/exclusion. Static header helpers return display field names.

`CreateFlag` is a public enum represented in JDiff as a final `Enum`. It validates create/append/overwrite semantics with `validate(EnumSet)`, `validate(path,pathExists,EnumSet)`, and `validateForAppend`. Valid combinations include `CREATE`, `APPEND`, `OVERWRITE`, `CREATE|APPEND`, `CREATE|OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`; invalid combinations include `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`.

`FileAlreadyExistsException` is an `IOException` used when an operation targets an existing file and overwrite is not configured.

`FileChecksum` is an abstract `Writable` for file checksum identity. Implementations provide algorithm name, length, bytes, optional checksum options, equality by algorithm/value, and hash code.

`FileContext` begins in this chunk. It is the application-facing API over `AbstractFileSystem`. The visible portion covers:

- Filesystem resolution: protected `getFSofPath(Path)`.
- Factory methods: `getFileContext` overloads for explicit `AbstractFileSystem`, default configuration, local filesystem, URI, URI plus `Configuration`, and `Configuration`; `getLocalFSFileContext` overloads.
- Context state: working directory setter/getter, UGI accessor, home directory, umask getter/setter.
- Path operations: `resolvePath`, `makeQualified`.
- Mutating operations visible before the chunk ends: `create`, `mkdir`, `delete`, and the beginning of `open(Path)`.

`FileContext` documents distributed semantics that differ from Unix process state: working directory is a path prefixing mechanism, not an inode-level process cwd. It also documents RPC exception surfaces and path validation runtime failures.

## Control flow and state behavior

The XML itself has no runtime control flow beyond nested JDiff structure: `api` contains `package`, each `package` contains `class`/`interface` entries, and each type contains constructors, fields, methods, exceptions, params, docs, and implemented interfaces. The semantic control flow is encoded in API contracts:

- Configuration values flow from default resources, added resources, programmatic setters, deprecated aliases, variable expansion, and typed getters. Resource state is lazy/reloadable; `reloadConfiguration` clears resource-derived state while preserving programmatic overlay behavior.
- Deprecated configuration keys are global/static API state. The Javadoc calls out an atomic swap pattern for adding deprecations and warns that adding deprecations after resources are loaded can throw `UnsupportedOperationException`.
- Password lookup first attempts credential providers, then conditionally falls back to clear-text configuration.
- Filesystem calls flow from user-facing `FileContext` to a default or path-derived `AbstractFileSystem`, which validates scheme/authority/path and delegates to concrete filesystem implementations.
- `ChecksumFileSystem` acts as a wrapper that maps data-file operations to raw filesystem operations plus checksum sidecar management.
- Key provider operations flow through `KeyProviderFactory` URI/service discovery into concrete `KeyProvider` implementations, which own persistence of key metadata and material.

State and persistence are mostly external to this XML but visible in contracts. Configuration persists via XML resources and `Writable` serialization. Filesystems persist namespace, block, ACL, xattr, snapshot, and checksum state in the backing storage. Key providers persist or expose key material depending on `isTransient`. `BlockLocation`, `ContentSummary`, and `FileChecksum` are serializable/value-style metadata views over persisted filesystem state.

## Dependencies and integration points

The generation command line records dependencies on Hadoop annotations, Guava, commons libraries, Jetty/Jersey/Jackson, Avro, protobuf, Hadoop auth, Curator/ZooKeeper, HTrace, Netty, and other Hadoop Common build artifacts. The API entries in this chunk integrate with:

- Hadoop `Configuration`, `Writable`, `Path`, `FSDataInputStream`, `FSDataOutputStream`, `FileSystem.Statistics`, `RemoteIterator`, `FsServerDefaults`, `Options`, `FsPermission`, `AclStatus`, `StorageType`, `Progressable`, and security exceptions/UGI.
- Java platform types: `URI`, `URL`, `InputStream`, `Reader`, `Writer`, `DataInput`, `DataOutput`, `Properties`, `Map`, `List`, `Set`, `Iterator`, `EnumSet`, `Pattern`, `TimeUnit`, `InetSocketAddress`, `ClassLoader`, and checked IO/class-loading exceptions.
- Avro through `org.apache.avro.file.SeekableInput`.
- Credential provider and KMS integration through `Configuration.getPassword`, `KeyProvider`, `KeyProviderFactory`, `HADOOP_SECURITY_KEY_PROVIDER_PATH`, and KMS cache constants.
- Hadoop RPC/security through documented RPC exceptions, ACL/xattr APIs, Kerberos relogin, authentication/authorization, auth-to-local, SASL resolver, impersonation provider, and group mapping cache constants.

## Risks and compatibility concerns

- Because this is a JDiff public API file, any malformed XML, missing type entry, incorrect signature, or incorrect deprecation marker can break compatibility reports or hide API regressions.
- `Configuration` has subtle global state around default resources and deprecation mappings. Order of resource loading, final parameters, alias propagation, variable expansion, and synchronized versus lockless update paths are all compatibility-sensitive.
- `Configuration.addResource(InputStream)` caches stream contents and explicitly warns about memory use.
- Password fallback to clear-text configuration is security-sensitive; callers expecting credential-provider-only behavior must understand fallback policy.
- Filesystem APIs expose many default methods that may or may not be supported by concrete filesystems. Optional features such as symlinks, ACLs, xattrs, snapshots, storage policies, readahead, drop-behind, unbuffer, and ByteBuffer reads require careful `UnsupportedOperationException`/`IOException` handling.
- `AbstractFileSystem` path qualification and scheme/authority checks are central to preventing operations against the wrong filesystem.
- `ChecksumFileSystem` must keep data and checksum sidecars consistent across create, append, truncate, rename, delete, local copy, ACL, permission, owner, and listing operations.
- `CreateFlag` validation defines user-visible create/append/overwrite behavior; invalid combinations must keep throwing `HadoopIllegalArgumentException`.
- `CommonConfigurationKeysPublic` includes deprecated MapReduce-moved constants and security-sensitive keys. Removing or renaming constants would be a binary/source compatibility issue for downstream users even if internal code uses `CommonConfigurationKeys`.
- This chunk cuts off mid-`FileContext`; any final whole-file report must merge later chunks before drawing complete conclusions about `FileContext`.

## Test signals

Useful validation signals for this chunk are primarily documentation/API compatibility checks rather than unit tests:

- XML well-formedness against the JDiff `api.xsd` shape and successful parsing of nested `package`, `class`, `interface`, `method`, `constructor`, `field`, `param`, `exception`, and `doc` elements.
- JDiff comparison against adjacent Hadoop Common releases should detect intended additions/removals/deprecations in the types listed above.
- Configuration tests should cover default resource order, final parameter enforcement, reload behavior, deprecation aliases, variable/environment expansion, typed conversion failures, `Writable` round trips, XML output, property sources, class loading, socket address handling, credential provider fallback, and null-value test mode.
- Key provider tests should cover factory URI discovery, configured provider path resolution, transient versus persistent providers, key creation/deletion/rolling, metadata/version naming, generated key bit length/cipher defaults, flush/close, and password warning/error behavior.
- Filesystem contract tests should cover path qualification, scheme/authority rejection, create/open/mkdir/delete/rename/truncate semantics, permission/owner/times, symlink behavior, ACL/xattr/snapshot/storage-policy optional support, checksum sidecar correctness, block location metadata, content summary formatting, and `CreateFlag` validation.
- Stream capability tests should verify `ByteBufferReadable` buffer position/limit behavior, zero-length reads, EOF `-1`, and optional unsupported paths for drop-behind, readahead, and unbuffer.

### subset-b-007166: lines 6053-11998

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 6053-11998

## Purpose

This chunk is generated JDiff API metadata for a major part of Hadoop Common 2.8.0's `org.apache.hadoop.fs` public contract. It starts inside the `FileContext` API, then covers `FileStatus`, the core abstract `FileSystem` base class, local file utility helpers, `FilterFileSystem`, filesystem constants, data input/output stream wrappers, filesystem error and input-stream abstractions, and `FsServerDefaults`.

The XML is not implementation code. Its value is the public compatibility surface: type names, inheritance, implemented interfaces, constructors, method signatures, checked exceptions, field names, deprecation state, and Javadocs describing expected semantics.

## API Inventory

### `org.apache.hadoop.fs.FileContext` tail

- The chunk begins in `FileContext` operations for opening files, truncating, changing replication, rename with `Options.Rename[]`, permission/owner/time mutation, file checksums, checksum verification, status and link status, symlink target lookup, filesystem status, symlink creation, directory/status iteration, corrupt block listing, located status listing, delete-on-exit registration, path resolution, and statistics.
- ACL APIs include `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, and `getAclStatus`, all using `AclEntry` lists or `AclStatus`.
- Extended attribute APIs include `setXAttr` with and without `EnumSet<XAttrSetFlag>`, `getXAttr`, `getXAttrs` for all or selected names, `listXAttrs`, and `removeXAttr`.
- Snapshot APIs include default and named `createSnapshot`, `renameSnapshot`, and `deleteSnapshot`.
- Storage policy APIs include `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, and `getAllStoragePolicies`.
- Static/default fields exposed in this chunk include `LOG`, `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`.

### `FileStatus`

- `FileStatus` implements `Writable` and `Comparable` and represents client-side file metadata.
- Constructors cover an empty writable instance, basic length/directory/replication/block-size/modification-time/path status, status with access time/permission/owner/group, status with symlink path, and a copy constructor that can throw `IOException`.
- Accessors expose file length, file/directory/symlink classification, block size, replication, modification and access timestamps, `FsPermission`, encryption status, owner, group, path, and symlink target.
- Mutators allow path, permission, owner, group, and symlink assignment.
- Persistence and identity methods include `write(DataOutput)`, `readFields(DataInput)`, `compareTo`, `equals`, `hashCode`, and `toString`.
- `isDir()` is retained as a deprecated old-style classifier in favor of explicit `isFile()` and `isDirectory()`.

### `FileSystem`

- `FileSystem` is the abstract base class for Hadoop filesystem implementations. It extends `Configured` and implements `Closeable`.
- Construction and lookup APIs include static `get` overloads, `newInstance` overloads, local filesystem lookup, default URI get/set helpers, filesystem class lookup, per-UGI close, and global close of cached filesystems.
- URI and identity APIs include `initialize`, `getScheme`, abstract `getUri`, `getCanonicalUri`, `canonicalizeUri`, `getDefaultPort`, `getFSofPath`, `getCanonicalServiceName`, deprecated `getName`, deprecated `getNamed`, `makeQualified`, and `checkPath`.
- Security integration is visible through `addDelegationTokens(String renewer, Credentials credentials)`, which obtains tokens not already present in credentials.
- File creation/opening APIs include many `create` overloads with overwrite, buffer size, replication, block size, progress callback, checksum options, permissions, and create flags; `primitiveCreate`; `primitiveMkdir`; `createNonRecursive`; `createNewFile`; `append`; and `concat`.
- Metadata and namespace operations include `open`, `truncate`, `setReplication`, old boolean `rename`, exception-rich `rename` with `Options.Rename[]`, `delete`, `deleteOnExit`, `cancelDeleteOnExit`, `processDeleteOnExit`, `exists`, `isDirectory`, `isFile`, deprecated `getLength`, `getContentSummary`, and `getQuotaUsage`.
- Listing/globbing APIs include `listStatus` overloads, `listCorruptFileBlocks`, `globStatus` overloads with optional `PathFilter`, `listLocatedStatus` overloads, `listStatusIterator`, and recursive `listFiles`.
- Working-directory and local-copy APIs include `getHomeDirectory`, `setWorkingDirectory`, `getWorkingDirectory`, `getInitialWorkingDirectory`, `mkdirs`, copy/move from local, copy/move to local, `startLocalOutput`, and `completeLocalOutput`.
- Capacity/default APIs include `getUsed`, path-scoped `getUsed`, deprecated `getBlockSize`, `getDefaultBlockSize`, path-scoped default block size, default replication, path-scoped default replication, and `getServerDefaults`.
- Symlink and checksum APIs include `createSymlink`, `getFileLinkStatus`, `supportsSymlinks`, `getLinkTarget`, `resolveLink`, `getFileChecksum` overloads, `setVerifyChecksum`, and `setWriteChecksum`.
- Administrative metadata APIs include `getStatus`, `setPermission`, `setOwner`, `setTimes`, snapshots, ACLs, xattrs, storage policies, trash roots, statistics, symlink global enablement, per-instance `StorageStatistics`, and global storage statistics.
- Fields include configuration keys/defaults (`FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`), `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, and per-filesystem `statistics`.

### `FileUtil`

- `FileUtil` is a static utility collection for file-processing tasks across Hadoop filesystems and local disk.
- Conversion helpers map `FileStatus[]` to `Path[]`.
- Deletion helpers include `fullyDelete`, `fullyDeleteContents`, and recursive delete variants with symlink-aware behavior.
- Copy helpers move data between `FileSystem` instances, from local disk to a filesystem, from a filesystem to local disk, and merge source files through `copyMerge`.
- Local path helpers include `makeShellPath` overloads, `readLink`, disk usage calculation through `getDU`, archive extraction through `unZip` and `unTar`, and temporary file creation.
- Permission and ownership helpers wrap platform-sensitive operations: `symLink`, `chmod`, recursive `chmod`, `setOwner`, readable/writable/executable setters and testers, and `setPermission`.
- Miscellaneous helpers include atomic-ish `replaceFile`, safe wrappers around `File.listFiles()` and `File.list()`, classpath-jar generation through `createJarWithClassPath`, and filesystem URI comparison through `compareFs`.
- `SYMLINK_NO_PRIVILEGE` is exposed as a return/status code for symlink creation failures caused by missing privilege.

### `FilterFileSystem`

- `FilterFileSystem` extends `FileSystem` and wraps another `FileSystem` held in the protected `fs` field. `swapScheme` is also exposed.
- Constructors support an empty instance and a wrapper around an existing raw filesystem.
- `getRawFileSystem()` exposes the wrapped target.
- Most methods delegate to the wrapped filesystem while preserving the `FileSystem` public contract: initialization, URI/canonical URI, path qualification/checking, block locations, path resolution, open/create/append/concat, listing, delete, rename, truncate, working directory, copy helpers, capacity/defaults, status, access checks, symlinks, checksums, configuration, close, ownership/times/permissions, primitive create/mkdir, child filesystems, snapshots, ACLs, xattrs, storage policies, and trash roots.

### Constants and stream/base types

- `FsConstants` exposes public filesystem constants: `LOCAL_FS_URI`, `FTP_SCHEME`, `MAX_PATH_LINKS`, `VIEWFS_URI`, and `VIEWFS_SCHEME`.
- `FSDataInputStream` extends `DataInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, and `CanUnbuffer`. It wraps an input stream with Hadoop seek/positioned-read APIs, byte-buffer reads, enhanced buffer-pool reads, file descriptor access, readahead/drop-behind controls, buffer release, unbuffering, and `toString`.
- `FSDataOutputStream` extends `DataOutputStream` and implements `Syncable` and `CanSetDropBehind`. Constructors can bind a raw output stream, filesystem statistics, and an initial start position. Methods expose current position, close, legacy `sync`, `hflush`, `hsync`, and drop-behind control.
- `FSError` extends `Error` for unexpected filesystem errors presumed to reflect native disk failures.
- `FSInputStream` is an abstract `InputStream` implementing `Seekable` and `PositionedReadable`. Subclasses must implement `seek`, `getPos`, and `seekToNewSource`; the base class supplies positioned `read`, argument validation, and `readFully` overloads.
- `FsServerDefaults` implements `Writable` and carries server-provided defaults: block size, bytes per checksum, write packet size, replication, file buffer size, encrypted data transfer flag, trash interval, and checksum type.

## Control Flow and State

The file and namespace APIs follow Hadoop's layered filesystem control flow. `FileContext` is a path-oriented client facade that resolves links, locates the target filesystem, and exposes exception-rich operations. `FileSystem` is the implementation base class behind those calls, with static factory/cache methods selecting concrete filesystems by URI scheme and authority, then instance methods executing file creation, reads, writes, listing, metadata mutation, and admin operations.

Create/write flows generally return `FSDataOutputStream`; read flows return `FSDataInputStream`. `FSDataInputStream` delegates seeks and positioned reads to `FSInputStream`-style capabilities where available, while enhanced byte-buffer APIs add buffer-pool lifecycle through `read(ByteBufferPool, int, EnumSet)` and `releaseBuffer`.

`FilterFileSystem` inserts a delegation layer. It preserves the `FileSystem` API while routing operations to an underlying raw filesystem, which is how Hadoop can wrap implementations for checksumming, filtering, scheme adaptation, or compatibility behavior.

Delete-on-exit state is process-local. `FileSystem.deleteOnExit` marks paths for deletion when the filesystem closes, while `FileContext.deleteOnExit` marks paths for JVM shutdown. The chunk also exposes shutdown hook priority fields for both classes.

Statistics are global and per-filesystem. `FileContext` and `FileSystem` include methods to get, clear, print, and enumerate `FileSystem.Statistics`; `FileSystem` additionally exposes `StorageStatistics` and global storage statistics.

## Persistence and Serialization

`FileStatus` and `FsServerDefaults` implement `Writable`, so the empty constructors and `write`/`readFields` APIs are part of Hadoop's binary serialization contract. `FileStatus` persists metadata such as path, length, directory/file/link state, replication, block size, times, permissions, owner, group, symlink target, and encryption status. `FsServerDefaults` persists client defaults learned from a server.

Streams and filesystem instances manage runtime state rather than durable persistence. `FSDataInputStream` tracks/read delegates current input position, buffering, readahead/drop-behind preferences, and enhanced byte buffers. `FSDataOutputStream` tracks output position and sync/flush behavior. `FileSystem` instances hold configuration, URI identity, working directory state, cached instance lifecycle, delete-on-exit registrations, and statistics.

## Dependencies and Integration Points

- Core dependencies are `Path`, `FileStatus`, `BlockLocation`, `LocatedFileStatus`, `RemoteIterator`, `ContentSummary`, `QuotaUsage`, `FsStatus`, `FsServerDefaults`, `FileChecksum`, `BlockStoragePolicySpi`, and `Options` types.
- Security and identity integration appears through `UserGroupInformation` close behavior, delegation tokens, `Credentials`, `AccessControlException`, owners/groups, and permission objects.
- ACL and xattr integration uses `org.apache.hadoop.fs.permission.AclEntry`, `AclStatus`, `FsAction`, `FsPermission`, `XAttrSetFlag`, and Java collections/maps.
- Stream integration uses Java IO (`InputStream`, `OutputStream`, `DataInputStream`, `DataOutputStream`, `FileDescriptor`, `DataInput`, `DataOutput`) plus Hadoop capability interfaces such as `Seekable`, `PositionedReadable`, `Syncable`, `ByteBufferReadable`, `HasEnhancedByteBufferAccess`, and `CanUnbuffer`.
- `FileUtil` integrates local `java.io.File`, shell/path conversion, archive extraction, local permissions, symlink support, and classpath manifest generation.
- Checksumming/defaults integrate with `org.apache.hadoop.util.DataChecksum.Type`, checksum options, checksum verification/write flags, and server default negotiation.

## Risks and Edge Cases

- This is generated API metadata. It should be treated as public-contract evidence, not proof of implementation behavior. Compatibility consumers should compare it with compiled classes or source when discrepancies matter.
- Rename and truncate semantics vary by filesystem. The docs explicitly warn that rename atomicity depends on the implementation, while truncate can return `false` when background block-length recovery is still in progress.
- Symlink APIs are conditional. Some filesystems do not support symlinks, global symlink enablement exists, `MAX_PATH_LINKS` constrains traversal, and `getFileStatus` versus `getFileLinkStatus` differ in whether the final symlink is followed.
- Delete-on-exit registrations are process state and can leak cleanup work or delete unexpected paths if reused `FileSystem`/`FileContext` instances cross ownership boundaries.
- `FileStatus` equality, ordering, and serialization are compatibility-sensitive because clients often cache or compare statuses by path.
- ACL, xattr, snapshot, and storage-policy methods are optional or backend-dependent. Callers must expect `UnsupportedOperationException`, `IOException`, `AccessControlException`, and missing-file errors depending on filesystem implementation.
- `FilterFileSystem` wrappers can accidentally expose the raw filesystem or mis-handle URI scheme/canonicalization if `swapScheme` and delegation are inconsistent.
- `FileUtil` performs local destructive operations and shell/permission work. Recursive delete, archive extraction, symlink creation, and chmod/chown behavior are especially platform-sensitive.
- Enhanced byte-buffer reads require callers to release buffers correctly; failing to do so can leak pooled or off-heap buffers.

## Test Signals

- API compatibility tests should verify every public class/interface, constructor, method, field, implemented interface, return type, parameter type, checked exception, visibility, and deprecation state represented in this chunk.
- `FileSystem` tests should cover URI-based factory lookup and caching, default URI configuration, canonical URI/default port behavior, path qualification/checking, local filesystem lookup, `newInstance` cache bypass, `closeAll`, and `closeAllForUGI`.
- File operation tests should cover open/create overloads, non-recursive create, append optional behavior, concat, create-new-file existence races, replication changes, rename overwrite rules, truncate synchronous/asynchronous return values, recursive delete, delete-on-exit/cancel/process behavior, and content/quota summaries.
- Listing tests should cover files versus directories, path filters, glob patterns, corrupt-file iterators, located-status iterators, lazy `RemoteIterator` behavior, and recursive `listFiles`.
- Metadata tests should cover permissions, owner/group, times, checksums with length-limited checksum calls, checksum verify/write flags, ACL replacement/incremental removal, xattr set/get/list/remove, snapshots, storage policies, trash roots, and symlink resolution/link-status distinctions.
- Serialization tests should round-trip `FileStatus` and `FsServerDefaults`, including symlink and non-symlink constructors, permissions, owner/group, access/modification times, replication, block size, encryption flag, and checksum type.
- Stream tests should cover seek/getPos, positioned read not changing stream position, `readFully` EOF behavior, `seekToNewSource`, byte-buffer reads, enhanced buffer release, file descriptor access, readahead/drop-behind unsupported cases, output `getPos`, `hflush`, `hsync`, legacy `sync`, close semantics, and statistics updates.
- `FilterFileSystem` tests should assert delegation to the wrapped filesystem for representative operations and verify URI/scheme/path behavior remains consistent.
- `FileUtil` tests should cover recursive deletion with symlinks, copy/copyMerge across local and Hadoop filesystems, shell path conversion, archive extraction, symlink/chmod/chown return behavior, permission setters/testers, temp-file creation, replacement behavior, safe list wrappers on null-returning directories, classpath jar manifest generation, and filesystem comparison.

### subset-b-007167: lines 11999-17994

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 11999-17994

## Purpose

This chunk is generated JDiff API metadata for Hadoop Common 2.8.0. It records public compatibility contracts rather than implementation bodies. The covered region starts at `org.apache.hadoop.fs.FsStatus`, spans filesystem path/status/local-filesystem/trash/xattr APIs, FTP and viewfs filesystem adapters, permission and ACL types, high-availability service protocols, protocol-buffer bridge markers, and the beginning of `org.apache.hadoop.io` Writable utilities through the first `IOUtils.copyBytes` overloads.

The file is important as public API evidence: it captures class/interface names, inheritance, implemented interfaces, constructors, method signatures, parameter and return types, checked exceptions, public/protected fields, deprecation status, and Javadoc contracts. Consumers should use this chunk to reason about source and binary compatibility for these Hadoop Common packages, not as proof of private implementation details.

## Scope Notes

- The source slice begins in the `org.apache.hadoop.fs` package and ends inside `org.apache.hadoop.io.IOUtils`; `IOUtils` is only partially covered here.
- Several package entries are empty or marker-only in this slice: `org.apache.hadoop.fs.crypto`, `org.apache.hadoop.fs.sftp`, `org.apache.hadoop.fs.shell.find`, `org.apache.hadoop.ha.protocolPB` except protocol interfaces, and `org.apache.hadoop.http.lib`.
- The XML references nested helper types such as builders, mount points, and option classes, but this chunk often records only the outer public method surface that uses those types.

## API Inventory

### `org.apache.hadoop.fs` status, path, and filters

- `FsStatus` represents filesystem capacity, used bytes, and remaining bytes. It implements `Writable`, has a `(long capacity, long used, long remaining)` constructor, exposes `getCapacity()`, `getUsed()`, `getRemaining()`, and serializes through `write(DataOutput)` and `readFields(DataInput)`.
- `GlobalStorageStatistics` is represented as a public final enum-style singleton surface for global `StorageStatistics` registration. Its synchronized methods `get(String)`, `put(String, StorageStatisticsProvider)`, `reset()`, and `iterator()` provide a process-wide registry for filesystem/storage statistics. `put` requires provider-created statistics to be non-null and name-matched.
- `GlobFilter` implements `PathFilter` for POSIX glob patterns with brace expansion. Constructors accept a glob string alone or a glob string plus a user `PathFilter`, and may throw `IOException` for invalid patterns. `hasPattern()` exposes whether the expression contains glob syntax, and `accept(Path)` combines glob matching with the optional user filter.
- `InvalidPathException` extends `HadoopIllegalArgumentException` for invalid path strings or filesystem-specific path rejections. It accepts either just a path or a path plus reason.
- `LocatedFileStatus` extends `FileStatus` with `BlockLocation[]`. Constructors wrap an existing `FileStatus` plus locations or fully specify length, directory flag, replication, block size, modification/access times, permission, owner, group, symlink, path, and locations. Equality, comparison, and hashing are path-name based, matching `FileStatus` semantics.
- `Options` is a final holder for filesystem operation option types referenced elsewhere, such as create and checksum options.
- `ParentNotDirectoryException` is an `IOException` signaling that an expected parent path is not a directory.
- `Path` is Hadoop's URI-backed filesystem path type. Constructors combine parent/child strings or `Path` instances, create from raw strings, `URI`, or `(scheme, authority, path)` components. Static helpers strip scheme/authority, merge paths while preserving the first path's scheme/authority, and detect Windows absolute paths. Instance methods expose URI conversion, filesystem lookup via `getFileSystem(Configuration)`, absolute/root/name/parent/depth checks, suffixing, string/equals/hash/compare behavior, and a deprecated `makeQualified(FileSystem)` overload. Public constants include `/` separator values, `"."`, and `WINDOWS`.
- `PathFilter` is the single-method predicate interface `accept(Path)`.
- `PositionedReadable` defines positional read methods that do not change stream offset: `read(position, buffer, offset, length)`, `readFully(position, buffer, offset, length)`, and `readFully(position, buffer)`. The contract requires thread-safe operations but warns that not all filesystems satisfy this, and some expose intermediate seek position via `Seekable.getPos()`.
- `ReadOption` is an enum of filesystem read options.
- `Seekable` defines `seek(long)` and `getPos()` for streams with a mutable current offset; seeking past EOF is prohibited by contract.
- `StorageStatistics` is an abstract statistics base with a name, optional scheme, iterators over long statistics, lookup by key, `isTracked(String)`, and `reset()`. Values are not guaranteed to be a point-in-time snapshot.
- `StorageType` is an enum surface for storage media. It exposes `isTransient()`, `supportTypeQuota()`, `isMovable()`, list helpers for all/movable/quota-supporting types, parse helpers from int or string, and public `DEFAULT`/`EMPTY_ARRAY` constants.
- `Syncable` defines filesystem flush semantics. Deprecated `sync()` is replaced by `hflush()`. `hflush()` makes client-buffered data visible to new readers, while `hsync()` is closer to POSIX fsync and pushes data toward disk devices.

### Local, trash, xattr, and FTP filesystem APIs

- `LocalFileSystem` extends `ChecksumFileSystem` and wraps a raw local filesystem with checksum behavior. It initializes from URI/configuration, returns scheme `file`, exposes the raw filesystem, converts `Path` to `File`, copies to/from local paths, reports checksum failures by moving files to a bad-file directory on the same device, and supports symlink creation/link status/link target lookup.
- `RawLocalFileSystem` extends `FileSystem` for direct local-file access. Its surface includes static `useStatIfAvailable()`, path-to-file conversion, URI/initialization, `open`, `append`, multiple `create` and `createNonRecursive` variants, protected output-stream factories with optional `FsPermission`, `rename`, Windows empty destination directory handling, `truncate`, recursive/non-recursive `delete`, `listStatus`, one-directory mkdir helpers, `mkdirs`, working/home directory management, local-output staging, `close`, status queries, `setOwner`, `setPermission`, `setTimes`, symlink support, link status, and link target resolution.
- `Trash` is a `Configured` facade for trash behavior. It can be constructed from `Configuration` or a specific `FileSystem` plus configuration. Static `moveToAppropriateTrash` resolves symlinks/mount points to use the trash in the actual target volume. Instance methods include `isEnabled()`, `moveToTrash(Path)`, checkpoint creation, checkpoint expunge, current-trash directory lookup, emptier creation, and deletion-interval access.
- `TrashPolicy` is the pluggable trash-policy base class. It is `Configured`, can be initialized with configuration, filesystem, and home directory, has a static `getInstance` factory, and defines abstract/overridable operations for enablement, moving to trash, checkpointing, expunging, emptier creation, current trash directory, and delete interval.
- `UnsupportedFileSystemException` is an `IOException` used when no implementation exists for a requested scheme or filesystem contract.
- `XAttrCodec` is an enum for extended-attribute value encoding/decoding. Static helpers decode values from strings and encode byte arrays. It is the string/binary boundary for shell/API xattr values.
- `XAttrSetFlag` is an enum for xattr mutation modes. `validate(String, boolean xattrExists, EnumSet<XAttrSetFlag>)` checks create/replace constraints against current existence.
- `FTPException` wraps FTP-related failures in a runtime exception.
- `FTPFileSystem` extends `FileSystem` using Apache Commons Net. It reports scheme `ftp`, has a default port hook, initializes from URI/configuration, and implements `open`, `create`, unsupported `append`, `delete`, `getUri`, `listStatus`, `getFileStatus`, `mkdirs`, `rename`, working/home directory methods, and configuration-key constants for user, password, host, host port, buffer size, block size, and same-directory rename limitations. Its `create` Javadoc warns that an acquired stream must be closed before other API calls, or later calls may block.

### Permissions and ACLs

- `org.apache.hadoop.fs.permission.AccessControlException` extends `IOException` but is deprecated in favor of `org.apache.hadoop.security.AccessControlException`. Constructors support default remote-exception unwrapping, message, and cause.
- `AclEntry` is an immutable ACL element with type, optional name, permission action, and scope. It exposes getters, stable and normal string forms, equality/hash behavior, `parseAclSpec(String, boolean)`, `parseAclEntry(String, boolean)`, and `aclSpecToString(List)`. Stable string output is intended for shell output and serialization compatibility.
- `AclEntryScope` is an enum for access/default scope.
- `AclEntryType` is an enum for ACL entry type and exposes normal plus stable string representations.
- `AclStatus` is an immutable ACL status object with owner, group, sticky bit, ordered ACL entries, associated `FsPermission`, equality/hash/string behavior, and effective-permission calculation. The two-argument `getEffectivePermission(AclEntry, FsPermission)` exists for old NameNode compatibility and may throw `IllegalArgumentException` when the old-NameNode path lacks the required permission argument.
- `FsAction` is the enum of read/write/execute combinations. It exposes implication, `and`, `or`, `not`, string-to-action lookup, and each enum value's symbolic permission string.
- `FsPermission` implements `Writable` for file/directory permission bits. Constructors accept user/group/other `FsAction`s with optional sticky bit, a short mode, copy source, or octal/symbolic string. It supports immutable creation, action getters, `fromShort`, `write`, `readFields`, static `read(DataInput)`, `toShort`, `toExtendedShort` for ACL/encryption bits, equality/hash/string behavior, `applyUMask`, `getUMask(Configuration)`, sticky/ACL/encrypted-bit getters, `setUMask`, default directory/file/cache-pool permissions, and `valueOf` for Unix symbolic strings. Public constants expose permission-string length and umask keys/defaults.

### ViewFS client-side mount table

- `NotInMountpointException` extends `UnsupportedOperationException` for operations attempted outside a mount point.
- `ViewFileSystem` extends `FileSystem` and implements a client-side mount table equivalent to `ViewFs` for the classic `FileSystem` API. Its surface mirrors filesystem operations and delegates them through mount links: URI/scheme, initialize, working/home directories, status, `open`, `create`, `append`, `rename`, `delete`, directory creation, list operations, checksum and block location queries, symlink support, ACL/xattr operations, delegation tokens, child filesystem and mount-point introspection, checksum verification/write toggles, and snapshot operations.
- `ViewFs` extends `AbstractFileSystem` and implements the same mount-table concept for the `AbstractFileSystem` API. It resolves paths through in-memory mount table configuration, delegates creation/open/delete/rename/list/status/block/checksum/access/symlink/owner/permission/replication/time/ACL/xattr/snapshot/storage-policy operations, exposes mount points and delegation tokens, and validates names. Its Javadoc documents `viewfs:///` usage and `fs.viewfs.mounttable.*` configuration keys for mount links. Merge mounts are documented as not implemented.

### High availability APIs

- `BadFencingConfigurationException` is an `IOException` for invalid configured fencing methods or arguments.
- `FailoverFailedException` is a checked exception for failed service failover.
- `FenceMethod` is the operator-extensible fencing interface. `checkArgs(String)` validates configured method arguments during startup, and `tryFence(HAServiceTarget, String)` attempts to prevent the target node from making progress. Implementations may also implement `Configurable` for framework configuration injection.
- `HAServiceProtocol` is the versioned HA management protocol. It defines `monitorHealth()`, `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(StateChangeRequestInfo)`, and `getServiceStatus()`, with checked exceptions for health, service-transition, access-control, and IO failures. The protocol is meant for HA frameworks that monitor and fail over services.
- `HAServiceProtocolHelper` provides static helper wrappers around active/standby transitions, converting protocol exceptions into the expected service-failure behavior.
- `HAServiceTarget` represents a target HA service. It exposes service, health-monitor, ZKFC, and fencing addresses, fencing parameters, proxy construction with timeout/configuration, auto-failover support, ZKFC support, transition-target checks, and a delegation-token service. The target object is the integration point between HA controllers, RPC proxies, and fencing.
- `HealthCheckFailedException` extends `IOException` for failed health checks.
- `ServiceFailedException` extends `IOException` for failed HA state transitions.
- `org.apache.hadoop.ha.protocolPB.HAServiceProtocolPB` and `ZKFCProtocolPB` are protobuf bridge interfaces for the HA and ZK failover-controller RPC protocols.

### `org.apache.hadoop.io` Writable and stream utilities

- `AbstractMapWritable` is the base for map-like Writables that carry per-instance class-id maps rather than global static maps. It implements `Writable` and `Configurable`, supports class registration, class/id lookup, synchronized copy from another writable, configuration access, and serialization. The documented class-id range is 1-127, limiting each map instance to 127 distinct classes.
- `ArrayFile` extends `MapFile` as a dense file-backed mapping from integer indexes to values.
- `ArrayPrimitiveWritable` wraps primitive arrays in an optimized Writable format without per-element object creation. It can be empty for deserialization, constructed with a known component type, or wrap an existing primitive array without copying. It exposes component-type inspection, value get/set, and read/write serialization.
- `ArrayWritable` wraps arrays of a single `Writable` value class. Constructors accept the value class, value class plus values, or strings. It exposes value-class lookup, string conversion, object-array conversion, value get/set, and read/write serialization. The docs recommend typed subclasses for reducer inputs.
- `BinaryComparable` is an abstract byte-backed `Comparable`. Subclasses provide `getLength()` and `getBytes()`. It supplies bytewise `compareTo`, comparison against a raw byte range, equality, and hash code using `WritableComparator` byte helpers.
- `BloomMapFile` adds Bloom-filter-assisted lookups to `MapFile` and exposes static `delete(FileSystem, String)` plus `BLOOM_FILE_NAME` and `HASH_COUNT` constants. It is optimized for sparse MapFiles.
- `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, and `IntWritable` are primitive `WritableComparable` wrappers. Each provides default/value constructors, `set`, `get`, `readFields`, `write`, equality/hash, `compareTo`, and `toString` contracts for its primitive type.
- `ByteBufferPool` abstracts pooled `ByteBuffer` allocation and release. `getBuffer(boolean direct, int length)` returns a buffer with at least the minimum requested capacity, and `putBuffer(ByteBuffer)` returns buffers to the pool.
- `BytesWritable` extends `BinaryComparable` and implements `WritableComparable` for resizable byte sequences. It distinguishes logical length from backing capacity, can copy or expose backing bytes, has deprecated `get()`/`getSize()` aliases in favor of `getBytes()`/`getLength()`, supports size/capacity mutation, setting from another `BytesWritable` or byte range, serialization, bytewise equality/hash, and hex-pair string output.
- `org.apache.hadoop.io.Closeable` is deprecated in favor of `java.io.Closeable` and simply extends it.
- `CompressedWritable` is an abstract `Writable` base for lazily inflated compressed data. Its final `readFields` and `write` methods delegate to subclass `readFieldsCompressed` and `writeCompressed`; field-accessing subclass methods must call `ensureInflated()`.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`. Static `constructOutputStream(DataOutput)` returns the input if it is already an `OutputStream`, otherwise wraps it. It implements single-byte and byte-array `write` variants.
- `DefaultStringifier<T>` implements `Stringifier<T>` using Hadoop serialization plus Base64 strings. It can stringify/restore individual objects, close its serializer/deserializer resources, and store/load individual objects or arrays in `Configuration` keys. Array storage rejects empty arrays via `IndexOutOfBoundsException`.
- `ElasticByteBufferPool` is a synchronized `ByteBufferPool` that allocates as needed and caches released direct or heap buffers. It returns the smallest cached buffer with sufficient capacity and intentionally does not cap cache size.
- `EnumSetWritable<E>` wraps `EnumSet` in a `Writable` and `Configurable` collection. It supports null/empty sets only when an explicit element type is provided, exposes iterator/size/add/set/get, element-type lookup, serialization, equality/hash/string, and configuration access.
- `GenericWritable` wraps one of a fixed set of `Writable` classes supplied by subclass `getTypes()`. It stores a compact type index rather than a class name per record, making it more efficient than `ObjectWritable` when value types are known. It is `Configurable` and passes configuration to wrapped configurable instances before deserialization.
- `IOUtils` begins in this chunk. Covered overloads include `copyBytes(InputStream, OutputStream, int, boolean)`, `copyBytes(InputStream, OutputStream, int)`, and `copyBytes(InputStream, OutputStream, Configuration)` plus the start of the configuration/close overload. The documented behavior copies stream contents, optionally closes streams in `finally`, and uses configuration-derived buffer sizing for config-based overloads.

## Control Flow and Behavior

Most behavior in this chunk is expressed as API-level contracts. Filesystem flows are path-oriented: `Path` normalizes and resolves URI-like names, then `getFileSystem(Configuration)` or filesystem-specific methods route operations to the owning `FileSystem`. `LocalFileSystem` layers checksum handling over a raw local filesystem, while `RawLocalFileSystem` maps Hadoop `Path` objects to `java.io.File` and then performs direct local operations. `ViewFileSystem` and `ViewFs` add a client-side resolution stage: incoming paths are matched against mount-table entries, rewritten to target filesystems, and delegated.

Trash operations add an indirection before delete. `Trash.moveToAppropriateTrash` resolves symlinks or mount points so the moved item lands in the trash for the actual backing volume. `TrashPolicy` defines the control hooks for enablement, move, checkpoint, and expunge operations; concrete policy behavior is outside this chunk.

Permission and ACL APIs convert between structured objects and stable string or numeric forms. `AclEntry.parseAclSpec` and `parseAclEntry` parse shell-compatible ACL text, while `toStringStable` supports compatibility-sensitive output. `FsPermission` converts among action triples, shorts, extended shorts, symbolic strings, and configuration-backed umask values. Effective ACL permissions may depend on whether the client is talking to an old NameNode.

HA control flow is protocol-driven. HA frameworks call `monitorHealth()` repeatedly, request transitions to active or standby through `HAServiceProtocol`, and use `HAServiceTarget` to obtain RPC proxies and fencing details. `FenceMethod` implementations are checked at startup and attempted in configured order by the fencing machinery referenced by the docs.

Writable control flow is serialization-centric. Primitive writables, byte-array writables, arrays, enum sets, generic wrappers, map-writable metadata, compressed writables, and stringifiers all define how objects move through `DataInput`/`DataOutput` or configuration strings. `GenericWritable` and `AbstractMapWritable` optimize wire formats by replacing repeated class names with compact ids.

## State and Persistence

- `FsStatus`, `FsPermission`, and most `org.apache.hadoop.io` wrappers persist state through Hadoop `Writable` methods.
- `GlobalStorageStatistics` is synchronized process-global registry state; `reset()` clears all registered statistics data.
- `StorageStatistics` implementations hold mutable metric state, but iterator results are not guaranteed to be a coherent snapshot.
- `Path` is value-like URI state with equality, comparison, and hash behavior tied to normalized path representation.
- `RawLocalFileSystem` and `LocalFileSystem` maintain runtime configuration, working directory, and filesystem handles; their durable state is the host filesystem.
- `Trash` and `TrashPolicy` persist deleted items and checkpoints into filesystem trash directories, but the XML only exposes the management contract.
- `AclEntry` and `AclStatus` are immutable value objects; `FsPermission` can be serialized and can also encode ACL/encryption marker bits in extended short form.
- `ViewFileSystem`/`ViewFs` keep an in-memory mount table initialized from configuration. The mount table itself is configuration-backed rather than persisted by the objects.
- HA target/protocol objects carry runtime endpoint and fencing state; actual HA state is owned by remote services.
- `CompressedWritable` stores compressed bytes until `ensureInflated()` is needed, then materializes subclass fields.
- `DefaultStringifier` persists serialized objects into `Configuration` string values using Base64 encoding.
- `ElasticByteBufferPool` maintains an unbounded in-process cache of returned buffers.

## Dependencies and Integration Points

- Filesystem classes integrate with `FileSystem`, `AbstractFileSystem`, `FileContext`-style APIs, `Configuration`, `Path`, `FileStatus`, `BlockLocation`, `FsServerDefaults`, `FSDataInputStream`, `FSDataOutputStream`, ACL/xattr types, snapshot/storage-policy APIs, and Java `URI`/`File`.
- Local filesystem permission changes depend on OS commands such as `chmod` and `chown`, and symlink behavior depends on platform support.
- FTP support integrates with Apache Commons Net and remote FTP server semantics. Its blocking warning around open create streams is an important integration contract.
- `ViewFileSystem` and `ViewFs` depend on mount-table configuration keys under `fs.viewfs.mounttable.*`, target filesystem implementations, delegation-token collection from child filesystems, and Hadoop's symlink and snapshot contracts.
- Permission APIs integrate with HDFS NameNode ACL behavior, shell command parsing/output, `Configuration` umask keys, and `DataInput`/`DataOutput` serialization.
- HA APIs integrate with Hadoop IPC/protobuf protocol bridges, security access checks, health monitors, ZK failover controllers, fencing implementations, and delegation-token service names.
- `org.apache.hadoop.io` classes integrate with Hadoop serialization, `WritableComparator`, `MapFile`, Bloom filter utilities, `Configuration`, `SerializationFactory`, Java primitive arrays, `ByteBuffer`, and Java stream/data interfaces.

## Risks and Edge Cases

- Because this is generated API XML, it can lag or diverge from implementation source if generation inputs are stale. Treat it as compatibility metadata for the generated artifact.
- `PositionedReadable` requires thread safety but explicitly warns that some filesystem implementations do not honor it; callers like HBase depend on the stronger contract.
- `Path` string handling crosses URI normalization and Windows path parsing. Scheme/authority stripping, drive-letter handling, and relative path merging are common compatibility hazards.
- `RawLocalFileSystem.rename` and `handleEmptyDstDirectoryOnWindows` encode platform-specific rename behavior; tests must cover Windows and non-Windows semantics separately.
- `RawLocalFileSystem.delete` throws when a directory is non-empty and recursive is false; callers relying only on boolean return can miss this checked-exception path.
- `LocalFileSystem.reportChecksumFailure` moves bad files aside on the same device. Failures in that path can hide corruption handling or accidentally reuse suspect storage.
- `Trash.moveToAppropriateTrash` must resolve symlinks and mount points correctly, or deletion may move data into the wrong filesystem's trash.
- `FTPFileSystem.create` can block other API calls until the stream is closed, making resource management and exception cleanup critical.
- `AclStatus.getEffectivePermission(AclEntry, FsPermission)` has old-NameNode compatibility behavior that can throw if `permArg` is missing.
- `FsPermission.toExtendedShort()` may encode values outside normal permission ranges; consumers assuming only `00000`-`01777` can drop ACL/encryption bits.
- `GlobalStorageStatistics` and `ElasticByteBufferPool` are synchronized global or shared state surfaces; they need cleanup/reset in tests to avoid cross-test leakage.
- `ElasticByteBufferPool` intentionally lacks a maximum cache size, so workloads with varied large buffers can retain substantial memory.
- `AbstractMapWritable` has a fixed 1-127 class-id range per map instance. Serializing more distinct Writable classes than that is a hard limit.
- `ArrayPrimitiveWritable` wraps arrays without copying, so later caller mutation can change serialized or observed state.
- `BytesWritable.getBytes()` exposes backing capacity beyond logical length; callers must respect `getLength()` or use `copyBytes()`.
- `CompressedWritable` requires subclasses to call `ensureInflated()` before field access; missing calls can observe stale/uninitialized field state.
- `GenericWritable.getTypes()` must be stable and include only `Writable` classes. Reordering or changing the type list breaks serialized type indexes.
- `IOUtils.copyBytes` close behavior varies by overload and boolean flag; accidental stream closure is a common integration risk.

## Test Signals

- API compatibility checks should assert every class/interface, method signature, constructor, field, checked exception, inheritance relationship, implemented interface, and deprecation marker present in this XML slice.
- `Path` tests should cover constructor normalization, parent/child resolution, scheme/authority preservation and removal, Windows absolute path detection, root/name/parent/depth behavior, suffixing, equality/hash/compare ordering, URI conversion, and filesystem resolution.
- Local filesystem tests should cover checksum-wrapped vs raw behavior, create/append/open/truncate/delete/list/status, permission and owner setting, symlink create/status/target behavior, working-directory resolution, local-output staging, checksum failure quarantine, and platform-specific rename behavior.
- Trash tests should cover disabled trash, already-in-trash cases, move to appropriate backing volume through symlinks or viewfs mount points, checkpoint creation, expunge, emptier scheduling, and policy factory selection.
- XAttr tests should cover encode/decode formats, create-vs-replace validation, missing/existing xattr combinations, and invalid flag sets.
- FTP tests should cover URI initialization, credential/host/port configuration, stream-close requirements after create, unsupported append behavior, same-directory rename limitations, directory creation/listing/status, and remote IO exception propagation.
- Permission and ACL tests should cover stable string round trips, parsing with and without permissions, named and unnamed entries, access/default scopes, effective permissions with old and new NameNode behavior, symbolic and octal `FsPermission` parsing, umask application, extended ACL/encryption bits, Writable round trips, and deprecated access-control exception compatibility.
- ViewFS tests should cover mount-table initialization from `fs.viewfs.mounttable.*`, path resolution, root and mount-point listing, delegation to child filesystems, unsupported paths raising `NotInMountpointException`, symlink handling, ACL/xattr/snapshot/storage-policy delegation, child filesystem enumeration, and delegation token aggregation.
- HA tests should cover fencing argument validation, successful/failed/indeterminate fencing, health monitor exception paths, active/standby idempotence, service status reporting, access-control failures, proxy construction with timeouts, ZKFC address/proxy behavior, auto-failover flags, and protobuf bridge compatibility.
- Writable tests should cover serialization round trips for primitive wrappers, `FsStatus`, `FsPermission`, arrays, primitive arrays, enum sets including null/empty cases with explicit element type, `BytesWritable` length/capacity semantics, `BinaryComparable` ordering, `AbstractMapWritable` class-id limits and copy behavior, `GenericWritable` type-index stability and configuration injection, `CompressedWritable` lazy inflation, `DefaultStringifier` store/load for objects and arrays, `DataOutputOutputStream` wrapping behavior, and `ElasticByteBufferPool` direct/heap reuse ordering.
- `IOUtils` tests for this covered portion should distinguish close and non-close overloads, configuration-derived buffer sizes, exception propagation, and guaranteed close in `finally` when requested.

### subset-b-007168: lines 17995-24293

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 17995-24293

## Purpose

This chunk is part of the generated JDiff API description for Hadoop Common 2.8.0. It is public API metadata rather than executable Java implementation. The useful research signal is the compatibility contract: packages, classes, interfaces, inheritance, implemented interfaces, constructors, methods, fields, visibility, checked exceptions, deprecation text, and embedded Javadocs.

The range starts inside the tail of `org.apache.hadoop.io.IOUtils`, covers most of the core `org.apache.hadoop.io` serialization and container APIs, covers the public compression codec framework in `org.apache.hadoop.io.compress`, covers TFile API metadata, serialization provider markers, legacy log/metrics surfaces, and ends inside the beginning of `org.apache.hadoop.metrics.spi.MetricsRecordImpl`.

## Important APIs and Types

### `org.apache.hadoop.io`

- The chunk begins with `IOUtils` stream helpers: `copyBytes` overloads, `wrappedReadForCompressedData`, `readFully`, `skipFully`, cleanup/close helpers that ignore cleanup-time `IOException`, socket close helpers, `writeFully` for `WritableByteChannel` and positional `FileChannel`, and `listDirectory`. These APIs centralize defensive I/O loops, short-write handling, and cleanup behavior.
- `LongWritable`, `ShortWritable`, `VIntWritable`, and `VLongWritable` are mutable primitive wrappers implementing `WritableComparable`. They expose value constructors, `set`, `get`, `readFields`, `write`, equality, hash, comparison, and string conversion.
- `MapFile` is a file-backed sorted map stored as a directory containing `data` and `index` files. Public constants name those files. Static helpers support rename, delete, command-line entry, and `fix(...)`, which can rebuild a corrupt index by scanning `data` and optionally dry-running.
- `SetFile` is the set variant of `MapFile`.
- `MapWritable` and `SortedMapWritable` extend `AbstractMapWritable` and implement Java `Map`/`SortedMap` with `Writable` keys and values. They expose copy constructors, normal map operations, and `Writable` serialization methods. `SortedMapWritable` additionally exposes comparator, first/last key, and head/sub/tail map views over `WritableComparable` keys.
- `MD5Hash` is a `WritableComparable` wrapper for 16-byte MD5 digests. It provides string/byte constructors, static `read`, `digest` overloads, `getDigester`, `getDigest`, `set`, `setDigest`, `halfDigest`, `quarterDigest`, comparison, equality, hash, and string conversion. `MD5_LEN` is the public digest-length constant.
- `MultipleIOException` aggregates multiple `IOException` instances and can convert a list into either a single `IOException`, a wrapper, or null depending on list contents.
- `NullWritable` is a singleton zero-byte `WritableComparable`, used where a key or value position exists in the API but no payload is needed.
- `ObjectWritable` is a polymorphic `Writable` and `Configurable` wrapper. It serializes class identity plus instances for `Writable`, `String`, primitives, and arrays. Its `allowCompactArrays` option is documented for RPC/internal use, while persisted or inter-cluster files should avoid compact arrays for compatibility.
- `RawComparator` extends `Comparator` with byte-range comparison so sort and shuffle paths can compare serialized records without full object creation.
- `SequenceFile` is the binary key/value file container API. This chunk exposes default compression-type accessors, a modern `createWriter(Configuration, Writer.Option...)`, many deprecated writer overloads, FileSystem/FileContext/raw-output writer creation, compression codec selection, metadata/progress/block-size/replication/create-parent options, and `SYNC_INTERVAL`. The Javadoc documents the common header and three storage formats: uncompressed, record-compressed values, and block-compressed key/value blocks.
- `Stringifier<T>` is a closeable conversion interface for serializing objects to strings and restoring them from strings.
- `Text` is Hadoop's mutable UTF-8 byte string. It exposes constructors from string, `Text`, and byte arrays; raw byte access with separate length; byte-position search; code-point access; set/append/clear; bounded read/write methods; static skip, encode/decode, UTF-8 validation, read/write string helpers, `bytesToCodePoint`, `utf8Length`, and `DEFAULT_MAX_LEN`.
- `TwoDArrayWritable` persists rectangular or ragged two-dimensional arrays of a configured `Writable` value class.
- `VersionedWritable` prefixes writable payloads with a version byte and validates versions through `VersionMismatchException`.
- `Writable` defines the core Hadoop binary serialization contract: `write(DataOutput)` and `readFields(DataInput)`. The docs require `readFields` to fully overwrite object state, not merge with previous state.
- `WritableComparable` combines `Writable` and `Comparable` for values that can be serialized and sorted.
- `WritableComparator` is the comparator registry and raw-comparison base. It can construct keys, register custom comparators with `define`, compare objects or serialized bytes, and parse primitive/vint values directly from byte arrays.
- `WritableFactories` and `WritableFactory` allow custom construction of non-public or special `Writable` classes, including configuration-aware instantiation.
- `WritableUtils` provides compressed byte/string helpers, string arrays, writable cloning/copying, variable-length integer/long encoding and decoding, range-checked vint reads, enum serialization by name, full skipping, byte-array conversion, and safe bounded string reads.

### `org.apache.hadoop.io.compress`

- `BlockCompressorStream` and `BlockDecompressorStream` adapt block-oriented compressors to Hadoop compression streams. Blocks include uncompressed length followed by one or more length-prefixed compressed chunks; decompression can reset state.
- `BZip2Codec` implements `Configurable` and `SplittableCompressionCodec`. It can use native bzip2 or pure Java depending on configuration. The docs warn that pure-Java mode does not implement `Compressor`/`Decompressor` methods that accept those objects, and splittable reads force pure-Java mode.
- `CodecPool` is the process-level pool for reusable `Compressor` and `Decompressor` instances, with get/return calls and leased compressor/decompressor counts.
- `CompressionCodec` defines the common codec contract: create compression/decompression streams with or without pooled codec state, expose compressor/decompressor classes, create state instances, and provide a default filename extension.
- `CompressionCodecFactory` discovers configured codecs, maps file extensions and class names to codecs, removes codec suffixes from filenames, exposes codec-class configuration helpers, logs through `LOG`, and has a command-line entry point.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream wrappers with protected underlying stream fields. Input streams expose `resetState`, position, seek, and alternate-source seeking. Output streams expose `finish` and `resetState` in addition to flush/close/write behavior.
- `Compressor` and `Decompressor` model zlib-style state machines. They manage input buffers, dictionaries, byte counters, finish/finished state, reset/end, reinitialization, remaining input, and decompression output loops.
- `CompressorStream` and `DecompressorStream` are concrete stream adapters that own a compressor/decompressor, byte buffer, closed/eof flags, and read/write/skip/available/close/reset behavior.
- `DefaultCodec` is the default configurable codec and also implements `DirectDecompressionCodec`.
- `DirectDecompressionCodec` and `DirectDecompressor` define decompression into direct `ByteBuffer` instances.
- `GzipCodec` extends `DefaultCodec` with gzip-specific stream and codec-state creation.
- `SplitCompressionInputStream` and `SplittableCompressionCodec` define split-aware compressed reads. Codecs may adjust requested compressed start/end offsets to block or algorithm boundaries, and `READ_MODE` controls whether position is reported continuously or at block boundaries.

### `org.apache.hadoop.io.file.tfile`

- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are checked exceptions for named TFile metadata blocks.
- `RawComparable` identifies a comparable byte range through `buffer`, `offset`, and `size`; an external `RawComparator` supplies the comparison semantics.
- `TFile` is a byte-oriented key/value container with type-less keys and values, 64 KB key limit, block compression, named metadata blocks, sorted or unsorted keys, and seeking by key or file offset. Public constants identify compression algorithms (`gz`, `lzo`, `none`) and comparator naming (`memcmp`, Java class prefix). `makeComparator`, `getSupportedCompressionAlgorithms`, and `main` are exposed.
- `Utils` contains TFile-local helpers for vint/vlong and string serialization plus binary-search style `lowerBound`/`upperBound` operations over lists and arrays using raw comparators.

### Serialization, Logging, and Legacy Metrics Packages

- `org.apache.hadoop.io.serializer` includes `JavaSerialization`, `JavaSerializationComparator`, and `WritableSerialization`. These are provider classes for Hadoop's serialization framework, including comparator support for Java-serialized values and the configured writable serializer.
- `org.apache.hadoop.io.serializer.avro` includes marker/interface and provider classes for Avro reflection and specific-record serialization. `AvroSerialization` exposes `AVRO_SCHEMA_KEY`; `AvroReflectSerialization` exposes `AVRO_REFLECT_PACKAGES`.
- `org.apache.hadoop.ipc.protocolPB` and `org.apache.hadoop.log` appear as package markers in this range.
- `org.apache.hadoop.log.metrics.EventCounter` is a Log4J `AppenderSkeleton` exposing `append`, `close`, and `requiresLayout`, used to count logging events for metrics.
- `org.apache.hadoop.metrics` package documentation describes the original Hadoop metrics API: `MetricsContext`, `MetricsRecord`, `Updater`, `ContextFactory`, and factory attributes such as `period`, `servers`, and class names. It is deprecated in favor of `metrics2`.
- `org.apache.hadoop.metrics.ganglia.GangliaContext` is a deprecated `AbstractMetricsContext` implementation that emits metrics to Ganglia servers over UDP. It exposes `close`, `emitMetric`, metadata lookup helpers for units/slope/tmax/dmax, XDR encoding helpers, and protected state for buffer, offset, server list, and datagram socket.
- `org.apache.hadoop.metrics.spi.AbstractMetricsContext` is the deprecated SPI base for the old metrics system. It manages context initialization, factory attributes, monitoring start/stop/close, record creation, updater registration, all-record retrieval, abstract `emitRecord`, optional `flush`, internal table `update`/`remove`, and period parsing. `CompositeContext` extends it as a deprecated composite implementation.
- The chunk ends inside `MetricsRecordImpl`, after its constructor, `getRecordName`, tag setters for string/integer types, `removeTag`, and the beginning of metric setters. The rest of `MetricsRecordImpl` is outside this mapped range.

## Control Flow

The `Writable` family defines the core serialization flow: callers allocate or reuse mutable objects, invoke `readFields` to fully replace prior state from a `DataInput`, and invoke `write` to emit a stable binary representation. Primitive writables write fixed or variable-length encodings. Map writables must serialize both class metadata and entry payloads so readers can reconstruct heterogeneous `Writable` key/value types.

`ObjectWritable` adds a polymorphic serialization flow. The writer records the declared class and payload, with special handling for primitive types, strings, arrays, and writable implementations. The reader loads classes through the provided `Configuration`, constructs instances through normal reflection or `WritableFactories`, then reads the payload. The compact-array flag changes wire format and is therefore reserved for compatibility-bounded contexts.

`SequenceFile` writer creation flows through either the modern options API or legacy overloads. The selected file system/context, output path/stream, key and value classes, compression type, codec, metadata, buffering, replication, block size, create flags, and progress callbacks determine the writer. At persistence time every file has a header with version, key/value classes, compression flags, codec, metadata, and sync marker. Records are then written uncompressed, record-compressed, or block-compressed; readers use the header and sync markers to bridge all supported formats.

`MapFile` builds on `SequenceFile` semantics by requiring sorted key insertion into a `data` file and a smaller in-memory `index` file. The `fix` path scans existing data and can rebuild the index, with dry-run mode to report without mutation.

`Text` control flow is byte-oriented rather than Java `String` oriented. Search and `charAt` operate on UTF-8 byte positions to avoid string allocation. Decode/encode can either replace malformed input or throw `CharacterCodingException`. Bounded read/write methods and `readStringSafely` provide defensive length checks before allocating.

Compression control flow is state-machine driven. A codec creates streams and optional reusable compressor/decompressor state. Callers feed input only when `needsInput()` is true, keep buffers stable until the codec has consumed them, call `finish()` to drain output, and call `reset()`/`end()` when reusing or releasing native state. Block streams add block-length framing, while split-aware codecs may adjust requested start/end offsets before returning a `SplitCompressionInputStream`.

Legacy metrics control flow starts with a `ContextFactory` creating and initializing an `AbstractMetricsContext`. Monitoring starts a timer, registered `Updater` callbacks update `MetricsRecordImpl` instances, records update or remove rows in the context's internal metric table, and each period calls subclass `emitRecord` followed by optional `flush`. Ganglia output converts metric records into XDR-like UDP datagrams for configured servers.

## State and Persistence Behavior

Most `org.apache.hadoop.io` classes in this chunk are mutable value objects. Their serialized form is compatibility-critical because Hadoop RPC, SequenceFile, MapFile, TFile, and many persisted metadata paths depend on stable read/write behavior. Reusing instances is normal, so `readFields` implementations must clear old state before reading new state.

`Text` stores an internal byte array plus a logical length. `getBytes()` can expose capacity beyond the valid range; `copyBytes()` returns an exact-length copy. `clear()` does not release the backing array, so retained buffers can preserve memory until reset with an empty byte array or smaller value.

`MapFile` persists data under a directory with `data` and `index` children. The index is read fully into memory, so key size and index interval affect memory footprint. `fix` can mutate persistent index state unless `dryrun` is true.

`SequenceFile` persists format, compression, class names, metadata, sync markers, and record blocks. Changing headers, sync intervals, compression semantics, or variable-length integer formats would break readers and sort/shuffle tooling.

`WritableComparator`, `WritableFactories`, and `CodecPool` expose process-wide registries/pools. These are not durable persistence, but they are global JVM state and can affect subsequent comparisons, object construction, or codec reuse.

Compression stream objects keep transient state: underlying stream, buffers, compressor/decompressor instances, eof/closed flags, adjusted split boundaries, and byte counters. Native compressors and decompressors require explicit return to `CodecPool` or `end()` to avoid leaks.

TFile persists byte keys/values, compressed blocks, metadata blocks, comparator identity, and compression algorithm names. Its public constants and comparator-name parsing are part of the on-disk interpretation contract.

The old metrics SPI stores transient in-process metric records, updater lists, periods, monitoring state, and output buffers. Ganglia integration sends UDP datagrams but does not persist local durable state.

## Dependencies and Integration Points

- Core I/O APIs depend on Java `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `Closeable`, `Socket`, `ByteBuffer`, `WritableByteChannel`, `FileChannel`, `File`, `FilenameFilter`, `MessageDigest`, and Hadoop `Configuration`.
- File container APIs integrate with `org.apache.hadoop.fs.FileSystem`, `FileContext`, `Path`, `FSDataOutputStream`, `Options.CreateOpts`, `Progressable`, compression codecs, raw comparators, and Hadoop sort/shuffle code paths.
- Serialization APIs integrate with `Configured`, Hadoop `Serialization`, Java serialization, writable serialization, Avro reflection/specific serialization, and class loading through `Configuration`.
- Compression APIs integrate with native codec libraries, pure-Java fallbacks, Hadoop codec discovery configuration, `CodecPool`, split input processing for MapReduce, direct `ByteBuffer` decompression, and filesystem filename extension matching.
- TFile integrates with raw byte comparators, codec names, compression algorithms, metadata blocks, binary search utilities, and command-line dump tooling.
- Legacy metrics APIs integrate with Apache Commons Logging, Log4J, Ganglia UDP servers, `ContextFactory` attributes, `MetricsContext`, `MetricsRecord`, `Updater`, old SPI `OutputRecord`, and the newer `metrics2` package through deprecation guidance.

## Risks and Edge Cases

- This is generated JDiff XML, not implementation. It should be treated as public-contract evidence. Any mismatch with Java source or bytecode would affect API compatibility analysis.
- The chunk starts inside `IOUtils` and ends inside `MetricsRecordImpl`; adjacent chunks are required before making final whole-class conclusions for those two classes.
- Silent cleanup helpers intentionally ignore `IOException`; using them outside exception cleanup can hide primary failures or resource leaks.
- `ObjectWritable` class-name based deserialization can fail if classes are absent, renamed, not public, or not registered with a factory. Compact array encoding is explicitly unsafe for long-lived persisted files shared with older clusters.
- `Writable` object reuse makes stale state a common bug if `readFields` does not fully overwrite collections, buffers, or optional fields.
- Raw comparators must agree with object comparators. Divergence can corrupt sort order in MapReduce shuffle, SequenceFile sorting, MapFile indexes, or TFile binary searches.
- `Text` uses byte offsets, not Java character indexes. Invalid UTF-8, trailing bytes, `getBytes()` capacity exposure, and `clear()` retaining memory are common correctness and memory-footprint traps.
- `SequenceFile` and `MapFile` depend on stable binary encodings, class names, sync markers, and sorted-key assumptions. Appending out-of-order keys or changing compression metadata can make files unreadable or indexes incorrect.
- `MapFile` index files are loaded entirely into memory; high-cardinality files with large keys or small index intervals can create memory pressure.
- Compression state machines require careful buffer ownership. The docs warn that input buffers must remain unmodified until `needsInput()` says more input is needed. Violating that can corrupt native and non-native decompression/compression.
- Codec pooling can leak native resources or corrupt future operations if compressors/decompressors are returned while still in use, not reset, or mixed with incompatible configurations.
- BZip2 behavior depends on native versus pure-Java mode. Splittability is only available in pure-Java mode, while compressor/decompressor object methods may throw `UnsupportedOperationException` in that same mode.
- Split compression offsets are advisory. Codecs may change start/end to align with block boundaries, so callers must use adjusted offsets for progress and split accounting.
- TFile keys are limited to 64 KB while values are practically storage-limited. Comparator names, compression algorithm availability, and metadata block uniqueness need validation.
- Old metrics and Ganglia APIs are deprecated. They still represent compatibility surface, but new integration should use `metrics2`. UDP Ganglia emission can drop data, and timer/updater concurrency can expose stale or partially updated records if implementations are careless.

## Test Signals

- API compatibility tests should verify all public/protected signatures, inheritance, implemented interfaces, checked exceptions, fields, constants, and deprecation text for this chunk against the Hadoop Common 2.8.0 baseline.
- Writable tests should round-trip `LongWritable`, `ShortWritable`, `VIntWritable`, `VLongWritable`, `NullWritable`, `Text`, `MapWritable`, `SortedMapWritable`, `TwoDArrayWritable`, `VersionedWritable`, `MD5Hash`, and `ObjectWritable`, including reused-instance `readFields` cases.
- Variable-length encoding tests should cover `WritableUtils.writeVInt/writeVLong/readVInt/readVLong`, sign and length decoding, boundary values, range-checked reads, malformed lengths, and `readStringSafely` maximum-size rejection.
- Comparator tests should compare object-level and raw-byte ordering for primitive writables, `Text`, MD5 hashes, TFile raw comparables, and custom comparators registered through `WritableComparator.define`.
- `Text` tests should cover UTF-8 validation, malformed encode/decode with replace true/false, byte-position `find`, `charAt` on valid and trailing bytes, max-length reads/writes, `copyBytes` versus `getBytes`, `clear` memory behavior, and `bytesToCodePoint` buffer-position mutation.
- `ObjectWritable` tests should cover primitives, strings, arrays, `Writable` classes, nulls, configured class loading, non-public writable factory registration, compact-array on/off compatibility, and missing-class failures.
- SequenceFile tests should create and read uncompressed, record-compressed, and block-compressed files; assert header metadata, sync markers, key/value class handling, deprecated and options-based writer paths, raw output writers, FileContext create flags, and codec selection.
- MapFile/SetFile tests should cover sorted insertion assumptions, index loading, rename/delete, corrupt index repair with dry-run and mutation paths, and behavior with large keys or dense indexes.
- IOUtils tests should cover full reads/skips across short-returning streams, EOF failures, short channel writes, positional file-channel writes, compressed-data read error wrapping, cleanup ignoring exceptions, and directory-listing IO failures.
- Compression tests should cover codec discovery by extension/name/class, codec suffix removal, stream finish/reset/close, compressor/decompressor state transitions, dictionary paths, concatenated streams through `finished` plus `getRemaining`, `CodecPool` lease counts, direct decompression, and resource release.
- BZip2 tests should explicitly cover native and pure-Java modes, unsupported compressor/decompressor methods in pure-Java mode, split input streams, adjusted start/end offsets, and continuous versus block read modes.
- TFile tests should cover supported compression names, comparator construction for `memcmp` and Java-class comparators, metadata block duplicate/missing exceptions, sorted and unsorted reads, key-size limits, offset/key seeks, and lower/upper bound helpers.
- Serialization-provider tests should verify Java, writable, and Avro serialization selection through configuration, including Avro schema and reflect-package keys.
- Metrics tests should cover old metrics context initialization, period parsing, updater registration/removal, record creation constraints, update/remove row matching by tags, start/stop/close idempotence, Ganglia units/slope/tmax/dmax configuration, UDP datagram encoding, and `EventCounter` appender counting.

## Cross-Chunk Notes

The preceding chunk is needed for the beginning of `IOUtils` and possibly package-level context before line 17995. The following chunk is needed for the remainder of `MetricsRecordImpl`, including the rest of metric mutation, update/remove behavior, and any subsequent SPI classes.

This document is intentionally chunk-scoped. The final per-file research document should merge this with the other chunks for `Apache_Hadoop_Common_2.8.0.xml` before drawing conclusions about the complete JDiff baseline.

### subset-b-007169: lines 24294-30693

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 24294-30693

## Scope

This chunk is a generated JDiff API-description slice for Hadoop Common 2.8.0. It starts inside the tail of `org.apache.hadoop.metrics.spi.MetricsRecordImpl`, covers the end of the deprecated `org.apache.hadoop.metrics.spi` package, the public `org.apache.hadoop.metrics2` API core, selected metrics2 annotations, filters, library helpers, sinks, and utilities, then covers `org.apache.hadoop.net` DNS/rack-mapping and socket-factory APIs. It also includes most of the deprecated Hadoop Record I/O runtime and compiler API surface under `org.apache.hadoop.record`, `org.apache.hadoop.record.compiler`, `org.apache.hadoop.record.compiler.ant`, and the beginning of `org.apache.hadoop.record.compiler.generated.Rcc`.

Because the source is JDiff XML rather than executable Java source, control-flow and persistence notes are inferred from documented API contracts, inheritance, synchronization flags, exception signatures, and package-level documentation. The final merge should treat this as API compatibility metadata for the 2.8.0 release, not as implementation code.

## Purpose

The covered metrics APIs document Hadoop's transition from the deprecated original `org.apache.hadoop.metrics` SPI to `org.apache.hadoop.metrics2`. The old SPI entries describe buffered metric values, no-op contexts, output records, and parsing helpers that remain public for compatibility but are explicitly replaced by metrics2. The metrics2 entries define the live source/collector/record/builder/sink/plugin model used by Hadoop daemons to expose counters, gauges, tags, rates, quantiles, and JMX-backed management endpoints.

The network section documents the pluggable hostname/IP-to-rack mapping layer used by Hadoop placement and scheduling logic. It defines the `DNSToSwitchMapping` contract, caching wrapper behavior, script-based mapping configuration, topology diagnostics, and socket factories for standard and SOCKS-proxied connections.

The Record I/O section documents a deprecated serialization and code-generation system replaced by Avro. It still matters as a compatibility surface: generated record classes implement Hadoop `WritableComparable`, records can be serialized in binary, CSV, and XML forms, raw comparators can be registered, and the record compiler plus Ant task still expose public entry points. The package-level documentation also preserves the original DDL, encoding, and Java/C++ mapping contracts.

## Important APIs, Types, and Functions

- `org.apache.hadoop.metrics.spi.MetricValue` wraps a `Number` with either `ABSOLUTE` or `INCREMENT` semantics through `isAbsolute()`, `isIncrement()`, and `getNumber()`.
- `NoEmitMetricsContext`, `NullContext`, and `NullContextWithUpdateThread` extend `AbstractMetricsContext`. They are deprecated compatibility contexts for cases that store-but-do-not-emit, do nothing, or run update callbacks without emitting data.
- `OutputRecord` exposes copied tags and metrics plus lookup by tag or metric name. Its returned tag types are documented as string and small integral types; metrics are numeric.
- `org.apache.hadoop.metrics.spi.Util.parse(String, int)` parses comma/space-separated host or host:port server specs and falls back to localhost with the supplied default port.
- `org.apache.hadoop.metrics2.AbstractMetric` is the immutable metric base. It implements `MetricsInfo`, delegates `name()` and `description()` to its info object, and requires `value()`, `type()`, and `visit(MetricsVisitor)`.
- `MetricsCollector` creates `MetricsRecordBuilder` instances by record name or `MetricsInfo`. `MetricsRecordBuilder` is a fluent abstract builder for tags, metrics, counters, gauges, context tags, and returning to the parent collector.
- `MetricsException` is the unchecked wrapper used across metrics2 constructors, registration, and management calls.
- `MetricsFilter` is a `MetricsPlugin` that accepts or rejects names, tags, tag sets, and whole records. The record-level method is concrete in the API surface while name/tag/tag-set decisions are abstract.
- `MetricsInfo`, `MetricsTag`, `MetricsRecord`, `MetricsSource`, `MetricsSink`, `MetricsVisitor`, `MetricsPlugin`, `MetricsSystem`, and `MetricsSystemMXBean` define the central metrics2 vocabulary: immutable metadata, grouping tags, timestamped records, sources that snapshot into collectors, sinks that consume records, visitor dispatch by metric kind, plugin initialization, source registration, publishing, shutdown, and JMX lifecycle/config access.
- `MetricStringBuilder` is a `MetricsRecordBuilder` implementation that accumulates a formatted string dump using a prefix, separator, and suffix.
- `org.apache.hadoop.metrics2.annotation.Metric` and `Metrics` are annotation types used by the metrics system to infer source metadata and metric fields/methods from annotated objects.
- `GlobFilter` and `RegexFilter` extend `AbstractPatternFilter`, compiling glob or regex expressions for metrics filtering.
- `DefaultMetricsSystem` is a singleton enum-style facade exposing static `initialize(prefix)`, `instance()`, and `shutdown()`.
- `Interns` creates interned `MetricsInfo` and `MetricsTag` objects, reducing duplicate metadata/tag allocation.
- `MetricsRegistry` owns a record/group info object and synchronized metric/tag maps. It can create integer/long counters, integer/long gauges, quantiles, stats, rates, aggregated rates, tags, context tags, add samples by name, and snapshot all registered mutable metrics.
- `MutableMetric` is the abstract changed-tracked metric base. It exposes `snapshot(builder, all)`, a convenience `snapshot(builder)`, protected `setChanged()` and `clearChanged()`, and public `changed()`.
- `MutableCounter`, `MutableCounterInt`, `MutableCounterLong`, `MutableGauge`, `MutableGaugeInt`, `MutableGaugeLong`, `MutableStat`, `MutableRate`, `MutableQuantiles`, `MutableRates`, and `MutableRatesWithAggregation` are the public mutable metric families for counters, gauges, latency/throughput statistics, periodic quantile estimators, synchronized method-rate collections, and thread-local aggregated rate collections.
- `FileSink`, `GraphiteSink`, and `StatsDSink` implement `MetricsSink` and `Closeable`; each initializes from `SubsetConfiguration`, accepts records through `putMetrics()`, flushes, and closes. `StatsDSink` additionally exposes `writeMetric(String)` and documents the StatsD line format plus configuration keys.
- `MBeans` registers and unregisters Hadoop MBeans using the standard `hadoop:service=<serviceName>,name=<nameName>` object-name convention and can extract service/name fields from an `ObjectName`.
- `MetricsCache` stores latest records for sinks that cannot handle sparse updates. It updates from `MetricsRecord`, optionally caches tags for later lookup, and retrieves by record name and tag collection.
- `Servers.parse(String, int)` is the metrics2 replacement for the older SPI server-spec parser.
- `DNSToSwitchMapping` resolves hostnames or IP addresses to network paths such as `/rack`, with cache reload hooks for all nodes or selected nodes.
- `AbstractDNSToSwitchMapping` adds `Configurable`, configuration storage, topology diagnostics, `isSingleSwitch()` policy hooks, `getSwitchMap()`, and static `isMappingSingleSwitch(DNSToSwitchMapping)`.
- `CachedDNSToSwitchMapping` wraps a raw mapper, caches resolved locations, exposes a copy of the host-to-switch map, delegates single-switch queries to the raw mapper, and reloads cached mappings.
- `ScriptBasedMapping` is a cached mapper backed by a script configured by `CommonConfigurationKeys.NET_TOPOLOGY_SCRIPT_FILE_NAME_KEY`; constructors accept default config, a raw mapping, or explicit `Configuration`.
- `ConnectTimeoutException` extends `SocketTimeoutException` and is the timeout surfaced by `NetUtils.connect`.
- `SocksSocketFactory` and `StandardSocketFactory` extend `javax.net.SocketFactory`. The SOCKS variant is configurable and equality/hash behavior depends on proxy configuration; the standard factory exposes direct socket creation methods.
- `TableMapping` extends `CachedDNSToSwitchMapping`, is configurable, and reloads mappings from a table-backed source.
- `BinaryRecordInput`/`BinaryRecordOutput`, `CsvRecordInput`/`CsvRecordOutput`, and `XmlRecordInput`/`XmlRecordOutput` implement the deprecated `RecordInput` and `RecordOutput` contracts for primitive values, `Buffer`, records, vectors, and maps.
- `Buffer` is a deprecated mutable byte sequence with capacity/count distinction, copy/set/append/truncate/reset operations, comparison, equality, cloning, and string conversion.
- `Index` is the iterator-like deserialization cursor returned by `startVector()` and `startMap()`.
- `Record` is the generated-record base class. It implements `WritableComparable` and `Cloneable`, requiring tagged `serialize`, tagged `deserialize`, and `compareTo`, while providing untagged serialize/deserialize plus `write(DataOutput)`, `readFields(DataInput)`, and `toString()`.
- `RecordComparator` is a `WritableComparator` base for optimized raw comparison of serialized `Record` implementations, with synchronized static `define(Class, RecordComparator)`.
- `RecordInput` and `RecordOutput` define the serializer/deserializer interface for byte, bool, int, long, float, double, UTF-8 string, `Buffer`, record, vector, and map boundaries.
- `Utils` provides deprecated record encoding helpers: float/double reading, variable-length int/long read/write, variable-int size calculation, byte comparison, and hex characters.
- `org.apache.hadoop.record.compiler` includes `CodeBuffer`, constants, primitive and compound type descriptors (`JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JMap`, `JVector`, `JRecord`, `JType`, `JField`), and `JFile.genCode(language, outputDirectory)`.
- `RccTask` is the Ant integration for the record compiler, accepting language, single file, filesets, destination directory, fail-on-error behavior, and `execute()`.
- `ParseException` is the JavaCC parser exception for record compiler parse failures, carrying `currentToken`, `expectedTokenSequences`, `tokenImage`, a special-constructor flag, and ASCII escaping for generated messages.
- `Rcc` begins in this chunk with parser constructors, `main`, `usage`, `driver`, grammar productions such as `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, `Vector`, parser reinitialization overloads, token accessors, and the start of `generateParseException()`.

## Control Flow

The old metrics SPI flow is context-buffer oriented. `MetricsRecordImpl` collects tags and metric values, then delegates `update()` and `remove()` back to its owning context. `MetricValue` tells that context whether an incoming number replaces the stored value or increments it. `NoEmitMetricsContext` keeps enough state for retrieval, `NullContext` drops everything, and `NullContextWithUpdateThread` keeps periodic updater callbacks active without emitting to an external sink.

The metrics2 flow is source-pull and sink-push. A `MetricsSystem` registers source objects, either directly with a name/description or by deriving metadata from annotations. When collection occurs, each `MetricsSource.getMetrics(collector, all)` receives a collector, calls `addRecord()`, and fills a builder with tags and metrics. The collector produces `MetricsRecord` instances; sinks receive them through `putMetrics()` and may flush or close during system stop. `publishMetricsNow()` is documented as a best-effort synchronous snapshot-and-flush path, while normal publishing is periodic in the implementation.

Mutable metrics follow an update-then-snapshot pattern. Counters increment, gauges increment/decrement/set, stats and rates accumulate samples, and quantiles add long values. `MutableMetric` tracks whether a metric changed so `snapshot(builder, all)` can skip unchanged values unless the caller requests all. `MutableStat` and `MutableQuantiles` synchronize sample update and snapshot methods. `MutableRates` synchronizes all access to its managed rate set, while `MutableRatesWithAggregation` moves per-thread updates into local rate counts and aggregates during synchronized snapshot.

Filtering is layered into metrics collection and sink pipelines. `GlobFilter` and `RegexFilter` compile configured patterns. `MetricsFilter.accepts(record)` can consider the record's name and tags after the lower-level name/tag predicates. `MetricsCache` sits on the sink side: incoming sparse `MetricsRecord` updates are merged into a stored record so sinks that require full records can render current state.

Network mapping flow starts with a list of hostnames/IPs and requires a returned list of network paths in the same order. `CachedDNSToSwitchMapping.resolve()` checks its cache, delegates misses to `rawMapping`, stores results, and returns a full ordered list. Cache reload calls either clear all mappings or selected names. `ScriptBasedMapping` configures the raw mapper from Hadoop configuration, invokes the script-defined mapping implementation underneath, then inherits caching. `AbstractDNSToSwitchMapping.dumpTopology()` reports implementation, known node mappings, and unique switch count for diagnostics.

Socket factory flow follows the `javax.net.SocketFactory` contract: callers ask for sockets by host/port or address/port, and the factory returns configured direct or proxied sockets. `SocksSocketFactory` additionally receives Hadoop configuration through `setConf()` before use, so proxy settings are configuration-driven.

Record I/O flow is DDL-to-generated-code plus runtime serialization. A `.jr` file declares includes, one module, and records. The record compiler parses input into `JFile`, `JRecord`, `JField`, and `JType` objects, then `genCode()` emits Java or C++ record code. The Ant task wraps this driver over a single file or nested filesets and optionally fails the build on errors.

Runtime Record I/O flow is stream-recursive. Generated `Record` subclasses implement tagged `serialize(RecordOutput, tag)` and `deserialize(RecordInput, tag)`. Binary, CSV, and XML record inputs/outputs read or write primitives, buffers, record boundaries, vector boundaries, and map boundaries. For vectors and maps, `startVector()` or `startMap()` returns an `Index`; generated deserializers loop until `done()` and call `incr()` after reading each element. `Record.write()` and `readFields()` bridge the record serialization contract to Hadoop `Writable`.

## State and Persistence Behavior

The XML file itself is static generated API metadata and does not persist runtime state. It is part of the dev-support compatibility surface used to compare public API changes across releases.

Metrics2 runtime state is held in registries, mutable metrics, caches, sinks, MBeans, and the default metrics system singleton. `MetricsRegistry` persists in-process metric objects and tags for a source. `MutableMetric.changed` state determines whether a metric appears in sparse snapshots. Counters and gauges keep current numeric values; stats keep rolling sample summaries; quantiles keep online estimators and a `previousSnapshot` map; aggregated rates keep thread-local sample data that can be lost if a short-lived thread dies before snapshot. `DefaultMetricsSystem` holds global singleton lifecycle state. `MBeans.register()` persists a platform MBean registration until explicit unregister or metrics shutdown.

Metrics sink persistence depends on the sink. `FileSink` writes records to a file-like target and must flush/close. `GraphiteSink` and `StatsDSink` emit to external monitoring daemons over network connections and may drop or fail metrics depending on connection state. `MetricsCache` is memory-only and stores the latest complete view of sparse records for sink formatting.

Network mapping state is process-local. `CachedDNSToSwitchMapping` stores host-to-rack cache entries and returns copies for diagnostics. Reload methods invalidate all or selected entries so future `resolve()` calls can observe changed topology data. `ScriptBasedMapping` stores configuration and script policy; `TableMapping` stores configuration for table lookup. These mappings influence HDFS block placement, YARN scheduling, and other topology-aware policies, but the mapping APIs themselves do not persist cluster topology remotely.

Record I/O state is stream and object state. `Buffer` owns or references a backing byte array and tracks count and capacity; using `set(byte[])` adopts the supplied array as backing storage while `copy()` replaces data with a copied range. Record inputs/outputs maintain stream cursors and encoding-specific parser/formatter state. Generated `Record` instances own field values and can be persisted through Hadoop Writable serialization, binary record streams, CSV text streams, XML streams, or generated C++/Java code. `RecordComparator.define()` mutates global comparator registration state for raw comparisons.

Record compiler state is parse/generation state. `ParseException` captures parser token state and expected token sequences. `Rcc` parser instances retain token manager/input stream state and can be reinitialized against new streams or readers. `RccTask` stores Ant task configuration including language, destination directory, filesets, and fail-on-error behavior before `execute()`.

## Dependencies and Integration Points

Metrics2 integrates with `org.apache.commons.configuration.SubsetConfiguration` for plugin/sink initialization, SLF4J/logging in implementations outside this slice, JMX through `MetricsSystemMXBean` and `MBeans`, Java annotations through `Metric`/`Metrics`, and Hadoop daemon source objects through `MetricsSource`. It also depends on utility classes from `org.apache.hadoop.metrics2.util` and mutable metric implementations in `org.apache.hadoop.metrics2.lib`.

Metrics records and tags depend on `MetricsInfo` identity and naming. `Interns` is an integration point for reducing duplicate info/tag objects, while `MetricStringBuilder` gives logging/debug output a builder-compatible sink. File, Graphite, and StatsD sinks connect the same record abstraction to local files and external observability systems.

Network topology APIs integrate with `org.apache.hadoop.conf.Configuration`, `Configurable`, `CommonConfigurationKeys`, `NetworkTopology.DEFAULT_RACK`, `NetUtils`, and Java networking types such as `Socket`, `InetAddress`, `InetSocketAddress`, `Proxy`, and `SocketTimeoutException`. The rack mapping contract is used by higher-level distributed filesystem and cluster scheduler code that needs placement locality and single-rack/multi-rack policy decisions.

Record I/O integrates with Hadoop's `Writable`, `WritableComparable`, and `WritableComparator` APIs, Java `DataInput`/`DataOutput`, JavaCC-generated parser classes, Ant `Task`/`FileSet`/`BuildException`, and generated C++ support files described by the package docs. The API is explicitly deprecated in favor of Avro, but the compatibility surface remains public in 2.8.0.

## Risks and Edge Cases

The biggest metrics risk is concurrency and sparse-state semantics. Some `MetricsRegistry` and mutable metric methods are synchronized while others are not; callers need the implementation's thread-safety guarantees, especially around high-volume counters, gauges, and rates. `MutableRates` is documented as high-contention-unfriendly, and `MutableRatesWithAggregation` can lose samples produced by threads that die before the next snapshot.

Metric identity is name/tag driven. Duplicate metric names or tags in a `MetricsRegistry` can conflict, and tag override behavior must be explicit. `MetricsFilter` implementations can accidentally drop whole records if tag-set and record-level predicates do not match. `MetricsCache` can grow or evict based on max records per name; sinks relying on complete state need tests for eviction and tag-included lookup behavior.

Sink behavior is externally fragile. File, Graphite, and StatsD sinks depend on filesystem or network availability and on correct configuration keys. `publishMetricsNow()` is only best-effort, so tests and admin tooling must not assume all sinks are fully flushed before the call returns.

JMX registration has naming collision risk. `MBeans.register()` uses a standard `hadoop:service=...,name=...` convention, so duplicate service/name pairs or invalid object-name characters can fail registration or hide the intended MBean. `currentConfig()` deliberately avoids a getter name that JConsole would expose as an unsupported multiline attribute.

Network topology mapping has correctness risk because placement policy consumes the returned rack paths. `DNSToSwitchMapping.resolve()` must preserve input order and size; unresolved nodes should normally map to `NetworkTopology.DEFAULT_RACK`. Cache reload gaps can leave stale rack assignments in long-running processes. `AbstractDNSToSwitchMapping.isMappingSingleSwitch()` documentation is subtle and should be confirmed against implementation because single-switch detection changes block-placement and scheduling decisions.

Script-based mapping is operationally sensitive. Missing scripts, slow scripts, script failures, malformed output, and configuration reload behavior all affect cluster topology visibility. The public `NO_SCRIPT` text is only diagnostic; lack of a script generally means default rack behavior, not an executable mapping.

Socket factories can affect all client connections using them. SOCKS proxy equality/hash behavior matters if factories are cached. Misconfigured proxies can produce hard-to-diagnose connection failures, while `ConnectTimeoutException` should be preserved distinctly from read timeouts and generic socket errors.

Record I/O carries deprecation and compatibility risk. New code should not build on it, but existing serialized data and generated code may depend on exact binary, CSV, XML, comparison, and Writable behavior. The package docs show several historical spelling and markup issues; the final report should treat the generated API and implementation tests as authoritative over prose typos.

`Buffer` exposes backing array behavior: `get()` returns data valid only through `getCount()`, and `set(byte[])` adopts the supplied storage. Callers can accidentally mutate shared data or read capacity bytes beyond count. Capacity shrink/grow and append operations need bounds tests.

Record encodings have format-specific edge cases: variable-length integer encoding boundaries; UTF-8 normalization; percent escaping for CSV and XML strings/buffers; XML restrictions around null/control characters and carriage returns; CSV delimiter escaping; vector/map size handling; and cross-language C++/Java type mappings. Raw comparator registration is global and synchronized, so duplicate or incompatible comparators can affect sorting/job behavior.

The chunk ends inside `org.apache.hadoop.record.compiler.generated.Rcc`, so parser control-flow and parser fields are incomplete in this research document. Adjacent chunk reconciliation is needed before making final statements about the full generated parser API.

## Test Signals

Useful validation for the metrics surface should include:

- Old SPI compatibility tests for `MetricValue` absolute vs increment behavior, `OutputRecord` copied tag/metric maps, null/no-emit contexts, and server-spec parsing with null, comma, space, host-only, and host:port inputs.
- Metrics2 source lifecycle tests covering `MetricsSystem.register()` by object and by explicit name/description, duplicate source registration, unregister, callback registration, `publishMetricsNow()` best-effort behavior, and shutdown return value.
- Builder tests verifying tags, context tags, counters, gauges of every primitive width, abstract metrics, parent/endRecord chaining, and `MetricStringBuilder` formatting.
- Filter tests for glob and regex configuration, name/tag/tag-set/record predicate interactions, and rejection effects on records reaching sinks.
- `MetricsRegistry` tests for duplicate metrics/tags, override vs non-override tags, synchronized getters, creation of each mutable metric type, `add(name, value)`, `snapshot()`, and context tag output.
- Mutable metric tests for changed flag handling, `all=false` sparse snapshots, counter/gauge increments and decrements, stat mean/min/max/stddev behavior, quantile rollover intervals and invalid interval errors, and reset-min-max.
- Concurrency tests comparing `MutableRates` under contention with `MutableRatesWithAggregation`, including the documented case where samples from short-lived threads can be lost before snapshot.
- Sink tests for file output/flush/close, Graphite connection failure handling, StatsD line formatting with and without hostname, service name configuration, and `MetricsCache` sparse update merging and max-record eviction.
- JMX tests for `MBeans.register()` object-name format, service/name extraction, duplicate names, unregister idempotence, and metrics MBean start/stop through `MetricsSystemMXBean`.

Network and socket tests should include:

- `DNSToSwitchMapping.resolve()` preserving order and count for empty, known, unknown, hostname, and IP inputs, plus default-rack fallback.
- Cache hit/miss behavior in `CachedDNSToSwitchMapping`, `getSwitchMap()` returning a defensive copy, selected and full reload invalidation, and delegation of single-switch policy.
- `ScriptBasedMapping` behavior for no script, configured script, failing script, malformed output, configuration reload, and diagnostic `toString()`.
- `TableMapping` configuration loading and reload behavior.
- `SocksSocketFactory` and `StandardSocketFactory` socket creation overloads, equality/hash code, proxy configuration, connection timeout propagation as `ConnectTimeoutException`, and direct vs proxied connection routing.

Record I/O and compiler tests should include:

- Binary, CSV, and XML round trips for every primitive, nested records, vectors, maps, empty collections, large buffers, UTF-8 strings, percent-escaped CSV/XML characters, control characters, and variable-length integer boundary values.
- `Buffer` tests for constructor ownership/copy semantics, `set`, `copy`, `append`, `reset`, `truncate`, capacity changes, comparison, equality, clone, and string conversion with explicit charset.
- Generated `Record` tests for tagged and untagged serialize/deserialize, `Writable.write/readFields`, `compareTo`, `toString`, equality/hash behavior in generated classes, and raw `RecordComparator.define()` registration.
- `RecordInput`/`RecordOutput` tests that generated code correctly consumes `Index.done()` and `Index.incr()` for vectors/maps and handles mismatched collection sizes or malformed input.
- `Utils` tests for zero-compressed VInt/VLong read/write, size calculation, float/double network byte order, and byte comparison.
- Record compiler tests for includes, module parsing, primitive/compound type parsing, Java and C++ code generation output paths, generated package/namespace mapping, invalid DDL parse exceptions with expected-token messages, and `Rcc.ReInit()` reuse.
- `RccTask` Ant tests for single file vs fileset inputs, language selection, destination directory, fail-on-error true/false, and build exception behavior.

## Cross-Chunk Notes

This chunk starts after the beginning of `org.apache.hadoop.metrics.spi.MetricsRecordImpl`, so the full old-SPI record implementation API must be merged from the previous chunk. It also ends inside the `org.apache.hadoop.record.compiler.generated.Rcc` class, before the generated parser class is complete. The final per-file research should combine this with adjacent chunks and should keep the distinction clear between generated JDiff API metadata and actual Java implementation files.

### subset-b-007170: lines 30694-36789

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 30694-36789

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.8.0. It starts in the tail of the deprecated generated record compiler parser `org.apache.hadoop.record.compiler.generated.Rcc`, covers the rest of generated record compiler support, the deprecated `org.apache.hadoop.record.meta` type metadata package, large parts of Hadoop security and token APIs, the service lifecycle framework, tracing admin protocol types, and utility APIs through most of `org.apache.hadoop.util.Shell`.

Because the source is generated API metadata rather than executable Java source, the research surface is the compatibility contract: packages, class/interface names, inheritance, implemented interfaces, constructors, method signatures, public/protected fields, checked exceptions, deprecation markers, and embedded Javadocs. The chunk begins and ends inside classes, so adjacent chunks own the opening of `Rcc` and the remainder of `Shell`.

## Purpose

The record compiler and `record.meta` APIs preserve the legacy Hadoop Record I/O compiler and type-description model. They are all deprecated in favor of Avro, but they still define parser tokens, lexer streams, token objects, lexer errors, and record schema metadata classes that older generated record code may reference.

The security APIs define Hadoop's process and RPC identity model: access-control exceptions, credentials storage, user/group/id mapping, Kerberos and token utility methods, UGI login/proxy/doAs behavior, credential-provider abstraction, ACL parsing/serialization, and proxy-user impersonation checks. The HTTP and token packages add web request protections, X-Frame headers, secret manager and token contracts, token renewal/selection, and HTTP delegation-token client flows.

The service APIs define a reusable lifecycle model for Hadoop daemons and components. `Service`, `AbstractService`, `CompositeService`, `ServiceStateModel`, lifecycle events, listeners, and helper operations provide a common NOTINITED/INITED/STARTED/STOPPED state machine with failure recording, listener notification, blockers, and orderly child-service shutdown.

The tracing and utility APIs expose span-receiver administration, application classloading isolation, progress callbacks, IP-list matching, pure-Java CRC implementations, reflection helpers, and platform-specific shell command construction/execution.

## Important APIs, Types, and Functions

### Deprecated record compiler and metadata

- `RccConstants` enumerates parser token kinds for the deprecated record compiler grammar: module, record, include, primitive types, string/buffer/vector/map tokens, punctuation, string/identifier tokens, lexical states, and `tokenImage`.
- `RccTokenManager` implements `RccConstants` and exposes JavaCC-style lexer lifecycle: constructors over `SimpleCharStream`, `setDebugStream(PrintStream)`, `ReInit(...)`, `SwitchTo(int)`, protected `jjFillToken()`, and `getNextToken()`.
- `SimpleCharStream` wraps `Reader` or `InputStream` inputs, including encoding-aware constructors and `ReInit` overloads. It tracks buffer positions, line/column arrays, CR/LF state, tab width, backup count, and exposes `BeginToken()`, `readChar()`, `backup()`, `GetImage()`, `GetSuffix()`, `Done()`, and `adjustBeginLineColumn()`.
- Generated `Token` stores token kind, begin/end line and column, string image, next regular token, and preceding special token. `newToken(int)` is the customization hook for token subclasses.
- `TokenMgrError` extends `Error`, formats lexical errors, escapes unprintable characters, and exposes `getMessage()`.
- `TypeID` and constants such as `BoolTypeID`, `BufferTypeID`, `ByteTypeID`, `DoubleTypeID`, `FloatTypeID`, `IntTypeID`, `LongTypeID`, and `StringTypeID` describe base record types. `VectorTypeID`, `MapTypeID`, and `StructTypeID` add element/key/value/record-type composition.
- `FieldTypeInfo` couples a field id/name with a `TypeID`; `RecordTypeInfo` is a writable record schema with name, fields, nested-struct lookup, `serialize(RecordOutput, String)`, `deserialize(RecordInput, String)`, and a `compareTo` that is explicitly not intended for sorting.
- `Utils.skip(RecordInput, String, TypeID)` reads and discards data based on a type descriptor.

### Security identity, credentials, and mapping

- `AccessControlException` extends the filesystem permission exception and keeps constructors needed for IPC `RemoteException` unwrapping.
- `Credentials` implements `Writable` for in-memory and persisted token/secret-key storage. It supports token lookup/add/enumeration/counting, secret-key lookup/add/remove/enumeration/counting, token-storage file/stream read/write, `write(DataOutput)`, `readFields(DataInput)`, `addAll()` with overwrite, and `mergeAll()` without overwrite.
- `GroupMappingServiceProvider` is the user-to-groups provider interface used by `Groups`, with `getGroups(String)`, `cacheGroupsRefresh()`, `cacheGroupsAdd(List)`, and `GROUP_MAPPING_CONFIG_PREFIX`.
- `IdMappingServiceProvider` maps users/groups to numeric IDs and back, with strict `getUid()`/`getGid()` that can throw `IOException` and permissive `getUidAllowingUnknown()`/`getGidAllowingUnknown()` variants.
- `SecurityUtil` centralizes Kerberos and token helpers: original-TGT detection, server-principal host substitution, keytab login overloads, delegation-token service-name construction, host extraction from principals, Kerberos/token annotation lookup, token service address extraction and setting, login/current-user `doAs` wrappers, authentication-method mapping, and privileged-port detection.
- `UserGroupInformation` wraps JAAS `Subject` identity. It exposes global configuration/security state, current/login/ticket-cache/subject UGI resolution, keytab and ticket-cache login/relogin/logout flows, remote/proxy/test user construction, real-user access, short and full names, primary group, group lists, token identifier/token/credential management, authentication method state, subject equality/hash, privileged `doAs` execution, diagnostics, and `HADOOP_TOKEN_FILE_LOCATION`.
- `UserGroupInformation.AuthenticationMethod` bridges UGI authentication methods to `SaslRpcServer.AuthMethod`.

### Credential providers, authorization, and HTTP filters

- `CredentialProvider` is the abstract password/secret store contract. It distinguishes transient stores, requires `flush()` for persistence, supports alias lookup/list/create/delete, password-needed diagnostics, and clear-text fallback configuration.
- `CredentialProviderFactory` creates providers from URI paths in `Configuration` using a service-loader interface and the `CREDENTIAL_PROVIDER_PATH` key.
- `AccessControlList` implements `Writable` for configured user/group ACLs. Constructors accept a combined ACL string or separate comma-separated user/group lists; methods add/remove users and groups, expose unmodifiable user/group collections, test direct membership and effective allowance against `UserGroupInformation`, stringify for display or exact reconstruction, and serialize/deserialize. `WILDCARD_ACL_VALUE` marks all-access ACLs.
- `AuthorizationException` extends `AccessControlException` but intentionally suppresses stack traces for security purposes.
- `DefaultImpersonationProvider` implements `ImpersonationProvider` and `Configurable`, initializes proxy-user configuration from a prefix, authorizes proxy users by effective user and remote address, and exposes generated superuser user/group/IP config keys plus proxy group/host maps.
- `RestCsrfPreventionFilter` is a servlet `Filter` that treats browser user agents as needing a custom CSRF header unless configured methods are ignored. It exposes constants for `User-Agent`, browser regex, custom header, and ignored methods, plus `handleHttpInteraction()` for servlet-independent filtering.
- `XFrameOptionsFilter` is a servlet `Filter` that sets an X-Frame-Options-style header using configurable header/value parameters.

### Tokens and web delegation-token clients

- `SecretManager<T extends TokenIdentifier>` creates and retrieves passwords, has a retriable retrieval path, creates identifiers, checks read availability, and provides static helpers for generating secrets, creating passwords, and wrapping secret keys.
- `org.apache.hadoop.security.token.Token<T>` implements the writable token payload: identifier bytes, password bytes, kind, service, URL-string encode/decode, identifier decoding through the token identifier class, equality/hash/string/cache-key helpers, and renew/cancel/isManaged operations through registered renewers.
- `Token.TrivialRenewer` is a default no-op renewer implementation; `TokenRenewer` is the abstract renew/cancel contract keyed by token kind; `TokenSelector<T>` selects a token from a collection for a service.
- `TokenIdentifier` is the writable identity payload contract with `getKind()`, `getUser()`, byte serialization through `getBytes()`, and tracking id support.
- `TokenInfo` is an annotation-like type that identifies the renewer class associated with a token-using protocol.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` with Hadoop delegation-token operations. It supports configurable default authenticator class, optional query-string token transport, connection opening with delegation tokens and optional `doAs`, token fetch, renew, and cancel overloads. Its nested `Token` holds both HTTP authentication state and a Hadoop delegation token.
- `DelegationTokenAuthenticator` wraps another `Authenticator` and adds HTTP/S delegation-token request, renew, and cancel flows with JSON/header/parameter constants for operation, delegation token, token, renewer, and response keys.
- `KerberosDelegationTokenAuthenticator` adds SPNEGO delegation-token support and falls back to pseudo authentication when the endpoint does not trigger SPNEGO. `PseudoDelegationTokenAuthenticator` models simple authentication by trusting the current UGI user as a query-string user.

### Service lifecycle framework

- `Service` is the lifecycle interface with `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration, name/config/state/start-time/failure/history/blocker accessors, and `waitForServiceToStop(long)`.
- `AbstractService` implements `Service`. It enforces state transitions, records first failure cause and failure state, stores configuration and start time, supports global and local listeners, records lifecycle history, tracks blocker name/details, exposes protected hooks `serviceInit()`, `serviceStart()`, and `serviceStop()`, and makes `close()` relay to `stop()`.
- `CompositeService` extends `AbstractService` for child-service management. It clones the service list for callers, adds/removes services, adds arbitrary objects only if they implement `Service`, and initializes/starts/stops children according to `STOP_ONLY_STARTED_SERVICES`.
- `LifecycleEvent` is a serializable record of transition time and new state; `LoggingStateChangeListener` logs service state changes.
- `ServiceOperations` stops services safely or quietly, returning caught exceptions for cleanup paths.
- `ServiceStateChangeListener` callbacks run on the initiating thread while the service is synchronized, making long-running listener work and reentrant service calls a documented deadlock risk.
- `ServiceStateException` converts arbitrary throwables into runtime service-state failures. `ServiceStateModel` stores the current lifecycle state, validates transitions, enters states thread-safely, and exposes static transition checks.

### Tracing and utility APIs

- `SpanReceiverInfo` exposes span receiver id and class name; `SpanReceiverInfoBuilder` collects class name and configuration pairs; `TraceAdminProtocol` lists/adds/removes span receivers and declares `versionID`; `TraceAdminProtocolPB` bridges protobuf RPC and `VersionedProtocol`.
- `ApplicationClassLoader` extends `URLClassLoader` to isolate application classes from system classes. It can be built from URL arrays or classpath strings, overrides resource and class loading, and exposes `isSystemClass()` plus `SYSTEM_CLASSES_DEFAULT`.
- `IPList.isIn(String)` tests whether an address is included in an IP list, and `Progressable.progress()` is the classic Hadoop progress callback.
- `PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum` with `getValue()`, `reset()`, and byte-array/int `update()` methods.
- `ReflectionUtils` handles `Configurable` injection, configuration-aware instance construction, contention tracing, thread dumps to streams/logs with throttling, typed class lookup, writable copy/clone through serialization, and retrieval of declared fields/methods including inherited members.
- `Shell` constructs and executes platform-specific shell commands. Static helpers cover Windows command-line length checks, group/user/netgroup commands, permission/owner/symlink/readlink/process/signal commands, environment-variable regexes, platform script extensions and interpreters, Hadoop home and qualified binary discovery, winutils detection, bash support checks, and simple `execCommand()` overloads. Subclasses implement `getExecString()` and `parseExecResult(BufferedReader)`, while the base class manages environment, working directory, process, exit code, timeout flag, and re-execution interval.

## Control Flow

The XML file has no runtime control flow, but the documented APIs imply several important flows:

- Record compiler lexing flows from `SimpleCharStream` through `RccTokenManager.getNextToken()` into linked `Token` objects, with `TokenMgrError` used for lexical failures. Parser tracing is toggled on `Rcc` through the tail methods visible at the start of the chunk.
- Record metadata flows build a `RecordTypeInfo` from named `FieldTypeInfo` entries and nested `TypeID` structures, then serialize/deserialize that schema through Hadoop Record I/O `RecordOutput` and `RecordInput`. `Utils.skip()` uses the same `TypeID` graph to consume data without materializing it.
- Credentials are populated in memory, optionally loaded from a token storage file or stream, merged into another credentials object, and written back through `Writable` or token-storage methods. `addAll()` overwrites aliases; `mergeAll()` preserves existing ones.
- UGI setup starts with `setConfiguration()`, resolves current/login users from JAAS subjects, ticket cache, or keytab, renews/relogs Kerberos credentials as needed, then runs code under a user identity through `doAs(PrivilegedAction)` or `doAs(PrivilegedExceptionAction)`. Proxy users carry a real user whose authentication method is consulted by helper APIs.
- Authorization flows parse ACL strings or proxy-user configuration, map users to groups/hosts, and test an incoming `UserGroupInformation` plus remote address. `AuthorizationException` intentionally avoids revealing stack traces.
- HTTP delegation-token flows authenticate a connection with an underlying authenticator, request a delegation token over HTTP/S, store it in a `DelegationTokenAuthenticatedURL.Token`, attach the token to subsequent connections either in headers or query strings, and later renew or cancel it. Kerberos-backed flows can fall back to pseudo authentication.
- Service lifecycle flows are state-machine driven: `init()` invokes `serviceInit()`, `start()` invokes `serviceStart()`, `stop()` invokes `serviceStop()`, all while recording lifecycle events, failures, listeners, blockers, and child-service behavior for composites.
- Shell execution flows through subclass-provided command arrays and parse callbacks. `run()` checks the minimum interval, starts a process with configured environment and working directory, captures output for parsing, records exit/timeout state, and exposes the live process and exit code.

## State and Persistence Behavior

The JDiff file itself persists API metadata for compatibility checks and release documentation. It does not store application data.

Several APIs in this chunk are persistence-sensitive:

- `Credentials`, `AccessControlList`, `Token`, `TokenIdentifier`, and record metadata types implement Hadoop `Writable` or record serialization contracts. Their binary and textual encodings are compatibility surfaces for job tokens, delegation tokens, ACL configuration, and older Record I/O users.
- `CredentialProvider` separates transient credential stores from persistent providers and requires explicit `flush()` to push changes to backing storage.
- UGI stores identity state in JAAS `Subject` instances, including authentication method, token identifiers, tokens, credentials, and real-user/proxy relationships. Keytab and ticket-cache login state is process-global enough that relogin and logout paths have broad side effects.
- Service objects keep lifecycle state, configuration, start time, failure cause/state, lifecycle history snapshots, listeners, and blocker maps. `CompositeService` adds child-service lists and shutdown policy state.
- Shell instances keep environment overrides, working directory, process handle, last exit code, timeout flag, redirect-error-stream setting, and re-execution interval state. Static Hadoop home/winutils helpers depend on environment variables, system properties, and file existence.
- `ApplicationClassLoader` stores classpath URLs and system-class patterns, which directly affect runtime class/resource resolution.

## Dependencies and Integration Points

The chunk depends heavily on Java standard APIs: `Reader`, `InputStream`, `PrintStream`, `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, `File`, `URI`, `URL`, `HttpURLConnection`, servlet `Filter` APIs, JAAS `Subject`, privileged actions, collections, `Checksum`, `URLClassLoader`, `Process`, `BufferedReader`, crypto `SecretKey`, and checked exceptions such as `IOException`, `UnsupportedEncodingException`, `FileNotFoundException`, `ServletException`, and authentication exceptions.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configurable` for UGI/security configuration, impersonation providers, credential-provider discovery, service initialization, and reflection-based object configuration.
- `org.apache.hadoop.io.Writable`, `Text`, `WritableUtils`, and token/credential serialization used by RPC, MapReduce jobs, filesystem clients, and delegation-token files.
- `org.apache.hadoop.fs.Path`, filesystem permission exceptions, and Hadoop home/bin utilities used by command execution and security setup.
- `org.apache.hadoop.security.authentication.client.AuthenticatedURL`, `Authenticator`, `ConnectionConfigurator`, and `AuthenticationException` for HTTP authentication and delegation-token clients.
- `org.apache.hadoop.ipc.VersionedProtocol` and generated protobuf blocking interfaces for tracing admin RPC.
- `org.apache.hadoop.record.RecordInput`, `RecordOutput`, and legacy record compiler generated code.
- Commons Logging and SLF4J logging used by service listeners, reflection thread dumps, shell diagnostics, and security utilities.

## Risks and Edge Cases

- The chunk starts and ends inside classes. The merge lane must combine this with adjacent chunks before making complete-file claims about `Rcc` and `Shell`.
- JDiff gives signatures and Javadocs, not implementation bodies. Exact synchronization, timeout handling, command arrays, binary encodings, and exception text require source-code validation.
- The record compiler APIs are deprecated but still public. Removing or changing them can break old generated record code even though Avro is the recommended replacement.
- `SimpleCharStream` exposes mutable lexer buffer state and many reinitialization paths. Off-by-one line/column handling, CR/LF normalization, backup counts, tab widths, and encoding constructors are compatibility-sensitive.
- `Credentials` stores byte arrays and tokens by aliases. Aliasing, mutation of returned arrays/tokens, overwrite-vs-merge semantics, and token-storage format compatibility are high-risk areas.
- UGI methods mix process-global login state, subject-local credentials, Kerberos keytab/ticket-cache renewal, proxy users, and privileged execution. Misordered configuration or relogin calls can affect unrelated callers in the same JVM.
- `AuthorizationException` suppresses stack traces. This is deliberate for security, but it can hide operational diagnostics if callers do not log enough context.
- ACL and proxy-user authorization depend on string parsing of users, groups, hosts, wildcard values, and remote addresses. Empty lists, wildcard ACLs, unknown users, and group lookup failures need explicit coverage.
- HTTP CSRF filtering depends on user-agent regexes and ignored methods. Browser misclassification or missing custom headers can either block legitimate clients or permit unsafe browser-originated requests.
- Delegation-token URL handling has both header and query-string modes. Query-string token transport risks token leakage through logs, browser history, proxies, and referrers if enabled casually.
- `AuthenticatedURL` instances are documented as not thread-safe; callers sharing `DelegationTokenAuthenticatedURL` or its token objects across threads need synchronization.
- Service listeners run synchronously during state changes and are warned against long-running or reentrant service calls. Listener misuse can block lifecycle transitions or deadlock.
- `CompositeService` shutdown policy and partial init/start failures are subtle: child services may be stopped even if not fully started, depending on failure path and `STOP_ONLY_STARTED_SERVICES`.
- `ApplicationClassLoader` class/resource ordering and system-class pattern matching can cause class shadowing or dependency leakage between application and Hadoop runtime classes.
- Shell helpers are platform-specific. Windows command-line length, winutils discovery, Hadoop home resolution, environment regexes, script suffixes, and group/id command behavior all vary by OS and configuration.

## Test Signals

Useful validation for this API surface should include:

- Golden API compatibility checks for all public/protected classes, interfaces, fields, constructors, methods, checked exceptions, deprecation markers, and package boundaries in this chunk.
- Lexer/parser compatibility tests for `SimpleCharStream`, `RccTokenManager`, `Token`, and `TokenMgrError`, including encoded input streams, CR/LF/tab line-column accounting, token backup, special tokens, EOF handling, tracing toggles, and lexical-error messages.
- Record metadata round trips for base, vector, map, struct, nested-record, and field type info, plus `Utils.skip()` coverage for each supported type.
- `Credentials` tests for token and secret-key add/get/remove/enumeration/counting, stream/file read/write, `Writable` round trips, alias overwrite in `addAll()`, alias preservation in `mergeAll()`, and mutation/copy behavior of byte-array secrets.
- Group/id mapping tests for known and unknown users/groups, cache refresh/add behavior, strict vs allowing-unknown ID methods, and empty-list handling for missing users.
- UGI tests covering simple and Kerberos modes, ticket-cache and keytab login, relogin throttling/immediate-renewal test hooks, proxy users and real users, token/credential propagation, authentication method mapping, group lookups, and `doAs` exception propagation.
- Security utility tests for principal host substitution, token service address build/parse/set, privileged port detection, annotation lookup, and fatal/nonfatal login-user `doAs` wrappers.
- Credential-provider tests for service-loader discovery from `CREDENTIAL_PROVIDER_PATH`, transient vs persistent providers, duplicate alias creation, delete, password-needed warning/error paths, clear-text fallback, and required `flush()`.
- ACL and impersonation tests for wildcard ACLs, empty users/groups, add/remove operations, exact ACL string reconstruction, writable serialization, stack-trace suppression in authorization failures, proxy-user user/group/IP config keys, and remote-address authorization.
- Servlet filter tests for CSRF browser regex defaults and customizations, custom header names, ignored methods, non-browser user agents, missing/invalid headers, X-Frame header configuration, and filter lifecycle.
- Token tests for password creation/retrieval, retriable failures, identifier decoding, URL-string encode/decode, service mutation, renewer selection, trivial renewer behavior, cancellation, managed/unmanaged token handling, and cache-key stability.
- HTTP delegation-token tests for Kerberos and pseudo authenticators, fallback behavior, `doAs` owner handling, header vs query-string transport, JSON response parsing, renew/cancel with and without authentication, unsupported non-HTTP URLs, and thread-safety assumptions.
- Service lifecycle tests for valid and invalid transitions, null configuration rejection, first failure capture, listener notification order and deadlock-safe expectations, blocker map snapshots, lifecycle history snapshots, wait-for-stop timing, `ServiceOperations.stopQuietly()`, and composite child init/start/stop ordering under partial failure.
- Tracing admin tests for span receiver list/add/remove RPC contracts and protobuf bridge compatibility.
- Utility tests for application classloader class/resource precedence, system-class pattern matching, CRC32/CRC32C values against known vectors, reflection configuration injection and inherited field/method discovery, writable copy/clone behavior, throttled thread logging, and platform shell command construction/execution on Unix and Windows.

## Cross-Chunk Notes

`subset-b-007169` should own the earlier portion of `org.apache.hadoop.record.compiler.generated.Rcc` and any package context before line 30694. `subset-b-007171` should complete `org.apache.hadoop.util.Shell` and subsequent utility APIs. The reconciliation lane should merge those adjacent chunks before producing a final report for `Apache_Hadoop_Common_2.8.0.xml`.

### subset-b-007171: lines 36790-37921

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 36790-37921

## Scope

This chunk is a JDiff API snapshot segment from Apache Hadoop Common 2.8.0. It starts in the tail of `org.apache.hadoop.util.Shell`, covers all visible APIs for `StringInterner`, `SysInfo`, `Tool`, `ToolRunner`, and the public `org.apache.hadoop.util.bloom` classes in this file, then ends with empty package stubs for `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash`.

The source is generated compatibility metadata, not implementation code. The useful research surface is therefore the public/protected API contract: type names, inheritance, implemented interfaces, constructors, method signatures, parameters, return types, checked exceptions, static/final/synchronized/abstract flags, deprecation text, fields, and Javadocs.

## Purpose

The `Shell` tail exposes Hadoop's cross-platform shell execution constants and state fields. These constants encode operating-system detection, command names used by file-permission/link utilities, Windows process-launch constraints, Hadoop home/winutils discovery, and shell-output parsing conventions used by callers that invoke native commands.

`StringInterner` provides Hadoop-local string canonicalization with strong and weak retention modes. It exists as a performance/memory-management alternative to `String.intern()`, especially for large Hadoop processes that repeatedly store equal strings.

`SysInfo` defines an abstract system-resource metrics plugin. It presents a platform-neutral contract for memory, CPU, vcore, network, and storage counters, with `newInstance()` selecting an OS-specific implementation or throwing when the platform cannot be determined.

`Tool` and `ToolRunner` define the standard Hadoop command-line application pattern. A `Tool` receives generic Hadoop options through `Configuration` handling and then runs application-specific arguments. `ToolRunner` wires `GenericOptionsParser`, configuration mutation, generic usage output, and yes/no prompting around the application `run` method.

The `org.apache.hadoop.util.bloom` package exposes probabilistic set-membership data structures: standard, counting, dynamic, and retouched Bloom filters, plus the hash adapter and removal-scheme constants used by retouched filters. These APIs are compact serialization-aware utilities for approximate membership tests and related network/cache protocols.

## Important APIs, Types, and Functions

### `org.apache.hadoop.util.Shell` Tail

- `WINDOWS_MAX_SHELL_LENGTH` is a public static final `int` documenting the Windows maximum command-line length from KB830473.
- `WINDOWS_MAX_SHELL_LENGHT` is the deprecated misspelled alias. The deprecation explicitly directs callers to `WINDOWS_MAX_SHELL_LENGTH`, so binary compatibility with older callers is intentionally retained.
- `USER_NAME_COMMAND`, `SET_PERMISSION_COMMAND`, `SET_OWNER_COMMAND`, `SET_GROUP_COMMAND`, `LINK_COMMAND`, and `READ_LINK_COMMAND` are public static final command-name strings used by shell-backed user, permission, ownership, group, hard/symbolic link, and readlink operations.
- `WindowsProcessLaunchLock` is a public static final `Object` used as a synchronization object for Windows `CreateProcess` launches.
- `osType` exposes the parsed `Shell.OSType`, and boolean platform flags `WINDOWS`, `SOLARIS`, `MAC`, `FREEBSD`, `LINUX`, `OTHER`, and `PPC_64` expose common branch predicates.
- `ENV_NAME_REGEX` documents the accepted environment-variable name pattern. `TOKEN_SEPARATOR_REGEX` documents the token separator used to parse shell-tool output.
- Protected instance fields `timeOutInterval` and `inheritParentEnv` carry per-shell execution policy: timeout duration and whether child processes inherit parent environment variables.
- `WINUTILS` is a deprecated nullable `String` path to `winutils`; the Javadoc warns callers must check for null and directs new callers to exception-raising getters such as `getWinUtilsPath()` and `getWinUtilsFile()`.
- `isSetsidAvailable` advertises whether `setsid` exists on the current platform.

### `StringInterner`

- Public constructor `StringInterner()` is visible, though the useful operations are static.
- `strongIntern(String sample)` returns the canonical equal string while retaining a strong reference, preventing garbage collection of the representative instance.
- `weakIntern(String sample)` returns the canonical equal string while retaining only a weak reference, allowing the representative instance to be garbage-collected.
- Class Javadoc positions this as equivalent in behavior to `String.intern()` while avoiding permanent-generation memory pressure.

### `SysInfo`

- `SysInfo` is an abstract public base class with a public constructor.
- `newInstance()` returns the default OS implementation and may throw `UnsupportedOperationException` when the OS cannot be determined.
- Abstract memory methods return byte counts: `getVirtualMemorySize()`, `getPhysicalMemorySize()`, `getAvailableVirtualMemorySize()`, and `getAvailablePhysicalMemorySize()`.
- Abstract CPU methods return processor and usage information: `getNumProcessors()`, `getNumCores()`, `getCpuFrequency()` in kHz, `getCumulativeCpuTime()` in milliseconds, `getCpuUsagePercentage()` from 0 to 100 or `-1` unavailable, and `getNumVCoresUsed()` from 0 to number of vcores or `-1` unavailable.
- Abstract I/O counter methods return aggregate byte counters: `getNetworkBytesRead()`, `getNetworkBytesWritten()`, `getStorageBytesRead()`, and `getStorageBytesWritten()`.

### `Tool`

- `Tool` is a public interface extending `org.apache.hadoop.conf.Configurable`.
- `run(String[] args)` returns an integer exit code and throws generic `Exception`.
- Javadocs define the intended pattern: delegate generic Hadoop command-line options to `ToolRunner`, read the processed `Configuration` from `getConf()`, then process only custom arguments in the tool implementation.
- The example references MapReduce types such as `JobConf`, `JobClient`, `RunningJob`, mapper/reducer classes, and `Path`, but those are documentation examples rather than signatures in this chunk.

### `ToolRunner`

- Public constructor `ToolRunner()` is visible.
- `run(Configuration conf, Tool tool, String[] args)` parses generic Hadoop arguments, sets the tool's possibly modified configuration, then calls `Tool.run(String[])` and returns that exit code.
- `run(Tool tool, String[] args)` delegates to the configuration-bearing overload using `tool.getConf()`.
- `printGenericCommandUsage(PrintStream out)` writes usage text for generic Hadoop options.
- `confirmPrompt(String prompt)` prints a prompt and returns true only for case-insensitive `y` or `yes`; it throws `IOException`.
- Class Javadoc identifies `GenericOptionsParser` as the parser integration and says application-specific options are passed through unmodified.

### `BloomFilter`

- `BloomFilter` extends `Filter` and is public, non-final, and concrete.
- Constructors include a default constructor for `readFields` and `BloomFilter(int vectorSize, int nbHash, int hashType)`.
- Mutating and query APIs include `add(Key)`, `membershipTest(Key)`, boolean-vector operations `and(Filter)`, `or(Filter)`, `xor(Filter)`, complement `not()`, `toString()`, and `getVectorSize()`.
- Serialization APIs are `write(DataOutput)` and `readFields(DataInput)`, both throwing `IOException`.
- Javadocs define standard Bloom-filter semantics: compact set-membership representation, linear construction cost, false positives possible, and false negatives not expected for normal add-only use.

### `CountingBloomFilter`

- `CountingBloomFilter` extends `Filter` and is public final.
- Constructors mirror `BloomFilter`: default for deserialization and `CountingBloomFilter(int vectorSize, int nbHash, int hashType)`.
- It supports `add(Key)`, `delete(Key)`, `membershipTest(Key)`, `approximateCount(Key)`, boolean-vector operations `and(Filter)`, `or(Filter)`, `xor(Filter)`, complement `not()`, `toString()`, and writable serialization with `write`/`readFields`.
- `delete(Key)` documents an invariant: if the key does not belong to the filter, nothing happens.
- `approximateCount(Key)` estimates how many times a key was added. The Javadoc warns that inserting the same key more than 15 times overflows all associated filter positions and increases error rates. It can return zero for absent keys, the true count with probability tied to the error rate, a higher count due to collisions, or a lower count if underflow occurred after deletes.

### `DynamicBloomFilter`

- `DynamicBloomFilter` extends `Filter` and is public concrete.
- Constructors include a zero-argument serialization constructor and `DynamicBloomFilter(int vectorSize, int nbHash, int hashType, int nr)`, where `nr` is the maximum number of keys per row.
- APIs include `add(Key)`, `membershipTest(Key)`, `and(Filter)`, `or(Filter)`, `xor(Filter)`, `not()`, `toString()`, `write(DataOutput)`, and `readFields(DataInput)`.
- Javadocs describe a matrix of standard Bloom-filter rows. When the active row reaches its key threshold, adding another key creates a new row. Membership is true when all hash positions are set in any row.

### `HashFunction`

- `HashFunction` is public final and constructs a multi-output hash adapter.
- Constructor `HashFunction(int maxValue, int nbHash, int hashType)` bounds returned hash values and selects the underlying hash algorithm type from `org.apache.hadoop.util.hash.Hash`.
- `hash(Key)` returns an `int[]` of hash positions for a key.
- `clear()` is explicitly documented as a no-op.

### `RemoveScheme`

- `RemoveScheme` is a public interface used by retouched Bloom filters.
- Constants are public static final `short` values:
  - `RANDOM`: randomly select a bit to reset.
  - `MINIMUM_FN`: select the reset bit expected to generate the minimum number of false negatives.
  - `MAXIMUM_FP`: select the reset bit expected to remove the maximum number of false positives.
  - `RATIO`: select a bit balancing maximum false-positive removal with minimum false-negative introduction.

### `RetouchedBloomFilter`

- `RetouchedBloomFilter` extends `BloomFilter`, implements `RemoveScheme`, and is public final.
- Constructors include a default `readFields` constructor and `RetouchedBloomFilter(int vectorSize, int nbHash, int hashType)`.
- It exposes `add(Key)` plus several overloads of `addFalsePositive`: one `Key`, `Collection`, `List`, and `Key[]`.
- `addFalsePositive(Key)` documents a null invariant: null false-positive information is ignored.
- `selectiveClearing(Key k, short scheme)` applies one of the `RemoveScheme` strategies to remove a false-positive key from the filter.
- It serializes with `write(DataOutput)` and `readFields(DataInput)`, both throwing `IOException`.
- Class Javadoc defines the retouched-filter tradeoff: remove selected false positives while introducing random false negatives and eliminating some other false positives.

### Empty Packages

- `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash` appear as empty package elements at the end of the chunk. The `hash` package is still referenced by Bloom filter constructors through `org.apache.hadoop.util.hash.Hash`, but this particular XML slice does not expose hash package members.

## Control Flow

The XML itself has no executable control flow. The exposed contracts imply several runtime flows:

- Shell-backed operations branch on static platform detection (`osType`, `WINDOWS`, `LINUX`, and peers), choose platform-specific commands or winutils paths, optionally synchronize Windows process creation on `WindowsProcessLaunchLock`, apply timeout and environment inheritance policy from each `Shell` instance, and parse results using token separators.
- String interning is lookup-oriented: callers provide a sample string, the interner checks an equal representative, returns the representative, and either retains it strongly or weakly depending on the selected API.
- `SysInfo.newInstance()` chooses a platform plugin, after which resource consumers poll abstract methods for point-in-time or cumulative metrics. Missing CPU/vcore usage can be represented by `-1` instead of an exception.
- `ToolRunner.run(conf, tool, args)` constructs or uses a `Configuration`, runs generic option parsing, mutates the configuration visible to the tool, calls `tool.setConf(...)`, then invokes `tool.run(...)`. `run(tool, args)` is a convenience path through `tool.getConf()`.
- `confirmPrompt` is synchronous user interaction: print prompt, read input, normalize case, and return true for affirmative `y`/`yes`.
- Basic Bloom-filter flow hashes a `Key` into several positions, sets positions on `add`, checks all positions on `membershipTest`, and combines compatible filters with boolean operations.
- Counting Bloom-filter flow replaces bits with counters. `add` increments hashed buckets, `delete` decrements only when the key is considered present, and `approximateCount` computes the lower observed counter bound while accepting collision and underflow error.
- Dynamic Bloom-filter flow searches for an active row below the `nr` threshold during `add`; if no active row exists, it allocates another Bloom-filter row and inserts there. Membership checks all rows.
- Retouched Bloom-filter flow records known false positives, then `selectiveClearing` chooses a bit to clear according to `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, or `RATIO`.
- Writable flow for Bloom filters is explicit and mutable: default constructors create empty shells for deserialization, then `readFields(DataInput)` populates state; `write(DataOutput)` emits the current state.

## State and Persistence Behavior

The JDiff file persists public API metadata for compatibility checking across Hadoop releases. It does not persist runtime application state.

The `Shell` fields represent a mixture of immutable static process state and mutable per-instance policy. Platform flags, command constants, winutils discovery, setsid availability, and token regexes are global API state. `timeOutInterval` and `inheritParentEnv` are protected mutable instance fields that subclasses and shell runners can use to govern child-process behavior.

`StringInterner` state is a process-local canonicalization cache. Strong interning deliberately keeps representative strings alive for the life of the backing cache, while weak interning allows representatives to disappear when no other references remain. Neither form is a durable persistence mechanism.

`SysInfo` represents live system state rather than durable state. Memory and usage values are snapshots; CPU time and byte counters are cumulative counters since system or interface start, depending on the platform implementation. The abstract contract must tolerate unavailable usage by returning `-1` for selected methods.

`Tool` state is carried mainly through the inherited `Configurable` contract. `ToolRunner` mutates and injects the `Configuration`, so command-line parsing can affect downstream filesystem, security, MapReduce, and application settings before `run` executes.

Bloom-filter classes are persistence-sensitive because they implement Hadoop writable-style serialization. Persisted state includes vector size, hash count, hash algorithm type, bit/counter/matrix contents, dynamic row counts and thresholds, and retouched false-positive bookkeeping. Default constructors explicitly exist to support `readFields`, so deserialization relies on mutable instances.

Approximate structures carry probabilistic state. Bloom filters persist compact membership approximations, not original key sets. Counting filters persist counters but can overflow at repeated counts above the documented small-count range. Retouched filters intentionally trade selected false-positive removal for possible false negatives, so persisted cleared bits affect future membership results.

## Dependencies and Integration Points

This chunk integrates with Java runtime APIs including `String`, `Object`, arrays, primitive numeric types, `java.io.DataInput`, `java.io.DataOutput`, `java.io.IOException`, `java.io.PrintStream`, and Java collections (`Collection`, `List`).

Hadoop integration points include:

- `org.apache.hadoop.conf.Configurable` and `Configuration` for the `Tool`/`ToolRunner` command-line contract.
- `GenericOptionsParser`, referenced by `Tool` and `ToolRunner` Javadocs, as the parser for generic Hadoop options.
- `org.apache.hadoop.util.Shell.OSType` and OS-specific native-command facilities for shell execution.
- Hadoop's Windows support and `winutils`, with the deprecated nullable `WINUTILS` field replaced by exception-raising getter methods outside this chunk.
- `org.apache.hadoop.util.bloom.Filter` and `Key`, which are base abstractions for every Bloom-filter implementation in this slice.
- `org.apache.hadoop.util.hash.Hash`, referenced by hash-type parameters and `HashFunction`, even though the package body is empty in this exact range.
- Hadoop `Writable` conventions through `write(DataOutput)` and `readFields(DataInput)`.

Operational integration points are broad. Shell constants are used by filesystem and utility code that shells out for permission, ownership, group, link, username, `setsid`, and Windows process behavior. `SysInfo` feeds resource monitoring and scheduler-style decisions. `Tool` and `ToolRunner` are the common entrypoint pattern for Hadoop CLI tools. Bloom filters can integrate with caches, map files, network membership summaries, or any code needing compact approximate membership checks.

## Risks and Edge Cases

- This chunk starts mid-`Shell`; method contracts such as actual command execution and winutils getter signatures are outside the assigned line range. Final file-level research must reconcile adjacent chunks before making complete claims about `Shell`.
- JDiff exposes signatures and Javadocs, not implementation bodies. Exact synchronization, validation, serialization layout, hash mixing, and exception messages require source-code validation beyond this XML.
- `WINDOWS_MAX_SHELL_LENGHT` is intentionally misspelled and deprecated. Removing it would break older compiled callers even though the correctly spelled constant exists.
- `WINUTILS` is nullable and deprecated because missed null checks caused support issues. Callers still using it can fail later with null dereferences or unclear Windows errors.
- Public static platform booleans are process-global snapshots; tests or code that expect them to change after `os.name` mutation will be fragile.
- Shell command constants encode platform assumptions. Missing native commands, different command output formats, environment variable parsing differences, or Windows command-line length limits can break callers.
- `WindowsProcessLaunchLock` being public exposes an internal synchronization object. External misuse could introduce lock contention or deadlock with process launches.
- Strong string interning can become a memory leak when applied to high-cardinality or unbounded input. Weak interning avoids that retention but cannot promise long-lived identity stability after garbage collection.
- `SysInfo` values are platform dependent and may be unavailable, stale, permission-limited, or differently scoped in containers. Callers must handle `-1` usage values and `UnsupportedOperationException` from `newInstance()`.
- `ToolRunner.run(Tool, String[])` depends on `tool.getConf()`. Tools with null or mutable shared configurations need predictable initialization.
- `Tool.run` can throw generic `Exception`, so command wrappers need consistent exit-code mapping and logging policies.
- `confirmPrompt` is interactive and can block automation if used in non-interactive contexts.
- Bloom filters have false positives by design. Counting filters add deletion support but introduce overflow and underflow risks. Retouched filters can introduce false negatives intentionally. Dynamic filters grow row state, so serialized size and query cost can increase as more keys are added.
- Boolean operations on filters require compatible vector sizes, hash counts, and hash types. The XML does not show validation details, so misuse may surface as runtime exceptions or invalid probabilistic results.
- `HashFunction.clear()` is a no-op; callers expecting it to reset hidden state will be disappointed.

## Test Signals

Useful validation around this API slice should include:

- JDiff or compatibility tests that verify public fields, deprecated aliases, constructors, method signatures, checked exceptions, and inheritance remain stable for Hadoop Common 2.8.0.
- Cross-platform `Shell` tests for OS detection flags, Windows command-length behavior, `WINUTILS` null/error paths, `setsid` availability, command constants, environment-name validation, timeout behavior, and parent-environment inheritance.
- Concurrency tests around Windows process launch synchronization if Windows execution paths are exercised.
- `StringInterner` tests for identity canonicalization, null/input edge behavior if defined by implementation, strong retention, and weak-reference cleanup under garbage collection.
- `SysInfo` tests using platform fixtures or mocks for memory sizes, CPU counts, CPU usage unavailable values, cumulative CPU time, and network/storage byte counters. Containerized environments should be covered separately from bare-metal assumptions.
- `ToolRunner` tests for generic option parsing, configuration injection into `Tool`, pass-through of application arguments, null configuration behavior, exit-code propagation, exception propagation, generic usage output, and `confirmPrompt` yes/no parsing.
- Bloom-filter tests for add/query semantics, expected false-positive behavior, no false negatives for standard add-only filters, boolean operations on compatible filters, rejection or failure on incompatible filters, `getVectorSize`, `toString`, and writable round trips.
- Counting Bloom-filter tests for delete invariants, approximate counts, absent keys, repeated insertions near and above the documented 15-count overflow threshold, and underflow behavior after deletes.
- Dynamic Bloom-filter tests for row creation once `nr` is reached, membership across multiple rows, serialization preserving row matrix state, and boolean operations with similarly shaped filters.
- Retouched Bloom-filter tests for false-positive recording overloads, null handling, each `RemoveScheme` strategy, selective clearing effects, introduced false-negative risk, and serialization of retouched state.
