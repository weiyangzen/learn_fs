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
