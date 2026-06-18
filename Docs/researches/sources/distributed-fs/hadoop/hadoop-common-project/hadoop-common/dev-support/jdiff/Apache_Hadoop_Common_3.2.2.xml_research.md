# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.2.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007192`: lines 1-6124, `Docs/researches/chunks/subset-b-007192_research.md`
- `subset-b-007193`: lines 6125-12096, `Docs/researches/chunks/subset-b-007193_research.md`
- `subset-b-007194`: lines 12097-18158, `Docs/researches/chunks/subset-b-007194_research.md`
- `subset-b-007195`: lines 18159-24459, `Docs/researches/chunks/subset-b-007195_research.md`
- `subset-b-007196`: lines 24460-30682, `Docs/researches/chunks/subset-b-007196_research.md`
- `subset-b-007197`: lines 30683-35381, `Docs/researches/chunks/subset-b-007197_research.md`

## Chunk Research

### subset-b-007192: lines 1-6124

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

### subset-b-007193: lines 6125-12096

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.2.xml lines 6125-12096

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.2.2. It begins inside the tail of `org.apache.hadoop.fs.ContentSummary`, then covers complete public API metadata for `CreateFlag`, `FileAlreadyExistsException`, `FileChecksum`, `FileContext`, `FileStatus`, and `FileSystem`. It then enters `FileUtil` and covers its public API through the beginning of `createLocalTempFile(File, String, boolean)`, where the line range ends mid-method documentation.

The source is generated compatibility metadata rather than implementation source. The research surface is therefore the Hadoop public/protected API contract: type names, inheritance, implemented interfaces, fields, method signatures, checked exceptions, static/final/abstract/synchronized markers, deprecations, and embedded Javadocs.

## Purpose

The visible `ContentSummary` tail documents command-output formatting for namespace and quota summaries. It exposes string and header rendering paths for directory count, file count, content size, quota, storage-type quota, human-readable units, and snapshot-exclusion behavior.

`CreateFlag` defines file creation and append semantics shared by `FileContext`, `FileSystem`, builders, and lower-level filesystem implementations. It validates combinations such as `CREATE`, `APPEND`, `OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`.

`FileAlreadyExistsException` is the public checked exception used when an operation targets an existing file or directory and overwrite semantics are not enabled.

`FileChecksum` is the abstract serializable checksum contract for files. It identifies the checksum algorithm, byte length, byte value, and checksum options, and defines equality based on algorithm and value.

`FileContext` is Hadoop's higher-level filesystem interface and the documented successor-style API for per-client file state. It binds a default `AbstractFileSystem`, working directory, user identity, and umask, then exposes create, open, mkdir, delete, rename, truncate, listing, symlink, ACL, xattr, snapshot, storage-policy, and capability operations across URI-addressed filesystems.

`FileStatus` is the client-side metadata record for a file, directory, or symlink. It carries path, length, replication, block size, timestamps, permissions, owner/group, symlink target, and attribute flags for ACL, encryption, erasure coding, and snapshot support. It is comparable, Java-serializable, Hadoop-`Writable`, and validates object deserialization.

`FileSystem` is the long-standing abstract base class for Hadoop filesystems. It is implemented by local, HDFS, object-store, and third-party filesystems and defines URI resolution, instance caching, path qualification, create/open/append/delete/list APIs, metadata mutation, checksums, ACLs, xattrs, snapshots, storage policies, trash roots, statistics, storage statistics, path capabilities, and builder entry points.

The visible `FileUtil` portion provides static bridge utilities for converting `FileStatus` arrays to paths, deleting local trees, copying between local and Hadoop filesystems, adapting paths for shell commands, unpacking archives, creating symlinks, changing permissions/owners, and performing platform-independent local permission checks.

## Important APIs, Types, and Functions

### ContentSummary Tail

- `hashCode()` is present at the chunk start, indicating `ContentSummary` participates in value-style comparison.
- `getHeader(boolean qOption)` returns formatted summary headers. Without quota it covers directory count, file count, and content size; with quota it adds quota and remaining quota fields.
- `getHeaderFields()` and `getQuotaHeaderFields()` expose the column names used by summary output.
- `toString()` overloads render the summary with combinations of quota output, human-readable units, storage-type quota output, snapshot exclusion, and explicit `StorageType` lists.

### CreateFlag and Exceptions

- `CreateFlag` is a public enum. Normal enum methods `values()` and `valueOf(String)` are exposed.
- `validate(EnumSet)` checks for invalid flag combinations and throws `HadoopIllegalArgumentException`.
- `validate(Object path, boolean pathExists, EnumSet flag)` applies create-operation semantics to a path and whether it exists, throwing `IOException` and `HadoopIllegalArgumentException`.
- `validateForAppend(EnumSet)` requires `APPEND` and rejects `OVERWRITE` for append operations.
- The documented valid combinations include create-if-absent, append-if-present, overwrite-if-present, create-or-append, create-or-overwrite, sync block, lazy persist, and append-to-new-block. Invalid combinations include `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`.
- `FileAlreadyExistsException` extends `IOException` and has no-arg and message constructors.

### FileChecksum

- `FileChecksum` is abstract and implements `Writable`.
- Abstract methods `getAlgorithmName()`, `getLength()`, and `getBytes()` define the checksum identity and bytes.
- `getChecksumOpt()` returns an `Options.ChecksumOpt` when available.
- `equals(Object)` returns true only when checksum algorithms and values match; `hashCode()` accompanies that equality contract.

### FileContext

- `FileContext` implements `PathCapabilities`.
- Static factory overloads create contexts from an `AbstractFileSystem`, default config, local filesystem, default `URI`, explicit `Configuration`, or both URI and configuration.
- `getFSofPath(Path)` resolves an absolute or fully qualified path to an `AbstractFileSystem`, throwing `UnsupportedFileSystemException` or `IOException`.
- Working-directory APIs are `setWorkingDirectory(Path)` and `getWorkingDirectory()`. The Javadocs emphasize that working-directory resolution is prefix-based and does not follow symlinks like Unix inode current directories.
- Identity and defaults include `getUgi()`, `getHomeDirectory()`, `getUMask()`, and `setUMask(FsPermission)`.
- Path handling includes `resolvePath(Path)` for following symlinks and mount points, and `makeQualified(Path)` for filling in default filesystem and working-directory context.
- Core mutation APIs include `create(Path, EnumSet<CreateFlag>, CreateOpts...)`, builder `create(Path)`, `mkdir(Path, FsPermission, boolean)`, `delete(Path, boolean)`, `truncate(Path, long)`, `setReplication(Path, short)`, `rename(Path, Path, Rename...)`, `setPermission`, `setOwner`, `setTimes`, `createSymlink`, and delete-on-exit registration.
- Read and status APIs include `open(Path)`, `open(Path, int)`, `getFileStatus(Path)`, `getFileLinkStatus(Path)`, `getLinkTarget(Path)`, `getFileChecksum(Path)`, `getFsStatus(Path)`, `listStatus(Path)`, `listCorruptFileBlocks(Path)`, and `listLocatedStatus(Path)`.
- Utility and statistics APIs include `util()`, `resolve(Path)`, `resolveIntermediate(Path)`, `getStatistics(Path)`, `clearStatistics()`, `printStatistics()`, and `getAllStatistics()`.
- Metadata extension APIs include ACL methods (`modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, `getAclStatus`) and xattr methods (`setXAttr`, flagged `setXAttr`, `getXAttr`, all/named `getXAttrs`, `removeXAttr`, `listXAttrs`).
- Snapshot APIs include default-name and explicit-name `createSnapshot`, `renameSnapshot`, and `deleteSnapshot`.
- Storage policy APIs include `satisfyStoragePolicy`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, and `getAllStoragePolicies`.
- `hasPathCapability(Path, String)` delegates capability checks to the bonded `AbstractFileSystem`.
- Public fields include `LOG`, compatibility `DEFAULT_PERM`, preferred `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`.

### FileStatus

- `FileStatus` implements `Writable`, raw `Comparable`, `Serializable`, and `ObjectInputValidation`.
- Constructors cover empty deserialization, compact status without permissions, status without symlink support, status with symlink, status with boolean ACL/encryption/erasure flags, status with a set of attributes, and a copy constructor.
- `attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts booleans into an attribute-flag set.
- Accessors expose length, file/directory/symlink classification, block size, replication, modification time, access time, permission, ACL flag, encryption flag, erasure-coded flag, snapshot-enabled flag, owner, group, path, and symlink target.
- Mutators include `setPath(Path)`, protected `setPermission`, protected `setOwner`, protected `setGroup`, and public `setSymlink(Path)`.
- `isDir()` is final and deprecated in favor of `isFile()`, `isDirectory()`, and `isSymlink()`.
- `compareTo(FileStatus)` and `compareTo(Object)` compare file statuses; the object overload was restored for binary compatibility by HADOOP-14683.
- `equals(Object)` and `hashCode()` are path-name based.
- `readFields(DataInput)` and `write(DataOutput)` encode as protobuf but are deprecated in favor of using `PBHelper` and protobuf serialization directly.
- `validateObject()` supports Java deserialization validation, and `NONE` is a shared empty attribute set.

### FileSystem

- `FileSystem` extends `Configured` and implements `Closeable`, `DelegationTokenIssuer`, and `PathCapabilities`.
- Static lookup APIs include `get(Configuration)`, `get(URI, Configuration)`, `get(URI, Configuration, String user)`, `newInstance(...)`, `newInstanceLocal(Configuration)`, `getLocal(Configuration)`, `getNamed(String, Configuration)` deprecated, `getDefaultUri(Configuration)`, and `setDefaultUri(...)`.
- Instance lifecycle and identity include protected constructor, `initialize(URI, Configuration)`, abstract `getUri()`, default `getScheme()`, protected `getCanonicalUri()`, `canonicalizeUri(URI)`, `getDefaultPort()`, `getCanonicalServiceName()`, deprecated `getName()`, `close()`, `closeAll()`, and `closeAllForUGI(UserGroupInformation)`.
- URI and path checks include static protected `getFSofPath(Path, Configuration)`, `makeQualified(Path)`, and protected `checkPath(Path)`.
- Creation APIs include static permission-preserving `create(FileSystem, Path, FsPermission)`, many `create(...)` overloads with overwrite, buffer size, replication, block size, progress, checksum options, and permission, `primitiveCreate`, non-recursive creation overloads, `createNewFile`, and builder `createFile(Path)`.
- Directory APIs include static `mkdirs(FileSystem, Path, FsPermission)`, instance `mkdirs(Path)`, abstract `mkdirs(Path, FsPermission)`, `primitiveMkdir`, and `primitiveMkdir(Path, FsPermission)`.
- Read and append APIs include multiple `open(...)` overloads, builder-related `getPathHandle` and `createPathHandle`, append overloads, and builder `appendFile(Path)`.
- Block and server-default APIs include `getFileBlockLocations(FileStatus, long, long)`, `getFileBlockLocations(Path, long, long)`, `getServerDefaults()`, and `getServerDefaults(Path)`.
- Mutating filesystem APIs include abstract `rename(Path, Path)`, protected option-based `rename(Path, Path, Rename...)`, `concat`, `truncate`, abstract recursive `delete`, deprecated one-argument `delete`, `setReplication`, `setPermission`, `setOwner`, `setTimes`, quotas, ACLs, xattrs, snapshots, storage policies, and `msync()`.
- Delete-on-exit APIs are `deleteOnExit(Path)`, `cancelDeleteOnExit(Path)`, and protected `processDeleteOnExit()`.
- Status and listing APIs include `exists`, deprecated `isDirectory`, deprecated `isFile`, deprecated `getLength`, `getContentSummary`, `getQuotaUsage`, abstract `listStatus(Path)`, filtered and multi-path `listStatus` overloads, `globStatus` overloads, `listLocatedStatus`, protected filtered `listLocatedStatus`, `listStatusIterator`, `listFiles`, `getFileStatus`, and `getFileLinkStatus`.
- Local copy APIs include `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, `moveToLocalFile`, `startLocalOutput`, and `completeLocalOutput`.
- Symlink APIs include `createSymlink`, `supportsSymlinks`, `getLinkTarget`, `resolveLink`, static `areSymlinksEnabled()`, and static `enableSymlinks()`.
- Checksum and verification APIs include `getFileChecksum(Path)`, `getFileChecksum(Path, long)`, `setVerifyChecksum(boolean)`, and `setWriteChecksum(boolean)`.
- Status/statistics APIs include `getStatus()`, `getStatus(Path)`, `getUsed()`, `getUsed(Path)`, block-size and replication defaults, static synchronized legacy statistics accessors, `clearStatistics()`, `printStatistics()`, per-instance `getStorageStatistics()`, and static `getGlobalStorageStatistics()`.
- Trash and capability APIs include `getTrashRoot(Path)`, `getTrashRoots(boolean)`, `hasPathCapability(Path, String)`, and static `getFileSystemClass(String, Configuration)`.
- Public fields include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and protected instance `statistics`.

### FileUtil Segment

- `stat2Paths(FileStatus[])` and `stat2Paths(FileStatus[], Path)` convert statuses to paths, with the second overload returning the supplied default path when stats are null.
- `fullyDeleteOnExit(File)` recursively registers local files for JVM-exit deletion.
- `fullyDelete(File)` and `fullyDelete(File, boolean)` delete local files/directories recursively. Their symlink behavior is explicitly documented: deleting a symlink does not delete the target, whether the target is a file or directory.
- `readLink(File)` returns a symlink target or empty string if not a symlink or inaccessible.
- `fullyDeleteContents(File)` and its permission-granting overload delete the contents of a directory without deleting the directory itself; if the argument is a symlink to a directory, contents of the target directory are deleted.
- Deprecated `fullyDelete(FileSystem, Path)` delegates recursive remote deletion use cases toward `FileSystem.delete(Path, boolean)`.
- `copy(...)` overloads move data between `FileSystem` instances, arrays of source paths, a `FileStatus` source, local `File`, and local destination `File`, with delete-source and overwrite options where available.
- `makeShellPath(...)` and `makeSecureShellPath(File)` convert local filenames to shell-compatible paths, with the secure variant intended to avoid script injection attacks.
- `getDU(File)` computes local disk usage with a basic implementation.
- `unZip(InputStream, File)` and `unZip(File, File)` extract ZIP data to a directory.
- `unTar(InputStream, File, boolean)` and `unTar(File, File)` extract `.tar`, `.tar.gz`, and `.tgz` archives; the stream overload can throw `IOException`, `InterruptedException`, and `ExecutionException`.
- `symLink(String, String)` creates a local symlink and returns zero on success; Windows security failures are documented to return code 2 with a warning.
- `chmod` overloads change file permissions with optional recursion.
- `setOwner(File, String, String)` changes local file owner/group and requires at least one of user or group to be non-null.
- `setReadable`, `setWritable`, `setExecutable`, `canRead`, `canWrite`, and `canExecute` provide platform-independent wrappers over Java `File` permission APIs, especially for Windows.
- `setPermission(File, FsPermission)` sets local permissions, using Java primitives instead of forking when group and other bits match.
- The chunk ends at the start of final static `createLocalTempFile(File basefile, String prefix, boolean isDeleteOnExit)`.

## Control Flow

The XML document has no executable control flow, but its API contracts imply several important operational paths.

`CreateFlag` validation is a gate before create/append calls mutate filesystem state. A caller chooses an `EnumSet`; validation checks illegal combinations, then path-existence-specific validation decides whether the operation creates, appends, overwrites, or fails with an exception.

`FileContext` factory methods establish default filesystem resolution and configuration first. Each path operation then qualifies or resolves the path, selects the owning `AbstractFileSystem`, applies user/umask defaults where relevant, and dispatches to the filesystem-specific implementation. The create builder path defers verification and filesystem mutation until `FSDataOutputStreamBuilder.build()` is invoked.

`FileContext` path resolution distinguishes fully qualified URIs, slash-relative paths resolved against the default filesystem, and working-directory-relative paths resolved by prefixing the FileContext working directory. The Javadocs explicitly reject relative paths with a scheme such as `scheme:foo/bar`.

`FileStatus` acts as a data transfer object. Filesystem implementations populate it, callers inspect flags and metadata, collection code compares it by path, and legacy serialization flows through protobuf-backed `readFields`/`write` while newer code should use `PBHelper` directly.

`FileSystem.get(URI, Configuration)` has explicit cache control flow: if `fs.$SCHEME.impl.disable.cache` is true, it creates and initializes a new instance without caching; otherwise it returns a matching cached instance or creates, initializes, caches, and returns a new one. `newInstance(...)` bypasses cache reuse and always returns a unique object.

`FileSystem.initialize(URI, Configuration)` is the required setup hook after construction. Subclasses overriding it must call the superclass implementation, while deciding whether to alter configuration before the call and whether to call before or after subclass setup.

`FileSystem` create/open/list/delete operations mix abstract hooks and default convenience wrappers. For example, convenience `open(Path)` routes to buffer-size overloads, `mkdirs(Path)` routes to `mkdirs(Path, FsPermission)`, and many local-copy methods route through `FileUtil.copy`-style behavior.

`FileSystem.rename(Path, Path, Rename...)` documents overwrite and type-compatibility rules separately from the abstract boolean `rename(Path, Path)`. The option-based implementation is explicitly non-atomic by default; atomicity is filesystem-specific.

Delete-on-exit flow registers paths on an instance, removes them with `cancelDeleteOnExit`, and recursively processes remaining paths when the `FileSystem` is closed or a cached filesystem is closed by the JVM shutdown hook.

Listing flow is split between eager arrays (`listStatus`), sorted globbing (`globStatus`), block-location-bearing iterators (`listLocatedStatus`, `listFiles`), and on-demand remote iteration (`listStatusIterator`). Implementations are encouraged to override iterator-based methods for efficiency.

`FileUtil` local delete flow treats symlinks differently depending on whether deleting the link itself or deleting contents through a link. Copy flow can optionally delete sources after successful transfer, so error ordering matters to avoid data loss. Archive extraction and permission APIs delegate to local filesystem and shell/platform mechanisms.

## State and Persistence Behavior

This JDiff file persists the 3.2.2 API shape for compatibility checks. It does not persist Hadoop runtime state.

`ContentSummary` instances represent filesystem-derived counts, quotas, and storage-type usage. The visible methods persist nothing themselves but define stable textual output that downstream tools and tests may parse.

`FileContext` carries process-local client state: default `AbstractFileSystem`, working directory, user identity, and umask. It also exposes statistics and delete-on-exit behavior. Filesystem operations invoked through it persist data or metadata in the target filesystem: file bytes, directories, permissions, ownership, timestamps, ACLs, xattrs, snapshots, quotas, storage policies, and symlinks.

`FileStatus` is both runtime metadata and a serialization boundary. It is Java-serializable and `Writable`, but its `Writable` methods are deprecated in favor of protobuf conversion. Its equality/hash state is path-only, while its payload contains much richer metadata. Attribute flags compact ACL, encryption, erasure coding, and snapshot capability state into a set.

`FileSystem` has both global and instance state. Global state includes cached filesystem instances keyed by URI/user/configuration behavior, global shutdown hooks, symlink enablement, service-loaded implementation classes, and global storage/statistics registries. Instance state includes configuration, URI identity, working directory in implementations, delete-on-exit path sets, per-instance storage statistics, protected legacy `statistics`, and any implementation-specific clients or connections.

`FileSystem.close()` is a state transition: after close, methods on the filesystem and streams created from it have undefined behavior. It also releases resources, processes delete-on-exit paths, and removes cached instances when applicable.

`FileUtil` primarily manipulates local filesystem state. Recursive deletion and archive extraction can partially mutate directories on failure. Permission helpers alter local file modes/ownership. `fullyDeleteOnExit` registers process-exit cleanup in JVM-local state rather than durable metadata.

## Dependencies and Integration Points

This chunk integrates with Java platform APIs such as `URI`, `File`, `IOException`, `FileNotFoundException`, `InvalidObjectException`, `DataInput`, `DataOutput`, `InputStream`, `Closeable`, `Serializable`, `ObjectInputValidation`, `EnumSet`, `Collection`, `List`, `Map`, `Set`, `ServiceLoader`, and `ExecutionException`.

Hadoop configuration and security integration points include `Configuration`, `Configured`, `UserGroupInformation`, `AccessControlException`, `DelegationTokenIssuer`, token service names, and `SecurityUtil`.

Hadoop filesystem integration points include `Path`, `PathFilter`, `PathCapabilities`, `PathHandle`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `AbstractFileSystem`, `LocalFileSystem`, `RawLocalFileSystem`, `FsStatus`, `FsServerDefaults`, `BlockLocation`, `BlockStoragePolicySpi`, `StorageType`, `StorageStatistics`, `GlobalStorageStatistics`, `RemoteIterator`, `ContentSummary`, `QuotaUsage`, `FileChecksum`, and the `Options` nested types for create options and rename options.

Permission and metadata integration points include `FsPermission`, ACL entry/status types under `org.apache.hadoop.fs.permission`, xattr namespace/flag handling, snapshot-capable filesystems, storage policy implementations, and protobuf helpers referenced as `PBHelper`.

`FileSystem` implementation discovery depends on configuration keys, service loading, scheme bindings, URI canonicalization, and filesystem-specific default ports. Its documented behavioral baseline is HDFS: the class Javadoc says that if HDFS differs from the written documentation or external filesystem spec, HDFS behavior is normative.

`FileUtil` bridges Hadoop `FileSystem` APIs with local `java.io.File`, shell path handling, archive formats, and OS-specific permission/symlink behavior.

## Risks and Edge Cases

- This chunk starts inside `ContentSummary`; the earlier fields, constructors, and accessors for the class are outside this range and must be merged from the previous chunk before producing a complete class report.
- This chunk ends inside `FileUtil.createLocalTempFile`; later parameters, full documentation, subsequent methods, fields, and class closing metadata are outside this range.
- JDiff gives signatures and Javadocs, not implementation. Exact cache keys, synchronization, exception text, retry behavior, stream handling, ACL/xattr validation, and object-store-specific semantics require implementation-source verification.
- `ContentSummary.toString` output is a compatibility surface. Changing spacing, headers, or inclusion/exclusion of snapshot and storage-type fields can break shell tooling and golden-output tests.
- `CreateFlag` combinations are easy to misuse. `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE` are invalid, while `CREATE|APPEND` and `CREATE|OVERWRITE` intentionally mean different things when the path exists.
- `FileContext.setWorkingDirectory` is prefix-based and does not follow symlinks. Code expecting Unix current-directory inode semantics can resolve paths differently after symlink changes.
- `FileContext.create(Path)` builder does not mutate filesystem state until `build()`; code that assumes validation at builder construction can miss delayed failures.
- Many `FileContext` methods list RPC client/server and unexpected-server exception cases in the Javadocs. Remote filesystems can fail with transport or server-side failures beyond local `IOException` subclasses.
- `FileStatus.equals` and `hashCode` use only path names. Two statuses for the same path but different timestamps, permissions, encryption flags, or lengths compare equal, which can surprise set/map users.
- `FileStatus.readFields` and `write` remain for binary/API compatibility but are deprecated. New code should avoid depending on their serialized wire format unless compatibility requires it.
- `FileSystem.get` returns cached instances unless caching is disabled. Shared cached instances can leak mutable state such as working directory, statistics, or delete-on-exit registrations across callers.
- `FileSystem.newInstance` avoids cache sharing but requires explicit close discipline to avoid resource leaks.
- Subclasses overriding `initialize` must call superclass initialization. Failure can break statistics, configuration, URI setup, or cache/service-name behavior.
- `FileSystem.getScheme()` default throws `UnsupportedOperationException`; implementations that do not override it may fail capability or builder code expecting a scheme.
- `FileSystem.rename(Path, Path)` atomicity is implementation-specific, and the option-based default implementation is documented as non-atomic. Applications needing atomic commit must validate the target filesystem.
- `FileSystem.setReplication` defaults to returning true for filesystems without replication support, possibly bypassing existence checks. Callers cannot interpret true as proof that replication changed.
- Deprecated `exists`, `isFile`, `isDirectory`, and `getLength` convenience checks can cause redundant RPCs and time-of-check/time-of-use races if used before a later operation.
- Delete-on-exit can significantly extend JVM shutdown, especially on remote filesystems or object stores, and clean shutdown is not guaranteed.
- `globStatus` has distinct null-vs-empty behavior depending on whether the pattern contains a glob and whether a non-glob path exists.
- ACL, xattr, snapshot, storage-policy, append, truncate, concat, checksum, and symlink APIs are optional or filesystem-specific. Default implementations may throw `UnsupportedOperationException`.
- Static symlink enablement in `FileSystem` is global process state. Tests or applications that toggle it can affect unrelated code.
- `FileUtil.fullyDeleteContents` follows symlink-to-directory targets when deleting contents, unlike `fullyDelete` which deletes the symlink itself. This difference is security-sensitive.
- `FileUtil.copy` with `deleteSource=true` must only remove the source after successful copy; partial failures can otherwise lose data or leave duplicate data.
- `FileUtil.makeShellPath` and `makeSecureShellPath` are sensitive to platform quoting and script injection risks. Callers should prefer the secure variant for untrusted paths.
- Archive extraction methods must guard against path traversal, overwrites, partial extraction, and interrupted external tar execution. The Javadocs identify command interruption and task submission failures for tar streams.
- Windows permission APIs differ from Unix. `setExecutable(false)` on a directory does not prevent file create/delete/rename within that directory on Windows.

## Test Signals

Useful tests for this API surface should include:

- JDiff/API compatibility checks ensuring all public/protected methods, fields, deprecations, visibility, final/static markers, exceptions, and implemented interfaces in this chunk remain stable.
- `ContentSummary` golden-output tests for every visible `toString` overload, human-readable formatting, quota and non-quota headers, storage-type lists, and snapshot-exclusion flag behavior.
- `CreateFlag` validation tests for every documented valid and invalid combination, append-specific validation, path-exists and path-missing branches, and exception types.
- `FileChecksum` tests for equality/hashCode by algorithm and bytes, checksum option propagation, `Writable` round trips in concrete implementations, and mismatched algorithm/value cases.
- `FileContext` factory tests for default config, explicit URI/config, local filesystem, and direct `AbstractFileSystem` construction, including unsupported scheme failures.
- `FileContext` path resolution tests for fully qualified URIs, slash-relative paths, working-directory-relative paths, illegal relative-with-scheme paths, symlink and mount-point resolution, and default FS selection.
- `FileContext` mutation tests for create options, delayed builder validation, mkdir parent creation, delete recursive behavior, truncate true/false completion behavior, rename overwrite semantics, permissions with umask, ownership, timestamps, checksums, and setVerifyChecksum behavior.
- `FileContext` metadata tests for ACL replacement/removal, xattr namespace and flag handling, snapshot create/rename/delete, storage policy set/unset/query, corrupt-block listing, located status listing, and path capability delegation.
- `FileStatus` tests for every constructor family, default permission/owner/group substitution on nulls, attribute flag conversion, file/directory/symlink classification, symlink target behavior, path-only equality/hashCode, compareTo object compatibility, `toString`, copy constructor, Java deserialization validation, and deprecated protobuf-backed `Writable` serialization.
- `FileSystem` cache tests for `get` vs `newInstance`, cache disabling through `fs.$SCHEME.impl.disable.cache`, close removal from cache, closeAll, closeAllForUGI, UGI-specific lookup, and resource cleanup.
- `FileSystem` subclass contract tests ensuring `initialize` calls superclass, URI canonicalization fills default ports, `checkPath` rejects foreign schemes/authorities, canonical service names work with tokens, and `getFileSystemClass` discovers service-loaded implementations.
- `FileSystem` operation tests for create overloads, primitive create/mkdir, non-recursive create, open overloads, append optional support, concat optional support, setReplication default semantics, rename type/overwrite cases, truncate unsupported and async-completion cases, recursive delete, and delete-on-exit processing.
- Listing tests for `listStatus` ordering assumptions, filter behavior, multi-path behavior, corrupt-block iterator, glob syntax and null/empty return behavior, located status block locations, lazy `listStatusIterator`, and recursive `listFiles`.
- Local copy tests for copy/move from local, copy/move to local, raw local filesystem option avoiding CRC files, local temp output workflow, delete-source ordering, overwrite behavior, and failure cleanup.
- Metadata tests for content summary, quota usage and quota setters, block-size/default-replication defaults, file status vs link status, link target resolution, checksum-by-length behavior, verify/write checksum toggles, fs status, used space, and `msync`.
- Statistics tests for legacy synchronized statistics methods, `clearStatistics`, `printStatistics`, per-instance `getStorageStatistics`, and global storage statistics registration.
- Trash/capability tests for per-path trash root, all-users trash roots, default capability false behavior, and filesystem-specific capability overrides.
- `FileUtil` tests for `stat2Paths` null/default handling, recursive delete symlink semantics, partial-delete false returns, permission-granting delete path, `readLink` empty-string behavior, local and cross-filesystem copy variants, shell path escaping, disk-usage calculation, ZIP/TAR extraction including interrupted tar, local symlink return codes, chmod/setOwner wrappers, Windows permission differences, and `setPermission` no-fork optimization.

## Cross-Chunk Notes

The previous chunk is required to complete `ContentSummary`. The next chunk is required to complete `FileUtil`, starting from the rest of `createLocalTempFile(File, String, boolean)` and continuing through any later utility methods and package metadata. The final reconciled file-level report should avoid treating this chunk's `FileUtil` coverage as complete.

### subset-b-007194: lines 12097-18158

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.2.xml lines 12097-18158

## Scope

This chunk is a generated JDiff API snapshot for Apache Hadoop Common 3.2.2. It starts in the tail of `org.apache.hadoop.fs.FileUtil`, covers a large public/protected portion of `org.apache.hadoop.fs`, then covers `org.apache.hadoop.fs.ftp`, high-availability APIs under `org.apache.hadoop.ha`, protobuf-facing HA protocol bridge interfaces, the package note for `org.apache.hadoop.http.lib`, and the beginning of `org.apache.hadoop.io` through the start of `DefaultStringifier.toString(T)`.

Because this is JDiff XML, the research surface is the compatibility contract rather than method bodies: package membership, class/interface inheritance, implemented interfaces, public/protected method signatures, fields, checked exceptions, deprecation markers, and embedded Javadocs. The chunk begins and ends inside classes, so the merge lane must combine it with neighboring chunks for complete `FileUtil` and `DefaultStringifier` coverage.

## Purpose

The `FileUtil` tail provides convenience helpers for local-file replacement, safer directory listing wrappers, classpath-manifest jar creation, jar wildcard expansion, filesystem comparison, and simple whole-file writes through either `FileSystem` or `FileContext`.

The main `org.apache.hadoop.fs` section documents client-facing file system abstractions and concrete local implementations. It includes the `FilterFileSystem` delegation wrapper, stream wrappers for positioned reads and synchronized writes, builder APIs for output streams, path representation and validation, local/raw-local filesystem behavior, status/quota/statistics models, storage-type metadata, capability queries, trash policy extension points, path/upload handle tokens, xattr codecs, and exception types.

The `org.apache.hadoop.fs.ftp` section exposes an FTP-backed `FileSystem` using Apache Commons Net, with the standard Hadoop `FileSystem` lifecycle and operations adapted to remote FTP semantics.

The `org.apache.hadoop.ha` section defines the public contract used by Hadoop high-availability frameworks and admin commands: fencing methods, HA service health/state transitions, helper wrappers for RPC exception unwrapping, HA service targets, and failure exception types.

The `org.apache.hadoop.io` section begins the Hadoop serialization layer: map class-id metadata, primitive and writable arrays, byte-sequence comparables, bloom-backed map file declaration, primitive writable values, byte buffer pools, compressed lazy-inflation writables, and `DataOutput` to `OutputStream` adaptation.

## Important APIs, Types, and Functions

### File Utilities

- `FileUtil.replaceFile(File src, File target)` moves a source file to a target path and throws `IOException` on failure.
- `FileUtil.listFiles(File)` and `FileUtil.list(File)` wrap Java `File` listing calls so invalid directories, unreadable directories, or I/O problems surface as exceptions instead of ambiguous `null`.
- `FileUtil.createJarWithClassPath(...)` creates a small jar with a manifest classpath. The documented purpose is to bypass platform command-line length limits, expand environment variables before manifest insertion, and expand `*` jar wildcards because jar manifests do not support wildcard classpath entries.
- `FileUtil.getJarsInDirectory(String[, boolean])` expands a directory or wildcard path into jar URLs, returning an empty list when no local directory or jars exist.
- `FileUtil.compareFs(FileSystem, FileSystem)` compares filesystem identity.
- The overload family `FileUtil.write(...)` writes byte arrays, iterable text lines, or one `CharSequence` to a `Path` through `FileSystem` or `FileContext`, creating or overwriting the destination and returning the filesystem/context. Text overloads support explicit `Charset` and UTF-8 defaults.
- `FileUtil.SYMLINK_NO_PRIVILEGE` is a public constant related to symlink privilege handling.

### FileSystem Wrappers and Streams

- `FilterFileSystem` extends `FileSystem` and contains a protected `fs` delegate plus a `swapScheme` field. Its constructors accept no delegate or a wrapped `FileSystem`; almost all operations forward to the contained filesystem.
- Delegated `FilterFileSystem` operations include initialization, URI/canonical URI handling, path qualification/checking, block locations, open/create/append/concat, non-recursive create, replication, rename/truncate/delete, listing variants, working directory/home, status, local copy helpers, default block size/replication/server defaults, file status, msync/access, symlinks, checksums, permissions/owner/times, snapshots, ACLs, xattrs, storage policies, trash roots, output stream builders, and path capability checks.
- `FsConstants` defines public constants for local, FTP, ViewFs, maximum symlink path links, ViewFs overload scheme implementation naming, and ViewFs/ViewFs-overload type strings.
- `FSDataInputStream` extends `DataInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `CanUnbuffer`, and `StreamCapabilities`. It exposes `seek`, `getPos`, positioned `read`, positioned `readFully`, `seekToNewSource`, `ByteBuffer` reads, enhanced zero-copy buffer reads with `ByteBufferPool`, `releaseBuffer`, `unbuffer`, `getFileDescriptor`, cache hints, and `hasCapability`.
- `FSDataOutputStream` extends `DataOutputStream` and implements `Syncable`, `CanSetDropBehind`, and `StreamCapabilities`. It tracks position, wraps a stream with optional `FileSystem.Statistics`, supports `hflush`, `hsync`, `setDropBehind`, close, and capability queries.
- `FSDataOutputStreamBuilder<B,S>` is an abstract fluent builder bound to a `FileSystem` and `Path`. It captures permission, buffer size, replication, block size, recursive parent creation, progress callback, `CreateFlag`s, checksum options, optional config keys, mandatory config keys, and ends at abstract `build()`.

### FileSystem Data Models and Path APIs

- `FSError` represents unexpected filesystem errors presumed to reflect disk errors.
- `FSInputStream` is the older seekable positioned-readable base stream. It declares `seek`, `getPos`, `seekToNewSource`, positional `read`, argument validation, and `readFully` helpers.
- `FsServerDefaults` carries server-provided defaults: block size, bytes per checksum, write packet size, replication, file buffer size, data-transfer encryption, trash interval, checksum type, key provider URI, and default storage policy id.
- `FsStatus` implements `Writable` for capacity, used, and remaining bytes on a filesystem.
- `GlobalStorageStatistics` is a singleton-like enum registry with synchronized `get`, `put`, `reset`, and `iterator` methods for named `StorageStatistics` providers.
- `StorageStatistics` is an abstract per-`FileSystem`/`FileContext` statistics object with a name, optional scheme, long-stat iterator, lookup by key, tracking check, and reset hook.
- `GlobFilter` implements `PathFilter` for POSIX glob patterns with brace expansion and optional user filter composition.
- `InvalidPathException`, `InvalidPathHandleException`, `ParentNotDirectoryException`, `UnsupportedFileSystemException`, and `UnsupportedMultipartUploaderException` encode specific path, handle, directory-parent, filesystem-scheme, and multipart-uploader failures.
- `LocatedFileStatus` extends `FileStatus` with block locations, constructors covering ACL/encryption/erasure-coded flags or `FileStatus.AttrFlags`, lazy protected `setBlockLocations`, and equality/hash/compare behavior inherited around path identity.
- `Path` implements `Comparable`, `Serializable`, and `ObjectInputValidation`. It can be built from parent/child strings or paths, URI, or scheme/authority/path components, and exposes URI conversion, filesystem resolution, absolute/root/name/parent/suffix/depth queries, path merging, Windows absolute-path detection, qualification, equality/hash/compare, and deserialization validation.
- `PathFilter.accept(Path)` is the generic filtering hook used by globbing and list operations.
- `PathHandle`, `PartHandle`, and `UploadHandle` are opaque serializable references backed by `ByteBuffer` bytes plus default `toByteArray()` serialization; they represent path entities, multipart part IDs, and multipart upload IDs respectively.
- `PositionedReadable` defines thread-safe positional read methods that must not change the stream offset, while warning that not all filesystems meet that contract.
- `Seekable` defines `seek(long)` and `getPos()` for streams.
- `QuotaUsage` stores file/directory counts, namespace quota, space consumed/quota, storage-type quota and consumption, type-quota availability checks, equality/hash, and formatted quota output headers/strings.
- `ReadOption` is an enum for filesystem read options.
- `StorageType` is an enum of supported storage media with helpers for transient, movable, quota-supporting, list, parse-by-index/string, `DEFAULT`, and `EMPTY_ARRAY`.
- `XAttrCodec` encodes and decodes extended-attribute byte values as text, hex (`0x`), or base64 (`0s`) strings for display and command/HTTP input.
- `XAttrSetFlag.validate(String, boolean, EnumSet)` validates create/replace xattr semantics against whether the target xattr already exists.

### Local and FTP File Systems

- `LocalFileSystem` extends `ChecksumFileSystem`, exposes the `file` scheme, wraps a raw local filesystem, converts `Path` to `File`, copies to/from local paths, reports checksum failures by moving bad files aside on the same device, and supports local symlink operations.
- `RawLocalFileSystem` extends `FileSystem` and implements direct host-filesystem operations: URI/init, path conversion, `PathHandle` open, create/append, output-stream creation with modes and permissions, non-recursive create, concat, rename, Windows empty-directory rename handling, truncate, recursive delete, unsorted listing via Java `File`, directory creation, working directory/home, status, local-output staging, close, file status, owner/permission/time changes via host commands, symlink operations, and path capabilities.
- `FTPException` wraps FTP errors as runtime exceptions.
- `FTPFileSystem` extends `FileSystem` for the `ftp` scheme. It supports default-port lookup, URI/init, open, create, delete, list, file status, mkdirs, rename, and working-directory/home behavior. Append is explicitly documented as unsupported, and a stream returned from `create` must be closed before other APIs are used or subsequent calls may block.
- FTP public constants include logging, default buffer/block sizes, configuration prefixes for user/password/host/port/data connection mode/transfer mode, and an error string requiring same-directory operations.

### Capabilities, Sync, and Trash

- `StreamCapabilities.hasCapability(String)` lets streams advertise lower-case capability strings. Public constants cover `hflush`, `hsync`, `in:readahead`, `dropbehind`, and `unbuffer` behavior by reference to the corresponding interfaces.
- `StreamCapabilitiesPolicy.unbuffer(InputStream)` implements the standard policy for invoking `CanUnbuffer.unbuffer()` and exposes a message for unsupported unbuffer implementations.
- `Syncable.hflush()` makes written bytes visible to new readers; `Syncable.hsync()` is a stronger POSIX-like flush toward disk.
- `Trash` is a configured facade over pluggable `TrashPolicy` implementations. It can choose the correct trash volume for symlinks or mount points, move paths to trash, create checkpoints, expunge old checkpoints, immediately empty trash, return an emptier runnable, and resolve the current trash directory for a path.
- `TrashPolicy` is the abstract extension point for trash behavior. It has old and new initialization signatures, enabled checks, move/checkpoint/delete/empty operations, current-trash-directory APIs, an emptier runnable, factory methods based on `fs.trash.classname`, and protected state for `fs`, `trash`, and `deletionInterval`. The newer APIs avoid assuming trash always lives under `/user/$USER`, which matters for HDFS encryption zones.

### High Availability APIs

- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` represent invalid fencing configuration, failed failover, failed health checks, and failed state transitions.
- `FenceMethod` lets operators plug in vendor/device-specific fencing. It validates configured arguments with `checkArgs(String)` and attempts fencing with `tryFence(HAServiceTarget, String)`, returning success/failure while allowing runtime configuration failures.
- `HAServiceProtocol` defines health monitoring, transitions to active/standby/observer, service status retrieval, access-control and I/O exceptions, and public `versionID`.
- `HAServiceProtocolHelper` wraps static calls to the protocol and unwraps remote exceptions into specific exception types for `monitorHealth`, `transitionToActive`, `transitionToStandby`, and `transitionToObserver`.
- `HAServiceTarget` represents the target used by client-side HA admin commands. It supplies the service IPC address, optional health-monitor address, ZKFC address, fencer, fencing preflight check, service/health/ZKFC proxies, transition-target state, fencing parameters for scripts, auto-failover flag, and observer-state support flag.
- `HAServiceProtocolPB` and `ZKFCProtocolPB` are protobuf RPC bridge interfaces extending generated blocking interfaces plus `VersionedProtocol`.

### Hadoop IO Types

- `AbstractMapWritable` implements `Writable` and `Configurable`. It maintains per-instance class-to-id and id-to-class metadata for `MapWritable`/`SortedMapWritable`, with class IDs in the range 1 through 127, synchronized add/copy hooks, configuration accessors, and `write`/`readFields`.
- `ArrayFile` extends `MapFile` and is documented as a dense file-based mapping from integers to values.
- `ArrayPrimitiveWritable` wraps primitive arrays in a `Writable` without per-element object allocation and without copying the underlying array. It supports declared component-type constructors, `get`, component-type queries, `set`, and serialization hooks.
- `ArrayWritable` stores arrays of same-class `Writable` elements, exposes the value class, conversion to strings/object arrays, set/get, and `Writable` serialization. Its Javadoc recommends subclassing for reducer input types.
- `BinaryComparable` is an abstract byte-sequence comparable requiring `getLength()` and `getBytes()`, with byte-wise compare overloads, equality, and hash semantics tied to `WritableComparator.compareBytes/hashBytes`.
- `BloomMapFile` extends `MapFile`, declares bloom metadata constants, and exposes static `delete(FileSystem, String)` for deleting a bloom map file.
- `BooleanWritable`, `ByteWritable`, and `BytesWritable` implement `WritableComparable` semantics for boolean, byte, and resizable byte-sequence values. They expose mutable setters/getters, `readFields`/`write`, equality/hash/compare, and string rendering.
- `ByteBufferPool` allocates or reuses `ByteBuffer` instances with `getBuffer(boolean direct, int length)` and returns them through `putBuffer(ByteBuffer)`. The Javadoc says returned capacity may exceed the request but must be at least one byte.
- `org.apache.hadoop.io.Closeable` is a deprecated alias extending `java.io.Closeable`.
- `CompressedWritable` is an abstract `Writable` base whose final `readFields` and `write` methods store data compressed and lazily inflate it. Subclasses implement protected `readFieldsCompressed` and `writeCompressed`; field accessors must call `ensureInflated()`.
- `DataOutputOutputStream` adapts any `DataOutput` to an `OutputStream`, returning the original object when it already implements `OutputStream`, otherwise wrapping writes through `DataOutput`.
- The visible start of `DefaultStringifier` shows it implements `Stringifier`, has a `(Configuration, Class)` constructor, and exposes `fromString(String)` plus the beginning of `toString(T)`, both throwing `IOException`.

## Control Flow

This XML has no executable control flow, but the documented APIs imply key runtime paths:

- File utility writes open/create the destination through `FileSystem` or `FileContext`, overwrite existing content, write the supplied bytes/text, then return the same handle for fluent use or caller confirmation.
- Manifest-jar creation receives a classpath, resolves environment variables using platform-specific syntax, expands terminal jar wildcards, writes a manifest jar in the chosen working/target directory context, and returns the generated jar path plus wildcard metadata.
- `FilterFileSystem` normal control flow is delegation: public `FileSystem` calls enter the wrapper, path/URI scheme adjustments may be applied, and the contained `fs` performs the real operation. Subclasses alter behavior by overriding selected methods while inheriting pass-through behavior for the rest.
- Stream reads use `FSDataInputStream` to dispatch seek, positional read, byte-buffer read, zero-copy read, cache hint, unbuffer, and capability operations to the wrapped stream if it supports the needed interface. `PositionedReadable` calls are expected not to mutate current stream offset.
- Stream writes use `FSDataOutputStream` to track current position, pass data to the wrapped stream, update statistics, and delegate `hflush`/`hsync`/drop-behind/capability calls when supported.
- `FSDataOutputStreamBuilder` accumulates create/append state through fluent setters, stores optional and mandatory keys in its internal options configuration, and finally calls `build()` in a concrete subclass. Mandatory keys create an integration contract: downstream filesystem implementations should fail or reject unknown mandatory options rather than silently ignore them.
- `Path` construction normalizes URI-like path strings, parent/child combinations, or URI components; later calls convert to URI, resolve the owning `FileSystem` via `Configuration`, qualify relative paths, and validate deserialized state before use.
- Local filesystem operations translate Hadoop `Path` values to Java `File` values, then call host filesystem primitives or shell commands for permissions/ownership/timestamps. `LocalFileSystem` layers checksum handling over `RawLocalFileSystem`; raw local operations bypass checksum sidecar behavior.
- Trash deletion flow resolves the correct filesystem/volume for the path being deleted, checks whether trash is enabled or the item is already in trash, renames into a current trash directory, and later checkpoint/expunge operations rotate or delete trash checkpoints. The policy API allows encryption-zone-aware trash locations.
- FTP flow initializes connection information from URI/configuration, then performs remote open/create/delete/list/status/mkdir/rename operations. Its create-stream rule serializes interaction: callers must close the stream before invoking other methods to avoid blocking.
- HA management flow has health monitors call `monitorHealth()` and `getServiceStatus()`, admin/failover logic call transition methods with `StateChangeRequestInfo`, and fencing logic check and try configured `FenceMethod` implementations in order through a `HAServiceTarget`.
- `HAServiceTarget` proxy methods choose the main address or optional health-monitor address, while fencing parameter generation exposes target metadata to script-style fencers by environment variable naming conventions.
- `Writable` flow in `org.apache.hadoop.io` is the standard `write(DataOutput)`/`readFields(DataInput)` round trip. Map/array/binary/writable values mutate in memory through setters and persist themselves to Hadoop binary streams when asked.
- `CompressedWritable` flow is intentionally lazy: `readFields` stores compressed bytes, field readers call `ensureInflated`, inflation invokes subclass `readFieldsCompressed`, and `write` invokes subclass `writeCompressed` while preserving the compressed-copy optimization for large objects.

## State and Persistence Behavior

The JDiff XML persists release API metadata for compatibility checking. It does not itself store Hadoop runtime data.

`FileUtil` methods mutate the host or target filesystem: `replaceFile` changes directory entries; listing helpers observe filesystem state; manifest-jar creation creates a local jar; write helpers create or overwrite files. These operations are durable at the target filesystem unless the underlying implementation is ephemeral or fails partway through.

`FilterFileSystem` stores protected mutable wrapper state: the delegate `FileSystem` and optional scheme swap. Its persistence behavior is inherited from the delegate; the wrapper itself is process-local.

`FSDataInputStream` and `FSInputStream` maintain stream cursor state, while positioned-read APIs promise not to alter that cursor. `FSDataOutputStream` maintains write position and potentially updates `FileSystem.Statistics`. `hflush` and `hsync` have different durability/visibility semantics: `hflush` is about reader visibility, while `hsync` pushes data closer to disk persistence.

`FSDataOutputStreamBuilder` stores pending creation state in memory until `build()`: target filesystem/path, permission, buffer size, replication, block size, recursive flag, progress callback, flags, checksum options, optional options, and mandatory option keys.

`FsServerDefaults`, `FsStatus`, `LocatedFileStatus`, `QuotaUsage`, `Path`, storage type values, xattr codec values, and handle interfaces are data carriers. Some are serializable or `Writable`; compatibility depends on preserving serialized forms and semantic equality, especially for `Path`, `PathHandle`, `PartHandle`, `UploadHandle`, and status/quota objects.

`RawLocalFileSystem` and `LocalFileSystem` persist changes directly in the local filesystem. Important durable effects include create/append/truncate/delete/rename, directory creation, owner/group/permission changes, timestamps, symlink creation, checksum-bad-file relocation, and local-output staging completion.

`Trash` and `TrashPolicy` persist soft deletions as filesystem renames into trash directories and later checkpoint directories. `deletionInterval` controls expiration behavior; current trash location may vary by source path for encryption-zone compatibility.

`FTPFileSystem` persists changes on the remote FTP server. State also includes process-local connection/session behavior, working directory, and configuration-derived credentials/host/transfer-mode settings.

HA APIs represent distributed service state rather than direct storage. Transition methods can change the active/standby/observer role of a service. Fencing methods can have severe external side effects such as killing processes, revoking storage access, or power control. `HAServiceTarget` fencing parameters are transient data passed to fencers or scripts.

`AbstractMapWritable` persists a per-instance class-id map alongside contents so nested or varied writable maps can deserialize class metadata without static global maps. `ArrayPrimitiveWritable`, `ArrayWritable`, `BooleanWritable`, `ByteWritable`, `BytesWritable`, `FsStatus`, and `CompressedWritable` all persist through `DataOutput`/`DataInput`. `BytesWritable` distinguishes logical length from backing capacity; callers using `getBytes()` observe the backing array and must respect `getLength()`.

`ByteBufferPool` owns process-local reusable buffers; returning buffers controls memory reuse but is not durable. `DataOutputOutputStream` stores no durable state beyond forwarding writes to the wrapped `DataOutput`.

## Dependencies and Integration Points

This chunk depends heavily on Java standard APIs: `java.io.File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `FileDescriptor`, checked I/O exceptions, URI, `ByteBuffer`, collections, `EnumSet`, `InetSocketAddress`, and serialization interfaces.

Key Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configured` for filesystem initialization, trash policy selection, FTP setup, output builder options, HA proxy creation, and IO stringification setup.
- `org.apache.hadoop.fs.FileSystem`, `FileContext`, `FileStatus`, `BlockLocation`, `Path`, `FsPermission`, `AclStatus`, `CreateFlag`, `Options.ChecksumOpt`, `Options.HandleOpt`, and `BlockStoragePolicySpi` as the central filesystem contracts.
- `org.apache.hadoop.util.Progressable` for create/write progress callbacks.
- Stream capability interfaces such as `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `CanUnbuffer`, `StreamCapabilities`, and `Syncable`.
- `org.apache.hadoop.io.Writable`, `WritableComparable`, `WritableComparator`, `ByteBufferPool`, `MapFile`, and `Stringifier` for Hadoop binary serialization and comparison.
- HDFS and distributed-filesystem features surfaced through generic `FileSystem` APIs: snapshots, ACLs, xattrs, encryption-zone-aware trash, erasure-coded file status flags, storage policies, storage type quotas, and path handles.
- FTP integration through Apache Commons Net and SLF4J logging.
- HA integration with `AccessControlException`, `NodeFencer`, `ZKFCProtocol`, `HAServiceStatus`, generated protobuf service interfaces, and Hadoop IPC `VersionedProtocol`.
- The `hadoop.http.filter.initializers` configuration key documented by the `org.apache.hadoop.http.lib` package note.

## Risks and Edge Cases

- The chunk begins mid-`FileUtil`; earlier methods and fields are not visible here. It also ends mid-`DefaultStringifier`; later methods and docs must come from the next chunk.
- JDiff shows API signatures and documentation, not implementations. Exact exception ordering, validation behavior, concurrency, resource cleanup, stream wrapping, and remote call details require implementation-source validation.
- `FileUtil.list` and `listFiles` intentionally convert ambiguous Java `null` results into exceptions. Callers migrating from raw Java APIs must handle checked `IOException` and access-denied cases.
- Manifest classpath jar creation is platform-sensitive: environment variable syntax differs between Windows and non-Windows platforms, Windows variables are case-insensitive, and wildcard expansion only covers `.jar`/`.JAR` entries.
- Whole-file `FileUtil.write` helpers overwrite existing files. They are convenient but risky for callers expecting append, atomic replace, or partial-write rollback.
- `FilterFileSystem` inherits the delegate's semantics. Subclasses that override only some methods can accidentally leak unsupported behavior, wrong scheme/authority, or inconsistent capability reporting through inherited pass-through methods.
- `PositionedReadable` documents thread-safety as required but also warns not all implementations satisfy it. Consumers such as HBase-style random readers should verify the concrete filesystem.
- `FSDataInputStream` enhanced byte-buffer access requires correct buffer release. Missing `releaseBuffer` calls can leak pooled or direct buffers.
- `StreamCapabilities` uses lower-case strings instead of enums. Typos or unrecognized capability names silently depend on implementation policy.
- `hflush` and `hsync` are often confused. Tests and callers need to distinguish reader visibility from stronger sync semantics.
- `Path` accepts URI-like strings with normalization and Windows-specific absolute path handling. Edge cases include drive letters, authority-less absolute paths, root paths with no parent, deserialization attacks, and deprecated `makeQualified(FileSystem)`.
- `LocatedFileStatus` equality/hash are path-based, so changes in block locations, ACL/encryption/erasure flags, or metadata do not necessarily affect equality.
- `RawLocalFileSystem.listStatus` notes that ordering is not guaranteed because it relies on Java `File.list()`.
- `RawLocalFileSystem` owner/permission/time updates depend on host commands or platform capabilities, creating portability and permission risks.
- `LocalFileSystem.reportChecksumFailure` moves files aside on the same device; failure to move should not be confused with successful quarantine.
- FTP append is unsupported, create streams can block other APIs until closed, and remote FTP operations often have weaker atomicity and consistency than HDFS/local operations.
- Trash behavior is rename-based and may fail across volumes or encryption zones unless the path-aware trash directory APIs are used.
- `TrashPolicy.initialize(conf, fs, home)` is deprecated because it assumes a home-based trash location; implementations should prefer the two-argument initialization plus path-aware current-trash lookup.
- HA fencing can be destructive by design. Bad fencing parameters or script environment generation can kill the wrong process or affect the wrong node.
- `HAServiceTarget.getHealthMonitorAddress()` may route monitoring to a separate lifeline RPC server; failover tests must cover both null and non-null cases.
- `AbstractMapWritable` supports at most 127 distinct classes per map instance. Large heterogeneous maps can exceed the id range.
- `ArrayPrimitiveWritable` does not copy the underlying array. External mutation after wrapping can change serialized output.
- `BytesWritable.getBytes()` exposes backing capacity, not just logical contents. Callers must use `copyBytes()` when they need an exact-length immutable-ish copy.
- `CompressedWritable` requires all field accessors in subclasses to call `ensureInflated()`. Forgetting this creates stale/uninitialized field reads.
- `org.apache.hadoop.io.Closeable` remains as a deprecated compatibility alias and should not be removed even though `java.io.Closeable` is preferred.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks that all public/protected methods, fields, deprecation markers, abstract/final/static/synchronized attributes, and checked exceptions in this chunk remain stable for Hadoop Common 3.2.2 compatibility.
- `FileUtil` tests for replacing files, invalid/unreadable directory listing exceptions, empty-list behavior, classpath manifest jar generation, environment expansion, wildcard jar expansion, filesystem comparison, and overwrite semantics for byte/text writes through both `FileSystem` and `FileContext`.
- `FilterFileSystem` tests with a tracing delegate to prove calls forward correctly, preserve exceptions, expose raw filesystem, handle URI/scheme qualification, close the delegate, and report capabilities from the wrapped filesystem.
- Stream tests for `FSDataInputStream` seek/getPos, positional reads not changing offset, `readFully` EOF behavior, byte-buffer read/release, readahead/drop-behind unsupported behavior, unbuffer policy, file descriptor availability, and `hasCapability` string handling.
- Stream output tests for `FSDataOutputStream` position accounting, statistics updates, close delegation, `hflush`/`hsync` propagation, drop-behind handling, and capability reporting.
- Builder tests for every fluent setter, create/overwrite/append flags, recursive parent behavior, checksum options, optional versus mandatory option propagation, and concrete `build()` failure on unknown mandatory keys.
- `Path` tests for constructor variants, URI conversion, parent/name/root/depth/suffix behavior, Windows absolute path detection, `mergePaths`, deprecated and current qualification, filesystem resolution through `Configuration`, equality/hash/compare, and `validateObject` rejecting invalid deserialized state.
- Local filesystem tests for raw versus checksumed behavior, path-to-file conversion, create/append/truncate/delete/rename, Windows rename edge cases, unsorted listing tolerance, mkdirs idempotence, working directory behavior, status/capacity, permission/owner/time updates, symlink support, path handles, and checksum-failure quarantine.
- Status/quota/statistics tests for `FsStatus` writable round trips, `FsServerDefaults` constructor/getter coverage, `LocatedFileStatus` block location and attr flag behavior, `QuotaUsage` type quotas and formatted headers, `StorageStatistics` lookup/reset behavior, and global statistics registry synchronization.
- `GlobFilter` tests for POSIX glob syntax, brace expansion, invalid pattern exceptions, and composition with a user `PathFilter`.
- Handle tests for `PathHandle`, `PartHandle`, and `UploadHandle` byte-buffer and byte-array serialization plus equality semantics.
- XAttr tests for text/hex/base64 encode/decode, invalid encodings, quoted text handling, and `XAttrSetFlag.validate` create/replace combinations.
- Trash tests for disabled trash, already-in-trash behavior, path-aware trash root resolution, encryption-zone-aware trash directory behavior, checkpoint creation, expunge, immediate emptying, and factory selection through `fs.trash.classname`.
- FTP tests with a controlled FTP server for initialization from URI/config, open/create close discipline, append unsupported errors, delete/list/status/mkdir/rename, working directory/home behavior, and credentials/port/transfer-mode config keys.
- HA tests for fencing argument validation, ordered fencing success/failure, script parameter map generation, health monitor address fallback, proxy creation, transition methods, observer support flag, auto-failover flag, exception unwrapping in `HAServiceProtocolHelper`, and protobuf bridge compatibility.
- IO serialization tests for `AbstractMapWritable` class-id persistence and 127-class limit, primitive array writable no-copy behavior, `ArrayWritable` homogeneous element round trips, `BinaryComparable` ordering/hash consistency, `BooleanWritable`/`ByteWritable`/`BytesWritable` comparison and writable round trips, byte buffer pool direct/non-direct allocation and return, `CompressedWritable` lazy inflation, and `DataOutputOutputStream` wrapping/non-wrapping cases.

## Cross-Chunk Notes

The previous chunk is required to complete `org.apache.hadoop.fs.FileUtil`, because this range starts after the `createLocalTempFile` method documentation has already begun. The next chunk is required to complete `org.apache.hadoop.io.DefaultStringifier`, because this range stops at the opening metadata for `toString(T)`.

### subset-b-007195: lines 18159-24459

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.2.xml lines 18159-24459

## Scope

This chunk is generated JDiff API metadata for Apache Hadoop Common 3.2.2. It starts inside the tail of `org.apache.hadoop.io.DefaultStringifier`, then covers a large part of the public `org.apache.hadoop.io` API, the visible `org.apache.hadoop.io.compress` package, `org.apache.hadoop.io.erasurecode.ECSchema`, empty erasure-code subpackages, and the beginning of `org.apache.hadoop.io.file.tfile` through `Utils.upperBound`.

The source is not implementation code. The research surface is the compatibility contract captured by the XML: public/protected type names, inheritance, implemented interfaces, method signatures, constructors, exceptions, fields, static/final/synchronized markers, deprecation status, and embedded Javadoc. Runtime behavior below is inferred from the API contracts and docs in this slice.

## Purpose

The `org.apache.hadoop.io` section defines Hadoop's core serialization and binary data model. `Writable` and `WritableComparable` are the central serialization contracts used by RPC, MapReduce keys and values, sequence files, map files, and many filesystem-side metadata types. Primitive wrappers such as `IntWritable`, `LongWritable`, `FloatWritable`, `DoubleWritable`, `ShortWritable`, `VIntWritable`, and `VLongWritable` make primitive values serializable, comparable, and usable as Hadoop keys.

The same package also provides higher-level serialization helpers and containers. `Text` is Hadoop's mutable UTF-8 byte-string type. `ObjectWritable`, `GenericWritable`, `MapWritable`, `SortedMapWritable`, `EnumSetWritable`, `TwoDArrayWritable`, and `NullWritable` support polymorphic, collection, enum-set, matrix, and sentinel-value serialization. `WritableComparator`, `WritableFactories`, and `WritableUtils` provide comparator registration, reflective/factory construction, byte-level comparison, compressed string/byte helpers, variable-length integer encoding, enum encoding, and clone/copy helpers.

The file-oriented APIs in this chunk expose legacy Hadoop binary file formats. `SequenceFile` is the flat binary key/value container with record, block, and no-compression modes and sync points. `MapFile` layers an indexed sorted map directory over sequence files, and `SetFile` specializes that pattern for keys only.

The `org.apache.hadoop.io.compress` section defines Hadoop's codec abstraction and stream model. `CompressionCodec`, `Compressor`, `Decompressor`, `CompressionInputStream`, `CompressionOutputStream`, `CompressorStream`, `DecompressorStream`, block stream variants, concrete default/gzip/bzip2 codecs, split-compression support, direct `ByteBuffer` decompression, codec discovery by filename/class/name, and `CodecPool` reuse are the public integration points for compressed input and output.

The erasure-code and TFile sections expose smaller contracts. `ECSchema` is a value object describing codec name, data/parity unit counts, and extra codec options. TFile APIs describe a block-compressed byte key/value container with named metadata blocks, sorted/unsorted modes, seek support, raw byte comparators, compression constants, and utility encodings.

## Important APIs, Types, and Functions

### Stringification and Primitive Writables

- `DefaultStringifier<T>` tail includes `toString(T)`, `fromString(String)`, `close()`, and static `store`, `load`, `storeArray`, and `loadArray` helpers. The docs say values are serialized through Hadoop `Serialization` implementations, base64 encoded, and stored in `Configuration` keys.
- `Stringifier<T>` defines the generic object/string conversion lifecycle: `toString(T)`, `fromString(String)`, and `close()`, all capable of forwarding `IOException`.
- `DoubleWritable`, `FloatWritable`, `IntWritable`, `LongWritable`, and `ShortWritable` implement `WritableComparable` with default and value constructors, `set`, `get`, `readFields(DataInput)`, `write(DataOutput)`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `VIntWritable` and `VLongWritable` mirror the fixed-width integer wrappers but persist values in Hadoop's variable-length integer format.
- `NullWritable` is a singleton `WritableComparable` with no serialized payload. `get()` returns the single instance, and `readFields`/`write` are no-op style hooks for APIs that require a writable key or value type.
- `MD5Hash` is a `WritableComparable` wrapper around a 16-byte digest. It can be constructed empty, from a hex string, or from bytes; it can digest byte arrays, strings, input streams, and arrays of byte arrays; it exposes `halfDigest`, `quarterDigest`, `setDigest`, `getDigest`, `read`, `write`, comparison, and string conversion.

### Writable Containers and Polymorphism

- `Writable` is the base contract: `write(DataOutput)` serializes fields, and `readFields(DataInput)` deserializes them in the same order. The docs emphasize compact, efficient binary serialization.
- `WritableComparable<T>` combines `Writable` with `Comparable<T>` for sortable key types.
- `GenericWritable` is an abstract wrapper for one of a fixed set of writable classes. Subclasses must implement protected `getTypes()` to return the allowed class array; the wrapper carries the selected instance and implements `Configurable`.
- `ObjectWritable` is a polymorphic writable for a `Writable`, `String`, primitive, primitive wrapper, enum, array, or null. It records the declared class, exposes static `writeObject` and `readObject` helpers with optional declared-class and configuration parameters, and has `loadClass(Configuration, String)` for class resolution.
- `MapWritable` extends `AbstractMapWritable` and implements `Map<Writable, Writable>` behavior with `clear`, membership checks, key/value/entry views, `put`, `putAll`, `remove`, `size`, `isEmpty`, `equals`, `hashCode`, `toString`, and explicit `write`/`readFields`.
- `SortedMapWritable` extends `AbstractMapWritable` and exposes `SortedMap` operations such as `comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, and `tailMap`, plus the same writable map serialization surface.
- `EnumSetWritable<E extends Enum<E>>` wraps an `EnumSet`, implements `Writable` and `Configurable`, and preserves `elementType` when the set is null or empty. Constructors and `set(EnumSet, Class)` require an element type for null/empty values.
- `TwoDArrayWritable` stores a two-dimensional array of writable instances for a configured value class and exposes `toArray`, `set`, `get`, `write`, and `readFields`.
- `VersionedWritable` writes and reads a version byte around subclass state and throws `VersionMismatchException` when serialized data does not match the current implementation version.
- `MultipleIOException` wraps a list of `IOException` instances and has `createIOException(List)` to return either a single exception or a combined one.

### IO Utilities, Comparators, and Factories

- `IOUtils` provides stream and channel helpers: `copyBytes` overloads for `InputStream`/`OutputStream` and `Configuration`, bounded copies, `readFully`, `skipFully`, `wrappedReadForCompressedData`, `cleanup`, `cleanupWithLogger`, close helpers for streams/sockets, `writeFully` for `WritableByteChannel` and positioned `FileChannel`, `listDirectory`, `fsync(FileChannel, boolean)`, `fsync(File)`, `wrapException`, and `readFullyToByteArray`.
- `ElasticByteBufferPool` implements `ByteBufferPool` with synchronized `getBuffer(boolean direct, int length)` and `putBuffer(ByteBuffer)`. Its docs state it creates buffers as needed, caches returned buffers, returns the smallest cached buffer large enough for a request, and does not enforce a maximum cache size.
- `WritableComparator` is the central raw comparator implementation for writable keys. It can be obtained with `get(Class)` or `get(Class, Configuration)`, configured, registered via `define(Class, WritableComparator)`, instantiate keys with `newKey`, compare objects or serialized byte ranges, compare/hash raw bytes, and parse primitive or vint/vlong values from byte arrays.
- `RawComparator<T>` adds binary `compare(byte[], int, int, byte[], int, int)` to normal object comparison so sorting code can compare serialized key bytes without object allocation.
- `WritableFactories` maintains class-to-`WritableFactory` registrations and constructs new writable instances with or without a `Configuration`. This supports non-public writable classes and avoids assuming every type has a public no-arg constructor.
- `WritableUtils` supplies compressed byte-array/string helpers, string and string-array serialization, byte-array display, `clone` and `cloneInto` by serializing through buffers, vint/vlong read/write and size helpers, enum read/write by name, `skipFully`, `toByteArray(Writable[])`, and `readStringSafely(DataInput, int)` with maximum encoded-length validation.

### SequenceFile, MapFile, and Text

- `SequenceFile` has public static helpers to get/set default compression type and many `createWriter` overloads. The overloads support writer option objects, filesystem/path-based creation, replication, block size, progress callbacks, metadata, compression type, codec, raw key/value classes, and stream-based writers.
- `SequenceFile.SYNC_INTERVAL` is the documented default byte distance between sync points. The class docs describe sequence files as flat binary key/value files with record compression, block compression, sync markers for seeking/splitting, metadata, and append/read/write patterns.
- `MapFile` exposes static `rename(FileSystem, String, String)`, `delete(FileSystem, String)`, `fix(FileSystem, Path, Class, Class, boolean, Configuration)`, and `main(String[])`, plus public `INDEX_FILE_NAME` and `DATA_FILE_NAME`. Its docs define it as a file-based map from keys to values backed by a data file and an index file.
- `SetFile` extends `MapFile` and represents a file-based set of keys.
- `Text` extends `BinaryComparable` and stores UTF-8 bytes. It has constructors from empty, `String`, `Text`, and `byte[]`; raw and copied byte accessors; length and code-point access; substring search; several `set` overloads; `append`; `clear`; string conversion; `readFields`, `readFields(DataInput, int)`, `skip`, `readWithKnownLength`; `write` overloads with optional max length; equality/hash; UTF-8 `decode` and `encode`; static string read/write helpers with maximum sizes; UTF-8 validation; `bytesToCodePoint`; `utf8Length`; and `DEFAULT_MAX_LEN`.

### Compression APIs

- `CompressionCodec` is the main codec contract. It creates `CompressionOutputStream` and `CompressionInputStream` instances with optional pooled `Compressor`/`Decompressor`, returns compressor/decompressor classes, creates compressor/decompressor objects, and exposes a default filename extension.
- `DefaultCodec`, `GzipCodec`, and `BZip2Codec` are concrete configurable codecs. `DefaultCodec` also implements `DirectDecompressionCodec`; `GzipCodec` extends `DefaultCodec`; `BZip2Codec` supports `SplittableCompressionCodec` by creating a `SplitCompressionInputStream` for a compressed byte range and read mode.
- `CodecConstants` provides public filename extension constants for default, bzip2, gzip, lz4, snappy, and zstandard codecs.
- `CompressionCodecFactory` discovers codecs from `io.compression.codecs`, Java `ServiceLoader`, and the configuration. It can list codec classes, set codec classes, find a codec by `Path`, class name, short name, or class object, remove suffixes, print its extension map, and run a small `main`.
- `CodecPool` is a global compressor/decompressor reuse pool. It leases compressors/decompressors for a codec, accepts them back with return methods, and exposes leased compressor/decompressor counts.
- `Compressor` and `Decompressor` are stream-state interfaces. They accept input buffers and optional dictionaries, report whether more input or dictionaries are needed, report bytes read/written or remaining bytes, finish/finished state, compress/decompress into caller buffers, reset for reuse, end resources, and in the compressor case `reinit(Configuration)`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases with protected underlying `in`/`out`, `close`, byte read/write hooks, `finish`, `flush`, `resetState`, and positional methods. `CompressionInputStream.seek` and `seekToNewSource` are documented as unsupported in this base class.
- `CompressorStream` and `DecompressorStream` bind a stream to a `Compressor` or `Decompressor`, maintain a byte buffer and closed/eof state, and implement write/read, compress/decompress loops, reset, skip/available, mark/reset behavior, and close.
- `BlockCompressorStream` and `BlockDecompressorStream` specialize the stream wrappers for block-oriented compressed payloads, including block-size and compression-overhead constructors, `compress`, `decompress`, `getCompressedData`, and state reset.
- `DirectDecompressionCodec` creates a `DirectDecompressor`; `DirectDecompressor.decompress(ByteBuffer, ByteBuffer)` defines direct buffer decompression without copying through byte arrays.
- `SplitCompressionInputStream` stores adjusted start/end positions for a compressed split. `SplittableCompressionCodec` creates such streams using a `READ_MODE` enum, start, and end offsets.

### Erasure Coding and TFile

- `ECSchema` stores erasure-code schema information. Constructors accept an options map or explicit codec name, data units, parity units, and extra options. Public fields name the canonical option keys: `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`. Accessors expose codec name, extra options, data units, parity units, string representation, equality, and hash code.
- `org.apache.hadoop.io.erasurecode.coder.util` and `org.apache.hadoop.io.erasurecode.grouper` appear as empty packages in this XML slice.
- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are checked TFile metadata block exceptions, both extending `IOException`.
- `org.apache.hadoop.io.file.tfile.RawComparable` exposes `buffer()`, `offset()`, and `size()` so external raw comparators can compare a byte range without wrapping or copying.
- `TFile` exposes comparator and format constants: `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, `COMPARATOR_MEMCMP`, and `COMPARATOR_JCLASS`. Static methods include `makeComparator(String)`, `getSupportedCompressionAlgorithms()`, and `main(String[])` for dumping TFile information.
- `TFile` docs define a byte key/value container with block compression, named metadata blocks, sorted or unsorted keys, seek by key or file offset, configurable chunk size and filesystem buffer sizes, and memory usage driven by block and metadata indexes.
- `org.apache.hadoop.io.file.tfile.Utils` provides an alternate TFile-specific variable-length integer encoding, string read/write in Text format, and generic `lowerBound`/`upperBound` binary-search helpers over lists with caller-supplied comparators.

## Control Flow

The XML has no executable flow, but the APIs imply several important runtime paths.

Writable serialization flows are symmetric. A writer calls `write(DataOutput)` in a type-specific order; the reader constructs an instance through a no-arg constructor, `WritableFactories`, `ObjectWritable`, or a containing type, then calls `readFields(DataInput)` in the same order. Comparability is layered on top through object `compareTo` or raw byte comparison with `RawComparator`/`WritableComparator`.

Polymorphic serialization writes enough type metadata to rebuild the runtime value. `GenericWritable` restricts that metadata to an allowed class table returned by `getTypes()`. `ObjectWritable` writes declared-class information and then dispatches to special handling for writables, strings, primitive types, arrays, enums, or null values. Read paths use configuration-aware class loading and object construction.

Text and string helper flows are length-prefixed. `Text` and `WritableUtils` read a vint length, validate or bound it where required, then consume UTF-8 bytes. `Text.validateUTF8`, `bytesToCodePoint`, and max-length overloads are the guard rails for malformed or oversized input.

SequenceFile writer construction is option-heavy but converges on creating a writer with configured key/value classes, destination stream/path, compression mode, optional codec, filesystem metadata, replication/block settings, and progress reporting. Record writes produce binary key/value records with periodic sync markers; block-compressed writers batch records into compressed blocks; raw writers accept pre-serialized key/value buffers.

MapFile operation is directory-oriented. A map contains a data sequence file and an index file. `rename` and `delete` operate on that directory layout, and `fix` reconstructs a missing or corrupt index by scanning the data file and writing a new index for the supplied key/value classes.

Compression output flow is: a codec creates or receives a `Compressor`, wraps the destination in a `CompressionOutputStream`, accepts uncompressed bytes, calls the compressor until bytes are emitted, and finalizes with `finish()` before close. Compression input reverses this by feeding compressed bytes into a `Decompressor`, emitting uncompressed bytes until `finished`, `needsInput`, or EOF state is reached. Block streams add block headers and block-level refill/flush boundaries.

Codec pooling flow is lease-and-return. Callers request a compressor/decompressor from `CodecPool`, use it with a codec-created stream, reset or finish the stream, then return the codec object. The leased-count APIs make pool misuse visible in tests and diagnostics.

Codec discovery flow maps configuration and service-loaded codec classes to filename extensions and aliases. `CompressionCodecFactory.getCodec(Path)` chooses by file suffix, while class-name and short-name methods support direct lookup.

Split compression flow is available only for codecs implementing `SplittableCompressionCodec`. The caller provides an input stream, decompressor, start/end byte offsets, and read mode; the returned `SplitCompressionInputStream` may adjust the effective start and end to codec-specific record boundaries.

TFile flow writes byte keys and values into data blocks, optionally compresses each block, maintains a block index and metadata-block index, and supports lookup by key or file offset. Comparator creation selects raw byte comparison either by the built-in memcmp comparator or by a Java comparator class prefix.

## State and Persistence Behavior

This JDiff file persists the Hadoop 3.2.2 API surface for compatibility comparison. It does not persist runtime Hadoop state, but many listed APIs define durable binary formats.

Every `Writable` type has serialized state. Primitive writable state is a single primitive value. VInt/VLong state is encoded using Hadoop's vint/vlong format, so byte compatibility depends on preserving the exact variable-length encoding. `Text` persists a length and UTF-8 bytes, not a Java `String` object. `MD5Hash` persists fixed 16-byte digest state. `NullWritable` persists no data and relies on singleton identity.

Container writables persist both structure and contained values. `MapWritable` and `SortedMapWritable` must persist enough class-id metadata through `AbstractMapWritable` to deserialize heterogeneous writable keys and values. `EnumSetWritable` must preserve the enum element type when the set is null or empty. `TwoDArrayWritable` persists matrix dimensions and each cell's writable state. `VersionedWritable` persists a version byte and rejects mismatches.

`ObjectWritable` and `GenericWritable` persist class identity. This creates compatibility pressure around class renames, classloader behavior, primitive/array encoding, and declared-class versus runtime-class distinctions. `WritableFactories` and `Configurable` hooks make construction depend on process-local registration and configuration rather than only reflection.

SequenceFile, MapFile, SetFile, and TFile define on-disk formats. SequenceFile state includes header metadata, key/value classes, compression type, codec identity, sync markers, and serialized records or blocks. MapFile state is split across data and index files inside a directory. TFile state includes data blocks, optional compression, key/value byte payloads, metadata blocks, and indexes; its docs call out memory cost proportional to block and metadata index counts.

Compression streams carry mutable, non-durable stream state such as input/output buffers, closed/eof booleans, compressor/decompressor objects, byte counters, pending input, dictionaries, and adjusted split bounds. The compressed bytes they produce are durable and must remain readable by the matching codec and format readers.

`CodecPool` has process-global state: available and leased compressor/decompressor instances. Returning objects correctly affects memory, native resource lifetime, and test isolation. `ElasticByteBufferPool` similarly has synchronized in-memory buffer caches with no maximum cache size.

`ECSchema` is an immutable-style value object from the visible API: codec name, data/parity counts, and extra options define durable erasure-coding policy metadata when embedded into higher-level HDFS state.

## Dependencies and Integration Points

These APIs sit on Java core I/O, NIO, reflection, collections, and security primitives: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `FileChannel`, `WritableByteChannel`, `ByteBuffer`, `MessageDigest`, `Comparator`, `Map`, `SortedMap`, `EnumSet`, and exception types.

Hadoop configuration and filesystem integration appears throughout. `DefaultStringifier`, `GenericWritable`, `ObjectWritable`, `WritableComparator`, `WritableFactories`, compression codecs, `CompressionCodecFactory`, `MapFile.fix`, and `SequenceFile.createWriter` depend on `org.apache.hadoop.conf.Configuration`. File-format helpers integrate with `FileSystem`, `Path`, `FSDataInputStream`, `FSDataOutputStream`, replication/block-size settings, progress callbacks, and Hadoop codec configuration.

MapReduce and shuffle integration depends on `WritableComparable`, `RawComparator`, `WritableComparator`, `Text`, primitive writable keys, and `SequenceFile`. Sorting and grouping can compare serialized bytes directly, so raw comparator behavior is a performance and correctness boundary.

Compression integrates with native or Java codec implementations behind the `Compressor` and `Decompressor` interfaces. Extension constants and `CompressionCodecFactory` connect file naming conventions to runtime codec choice. `SplittableCompressionCodec` integrates compressed files with input split planning.

TFile integrates the IO, compression, raw comparison, and utility encoding layers. It accepts compression algorithm names compatible with `TFile.Writer`, uses raw comparators for sorted keys, uses Text-style string encoding in utilities, and uses block indexes for seek behavior.

The JDiff file itself integrates with Hadoop's dev-support compatibility tooling. Changes in this XML are signals for public API additions, removals, signature changes, deprecations, and documentation shifts between Hadoop releases.

## Risks and Edge Cases

Binary compatibility is the main risk. Changing method signatures, constructors, field names, checked exceptions, implemented interfaces, or visibility in these APIs can break downstream Hadoop applications, file readers, RPC clients, MapReduce jobs, or codec plugins compiled against 3.2.2.

Serialization compatibility is more fragile than source compatibility. Reordering `write`/`readFields`, changing vint/vlong encoding, changing Text length checks, modifying ObjectWritable class encoding, or changing MapWritable class-id behavior can make existing files unreadable or produce subtle cross-version failures.

Raw comparators are correctness-critical. A comparator that orders serialized bytes differently from object `compareTo` can corrupt sort order, MapFile indexes, SequenceFile sort outputs, TFile sorted-key behavior, or MapReduce partition/group assumptions.

Length-prefixed readers need strict bounds. `Text.readString`, `WritableUtils.readStringSafely`, compressed byte-array readers, and TFile string/vint decoders can be exposed to malformed or hostile input; negative lengths, oversized lengths, truncated streams, and invalid UTF-8 are important failure modes.

Compression pooling can leak resources. Forgetting to return compressors/decompressors, returning ended objects, using objects after return, or failing to reset dictionaries and buffers can cause native memory leaks, data corruption, or nondeterministic test failures. The leased-count methods are intended test signals for this.

Split compression is codec-sensitive. A wrong adjusted start/end boundary can duplicate or omit records in split reads. Base `CompressionInputStream` seeking is unsupported, so callers must use split-aware codecs rather than assuming arbitrary seekability.

`ElasticByteBufferPool` has intentionally unbounded cache growth. Workloads with diverse large buffer sizes can retain substantial heap or direct memory after the peak has passed.

`ObjectWritable` and `WritableFactories` depend on class names, classloaders, and factory registration. Missing classes, renamed packages, non-public constructors without factories, or different configuration classloaders can break deserialization.

`MapFile.fix` can rebuild indexes but cannot recover missing or corrupt data records. Supplying the wrong key/value classes or comparator semantics can create an index that is syntactically present but semantically wrong.

TFile docs note tradeoffs around block size, compression, and buffering. Too-small blocks increase index memory and compressor flush overhead; too-large blocks hurt random access; poor compression choices waste CPU or storage. The documented single-threaded seek/read behavior means multiple scanners over one TFile may serialize I/O even when reading different DFS blocks.

## Test Signals

API compatibility tests should compare this JDiff output against expected public surface: class/interface presence, inheritance, implemented interfaces, constructor and method signatures, checked exceptions, public fields, static/final/synchronized flags, deprecation markers, and package docs.

Writable round-trip tests should serialize and deserialize every primitive wrapper, `Text`, `MD5Hash`, `NullWritable`, `EnumSetWritable` including null/empty sets, `MapWritable`, `SortedMapWritable`, `TwoDArrayWritable`, `GenericWritable` subclasses, `ObjectWritable` values for writable/string/primitive/array/enum/null cases, and `VersionedWritable` mismatch failures.

Comparator tests should verify object comparison and raw byte comparison agree for primitive writables, `Text`, `MD5Hash`, vint/vlong values, and any registered optimized comparator. Byte parsing helpers in `WritableComparator` and `WritableUtils` need boundary cases for negative values, minimum/maximum widths, and malformed encodings.

IO utility tests should cover short reads/writes, EOF during `readFully` and `skipFully`, bounded copy closure behavior, cleanup swallowing exceptions while logging where appropriate, `fsync` on files/directories, exception wrapping, and `readFullyToByteArray` behavior on finite streams.

File-format tests should write and read SequenceFiles with no compression, record compression, block compression, metadata, sync seeking, raw writers, and several key/value classes. MapFile/SetFile tests should cover index creation, rename/delete, corrupt or missing index repair, and wrong-class failure paths. TFile tests should cover compression algorithms, sorted and unsorted keys, metadata block duplicate/missing exceptions, key/file-offset seeks, comparator creation, and configured chunk/buffer sizes.

Compression tests should cover codec discovery by extension, canonical class name, short name, and configured codec list; stream round trips for Default, Gzip, and BZip2 codecs; compressor/decompressor pool lease counts before and after return; reset/reuse behavior; dictionary needs; block stream boundaries; direct `ByteBuffer` decompression; and bzip2 split reads with adjusted start/end positions.

Erasure-code schema tests should cover constructors from option maps and explicit parameters, preservation of extra options, equality/hashCode, string output for logs, and validation behavior in higher-level consumers that interpret `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.

### subset-b-007196: lines 24460-30682

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.2.xml lines 24460-30682

## Scope

This chunk is a generated JDiff API snapshot for Apache Hadoop Common 3.2.2. It begins inside the tail of `org.apache.hadoop.io.file.tfile.Utils`, covers serializer, Avro serializer, log metrics, metrics2 core/filter/lib/sink/util APIs, network topology and socket factory APIs, the main security and authorization APIs, HTTP security filters, and ends inside `org.apache.hadoop.security.token.Token`.

The source is API metadata rather than executable implementation. The research therefore treats method signatures, visibility, inheritance, implemented interfaces, checked exceptions, static/final/synchronized markers, fields, and embedded Javadocs as the compatibility contract. Runtime behavior below is inferred from those public contracts and docs.

## Purpose

The opening `tfile.Utils` tail exposes sorted-list binary-search helpers used by TFile and its users. `lowerBound(List, T)` returns the first element greater than or equal to a key, while `upperBound(List, T)` returns the first element greater than a key.

The serialization packages define Hadoop pluggable serialization entry points. `JavaSerialization` is an experimental `Serialization` for Java `Serializable` classes, `JavaSerializationComparator` deserializes and compares objects through `Comparable`, and `WritableSerialization` delegates to Hadoop `Writable.write` and `Writable.readFields`. The Avro subpackage adds `AvroSerialization` as a configured abstract base plus specific and reflect variants selected by generated Avro classes, configured package names, or the `AvroReflectSerializable` marker.

The metrics packages are the largest surface. They describe immutable metric values and tags, record builders, sources, sinks, metrics-system lifecycle and JMX control, mutable counters/gauges/stats/quantiles/rates/rolling averages, sink implementations for files, Graphite, rolling filesystem output, and StatsD, plus MBean, cache, and server-address utilities.

The network package provides rack-awareness and socket-factory APIs. DNS/IP names are mapped to network locations by pluggable `DNSToSwitchMapping` implementations, optionally cached, script-backed, or table-backed. Socket factories create standard or SOCKS-proxied sockets.

The security packages cover credential and token storage, group and id mapping, Kerberos login utilities, user identity/proxy-user management, credential-provider abstraction, ACLs, impersonation checks, CSRF/clickjacking servlet filters, and the beginning of token secret-manager/token APIs.

## Important APIs, Types, and Functions

### Serialization

- `org.apache.hadoop.io.serializer.JavaSerialization` implements `Serialization` for Java `Serializable` classes.
- `JavaSerializationComparator<T>` extends `DeserializerComparator` and can throw `IOException` during construction; it compares deserialized objects via `Comparable`.
- `WritableSerialization` extends `Configured` and implements `Serialization`, delegating object state to the `Writable` protocol.
- Package configuration is through the `io.serializations` property, whose values name `Serialization` implementations able to create serializers and deserializers.
- `AvroSerialization` extends `Configured`, implements `Serialization`, and exposes `AVRO_SCHEMA_KEY`.
- `AvroSpecificSerialization` handles Avro generated "specific" classes.
- `AvroReflectSerialization` handles classes either in configured comma-separated `AVRO_REFLECT_PACKAGES` (`avro.reflect.pkgs`) or implementing the marker `AvroReflectSerializable`.

### Log Metrics

- `EventCounter` extends log4j `AppenderSkeleton`.
- Its public appender contract includes `append(LoggingEvent)`, `close()`, and `requiresLayout()`.
- It counts fatal, error, and warn events and is wired by class name from `log4j.properties`.

### Metrics2 Core

- `AbstractMetric` implements `MetricsInfo` and represents immutable metric metadata plus abstract `value()`, `type()`, and `visit(MetricsVisitor)` methods. It also supplies name, description, equality, hash, and string behavior.
- `MetricsInfo` supplies immutable `name()` and `description()` metadata; annotation docs tie names/descriptions to `@Metric` values or class names.
- `MetricsTag` implements `MetricsInfo` and adds immutable tag `value()`.
- `MetricsCollector.addRecord(String|MetricsInfo)` creates a `MetricsRecordBuilder`.
- `MetricsRecord` is an immutable timestamped snapshot with `name`, `description`, `context`, unmodifiable tags, and immutable metric iteration.
- `MetricsRecordBuilder` is the fluent writer API for tags, existing tags, existing immutable metrics, context, int/long counters, int/long/float/double gauges, `parent()`, and `endRecord()`.
- `MetricsJsonBuilder` and `MetricStringBuilder` implement record-building APIs that render collected data to JSON or custom delimited strings. `MetricsJsonBuilder.LOG` is a public static logger.
- `MetricsPlugin.init(SubsetConfiguration)` is the common plugin initialization hook.
- `MetricsSource.getMetrics(MetricsCollector, boolean all)` snapshots source state; `MetricsSink.putMetrics(MetricsRecord)` and `flush()` consume records.
- `MetricsSystem` registers/unregisters sources, registers JMX callbacks, requests best-effort immediate publication with `publishMetricsNow()`, and shuts down via `shutdown()`.
- `MetricsSystemMXBean` exposes JMX lifecycle and diagnostics: `start`, `stop`, `startMetricsMBeans`, `stopMetricsMBeans`, and `currentConfig`.
- `MetricsVisitor` receives typed gauge/counter callbacks for int, long, float, and double gauge values and int/long counters.

### Metrics2 Filters and Mutable Metrics

- `GlobFilter` and `RegexFilter` compile configured expressions to `com.google.re2j.Pattern` for metrics filtering.
- `DefaultMetricsSystem` is the default singleton with `initialize`, `instance`, `shutdown`, `setMiniClusterMode`, and `inMiniClusterMode`.
- `Interns` creates interned `MetricsInfo` and `MetricsTag` instances.
- `MetricsRegistry` creates and owns mutable metrics: int/long counters, int/long/float gauges, quantiles, stats, rates, aggregated rates, rolling averages, tags, context, named sample additions, and snapshots into a builder. Several mutating methods are synchronized, marking it as a shared source-side state container.
- `MutableMetric` tracks change state with `setChanged`, `clearChanged`, `changed`, and `snapshot(builder, all)`/`snapshot(builder)`.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` model monotonically increasing metrics.
- `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong` model values that can increase, decrease, or be set.
- `MutableQuantiles` maintains online estimates for fixed quantiles, rolls over at a configured interval, exposes `quantiles`, `previousSnapshot`, an estimator getter/setter, `add(long)`, `snapshot`, and `stop`.
- `MutableStat` stores sample statistics, optional extended stats, Welford-based variance data, `lastStat`, and min/max reset. Its docs warn that adding many samples as a single `(numSamples, sum)` preserves mean but may reduce variance accuracy.
- `MutableRate`, `MutableRates`, and `MutableRatesWithAggregation` cover throughput/rate tracking. `MutableRates` synchronizes all accesses and is documented as poor for high contention; `MutableRatesWithAggregation` uses per-thread local counts aggregated on snapshot and can lose samples produced between the last snapshot and thread death.
- `MutableRollingAverages` implements `Closeable`, keeps sliding-window average state, can collect thread-local states, add named samples, snapshot, close, and return stats filtered by minimum sample count.

### Metrics Sinks and Utilities

- `FileSink`, `GraphiteSink`, and `StatsDSink` implement sink lifecycle with `init`, `putMetrics`, `flush`, and `close`; `StatsDSink` also exposes `writeMetric`.
- `RollingFileSystemSink` writes metrics to a filesystem-backed rolling sink. It has a reflection constructor and a testing constructor, `init`, roll interval extraction, flush scheduling (`updateFlushTime`, `setInitialFlushTime`), `putMetrics`, `flush`, and `close`.
- `RollingFileSystemSink` exposes protected state for source name, error policy, append policy, base path, roll/offset intervals, next flush calendar, force/has-flushed booleans, and supplied test configuration/filesystem.
- Empty package markers exist for `org.apache.hadoop.metrics2.sink.ganglia` and `org.apache.hadoop.metrics2.source` in this slice.
- `MBeans` registers/unregisters MBeans and parses service/name parts from Hadoop's standard MBean name format.
- `MetricsCache` keeps dense cached records for sinks that do not support sparse updates.
- `Servers.parse(String, int)` parses comma and/or space separated server specifications with default ports.

### Network

- `AbstractDNSToSwitchMapping` implements common `DNSToSwitchMapping` support without extending `Configured`, explicitly to avoid superclass-constructor calls into subclass `setConf`. It tracks configuration, reports single-switch status, returns switch maps, dumps known topology, and exposes `isMappingSingleSwitch(DNSToSwitchMapping)`.
- `DNSToSwitchMapping.resolve(List)` maps hostnames/IPs one-to-one to rack paths such as `/foo/rack`; implementations should return `NetworkTopology.DEFAULT_RACK` for unknown names. It also defines cache reload methods for all or selected names.
- `CachedDNSToSwitchMapping` wraps a raw mapper, caches resolved host-to-rack mappings, exposes a copied switch map, delegates single-switch checks to the raw mapping, and can reload all or selected cached mappings.
- `ScriptBasedMapping` is a cached wrapper around a script-backed raw mapper configured by `CommonConfigurationKeys.NET_TOPOLOGY_SCRIPT_FILE_NAME_KEY`; it also exposes `NO_SCRIPT`, constructors for default/raw/conf inputs, and `Configurable` methods.
- `TableMapping` is a cached mapper backed by a two-column whitespace-separated table configured via `net.topology.table.file.name`; unresolved entries map to `/default-rack`.
- `ConnectTimeoutException` extends `SocketTimeoutException` for `NetUtils.connect` connection timeouts.
- `SocksSocketFactory` extends `javax.net.SocketFactory`, implements `Configurable`, and creates sockets through a configured or supplied SOCKS `Proxy`.
- `StandardSocketFactory` exposes the same `createSocket` overload family without `Configurable` and represents normal socket creation.

### Security, Credentials, and UGI

- `AccessControlException` extends `IOException` and includes a default constructor for unwrapping `RemoteException`.
- `Credentials` implements `Writable` and stores tokens plus secret keys in memory. It supports token/key get/add/remove/list/count maps, static token-storage file reads from `Path` or local `File`, stream read/write, file write with optional `SerializedFormat`, `Writable` read/write, `addAll` overwrite merge, and `mergeAll` non-overwrite merge.
- `GroupMappingServiceProvider` returns groups for users, refreshes group caches, and pre-adds group cache entries. `GROUP_MAPPING_CONFIG_PREFIX` is public.
- `IdMappingServiceProvider` maps user/group names and numeric ids in both directions, including unknown-tolerant uid/gid methods.
- `KerberosAuthException` carries contextual fields for user, principal, keytab file, and ticket cache file, with setters/getters and a composed message.
- `SecurityUtil` exposes global security helpers: configuration setup, original TGT checks, server principal substitution, keytab/ticket-cache login helpers, delegation-token service-name construction, Kerberos/token annotation discovery, token-service address/text conversion, login/current-user `doAs` helpers, auth-method configuration, privileged-port checks, and ZooKeeper auth-info loading. Public constants include `LOG`, `HOSTNAME_PATTERN`, and `FAILED_TO_GET_UGI_MSG_HEADER`.
- `UserGroupInformation` wraps a JAAS `Subject` and supports simple, Windows/Unix, and Kerberos identity flows. Static APIs manage global configuration, initialization checks, metrics reattachment, security-enabled state, login/current/best UGI discovery, ticket-cache/subject/keytab logins, keytab logout/relogin/force-relogin, remote/proxy/test user construction, login-method checks, and debug logging.
- UGI instances expose Kerberos-credential checks, real/effective user data, short/full user name, primary group, group arrays/lists, token identifiers, tokens, credentials, auth-method setters/getters, equality/hash by subject, protected subject access, and `doAs` wrappers for privileged actions.
- `UserGroupInformation.AuthenticationMethod` is an enum-compatible nested class with `values`, `valueOf(String)`, conversion to/from `SaslRpcServer.AuthMethod`, and docs naming existing authentication method types.

### Security Alias, Authorization, HTTP, and Tokens

- `CredentialProvider` is an abstract, thread-safe credential/password store API. It differentiates transient stores from durable ones, flushes changes, retrieves aliases and entries, creates/deletes entries, reports missing-password state, and exposes `CLEAR_TEXT_FALLBACK`.
- `CredentialProviderFactory` loads provider implementations by service loader and configuration path (`CREDENTIAL_PROVIDER_PATH`), with abstract `createProvider(URI, Configuration)` and static `getProviders(Configuration)`.
- `AccessControlList` implements `Writable`, parses user/group ACL strings, supports wildcard all-allowed state, add/remove users/groups, user and group collection access, membership checks against `UserGroupInformation`, ACL string rendering, and serialization.
- `AuthorizationException` extends `AccessControlException` but suppresses stack trace access/printing for security.
- `DefaultImpersonationProvider` implements `ImpersonationProvider`, is configurable, initializes from a proxy-user configuration prefix, authorizes proxy UGI plus remote address, builds proxy superuser config keys, exposes configured proxy groups/hosts, and has synchronized `getTestProvider`.
- `ImpersonationProvider` extends `Configurable`, initializes by configuration prefix, and authorizes proxy users by `InetAddress`; the string-address overload is a default compatibility path that is documented as less preferred because it may re-resolve addresses.
- `RestCsrfPreventionFilter` implements `javax.servlet.Filter`, classifies browser user agents with configurable regex defaults (`^Mozilla.*`, `^Opera.*`), enforces a configurable custom header unless ignored by method/user-agent rules, exposes `handleHttpInteraction`, and converts prefixed Hadoop `Configuration` keys into filter init parameters.
- `XFrameOptionsFilter` implements `Filter`, adds clickjacking protection through `X_FRAME_OPTIONS`, and also exposes configuration-prefix-to-filter-params conversion.
- Empty package markers exist for `org.apache.hadoop.security.protocolPB` and `org.apache.hadoop.security.ssl`.
- `SecretManager<T>` is the server-side token secret manager. It creates/retrieves token passwords, provides a retriable retrieval path with `StandbyException`, `RetriableException`, and `IOException`, creates empty identifiers, checks read availability, generates random secrets, computes HMAC passwords, and converts raw bytes into `SecretKey`.
- The chunk ends in the middle of `Token<T>`. Visible APIs construct tokens from identifiers plus secret managers, raw components, default state, another token, or `SecurityProtos.TokenProto`; mutate identifier/password/service; copy tokens; convert to protobuf; expose identifier, decoded identifier, password, kind, and service; and define public/private clone predicates where base tokens are non-private.

## Control Flow

The XML has no runtime control flow, but the API contracts imply these operational paths:

- Serialization selection starts from `io.serializations`; Hadoop code asks configured `Serialization` implementations whether they support a class, then obtains matching serializers/deserializers. Writable serialization delegates to each object's `write`/`readFields`; Java comparator deserializes both inputs and invokes `Comparable`.
- Avro reflect serialization accepts a class when it either implements the marker interface or belongs to a configured package. Specific serialization is intended for generated Avro classes.
- Metrics collection flows from mutable source-side state to immutable records: a `MetricsSource` snapshots into a `MetricsCollector`, builder calls add tags/metrics/gauges/counters, `MetricsSystem` periodically polls sources, then pushes records to `MetricsSink` implementations and flushes them. `publishMetricsNow()` is documented as best-effort synchronous snapshot and sink publication.
- Mutable metrics update local state and mark themselves changed. Snapshot calls emit either all metrics or only changed metrics depending on the `all` flag, then clear changed state as appropriate. Registry-level snapshots aggregate all registered mutables.
- Quantile/stat/rate/rolling-average metrics add samples during operation and publish derived snapshots later. Quantiles roll over by interval; rolling averages rotate windows; aggregated rates collect thread-local data at snapshot time.
- Sink control flow is lifecycle based: `init(SubsetConfiguration)` configures external destination and buffering, `putMetrics` writes records, `flush` forces buffered data, and `close` releases resources. Rolling filesystem output also advances `nextFlush` according to roll and offset intervals.
- Rack mapping starts with `resolve(List)` and requires output list position correspondence with input hosts. Cached mapping resolves misses through a raw mapping and serves repeated lookups from memory until all or selected mappings are reloaded. Script and table mappings derive their raw data from configuration.
- Security credential flow keeps tokens and secret keys in memory, can serialize them through `Writable`, stream, or token-storage files, and can merge credential sets either overwriting or preserving existing entries.
- UGI flow initializes global security configuration, discovers or performs a login, creates current/login/proxy/remote users, attaches tokens/credentials to a subject-backed identity, and executes actions under that identity with `doAs`.
- Impersonation flow initializes provider state from proxy-user configuration, receives an effective/proxy UGI plus remote address, and throws `AuthorizationException` if the real user, allowed groups/users, or allowed host constraints fail.
- HTTP filter flow initializes servlet filters from prefixed configuration, classifies browser requests, enforces CSRF headers for browser-like clients and non-ignored methods, or injects X-Frame-Options before delegating through the filter chain.
- Token flow constructs identifiers and passwords through `SecretManager`, stores token bytes/kind/service in `Token`, decodes identifiers for consumers, and uses retriable password retrieval to signal invalid, standby, or temporary server-side token validation failures.

## State and Persistence Behavior

The JDiff file itself is persisted API metadata for compatibility checking. It does not store Hadoop runtime state.

Serializer classes are mostly stateless factories, but they consume `Configuration` through `Configured`. The durable compatibility concern is serialized data format: Java serialization, Avro schema/key use, and Writable byte layout must remain readable by corresponding deserializers.

Metrics APIs split state into mutable and immutable layers. `MetricsInfo`, `MetricsTag`, `AbstractMetric`, and `MetricsRecord` are immutable snapshots. `MutableMetric` subclasses hold process-local counters, gauges, sample statistics, quantile estimators, per-thread rate accumulators, rolling windows, change flags, and previous snapshots. `MetricsRegistry` stores the named collection of mutable metrics and tags. `DefaultMetricsSystem` is a process singleton and has mini-cluster mode state.

Metrics sinks persist or transmit data externally. File and rolling filesystem sinks write durable metrics output; Graphite and StatsD sinks send metrics over network protocols. `MetricsCache` stores in-memory dense records for sinks that cannot process sparse updates. MBeans register process-local JMX objects under stable ObjectNames.

Network mapping state is in-memory cache plus external configuration or mapping files/scripts. `CachedDNSToSwitchMapping` stores host-to-rack results and exposes copies for diagnostics. `TableMapping` persists mapping data in the configured two-column file; `ScriptBasedMapping` depends on the configured script and cache invalidation.

Security state includes both in-memory identity state and durable credential material. `Credentials` stores token and secret-key maps, writes/reads token storage files and streams, and implements `Writable`. `CredentialProvider` implementations may be transient or durable; durable providers require `flush()` to persist changes. ACLs are serializable through `Writable`.

UGI maintains global static security configuration, login user state, metrics attachment, and per-instance JAAS subjects with principals, groups, token identifiers, tokens, credentials, and auth method markers. Kerberos login/relogin updates the subject's credentials in place. Keytab and ticket-cache paths appear in exception context and login flows but are not themselves persisted by UGI.

Token state visible in this chunk is byte arrays for identifier/password plus `Text` kind/service, with conversion to/from protobuf and `Writable` hooks continuing past the chunk boundary. `SecretManager` state is implementation-specific, but the contract requires secret keys and registries sufficient to create/retrieve passwords and detect expiry/revocation/standby availability.

## Dependencies and Integration Points

Key Java dependencies include `Serializable`, `Comparable`, collections, `Closeable`, `IOException`, `DataInput/DataOutput`, `DataInputStream/DataOutputStream`, `File`, `URI`, `InetAddress`, `Socket`, `SocketTimeoutException`, `UnknownHostException`, `Proxy`, `Calendar`, `PrintStream/PrintWriter`, JAAS `Subject`, privileged action interfaces, JMX `ObjectName`, servlet `Filter` APIs, and crypto `SecretKey`.

External library integrations include log4j `AppenderSkeleton` and `LoggingEvent`, SLF4J `Logger`, Apache Commons Configuration2 `SubsetConfiguration`, Avro specific/reflect serialization concepts, RE2/J `Pattern`, and servlet containers.

Hadoop integration points include `Configuration`, `Configured`, `Configurable`, `Writable`, `Text`, `Path`, `FileSystem`, `SecurityProtos.TokenProto`, `RemoteException`, `StandbyException`, `RetriableException`, `NetworkTopology`, `NetUtils`, `CommonConfigurationKeys`, `SaslRpcServer.AuthMethod`, `KerberosInfo`, `TokenInfo`, `TokenIdentifier`, token secret-manager subclasses, ZooKeeper auth utilities, and metrics annotation packages.

The empty package markers indicate API namespace presence but no public types in this line window for `org.apache.hadoop.ipc.protocolPB`, `org.apache.hadoop.log`, `org.apache.hadoop.metrics2.sink.ganglia`, `org.apache.hadoop.metrics2.source`, `org.apache.hadoop.net.unix`, `org.apache.hadoop.security.protocolPB`, and `org.apache.hadoop.security.ssl`.

## Risks and Edge Cases

- This chunk begins mid-class and ends mid-class. Complete reports for `tfile.Utils` and `Token` require adjacent chunks.
- JDiff omits method bodies. Exact JSON rendering, string escaping, socket proxy configuration keys, file formats, Kerberos timing policy, token byte-copy behavior, and synchronization internals need implementation-source validation.
- `JavaSerialization` is explicitly experimental and relies on Java serialization, which carries compatibility and security risks for untrusted streams.
- `JavaSerializationComparator` assumes deserialized objects implement compatible `Comparable` semantics; class mismatches or malicious serialized data can fail at runtime.
- Avro reflect package configuration is broad. Over-including packages may serialize unintended classes; under-including packages silently rejects classes unless they implement the marker.
- Metrics mutable classes mix synchronized and unsynchronized methods. Consumers should not assume all value reads are atomic or globally ordered unless the concrete implementation provides it.
- `MutableRates` warns about high contention. `MutableRatesWithAggregation` improves concurrency but can lose per-thread samples when short-lived threads die before collection.
- `MutableStat.add(numSamples, sum)` can preserve mean while degrading variance accuracy for large `numSamples`.
- Quantile and rolling-average metrics keep estimators/windows in memory; missing `stop()` or `close()` can leak scheduled work or buffers in long-running daemons.
- `publishMetricsNow()` is best effort and may return before every source/sink completes under time pressure.
- Rolling filesystem sinks expose multiple protected fields and depend on clock/roll interval math, append support, and filesystem behavior; rollover boundaries and error-ignore settings are likely failure points.
- Rack mapping requires one output per input. Returning null, wrong-sized lists, or malformed paths can break scheduler/topology assumptions.
- `AbstractDNSToSwitchMapping.isMappingSingleSwitch` documentation is internally surprising: it says mappings not derived from this class are assumed multi-switch, while the `@return` line says true if not derived. Implementation should be checked before relying on the text.
- Script-based mapping depends on external scripts and can fail due to missing executables, slow scripts, malformed output, or command injection if host inputs are not handled carefully.
- Table mapping returns `/default-rack` for misses, which can hide configuration drift by clustering unknown hosts together.
- Socket factories expose equality/hash behavior, which can affect connection-pool reuse; SOCKS proxy configuration must be included consistently.
- `Credentials` stores secret keys and token passwords in memory as byte arrays. Returned arrays may expose mutable secret material depending on implementation.
- Credential-provider implementations must be thread safe; factories using service loading and URI lists need deterministic error handling for unknown schemes or missing passwords.
- `AuthorizationException` intentionally hides stack traces, improving information hiding but reducing diagnostics.
- UGI has significant global static state. Tests that call `setConfiguration`, `setShouldRenewImmediatelyForTests`, login APIs, or mini-cluster metrics hooks can affect later tests in the same JVM.
- `doAsLoginUserOrFatal` can terminate the JVM if login user lookup fails; it is unsafe in libraries or tests unless failure is truly fatal.
- Kerberos relogin methods mutate the subject credentials and depend on keytab/ticket-cache availability and timing windows.
- HTTP CSRF browser detection is regex-based and user-agent controlled. Non-browser clients that look browser-like must send the header; browser user agents that do not match configured patterns may bypass enforcement.
- X-Frame-Options only addresses frame embedding; it does not replace broader content-security policies.
- `SecretManager.retriableRetrievePassword` broadens failure modes. Clients must distinguish invalid-token terminal failures from standby/retriable temporary failures.
- Base `Token.isPrivate()` and `isPrivateCloneOf()` are documented as false for non-private tokens; private clone behavior may depend on subclass or continuation beyond this chunk.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks ensuring all public classes, fields, constructors, overloads, checked exceptions, and deprecated markers in this JDiff slice remain present.
- Serialization tests for Java/Writable/Avro specific/Avro reflect selection, configured `io.serializations`, reflect package inclusion, marker-interface inclusion, schema key handling, comparator construction failures, and round-trip byte compatibility.
- Log metrics tests for `EventCounter` counting fatal/error/warn events, ignoring lower levels if intended, appender lifecycle, and layout requirement.
- Metrics core tests for immutable equality/hash/string behavior, builder chaining, context/tag/gauge/counter output, JSON/string rendering, visitor dispatch by metric type, record tag immutability, and source-to-sink collection through `MetricsSystem`.
- Metrics system lifecycle tests for source registration uniqueness, unregister behavior, callback registration, JMX start/stop, `currentConfig`, `publishMetricsNow` flushing, complete shutdown, and default singleton mini-cluster mode.
- Mutable metrics tests for changed-flag behavior, `all` snapshots, int/long counter increments, gauge increments/decrements/sets, registry lookup/tag override behavior, synchronized paths under concurrency, and duplicate metric/tag names.
- Statistical metric tests for quantile rollover and estimator replacement, `MutableStat` mean/min/max/stdev and variance degradation case, rate initialization from protocol classes, per-thread aggregation collection, rolling-average window eviction, `getStats(minSamples)`, and close/stop cleanup.
- Sink tests for file, Graphite, rolling filesystem, and StatsD initialization, record formatting, flush/close idempotence, connection failures, ignored versus fatal errors, rolling interval parsing, offset scheduling, append behavior, and filesystem injection for tests.
- MBeans and cache tests for ObjectName format parsing, duplicate registration/unregistration, sparse-to-dense cache updates, record eviction limits, and server specification parsing with default ports.
- Network tests for one-to-one rack mapping, empty input, unknown-host default rack, cache hits/misses/reloads, copied switch maps, topology dump content, script absent/present behavior, malformed script/table output, table reload, socket factory overloads, SOCKS proxy configuration, and equality/hash consistency.
- Security credentials tests for token/secret-key add/get/remove/count/map immutability, stream/file/Writable/protobuf round trips, overwrite versus non-overwrite merge semantics, malformed token storage, and secret byte defensive copying.
- Group/id mapping tests for nonexistent users returning empty groups, cache refresh/add behavior, unknown uid/gid handling, and IOException propagation.
- Kerberos/SecurityUtil/UGI tests for principal host substitution, keytab and ticket-cache login paths, subject-based UGI creation, current/login/proxy/remote/test users, token and credential attachment, group lookup failure behavior, auth method conversions, relogin and logout errors, `doAs` exception mapping, static configuration isolation, and debug logging.
- Credential-provider tests for service-loader provider discovery, URI scheme handling, transient versus persistent stores, missing-password warnings/errors, create duplicate alias failure, delete missing alias behavior, flush durability, and thread safety.
- Authorization tests for ACL parsing/rendering, wildcard semantics, user/group add/remove, serialization, suppressed stack traces, proxy superuser key generation, group/host allow and deny cases, string-address authorization compatibility, and remote address resolution avoidance.
- HTTP filter tests for prefixed configuration extraction, browser regex matching including null user agent, custom header enforcement, ignored HTTP methods, servlet chain continuation/rejection status, X-Frame-Options header value, and filter lifecycle.
- Token tests for HMAC password determinism with a fixed key, random secret generation shape, invalid/standby/retriable retrieval exceptions, read-availability checks, token constructor defensive copies, protobuf conversion, service mutation, identifier decoding failure paths, and private clone base behavior.

## Cross-Chunk Notes

The previous chunk is required to complete `org.apache.hadoop.io.file.tfile.Utils`; this one only includes `lowerBound`, `upperBound`, and the closing class/package docs. A later chunk is required to complete `org.apache.hadoop.security.token.Token`; this chunk stops at the opening of `readFields`.

### subset-b-007197: lines 30683-35381

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.2.xml lines 30683-35381

## Scope

This chunk is the final segment of the Apache Hadoop Common 3.2.2 JDiff API XML. It starts inside the tail of `org.apache.hadoop.security.token.Token`, then covers token renewer/identifier/selector APIs, HTTP delegation-token APIs, service lifecycle APIs, service launcher contracts, tracing administration interfaces, common utility classes, `Shell`, shutdown and tool helpers, build/version metadata, Bloom filter implementations, and the closing empty package markers for `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash`.

The source is generated API metadata rather than implementation code. The research surface is the public/protected compatibility contract: type names, inheritance, implemented interfaces, constructors, method signatures, parameters, return types, checked exceptions, visibility/static/final/synchronized/abstract flags, deprecation text, fields, and embedded Javadocs.

## Purpose

The security-token portion defines Hadoop's client-side token compatibility surface. `Token` supports writable serialization, URL-safe string encoding, equality/hash/cache-key behavior, renewability checks, renewal, and cancellation. `TokenIdentifier`, `TokenRenewer`, `TokenSelector`, `TokenInfo`, and `Token.TrivialRenewer` define the extension points used by services and filesystems to create, identify, select, renew, and cancel delegation tokens.

The delegation-web package layers Hadoop delegation-token operations on top of HTTP authentication. It lets clients authenticate with Kerberos SPNEGO or pseudo authentication, request delegation tokens, transmit tokens via headers or query strings for WebHDFS compatibility, renew tokens, and cancel tokens against HTTP/S endpoints.

The service packages define Hadoop's reusable daemon lifecycle model. `Service`, `AbstractService`, `CompositeService`, listeners, lifecycle events, lifecycle exceptions, and state models standardize initialization, start, stop, close, state history, failure recording, blocker tracking, child-service composition, and state transition validation. The launcher subpackage adds a command-line service execution contract, common exit codes, launch exceptions, and an uncaught-exception handler.

The tracing portion exposes APIs for listing, adding, and removing span receivers through Java and protobuf-compatible protocols. The util portion provides application classloader isolation, IP-list membership, progress callbacks, checksums, reflection helpers, portable shell execution, shutdown-hook registration, string interning, host resource metrics, Hadoop CLI tool execution, version metadata, and probabilistic Bloom filter data structures.

## Important APIs, Types, and Functions

### Security Tokens

- The visible tail of `Token` includes `write(DataOutput)`, `encodeToUrlString()`, `decodeFromUrlString(String)`, `equals(Object)`, `hashCode()`, `toString()`, `buildCacheKey()`, `isManaged()`, `renew(Configuration)`, `cancel(Configuration)`, and public static final `LOG`.
- `Token.TrivialRenewer` extends `TokenRenewer` for token kinds that are not managed. Subclasses provide protected `getKind()`. The class implements `handleKind(Text)`, `isManaged(Token)`, `renew(Token, Configuration)`, and `cancel(Token, Configuration)`.
- `TokenIdentifier` is an abstract `Writable`. It requires `getKind()` and `getUser()`, and provides `getBytes()` plus `getTrackingId()`, documented as an MD5 of the serialized identifier bytes.
- `TokenInfo` is an annotation marker for token-related information.
- `TokenRenewer` is the plugin base class for token operations. Implementations must answer `handleKind(Text)`, determine `isManaged(Token)`, renew tokens to a new expiration time, and cancel tokens.
- `TokenSelector` selects a `Token` from a token collection for a named `Text` service.

### Delegation Token Web APIs

- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL`. Constructors accept no arguments, a `DelegationTokenAuthenticator`, a `ConnectionConfigurator`, or both authenticator and configurator.
- Static default authenticator control is exposed through `setDefaultDelegationTokenAuthenticator(Class)` and `getDefaultDelegationTokenAuthenticator()`. The documented default is `KerberosDelegationTokenAuthenticator`.
- `setUseQueryStringForDelegationToken(boolean)` is protected and exists for WebHDFS backwards compatibility. `useQueryStringForDelegationToken()` reports whether delegation tokens are sent in the query string rather than the `DelegationTokenAuthenticator.DELEGATION_TOKEN_HEADER` header.
- `openConnection(...)` overloads return authenticated `HttpURLConnection` instances. When a `DelegationTokenAuthenticatedURL.Token` contains a delegation token, that token takes precedence over the configured authenticator.
- `getDelegationToken(...)`, `renewDelegationToken(...)`, and `cancelDelegationToken(...)` each have overloads with optional `doAsUser`. Get and renew can throw `AuthenticationException`; cancellation is documented as not requiring configured-authenticator authentication and throws `IOException`.
- Nested `DelegationTokenAuthenticatedURL.Token` extends `AuthenticatedURL.Token` and stores an `org.apache.hadoop.security.token.Token` through `getDelegationToken()` and `setDelegationToken(Token)`.
- `DelegationTokenAuthenticator` wraps an `Authenticator` and implements `Authenticator` itself. It supports `setConnectionConfigurator`, `authenticate`, token get/renew/cancel operations, and public constants for operation, header, query parameter, service parameter, renewer parameter, token JSON field names, and renewal JSON field names.
- `KerberosDelegationTokenAuthenticator` supports Kerberos SPNEGO plus delegation-token operations and falls back to `PseudoDelegationTokenAuthenticator` if the endpoint does not trigger SPNEGO.
- `PseudoDelegationTokenAuthenticator` supports Hadoop pseudo authentication by trusting the current `UserGroupInformation` username model.

### Service Lifecycle

- `Service` extends `Closeable` and defines `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration, name/config/state/start-time/failure accessors, `isInState(STATE)`, `waitForServiceToStop(long)`, lifecycle history, and blocker maps.
- `AbstractService` implements `Service`. It exposes final state/failure methods, protected `setConfig(Configuration)`, public lifecycle methods, protected `noteFailure(Exception)`, protected hooks `serviceInit(Configuration)`, `serviceStart()`, and `serviceStop()`, global listener registration, lifecycle history, and blocker management.
- `CompositeService` extends `AbstractService` and manages child services through cloned `getServices()`, protected `addService(Service)`, `addIfService(Object)`, synchronized `removeService(Service)`, and lifecycle hook overrides. The protected `STOP_ONLY_STARTED_SERVICES` policy controls whether shutdown tries every child or only started children.
- `LifecycleEvent` is serializable and exposes public `time` and `state` fields for lifecycle history.
- `LoggingStateChangeListener` implements `ServiceStateChangeListener` and logs transitions at INFO level, either to a supplied SLF4J `Logger` or its static class logger.
- `ServiceOperations` provides static stop helpers: `stop(Service)` and three `stopQuietly(...)` overloads that return caught exceptions rather than throwing during cleanup.
- `ServiceStateException` is a runtime lifecycle exception that implements `ExitCodeProvider`. Constructors can derive an exit code from a nested cause or accept one explicitly, and `convert(Throwable)` overloads wrap checked failures in runtime exceptions.
- `ServiceStateModel` owns state validation. It can start in `NOTINITED` or a supplied state, query current state, ensure an expected state, enter a new state in a synchronized method, check transitions statically, and test whether a transition is valid.

### Service Launcher

- `LaunchableService` extends `Service` and adds `bindArgs(Configuration, List)` plus `execute()`. `bindArgs` runs before `Service.init`, and any non-null returned configuration becomes the configuration passed into initialization. `execute` runs after `Service.start`, and its return value becomes the process exit code.
- `AbstractLaunchableService` extends `AbstractService` and implements `LaunchableService` with a protected constructor, a default `bindArgs` that logs arguments and returns the same configuration, and a default `execute` returning success.
- `HadoopUncaughtExceptionHandler` implements `Thread.UncaughtExceptionHandler`. It is intended for main entry points; standard exceptions are logged during normal operation, while `Error` conditions lead to process shutdown/exit behavior.
- `LauncherExitCodes` defines stable integer process outcomes: success, generic fail, client-initiated shutdown, task launch failure, interrupted, other failure, command argument error, unauthorized, usage, forbidden, not found, operation not allowed, not acceptable, connectivity problem, bad configuration, exception thrown, unimplemented, service unavailable, unsupported version, service creation failure, and service lifecycle exception. Many are documented as one-byte analogues of HTTP status families.
- `ServiceLaunchException` extends `ExitUtil.ExitException`, implements `ExitCodeProvider` and `LauncherExitCodes`, and carries explicit exit codes. Its formatted constructor uses `String.format` in the English locale and treats the last throwable argument as the cause.

### Tracing

- `SpanReceiverInfo` exposes `getId()` and `getClassName()`.
- `SpanReceiverInfoBuilder` is constructed with a class name, accepts configuration pairs through `addConfigurationPair(String, String)`, and emits a `SpanReceiverInfo` via `build()`.
- `TraceAdminProtocol` lists span receivers, adds a span receiver and returns its id, removes a receiver by id, throws `IOException` on protocol operations, and exposes `versionID`.
- `TraceAdminProtocolPB` combines generated protobuf `TraceAdminPB.TraceAdminService.BlockingInterface` with Hadoop `VersionedProtocol`.

### General Utilities

- `ApplicationClassLoader` extends `URLClassLoader`, can be constructed from URL arrays or a classpath string, overrides resource and class loading, and exposes static `isSystemClass(String, List)`. `SYSTEM_CLASSES_DEFAULT` marks JDK, Hadoop, resource, and selected third-party classes as parent/system loaded.
- `IPList.isIn(String)` is the package-level IP membership abstraction.
- `Progressable.progress()` is the minimal callback for long-running Hadoop APIs to report forward progress.
- `PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum` with `getValue()`, `reset()`, and both single-byte and byte-array `update` methods.
- `ReflectionUtils` handles configuration injection (`setConf`), reflective construction (`newInstance` overloads), lock contention tracing toggles, thread-info printing/logging with rate limiting, class lookup, writable copy/clone through serialization, and inherited field/method discovery.
- `Shell` is an abstract base for portable command execution. It exposes Java-version checks, Windows command-line length validation, OS-specific command builders for groups/users/permissions/ownership/symlinks/process signaling, script-extension helpers, Hadoop home/bin/winutils discovery, bash support checks, per-command environment and working-directory setters, interval-gated `run()`, abstract command/result hooks, process/exit/timeout inspection, static `execCommand` overloads, global process destruction/listing, and memory-lock-limit calculation.
- `Shell` public fields include platform constants and booleans (`WINDOWS`, `LINUX`, `MAC`, `SOLARIS`, `FREEBSD`, `OTHER`, `PPC_64`), Hadoop home variables, command names, `WindowsProcessLaunchLock`, deprecated `WINDOWS_MAX_SHELL_LENGHT`, deprecated nullable `WINUTILS`, `isSetsidAvailable`, `ENV_NAME_REGEX`, and `TOKEN_SEPARATOR_REGEX`. Protected fields include `timeOutInterval` and `inheritParentEnv`.
- `ShutdownHookManager` is a final singleton with `get()`, prioritized hook registration, registration with timeout/unit, hook removal, hook presence checks, shutdown-in-progress checks, and `clearShutdownHooks()`. Public constants define minimum timeout and default time unit.
- `StringInterner` exposes strong and weak canonicalization through `strongIntern(String)`, `weakIntern(String)`, and in-place array interning via `internStringsInArray(String[])`.
- `SysInfo.newInstance()` selects a host metrics implementation. Abstract metrics include total/available virtual and physical memory, processors, cores, CPU frequency, cumulative CPU time, CPU usage percentage, vcores used, network bytes read/written, and storage bytes read/written.
- `Tool` extends `Configurable` with `run(String[] args)` returning an integer process-style exit code.
- `ToolRunner` wires generic Hadoop option parsing and tool execution through `run(Configuration, Tool, String[])` and `run(Tool, String[])`, plus `printGenericCommandUsage(PrintStream)` and interactive `confirmPrompt(String)`.
- `VersionInfo` exposes component/build metadata through protected instance getters and static Hadoop-common getters for version, revision, branch, build date, user, URL, source checksum, build version, protoc version, and `main(String[])`.

### Bloom Filter APIs

- `BloomFilter` extends `Filter` with a default deserialization constructor and `(int vectorSize, int nbHash, int hashType)` constructor. It supports `add(Key)`, `membershipTest(Key)`, logical operations `and(Filter)`, `or(Filter)`, `xor(Filter)`, complement `not()`, `toString()`, `getVectorSize()`, and writable `write(DataOutput)`/`readFields(DataInput)`.
- `CountingBloomFilter` is final and extends `Filter`. It supports the normal filter operations plus `delete(Key)` and `approximateCount(Key)`. The Javadocs warn that adding the same key more than 15 times can overflow associated counters and raise error rates for this and other keys.
- `DynamicBloomFilter` extends `Filter`, adds an `(int vectorSize, int nbHash, int hashType, int nr)` constructor, and grows by adding Bloom-filter rows when the active row threshold is exceeded.
- `HashFunction` is final and maps a `Key` to `nbHash` bounded integer positions using the selected `org.apache.hadoop.util.hash.Hash` type. `clear()` is explicitly a no-op.
- `RemoveScheme` defines public short constants `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO` for retouched Bloom filter clearing strategies.
- `RetouchedBloomFilter` is final, extends `BloomFilter`, implements `RemoveScheme`, records false-positive evidence through overloads accepting a `Key`, `Collection`, `List`, or `Key[]`, applies `selectiveClearing(Key, short)`, and supports writable serialization.

## Control Flow

The XML itself has no runtime control flow. The documented APIs imply these execution paths:

- Token clients serialize and deserialize tokens through `Writable`, encode them into URL-safe strings for transport, select them from user credential collections by service name, and invoke `TokenRenewer` plugins for managed-token renewal or cancellation. `Token.TrivialRenewer` provides the no-management path for token kinds that cannot be renewed.
- HTTP delegation-token clients create a `DelegationTokenAuthenticatedURL`, optionally customize the authenticator and connection configurator, authenticate or attach an existing delegation token, then use REST-style token get/renew/cancel calls. Query-string transport is an alternate path for compatibility, while the documented default is header transport.
- Service flow is a state-machine lifecycle: construct, bind or set configuration, `init`, `start`, optionally execute or serve, then `stop`/`close`. `AbstractService` wraps subclass hooks, records failures, maintains lifecycle history, and notifies local plus global listeners. `CompositeService` cascades init/start/stop across child services.
- Launcher flow passes command-line arguments into `LaunchableService.bindArgs` before initialization, starts the service, calls `execute`, then maps return values or thrown exceptions into process exit codes. Exceptions that already carry exit codes are preserved or wrapped into `ServiceLaunchException`.
- The uncaught-exception handler branches between ordinary exceptions, which are logged in non-shutdown conditions, and `Error` cases, where the documented behavior is to exit because process state is unknown.
- Tracing admin flow builds span receiver descriptions, calls the Java or protobuf protocol to list/add/remove receivers, and returns either receiver arrays, new ids, or `IOException`.
- Application classloading uses child-first lookup for application classes/resources, while configured system-class patterns force parent/system loading. `isSystemClass` requires a positive match and no negative-pattern match.
- Tool execution flows through `ToolRunner`: parse generic Hadoop options into a `Configuration`, set that configuration on the `Tool`, pass remaining arguments to `Tool.run`, and return the resulting exit code.
- Shell execution flow constructs a command vector, validates or adapts for platform details, applies environment and working directory, optionally gates repeated execution by interval, runs a subprocess, parses stdout through `parseExecResult(BufferedReader)`, records exit/timeout/process state, and exposes global cleanup through `destroyAllShellProcesses()`.
- Shutdown hooks are registered with priority and optional timeout. Higher-priority hooks run earlier; equal priorities have non-deterministic ordering; timed hooks are terminated if they exceed their configured duration.
- Bloom filters hash a `Key` into multiple positions. Add operations mutate bit/counter/row state, membership tests check the corresponding positions, logical operations combine compatible filters, and default constructors plus `readFields` support deserialization. Counting filters decrement counters on delete, dynamic filters allocate rows as thresholds are reached, and retouched filters clear selected bits based on recorded false positives and a removal scheme.

## State and Persistence Behavior

This JDiff file persists Hadoop's public API metadata for release compatibility checks. It does not store Hadoop runtime state.

Token APIs are persistence-sensitive. `Token` and `TokenIdentifier` use Hadoop `Writable` serialization; URL-safe encoding is a transport representation of token bytes; `buildCacheKey`, equality, and hash code influence in-memory token caches and credential lookup behavior. Renew and cancel are external state changes against token authorities.

Delegation-token web state lives in authentication token objects, the optional stored Hadoop delegation token, the selected default authenticator class, connection configurators, and endpoint-side token state. Cancellation and renewal mutate server-side token state; header versus query-string transmission affects exposure risk and compatibility.

Service APIs maintain process-local lifecycle state. `AbstractService` records current state, failure cause/state, start time, lifecycle history, registered listeners, global listeners, and blocker maps. `LifecycleEvent` snapshots transition time and state. `ServiceStateModel.enterState` is synchronized, while callers see state through query methods. This state is not durable unless a service implementation records it elsewhere.

`CompositeService` stores child-service lists and cascades lifecycle operations. `getServices()` returns a cloned snapshot, so later additions are not visible through a previously returned list.

Launcher state includes bound arguments, the configuration returned from `bindArgs`, service state after start, and process exit-code mapping. `ServiceLaunchException` carries exit status as structured exception state.

Tracing APIs represent active span receivers in the tracing subsystem. `SpanReceiverInfo` stores receiver id, class name, and builder-provided configuration pairs; add/remove operations mutate tracing runtime state through the protocol implementation.

Utility state is mostly process-local:

- `ApplicationClassLoader` stores URLs, parent loader, and loaded-class cache inherited from `URLClassLoader`.
- `StringInterner` keeps canonical string representatives; strong interning retains representatives, weak interning allows collection.
- `ReflectionUtils` likely relies on cached constructors and serialization helpers behind its static API, though exact cache shape is not visible in JDiff.
- `Shell` holds per-instance execution policy and subprocess state plus static platform detection and command-path state. `getAllShells()` and `destroyAllShellProcesses()` imply a process-wide registry of active shell instances.
- `ShutdownHookManager` stores hook entries and shutdown-progress status in the JVM.
- `SysInfo` exposes live host counters and capacities. These are snapshots or cumulative operating-system values, not Hadoop-managed persistence.
- `VersionInfo` exposes immutable build-time metadata embedded in Hadoop artifacts.

Bloom filters explicitly persist through `write(DataOutput)` and `readFields(DataInput)`. Durable state includes vector size, hash count/type, bit vectors, counter vectors, dynamic row matrices and thresholds, and retouched false-positive bookkeeping. The structures persist compact probabilistic summaries, not original key sets; deserialized filters rely on compatible hash behavior to preserve query semantics.

## Dependencies and Integration Points

This chunk depends heavily on Java platform APIs: `java.io` data streams, exceptions, `Closeable`, `Serializable`, `File`, `BufferedReader`, `PrintStream`, `Process`, URL/HTTP classes, `URLClassLoader`, collections, `Thread.UncaughtExceptionHandler`, `TimeUnit`, checksums, annotations, and primitive arrays/strings.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configurable` for services, token renewal, launchable services, and `ToolRunner`.
- `org.apache.hadoop.io.Text`, `Writable`, and Hadoop serialization conventions for token identifiers and Bloom filters.
- `org.apache.hadoop.security.UserGroupInformation` for token identity and pseudo-authentication behavior.
- `org.apache.hadoop.security.authentication.client.AuthenticatedURL`, `Authenticator`, `ConnectionConfigurator`, and `AuthenticationException` for HTTP authentication.
- `org.apache.hadoop.service.Service.STATE`, `ServiceStateChangeListener`, `ExitCodeProvider`, `ExitUtil.ExitException`, and launcher exit-code mapping.
- Hadoop IPC/protobuf through `TraceAdminPB.TraceAdminService.BlockingInterface` and `VersionedProtocol`.
- SLF4J logging through `Logger` fields and listeners.
- `GenericOptionsParser`, referenced by `Tool`/`ToolRunner` Javadocs, as the parser for Hadoop generic command-line options.
- Native OS integration through `Shell`: Hadoop home discovery, `winutils`, Unix command names, Windows command-line length constraints, process signaling, symlink/readlink helpers, bash support, and `setsid` availability.
- `org.apache.hadoop.util.bloom.Filter` and `Key`, plus `org.apache.hadoop.util.hash.Hash`, for all Bloom filter variants.

The empty `org.apache.hadoop.tools`, `org.apache.hadoop.tools.protocolPB`, `org.apache.hadoop.util.curator`, and `org.apache.hadoop.util.hash` package elements are package markers in this JDiff segment. Public members for those packages are absent from this exact range, though `hash.Hash` is referenced by Bloom constructors and `HashFunction` Javadocs.

## Risks and Edge Cases

- This chunk begins mid-`Token`; constructors, fields, and earlier token methods are outside the assigned range and must be reconciled with the previous chunk before producing a complete file-level report.
- JDiff exposes signatures and Javadocs only. Exact validation, synchronization, serialization wire formats, REST operation names, subprocess draining, timeout enforcement, listener notification ordering, and exception messages require implementation-source validation.
- Token renewal and cancellation are security-sensitive external side effects. Wrong renewer selection, malformed services, stale cache keys, or URL string decoding errors can break authentication or leak credentials.
- `TokenIdentifier.getTrackingId()` is documented as MD5 of token identifier bytes. This is useful for correlation, not for strong security guarantees.
- HTTP delegation token query-string transport exists for WebHDFS compatibility but is riskier than header transport because URLs are commonly logged or cached.
- `DelegationTokenAuthenticatedURL` instances are explicitly documented as not thread-safe. Sharing a token/authenticated URL instance across threads risks state races.
- Pseudo delegation-token authentication trusts current-user identity. It must only be used where Hadoop simple authentication semantics are acceptable.
- Service listener callbacks can stall lifecycle transitions if slow, and implementations that re-enter service methods from callbacks can create lock-ordering problems depending on implementation details.
- `AbstractService.serviceStop()` implementations are required to be robust against partial failures and null references; otherwise the first cleanup failure can mask later cleanup work.
- `CompositeService` shutdown policy can skip non-started child services unless failure paths force stop. Child services that require stop after partial init need tests around init/start failures.
- Exit-code constants are public compatibility surface. Renumbering them would break scripts and service launchers that rely on stable process outcomes.
- `HadoopUncaughtExceptionHandler` may terminate the process on `Error`, so tests and embedding applications need clear isolation.
- Classloader isolation depends on system-class pattern correctness. Bad negative/positive patterns can load duplicate Hadoop classes or incompatible dependencies.
- `Shell.WINDOWS_MAX_SHELL_LENGHT` remains misspelled and deprecated for compatibility; removing it would break callers compiled against the typo.
- `Shell.WINUTILS` is deprecated and nullable. Callers should use exception-raising getters; legacy null checks remain necessary for direct field use.
- Public `WindowsProcessLaunchLock` exposes a global synchronization object; external misuse can serialize or deadlock process launches.
- Static platform booleans are process snapshots. Code that changes `os.name` after class initialization should not expect these fields to update.
- `Shell.destroyAllShellProcesses()` is global and can affect unrelated active shell users in the same JVM.
- `Tool.run` throws broad `Exception`, so launchers must define consistent logging and exit-code policy.
- `ToolRunner.confirmPrompt` is interactive and can block unattended automation.
- `SysInfo` metrics are platform/container dependent and may be unavailable, permission-limited, or differently scoped. Callers should tolerate sentinel/unavailable values and unsupported platforms.
- Strong string interning can leak memory on high-cardinality inputs; weak interning cannot guarantee stable identity once representatives are collected.
- Bloom filters have false positives by design. Counting filters add deletion but can overflow after repeated same-key inserts above the documented 15-count range and can underflow after deletes. Retouched filters intentionally introduce possible false negatives. Dynamic filters grow memory and serialized size as rows are added.
- Logical Bloom filter operations require compatible vector sizes, hash counts, and hash algorithms. The XML does not show how incompatibility is detected or reported.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks confirming all public/protected classes, interfaces, fields, constructors, methods, checked exceptions, deprecation strings, abstract/final/static/synchronized flags, and inheritance relationships remain stable for Hadoop Common 3.2.2.
- Token tests for writable round trips, URL-safe encode/decode round trips, equality/hash/cache-key stability, token selector service matching, `TokenIdentifier.getBytes()` determinism, tracking id determinism, renewer selection by kind, unmanaged `TrivialRenewer` behavior, and renew/cancel exception propagation.
- Delegation web tests for default authenticator selection, custom authenticator/configurator wiring, header versus query-string token transmission, token precedence over authenticator login, doAs variants, HTTP/S validation, JSON field parsing, renew expiration return values, cancellation without configured-authenticator authentication, and non-thread-safe usage documentation.
- Service lifecycle tests covering valid and invalid transitions, null configuration rejection, idempotent lifecycle calls, failure cause/state recording, lifecycle history snapshots, listener registration/removal/global notification, blocker add/remove snapshots, `waitForServiceToStop` timeouts, and close relaying to stop.
- Composite service tests for child init/start/stop ordering, cloned `getServices()` snapshots, `addIfService` behavior, synchronized removal, shutdown policy, and cleanup after child init/start failures.
- Launcher tests for `bindArgs` configuration replacement, `execute` exit-code propagation, wrapping of exceptions that implement `ExitCodeProvider`, preservation of `ExitUtil.ExitException`, formatted `ServiceLaunchException` causes, and every `LauncherExitCodes` constant used by callers.
- Uncaught handler tests for ordinary exception logging, shutdown-in-progress behavior, `Error` escalation, and delegate handler behavior for simple exceptions.
- Tracing tests for span receiver builder configuration pairs, list/add/remove protocol behavior, id return values, `IOException` handling, and PB protocol version compatibility.
- Application classloader tests for URL-array and classpath-string construction, wildcard expansion if implemented, parent/system class patterns, negative pattern precedence, resource lookup ordering, synchronized `loadClass(name, resolve)`, and `MalformedURLException` handling.
- Utility tests for IP list membership, `Progressable.progress()` callback invocation by consumers, CRC32/CRC32C known vectors, `ReflectionUtils` constructor/configuration injection, writable copy/clone behavior, inherited field/method discovery, thread-info logging rate limits, and contention tracing toggles.
- Shell tests for Java version predicates, Windows command-length validation including delimiter assumptions, user/group command builders, permission/owner/symlink/readlink command builders, process-alive/signal command builders, environment regex, script extension and script run command selection, Hadoop home/bin/winutils success and failure paths, bash support interruption, interval-gated execution, environment/working-directory inheritance, stdout parsing delegation, timeout marking, exit code capture, waiting-thread exposure, static `execCommand` overloads, global shell destruction, active shell set snapshots, and memlock limit calculation.
- Shutdown hook tests for singleton identity, priority ordering, non-deterministic equal-priority handling, timeout enforcement, removal/has checks, shutdown-in-progress flag behavior, default timeout/unit, and test cleanup through `clearShutdownHooks()`.
- String interner tests for strong and weak identity canonicalization, null behavior if defined by implementation, array in-place interning, weak-reference reclamation, and strong-cache growth under high-cardinality input.
- SysInfo tests for OS-specific `newInstance`, unsupported platforms, memory/core/frequency ranges, unavailable CPU/vcore sentinels, monotonic cumulative CPU/network/storage counters where expected, and containerized-host differences.
- Tool/ToolRunner tests for generic Hadoop option parsing, configuration injection, argument pass-through, exit-code propagation, exception propagation, generic usage output, prompt yes/no parsing, and noninteractive prompt handling.
- VersionInfo tests for non-null static build metadata, component-specific protected getter behavior through a test subclass, protoc version exposure, build-version formatting, source checksum exposure, and `main` output stability.
- Bloom filter tests for add/membership semantics, expected false-positive behavior, absence of false negatives in add-only Bloom filters, logical operations on compatible filters, failure or rejection for incompatible filters, vector-size reporting, string rendering, serialization round trips, counting delete and approximate count behavior, overflow above 15 repeated inserts, underflow after deletes, dynamic row growth at `nr`, `HashFunction` determinism/bounds/no-op clear, retouched false-positive overloads including null no-op, every `RemoveScheme`, selective-clearing tradeoffs, and serialized compatibility golden data.

## Cross-Chunk Notes

The assigned range starts after the beginning of `org.apache.hadoop.security.token.Token`; earlier token API members are outside this chunk. This chunk reaches the closing `</api>` tag of `Apache_Hadoop_Common_3.2.2.xml`, so there is no later chunk for this source file after the empty `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash` package markers.
