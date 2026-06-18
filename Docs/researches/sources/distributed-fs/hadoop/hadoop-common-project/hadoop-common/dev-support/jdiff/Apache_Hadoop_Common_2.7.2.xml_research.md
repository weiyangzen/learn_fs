# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007159`: lines 1-5873, `Docs/researches/chunks/subset-b-007159_research.md`
- `subset-b-007160`: lines 5874-11915, `Docs/researches/chunks/subset-b-007160_research.md`
- `subset-b-007161`: lines 11916-17986, `Docs/researches/chunks/subset-b-007161_research.md`
- `subset-b-007162`: lines 17987-24376, `Docs/researches/chunks/subset-b-007162_research.md`
- `subset-b-007163`: lines 24377-30557, `Docs/researches/chunks/subset-b-007163_research.md`
- `subset-b-007164`: lines 30558-32555, `Docs/researches/chunks/subset-b-007164_research.md`

## Chunk Research

### subset-b-007159: lines 1-5873

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml lines 1-5873

## Scope

This chunk is the opening slice of the generated JDiff API descriptor for Apache Hadoop Common 2.7.2. It records public API metadata rather than executable implementation: package/class/interface declarations, inheritance, implemented interfaces, constructors, methods, fields, checked exceptions, deprecation markers, and embedded Javadoc.

The visible source range covers:

- `org.apache.hadoop`: `HadoopIllegalArgumentException`.
- `org.apache.hadoop.conf`: `Configurable`, `Configuration`, `Configured`, and `ReconfigurationTaskStatus`.
- Empty package markers for `org.apache.hadoop.crypto`, `org.apache.hadoop.crypto.key.kms`, and `org.apache.hadoop.crypto.random`.
- `org.apache.hadoop.crypto.key`: `KeyProvider` and `KeyProviderFactory`.
- `org.apache.hadoop.fs`: `AbstractFileSystem`, `AvroFSInput`, `BlockLocation`, stream capability interfaces, checksum-related APIs, `CommonConfigurationKeysPublic`, `ContentSummary`, `CreateFlag`, `FileAlreadyExistsException`, `FileChecksum`, and the opening part of `FileContext` through the declaration of `listLocatedStatus`.

The chunk ends inside `FileContext`; adjacent chunks must be merged before forming a complete final report for the full XML file.

## Purpose

The file preserves Hadoop Common 2.7.2's public compatibility contract for JDiff/API-change reporting. This first chunk maps the main runtime configuration API, the key-provider abstraction used by encryption and credentials-aware components, and the filesystem abstraction layer used by Hadoop clients and filesystem implementations.

`Configuration` is the central service for layered XML resources, typed value parsing, variable expansion, final parameters, deprecated key aliases, class loading, credential-provider password lookup, socket address handling, and writable serialization. `AbstractFileSystem` is the implementor-facing filesystem interface behind `FileContext`; `FileContext` is the user-facing API that dispatches operations to the appropriate filesystem for each `Path`. The supporting `org.apache.hadoop.fs` classes describe block locations, checksums, local checksum sidecar files, public configuration keys, content summary/quota display, create semantics, and symlink-aware filesystem operations.

## Important APIs, Types, and Functions

### Hadoop and configuration APIs

- `HadoopIllegalArgumentException` extends `IllegalArgumentException` to distinguish invalid-argument failures raised by Hadoop implementation code from JDK-originated `IllegalArgumentException`.
- `Configurable` defines the standard `setConf(Configuration)` and `getConf()` contract.
- `Configuration` implements `Iterable` and `Writable`. It provides constructors for default loading, explicit `loadDefaults`, and cloning another configuration.
- Global deprecation APIs include `addDeprecations`, several `addDeprecation` overloads, `isDeprecated`, `setDeprecatedProperties`, `dumpDeprecatedKeys`, and `hasWarnedDeprecation`. Deprecated keys can map to replacement keys and aliases.
- Resource APIs include `addDefaultResource`, `addResource` overloads for classpath names, `URL`, `Path`, `InputStream`, named `InputStream`, and another `Configuration`, plus `reloadConfiguration`.
- String accessors include `get`, `getTrimmed`, `getRaw`, `set`, `unset`, `setIfUnset`, `onlyKeyExists`, `setAllowNullValueProperties`, and `getValByRegex`.
- Typed accessors cover `int`, `int[]`, `long`, human-readable byte counts, `float`, `double`, `boolean`, enum values, time durations with `TimeUnit`, regular-expression `Pattern`, integer ranges, string collections, trimmed string collections, and comma-delimited string arrays.
- Secret lookup APIs include `getPassword`, protected `getPasswordFromCredentialProviders`, and protected `getPasswordFromConfig`, allowing credential-provider aliases to replace cleartext configuration values.
- Network helpers include `getSocketAddr`, `setSocketAddr`, and `updateConnectAddr`, including bind-host versus advertised-address handling and wildcard-address replacement.
- Class-loading helpers include `getClassByName`, `getClassByNameOrNull`, `getClasses`, `getClass`, `getInstances`, `setClass`, and configurable class loader accessors.
- Local resource helpers include `getLocalPath`, `getFile`, `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader`.
- Persistence and introspection APIs include `getFinalParameters`, protected synchronized `getProps`, `size`, `clear`, `iterator`, `writeXml(OutputStream)`, `writeXml(Writer)`, static `dumpConfiguration`, `readFields`, `write`, `toString`, `setQuietMode`, and a debugging `main`.
- `Configured` is a simple base class implementing `Configurable`.
- `ReconfigurationTaskStatus` exposes start/end times, status map, `hasTask()`, and `stopped()` for live reconfiguration state.

### Key provider APIs

- `KeyProvider` is an abstract, thread-safe provider of secret key material. It stores a `Configuration` and exposes constants for default cipher and bit length configuration.
- Read-side methods include `getKeyVersion(versionName)`, `getKeys()`, `getKeysMetadata(names)`, `getKeyVersions(name)`, `getCurrentKey(name)`, and `getMetadata(name)`.
- Mutation methods include abstract `createKey(name, material, options)`, generated-material `createKey(name, options)`, `deleteKey(name)`, abstract `rollNewVersion(name, material)`, generated-material `rollNewVersion(name)`, `flush()`, and `close()`.
- Helper methods include static `options(conf)`, protected `generateKey(size, algorithm)`, static `getBaseName(versionName)`, protected static `buildVersionName(name, version)`, static `findProvider(providerList, keyName)`, and `isTransient()`.
- `KeyProviderFactory` is a service-loader-backed factory. It exposes `KEY_PROVIDER_PATH`, abstract `createProvider(URI, Configuration)`, static `getProviders(conf)`, and static `get(uri, conf)`.

### Filesystem implementation APIs

- `AbstractFileSystem` is the implementor-facing filesystem contract. Its constructor validates URI scheme/authority requirements and records filesystem statistics.
- Factory/statistics methods include `createFileSystem(uri, conf)`, static `get(uri, conf)`, protected/static statistics lookup, `clearStatistics`, `printStatistics`, `getAllStatistics`, and instance `getStatistics`.
- URI/path helpers include `checkScheme`, abstract `getUriDefaultPort`, `getUri`, `checkPath`, `getUriPath`, `makeQualified`, `getInitialWorkingDirectory`, and default `getHomeDirectory`.
- Core filesystem methods include server defaults, path resolution, create/createInternal, mkdir, delete, open, truncate, replication, rename, permissions, owner, timestamps, checksum lookup, block-location lookup, file status/link status, filesystem status, list-status iterators, corrupt-block listing, checksum verification, canonical service name, ACL methods, and xattr methods.
- The public docs explicitly align most `AbstractFileSystem` methods with `FileContext` behavior while requiring fully qualified paths or paths belonging to the specific filesystem.
- `AvroFSInput` adapts `FSDataInputStream` or `FileContext`+`Path` to Avro `SeekableInput`, with `length`, `read`, `seek`, `tell`, and `close`.
- `BlockLocation` models block replica metadata: hosts, cached hosts, host:port names, topology paths, offset, length, and corruption state, with copy and multi-array constructors plus setters/getters.
- `CanSetDropBehind` and `CanSetReadahead` are stream capability interfaces using nullable `Boolean`/`Long` to mean default behavior and allowing `UnsupportedOperationException`.
- `ChecksumException` is an `IOException` carrying the position of a checksum failure.
- `ChecksumFileSystem` is a `FilterFileSystem` wrapper that maintains checksum sidecar files. It exposes checksum-file naming/recognition/length calculations, bytes-per-checksum, raw filesystem access, checksum verification/write flags, open/create/append/truncate paths, replication, delete, rename, listing, directory creation, copy helpers, and raw filesystem conversion.

### Configuration constants and filesystem data objects

- `CommonConfigurationKeysPublic` publishes documented common configuration keys and defaults for native library availability, topology scripts, default filesystem URI, disk usage intervals, symlink resolution, trash intervals, local block size, automatic filesystem close, file/FTP implementations, MapFile/SequenceFile/TFile I/O settings, checksum behavior, IPC client/server settings, RPC socket factory and SOCKS proxy, hash type, group mapping/cache settings, security/authentication/authorization, SSL/HTTP policy, RPC protection, SASL property resolver, crypto codec/cipher/JCE/buffer settings, impersonation provider, KMS encrypted-key cache tuning, and secure random settings. It notes that callers should generally prefer `CommonConfigurationKeys`.
- `ContentSummary` implements `Writable` and stores directory/file/content length and quota information, including storage-type quota and consumed-space accessors. Its constructors are documented as superseded by `ContentSummary.Builder`, and output helpers provide quota and human-readable formatting.
- `CreateFlag` defines file creation semantics through combinations such as create, append, and overwrite. Validation methods check generic flag sets, create behavior against path existence, and append-specific constraints.
- `FileAlreadyExistsException` is an `IOException` subclass for create/rename conflicts.
- `FileChecksum` implements `Writable` and defines algorithm name, byte length, raw bytes, checksum options, equality, and hash behavior.

### FileContext APIs in this chunk

- Static factories create `FileContext` instances for default configuration, a supplied `Configuration`, a default filesystem `URI`, a supplied `AbstractFileSystem`, local filesystem contexts, and local contexts with a configuration.
- Context state accessors include `getFSofPath`, `setWorkingDirectory`, `getWorkingDirectory`, `getUgi`, `getHomeDirectory`, `getUMask`, `setUMask`, `resolvePath`, and `makeQualified`.
- File operations visible in this chunk include `create`, `mkdir`, `delete`, `open` overloads, `truncate`, `setReplication`, `rename`, `setPermission`, `setOwner`, `setTimes`, `getFileChecksum`, `setVerifyChecksum`, `getFileStatus`, `getFileLinkStatus`, `getLinkTarget`, `getFsStatus`, `createSymlink`, `listStatus`, `listCorruptFileBlocks`, and the declaration of `listLocatedStatus`.
- Javadocs document rich checked-exception contracts for local and RPC-backed filesystems: `AccessControlException`, `FileAlreadyExistsException`, `FileNotFoundException`, `ParentNotDirectoryException`, `UnsupportedFileSystemException`, `UnresolvedLinkException`, `IOException`, and RPC client/server wrapper exceptions in some method docs.

## Control Flow

`Configuration` has a lazy, layered loading flow. Constructors decide whether default resources are used; callers add resources; subsequent getters trigger resource parsing; later resources override earlier ones unless a parameter has been marked final. Programmatic `set` values overlay resource values. `reloadConfiguration()` clears parsed resource state so resources are reread on next access, while values set through setters remain overlays. `get` and typed accessors apply deprecated-key resolution and, except for raw access, variable expansion against the configuration and then Java system properties.

Deprecation handling is global and lock-conscious. `addDeprecations()` constructs a new deprecation context from the previous one and atomically swaps it, retrying on races. Deprecated key aliases mean a write through an old or replacement key can update related keys, and reads through an old key return the first replacement value that is set.

Password lookup flows from `getPassword(name)` through credential providers first, then conditionally falls back to cleartext configuration. This makes `Configuration` an integration point between normal XML configuration and Hadoop's credential-provider API.

Key-provider flow separates public orchestration from provider-specific persistence. Factories resolve configured URI paths into providers. Callers ask providers for existing metadata/current versions when encrypting or decrypting, create keys with supplied or generated material, roll new key versions, delete keys, and call `flush()` to force buffered changes to the backing store. Helper methods encode/decode the convention that version names derive from a base key name plus version number.

`AbstractFileSystem` factory flow uses the URI scheme to find configuration property `fs.AbstractFileSystem.<scheme>.impl`, instantiate an implementation, and pass the full URI and configuration to it. Client code normally enters through `FileContext`; `FileContext` resolves the filesystem for a `Path`, qualifies paths, applies umask where appropriate, resolves internal symlinks or mount points, and dispatches to `AbstractFileSystem` methods. Implementations receive fully qualified or filesystem-owned paths and return Hadoop filesystem objects such as streams, statuses, checksums, iterators, and block locations.

Create/open/mutation flows are heavily contract driven. `CreateFlag.validate` determines whether create, append, or overwrite combinations are legal relative to path existence. `FileContext.create` applies options such as permissions, buffering, replication, block size, progress callbacks, checksum options, and parent creation before delegating to `AbstractFileSystem.createInternal`. Permission-sensitive operations carry explicit access-control and unsupported-filesystem exceptions.

Symlink flow is documented in detail in `FileContext.createSymlink`. Leading-path symlinks are resolved transparently, while the final path component is treated specially by operations such as delete, rename, link-target lookup, and link-status lookup. Targets may be fully qualified URIs, partially qualified URIs, relative paths, or absolute paths, each resolved against the target filesystem, resolved parent path, or source filesystem authority as appropriate.

Checksum flow can be direct filesystem checksum support or `ChecksumFileSystem` sidecar support. `ChecksumFileSystem` maps data files to checksum-file paths, can verify checksums during reads, write checksum files during creates, derive checksum file length from data length and bytes per sum, and expose the raw underlying filesystem for operations that should bypass checksum wrapping.

## State and Persistence Behavior

The XML file itself is generated persistent API metadata. Runtime state and persistence described by the APIs include configuration resources, writable serialization, key stores, filesystem state, and sidecar checksum files.

`Configuration` maintains mutable resource lists, parsed properties, final-parameter sets, property sources, quiet-mode state, a class loader, global deprecation state, and values set programmatically. It can serialize non-default properties to XML, dump all parameters and metadata to JSON-like writer output, and serialize/deserialize itself as a `Writable`. InputStream resources are explicitly cached and closed after being read, increasing memory use. Local-path helpers may create directories based on configured directory lists and path hash.

Final parameters are persistence-sensitive because once loaded as final from a resource, later resources cannot override them. Variable expansion also means persisted values can depend on other configuration keys or JVM system properties at read time. Property-source tracking preserves the provenance chain of resources or programmatic settings.

`ReconfigurationTaskStatus` is a snapshot-like object containing task start/end times and a status map. It distinguishes no task, running task, and stopped task states.

`KeyProvider` state depends on implementation, but the public contract requires providers to be thread-safe and exposes whether the provider is transient. Key material and metadata persist through provider-specific stores, and `flush()` is the explicit durability boundary for buffered updates. `close()` releases provider resources.

Filesystem APIs operate against durable filesystem namespaces. `AbstractFileSystem` owns a protected statistics object, participates in static per-filesystem statistics tables, and exposes equality/hash semantics tied to its identity. `FileContext` instances carry the active user (`UserGroupInformation`), working directory, umask, and filesystem resolution behavior. `setWorkingDirectory`, `setUMask`, checksum verification toggles, and create options affect subsequent operations through that context or underlying filesystem.

`BlockLocation`, `ContentSummary`, and `FileChecksum` are data carriers whose fields represent persisted or externally observed filesystem metadata. `ContentSummary` and `FileChecksum` implement `Writable`, so their serialization format is part of Hadoop compatibility. `ChecksumFileSystem` persists checksum sidecar files beside data files and must keep those sidecars consistent across create, append, truncate, delete, and rename operations.

## Dependencies and Integration Points

- Java platform dependencies include `java.io` streams/readers/writers/files, `DataInput`, `DataOutput`, `IOException`, `FileNotFoundException`, `java.net.URI`, `URL`, `InetSocketAddress`, `URISyntaxException`, `ClassLoader`, regex `Pattern`, collections, `EnumSet`, `TimeUnit`, and security `NoSuchAlgorithmException`.
- Configuration APIs integrate with Hadoop `Path`, `Writable`, credential providers, classpath resources, system properties, log4j deprecation logging, and class loading for plugin-style components.
- Key-provider APIs integrate with Hadoop encryption, KMS clients, credential-provider-like URI discovery, configured provider paths, secure random/key generation, and provider implementations loaded through Java service discovery.
- `AbstractFileSystem` and `FileContext` integrate with `FileSystem.Statistics`, `FSDataInputStream`, `FSDataOutputStream`, `FsServerDefaults`, `FsStatus`, `FileStatus`, `RemoteIterator`, `Options.CreateOpts`, `Options.ChecksumOpt`, `CreateFlag`, `Progressable`, filesystem permission and ACL types, xattr flags, storage types, `UserGroupInformation`, and Hadoop security access-control exceptions.
- `AvroFSInput` bridges Hadoop filesystem streams to Avro's `SeekableInput`.
- `ChecksumFileSystem` integrates with `FilterFileSystem`, raw filesystem implementations, checksum files, replication/block-size settings, progress callbacks, and local/global checksum configuration.
- `CommonConfigurationKeysPublic` is the shared constant surface consumed by filesystem, IPC/RPC, security, crypto, group mapping, topology, trash, and I/O components.

## Risks and Edge Cases

- This is generated API metadata, not implementation code. Behavioral conclusions are grounded in signatures and Javadocs; exact algorithms, synchronization details, and private state require source-code inspection outside this XML.
- The chunk ends inside `FileContext`. Final per-file research must reconcile later chunks before listing the complete `FileContext` API surface.
- `Configuration` is a high-risk compatibility surface: XML resource precedence, final parameters, deprecated aliases, variable expansion, null-value testing mode, property-source ordering, and typed parsing all affect many Hadoop subsystems.
- Global deprecation maps and default resources are process-wide. Tests or applications that mutate them can create order-dependent behavior unless they isolate or reset global state.
- `addResource(InputStream)` caches stream contents and closes the stream on delayed read. Large streams can increase memory use, and callers must not expect the stream to remain open.
- Typed configuration accessors throw or suppress errors differently. Invalid numeric/time/range/class values can fail at read time, while invalid booleans return defaults. Pattern parsing returns the default for invalid patterns. Tests need to capture these differences.
- `getPassword` can fall back to cleartext configuration if credential providers do not contain an alias. Misconfiguration can silently leave secrets in XML-backed configuration unless fallback behavior is explicitly tested and documented.
- Socket-address helpers rewrite wildcard bind addresses to local host addresses and combine bind-host properties with advertised ports. Multi-homed hosts and unresolved hostnames are common failure points.
- `KeyProvider` implementations must be thread-safe and must handle key material securely. Version-name parsing/building, provider search ordering, generated key size/algorithm choices, transient provider behavior, and `flush()` durability are compatibility and security sensitive.
- `AbstractFileSystem` path validation requires scheme/authority matches or slash-relative names. Incorrect qualification can send operations to the wrong filesystem or reject valid paths.
- `CreateFlag` combinations carry precise create/append/overwrite semantics. Incorrect validation can cause accidental truncation, unexpected append, or false `FileAlreadyExistsException`/`FileNotFoundException`.
- `FileContext` symlink behavior is nuanced. Operations differ on whether they act on the final symlink itself or the target, and target resolution differs for fully qualified, partially qualified, relative, and absolute targets.
- `ChecksumFileSystem` sidecar consistency is fragile around append, truncate, rename, delete, and raw filesystem access. A mismatch can surface later as `ChecksumException` or silent verification bypass if checksum flags are wrong.
- `BlockLocation` exposes mutable arrays through getters/setters in the public API. Callers and implementations must avoid accidental external mutation or stale topology/cache-host data.
- `CommonConfigurationKeysPublic` includes deprecated MapReduce-era keys such as `IO_SORT_MB_KEY` and `IO_SORT_FACTOR_KEY`. Downstream callers may still compile against them, so compatibility changes need explicit migration handling.
- ACL and xattr methods in `AbstractFileSystem` default to public API methods but support may vary by implementation. Unsupported or permission-filtered behavior must be visible as documented `IOException`/access-control failures.

## Test Signals

- API compatibility checks should assert every public package, class/interface, constructor, method, field, inheritance edge, implemented interface, checked exception, visibility, synchronization/static/final marker, and deprecation note in lines 1-5873.
- `Configuration` tests should cover default resource loading on/off, resource precedence, final parameters, `reloadConfiguration`, property-source ordering, InputStream resource caching, quiet mode, XML write/read, writable read/write, JSON-style dump output, regex key lookup, and iterator/size/clear behavior.
- Deprecation tests should cover single and bulk deprecation registration, deprecated-to-new key reads, alias write propagation, multiple replacement-key behavior for deprecated overloads, custom messages, duplicate registration, `setDeprecatedProperties`, and warning tracking.
- Typed accessor tests should cover valid and invalid ints, longs, human-readable byte suffixes, floats, doubles, booleans, enums, time units, regex patterns, integer ranges, comma-delimited strings, trimmed strings, null-value-only keys, default-value behavior, and `NumberFormatException`/`IllegalArgumentException` paths.
- Credential/password tests should cover provider alias success, cleartext fallback, provider miss, provider `IOException`, and behavior when fallback is disabled by configuration.
- Network/class-loading tests should cover bind-host and advertised-address combinations, wildcard replacement, default ports, unresolved hosts, `getClassByNameOrNull` no-exception behavior, interface enforcement in `getClass`/`setClass`, instance creation, and custom class loaders.
- Key-provider tests should cover provider discovery from configured URIs, missing URI schemes, transient provider flags, key create/delete/roll/current-version flows, generated key material, metadata bulk lookup, base/version-name parsing, provider search ordering, `flush()` persistence, `close()`, and concurrent access.
- `AbstractFileSystem` tests should cover URI scheme/authority validation, unsupported filesystem lookup, path qualification/checking, statistics registration/clearing/printing, server defaults, home/initial working directory, create/mkdir/delete/open/truncate/rename, replication, status, block locations, filesystem status, corrupt-block iterators, checksum verification, ACLs, and xattrs.
- `FileContext` tests should cover all visible factory overloads, default/local context creation, UGI propagation, working directory and umask behavior, path resolution, operation dispatch to the correct filesystem, exception mapping, RPC wrapper exceptions where applicable, and interactions with unsupported filesystems.
- Symlink tests should cover creation with and without parent creation, dangling targets, existing-link conflicts, link-status versus file-status behavior, final-component behavior for delete/rename/open/create/mkdir/list/status, and all documented target forms: fully qualified URI, partially qualified URI, relative path, and absolute path.
- Checksum tests should cover checksum filename derivation, checksum-file length calculation, read verification on/off, write checksums on/off, raw filesystem access, append/truncate sidecar updates, checksum file listing/filtering, rename/delete consistency, and `ChecksumException` position reporting.
- Data-object tests should cover `BlockLocation` constructors and mutable array fields, cached hosts, topology paths, corruption flag, `ContentSummary` writable round trips, quota/storage-type formatting and human-readable output, `FileChecksum` equality/hash/bytes/checksum options, and `CreateFlag` validation for every legal and illegal flag combination.

## Cross-Chunk Notes

The merge lane should join this chunk with the following chunks before making final claims about `FileContext`, because this slice stops immediately after `listLocatedStatus` begins. Later chunks should also capture nested types omitted or not separately expanded in this range, such as `Configuration.DeprecationDelta`, `Configuration.IntegerRanges`, `KeyProvider.Options`, `KeyProvider.Metadata`, `KeyProvider.KeyVersion`, and any `ContentSummary.Builder` details if they appear elsewhere in the generated descriptor.

### subset-b-007160: lines 5874-11915

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml lines 5874-11915

## Scope

This chunk is a JDiff API description for Hadoop Common 2.7.2, not executable Java source. It covers the tail of `org.apache.hadoop.fs.FileContext`, then the public API metadata for core `org.apache.hadoop.fs` filesystem abstractions through the beginning of `Syncable`. The chunk includes `FileStatus`, most of `FileSystem`, `FileUtil`, `FilterFileSystem`, stream wrappers, filesystem status/default-value carriers, path/filter interfaces, local filesystem implementations, storage media enums, and the first `Syncable` methods. It ends inside `Syncable.hsync()`, so final details of that interface continue in the next chunk.

## Purpose

The file records the stable client-facing Hadoop filesystem API surface for compatibility comparison. In this range, the API describes how callers discover and instantiate filesystems, qualify and resolve paths, read and write data streams, create, append, rename, truncate, delete, list, glob, snapshot, ACL, xattr, checksum, symlink, and local-copy operations, and inspect metadata such as `FileStatus`, block locations, capacity, server defaults, and storage types.

For research purposes, this chunk is best read as a contract map. Method entries expose signatures, visibility, abstract/deprecated status, declared exceptions, and documentation promises. Implementations live in Java classes elsewhere, but this XML defines the public and protected behavior that downstream Hadoop users, filesystem implementations, and compatibility tests depend on.

## Important APIs, Types, and Functions

### FileContext tail

- `FileContext.deleteOnExit(Path)` marks an existing path for JVM-shutdown deletion and documents access-control, unsupported-filesystem, IO, and RPC-side failure modes.
- `FileContext.resolve(Path)` and `resolveIntermediate(Path)` are protected symlink-resolution helpers, with the latter resolving only components before the final path segment.
- `FileContext.getStatistics(URI)`, `clearStatistics()`, `printStatistics()`, and `getAllStatistics()` expose per-filesystem statistics keyed by URI scheme and authority.
- ACL operations `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, and `getAclStatus` define merge, removal, replacement, and read behavior for file and directory ACLs.
- XAttr operations `setXAttr`, `getXAttr`, `getXAttrs`, `removeXAttr`, and `listXAttrs` define namespaced extended-attribute access. Names must use a namespace prefix such as `user.` and visibility is permission-limited.
- `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY` expose default permission and shutdown-hook constants. The docs note `DEFAULT_PERM` is retained for compatibility after HADOOP-9155 split file and directory defaults.
- The class doc defines the `FileContext` model: default filesystem, working directory, URI-qualified/slash-relative/working-directory-relative paths, umask handling, and server-side defaults for home directory, replication, block size, buffers, encryption, and checksum options.

### Metadata carriers

- `FileStatus` implements `Writable` and `Comparable`. It carries length, type, replication, block size, modification/access times, permission, encryption state, owner, group, path, and optional symlink target.
- `FileStatus.isDir()` is deprecated in favor of `isFile()`, `isDirectory()`, and `isSymlink()`.
- `FileStatus.write(DataOutput)` and `readFields(DataInput)` make the object serializable through Hadoop's `Writable` contract.
- `FileStatus.compareTo`, `equals`, and `hashCode` are path-based according to the docs, so equality is not a full metadata comparison.
- `LocatedFileStatus` extends `FileStatus` with `BlockLocation[]`, giving listing callers file metadata plus block placement.
- `FsServerDefaults` is a writable carrier for server-side defaults: block size, bytes per checksum, write packet size, replication, file buffer size, encrypted transfer flag, trash interval, and checksum type.
- `FsStatus` is a writable capacity snapshot with `capacity`, `used`, and `remaining`.

### FileSystem core

- `FileSystem` is the abstract base class for local and distributed filesystems. It extends `Configured` and implements `Closeable`.
- Instantiation and caching are exposed through `get(URI, Configuration)`, `get(Configuration)`, `get(URI, Configuration, user)`, `newInstance(...)`, `newInstanceLocal(Configuration)`, `getLocal(Configuration)`, `closeAll()`, and `closeAllForUGI(UserGroupInformation)`.
- Default URI handling is exposed through `getDefaultUri(Configuration)` and `setDefaultUri(Configuration, URI/String)`. Scheme resolution uses configuration keys of the form `fs.<scheme>.class`.
- Filesystem identity and path binding APIs include `initialize(URI, Configuration)`, `getScheme()`, abstract `getUri()`, `getCanonicalUri()`, `canonicalizeUri(URI)`, `getDefaultPort()`, `checkPath(Path)`, `makeQualified(Path)`, `getFSofPath(Path, Configuration)`, and deprecated `getName()`/`getNamed()`.
- Creation APIs include many overloads of `create(...)`, abstract permission-aware `create(Path, FsPermission, boolean, int, short, long, Progressable)`, `create(Path, FsPermission, EnumSet<CreateFlag>, ..., ChecksumOpt)`, protected `primitiveCreate(...)`, `createNonRecursive(...)`, and `createNewFile(Path)`.
- Data mutation APIs include abstract `append(Path, int, Progressable)`, `concat(Path, Path[])`, `setReplication(Path, short)`, abstract `rename(Path, Path)`, protected option-based `rename(Path, Path, Options.Rename...)`, `truncate(Path, long)`, abstract `delete(Path, boolean)`, and deprecated single-argument `delete(Path)`.
- Lifecycle deletion APIs include `deleteOnExit(Path)`, `cancelDeleteOnExit(Path)`, and protected `processDeleteOnExit()`. The docs distinguish `FileSystem` close/JVM shutdown behavior from immediate delete.
- Query/list APIs include `exists`, `isDirectory`, `isFile`, deprecated `getLength`, `getContentSummary`, abstract `listStatus(Path)`, filtered and multi-path `listStatus` overloads, `globStatus`, `listLocatedStatus`, `listStatusIterator`, and recursive `listFiles`.
- Local copy APIs include `copyFromLocalFile`/`moveFromLocalFile` overloads, `copyToLocalFile`/`moveToLocalFile`, `startLocalOutput`, and `completeLocalOutput`.
- Default value and status APIs include `getUsed`, `getBlockSize`, `getDefaultBlockSize`, `getDefaultReplication`, `getServerDefaults`, `getFileStatus`, and `getStatus`.
- Integrity and stream behavior APIs include `getFileBlockLocations`, `getFileChecksum(Path[, length])`, `setVerifyChecksum`, and `setWriteChecksum`.
- Namespace and permission APIs include `setPermission`, `setOwner`, `setTimes`, `access(Path, FsAction)`, symlink operations, snapshot operations, ACL operations, and xattr operations.
- Static statistics APIs include synchronized `getStatistics`, `getAllStatistics`, `clearStatistics`, and `printStatistics`, plus class lookup via `getFileSystemClass`.
- Constants include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `LOG`, `SHUTDOWN_HOOK_PRIORITY`, and protected instance `statistics`.

### Utility and wrapper APIs

- `FileUtil` contains local and cross-filesystem helpers: `stat2Paths`, recursive delete helpers, symlink target read, cross-filesystem `copy`, `copyMerge`, local-to-filesystem and filesystem-to-local copy, shell-path conversion, local disk usage, zip/tar extraction, symlink/chmod/chown wrappers, portable permission checks/setters, temp-file creation, file replacement, safe `File.listFiles()` and `File.list()` wrappers, and classpath-jar creation.
- `FileUtil.fullyDelete` explicitly distinguishes symlink-to-file, symlink-to-directory, file, and normal-directory behavior. `fullyDeleteContents` deletes contents and follows a symlinked directory's target contents, a materially different contract.
- `FilterFileSystem` extends `FileSystem` and wraps another filesystem in protected `fs`, optionally transforming schemes with `swapScheme`. The class contract says it delegates all `FileSystem` methods to the contained filesystem unless subclasses override.
- `FsConstants` exposes filesystem URI/scheme constants such as local FS, FTP, viewfs, and `MAX_PATH_LINKS`.

### Streams, paths, filters, and local filesystems

- `FSDataInputStream` wraps an `FSInputStream` in `DataInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, and `CanUnbuffer`. Its contract includes seek, current position, positional read, readFully with EOF semantics, alternate-source seek, byte-buffer reads, enhanced buffer access/release, readahead/drop-behind hints, and unbuffering.
- `FSDataOutputStream` wraps `OutputStream` in `DataOutputStream`, implements `Syncable` and `CanSetDropBehind`, tracks output position, and exposes `sync`, `hflush`, `hsync`, close, and drop-behind hints.
- `FSError` is an `Error` for unexpected native filesystem failures presumed to reflect disk errors.
- `GlobFilter` implements `PathFilter` using POSIX glob patterns with brace expansion and optional user filter composition.
- `Path` represents Hadoop filesystem paths as URI-like names. Constructors support parent/child combinations, strings, URIs, and scheme/authority/path components. Helpers include scheme/authority stripping, merge, Windows absolute-path detection, URI conversion, filesystem lookup, absoluteness/root/name/parent/suffix/depth checks, qualification, and comparable/string/equality behavior. Constants include slash separator, current directory, and a `WINDOWS` flag.
- `PathFilter.accept(Path)` is the listing/globbing predicate interface.
- `PositionedReadable` defines non-mutating positional reads and readFully calls.
- `Seekable` defines cursor-changing `seek(long)` and `getPos()`.
- `ReadOption` is an enum for read options; the actual enum constants are not visible in this JDiff snippet.
- `StorageType` is an enum for storage media, with helpers for transient status, type-quota support, movability, list views, parsing by int/string, `DEFAULT`, and `EMPTY_ARRAY`.
- `LocalFileSystem` extends `ChecksumFileSystem`, exposes `getRaw()`, local path conversion, local copy overrides, checksum-failure reporting that moves files to a bad-file directory, and symlink support.
- `RawLocalFileSystem` extends `FileSystem` and implements raw local disk operations: path conversion, URI/init, open/append/create streams, non-recursive create, rename, truncate, delete, list, mkdirs, working/home directories, status, local-output staging, owner/permission/timestamp changes, symlinks, and link-status/target APIs.

## Control Flow

The XML does not contain method bodies, but the API contracts imply several important call flows.

Filesystem acquisition begins with a URI and `Configuration`. `FileSystem.get` resolves a scheme to a configured implementation class, constructs or retrieves a cached filesystem for the scheme/authority/user, then calls `initialize(URI, Configuration)`. `newInstance` variants bypass the shared cache by returning unique configured instances. Default filesystem selection flows through `fs.defaultFS`/`FS_DEFAULT_NAME_KEY`, and path qualification binds relative or slash-relative paths to the selected URI.

File creation flows from convenience `create` overloads to the abstract permission-aware creation method or protected `primitiveCreate`. The overload set collects defaults for buffer size, replication, block size, progress reporting, create flags, permissions, and checksum options. `primitiveMkdir` similarly exists to support `FileContext` after umask processing, so permissions passed there are documented as absolute.

Read flows compose `FileSystem.open` with `FSDataInputStream`. Consumers can perform sequential reads inherited from `DataInputStream`, reposition with `seek`, perform positional reads that do not necessarily change the stream cursor, use `readFully` for exact-length reads, request alternate data sources, and use byte-buffer or enhanced byte-buffer access if the implementation supports it.

Write flows compose `create` or `append` with `FSDataOutputStream`. `getPos` reports output offset; `hflush` makes client-buffered data visible to new readers; `hsync` is the durable sync contract; deprecated `sync` remains for older callers and forwards conceptually to newer flush/sync semantics.

Listing flows move from `listStatus` to filtered/multi-path convenience wrappers, glob expansion via `GlobFilter`, and located listings that attach block locations. `listStatusIterator` and `listFiles` provide iterator/recursive APIs; docs warn that iterator `hasNext()` or `next()` can surface IO failures after listing has begun.

Delete and shutdown-delete are separate flows. Immediate `delete(Path, recursive)` performs filesystem deletion. `deleteOnExit` records paths for later processing when `FileSystem` instances close during JVM shutdown; `cancelDeleteOnExit` removes that pending state; `processDeleteOnExit` performs recursive deletion of all marked paths.

Wrapper flows in `FilterFileSystem` forward almost every API call to `fs`, preserving the outer API while allowing subclasses to transform behavior. Local wrappers in `LocalFileSystem` add checksum handling over `RawLocalFileSystem`, while `RawLocalFileSystem` maps Hadoop `Path` values to `java.io.File` and local OS operations.

## State and Persistence Behavior

The XML itself is static API metadata consumed by JDiff tooling. The runtime state described by this chunk belongs to the Hadoop filesystem layer:

- `FileSystem` instances hold `Configuration`, URI identity, a protected `statistics` object, checksum verification/write flags, working directory state in implementations, and delete-on-exit registrations. Static caches and statistics tables are process-wide.
- `FileContext` holds namespace context: default filesystem, working directory, and umask. It resolves path forms against that state but depends on filesystem instances for server-side defaults and actual storage.
- `FileStatus`, `LocatedFileStatus`, `FsStatus`, and `FsServerDefaults` are serializable state snapshots. They persist over RPC or serialization through the `Writable` protocol but do not mutate filesystem storage by themselves.
- `Path` stores URI-derived path state and is used as the identity basis for many comparisons. Since `FileStatus.equals`/`hashCode` are path-based, metadata-only changes do not alter equality.
- ACLs, xattrs, snapshots, symlinks, permissions, ownership, timestamps, replication, checksums, and storage policies are persistent filesystem-side state. This chunk defines the client API and exceptions for touching that state; individual filesystem implementations define exact persistence semantics.
- `FileUtil` mutates local disk state for recursive deletion, chmod/chown, symlink creation, archive extraction, replacement, temp files, and permission changes. Some helpers can leave partial results, explicitly documented for recursive delete.

## Dependencies and Integration Points

This API surface depends on core Hadoop and Java types:

- Hadoop configuration and security: `Configuration`, `UserGroupInformation`, `AccessControlException`.
- Hadoop filesystem model: `Path`, `FileStatus`, `BlockLocation`, `ContentSummary`, `RemoteIterator`, `FsPermission`, `FsAction`, `AclStatus`, `CreateFlag`, `Options.Rename`, `Options.ChecksumOpt`, `FileChecksum`, and symlink/snapshot exception types.
- Hadoop IO utilities: `Writable`, `ByteBufferPool`, `DataChecksum.Type`, `Progressable`, stream capability interfaces, and `RemoteIterator`.
- Java platform APIs: `URI`, `File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `ByteBuffer`, `Closeable`, exceptions, arrays, lists, maps, and enum sets.
- Filesystem implementations outside this XML: local, raw local, checksum local, HDFS `DistributedFileSystem`, viewfs, FTP, and any custom implementation configured under `fs.<scheme>.class`.
- RPC-facing behavior is documented for `FileContext` listing/deletion failures, including client/server/unexpected server exception categories when filesystems are accessed over RPC.

## Risks and Edge Cases

- This is compatibility metadata. A signature or deprecation change here may be more important than a small implementation change because downstream applications and third-party filesystems compile against these contracts.
- `FileStatus.equals` and `hashCode` being path-based can surprise callers expecting length, type, permission, owner, or timestamp to participate in equality.
- `FileSystem.rename(Path, Path)` declares a simple boolean contract, while the protected `rename` with options documents non-atomic default behavior and overwrite edge cases. Implementations can vary materially in atomicity.
- `truncate(Path, long)` can return `false` to indicate asynchronous block-length adjustment. Callers must not assume the file is immediately appendable after every successful truncate call.
- `deleteOnExit` stores process-level deferred deletion state. Long-running clients can accumulate state, and shutdown deletion can recursively remove paths long after the initiating code has moved on.
- Recursive local deletion helpers document partial deletion on failure. Symlink behavior differs between `fullyDelete` and `fullyDeleteContents`, creating a sharp edge for cleanup code.
- `FileUtil.symLink`, `chmod`, `setOwner`, and shell path helpers integrate with platform commands and Windows-specific behavior. Security privileges and path quoting are likely failure points.
- XAttr APIs require namespace-prefixed names and return only attributes visible to the logged-in user. Tests must account for permission filtering rather than assuming all xattrs are visible.
- ACL `setAcl` must include base user/group/other entries for permission-bit compatibility; missing base entries are a likely validation failure in implementations.
- `FSDataInputStream` exposes optional capability interfaces. Implementations may throw `UnsupportedOperationException` for readahead, drop-behind, or enhanced byte-buffer reads.
- `FilterFileSystem` pass-through behavior means wrapper subclasses must override every operation whose semantics they need to alter, including newer ACL/xattr/snapshot/symlink methods.
- The chunk ends inside `Syncable`; any final `hsync` documentation and later filesystem APIs must be reconciled with the next chunk before making whole-file conclusions.

## Test Signals

Useful tests around this API surface should include:

- JDiff/API compatibility checks that verify constructors, method signatures, visibility, deprecation strings, exceptions, implemented interfaces, and fields for every type in this chunk.
- `FileSystem` acquisition tests for default URI resolution, scheme-to-class lookup, cached vs `newInstance` behavior, `closeAll`, `closeAllForUGI`, canonical URI/default port behavior, and user-specific lookup.
- Path qualification tests for fully qualified URIs, slash-relative paths, working-directory-relative paths, illegal relative paths with scheme, Windows absolute paths, path merge, parent/name/suffix/depth, and `Path.getFileSystem`.
- File operation contract tests for create overload defaults, create flags, checksum options, non-recursive create parent failure, append optional support, concat, rename overwrite and directory/file mismatch cases, truncate true/false behavior, delete recursive vs non-recursive, and deferred delete-on-exit cancellation.
- Listing tests for missing paths, file vs directory inputs, filters, multi-path arrays, glob syntax including braces/character classes/escaping, sorted glob results, located statuses with block locations, iterator error propagation, and recursive `listFiles`.
- Metadata tests for `FileStatus` serialization, symlink targets, encrypted flag, default permission/owner/group behavior, path-based compare/equality/hashCode, and `LocatedFileStatus` block locations.
- Permission/security tests for `access`, `setPermission`, `setOwner`, `setTimes`, ACL merge/remove/default/remove-all/set/get flows, and xattr set/get/list/remove with namespace and visibility rules.
- Stream capability tests for `FSDataInputStream` seek/position/positional read/readFully EOF semantics, byte-buffer reads, file descriptor access, readahead/drop-behind unsupported behavior, enhanced buffer release, and unbuffering.
- Output stream tests for `FSDataOutputStream.getPos`, close, `hflush` visibility to new readers, `hsync` durability semantics where supported, deprecated `sync`, and drop-behind hints.
- `FileUtil` tests for recursive delete symlink distinctions, partial-failure handling, copy/copyMerge across filesystems, local-to-FS and FS-to-local copy with delete-source and overwrite flags, archive extraction, chmod/chown return codes, portable permission checks, temp-file delete-on-exit, replace-file behavior, and safe list/listFiles IOException behavior.
- Wrapper tests for `FilterFileSystem` delegation across core, symlink, checksum, snapshot, ACL, xattr, and statistics APIs.
- Local filesystem tests for `LocalFileSystem` checksum failure handling and `RawLocalFileSystem` mapping between `Path` and `File`, mkdirs idempotence, local symlink support, ignored access-time setting, and command-based owner/permission changes.

### subset-b-007161: lines 11916-17986

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml lines 11916-17986

## Purpose

This chunk is part 3 of the Hadoop Common 2.7.2 JDiff API XML. It records generated public API metadata, not executable implementation bodies. The useful research signal is the public contract: packages, class/interface names, inheritance, implemented interfaces, method and constructor signatures, checked exceptions, fields, deprecation state, and Javadoc summaries.

The span starts at the tail of `org.apache.hadoop.fs.Syncable`, covers filesystem trash, xattr, FTP, permission/ACL, viewfs, HA, protobuf bridge, HTTP filter-package docs, and a large portion of `org.apache.hadoop.io`, ending inside the `Text.clear()` method documentation. Later chunks must complete the `Text` API and the rest of the file.

## API Inventory

### `org.apache.hadoop.fs` tail

- The chunk begins with the `Syncable` `hsync()`-style contract: flush client-buffered data through the OS to the disk device, with disk cache caveats, and throw `IOException` on error. `Syncable` is the flush/sync capability interface used by Hadoop streams.
- `Trash` extends `Configured` and wraps a configured `TrashPolicy`. Constructors accept a `Configuration` or an explicit `FileSystem` plus `Configuration`. `moveToAppropriateTrash(FileSystem, Path, Configuration)` handles symlinks and mount points by resolving the target volume and moving the deleted path to that volume's trash. Instance APIs expose `isEnabled()`, `moveToTrash(Path)`, `checkpoint()`, `expunge()`, and `getEmptier()`.
- `TrashPolicy` is the abstract pluggable policy base. Implementations must `initialize(Configuration, FileSystem, Path)`, report `isEnabled()`, move paths into trash, create/delete checkpoints, expose `getCurrentTrashDir()`, and provide a superuser emptier `Runnable`. The static `getInstance` factory uses `fs.trash.classname`. Protected state includes `fs`, `trash`, and `deletionInterval`.
- `UnsupportedFileSystemException` is an `IOException` raised when a filesystem scheme/name is unsupported.
- `XAttrCodec` is an enum API for xattr value string conversion. `decodeValue(String)` recognizes `0x`/`0X` hexadecimal, `0s`/`0S` base64, double-quoted text, or bare text. `encodeValue(byte[], XAttrCodec)` emits text, hex, or base64 string forms.
- `XAttrSetFlag` is an enum with static `validate(String xAttrName, boolean xAttrExists, EnumSet flag)` to enforce create/replace semantics and throw `IOException` for invalid extended-attribute writes.
- `org.apache.hadoop.fs.crypto` is present as an empty package in this chunk.

### `org.apache.hadoop.fs.ftp`

- `FTPException` is a runtime wrapper around message/cause variants.
- `FTPFileSystem` extends `FileSystem` and exposes the `ftp` scheme. It initializes from a `URI` and `Configuration`, supports `open`, `create`, `delete`, `listStatus`, `getFileStatus`, `mkdirs`, `rename`, working/home directory accessors, and `setWorkingDirectory`.
- FTP constants include `DEFAULT_BUFFER_SIZE`, `DEFAULT_BLOCK_SIZE`, `FS_FTP_USER_PREFIX`, `FS_FTP_HOST`, `FS_FTP_HOST_PORT`, `FS_FTP_PASSWORD_PREFIX`, and `E_SAME_DIRECTORY_ONLY`. The class also exposes a Commons Logging `LOG`.
- `create` warns that the returned stream must be closed before calling other APIs or later invocations can block. `append` is documented as unsupported.

### `org.apache.hadoop.fs.permission`

- `AccessControlException` extends `IOException` for filesystem permission denial and supports empty, message, and cause constructors.
- `AclEntry` is an immutable ACL entry with type, optional name, `FsAction` permission, and scope. It exposes accessors, `equals`, `hashCode`, `toString`, `parseAclSpec(String, boolean)`, `parseAclEntry(String, boolean)`, and `aclSpecToString(List)`. Parsing supports full set-ACL specs with permissions and remove-ACL specs without permissions.
- `AclEntryScope` and `AclEntryType` are enum APIs for ACL scope and ACL principal/type.
- `AclStatus` is an immutable ACL status value containing owner, group, sticky bit, ordered entries, and base `FsPermission`. It computes effective permissions for an `AclEntry`, including an overload that accepts a permission argument for compatibility with older NameNodes and can throw `IllegalArgumentException` when required permission data is missing.
- `FsAction` is an enum for read/write/execute combinations. APIs include `implies`, `and`, `or`, `not`, `getFsAction(String)`, and public `SYMBOL` text.
- `FsPermission` is a `Writable` representation of Unix-style Hadoop permissions. Constructors accept user/group/other `FsAction` triples, sticky-bit variants, a short mode, another permission, or an octal/symbolic string. APIs cover immutable creation, per-class action access, `fromShort`, `write/readFields/read`, `toShort`, `toExtendedShort`, equality/hash/string conversion, `applyUMask`, `getUMask`, sticky/ACL/encrypted bits, `setUMask`, default directory/file/cache-pool permissions, and symbolic `valueOf`.
- Permission constants include `MAX_PERMISSION_LENGTH`, `DEPRECATED_UMASK_LABEL`, `UMASK_LABEL`, and `DEFAULT_UMASK`. The `getDefault()` Javadoc notes the historical executable-bit behavior for files and points callers to `getDirDefault()` and `getFileDefault()`.

### `org.apache.hadoop.fs.viewfs`

- `org.apache.hadoop.fs.shell.find` is an empty package marker here.
- `NotInMountpointException` extends `UnsupportedOperationException` for paths not mounted through viewfs. It supports path/method and string constructors plus `getMessage()`.
- `ViewFileSystem` extends `FileSystem` and implements the classic `FileSystem` API over a client-side mount table. It supports `viewfs` scheme initialization, URI and path resolution, trash-location lookup, home/working directory handling, append/create/createNonRecursive/delete, block locations, checksum, file status, access checks, listing, mkdirs, open, rename, truncate, ownership, permissions, replication, times, ACL operations, xattr operations, checksum toggles, default block size/replication/server defaults, content summary, child filesystem enumeration, and mount-point listing.
- `ViewFs` extends `AbstractFileSystem` and provides the newer FileContext/AbstractFileSystem surface for the same client-side mount table model. It exposes server defaults, default port, home directory, `resolvePath`, internal create/delete/status/access/open/truncate/rename APIs, symlink support, owner/permission/replication/time updates, checksum toggles, delegation tokens, name validation, ACL operations, xattr operations, and mount-point listing.
- The `ViewFs` package documentation describes mount-table configuration under `fs.viewfs.mounttable.*`, default vs authority-named mount tables, and merge-mount configuration syntax, while noting merge mounts are not implemented yet.

### `org.apache.hadoop.ha`

- `BadFencingConfigurationException` and `FailoverFailedException` describe invalid fencing configuration and failed failover, respectively.
- `FenceMethod` is the operator/plugin contract for fencing an HA service. `checkArgs(String)` validates configured arguments at startup. `tryFence(HAServiceTarget, String)` attempts to prevent a target from making progress and returns success/failure/indeterminate as a boolean, with runtime configuration validation via `BadFencingConfigurationException`.
- `HAServiceProtocol` is the RPC-facing HA primitive contract. It declares `monitorHealth()`, `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(StateChangeRequestInfo)`, and `getServiceStatus()`. It throws `HealthCheckFailedException`, `ServiceFailedException`, `AccessControlException`, and `IOException` as appropriate, and exposes `versionID`.
- `HAServiceProtocolHelper` wraps HA protocol RPC calls and unwraps `RemoteException` into specific checked exceptions for health and state transitions.
- `HAServiceTarget` models a client-side HA administration target. Subclasses provide the IPC address, ZKFC address, `NodeFencer`, and fencing preflight validation. The base class creates HA and ZKFC protocol proxies, exposes final fencing parameters, lets subclasses add fencer environment/script parameters, and reports whether automatic failover is enabled.
- `HealthCheckFailedException` and `ServiceFailedException` are `IOException` subclasses for unhealthy services and failed state-changing operations.

### `org.apache.hadoop.ha.protocolPB` and `org.apache.hadoop.http.lib`

- `HAServiceProtocolPB` and `ZKFCProtocolPB` are protobuf RPC bridge interfaces. Each implements the generated protobuf blocking service interface plus `VersionedProtocol`.
- `org.apache.hadoop.http.lib` has package-level docs for user-selectable web UI filter initializers configured through `hadoop.http.filter.initializers`, including `StaticUserWebFilter`.

### `org.apache.hadoop.io` maps, arrays, bytes, and simple writables

- `AbstractMapWritable` is the shared `Writable`/`Configurable` base for `MapWritable` and `SortedMapWritable`. It maps runtime classes to byte IDs per instance rather than through static tables, supports synchronized class registration/copy, ID/class lookup, configuration access, and `write/readFields`. The class-ID range is documented as 1-127.
- `ArrayFile` extends `MapFile` as a dense integer-to-value file mapping.
- `ArrayPrimitiveWritable` wraps primitive arrays without per-element objects and without copying the underlying array. It exposes declared/actual component type, setter/getter, and `Writable` serialization.
- `ArrayWritable` wraps homogeneous `Writable[]` values with a value class, string-array constructor, `toStrings`, `toArray`, `set/get`, and `write/readFields`. Docs warn reducers often need typed subclasses.
- `BinaryComparable` is the byte-oriented comparable base used by byte-backed writable comparables. Subclasses provide `getLength()` and `getBytes()`, while the base implements byte-wise comparisons, equality, and hashing via `WritableComparator` semantics.
- `BloomMapFile` adds a dynamic Bloom filter to `MapFile` for faster sparse key membership tests. It exposes static `delete(FileSystem, String)` plus `BLOOM_FILE_NAME` and `HASH_COUNT`.
- `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, `LongWritable`, and `ShortWritable` are scalar `WritableComparable` wrappers. Their common contract is default/value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `BytesWritable` is a resizable byte sequence usable as a key or value. It distinguishes logical length from backing capacity, exposes copy/raw byte access, deprecated `get()`/`getSize()` aliases, size/capacity mutation, range setters, serialization, memcmp-style equality/order semantics, and hex-pair `toString()`.
- `ByteBufferPool` is the buffer leasing interface with `getBuffer(boolean direct, int length)` and `putBuffer(ByteBuffer)`.
- `ElasticByteBufferPool` is a synchronized, unbounded caching `ByteBufferPool` that returns the smallest cached buffer with sufficient capacity, creating buffers as needed.
- `Closeable` is a deprecated Hadoop alias for `java.io.Closeable`.

### `org.apache.hadoop.io` serialization helpers and containers

- `CompressedWritable` is an abstract `Writable` base for lazily inflated compressed data. Public `readFields` and `write` are final; subclasses implement `readFieldsCompressed` and `writeCompressed`, and must call `ensureInflated()` before field access.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`, returning the original object if it already is an `OutputStream`.
- `DefaultStringifier<T>` implements `Stringifier<T>` by serializing through Hadoop `SerializationFactory` and base64-encoding the result. It can stringify/fromString instances, close underlying resources, and store/load single objects or arrays from `Configuration` keys.
- `EnumSetWritable<E>` wraps `EnumSet` for `Writable` serialization and is also `Configurable`. Empty/null enum sets require an explicit element type. It implements collection iteration, size, add, reset, equality/hash/string, element-type access, and configuration access.
- `GenericWritable` is an efficient polymorphic wrapper for a fixed set of writable classes declared by subclass `getTypes()`. It avoids writing a class name for every value and passes configuration into wrapped `Configurable` instances before deserialization.
- `MapWritable` extends `AbstractMapWritable` and implements `Map<Writable, Writable>` operations with serialization of dynamic key/value classes.
- `SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap<WritableComparable, Writable>` operations including `firstKey`, `lastKey`, `headMap`, `subMap`, and `tailMap`.
- `ObjectWritable` is a polymorphic `Writable` that records the declared class name and handles writables, strings, primitive types, and arrays. Static `writeObject` has an `allowCompactArrays` flag intended for RPC/internal usage while preserving older persisted-file compatibility when disabled. Static `readObject` overloads reconstruct objects, and `loadClass` consults `Configuration`.
- `Stringifier<T>` is the closeable interface for converting objects to and from string representations.

### `org.apache.hadoop.io` IO utilities, hashes, files, comparators, and sequence files

- `IOUtils` provides stream/channel utilities: multiple `copyBytes` overloads with buffer size, configuration, count, and close behavior; `wrappedReadForCompressedData`; `readFully`; `skipFully`; cleanup/close helpers for streams and sockets; `writeFully` for `ByteBuffer` to `WritableByteChannel` or `FileChannel` at offset; and `listDirectory(FileSystem, Path)` excluding CRC files.
- `MapFile` is a file-backed sorted key/value map stored as a directory containing `data` and `index` files. Static utilities rename, delete, and `fix` corrupt maps by recreating the index, with a `main` entry point. Public constants name the index and data files.
- `MD5Hash` is a 16-byte `WritableComparable` digest wrapper. It can be built from empty state, hex string, or bytes; read/write from data streams; copy another digest; expose digest bytes; compute digests from byte arrays, ranges, input streams, strings, and deprecated `UTF8`; provide thread-local digesters; derive half/quarter digest values; compare, hash, stringify, and set from hex.
- `MultipleIOException` wraps a list of `IOException` values and offers `createIOException(List)` for convenient aggregation.
- `NullWritable` is a singleton zero-data writable comparable whose read/write are no-ops and whose comparison/equality treat all instances as equivalent.
- `RawComparator<T>` extends `Comparator<T>` with direct byte-array comparison for serialized object representations.
- `SequenceFile` APIs in this chunk cover default compression configuration and a large set of static `createWriter` overloads. The preferred modern form is `createWriter(Configuration, Writer.Option...)`; many older overloads taking `FileSystem`, `FileContext`, paths, key/value classes, buffer/replication/block size, compression type, codec, progress, metadata, create flags, and create options are documented as deprecated in favor of the option-based writer.
- `SequenceFile.SYNC_INTERVAL` is the sync-marker interval. The class documentation describes the binary file format: header with version, key/value class names, compression flags and codec, metadata, and sync marker; uncompressed records; record-compressed records; block-compressed records with separate compressed key-length, key, value-length, and value blocks; and sync markers.
- `SetFile` extends `MapFile` as a file-backed set of keys.
- `Text` begins in this chunk. It extends `BinaryComparable` and implements `WritableComparable`. Constructors accept empty, `String`, another `Text`, or a byte array. Covered methods include `copyBytes`, raw `getBytes`, `getLength`, UTF-8 scalar `charAt`, byte-position `find` overloads, `set` from string/byte array/other text/range, `append`, and the start of `clear()` documentation.

## Control Flow and State

The XML only exposes control flow through API contracts and Javadocs. Filesystem delete-to-trash flow is delegated from `Trash` to a configured `TrashPolicy`; `moveToAppropriateTrash` adds resolution through symlinks and mount points so the trash location is on the actual target volume. Checkpoint and expunge operations imply periodic lifecycle behavior through `getEmptier()`.

Viewfs operations flow through a client-side mount table. `ViewFileSystem` and `ViewFs` resolve incoming viewfs paths to mounted target filesystems, then delegate filesystem operations while preserving the appropriate `FileSystem` or `AbstractFileSystem` API shape. Operations that require target metadata expose checked exceptions for access denial, missing files, unresolved links, and IO failures.

HA control flow is explicit: monitoring checks health, transition calls request active/standby state changes, failover/fencing code uses `HAServiceTarget` to build proxies and fencing parameters, and configured `FenceMethod` implementations are attempted by the HA framework. Fencing methods return boolean success rather than throwing for normal failed attempts, reserving `BadFencingConfigurationException` for invalid configuration.

Hadoop IO classes split into mutable value wrappers, file formats, and serialization helpers. Writables are stateful objects whose fields are replaced by `readFields` and emitted by `write`. `CompressedWritable` specifically delays inflation until access. `AbstractMapWritable` maintains per-instance type-ID mappings as part of map state, while `MapFile` and `SequenceFile` define durable on-disk record layouts.

## State and Persistence

Persistent contracts are concentrated in `Writable` implementations and file-format helpers. `FsPermission`, scalar writables, byte/array/map writables, `MD5Hash`, `NullWritable`, `ObjectWritable`, `GenericWritable`, `CompressedWritable`, `EnumSetWritable`, and related classes all expose `write(DataOutput)` and `readFields(DataInput)`.

`MapFile` and `SequenceFile` define durable filesystem artifacts. `MapFile` persists sorted data and an in-memory-loaded index file; `SequenceFile` persists typed key/value streams with optional record or block compression and sync markers. `BloomMapFile` adds a Bloom-filter side file for membership acceleration.

Configuration-backed persistence appears in `DefaultStringifier.store/load` and `FsPermission.getUMask/setUMask`. Runtime-only state appears in `TrashPolicy` fields, `ViewFs` mount tables, HA proxies/fencing parameter maps, and FTP working-directory/connection state. The XML does not prove internal field layouts beyond fields that are part of the public/protected API.

## Dependencies and Integration Points

- Filesystem APIs depend on `Configuration`, `Configured`, `FileSystem`, `AbstractFileSystem`, `FileContext`, `Path`, `FileStatus`, `BlockLocation`, `FileChecksum`, `FsServerDefaults`, `ContentSummary`, `RemoteIterator`, `PathFilter`, `Options.CreateOpts`, `CreateFlag`, `Progressable`, and Java IO exceptions.
- Trash integrates with configurable policy class loading through `fs.trash.classname`, target filesystem resolution, home directories, and superuser emptier scheduling.
- FTP integrates with Apache Commons Logging, FTP host/user/password/port configuration keys, Hadoop stream wrappers, and the `FileSystem` contract.
- ACL and permission APIs integrate with NameNode/file-status metadata, shell parsing of ACL specs, old-NameNode compatibility for effective permissions, and umask configuration.
- Viewfs integrates with mount-table configuration under `fs.viewfs.mounttable.*`, delegated child filesystems, delegation-token collection, ACL/xattr support, symlink handling, and both `FileSystem` and `AbstractFileSystem` client APIs.
- HA APIs integrate with Hadoop RPC/protobuf, `VersionedProtocol`, ZKFC protocols, `NodeFencer`, `HAServiceStatus`, security `AccessControlException`, and service-specific implementations such as HDFS NameNode HA.
- IO APIs integrate with Hadoop serialization, compression codecs, Java `DataInput/DataOutput`, NIO channels and buffers, `MessageDigest`, `Configuration`, `FileSystem`, and `WritableComparator`/`RawComparator` sort paths.

## Risks and Edge Cases

- This is generated JDiff XML; it is authoritative for the generated compatibility snapshot, but it does not show implementation branches, validation details, synchronization beyond method flags, or private fields.
- Trash behavior is path-resolution sensitive. Incorrectly resolving symlinks or mount points can move deleted data into the wrong volume's trash or skip trash when users expect recoverability.
- FTP streams can block later API calls if callers do not close a stream returned by `create`. `append` is advertised but unsupported, so clients must handle `IOException` or unsupported-operation behavior.
- XAttr decoding has multiple string syntaxes; callers must distinguish text from hex/base64 prefixes and quoted strings. Invalid flag combinations in `XAttrSetFlag.validate` are expected to fail early.
- ACL parsing has two modes: specs with permissions and removal specs without permissions. Mixing these can produce incorrect ACL entries or validation failures.
- `FsPermission.toExtendedShort()` can encode values outside the historical `00000-01777` range because ACL/encryption bits may be included; code assuming plain POSIX mode ranges can misinterpret metadata.
- Viewfs is entirely client-side. Mount-table misconfiguration, authority mismatch, incomplete ACL/xattr support on target filesystems, and cross-filesystem rename/delete semantics are key integration risks.
- Fencing methods are operator supplied and may perform destructive external actions. `tryFence` returning false includes indeterminate results, so failover orchestration must treat false conservatively.
- `AbstractMapWritable` allows only 127 distinct classes per map instance. Dynamic or user-controlled map contents can exhaust that ID space.
- `BytesWritable.getBytes()` and `Text.getBytes()` expose backing arrays where only `getLength()` bytes are valid. Using capacity rather than length leaks stale bytes into comparisons, hashes, or output.
- `ArrayPrimitiveWritable` does not copy the wrapped primitive array, so external mutation after wrapping changes serialized state.
- `ObjectWritable` class-name persistence is flexible but expensive and can be compatibility sensitive. Compact array serialization is explicitly not for inter-cluster or persisted-file interchange.
- `SequenceFile` has many deprecated writer overloads; new call sites should prefer `Writer.Option...` to avoid overload ambiguity and compatibility churn. Block-compressed records have a more complex layout and require codec compatibility.
- The chunk ends mid-`Text`; consumers must merge with the next chunk before treating `Text` coverage as complete.

## Test Signals

- API compatibility checks should assert every class, interface, method, constructor, field, visibility, inheritance relationship, implemented interface, deprecation marker, and checked exception recorded in lines 11916-17986.
- Trash tests should cover disabled trash, paths already in trash, symlink and mount-point deletion, checkpoint creation, expunge deletion, and emptier scheduling behavior.
- XAttr tests should cover text, quoted text, hex, base64, invalid encodings, and create/replace flag validation for existing and missing attributes.
- FTP filesystem tests should cover initialization from URI/config, default port, configured credentials, open/create/close ordering, unsupported append, recursive/non-recursive delete, same-directory rename constraints, list/status behavior, and working-directory resolution.
- Permission and ACL tests should cover ACL spec parsing for set vs remove modes, effective permission with and without old-NameNode permission arguments, symbolic/octal permissions, extended short bits, umask parsing including deprecated decimal config, default directory/file/cache-pool permissions, and `Writable` round trips.
- Viewfs tests should cover mount-table initialization, default and named authorities, path resolution, trash locations, delegation to child filesystems, access/list/status/open/create/delete/rename/truncate, ACL/xattr forwarding, symlink support, delegation-token aggregation, and cross-mount edge cases.
- HA tests should cover fencing argument validation, false/true fencing results, fencing parameter maps, proxy creation, health-monitor exceptions, active/standby transition exceptions, `RemoteException` unwrapping by `HAServiceProtocolHelper`, protobuf bridge compatibility, and auto-failover flags.
- IO serialization tests should cover scalar writable round trips and comparisons, `BytesWritable` length vs capacity, `Text` UTF-8 scalar/index behavior for the methods present here, `ArrayPrimitiveWritable` primitive array types, `ArrayWritable` typed subclass usage, map writable dynamic class registration and 127-class limit, `EnumSetWritable` empty/null set element types, `GenericWritable` type whitelist enforcement, `ObjectWritable` primitive/array/writable cases with compact arrays on/off, `MD5Hash` known digests, `IOUtils` copy/skip/read/write boundary conditions, `MapFile.fix` dry-run and repair modes, and `SequenceFile` writer overload compatibility plus uncompressed/record-compressed/block-compressed layout round trips.

### subset-b-007162: lines 17987-24376

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml lines 17987-24376

## Purpose

This chunk is part of the generated Hadoop Common 2.7.2 JDiff API description. It is not implementation code; it records the public API contract emitted for compatibility comparison: packages, classes, interfaces, constructors, methods, fields, visibility, inheritance, implemented interfaces, checked exceptions, deprecation state, and Javadoc text.

The covered API surface runs from the tail of `org.apache.hadoop.io.Text` through core `Writable` APIs, compression codecs and streams, TFile metadata utilities, Hadoop serialization adapters, legacy metrics SPI/Ganglia/log4j metrics support, and the beginning of the metrics2 mutable metrics library. The line range starts in the middle of `Text` and ends in the middle of `MutableQuantiles`, so those two entries are partial for this chunk.

## API Inventory

### `org.apache.hadoop.io` tail and writable core

- The chunk begins inside `Text`, covering UTF-8 byte/string conversion and serialization operations: `toString`, `readFields(DataInput)`, bounded `readFields(DataInput,int)`, `skip(DataInput)`, `readWithKnownLength`, `write(DataOutput)`, bounded `write(DataOutput,int)`, equality/hash, static `decode` and `encode` overloads, static `readString`/`writeString` overloads, UTF-8 validation, `bytesToCodePoint`, `utf8Length`, and `DEFAULT_MAX_LEN`. The class doc describes standard UTF-8 storage with zero-compressed integer lengths and byte-level comparison/traversal utilities.
- `TwoDArrayWritable` is a `Writable` wrapper for `Writable[][]` matrices. It stores the element class and exposes constructors, `toArray`, `set`, `get`, `readFields`, and `write`.
- `VersionedWritable` is an abstract `Writable` base that writes and verifies an implementation version byte. Subclasses implement `getVersion()` and are expected to handle `VersionMismatchException` in custom `readFields` logic when evolving serialized formats.
- `VersionMismatchException` extends `IOException` and reports mismatches between a serialized version byte and the current `VersionedWritable#getVersion()`.
- `VIntWritable` and `VLongWritable` are `WritableComparable` wrappers around variable-length encoded `int` and `long` values. They expose default/value constructors, `set`, `get`, `readFields`, `write`, equality/hash, typed `compareTo`, and `toString`.
- `Writable` defines the base Hadoop binary serialization contract: `write(DataOutput)` and `readFields(DataInput)`. The docs emphasize that `readFields` must completely overwrite object state because Hadoop commonly reuses instances during deserialization.
- `WritableComparable` combines `Writable` and Java `Comparable` for sortable serialized records.
- `WritableComparator` implements `RawComparator` and `Configurable`. It exposes comparator lookup/registration through `get` and `define`, key instantiation through `newKey`, object and raw-byte `compare` paths, byte-array comparison/hash helpers, and primitive readers (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`) used by raw comparators.
- `WritableFactories` maintains per-class `WritableFactory` registrations and can create new `Writable` instances with or without a `Configuration`.
- `WritableFactory` is the one-method factory interface returning a new `Writable`.
- `WritableUtils` is the static helper collection for compressed byte arrays and strings, string arrays, byte-array display, writable cloning/copying, zero-compressed VInt/VLong read/write and sizing, enum serialization by string name, exact skipping, conversion of writables to byte arrays, and bounded `readStringSafely`.

### `org.apache.hadoop.io.compress`

- `BlockCompressorStream` extends `CompressorStream` for block-oriented compression. It writes blocks as uncompressed length plus one or more length-prefixed compressed chunks, supports configurable buffer size and compression overhead, and exposes `write`, `finish`, and protected `compress`.
- `BlockDecompressorStream` extends `DecompressorStream` for the matching block-oriented decode path. It exposes constructors with explicit/default buffers, protected `decompress`, protected `getCompressedData`, and `resetState`.
- `BZip2Codec` implements `Configurable` and `SplittableCompressionCodec`. It supports configuration accessors, output/input stream creation with optional compressor/decompressor instances, split input stream creation with start/end/read-mode arguments, compressor/decompressor factory methods, and default extension reporting.
- `CodecPool` leases and returns reusable `Compressor` and `Decompressor` instances, including overloads for compressor acquisition with `Configuration`. It exposes leased compressor/decompressor counts, which are useful for leak checks.
- `CompressionCodec` is the base codec interface for creating compression output/input streams, identifying and creating compressor/decompressor implementations, and reporting the default filename extension.
- `CompressionCodecFactory` discovers configured codec classes and maps codecs by path extension, class name, and user-friendly name. It also exposes `setCodecClasses`, suffix removal, a CLI `main`, and `LOG`.
- `CompressionInputStream` extends `InputStream` and implements `Seekable`. It wraps an underlying `InputStream`, exposes `resetState`, position/seek methods, `seekToNewSource`, and `maxAvailableData`.
- `CompressionOutputStream` extends `OutputStream`, wraps an underlying `OutputStream`, and defines the compression-stream lifecycle through `finish` and `resetState` in addition to `close`, `flush`, and byte-array `write`.
- `Compressor` is the stream compressor interface modeled after `Deflater`: `setInput`, `needsInput`, `setDictionary`, byte counters, `finish`, `finished`, `compress`, `reset`, `end`, and `reinit(Configuration)`.
- `CompressorStream` is a concrete `CompressionOutputStream` backed by a `Compressor`, output buffer, and closed flag. It exposes write/compress/finish/reset/close behavior and a single-byte `write`.
- `Decompressor` is the stream decompressor interface modeled after `Inflater`: `setInput`, `needsInput`, `setDictionary`, `needsDictionary`, `finished`, `decompress`, `getRemaining`, `reset`, and `end`.
- `DecompressorStream` is a concrete `CompressionInputStream` backed by a `Decompressor`, buffer, EOF flag, and closed flag. It exposes single-byte and byte-array reads, protected decompress/data-fetch hooks, stream checks, reset, skip, availability, close, and mark/reset behavior.
- `DefaultCodec` implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`, providing default compression stream/decompressor factories and direct decompressor creation.
- `DirectDecompressionCodec` marks codecs that can produce a `DirectDecompressor` for direct `ByteBuffer` decompression.
- `DirectDecompressor` defines `decompress(ByteBuffer src, ByteBuffer dst)`.
- `GzipCodec` extends `DefaultCodec` and overrides stream, compressor/decompressor, direct decompressor, type, and extension methods for gzip.
- `SplitCompressionInputStream` is an abstract `CompressionInputStream` for compressed ranges whose start/end may be adjusted to codec boundaries. It exposes protected setters and public `getAdjustedStart`/`getAdjustedEnd`.
- `SplittableCompressionCodec` extends `CompressionCodec` with split-aware `createInputStream(InputStream,Decompressor,long,long,READ_MODE)`. The docs explain that this is for codecs that can decompress from arbitrary positions and therefore support parallel processing of compressed input splits.

### `org.apache.hadoop.io.file.tfile`

- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are `IOException` types for TFile named metadata block conflicts and missing blocks.
- `RawComparable` exposes a byte-array slice through `buffer`, `offset`, and `size` so external raw comparators can compare byte ranges without object conversion.
- `TFile` is documented as a type-less byte key/value container with block compression, named metadata blocks, sorted or unsorted keys, and key/file-offset seeking. This chunk exposes static `makeComparator`, `getSupportedCompressionAlgorithms`, `main`, constants `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, `COMPARATOR_MEMCMP`, and `COMPARATOR_JCLASS`. Its docs also describe key size limits, chunked values, index memory footprint, configuration knobs for chunk and FS buffer sizes, and performance guidance.
- `Utils` contains TFile support helpers: variable-length integer/long read/write, Text-format string read/write, and lower/upper-bound binary search overloads for sorted collections and raw comparable data.

### `org.apache.hadoop.io.serializer`

- `JavaSerialization` is a serialization adapter for Java `Serializable` objects.
- `JavaSerializationComparator` extends `DeserializerComparator` for comparing Java-serialized objects through deserialization.
- `WritableSerialization` extends `Configured` and provides `Serialization` for Hadoop `Writable` types, delegating actual object data to each writable's `write`/`readFields` methods.
- `AvroReflectSerializable` is a marker interface for classes eligible for Avro reflect serialization.
- `AvroReflectSerialization` extends `AvroSerialization` and exposes `AVRO_REFLECT_PACKAGES`, the configuration key for package allow-listing. The docs state that classes are accepted when they implement the marker interface or are in configured packages.
- `AvroSerialization` is the configured base for Avro serialization providers and exposes `AVRO_SCHEMA_KEY`.
- `AvroSpecificSerialization` extends `AvroSerialization` for Avro specific classes.

### Legacy metrics and log metrics

- `EventCounter` extends log4j `AppenderSkeleton`. It counts log events by level and exposes appender lifecycle methods `append`, `close`, and `requiresLayout`.
- `GangliaContext` extends `AbstractMetricsContext` to emit legacy metrics to Ganglia over UDP. It exposes `close`, `emitMetric`, metadata helpers (`getUnits`, `getSlope`, `getTmax`, `getDmax`), XDR encoders (`xdr_string`, `xdr_int`), and state fields for the byte buffer, current offset, configured metric servers, and datagram socket.
- `AbstractMetricsContext` is the legacy metrics SPI base. It implements `MetricsContext`, initializes from `ContextFactory`, reads attributes and attribute tables, starts/stops monitoring, creates records, registers/unregisters periodic `Updater`s, exposes all buffered records, emits records through an abstract `emitRecord`, optionally flushes after each period, updates/removes internal metric rows, and manages the monitoring period through `getPeriod`, protected `setPeriod`, and `parseAndSetPeriod`.
- `CompositeContext` extends `AbstractMetricsContext` as a context that can fan metrics out to multiple child contexts.
- `MetricsRecordImpl` implements legacy `MetricsRecord`. It stores tags and metrics, supports typed `setTag` overloads for string/int/long/short/byte, `removeTag`, typed `setMetric` overloads for int/long/short/byte/float, typed `incrMetric` overloads for the same numeric types, and delegates `update`/`remove` back to its `AbstractMetricsContext`.
- `MetricValue` wraps a `Number` as either absolute or incremental, with `ABSOLUTE`, `INCREMENT`, `isIncrement`, `isAbsolute`, and `getNumber`.
- `NoEmitMetricsContext`, `NullContext`, and `NullContextWithUpdateThread` are no-output metrics contexts. `NoEmitMetricsContext` preserves records for polling, `NullContext` is the default do-nothing context, and `NullContextWithUpdateThread` samples periodically without emitting so pollers such as JMX see updated values.
- `OutputRecord` is the emitted legacy metrics record view. It exposes tag/metric names, individual tag/metric lookup, and copy accessors for the underlying tag and metric maps.
- `Util.parse(String,int)` parses space/comma-separated host or host:port metrics server specs, defaulting to localhost with a supplied port.

### `org.apache.hadoop.metrics2`

- `AbstractMetric` is the immutable metrics2 metric base implementing `MetricsInfo`. It exposes metric name/description/info, abstract `value`, abstract `type`, visitor dispatch, equality/hash, and string conversion.
- `MetricsCollector` creates `MetricsRecordBuilder`s by record name or `MetricsInfo`.
- `MetricsException` is the runtime wrapper for metrics failures, with message, cause, and message-plus-cause constructors.
- `MetricsFilter` is a metrics2 plugin that accepts or rejects names, tags, tag iterables, and whole metrics records.
- `MetricsInfo` supplies immutable name and description metadata for metrics and tags.
- `MetricsPlugin` initializes metrics framework plugins from `SubsetConfiguration`.
- `MetricsRecord` is an immutable timestamped metrics snapshot with record name, description, context, unmodifiable tag collection, and immutable metric iterable.
- `MetricsRecordBuilder` is the fluent builder API for metrics records. It adds tags, prebuilt metric/tag objects, context, integer/long counters, integer/long/float/double gauges, and returns the parent collector or ends the record.
- `MetricsSink` consumes `MetricsRecord`s through `putMetrics` and `flush`.
- `MetricsSource` publishes metrics through `getMetrics(MetricsCollector, boolean all)`.
- `MetricsSystem` implements `MetricsSystemMXBean` and provides source registration/unregistration, immediate publishing, and shutdown.
- `MetricsSystemMXBean` controls metrics system start/stop, MBean start/stop, and exposes current config text.
- `MetricsTag` is an immutable tag implementing `MetricsInfo`, with name/description/info/value accessors and equality/hash/string behavior.
- `MetricsVisitor` receives typed gauge and counter values for integer, long, float, and double metrics.
- `Metric` and `Metrics` are annotation interfaces used by the metrics2 annotation-based source machinery.
- `GlobFilter` and `RegexFilter` extend `AbstractPatternFilter`, compiling glob or regex strings to `Pattern`s.
- `DefaultMetricsSystem` is an enum singleton facade exposing `values`, `valueOf`, `initialize`, `instance`, and `shutdown`.
- `Interns` interns metrics metadata and tags through `info` and `tag` overloads to reduce duplicate object allocation.
- `MetricsRegistry` owns mutable metrics and tags for a source. It exposes registry metadata, metric/tag lookup, counter/gauge factory overloads, quantile/stat/rate factory overloads, synchronized sample addition by metric name, context tagging, tag addition with optional override, synchronized snapshot emission, and `toString`.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` define and implement monotonically increasing mutable counters. Concrete classes expose `incr`, delta `incr`, typed `value`, and `snapshot`.
- `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong` define and implement mutable gauges. Concrete classes expose typed `value`, `incr`, delta `incr`, `decr`, delta `decr`, `set`, and `snapshot`.
- `MutableMetric` is the abstract mutable metric base with abstract `snapshot(builder, all)`, convenience `snapshot(builder)`, changed-flag management through `setChanged`/`clearChanged`, and `changed`.
- The chunk ends inside `MutableQuantiles`, showing its interval-based constructor, synchronized `snapshot`, synchronized `add(long)`, `getInterval`, static `quantiles`, protected `previousSnapshot`, and the beginning of documentation for online estimates over a stream of long values.

## Control Flow and State

This XML records public contract rather than executable control flow. The main control-flow obligations are therefore encoded in method contracts and lifecycle pairs:

- Writable objects are written to `DataOutput` and read back from `DataInput`; reusable object instances must have all relevant state replaced in `readFields`.
- `Text`, `WritableUtils`, `VIntWritable`, and `VLongWritable` share the zero-compressed variable-length integer convention. Readers consume length prefixes and then bounded byte/string payloads; writer methods return encoded lengths where documented.
- Raw comparison flows in `WritableComparator` avoid object materialization where possible: callers pass two serialized byte ranges, helper methods parse primitive values directly, and typed comparators can fall back to object `compare`.
- Compression output flows from codec-created streams to `Compressor` instances, `finish`, and close/reset. Decompression flows from codec-created streams through `Decompressor`, repeated `needsInput`/`setInput`/`decompress` cycles, and reset/end cleanup. Split codecs may adjust requested input start/end positions before returning a stream.
- TFile contracts describe a block-oriented key/value container with optional sorted-key lookup, metadata blocks, and configurable chunking/buffering. The API surface in this chunk is primarily static utilities and constants, while the docs describe the larger reader/writer flow.
- Legacy metrics flow from `MetricsRecordImpl` mutation to `update`/`remove` calls on `AbstractMetricsContext`; contexts periodically call registered `Updater`s, convert internal rows to `OutputRecord`s, call subclass `emitRecord`, and then `flush`.
- Metrics2 flow is builder/collector oriented. A `MetricsSource` emits records to a `MetricsCollector`; records are built with `MetricsRecordBuilder`; mutable metrics and registries snapshot changed or all metrics into builders; sinks receive immutable `MetricsRecord`s.

Stateful APIs in this chunk include writable object payloads, codec pools and leased compressor/decompressor counts, stream buffers and closed/EOF flags, TFile comparator/compression configuration, metrics context tables and update thread state, Ganglia UDP buffer/socket state, metrics registry maps/tags, mutable metric values, changed flags, and quantile snapshots.

## Persistence and Serialization

The `org.apache.hadoop.io` portion is explicitly about Hadoop's binary persistence contract. `Writable` implementors persist state through `write(DataOutput)` and restore through `readFields(DataInput)`. `VersionedWritable` adds a version byte to serialized forms and raises `VersionMismatchException` on incompatible input. `Text` and `WritableUtils` use zero-compressed lengths and UTF-8 bytes; bounded read/write methods and `readStringSafely` are guardrails for oversized serialized data.

Compression stream APIs transform persisted or network byte streams but do not themselves define durable object formats except for block compressor stream framing. TFile is a durable container format with compressed data blocks, metadata blocks, indexes, key/value bytes, and configuration-dependent chunking/buffering. Serialization adapters bridge Java serialization, Hadoop Writables, and Avro reflect/specific formats.

Legacy metrics and metrics2 APIs mostly represent runtime telemetry state. `MetricsRecordImpl`, `OutputRecord`, `AbstractMetric`, `MetricsTag`, `MetricsRecord`, `MetricsRegistry`, and mutable metrics model current or snapshotted metrics rather than durable storage. Emission to Ganglia is network transmission, not local persistence.

## Dependencies and Integration Points

- Writable APIs integrate with Java `DataInput`/`DataOutput`, Hadoop `Configuration`, `RawComparator`, reflection-based instantiation, and downstream storage/RPC formats that rely on stable byte encodings.
- Compression APIs integrate with `InputStream`/`OutputStream`, `Seekable`, `Configuration`, codec implementations, native and pure-Java compressor/decompressor backends, direct `ByteBuffer` decompression, and split input processing in MapReduce-style readers.
- `BZip2Codec`, `GzipCodec`, and `DefaultCodec` are selected by `CompressionCodecFactory` through configured classes, filename extensions, class names, or codec names.
- TFile integrates with compression codecs, raw comparators, filesystem streams, and configuration keys controlling chunk and buffer sizes.
- Serializer classes integrate with Hadoop's `Serialization` framework, Java serialization, `Writable` implementations, Avro reflect/specific classes, and schema/package configuration keys.
- Legacy metrics integrate with `ContextFactory`, `MetricsContext`, `MetricsRecord`, `Updater`, log4j appenders, Ganglia UDP/XDR protocol expectations, and polling consumers such as `MetricsServlet` or JMX-style readers.
- Metrics2 integrates with `SubsetConfiguration`, metrics sources, sinks, collectors, builders, visitors, filters, MXBeans, annotations, interned metadata, and mutable metric registries.

## Risks and Edge Cases

- The source is generated JDiff metadata. It is strong evidence for the published Hadoop Common 2.7.2 API surface but does not prove implementation behavior, private state layout, or runtime bugs.
- The chunk boundaries are partial: `Text` starts before line 17987 and `MutableQuantiles` continues after line 24376. Consumers should merge adjacent chunk research before making whole-class claims for those two types.
- Writable deserialization is mutation-based. A `readFields` implementation that leaves stale fields behind can corrupt reused objects. Bounded text/string APIs are important for defending against malformed or oversized serialized inputs.
- Variable-length integer encodings must preserve exact byte compatibility. Off-by-one errors in first-byte sign/length decoding can break persisted data, sort order, and cross-version RPC/storage compatibility.
- Raw comparators depend on serialized byte layout. Changing a writable's encoding without updating comparators can produce inconsistent sorting or grouping.
- Compression codecs have lifecycle-sensitive resources. Failing to `finish`, `reset`, return pooled compressors/decompressors, or call `end` can leak native state or corrupt concatenated streams. Split compression requires careful start/end adjustment or readers may miss or duplicate records.
- Codec discovery by extension/name can be ambiguous if configured codecs overlap. Factory tests should confirm intended precedence and suffix removal.
- TFile performance and memory use depend on block size, chunk size, compression choice, and index cardinality. The docs warn about random-access costs for large blocks and index memory growth with many blocks or metadata blocks.
- Legacy metrics contexts are synchronized in several mutation paths but still depend on periodic background updates and global configuration. Null/no-emit contexts can hide missing metrics output in production if selected unexpectedly.
- Ganglia emission uses UDP and manual XDR buffer encoding; truncation, bad offsets, server spec parsing, and socket lifecycle are likely failure points.
- Metrics2 mutable metrics use changed flags and snapshot filtering. Forgetting to set or clear the changed flag can omit updates or repeatedly emit unchanged values. Counter/gauge synchronization differs by concrete class and overload, so concurrent updates should be tested under expected source usage.
- Filter and annotation APIs are extension points. Misconfigured glob/regex filters or metrics annotations can silently suppress records.

## Test Signals

- API compatibility checks should assert all documented classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, visibility, deprecation markers, and checked exceptions in this line range remain stable for Hadoop Common 2.7.2.
- Writable tests should cover `Text` UTF-8 encode/decode/validation, bounded reads/writes, zero-length and malformed input, `WritableUtils` VInt/VLong boundary values, enum round trips, exact skip failures, `readStringSafely` negative/oversized lengths, `WritableFactories` configured construction, and `WritableComparator` raw primitive reads/comparisons.
- Versioned writable tests should verify matching version reads, mismatched version exceptions, and subclass handling of old serialized versions.
- Compression tests should cover codec factory lookup by path/name/class, pooled compressor/decompressor lease/return counts, stream `finish`/`close`/`resetState`, block framing round trips, direct decompression where supported, split BZip2 reads with adjusted start/end offsets, concatenated decompressor streams, and resource cleanup after exceptions.
- TFile tests should exercise comparator creation, supported compression algorithm names, metadata block duplicate/missing exceptions, variable-length utilities, lower/upper-bound searches, and documented configuration effects on chunk/buffer sizing.
- Serialization tests should cover Java serializable acceptance, writable serialization/deserialization, Avro reflect package/marker acceptance, Avro schema configuration, and comparator behavior over serialized payloads.
- Legacy metrics tests should cover context initialization attributes, period parsing, updater registration/removal, start/stop monitoring idempotence, record tag/metric mutation by type, absolute versus incremental values, `update`/`remove` row matching, no-emit and null context behavior, Ganglia server parsing, XDR encoding, socket close, and log4j event counting by level.
- Metrics2 tests should cover immutable metric/tag equality, record builder fluent chaining, collector/source/sink interactions, filter decisions for names/tags/records, plugin initialization, metrics system registration/unregistration/shutdown, MXBean operations, interned metadata identity, registry duplicate/override tag behavior, counter/gauge mutation and snapshot output, changed-flag semantics, and quantile add/snapshot behavior once adjacent chunks provide the full class entry.

### subset-b-007163: lines 24377-30557

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml lines 24377-30557

## Scope

This chunk is a JDiff API-description slice for Hadoop Common 2.7.2. It starts at the tail of the `org.apache.hadoop.metrics2.lib.MutableQuantiles` documentation, covers metrics helper/sink/util APIs, network topology and socket factory APIs, the deprecated Hadoop Record I/O runtime and compiler surface, selected security mapping and credential-provider APIs, HTTP delegation-token authentication APIs, and ends inside the beginning of `org.apache.hadoop.service.AbstractService`.

Because the source is generated XML API metadata rather than executable Java source, control-flow and state notes are inferred from public method contracts, inheritance, synchronization flags, exceptions, and documentation text. The slice is still operationally useful: it captures the public compatibility contract that Hadoop clients, services, metrics sinks, network topology providers, record-compiler tools, and security-token integrations were expected to preserve in the 2.7.2 common module.

## Purpose

The metrics portion defines mutable rate/statistic primitives and sinks used by Hadoop daemons to publish operational measurements. `MutableRate`, `MutableRates`, and `MutableStat` accumulate latency/throughput samples and snapshot them into `MetricsRecordBuilder`; `FileSink` and `GraphiteSink` export records to local files or Graphite; `MBeans`, `MetricsCache`, and `Servers` help expose, cache, and address metrics.

The network portion defines pluggable host-to-rack resolution and socket creation. `DNSToSwitchMapping` is the contract used by block placement and other topology-aware code. `AbstractDNSToSwitchMapping`, `CachedDNSToSwitchMapping`, `ScriptBasedMapping`, and `TableMapping` provide common mapping, caching, script-based, and file/table-based behavior. `StandardSocketFactory` and `SocksSocketFactory` are `javax.net.SocketFactory` implementations used by client networking, with the SOCKS variant configurable through Hadoop `Configuration`.

The Record I/O portion documents Hadoop's older serialization system, explicitly deprecated in favor of Avro across many classes. It includes binary, CSV, and XML `RecordInput`/`RecordOutput` implementations, `Buffer`, `Record`, `RecordComparator`, low-level varint helpers, type metadata classes, compiler AST/type classes, an Ant task, and JavaCC-generated parser/lexer classes.

The security portion defines group and ID mapping provider contracts, an authentication-method enum entry point, credential-provider abstractions for secret storage, and web delegation-token clients/authenticators. These APIs integrate Hadoop identity, alias-backed credentials, HTTP authentication, Kerberos/SPNEGO fallback, pseudo authentication, proxy-user `doAs`, and delegation-token lifecycle operations.

The final service portion begins `AbstractService`, Hadoop's base class for lifecycle-managed components. In this chunk it exposes service construction, state/failure accessors, configuration setting, `init`, `start`, `stop`, `close`, failure recording, and the beginning of stop-wait behavior.

## Important APIs, Types, and Functions

- `org.apache.hadoop.metrics2.lib.MutableRate` extends `MutableStat` as a convenience metric for throughput measurement.
- `MutableRates` extends `MutableMetric` and provides `init(Class protocol)`, `add(String name, long elapsed)`, and `snapshot(MetricsRecordBuilder rb, boolean all)`. Its `init` method pre-registers protocol methods so JMX output includes all rates in the first snapshot.
- `MutableStat` extends `MutableMetric`, has constructors with metric name/description/sample/value labels and optional extended statistics, synchronized `setExtended(boolean)`, synchronized `add(long numSamples, long sum)`, synchronized `add(long value)`, synchronized `snapshot(...)`, and `resetMinMax()`.
- `FileSink` and `GraphiteSink` both implement `MetricsSink` and `Closeable` with `init(SubsetConfiguration)`, `putMetrics(MetricsRecord)`, `flush()`, and `close()`.
- `MBeans.register(String serviceName, String nameName, Object theMbean)` registers an MBean under the standard `hadoop:service=<serviceName>,name=<nameName>` naming convention and returns the `ObjectName`; `unregister(ObjectName)` removes it.
- `MetricsCache` has default and max-record constructors, `update(MetricsRecord, boolean includingTags)`, `update(MetricsRecord)`, and `get(String name, Collection tags)` for sinks that need dense records rather than sparse metric deltas.
- `Servers.parse(String specs, int defaultPort)` parses space/comma-separated `hostname` or `hostname:port` specifications, defaulting to localhost at the supplied port when specs are null.
- `DNSToSwitchMapping` defines `resolve(List names)`, `reloadCachedMappings()`, and `reloadCachedMappings(List names)` for pluggable rack/switch lookup.
- `AbstractDNSToSwitchMapping` implements `DNSToSwitchMapping` and `Configurable`; it stores configuration, reports whether a mapping is single-switch, exposes diagnostics through `getSwitchMap()` and `dumpTopology()`, and provides `isMappingSingleSwitch(DNSToSwitchMapping)`.
- `CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping`, caches host-to-switch answers, exposes its `rawMapping` field, delegates unresolved names, and can reload all or selected cached mappings.
- `ScriptBasedMapping` extends the cached mapping with script-backed topology lookup. It has constructors for default configuration, raw mapping, and explicit `Configuration`, plus `setConf`, `getConf`, `toString`, and `NO_SCRIPT`.
- `TableMapping` extends `CachedDNSToSwitchMapping` and supports configuration-driven, reloadable host/rack mappings from a table file.
- `ConnectTimeoutException` extends `SocketTimeoutException` for `NetUtils.connect(...)` timeout failures.
- `SocksSocketFactory` and `StandardSocketFactory` provide the five standard `createSocket` overloads plus equality/hash behavior; `SocksSocketFactory` also implements `Configurable` and can be built from a supplied `Proxy`.
- `RecordInput` and `RecordOutput` define the serialization contract: primitive read/write methods, `Buffer` support, and start/end markers for records, vectors, and maps.
- `BinaryRecordInput`, `CsvRecordInput`, and `XmlRecordInput` implement `RecordInput`; `BinaryRecordOutput`, `CsvRecordOutput`, and `XmlRecordOutput` implement `RecordOutput`.
- `BinaryRecordInput.get(DataInput)` and `BinaryRecordOutput.get(DataOutput)` are documented as thread-local helpers, so caller code may reuse per-thread wrappers over changing underlying data streams.
- `Buffer` is a comparable, cloneable byte-sequence type with constructors over empty storage, full byte arrays, and byte ranges; mutation/access methods include `set`, `copy`, `get`, `getCount`, `getCapacity`, `setCapacity`, `reset`, `truncate`, and two `append` overloads.
- `Record` is an abstract generated-record base class implementing `WritableComparable` and `Cloneable`, with tagged and untagged `serialize`/`deserialize`, plus Hadoop `write(DataOutput)` and `readFields(DataInput)`.
- `RecordComparator` extends `WritableComparator` and registers optimized comparators for `Record` implementations through `define(Class, RecordComparator)`.
- `org.apache.hadoop.record.Utils` provides float/double parsing from byte arrays, zero-compressed variable-length integer and long read/write helpers, encoded-length calculation, and lexicographic byte comparison.
- `org.apache.hadoop.record.compiler` includes `CodeBuffer`, `Consts`, primitive/composite `JType` classes (`JBoolean`, `JBuffer`, `JByte`, `JDouble`, `JFloat`, `JInt`, `JLong`, `JMap`, `JRecord`, `JString`, `JVector`), `JField`, and `JFile.genCode(String language, String destDir)` for record DDL code generation.
- `RccTask` is an Ant `Task` with setters for language, file, fail-on-error, destination directory, file sets, and `execute()` to run the record compiler.
- `org.apache.hadoop.record.compiler.generated.Rcc` is the JavaCC parser driver with constructors over input streams, readers, and token managers; parsing methods include `Input`, `Include`, `Module`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`.
- Generated compiler support includes `RccConstants` token IDs and lexical states, `RccTokenManager`, `SimpleCharStream`, `Token`, `ParseException`, and `TokenMgrError`.
- `org.apache.hadoop.record.meta` provides `TypeID` constants for primitive record types, `MapTypeID`, `VectorTypeID`, `StructTypeID`, `FieldTypeInfo`, `RecordTypeInfo`, and metadata `Utils.skip(DataInput, byte)` for skipping serialized values by type.
- `GroupMappingServiceProvider` defines group lookup plus cache refresh/add methods and `GROUP_MAPPING_CONFIG_PREFIX`.
- `IdMappingServiceProvider` maps user/group names to numeric IDs and back, with strict and unknown-tolerant variants: `getUid`, `getGid`, `getUserName`, `getGroupName`, `getUidAllowingUnknown`, and `getGidAllowingUnknown`.
- `UserGroupInformation.AuthenticationMethod` is an enum surface with `values`, `valueOf(String)`, and `getAuthMethod()` returning `SaslRpcServer.AuthMethod`.
- `CredentialProvider` defines transient-vs-persistent provider detection, `flush()`, alias listing, credential retrieval/creation/deletion, and `CLEAR_TEXT_FALLBACK`.
- `CredentialProviderFactory` creates providers from a configuration path via `createProvider(URI, Configuration)` and `getProviders(Configuration)`, keyed by `CREDENTIAL_PROVIDER_PATH`.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` and adds default-authenticator configuration, query-string delegation-token mode, authenticated `HttpURLConnection` creation, and delegation-token get/renew/cancel overloads with optional `doAsUser`.
- `DelegationTokenAuthenticatedURL.Token` extends `AuthenticatedURL.Token` and stores a Hadoop `Token` delegation token through `getDelegationToken()` and `setDelegationToken(Token)`.
- `DelegationTokenAuthenticator` wraps an `Authenticator` and exposes connection configurator propagation, `authenticate`, token get/renew/cancel overloads, and public parameter/header/JSON field constants such as `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `DELEGATION_PARAM`, `TOKEN_PARAM`, and `RENEWER_PARAM`.
- `KerberosDelegationTokenAuthenticator` provides Kerberos SPNEGO plus delegation-token operations and falls back to `PseudoDelegationTokenAuthenticator` when the HTTP endpoint does not trigger SPNEGO.
- `PseudoDelegationTokenAuthenticator` provides Hadoop pseudo/simple authentication using a query-string user name based on `UserGroupInformation.getCurrentUser()`.
- `AbstractService` implements `Service` and begins the lifecycle API with constructor `AbstractService(String name)`, `getServiceState`, synchronized failure accessors, protected `setConfig`, `init(Configuration)`, `start()`, `stop()`, final `close()`, final protected `noteFailure(Exception)`, and `waitForServiceToStop(long)`.

## Control Flow

Metrics control flow is sample accumulation followed by snapshot/export. Producers call `MutableRate` or `MutableStat.add(...)`; synchronized `MutableStat` mutators serialize updates to current sample state and extended-stat toggles. A metrics system later calls `snapshot(MetricsRecordBuilder, boolean)`, which emits counters/gauges into the record builder. `MutableRates.init(protocol)` pre-populates metrics from a protocol class before samples arrive so first-snapshot/JMX consumers see stable names. Sinks receive configured state through `init(SubsetConfiguration)`, consume records in `putMetrics`, and flush or close their outputs.

Metrics cache control flow fills gaps for sinks that do not handle sparse updates. Each incoming `MetricsRecord` updates a cached record keyed by name and tags; callers can choose whether tag values are included for later lookup. Sinks such as file or Graphite exporters can then emit complete records using cached data rather than only the fields present in an individual update.

Network topology resolution flows through `DNSToSwitchMapping.resolve(List)`. Hadoop topology-aware code supplies hostnames or IP addresses and expects a returned list in the same order and size, with `null` indicating failure. `CachedDNSToSwitchMapping` filters out names already present in cache, delegates misses to the raw mapping, then serves future lookups from memory. Reload methods either invalidate all cached mappings or selected nodes. `AbstractDNSToSwitchMapping.dumpTopology()` provides diagnostic flow by collecting known mappings and switch counts.

Script/table topology providers layer configuration over the same contract. `ScriptBasedMapping.setConf(Configuration)` configures the script-backed raw resolver; if no script is configured, `NO_SCRIPT` appears in string diagnostics and the mapping behaves as a default/single-policy resolver depending on implementation. `TableMapping.reloadCachedMappings()` refreshes its table-backed raw map and invalidates cached entries so subsequent `resolve` calls see updated rack assignments.

Socket factory flow is the standard Java networking path. Hadoop clients obtain a `SocketFactory`, call one of the overloaded `createSocket` methods, and either get direct sockets from `StandardSocketFactory` or proxy-routed sockets from `SocksSocketFactory`. The configurable SOCKS factory reads Hadoop configuration to construct or update its proxy settings; equality/hash behavior allows factories to be compared or cached.

Record I/O runtime flow is serializer-implementation dependent but contractually uniform. Generated `Record` classes call `RecordOutput.startRecord`, primitive/vector/map write methods, and `endRecord`; deserialization mirrors that through `RecordInput.startRecord`, primitive reads, index-based vector/map loops, and end markers. Binary implementations use compact binary and zero-compressed integer utilities; CSV and XML implementations add format-specific escaping and structural markers. `Record.write/readFields` bridge generated records to Hadoop `Writable` APIs.

Record compiler flow starts from `.jr` record definitions. The generated `Rcc` parser reads input through `SimpleCharStream` and `RccTokenManager`, builds compiler model objects such as `JFile`, `JRecord`, `JField`, and `JType`, and `JFile.genCode` emits source for the selected language into a destination directory. `RccTask.execute()` wraps that driver for Ant builds, applying language, destination, file, file-set, and fail-on-error settings.

Record metadata flow lets code describe and skip serialized records without binding to a generated Java class. `RecordTypeInfo` stores a record name and ordered field type information, can serialize/deserialize itself, and can find nested struct type info by name. `TypeID` subclasses encode primitive, map, vector, and struct shapes; metadata `Utils.skip` uses type IDs to consume serialized data from a stream.

Security mapping flow is provider-driven. Group mapping services receive a user name, return group memberships, and expose cache refresh/add hooks for administrative updates. ID mapping providers translate between user/group names and integer IDs, with unknown-tolerant methods for protocols such as NFS that may encounter unmapped principals.

Credential-provider flow is path/configuration based. `CredentialProviderFactory.getProviders(conf)` reads configured provider URIs and creates provider instances. Applications call provider methods to list aliases, retrieve credential entries, create new entries, delete entries, and call `flush()` so durable providers write changes to their backing store. `isTransient()` differentiates in-memory/non-persistent providers from persistent stores.

Web delegation-token flow layers token operations on top of `AuthenticatedURL`. `DelegationTokenAuthenticatedURL.openConnection(...)` authenticates using either an existing delegation token in its nested `Token` object or the configured authenticator. Token acquisition authenticates the user and stores/returns a Hadoop delegation token; renewal authenticates with the configured authenticator and returns a new expiration time; cancellation sends the token to the server endpoint and intentionally does not require authenticator-based login. Overloads carrying `doAsUser` propagate proxy-user identity to server-side token ownership/operation semantics.

`DelegationTokenAuthenticator` control flow is wrapper-oriented: it delegates base HTTP authentication to an inner `Authenticator`, applies any `ConnectionConfigurator`, and then performs delegation-token operations using documented query parameters, headers, and JSON response field names. The Kerberos subclass first attempts SPNEGO-capable behavior and can fall back to pseudo authentication; the pseudo subclass trusts the current Hadoop user identity and serializes it as an HTTP query parameter.

`AbstractService` lifecycle flow begins with `init(conf)`, moves through `start()`, and ends at `stop()` or `close()`. The public methods enforce service-state transitions and delegate implementation work to lifecycle hooks outside this chunk (`serviceInit`, `serviceStart`, `serviceStop` are referenced but not fully visible here). Failures are recorded through `noteFailure`, and callers can inspect both the throwable cause and the service state in which failure happened.

## State and Persistence Behavior

The XML file itself is generated API metadata and has no runtime persistence behavior. Runtime state and durability are implied by the public contracts it describes.

Metrics classes are in-memory mutable state holders until a snapshot is taken. `MutableStat` keeps running sample counts, sums, min/max, and optional extended statistics; synchronized methods imply concurrency-sensitive in-memory state. `resetMinMax()` explicitly clears all-time min/max state. `FileSink` persists emitted metrics to a file, while `GraphiteSink` sends them to an external Graphite endpoint; both need `flush()` and `close()` handling to avoid losing buffered data. `MetricsCache` stores the latest metric/tag values in memory and may evict or reject records based on the configured max-records-per-name limit.

Network topology mappings are local cached state over external or configurable sources. `CachedDNSToSwitchMapping` maintains host-to-switch memory state and exposes a copy for diagnostics. `ScriptBasedMapping` depends on configured script path/arguments and process execution outside this XML surface. `TableMapping` persists its authoritative mapping in a configuration-specified table file and refreshes in-memory state on reload. Stale mappings directly affect rack-aware scheduling and block placement decisions until refreshed.

Socket factories hold little durable state, but `SocksSocketFactory` keeps configuration/proxy state. Equality and hash code behavior matter if factories are used as keys or cached by RPC/client code.

Record I/O persists application data to binary, CSV, or XML streams through `RecordOutput` and restores it through `RecordInput`. `Buffer` owns mutable byte-array storage with distinct count and capacity, so `get()` exposes underlying storage rather than necessarily a right-sized copy. `RecordTypeInfo` is itself a serializable `Record`, so schema/type metadata can travel in files or RPC streams with record data. The compiler and generated parser hold transient parse/token buffers and write generated source files as their durable output.

Security providers model both transient and durable state. Group and ID mapping providers typically cache OS, LDAP, shell, or service-backed identity data; cache refresh/add methods are part of the public contract. `CredentialProvider` implementations may be transient or persistent; persistent stores require `flush()` to write changes. Credential aliases and entries represent sensitive state and must preserve delete/create semantics and clear-text fallback policy.

Delegation-token classes hold authentication cookies and Hadoop delegation tokens client-side. The nested `DelegationTokenAuthenticatedURL.Token` combines the base authenticated URL token state with a Hadoop delegation token. Server-side token acquisition, renewal, and cancellation mutate remote token-manager state even though the client API only exposes HTTP calls and returned expiration timestamps. Query-string transmission mode persists sensitive token material into URLs and potentially logs, caches, or proxies, so its state exposure differs from header transmission.

`AbstractService` holds lifecycle state, configuration, failure cause, and failure state. `getFailureCause()` and `getFailureState()` are synchronized, implying cross-thread visibility requirements after lifecycle failures. `close()` is final and delegates to `stop()`, so service implementations cannot bypass the common close/stop contract.

## Dependencies and Integration Points

The metrics APIs integrate with `org.apache.hadoop.metrics2` core interfaces: `MutableMetric`, `MetricsRecordBuilder`, `MetricsRecord`, `MetricsSink`, and Apache Commons Configuration `SubsetConfiguration`. Export paths integrate with JMX (`MBeans` and `javax.management.ObjectName`), local I/O (`FileSink`), Graphite's plaintext network protocol (`GraphiteSink`), and Java networking (`InetSocketAddress` through `Servers.parse`).

Network APIs integrate with Hadoop configuration (`Configurable`, `Configuration`), topology-aware HDFS policies, `NetUtils`, Java sockets, `SocketTimeoutException`, `SocketFactory`, `Proxy`, `InetAddress`, `SocketAddress`, and external mapping sources such as scripts and table files. The `isSingleSwitch` and `isMappingSingleSwitch` contracts are direct integration points for block placement and scheduling policies that distinguish single-rack from multi-rack clusters.

Record I/O integrates with Hadoop `WritableComparable`, `WritableComparator`, Java `DataInput`/`DataOutput`, `InputStream`/`OutputStream`, JavaCC-generated parser infrastructure, Ant task execution, and generated application record classes. Many classes explicitly document Avro as the replacement, so compatibility work must consider both legacy support and migration paths.

Record compiler APIs integrate with source generation pipelines, build tooling, JavaCC parser/token classes, language-specific code generators, and destination directories. The Ant task bridges Hadoop's record compiler into legacy build files through `org.apache.tools.ant.Task` and `FileSet`.

Security mapping integrates with `UserGroupInformation`, SASL RPC auth methods, OS/directory-service identity providers, cache management commands, and NFS-style numeric identity mapping. Credential providers integrate with `Configuration`, URI-based provider paths, keystores or other secret stores, and applications that resolve aliases instead of embedding passwords in clear text.

Delegation-token web APIs integrate with `org.apache.hadoop.security.authentication.client.AuthenticatedURL`, `Authenticator`, `ConnectionConfigurator`, `AuthenticationException`, `HttpURLConnection`, `URL`, Hadoop `Token`, Kerberos SPNEGO, pseudo authentication, proxy-user `doAs`, and server endpoints that implement the delegation-token HTTP protocol and JSON field names exposed as constants.

`AbstractService` integrates with `org.apache.hadoop.service.Service`, `Service.STATE`, `ServiceStateException`, `Configuration`, Java `Closeable`, and any Hadoop daemon/component that follows the common init/start/stop lifecycle.

## Risks and Edge Cases

Metrics update and snapshot semantics are concurrency-sensitive. `MutableStat` synchronizes important mutators, but `MutableRates` methods in this XML are not marked synchronized; implementations must still protect dynamic metric registration and per-name stat lookup when multiple RPC/client threads add samples. `resetMinMax()` is not marked synchronized in this metadata, which is a potential race area if reset can run concurrently with updates/snapshots.

Metrics sinks can lose data or block daemon progress. `FileSink` depends on file permissions, path validity, and flush/close discipline. `GraphiteSink` depends on network reachability and Graphite formatting; failure handling must avoid unbounded memory growth or service disruption. `MetricsCache` can produce misleading output if tags are excluded when a sink later expects tag-qualified records.

Topology mapping contracts require strict output alignment. `DNSToSwitchMapping.resolve` must return a list with one element per input in the same order; returning fewer, more, or reordered elements can corrupt rack placement. Stale caches after host moves or table/script changes can degrade HDFS placement until reload. `AbstractDNSToSwitchMapping.isMappingSingleSwitch` documentation is subtle: code must verify actual implementation behavior because the text describes special treatment for mappings not derived from the base class.

Script-based mapping is operationally fragile. Missing scripts, slow scripts, script output parse errors, and command-injection risks from hostnames can affect topology resolution. Table mappings risk stale or malformed files. Diagnostics from `dumpTopology()` and `getSwitchMap()` are snapshots and should not be treated as authoritative in concurrent reload scenarios.

SOCKS socket configuration can silently change network routing and security posture. Equality/hash behavior must include proxy-relevant state; otherwise caches may reuse incompatible factories. `ConnectTimeoutException` distinguishes connect timeout from other socket failures and should be preserved by callers that implement retry/backoff logic.

Record I/O is deprecated but still compatibility-sensitive. Binary/CSV/XML encodings must remain readable for legacy data. `Buffer.get()` exposing backing storage can leak mutable internal state if callers modify the returned array. Capacity/count mismatches, truncation, append bounds, clone/copy semantics, and lexicographic byte comparison are common edge cases. CSV/XML string and buffer escaping must round-trip delimiters, non-ASCII, binary data, and empty values.

Generated record comparison and serialization need stable ordering. `RecordComparator.define` changes comparator dispatch globally for a record class; wrong registration can corrupt sort/shuffle behavior. `Record.compareTo` and raw byte comparators must agree. Variable-length integer utilities must handle negative values, boundary values, malformed encodings, and EOF without truncation bugs.

Record compiler/parser classes are generated and easy to break with manual edits. `SimpleCharStream` manages line/column state, buffer expansion, backup, tab size, and begin/end token positions; off-by-one errors affect parse diagnostics. `ParseException` and `TokenMgrError` construct human-facing messages and escaped text; malformed or huge inputs can stress token buffers. Compiler deprecation reduces active coverage but does not remove public API compatibility obligations.

Credential-provider APIs handle sensitive material. Providers must reject duplicate alias creation, handle missing deletes, avoid leaking credential char arrays/entries, and ensure `flush()` is called for persistent stores. `CLEAR_TEXT_FALLBACK` can weaken security if enabled unexpectedly. URI parsing in `CredentialProviderFactory` must avoid accepting unsupported or malicious provider schemes.

Group and ID mapping providers can create authorization and ownership bugs. Cache refresh/add must be visible to subsequent lookups. Unknown-tolerant UID/GID methods need deterministic behavior for unmapped principals. Group membership ordering and duplicates can affect policy checks or tests.

Delegation-token URL handling is security-critical. Sending tokens in query strings can expose secrets through logs, browser/proxy caches, referrers, and monitoring systems; header mode is safer where supported. Token get/renew methods require authentication and can throw both `IOException` and `AuthenticationException`; cancellation intentionally does not require configured authenticator login, so the token itself must be sufficient proof. `doAsUser` propagation must be encoded and authorized consistently to avoid proxy-user escalation.

Kerberos-to-pseudo fallback improves interoperability but can mask server misconfiguration. Clients expecting strong SPNEGO authentication may accidentally proceed with pseudo auth if endpoint negotiation fails. Tests and deployments need explicit coverage of fallback enablement and failure behavior.

`AuthenticatedURL` instances are documented as not thread-safe, and `DelegationTokenAuthenticatedURL` inherits that warning. Sharing one instance or nested token object across threads can corrupt cookie/delegation-token state.

`AbstractService` lifecycle transitions are failure-prone under concurrency. `init` requires non-null configuration and valid state transitions; `start` and `stop` must reject illegal states. Failure cause should be recorded only once according to the doc for `noteFailure`. Since `close()` is final and relays to `stop()`, code must avoid assuming `close()` can throw implementation-specific cleanup exceptions beyond the `IOException` signature and stop behavior.

## Test Signals

Useful validation for this chunk should focus on API contract behavior across legacy and integration boundaries:

- Metrics tests for `MutableStat` constructors, synchronized sample addition, extended-stat toggling, snapshot contents with `all=true/false`, min/max reset, and concurrent add/snapshot/reset behavior.
- `MutableRates` tests that `init(protocol)` pre-creates method-rate metrics, `add(name, elapsed)` creates or updates the expected rate, and snapshots expose stable names for JMX consumers.
- `FileSink` and `GraphiteSink` tests for configuration parsing, put/flush/close behavior, output formatting, close idempotence, IO failures, and network failures without daemon crashes.
- `MetricsCache` tests for sparse update merging, tag-inclusive vs tag-exclusive lookup, max-records-per-name handling, record eviction/error behavior, and sinks that require dense output.
- `MBeans` tests for exact Hadoop object-name format, duplicate registration handling, unregister behavior, and invalid service/name inputs.
- `Servers.parse` tests for null specs, whitespace/comma combinations, host-only default ports, explicit ports, IPv6 or unusual host strings if supported, and malformed specifications.
- `DNSToSwitchMapping` implementation tests verifying output list size/order, null handling, failed resolutions, full and selective cache reload, `getSwitchMap` copy semantics, `dumpTopology` diagnostics, and `isSingleSwitch`/`isMappingSingleSwitch` policy results.
- `ScriptBasedMapping` tests for configured script execution, no-script fallback string, malformed output, timeout/slow script behavior, duplicate hosts, and configuration replacement through `setConf`.
- `TableMapping` tests for table-file parsing, reload after file changes, missing/malformed entries, cache invalidation, and default rack behavior.
- Socket factory tests for every `createSocket` overload, SOCKS proxy configuration, equality/hash differences between proxy settings, invalid proxy config, and connect timeout propagation through `ConnectTimeoutException`.
- Record I/O round-trip tests across binary, CSV, and XML for every primitive, strings with escapes/non-ASCII, empty and large `Buffer` values, nested records, vectors, maps, and malformed/EOF inputs.
- `Buffer` tests for count/capacity invariants, `set` vs `copy` aliasing, append growth, truncation, reset, clone independence, lexicographic `compareTo`, encoding-specific `toString`, equality, and hash code stability.
- `Record` and `RecordComparator` tests ensuring generated records serialize/deserialize through tagged and untagged APIs, `Writable` methods round-trip, raw comparators agree with object comparison, and comparator registration applies only to the intended class.
- `org.apache.hadoop.record.Utils` tests for variable-length integer/long boundary values, negative numbers, encoded sizes, byte-array and stream readers, malformed varints, float/double parsing, and byte comparison ordering.
- Record compiler tests for `Rcc.driver`, parser productions, include/module/record/type parsing, generated source output paths, invalid syntax diagnostics, JavaCC token positions, and Ant `RccTask` fail-on-error behavior.
- Record metadata tests for `TypeID` equality/hash behavior, map/vector/struct nested types, `RecordTypeInfo` serialize/deserialize, nested struct lookup, field ordering, and `meta.Utils.skip` consuming exactly the expected bytes.
- Group and ID mapping provider tests for cache refresh/add semantics, duplicate and unknown groups/users, unknown-tolerant UID/GID behavior, and integration with `UserGroupInformation`.
- Credential provider tests for provider discovery from `CREDENTIAL_PROVIDER_PATH`, URI scheme validation, transient vs persistent providers, create/get/list/delete aliases, duplicate alias rejection, missing alias behavior, `flush()` durability, and clear-text fallback policy.
- Delegation-token URL tests for default authenticator get/set, header vs query-string token transmission, authenticated open connection with and without an existing delegation token, get/renew/cancel with and without `doAsUser`, IO/authentication exception surfaces, JSON parsing, and token storage in the nested token object.
- Kerberos and pseudo authenticator tests for SPNEGO success, SPNEGO fallback to pseudo when appropriate, pseudo user parameter construction from current UGI, connection configurator propagation, and no accidental fallback when strong authentication is required.
- `AbstractService` tests for legal state transitions, null configuration rejection, failure recording, failure-cause visibility across threads, `close()` calling `stop()`, stop wait behavior, and subclass hook invocation order.

## Cross-Chunk Notes

This chunk begins in the middle of `MutableQuantiles` documentation and ends before the full `AbstractService` API entry is complete. Adjacent chunks should supply the preceding metrics classes and the remainder of `org.apache.hadoop.service`. The merge lane should keep this document tied to the JDiff XML source and distinguish API compatibility metadata from implementation details that need confirmation in the corresponding Java classes under Hadoop Common.

### subset-b-007164: lines 30558-32555

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.7.2.xml lines 30558-32555

## Scope

This chunk is the final chunk of the JDiff API snapshot for Apache Hadoop Common 2.7.2. It starts inside the tail of `org.apache.hadoop.service.AbstractService`, completes the `org.apache.hadoop.service` package, covers `org.apache.hadoop.tracing`, covers a set of public `org.apache.hadoop.util` helpers, covers most visible `org.apache.hadoop.util.bloom` filter APIs, then closes with empty package entries for `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash`.

The source is generated API metadata, not executable Java source. The useful research surface is therefore the compatibility contract exposed by the XML: public/protected classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, synchronization/finality markers, deprecation markers, and embedded Javadoc. Runtime implementation details are inferred only from signatures and documentation visible in this chunk.

## Purpose

This slice captures three main Hadoop Common API areas:

- Service lifecycle support: `Service`, `AbstractService`, `CompositeService`, lifecycle history events, state-change listeners, state transition validation, and helper methods for stopping services safely.
- Operational utilities: trace span receiver administration, application classloader isolation, progress callbacks, Java checksum implementations, reflection and writable-copy helpers, string interning, and the `Tool`/`ToolRunner` command-line contract.
- Probabilistic membership structures: Bloom filters, counting Bloom filters, dynamic Bloom filters, retouched Bloom filters, hash fanout helpers, and remove-scheme constants.

Because this is a JDiff baseline under `dev-support/jdiff`, its repository role is release compatibility checking for Hadoop Common 2.7.2. Any method or field in this XML is part of the documented API baseline that later releases can be compared against.

## Important APIs, Types, and Functions

### Service Lifecycle

- `AbstractService` is already open when the chunk starts. The visible tail includes protected lifecycle hooks `serviceInit(Configuration)`, `serviceStart()`, and `serviceStop()`, plus listener registration, static global listener registration, service metadata accessors, blocker management, and state predicates.
- `AbstractService.serviceInit(Configuration)` is documented as the one-time initialization hook. It can update the service configuration if a subclass created a replacement configuration instance. Exceptions are caught/wrapped by the outer lifecycle operation and can trigger service stop.
- `AbstractService.serviceStart()` is the one-time INITED-to-STARTED hook. Exceptions are caught/wrapped and trigger a stop.
- `AbstractService.serviceStop()` is the one-time transition-to-STOPPED hook. The Javadoc explicitly requires robust shutdown logic that tolerates null fields and continues cleanup after an earlier shutdown failure.
- `AbstractService.registerServiceListener(ServiceStateChangeListener)` and `unregisterServiceListener(...)` manage per-service callbacks. `registerGlobalListener(...)` and `unregisterGlobalListener(...)` expose JVM-wide callbacks for all service state changes.
- `AbstractService.getName()`, synchronized `getConfig()`, `getStartTime()`, synchronized `getLifecycleHistory()`, final `isInState(Service.STATE)`, and `toString()` expose state/identity. `putBlocker(String, String)`, `removeBlocker(String)`, and `getBlockers()` expose live-service blocker diagnostics.
- `CompositeService` extends `AbstractService` and manages child `Service` instances. Its public constructor takes a name. `getServices()` returns a cloned snapshot list; `addService(Service)`, `addIfService(Object)`, and synchronized `removeService(Service)` manage children; `serviceInit`, `serviceStart`, and `serviceStop` cascade lifecycle operations to children.
- `CompositeService.STOP_ONLY_STARTED_SERVICES` is a protected static final shutdown policy flag. The field documentation states the tradeoff between stopping everything and stopping only started services, and notes that children failing during init/start still get `stop()` called.
- `LifecycleEvent` is `Serializable` and carries public mutable fields `time` and `state`, representing a timestamp and the state entered.
- `LoggingStateChangeListener` implements `ServiceStateChangeListener`, has constructors for a supplied Commons Logging `Log` or a default static log, and logs `stateChanged(Service)` callbacks at INFO level.
- `Service` is a public interface extending `Closeable`. It defines the lifecycle contract: `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration, `getName()`, `getConfig()`, `getServiceState()`, `getStartTime()`, `isInState(STATE)`, `getFailureCause()`, `getFailureState()`, `waitForServiceToStop(long)`, `getLifecycleHistory()`, and `getBlockers()`.
- `Service.init(Configuration)` must transition NOTINITED to INITED unless it fails; on failure `stop()` must be invoked and the state becomes STOPPED. `Service.start()` similarly requires INITED to STARTED, with failure driving stop/STOPPED. `Service.stop()` must be a no-op when already STOPPED and best-effort otherwise.
- `Service.close()` is specified as Java 7 close-clause friendly and must relay directly to `stop()`. It declares `IOException`, but the Javadoc says it never throws an `IOException`.
- `Service.waitForServiceToStop(long)` blocks until service stop actions have executed or timeout expires. A timeout of zero means wait forever, and it may be called before init/start to avoid races with fast stops.
- `ServiceOperations` is a final helper class with static `stop(Service)` and `stopQuietly(Service)` / `stopQuietly(Log, Service)` methods. It centralizes null-safe and exception-swallowing service cleanup.
- `ServiceStateChangeListener` defines `stateChanged(Service)`. Its Javadoc is important: callbacks run on the thread that initiated the state change while the service is in a synchronized section, so long-running callbacks and reentrant service calls can delay or deadlock lifecycle transitions.
- `ServiceStateException` extends `RuntimeException`, has constructors for message/cause combinations, and static `convert(Throwable)` / `convert(String, Throwable)` methods that preserve existing runtime exceptions or wrap other throwables as service-state failures.
- `ServiceStateModel` tracks and validates a service's current `Service.STATE`. It has constructors for NOTINITED or an explicit initial state, `getState()`, `isInState(STATE)`, `ensureCurrentState(STATE)`, synchronized `enterState(STATE)`, static `checkStateTransition(String, STATE, STATE)`, static `isValidStateTransition(STATE, STATE)`, and `toString()`.

### Tracing Administration

- `org.apache.hadoop.tools.protocolPB` appears as an empty package in this chunk.
- `SpanReceiverInfo` exposes `getId()` and `getClassName()`, representing active trace span receiver metadata.
- `SpanReceiverInfoBuilder` constructs span receiver descriptions from a class name. `addConfigurationPair(String, String)` adds configuration to the pending receiver description, and `build()` returns a `SpanReceiverInfo`.
- `TraceAdminProtocol` is the non-PB tracing admin interface. It exposes `listSpanReceivers()`, `addSpanReceiver(SpanReceiverInfo)`, and `removeSpanReceiver(long)`, all throwing `IOException`, plus a public static final `versionID` field.
- `TraceAdminProtocolPB` extends generated `TraceAdminPB.TraceAdminService.BlockingInterface` and Hadoop IPC `VersionedProtocol`, making the same administrative surface available via protobuf-backed RPC.

### General Utilities

- `ApplicationClassLoader` extends `URLClassLoader`. It has constructors from `URL[]` or a classpath string, parent classloader, and system-class pattern list. It overrides `getResource(String)`, public `loadClass(String)`, and synchronized protected `loadClass(String, boolean)`.
- `ApplicationClassLoader.isSystemClass(String, List)` checks whether a class/resource should be loaded by the system/parent side based on positive and negative system class patterns. `SYSTEM_CLASSES_DEFAULT` documents the default parent-loaded set, including JDK classes, Hadoop classes/resources, and selected third-party classes.
- `IPList` is a small predicate interface with `isIn(String ipAddress)`.
- `Progressable` defines `progress()`, the callback used by long-running operations to report liveness to the Hadoop framework and avoid timeout assumptions.
- `PureJavaCrc32` implements `java.util.zip.Checksum` with constructor, `getValue()`, `reset()`, `update(byte[], int, int)`, and final `update(int)`. Its documentation says it uses the same polynomial as native `java.util.zip.CRC32` and avoids JNI overhead for many small checksums.
- `PureJavaCrc32C` also implements `Checksum`, with the same visible operations, but uses the CRC32-C polynomial used by iSCSI and hardware support on some Intel chipsets.
- `ReflectionUtils` exposes configuration, instantiation, thread-info, writable-copy, and inherited-member helpers. Important methods include `setConf(Object, Configuration)`, generic `newInstance(Class, Configuration)`, `setContentionTracing(boolean)`, synchronized `printThreadInfo(PrintStream, String)`, `logThreadInfo(Log, String, long)`, generic `getClass(T)`, generic `copy(Configuration, T src, T dst)`, `cloneWritableInto(Writable, Writable)`, `getDeclaredFieldsIncludingInherited(Class)`, and `getDeclaredMethodsIncludingInherited(Class)`.
- `StringInterner` exposes static `strongIntern(String)` and `weakIntern(String)`. The documentation emphasizes reducing permanent-generation pressure versus direct `String.intern()` by using strong or weak representative references.
- `Tool` extends `Configurable` and defines `run(String[]) throws Exception`. The long embedded example documents the standard pattern of letting `ToolRunner` handle generic Hadoop command-line options, then using the resulting `Configuration` for application-specific setup.
- `ToolRunner` has static `run(Configuration, Tool, String[])`, `run(Tool, String[])`, `printGenericCommandUsage(PrintStream)`, and `confirmPrompt(String)`. It integrates `Tool` with generic option parsing and configuration mutation before invoking `Tool.run(...)`.

### Bloom Filter Utilities

- `BloomFilter` extends `Filter`. It has a zero-argument constructor for `readFields`, a constructor `(int vectorSize, int nbHash, int hashType)`, and operations `add(Key)`, `and(Filter)`, `membershipTest(Key)`, `not()`, `or(Filter)`, `xor(Filter)`, `toString()`, `getVectorSize()`, `write(DataOutput)`, and `readFields(DataInput)`.
- `CountingBloomFilter` is final and extends `Filter`. It adds `delete(Key)` and `approximateCount(Key)` to the same add/membership/boolean-combination/serialization surface. Its Javadoc states count storage is limited by bucket size, with overflow after repeated inserts around 15 and possible underflow after deletes.
- `DynamicBloomFilter` extends `Filter` and has constructors for serialization and `(vectorSize, nbHash, hashType, nr)`. It grows by adding Bloom-filter rows when the active row reaches the configured threshold `nr`. It exposes the same add, logical combination, membership, string, and Writable methods.
- `HashFunction` is a final helper. Its constructor accepts a maximum value, number of hash results, and hash type. `clear()` is a no-op, and `hash(Key)` returns an `int[]` of hash positions.
- `RemoveScheme` is an interface used as a constant holder for retouched Bloom filters. Public static final short constants are `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`, each documenting a different selective-clearing heuristic.
- `RetouchedBloomFilter` is final, extends `BloomFilter`, and implements `RemoveScheme`. It has constructors for serialization and `(vectorSize, nbHash, hashType)`, overrides/extends `add(Key)`, has overloads of `addFalsePositive(...)` for one `Key`, `Collection`, `List`, and `Key[]`, exposes `selectiveClearing(Key, short)`, and implements `write(DataOutput)` / `readFields(DataInput)`.
- Empty package nodes for `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash` close the file. In this chunk, `org.apache.hadoop.util.hash` has no class declarations even though Bloom constructors reference `org.apache.hadoop.util.hash.Hash`; the referenced hash APIs must be in an earlier chunk or absent from this JDiff slice.

## Control Flow

The XML itself has no executable control flow, but it documents several important flows:

- Service lifecycle flow starts at `Service.init(Configuration)`, transitions from NOTINITED to INITED, then `start()` transitions from INITED to STARTED, and `stop()` transitions to STOPPED. Failures during init/start must trigger stop and capture failure state/cause.
- `AbstractService` implements the template-method structure around subclass hooks. Public lifecycle methods in earlier parts of the class call protected `serviceInit`, `serviceStart`, and `serviceStop` once per instance; these hooks do not need their own synchronization because the outer lifecycle methods prevent re-entry.
- Composite lifecycle flow is parent-driven. `CompositeService.serviceInit`, `serviceStart`, and `serviceStop` apply lifecycle operations to a snapshot/list of child services. Shutdown policy is governed by `STOP_ONLY_STARTED_SERVICES`, but failed children during init/start still receive `stop()`.
- Listener flow is synchronous with state transition. A service state change first changes the service state, then invokes registered listeners and global listeners on the initiating thread while the service is synchronized. Logging listeners simply record the change.
- Service stop helper flow is defensive. `ServiceOperations.stop(Service)` checks for null and state before stopping, while `stopQuietly` catches and logs exceptions for cleanup paths.
- State model flow centralizes transition validation. Callers query `getState`/`isInState`, assert with `ensureCurrentState`, then call synchronized `enterState` to atomically validate and store a proposed state. Static helpers expose validation without mutating an instance.
- Tracing admin flow lists existing span receivers, builds a `SpanReceiverInfo` with configuration pairs, sends it through `TraceAdminProtocol.addSpanReceiver`, and later removes it by id. The PB interface is the IPC transport boundary for the same operations.
- Application classloading flow checks `isSystemClass` patterns before deciding whether parent/system loading should win or whether application URLs should be consulted first. This supports isolation while preserving Hadoop/JDK/shared classes.
- Tool execution flow wraps application logic with generic Hadoop option parsing. `ToolRunner.run` sets the possibly modified `Configuration` onto the `Tool`, then invokes `Tool.run(String[])`; callers use the integer return code as the process status.
- Checksum flow follows the `Checksum` interface: repeated `update(...)` calls mutate an internal CRC state, `getValue()` reads it, and `reset()` clears it.
- Reflection copy flow serializes a `Writable` source into a buffer and deserializes into the destination, destroying prior destination contents. `cloneWritableInto` performs the same style of mutable target update.
- Bloom filter flow hashes a `Key` to multiple vector positions with `HashFunction`, mutates internal vectors/counters on `add`, and answers `membershipTest` by checking whether the necessary positions are set. Logical `and`, `or`, `xor`, and `not` operate on filter state and require compatible filter shapes.
- Counting filter deletion flow decrements counters for a key only when the key is believed present. Dynamic filter insertion chooses an active row or creates a new row once the active-row threshold is exceeded. Retouched filter flow records known false positives and selectively clears bits using one of the `RemoveScheme` constants.

## State and Persistence Behavior

The JDiff XML file persists an API baseline, not application state. Its own important state is structural: package names, type names, method signatures, field declarations, inheritance relationships, checked exception declarations, and documentation blocks. This file should remain stable for compatibility comparisons.

The APIs described in the chunk expose several runtime state models:

- Service state is explicit and observable through `Service.STATE`, `ServiceStateModel`, lifecycle history, start time, failure cause/state, and blocker maps. Lifecycle history is returned as a snapshot list, and blockers are returned as a snapshotted map.
- `AbstractService.getConfig()` and `getLifecycleHistory()` are synchronized in this baseline, indicating concurrency-sensitive mutable internal state. `ServiceStateModel.enterState(...)` is also synchronized.
- `LifecycleEvent` is serializable and uses public fields, so its serialized shape and field names are part of a durable Java serialization contract.
- `CompositeService` owns a mutable child-service list; `getServices()` returns a clone so callers cannot mutate the manager's internal list directly.
- Trace administration persists active receiver configuration outside the XML. `SpanReceiverInfo` carries receiver id/class and builder-supplied configuration pairs that are sent over the tracing admin protocol.
- `ApplicationClassLoader` persists no external state, but its constructor-supplied URL list, parent loader, and system-class pattern list define class/resource resolution behavior for the life of the loader.
- `PureJavaCrc32` and `PureJavaCrc32C` maintain mutable checksum accumulators compatible with `java.util.zip.Checksum`.
- `ReflectionUtils.copy` and `cloneWritableInto` are serialization-sensitive because they depend on Hadoop `Writable` binary round trips.
- `StringInterner.strongIntern` retains strong references and can grow memory retention; `weakIntern` allows garbage collection.
- `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, and `RetouchedBloomFilter` implement `write(DataOutput)` and `readFields(DataInput)`, making vector size, hash count/type, bit/counter vectors, row counts, false-positive metadata, and other internal fields durable Hadoop Writable state. Changing the order or meaning of serialized fields would break persisted filters.
- Counting Bloom filters have counter overflow/underflow semantics documented as part of the behavioral contract. Dynamic Bloom filters persist a matrix-like collection of rows and an `nr` threshold. Retouched Bloom filters persist or reconstruct false-positive/selective-clearing state through their Writable methods.

## Dependencies and Integration Points

This chunk integrates with core Java APIs:

- `java.io.Closeable`, `IOException`, `Serializable`, `DataInput`, `DataOutput`, `PrintStream`, and `MalformedURLException`.
- `java.net.URL`, `URLClassLoader`, and class/resource loading.
- `java.util.List`, `Collection`, `Map`, and Java reflection `Class`.
- `java.util.zip.Checksum`.

Hadoop-specific integration points include:

- `org.apache.hadoop.conf.Configuration`, `Configurable`, and the generic command-line option system used by `Tool` and `ToolRunner`.
- `org.apache.hadoop.service.Service.STATE`, `ServiceStateChangeListener`, `ServiceStateException`, and lifecycle model classes used by long-running daemons across Hadoop Common, HDFS, and YARN.
- Commons Logging `org.apache.commons.logging.Log` for service state logging, stop-quietly warnings, and thread-info logging.
- Hadoop tracing protobufs and IPC through `TraceAdminPB.TraceAdminService.BlockingInterface` and `org.apache.hadoop.ipc.VersionedProtocol`.
- Hadoop serialization through `org.apache.hadoop.io.Writable` and `Writable` copy helpers.
- Bloom-filter package types `Filter`, `Key`, and hash-type constants from `org.apache.hadoop.util.hash.Hash`, which are referenced here but defined outside this visible chunk.
- Command-line tools that implement `Tool` commonly combine this API with `Configured`, `GenericOptionsParser`, filesystem paths, MapReduce job setup, and process exit handling.

## Risks and Edge Cases

- This chunk begins mid-`AbstractService`, immediately after the `waitForServiceToStop(long)` method declaration opened in the previous chunk. The merge lane must combine chunk 5 and chunk 6 before making whole-class claims about all `AbstractService` fields and methods.
- JDiff metadata does not contain method bodies. Exact listener collections, blocker map implementation, lifecycle transition tables, Bloom vector encodings, classloader pattern syntax, and exception messages require Java source validation if implementation-level details matter.
- Service listeners are invoked while the service is synchronized and on the transition caller's thread. Long callbacks, recursive service calls, or callbacks that wait on other lifecycle operations can deadlock or stall daemon startup/shutdown.
- `Service.getConfig()` documentation says the returned configuration is normally not cloned. Mutating it after service initialization can have undefined or implementation-specific effects.
- `Service.stop()` must work even when fields were never initialized or were only partially initialized. Subclasses that assume STARTED-only state in cleanup risk failing after init/start errors.
- `CompositeService.getServices()` returns a snapshot; services added after the call are not visible through that list. Code that iterates an older snapshot may miss later children.
- `STOP_ONLY_STARTED_SERVICES` changes shutdown breadth. Child services must tolerate stop after failed init/start even if normal policy skips non-started services.
- `ServiceStateException.convert(Throwable)` preserves runtime exceptions but wraps checked exceptions and other throwables. Callers relying on exact checked exception types lose that static typing at this boundary.
- Trace admin methods throw `IOException`; adding/removing span receivers is an operational RPC surface and can fail due to authorization, IPC, invalid class/configuration, or receiver construction failures.
- `ApplicationClassLoader` class/resource isolation is pattern-driven. Incorrect system-class patterns can cause class version conflicts, parent/application split-brain, resource shadowing, or linkage errors.
- `PureJavaCrc32` documentation cites performance relative to old Java 1.6 native CRC32; modern JVM/hardware behavior may differ, so performance tests should not assume that old ratio.
- `StringInterner.strongIntern` intentionally retains strong references and can create unbounded memory retention if used on high-cardinality data.
- `ReflectionUtils.copy` destroys the destination object's old contents and depends on correct `Writable` serialization. It is unsafe for objects with non-serialized side state unless callers account for that.
- `ToolRunner.run(Tool, String[])` is documented as equivalent to `run(tool.getConf(), tool, args)`. A null or shared `Configuration` can affect command parsing and later code unexpectedly.
- Bloom filter logical operations require compatible vector size/hash configuration. The signatures accept `Filter`, so invalid concrete type or incompatible shape likely fails at runtime.
- Standard Bloom filters can return false positives by design but should not return false negatives after insertion. Counting and retouched variants can introduce underflow/false-negative behavior around deletes and selective clearing.
- Counting Bloom filters overflow when the same key is inserted too many times for the bucket size; the Javadoc explicitly warns that more than 15 inserts can increase error rates for that and other keys.
- `RetouchedBloomFilter.selectiveClearing` trades false positives for false negatives. Users must choose remove schemes based on the expected cost of each error type.
- The empty `org.apache.hadoop.util.hash` package node in this chunk means hash implementations are not visible here, even though Bloom APIs depend on hash type constants and behavior.

## Test Signals

Useful tests or compatibility checks for this chunk include:

- JDiff/schema checks that every package/type/method/field in lines 30558-32555 remains parseable and that generated metadata preserves visibility, static/final/synchronized flags, return types, parameters, checked exceptions, and deprecation markers.
- Service lifecycle tests for NOTINITED-to-INITED-to-STARTED-to-STOPPED transitions, invalid transitions, double init/start/stop behavior, failure cause/state recording, start time, lifecycle history snapshots, and `waitForServiceToStop(0)` / timeout behavior.
- `AbstractService` tests for subclass hook invocation exactly once, configuration replacement during `serviceInit`, robust stop after partial initialization, blocker map put/remove/snapshot behavior, local/global listener registration, unregister return values, and close delegating to stop.
- Listener tests that assert callbacks see the updated state, that callbacks run synchronously on the initiating thread, that slow listeners delay transition completion, and that reentrant listener behavior is documented or guarded.
- `CompositeService` tests for child init/start/stop ordering, child failure cleanup, removing services, `addIfService(Object)` true/false behavior, snapshot semantics of `getServices()`, and shutdown behavior around `STOP_ONLY_STARTED_SERVICES`.
- `ServiceOperations` tests for null-safe stop, state-checked stop, `stopQuietly` exception capture, optional logging, and non-catching behavior for non-Exception `Throwable` if the implementation follows the Javadoc strictly.
- `ServiceStateModel` tests for every valid and invalid transition, synchronized concurrent `enterState`, `ensureCurrentState` errors, and `toString()` state text.
- Tracing admin tests for `SpanReceiverInfoBuilder` configuration-pair construction, `listSpanReceivers`, `addSpanReceiver`, `removeSpanReceiver`, protobuf protocol versioning, error propagation, and access-control/invalid-receiver failures.
- `ApplicationClassLoader` tests for URL and classpath-string constructors, malformed classpath errors, resource child-first behavior, class child-first behavior, parent/system class exclusions, negative pattern handling, and compatibility with `SYSTEM_CLASSES_DEFAULT`.
- `Progressable` integration tests in long-running operations to confirm progress calls prevent framework timeouts.
- CRC tests comparing `PureJavaCrc32` against `java.util.zip.CRC32` golden values and `PureJavaCrc32C` against CRC32-C golden values, including byte-array chunking, single-byte updates, reset, and empty input.
- `ReflectionUtils` tests for `setConf` on `Configurable` and non-`Configurable` objects, `newInstance` configuration injection, thread-info logging interval behavior, `copy`/`cloneWritableInto` golden Writable round trips, and inherited field/method enumeration.
- `StringInterner` tests for equal strings returning representative instances, weak references becoming collectible, strong references remaining retained, and null handling if supported by implementation.
- `Tool`/`ToolRunner` tests for generic option parsing, configuration mutation before `run`, run return-code propagation, exception propagation, `printGenericCommandUsage`, and `confirmPrompt` yes/no parsing.
- Bloom filter tests for add/membership false-positive bounds, no false negatives for inserted keys in plain Bloom filters, logical and/or/xor/not compatibility checks, serialization round trips, vector-size reporting, and constructor/readFields behavior.
- Counting Bloom filter tests for delete of absent keys, count approximation, repeated insert overflow warnings, underflow after deletes, serialization, and logical operations against incompatible filters.
- Dynamic Bloom filter tests for row growth when `nr` is reached, membership across multiple rows, serialization of row thresholds/state, and logical operation behavior across dynamic filters.
- Retouched Bloom filter tests for adding false positives through all overloads, null false-positive handling, selective clearing with each `RemoveScheme`, tradeoff effects on false positives/false negatives, and Writable round trips.

## Cross-Chunk Notes

The previous chunk owns the beginning and middle of `AbstractService`, including the public lifecycle method declarations that lead into this chunk. This chunk closes the XML file, so there is no next chunk. The merge/reconciliation lane should combine all six chunks for `Apache_Hadoop_Common_2.7.2.xml` before producing the final source-tree-aligned per-file report.
