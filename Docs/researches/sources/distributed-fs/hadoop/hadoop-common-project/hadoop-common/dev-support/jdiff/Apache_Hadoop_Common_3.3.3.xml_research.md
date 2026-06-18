# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007204`: lines 1-6066, `Docs/researches/chunks/subset-b-007204_research.md`
- `subset-b-007205`: lines 6067-12059, `Docs/researches/chunks/subset-b-007205_research.md`
- `subset-b-007206`: lines 12060-18114, `Docs/researches/chunks/subset-b-007206_research.md`
- `subset-b-007207`: lines 18115-24646, `Docs/researches/chunks/subset-b-007207_research.md`
- `subset-b-007208`: lines 24647-30892, `Docs/researches/chunks/subset-b-007208_research.md`
- `subset-b-007209`: lines 30893-37013, `Docs/researches/chunks/subset-b-007209_research.md`
- `subset-b-007210`: lines 37014-39037, `Docs/researches/chunks/subset-b-007210_research.md`

## Chunk Research

### subset-b-007204: lines 1-6066

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml lines 1-6066

## Scope

This chunk is the opening of the JDiff API snapshot for Apache Hadoop Common 3.3.3. It covers the XML prologue and command-line generation metadata, then the public API entries for `org.apache.hadoop.HadoopIllegalArgumentException`, `org.apache.hadoop.conf.Configurable`, `Configuration`, `Configured`, `org.apache.hadoop.crypto.key.KeyProvider`, `KeyProviderFactory`, and the start of `org.apache.hadoop.fs` through `CommonConfigurationKeysPublic.HADOOP_SECURITY_KEY_DEFAULT_CIPHER_DEFAULT`.

The source is generated compatibility metadata, not implementation code. The research surface is therefore the public/protected API contract: packages, type names, inheritance, implemented interfaces, constructors, method signatures, visibility, static/final/abstract/synchronized attributes, checked exceptions, fields, deprecation markers, and embedded Javadocs.

## Purpose

The first package establishes Hadoop-wide public contracts: `HadoopIllegalArgumentException` distinguishes Hadoop implementation argument failures from plain JDK `IllegalArgumentException`, while `Configurable` and `Configured` define the standard object-to-`Configuration` binding used throughout Hadoop.

`Configuration` is the dominant API in this chunk. It models layered XML-backed configuration resources with default resources, site resources, final parameters, deprecation aliases, variable expansion, tags, typed getters/setters, credential-provider password lookup, resource serialization, JSON/XML dumping, class loading, and `Writable` serialization. The class-level Javadocs identify `core-default.xml` and `core-site.xml` as the default resource pair and document resource precedence and final-parameter behavior.

`KeyProvider` and `KeyProviderFactory` define Hadoop's secret-key storage abstraction. They separate encryption key consumers from storage backends, support key versions, metadata, generated key material, rolling keys, cache invalidation, flush-to-persistent-store semantics, password requirements, and service-loader based provider lookup from configured URI paths.

The filesystem portion starts the core `org.apache.hadoop.fs` public surface. It includes stream abort support, the `AbstractFileSystem` implementor-facing contract behind `FileContext`, Avro stream adaptation, batched listing, block-location metadata, storage-policy SPI, byte-buffer and stream capability interfaces, checksum exceptions, the client-side `ChecksumFileSystem` wrapper, and the beginning of public configuration constants for filesystem, IO, IPC, security, crypto, and key-provider behavior.

## Important APIs, Types, and Functions

### Configuration APIs

- `Configurable` declares `setConf(Configuration)` and `getConf()`. `Configured` implements that storage pattern with default and configuration-taking constructors.
- `Configuration` implements `Iterable` and `org.apache.hadoop.io.Writable`. Constructors support default loading, explicit `loadDefaults`, and cloning another configuration.
- Global deprecation APIs include `addDeprecations(DeprecationDelta[])`, several `addDeprecation` overloads, `isDeprecated`, `setDeprecatedProperties`, `dumpDeprecatedKeys`, and `hasWarnedDeprecation`.
- Resource APIs include synchronized static `addDefaultResource`, many `addResource` overloads for classpath names, URLs, `Path`, `InputStream`, named streams, and another `Configuration`, plus `reloadConfiguration` and static `reloadExistingConfigurations`.
- String accessors include `get`, `getTrimmed`, `getRaw`, `set`, `unset`, `setIfUnset`, `onlyKeyExists`, and null-value/restricted-system-property controls.
- Typed accessors cover `int`, `int[]`, `long`, byte-sized longs with suffixes, `float`, `double`, `boolean`, enums, time durations and duration arrays, storage sizes via `StorageUnit`, regex `Pattern`, integer ranges, string collections, string arrays, and trimmed string variants.
- Credential and address helpers include `getPassword`, `getPasswordFromCredentialProviders`, protected `getPasswordFromConfig`, `getSocketAddr`, `setSocketAddr`, and `updateConnectAddr`.
- Dynamic class APIs include `getClassByName`, `getClassByNameOrNull`, `getClasses`, `getClass`, `getInstances`, `setClass`, `getClassLoader`, and `setClassLoader`.
- Local resource helpers include `getLocalPath`, `getFile`, `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader`.
- Introspection and persistence APIs include `getFinalParameters`, protected synchronized `getProps`, `size`, `clear`, `iterator`, `getPropsWithPrefix`, `addTags`, `writeXml` overloads, static `dumpConfiguration` overloads, `readFields`, `write`, `getValByRegex`, `getAllPropertiesByTag`, `getAllPropertiesByTags`, `isPropertyTag`, `setQuietMode`, and debug `main`.

### Crypto Key APIs

- `KeyProvider` is abstract, implements `Closeable`, stores a `Configuration`, and is documented as requiring thread-safe implementations.
- Abstract key-store operations include `getKeyVersion`, `getKeys`, `getKeyVersions`, `getMetadata`, `createKey(String, byte[], Options)`, `deleteKey`, `rollNewVersion(String, byte[])`, and `flush`.
- Concrete helper operations include bulk `getKeysMetadata`, current-key lookup, generated `createKey`, generated `rollNewVersion`, `generateKey`, `invalidateCache`, `close`, `getBaseName`, `buildVersionName`, and `findProvider`.
- Provider password APIs include `needsPassword`, `noPasswordWarning`, and `noPasswordError`.
- Public constants include default cipher and bit-length names/defaults plus JCEKS serial-filter constants.
- `KeyProviderFactory` is an abstract service-provider factory with `createProvider(URI, Configuration)`, static `getProviders(Configuration)`, static `get(URI, Configuration)`, and `KEY_PROVIDER_PATH`.

### Filesystem APIs

- `Abortable.abort()` returns `AbortableResult` and promises that aborted stream output must not become visible.
- `AbstractFileSystem` implements `PathCapabilities` and is the implementor-facing VFS-like contract used by `FileContext`. It owns a protected `FileSystem.Statistics statistics` field and static statistics table accessors.
- `AbstractFileSystem` factory and identity APIs include `createFileSystem`, `get(URI, Configuration)`, protected static `getStatistics`, `clearStatistics`, `printStatistics`, `getAllStatistics`, `checkScheme`, `getUriDefaultPort`, `getUri`, `checkPath`, `getUriPath`, `makeQualified`, `getInitialWorkingDirectory`, `getHomeDirectory`, `hashCode`, and `equals`.
- Core namespace/data APIs include `getServerDefaults`, `resolvePath`, final high-level `create`, abstract `createInternal`, `mkdir`, `delete`, `open`, `truncate`, `setReplication`, final `rename`, `renameInternal`, symlink APIs, permission/owner/time setters, checksums, status and block-location queries, filesystem status, listing iterators, corrupt-block listing, checksum verification, and canonical service names.
- Optional advanced APIs include ACL methods, xattr methods, snapshot operations, storage policy methods, `openFileWithOptions`, `hasPathCapability`, `createMultipartUploader`, and protected final `methodNotSupported`.
- `AvroFSInput` adapts `FSDataInputStream` to Avro `SeekableInput` with length, read, seek, tell, and close operations.
- `BatchListingOperations` defines `batchedListStatusIterator` and `batchedListLocatedStatusIterator` returning `RemoteIterator<PartialListing>`-style results, with a path capability used to advertise support.
- `BlockLocation` is a serializable block metadata carrier with constructors for hosts, names, topology paths, storage IDs, storage types, offset, length, and corrupt state. It exposes getters/setters plus `isStriped` for erasure-coded block groups.
- `BlockStoragePolicySpi` exposes policy name, preferred storage types, creation fallbacks, replication fallbacks, and copy-on-create/inherit-only behavior.
- `ByteBufferPositionedReadable`, `ByteBufferReadable`, `CanSetDropBehind`, `CanSetReadahead`, and `CanUnbuffer` define optional stream capabilities around positioned byte-buffer reads, sequential byte-buffer reads, cache hints, readahead hints, and buffer release.
- `ChecksumException` adds a failing position to an `IOException`-style checksum failure.
- `ChecksumFileSystem` wraps a raw `FileSystem` and creates/verifies sidecar checksum files client-side. Its API exposes checksum-file naming and length calculation, bytes-per-sum, checksum verification/write toggles, raw filesystem access, open/append/truncate/concat/create variants, metadata delegation, rename/delete/list/mkdir/copy/local-output helpers, checksum failure reporting, builder hooks, and path capability filtering.
- `CommonConfigurationKeysPublic` begins a long constant table. In this line range it includes filesystem defaults and topology keys, trash/protected-directory/local-block/automatic-close/filesystem-creation keys, mapfile/sequencefile/TFile IO keys, caller context keys, IPC client/server timeout and socket keys, RPC socket/socks/hash keys, group mapping/cache keys, authentication/authorization/auth-to-local/DNS/token/Kerberos/SASL/RPC protection keys, crypto codec/cipher/JCE/provider/buffer keys, impersonation provider keys, and key-provider default cipher/bit-length/path keys. Some older MapReduce sort and shell-timeout constants are marked deprecated in favor of newer names.

## Control Flow

The XML has no executable flow, but the APIs imply the following behavioral paths:

- Configuration construction optionally loads default resources lazily. The first read path loads resources, applies resource order, honors final parameters, resolves deprecated keys to replacement keys, expands variables from other properties, environment variables, or system properties, then returns typed or raw values.
- Configuration write paths call `set`/typed setters, propagate deprecated-key aliases where applicable, track source information, and may overlay values loaded from resources. `unset`, `setIfUnset`, and `reloadConfiguration` mutate the in-memory property set and lazy-load state.
- Configuration resource flow distinguishes classpath resources, local `Path`/URL resources, input streams, and another `Configuration`. Later resources override earlier ones unless blocked by final parameters. InputStream resources are cached and then closed on load.
- Password lookup first tries credential providers, then conditionally falls back to clear-text configuration through the protected fallback hook.
- Address flow parses host/port properties into `InetSocketAddress` and can rewrite wildcard listener addresses into client-connect addresses using configured bind-host and service-address properties.
- Key-provider flow resolves configured provider URI paths through `KeyProviderFactory`, uses service-loader factories to create providers, then performs key lookup, creation, roll, deletion, cache invalidation, and `flush()` to make mutations durable in provider storage.
- Abstract filesystem flow starts with URI scheme/authority validation and configuration-driven class lookup using `fs.AbstractFileSystem.<scheme>.impl`. `FileContext` callers pass qualified paths through `checkPath`/`getUriPath`; high-level operations then dispatch to abstract filesystem implementations with absolute permissions and explicit options.
- `AbstractFileSystem.create` and `rename` are final wrappers that normalize option handling before invoking `createInternal` or `renameInternal`. The overwrite-aware rename overload can be built from a no-overwrite primitive.
- Optional filesystem features are exposed through capability checks or default unsupported behavior: symlinks, ACLs, xattrs, snapshots, storage policies, multipart uploads, byte-buffer reads, cache hints, and batched listing.
- `ChecksumFileSystem` flow routes user data operations to the raw filesystem while maintaining checksum sidecar files. Reads verify checksums when enabled; writes can generate checksum files; rename/delete/list/copy operations must account for both raw data paths and checksum paths.

## State and Persistence Behavior

This JDiff file persists the Hadoop 3.3.3 public API baseline for compatibility tooling. It does not store live Hadoop runtime state.

`Configuration` has substantial process-local mutable state: loaded resources, overlay properties, final-parameter sets, property source metadata, tags, class loader, quiet mode, system-property restrictions, and deprecation warning state. It can serialize non-default properties to XML or JSON-like dumps and implements `Writable` through `readFields`/`write`. Resource loading is lazy and reloadable, so tests must account for first-read side effects.

Global configuration state includes default resources and deprecation mappings. Several mutators are synchronized or documented as lockless/atomic-copy updates, so compatibility depends on preserving both API signatures and concurrency assumptions.

`KeyProvider` state lives in provider implementations. The abstract contract distinguishes transient providers from long-term stores and requires `flush()` to write key mutations to persistent storage. Version names, metadata, key material, caches, and password availability are all provider-managed. Generated-key helpers add cryptographic randomness and algorithm availability as implicit state dependencies.

`AbstractFileSystem` and `ChecksumFileSystem` operate on persistent filesystem namespace state: files, directories, symlinks, replication, permissions, owner/group, timestamps, checksums, ACLs, xattrs, snapshots, storage policies, and multipart upload state. `AbstractFileSystem` also maintains per-scheme/authority statistics in process-local tables. `ChecksumFileSystem` persists sidecar checksum files and therefore must keep namespace operations consistent between data files and checksum files.

`BlockLocation` and storage-policy objects are metadata snapshots or policy descriptors. `BlockLocation` is mutable and serializable; fields such as hosts, cached hosts, transfer names, topology paths, storage IDs/types, offset, length, corrupt, and striped state describe current placement rather than independent durable state.

`CommonConfigurationKeysPublic` is a stable constant surface tying Java code to keys in `core-default.xml` and related configuration files. Changing names, defaults, or deprecation state would affect configuration compatibility across Hadoop components and downstream applications.

## Dependencies and Integration Points

The chunk integrates with Java core APIs including `Iterable`, `Closeable`, `IOException`, `FileNotFoundException`, `URISyntaxException`, `NoSuchAlgorithmException`, `InputStream`, `OutputStream`, `Reader`, `Writer`, `DataInput`, `DataOutput`, `File`, `URL`, `URI`, `InetSocketAddress`, `ClassLoader`, `Pattern`, `Properties`, collections, `EnumSet`, `ByteBuffer`, and `CompletableFuture`.

Hadoop dependencies include `org.apache.hadoop.io.Writable`, `Path`, `FileSystem`, `FileContext`, `FSDataInputStream`, `FSDataOutputStream`, `FsServerDefaults`, `FsStatus`, `FileStatus`, `BlockLocation`, `BlockStoragePolicySpi`, `RemoteIterator`, `MultipartUploaderBuilder`, `FutureDataInputStreamBuilder`, `FSDataOutputStreamBuilder`, `OpenFileParameters`, `Options.CreateOpts`, `Options.ChecksumOpt`, `Options.Rename`, `CreateFlag`, `PathCapabilities`, `StreamCapabilities`, `FsPermission`, ACL and xattr types, `AccessControlException`, `Progressable`, `StorageType`, `StorageUnit`, and credential-provider/key-provider infrastructure.

External integration points include Avro `SeekableInput`, service-loader discovery for `KeyProviderFactory`, JCE cryptographic algorithms for key generation, XML configuration files such as `core-default.xml` and `core-site.xml`, environment variables and system properties for variable expansion, and platform/network configuration keys for IPC, RPC, Kerberos, SASL, DNS, group mapping, and sockets.

## Risks and Edge Cases

- JDiff metadata records API shape and Javadocs, not implementation details. Exact parsing, locking, resource cleanup, exception text, checksum algorithms, and filesystem semantics need implementation-source validation.
- `Configuration.get` has lazy-load side effects. Tests that inspect property counts, sources, or deprecation warnings can become order-sensitive if they accidentally trigger loading early.
- Final parameters prevent later resource overrides. Incorrect handling can allow users to bypass administrator-enforced settings or can reject legitimate overlays.
- Deprecated-key aliasing is global and compatibility-sensitive. Multi-key aliases set all replacement keys, warning state is global, and late deprecation registration after resource loading is documented as unsupported in some overloads.
- Variable expansion consults environment variables and system properties. This can introduce nondeterminism and security risks when configuration values include untrusted interpolation.
- InputStream-backed resources are cached and later closed. Large streams can increase memory usage, and callers must not assume the stream remains open.
- Clear-text password fallback is intentionally secondary to credential providers. Enabling fallback can expose secrets through normal configuration dumps if sensitive-key filtering is incomplete.
- Dynamic class loading through configuration can fail late with `ClassNotFoundException` or interface-mismatch errors and is a code-loading boundary for downstream integrations.
- `KeyProvider` implementations must be thread safe and must make `flush()` durable. Caching, generated key material, password handling, and key rolling are high-risk areas for encryption correctness.
- `KeyProvider.findProvider` chooses a provider by key existence. Duplicate key names across providers can make resolution order significant.
- `AbstractFileSystem` requires strict URI scheme/authority and path validation. Mis-qualification can route operations to the wrong filesystem or reject valid relative paths.
- Many filesystem operations are optional or default to unsupported behavior. ACLs, xattrs, snapshots, storage policies, symlinks, multipart uploads, byte-buffer reads, readahead/drop-behind, and unbuffering must be capability-checked by portable callers.
- `openFileWithOptions` returns a `CompletableFuture` but the base implementation performs a blocking open before returning a completed future. Callers must not assume asynchronous execution unless the implementation documents it.
- `BlockLocation` semantics differ for replicated and erasure-coded files. In erasure-coded files, offset/length describe logical block groups and hosts include data plus parity locations.
- `ChecksumFileSystem` must keep checksum sidecars synchronized across rename, delete, concat, truncate, copy, local-output completion, and metadata updates. Partial failures can leave orphaned or stale checksum files.
- Deprecated constants such as MapReduce-era IO sort keys and shell timeout aliases must remain present for binary/source compatibility even when newer keys are preferred.

## Test Signals

Compatibility tests should parse this XML and assert the presence, visibility, deprecation status, and signatures of the covered public/protected API, especially overloaded `Configuration.addResource`, typed getters/setters, `writeXml`/`dumpConfiguration`, key-provider operations, `AbstractFileSystem` create/rename/open/list/status methods, stream capability interfaces, `ChecksumFileSystem` create/open/delete/list/copy hooks, and the visible `CommonConfigurationKeysPublic` constants.

Configuration behavior tests should cover resource precedence, final-parameter blocking, lazy loading, `reloadConfiguration`, global `reloadExistingConfigurations`, deprecated-key alias propagation and warnings, variable expansion from properties/environment/system properties, typed parsing failures, trimmed versus raw values, tag queries, property-source reporting, class loading/interface validation, XML writing, JSON-style dumping, `Writable` round trips, and sensitive password lookup through credential providers with and without clear-text fallback.

Key-provider tests should cover service-loader factory resolution from URI paths, transient versus persistent providers, key creation with supplied and generated material, metadata lookup, current-key version selection, rolling new versions, cache invalidation, delete semantics, duplicate key names across providers, password-required warnings/errors, close behavior, and `flush()` durability.

Filesystem implementation tests should exercise `AbstractFileSystem` URI validation, scheme/authority mismatch handling, path qualification, default ports, statistics tables, server defaults by path, create option normalization, rename overwrite/no-overwrite behavior, symlink resolution, block locations, file status and located listing, corrupt-block iterators, checksum verification toggles, ACL/xattr/snapshot/storage-policy optional paths, capability checks, and unsupported-operation defaults.

Checksum filesystem tests should verify checksum-file naming, checksum length calculation, bytes-per-sum, read verification, write checksum generation toggles, append/truncate/concat behavior, rename/delete/list filtering of checksum files, local copy behavior with optional CRC copying, checksum failure reporting, and stale sidecar cleanup after partial failures.

Stream and metadata tests should cover byte-buffer positioned reads, full reads, buffer position/limit behavior on success and failure, sequential byte-buffer reads, drop-behind/readahead hints, unbuffer support, abort visibility guarantees for output streams, Avro `SeekableInput` length/seek/tell/read behavior, batched listing capability advertisement, and `BlockLocation` round trips for replicated and erasure-coded layouts.

## Cross-Chunk Notes

This is the first chunk for `Apache_Hadoop_Common_3.3.3.xml`; it starts at the XML prologue and reaches the middle of `CommonConfigurationKeysPublic`. Later chunks are required to complete the constants table and the rest of the Hadoop Common 3.3.3 API surface. Do not treat this chunk as a complete report for `Configuration`, `AbstractFileSystem`, or filesystem configuration constants until the merge/reconciliation lane combines all mapped chunks for the source file.

### subset-b-007205: lines 6067-12059

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml lines 6067-12059

## Scope And Purpose

This chunk is part of Hadoop Common's generated JDiff API description for Apache Hadoop Common 3.3.3. It is not executable source; it records public/protected API signatures, inheritance, visibility, deprecation text, checked exceptions, parameters, and Javadoc for API compatibility review. The chunk starts in the final fields of `org.apache.hadoop.fs.CommonConfigurationKeysPublic`, covers several core `org.apache.hadoop.fs` public types completely, and ends inside the public fields of `org.apache.hadoop.fs.FileSystem`.

The dominant purpose of this slice is to describe the stable filesystem API surface exposed by Hadoop Common:

- Common security/KMS/credential/HTTP/service configuration key constants.
- Filesystem metadata containers: `ContentSummary`, `FileStatus`, and `FileChecksum`.
- Creation semantics via `CreateFlag`.
- User-facing filesystem APIs: `FileContext` and `FileSystem`, including path resolution, creation, open/read, metadata, listing, symlink, ACL, xattr, snapshot, storage-policy, statistics, builder, and multipart-upload contracts.

Because this is JDiff XML, control-flow and persistence details are inferred from documented semantics, inheritance, method abstractness, default behavior descriptions, and exceptions. The implementation bodies live in the corresponding Java sources; this file is the compatibility contract consumed by API-diff tooling.

## Important APIs, Types, And Contracts

### `CommonConfigurationKeysPublic` Tail

Lines 6067-6435 complete `org.apache.hadoop.fs.CommonConfigurationKeysPublic`. The chunk lists public static final constants for:

- KMS encrypted key cache settings: `KMS_CLIENT_ENC_KEY_CACHE_SIZE`, low-watermark, refill thread count, expiry, and defaults.
- KMS client timeout/failover knobs: timeout seconds, max retries, base/max failover sleep in milliseconds.
- Secure random and crypto-related keys: Java secure random algorithm, secure random implementation, secure random device file path and default.
- Shell and deletion safety settings: missing default FS warning and safe delete file-count limit.
- HTTP observability and timeout settings: HTTP logs enabled, Prometheus enabled, HTTP idle timeout.
- Credential provider settings: credential provider path, clear-text fallback and default, credential password file, sensitive config key regex/default.
- Hadoop tagging settings: system tags, custom tags, and deprecated/replacement-looking `HADOOP_TAGS_SYSTEM` / `HADOOP_TAGS_CUSTOM`.
- Service shutdown timeout and default.

The class-level doc says this class contains publicly documented common configuration keys and should generally not be used directly, preferring `CommonConfigurationKeys`. Many constants point consumers to `core-default.xml`, making this API an integration bridge between code constants and configuration documentation.

### `ContentSummary`

`ContentSummary` extends `QuotaUsage` and implements `Writable`. It models aggregate content metrics for a file or directory.

Important API points:

- Deprecated constructors exist for binary/source compatibility; docs direct new use to `ContentSummary.Builder`.
- Count accessors include length, directory count, file count, snapshot length/counts, snapshot space consumed, and erasure coding policy.
- Static header helpers expose CLI/report formatting contracts: `getHeader(boolean)`, `getSnapshotHeader()`, `getHeaderFields()`, and `getQuotaHeaderFields()`.
- Multiple `toString` overloads drive report output: quota display, human-readable units, storage-type quota display, snapshot inclusion/exclusion, and selected storage types.
- `toSnapshot(boolean)` formats snapshot counts separately.
- `equals` and `hashCode` are part of the public contract, so changes to represented fields affect compatibility and test expectations.

The key integration point is filesystem reporting: `FileSystem.getContentSummary(Path)` returns this type, and shell/UI consumers rely on its header and string layout.

### `CreateFlag`

`CreateFlag` is a public enum whose JDiff slice exposes enum utility methods and validation helpers:

- `values()` and `valueOf(String)`.
- `validate(EnumSet<CreateFlag>)`.
- `validate(Object path, boolean pathExists, EnumSet<CreateFlag>)`.
- `validateForAppend(EnumSet<CreateFlag>)`.

Documented create semantics include `CREATE`, `APPEND`, `OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`. Invalid combinations include `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`. The append validation contract requires `APPEND` and rejects `OVERWRITE`.

This enum is a critical control surface for `FileSystem.create(...)`, `FileContext.create(...)`, builder APIs, and implementations that must enforce compatible behavior across local filesystems, HDFS, and object-store adapters.

### `FileAlreadyExistsException`

This public `IOException` subtype has default and message constructors. It is thrown when a target already exists and the operation is not configured to overwrite. The API is small but important because it distinguishes existence conflicts from generic I/O failure in create/rename code paths.

### `FileChecksum`

`FileChecksum` is an abstract `Writable` for file checksum metadata. Abstract methods define the required checksum payload:

- `getAlgorithmName()`.
- `getLength()`.
- `getBytes()`.

It also exposes `getChecksumOpt()`, `equals(Object)`, and `hashCode()`. Equality is documented as algorithm plus value equality. `FileSystem.getFileChecksum(Path)` and `getFileChecksum(Path, long)` return this type or `null` if checksums are unsupported.

### `FileContext`

`FileContext` is a public user-facing filesystem facade implementing `PathCapabilities`. Its class documentation positions it as the analogue of per-process Unix file state, with a default filesystem and umask, while server-side defaults cover home directory, replication, block size, buffer size, encryption transfer, and checksum options.

Factory and state APIs:

- `getFileContext(...)` overloads create contexts from default configuration, `URI`, `Configuration`, both URI/configuration, `AbstractFileSystem`, or user identity.
- `getLocalFSFileContext(...)` overloads create local contexts.
- `setWorkingDirectory(Path)` and `getWorkingDirectory()` maintain context-level path resolution state.
- `getUgi()`, `getHomeDirectory()`, `getUMask()`, and `setUMask(FsPermission)` expose per-context identity and permission defaults.
- Protected `getFSofPath(Path)` selects the bound `AbstractFileSystem` for absolute or qualified paths.

Core operations:

- Path normalization and resolution: `resolvePath`, `makeQualified`, `resolve`, and `resolveIntermediate`.
- Creation: stream-returning `create(Path, EnumSet<CreateFlag>, Options.CreateOpts...)` and builder-returning `create(Path)` / `createFile`-style API via `FSDataOutputStreamBuilder`.
- Directory and deletion: `mkdir`, `delete`, and `deleteOnExit`.
- Read/open: `open(Path)` and `open(Path, int)`, plus builder `openFile(Path)`.
- Mutation: `truncate`, `setReplication`, `rename`, `setPermission`, `setOwner`, `setTimes`.
- Metadata and location: `getFileStatus`, `getFileLinkStatus`, `getLinkTarget`, `getFsStatus`, `getFileChecksum`, `getServerDefaults`.
- Listing: `listStatus`, `listLocatedStatus`, `listCorruptFileBlocks`.
- Symlink creation and resolution.
- ACL and xattr methods: modify/remove/default/remove-all/set ACLs, get ACL status, set/get/list/remove xattrs.
- Snapshots: create, rename, delete.
- Storage policy: satisfy, set, unset, get, list all policies.
- Capabilities and multipart upload: `hasPathCapability(Path, String)` and `createMultipartUploader(Path)`.

Public fields include `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`. `DEFAULT_PERM` is retained for compatibility after HADOOP-9155 separated directory and file defaults.

The API is structured as a higher-level facade over `AbstractFileSystem`. Many operations mention exceptions applicable to RPC-backed filesystems, which indicates integration with HDFS and remote service implementations. Permission behavior is also significant: `FileContext` applies umask before calling lower-level primitive methods in `FileSystem` during the migration path.

### `FileStatus`

`FileStatus` is a serializable, writable, comparable metadata record for a file, directory, or symlink. It implements `Writable`, `Comparable`, `Serializable`, and `ObjectInputValidation`.

Important state exposed by constructors and accessors:

- Length, directory/file/symlink kind, block size, replication, modification time, access time.
- `FsPermission`, owner, group, path, and symlink target.
- Attribute flags for ACL, encryption, erasure coding, and snapshot-enabled state.
- Static `attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts booleans into the attribute flag set.
- Shared empty `NONE` attribute set.

Behavioral contracts:

- `isDir()` is deprecated in favor of explicit `isFile()`, `isDirectory()`, and `isSymlink()`.
- `compareTo(FileStatus)` orders by file status path; `compareTo(Object)` was restored for HADOOP-14683 binary compatibility.
- `equals(Object)` and `hashCode()` are path-based, not deep metadata equality.
- `readFields(DataInput)` and `write(DataOutput)` are deprecated in favor of PBHelper/protobuf serialization, but remain public compatibility points.
- `validateObject()` participates in Java object deserialization validation.

This type is central to almost every listing and metadata API in `FileSystem` and `FileContext`.

### `FileSystem`

`FileSystem` is an abstract public class extending `Configured` and implementing `Closeable`, `DelegationTokenIssuer`, and `PathCapabilities`. This chunk covers the constructor and a large public/protected API subset through early fields.

Instantiation, caching, and identity:

- Static `get(...)` overloads resolve a filesystem from `Configuration`, `URI`, and optionally user name.
- `newInstance(...)` overloads always return a new object, unlike cache-aware `get(...)`.
- `getLocal(Configuration)` and `newInstanceLocal(Configuration)` create local filesystem instances.
- `getDefaultUri(Configuration)` / `setDefaultUri(...)` read and mutate the configured default filesystem.
- `initialize(URI, Configuration)` is called after construction and before use; overriding implementations must call super.
- `getUri()` is abstract; `getScheme()`, `getCanonicalUri()`, `canonicalizeUri(URI)`, and `getDefaultPort()` define URI identity and default-port normalization.
- `getCanonicalServiceName()` integrates with token caches and delegation token lookup.
- `getFileSystemClass(String, Configuration)` discovers implementations through configuration and `ServiceLoader`.
- `closeAll()` and `closeAllForUGI(UserGroupInformation)` close cached instances.

Path and namespace operations:

- `makeQualified(Path)` and `checkPath(Path)` enforce that paths belong to the filesystem.
- `resolvePath(Path)` resolves symlinks or mount points.
- `fixRelativePart(Path)` aligns with `FileContext` relative path handling.
- `getFSofPath(Path, Configuration)` is a protected static helper for dispatching by path.

Read and path-handle APIs:

- Abstract `open(Path, int)` plus convenience `open(Path)`.
- `open(PathHandle)` and `open(PathHandle, int)` support durable handles with constraints.
- Final `getPathHandle(FileStatus, HandleOpt...)` validates ownership and delegates to protected `createPathHandle(...)`.
- Builder APIs: `openFile(Path)`, `openFile(PathHandle)`, and protected `openFileWithOptions(...)` methods returning `CompletableFuture<FSDataInputStream>`.

Create, append, and output APIs:

- Many convenience `create(...)` overloads supply overwrite, buffer size, replication, block size, progress, permissions, `CreateFlag` sets, and checksum options.
- The abstract create primitive is `create(Path, FsPermission, boolean, int, short, long, Progressable)`.
- Extended create with `EnumSet<CreateFlag>` and `Options.ChecksumOpt` links directly to `CreateFlag` validation and checksum configuration.
- `primitiveCreate(...)`, `primitiveMkdir(...)`, and protected rename-with-options are migration hooks for `FileContext`; docs describe them as temporary transition support.
- `createNonRecursive(...)` variants fail if the parent directory does not exist.
- `createNewFile(Path)` creates zero-length files but explicitly documents that the default implementation is not atomic.
- `append(...)` has convenience overloads plus abstract `append(Path, int, Progressable)`.
- `concat(Path, Path[])` is optional by default.
- `createFile(Path)` and `appendFile(Path)` expose `FSDataOutputStreamBuilder` builders; the create builder notes HADOOP-14384 stability/visibility caution.

Mutation and metadata:

- Abstract `rename(Path, Path)` and `delete(Path, boolean)`.
- `truncate(Path, long)` returns `true` for immediate availability or `false` when background block adjustment is needed.
- `setReplication(Path, short)` has default behavior that may return true even if replication is unsupported.
- Quota APIs: `getContentSummary(Path)`, `getQuotaUsage(Path)`, `setQuota(Path, long, long)`, and `setQuotaByStorageType(Path, StorageType, long)`.
- `getFileStatus(Path)` is abstract and is the preferred replacement for deprecated `isDirectory`, `isFile`, `getLength`, `getBlockSize`, and `getReplication`.
- `getServerDefaults()` is deprecated in favor of path-aware `getServerDefaults(Path)`.
- `getDefaultBlockSize(Path)` and `getDefaultReplication(Path)` are path-aware defaults.
- `getStatus()` / `getStatus(Path)` report capacity and usage.
- `setPermission`, `setOwner`, and `setTimes` mutate metadata.

Listing and globbing:

- Abstract `listStatus(Path)` returns non-null arrays and does not guarantee sorted order.
- Filtered and multi-path `listStatus(...)` overloads apply `PathFilter`.
- `globStatus(Path)` and `globStatus(Path, PathFilter)` define shell-style glob syntax and sorted result behavior; no-match behavior differs for glob vs non-glob patterns.
- `listLocatedStatus(Path)` and protected filtered variant return `RemoteIterator<LocatedFileStatus>`-style results with block locations.
- `listStatusIterator(Path)` supports lazy/on-demand listing and should be overridden for efficiency.
- `listFiles(Path, boolean)` recursively or non-recursively lists files with block locations.
- `listCorruptFileBlocks(Path)` is optional and may return duplicates for multi-block corruption.

Local copy/output helpers:

- `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, and `moveToLocalFile` cover local-to-filesystem and filesystem-to-local transfers, with delete-source and overwrite options.
- `copyToLocalFile(..., useRawLocalFileSystem)` can bypass local checksum side files by using `RawLocalFileSystem`.
- `startLocalOutput` and `completeLocalOutput` support writing through local temporary files for remote filesystems.

Lifecycle and persistent side effects:

- `close()` releases locks, deletes paths queued through `deleteOnExit`, removes cached instances, and leaves subsequent use undefined.
- `deleteOnExit(Path)`, `cancelDeleteOnExit(Path)`, and protected `processDeleteOnExit()` maintain a per-filesystem deferred-delete list. The docs call out shutdown uncertainty and high cost on object stores or remote filesystems.
- `getUsed()` and `getUsed(Path)` summarize consumed bytes.
- `msync()` synchronizes client metadata state for consistency-sensitive implementations such as HDFS HA.

Optional feature surfaces:

- Symlinks: `createSymlink`, `getFileLinkStatus`, `supportsSymlinks`, `getLinkTarget`, `resolveLink`, global `areSymlinksEnabled()`, and `enableSymlinks()`.
- Checksums: `getFileChecksum(Path)`, range checksum, `setVerifyChecksum`, and `setWriteChecksum`.
- Snapshots: `createSnapshot`, `renameSnapshot`, and `deleteSnapshot`.
- ACLs: `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, and `getAclStatus`.
- XAttrs: `setXAttr`, `getXAttr`, `getXAttrs`, `listXAttrs`, and `removeXAttr`.
- Storage policies: `satisfyStoragePolicy`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, and `getAllStoragePolicies`.
- Trash: `getTrashRoot(Path)` and `getTrashRoots(boolean)`.
- Capabilities: `hasPathCapability(Path, String)` defaults false unless an implementation can determine support.
- Statistics: deprecated static `getStatistics`, `getAllStatistics`, and `getStatistics(String, Class)` are synchronized and replaced by `getGlobalStorageStatistics()`. `clearStatistics()` and `printStatistics()` remain public, and `getStorageStatistics()` is per-instance.
- Multipart upload: `createMultipartUploader(Path)` returns a builder and may fail early with `IOException` or `UnsupportedOperationException`.

Fields at the end of the chunk include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, and `LOG`. The `LOG` doc warns it is widely used in `org.apache.hadoop.fs` code and tests, so changing it has broad compatibility impact.

## Control Flow And Behavioral Signals

The XML does not contain executable control flow, but the documented API flow is clear:

- Filesystem lookup flows from configuration and URI to implementation discovery, instance creation/initialization, optional cache lookup, and user-context execution through UGI-aware overloads.
- Relative paths are resolved through working directory/default filesystem state in `FileContext` or `FileSystem` before dispatching to concrete filesystem implementations.
- Convenience methods generally funnel to abstract core operations: `open(Path)` to `open(Path, int)`, many `create(...)` overloads to permission/overwrite/buffer/replication/block-size create primitives, `mkdirs(Path)` to `mkdirs(Path, FsPermission)`, and listing helpers to `listStatus` or iterator equivalents.
- Builder APIs defer operation execution until `build()`; `openFileWithOptions(...)` explicitly returns a `CompletableFuture` whose evaluation may surface unsupported path-handle behavior.
- Optional operations default to unsupported, no-op, null, false, or conservative behavior unless subclasses override them. This pattern applies to append support, concat, checksums, symlinks, snapshots, ACLs, xattrs, storage policies, multipart upload, and path capabilities.
- `FileStatus` equality/order flows through path comparison rather than all metadata fields, which affects sets, maps, sorting, and deduplication.

## State And Persistence Behavior

Stateful surfaces visible in this chunk include:

- `FileContext` stores default filesystem, umask, working directory, and UGI identity. These affect every path and permission operation made through the context.
- `FileSystem` stores configuration through `Configured`, URI identity, cached instance membership, working directory in subclasses, delete-on-exit registrations, stream handles, and per-instance storage statistics.
- Static/global `FileSystem` state includes the filesystem cache, global storage statistics, legacy statistics maps, global symlink enablement, implementation-class discovery, and shutdown-hook behavior.
- Persistent filesystem side effects include file creation/overwrite/append/truncate/delete/rename, directory creation, local copy/move, metadata changes, quota changes, ACL/xattr mutation, snapshot operations, storage policy changes, checksum verification/write settings when supported, and trash-root behavior.
- Serialization/persistence contracts are exposed by `Writable` implementations (`ContentSummary`, `FileChecksum`, `FileStatus`) and Java serialization validation in `FileStatus`. Deprecated `FileStatus` Writable methods now point to protobuf conversion but remain part of compatibility.

## Dependencies And Integration Points

This API slice integrates with:

- Hadoop configuration: `Configuration`, `CommonConfigurationKeys`, `core-default.xml`, KMS keys, credential providers, security tags, HTTP/Prometheus settings, and service shutdown settings.
- Hadoop filesystem primitives: `Path`, `AbstractFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `FutureDataInputStreamBuilder`, `MultipartUploaderBuilder`, `FsStatus`, `FsServerDefaults`, `BlockLocation`, `LocatedFileStatus`, `RemoteIterator`, `PathFilter`, `PathHandle`, and `Options`.
- Hadoop security: `UserGroupInformation`, `DelegationTokenIssuer`, delegation-token service naming, `AccessControlException`, credential-provider configuration, Kerberos/token-related constants from the immediately preceding class context.
- Hadoop permission and metadata models: `FsPermission`, `AclStatus`, `AclEntry`, `StorageType`, `BlockStoragePolicySpi`, xattr flag enums, and quota usage.
- Java platform APIs: `URI`, `IOException` and subtypes, `Serializable`, `ObjectInputValidation`, `CompletableFuture`, `ServiceLoader`, `EnumSet`, collections, and logging.
- HDFS/RPC implementations: method docs mention RPC client/server/unexpected-server exceptions for snapshots and distributed block-location behavior.
- Command-line and test consumers: `ContentSummary` formatting helpers and `FileSystem.LOG` are explicitly stable surfaces used outside implementation internals.

## Risks And Compatibility Concerns

- This XML is a compatibility artifact. Any changed signature, visibility, exception, deprecation string, or documented behavior may affect JDiff/API compatibility gates even if implementation tests pass.
- The chunk begins and ends inside classes. Merge logic must combine it with adjacent chunks to avoid losing the earlier `CommonConfigurationKeysPublic` fields and later `FileSystem` fields/nested classes.
- Many `FileSystem` methods are convenience wrappers around abstract methods. Subclass implementers depend on those delegation contracts; changing defaults can alter behavior across HDFS, local filesystems, and object stores.
- `FileSystem.get(...)` cache behavior is explicitly configurable through `fs.$SCHEME.impl.disable.cache`; cache-key changes can cause resource leaks, stale clients, or unexpected sharing across users.
- Delete-on-exit is operationally risky for remote/object stores because shutdown is not guaranteed and deletion may be slow or fail under connectivity issues.
- `createNewFile(Path)` default non-atomicity is a concurrency risk; callers needing atomic create must use stronger filesystem-specific primitives.
- Deprecated APIs are still compatibility-sensitive, especially `FileStatus.compareTo(Object)`, `FileStatus` Writable serialization, legacy `FileSystem` statistics methods, and path-unaware server/default replication/block-size methods.
- `FileStatus.equals` being path-only can surprise callers expecting metadata equality.
- Optional-operation defaults vary between unsupported exceptions, `null`, `false`, no-op, or `true` for unsupported replication. Tests must assert the documented fallback for each operation.
- ACL and xattr methods expose permission-filtered reads; implementations must avoid leaking unauthorized metadata.
- Builder APIs defer validation to `build()` or future evaluation; tests must cover both early and deferred failure modes.
- Configuration key constants are used by external deployments. Renaming or changing defaults for KMS, credential, HTTP, shutdown, and random-source settings can break cluster security or operational behavior.

## Test Signals

Useful validation signals for this API chunk include:

- JDiff or equivalent API-compatibility checks comparing Hadoop Common 3.3.3 public signatures and deprecation text.
- Unit tests for `CreateFlag.validate(...)` covering valid create/append/overwrite combinations and invalid append-overwrite combinations.
- Contract tests for `FileSystem` implementations verifying create/open/append/delete/rename/list/status behavior through both direct APIs and builder APIs.
- Cache tests for `FileSystem.get(...)`, `newInstance(...)`, `closeAll()`, `closeAllForUGI(...)`, and `fs.$SCHEME.impl.disable.cache`.
- Serialization compatibility tests for `FileStatus`, including protobuf replacement paths and legacy Writable methods while they remain public.
- Metadata tests for `FileStatus` equality, comparison, symlink flags, ACL/encryption/EC/snapshot attributes, and `ObjectInputValidation`.
- `ContentSummary` formatting tests for header fields, quota display, human-readable display, storage-type quota display, snapshot inclusion/exclusion, and erasure coding policy reporting.
- Optional-feature contract tests ensuring unsupported checksums, ACLs, xattrs, snapshots, storage policies, symlinks, multipart upload, and path capabilities fail or return defaults as documented.
- Security tests around UGI-specific filesystem acquisition, token service names, credential provider fallback keys, xattr visibility filtering, and ACL mutation.
- Integration tests for HDFS HA `msync()`, block locations, corrupt-block iteration, snapshots, quotas, and storage policies.
- Object-store/local-filesystem tests around non-atomic `createNewFile`, expensive delete-on-exit behavior, local copy checksum side files, and raw local copy mode.

### subset-b-007206: lines 12060-18114

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml lines 12060-18114

## Scope

This chunk is a JDiff API snapshot for Hadoop Common 3.3.3, not executable implementation source. It begins at the tail of `org.apache.hadoop.fs.FileSystem`, then covers the public/protected API records for many `org.apache.hadoop.fs` types from `FileUtil` through `XAttrSetFlag`, the complete `org.apache.hadoop.fs.audit.CommonAuditContext`, FTP filesystem APIs, and the opening of `org.apache.hadoop.fs.statistics` through `IOStatistics.meanStatistics()`. The XML captures signatures, inheritance, implemented interfaces, checked exceptions, public/protected fields, deprecation text, and Javadoc contracts used for compatibility comparison.

## Purpose and major API surface

The closing `FileSystem` fragment exposes constants and state that frame the rest of the filesystem API: `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, the widely referenced `LOG`, shutdown-hook priority, trash and home-directory prefixes, and protected per-instance `statistics`. Its class Javadoc explicitly treats HDFS behavior as the normative baseline when documentation and implementation diverge, and warns developers that new public/protected `FileSystem` methods must be reflected through `FilterFileSystem`, `ChecksumFileSystem`, HAR tests, HBase shims, and Hive shims.

`FileUtil` is the static utility surface for local-file and Hadoop-filesystem support work. It converts `FileStatus[]` to `Path[]`, performs recursive delete and delete-on-exit registration, reads symlinks, copies between `FileSystem` instances and local files, builds shell-safe paths, computes local disk usage, extracts zip/tar streams and files, creates symlinks, runs chmod/chown-style permission changes, checks and sets local readability/writability/executability, creates temporary files, replaces files, wraps nullable local listing APIs, builds classpath jars, lists jars in directories, compares filesystem identities, and writes strings through `FileSystem` or `FileContext` with overwrite/append and permission variants. `SYMLINK_NO_PRIVILEGE` is the exposed return-code constant for symlink privilege failures.

`FilterFileSystem` is the primary wrapper/decorator API around another `FileSystem`. It stores a protected `fs` delegate and optional `swapScheme`, exposes `getRawFileSystem()`, and mirrors the broad `FileSystem` surface: URI and path qualification, block locations, path resolution, open/create/append/concat, path handles, non-recursive create, replication, rename/truncate/delete, listings and iterators, working directory, status and mkdirs, local copy staging, defaults and usage, file status, access checks, symlink APIs, checksums, configuration and close, owner/times/permissions, primitive create/mkdir, child filesystems, snapshots, ACLs, xattrs, storage policies, trash roots, stream builders, async open builders, and path capabilities.

The chunk includes builder and stream primitives. `FSBuilder<S,B>` defines typed `opt()` and `must()` options for string, boolean, int, float, double, and string-array values, with `build()` throwing `IllegalArgumentException`, `UnsupportedOperationException`, or `IOException`. `FutureDataInputStreamBuilder` specializes this to return `CompletableFuture<FSDataInputStream>` and optionally accepts a `FileStatus`. `FSDataOutputStreamBuilder` carries filesystem, path, permission, buffer size, replication, block size, recursive parent creation, progress callback, create/overwrite/append flags, checksum options, and abstract output-stream construction.

`FSDataInputStream`, `FSInputStream`, `PositionedReadable`, `Seekable`, `FSDataOutputStream`, `Syncable`, `StreamCapabilities`, and `StreamCapabilitiesPolicy` define the Hadoop stream contract. Inputs support seek, position, positioned reads, readFully, alternate data sources, byte-buffer reads, enhanced pooled buffers, file descriptors, readahead/drop-behind, unbuffering, capability probes, and IO statistics. Outputs support position, close, flush/sync semantics, drop-behind, capability probes, IO statistics, and abort when the wrapped stream is `Abortable`. Capability constants include `hflush`, `hsync`, `in:readahead`, `dropbehind`, `unbuffer`, byte-buffer reads, positioned byte-buffer reads, IO statistics, and abortable streams.

Path, metadata, and storage model APIs are heavily represented. `FsConstants` defines local, FTP, viewfs, viewfs overload, and symlink-loop constants. `FsServerDefaults` serializes server defaults for block size, checksum bytes, packet size, replication, file buffer size, encryption, trash interval, checksum type, key provider URI, and default storage policy. `FsStatus` serializes capacity/used/remaining. `GlobalStorageStatistics` synchronizes registry access for named `StorageStatistics`, while `StorageStatistics` exposes tracked long statistics. `GlobFilter`, `PathFilter`, `InvalidPathException`, and `Path` define POSIX-style glob matching and URI-like path construction/normalization/comparison/qualification. `PathHandle`, `PartHandle`, and `UploadHandle` are opaque serializable byte-buffer handles for stable filesystem references and multipart upload state.

Local filesystem surfaces include `LocalFileSystem`, a checksumed local filesystem wrapper, and `RawLocalFileSystem`, the raw `file:` implementation. They expose `pathToFile`, local copy behavior, checksum-failure reporting, symlink support, local open/create/append/truncate/delete/list/mkdir/status, owner and permission updates via local commands, time setting, path handles, and capability probing.

The chunk also covers higher-level filesystem features: `LocatedFileStatus` extends `FileStatus` with block locations and preserves equality/comparison by path; `MultipartUploader` defines async start/put/complete/abort/abort-under-path operations and extends IO statistics sourcing; `PartialListing` models batched directory listings that may contain either results or a deferred `RemoteException`; `QuotaUsage` reports namespace, space, and storage-type quotas with command-output formatting; `StorageType` models storage media traits and parsing; `Trash` and `TrashPolicy` define pluggable trash movement, checkpointing, expunge, immediate cleanup, emptier runnables, and path-aware trash directories for encryption-zone-safe deletion; `UnsupportedFileSystemException`, `UnsupportedMultipartUploaderException`, `ParentNotDirectoryException`, `FSError`, and `InvalidPathHandleException` expose compatibility-visible failure types; `XAttrCodec` converts xattr byte values to/from text, hex, and base64 forms; and `XAttrSetFlag.validate()` enforces create/replace flag semantics.

`CommonAuditContext` provides thread-local and global audit context state shared across filesystem audit spans. Instance methods add fixed string entries or supplier-backed entries, remove keys, read entries, reset the thread context, test containment, fetch the current audit context, obtain a current thread ID, and evaluate supplier entries. Static global methods set, get, remove, and iterate global entries, while `noteEntryPoint(Object)` records a command name under `AuditConstants.PARAM_COMMAND` if not already set. `PROCESS_ID` is a public process identity built from UUID and timestamp.

`FTPException` is a runtime wrapper for FTP-layer failures. `FTPFileSystem` is a `FileSystem` backed by Apache Commons Net and exposes the `ftp` scheme, default port, initialization from `URI` and `Configuration`, open/create/delete/list/status/mkdir/rename/working-directory/home-directory operations, plus FTP configuration keys for user, password, host, port, data connection mode, transfer mode, timeout, and same-directory-only rename behavior. Its create Javadoc warns that the returned stream must be closed before other APIs are used, or later invocations can block.

The statistics package starts with `DurationStatisticSummary`, a serializable immutable-style summary for duration metrics keyed by statistic name and success/failure dimension, including count, min, max, and cloned `MeanStatistic`. Static helpers fetch success or success/failure summaries from `IOStatistics`. The visible `IOStatistics` interface returns maps for counters, gauges, minimums, maximums, and mean statistics; the unset minimum/maximum constants appear just beyond the chunk boundary.

## Control flow and behavioral contracts

Direct implementation control flow is not present in this XML. The observable flow is the API layering and Javadoc contract. Filesystem calls flow from `Path` resolution and `FileSystem`/`FileContext` builders into scheme-specific implementations; wrapper filesystems must pass calls through `FilterFileSystem` unless they intentionally transform behavior. This pass-through contract is a compatibility risk because new `FileSystem` methods must be added to wrappers and capability probes consistently.

Builder control flow separates optional and mandatory filesystem-specific options. `opt()` entries may be ignored when unrelated to an implementation. `must()` entries are part of the contract: unsupported mandatory options should cause `build()` or the underlying open/create operation to raise `IllegalArgumentException`. `FutureDataInputStreamBuilder.build()` returns a `CompletableFuture`, allowing actual open work and failures to be represented asynchronously.

Stream flow is explicitly stateful. `seek()` changes the current offset, while positioned reads should not change the current offset and are documented as thread-safe in the interface contract, with a warning that not all filesystems actually satisfy this. `readFully()` loops until the requested length is read or EOF is reached. Enhanced byte-buffer reads allocate from a `ByteBufferPool` and require `releaseBuffer()`. `unbuffer()` is mediated by `StreamCapabilitiesPolicy`, and output durability separates `hflush()` visibility to new readers from `hsync()` disk-oriented sync semantics.

Local filesystem flow is partly command/platform driven. `RawLocalFileSystem.setOwner()` and `setPermission()` are documented as using `chown` and `chmod`; `FileUtil` shell-path conversion, symlink creation, chmod/chown helpers, archive extraction, and recursive delete all cross from Java APIs into OS-dependent behavior. `LocalFileSystem.reportChecksumFailure()` moves suspect data aside to a bad-file directory on the same device so storage is not reused.

Trash flow is policy based. `Trash.moveToAppropriateTrash()` resolves symlinks and mount points to choose a trash location in the actual backing volume of the deleted path. `TrashPolicy.initialize(Configuration, FileSystem)` supersedes the home-directory-based initializer because HDFS encryption zones can forbid renames across zone boundaries. Checkpoint and emptier APIs encode periodic cleanup, while immediate expunge deletes all checkpoints.

FTP flow is connection-serialized enough that the API warns callers to close create streams before invoking other `FTPFileSystem` methods. Rename behavior is constrained by `E_SAME_DIRECTORY_ONLY`, append is explicitly unsupported, and file operations depend on configuration-provided credentials, host, data connection mode, transfer mode, and timeout.

Audit flow distinguishes thread-local and global state. Audit spans capture a reference to the current thread context, and that reference can be retained as spans move across threads. Supplier-backed entries are evaluated by `getEvaluatedEntries()` in whichever thread invokes evaluation, so supplier side effects and thread-sensitive values matter. Global entries are visible to all threads and are intended for low-cardinality process-level data such as process ID and entry point.

## State, persistence, and side effects

The persistent filesystem side effects represented here include file contents, directories, symlinks, ownership, permissions, modification/access times, ACLs, xattrs, snapshots, storage policies, quotas, trash directories, multipart upload parts, and path-handle referents. Metadata carriers such as `FsStatus`, `FsServerDefaults`, `LocatedFileStatus`, `QuotaUsage`, and duration summaries are snapshots or serializable views rather than direct mutators.

`FileSystem` and `FilterFileSystem` carry mutable client-side state: configuration, URI identity, working directory, statistics, wrapped delegates, and lifecycle. `GlobalStorageStatistics` is explicitly synchronized and process-global. `CommonAuditContext` combines thread-local per-context maps, supplier entries, global process-wide entries, and a generated process ID; leaking or failing to reset these maps can contaminate later audit spans or tests.

`FileUtil` has high-impact local side effects. Recursive delete can partially delete a tree before returning false; delete-on-exit registers later deletion; archive extraction writes trees; `replaceFile()` alters local files; permission helpers mutate local mode/owner bits; and jar creation writes artifacts representing classpaths.

Multipart upload state is remote and durable until completed or aborted. `UploadHandle` and `PartHandle` are opaque serialized references, `putPart()` uploads numbered pieces, `complete()` combines handles into a final file and returns a `PathHandle`, and `abortUploadsUnderPath()` is explicitly best-effort with possible misses on eventually consistent listings.

## Dependencies and integration points

The APIs integrate across Hadoop Common: `Configuration`, `Path`, `FileSystem`, `FileContext`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `PathHandle`, `FSDataInputStream`, `FSDataOutputStream`, `CreateFlag`, `Options`, `Options.ChecksumOpt`, `Options.HandleOpt`, `Options.Rename`, `RemoteIterator`, `FsPermission`, `FsAction`, ACL types, xattr types, `BlockStoragePolicySpi`, `Progressable`, `DataChecksum.Type`, `RemoteException`, `IOStatistics`, `IOStatisticsSource`, `MeanStatistic`, and audit constants.

Java integration points include `URI`, `File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, `FileDescriptor`, `ByteBuffer`, `Serializable`, `ObjectInputValidation`, `CompletableFuture`, `Runnable`, collections, `Supplier`, and checked exceptions. Platform integration appears through POSIX-like permissions, symlinks, `chmod`, `chown`, shell paths, local filesystem stat behavior, and Windows-specific path handling.

External integration points include Apache Commons Net for `FTPFileSystem`, HDFS as the normative behavior reference for `FileSystem`, viewfs constants and overload patterns, Hadoop shell/JSON xattr display through `XAttrCodec`, and downstream compatibility consumers called out in the Javadocs: `FilterFileSystem`, `ChecksumFileSystem`, HAR tests, HBase shims, and Hive shims.

## Risks and compatibility concerns

Because this is a JDiff compatibility baseline, changes to method signatures, type parameters, visibility, field names, deprecation messages, thrown checked exceptions, class inheritance, implemented interfaces, or Javadoc contracts can break API compatibility checks even without implementation changes.

The broad `FileSystem` and `FilterFileSystem` surfaces are easy to desynchronize. If a new method or capability is added to `FileSystem`, wrappers must either delegate it correctly or deliberately reject capabilities. The source Javadoc explicitly warns that `FilterFileSystem#hasPathCapability(Path, String)` must return false for capability-probed APIs it does not support.

Thread safety is a documented but uneven stream concern. `PositionedReadable` requires thread-safe positioned operations, but warns that not all implementations comply. Applications such as HBase can rely on this; filesystem implementations and wrappers need targeted tests to avoid exposing current-position races.

Path handling is portability-sensitive. `Path` treats strings as URI-like values with additional normalization, handles Windows absolute paths specially, validates deserialized objects to defend against malicious streams, and contains deprecated qualification APIs. Misparsing scheme/authority/path combinations can route operations to the wrong filesystem.

Local operations are platform and privilege sensitive. Symlink creation can fail due to privilege, recursive delete may leave partial state, `chmod`/`chown` behavior varies by OS, FTP rename may be directory-constrained, and FTP create streams can block subsequent operations if not closed.

Trash and encryption-zone behavior is subtle. Older home-directory-based trash APIs are deprecated because encryption zones can forbid cross-zone renames. Callers should use path-aware trash-directory APIs when deleting files in mounted, symlinked, or encryption-zone-backed filesystems.

Audit context can leak between operations. Global entries span all threads, thread-local contexts span filesystems within a thread, and audit spans retain references as they move across threads. Tests must reset context and avoid supplier entries with non-deterministic side effects unless intentional.

Statistics snapshots are not necessarily atomic. `StorageStatistics.getLongStatistics()` states values need not reflect one point in time, `DurationStatisticSummary` can be incomplete for unknown keys, and IO statistics maps expose implementation-defined current values.

## Test signals

Compatibility tests should assert the presence and signatures of every covered type, especially `FileUtil` overloads, `FilterFileSystem` delegation methods, `FSBuilder` typed `opt`/`must` methods, stream capability constants, `FSDataInputStream` byte-buffer and IO-statistics methods, `FSDataOutputStream.abort()`, path-handle interfaces, multipart upload futures, trash policy overloads, `CommonAuditContext` global/thread-local methods, `FTPFileSystem` constants, and `IOStatistics` map accessors.

Behavioral filesystem tests should exercise wrapper delegation through `FilterFileSystem`, path qualification and Windows path parsing, symlink creation/resolution and link-loop limits, positioned-read concurrency, seek/readFully EOF behavior, enhanced byte-buffer allocation/release, unbuffer fallback policy, hflush/hsync semantics, abortable output streams, path handles under file replacement, and storage statistics reset/iteration.

Local utility tests should cover recursive delete of files/directories/symlinks, partial-delete failure handling, delete-on-exit registration isolation, shell path escaping, archive extraction, chmod/chown and readable/writable/executable helpers, null-safe list wrappers, classpath jar creation, jar directory scans, temp-file creation, `replaceFile()`, and filesystem comparison.

Integration tests should cover `LocalFileSystem` and `RawLocalFileSystem` local side effects, checksum-failure quarantine, permission/time updates, trash movement across symlinks/mount points/encryption-zone-like boundaries, policy checkpoint/expunge behavior, FTP configuration and unsupported append, FTP stream close-before-next-operation behavior, xattr encode/decode formats, xattr create/replace validation, multipart upload complete/abort cleanup, and audit context reset/global-entry isolation.

### subset-b-007207: lines 18115-24646

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml lines 18115-24646

## Research scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.3.3, not Java implementation source. The selected range begins at the tail of `org.apache.hadoop.fs.statistics.IOStatistics`, covers the filesystem I/O statistics support package, Hadoop HA service and fencing contracts, protocol-buffer bridge interfaces, and a large part of `org.apache.hadoop.io` serialization APIs through the opening of `WritableComparator`. Conclusions are based on public signatures, inheritance, field constants, declared exceptions, deprecation metadata, and embedded Javadocs.

## Purpose

The range documents public compatibility contracts for three adjacent Hadoop Common areas.

The `org.apache.hadoop.fs.statistics` section standardizes low-cost per-instance I/O metrics. It defines snapshots, aggregation, logging helpers, mean-statistic arithmetic, and a common vocabulary of operation/stream statistic names used by filesystem and object-store implementations.

The `org.apache.hadoop.ha` section defines administrative service-state control for highly available Hadoop services. It covers health checks, transitions to active/standby/observer states, service target metadata, fencing hooks, and exception types used by failover controllers and health monitors.

The `org.apache.hadoop.io` section defines Hadoop's core binary serialization and comparison framework. It includes primitive and array `Writable` wrappers, map-backed writables with per-instance class registries, byte/text comparable types, generic/object writables, sequence-file writer factory APIs, file helpers such as `MapFile` and `SetFile`, stringification, checksums, utility I/O operations, and the base `Writable`/`WritableComparable` contracts used by MapReduce, RPC payloads, and on-disk data formats.

## Important APIs and types

`IOStatistics` ends in this range with `MIN_UNSET_VALUE` and `MAX_UNSET_VALUE`, sentinel constants used when minimum/maximum statistics have never been recorded. `IOStatisticsAggregator.aggregate(IOStatistics)` is the opt-in contract for merging another statistics instance into a current accumulator and returns whether a non-null source was aggregated.

`IOStatisticsLogging` is a final utility class for robust logging of statistics. It extracts statistics from an `IOStatistics` or `IOStatisticsSource`, converts statistics to compact or sorted pretty strings, builds lazy stringifier objects for cheap log-argument use, and logs extracted statistics at debug or a named level. Its Javadocs explicitly say extraction exceptions are caught and downgraded to debug logging, so logging must not destabilize filesystem operations.

`IOStatisticsSnapshot` is a final, serializable, synchronized snapshot and accumulator implementing `IOStatistics` and `IOStatisticsAggregator`. It can be empty, constructed from a source, cleared, overwritten by `snapshot(source)`, or merged via `aggregate(source)`. It exposes synchronized metric maps for counters, gauges, minimums, maximums, and `MeanStatistic` values. Static `serializer()` and `requiredSerializationClasses()` integrate with Hadoop's JSON serialization and with safer Java deserialization allow-lists.

`IOStatisticsSupport` provides factory and helper entry points: `snapshotIOStatistics(statistics)`, an empty `snapshotIOStatistics()` accumulator, `retrieveIOStatistics(Object)` for direct statistics or source objects, and singleton stub duration tracker factories/trackers for no-op instrumentation paths.

`MeanStatistic` is a final serializable and cloneable mutable statistic with synchronized getters and mutators for sample count and sum. It normalizes invalid sample counts to an empty statistic, computes a mean, adds another mean statistic or a sample, supports `copy()`/`clone()`, and defines equality/hash/string behavior.

`StoreStatisticNames` and `StreamStatisticNames` are final constant catalogs. Store-level names include filesystem operations (`OP_OPEN`, `OP_CREATE`, `OP_RENAME`, `OP_DELETE`, ACL/xattr/status operations), object-store request counters (list, continue-list, bulk delete, metadata, copy, put, select), multipart upload counters, throttle/retry/request metrics, and suffixes such as `.min`, `.max`, `.mean`, and `.failures`. Stream-level names include read-open/close/abort counters, bytes read/discarded/skipped, seek and readFully operations, version mismatches, unbuffering, write exceptions, block upload queue/active/pending/committed counters, upload byte totals, queue wait/put request timing, remote read metrics, and block allocation/release counters.

`BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` mark distinct HA failure modes: invalid fencing setup, overall failover failure, failed service health checks, and service transition/operation failure.

`FenceMethod` defines `checkArgs(String)` and `tryFence(HAServiceTarget, String)`. Fencing implementations validate configuration arguments before use and return a boolean success signal when attempting to isolate a target.

`HAServiceProtocol` is the service administration RPC contract. It exposes `monitorHealth()`, `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(StateChangeRequestInfo)`, `transitionToObserver(StateChangeRequestInfo)`, `getServiceStatus()`, and `versionID`. Methods declare `IOException`, `ServiceFailedException`, `AccessControlException`, and health-check failures as appropriate, so callers must distinguish transport/security failures from service-state failures.

`HAServiceProtocolHelper` wraps the same HA operations as static helper methods. Its role is to invoke service protocol methods and normalize remote failures for callers, especially failover-controller code.

`HAServiceTarget` is an abstract endpoint descriptor. It supplies RPC addresses for the service, health monitor, and ZKFC; an optional `NodeFencer`; fencing configuration checks; RPC proxy creation with retry/sleep controls; health-monitor proxy creation; ZKFC proxy creation; fencing parameter maps; transition-target HA state storage; auto-failover enablement; and observer-state support flags. `addFencingParameters(Map)` lets subclasses enrich the map passed to fencing methods.

`HAServiceProtocolPB` and `ZKFCProtocolPB` are protocol-buffer bridge interfaces extending generated protobuf blocking service interfaces plus `VersionedProtocol`, binding the public Java HA/ZKFC contracts to Hadoop IPC.

`AbstractMapWritable` is a configurable `Writable` base for map-like writables. It maintains a per-instance mapping between classes and small byte ids, supports class registration and copying, exposes `getClass(byte)`/`getId(Class)`, carries a `Configuration`, and serializes/deserializes the class-id map.

`ArrayFile`, `MapFile`, `BloomMapFile`, and `SetFile` are file-format helpers around sorted key/value storage. `ArrayFile` extends `MapFile` for dense integer-keyed arrays. `MapFile` exposes static `rename`, `delete`, `fix`, `main`, and file-name constants `INDEX_FILE_NAME` and `DATA_FILE_NAME`. `BloomMapFile` exposes deletion and bloom metadata constants. `SetFile` extends `MapFile` for set-like storage.

`ArrayPrimitiveWritable`, `ArrayWritable`, and `TwoDArrayWritable` serialize primitive arrays, one-dimensional writable arrays, and two-dimensional writable matrices. `ArrayPrimitiveWritable` preserves declared component type and can wrap primitive arrays. `ArrayWritable` carries a writable value class and supports conversion to strings or object arrays. `TwoDArrayWritable` carries a value class and serializes nested writable arrays.

`BinaryComparable` is the base for byte-backed comparable values. It requires subclasses to expose `getBytes()` and `getLength()`, then provides byte-wise comparison, equality, and hashing. `BytesWritable` and `Text` build on it.

Primitive wrapper writables include `BooleanWritable`, `ByteWritable`, `ShortWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, `DoubleWritable`, `VIntWritable`, and `VLongWritable`. They generally provide default/value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`. `VIntWritable` and `VLongWritable` store values in Hadoop variable-length integer encodings.

`ByteBufferPool` defines `getBuffer(boolean direct, int length)` and `putBuffer(ByteBuffer)` for reusable heap/direct byte buffers. `ElasticByteBufferPool` implements the pool with elastic buffer allocation and return.

`CompressedWritable` is a base class for compressed serialized state. It serializes compressed data through `writeCompressed`, lazily inflates via `ensureInflated`, and asks subclasses to implement `readFieldsCompressed`.

`DataOutputOutputStream` adapts `DataOutput` to `OutputStream`, including a static `constructOutputStream(DataOutput)` and byte/array write overloads.

`Stringifier<T>` defines text serialization with `toString(T)`, `fromString(String)`, and `close()`. `DefaultStringifier<T>` implements it using Hadoop `Configuration` and a target class, plus static helpers to store/load one object or arrays in configuration keys.

`EnumSetWritable<E extends Enum<E>>` is a configurable writable collection for enum sets, preserving element type even when the set is empty. It extends `AbstractCollection`, implements `Writable`/`Configurable`, and exposes iterator, size, add, set/get, serialization, equality, hash, string, and configuration methods.

`GenericWritable` stores one writable instance from a subclass-provided whitelist returned by `getTypes()`. It carries configuration, delegates string form to the contained instance, and serializes the type choice plus value. `ObjectWritable` is broader: it stores declared class plus object instance, supports configurable `writeObject`/`readObject`, class loading, and configuration propagation.

`IOUtils` collects stream and filesystem utility operations: stream copying with explicit buffer sizes, counts, configuration-derived buffer sizes, and close policies; compressed-data reads wrapped as `IOException`; `readFully`; `skipFully`; cleanup helpers that ignore close failures; socket close; full writes to `WritableByteChannel` and positional `FileChannel`; directory listing that preserves `IOException`; file/channel fsync; exception wrapping with path/method context; and `readFullyToByteArray(DataInput)`. It exposes a public SLF4J `LOG`.

`MapWritable` and `SortedMapWritable` are mutable map implementations backed by `AbstractMapWritable`. `MapWritable` exposes standard map operations and writable serialization. `SortedMapWritable` exposes sorted-map navigation (`firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`, comparator) plus mutation, lookup, serialization, equality, and hashing.

`MD5Hash` is a writable comparable wrapper around a 16-byte MD5 digest. It supports construction from strings or bytes, reading/writing, static digest creation over strings/byte arrays/input streams, `MessageDigest` access, half/quarter digest extraction, equality, hashing, comparison, string conversion, and `MD5_LEN`.

`MultipleIOException` aggregates several `IOException` instances and exposes `getExceptions()` plus `createIOException(List)` for returning a single exception when multiple close or cleanup failures occur.

`NullWritable` is a singleton writable comparable carrying no data. `get()` returns the singleton; read/write are no-ops; comparison/equality/hash/string are stable.

`RawComparator<T>` extends `Comparator<T>` with byte-level `compare(byte[], int, int, byte[], int, int)`, allowing sort and shuffle code to compare serialized keys without full deserialization.

`SequenceFile` is the main flat binary key/value file format. This range includes default compression type getters/setters and many `createWriter` overloads. The preferred API is `createWriter(Configuration, SequenceFile.Writer.Option...)`; many older overloads are deprecated in favor of it. Non-deprecated overloads still support `FileSystem` or `FileContext`, key/value classes, buffer size, replication, block size, parent creation, compression type, codec, metadata, create flags, and create options. The Javadocs define uncompressed, record-compressed, and block-compressed formats, a common header, sync markers, metadata, compression codec fields, and `SYNC_INTERVAL`.

`Text` is Hadoop's UTF-8 byte-backed string type. It supports construction from strings, other `Text`, or bytes; byte copying and backing-array access; length; code-point lookup by byte position; substring find; setting from string/text/bytes; appending; clearing; string conversion; length-limited and known-length reading; skipping serialized text; writing; equality/hash; static decode/encode helpers with replacement control; `readString`/`writeString` with max-length overloads; UTF-8 validation; byte-buffer code-point extraction; UTF-8 length calculation; and `DEFAULT_MAX_LEN`.

`VersionedWritable` writes a version byte before subclass payload and checks it during `readFields`; subclasses implement `getVersion()`. `VersionMismatchException` reports a mismatch between serialized and current versions.

`Writable` defines Hadoop's simple serialization protocol over `DataOutput` and `DataInput`. `WritableComparable<T>` combines `Writable` and `Comparable<T>` and documents that stable `hashCode()` implementations matter for partitioning. `WritableComparator` begins at the end of this chunk as the comparator implementation for writable comparables; only its constructors are visible in this range.

## Control flow and behavior

The statistics APIs follow a capture, aggregate, and report flow. Producers expose `IOStatistics` maps. Consumers call `IOStatisticsSupport.retrieveIOStatistics(source)` when the source may be either the statistics object or an `IOStatisticsSource`. Snapshots either overwrite current maps from a source through `snapshot(source)` or merge into accumulated maps through `aggregate(source)`. Logging helpers delay string conversion until log evaluation and intentionally tolerate nulls, wrong source types, and extraction failures.

Mean-statistic behavior centers on synchronized mutation of `samples` and `sum`. Invalid or non-positive sample counts become an empty statistic. Adding a sample or another statistic mutates the current accumulator; `mean()` derives the average from the two counters.

HA control flow is RPC and failover-controller oriented. Health monitors call `monitorHealth()` and inspect `HAServiceStatus`. Failover controllers use `HAServiceTarget` to locate service, health, and ZKFC endpoints, construct proxies, verify fencing configuration, and inject target-specific fencing parameters. State transitions carry `StateChangeRequestInfo` so services can distinguish request sources and enforce authorization or policy. Fencing methods validate arguments before use and return a boolean success/failure signal when trying to isolate a stale active.

Writable control flow is explicit serialization into `DataOutput` and reconstruction from `DataInput`. Primitive writables write fixed or variable-length binary values. Array writables write element counts and then each element. Map writables write a class-id table followed by entries so dynamic writable types can be deserialized. `GenericWritable` selects among a bounded type whitelist. `ObjectWritable` writes declared class metadata and object payload, using `Configuration` for class loading. `VersionedWritable` inserts a version check before subclass fields.

Sequence-file writer creation is option-assembly flow. Modern callers build `Writer.Option` arrays and call the central factory. Older overloads progressively specify filesystem/context, path, key/value classes, compression, codec, metadata, progress, and file-creation settings before delegating internally to the writer implementation. The on-disk flow begins with a common header and sync marker, then writes records differently depending on no compression, record compression, or block compression.

Text and binary comparison flows avoid unnecessary object creation. `BinaryComparable` compares byte arrays directly. `RawComparator` permits serialized-key byte comparisons. `Text` tracks byte length separately from backing capacity, validates/decodes UTF-8 as needed, and can scan/find/codepoint-traverse without first converting the whole value to `String`.

`IOUtils` control flow is defensive around partial reads/writes and cleanup. `copyBytes`, `readFully`, `skipFully`, and channel `writeFully` loop until requested work completes or fail with `IOException`. Cleanup methods intentionally swallow close failures and are documented as exception-handler-only utilities. `wrapException` preserves or specializes important exception types while adding path and method diagnostics.

## State and persistence behavior

Most statistics objects are in-memory process-local metrics. `IOStatisticsSnapshot`, however, is explicitly serializable and JSON-serializable so frameworks can ship captured statistics back from distributed workers. The snapshot uses map fields for counters, gauges, min/max, and means; synchronized access indicates mutable shared state within a JVM, not atomic capture from arbitrary sources.

`StoreStatisticNames` and `StreamStatisticNames` persist only as stable public string constants. Their practical persistence impact is external: metrics sinks, logs, dashboards, and tests may key on exact names, so renaming or reclassifying constants would be a compatibility break.

HA service state lives in the target service and failover-controller ecosystem, not in these API descriptor objects. `HAServiceTarget` does carry local configuration-derived state such as transition-target HA status and exposes derived addresses, fencers, and fencing parameter maps. Fencing effects are external and operational: they may kill processes, revoke access, or otherwise isolate a target outside the JVM.

Writable objects persist their state directly to `DataOutput` streams. This is both wire format and file format for many Hadoop components. Stable serialization matters for MapReduce shuffle keys, RPC arguments, sequence files, map files, configuration-encoded stringified objects, and long-lived data files. `VersionedWritable` adds a version byte to support evolution but will throw `VersionMismatchException` unless subclasses handle mismatches.

`SequenceFile` persists a structured file with header metadata, key/value class names, compression flags, codec class, metadata, sync markers, and binary key/value records or compressed blocks. `MapFile`, `ArrayFile`, `BloomMapFile`, and `SetFile` layer indexed or set-like access patterns on persisted file structures. `MD5Hash` persists a fixed 16-byte digest. `Text` persists UTF-8 bytes preceded by a length encoded using Hadoop's variable-length integer convention.

Byte-array and buffer classes expose mutable backing storage. `BytesWritable.getBytes()` and `Text.getBytes()` return backing arrays whose valid content is bounded by length; capacity can exceed logical length. `ArrayPrimitiveWritable` wraps arrays and its Javadocs in adjacent API docs indicate no-copy behavior, so caller mutation can affect later serialization.

## Dependencies and integration points

Statistics APIs integrate with `IOStatisticsSource`, `DurationTracker`, `DurationTrackerFactory`, `JsonSerialization`, `MeanStatistic`, SLF4J logging, and filesystem/object-store implementations that publish metrics under the shared name constants.

HA APIs integrate with Hadoop IPC (`VersionedProtocol`), generated protobuf services, `ZKFCProtocol`, `NodeFencer`, `HAServiceStatus`, `StateChangeRequestInfo`, `Configuration`, security authorization (`AccessControlException`), network endpoints (`InetSocketAddress`), retry/sleep parameters, and service-specific subclasses of `HAServiceTarget`.

Writable APIs integrate with Java `DataInput`/`DataOutput`, `InputStream`/`OutputStream`, NIO `ByteBuffer`, `WritableByteChannel`, `FileChannel`, `File`, `FilenameFilter`, `Socket`, `Configuration`, `Configurable`, Hadoop `FileSystem`, `FileContext`, `Path`, create flags/options, `FSDataOutputStream`, `Progressable`, compression codecs, and Hadoop's sort/shuffle comparator stack.

Configuration integration is especially broad. `DefaultStringifier` stores serialized values in configuration keys. `EnumSetWritable`, `GenericWritable`, `ObjectWritable`, and `AbstractMapWritable` carry `Configuration` for nested values and class loading. `SequenceFile` consults or mutates configuration for default compression type.

## Risks and edge cases

`IOStatisticsSnapshot.snapshot()` is documented as not atomic through the support helper, so callers aggregating live mutable sources may observe mixed-time values. Snapshot map access is synchronized on the snapshot object, but that cannot make the original source's exported maps atomic.

Statistics logging intentionally catches exceptions. This is safe for production paths but can hide broken statistics providers unless debug logs or tests assert extraction behavior.

Mean statistics can lose information or overflow if sample sums grow past `long` capacity. Empty statistics and invalid sample counts are normalized, so tests must check both `samples` and `sum` rather than relying only on `mean()`.

Metric name constants are compatibility-sensitive. Downstream dashboards, object-store performance tests, and contract tests may assume exact strings and suffix semantics such as min/max/mean/failures.

HA transition APIs are high-risk operational controls. Callers must handle authorization, service failure, health-check failure, and network `IOException` distinctly. Observer-state support is optional, and `supportObserver()` must be checked before assuming observer transitions are valid.

Fencing configuration errors can make failover unsafe. `checkFencingConfigured()` and `FenceMethod.checkArgs()` need to be exercised before a failover event, not only after a stale active is suspected. A `false` fencing result must be treated as failure to isolate the previous active.

`HAServiceTarget` exposes several addresses that may differ: service RPC, health monitor RPC, and ZKFC RPC. Using the wrong endpoint can break health checks or administrative commands even if normal service RPC works.

Writable serialization requires a public no-arg constructor for many deserialization paths. Missing constructors, unstable `hashCode()`, non-deterministic comparison, or changed wire order will break MapReduce sorting, partitioning, RPC compatibility, and persisted data.

`AbstractMapWritable` uses byte ids for class mappings, so there is a practical limit on distinct writable classes in one map instance. Dynamic class-id state also means copies and reads must preserve the class table exactly.

Backing-array access in `BytesWritable` and `Text` is easy to misuse. Callers must honor logical length and avoid assuming the returned byte array is trimmed or immutable. `BytesWritable.setCapacity()`/`setSize()` and `Text.append()` can expose stale capacity bytes if callers serialize or compare incorrectly.

`Text` works in UTF-8 byte offsets, not Java UTF-16 character indexes. `charAt`, `find`, decode, validate, and `bytesToCodePoint` can fail or return byte positions that surprise callers mixing byte and character indexing. Max-length overloads must be used when reading untrusted data.

`IOUtils.cleanup*` and `closeStream(s)` swallow all throwables by design and are only appropriate during exception cleanup. Using them on primary close paths can hide data-loss failures. `readFullyToByteArray(DataInput)` warns that infinite inputs never return and can exhaust memory.

`SequenceFile` has many deprecated writer overloads retained for compatibility. New code should use the option-based factory to avoid overload confusion. Compression type, codec, metadata, create flags, parent creation, and sync intervals are part of persisted format and read compatibility.

`ObjectWritable` and Java class loading are security-sensitive when reading untrusted data. Declared classes, configurations, and class loaders must be constrained in code paths that process remote or user-supplied serialized values.

## Test signals

Good coverage for code relying on this chunk should include statistics snapshot tests for null sources, overwrite versus aggregate semantics, synchronized map visibility, mean-statistic merging, empty min/max sentinels, JSON round trips, Java serialization class allow-list coverage, and lazy logging that tolerates wrong source types and provider exceptions.

Metric vocabulary tests should assert stable `StoreStatisticNames` and `StreamStatisticNames` strings for externally consumed counters, including object-store request counters, multipart upload counters, stream seek/read/write counters, and min/max/mean/failure suffixes.

HA tests should cover health-monitor success and failure, access-control failure propagation, active/standby/observer transition requests, optional observer support, `HAServiceProtocolHelper` remote exception handling, service/health/ZKFC proxy construction, fencing parameter injection, invalid fencing arguments, missing fencer configuration, false fencing results, and auto-failover enablement.

Writable tests should round-trip every primitive writable, variable-length integer edge values, arrays, two-dimensional arrays, enum sets including empty sets with explicit element type, `MapWritable`/`SortedMapWritable` with multiple key/value classes, `GenericWritable` accepted and rejected types, `ObjectWritable` declared-class handling, `NullWritable` singleton behavior, `VersionedWritable` mismatch handling, and `MD5Hash` digest/string/compare behavior.

Comparator tests should compare object-level and byte-level ordering for `BinaryComparable`, `BytesWritable`, `Text`, primitive writables, and custom `WritableComparable` keys. They should also assert stable hash codes across JVM instances for types used as keys.

`Text` tests need valid and invalid UTF-8 cases, multibyte code points, byte-offset `charAt`, substring `find`, append/clear/set behavior, max-length read/write enforcement, decode with and without replacement, `utf8Length`, and backing-array capacity larger than logical length.

`IOUtils` tests should cover copy loops with and without close, exact count copying, EOF behavior in `readFully` and `skipFully`, short channel writes, compressed-stream error wrapping, directory listing failures that `File.list()` would hide, fsync for files and directories, close suppression only in cleanup paths, socket close, exception wrapping preserving `InterruptedIOException` and `PathIOException`, and bounded use of `readFullyToByteArray`.

`SequenceFile` tests should exercise the option-based writer factory, deprecated overload compatibility, uncompressed/record-compressed/block-compressed writers, codec selection, metadata preservation, sync marker seekability, create-parent behavior, `FileContext` create flags/options, default compression type configuration, and reader compatibility across files written by old overloads.

File-format helper tests should cover `MapFile.rename/delete/fix`, `ArrayFile` dense key behavior, `SetFile` membership semantics, and `BloomMapFile` sidecar deletion/metadata expectations.

### subset-b-007208: lines 24647-30892

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml lines 24647-30892

## Research scope

This chunk is a JDiff XML public API snapshot for Apache Hadoop Common 3.3.3, not Java implementation source. The range begins inside `org.apache.hadoop.io.WritableComparator`, covers the remainder of core `org.apache.hadoop.io` serialization helpers, compression stream/codec contracts, erasure-code schema metadata, TFile public helpers, Hadoop serializer bindings, log metrics, most of the metrics2 public API and mutable metric library, metrics sinks, selected metrics utilities, and then ends inside the opening of `org.apache.hadoop.net.AbstractDNSToSwitchMapping`. Findings below are based on class/interface signatures, visibility, inheritance, fields, declared exceptions, constants, and embedded Javadocs.

## Purpose

The slice documents Hadoop Common's public contracts for binary serialization, compressed I/O, type-specific serializer registration, and metrics export. The `org.apache.hadoop.io` APIs provide the low-level `Writable` comparison, factory, and variable-length encoding utilities that support RPC, sequence files, TFile, and other on-disk/wire formats. The compression package defines reusable codec, compressor, decompressor, split-compression, direct-buffer decompression, stream wrapper, codec discovery, and resource-pooling abstractions used by filesystem, MapReduce, and storage readers.

The later packages document how Hadoop publishes observability data: immutable metric records and tags, mutable metric sources, record builders, visitors, filters, default metrics-system lifecycle, MBean registration, caches for sparse-update sinks, and concrete file/Graphite/HDFS/StatsD sink entry points. The final net package lines start the topology mapping base class used by Hadoop's rack-awareness layer.

## Important APIs and types

`WritableComparator` is the tail of the class from the previous chunk. This range includes the protected constructor accepting key class, `Configuration`, and instance-creation behavior; static comparator lookup and registration through `get(...)` and `define(...)`; `Configurable` methods; key allocation with `newKey()`; object and raw-byte `compare(...)` overloads; byte lexicographic comparison; byte hashing; primitive byte-array readers; and VInt/VLong byte-array decoders. The API exists so compare-heavy paths can avoid deserializing whole keys when an optimized raw comparator is available. Registered comparators are documented as thread-safe.

`WritableFactories` and `WritableFactory` provide a global factory registry for `Writable` implementations, especially non-public writable classes that `ObjectWritable` cannot instantiate directly through ordinary reflection. `setFactory`, `getFactory`, and `newInstance` are the main surface, with configuration-aware instantiation where available.

`WritableUtils` is a final utility holder for Hadoop's `Writable` wire-format helpers. It covers compressed byte arrays and strings, plain UTF string read/write, string arrays, debug display of byte arrays, serialization-based clone helpers, VInt/VLong writing and reading, bounded integer decoding with `readVIntInRange`, encoded-size and sign helpers, enum serialization by string name, exact skipping, serialization of multiple writables to a byte array, and guarded string reading through `readStringSafely`. `cloneInto` remains in the public API but is deprecated in favor of `ReflectionUtils.cloneInto`.

The `org.apache.hadoop.io.compress` package defines the primary compression contracts. `CompressionCodec` is the central codec interface: it creates compression/decompression streams, exposes compressor/decompressor classes, allocates compressor/decompressor instances, and supplies a default filename extension. `DirectDecompressionCodec` adds direct `ByteBuffer` decompression support through `DirectDecompressor`, while `SplittableCompressionCodec` creates `SplitCompressionInputStream` instances for compressed data ranges.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases that wrap `InputStream`/`OutputStream`, surface underlying `IOStatistics`, and define reset/finish behavior. `CompressorStream` and `DecompressorStream` adapt `Compressor` and `Decompressor` state machines to stream reads and writes, with fields for the codec object, buffers, EOF/closed state, and close/reset handling. `BlockCompressorStream` and `BlockDecompressorStream` add block framing semantics, compressing no more than a configured block and decoding framed compressed blocks.

`Compressor` and `Decompressor` are stateful codec engines. They accept input buffers, optional dictionaries, report bytes read/written or remaining compressed data, expose `needsInput`, `needsDictionary`, `finish`, `finished`, `reset`, and `end`, and perform byte-buffer style `compress`/`decompress` calls. `Compressor.reinit(Configuration)` lets pooled compressors be reused with new settings.

Concrete codec-facing classes in this range include `BZip2Codec`, `DefaultCodec`, `GzipCodec`, and `PassthroughCodec`. `BZip2Codec` also implements split decompression via a `READ_MODE`-like read-mode parameter. `DefaultCodec` and `GzipCodec` expose direct decompressor creation. `PassthroughCodec` is a special no-transform codec with configurable extension constants. `CodecConstants` records default filename suffixes for default, bzip2, gzip, lz4, passthrough, snappy, and zstandard codecs.

`CodecPool` is the global compressor/decompressor lease pool. It returns codec-specific compressor/decompressor instances, accepts them back through `returnCompressor` and `returnDecompressor`, and exposes leased-resource counts for tests or diagnostics. `CompressionCodecFactory` discovers codecs from `io.compression.codecs`, Java `ServiceLoader`, and built-ins; resolves codecs by path suffix, class name, short name, alias, or class; removes codec suffixes from filenames; and has a small `main` test utility.

`ECSchema` in `org.apache.hadoop.io.erasurecode` is a value object for erasure-code policy shape. It can be built from a map of options or from codec name, data-unit count, parity-unit count, and optional extras. It exposes constants for option keys, getters, `toString`, `equals`, and `hashCode`.

The TFile section contains checked exception types `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist`, `RawComparable` for byte-array backed comparison, `TFile` public constants and helpers, and `Utils` variable-length encoding/search helpers. `TFile.makeComparator` creates raw comparators from comparator names, `getSupportedCompressionAlgorithms` lists accepted compression labels, and public constants identify `gz`, `lzo`, `none`, `memcmp`, and Java-class comparator prefixes. `Utils` duplicates TFile-specific VInt/VLong and string encoding plus lower/upper-bound binary-search helpers over lists and arrays.

The serializer package records bindings for Java object serialization and Writable serialization. `JavaSerialization`, `JavaSerializationComparator`, and `WritableSerialization` expose public constructors, while docs note Java serialization support for `Serializable` and Writable serialization that delegates to the `Writable` methods. The Avro serializer package includes marker `AvroReflectSerializable`, `AvroReflectSerialization` with the `AVRO_REFLECT_PACKAGES` configuration key, abstract/base `AvroSerialization` with `AVRO_SCHEMA_KEY`, and `AvroSpecificSerialization` for Avro `SpecificRecord` types.

`EventCounter` in `org.apache.hadoop.log.metrics` is a Log4J appender that counts warning, error, and fatal events. Its API has `append`, `close`, and `requiresLayout`, making it a bridge from logging events into metrics-style counters.

The `org.apache.hadoop.metrics2` package defines the metrics framework core. `AbstractMetric` is the immutable metric value base with `MetricsInfo`, numeric value, `MetricType`, visitor dispatch, equality/hash/toString. `MetricsInfo`, `MetricsTag`, `MetricsRecord`, `MetricsCollector`, `MetricsRecordBuilder`, `MetricsVisitor`, `MetricsSink`, `MetricsSource`, `MetricsPlugin`, `MetricsFilter`, `MetricsException`, `MetricsSystem`, and `MetricsSystemMXBean` form the main publication contract. Builders accept tags, immutable metrics, counters, gauges across primitive numeric types, context tags, parent collector navigation, and fluent `endRecord`. Visitors receive typed callbacks for gauges and counters.

`MetricsJsonBuilder` and `MetricStringBuilder` are concrete `MetricsRecordBuilder` implementations for textual dumps. They consume the same builder calls as sinks/sources but render records to JSON or delimited strings.

Metrics annotations are represented by marker annotation types `Metric` and `Metrics`. Filter implementations in `metrics2.filter` include `GlobFilter` and `RegexFilter`; both compile user patterns to `com.google.re2j.Pattern` and plug into the `MetricsFilter` acceptance contract.

The `metrics2.lib` package supplies source-side mutable metric state. `DefaultMetricsSystem` is a singleton-style enum with initialize/instance/shutdown and mini-cluster mode controls. `Interns` interns `MetricsInfo` and `MetricsTag` objects. `MetricsRegistry` owns a record's metadata, tags, and mutable metrics; it creates typed counters and gauges, quantiles, stats, rates, aggregated rates, and rolling averages; adds samples by metric name; sets context; tags records with optional override behavior; and snapshots all mutable metrics into a `MetricsRecordBuilder`.

The mutable metric hierarchy includes `MutableMetric` with changed-flag lifecycle and conditional snapshotting; `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` for monotonic counters; `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong` for increment/decrement/settable gauges; `MutableStat` for sample statistics with optional extended stats and min/max reset; `MutableRate`, `MutableRates`, and `MutableRatesWithAggregation` for rates keyed by protocol methods or named samples; `MutableQuantiles` for scheduled rolling quantile estimation; and `MutableRollingAverages` for thread-local rolling averages with explicit close and test-only validity configuration.

The sink package exposes concrete metrics output plugins. `FileSink`, `GraphiteSink`, `RollingFileSystemSink`, and `StatsDSink` implement `MetricsSink` and close/flush behavior where appropriate. `RollingFileSystemSink` has the richest public state and behavior: source name, error policy, append policy, base path, roll interval, random roll offset interval, next-flush calendar, static test hooks for force flushing and supplied configuration/filesystem, constructors including a testing constructor, roll-interval parsing, initial and subsequent flush-time scheduling, metric writing, flushing, and close. `StatsDSink` writes metrics lines to a StatsD daemon and exposes `writeMetric` for individual line emission.

`metrics2.util.MBeans` registers/unregisters Hadoop-standard JMX object names, optionally with extra properties, and can extract `service` and `name` components from `ObjectName`. `MetricsCache` keeps latest record state for sinks that cannot consume sparse updates, optionally caching tag values for later lookup and limiting record count per name. `Servers.parse` turns space/comma separated host or host:port specs into socket addresses, defaulting null input to localhost plus the caller-supplied port.

The chunk ends after the constructors and start of `getConf` for `org.apache.hadoop.net.AbstractDNSToSwitchMapping`, an abstract `DNSToSwitchMapping` and `Configurable` base. The visible constructors support unconfigured construction and construction with a cached `Configuration`; the constructor doc explicitly says it does not call `setConf`, so subclasses that derive state in `setConf` must call it themselves.

## Control flow and behavior

Writable comparison follows a two-tier path. If a class has an optimized comparator registered in `WritableComparator.define`, callers can compare serialized bytes directly with `compare(byte[], int, int, byte[], int, int)`. Otherwise, the default path constructs two key instances, deserializes with `Writable.readFields`, and compares via natural ordering. The byte helper methods support raw comparator implementations that parse primitive fields or VInts without constructing objects.

Writable factory lookup is registry-driven. Callers ask `WritableFactories.newInstance` for a class, the registry returns a configured factory when one exists, and reflection/fallback creation is implied for ordinary public writables. This supports deserialization paths where the encoded type is known but the constructor is not public.

Compression control flow is stream and state-machine based. A codec creates a stream around an existing input/output stream and either obtains a fresh or pooled `Compressor`/`Decompressor`. Compression callers repeatedly set input, check `needsInput`, call `compress`, call `finish`, and observe `finished`; decompression callers set input or let `DecompressorStream` refill compressed data, then call `decompress` until output is produced, EOF is reached, or a dictionary is required. `resetState` makes a stream reusable for a new compressed member, while `end` releases native or external resources owned by a codec engine.

Codec discovery and file matching flow through `CompressionCodecFactory`: construction reads configured codec classes and discovered implementations, builds extension/name/class maps, then `getCodec(Path)` selects by filename suffix. Name-based lookups support canonical class names, simple names, and configured aliases. Splittable readers call the `SplittableCompressionCodec` overload with start/end offsets and read mode, after which `SplitCompressionInputStream` may adjust the effective range.

Metrics control flow has source, builder, collector, and sink stages. A `MetricsSource.getMetrics` call receives a `MetricsCollector`; the source adds records and uses `MetricsRecordBuilder` to add tags, context, counters, and gauges. Mutable metrics snapshot into the builder, optionally only when `changed`. A `MetricsSystem` registers sources and sinks, can publish immediately, and shuts down at process stop. Sinks consume immutable `MetricsRecord` instances through `putMetrics` and eventually `flush` or `close`.

Mutable rate/stat control flow accumulates samples in source-side objects, then emits a snapshot. `MutableStat` tracks sample count/sum and optional extended statistics; `MutableQuantiles` maintains an online estimator and periodically rolls previous snapshots; `MutableRollingAverages` gathers thread-local state before snapshotting. Aggregated rates initialize from protocol methods or explicit names, creating per-method metrics lazily or during initialization.

Rolling file sink behavior is time-window based. Initialization reads base path, source, append/error settings, roll interval, random offset, security keytab/principal keys, and filesystem configuration. `setInitialFlushTime` computes an initial roll point with random offset; `updateFlushTime` advances by whole intervals while preserving that offset. `putMetrics` writes records under a GMT interval directory to a host/source-specific log file, using append when allowed and supported or sequence-suffixed files when append is disabled or unavailable.

## State and persistence behavior

Writable and TFile utilities define persistent wire formats: compressed byte arrays/strings, VInt/VLong encodings, enum names, string arrays, TFile key strings, and raw comparator byte ranges. Any change to these encodings would affect RPC compatibility, sequence/TFile data, and persisted metadata readers. `WritableComparator`'s comparator registry and `WritableFactories`' factory registry are process-global mutable state; registered entries affect all subsequent deserialization/comparison paths in the JVM.

Compression streams persist data to the wrapped output stream in codec-specific format and read it from the wrapped input stream. Codec engine objects are stateful and often native-resource backed; `reset`, `reinit`, `finish`, `finished`, and `end` determine whether pooled instances can safely be reused. `CodecPool` itself is global mutable process state that tracks leased compressor/decompressor objects.

`ECSchema` is a serializable-style value object for erasure-code policy metadata, but this XML range only exposes ordinary constructor/getter/equality APIs. Its option keys and equality/hash behavior are important because schemas may be used in policy maps, configuration, logs, and RPC payloads.

Metrics framework state is split between immutable published records and mutable source registries. `MetricsRegistry` owns tags and mutable metrics for a source; each mutable metric tracks a changed flag or accumulated statistics until snapshot. `DefaultMetricsSystem` is a singleton lifecycle manager and mini-cluster mode flag holder. `MBeans` registers external JVM MBean state under Hadoop's standard object-name convention.

Sink persistence depends on destination. `FileSink` writes to a local file or stream; `GraphiteSink` writes over a network connection to Graphite; `StatsDSink` emits StatsD line protocol to a daemon; and `RollingFileSystemSink` writes durable metrics logs through Hadoop `FileSystem`, commonly HDFS. Rolling file sink fields such as `basePath`, `nextFlush`, `allowAppend`, `ignoreError`, and static supplied test hooks directly shape where records are stored, when files roll, and whether write failures propagate.

`MetricsCache` is an in-memory state store for sink-side reconstruction of full records from sparse updates. `Servers.parse` is stateless. `AbstractDNSToSwitchMapping` stores a `Configuration` reference in subclasses/base state, but the visible constructor notes it does not invoke subclass configuration logic automatically.

## Dependencies and integration points

This chunk depends on Hadoop core interfaces including `Configuration`, `Configurable`, `Writable`, `WritableComparable`, `RawComparator`, `Path`, `IOStatistics`, metrics interfaces, and `FileSystem`. It also uses Java platform types such as `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `ByteBuffer`, `Class`, `Map`, `Collection`, `Calendar`, `Date`, `Closeable`, `ObjectName`, and socket address parsing.

Compression APIs integrate with codec implementations for zlib/default, gzip, bzip2, passthrough, lz4, snappy, and zstandard. The XML exposes suffix constants for several codecs even when their implementation classes are outside this range. `CompressionCodecFactory` integrates with configuration key `io.compression.codecs` and Java service discovery. `CodecPool` integrates with all codecs that expose reusable compressor/decompressor objects.

TFile integrates with raw byte comparators, Hadoop `Text`-compatible string encoding, and compression algorithm names. Serializer bindings integrate with Java `Serializable`, Hadoop `Writable`, and Avro reflect/specific classes, with configuration keys controlling Avro schema and reflect package acceptance.

Metrics APIs integrate with Hadoop daemons and libraries that expose sources through annotations, mutable registries, or direct `MetricsSource` implementations. Sinks integrate with Apache Commons Configuration `SubsetConfiguration`, Log4J appenders, JMX/MBeanServer, Graphite, StatsD, local files, and Hadoop `FileSystem` targets such as HDFS, local FS, S3-compatible filesystems, or any configured filesystem. `RollingFileSystemSink` additionally integrates with Kerberos by reading configured keytab/principal keys and with filesystem append semantics.

The partial net package entry integrates with `DNSToSwitchMapping`, which is the rack-resolution interface used by HDFS, YARN, and cluster placement logic, though the full mapping API lies outside this chunk.

## Risks and edge cases

- Raw comparator correctness is high risk. A custom `WritableComparator.compare(byte[], ...)` must match object-level `compareTo` exactly, handle VInt/VLong offsets correctly, and be thread-safe if registered globally.
- `WritableComparator` fallback comparison deserializes two key objects, which can be expensive in sort-heavy code and can fail if factories or constructors are unavailable.
- `WritableFactories` and comparator registration are global mutable state, so tests and plugins can leak behavior across unrelated code in the same JVM.
- VInt/VLong boundaries, negative encodings, encoded-size calculation, and `readVIntInRange` bounds are compatibility-critical. Off-by-one errors can corrupt data or allow oversized allocations.
- Compression objects are stateful. Returning a compressor/decompressor to `CodecPool` without reset/reinit discipline, continuing to use a returned object, or missing `end` on non-pooled objects can cause data corruption or native-resource leaks.
- `CompressionInputStream.seek` and `seekToNewSource` are documented as unsupported in the base class; callers must not assume arbitrary compressed streams are seekable unless using a split-aware codec contract.
- Splittable compression changes effective start/end offsets after stream creation. Record readers must use `getAdjustedStart` and `getAdjustedEnd` rather than the originally requested byte range.
- `PassthroughCodec` intentionally does not transform data, so code that treats every codec as reducing or validating compressed format may mis-handle it.
- `CodecPool` leased-count APIs are useful for detecting leaks; nonzero counts after jobs/tests indicate compressors or decompressors were not returned.
- `ECSchema` equality and option maps can be sensitive to missing required keys, extra options, and map mutability. Callers should avoid mutating option maps after construction unless implementation defensively copies them.
- TFile comparator names and compression labels are stringly typed. Unsupported algorithms, missing Java comparator classes, or inconsistent raw comparator ordering can make files unreadable or incorrectly sorted.
- Java serialization is fragile across class evolution and should not be assumed compatible with Writable/Avro serializers. Avro reflect package configuration and schema keys control which classes are accepted.
- Metrics builder APIs are fluent but order-sensitive for record construction. Missing `endRecord`, wrong context tags, duplicate metric names, or forgotten `changed` flags can produce incomplete or stale metrics.
- Metrics filters can exclude by name, tag, tag collection, or whole record. Misconfigured glob/regex patterns may silently suppress operational data.
- RollingFileSystemSink's Javadoc warns that the documented `ignore-error` behavior is subtle: failures may be swallowed or propagated depending on configuration, so operators/tests must validate actual behavior for their setting.
- Rolling file append support varies by filesystem. When append is unavailable, concurrent daemons on one host rely on source names and sequence suffixes; when append is enabled on HDFS, insufficient datanodes can make appended data unreadable even after a successful append call.
- Rolling file directory names use GMT interval boundaries and randomized initial offsets. Tests should not rely on local timezone or exact roll time without controlling clocks/random offsets.
- StatsD and Graphite sinks depend on network availability and formatting conventions; metric names/tags containing unexpected punctuation can affect downstream parsing.
- `AbstractDNSToSwitchMapping(Configuration)` does not call `setConf`, so subclass constructors that assume `setConf` side effects may be partially initialized.

## Test signals

Useful tests for code using or changing this API surface should include:

- Comparator compatibility tests that compare raw-byte and object-level `WritableComparable` ordering over normal, empty, negative, and malformed inputs.
- Registry isolation tests for `WritableComparator.define` and `WritableFactories.setFactory`, including non-public writable construction and cleanup between tests.
- VInt/VLong golden-vector tests for boundary values around one-byte encodings, negative encodings, maximum/minimum int/long, encoded sizes, and range-check failures.
- WritableUtils tests for compressed byte arrays/strings, null or empty strings where supported, string arrays, enum round trips, `skipFully` EOF behavior, and clone compatibility.
- Codec stream tests for write/finish/close/reset lifecycle, dictionary handling, EOF behavior, byte counters, IOStatistics passthrough, and native-resource cleanup.
- CodecPool leak tests that lease and return compressors/decompressors and assert leased counts return to zero.
- CompressionCodecFactory tests for configured codecs, service-loaded codecs, default built-ins, suffix selection, class-name/simple-name lookup, alias lookup, and suffix removal.
- Splittable codec tests that create streams over nonzero start/end offsets and assert adjusted boundaries are used by record readers.
- ECSchema tests for construction from maps and explicit arguments, required key validation, extra option preservation, equality/hashCode stability, and log-friendly string output.
- TFile utility tests for VInt/VLong/string golden encodings, lower/upper-bound behavior with duplicates and edge positions, comparator creation from `memcmp` and Java-class names, and supported compression algorithm names.
- Serializer tests covering Java, Writable, Avro reflect, and Avro specific acceptance/rejection rules, schema configuration, and comparator behavior for serialized Java objects.
- EventCounter tests that append warning/error/fatal events and verify counted metrics without requiring a layout.
- Metrics source tests that register with `MetricsSystem`, build records with tags/context/counters/gauges, snapshot mutable metrics only when expected, and publish immediately to a test sink.
- Mutable metric tests for changed-flag lifecycle, counter monotonicity, gauge increment/decrement/set, `MutableStat` extended stats and min/max reset, rate aggregation, quantile estimator rolling, rolling-average thread-local collection, and `close` cleanup.
- Metrics filter tests for glob and regex acceptance across names, tags, tag sets, and full records.
- Sink tests for FileSink output formatting, Graphite connection failure behavior, StatsD line formatting and close behavior, and RollingFileSystemSink roll scheduling, sequence suffix selection, append/no-append modes, GMT directory naming, Kerberos key lookup, and failure propagation under both ignore-error settings.
- MBeans tests for object-name construction with and without extra properties, service/name extraction, duplicate registration handling, and unregister idempotence.
- MetricsCache tests for sparse update reconstruction, tag inclusion/exclusion behavior, lookup by name/tags, and max-record eviction behavior.
- Servers.parse tests for null input, comma/space combinations, default ports, explicit ports, IPv6 or invalid host specs where supported, and whitespace trimming.
- AbstractDNSToSwitchMapping subclass tests that verify configuration is cached but subclass-specific `setConf` logic is only run when explicitly invoked.

### subset-b-007209: lines 30893-37013

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml lines 30893-37013

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 3.3.3. It starts inside the tail of `org.apache.hadoop.net.AbstractDNSToSwitchMapping`, covers complete API metadata for the rest of `org.apache.hadoop.net`, the visible security, credential, authorization, HTTP security, token, delegation-token web, service, service-launcher, and selected utility classes, then ends inside `org.apache.hadoop.util.Shell.getQualifiedBinPath`.

The source is generated API metadata rather than implementation code. The research surface is the public/protected compatibility contract: packages, type names, inheritance, implemented interfaces, constructors, methods, parameters, checked exceptions, fields, static/final/abstract/synchronized flags, deprecation markers, and embedded Javadocs. Exact method bodies and internal algorithms must be validated against Java sources when implementation-level behavior matters.

## Purpose

The `org.apache.hadoop.net` slice defines host-to-network-topology mapping APIs and socket factories. These APIs let Hadoop resolve hostnames/IPs to rack paths, cache those mappings, configure script/table-based mappings, and create either standard or SOCKS-proxied sockets.

The security slice defines Hadoop's core identity and credential contracts. `Credentials` stores secret keys and tokens in memory and serializes them to token-storage files/streams. `UserGroupInformation` wraps JAAS `Subject` state and exposes login, keytab, ticket-cache, proxy-user, group, token, and `doAs` operations. `SecurityUtil`, group/ID mapping interfaces, ACLs, impersonation providers, servlet security filters, and credential providers sit around that identity model.

The token slice defines server-side token password generation, client-side token serialization/renewal/cancelation, token identifiers, token renewer plugins, token selectors, and HTTP delegation-token operations. It connects Hadoop tokens to authentication-client URLs, Kerberos or pseudo HTTP authenticators, and JSON/HTTP parameter names.

The service and launcher slices define Hadoop's reusable lifecycle model. Services move through `NOTINITED`, `INITED`, `STARTED`, and `STOPPED`, record lifecycle events and first failures, notify listeners, support composite child services, expose blockers, and integrate with launcher exit-code conventions.

The utility tail covers classloading, duration/progress helpers, Java CRC32/CRC32C implementations, reflection utilities, and the start of `Shell`, including platform-specific command helpers and Hadoop-home/bin resolution.

## Important APIs, Types, and Functions

### Network APIs

- `DNSToSwitchMapping` defines `resolve(List)` plus `reloadCachedMappings()` overloads. Implementations must preserve one-to-one ordering between input hosts and returned network paths, and should fall back to `NetworkTopology.DEFAULT_RACK` when a name cannot be resolved.
- `AbstractDNSToSwitchMapping` provides `Configurable`-style `getConf`/`setConf`, `isSingleSwitch`, diagnostic `getSwitchMap`, `dumpTopology`, protected `isSingleSwitchByScriptPolicy`, and static `isMappingSingleSwitch(DNSToSwitchMapping)`. The Javadocs explicitly discourage extending `Configured` because its constructor can call subclass `setConf` before subclass construction completes.
- `CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping`, caches host-to-rack results, exposes a copied switch map, delegates single-switch detection to the raw mapping, and supports cache reloads for all or selected names.
- `ScriptBasedMapping` extends the cached mapper and reads configuration for a script named by `CommonConfigurationKeys.NET_TOPOLOGY_SCRIPT_FILE_NAME_KEY`. Its visible API includes constructors from default config, raw mapping, or `Configuration`, plus `getConf`, `setConf`, `toString`, and the `NO_SCRIPT` marker.
- `TableMapping` extends `CachedDNSToSwitchMapping` with `getConf`, `setConf`, and reload behavior for table-backed topology data.
- `ConnectTimeoutException` is a `SocketTimeoutException` thrown by `NetUtils.connect(...)`.
- `SocksSocketFactory` implements `Configurable` and `SocketFactory` creation overloads using a configured or supplied `Proxy`; it also defines `equals`, `hashCode`, `getConf`, and `setConf`.
- `StandardSocketFactory` provides the normal `SocketFactory` creation overloads plus equality/hash behavior.

### Security and Credentials

- `AccessControlException` extends `IOException` for access-control failures. `AuthorizationException` extends it and overrides stack-trace methods, which is a visible diagnostic behavior.
- `Credentials` implements `Writable` and manages token and secret-key maps keyed by `Text`. It exposes token add/get/list/map/count operations; secret-key add/get/remove/list/map/count operations; static `readTokenStorageFile(Path|File, Configuration)`; stream/file write methods with optional `Credentials.SerializedFormat`; `write`, `readFields`, `addAll`, and `mergeAll`. `addAll` overwrites existing entries, while `mergeAll` preserves them.
- `GroupMappingServiceProvider` supplies `getGroups`, `cacheGroupsRefresh`, and `cacheGroupsAdd`, with `GROUP_MAPPING_CONFIG_PREFIX` as the public configuration prefix.
- `IdMappingServiceProvider` maps user/group names to IDs and back, with strict `getUid`/`getGid` methods that throw `IOException` and allowing-unknown variants that return IDs without checked exceptions.
- `KerberosAuthException` stores structured context around failed Kerberos auth: user, principal, keytab file, ticket-cache file, initial message, and a formatted `getMessage`.
- `SecurityUtil` exposes static helpers for Kerberos principal substitution, login from keytab config, token-service construction, token annotations, `doAs` wrappers for login/current user, authentication-method get/set, privileged-port checks, and ZooKeeper auth info. Its public fields include `LOG`, `HOSTNAME_PATTERN`, and `FAILED_TO_GET_UGI_MSG_HEADER`.
- `UserGroupInformation` is the central identity API: static initialization/configuration, security-enabled checks, current/login/best UGI lookup, ticket-cache and keytab login, keytab relogin/logout, remote/proxy/test user creation, real-user access, user/group getters, token and credential mutation, auth-method mutation/lookup, `Subject` access, equality/hash, `doAs(PrivilegedAction|PrivilegedExceptionAction)`, debug logging, and a diagnostic `main`. It exposes token environment variable names `HADOOP_TOKEN_FILE_LOCATION` and `HADOOP_TOKEN`.
- `UserGroupInformation.AuthenticationMethod` bridges UGI auth methods to and from `SaslRpcServer.AuthMethod`.
- `CredentialProvider` is an abstract credential-store API with transient-store detection, `flush`, entry lookup, alias listing, create/delete operations, password-needed diagnostics, and `CLEAR_TEXT_FALLBACK`.
- `CredentialProviderFactory` creates providers and lists configured providers via the `CREDENTIAL_PROVIDER_PATH` setting.
- `AccessControlList` implements `Writable`, parses ACL strings, supports wildcard ACLs, adds/removes users/groups, checks `UserGroupInformation` membership, exposes ACL strings, and serializes/deserializes ACL state. Public constants include `WILDCARD_ACL_VALUE` and `USE_REAL_ACLS`.
- `DefaultImpersonationProvider` implements `ImpersonationProvider`, initializes from config, authorizes proxy users by remote address, exposes proxy-user/group/IP config-key builders, and returns proxy group/host maps. `ImpersonationProvider` also has an overload accepting a configured proxy-prefix.
- `RestCsrfPreventionFilter` and `XFrameOptionsFilter` implement servlet `Filter` and expose initialization, `doFilter`, destroy, filter-param extraction, and public header/config parameter constants.

### Token and Delegation Token APIs

- `SecretManager<T>` creates token passwords, retrieves passwords, has a retriable retrieval path, creates identifiers, checks read availability with `StandbyException`, generates `SecretKey` values, computes HMAC passwords, and converts byte arrays to secret keys.
- `Token<T extends TokenIdentifier>` implements `Writable` and can be constructed from an identifier and secret manager, raw identifier/password/kind/service components, or another token. It exposes mutable identifier/password/service state, `copyToken`, identifier decoding, private-clone checks, `readFields`/`write`, URL-safe encode/decode, equality/hash/string/cache-key behavior, and delegation-token `isManaged`, `renew`, and `cancel`.
- `Token.TrivialRenewer` extends `TokenRenewer` for token kinds that are not managed. Subclasses provide `getKind`; the renewer reports handling/managed state and no-op style renewal/cancel semantics through the renewer contract.
- `TokenIdentifier` is an abstract `Writable` with abstract `getKind` and `getUser`, concrete byte serialization through `getBytes`, and `getTrackingId` documented as an MD5 of identifier bytes.
- `TokenInfo` is an annotation type marker for token-related metadata.
- `TokenRenewer` is the plugin interface for token renewal and cancelation: `handleKind`, `isManaged`, `renew`, and `cancel`.
- `TokenSelector<T>` selects a token for a named service from a collection.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL`, chooses a default delegation-token authenticator, controls whether delegation tokens travel in URL query strings, opens authenticated HTTP connections with optional `doAs`, and gets/renews/cancels delegation tokens.
- `DelegationTokenAuthenticatedURL.Token` extends `AuthenticatedURL.Token` with a Hadoop delegation token getter/setter.
- `DelegationTokenAuthenticator` wraps a base `Authenticator`, supports a `ConnectionConfigurator`, authenticates connections, and implements HTTP delegation-token get/renew/cancel operations with optional `doAs`. Public fields define operation, header, query parameter, and JSON key names.
- `KerberosDelegationTokenAuthenticator` adds SPNEGO delegation-token support and falls back to pseudo authentication when the endpoint does not trigger SPNEGO. `PseudoDelegationTokenAuthenticator` uses Hadoop simple-auth style current-user trust.

### Service and Launcher APIs

- `Service` extends `Closeable` and defines lifecycle operations, listener registration, name/config/state/start-time access, failure cause/state, stop waiting, lifecycle-history snapshots, and blocker maps.
- `AbstractService` implements `Service`, stores service name/config/state/start time, records failure cause/state, invokes protected `serviceInit`, `serviceStart`, and `serviceStop` hooks, supports local/global listeners, implements final `close`, wait-for-stop, lifecycle history, state tests, blockers, and failure recording.
- `CompositeService` manages child `Service` instances, adds/removes child services, adds only if an object implements `Service`, returns cloned child lists, and overrides init/start/stop to propagate lifecycle operations. `STOP_ONLY_STARTED_SERVICES` defines shutdown policy.
- `LifecycleEvent` is serializable public state containing transition time and state. `LoggingStateChangeListener` logs service state changes.
- `ServiceOperations` provides static `stop` and `stopQuietly` overloads for cleanup, including commons-logging and SLF4J variants.
- `ServiceStateChangeListener` callbacks are invoked after state change while the initiating thread is still in a synchronized section; the Javadoc warns long-running callbacks and reentrant service calls can delay or deadlock transitions.
- `ServiceStateException` carries an exit code, converts throwables to runtime exceptions, and defaults to `EXIT_SERVICE_LIFECYCLE_EXCEPTION` when no inner exit code exists.
- `ServiceStateModel` encapsulates valid lifecycle state transitions through `enterState`, `checkStateTransition`, and `isValidStateTransition`.
- `LaunchableService` extends `Service` with `bindArgs(Configuration, List<String>)` and `execute()` for CLI-launched services. `AbstractLaunchableService` supplies default implementations on top of `AbstractService`.
- `HadoopUncaughtExceptionHandler` wraps optional downstream uncaught-exception handling.
- `LauncherExitCodes` publishes standardized process exit codes for success, failures, user shutdown, launch failure, interruption, argument errors, auth failures, HTTP-style conditions, bad configuration, thrown exceptions, unimplemented operations, service unavailable, unsupported version, service creation failure, and lifecycle exceptions.
- `ServiceLaunchException` extends `ExitUtil.ExitException`, implements both `ExitCodeProvider` and `LauncherExitCodes`, and provides formatted-message constructors.

### Utility APIs

- `ApplicationClassLoader` extends `URLClassLoader`, supports classpath-string and URL-array constructors, overrides resource/class loading, and exposes `isSystemClass` plus `SYSTEM_CLASSES_DEFAULT`.
- `DurationInfo` extends `OperationDuration` and implements `AutoCloseable`; it logs/records operation duration and has close/toString behavior.
- `IPList` defines `isIn(String)` membership checks. `Progressable` defines a single `progress()` callback.
- `OperationDuration` tracks elapsed time with `time`, `finished`, `getDurationString`, static `humanTime`, `toString`, numeric `value`, and `asDuration`.
- `PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum` with constructors, `getValue`, `reset`, byte-array update, and final single-byte update. The CRC32C Javadoc calls out the iSCSI polynomial and SSE4.2 hardware compatibility.
- `ReflectionUtils` provides static configuration injection, reflective instantiation, contention tracing, thread-stack printing/logging for commons-logging and SLF4J, correctly typed class lookup, Writable copy/clone helpers, and inherited declared field/method discovery.
- `Shell` starts in this chunk with protected constructors, Java-version helpers, command builders for groups, netgroups, permissions, ownership, symlinks, readlinks, process liveness, signals, environment-variable regex, script extension/run command helpers, Hadoop-home discovery, and qualified Hadoop bin lookup. The chunk ends before the full `getQualifiedBinPath` method and later `Shell` APIs/fields are visible.

## Control Flow

The XML itself has no executable runtime flow, but the APIs imply several important paths:

- Rack resolution flows from callers through `DNSToSwitchMapping.resolve(List)`. Cached wrappers resolve misses through a raw mapping, return cached locations for known hosts, and clear all or selected cache entries on reload. Script/table mappings derive raw data from configuration and external mapping sources.
- Socket creation flows through `SocketFactory` overloads. Standard sockets delegate to normal Java socket construction, while SOCKS sockets route through configured proxy state.
- Credential persistence flows from in-memory token/secret maps to `Writable` streams or token-storage files, and back through `readFields`/`readTokenStorage*`. Merging either overwrites (`addAll`) or preserves (`mergeAll`) existing aliases.
- UGI setup flows from static configuration into login/current user lookup, then into Kerberos keytab, ticket-cache, remote, proxy, or testing user creation. Privileged execution flows through `doAs`, where actions run under the wrapped JAAS `Subject` and exceptions are surfaced according to `PrivilegedAction` or `PrivilegedExceptionAction`.
- Security utility flow performs principal host substitution, logins based on configuration keys, token-service address construction, annotation lookups, and authenticated `doAs` helpers.
- ACL and impersonation authorization flow parses configured users/groups/hosts, maps real and effective users, and rejects unauthorized proxy access by throwing authorization/access-control exceptions.
- Servlet filters initialize from filter parameters, inspect requests/responses in `doFilter`, and enforce CSRF or frame-option policy through configured headers/method/user-agent handling.
- Token creation flows from a `TokenIdentifier` to a `SecretManager` password. Client-side tokens can be serialized, URL-encoded, decoded, renewed, and canceled through token renewer plugins or delegation-token HTTP endpoints.
- HTTP delegation-token flow opens authenticated connections, optionally sends delegation tokens by query parameter or header, applies optional `doAs`, and issues get/renew/cancel operations. Kerberos and pseudo authenticators provide different upstream authentication mechanisms behind the same delegation-token wrapper.
- Service lifecycle flow is `NOTINITED -> INITED -> STARTED -> STOPPED`. `AbstractService.init/start/stop` invoke subclass hooks, record lifecycle events, notify listeners, record first failures, and force stop on failed init/start. `CompositeService` applies the same lifecycle to child services.
- Launcher flow binds command-line arguments into a `Configuration`, executes a launchable service, and converts service or launch failures into standardized exit codes.
- Utility flow includes reflective construction plus optional `Configurable` injection, Writable copy through serialization buffers, operation duration measurement, checksum incremental updates, and platform command-vector construction.

## State and Persistence Behavior

This JDiff XML persists API metadata for release compatibility checks. It does not itself persist Hadoop runtime state.

Runtime state exposed by these APIs includes DNS/rack caches, raw mapping delegates, socket proxy configuration, credential maps, secret-key byte arrays, token identifiers/passwords/kinds/services, UGI subjects, authentication methods, token and group memberships, service lifecycle states, lifecycle history, failure cause/state, blockers, listeners, child service lists, launch exit codes, operation timers, checksum accumulators, and platform command discovery.

Durable persistence is most explicit in security/token APIs. `Credentials`, `AccessControlList`, `Token`, and `TokenIdentifier` use Hadoop `Writable`-style `write`/`readFields` contracts; `Credentials` also persists to token-storage streams and files using selectable serialized formats. `Token.encodeToUrlString` and `decodeFromUrlString` define a text transport form for HTTP/query/header propagation.

Credential-provider state may be transient or durable depending on provider implementation. `CredentialProvider.flush()` is the visible commit hook for providers that buffer updates.

UGI and token state is mostly in-memory per process, but it can be initialized from keytabs, ticket caches, token cache files, and base64 token environment variables. Relogin methods mutate the login user's Kerberos credential state. Proxy users retain both effective and real user identity.

Service state is in-memory, with `LifecycleEvent` serializable as a public data holder. Lifecycle history is documented as a snapshot, not a durable audit log. Global service listeners are JVM-wide state and can observe all service transitions.

Utility persistence is limited. CRC objects maintain running checksum values. `OperationDuration` records timing state. `ApplicationClassLoader` holds classpath/system-class policy in memory. `Shell` helpers derive process-local platform command paths such as Hadoop home and qualified bin locations.

## Dependencies and Integration Points

The chunk integrates heavily with Java core APIs: collections, `IOException`, `File`, `FileNotFoundException`, `Socket`, `SocketAddress`, `InetAddress`, `Proxy`, `SocketFactory`, servlet `Filter`, JAAS `Subject`, privileged action APIs, `SecretKey`, `DataInput`/`DataOutput`, `DataInputStream`/`DataOutputStream`, `Closeable`, `URL`, `HttpURLConnection`, `URLClassLoader`, `Checksum`, `Duration`, and logging interfaces.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configurable` across network mappings, socket factories, UGI, credential providers, impersonation, services, launchable services, tokens, and reflection utilities.
- `org.apache.hadoop.io.Text` and `Writable` for credentials, tokens, ACLs, and token identifiers.
- `org.apache.hadoop.fs.Path` for token-storage file access.
- `NetworkTopology`, `NetUtils`, and `CommonConfigurationKeys` for rack mapping and connection behavior.
- `SaslRpcServer.AuthMethod`, `KerberosInfo`, `TokenInfo`, `Groups`, and token/UGI classes for Hadoop authentication and authorization.
- Hadoop authentication-client APIs: `AuthenticatedURL`, `AuthenticatedURL.Token`, `Authenticator`, `ConnectionConfigurator`, and `AuthenticationException`.
- `ExitUtil.ExitException`, `ExitCodeProvider`, and `LauncherExitCodes` for service launch failure propagation.
- SLF4J and commons-logging for diagnostics in security, service operations, reflection, and duration utilities.
- External OS/process integration through `Shell` command helpers, Hadoop home/bin lookup, group/netgroup commands, signal commands, script interpreter choice, and Windows command-line constraints.

## Risks and Edge Cases

- The range begins mid-class in `AbstractDNSToSwitchMapping` and ends mid-method/Javadoc in `Shell.getQualifiedBinPath`; adjacent chunks are required for complete class-level analysis of both boundaries.
- JDiff omits private implementation fields and method bodies. Cache concurrency, token byte-copy defensiveness, exact error text, classloader order, shell quoting, and servlet filter behavior need source-code confirmation.
- The `AbstractDNSToSwitchMapping.isMappingSingleSwitch` Javadoc says it assumes mappings not derived from the base class are multi-switch but also states the return as "or the mapping is not derived"; this ambiguity should be checked in implementation before relying on fallback semantics.
- Rack mappings must preserve input/output list cardinality and order. A script/table/raw mapper that returns fewer, more, or misordered paths can corrupt block-placement and locality policy.
- `Credentials` and `Token` expose byte-array based secrets. If implementations return mutable arrays directly, callers can accidentally or maliciously mutate credential state; source/tests should verify copy behavior.
- `Credentials.addAll` overwrites while `mergeAll` does not. Calling the wrong merge path can silently replace delegation tokens or keep stale credentials.
- `KerberosAuthException` and UGI logging can include principal, user, keytab, ticket-cache, and token context. Diagnostics must avoid leaking secrets while retaining enough context to debug auth failures.
- UGI static configuration and login-user state are JVM-wide. Tests and long-running daemons must avoid cross-test contamination and must handle relogin race conditions.
- Proxy-user authorization depends on both groups and remote address. Misconfigured `DefaultImpersonationProvider` keys or proxy prefixes can either block legitimate workloads or allow excessive impersonation.
- `AuthorizationException` suppresses or overrides stack trace behavior, so diagnostics may be intentionally sparse.
- CSRF and X-Frame filters depend on exact header names, user-agent classification, and ignored-method configuration; overly broad ignore settings can weaken HTTP endpoints.
- Token renewal/cancelation crosses process and network boundaries and throws both `IOException` and `InterruptedException` or authentication exceptions. Callers must preserve interruption and avoid losing renewed expiration times.
- `TokenIdentifier.getTrackingId` is documented as MD5 of serialized bytes. It is useful for correlation, not cryptographic security.
- Delegation tokens can be transmitted in query strings when configured. That increases leakage risk through logs, browser history, referrers, and intermediaries compared with headers.
- `ServiceStateChangeListener` runs on the initiating state-change thread while the service is synchronized. Listener callbacks that block or re-enter service methods can delay state transitions or deadlock.
- `ServiceOperations.stop` is documented as not thread safe because it checks state before operation. Concurrent lifecycle calls can race.
- `CompositeService.STOP_ONLY_STARTED_SERVICES` affects cleanup of partially initialized children. Child services must tolerate `stop()` after failed init/start as documented.
- `ServiceStateException.convert` wraps non-runtime throwables and maps exit codes. Incorrect conversion can hide original checked exception types from callers.
- `ApplicationClassLoader` class/resource resolution order can affect dependency isolation and shading. `isSystemClass` patterns need compatibility tests.
- `ReflectionUtils.newInstance` can call `setConf`; constructors and configurable setters must be side-effect safe.
- Pure Java CRC implementations must match standard CRC32/CRC32C vectors exactly; performance changes must not alter incremental update semantics.
- `Shell` helpers are platform-sensitive. Hadoop-home/bin lookup checks file existence, so callers are expected to cache results and handle missing `HADOOP_HOME` or missing binaries.

## Test Signals

Useful validation for this API surface should include:

- JDiff/API compatibility checks ensuring all listed public/protected types, methods, fields, exceptions, synchronization/final/static flags, and deprecation statuses remain stable for Hadoop Common 3.3.3.
- DNS mapping tests for one-to-one resolve results, default-rack fallback, cached hits/misses, selected and full cache reloads, diagnostic map copying, single-switch predicates, script/table configuration, and constructor/setConf ordering.
- Socket factory tests for standard and SOCKS socket creation overloads, proxy configuration loading, local bind variants, equality/hash behavior, and connection timeout exception propagation through `NetUtils.connect`.
- Credential tests for token/secret add/get/remove/list/map/count behavior, immutability of returned maps, byte-array copy behavior, `addAll` overwrite semantics, `mergeAll` preservation semantics, token-storage stream/file round trips, and serialized-format compatibility.
- Group and ID mapping tests for unknown-user behavior, refresh/add cache hooks, name/ID round trips, and allowing-unknown fallbacks.
- Kerberos/UGI tests for static initialization, security-enabled transitions, current/login/best user selection, keytab and ticket-cache login/relogin/logout, proxy and remote user creation, real/effective user identity, short-name parsing, primary group lookup, token/credential propagation, auth-method mapping, `doAs` exception propagation, and token environment variable loading.
- SecurityUtil tests for hostname principal replacement, server principal overloads, keytab login config keys, token-service address building, token/kerberos annotation lookup, privileged-port checks, and ZooKeeper auth info parsing.
- CredentialProvider tests for transient vs durable providers, alias listing, create/delete, password-needed warning/error strings, flush persistence, clear-text fallback policy, and factory provider-path parsing.
- ACL and impersonation tests for wildcard ACLs, user/group add/remove, serialization, real ACL group checks, remote-address restrictions, proxy config-key generation, and rejection diagnostics.
- Servlet filter tests for CSRF header requirements, browser user-agent detection, ignored-method configuration, X-Frame header defaults/overrides, filter-param extraction, and servlet chain continuation/blocking behavior.
- SecretManager and Token tests for HMAC password generation, standby read checks, identifier serialization/decoding failures, private clones, URL-safe encode/decode, equality/hash/cache key stability, renewer discovery, managed-token renew/cancel behavior, and interruption handling.
- Delegation-token web tests for default authenticator selection, connection configurator use, header vs query-string token transport, `doAs` variants, HTTP JSON parsing keys, get/renew/cancel success and failure paths, Kerberos fallback to pseudo auth, and unsupported URL schemes.
- Service lifecycle tests for legal and illegal state transitions, null configuration rejection, hook single-invocation guarantees, failed init/start triggering stop, first-failure recording, wait-for-stop timeouts, listener registration/unregistration and deadlock-sensitive callbacks, blocker maps, global listeners, and close relaying to stop.
- Composite service tests for child ordering during init/start/stop, partial failure cleanup, `addIfService`, cloned child-list behavior, removal, and `STOP_ONLY_STARTED_SERVICES` policy.
- Launcher tests for `bindArgs`, `execute`, uncaught exception handling, formatted `ServiceLaunchException` messages, exit-code constants, and exit-code propagation through `ServiceStateException`.
- Utility tests for application classloader system-class matching, resource/class loading order, duration string formatting and close behavior, IP-list membership, progress callbacks, CRC32 and CRC32C standard vectors with segmented updates, reflection configuration injection and Writable copy/clone, inherited field/method discovery, and Shell command-vector generation across Unix/Windows assumptions.

## Cross-Chunk Notes

The previous chunk is required to complete `org.apache.hadoop.net.AbstractDNSToSwitchMapping`, including its class declaration and earlier constructors. This chunk contains the full classes from `CachedDNSToSwitchMapping` through `ReflectionUtils`, then starts `Shell`. The next chunk is required to complete `Shell.getQualifiedBinPath` and the remaining `Shell` API surface.

### subset-b-007210: lines 37014-39037

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml lines 37014-39037

## Scope

This chunk is the final segment of the Hadoop Common 3.3.3 JDiff API snapshot. It begins in the middle of `org.apache.hadoop.util.Shell`, then covers public API entries for shutdown hooks, string interning, system information, Hadoop `Tool` execution, build version metadata, Bloom filter implementations, and the first functional async/iterator helpers. The source is an API-description XML, so the chunk records public/protected signatures, fields, documentation, deprecation status, thrown exceptions, package/class boundaries, and selected type relationships rather than method bodies.

## Purpose

The APIs in this chunk are general support infrastructure used across Hadoop Common and downstream modules:

- `Shell` abstracts platform-specific process execution, command construction, Windows `winutils.exe` discovery, timeout handling, and process cleanup.
- `ShutdownHookManager` centralizes JVM shutdown hook ordering and timeout enforcement.
- `StringInterner`, `SysInfo`, `Tool`, `ToolRunner`, and `VersionInfo` provide common CLI, metadata, resource-reporting, and memory-optimization utilities.
- `org.apache.hadoop.util.bloom` provides serializable Bloom filter variants used by Hadoop IO components such as Bloom map files and by modules that need probabilistic membership tests.
- `FutureIO` and `RemoteIterators` in `org.apache.hadoop.util.functional` adapt Java futures and Hadoop `RemoteIterator` APIs to IOException-aware functional workflows.

## Important APIs and Types

### `org.apache.hadoop.util.Shell`

The chunk includes the lower portion of `Shell`:

- Windows binary discovery and validation: `hasWinutilsPath()`, `getWinUtilsPath()`, `getWinUtilsFile()`, public deprecated `WINUTILS`, and Hadoop home constants `SYSPROP_HADOOP_HOME_DIR` and `ENV_HADOOP_HOME`.
- Bash/process support: `checkIsBashSupported()`, `isSetsidAvailable`, OS booleans (`WINDOWS`, `LINUX`, `MAC`, `SOLARIS`, `FREEBSD`, `OTHER`, `PPC_64`), `osType`, and command constants such as `SET_PERMISSION_COMMAND`, `SET_OWNER_COMMAND`, `SET_GROUP_COMMAND`, `LINK_COMMAND`, `READ_LINK_COMMAND`, and `TOKEN_SEPARATOR_REGEX`.
- Execution lifecycle for subclasses: protected `setEnvironment(Map)`, `setWorkingDirectory(File)`, `run()`, abstract `getExecString()`, and abstract `parseExecResult(BufferedReader)`.
- Runtime inspection and cleanup: `getEnvironment(String)`, `getProcess()`, `getExitCode()`, `getWaitingThread()`, `isTimedOut()`, `destroyAllShellProcesses()`, and `getAllShells()`.
- Convenience execution: overloaded static `execCommand(...)` variants with optional environment and timeout.
- Platform-specific safety: `WindowsProcessLaunchLock`, `WINDOWS_MAX_SHELL_LENGTH`, deprecated misspelled `WINDOWS_MAX_SHELL_LENGHT`, and `getMemlockLimit(Long)`.

The implementation behind these declarations keeps a process-wide weak set of active `Shell` instances, starts `ProcessBuilder` commands, drains stdout/stderr in separate flows, destroys timed-out processes through a `TimerTask`, and converts nonzero exits into `ExitCodeException` from the nested class declared earlier in the XML.

### `ShutdownHookManager`

`ShutdownHookManager` is a final singleton. Its visible API in this chunk:

- `get()` returns the singleton.
- `addShutdownHook(Runnable, int)` and `addShutdownHook(Runnable, int, long, TimeUnit)` register hooks with priority and optional timeout.
- `removeShutdownHook(Runnable)`, `hasShutdownHook(Runnable)`, `isShutdownInProgress()`, and `clearShutdownHooks()` manage registrations and state.
- `TIMEOUT_MINIMUM` and `TIME_UNIT_DEFAULT` define timeout defaults.

Hook identity is based on the runnable instance. Hooks with higher priority execute first; same-priority ordering is explicitly non-deterministic.

### `StringInterner`

`StringInterner` exposes static helpers:

- `strongIntern(String)` uses a strong Guava interner and retains interned values.
- `weakIntern(String)` delegates to Java string interning and does not add a Hadoop-owned strong reference.
- `internStringsInArray(String[])` mutates an array in place by weak-interning all entries.

Null string inputs return null for individual intern operations.

### `SysInfo`

`SysInfo` is an abstract resource information plugin:

- `newInstance()` chooses an OS-specific implementation, Linux or Windows in the backing code.
- Abstract getters expose total/available virtual and physical memory, processor/core counts, CPU frequency, cumulative CPU time, CPU utilization, vcores used, network bytes read/written, and storage bytes read/written.

Unsupported OS detection raises `UnsupportedOperationException`.

### `Tool` and `ToolRunner`

`Tool` extends Hadoop `Configurable` and defines `int run(String[] args) throws Exception`. It is the stable CLI application contract used by MapReduce and file-system tools.

`ToolRunner` runs a `Tool` after generic Hadoop option parsing:

- `run(Configuration, Tool, String[])` installs/updates the tool configuration through `GenericOptionsParser`, sets CLI caller/audit context in the backing implementation, and invokes `Tool.run()` with remaining arguments.
- `run(Tool, String[])` delegates to the tool's current configuration.
- `printGenericCommandUsage(PrintStream)` delegates generic option help.
- `confirmPrompt(String)` loops on `System.in` until `y/yes` or `n/no`.

### `VersionInfo`

`VersionInfo` reads component version properties and exposes common build metadata:

- Protected constructor and `_getVersion`, `_getRevision`, `_getBranch`, `_getDate`, `_getUser`, `_getUrl`, `_getSrcChecksum`, `_getBuildVersion`, `_getProtocVersion`.
- Static common accessors `getVersion`, `getRevision`, `getBranch`, `getDate`, `getUser`, `getUrl`, `getSrcChecksum`, `getBuildVersion`, `getProtocVersion`.
- `main(String[])` prints human-readable Hadoop build metadata.

The backing class also has a `getCompilePlatform()` API outside this exact JDiff chunk.

### `org.apache.hadoop.util.bloom`

The chunk covers the public Bloom-filter surface:

- `BloomFilter` extends `Filter`; it supports `add`, `membershipTest`, `and`, `or`, `xor`, `not`, `toString`, `getVectorSize`, `write`, and `readFields`.
- `CountingBloomFilter` extends `Filter`; it supports `add`, `delete`, `membershipTest`, `approximateCount`, `and`, `or`, `toString`, `write`, and `readFields`; `not` and `xor` are declared but unsupported by implementation.
- `DynamicBloomFilter` extends `Filter`; it adds new internal Bloom-filter rows when the current row reaches its configured record threshold and supports logical operations, string rendering, and Writable serialization.
- `HashFunction` turns a `Key` into `nbHash` vector positions using a selected `org.apache.hadoop.util.hash.Hash` implementation.
- `RemoveScheme` defines retouched Bloom clearing constants: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` extends `BloomFilter` and implements `RemoveScheme`; it tracks false-positive and true-key vectors, accepts false-positive observations, performs `selectiveClearing(Key, short)`, and serializes its extra vectors and ratios.

All Bloom classes are serializable through Hadoop `Writable` methods and depend on `Key`, `Filter`, and hash implementations in `org.apache.hadoop.util.hash`.

### `org.apache.hadoop.util.functional.FutureIO`

Visible APIs in this chunk:

- `awaitFuture(Future<T>)` and `awaitFuture(Future<T>, long, TimeUnit)` block for results while converting `InterruptedException` to `InterruptedIOException`, unwrapping nested execution failures, preserving runtime exceptions, and exposing timeout/cancellation separately.
- `raiseInnerCause(ExecutionException)` and `raiseInnerCause(CompletionException)` rethrow the meaningful nested cause.
- `unwrapInnerException(Throwable)` recursively unwraps `IOException`, `UncheckedIOException`, `ExecutionException`, and `CompletionException`, throws nested runtime/errors, or wraps unknown causes in `IOException`.

The backing file also includes additional APIs after this JDiff-visible set, such as option propagation and `CompletableFuture` evaluation helpers.

### `org.apache.hadoop.util.functional.RemoteIterators`

Visible APIs in this chunk adapt `RemoteIterator<T>`:

- Constructors from singleton, Java `Iterator`, `Iterable`, or array.
- Wrappers for mapping, type casting, filtering, and combined close behavior.
- Conversions to `List` or array.
- `foreach(RemoteIterator, ConsumerRaisingIOE)` applies an IOException-aware consumer and returns the processed count.
- `cleanupRemoteIterator(RemoteIterator)` logs `IOStatistics` at debug and closes closeable iterators.

Backing implementations preserve `IOStatisticsSource` where possible and close wrapped iterators when exhausted or on cleanup.

## Control Flow

`Shell.run()` is interval-gated: if the last execution is too recent, it returns without launching. Otherwise it constructs the command from `getExecString()`, applies the configured environment and working directory, launches through `ProcessBuilder`, starts timeout handling if configured, drains stderr concurrently, lets `parseExecResult()` process stdout, waits for the process, records the exit code, and tears down streams/process references in `finally`. Static `execCommand()` uses a `ShellCommandExecutor` wrapper for simple commands.

`ShutdownHookManager` registers one JVM hook at class initialization. During JVM shutdown, it flips an atomic shutdown flag, sorts registered hooks by descending priority, submits each hook to a single-thread executor, waits for the hook-specific timeout, cancels timed-out hooks, logs failures, then shuts down the executor with a configured timeout.

`ToolRunner.run()` normalizes the configuration, parses generic Hadoop command-line options, sets the mutated configuration back onto the `Tool`, and calls the tool with only remaining application arguments.

Bloom filter control flow is hash-first: each added or queried `Key` is converted to one or more vector positions by `HashFunction.hash(Key)`. Standard Bloom operations mutate `BitSet` state; counting filters mutate 4-bit counters packed into `long[]`; dynamic filters route inserts to the active row or append a new row; retouched filters choose a bit-clearing index using the selected removal scheme and update the true-key/false-positive tracking vectors.

`FutureIO.awaitFuture()` is a blocking boundary around asynchronous code: it calls `Future.get`, translates interruption, preserves cancellation, and unwraps asynchronous failure wrappers to match Hadoop's IOException-centric APIs.

`RemoteIterators` builds lazy wrapper chains. Filtering can advance the source in `hasNext()`; mapping applies during `next()`. `foreach()` guarantees cleanup in a `finally` block but intentionally does not hide IOExceptions from the source or consumer.

## State and Persistence Behavior

- `Shell` maintains static OS detection state, cached Hadoop home/winutils resolution results, and a synchronized weak map of active shell instances. Per-instance state includes timeout interval, inherit-parent-env flag, environment map, working directory, current process, exit code, waiting thread, completed flag, and timed-out flag. Shell state is runtime-only, not persisted.
- `ShutdownHookManager` stores hook entries in a synchronized set and shutdown progress in an `AtomicBoolean`. It is process-global runtime state.
- `StringInterner` strong interning retains process-lifetime references; weak interning uses the JVM string pool.
- `VersionInfo` loads properties from classpath resources into a `Properties` object and exposes them as static common metadata. Missing keys resolve to `"Unknown"`.
- Bloom filters persist through `Writable.write/readFields`. `Filter` writes a negative version marker, hash count, hash type, and vector size while retaining compatibility with an older unversioned format. Subclasses append their bit vectors, packed counters, dynamic row arrays, or retouched tracking vectors.
- `FutureIO` and `RemoteIterators` are stateless utility classes, but iterator wrappers carry lazy cursor, cached next-value, close state, or underlying iterator references.

## Dependencies and Integration Points

- `Shell` integrates with the host OS, `ProcessBuilder`, Hadoop home layout, `winutils.exe`, shell tools such as `bash`/`setsid`, `Time.monotonicNow`, `SubjectInheritingThread`, SLF4J, and Windows process serialization.
- `ShutdownHookManager` depends on JVM shutdown hooks, Hadoop `Configuration`, `CommonConfigurationKeysPublic.SERVICE_SHUTDOWN_TIMEOUT`, `HadoopExecutors`, Guava `ThreadFactoryBuilder`, `SubjectInheritingThread`, and SLF4J.
- `ToolRunner` depends on `Configuration`, `GenericOptionsParser`, `CallerContext`, and `CommonAuditContext`; it is used broadly by Hadoop CLIs and tests.
- Bloom filters depend on `Writable`, `DataInput/DataOutput`, `Key`, `HashFunction`, and hash implementations. `BloomMapFile` tests and IO code are downstream integration signals.
- `FutureIO` integrates Java `Future`, `CompletableFuture`, `ExecutionException`, `CompletionException`, Hadoop filesystem builder APIs outside this chunk, and IOException-oriented contract tests.
- `RemoteIterators` integrates Hadoop `RemoteIterator`, `IOStatisticsSource`, `IOStatistics` logging/support, `Closeable`, and IOException-aware functional interfaces.

## Risks and Edge Cases

- `Shell` has strong platform coupling. Hadoop home/winutils are cached at class initialization, so environment/property changes after class load do not affect lookup. Process timeout uses `Process.destroy()` and a timer; subprocess trees or platform-specific process behavior may survive. `getWinUtilsPath()` throws `RuntimeException` on unresolved paths, whereas `getWinUtilsFile()` throws checked `FileNotFoundException`.
- `Shell.destroyAllShellProcesses()` iterates a global weak set and destroys current processes; callers must understand it is process-wide.
- Shutdown hooks with equal priority run in unspecified order; long-running hooks are cancelled but cancellation depends on interrupt responsiveness. Adding/removing hooks during shutdown raises `IllegalStateException`.
- Strong string interning can grow memory permanently for unbounded inputs.
- `SysInfo.newInstance()` only supports the OSes implemented by Hadoop; unsupported OSes fail at runtime.
- `ToolRunner.confirmPrompt()` blocks on standard input and writes prompts to stderr, making it unsuitable for noninteractive paths unless guarded.
- Bloom filters are mutable and not generally thread-safe. Counting filters saturate 4-bit counters at 15, so repeated insertions can distort `approximateCount()` and deletes. Dynamic filters require compatible matrix length and threshold for logical operations. Retouched Bloom filters intentionally trade selected false-positive removal for false negatives, and `RANDOM` clearing depends on an unseeded `Random`.
- `HashFunction.hash()` rejects null/empty key byte arrays and uses absolute modulo; extreme hash values should be considered in tests because `Math.abs(Integer.MIN_VALUE)` remains negative in Java.
- `FutureIO.awaitFuture()` blocks; cancellation is deliberately not converted to IOException. Callers that expect all failures as IOExceptions must handle `CancellationException`, runtime exceptions, and errors separately.
- `RemoteIterators.filteringRemoteIterator()` may perform source IO in `hasNext()`, which can surprise callers that assume `hasNext()` is cheap. `foreach()` closes/cleans up the iterator after iteration, so callers should not reuse it.

## Test Signals

Relevant tests and downstream signals in the tree include:

- `src/test/java/org/apache/hadoop/util/TestShell.java` and `TestWinUtils.java` for shell execution, timeout/platform behavior, Hadoop home, and winutils lookup.
- `src/test/java/org/apache/hadoop/util/TestShutdownHookManager.java` for ordering, registration, timeout, and shutdown-state behavior.
- `src/test/java/org/apache/hadoop/util/TestStringInterner.java` for null handling and strong/weak interning behavior.
- `src/test/java/org/apache/hadoop/util/TestSysInfoLinux.java` and `TestSysInfoWindows.java` for OS-specific `SysInfo` parsing.
- ToolRunner integration appears in CLI tests such as `TestFindClass`, filesystem shell tests, RPC benchmark tests, and tool-based load generator tests.
- `src/test/java/org/apache/hadoop/util/bloom/TestBloomFilters.java` and `BloomFilterCommonTester.java` cover Bloom membership, add, exception behavior, serialization/deserialization, logical operations, dynamic rows, counting approximate counts/deletes, retouched selective clearing, and large vector serialization.
- `src/test/java/org/apache/hadoop/io/TestBloomMapFile.java` is an integration signal for Bloom filters in Hadoop IO.
- `src/test/java/org/apache/hadoop/fs/impl/TestFutureIO.java`, filesystem contract tests, and statistics duration tests exercise `FutureIO.awaitFuture`, exception extraction, timeouts, and async filesystem flows.
- `src/test/java/org/apache/hadoop/util/functional/TestRemoteIterators.java` covers iterator creation, mapping/filtering, closing, statistics passthrough, haltable iteration, and list/array/foreach conversions.

## Chunk Notes for Reconciliation

This document intentionally describes only `Apache_Hadoop_Common_3.3.3.xml` lines 37014-39037. Earlier methods and nested classes of `Shell`, the abstract `Filter` base class, `Key`, hash package classes, and later functional helpers may be covered by adjacent chunks or by final merge reconciliation. No final per-source report was written here.
