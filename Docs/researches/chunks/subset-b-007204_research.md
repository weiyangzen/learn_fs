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
