# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007211`: lines 1-6066, `Docs/researches/chunks/subset-b-007211_research.md`
- `subset-b-007212`: lines 6067-12059, `Docs/researches/chunks/subset-b-007212_research.md`
- `subset-b-007213`: lines 12060-18114, `Docs/researches/chunks/subset-b-007213_research.md`
- `subset-b-007214`: lines 18115-24646, `Docs/researches/chunks/subset-b-007214_research.md`
- `subset-b-007215`: lines 24647-30892, `Docs/researches/chunks/subset-b-007215_research.md`
- `subset-b-007216`: lines 30893-37013, `Docs/researches/chunks/subset-b-007216_research.md`
- `subset-b-007217`: lines 37014-39037, `Docs/researches/chunks/subset-b-007217_research.md`

## Chunk Research

### subset-b-007211: lines 1-6066

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 1-6066

## Scope

This chunk covers lines 1-6066 of the Hadoop Common 3.3.4 JDiff XML API snapshot. It is generated documentation metadata, not executable Java source. The XML starts the `<api name="Apache Hadoop Common 3.3.4">` document, records the JDiff doclet invocation and build classpath, and describes public API contracts from the start of the file through the first part of `org.apache.hadoop.fs.CommonConfigurationKeysPublic`.

The covered public surface includes `org.apache.hadoop.HadoopIllegalArgumentException`, `org.apache.hadoop.conf.Configurable`, `Configuration`, and `Configured`, the crypto key-provider abstraction and factory, and the beginning of the `org.apache.hadoop.fs` API. The filesystem portion covers `Abortable`, `AbstractFileSystem`, Avro input adaptation, batched listing, block-location/storage-policy metadata, ByteBuffer and stream capability interfaces, checksum exceptions, `ChecksumFileSystem`, and many shared configuration constants. Because this is JDiff output, method bodies are absent; behavioral notes below are drawn from signatures, declared exceptions, fields, deprecation metadata, and embedded Javadoc.

## Purpose

The file persists the public Hadoop Common 3.3.4 API as an XML baseline for JDiff compatibility checks. This chunk is especially important because it captures cross-cutting APIs used by most Hadoop subsystems:

- Configuration loading, deprecation, typed access, credential lookup, serialization, tagging, and diagnostics.
- Pluggable encryption key-provider discovery and key lifecycle operations.
- The `AbstractFileSystem` service-provider contract used by `FileContext`.
- Stream, listing, block metadata, storage policy, checksum, abort, and optional capability contracts used by concrete filesystems.
- Public constant names for core filesystem, IO, IPC/RPC, security, crypto, and key-provider settings.

Downstream compatibility tooling can compare this XML against adjacent Hadoop releases to detect public signature, exception, field, and deprecation changes. Runtime behavior is implemented in the corresponding Java sources under `hadoop-common/src/main/java`, but this XML defines which parts are public and therefore compatibility-sensitive.

## Important APIs, Types, and Functions

`org.apache.hadoop.HadoopIllegalArgumentException` extends `IllegalArgumentException` and exists to distinguish invalid arguments thrown by Hadoop implementation code from generic JDK argument failures.

`org.apache.hadoop.conf.Configurable` defines the minimal configuration carrier contract with `setConf(Configuration)` and `getConf()`. `Configured` is the base implementation with constructors for null/default configuration and explicit `Configuration` injection.

`org.apache.hadoop.conf.Configuration` is the largest type in this chunk. It implements `Iterable` and `Writable` and exposes:

- Constructors for default resource loading, disabling default loading, and copy construction.
- Static deprecation management through `addDeprecations`, `addDeprecation` overloads, `isDeprecated`, `setDeprecatedProperties`, `dumpDeprecatedKeys`, and `hasWarnedDeprecation`.
- Resource loading through `addDefaultResource` and many `addResource` overloads for classpath resource names, `URL`, `Path`, `InputStream`, and another `Configuration`, plus `reloadConfiguration` and static `reloadExistingConfigurations`.
- Lookup and mutation methods including `get`, `getTrimmed`, `getRaw`, `set`, `unset`, `setIfUnset`, `onlyKeyExists`, `getPropertySources`, `getFinalParameters`, protected `getProps`, `size`, `clear`, and iteration.
- Typed getters/setters for numeric values, byte-size longs, floats, doubles, booleans, enums, time durations, storage sizes, regex patterns, integer ranges, string collections, arrays, trimmed strings, classes, class instances, local paths, files, URLs, streams, and readers.
- Password handling through `getPassword`, `getPasswordFromCredentialProviders`, and protected `getPasswordFromConfig`.
- Network helpers `getSocketAddr`, `setSocketAddr`, and `updateConnectAddr` for bind/client address management.
- XML and diagnostic output through `writeXml`, static `dumpConfiguration`, `readFields`, `write`, `getValByRegex`, tag APIs `addTags`, `getAllPropertiesByTag`, `getAllPropertiesByTags`, and `isPropertyTag`.

`org.apache.hadoop.crypto.key.KeyProvider` is an abstract, `Closeable`, thread-safe provider of secret key material. It exposes provider configuration access, option creation, transient-provider detection, key-version retrieval, key listing, metadata lookup, key creation with supplied or generated material, deletion, rolling versions with supplied or generated material, cache invalidation, `flush()` for durability, version-name helpers, provider search by key name, and password warning/error hooks. Public constants define default cipher, default bit length, and JCEKS serial-filter settings.

`KeyProviderFactory` is the URI/service-loader bridge for key providers. It defines abstract `createProvider(URI, Configuration)`, static `getProviders(Configuration)`, static `get(URI, Configuration)`, and the public `KEY_PROVIDER_PATH` configuration key.

The `org.apache.hadoop.fs` portion begins with `Abortable`, whose `abort()` contract says active writes must be canceled without making output visible. This is passed through `FSDataOutputStream` for filesystems, especially object stores, that can abort pending writes.

`AbstractFileSystem` is the main filesystem SPI behind `FileContext`. It implements `PathCapabilities`, carries protected `FileSystem.Statistics`, and exposes factory/statistics helpers, URI scheme/path validation, path qualification, working/home directory helpers, server defaults, symlink-aware path resolution, create/open/delete/mkdir/truncate/replication/rename operations, permission/owner/time/checksum/status/block-location/listing methods, corrupt-block listing, checksum verification toggles, canonical service naming, ACL APIs, xattr APIs, snapshot APIs, storage-policy APIs, asynchronous `openFileWithOptions`, path capability checks, multipart uploader builder creation, and a `methodNotSupported()` helper. Some methods are abstract requirements for filesystem implementations; others are default methods that mirror `FileContext` semantics or throw unsupported-operation behavior unless overridden.

Other filesystem APIs in this chunk include:

- `AvroFSInput`, adapting `FSDataInputStream` and `FileContext`/`Path` inputs to Avro `SeekableInput`.
- `BatchListingOperations`, an optional interface for filesystems that can return `PartialListing` iterators for lists of paths, with and without block locations.
- `BlockLocation`, a mutable serializable holder for hosts, cached hosts, names, topology paths, storage IDs, storage types, offset, length, corrupt flag, and striped/erasure-coded block-group indication.
- `BlockStoragePolicySpi`, the public storage-policy view exposing policy name, preferred storage types, creation fallbacks, replication fallbacks, and inherit-only/copy-on-create status.
- `ByteBufferPositionedReadable` and `ByteBufferReadable`, optional interfaces for positioned and sequential `ByteBuffer` reads, with explicit buffer-state and zero-length-read contracts.
- `CanSetDropBehind`, `CanSetReadahead`, and `CanUnbuffer`, optional stream controls for cache/readahead behavior and releasing buffers.
- `ChecksumException`, which extends `IOException` and carries the byte position where checksum verification failed.
- `ChecksumFileSystem`, a `FilterFileSystem` subclass that wraps a raw filesystem with client-side checksum file creation and verification.
- `CommonConfigurationKeysPublic`, a public constants class. This chunk reaches constants for topology, default filesystem URI, disk usage/space checks, symlink resolution, trash, filesystem implementation and creation parallelism, IO buffering/checksum/sort/serialization/TFile settings, caller context, IPC client/server tuning, socket factories, socks proxy, hash type, group mapping/cache settings, Kerberos/security/authentication tokens, SASL, crypto codec/cipher/JCEKS settings, impersonation provider, key-provider path, and default key bit length/cipher. The chunk ends in the declaration of `HADOOP_SECURITY_KEY_DEFAULT_CIPHER_DEFAULT`.

## Control Flow

The XML itself has no executable runtime control flow. Its meaningful flow is the contract flow described by public signatures and Javadocs.

`Configuration` instances load default resources unless constructed with defaults disabled, then overlay additional resources in insertion order. Final parameters prevent later resources from overriding protected values. Reads trigger variable expansion against other configuration keys, environment variables with supported default forms, and system properties unless restrictions are enabled. Static deprecation metadata can redirect old keys to replacement keys; the Javadoc for `addDeprecations` describes a lockless context-copy and atomic-swap retry pattern. Reload paths clear parsed state so resource values are re-read on subsequent access, and static reload applies that behavior to existing configuration instances.

Credential flow in `Configuration.getPassword` prefers configured credential providers and can fall back to cleartext configuration through `getPasswordFromConfig`. Socket helpers parse configured host/port values and can rewrite connect addresses to handle wildcard or multi-home bind addresses.

`KeyProviderFactory` resolves provider URIs from configuration, locates a provider factory through service loading, and instantiates a `KeyProvider`. Key lifecycle flow is read current metadata/key versions for encryption/decryption, create new keys, roll versions, invalidate provider caches when stronger visibility is needed, delete keys, then call `flush()` so provider-specific persistence stores receive mutations.

`AbstractFileSystem` creation flow resolves the implementation class from `fs.AbstractFileSystem.<scheme>.impl`, constructs it with the target URI and configuration, checks scheme/authority rules, and publishes statistics keyed by URI scheme/authority. Operation flow generally validates that paths belong to the filesystem, qualifies or resolves them as needed, then delegates to abstract or overrideable filesystem-specific methods. Default `openFileWithOptions` returns a `CompletableFuture` but performs a blocking `open(Path, int)` setup and expects callers to evaluate the future for the result.

`ChecksumFileSystem` wraps raw filesystem operations. Reads open data and checksum streams when verification is enabled; writes and creates generate sidecar checksum files when write checksums are enabled; delete, rename, list, copy-to-local, truncate, concat, ACL, permission, owner, replication, builder, and capability methods coordinate with the raw filesystem while hiding or preserving checksum files according to the operation. `reportChecksumFailure` lets implementations decide whether a retry is needed after bad data/checksum positions are reported.

## State and Persistence Behavior

The JDiff file is a persisted generated artifact under `dev-support/jdiff`. It records the API name, generation timestamp, doclet, classpath/sourcepath inputs, packages, classes, interfaces, constructors, methods, fields, exceptions, visibility, abstract/static/final/synchronized/native flags, deprecation text, and Javadocs. It does not mutate Hadoop runtime state.

The runtime APIs described by the chunk have significant state implications:

- `Configuration` manages loaded resource state, programmatic overlays, classloader selection, quiet-mode settings, final-parameter tracking, deprecation warning state, property source history, tags, and `Writable` serialized state. InputStream resources are cached, which is explicitly called out in the API docs as a memory consideration.
- Configuration values can be influenced by local process system properties and environment variables. This makes expansion useful but can make behavior host-dependent.
- Key provider implementations persist key metadata and material in provider-specific stores. The abstract contract makes `flush()` the durability boundary and `isTransient()` the signal that a provider is intended for transient key-material access rather than long-term storage.
- `AbstractFileSystem` owns per-filesystem statistics objects and exposes static clearing/printing of all statistics. Concrete filesystem implementations persist namespace mutations for file creation, deletion, rename, permissions, ACLs, xattrs, snapshots, storage policies, timestamps, replication, checksums, and multipart uploads.
- `Abortable.abort()` defines visibility state: after a successful abort, pending output must not become visible.
- `BlockLocation` is mutable serializable metadata, not an authoritative store. Array-valued getters/setters represent live metadata carriers used by listing and block-location APIs.
- `ChecksumFileSystem` persists checksum sidecar files alongside raw data files and can leave raw/checksum state inconsistent if operations partially fail.
- `CommonConfigurationKeysPublic` constants are compile-time API state. Even fields with typo-preserving Javadocs or deprecated status remain compatibility-sensitive public fields.

## Dependencies and Integration Points

The XML header records a build using the Hadoop annotations JDiff doclet and a large compile classpath including Hadoop Common/Auth artifacts, shaded protobuf and Guava, Commons libraries, HTTP client/core, servlet/Jetty/Jersey/Jackson/JAXB/Jettison, SLF4J/reload4j, Avro, RE2J, protobuf, Gson, Nimbus JOSE JWT, Kerby, Curator, JSch, ZooKeeper, Yetus annotations, Commons Compress, Woodstox, dnsjava, WildFly OpenSSL, Snappy, LZ4, Xerces, and XML APIs. The source path points to `hadoop-common-project/hadoop-common/src/main/java`.

Major integration points reflected in this chunk include:

- `Configuration` integrates with nearly every Hadoop subsystem through `core-default.xml`, `core-site.xml`, public configuration keys, class loading, `Writable` serialization, credential providers, local filesystem path selection, socket address publication, XML/JSON-style diagnostics, and property tags.
- `KeyProvider` integrates encryption clients with KMS/JCEKS/user or third-party key stores through `KeyProviderFactory`, configured provider paths, JCE algorithms, provider password handling, and crypto configuration constants.
- `AbstractFileSystem` integrates concrete filesystems with `FileContext`, `Path`, `FileStatus`, `LocatedFileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `RemoteIterator`, `FsServerDefaults`, `Options.CreateOpts`, `Options.Rename`, `Options.ChecksumOpt`, `FsPermission`, ACL entries/status, xattrs, storage policies, multipart upload builders, and Hadoop security exceptions.
- `Abortable` and `ChecksumFileSystem` integrate stream lifecycle and checksum behavior into higher-level `FSDataOutputStream` and `FileSystem` APIs.
- `AvroFSInput` bridges Hadoop filesystems to Avro readers.
- ByteBuffer and cache-control interfaces integrate optional capabilities with `StreamCapabilities` and stream implementations.
- `CommonConfigurationKeysPublic` ties public Java constants to `core-default.xml` documentation and to subsystems for topology resolution, filesystem creation, IO, IPC/RPC, group mapping, Kerberos/security, crypto, tokens, and key providers.

## Risks and Edge Cases

The primary artifact risk is stale generation. If this XML does not match the Hadoop Common 3.3.4 Java sources and build classpath, compatibility reports can either miss an API break or report a false break.

`Configuration` has high operational risk because precedence and expansion are subtle. Resource insertion order, final parameters, default loading, deprecation aliases, programmatic overlays, property tags, and reload behavior can interact in ways that surprise callers. Variable expansion can read host-specific environment variables and system properties, affecting reproducibility. InputStream resources are cached and can grow memory use. Password fallback to cleartext configuration is security-sensitive.

Typed configuration APIs expose many validation paths: numeric and storage-size parsing, time-unit conversion, regex compilation, range parsing, class loading and interface validation, socket address rewriting, and credential-provider errors. Deprecation aliases can update multiple keys, and old/new key precedence must remain stable for compatibility.

`KeyProvider` implementors must be thread safe, correctly distinguish transient and durable providers, protect key material, preserve version naming/base-name parsing semantics, handle missing provider passwords, avoid stale cache reads after key rolling, and require callers or implementations to `flush()` when changes must be durable. Duplicate key names across multiple providers can make `findProvider` order-sensitive.

`AbstractFileSystem` is a broad SPI. Implementations must honor same-filesystem path checks, default-port URI identity, unsupported-operation contracts, symlink and mount resolution behavior, create/overwrite/append semantics, ACL and xattr permissions, storage policy support, snapshot naming, block-location formats for replicated versus erasure-coded files, and exception contracts. The default asynchronous open wrapper is still backed by a blocking open, so callers must not assume nonblocking setup unless a filesystem overrides it.

`Abortable` requires failed or aborted writes to remain invisible; object-store implementations with multipart upload state need tests around partial upload cleanup and close-after-abort behavior. `ChecksumFileSystem` can leave stale checksum files around failed create, append, truncate, rename, concat, copy, or delete operations. It also has to hide checksum files from listings where users expect only logical data files.

`BlockLocation` has different meanings for replicated and erasure-coded files. Callers relying on offset/length/host cardinality need to account for logical block groups. ByteBuffer read interfaces state that buffer state is undefined after exceptions, so retry code must reset buffers explicitly. Several constants in `CommonConfigurationKeysPublic` are deprecated, typo-preserving, or moved to MapReduce; they cannot be removed or renamed without public API consequences.

The chunk ends mid-field inside `CommonConfigurationKeysPublic`, so this report intentionally does not claim the constants class is complete. Later chunks must reconcile the remaining constants and subsequent Hadoop Common APIs.

## Test Signals

Useful validation signals for this chunk include:

- JDiff or equivalent API comparison against Hadoop Common 3.3.3, 3.3.5, and source-generated 3.3.4 output to verify public signature, field, exception, and deprecation stability.
- Configuration tests for default-resource loading, `loadDefaults=false`, resource overlay order, final parameters, reload behavior, deprecated-key aliases, warning suppression, property source tracking, tag lookup, variable/environment/system-property expansion, restricted system properties, typed parsing, socket helpers, class loading, XML output, diagnostic dumping, regex lookup, `Writable` round trips, and credential-provider fallback.
- Security tests for password lookup, cleartext fallback controls, key-provider password warnings/errors, JCEKS serial-filter settings, token file constants, auth-to-local configuration, Kerberos relogin/autorenewal settings, impersonation provider overrides, and SASL property resolver configuration.
- Key-provider tests for service-loader discovery, URI scheme selection, provider path parsing, missing provider behavior, generated key material, explicit material creation, key version naming and base-name parsing, metadata lookup, version rolling, cache invalidation, deletion, `flush()` durability, transient providers, duplicate key names, and concurrent access.
- Filesystem SPI contract tests through `FileContext` and concrete `AbstractFileSystem` implementations for URI qualification, invalid paths, same-filesystem checks, create/open/delete/mkdir/truncate/rename semantics, overwrite behavior, symlink support, server defaults, file/link status, block locations, listing iterators, corrupt-block listing, checksum verification toggles, canonical service names, ACLs, xattrs, snapshots, storage policies, path capabilities, multipart upload builder creation, and unsupported-operation paths.
- Stream tests for `Abortable` visibility guarantees, ByteBuffer sequential and positioned reads, zero-length reads, exception recovery with reset buffer state, drop-behind/readahead support, and `unbuffer()`.
- Checksum filesystem tests for checksum file naming, checksum length calculation, open verification, write checksum generation, append/truncate/concat behavior, rename/delete cleanup, list filtering, copy-to-local CRC behavior, builder delegation, capability suppression, and checksum-failure reporting.
- Public constants tests or compatibility checks confirming field names, types, deprecation metadata, and documented defaults in `CommonConfigurationKeysPublic` remain aligned with `core-default.xml` and downstream references.

## Cross-Chunk Notes

This is chunk 1 of the Hadoop Common 3.3.4 JDiff XML file. It starts the API document and ends before `CommonConfigurationKeysPublic` closes. The merge/reconciliation lane should combine this with chunks `subset-b-007212` through `subset-b-007217` before producing a final per-file report, especially to complete the constants class and cover the remaining `org.apache.hadoop.fs`, IO, IPC, metrics, net, security, service, util, and other Hadoop Common public APIs.

### subset-b-007212: lines 6067-12059

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 6067-12059

## Scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.3.4. It starts in the tail of `org.apache.hadoop.fs.CommonConfigurationKeysPublic`, then covers complete public API entries for `ContentSummary`, `CreateFlag`, `FileAlreadyExistsException`, `FileChecksum`, `FileContext`, and `FileStatus`, and continues through the first large portion of `FileSystem`.

The source is API metadata, not Java method bodies. Control flow and persistence notes below are therefore derived from documented contracts, abstract/default method markers, overload relationships, builder hooks, and class/interface relationships visible in the JDiff file.

## Purpose

The covered API surface defines the core Hadoop filesystem client contract. It exposes:

- public configuration keys for KMS client caches, secure random generation, shell behavior, credential providers, sensitive config redaction, HTTP logs, tags, shutdown hook timeout, Prometheus, and HTTP idle timeout;
- content and quota reporting through `ContentSummary`;
- file creation semantics through `CreateFlag`;
- canonical filesystem metadata objects through `FileStatus` and `FileChecksum`;
- the newer `FileContext` API over `AbstractFileSystem`, with URI-aware path resolution and per-context defaults;
- the legacy and still central `FileSystem` abstract base class, including filesystem discovery, caching, path qualification, read/write/list/delete primitives, optional advanced features, statistics, builders, and service-token integration.

The JDiff file itself exists under `dev-support/jdiff`, so its immediate role is release/API compatibility documentation. The APIs it describes are production contracts used by Hadoop clients, HDFS, local filesystems, object-store connectors, and compatibility tools.

## Important APIs, Types, and Functions

### `CommonConfigurationKeysPublic` tail

The chunk begins inside `CommonConfigurationKeysPublic` and lists public constants for:

- KMS encrypted key cache size, low watermark, refill thread count, expiry, timeout, and failover retry/backoff settings;
- secure random algorithm, implementation, and device file path settings;
- shell warnings and safe-delete limits;
- HTTP log and idle-timeout settings;
- credential provider path, clear-text fallback, password-file key, and sensitive-key redaction settings;
- deprecated `HADOOP_SYSTEM_TAGS` and `HADOOP_CUSTOM_TAGS`, replaced by `HADOOP_TAGS_SYSTEM` and `HADOOP_TAGS_CUSTOM`;
- service shutdown hook timeout;
- Prometheus enablement.

These are all static public constants, mostly documented as matching `core-default.xml` entries. Their risk is compatibility: downstream code and configuration files may refer to the exact constant names and property keys.

### `ContentSummary`

`ContentSummary` extends `QuotaUsage` and implements `Writable`. It stores summarized counts and sizes for a directory or file, including length, directory count, file count, snapshot length/count/space, erasure-coding policy, quota display fields, and storage-type quota display.

Constructors are documented as deprecated in favor of `ContentSummary.Builder`; the three-argument constructor historically set `spaceConsumed` equal to `length`, while builder use makes both explicit. Public formatting methods include `getHeader()`, `getSnapshotHeader()`, `getHeaderFields()`, `getQuotaHeaderFields()`, multiple `toString(...)` overloads for quota, human-readable, storage-type, and snapshot-exclusion options, plus `toSnapshot(boolean)`.

### `CreateFlag`

`CreateFlag` is an enum describing create/open-write behavior. Documented combinations include `CREATE`, `APPEND`, `OVERWRITE`, `CREATE|APPEND`, `CREATE|OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`. Invalid combinations include `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`.

Validation APIs are static: `validate(EnumSet)`, `validate(path, pathExists, EnumSet)`, and `validateForAppend(EnumSet)`. They enforce whether a path may be created, appended to, or overwritten, and throw `HadoopIllegalArgumentException` or `IOException` on invalid states.

### `FileAlreadyExistsException` and `FileChecksum`

`FileAlreadyExistsException` is an `IOException` used when a target already exists and the operation is not configured to overwrite it.

`FileChecksum` is an abstract `Writable` for file checksums. Subclasses must provide `getAlgorithmName()`, `getLength()`, and `getBytes()`. The base API also exposes `getChecksumOpt()`, `equals()`, and `hashCode()`, with equality defined by algorithm and byte value.

### `FileContext`

`FileContext` implements `PathCapabilities` and provides the newer filesystem API over `AbstractFileSystem`. It is URI namespace aware and maintains per-context state: default filesystem, working directory, umask, and user identity (`UserGroupInformation`).

Factory methods build contexts from an `AbstractFileSystem`, default configuration, local filesystem URI, explicit URI, or supplied `Configuration`. Core methods include:

- path and context state: `getFSofPath()`, `setWorkingDirectory()`, `getWorkingDirectory()`, `getUgi()`, `getHomeDirectory()`, `getUMask()`, `setUMask()`, `resolvePath()`, `makeQualified()`;
- file and directory operations: `create(...)`, `create(Path)` builder, `mkdir()`, `delete()`, `open()`, `truncate()`, `setReplication()`, `rename()`;
- metadata operations: `setPermission()`, `setOwner()`, `setTimes()`, `getFileChecksum()`, `setVerifyChecksum()`, `getFileStatus()`, `msync()`, `getFileLinkStatus()`, `getLinkTarget()`, `getFsStatus()`;
- symlinks: `createSymlink()`, `resolve()`, `resolveIntermediate()`, with detailed final-component behavior and target-resolution rules for fully qualified, partially qualified, relative, and absolute targets;
- listing and lifecycle: `listStatus()`, `listLocatedStatus()`, `listCorruptFileBlocks()`, `deleteOnExit()`, `util()`;
- global `AbstractFileSystem` statistics helpers;
- ACL and xattr operations;
- snapshot operations;
- storage policy operations;
- `openFile(Path)` builder, path capability checks, server defaults, and multipart uploader builder.

`FileContext` defines `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`. The Javadocs explicitly note that `DEFAULT_PERM` is retained for compatibility after HADOOP-9155 because older versions used directory-style executable defaults for files.

### `FileStatus`

`FileStatus` is the serializable client-side metadata record for a filesystem entry. It implements `Writable`, `Comparable`, `Serializable`, and `ObjectInputValidation`. Constructors cover minimal metadata, no-symlink filesystems, symlink targets, boolean attribute triples, explicit attribute sets, and copy construction.

State exposed by getters includes length, file/directory/symlink kind, block size, replication, modification/access times, permission, ACL/encryption/erasure-coding/snapshot flags, owner, group, path, and symlink target. `attributes(acl, crypt, ec, sn)` converts booleans to an attribute flag set; `NONE` is the shared empty attribute set.

Ordering, equality, and hash code are path-based. A raw-object `compareTo(Object)` exists specifically for binary compatibility per HADOOP-14683. `readFields()` and `write()` are deprecated in favor of direct protobuf conversion through `PBHelper`, but remain public for compatibility.

### `FileSystem`

`FileSystem` is an abstract `Configured` class implementing `Closeable`, `DelegationTokenIssuer`, and `PathCapabilities`. The covered portion exposes the central legacy filesystem contract.

Important static factory/discovery APIs include `get(...)`, `newInstance(...)`, `getDefaultUri()`, `setDefaultUri()`, `getLocal()`, `newInstanceLocal()`, `closeAll()`, `closeAllForUGI()`, and `getFileSystemClass()`. `get(URI, Configuration)` may return cached instances unless `fs.$SCHEME.impl.disable.cache` is true; `newInstance(...)` always returns a new initialized object. `getFileSystemClass()` scans service-loaded implementations and configuration bindings.

Core identity and path APIs include `initialize()`, `getScheme()`, abstract `getUri()`, `getCanonicalUri()`, `canonicalizeUri()`, `getDefaultPort()`, `getCanonicalServiceName()`, deprecated `getName()`/`getNamed()`, `makeQualified()`, and protected `checkPath()`.

The covered I/O contract includes many overloads and hooks:

- block locations and server defaults: `getFileBlockLocations(...)`, `getServerDefaults(...)`;
- open APIs: `open(Path)`, `open(Path, int)`, `open(PathHandle)`, `open(PathHandle, int)`;
- path handles: `getPathHandle()` and protected `createPathHandle()`;
- create APIs: multiple `create(...)` overloads, the abstract full-parameter create method, flag/checksum create overloads, protected `primitiveCreate()`, `primitiveMkdir()`, and `createNonRecursive(...)`;
- append and concat: `append(...)` overloads, abstract append-with-buffer/progress, and optional `concat()`;
- namespace mutation: abstract `rename(Path, Path)`, protected rename-with-options, `truncate()`, abstract `delete(Path, boolean)`, deprecated `delete(Path)`, `deleteOnExit()`, `cancelDeleteOnExit()`, and protected `processDeleteOnExit()`;
- existence and metadata helpers: `exists()`, deprecated `isDirectory()`, deprecated `isFile()`, deprecated `getLength()`, `getContentSummary()`, `getQuotaUsage()`, quota setters, abstract `listStatus()`, filtered/glob/list-located/list-files/list-iterator APIs, `getHomeDirectory()`, abstract working directory accessors, and `getInitialWorkingDirectory()`;
- local copy helpers: `copyFromLocalFile()`, `moveFromLocalFile()`, `copyToLocalFile()`, `moveToLocalFile()`, `startLocalOutput()`, and `completeLocalOutput()`;
- closure and capacity/defaults: `close()`, `getUsed()`, deprecated `getBlockSize()`, default block size and default replication methods;
- filesystem metadata: abstract `getFileStatus()`, `msync()`, symlink support, checksums, status/capacity, permissions, owners, times, snapshots, ACLs, xattrs, storage policies, trash roots, path capabilities, and multipart/builder APIs.

Statistics APIs are split between deprecated synchronized global maps/lists (`getStatistics()`, `getAllStatistics()`, `getStatistics(scheme, cls)`) and modern `StorageStatistics` / `GlobalStorageStatistics`. Static `clearStatistics()` and `printStatistics()` remain available.

## Control Flow

For `FileContext`, the intended flow is: construct a context from configuration or an explicit default filesystem; qualify or resolve user paths using the context default filesystem and working directory; locate the bonded `AbstractFileSystem` for the path; then delegate the actual operation to that filesystem. Builder APIs defer filesystem mutation until `build()` is called. The `create(Path)` builder explicitly says `FileContext` verifies builder parameters and then calls `AbstractFileSystem#create`.

For symlink operations, intermediate path components are transparently resolved in most calls, while the final component is treated specially for delete, delete-on-exit, rename, `getLinkTarget()`, and `getFileLinkStatus()`. Create and mkdir expect the final component not to exist; most other operations follow the final symlink.

For `FileSystem` acquisition, `get(URI, conf)` follows a cache-first path unless disabled by `fs.$SCHEME.impl.disable.cache`; `newInstance(...)` bypasses the cache. Initialization happens after construction through `initialize(URI, Configuration)`, and subclasses overriding it must call the superclass.

For `FileSystem` write operations, simple overloads funnel toward fuller methods with default buffer sizes, replication, block size, permission, flags, progress callback, and checksum options. The abstract full create method is the real subclass contract, while `primitiveCreate()` and `primitiveMkdir()` exist so `FileContext` can pre-apply umask and pass absolute permissions during the transition from `FileSystem` to `FileContext`.

For builders, `createFile()` and `appendFile()` return `FSDataOutputStreamBuilder`; `openFile()` returns `FutureDataInputStreamBuilder`. The protected `openFileWithOptions()` methods are the real execution hooks. The base implementation performs a blocking `open(...)` call and wraps the result in a `CompletableFuture`, so asynchronous-looking APIs may still execute synchronously unless overridden.

For lifecycle, `deleteOnExit()` records paths on an instance; cached instances are closed during clean JVM shutdown, which then processes recursive deletion. `close()` releases locks, processes delete-on-exit paths, and removes the instance from the cache if cached. `closeAll()` and `closeAllForUGI()` operate over cached instances.

## State and Persistence Behavior

This chunk defines public API state rather than storage internals.

`FileContext` state is per object: default filesystem, working directory, umask, and UGI. It also participates in global `AbstractFileSystem` statistics and has a shutdown hook priority for cleanup behavior. `setWorkingDirectory()` deliberately stores the path as a prefixing rule rather than following symlinks to an inode, which is important in a distributed namespace with multiple roots.

`FileStatus` is a persistent/wire-facing metadata record. Its `Writable` methods still exist but are deprecated in favor of protobuf conversion. Serialized status must preserve path, type, symlink, permission, owner/group, timestamps, block metadata, and attribute flags. Java object deserialization invokes `validateObject()`.

`ContentSummary` is a `Writable` content/quota summary. Its public persistence surface includes both legacy constructor semantics and newer builder-derived fields, especially the distinction between logical length and space consumed.

`FileSystem` has significant global and instance state implied by the API:

- a cache of filesystem instances keyed by URI/user/config context;
- per-instance configuration, URI identity, delete-on-exit path list, checksum verification/write flags where supported, working directory in legacy implementations, and statistics;
- global storage statistics and deprecated global statistics maps;
- static symlink enablement toggles;
- service-loader-discovered implementation classes and configuration-based scheme bindings;
- delegation-token service names derived from canonical URI and port when a filesystem issues its own tokens.

Actual file, directory, ACL, xattr, snapshot, quota, storage-policy, and trash persistence is delegated to filesystem implementations such as HDFS, local filesystems, and object-store connectors.

## Dependencies and Integration Points

The APIs depend heavily on Hadoop Common types:

- `Configuration`, `Configured`, and `CommonConfigurationKeysPublic` for runtime defaults;
- `Path`, `PathHandle`, `PathFilter`, `RemoteIterator`, `BlockLocation`, `FsStatus`, `FsServerDefaults`, `StorageType`, `BlockStoragePolicySpi`, and stream builders for filesystem operations;
- `FSDataInputStream`, `FSDataOutputStream`, `FutureDataInputStreamBuilder`, `FSDataOutputStreamBuilder`, and `MultipartUploaderBuilder` for I/O;
- `FsPermission`, `AclStatus`, ACL entries, and xattr flags for metadata;
- `UserGroupInformation`, `DelegationTokenIssuer`, and token service naming for security;
- `AbstractFileSystem` and `DelegateToFileSystem` as `FileContext` and builder integration points;
- `ServiceLoader` and `fs.$SCHEME.impl` configuration bindings for filesystem implementation discovery;
- `PBHelper` for protobuf-compatible `FileStatus` serialization.

The covered constants integrate with `core-default.xml` and with components such as KMS clients, shell commands, HTTP servers, credential providers, shutdown hooks, metrics, and config redaction. The API also preserves multiple deprecated methods and fields because external applications compile against this surface.

## Risks and Edge Cases

The JDiff file is generated compatibility metadata. A missing, renamed, visibility-changed, or deprecation-changed member can break downstream source or binary compatibility even if implementation behavior is unchanged.

`ContentSummary` constructor compatibility is subtle because legacy constructors may imply `spaceConsumed == length`, while builder code can separate those values. Output formatting has many boolean options whose meanings are easy to invert; the x-option documentation says false includes snapshot calculations and true excludes them.

`CreateFlag` combinations control destructive behavior. Incorrect validation around `APPEND`, `OVERWRITE`, or `CREATE` can cause accidental overwrite, failed append, or non-atomic create behavior.

`FileContext` path resolution differs from Unix working-directory semantics. The working directory is a prefix, not an inode reference, and relative paths with schemes are illegal. Symlink final-component behavior differs by operation, so clients and filesystem implementations must agree on whether links are followed or operated on directly.

`FileSystem.get()` caching is a common source of state leakage. Callers expecting isolated checksum flags, working directories, delete-on-exit lists, statistics, or credentials may need `newInstance(...)` or cache-disabling configuration. Conversely, overuse of uncached instances can bypass shared lifecycle cleanup.

`deleteOnExit()` is best-effort and can make JVM shutdown slow or unreliable on remote/object stores. The documentation warns that clean shutdown is not guaranteed and that existence/deletion costs can dominate shutdown time.

Many `FileSystem` operations are optional with default `UnsupportedOperationException`, no-op, null, true, or empty-statistics behavior. Examples include append, concat, truncate, symlinks, checksums, ACLs, xattrs, snapshots, storage policies, multipart upload, and path handles. Generic clients must probe capabilities or handle unsupported operations.

Several deprecated convenience methods (`isFile`, `isDirectory`, `getLength`, `getReplication`, old statistics APIs) perform extra status calls or expose older semantics. The docs explicitly discourage repeated `exists()`/`getFileStatus()` patterns because they may trigger redundant HDFS RPCs.

`FileStatus` equality and ordering are path-based, not based on full metadata. Code using `Set<FileStatus>` or sorted collections can silently collapse entries with the same path but different metadata snapshots.

The base `openFileWithOptions()` wraps a blocking open in a `CompletableFuture`; clients must not assume nonblocking behavior unless a specific filesystem documents an override. Unknown mandatory open-file options are specified to raise `IllegalArgumentException`.

## Test Signals

Compatibility checks should diff this JDiff output against adjacent Hadoop Common versions and flag changes in public classes, method signatures, visibility, abstract/final/static flags, checked exceptions, fields, implemented interfaces, and deprecation strings.

`CreateFlag` tests should cover every documented valid and invalid combination, including path-exists and path-missing cases for create, append, overwrite, append-new-block, sync-block, and lazy-persist options.

`ContentSummary` tests should cover builder construction, legacy constructors, equality/hash behavior, header fields, quota fields, human-readable output, storage-type quota output, snapshot-inclusive/exclusive output, erasure-coding policy display, and writable/protobuf interoperability where applicable.

`FileStatus` tests should cover constructors with and without symlinks, attribute boolean-to-set conversion, default permission/owner/group behavior for nulls, path-based equality/ordering, raw-object `compareTo(Object)` binary compatibility, protobuf conversion, deprecated `Writable` read/write, and object validation after Java serialization.

`FileContext` tests should exercise default, local, explicit URI, explicit `AbstractFileSystem`, and explicit configuration factories; working-directory qualification; invalid relative-with-scheme paths; umask application; server-default propagation; create builder build-time validation; symlink target resolution cases; ACL/xattr/snapshot/storage-policy dispatch; `hasPathCapability()` delegation; and statistics collection.

`FileSystem` tests should cover cached versus uncached acquisition, cache disablement via `fs.$SCHEME.impl.disable.cache`, `closeAll()` and `closeAllForUGI()`, service-loader filesystem discovery, canonical URI/default port behavior, token service naming, path qualification/checking, all simple-to-full overload funnels for create/open/append/list/copy, and correct subclass abstract-method dispatch.

Lifecycle tests should verify delete-on-exit registration/cancellation/processing, close removing cached instances, best-effort behavior when paths disappear before shutdown, and performance/failure behavior on slow remote filesystem deletes.

Optional-feature tests should assert default unsupported/no-op/null behavior and implementation overrides for append, concat, truncate, symlinks, checksums, ACLs, xattrs, snapshots, storage policies, path handles, multipart upload, `msync()`, and builder-based open/create/append.

Performance-sensitive tests should detect redundant RPC patterns around `exists()`, `isFile()`, `isDirectory()`, and repeated `getFileStatus()` calls, and should validate lazy/on-demand behavior of `listStatusIterator()` for filesystems that override it.

## Cross-Chunk Notes

The chunk starts after the beginning of `CommonConfigurationKeysPublic`, so the final per-file report should combine this with the previous chunk for the full constants class. It also stops inside `FileSystem` immediately after the `LOG` field begins, so subsequent chunks must supply the remaining fields, nested classes, and methods before drawing conclusions about the complete `FileSystem` API.

### subset-b-007213: lines 12060-18114

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 12060-18114

## Scope And Purpose

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.3.4. It is metadata rather than executable Java source: the XML records public/protected API signatures, inheritance, implemented interfaces, field visibility, exceptions, deprecation status, and Javadoc text. The range starts at the tail of `org.apache.hadoop.fs.FileSystem`, covers a large portion of `org.apache.hadoop.fs`, then enters `org.apache.hadoop.fs.audit`, `org.apache.hadoop.fs.ftp`, and the beginning of `org.apache.hadoop.fs.statistics`.

The source range is not a standalone XML document. It begins after many `FileSystem` members have already been listed and ends inside the `IOStatistics` interface after `meanStatistics` starts. The merge lane must combine this with adjacent chunks to reconstruct the full file and the full API surface.

The dominant purpose of this chunk is to describe Hadoop's filesystem abstraction layer: utility helpers, filesystem wrappers, stream contracts, path and handle types, local/FTP filesystem implementations, quotas, storage statistics, trash policy integration, stream capability probing, audit context propagation, multipart upload handles, and duration/statistics reporting APIs.

## API Surface In This Chunk

The range starts with final fields and class documentation for `FileSystem`. The tail includes API-sensitive constants such as `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and protected `statistics`. The class documentation is important because it states that `FileSystem` is the generic filesystem API for local, HDFS, object-store, and third-party implementations, and warns developers to update forwarding/filtering subclasses such as `FilterFileSystem` and `ChecksumFileSystem` when adding public or protected methods.

`FileUtil` is a static helper collection for local file and Hadoop filesystem operations. It converts `FileStatus[]` to `Path[]`, recursively deletes local files/directories, handles symlink targets, copies between `FileSystem` instances and local files, prepares shell-safe paths, computes local disk usage, unzips/untars archives, creates symlinks, runs permission/ownership changes, wraps `File.list*()` null behavior as exceptions, creates temp files, replaces files, builds classpath jars, finds jars in directories, compares filesystems, and writes bytes/text to a `FileSystem` or `FileContext`. Its `fullyDelete(FileSystem, Path)` overload is deprecated in favor of `FileSystem.delete(Path, boolean)`.

`FilterFileSystem` is a forwarding wrapper around another `FileSystem`. It exposes `getRawFileSystem()`, forwards URI/path qualification, open/create/append/concat/rename/delete/list/status, checksum, permission, ACL, xattr, storage policy, snapshot, builder, and path capability APIs, and stores the wrapped `fs` plus optional `swapScheme`. This class is a central integration point for subclasses that decorate or adapt another filesystem implementation.

`FSBuilder<S, B>` defines the generic builder contract used by filesystem and file-context builders. It has typed `opt()` and `must()` overloads for optional and mandatory options, plus `build()`. The contract says optional unknown options may be ignored, while unsupported mandatory options should fail, normally through `IllegalArgumentException`.

`FSDataInputStream`, `FSDataOutputStream`, `FSInputStream`, `Seekable`, `PositionedReadable`, `Syncable`, `StreamCapabilities`, and `StreamCapabilitiesPolicy` define the stream layer. Input streams support seek, positioned reads, byte-buffer reads, readahead/drop-behind, unbuffering, path capabilities, and IO statistics when the nested stream exposes `IOStatisticsSource`. Output streams expose position, close, hflush/hsync, drop-behind, capability probing, IO statistics, and abort when the wrapped stream is `Abortable`. `PositionedReadable` explicitly requires thread-safe positional reads, but its Javadoc warns that not all implementations satisfy this requirement.

`FSDataOutputStreamBuilder` is the create/append builder for output streams. It captures permission, buffer size, replication, block size, recursive parent creation, progress callbacks, create/overwrite/append flags, checksum options, and generic `opt`/`must` options inherited from `FSBuilder`. Its documentation explicitly discourages `instanceof` checks for filesystem-specific behavior and recommends namespaced builder options instead.

`FsConstants`, `FsServerDefaults`, and `FsStatus` describe shared filesystem constants and serializable server/status defaults. `FsServerDefaults` is a `Writable` carrier for block size, bytes-per-checksum, packet size, replication, file buffer size, encryption flag, trash interval, checksum type, key provider URI, and default storage policy ID. `FsStatus` is a `Writable` view of capacity, used, and remaining bytes.

`FutureDataInputStreamBuilder` is the asynchronous open-builder API. Its `build()` returns `CompletableFuture<FSDataInputStream>` and may accept a `FileStatus` hint through `withFileStatus()`. Like output builders, it uses `opt` and `must` parameters for implementation-specific options.

`GlobalStorageStatistics` and `StorageStatistics` provide process-wide and per-instance statistics plumbing. `GlobalStorageStatistics` has synchronized `get`, `put`, `reset`, and `iterator` operations around named statistics providers. `StorageStatistics` is an abstract named statistics object with optional scheme association, long-statistic iteration, key lookup, tracking checks, and reset.

`GlobFilter`, `PathFilter`, `Path`, `InvalidPathException`, and `InvalidPathHandleException` cover path parsing/filtering. `Path` is serializable and comparable, can be built from parent/child pairs, strings, URIs, and components, and supports URI conversion, filesystem resolution, qualification, absolute/root/name/parent/suffix/depth checks, Windows absolute-path detection, merge/removal of scheme and authority, and deserialization validation against malicious object streams.

`LocalFileSystem` and `RawLocalFileSystem` adapt the abstract `FileSystem` contract to the host filesystem. `LocalFileSystem` extends `ChecksumFileSystem`, exposes the raw filesystem, maps paths to `java.io.File`, handles local copy operations, reports checksum failures, and supports symlink operations. `RawLocalFileSystem` implements local open/create/append/rename/truncate/delete/list/mkdir/status/working-directory operations directly, uses `chmod`/`chown` style behavior for permissions and ownership, supports path handles, symlinks, and path capability checks.

`LocatedFileStatus`, `PartialListing`, `QuotaUsage`, `StorageType`, `ReadOption`, `PathHandle`, `PartHandle`, `UploadHandle`, and `MultipartUploader` carry filesystem metadata and handles. `LocatedFileStatus` adds block locations to `FileStatus`. `PartialListing` behaves like a future-like partial directory listing that may throw on `get()`. `QuotaUsage` stores namespace, space, and storage-type quota/consumption values and produces shell-style formatted output. `StorageType` models media classes, movability, transient storage, and quota support. `MultipartUploader` is an async, closeable upload API with `startUpload`, `putPart`, `complete`, `abort`, and best-effort `abortUploadsUnderPath`.

`Trash` and `TrashPolicy` provide pluggable trash behavior. `Trash` delegates to configured policies and includes `moveToAppropriateTrash()` for symlinks and mount points, where deletion should move to the trash directory on the resolved target volume. `TrashPolicy` defines initialization, enablement, move/checkpoint/delete operations, current trash directory lookup, emptier creation, and factories controlled by `fs.trash.classname`. Older APIs that require a home directory are deprecated because encryption zones require path-specific trash resolution.

`UnsupportedFileSystemException`, `UnsupportedMultipartUploaderException`, `ParentNotDirectoryException`, `FSError`, and `FTPException` define error types around unsupported schemes, unsupported multipart uploaders, invalid parents, presumed native filesystem errors, and FTP runtime exception wrapping.

`XAttrCodec` and `XAttrSetFlag` expose extended-attribute value conversion and set validation. `XAttrCodec` decodes text, hex-prefixed `0x`/`0X`, base64-prefixed `0s`/`0S`, and quoted string representations into byte arrays, and encodes byte arrays back to shell/API-friendly strings. `XAttrSetFlag.validate()` checks xattr create/replace semantics against whether the xattr already exists.

`CommonAuditContext` is a final audit-context container shared across filesystem audit spans. It supports per-thread context entries, dynamically evaluated suppliers, reset/remove/get/contains operations, thread ID reporting, evaluated-entry maps, global key/value context, process ID, and entry-point recording through `noteEntryPoint()`. The Javadoc states that audit spans retain a reference to the current thread context even when spans move across threads.

`FTPFileSystem` is a `FileSystem` backed by Apache Commons Net. It exposes the `ftp` scheme, default port, initialization, open/create/delete/list/status/mkdir/rename/working-directory operations, and configuration constants for user, host, port, password, data connection mode, transfer mode, same-directory rename behavior, and timeout. Its create-stream Javadoc warns that the stream must be closed before using other APIs on the class or calls may block. `append()` is explicitly unsupported.

`DurationStatisticSummary` and the opening of `IOStatistics` start the `org.apache.hadoop.fs.statistics` section. `DurationStatisticSummary` is serializable, records key, success/failure selection, count, max, min, and mean, and can fetch success/failure summaries from an `IOStatistics` source. `IOStatistics` begins with maps for counters, gauges, minimums, maximums, and then continues beyond this chunk.

## Control Flow And State Behavior

Because this is JDiff XML, direct control flow is limited to API contracts. The runtime control flow implied by the documented APIs is:

1. Client code resolves `Path` objects through `FileSystem` or `FileContext`, then uses generic `FileSystem` operations instead of implementation-specific classes.
2. Wrapper filesystems such as `FilterFileSystem` forward calls to an underlying `FileSystem`; new base APIs must be audited so wrappers do not accidentally drop or incorrectly advertise behavior.
3. Stream creation is either immediate through `open/create/append` or declarative through builders. Builder options split into optional keys that can be ignored and mandatory keys that must be honored or rejected.
4. Input streams maintain mutable seek position, while positional reads are intended not to change that position. The API warns that thread safety is a contract but not universally achieved.
5. Output streams track position and may flush to readers through `hflush()` or to storage through `hsync()`. Abort support is capability-dependent and must be probed or handled through exceptions.
6. Trash operations resolve the appropriate filesystem/trash root, especially across symlinks, mount points, and HDFS encryption zones, then move paths, checkpoint trash, or expunge old checkpoints.
7. Multipart uploads follow a future-returning lifecycle: start an upload, upload one or more numbered parts, complete with a non-empty map of part handles to obtain a `PathHandle`, or abort the upload.
8. Audit context flows from per-thread maps and global entries into filesystem audit spans. Dynamic supplier values are evaluated when `getEvaluatedEntries()` is called, which may happen in a different thread from where the supplier was registered.
9. Statistics flow from implementations into `StorageStatistics`, `GlobalStorageStatistics`, `IOStatisticsSource`, and duration summaries for reporting and testing.

State and persistence behavior is mostly delegated to implementations. Persistent filesystem state is affected by create, append, delete, rename, truncate, mkdir, permission/owner/time changes, ACL/xattr operations, storage policy changes, snapshots, trash movement/checkpoint deletion, local raw-file operations, and FTP operations. In-memory state includes working directories, stream positions, builder options, per-stream/per-filesystem statistics, global statistics registry entries, audit context maps, and trash policy fields (`fs`, `trash`, `deletionInterval`).

## Dependencies And Integration Points

The XML describes APIs that integrate across Hadoop Common and external filesystems:

- Core Hadoop types: `Configuration`, `FileSystem`, `FileContext`, `Path`, `FileStatus`, `BlockLocation`, `FsPermission`, ACL/xattr/storage-policy types, `RemoteIterator`, `Progressable`, `DataChecksum.Type`, `Writable`, and Hadoop security exceptions.
- Java platform types: `URI`, `File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `ByteBuffer`, `CompletableFuture`, collections, `Serializable`, `Closeable`, and object deserialization validation.
- Local OS integration through shell path conversion, chmod/chown/symlink operations, Windows-specific permission and path behavior, and Java file APIs.
- Apache Commons Net for `FTPFileSystem`.
- Filesystem-spec integration through documented semantics for `FileSystem`, `Syncable`, stream capabilities, path capabilities, and IO statistics.
- Compatibility integration with downstream projects called out in `FileSystem` documentation, including Hive shims and HBase/HBoss references.

The most sensitive integration point is API evolution. The `FileSystem` class documentation explicitly instructs developers adding public/protected methods to review forwarding subclasses such as `FilterFileSystem`, checksum behavior in `ChecksumFileSystem`, and test interfaces such as `TestFilterFileSystem.MustNotImplement` and `TestHarFileSystem.MustNotImplement`. Capability probing through `hasPathCapability(Path, String)` also requires wrappers to avoid over-reporting support.

## Risks And Edge Cases

- This chunk starts and ends mid-structure; chunk-local XML parsing will fail and any class-level interpretation must be reconciled with adjacent chunks.
- `FileUtil.fullyDelete()` can return false after partial deletion, and `fullyDeleteContents()` follows symlinks to directories when deleting contents. Callers need to understand whether a symlink itself or its target contents are affected.
- Shell/permission helpers have platform-specific behavior. Windows symlink creation may fail with `SYMLINK_NO_PRIVILEGE`, and Windows permission semantics differ from Unix, especially execute permission on directories.
- Archive extraction helpers (`unZip`, `unTar`) are filesystem-writing utilities; callers need path traversal and overwrite behavior covered by implementation tests even though this XML only records signatures and Javadoc.
- `FilterFileSystem` can create compatibility bugs if a new `FileSystem` method is not forwarded, is forwarded with the wrong default, or incorrectly reports capabilities.
- Builder options intentionally allow unknown optional keys to be ignored. Misspelled mandatory options should fail, while misspelled optional options may silently have no effect.
- `PositionedReadable` promises thread-safe positioned reads but warns that not all filesystems meet it. Consumers such as HBase can be sensitive to this mismatch.
- `FSDataInputStream.getIOStatistics()` may return null when the nested stream is not an `IOStatisticsSource`, while `FSDataOutputStream.getIOStatistics()` documents an empty-statistics fallback. Callers should not treat the input and output contracts as identical.
- `Path.validateObject()` exists to defend deserialization; any custom serialized path handling should preserve this validation.
- Trash path selection must account for encryption zones, symlinks, and mount points. Deprecated home-directory-based trash APIs can place data in the wrong trash location for encrypted paths.
- `FTPFileSystem.create()` blocks later API use until the returned stream is closed; `append()` is unsupported. FTP rename also has a same-directory constraint constant, so behavior may differ from HDFS/local filesystems.
- Multipart upload cleanup is best effort. `abortUploadsUnderPath()` may be unsupported or miss uploads because of eventually consistent listings.
- Audit context suppliers may be evaluated in different threads, so supplier implementations must be thread-safe and should not assume caller-thread state.
- `XAttrCodec` accepts multiple textual encodings; invalid prefixes, quoting, and byte conversion errors need explicit tests to avoid shell/API compatibility regressions.

## Test Signals

Useful validation around this chunk includes:

- JDiff/API compatibility tests that compare this XML against neighboring Hadoop Common versions and flag public/protected signature changes in the listed classes.
- Unit tests for every `FileSystem` API addition to ensure `FilterFileSystem`, `ChecksumFileSystem`, HAR, and local/raw local filesystems either forward, implement, or deliberately reject the method.
- Local filesystem tests for recursive deletion, symlink deletion versus target deletion, Windows permission behavior, chmod/chown wrappers, temp-file creation, file replacement, and `PathHandle` support.
- Stream tests for seek/getPos, positioned reads that do not alter stream offset, `readFully()` EOF behavior, ByteBuffer reads, unbuffer policy, drop-behind/readahead capability probing, hflush/hsync semantics, abort support, and IO statistics fallback behavior.
- Builder tests for optional versus mandatory options, overwrite/create/append flag combinations, recursive parent creation, invalid parameter rejection, checksum options, and asynchronous open futures.
- Path tests for URI construction, Windows absolute paths, parent/child resolution, scheme/authority removal, path merging, equality/hash/compare behavior, root/depth calculations, and deserialization validation.
- Trash tests for disabled trash, already-in-trash paths, symlink and mount-point resolution, encryption-zone-specific trash directories, checkpoint creation/deletion, immediate expunge, and policy factory configuration via `fs.trash.classname`.
- Multipart uploader tests for start/put/complete/abort ordering, parallel part uploads, input stream closure after `putPart`, empty handle-map rejection, unsupported abort-under-path behavior, and `PathHandle`/`PartHandle`/`UploadHandle` serialization equality.
- Audit tests for thread-local context isolation, global entry visibility, `PROCESS_ID`, `noteEntryPoint()` idempotence, supplier evaluation timing, reset behavior, and cross-thread span propagation.
- FTP filesystem integration tests for open/create stream lifecycle, append unsupported behavior, working directory handling, recursive delete/mkdir/list/status, timeout/config key handling, and rename restrictions.
- Statistics tests for `GlobalStorageStatistics` synchronized registry behavior, reset/iterator semantics, `StorageStatistics` tracking, `DurationStatisticSummary` success/failure extraction, and `IOStatistics` map presence after the adjacent chunk completes the interface.

### subset-b-007214: lines 18115-24646

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 18115-24646

## Research scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.3.4, not Java implementation source. The range begins at the end of `org.apache.hadoop.fs.statistics.IOStatistics`, covers the public `fs.statistics` aggregation/logging/name constants, Hadoop HA failover/fencing contracts, protobuf bridge interfaces, and a large part of the `org.apache.hadoop.io` serialization package from map/array writables through the opening constructors of `WritableComparator`. Conclusions are based on API signatures, inheritance, visibility, declared exceptions, constants, and embedded Javadocs.

## Purpose

The chunk documents three adjacent public API areas. First, Hadoop's `IOStatistics` model gives filesystem and stream implementations a low-cost way to expose counters, gauges, minimums, maximums, and mean statistics, plus stable metric-name constants for filesystem, object-store, and stream instrumentation. Second, the `org.apache.hadoop.ha` entries define the administrative protocol used by health monitors and failover controllers to inspect and move services among standby, active, and observer states, including fencing hooks and service-target proxy construction. Third, the `org.apache.hadoop.io` entries define Hadoop's compact serialization and comparison layer: `Writable`, `WritableComparable`, primitive wrappers, array/map wrappers, UTF-8 text, sequence/map file factories, stringification, raw byte comparators, and utilities around data streams and byte buffers.

## Important APIs and types

The `IOStatistics` tail exposes `minimums()`, `maximums()`, and `meanStatistics()` maps, with sentinel constants `MIN_UNSET_VALUE` and `MAX_UNSET_VALUE` for metrics that have not been initialized. `IOStatisticsAggregator.aggregate(IOStatistics)` is the extension point for accumulating a source statistics instance into an aggregate, returning false for null inputs. `IOStatisticsSnapshot` implements `IOStatistics`, `IOStatisticsAggregator`, and `Serializable`; it can be empty, snapshot a source, clear maps, aggregate another source, expose synchronized map accessors, stringify itself, provide a `JsonSerialization` helper, and list classes needed for secure deserialization. `IOStatisticsSupport` provides factory/retrieval helpers: snapshot current statistics, create an empty aggregating snapshot, extract statistics from either an `IOStatistics` or `IOStatisticsSource`, and return no-op `DurationTracker`/`DurationTrackerFactory` singletons. `IOStatisticsLogging` converts statistics or statistics sources to string form, supports more expensive sorted/pretty output, lazy `toString()` wrappers for log statements, and debug/level-based logging through SLF4J.

`MeanStatistic` is the serializable mean accumulator used inside `IOStatistics`. It stores sample count plus sum, derives mean on demand, treats zero-sample values as empty, normalizes invalid sample counts to zero, supports copying/cloning, and exposes synchronized mutation and aggregation methods such as `setSamplesAndSum`, `setSamples`, `setSum`, `set`, `add`, and `addSample`. Its Javadoc highlights that equality for empty values ignores the sum, while non-empty equality requires both sample and sum equality.

`StoreStatisticNames` and `StreamStatisticNames` are public constant catalogs. Store names cover generic filesystem API operations (`OP_OPEN`, `OP_CREATE`, `OP_RENAME`, `OP_DELETE`, ACL/xattr setters/getters, status/list calls), delegation-token issuance, retry/throttle/request probes, object-store request families (list, delete, metadata, copy, PUT, multipart upload, select), suffixes for min/max/mean/failure statistics, HTTP method action names, and multipart-upload lifecycle counters. Stream names cover read/write lifecycle and I/O telemetry: bytes read/written, aborted/closed/opened reads, close and seek operations, discarded/skipped bytes, version mismatches, readFully/read/skip/unbuffer events, write upload queue/block activity, upload success/failure bytes, queue wait/put request durations, remote read counts, readahead bytes, buffer reads, and block allocation/release.

The HA section starts with exceptions: `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException`. `FenceMethod` requires `checkArgs(String)` and `tryFence(HAServiceTarget, String)`, where fencing can throw bad-configuration or unexpected exceptions and returns true only when the old active service has been successfully fenced. `HAServiceProtocol` declares the RPC-compatible service lifecycle protocol: `monitorHealth`, `transitionToActive`, `transitionToStandby`, `transitionToObserver`, `getServiceStatus`, and `versionID`. Transition methods take `StateChangeRequestInfo` and can fail through `ServiceFailedException`, `AccessControlException`, or `IOException`; status and health methods include health and service-failure exception paths. `HAServiceProtocolHelper` wraps those calls and is intended to convert protobuf/remote exceptions into the public Java exceptions. `HAServiceTarget` represents a concrete HA endpoint with service, health-monitor, and ZKFC addresses; fencer access and fencing validation; proxy creation with retry and timeout parameters; transition-target state storage; fencing parameter maps; auto-failover flag; and observer-support flag. `HAServiceProtocolPB` and `ZKFCProtocolPB` are protobuf blocking-service plus `VersionedProtocol` bridge interfaces.

The `org.apache.hadoop.io` segment starts with `AbstractMapWritable`, a `Writable`/`Configurable` base that tracks per-instance class-to-byte-id mappings. It exposes synchronized class registration, lookup by class or id, copy, and serialization/deserialization of class metadata. `MapWritable` builds a mutable `Map<Writable, Writable>` on that base, while `SortedMapWritable` builds sorted-map operations including first/last/head/sub/tail views. `ArrayWritable`, `TwoDArrayWritable`, and `ArrayPrimitiveWritable` cover array serialization: arrays of a declared `Writable` class, two-dimensional writable matrices, and primitive arrays with declared component type, direct wrapped value access, and no-copy behavior implied by the API docs. `GenericWritable` is a configurable tagged union over a subclass-supplied `Class[] getTypes()` whitelist.

Primitive and scalar writable wrappers include `BooleanWritable`, `ByteWritable`, `ShortWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, `DoubleWritable`, `VIntWritable`, and `VLongWritable`. Each exposes default and value constructors, `set`, `get`, `readFields`, `write`, equality, hashing, comparison, and stringification. `VIntWritable` and `VLongWritable` store values through Hadoop's variable-length integer encoding. `NullWritable` is the singleton zero-byte placeholder with `get()`, no-op read/write, compare/equality/hash behavior, and stringification.

`BinaryComparable` defines byte-array backed ordering and hashing through abstract `getBytes()` and `getLength()`. `BytesWritable` extends it with mutable capacity and logical length, direct buffer access, copying, resizing, setting from arrays or ranges, and writable serialization. `Text` extends `BinaryComparable` for standard UTF-8 text with constructors from string/text/bytes, copied and direct byte access, length, character lookup, substring find, several `set` overloads, append, clear, string conversion, deserialization with optional maximum length, skipping, known-length read, length-prefixed write, static UTF-8 decode/encode helpers, string read/write helpers, UTF-8 validation, code-point extraction from a `ByteBuffer`, `utf8Length`, and `DEFAULT_MAX_LEN`.

File/container APIs include `MapFile` static operations for rename, delete, fixing/rebuilding indexes, a CLI `main`, and `INDEX_FILE_NAME`/`DATA_FILE_NAME`; `ArrayFile` and `SetFile` extend `MapFile` for dense array-like and set-like stored data. `BloomMapFile` exposes `delete` and constants for `BLOOM_FILE_NAME` and `HASH_COUNT`. `SequenceFile` exposes default compression-type get/set, many overloaded `createWriter(...)` factories spanning old `FileSystem`/`Path` forms and newer `SequenceFile.Writer.Option...` forms, and `SYNC_INTERVAL`.

Utility and adaptation APIs include `ByteBufferPool` and `ElasticByteBufferPool` for direct/heap `ByteBuffer` reuse, `Closeable` as an `org.apache.hadoop.io` close contract, `CompressedWritable` for lazily inflated compressed fields, `DataOutputOutputStream` for adapting `DataOutput` to `OutputStream`, `DefaultStringifier` plus `Stringifier<T>` for serializing objects to/from strings in `Configuration`, `IOUtils` for copying bytes, compressed reads, full reads/skips, cleanup/close/socket close, `writeFully`, directory listing, `fsync`, exception wrapping, and reading an entire stream to a byte array, and `MD5Hash` for fixed-length MD5 values, digest helpers over strings/bytes/streams, half/quarter digest projections, comparison, and writable serialization.

`ObjectWritable` is the configurable general-purpose wrapper for arbitrary declared classes and values. It supports constructors with object or declared class/value, `get`, `getDeclaredClass`, `set`, `readFields`, `write`, static `writeObject` overloads including declared-class/configuration/allow-compact-array forms, static `readObject` overloads into an instance or as a return value, class loading, and configuration access. `RawComparator<T>` extends `Comparator<T>` with byte-range comparison for serialized forms. `Writable` declares the base `write(DataOutput)` and `readFields(DataInput)` protocol; `WritableComparable<T>` combines `Writable` with `Comparable<T>` and documents stable cross-JVM `hashCode()` as important for Hadoop partitioning. The chunk ends inside `WritableComparator`, showing protected constructors for key classes, including an overload with `Configuration` and instance creation control continuing into the next chunk.

## Control flow and behavior

Direct implementation flow is not present in the JDiff file, but the exposed contracts show several important flows. Statistics flow from individual stream/filesystem objects through `IOStatisticsSource` or direct `IOStatistics` references into `IOStatisticsSnapshot`, either by replacing the snapshot's maps through `snapshot(source)` or by adding values through `aggregate(source)`. Logging APIs are designed to avoid expensive string construction unless needed: callers can pass lazy stringifier objects to SLF4J, and debug helpers first check logging level before extracting/stringifying statistics.

Mean aggregation is sum/sample-count based. A caller records samples with `addSample(long)` or merges another statistic with `add(MeanStatistic)`; `mean()` then computes the arithmetic mean at read time. The synchronized accessors and mutators indicate the intended aggregation path preserves sum/sample consistency even when statistics are updated concurrently.

HA control flow is request/response RPC with explicit safety gates. A failover controller or health monitor obtains an `HAServiceProtocol` proxy from an `HAServiceTarget`, calls `monitorHealth()` and `getServiceStatus()`, then requests `transitionToStandby`, `transitionToActive`, or `transitionToObserver` with `StateChangeRequestInfo`. If the previous active cannot be trusted to stop, configured `FenceMethod` implementations validate arguments via `checkArgs` and attempt fencing via `tryFence` before the target state transition is considered safe. `HAServiceProtocolHelper` sits between protobuf transport exceptions and the public exception model.

Writable control flow is simple but pervasive: objects write their fields to `DataOutput` and restore into an existing instance through `readFields(DataInput)`, often reusing internal storage for efficiency. Comparable writables then support object-level `compareTo`, while `RawComparator`/`WritableComparator` enable sort paths to compare serialized byte ranges without fully materializing keys where optimized comparators exist. `AbstractMapWritable` and derived maps first maintain class-id metadata so arbitrary writable key/value classes can be reconstructed during deserialization.

Container/file APIs layer on the Writable protocol. `SequenceFile.createWriter` factories gather configuration, filesystem/path or writer options, key/value classes, compression choices, progress callbacks, checksums, metadata, replication/block-size settings, and codec settings before returning a writer. `MapFile`, `ArrayFile`, `SetFile`, and `BloomMapFile` build indexed or specialized storage formats around those sequence-file primitives.

## State and persistence behavior

`IOStatisticsSnapshot` is explicitly serializable and JSON-serializable. It stores statistic maps for counters, gauges, minimums, maximums, and mean values, using synchronized access for mutation and map exposure. The Javadocs warn that Java deserialization from untrusted streams is unsafe and provide `requiredSerializationClasses()` for controlled deserialization. `MeanStatistic` is also serializable and Jackson-friendly, with mutable sum/sample state and input sanitization for invalid sample counts.

`StoreStatisticNames` and `StreamStatisticNames` persist no runtime state; they are compatibility-sensitive public constants used as metric keys across filesystem, object-store, and stream implementations. Any rename or semantic drift would break dashboards, tests, and consumers that aggregate by string key.

HA objects mostly represent client-side connection and control metadata. `HAServiceTarget` carries addresses, fencer/proxy construction behavior, fencing parameter maps, auto-failover/observer capability flags, and a transition target state. Service state persistence itself is external to these APIs: the managed NameNode or other HA service owns active/standby/observer state, while ZooKeeper failover controller state is reached through `ZKFCProtocol`.

The `org.apache.hadoop.io` types are persistence contracts. Primitive writables, `Text`, `BytesWritable`, array/map writables, `ObjectWritable`, `VersionedWritable`, `MD5Hash`, and file-format helpers define on-wire or on-disk binary forms consumed by MapReduce, RPC, `SequenceFile`, `MapFile`, configuration stringification, and legacy Hadoop data. Mutable wrappers expose internal buffers in places (`BytesWritable.getBytes`, `Text.getBytes`, primitive arrays in `ArrayPrimitiveWritable`), so persisted content can change if callers mutate after setting but before writing.

`CompressedWritable` persists compressed representations and inflates lazily through `ensureInflated()`, deferring object-field reads until needed. `VersionedWritable` persists a version byte ahead of subclass fields and rejects mismatches with `VersionMismatchException`, letting subclasses handle schema evolution explicitly.

## Dependencies and integration points

The statistics APIs integrate with `org.apache.hadoop.fs.statistics.IOStatistics`, `IOStatisticsSource`, `DurationTracker`, `DurationTrackerFactory`, `MeanStatistic`, `JsonSerialization`, Java serialization, Jackson JSON serialization, `Map`, `List`, and SLF4J `Logger`. Metric-name constants integrate with filesystem implementations, object-store connectors, stream wrappers, and external metrics/logging consumers.

HA APIs integrate with Hadoop IPC and security: `VersionedProtocol`, generated protobuf blocking interfaces, `StateChangeRequestInfo`, `HAServiceStatus`, `HAServiceProtocol.HAServiceState`, `NodeFencer`, `ZKFCProtocol`, `InetSocketAddress`, `Configuration`, `AccessControlException`, and `UserGroupInformation`-backed proxy creation paths implied by the target/protocol layer. They are common contracts for HDFS NameNode HA and any other Hadoop service implementing the same lifecycle model.

The IO package depends on Java `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `FileDescriptor`-like stream behavior through utilities, `ByteBuffer`, `MessageDigest`, collections (`Map`, `SortedMap`, `Collection`, `Iterator`, `EnumSet`), `Comparator`, reflection/class loading, `Configuration`, `Configurable`, `FileSystem`, `Path`, `Progressable`, compression codec classes, and Hadoop's `WritableUtils`/serialization ecosystem. `SequenceFile` and `MapFile` are integration points for MapReduce intermediate data, old Hadoop storage files, and sorted key/value datasets.

## Risks and edge cases

- This file is an API compatibility baseline. Signature, visibility, exception, deprecation, or constant-name changes in these entries can be externally visible even when implementation code remains source-compatible.
- `IOStatisticsSnapshot.snapshot(...)` is documented as replacing map data and `IOStatisticsSupport.snapshotIOStatistics(...)` is not atomic. Consumers comparing live metrics must tolerate race windows and partial interleavings.
- Java object deserialization of `IOStatisticsSnapshot` is explicitly unsafe for untrusted streams; tests and consumers should prefer JSON or controlled class allowlists when crossing trust boundaries.
- `MeanStatistic` equality and hash code are mutable and depend on current sample/sum state. Using a live statistic as a hash-map key is risky after updates, and empty-stat equality ignores sum.
- Metric constants are public integration keys. Removing or repurposing operation names, suffixes, or stream counters can break metrics dashboards and connector tests.
- HA transitions are safety-critical. Missing fencing, bad fencing args, access-control failures, remote exception wrapping, observer-state support differences, or stale transition-target state can lead to split-brain or failed failover.
- `FenceMethod.tryFence` returning false is semantically distinct from throwing bad configuration or unexpected errors; callers must handle all three outcomes.
- Many writable wrappers are mutable and expose backing arrays/buffers. Direct mutation after insertion into maps, sorting structures, or before serialization can corrupt keys or persisted values.
- `AbstractMapWritable` uses byte class ids, so large heterogeneous maps have a practical class-id limit. Deserialization also depends on the embedded class mappings being consistent and loadable.
- `ObjectWritable` depends on class names and reflective loading. It can fail when classes are missing, renamed, shaded, or restricted, and it needs care around compact primitive array/object encoding.
- `Text` validates UTF-8 and has maximum-length paths. Invalid byte sequences, length overflows, `charAt` on byte offsets rather than Java char indexes, and mutable direct byte access are common sources of bugs.
- `RawComparator` implementations must match object-level `compareTo` ordering. Divergence can corrupt `SequenceFile`/MapReduce sorting and grouping.
- `IOUtils.cleanup` style helpers intentionally swallow/log close errors; cleanup paths must not hide primary failure signals unintentionally.

## Test signals

Useful verification for code touching these APIs should include:

- API compatibility tests parsing this JDiff baseline for all public `fs.statistics`, `ha`, protobuf bridge, and `io` signatures in this line range, including overload counts and declared exceptions.
- Statistics tests for counter/gauge/min/max/mean map exposure, snapshot replacement, aggregate-null false returns, aggregate value semantics, lazy logging stringifiers, pretty output ordering/filtering, and no-op duration tracker behavior.
- `MeanStatistic` tests for zero/negative sample handling, empty equality, synchronized `add`/`addSample` consistency, copy/clone behavior, JSON/Java serialization round trips, mean calculation, and mutable hash-code warnings.
- Metric-name tests in filesystem and object-store connectors verifying expected `StoreStatisticNames` and `StreamStatisticNames` keys are emitted for open/create/delete/list/read/write/multipart/retry/throttle/seek paths.
- HA tests for health checks, active/standby/observer transitions, status retrieval, helper exception unwrapping, fencing argument validation, failed/false/exceptional fencing outcomes, proxy construction timeouts, fencing parameter injection, auto-failover flags, and unsupported observer targets.
- Writable round-trip tests for every primitive wrapper, variable-length integer wrappers, `NullWritable`, `BytesWritable`, `Text`, `ArrayWritable`, `TwoDArrayWritable`, `ArrayPrimitiveWritable`, `MapWritable`, `SortedMapWritable`, `GenericWritable`, `ObjectWritable`, `MD5Hash`, `CompressedWritable`, and `VersionedWritable` version mismatch behavior.
- Comparator tests confirming object-level and raw-byte ordering agree for `BinaryComparable`, `Text`, numeric writables, and custom `WritableComparable` implementations registered with `WritableComparator`.
- File-format tests for `SequenceFile.createWriter` overloads/options, compression type defaults, sync interval behavior, `MapFile` rename/delete/fix, and `ArrayFile`/`SetFile` compatibility.
- Utility tests for `ByteBufferPool` reuse/directness, `DataOutputOutputStream` write delegation, `DefaultStringifier` store/load and array store/load in `Configuration`, `IOUtils.copyBytes/readFully/skipFully/writeFully/fsync/wrapException/readFullyToByteArray`, and cleanup/close behavior under secondary exceptions.

### subset-b-007215: lines 24647-30892

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 24647-30892

Chunk id: `subset-b-007215`
Source: `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml`
Line range: 24647-30892

## Research Scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.3.4, not Java implementation source. It records public and protected API shape, inheritance, declared exceptions, fields, synchronization markers, deprecation markers, and embedded Javadocs. The range starts in the middle of `org.apache.hadoop.io.WritableComparator`, covers Hadoop Writable utility APIs, compression APIs, TFile and serializer APIs, a large part of the metrics2 API and sink library, and ends at the beginning of `org.apache.hadoop.net.AbstractDNSToSwitchMapping`.

## Purpose

The chunk documents several reusable Hadoop Common surfaces:

- Writable comparison, instantiation, compact binary encoding, and safe string/enum serialization helpers.
- Stream-based compression/decompression contracts, codec discovery, codec pooling, splittable compression, direct `ByteBuffer` decompression, and concrete BZip2/GZip/default/pass-through codec wrappers.
- Erasure-code schema metadata and TFile-facing raw comparison, compression naming, and variable-length utility functions.
- Java, Writable, and Avro serialization adapters used by Hadoop's configurable serialization framework.
- Log event counting and the metrics2 framework: immutable metrics, collectors, record builders, filters, system lifecycle hooks, mutable counters/gauges/stats/rates/quantiles, output sinks, MBean registration, sparse-update caching, and server-address parsing.
- The opening of the network topology DNS-to-switch mapping base class, where configuration and single-switch topology diagnostics begin.

Because the source is an API descriptor, behavior below is inferred from signatures and Javadocs rather than method bodies.

## Important APIs, Types, and Functions

`org.apache.hadoop.io.WritableComparator` implements `RawComparator` and `Configurable`. This chunk includes its protected configuration-aware constructor and the public comparator registry and comparison helpers: `get(Class)`, `get(Class, Configuration)`, `define(Class, WritableComparator)`, `getKeyClass`, `newKey`, object and raw-byte `compare` overloads, `compareBytes`, `hashBytes`, primitive byte-array readers, and byte-array VInt/VLong readers. The key integration point is optimized raw comparison for `WritableComparable` implementations, especially sort-heavy paths such as `SequenceFile.Sorter`.

`WritableFactories` and `WritableFactory` provide factory registration for non-public or special-case `Writable` implementations. `setFactory`, `getFactory`, and `newInstance` let `ObjectWritable` and related serializers instantiate classes that reflection alone may not construct cleanly.

`WritableUtils` collects low-level Hadoop binary helpers: compressed byte arrays and strings, string arrays, plain UTF strings, byte-array display, cloning via serialization, deprecated `cloneInto`, zero-compressed `writeVInt`/`writeVLong` and `readVInt`/`readVLong`, range-checked VInt reads, VInt sign/size helpers, enum read/write, exact skipping, multi-writable byte-array packing, and bounded `readStringSafely`. Its public contract is the stable wire format used across Hadoop RPC, filesystem metadata, and older file formats.

The `org.apache.hadoop.io.compress` package in this chunk defines the core compression abstraction. `CompressionCodec` is the central streaming codec interface, with methods to create input/output streams with or without pooled compressors/decompressors, report compressor/decompressor implementation classes, allocate new codec engines, and return a default filename extension. `SplittableCompressionCodec` adds split-aware input construction for block readers that need adjusted start/end positions.

`Compressor` and `Decompressor` are stateful stream-engine contracts. They expose `setInput`, dictionary setup, progress counters or remaining-byte counters, `needsInput`, `needsDictionary`, `finish`, `finished`, `compress`/`decompress`, `reset`, `end`, and, for compressors, `reinit(Configuration)`. `DirectDecompressionCodec` and `DirectDecompressor` add direct `ByteBuffer` decompression support.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases. The input side extends `InputStream`, implements `Seekable` and `IOStatisticsSource`, carries protected `in` and `maxAvailableData`, and declares read, reset, position, unsupported seek, and statistics behavior. The output side extends `OutputStream`, implements `IOStatisticsSource`, wraps protected `out`, and defines compressed write, `finish`, `resetState`, flush/close, and statistics behavior.

`CompressorStream`, `DecompressorStream`, `BlockCompressorStream`, and `BlockDecompressorStream` are reusable stream implementations around compressor/decompressor engines. They maintain protected engine references, buffers, EOF/closed state, implement read/write loops, finish/close/reset behavior, and block-oriented compressed-data framing.

Concrete and utility compression classes include:

- `BZip2Codec`, a `Configurable` `SplittableCompressionCodec` with split-aware BZip2 streams and `.bz2` extension handling.
- `DefaultCodec`, a `Configurable` codec with direct decompression support.
- `GzipCodec`, a `DefaultCodec` subclass for gzip compressor/decompressor creation and extension handling.
- `PassthroughCodec`, a non-transforming codec with configurable extension constants for workflows that want codec plumbing without compression.
- `SplitCompressionInputStream`, which records adjusted split start/end after codec stream creation.
- `CodecConstants`, which centralizes default extensions for default, BZip2, GZip, LZ4, pass-through, Snappy, and ZStandard codecs.
- `CodecPool`, a global compressor/decompressor pool with leased-object counts and return methods.
- `CompressionCodecFactory`, which discovers codecs from `io.compression.codecs` and Java `ServiceLoader`, maps file extensions and codec names/classes to codec instances, removes suffixes, and has a small test `main`.

`ECSchema` is a serializable erasure coding schema object. Constructors accept option maps or the core tuple of codec name, data units, and parity units. Accessors expose codec name, extra options, data-unit count, parity-unit count, and standard equality/hash/string behavior. Public keys include `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.

The TFile section defines `MetaBlockAlreadyExists`, `MetaBlockDoesNotExist`, `RawComparable`, `TFile`, and `Utils`. `RawComparable` exposes backing byte array, offset, and size for raw comparator use. `TFile` declares compression constants (`gz`, `lzo`, `none`), comparator constants (`memcmp`, Java-class prefix), `makeComparator`, supported compression algorithm listing, and an inspection `main`. `Utils` provides TFile-specific VInt/VLong and string read/write helpers plus lower/upper-bound binary search overloads over comparable lists and custom comparators.

Serialization adapters include `JavaSerialization`, `JavaSerializationComparator`, `WritableSerialization`, `AvroReflectSerializable`, `AvroReflectSerialization`, `AvroSerialization`, and `AvroSpecificSerialization`. The Java and Avro classes implement or extend Hadoop's `Serialization`/`DeserializerComparator` framework. `AvroSerialization` exposes `AVRO_SCHEMA_KEY`; reflect serialization exposes `AVRO_REFLECT_PACKAGES`; `WritableSerialization` delegates to the `Writable` contract.

`EventCounter` is a Log4J `AppenderSkeleton` that counts logging events by severity and implements `append`, `close`, and `requiresLayout`.

The `org.apache.hadoop.metrics2` package supplies the core metrics model. `AbstractMetric` is an immutable metric implementing `MetricsInfo`, with `value`, `type`, visitor dispatch, equality, hash, and string conversion. `MetricsInfo`, `MetricsTag`, `MetricsRecord`, and `MetricsCollector` define immutable metadata, tag, record snapshot, and collector contracts. `MetricsRecordBuilder`, `MetricsJsonBuilder`, and `MetricStringBuilder` build records in fluent form with tags, context, counters, gauges, parent collectors, and string/JSON dump support.

Metrics lifecycle and plugin APIs include `MetricsPlugin.init(SubsetConfiguration)`, `MetricsSink.putMetrics/flush`, `MetricsSource.getMetrics`, `MetricsFilter.accepts` overloads for names/tags/tag collections/records, `MetricsSystem.register`, `unregisterSource`, callback registration, immediate publication, and shutdown, plus `MetricsSystemMXBean` start/stop/MBean lifecycle/current-config operations.

Metrics library classes in `org.apache.hadoop.metrics2.lib` provide the mutable source-side implementation layer. `DefaultMetricsSystem` is the daemon-wide singleton enum with initialize, instance, shutdown, mini-cluster mode setters, and mini-cluster mode query. `Interns` creates interned `MetricsInfo` and `MetricsTag` objects. `MetricsRegistry` creates, stores, tags, and snapshots mutable counters, gauges, quantiles, stats, rates, aggregated rates, and rolling averages.

Mutable metric classes include `MutableMetric` with changed-state tracking and conditional snapshots; `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong`; `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong`; `MutableQuantiles` with rolling interval, estimator access, previous snapshot, and `stop`; `MutableRate`; `MutableRates`; `MutableRatesWithAggregation`; `MutableRollingAverages`, which is `Closeable` and supports thread-local state collection and test-only record-validity tuning; and `MutableStat`, a synchronized sample-stat metric with extended stats, timestamp updates, bulk sample adds, single-value adds, snapshots, last-stat access, min/max reset, and snapshot timestamp.

Metrics sinks include `FileSink`, `GraphiteSink`, `RollingFileSystemSink`, and `StatsDSink`. The simple sinks implement `MetricsSink` and `Closeable` with `init`, `putMetrics`, `flush`, and `close`. `RollingFileSystemSink` writes metrics logs through `FileSystem`, rolls directories by interval, can add randomized roll offsets, writes host log files under a base path, supports append where the target filesystem does, and has protected fields for source, error handling, append behavior, base path, roll timings, next flush, static test hooks, supplied configuration, and supplied filesystem. `StatsDSink` formats records for a StatsD daemon and exposes `writeMetric`.

Metrics utilities include `MBeans.register` overloads with Hadoop's `hadoop:service=...,name=...` naming convention, `getMbeanNameService`, `getMbeanNameName`, and `unregister`; `MetricsCache`, which caches records for sinks that cannot consume sparse updates; and `Servers.parse`, which turns comma/space-separated `host` or `host:port` specifications into socket-address lists with localhost fallback.

The chunk ends at the start of `AbstractDNSToSwitchMapping`, an abstract `DNSToSwitchMapping` and `Configurable` base. The visible portion includes protected constructors, one configuration-aware constructor that explicitly does not call `setConf`, and the beginning of `getConf`.

## Control Flow and Behavior

Writable comparison flow is registry-driven. Callers ask `WritableComparator.get` for a comparator for a `WritableComparable` class; registered comparators can override raw-byte comparison. If raw comparison is not specialized, the documented default is to deserialize the byte slices into key objects using `Writable.readFields` and then call the object comparator, which normally delegates to natural `Comparable.compareTo`.

Writable instantiation flow is factory-first. Code that needs a `Writable` instance can consult `WritableFactories`; registered factories allow non-public or otherwise special classes to participate in `ObjectWritable` and generic deserialization paths.

Variable-length integer control flow is byte-header based. `WritableUtils` and TFile `Utils` write a one-byte representation for values in the small range and use leading marker bytes to indicate sign and following byte count for larger integers. Read paths interpret the first byte with sign and size helpers, then consume the required number of high-non-zero-byte-first payload bytes. Range-checked reads add a validation layer after decoding.

Compression control flow is stream and pool oriented. A codec creates streams either with newly created engines or with engines supplied by `CodecPool`. Writers feed uncompressed bytes to `CompressorStream` or block compressor streams, call `finish` to drain compressed output, and return compressors to the pool after close/reset. Readers feed compressed bytes to `DecompressorStream` or block decompressor streams, refill when `needsInput` is true, surface EOF and availability, and reset state when reused for another logical stream.

Codec discovery flow in `CompressionCodecFactory` starts from configuration and service discovery, then builds mappings by extension, canonical class name, and short name. File readers can ask for a codec by `Path`; tools can use `removeSuffix` to derive uncompressed names.

Splittable compression flow gives the codec both the seeked input stream and the requested split boundaries. The resulting `SplitCompressionInputStream` can report adjusted boundaries because some codecs need to move to compression-block-safe positions.

Metrics collection flow starts at a `MetricsSource.getMetrics` callback, where sources populate a `MetricsCollector` using `MetricsRecordBuilder`. Mutable metrics in a `MetricsRegistry` snapshot their current values into builders, optionally only when changed. Metrics filters accept or reject records by name, tags, or record contents. The `MetricsSystem` coordinates source registration, immediate publication, sink delivery, JMX lifecycle, and shutdown.

Metrics sink flow is push-based. The metrics system calls `putMetrics(record)` for each record and then `flush` as needed. File-like sinks serialize records to a stream or external service. `RollingFileSystemSink` adds roll scheduling: initial flush time is offset randomly within a configured bound, later flushes preserve that offset by adding integer roll intervals, and output moves to a new interval directory when the roll boundary passes.

MBean flow is conventional JMX registration. Hadoop code registers an object with service/name properties, optionally adding more key-value properties, and unregisters by the returned `ObjectName`.

The visible network-topology flow is only partial. `AbstractDNSToSwitchMapping` constructors store or defer configuration setup; later methods in the next chunk complete mapping, diagnostics, and single-switch policy behavior.

## State and Persistence Behavior

Most classes in this chunk are API-level wrappers over external or transient state rather than durable stores.

Writable wire state is persistent by contract. `WritableUtils`, `WritableComparator`, factory registration, serializer adapters, and TFile utilities encode data that may cross RPC boundaries or be stored in Hadoop sequence/file formats. Any incompatible change to VInt/VLong, strings, enum names, or Writable instantiation changes persisted data compatibility.

Compression state is per engine and per stream. `Compressor`/`Decompressor` instances hold input/output buffers, dictionaries, byte counters, finish flags, and native or Java codec state until `reset` or `end`. `CodecPool` adds process-global leased-object state and exposes leased counts, so missing returns can create resource leaks and skew diagnostics. `CompressionInputStream` and `CompressionOutputStream` hold the wrapped streams and expose IO statistics from underlying streams when available.

`ECSchema` is serializable metadata. Its durable identity is the codec name, data/parity unit counts, and extra options map. Equality and hash behavior make those fields relevant for configuration comparisons and policy lookups.

TFile metadata and raw comparator behavior depend on string constants for compression and comparator names. `RawComparable` instances expose borrowed byte-array ranges, so state is external to the object and can be invalidated or mutated if backing buffers are reused.

Metrics state is in mutable metrics and registries. Counters monotonically increase; gauges move up/down or can be set; stats aggregate samples, min/max, mean, and optional extended statistics; quantiles maintain rolling online estimators and previous snapshots; rolling averages keep per-name aggregate state and thread-local contributions. `MutableMetric.changed` gates sparse snapshots and must be set/cleared correctly around mutations and snapshots.

Metrics sink state varies by destination. `RollingFileSystemSink` holds configuration-derived fields and writes durable log files to a `FileSystem` path. It may create interval directories, create sequence-suffixed files when append is unavailable or disabled, append to existing files when allowed, and preserve roll timing in `nextFlush`. Static fields such as `forceFlush`, `hasFlushed`, `suppliedConf`, and `suppliedFilesystem` are visible test hooks and can affect process-wide behavior.

`MBeans` state is held in the platform MBean server under generated `ObjectName`s. `MetricsCache` keeps recent record/tag/metric values so sinks that do not support sparse updates can emit complete records even when updates contain only changed fields.

The beginning of `AbstractDNSToSwitchMapping` shows cached `Configuration` state, but the full mapping cache and diagnostics surface continue beyond this chunk.

## Dependencies and Integration Points

The IO APIs integrate with Hadoop core types such as `Configuration`, `Configurable`, `Writable`, `WritableComparable`, `RawComparator`, `DataInput`, `DataOutput`, `ObjectWritable`, `ReflectionUtils`, `Text`, `Path`, and TFile internals. Serializer adapters integrate with the Hadoop serialization SPI and with Java serialization, Writable serialization, and Avro reflect/specific classes.

Compression APIs depend on Java streams, `ByteBuffer`, Hadoop `Seekable`, Hadoop filesystem IO statistics, codec implementations such as BZip2/GZip/LZ4/Snappy/ZStandard outside this exact chunk, Java `ServiceLoader`, and configuration key `io.compression.codecs`. Native-code-backed codecs must honor `end`/`reset` contracts to avoid native resource leaks.

Erasure coding schema metadata integrates with HDFS and other erasure-code policy code that consumes codec names and unit counts.

Metrics APIs depend on `org.apache.commons.configuration2.SubsetConfiguration`, SLF4J logging, Log4J for `EventCounter`, Hadoop metrics annotations, `com.google.re2j.Pattern` for glob and regex filters, JMX `ObjectName`, `FileSystem`/`Path` for rolling file logs, network sockets for Graphite and StatsD, and quantile/stat utility classes in `org.apache.hadoop.metrics2.util`.

`RollingFileSystemSink` integrates directly with configured filesystems including HDFS, local filesystems, S3-like filesystems, and security configuration for Kerberos keytab/principal lookup. Its Javadocs explicitly call out HDFS append and file-size visibility behavior.

`AbstractDNSToSwitchMapping` integrates with `DNSToSwitchMapping`, `Configuration`, and later topology-aware block placement and rack-policy code.

## Risks and Edge Cases

- This file is generated JDiff XML. It is useful for API compatibility research but not enough to prove implementation details such as exact locking, error handling, or allocation behavior.
- `WritableComparator.define` requires registered comparators to be thread-safe. An optimized raw comparator that reuses mutable state unsafely can corrupt sort results under concurrent use.
- The default raw comparator path deserializes both keys before comparison; it is correct but expensive and can surface `readFields` compatibility bugs during sort.
- `WritableFactories` are process-global registration points. Wrong factories can instantiate incompatible classes for persisted data.
- `WritableUtils.cloneInto` is deprecated in favor of `ReflectionUtils.cloneInto`; users retaining the old API carry migration risk.
- VInt/VLong formats are compatibility-critical. Boundary values around `-112`, `127`, negative markers, and long/int range narrowing are high-risk.
- `readStringSafely` exists because unbounded string lengths are unsafe; callers that use plain string reads on untrusted input may allocate excessively or accept malformed data.
- Compression streams are stateful and close-sensitive. Failing to call `finish`, `reset`, `end`, or `CodecPool.return*` can lose trailing compressed bytes, poison reused engines, or leak native buffers.
- Dictionary support is optional and codec-specific. Callers must handle `needsDictionary` rather than assuming all streams are self-contained.
- `CompressionInputStream.seek` and `seekToNewSource` are documented as unsupported at the base level. Split readers must use codec-specific split APIs rather than assuming arbitrary seeking works.
- `SplittableCompressionCodec` can adjust requested split start/end positions, so callers must use `getAdjustedStart` and `getAdjustedEnd` for record-boundary correctness.
- `PassthroughCodec` intentionally does not transform bytes. Misconfiguration can make files look codec-managed by extension while providing no compression.
- `CompressionCodecFactory` behavior depends on classpath service discovery and configured codec classes; ambiguous extensions or missing service entries can change which codec is selected.
- TFile `RawComparable` exposes raw buffers by reference. Buffer reuse or mutation can break comparator results.
- Avro serialization depends on schema configuration and class category; reflect vs specific acceptance must match configured packages and Avro schemas.
- Metrics mutable classes mix synchronized and unsynchronized methods. `MutableStat.add` and snapshot methods are synchronized, but callers still need to respect per-metric thread-safety assumptions and registry-level concurrency.
- Bulk `MutableStat.add(numSamples, sum)` preserves mean but Javadoc warns variance can be inaccurate for large sample counts due to a single Welford step.
- Sparse metrics snapshots rely on `changed` flags. Missing `setChanged` calls produce silent under-reporting for sinks that only receive changed metrics.
- `MutableQuantiles` and `MutableRollingAverages` own background or thread-local/rolling state and expose `stop`/`close`; failure to close can leak scheduled work or stale state.
- `RollingFileSystemSink` has subtle operational behavior: `ignore-error` wording in the Javadoc says the default is true but also describes throwing behavior in a confusing way; append support varies by filesystem; sequence-suffixed files have newest-as-highest semantics; HDFS append can appear successful with too few datanodes but later fail on read; HDFS file sizes may not update until close.
- `RollingFileSystemSink` static test hooks can affect all instances in a JVM. Tests must isolate or reset them.
- StatsD and Graphite sinks depend on external daemons and network availability; metric naming must avoid collisions after hostname skipping, service naming, context, record, and metric name concatenation.
- MBean registration can collide if service/name/properties are reused without unregistering.
- `Servers.parse` has default-localhost behavior for null specs; unintended null configuration can silently target localhost.
- This chunk ends mid-`AbstractDNSToSwitchMapping`; final file synthesis must merge with the next chunk before drawing conclusions about topology cache behavior.

## Test Signals

Useful tests for code using or modifying APIs in this chunk should include:

- Writable comparator tests for registry lookup, custom raw comparator ordering, object comparator fallback, byte-array primitive readers, VInt/VLong byte-array reads, hash/lexicographic byte comparison, and thread-safety under concurrent sorts.
- Writable factory tests for non-public `Writable` classes, configuration-aware instantiation, missing factory fallback, and wrong-factory failure modes.
- `WritableUtils` compatibility tests for compressed byte/string arrays, plain string arrays, enum read/write by name, `skipFully` short streams, `toByteArray`, `readStringSafely` maximum length rejection, and VInt/VLong boundary values.
- Compression lifecycle tests for each codec class: create stream with new and pooled engines, write/read round trip, `finish` before close, reset and reuse, `end` release, dictionary-needed paths, byte counters, and leased count returning to zero in `CodecPool`.
- Split compression tests for BZip2 and any other splittable codec, validating adjusted start/end and record-boundary behavior across split edges.
- `CompressionCodecFactory` tests for configured codec classes, service-loaded codecs, extension lookup, name/class lookup, ambiguous names, suffix removal, and missing codec behavior.
- Direct decompression tests for `DefaultCodec`/`GzipCodec` direct decompressor creation and `ByteBuffer` input/output position updates.
- `PassthroughCodec` tests proving identity byte behavior and configurable/default extension handling.
- `ECSchema` tests for constructor option parsing, equality/hash, extra-option retention, invalid/missing option handling, and string output.
- TFile utility tests for raw comparator creation, supported compression algorithm names, VInt/VLong and string encoding compatibility, and lower/upper-bound behavior with duplicate keys and custom comparators.
- Serialization tests for Java, Writable, Avro reflect, and Avro specific classes, including schema-key configuration, package filtering for reflect serialization, and comparator behavior.
- Metrics record-builder tests for tag/context/counter/gauge additions, JSON/string output, visitor callbacks for all numeric types, and immutable metric/tag equality.
- Metrics registry tests for duplicate metric/tag names, counter monotonicity, gauge increment/decrement/set, changed-flag sparse snapshots, all-vs-changed snapshots, and registry context tagging.
- `MutableStat`, `MutableRate`, `MutableQuantiles`, `MutableRatesWithAggregation`, and `MutableRollingAverages` tests for concurrent adds, snapshots, min/max reset, extended stats, rolling interval rollover, close/stop cleanup, test-only validity tuning, and bulk-sample variance caveats.
- Metrics system tests for source registration/unregistration, duplicate source names, callback registration, immediate publish, shutdown idempotence, MXBean start/stop/config methods, and mini-cluster mode behavior.
- Metrics filter tests for glob/regex compilation with RE2J and acceptance/rejection by metric name, tags, tag collections, and records.
- Sink tests for `FileSink`, `GraphiteSink`, and `StatsDSink` initialization, record formatting, flush/close exception handling, hostname skipping, service-name configuration, and external-service failure behavior.
- `RollingFileSystemSink` tests for roll interval parsing and minimums, initial random offset bounds, preserved offset across rolls, base path defaulting, sequence-suffix creation when append is disabled, append-enabled behavior on append-capable filesystems, error handling under `ignore-error`, Kerberos keytab/principal configuration, HDFS-like delayed size visibility assumptions, and reset of static test hooks.
- `MBeans` tests for object-name construction, extra properties, duplicate registration, extraction of service/name fields, and unregister idempotence.
- `MetricsCache` tests for sparse update completion, tag-including and tag-excluding updates, maximum records per name eviction, and lookup by name/tag collection.
- `Servers.parse` tests for null specs, comma and whitespace separation, default port injection, explicit ports, IPv6 or malformed host strings if supported by implementation, and localhost fallback.

## Cross-Chunk Notes

This chunk starts after the declaration and earlier constructors of `WritableComparator`, so the previous chunk contains that class opening. It ends inside `AbstractDNSToSwitchMapping`; the next chunk must be consulted for the rest of topology mapping behavior, including any switch-map cache fields, resolution APIs, reload behavior, and diagnostics.

### subset-b-007216: lines 30893-37013

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 30893-37013

## Scope

This chunk is a JDiff public API slice for Hadoop Common 3.3.4. It begins in the tail of `org.apache.hadoop.net.AbstractDNSToSwitchMapping` and ends in the middle of `org.apache.hadoop.util.Shell.getQualifiedBinPath`; the complete `Shell` class continues in the next chunk. Because this is generated JDiff XML, the source exposes API signatures, inheritance, visibility, deprecation state, exceptions, fields, and embedded Javadoc, but not implementation bodies.

The covered APIs are grouped around Hadoop's shared runtime infrastructure: network/rack resolution, security identity and token handling, HTTP security filters, service lifecycle management, service launcher exits, and low-level utility classes.

## Network Topology And Socket APIs

Lines 30893-31412 cover `org.apache.hadoop.net` APIs:

- `AbstractDNSToSwitchMapping` tail exposes `setConf(Configuration)`, `isSingleSwitch()`, `getSwitchMap()`, `dumpTopology()`, protected `isSingleSwitchByScriptPolicy()`, and static `isMappingSingleSwitch(DNSToSwitchMapping)`. The class is documented as a preferred base for pluggable DNS-to-switch mappings and deliberately does not extend `Configured` because superclass construction would call subclass `setConf()` too early.
- `CachedDNSToSwitchMapping` wraps a protected final `DNSToSwitchMapping rawMapping`, implements `resolve(List)`, exposes a diagnostic copy of host-to-rack cache via `getSwitchMap()`, delegates `isSingleSwitch()` to `AbstractDNSToSwitchMapping.isMappingSingleSwitch`, and supports `reloadCachedMappings()` for all or selected names.
- `DNSToSwitchMapping` is the core interface: `resolve(List)` must return a same-sized list of network paths, and cache reload methods either clear all mappings or specific nodes. The Javadoc says unresolved names should conventionally map to `NetworkTopology.DEFAULT_RACK`.
- `ScriptBasedMapping` extends `CachedDNSToSwitchMapping`, with constructors for default config, raw mapping, or `Configuration`. Its configuration is driven by `CommonConfigurationKeys.NET_TOPOLOGY_SCRIPT_FILE_NAME_KEY`; the outer class caches results while an inner raw script mapping executes configured scripts.
- `TableMapping` also extends `CachedDNSToSwitchMapping` and offers `getConf()`, `setConf(Configuration)`, and `reloadCachedMappings()`, indicating a config-driven static mapping source.
- `SocksSocketFactory` and `StandardSocketFactory` both extend `javax.net.SocketFactory` and expose the usual five `createSocket` overloads. `SocksSocketFactory` is also `Configurable`, supports a `Proxy` constructor, and defines `equals`/`hashCode`; `StandardSocketFactory` is the direct socket implementation.
- `ConnectTimeoutException` extends `SocketTimeoutException` and is thrown by `NetUtils.connect(...)` when a socket connect times out.

Control flow is mostly contract based: callers resolve host names through a `DNSToSwitchMapping`, often a cached wrapper, then Hadoop placement/topology logic can query whether the mapping is single-switch. Socket factories are reflection-friendly via default constructors and integrate with Hadoop configuration where proxies are needed.

State is in-memory: cached DNS-to-rack entries, table/script configuration, and proxy configuration. The key risk is stale topology data unless reload APIs are invoked after script/table changes. Another risk is return-list cardinality from `resolve(List)`: consumers expect one returned path per input name.

## Core Security APIs

Lines 31417-32931 cover `org.apache.hadoop.security`:

- `AccessControlException` is the base `IOException` for access-denied failures with default, message, and cause constructors.
- `Credentials` is `Writable` storage for delegation tokens and secret keys. It supports token CRUD by `Text` alias, unmodifiable token/secret maps, token count and secret count, static `readTokenStorageFile(Path|File, Configuration)`, stream/file writers with optional `Credentials.SerializedFormat`, `write(DataOutput)`, `readFields(DataInput)`, and merge/copy helpers. `addAll()` overwrites existing entries; `mergeAll()` preserves existing entries.
- `GroupMappingServiceProvider` defines user-to-groups lookup plus cache refresh and cache injection. `IdMappingServiceProvider` maps users/groups to UID/GID and supports "allowing unknown" variants.
- `KerberosAuthException` captures unrecoverable Kerberos login/logout or invalid-subject failures. It carries optional user, principal, keytab, ticket-cache, and initial-message fields, and customizes `getMessage()`.
- `SecurityUtil` is a final static utility class. It configures security state, checks original TGTs, expands server principals with host substitution, logs in from keytab/principal config, builds delegation-token service names from URIs or socket addresses, looks up `KerberosInfo`/client principal/`TokenInfo` through security providers, manipulates token service fields, runs privileged actions as login/current user, reads authentication method from configuration, checks privileged ports, and parses ZK auth info.
- `UserGroupInformation` is the central identity abstraction. It has static initialization/configuration and metrics hooks, security-enabled checks, current/login-user lookup, ticket-cache and subject construction, keytab login/logout/relogin flows, ticket-cache relogin, remote/proxy/testing user factories, user and group accessors, token and token-identifier attachment, credentials aggregation, authentication method getters/setters, equality/hash, subject exposure, `doAs` privileged execution, logging, and a `main` helper. Public fields identify token-file environment/property names: `HADOOP_TOKEN_FILE_LOCATION` and `HADOOP_TOKEN`.
- `UserGroupInformation.AuthenticationMethod` is an enum bridge to `SaslRpcServer.AuthMethod`, with `values()`, string `valueOf`, `getAuthMethod()`, and reverse `valueOf(AuthMethod)`.

The security flow is centered on UGI: configuration selects simple or Kerberos authentication, login material may come from local user, keytab, ticket cache, or subject, and downstream code executes via `doAs`. `SecurityUtil` adapts protocol metadata, principals, and delegation-token service strings for RPC and filesystem clients. `Credentials` is the persistence container used to carry tokens and secret material across process and job boundaries.

Persistence behavior is explicit in `Credentials`: token/secret state can be serialized through Hadoop `Writable` streams or token storage files in a chosen serialized format. UGI itself exposes process/static login state and subject-held credentials, not durable storage. Kerberos and token validity depend on external KDC/token secret-manager state.

Risks include leakage of credential maps or byte arrays, confusion between `addAll()` overwrite and `mergeAll()` non-overwrite semantics, stale group/ID caches, principal substitution against unexpected hostnames, and relogin code paths that must avoid retrying unrecoverable `KerberosAuthException`s.

## Credential Provider APIs

Lines 32934-33102 cover `org.apache.hadoop.security.alias`:

- `CredentialProvider` is an abstract, thread-safe credential/password store. It defines `flush()` for durable writes, alias lookup/list/create/delete, `needsPassword()`, warning/error text for missing provider passwords, and `CLEAR_TEXT_FALLBACK`.
- `CredentialProviderFactory` creates providers from URI names and resolves the configured provider list from `CREDENTIAL_PROVIDER_PATH` using service-loader style discovery.

The control flow is configuration-driven: callers ask the factory for providers, then call provider CRUD methods and `flush()` to persist changes. The main integration points are Hadoop `Configuration`, provider URI schemes, and implementations discovered through Java service loading. Risks are missing provider passwords, fallback to clear text when enabled, and implementations that violate the documented thread-safety expectation.

## Authorization And HTTP Filters

Lines 33107-33674 cover authorization and servlet filters:

- `AccessControlList` is a `Writable` ACL value with constructors from combined ACL string or separate users/groups. It supports wildcard ACLs, mutable add/remove methods, immutable user/group views, `isUserInList(UserGroupInformation)`, `isUserAllowed(UserGroupInformation)`, a parseable `getAclString()`, and `write/readFields`. `USE_REAL_ACLS` enables real-user ACL handling for proxied users.
- `AuthorizationException` extends `AccessControlException`, but intentionally suppresses stack trace exposure for security-sensitive authorization failures.
- `DefaultImpersonationProvider` implements `ImpersonationProvider`, is configurable, initializes from a configuration prefix, authorizes proxy users by effective user and remote `InetAddress`, provides config-key builders for proxy users/groups/IPs, and exposes proxy group/host maps.
- `ImpersonationProvider` extends `Configurable`, defines `init(prefix)`, keeps a string-address `authorize` convenience method, and prefers the `InetAddress` overload to avoid redundant DNS resolution.
- `RestCsrfPreventionFilter` is a servlet `Filter` that requires a configurable custom header for browser-originated REST calls. It exposes browser-agent detection, a testable `handleHttpInteraction(...)` path, servlet `doFilter`, and a static `getFilterParams(Configuration, prefix)` helper. Public constants define user-agent, browser-regex, custom-header, ignored-method, and default-header parameter names.
- `XFrameOptionsFilter` is a servlet `Filter` that adds clickjacking protection through an X-Frame-Options-style header. It has `init`, `doFilter`, `destroy`, `getFilterParams`, and constants for `X_FRAME_OPTIONS` and custom header parameter naming.

The authorization flow combines identity from UGI, ACL membership, proxy-user configuration, and remote client address. The HTTP filters are initialized from prefixed `Configuration` values converted to servlet init parameters, then enforce request headers during `doFilter`.

State persists only when ACLs are serialized as `Writable`s or when proxy/filter settings live in configuration. Runtime maps in impersonation providers and filter params are derived state. Test signals should include wildcard ACL parsing, real-user proxy ACL behavior, stack-trace suppression in `AuthorizationException`, browser/non-browser CSRF branches, ignored HTTP methods, custom header names, and X-Frame-Options header emission.

## Token And Delegation Token APIs

Lines 33681-34844 cover `org.apache.hadoop.security.token` and `org.apache.hadoop.security.token.delegation.web`:

- `SecretManager<T extends TokenIdentifier>` is the token-password authority. Subclasses implement `createPassword(T)`, `retrievePassword(T)`, and `createIdentifier()`. The base API adds `retriableRetrievePassword(...)` for standby/retriable server states, `checkAvailableForRead()`, secret-key generation, HMAC password creation from identifier bytes plus `SecretKey`, and secret-key reconstruction.
- `Token<T extends TokenIdentifier>` is `Writable` token state with constructors from identifier/secret manager, raw byte arrays, empty, and copy. It exposes ID/password setters, identifier/password/kind/service getters, private clone support, read/write serialization, URL-safe encode/decode, equality/hash/string/cache-key helpers, and lifecycle methods `isManaged()`, `renew(Configuration)`, and `cancel(Configuration)`.
- `Token.TrivialRenewer` is a `TokenRenewer` implementation for unmanaged/simple token kinds.
- `TokenIdentifier` is `Writable`, with `getKind()`, `getUser()`, serialized bytes, and optional tracking ID.
- `TokenInfo` is an annotation type for binding protocols to token selectors.
- `TokenRenewer` is the service-provider API for token kind handling, managed-state checks, renewal, and cancellation.
- `TokenSelector<T extends TokenIdentifier>` selects a token by service from a collection.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` with delegation-token operations. It has constructors taking authenticators/configurators, static default authenticator configuration, query-string behavior toggles, `openConnection` overloads, token get/renew/cancel operations with optional doAs user, and a nested `Token` that holds a Hadoop delegation token alongside the HTTP auth token.
- `DelegationTokenAuthenticator` wraps an `Authenticator` and adds delegation-token REST operations. It has constants for operation, delegation header/parameter names, token/renewer/service params, and JSON fields. `KerberosDelegationTokenAuthenticator` supports SPNEGO with fallback to pseudo auth; `PseudoDelegationTokenAuthenticator` models simple auth through current UGI/query user.

Token control flow starts with an identifier and secret manager producing a password, persists token bytes through `Writable` or URL encoding, and uses `TokenRenewer` implementations for managed renew/cancel. HTTP delegation-token flow authenticates with an `AuthenticatedURL.Token`, calls remote endpoints for get/renew/cancel, and stores the resulting Hadoop token in the nested URL token holder.

Persistent state includes token identifier/password/kind/service bytes, URL-encoded token strings, and credential stores that carry tokens. Secret-manager key material and token validity are server-side authority state. Risks include using `TrivialRenewer` for managed tokens, relying on client-side token fields without server validation, failing to handle standby/retriable exceptions, placing delegation tokens in query strings when headers are safer, and inconsistent service text construction across RPC and web clients.

## Service Lifecycle And Launcher APIs

Lines 34847-36232 cover `org.apache.hadoop.service` and `org.apache.hadoop.service.launcher`:

- `AbstractService` implements `Service` and provides the lifecycle template: `init(Configuration)` invokes `serviceInit`, `start()` invokes `serviceStart`, `stop()` invokes `serviceStop`, `close()` relays to `stop()`, and `noteFailure(Exception)` records failure cause/state. It also tracks service name, config, start time, lifecycle history, blockers, local listeners, and global listeners.
- `CompositeService` extends `AbstractService` to own child services. It adds protected `addService`, `addIfService`, `removeService`, cloned `getServices()`, and overrides service init/start/stop to cascade lifecycle operations. `STOP_ONLY_STARTED_SERVICES` documents shutdown policy.
- `LifecycleEvent` is serializable event state with public `time` and `state`.
- `LoggingStateChangeListener` logs service state changes.
- `Service` extends `Closeable` and defines the service state machine contract: `init`, `start`, `stop`, `close`, listener registration, name/config/state/start-time/failure/history/blocker accessors, `isInState`, and `waitForServiceToStop`. The Javadoc is strict that failed init/start should invoke stop and enter `STOPPED`; stop must be robust even for partially initialized internals.
- `ServiceOperations` supplies static `stop` and several `stopQuietly` overloads for safe service cleanup.
- `ServiceStateChangeListener` is the callback interface.
- `ServiceStateException` is a runtime exception with `ExitCodeProvider` support and conversion helpers.
- `ServiceStateModel` is the explicit state-transition engine with current-state access, `ensureCurrentState`, `enterState`, transition validation, and `isValidStateTransition`.
- `AbstractLaunchableService` extends `AbstractService` and implements `LaunchableService` with default `bindArgs` and `execute` behavior.
- `HadoopUncaughtExceptionHandler` is intended for process entry points; it exits for `Error`s and logs ordinary exceptions, with optional delegation for simple cases.
- `LaunchableService` extends `Service` and adds `bindArgs(Configuration, List)` before init and `execute()` after start. Its exception policy maps `ExitException`, `ExitCodeProvider`, and generic exceptions into process exit behavior.
- `LauncherExitCodes` defines common process exit constants, deliberately mapped near HTTP-like categories.
- `ServiceLaunchException` extends `ExitUtil.ExitException`, implements `ExitCodeProvider` and `LauncherExitCodes`, and supports formatted messages with explicit exit codes and causes.

The lifecycle flow is a template method pattern plus state model: configure, initialize, start, execute if launchable, then stop/close. Failure is recorded and converted into lifecycle or launcher exceptions with exit codes. Composite services apply this flow recursively to child services.

State is in-memory lifecycle metadata: current state, start time, failure cause/state, history, blockers, listeners, and child-service lists. `LifecycleEvent` is serializable but the service framework itself is not a persistence layer. Risks include invalid state transitions, non-idempotent stop logic, failing to stop after partial init/start failure, listener side effects during state changes, and child services that cannot tolerate stop unless fully started.

## Utility APIs

Lines 36241-37013 cover the beginning of `org.apache.hadoop.util`:

- `ApplicationClassLoader` extends `URLClassLoader` for application isolation. It supports URL-array and classpath-string constructors, child-first `getResource`/`loadClass` behavior except for system classes, static `isSystemClass(name, patterns)`, and `SYSTEM_CLASSES_DEFAULT` for JDK, Hadoop, resource, and selected third-party exclusions.
- `DurationInfo` extends `OperationDuration` and implements `AutoCloseable`; constructors format/log a duration message at info or debug, and `close()` logs the final state for try-with-resources usage.
- `IPList` defines a single membership check for IP address strings.
- `OperationDuration` tracks start and finish times, exposes `finished()`, printable duration, static `humanTime(long)`, raw millisecond value, and `java.time.Duration` conversion.
- `Progressable` is the callback for long operations to report progress to Hadoop frameworks.
- `PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum`, with `getValue`, `reset`, byte-array `update`, and int `update`. The first matches the standard CRC32 polynomial and avoids JNI overhead for small repeated checksum operations; the second uses CRC32-C/iSCSI polynomial.
- `ReflectionUtils` provides configuration injection, reflective construction with configuration, contention tracing toggle, synchronized thread-info printing, commons-logging and slf4j thread-stack logging with minimum interval, typed class lookup, `Writable` copy/clone using serialization, and inherited declared field/method enumeration.
- `Shell` begins here as an abstract base for platform command execution. The covered part includes constructors with optional minimum interval and stderr redirection, deprecated `isJava7OrAbove()` which always returns true, Java major-version checks, Windows command-line length validation, platform-specific group/user/netgroup/permission/owner/symlink/readlink/process/signal command builders, environment-variable regex generation, script-extension helpers, run-script command generation, Hadoop home lookup, and qualified Hadoop bin lookup/path methods. The XML chunk stops inside the Javadoc for `getQualifiedBinPath`.

Control flow is utility specific: class loading decides parent/system versus application lookup, duration classes record and later finish/log elapsed time, CRC implementations mutate internal checksum state across updates, reflection helpers create/configure objects and copy `Writable`s through serialization, and `Shell` builds platform-specific command arrays before execution in later methods outside this chunk.

State is local and mutable for timers, checksum accumulators, shell interval/output settings, and loaded classpath URLs. Risks include classloader isolation mistakes from incorrect system-class patterns, checksum offset/length bounds, thread-dump throttling correctness, reflection constructor/configuration failures, platform-specific command quoting and Windows length limits, and expensive qualified-bin existence checks that Javadoc says callers should cache.

## Dependencies And Integration Points

Major dependencies visible in this API slice include Hadoop `Configuration`, `Writable`, `Text`, `Path`, RPC/security annotations, servlet `Filter` APIs, Java JAAS/Kerberos classes, Java networking/socket APIs, Java crypto `SecretKey`, logging through slf4j and commons-logging, and Java classloading/reflection/serialization primitives.

The integration surface is broad:

- HDFS/YARN block placement and topology code consume `DNSToSwitchMapping` and rack paths.
- RPC, filesystem, and HTTP clients consume `SecurityUtil`, `UserGroupInformation`, `Credentials`, `Token`, and delegation-token URL helpers.
- Daemons and launchers use `Service`, `AbstractService`, `CompositeService`, `LaunchableService`, and launcher exit codes.
- Web UIs and REST endpoints use CSRF and X-Frame filters.
- Configuration and service-provider discovery connect credential providers, token renewers/selectors, security-info providers, socket factories, and classloader policies.

## Test Signals

Useful tests for this chunk should validate API contracts rather than implementation internals:

- DNS mapping returns same-sized result lists, caches and reloads correctly, dumps topology diagnostics, and respects single-switch policy.
- Script/table mappings re-read configuration and handle missing or failing mapping inputs without corrupting cached state.
- Socket factories create equivalent sockets and proxy-backed sockets, and `ConnectTimeoutException` is surfaced from timeout paths.
- `Credentials` read/write round trips tokens and secrets across stream/file formats; `addAll` overwrites while `mergeAll` preserves.
- UGI covers simple, keytab, ticket-cache, subject, remote, proxy, and testing users; relogin and `doAs` behavior should propagate exceptions and authentication methods correctly.
- ACL and impersonation tests cover wildcard, user/group, real-user proxy, host/IP matching, and stack-trace suppression for authorization failures.
- Servlet filter tests cover browser detection, custom CSRF headers, ignored methods, missing headers, and X-Frame header configuration.
- Token tests cover `Writable` and URL encode/decode round trips, service/kind matching, private clones, renew/cancel delegation, and retriable/standby secret-manager exceptions.
- Service tests cover all valid and invalid state transitions, failure recording, listener notification, blocker maps, wait-for-stop, composite child ordering, and launch exception exit-code mapping.
- Utility tests cover application classloader positive/negative system patterns, duration finalization, CRC32/CRC32C known vectors, `ReflectionUtils.copy` for `Writable`s, thread-info throttling, and `Shell` command construction across Unix/Windows branches.

### subset-b-007217: lines 37014-39037

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 37014-39037

## Scope

This chunk is the final portion of the Hadoop Common 3.3.4 JDiff public API XML. It closes the `org.apache.hadoop.util.Shell` class, documents several core utility classes in `org.apache.hadoop.util`, then covers the public Bloom filter API under `org.apache.hadoop.util.bloom` and functional helper APIs under `org.apache.hadoop.util.functional`. The source is an API snapshot rather than executable source, so the research focuses on exposed contracts, state surfaces, expected control flow, integration points, and compatibility risks.

## Purpose

The chunk groups utility APIs used across Hadoop Common:

- `Shell` provides a base abstraction and static helpers for launching native commands, discovering Hadoop home and Windows `winutils`, enforcing timeouts, tracking live shell processes, and exposing OS/platform constants.
- `ShutdownHookManager` gives Hadoop a deterministic, priority-ordered shutdown hook registry with per-hook timeouts instead of relying directly on JVM shutdown hook ordering.
- `StringInterner`, `SysInfo`, `Tool`, `ToolRunner`, and `VersionInfo` support common runtime concerns: memory-efficient strings, OS resource metrics, command-line application bootstrapping, generic Hadoop option parsing, and build metadata reporting.
- `org.apache.hadoop.util.bloom` exposes Bloom filter variants for compact set-membership structures, deletion/counting, dynamic growth, retouched false-positive removal, and hash vector generation.
- `FutureIO` and `RemoteIterators` make async IO and `RemoteIterator` composition easier while preserving Hadoop IO exception semantics and optional IO statistics.

## Important APIs, Types, And Functions

### `org.apache.hadoop.util.Shell`

This segment contains the operational tail of `Shell`:

- Windows executable discovery: `hasWinutilsPath()`, `getWinUtilsPath()`, and `getWinUtilsFile()` publish a safer replacement for directly reading the deprecated nullable `WINUTILS` field. `getWinUtilsPath()` converts lookup failure to `RuntimeException`; `getWinUtilsFile()` raises `FileNotFoundException`.
- Shell capability probing: `checkIsBashSupported()` returns whether bash can be used and may raise `InterruptedIOException`.
- Instance setup and execution: protected `setEnvironment(Map)`, `setWorkingDirectory(File)`, `run()`, abstract `getExecString()`, and abstract `parseExecResult(BufferedReader)` define the subclass contract. A subclass provides command arguments and parses stdout; the base class handles launch cadence, timeout behavior, and process state.
- Runtime inspection: `getEnvironment(String)`, `getProcess()`, `getExitCode()`, `getWaitingThread()`, and `isTimedOut()` expose environment lookup and current process lifecycle state.
- Convenience execution: overloaded static `execCommand(...)` methods run a command with optional environment and timeout and return stdout as a `String`.
- Process registry: `destroyAllShellProcesses()` destroys all currently running `Shell` processes in a thread-safe way; `getAllShells()` returns the registered set.
- Native memory helper: `getMemlockLimit(Long ulimit)` computes the datanode memory lock limit capped by the provided `ulimit`.
- Published constants include Hadoop home property/env names, OS booleans and `osType`, Unix command names, Windows process-launch lock, Windows command-line length limit, `ENV_NAME_REGEX`, `TOKEN_SEPARATOR_REGEX`, timeout and environment inheritance fields, deprecated misspelled `WINDOWS_MAX_SHELL_LENGHT`, deprecated nullable `WINUTILS`, and `isSetsidAvailable`.

### `org.apache.hadoop.util.ShutdownHookManager`

`ShutdownHookManager` is a final singleton reached through `get()`. Its registry API is:

- `addShutdownHook(Runnable, int)` and `addShutdownHook(Runnable, int, long, TimeUnit)` register hooks with priority. Higher priority runs earlier; same-priority hooks run in nondeterministic order.
- `removeShutdownHook(Runnable)` and `hasShutdownHook(Runnable)` query and mutate the registry.
- `isShutdownInProgress()` exposes shutdown state.
- `clearShutdownHooks()` removes all registered hooks, mostly useful for tests.
- `TIMEOUT_MINIMUM` and `TIME_UNIT_DEFAULT` define timeout policy. The class documentation states default hook timeout comes from `CommonConfigurationKeysPublic.SERVICE_SHUTDOWN_TIMEOUT` with `SERVICE_SHUTDOWN_TIMEOUT_DEFAULT`.

### `org.apache.hadoop.util.StringInterner`

`StringInterner` exposes `strongIntern(String)`, `weakIntern(String)`, and `internStringsInArray(String[])`. The array method interns in place and returns the same array. Documentation says weak interning uses the standard `String.intern()` behavior from JDK 7 onward, while strong interning retains a strong reference and prevents collection.

### `org.apache.hadoop.util.SysInfo`

`SysInfo` is an abstract plugin interface for OS resource metrics. `newInstance()` chooses the default OS implementation and may throw `UnsupportedOperationException` when the OS cannot be determined. Implementations provide:

- memory totals and availability: virtual and physical memory sizes;
- CPU topology and usage: logical processors, physical cores, CPU frequency, cumulative CPU time, CPU usage percentage, and vcores used;
- aggregate IO counters: network bytes read/written and storage bytes read/written.

Methods return primitive `long`, `int`, or `float`; CPU usage and vcores may return `-1` when unavailable.

### `org.apache.hadoop.util.Tool` And `ToolRunner`

`Tool` extends `Configurable` and standardizes Hadoop command-line applications through `run(String[] args): int`. The contract expects generic Hadoop options to be delegated to `ToolRunner`, while the tool handles only application-specific arguments.

`ToolRunner` provides:

- `run(Configuration, Tool, String[])`: parses generic options through `GenericOptionsParser`, updates the tool's configuration, and invokes `Tool.run`.
- `run(Tool, String[])`: delegates using the tool's existing configuration.
- `printGenericCommandUsage(PrintStream)`: emits generic option usage.
- `confirmPrompt(String)`: prompts and returns true for case-insensitive `y` or `yes`.

### `org.apache.hadoop.util.VersionInfo`

`VersionInfo` exposes protected instance accessors for component build metadata and public static getters:

- `getVersion()`, `getRevision()`, `getBranch()`, `getDate()`, `getUser()`, `getUrl()`, `getSrcChecksum()`, `getBuildVersion()`, and `getProtocVersion()`;
- `main(String[])` for command-line metadata display.

The class is the public build-info surface for Hadoop components, including Git revision, branch, compile date/user, source checksum, and protobuf compiler version.

### `org.apache.hadoop.util.bloom`

The Bloom package in this chunk contains:

- `BloomFilter extends Filter`: standard Bloom filter with constructors for deserialization and `(vectorSize, nbHash, hashType)`. It supports `add(Key)`, `membershipTest(Key)`, boolean operations `and`, `or`, `xor`, `not`, `getVectorSize()`, `toString()`, and `Writable`-style `write(DataOutput)` / `readFields(DataInput)`.
- `CountingBloomFilter final extends Filter`: counting-vector implementation that supports `add(Key)`, `delete(Key)`, `membershipTest(Key)`, `approximateCount(Key)`, boolean operations, string rendering, and serialization. Counts are limited by small buckets; the docs warn that inserting the same key more than 15 times overflows associated positions and increases error rates.
- `DynamicBloomFilter extends Filter`: matrix/row-based filter that grows by adding rows when the active row reaches threshold `nr`. It supports add, membership test, boolean operations, string rendering, and serialization.
- `HashFunction final`: configured by `maxValue`, `nbHash`, and Hadoop hash type. `hash(Key)` returns multiple integer positions; `clear()` is a no-op.
- `RemoveScheme`: constants `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO` define retouched Bloom filter bit-clearing strategies.
- `RetouchedBloomFilter final extends BloomFilter implements RemoveScheme`: adds false-positive tracking through `addFalsePositive(Key)`, overloads for `Collection`, `List`, and `Key[]`, and `selectiveClearing(Key, short)` to remove selected false positives at the cost of possible false negatives. It also participates in serialization through `write` and `readFields`.

### `org.apache.hadoop.util.functional.FutureIO`

`FutureIO` is a final static helper class for waiting on asynchronous IO while preserving checked `IOException` behavior:

- `awaitFuture(Future<T>)` and `awaitFuture(Future<T>, long, TimeUnit)` wait for completion, extract exceptions from the future, and rethrow nested `IOException`, `RuntimeException`, `InterruptedIOException`, or `TimeoutException` as appropriate.
- `raiseInnerCause(ExecutionException)` and `raiseInnerCause(CompletionException)` always throw the inner cause as an `IOException`, runtime exception, or wrapped `IOException`.
- `unwrapInnerException(Throwable)` recursively unwraps `IOException`, `UncheckedIOException`, `ExecutionException`, and `CompletionException`; it throws runtime exceptions and errors directly, and wraps other causes in `IOException`.

### `org.apache.hadoop.util.functional.RemoteIterators`

`RemoteIterators` is a final static helper class for building and composing Hadoop `RemoteIterator` instances:

- factories: `remoteIteratorFromSingleton(T)`, `remoteIteratorFromIterator(Iterator<T>)`, `remoteIteratorFromIterable(Iterable<T>)`, and `remoteIteratorFromArray(T[])`;
- transforms: `mappingRemoteIterator(RemoteIterator<S>, FunctionRaisingIOE<S,T>)`, `typeCastingRemoteIterator(RemoteIterator<S>)`, and `filteringRemoteIterator(RemoteIterator<S>, FunctionRaisingIOE<S,Boolean>)`;
- lifecycle composition: `closingRemoteIterator(RemoteIterator<S>, Closeable)` forwards close behavior to wrapped iterators and an additional closeable;
- materialization and consumption: `toList(RemoteIterator<T>)`, `toArray(RemoteIterator<T>, T[])`, `foreach(RemoteIterator<T>, ConsumerRaisingIOE<T>)`, and `cleanupRemoteIterator(RemoteIterator<T>)`.

The class is intended to preserve IOStatisticsSource passthrough and log IO statistics at DEBUG during `foreach` or cleanup when available.

## Control Flow

`Shell` subclasses follow a template-method pattern: configure environment and working directory, call protected `run()`, let the subclass provide the command vector through `getExecString()`, then parse process output through `parseExecResult(BufferedReader)`. Static `execCommand` wraps this pattern for simple one-shot commands. Timeout flow is visible through `timeOutInterval`, `isTimedOut()`, exit-code inspection, and `getWaitingThread()`. Global shutdown or cleanup can call `destroyAllShellProcesses()` to terminate all registered shells.

`ShutdownHookManager` centralizes JVM shutdown handling. Instead of registering many independent JVM hooks, Hadoop registers one manager hook, sorts registered runnables by priority, and runs higher-priority hooks first. A hook registered with an explicit timeout uses its own timeout; otherwise timeout configuration is read from `core-site.xml`. Same-priority ordering remains nondeterministic.

`ToolRunner` control flow is generic-option parse, configuration mutation, and `Tool.run` invocation. The two `run` overloads differ only in where the initial `Configuration` comes from. `confirmPrompt` is synchronous stdin/stdout interaction with a narrow yes condition.

Bloom filter control flow is hash-driven: `HashFunction.hash(Key)` maps a key to positions; `add` mutates vectors/counters/rows; `membershipTest` checks positions; boolean operations combine compatible filters. `CountingBloomFilter.delete` decrements counters only for present keys by contract. `DynamicBloomFilter.add` inserts into an active row or creates a new row once the row threshold is met. `RetouchedBloomFilter` first records known false positives, then `selectiveClearing` chooses bits to reset based on a `RemoveScheme`.

`FutureIO` control flow is exception normalization around `Future.get()`: interruption becomes `InterruptedIOException`, timeout remains `TimeoutException`, nested checked IO failures are surfaced as `IOException`, unchecked failures remain unchecked, and arbitrary checked causes are wrapped. `RemoteIterators` builds lazy wrappers: mapping/filtering happen during iteration, filtering may advance in `hasNext()`, materialization consumes the source, and cleanup optionally closes and logs statistics.

## State And Persistence Behavior

`Shell` has both per-instance mutable state and process-wide static state. Per-instance state includes environment, working directory, current `Process`, exit code, waiting thread, timeout flag/interval, and whether to inherit parent environment. Static state includes OS detection constants, `WINUTILS`, `isSetsidAvailable`, command constants, and a registry of live shells. `WINUTILS` is deprecated because null handling leaked into callers; the exception-raising getters are the stable contract.

`ShutdownHookManager` persists hook registrations in memory only for the JVM lifetime. It tracks shutdown-in-progress state and hook metadata including priority and timeout. `clearShutdownHooks()` can erase this state, which is valuable in tests but risky in shared runtime code.

`StringInterner` stores interned strings either strongly or weakly depending on method, affecting heap retention. `internStringsInArray` mutates the caller's array in place.

`SysInfo` exposes live OS counters. Values are observational and may be unavailable, platform-specific, cumulative, or sampled.

`VersionInfo` reads build metadata generated at build time and exposes it as immutable strings at runtime.

Bloom filters are persistent Hadoop data structures through `write(DataOutput)` and `readFields(DataInput)`. Default constructors exist specifically for deserialization. Persistent state includes vector size, hash count/type, bit vectors, counter vectors, dynamic rows and thresholds, and retouched false-positive metadata. Compatibility depends on serialized field order in the implementation, not visible in this JDiff snapshot.

`FutureIO` is stateless. `RemoteIterators` wrappers hold references to source iterators, mapping/filter functions, optional cached next elements, closeables, and possibly IO statistics sources; they are lazy and stateful across iteration.

## Dependencies And Integration Points

Key dependencies surfaced in this chunk:

- Java platform APIs: `Process`, `Thread`, `File`, `BufferedReader`, `DataInput`, `DataOutput`, `IOException`, `FileNotFoundException`, `InterruptedIOException`, `UncheckedIOException`, `ExecutionException`, `CompletionException`, `Future`, `TimeoutException`, `TimeUnit`, `Iterator`, `Iterable`, `Collection`, `List`, `Closeable`, and `PrintStream`.
- Hadoop configuration and CLI: `org.apache.hadoop.conf.Configurable`, `Configuration`, `GenericOptionsParser`, `CommonConfigurationKeysPublic`, and the generic options command manual.
- Hadoop filesystem iteration: `org.apache.hadoop.fs.RemoteIterator`, IO statistics source behavior, and functional interfaces `FunctionRaisingIOE` and `ConsumerRaisingIOE`.
- Hadoop hashing and serialization: `org.apache.hadoop.util.hash.Hash`, Bloom `Key`, base `Filter`, and Writable-style binary IO through `DataInput`/`DataOutput`.
- Logging: `Shell.LOG` and `RemoteIterators` DEBUG logging for IO statistics.
- Native/platform integration: OS detection, Unix commands such as permission/owner/group/link/readlink, Windows `winutils`, bash probing, `setsid`, Windows process launch locking, and command-line length limits.

These APIs are broad integration points. `Tool`/`ToolRunner` are a stable entry path for Hadoop command-line applications. `RemoteIterators` is especially relevant to object-store filesystems and listings, where lazy remote enumeration, closeable resources, and IO statistics are operationally important.

## Risks And Edge Cases

- `Shell.WINUTILS` remains public but deprecated and nullable. Callers that still read it directly risk null failures and weaker diagnostics.
- Native command execution is platform-sensitive. Windows command length, bash availability, `setsid`, environment variable validation, working directory existence, and Hadoop home discovery are all likely failure points.
- `destroyAllShellProcesses()` is process-wide. It is useful for shutdown/test cleanup but can terminate unrelated active shell operations in the same JVM.
- `ShutdownHookManager` same-priority hook ordering is nondeterministic. Hooks with dependencies need explicit priority separation.
- Shutdown hook timeouts can terminate unfinished cleanup. Very short explicit timeouts or misconfigured service shutdown timeout may leave resources unflushed.
- `StringInterner.strongIntern` can create unbounded retention if applied to high-cardinality strings.
- `SysInfo` is abstract and platform-backed; metric semantics can differ by OS and unsupported metrics may return `-1` or throw during instance selection.
- `ToolRunner.confirmPrompt` is interactive and unsuitable for non-interactive daemons unless guarded.
- Bloom filters are probabilistic. Standard Bloom filters allow false positives; counting filters can overflow after repeated adds and can underflow after deletes, introducing inaccurate counts or false negatives; retouched filters intentionally trade selected false positives for possible false negatives.
- Boolean operations on Bloom filters are only meaningful for compatible vector sizes, hash counts, and hash types. The JDiff contract does not show validation behavior, so implementation tests should cover incompatible filters.
- `FutureIO.unwrapInnerException` intentionally rethrows runtime exceptions and errors. Callers expecting all failures as `IOException` must account for unchecked propagation.
- `RemoteIterators.filteringRemoteIterator` may perform filtering work in `hasNext()`, which can surface IO failures or advance remote state earlier than callers expect. Materializing with `toList`/`toArray` can consume large remote listings into memory.
- `RemoteIterators.cleanupRemoteIterator` depends on closeable support and DEBUG logging; missing cleanup can leak network connections, file handles, or listing resources.

## Test Signals

Useful tests and validation signals for code touching APIs in this chunk:

- `Shell`: tests for `winutils` discovery on Windows and non-Windows, exception behavior of `getWinUtilsPath()`/`getWinUtilsFile()`, command timeout and `isTimedOut()`, environment propagation, working directory propagation, exit-code capture, process registry cleanup, and concurrent `destroyAllShellProcesses()`.
- `ShutdownHookManager`: ordering by priority, nondeterministic same-priority tolerance, explicit and default timeout handling, removal/query semantics, shutdown-in-progress state, and `clearShutdownHooks()` isolation across tests.
- `StringInterner`: identity reuse for equal strings, in-place array mutation, null behavior if supported by implementation, and memory-retention expectations for strong versus weak paths.
- `SysInfo`: platform-specific implementations should be tested for units, unavailable metric sentinels, monotonic cumulative CPU time, and supported OS selection in `newInstance()`.
- `ToolRunner`: generic option parsing should mutate the tool configuration while preserving application args; exit code from `Tool.run` should pass through; usage printing and prompt parsing should be covered.
- `VersionInfo`: generated build metadata resource loading, static getter consistency, and CLI output from `main`.
- Bloom filters: add/membership semantics, expected false-positive/no-false-negative properties for standard Bloom filters, counting add/delete/approximate count including overflow and underflow cases, dynamic row expansion at threshold `nr`, retouched selective clearing for each `RemoveScheme`, boolean operations, `toString`, and round-trip `write`/`readFields` compatibility.
- `FutureIO`: completed future result propagation, interrupted waits, timeout waits, unwrapping of `IOException`, `UncheckedIOException`, `ExecutionException`, `CompletionException`, runtime exceptions, errors, and arbitrary checked exceptions.
- `RemoteIterators`: singleton/array/iterator/iterable factories, lazy mapping and filtering with IO-raising functions, type casting behavior, close propagation through nested wrappers, `toList`/`toArray` materialization, `foreach` count return, consumer failure propagation, cleanup idempotence, and IOStatistics logging when DEBUG is enabled.
