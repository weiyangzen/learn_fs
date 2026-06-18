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
