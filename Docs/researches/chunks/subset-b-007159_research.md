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
