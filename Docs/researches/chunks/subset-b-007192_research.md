# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.2.xml lines 1-6124

## Scope

This chunk is the opening slice of the generated JDiff API snapshot for Apache Hadoop Common 3.2.2. It includes the XML/API header, the top-level Hadoop exception package, all visible `org.apache.hadoop.conf` APIs, the public key-provider API under `org.apache.hadoop.crypto.key`, empty package markers for `org.apache.hadoop.crypto`, `org.apache.hadoop.crypto.key.kms`, and `org.apache.hadoop.crypto.random`, and the beginning of `org.apache.hadoop.fs` through the first methods of `ContentSummary`.

The source is generated compatibility metadata rather than implementation code. The research surface is the public/protected API contract: package names, classes/interfaces, inheritance, implemented interfaces, constructors, method signatures, checked exceptions, public/protected fields, deprecation markers, Javadocs, and constants that bind Hadoop code to `core-default.xml` keys.

## Purpose

The file records the public Hadoop Common 3.2.2 Java API used by downstream code and by JDiff compatibility checks. The header captures the generating doclet, release name, source path, and full classpath used to build the API snapshot.

The early packages cover foundational configuration and filesystem behavior:

- `org.apache.hadoop.HadoopIllegalArgumentException` distinguishes Hadoop argument-validation failures from plain JDK `IllegalArgumentException`.
- `org.apache.hadoop.conf` defines the `Configurable` contract, the central mutable `Configuration` object, and the simple `Configured` base class.
- `org.apache.hadoop.crypto.key` abstracts secret key storage, versioning, provider lookup, generated key material, password-required warnings, and persistent flush semantics.
- `org.apache.hadoop.fs` begins the filesystem API surface, including `AbstractFileSystem`, stream adapters, block-location metadata, storage policy interfaces, optional stream controls, checksum exceptions/filesystems, public configuration-key constants, and the start of `ContentSummary`.

## Important APIs, Types, and Functions

### Hadoop and Configuration

- `HadoopIllegalArgumentException(String)` is a public subclass of `IllegalArgumentException` for invalid arguments originating inside Hadoop code.
- `Configurable` is a public interface with `setConf(Configuration)` and `getConf()`.
- `Configuration` implements `Iterable` and `Writable`. Constructors support default loading, disabling default resources, and cloning another configuration.
- Configuration resource APIs include `addDefaultResource`, many `addResource` overloads for classpath names, `URL`, `Path`, `InputStream`, named streams, and another `Configuration`, plus `reloadConfiguration` and synchronized `reloadExistingConfigurations`.
- Deprecation APIs include static/global `addDeprecations`, deprecated array-based `addDeprecation` overloads, replacement single-key overloads, `isDeprecated`, `setDeprecatedProperties`, `dumpDeprecatedKeys`, and `hasWarnedDeprecation`.
- Lookup and mutation APIs cover raw and expanded string retrieval (`get`, `getRaw`, `getTrimmed`), key-only detection, null-value allowance, system-property restrictions, `set`, `unset`, and `setIfUnset`.
- Typed accessors cover `int`, `long`, byte-size strings, `float`, `double`, `boolean`, enum values, time durations, storage sizes, regex patterns, integer ranges, string collections/arrays, and trimmed string collections/arrays.
- Secret retrieval APIs include `getPassword`, `getPasswordFromCredentialProviders`, and `getPasswordFromConfig`.
- Network and plugin APIs include `getSocketAddr`, `setSocketAddr`, `updateConnectAddr`, class loading by name, typed class lookup, `getInstances`, `setClass`, local path/file resolution, classpath resources, and configuration resource readers.
- Introspection and export APIs include `getFinalParameters`, `getProps`, `size`, `clear`, `iterator`, `getPropsWithPrefix`, `addTags`, several `writeXml` overloads, static `dumpConfiguration`, classloader accessors, `toString`, `setQuietMode`, `main`, `readFields`, `write`, `getValByRegex`, and tag queries (`getAllPropertiesByTag`, `getAllPropertiesByTags`, `isPropertyTag`).
- `Configured` implements `Configurable` and provides no-arg and `Configuration` constructors plus simple `setConf`/`getConf` storage.

### Crypto Key Providers

- `KeyProvider` is an abstract, thread-safe `Closeable` for secret key material. It stores/returns a `Configuration` and exposes `options(Configuration)` to create `KeyProvider.Options`.
- Abstract key operations include `getKeyVersion`, `getKeys`, `getKeyVersions`, `getMetadata`, `createKey(String, byte[], Options)`, `deleteKey`, `rollNewVersion(String, byte[])`, and `flush`.
- Concrete helper operations include bulk `getKeysMetadata`, `getCurrentKey`, generated-material `createKey(String, Options)`, generated-material `rollNewVersion(String)`, cache invalidation, close, password-warning/error helpers, `needsPassword`, `getBaseName`, protected `buildVersionName`, protected `generateKey`, and `findProvider`.
- Public key defaults and compatibility constants include `DEFAULT_CIPHER_NAME`, `DEFAULT_CIPHER`, `DEFAULT_BITLENGTH_NAME`, `DEFAULT_BITLENGTH`, `JCEKS_KEY_SERIALFILTER_DEFAULT`, and `JCEKS_KEY_SERIAL_FILTER`.
- `KeyProviderFactory` is an abstract service-loader factory. It declares `createProvider(URI, Configuration)` and static helpers `getProviders(Configuration)` and `get(URI, Configuration)`, keyed by public `KEY_PROVIDER_PATH`.

### Filesystem APIs

- `AbstractFileSystem` implements `PathCapabilities` and is the central abstract contract for scheme/authority-based filesystem implementations. Its constructor validates URI shape, supported scheme, authority requirement, and default port.
- Factory/statistics APIs include static `createFileSystem`, static `get`, instance/static `getStatistics`, synchronized static `clearStatistics`, `printStatistics`, and protected `getAllStatistics`.
- URI/path APIs include `checkScheme`, abstract `getUriDefaultPort`, `getUri`, `checkPath`, `getUriPath`, `makeQualified`, `getInitialWorkingDirectory`, and `getHomeDirectory`.
- Core file operations include abstract or overridable `getServerDefaults`, `resolvePath`, `create`, `createInternal`, `mkdir`, `delete`, `open`, `truncate`, `setReplication`, `rename`, `renameInternal`, symlink APIs, permission/owner/time updates, checksum/status/block-location queries, `msync`, directory listing, corrupt-block listing, checksum verification control, canonical service name, ACL operations, xattr operations, snapshots, storage policy operations, equality/hashCode, and `hasPathCapability`.
- `AvroFSInput` adapts `FSDataInputStream` or `FileContext` + `Path` to Avro `SeekableInput`, with `length`, positional `read`, `seek`, `tell`, and `close`.
- `BlockLocation` is `Serializable` block metadata. Constructors accept host/name/topology/cache/storage-id/storage-type arrays plus offset, length, and corruption state. Getters/setters expose hosts, cached hosts, names, topology paths, storage IDs, storage types, offset, length, corruption flag, and `toString`.
- `BlockStoragePolicySpi` exposes storage policy name, storage types, creation fallbacks, replication fallbacks, and copy-on-create behavior.
- Stream capability interfaces are small opt-in contracts: `ByteBufferReadable.read(ByteBuffer)`, `CanSetDropBehind.setDropBehind(Boolean)`, `CanSetReadahead.setReadahead(Long)`, and `CanUnbuffer.unbuffer()`.
- `ChecksumException` extends `IOException` and records the failed byte position via `getPos()`.
- `ChecksumFileSystem` extends `FilterFileSystem` and layers client-side checksum files over a raw filesystem. It exposes checksum-length calculations, checksum-file naming/detection, bytes-per-checksum, verification/write toggles, raw filesystem access, open/create/append/truncate/delete/rename/list/mkdir/copy/local-output paths, ACL and permission propagation, checksum-failure reporting, and a restricted `hasPathCapability`.
- `CommonConfigurationKeysPublic` is a public constants holder for documented common configuration keys and defaults. The visible fields cover filesystem defaults and intervals, topology mapping, trash, protected directories, local/FTP implementations, MapFile/Bloom and SequenceFile/TFile IO settings, caller context, IPC client/server tuning, RPC socket factory and SOCKS proxy, hash type, group mapping/cache behavior, security authentication/authorization/Kerberos/DNS/token/RPC protection, crypto codec/cipher/buffer/key provider defaults, KMS client cache/failover/timeouts, secure random settings, shell warnings/safe-delete, HTTP logs/idle timeout, credential providers, sensitive config keys, tag keys, and service shutdown timeout.
- `ContentSummary` starts at the end of this chunk. It extends `QuotaUsage`, implements `Writable`, and exposes legacy constructors plus getters for length, snapshot length, directory/file counts, snapshot directory/file counts, snapshot space consumed, erasure coding policy, and `equals(Object)` before the chunk ends.

## Control Flow

The XML itself is declarative. Runtime behavior is inferred from the documented API contracts:

- Configuration construction decides whether default resources are loaded, then resources are added in order. Later resources can override earlier ones unless a prior resource marks a property final.
- Configuration value retrieval resolves variables from other configuration properties, environment variables via the `env.` namespace, and Java system properties unless restrictions are enabled. Typed getters parse and normalize strings into primitives, durations, storage units, regex patterns, ranges, socket addresses, classes, or collections.
- Global deprecation registration is documented as lockless copy-and-swap behavior for deprecation contexts. Array-based overloads remain for compatibility but are deprecated in favor of single replacement-key overloads.
- Key creation/rolling flows either accept caller-supplied key material or generate material with `generateKey`, then delegate to the abstract provider-specific storage method. `flush` is the persistence boundary, and `invalidateCache` is the hook for stronger visibility after a key roll.
- Key-provider discovery flows from `KeyProviderFactory.getProviders(conf)` over URI paths from configuration, then through service-loaded factories that create providers for matching URI schemes.
- `AbstractFileSystem.get(uri, conf)` maps a URI scheme to a configuration property named like `fs.AbstractFileSystem.<scheme>.impl`, instantiates the implementation, and passes the URI and configuration to it. Path operations then validate scheme/authority, path syntax, and filesystem capabilities before dispatching to implementation-specific create/open/delete/list/etc. methods.
- `ChecksumFileSystem` routes user operations through checksum-aware wrappers. Reads verify checksum sidecar files when enabled, writes create/update checksum files when enabled, and operations such as rename/delete/copy/permission/ACL changes must coordinate raw data paths with their checksum path companions.
- `BlockLocation` is a mutable metadata carrier, so callers construct or receive arrays describing block placement, cached hosts, storage IDs/types, offset/length, and corruption state, then pass that metadata to scheduling, diagnostics, or UI layers.
- `CommonConfigurationKeysPublic` has no execution flow; its constants are consumed by `Configuration`, filesystems, IPC, security, crypto, KMS clients, shell code, and service shutdown code.

## State and Persistence Behavior

This JDiff XML persists a generated API snapshot for compatibility checks. It is not runtime state, but changing it reflects a changed public API.

`Configuration` is mutable in-memory state backed by an ordered list of resources and explicitly set properties. It can serialize through `Writable` (`write`/`readFields`) and export XML through `writeXml`. Important persistent or semi-persistent semantics include loaded resource order, final parameters, variable expansion, deprecated-key aliases, tag metadata, property sources, and optional loading from credential providers.

`Configured` only stores an in-memory `Configuration` reference. `Configurable` defines the convention used across Hadoop tools and services for configuration injection.

`KeyProvider` represents durable or transient key stores. The API explicitly differentiates transient providers from long-term storage, requires providers to be thread safe, and makes `flush()` the operation that ensures key changes reach persistent storage. Key versions are addressable durable identities, while generated key material and password handling are sensitive in-memory state.

`KeyProviderFactory` does not itself persist data, but its provider list is derived from configuration and Java service-loader registrations. URI order and scheme support affect which stores become available.

`AbstractFileSystem` instances hold immutable URI identity and a shared `FileSystem.Statistics` object keyed by scheme/authority. Filesystem methods operate on external durable state: files, directories, permissions, ACLs, xattrs, symlinks, snapshots, storage policies, block locations, and checksums. Static statistics are process-local counters and can be cleared or printed.

`AvroFSInput` stores stream position and delegates persistence to the underlying Hadoop filesystem. `BlockLocation` is serializable metadata, not file data. `ChecksumException` stores the position of detected corruption.

`ChecksumFileSystem` adds checksum sidecar files as durable state next to raw files. Its checksum length, checksum-file naming, verification flags, and write-checksum mode must remain compatible with existing data and readers.

`CommonConfigurationKeysPublic` constants are compile-time/public API state. Even deprecated constants must remain stable for binary/source compatibility until formally removed in a major API change. `ContentSummary` is a `Writable` value object for durable/transmitted filesystem summary data; this chunk only contains its beginning.

## Dependencies and Integration Points

The generator classpath in the header shows this API snapshot was built with Hadoop annotations/auth, Guava, commons libraries, Jetty/Jersey/Jackson, Avro, Protobuf, Curator/ZooKeeper, JSch, HTrace, Kerby, Jackson 2.x, Woodstox, dnsjava, Xerces, and related dependencies.

Direct API integrations in this chunk include:

- Java core types: `IllegalArgumentException`, `Iterable`, `Closeable`, `Serializable`, `IOException`, `FileNotFoundException`, `InputStream`, `Reader`, `File`, `PrintStream`, `DataInput`, `DataOutput`, `URI`, `URL`, `InetSocketAddress`, `ByteBuffer`, `Class`, `ClassLoader`, collections/maps/properties/sets/iterators, regex `Pattern`, `TimeUnit`, `NoSuchAlgorithmException`, and `URISyntaxException`.
- Hadoop configuration and IO: `Configuration`, `Writable`, `Path`, `FileSystem.Statistics`, `FSDataInputStream`, `FSDataOutputStream`, `FileContext`, `FileStatus`, `FsServerDefaults`, `FsStatus`, `RemoteIterator`, `BlockStoragePolicySpi`, `StorageType`, `Options.CreateOpts`, `Options.ChecksumOpt`, `CreateFlag`, `Progressable`, `AclStatus`, `AclEntry`, and permissions.
- Hadoop security: `AccessControlException`, group mapping and auth configuration constants, credential provider paths, Kerberos relogin tuning, SASL/RPC protection, impersonation provider configuration, key-provider and KMS client configuration.
- Avro integration through `org.apache.avro.file.SeekableInput`.
- Filesystem implementation lookup through configuration keys such as `fs.AbstractFileSystem.<scheme>.impl` and through `CommonConfigurationKeysPublic` constants that mirror `core-default.xml`.

## Risks and Edge Cases

- This source is generated API metadata. It does not show implementation details such as synchronization internals, parser behavior, stream handling, checksum algorithms, or filesystem-specific semantics.
- The line range ends mid-`ContentSummary`; a complete report for that class requires the later chunk.
- `Configuration` has broad global behavior: default resources, deprecations, system-property restrictions, classloader changes, and quiet mode can affect many components in one JVM.
- Variable expansion can read environment variables and system properties. Restriction flags and null-value handling are security-sensitive and should be tested around untrusted configuration sources.
- Deprecated configuration aliases need compatibility tests. Removing deprecated overloads or constants can break downstream code compiled against Hadoop 3.2.2.
- `getPasswordFromConfig` and credential-provider fallback behavior can expose secrets if clear-text fallback and sensitive-key filtering are misconfigured.
- `KeyProvider` implementations must be thread safe and must honor `flush` durability. Weak cache invalidation after `rollNewVersion` can cause stale encryption keys.
- Key version naming is part of the contract (`name@version` style from `buildVersionName`); parsing mistakes in `getBaseName` can select or delete the wrong key.
- `KeyProviderFactory.get(uri, conf)` returns null when no scheme provider exists, so callers must not assume a configured URI always yields a provider.
- `AbstractFileSystem` methods throw many checked exceptions; preserving exception specificity matters for callers that distinguish access denied, missing file, unresolved symlink, unsupported filesystem, and parent-not-directory conditions.
- URI scheme/authority validation is central. Incorrect `checkPath` or `makeQualified` behavior can route operations to the wrong filesystem or permit invalid paths.
- `msync` can throw `UnsupportedOperationException`; clients must handle filesystems without synchronization semantics.
- `BlockLocation` exposes mutable arrays. Callers and implementations need defensive-copy policy to avoid accidental mutation of block metadata.
- `ByteBufferReadable`, readahead, drop-behind, and unbuffer are optional stream capabilities; callers must handle unsupported operations and `null` advisory values.
- `ChecksumFileSystem` must keep raw data and checksum sidecars consistent through create, append, truncate, rename, delete, permission/ACL changes, and local copies. Disabling checksum verification or write checksums changes integrity behavior.
- `CommonConfigurationKeysPublic` includes misspellings in Javadocs such as "Defalt"; the text is harmless, but constants and deprecation annotations are compatibility-relevant.
- Deprecated constants such as `IO_SORT_MB_KEY`, `IO_SORT_FACTOR_KEY`, `HADOOP_SECURITY_GROUP_SHELL_COMMAND_TIMEOUT_SECS`, `HADOOP_SECURITY_GROUP_SHELL_COMMAND_TIMEOUT_SECS_DEFAULT`, `HADOOP_SYSTEM_TAGS`, and `HADOOP_CUSTOM_TAGS` should remain present for compatibility while users migrate to documented replacements.

## Test Signals

Useful validation for this API surface should include:

- JDiff/API golden tests confirming the package/class/member signatures in this chunk remain stable for Hadoop Common 3.2.x compatibility.
- `Configuration` tests for constructor default-resource loading, resource ordering, final parameters, variable expansion from config/env/system properties, system-property restriction flags, null-value property handling, typed parser success/failure cases, `getRaw` versus expanded `get`, and reload behavior.
- Deprecation tests for lockless global registration, deprecated array overload compatibility, alias propagation, warning suppression/tracking, and `setDeprecatedProperties`.
- Configuration serialization/export tests for `Writable` round trips, `writeXml` output, JSON-style `dumpConfiguration`, property sources, tags, prefix queries, regex queries, classloader behavior, and class instantiation through `getInstances`.
- Secret tests for credential-provider lookup, clear-text fallback, missing password handling, sensitive-key filtering, and `IOException` propagation from credential providers.
- `Configured`/`Configurable` tests for null and non-null configuration injection.
- `KeyProvider` contract tests for key creation with supplied/generated material, version naming/base-name parsing, current-key lookup, metadata/key-version listing, delete, roll, cache invalidation, password warnings/errors, transient-provider behavior, close, and durable `flush`.
- `KeyProviderFactory` tests for provider-path parsing, service-loader scheme matching, ordered provider creation, null return for unknown schemes, initialization failure propagation, and multiple-provider lookup through `findProvider`.
- `AbstractFileSystem` tests for URI constructor validation, scheme/authority checks, factory lookup from `fs.AbstractFileSystem.<scheme>.impl`, statistics sharing/clearing/printing, path qualification, invalid paths, and checked-exception mapping for every core operation.
- Filesystem behavior tests for create/open/delete/rename/truncate/list/status/block-location/server-defaults, symlink support, ACLs, xattrs, snapshots, storage policies, `msync`, canonical service name, and `hasPathCapability`.
- `AvroFSInput` tests for `SeekableInput` length/read/seek/tell/close behavior against an `FSDataInputStream`.
- `BlockLocation` tests for every constructor shape, getter/setter consistency, corrupt flag, storage ID/type arrays, cached hosts, topology paths, serialization compatibility, and array mutation policy.
- Optional stream capability tests for direct/heap `ByteBuffer` reads, drop-behind/readahead advisory values including null, unsupported-operation behavior, and `unbuffer`.
- `ChecksumException` tests for message and position preservation.
- `ChecksumFileSystem` tests for checksum sidecar naming and length calculations, bytes-per-sum, open verification, create/append/truncate checksum updates, delete/rename sidecar consistency, copy-to-local with and without CRCs, checksum-failure reporting, permission/owner/ACL propagation, and blocked path capabilities.
- `CommonConfigurationKeysPublic` tests that public constants match `core-default.xml` keys/defaults, deprecated constants remain present with expected replacement guidance, and security/crypto/KMS/IPC/filesystem constants are consumed by their owning modules.

## Cross-Chunk Notes

This is the first chunk of `Apache_Hadoop_Common_3.2.2.xml`; there is no previous chunk needed for context before line 1. The chunk ends inside `org.apache.hadoop.fs.ContentSummary` at `equals(Object)`, so the merge/reconciliation lane must combine this with the following chunk before treating `ContentSummary` or later `org.apache.hadoop.fs` APIs as complete.
