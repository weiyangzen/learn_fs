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
