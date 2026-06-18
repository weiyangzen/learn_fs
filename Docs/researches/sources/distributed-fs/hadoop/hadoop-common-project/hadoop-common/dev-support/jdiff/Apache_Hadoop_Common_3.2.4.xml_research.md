# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.4.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007198`: lines 1-6121, `Docs/researches/chunks/subset-b-007198_research.md`
- `subset-b-007199`: lines 6122-12095, `Docs/researches/chunks/subset-b-007199_research.md`
- `subset-b-007200`: lines 12096-18157, `Docs/researches/chunks/subset-b-007200_research.md`
- `subset-b-007201`: lines 18158-24453, `Docs/researches/chunks/subset-b-007201_research.md`
- `subset-b-007202`: lines 24454-30679, `Docs/researches/chunks/subset-b-007202_research.md`
- `subset-b-007203`: lines 30680-35426, `Docs/researches/chunks/subset-b-007203_research.md`

## Chunk Research

### subset-b-007198: lines 1-6121

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.4.xml lines 1-6121

## Scope

This chunk is the opening slice of the Apache Hadoop Common 3.2.4 JDiff API snapshot. It includes the XML header, generation metadata, classpath/doclet command, `org.apache.hadoop.HadoopIllegalArgumentException`, the complete visible `org.apache.hadoop.conf` package in this range, `org.apache.hadoop.crypto.key` key-provider APIs, empty package markers for `org.apache.hadoop.crypto`, `org.apache.hadoop.crypto.key.kms`, and `org.apache.hadoop.crypto.random`, and the start of `org.apache.hadoop.fs` through the beginning of `ContentSummary`.

The source is generated API metadata rather than implementation code. The research surface is the public/protected compatibility contract: type names, inheritance, implemented interfaces, method signatures, checked exceptions, fields, deprecation markers, abstract/final/static/synchronized attributes, and embedded Javadocs. This chunk ends mid-`ContentSummary`, so later chunks are required for the complete `ContentSummary` API.

## Purpose

The file exists to feed JDiff compatibility checks for Hadoop Common 3.2.4. The header records the release name, doclet version, generation time, source path, and build-time dependency classpath used to extract public API metadata.

The first API group defines Hadoop's configuration contract. `Configuration` is the central mutable settings container used across Hadoop, with XML resource loading, default-resource management, deprecated-key aliasing, variable expansion, typed getters/setters, password lookup through credential providers, class loading, socket-address helpers, XML/JSON-like dumps, `Writable` serialization, and tag-based property grouping. `Configurable` and `Configured` are the small integration points used by Hadoop tools and services to receive a `Configuration`.

The crypto key-provider group defines the storage-neutral abstraction for Hadoop secret key material. `KeyProvider` separates callers from concrete key stores, exposes key-version lifecycle operations, and is explicitly documented as thread-safe for implementations. `KeyProviderFactory` discovers providers from configured URIs through a service-loader style factory mechanism.

The filesystem group begins Hadoop's abstract filesystem compatibility surface. `AbstractFileSystem` is the implementor-facing VFS layer behind `FileContext`, with methods for path validation, qualification, create/open/delete/rename/list/status operations, symlink handling, ACLs, xattrs, snapshots, storage policies, and capability probing. Supporting types in this slice describe Avro input adaptation, block locations, storage policies, direct `ByteBuffer` reads, stream cache/readahead/unbuffer controls, checksum errors, client-side checksum filesystems, public common configuration constants, and the start of content-summary counters.

## Important APIs, Types, and Functions

### Hadoop Root

- `HadoopIllegalArgumentException` extends `IllegalArgumentException` and carries a string detail message. Its purpose is to distinguish invalid-argument failures thrown by Hadoop code from those thrown by the JDK.

### Configuration Package

- `Configurable` declares `setConf(Configuration)` and `getConf()`.
- `Configured` implements `Configurable`, has zero-arg and `Configuration` constructors, and stores/retrieves the current configuration for subclasses.
- `Configuration` extends `Object`, implements `Iterable` and `Writable`, and has constructors for default loading, explicit `loadDefaults`, and cloning another configuration.
- Global deprecation APIs include `addDeprecations(DeprecationDelta[])`, several `addDeprecation` overloads for one or multiple replacement keys and optional custom messages, `isDeprecated(String)`, `hasWarnedDeprecation(String)`, and `dumpDeprecatedKeys()`. The Javadocs call out lockless atomic replacement of deprecation context for bulk additions.
- Resource loading APIs include `addDefaultResource(String)`, many `addResource` overloads for classpath names, `URL`, `Path`, `InputStream`, `Properties`, restricted parser flags, and custom resource names, plus `reloadConfiguration()` and static synchronized `reloadExistingConfigurations()`.
- System-property controls include static `setRestrictSystemPropertiesDefault(boolean)`, instance `setRestrictSystemProperties(boolean)`, and `setRestrictSystemProps(boolean)`.
- String lookup and mutation APIs include `get`, `getTrimmed`, `getRaw`, `set`, `unset`, `setIfUnset`, `onlyKeyExists`, `setAllowNullValueProperties`, `getPropertySources`, `getPropsWithPrefix`, `getValByRegex`, and `iterator`.
- Typed getters/setters include `getInt`/`setInt`, `getInts`, `getLong`/`setLong`, `getLongBytes`, `getFloat`/`setFloat`, `getDouble`/`setDouble`, `getBoolean`/`setBoolean`, `setBooleanIfUnset`, `getEnum`/`setEnum`, time-duration overloads with `TimeUnit`, storage-size overloads with `StorageUnit`, `getPattern`/`setPattern`, ranges, string collections, string arrays, and trimmed-string variants.
- Security-sensitive configuration access includes `getPassword`, `getPasswordFromCredentialProviders`, and protected `getPasswordFromConfig`, with explicit `IOException` on provider lookup paths.
- Networking helpers include `getSocketAddr` overloads, `setSocketAddr`, and `updateConnectAddr` overloads for wildcard/bind-host and advertised address handling.
- Class-loading helpers include `getClassByName`, `getClassByNameOrNull`, `getClasses`, `getClass` overloads with interface validation, `getInstances`, `setClass`, `getClassLoader`, and `setClassLoader`.
- Local resource helpers include `getLocalPath`, `getFile`, `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader`.
- Persistence and debug output APIs include `getFinalParameters`, protected synchronized `getProps`, `size`, `clear`, `writeXml` overloads, static `dumpConfiguration` overloads, `toString`, `setQuietMode`, `main`, `readFields`, and `write`.
- Tag APIs include `addTags(Properties)`, `getAllPropertiesByTag(String)`, `getAllPropertiesByTags(List)`, and `isPropertyTag(String)`. The class-level docs describe system/custom tags configured by `hadoop.tags.system` and `hadoop.tags.custom`.

### Crypto Key APIs

- `KeyProvider` is abstract, implements `Closeable`, and is constructed with a `Configuration`.
- Key lookup and metadata APIs include `getConf`, abstract `getKeyVersion(String)`, abstract `getKeys()`, concrete bulk `getKeysMetadata(String[])`, abstract `getKeyVersions(String)`, concrete `getCurrentKey(String)`, and abstract `getMetadata(String)`.
- Key lifecycle APIs include abstract `createKey(String, byte[], Options)`, concrete generated-material `createKey(String, Options)`, abstract `deleteKey(String)`, abstract `rollNewVersion(String, byte[])`, concrete generated-material `rollNewVersion(String)`, `invalidateCache(String)`, abstract `flush()`, and `close()`.
- Helper APIs include static `options(Configuration)`, `isTransient()`, protected `generateKey(int, String)`, static `getBaseName(String)`, protected static `buildVersionName(String, int)`, static `findProvider(List, String)`, `needsPassword()`, `noPasswordWarning()`, and `noPasswordError()`.
- Public constants include `DEFAULT_CIPHER_NAME`, `DEFAULT_CIPHER`, `DEFAULT_BITLENGTH_NAME`, `DEFAULT_BITLENGTH`, `JCEKS_KEY_SERIALFILTER_DEFAULT`, and `JCEKS_KEY_SERIAL_FILTER`.
- `KeyProviderFactory` is abstract, with abstract `createProvider(URI, Configuration)`, static `getProviders(Configuration)`, static `get(URI, Configuration)`, and `KEY_PROVIDER_PATH`.

### Filesystem APIs

- `AbstractFileSystem` has a constructor `(URI, String, boolean, int)` and protected `statistics`. Static factory/statistics APIs include `createFileSystem`, `getStatistics(URI)`, `clearStatistics`, `printStatistics`, `getAllStatistics`, and static `get(URI, Configuration)`.
- Path and identity helpers include `isValidName`, `checkScheme`, `getUriDefaultPort`, `getUri`, `checkPath`, `getUriPath`, `makeQualified`, `getInitialWorkingDirectory`, `getHomeDirectory`, `hashCode`, and `equals`.
- Server-default and metadata APIs include `getServerDefaults()` and `getServerDefaults(Path)`, `resolvePath`, `getFileStatus`, `getFileLinkStatus`, `getFileBlockLocations`, `getFsStatus(Path)`, abstract `getFsStatus()`, `getCanonicalServiceName`, `msync`, and `hasPathCapability`.
- File operations include final `create(Path, EnumSet, Options.CreateOpts...)`, abstract `createInternal(...)`, abstract `mkdir`, abstract `delete`, `open(Path)`, abstract `open(Path, int)`, `truncate`, abstract `setReplication`, final `rename(Path, Path, Options.Rename...)`, abstract no-overwrite `renameInternal(Path, Path)`, and overload `renameInternal(Path, Path, boolean)`.
- Link and namespace operations include `supportsSymlinks`, `createSymlink`, `getLinkTarget`, `setPermission`, `setOwner`, `setTimes`, `getFileChecksum`, `setVerifyChecksum`, and corrupt-block listing.
- Directory listing APIs include `listStatusIterator`, `listLocatedStatus`, abstract `listStatus`, and `listCorruptFileBlocks`.
- ACL APIs include `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, and `getAclStatus`.
- XAttr APIs include `setXAttr` overloads, `getXAttr`, `getXAttrs` overloads, `listXAttrs`, and `removeXAttr`.
- Snapshot and storage-policy APIs include `createSnapshot`, `renameSnapshot`, `deleteSnapshot`, `satisfyStoragePolicy`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, and `getAllStoragePolicies`.
- `AvroFSInput` wraps `FSDataInputStream` or `(FileContext, Path)` for Avro-style seekable input with `length`, `read`, `seek`, `tell`, and `close`.
- `BlockLocation` is `Serializable` and models hosts, cached hosts, IP/transfer names, topology paths, storage IDs, storage types, offset, length, and corruption state. Constructors cover default, copy, replicated layout, topology-aware layout, cached-host layout, and storage-type-aware layout. Getters/setters expose all block-location fields.
- `BlockStoragePolicySpi` defines storage policy name, preferred storage types, creation fallbacks, replication fallbacks, and copy-on-create/inherit-only behavior.
- `ByteBufferReadable.read(ByteBuffer)` reads into a `ByteBuffer`, advancing position but not limit on success, returning `-1` at EOF, and allowing `UnsupportedOperationException` for implementations that do not support the path.
- `CanSetDropBehind`, `CanSetReadahead`, and `CanUnbuffer` are opt-in stream capabilities for cache dropping, readahead tuning, and buffer/file-descriptor/socket release.
- `ChecksumException` extends `IOException` and stores a file position via `getPos()`.
- `ChecksumFileSystem` extends `FilterFileSystem`, wraps a raw filesystem, and exposes checksum-file naming, checksum length calculation, verify/write checksum toggles, open/create/append/truncate, permission/owner/ACL forwarding, replication, rename/delete/list, local-copy integration, checksum failure reporting, and capability masking.
- `CommonConfigurationKeysPublic` is a public constants holder for common `core-default.xml` keys and defaults: topology scripts, default FS, disk usage intervals, trash/protected directories, filesystem implementations, IO/mapfile/sequence-file/TFile settings, caller context, IPC/RPC settings, hash type, group mapping/cache settings, security/auth/Kerberos/SASL/token/crypto/key-provider/KMS settings, shell safety and missing-default-FS warnings, HTTP logs/idle timeout, credential-provider settings, sensitive config key patterns, Hadoop tags, and shutdown timeout. `HADOOP_SYSTEM_TAGS` and `HADOOP_CUSTOM_TAGS` are deprecated in favor of `HADOOP_TAGS_SYSTEM` and `HADOOP_TAGS_CUSTOM`.
- `ContentSummary` begins at the end of the chunk. The visible portion shows it extends `QuotaUsage`, implements `Writable`, has deprecated constructors superseded by `ContentSummary.Builder`, and exposes counters for length, snapshot length, directory count, snapshot directory count, file count, snapshot file count, and the start of `getSnapshotSpaceConsumed`.

## Control Flow

The XML has no executable runtime flow, but the API contracts imply several important paths.

`Configuration` construction decides whether default resources are loaded. Resources are added in order, later resources override earlier ones unless earlier values are final, and calls to getters trigger property lookup, deprecated-key alias resolution, variable expansion, and type conversion. Setting a deprecated key propagates values to replacement keys, while bulk deprecation additions replace the global deprecation context atomically. Reload operations invalidate/reload existing instances, and write/dump methods emit non-default or selected properties for persistence/debugging.

Configuration variable expansion searches the configuration first, then environment variables for `env.`-prefixed variables, then JVM system properties unless restricted. The class documentation also defines environment-default syntaxes like `${env.NAME:-default}` and `${env.NAME-default}`.

Password lookup flows through `getPassword`: it attempts credential-provider resolution first and conditionally falls back to clear-text configuration via `getPasswordFromConfig`. This makes credential provider configuration and clear-text fallback policy security-critical.

Key-provider callers discover providers through `KeyProviderFactory.getProviders(Configuration)` or `get(URI, Configuration)`, then operate through `KeyProvider`. Encryption uses `getCurrentKey` to pick a current key version, decryption uses `getKeyVersion`, and key rotation uses `rollNewVersion` followed by optional `invalidateCache` and required `flush` for durable backends. Generated-key overloads call `generateKey` before delegating to material-explicit abstract methods.

`AbstractFileSystem` callers generally reach implementations through static `get` or `FileContext`, validate scheme/authority with `checkPath`, qualify paths, then invoke abstract or default filesystem methods. Final convenience methods such as `create` and `rename` normalize options before delegating to implementation hooks (`createInternal`, `renameInternal`). The method docs repeatedly require fully qualified paths for this filesystem and absolute permissions after umask application.

Symlink-aware flows distinguish full path resolution (`resolvePath`) from partial target lookup (`getLinkTarget`) used by `FSLinkResolver`. Link status methods may throw `UnresolvedLinkException` for symlinks encountered before the final path component.

`ChecksumFileSystem` wraps a raw filesystem. Reads open both data and checksum state when verification is enabled; writes create checksum sidecar files; delete, rename, copy, and listing operations must hide or maintain checksum files consistently with raw files. `reportChecksumFailure` provides a retry signal after checksum mismatch handling.

## State and Persistence Behavior

This JDiff XML persists release API metadata only; Hadoop runtime state lives in the implementations represented by the signatures.

`Configuration` holds mutable in-memory properties, final-parameter markers, per-key source metadata, loaded resource references, quiet-mode and system-property restrictions, class loader state, and property tags. It can persist/restore via Hadoop `Writable` methods `write(DataOutput)` and `readFields(DataInput)`, and can export XML through `writeXml`. Static default resources and deprecation context are process-wide state that affects all configurations in the JVM.

Final parameters are durable when written in configuration XML resources and prevent later resources from overriding them. Source tracking is explicitly maintained so `getPropertySources` and dumps can identify command-line, programmatic, file, URL, or other origins. Allowing null-value properties is documented as testing-oriented state.

`KeyProvider` implementations may be transient or persistent. The contract distinguishes stores intended for long-term key storage from transient providers. `flush()` is the durability boundary for persistent stores, while `invalidateCache` lets providers refresh cached key metadata/material after rotation. Key version names encode basename plus version number using the documented `name@version` format.

`AbstractFileSystem` maintains `FileSystem.Statistics` for each filesystem instance and static statistics maps for schemes/URIs. Filesystem operation state is mostly external and durable in the backing namespace: files, directories, block metadata, permissions, owners, ACLs, xattrs, snapshots, storage policies, checksums, and symlinks. `msync` exists to synchronize client metadata state, especially for HA filesystems.

`BlockLocation` is serializable in the Java sense and carries mutable arrays for hosts, cached hosts, topology paths, storage IDs/types, plus offset/length/corrupt flags. It is a metadata snapshot for a file range, with different interpretation for replicated files and erasure-coded block groups.

`ChecksumFileSystem` persists checksum data in sidecar checksum files associated with raw data files. Its state includes verify/write checksum flags, bytes-per-checksum settings, raw filesystem delegation, and checksum-file naming/length conventions.

`ContentSummary` state is only partially visible here. The visible API indicates counters for normal and snapshot file/directory/length/space usage, inherited quota usage, and `Writable` persistence in later methods outside this chunk.

## Dependencies and Integration Points

The generated header shows the API was produced by Hadoop's `IncludePublicAnnotationsJDiffDoclet` with Java 8, Hadoop annotations, Guava, Commons libraries, Jetty/Jersey, Jackson, protobuf, Hadoop Auth, Curator/ZooKeeper, Kerby, Woodstox, and other build-time dependencies on the doclet classpath.

Runtime API dependencies in this chunk include Java `Iterable`, `Closeable`, `URI`, `URL`, `InputStream`, `Reader`, `Writer`, `DataInput`, `DataOutput`, `File`, `IOException`, `FileNotFoundException`, `Class`, `ClassLoader`, `InetSocketAddress`, `Pattern`, `TimeUnit`, `EnumSet`, `Collection`, `List`, `Map`, `Properties`, `ByteBuffer`, and security `NoSuchAlgorithmException`.

Hadoop integration points include:

- `org.apache.hadoop.io.Writable` for `Configuration` and `ContentSummary` serialization.
- `org.apache.hadoop.fs.Path`, `FileContext`, `FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `FsStatus`, `FsServerDefaults`, `RemoteIterator`, `FileChecksum`, `Options`, `CreateFlag`, `StorageType`, `BlockStoragePolicySpi`, and multiple filesystem exception types.
- `org.apache.hadoop.fs.permission.FsPermission`, `AclEntry`, and `AclStatus` for permission and ACL integration.
- `org.apache.hadoop.security.AccessControlException` for filesystem authorization failures.
- `org.apache.hadoop.crypto.key` nested types `KeyProvider.Options`, `KeyProvider.KeyVersion`, and `KeyProvider.Metadata`, which are referenced before their nested-class definitions appear in later XML lines.
- Credential-provider integration through `Configuration.getPassword` and key-provider path constants in `CommonConfigurationKeysPublic`.
- Avro integration through `AvroFSInput`, which adapts Hadoop streams to Avro's expected seekable input shape.
- `core-default.xml` integration through many `CommonConfigurationKeysPublic` constants and class-level references.

## Risks and Edge Cases

- This is a generated compatibility file. It does not show method bodies, default return values, serialized byte layout, exception messages, synchronization internals, or validation details beyond Javadocs and signature attributes.
- The chunk ends inside `ContentSummary`; any complete report must merge the next chunk before describing all content-summary formatting, quota, serialization, builder, and storage-type behavior.
- Configuration resource ordering and final parameters are easy to misuse. A final value in an earlier resource silently blocks later overrides, which can surprise applications adding resources late.
- Deprecation handling is global and process-wide. Adding deprecations after resources have loaded is documented as unsupported for several overloads, and aliasing multiple keys means setting any alias can reset the others.
- Variable expansion can read environment variables and system properties. Restriction flags and fallback/default syntax should be tested carefully to avoid leaking system properties or expanding unexpected values.
- Typed getters throw or default inconsistently by type: numeric invalid values can throw `NumberFormatException`, while boolean invalid values return the provided default. Callers need type-specific error policy.
- `getLongBytes`, time durations, and storage sizes rely on suffix parsing. Unit ambiguity, overflow, negative values, and default-unit handling are high-risk compatibility cases.
- `getPattern` explicitly does not trim returned values, unlike many string getters. This can make whitespace significant in regex configuration.
- Password fallback to clear-text configuration is security-sensitive. Provider errors, missing aliases, and fallback disablement must not accidentally expose or accept insecure credentials.
- `KeyProvider` implementations must be thread safe. Caches, key rotation, generated material, password prompts, and `flush` ordering are concurrency and durability risks.
- Key version parsing/building uses basename/version delimiters. Names containing unexpected delimiter characters or malformed version names can produce `IOException` or ambiguous behavior.
- `KeyProviderFactory.get(URI, Configuration)` returns null when no provider handles a URI scheme, so callers must not assume a provider is always returned.
- `AbstractFileSystem` methods often require fully qualified paths matching the filesystem scheme/authority. Passing slash-relative or wrong-scheme paths should be rejected consistently.
- Default implementations for operations such as truncate, symlinks, ACLs, xattrs, snapshots, and storage policies may throw unsupported-operation failures depending on concrete filesystems.
- `msync` is especially important for HA metadata consistency; clients that ignore unsupported or failed `msync` may see stale metadata.
- `ByteBufferReadable` states that buffer position/limit are undefined on exception. Robust callers need recovery paths after failed reads.
- `BlockLocation` array lengths for hosts, names, topology paths, storage IDs, and storage types must remain aligned. Erasure-coded block groups have different semantics than replicated block locations.
- `ChecksumFileSystem` must keep checksum sidecar files coherent during create, append, truncate, rename, delete, copy, ACL, and listing operations. Incoherence can create false checksum failures or stale sidecars.
- `CommonConfigurationKeysPublic` exposes many constants as public API, including deprecated tag constants and typo-containing Javadocs such as "Defalt"; compatibility checks must preserve field names even when docs are imperfect.

## Test Signals

Useful validation for this API surface should include:

- JDiff/API compatibility checks that assert all visible classes, interfaces, constructors, methods, fields, deprecation markers, checked exceptions, and visibility/final/static/synchronized attributes remain stable.
- `Configuration` tests for default resource loading on/off, clone behavior, resource precedence, final-parameter blocking, reload behavior, classpath/URL/Path/InputStream/Properties resource additions, and restricted parser paths.
- Configuration deprecation tests for single-key and multi-key aliases, custom messages, bulk atomic addition, setting old/new aliases, duplicate additions, `hasWarnedDeprecation`, and attempts to add deprecations after resources load.
- Variable expansion tests for config properties, `env.` variables, JVM system properties, restriction flags, `${env.NAME:-default}` versus `${env.NAME-default}`, recursion, missing variables, and cycles.
- Typed getter/setter tests for invalid numeric values, booleans, enum validation, time suffixes, storage-size suffixes, regex whitespace, comma splitting/trimming, ranges, null-value keys, source tracking, tags, and regex key matching.
- Password tests covering credential-provider hit/miss/error, clear-text fallback enabled/disabled, protected `getPasswordFromConfig`, and `IOException` propagation.
- Configuration persistence tests for `write`/`readFields`, `writeXml` selected/all properties, `dumpConfiguration` selected/all properties, final/source attributes, and sensitive-key redaction if implemented outside this signature slice.
- `Configured` tests for constructor-provided configuration, later `setConf`, null configuration, and subclass integration.
- `KeyProvider` contract tests for thread-safe concurrent reads/creates/rolls, generated key size/algorithm handling, create duplicate failures, delete missing/existing keys, current-key lookup, metadata bulk lookup, cache invalidation after roll, `flush` durability, transient-provider flag, password-needed warnings/errors, malformed version names, and factory behavior for unknown URI schemes.
- `AbstractFileSystem` tests for URI/scheme/path validation, qualification, statistics registration/clearing/printing, server defaults, create option normalization, permission after umask, rename overwrite and no-overwrite semantics, symlink resolution exceptions, file/link status differences, block-location ranges, corrupt-block iteration, and canonical service naming.
- Filesystem feature tests for ACL merge/remove/replace/status, xattr set/get/list/remove and namespace validation, snapshot create/rename/delete, storage policy set/unset/get/list/satisfy, capability probing, unsupported-operation behavior, and `msync` in HA-style clients.
- `AvroFSInput` tests for length, positional read, seek/tell, EOF, close behavior, and propagation of `FileContext`/stream exceptions.
- `BlockLocation` tests for constructor variants, copy isolation, array alignment, getters/setters with invalid host/name/topology inputs, corrupt flag, string rendering, cached-hosts/storage IDs/storage types, and replicated versus erasure-coded interpretation.
- Stream capability tests for `ByteBufferReadable` zero-length reads, EOF, buffer position advancement, exception recovery, unsupported operation, `CanSetDropBehind`, `CanSetReadahead`, and `CanUnbuffer`.
- `ChecksumFileSystem` tests for checksum-file name detection, checksum length math, bytes-per-sum, verify/write toggles, open/create/append/truncate with checksums, sidecar rename/delete/list hiding, local copy CRC behavior, checksum failure reporting, and blocked capabilities.
- Constants tests for `CommonConfigurationKeysPublic` field presence and value compatibility, especially deprecated `HADOOP_SYSTEM_TAGS`/`HADOOP_CUSTOM_TAGS`, security and credential keys, KMS cache/failover keys, IPC/RPC defaults, tag keys, and shutdown/HTTP/shell safety settings.

## Cross-Chunk Notes

This is the first chunk for `Apache_Hadoop_Common_3.2.4.xml`; no earlier chunk is needed for the header or `Configuration` start. The next chunk is required to complete `ContentSummary` and continue the `org.apache.hadoop.fs` package. Empty package markers for crypto, KMS, and random packages in this chunk should be preserved in merge output as package-level API presence even though they expose no public types here.

### subset-b-007199: lines 6122-12095

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.4.xml lines 6122-12095

## Purpose

This chunk is a JDiff-generated public API description for Apache Hadoop Common 3.2.4, not executable Java source. Its research value is the exported contract: class names, inheritance, implemented interfaces, method and constructor signatures, checked exceptions, field visibility, deprecation state, and embedded Javadoc. The span starts inside the tail of `org.apache.hadoop.fs.ContentSummary`, covers core `org.apache.hadoop.fs` creation/status/context/filesystem APIs, and ends inside the beginning of `org.apache.hadoop.fs.FileUtil`.

This is a central filesystem API slice. It documents both the older `FileSystem` abstraction and the newer `FileContext` abstraction, plus value objects and utilities that all Hadoop filesystems, HDFS clients, object stores, local filesystem code, command-line tools, and tests integrate with.

## API Inventory

### `org.apache.hadoop.fs.ContentSummary` tail

- The chunk begins after earlier `ContentSummary` declarations and includes output/formatting methods: `getErasureCodingPolicy()`, `equals(Object)`, `hashCode()`, static `getHeader(boolean)`, static `getHeaderFields()`, static `getQuotaHeaderFields()`, and multiple `toString(...)` overloads.
- The `toString` overloads format directory count, file count, content size, quotas, human-readable sizes, per-storage-type quotas, and snapshot-inclusion behavior. The five-argument overload `toString(boolean qOption, boolean hOption, boolean tOption, boolean xOption, List types)` is the complete formatter referenced by shorter overloads.
- This is a value/reporting object for content summary data; earlier fields and constructors are outside this chunk and must be reconciled with preceding chunks.

### `CreateFlag`

- `CreateFlag` is a public final enum describing file-create and append semantics.
- Static enum APIs are present: `values()` and `valueOf(String)`.
- Validation APIs are `validate(EnumSet flag)`, `validate(Object path, boolean pathExists, EnumSet flag)`, and `validateForAppend(EnumSet flag)`.
- Documented valid semantics include `CREATE`, `APPEND`, `OVERWRITE`, `CREATE|APPEND`, `CREATE|OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`.
- Invalid combinations include `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`, which raise `HadoopIllegalArgumentException`; create validation can also raise `IOException` for path-existence semantics.

### `FileAlreadyExistsException`

- `FileAlreadyExistsException` extends `java.io.IOException`.
- It has no-arg and message constructors.
- It is the create/rename-style failure used when a target already exists and overwrite behavior was not requested.

### `FileChecksum`

- `FileChecksum` is an abstract `Writable` value contract for file checksum implementations.
- Subclasses must implement `getAlgorithmName()`, `getLength()`, and `getBytes()`.
- The base API also exposes `getChecksumOpt()`, `equals(Object)`, and `hashCode()`.
- Equality is defined by checksum algorithm and checksum bytes. Serialization behavior is inherited from the `Writable` contract implemented by concrete subclasses.

### `FileContext`

- `FileContext` is a public facade implementing `PathCapabilities`. It is documented as the Unix-like per-process filesystem state analogue: default filesystem, working directory, user identity, and umask.
- Factory methods create contexts from an `AbstractFileSystem`, a default `URI`, a `Configuration`, the process default configuration, or the local filesystem. Unsupported default schemes raise `UnsupportedFileSystemException`; URI/config instantiation can raise runtime failures when a supported filesystem cannot be created or login fails.
- Path resolution and naming APIs include protected `getFSofPath(Path)`, `resolvePath(Path)`, `makeQualified(Path)`, `setWorkingDirectory(Path)`, `getWorkingDirectory()`, `getHomeDirectory()`, `getUgi()`, `getUMask()`, and `setUMask(FsPermission)`.
- Mutating namespace APIs include `create(Path, EnumSet, Options.CreateOpts...)`, `create(Path)` returning `FSDataOutputStreamBuilder`, `mkdir(Path, FsPermission, boolean)`, `delete(Path, boolean)`, `truncate(Path, long)`, `rename(Path, Path, Options.Rename...)`, `setReplication(Path, short)`, `setPermission(Path, FsPermission)`, `setOwner(Path, String, String)`, and `setTimes(Path, long, long)`.
- Data access APIs include `open(Path)`, `open(Path, int)`, `getFileChecksum(Path)`, `setVerifyChecksum(boolean)`, `getFileStatus(Path)`, `getFileLinkStatus(Path)`, `getLinkTarget(Path)`, `getFsStatus(Path)`, `listStatus(Path)`, `listLocatedStatus(Path)`, and `listCorruptFileBlocks(Path)`.
- Symlink and resolution helpers include `createSymlink(Path target, Path link, boolean createParent)`, `resolve(Path)`, and `resolveIntermediate(Path)`.
- Delete-on-exit and utility integration are exposed through `deleteOnExit(Path)` and `util()`.
- ACL APIs include `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, and `getAclStatus`.
- XAttr APIs include two `setXAttr` overloads, `getXAttr`, two `getXAttrs` overloads, `removeXAttr`, and `listXAttrs`. XAttr names must include a namespace prefix such as `user.attr`; returned xattrs are permission-filtered.
- Snapshot APIs include `createSnapshot(Path)`, `createSnapshot(Path, String)`, `renameSnapshot`, and `deleteSnapshot`.
- Storage policy APIs include `satisfyStoragePolicy`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, and `getAllStoragePolicies`.
- Capability/statistics APIs include `hasPathCapability(Path, String)`, static `getStatistics(URI)`, `clearStatistics()`, `printStatistics()`, and `getAllStatistics()`.
- Public fields include `LOG`, compatibility `DEFAULT_PERM`, preferred `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`.

### `FileStatus`

- `FileStatus` is a public client-side file metadata value object implementing `Writable`, `Comparable`, `Serializable`, and `ObjectInputValidation`.
- Constructors cover empty status, common file metadata, symlink-aware metadata, boolean attribute metadata, attribute-set metadata, and a copy constructor.
- Static `attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts ACL/encryption/erasure-coding/snapshot booleans into an attribute flag set. `NONE` is the shared empty attribute set.
- Accessors include length, file/directory/symlink classification, block size, replication, modification/access times, permission, ACL presence, encryption, erasure coding, snapshot-enabled flag, owner, group, path, and symlink target.
- Mutators are limited mostly to path/symlink plus protected normalization hooks for permission, owner, and group.
- Comparison, equality, and hash code are path-based. The `compareTo(Object)` overload is explicitly retained for binary compatibility after HADOOP-14683.
- `readFields(DataInput)` and `write(DataOutput)` are deprecated in favor of direct protobuf serialization through `PBHelper`; both document protobuf encoding. `validateObject()` supports Java serialization validation.
- `isDir()` is deprecated in favor of explicit `isFile()`, `isDirectory()`, and `isSymlink()`.

### `FileSystem`

- `FileSystem` is the abstract, configurable filesystem base class. It extends `Configured` and implements `java.io.Closeable`, `DelegationTokenIssuer`, and `PathCapabilities`.
- Static construction APIs include `get(Configuration)`, `get(URI, Configuration)`, `get(URI, Configuration, String user)`, `getLocal(Configuration)`, `newInstance(Configuration)`, `newInstance(URI, Configuration)`, `newInstance(URI, Configuration, String user)`, and `newInstanceLocal(Configuration)`.
- `get(URI, Configuration)` documents cache behavior: return an uncached new instance when `fs.$SCHEME.impl.disable.cache` is true, reuse a matching cached instance when available, or instantiate, initialize, cache, and return a new filesystem. `newInstance(...)` always returns a unique filesystem instance.
- URI/configuration APIs include `getDefaultUri`, two `setDefaultUri` overloads, `initialize(URI, Configuration)`, `getScheme()`, abstract `getUri()`, protected `getCanonicalUri()`, protected `canonicalizeUri(URI)`, protected `getDefaultPort()`, protected static `getFSofPath(Path, Configuration)`, `getCanonicalServiceName()`, deprecated `getName()`, deprecated `getNamed(String, Configuration)`, `makeQualified(Path)`, and protected `checkPath(Path)`.
- Core data and namespace APIs include many `create(...)` overloads, `primitiveCreate`, `primitiveMkdir`, `mkdirs(...)`, `createNonRecursive(...)`, `createNewFile`, `open(...)`, `append(...)`, `concat`, `rename(...)`, `truncate`, `delete(...)`, `deleteOnExit`, `cancelDeleteOnExit`, `processDeleteOnExit`, `exists`, `isDirectory`, `isFile`, `getLength`, `getFileStatus`, and `msync()`.
- Listing/search APIs include `listStatus(...)`, `listCorruptFileBlocks(Path)`, `globStatus(...)`, `listLocatedStatus(...)`, `listStatusIterator(Path)`, and recursive `listFiles(Path, boolean)`.
- File locality and server-default APIs include `getFileBlockLocations(...)`, `getServerDefaults()`, `getServerDefaults(Path)`, `getStatus()`, `getStatus(Path)`, `getUsed()`, `getUsed(Path)`, `getBlockSize(Path)`, `getDefaultBlockSize()`, `getDefaultBlockSize(Path)`, `getDefaultReplication()`, and `getDefaultReplication(Path)`.
- Local copy APIs include multiple `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, `moveToLocalFile`, `startLocalOutput`, and `completeLocalOutput`.
- Symlink APIs include `createSymlink`, `getFileLinkStatus`, `supportsSymlinks`, `getLinkTarget`, `resolveLink`, static `areSymlinksEnabled()`, and static `enableSymlinks()`.
- Checksum APIs include `getFileChecksum(Path)`, `getFileChecksum(Path, long)`, `setVerifyChecksum(boolean)`, and `setWriteChecksum(boolean)`.
- Metadata mutation includes `setReplication`, `setPermission`, `setOwner`, `setTimes`, quotas (`getContentSummary`, `getQuotaUsage`, `setQuota`, `setQuotaByStorageType`), snapshots, ACLs, xattrs, storage policy operations, trash roots, and path capabilities.
- Pluggability/statistics APIs include `getFileSystemClass(String, Configuration)`, deprecated global `getStatistics`/`getAllStatistics` APIs, `clearStatistics`, `printStatistics`, per-instance `getStorageStatistics()`, global `getGlobalStorageStatistics()`, `createFile(Path)` builder, and `appendFile(Path)` builder.
- Public/protected fields include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, widely used `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and protected per-filesystem `statistics`.

### `FileUtil` start

- The chunk begins `FileUtil`, a static local/remote filesystem utility class, but stops at the declaration of `createLocalTempFile(...)`; later chunks must complete the class.
- APIs in this slice include `stat2Paths(...)`, `fullyDeleteOnExit(File)`, `fullyDelete(File)`, `fullyDelete(File, boolean)`, `readLink(File)`, `fullyDeleteContents(File)`, `fullyDeleteContents(File, boolean)`, deprecated `fullyDelete(FileSystem, Path)`, multiple `copy(...)` overloads, `makeShellPath(...)`, `makeSecureShellPath(File)`, `getDU(File)`, `unZip(...)`, `unTar(...)`, `symLink(String, String)`, `chmod(...)`, `setOwner(File, String, String)`, platform-independent `setReadable`, `setWritable`, `setExecutable`, `canRead`, `canWrite`, `canExecute`, and `setPermission(File, FsPermission)`.
- The deletion APIs distinguish symlinks from normal directories: deleting a symlink deletes the link, not the linked file or directory. `fullyDeleteContents`, however, warns that when passed a symlink to a directory it deletes contents of the actual target directory.
- Shell/path APIs explicitly handle Windows subprocess issues and include a secure shell path variant intended to avoid script injection.

## Control Flow and Behavior

- `FileContext` operations resolve relative, slash-relative, and fully qualified `Path` values through its working directory and default `AbstractFileSystem`. Relative paths with a scheme are invalid. Once a target filesystem is selected, operations delegate to that `AbstractFileSystem`.
- `FileContext.create(Path)` returns a builder whose `build()` call performs parameter verification in `FileContext` and `AbstractFileSystem#create`, then mutates filesystem state by creating or overwriting the file.
- `FileSystem.get(...)` is the main cached factory path. It discovers/loads the implementation class for the scheme, initializes the filesystem, and reuses cached instances unless the per-scheme cache-disable key is set. `newInstance(...)` bypasses that cache path.
- `FileSystem.initialize(...)` is a subclass lifecycle hook. Implementations overriding it must call the superclass implementation before the instance is considered ready.
- `FileSystem` convenience methods layer on primitive filesystem operations. Examples in this chunk include recursive listing over `listStatus`/`listLocatedStatus`, delete-on-exit registration and later `processDeleteOnExit`, two-RPC permission-specific `create(FileSystem, Path, FsPermission)`, and local copy helpers delegating through `FileUtil`.
- `CreateFlag.validate(...)` centralizes create/append semantic checks before mutating calls are issued, preventing ambiguous append/overwrite combinations.
- `FileStatus` control flow is mostly value-object behavior: comparisons and equality use the path, while deprecated `Writable` serialization encodes/decodes a protobuf representation.
- `FileUtil` methods are procedural utilities around local filesystem mutation, shell command invocation, archive extraction, and cross-filesystem copy.

## State and Persistence

- The XML itself persists API metadata for compatibility comparison; it does not contain implementation bodies.
- `FileContext` stores client-side state: default filesystem, working directory, UGI, umask, delete-on-exit registrations, and statistics. It does not persist filesystem data directly, but its mutating APIs create, remove, or update remote/local filesystem namespace and metadata.
- `FileSystem` instances hold configuration-derived identity, URI, per-instance statistics, and possibly cached global lifecycle state. Static caches are observable through `get`, `newInstance`, `closeAll`, and `closeAllForUGI`.
- `FileSystem` mutating calls persist external filesystem effects: file contents, directories, metadata, ACLs, xattrs, quotas, snapshots, storage policies, trash roots, symlinks, and local-copy output.
- `FileStatus`, `ContentSummary`, and `FileChecksum` are serializable/reporting value objects. `FileStatus` has deprecated `Writable` protobuf serialization and Java object validation.
- `FileUtil` can persist destructive local changes via recursive deletion, permission/owner changes, symlink creation, archive extraction, and copy/delete-source operations.

## Dependencies and Integration Points

- Core dependencies are `org.apache.hadoop.conf.Configuration`, `org.apache.hadoop.fs.Path`, `AbstractFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `RemoteIterator`, `FileStatus`, `ContentSummary`, `QuotaUsage`, `FsStatus`, `BlockLocation`, `BlockStoragePolicySpi`, `StorageStatistics`, and `GlobalStorageStatistics`.
- Security integration includes `UserGroupInformation`, Hadoop `AccessControlException`, `DelegationTokenIssuer`, canonical service names for token caches, and permission/ACL classes under `org.apache.hadoop.fs.permission`.
- Error surfaces include `IOException`, `FileNotFoundException`, `FileAlreadyExistsException`, `ParentNotDirectoryException`, `UnsupportedFileSystemException`, `UnresolvedLinkException`, `InvalidObjectException`, RPC client/server exception families documented in Javadoc, and `UnsupportedOperationException` defaults for optional features.
- Pluggability flows through URI schemes, `ServiceLoader` discovery in `getFileSystemClass`, configuration keys such as `fs.defaultFS`/`FS_DEFAULT_NAME_KEY`, per-scheme cache disablement, and filesystem-specific implementations for HDFS, local filesystems, object stores, and third-party filesystems.
- Compatibility integration is broad: the `FileSystem.LOG` field is documented as widely used in `org.apache.hadoop.fs` code and tests, deprecated APIs remain for binary/source compatibility, and builder APIs are marked as temporarily reduced/stabilizing around HADOOP-14384.
- `FileUtil` integrates Java `File`, shell commands, permissions, archive streams, Hadoop `FileSystem`, and `Configuration`; behavior differs across Unix and Windows.

## Risks and Edge Cases

- This chunk is API metadata. It cannot prove implementation details beyond documented behavior; final research should reconcile this with Java source if implementation behavior is required.
- The chunk starts mid-`ContentSummary` and ends mid-`FileUtil`, so class-level conclusions for those two types are incomplete without adjacent chunks.
- `FileSystem` caching can cause lifecycle bugs when callers assume `get(...)` returns a fresh instance; `closeAll` and `closeAllForUGI` can invalidate shared cached instances.
- `FileContext` path resolution differs from Unix inode working directories: working directories are prefixed into relative paths and do not follow symlinks when set.
- Create semantics are subtle. Incorrect `CreateFlag` combinations or misuse of append/overwrite flags can cause unexpected `IOException` or `HadoopIllegalArgumentException`.
- Optional features such as ACLs, xattrs, snapshots, storage policies, symlinks, truncation, append, path handles, and capabilities may default to unsupported on some filesystems.
- Permission behavior has compatibility traps: `DEFAULT_PERM` historically gave files executable bits, so callers should prefer `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`.
- `FileStatus` equality and ordering by path can hide metadata differences when statuses for the same path differ in length, owner, ACL, encryption, or timestamps.
- Deprecated `FileStatus` `Writable` serialization and deprecated statistics APIs remain compatibility surfaces; tests should catch accidental removal or signature drift.
- `FileUtil.fullyDeleteContents` has a dangerous symlink-to-directory behavior documented in this chunk: it can delete target directory contents. Archive extraction and shell path helpers also need traversal and injection scrutiny.
- Windows-specific permission and symlink behavior differs from Unix, including `symLink` return code `2` for security-setting failure and folder execute-permission caveats.

## Test Signals

- API compatibility tests should compare JDiff output for method signatures, deprecation text, checked exceptions, implemented interfaces, and public fields for `FileContext`, `FileStatus`, `FileSystem`, and `FileUtil`.
- Factory/cache tests should cover `FileSystem.get`, `newInstance`, per-scheme cache-disable configuration, `closeAll`, and `closeAllForUGI`.
- Path-resolution tests should cover `FileContext` and `FileSystem` with fully qualified, slash-relative, working-directory-relative, illegal scheme-relative, symlink, and mount-point paths.
- Create/open/delete/rename/truncate tests should exercise `CreateFlag` validation, parent creation, overwrite/append combinations, recursive delete behavior, and cross-filesystem rename/error cases.
- Metadata tests should cover `FileStatus` path-based equality/comparison, protobuf serialization compatibility, attribute flags, deprecated `isDir()`, and `ObjectInputValidation`.
- Feature-surface tests should cover ACLs, xattrs, snapshots, quotas, storage policies, trash roots, symlinks, checksums, path capabilities, storage statistics, and unsupported-operation defaults across representative filesystems.
- Local utility tests should cover `FileUtil` recursive delete on normal files/directories and symlinks, copy with `deleteSource` and `overwrite`, shell path escaping, archive extraction, chmod/chown permission behavior, and platform-specific Windows branches.

### subset-b-007200: lines 12096-18157

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.4.xml lines 12096-18157

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.2.4. It starts inside the tail of `org.apache.hadoop.fs.FileUtil`, covers a broad run of `org.apache.hadoop.fs` public and protected APIs, includes the FTP filesystem package, the core `org.apache.hadoop.ha` high-availability interfaces, protocol-buffer bridge interfaces for HA/ZKFC RPC, and the beginning of `org.apache.hadoop.io` through the opening constructor of `DefaultStringifier`.

The source is generated compatibility metadata rather than implementation source. The relevant research surface is the release API contract: type names, inheritance, implemented interfaces, method signatures, checked exceptions, visibility, abstract/final/static attributes, deprecation markers, public/protected fields, and embedded Javadocs. Exact algorithms, private fields, and private helper flow must be validated in Java sources when implementation-level detail is required.

## Purpose

The `org.apache.hadoop.fs` portion defines Hadoop Common's filesystem abstraction boundary. It includes utility helpers (`FileUtil` tail), filesystem wrappers (`FilterFileSystem`), URI and scheme constants (`FsConstants`), stream contracts (`FSDataInputStream`, `FSDataOutputStream`, `FSInputStream`, `Seekable`, `PositionedReadable`, `Syncable`, `StreamCapabilities`), builder-style file creation (`FSDataOutputStreamBuilder`), path modeling (`Path`, `PathFilter`, `PathHandle`), local filesystem implementations (`LocalFileSystem`, `RawLocalFileSystem`), quota and storage accounting (`QuotaUsage`, `FsStatus`, `FsServerDefaults`, `StorageStatistics`, `GlobalStorageStatistics`, `StorageType`), trash policy plumbing, xattr conversion, and multipart upload handle types.

The `org.apache.hadoop.fs.ftp` portion exposes an FTP-backed `FileSystem` implementation built around Apache Commons Net. It maps Hadoop `FileSystem` operations onto FTP concepts and documents important limitations such as single-stream blocking and unsupported append.

The `org.apache.hadoop.ha` portion defines client-side and service-side contracts for Hadoop high availability. It covers health monitoring, state transitions to active/standby/observer, fencing method configuration and execution, HA target metadata, helper wrappers for RPC exception unwrapping, and typed exceptions for fencing, failover, health, and service transition failures.

The `org.apache.hadoop.io` portion starts the Writable ecosystem in this file segment. It documents map type registration support, writable arrays and primitive arrays, binary comparison, simple writable scalar types, byte-buffer pooling, compressed writable lazy inflation, and a `DataOutput` to `OutputStream` adapter.

## Important APIs, Types, and Functions

### File Utilities and Filesystem Wrappers

- `FileUtil` tail includes `createLocalTempFile(File, String, boolean)`, `replaceFile(File, File)`, checked wrappers for `File.listFiles()` and `File.list()`, `createJarWithClassPath(...)`, `getJarsInDirectory(...)`, `compareFs(FileSystem, FileSystem)`, and multiple `write(...)` overloads for `FileSystem` and `FileContext`. The write helpers cover raw `byte[]`, line iterables with explicit `Charset`, a single `CharSequence` with explicit charset, and UTF-8 defaults.
- `FileUtil.SYMLINK_NO_PRIVILEGE` remains public, indicating Windows or platform-specific symlink failure reporting is part of the API.
- `FilterFileSystem` extends `FileSystem` and delegates almost the whole filesystem surface to a wrapped `FileSystem` stored in protected field `fs`. It exposes constructors with and without a raw filesystem, `getRawFileSystem()`, URI/canonicalization hooks, path qualification/checking, open/create/append/concat/delete/rename/truncate/list/mkdir/status methods, local copy helpers, checksum toggles, symlink APIs, snapshots, ACLs, xattrs, storage policies, trash roots, builder factories, and `hasPathCapability`.
- `FilterFileSystem.swapScheme` is a protected field used by wrapper implementations that need to present a different scheme from the underlying filesystem.

### Core Filesystem Streams and Builders

- `FSDataInputStream` extends `DataInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `CanUnbuffer`, and `StreamCapabilities`. It exposes seeking, position reporting, positional `read` and `readFully`, source switching, byte-buffer reads via `ByteBufferPool`, buffer release, unbuffering, capability checks, file descriptor access, and readahead/drop-behind controls.
- `FSInputStream` is the lower-level abstract seekable positioned input stream. It declares `seek`, `getPos`, and `seekToNewSource`, provides positioned `read` and `readFully` helpers, and includes `validatePositionedReadArgs`.
- `FSDataOutputStream` extends `DataOutputStream` and implements `Syncable`, `CanSetDropBehind`, and `StreamCapabilities`. Constructors accept an `OutputStream`, filesystem statistics, and optional start position. Public methods expose `getPos`, `close`, `hflush`, `hsync`, drop-behind, capability checks, and `toString`.
- `FSDataOutputStreamBuilder<B,S>` is a fluent builder around file creation and append. It carries a `FileSystem`, `Path`, permission, buffer size, replication, block size, recursive flag, progress callback, create/overwrite/append flags, checksum options, optional and mandatory named options, and `build()` returning the stream type. Its `opt` and `must` overloads accept booleans, ints, floats, doubles, strings, and string arrays, so filesystem-specific options can be preserved as typed configuration keys and mandatory-key sets.
- `Syncable` defines `hflush()` and `hsync()` semantics. `StreamCapabilities` defines string capability names for `hflush`, `hsync`, `in:readahead`, `dropbehind`, and `in:unbuffer`. `StreamCapabilitiesPolicy.unbuffer(InputStream)` centralizes optional unbuffer dispatch and exposes a standard not-implemented message.

### Path, Handles, Status, and Filters

- `Path` models filesystem names as URI-like slash-separated paths. Constructors cover string parent/child combinations, `Path` parent/child combinations, raw strings, `URI`, and explicit scheme/authority/path triples. Static helpers strip scheme/authority, merge paths while preserving the first path scheme and authority, and detect Windows absolute paths.
- `Path` instance APIs expose URI conversion, filesystem resolution from `Configuration`, absolute/root/name/parent/depth queries, suffixing, string/equality/hash/ordering behavior, deprecated `makeQualified(FileSystem)`, and `validateObject()` to reject invalid deserialized paths. Public constants include `SEPARATOR`, `SEPARATOR_CHAR`, `CUR_DIR`, and host `WINDOWS`.
- `PathFilter.accept(Path)` is the simple predicate extension point used by listing/glob APIs. `GlobFilter` implements this contract using POSIX glob patterns with brace expansion and can compose a user filter.
- `PathHandle`, `PartHandle`, and `UploadHandle` are opaque serializable handle interfaces. Each exposes default `toByteArray()`, abstract `bytes()` returning a `ByteBuffer`, and `equals(Object)`. `PathHandle` references filesystem entities with optional validation metadata, while `PartHandle` and `UploadHandle` identify multipart upload parts and upload IDs.
- `InvalidPathException`, `InvalidPathHandleException`, and `ParentNotDirectoryException` define path-specific failures. `InvalidPathHandleException` is tied to path-handle constraints failing after filesystem mutation.
- `LocatedFileStatus` extends `FileStatus` with block locations. Constructors cover wrapping an existing status, explicit status fields, ACL/encryption/erasure-coded booleans, or generic `FileStatus.AttrFlags`. It exposes `getBlockLocations`, protected lazy `setBlockLocations`, and path-based comparison/equality/hash behavior.
- `Options` is a final grouping class for filesystem operation options. Nested option types are outside this chunk, but APIs in this segment reference `Options.HandleOpt` and `Options.ChecksumOpt`.

### Local, Raw Local, and FTP Filesystems

- `LocalFileSystem` extends `ChecksumFileSystem` and wraps a raw local filesystem. It exposes scheme `file`, `getRaw`, `pathToFile`, copy-to/from-local operations, checksum-failure quarantine via `reportChecksumFailure`, and symlink APIs.
- `RawLocalFileSystem` extends `FileSystem` and maps Hadoop paths directly to `java.io.File`. It exposes path conversion, URI initialization, open by path or `PathHandle`, append, create and non-recursive create variants, protected output-stream construction with permissions, concat, rename, truncate, delete, unsorted `listStatus`, mkdir helpers, working directory/home directory state, status, local-output staging, owner/permission/time mutation through platform commands, path handles, symlinks, and path capability checks.
- `ReadOption` is an enum marker for read behavior. `Seekable` defines `seek(long)` and `getPos()`.
- `FTPFileSystem` extends `FileSystem` with scheme `ftp`. It has initialization from URI/configuration, default port lookup, open/create/delete/list/status/mkdir/rename/working-directory/home-directory APIs, and config constants for user, host, port, password, data connection mode, and transfer mode. The create Javadoc warns that the returned stream must be closed before using other APIs or calls can block; append is documented as unsupported.
- `FTPException` wraps lower-level failures in an unchecked runtime exception.

### Capacity, Quota, Storage, and Trash

- `FsServerDefaults` is a `Writable` carrying default block size, checksum bytes, write packet size, replication, file buffer size, encryption-transfer flag, trash interval, checksum type, key provider URI, and default storage policy ID.
- `FsStatus` is a `Writable` with capacity, used, and remaining bytes.
- `QuotaUsage` stores namespace and space quota consumption plus per-`StorageType` quota/consumption. It has protected constructors/mutators for builder use, public getters, type-quota availability checks, equality/hash, formatted headers, human-readable and storage-type-aware string output, and protected formatting helpers.
- `GlobalStorageStatistics` is an enum singleton-style registry exposing `get(String)`, `put(String, StorageStatistics)`, `reset()`, and iteration over registered `StorageStatistics`.
- `StorageStatistics` is an abstract named statistics source with `getScheme`, iterator over long statistics, `getLong(String)`, `isTracked(String)`, and `reset`.
- `StorageType` is an enum with helper classification methods for transience, quota support, movability, list views, parser overloads, and public `DEFAULT` and `EMPTY_ARRAY` fields.
- `Trash` is a configured facade over `TrashPolicy`. It can move paths to the appropriate trash, check enablement, create checkpoints, expunge old or all checkpoints, return a superuser emptier `Runnable`, and resolve current trash directories per path.
- `TrashPolicy` is the abstract policy extension point. It supports deprecated home-directory initialization and newer initialization that avoids assuming `/user/$USER`, specifically to handle encryption-zone rename constraints. It defines enablement, move-to-trash, checkpoint create/delete, immediate delete, per-path trash directory resolution, emptier creation, factory methods keyed by `fs.trash.classname`, and protected state `fs`, `trash`, and `deletionInterval`.

### XAttrs and Unsupported Features

- `XAttrCodec` encodes and decodes xattr byte values for shell, HTTP, and JSON presentation. `decodeValue(String)` recognizes hex prefixes `0x`/`0X`, base64 prefixes `0s`/`0S`, quoted text, and unquoted text. `encodeValue(byte[], XAttrCodec)` emits quoted text, hex, or base64.
- `XAttrSetFlag.validate(String, boolean, EnumSet)` enforces create/replace semantics for xattr updates.
- `UnsupportedFileSystemException` and `UnsupportedMultipartUploaderException` are checked `IOException` subclasses used when a scheme lacks a filesystem or multipart uploader implementation.

### High Availability APIs

- `FenceMethod` defines operator-configured fencing implementations. `checkArgs(String)` validates configured arguments at startup, and `tryFence(HAServiceTarget, String)` attempts to stop another node from making progress, returning a boolean and allowing runtime configuration failure.
- `HAServiceProtocol` defines `monitorHealth`, `transitionToActive`, `transitionToStandby`, `transitionToObserver`, and `getServiceStatus`. Methods can throw service-specific failures, access control failures, and `IOException`. Public `versionID` documents the initial protocol version.
- `HAServiceProtocolHelper` wraps HA RPC calls and unwraps `RemoteException` into more specific exceptions for monitor and state transition operations.
- `HAServiceTarget` represents a target for HA admin commands. It supplies IPC address, optional health-monitor address, ZKFC address, fencer, preflight fencing validation, HA/ZKFC proxies with timeouts, desired transition target state, fencing parameters, auto-failover flag, and observer support flag. `addFencingParameters(Map)` documents how shell fencing receives entries as environment variables prefixed with `target_`.
- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` encode failure categories for HA control paths.
- `HAServiceProtocolPB` and `ZKFCProtocolPB` are protocol-buffer bridge interfaces that extend generated blocking service interfaces and `VersionedProtocol`, making protobuf RPC services part of the public compatibility surface.

### Writable and IO Types

- `AbstractMapWritable` implements `Writable` and `Configurable`, maintaining a class-to-byte-id registry for map-like writables. APIs include protected `addToMap(Class, byte)`, `getClass(byte)`, `getId(Class)`, `copy(Writable)`, configuration getters/setters, and serialization hooks.
- `ArrayFile` extends `MapFile`; this chunk only shows its constructor.
- `ArrayPrimitiveWritable` stores Java primitive arrays as a `Writable`, with constructors for no-arg read, declared component type, or initial array. It exposes the stored array, actual and declared component types, declared-type checks, mutation, and serialization.
- `ArrayWritable` stores arrays of `Writable` values with a declared value class. It exposes `getValueClass`, `toStrings`, `toArray`, `set`, `get`, and serialization.
- `BinaryComparable` is a base comparable over byte sequences. Subclasses provide `getLength` and `getBytes`; the class supplies byte-wise `compareTo`, equality, and hash behavior.
- `BloomMapFile` appears as a namespace class with public constants `BLOOM_FILE_NAME` and `HASH_COUNT`, plus a static `delete(FileSystem, String)` helper.
- `BooleanWritable`, `ByteWritable`, and `BytesWritable` are `WritableComparable` implementations for boolean, byte, and byte-array data. The scalar types expose constructors, set/get, read/write, equality/hash, comparison, and string conversion. `BytesWritable` extends `BinaryComparable`, distinguishes logical length from capacity, exposes backing-array and exact-copy access, deprecated `get()`/`getSize()` aliases, resizing and capacity changes, range-copy mutation, serialization, equality/hash, and hex string rendering.
- `ByteBufferPool` defines direct-buffer lifecycle methods `getBuffer(boolean direct, int length)` and `putBuffer(ByteBuffer)`.
- `org.apache.hadoop.io.Closeable` is deprecated in favor of `java.io.Closeable`.
- `CompressedWritable` is an abstract `Writable` base that stores compressed serialized bytes and lazily inflates fields. Final `readFields` and `write` wrap abstract protected `readFieldsCompressed` and `writeCompressed`; subclasses must call `ensureInflated()` before field access.
- `DataOutputOutputStream.constructOutputStream(DataOutput)` returns the original object if it is already an `OutputStream`, otherwise wraps a `DataOutput`. The adapter exposes `write(int)`, `write(byte[], int, int)`, and `write(byte[])`.
- The chunk ends at the beginning of `DefaultStringifier`, showing that it implements `Stringifier` and has a constructor taking `Configuration` and `Class`; the rest of that class is outside this range.

## Control Flow

The XML has no runtime control flow, but the API contracts imply several important execution paths.

Filesystem calls often flow from high-level `FileSystem` clients through wrappers. `FilterFileSystem` receives operations, applies wrapper path/URI behavior such as `swapScheme` or canonicalization, and delegates to its raw filesystem. Subclasses can override individual operations while leaving the rest of the surface delegated.

Stream reads flow through `FSDataInputStream` to an underlying stream that may implement optional interfaces. Seek and positioned reads are part of the stable contract; byte-buffer reads use `ByteBufferPool` and require explicit `releaseBuffer`; `unbuffer()` routes through capability policy so implementations that support releasing OS/socket buffers can do so without every caller hard-coding concrete stream types.

File creation flows through direct `FileSystem.create` overloads or through `FSDataOutputStreamBuilder`. Builder calls accumulate flags, permissions, buffering, replication, block sizing, checksums, progress callbacks, and optional/mandatory implementation-specific options. `build()` is the point where the configured filesystem interprets these settings and returns an output stream.

Path resolution flows from raw strings or URIs into normalized `Path` values, then into `getFileSystem(Configuration)` for scheme resolution. `PathHandle`-based reads add an extra validation flow: the handle bytes encode constraints, and opening with a stale or mismatched handle can raise `InvalidPathHandleException`.

Trash operations flow through `Trash` into a configured `TrashPolicy`. The newer policy methods take a deleted path when resolving the trash directory, which is important when HDFS encryption zones prevent rename across zone boundaries. Checkpoint and expunge APIs separate current trash movement from old-checkpoint cleanup.

HA control flow is health-monitor driven. A framework calls `monitorHealth`; unhealthy active services may trigger failover. Transition calls carry `StateChangeRequestInfo` and move services between active, standby, and observer states. If failover requires fencing, an `HAServiceTarget` supplies fencing configuration and parameters; configured `FenceMethod` implementations are checked at startup and tried in order at runtime.

Writable control flow follows Hadoop serialization conventions. `write(DataOutput)` emits durable type/value state, and `readFields(DataInput)` reconstructs mutable objects. `CompressedWritable` modifies this flow by reading compressed bytes first and delaying field materialization until `ensureInflated()` is called. `AbstractMapWritable` persists class/id mappings so heterogeneous writable maps can deserialize their entry types.

## State and Persistence Behavior

This JDiff file persists API metadata for compatibility checking. It does not persist Hadoop runtime state itself.

The APIs described here do manage or expose several kinds of runtime state. `FilterFileSystem` holds a wrapped filesystem and optional scheme substitution. `RawLocalFileSystem` and `FTPFileSystem` maintain URI, configuration, and working-directory state. `FSDataInputStream` and `FSDataOutputStream` track stream position and may update `FileSystem.Statistics`. Builder instances hold mutable pre-build option state.

`Path` is serializable and includes `validateObject()` to defend against invalid deserialized objects. `PathHandle`, `PartHandle`, and `UploadHandle` are explicit durable byte handles, but their contents are opaque and filesystem-defined. Their equality semantics are part of correctness because handles may be used as replayable references.

`FsServerDefaults`, `FsStatus`, `ArrayPrimitiveWritable`, `ArrayWritable`, `BooleanWritable`, `ByteWritable`, `BytesWritable`, `AbstractMapWritable`, and `CompressedWritable` use `Writable` serialization. Compatibility depends on stable field order, class-id mapping rules, byte ordering, capacity/length handling, and lazy compression behavior.

Quota and storage APIs expose snapshots of filesystem accounting state. `QuotaUsage` combines namespace count, namespace quota, disk space consumed, space quota, and per-storage-type quota/consumption. `StorageStatistics` and `GlobalStorageStatistics` expose mutable process-level counters that can be reset. `FsStatus` and `FsServerDefaults` carry filesystem-reported capacity/default snapshots.

Trash state is filesystem-resident: moving to trash renames or copies paths into policy-defined trash directories, checkpoint creation creates durable checkpoint directories, and expunge removes old or all checkpoints. Policy selection is configuration-driven through `fs.trash.classname`.

HA APIs are mostly remote-control contracts, but `HAServiceTarget` stores target state such as desired transition target status and exposes derived fencing parameter maps. The target addresses, fencer, and ZKFC proxy state integrate local admin clients with remote services.

## Dependencies and Integration Points

This chunk depends heavily on Java standard library APIs: `File`, `URI`, `IOException`, `AccessControlException`, `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `DataInputStream`, `DataOutputStream`, `FileDescriptor`, `ByteBuffer`, `Charset`, `Serializable`, `ObjectInputValidation`, collections, `EnumSet`, `Iterator`, and network socket addresses.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration`, `Configured`, and `Configurable` for filesystem initialization, trash policy setup, builder options, HA proxies, and writable configuration propagation.
- `org.apache.hadoop.fs.FileSystem`, `FileContext`, `FileStatus`, `BlockLocation`, `BlockStoragePolicySpi`, `RemoteIterator`, `CreateFlag`, `Options.ChecksumOpt`, `Options.HandleOpt`, and permission/ACL classes.
- Stream optional-capability interfaces such as `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, and `CanUnbuffer`.
- `org.apache.hadoop.util.Progressable` for create/append progress callbacks and `org.apache.hadoop.util.DataChecksum.Type` for server defaults.
- Hadoop security through `org.apache.hadoop.security.AccessControlException` in HA methods and owner/group/permission operations in local filesystems.
- HA support classes outside this chunk: `HAServiceStatus`, `HAServiceProtocol.StateChangeRequestInfo`, `HAServiceProtocol.HAServiceState`, `NodeFencer`, and `ZKFCProtocol`.
- Protocol-buffer generated services under `org.apache.hadoop.ha.proto.*` and IPC `VersionedProtocol`.
- Hadoop IO base interfaces `Writable`, `WritableComparable`, and `Stringifier`.
- Apache Commons Net for `FTPFileSystem`, as documented by the class Javadoc.
- SLF4J through `FTPFileSystem.LOG`.

## Risks and Edge Cases

- The chunk begins mid-method metadata in `FileUtil` and ends mid-class in `DefaultStringifier`; neighboring chunks are required for complete class-level reports.
- JDiff signatures do not show private implementation details. Behavior such as permission handling, atomic rename guarantees, path normalization edge cases, symlink support, trash checkpoint naming, and compressed byte layout require implementation-source validation.
- `FileUtil.createJarWithClassPath` must expand environment variables and wildcards before writing manifests. Platform differences are explicit: `%VAR%` on Windows, `$VAR` otherwise, and case-insensitive environment lookup on Windows.
- `FileUtil.listFiles` and `list` convert null-returning Java file APIs into checked exceptions or empty lists. Tests must distinguish invalid directory, unreadable directory, no entries, and I/O error.
- `FilterFileSystem` has a very wide delegation surface. Missing one overridden method can bypass wrapper policy for ACLs, xattrs, storage policies, snapshots, trash roots, path capabilities, or path handles.
- `FSDataInputStream` advertises thread-safe positioned reads through `PositionedReadable`, but the Javadocs warn that not all implementations satisfy the requirement. This matters for HBase-like consumers.
- Byte-buffer access requires callers to release buffers. Failure to call `releaseBuffer` can leak pooled direct buffers or pin resources.
- `StreamCapabilities.hasCapability` is string-keyed. Typos, case mismatches, or unsupported optional features can lead to false capability assumptions.
- `FSDataOutputStreamBuilder` separates optional and mandatory options. Filesystems must reject unknown mandatory keys but may ignore optional ones; incorrect handling can silently drop caller requirements.
- `Path` compatibility is sensitive to URI escaping, Windows drive parsing, root/relative handling, serialization validation, and deprecated `makeQualified(FileSystem)` behavior.
- `PathHandle`, `PartHandle`, and `UploadHandle` expose opaque bytes. Equality and byte-buffer immutability are important because callers may persist or compare handles across processes.
- `RawLocalFileSystem.listStatus` is explicitly unsorted because it relies on Java `File.list()`. Tests and callers must not assume deterministic order.
- Local owner and permission mutation shell out to platform commands such as `chown` and `chmod`; behavior varies by OS, privileges, and filesystem support.
- FTP streams can block other operations until closed. Append is unsupported despite being part of the inherited filesystem surface.
- Trash per-path resolution exists because encryption-zone renames can fail across zones. Older `getCurrentTrashDir()` without a path can be wrong in those deployments.
- HA transition and fencing methods are remote and operationally risky. Incorrect fencing configuration can allow split-brain, while over-aggressive fencing can stop healthy nodes.
- `HAServiceTarget.addFencingParameters` maps values into shell-fencing environments. Key normalization and untrusted values need careful handling by shell-based fencers.
- `AbstractMapWritable` uses byte IDs for classes. ID collisions or failure to persist mappings correctly can corrupt heterogeneous map deserialization.
- `BytesWritable.getBytes()` exposes the backing array, and only the range `0..getLength()-1` is valid data. Callers that serialize or compare full capacity can read stale bytes.
- `BytesWritable` preserves old deprecated aliases `get()` and `getSize()` for compatibility; removing them would break existing consumers.
- `CompressedWritable` subclasses must call `ensureInflated()` before field access. Omitting that in accessors can expose uninitialized/default fields after deserialization.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks that all classes, interfaces, fields, overloads, visibility, exceptions, and deprecation markers in this chunk remain stable for Hadoop Common 3.2.4 compatibility.
- `FileUtil` tests for temp-file creation and delete-on-exit flagging, replacement failure modes, `list`/`listFiles` null-to-exception behavior, classpath jar manifest creation with Windows and Unix environment expansion, wildcard jar expansion, and all `write` overloads for `FileSystem` and `FileContext`.
- `FilterFileSystem` delegation tests covering ordinary file operations plus less common surfaces: ACLs, xattrs, snapshots, storage policies, symlinks, path handles, trash roots, builder factories, checksums, and path capability queries.
- Stream tests for seek/getPos, positioned read argument validation, `readFully` EOF behavior, byte-buffer read/release, unbuffer dispatch, readahead/drop-behind pass-through, hflush/hsync, capability strings, close semantics, and statistics position updates.
- Builder tests for fluent self-type returns, default values, create/overwrite/append flag combinations, checksum options, optional versus mandatory option storage, typed option serialization into `Configuration`, and filesystem rejection of unknown mandatory options.
- `Path` tests for construction from strings/URIs/components, parent-child resolution, normalization, Windows absolute parsing, scheme/authority stripping, merge semantics, `getFileSystem`, parent/name/root/depth queries, equality/order/hash, serialization validation, and deprecated qualification compatibility.
- Handle tests for `PathHandle`, `PartHandle`, and `UploadHandle` byte serialization, equality, immutability expectations, stale-handle rejection, and multipart upload resume behavior where supported.
- Local filesystem tests for raw path conversion, unsorted listing tolerance, create/append/truncate/rename/delete semantics, recursive delete failures, mkdir permission application, symlink create/status/target, owner/permission/time mutation, path capabilities, checksum failure quarantine, and Windows empty-directory rename handling.
- FTP tests with a controlled FTP server for initialization from config, authentication, open/create blocking until close, unsupported append, delete/list/status/mkdir/rename semantics, working directory handling, data connection mode, transfer mode, and default port logic.
- Quota/storage tests for `QuotaUsage` builder-derived values, per-storage-type quota/consumption, formatted headers, human-readable output, equality/hash, `FsStatus` and `FsServerDefaults` writable round trips, storage-type parsing/classification, and statistics registry reset/iteration.
- Trash tests for enabled/disabled policy behavior, move-to-trash return values for already-in-trash paths, checkpoint creation, old checkpoint deletion, immediate expunge, emptier runnable behavior, factory class loading, and encryption-zone-aware per-path trash locations.
- XAttr tests for hex/base64/quoted/unquoted decode, encode prefixes, invalid input exceptions, create/replace validation, and null or empty values.
- HA tests for health monitor exceptions, active/standby/observer transition no-op behavior when already in state, access-control propagation, helper unwrapping of remote exceptions, fencer argument validation, ordered fencing success/failure behavior, fencing parameter environment mapping, optional health-monitor address routing, ZKFC proxy creation, auto-failover flag, and observer support flag.
- Writable tests for golden serialized bytes and round trips for `ArrayPrimitiveWritable`, `ArrayWritable`, `BooleanWritable`, `ByteWritable`, `BytesWritable`, `FsStatus`, `FsServerDefaults`, and `AbstractMapWritable`; include class-id registry preservation, backing-array versus logical-length behavior, byte-wise comparison, and compressed lazy inflation.
- `ByteBufferPool` tests for direct/non-direct requests, minimum capacity handling, reuse after `putBuffer`, and robustness against caller-mutated buffer position/limit.
- `DataOutputOutputStream` tests for returning an existing `OutputStream` unchanged, wrapping plain `DataOutput`, and correct byte forwarding for single-byte and array writes.

## Cross-Chunk Notes

The preceding chunk is required to complete `FileUtil`; this chunk starts after the method name for `createLocalTempFile` has already appeared. The following chunk is required to complete `DefaultStringifier` and the rest of `org.apache.hadoop.io`. The merge lane should preserve this document as the line-range-specific research note and synthesize final per-file conclusions only after all chunks for `Apache_Hadoop_Common_3.2.4.xml` are available.

### subset-b-007201: lines 18158-24453

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.4.xml lines 18158-24453

## Scope And Purpose

This chunk is a JDiff public API slice for Hadoop Common 3.2.4. It is not runtime implementation code; it is an XML description of exported Java packages, classes, interfaces, fields, method signatures, deprecation status, exceptions, and embedded Javadocs. The covered range starts in the tail of `org.apache.hadoop.io.DefaultStringifier`, spans most of the public `org.apache.hadoop.io` serialization and file-container API surface, covers `org.apache.hadoop.io.compress`, includes `org.apache.hadoop.io.erasurecode.ECSchema`, and begins the `org.apache.hadoop.io.file.tfile` APIs through the start of `Utils.upperBound`.

The main purpose of this slice is API compatibility documentation. Downstream checks can compare these signatures and docs against other Hadoop versions to detect binary/source compatibility changes in writable serialization, SequenceFile/MapFile/TFile containers, compression codec plumbing, and erasure-coding schema configuration.

## API Surface Covered

The chunk covers these package regions:

- `org.apache.hadoop.io`: `DefaultStringifier` tail, primitive writable wrappers, map and sorted-map writables, object and generic writables, raw comparators, sequence/map/set files, UTF-8 `Text`, versioned writable support, writable factories, and writable utility methods.
- `org.apache.hadoop.io.compress`: block and stream compressor/decompressor streams, concrete codecs for bzip2/default/gzip, codec constants, codec discovery and pooling, compression/decompression interfaces, direct decompression interfaces, and splittable compression contracts.
- `org.apache.hadoop.io.erasurecode`: immutable public `ECSchema` configuration holder.
- Empty package markers for `org.apache.hadoop.io.erasurecode.coder.util` and `org.apache.hadoop.io.erasurecode.grouper`.
- `org.apache.hadoop.io.file.tfile`: TFile metadata exceptions, raw byte-range comparison interface, top-level `TFile` constants and helpers, and `Utils` variable-length integer/string helpers. The chunk stops inside the `upperBound` method declaration, so the remainder of that method and following TFile utility APIs are cross-chunk dependencies.

## Important Types And APIs

The writable primitive wrappers `DoubleWritable`, `FloatWritable`, `IntWritable`, `LongWritable`, `ShortWritable`, `VIntWritable`, and `VLongWritable` expose the standard Hadoop `WritableComparable` pattern: default and value constructors, `set`, `get`, `readFields(DataInput)`, `write(DataOutput)`, equality, hash code, comparison, and `toString`. Fixed-width wrappers serialize Java primitive values directly, while `VIntWritable` and `VLongWritable` use Hadoop variable-length integer encoding to reduce storage for small values.

`DefaultStringifier<T>` bridges Hadoop `Serialization` to string form using base64-encoded serialized object bytes. Its static helpers store/load single objects and arrays in `Configuration` keys. Empty arrays are explicitly risky because `storeArray` documents `IndexOutOfBoundsException` when the array is empty.

`ElasticByteBufferPool` is a synchronized `ByteBufferPool` implementation that returns either direct or heap buffers and caches released buffers. Its documented policy is simple and unbounded: return the smallest cached buffer with at least the requested capacity and do not enforce a maximum cache size.

`EnumSetWritable<E>` wraps nullable or empty `EnumSet`s while preserving element type when required. It implements both `Writable` and `Configurable`; constructors and `set` require a non-null `elementType` when the value is null or empty. This makes type metadata part of the serialized state contract.

`GenericWritable` is an abstract configurable polymorphic wrapper for a bounded set of writable implementation classes. Subclasses must return a constant `Class[]` from `getTypes()`. `ObjectWritable` is a broader polymorphic wrapper that writes an instance with its class name and supports arrays, strings, primitives, and regular `Writable`s. `WritableFactories` and `WritableFactory` let non-public writable classes be constructed by factory rather than public zero-argument constructor, which matters for `ObjectWritable` deserialization.

`MapWritable` and `SortedMapWritable` adapt Java `Map` and `SortedMap` APIs to writable key/value serialization through `AbstractMapWritable`. Both expose collection views and standard mutation methods plus `readFields`/`write`. `SortedMapWritable` adds `comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, and `tailMap`.

`NullWritable` is a singleton writable comparable for empty keys or values. Its `readFields` and `write` are intentionally no-op, while `get()` returns the singleton instance.

`MD5Hash` is a 16-byte writable comparable digest value. It supports construction from hex string or byte array, static digest helpers for byte arrays, byte-array slices, byte-array arrays, strings, `UTF8`, and `InputStream`, thread-local `MessageDigest` creation, half and quarter digest projections, binary serialization, and hex parsing through `setDigest`.

`MultipleIOException` aggregates multiple `IOException`s and provides `createIOException(List)`, allowing cleanup or batch operations to surface several failures as one checked exception.

`Writable` and `WritableComparable` define the core serialization contract. `Writable.readFields` emphasizes storage reuse on deserialization, and `WritableComparable` documents the distributed-systems requirement that `hashCode()` be stable across JVM instances because Hadoop uses it for key partitioning.

`RawComparator<T>` compares serialized byte slices directly. `WritableComparator` implements the default object-based and byte-slice comparison path, allows registration of thread-safe optimized comparators via `define`, creates key instances, and exposes byte parsing helpers such as `compareBytes`, `hashBytes`, `readInt`, `readLong`, `readDouble`, `readVLong`, and `readVInt`.

`WritableUtils` groups serialization helpers: compressed byte arrays/strings/string arrays, plain string arrays, byte-array display, writable clone/cloneInto, zero-compressed `writeVInt`/`writeVLong` and `readVInt`/`readVLong`, range-checked VInt reads, VInt sign/size helpers, enum read/write as string, fully skipping a `DataInput`, conversion of writables to a byte array, and `readStringSafely` with maximum encoded-size validation.

`IOUtils` exposes stream and file utility methods: several `copyBytes` overloads, compressed-data read wrapper, `readFully`, `skipFully`, cleanup/close helpers, socket close, channel write loops, directory listing that preserves IO errors, file/channel `fsync`, exception wrapping with path and method diagnostics, and `readFullyToByteArray`. The older `cleanup(Log, Closeable...)` overload is deprecated in favor of SLF4J `cleanupWithLogger`.

`MapFile`, `SetFile`, and `SequenceFile` are file-container APIs. `MapFile` is a directory with `data` and `index` files and exposes `rename`, `delete`, and index repair through `fix`. `SetFile` is a key-only specialization of `MapFile`. `SequenceFile` documents binary key/value flat files with uncompressed, record-compressed, and block-compressed formats, a common header, sync markers, metadata, compression codec selection, default compression type helpers, many legacy `createWriter` overloads, a modern `createWriter(Configuration, Writer.Option...)`, and `SYNC_INTERVAL`.

`Text` is Hadoop's mutable UTF-8 byte sequence. It supports raw byte access, exact byte copying, byte length, scalar-codepoint traversal without creating a `String`, substring search, multiple setters from string/text/byte ranges, append, clear, bounded and unbounded deserialization/serialization, UTF-8 encode/decode helpers with optional replacement, static read/write string helpers with maximum-length variants, UTF-8 validation, codepoint extraction from `ByteBuffer`, and encoded-length computation.

`TwoDArrayWritable` serializes a matrix of writable instances for a configured element class. `VersionedWritable` prefixes writable data with a version byte and throws `VersionMismatchException` when input version does not match `getVersion()`, giving evolving writable classes an explicit compatibility hook.

## Compression APIs And Integration

The compression package defines a layered streaming model:

- `CompressionCodec` creates compression/decompression streams, compressor/decompressor instances, advertises required implementation classes, and returns the default extension.
- `Compressor` and `Decompressor` are state-machine interfaces modeled after `Deflater` and `Inflater`. They use `setInput`, `needsInput`, optional dictionaries, byte counters or remaining-byte reporting, finish/finished/reset/end, and `compress` or `decompress` calls.
- `CompressionOutputStream` and `CompressionInputStream` are abstract stream wrappers. Output streams must implement `write(byte[], int, int)`, `finish`, and `resetState`; input streams expose reset-state behavior and position/seek-related methods.
- `CompressorStream`, `BlockCompressorStream`, `DecompressorStream`, and `BlockDecompressorStream` provide stream wrappers around those state machines. Block streams write or read length-prefixed compressed blocks and are intended for block-oriented algorithms.
- `DirectDecompressionCodec` and `DirectDecompressor` add direct `ByteBuffer` decompression for codecs that can bypass heap-copy flows.
- `SplittableCompressionCodec` and `SplitCompressionInputStream` define compressed-input range reading. Codecs may adjust requested start/end offsets to block boundaries, which is central to parallel processing of compressed Hadoop inputs.

Concrete/public codec entries in this range include `BZip2Codec`, `DefaultCodec`, and `GzipCodec`. `BZip2Codec` is configurable and splittable; its docs state that it can use a native bzip2 library or a pure-Java implementation, that pure-Java mode does not implement `Compressor`/`Decompressor` methods with explicit compressor/decompressor arguments, and that splittability is available only in pure-Java mode. `DefaultCodec` implements direct decompression in addition to normal codec creation, and `GzipCodec` specializes default behavior for gzip.

`CodecConstants` lists standard filename extensions for default, bzip2, gzip, LZ4, Snappy, and Zstandard codecs. `CodecPool` is a global pool for reusing possibly native compressor/decompressor instances and exposes leased-instance counts. `CompressionCodecFactory` discovers codecs through `io.compression.codecs` and Java `ServiceLoader`, resolves codecs by file suffix, class name, or case-insensitive alias, removes suffixes, and has a diagnostic `main`.

## TFile And Erasure Coding APIs

`ECSchema` is a final serializable value object for erasure coding schema data. It can be built from a full options map or from codec name, data unit count, parity unit count, and optional extra options. Public constants identify the option keys for codec name, number of data units, and number of parity units. Equality, hash code, and string output are part of the public surface, so schema identity and logging representations are compatibility-sensitive.

`MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are checked TFile metadata exceptions. `RawComparable` describes a byte array, offset, and size triple used with external raw comparators. The docs explicitly put semantic compatibility responsibility on applications: two raw comparables must be compared with a comparator that understands both byte ranges.

`TFile` is a byte-oriented key/value container. It supports type-less keys and values, 64 KB key limit, unrestricted value length in practice, block compression, named metadata blocks, sorted or unsorted keys, and seeking by key or file offset. Public constants name compression algorithms (`gz`, `lzo`, `none`) and comparator naming conventions (`memcmp`, Java class comparator prefix). `makeComparator` builds raw comparators from names, `getSupportedCompressionAlgorithms` returns accepted compression algorithm names, and `main` dumps TFile information.

TFile's embedded docs are unusually operational. They document memory footprint from per-block codecs, temporary key/value buffering, data-block index cost as `(56 + AvgKeySize) * NumBlocks`, and metadata-block index cost as `(40 + AvgMetaBlockName) * NumMetaBlock`. Configuration knobs include `tfile.io.chunk.size`, `tfile.fs.output.buffer.size`, and `tfile.fs.input.buffer.size`. Performance guidance weighs block size, sequential versus random reads, compression ratios, gzip CPU cost relative to LZO, and the lack of true multithreaded reading when scanners share one `FSDataInputStream`.

`org.apache.hadoop.io.file.tfile.Utils` in this chunk exposes TFile-specific variable-length integer/string helpers. Its `writeVInt` delegates conceptually to `writeVLong`; `writeVLong` documents a different encoding family from `WritableUtils`, using first-byte ranges for 1 to 9 byte signed encodings. `readVInt`, `readVLong`, `writeString`, `readString`, and `lowerBound` are fully visible. The chunk ends at the `upperBound` declaration before its parameters and docs are complete.

## Control Flow And Data Flow

The XML itself has no executable control flow beyond the sequence of JDiff declarations. The documented runtime flows are these:

- Writable serialization is symmetrical: constructors or factory-created instances are populated by `readFields(DataInput)` after data was produced by `write(DataOutput)`. Mutable implementations are expected to reuse storage on reads where possible.
- Polymorphic serialization flows through `GenericWritable` type tables, `ObjectWritable` class-name records, and `WritableFactories` for non-public classes. Deserialization therefore depends on class availability, configuration, and factory registration.
- Raw comparison flows either deserialize two writable values and call natural ordering, or optimized comparators compare serialized byte slices directly. `WritableComparator.define` changes the comparator selected for a key class globally.
- SequenceFile writer creation flows through either a modern option-list API or many legacy overloads that choose filesystem, path or output stream, key/value classes, compression type, codec, progress, metadata, replication, block size, and create flags. Readers are documented as format bridges across uncompressed, record-compressed, and block-compressed files.
- Compression streams repeatedly accept input, check `needsInput`, compress/decompress into caller buffers, and finish/reset/end codec state. Codec pools lease and return compressor state; failure to return instances changes memory/native-resource behavior.
- Splittable compression flows from a seekable compressed stream and requested compressed offsets to adjusted block-aligned offsets and a `SplitCompressionInputStream` that reports positions according to the read mode.
- TFile lookup and scan behavior depends on block indexes, meta-block indexes, comparator choice, compression algorithm, and shared stream seek/read sequencing.

## State And Persistence Behavior

The JDiff XML persists API metadata only. The APIs it describes are deeply stateful:

- Writable instances hold mutable field state and serialize it to `DataOutput`; callers must keep read/write order stable across versions.
- `DefaultStringifier.store/load` persists serialized objects or arrays into Hadoop `Configuration` entries, so configuration becomes a transport/storage layer for object state.
- `ElasticByteBufferPool`, `CodecPool`, `WritableComparator` registrations, `WritableFactories`, and thread-local `MD5Hash` digesters are process-level state caches or registries.
- `IOUtils.copyBytes`, `fsync`, `listDirectory`, and close helpers touch files, sockets, channels, and streams. `fsync` is a durability boundary and has platform-specific behavior for directories.
- `MapFile` persists data and index files in a directory; `fix` can recreate an index and can run as a dry run. `SequenceFile` persists binary records, headers, sync markers, compression metadata, and user metadata. `TFile` persists compressed data blocks, metadata blocks, indexes, and comparator/compression settings.
- Compressor and decompressor instances have lifecycle state: input buffers, dictionaries, counters, finished flags, remaining compressed bytes, reset state, and native resources released by `end`.
- `ECSchema` carries erasure-code layout state that integrates with higher-level HDFS erasure-coding policy logic outside this chunk.

## Dependencies And Integration Points

This API slice depends on core Java I/O and NIO (`DataInput`, `DataOutput`, streams, channels, `ByteBuffer`, `FileChannel`), collections, reflection/class loading, `MessageDigest`, and character-coding APIs. Hadoop dependencies include `Configuration`, `Configurable`, `FileSystem`, `FileContext`, `Path`, `Options.CreateOpts`, `Progressable`, `SerializationFactory` and serialization interfaces, `ByteBufferPool`, `BinaryComparable`, `UTF8`, `AbstractMapWritable`, and compression implementation classes outside this XML slice.

Integration points include MapReduce key/value serialization and partitioning, SequenceFile and MapFile data exchange, TFile readers/writers, HDFS and other `FileSystem` implementations, native compression libraries, Java `ServiceLoader` codec discovery, job configuration properties such as default SequenceFile compression type and `io.compression.codecs`, and erasure-code schema consumers.

Because this is a public API report, source and binary compatibility are central integration concerns. Method overloads marked deprecated still appear in the public contract and may be used by older callers. Comparator encodings, writable byte formats, SequenceFile headers, TFile variable-length integer formats, and codec aliases are storage-format or wire-format contracts rather than ordinary helper details.

## Risks And Edge Cases

- The range begins mid-`DefaultStringifier` and ends mid-`Utils.upperBound`; final analysis for those two classes needs adjacent chunk reconciliation.
- Serialization compatibility is fragile. Changing field order, VInt encoding, `Text` length bounds, or class names used by `ObjectWritable` can break persisted data and distributed RPC/data exchange.
- `WritableComparable.hashCode()` must be stable across JVM processes. Implementations using identity-based or randomized hash behavior can corrupt partitioning behavior.
- `WritableComparator.define` requires thread-safe comparators but does not encode enforcement in the signature. A non-thread-safe raw comparator can cause sort/group instability under parallel use.
- `ElasticByteBufferPool` documents no maximum cache size. Long-running processes can retain large direct or heap buffers if workload sizes spike.
- `CodecPool` requires disciplined return of compressors/decompressors. Missing returns leak pooled/native resources and distort leased-count diagnostics.
- `BZip2Codec` behavior changes by native versus pure-Java mode: splittability forces pure-Java, while compressor/decompressor-argument methods can throw `UnsupportedOperationException` in pure-Java mode.
- `Decompressor.setInput` requires input buffers to remain unmodified until `needsInput()` permits modification. Violating this can produce data corruption without a type-system signal.
- `IOUtils.cleanup*` intentionally ignores `Throwable`, which is appropriate for exception cleanup but risky if used on the main success path.
- `IOUtils.readFullyToByteArray` warns that infinite `DataInput` never returns; callers need bounded input when reading untrusted or streaming data.
- `Text.getBytes()` returns the backing array, not an exact-length copy. Callers must honor `getLength()` or use `copyBytes()` to avoid stale trailing data.
- `MapFile` indexes are read entirely into memory and key implementations should stay small. Large keys or many index entries increase heap pressure.
- TFile shared-stream reads are documented as effectively sequential even with multiple scanners, which can surprise callers expecting parallel random access.
- TFile compression choices affect CPU and random-access behavior; large blocks help sequential reads but hurt random access and index memory tradeoffs.
- `ECSchema` constructors from maps depend on required option names and value validity; invalid unit counts or missing options are likely handled in implementation outside this XML but should be validated by consumers.

## Test Signals

Useful validation for this chunk includes:

- JDiff/XML parsing checks that every visible class, interface, method, field, deprecation flag, exception, and package boundary is well-formed; include boundary tests for this chunk's partial start/end classes.
- Serialization round-trip tests for all primitive writables, `EnumSetWritable` including null and empty sets with element type, `MapWritable`, `SortedMapWritable`, `TwoDArrayWritable`, `VersionedWritable`, `ObjectWritable`, and `GenericWritable` subclasses.
- Compatibility tests for `WritableUtils` VInt/VLong sizes, sign handling, range validation, enum string encoding, safe string maximum lengths, and TFile `Utils` variable-length integer/string encodings.
- Comparator tests for object comparison versus raw byte-slice comparison, optimized comparator registration, stable `hashBytes`, and byte parsing helpers.
- `Text` tests for malformed UTF-8 replacement versus exception behavior, maximum-length read/write enforcement, `charAt` on invalid positions/trailing bytes, `find`, append, clear, backing-array length semantics, and codepoint traversal.
- File-container tests for SequenceFile writer overloads, default compression configuration, metadata persistence, sync interval behavior, uncompressed/record-compressed/block-compressed read interoperability, MapFile rename/delete/fix dry-run and repair behavior, and SetFile key-only semantics.
- IO utility tests for short reads/writes, EOF behavior in `readFully` and `skipFully`, close cleanup swallowing behavior, `wrapException` preserving important exception types, directory listing IO failures, and file/channel `fsync` behavior across supported platforms.
- Compression tests for codec factory discovery by config and `ServiceLoader`, suffix and alias lookup, codec pool lease/return counters, compressor/decompressor reset and finish state, direct `ByteBuffer` decompression, concatenated streams via `getRemaining`, and splittable bzip2 adjusted offsets.
- TFile tests for supported compression names, comparator name parsing, metadata-block duplicate/missing exceptions, sorted and unsorted key behavior, seek-by-key and seek-by-offset, block-size and chunk-size configuration, index memory scaling, and concurrent scanner behavior over a shared reader.
- Erasure-code schema tests for constructors from maps and explicit arguments, extra-option preservation, equality/hash-code stability, and string output suitable for logs.

### subset-b-007202: lines 24454-30679

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.4.xml lines 24454-30679

## Scope And Purpose

This chunk is part of Hadoop Common 3.2.4's JDiff API descriptor. It is generated XML that records the public/protected Java API surface, inheritance, visibility, synchronization flags, exceptions, fields, and Javadoc for a slice of Hadoop Common. It does not contain implementation bodies, so control flow and persistence behavior below are derived from the API contracts and comments visible in this chunk.

The slice starts at the end of `org.apache.hadoop.io.file.tfile.Utils` binary-search helpers, then covers serialization packages, Log4J event counting, the core `metrics2` API, metrics mutable registries and sinks, metrics/JMX utilities, network topology/socket factories, security credentials and Kerberos/UGI utilities, credential-provider APIs, authorization/proxy-user and servlet security filters, and the beginning of token secret management.

## Important APIs, Types, And Functions

- `org.apache.hadoop.io.file.tfile.Utils` ends with static `lowerBound` and `upperBound` overloads over `java.util.List`, with optional `java.util.Comparator`, used by TFile consumers to locate sorted-list insertion/search boundaries.
- `org.apache.hadoop.io.serializer` defines Hadoop serialization integration points: `JavaSerialization`, `JavaSerializationComparator`, and `WritableSerialization`. `WritableSerialization` delegates to `Writable.write(DataOutput)` and `Writable.readFields(DataInput)`, while `JavaSerializationComparator` deserializes Java-serialized objects and compares via `Comparable`.
- `org.apache.hadoop.io.serializer.avro` exposes `AvroSerialization`, `AvroSpecificSerialization`, `AvroReflectSerialization`, and marker interface `AvroReflectSerializable`. Key configuration fields include `AVRO_SCHEMA_KEY` and `AVRO_REFLECT_PACKAGES`.
- `org.apache.hadoop.log.metrics.EventCounter` is a Log4J `AppenderSkeleton` with `append`, `close`, and `requiresLayout`; its documented purpose is counting fatal, error, and warn events.
- `org.apache.hadoop.metrics2` provides the core metrics contracts: immutable `AbstractMetric`, `MetricsInfo`, `MetricsTag`, `MetricsRecord`, `MetricsCollector`, `MetricsRecordBuilder`, `MetricsVisitor`, `MetricsFilter`, `MetricsSource`, `MetricsSink`, `MetricsPlugin`, `MetricsSystem`, and `MetricsSystemMXBean`. Builders support tags, context, counters, and gauges across int/long/float/double variants.
- `MetricsJsonBuilder` and `MetricStringBuilder` are concrete `MetricsRecordBuilder` implementations for JSON and string dump representations. They collect tags/metrics and expose `toString()`.
- `DefaultMetricsSystem` is a singleton-style enum facade for initializing, accessing, shutting down, and setting mini-cluster mode on the default daemon metrics system.
- `Interns` creates interned `MetricsInfo` and `MetricsTag` instances.
- `MetricsRegistry` holds mutable metrics and tags for a metrics source. It creates counters, gauges, rates, stats, quantiles, rates-with-aggregation, and rolling averages, and snapshots all registered mutable metrics into a `MetricsRecordBuilder`.
- Mutable metrics include `MutableMetric`, `MutableCounter`, `MutableCounterInt`, `MutableCounterLong`, `MutableGauge`, `MutableGaugeInt`, `MutableGaugeLong`, `MutableQuantiles`, `MutableRate`, `MutableRates`, `MutableRatesWithAggregation`, `MutableRollingAverages`, and `MutableStat`.
- Metrics sinks in this chunk include `FileSink`, `GraphiteSink`, `RollingFileSystemSink`, and `StatsDSink`. Each implements `MetricsSink`; most also implement `Closeable`.
- `RollingFileSystemSink` is the most stateful sink here, with protected fields for `source`, `ignoreError`, `allowAppend`, `basePath`, roll intervals, next flush time, forced flush flags, and supplied test filesystem/configuration hooks.
- `MBeans` standardizes JMX object-name registration as `hadoop:service=<serviceName>,name=<nameName>` with optional properties. `MetricsCache` stores sparse metric updates for sinks that need complete records. `Servers.parse` turns comma/space separated host specs into `InetSocketAddress` values.
- `org.apache.hadoop.net` covers rack/topology mapping and socket factories: `DNSToSwitchMapping`, `AbstractDNSToSwitchMapping`, `CachedDNSToSwitchMapping`, `ScriptBasedMapping`, `TableMapping`, `ConnectTimeoutException`, `SocksSocketFactory`, and `StandardSocketFactory`.
- `Credentials` stores Hadoop tokens and secret keys in memory and supports `Writable` serialization, token-storage file/stream read/write, `addAll`, and `mergeAll`.
- `GroupMappingServiceProvider` and `IdMappingServiceProvider` are pluggable OS/security mapping interfaces for users to groups and numeric IDs.
- `KerberosAuthException` enriches unrecoverable Kerberos login failures with user, principal, keytab, and ticket-cache context.
- `SecurityUtil` centralizes Kerberos principal expansion, login from configuration, token service construction, token-service decoding, `doAs` helpers, authentication-method configuration, privileged-port checks, and ZooKeeper auth loading.
- `UserGroupInformation` wraps a JAAS `Subject` and exposes static process-wide security initialization, current/login user discovery, keytab/ticket-cache login and relogin, remote/proxy/test user construction, token/credential attachment, group lookup, authentication-method handling, and `doAs` execution.
- `UserGroupInformation.AuthenticationMethod` maps UGI auth methods to `SaslRpcServer.AuthMethod`.
- `CredentialProvider` and `CredentialProviderFactory` define thread-safe password/credential storage abstraction, persistent `flush`, alias enumeration, create/delete operations, password-needed warnings/errors, and provider discovery through configured URI paths.
- `AccessControlList`, `AuthorizationException`, `DefaultImpersonationProvider`, and `ImpersonationProvider` cover ACL parsing/serialization and proxy-user authorization against configured groups/users/hosts.
- `RestCsrfPreventionFilter` and `XFrameOptionsFilter` are servlet filters for REST CSRF and clickjacking protection. Both expose static `getFilterParams(Configuration, prefix)` helpers for translating Hadoop configuration prefixes into filter init parameters.
- `SecretManager<T>` and the start of `Token<T>` define delegation-token password creation/retrieval, standby/retriable read paths, HMAC password generation, secret-key conversion, token construction from identifiers/components/protobuf, token copy, token protobuf conversion, identifier decode, and accessors for identifier/password/kind/service.

## Control Flow And Lifecycle

The metrics path is a publish/collect/sink pipeline. A daemon initializes `DefaultMetricsSystem`, registers `MetricsSource` instances with `MetricsSystem.register`, and sources populate records through `MetricsCollector.addRecord`. `MetricsRegistry` simplifies source implementations by owning mutable metrics and tags; source code mutates counters/gauges/stats over time, then `snapshot(builder, all)` emits changed or all values to a `MetricsRecordBuilder`. Sinks receive `MetricsRecord` objects via `putMetrics`, then flush/close according to their implementation.

Mutable metrics distinguish change tracking from collection. `MutableMetric.snapshot(builder)` emits only changed metrics, while `snapshot(builder, all)` can force unchanged values too. Counters are monotonic increments, gauges can increment/decrement/set, stats collect sample counts/sums and optionally extended statistics, quantiles maintain online estimates over periodic rollover intervals, and rolling averages keep sliding-window aggregate state.

`MutableRatesWithAggregation` changes the rate-update flow for high-contention scenarios: each long-running thread keeps local rate counts, and `snapshot` aggregates thread-local state into a global rate. The Javadoc explicitly warns that values produced after the last snapshot and before thread death can be lost, which is a lifecycle risk for short-lived threads.

`RollingFileSystemSink` rolls output directories/files on a schedule. `init` reads metrics2 properties, `setInitialFlushTime` picks an initial roll time with a random offset, `updateFlushTime` advances to the next interval preserving that offset, and `putMetrics`/`flush`/`close` write metrics through Hadoop `FileSystem`. It can append where supported or create sequence-suffixed files; secure deployments require configured keytab and principal keys.

Network topology resolution flows through `DNSToSwitchMapping.resolve(List)`, returning a one-to-one list of rack paths. `CachedDNSToSwitchMapping` delegates misses to a raw mapping and stores host-to-rack results until `reloadCachedMappings` clears all or selected entries. `ScriptBasedMapping` wraps a raw script-based resolver configured from `net.topology.script.file.name`; `TableMapping` reads a two-column mapping file configured by `net.topology.table.file.name`.

Security flows center on static UGI process state and per-user `Subject` state. `UserGroupInformation.setConfiguration` initializes authentication mode and group lookup. `getCurrentUser` returns the current subject, including nested `doAs` scopes. Keytab and ticket-cache login methods create or refresh login credentials; relogin methods update the UGI subject. `doAs` executes privileged actions as a selected UGI and propagates checked or unchecked failures per method contract.

Delegation token flow starts with a token identifier and `SecretManager`. `SecretManager.createPassword(T)` creates token passwords for issued identifiers; `retrievePassword(T)` validates tokens, including expiry/revocation checks supplied by subclasses. `retriableRetrievePassword` can signal standby or temporary retriable failure so clients can fail over or retry. `Token` stores identifier bytes, password, kind, and service, can be serialized as Writable/protobuf, and can decode its identifier through token kind metadata.

Proxy-user authorization flows through `ImpersonationProvider.init(prefix)`, then `authorize(proxyUgi, remoteAddress)`. `DefaultImpersonationProvider` derives configuration keys for allowed effective users, groups, and IPs for a real superuser and throws `AuthorizationException` on denial. The exception suppresses stack traces for security.

HTTP filter flow is standard servlet lifecycle: `init` consumes filter params, `doFilter` applies policy, and `destroy` releases state. `RestCsrfPreventionFilter.handleHttpInteraction` enforces a configurable header for browser-originating requests, while `isBrowser` defaults to user-agent regex matching. `XFrameOptionsFilter` injects the configured frame-options response header before continuing the chain.

## State And Persistence Behavior

The JDiff file itself is static generated metadata. The APIs it describes manage several important state surfaces:

- Metrics state is held in mutable metric objects, `MetricsRegistry` maps, tags, and singleton `DefaultMetricsSystem` process state. Snapshot behavior clears or observes changed flags depending on implementation.
- `MetricsCache` persists sparse metric updates only in memory for sink-side reconstruction of complete records.
- `RollingFileSystemSink` persists metrics records to a Hadoop `FileSystem` under a time-rolled base path. It may append to existing files or create new numbered files, and has explicit error-handling behavior controlled by `ignore-error`.
- `Credentials` persists tokens and secret keys through Hadoop Writable/token-storage file formats and maintains in-memory alias maps for tokens and secret keys.
- `CredentialProvider` implementations are required to be thread safe and may represent persistent stores or transient stores. `flush()` is the contract for writing changes to backing storage.
- UGI maintains static process configuration/login state and per-UGI subject credentials. The `HADOOP_TOKEN_FILE_LOCATION` environment variable points to a token cache file.
- ACLs are `Writable` and can round-trip through `write/readFields`; they also expose a canonical `getAclString()` for configuration persistence.
- Secret-manager implementations own server-side token key/registry state outside this XML chunk; the exposed contract requires validation of expiry and revocation during password retrieval.

## Dependencies And Integration Points

This chunk ties Hadoop Common to Java core libraries (`java.io`, `java.net`, `java.security`, `javax.crypto`, `javax.management`, `javax.security.auth`, servlet APIs), Hadoop contracts (`Configuration`, `Configured`, `Writable`, `Text`, `Path`, `FileSystem`, IPC exceptions, SASL auth methods, token identifiers, security protobufs), Apache Commons Configuration `SubsetConfiguration`, Avro serialization, Log4J, SLF4J, RE2/J patterns, and JMX.

Metrics integration is broad: daemon code registers sources in `DefaultMetricsSystem`, sources use annotations/registries/builders, and sinks integrate with files, Graphite, StatsD, and JMX consumers. Configuration is through `hadoop-metrics2.properties`-style prefixes and sink properties.

Network integration affects HDFS block placement and rack awareness. The `isSingleSwitch` predicate is explicitly used by policies that behave differently on single-rack versus multi-rack systems.

Security integration spans Kerberos principal substitution, keytabs, ticket caches, token service strings, ZooKeeper ACL auth files, JAAS Subjects, RPC remote/proxy users, servlet filters, and credential provider service loading. Misconfiguration in these integration points can surface as authentication failures, authorization denials, or silently ineffective protection.

## Risks And Edge Cases

- Because this is JDiff metadata, method bodies and actual invariants are not visible. Research consumers should verify implementation details in the corresponding `.java` sources before changing behavior.
- Serialization APIs are compatibility-sensitive. Changing `WritableSerialization`, `Credentials`, `Token`, or ACL Writable formats would affect persisted token files and wire compatibility.
- `JavaSerialization` is documented as experimental; using Java object serialization can carry performance, compatibility, and security concerns.
- Metrics naming/tagging APIs are public contracts. Duplicate metric or tag names, incorrect context tags, or misuse of `all=false` snapshots can make metrics disappear or become misleading.
- `MutableRates` is documented as synchronized and unsuitable for high contention. `MutableRatesWithAggregation` improves concurrency but can lose samples from short-lived threads.
- `MutableStat.add(numSamples, sum)` warns that large `numSamples` can produce inaccurate variance due to one-step Welford variance calculation.
- `RollingFileSystemSink` has operational pitfalls: default base path may resolve to `/tmp` on the default filesystem, append support varies by filesystem, HDFS append requires enough DataNodes, HDFS file size may not update until close, and simultaneous cluster-wide rolls can overload HDFS unless roll offset is configured.
- Rack mapping must preserve one-to-one input/output ordering. Unknown hosts should map to default rack in bundled implementations; bad scripts or stale table files can degrade placement locality.
- `AbstractDNSToSwitchMapping` intentionally avoids extending `Configured` because constructor-time `setConf` dispatch can call subclass methods before construction completes.
- `SecurityUtil.doAsLoginUserOrFatal` can terminate the JVM if login user cannot be determined.
- Kerberos login/relogin depends on correct hostname substitution, reverse DNS, keytab path, principal, and ticket-cache state. `KerberosAuthException` is marked unrecoverable and callers should not retry it blindly.
- `AccessControlList.isUserInList` has special behavior for proxied users and `USE_REAL_ACLS`; ACL reviews need to consider both effective and real users.
- `AuthorizationException` intentionally hides stack traces, which is good for security but can reduce diagnosability in tests/logs.
- CSRF protection depends on browser user-agent detection and required custom headers. Non-browser clients may bypass header enforcement by design; user-agent regex changes are security-sensitive.
- `CredentialProvider.needsPassword` and clear-text fallback behavior require careful error handling so callers do not silently fall back to insecure or unavailable credentials.
- `Token.decodeIdentifier` may return null if the identifier class is unavailable and may throw runtime exceptions if instantiation fails; callers must handle both.
- `SecretManager.retriableRetrievePassword` explicitly adds standby/retry exceptions to the authentication path; clients and tests must preserve failover semantics.

## Test Signals

Useful validation signals for this API slice include:

- JDiff/API compatibility tests ensuring public classes, methods, fields, visibility, synchronization, and exceptions remain stable across Hadoop Common releases.
- Serialization round-trip tests for `WritableSerialization`, Avro specific/reflect serializations, `Credentials`, `Token`, and `AccessControlList`.
- Metrics tests that register sources, mutate counters/gauges/stats/quantiles/rates, snapshot with `all=true/false`, validate JSON/string builders, and confirm MBean registration names.
- Concurrency tests for `MetricsRegistry`, mutable metric updates, `MutableRatesWithAggregation`, `MutableRollingAverages.collectThreadLocalStates`, and thread-safe `CredentialProvider` implementations.
- Sink integration tests for `FileSink`, `GraphiteSink`, `StatsDSink`, and especially `RollingFileSystemSink` across local FS/HDFS, append/no-append, roll interval parsing, random roll offset, secure keytab/principal configuration, and error-ignore behavior.
- Rack mapping tests for empty input, unresolved hosts, cache reload, script absence/failure, table-file reload, one-to-one output ordering, and single-switch predicates.
- Socket factory tests for standard and SOCKS proxy socket creation, equality/hashCode, and configuration loading.
- Security tests for UGI initialization, current/login/proxy/test users, keytab/ticket-cache login and relogin, token/credential attachment, `doAs` exception propagation, auth-method mapping, and `HADOOP_TOKEN_FILE_LOCATION` loading.
- Authorization tests for wildcard ACLs, user/group add/remove, proxied real-user ACL behavior, Writable round trips, hidden stack traces, and proxy-user group/host config enforcement.
- Servlet filter tests for CSRF browser detection, custom header/method-ignore configuration, bad-request rejection, config-prefix parameter extraction, and X-Frame-Options header insertion.
- Token/secret-manager tests for password HMAC generation, secret-key conversion, invalid/expired/revoked token handling, standby/retriable failure propagation, protobuf conversion, and identifier decode failure handling.

## Unresolved Cross-Chunk References

The chunk begins mid-class after earlier `Utils` methods and ends mid-`Token` class at `getService`; additional token mutators, Writable methods, equality/string helpers, token renewer/canceler classes, and token identifier classes likely appear in later lines. Some metrics types referenced here, such as `MutableGaugeFloat`, `MetricType`, concrete metric implementations, `AbstractPatternFilter`, quantile utility classes, and nested helper records, are outside the visible range. The source Java implementation files should be used by the merge lane to reconcile exact implementation details.

### subset-b-007203: lines 30680-35426

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.2.4.xml lines 30680-35426

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.2.4, not Java implementation source. The range starts in the tail of `org.apache.hadoop.security.token.Token`, then covers token renewer/identifier/selector APIs, HTTP delegation-token client helpers, the Hadoop service lifecycle framework, service launcher contracts, tracing admin protocol contracts, core utility classes, and the Bloom filter utility package. The conclusions below are based on public/protected signatures, inheritance, constants, declared exceptions, deprecation state, and embedded Javadocs.

## Purpose

The chunk documents reusable Hadoop Common APIs used by higher-level filesystems and daemons rather than a single execution path. The security-token portion defines client-side token identity, selection, renewal, cancellation, and HTTP transport for delegation tokens. The service portion defines a standard lifecycle state machine for Hadoop components and command-line launchable services. The utility portion exposes classloading, shell command execution, reflection, shutdown-hook, version, system-metric, and generic `Tool` support. The final package defines serializable Bloom filter variants used for approximate set membership and count-like behavior.

## Important APIs and types

The visible tail of `org.apache.hadoop.security.token.Token` exposes token service management and wire/string forms: `setService`, `isPrivate`, `isPrivateCloneOf`, `privateClone`, `readFields`, `write`, `encodeToUrlString`, `decodeFromUrlString`, equality/hash/string/cache-key helpers, and lifecycle operations `isManaged`, `renew`, and `cancel`. The `LOG` field is public static final. This is the client-side token representation whose serialized identifier, password, kind, and service are used by RPC and web clients.

`Token.TrivialRenewer` is a `TokenRenewer` for unmanaged token kinds. Subclasses provide `getKind`; `handleKind`, `isManaged`, `renew`, and `cancel` provide default behavior for tokens that are not renewable. `TokenIdentifier` is an abstract `Writable` carrying public token identity; subclasses must expose `getKind` and `getUser`, while the base class provides `getBytes` and an MD5-like tracking id over the serialized identifier. `TokenInfo` is an annotation marker for token metadata. `TokenRenewer` is the plugin interface for `handleKind`, `isManaged`, `renew`, and `cancel`. `TokenSelector` chooses a token for a named `Text` service from a token collection.

`org.apache.hadoop.security.token.delegation.web.DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` for HTTP services that support Hadoop delegation tokens. It has constructors for default or supplied `DelegationTokenAuthenticator` and optional `ConnectionConfigurator`; static configuration of the default authenticator class; a WebHDFS compatibility switch for sending tokens in the query string instead of the `DelegationTokenAuthenticator.DELEGATION_TOKEN_HEADER`; overloaded `openConnection`; and token operations `getDelegationToken`, `renewDelegationToken`, and `cancelDelegationToken`, each with overloads that accept an `AuthenticatedURL.Token` plus URL and token/renewer/service details.

`DelegationTokenAuthenticatedURL.Token` extends the authentication token container with a Hadoop delegation token field through `getDelegationToken` and `setDelegationToken`. `DelegationTokenAuthenticator` wraps an underlying `Authenticator`, accepts a `ConnectionConfigurator`, authenticates HTTP connections, and exposes direct delegation-token get/renew/cancel methods. Its constants define the HTTP/JSON parameter contract: `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `DELEGATION_PARAM`, `TOKEN_PARAM`, `RENEWER_PARAM`, `SERVICE_PARAM`, `DELEGATION_TOKEN_JSON`, `DELEGATION_TOKEN_URL_STRING_JSON`, and `RENEW_DELEGATION_TOKEN_JSON`. `KerberosDelegationTokenAuthenticator` and `PseudoDelegationTokenAuthenticator` provide Kerberos and pseudo-auth variants.

`org.apache.hadoop.service.AbstractService` is the base implementation of the Hadoop service lifecycle. It exposes state and failure inspection (`getServiceState`, `getFailureCause`, `getFailureState`), configuration binding, `init`, `start`, `stop`, `close`, failure recording, stop waiting, protected hooks `serviceInit`, `serviceStart`, and `serviceStop`, listener registration, global listener registration, name/config/start-time/lifecycle-history accessors, state testing, blocker management, and stringification. `CompositeService` extends it with child service management through `getServices`, `addService`, `addIfService`, `removeService`, and lifecycle propagation hooks; `STOP_ONLY_STARTED_SERVICES` controls child-stop behavior.

`LifecycleEvent` is a simple event value object with public `time` and `state` fields. `LoggingStateChangeListener` logs service state changes. The `Service` interface defines the common contract for init/start/stop/close, listener registration, name/config/state/start-time/failure/lifecycle-history/blocker access, and `waitForServiceToStop`. `ServiceOperations` centralizes null-safe and quiet stop helpers. `ServiceStateChangeListener` receives state change callbacks. `ServiceStateException` is a runtime exception with exit-code-aware constructors and `convert` helpers. `ServiceStateModel` owns legal state transitions through `getState`, `ensureCurrentState`, `enterState`, `checkStateTransition`, and `isValidStateTransition`.

The service launcher package provides command-line service contracts. `AbstractLaunchableService` extends `AbstractService` and implements `LaunchableService`, with default `bindArgs` and `execute`. `LaunchableService` separates argument binding from execution. `HadoopUncaughtExceptionHandler` handles uncaught exceptions, optionally delegating to an existing handler. `LauncherExitCodes` defines the process exit-code vocabulary, including success, generic failure, interrupted, argument/usage errors, unauthorized/forbidden/not-found style failures, connectivity/configuration/exception/unimplemented/service-unavailable/version failures, and lifecycle/creation failures. `ServiceLaunchException` carries launcher exit codes with formatted-message constructors.

The tracing package exposes administrative protocol types. `SpanReceiverInfo` reports a receiver id and class name. `SpanReceiverInfoBuilder` builds those records with configuration pairs. `TraceAdminProtocol` lists, adds, and removes span receivers and declares `versionID`; `TraceAdminProtocolPB` is the protobuf bridge interface that extends the generated protocol plus Hadoop versioned protocol behavior.

`org.apache.hadoop.util.ApplicationClassLoader` is a child/application classloader with constructors from URL arrays or classpath strings, `getResource`, `loadClass`, and static `isSystemClass`; `SYSTEM_CLASSES_DEFAULT` defines parent-first/system class patterns. `IPList` is a membership predicate. `Progressable` is the classic single-method progress callback. `PureJavaCrc32` and `PureJavaCrc32C` implement checksum calculation with `getValue`, `reset`, and byte-array/single-int `update`.

`ReflectionUtils` provides configuration injection, reflective `newInstance`, contention tracing control, thread-info printing/logging, class lookup, configurable `Writable` copy/clone helpers, and methods to collect declared fields or methods including inherited members. `Shell` is Hadoop's platform abstraction for command execution and OS-specific commands. It exposes Java-version checks, Windows command-line length checking, group/user/netgroup commands, permission/owner/symlink/readlink/process/signal commands, environment-variable regex, script extension and run-script helpers, Hadoop home/bin/winutils resolution, bash support checks, mutable environment and working directory, `run`, command parsing hooks, process/exit/waiting-thread/timeout inspection, static `execCommand` overloads, shell-process cleanup, memory-lock limit lookup, and many OS/configuration constants.

`ShutdownHookManager` manages priority-ordered shutdown hooks with optional timeouts, removal and presence checks, shutdown-in-progress detection, and hook clearing; `TIMEOUT_MINIMUM` and `TIME_UNIT_DEFAULT` define timeout constraints. `StringInterner` exposes strong and weak string interning and in-place array interning. `SysInfo` is an abstract system metrics provider with factory `newInstance` and virtual/physical memory, processor/core, CPU frequency/time/usage/vcore, network, and storage counters. `Tool` and `ToolRunner` are the standard configurable command-line tool contract and runner, including generic option parsing, command usage printing, and confirmation prompting. `VersionInfo` exposes build metadata through instance and static getters plus a `main` entry point.

The Bloom filter package includes `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, `HashFunction`, `RemoveScheme`, and `RetouchedBloomFilter`. `BloomFilter` extends the abstract `Filter` base and provides default and parameterized constructors, add/logical operations, membership test, vector size, string form, and `Writable` serialization. `CountingBloomFilter` uses counters instead of bits, adds `delete` and `approximateCount`, and warns that repeated insertion beyond small counts can overflow buckets and increase false positives or underflow-related false negatives. `DynamicBloomFilter` grows by adding Bloom filter rows once the configured threshold is reached. `HashFunction` hashes a `Key` into multiple bounded integer positions. `RemoveScheme` defines selective-clearing strategies `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`. `RetouchedBloomFilter` records known false positives and selectively clears bits to remove them while trading off false negatives.

## Control flow and behavior

Token behavior is plugin- and service-driven. A client-side `Token` carries opaque bytes plus kind/service metadata; callers select a token by service with `TokenSelector`, then renew or cancel only if a `TokenRenewer` says it handles the token kind and considers the token managed. `TrivialRenewer` is the default path for unmanaged token kinds and should not produce real renewal semantics.

HTTP delegation-token flow layers token operations over `AuthenticatedURL`. A caller authenticates or opens a URL connection with an `AuthenticatedURL.Token`; when a Hadoop delegation token is present, it is transmitted either via the delegation-token HTTP header or, for backwards compatibility, in the URL query string. Get/renew/cancel operations are represented as HTTP requests with operation, token, renewer, and service parameters and JSON response fields.

Service lifecycle flow is a constrained state machine. Services move through init, start, and stop through public methods, while subclasses implement protected hooks for stage-specific work. Failures are recorded with a state and cause, listeners are notified of transitions, lifecycle history is accumulated, and `waitForServiceToStop` provides synchronization for shutdown. `CompositeService` applies the same lifecycle phases to registered child services, making child ordering and stop-on-started-only behavior important.

Launcher flow separates startup parsing from execution. `bindArgs` binds command-line arguments and returns configuration, then `execute` returns a process exit code from `LauncherExitCodes` or throws `ServiceLaunchException`. The uncaught exception handler maps otherwise uncontrolled thread failures into launcher-level handling.

Utility control flow is mostly adapter-oriented. `ReflectionUtils` centralizes reflective construction and configuration injection. `Shell` builds platform-specific command arrays, executes them under optional environment and working-directory settings, records process state, and parses command output through subclass hooks. `ToolRunner` builds a configured `Tool`, applies generic Hadoop options, invokes `run`, and can prompt the terminal for confirmation.

Bloom filter behavior follows hashed-position operations. A key is hashed to multiple positions by `HashFunction`; add sets or increments those positions; membership tests require all relevant positions to be present in the target row/vector; logical operations combine compatible filters. Dynamic filters add rows as capacity thresholds are reached, counting filters decrement counters on delete, and retouched filters use recorded false positives plus a selected removal scheme to clear positions.

## State and persistence behavior

Token state is serialized through `Writable` methods and URL-safe strings. The service field controls where a token is valid; private clones alter service visibility without changing the public token concept. `TokenIdentifier.getBytes` and `getTrackingId` derive stable identity from serialized identifier bytes, so changes to identifier serialization affect tracking and compatibility.

Delegation-token web clients maintain authentication token state and may also hold a Hadoop delegation token in `DelegationTokenAuthenticatedURL.Token`. The wire contract is HTTP parameters, headers, and JSON fields rather than local persistence. Sending tokens in query strings is explicitly supported only for compatibility and has higher leakage risk through logs, proxies, and browser history.

Services maintain in-memory lifecycle state, configuration, start time, failure cause/state, lifecycle event history, listeners, and blocker maps. `CompositeService` additionally maintains child-service lists. These are process-local state holders; persistent effects are performed by concrete service implementations through their hooks.

Launcher and shutdown utilities affect process state. `ShutdownHookManager` stores JVM-wide hooks with priority and timeout metadata. `Shell` tracks each launched process, timeout flag, waiting thread, inherited environment, configured environment, working directory, and global shell sets for cleanup. These APIs can outlive individual callers and therefore need cleanup in tests.

`VersionInfo` reads build metadata embedded in Hadoop build properties. `SysInfo` reports live host metrics and does not persist them. Bloom filters and several Hadoop utility value types implement `Writable`; their vector/counter/matrix state is serializable through `write` and `readFields`, making binary compatibility relevant for RPC, cached artifacts, or persisted filter files.

## Dependencies and integration points

The token APIs depend on `org.apache.hadoop.io.Text`, `Writable`, `Configuration`, `UserGroupInformation`, and Hadoop security-token plugin discovery. HTTP delegation-token classes integrate with `org.apache.hadoop.security.authentication.client.AuthenticatedURL`, `Authenticator`, `ConnectionConfigurator`, `HttpURLConnection`, Hadoop `Token`, and JSON/HTTP parameter conventions used by WebHDFS and other Hadoop web services.

The service framework integrates with `Configuration`, Java `Closeable`, listener interfaces, SLF4J logging, process exit-code handling, and daemon implementations across Hadoop. Launchable services bridge service lifecycle code to command-line entry points and shell/script integration.

Tracing admin contracts integrate with Hadoop IPC/protobuf protocol machinery and span receiver implementations. Utility classes integrate with Java reflection, `Writable`, thread management, classloading, `Checksum`, operating-system commands, environment variables, subprocesses, shutdown hooks, and build metadata resources. The shell API has explicit OS branches for Windows, Solaris, macOS, FreeBSD, Linux, PPC64, and other platforms, including `winutils` and `setsid` support.

Bloom filters depend on Hadoop's `org.apache.hadoop.util.bloom.Key`, abstract `Filter`, and `org.apache.hadoop.util.hash.Hash`, plus Java `DataInput`, `DataOutput`, and collections for false-positive tracking. They are general-purpose utilities and can be embedded by storage, caching, or query code that needs approximate membership tests.

## Risks and edge cases

This XML is a compatibility baseline, so public signature, visibility, exception, constant, and Javadoc changes can be meaningful even without implementation edits. The range also starts mid-class in `Token`, so final merged research should reconcile the earlier `Token` constructors and fields with this tail.

Token renewal is intentionally indirect. A token may exist but be unmanaged, unsupported by the available renewer, or invalid for the configured service. Incorrect service text or private-clone handling can lead to cache misses, accidental token sharing, or failed authentication. Tracking ids depend on serialization bytes and should not be treated as a cryptographic secret.

HTTP delegation tokens are sensitive transport data. Query-string transport is a backwards-compatibility path and is easier to expose in logs than header transport. Token get/renew/cancel APIs also cross authentication systems, so callers need to handle authentication failures, HTTP errors, interrupted renewals, and partially updated token containers.

Service lifecycle code is stateful and concurrent. Invalid transitions, exceptions in subclass hooks, listener exceptions, double start/stop, child-service partial failures, and waits during shutdown are the major correctness risks. Global listeners and shutdown hooks can leak across tests unless explicitly removed or cleared.

Shell utilities are platform-sensitive. Windows command-line limits, `winutils` discovery, environment-variable syntax, symlink and permission command differences, `setsid` availability, process cleanup, timeouts, and inherited environment behavior can all change behavior by OS and runtime configuration. Deprecated misspelled constant `WINDOWS_MAX_SHELL_LENGHT` is still part of the compatibility surface.

Reflection helpers can instantiate unexpected classes and inject configuration implicitly, so constructor caching, classloader choice, and access to inherited fields/methods need careful testing. `ToolRunner.confirmPrompt` can block interactive runs if used in non-interactive contexts.

Bloom filters are probabilistic. False positives are expected, counting filters can overflow small buckets when the same key is added too often, delete can introduce underflow-related false negatives, dynamic filters require compatible row/vector/hash parameters for logical operations, and retouched filters deliberately trade selected false positives for possible false negatives.

## Test signals

Compatibility tests should parse this XML range and assert the presence and signatures of token renewer/identifier/selector APIs, delegation-token web constants and overloads, service lifecycle methods, launcher exit-code constants, shell constants and command helpers, version/build metadata getters, and Bloom filter constructors/operations.

Token tests should cover service setting, URL-safe encode/decode round trips, `Writable` round trips, private clone behavior, token cache keys, managed versus unmanaged renewer behavior, renew/cancel exception propagation, selector matching by service, and identifier tracking id stability across serialization.

Delegation-token web tests should use a controllable HTTP endpoint to verify header versus query-string token transmission, get/renew/cancel request parameters, JSON response parsing, authenticator selection, connection configurator use, Kerberos and pseudo-auth variants, and failure behavior for bad tokens or authentication errors.

Service tests should cover valid and invalid state transitions, subclass hook ordering, listener registration/removal and notification, failure state recording, lifecycle history, blocker add/remove visibility, `waitForServiceToStop`, `close`, quiet stop helpers, `CompositeService` child ordering, and partial child-start or child-stop failures.

Launcher tests should exercise `bindArgs`, `execute`, `ServiceLaunchException` exit-code preservation, uncaught exception handling, and mapping to `LauncherExitCodes`. Tracing tests should verify list/add/remove span receiver protocol behavior and protobuf bridge version compatibility.

Utility tests should cover application classloader parent-first/system class matching, CRC32/CRC32C known vectors, reflective construction with and without `Configuration`, writable copy/clone behavior, shell command generation for supported OS families, command timeout and process cleanup, Hadoop home/bin/winutils resolution, shutdown-hook priority/timeout/removal behavior, string interning identity expectations, `SysInfo` metric availability, `ToolRunner` generic option parsing, confirmation prompts, and `VersionInfo` build-property loading.

Bloom filter tests should cover add/membership false-positive expectations, logical operation compatibility checks, serialization round trips, counting add/delete/approximateCount including overflow and underflow cases, dynamic row growth when thresholds are exceeded, retouched false-positive registration for single keys/collections/lists/arrays, and each `RemoveScheme` path.
