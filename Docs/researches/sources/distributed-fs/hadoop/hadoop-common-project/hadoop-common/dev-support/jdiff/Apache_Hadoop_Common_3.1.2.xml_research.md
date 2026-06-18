# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007186`: lines 1-6130, `Docs/researches/chunks/subset-b-007186_research.md`
- `subset-b-007187`: lines 6131-12080, `Docs/researches/chunks/subset-b-007187_research.md`
- `subset-b-007188`: lines 12081-17950, `Docs/researches/chunks/subset-b-007188_research.md`
- `subset-b-007189`: lines 17951-24252, `Docs/researches/chunks/subset-b-007189_research.md`
- `subset-b-007190`: lines 24253-30507, `Docs/researches/chunks/subset-b-007190_research.md`
- `subset-b-007191`: lines 30508-35695, `Docs/researches/chunks/subset-b-007191_research.md`

## Chunk Research

### subset-b-007186: lines 1-6130

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml lines 1-6130

## Scope

This chunk is the opening section of the JDiff API XML snapshot for Apache Hadoop Common 3.1.2. It includes generated metadata and Javadocs for public/protected API in `org.apache.hadoop`, `org.apache.hadoop.conf`, `org.apache.hadoop.crypto.key`, and the first part of `org.apache.hadoop.fs` through the start of `CreateFlag`.

The source is not implementation code. The available evidence is API structure: package/type boundaries, inheritance, interfaces, method signatures, checked exceptions, `static`/`final`/`abstract`/`synchronized` flags, field names, deprecation markers, and embedded documentation. Runtime control flow and persistence details below are therefore inferred from the documented contracts rather than method bodies.

## Purpose

The chunk defines several core Hadoop Common compatibility surfaces:

- `HadoopIllegalArgumentException` is Hadoop's public illegal-argument exception type, used to distinguish invalid Hadoop API usage from JDK-originated `IllegalArgumentException`.
- `Configurable`, `Configuration`, and `Configured` form Hadoop's central configuration system. They load XML resources, overlay defaults and site settings, expand variables, track final parameters and property sources, support deprecated key aliases, serialize configuration state, and expose typed conversion helpers for common primitive, collection, class, path, socket, credential, time, and storage-size values.
- `KeyProvider` and `KeyProviderFactory` define the key-management abstraction used by Hadoop encryption clients. Providers supply versioned key material, metadata, rollover, cache invalidation, flushing, password status, and factory discovery through configured URI paths.
- `AbstractFileSystem` defines the FileContext-facing filesystem provider contract. It covers URI validation, filesystem discovery, statistics, path qualification, creation/open/delete/rename, symlinks, permissions, ACLs, xattrs, snapshots, storage policies, block locations, and service-name discovery.
- Early `org.apache.hadoop.fs` support types model Avro seekable input, block locations, block storage policies, stream buffer-control capabilities, checksum errors, checksum-wrapping filesystems, public configuration key constants, and content summary output formatting.

## Important APIs, Types, and Functions

### Core and Configuration

- `org.apache.hadoop.HadoopIllegalArgumentException` extends `java.lang.IllegalArgumentException` and has a `String` constructor for detail messages.
- `Configurable` is a small public interface with `setConf(Configuration)` and `getConf()`.
- `Configuration` implements `Iterable` and `org.apache.hadoop.io.Writable`. Constructors create default-loading, no-default-loading, or cloned configurations.
- Static deprecation APIs include `addDeprecations(DeprecationDelta[])`, several `addDeprecation(...)` overloads, `isDeprecated(String)`, `reloadExistingConfigurations()`, `addDefaultResource(String)`, `dumpConfiguration(...)`, `dumpDeprecatedKeys()`, and `hasWarnedDeprecation(String)`. The Javadoc states `addDeprecations` updates global deprecation state with an atomic retry loop.
- Resource APIs include `addResource` overloads for classpath names, `URL`, `Path`, `InputStream`, named streams, and another `Configuration`, plus `reloadConfiguration()`. Overloads with `restrictedParser` indicate secure/restricted XML parsing support.
- Lookup and mutation APIs include `get`, `getTrimmed`, `getRaw`, `set`, `unset`, `setIfUnset`, `onlyKeyExists`, `size`, `clear`, `iterator`, `getPropsWithPrefix`, and `getPropertySources`.
- Typed conversion APIs cover `getInt`, `getInts`, `setInt`, `getLong`, `getLongBytes`, `setLong`, `getFloat`, `setFloat`, `getDouble`, `setDouble`, `getBoolean`, `setBoolean`, `setBooleanIfUnset`, `setEnum`, `getEnum`, `setTimeDuration`, `getTimeDuration`, `getTimeDurations`, `getStorageSize`, `setStorageSize`, `getPattern`, `setPattern`, range parsing, string collections, and trimmed string arrays.
- Credential and secret APIs include `getPassword`, `getPasswordFromCredentialProviders`, and protected `getPasswordFromConfig`. The contract prefers CredentialProvider aliases with optional clear-text fallback.
- Network/address helpers include `getSocketAddr`, `setSocketAddr`, and `updateConnectAddr`, including bind-host versus client-connect address handling for multi-homed services.
- Class-loading helpers include `getClassByName`, `getClassByNameOrNull`, `getClasses`, `getClass`, `getInstances`, `setClass`, `getClassLoader`, and `setClassLoader`.
- Local resource helpers include `getLocalPath`, `getFile`, `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader`.
- Serialization/introspection APIs include `writeXml` overloads, static JSON-like `dumpConfiguration` overloads, `readFields(DataInput)`, `write(DataOutput)`, `main(String[])`, `getValByRegex`, tag queries, and property tag validation.
- `Configured` implements `Configurable` as a base class with zero-arg and `Configuration` constructors.

### Crypto Key Management

- `KeyProvider` is abstract and documented as a thread-safe provider of secret key material. It is configured by `Configuration`.
- Abstract provider operations include `getKeyVersion(String)`, `getKeys()`, `getKeyVersions(String)`, `getMetadata(String)`, `createKey(String, byte[], Options)`, `deleteKey(String)`, `rollNewVersion(String, byte[])`, and `flush()`.
- Concrete helper/default operations include `getConf`, static `options(Configuration)`, `isTransient`, bulk `getKeysMetadata(String[])`, `getCurrentKey(String)`, generated-material `createKey(String, Options)`, `close`, generated-material `rollNewVersion(String)`, `invalidateCache(String)`, static `getBaseName(String)`, protected static `buildVersionName(String, int)`, static `findProvider(List, String)`, `needsPassword`, `noPasswordWarning`, and `noPasswordError`.
- Public constants include default cipher and bit-length keys/defaults plus JCEKS serialization-filter defaults.
- `KeyProviderFactory` is abstract. Implementations provide `createProvider(URI, Configuration)`. Static `getProviders(Configuration)` creates all configured providers, and static `get(URI, Configuration)` resolves one URI through service-loaded factories. `KEY_PROVIDER_PATH` identifies the configuration key for provider URI paths.

### Abstract Filesystem Contract

- `AbstractFileSystem` is an abstract base class for FileContext filesystems. Its constructor binds a filesystem URI, supported scheme, authority requirement, and default port validation.
- Factory/statistics APIs include `createFileSystem(URI, Configuration)`, static `get(URI, Configuration)`, instance/static `getStatistics`, static `clearStatistics`, `printStatistics`, and protected static `getAllStatistics`.
- URI/path APIs include `isValidName`, `checkScheme`, abstract `getUriDefaultPort`, `getUri`, `checkPath`, `getUriPath`, `makeQualified`, `getInitialWorkingDirectory`, `getHomeDirectory`, `getServerDefaults()` deprecated in favor of `getServerDefaults(Path)`, and `resolvePath`.
- Core IO APIs include final `create(Path, EnumSet, CreateOpts...)`, abstract `createInternal(...)`, abstract `mkdir`, abstract `delete`, `open(Path)`, abstract `open(Path, int)`, `truncate`, abstract `setReplication`, final `rename(Path, Path, Rename...)`, abstract `renameInternal(Path, Path)`, and overwrite-aware `renameInternal(Path, Path, boolean)`.
- Metadata and namespace APIs include symlink support and target resolution, permission/owner/times setters, checksum lookup, status and link-status lookup, block locations, filesystem status, status iterators, corrupt-block listing, checksum verification toggle, and canonical delegation-token service name lookup.
- Security and metadata extension APIs include ACL modification/removal/status, xattr set/get/list/remove, snapshot create/rename/delete, storage policy set/unset/get/list, plus `hashCode` and `equals`.

### Filesystem Support Types

- `AvroFSInput` adapts `FSDataInputStream` to Avro's `SeekableInput`; it exposes constructors from an input stream plus length or a `FileContext`/`Path`, and implements `length`, `read(byte[], int, int)`, `seek`, `tell`, and `close`.
- `BlockLocation` is serializable and models a file block's network/storage placement. It has constructors for hosts, names, topology paths, cached hosts, storage IDs/types, offset, length, and corrupt flag. Accessors and mutators expose all of those fields.
- `BlockStoragePolicySpi` describes block replica placement policy with policy name, preferred storage types, creation fallbacks, replication fallbacks, and copy-on-create/inherit-only behavior.
- `ByteBufferReadable.read(ByteBuffer)` defines direct reads into a `ByteBuffer`.
- `CanSetDropBehind`, `CanSetReadahead`, and `CanUnbuffer` define optional stream controls for cache dropping, readahead, and buffer/socket/file-descriptor release.
- `ChecksumException` extends `IOException` and carries a byte position through `getPos()`.
- `ChecksumFileSystem` extends `FilterFileSystem` and wraps a raw filesystem with client-side checksum files. It exposes checksum file naming/length calculations, checksum verification/write controls, raw filesystem access, open/append/create/truncate, metadata forwarding, rename/delete/list/mkdir/copy local helpers, local-output staging, and `reportChecksumFailure`.
- `CommonConfigurationKeysPublic` is a constants catalog for publicly documented common configuration keys and defaults. The visible constants cover filesystem defaults, topology, trash, protected directories, IO and TFile tuning, caller context, IPC, RPC sockets, groups cache, security/authentication/authorization, Kerberos relogin, SASL/RPC protection, crypto codec/cipher/JCE/KMS settings, secure random, shell warnings/deletion safety, HTTP logs, credential provider behavior, sensitive config keys, config tags, and shutdown hook timeout.
- `ContentSummary` extends `QuotaUsage` and implements `Writable`. It stores and formats directory/file/content-size summary values, snapshot-specific counts/space, erasure-coding policy, quota headers, storage-type quota formatting, and human-readable output variants. Constructors are documented as superseded by `ContentSummary.Builder`.
- The visible start of `CreateFlag` shows enum-style `values`, `valueOf`, and static `validate(EnumSet<CreateFlag>)`, which throws `HadoopIllegalArgumentException` for invalid create flag combinations.

## Control Flow

`Configuration` has a layered load path: instances optionally include default resources (`core-default.xml`, then `core-site.xml`), callers add more resources, later resources override earlier ones unless an earlier property is final, and explicit `set` calls overlay loaded values. Accessors trigger parsing and variable expansion for normal `get` paths, while `getRaw` bypasses expansion. `reloadConfiguration` clears loaded resource-derived data and final-parameter state so previously added resources are read again on next access.

Deprecated-key flow is global. Developers register old-to-new mappings before resources have been loaded; reads of deprecated keys return the first replacement value that is present, and writes to deprecated names also write replacement names. `setDeprecatedProperties` backfills deprecated aliases for currently set new properties so iteration can expose both forms.

Typed configuration methods generally flow through string lookup, trimming or expansion according to the method, then parse into the target type. Numeric getters throw `NumberFormatException` for invalid numbers except boolean parsing, which returns the default for missing or invalid values. Time-duration and storage-size helpers parse unit suffixes and convert into requested target units.

Password lookup first attempts CredentialProvider alias resolution and then falls back to clear-text configuration if that behavior is allowed. Socket helpers build or update `InetSocketAddress` values and special-case wildcard listener addresses by replacing them with client-usable hostnames.

`KeyProvider` control flow separates persistent provider operations from convenience operations. Generated-material `createKey` and `rollNewVersion` call the material-generating helper and then delegate to abstract material-explicit methods. `getCurrentKey` uses metadata/version information to locate the current version. Cache invalidation and `flush` are explicit, so callers that roll/delete/create keys need to call provider-specific persistence or cache refresh paths when strong consistency is required.

`KeyProviderFactory` discovery flows from configured provider URI paths through service-loaded `KeyProviderFactory` implementations. A URI scheme selects a factory, and the returned provider is initialized with the same `Configuration`.

`AbstractFileSystem` creation flows from a URI's scheme to the configuration key `fs.AbstractFileSystem.<scheme>.impl`. The implementation constructor receives the full URI and configuration. Instance methods generally validate that paths belong to the filesystem, qualify relative paths, and then delegate to abstract operations implemented by concrete filesystems.

The filesystem IO path separates public convenience methods from implementation points. For example, final `create` parses `Options.CreateOpts` and calls `createInternal` with explicit parameters; final `rename` parses rename options and delegates to `renameInternal`; `open(Path)` delegates to `open(Path, int)` with a default buffer size. ACL, xattr, snapshot, storage policy, and symlink methods are optional hooks that implementations may override or default to unsupported behavior.

`ChecksumFileSystem` wraps another `FileSystem`. Writes create or update sidecar checksum files, reads verify data against those checksum files when verification is enabled, and operations such as rename/delete/list/copy coordinate raw data paths with checksum paths. Checksum failure reporting receives both data and checksum streams plus positions, allowing implementations to decide whether retry is useful.

`ContentSummary` formatting flow selects columns based on quota, human-readable, snapshot, and storage-type flags. Static header helpers expose the corresponding field names for command output alignment.

## State and Persistence Behavior

The XML file itself persists generated release API metadata for JDiff compatibility comparisons. It does not store runtime state.

`Configuration` carries mutable in-memory state: resource references, loaded properties, final parameters, property sources, class loader, quiet mode, allow-null-value mode, and system-property restriction settings. It also participates in static process-wide state for default resources, deprecated-key mappings, and existing-configuration reloads. It persists through `Writable` `write`/`readFields` and through `writeXml`, while `dumpConfiguration` emits a JSON-like diagnostic view with value, final flag, and resource/source information.

Configuration resources are XML inputs from classpath names, URLs, local `Path`s, streams, or other `Configuration` instances. Stream resources are documented as cached in memory and closed after loading, making them a state-retention risk for large inputs. Final parameters persist in the in-memory loaded properties and prevent later resource override until reload.

Variable expansion pulls from configuration properties, environment variables prefixed with `env.`, and Java system properties unless restriction flags block system property use. This means returned values may depend on process environment and system properties, not only XML files.

`KeyProvider` state is provider-specific but contractually includes key names, key metadata, versioned key material, caches, password availability, and persistent backing stores. `flush()` is the explicit durability boundary for changes. `isTransient()` identifies providers that should not be treated as long-term storage.

`AbstractFileSystem` has per-instance URI/statistics state and static process-wide statistics tables keyed by scheme/authority. Concrete implementations persist namespace and data in their backing stores, but this API makes persistence visible only through filesystem operations and metadata calls.

`BlockLocation` is a mutable serializable value object. Its state includes hostnames, cached hostnames, host:port names, topology paths, storage IDs, storage types, offset, length, and corrupt flag.

`ChecksumFileSystem` persists checksum data as separate checksum files associated with raw data files. Its state also includes checksum verification/write booleans and bytes-per-checksum configuration. Rename/delete/copy operations must keep data and checksum files consistent.

`CommonConfigurationKeysPublic` is immutable constant state compiled into the API. The constants map string keys and defaults to broader Hadoop subsystems.

`ContentSummary` is `Writable`, so its count/size/quota summary fields have serialized form. Its string output is also a public compatibility surface for shell/UI consumers that parse summary output.

## Dependencies and Integration Points

This chunk integrates with Java standard APIs including `IllegalArgumentException`, `IOException`, `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `Reader`, `Writer`, `File`, `URL`, `URI`, `InetSocketAddress`, `ClassLoader`, regex `Pattern`, collections, `TimeUnit`, `ByteBuffer`, `Serializable`, and security `NoSuchAlgorithmException`.

Hadoop dependencies include `Path`, `FileContext`, `FileSystem`, `FilterFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FsServerDefaults`, `FsStatus`, `FileStatus`, `FileChecksum`, `BlockLocation`, `BlockStoragePolicySpi`, `StorageType`, `RemoteIterator`, `Options.CreateOpts`, `Options.Rename`, `Options.ChecksumOpt`, `FsPermission`, `AclStatus`, `AclEntry`, `XAttrSetFlag`, `Progressable`, `AccessControlException`, and `Writable`.

`Configuration` is an integration hub for nearly every other component: `Configured` stores it, `KeyProvider` and factories initialize from it, `AbstractFileSystem` discovery uses it, and `CommonConfigurationKeysPublic` defines the public keys consumed throughout Hadoop Common, HDFS, YARN, MapReduce, KMS, IPC, security, crypto, and shell tooling.

`KeyProviderFactory` integrates with Java service loading and configuration URI paths. Provider implementations outside this chunk must register factories for URI schemes such as local Java keystores, user providers, or KMS providers.

`AbstractFileSystem` integrates with `FileContext` rather than the older `FileSystem` API. Its Javadocs repeatedly define behavior by reference to `FileContext` methods, with additional constraints such as fully qualified paths and pre-applied umask permissions.

`AvroFSInput` is an explicit third-party integration point with Apache Avro's `SeekableInput`.

`ChecksumFileSystem` integrates the old `FileSystem` hierarchy with checksum sidecar behavior and raw filesystem delegation.

## Risks and Edge Cases

- JDiff omits method bodies, nested type definitions beyond referenced names, default values for constants, and exact serialization layout. Implementation source is needed before changing behavior.
- `Configuration` has process-wide mutable static state for deprecations, default resources, and existing-instance reloads. Tests and long-lived services can interfere with each other if they mutate global defaults or deprecation mappings.
- Deprecation registration is documented as developer-only and unsupported after resources have loaded. Late registration can throw `UnsupportedOperationException` and can create inconsistent alias visibility.
- Final parameters can silently prevent later resources from overriding values. Debugging depends on `getPropertySources`, `writeXml`, and `dumpConfiguration` preserving source/final metadata.
- Variable expansion can read environment variables and system properties. That is convenient but can leak ambient process state into configuration values and can make tests nondeterministic unless restriction settings are used.
- InputStream resources are cached and closed later, increasing memory pressure for large resources and making stream lifecycle subtle.
- Boolean getters return the default on invalid values, unlike numeric getters that throw. Misconfigured booleans can therefore fail open or fail closed depending on defaults.
- `getLongBytes`, time-duration parsing, and storage-size parsing depend on suffix interpretation. Case, missing units, and overflow boundaries need explicit tests.
- Password fallback to clear text is security-sensitive. `getPassword` callers must understand whether `HADOOP_SECURITY_CREDENTIAL_CLEAR_TEXT_FALLBACK` is enabled and whether credential provider paths are configured.
- `getClass`, `getInstances`, and filesystem/provider factory discovery load classes by name from configuration. Bad class names, wrong interfaces, or hostile classpaths can fail late or load unexpected code.
- `KeyProvider` implementations must be thread safe. Cache invalidation, key rollover, and `flush` semantics are high-risk because stale key material can break encryption/decryption or weaken rotation guarantees.
- `needsPassword` indicates a provider cannot operate normally without a password discovered through normal means. Callers that ignore it may get delayed failures or accidentally create transient/incomplete provider state.
- `AbstractFileSystem` has many optional features. Default unsupported behavior for symlinks, ACLs, xattrs, snapshots, storage policies, truncate, and checksums must be visible to callers through expected exceptions.
- Rename semantics are nuanced: the no-overwrite abstract method and overwrite-aware default method must preserve FileContext behavior, especially around existing destinations, parent-not-directory cases, and cross-filesystem paths.
- `checkPath` and URI authority handling are compatibility-sensitive. Wrong normalization can accept paths for the wrong filesystem or reject valid default-port paths.
- Static filesystem statistics can accumulate across tests and long-running processes unless `clearStatistics` is used.
- `BlockLocation` exposes mutable arrays through getters/setters unless implementations defensively copy. Consumers should avoid mutating returned arrays unless the implementation contract allows it.
- `ChecksumFileSystem` must keep sidecar checksum files consistent during append, truncate, rename, delete, and local copy. Partial failures can leave data and checksums mismatched.
- `CommonConfigurationKeysPublic` has deprecated IO sort constants moved to MapReduce while still public for compatibility. Removing or renaming them would break downstream code.
- `ContentSummary` constructors are documented as deprecated by builder usage but not marked deprecated in the XML metadata. Consumers may continue to compile against them, so compatibility must be preserved.
- `CreateFlag.validate` is only partially visible in this chunk; enum constants and later methods are outside the assigned range and must be merged from the next chunk.

## Test Signals

Useful validation around this API surface should include:

- API compatibility tests over the JDiff surface: public/protected signatures, deprecation metadata, `static`/`final`/`abstract` attributes, checked exceptions, and constants remain stable.
- `Configuration` resource-order tests for default resources, added resources, final-property blocking, reload behavior, cloning, `clear`, `size`, iteration, and property-source ordering.
- Deprecation tests for old-to-new aliases, multiple replacement keys, custom messages, no override of existing mappings, warning-once behavior, late registration failure, and `setDeprecatedProperties`.
- Variable expansion tests for nested config properties, Java system properties, `env.NAME`, `env.NAME:-default`, `env.NAME-default`, missing values, raw lookup, trimmed lookup, and restricted system-property mode.
- Typed getter/setter tests for all primitive conversions, invalid numeric exceptions, invalid boolean defaults, byte suffixes, time suffixes, storage units, regex patterns, integer ranges, string collections, and null-value testing mode.
- Credential tests for provider alias lookup, clear-text fallback enabled/disabled, missing aliases, IO failures, and password char-array behavior.
- Socket/class/path helper tests for wildcard listener replacement, bind-host/client-address split, class-not-found/null behavior, interface enforcement, instance creation, classloader override, local directory selection by path hash, and missing resource streams/readers.
- XML/diagnostic serialization tests for `writeXml`, property-specific `writeXml`, invalid property errors, `dumpConfiguration` single/all-property output, final flags, sources, and exclusion of stream-loaded properties where documented.
- `Writable` round-trip tests for `Configuration`, `ContentSummary`, and other visible writable types.
- `KeyProvider` contract tests using fake providers: create/delete/roll/get current versions, metadata bulk lookup, generated material size/algorithm, version-name parsing/building, cache invalidation, `flush` durability, close, provider search, password warnings/errors, transient-provider flag, and thread-safety under concurrent calls.
- `KeyProviderFactory` tests for configured URI lists, unknown URI schemes returning null, IO exception propagation, service-loader discovery, and provider ordering.
- `AbstractFileSystem` implementation tests with a minimal fake filesystem: URI scheme/authority validation, default-port normalization, class discovery via `fs.AbstractFileSystem.<scheme>.impl`, statistics accounting/clearing, path qualification, checkPath failures, create option parsing, rename overwrite/no-overwrite behavior, open/create/delete/mkdir errors, and optional-feature unsupported exceptions.
- File metadata tests for ACL, xattr, snapshot, storage policy, symlink, checksum, corrupt block, block location, fs status, and canonical service name behavior.
- `AvroFSInput` tests for length, read, seek, tell, close, and FileContext constructor behavior.
- `BlockLocation` tests for constructor variants, copy constructor, cached hosts, topology paths, storage IDs/types, corrupt flag, mutability/defensive-copy expectations, and `toString`.
- Stream capability tests for `ByteBufferReadable`, drop-behind, readahead, and unbuffer support including unsupported-operation paths.
- `ChecksumFileSystem` tests for checksum file naming, length formulas, open verification, write checksum toggles, append/truncate consistency, rename/delete/list filtering, local copy with/without CRCs, checksum failure reporting, raw filesystem delegation, and metadata forwarding.
- `CommonConfigurationKeysPublic` tests should assert key/default constant values against `core-default.xml` and guard deprecated constant presence.
- `ContentSummary` tests for getters, equality/hash code, header fields, quota header fields, output formatting under quota/human-readable/storage-type/snapshot flags, erasure-coding policy display, and builder-versus-constructor compatibility.

## Cross-Chunk Notes

This is the first chunk for `Apache_Hadoop_Common_3.1.2.xml` and starts at the XML header. It ends mid-`CreateFlag`; enum constants and the rest of the `org.apache.hadoop.fs` API are in later chunks. The final per-file report should reconcile this chunk with later filesystem chunks before making complete statements about `CreateFlag`, `FileSystem`, path APIs, permission types, and the rest of Hadoop Common 3.1.2.

### subset-b-007187: lines 6131-12080

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml lines 6131-12080

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.1.2, not implementation source. It starts inside the tail of `org.apache.hadoop.fs.CreateFlag`, fully covers `FileAlreadyExistsException`, `FileChecksum`, `FileContext`, `FileStatus`, `FileSystem`, and `FileUtil`, then ends inside the beginning of `FilterFileSystem`.

The research surface is the public and protected compatibility contract: class names, inheritance, implemented interfaces, constructors, method signatures, checked exceptions, public/protected fields, static/final/abstract/synchronized flags, deprecation markers, and embedded Javadocs. Runtime algorithms must be confirmed against Java implementation files, but this XML is authoritative for the release API snapshot used by JDiff.

## Purpose

The covered APIs define Hadoop Common's core filesystem client surface.

`CreateFlag` describes creation and append semantics for file creation APIs: create, append, overwrite, sync blocks, lazy persistence, and appending into a new block. The visible tail documents validation helpers and invalid flag combinations.

`FileAlreadyExistsException` is the checked I/O exception used when an operation targets an existing path and overwrite semantics were not requested.

`FileChecksum` is the abstract checksum value contract for files. It is serializable through Hadoop `Writable`, exposes algorithm name, checksum length, raw bytes, checksum options, equality, and hashing.

`FileContext` is Hadoop's newer filesystem facade, modeled as per-client filesystem state. It carries a default `AbstractFileSystem`, user identity, working-directory resolution, and umask, and exposes high-level operations for creation, deletion, listing, status, symlinks, ACLs, xattrs, snapshots, and storage policies.

`FileStatus` is the client-side metadata record for a file, directory, or symlink. It stores length, type, replication, block size, times, permission, owner, group, path, symlink target, and attribute flags for ACL, encryption, erasure coding, and snapshot support.

`FileSystem` is the older abstract base class for local, distributed, object-store, and third-party filesystems. It defines instance caching, URI qualification, initialization, stream creation/opening, directory and metadata operations, local-copy helpers, statistics, trash, storage policies, and builder APIs.

`FileUtil` is a static utility class for local and cross-filesystem file processing: deletion, copying, shell path conversion, disk usage, archive extraction, symlinks, chmod/chown/permission portability, temp-file creation, replacement, listing wrappers, and classpath-manifest jar creation.

The visible `FilterFileSystem` portion defines a `FileSystem` wrapper that delegates operations to a raw underlying `FileSystem`, useful for layered filesystem behavior.

## Important APIs, Types, and Functions

### CreateFlag Tail

- `validate(Object path, boolean pathExists, EnumSet flag)` validates create semantics and throws `IOException` or `HadoopIllegalArgumentException`.
- `validateForAppend(EnumSet flag)` requires `APPEND` and rejects `OVERWRITE`.
- Documented flags include `CREATE`, `APPEND`, `OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`.
- Invalid combinations are `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`.

### FileAlreadyExistsException and FileChecksum

- `FileAlreadyExistsException` extends `IOException` and has empty and message constructors.
- `FileChecksum` implements `Writable` and declares abstract `getAlgorithmName()`, `getLength()`, and `getBytes()`.
- `getChecksumOpt()` returns `Options.ChecksumOpt`.
- `equals(Object)` is defined around algorithm and checksum value equality; `hashCode()` completes the value contract.

### FileContext

- Factory methods build contexts from an `AbstractFileSystem`, default config, local FS, `URI`, or explicit `Configuration`.
- Path and identity APIs include `getFSofPath(Path)`, `setWorkingDirectory(Path)`, `getWorkingDirectory()`, `getUgi()`, `getHomeDirectory()`, `getUMask()`, `setUMask(FsPermission)`, `resolvePath(Path)`, and `makeQualified(Path)`.
- File operations include `create(Path, EnumSet<CreateFlag>, Options.CreateOpts...)`, `mkdir(Path, FsPermission, boolean)`, `delete(Path, boolean)`, `open(Path)`, `open(Path, int)`, `truncate(Path, long)`, `setReplication(Path, short)`, and `rename(Path, Path, Options.Rename...)`.
- Metadata and link operations include `setPermission`, `setOwner`, `setTimes`, `getFileChecksum`, `setVerifyChecksum`, `getFileStatus`, `getFileLinkStatus`, `getLinkTarget`, `getFsStatus`, and `createSymlink`.
- Listing APIs return `RemoteIterator` for `listStatus`, `listLocatedStatus`, and `listCorruptFileBlocks`.
- Lifecycle and utilities include `deleteOnExit(Path)`, `util()`, protected symlink-resolution helpers, and static statistics helpers.
- Security and namespace extensions include ACL mutation/read APIs, xattr mutation/read/list/remove APIs, snapshot create/rename/delete, and storage policy set/unset/get/list.
- Public fields include `LOG`, compatibility `DEFAULT_PERM`, preferred `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`, plus `SHUTDOWN_HOOK_PRIORITY`.

### FileStatus

- Implements `Writable`, `Comparable`, `Serializable`, and `ObjectInputValidation`.
- Constructors cover no-arg deserialization, basic metadata, metadata without symlink support, symlink targets, boolean attribute triples, explicit attribute sets, and copy construction.
- Static `attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts booleans into a set of attribute flags; `NONE` is the shared empty attribute set.
- Accessors expose length, `isFile()`, `isDirectory()`, deprecated `isDir()`, `isSymlink()`, block size, replication, modification/access time, permissions, ACL/encryption/erasure-coded/snapshot flags, owner, group, path, and symlink target.
- Protected setters normalize permission, owner, and group defaults; public setters exist for path and symlink.
- `compareTo(FileStatus)`, binary-compatible `compareTo(Object)`, `equals(Object)`, and `hashCode()` are path-based.
- `readFields(DataInput)` and `write(DataOutput)` are deprecated in favor of `PBHelper` and protobuf serialization; `validateObject()` supports Java deserialization validation.

### FileSystem

- Extends `Configured`, implements `Closeable` and `DelegationTokenIssuer`, and has a protected constructor.
- Static acquisition and cache APIs include `get(URI, Configuration, String)`, `get(Configuration)`, `get(URI, Configuration)`, `newInstance(...)`, `newInstanceLocal(Configuration)`, `closeAll()`, and `closeAllForUGI(UserGroupInformation)`.
- Default filesystem helpers include `getDefaultUri(Configuration)`, `setDefaultUri(Configuration, URI/String)`, `getLocal(Configuration)`, deprecated `getNamed`, deprecated `getName`, and `getFileSystemClass(String, Configuration)`.
- Initialization and URI APIs include `initialize(URI, Configuration)`, `getScheme()`, abstract `getUri()`, `getCanonicalUri()`, `canonicalizeUri(URI)`, `getDefaultPort()`, `checkPath(Path)`, `makeQualified(Path)`, and protected `getFSofPath(Path, Configuration)`.
- Token integration is via `getCanonicalServiceName()`, whose default behavior uses URI and port when the filesystem has its own tokens.
- Stream and creation APIs include abstract `open(Path, int)`, `open(Path)`, `open(PathHandle)`, `open(PathHandle, int)`, `getPathHandle(FileStatus, HandleOpt...)`, protected `createPathHandle(...)`, many `create(...)` overloads, `primitiveCreate`, `primitiveMkdir`, `createNonRecursive`, `createNewFile`, `append(...)`, and builder APIs `createFile(Path)` and `appendFile(Path)`.
- Mutation APIs include `mkdirs`, `concat`, `setReplication`, `rename`, `truncate`, `delete`, `deleteOnExit`, `cancelDeleteOnExit`, `processDeleteOnExit`, permission/owner/time setters, ACLs, xattrs, snapshots, storage policy operations, and symlink operations.
- Query APIs include block locations, server defaults, resolve path, content summary, quota usage, status/link status, existence/type/length helpers, listings, globbing, located listings, recursive file listings, home/working directory, checksums, filesystem capacity status, used bytes, block size/default block size/default replication, trash roots, storage statistics, and global statistics.
- Public fields include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and protected per-instance `statistics`.

### FileUtil

- `stat2Paths(...)` converts `FileStatus[]` to `Path[]`, optionally returning a default path when stats are null.
- Deletion utilities include `fullyDeleteOnExit(File)`, `fullyDelete(File)`, `fullyDelete(File, boolean)`, deprecated `fullyDelete(FileSystem, Path)`, `fullyDeleteContents(File)`, and `fullyDeleteContents(File, boolean)`.
- Copy utilities cover filesystem-to-filesystem, multi-source filesystem copy, `FileStatus`-based copy, local-to-filesystem, and filesystem-to-local overloads with delete-source and overwrite options.
- Shell/local utilities include `readLink(File)`, `makeShellPath(...)`, `makeSecureShellPath(File)`, `getDU(File)`, `symLink(String, String)`, `chmod(...)`, `setOwner(File, String, String)`, permission and access wrappers, `setPermission(File, FsPermission)`, `createLocalTempFile`, `replaceFile`, `listFiles(File)`, and `list(File)`.
- Archive and classpath helpers include `unZip(InputStream/File, File)`, `unTar(InputStream, File, boolean)`, `unTar(File, File)`, `createJarWithClassPath(...)`, and `getJarsInDirectory(...)`.
- `SYMLINK_NO_PRIVILEGE` is the public return-code constant for Windows symlink privilege failure.

### FilterFileSystem Beginning

- Constructors allow empty construction or wrapping a raw `FileSystem`.
- `getRawFileSystem()` exposes the wrapped filesystem.
- Visible overrides/delegations include `initialize`, URI/canonicalization, qualification/checking, block locations, `resolvePath`, `open(Path, int)`, `open(PathHandle, int)`, `createPathHandle`, `append`, `concat`, and the beginning of `create(...)`.

## Control Flow

The XML itself has no executable control flow, but the APIs define several important runtime paths.

`FileContext` path handling first qualifies relative or slash-relative paths using its default filesystem and working directory, then routes the operation to the `AbstractFileSystem` returned by `getFSofPath`. Symlink and mount-point resolution is explicit in `resolvePath`, while `setWorkingDirectory` is documented as string-prefix resolution rather than Unix inode-relative state.

`FileContext.create` and `FileSystem.create` both depend on `CreateFlag` and option validation. The API distinguishes "create if absent", "append if present", and "overwrite existing" semantics; invalid flag combinations fail before or during the actual filesystem operation. Permission flow applies umask for normal creation, while static `FileSystem.create(fs, file, permission)` and `mkdirs(fs, dir, permission)` intentionally set the exact requested permission after creation to avoid thread-unsafe configuration mutation.

`FileSystem.get(URI, Configuration)` follows a cache decision path: if `fs.$SCHEME.impl.disable.cache` is true, construct and initialize a new instance without caching; otherwise return a matching cached instance or create, initialize, cache, and return a new one. `newInstance(...)` variants always construct unique instances. `close()`, `closeAll()`, and `closeAllForUGI()` release cached resources and process delete-on-exit queues.

`FileSystem.initialize` is a required superclass-forwarding hook for subclasses. Subclasses may alter configuration before or after calling the superclass, but callers rely on initialization completing before use.

Read flow opens `FSDataInputStream` by path or, if supported, by `PathHandle`. The `PathHandle` path checks encoded constraints such as path, content identity, or metadata stability; unsupported filesystems throw `UnsupportedOperationException`.

Listing and glob flow uses eager arrays for `listStatus`/`globStatus` and remote iterators for `listLocatedStatus`, `listStatusIterator`, `listFiles`, `FileContext.listStatus`, and related APIs. The docs explicitly warn that some iterator flows do not guarantee sorted order.

Metadata extension flow for ACLs, xattrs, snapshots, and storage policies is exposed on both `FileContext` and `FileSystem`. The default `FileSystem` contract often permits `UnsupportedOperationException`, while HDFS-backed implementations are expected to provide behavior.

`FileUtil` deletion flow distinguishes symlink deletion from target deletion for `fullyDelete(File)`, but `fullyDeleteContents(File)` follows a symlink to a directory and deletes the target directory contents. Copy flow composes source and destination `FileSystem` handles, paths or local files, delete-source semantics, overwrite policy, and `Configuration`.

`FilterFileSystem` control flow is delegation: wrapper methods should validate/qualify through the wrapper where required and forward actual operations to the raw filesystem. The chunk ends before the full delegation surface is visible.

## State and Persistence Behavior

This JDiff file persists API metadata for compatibility checking. It does not store live Hadoop runtime state.

`FileContext` contains client-side, in-memory state: default filesystem, working directory, user/group identity, umask, delete-on-exit registrations, and statistics access. Its operations mutate remote filesystem namespace state through the selected `AbstractFileSystem`: file contents, directories, symlinks, permissions, ACLs, xattrs, snapshots, storage policies, ownership, timestamps, replication, and truncation.

`FileStatus` is a serializable metadata value object. Its `Writable` stream methods remain for compatibility but are deprecated in favor of protobuf conversion. Equality, ordering, and hashing are path-based, which means metadata changes on the same path do not change equality identity.

`FileChecksum` is a `Writable` value contract. Durable equality depends on both algorithm name and raw bytes, while `getChecksumOpt()` connects a checksum value back to checksum configuration.

`FileSystem` has substantial process-local global state: cached filesystem instances, global statistics, global storage statistics, symlink enablement, default filesystem configuration keys, shutdown hooks, and delete-on-exit queues. Individual instances maintain configuration and protected `statistics`. Persistent effects are delegated to concrete filesystems and may be local disk state, HDFS namespace/block state, object-store objects, or third-party backend state.

`FileUtil` is mostly stateless, but many methods produce durable local or filesystem side effects: recursive deletion, permission and owner changes, symlink creation, archive extraction, temp-file creation, file replacement, copy, and optional source deletion. `createJarWithClassPath` creates a small manifest jar and returns paths describing generated and unexpanded wildcard entries.

`FilterFileSystem` stores a raw wrapped `FileSystem` reference. Its durable behavior should mirror the wrapped filesystem unless the filter subclass modifies semantics.

## Dependencies and Integration Points

The chunk is centered on `org.apache.hadoop.fs` and integrates with:

- Java core types: `URI`, `File`, `IOException`, `FileNotFoundException`, `DataInput`, `DataOutput`, `Serializable`, `ObjectInputValidation`, collections, streams, and concurrency exceptions for untar helpers.
- Hadoop configuration and identity: `Configuration`, `Configured`, `UserGroupInformation`, `AccessControlException`, and delegation-token service naming.
- Hadoop filesystem primitives: `Path`, `AbstractFileSystem`, `FileSystem`, `LocalFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `PathHandle`, `RemoteIterator`, `BlockLocation`, `FsStatus`, `FsServerDefaults`, `ContentSummary`, `QuotaUsage`, `BlockStoragePolicySpi`, `StorageStatistics`, and `GlobalStorageStatistics`.
- Hadoop permission and metadata APIs: `FsPermission`, `AclStatus`, ACL entry lists, xattr set flags, checksum options, and create/rename/handle options.
- Hadoop utility APIs: `Progressable`, `Writable`, `PBHelper`, `NetUtils`, `SecurityUtil`, service discovery through `ServiceLoader`, and logging through SLF4J or Commons Logging.
- HDFS-specific behavior: block locations, replication, erasure-coded logical block groups, snapshots, xattrs, storage policies, and HDFS as the documented normative behavior source when docs disagree with implementation.

Integration-sensitive points are filesystem plugin discovery by URI scheme, caching keyed by URI/user/configuration behavior, statistics registration, token canonical service naming, and the compatibility bridge between `FileSystem` and newer `FileContext`/`AbstractFileSystem` APIs.

## Risks and Edge Cases

- This chunk begins and ends mid-class. The previous chunk is required for complete `CreateFlag`; the next chunk is required for complete `FilterFileSystem`.
- JDiff does not show method bodies. Exact cache keys, permission application, path normalization, retry behavior, RPC details, and exception messages require Java implementation review.
- `CreateFlag` combinations are easy to misuse. In particular, `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE` must fail, while `CREATE|APPEND` and `CREATE|OVERWRITE` have different existence semantics.
- `FileContext.setWorkingDirectory` does not follow symlinks like a Unix process working directory. Code that assumes inode-like working directory behavior can resolve later relative paths differently than expected.
- `FileStatus.equals` and `hashCode` are path-based. Caches keyed by `FileStatus` can miss metadata changes if they assume equality covers length, permission, timestamps, or file type.
- `FileStatus.readFields`/`write` are deprecated but public. Removing or changing their protobuf-backed format would break old clients and serialized compatibility.
- `FileSystem.get` returns cached shared instances unless cache is disabled. Closing a shared instance can break other users; using `newInstance` avoids sharing but increases resource usage.
- `FileSystem.close()` makes later use of the instance and its streams undefined. Tests and applications must avoid reusing streams after filesystem closure.
- `FileSystem.initialize` overriding is fragile because subclasses must call the superclass. Skipping it can corrupt cache/statistics/configuration setup.
- `getFileBlockLocations` has special behavior for nonexistent paths, zero-length regions, default local locations, and HDFS erasure-coded logical block groups. Consumers must handle null, empty arrays, and logical rather than physical block semantics.
- Many optional APIs default to `UnsupportedOperationException`: path handles, symlinks, ACLs, xattrs, snapshots, and storage policies depend on concrete filesystem support.
- Trash-root defaults are user-home based, while object stores and multi-root filesystems may override them. Delete-to-trash code must not hardcode `/user/$USER/.Trash`.
- Global statistics APIs are synchronized and some are deprecated in favor of `GlobalStorageStatistics`; both old and new stats may need validation during compatibility work.
- `FileUtil.fullyDelete` can leave partial deletion on failure. `fullyDeleteContents` follows directory symlinks and deletes target contents, unlike `fullyDelete` symlink handling.
- `FileUtil.readLink` returns an empty string both for non-symlinks and errors, collapsing distinct states.
- `FileUtil.makeSecureShellPath` exists because shell path conversion can otherwise permit script injection. Callers should use the secure variant for untrusted local paths.
- `FileUtil.unTar(InputStream, ...)` can throw `InterruptedException` and `ExecutionException`, suggesting asynchronous or shell-backed extraction paths that must be tested under interruption and command failure.
- Windows behavior is explicitly different for symlink privilege failures, chmod/access checks, and executable permission revocation on directories.
- `createJarWithClassPath` expands environment variables and wildcards differently on Windows versus Unix-like systems. Manifest classpath behavior can diverge from process classpath behavior.

## Test Signals

Useful validation for this API surface should include:

- JDiff/API compatibility tests ensuring all visible classes, constructors, methods, fields, deprecations, and checked exceptions remain stable.
- `CreateFlag` validation tests for every documented create/append/overwrite combination, including invalid mixed append/overwrite cases and `APPEND_NEWBLOCK`, `SYNC_BLOCK`, and `LAZY_PERSIST` preservation.
- `FileChecksum` tests for algorithm/byte equality, hash code consistency, checksum option exposure, and `Writable` round trips in concrete checksum subclasses.
- `FileContext` tests for default/local/URI/config factories, UGI propagation, working-directory resolution, invalid relative-with-scheme paths, umask application, create/mkdir/delete/open/truncate/rename behavior, symlink resolution, delete-on-exit, and statistics.
- `FileContext` metadata tests for ACL merge/remove/replace/read, xattr set/get/list/remove with namespaces and flags, snapshots, storage policies, checksum verification flags, and unsupported-filesystem failure modes.
- `FileStatus` tests for all constructor variants, null permission/owner/group defaults, attribute flag conversion, deprecated `isDir`, symlink target behavior, path-based equality/ordering/hash code, Java deserialization validation, and deprecated `Writable` serialization compatibility.
- `FileSystem` cache tests for default URI selection, scheme implementation loading, `fs.$SCHEME.impl.disable.cache`, user-specific `get`, `newInstance` uniqueness, `closeAll`, `closeAllForUGI`, and use-after-close behavior.
- `FileSystem` operation tests for path qualification/checking, canonical URI/default port handling, token canonical service names, open/create/append overloads, nonrecursive create, path handles and invalid handles, mkdirs, concat, replication, rename options, truncate return semantics, delete/delete-on-exit, glob/list/listFiles ordering expectations, and local copy helpers.
- HDFS-specific signals for block locations, including replicated files and erasure-coded logical block groups, plus snapshots, xattrs, storage policies, ACLs, and trash roots.
- `FileUtil` tests for symlink-safe recursive deletion, partial deletion failure reporting, `fullyDeleteContents` symlink-to-directory behavior, cross-filesystem copy with overwrite/delete-source options, local copy direction, shell path conversion and secure escaping, disk usage, zip/tar extraction, Windows symlink privilege code, chmod/chown/access wrappers, permission setting without forking when possible, temp-file lifecycle, replacement behavior, and list/listFiles throwing `IOException` instead of returning null.
- `createJarWithClassPath` tests for long classpaths, manifest classpath generation, environment expansion on Windows and Unix syntax, wildcard expansion for `.jar` and `.JAR`, target directory handling, and returned path array contract.
- `FilterFileSystem` delegation tests in the next merged report should verify raw filesystem initialization, URI qualification, open/append/create delegation, path-handle delegation, and statistics/close behavior across the full class.

## Cross-Chunk Notes

The previous chunk must supply the beginning of `org.apache.hadoop.fs.CreateFlag`, including enum constants not fully visible here. This chunk closes `CreateFlag` and then covers the major filesystem API classes through most of line 12080.

The next chunk must continue `org.apache.hadoop.fs.FilterFileSystem` from its `create(Path, FsPermission, boolean, int, ...)` method onward. Any final per-file report should avoid treating this chunk's `FilterFileSystem` notes as complete until that adjacent slice is merged.

### subset-b-007188: lines 12081-17950

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml lines 12081-17950

## Research scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.1.2, not Java implementation source. The range begins in the middle of `org.apache.hadoop.fs.FilterFileSystem`, covers much of the public filesystem API surface, then moves through FTP, ViewFS, HA protocol, protocol-buffer bridge interfaces, HTTP package documentation, and the beginning of `org.apache.hadoop.io` Writable types. Research conclusions below are therefore based on signatures, inheritance, visibility, declared exceptions, constants, and embedded Javadocs.

## Purpose

The chunk documents Hadoop Common's client-side filesystem abstraction layer and adjacent support contracts. It describes how generic `FileSystem` calls are delegated or adapted by wrappers such as `FilterFileSystem`, local implementations such as `RawLocalFileSystem` and `LocalFileSystem`, protocol-backed filesystems such as `FTPFileSystem`, and mount-table based filesystems such as `ViewFileSystem` and `ViewFs`. It also captures stream primitives, path and handle abstractions, quota/status/statistics value objects, trash policy hooks, xattr helpers, storage policy entry points, HA failover/fencing protocols, and the start of Hadoop's serializable `Writable` containers.

## Important APIs and types

The chunk starts with the tail of `org.apache.hadoop.fs.FilterFileSystem`, a delegating `FileSystem` wrapper with protected state `fs` and `swapScheme`. Its methods forward or adapt nearly the full filesystem contract: create/open/append, non-recursive creation, rename/truncate/delete, list status and located status, local-copy helpers, server defaults, file status, ACLs, xattrs, storage policies, snapshot operations, trash roots, and the newer `createFile`/`appendFile` builder entry points. The important integration contract is that subclasses can intercept selected calls while default behavior passes requests to the contained filesystem.

`org.apache.hadoop.fs.FsConstants` defines shared filesystem constants including local, FTP, and ViewFS schemes/URIs and `MAX_PATH_LINKS`, which are scheme-resolution and symlink traversal guardrails.

`FSDataInputStream`, `FSInputStream`, `PositionedReadable`, `Seekable`, `StreamCapabilities`, and `Syncable` define the stream contract. `FSDataInputStream` wraps an input stream and implements seeking, positional reads, byte-buffer reads, enhanced buffer access, file descriptor access, readahead/drop-behind hints, unbuffering, and capability probing. `FSDataOutputStream` wraps output streams and adds position, close, `hflush`, `hsync`, drop-behind, and capability checks. `FSDataOutputStreamBuilder` is the abstract builder for create/append, covering permission, buffer size, replication, block size, recursive parent creation, progress callbacks, checksum options, optional and mandatory FS-specific options, and `build()`.

`FsServerDefaults` and `FsStatus` are `Writable` value objects. Server defaults expose block size, bytes-per-checksum, packet size, replication, file buffer size, encrypted transfer flag, trash interval, checksum type, key provider URI, and default storage policy id. `FsStatus` serializes capacity, used, and remaining bytes.

`GlobalStorageStatistics` stores named `StorageStatistics` instances with synchronized `get`, `put`, `reset`, and iterator methods. `StorageStatistics` supplies a named statistics interface with long-stat iterators, lookup, tracked checks, and reset.

`GlobFilter`, `Path`, `PathFilter`, `PathHandle`, `InvalidPathException`, and `InvalidPathHandleException` form the path-selection and path-identity layer. `Path` supports URI construction, parent/name/suffix operations, qualification, comparison, depth, serialization validation, and cross-platform constants. `PathHandle` is an opaque serializable reference with byte serialization; invalid handles can fail if encoded constraints no longer hold.

`QuotaUsage` records namespace and space quota consumption, storage-type quotas and consumption, string/table formatting helpers, and header constants. `StorageType` exposes storage-media classification helpers such as transient, quota-supporting, movable, parse, list, and static arrays.

`RawLocalFileSystem` implements the raw local disk `FileSystem`: path-to-`File` conversion, URI/initialization, open/append/create/createNonRecursive, output stream creation with permissions, rename, Windows empty-directory rename handling, truncate, delete, list, mkdir helpers, working/home directories, local output staging, status, owner/permission/time mutation, symlink support, link status, and link target. `LocalFileSystem` extends `ChecksumFileSystem`, wraps a raw filesystem, and adds checksum-aware local copy and checksum-failure quarantine behavior.

`LocatedFileStatus` extends `FileStatus` with `BlockLocation[]`, exposing constructors for status-plus-locations, erasure/metadata flags, storage policy sets, `getBlockLocations`, mutation, comparison, equality, and hashing.

`Trash` and `TrashPolicy` define pluggable delete-to-trash behavior. `Trash` constructs against a `Configuration` or specific `FileSystem`, moves paths to the appropriate volume's trash, checkpoints, expunges old checkpoints, exposes emptier runnables, and resolves current trash directories. `TrashPolicy` is the abstract policy with initialization, enablement, move, checkpoint, delete checkpoint, current trash, emptier, and factory methods. It holds protected `fs`, `trash`, and `deletionInterval` state.

`XAttrCodec` encodes and decodes xattr byte values to text, hex, or base64 string forms. `XAttrSetFlag.validate` checks create/replace semantics for xattr mutation.

`org.apache.hadoop.fs.ftp.FTPFileSystem` is a `FileSystem` backed by Apache Commons Net. It exposes FTP-specific configuration constants for user, host, port, password, data connection mode, transfer mode, and same-directory rename behavior. Its API includes scheme/default-port/initialize, open/create, unsupported append, delete, URI, listing, status, mkdirs, rename, and working/home directory handling.

`org.apache.hadoop.fs.viewfs.ViewFileSystem` and `ViewFs` implement mount-table based client-side filesystem views for the old `FileSystem` and newer `AbstractFileSystem` APIs respectively. They resolve logical paths to target filesystems and proxy create/open/append/delete/list/status/block-location/checksum/access/rename/truncate/owner/permission/replication/time/ACL/xattr/snapshot/storage-policy/trash/status/used operations. They also expose mount points, child filesystems, and delegation-token collection. `NotInMountpointException` represents calls against paths that are not mounted through ViewFS. `ViewFileSystemUtil.getStatus` aggregates status across ViewFS paths.

The HA package introduces failover and fencing contracts: `FenceMethod`, `HAServiceProtocol`, `HAServiceProtocolHelper`, `HAServiceTarget`, and exceptions for bad fencing configuration, failed failover, failed health checks, and failed service transitions. `HAServiceProtocol` defines `monitorHealth`, `transitionToActive`, `transitionToStandby`, `getServiceStatus`, and `versionID`. `HAServiceTarget` provides service, health monitor, and ZKFC addresses; fencer access; pre-flight fencing validation; RPC proxy construction; fencing parameter maps; and auto-failover enablement. Protocol bridge interfaces `HAServiceProtocolPB` and `ZKFCProtocolPB` extend generated protobuf blocking interfaces plus `VersionedProtocol`.

The `org.apache.hadoop.io` section starts with `AbstractMapWritable`, `ArrayFile`, `ArrayPrimitiveWritable`, and the opening of `ArrayWritable`. `AbstractMapWritable` is a configurable `Writable` base that carries class-id maps per map instance, supports synchronized class registration and copy, and serializes/deserializes those maps. `ArrayPrimitiveWritable` wraps primitive arrays without copying and serializes them in an optimized wire format. `ArrayFile` is a dense file-based integer-to-value mapping extending `MapFile`.

## Control flow and behavior

Most filesystem operations in this chunk follow a dispatch pattern: a high-level `FileSystem` API method accepts a logical `Path`, resolves or qualifies it, and delegates to an underlying raw filesystem, wrapped filesystem, FTP client, or ViewFS mount target. `FilterFileSystem` is the purest delegator; `ViewFileSystem` and `ViewFs` add a mount-point resolution step and then forward to the resolved target. Local filesystems convert `Path` to `java.io.File` and perform OS-backed operations.

Stream control flow is capability-driven. Input streams support sequential reads, positional reads, and optional enhanced buffer operations; callers are expected to check or tolerate capability failures for readahead, drop-behind, unbuffer, and enhanced byte buffers. Output streams similarly expose flush/sync behavior through `Syncable` and advertised capabilities. `FSDataOutputStreamBuilder` accumulates create/append parameters, separates optional from mandatory FS-specific keys, and defers validation and actual stream creation until `build()`.

Trash behavior is policy-mediated. Delete-like workflows may call `Trash.moveToAppropriateTrash`, which resolves symlinks or mount points so deletion lands in the trash for the actual volume containing the path. Policies create checkpoints, delete old checkpoints, and may provide a superuser emptier runnable.

HA control flow is administrative and RPC-oriented. Health monitors periodically call `monitorHealth`; failover controllers request standby/active transitions; fencing is attempted through an ordered list of configured `FenceMethod` implementations, each validating arguments before use and returning success/failure/indeterminate through `tryFence`.

Writable control flow serializes compact metadata alongside payloads. `AbstractMapWritable` writes class-id mappings with the map instance so nested map writables can be reconstructed without relying on global static class registries. `ArrayPrimitiveWritable` records primitive component type and array data, then reconstructs the wrapped array on read.

## State and persistence behavior

Filesystem state is external to these API objects and resides in backing stores: local disk, FTP server state, mounted target filesystems, or distributed filesystems behind the generic interfaces. The chunk exposes stateful client-side wrappers through fields such as `FilterFileSystem.fs`, `FilterFileSystem.swapScheme`, `TrashPolicy.fs`, `TrashPolicy.trash`, and `TrashPolicy.deletionInterval`. `ViewFileSystem`/`ViewFs` hold mount-table derived state implied by mount-point and child-filesystem APIs.

Persistent metadata surfaces include permissions, owners, groups, modification/access times, ACLs, xattrs, snapshots, storage policies, symlinks, checksums, block locations, quota usage, and filesystem capacity accounting. `FsServerDefaults`, `FsStatus`, `AbstractMapWritable`, and `ArrayPrimitiveWritable` explicitly implement `Writable` serialization, indicating RPC or on-disk/wire persistence contracts.

`PathHandle` is a durable opaque reference whose serialized bytes may include constraints used to verify later access. A later `open(PathHandle)` can fail with `InvalidPathHandleException` if the constraints encoded in the handle no longer hold.

## Dependencies and integration points

The filesystem APIs depend heavily on Hadoop common types: `Configuration`, `Path`, `FileSystem`, `AbstractFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `FsPermission`, `FsAction`, `AclStatus`, `Options` families, `RemoteIterator`, `Progressable`, `DataChecksum.Type`, `Writable`, `Configurable`, and security exceptions. Local filesystem implementations integrate with `java.io.File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, and platform-specific behavior, especially Windows rename handling and symlink support.

`FTPFileSystem` integrates with Apache Commons Net and external FTP server configuration. ViewFS integrates with Hadoop mount-table configuration and target filesystems, including delegation token collection across children. HA types integrate with Hadoop IPC, generated protobuf service interfaces, ZKFC protocol, `NodeFencer`, and service-specific target implementations.

The HTTP package documentation records web UI extension integration via `hadoop.http.filter.initializers`, including static-user filtering.

## Risks and edge cases

The snapshot exposes several compatibility and correctness risks:

- `PositionedReadable` requires thread-safe positioned reads, but its Javadoc warns not all filesystems satisfy that requirement. Callers such as HBase-like stores must verify backing filesystem behavior.
- `FSDataInputStream` and `FSDataOutputStream` expose optional capabilities; unsupported readahead, drop-behind, enhanced byte buffers, unbuffering, `hflush`, or `hsync` can break callers that assume all streams implement them.
- `FSDataOutputStreamBuilder.must(...)` is intentionally strict: unsupported mandatory options should cause `build()` to throw `IllegalArgumentException`, while unrelated optional keys may be ignored.
- `RawLocalFileSystem.listStatus` notes returned listings are not sorted because they rely on `File.list()`. Tests and callers must not depend on order.
- `FTPFileSystem.create` warns that streams must be closed before other APIs are used or calls may block. FTP append is declared unsupported.
- ViewFS operations can fail due to mount resolution, unmapped paths, cross-filesystem semantics, target capability differences, `AccessControlException`, `UnresolvedLinkException`, and aggregation across multiple child filesystems.
- Trash placement is nontrivial for symlinks, mount points, and encryption zones. Older `TrashPolicy.getCurrentTrashDir()` is insufficient for encryption-zone-aware deletes; the path-specific overload is the safer API.
- Fencing is operator-configured and may be vendor-specific. Invalid arguments can be detected at startup or runtime, and a failed or indeterminate fence must be treated as unsafe for failover.
- `AbstractMapWritable` class ids range from 1 to 127, limiting the number of distinct classes in one map instance.
- `ArrayPrimitiveWritable` does not copy the wrapped primitive array, so subsequent caller mutation can change serialized or observed content.
- `Path.validateObject` exists to guard deserialized paths; malformed or malicious serialized objects must be rejected.

## Test signals

Useful test coverage for code using or changing the APIs in this chunk should include:

- Delegation tests for `FilterFileSystem` subclasses proving each overridden operation either transforms arguments intentionally or forwards to the wrapped `FileSystem`.
- Stream conformance tests for seek, positioned read, `readFully` EOF behavior, byte-buffer read/release, capability strings, readahead/drop-behind/unbuffer, and output `hflush`/`hsync`.
- Builder tests that cover create vs append flags, overwrite false on existing files, recursive vs non-recursive parent creation, checksum options, optional option ignoring, mandatory option rejection, and invalid parameter exceptions.
- Local filesystem tests for path-to-file conversion, unsorted listing tolerance, recursive delete errors, mkdir idempotency, chmod/chown/time operations, symlink status vs target status, truncate, Windows rename edge cases, and checksum-failure quarantine.
- FTP tests using a controllable FTP server for open/create/list/status/delete/mkdir/rename and explicit validation that append is unsupported and unclosed streams block or prevent concurrent operations as documented.
- ViewFS/ViewFs tests for mount resolution, NotInMountpoint behavior, delegation across target filesystems, ACL/xattr/snapshot/storage-policy forwarding, trash roots, child filesystem enumeration, delegation tokens, access-control propagation, and cross-mount rename/truncate semantics.
- Trash tests for disabled trash, already-in-trash paths, checkpoint/expunge, path-specific trash locations, symlink and mount-point resolution, and encryption-zone aware current trash lookup.
- HA tests for health monitor address fallback, proxy construction timeouts, RemoteException unwrapping in `HAServiceProtocolHelper`, active/standby idempotence, service failure propagation, fencing parameter injection, bad fencing configurations, and auto-failover flag behavior.
- Writable serialization tests for `FsServerDefaults`, `FsStatus`, `AbstractMapWritable`, `ArrayPrimitiveWritable`, and `ArrayWritable` compatibility, including nested map writables, primitive type preservation, class-id limit handling, and no-copy mutation hazards.

### subset-b-007189: lines 17951-24252

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml - subset-b-007189

## Scope

- Source chunk: `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml` lines 17951-24252.
- This is a JDiff XML API snapshot for Apache Hadoop Common 3.1.2, not Java implementation source. It records public/protected type names, inheritance, constructors, methods, fields, deprecation markers, exceptions, parameters, and selected Javadoc text.
- The chunk starts inside `org.apache.hadoop.io.ArrayWritable` and ends inside `org.apache.hadoop.io.compress.SplitCompressionInputStream`; adjacent classes outside this range are intentionally left for neighboring chunks.

## Purpose

This chunk describes Hadoop Common's core binary serialization and compression public APIs. The main purpose is to define stable contracts for:

- `Writable` serialization, deserialization, comparison, and factory construction.
- Primitive and compound writable value wrappers used throughout Hadoop RPC, SequenceFile, MapFile, MapReduce keys and values, and configuration persistence.
- Byte and text handling utilities for Hadoop's binary formats.
- SequenceFile, MapFile, SetFile, and BloomMapFile file-format entry points.
- Compression codec abstractions, stream wrappers, codec lookup, compressor/decompressor pooling, and built-in default/gzip/bzip2 APIs.

Because this is a compatibility descriptor, the important information is the API surface and behavioral promises captured in documentation. Runtime behavior must be verified against the matching Java sources, but this chunk is sufficient to identify the exported contracts and integration points.

## Major API Areas

### Writable Core

- `Writable` defines the central binary serialization interface with `write(DataOutput)` and `readFields(DataInput)`. Implementations must read fields in the same order and representation used by `write`.
- `WritableComparable` combines `Writable` with Java `Comparable`, making writable values usable as sort keys.
- `RawComparator<T>` adds binary comparison over serialized byte ranges through `compare(byte[], int, int, byte[], int, int)`, avoiding full object materialization.
- `WritableComparator` is the main comparator framework. It provides comparator lookup/registration with `get(...)` and `define(...)`, reflective key construction via `newKey()`, object-level and raw byte comparison, byte hashing, and primitive readers such as `readInt`, `readLong`, `readVInt`, and `readVLong`.
- `WritableFactories` and `WritableFactory` provide factory registration and instantiation for writable classes, especially non-public implementations or classes that cannot be constructed directly by ordinary reflection.
- `VersionedWritable` writes and checks a version byte before subclass data; `VersionMismatchException` reports mismatches.

### Primitive Writable Types

The chunk includes writable wrappers for primitive-like scalar values:

- `BooleanWritable`, `ByteWritable`, `ShortWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, and `DoubleWritable`.
- `VIntWritable` and `VLongWritable`, which store integer and long values in variable-length Hadoop encoding.
- Each scalar wrapper exposes a default constructor, a value constructor, `set(...)`, `get()`, `readFields(DataInput)`, `write(DataOutput)`, `equals(Object)`, `hashCode()`, `compareTo(...)`, and `toString()`.

These classes are small state containers around one primitive value. Their public contract is important because Hadoop sort, shuffle, SequenceFile, and RPC paths depend on serialized byte compatibility and stable ordering.

### Byte, Text, and Binary Comparison

- `BinaryComparable` is an abstract base for byte-backed comparable objects. Subclasses implement `getBytes()` and `getLength()`, while the base provides comparison, equality, and hashing over byte ranges.
- `BytesWritable` extends `BinaryComparable` and represents a resizable byte sequence with distinct logical length and backing capacity. It exposes `copyBytes()`, `getBytes()`, `getLength()`, `setSize(int)`, `getCapacity()`, `setCapacity(int)`, `set(BytesWritable)`, `set(byte[], int, int)`, serialization, hashing, equality, and hex-style `toString()`. Deprecated aliases `get()` and `getSize()` point callers to `getBytes()` and `getLength()`.
- `Text` stores standard UTF-8 text and exposes constructors from `String`, `Text`, and `byte[]`; mutable byte operations such as `set(...)`, `append(...)`, and `clear()`; string conversion; serialization with optional maximum length; UTF-8 encode/decode helpers; validation; code point iteration helpers; and `DEFAULT_MAX_LEN`.
- `MD5Hash` is a writable/comparable MD5 value type. It supports construction from bytes or hex string, reading/writing, digest creation from byte arrays, byte array arrays, strings, and input streams, thread-local digester access, half and quarter digest projections, digest copying, hex parsing, equality, hashing, comparison, and `MD5_LEN`.

### Array, Map, Object, and Generic Writables

- `ArrayWritable` represents arrays of a single writable element class, with value-class reporting, conversion to strings/object arrays, `set(Writable[])`, `get()`, and serialization.
- `TwoDArrayWritable` generalizes the array contract to two-dimensional writable matrices.
- `MapWritable` is a writable map with ordinary `Map`-style operations: `clear`, `containsKey`, `containsValue`, `entrySet`, `get`, `put`, `putAll`, `remove`, `size`, `values`, plus `readFields` and `write`.
- `SortedMapWritable` extends the map contract with `SortedMap`-style operations such as `comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, and `tailMap`.
- `EnumSetWritable` wraps an `EnumSet`, carries element type information, implements collection operations, and is configurable through `getConf()` and `setConf(Configuration)`.
- `GenericWritable` wraps one of a fixed set of writable classes supplied by subclasses through `getTypes()`. It stores the concrete instance plus configuration and handles dynamic serialization.
- `ObjectWritable` is the polymorphic writable for `Writable`, `String`, primitive types, arrays, and declared classes. Static `writeObject(...)` and `readObject(...)` methods serialize class metadata plus values; `loadClass(...)` resolves a class name through the active configuration/classloader.
- `NullWritable` is a singleton writable with no payload, used for key or value positions that intentionally carry no data.

### File-Oriented Writable Formats

- `SequenceFile` exposes writer creation APIs and compression defaults for Hadoop's binary flat file of key/value pairs. The chunk lists many overloaded `createWriter(...)` methods, several deprecated in favor of `createWriter(Configuration, Writer.Option...)`, plus `getDefaultCompressionType`, `setDefaultCompressionType`, and `SYNC_INTERVAL`.
- `MapFile` is a directory-backed sorted key/value map built from data and index files. Exposed static helpers include `rename(FileSystem, String, String)`, `delete(FileSystem, String)`, `fix(...)` for rebuilding corrupt indexes, and constants `INDEX_FILE_NAME` and `DATA_FILE_NAME`.
- `SetFile` is a file-backed set of keys.
- `BloomMapFile` extends the MapFile model with a dynamic Bloom filter for fast negative membership checks. It exposes `delete(...)` and constants `BLOOM_FILE_NAME` and `HASH_COUNT`.

### IO Utilities and Stringification

- `IOUtils` provides stream and channel utility methods: multiple `copyBytes(...)` overloads, compressed-data read wrapping, `readFully`, `skipFully`, close/cleanup helpers, socket closing, `writeFully` for channels/file offsets, directory listing, `fsync(...)`, exception wrapping, and `readFullyToByteArray`.
- `Stringifier<T>` defines conversion between objects and string representations plus `close()`.
- `DefaultStringifier<T>` implements the stringifier contract using Hadoop serialization and provides static configuration helpers: `store`, `load`, `storeArray`, and `loadArray`.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`.
- `MultipleIOException` groups multiple `IOException` instances and exposes a convenience constructor method.
- `Closeable` exists only as a deprecated Hadoop interface in favor of `java.io.Closeable`.

### Compression APIs

- `CompressionCodec` is the central codec abstraction. It creates compression/decompression streams, creates compressor/decompressor instances, exposes compressor/decompressor implementation classes, and declares a default file extension.
- `CompressionCodecFactory` discovers codec classes from configuration `io.compression.codecs` and Java `ServiceLoader`, maps path suffixes to codecs, supports lookup by path, class name, or codec name, exposes `setCodecClasses(...)`, `getCodecClasses(...)`, `removeSuffix(...)`, and a small `main(...)` test program. It has a `LOG` field.
- `CodecPool` is a global pool for reusing compressors and decompressors. It leases objects by codec, returns them to the pool, and exposes leased compressor/decompressor counts for testing or diagnostics.
- `Compressor` defines the state machine for stream compression: `setInput`, `needsInput`, optional `setDictionary`, byte counters, `finish`, `finished`, `compress`, `reset`, `end`, and `reinit(Configuration)`.
- `Decompressor` mirrors the decompression state machine: `setInput`, `needsInput`, optional dictionary handling, `needsDictionary`, `finished`, `decompress`, `getRemaining`, `reset`, and `end`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream wrappers around input/output streams. They define close/read or close/flush/write behavior plus `resetState`; the input side also exposes `getPos`, unsupported seek hooks, and `maxAvailableData`.
- `CompressorStream` and `DecompressorStream` are concrete stream adapters around a `Compressor` or `Decompressor`. They maintain protected state fields such as `compressor`, `decompressor`, byte buffers, `closed`, and on decompression `eof`.
- `BlockCompressorStream` and `BlockDecompressorStream` handle block-oriented codecs by splitting input into chunks, writing block-compressed data, reading compressed block payloads, and resetting stream state.
- `BZip2Codec` implements configurable bzip2 streams, including split input stream creation for file splits and `.bz2` as the default extension.
- `DefaultCodec` implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`, providing default stream creation, compressor/decompressor creation, direct decompressor creation, and default extension handling.
- `GzipCodec` extends `DefaultCodec` with gzip-specific stream, compressor, decompressor, direct decompressor, and extension behavior.
- `DirectDecompressionCodec` and `DirectDecompressor` define the direct `ByteBuffer` decompression path.
- `SplitCompressionInputStream` begins in this chunk and exposes construction from an input stream plus start/end offsets and protected `setStart(long)` / `setEnd(long)` mutators. Its remaining API is outside this chunk.

## Control Flow and Behavioral Contracts

Although implementation bodies are not present, the XML documents several important control-flow protocols:

- Writable read/write flow is paired and ordered: callers invoke `write(DataOutput)` to serialize fields and `readFields(DataInput)` to mutate an existing object by reading the same representation back.
- Raw comparison flow avoids object allocation: Hadoop sort components can compare serialized byte ranges through `RawComparator` or optimized `WritableComparator.compare(byte[], ...)`.
- Variable-length integer flow uses first-byte decoding through `WritableUtils.isNegativeVInt`, `decodeVIntSize`, `readVLong`, `readVInt`, and corresponding write helpers. Callers that validate ranges use `readVIntInRange`.
- `CompressedWritable` stores compressed bytes after `readFields` and lazily inflates them. Subclasses must route field access through `ensureInflated()` and implement `readFieldsCompressed(DataInput)` / `writeCompressed(DataOutput)`.
- `GenericWritable` and `ObjectWritable` serialize class identity along with value payloads; deserialization flow includes class lookup and instance construction, so configuration/classloader availability is part of the runtime path.
- `SequenceFile.createWriter(...)` overloads funnel callers toward a writer configured by key/value classes, filesystem/path, buffer size, replication, block size, progress callback, metadata, and compression settings. Newer APIs prefer option objects.
- `MapFile.fix(...)` is a repair path that scans data and rebuilds the index for corrupt map directories.
- Compression streams follow a loop: set input on a compressor/decompressor, call `compress` or `decompress` until output is produced or more input is needed, signal `finish`, observe `finished`, then `reset` for reuse or `end` for disposal.
- `CodecPool` adds a lease/return flow around codec-created compressors and decompressors; callers must return leased objects to prevent pool accounting leaks.
- `Decompressor.finished()` plus `getRemaining()` is documented as the way to detect concatenated compressed data streams; a caller resets before processing the next stream segment.

## State and Persistence Behavior

- Every `Writable` in this chunk persists state to `DataOutput` and restores it from `DataInput`; compatibility depends on exact binary format stability.
- Primitive writable classes persist one scalar field, while variable-length wrappers persist using Hadoop zero-compressed encodings.
- `BytesWritable` and `Text` separate logical length from backing storage. Returning raw byte arrays can expose capacity beyond valid data; callers must honor `getLength()` or copy via `copyBytes()`.
- `MapWritable` and `SortedMapWritable` persist both keys and values as writable entries and must track runtime classes so heterogeneous maps can deserialize correctly.
- `EnumSetWritable` persists enum set contents plus element type, including the special need to retain element type when a value can be null or empty.
- `DefaultStringifier` persists serialized objects into `Configuration` values, making configuration keys an integration point for object state.
- `SequenceFile`, `MapFile`, `SetFile`, and `BloomMapFile` persist data to Hadoop `FileSystem` paths. MapFile has separate index and data files; BloomMapFile adds a Bloom filter file.
- Compression stream classes maintain mutable stream state: buffers, closed/eof flags, byte counters, dictionary state, remaining compressed input, and direct buffer positions.
- `CodecPool` maintains global shared state for leased and cached compressors/decompressors; misuse can have process-wide impact.

## Dependencies

The API surface depends on:

- Java core I/O: `java.io.DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `IOException`, `EOFException`, `File`, and closeable/stream contracts.
- Java NIO: `ByteBuffer`, `WritableByteChannel`, and `FileChannel`.
- Java collections and language types: `Map`, `SortedMap`, `Set`, `Collection`, `Iterator`, `EnumSet`, `Comparator`, `Class`, arrays, and primitives.
- Java security and text support through `MessageDigest`, character encoding, and UTF-8 validation/encoding behavior.
- Hadoop configuration and filesystem APIs: `org.apache.hadoop.conf.Configuration`, `Configurable`, `org.apache.hadoop.fs.FileSystem`, `Path`, and `Progressable`.
- Hadoop serialization infrastructure for `DefaultStringifier`, `ObjectWritable`, and writable cloning.
- Hadoop compression implementations and native/direct codecs behind `DefaultCodec`, `GzipCodec`, `BZip2Codec`, `Compressor`, `Decompressor`, and `DirectDecompressor`.
- Logging through `org.slf4j.Logger` in utility/factory classes.

## Integration Points

- MapReduce key/value types rely heavily on `WritableComparable`, `RawComparator`, and primitive writable wrappers for shuffle sorting and grouping.
- Hadoop RPC and IPC paths use `ObjectWritable`, `Writable`, and related factories for polymorphic request/response payloads.
- SequenceFile and MapFile users integrate with `FileSystem`, compression codecs, progress callbacks, and raw comparators.
- HDFS and filesystem clients use `IOUtils` for safe stream copying, reading, skipping, close suppression, and `fsync` operations.
- Configuration-driven features use `DefaultStringifier` and `WritableUtils` to store serialized objects or string arrays in `Configuration`.
- Compression-aware readers and writers use `CompressionCodecFactory` to infer codecs from path suffixes and configuration, then obtain stream wrappers or pooled codec instances.
- Split-aware input formats depend on `BZip2Codec` and `SplitCompressionInputStream` style APIs for compressed file splitting.
- Direct decompression integrates with consumers that operate on `ByteBuffer` rather than heap byte arrays.

## Deprecation and Compatibility Signals

- `org.apache.hadoop.io.Closeable` is deprecated in favor of `java.io.Closeable`.
- `BytesWritable.get()` and `BytesWritable.getSize()` are deprecated in favor of `getBytes()` and `getLength()`.
- Several legacy `SequenceFile.createWriter(...)` overloads are deprecated in favor of `createWriter(Configuration, Writer.Option...)`.
- `WritableUtils.cloneInto(...)` is deprecated in favor of `ReflectionUtils.cloneInto`.
- These deprecations indicate migration pressure but also compatibility obligations because the APIs remain present in the 3.1.2 surface.

## Risks and Edge Cases

- Raw byte access in `BytesWritable` and `Text` can expose unused backing capacity. Callers that ignore logical length can compare, hash, or persist garbage bytes.
- Writable deserialization mutates existing instances. Reusing an instance without clearing all fields can leak previous state if an implementation is incomplete.
- `ObjectWritable` and `GenericWritable` depend on class names and classloaders. Missing classes, incompatible declared classes, or unsafe polymorphic inputs can fail at runtime.
- Writable binary compatibility is fragile. Any change to field order, vint encoding, or comparator behavior can break stored files or distributed sort compatibility.
- Compression pooling requires disciplined return of leased objects; leaked compressors/decompressors can increase native memory pressure and distort diagnostics.
- `Compressor.end()` and `Decompressor.end()` discard pending input/state. Calling them too early can corrupt stream processing, while failing to call/return resources can leak resources.
- `Decompressor.finished()` with positive `getRemaining()` represents concatenated stream data. Readers that treat `finished()` alone as EOF can drop remaining data.
- Deprecated SequenceFile writer overloads may hide configuration defaults differently from the newer option API, so compatibility tests should cover legacy creation paths.
- `MapFile.fix(...)` is a repair utility, but rebuilding indexes from corrupt data can still preserve corrupted ordering or values if the data file itself is invalid.
- `Text` UTF-8 helpers include validation and maximum-length overloads because unbounded or invalid text inputs are a denial-of-service and correctness risk.
- This XML records signatures, not implementation. Any implementation-specific behavior, synchronization, performance characteristic, or native codec fallback must be confirmed in Java source and tests.

## Test Signals

Useful tests implied by this chunk include:

- Round-trip serialization tests for each primitive writable, `BytesWritable`, `Text`, `MD5Hash`, arrays, maps, `EnumSetWritable`, `GenericWritable`, and `ObjectWritable`.
- Comparator parity tests where object comparison equals raw serialized-byte comparison for supported writable keys.
- Boundary tests for vint/vlong encodings, including negative values, first-byte size decoding, range checks, and skip behavior.
- `BytesWritable` and `Text` tests for capacity versus logical length, copying versus raw array exposure, append/set/clear behavior, UTF-8 validation, and maximum string length enforcement.
- SequenceFile tests for old and new writer creation APIs, compression type defaults, sync interval behavior, metadata, and raw writer variants.
- MapFile/BloomMapFile tests for rename/delete/fix behavior, index/data/bloom file presence, sparse lookup, and corrupt index recovery.
- IOUtils tests for copy close semantics, exact byte reads, full skipping, cleanup exception suppression, socket close handling, channel short writes, fsync on files/directories, and exception wrapping.
- Compression tests for codec discovery by config/service loader, suffix lookup, removing suffixes, pool lease/return counts, stream close/finish/reset behavior, dictionary handling, concatenated stream processing, and direct `ByteBuffer` decompression.
- Split bzip2 tests for `createInputStream(..., start, end, READ_MODE)` and split-boundary behavior, with follow-up coverage from the next chunk for the remainder of `SplitCompressionInputStream`.

## Chunk Boundary Notes

- `ArrayWritable` is already in progress at line 17951; its earlier declaration and constructors are in the previous chunk, while this chunk includes additional constructors and all listed methods.
- `SplitCompressionInputStream` is only partially visible by line 24252; this chunk captures its constructor and protected start/end mutators, but not the full class end or any later split-compression interfaces.
- The next merge lane should combine this report with adjacent chunks before producing a final per-file research document for the full JDiff XML file.

### subset-b-007190: lines 24253-30507

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml lines 24253-30507

## Scope

This chunk is part 5 of 6 for the Apache Hadoop Common 3.1.2 JDiff API snapshot. It starts inside the tail of `org.apache.hadoop.io.compress.SplitCompressionInputStream`, covers the full public API records for erasure-code schema, TFile helpers, serializers, metrics, network-topology mapping, core security identity/credential utilities, and ends at the start of `org.apache.hadoop.security.authorize.ImpersonationProvider`.

The source is generated JDiff XML rather than implementation code. Its research value is the compatibility surface: public/protected type names, inheritance, implemented interfaces, method signatures, checked exceptions, static/final/abstract/synchronized flags, deprecation markers, public fields, and embedded Javadocs. Runtime control flow below is inferred from those contracts and must be reconciled with Java implementation sources before changing behavior.

## Purpose

The compression tail documents split-aware compressed-input contracts. `SplitCompressionInputStream` exposes adjusted start/end offsets after a codec aligns a requested byte range, and `SplittableCompressionCodec` lets codecs create positioned decompression streams for parallel reads of compressed data.

`org.apache.hadoop.io.erasurecode.ECSchema` records erasure-code schema metadata: codec name, data-unit count, parity-unit count, and extra codec-specific options. The empty `coder.util` and `grouper` package elements indicate package presence but no public types in this line range.

`org.apache.hadoop.io.file.tfile` exposes the public TFile container surface. TFile is a byte-oriented key/value container with block compression, named metadata blocks, sorted or unsorted keys, key/file-offset seeking, compression/comparator constants, binary-search utilities, variable-length integer/string encoding helpers, and meta-block exception types.

The serializer packages expose Hadoop serialization implementations and Avro integration markers. `JavaSerialization`, `WritableSerialization`, `AvroSerialization`, `AvroReflectSerialization`, and `AvroSpecificSerialization` are API entries for plugging Java, Writable, and Avro formats into Hadoop's `Serialization` framework.

The metrics packages are the largest part of the chunk. They define immutable metric/tag metadata, collector/record/builder/source/sink/plugin/system contracts, mutable counters/gauges/stats/rates/quantiles, annotation markers, filters, singleton system accessors, sink implementations, JMX helpers, metrics caches, and address parsing helpers.

The network package documents rack/topology mapping and socket factory contracts. It includes configurable DNS-to-switch mapping abstractions, cached/script/table implementations, a connect-timeout exception, and standard/SOCKS socket factories.

The security packages define access-control exceptions, in-memory and serialized credentials, group/id mapping provider interfaces, Kerberos authentication exception context, security utility helpers, `UserGroupInformation`, credential-provider abstractions, and the opening authorization APIs for ACLs, authorization exceptions, and proxy-user impersonation.

## Important APIs, Types, and Functions

### Compression and Erasure Coding

- `SplitCompressionInputStream.getAdjustedStart()` and `getAdjustedEnd()` return codec-adjusted compressed-range offsets after stream creation.
- `SplittableCompressionCodec` extends `CompressionCodec` and adds `createInputStream(InputStream seekableIn, Decompressor decompressor, long start, long end, READ_MODE readMode) throws IOException`, returning a `SplitCompressionInputStream`.
- `SplittableCompressionCodec.READ_MODE` is referenced as the read-position reporting mode; the enum body is outside this chunk.
- `ECSchema` is final and `Serializable`. Constructors accept either an all-options `Map`, `(String codecName, int numDataUnits, int numParityUnits)`, or those key parameters plus extra options.
- `ECSchema` getters expose `getCodecName()`, `getExtraOptions()`, `getNumDataUnits()`, and `getNumParityUnits()`, with `toString()`, `equals(Object)`, and `hashCode()` for logging and value semantics.
- Public schema keys are `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.

### TFile and Serialization

- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are `IOException` subclasses for named TFile metadata block operations.
- `RawComparable` exposes `buffer()`, `offset()`, and `size()` so external `RawComparator` instances can compare a byte range without copying.
- `TFile` exposes compression constants `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE` and comparator constants `COMPARATOR_MEMCMP`, `COMPARATOR_JCLASS`.
- `TFile.makeComparator(String)` builds a raw comparator from a configured comparator name; `getSupportedCompressionAlgorithms()` returns writer-accepted compression names; `main(String[])` dumps TFile information for paths.
- `TFile` Javadocs define the container contract: type-less byte keys/values, 64KB key limit, block compression, named metadata blocks, sorted/unsorted modes, seek by key or offset, configurable chunk and filesystem buffer sizes, and performance tradeoffs around block size, compression, and buffering.
- `Utils` writes and reads variable-length ints/longs and Text-format strings through `writeVInt`, `writeVLong`, `readVInt`, `readVLong`, `writeString`, and `readString`.
- `Utils.lowerBound`/`upperBound` overloads implement binary-search boundary lookups over `List` values with either natural comparison or a supplied `Comparator`.
- `JavaSerialization` and `WritableSerialization` implement `Serialization`; `WritableSerialization` delegates to `Writable.write`/`readFields`.
- `JavaSerializationComparator` provides a comparator path for Java-serialized objects.
- `AvroReflectSerializable` is a marker interface; `AvroReflectSerialization` is configured by `AVRO_REFLECT_PACKAGES`; `AvroSerialization` implements `Serialization` and carries `AVRO_SCHEMA_KEY`; `AvroSpecificSerialization` handles Avro specific records.

### Metrics Core

- `EventCounter` is a Log4J appender that counts logging events at fatal/error/warn/info levels via `append`, `close`, and `requiresLayout`.
- `AbstractMetric` implements `MetricsInfo` and exposes immutable metric metadata and value through `name`, `description`, `info`, `value`, `type`, `visit`, equality, hash, and string rendering.
- `MetricsCollector` creates `MetricsRecordBuilder` instances by record name or `MetricsInfo`.
- `MetricsRecordBuilder` is the fluent mutable assembly surface for metrics records: `tag`, `add`, `setContext`, `addCounter`, `addGauge`, `parent`, and `endRecord`.
- `MetricsRecord` is the immutable snapshot surface: `timestamp`, `name`, `description`, `context`, `tags`, and `metrics`.
- `MetricsSource.getMetrics(MetricsCollector, boolean all)` emits updated metrics; `MetricsSink.putMetrics(MetricsRecord)` and `flush()` consume them; `MetricsPlugin.init(SubsetConfiguration)` initializes plugins.
- `MetricsSystem` registers/unregisters sources, registers JMX callbacks, publishes metrics immediately, and shuts down. `MetricsSystemMXBean` exposes start/stop of the system and MBeans plus `currentConfig()`.
- `MetricsJsonBuilder` and `MetricStringBuilder` implement `MetricsRecordBuilder`-style output builders for JSON/string dumps.
- `MetricsFilter` accepts/rejects metric names, tags, tag collections, and records. `GlobFilter` and `RegexFilter` compile filters to `com.google.re2j.Pattern`.
- `MetricsInfo` supplies immutable name/description metadata; `MetricsTag` implements `MetricsInfo` and adds a tag value.
- `MetricsVisitor` receives typed gauge and counter callbacks for int, long, float, and double metrics.
- Annotation types `Metric` and `Metrics` mark individual metric members and grouped metric sources.

### Metrics Library and Sinks

- `DefaultMetricsSystem` is the singleton enum facade for daemon metrics systems: `initialize`, `instance`, `shutdown`, `setMiniClusterMode`, and `inMiniClusterMode`.
- `Interns.info` and `Interns.tag` create interned `MetricsInfo` and `MetricsTag` objects to reduce repeated metadata allocation.
- `MetricsRegistry` creates and tracks mutable metrics and tags. It has constructors by record name or `MetricsInfo`, lookup methods `get`/`getTag`, factories for counters, gauges, quantiles, stats, rates, aggregate rates, and rolling averages, plus `add`, `setContext`, `tag`, and `snapshot`.
- `MutableMetric` defines changed-state-aware snapshot behavior through `snapshot(builder, all)`, `snapshot(builder)`, `setChanged`, `clearChanged`, and `changed`.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` expose monotonic incrementing counters with typed `value()` and `snapshot`.
- `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong` expose increment/decrement/set gauges with typed `value()`, `snapshot`, and string rendering.
- `MutableQuantiles` maintains online quantile estimates over a rolling interval, with `add`, `snapshot`, `getInterval`, `stop`, `getEstimator`, `setEstimator`, and exposed `quantiles`/`previousSnapshot` fields.
- `MutableStat` accumulates sample statistics, supports extended statistics toggling, adding counts/sums or samples, `lastStat`, `resetMinMax`, and snapshotting.
- `MutableRate`, `MutableRates`, `MutableRatesWithAggregation`, and `MutableRollingAverages` provide throughput/rate and rolling-average helpers, including protocol-method initialization, per-name sample addition, thread-local state collection, closing, and stats retrieval.
- `FileSink`, `GraphiteSink`, `StatsDSink`, and `RollingFileSystemSink` implement configured metrics output. Rolling HDFS/file-system sink state includes source, ignore/append flags, base path, roll and offset intervals, next flush time, force/has-flushed flags, supplied configuration, and supplied filesystem.
- `MBeans` registers/unregisters standard Hadoop MBeans and can extract service/name components from an MBean name.
- `MetricsCache` updates and retrieves cached sparse metrics records for sinks that need complete records.
- `Servers.parse(String, int)` parses comma/space-separated host specifications into `InetSocketAddress` values.

### Network

- `AbstractDNSToSwitchMapping` implements `Configurable` support for topology mappers and provides `isSingleSwitch`, `getSwitchMap`, `dumpTopology`, `isSingleSwitchByScriptPolicy`, and static `isMappingSingleSwitch`.
- `DNSToSwitchMapping` defines `resolve(List<String>)`, `reloadCachedMappings()`, and `reloadCachedMappings(List<String>)` for pluggable host-to-rack mapping.
- `CachedDNSToSwitchMapping` wraps a raw mapping, caches host-to-switch results, exposes `rawMapping`, and supports targeted/full cache reload.
- `ScriptBasedMapping` uses configured scripts for host topology resolution and exposes `NO_SCRIPT`; constructors accept default config, raw mapping, or `Configuration`.
- `TableMapping` provides table-backed mapping configuration and cache reload.
- `SocksSocketFactory` and `StandardSocketFactory` provide multiple `createSocket` overloads plus equality/hash behavior; the SOCKS variant also implements `Configurable`.
- `ConnectTimeoutException` is thrown by NetUtils connection paths on connect timeout.

### Security and Credentials

- `AccessControlException` is the base access-control exception with default, message, and cause constructors.
- `Credentials` stores tokens and secret keys in memory and serializes token-storage files/streams. Important methods include token lookup/add/list/count, secret-key lookup/add/remove/list/count, static `readTokenStorageFile` overloads, `readTokenStorageStream`, `writeTokenStorageToStream` overloads, `writeTokenStorageFile` overloads, `write`, `readFields`, `addAll`, and `mergeAll`.
- `GroupMappingServiceProvider` maps users to groups and supports cache refresh/addition. It exposes `GROUP_MAPPING_CONFIG_PREFIX`.
- `IdMappingServiceProvider` maps UID/GID to names and back, including allowing-unknown variants for UID/GID lookup.
- `KerberosAuthException` records context for unrecoverable UGI failures: user, principal, keytab file, ticket cache file, initial message, and contextual `getMessage`.
- `SecurityUtil` configures security behavior and provides helpers for Kerberos principals, logins, delegation-token service names, Kerberos/TokenInfo annotation lookup, token service encode/decode, privileged-port checks, ZK auth extraction, and `doAsLoginUser`/`doAsCurrentUser` execution helpers.
- `UserGroupInformation` is the central identity object. Static APIs configure UGI, determine security status, get current/login users, select the best UGI from ticket cache/user, create UGIs from ticket caches or subjects, login/logout/relogin from keytab or ticket cache, create remote/proxy/testing users, and reattach metrics.
- UGI instance APIs expose real/effective user relationships, short/full user names, primary/group names, token identifiers, tokens, credentials, authentication methods, the underlying JAAS `Subject`, equality/hash, string rendering, debug logging, and `doAs` execution for `PrivilegedAction`/`PrivilegedExceptionAction`.
- `UserGroupInformation.AuthenticationMethod` enumerates authentication methods and maps to/from `SaslRpcServer.AuthMethod`.
- `CredentialProvider` is a thread-safe credential-store abstraction. It exposes transient-store detection, `flush`, credential lookup/list/create/delete, password-needed checks, no-password warning/error text, and `CLEAR_TEXT_FALLBACK`.
- `CredentialProviderFactory` creates providers from configured URI paths via service loading. `CREDENTIAL_PROVIDER_PATH` is the configuration key; `getProviders(Configuration)` returns the provider list.

### Authorization

- `AccessControlList` implements `Writable`, can be built from a combined ACL string or separate user/group strings, and supports wildcard ACLs through `WILDCARD_ACL_VALUE`.
- ACL methods include `isAllAllowed`, user/group add/remove, immutable user/group collection accessors, `isUserInList`, `isUserAllowed`, descriptive `toString`, exact `getAclString`, and `write`/`readFields`.
- `AuthorizationException` extends `AccessControlException` and deliberately suppresses stack trace access/printing for security-sensitive authorization failures.
- `DefaultImpersonationProvider` implements `ImpersonationProvider`, has a synchronized test-provider getter, accepts configuration, initializes with a proxy-user configuration prefix, authorizes a real user and remote address, generates proxy-user config keys, and exposes proxy group/host maps.
- This chunk stops at the opening of `ImpersonationProvider`; its method details continue in the next chunk.

## Control Flow

The XML has no executable flow, but the APIs imply these runtime paths:

- Split-compression readers call the codec-specific `createInputStream` with a seekable compressed stream and requested range. The codec may adjust start/end to compression block boundaries; callers then read the adjusted range from `SplitCompressionInputStream`.
- TFile writes group key/value data into compressed blocks and optional named metadata blocks, while readers load indexes and seek by key or file offset. Utility encoding methods serialize primitive/string metadata to `DataOutput` and recover it from `DataInput`.
- Serializer selection is framework-driven: Hadoop asks configured `Serialization` implementations whether they accept a class, then uses the serializer/deserializer provided by Java, Writable, Avro reflect, or Avro specific implementations.
- Metrics sources register with a `MetricsSystem`; sources fill `MetricsRecordBuilder` instances when polled, mutable metrics snapshot changed values into builders, filters can accept/reject names/tags/records, and sinks publish records to files, Graphite, StatsD, rolling filesystem paths, JSON, strings, JMX, or caches.
- Mutable metrics generally mutate local counters/gauges/stats on application events, mark themselves changed, and clear that changed flag during snapshot unless a full snapshot is requested.
- Rolling metrics and quantiles accept stream samples over time, maintain in-memory estimators/windows, and publish snapshots periodically or when requested.
- Network topology resolution flows from host lists to configured `DNSToSwitchMapping` implementations. Cached wrappers first return stored mappings, miss through to raw/script/table providers, and can be invalidated globally or for selected hosts.
- Security setup flows through `UserGroupInformation.setConfiguration` and `SecurityUtil.setConfiguration`, then identities are created from the current subject, Kerberos keytabs, ticket caches, remote usernames, or proxy relationships. `doAs` runs work under the selected subject.
- Token and secret-key flows use `Credentials` as the in-memory carrier and `writeTokenStorage*`/`readTokenStorage*` for persistence through streams or files.
- Credential providers are discovered from URI paths in configuration, created through factory service loading, mutated via create/delete, and committed to backing stores only when `flush()` succeeds.
- Authorization flows parse ACL strings into user/group sets or wildcard state, then test `UserGroupInformation` users/groups. Proxy authorization uses `DefaultImpersonationProvider` configuration maps of allowed effective users/groups and remote hosts.

## State and Persistence Behavior

This JDiff file persists API metadata for release compatibility checks. It does not store Hadoop runtime data.

`ECSchema` is value-like schema metadata. Its durable relevance is in configuration and serialized consumers that rely on the public option-key strings and equality/hash behavior.

TFile state is durable file content: data blocks, compressed block indexes, metadata block indexes, comparator/compression names, value chunking, and encoded primitive/string metadata. Public constants and variable-length encodings are compatibility-sensitive because existing TFiles and clients depend on them.

Metrics state is mostly in-memory and process-local. Immutable records/tags/metrics are snapshots; mutable counters/gauges/stats/rates/quantiles hold live process measurements; registries own metric instances and tags; `DefaultMetricsSystem` owns singleton lifecycle state; caches retain recent records for sparse sinks. Sinks persist or transmit metrics to files, filesystems, Graphite, StatsD, JMX, or logs depending on configuration.

Network mapping state is configuration plus optional caches. `CachedDNSToSwitchMapping` stores host-to-rack results in memory; script/table providers depend on external script or table configuration; reload calls invalidate or refresh cached mappings.

Security state includes in-memory JAAS subjects, authentication methods, token identifiers, delegation tokens, credentials, Kerberos login context, ticket/keytab paths, and group/id mapping caches. `Credentials` has explicit Writable/token-storage persistence through `DataInput`, `DataOutput`, streams, and files.

Credential-provider state may be transient or backed by persistent stores. `isTransient()` distinguishes non-durable stores; `flush()` is the durability boundary for persisted credential mutations. Password-needed methods report whether provider access is blocked by missing password material.

Authorization ACLs are serializable through `Writable` and preserve user/group/wildcard state. `AuthorizationException` suppresses stack traces as part of its externally visible security behavior.

## Dependencies and Integration Points

- Java dependencies include `InputStream`, `IOException`, `DataInput`, `DataOutput`, `DataInputStream`, `File`, `PrintStream`, `Comparator`, collections, `InetSocketAddress`, `Socket`, `Proxy`, `SocketFactory`, JAAS `Subject`, privileged actions, JMX `ObjectName`, and primitive arrays.
- Hadoop dependencies include `CompressionCodec`, `Decompressor`, `Configuration`, `Configurable`, `Writable`, `RawComparator`, `Text`, `Path`, `FileSystem`, token classes, Kerberos/Token annotation classes, SASL RPC auth methods, `UserGroupInformation`, and `SubsetConfiguration`.
- Metrics integrates with Log4J (`EventCounter`), SLF4J logger fields, Apache Commons Configuration for plugin init, RE2/J pattern compilation for filters, JMX MBean registration, and external metrics systems such as Graphite and StatsD.
- TFile integrates with Hadoop filesystem streams, Hadoop compression codecs, Text-compatible string encoding, raw comparators, and `Writable`-style serialization.
- Network mapping integrates with Hadoop configuration keys, external rack-resolution scripts or table files, and Java socket creation used by RPC/client layers.
- Security APIs integrate with Kerberos principals/keytabs/ticket caches, delegation-token service naming, ZooKeeper auth configuration, service-loaded credential providers, group mapping providers, id mapping providers, RPC impersonation, and Hadoop authorization checks.

## Risks and Edge Cases

- The chunk begins mid-class and ends mid-interface. Full reports must merge previous chunk data for `SplitCompressionInputStream` and next chunk data for `ImpersonationProvider`.
- JDiff omits implementation bodies. Thread safety, synchronization details, cache eviction, serialization wire layout, and error-message behavior require implementation-source validation.
- Split-compression correctness depends on codecs consistently adjusting start/end and reporting positions according to `READ_MODE`. Misaligned offsets can lose records or duplicate records in split processing.
- TFile public docs mention LZO support, comparator class loading, sorted/unsorted behavior, filesystem buffering, and block-size tuning; all can have performance or compatibility impact. Existing files depend on varint/string encodings and comparator/compression names.
- `RawComparable` exposes a mutable backing byte array plus offset/size. Callers must honor range boundaries and avoid mutating bytes while comparisons are in progress.
- Strong interning is not in this chunk, but metrics `Interns` performs object interning; high-cardinality metric names/tags can still cause memory retention.
- Mutable metrics can be lost or duplicated in snapshots if changed flags, full snapshots, and concurrent updates are mishandled. Rolling/quantile metrics have lifecycle risk if `stop()`/`close()` is not called.
- `DefaultMetricsSystem` singleton and mini-cluster mode are global process state. Tests must isolate initialization and shutdown to avoid cross-test contamination.
- File, rolling filesystem, Graphite, and StatsD sinks depend on external IO endpoints. `ignoreError`, append support, flush scheduling, and roll intervals are behaviorally important under failures.
- DNS-to-switch mapping can return nulls, stale caches, incomplete host lists, or single-switch defaults. Incorrect topology mapping degrades block placement and scheduler locality.
- Script-based topology mapping depends on external scripts and configuration; reload behavior must handle script changes and missing scripts cleanly.
- Socket factories must preserve equality/hash behavior because they may be used as configurable connection-factory keys.
- Security and credential APIs are high risk: token storage files contain sensitive material; credentials are mutable in memory; provider flush is the only persistence guarantee; missing passwords may force clear-text fallback depending on configuration.
- `Credentials.addAll` and `mergeAll` have different overwrite/merge semantics in implementation; callers need tests around alias collisions.
- Kerberos principal expansion with host substitution, ticket-cache/keytab relogin, and `doAs` execution are sensitive to configuration, DNS, clock skew, and exception propagation.
- `AuthorizationException` suppresses stack traces by contract; debugging tools should not assume stack details are available.
- ACL string parsing must handle wildcard, empty users/groups, whitespace, duplicate entries, and group resolution correctly. Proxy-user authorization must validate both user/group and remote host dimensions.

## Test Signals

- API compatibility checks should assert public classes, interfaces, fields, constructors, method signatures, checked exceptions, deprecation status, and partial-boundary merge correctness for this chunk.
- Split-compression tests should cover adjusted start/end reporting, read-mode behavior, block-boundary alignment, and split processing with compressed inputs.
- `ECSchema` tests should cover constructor variants, required option keys, extra options preservation, invalid/missing options if enforced by implementation, equality/hash consistency, serialization compatibility where used, and stable `toString`.
- TFile tests should cover compression constant acceptance, comparator creation, sorted and unsorted reads, named meta-block duplicate/missing errors, seek by key/offset, varint/string round trips, lower/upper-bound behavior, and compatibility with existing TFile fixtures.
- Serializer tests should cover Java, Writable, Avro reflect, and Avro specific class acceptance, schema-key configuration, round-trip serialization, and comparator behavior.
- Metrics tests should cover collector/builder fluent behavior, immutable record/tag/metric equality and rendering, visitor dispatch for all numeric types, filter accept/reject behavior, source registration, immediate publish, shutdown lifecycle, JMX callbacks, and MXBean config output.
- Mutable metrics tests should cover counter monotonicity, gauge set/incr/decr including negative values if allowed, changed-flag semantics, full versus changed-only snapshots, stat min/max/stddev behavior, rate aggregation, rolling-average state collection, quantile intervals, estimator replacement, and close/stop cleanup.
- Sink tests should cover file output, rolling interval/offset calculation, append/no-append behavior, flush scheduling, error handling, Graphite formatting, StatsD metric writing, cache updates, and server address parsing.
- Network tests should cover cache hits/misses/reloads, script/table configuration, single-switch detection, null or partial mapping responses, topology dump text, socket factory creation overloads, proxy configuration, and connection timeout exception handling.
- Security tests should cover credential token/secret-key add/get/remove/list/count, token-storage file and stream round trips, alias collision behavior for `addAll` and `mergeAll`, group/id mapping cache operations, Kerberos exception contextual messages, principal host substitution, token service encode/decode, ZK auth extraction, privileged-port checks, and doAs exception propagation.
- UGI tests should cover configuration initialization, current/login/best user selection, subject and ticket-cache creation, keytab login/logout/relogin, ticket-cache relogin, remote/proxy/testing user creation, real/effective user relationships, group lookup, authentication method mapping, token and credential attachment, equality/hash, and debug logging.
- Credential-provider tests should cover provider path parsing, service-loader factory selection, transient versus persistent providers, create/get/delete/list aliases, password-needed warning/error paths, clear-text fallback configuration, and flush durability.
- Authorization tests should cover ACL parsing from combined and split strings, wildcard behavior, user/group add/remove, immutable returned collections, Writable serialization, user membership checks against UGI groups, suppressed stack traces, proxy-user config-key generation, and authorize success/failure for user/group/host combinations.

## Cross-Chunk Notes

The previous chunk is needed for the complete `SplitCompressionInputStream` class declaration and constructor/mutator context. The next chunk is needed for the complete `ImpersonationProvider` interface and the remaining authorization/security APIs in this JDiff file. This chunk should be merged into the final per-file research document for `Apache_Hadoop_Common_3.1.2.xml` only after all six chunk documents are available.

### subset-b-007191: lines 30508-35695

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml

Chunk: `subset-b-007191`
Lines researched: 30508-35695 of generated JDiff XML for `Apache Hadoop Common 3.1.2`.

## Purpose

This chunk is a line-bounded slice of Hadoop Common 3.1.2's generated JDiff API description. It is not implementation source; it is a public API snapshot used by Hadoop release tooling to compare package/type/member compatibility across versions. The XML records public and protected API shape: packages, classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, visibility, abstract/static/final/synchronized flags, deprecation metadata, checked exceptions, parameter types, and Javadoc text.

The chunk starts inside the tail of `org.apache.hadoop.security.authorize.ImpersonationProvider`, then covers security HTTP filters, security token APIs, web delegation token clients/authenticators, the service lifecycle model, service launcher contracts and exit codes, tracing administration protocol types, general utilities, shell execution helpers, shutdown-hook management, build-version metadata, and Bloom filter data structures. It ends with empty package markers for `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash`, followed by the XML document close.

## XML Structure And Coverage

The slice contains complete `<package>` sections for:

- `org.apache.hadoop.security.http`
- `org.apache.hadoop.security.protocolPB` and `org.apache.hadoop.security.ssl` as empty API package markers
- `org.apache.hadoop.security.token`
- `org.apache.hadoop.security.token.delegation.web`
- `org.apache.hadoop.service`
- `org.apache.hadoop.service.launcher`
- `org.apache.hadoop.tools` and `org.apache.hadoop.tools.protocolPB` as empty API package markers
- `org.apache.hadoop.tracing`
- `org.apache.hadoop.util`
- `org.apache.hadoop.util.bloom`
- `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash` as empty API package markers

The first lines complete `ImpersonationProvider`, whose API was opened earlier in the XML. The visible tail confirms it implements `Configurable` and exposes `init(String configurationPrefix)` plus `authorize(UserGroupInformation user, String remoteAddress)`, with `AuthorizationException` on rejected proxy-user impersonation. Whole-file reconciliation should merge this with the previous chunk before summarizing the full type.

## APIs And Types Covered

`org.apache.hadoop.security.http.RestCsrfPreventionFilter` is a servlet `Filter` for REST CSRF protection. It exposes `init`, `doFilter`, `destroy`, protected `isBrowser(String)`, public `handleHttpInteraction(RestCsrfPreventionFilter.HttpInteraction)`, and static `getFilterParams(Configuration, String)`. Public constants identify the user-agent header, browser user-agent regex parameter, custom header parameter, methods-to-ignore parameter, and default header name. Its contract is browser-sensitive: browser-like user agents must supply the configured CSRF header, while non-browser user agents are not forced through that check.

`org.apache.hadoop.security.http.XFrameOptionsFilter` is a servlet `Filter` for clickjacking protection. It initializes from filter config, adds X-Frame-Options behavior during `doFilter`, and exposes `getFilterParams(Configuration, String)` plus constants for the X-Frame-Options header and custom header parameter.

`org.apache.hadoop.security.token.SecretManager<T>` is the server-side abstraction for token secrets. Implementations create token passwords, retrieve passwords while validating expiration/revocation, and create empty identifiers. It also exposes `retriableRetrievePassword` for failover/retry-aware callers, `checkAvailableForRead()` for standby-state gating, `generateSecret()`, static HMAC password creation from identifier bytes and a `SecretKey`, and `createSecretKey(byte[])`.

`org.apache.hadoop.security.token.Token<T>` is the client-side token value and implements `Writable`. It can be constructed from an identifier plus `SecretManager`, raw identifier/password/kind/service components, another token, a protobuf `SecurityProtos.TokenProto`, or an empty default constructor. Its public API covers cloning, protobuf conversion, identifier/password/kind/service access, service mutation, private clone checks and creation, Writable serialization, URL-safe encode/decode, equality/hash/string/cache-key behavior, and delegation-token management through `isManaged`, `renew(Configuration)`, and `cancel(Configuration)`.

`Token.TrivialRenewer` is a static public `TokenRenewer` subclass for token kinds that are not managed. Subclasses provide `getKind`; it implements kind matching, unmanaged status, no-op/unsupported renewal semantics, and cancellation behavior.

`TokenIdentifier` is the abstract, writable identifier side of a token. Implementations provide `getKind()` and `getUser()`. The base API serializes itself through `getBytes()` and exposes `getTrackingId()`, documented as an MD5-derived cross-session tracking identifier.

`TokenInfo` is a public annotation type marker for token-related metadata. `TokenRenewer` is the plugin interface for token kind support, managed-token checks, renewal, and cancellation. `TokenSelector<T>` selects a token for a named `Text` service from a collection.

`DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` with Hadoop delegation-token support. It has constructors for default, explicit authenticator, connection configurator, and both together. Public behavior includes global default authenticator selection, optional query-string token transport for WebHDFS compatibility, authenticated connection opening, delegation-token acquisition, renewal, and cancellation, with overloads supporting `doAs` proxy-user parameters. Its nested `Token` extends `AuthenticatedURL.Token` and stores an optional Hadoop delegation `Token`.

`DelegationTokenAuthenticator` wraps an underlying `Authenticator` and implements `Authenticator` itself. It accepts a `ConnectionConfigurator`, performs authentication, and drives remote delegation-token operations through URL endpoints. Public constants define operation/query/header names and JSON field names such as delegation token header, delegation parameter, token parameter, renewer parameter, service parameter, token JSON, URL-string JSON, and renew-expiration JSON. `KerberosDelegationTokenAuthenticator` and `PseudoDelegationTokenAuthenticator` are concrete simple constructors for SPNEGO-backed and pseudo-auth-backed delegation flows.

`org.apache.hadoop.service.Service` is the public lifecycle contract. It extends `Closeable` and defines `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration, name/config/state/start-time queries, state checks, failure cause/state access, `waitForServiceToStop(long)`, lifecycle history snapshots, and blocker snapshots. The documented state model is `NOTINITED -> INITED -> STARTED -> STOPPED`, with failures expected to trigger stop and move to `STOPPED`.

`AbstractService` is the base implementation for `Service`. It exposes lifecycle entry points, protected overridable `serviceInit`, `serviceStart`, and `serviceStop`, failure recording via `noteFailure`, per-service and global state listener registration, lifecycle history, start time, configuration, state, blocker management, and service-stop waiting.

`CompositeService` manages child `Service` instances. It can add/remove children, add objects only if they implement `Service`, return a cloned service list, and cascades init/start/stop across children. The protected `STOP_ONLY_STARTED_SERVICES` field documents shutdown policy around stopping all children versus only started children, while still stopping children that failed during init/start.

`LifecycleEvent` is a serializable value object with public `time` and `state` fields. `LoggingStateChangeListener` logs service state changes. `ServiceOperations` provides static stop helpers, including quiet variants that catch and return exceptions while logging warnings. `ServiceStateChangeListener` receives callbacks after state changes and its docs warn that callbacks execute inside synchronized service transition paths, so slow listeners or reentrant service calls can deadlock.

`ServiceStateException` is a runtime exception that implements `ExitCodeProvider`; it records or derives a service lifecycle exit code and offers static `convert` helpers that wrap arbitrary throwables. `ServiceStateModel` is a small state-machine helper with current-state checks, synchronized `enterState`, static transition validation, and string rendering.

`org.apache.hadoop.service.launcher.LaunchableService` extends `Service` for process-launch-managed services. `bindArgs(Configuration, List)` is invoked before service init and can return a replacement configuration; `execute()` runs after service start and returns the process exit code. `AbstractLaunchableService` supplies defaults that return the input configuration and success exit code.

`HadoopUncaughtExceptionHandler` implements the JVM uncaught-exception hook policy for Hadoop launcher entry points. It logs ordinary exceptions outside shutdown but exits on `Error` because process state may be unsafe. `LauncherExitCodes` is a constants interface defining success, generic failure, client shutdown, task launch failure, interruption, command argument/config/auth/HTTP-like error categories, exception, unimplemented, service unavailable, unsupported version, service creation failure, and service lifecycle exception codes. `ServiceLaunchException` extends `ExitUtil.ExitException` and carries launcher exit codes, including formatted English-locale message construction.

`org.apache.hadoop.tracing.SpanReceiverInfo` exposes span receiver id and class name. `SpanReceiverInfoBuilder` builds receiver descriptions from a class name plus configuration pairs. `TraceAdminProtocol` lists, adds, and removes span receivers over an IOException-throwing protocol with a public `versionID`; `TraceAdminProtocolPB` bridges to the protobuf blocking interface and `VersionedProtocol`.

`org.apache.hadoop.util.ApplicationClassLoader` is a `URLClassLoader` for application isolation. It supports URL-array and classpath-string constructors, resource lookup, public/protected class loading, and static `isSystemClass(String, List)` pattern matching. `SYSTEM_CLASSES_DEFAULT` marks JDK, Hadoop, resource, and selected third-party classes that should stay parent/system loaded.

`IPList` is a one-method inclusion test for IP addresses. `Progressable` is a callback interface for long-running operations to report progress to Hadoop framework code and avoid timeout assumptions.

`PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum`. Both expose construction, `getValue`, `reset`, byte-array update, and single-byte update. `PureJavaCrc32` targets the same polynomial as native CRC32 to avoid JNI overhead for many small checksum operations; `PureJavaCrc32C` targets CRC32-C/iSCSI/SSE4.2-compatible polynomial behavior.

`ReflectionUtils` provides static helpers for configuration injection, reflective new instance creation, contention tracing, thread dump printing/logging through commons-logging or SLF4J, runtime class lookup for a typed object, Writable copy/clone through serialization, and declared field/method collection across inheritance.

`Shell` is an abstract base class for shell command execution and OS-specific command construction. It exposes static OS/JDK checks, Windows command-line length validation, groups/user/netgroup/permission/owner/symlink/readlink/process-signal command builders, environment variable regex, script extension helpers, Hadoop home/bin/winutils discovery, bash support checks, environment and working-directory setters, protected `run()`, abstract `getExecString()` and `parseExecResult(BufferedReader)`, process/exit/waiting-thread/timeout accessors, static `execCommand` overloads, global process destruction/listing, and memory-lock-limit parsing. Public fields capture Hadoop home env/system property names, Windows command-length constants including a deprecated misspelled alias, OS booleans, command constants, timeout/inherit-env state, deprecated `WINUTILS`, setsid availability, and token separator regex.

`ShutdownHookManager` is a singleton deterministic shutdown-hook registry. It registers hooks by priority, supports optional per-hook timeout and time unit, removal, presence checks, shutdown-in-progress checks, and clearing. Public constants define minimum timeout and default time unit. The class centralizes hooks behind one JVM shutdown hook so higher-priority hooks run earlier.

`StringInterner` exposes strong and weak string interning and in-place array interning. `SysInfo` is the abstract system-resource plugin surface for memory, processor/core counts, CPU frequency/time/usage, virtual cores used, network IO, and storage IO, with `newInstance()` selecting a default OS implementation.

`Tool` extends `Configurable` and defines `run(String[])` as Hadoop's generic CLI tool contract. `ToolRunner` parses generic Hadoop command-line options, injects the resulting `Configuration` into a `Tool`, invokes it, prints generic usage, and provides an interactive confirmation prompt. `VersionInfo` exposes protected instance getters and public static getters for Hadoop version, git revision, branch, build date, build user, source URL, source checksum, build version, protoc version, plus `main`.

`org.apache.hadoop.util.bloom.BloomFilter` is a standard Bloom filter extending `Filter`, with constructors for serialization and vector/hash setup, `add`, logical `and`/`or`/`xor`/`not`, membership tests, string rendering, vector-size access, and Writable serialization.

`CountingBloomFilter` is a final counting Bloom filter supporting add, delete, membership, approximate count, logical operations, string rendering, and Writable serialization. Its docs highlight 4-bit bucket-style overflow risk: adding the same key more than 15 times can overflow positions and raise error rates; delete can underflow and introduce false negatives.

`DynamicBloomFilter` supports a matrix of Bloom-filter rows that grows when the active row reaches its key threshold. It exposes add, membership, logical operations, string rendering, and Writable serialization. `HashFunction` maps a `Key` to multiple hash positions using configured max value, hash count, and hash type. `RemoveScheme` defines retouched Bloom filter clearing strategies: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`. `RetouchedBloomFilter` extends `BloomFilter`, records known false positives through single key, collection, list, or array overloads, and applies `selectiveClearing(Key, short)` to trade selected false positive removal against possible false negatives.

## Control Flow And Behavioral Contracts

The XML itself has no executable control flow; behavior is inferred from method contracts, signatures, exceptions, and Javadoc.

Security HTTP request flow is filter-based. `RestCsrfPreventionFilter` initializes from servlet/configuration parameters, classifies the `User-Agent` through regexes, and rejects browser-originated REST requests that lack the configured custom header unless the method is ignored. `XFrameOptionsFilter` initializes header configuration and applies the clickjacking header before passing the request down the filter chain.

Token flow separates server and client responsibilities. `SecretManager` creates and validates token passwords and can signal invalid, standby, retriable, or IO states. `Token` carries the serialized identity/password/kind/service payload across RPC or HTTP boundaries, can be encoded for URLs or protobuf, and delegates renew/cancel/isManaged to registered `TokenRenewer` plugins. `TokenSelector` resolves service-specific tokens from collections.

Web delegation-token flow builds on `AuthenticatedURL`. Connections authenticate normally unless the URL token wrapper already carries a delegation token, in which case that token takes precedence. Acquisition and renewal require configured authentication, while cancellation is explicitly documented as not requiring authentication. Optional `doAs` parameters integrate with proxy-user flows, and optional query-string transport exists for WebHDFS compatibility despite header transport being the default.

Service lifecycle flow is explicit and guarded: services are initialized with a `Configuration`, started, stopped, and closed through `stop()`. On init/start failures, the documented contract is to stop and enter `STOPPED`. `AbstractService` records history and failures, notifies local/global listeners during transitions, and exposes blockers. `CompositeService` recursively initializes/starts/stops children. `ServiceStateModel` enforces valid transitions and throws `ServiceStateException` for illegal movement.

Launcher flow calls `LaunchableService.bindArgs()` before init, then starts the service, then calls `execute()`, using the returned value or thrown exception to produce a process exit code. `ServiceLaunchException`, `ExitCodeProvider`, and `LauncherExitCodes` form the process-exit mapping layer.

Utility control flow centers on adapters and helpers. `ApplicationClassLoader` applies child-first loading except for configured system-class patterns. `ReflectionUtils.newInstance()` constructs and config-injects objects. `Shell.run()` gates command execution by interval, constructs command arrays through subclass `getExecString()`, executes the process, and lets subclasses parse output. `ShutdownHookManager` orders registered hooks by priority and enforces configured timeouts.

Bloom filter control flow follows probabilistic set operations. Keys are hashed into positions through `HashFunction`; Bloom filters set/test bit vectors; counting filters increment/decrement counters and derive approximate counts; dynamic filters add rows when a row's record threshold is reached; retouched filters record false positives and selectively clear positions using one of the configured schemes.

## State And Persistence Behavior

The JDiff XML is persistent release metadata. Its primary durable state is the API description in the source tree; it should be preserved byte-for-byte except when the API snapshot is regenerated intentionally.

Runtime state described by the APIs includes servlet filter configuration, CSRF browser regex/header/method-ignore settings, X-Frame-Options header settings, token identifiers/passwords/kinds/services, delegation-token transport choices, authentication tokens, token renewal/cancellation state, and server-side token secret material. Secret material is not itself shown in the XML, but `SecretManager` APIs imply persistent or replicated backing state in concrete implementations.

Service APIs maintain mutable lifecycle state: current state, configuration, start time, failure cause/state, lifecycle event history, listeners, global listeners, blockers, and child service lists. State changes are synchronized in the model/base implementation, but listener callbacks can observe transient multi-threaded states.

Launcher and tracing state includes process exit-code decisions, uncaught exception handling policy, span receiver descriptions, span receiver ids, and configuration key/value pairs for receiver creation.

Utility state includes classloader URL/classpath and system-class patterns, CRC accumulator values, reflection/thread-dump throttling state, shell environment/working directory/current process/exit code/timeout/global shell registry, shutdown-hook registry and shutdown-in-progress flag, intern pools, system metrics snapshots, and version metadata loaded from build properties.

Bloom filters persist their probabilistic structures through `write(DataOutput)` and `readFields(DataInput)`. Standard filters persist bit vectors; counting filters persist counters; dynamic filters persist row matrices and thresholds; retouched filters persist false-positive metadata and adjusted filter state. Default constructors are explicitly present for deserialization.

## Dependencies And Integration Points

This generated XML integrates with JDiff/Javadoc compatibility tooling. Consumers compare it with other Hadoop Common API XML files to detect public API additions, removals, signature changes, deprecations, and documentation shifts.

Runtime APIs described here integrate with:

- Java Servlet API for REST CSRF and X-Frame-Options filters.
- Hadoop `Configuration`, `UserGroupInformation`, security authorization, authentication client classes, `AuthenticatedURL`, `Authenticator`, and `ConnectionConfigurator`.
- Hadoop `Writable`, `Text`, security protobufs, token identifiers, token renewer plugins, and secret-manager implementations.
- HTTP/S delegation-token services, WebHDFS compatibility behavior, Kerberos SPNEGO, pseudo authentication, proxy-user `doAs` flows, and JSON delegation-token responses.
- Hadoop service framework classes, SLF4J and commons-logging, launcher exit-code handling, JVM uncaught exception hooks, and `ExitUtil`.
- Hadoop IPC/protobuf tracing administration through `VersionedProtocol` and `TraceAdminPB`.
- Java class loading, reflection, management/thread diagnostics, process execution, OS-specific shell commands, shutdown hooks, checksums, and system-resource probes.
- Hadoop CLI conventions through `Tool`, `ToolRunner`, `GenericOptionsParser`, and configuration injection.
- Hadoop Bloom filter support classes such as `Filter`, `Key`, and hash implementations under `org.apache.hadoop.util.hash.Hash`.

## Risks And Compatibility Notes

- The chunk begins mid-`ImpersonationProvider`, so any whole-type report must merge with the preceding chunk. This chunk should only claim the visible tail for that interface.
- Empty packages are still compatibility-relevant package markers in the XML, but they do not expose public types in this slice.
- Generated API XML can drift if regenerated with a different doclet classpath, JDK, annotations, or source set. Compatibility checks should treat the source as generated metadata, not hand-authored API truth.
- `RestCsrfPreventionFilter.isBrowser` is protected and overrideable; subclasses can weaken or alter CSRF enforcement. Tests should cover default regex behavior and configured overrides.
- Header/query-string delegation-token transport affects security posture. Query-string tokens are present for compatibility and may leak through logs or caches if used carelessly.
- `AuthenticatedURL` instances are documented as not thread-safe; delegation-token URL wrappers should not be shared across concurrent client operations without external synchronization.
- `Token` exposes byte-array identifier/password accessors and URL encoders; callers must avoid accidental logging or mutation of sensitive token material.
- `TokenIdentifier.getTrackingId()` is documented as MD5-derived; this is a tracking identifier, not a modern cryptographic guarantee.
- `ServiceStateChangeListener` callbacks run during synchronized state transitions. Slow callbacks or callbacks that reenter service methods can block transitions or deadlock.
- `ServiceOperations.stop(Service)` is explicitly not thread-safe because it checks state before stopping; concurrent lifecycle operations need external coordination.
- `Shell` is OS-sensitive and has deprecated compatibility fields/methods, including `isJava7OrAbove`, misspelled `WINDOWS_MAX_SHELL_LENGHT`, and nullable deprecated `WINUTILS`. Command construction and Windows command-line limits need platform coverage.
- `Shell.execCommand` and global process destruction are high-impact APIs; tests and callers should handle timeouts, stderr behavior, environment inheritance, and process cleanup.
- Shutdown hook ordering is deterministic only within `ShutdownHookManager`; JVM-level hook ordering remains centralized through its single registered hook and can be affected by shutdown already being in progress.
- Bloom filter APIs are probabilistic and mutable. Counting filter overflow beyond 15 repeated inserts and delete underflow can increase false positives or introduce false negatives.

## Test Signals

Useful validation signals for this chunk include:

- XML well-formedness from line 30508 through the closing `</api>`, with matching start/end class and interface comments for all complete types in this slice.
- JDiff comparisons against adjacent Hadoop Common releases should flag public API changes in servlet filters, token/delegation-token APIs, service lifecycle APIs, launcher exit codes, shell utilities, and Bloom filters.
- Security filter tests should cover CSRF header enforcement for browser and non-browser user agents, custom browser regexes, custom header names, ignored HTTP methods, filter parameter extraction from `Configuration`, and X-Frame-Options header initialization/application.
- Token tests should cover SecretManager password creation/retrieval, invalid/retriable/standby behavior, Token Writable and protobuf round trips, URL-safe encode/decode, private clones, service mutation, renewer plugin discovery, renew/cancel/isManaged paths, and selector behavior.
- Delegation-token HTTP tests should cover default Kerberos authenticator selection, pseudo fallback where applicable, connection configurator propagation, header versus query-string token transport, `doAs` handling, get/renew/cancel operations, JSON parsing fields, and cancellation without authentication.
- Service lifecycle tests should cover valid and invalid state transitions, failure recording, listener/global-listener notification ordering, listener deadlock avoidance expectations, lifecycle history snapshots, blocker add/remove snapshots, wait-for-stop timeouts, CompositeService child ordering, and quiet stop exception capture.
- Launcher tests should cover `bindArgs` configuration replacement, execute return-code propagation, exception-to-exit-code wrapping, uncaught `Error` versus ordinary exception handling, and stability of every `LauncherExitCodes` constant.
- Tracing tests should cover span receiver builder configuration pairs, list/add/remove protocol behavior, receiver id returns, and protobuf protocol bridge compatibility.
- Utility tests should cover ApplicationClassLoader child-first/system-class matching, CRC32/CRC32C vectors, ReflectionUtils configuration injection and Writable copy, Shell command builders across Linux/Mac/Windows/Solaris/FreeBSD branches, command timeout cleanup, winutils discovery failures, shutdown-hook priority/timeout/removal behavior, string interning null/array cases, SysInfo unsupported OS handling, ToolRunner generic option parsing, and VersionInfo property loading.
- Bloom filter tests should cover add/membership, logical operations, serialization round trips, counting delete/underflow/overflow behavior, approximate counts, dynamic row growth at `nr`, hash position bounds, retouched false-positive recording overloads, and selective clearing schemes.

## Cross-Chunk Continuations

Previous chunk context is required for the beginning of `org.apache.hadoop.security.authorize.ImpersonationProvider`. This chunk reaches the end of the XML document after `org.apache.hadoop.util.hash`, so the merge lane should treat it as the terminal chunk for this JDiff file while still reconciling earlier chunks for packages and types not covered here.
