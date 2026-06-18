# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007232`: lines 1-6056, `Docs/researches/chunks/subset-b-007232_research.md`
- `subset-b-007233`: lines 6057-12223, `Docs/researches/chunks/subset-b-007233_research.md`
- `subset-b-007234`: lines 12224-18113, `Docs/researches/chunks/subset-b-007234_research.md`
- `subset-b-007235`: lines 18114-24626, `Docs/researches/chunks/subset-b-007235_research.md`
- `subset-b-007236`: lines 24627-30661, `Docs/researches/chunks/subset-b-007236_research.md`
- `subset-b-007237`: lines 30662-36701, `Docs/researches/chunks/subset-b-007237_research.md`
- `subset-b-007238`: lines 36702-42861, `Docs/researches/chunks/subset-b-007238_research.md`
- `subset-b-007239`: lines 42862-48966, `Docs/researches/chunks/subset-b-007239_research.md`
- `subset-b-007240`: lines 48967-50813, `Docs/researches/chunks/subset-b-007240_research.md`

## Chunk Research

### subset-b-007232: lines 1-6056

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

### subset-b-007233: lines 6057-12223

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 6057-12223

## Scope

This chunk is a jdiff public API description for Hadoop Common 3.5.0. It starts near the end of `org.apache.hadoop.fs.CommonConfigurationKeysPublic`, covers several core `org.apache.hadoop.fs` public APIs, and ends inside the `FileSystem.create(Path, FsPermission, boolean, int, short, long, Progressable)` method documentation. The source is XML metadata generated from Java APIs, so it exposes class/interface names, signatures, exception contracts, visibility, deprecation text, and Javadoc, but not method bodies.

The covered API surface is:

- The tail of `CommonConfigurationKeysPublic`, with public configuration-key constants for TFile, caller context, IPC, security, crypto, KMS, shell, HTTP, credential providers, tags, service shutdown, Prometheus, metrics, and JMX NaN filtering.
- `ContentSummary`, `CreateFileOptionKeys`, `CreateFlag`, and `FSBuilder`.
- Stream wrappers and primitives: `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `FSError`, `FSInputStream`, `FileAlreadyExistsException`, and `FileChecksum`.
- The main `FileContext` API range from construction and path resolution through create/open/mkdir/delete/rename, symlink handling, listing, ACLs, xattrs, snapshots, storage policies, builder-based open, path capabilities, server defaults, multipart upload creation, and public constants.
- `FileStatus`, including serialization/deprecation notes and file attribute flags.
- The beginning of `FileSystem`, including instance lookup/caching, URI canonicalization, delegation token hooks, block-location APIs, server defaults, path handles, open overloads, and create overloads through the abstract permission-bearing create method.

## Purpose

The chunk documents the public filesystem contract exported by Hadoop Common. The APIs provide the common layer used by HDFS, local filesystems, object-store connectors, view filesystems, and other `FileSystem` or `AbstractFileSystem` implementations.

At a high level, the chunk defines:

- Configuration keys that external deployments and connectors depend on.
- File metadata models (`ContentSummary`, `FileStatus`, `FileChecksum`).
- Stream and builder abstractions used for data reads/writes.
- Operation contracts for create, open, delete, rename, symlink, ACL, xattr, snapshot, storage policy, and capability discovery.
- Compatibility contracts such as deprecated overloads, default methods, `Writable` serialization, `Serializable`, and binary-compatible `compareTo(Object)`.

Because this is a generated API XML, the research value is in the public contract: which methods are abstract versus defaulted, what callers may rely on, what implementors must override, and which behaviors vary by backing filesystem.

## Important APIs And Types

### `CommonConfigurationKeysPublic`

The covered tail of this constants class exposes public keys and defaults for common Hadoop behavior. The class doc says it contains publicly documented configuration keys used by common code and that callers should generally use `CommonConfigurationKeys` rather than this class directly.

Notable constant families:

- TFile I/O and filesystem input/output buffer sizing.
- Caller context enablement, maximum context size, signature size, and separator.
- IPC client and server controls: max idle time, connect timeout, max retries, retry interval, socket-timeout retries, TCP no-delay, low latency, listen queue size, idle threshold, connection kill max, server reuse-address, max connections, slow RPC logging, purge interval, socket factory, SOCKS server, and server metrics update interval.
- Security group mapping and group cache controls, including positive/negative cache seconds, warning threshold, background reload, reload threads, and shell command timeout. Some older timeout constants are explicitly deprecated in favor of newer names.
- Authentication and authorization keys: security authentication, authorization, instrumentation admin requirement, service user name, auth-to-local rules and mechanism, DNS interface/nameserver, token file/env keys, HTTP authentication type, Kerberos relogin and keytab auto-renewal, RPC protection, SASL mechanism and callback/property resolver hooks.
- Crypto and key management: codec class prefixes for AES/SM4 CTR no-padding, cipher suite, JCE provider and auto-add flag, JCEKS serialization filter, crypto buffer size, impersonation provider, key provider path, default key bit length/cipher, KMS encrypted-key cache sizing, low watermark, refill threads, expiry, client timeout, and failover retry/sleep controls.
- Secure random configuration: Java secure random algorithm, implementation, OpenSSL engine ID, and random device path.
- Shell, HTTP, credentials, secret manager, sensitivity, tags, shutdown, Prometheus, idle timeout, and JMX NaN filtering controls.

These fields are dependency anchors for `core-default.xml`, security setup, RPC behavior, object store integrations, and operational observability.

### `ContentSummary`

`ContentSummary` extends `QuotaUsage` and implements `Writable`. It stores summary information for a file or directory, including content length, file count, directory count, quotas inherited from `QuotaUsage`, snapshot counts/space, and erasure coding policy.

Important APIs:

- Deprecated constructors remain for compatibility; docs direct newer code toward `ContentSummary.Builder`.
- Getters expose length, file count, directory count, snapshot length/file/directory counts, snapshot space consumed, and erasure coding policy.
- `write(DataOutput)` and `readFields(DataInput)` preserve Hadoop `Writable` serialization.
- `equals()` and `hashCode()` define value comparison behavior.
- Static header helpers return formatted field names for summary and quota output.
- Multiple `toString(...)` overloads format summary output with quota, human-readable, storage-type, and snapshot options.
- `toErasureCodingPolicy()` and `toSnapshot(boolean)` format EC policy and snapshot data.

The control-flow contract is mostly formatting selection: flags such as `qOption`, `hOption`, `tOption`, and `xOption` determine which counters and quota fields appear and whether byte counts are humanized.

### `CreateFileOptionKeys`

This interface defines standard `createFile()` builder option keys, especially for object stores and commit-style writes.

Important options:

- `FS_OPTION_CREATE_CONDITIONAL_OVERWRITE`: defers the overwrite/existence check until stream `close()` for implementations that manifest objects at close time. If passed as a mandatory option and supported/enabled, the filesystem must omit early overwrite checks and perform an atomic existence-check-and-create at close. Unsupported mandatory use must be rejected.
- `FS_OPTION_CREATE_CONDITIONAL_OVERWRITE_ETAG`: conditional overwrite based on a non-empty ETag string returned by an ETag source. Supported stores must compare the target object's ETag and reject missing or mismatched targets. The check/create may occur at `create()` or `close()`, but must be atomic.
- `FS_OPTION_CREATE_IN_CLOSE`: declares files or objects are created in `close()` rather than in `create()` or `createFile()`.
- `FS_OPTION_CREATE_CONTENT_TYPE`: supplies a content type/file type string.

The important integration point is capability discovery: supported features should be exported as path capabilities and stream capabilities so clients can decide whether optional or mandatory builder parameters are valid.

### `CreateFlag`

`CreateFlag` is the enum contract for file creation and append semantics. The documented combinations include:

- `CREATE`: create only if absent.
- `APPEND`: append only if present.
- `OVERWRITE`: truncate/overwrite existing file.
- `CREATE|APPEND`: create if absent, append if present.
- `CREATE|OVERWRITE`: create if absent, overwrite if present.
- `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK` as additional durability/storage/write-placement semantics.

Validation methods reject invalid combinations. The docs explicitly call out `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE` as invalid and describe `validateForAppend()` as requiring `APPEND` and prohibiting `OVERWRITE`.

### `FSBuilder<S,B>`

`FSBuilder` is the generic builder interface for filesystem and file-context operations. It separates optional parameters from mandatory parameters:

- `opt(...)` sets optional options that implementations may ignore.
- `must(...)` sets required options; if unsupported or unavailable, `build()` should fail with `IllegalArgumentException`.
- `optLong`, `optDouble`, `mustLong`, and `mustDouble` exist to avoid overload ambiguity and precision loss. The older float/double/long overloads have deprecation notes where values are converted in surprising ways.
- `build()` may throw `IllegalArgumentException`, `UnsupportedOperationException`, or `IOException`.

This is central to extensible APIs such as open/create builders where object stores and specialized filesystems need extra implementation-specific options without changing every public method signature.

### `FSDataInputStream` And `FSInputStream`

`FSInputStream` is the abstract seekable positioned-read base class. It extends `InputStream` and implements `Seekable` and `PositionedReadable`. It requires subclasses to implement `seek(long)`, `getPos()`, and `seekToNewSource(long)`, and provides positioned `read` and `readFully` helpers plus argument validation. `validatePositionedReadArgs()` rejects negative positions, invalid buffer regions, and other illegal arguments.

`FSDataInputStream` wraps an `FSInputStream` in `DataInputStream` and exposes a richer capability set:

- Seek and position APIs.
- Positioned byte-array reads and `readFully`.
- `ByteBufferReadable`, `ByteBufferPositionedReadable`, enhanced byte-buffer access with `ByteBufferPool`, and `releaseBuffer`.
- Readahead/drop-behind controls.
- `CanUnbuffer`, `StreamCapabilities`, and `IOStatisticsSource`.
- Vector-read controls: minimum seek, maximum read size, and `readVectored(...)` with allocator and optional release callback.

The stream delegates most behavior to its wrapped stream. That means correctness depends on the underlying filesystem stream implementing the optional interfaces it advertises. Unsupported operations may throw `UnsupportedOperationException`.

### `FSDataOutputStream` And `FSDataOutputStreamBuilder`

`FSDataOutputStream` wraps an `OutputStream` in `DataOutputStream` and implements `Syncable`, `CanSetDropBehind`, `StreamCapabilities`, `IOStatisticsSource`, and `Abortable`.

Important methods:

- `getPos()` returns current write offset.
- `close()` closes the underlying stream.
- `hflush()` and `hsync()` expose Hadoop write durability semantics.
- `setDropBehind(Boolean)` controls cache-dropping where supported.
- `getIOStatistics()` returns nested stream stats or empty stats.
- `abort()` delegates to the wrapped stream if it is `Abortable`, otherwise throws `UnsupportedOperationException`.

`FSDataOutputStreamBuilder` extends `AbstractFSBuilderImpl<S,B>` and accumulates create/append options for a `FileSystem` path:

- File parameters: permission, buffer size, replication, block size, checksum options.
- Operational controls: recursive parent creation, progress callback, create/overwrite/append flags.
- Generic `opt`/`must` parameters inherited from the builder contract.
- `build()` creates the stream and may fail with invalid parameters or filesystem I/O errors.

The builder defaults to not creating missing parent directories. `recursive()` is the explicit opt-in for parent creation.

### `FSError`, `FileAlreadyExistsException`, And `FileChecksum`

`FSError` is an `Error` used for unexpected filesystem failures presumed to reflect native disk errors. Its severity matters: callers should not treat it like normal `IOException` flow.

`FileAlreadyExistsException` is an `IOException` raised when a target already exists and overwrite is not configured.

`FileChecksum` is an abstract `Writable` with `getAlgorithmName()`, `getLength()`, `getBytes()`, optional `getChecksumOpt()`, and equality/hash behavior based on algorithm and bytes. Filesystems that do not implement checksums can return null from higher-level checksum APIs.

## `FileContext` API Surface

`FileContext` is a higher-level user API backed by `AbstractFileSystem`. It implements `PathCapabilities` and exposes operations using `Path`, `Options`, permissions, and richer exception contracts.

### Construction And Path Context

Factory methods create contexts from:

- A supplied `AbstractFileSystem` plus `Configuration`.
- Default configuration.
- Local filesystem defaults.
- A default `URI` with default or explicit configuration.

Context state includes the default filesystem, working directory, user identity (`UserGroupInformation`), and umask. `setWorkingDirectory()` explicitly does not follow symlinks when setting the working directory; it stores the supplied logical working directory behavior used to qualify relative paths. `makeQualified()` applies default filesystem and working directory rules.

### Core Operations

`FileContext` exposes create, builder-based create, mkdir, delete, open, truncate, setReplication, rename, permission/owner/time updates, checksum, checksum verification, status lookup, access checks, symlink status/target lookup, block locations, filesystem status, symlink creation, listings, delete-on-exit, and utility resolution helpers.

The API documents many filesystem-specific exception paths:

- `AccessControlException` for authorization failures.
- `FileAlreadyExistsException` for conflicting create/rename/symlink targets.
- `FileNotFoundException` for missing paths or missing parents.
- `ParentNotDirectoryException` for invalid parent path shape.
- `UnsupportedFileSystemException` for unsupported schemes.
- RPC-related client/server/unexpected server exceptions for remote implementations.
- `InvalidPathException` and argument exceptions for invalid paths or parameters.

Several methods describe implementation-dependent semantics. `rename()` explicitly notes atomicity depends on the filesystem. `truncate()` may return `false` when a background process must finish adjusting the last block before the file can be safely reused for updates.

### Symlink Semantics

The symlink documentation is unusually detailed and is a key behavioral contract:

- Symlink permissions are ignored; target permissions determine access.
- Intermediate symlinks are generally resolved transparently.
- Final-component symlinks are operated on directly by `delete`, `deleteOnExit`, `rename`, `getLinkTarget`, and `getFileLinkStatus`.
- `create()` and `mkdir()` expect a nonexistent final component; an existing symlink is treated like an existing file or directory.
- Most other methods follow the symlink.
- Symlink targets are stored as supplied when the filesystem can store fully qualified URIs.
- Dangling symlinks are permitted.
- Fully qualified, partially qualified, relative, and absolute targets resolve differently based on the target URI and the link path context.

These rules are integration-critical for view filesystems, local filesystems, HDFS, and any connector trying to emulate POSIX-like link behavior.

### ACLs, XAttrs, Snapshots, Storage Policies, And Capabilities

The ACL methods modify, remove, replace, and read ACL state. `setAcl()` must include base entries for user, group, and others for permission-bit compatibility. XAttr methods require names prefixed by namespace, such as `user.attr`, and only return attributes visible to the logged-in user.

Snapshot methods create default or named snapshots, rename snapshots, and delete snapshots. Storage policy methods satisfy, set, unset, query, and enumerate storage policies. These are optional or implementation-specific in many filesystems.

`openFile(Path)` returns a builder whose actual open occurs during `FSDataInputStreamBuilder.build()`. `hasPathCapability(Path, String)` delegates capability checks to the bound `AbstractFileSystem`. `getServerDefaults(Path)` fetches defaults based on a path, and `createMultipartUploader(Path)` returns a builder for multipart uploads.

### Public Constants

`FileContext` exposes `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`. `DEFAULT_PERM` remains for compatibility but docs direct users to separate directory and file defaults because older behavior could create files with execute permissions.

## `FileStatus`

`FileStatus` represents client-side file metadata. It implements `Writable`, `Comparable<Object>`, `Serializable`, and `ObjectInputValidation`.

Important state and APIs:

- Constructors cover minimal metadata, non-symlink filesystems, symlink-aware metadata, boolean attribute flags, explicit `Set<AttrFlags>`, and copy construction.
- `attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts booleans to flags such as ACL, encrypted, erasure-coded, and snapshot-enabled.
- Accessors expose length, file/directory/symlink kind, block size, replication, modification/access times, permissions, owner, group, path, symlink, ACL/encryption/EC/snapshot flags.
- Mutators exist for path, symlink, and protected permission/owner/group normalization.
- Equality, hash code, and compare order are based on path. `compareTo(Object)` was restored for binary compatibility.
- `readFields()` and `write()` are deprecated in favor of PBHelper/protobuf serialization directly, but remain in the API.
- `NONE` is a shared empty attribute set for the common no-attributes case.

The persistence contract is split: legacy Hadoop `Writable` remains available, while docs push new code toward protobuf conversion. Java serialization also invokes object validation.

## `FileSystem` API Surface In This Chunk

`FileSystem` is the older abstract filesystem facade. It extends `Configured` and implements `Closeable`, `DelegationTokenIssuer`, `PathCapabilities`, and `BulkDeleteSource`.

### Instance Lookup, Caching, And URI Identity

Static factory methods include:

- `get(URI, Configuration, String)` and `newInstance(URI, Configuration, String)` to execute under a named user through UGI.
- `get(Configuration)` and `get(URI, Configuration)` for default or explicit filesystem lookup.
- `newInstance(...)` variants that always return unique, newly initialized instances.
- `getLocal()` and `newInstanceLocal()` for local filesystems.
- `closeAll()` and `closeAllForUGI()` for cached instance cleanup.

The `get(URI, Configuration)` contract documents caching control through `fs.$SCHEME.impl.disable.cache`: when enabled, lookup returns a new initialized instance without caching; otherwise it reuses a matching cached instance or creates and caches a new one. This is a major state-management behavior and affects resource lifetime, authentication context, metrics, and test isolation.

URI APIs include `getDefaultUri`, `setDefaultUri`, `initialize`, `getScheme`, abstract `getUri`, `getCanonicalUri`, `canonicalizeUri`, `getDefaultPort`, `getFSofPath`, `checkPath`, and deprecated `getName`/`getNamed`. The canonicalization contract allows implementations to normalize hostnames and default ports.

### Tokens, Children, And Delegation

`getCanonicalServiceName()` returns the service name used by token caches, or null when no own token is available. The default behavior accounts for child filesystems. `getDelegationToken()`, `getChildFileSystems()`, and `getAdditionalTokenIssuers()` let complex filesystems contribute tokens from embedded or related filesystems.

### File Operations In This Range

The chunk covers:

- Static `create(FileSystem, Path, FsPermission)` and `mkdirs(FileSystem, Path, FsPermission)` helpers that set the exact requested permission rather than applying umask. The HDFS create helper is documented as two RPCs but thread-safe, chosen over mutating umask in configuration.
- `getFileBlockLocations(FileStatus, long, long)` and `getFileBlockLocations(Path, long, long)` with default localhost behavior and detailed HDFS replicated and erasure-coded examples.
- `getServerDefaults()` deprecated in favor of `getServerDefaults(Path)`.
- `resolvePath(Path)` through symlinks or mount points.
- Abstract `open(Path, int)`, convenience `open(Path)`, and PathHandle-based open overloads.
- `getPathHandle(FileStatus, HandleOpt...)` and protected `createPathHandle(...)` for durable serializable references with validation constraints.
- Multiple `create(...)` overloads that eventually lead toward the abstract permission-bearing create method. Defaults include overwriting files unless an overload says otherwise. Overloads add overwrite flag, progress callback, replication, buffer size, block size, and permission.

The final method in this chunk is abstract and is the core implementor hook for creating a file with explicit permission, overwrite behavior, buffer size, replication, block size, and progress reporting.

## Control Flow And Behavior

The XML does not expose method bodies, but the documented API flow is clear:

- Builder APIs collect options first, then perform validation and the filesystem operation in `build()`. This makes failure timing different from immediate APIs: mandatory unsupported options, path existence checks, and I/O failures may occur at build time.
- `FileContext.create(Path, EnumSet<CreateFlag>, CreateOpts...)` validates create flags and options, resolves the target filesystem through `AbstractFileSystem`, applies umask/permissions and server defaults, and returns an `FSDataOutputStream`.
- `FileSystem.create(...)` overloads form a convenience cascade toward the abstract full-parameter create method implemented by concrete filesystems.
- Stream wrappers delegate optional behavior to wrapped streams. Capability checks and `UnsupportedOperationException` are part of normal control flow for optional interfaces.
- Path resolution distinguishes relative, absolute, slash-relative, fully qualified, symlink, and mount-point paths. `FileContext` keeps working-directory behavior as path-prefix logic rather than inode-like process state.
- Access checks are explicitly vulnerable to time-of-check/time-of-use races; docs recommend performing real filesystem actions as the desired `UserGroupInformation` instead of relying on prior access checks.
- Filesystem lookup may return cached or new instances depending on configuration, and closing cached instances invalidates them for future operations.

## State And Persistence Behavior

Important stateful behavior in this range:

- Configuration constants define process and cluster behavior for IPC, security, crypto, credential lookup, metrics, and HTTP endpoints.
- `FileSystem` maintains cached instances keyed by URI/user/config-derived identity unless caching is disabled per scheme.
- `FileContext` stores default filesystem, working directory, UGI, and umask.
- `ContentSummary`, `FileStatus`, and `FileChecksum` are metadata snapshots. Some are writable/serializable for RPC, IPC, or persistence compatibility.
- `FSDataInputStream` and `FSDataOutputStream` hold nested stream state, current positions, optional buffers, IO statistics, and capability-dependent behavior.
- `FSDataOutputStream.close()` may be the point where object-store creation is finalized for create-in-close or conditional overwrite modes.
- `deleteOnExit()` registers paths for JVM shutdown cleanup; `SHUTDOWN_HOOK_PRIORITY` controls FileContext cleanup ordering.
- ACLs, xattrs, snapshots, storage policies, owner/group/permission/time changes, replication, truncate, and create/delete/rename operations mutate persistent filesystem namespace or metadata.
- Path handles are durable serializable references whose validity depends on constraints chosen at creation time and enforcement by the filesystem.

## Dependencies And Integration Points

The chunk sits in `org.apache.hadoop.fs` but connects to many Hadoop Common modules:

- `org.apache.hadoop.conf.Configuration` and `Configured` for filesystem configuration.
- `Path`, `PathHandle`, `BlockLocation`, `FsStatus`, `FsServerDefaults`, `Options`, `StorageType`, `BlockStoragePolicySpi`, `MultipartUploaderBuilder`, and related fs model types.
- `FsPermission`, `FsAction`, `AclEntry`, and `AclStatus` for permissions and ACLs.
- `UserGroupInformation`, `AccessControlException`, `Credentials`, and `Token` for security and delegation token integration.
- `Progressable` for write progress callbacks.
- `ByteBufferPool`, `Writable`, and protobuf helper paths for serialization and buffer management.
- `IOStatistics` and `IOStatisticsSource` for stream/filesystem metrics.
- RPC exception types documented for remote filesystems.
- `StreamCapabilities` and `PathCapabilities` for optional feature discovery.
- Object-store connectors through create-in-close, conditional overwrite, ETag, multipart upload, content type, and mandatory/optional builder options.

Concrete implementors must align these contracts with HDFS, local filesystem, object stores, view/mount filesystems, and any custom scheme registered in configuration.

## Risks And Edge Cases

- The source is a public API XML, not implementation code; implementation details must be confirmed in Java sources before changing behavior.
- Public constants are compatibility-sensitive. Renaming, removing, or changing defaults can break deployed clusters and external connectors.
- Builder overloads for numeric values have historical ambiguity and precision-loss deprecations. New code should use explicit `optLong`, `optDouble`, `mustLong`, and `mustDouble`.
- Mandatory builder options must be rejected when unsupported. Silently ignoring `must()` options can corrupt commit protocols, especially conditional object-store writes.
- Conditional overwrite and ETag create options require atomic check-and-create behavior. Object stores with weak or emulated atomicity need careful documentation and tests.
- `APPEND`, `OVERWRITE`, and `CREATE` flag combinations are easy to misuse; invalid combinations must be rejected consistently across builders and classic APIs.
- `access()` checks are vulnerable to TOCTOU races and may not reflect ACL-rich authorization models unless overridden.
- `rename()` atomicity is filesystem-dependent; callers cannot assume POSIX atomic rename across all Hadoop filesystems.
- `truncate()` may complete asynchronously, signaled by a `false` return value. Callers that append or rewrite immediately must handle this.
- Symlink resolution has many path-form cases. Incorrect handling of final-component versus intermediate symlinks can break compatibility or create security bugs.
- FileSystem caching can leak resources or cross-contaminate tests if not closed or disabled deliberately.
- `FileStatus.equals()` and `hashCode()` are path-based, not full metadata-based. Using `FileStatus` as a cache key can miss metadata changes.
- Legacy `Writable` serialization remains present but deprecated for some types; mixed-version clients may still depend on it.
- Stream capability methods depend on the nested stream honestly implementing optional interfaces. Incorrect capability reporting leads to runtime `UnsupportedOperationException` or data-path failures.

## Test Signals

Useful tests for changes touching APIs in this chunk include:

- API compatibility checks against this jdiff surface, especially method signatures, visibility, exceptions, and deprecation annotations.
- Unit tests for `CreateFlag.validate()` and `validateForAppend()` covering all documented valid and invalid combinations.
- Builder tests proving `opt()` options may be ignored but `must()` unsupported options fail during `build()`.
- Tests for numeric builder overloads that verify long/double values are preserved through `optLong`, `optDouble`, `mustLong`, and `mustDouble`.
- Filesystem contract tests for create overwrite/non-overwrite, create parent behavior, append, recursive parent creation, progress callback tolerance, and checksum options.
- Object-store contract tests for create-in-close, conditional overwrite, ETag matching/mismatching/missing target, stream/path capability advertisement, and atomic close behavior.
- Stream tests for seek, positioned reads, byte-buffer reads, vectored reads, unbuffer, drop-behind, readahead, hflush/hsync, abort, and IO statistics fallback.
- `FileContext` contract tests for working directory qualification, default URI behavior, symlink resolution forms, final symlink operations, dangling symlinks, and mount-point resolution.
- Authorization tests for `access()`, ACL mutation, xattr visibility by user, and permission/owner/group update behavior.
- Snapshot and storage policy tests on filesystems that support those features, plus unsupported-operation behavior on filesystems that do not.
- `FileSystem` cache tests for default cached lookup, per-scheme cache disablement, `newInstance()` uniqueness, `closeAll()`, and `closeAllForUGI()`.
- Serialization tests for `ContentSummary`, `FileStatus`, and `FileChecksum`, including deprecated `Writable` paths where compatibility is still required.
- Block-location tests for local default behavior, HDFS replicated files, and erasure-coded files where logical block groups differ from replicated block layout.

### subset-b-007234: lines 12224-18113

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 12224-18113

## Scope

This chunk is part 3 of the JDiff XML API description for Hadoop Common 3.5.0. It starts in the documentation body for `org.apache.hadoop.fs.FileSystem.create(Path, FsPermission, boolean, int, short, long, Progressable)`, continues through the remainder of `FileSystem`, and then covers complete API entries for `FileUtil`, `FilterFileSystem`, `FsConstants`, `FsServerDefaults`, `FsStatus`, `FutureDataInputStreamBuilder`, `GlobFilter`, `GlobalStorageStatistics`, `InvalidPathException`, `InvalidPathHandleException`, `LocalFileSystem`, `LocatedFileStatus`, `MultipartUploader`, `OpenFileOptions`, `Options`, `ParentNotDirectoryException`, `PartHandle`, and `PartialListing`. It ends inside the deprecated `Path.makeQualified(FileSystem)` method documentation, with the rest of `Path` continuing in the next chunk.

The source is generated API metadata rather than executable implementation. It records public/protected signatures, inheritance, exceptions, visibility, abstract/default status, deprecation notes, fields, and Javadocs. Research here therefore focuses on public API contracts, implementation obligations for Hadoop filesystem providers, and behavior exposed to callers.

## Purpose

The chunk documents the central Hadoop filesystem API layer. The `FileSystem` tail defines the user-facing and implementation-facing contract for creation, append, rename, delete, listing, status lookup, local copy helpers, working directories, checksum and symlink handling, ACL/xattr/snapshot/storage-policy APIs, path capabilities, stream builders, async open, multipart upload creation, and bulk delete creation. The later classes define utility and wrapper APIs around those operations, local filesystem behavior, serializable filesystem metadata, async/multipart option constants, path/listing exceptions, and path-construction behavior.

This section is especially important for compatibility because `FileSystem` is a base class used by HDFS, `LocalFileSystem`, `FilterFileSystem`, object-store connectors, view filesystems, and third-party filesystems. Its class documentation warns that new public/protected APIs must be mirrored or consciously blocked by wrappers such as `FilterFileSystem` and tested by compatibility tests such as `TestFilterFileSystem.MustNotImplement`.

## Important APIs And Types

### `FileSystem` tail

The chunk contains the remainder of `FileSystem` beginning with create overloads:

- `create(...)` overloads accept `Path`, optional `FsPermission`, overwrite booleans or `EnumSet<CreateFlag>`, buffer size, replication, block size, `Progressable`, and optional `Options.ChecksumOpt`.
- `primitiveCreate(...)` and `primitiveMkdir(...)` are protected transition hooks used by `FileContext` after applying umask-derived absolute permissions.
- `createNonRecursive(...)` variants create without making missing parents.
- `createNewFile(Path)` creates a zero-length file but documents that the default implementation is not atomic.
- `append(...)` variants support optional buffer size, progress callback, and `appendToNewBlock`; append is optional and may throw `UnsupportedOperationException`.
- `concat(Path, Path[])`, `setReplication(Path, short)`, abstract `rename(Path, Path)`, protected option-bearing `rename(Path, Path, Options.Rename...)`, `truncate(Path, long)`, and `delete(Path, boolean)` define core mutating operations. Rename atomicity is implementation-dependent, and the protected option-bearing rename default is explicitly non-atomic.
- Status and listing APIs include `exists`, deprecated `isDirectory`/`isFile`, deprecated `getLength`, `getContentSummary`, `getQuotaUsage`, quota setters, `listStatus`, `listStatusBatch`, `listCorruptFileBlocks`, `globStatus`, `listLocatedStatus`, `listStatusIterator`, and recursive `listFiles`.
- Path context APIs include `getHomeDirectory`, `setWorkingDirectory`, `getWorkingDirectory`, `getInitialWorkingDirectory`, and `fixRelativePart`.
- Local transfer APIs include `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, `moveToLocalFile`, `startLocalOutput`, and `completeLocalOutput`.
- Filesystem metadata APIs include `getUsed`, `getBlockSize`, `getDefaultBlockSize`, `getDefaultReplication`, abstract `getFileStatus`, `msync`, `access`, `getStatus`, and `getStatus(Path)`.
- Symlink/checksum APIs include `createSymlink`, `getFileLinkStatus`, `supportsSymlinks`, `getLinkTarget`, `resolveLink`, `getFileChecksum(Path)`, `getFileChecksum(Path,long)`, `setVerifyChecksum`, and `setWriteChecksum`.
- Security and metadata mutation APIs include `setPermission`, `setOwner`, `setTimes`, snapshot create/rename/delete, ACL mutation and lookup, xattr mutation and lookup, storage-policy APIs, trash root lookup, and path capability probing.
- Static/global APIs include `getFileSystemClass`, `getStatistics` overloads, `getAllStatistics`, `clearStatistics`, `printStatistics`, `areSymlinksEnabled`, `enableSymlinks`, `getStorageStatistics`, and `getGlobalStorageStatistics`.
- Builder/newer APIs include `createDataOutputStreamBuilder`, `createFile`, `appendFile`, `openFile(Path)`, `openFile(PathHandle)`, protected `openFileWithOptions(...)` for `Path` and `PathHandle`, `createDataInputStreamBuilder`, `getEnclosingRoot`, `createMultipartUploader`, and `createBulkDelete`.

Important fields in this tail are public constants `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and protected instance `statistics`. `LOG` is explicitly called out as widely used in Hadoop FS code and tests and must be changed with care.

### `FileUtil`

`FileUtil` is a static utility collection for local files, Hadoop `FileSystem` paths, archives, permissions, process classpaths, and small write helpers. Important APIs include:

- `stat2Paths(...)` converts `FileStatus[]` to `Path[]`, with an overload that returns a default path when statuses are null.
- Recursive local deletion helpers `fullyDeleteOnExit`, `fullyDelete(File)`, `fullyDelete(File, boolean)`, `fullyDeleteContents(...)`, and deprecated `fullyDelete(FileSystem, Path)`. The docs distinguish regular files, symlinks to files, symlinks to directories, and recursive directory deletion; partial deletion is possible when false is returned.
- `readLink(File)` reports symlink targets or an empty string on errors/non-links.
- `copy(...)` overloads copy between filesystems, from local files into filesystems, and from filesystems to local files. The recursive copy contract warns that when `deleteSource` is true, source directories may be partially deleted if the operation fails mid-tree.
- Local file and shell helpers include `isRegularFile`, `makeShellPath`, `makeSecureShellPath`, `getDU`, `symLink`, `chmod`, `setOwner`, `setReadable`, `setWritable`, `setExecutable`, `canRead`, `canWrite`, `canExecute`, and `setPermission`.
- Archive helpers `unZip(...)` and `unTar(...)` accept streams/files and target directories; untar may throw `InterruptedException` and `ExecutionException` for command/task failures.
- `createLocalTempFile` creates a temp file adjacent to a base file and optionally registers delete-on-exit.
- `replaceFile`, safe `listFiles(File)`, and safe `list(File)` wrap fragile `java.io.File` APIs so callers get exceptions rather than nulls.
- `createJarWithClassPath(...)` builds a manifest-only classpath jar and expands environment variables and wildcard jar entries; this is primarily for platform command-line length limits.
- `getJarsInDirectory(...)`, `compareFs`, eight `write(...)` overloads for `FileSystem`/`FileContext`, byte arrays, lines, char sequences, charset/UTF-8, `rename`, `maybeIgnoreMissingDirectory`, and `checkFSSupportsEC`.

The `SYMLINK_NO_PRIVILEGE` constant is exposed for symlink creation results.

### `FilterFileSystem`

`FilterFileSystem` extends `FileSystem` and wraps another `FileSystem` in protected field `fs`, with optional protected `swapScheme`. The class doc says it passes all requests to the contained filesystem unless subclasses override behavior. The chunk lists pass-through implementations for initialization, URI/canonical URI handling, path qualification, path checking, block locations, path resolution, open/create/append/concat, path handles, listing, delete, rename, truncate, copy, status/defaults, symlink/checksum behavior, metadata mutation, ACL/xattr/snapshot/storage-policy APIs, builder APIs, async open, enclosing root, and path capability probing.

This wrapper is a major integration point. Any new `FileSystem` API must be considered for pass-through, explicit unsupported behavior, and capability reporting. The `FileSystem` class doc in this chunk specifically warns that `FilterFileSystem#hasPathCapability(Path, String)` must return false for newly probed capabilities unless the wrapper truly supports them.

### Filesystem constants and serializable metadata

`FsConstants` exposes constants for local, FTP, and viewfs schemes, maximum symlink path links, and the viewfs-overload target implementation pattern.

`FsServerDefaults` implements `Writable` and transports server-provided defaults to clients. It has constructors for block size, bytes per checksum, write packet size, replication, file buffer size, encrypted transfer, trash interval, checksum type, key provider URI, default storage policy id, and snapshot-trash-root enablement. Getters expose each value, and `write(DataOutput)`/`readFields(DataInput)` define Hadoop serialization.

`FsStatus` also implements `Writable` and stores filesystem capacity, used bytes, and remaining bytes, with getters plus `write`/`readFields`.

`LocatedFileStatus` extends `FileStatus` and adds `BlockLocation[]`. Constructors wrap an existing `FileStatus` or build full file metadata with block locations. `getBlockLocations`, `setBlockLocations`, `compareTo`, `equals`, and `hashCode` define how block locality participates in status objects.

`PartialListing<T>` represents one batch of a listing. It stores the listed `Path` and either a `List<T>` result or a `RemoteException`; `get()` behaves like a future by returning the list or throwing the recorded exception.

### Async open, multipart upload, and option constants

`FutureDataInputStreamBuilder` extends `FSBuilder<CompletableFuture<FSDataInputStream>, FutureDataInputStreamBuilder>`. `build()` returns a `CompletableFuture` and may throw argument, unsupported, or I/O errors before or while constructing the future. `withFileStatus(FileStatus)` is optional advisory input that implementations may use or ignore. Its docs explain the `opt` versus `must` builder contract: optional unknown options may be ignored; mandatory unknown/unsupported options must trigger `IllegalArgumentException`.

`MultipartUploader` is an async interface for object-store-style multipart writes. It exposes:

- `startUpload(Path)` returning `CompletableFuture<UploadHandle>`.
- `putPart(Path, InputStream, int partNumber, UploadHandle, long length)` returning `CompletableFuture<PartHandle>`.
- `complete(Path, Map<Integer, PartHandle>, UploadHandle)` returning `CompletableFuture<PathHandle>`.
- `abort(Path, UploadHandle)` returning `CompletableFuture<Void>`.
- `abortUploadsUnderPath(Path)` returning `CompletableFuture<Integer>` and warning that stores may leave partial uploads after application failure; callers should expect eventual cleanup.

`PartHandle` is a serializable opaque multipart part identifier. It provides default `toByteArray()`, abstract `bytes()`, and abstract `equals(Object)`.

`OpenFileOptions` defines standard option keys for `openFile()` and related builders: file length, split start/end, buffer size, footer cache, read policy, standard-option set, read policy values for adaptive, Avro, columnar, CSV, default, HBase, JSON, ORC, Parquet, random, sequential, vector, whole-file, the set of all read policies, and the EC policy option.

`Options` is a final public namespace class for filesystem operation options. Nested types are not in this chunk, but many APIs in this chunk refer to `Options.Rename`, `Options.ChecksumOpt`, `Options.HandleOpt`, and `Options.OpenFileOptions`.

### Filters, statistics, exceptions, local filesystem, and path prefix

`GlobFilter` implements `PathFilter` for POSIX glob patterns with brace expansion and optional user-supplied filter. Constructors throw `IOException` for invalid patterns; `hasPattern()` reports whether the input contained glob syntax; `accept(Path)` applies the filter.

`GlobalStorageStatistics` is modeled as a final enum and stores global `StorageStatistics` instances. `get`, `put`, `reset`, and `iterator` are synchronized. `put` creates or returns statistics by name through a provider and may throw runtime exceptions if the provider returns null or a statistic with the wrong name.

`InvalidPathException` extends `HadoopIllegalArgumentException` for invalid path strings or filesystem-specific invalidity. `InvalidPathHandleException` extends `IOException` for `PathHandle` constraints that no longer hold. `ParentNotDirectoryException` extends `IOException` when a specified parent is not a directory.

`LocalFileSystem` extends `ChecksumFileSystem`. The API exposes initialization, `file` scheme reporting, raw filesystem access, `pathToFile(Path)`, copy-to/from-local behavior, checksum failure reporting, symlink support, symlink creation, link status, and link target lookup.

The chunk begins `Path`, which implements `Comparable<Path>`, `Serializable`, and `ObjectInputValidation`. It includes constructors from parent/child strings and paths, raw strings, URIs, and scheme/authority/path components. Static helpers strip scheme/authority, merge paths while preserving the first path's scheme/authority, and detect Windows absolute path strings. Instance methods in this chunk cover `toUri`, resolving a `FileSystem` from configuration, absolute/root/name/parent checks, optional parent lookup, suffixing, `toString`, equality, hash, comparison, depth, and the deprecated `makeQualified(FileSystem)` signature whose documentation continues past this chunk boundary.

## Control Flow And Behavioral Contracts

Most control flow is described as delegation, default implementation, or implementation responsibility:

- `FileSystem` overloads normalize caller convenience into lower-level operations: create variants funnel toward permission/create-flag/checksum-aware creation; append overloads add default buffer/progress/new-block options; deprecated status helpers are wrappers around `getFileStatus`; listing APIs either materialize arrays or return `RemoteIterator`/partial batches.
- `FileSystem` mutators intentionally expose weaker, implementation-dependent guarantees. `rename` and `createNewFile` default implementations are not necessarily atomic; append and truncate may be unsupported or asynchronous; set-replication may return success even on filesystems that do not implement replication.
- `deleteOnExit`, `cancelDeleteOnExit`, and `processDeleteOnExit` provide VM-lifetime cleanup flow. These APIs are stateful, and cleanup runs later against queued paths.
- `FileUtil.copy` recursively walks/copies source trees, optionally deleting source items as it progresses. Failure after partial progress can leave both source and destination in mixed states.
- `FilterFileSystem` control flow is wrapper delegation: most calls are forwarded to `fs`, with path/URI scheme adaptation available via `swapScheme`.
- `FutureDataInputStreamBuilder` and multipart upload APIs are asynchronous control-flow contracts. Some validation may fail immediately, while actual stream creation/upload completion is represented by `CompletableFuture`.
- `PartialListing.get()` defers remote listing failure until the consumer asks for the batch result.
- `GlobalStorageStatistics` serializes access to the global registry with synchronized methods.
- `Path` construction and helper methods normalize URI/path representations and compare paths by their string/URI identity.

## State And Persistence Behavior

The visible state contracts include:

- `FileSystem.statistics` and static/global statistics registries persist counters across filesystem operations and tests. Static `getStatistics`, `clearStatistics`, and `printStatistics` operate on shared state.
- `FileSystem` tracks working directory state per instance. Relative paths are resolved against that state through qualification/fixup helpers.
- `deleteOnExit` registers paths for later deletion and must coordinate with shutdown hooks (`SHUTDOWN_HOOK_PRIORITY` is public).
- `setVerifyChecksum` and `setWriteChecksum` toggle per-filesystem checksum behavior where implementations honor them.
- `FsServerDefaults`, `FsStatus`, and `LocatedFileStatus` are metadata value objects with Hadoop `Writable` or inherited serialization semantics. Changing field order or serialization would break wire/storage compatibility.
- `MultipartUploader` persists upload sessions externally in backing stores through `UploadHandle` and `PartHandle`. The docs explicitly warn that partial uploads may remain after application failure and may require cleanup.
- `PartHandle` byte serialization is opaque; callers must not interpret it beyond equality/round-trip use.
- `OpenFileOptions` constants are persistent API strings used in builder parameter maps and path capability discovery.
- `GlobalStorageStatistics` keeps JVM-global named statistics and must guard consistency when providers create entries.
- `Path` is serializable and validates deserialized objects via `ObjectInputValidation` in later `Path` methods outside this chunk; this chunk already establishes the serializable path object surface.

## Dependencies And Integration Points

This chunk depends heavily on Hadoop common types:

- Filesystem model: `Path`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `ContentSummary`, `QuotaUsage`, `FsStatus`, `FsServerDefaults`, `BlockStoragePolicySpi`, `PathHandle`, `UploadHandle`, `PartHandle`, `BulkDelete`, and builders.
- Permissions/security: `FsPermission`, `AclEntry`, `AclStatus`, `FsAction`, `AccessControlException`, owner/group strings, and xattr flags.
- I/O and serialization: `FSDataInputStream`, `FSDataOutputStream`, `DataInput`, `DataOutput`, `Writable`, `InputStream`, `RemoteIterator`, `CompletableFuture`, and `Progressable`.
- Configuration and runtime: `Configuration`, `URI`, `UserGroupInformation`-related context from adjacent APIs, `DataChecksum.Type`, SLF4J logging, and Java local file APIs.
- Wrapper and compatibility layers: `FileContext`, `AbstractFileSystem`, `ChecksumFileSystem`, `FilterFileSystem`, `LocalFileSystem`, HDFS, object-store connectors, viewfs, and third-party filesystem implementations.

Key integration points are capability probing (`hasPathCapability`, builder `must` options, `checkFSSupportsEC`), wrapper propagation (`FilterFileSystem`), object store semantics (`CreateFileOptionKeys` from the previous chunk plus multipart/open-file options here), and compatibility with external projects called out in the `FileSystem` docs such as HBase and Hive shims.

## Risks And Edge Cases

- The chunk starts and ends mid-API documentation. Merge must join this with adjacent chunk reports for complete `FileSystem.create(...)` and `Path.makeQualified(...)` docs.
- JDiff XML may include generated or misspelled parameter names, such as `FilterFileSystem.primitiveMkdir` showing `abdolutePermission`; research consumers should treat it as API metadata evidence, not source-of-truth implementation spelling without checking Java source.
- `FileSystem` API changes can break wrappers. `FilterFileSystem`, `ChecksumFileSystem`, HAR tests, and downstream shims must be updated when new methods or capabilities are introduced.
- Several operations return booleans rather than throwing for all failures (`delete`, `rename`, `setReplication`, copy helpers), creating ambiguity between unsupported, absent, and partial-success states.
- Non-atomic defaults for `createNewFile` and option-bearing `rename` can surprise callers expecting POSIX/HDFS semantics.
- Recursive delete/copy utilities can leave partial state on failure, especially with `deleteSource=true`, permission adjustment, or symlink handling.
- Symlink handling is security-sensitive. `FileUtil` distinguishes deleting symlinks from deleting targets for `fullyDelete`, but `fullyDeleteContents` follows symlinks to directories and deletes target contents.
- Archive extraction helpers (`unZip`, `unTar`) and shell helpers (`symLink`, `chmod`, `setOwner`, shell path construction) carry platform, permission, subprocess, and path-injection risks; `makeSecureShellPath` exists to reduce script injection risk.
- Async builders and multipart uploads split validation/completion timing across immediate exceptions and future failures. Partial uploads can leak storage if abort/cleanup is not called after failures.
- `OpenFileOptions` strings are public compatibility surface. Renaming or changing accepted values would break clients that pass options through generic builders.
- `GlobalStorageStatistics` is synchronized but JVM-global; tests must clear/reset state to avoid cross-test interference.
- `Path` constructors and Windows path detection are portability-sensitive, especially around URI scheme/authority, relative paths, and drive-letter interpretation.

## Test Signals

Useful tests and validation signals for this API area include:

- JDiff/API compatibility checks should detect signature, visibility, exception, deprecation, and constant changes in this XML.
- `FileSystem` contract tests should cover create/createNonRecursive/primitiveCreate permission semantics, append support flags, rename overwrite behavior and atomicity claims, delete return values, truncate completion behavior, listing/glob/status behavior, checksum toggles, symlink support, ACL/xattr/storage-policy support, and path capability reporting.
- Wrapper tests should assert `FilterFileSystem` delegates every supported `FileSystem` method and deliberately returns false/unsupported for unimplemented capabilities. The class doc explicitly references `TestFilterFileSystem.MustNotImplement`.
- Local filesystem tests should cover `LocalFileSystem` scheme, raw filesystem conversion, symlink behavior, checksum failure reporting, and local copy direction semantics.
- `FileUtil` tests should exercise symlink deletion versus target deletion, partial recursive copy/delete failure behavior, permission fallback, archive extraction, classpath jar creation with wildcards/environment variables, safe list wrappers, and `maybeIgnoreMissingDirectory` behavior for inconsistent listings.
- Serialization round-trip tests are needed for `FsServerDefaults`, `FsStatus`, `LocatedFileStatus`, `PartHandle` implementations, and adjacent `Path` serialization validation.
- Async builder tests should distinguish optional and mandatory options, immediate validation exceptions, future-completion exceptions, `withFileStatus` advisory behavior, and `OpenFileOptions` read-policy handling.
- Multipart uploader tests should cover start/put/complete/abort flow, part-number ordering, invalid handle failures, cleanup under a path, and leaked multipart state after simulated application failure.
- Statistics tests should verify per-filesystem statistics, global storage statistics registration/reset/iteration, and no cross-test state bleed after `clearStatistics`/`reset`.

### subset-b-007235: lines 18114-24626

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 18114-24626

## Scope

This chunk is part of the Hadoop Common 3.5.0 JDiff API snapshot. It is XML metadata for public and protected Java API surface, not executable implementation code. The range starts inside `org.apache.hadoop.fs.Path` and continues through multiple `org.apache.hadoop.fs.*` packages, ending in the opening constructor documentation for `org.apache.hadoop.fs.viewfs.ViewFileSystem`. The merge lane should treat `Path` and `ViewFileSystem` as cross-chunk continuations.

## Purpose

The chunk documents Hadoop filesystem API contracts around paths, positioned reads, quota reporting, local and FTP filesystem implementations, stream capability probing, trash policy abstraction, ACL/permission modeling, IO statistics, object-store metric names, and initial ViewFS mountpoint support. It is primarily a compatibility contract: downstream users and filesystem implementations rely on these declarations to know method signatures, checked exceptions, deprecation status, stable string formats, and behavioral notes.

## Important APIs And Types

`org.apache.hadoop.fs.Path` appears at the chunk boundary with `makeQualified(URI, Path)`, deprecated `makeQualified(FileSystem)`, `validateObject()`, and separator/current-directory constants. The documented contract is path qualification against a default URI and working directory, plus deserialization validation to reject malicious object streams without a URI.

`PathFilter`, `PathHandle`, `UploadHandle`, `Seekable`, and `PositionedReadable` define small but central extension points. `PathFilter.accept(Path)` is the path-list inclusion predicate. `PathHandle` and `UploadHandle` are opaque serializable references backed by `ByteBuffer`/byte arrays and equality semantics. `Seekable` exposes `seek`, `getPos`, and `seekToNewSource`. `PositionedReadable` defines thread-safe positional reads, `readFully` variants, vectored read defaults, and vector tuning hooks `minSeekForVectorReads()` and `maxReadSizeForVectorReads()`.

`QuotaUsage` models directory quota state: file/directory count, namespace quota, space consumed, space quota, per-`StorageType` quotas and consumption, output header/string formatting, equality, and protected setters/building hooks. `StorageType` enumerates storage media behavior with helpers for transient/RAM/movable/quota-support classification, parsing from strings/ints, same-disk tiering policy, and configuration-key lookup.

`RawLocalFileSystem` is the public local filesystem implementation over `java.io.File`. The chunk lists URI initialization, `pathToFile`, `open` by path and path handle, `append`, multiple `create`/`createNonRecursive` overloads, output-stream creation hooks, `concat`, `rename`, Windows empty-destination-directory handling, `truncate`, `delete`, `listStatus`, `exists`, directory creation helpers, working/home directory methods, local-output staging, status, ownership/permission/time mutation, path-handle creation, symlink methods, and `hasPathCapability`.

Read/write capability and durability APIs include `ReadOption`, nested `Options.Rename`, `SafeModeAction`, `StreamCapabilities`, `StreamCapabilitiesPolicy`, nested `StreamCapability`, and `Syncable`. Capability strings cover `hflush`, `hsync`, readahead, drop-behind, unbuffer, ByteBuffer reads, positioned ByteBuffer reads, IOStatistics, vectored IO, sliced vectored buffers, abortable streams, and thread-level IOStatistics context.

`Trash` and abstract `TrashPolicy` define delete-to-trash behavior. `Trash` is a configured facade with constructors from `Configuration` or `FileSystem`, static `moveToAppropriateTrash`, `moveToTrash`, checkpointing, expunge operations, immediate expunge, current trash directory lookup, and an emptier runnable. `TrashPolicy` supplies initialization, enablement, move/checkpoint/delete operations, emptier creation, current-trash-dir lookup, factory methods, and protected state fields `fs`, `trash`, and `deletionInterval`. Older home-directory initialization and factory overloads are deprecated.

`XAttrCodec` and `XAttrSetFlag` cover extended attribute shell/API value encoding and flag validation. `XAttrCodec.decodeValue` accepts hex (`0x`/`0X`), base64 (`0s`/`0S`), quoted text, or plain text; `encodeValue` returns text/hex/base64 string forms. `XAttrSetFlag.validate` checks create/replace flag compatibility against existing xattrs.

`org.apache.hadoop.fs.audit.CommonAuditContext` provides thread-local and global audit metadata. It supports static current context lookup, process/thread identifiers, entry-point recording, global context put/get/remove/iteration, per-thread put/remove/get/reset/contains, and delayed `Supplier<String>` values. The docs explicitly warn that long-lived suppliers must not retain large object graphs.

`org.apache.hadoop.fs.ftp.FTPFileSystem` is a `FileSystem` backed by Apache Commons Net. It exposes `ftp` scheme/default port, URI initialization, open/create/delete/list/status/mkdirs/rename/working-directory/home-directory APIs, and public FTP configuration constants for host, port, user, password, data connection mode, transfer mode, timeout, buffer/block size, and same-directory rename restrictions. `FTPException` wraps checked or unchecked causes as a runtime exception.

`org.apache.hadoop.fs.impl.AbstractFSBuilderImpl`, `FutureDataInputStreamBuilderImpl`, and `MultipartUploaderBuilderImpl` are implementation-support classes for filesystem builders. They track either a `Path` or a `PathHandle`, mutable option `Configuration`, mandatory and optional key sets, fluent typed `opt`/`must` setters, and rejection of unknown mandatory keys. The future input-stream builder returns `CompletableFuture<FSDataInputStream>` and carries buffer size and optional `FileStatus`; the multipart builder carries permission, buffer size, replication, block size, create/overwrite/append flags, and checksum options.

`org.apache.hadoop.fs.impl.prefetch.Kind`, `State`, and `org.apache.hadoop.fs.store.DestState` expose nested implementation enum values for block operations, buffer state, and data block destination state. Their package docs mark these areas as object-store/internal support with no stability guarantees.

`org.apache.hadoop.fs.permission` provides ACL and permission models. `AclEntry` is immutable with type/name/permission/scope accessors, stable string formatting, ACL spec parsing, single-entry parsing, and list-to-string conversion. `AclEntryScope` and `AclEntryType` are enums with stable string forms. `AclStatus` exposes owner, group, sticky bit, ACL entries, base permission, and effective permission calculations, including a compatibility overload for old NameNodes. `FsAction` supports permission implication and boolean algebra. `FsCreateModes` stores masked and unmasked creation modes. `FsPermission` implements `Writable`, `Serializable`, and `ObjectInputValidation`; it constructs permissions from actions, shorts, ints, strings, or copies, serializes/deserializes with `DataInput/DataOutput`, applies/get/sets umask, exposes default directory/file/cache-pool permissions, parses Unix symbolic strings, and validates deserialized objects. Deprecated ACL/encryption/EC bits are documented as moving to `FileStatus`.

`org.apache.hadoop.fs.statistics` is a public statistics surface. `IOStatistics` exposes counters, gauges, minimums, maximums, and mean statistics maps, plus unset sentinel values. `IOStatisticsAggregator` merges statistics. `IOStatisticsSetters` sets values. `IOStatisticsSnapshot` is synchronized for clear/snapshot/aggregate/map reads/setters, serializable, JSON-friendly, and exposes secure deserialization class lists. `IOStatisticsSupport` retrieves/snapshots stats and returns no-op duration trackers. `IOStatisticsLogging` stringifies and logs statistics robustly and lazily. `DurationStatisticSummary` extracts success/failure duration summaries. `MeanStatistic` tracks samples and sum with synchronized mutation/copy/mean/equality paths. `FileSystemStatisticNames`, `StoreStatisticNames`, and `StreamStatisticNames` declare stable metric keys for filesystem lifecycle, object-store operations, HTTP responses, multipart upload, stream reads/writes/seeks/vectored IO, prefetching, upload queues, and cache behavior.

`org.apache.hadoop.fs.viewfs.NotInMountpointException` and `RegexMountPointInterceptorType` begin the ViewFS section. The exception formats unsupported-operation errors when a path is not mounted through ViewFS. The interceptor enum maps names to configured regex mount-point interceptor types. The chunk ends immediately after the `ViewFileSystem` constructor opens, so the actual ViewFS method surface is outside this chunk.

## Control Flow And Behavioral Contracts

The XML does not contain method bodies, but the API docs describe expected flows. Path qualification borrows scheme/authority from a default URI and resolves relative paths against a working directory. Deserialization validation on `Path` and `FsPermission` is a defensive post-read step.

Positioned reads must not change the stream offset and are intended to be thread-safe, while the docs warn that some filesystems may violate this. `readVectored` defaults to synchronous per-range reading but allows subclasses to optimize. The release-aware overload delegates to the non-release overload by default and should be overridden by implementations that allocate pooled buffers.

Filesystem operations on `RawLocalFileSystem` and `FTPFileSystem` follow the `FileSystem` contract: initialize from URI/configuration, resolve path-to-storage, open/create/append/delete/list/status/rename/mkdir, then optionally mutate metadata. FTP create streams must be closed before other APIs are called or subsequent calls can block.

Builder control flow is option accumulation followed by `build()` in implementations. `opt` keys may be ignored; `must` keys require support and unknown mandatory keys must trigger `IllegalArgumentException`. Builders may be constructed around either a path or a path handle, but the base constructor rejects having both.

Trash flow resolves the correct trash location, moves deleted paths there, periodically checkpoints, and expunges old or all checkpoints. `moveToAppropriateTrash` specifically handles symlink and mount-point cases by resolving the path's volume before moving it.

Permission and ACL parsing converts stable shell-style strings into immutable `AclEntry`/`FsPermission` objects, and string outputs are explicitly compatibility-sensitive. Effective ACL permission calculation may need old NameNode compatibility data when the server does not provide modern effective-permission metadata.

IO statistics flow is source probing through `IOStatisticsSource`, retrieval of a possibly dynamic or immutable `IOStatistics`, optional snapshotting/aggregation, and logging or assertion. The package doc requires fast, nonblocking retrieval, stable key sets, post-close availability, and per-source uniqueness.

## State And Persistence

Most objects in this chunk are value or facade APIs, but several persist or expose state:

- `PathHandle` and `UploadHandle` are serialized opaque byte references and must preserve equality identity semantics.
- `QuotaUsage` persists quota and consumption counters, including per-storage-type arrays/maps.
- `RawLocalFileSystem`, `FTPFileSystem`, and `TrashPolicy` hold configuration-derived filesystem state such as URI, working directory, target filesystem, trash path, and deletion interval.
- `CommonAuditContext` has thread-local context and process-wide global context. Supplier-valued entries are long-lived and can create memory retention risks.
- `FsPermission` and `IOStatisticsSnapshot` are serializable; both include validation or deserialization safety notes. `IOStatisticsSnapshot` uses concrete sorted map structures for cross-framework transport and JSON serialization.
- `MeanStatistic` maintains mutable sample/sum state with synchronized update paths.
- Metric-name classes intentionally persist stable string constants for external dashboards, tests, and log parsing.

## Dependencies And Integration Points

The APIs depend on core Hadoop types including `Configuration`, `FileSystem`, `FileContext`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `FileRange`, `Path`, `PathHandle`, `Progressable`, `CreateFlag`, `Options.ChecksumOpt`, `Options.HandleOpt`, `FsPermission`, `StorageType`, `JsonSerialization`, and statistics/duration tracker interfaces.

External Java dependencies include `java.net.URI`, `java.io` streams and serialization types, `java.nio.ByteBuffer`, `java.util` collections/enums/optionals, `java.util.concurrent.CompletableFuture`, Java functional interfaces, and SLF4J `Logger`. FTP integration is explicitly backed by Apache Commons Net. Object-store integration is signaled through store/stream statistics, multipart upload builder APIs, prefetch/cache metric names, and package docs for shared object-store internals.

The chunk integrates with HDFS and non-HDFS implementations through shared filesystem interfaces: safe mode action compatibility, ACL/effective permission compatibility with older NameNodes, storage-type quota support, encryption-zone-aware trash lookup, ViewFS mountpoint behavior, and stream/path capability probes that let clients select optional behavior without binding to implementation classes.

## Risks And Edge Cases

Thread-safety is a recurring risk. `PositionedReadable` requires thread-safe positional reads, but the docs explicitly warn that not all filesystems satisfy it. Dynamic `IOStatistics` can be non-atomic across multiple map/value reads, so callers must avoid assuming snapshot consistency unless they create an `IOStatisticsSnapshot`.

Security-sensitive edges include malicious Java object streams for `Path` and `FsPermission`, untrusted deserialization of `IOStatisticsSnapshot`, supplier retention in `CommonAuditContext`, and xattr value decoding of user-provided text/hex/base64 inputs.

Compatibility risks include stable ACL string formats, stable metric names, deprecated `TrashPolicy` initialization/factory overloads, deprecated permission bits moved to `FileStatus`, and `QuotaUsage` output formatting. Changing these can break shell output, serialized data, dashboards, and downstream filesystem implementations.

Filesystem behavior varies by backend. `RawLocalFileSystem.listStatus` is documented as unsorted because it relies on Java `File.list()`. FTP create streams can block other API calls until closed. Rename, symlink, path capability, trash movement, path handles, and vectored IO are backend-sensitive and need careful capability probing.

The chunk boundary truncates `ViewFileSystem`, so no conclusion should be drawn here about its full constructor or methods. The merge lane must combine the following chunk before summarizing ViewFS behavior.

## Test Signals

Relevant tests should assert API contract behavior rather than XML parsing alone:

- Path qualification and deserialization validation reject invalid serialized state and correctly resolve URI/working-directory combinations.
- Positional read implementations preserve or document stream-position behavior, throw `EOFException` for incomplete `readFully`, validate non-overlapping vectored ranges, and release allocated buffers on failure when supported.
- Local and FTP filesystem contract tests cover create/open/append/delete/list/rename/truncate/mkdir/status/metadata operations, unsorted local listings, FTP stream-close blocking behavior, Windows destination-directory rename handling, and capability probes.
- Trash tests cover disabled trash, already-in-trash paths, mountpoint/symlink volume resolution, encryption-zone-aware trash directory selection, checkpoint creation, scheduled expunge, and immediate expunge.
- ACL and permission tests cover stable string round trips, parse failures, masked/unmasked create modes, umask handling, effective permission with and without old-NameNode compatibility data, serialization, and deprecated-bit migration to `FileStatus`.
- XAttr tests cover text, quoted text, hex, base64, invalid encodings, and create/replace flag validation.
- Audit context tests should verify thread-local isolation, global entry visibility, entry-point recording, reset behavior, supplier evaluation, and cleanup to avoid retained large objects.
- Builder tests should verify path-vs-path-handle exclusivity, typed `opt`/`must` storage, unknown mandatory-key rejection, buffer/status propagation, multipart flag transitions, and implementation-specific build failures.
- IOStatistics tests should cover stable key sets, post-close access, snapshot/aggregate/setter synchronization, JSON and Java serialization allowlists, mean-statistic edge cases, lazy logging, and consistency of exported metric names used by object stores and streams.

### subset-b-007236: lines 24627-30661

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 24627-30661

## Scope And Purpose

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.5.0. It is not executable Java source; it records the public and protected API surface, signatures, exceptions, inheritance, deprecation text, and extracted Javadoc for part of `hadoop-common`. The line range starts in the middle of `org.apache.hadoop.fs.viewfs.ViewFileSystem` and ends in the middle of `org.apache.hadoop.io.Text`, so the research covers only the members visible in this slice.

The chunk spans three major API areas:

- ViewFS client-side mount-table APIs: `ViewFileSystem`, `ViewFileSystemUtil`, and `ViewFs`.
- High availability and HTTP support APIs: HA protocol, fencing, service-target abstractions, protobuf protocol markers, and small HTTP config enums/constants.
- Hadoop IO serialization and file-format APIs: `Writable` wrappers, map and sequence-file formats, stringification, buffer pools, hash utilities, and the first part of `Text`.

Because this XML is used for API comparison, its main purpose is compatibility tracking. Any signature, return type, exception, visibility, deprecation marker, enum member, nested type reference, or documented behavior in this chunk is part of Hadoop Common's compatibility surface.

## ViewFS APIs

`ViewFileSystem` extends the classic `FileSystem` API and implements a client-side mount table with behavior documented as identical to `ViewFs`. The visible members expose the normal filesystem operations and forward them through ViewFS path resolution: initialization, URI/scheme access, working directory, open/create/append/delete/rename/truncate, mkdirs, status/listing, block locations, checksums, ACLs, xattrs, snapshots, storage policies, content/quota usage, trash roots, filesystem status, child filesystems, mount points, link targets, path capabilities, enclosing root, and close.

The most important behavior documented in this chunk is mount-link status handling. `getFileStatus(Path)` resolves a mount link to its target and returns the target status as a normal file or directory. `listStatus(Path)` defaults to representing immediate mount-link children as symlinks, with `getSymlink()` carrying the target; this can be changed by `fs.viewfs.mount.links.as.symlinks=false`, in which case target attributes are surfaced directly. `listStatus` also considers fallback links and documents that when the same directory path exists in configured mounts and fallback FS, the fallback path is listed except for links.

Trash root behavior is also a high-signal contract. `getTrashRoot(Path)` accounts for a `FORCE_INSIDE_MOUNT_POINT` flag and can return a target filesystem trash root, a corresponding ViewFS path, or `/{mountpoint}/.Trash/{user}` depending on whether the path, trash, fallback filesystem, encryption zone, snapshot root, or cloud-storage home-directory case requires localizing trash under the mount point. `getTrashRoots(boolean)` similarly returns trash roots under each mount point when forced inside mount points.

`ViewFileSystemUtil` is a final utility class with type-detection helpers for `ViewFileSystem` and `ViewFileSystemOverloadScheme`, plus `getStatus(FileSystem, Path)`. Its status helper maps matching ViewFS mount points to `FsStatus` for a path, including internal mount-tree directories such as `/dept` that resolve to root and aggregate all descendant mount points.

`ViewFs` extends `AbstractFileSystem` and exposes the FileContext-era equivalent surface: server defaults, URI default port, home directory, resolve path, `createInternal`, delete, file block locations, checksum, file/link status, `access`, `getFsStatus`, list iterators, `mkdir`, open, truncate, rename overloads, symlink support, link target, owner/permission/replication/times/checksum flags, mount points, delegation tokens, path validation, ACLs, xattrs, snapshots, and storage policies. As with `ViewFileSystem`, listing documentation emphasizes whether immediate mount links are returned as symlinks or target statuses.

## HA And HTTP APIs

The HA section defines exception types and the client-side protocol used by Hadoop HA frameworks:

- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` model fencing, failover, health-check, and service-transition failures.
- `FenceMethod` lets operators implement ordered fencing strategies. `checkArgs(String)` validates configured arguments, and `tryFence(HAServiceTarget, String)` returns true only when fencing succeeds; false covers failure or indeterminate outcomes.
- `HAServiceProtocol` is the RPC contract for health monitoring and failover. It exposes `monitorHealth`, `transitionToActive`, `transitionToStandby`, `transitionToObserver`, `getServiceStatus`, and a public `versionID`.
- `HAServiceProtocolHelper` wraps those RPC calls and unwraps `RemoteException` into the specific checked exceptions.
- `HAServiceTarget` is the abstract client-side target used by HA admin commands. It supplies the service IPC address, optional separate health-monitor RPC address, ZKFC address, fencer, fencing preflight validation, service and ZKFC proxies, transition target status, fencing parameters, auto-failover flag, and observer-state support flag.

State transitions are explicit: services can be active, standby, observer, initializing, or stopping, and transition calls are documented as no-ops when the service is already in the requested state. `RequestSource` captures who requested a transition, and `StateChangeRequestInfo` is passed into transition methods even though that nested class is outside the direct class inventory lines.

The protobuf protocol marker interfaces `HAServiceProtocolPB` and `ZKFCProtocolPB` appear at the package boundary and mark the protobuf-backed RPC integration points. The HTTP section is small: `JettyUtils` exposes UTF-8 and header-size constants, `HttpConfig.Policy` supports string parsing plus HTTP/HTTPS enablement checks, and `HttpServer2.XFrameOption` exposes enum conversion and string rendering for X-Frame-Options behavior.

## Hadoop IO Serialization APIs

The IO portion is the largest part of this chunk and covers Hadoop's long-lived binary serialization surface.

`AbstractMapWritable` is the base for `MapWritable` and `SortedMapWritable`. It implements `Writable` and `Configurable`, stores class-id mappings per map instance rather than statically, and limits class IDs to 1 through 127. Its synchronized `addToMap` and `copy` methods are important because map serialization must preserve the dynamic class table across nested writable maps.

Primitive and byte-oriented writables include `BooleanWritable`, `ByteWritable`, `ShortWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, `DoubleWritable`, `BytesWritable`, and `MD5Hash`. These generally implement `WritableComparable`, expose constructors, `set`/`get`, `readFields`, `write`, equality, hash, comparison, and string conversion. `BytesWritable` distinguishes logical length from backing capacity and has deprecated aliases `get()` and `getSize()`. `BinaryComparable` supplies bytewise comparison, equality, and hash semantics for byte-backed comparables such as `BytesWritable` and `Text`.

Array wrappers include `ArrayPrimitiveWritable`, which wraps primitive arrays without per-element object creation and without copying the underlying array, and `ArrayWritable`, which wraps homogeneous `Writable` arrays. `EnumSetWritable` serializes enum sets and requires an explicit element type when the set is null or empty. `GenericWritable` efficiently wraps one of a fixed set of `Writable` types by writing a compact type discriminator instead of writing a class name for every record, and it propagates configuration to wrapped configurables before deserialization.

`CompressedWritable` is a lazy-inflation base class. Subclasses implement `readFieldsCompressed` and `writeCompressed`; callers that access fields must call `ensureInflated()`. This contract is performance-sensitive for large map/reduce values because compressed data can be copied without full object inflation.

`DefaultStringifier` implements `Stringifier<T>` by serializing objects through Hadoop's `SerializationFactory` and Base64-encoding the result. It provides configuration-backed `store`, `load`, `storeArray`, and `loadArray` helpers, so it is an integration point between object serialization and `Configuration` persistence. The separate `Stringifier<T>` interface defines `toString(T)`, `fromString(String)`, and `close()`.

`ObjectWritable` is the generic object serializer with constructors for object and declared class, read/write methods, static `writeObject` overloads, static `readObject` overloads, class loading, and configuration propagation. The chunk contrasts it indirectly with `GenericWritable`: `ObjectWritable` writes class declarations more often and is less compact for repeated heterogeneous values.

`MapWritable` implements `Map<Writable, Writable>`, while `SortedMapWritable<K>` implements `SortedMap<K, Writable>`. Both inherit the dynamic class table from `AbstractMapWritable` and expose normal map operations plus `readFields` and `write`. `SortedMapWritable` additionally exposes comparator, first/last key, and range-view methods.

## File Format APIs

`SequenceFile` documents Hadoop's binary key/value container format. It exposes default compression configuration and a large overload set of `createWriter` methods. Many old overloads are deprecated in favor of `createWriter(Configuration, Writer.Option...)`; compatibility still matters because the deprecated signatures remain public. Non-deprecated overloads include filesystem-based creation with buffer size, replication, block size, `createParent`, compression type, codec, and metadata, plus FileContext-based creation with create flags and create options.

The file-format documentation is detailed and compatibility-critical. Sequence files share a header containing the `SEQ` magic/version, key class, value class, compression flags, optional compression codec class, metadata, and sync marker. Three writer formats are described: uncompressed records, record-compressed files where only values are compressed, and block-compressed files where key lengths, keys, value lengths, and values are collected into separately compressed blocks. `SYNC_INTERVAL` is the public default sync spacing, documented as 100 KB.

`MapFile` is a directory-backed sorted key/value map with `data` and `index` files. The index is read fully into memory, so key size affects reader memory use. Map files are created by appending entries in order; large updates are expected to be handled by copying an old database and merging a sorted change list. Static APIs support rename, delete, repair-by-recreating-index through `fix`, and a command-line `main`. `ArrayFile`, `SetFile`, and `BloomMapFile` build on this family: dense integer-to-value maps, file-based key sets, and MapFiles with dynamic Bloom filters for faster sparse key lookup. `BloomMapFile` exposes `BLOOM_FILE_NAME` and `HASH_COUNT`.

`NullWritable` is the singleton zero-value writable used where a key or value slot is intentionally empty. `MultipleIOException` aggregates multiple IOExceptions and has a factory method that returns a convenient IOException wrapper. `DataOutputOutputStream` adapts a `DataOutput` to `OutputStream`, returning the original object if it already is an `OutputStream`.

## Buffer, Stream, And Filesystem Utility APIs

`ByteBufferPool` defines `getBuffer(boolean direct, int length)`, `putBuffer(ByteBuffer)`, and a default `release()` method to clear buffers. The documentation promises a returned buffer with at least one byte of capacity, while the `direct` flag requests direct versus heap buffers. `ElasticByteBufferPool` implements this with synchronized get/put methods, caches released buffers, returns the smallest cached buffer with enough capacity, and intentionally does not impose a maximum cache size. This creates a memory-retention risk for large or adversarial buffer sizes.

`IOUtils` collects stream, channel, socket, directory, and fsync helpers. Key methods include `copyBytes` overloads with buffer size, count, configuration-derived buffer size, and optional close behavior; `wrappedReadForCompressedData`; `readFully`; `skipFully`; cleanup methods that deliberately ignore throwables; socket close; channel `writeFully` overloads for short-write handling; `listDirectory` that preserves IOExceptions rather than silently returning null; `fsync(File)` and `fsync(FileChannel, boolean)`; `wrapException` that adds path and method diagnostics while preserving special IOException types; and `readFullyToByteArray(DataInput)` which reads until EOF and must not be used with infinite inputs.

## Text API Slice

The chunk reaches the beginning of `org.apache.hadoop.io.Text`, Hadoop's mutable UTF-8 byte-string implementation extending `BinaryComparable` and implementing `WritableComparable<BinaryComparable>`. Visible constructors accept empty, `String`, another `Text`, or a UTF-8 byte array.

The visible API distinguishes efficient access to the backing array from exact copies: `getBytes()` returns the raw backing bytes valid only up to `getLength()`, while `copyBytes()` returns an exact-length copy. `getTextLength()` returns Unicode code-unit length, `charAt(int)` returns a Unicode scalar value without constructing a `String`, and `find(String[, int])` searches the UTF-8 backing buffer by byte position. Mutators include `set(String)`, `set(byte[])`, `set(Text)`, `set(byte[], int, int)`, `append(byte[], int, int)`, and `clear()`. `clear()` resets logical content but intentionally does not clear or free the backing array; callers must set an empty byte array to release that storage.

The visible serialization methods include `readFields(DataInput)`, `readFields(DataInput, int maxLength)`, static `skip(DataInput)`, `readWithKnownLength(DataInput, int)`, `write(DataOutput)`, and `write(DataOutput, int maxLength)`. The visible part ends at static `decode(byte[])`; later `Text` methods are outside this chunk.

## State And Persistence Behavior

The XML file itself is generated metadata and has no runtime state beyond representing Hadoop's public API at release 3.5.0. The APIs it describes do manipulate or encode persistent state:

- ViewFS state is configuration-derived mount-table state. Operations resolve ViewFS paths to target filesystems, fallback filesystems, trash roots, mount links, and child filesystem instances; persistence is delegated to the target filesystem.
- HA state lives in the managed service, ZKFC, fencing configuration, and RPC endpoints. This API controls transitions and health monitoring but does not itself persist active/standby state.
- Writable objects persist binary records through `DataInput` and `DataOutput`. Backing arrays and map class tables are object-local state that directly affect serialized bytes.
- `SequenceFile`, `MapFile`, `ArrayFile`, `SetFile`, and `BloomMapFile` persist Hadoop's on-disk binary formats. Their headers, sync markers, compression settings, index files, data files, Bloom filter files, and class names are compatibility-critical.
- `DefaultStringifier` persists serialized objects into `Configuration` keys as Base64 text.
- `ElasticByteBufferPool` retains buffers in memory after release and exposes an explicit release hook through `ByteBufferPool`.

## Dependencies And Integration Points

This chunk integrates with core Hadoop and Java APIs: `FileSystem`, `AbstractFileSystem`, `FileContext`, `Path`, `FileStatus`, `LocatedFileStatus`, `FsStatus`, `FsServerDefaults`, `ContentSummary`, `QuotaUsage`, `BlockStoragePolicySpi`, ACL and xattr types, `FsPermission`, `FsAction`, `CreateFlag`, `Options.CreateOpts`, delegation `Token`, `Configuration`, and `Progressable`.

HA APIs integrate with Hadoop IPC and protobuf RPC, `RemoteException` unwrapping, `ZKFCProtocol`, `NodeFencer`, operator-provided fencing scripts or classes, access-control exceptions, and optional lifeline/health-monitor RPC addresses.

IO APIs depend on Java `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `FileChannel`, `WritableByteChannel`, `ByteBuffer`, `Socket`, `MessageDigest`, collections, enums, and Hadoop serialization infrastructure such as `Writable`, `WritableComparable`, `RawComparator`, `WritableComparator`, `Serialization`, `Serializer`, `Deserializer`, `SerializationFactory`, compression codecs, and SLF4J logging.

The JDiff XML integrates with Hadoop's API compatibility tooling. Consumers compare these generated snapshots across releases to detect additions, removals, deprecations, signature changes, and doc-visible API changes.

## Risks And Edge Cases

- The chunk begins and ends mid-class. A reconciliation pass must merge it with adjacent chunks before drawing whole-file conclusions about `ViewFileSystem` and `Text`.
- ViewFS mount-link status semantics are subtle. `getFileStatus` resolves links, while `listStatus` may present immediate mount children as symlinks unless configured otherwise. Tests must cover both default and `fs.viewfs.mount.links.as.symlinks=false` behavior.
- Fallback filesystem handling can hide configured mount-path entries in listings, so regressions can appear as missing or duplicate directory children.
- Trash-root behavior depends on mount-point boundaries, fallback filesystems, cloud storage home semantics, encryption zones, snapshot roots, and `FORCE_INSIDE_MOUNT_POINT`.
- HA transition APIs are state-changing RPC calls. Incorrect exception unwrapping, access-control handling, or health-monitor address selection can cause failover automation to misclassify service state.
- Fencing APIs deliberately allow custom operator code. Argument validation must happen at startup through `checkArgs`, but `tryFence` can still discover runtime configuration errors.
- Writable serialization is binary compatibility sensitive. Changing field order, class-id assignment, compression markers, sequence-file headers, map-file index behavior, or Text length encoding can break old data.
- `AbstractMapWritable` supports only 127 distinct classes in one instance; large heterogeneous maps can exceed the class-id space.
- `ArrayPrimitiveWritable` and `BytesWritable.getBytes()` expose backing arrays. Callers can mutate internal state or retain oversized arrays if they do not use copy APIs.
- `Text.clear()` does not free the backing byte array. Long-lived `Text` reuse after large values can retain memory.
- `ElasticByteBufferPool` intentionally has no maximum cache size, so it can retain large direct or heap buffers until released or discarded.
- Several SequenceFile writer overloads are deprecated but public; removing or changing them would be an API compatibility break even if newer option-based construction is preferred.
- `readFullyToByteArray(DataInput)` reads until EOF and can hang or exhaust memory on unbounded inputs.

## Test Signals

Useful validation signals for this chunk include:

- JDiff/API compatibility checks between Hadoop Common versions, especially for public/protected signatures, exceptions, visibility, deprecation text, enum identities, fields, and nested type references.
- ViewFS unit and integration tests for mount resolution, fallback links, symlink-vs-target listing modes, ACL/xattr forwarding, snapshots, storage policies, content/quota usage, trash-root selection, status aggregation, and path capabilities.
- HA tests that mock or run HA services to validate health checks, active/standby/observer transitions, access-control failures, service-failure exceptions, lifeline health-monitor addresses, ZKFC proxy creation, and ordered fencing behavior.
- Serialization round-trip tests for every visible `Writable`, including null and empty enum sets, nested `MapWritable`/`SortedMapWritable`, heterogeneous `GenericWritable`, `ObjectWritable` class loading, compressed lazy inflation, exact backing-array length behavior, and configuration propagation.
- Golden-file compatibility tests for `SequenceFile` uncompressed, record-compressed, and block-compressed formats, including header fields, sync markers, metadata, compression codecs, deprecated and option-based writer creation paths, and old-reader/new-writer interoperability.
- MapFile repair and persistence tests for `data`/`index` files, sorted insertion requirements, index memory behavior, rename/delete, dry-run `fix`, `ArrayFile`, `SetFile`, and `BloomMapFile` membership lookup.
- IO utility tests for short reads/writes, EOF handling, close-on-copy semantics, ignored cleanup exceptions, socket close, directory listing errors, fsync files versus directories, exception wrapping, and unbounded-input safeguards.
- `Text` tests for UTF-8 validation, byte-position search, Unicode scalar `charAt`, exact versus backing-byte access, max-length guarded reads/writes, skip behavior, known-length reads, and memory retention after `clear()`.

### subset-b-007237: lines 30662-36701

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml - subset-b-007237

## Scope

This chunk covers lines 30662-36701 of the Hadoop Common 3.5.0 JDiff XML API dump. It is API metadata rather than executable Java source. The slice starts inside the tail of `org.apache.hadoop.io.Text`, completes the remaining public `org.apache.hadoop.io` writable/serialization utility APIs, covers the public compression API families under `org.apache.hadoop.io.compress`, several small nested enum API dumps for bzip2/zlib/native IO/retry, erasure-code schema metadata, TFile public helpers, compatibility wrappers under `org.apache.hadoop.io.wrappedio`, and the beginning of the IPC package through `Client`, `Server`, and `ProcessingDetails.Timing`. It ends at the start of `org.apache.hadoop.metrics2.AbstractMetric`.

## Purpose

The XML records Hadoop Common's public binary/source API for compatibility checking. In this chunk, most APIs are core cross-cutting infrastructure:

- Writable encoding and raw comparison primitives used by Hadoop RPC, MapReduce sort/shuffle, filesystem metadata, and other binary protocols.
- Compression codec contracts, stream wrappers, codec lookup/pooling, and splittable codec behavior used by filesystems and input formats.
- Erasure coding and TFile public metadata helpers.
- Reflection-friendly wrapper classes that let downstream libraries use newer Hadoop filesystem/statistics APIs while still compiling against older Hadoop releases.
- IPC client/server entry points and observability hooks used by RPC engines, service authorization, metrics, call queues, and tests.

Because this is a JDiff file, the "control flow" is expressed by API contracts, constructor/method signatures, inheritance, exceptions, and documented lifecycle expectations rather than method bodies.

## Important APIs And Types

### `org.apache.hadoop.io` tail

- `Text` tail methods expose UTF-8 byte/string conversions and validation: `decode(byte[], int, int)`, `decode(byte[], int, int, boolean)`, `encode(String)`, `encode(String, boolean)`, `readString(DataInput[, int])`, `writeString(DataOutput, String[, int])`, `validateUTF8(byte[][, int, int])`, `bytesToCodePoint(ByteBuffer)`, `utf8Length(String)`, and `DEFAULT_MAX_LEN`. The API contract distinguishes replacement of malformed input from `CharacterCodingException`/`MalformedInputException` failures, and uses `DataInput`/`DataOutput` for wire persistence.
- `TwoDArrayWritable` is a `Writable` matrix wrapper with constructors for a value class and optional `Writable[][]`, plus `toArray`, `set`, `get`, `readFields`, and `write`.
- `VIntWritable` and `VLongWritable` are `WritableComparable` holders for zero-compressed variable-length integer encodings. Both expose no-arg/value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `VersionMismatchException` extends `IOException` and is thrown when a `VersionedWritable` stream version does not match the implementation version.
- `VersionedWritable` is an abstract `Writable` base with abstract `getVersion()`, plus concrete `write(DataOutput)` and `readFields(DataInput)` version checking.
- `Writable` defines the core Hadoop binary persistence contract: `write(DataOutput)` and `readFields(DataInput)`. Its documentation emphasizes that `readFields` must restore all fields written by `write`.
- `WritableComparable<T>` combines `Writable` with Java `Comparable<T>`.
- `WritableComparator` provides comparator registration and byte-level utilities. Important APIs include static `get(Class[, Configuration])`, static `define`, instance `newKey`, object and raw-byte `compare` overloads, `compareBytes`, `hashBytes`, primitive readers from byte arrays (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`), and `Configurable` methods `setConf`/`getConf`.
- `WritableFactories` and `WritableFactory` support factory registration for non-public writable types so `ObjectWritable` and other reflective paths can instantiate them.
- `WritableUtils` centralizes binary helper methods: compressed byte/string arrays, plain and compressed string arrays, display/debug byte dumps, serialization-based `clone`, deprecated `cloneInto`, VInt/VLong write/read/size/sign decoding, enum write/read, `skipFully`, `toByteArray`, and bounded `readStringSafely`.

### `org.apache.hadoop.io.compress`

- `CompressionCodec` is the central codec interface. It creates compression/decompression streams with or without explicit `Compressor`/`Decompressor` instances, exposes compressor/decompressor classes and factories, and declares a default filename extension.
- `BZip2Codec` implements `Configurable` and `SplittableCompressionCodec`. Its docs state it can choose native bzip2 or pure Java based on configuration, that compressor/decompressor argument overloads may be unsupported in pure-Java mode, and that split input uses the pure-Java path to align at block boundaries.
- `BlockCompressorStream` and `BlockDecompressorStream` adapt block-based compressors/decompressors to Hadoop streams. The documented format stores an uncompressed block length followed by one or more length-prefixed compressed blocks.
- `CodecConstants` publishes default extension constants for default, bzip2, gzip, lz4, passthrough, snappy, and zstandard codecs.
- `CodecPool` leases and returns reusable `Compressor` and `Decompressor` instances. It also exposes leased compressor/decompressor counts, which are useful as leak test signals.
- `CompressionCodecFactory` constructs a codec registry from `Configuration`, supports static `getCodecClasses`/`setCodecClasses`, and resolves codecs by path, class name, short name, or class. It also has `removeSuffix` and a diagnostic `main`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases with state reset and IO statistics hooks. Input streams additionally expose position/seek/seek-to-new-source methods; output streams expose `finish`, `flush`, `resetState`, and the wrapped `out`.
- `Compressor`, `Decompressor`, `DirectDecompressionCodec`, and `DirectDecompressor` define stateful compression primitives. The contracts expose input/dictionary management, byte counters, `finish`/`finished`, `needsInput`, `needsDictionary`, `reset`, `end`, `reinit(Configuration)`, and direct `ByteBuffer` decompression.
- `CompressorStream` and `DecompressorStream` are stream implementations around those stateful primitives, with protected buffers and `closed`/`eof` fields that matter for lifecycle correctness.
- `DefaultCodec` implements the standard deflate-style codec and direct decompression factory. `GzipCodec` extends it for gzip streams. `PassthroughCodec` implements `CompressionCodec` without transforming bytes and is documented as a way to disable decompression for configured extensions such as `.gz`.
- `SplittableCompressionCodec` and its nested `READ_MODE` enum define the split-aware compressed input contract. `SplitCompressionInputStream` tracks adjusted start/end offsets after a codec aligns a requested split to actual compressed-block boundaries.

### Compression nested enum packages

- `org.apache.hadoop.io.compress.bzip2.CBZip2InputStream.STATE` appears as public nested enum metadata with `values`/`valueOf`, representing decoder state labels.
- `org.apache.hadoop.io.compress.zlib.ZlibCompressor.CompressionHeader`, `ZlibDecompressor.CompressionHeader`, `ZlibCompressor.CompressionLevel`, `ZlibCompressor.CompressionStrategy`, and `BuiltInGzipDecompressor.GzipStateLabel` expose `values`/`valueOf`; the compression header enums also expose `windowBits()`.

### Erasure coding

- `ECSchema` is a final `Serializable` metadata holder for erasure-code schema parameters. Constructors accept an all-options map, `(codecName, numDataUnits, numParityUnits)`, or key parameters plus extra options. Accessors include `getCodecName`, `getExtraOptions`, `getNumDataUnits`, `getNumParityUnits`, plus `toString`, `equals`, and `hashCode`. Public keys are `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.

### TFile

- `Compression.Algorithm` is an enum-like public nested type with abstract `createCompressionStream`, `createDecompressionStream`, and `isSupported`, plus compressor/decompressor leasing helpers, `getName`, shared `conf`, and `CONF_LZO_CLASS`.
- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are public `IOException` subclasses for TFile metadata block errors.
- `RawComparable` exposes byte range accessors `buffer`, `offset`, and `size`; comparisons are delegated to a `RawComparator`.
- `TFile` exposes static helper APIs `makeComparator(String)`, `getSupportedCompressionAlgorithms()`, and `main(String[])`, along with public constants `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, `COMPARATOR_MEMCMP`, and `COMPARATOR_JCLASS`.
- `Utils` exposes TFile-local VInt/VLong encoding and decoding, string write/read helpers, and generic `lowerBound`/`upperBound` binary search utilities over lists with comparators.

### Native IO and retry enum fragments

- `NativeIO.Windows.AccessRight` exposes `values`, `valueOf`, and `accessRight()` for Windows access masks.
- `Errno` exposes POSIX/native errno enum metadata.
- `NativeIO.POSIX.SupportState` exposes `values`, `valueOf`, `getStateCode`, and `getMessage`.
- `RetryPolicy.RetryAction.RetryDecision` exposes enum metadata for retry/fail/failover style decisions.

### Serialization packages

- `JavaSerialization` accepts `Serializable` values and creates corresponding Hadoop `Serializer`/`Deserializer` instances.
- `JavaSerializationComparator<T>` extends `DeserializerComparator<T>` and compares serialized Java objects at byte-array offsets.
- `WritableSerialization` extends `Configured` and accepts `Writable` values, returning serializers/deserializers for Hadoop writables.
- `AvroReflectSerializable` is a marker interface.
- `AvroSerialization<T>` is the configured base for Avro serializers/deserializers, requiring schema, writer, and reader hooks, and publishing `AVRO_SCHEMA_KEY`.
- `AvroReflectSerialization` accepts reflect-serializable objects/packages, with `AVRO_REFLECT_PACKAGES`, and supplies Avro reflect schema/reader/writer.
- `AvroSpecificSerialization` accepts Avro `SpecificRecord` values and supplies specific Avro schema/reader/writer.

### Wrapped compatibility APIs

- `WrappedIO` is a final static facade for reflection-friendly access to newer filesystem APIs. It wraps bulk delete page size and delete calls, path and stream capability probing, `FileSystem.openFile(Path)` with optional policy/status/length/options, `FileSystem.getEnclosingRoot(Path)`, and `ByteBufferPositionedReadable` positioned read helpers.
- `WrappedStatistics` is a final facade around IOStatistics APIs. It can test object types, create/load/save/retrieve/aggregate `IOStatisticsSnapshot` values, serialize/deserialize JSON strings, expose counters/gauges/minimums/maximums/means maps, manage thread-level `IOStatisticsContext`, pretty-print statistics, and apply functions to valid snapshots.
- The package documentation explicitly says public classes here are intended for reflective loading by downstream libraries, and tests should themselves use reflection to guarantee that compatibility surface.

### `org.apache.hadoop.ipc`

- `CallerContext` is an immutable audit context with context/signature accessors, validity, equality/hash/string behavior, static thread-local `getCurrent`/`setCurrent`, and public string constants for client IP, port, id, call id, real user, and proxy user port.
- `Client` is the core IPC client and implements `AutoCloseable`. It constructs from a `Writable` value class, `Configuration`, and optional `SocketFactory`; manages async response retrieval (`getAsyncRpcResponse`, `getResponseFuture`), call id/retry state, external handlers, max async calls, ping/connect/RPC timeout configuration, synchronous/asynchronous mode, `nextCallId`, `call(...)` overloads, `stop`, `close`, and logging.
- `RPC.RpcKind` appears as a nested enum dump with `values` and `valueOf`.
- `Server` is the abstract IPC service. Constructors bind address/port, request class, handler/readers/queue sizing, configuration, server name, token secret manager, and optional port range configuration. Public/static APIs include logging exception filters, alignment context, protocol engine registration, invoker lookup, thread-local current server/call details, remote IP/port/address/user/protocol/client id lookup, call id/retry count/priority, slow RPC settings, bind helpers, metrics accessors, service ACL refresh, call queue refresh/queueing, auxiliary listeners, socket send buffer sizing, tracing, lifecycle `start`/`stop`/`join`, listener address queries, abstract modern `call(RPC.RpcKind, String, Writable, long)`, deprecated legacy `call(Writable, long)`, and operational counters/backoff/failover/queue/reader/max-idle/server-name accessors.
- `ProcessingDetails.Timing` appears as a nested enum dump with `values`/`valueOf` for RPC timing stages.

### `org.apache.hadoop.metrics2`

- The chunk starts `AbstractMetric`, an abstract `MetricsInfo` implementation with a protected `MetricsInfo` constructor, concrete `name`, `description`, protected `info`, and abstract `value()`. The class continues in the next chunk, so this report only covers the visible prefix.

## Control Flow And Lifecycle Contracts

- Writable flow is consistently `write(DataOutput)` followed by `readFields(DataInput)` on a reused or newly constructed object. Versioned writables add a leading version byte and throw `VersionMismatchException` during `readFields` if the stream version is incompatible.
- Raw comparison flow in `WritableComparator` favors byte-array comparison for performance-sensitive sorting. Object comparison can instantiate keys through registered factories, while optimized subclasses can override the byte-level compare path and use static primitive readers.
- Variable-length integer flow is shared across `VIntWritable`, `VLongWritable`, `WritableUtils`, `WritableComparator`, and TFile `Utils`: a first byte encodes sign and encoded width; subsequent non-zero bytes are stored high-order first.
- Compression flow is codec -> optional pooled compressor/decompressor -> stream wrapper -> `finish`/`close`/`resetState` -> return pooled primitive. Direct decompression bypasses heap byte arrays through `ByteBuffer`.
- Splittable compression flow gives codecs a requested compressed start/end range and a `READ_MODE`; codecs may adjust boundaries and expose final values through `SplitCompressionInputStream.getAdjustedStart()`/`getAdjustedEnd()`.
- `CodecPool` creates shared mutable resource flow: callers lease compressors/decompressors and must return them. `getLeasedCompressorsCount` and `getLeasedDecompressorsCount` are direct observability for resource leaks.
- `WrappedIO` and `WrappedStatistics` convert availability-sensitive APIs into stable reflective helper calls. Several methods deliberately convert checked `IOException` into `UncheckedIOException` or boolean false for compatibility.
- IPC client flow is construct client -> configure call id/retry/async/thread-local response state -> invoke `call` against a `ConnectionId` -> read a `Writable` response or async future -> `stop`/`close`. Static asynchronous mode and response future APIs imply thread-local/global state that must be reset carefully in tests.
- IPC server flow is construct/bind -> optionally register protocol engines and configure ACLs/call queues/tracing/slow-RPC logging -> `start` service threads -> queue and dispatch calls to the abstract `call(RpcKind, protocol, param, receiveTime)` -> report metrics and state -> `stop` and optionally `join`.

## State And Persistence Behavior

- Binary persistence is dominated by Hadoop's `Writable` protocol and Java `DataInput`/`DataOutput`. Public API stability here matters because the same bytes are used in files, RPC requests/responses, and sorted keys.
- `Text` and `WritableUtils` both serialize strings with explicit lengths and UTF-8 bytes; `readStringSafely` adds length bounds before consuming the payload.
- Compressed byte arrays/strings in `WritableUtils` and block compression streams introduce secondary persistence formats inside the writable stream. Block compression stores uncompressed sizes and length-prefixed compressed chunks.
- `ECSchema` is `Serializable` and map-backed enough for schema options to persist across configuration or RPC/file metadata boundaries.
- Avro serialization relies on schemas from configuration (`AVRO_SCHEMA_KEY`) or reflected/specific Avro types. Changes to accepted classes, schema discovery, or writer/reader types are compatibility-sensitive.
- `WrappedStatistics` explicitly persists IO statistics snapshots as JSON through Hadoop `FileSystem` paths and can reload them as serializable snapshots.
- IPC server/client state includes thread-local current call/server context, call ids, retry counts, async futures, caller context, metrics objects, call queue state, listener sockets, auxiliary listener sockets, slow RPC flags, service ACLs, and secret manager integration. These are runtime state surfaces, not file persistence, but they are observable and API-stable.

## Dependencies And Integration Points

- Core Java dependencies: `java.io`, `java.nio.ByteBuffer`, `java.nio.charset`, `java.net`, `java.util`, `java.util.concurrent.CompletableFuture`, `java.util.concurrent.atomic.AtomicBoolean`, and enum/serialization infrastructure.
- Hadoop dependencies: `Configuration`, `Configured`, `Writable`, `RawComparator`, `FileSystem`, `FSDataInputStream`, `FileStatus`, `Path`, filesystem statistics APIs, security `UserGroupInformation`, token `SecretManager`/`TokenIdentifier`, service authorization `PolicyProvider`/`ServiceAuthorizationManager`, RPC `AlignmentContext`, `RPC.RpcInvoker`, tracing `Tracer`, and IPC metrics classes.
- External dependencies: SLF4J logging, Avro `Schema`, `DatumReader`, `DatumWriter`, `SpecificRecord`, zlib/bzip2 native or Java codecs, and optional LZO class support in TFile compression.
- Integration-sensitive public packages in this chunk are explicitly used by downstream projects: `org.apache.hadoop.ipc` package docs warn that changes to `RPC` and `RpcEngine` signatures break other ASF projects, including shaded/unshaded protobuf deployments.

## Risks And Compatibility Concerns

- This XML is generated API metadata. It is useful for signature compatibility but cannot prove method-body behavior, exception ordering, synchronization correctness, resource cleanup, or thread-local cleanup.
- `Writable` and variable-length integer encodings are long-lived wire/file formats. Any signature or behavior drift in read/write, length bounds, sign decoding, or byte order can corrupt persisted data or break RPC compatibility.
- `Text` malformed UTF-8 handling has two modes. Replacing invalid bytes vs throwing `MalformedInputException` affects security and input validation paths.
- `WritableFactories` and `WritableComparator` rely on reflection/configuration and global registrations. Factory or comparator registration changes can alter deserialization and sort behavior process-wide.
- Compression APIs are stateful and resource-backed. Leaked compressors/decompressors, incorrect `reset`/`end`/`return*` behavior, or direct `ByteBuffer` position mishandling can cause native memory leaks, corrupted streams, or bad split boundaries.
- `BZip2Codec` has divergent native and pure-Java behavior, including documented unsupported compressor/decompressor overloads in pure-Java mode and split support only through pure Java. Tests must exercise both configuration branches where available.
- `PassthroughCodec` intentionally disables decompression by extension. Registering it broadly can silently pass compressed bytes to callers expecting decompressed data.
- Wrapped compatibility facades trade compile-time type safety for reflection-friendly APIs. Wrong object types are documented to produce `IllegalArgumentException`, `ClassCastException`, `UncheckedIOException`, or false capability probes; downstream callers may depend on those exact failure modes.
- IPC `Client`/`Server` APIs expose global/thread-local state, async state, call ids that wrap back to zero, service ACL refresh, failover/backoff behavior, and metrics/test accessors. Concurrency bugs or signature changes here have high blast radius.
- Deprecated APIs remain part of the API dump, including `WritableUtils.cloneInto`, `Client.getTimeout`, and legacy `Server.call(Writable, long)`. Removal or behavior changes can break older downstream tests and integrations.
- The chunk ends mid-`AbstractMetric`, so metrics API conclusions are incomplete until the next chunk is merged.

## Test Signals

- JDiff/API compatibility tests should ensure the signatures, visibility, deprecation text, thrown checked exceptions, static/final/abstract flags, and field visibility in this XML remain stable unless an intentional compatibility change is recorded.
- Writable round-trip tests should cover `Text`, `TwoDArrayWritable`, `VIntWritable`, `VLongWritable`, `VersionedWritable`, factories, and `WritableUtils` string/array/compressed helpers, including max-length and malformed UTF-8 cases.
- Raw comparator tests should compare object-order and byte-order paths, primitive byte readers, VInt/VLong readers, custom `WritableComparator.define`, and configured comparator construction.
- Compression tests should cover codec factory lookup by extension/name/class, configured codec lists, pool lease/return counters, compressor/decompressor reset/end behavior, block stream round trips, direct decompressor `ByteBuffer` position changes, and splittable bzip2 adjusted start/end values.
- Codec-specific tests should include bzip2 native vs pure-Java configuration, gzip/default direct decompression, passthrough extension override, and TFile compression algorithm support detection.
- Serialization tests should cover Java serialization acceptance, writable serialization acceptance, Avro reflect package configuration, Avro specific record schemas, and comparator behavior on serialized byte slices.
- WrappedIO tests should intentionally use reflection to call the public methods, as the package docs require. Cases should cover unsupported bulk delete, invalid paths outside base, capability false-on-IO behavior, `openFile` options/status/length wiring, and ByteBuffer positioned-read detection through wrapped streams.
- WrappedStatistics tests should cover valid and invalid snapshot objects, JSON save/load/from-string/to-string, aggregate behavior, thread context set/reset/snapshot, and map accessor stability for counters/gauges/min/max/means.
- IPC tests should exercise sync and async `Client.call`, `CompletableFuture` retrieval, call id wrapping/non-negative masking, retry count propagation, connection timeout/ping/RPC timeout configuration, fallback-to-simple-auth flag behavior, and close/stop idempotence.
- IPC server tests should verify bind error clarity, port-range binding, service ACL refresh paths, call queue refresh, auxiliary listener addresses, metrics handles, slow-RPC flag/threshold, connection/drop/queue counters, client backoff/failover settings, and deprecated legacy `call` delegation to the modern abstract call path.

### subset-b-007238: lines 36702-42861

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 36702-42861

## Scope

This chunk is a JDiff public API snapshot for Hadoop Common 3.5.0. It starts in the tail of `org.apache.hadoop.metrics2.AbstractMetric`, covers the rest of the public Metrics2 API and several Metrics2 subpackages, then moves through network mapping/socket APIs, ONC RPC enum surfaces, Hadoop security credential/authentication APIs, and ends at the beginning of `org.apache.hadoop.security.alias.CredentialProvider`. Because the source is generated XML rather than implementation code, the research focuses on exposed contracts, API shape, state surfaces, integration behavior implied by signatures/docs, compatibility risks, and tests that should protect users of these contracts.

## Purpose

The chunk documents several cross-cutting Hadoop Common subsystems:

- Metrics2 core interfaces and helpers define how Hadoop components expose metrics, build records, filter sources/sinks, publish to sinks, register with a metrics system, expose JMX controls, and represent immutable metric/tag values.
- Metrics2 annotations, filters, libraries, sinks, Ganglia enums, and utilities provide the higher-level instrumentation layer used by Hadoop daemons and tests: registries, mutable counters/gauges/stats/quantiles, default singleton metrics system management, file/network metrics sinks, MBean registration, and sink-side cache helpers.
- Network APIs define DNS-to-rack mapping contracts, cached/script/table mapping implementations, socket factories, and connect-timeout exception typing used by Hadoop RPC/filesystem clients and daemons.
- ONC RPC APIs expose enum conversions for RPC message/reply/auth states used by Hadoop's NFS/portmap-style services.
- Security APIs expose access-control exceptions, SASL/authentication enum mapping, credentials token/secret-key storage and serialization, group/id mapping providers, Kerberos exception diagnostics, security utility methods, and `UserGroupInformation` login/proxy/doAs/token/group behavior.
- The final `CredentialProvider` fragment marks the start of the credential alias provider API, but this chunk only includes its constructor and the beginning of `isTransient()`.

## Important APIs, Types, And Functions

### Metrics2 Core

The tail of `AbstractMetric` exposes `type()`, `visit(MetricsVisitor)`, and object identity methods. It is the immutable metric value abstraction paired with visitor callbacks for gauges and counters.

`MetricStringBuilder` and `MetricsJsonBuilder` both extend `MetricsRecordBuilder` and collect metric records into diagnostic renderings. `MetricStringBuilder` formats entries as `prefix + name + separator + value + suffix`, supports arbitrary `tuple(key, value)`, and implements the tag/counter/gauge/add paths. `MetricsJsonBuilder` exposes the same builder-style record API and serializes collected values as JSON; it also exposes a public `LOG`.

`MetricType` is the public enum for metric kind. `MetricsInfo` carries immutable metric/tag metadata through `name()` and `description()`. `MetricsTag` combines `MetricsInfo` and a string value and exposes name, description, info, value, equality, hash, and string conversion.

`MetricsCollector` starts records via `addRecord(String)` or `addRecord(MetricsInfo)`. `MetricsRecordBuilder` is the fluent builder contract for `tag`, `add(MetricsTag)`, `add(AbstractMetric)`, `setContext`, overloaded `addCounter`, overloaded `addGauge`, `parent()`, and `endRecord()`. `MetricsRecord` is the immutable snapshot interface exposing timestamp, name, description, context, tags, and metric iterable.

`MetricsSource.getMetrics(MetricsCollector, boolean)` is the pull side of the framework. `MetricsSink.putMetrics(MetricsRecord)` and `flush()` are the sink side. `MetricsFilter` can accept or reject by name, tag, tag collection, or whole record and implements `MetricsPlugin`; `MetricsPlugin.init(SubsetConfiguration)` is the common configuration hook. `MetricsException` is the runtime wrapper used by the framework.

`MetricsSystem` is the daemon-facing registration and lifecycle abstraction: `init(prefix)`, `register(source)`, `register(name, desc, source)`, `unregisterSource(name)`, `getSource(name)`, callback registration, immediate publication, and `shutdown()`. `MetricsSystemMXBean` exposes JMX lifecycle operations for starting/stopping the system and Metrics MBeans plus `currentConfig()`. `MetricsVisitor` defines overloaded gauge/counter callbacks for `int`, `long`, `float`, and `double`.

### Metrics2 Annotation, Filter, Library, Sink, And Utility APIs

`org.apache.hadoop.metrics2.annotation.Metric` annotates fields or methods with optional value/name/description, sample/value names for stats, `always`, type, and quantile rollover interval. `Metrics` annotates metric groups with record name, description, and context. The nested `Metric.Type` enum is represented in this XML as `Type`.

`GlobFilter` and `RegexFilter` extend the metrics pattern filter base and compile strings to `com.google.re2j.Pattern`. They are intended for metrics configuration files.

`DefaultMetricsSystem` is an enum singleton facade for the process-wide default metrics system. It initializes or returns the current `MetricsSystem`, shuts it down, swaps the instance, toggles mini-cluster mode, manages MBean/source-name uniqueness, and returns `ObjectName` values. Name collision behavior is visible through `sourceName(name, dupOK)`.

`Interns` creates interned `MetricsInfo` and `MetricsTag` instances to reduce allocation and provide canonical metadata/tag objects.

`MetricsRegistry` is the main mutable source-side registry. It exposes registry info, metric/tag lookup, factory methods for int/long counters, int/long/float gauges, quantiles, inverse quantiles, stats, rates, aggregated rates, and rolling averages. It also supports adding samples by name, context/tag creation with override controls, snapshotting all metrics into a `MetricsRecordBuilder`, and string conversion.

The mutable metric hierarchy includes:

- `MutableMetric`: abstract base with `snapshot(builder, all)`, convenience `snapshot(builder)`, changed-flag management, and `changed()`.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong`: monotonically increasing counters with increment/value/snapshot behavior.
- `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong`: gauges with increment/decrement/set/value/snapshot behavior.
- `MutableQuantiles` and `MutableInverseQuantiles`: online quantile estimators with interval rollover, quantile metadata arrays, estimator access, add, snapshot, stop, and previous snapshot state. They expose `QUANTILES`, `INVERSE_QUANTILES`, and `previousSnapshot`.
- `MutableRate`, `MutableRates`, and `MutableRatesWithAggregation`: throughput/rate metrics, protocol-method initialization, named elapsed-time sample updates, and snapshots.
- `MutableRollingAverages`: rolling aggregate collection with thread-local state collection, named sample add, close, test-only record-validity control, and stats retrieval.
- `MutableStat`: sample count/sum/stat tracking with optional extended stats, timestamp control, reset of min/max, last-stat access, snapshot timestamp, and string conversion.

Metrics sinks in this chunk include `FileSink`, `GraphiteSink`, `RollingFileSystemSink`, and `StatsDSink`. They implement the standard `init(SubsetConfiguration)`, `putMetrics(MetricsRecord)`, `flush()`, and close/write paths where applicable. `RollingFileSystemSink` has the richest public surface: test constructor with roll intervals, roll interval parsing, next-flush computation, initial flush time setup, and public fields for source, error handling, append behavior, base path, roll intervals, next flush calendar, force/has-flushed flags, supplied configuration, and supplied filesystem. `StatsDSink.writeMetric(String)` exposes the line-writing path.

Ganglia-related enum surfaces expose `GangliaConfType` and `GangliaSlope`. `org.apache.hadoop.metrics2.source` has no concrete public types in this chunk. `MBeans` provides standard Hadoop MBean registration/unregistration and name parsing. `MetricsCache` caches `MetricsRecord` values for sinks that cannot handle sparse updates. `Servers.parse(specs, defaultPort)` parses comma/space-separated server endpoint strings.

### Network And ONC RPC APIs

`DNSToSwitchMapping` is the rack-resolution interface: `resolve(List<String>)`, `reloadCachedMappings()`, and targeted reload by node list. `AbstractDNSToSwitchMapping` adds `Configurable` behavior, default single-switch/topology diagnostics, switch-map access, and helper `isMappingSingleSwitch(mapping)`.

`CachedDNSToSwitchMapping` wraps a raw mapping, caches results, exposes the raw mapping field, resolves names, dumps its switch map, delegates single-switch queries, and reloads all or selected cached mappings. `ScriptBasedMapping` is a cached mapping using a configured external script and exposes `NO_SCRIPT`, configuration access, and `toString()`. `TableMapping` is a cached mapping backed by a table file and supports configuration and cache reload.

`ConnectTimeoutException` specializes `SocketTimeoutException` for `NetUtils.connect`. `SocksSocketFactory` and `StandardSocketFactory` implement the overloaded `SocketFactory.createSocket` variants. `SocksSocketFactory` also implements Hadoop configuration access and equality/hash behavior around its proxy; `StandardSocketFactory` provides equality/hash behavior for default sockets.

ONC RPC enum surfaces include accepted reply state (`AcceptState` with integer value conversion), denied reply state (`RejectState`), reply state (`ReplyState` with `fromValue`), XDR state (`State`), RPC message type (`Type` with `getValue()` and `fromValue()`), and security auth flavor (`AuthFlavor` with numeric RFC 1831 value).

### Security APIs

`AccessControlException` is the checked access-control failure type. `AuthMethod` is the SASL RPC auth enum surface with mechanism name, binary read/write, and public `code`. `AuthenticationMethod` maps UGI authentication modes to/from `SaslRpcServer.AuthMethod`.

`Credentials` stores tokens and secret keys in memory and serializes them. Public operations include token lookup/add/remove, unmodifiable token map access, token count, secret key lookup/add/remove, secret-key alias listing, unmodifiable secret-key map access, reading token storage files from `Path` or `File`, stream read/write, token storage file write with optional serialized format, `Writable`-style `write`/`readFields`, and combining credentials through `addAll` and `mergeAll`.

`GroupMappingServiceProvider` resolves a user to groups, refreshes/augments caches, exposes a set-returning alternative, and publishes `GROUP_MAPPING_CONFIG_PREFIX`. `IdMappingServiceProvider` maps users/groups to numeric ids and ids back to names, with "allowing unknown" variants.

`KerberosAuthException` carries diagnostic context around failed Kerberos authentication. It can be constructed from message, cause, or both, then enriched with user, principal, keytab file, and ticket cache file. Accessors and `getMessage()` expose the enriched details. `QualityOfProtection` exposes the SASL QOP string through `getSaslQop()` and public `saslQop`.

`SecurityUtil` is the public utility surface for security configuration and protocol metadata. It includes static configuration and token-service-IP controls, Kerberos TGT inspection, server principal expansion from hostname/address, keytab login helpers, delegation-token service-name construction, principal host extraction, security-info provider registration, Kerberos/token info lookup for RPC protocols, token service address/set/build helpers, privileged `doAs` helpers for login/current user, secure DNS resolution, authentication-method config get/set, privileged-port checks, ZooKeeper auth info parsing, and ZooKeeper SSL configuration validation/application. Its public fields include `LOG`, `HOSTNAME_PATTERN`, and `FAILED_TO_GET_UGI_MSG_HEADER`.

`SerializedFormat` is the credentials serialized-format enum with `valueOf(String)` and `valueOf(int)`.

`UserGroupInformation` is the central Hadoop user identity surface. This chunk exposes static initialization/configuration/reset methods, security status checks, login success and Kerberos credential checks, current/login/best UGI selection, ticket-cache and `Subject` login helpers, setting login user, keytab/ticket relogin flows, remote/proxy/testing user creation, real-user lookup, short/full username and primary group access, token identifier/token/credential mutation and access, group retrieval, authentication method get/set including real-authentication handling, subject identity equality/hash, protected subject access, `doAs` wrappers for privileged actions, user-info logging helpers, a diagnostic `main`, and token environment variable names `HADOOP_TOKEN_FILE_LOCATION` and `HADOOP_TOKEN`. `getGroups()` is explicitly deprecated in favor of `getGroupsSet()`.

The final `org.apache.hadoop.security.alias.CredentialProvider` fragment shows an abstract provider class with a public constructor and `isTransient()` returning whether the provider represents a transient store. The rest of that class belongs to a later chunk.

## Control Flow

Metrics source flow is pull-oriented. A registered `MetricsSource` receives a `MetricsCollector`, opens a record through `addRecord`, populates tags/counters/gauges/metrics through a `MetricsRecordBuilder`, and the `MetricsSystem` publishes snapshots to configured `MetricsSink` instances. Filters may run at source or sink boundaries by name/tag/record. Builder helpers such as `MetricStringBuilder` and `MetricsJsonBuilder` use the same builder methods but terminate in a diagnostic `toString()` representation.

Mutable metrics use a changed-flag/snapshot flow. Counter/gauge/stat/quantile objects mutate in source code paths, set changed state, and later write a snapshot into a record builder. The `all` flag controls whether unchanged metrics are emitted. Quantile and rolling-average APIs add extra rollover/estimator collection behavior, and `stop()`/`close()` are lifecycle hooks for background or retained state.

Metrics sink flow begins with `init(SubsetConfiguration)`, then repeated `putMetrics(record)` calls, periodic `flush()`, and optional `close()`. Rolling filesystem sink flow includes deriving roll intervals from configuration, computing initial and next flush times, writing metrics to a filesystem path, and rolling/forcing flushes based on clock state.

Rack mapping flow calls `resolve(names)` on a raw or cached mapper. Cached mapping resolves misses through the raw mapper and preserves results until full or targeted reload. Script/table mappings feed raw results from external configuration or data files. Socket factories create configured sockets through Java `SocketFactory` overloads.

ONC RPC enum flow is value conversion: wire integer values map to enum constants through `fromValue`, while outbound paths use `getValue()`.

Security flow is layered. `SecurityUtil` interprets configuration, expands principals, configures protocol security metadata, performs keytab login, constructs token service names, and wraps privileged execution. `UserGroupInformation` holds or locates the active identity, manages relogin, creates remote/proxy/test users, attaches token credentials, exposes groups, and runs actions through `Subject.doAs` semantics. `Credentials` is the portable container for tokens and secret keys that UGI can absorb or expose.

## State And Persistence Behavior

Metrics state is mostly process-local and in memory. `DefaultMetricsSystem` maintains singleton process state, source/MBean names, and mini-cluster mode. `MetricsRegistry` owns a mutable map of metrics and tags. Mutable metrics hold counters, gauges, sample stats, quantile estimators, rolling average windows, previous snapshots, changed flags, and in some cases thread-local state.

Metrics persistence occurs mainly through sinks. `FileSink` and `RollingFileSystemSink` write metrics to files or Hadoop filesystems; the rolling sink carries public scheduling and filesystem state. `GraphiteSink` and `StatsDSink` persist by sending metrics to external daemons over the network. `MetricsCache` keeps sink-side record state so sinks that need complete records can handle sparse updates.

Network mapping state is cached in `CachedDNSToSwitchMapping` and subclasses. It can become stale until reloaded, and diagnostics can expose a copy of host-to-switch mappings. Script and table mappings depend on configuration and external command/file state outside the Java heap.

Credentials persist in two forms: in-memory maps keyed by `Text` aliases, and serialized token storage streams/files using `Credentials.SerializedFormat`. Returned token/secret maps are documented as unmodifiable views, but byte arrays remain sensitive mutable data at the API boundary.

UGI state is both global and per-subject. Global state includes static configuration, initialized/security flags, login user, relogin scheduling, and metrics attachment. Per-user state is represented by a JAAS `Subject`, principals, token identifiers, tokens/credentials, authentication method, real-user relation for proxies, and group resolution results. The token-related environment variables indicate integration with external credential files or base64 token payloads.

## Dependencies And Integration Points

This API surface integrates with Java core APIs (`DataInput`, `DataOutput`, `IOException`, `InterruptedException`, `RuntimeException`, `Socket`, `SocketFactory`, `InetAddress`, `InetSocketAddress`, `URI`, `Subject`, privileged actions, JMX `ObjectName`, `Date`, `Calendar`, collections, and concurrency/lifecycle close hooks).

Hadoop dependencies include `Configuration`, `Configurable`, `Path`, `FileSystem`, `Text`, `MetricsInfo`, token and token identifier classes, security annotations/providers, `ZKUtil.ZKAuthInfo`, RPC/SASL classes, and Writable-style serialization. External dependencies include Apache Commons Configuration `SubsetConfiguration`, RE2/J regex patterns, ZooKeeper client SSL classes, SLF4J logging, Kerberos/JGSS JAAS concepts, and external metrics services such as Graphite, StatsD, Ganglia, and filesystem-backed logs.

Operational integration points are broad: daemon startup initializes metrics and UGI; RPC setup uses `SecurityUtil` and UGI authentication state; HDFS/YARN rack awareness uses `DNSToSwitchMapping`; token files move credentials between clients and services; metrics sinks ship operational data to local files and monitoring backends; MBeans expose metrics lifecycle controls to JMX.

## Risks And Edge Cases

- This is generated API XML, so implementation details such as synchronization, exact map types, serialization field order, retry behavior, and background thread management must be confirmed in Java sources when changing behavior.
- Metrics names, tag names, source names, and MBean names are compatibility-sensitive. Changes can break dashboards, alerts, JMX consumers, and sink parsers.
- `DefaultMetricsSystem` is process-global. Tests and embedded mini-clusters can interfere unless singleton state and source-name registries are reset carefully.
- Mutable metric snapshot semantics depend on changed flags and the `all` parameter. Missed `setChanged()` calls or overuse of `all=false` can hide metrics.
- Quantile, inverse quantile, and rolling average classes retain estimator/window state and expose lifecycle methods. Missing `stop()` or `close()` risks retained background resources or stale observations.
- Rolling file metrics output depends on clock calculations, filesystem append support, configured paths, and flush/roll intervals. Public mutable fields increase the risk of inconsistent test or subclass state.
- Pattern filters use RE2/J. Regex/glob compatibility and invalid patterns need explicit validation in configuration tests.
- Cached rack mappings can become stale after DNS, script, or table changes. Reload behavior, partial reload behavior, and single-switch optimizations must be covered.
- Script-based mapping depends on external process execution and configuration. Missing scripts, slow scripts, malformed output, and differing host/IP canonicalization can affect placement.
- Socket factory equality/hash behavior matters for connection pooling. Proxy configuration changes must be reflected consistently.
- ONC RPC enum `fromValue` methods must reject or handle unknown wire values predictably.
- Credentials expose sensitive tokens and secret-key byte arrays. Copying, map immutability, alias collisions, serialization format compatibility, and accidental logging are high-risk areas.
- `Credentials.addAll` and `mergeAll` likely differ on overwrite behavior; callers need tests that protect expected token/secret collision semantics.
- `GroupMappingServiceProvider.getGroups()` can fail with `IOException`; callers must tolerate empty/failing group providers and cache refresh races.
- `KerberosAuthException` carries keytab/ticket-cache details. Diagnostics are useful but can leak sensitive deployment paths if logged broadly.
- `SecurityUtil.setTokenServiceUseIp`, DNS resolution, and principal host expansion affect token identity and Kerberos service names. Behavior can change across IP/hostname, HA, proxy, and secure DNS environments.
- ZooKeeper SSL configuration must validate complete truststore/keystore inputs; partial configuration should fail early and clearly.
- UGI has substantial static global state. `setConfiguration`, `reset`, `setLoginUser`, relogin methods, and test hooks can affect every caller in the JVM.
- UGI proxy users must preserve real-user and real-authentication semantics. Incorrect handling can weaken authorization/audit trails.
- `getGroups()` is deprecated in favor of `getGroupsSet()`; new code should avoid list conversion unless primary-group ordering is required.
- Token and credential mutation on UGI has synchronization-sensitive APIs (`addTokenIdentifier`, auth method getters/setters are synchronized in the XML). Concurrency tests should cover simultaneous token additions and `doAs` usage.
- The `CredentialProvider` class is incomplete in this chunk; any conclusions about its full behavior must be deferred to later chunk research.

## Test Signals

Useful validation for code touching APIs in this chunk:

- Metrics core: source registration/unregistration, duplicate source naming, record builder chaining, context tag insertion, all counter/gauge numeric overloads, metric visitor dispatch, filter acceptance by name/tag/record, JSON/string builder output, and MXBean lifecycle methods.
- Metrics registry/mutable metrics: counter/gauge increment/decrement/set, changed-flag behavior, snapshot with `all=true` and `all=false`, stat min/max/stdev and timestamp behavior, rate sample aggregation, protocol-based rate initialization, quantile rollover, inverse quantile outputs, rolling average collection/close, and concurrent metric updates.
- Metrics sinks: configuration parsing, malformed configs, flush/close idempotence, file append support, rolling interval and next-flush calculations, StatsD/Graphite line formatting, network failure handling, and filesystem error behavior under `ignoreError`.
- MBeans/cache/server utilities: JMX object name construction including extra properties, unregister idempotence, cache update/get with and without tags, sparse metric update behavior, and parsing of server specs with default ports and malformed entries.
- Network mapping: raw and cached `resolve`, cache hit/miss behavior, full and targeted reloads, script/table configuration changes, unknown hosts, single-switch detection, topology dump content, and socket factory behavior with local bind addresses and SOCKS proxy settings.
- ONC RPC: enum round-trip for every known wire value and explicit tests for unknown values.
- Credentials: token and secret-key add/remove/count/map immutability, alias collision behavior, byte-array handling, read/write stream round trips, `Path` and `File` token-storage file round trips, all serialized formats, `addAll` versus `mergeAll`, and invalid/corrupt token-storage files.
- Group/id mapping: IOException propagation, cache refresh/add behavior, set/list consistency, unknown uid/gid behavior, and provider configuration prefix use.
- Kerberos/security utilities: principal expansion for `_HOST`, keytab login failure diagnostics, TGT original-ticket detection, token service build/parse with IP and hostname modes, security info provider lookup, `doAsLoginUser` and `doAsCurrentUser` exception propagation, secure DNS failure modes, privileged port boundary values, ZooKeeper auth parsing, and SSL configuration validation.
- UGI: static initialization/reset isolation, security-enabled mode selection, current/login user behavior, ticket-cache and keytab login/relogin flows, forced relogin throttling bypass, remote/proxy/test user creation, real-user and real-authentication results, token identifier and token mutation, credentials import/export, group retrieval including deprecated `getGroups`, equality/hash by subject, `doAs` checked/unchecked exception propagation, and logging helpers with token redaction expectations.

### subset-b-007239: lines 42862-48966

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 42862-48966

## Scope

This chunk is a Hadoop Common 3.5.0 JDiff public API slice. It begins inside `org.apache.hadoop.security.alias.CredentialProvider`, then covers security authorization, HTTP security filters, token and delegation-token APIs, the service lifecycle and service launcher contracts, and the first part of `org.apache.hadoop.util` utility APIs through `StringInterner`. The source is an API XML snapshot rather than Java implementation source, so the research is based on exposed classes, method contracts, state fields, documented control flow, persistence hooks, and compatibility signals.

## Purpose

The chunk documents infrastructure APIs used across Hadoop daemons, clients, command-line tools, and HTTP endpoints:

- Credential provider and ACL APIs abstract credential persistence, ACL string parsing, Writable serialization, and proxy-user authorization.
- HTTP security filters add CSRF prevention and `X-Frame-Options` response hardening for servlet deployments.
- Token APIs define client-side token encoding, token identifiers, selectors, renewer plugins, shared-secret generation, and delegation-token state management.
- Delegation-token web APIs extend `AuthenticatedURL` so HTTP clients can acquire, send, renew, and cancel Hadoop delegation tokens over HTTP/S.
- Service APIs define the shared lifecycle model for Hadoop services, composite service ordering, listener notification, failure recording, lifecycle history, and standardized service-launch exit codes.
- Utility APIs cover application classloader isolation, duration logging, IP-list membership, CRC implementations, reflection helpers, shell command execution, shutdown-hook ordering, and string interning.

## Important APIs, Types, And Functions

### Credential Providers

The visible tail of `org.apache.hadoop.security.alias.CredentialProvider` exposes the provider contract for credential storage. Implementations must be thread safe. Key methods are `flush()`, `getCredentialEntry(String)`, `getAliases()`, `createCredentialEntry(String, char[])`, and `deleteCredentialEntry(String)`, all IO-bearing where storage access may fail. The non-abstract password helpers `needsPassword()`, `noPasswordWarning()`, and `noPasswordError()` model providers whose backing store requires a password not found through normal mechanisms. `isTransient()` is documented for providers intended for temporary job access rather than long-term storage, such as user-backed providers. `CLEAR_TEXT_FALLBACK` is a public configuration-related constant.

`CredentialProviderFactory` is a service-loader based factory. `createProvider(URI, Configuration)` is the factory method implemented by concrete factories; `getProviders(Configuration)` resolves the configured provider path from `CREDENTIAL_PROVIDER_PATH` and returns the matching provider list.

### Authorization And Impersonation

`AccessControlList` represents a configured ACL and implements `Writable`. It can be built from a single ACL string of comma-separated users followed by comma-separated groups, or separate user and group strings. It exposes `addUser`, `addGroup`, `removeUser`, `removeGroup`, `getUsers`, `getGroups`, `isAllAllowed`, `isUserInList(UserGroupInformation)`, `isUserAllowed(UserGroupInformation)`, `getAclString`, `toString`, `write(DataOutput)`, and `readFields(DataInput)`. `WILDCARD_ACL_VALUE` models all-access ACLs. `USE_REAL_ACLS` is significant for proxied users: `isUserInList` treats `USE_REAL_ACLS + realUser` as a match for a proxied user.

`AuthorizationException` extends `AccessControlException` and deliberately suppresses stack-trace visibility for security. It overrides `getStackTrace()` and all `printStackTrace` variants, which is an API-level signal that callers should not rely on stack details for this exception.

`DefaultImpersonationProvider` implements `ImpersonationProvider` and `Configurable`. It reads proxy-user configuration with a configurable prefix, authorizes a `UserGroupInformation` plus remote `InetAddress`, and exposes helper methods for user, group, and IP configuration keys: `getProxySuperuserUserConfKey`, `getProxySuperuserGroupConfKey`, and `getProxySuperuserIpConfKey`. It also exposes current proxy group and host maps for inspection. `getTestProvider()` returns a synchronized singleton-style test provider.

`ImpersonationProvider` is the extension point. Implementations receive `init(String configurationPrefix)`, then authorize either `(UserGroupInformation, String remoteAddress)` or `(UserGroupInformation, InetAddress remoteAddress)`, and inherit `Configurable` setup through `setConf`/`getConf`.

### HTTP Security Filters

`RestCsrfPreventionFilter` implements `javax.servlet.Filter`. Its public surface includes `init(FilterConfig)`, `doFilter(ServletRequest, ServletResponse, FilterChain)`, `destroy()`, `getFilterParams(Configuration, String)`, `isBrowser(String userAgent)`, and `handleHttpInteraction(HttpServletRequest, HttpServletResponse, FilterChain)`. Constants define the user-agent header, browser-user-agent parameter, custom CSRF header parameter, methods-to-ignore parameter, and default header name. The intended flow is: detect browser-like requests, require the configured custom header on unsafe methods, and let configured ignored methods through.

`XFrameOptionsFilter` is another servlet `Filter`. It initializes from filter config, sets the `X-Frame-Options` response header in `doFilter`, exposes `getFilterParams(Configuration, String)`, and publishes `X_FRAME_OPTIONS` and `CUSTOM_HEADER_PARAM`.

`org.apache.hadoop.security.ssl.SSLChannelMode` is an enum-style public nested type from `DelegatingSSLSocketFactory`, exposed here with `values()` and `valueOf(String)`.

### Token Core

`SecretManager<T extends TokenIdentifier>` is the abstract base for issuing and validating token passwords. Implementations provide `createPassword(T)`, `retrievePassword(T)`, and `createIdentifier()`. The visible concrete helpers include `retriableRetrievePassword(T)`, `checkAvailableForRead()`, static `generateSecret()`, `validateSecretKeyLength(byte[])`, static password generation from identifier bytes and a `SecretKey`, and `createSecretKey(byte[])`. It depends on JCE `SecretKey` and logs through SLF4J. The nested `InvalidToken` exception is referenced by retrieval and verification APIs.

`Token<T extends TokenIdentifier>` is the client-side token representation and implements `Writable`. Constructors cover creating from an identifier plus `SecretManager`, raw identifier/password/kind/service fields, default deserialization, and copy construction. Core fields are exposed through `getIdentifier`, `getPassword`, synchronized `getKind`/`setKind`, `getService`/`setService`, and token cloning helpers. `privateClone(Text)` creates a token tied to a private service, while `isPrivate()` and `isPrivateCloneOf(Text)` differentiate public and private forms. Serialization and transport surfaces are `readFields`, `write`, `encodeToUrlString`, and `decodeFromUrlString`. Runtime operations `isManaged`, `renew(Configuration)`, and `cancel(Configuration)` delegate to token renewers and can raise IO or interruption.

`TokenIdentifier` is a `Writable` identifier contract. Implementations provide `getKind()` and `getUser()`. Base methods serialize to bytes with `getBytes()` and provide a cross-session tracking ID, documented as an MD5 of the identifier bytes.

`TokenInfo` is an annotation-style interface whose `value()` names the `TokenSelector` class for a token family. `TokenSelector<T>` chooses a token for a service from a token collection. `TokenRenewer` is the plugin contract for renew/cancel support: `handleKind(Text)`, `isManaged(Token<?>)`, `renew(Token<?>, Configuration)`, and `cancel(Token<?>, Configuration)`. `TrivialRenewer` is a base class for unmanaged token kinds; subclasses implement `getKind()`, while `isManaged` is false and renew/cancel are trivial.

### Delegation Token Manager

`AbstractDelegationTokenIdentifier` extends `TokenIdentifier` with delegation-token metadata: owner, renewer, real user, issue date, max date, sequence number, and master key ID. It provides setters/getters, equality/hash behavior, Writable serialization, `toString()`, and `toStringStable()`. `getUser()` resolves the encoded user or owner into a `UserGroupInformation`.

`AbstractDelegationTokenSecretManager<TokenIdent>` extends `SecretManager<TokenIdent>` and is the central stateful delegation-token manager. Its constructor takes intervals for key rolling, maximum token lifetime, renew interval, and expired-token scan interval. Public lifecycle and recovery APIs include `startThreads()`, `stopThreads()`, `reset()`, `isRunning()`, `addKey(DelegationKey)`, `getAllKeys()`, `getCurrentTokensSize()`, and `addPersistedDelegationToken(TokenIdent, long)`. The recovery method must be called before activation and marks tokens with unknown `DelegationKey`s as expired for cleanup.

The class exposes many protected hooks for durable storage and HA/externalized state, especially ZooKeeper-backed implementations: `storeNewMasterKey`, `removeStoredMasterKey`, `storeDelegationKey`, `updateDelegationKey`, `storeNewToken`, `removeStoredToken`, `updateStoredToken`, `storeToken`, `updateToken`, `removeExpiredStoredToken`, `logUpdateMasterKey`, `logExpireToken`, and `logExpireTokens`. It also exposes protected/current-id helpers for external storage: `getCurrentKeyId`, `incrementCurrentKeyId`, `setCurrentKeyId`, `getDelegationTokenSeqNum`, `incrementDelegationTokenSeqNum`, and `setDelegationTokenSeqNum`.

Validation and mutation APIs include `rollMasterKey()`, protected `createPassword(TokenIdent)`, `checkToken(TokenIdent)`, public `retrievePassword(TokenIdent)`, `verifyToken(TokenIdent, byte[])`, `renewToken(Token<TokenIdent>, String)`, `cancelToken(Token<TokenIdent>, String)`, `decodeTokenIdentifier(Token<TokenIdent>)`, and token tracking helpers `getTrackingIdIfEnabled` and `getTokenTrackingId`. Metrics support is exposed through `getTopTokenRealOwners(int)`, `addTokenForOwnerStats(TokenIdent)`, `syncTokenOwnerStats()`, and `getMetrics()`.

State fields are explicitly documented: `currentTokens` maps token identifiers to token information and is protected by the manager monitor; `allKeys`, `currentId`, and `delegationTokenSequenceNumber` are also monitor-protected; `tokenOwnerStats` tracks real-owner counts for metrics; `storeTokenTrackingId` controls whether tracking IDs are stored in token information; `running` is volatile; and `noInterruptsLock` prevents interruption of the update thread while held.

### Delegation Tokens Over HTTP

`DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` and is explicitly not thread safe. It uses `KerberosDelegationTokenAuthenticator` by default, with fallback to pseudo authentication. Constructors accept an optional `DelegationTokenAuthenticator` and/or `ConnectionConfigurator`. Static methods `setDefaultDelegationTokenAuthenticator` and `getDefaultDelegationTokenAuthenticator` change or read the default authenticator class. `setUseQueryStringForDelegationToken(boolean)` exists for WebHDFS backwards compatibility; otherwise delegation tokens are sent in the `DelegationTokenAuthenticator.DELEGATION_TOKEN_HEADER` header.

Its `openConnection` overloads authenticate a URL using either an embedded delegation token, an `AuthenticatedURL.Token`, or a `doAs` user. If a delegation token is present in the nested `Token`, that token takes precedence over the configured authenticator. It can select a delegation token from `Credentials` based on URL, obtain a new token with `getDelegationToken`, renew with `renewDelegationToken`, and cancel with `cancelDelegationToken`. Cancel operations are documented as not requiring authentication by the configured authenticator.

`DelegationTokenAuthenticator` wraps another `Authenticator`. It supports `setConnectionConfigurator`, `authenticate`, token acquisition, token renewal, and token cancellation, with overloads that include a `doAsUser`. Public constants define HTTP query and JSON field names: `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `DELEGATION_PARAM`, `TOKEN_PARAM`, `RENEWER_PARAM`, `SERVICE_PARAM`, `DELEGATION_TOKEN_JSON`, `DELEGATION_TOKEN_URL_STRING_JSON`, and `RENEW_DELEGATION_TOKEN_JSON`.

`KerberosDelegationTokenAuthenticator` adds SPNEGO plus delegation-token operations and falls back to `PseudoDelegationTokenAuthenticator` if the endpoint does not trigger SPNEGO. `PseudoDelegationTokenAuthenticator` accepts the user name from a query parameter, matching Hadoop Simple authentication's trust in `UserGroupInformation.getCurrentUser()`. The nested web `Token` extends `AuthenticatedURL.Token` and stores a Hadoop delegation token through `getDelegationToken()` and `setDelegationToken(...)`.

### Service Lifecycle

`Service` is the core lifecycle interface and extends `Closeable`. Its state machine is `NOTINITED -> INITED -> STARTED -> STOPPED`, exposed through enum `Service.STATE`, whose `getValue()` returns a numeric code. `init(Configuration)` must move from `NOTINITED` to `INITED`, or call `stop()` and enter `STOPPED` on failure. `start()` must move from `INITED` to `STARTED`, or stop on failure. `stop()` must be a no-op if already stopped and should be robust regardless of partially initialized fields. `close()` must relay to `stop()` and is documented to never throw `IOException`. Read APIs include name, config, state, start time, failure cause/state, lifecycle history, blockers, and `waitForServiceToStop(long)`.

`AbstractService` is the base implementation. It manages state transitions, failure recording via `noteFailure(Exception)`, listener registration, global listener registration, start time, lifecycle history snapshots, blockers, and `close()` relay. Subclasses implement or override `serviceInit(Configuration)`, `serviceStart()`, and `serviceStop()`, each called once per instance lifecycle by the base transition logic. The docs emphasize non-reentrancy guarantees around these hooks and require `serviceStop()` to tolerate failures and null internal fields.

`CompositeService` extends `AbstractService` and manages child services. It exposes a cloned snapshot from `getServices()`, protected `addService`, `addIfService(Object)`, `removeService`, and lifecycle hooks that initialize, start, and stop children. `STOP_ONLY_STARTED_SERVICES` documents a shutdown policy tradeoff: close everything or only services that reached started state, while still stopping children that fail during init/start.

`LifecycleEvent` is a serializable record with public `time` and `state` fields. `LoggingStateChangeListener` logs state changes at INFO level. `ServiceStateChangeListener` is called after state changes, on the thread that initiated the transition, while the service is in a synchronized section; the docs warn that long-lived listener work can block transitions and listener-spawned calls back into the service can deadlock.

`ServiceOperations` is a final static helper with `stop(Service)` and `stopQuietly` overloads. It catches and logs exceptions for cleanup paths but not `Throwable`s. The `commons-logging` overload is deprecated in favor of the SLF4J `Logger` overload. `ServiceStateException` is a runtime exception implementing `ExitCodeProvider`; it can derive an exit code from a cause or use `EXIT_SERVICE_LIFECYCLE_EXCEPTION`, and its `convert` helpers wrap arbitrary failures as runtime exceptions.

`ServiceStateModel` is the standalone thread-safe state-machine helper. It exposes `getState`, `isInState`, `ensureCurrentState`, synchronized `enterState(STATE)`, static `checkStateTransition`, static `isValidStateTransition`, and `toString`.

### Service Launcher

`AbstractLaunchableService` extends `AbstractService` and implements `LaunchableService`. Its base `bindArgs(Configuration, List<String>)` logs arguments at debug and returns the same configuration, while `execute()` returns success (`0`).

`LaunchableService` extends `Service` for command-line managed services. `bindArgs(Configuration, List<String>)` is called before `init(Configuration)` and may mutate or replace the configuration, often to instantiate `YarnConfiguration` or another subclass that loads default resources. `execute()` is called after `start()` and its return value becomes the process exit code unless an exception overrides it.

`HadoopUncaughtExceptionHandler` is intended for installation through `Thread.setDefaultUncaughtExceptionHandler`. Standard exceptions are logged or delegated; `Error` causes process shutdown because the system state is considered unknown.

`LauncherExitCodes` standardizes exit codes. It includes success, generic failure, client-initiated shutdown, launch failure, interrupted, argument/usage/configuration errors, unauthorized/forbidden/not-found style client errors, connectivity and service-side failures, unsupported version, service creation failure, and lifecycle exception. The docs map many codes loosely to HTTP status classes while preserving Unix `0` for success.

`ServiceLaunchException` extends `ExitUtil.ExitException` and implements both `ExitCodeProvider` and `LauncherExitCodes`. Constructors support exit-code plus cause, message, `String.format` style varargs in English locale, and explicit cause plus format. The package-level launcher docs describe the broader flow: instantiate a service with a no-arg or string constructor, load `--conf <file>` local configuration files, call `bindArgs` for launchable services, initialize, start, execute or wait for stop, stop on completion, convert exceptions or exit-code-providing exceptions to `ExitException`, and terminate through `ExitUtil`. Interrupt handling uses an escalator that tries service shutdown on first signal and halts on a repeated signal.

### Tools And Utility Classes

`org.apache.hadoop.tools.TableListing.Justification` appears as an enum-style nested public type with `values()` and `valueOf(String)`. Empty package declarations for `tools.protocolPB` and `tracing` are present in the snapshot.

`ApplicationClassLoader` extends `URLClassLoader` for application isolation. It prefers application JARs over the parent loader except for system classes. Constructors accept URLs or a classpath string, parent loader, and system-class patterns. `getResource`, `loadClass`, protected synchronized `loadClass(String, boolean)`, and static `isSystemClass(String, List<String>)` define loading behavior. `SYSTEM_CLASSES_DEFAULT` lists JDK, Hadoop, resources, and selected third-party classes that should remain parent/system loaded.

`OperationDuration` records start and finished times. It exposes `finished()`, `value()` in milliseconds, `asDuration()`, `getDurationString()`, `humanTime(long)`, and `toString()`. `DurationInfo` extends it and implements `AutoCloseable`, logging the formatted operation text at construction and the final duration on `close()`, which makes it a try-with-resources timing helper.

`IPList` is a simple membership interface with `isIn(String ipAddress)`. `Shell.OSType` is exposed as an enum-style nested type with `values()` and `valueOf(String)`. `Progressable` is a callback interface with `progress()`.

`PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum`. Each has `getValue`, `reset`, `update(int)`, `update(byte[], int, int)`, and protected `mod(int)`. They are pure Java checksum implementations used where native or JDK alternatives are not desired.

`ReflectionUtils` provides common reflection helpers: `setConf(Object, Configuration)`, overloaded `newInstance(Class<T>, Configuration)` and `newInstance(Class<T>, Configuration, Class<?>[])`, contention tracing toggles, thread-info printing/logging, class lookup by name, deep copy through serialization, `cloneWritableInto`, and inherited field/method collection. The `commons-logging` `logThreadInfo` overload is deprecated in favor of the SLF4J overload.

`Shell` is an abstract base for running native commands. It provides constructors with timeout and parent-environment inheritance, Java version checks, Windows command-line length checks, `bashQuote`, group/user command builders, permission/owner/symlink/readlink/process/signal command builders, environment variable regex access, script extension helpers, run-script command construction, Hadoop home and qualified bin discovery, and Windows `winutils` discovery. Protected instance setup includes `setEnvironment(Map)`, `setWorkingDirectory(File)`, `run()`, abstract `getExecString()`, and abstract `parseExecResult(BufferedReader)`. Runtime inspection APIs expose environment values, current process, exit code, waiting thread, and timeout state. Static `execCommand` overloads cover common one-shot command execution with optional environment and timeout. Static process registry helpers `destroyAllShellProcesses()` and `getAllShells()` support global cleanup. Constants expose OS booleans, command strings, Hadoop home property/env names, Windows launch lock, `ENV_NAME_REGEX`, `TOKEN_SEPARATOR_REGEX`, deprecated misspelled `WINDOWS_MAX_SHELL_LENGHT`, deprecated nullable `WINUTILS`, and `isSetsidAvailable`.

`ShutdownHookManager` is a final singleton that registers a single JVM shutdown hook and then runs Hadoop-registered hooks in priority order. `addShutdownHook` overloads accept priority and optional timeout, `removeShutdownHook`, `hasShutdownHook`, `isShutdownInProgress`, and `clearShutdownHooks` manage/query the registry. `TIMEOUT_MINIMUM` and `TIME_UNIT_DEFAULT` define timeout policy, and default hook timeout comes from `CommonConfigurationKeysPublic.SERVICE_SHUTDOWN_TIMEOUT`.

`StringInterner` begins at the end of the chunk. The visible `strongIntern(String)` method returns the representative instance for equal strings; later methods continue outside this chunk.

## Control Flow

Credential-provider control flow is provider-path resolution followed by provider-specific CRUD. `CredentialProviderFactory.getProviders(conf)` reads configured URIs, locates factories with a service-loader mechanism, and asks them to create providers. Mutating credential operations are not durable until `flush()` succeeds.

Authorization flow starts with ACL string parsing, then membership checks against explicit users/groups, wildcard ACLs, and special real-user ACL entries for proxied users. Proxy authorization loads prefix-scoped proxy-user rules, then validates both effective user/group authorization and source host/IP authorization before allowing impersonation.

HTTP filter flow is servlet-chain mediation. `RestCsrfPreventionFilter.doFilter` delegates to `handleHttpInteraction`, classifies the user agent, skips configured methods, requires the custom header for browser-originating state-changing requests, and either rejects or continues the chain. `XFrameOptionsFilter.doFilter` sets the configured frame-options header before continuing the chain.

Token flow has a clear separation of public identifier, private password, and service/kind metadata. A `SecretManager` creates a token password from an identifier and secret key; clients serialize or URL-encode `Token` instances; renew/cancel operations are routed by token kind to a `TokenRenewer`. `TokenIdentifier.getTrackingId()` gives a stable correlation key without exposing the password.

Delegation-token manager flow is stateful and time driven. Before service activation, previously persisted keys and tokens are loaded through `addKey` and `addPersistedDelegationToken`. `startThreads()` activates key rolling and expired-token cleanup. New token creation increments sequence state, signs identifiers with the current master key, stores token information, and optionally stores tracking IDs. Renewal verifies the token and renewer, extends renew time within max lifetime, and updates persistent storage. Cancellation removes active and stored token state. Expiry scanning removes expired tokens and calls storage/logging hooks.

HTTP delegation-token flow layers token operations over `AuthenticatedURL`. A connection first prefers an already stored delegation token; otherwise it authenticates with the configured authenticator. Token acquisition and renewal require authentication; cancellation is explicitly unauthenticated by the configured authenticator. `doAs` overloads propagate proxy-user intent to the server endpoint.

Service lifecycle flow is strict. `init` transitions from `NOTINITED` to `INITED` and calls `serviceInit`; `start` transitions from `INITED` to `STARTED` and calls `serviceStart`; `stop` transitions to `STOPPED` and calls `serviceStop` once. Failures are recorded with the state in which they occurred and may trigger stop. Listeners are invoked synchronously in the transition path. `waitForServiceToStop(0)` waits indefinitely.

Composite-service flow applies the same lifecycle to child services and handles partial failures by stopping children that failed during init or start. Launcher flow builds configuration, strips and applies `--conf <file>` arguments, optionally binds command arguments through `LaunchableService.bindArgs`, initializes and starts the service, then either waits for a regular service to stop or calls `execute()` for a launchable service. Return codes and exceptions are normalized through `ExitCodeProvider`, `ExitUtil.ExitException`, and `ServiceLaunchException`.

Utility control flow is mostly wrapper/template based. `ApplicationClassLoader` tests system-class patterns before deciding parent versus application loading. `DurationInfo` starts logging at construction and emits elapsed time on `close()`. `ReflectionUtils.newInstance` creates and configures objects. `Shell` subclasses provide command vector and parse stdout while the base class manages process launch, timeout, environment, working directory, and process registry. `ShutdownHookManager` sorts registered hooks by priority and applies per-hook timeout policy.

## State And Persistence Behavior

Credential providers may be persistent or transient. The API explicitly separates in-memory mutation from durable storage by requiring `flush()`. Providers may also require an external password; `needsPassword()` and the warning/error text are part of the user-facing state surface.

`AccessControlList` persists through Hadoop `Writable` serialization. Its user/group collections are returned as unmodifiable snapshots by contract. ACL state also has a special wildcard all-allowed mode and real-user proxy matching behavior.

Token persistence is split across several layers. `Token` and `TokenIdentifier` are `Writable`, plus `Token` has URL-safe string encoding for transport. Delegation-token identifiers carry owner, renewer, real user, issue/max dates, sequence number, and master key ID in serialized form. `AbstractDelegationTokenSecretManager` maintains in-memory maps for active tokens and keys, but provides protected hooks for edit logs, ZooKeeper, or other durable stores. Recovery APIs must run before activation. Unknown-key persisted tokens are marked expired and later cleaned up.

Service state is in-memory but observable: current state, lifecycle history, start time, blockers, first failure cause, and failure state. `LifecycleEvent` is serializable, but the lifecycle history API returns a snapshot and is not itself a persistence layer. `CompositeService` holds child service references and exposes cloned lists to avoid callers mutating live state.

Launcher configuration state is assembled before service initialization. The package docs state that `--conf <file>` pairs are read from local files, merged in command-line order with later files applied later, and removed from the argument list passed to services. Launchable services may mutate or replace the configuration before `init`.

`Shell` has both per-instance mutable process state and process-wide static state. Per-instance state includes environment, working directory, process, exit code, waiting thread, timeout interval, timeout flag, and parent-environment inheritance. Static state includes OS detection, command constants, winutils discovery, setsid availability, and the global live-shell registry. `ShutdownHookManager` owns a process-wide hook registry and shutdown-in-progress flag. `OperationDuration` stores start and finish timestamps; `DurationInfo` adds logging side effects.

## Dependencies And Integration Points

This chunk depends heavily on Hadoop Common core types: `Configuration`, `UserGroupInformation`, `Credentials`, `Text`, `Writable`, `DelegationKey`, `Metrics2Util.NameValuePair`, `ExitUtil`, and `ExitCodeProvider`. It also integrates with Java platform APIs: servlet filters, `HttpURLConnection`, `URLClassLoader`, JCE `SecretKey`, `DataInput`/`DataOutput`, `Closeable`, `Thread.UncaughtExceptionHandler`, `Process`, `TimeUnit`, `Checksum`, reflection APIs, and SLF4J logging.

Security integration points include credential-provider service loading, proxy-user configuration keys, servlet container filter configuration, SPNEGO/pseudo HTTP authentication, token-renewer plugins, token selectors registered through `TokenInfo`, and delegation-token secret-manager persistence hooks for HA stores such as ZooKeeper.

Service integration points include global state-change listeners, shutdown hooks, command-line service launching, signal/interrupt escalation, `--conf` local file loading, and exception-to-exit-code conversion. Utility integration points include application classpath isolation, shell command execution for platform-specific operations, and JVM shutdown ordering.

## Risks And Compatibility Notes

- `AuthorizationException` intentionally hides stack traces; diagnostics must rely on messages and surrounding logs.
- ACL parsing and proxy-user real-user matching are security sensitive. Regressions can either block legitimate proxy use or allow unintended impersonation.
- `RestCsrfPreventionFilter` security depends on accurate browser detection, ignored-method configuration, and consistent custom-header enforcement.
- `DelegationTokenAuthenticatedURL` is documented as not thread safe; sharing instances across callers can corrupt authentication/delegation-token state.
- Sending delegation tokens in query strings exists for WebHDFS compatibility but increases exposure through URLs, logs, and caches compared with headers.
- Delegation-token manager methods document monitor-protected state. Implementations or subclasses that bypass locking around `currentTokens`, `allKeys`, `currentId`, or sequence state risk duplicate sequence numbers, stale keys, failed renewals, or accepting expired tokens.
- Persistent token recovery must occur before `startThreads()`. Loading persisted tokens after activation can race with key rolling and cleanup.
- `TokenIdentifier.getTrackingId()` is documented as MD5 of identifier bytes; it is for correlation, not cryptographic proof.
- Service listeners run synchronously during state transitions. Slow listeners or callbacks into the same service can delay startup/shutdown or deadlock.
- `Service.stop()` must tolerate partially initialized state. Many lifecycle failures route through stop, so null-sensitive cleanup code can mask the original failure.
- Launcher exit-code conversion gives priority to exceptions over normal return codes. Tests should cover both `ExitException` and generic exception paths.
- `Shell.WINUTILS` is deprecated because it may be null; callers should use exception-raising getters. Windows command length and process launch locking remain platform-sensitive.
- Deprecated APIs in this chunk include the `ServiceOperations.stopQuietly(org.apache.commons.logging.Log, Service)` overload, `ReflectionUtils.logThreadInfo` with commons logging, `Shell.isJava7OrAbove`, the misspelled `WINDOWS_MAX_SHELL_LENGHT`, and nullable `Shell.WINUTILS`.

## Test Signals

Relevant tests should assert API behavior rather than XML shape:

- Credential provider tests should cover provider-path resolution, transient versus persistent providers, password-required warnings/errors, create/delete/list/get behavior, duplicate alias rejection, and durability only after `flush()`.
- ACL and impersonation tests should cover wildcard ACLs, separate and combined user/group ACL parsing, Writable round trips, proxied real-user entries with `USE_REAL_ACLS`, host/IP constraints, and negative authorization cases.
- HTTP filter tests should cover browser versus non-browser user agents, ignored HTTP methods, missing/valid custom CSRF headers, custom filter parameters, and `X-Frame-Options` header injection.
- Token tests should cover Writable and URL-string round trips, kind/service mutation, private clone semantics, token selector lookup, renewer dispatch, unmanaged `TrivialRenewer` behavior, and missing token class decode behavior.
- Delegation-token secret-manager tests should cover key rolling, token issue/renew/cancel, expired-token cleanup, persisted key/token recovery before activation, unknown-key recovery cleanup, token owner metrics, tracking ID storage, and concurrent access around monitor-protected maps.
- Delegation-token HTTP tests should cover default Kerberos authenticator selection, pseudo fallback, header versus query-string token transmission, `doAs` propagation, credential token selection by URL, and unauthenticated cancel semantics.
- Service lifecycle tests should cover valid and invalid state transitions, idempotent stop, failure cause/state recording, listener registration/unregistration, listener deadlock avoidance by design, lifecycle history snapshots, blockers, `waitForServiceToStop`, `CompositeService` child ordering, and cleanup after child init/start failure.
- Launcher tests should cover `--conf` local file loading and stripping, `bindArgs` replacing configuration, `execute()` return-code propagation, exception-to-exit-code conversion, signal/shutdown hook behavior, and uncaught `Error` handling.
- Utility tests should cover classloader system-class inclusion/exclusion patterns, duration value before and after `finished()`, CRC known vectors, reflection configuration injection and inherited member discovery, shell command timeout/exit-code/environment behavior, Windows-specific winutils failures, shutdown-hook priority/timeout ordering, and string interning identity.

### subset-b-007240: lines 48967-50813

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 48967-50813

## Scope

This chunk is the tail of the Apache Hadoop Common 3.5.0 JDiff API XML. It begins inside `org.apache.hadoop.util.StringInterner`, continues through the end of `org.apache.hadoop.util`, covers the public Bloom filter API package, a Curator package summary, and the public functional helper APIs under `org.apache.hadoop.util.functional`, then closes with an empty `org.apache.hadoop.util.hash` package and the closing `</api>`.

Because the source is JDiff XML, this document describes the exported API contract rather than full method bodies. Control-flow and state notes are inferred only from signatures, inheritance, serialization methods, and Javadocs present in this chunk.

## Purpose

The chunk documents utility APIs used across Hadoop Common rather than one cohesive runtime subsystem. The covered APIs fall into five groups:

- General Hadoop utilities: string interning, OS resource introspection, command-line `Tool` execution, binary prefix parsing/formatting, checksum type identity, and build/version metadata.
- Probabilistic set-membership utilities: standard, counting, dynamic, and retouched Bloom filters plus the hash adapter and selective-removal scheme constants.
- Curator integration marker package: package-level documentation for ZooKeeper Curator utilities.
- Functional and asynchronous I/O helpers: checked-exception-friendly future handling, option propagation into filesystem builders, closeable task-pool submission, and `RemoteIterator` adapters.
- Package boundary metadata for `org.apache.hadoop.util.hash`, which is present here only as an empty package entry.

These APIs provide reusable infrastructure for Hadoop command-line tools, filesystem/client code, distributed service diagnostics, probabilistic metadata structures, and asynchronous filesystem operations.

## Important APIs, Types, and Functions

`StringInterner` is partially covered. The visible methods are `weakIntern(String)` and `internStringsInArray(String[])`, with the preceding `strongIntern` documentation tail also visible. The API distinguishes strong interning, which retains a strong reference and prevents collection, from weak interning, which uses `String.intern()` without retaining application-level strong references. `internStringsInArray()` mutates the supplied array in place and returns the same array.

`SysInfo` is an abstract public plugin for system resource information. `newInstance()` returns a default OS-specific implementation or throws `UnsupportedOperationException` when the OS cannot be determined. Abstract getters expose total and available virtual/physical memory, logical processor count, physical core count, CPU frequency, cumulative CPU time, CPU usage percentage, used virtual cores, aggregate network bytes read/written, and aggregate storage bytes read/written. CPU percentage and vcore usage may return `-1` when unavailable.

`Tool` is the standard Hadoop command interface. It extends `org.apache.hadoop.conf.Configurable` and defines `run(String[] args)`, returning a process-style exit code and allowing checked exceptions. The Javadoc establishes the integration contract: generic Hadoop options should be delegated to `ToolRunner`, while the implementation handles application-specific arguments.

`ToolRunner` provides static execution and utility methods. `run(Configuration, Tool, String[])` parses generic arguments, updates the tool configuration, and invokes `Tool.run()`. `run(Tool, String[])` delegates using the tool's current configuration. `printGenericCommandUsage(PrintStream)` emits generic option help. `confirmPrompt(String)` reads an interactive response and returns true for case-insensitive `y` or `yes`.

`StringUtils.TraditionalBinaryPrefix` is represented as a public static enum in the XML. It exposes `values()`, name-based `valueOf(String)`, symbol-based `valueOf(char)`, `string2long(String)`, and `long2String(long, String, int)`. Public final fields `value`, `symbol`, `bitShift`, and `bitMask` define each prefix. The documented prefixes are traditional binary units from kilo through exa, with case-insensitive symbols; parsing examples show suffix multiplication by powers of 1024.

`DataChecksum.Type` is represented as a public static enum with `values()`, name-based `valueOf(String)`, id-based `valueOf(int)`, and public final fields `id` and `size`. This is the API-visible identity layer for checksum algorithms and checksum byte sizes.

`VersionInfo` exposes protected instance getters and public static getters for Hadoop build metadata: version, Git revision, branch, compile date, user, repository URL, source checksum, build version, protoc version, and compile platform. `main(String[])` is public and static, indicating a command-line reporting entry point.

`BloomFilter` extends `Filter` and supports default deserialization construction, parameterized construction with vector size, number of hash functions, and hash type, plus `add(Key)`, `and(Filter)`, `or(Filter)`, `xor(Filter)`, `not()`, `membershipTest(Key)`, `toString()`, `getVectorSize()`, `write(DataOutput)`, and `readFields(DataInput)`. The contract is classic Bloom-filter behavior: compact set membership, no false negatives for normal insertion/query use, and possible false positives.

`CountingBloomFilter` is a final `Filter` implementation with the same constructor shape and logical operations as `BloomFilter`, plus `delete(Key)` and `approximateCount(Key)`. The API documents a small counter width: inserting the same key more than 15 times can overflow all associated positions, increasing error rates. Deletion is documented as a no-op when the key is not considered present, but underflow can later reduce approximate counts below the true count with a false-negative probability.

`DynamicBloomFilter` extends `Filter` and adds a parameterized constructor `(vectorSize, nbHash, hashType, nr)`, where `nr` is the maximum number of keys per row. Its contract is a matrix of standard Bloom filters that adds rows as the recorded set grows and no active row can accept more keys.

`HashFunction` is a final helper that maps a `Key` into multiple integer positions. The constructor takes the maximum returned value, number of hash values, and hash algorithm type. `hash(Key)` returns the integer positions. `clear()` is explicitly a no-op.

`RemoveScheme` is a public interface used by retouched Bloom filters. It exports short constants `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`, representing strategies for selecting a bit to clear when removing false positives.

`RetouchedBloomFilter` is a final subclass of `BloomFilter` and implements `RemoveScheme`. It adds false-positive tracking through overloaded `addFalsePositive()` methods for a single `Key`, `Collection<Key>`, `List<Key>`, and `Key[]`. `selectiveClearing(Key, short)` applies a removal scheme to clear bits for a known false positive. It retains writable serialization through `write(DataOutput)` and `readFields(DataInput)`.

`CloseableTaskPoolSubmitter` implements `TaskPool.Submitter` and `Closeable`. It wraps an `ExecutorService`, exposes `getPool()`, submits `Runnable` tasks as `Future<?>`, and shuts the pool down in `close()`. Its purpose is explicit thread-pool lifecycle management.

`FutureIO` is a final utility class for futures and checked exceptions. It includes `awaitFuture(Future<T>)`, timed `awaitFuture(Future<T>, long, TimeUnit)`, untimed and duration-bounded `awaitAllFutures(Collection<Future<T>>...)`, `cancelAllFuturesAndAwaitCompletion(Collection<Future<T>>, boolean, Duration)`, overloads of `raiseInnerCause()` for `ExecutionException` and `CompletionException`, `unwrapInnerException(Throwable)`, `propagateOptions()` overloads for `FSBuilder`, and `eval(CallableRaisingIOE<T>)`. The key contract is that future failures are unwrapped so `IOException`, `RuntimeException`, `Error`, cancellation, timeout, and interruption are surfaced in caller-friendly forms.

`RemoteIterators` is a final utility class for adapting and composing Hadoop `RemoteIterator` instances. It creates iterators from singletons, `Iterator`, `Iterable`, arrays, long ranges, mapping functions, filters, casts, closeable wrappers, and halt predicates. It also converts remote iterators to `List` or array, applies a checked-exception consumer with `foreach()`, and performs cleanup with optional statistics logging and close propagation.

## Control Flow

`ToolRunner` defines the command startup flow expected by Hadoop CLI applications. A caller provides a `Configuration`, a `Tool`, and raw arguments. `ToolRunner` parses generic Hadoop command-line options, mutates or creates the configuration, sets it on the tool, and then delegates the remaining application arguments to `Tool.run()`. The return value is the tool's process-style exit code.

`SysInfo` flow is implementation-selected. Callers ask `SysInfo.newInstance()` for the OS default, then repeatedly call abstract metric getters. The API separates instantaneous or sampled values, such as CPU usage percentage, from cumulative counters, such as cumulative CPU time and aggregate I/O byte counters. Unavailable sampled metrics are represented by sentinel `-1` values rather than exceptions.

`TraditionalBinaryPrefix` parsing first trims input and then interprets an optional binary-prefix suffix. Formatting reverses that by selecting an appropriate binary prefix and applying the requested unit and decimal precision. The enum fields expose the exact multiplier and bit-mask metadata used by the conversion layer.

The Bloom filter family has a common lifecycle: construct an empty filter, add keys through `add(Key)`, query with `membershipTest(Key)`, combine compatible filters with boolean operations, and optionally serialize through `write()`/`readFields()`. Counting filters add deletion and approximate count retrieval; dynamic filters add row-growth when the active row reaches `nr`; retouched filters add a second phase where observed false positives are recorded and selected bits are cleared according to a removal scheme.

`FutureIO.awaitFuture()` and `awaitAllFutures()` block on one or more futures, unwrap `ExecutionException` or `CompletionException`, and rethrow meaningful causes. Interruption while waiting becomes `InterruptedIOException`; future cancellation remains `CancellationException`; timed waiting may raise `TimeoutException`. `cancelAllFuturesAndAwaitCompletion()` first cancels every future with a caller-selected interrupt flag, then waits up to a duration and returns futures that still completed successfully while ignoring thrown exceptions and timeout.

`FutureIO.propagateOptions()` scans a `Configuration` for keys under optional and mandatory prefixes and applies the stripped options to an `FSBuilder`. The documented stripping rules convert keys such as `fs.example.s3a.option` to `s3a.option`, `fs.example.fs.io.policy` to `fs.io.policy`, and `fs.example.something` to `something`. The overload with separate optional and mandatory prefixes applies both modes to the same builder.

`RemoteIterators` composes lazy iteration. Source adapters provide a `RemoteIterator<T>` interface over local objects, Java iterators, arrays, or numeric ranges. Mapping and type-casting wrappers transform each yielded value. Filtering may advance the source in `hasNext()` to find the next accepted value, or perform that work on demand in `next()` if `hasNext()` is skipped. Closing wrappers propagate close to any closeable source iterator and also close an extra supplied resource. Haltable wrappers consult a checked-exception boolean predicate so long-running iteration can stop quickly.

## State and Persistence Behavior

The XML itself is generated API metadata and has no runtime persistence behavior. The APIs it describes expose several stateful runtime contracts.

`StringInterner` state is process-local interning state. Strong interning deliberately retains references and can grow memory retention; weak interning avoids retaining the original object strongly. `internStringsInArray()` mutates caller-owned array state in place.

`SysInfo` has no persistent state in the public contract, but implementations are expected to observe OS state and counters. Some values are static hardware/container properties, while CPU usage and I/O counters depend on sampling and operating-system support.

`VersionInfo` reads build-time metadata embedded in the Hadoop artifact. The protected instance getters indicate an instance-backed metadata source, while the public static getters expose process-wide component build information to callers and command-line tools.

Bloom filters are explicitly stateful and serializable through Hadoop's `DataOutput`/`DataInput` pattern. `BloomFilter` persists the bit vector and filter parameters. `CountingBloomFilter` persists counter state and can be affected by overflow or underflow. `DynamicBloomFilter` persists multiple row filters and insertion thresholds. `RetouchedBloomFilter` persists both the base Bloom filter state and the additional false-positive information used for selective clearing.

`CloseableTaskPoolSubmitter` owns an `ExecutorService` lifecycle. Its durable state is not persisted, but the object controls whether the executor can accept more work and whether threads are shut down through `close()`.

`FutureIO` is stateless, but it controls observable state transitions in futures by waiting, cancelling, or propagating exceptions. It also mutates `FSBuilder` state when propagating configuration options.

`RemoteIterators` wrappers are stateful during traversal. Filtering wrappers may cache the next accepted element between `hasNext()` and `next()`. Range iterators track the current long. Closing wrappers track resources that should be closed after use. Wrappers may preserve and expose underlying `IOStatisticsSource` statistics so statistics survive transformation chains.

## Dependencies and Integration Points

The utility APIs integrate with `org.apache.hadoop.conf.Configuration`, `Configurable`, `GenericOptionsParser`, `FSBuilder`, `RemoteIterator`, `IOStatisticsSource`, and Hadoop's checked-exception functional interfaces such as `CallableRaisingIOE`, `FunctionRaisingIOE`, and `ConsumerRaisingIOE`.

Command-line integration is through `Tool` and `ToolRunner`, which are the bridge between Hadoop generic options and application-specific drivers. The Javadoc example references MapReduce-era classes such as `JobConf`, `JobClient`, and `RunningJob`, showing that the contract is intended for both Common and MapReduce tools.

System and build diagnostics integrate through `SysInfo` and `VersionInfo`. Resource managers, daemons, tests, and command-line diagnostics can depend on the stable public getters for memory, CPU, I/O, and build metadata.

Bloom filters depend on `org.apache.hadoop.util.bloom.Key`, `Filter`, `org.apache.hadoop.util.hash.Hash`, Java collections, and Hadoop writable-style serialization via `DataInput`/`DataOutput`. They are reusable across any subsystem needing approximate membership or compact cache summaries.

`FutureIO` integrates asynchronous Java concurrency (`Future`, `CompletableFuture`, `ExecutionException`, `CompletionException`, `CancellationException`, `TimeoutException`, `Duration`, `TimeUnit`) with Hadoop's `IOException`-oriented filesystem APIs. It also promotes APIs from `org.apache.hadoop.fs.impl.FutureIOSupport` into the public utility namespace for application code.

`RemoteIterators` integrates local Java iteration sources with Hadoop remote listing APIs. The package documentation explicitly notes that Hadoop filesystem APIs raise `IOException`, which is why the functional package provides checked-exception-capable alternatives to `java.util.function`.

The Curator package appears here only with package-level documentation stating that it provides utilities for Curator ZooKeeper interaction. The empty hash package marker indicates that the public API for `org.apache.hadoop.util.hash` is either absent from this chunk or contains no documented public types here.

## Risks and Edge Cases

`StringInterner` strong interning can retain data indefinitely, so it is risky for high-cardinality or untrusted strings. `internStringsInArray()` mutates its argument, which can surprise callers that expect a copy.

`SysInfo` values are platform-dependent. `newInstance()` can fail for unsupported OS detection, and CPU usage or vcore usage may be unavailable. Tests and callers must accept sentinel values and should not assume every metric exists on every platform or container environment.

`ToolRunner.confirmPrompt()` performs interactive I/O and only treats `y` or `yes` as affirmative. Automation using Hadoop tools needs to avoid unexpected prompts or provide input explicitly.

`TraditionalBinaryPrefix.string2long()` can overflow if a large numeric prefix is multiplied by a binary unit. Case-insensitive symbols are convenient but can mask invalid user input if validation is weak around suffix handling.

Checksum type lookup by integer id must remain compatible with serialized data and wire protocols. Unknown ids or size mismatches are compatibility-sensitive because checksum metadata is used in storage and data-transfer paths.

Bloom filters have inherent false-positive risk. Counting Bloom filters add overflow risk after repeated insertion of the same key and possible underflow effects after deletion, including approximate counts lower than the true count. Retouched Bloom filters intentionally trade selected false-positive removal for possible false negatives, so they are not appropriate where classic Bloom-filter "no false negatives" behavior is required after retouching.

Boolean operations on Bloom filters are only meaningful for compatible filters. The API signatures accept `Filter`, so implementations must defend against mismatched vector sizes, hash counts, hash types, or incompatible subclasses.

`FutureIO` can hide subtle concurrency behavior if callers do not distinguish thread interruption, future cancellation, task failure, and timeout. Its documented behavior preserves `CancellationException`, converts waiting interruption to `InterruptedIOException`, and unwraps runtime errors, so callers need tests for each case. `cancelAllFuturesAndAwaitCompletion()` deliberately ignores exceptions and timeout, which is useful for cleanup but risky if used where failures must be reported.

`FutureIO.propagateOptions()` relies on prefix naming and dot-segment stripping. Misconfigured prefixes can silently push wrong optional or mandatory settings into an `FSBuilder`, and mandatory propagation can change builder validation behavior.

`RemoteIterators` are lazy and may own remote resources. `foreach()` explicitly does not close the iterator afterwards, so callers need `cleanupRemoteIterator()` or closeable wrappers when iterators hold file handles, network connections, or listing statistics. Filtering in `hasNext()` can perform remote I/O earlier than callers expect, and skipping `hasNext()` shifts that work into `next()`.

## Test Signals

Useful tests for `StringInterner` should verify strong versus weak/reference-retention expectations where observable, in-place array mutation, null handling if supported by the implementation, and idempotence for equal strings.

`SysInfo` tests should cover OS-specific `newInstance()` selection, unsupported OS handling, non-negative hardware counters, `-1` sentinel behavior for unavailable sampled metrics, and monotonicity for cumulative CPU and I/O counters where the platform supports them.

`Tool` and `ToolRunner` tests should exercise generic option parsing, propagation into the tool's `Configuration`, preservation of application-specific arguments, null configuration handling, returned exit codes, printed generic usage, and prompt parsing for `y`, `yes`, mixed case, and negative responses.

`TraditionalBinaryPrefix` tests should cover suffix parsing for positive and negative values, case-insensitive symbols, no-suffix values, whitespace trimming, formatting precision, unit suffixes, maximum representable prefixes, overflow rejection, and invalid suffix diagnostics.

`DataChecksum.Type` tests should verify stable id lookup, name lookup, checksum size fields, and unknown id behavior.

Bloom filter tests should cover insertion, membership, expected false-positive behavior under controlled parameters, no false negatives for standard filters before retouching, logical `and`/`or`/`xor`/`not`, serialization round trips, vector-size reporting, and rejection or handling of incompatible filter operations.

Counting Bloom filter tests should add and delete keys, verify absent-key deletion is a no-op, assert approximate counts for low values, and explicitly exercise counter overflow beyond 15 repeated inserts and underflow-adjacent deletion cases.

Dynamic Bloom filter tests should insert enough keys to cross the per-row `nr` threshold, verify new rows are added without losing membership for earlier rows, and round-trip the multi-row state through `write()`/`readFields()`.

Retouched Bloom filter tests should record false positives through every overload, apply each `RemoveScheme` constant, verify selected false positives can be removed, and measure or assert the accepted false-negative tradeoff after selective clearing.

`CloseableTaskPoolSubmitter` tests should verify `submit()` delegates to the wrapped executor, `getPool()` returns the original executor, and `close()` shuts it down without requiring callers to touch the executor directly.

`FutureIO` tests should cover successful future results, `IOException` wrapped in `ExecutionException` or `CompletionException`, `UncheckedIOException`, runtime exceptions, errors, cancellation, interruption, timeout, multiple futures, cancellation cleanup, and `eval()` conversion of checked I/O failures into future-compatible failures.

`FutureIO.propagateOptions()` tests should populate `Configuration` keys under optional and mandatory prefixes and assert the exact stripped builder option names, including the documented `s3a.option`, `fs.io.policy`, and `something` cases.

`RemoteIterators` tests should cover every source adapter, mapping, type casting, filtering with and without explicit `hasNext()`, close propagation, halt predicates returning false, range `[start, excludedFinish)` boundaries, `toList()`, `toArray()` with too-small and sufficiently-sized destination arrays, `foreach()` count returns, exception propagation from source and consumer, statistics passthrough, and cleanup of closeable sources.

## Cross-Chunk Notes

The chunk starts after the beginning of `StringInterner`, so the full `strongIntern(String)` method declaration and any earlier `org.apache.hadoop.util` classes are in the preceding chunk. The final per-file reconciliation should merge this with earlier chunks for complete package coverage.

The Bloom API references `Filter`, `Key`, and hash classes whose declarations are outside this chunk. The final report should combine this chunk with the chunks that contain those declarations to describe the complete serialization format and compatibility constraints.

`FutureIO` references `CallableRaisingIOE`, `FunctionRaisingIOE`, `ConsumerRaisingIOE`, `TaskPool`, and `FSBuilder` declarations that are not fully defined here. The reconciliation lane should connect this public helper surface to those functional interfaces and builder implementations.
