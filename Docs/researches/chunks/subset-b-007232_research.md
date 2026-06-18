# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 1-6056

## Scope

This chunk is the opening segment of the JDiff API snapshot for Apache Hadoop Common 3.5.0. It begins with the XML/JDiff metadata and covers public API entries from `org.apache.hadoop.HadoopIllegalArgumentException`, `org.apache.hadoop.conf`, crypto key provider packages, and the beginning of `org.apache.hadoop.fs`. It ends inside the `org.apache.hadoop.fs.CommonConfigurationKeysPublic` field list at `TFILE_IO_CHUNK_SIZE_DEFAULT`, so the final class is incomplete in this chunk.

The source is generated compatibility metadata, not implementation source. The research surface is therefore the externally visible API contract: package/class/interface names, inheritance and implemented interfaces, constructors, methods, fields, visibility, abstract/static/final/synchronized flags, declared exceptions, deprecation markers, and embedded Javadocs.

## Purpose

This JDiff file preserves the Hadoop Common 3.5.0 public API for release-to-release compatibility comparison. In this range it documents foundational configuration behavior, key-provider contracts for encryption, filesystem implementation contracts, stream capability interfaces, checksum filesystem behavior, and public configuration constants.

`org.apache.hadoop.conf.Configuration` is the largest API in the range. It is Hadoop's central configuration container, loading XML resources from classpath, local paths, URLs, input streams, and other `Configuration` instances. The documented behavior includes default resource loading, lazy resource initialization, final-parameter precedence, variable expansion from other properties/environment/system properties, deprecation aliasing, typed getters/setters, class loading, credential-provider lookup for passwords, XML/JSON-style dumping, Writable serialization, property source tracking, tags, and reload behavior.

The crypto portion exposes `KeyProvider` and `KeyProviderFactory`, Hadoop's abstraction for storing and retrieving encryption key material independently from the consumers that encrypt/decrypt data. It covers versioned keys, metadata, key creation, deletion, rolling, provider discovery, password requirements, cache invalidation, and explicit persistence through `flush()`.

The filesystem portion starts with `Abortable` and a broad `AbstractFileSystem` contract. `AbstractFileSystem` is the implementation-facing API used by `FileContext`, with fully qualified path requirements, URI/scheme validation, server defaults, create/open/delete/rename/mkdir, status/listing, checksum, ACL, xattr, snapshot, storage policy, delegation-token, capability, multipart upload, and enclosing-root methods.

Later filesystem entries document block-locality metadata (`BlockLocation`), storage policy SPI (`BlockStoragePolicySpi`), bulk deletion APIs, byte-buffer read contracts, cache/readahead/unbuffer stream capability interfaces, checksum-related options and exceptions, `ChecksumFileSystem`, closed/capacity exception types, and the beginning of `CommonConfigurationKeysPublic`.

## Important APIs, Types, and Functions

### Base and Configuration APIs

- `HadoopIllegalArgumentException` extends `IllegalArgumentException` to distinguish invalid Hadoop implementation arguments from JDK-originated `IllegalArgumentException`.
- `Configurable` declares `setConf(Configuration)` and `getConf()`, the standard injection contract for Hadoop components.
- `Configured` implements `Configurable` and acts as a base class storing a `Configuration`.
- `Configuration` implements `Iterable<Map.Entry<String,String>>` and `Writable`. Constructors create a default-loading configuration, a load-defaults-controlled configuration, or a clone from another configuration.
- Static `Configuration.addDeprecation(...)`, `addDeprecations(...)`, `isDeprecated(...)`, `dumpDeprecatedKeys()`, and `hasWarnedDeprecation(...)` expose global configuration-key deprecation management. Multi-key overloads are deprecated in favor of single replacement keys, while the bulk API uses a lock-free/atomic swap loop.
- Resource loading APIs include `addDefaultResource(String)`, many `addResource(...)` overloads for resource names, `URL`, `Path`, `InputStream`, named streams, and another `Configuration`, plus restricted-parser variants.
- Reload and lifecycle APIs include `reloadConfiguration()`, static synchronized `reloadExistingConfigurations()`, `clear()`, `size()`, synchronized `getProps()`, `iterator()`, `getFinalParameters()`, and `setQuietMode(boolean)`.
- String accessors include `get`, `getTrimmed`, `getRaw`, `onlyKeyExists`, `set`, `unset`, `setIfUnset`, `substituteCommonVariables`, and prefix/regex queries (`getPropsWithPrefix`, `getValByRegex`).
- Typed accessors include `getInt`/`setInt`, `getInts`, `getLong`/`setLong`, `getLongBytes`, `getFloat`/`setFloat`, `getDouble`/`setDouble`, `getBoolean`/`setBoolean`, `setBooleanIfUnset`, enum and enum-set APIs, time-duration APIs, storage-size APIs, regex pattern APIs, integer range APIs, string collection/array APIs, and `setStrings`.
- Security-sensitive accessors include `getPassword`, `getPasswordFromCredentialProviders`, and protected `getPasswordFromConfig`, explicitly preferring credential providers before clear-text fallback.
- Network and plugin APIs include socket address getters/setters/update helpers, `getClassByName`, `getClassByNameOrNull`, `getClasses`, typed `getClass`, `getInstances`, `setClass`, and configurable `ClassLoader` access.
- Local path/resource helpers include `getLocalPath`, `getFile`, `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader`.
- Output/debug APIs include multiple `writeXml(...)` overloads, static `dumpConfiguration(...)`, `toString()`, and a debugging `main(String[])`.
- `StorageUnit` is an enum-like class with abstract conversion methods between bytes, KB, MB, GB, TB, PB, and EB, plus long/short/suffix names and default conversion behavior.

### Crypto Key Provider APIs

- `KeyProvider` is an abstract, `Closeable`, thread-safe provider of secret key material. It is constructed with a `Configuration` and exposes `getConf()` plus static `options(Configuration)`.
- Key lookup APIs include `getKeyVersion(String)`, `getKeys()`, `getKeysMetadata(String...)`, `getKeyVersions(String)`, `getCurrentKey(String)`, and `getMetadata(String)`.
- Mutation APIs include abstract `createKey(String, byte[], Options)`, abstract `deleteKey(String)`, abstract `rollNewVersion(String, byte[])`, default material-generating `createKey(String, Options)` and `rollNewVersion(String)`, `invalidateCache(String)`, and abstract `flush()`.
- Helper APIs include protected `generateKey(int, String)`, static `getBaseName(String)`, protected static `buildVersionName(String, int)`, static `findProvider(List<KeyProvider>, String)`, `needsPassword()`, `noPasswordWarning()`, `noPasswordError()`, and no-op/default `close()`.
- Public fields define default cipher and bit-length names/values and JCEKS serialization-filter keys.
- `KeyProviderFactory` is a service-loader-backed factory. It defines abstract `createProvider(URI, Configuration)`, static `getProviders(Configuration)`, static `get(URI, Configuration)`, and `KEY_PROVIDER_PATH`.
- `org.apache.hadoop.crypto.key.kms.SyncGenerationPolicy` is an enum for deciding how many values to generate synchronously when a KMS value queue is empty.

### Abstract Filesystem Contract

- `Abortable.abort()` returns an `AbortableResult` and guarantees that aborted stream output must not become visible. Unsupported implementations may throw `UnsupportedOperationException`.
- `AbstractFileSystem` implements `PathCapabilities`. Its constructor validates URI scheme/authority/default port expectations for a concrete filesystem scheme.
- Static factory/statistics APIs include `createFileSystem(URI, Configuration)`, `get(URI, Configuration)`, protected static synchronized `getStatistics(URI)`, `clearStatistics()`, `printStatistics()`, and protected `getAllStatistics()`.
- URI/path APIs include `isValidName(String)`, `checkScheme(URI, String)`, abstract `getUriDefaultPort()`, `getUri()`, `checkPath(Path)`, `getUriPath(Path)`, `makeQualified(Path)`, `getInitialWorkingDirectory()`, `getHomeDirectory()`, and `resolvePath(Path)`.
- Create/open/mutation APIs include final high-level `create(Path, EnumSet<CreateFlag>, Options.CreateOpts...)`, abstract `createInternal(...)`, abstract `mkdir`, abstract `delete`, `open(Path)`, abstract `open(Path,int)`, `truncate`, abstract `setReplication`, final `rename(Path,Path,Options.Rename...)`, abstract no-overwrite `renameInternal(Path,Path)`, overwrite-capable `renameInternal(Path,Path,boolean)`, `setPermission`, `setOwner`, and `setTimes`.
- Symlink/status/listing APIs include `supportsSymlinks()`, `createSymlink`, `getLinkTarget`, `getFileChecksum`, abstract `getFileStatus`, `msync`, `getFileLinkStatus`, `getFileBlockLocations`, path and no-arg `getFsStatus`, `listStatusIterator`, `listLocatedStatus`, abstract `listStatus`, and `listCorruptFileBlocks`.
- Security and metadata APIs include `setVerifyChecksum`, `getCanonicalServiceName`, `getDelegationTokens`, ACL methods (`modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, `getAclStatus`), xattr methods (`setXAttr`, `getXAttr`, `getXAttrs`, `listXAttrs`, `removeXAttr`), snapshots, and storage policy methods.
- Newer extension points include `openFileWithOptions(Path, OpenFileParameters)` returning `CompletableFuture<FSDataInputStream>`, `hasPathCapability(Path,String)`, `createMultipartUploader(Path)`, `getEnclosingRoot(Path)`, and protected final `methodNotSupported()`.
- The protected `statistics` field exposes per-filesystem `FileSystem.Statistics`.

### Filesystem Data and Capability Types

- `FileStatus.AttrFlags` is an enum for entity attributes.
- `AvroFSInput` adapts `FSDataInputStream` to Avro `SeekableInput`, with constructors from stream/length or `FileContext`/`Path`, and implements `length`, `read`, `seek`, `tell`, and `close`.
- `BatchListingOperations` exposes batched status and located-status listing through `RemoteIterator<PartialListing<...>>`; implementers should also advertise the experimental batch-listing path capability.
- `BlockLocation` is a serializable carrier for block replica locality, topology paths, cached hosts, storage IDs/types, offsets, lengths, corruption state, and striped/erasure-coded status. It has many constructors for replicated and richer storage metadata and setters/getters for every field.
- `BlockStoragePolicySpi` exposes storage policy name, preferred storage types, creation fallbacks, replication fallbacks, and copy-on-create/inherit-only status.
- `BulkDelete` extends `IOStatisticsSource` and `Closeable`; it defines `pageSize()`, `basePath()`, and `bulkDelete(Collection<Path>)`. The contract is non-atomic, file/object-only, idempotency-tolerant, path-bounded under `basePath`, and may omit parent directory marker repair.
- `BulkDeleteSource.createBulkDelete(Path)` is the provider hook for bulk delete support and must be paired with the `CommonPathCapabilities.BULK_DELETE` capability.
- `ByteBufferPositionedReadable` defines thread-safe positioned reads into `ByteBuffer` without changing stream offset, plus `readFully`; support should be checked through stream capabilities.
- `ByteBufferReadable` defines sequential reads into `ByteBuffer`, with well-defined buffer position advancement on success and undefined buffer state on exception.
- `CanSetDropBehind`, `CanSetReadahead`, and `CanUnbuffer` expose optional stream-level cache and resource-release controls.
- `Options.ChecksumCombineMode` is an enum for client-side file checksum aggregation mode; Javadocs distinguish it from persistent file-at-rest checksum options.
- `ChecksumException` extends `IOException` and carries the bad-data position through `getPos()`.
- `ChecksumFileSystem` extends `FilterFileSystem` and supplies a client-side checksum layer over a raw filesystem. It exposes checksum-file naming/length helpers, checksum verification/write flags, raw filesystem access, open/append/create/createNonRecursive/truncate/concat/delete/rename/list/mkdir/copy/local-output/report-failure flows, builder overrides, and path capability filtering.
- `ClosedIOException` extends `PathIOException` for closed streams, caches, or other closeable resources.
- `ClusterStorageCapacityExceededException` is an HDFS-originated `IOException` signaling cluster storage capacity exhaustion.
- `CommonConfigurationKeysPublic` begins a public constant set for Hadoop core configuration keys and defaults. Visible fields include network topology script/mapping keys, default filesystem keys, disk free/used interval keys, local and FTP filesystem keys, trash and protected-directory keys, automatic close, filesystem creation parallelism, mapfile/sequencefile/TFile IO keys, compression codec keys, checksum-error handling, symlink resolution, topology resolution, and deprecated MapReduce-era `IO_SORT_*` constants.

## Control Flow

The XML has no executable control flow, but the API contracts imply important runtime paths.

Configuration flow starts with construction, optionally loading default resources. Resource declarations are appended in order; later resources override earlier values unless a previous value is marked final. Calls to `get`, typed getters, iteration, write, or dump APIs can lazily load resources. Programmatic `set` values overlay resource values, while `reloadConfiguration()` clears loaded resource/final-parameter state so resources are read again before later access. Static `reloadExistingConfigurations()` triggers reload across live instances.

Configuration deprecation flow is global. Developers register deprecated keys and replacement keys before resource loading. Accessing or setting deprecated names resolves through replacement keys, and setting aliases propagates values across associated names. `addDeprecations` creates a new deprecation context and atomically swaps it in, retrying on races.

Variable expansion flow processes returned string values. A placeholder first resolves against this `Configuration`, then against environment variables for `env.*`, and then against Java system properties. Environment expressions support default syntaxes for undefined or empty variables. `substituteCommonVariables` exposes this expansion path directly and can throw when expansion exceeds the configured substitution limit.

Credential flow for passwords first attempts to resolve the configuration key as a credential-provider alias, then falls back to clear-text configuration through the protected fallback method. Callers must handle `IOException` from provider access.

Key-provider flow uses `KeyProviderFactory.getProviders(conf)` to discover provider URIs from configuration, uses service-loaded factories to instantiate providers, then locates key material by name or version. Creating or rolling keys can either accept caller-supplied material or generate material from configured algorithm/bit-length options, then delegate to abstract provider storage methods. Mutations require `flush()` for persistence guarantees; `invalidateCache()` is a post-roll hook for stronger current-version reads.

`AbstractFileSystem` flow starts with URI/scheme/authority validation and path qualification. Public high-level methods such as `create` and `rename` enforce `FileContext`-style contracts, then call lower-level abstract implementation hooks such as `createInternal` and `renameInternal`. Most methods require the `Path` to belong to the target filesystem; symlink resolution can throw `UnresolvedLinkException`.

Listing and status flow includes both array-returning APIs and streaming `RemoteIterator` APIs. Located-status listings add block locations, with HDFS-specific notes that replicated and erasure-coded files expose different `BlockLocation` formats.

Bulk delete flow is explicitly scoped and non-atomic: a caller obtains a `BulkDelete` from `BulkDeleteSource`, submits at most `pageSize()` absolute paths below `basePath()`, receives only failed path/message pairs, and closes the object so IO statistics are updated.

Byte-buffer read flow requires callers to prepare `ByteBuffer.position()` and `limit()` before invoking reads. Successful reads advance position and leave limit unchanged; exception paths leave buffer state undefined. Positioned byte-buffer reads are explicitly thread-safe and do not alter the stream's current offset.

Checksum filesystem flow wraps a raw filesystem. Data reads verify companion checksum files when enabled; writes can create checksum side files; checksum failures can be reported through `reportChecksumFailure`; copy-to-local can optionally include CRC files; and some capabilities are filtered because the checksum wrapper blocks or changes behavior relative to the raw filesystem.

## State and Persistence Behavior

The JDiff file itself persists the generated Hadoop Common 3.5.0 API contract for compatibility checks. It does not persist Hadoop runtime state.

`Configuration` owns mutable in-memory state: resource list, loaded properties, overlay values set programmatically, final-parameter tracking, property sources, tags, quiet mode, class loader, null-value test mode, and system-property restriction settings. Its `Writable` methods define binary serialization behavior for transferring configuration state, while `writeXml` persists non-default properties and attributes to XML. `dumpConfiguration` writes a diagnostic property/resource/final representation to a `Writer`.

`Configuration` also interacts with process-global state. Default resources, deprecation mappings, deprecation warning tracking, and `reloadExistingConfigurations()` affect more than one instance. The deprecation context is intentionally updated atomically without coarse locking, so compatibility-sensitive tests must account for global ordering.

Configuration resource values persist only in the underlying XML/resource files or programmatic setters; `reloadConfiguration()` does not persist changes. Final parameters prevent later resources from overriding values during load. `InputStream` resources are cached by the API, increasing memory usage but allowing delayed load after the original stream is consumed and closed.

Password retrieval may expose persisted secrets from credential providers or clear-text configuration. The returned type is `char[]`, which lets callers wipe memory after use; the XML contract does not guarantee provider-specific lifecycle or zeroing.

`KeyProvider` implementations own persistent or transient key storage. `isTransient()` identifies providers intended for short-lived keying material rather than durable storage. Abstract mutations do not guarantee durability until `flush()` writes changes to the persistent store. Version names encode base names and numeric versions using the documented `name@version` pattern.

`AbstractFileSystem` implementations persist namespace and metadata changes in their backing stores: file creation, writes, deletes, renames, truncation, directories, replication, owner/group, permissions, timestamps, ACLs, xattrs, snapshots, storage policies, and multipart uploads. The abstract base itself holds URI identity and `statistics` state, while static statistics tables are process-global and synchronized.

`BlockLocation` is serializable metadata, not live storage state. It snapshots block/replica location information, including topology, cached hosts, storage IDs/types, offset/length, corruption, and erasure-coded grouping semantics.

`ChecksumFileSystem` persists checksum side files alongside raw data files and can alter copy/delete/rename/list behavior to account for checksum metadata. `setVerifyChecksum` and `setWriteChecksum` are in-memory flags controlling read/write behavior.

`BulkDelete` has destructive persistent side effects on object/file stores. It is non-atomic and idempotent by design, so retries after network failure can delete newly created objects that reuse a submitted path.

`CommonConfigurationKeysPublic` constants are stable public API names for configuration keys and defaults. The fields themselves do not persist state, but callers and XML config files depend on their string values and default constants remaining compatible.

## Dependencies and Integration Points

This chunk integrates with Java core APIs including `String`, arrays, `Iterable`, collections, `Properties`, `Pattern`, `Class`, `ClassLoader`, `URL`, `URI`, `InputStream`, `OutputStream`, `Reader`, `Writer`, `DataInput`, `DataOutput`, `File`, `InetSocketAddress`, `TimeUnit`, `ByteBuffer`, `CompletableFuture`, `IOException`, `EOFException`, `NoSuchAlgorithmException`, and `UnsupportedOperationException`.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration`, `Configurable`, and `Configured` as the central configuration and dependency-injection surface.
- `org.apache.hadoop.io.Writable` for configuration serialization.
- `org.apache.hadoop.fs.Path`, `FileSystem`, `FileContext`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `LocatedFileStatus`, `RemoteIterator`, `PartialListing`, `FileChecksum`, `BlockLocation`, `FsServerDefaults`, `FsStatus`, `CreateFlag`, `Options`, `MultipartUploaderBuilder`, `BlockStoragePolicySpi`, `PathCapabilities`, and `CommonPathCapabilities`.
- `org.apache.hadoop.fs.permission.FsPermission`, `AclEntry`, and `AclStatus` for file permissions and ACL operations.
- `org.apache.hadoop.security.AccessControlException` and delegation-token types for authorization and security-token integration.
- `org.apache.hadoop.fs.statistics.IOStatisticsSource` for bulk delete statistics publication.
- `org.apache.hadoop.crypto.key` provider and factory APIs for encryption key lifecycle.
- Credential provider APIs referenced by `Configuration.getPassword`.
- Apache Avro's `SeekableInput` through `AvroFSInput`.
- Java Cryptography Architecture key generation by algorithm and bit length.
- Service-loader discovery for `KeyProviderFactory`.

## Risks and Edge Cases

- The range ends in the middle of `CommonConfigurationKeysPublic`; adjacent chunks are required for the complete class and source-file report.
- JDiff records signatures and Javadocs, not method bodies. Exact XML parsing behavior, synchronization internals, exception messages, default values, credential-provider lookup order, classloader fallback, checksum-file format, and filesystem-specific behavior require implementation-source review.
- `Configuration` uses global deprecation/default-resource state. Tests that mutate deprecation mappings, default resources, or existing configurations can leak state across cases.
- Multi-key deprecation overloads are themselves deprecated. Code still depending on multi-key alias semantics may retain compatibility pressure even as Javadocs direct callers to single replacement keys.
- Resource loading is lazy; a first `get` can trigger IO and parsing. Errors may surface far from `addResource`, and `InputStream` resources are cached with explicit memory-consumption warnings.
- Final parameters create ordering-sensitive behavior. Resource addition order and reload behavior must be tested because later resources cannot override earlier final values.
- Variable expansion can read environment variables and Java system properties. This can make tests environment-sensitive and can expose secrets if configuration values include unrestricted placeholders.
- `setRestrictSystemPropertiesDefault`, `setRestrictSystemProperties`, and `setRestrictSystemProps` indicate security hardening paths; exact enforcement requires code review because JDiff lists limited documentation.
- Typed getters differ in failure behavior. Invalid numeric/time/storage values can throw `NumberFormatException`, invalid enum mappings can throw `IllegalArgumentException`, while invalid booleans fall back to defaults.
- `getPattern` deliberately does not trim values, unlike many string/enum accessors. Whitespace handling is a compatibility risk.
- `getPassword` can fall back to clear text. Deployments expecting no clear-text secrets need tests/configuration that disable or detect fallback behavior.
- `KeyProvider` implementations must be thread safe. Caching, rolling new versions, `invalidateCache`, and `flush` are high-risk for stale key material and durability.
- `needsPassword()` and password warning/error helpers imply provider initialization may partially succeed without required credentials. Callers must surface actionable errors without leaking secrets.
- `AbstractFileSystem` requires path ownership and fully qualified/slash-relative semantics. Incorrect `checkPath`, `makeQualified`, or URI default-port handling can route operations to the wrong filesystem.
- Many `AbstractFileSystem` methods are optional default implementations. Callers must handle `UnsupportedOperationException` for symlinks, snapshots, ACLs, xattrs, storage policies, multipart upload, path capabilities, and `msync`.
- `renameInternal` has separate no-overwrite and overwrite flows. Filesystems without native overwrite rely on the default path; race handling around destination existence is a compatibility and data-loss risk.
- `BlockLocation` semantics differ for replicated and erasure-coded files. Callers interpreting offset/length/hosts as per-replica physical block data can be wrong for striped files.
- Bulk delete is not atomic and is idempotency-oriented. Retried requests can delete newly created objects at the same paths, and parent directories/markers are not guaranteed to remain.
- Byte-buffer read APIs leave buffer state undefined on exception. Callers must not reuse position/limit assumptions after failed reads.
- `ChecksumFileSystem` can block or alter capabilities of the wrapped raw filesystem; wrapper tests must validate capability filtering and checksum side-file handling.
- Public configuration constants are compatibility-critical. Renaming, removing, or changing defaults can break XML configs, downstream code, and compatibility tests.

## Test Signals

- API compatibility tests should parse this XML and verify the public/protected signatures, fields, constructors, deprecation markers, and declared exceptions for `Configuration`, `StorageUnit`, `KeyProvider`, `KeyProviderFactory`, `AbstractFileSystem`, `BlockLocation`, `BulkDelete`, byte-buffer stream interfaces, and `ChecksumFileSystem`.
- Configuration tests should cover default-resource loading, disabled default loading, resource override ordering, final parameters, lazy load on first access, reload behavior, cloning, `Writable` round trips, XML writing, dumping individual/missing/all properties, property-source tracking, and iteration.
- Deprecation tests should cover single-key and deprecated multi-key aliases, bulk atomic addition, no override of existing deprecations, setting deprecated and replacement keys, warning tracking, and failure when adding after resource load where applicable.
- Variable expansion tests should cover nested configuration references, Java system properties, environment variables, empty/undefined env default syntax, substitution limits, raw versus expanded getters, and system-property restriction settings.
- Typed getter tests should cover invalid ints/longs/floats/doubles/time durations/storage sizes/enums/patterns, trimming differences, comma-delimited string/int parsing, enum `*` expansion, duplicate enum values differing only by case, and boolean fallback behavior.
- Credential tests should cover provider alias lookup, clear-text fallback, missing aliases, IO failures, returned `char[]` behavior, and configurations that should reject clear-text secrets.
- Key-provider tests should cover provider discovery from `KEY_PROVIDER_PATH`, URI scheme selection, transient provider behavior, create/delete/roll/current-version metadata, generated-key paths, base/version name parsing, cache invalidation after roll, password-required flows, close, and flush durability.
- `AbstractFileSystem` implementation tests should exercise URI validation, path qualification/checking, create/open/delete/rename/mkdir/truncate, server defaults by path, status/link status, block locations, listings, checksum, corrupt-block iteration, verify-checksum toggles, delegation tokens, ACLs, xattrs, snapshots, storage policies, multipart uploader creation, path capabilities, and unsupported-operation paths.
- Block-location tests should cover all constructors, copy construction, getters/setters, corrupt and striped flags, cached hosts, storage IDs/types, topology paths, replicated examples, and erasure-coded block-group interpretation.
- Bulk delete tests should validate base-path enforcement, page-size enforcement, invalid path rejection, file-only behavior, partial failure reporting, idempotent retry hazards, close/statistics updates, and capability advertisement.
- Byte-buffer stream tests should cover zero-length reads, EOF behavior, position/limit advancement on success, undefined buffer recovery after exception, positioned reads that do not affect stream offset, `readFully` EOF behavior, and unsupported capability checks.
- Checksum filesystem tests should cover checksum side-file naming and length calculation, read verification, write checksum toggles, checksum failure reporting, raw filesystem delegation, create/open/append/truncate/concat/delete/rename/list behavior, local copy CRC inclusion, builder methods, and path capability filtering.
