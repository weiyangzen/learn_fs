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
