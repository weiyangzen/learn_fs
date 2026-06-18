# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007218`: lines 1-6037, `Docs/researches/chunks/subset-b-007218_research.md`
- `subset-b-007219`: lines 6038-12116, `Docs/researches/chunks/subset-b-007219_research.md`
- `subset-b-007220`: lines 12117-18225, `Docs/researches/chunks/subset-b-007220_research.md`
- `subset-b-007221`: lines 18226-24779, `Docs/researches/chunks/subset-b-007221_research.md`
- `subset-b-007222`: lines 24780-31074, `Docs/researches/chunks/subset-b-007222_research.md`
- `subset-b-007223`: lines 31075-37145, `Docs/researches/chunks/subset-b-007223_research.md`
- `subset-b-007224`: lines 37146-40640, `Docs/researches/chunks/subset-b-007224_research.md`

## Chunk Research

### subset-b-007218: lines 1-6037

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml lines 1-6037

## Research scope

This chunk is the first JDiff XML segment for the Apache Hadoop Common 3.3.5 public API snapshot. It is generated documentation metadata rather than Java implementation source, so the research below is based on package/class boundaries, public/protected signatures, inheritance, declared exceptions, constants, deprecation text, and embedded Javadocs. The range covers the API root, `org.apache.hadoop`, `org.apache.hadoop.conf`, `org.apache.hadoop.crypto.key`, and the beginning of `org.apache.hadoop.fs` through the first fields of `CommonConfigurationKeysPublic`.

## Purpose

The chunk documents core Hadoop Common contracts that many higher-level modules depend on: Hadoop-specific argument exceptions, the configurable object model, the central `Configuration` API, pluggable encryption key provider interfaces, the `AbstractFileSystem` implementation contract used by `FileContext`, filesystem stream and metadata helper interfaces, client-side checksum wrapping, and shared public configuration key constants.

At a higher level, this range describes how Hadoop components acquire configuration, resolve defaults and resource overlays, discover filesystem and key-provider implementations from configuration, expose filesystem operations through stable public contracts, and advertise optional stream/filesystem capabilities without forcing every filesystem to implement every feature.

## Important APIs and types

`org.apache.hadoop.HadoopIllegalArgumentException` is a Hadoop-specific subclass of `IllegalArgumentException`. Its purpose is diagnostic separation: callers can distinguish argument errors thrown by Hadoop implementation code from argument errors thrown by the JDK.

`org.apache.hadoop.conf.Configurable` defines the two-method configuration injection contract: `setConf(Configuration)` and `getConf()`. `Configured` is the simple base implementation holding a `Configuration`, with default and configuration-taking constructors.

`org.apache.hadoop.conf.Configuration` is the largest surface in this chunk. It implements `Iterable` and `Writable` and exposes constructors for default loading, explicit `loadDefaults`, and cloning from another configuration. Major API families include:

- Global key deprecation APIs: `addDeprecation`, `addDeprecations`, `isDeprecated`, `hasWarnedDeprecation`, `dumpDeprecatedKeys`, and `setDeprecatedProperties`.
- Resource loading: `addDefaultResource`, `addResource` overloads for classpath names, `URL`, `Path`, `InputStream`, named streams, another `Configuration`, and restricted parser variants.
- Reloading: static `reloadExistingConfigurations()` and instance `reloadConfiguration()`.
- String and raw access: `get`, `getRaw`, `getTrimmed`, `set`, `unset`, `setIfUnset`, `onlyKeyExists`, and `clear`.
- Typed accessors: integer, integer arrays, long, human-readable byte sizes, float, double, boolean, enum, time duration, time duration arrays, storage-size conversion, regex `Pattern`, integer ranges, string collections, arrays, trimmed arrays, and multi-string setters.
- Secret handling: `getPassword`, `getPasswordFromCredentialProviders`, and protected clear-text fallback `getPasswordFromConfig`.
- Network helpers: `getSocketAddr`, `setSocketAddr`, and `updateConnectAddr`, including bind-host versus client-connect address handling and wildcard replacement.
- Class loading and plugin construction: `getClassByName`, `getClassByNameOrNull`, `getClasses`, `getClass`, `getInstances`, `setClass`, `getClassLoader`, and `setClassLoader`.
- Local path helpers: `getLocalPath`, `getFile`, `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader`.
- Introspection and output: `getPropertySources`, `getFinalParameters`, protected `getProps`, `size`, `iterator`, `getPropsWithPrefix`, `writeXml`, `dumpConfiguration`, `getValByRegex`, `addTags`, `getAllPropertiesByTag`, `getAllPropertiesByTags`, and `isPropertyTag`.
- Serialization and CLI/debug hooks: `readFields`, `write`, `toString`, `setQuietMode`, and `main`.

`Configuration` Javadocs define the semantics that matter most: resources are loaded from classpath names or local `Path`s, default resources are normally `core-default.xml` then `core-site.xml`, later resources override earlier resources unless a property was marked final, and variable expansion resolves against the current configuration, environment variables prefixed with `env.`, and system properties. The docs also define tag-based grouping via `hadoop.tags.system`, `hadoop.tags.custom`, and per-property `<tag>` elements.

`org.apache.hadoop.crypto.key.KeyProvider` is an abstract, thread-safe provider of secret key material. It is constructed with a `Configuration` and implements `Closeable`. The abstract storage contract includes `getKeyVersion`, `getKeys`, `getKeyVersions`, `getMetadata`, `createKey(name, material, options)`, `deleteKey`, `rollNewVersion(name, material)`, and `flush`. Convenience/default behavior includes `options(conf)`, bulk metadata lookup, current-key lookup, generated-material create and roll methods, cache invalidation, close, version-name helpers, provider search, password requirement checks, and warning/error text for missing passwords. Public constants define default cipher, bit length, and JCEKS serialization filtering keys.

`KeyProviderFactory` is the service-loader style factory layer. It has an abstract `createProvider(URI, Configuration)`, static `getProviders(Configuration)` for configured provider paths, static `get(URI, Configuration)` for one provider URI, and the public `KEY_PROVIDER_PATH` configuration constant.

`org.apache.hadoop.fs.Abortable` defines a stream abort contract. `abort()` must cancel an active write so the output does not become visible, returning an `AbortableResult` or throwing `UnsupportedOperationException`.

`org.apache.hadoop.fs.AbstractFileSystem` is the central implementor-facing filesystem abstraction behind `FileContext`. It is abstract, implements `PathCapabilities`, is constructed with a URI, supported scheme, authority requirement, and default port, and holds protected `FileSystem.Statistics statistics`. Important APIs include:

- Factory and statistics lifecycle: `createFileSystem`, `get(uri, conf)`, static/protected `getStatistics`, `clearStatistics`, `printStatistics`, and `getAllStatistics`.
- URI/path validation: `isValidName`, `checkScheme`, `getUriDefaultPort`, `getUri`, `checkPath`, `getUriPath`, and `makeQualified`.
- Directory defaults and user locations: `getInitialWorkingDirectory`, `getHomeDirectory`, and `getServerDefaults` with the older no-path overload deprecated in favor of `getServerDefaults(Path)`.
- Core data operations: final `create(Path, EnumSet<CreateFlag>, CreateOpts...)` dispatching to explicit abstract `createInternal`, abstract `mkdir`, `delete`, `open(Path, int)`, `setReplication`, `setPermission`, `setOwner`, `setTimes`, `getFileChecksum`, `getFileStatus`, `getFileBlockLocations`, `getFsStatus()`, `listStatus`, and `setVerifyChecksum`.
- Default or optional operations: `open(Path)`, `truncate`, final `rename` with options, abstract no-overwrite `renameInternal`, overwrite-capable `renameInternal`, symlink support methods, `resolvePath`, `msync`, link status, status iterators, located status, corrupt-block listing, canonical service name, ACLs, xattrs, snapshots, storage policies, `openFileWithOptions`, path capability checks, multipart uploader creation, and `methodNotSupported()`.

`AvroFSInput` adapts `FSDataInputStream` to Avro's `SeekableInput`, either from an existing stream plus length or from `FileContext` and `Path`. It exposes `length`, `read`, `seek`, `tell`, and `close`.

`BatchListingOperations` is an optional filesystem interface for listing many paths in one call. It returns `RemoteIterator<PartialListing>` from `batchedListStatusIterator` and `batchedListLocatedStatusIterator`; filesystems that implement it should advertise `CommonPathCapabilities.FS_EXPERIMENTAL_BATCH_LISTING`.

`BlockLocation` is a serializable value object describing block replica locations. Constructors support basic replicated block fields, corrupt flags, network topology paths, cached hosts, storage IDs, storage types, and erasure-coded/striped block groups. Accessors and mutators cover hosts, cached hosts, names, topology paths, storage IDs, storage types, offset, length, corrupt flag, striped flag, and string formatting. Its Javadoc explicitly distinguishes replicated files from erasure-coded files, where one `BlockLocation` may represent a logical block group rather than one replicated block.

`BlockStoragePolicySpi` describes a storage policy through a name, preferred storage types, creation fallback types, replication fallback types, and copy-on-create/inherit-only status.

Stream capability interfaces in this chunk include `ByteBufferPositionedReadable`, `ByteBufferReadable`, `CanSetDropBehind`, `CanSetReadahead`, and `CanUnbuffer`. They define byte-buffer read semantics, positioned byte-buffer reads that do not change file offset and must be thread-safe, cache-dropping hints, readahead hints, and explicit buffer/resource release. The docs emphasize checking stream capabilities before assuming support.

`ChecksumException` is an `IOException` with a stored error position. `ChecksumFileSystem` extends `FilterFileSystem` to add client-side checksum files around a raw filesystem. It exposes checksum filename derivation, checksum-file detection, checksum length calculation, bytes-per-checksum, read/write checksum toggles, raw filesystem access, open/create/append/truncate/concat, permission/owner/ACL forwarding, replication, rename/delete/listing/mkdir/copy helpers, local output staging, checksum failure reporting, builder overrides, and capability filtering.

`CommonConfigurationKeysPublic` begins in this chunk and is a public constants holder for keys/defaults used across Hadoop Common. The visible fields cover filesystem defaults and tuning (`fs.defaultFS`, df/du intervals, `fs.getspaceused` implementation and jitter, remote symlink resolution, filesystem implementation keys, FTP host/port, trash intervals, protected directories, automatic close, parallel filesystem creation), network topology keys, IO and sequence-file tuning, compression codec key names, TFile buffer sizing, caller context limits, IPC client/server socket and retry settings, RPC socket factory and SOCKS server keys, hashing type, and the first group mapping cache keys. Several older mapreduce sort constants are explicitly deprecated in favor of mapreduce keys, while sequence-file sorter keys remain in Common.

## Control flow and behavior

Configuration control flow is lazy and overlay-based. A new `Configuration` may load defaults automatically, but actual resource parsing is documented as lazy: `get()` can trigger loading on first access. Resources are applied in order, later resources override earlier resources, and final parameters block later overrides. Programmatic `set()` calls overlay resource-loaded values and propagate values across deprecated and replacement keys. `reloadConfiguration()` clears loaded resource state and final parameters so resources are reread later, while preserving values set through setters as an overlay.

Deprecation control flow is global and concurrent. The `addDeprecations` doc describes a lockless copy-and-swap of a deprecation context, retrying if another thread wins the race. Deprecated keys can alias one or more replacement keys; getting a deprecated key returns the first non-null replacement, and setting a deprecated key sets associated replacement keys.

Value interpretation flows through specialized helpers. Raw access bypasses variable expansion; normal string access expands variables. Numeric, duration, storage, enum, pattern, range, collection, address, and class APIs all build on the resolved string value and throw or return defaults according to the specific accessor contract. `getPassword` first asks credential providers for an alias and only falls back to clear-text configuration when appropriate.

Key-provider control flow separates discovery from storage operations. `KeyProviderFactory` resolves provider URIs from configuration and service-loader factories, then `KeyProvider` instances perform key metadata lookup, current version lookup, creation, deletion, rolling, cache invalidation, and `flush()` to make changes durable. Generated-material create/roll methods call into abstract material-taking methods after local key generation.

`AbstractFileSystem` control flow is a template contract. Public entry points validate qualification and `FileContext`-level semantics, then dispatch into abstract filesystem-specific methods such as `createInternal`, `open(Path, int)`, `delete`, `renameInternal`, and status/listing calls. Some public methods are final to preserve common behavior, notably `create` and option-based `rename`. Optional features default to unsupported behavior or generic blocking wrappers, such as `openFileWithOptions` returning a `CompletableFuture` whose result is produced by a blocking `open(Path, int)` call.

Path-sensitive filesystem control flow centers on URI ownership. `checkPath`, `getUriPath`, and most operation Javadocs require the path to belong to the filesystem or be slash-relative. Symlink-aware methods may partially resolve links and may throw `UnresolvedLinkException`. `msync()` is an explicit metadata synchronization hook for filesystems such as HDFS where client metadata freshness matters in HA deployments.

Checksum filesystem control flow wraps raw operations with sidecar checksum-file management. Opening a data file may verify checksums; creating/appending data may create or update checksum files; rename, delete, copy, and list methods must account for both user-visible data paths and hidden checksum paths. `reportChecksumFailure` gives the raw filesystem a chance to handle corrupt data/checksum ranges and indicate whether retry is useful.

## State and persistence behavior

`Configuration` state includes resource lists, loaded properties, final-parameter names, property source tracking, deprecation aliases/warning state, class loader, quiet mode, system-property restriction flags, null-value handling for tests, and tag mappings. It persists through `Writable` `readFields`/`write`, XML output via `writeXml`, and JSON-like diagnostic dumps via `dumpConfiguration`. Resource-backed state remains external in XML files; setter-backed values are in-memory overlays unless written out.

Configuration persistence is also provenance-aware. `getPropertySources` returns ordered source information, including resource paths and programmatic/command-line origins, which is important for debugging why a value won. Final properties and tags are metadata attached to configuration properties, not just key/value pairs.

Key-provider persistent state resides in provider implementations such as JCEKS files, KMS-backed stores, or other third-party bindings. The base `KeyProvider` makes durability explicit with `flush()`, exposes `isTransient()` for non-long-term providers, and provides `needsPassword()`/missing-password messages for stores that require unlock material.

Filesystem state is external to `AbstractFileSystem` implementations: directories, files, blocks, permissions, ACLs, xattrs, snapshots, storage policies, quotas, and checksums live in the backing filesystem. The API object itself holds URI identity and statistics, and its methods expose external state through `FileStatus`, `FsStatus`, `BlockLocation`, ACL status, xattr maps, and storage policy objects.

`BlockLocation` is serializable client metadata. It carries block offset/length, host arrays, topology paths, storage IDs/types, cached hosts, corruption state, and erasure-coded striped state. Callers should treat it as a snapshot of block placement, not durable authority.

`ChecksumFileSystem` maintains client-side checksum sidecars in the backing raw filesystem. This means data-file mutations and metadata operations have hidden persistence effects on checksum files; delete/rename/list/copy semantics must keep checksum and data files consistent.

## Dependencies and integration points

This chunk depends on Java core types such as `IOException`, `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `Writer`, `Reader`, `URL`, `URI`, `InetSocketAddress`, `ClassLoader`, `Pattern`, `Properties`, collections, `CompletableFuture`, `TimeUnit`, `ByteBuffer`, `Serializable`, and cryptographic exceptions.

Hadoop-internal dependencies include `org.apache.hadoop.fs.Path`, `FileSystem`, `FileContext`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `FsServerDefaults`, `FsStatus`, `BlockLocation`, `BlockStoragePolicySpi`, `MultipartUploaderBuilder`, `RemoteIterator`, `Options`, `CreateFlag`, `OpenFileParameters`, `PartialListing`, `PathCapabilities`, `CommonPathCapabilities`, permission and ACL classes, security `AccessControlException`, `Progressable`, `Writable`, and credential-provider APIs.

`Configuration` is an integration hub for almost every other component. Filesystem factories use configuration keys such as `fs.AbstractFileSystem.<scheme>.impl` and `fs.<scheme>.impl`. Key providers use `KeyProviderFactory.KEY_PROVIDER_PATH`. Password access integrates with credential providers. Class-based settings instantiate plugin implementations, so class loader selection and interface validation are compatibility-critical.

`AbstractFileSystem` integrates with `FileContext` rather than direct `FileSystem` callers. Many Javadocs define behavior by reference to equivalent `FileContext` methods, with additional requirements such as fully qualified paths and absolute permissions after umask application.

`AvroFSInput` integrates Hadoop filesystem streams with Apache Avro. Byte-buffer read interfaces integrate with stream capability advertising, allowing libraries to use zero-copy or direct-buffer paths only when safely supported.

`CommonConfigurationKeysPublic` integrates code with `core-default.xml` and public documentation. The JDiff fields are the Java-side constants that prevent stringly typed use of configuration keys across common, HDFS, YARN, MapReduce, IPC, security, filesystem, and IO code.

## Risks and edge cases

- `Configuration.get()` can trigger lazy resource loading, so code that mutates global deprecations or default resources after configurations have loaded may observe unsupported or inconsistent behavior.
- Deprecated-key aliasing can be surprising: setting one key may update deprecated and replacement names, and multiple replacement keys can reset each other to maintain alias semantics.
- Variable expansion can resolve from environment variables and system properties. Restricted system-property flags exist because unbounded system property lookup can be a security or reproducibility risk.
- `InputStream` resources are cached and later closed; the docs warn this increases memory consumption and should be used sparingly.
- Final configuration properties block later overrides. Tests that assume last-writer-wins must include final-property cases.
- Typed accessors differ in failure behavior: invalid ints/longs/floats/doubles/time durations can throw, while invalid booleans return defaults. Callers must not assume uniform parsing behavior.
- `getPassword` may fall back to clear-text configuration, which is useful for compatibility but risky if callers expect credential-provider-only behavior.
- `getSocketAddr` and `updateConnectAddr` have bind-host/client-address split behavior and wildcard address rewriting. Multi-homed hosts and wildcard listeners are easy places for wrong advertised addresses.
- `KeyProvider` implementations must be thread-safe and must make `flush()` durable. Missing cache invalidation after `rollNewVersion` can lead to stale encryption keys.
- `KeyProvider` generated-material paths depend on cryptographic algorithm availability; `NoSuchAlgorithmException` is part of normal API behavior.
- `AbstractFileSystem` methods often throw several checked exceptions, including `AccessControlException`, `FileNotFoundException`, `UnresolvedLinkException`, and `UnsupportedFileSystemException`. Adapters that collapse these exceptions can lose important semantics.
- `rename` behavior is split between no-overwrite and overwrite-capable internal methods. Implementations that only override one path must still satisfy `FileContext` option semantics.
- Optional filesystem operations such as ACLs, xattrs, snapshots, storage policies, multipart upload, `msync`, and byte-buffer reads may be unsupported; callers should use capability checks or tolerate `UnsupportedOperationException`/`IOException`.
- `openFileWithOptions` in the base `AbstractFileSystem` uses a blocking open behind a future. Code expecting true asynchronous IO must verify filesystem-specific overrides.
- `BlockLocation` representation changes for erasure-coded files: offset/length may describe a logical block group, and hosts include all data and parity block holders.
- ByteBuffer read methods leave buffer state undefined on exception. Robust callers must reset or discard buffers after failures.
- `ChecksumFileSystem` hides sidecar checksum files. Listing, copying, renaming, and deleting must avoid exposing or orphaning checksum files, and truncation/concat must keep checksum data consistent with file data.
- Deprecated constants such as `IO_SORT_MB_KEY` and `IO_SORT_FACTOR_KEY` remain present for compatibility but point users to MapReduce-specific keys.

## Test signals

Useful validation for code depending on this API surface should include:

- Configuration resource order tests covering defaults, site resources, added resources, final parameters, clone construction, reload behavior, and programmatic overlay after reload.
- Deprecation tests for one-to-one and one-to-many aliases, no override of existing deprecation entries, warning-state tracking, `setDeprecatedProperties`, and concurrent `addDeprecations`.
- Variable expansion tests for configuration variables, `env.NAME`, `env.NAME:-default`, `env.NAME-default`, system-property fallback, and restricted system-property modes.
- Typed configuration tests for invalid numeric parsing, human-readable byte suffixes, time suffix conversion/default units, storage-size units, enum validation, regex defaults, range parsing, string trimming, empty arrays, and null-value test mode.
- Credential tests proving credential-provider lookup precedes clear-text fallback and that `IOException` surfaces from provider failures.
- Socket-address tests for bind host versus service address, wildcard replacement, default ports, and `updateConnectAddr` on multi-home configurations.
- `Writable`/XML/dump tests for `Configuration` round trips, property sources, final flags, tag metadata, single-property dumps, missing-property errors, and `InputStream`-loaded resource omissions in dumps.
- Key-provider contract tests for provider discovery from URI schemes, missing provider handling, create/delete/roll/get-current flows, metadata bulk lookup, generated key algorithm failures, `flush()` durability, cache invalidation, transient providers, password-required warnings/errors, and thread safety.
- `AbstractFileSystem` implementor tests for URI scheme/authority validation, path qualification, invalid names, create option dispatch, absolute permission handling, mkdir/delete/open/truncate/replication/rename semantics, overwrite/no-overwrite behavior, symlink handling, status/listing/block-location calls, and exception preservation.
- Capability tests for ACL, xattr, snapshot, storage policy, multipart upload, `msync`, `openFileWithOptions` mandatory option rejection, and `hasPathCapability`.
- Avro adapter tests for length, seek/tell, EOF/read behavior, close propagation, and construction through `FileContext`.
- Batch listing tests for multiple input paths, located versus unlocated partial listings, iterator error propagation, and advertised experimental capability.
- `BlockLocation` tests for constructor variants, defensive handling of arrays, cached hosts, storage IDs/types, corrupt and striped flags, replicated versus erasure-coded formatting, serialization compatibility, and `toString`.
- Stream interface tests for byte-buffer position/limit updates, zero-length reads, EOF, exception buffer-state handling, positioned-read thread safety, and unsupported readahead/drop-behind/unbuffer behavior.
- `ChecksumFileSystem` tests for checksum filename generation, checksum length math, verify/write toggles, open/create/append/truncate/concat, hidden checksum file listing, delete/rename consistency, ACL/owner/permission forwarding, local copy with and without CRC, checksum failure reporting, builder delegation, and disabled capabilities.
- Constant-level tests or compatibility checks that Java constants in `CommonConfigurationKeysPublic` match `core-default.xml` names/defaults and that deprecated IO sort constants continue to compile while directing callers to MapReduce replacements.

### subset-b-007219: lines 6038-12116

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml lines 6038-12116

## Research scope

This chunk is part of the generated JDiff XML API snapshot for Apache Hadoop Common 3.3.5. It is not Java implementation source; it records public/protected API signatures, inheritance, visibility, deprecation text, checked exceptions, constants, and embedded Javadocs emitted from the Hadoop Common build. The range begins in the middle of `org.apache.hadoop.fs.CommonConfigurationKeysPublic`, then covers core `org.apache.hadoop.fs` API types through the first large portion of `FileSystem`, ending inside `FileSystem.getXAttrs(Path, List)`.

## Purpose

The chunk documents the public Hadoop Common filesystem contract and the configuration keys that shape that contract. It captures security, IPC, crypto, key-provider, KMS, credential-provider, shell, HTTP, metrics, and service shutdown configuration constants, then moves into the filesystem API objects that client code, filesystem implementations, command-line tools, and RPC bridges rely on.

The main filesystem purpose is to define how Hadoop clients describe file and directory metadata (`FileStatus`, `ContentSummary`, `FileChecksum`), how create semantics are validated (`CreateFlag`), how higher-level client state is handled (`FileContext`), and how the older but dominant `FileSystem` abstraction resolves schemes, instantiates/caches implementations, creates/open/appends files, lists paths, mutates metadata, and exposes optional capabilities such as symlinks, checksums, ACLs, xattrs, snapshots, storage policies, and path handles.

## Important APIs and types

`org.apache.hadoop.fs.CommonConfigurationKeysPublic` is represented by the tail of its public constants. The visible section includes keys and defaults for group mapping and group caches, shell group lookup timeout, security authentication/authorization, auth-to-local rules, token file/env handling, Kerberos relogin and keytab auto-renewal, RPC protection, SASL property resolver override, crypto codec/cipher/JCE provider/buffer configuration, impersonation provider override, key provider and default key metadata, KMS encrypted-key cache and failover tuning, secure random implementation and entropy device path, safe shell delete limits, HTTP log exposure and idle timeout, credential-provider path and clear-text fallback, sensitive config keys, system/custom tags, shutdown hook timeout, Prometheus enablement, and IPC server metrics update runner interval. Deprecated aliases include shell timeout seconds constants and old Hadoop tags constants.

`ContentSummary` extends `QuotaUsage` and implements `Writable`. It stores and formats content accounting for a file or directory: length, directory count, file count, snapshot length/counts/space consumed, erasure coding policy, quota-derived formatting, equality/hash, and table header generation. Older constructors remain but are documented as superseded by `ContentSummary.Builder`, with one legacy constructor implicitly treating space consumed as length. Multiple `toString(...)` overloads control quota output, human-readable formatting, storage-type quota display, snapshot inclusion/exclusion, and selected storage types.

`CreateFlag` is the enum contract for create/append behavior. Its documented combinations define create-if-absent, append-if-present, overwrite-if-present, create-or-append, create-or-overwrite, synchronous block behavior through `SYNC_BLOCK`, transient storage placement through `LAZY_PERSIST`, and append-to-new-block through `APPEND_NEWBLOCK`. Static validation methods reject illegal combinations such as `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`, validate create behavior against path existence, and validate append flags.

`FileAlreadyExistsException` is the IOException used when a target exists and the operation is not configured to overwrite it.

`FileChecksum` is an abstract `Writable` for file checksum values. Implementations provide algorithm name, byte length, raw bytes, and optional `Options.ChecksumOpt`; equality requires matching algorithm and checksum bytes.

`FileContext` is the newer high-level client interface backed by `AbstractFileSystem`. It implements `PathCapabilities` and models per-client filesystem state: default filesystem, working directory, umask, and UGI. Factory methods create contexts from an `AbstractFileSystem`, default configuration, explicit URI, explicit configuration, or local filesystem. Path handling methods include `getFSofPath`, `makeQualified`, `resolvePath`, symlink-aware intermediate resolution helpers, and working-directory management. Operational APIs cover create, create builder, mkdir, delete, open, truncate, set replication, rename, permissions, owner/group, times, checksums, file/link status, symlinks, filesystem status, listing, delete-on-exit, statistics, ACLs, xattrs, snapshots, storage policies, open-file builder, path capability checks, server defaults, and multipart upload builder. Public defaults include `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and shutdown hook priority.

`FileStatus` is the serializable client-side metadata object for a file, directory, or symlink. It implements `Writable`, `Comparable`, Java serialization, and object validation. Constructors cover status without symlink support, symlink-aware status, boolean attribute flags, attribute-set status, and copy construction. It exposes length, file/directory/symlink checks, block size, replication, modification/access time, permission, ACL/encryption/erasure-coded/snapshot-enabled flags, owner/group, path, symlink target, ordering/equality/hash by path, protobuf-backed `readFields`/`write` methods that are now deprecated in favor of `PBHelper`, and the shared empty attribute set `NONE`. The old `isDir()` method is deprecated in favor of explicit `isFile()`, `isDirectory()`, and `isSymlink()`.

`FileSystem` is the abstract, configured filesystem base class. In this range it implements `Closeable`, `DelegationTokenIssuer`, and `PathCapabilities`. The API includes static instance lookup and cache control (`get`, `newInstance`, `getLocal`, `newInstanceLocal`, `closeAll`, `closeAllForUGI`), default URI accessors, initialization, scheme/URI/canonical URI hooks, default port hooks, path qualification and membership checks, canonical delegation-token service naming, server defaults, block-location queries, path handles, open methods, many `create` overloads, primitive create/mkdir helpers for `FileContext`, non-recursive create, append, concat, replication, rename, truncate, delete, delete-on-exit, existence/type/length/status helpers, content summary and quota APIs, listing/globbing APIs, local copy/move helpers, local-output staging, close semantics, space and default block/replication queries, metadata sync, symlink APIs, checksum APIs, filesystem capacity status, permission/owner/time mutation, snapshots, ACL mutation/query, and xattr mutation/query.

## Control flow and behavior

The generated API shows two parallel filesystem client control paths. `FileContext` routes operations through `AbstractFileSystem` and carries client-side defaults such as default filesystem, working directory, UGI, and umask. Its path methods normalize relative, slash-relative, and fully qualified URI names before dispatching to the filesystem of the target path. The Javadoc emphasizes that working directory handling is prefix-based and does not follow symlinks the way Unix process working directories do.

`FileSystem` provides the older scheme/authority based control path. Static `get(URI, Configuration)` first honors per-scheme cache disabling through `fs.$SCHEME.impl.disable.cache`; otherwise it returns a cached filesystem for the URI or creates, initializes, caches, and returns a new instance. `newInstance(...)` always creates a unique filesystem. Initialization must be forwarded by subclasses to `super.initialize(...)`, while subclasses may canonicalize URI authority, add default ports, and provide scheme/URI identity. `close()` releases resources, removes cached instances, and processes delete-on-exit paths; operations after close are documented as undefined.

Create/open control flow is heavily overloaded but centers on a few implementation points. `FileContext.create(Path, EnumSet<CreateFlag>, CreateOpts...)` verifies create flags and create options, applies umask to permissions, and then calls the backing filesystem create path. `FileSystem.create(...)` overloads supply defaults for overwrite, buffer size, replication, block size, progress, permission, flags, and checksum options until reaching abstract or implementation-specific create methods. `primitiveCreate(...)` exists as a compatibility hook for `FileContext` to pass absolute permissions after umask processing. Builder APIs defer validation and state-changing work until `FSDataOutputStreamBuilder.build()` or `FSDataInputStreamBuilder.build()`.

Path handles introduce identity-oriented open control flow. `getPathHandle(FileStatus, HandleOpt...)` verifies that the status belongs to the filesystem, then delegates to `createPathHandle(...)`. Later `open(PathHandle, int)` may use encoded metadata to address the resource directly and enforce handle constraints; it can throw `InvalidPathHandleException` when those constraints no longer hold.

Listing and matching control flow distinguishes eager arrays from remote iterators. `listStatus(Path)` must not return null and does not guarantee sorted results. `globStatus(...)` sorts matching results by path/name and has a special null-vs-empty distinction: null may mean a non-glob path does not exist, while an empty array means a glob matched nothing. `listLocatedStatus(...)`, `listStatusIterator(...)`, and `listFiles(...)` expose remote iteration so implementations can fetch entries on demand; the API asks implementations to override iterator methods for efficiency.

Metadata mutation control flow is feature-dependent. ACL, xattr, snapshot, storage policy, checksum, truncate, concat, symlink, and corrupt-block APIs often default to `UnsupportedOperationException` or no-op/neutral behavior if a filesystem does not support the feature. For example, default checksum lookup can return null, checksum verification/write flags may do nothing, append and concat are optional, and many ACL/xattr/snapshot operations document unsupported default outcomes.

## State and persistence behavior

Most durable state is external to these API classes and lives in the backing filesystem: file bytes, directories, symlinks, permissions, owners, groups, modification/access times, ACLs, xattrs, snapshots, storage policies, quotas, block placement, checksums, and capacity usage. The API objects are the stable client contracts for reading and mutating that state.

Client-side persistent or semi-persistent state appears in several places. `FileSystem` instances are cached by scheme/authority/user/config behavior unless disabled, and `closeAll`/`closeAllForUGI` clear cached instances. `deleteOnExit` stores paths to delete when the filesystem closes or the JVM closes cached filesystems cleanly; this queue must be treated as best-effort because shutdown, network reachability, and remote filesystem cost can affect completion. `FileContext` stores per-context default filesystem, working directory, UGI, and umask; unlike process-global Unix state, these are object properties.

`ContentSummary`, `FileChecksum`, and `FileStatus` implement Hadoop `Writable`, marking them as wire-serialization or persistence-compatible API objects. `FileStatus.readFields` and `write` now encode protobuf and are deprecated in favor of direct `PBHelper` protobuf conversion, but their presence is an important binary compatibility signal. `FileStatus` also participates in Java serialization and object validation.

Configuration constants in `CommonConfigurationKeysPublic` govern process/runtime behavior rather than storing application state themselves. They bind the API to `core-default.xml` and runtime `Configuration` state, affecting caches, authentication, RPC, crypto, KMS, credential lookup, metrics, HTTP exposure, shutdown timing, and filesystem implementation discovery.

## Dependencies and integration points

This chunk integrates the filesystem API with Hadoop Common configuration, security, IO, permissions, and utility types. Key Hadoop dependencies include `Configuration`, `Configured`, `Path`, `AbstractFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `FutureDataInputStreamBuilder`, `MultipartUploaderBuilder`, `RemoteIterator`, `BlockLocation`, `FsStatus`, `FsServerDefaults`, `QuotaUsage`, `StorageType`, `BlockStoragePolicySpi`, `Options.CreateOpts`, `Options.ChecksumOpt`, `Options.HandleOpt`, `Options.Rename`, `PathFilter`, `PathCapabilities`, `FsPermission`, `AclStatus`, `UserGroupInformation`, `DelegationTokenIssuer`, and Hadoop security/access exceptions.

External and JDK integration points include `java.net.URI` for scheme/authority naming, `java.io.Closeable`, `IOException`, `FileNotFoundException`, `DataInput`, `DataOutput`, Java serialization interfaces, `EnumSet`, `List`, `Map`, `Collection`, and logging through SLF4J for `FileContext`. The XML header shows this API snapshot was generated with the Hadoop public-annotation JDiff doclet against the Hadoop Common 3.3.5 classpath; it therefore reflects the exported public/protected compatibility surface rather than private implementation details.

`CommonConfigurationKeysPublic` links many constants to `core-default.xml`, which is the configuration integration point for default values and operator-facing documentation. Filesystem implementation loading depends on scheme-specific implementation keys and cache-disable keys. Token integration depends on `FileSystem.getCanonicalServiceName()` and child-filesystem behavior, with the token cache using the canonical service name to find delegation tokens.

## Risks and edge cases

The chunk exposes several compatibility and correctness risks:

- The range starts mid-class at `CommonConfigurationKeysPublic`; any per-file merged research should combine this chunk with earlier lines to avoid treating the visible constants as the complete class.
- Generated JDiff XML does not expose method bodies. Behavior described here is limited to signatures and Javadocs; implementation-specific behavior can diverge among HDFS, local filesystems, object stores, ViewFS, and custom plugins.
- `FileSystem.get(URI, Configuration)` caching means callers may share mutable filesystem clients unintentionally. Tests that need isolation should use `newInstance(...)` or disable per-scheme caching.
- `FileSystem.close()` makes later use of the filesystem and its streams undefined. Cached instances closed by `closeAll` or `closeAllForUGI` can break code that retains references.
- `deleteOnExit` is best-effort and can significantly extend shutdown on remote or object-store filesystems because existence checks and recursive deletes may be expensive or blocked by connectivity.
- `createNewFile(Path)` is explicitly documented as not atomic in the default implementation, so it is unsafe as a cross-client lock primitive unless a specific filesystem overrides it atomically.
- `rename(Path, Path, Rename...)` documents non-atomic default behavior and implementation-dependent atomicity. Cross-filesystem, object-store, and wrapper implementations need explicit tests for overwrite, empty-directory, and parent-directory cases.
- `exists`, `isDirectory`, `isFile`, `getLength`, `getBlockSize`, and `getReplication` are deprecated or discouraged in favor of `getFileStatus(Path)` because repeated status RPCs can be expensive and race-prone.
- `listStatus` and iterator listings do not guarantee sorted results; only `globStatus` documents sorted results. Tests and callers must avoid assuming directory order.
- Optional operations such as append, concat, truncate, symlinks, ACLs, xattrs, snapshots, storage policies, checksum retrieval, and corrupt-block listing may throw `UnsupportedOperationException`, return null, no-op, or report feature success without actual semantics depending on the filesystem.
- `CreateFlag` combinations are strict. `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE` are invalid, `APPEND` requires an existing file, and `OVERWRITE` alone requires an existing file according to the documented semantics.
- `SYNC_BLOCK` does not by itself guarantee fully synchronous behavior; the Javadoc says callers should also call `Syncable.hsync()` after each write when true synchronous behavior is required.
- `FileStatus.equals` and `hashCode` are path-based, not full metadata-based. Metadata changes may not affect equality if the path is unchanged.
- `FileStatus` returns default/empty permission, owner, or group values when the underlying filesystem lacks those concepts or cannot determine them, so callers must not assume POSIX-like metadata fidelity.
- Path handles can become invalid when encoded constraints are no longer satisfied, and support requires filesystem-specific overrides. Generic callers must handle `UnsupportedOperationException` and `InvalidPathHandleException`.
- `FileContext.setWorkingDirectory` rejects relative paths with schemes and non-existent directories; it also does not follow symlinks, which can surprise code expecting Unix working-directory inode semantics.
- `globStatus` has a nuanced null/empty distinction that can break callers that treat both as "no results."
- ACL and xattr APIs require namespace or base-entry conventions; xattr names must include a namespace prefix such as `user.` and ACL `setAcl` must include user/group/other base entries.

## Test signals

Useful test signals for this API surface include:

- JDiff/API compatibility tests should verify public/protected method signatures, overload retention, visibility, deprecation text, checked exceptions, and constants for `CommonConfigurationKeysPublic`, `ContentSummary`, `CreateFlag`, `FileChecksum`, `FileContext`, `FileStatus`, and `FileSystem`.
- Configuration tests should assert that public keys visible here resolve through `core-default.xml` where documented, including security, crypto, KMS, credential, HTTP, metrics, and shutdown defaults.
- `CreateFlag` unit tests should cover valid and invalid combinations, path-exists/path-missing create validation, append validation, and exception types.
- `FileContext` tests should cover factory construction with default config, explicit URI/config, and local filesystem; path qualification; slash-relative versus working-directory-relative names; illegal `scheme:relative` paths; umask application; and dispatch to the correct `AbstractFileSystem`.
- `FileSystem` tests should cover cached versus uncached instance creation, per-scheme cache disabling, `newInstance` uniqueness, close/closeAll behavior, and `closeAllForUGI` scoping.
- Filesystem contract tests should cover create/open/append overloads, non-recursive create parent failure, builder deferred validation, overwrite behavior, static permission helpers, primitive create/mkdir hooks, and checksum option propagation.
- Metadata tests should cover `FileStatus` serialization compatibility, protobuf conversion migration, Java serialization validation, path-based equality/hash, symlink metadata, attribute flags, and default permission/owner/group fallbacks.
- Listing tests should assert unsorted-permitted behavior for `listStatus` and iterator methods, sorted behavior for `globStatus`, null-versus-empty glob results, filtering, recursive `listFiles`, and block-location enrichment in `listLocatedStatus`.
- Mutation tests should cover rename overwrite and non-empty-directory failures, documented non-atomic defaults where applicable, truncate true/false completion semantics, delete recursive behavior, delete-on-exit queuing/canceling/processing, and shutdown cost considerations.
- Feature capability tests should explicitly exercise unsupported append, concat, ACL, xattr, symlink, snapshot, storage policy, checksum, corrupt-block, path handle, multipart upload, and open-file builder behavior for each filesystem implementation.
- Security and authorization tests should cover `AccessControlException` paths for `FileContext` and `FileSystem` methods, UGI-sensitive filesystem caching, canonical service name/token-cache integration, impersonation provider configuration, and sensitive config key redaction behavior.

### subset-b-007220: lines 12117-18225

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml lines 12117-18225

## Scope

This chunk is a generated JDiff API snapshot for Hadoop Common 3.3.5, not executable implementation source. It begins inside `org.apache.hadoop.fs.FileSystem` extended-attribute documentation and continues through complete or partial public API entries for `FileSystem`, `FileUtil`, `FilterFileSystem`, `FSBuilder`, `FsConstants`, stream classes, filesystem metadata/value classes, local filesystem implementations, multipart upload handles, `Path`, quota/storage/capability APIs, `Trash`, and the opening of `TrashPolicy`.

The XML records API compatibility metadata: class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, deprecation state, and Javadoc contracts. The merge lane must combine this chunk with adjacent chunks before making whole-file claims about `FileSystem` or `TrashPolicy`, because this chunk starts and ends in the middle of those classes.

## Purpose and major API surface

`FileSystem` is represented from xattr/storage/trash/statistics/builder methods through its class documentation. The visible API covers `listXAttrs`, `removeXAttr`, storage policy setters/getters, trash root discovery, path capability probing, implementation-class lookup via service loading, deprecated scheme-indexed statistics, global storage statistics, file create/append builders, asynchronous `openFile` builders for `Path` and `PathHandle`, protected `openFileWithOptions` execution hooks, and multipart uploader builder creation. Fields include default-FS keys, the shared `LOG`, shutdown-hook priority, trash/user-home prefixes, and per-instance `statistics`.

`FileUtil` is a static helper collection for converting `FileStatus` values to `Path`s, recursive delete and delete-on-exit, symlink target reads, filesystem-to-filesystem/local copy overloads, shell-path conversion including secure shell paths, disk usage, zip/tar extraction, local symlink/chmod/chown/permission helpers, portable read/write/execute checks, temp file creation, file replacement, checked wrappers around `File.listFiles()` and `File.list()`, manifest classpath jar creation, jar wildcard expansion, filesystem comparison, and convenience `write` overloads for bytes, line iterables, and char sequences through `FileSystem` or `FileContext`.

`FilterFileSystem` wraps an underlying `FileSystem` in protected `fs` with optional `swapScheme`. Its API mirrors the classic `FileSystem` surface and delegates URI handling, qualification, open/create/append/concat, path handles, listing, rename/delete/truncate, local copy staging, usage/defaults/status, permission/owner/time changes, symlinks, checksums, snapshots, ACLs, xattrs, storage policies, trash roots, builder APIs, protected open-file option hooks, and path capability checks.

`FSBuilder<S,B>` defines the generic builder contract used by filesystem operations. It has typed optional `opt()` and mandatory `must()` overloads for strings, primitives, and string arrays, plus `build()`. The key semantic distinction is that unsupported optional keys may be ignored, while unsupported mandatory keys are expected to make `build()` fail with `IllegalArgumentException`.

`FsConstants` exposes filesystem constants for local, FTP, viewfs, viewfs-overload target implementation patterns, viewfs type, and symlink traversal limits. These constants bind API consumers to Hadoop's scheme names and path-resolution guardrails.

`FSDataInputStream` is a buffered `DataInputStream` wrapper implementing `Seekable`, `PositionedReadable`, byte-buffer readable interfaces, file-descriptor access, readahead/drop-behind controls, enhanced byte-buffer access, unbuffering, `StreamCapabilities`, byte-buffer positioned reads, vectored reads, and `IOStatisticsSource`. `FSDataOutputStream` wraps an `OutputStream` as a `DataOutputStream`, implements `Syncable`, drop-behind, stream capabilities, IO statistics, and `Abortable`, and exposes `getPos`, `hflush`, `hsync`, `abort`, and nested-stream statistics behavior.

`FSDataOutputStreamBuilder` is the abstract create/append builder for `FSDataOutputStream`. It tracks filesystem, permission, buffer size, replication, block size, recursive parent creation, progress callback, create/overwrite/append flags, checksum options, generic optional/mandatory options inherited from `AbstractFSBuilderImpl`, and abstract `build()`. Its docs explicitly prefer implementation-agnostic option keys over `instanceof`-based filesystem branching.

`FSInputStream` is the abstract seekable input base for filesystem streams. It requires `seek`, `getPos`, and `seekToNewSource`, supplies positioned read validation, `readFully` loops, and a `toString` that can include `IOStatisticsSource` data from subclasses.

`FsServerDefaults` and `FsStatus` are value/serialization APIs. Server defaults expose block size, checksum bytes, write packet size, replication, file buffer size, data-transfer encryption, trash interval, checksum type, key provider URI, and default storage policy ID. `FsStatus` implements `Writable` for capacity, used, and remaining filesystem space.

`FutureDataInputStreamBuilder` extends `FSBuilder<CompletableFuture<FSDataInputStream>, ...>` for async-capable open operations and accepts an optional `FileStatus` hint. `Options.OpenFileOptions` provides the standard open-file option keys for length, split start/end, buffer size, read policy, and supported read-policy values such as adaptive, default, random, sequential, vector, and whole-file.

`GlobalStorageStatistics`, `StorageStatistics`, and `StorageType` expose storage telemetry and storage-media APIs. Global statistics are synchronized `get`, `put`, `reset`, and iteration operations keyed by name. `StorageStatistics` is an abstract named statistics source with long-statistic iteration, individual lookup, tracking checks, and reset. `StorageType` enumerates storage media behavior through transient, quota-supporting, movable, parsing, and filtered-list APIs.

`GlobFilter`, `PathFilter`, `Path`, `PathHandle`, and `InvalidPath*` APIs cover path matching, naming, validation, serialization, and stable/opaque references. `Path` constructors accept strings, URIs, and parent/child forms; methods strip scheme/authority, merge paths, detect Windows absolute paths, resolve owning filesystems, inspect path structure, compare/equal/hash paths, qualify paths, and validate deserialized objects. `PathHandle` serializes opaque file references to byte arrays/byte buffers and can fail later through `InvalidPathHandleException` if encoded constraints no longer hold.

`LocalFileSystem` and `RawLocalFileSystem` are local implementations. `LocalFileSystem` is a checksumed wrapper over a raw filesystem and exposes local path conversion, local copy methods, checksum failure handling, and symlink support. `RawLocalFileSystem` is the direct `file:` implementation with open/create/append/createNonRecursive, local output stream hooks, concat/rename/truncate/delete/list/mkdir/status, working directory, owner/permission/times using platform commands, path handles, symlink APIs, and path capability checks.

`LocatedFileStatus`, `PartialListing`, `PartHandle`, and `MultipartUploader` support listing and upload workflows. `LocatedFileStatus` extends `FileStatus` with block locations and constructors including ACL/encryption/erasure-coded flags and generic attr flags. `PartialListing` represents one batch of a potentially multi-batch listing and may rethrow a stored `RemoteException` on `get()`. `PartHandle` is the opaque serializable multipart part reference. `MultipartUploader` is an async API for start, part upload, complete, abort, and best-effort abort-under-path operations, and also advertises IO statistics.

`PositionedReadable`, `Seekable`, `ReadOption`, `StreamCapabilities`, `StreamCapabilitiesPolicy`, and `Syncable` define stream contracts. Positioned reads must not alter the current stream offset and are documented as thread-safe requirements, though not all filesystems satisfy them. Vectored reads attach futures to file ranges and may leave stream position undefined. Stream capabilities use lowercase string constants for optional features such as `hflush`, `hsync`, readahead, drop-behind, unbuffer, byte-buffer reads, IO statistics, vectored IO, abortable streams, and IO statistics contexts. `Syncable` separates `hflush` visibility from `hsync` disk-flush semantics.

`QuotaUsage` is a directory quota value class with namespace quota/count, space consumed/quota, per-`StorageType` quotas/consumption, availability checks, equality/hash behavior, CLI header/format helpers, human-readable and storage-type string output. `Trash` is a configured facade around pluggable trash policies, with constructors for default or explicit filesystem, mount/symlink-aware `moveToAppropriateTrash`, `moveToTrash`, checkpoint, expunge, immediate expunge, emptier runnable, and current trash directory lookup. `TrashPolicy` starts at the end of this chunk and includes old/new initialization contracts plus abstract enablement, move, checkpoint, delete checkpoint, and a truncated `deleteCheckpointsImmediately` declaration.

## Control flow and behavioral contracts

The XML has no executable control flow, but the Javadoc captures API-level flow. `FileSystem.openFile(Path|PathHandle)` returns a builder; preconditions and actual open may be deferred to `build()`. Protected `openFileWithOptions` is the implementation hook called by the builder and `DelegateToFileSystem`; the base contract performs a blocking `open(Path, int)` but wraps the outcome in a `CompletableFuture`, so callers must evaluate the future to observe failures. Mandatory unknown open options produce `IllegalArgumentException`; unsupported path handles may fail immediately or when the future is evaluated.

Create and append flow is builder-driven. `FileSystem.createFile(path)` creates an `FSDataOutputStreamBuilder` that overwrites by default, while `appendFile(path)` sets up append. The builder accumulates permission, buffer, replication, block size, progress, recursive parent creation, create/overwrite/append flags, checksum options, and generic options before `build()` asks the filesystem to create or append. Missing parent creation is opt-in via `recursive()`.

`FilterFileSystem` is a delegation flow. Its public surface is intentionally broad because it must pass through new `FileSystem` APIs to its wrapped filesystem. The `FileSystem` docs warn maintainers that adding public/protected methods requires updating `FilterFileSystem`, `ChecksumFileSystem`, HAR tests, and path capability behavior; in particular, `FilterFileSystem.hasPathCapability()` must return false for newly probed capabilities unless support is intentionally known.

`FileUtil.copy` has recursive and destructive behavior. When `deleteSource` is true, source deletion happens as each subtree is copied; a mid-copy failure may leave the source tree partially deleted. Destination-directory handling can return false rather than throw if `mkdirs(dst)` fails. Overwrite only applies to files, not file-over-directory or directory-over-file mismatches.

`FSDataInputStream` delegates capability-specific calls to its wrapped stream. It supports seek and positioned reads, pooled byte-buffer reads, byte-buffer positioned reads, vectored reads, readahead, drop-behind, unbuffer, and IO statistics only when the nested stream supports the relevant interfaces or policies. `FSDataOutputStream` similarly delegates sync, drop-behind, abort, and statistics behavior to the wrapped stream and exposes unsupported-operation paths when unavailable.

`MultipartUploader` flow is explicitly asynchronous and stateful: `startUpload(Path)` returns an upload handle, `putPart()` can run out of order or in parallel and must close the supplied input stream after reading, `complete()` takes a non-empty map of part numbers to handles and returns a `PathHandle`, and `abort()`/`abortUploadsUnderPath()` clean up pending uploads. Abort-under-path is best effort and may miss uploads when listing is eventually consistent.

`Path` flow normalizes URI-like path strings but with unescaped elements and Hadoop-specific handling. FileSystem resolution uses `Path.getFileSystem(Configuration)`, qualification uses filesystem URI and working directory, and deserialization runs `validateObject()` to reject malicious or invalid object streams without a URI.

`Trash.moveToAppropriateTrash()` resolves symlinks or mount points to the actual volume, gets the filesystem for the fully qualified resolved path, and moves the original path into the trash root for that volume. `TrashPolicy.initialize(Configuration, FileSystem)` supersedes the older home-directory based initializer because trash placement cannot always assume `/user/$USER` under HDFS encryption zones.

## State, persistence, and side effects

The JDiff file itself is persistent API metadata used by compatibility checks. Runtime state described by this chunk belongs to the Hadoop APIs, not to the XML.

Persistent filesystem effects include xattr removal/listing, storage policy updates, file create/append/open, multipart uploads, local and remote copy, recursive delete, symlink creation, chmod/chown/permission changes, owner/time updates, directory creation, concat, rename, truncate, trash movement/checkpointing/expunge, path-handle validation, and quota/statistics reporting. Many APIs throw `IOException` and some optional operations throw `UnsupportedOperationException`.

Process-level state appears in statistics and caches. `FileSystem` has per-instance `statistics`, deprecated static statistics maps, global storage statistics, shutdown hook priority, and constants used by shutdown/trash behavior. `GlobalStorageStatistics` is synchronized and stores named providers; `StorageStatistics` objects can reset tracked counters.

Local filesystem state is especially platform-sensitive. `RawLocalFileSystem` maps Hadoop `Path` objects to `java.io.File`, uses host file permissions, can call shell/platform utilities for owner and permission changes, and returns unsorted local listings because it relies on Java `File.list()`. `FileUtil` helpers can create/delete local files, expand archives, generate classpath jars, replace files, and register recursive delete-on-exit work.

Stream state includes current input/output positions, optional read-ahead/drop-behind hints, pooled byte buffers that must be released, unbuffered resources, and vectored read futures attached to ranges. `PositionedReadable.readVectored()` documents that stream position after the call is undefined and that file mutation during a vectored read produces undefined mixed data.

Value classes store serializable metadata snapshots. `FsServerDefaults`, `FsStatus`, `LocatedFileStatus`, `QuotaUsage`, `PartHandle`, and `PathHandle` carry state across process or RPC boundaries; handles are intentionally opaque and may encode constraints checked on later access.

## Dependencies and integration points

These APIs integrate with Hadoop Common filesystem types including `Path`, `FileSystem`, `FileContext`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `FutureDataInputStreamBuilder`, `PathHandle`, `PartHandle`, `UploadHandle`, `MultipartUploaderBuilder`, `RemoteIterator`, `FileRange`, `FsStatus`, `FsServerDefaults`, `BlockStoragePolicySpi`, `StorageStatistics`, `GlobalStorageStatistics`, `StorageType`, `Options`, `CreateFlag`, and `ReadOption`.

Permission, security, and metadata integration points include `FsPermission`, `FsAction`, ACL entry/status classes, `XAttrSetFlag`, `AccessControlException`, `Configuration`, `Configured`, `Progressable`, `IOStatisticsSource`, `IOStatistics`, `ByteBufferPool`, `DataChecksum.Type`, and `RemoteException`.

Java and platform dependencies include `URI`, `File`, `FileDescriptor`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `ByteBuffer`, `EnumSet`, `CompletableFuture`, `IntFunction`, `Iterator`, `Map`, `List`, `Collection`, `Set`, `Serializable`, `Comparable`, `Closeable`, and local shell/platform command behavior for symlink, chmod, chown, archive extraction, and Windows path/permission handling.

Compatibility tooling depends on the structured XML attributes more than implementation code. Any public/protected signature, visibility, deprecation, exception, field, or documentation-contract change in this source API surface can affect JDiff comparisons between Hadoop releases.

## Risks and compatibility notes

This chunk is line-bounded and partial at both ends. It should not be used alone to summarize all of `FileSystem` or `TrashPolicy`; adjacent chunks are needed for complete class coverage.

Builder option handling is compatibility-sensitive. Optional keys may be ignored, but mandatory keys must fail if unsupported or invalid. Filesystem-specific builders must recognize standard `Options.OpenFileOptions` keys even when values are ignored, or generic callers can break.

Asynchronous APIs may still perform blocking work in default implementations. `openFileWithOptions()` returns a `CompletableFuture`, but the base contract performs the open call synchronously before returning a completed/failing future. Callers and tests should not assume background execution unless a concrete filesystem documents it.

Positioned and vectored reads have subtle consistency and concurrency risks. The API requires thread-safe positioned reads, while warning that not all implementations satisfy this. Vectored reads can block normal reads, leave current position undefined, and return undefined data if the file changes during the operation.

`FileUtil` deletion/copy helpers can leave partial results. Recursive delete returns false after partial deletion, and copy with `deleteSource` can delete subtrees as work progresses. Cleanup logic must not assume atomic copy/delete semantics.

Local filesystem behavior varies by platform. Windows path handling, symlink privilege failures, permission checks, execute-bit semantics on directories, unsorted listings, and shell command availability can change behavior even though the public API is stable.

Opaque handles and multipart uploads encode implementation-specific state. `PathHandle` and `PartHandle` equality/serialization must remain stable enough for retries, but `InvalidPathHandleException` is expected when encoded constraints no longer match. Multipart abort-under-path is explicitly best effort and can miss uploads under eventually consistent listing systems.

Trash behavior depends on filesystem resolution, mount points, symlinks, encryption zones, configured policy, and user trash roots. The older `TrashPolicy.initialize(conf, fs, home)` is deprecated because it assumes a home-rooted trash layout that is not always valid.

## Test signals

JDiff validation should confirm the XML remains well-formed and preserves all class/interface boundaries in this line range, including the partial `FileSystem` and partial `TrashPolicy` entries. API compatibility tests should check signatures, visibility, exceptions, field names, and deprecation strings for the covered methods.

Filesystem contract tests should exercise `FileSystem` xattr/storage-policy/trash-root APIs, `hasPathCapability`, global/per-instance statistics, `createFile`, `appendFile`, `openFile(Path)`, `openFile(PathHandle)`, open options, multipart uploader creation, and default unsupported-operation paths.

Wrapper tests should run core operations through `FilterFileSystem` and verify delegation for URI handling, path qualification, open/create/append/list/delete/rename/truncate, local copies, defaults/status, permissions, symlinks, checksums, snapshots, ACLs, xattrs, storage policies, trash roots, builders, and path capability behavior.

Stream tests should cover seek/getPos/readFully, byte-buffer reads, byte-buffer positioned reads, readahead/drop-behind, file descriptor availability, pooled buffer release, unbuffer policy, stream capability strings, IO statistics fallback behavior, hflush/hsync, abortable output streams, and vectored read edge cases.

Local utility tests should cover recursive delete of files/directories/symlinks, partial-failure behavior, archive extraction, secure shell path conversion, chmod/chown/setPermission portability, Windows symlink privilege return code, null-safe listing wrappers, classpath jar generation with environment-variable and wildcard expansion, and write helpers for `FileSystem` and `FileContext`.

Value-object tests should cover `Path` normalization and Windows absolute path detection, deserialization validation, `PathHandle` and `PartHandle` byte serialization/equality, `LocatedFileStatus` block-location equality/hash behavior, `FsStatus` writable round trips, `FsServerDefaults` getters, `QuotaUsage` string/header formatting with storage types, and `StorageType` parsing/filtering.

Trash tests should cover disabled trash, already-in-trash returns, mount/symlink-aware `moveToAppropriateTrash`, checkpoint creation, old checkpoint deletion, immediate expunge, emptier runnable creation for superuser-style cleanup, encryption-zone-aware `TrashPolicy.initialize(conf, fs)`, and legacy initializer compatibility.

### subset-b-007221: lines 18226-24779

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml lines 18226-24779

## Scope

This chunk is part 4 of the Hadoop Common 3.3.5 JDiff API snapshot. It starts inside the tail of `org.apache.hadoop.fs.TrashPolicy`, finishes the visible `org.apache.hadoop.fs` package entries in this range, covers `org.apache.hadoop.fs.audit`, `org.apache.hadoop.fs.ftp`, `org.apache.hadoop.fs.statistics`, `org.apache.hadoop.ha`, `org.apache.hadoop.ha.protocolPB`, and begins `org.apache.hadoop.io` through `ShortWritable.toString()`.

The file is generated API metadata, not runtime source. It records public/protected type declarations, inheritance, constructors, methods, parameters, exceptions, fields, deprecation strings, and Javadoc. Control-flow and persistence notes below are therefore derived from signatures and API contracts, especially where the XML documents durable file formats or mutable state.

## Purpose

The source file is a compatibility baseline for Hadoop Common 3.3.5. This slice captures several stable surfaces used by filesystem clients, object-store instrumentation, HA administration, RPC protocol binding, and Hadoop binary serialization.

The filesystem tail records trash policy behavior, unsupported filesystem/upload exceptions, multipart upload handles, extended attribute encoding, and XAttr creation/replacement validation. `CommonAuditContext` captures thread-local and global audit attributes that filesystem audit spans can include in downstream logging or HTTP referrer headers. `FTPFileSystem` exposes the legacy FTP `FileSystem` implementation and its configuration keys.

The statistics package records the low-cost `IOStatistics` contract used by filesystem and stream implementations to publish counters, gauges, min/max values, and mean statistics. It also defines common statistic-name constants for store operations, object-store multipart uploads, HTTP actions, read streams, write streams, buffering, and remote reads.

The HA package defines the client-side failover and fencing API: service health checks, transitions to active/standby/observer, status retrieval, target addressing, fencing configuration, and protocol-buffer RPC marker interfaces. The `org.apache.hadoop.io` section begins Hadoop's core `Writable` data model and persistent file containers, including primitive wrappers, byte/array wrappers, map writables, object serialization, `MapFile`, and `SequenceFile` writer creation.

## Important APIs, Types, and Functions

### Filesystem tail and audit context

- `TrashPolicy` methods in this range include `deleteCheckpointsImmediately()`, legacy `getCurrentTrashDir()`, path-aware `getCurrentTrashDir(Path)`, `getEmptier()`, and factory overloads `getInstance(Configuration, FileSystem, Path)` and `getInstance(Configuration, FileSystem)`. Protected fields `fs`, `trash`, and `deletionInterval` define the policy's filesystem, trash directory, and checkpoint interval state. The legacy current-trash API is documented as unsafe for HDFS encryption-zone deletes, with callers directed to the path-aware overload.
- `UnsupportedFileSystemException` and `UnsupportedMultipartUploaderException` are `IOException` subclasses with string-message constructors, used when a filesystem scheme or multipart uploader implementation is unavailable.
- `UploadHandle` is an opaque multipart-upload identifier. It extends `Serializable`, exposes `bytes()` as a `ByteBuffer`, has a default `toByteArray()`, and requires `equals(Object)`.
- `XAttrCodec` converts XAttr byte arrays to and from textual representations. `decodeValue(String)` recognizes `0x`/`0X` hex, `0s`/`0S` base64, and quoted or unquoted text. `encodeValue(byte[], XAttrCodec)` emits quoted text, hex, or base64 with prefixes.
- `XAttrSetFlag.validate(String, boolean, EnumSet)` validates create/replace flag combinations against whether an xattr already exists.
- `CommonAuditContext` is a final audit metadata holder. It supports string or supplier-valued `put()`, `remove()`, `get()`, `containsKey()`, `reset()`, `getEvaluatedEntries()`, thread-local `currentAuditContext()`, process-unique `currentThreadID()`, global context setters/getters/removal, `getGlobalContextEntries()`, and `noteEntryPoint(Object)`. `PROCESS_ID` is public and is documented as UUID/timestamp based.

### FTP filesystem

- `FTPException` wraps a message, cause, or both.
- `FTPFileSystem` extends Hadoop's `FileSystem` API with `getScheme()`, `getDefaultPort()`, `initialize(URI, Configuration)`, `open(Path, int)`, `create(Path, FsPermission, boolean, int, short, long, Progressable)`, unsupported `append(Path, int, Progressable)`, `delete(Path, boolean)`, `getUri()`, `listStatus(Path)`, `getFileStatus(Path)`, `mkdirs(Path, FsPermission)`, `rename(Path, Path)`, `getWorkingDirectory()`, `getHomeDirectory()`, and `setWorkingDirectory(Path)`.
- Public constants include defaults for buffer size, block size, timeout, configuration prefixes/keys for user, host, port, password, data connection mode, transfer mode, timeout, and `E_SAME_DIRECTORY_ONLY` for rename restrictions.

### IO statistics

- `DurationStatisticSummary` summarizes duration metrics with key, success flag, count, min, max, and `MeanStatistic`, and can fetch duration or success summaries from an `IOStatistics` source.
- `IOStatistics` is the base interface returning maps for `counters()`, `gauges()`, `minimums()`, `maximums()`, and `meanStatistics()`. `MIN_UNSET_VALUE` and `MAX_UNSET_VALUE` mark unset extrema.
- `IOStatisticsAggregator.aggregate(IOStatistics)` merges statistics into an implementation-specific aggregate and returns whether a non-null source was processed.
- `IOStatisticsLogging` stringifies `IOStatistics` or `IOStatisticsSource`, provides lazy `toString()` wrappers for low-cost logging, and logs statistics at debug or named levels while swallowing source extraction failures into debug logging.
- `IOStatisticsSnapshot` implements `IOStatistics`, `Serializable`, and `IOStatisticsAggregator`. It can be built empty or from a source, synchronizes `clear()`, `snapshot()`, `aggregate()`, and map accessors, exposes `serializer()` as `JsonSerialization`, and lists `requiredSerializationClasses()` for safer deserialization.
- `IOStatisticsSupport` builds empty or populated snapshots, retrieves statistics from either an `IOStatistics` instance or `IOStatisticsSource`, and returns singleton no-op duration tracker factory/tracker implementations.
- `MeanStatistic` is a synchronized, serializable, cloneable `(samples, sum)` pair. It handles invalid sample counts by resetting to empty, supports getters, clear, set, add another statistic, add a sample, `mean()`, equality/hash, clone/copy, and string rendering.
- `StoreStatisticNames` and `StreamStatisticNames` are constant catalogs. Store names cover filesystem API operations, xattr operations, delegation tokens, object-store probes, throttling/rate limiting/retries, list/delete/copy/metadata requests, HTTP verbs, multipart upload lifecycle, and suffixes for min/max/mean/failure metrics. Stream names cover read open/close/abort, read bytes and operations, vectored reads, seeks/skips, unbuffering, write failures, block upload queues, uploaded/failed byte counts, task wait time, buffer reads, remote reads, read-ahead, and block allocation/release.

### High availability APIs

- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` are HA-specific exception types with message and message/cause constructors where applicable.
- `FenceMethod` validates fencing method arguments via `checkArgs(String)` and attempts fencing with `tryFence(HAServiceTarget, String)`, returning whether the target was fenced.
- `HAServiceProtocol` defines RPC operations `monitorHealth()`, `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(StateChangeRequestInfo)`, `transitionToObserver(StateChangeRequestInfo)`, and `getServiceStatus()`, plus `versionID`.
- `HAServiceProtocolHelper` wraps the transition and health RPC calls, preserving the same operation set for callers.
- `HAServiceTarget` abstracts a target used by HA admin clients. It exposes primary, health-monitor, and ZKFC addresses; fencer lookup and configuration checks; normal and health-monitor proxies with timeouts; ZKFC proxy creation; fencing parameters with subclass extension; auto-failover flag; observer support flag; and transition-target HA status accessors.
- `HAServiceProtocolPB` and `ZKFCProtocolPB` are protocol-buffer service marker interfaces extending the generated blocking protobuf interfaces and Hadoop `VersionedProtocol`.

### Hadoop IO and writable APIs in this chunk

- `AbstractMapWritable` implements `Writable` and `Configurable`. It maintains per-instance class-to-id and id-to-class tables for `MapWritable` and related classes, with `addToMap()`, `getClass(byte)`, `getId(Class)`, `copy(AbstractMapWritable)`, configuration accessors, and `write()`/`readFields()`.
- `ArrayFile`, `BloomMapFile`, `MapFile`, and `SetFile` are file-backed containers. `MapFile` exposes directory `rename()`, `delete()`, index repair via `fix(FileSystem, Path, Class, Class, boolean, Configuration)`, `main()`, and `INDEX_FILE_NAME`/`DATA_FILE_NAME`. `BloomMapFile` adds `delete()` and constants `BLOOM_FILE_NAME` and `HASH_COUNT`.
- `ArrayPrimitiveWritable` wraps primitive Java arrays without copying, records declared/component type, supports `set(Object)`, `get()`, `write()`, and `readFields()`.
- `ArrayWritable` serializes homogeneous arrays of `Writable` values, with constructors for value class, value class plus values, and `String[]`; accessors `getValueClass()`, `get()`, `set()`, `toArray()`, `toStrings()`, `readFields()`, `write()`, and `toString()`.
- `BinaryComparable` supplies byte-based comparison over `getBytes()` and `getLength()`, plus byte-slice comparison, equality, and hash.
- Primitive writables present in this range include `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, `LongWritable`, and `ShortWritable`. Each follows the standard mutable wrapper pattern: constructors, `set()`, `get()`, `readFields(DataInput)`, `write(DataOutput)`, equality, hash, comparison, and string conversion.
- `BytesWritable` is a mutable byte sequence with exact copy access (`copyBytes()`), backing-array access (`getBytes()` and deprecated `get()`), logical length/capacity access and mutation, range `set()` overloads, writable serialization, comparison-compatible equality/hash, and hex-pair `toString()`.
- `ByteBufferPool` provides `getBuffer(boolean direct, int length)`, `putBuffer(ByteBuffer)`, and `release()`. `ElasticByteBufferPool` implements it by creating buffers as needed and retaining released buffers for reuse.
- `CompressedWritable` is a base class for writables that store compressed bytes and inflate lazily. Subclasses implement `readFieldsCompressed(DataInput)` and `writeCompressed(DataOutput)` and must call `ensureInflated()` before accessing fields.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`, including `constructOutputStream(DataOutput)` and byte write overloads.
- `DefaultStringifier<T>` implements `Stringifier<T>` for Hadoop serialization encoded as base64 strings, with static helpers `store()`, `load()`, `storeArray()`, and `loadArray()` against `Configuration`.
- `EnumSetWritable<E>` wraps an `EnumSet`, implements `Writable` and `Configurable`, carries an element type for null/empty sets, and supports iteration, size, add, set, get, serialization, equality/hash, element-type access, and configuration accessors.
- `GenericWritable` wraps one writable from a fixed subclass-declared type list from `getTypes()`, with compact type-index serialization and `Configurable` integration.
- `IOUtils` is a broad stream/file utility class covering `copyBytes()` overloads, compressed-data read wrapping, exact `readFully()` and `skipFully()`, cleanup and close helpers, socket close, full `ByteBuffer` writes to channels/files, directory listing with exception propagation, file/channel `fsync()`, exception wrapping with path/method context, and `readFullyToByteArray()`.
- `MapWritable` implements `Map<Writable, Writable>` and writable serialization, including copy construction and the standard `Map` operations.
- `MD5Hash` is a `WritableComparable` digest wrapper with constructors from empty, hex string, or bytes; `read()` helper; digest setters/getters; static digest helpers for byte arrays, byte-array arrays, strings, and streams; thread-local digester creation; half/quarter digest projections; and natural ordering.
- `MultipleIOException` encapsulates a list of `IOException` instances and has `createIOException(List)` to return a single exception or wrapper.
- `NullWritable` is the singleton no-data writable, with no-op read/write and stable equality/ordering.
- `ObjectWritable` is polymorphic writable serialization for `Writable`, `String`, primitives, and arrays, storing declared class metadata. Static `writeObject()` and `readObject()` have configuration-aware overloads and an `allowCompactArrays` option; `loadClass(Configuration, String)` resolves serialized class names.
- `RawComparator<T>` compares serialized byte ranges directly without requiring object materialization.
- `SequenceFile` exposes default compression type getters/setters and many `createWriter()` overloads, including modern `Writer.Option...` and deprecated legacy overloads for `FileSystem`, `FileContext`, `FSDataOutputStream`, key/value classes, compression type, codec, progress, metadata, buffer size, replication, block size, create-parent flag, create flags, and create options. `SYNC_INTERVAL` is the public default sync interval.
- The `SequenceFile` Javadoc specifies persistent formats: a common header with magic/version, key/value class names, compression flags, codec, metadata, and sync marker; uncompressed records; record-compressed records; and block-compressed records with grouped/compressed key lengths, keys, value lengths, and values.

## Control Flow

JDiff itself has no runtime flow. Runtime behavior is visible through API contracts.

Trash policy flow is filesystem-configuration driven: callers obtain an implementation via `TrashPolicy.getInstance()`, move/delete paths through policy-specific code outside this chunk, ask for a path-specific trash directory when encryption zones matter, and run the returned emptier as a superuser maintenance task. XAttr flow is decode/validate/encode around shell, HTTP, JSON, or filesystem calls.

Audit flow is context propagation. A caller mutates the thread-local `CommonAuditContext`, optionally sets global attributes, and audit spans retain a reference to the context from the thread where they were created. Supplier-valued entries are evaluated later by `getEvaluatedEntries()`, potentially in another thread.

FTP filesystem flow follows the Hadoop `FileSystem` contract but is constrained by FTP protocol state. `initialize()` configures connection details, `open()` and `create()` create streams, `append()` is explicitly unsupported, and rename/delete/list/status/mkdir/working-directory methods operate through remote FTP commands.

Statistics flow starts with live `IOStatistics` maps on a stream or store. `IOStatisticsSupport.retrieveIOStatistics()` extracts them from a source, `IOStatisticsSnapshot.snapshot()` copies them, `aggregate()` merges them into synchronized map state, and logging utilities defer expensive stringification until a log statement evaluates the wrapper object.

HA control flow is command/RPC oriented. Admin clients identify an `HAServiceTarget`, optionally check fencing configuration, obtain protocol proxies, monitor health, request state transitions, and fence failed peers through a configured `FenceMethod`. Observer transition support is explicit and can be disabled by a target.

Writable control flow is caller-driven serialization. Writers call `write(DataOutput)` in deterministic order; readers instantiate or reuse an object and call `readFields(DataInput)` in the matching order. Containers add length/type/class metadata before delegating nested payloads. `RawComparator` and `BinaryComparable` support sort/shuffle paths that compare serialized bytes directly.

SequenceFile writer flow converges through overloads into a writer configured with filesystem/path or raw output stream, key/value classes, compression type, optional codec, metadata, and creation options. Records are then laid out in one of the documented uncompressed, record-compressed, or block-compressed forms with sync markers for resynchronization.

## State and Persistence Behavior

The XML file persists the Hadoop Common 3.3.5 API surface for compatibility tooling. It does not persist application runtime state.

The APIs described here are stateful in several ways. `TrashPolicy` carries filesystem, trash path, and deletion interval. `CommonAuditContext` has thread-local maps, global maps, supplier-valued entries, a process id, and generated thread ids. Its Javadoc warns that long-lived suppliers must not capture large object instances and should be removed when no longer needed.

`IOStatisticsSnapshot` intentionally persists copied statistics maps and is `Serializable` so frameworks such as Spark or Flink can propagate statistics. The docs warn not to deserialize untrusted Java object streams unless the required class list is used. `MeanStatistic` persists sum/sample state and normalizes invalid sample counts to an empty statistic.

Writable classes define binary persistence contracts through `write()` and `readFields()`. Mutable wrappers store current primitive values, byte arrays, array references, maps, declared classes, element types, or class-id maps. `BytesWritable.getBytes()` exposes backing capacity, not only logical length. `ArrayPrimitiveWritable` wraps primitive arrays without copying. `CompressedWritable` stores compressed bytes until lazy inflation.

`AbstractMapWritable` and `MapWritable` persist per-instance class-id tables along with entries. `ObjectWritable` persists class names/declared types and payloads, creating compatibility and classloading dependencies at read time. `DefaultStringifier` stores serialized objects as strings in `Configuration`.

File persistence is explicit in `MapFile` and `SequenceFile`. `MapFile` uses directory state with `data` and `index` files and can rebuild a corrupt index from data. `SequenceFile` persists key/value class names, compression metadata, sync markers, and one of three documented record/block layouts. These formats are durable compatibility contracts for Hadoop data files.

## Dependencies and Integration Points

- Java APIs: `IOException`, `Serializable`, `ByteBuffer`, `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `FileChannel`, `WritableByteChannel`, `Socket`, `MessageDigest`, `URI`, `InetSocketAddress`, collections, `Supplier`, and Java serialization.
- Hadoop configuration and filesystem APIs: `Configuration`, `Configurable`, `FileSystem`, `FileContext`, `Path`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `FsPermission`, `Options.CreateOpts`, and `Progressable`.
- Hadoop audit and object-store integration: `CommonAuditContext` references `AuditConstants#PARAM_COMMAND` and `HttpReferrerAuditHeader`, and the statistic-name constants are clearly aligned with S3A/object-store operations, multipart uploads, HTTP actions, vectored reads, seeks, and remote stream handling.
- HA/RPC integration: `HAServiceProtocol`, `HAServiceTarget`, `ZKFCProtocol`, protobuf generated blocking interfaces, and Hadoop `VersionedProtocol`.
- Hadoop serialization/data path integration: `Writable`, `WritableComparable`, `RawComparator`, `SequenceFile`, `MapFile`, `ObjectWritable`, `GenericWritable`, `Stringifier`, `JsonSerialization`, and compression codec classes referenced by `SequenceFile`.
- Logging integration: `org.slf4j.Logger` is used by `FTPFileSystem`, `IOStatisticsLogging`, and `IOUtils`.

## Risks and Edge Cases

- The chunk starts inside `TrashPolicy` and ends inside `ShortWritable`; adjacent chunk research must be merged before making whole-class claims about either boundary.
- JDiff records API shape and Javadocs, not implementation bodies. Details such as FTP command sequencing, synchronization internals, map implementations, buffer growth, and exact exception messages require Java source validation.
- The old `TrashPolicy.getCurrentTrashDir()` is documented as incorrect for HDFS encryption-zone deletes. Callers deleting encryption-zone paths should use `getCurrentTrashDir(Path)`.
- `CommonAuditContext` supplier entries are long-lived and may be evaluated on another thread. Capturing large objects, request-scoped objects, or mutable state can create memory leaks or misleading audit output.
- `IOStatisticsSupport.snapshotIOStatistics()` is explicitly not atomic. Concurrent updates can produce mixed snapshots unless the source implementation provides its own synchronization.
- `IOStatisticsSnapshot` is serializable, but its Javadoc warns against untrusted Java deserialization. Tests and integrations should prefer controlled class lists or JSON serialization when crossing trust boundaries.
- Statistic-name constants are cross-component contracts. Renaming or reusing a key can break dashboards, assertions, object-store diagnostics, and downstream log parsers.
- FTP filesystem semantics are weaker than HDFS/local filesystems. Append is unsupported; rename is constrained by same-directory behavior; streams may need to be closed before other APIs are used; credentials and host details are configuration-sensitive.
- HA fencing is safety-critical. A `tryFence()` false result or misvalidated args can permit split-brain. Observer transitions require explicit target support.
- Writable binary compatibility is fragile. Changes to field order, class metadata, length prefixes, enum element typing, or `ObjectWritable` compact-array mode can break persisted files, RPC payloads, and inter-version reads.
- Backing-array exposure in `BytesWritable` and no-copy array wrapping in `ArrayPrimitiveWritable` can leak stale bytes, retain large buffers, or allow external mutation after serialization assumptions have been made.
- `SequenceFile` has many deprecated writer overloads kept for compatibility. New code should use `createWriter(Configuration, Writer.Option...)`, but compatibility tests must still cover legacy overload behavior.
- `MapFile.fix()` can repair an index from data, but incorrect key/value classes or data corruption can produce partial recovery or misleading valid-entry counts.

## Test Signals

- API baseline tests should verify this JDiff slice remains well-formed around the chunk boundaries and that generated signatures/deprecations match Java sources for Hadoop Common 3.3.5.
- Trash tests should cover checkpoint deletion, path-aware trash location under encryption-zone and non-encryption-zone paths, emptier behavior, configured policy instantiation, and deprecation compatibility for the old factory.
- XAttr tests should round-trip text, quoted text, hex, base64, invalid encodings, and `XAttrSetFlag.validate()` create/replace combinations.
- Audit tests should cover thread-local isolation, global context propagation, `noteEntryPoint()`, supplier evaluation/removal, `reset()` behavior, process/thread id stability, and memory-sensitive supplier cleanup.
- FTP tests should cover configuration keys, default port/scheme, open/create stream close ordering, unsupported append, recursive and nonrecursive delete, same-directory rename constraints, list/status/mkdirs, working directory behavior, and timeout/data-transfer modes.
- IO statistics tests should cover all map categories, unset min/max sentinels, `DurationStatisticSummary` extraction, synchronized snapshot and aggregate behavior, mean-statistic invalid sample handling, JSON serialization, required deserialization classes, lazy logging wrappers, null/wrong-type sources, and stable statistic-name constants.
- HA tests should cover `FenceMethod.checkArgs()` and `tryFence()`, target proxy creation with timeouts, transition request helper methods, health-monitor address fallback/separation, ZKFC proxy lookup, fencing parameter extension, auto-failover flags, observer support, and protobuf protocol version compatibility.
- Writable tests should round-trip every primitive writable in this chunk, `BytesWritable`, arrays, enum sets, maps, object wrappers, `MD5Hash`, `NullWritable`, and compressed writables. Include golden-byte compatibility tests against earlier Hadoop versions where serialized formats are durable.
- Comparator tests should compare object-level ordering with raw byte ordering for `BinaryComparable`, primitive writables, `BytesWritable`, and `MD5Hash`.
- `IOUtils` tests should simulate partial reads/skips/writes, EOF, cleanup swallowing/logging, socket close, directory-list exceptions, fsync on file and directory paths, compressed-read exception wrapping, and unbounded `readFullyToByteArray()` memory risk.
- `MapFile`/`SequenceFile` tests should cover writer overloads, metadata, compression type defaults, codec use, sync markers, create-parent behavior, raw output-stream writers, corrupt/missing index repair, dry-run repair, and directory constant expectations.

## Cross-Chunk Notes

`subset-b-007220` should contain the earlier part of `TrashPolicy` and filesystem APIs preceding this slice. `subset-b-007222` should continue after `ShortWritable`, including the rest of `org.apache.hadoop.io` and subsequent packages. The merge lane should preserve this chunk as a source-aligned subsection and avoid treating it as a complete file-level analysis until all seven chunks for `Apache_Hadoop_Common_3.3.5.xml` are present.

### subset-b-007222: lines 24780-31074

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml lines 24780-31074

Chunk: `subset-b-007222`
Lines researched: 24780-31074 of generated JDiff XML for `Apache Hadoop Common 3.3.5`.

## Scope

This chunk is a line-bounded slice of Hadoop Common 3.3.5's generated JDiff API snapshot. It is not implementation source; it records public/protected API metadata: packages, class/interface names, inheritance, implemented interfaces, constructors, methods, fields, static/final/abstract/synchronized flags, visibility, checked exceptions, deprecation markers, and Javadoc text.

The slice starts inside the end of `org.apache.hadoop.io.ShortWritable`, then covers a large run of `org.apache.hadoop.io`, compression, erasure-code schema, TFile, serializer, log metrics, and metrics2 APIs. It ends at the opening method of `org.apache.hadoop.metrics2.lib.MutableGaugeInt`, so that class is incomplete in this chunk and must be reconciled with the next chunk for a full type report.

## Purpose

The `org.apache.hadoop.io` portion documents Hadoop's core serialization and comparison primitives. These APIs provide the `Writable` contract, comparable value wrappers, raw-byte comparators, factory hooks for instantiating Writables, UTF-8 text handling, variable-length integer encodings, arrays, map wrappers, and utility helpers used throughout Hadoop RPC, file formats, MapReduce shuffle/sort, and configuration serialization.

The `org.apache.hadoop.io.compress` portion documents the codec SPI and concrete codec wrappers for block, stream, gzip, bzip2, default/zlib, passthrough, and splittable compression. These APIs define how Hadoop discovers codecs, leases compressor/decompressor instances, wraps input/output streams, supports direct decompression, and handles split boundaries for compressed files.

The `org.apache.hadoop.io.erasurecode`, `org.apache.hadoop.io.file.tfile`, and serializer portions document smaller but important integration APIs: erasure coding schema descriptors, TFile constants/helpers/raw comparable interfaces, and pluggable Java/Writable/Avro serialization adapters.

The `org.apache.hadoop.metrics2` and `org.apache.hadoop.metrics2.lib` portion documents the metrics framework public surface. It defines metric values, tags, records, collectors, builders, sources, sinks, filters, visitors, plugin lifecycle, metrics system lifecycle, singleton access, registries, interned metadata, and the first mutable counter/gauge types.

## Important APIs, Types, and Functions

### Hadoop IO and Writable APIs

- `ShortWritable` is only partially visible at the chunk start. The visible tail includes `toString()` returning short values in string form and class documentation identifying it as a `WritableComparable` for shorts.
- `SortedMapWritable` extends `AbstractMapWritable` and implements `java.util.SortedMap`. It exposes default and copy constructors, sorted-map navigation (`comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`), normal map operations, `readFields(DataInput)`, `write(DataOutput)`, `equals`, and `hashCode`.
- `Stringifier<T>` extends `Closeable` and defines `toString(T)`, `fromString(String)`, and `close()`, all throwing `IOException`. It is the generic object-to-string and string-to-object conversion contract.
- `Text` extends `BinaryComparable` and implements `WritableComparable`. It stores strings as standard UTF-8 bytes and exposes constructors from `String`, `Text`, and `byte[]`; raw and copied byte access; byte length; UTF-8 scalar access via `charAt`; byte-position search via `find`; mutators `set`, `append`, and `clear`; serialization with optional max lengths; static `skip`, `readWithKnownLength`, UTF-8 `encode`/`decode`, `readString`/`writeString`, validation, code-point extraction, and `utf8Length`. `DEFAULT_MAX_LEN` is a public static final max-length constant.
- `TwoDArrayWritable` represents matrices of `Writable` instances for a declared value class. It supports construction with a value class and optional initial two-dimensional array, conversion to Java arrays, `set`, `get`, and Writable serialization.
- `VersionedWritable` is a base class for Writables with version checking. Subclasses provide `getVersion()`, and the base `write`/`readFields` contract persists/checks the version byte.
- `VersionMismatchException` carries expected/found version bytes and provides a string representation for version-read failures.
- `VIntWritable` and `VLongWritable` are `WritableComparable` wrappers for variable-length integer and long encodings. They expose default/value constructors, `set`, `get`, `readFields`, `write`, equality/hash, comparison, and string conversion.
- `Writable` defines Hadoop's simple serialization contract: `write(DataOutput)` and `readFields(DataInput)`, both throwing `IOException`. `WritableComparable<T>` combines `Writable` with `Comparable<T>`.
- `WritableComparator` is the comparator and raw-byte comparison hook for `WritableComparable` keys. It has constructors binding key classes and optional `Configuration`, static `get` and `define` registry methods, configurable support, `newKey`, object and byte-array `compare` methods, `compareBytes`, byte-array hash helpers, primitive readers (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`), and zero-compressed variable-length readers.
- `WritableFactories` holds the factory registry for classes needing non-public or custom construction. It exposes `setFactory`, `getFactory`, and `newInstance` overloads with and without `Configuration`.
- `WritableFactory` is the single-method factory interface with `newInstance()`.
- `WritableUtils` is the serialization utility class. It covers compressed byte arrays and strings, string and compressed-string arrays, display helpers, cloning into new or existing Writables, variable-length int/long read/write and size calculation, bounded int reads, enum read/write, full skipping, byte-array conversion of Writables, and safe string reads with a max length.

### Compression APIs

- `BlockCompressorStream` and `BlockDecompressorStream` are block-oriented stream adapters around `Compressor` and `Decompressor`. They add block size and compression-overhead handling, `finish`, `compress`, `decompress`, `getCompressedData`, and `resetState`.
- `BZip2Codec`, `DefaultCodec`, `GzipCodec`, and `PassthroughCodec` implement `CompressionCodec` style construction of compression streams, codec-specific compressor/decompressor types, direct decompressor support where available, configuration access, and default extensions.
- `CodecConstants` defines public extension constants for default, bzip2, gzip, lz4, passthrough, snappy, and zstandard codecs.
- `CodecPool` manages reusable `Compressor` and `Decompressor` instances. It supports leasing by codec, returning instances, and counting currently leased compressor/decompressor objects.
- `CompressionCodec` defines the codec SPI: create input/output streams with or without supplied compressor/decompressor, report compressor/decompressor classes, create instances, and return a default filename extension.
- `CompressionCodecFactory` discovers configured codec classes from `Configuration`, maps paths/names/class names to codecs, removes codec suffixes, and exposes a diagnostic `main`. It has a public SLF4J `LOG` field.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream wrappers with protected underlying `in`/`out` fields, close/flush/read/write integration, `finish`, `resetState`, seek-position stubs on input, and `getIOStatistics()`.
- `Compressor` and `Decompressor` define the low-level state machines: input/dictionary setup, input/dictionary needs, byte counters, finish/finished, compress/decompress, remaining bytes for decompression, reset, end, and compressor reinitialization with `Configuration`.
- `CompressorStream` and `DecompressorStream` are generic stream implementations with protected compressor/decompressor, buffer, eof/closed state, close/reset/skip/available/mark behavior, and protected `compress`, `decompress`, `getCompressedData`, and stream checking hooks.
- `DirectDecompressionCodec` creates `DirectDecompressor` instances, while `DirectDecompressor` exposes direct `ByteBuffer` decompression.
- `SplitCompressionInputStream` tracks adjusted split start/end offsets. `SplittableCompressionCodec` creates such streams for a requested split and declares `READ_MODE`.

### Erasure Coding, TFile, and Serialization

- `ECSchema` describes an erasure coding policy schema. Constructors accept a map or explicit codec name, data units, parity units, and extra options. Getters expose codec, extra options, data units, and parity units; equality/hash/string methods make it value-like. Public keys are `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.
- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are TFile-specific exceptions for metadata block conflicts/misses.
- `RawComparable` exposes `buffer()`, `offset()`, and `size()` for comparing raw byte slices without object conversion.
- `TFile` exposes compression and comparator constants (`COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, `COMPARATOR_MEMCMP`, `COMPARATOR_JCLASS`), supported compression algorithm lookup, comparator construction, and a `main`.
- `org.apache.hadoop.io.file.tfile.Utils` provides TFile helper encodings and searches: variable-length ints/longs, strings, and lower/upper bound binary-search helpers over comparable sequences.
- `JavaSerialization`, `JavaSerializationComparator`, and `WritableSerialization` are serializer adapter types.
- Avro integration includes the marker `AvroReflectSerializable`, `AvroReflectSerialization` with `AVRO_REFLECT_PACKAGES`, base `AvroSerialization` with `AVRO_SCHEMA_KEY`, and `AvroSpecificSerialization`.

### Logging and Metrics2 APIs

- `EventCounter` is a log4j appender-like metrics bridge with `append`, `close`, and `requiresLayout`.
- `AbstractMetric` is the immutable metric base, storing `MetricsInfo` and exposing `name`, `description`, `info`, numeric `value`, `MetricType`, visitor dispatch, equality/hash, and string conversion.
- `MetricsCollector` creates `MetricsRecordBuilder` instances with `addRecord(String)` or `addRecord(MetricsInfo)`.
- `MetricsException` is the framework runtime exception with string, cause, and string-plus-cause constructors.
- `MetricsFilter` accepts or rejects names, tags, tag collections, and records.
- `MetricsInfo` exposes immutable metric/tag metadata `name()` and `description()`.
- `MetricsJsonBuilder` and `MetricStringBuilder` are `MetricsRecordBuilder` implementations that build JSON or string dumps of metrics. They implement tag/add/context/counter/gauge methods, parent access, and `toString()`.
- `MetricsPlugin` has `init(SubsetConfiguration)`. `MetricsSink` has `putMetrics(MetricsRecord)` and `flush()`. `MetricsSource` has `getMetrics(MetricsCollector, boolean)`.
- `MetricsRecord` is an immutable metrics snapshot with timestamp, name, description, context, tags, and metrics.
- `MetricsRecordBuilder` is the fluent builder for tags, immutable metric additions, counters, gauges for int/long/float/double, context setting, parent lookup, and `endRecord`.
- `MetricsSystem` registers/unregisters sources, callbacks, publishes immediately, starts/stops metrics and MBeans, and shuts down.
- `MetricsSystemMXBean` exposes JMX lifecycle/config methods: `start`, `stop`, `startMetricsMBeans`, `stopMetricsMBeans`, and `currentConfig`.
- `MetricsTag` is an immutable tag with `MetricsInfo`, value, equality/hash, and string conversion.
- `MetricsVisitor` has callbacks for gauge and counter values across int, long, float, and double forms.
- `@Metric` and `@Metrics` are annotation types for declaring individual metrics and metrics groups.
- `GlobFilter` and `RegexFilter` compile metric filters using `com.google.re2j.Pattern`.
- `DefaultMetricsSystem` is an enum singleton API for initialization, instance lookup, shutdown, and mini-cluster mode toggles.
- `Interns` creates interned `MetricsInfo` and `MetricsTag` instances.
- `MetricsRegistry` creates and maintains mutable metrics and tags. It exposes registry info, metric/tag lookup, counter and gauge factories for int/long/float values, quantiles, stats, rates, aggregated rates, rolling averages, sample addition by name, context/tag creation with override control, snapshotting into a builder, and string conversion.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` define mutable monotonically increasing counters with increment, value, and snapshot operations. `MutableCounterInt.incr(int)` is synchronized in this snapshot; `MutableCounterLong.incr(long)` is not marked synchronized.
- `MutableGauge` is the abstract mutable gauge base with `incr` and `decr`. `MutableGaugeInt` begins at the chunk end and only its `value()` method start is included in this slice.

## Control Flow and Behavioral Contracts

The XML itself has no executable control flow, but the API contracts imply several runtime paths:

- Writable serialization flows through `write(DataOutput)` and `readFields(DataInput)`. Value classes such as `Text`, `VIntWritable`, `VLongWritable`, `SortedMapWritable`, `TwoDArrayWritable`, and versioned Writables persist their internal state into Hadoop's binary formats and reconstruct themselves from `DataInput`.
- Sorting and grouping paths can bypass object creation through `WritableComparator.compare(byte[], int, int, byte[], int, int)`, primitive byte readers, and zero-compressed integer readers. This is the hot path for file formats and shuffle/sort code using serialized keys.
- `Text` operations are byte-oriented. `find` returns byte positions, `charAt` returns Unicode scalar values without constructing a `String`, `getBytes()` exposes a backing buffer whose valid content is limited by `getLength()`, and `clear()` intentionally does not erase or free the backing byte array.
- Compression stream flow starts from `CompressionCodecFactory` resolving a codec for a path/name/class, then `CodecPool` optionally leases compressor/decompressor instances, then codec `createInputStream`/`createOutputStream` wraps the raw stream. Finish/reset/close methods coordinate codec state with underlying streams and returned pooled objects.
- Low-level `Compressor` and `Decompressor` implementations use an explicit state machine: receive input, report whether more input or a dictionary is needed, transform bytes, expose consumed/produced counts, finish or reset, and release native resources through `end`.
- Splittable compression flow uses `SplittableCompressionCodec.createInputStream` to adjust requested split boundaries into codec-valid `getAdjustedStart()`/`getAdjustedEnd()` offsets.
- TFile helpers define compact integer/string encodings and binary-search helpers used by indexed block formats.
- Metrics flow starts with `MetricsSource.getMetrics`, which emits records through a `MetricsCollector`; each record is populated by a `MetricsRecordBuilder`; sinks consume immutable `MetricsRecord` snapshots. Mutable metrics are registered in a `MetricsRegistry`, sampled with `snapshot(builder, all)`, and published through the metrics system.
- Metrics lifecycle flows through `DefaultMetricsSystem.initialize(prefix)`, source registration on `MetricsSystem`, periodic or immediate `publishMetricsNow`, sink `putMetrics`, sink `flush`, and shutdown/start/stop paths including optional JMX MBeans.

## State and Persistence Behavior

This JDiff file persists API metadata for compatibility checks. It does not persist runtime state directly.

Writable-based APIs in this chunk define durable binary state. `Text` persists a variable-length encoded byte count followed by UTF-8 bytes; `VIntWritable` and `VLongWritable` persist zero-compressed integers; `SortedMapWritable` and `TwoDArrayWritable` persist collections of nested Writables and their class identity through inherited map/array mechanisms; `VersionedWritable` persists and checks a version byte before subclass state. Golden-byte compatibility matters because Hadoop data files and RPC payloads can outlive the producing process.

`WritableFactories` and `WritableComparator` maintain process-local registries for factories and optimized comparators. These registries affect how deserialization and sort comparison instantiate or compare classes inside a JVM but are not durable.

Compression classes carry stream-local state: buffers, compressor/decompressor objects, eof/closed flags, split boundaries, and underlying input/output streams. `CodecPool` adds process-level state by tracking leased and returned compressors/decompressors. Incorrect return/reset/end behavior can leak native resources or corrupt later users of a pooled codec instance.

`ECSchema`, `MetricsTag`, and many metrics metadata objects are value-like immutable descriptors. `Interns` adds process-local interning for metrics info and tags, trading allocation reduction for cache retention.

Metrics runtime state is mostly in-memory. `MetricsRegistry` owns mutable metric objects and tags; counters are monotonically increasing, gauges can increase/decrease/set in later chunks, quantiles/stats/rates accumulate samples, and `snapshot` transfers current values into a record builder. `DefaultMetricsSystem` and `MetricsSystem` manage singleton/global lifecycle state, registered sources/sinks, callbacks, and MBean publication state.

Serializer and Avro classes describe adapter entry points. Persistence semantics are delegated to Java serialization, Hadoop Writable serialization, or Avro schemas configured through keys such as `AVRO_SCHEMA_KEY` and `AVRO_REFLECT_PACKAGES`.

## Dependencies and Integration Points

This chunk depends on JDiff/Javadoc generation semantics and the JDiff XML schema. The represented APIs integrate with:

- Java IO (`InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `Closeable`, `IOException`), NIO (`ByteBuffer`, charset exceptions), collections, comparators, patterns, and primitive wrappers.
- Hadoop `Configuration` and `Configurable` for comparator, factory, codec, compressor, serializer, and metrics plugin setup.
- Hadoop `Writable`, `WritableComparable`, `BinaryComparable`, `AbstractMapWritable`, `MetricsInfo`, `MetricsRecordBuilder`, `MetricsCollector`, `MetricsRecord`, and mutable metrics classes across package boundaries in this same API snapshot.
- Hadoop filesystem statistics through `CompressionInputStream.getIOStatistics()` and `CompressionOutputStream.getIOStatistics()`.
- Compression native libraries and codec implementations behind `Compressor`, `Decompressor`, `DirectDecompressor`, gzip, bzip2, zlib/default, passthrough, and splittable codec implementations.
- TFile data structures and block/index lookup code through raw comparable byte slices, compression constants, comparator factories, and compact encodings.
- Avro serialization through reflect/specific serialization classes and schema configuration keys.
- Metrics integrations through Apache Commons Configuration `SubsetConfiguration`, SLF4J loggers, log4j-style `EventCounter`, RE2/J regex patterns, JMX MXBeans, metrics source/sink/plugin contracts, and singleton `DefaultMetricsSystem` access.

## Risks and Compatibility Notes

- The chunk starts in the middle of `ShortWritable` and ends in the middle of `MutableGaugeInt`; whole-file reconciliation must merge adjacent chunks before claiming complete coverage of those types.
- JDiff exposes signature and documentation compatibility, not implementation details. Exact serialization byte layouts, pool locking behavior, native-code error paths, codec header formats, and metrics scheduling require implementation-source or tests to verify.
- `Text.getBytes()` exposes the backing array and is only valid up to `getLength()`. Callers that use the full array can read stale data; `clear()` also leaves the old backing bytes allocated and visible via `getBytes()`.
- `Text` method positions are byte offsets, not Java UTF-16 character indexes. Misinterpreting `find`, `charAt`, or `validateUTF8` offsets can corrupt multibyte UTF-8 handling.
- Max-length overloads on `Text.readFields`, `Text.write`, `readString`, `writeString`, and `WritableUtils.readStringSafely` are important input-boundary defenses. Callers that use unbounded reads on untrusted inputs risk excessive allocation.
- `WritableComparator` raw-byte comparison must remain consistent with object `compareTo`. Divergence causes incorrect sorted order, grouping, partitioning, or binary-search behavior.
- Factory and comparator registries are process-global. Tests or applications that register custom factories/comparators can affect unrelated code in the same JVM.
- Codec pooling requires disciplined ownership. Returning a compressor/decompressor while still in use, failing to return it, or failing to reset state can cause data corruption, leaks, or cross-stream contamination.
- `CompressionInputStream.seek` and `seekToNewSource` are present on the abstract stream, but many compressed streams are not meaningfully seekable. Callers should rely on codec/splittable capabilities rather than assuming random access.
- Direct decompression uses `ByteBuffer` and codec-specific native paths. Implementations must define buffer position/limit behavior carefully and handle unsupported direct decompression.
- `PassthroughCodec` deliberately reports a codec extension while performing no compression. Code that assumes every codec changes bytes or compression ratio may mis-handle it.
- TFile constants include `COMPRESSION_LZO`, but actual support depends on configured/native codec availability.
- Metrics filters use RE2/J patterns rather than `java.util.regex.Pattern`, which affects syntax/performance compatibility.
- `MetricsRegistry.newQuantiles` documents `MetricsException` for non-positive intervals. Registry callers should validate interval configuration before runtime registration.
- Mutable metric synchronization differs by class/method in the metadata. Concurrency assumptions should be checked against implementation, especially for high-frequency counters and registry mutation/snapshot paths.
- `DefaultMetricsSystem` is a singleton/global access point. Mini-cluster mode and shutdown can affect all metrics users in the JVM.

## Test Signals

Useful validation for the APIs represented by this chunk includes:

- XML well-formedness and JDiff compatibility checks that all class/interface start/end markers inside the slice match except the documented partial `ShortWritable` and `MutableGaugeInt` boundaries.
- Writable round-trip tests for `SortedMapWritable`, `Text`, `TwoDArrayWritable`, `VersionedWritable` subclasses, `VIntWritable`, and `VLongWritable`, including empty values, nested Writables, negative numbers, boundary variable-length encodings, and version mismatch failures.
- `Text` tests for UTF-8 multibyte characters, invalid UTF-8 validation, byte-position `find`, scalar `charAt`, append/set/copy semantics, max-length read/write enforcement, backing-array behavior of `getBytes`, and `clear()` retaining capacity.
- Comparator tests asserting `WritableComparator` raw-byte compare agrees with object `compareTo`; primitive byte readers decode known big-endian/zero-compressed sequences; custom comparator registration affects lookup; and `newKey()` uses the expected factory/configuration.
- `WritableFactories` tests for custom factory registration, `Configuration` propagation, default constructor fallback, and non-public Writable instantiation.
- `WritableUtils` golden-byte tests for compressed byte arrays/strings, string arrays, enum read/write, `skipFully`, `toByteArray`, clone/cloneInto behavior, and safe string length rejection.
- Compression tests for each codec's default extension, stream round trips, finish/flush/close ordering, reset-state reuse, dictionary-required paths where applicable, direct decompressor behavior, split-boundary adjustment, IOStatistics delegation, and malformed/truncated input handling.
- `CodecPool` tests for lease/return counts, reuse after return, reset before reuse, double return behavior, concurrent leasing, and native resource release through compressor/decompressor `end`.
- `CompressionCodecFactory` tests for configured codec classes, lookup by path/class/name, suffix removal, duplicate extensions, and absent codec handling.
- `ECSchema` tests for map and explicit constructors, required keys, extra option preservation, equality/hash stability, and string rendering.
- TFile tests for supported compression listing, comparator construction, raw comparable offsets/sizes, variable-length helper encodings, string helper encodings, and lower/upper-bound search edge cases.
- Serializer tests for Java, Writable, Avro reflect, and Avro specific adapters, including configured schemas/packages and comparator behavior for serialized Java objects.
- Metrics tests for collector/builder chaining, immutable record/tag/metric equality, JSON/string builder output shape, visitor dispatch by metric type, filter accept/reject behavior for names/tags/records, plugin initialization with subset configuration, source-to-sink publication, sink flushing, and metrics system start/stop/shutdown/JMX lifecycle.
- `MetricsRegistry` tests for duplicate metric/tag names, tag override behavior, counter/gauge creation and lookup, stat/rate/quantile registration, invalid quantile intervals, `add(name, value)` routing, snapshot with `all` true/false, and concurrent mutation while snapshotting.
- Mutable counter tests for increment-by-one, delta increments, monotonicity, value reporting, snapshot output, integer overflow behavior if defined by implementation, and thread behavior matching the synchronization contract.

## Cross-Chunk Notes

The previous chunk is needed to complete `org.apache.hadoop.io.ShortWritable`; this chunk only includes the tail of its `toString()` method and class doc before the class ends at line 24787.

The next chunk is needed to complete `org.apache.hadoop.metrics2.lib.MutableGaugeInt`; this slice stops immediately after the `value()` method declaration begins at line 31074. Later methods such as integer gauge increments, decrements, setters, and snapshot behavior are outside this mapped range.

### subset-b-007223: lines 31075-37145

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml lines 31075-37145

## Research scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.3.5, not Java implementation source. The range starts in the tail of `org.apache.hadoop.metrics2.lib.MutableGaugeInt`, then covers metrics mutable types and sinks, MBean and metrics-cache helpers, network topology and socket factories, security credentials, user/group identity, Kerberos helpers, authorization and impersonation contracts, HTTP security filters, token and delegation-token APIs, and the service lifecycle framework through the opening of `ServiceStateModel`. Research conclusions below are based on public signatures, inheritance, fields, declared exceptions, synchronization flags, and embedded Javadocs in the XML slice.

## Purpose

The chunk documents several Hadoop Common support layers that many distributed filesystem components depend on:

- Metrics APIs for recording mutable counters, gauges, rates, rolling averages, quantiles, and exporting those records to files, HDFS-like filesystems, Graphite, StatsD, JMX, and in-memory caches.
- Network resolution APIs for mapping host names to rack or switch locations, caching those mappings, loading static/scripted mappings, and constructing standard or SOCKS-backed sockets.
- Security APIs for token/secret persistence, Kerberos login and relogin, user identity, group/id mapping, ACL checks, proxy-user authorization, credential-provider lookup, delegation-token HTTP operations, and servlet filters for REST CSRF and frame protection.
- Service lifecycle APIs that standardize initialization, startup, shutdown, failure capture, listener notification, composition, and state transition validation for Hadoop daemons and subservices.

## Important APIs and types

The metrics section begins with mutable metric primitives. `MutableGaugeLong` mirrors the preceding `MutableGaugeInt` tail with `value`, no-arg and delta `incr`/`decr`, `set`, `snapshot(MetricsRecordBuilder, boolean)`, and `toString`. `MutableMetric` is the abstract base with `snapshot(builder, all)`, convenience `snapshot(builder)`, protected `setChanged`/`clearChanged`, and public `changed`, establishing the change-flag contract used by mutable metrics.

`MutableQuantiles` tracks a stream of long samples with online quantile estimates. It has interval-based construction, synchronized `snapshot`, `add`, `getEstimator`, and `setEstimator`, public static `quantiles`, protected `previousSnapshot`, `getInterval`, and `stop`. `MutableStat` records sample statistics through constructors with sample/value names and optional extended statistics, `setExtended`, `setUpdateTimeStamp`, count/value `add` overloads, `snapshot`, `lastStat`, `resetMinMax`, `getSnapshotTimeStamp`, and `toString`. `MutableRate` is a convenience `MutableStat`. `MutableRates` groups named rates but warns that it synchronizes access and is unsuitable under high contention. `MutableRatesWithAggregation` provides protocol/name initialization, prefixed initialization, per-thread sample addition, and synchronized snapshot aggregation for higher concurrency, with a documented caveat that samples in short-lived threads can be lost before snapshot. `MutableRollingAverages` is `Closeable`, stores rolling windows, supports thread-local collection, per-name `add`, `snapshot`, synchronized `getStats(minSamples)`, test-only `setRecordValidityMs`, and `close`.

The metrics sink section defines `FileSink`, `GraphiteSink`, `RollingFileSystemSink`, and `StatsDSink`, all implementing `MetricsSink` and most also `Closeable`. They expose `init(SubsetConfiguration)`, `putMetrics(MetricsRecord)`, `flush`, and `close`; `StatsDSink` additionally exposes `writeMetric`. `RollingFileSystemSink` has constructors for normal and supplied timing intervals, fields such as `source`, `ignoreError`, `allowAppend`, `basePath`, roll/offset intervals, `nextFlush`, `forceFlush`, `hasFlushed`, `suppliedConf`, and `suppliedFilesystem`, plus `getRollInterval`, `updateFlushTime`, and `setInitialFlushTime`.

`MBeans` is the JMX bridge with registration overloads returning `ObjectName`, service/name extraction helpers, and `unregister`. `MetricsCache` stores recent `MetricsRecord` values with bounded constructors, `update` overloads, and `get`. `Servers.parse` parses server specifications into address lists.

The network section centers on `DNSToSwitchMapping`, whose contract maps host names to network locations and supports full or selective cache reload. `AbstractDNSToSwitchMapping` adds `Configurable`, configuration access, `isSingleSwitch`, `getSwitchMap`, `dumpTopology`, and static helpers for single-switch policy checks. `CachedDNSToSwitchMapping` wraps a raw mapping, caches `resolve` results, exposes `rawMapping`, `getSwitchMap`, `isSingleSwitch`, `toString`, and reload methods. `ScriptBasedMapping` is a cached mapping driven by configured scripts, includes `NO_SCRIPT`, and exposes constructors for default, raw mapping, or `Configuration`. `TableMapping` is another cached mapping driven by a static table and overrides configuration and reload behavior.

`SocksSocketFactory` and `StandardSocketFactory` extend `javax.net.SocketFactory` with five `createSocket` overloads. `SocksSocketFactory` is `Configurable`, supports construction with a `Proxy`, and implements equality/hash based on proxy/config state; `StandardSocketFactory` provides standard socket construction and equality/hash behavior. `ConnectTimeoutException` is a `SocketTimeoutException` specialization.

The security credentials section starts with `AccessControlException` as an `IOException` base for access failures. `Credentials` is a `Writable` container for tokens and secret keys. It supports copying, token add/get/list/map/count, secret-key add/get/remove/list/map/count, token-storage file and stream read/write using `FileSystem` and `Configuration`, normal `write`/`readFields`, `addAll`, and `mergeAll`.

`GroupMappingServiceProvider` resolves user groups and supports cache refresh/addition; `IdMappingServiceProvider` maps names to uid/gid and back, including allowing unknown ids. `KerberosAuthException` captures contextual Kerberos failure details with setters/getters for user, principal, keytab, ticket cache, initial message, and custom `getMessage`.

`SecurityUtil` is a static security helper surface. It configures security behavior, derives server principals from host names or addresses, performs keytab logins, builds delegation-token service names and token services, extracts hosts from principals, locates `KerberosInfo` and `TokenInfo` annotations, gets token service addresses, runs actions as login or current users, maps authentication methods, checks privileged ports, fetches ZooKeeper auth info, and exposes constants/logging fields including `HOSTNAME_PATTERN` and `FAILED_TO_GET_UGI_MSG_HEADER`.

`UserGroupInformation` is the central user identity and subject wrapper. This chunk exposes static initialization/configuration, security-enabled checks, current/login/best user discovery, ticket-cache and subject-based UGI creation, keytab login/logout/relogin/forced relogin, ticket-cache relogin, remote and proxy-user construction, testing UGIs, real-user access, short/full names, token identifier and token management, credential merging, group lookup, subject access, authentication-method management, equality/hash, generic `doAs` overloads, diagnostic logging, and a `main`. It also exposes environment constants `HADOOP_TOKEN_FILE_LOCATION` and `HADOOP_TOKEN`. The nested `UserGroupInformation.AuthenticationMethod` enum maps values to SASL RPC auth methods and supports value lookup.

`CredentialProvider` is an abstract, thread-safe credential-store interface with transient-store detection, persistent `flush`, alias lookup/listing, creation and deletion of credential entries, password-needed checks, warning/error text, and `CLEAR_TEXT_FALLBACK`. `CredentialProviderFactory` is a service-loader based provider factory keyed by `CREDENTIAL_PROVIDER_PATH`.

The authorization section includes `AccessControlList`, a `Writable` ACL parser and serializer with wildcard and real-ACL constants, user/group add/remove/list operations, `isAllAllowed`, `isUserInList`, `isUserAllowed`, string conversion, and exact ACL string output. `AuthorizationException` extends `AccessControlException` and deliberately suppresses stack traces for security. `DefaultImpersonationProvider` implements `ImpersonationProvider`, provides a test singleton, configuration/init, proxy-user authorization, configuration key builders for users/groups/IPs, and access to proxy group/host maps. `ImpersonationProvider` is `Configurable`, initializes from a configuration prefix, and authorizes superuser `doAs` requests by user and optional remote address.

`RestCsrfPreventionFilter` and `XFrameOptionsFilter` are servlet filters. The CSRF filter classifies browser user agents, applies configurable custom header and ignored-method policy, exposes filter-param extraction, and rejects unsafe browser REST requests lacking the header. The X-Frame filter adds frame-protection response headers and exposes similar filter-param extraction.

The token section defines `SecretManager<T extends TokenIdentifier>` with password creation/retrieval, retriable retrieval, identifier creation, read-availability checks, and static helpers for generating/creating secret keys and passwords. `Token<T>` is a `Writable` for identifier/password/kind/service data with constructors from identifiers, raw byte arrays, default, and copy; mutation/accessors; `copyToken`; `decodeIdentifier`; private-token clone checks; serialization; URL-safe encode/decode; equality/hash; `toString`; cache-key generation; and renew/cancel/isManaged integration with `TokenRenewer`. `Token.TrivialRenewer` handles unmanaged tokens. `TokenIdentifier` is a `Writable` base with kind, user, serialized bytes, and tracking id. `TokenInfo` is an annotation type. `TokenRenewer` is the abstract renewal/cancel SPI. `TokenSelector` selects a token by kind/service from a collection.

The delegation-token HTTP section includes `DelegationTokenAuthenticatedURL`, its nested token type, `DelegationTokenAuthenticator`, and Kerberos/pseudo subclasses. `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL`, manages a default authenticator class, controls whether delegation tokens travel in query strings, opens configured `HttpURLConnection` instances, and obtains/renews/cancels delegation tokens with optional renewer or doAs user. Its nested `Token` holds both the authentication token and Hadoop delegation token. `DelegationTokenAuthenticator` wraps an `Authenticator`, supports connection configuration, authenticates, performs token get/renew/cancel operations, and exposes protocol parameter/JSON constants such as `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `TOKEN_PARAM`, `RENEWER_PARAM`, `SERVICE_PARAM`, and response field names.

The service lifecycle section defines `AbstractService`, `CompositeService`, `LifecycleEvent`, `LoggingStateChangeListener`, `Service`, `ServiceOperations`, `ServiceStateChangeListener`, `ServiceStateException`, and the start of `ServiceStateModel`. `Service` is a `Closeable` lifecycle interface with `init`, `start`, `stop`, `close`, listener registration, name/config/state/start-time accessors, state checks, failure cause/state accessors, `waitForServiceToStop`, lifecycle history snapshots, and blockers. `AbstractService` implements this contract with overridable `serviceInit`, `serviceStart`, `serviceStop`, listener management including global listeners, `noteFailure`, blockers, and lifecycle history. `CompositeService` manages child services with add/remove, add-if-service, child listing, and lifecycle propagation; `STOP_ONLY_STARTED_SERVICES` controls stop behavior. `LifecycleEvent` is serializable with public `time` and `state`. `LoggingStateChangeListener` logs service state transitions. `ServiceOperations` provides static stop and quiet-stop helpers for SLF4J and Commons Logging. `ServiceStateException` is an exit-code-bearing runtime exception with conversion helpers. `ServiceStateModel` validates and enters service states, with synchronized `enterState`.

## Control flow and behavior

Metrics control flow is producer/snapshot oriented. Mutable metrics accept local updates via `add`, `incr`, `decr`, or `set`, mark themselves changed through the `MutableMetric` change flag, and later emit values to a `MetricsRecordBuilder` on `snapshot`. `all=true` forces unchanged metrics to be emitted. Quantile and rolling-average metrics add timer/window behavior: samples accumulate in estimators or thread-local/window structures, then snapshots publish previous or aggregated state while rollover/record-validity rules evict stale samples. Rate groups either synchronize all updates in one registry (`MutableRates`) or let threads maintain local rate counts and aggregate them during snapshot (`MutableRatesWithAggregation`).

Sink control flow receives records from the metrics system after snapshot. File-like sinks initialize output destinations from subset configuration, write each `MetricsRecord`, flush buffered data, and close resources. `RollingFileSystemSink` adds periodic roll decisions based on roll intervals, offset intervals, initial flush time, and next-flush state; error handling is influenced by `ignoreError` and append support by `allowAppend`. Graphite and StatsD sinks translate Hadoop metric names and values into external monitoring protocols.

Network mapping control flow resolves host lists to rack paths. Cached mappings first satisfy known hosts from cache, ask the raw mapping for misses, then update cache state. Reload methods either clear all cached mappings or selectively remove specified hosts. Script/table mappings plug different raw-resolution sources under the same `DNSToSwitchMapping` contract. Socket factories abstract actual `Socket` construction so downstream RPC/client code can use standard sockets or a configured SOCKS proxy without changing call sites.

Security control flow starts with static configuration of authentication mode and then flows through UGI. Callers obtain the current/login/best user, optionally log in from keytab or ticket cache, execute privileged actions via `doAs`, attach credentials and tokens, and refresh Kerberos state through relogin helpers before credentials expire. Proxy-user authorization flows from a real user plus effective user through `ImpersonationProvider.authorize`, which checks configured users, groups, and IP hosts. Credential providers are discovered from configured provider-path URIs, mutated through provider-specific stores, then made durable by `flush`.

Token control flow separates token identity, password/secret management, token selection, and renewal. `SecretManager` creates or retrieves passwords for `TokenIdentifier` instances. `Token` serializes identifier, password, kind, and service, can decode identifiers through the relevant class, and delegates renew/cancel/isManaged behavior to registered `TokenRenewer` implementations. Delegation-token HTTP clients authenticate a connection first, then issue token management operations using query/form parameters and parse JSON responses into Hadoop `Token` values.

Servlet-filter control flow is request/response oriented. The CSRF filter examines HTTP method, user agent, and presence of a configured custom header; browser-like requests for protected methods without the header are rejected. The frame-options filter injects an `X-Frame-Options` header using init/config parameters before passing the request down the filter chain.

Service lifecycle control flow is a constrained state machine. `Service.init(Configuration)` moves from `NOTINITED` to `INITED`; `start()` moves from `INITED` to `STARTED`; `stop()` must be idempotent and should work even from partially initialized states. Failures during init/start require stopping and recording failure cause/state. `AbstractService` wraps subclass hooks with state transition, history, listener notification, and termination waiting. `CompositeService` applies the same lifecycle transitions to children, while `ServiceOperations.stopQuietly` provides cleanup-time best-effort stopping that catches exceptions but not arbitrary throwables.

## State and persistence behavior

Metrics state is in-memory until exported by sinks. Mutable metrics store current values, changed flags, sample statistics, quantile estimators, previous quantile snapshots, rate registries, rolling-average windows, thread-local accumulators, timestamps, and min/max state. Sink state includes open writers or sockets, filesystem paths, roll calendars, flush timing, append/error flags, supplied configuration/filesystem handles, and external monitoring endpoints. JMX registration persists only in the local JVM MBean server until unregistered.

Network state includes cached host-to-switch mappings, raw mapping configuration, script/table configuration, socket proxy configuration, and one-switch policy results. The authoritative topology usually lives outside these classes in scripts, config files, DNS, or static tables; cache reload APIs are the consistency boundary.

Security state is split across JVM subject state, serialized credentials, external Kerberos infrastructure, credential-provider stores, configuration, and token secret managers. `Credentials`, `AccessControlList`, `Token`, and `TokenIdentifier` implement `Writable` persistence for RPC, token files, and on-disk or stream storage. Credential providers may be transient or persistent; persistent providers require `flush` to commit changes. `UserGroupInformation` state includes the login user, current subject, real/effective user relationship, tokens, token identifiers, authentication method, and group memberships. Kerberos state includes keytab path, principal, ticket cache, TGT lifetime, and relogin timing.

Authorization and HTTP filter state is primarily configuration-derived: ACL users/groups, proxy-user allowed users/groups/hosts, custom CSRF headers, ignored HTTP methods, browser user-agent patterns, and frame-options header value. `AuthorizationException` intentionally hides stack traces to avoid leaking security-sensitive details.

Service state is explicit and queryable. Services maintain `STATE`, configuration, start time, failure cause/state, lifecycle event history, blockers, listeners, and a termination notification object used by `waitForServiceToStop`. `CompositeService` also maintains child service lists. `LifecycleEvent` instances can be serialized and contain transition time and state.

## Dependencies and integration points

The metrics APIs integrate with `org.apache.hadoop.metrics2` core types (`MetricsSink`, `MetricsRecord`, `MetricsRecordBuilder`, `MetricsInfo` indirectly), `org.apache.commons.configuration2.SubsetConfiguration`, Hadoop `Configuration`, Hadoop `FileSystem`/`Path` for rolling filesystem output, JMX `ObjectName`, and external Graphite/StatsD services. Quantiles depend on `org.apache.hadoop.metrics2.util.Quantile`, `QuantileEstimator`, and `SampleStat`.

Network APIs integrate with Hadoop `Configuration`/`Configurable`, Java networking (`Socket`, `InetAddress`, `InetSocketAddress`, `Proxy`, `SocketFactory`, `SocketTimeoutException`), DNS, topology scripts, and static mapping files. These mappings feed placement-aware components such as HDFS block placement and rack-aware schedulers.

Security APIs integrate with Hadoop `Writable`, `Text`, `FileSystem`, `Path`, `Configuration`, SASL RPC auth methods, JAAS `Subject`, Kerberos principals/keytabs/ticket caches, `PrivilegedAction` and `PrivilegedExceptionAction`, group and id mapping providers, servlet APIs, credential-provider service loading, ZooKeeper auth config, and Hadoop authentication client classes such as `AuthenticatedURL`, `Authenticator`, and `ConnectionConfigurator`.

Token APIs integrate with `SecretKey`, token renewer plugins, token selectors, URL-safe encodings, JSON delegation-token responses, HTTP connections, and service-specific token identifiers. `SecurityUtil.getKerberosInfo` and `getTokenInfo` expose annotation-driven integration for protocol classes.

Service lifecycle APIs integrate with `Configuration`, SLF4J and Commons Logging, Hadoop launcher exit codes via `ExitCodeProvider`, and any daemon/subsystem implemented as a `Service`. Listener callbacks are synchronous with state changes, making them part of the lifecycle critical path.

## Risks and edge cases

- `MutableRates` synchronizes all access to contained metrics, so high-contention instrumentation can become a bottleneck; `MutableRatesWithAggregation` reduces contention but can lose samples produced by short-lived threads before snapshot.
- `MutableQuantiles` and rolling-average metrics rely on timed rollovers and previous snapshots; tests and dashboards must tolerate interval boundaries, empty snapshots, and stale-window eviction.
- `RollingFileSystemSink` combines filesystem append support, rolling intervals, flush scheduling, and ignore-error behavior. Misconfiguration can silently drop metrics when `ignoreError` is enabled or fail on filesystems that do not support append.
- Graphite and StatsD sinks translate Hadoop metric names into external wire formats; name escaping, counter/gauge type selection, network failure, and flush/close behavior are common integration risks.
- Cached DNS-to-switch mappings can become stale after topology changes unless reload APIs are called. Script/table mappings also need clear behavior for failed scripts, missing scripts, unknown hosts, and single-switch fallback.
- `SocksSocketFactory.equals`/`hashCode` behavior matters because socket factories may be cached; proxy or configuration changes can otherwise produce surprising reuse.
- `Credentials.mergeAll` and `addAll` have different overwrite semantics in implementation; callers must test duplicate token aliases and duplicate secret keys rather than assuming merge behavior.
- Kerberos login/relogin APIs have time-sensitive behavior. Keytab relogin, ticket-cache relogin, forced relogin, and test-only immediate-renew settings can race with long-running RPC clients if not covered.
- `UserGroupInformation` stores both real and effective users. Authorization and audit paths must use the correct real/effective identity, especially for proxy users and token-authenticated RPCs.
- `AuthorizationException` suppresses stack traces intentionally; diagnostics must not rely on stack traces for these failures.
- `AccessControlList` wildcard handling can bypass user/group checks by design. The optional `USE_REAL_ACLS` flag indicates alternate ACL semantics that need explicit tests.
- CSRF protection depends on correct browser detection, protected method lists, and custom header configuration. Non-browser clients and ignored methods can bypass the header requirement by design.
- `Token.privateClone` and `isPrivateCloneOf` introduce private service scoping. Renew/cancel code must avoid accidentally operating on the wrong service-specific clone.
- Delegation-token HTTP operation parameters can be sent through query strings when configured; this is compatible with some servers but increases token exposure in logs and intermediaries.
- Service state listener callbacks run on the thread initiating the state change while the service is in a synchronized section. Long-running callbacks can delay lifecycle transitions, and callbacks that re-enter service methods from other threads risk deadlock.
- `ServiceOperations.stop` checks state before stopping and is documented as not thread-safe. Concurrent lifecycle transitions need stronger synchronization at the caller or service implementation level.
- `Service.stop` must be robust even when fields are partially initialized. Subclasses that assume successful `serviceInit` before `serviceStop` can fail cleanup paths after startup errors.

## Test signals

Useful test coverage for code using or changing APIs in this chunk should include:

- Mutable metric tests for change-flag behavior, `snapshot(all=false)` suppression, `snapshot(all=true)` emission, gauge increment/decrement/set, stat count/value aggregation, min/max reset, extended statistics toggling, and timestamp updates.
- Quantile and rolling-average tests for rollover intervals, synchronized add/snapshot behavior, estimator replacement, previous-snapshot content, stop/close behavior, thread-local state collection, `minSamples` filtering, stale record validity, and empty stream behavior.
- Rate tests comparing `MutableRates` and `MutableRatesWithAggregation` under concurrent updates, protocol/name initialization, prefix handling, and sample loss from short-lived threads.
- Sink tests for init parameters, output format, flush/close idempotence, filesystem roll timing, append support, `ignoreError`, Graphite/StatsD network failure, and metric name/value escaping.
- MBean and metrics-cache tests for duplicate registration, unregister idempotence, ObjectName service/name parsing, cache update replacement, bounded eviction, and tag/metric lookup.
- Network topology tests for cache hit/miss behavior, full and selective reload, unknown-host handling, script absence (`NO_SCRIPT`), script failure, table reload, single-switch policy detection, topology dumps, and socket factory equality/hash across proxy/config changes.
- Credentials tests for token and secret-key add/get/remove/list/count, token-storage file and stream round trips, `Writable` compatibility, duplicate aliases, `addAll` versus `mergeAll`, and read/write behavior through a real `FileSystem`.
- Kerberos and UGI tests using controlled/minicluster fixtures for keytab login, logout, ticket-cache login, relogin throttling, forced relogin, current/login user discovery, `doAs` checked and unchecked exception propagation, token attachment, credentials merge, group lookup, proxy-user real/effective identity, and authentication-method mapping.
- Credential provider tests for service-loader discovery from `CREDENTIAL_PROVIDER_PATH`, transient versus persistent providers, missing passwords, warning/error strings, alias creation/deletion/listing, duplicate alias failures, thread safety, and `flush` durability.
- ACL and impersonation tests for wildcard ACLs, user and group mutations, serialization round trip, proxy superuser user/group/IP configuration keys, authorization success/failure, remote-address overloads, suppressed stack traces, and real-ACL mode if enabled.
- Servlet filter tests for browser/non-browser user agents, custom header names, ignored method configuration, rejection status for missing headers, pass-through with valid headers, frame-options header injection, and filter-param extraction by prefix.
- Token tests for password generation/retrieval, retriable retrieval, identifier serialization/deserialization, URL encode/decode, private clone service isolation, renew/cancel with matching and nonmatching renewers, selector behavior, cache-key generation, equality/hash, and unmanaged `TrivialRenewer` behavior.
- Delegation-token HTTP tests for authenticator wrapping, connection configurator use, default authenticator class changes, query-string versus header/body token transmission, get/renew/cancel operations, doAs handling, service parameter handling, JSON parsing, and HTTP failure mapping.
- Service lifecycle tests for valid and invalid transitions, init/start failure forcing stop, idempotent stop/close, failure cause/state capture, listener registration/unregistration/global listeners, listener deadlock avoidance, lifecycle history snapshots, `waitForServiceToStop` timeout and success paths, blockers, `ServiceOperations.stopQuietly` logging/return values, composite child ordering, and `STOP_ONLY_STARTED_SERVICES` behavior.

### subset-b-007224: lines 37146-40640

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml lines 37146-40640

## Research scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.3.5, not Java implementation source. The range starts at the tail of `org.apache.hadoop.service.ServiceStateModel`, covers the public `org.apache.hadoop.service.launcher` package, a broad slice of `org.apache.hadoop.util`, all visible `org.apache.hadoop.util.bloom` entries in this range, and the beginning of `org.apache.hadoop.util.functional`. Conclusions are based on package/class/interface declarations, inheritance, visibility, declared exceptions, fields, method signatures, and embedded Javadocs.

## Purpose

The chunk documents support APIs that sit under Hadoop command-line tools, service launchers, platform integration, diagnostics, serialization-friendly probabilistic data structures, and async/listing utilities. The service launcher layer gives long-running Hadoop services a standard lifecycle and process-exit contract. The utility layer provides classloader isolation, command execution, shutdown hook ordering, reflection-based instantiation, duration logging, checksums, system-resource reporting, CLI `Tool` dispatch, and build-version reporting. The Bloom filter package exposes serializable set-membership filters. The functional package begins a newer set of helpers for executor lifecycle management, future exception unwrapping, filesystem builder option propagation, and `RemoteIterator` composition.

## Important APIs and types

The chunk begins with `ServiceStateModel.checkStateTransition(String, Service.STATE, Service.STATE)`, `isValidStateTransition(Service.STATE, Service.STATE)`, and `toString()`. These APIs guard and describe Hadoop `Service` lifecycle transitions. `isValidStateTransition` explicitly treats `current == proposed` as a non-transition rather than a valid transition check.

`org.apache.hadoop.service.launcher.AbstractLaunchableService` extends `AbstractService` and implements `LaunchableService`. Its protected name constructor delegates service naming to the superclass. The base `bindArgs(Configuration, List)` logs command-line arguments at debug level and returns the original `Configuration`; the base `execute()` returns success code `0`.

`HadoopUncaughtExceptionHandler` implements `Thread.UncaughtExceptionHandler`. It can wrap a delegate handler for "simple" exceptions or run standalone. Its contract is conservative for JVM `Error`: log and exit instead of attempting a clean shutdown when process state may be corrupt. It is intended to be installed as the default uncaught exception handler in main entry points.

`LaunchableService` extends `Service` and adds `bindArgs(Configuration, List)` plus `execute()`. The launcher invokes `bindArgs` before `Service.init(Configuration)`, allowing a service to replace or mutate the configuration before initialization. After `Service.start()`, the launcher calls `execute()`, and that return value becomes the process exit code. Its exception policy distinguishes `ExitUtil.ExitException`, `ExitCodeProvider`, and generic exceptions, mapping the latter two into `ServiceLaunchException` where needed.

`LauncherExitCodes` centralizes process exit constants. The documented groups are Unix success `0`, generic command issues, HTTP-like client/config errors in the 40s, service-side failures in the 50s, and application-specific codes at 60+. Named constants include success/fail, client shutdown, task launch failure, interrupted, command argument error, unauthorized, usage, forbidden, not found, operation not allowed, not acceptable, connectivity problem, bad configuration, exception thrown, unimplemented, service unavailable, unsupported version, service creation failure, and service lifecycle exception.

`ServiceLaunchException` extends `ExitUtil.ExitException` and implements both `ExitCodeProvider` and `LauncherExitCodes`. Constructors accept an exit code plus a cause, message, formatted message, or cause with formatted message. The formatted constructors use English-locale `String.format`, and one constructor treats a trailing throwable in the argument list as the cause.

`ApplicationClassLoader` extends `URLClassLoader` for application isolation. It can be constructed from URL arrays or a classpath string, overrides resource lookup and class loading, and exposes `isSystemClass(String, List)` to decide whether a name should be loaded from the parent/system side. `SYSTEM_CLASSES_DEFAULT` keeps JDK, Hadoop, resource, and selected third-party classes out of the application-first loader path.

`DurationInfo` extends `OperationDuration` and implements `AutoCloseable`. It logs a formatted operation description at info or debug level and logs final duration in `close()`, making it suitable for try-with-resources timing blocks. `OperationDuration` records start and finish clock times, exposes `finished()`, `value()` in milliseconds, `asDuration()`, and static `humanTime(long)` formatting.

`IPList` is a small membership interface with `isIn(String ipAddress)`. `Progressable` exposes `progress()` for long-running Hadoop operations to report liveness to a framework that may otherwise time out work.

`PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum`. Each has `getValue()`, `reset()`, `update(byte[], int, int)`, and final single-byte `update(int)`. `PureJavaCrc32` targets the same polynomial as the native `CRC32` while avoiding JNI overhead for small repeated updates. `PureJavaCrc32C` targets the CRC32-C polynomial used by iSCSI and hardware-accelerated on many Intel chipsets.

`ReflectionUtils` provides Hadoop-aware reflection helpers: `setConf(Object, Configuration)` for `Configurable` instances, `newInstance(Class, Configuration)` for configured construction, contention tracing toggles, synchronized thread dump printing, commons-logging and SLF4J thread-stack logging with minimum intervals, typed `getClass(T)`, serialization-based `copy(Configuration, T, T)`, `cloneWritableInto(Writable, Writable)`, and utilities that gather declared fields or methods across superclasses.

`Shell` is an abstract base for platform-aware command execution. It has protected constructors for no throttling, minimum run interval, and optional stderr redirection. Static helpers build OS-specific command arrays for group lookup, group-id lookup, netgroups, permissions, ownership, symlinks, readlink, process liveness, signal/kill, scripts, Hadoop-home qualified binaries, Winutils lookup, bash support, and one-shot `execCommand` calls. Instance methods configure environment and working directory, run commands subject to the interval, expose process/exit/waiting-thread/timeout state, and require subclasses to implement `getExecString()` and `parseExecResult(BufferedReader)`. Public fields document OS booleans, command constants, regexes, timeout and environment behavior, `WINUTILS`, setsid support, and the token separator regex. `isJava7OrAbove()` remains public but is deprecated because Hadoop now assumes Java 7 or later.

`ShutdownHookManager` is a singleton manager for deterministic shutdown hook ordering. It registers one JVM hook and runs registered `Runnable` hooks by priority, with higher priorities first and same-priority hooks unordered. Hooks can be added with just priority or with priority plus timeout/time unit, removed, tested, queried for shutdown-in-progress, or cleared. `TIMEOUT_MINIMUM` and `TIME_UNIT_DEFAULT` document timeout defaults, and the class Javadoc ties default timeout behavior to `CommonConfigurationKeysPublic.SERVICE_SHUTDOWN_TIMEOUT`.

`StringInterner` provides `strongIntern(String)`, `weakIntern(String)`, and in-place `internStringsInArray(String[])`. The Javadoc says weak interning uses standard `String.intern()` behavior, while strong interning retains a strong representative reference.

`SysInfo` is an abstract plugin for host resource metrics. `newInstance()` returns the default implementation for the detected OS or throws `UnsupportedOperationException`. Abstract methods report virtual and physical memory totals and availability, logical processors, physical cores, CPU frequency, cumulative CPU time, CPU usage percentage, vcores used, network bytes read/written, and storage bytes read/written. Several metrics may return `-1` where unavailable.

`Tool` extends `Configurable` and defines `run(String[] args)`. Its Javadoc establishes the standard Hadoop command-line pattern: `ToolRunner` parses generic options into a `Configuration`, sets the tool's configuration, then leaves application-specific arguments for the tool. `ToolRunner` exposes `run(Configuration, Tool, String[])`, `run(Tool, String[])`, `printGenericCommandUsage(PrintStream)`, and `confirmPrompt(String)`.

`VersionInfo` exposes build metadata: version, Git revision, branch, compile date, build user, repository URL, source checksum, build version, protoc version, and `main(String[])`. Protected instance methods back the public static accessors, with a protected constructor taking a component name.

`org.apache.hadoop.util.bloom.BloomFilter` extends `Filter` with constructors for deserialization and configured vector size/hash count/hash type. It supports `add(Key)`, logical `and`, `or`, `xor`, `not`, `membershipTest(Key)`, `toString()`, `getVectorSize()`, and `Writable` `write(DataOutput)`/`readFields(DataInput)`. It is the standard false-positive/no-false-negative bit-vector filter.

`CountingBloomFilter` is a final `Filter` implementation using counters rather than bits. It adds `delete(Key)` and `approximateCount(Key)`. The approximate count contract is constrained by 4-bit bucket behavior: repeated insertion past 15 can overflow and raise error rates, while delete underflow can introduce false negatives.

`DynamicBloomFilter` extends `Filter` with a row-threshold constructor `(vectorSize, nbHash, hashType, nr)`. It grows by adding rows when the current row reaches the configured key threshold. It supports the same logical operations and `Writable` serialization as the other filters.

`HashFunction` wraps repeated hashing for Bloom filters. Its constructor takes vector size, hash count, and hash type. `hash(Key)` returns an array of positions, and `clear()` resets internal behavior/state.

`RemoveScheme` defines retouched Bloom filter clearing strategies: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`. `RetouchedBloomFilter` extends `BloomFilter` and implements `RemoveScheme`; it can record false positives through overloads accepting `Key`, `Collection<Key>`, `List<Key>`, or `Key[]`, then run `selectiveClearing(Key, short)` according to a remove scheme. It also serializes/deserializes its additional retouched-filter state.

`CloseableTaskPoolSubmitter` implements `TaskPool.Submitter` and `Closeable`. It wraps a non-null `ExecutorService`, exposes `getPool()`, submits `Runnable` tasks as `Future`, and shuts the pool down in `close()`.

`FutureIO` is a final utility class for integrating `Future`/`CompletableFuture` work with IOException-oriented Hadoop APIs. `awaitFuture(Future)` and the timeout overload evaluate a future and extract nested failures. `raiseInnerCause(ExecutionException)` and `raiseInnerCause(CompletionException)` always rethrow as the inner `IOException`, inner `RuntimeException`, or an `IOException` wrapper. `unwrapInnerException(Throwable)` recursively handles `IOException`, `UncheckedIOException`, `ExecutionException`, `CompletionException`, `RuntimeException`, and `Error`. `propagateOptions(FSBuilder, Configuration, optionalPrefix, mandatoryPrefix)` and its single-prefix overload map configuration keys into optional or mandatory builder options. `eval(CallableRaisingIOE)` evaluates in the current thread, converting IOExceptions to runtime failures inside a completed/failing `CompletableFuture`.

`RemoteIterators` is a final utility class for `org.apache.hadoop.fs.RemoteIterator` composition. It creates remote iterators from singletons, Java iterators, iterables, and arrays; maps items with `FunctionRaisingIOE`; performs type-casting wrappers; filters lazily; wraps close behavior; materializes to lists or arrays; applies a `ConsumerRaisingIOE` to each element while returning the count; and cleans up iterators. Its Javadoc emphasizes IOStatistics passthrough and debug-only statistics logging, plus close passthrough for iterators that hold remote resources.

The `org.apache.hadoop.tools`, `org.apache.hadoop.tools.protocolPB`, `org.apache.hadoop.tracing`, `org.apache.hadoop.util.curator`, and `org.apache.hadoop.util.hash` package elements in this range are empty placeholders in the JDiff output.

## Control flow and behavior

Service launch flow is explicit. A launcher creates or receives a service, passes command-line tail arguments into `LaunchableService.bindArgs`, initializes the service with the resulting non-null configuration, starts it through the normal `Service` lifecycle, then calls `execute()`. Exceptions from `execute()` are converted into process semantics: existing `ExitException` instances propagate, `ExitCodeProvider` exceptions are wrapped with their own exit code, and other exceptions become `ServiceLaunchException` with `EXIT_EXCEPTION_THROWN`.

Lifecycle state control is guarded by `ServiceStateModel`: callers can check proposed transitions before mutating service state, and invalid transitions are converted from boolean checks into thrown exceptions by `checkStateTransition`.

Command execution through `Shell` follows a template-method pattern. Subclasses describe commands through `getExecString()` and parse stdout through `parseExecResult(BufferedReader)`. The base class decides whether a run is needed based on the minimum interval, constructs and starts a process, merges stderr if configured, tracks the process and waiting thread, records exit code/timeout state, and exposes platform-specific command builders for common Hadoop needs.

Tool execution flows through `ToolRunner`: generic Hadoop options are parsed into the configuration before `Tool.run(String[])` sees the remaining command-specific arguments. This keeps tool implementations focused on application options while preserving standard `-conf`, `-D`, filesystem, jobtracker, and related generic behavior.

Shutdown behavior is centralized in `ShutdownHookManager`. Instead of relying on JVM hook ordering, Hadoop components register hooks with numeric priorities and optional timeouts. During JVM shutdown, the manager runs hooks in priority order, enforcing configured/default time budgets.

Bloom filter behavior is hash-driven. `HashFunction.hash(Key)` calculates vector positions; filters mutate bit vectors, counter vectors, or dynamic rows on `add`; membership checks require all associated positions to be present/non-zero. Logical operations combine compatible filters. Retouched filters collect known false positives and selectively clear positions, accepting a trade-off between reducing false positives and possibly introducing false negatives.

Future and iterator utilities make asynchronous and remote-listing code fit Hadoop's checked-exception style. `FutureIO.awaitFuture` blocks until success/failure/timeout and unwraps nested IO-related causes. `RemoteIterators` adapters defer mapping and filtering to `hasNext()`/`next()` time, propagate `IOException`, and optionally preserve close/statistics behavior through wrapper chains.

## State and persistence behavior

Most state in this chunk is process-local support state rather than distributed filesystem data. Service launch classes manage lifecycle state through `Service` and convert exceptions to process exit status. `HadoopUncaughtExceptionHandler` affects JVM-global uncaught-exception behavior when installed.

`ApplicationClassLoader` maintains classpath URLs and parent/system-class policy. This state influences class identity and resource resolution for the lifetime of the classloader, which is significant in long-running daemons or application containers.

`OperationDuration` stores start and finish timestamps; `DurationInfo` adds log text and log-level behavior. `Shell` stores environment overrides, working directory, current `Process`, timeout flag, exit code, waiting thread, minimum run interval, and whether parent environment is inherited. `ShutdownHookManager` holds a registry of hooks, priorities, and per-hook timeout metadata until shutdown or explicit removal/clear.

`StringInterner` state differs by mode: strong interning retains representatives and can grow memory usage, while weak/standard interning depends on JVM intern table behavior. `ReflectionUtils` may cache constructor/reflection data in implementation, although this XML chunk only exposes the API.

The Bloom filters explicitly persist through Hadoop `Writable` methods. `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, and `RetouchedBloomFilter` expose zero-argument constructors for `readFields` and serialize their filter vectors/counters/rows and parameters to `DataOutput`. Their state is probabilistic and lossy by design: serialized filters preserve the membership approximation, not the original set.

`FutureIO` and `RemoteIterators` are stateless utility classes from the public API perspective. `CloseableTaskPoolSubmitter` owns an `ExecutorService` lifecycle and can stop accepting/running tasks when `close()` shuts the pool down.

`VersionInfo` reads build-time metadata packaged with Hadoop components. `SysInfo` implementations surface operating-system counters that are external and time-varying rather than persisted by Hadoop.

## Dependencies and integration points

The service launcher APIs integrate with `org.apache.hadoop.service.Service`, `AbstractService`, `Configuration`, `ExitUtil.ExitException`, `ExitCodeProvider`, and process exit handling. They are intended for command-line entry points and service daemons.

The utility layer depends on core Java APIs including `URLClassLoader`, `MalformedURLException`, `Logger`/SLF4J, commons logging, `AutoCloseable`, `Checksum`, `ThreadMXBean`-style diagnostics by implication, `PrintStream`, `Process`, `File`, `BufferedReader`, `TimeUnit`, `Duration`, `DataInput`, `DataOutput`, `IOException`, and `InterruptedIOException`. Hadoop-specific dependencies include `Configuration`, `Configurable`, `Writable`, `GenericOptionsParser`, `CommonConfigurationKeysPublic`, and filesystem-oriented callers that rely on shell commands for permissions, ownership, symlinks, and platform utilities such as `winutils`.

`Shell` is deeply platform-integrated. It depends on OS detection booleans and command formats for Unix-like systems, Windows, Solaris, macOS, FreeBSD, Linux, PowerPC 64-bit, setsid availability, environment variable syntax, Hadoop home resolution, and Windows command length limits.

`Tool`/`ToolRunner` are integration points for nearly every Hadoop CLI application. They bridge generic Hadoop options, user configuration resources, and application-specific command parsing.

Bloom filters depend on `org.apache.hadoop.util.bloom.Filter`, `Key`, `org.apache.hadoop.util.hash.Hash` hash types, `Writable` serialization, and Java collection types for false-positive lists. They can be used by distributed cache, web cache, network, or filesystem metadata code that needs compact approximate membership.

The functional helpers integrate with `ExecutorService`, `Future`, `CompletableFuture`, `ExecutionException`, `CompletionException`, `TimeoutException`, `UncheckedIOException`, Hadoop `FSBuilder`, `Configuration`, `RemoteIterator`, `IOStatisticsSource` by documentation, and Hadoop functional interfaces such as `CallableRaisingIOE`, `FunctionRaisingIOE`, and `ConsumerRaisingIOE`.

## Risks and edge cases

Service lifecycle code must treat same-state proposals carefully: `isValidStateTransition` does not validate `current == proposed`, so callers need a separate idempotence policy if repeated lifecycle calls are allowed. Incorrect exception mapping in a launcher can hide meaningful application exit codes.

`HadoopUncaughtExceptionHandler` intentionally exits on `Error`. Tests and embedding environments must not install it casually where process termination is unacceptable.

`LaunchableService.bindArgs` can replace the configuration before initialization. Implementations that return `null`, mutate shared configurations unexpectedly, or forget to instantiate a needed subclass such as a YARN-specific configuration can fail later during `init`.

Exit codes are a public compatibility surface. Reusing HTTP-like values inconsistently, or returning codes outside the documented single-byte-friendly ranges, can break scripts and service managers.

Application classloader isolation is sensitive to `SYSTEM_CLASSES_DEFAULT` and `isSystemClass` pattern ordering. Loading Hadoop or dependency classes on the wrong side can produce class identity conflicts, linkage errors, or resource shadowing.

`Shell` APIs are inherently platform fragile. Windows command-line length, `winutils` discovery, bash availability, setsid support, command quoting, inherited environment, and non-sorted or locale-specific command output can all affect behavior. Long-running or timed-out processes must be destroyed and not left tracked in `getAllShells()`.

`ShutdownHookManager` hooks with the same priority run in nondeterministic order. Hooks must tolerate partial shutdown, timeout termination, and dependencies already being stopped. Clearing hooks is dangerous outside tests.

Strong string interning can retain unbounded input. Code should avoid strong-interning high-cardinality or user-controlled strings.

`ReflectionUtils.copy` and `cloneWritableInto` rely on correct `Writable` serialization. Broken `write`/`readFields` implementations can corrupt destination objects, and reflection-based construction may fail for missing no-argument constructors or inaccessible classes.

CRC implementations must exactly match expected polynomials and byte ordering. Any optimization or substitution needs cross-checks against `java.util.zip.CRC32` and known CRC32-C vectors.

`SysInfo` metrics may be unavailable, OS-specific, or sampled at different times. Callers must handle `-1`, unsupported OS exceptions, and counter wrap/reset behavior.

Counting Bloom filters can overflow counters above 15 repeated inserts and underflow after deletes, increasing false positives or introducing false negatives. Dynamic filters must only combine compatible layouts. Retouched filters deliberately allow false negatives after selective clearing, which violates the standard Bloom filter guarantee.

`FutureIO.unwrapInnerException` rethrows `RuntimeException` and `Error` immediately. Callers expecting only `IOException` must account for unchecked propagation. Timeout handling in `awaitFuture` does not imply cancellation unless callers do it separately.

`RemoteIterators.foreach` explicitly does not close the iterator afterwards. Callers must invoke `cleanupRemoteIterator` or use close-aware wrappers when remote listings hold connections or file handles. Filtering in `hasNext()` can perform remote IO earlier than callers expect.

## Test signals

Useful test coverage for code using or changing these APIs should include:

- Service lifecycle tests for valid and invalid `Service.STATE` transitions, same-state idempotence behavior, `checkStateTransition` exception text, and launch flow order: `bindArgs`, `init`, `start`, `execute`.
- Launcher exception tests covering raw `ExitUtil.ExitException`, arbitrary `ExitCodeProvider`, generic checked exceptions, runtime exceptions, formatted `ServiceLaunchException` constructors, and expected process exit codes.
- Uncaught exception handler tests that distinguish ordinary exceptions from `Error` without terminating the test JVM directly, using injectable or intercepted exit behavior.
- Classloader tests for application-first loading, parent/system-class delegation, negative and positive system class patterns, resource lookup, malformed classpath entries, and dependency shadowing.
- Duration/logging tests for `OperationDuration.finished()`, `value()`, `asDuration()`, `humanTime()`, and `DurationInfo.close()` at info versus debug.
- Checksum tests using known CRC32 and CRC32-C vectors, byte-array offsets, single-byte updates, reset behavior, and comparison with JDK CRC32 where applicable.
- Reflection tests for `newInstance` with `Configurable` classes, constructor caching behavior, thread dump throttling, serialization copy compatibility, and inherited field/method discovery.
- Shell tests across mocked or isolated OS modes for command construction, Windows command length rejection, script extension selection, Hadoop-home/bin qualification, winutils absence, environment and working-directory propagation, timeout handling, process cleanup, and static `execCommand` error propagation.
- Shutdown hook tests for priority ordering, equal-priority nondeterminism tolerance, hook removal, timeout enforcement, shutdown-in-progress reporting, and test-only clearing.
- ToolRunner tests for generic option parsing, configuration injection, null configuration behavior, usage printing, prompt yes/no parsing, and preservation of application-specific arguments.
- VersionInfo tests that packaged build metadata is readable and `main` prints fields without null-sensitive failures.
- Bloom filter tests for serialization round trips, membership false-positive/no-false-negative expectations for standard filters, logical operation compatibility checks, counting delete and approximate count behavior, overflow/underflow edges, dynamic row growth, and retouched selective-clearing schemes.
- FutureIO tests for successful futures, interrupted futures mapped to `InterruptedIOException`, nested `ExecutionException`/`CompletionException`/`UncheckedIOException` unwrapping, runtime/error propagation, timeout behavior, and `FSBuilder` optional versus mandatory option propagation from configuration prefixes.
- RemoteIterators tests for singleton/iterator/iterable/array adapters, lazy mapping/filtering, IOException propagation from source and callbacks, close passthrough, `toList`/`toArray` materialization, returned count from `foreach`, debug-only IOStatistics paths, and explicit cleanup of closeable remote iterators.
