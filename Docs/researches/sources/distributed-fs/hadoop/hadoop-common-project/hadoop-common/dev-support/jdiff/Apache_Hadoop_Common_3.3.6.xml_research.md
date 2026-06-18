# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007225`: lines 1-6040, `Docs/researches/chunks/subset-b-007225_research.md`
- `subset-b-007226`: lines 6041-12112, `Docs/researches/chunks/subset-b-007226_research.md`
- `subset-b-007227`: lines 12113-18228, `Docs/researches/chunks/subset-b-007227_research.md`
- `subset-b-007228`: lines 18229-24759, `Docs/researches/chunks/subset-b-007228_research.md`
- `subset-b-007229`: lines 24760-31093, `Docs/researches/chunks/subset-b-007229_research.md`
- `subset-b-007230`: lines 31094-37159, `Docs/researches/chunks/subset-b-007230_research.md`
- `subset-b-007231`: lines 37160-40994, `Docs/researches/chunks/subset-b-007231_research.md`

## Chunk Research

### subset-b-007225: lines 1-6040

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 1-6040

## Research scope

This chunk is the opening portion of the generated JDiff XML API snapshot for Apache Hadoop Common 3.3.6. It is not implementation source; it records public API declarations, inheritance, visibility, deprecation annotations, fields, method signatures, checked exceptions, and embedded Javadocs. The range covers the document header and generation classpath, `org.apache.hadoop.HadoopIllegalArgumentException`, the public `org.apache.hadoop.conf` API, empty crypto package markers, the `org.apache.hadoop.crypto.key` provider API, and the beginning of `org.apache.hadoop.fs` through part of `CommonConfigurationKeysPublic`.

## Purpose

The file exists to support API compatibility comparison between Hadoop Common releases. The XML captures the externally visible Hadoop Common contract for tools such as JDiff, including which APIs are public, abstract, final, deprecated, or exception-bearing.

Within this chunk, the API surface is foundational. `org.apache.hadoop.conf.Configuration` is the main configuration loader, overlay, query, serialization, deprecation, and typed-conversion API used across Hadoop. `Configured` and `Configurable` establish the common pattern for components that receive a `Configuration`. `KeyProvider` and `KeyProviderFactory` define the encryption key management abstraction and provider discovery contract. The `org.apache.hadoop.fs` section starts the filesystem abstraction layer: `AbstractFileSystem` is the implementor-facing API behind `FileContext`; supporting types describe abortable writes, Avro seekable input, batched listing, block locations, storage policies, byte-buffer reads, stream cache hints, checksum exceptions, checksum-backed filesystems, and public configuration keys.

## Important APIs and types

`org.apache.hadoop.HadoopIllegalArgumentException` extends `IllegalArgumentException` to distinguish Hadoop-thrown invalid-argument failures from JDK-originated ones. It exposes a public message constructor.

`Configurable` defines `setConf(Configuration)` and `getConf()`. `Configured` is the base implementation with default and configuration constructors, storing and returning a `Configuration`.

`Configuration` implements `Iterable` and `Writable`. Constructors create a default-loading configuration, a configuration with default resources optionally disabled, or a clone of another `Configuration`. Global static APIs manage default resources and deprecation metadata: `addDefaultResource`, `reloadExistingConfigurations`, `addDeprecation`, `addDeprecations`, `isDeprecated`, `dumpDeprecatedKeys`, and `hasWarnedDeprecation`.

`Configuration` resource APIs accept classpath names, `URL`, `Path`, `InputStream`, named `InputStream`, and another `Configuration`, with optional restricted parser flags. Resource order is significant: later resources override earlier resources unless a property was marked final. InputStream resources may be cached, increasing memory pressure.

`Configuration` lookup and mutation APIs include `get`, `getRaw`, `getTrimmed`, `set`, `unset`, `setIfUnset`, `onlyKeyExists`, `size`, `clear`, and `iterator`. The typed layer covers ints, integer arrays, longs, byte-sized longs with suffixes, floats, doubles, booleans, enums, time durations, duration arrays, storage sizes, regex patterns, integer ranges, comma-delimited string collections, trimmed strings, classes, class arrays, instantiated classes, local paths, local files, resources, socket addresses, and connect-address rewriting.

Password handling is exposed through `getPassword`, `getPasswordFromCredentialProviders`, and protected `getPasswordFromConfig`. The public contract prefers the credential provider API and only conditionally falls back to clear text configuration.

Serialization and diagnostics in `Configuration` include `writeXml(OutputStream)`, `writeXml(Writer)`, single-property `writeXml(String, Writer)`, static JSON-style `dumpConfiguration`, `readFields`, `write`, `getPropertySources`, `getFinalParameters`, `getPropsWithPrefix`, `getValByRegex`, `getAllPropertiesByTag`, `getAllPropertiesByTags`, `isPropertyTag`, `setQuietMode`, classloader get/set, and a debugging `main`.

The `Configuration` class documentation defines key behavior: default resources are `core-default.xml` and `core-site.xml`; final parameters prevent later override; variable expansion resolves other configuration values, `env.` variables with default syntaxes, and system properties; deprecated keys warn by default; and tags group related properties such as HDFS or security settings.

`KeyProvider` is an abstract, thread-safe, `Closeable` provider of secret key material. It exposes provider configuration, options creation, transient-store detection, key lookup by version, key listing, metadata lookup, bulk metadata lookup, current-key lookup, key creation with caller-supplied or generated material, key deletion, key rolling with supplied or generated material, cache invalidation, flushing to persistent storage, password-needed/warning/error hooks, and helpers for base/version names and provider search. Public constants identify default cipher, bit length, and JCEKS serialization-filter configuration.

`KeyProviderFactory` is an abstract service-loader-based factory. It creates providers for URIs, discovers provider lists from a `Configuration`, and exposes `KEY_PROVIDER_PATH` as the configuration key for provider URI paths.

`Abortable` defines `abort()`, returning `AbortableResult`, for output streams whose pending writes can be canceled so data never becomes visible. The Javadoc ties this to object-store output streams and `FSDataOutputStream`.

`AbstractFileSystem` is the core implementor-facing filesystem interface for `FileContext`, implements `PathCapabilities`, and owns a protected `FileSystem.Statistics statistics` field. Its constructor binds URI, supported scheme, authority requirements, and default port. Factory/static APIs include `createFileSystem`, `get(URI, Configuration)`, statistics lookup, clear, print, and map access.

`AbstractFileSystem` path and metadata APIs include scheme/path validation, URI/default-port access, `makeQualified`, initial working directory, home directory, path-based server defaults, symlink/mount resolution, status lookup, file-link status, block locations, FS status, listing, corrupt-block listing, checksum verification toggles, canonical service name, equality/hash code, and `msync` for synchronizing client metadata state in systems such as HDFS HA.

`AbstractFileSystem` data and namespace mutation APIs include final `create`, abstract `createInternal`, `mkdir`, `delete`, `open`, `truncate`, `setReplication`, final `rename`, `renameInternal` overloads, symlink creation/target lookup, permission/owner/time changes, checksum retrieval, ACL APIs, xattr APIs, snapshot create/rename/delete, storage-policy APIs, asynchronous-style `openFileWithOptions`, `hasPathCapability`, multipart uploader creation, and `methodNotSupported`.

`AvroFSInput` adapts `FSDataInputStream` to Avro `SeekableInput`, with constructors from a stream plus length or from `FileContext` and `Path`, and methods `length`, `read`, `seek`, `tell`, and `close`.

`BatchListingOperations` is an optional filesystem capability. Filesystems implementing it can return `RemoteIterator<PartialListing>` for batches of paths, optionally with located statuses; implementations should advertise `CommonPathCapabilities.FS_EXPERIMENTAL_BATCH_LISTING`.

`BlockLocation` is a serializable block metadata carrier. It stores host names, cached hosts, transfer names, topology paths, storage IDs, storage types, file offset, length, corruption flag, and striped/erasure-coded status. Its documentation distinguishes replicated-file block locations from erasure-coded logical block groups.

`BlockStoragePolicySpi` names storage policy behavior: policy name, preferred storage types, creation fallbacks, replication fallbacks, and whether the policy is inherit-only/copy-on-create.

`ByteBufferPositionedReadable` and `ByteBufferReadable` expose direct `ByteBuffer` read APIs. Positioned reads are documented as thread-safe and must not change the stream offset; both APIs define buffer position/limit behavior and warn that buffer state is undefined after exceptions. Callers are expected to check stream capabilities first.

`CanSetDropBehind`, `CanSetReadahead`, and `CanUnbuffer` are stream capability interfaces for cache-dropping hints, readahead hints, and releasing buffers/sockets/file descriptors.

`ChecksumException` extends `IOException` and carries a failing file position via `getPos()`.

`ChecksumFileSystem` is an abstract `FilterFileSystem` that creates and verifies client-side checksum files for each raw file. It exposes checksum-file naming, checksum-length calculations, bytes-per-checksum, raw filesystem access, checksum verification/write toggles, open/create/append/truncate/concat variants, permission/owner/ACL propagation, replication, rename/delete/listing/mkdir/copy/local-output operations, checksum failure reporting, builder-style open/create/append integration, and path capability filtering.

`CommonConfigurationKeysPublic` begins a long list of public configuration key constants and defaults. In this range the constants cover network topology scripts and mappings, default filesystem names, disk usage and free-space scan intervals, remote symlink resolution, trash settings, protected directories, local block size, automatic filesystem close, parallel filesystem creation count, local/FTP filesystem implementation keys, client topology resolution, MapFile/Bloom and SequenceFile/TFile IO settings, LZO codec class, file buffer size, checksum-error skipping, deprecated MapReduce-era sort keys, caller context limits/separators, IPC client/server connection tuning, slow RPC logging, RPC socket factory and SOCKS server, hash type, and group mapping/cache settings. The chunk ends inside `HADOOP_SECURITY_GROUPS_CACHE_BACKGROUND_RELOAD`.

## Control flow and behavior

`Configuration` follows lazy resource loading. The Javadocs for `get` state that first access loads properties from configured sources; `reloadConfiguration` clears loaded resource-derived properties and final-parameter state so resources will be reread before the next access, while programmatic `set` values still overlay resource values.

Resource override flow is order-based with final-property gates. Default resources load first unless disabled, added resources load later, and later values override earlier values except where an earlier resource marked a key final. `setDeprecatedProperties` can materialize deprecated aliases for currently set replacement keys so iteration sees both names.

Deprecation registration is global and lockless by contract: `addDeprecations` creates a new deprecation context from the old one and atomically swaps until it wins any race. Deprecated-key reads return the first non-null replacing key, while setting a deprecated key also sets replacement keys. Some older multi-new-key overloads are deprecated in favor of single-new-key forms.

Value lookup behavior includes name trimming, optional variable expansion, raw access without expansion, typed parsing with defaults, and explicit failure modes. Numeric methods throw `NumberFormatException` for malformed numeric values; enum/class APIs throw for invalid mappings; socket-address helpers combine bind-host and client-address configuration and replace wildcard listener addresses with connectable local addresses.

Credential flow in `getPassword` tries credential providers first, then falls back to clear text configuration through `getPasswordFromConfig`. This is an explicit security control point for replacing clear-text secrets with provider aliases.

`Configuration` output flow writes non-default properties to XML or emits JSON-like dumps of values plus final/resource metadata. Single-property dump/write methods throw `IllegalArgumentException` when a requested non-empty property is missing.

`KeyProvider` separates generated-key convenience methods from storage-specific abstract methods. The public `createKey(name, options)` and `rollNewVersion(name)` generate material and delegate to abstract overloads that accept raw bytes. Persistent providers must implement `flush()` so key changes reach durable storage; `invalidateCache` exists to make post-roll reads observe the new version strongly.

`KeyProviderFactory` resolves provider URIs from configuration and uses service-loader discovery to find factories. A missing scheme-specific factory returns null from `get(URI, conf)` rather than always failing; provider initialization failures can throw `IOException`.

`AbstractFileSystem` factory flow uses the URI scheme to derive `fs.AbstractFileSystem.<scheme>.impl`, instantiate the implementation with the full URI and configuration, and bind statistics by scheme/authority. Path operations first validate the path belongs to the filesystem, either by matching scheme/authority for qualified URIs or by requiring a slash-relative path.

`AbstractFileSystem` uses template and wrapper patterns. Public final `create` and `rename` handle option normalization and policy before delegating to abstract or overridable internals. Many optional features have default implementations that throw unsupported-operation exceptions via `methodNotSupported`, allowing filesystems to implement only supported capabilities.

Metadata and data operation flow mirrors `FileContext`: `create`, `mkdir`, `delete`, `open`, `rename`, permission/owner/time changes, listing, ACLs, xattrs, snapshots, and storage policies all state that their specification matches the corresponding `FileContext` method, with the added requirement that paths belong to the filesystem and permissions are already absolute after umask application where relevant.

`openFileWithOptions` in `AbstractFileSystem` returns a `CompletableFuture` but the documented base implementation performs a blocking `open(Path, int)` call before completing the future. This sets asynchronous-looking API expectations without requiring a thread pool in base implementations.

`ChecksumFileSystem` wraps raw filesystem operations with checksum sidecar behavior. Reads open data and checksum streams when verification is enabled; writes create or update checksum files when write checksums are enabled; rename, delete, local copy, append, truncate, concat, permission, owner, ACL, listing, and capability methods must account for both visible data paths and hidden checksum files.

## State and persistence behavior

`Configuration` has both instance state and global state. Instance state includes resource references, loaded properties, final-parameter sets, source metadata, tag metadata, quiet mode, classloader, system-property restriction flags, and programmatic overlays. Global state includes default resources and the deprecation context. Because configurations can be reloaded globally through `reloadExistingConfigurations`, code holding configuration instances must expect resource-derived values to change after reload.

Configuration persistence is explicit through Hadoop `Writable` `readFields`/`write` and XML output methods. XML output is limited to non-default properties, and JSON-style dumps intentionally omit properties loaded from input-stream resources. InputStream resources may be cached, so configuration state can retain full resource contents in memory.

`Configurable` and `Configured` make configuration state part of component lifecycle. Components that mutate or replace the configuration can affect later initialization and classloading behavior.

`KeyProvider` state belongs to provider implementations but the API requires thread safety. It may manage durable key stores, transient key material, caches, current-version metadata, password state, and pending writes. `flush()` is the persistence boundary; `close()` is the lifecycle boundary; `needsPassword` describes whether normal operation lacks required credentials.

`KeyProviderFactory` itself is stateless from this XML view, but provider discovery depends on `Configuration` and Java service-loader metadata.

`AbstractFileSystem` instances retain their URI identity and per-filesystem statistics. Static statistics tables persist process-wide until cleared. Filesystem implementations persist or mutate external state such as files, directories, ACLs, xattrs, snapshots, checksums, block placement, and storage policy through their backing storage systems.

`BlockLocation` is mutable serializable metadata, not a live block handle. Callers can modify hosts, names, topology paths, storage IDs/types, offset, length, and corruption flags locally; persisted meaning comes from the filesystem implementation that produced it.

`AvroFSInput` owns or wraps an `FSDataInputStream` and current stream position; `close()` releases it. Byte-buffer stream interfaces mutate caller-supplied buffer positions on success but leave buffer state undefined on failure.

`ChecksumFileSystem` persists checksum sidecar files in the wrapped filesystem. Its verification/write flags and bytes-per-checksum configuration are instance behavior; its operations must keep data files and checksum files consistent across create, rename, truncate, append, concat, copy, and delete.

`CommonConfigurationKeysPublic` is constant metadata. Its state is compile-time public API, but changing names or defaults is compatibility-sensitive because downstream deployments and tools reference these constants and corresponding XML keys.

## Dependencies and integration points

This JDiff file was generated by `IncludePublicAnnotationsJDiffDoclet` against Hadoop Common 3.3.6 with a large Java 8 classpath. The classpath lists Hadoop annotations, shaded protobuf and Guava, commons libraries, Jetty, Jersey, Jackson, Avro, Curator, ZooKeeper, Kerby, JSch, reload4j/SLF4J, compression libraries, XML libraries, DNS Java, WildFly OpenSSL, and `hadoop-auth`; the XML itself records only the resulting public API.

`Configuration` integrates with core Java IO, networking, regex, classloading, collections, `TimeUnit`, Hadoop `Path`, `Writable`, credential providers, local filesystem selection, and service/application code that implements `Configurable`. It is the central dependency injection and runtime policy object for Hadoop Common.

`Configured` is a base class for Hadoop tools and services that want to participate in generic configuration handling. `HadoopIllegalArgumentException` is a common exception type for Hadoop API validation.

`KeyProvider` integrates with encryption zones and other Hadoop encryption clients through secret-key material, metadata, version names, current-key selection, and provider-specific storage. `KeyProviderFactory` integrates with service-loader providers and the `hadoop.security.key.provider.path` style configuration path represented by `KEY_PROVIDER_PATH`.

`AbstractFileSystem` is the implementor side of `FileContext`, and its Javadocs repeatedly reference `FileContext` method contracts. It depends on `Path`, `FSDataInputStream`, `FSDataOutputStream`, `FsServerDefaults`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `FsStatus`, `FileChecksum`, `RemoteIterator`, ACL and permission types, xattr flag enums, storage policy SPI, multipart upload builders, `OpenFileParameters`, `PathCapabilities`, progress callbacks, and Hadoop security `AccessControlException`.

`AvroFSInput` bridges Hadoop filesystem streams to Apache Avro's `SeekableInput`. `BatchListingOperations` bridges filesystem implementations to higher-level clients that can profit from multi-path listing. Byte-buffer read interfaces integrate with `StreamCapabilities` flags, enabling callers to probe support before invoking optional methods.

`ChecksumFileSystem` depends on `FilterFileSystem`, raw `FileSystem`, checksum options, `FSDataInputStream`, `FSDataOutputStream`, `Progressable`, permissions, ACLs, remote iterators, and builder APIs. It integrates with local copy operations and checksum failure reporting.

`CommonConfigurationKeysPublic` integrates public Java constants with `core-default.xml` and deployment configuration. It spans filesystem behavior, topology, IO formats, compression, IPC, RPC, caller context, hashing, and group-mapping subsystems.

## Risks and edge cases

Because this is generated API XML, it can drift from implementation only if generation inputs or annotations are wrong. Consumers should not treat it as executable behavior beyond documented public contracts.

`Configuration` lazy loading means reads can trigger IO, parsing, variable expansion, deprecation warnings, and cache population. Tests and callers that assume construction eagerly loads resources can miss failures until first lookup.

Final parameters and resource order are easy to misapply. A later resource silently cannot override a final value, and programmatic `set` overlays resource-derived values even after `reloadConfiguration`.

Deprecation aliasing is global and concurrency-sensitive. Adding deprecations after resources have loaded can throw `UnsupportedOperationException`; multi-key aliases can reset related keys together; deprecated overloads remain public for compatibility but should not anchor new code.

Variable expansion crosses configuration, environment, and system properties. This can expose deployment-specific behavior, recursive expansion risks, and differences when system-property restriction flags are enabled.

Clear-text password fallback is a security risk when credential providers are expected. Code using `getPassword` should validate provider configuration and not accidentally depend on `getPasswordFromConfig` in production.

Typed getters can hide or surface bad configuration differently. Booleans return defaults for invalid values, while numeric and enum/class lookups can throw. Storage-size and time-duration suffix parsing needs coverage for units, defaults, and invalid suffixes.

`Configuration` InputStream resources are cached and later closed. Reusing large streams can increase memory use, and source metadata for input-stream properties is omitted by dump output.

`KeyProvider` implementations must be thread safe and must clearly separate transient providers from durable stores. Failing to call `flush()` after key create/delete/roll can leave key state unpersisted. Cache invalidation after rolling keys is important for strong read-after-roll guarantees.

Key version naming is public behavior. `getBaseName` and `buildVersionName` encode parsing assumptions around separators such as `@`; incompatible naming can break provider search, current-key lookup, and decrypt-by-version flows.

`AbstractFileSystem` path validation is a correctness and security boundary. Accepting mismatched schemes/authorities, relative paths incorrectly, invalid names, or unresolved symlinks can route operations to the wrong backend or bypass checks.

Optional filesystem APIs default to unsupported behavior. Callers should use capability checks for symlinks, byte-buffer reads, multipart upload, batch listing, and path capabilities rather than assuming every filesystem supports HDFS-like features.

`openFileWithOptions` returns a future but can block in the base implementation. Callers must not assume non-blocking behavior unless the concrete filesystem documents it.

ACL, xattr, snapshot, storage-policy, and checksum operations have backend-specific semantics and permissions. Default implementations may throw, and wrappers such as `ChecksumFileSystem` must avoid exposing checksum files as normal user data.

`BlockLocation` semantics differ for replicated versus erasure-coded files. Consumers that assume one block location equals one physical block or fixed replica count can mis-handle striped files.

Byte-buffer read APIs leave buffer contents and positions undefined on exceptions. Robust callers must repair or discard buffers after failures.

`ChecksumFileSystem` must keep checksum sidecars synchronized with raw files. Append, truncate, concat, rename, delete, copy-to-local with optional CRC, and permission/ACL changes are all places where data and checksum metadata can diverge.

Public configuration constants are compatibility-sensitive. Deprecated `IO_SORT_*` keys now belong to MapReduce for task sort behavior, while `SEQ_IO_SORT_*` applies to `SequenceFile.Sorter`; confusing the two can produce ineffective tuning.

The line range ends inside a field declaration for `HADOOP_SECURITY_GROUPS_CACHE_BACKGROUND_RELOAD`, so the next chunk must complete that constant and continue the remaining public key surface.

## Test signals

Useful test coverage for code using or changing these APIs should include:

- `Configuration` resource precedence tests covering default-resource loading on/off, added resource order, final-property override rejection, reload behavior, and programmatic overlays after reload.
- Deprecation tests for single-key and legacy multi-key aliasing, warning tracking, `setDeprecatedProperties`, adding deprecations before and after load, and concurrent `addDeprecations` behavior.
- Variable expansion tests for other configuration keys, `env.NAME`, `env.NAME:-default`, `env.NAME-default`, system properties, missing values, recursive references, raw lookup, and system-property restriction flags.
- Typed getter tests for malformed ints/longs/floats/doubles/enums/classes, boolean invalid-value defaulting, byte-size suffixes, storage units, duration suffixes/default units, regex compilation fallback, integer ranges, and trimmed string collections.
- Serialization and diagnostics tests for `writeXml`, single-property XML output, missing single-property errors, `dumpConfiguration`, `readFields`/`write`, property sources, final parameters, tagged-property queries, regex key lookup, and InputStream resource omissions.
- Password tests that verify credential-provider precedence, clear-text fallback behavior, provider IO exceptions, and production configurations that disable or avoid clear-text secrets.
- `Configured`/`Configurable` tests for configuration propagation into tools, filesystems, reflection-created objects, and services.
- `KeyProvider` implementation tests for thread safety, create/delete/roll flows with caller-supplied and generated material, current-key lookup, version-name parsing, metadata bulk lookup, cache invalidation, `flush()` durability, `close()` cleanup, password-needed states, and transient-provider behavior.
- `KeyProviderFactory` tests for configured provider paths, multiple URI schemes, service-loader discovery, missing provider schemes returning null where documented, and initialization failure propagation.
- `AbstractFileSystem` tests for URI scheme/authority validation, default ports, path qualification, invalid paths, slash-relative paths, statistics tables, factory configuration keys, unsupported filesystem errors, and equality/hash code identity.
- Filesystem operation contract tests for create option normalization, absolute permissions after umask, mkdir parent behavior, delete recursion, open buffer size, truncate return values, rename overwrite/no-overwrite behavior, symlink support, resolvePath, file-link status, block locations, fs status, listings, corrupt-block iterators, and checksum verification toggles.
- Metadata feature tests for ACL merge/remove/replace, xattr namespace validation and visibility, snapshot create/rename/delete, storage policy set/unset/get/list, `msync`, `hasPathCapability`, multipart uploader creation, and unsupported-operation defaults.
- `openFileWithOptions` tests for mandatory unknown key rejection, returned `CompletableFuture` success/failure, blocking base behavior, and concrete filesystem asynchronous overrides.
- `AvroFSInput` tests for length, positioned seeking, tell, read bounds, close propagation, and construction from `FileContext` plus `Path`.
- Batch listing tests for partial listings, located statuses, path-order correspondence, IO failure propagation, and advertised experimental capability.
- `BlockLocation` tests for all constructor forms, copy behavior, mutable fields, cached hosts, storage IDs/types, corrupt flag, striped flag, `toString`, replicated-file interpretation, and erasure-coded block-group interpretation.
- Byte-buffer read tests for zero-length reads, EOF `-1`, full-read EOF exceptions, buffer position/limit advancement, positioned-read thread safety, and capability probing before invocation.
- Stream hint tests for drop-behind, readahead, and unbuffer support, including `null` defaults and unsupported-operation behavior.
- `ChecksumFileSystem` tests for checksum file naming/detection/length calculations, bytes-per-checksum, read verification on/off, write checksum on/off, append/truncate/concat checksum updates, rename/delete/list filtering, copy-to-local CRC behavior, local output completion, checksum failure reporting, builder API routing, and capability suppression for blocked operations.
- Configuration-key tests that public constants match `core-default.xml`, deprecated sort keys point users to MapReduce or sequence-file alternatives correctly, and IPC/RPC/group-cache defaults are consumed by their owning subsystems.

### subset-b-007226: lines 6041-12112

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 6041-12112

## Scope

This chunk is generated JDiff compatibility metadata for Apache Hadoop Common 3.3.6. It starts inside `org.apache.hadoop.fs.CommonConfigurationKeysPublic`, covers several complete public API entries in `org.apache.hadoop.fs`, and ends inside the `org.apache.hadoop.fs.FileSystem#getXAttr(Path, String)` declaration.

The source is not implementation code. The useful research surface is the public and protected API contract: class names, inheritance, implemented interfaces, constructors, fields, method overloads, parameter and return types, exceptions, visibility, abstract/final/static flags, deprecation markers, and embedded Javadocs.

## Purpose

The first part of the chunk documents public Hadoop Common configuration keys. These constants bind runtime behavior to `core-default.xml` and user configuration for security group caching, shell group lookup timeouts, Kerberos, RPC protection, crypto codecs and key providers, KMS client caches and failover, secure random providers, safe shell deletion limits, HTTP logs and idle timeouts, credential providers, sensitive-key filtering, tag metadata, service shutdown, Prometheus support, and IPC server metrics scheduling.

The `ContentSummary`, `CreateFlag`, `FileAlreadyExistsException`, and `FileChecksum` entries define core value and validation contracts used by file creation, quota/content accounting, and checksum reporting. They sit beneath both classic `FileSystem` and newer `FileContext` APIs.

The largest part of the chunk covers `FileContext`, `FileStatus`, and the first large portion of `FileSystem`. These are Hadoop's main client-side filesystem contracts. `FileContext` exposes a URI-aware, default-filesystem-aware user interface backed by `AbstractFileSystem`; `FileSystem` exposes the older abstract filesystem base with global cache semantics, URI canonicalization, stream creation/opening, metadata operations, listing, local-copy helpers, symlinks, checksums, status, ACLs, snapshots, storage policies, xattrs, and deletion-on-exit. `FileStatus` is the serializable metadata carrier shared by these APIs.

## Important APIs, Types, and Functions

### Configuration Keys

`CommonConfigurationKeysPublic` fields in this chunk are public static final constants that external callers and downstream modules can rely on. They include:

- Security group cache controls: `HADOOP_SECURITY_GROUPS_CACHE_BACKGROUND_RELOAD_DEFAULT`, `HADOOP_SECURITY_GROUPS_CACHE_BACKGROUND_RELOAD_THREADS`, `HADOOP_SECURITY_GROUPS_CACHE_BACKGROUND_RELOAD_THREADS_DEFAULT`, `HADOOP_SECURITY_GROUP_SHELL_COMMAND_TIMEOUT_KEY`, and deprecated `HADOOP_SECURITY_GROUP_SHELL_COMMAND_TIMEOUT_SECS` aliases.
- Core security identity and authorization keys: `HADOOP_SECURITY_AUTHENTICATION`, `HADOOP_SECURITY_AUTHORIZATION`, `HADOOP_SECURITY_INSTRUMENTATION_REQUIRES_ADMIN`, `HADOOP_SECURITY_SERVICE_USER_NAME_KEY`, `HADOOP_SECURITY_AUTH_TO_LOCAL`, `HADOOP_SECURITY_AUTH_TO_LOCAL_MECHANISM`, DNS interface/nameserver keys, token files, and HTTP authentication type.
- Kerberos and SASL controls: minimum seconds before relogin, keytab auto-renewal flag, `HADOOP_RPC_PROTECTION`, and `HADOOP_SECURITY_SASL_PROPS_RESOLVER_CLASS`.
- Crypto and key-provider controls: codec class keys, AES CTR no-padding defaults, cipher suite, JCE provider, JCEKS serial filter, crypto buffer size, impersonation provider, key-provider path, default key bit length, and default cipher.
- KMS client tuning: encrypted-key cache size, low watermark, refill thread count, expiry, timeout, failover retry count, and failover sleep bounds.
- Secure random and shell/http/service controls: Java secure random algorithm, secure random implementation and device path, missing-default-FS shell warning, safe delete limit, HTTP logs, credential provider path/fallback/password file, sensitive config keys, system/custom tags, service shutdown timeout, Prometheus flag, HTTP idle timeout, and IPC server metrics update runner interval.

Two tag constants, `HADOOP_SYSTEM_TAGS` and `HADOOP_CUSTOM_TAGS`, are deprecated in favor of `HADOOP_TAGS_SYSTEM` and `HADOOP_TAGS_CUSTOM`. The group shell command timeout `*_SECS` constants are deprecated in favor of `*_KEY` and `*_DEFAULT`.

### Content and Creation Contracts

`ContentSummary` extends `QuotaUsage` and implements `Writable`. Visible constructors are retained for compatibility but their Javadocs point callers toward `ContentSummary.Builder`. Accessors expose length, file count, directory count, snapshot length/file/directory counts, snapshot space consumption, and erasure coding policy. Formatting methods include static header helpers and multiple `toString(...)` overloads for quota output, human-readable output, storage-type quota display, and snapshot-inclusive or snapshot-exclusive output. `toSnapshot(boolean)` formats snapshot counts.

`CreateFlag` is an enum API for create/append semantics. Static validators check invalid combinations generally, for create with path existence, and for append. Javadocs define legal combinations such as `CREATE`, `APPEND`, `OVERWRITE`, `CREATE|APPEND`, `CREATE|OVERWRITE`, `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`, while explicitly rejecting `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`.

`FileAlreadyExistsException` is the typed `IOException` for operations whose target already exists and is not configured for overwrite.

`FileChecksum` is an abstract `Writable` exposing algorithm name, checksum byte length, raw checksum bytes, optional `Options.ChecksumOpt`, and equality/hash behavior based on algorithm and value.

### FileContext

`FileContext` implements `PathCapabilities` and provides factory methods for default, local, URI-specific, `Configuration`-specific, and `AbstractFileSystem`-specific contexts. It has protected `getFSofPath(Path)` routing to the backing `AbstractFileSystem`.

The visible operations include working directory and umask state (`setWorkingDirectory`, `getWorkingDirectory`, `getUMask`, `setUMask`), user identity (`getUgi`), home directory lookup, path resolution and qualification, file create through both direct `FSDataOutputStream` and `FSDataOutputStreamBuilder`, mkdir, delete, open, truncate, set replication, rename, permission/owner/time setters, checksum and checksum verification controls, file and link status, symlink creation and target lookup, filesystem status, list status and located status iterators, corrupt block listing, delete-on-exit, symlink resolution helpers, and filesystem statistics inspection.

It also exposes advanced metadata and policy operations: ACL modification/removal/replacement/status, xattr set/get/list/remove, snapshot create/rename/delete, storage policy satisfy/set/unset/get/list, builder-based `openFile`, path capability checks, server-default lookup by path, and multipart uploader creation.

Public constants include `LOG`, compatibility `DEFAULT_PERM`, separate `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`.

### FileStatus

`FileStatus` implements `Writable`, `Comparable`, `Serializable`, and `ObjectInputValidation`. Constructors cover legacy metadata without symlinks, metadata with symlink path, metadata with boolean attributes, metadata with an attribute set, a no-arg constructor, and a copy constructor.

The API exposes length, file/directory/symlink classification, deprecated `isDir()`, block size, replication, modification/access times, permission, ACL/encryption/erasure-coding/snapshot-enabled flags, owner, group, path, symlink, setters for path and symlink, protected defaulting setters for permission/owner/group, comparison, equality, hash, string rendering, protobuf-backed `readFields`/`write` methods deprecated in favor of PBHelper/protobuf use, and `validateObject`.

`FileStatus.attributes(boolean acl, boolean crypt, boolean ec, boolean sn)` converts booleans to an attribute flag set. `NONE` is a shared empty attribute set for the common case.

### FileSystem

`FileSystem` is abstract, extends `Configured`, and implements `Closeable`, `DelegationTokenIssuer`, and `PathCapabilities`. The chunk covers its protected constructor and a large part of its public/protected/static contract.

Instance acquisition and lifecycle APIs include `get(URI, Configuration, String)`, `get(Configuration)`, `get(URI, Configuration)`, `newInstance(...)` overloads, `getLocal`, `newInstanceLocal`, `closeAll`, and `closeAllForUGI`. Javadocs specify the important cache behavior: `get(URI, Configuration)` may return a cached instance unless `fs.$SCHEME.impl.disable.cache` is true, while `newInstance` always creates a unique instance.

URI and identity methods include `getDefaultUri`, `setDefaultUri`, `initialize`, `getScheme`, abstract `getUri`, protected `getCanonicalUri`, protected `canonicalizeUri`, protected `getDefaultPort`, protected static `getFSofPath`, `getCanonicalServiceName`, deprecated `getName`, deprecated `getNamed`, `makeQualified`, and protected `checkPath`.

Data path APIs include static permission-preserving `create(FileSystem, Path, FsPermission)` and `mkdirs(FileSystem, Path, FsPermission)`, multiple `open(Path)` and `open(PathHandle)` overloads, `getPathHandle` with protected `createPathHandle`, many `create(...)` overloads, abstract full-argument `create`, `primitiveCreate`, `primitiveMkdir`, `createNonRecursive` overloads, non-atomic `createNewFile`, append overloads including append-to-new-block, `concat`, replication getters/setters, abstract boolean `rename`, protected option-based rename, `truncate`, abstract recursive delete, deprecated single-argument delete, delete-on-exit registration/cancellation/processing, existence/type/length helpers, content summary and quota usage, quota setters, list/glob/located status APIs, local/remote copy and move helpers, local-output staging, close, used/block-size/default-block/default-replication helpers, file status, and metadata synchronization via `msync`.

The latter visible part covers `fixRelativePart`, symlink create/status/target/resolve support, checksum lookup for whole files and prefix ranges, checksum verification/write toggles, filesystem capacity status, permission/owner/time setters, snapshots, ACLs, and the beginning of xattr support (`setXAttr` overloads and the start of `getXAttr`).

## Control Flow

The XML itself has no executable control flow, but the API contracts imply several important flows.

Configuration flow starts with keys from `CommonConfigurationKeysPublic` being read from `Configuration` and `core-default.xml`, then consumed by security, HTTP, KMS, crypto, shell, service, and metrics subsystems. The constants are compatibility anchors: downstream code compiles against these names and expects the runtime configuration files to use the same string values.

File creation flow validates `CreateFlag` combinations first, then routes through `FileContext#create` or `FileSystem#create`. `FileContext` applies its umask and server-default logic before invoking the target `AbstractFileSystem`; `FileSystem` exposes compatibility helpers such as `primitiveCreate` for the FileSystem-to-FileContext transition. Builder-based create delays final validation and filesystem mutation until `build()`.

Path routing flow in `FileContext` resolves working-directory-relative and slash-relative paths using a default filesystem and the context working directory. It then selects an `AbstractFileSystem` with `getFSofPath` and delegates operations. In `FileSystem`, `checkPath`, URI canonicalization, and scheme/authority matching guard whether a path belongs to an instance.

Filesystem lookup flow differs between cached and uncached APIs. `FileSystem.get(...)` can return a cached initialized instance keyed by scheme/authority/user/config behavior; `newInstance(...)` always creates a unique instance. `closeAll` and `closeAllForUGI` close cached instances and can invalidate objects still referenced by callers.

Read flow uses `open(Path, bufferSize)` or builder-based `openFile(Path)`; path-handle reads use a durable serializable handle and may verify constraints encoded when the handle was created. Block-location flow maps a file range to physical hosts for distributed filesystems or a default localhost block for simpler filesystems.

Write flow uses create, append, concat, truncate, replication, and checksum options. `truncate` has an asynchronous completion signal: `true` means immediately reusable, while `false` means a background block-length adjustment is still running.

Metadata flow uses `FileStatus` and `ContentSummary` as carriers. List/glob/located-status methods return arrays or `RemoteIterator`s; ACL, xattr, snapshot, and storage-policy methods mutate or retrieve metadata on the underlying filesystem, with unsupported implementations allowed to throw `UnsupportedOperationException`.

Delete-on-exit flow registers paths on a `FileSystem` instance and processes them when the instance closes or a clean JVM shutdown closes cached filesystems. This makes correctness depend on cache use and lifecycle ordering.

## State and Persistence Behavior

This JDiff file persists the 3.3.6 API signature set for compatibility comparison. It does not store Hadoop runtime state, but many APIs in the range define stateful or durable behavior.

`FileContext` stores process-local user-facing state: default filesystem, working directory, umask, and UGI. Its Javadocs emphasize that working directory behavior is prefix-based rather than inode-based, so setting the working directory does not resolve symlinks the way a Unix process directory might.

`FileSystem` has process-global cache state behind `get(...)` and static close operations. Cached instances share lifecycle and delete-on-exit processing; unique `newInstance(...)` objects bypass the cache. `initialize(URI, Configuration)` is the transition point between construction and ready-for-use state, and subclasses overriding it must call the superclass.

Persistent filesystem state is changed by create, append, concat, truncate, rename, delete, mkdir, set replication, set permission, set owner, set times, symlink creation, snapshot operations, ACL mutation, xattr mutation, storage-policy changes, and quota changes. Some operations are optional or implementation-dependent, especially append, concat, truncate, symlinks, ACLs, xattrs, snapshots, and storage policies.

`FileStatus`, `ContentSummary`, and `FileChecksum` are value carriers with serialization or equality contracts. `FileStatus` retains protobuf-backed `Writable` methods for compatibility but deprecates them in favor of PBHelper/protobuf direct use. `ContentSummary` inherits quota state from `QuotaUsage` and adds snapshot and erasure-coding fields. `FileChecksum` equality depends on both algorithm and byte value.

Configuration-key state is externalized in `Configuration` and core XML files. Security and crypto settings are especially durable from an operator perspective because they affect authentication, key provider selection, credential fallback, random source selection, group lookup cache behavior, and KMS failover behavior.

## Dependencies and Integration Points

This chunk depends on Java platform types such as `URI`, `DataInput`, `DataOutput`, `IOException`, `FileNotFoundException`, `InvalidObjectException`, arrays, collections, enums, and `Serializable`/`ObjectInputValidation`.

Key Hadoop dependencies include `org.apache.hadoop.conf.Configuration`, `org.apache.hadoop.conf.Configured`, `org.apache.hadoop.fs.Path`, `AbstractFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, stream builders, `RemoteIterator`, `BlockLocation`, `BlockStoragePolicySpi`, `FsServerDefaults`, `FsStatus`, `MultipartUploaderBuilder`, `PathHandle`, `Options.*`, `PathCapabilities`, `QuotaUsage`, `StorageType`, `ParentNotDirectoryException`, `UnsupportedFileSystemException`, `UnresolvedLinkException`, `InvalidPathHandleException`, and `InvalidPathException`.

Security integration points include `UserGroupInformation`, `AccessControlException`, delegation token issuance, token service-name construction, Kerberos relogin settings, RPC protection, SASL property resolution, group mapping, impersonation provider selection, and credential-provider configuration.

Permission and metadata integration points include `FsPermission`, `AclStatus`, ACL entry lists, xattr name/value maps, snapshot management, storage policies, erasure-coding and encryption status, and PBHelper/protobuf serialization for `FileStatus`.

Operational integration points include `core-default.xml`, HTTP/logging/Prometheus settings, shutdown hook management, shell command behavior, KMS client caches and failover, secure random implementation selection, and IPC server metrics update scheduling. `FileContext.LOG` uses SLF4J.

## Risks and Edge Cases

- The chunk begins and ends inside larger class declarations. Adjacent chunks are required for complete `CommonConfigurationKeysPublic` and `FileSystem` coverage.
- JDiff metadata omits method bodies. Exact cache keys, synchronization, exception mapping, path normalization, flag validation, and filesystem-specific behavior require implementation-source review.
- Public configuration constants are compatibility-sensitive. Renaming, removing, or changing string values can silently break operator configuration, security behavior, and downstream compilation.
- Deprecated aliases remain part of the public API. Removing `*_SECS`, `HADOOP_SYSTEM_TAGS`, `HADOOP_CUSTOM_TAGS`, `FileSystem#getName`, `FileSystem#getNamed`, `FileStatus#isDir`, or deprecated `FileStatus` Writable methods can break binary or source compatibility.
- `CreateFlag` validation is safety-critical. Accepting `APPEND|OVERWRITE` or mishandling `CREATE|APPEND`/`CREATE|OVERWRITE` changes data-loss behavior.
- `SYNC_BLOCK` Javadocs warn that callers still need `Syncable#hsync()` after each write for true synchronous behavior. Misunderstanding this flag can produce durability gaps.
- `LAZY_PERSIST` depends on transient storage availability and may not behave consistently across filesystems.
- `ContentSummary` output has many option combinations. Snapshot inclusion/exclusion, storage-type quota display, and human-readable formatting are easy to regress in CLI-visible output.
- `FileContext` working directories are prefix-based and do not follow symlinks. Code expecting Unix inode-like current-directory semantics may resolve paths differently.
- `FileSystem.get(...)` cache behavior can leak stale configuration, credentials, delete-on-exit registrations, or lifecycle state across callers if cache disabling and `newInstance` are used incorrectly.
- `closeAll` and `closeAllForUGI` can invalidate cached instances still held by application code.
- `initialize(...)` override ordering matters. Subclasses that fail to call `super.initialize` or mutate configuration incorrectly can break statistics, caching, and URI setup.
- URI canonicalization may add default ports or canonicalize hosts. Token service names and cache keys can change if this logic is inconsistent.
- `checkPath` performs scheme/authority matching and subclasses may vary; case sensitivity and authority normalization are common cross-filesystem pitfalls.
- `createNewFile` is explicitly not atomic by default, so it is unsafe as a distributed lock primitive unless overridden atomically.
- `rename` atomicity is filesystem-dependent, and the option-based default implementation is documented as non-atomic.
- `truncate` returning `false` means clients must wait before appending or otherwise updating the file. Ignoring this can corrupt workflow assumptions.
- `setReplication` returns true even when replication is unsupported in the default implementation, so callers cannot always infer that storage replication changed.
- `getFileBlockLocations` has edge semantics for null file status, ranges beyond EOF, replicated files, and erasure-coded logical block groups.
- `PathHandle` references depend on stored constraints; stale or moved files may throw `InvalidPathHandleException`.
- `FileStatus` equality and hash are path-based, not full metadata-based. Collections keyed by `FileStatus` may ignore changes to length, owner, permission, or attributes.
- `FileStatus` permissions default to all-access when unavailable. Consumers must not assume a permissive value means the backing filesystem actually enforces those permissions.
- ACL and xattr APIs may be unsupported. Callers must handle `UnsupportedOperationException` as well as `IOException`.
- XAttr names must include a namespace prefix such as `user.`. Validation differences can create compatibility problems with HDFS documentation and CLI behavior.
- Delete-on-exit only runs for clean shutdown or close processing; non-cached filesystems and abnormal termination need explicit cleanup.

## Test Signals

Useful validation for this API surface should include:

- JDiff/API compatibility checks that all fields, classes, constructors, methods, overloads, visibility flags, abstract/static/final markers, exception declarations, and deprecation strings in lines 6041-12112 remain stable.
- Configuration tests that load representative keys from `core-default.xml`, verify deprecated aliases still map as expected, and cover security group cache reload settings, Kerberos relogin/renewal, RPC protection, crypto/key-provider settings, KMS cache/failover, credential fallback, sensitive-key filtering, HTTP idle/log settings, service shutdown, Prometheus, and IPC metrics scheduling.
- `CreateFlag` tests for every documented valid and invalid combination, including path-exists versus path-missing cases and append-specific validation.
- `ContentSummary` tests for constructor compatibility, builder equivalence, getters, equality/hash, headers, quota fields, human-readable formatting, storage-type display, snapshot fields, erasure-coding policy, and `Writable` round trips inherited through the class.
- `FileChecksum` tests for algorithm/length/bytes/checksum option reporting, equality/hash behavior, and filesystem checksum null handling.
- `FileContext` tests for every factory overload, default URI handling, local context creation, working directory legal/illegal forms, prefix-based relative resolution, umask application, path qualification, UGI exposure, and unsupported filesystem failures.
- `FileContext` operation tests for create builder and direct create, mkdir parent behavior, delete recursion, open buffer sizes, truncate true/false completion, replication, rename overwrite semantics, permission/owner/time setters, checksum verify toggles, file/link status, symlink creation/target lookup, list iterators, corrupt block listing, delete-on-exit, statistics, ACLs, xattrs, snapshots, storage policies, server defaults, path capabilities, `openFile`, and multipart uploader creation.
- `FileStatus` tests for all constructors, attribute flag conversion, getters, setters, symlink behavior, path-based compare/equality/hash, deprecated `isDir`, protobuf-backed deprecated read/write compatibility, Java object validation, and copy-constructor behavior.
- `FileSystem` cache tests for `get` versus `newInstance`, cache-disable configuration, user-specific lookup, closeAll/closeAllForUGI lifecycle behavior, local filesystem factories, and behavior after cached instances are closed.
- URI and path tests for default URI get/set, `initialize` superclass requirements, `getScheme` defaults, canonical URI/default port behavior, canonical service name/token integration, deprecated `getName`/`getNamed`, `makeQualified`, and `checkPath` mismatch failures.
- Data operation tests for all visible `open`, `open(PathHandle)`, `getPathHandle`, create overloads, primitive create/mkdir, non-recursive create parent failures, non-atomic `createNewFile`, append overloads including append-to-new-block, concat unsupported/default behavior, replication default behavior, rename option semantics and atomicity expectations, truncate asynchronous completion, recursive delete, exists/isDirectory/isFile/getLength helpers, quota/content summary, listing/globbing/located status, local copy/move helpers, local-output staging, close, used/default block/default replication, and `msync`.
- Metadata tests for symlink support, checksum range and full-file lookups, checksum verification/write flags, filesystem status by root/path, permission/owner/time setters, snapshot lifecycle, ACL merge/remove/replace/status, and xattr set/get behavior at the chunk boundary.

### subset-b-007227: lines 12113-18228

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 12113-18228

## Scope

This chunk is a JDiff API description for Apache Hadoop Common 3.3.6. It is not executable implementation source; it records public and protected API signatures, inheritance, fields, checked exceptions, deprecation state, and Javadoc-derived behavioral contracts. The slice starts inside `org.apache.hadoop.fs.FileSystem` and continues through filesystem utility, stream, path, local filesystem, statistics, quota, capability, and trash APIs under `org.apache.hadoop.fs`.

Because the source is API XML, the "control flow" below is the documented call/delegation flow and object lifecycle promised to callers and implementors.

## Purpose

The chunk captures the central Hadoop filesystem API surface used by clients, filesystem implementors, wrappers, tests, and downstream projects. It documents:

- Extension points for `FileSystem` and its forwarding wrapper `FilterFileSystem`.
- Local filesystem implementations (`LocalFileSystem`, `RawLocalFileSystem`) and file utility helpers (`FileUtil`).
- Stream contracts for seeking, positional reads, vectored reads, buffering, sync/flush, stream capabilities, and IO statistics.
- Builder APIs for input/output stream creation and generic option negotiation.
- Persistent value objects for paths, file status with block locations, quotas, server defaults, filesystem capacity, storage types, path handles, and multipart handles.
- Integration contracts for ACLs, xattrs, snapshots, storage policies, multipart upload, trash handling, and global statistics.

## Important APIs, Types, and Functions

### `FileSystem` tail section

The chunk begins with the extended API tail of `org.apache.hadoop.fs.FileSystem`. It covers ACL/xattr continuations and then documents xattr accessors (`getXAttr`, `getXAttrs`, `listXAttrs`, `removeXAttr`) where names must include a namespace prefix such as `user.attr`; unsupported implementations may throw `UnsupportedOperationException`.

Storage policy methods (`satisfyStoragePolicy`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, `getAllStoragePolicies`) expose HDFS-oriented placement policy controls through the common API. Trash methods (`getTrashRoot`, `getTrashRoots`) define default user trash location behavior, and `hasPathCapability(Path, String)` gives implementors a path-scoped feature probe with a base default of false.

Static discovery/statistics APIs include `getFileSystemClass(scheme, conf)`, which scans service-loaded filesystem implementations and configuration bindings, deprecated synchronized global `Statistics` accessors, `clearStatistics`, `printStatistics`, symlink toggles, `getStorageStatistics`, and `getGlobalStorageStatistics`.

Builder entry points (`createFile`, `appendFile`, `openFile(Path)`, `openFile(PathHandle)`, protected `openFileWithOptions`, and `createMultipartUploader`) define newer extensible creation/open flows. The documented default for `openFileWithOptions` performs a blocking `open(Path, int)` but returns the result in a `CompletableFuture`; subclasses can override for truly asynchronous behavior.

The class doc is a critical integration warning: public/protected API additions must be reflected through `FilterFileSystem`, `ChecksumFileSystem`, and tests such as `TestFilterFileSystem.MustNotImplement` and `TestHarFileSystem`. It also says Hadoop treats HDFS behavior as the normative filesystem contract when Javadocs and specification disagree.

### `FileUtil`

`FileUtil` is a static utility collection for local and cross-filesystem operations. It converts `FileStatus[]` to `Path[]`, recursively deletes files/directories (`fullyDelete`, `fullyDeleteContents`, delete-on-exit registration), reads symlink targets, copies among `FileSystem`, `FileContext`, and `java.io.File`, and writes bytes/text to filesystem paths.

Important platform-sensitive APIs include `makeShellPath`, `makeSecureShellPath`, `symLink`, `chmod`, `setOwner`, `setReadable`, `setWritable`, `setExecutable`, `canRead`, `canWrite`, and `canExecute`. The XML specifically notes Windows differences and symlink privilege return code `SYMLINK_NO_PRIVILEGE`. Archive helpers (`unZip`, `unTar`) and classpath helpers (`createJarWithClassPath`, `getJarsInDirectory`) support process launch and unpacking workflows.

Operational risks in this API include partial deletion/copy results: several methods return false after partial work rather than guaranteeing all-or-nothing behavior, and recursive copy with `deleteSource=true` may delete source subtrees as they are copied.

### `FilterFileSystem`

`FilterFileSystem` wraps a contained `FileSystem` in the protected `fs` field and forwards almost the full `FileSystem` API surface. The chunk lists forwarding for URI qualification, path checking, block locations, open/create/append/concat/delete/rename/truncate, status/listing operations, local copy helpers, working directory, space usage, defaults, ACLs, xattrs, snapshots, symlinks, checksums, permissions/times/owners, storage policies, builder APIs, path capabilities, and trash roots.

This class is a compatibility chokepoint. New methods in `FileSystem` must either be passed through here or deliberately listed as unsupported by tests. The `swapScheme` field indicates wrapper-level URI scheme substitution support. `hasPathCapability` has special documented expectations from `FileSystem`: wrappers must avoid claiming capabilities that the filter cannot safely provide.

### Builder interfaces and constants

`FSBuilder<S, B>` defines `opt` and `must` option setting for string, boolean, int, long, double, and string-array values, plus `build`. The Javadoc records the HADOOP-18724 compatibility problem: overloaded long/double/float variants can bind unexpectedly, so explicit `optLong`, `optDouble`, `mustLong`, and `mustDouble` were added. Older float/double overloads are deprecated or forward through long paths with precision loss. Mandatory options must cause `build()` to throw `IllegalArgumentException` when unsupported.

`FSDataOutputStreamBuilder` extends Hadoop's abstract builder implementation for creating or appending `FSDataOutputStream` objects. It manages permission, buffer size, replication, block size, recursion, progress callbacks, create/overwrite/append flags, checksum options, generic options, and final `build`. The default policy is non-recursive parent creation unless `recursive()` is set.

`FutureDataInputStreamBuilder` specializes builders for asynchronous input stream creation, returning `CompletableFuture<FSDataInputStream>` and accepting an optional `FileStatus` hint via `withFileStatus`.

`FsConstants` provides shared identifiers for local filesystems, FTP, viewfs, maximum symlink resolution count, and viewfs overload patterns.

### Stream and IO APIs

`FSDataInputStream` wraps an `FSInputStream` in a `DataInputStream` and implements a wide set of optional interfaces: `Seekable`, `PositionedReadable`, byte-buffer readable variants, file descriptor access, drop-behind/readahead controls, enhanced byte-buffer access, unbuffering, stream capability probing, and IO statistics. It exposes `seek`, `getPos`, positional `read`, `readFully`, alternate-source seek, byte-buffer reads, buffer release, `unbuffer`, `hasCapability`, IO statistics extraction, and vectored read parameters and execution.

`FSDataOutputStream` wraps `OutputStream` in `DataOutputStream` and implements `Syncable`, `CanSetDropBehind`, `StreamCapabilities`, `IOStatisticsSource`, and `Abortable`. It exposes position, close, capability probing, `hflush`, `hsync`, drop-behind, IO statistics, and abort. `abort` is delegated to the wrapped stream only if it implements `Abortable`; otherwise it raises `UnsupportedOperationException`.

`FSInputStream` is the abstract seekable/positioned base. It requires `seek`, `getPos`, and `seekToNewSource`, supplies positional read/readFully helpers, and offers `validatePositionedReadArgs` to enforce nonnegative positions and buffer bounds. Its `toString` may include subclass IO statistics if implemented.

`Seekable` is the minimal `seek`/`getPos` contract. `PositionedReadable` defines thread-safe positional read and readFully contracts, while warning that not all filesystem implementations satisfy thread safety. Its default vectored-read API reads ranges asynchronously via `FileRange.setData(CompletableFuture)`, may make the post-call stream position undefined, may mix data if the file changes during operation, and may block normal reads during execution.

`StreamCapabilities` standardizes lower-case capability strings for stream features: `hflush`, `hsync`, readahead, drop-behind, unbuffer, byte-buffer reads, positioned byte-buffer reads, IO statistics, vectored IO, abortable streams, and IO statistics context. `StreamCapabilitiesPolicy.unbuffer(InputStream)` centralizes the policy for invoking `CanUnbuffer`.

`Syncable` defines `hflush` for making client-buffered data visible to new readers and `hsync` for fsync-like persistence toward disk, with the exact filesystem semantics delegated to the Hadoop filesystem specification.

### Status, statistics, and quota types

`FsServerDefaults` is a `Writable` value object carrying server default block size, bytes per checksum, write packet size, replication, file buffer size, encryption flag, trash interval, checksum type, key provider URI, and default storage policy ID.

`FsStatus` is a `Writable` capacity snapshot with capacity, used, and remaining byte counters.

`GlobalStorageStatistics` is an enum singleton-style registry with synchronized `get`, `put`, `reset`, and iterator methods over named `StorageStatistics` instances. `StorageStatistics` itself is an abstract per-filesystem or per-context statistics provider with name, optional scheme, long-statistic iterator, `getLong`, `isTracked`, and `reset`. Values need not be a consistent point-in-time snapshot.

`QuotaUsage` stores namespace and storage-space quota usage for directories. It exposes counts, quotas, type-specific quota and consumption by `StorageType`, equality/hash behavior, and CLI-style string/header formatting including human-readable and storage-type modes. Protected setters and builder constructors indicate instances are normally populated by builders or subclasses.

`StorageType` is an enum for storage media. It exposes transient/movable/type-quota support checks, list helpers, parsing by int/string, a default type, and an empty array constant.

### Path, handles, and listing

`Path` is the core serializable, comparable URI-like name for files/directories. Constructors accept parent/child strings, `Path` combinations, raw strings, `URI`, and scheme/authority/path components. Static helpers strip scheme/authority, merge paths while preserving the first path's scheme/authority, and detect Windows absolute drive paths. Instance methods expose URI conversion, filesystem resolution from `Configuration`, absolute/root/name/parent/suffix/depth checks, equality/hash/compare, deprecated `makeQualified(FileSystem)`, and deserialization validation to reject malicious object streams without a URI.

`PathFilter` is the single-method inclusion predicate used by listing/globbing. `GlobFilter` implements it using POSIX glob patterns with brace expansion and can compose with a user filter.

`PathHandle` and `PartHandle` are opaque serializable references represented as byte buffers, with default `toByteArray` and required `bytes`/`equals` methods. `PathHandle` can include enough metadata to validate later path access independent of subsequent filesystem mutations; `InvalidPathHandleException` is thrown when encoded constraints no longer hold. `PartHandle` identifies a multipart upload part.

`PartialListing` represents one page of directory/listing results, or a stored remote exception. Its `get()` behaves like a future result: it returns the list or throws the captured `IOException`. Multiple partial listings may need to be combined for a full directory listing.

`LocatedFileStatus` extends `FileStatus` with block locations. Constructors cover wrapping an existing status, explicit status fields, ACL/encryption/erasure-coded booleans, and attribute flag sets. Equality, ordering, and hash code remain path-based, while `getBlockLocations` warns that HDFS replicated and erasure-coded files may have different `BlockLocation` formats.

### Local filesystem APIs

`LocalFileSystem` extends `ChecksumFileSystem` and represents the checksummed local filesystem. It initializes with a URI/configuration, reports scheme `file`, exposes the raw filesystem, maps `Path` to `File`, handles local copy shortcuts, reports checksum failures by moving files to a bad-file directory on the same device, and supports symlink creation/status/targets.

`RawLocalFileSystem` extends `FileSystem` and implements direct local filesystem operations without checksum wrapping. It provides path-to-file conversion, URI/initialization, `open` by `Path` or `PathHandle`, append/create/createNonRecursive variants, protected output stream creation with optional mode, concat, rename, Windows-specific empty destination directory handling, truncate, delete, unsorted list status based on `File.list()`, existence, mkdir helpers, working directory, status, local output staging, close/toString, file status, owner/permission/time mutation, path handles, symlinks, link status/target, and path capability probing.

The local APIs depend heavily on `java.io.File`, process-level OS commands for owner/permission changes, and platform-specific behavior around Windows permissions, symlinks, ordering, and rename semantics.

### Multipart upload and trash

`MultipartUploader` is a closeable, IO-statistics-capable interface for multipart/cross-node uploads. It uses `CompletableFuture` for `startUpload`, `putPart`, `complete`, `abort`, and best-effort `abortUploadsUnderPath`. Parts may be uploaded in any order or parallel. `putPart` must close the input stream after reading. `complete` accepts a non-empty map of part numbers to part handles and returns a path handle. `abortUploadsUnderPath` may be unsupported (`-1`) and can miss entries with eventually consistent listings.

`Trash` is a configured wrapper around filesystem trash policy. Constructors accept `Configuration` or `(FileSystem, Configuration)`. `moveToAppropriateTrash` resolves symlinks/mount points to move deleted paths into the trash for the actual volume, `isEnabled` reports policy status, `moveToTrash` moves a path when enabled and not already trashed, and this chunk ends at `checkpoint`.

## Control Flow and Lifecycle

The primary documented flows are:

- `FileSystem` discovery: `Path.getFileSystem(conf)` resolves a `FileSystem`; `FileSystem.getFileSystemClass(scheme, conf)` can trigger service loading and configuration lookup for implementations.
- Builder-based open/create: callers obtain builders from `FileSystem.createFile`, `appendFile`, or `openFile`; optional and mandatory options are set on `FSBuilder`; `build()` validates mandatory support and performs the filesystem operation. The default open path routes through `openFileWithOptions`, which by default calls blocking `open(Path, int)` and exposes the result through a `CompletableFuture`.
- Wrapper delegation: `FilterFileSystem` receives caller operations and forwards them to its contained `fs`, preserving behavior unless subclasses override. This makes it the required integration point for any new `FileSystem` method.
- Local file IO: `LocalFileSystem` layers checksum behavior over a raw local filesystem; `RawLocalFileSystem` maps Hadoop `Path` values to `java.io.File` and performs open/create/delete/list/rename/permission operations against the host OS.
- Stream use: input streams support seek, positioned reads, byte-buffer reads, vectored reads, optional unbuffer/readahead/drop-behind, and capability probes. Output streams support position, flush/sync, drop-behind, optional abort, and IO statistics.
- Multipart upload: `startUpload` returns an upload handle, zero or more `putPart` calls produce part handles, `complete` assembles parts into a file and returns a path handle, and `abort` or `abortUploadsUnderPath` cleans up pending uploads.
- Trash flow: delete clients can call `moveToAppropriateTrash`, which resolves the actual volume for symlinks/mount points and then moves content to that volume's trash root if enabled.

## State and Persistence Behavior

Persistent or state-bearing elements include:

- `Path` values are serializable and validate their URI during deserialization.
- `PathHandle` and `PartHandle` serialize opaque byte identifiers and rely on equality semantics supplied by implementations.
- `FileSystem.statistics` is a protected per-instance statistics field, while deprecated global `Statistics` maps and `GlobalStorageStatistics` provide process-wide state. Global registry operations are synchronized.
- `StorageStatistics` values can be reset and may not represent a stable snapshot while iterating.
- `FSDataOutputStream` tracks position and delegates persistence semantics to `hflush`/`hsync`; `hsync` is fsync-like but still subject to device caching.
- `FsStatus`, `FsServerDefaults`, and `QuotaUsage` are value snapshots of capacity/default/quota state, with `FsStatus` and `FsServerDefaults` implementing Hadoop `Writable`.
- `FileUtil.fullyDelete`, `FileUtil.copy`, `RawLocalFileSystem.delete`, `rename`, and `Trash.moveToTrash` mutate filesystem contents and may leave partial state on failure.
- `MultipartUploader` persists temporary upload state between `startUpload`, `putPart`, and `complete`/`abort`; cleanup may be best effort and eventually consistent for some backends.
- `RawLocalFileSystem` maintains working directory state and may use process/OS-level commands for permissions and ownership.

## Dependencies and Integration Points

This API surface depends on Java core IO/NIO/concurrency (`java.io`, `java.net.URI`, `java.nio.ByteBuffer`, `CompletableFuture`, `Iterator`, collections), Hadoop configuration and IPC (`Configuration`, `RemoteException`), Hadoop filesystem types (`Path`, `FileStatus`, `BlockLocation`, `Options`, `PathHandle`, `UploadHandle`, `MultipartUploaderBuilder`), permissions/security (`FsPermission`, `FsAction`, `AclStatus`, `AccessControlException`), checksum and utility types (`DataChecksum.Type`, `Progressable`, `ByteBufferPool`), and statistics (`IOStatistics`, `IOStatisticsSource`).

Key integration points are downstream filesystem implementations, `FilterFileSystem` wrappers, `ChecksumFileSystem`, HDFS-specific behavior, object-store filesystems, viewfs, local OS filesystems, CLI/status formatting, multipart upload implementations, and test suites which enforce method forwarding or unsupported declarations.

## Risks and Edge Cases

- The chunk is generated API XML; it describes contracts but not implementation details. Behavioral research should be reconciled with Java sources before making code changes.
- The source slice starts mid-`FileSystem` and ends mid-`Trash`; adjacent chunks are needed for complete class coverage.
- `FileSystem` API evolution is high risk because wrappers and downstream shims must be updated together.
- `FSBuilder` overloads can silently coerce floating-point values through long paths; callers needing cross-version correctness should pass strings explicitly or use explicit long/double methods.
- `FilterFileSystem` can accidentally over-advertise capabilities if it forwards or claims path capabilities incorrectly.
- Positional-read thread safety is required by contract but explicitly not met by all filesystems; this affects HBase-style consumers.
- Vectored reads have undefined position after completion, undefined results during concurrent file mutation, and may block regular reads.
- Local filesystem behavior varies by platform: Windows symlink privileges, permission bits, execute semantics, path drive handling, `File.list()` ordering, and rename/delete edge cases are all documented hazards.
- Recursive delete/copy utilities and trash/multipart cleanup are not transactional and may leave partially mutated state.
- `GlobalStorageStatistics` and deprecated `FileSystem.Statistics` are process-wide mutable registries; tests must clear/reset to avoid cross-test contamination.
- `StorageStatistics` iterators do not promise point-in-time consistency.
- Multipart aborts under a path are best effort and may miss uploads under eventually consistent listings.

## Test Signals

Useful test coverage implied by this API chunk includes:

- API compatibility/JDiff checks against `Apache_Hadoop_Common_3.3.6.xml` for signature, visibility, exception, field, deprecation, and doc-contract drift.
- `FilterFileSystem` forwarding tests for every new `FileSystem` method, plus negative tests where wrappers must not claim unsupported path capabilities.
- Builder tests for optional vs mandatory options, unsupported mandatory option failures, long/double overload behavior, recursive parent creation, append/create/overwrite flags, checksum options, and asynchronous open futures.
- Stream tests for seek/getPos, positional read preserving current offset, EOF behavior, byte-buffer reads, vectored reads, unbuffer/drop-behind/readahead, capability string lower-casing, abort fallback, and IO statistics exposure.
- Local filesystem tests across Unix and Windows for symlinks, permissions, chmod/chown fallbacks, rename/delete/truncate, unsorted listings, working directory handling, path handles, checksum failure quarantine, and file status for links.
- Value-object serialization and equality tests for `Path`, `PathHandle`, `PartHandle`, `FsStatus`, `FsServerDefaults`, `LocatedFileStatus`, `QuotaUsage`, and storage type parsing.
- Multipart uploader lifecycle tests for out-of-order/parallel parts, input stream closure, complete with non-empty handles, abort, unsupported path-wide abort, and IO statistics availability.
- Trash tests for disabled trash, already-in-trash paths, symlink or mount-point volume resolution, checkpoint behavior in the adjacent chunk, and filesystem-specific trash roots.

### subset-b-007228: lines 18229-24759

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 18229-24759

## Scope

This chunk is a public API snapshot from Hadoop Common 3.3.6 JDiff XML. It begins in the tail of `org.apache.hadoop.fs.Trash`, covers filesystem support APIs (`TrashPolicy`, XAttr codecs, upload handles, audit context, FTP filesystem, IO statistics), HA protocol contracts, and then enters `org.apache.hadoop.io` through the first group of Writable and file-format APIs, ending inside the overloaded `SequenceFile.createWriter(...)` API family. Because the source is API metadata rather than implementation source, the research below focuses on exported contracts, expected control flow, state and persistence surfaces, integration points, risks, and test signals implied by the public signatures and documentation.

## Purpose

The chunk documents several foundational Hadoop Common surfaces:

- Filesystem delete/trash behavior, including pluggable trash policies and path-aware trash directories for HDFS encryption zones.
- Filesystem extension points for unsupported schemes, multipart upload handles, XAttr value encoding, and XAttr create/replace validation.
- Process-wide and thread-local audit context propagated into filesystem audit spans.
- A `FileSystem` implementation backed by Apache Commons Net FTP.
- Low-cost IO statistics contracts, serializable snapshots, metric name constants, and duration/mean aggregation helpers used by object stores and stream implementations.
- HA fencing and service transition protocols used by client-side failover administration.
- Core Hadoop `Writable` building blocks: primitive wrappers, byte arrays, arrays, maps, enum sets, polymorphic object serialization, IO helpers, MD5 hashes, `MapFile`, and the beginning of `SequenceFile` writer creation APIs.

## Important APIs, Types, And Functions

### `org.apache.hadoop.fs`

`Trash` is only partially included here. The visible methods are `expunge()`, `expungeImmediately()`, `getEmptier()`, and `getCurrentTrashDir(Path)`. These expose scheduled and immediate cleanup of trash checkpoints and a superuser-oriented emptier runnable.

`TrashPolicy extends Configured` is the main abstraction for pluggable trash implementations:

- Initialization has a deprecated `initialize(Configuration, FileSystem, Path home)` and the preferred `initialize(Configuration, FileSystem)`. The newer contract avoids assuming trash lives below `/user/$USER`, which matters for HDFS encryption zones where cross-zone rename is disallowed.
- `isEnabled()`, `moveToTrash(Path)`, `createCheckpoint()`, `deleteCheckpoint()`, and `deleteCheckpointsImmediately()` define the lifecycle.
- `getCurrentTrashDir()` is the older pathless API and is explicitly called out as wrong for files deleted from encryption zones. `getCurrentTrashDir(Path)` is the path-aware replacement.
- `getEmptier()` returns a periodic cleanup `Runnable`, intended for the superuser.
- `getInstance(Configuration, FileSystem, Path)` is deprecated in favor of `getInstance(Configuration, FileSystem)`, with both driven by `fs.trash.classname`.
- Protected state includes `fs`, `trash`, and `deletionInterval`.

`UnsupportedFileSystemException` and `UnsupportedMultipartUploaderException` are `IOException` subclasses carrying message-only constructors for unsupported filesystem schemes and unsupported multipart uploaders.

`UploadHandle` is a serializable opaque multipart upload identifier. `bytes()` returns a `ByteBuffer`, `toByteArray()` serializes from that buffer, and implementations must define equality.

`XAttrCodec` encodes and decodes XAttr byte values for shell, HTTP, and JSON surfaces. `decodeValue(String)` accepts hex prefixes `0x`/`0X`, base64 prefixes `0s`/`0S`, quoted text, and unquoted text. `encodeValue(byte[], XAttrCodec)` emits text with quotes, hex with `0x`, or base64 with `0s`.

`XAttrSetFlag` exposes enum values and `validate(String xAttrName, boolean xAttrExists, EnumSet flag)`, the public validation point for create/replace XAttr semantics.

### `org.apache.hadoop.fs.audit.CommonAuditContext`

`CommonAuditContext` is a final context holder for audit attributes shared across all filesystems within a thread and optionally across all threads:

- Per-thread entries: `put(String, String)`, `put(String, Supplier<String>)`, `remove(String)`, `get(String)`, `containsKey(String)`, `reset()`, and `getEvaluatedEntries()`.
- Accessors: `currentAuditContext()` returns the thread-local context; `currentThreadID()` returns a process-unique thread identifier shared across S3A clients on that thread.
- Global entries: `setGlobalContextEntry`, `getGlobalContextEntry`, `removeGlobalContextEntry`, and `getGlobalContextEntries()`.
- `noteEntryPoint(Object)` records the launched tool/application under the audit command parameter when absent.
- `PROCESS_ID` is a process identifier built from UUID and timestamp.

The API explicitly warns that long-lived supplier entries must not capture large object instances, because audit spans retain references to context entries and may be evaluated later in another thread.

### `org.apache.hadoop.fs.ftp`

`FTPException` is a runtime wrapper for FTP failures, with message, cause, and message-plus-cause constructors.

`FTPFileSystem extends FileSystem` exposes Hadoop FS semantics over Apache Commons Net FTP:

- Identification and setup: `getScheme()` returns `ftp`, `getDefaultPort()`, `initialize(URI, Configuration)`, and `getUri()`.
- File operations: `open(Path, int)`, `create(Path, FsPermission, boolean, int, short, long, Progressable)`, `delete(Path, boolean)`, `listStatus(Path)`, `getFileStatus(Path)`, `mkdirs(Path, FsPermission)`, and `rename(Path, Path)`.
- Directory state: `getWorkingDirectory()`, `getHomeDirectory()`, and `setWorkingDirectory(Path)`.
- `append(Path, int, Progressable)` is documented as unsupported.
- Public constants cover buffer size, block size, timeout, config prefixes for FTP user/password/host/port/data connection mode/transfer mode, and the same-directory-only rename error.

The `create` doc warns that its returned stream must be closed before any other API call on the same filesystem instance, or the next invocation may block.

### `org.apache.hadoop.fs.statistics`

`DurationStatisticSummary` is a serializable reporting/test helper over duration metrics. It stores a key, success/failure side, count, min, max, and a cloned `MeanStatistic`. `fetchDurationSummary(IOStatistics, String, boolean)` and `fetchSuccessSummary(IOStatistics, String)` extract summaries from an `IOStatistics` source.

`IOStatistics` defines five metric maps: `counters()`, `gauges()`, `minimums()`, `maximums()`, and `meanStatistics()`. `MIN_UNSET_VALUE` and `MAX_UNSET_VALUE` define unset sentinel values.

`IOStatisticsAggregator` exposes `aggregate(IOStatistics)` and allows full or selective merging. `IOStatisticsSetters` extends `IOStatistics` with simple setters for counters, gauges, minimums, maximums, and means.

`IOStatisticsLogging` is a final static helper for robust stringification/logging. It retrieves statistics from `IOStatistics` or `IOStatisticsSource`, produces compact or sorted pretty strings, builds lazy demand-stringifier objects for log statements, and logs at DEBUG or a named level while catching/downgrading retrieval failures.

`IOStatisticsSnapshot` is final, serializable, and implements `IOStatistics`, `IOStatisticsAggregator`, and `IOStatisticsSetters`. It can be constructed empty or from a source, `clear()` all maps, `snapshot(IOStatistics)` by overwriting current state, `aggregate(IOStatistics)` by synchronized merge, expose synchronized metric maps, and serialize through a static Jackson `JsonSerialization` helper. `requiredSerializationClasses()` exists for safer deserialization of known classes.

`IOStatisticsSupport` provides static helpers for `snapshotIOStatistics(IOStatistics)`, creating empty snapshots, `retrieveIOStatistics(Object)`, and no-op duration tracker singletons.

`MeanStatistic` is a serializable, cloneable sum/sample-count statistic. It protects invalid sample counts by normalizing nonpositive counts to empty state, calculates mean on demand, supports synchronized sample addition and merging, treats all empty statistics as equivalent, and warns that hash code depends on mutable mean/sample state.

`StoreStatisticNames` and `StreamStatisticNames` are public constant catalogs. Store names cover common filesystem operations, object-store requests, multipart upload lifecycle, throttle/rate-limit/retry signals, HTTP method actions, metadata/copy requests, and suffixes for min/max/mean/failure counters. Stream names cover read/write counters, read seek/skip/vector/prefetch/cache metrics, remote stream drain/abort/version mismatch, upload queue/timing/byte counters, and block allocation/release signals.

### `org.apache.hadoop.ha`

Exception types in this chunk include `BadFencingConfigurationException extends IOException`, `FailoverFailedException extends Exception`, `HealthCheckFailedException extends IOException`, and `ServiceFailedException extends IOException`, each with message and message-plus-cause constructors where applicable.

`FenceMethod` is the operator/plugin interface for forcing a target node to stop making progress:

- `checkArgs(String)` validates configured arguments at startup.
- `tryFence(HAServiceTarget, String)` attempts fencing and returns true only for known success. False includes failure or indeterminate results.
- Implementations may also implement `Configurable` for configuration injection.

`HAServiceProtocol` is the RPC contract for HA frameworks:

- `monitorHealth()` performs service-specific health checks and may trigger failover if an active service fails.
- `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(...)`, and `transitionToObserver(...)` request state changes and are no-ops if already in that state.
- `getServiceStatus()` returns `HAServiceStatus`.
- Calls can throw access-control, IO, health-check, or service-transition exceptions.
- `versionID` marks the initial protocol version.

`HAServiceProtocolHelper` wraps HA RPC calls and unwraps `RemoteException` to specific exceptions for monitor and transition methods.

`HAServiceTarget` is an abstract representation of a target node for HA administration. Subclasses provide IPC address, ZKFC address, fencer, and fencing preflight validation. The base class creates service, health-monitor, and ZKFC proxies with timeout/retry parameters, optionally uses a separate health-monitor address, tracks a transition-target HA state, returns fencing parameters for scripts, allows subclasses to add parameters, and advertises whether auto-failover or observer state is supported.

`org.apache.hadoop.ha.protocolPB.HAServiceProtocolPB` and `ZKFCProtocolPB` are protobuf RPC marker interfaces in this chunk.

### `org.apache.hadoop.io` Writable And Utility APIs

`AbstractMapWritable` is a configurable `Writable` base for map-like writables. It keeps per-instance class-to-id mappings rather than static mappings, supports up to 127 distinct classes in a map instance, and serializes those class mappings with the data. `addToMap(Class)` and `copy(Writable)` are synchronized protected helpers.

Array and primitive wrappers:

- `ArrayFile extends MapFile` is a dense file-based mapping from integers to values.
- `ArrayPrimitiveWritable` wraps primitive arrays without copying and provides an optimized wire format.
- `ArrayWritable` serializes homogeneous `Writable[]` values; reducer inputs generally need subclasses that bind a concrete value class.
- `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, and `LongWritable` are `WritableComparable` primitive wrappers with constructors, `set`, `get`, `readFields`, `write`, equality, hash, comparison, and string conversion.
- `BytesWritable extends BinaryComparable` is a resizable byte-sequence key/value. It distinguishes logical length from backing capacity, exposes `copyBytes()` for exact copies and `getBytes()` for direct backing access, deprecates `get()` and `getSize()`, and compares like `memcmp`.
- `BinaryComparable` defines byte-backed ordering through `getBytes()` and `getLength()`, with compare/equality/hash backed by `WritableComparator` byte helpers.

Buffer and close helpers:

- `ByteBufferPool` defines `getBuffer(boolean direct, int length)`, `putBuffer(ByteBuffer)`, and default `release()`.
- `ElasticByteBufferPool` is a synchronized implementation that allocates on demand and caches returned direct or heap buffers, always selecting the smallest cached buffer large enough and deliberately not bounding cache size.
- `org.apache.hadoop.io.Closeable` is deprecated in favor of `java.io.Closeable`.

Serialization wrappers:

- `CompressedWritable` stores data compressed and lazily inflates on field access. Its `readFields` and `write` are final; subclasses implement `readFieldsCompressed` and `writeCompressed`.
- `DataOutputOutputStream` adapts `DataOutput` to `OutputStream`, returning the original object when it already is an `OutputStream`.
- `DefaultStringifier<T>` uses Hadoop `SerializationFactory`, `Serializer`, and `Deserializer` to turn objects into base64 strings. It offers static `store/load` and `storeArray/loadArray` helpers for persisting objects in `Configuration` keys.
- `EnumSetWritable<E extends Enum<E>>` wraps `EnumSet` and requires an explicit element type when the value is null or empty; it also carries configuration.
- `GenericWritable` wraps one of a finite set of `Writable` classes supplied by subclass `getTypes()`.
- `ObjectWritable` serializes a `Writable`, `String`, primitive type, or array along with its declared class name. It has `writeObject` overloads, including `allowCompactArrays`: true for RPC/internal usage and false for inter-cluster, file, and other persisted output where compatibility matters. `readObject` reconstructs instances and `loadClass(Configuration, String)` resolves class names through configuration when available.

IO and file-format helpers:

- `IOUtils` provides stream/channel copy, read/skip fully, compressed-read wrapping, cleanup methods that ignore close failures, socket close, full `ByteBuffer` channel writes, directory listing, file/directory `fsync`, exception wrapping with path/method context, and `readFullyToByteArray(DataInput)` until EOF.
- `MapFile` exposes static `rename`, `delete`, `fix`, and `main`, with `INDEX_FILE_NAME` and `DATA_FILE_NAME` constants.
- `MapWritable extends AbstractMapWritable` implements `Map<Writable,Writable>`-like operations plus `write/readFields`.
- `MD5Hash` is a fixed 16-byte hash `WritableComparable`; it can digest strings, byte arrays, byte ranges, input streams, and MD5 digests, return full digest bytes, half/quarter digests, compare, stringify, and parse/set digest.
- `MultipleIOException` aggregates a list of IOExceptions and can create either a single exception or an aggregate.
- `NullWritable` is a singleton zero-value `WritableComparable` with no serialized data.
- `RawComparator<T>` extends `Comparator<T>` with direct binary `compare(byte[], int, int, byte[], int, int)`.

`SequenceFile` begins here. The visible API includes default compression getters/setters and many `createWriter(...)` overloads. The preferred modern surface is `createWriter(Configuration, Writer.Option...)`; most older overloads taking `FileSystem`, `Path`, key/value classes, compression, codec, progress, metadata, buffer size, replication, and block size are deprecated in favor of options. Non-deprecated compatibility overloads still support explicit `createParent` and `FileContext` plus `CreateFlag`/`CreateOpts`.

## Control Flow

Trash flow is policy-driven. `Trash` delegates deletion/checkpoint/expunge operations to the configured `TrashPolicy`. `TrashPolicy.getInstance(...)` selects a policy class from configuration, initializes it with a filesystem, and subsequent delete flows call `moveToTrash(Path)`. Cleanup flows call `createCheckpoint()`, `deleteCheckpoint()`, `deleteCheckpointsImmediately()`, or schedule `getEmptier()`.

XAttr conversion flow is prefix-driven: decode first inspects the textual prefix or quotes to select hex, base64, or text decoding; encode chooses a representation from the requested `XAttrCodec`. XAttr set flow should call `XAttrSetFlag.validate(...)` before applying create/replace semantics to the filesystem.

Audit flow is split between thread-local and global maps. Filesystem entry points populate the current thread's `CommonAuditContext`, optionally register long-lived global attributes, and audit spans retain the context reference. `getEvaluatedEntries()` later forces any suppliers, potentially in a different thread from where they were registered.

FTP filesystem flow wraps an FTP client under the Hadoop `FileSystem` API. `initialize` derives host/user/password/port and transfer settings from URI/configuration. File streams returned by `open` and `create` must be consumed and closed before other operations on the instance proceed reliably.

IO statistics flow is map-based. Producers expose `IOStatistics` or `IOStatisticsSource`; callers retrieve them through `IOStatisticsSupport`, snapshot them into `IOStatisticsSnapshot`, optionally aggregate multiple sources, and log compact or pretty forms through `IOStatisticsLogging`. Duration summaries derive counts/min/max/mean from a naming convention over the metric maps.

HA control flow is failover-oriented. Admin or failover code builds an `HAServiceTarget`, preflights fencing through `checkFencingConfigured()`, monitors health through `HAServiceProtocol.monitorHealth()`, calls transition methods with `StateChangeRequestInfo`, and invokes configured `FenceMethod` instances in order until one returns success. `HAServiceProtocolHelper` centralizes RPC exception unwrapping.

Writable control flow follows Hadoop's `Writable` binary serialization pattern: default constructor, `readFields(DataInput)` to mutate an empty instance from bytes, and `write(DataOutput)` to persist state. Comparable wrappers add stable sort order. Polymorphic wrappers (`GenericWritable`, `ObjectWritable`, `AbstractMapWritable`) serialize type information so deserialization can instantiate the right class. `IOUtils` operations are procedural helpers around streams/channels and deliberately swallow errors in cleanup variants.

`SequenceFile.createWriter(...)` flow is overloaded compatibility funneling. New code should build a writer through `Writer.Option` values, while old overloads adapt explicit filesystem/path/classes/compression/metadata/storage options into the writer construction path.

## State And Persistence Behavior

`TrashPolicy` holds protected mutable state: the target `FileSystem`, current trash `Path`, and deletion interval. Trash checkpoints are persisted as filesystem directories and renamed/deleted by the policy implementation, while this XML exposes only the abstract lifecycle.

`UploadHandle` instances are opaque but serializable. The exact bytes returned by `bytes()`/`toByteArray()` are a persistence boundary for multipart upload recovery or continuation.

`CommonAuditContext` has JVM-global state and thread-local state. Global context entries apply across all threads and audit spans; thread context is per-thread but audit spans retain references after crossing thread boundaries. Supplier entries are stateful callbacks and can retain captured objects until removed.

`FTPFileSystem` maintains filesystem URI, working directory, connection/client state, and stream lifecycle. Configuration keys persist connection metadata in `Configuration`; FTP itself does not expose Hadoop-style block/replication semantics even though method signatures include those parameters for `FileSystem` compatibility.

`IOStatisticsSnapshot` is explicitly serializable for propagation through frameworks such as Spark and Flink and is annotated for Jackson. It uses concrete sorted map state for counters, gauges, min/max values, and mean statistics. The docs warn against deserializing untrusted Java object streams and provide `requiredSerializationClasses()` for defensive class allowlisting.

`MeanStatistic` stores mutable `samples` and `sum`; mean is computed on demand. Empty state is represented by zero samples and is equivalent regardless of sum. Hash/equality depend on mutable state, so instances are unsafe as hash-map keys after mutation.

`StoreStatisticNames` and `StreamStatisticNames` are constants with no runtime state, but their string values form a compatibility surface for metrics dashboards, tests, and downstream consumers.

Writable classes define persistent binary formats through `write/readFields`. Key persistence surfaces include per-instance class tables in `AbstractMapWritable`, no-copy primitive array storage in `ArrayPrimitiveWritable`, logical length plus capacity in `BytesWritable`, compressed payload caching in `CompressedWritable`, enum element type in `EnumSetWritable`, declared class names in `ObjectWritable`, and MD5 digest bytes in `MD5Hash`.

`DefaultStringifier` persists serialized objects into `Configuration` string values using base64. This makes configuration values dependent on the configured Hadoop serialization framework and the class availability on load.

`MapFile`/`ArrayFile`/`BloomMapFile`-adjacent APIs persist data in filesystem directories with `data` and `index` files; the chunk exposes static maintenance operations rather than reader/writer internals. `SequenceFile` writer APIs create persistent key/value files whose compression type, codec, metadata, replication, block size, and parent creation semantics are caller-controlled.

## Dependencies And Integration Points

Major Hadoop dependencies surfaced here include `Configuration`, `Configured`, `FileSystem`, `FileContext`, `Path`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `FsPermission`, `Options.CreateOpts`, `Progressable`, `RemoteException`, HA service/status/request types, `NodeFencer`, `ZKFCProtocol`, `Writable`, `WritableComparable`, `WritableComparator`, `JsonSerialization`, and Hadoop serialization factories.

Java dependencies include `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `FileChannel`, `WritableByteChannel`, `ByteBuffer`, `Socket`, `URI`, `InetSocketAddress`, `IOException`, `RuntimeException`, collections, `Supplier`, `Serializable`, `Cloneable`, and cryptography `MessageDigest`.

External integration is visible through Apache Commons Net for FTP and Jackson JSON serialization for statistics snapshots. The audit docs explicitly reference S3A clients and hadoop-aws auditing architecture; statistics names also map heavily to object-store operations such as list, PUT, metadata, copy, bulk delete, multipart upload, throttling, retry, and HTTP actions.

Metrics constants are integration contracts for filesystem implementations, stream implementations, logging, tests, and operational dashboards. HA interfaces integrate with RPC protocol PB interfaces, ZooKeeper Failover Controller addresses, fencer implementations, and operator-provided fencing scripts or devices. Writable and SequenceFile APIs integrate with MapReduce, RPC, inter-cluster file interchange, and long-lived on-disk Hadoop data formats.

## Risks And Edge Cases

- The chunk starts mid-class and ends mid-`SequenceFile`, so this research covers only the visible public API segment; adjacent chunks must reconcile full class-level behavior.
- Pathless trash APIs can choose the wrong trash directory for HDFS encryption zones, causing rename failures across zones. New code should prefer `getCurrentTrashDir(Path)` and the newer `initialize(Configuration, FileSystem)` / `getInstance(Configuration, FileSystem)` contracts.
- `TrashPolicy.getInstance` depends on a configured class name. Bad classes, incompatible constructors, or incorrect initialization can break deletion behavior at runtime.
- `moveToTrash(Path)` returns false both when trash is disabled and when a path is already in trash; callers that need diagnostics must distinguish this elsewhere.
- `UploadHandle` equality and byte serialization are implementation-defined. ByteBuffer position/limit handling is a common source of inconsistent `toByteArray()` results if implementations are sloppy.
- `XAttrCodec` must reject malformed hex/base64 cleanly and preserve exact bytes for text encodings. Ambiguous unquoted strings are treated as text, not errors.
- Audit supplier entries can retain large object graphs or evaluate in unexpected threads. Global context entries are shared process-wide and can leak cross-tenant/application metadata in long-lived JVMs if not removed.
- FTP operations are constrained by FTP semantics. Append is unsupported, rename may be limited to the same directory, block size/replication are mostly advisory compatibility parameters, and unclosed create streams can block subsequent operations.
- `IOStatisticsSnapshot.snapshot()` is documented as non-atomic when reading a live source. Concurrent metric mutation can produce internally inconsistent snapshots unless producers provide stronger synchronization.
- `IOStatisticsSnapshot` Java serialization should not be used on untrusted streams. JSON/Jackson deserialization must include the required classes.
- `MeanStatistic` is mutable and hash-code-sensitive; using it as a map key after mutation is unsafe. Arithmetic sum/sample accumulation can also overflow `long`.
- Metric name constants are string compatibility contracts. Renaming or reusing constants breaks dashboards and tests even when Java signatures compile.
- HA fencing can return false for indeterminate results, so failover orchestration must treat non-true as unsafe. Misconfigured fencing parameters or missing superclass `addFencingParameters` delegation can break shell-script fencers.
- Separate health-monitor addresses protect the main RPC handler pool, but incorrect address configuration can make healthy services appear unhealthy.
- Writable binary formats are compatibility-sensitive. `ObjectWritable.writeObject(..., allowCompactArrays=true)` is only for RPC/internal usage; using compact arrays in persisted files can reduce interchange compatibility with other Hadoop versions.
- `AbstractMapWritable` has a per-instance class id range of 1-127. Maps containing too many distinct writable classes can exceed the representable range.
- `ArrayPrimitiveWritable` and `BytesWritable.getBytes()` expose backing storage. Callers can mutate internal state unintentionally or read beyond logical length.
- `ElasticByteBufferPool` intentionally lacks a max cache size, which can retain large heap or direct buffers after bursts.
- Cleanup methods in `IOUtils` ignore failures by design. They are inappropriate when close/fsync failures must be reported to preserve durability guarantees.
- `DefaultStringifier` stores opaque base64 serialized payloads in configuration; changes to serializers or missing classes can make old configuration values unreadable.
- Deprecated `SequenceFile.createWriter` overloads remain source-compatible but should not be expanded in new code; option-based writer creation is the stable direction.

## Test Signals

Focused validation for code touching these APIs should include:

- Trash: policy selection from `fs.trash.classname`, initialization overload behavior, enabled/disabled delete paths, already-in-trash handling, checkpoint creation/deletion, immediate expunge, superuser emptier execution, and encryption-zone path-aware trash directory selection.
- XAttrs: round-trip encode/decode for hex, base64, quoted text, unquoted text, malformed inputs, empty values, and `XAttrSetFlag.validate` create/replace combinations with existing and absent attributes.
- Upload handles: stable byte serialization independent of `ByteBuffer` position, equality/hash behavior for equivalent handles, and Java serialization compatibility if implementations support it.
- Audit context: thread-local isolation, global entry propagation, `noteEntryPoint` idempotence, supplier lazy evaluation, removal of supplier references, `reset()` restoring standard options, and cross-thread span evaluation behavior.
- FTP filesystem: initialization from URI/config keys, default port, login failure, open/create close sequencing, unsupported append, delete recursive/nonrecursive cases, list/status behavior, mkdirs, working directory resolution, home directory, same-directory rename limits, and timeout handling.
- IO statistics: map exposure for all metric classes, unset min/max sentinels, snapshot overwrite semantics, aggregate null handling, synchronized map/setter behavior, JSON round trip, Java serialization allowlist classes, pretty/compact logging output, and no-op duration tracker behavior.
- Mean/duration statistics: empty equivalence, invalid sample normalization, synchronized add/merge/copy, overflow edge cases, mean calculation, mutable hash-code warning, and success/failure duration summary extraction with missing keys.
- Metrics constants: tests that emitted operation and stream metrics use exact expected names for object-store requests, multipart upload, throttling, vector reads, seek/skip, prefetch, cache, and write queue counters.
- HA: fencing argument validation, ordered fencing false/true behavior, runtime `BadFencingConfigurationException`, transition no-op behavior when already in target state, monitor health exception propagation, `RemoteException` unwrapping through helper methods, health monitor address fallback/override, proxy timeouts/retries, fencing parameter map contents, auto-failover flag, and observer support.
- Writables: default-constructor/readFields round trips, write/read compatibility across versions, comparison/equality/hash consistency, backing-array mutation hazards, `BytesWritable` length versus capacity, primitive wrapper ordering, `EnumSetWritable` null/empty element type requirements, `GenericWritable` rejection of unsupported types, and `ObjectWritable` declared-class handling.
- IO utilities: exact-byte copy, count-limited copy, close flag behavior, short channel writes, positioned writes, read/skip fully EOF handling, cleanup swallowing behavior, fsync for files and directories, exception wrapping with path/method context, and `readFullyToByteArray` memory behavior on large inputs.
- File formats: `MapFile.rename/delete/fix` on missing/corrupt index/data files, `MD5Hash` digest sources and string parsing, `MultipleIOException.createIOException` for zero/one/many exceptions, `NullWritable` singleton serialization, `RawComparator` byte-range ordering, and `SequenceFile.createWriter` option-based and legacy overload parity for compression, codec, metadata, parent creation, `FileSystem`, and `FileContext` paths.

### subset-b-007229: lines 24760-31093

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 24760-31093

## Scope

This chunk is the fifth slice of the Hadoop Common 3.3.6 JDiff public API XML. It starts at the end of `org.apache.hadoop.io.SequenceFile`, then covers a large part of the public `org.apache.hadoop.io` serialization surface, the public compression codec/stream contracts under `org.apache.hadoop.io.compress`, erasure coding schema metadata, TFile helper APIs, serializer adapters, a Log4J event counter, and the early metrics2 API through the beginning of `MetricsRegistry`.

The source is generated API metadata rather than implementation code. The research therefore treats classes, methods, fields, docs, exceptions, inheritance, and interface contracts as the authoritative public compatibility surface.

## Purpose

The APIs in this chunk support Hadoop's binary data and observability foundations:

- SequenceFile and Writable APIs define Hadoop's native binary record format, primitive/value wrappers, raw comparators, variable-length integer encoding, and factories used by MapReduce, RPC, SequenceFile, MapFile, and many file formats.
- Compression APIs define how codecs create compressor/decompressor streams, how codec instances are discovered by filename or class name, how codec resources are pooled, and how splittable compression exposes adjusted split boundaries.
- TFile and serializer APIs expose lower-level sorted binary container helpers and pluggable serialization bridges for Java serialization, Writable serialization, and Avro reflection/specific serialization.
- Metrics2 APIs define the public producer/collector/sink contracts used by daemons to emit metrics records, tags, counters, gauges, JSON/string representations, filters, annotations, and a default metrics-system singleton.

## Important APIs, Types, And Functions

### SequenceFile Tail

The chunk opens with deprecated `SequenceFile.createWriter(...)` overloads for constructing writers over a `FileSystem`/`Path` or raw `FSDataOutputStream`, with key/value classes, `CompressionType`, optional `CompressionCodec`, metadata, and optional `Progressable`. The deprecation text directs callers to `createWriter(Configuration, Writer.Option...)`.

`SequenceFile.SYNC_INTERVAL` remains a public constant documenting the default sync-point spacing of 100 KB. The class documentation in this slice is especially important because it fixes the public binary format contract:

- common header fields include magic/version, key class, value class, compression booleans, codec class, metadata, and sync marker;
- uncompressed and record-compressed records store record length, key length, key bytes, and value bytes, with record compression applying only to values;
- block-compressed records group counts, compressed key-length blocks, key blocks, value-length blocks, and value blocks, with sync markers every block;
- key/value lengths in compressed blocks use zero-compressed integer encoding.

### `org.apache.hadoop.io`

This chunk covers core Writable and comparable types:

- `SetFile extends MapFile` is a file-backed key set with a protected constructor.
- `ShortWritable`, `VIntWritable`, and `VLongWritable` are mutable `WritableComparable` wrappers with constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `SortedMapWritable extends AbstractMapWritable implements SortedMap` exposes a Writable sorted map with default/copy constructors, sorted-map views (`firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`, `comparator`) and full map operations plus `readFields`/`write`.
- `Stringifier<T> extends Closeable` converts objects to and from string form through `toString(T)`, `fromString(String)`, and `close`, all allowed to raise `IOException`.
- `Text extends BinaryComparable implements WritableComparable` is Hadoop's mutable UTF-8 string type. It exposes byte ownership and length (`copyBytes`, `getBytes`, `getLength`), UTF-8 character lookup (`charAt`), substring search (`find`), multiple `set` overloads from strings, bytes, and other `Text`, append/clear, serialization helpers, static UTF-8 encode/decode/validate routines, static string read/write helpers with optional max length, `bytesToCodePoint`, `utf8Length`, and `DEFAULT_MAX_LEN`.
- `TwoDArrayWritable` serializes a two-dimensional array of a configured `Writable` value class through `set`, `get`, `toArray`, `readFields`, and `write`.
- `VersionedWritable` writes and reads a version byte around a Writable payload. Subclasses override `getVersion`; `VersionMismatchException` reports expected versus found versions.
- `Writable` is the base binary serialization interface with `write(DataOutput)` and `readFields(DataInput)`. Its docs define the reuse contract: deserialization should overwrite existing object state.
- `WritableComparable<T>` combines `Writable` and `Comparable<T>` for keys that can be serialized and sorted.

Comparator and factory helpers are also public:

- `WritableComparator implements RawComparator, Configurable` provides registry lookup (`get`), registry override (`define`), key construction (`newKey`), object and raw-byte comparison, byte hashing, primitive reads from byte arrays, and variable-length integer reads. Constructors allow key class, configuration, and instance creation behavior.
- `WritableFactories` registers optional `WritableFactory` instances and creates `Writable` objects through registered factories or reflection.
- `WritableFactory` exposes `newInstance()`.
- `WritableUtils` supplies compressed byte-array/string IO, string arrays, cloning through serialization, variable-length integer and long encoding/decoding, range-checked VInt reads, enum read/write, `skipFully`, `toByteArray`, and `readStringSafely`.

### `org.apache.hadoop.io.compress`

The compression package exposes three related layers: codec discovery, codec contracts, and stream/compressor state machines.

Codec discovery and constants:

- `CodecConstants` publishes standard filename extensions for default, bzip2, gzip, lz4, passthrough, snappy, and zstandard codecs.
- `CompressionCodecFactory` is constructed from `Configuration`; it can list and set codec classes, locate codecs by `Path`, full class name, or short name, return codec classes by name, remove suffixes, print via `toString`, and run a command-line `main`. `LOG` is a public logger field.
- `CodecPool` leases compressors/decompressors for a codec, optionally with configuration, returns them, and exposes leased compressor/decompressor counts. This is the public resource-pooling surface for native and Java codec state.

Codec and stream contracts:

- `CompressionCodec` defines output/input stream factories with and without existing `Compressor`/`Decompressor`, factory methods for compressor/decompressor types and instances, and `getDefaultExtension`.
- `SplittableCompressionCodec extends CompressionCodec` adds a split-aware `createInputStream` accepting seekable input, decompressor, start/end offsets, and `READ_MODE`, returning `SplitCompressionInputStream`.
- `DirectDecompressionCodec` and `DirectDecompressor` expose direct-buffer decompression for codecs that can bypass byte-array streams.
- `CompressionInputStream extends InputStream implements Seekable, IOStatisticsSource`; it wraps an input stream, exposes `resetState`, passthrough seek methods, position, optional new-source seeking, IO statistics, and `maxAvailableData`.
- `CompressionOutputStream extends OutputStream implements IOStatisticsSource`; it wraps an output stream and defines `finish`, `resetState`, flush/close/write behavior, and IO statistics.
- `Compressor` accepts input and optional dictionaries, reports input/output byte counts, supports `finish`/`finished`, compresses into caller buffers, resets, ends native resources, and can be reinitialized from `Configuration`.
- `Decompressor` mirrors that state machine for input, dictionaries, finished state, decompression, remaining input, reset, and native-resource cleanup.
- `CompressorStream` and `DecompressorStream` are base stream adapters with protected compressor/decompressor fields, buffers, closed/eof flags, reset/close behavior, and lower-level `compress`/`decompress` hooks.
- `BlockCompressorStream` and `BlockDecompressorStream` adapt compressors into block formats; constructors accept buffer and compression-overhead sizing, and their docs emphasize writing input lengths before compressed payloads.
- `SplitCompressionInputStream` stores adjusted split start/end offsets via setters and getters for codecs that need to align reader boundaries.

Concrete codecs in this slice:

- `DefaultCodec implements Configurable, CompressionCodec, DirectDecompressionCodec` and provides the default deflate-style streams, compressor/decompressor types, direct decompressor creation, and default extension.
- `GzipCodec extends DefaultCodec` overrides stream creation, compressor/decompressor creation and types, direct decompressor creation, and default extension.
- `BZip2Codec implements Configurable, SplittableCompressionCodec`; it supports regular and split-aware input streams, output streams with optional compressors, compressor/decompressor factories, default extension, and `writeHeader`.
- `PassthroughCodec implements Configurable, CompressionCodec`; it publishes `CLASSNAME`, `OPT_EXTENSION`, and `DEFAULT_EXTENSION`, and creates pass-through streams while still presenting the normal codec contract.

### Erasure Coding Metadata

`ECSchema implements Serializable` represents erasure coding policy schema metadata. It can be built from a map or from codec name, data-unit count, parity-unit count, and extra options. Public accessors expose codec name, extra options, number of data units, and parity units. Equality, hash code, and `toString` are part of the compatibility surface. Public map keys are `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.

The chunk also contains package markers for `org.apache.hadoop.io.erasurecode.coder.util` and `org.apache.hadoop.io.erasurecode.grouper` without public classes in this slice.

### TFile And Raw Comparison

`MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are `IOException` subclasses used by TFile metadata operations.

`RawComparable` exposes byte-array comparison material through `buffer()`, `offset()`, and `size()`.

`TFile` publishes compression and comparator names (`COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, `COMPARATOR_MEMCMP`, `COMPARATOR_JCLASS`), builds comparators from comparator names with `makeComparator`, lists supported compression algorithms, and has a command-line `main`.

`org.apache.hadoop.io.file.tfile.Utils` supplies TFile-specific variable-length integer and long encoding, string IO, and binary-search helpers `lowerBound`/`upperBound` over arrays of `RawComparable` or generic objects with comparators.

### Serialization Adapters

`JavaSerialization implements Serialization`, `WritableSerialization extends Configured implements Serialization`, and `AvroSerialization extends Configured implements Serialization` are public adapter classes for Hadoop's serialization plugin layer. Their JDiff entries in this chunk mostly expose constructors and inheritance, so the important surface is compatibility with the broader `Serialization` contract from adjacent chunks.

`JavaSerializationComparator extends DeserializerComparator` exposes a constructor for comparing Java-serialized values.

Avro support includes:

- `AvroReflectSerializable`, a marker interface for types opting into reflect serialization;
- `AvroReflectSerialization extends AvroSerialization` with `AVRO_REFLECT_PACKAGES`, a configuration property for package allow-listing;
- `AvroSpecificSerialization extends AvroSerialization`, for Avro generated/specific records;
- `AvroSerialization.AVRO_SCHEMA_KEY`, the configuration key for schema material.

### Log Metrics

`EventCounter extends org.apache.log4j.AppenderSkeleton` is a Log4J appender for counting logging events. Its public surface is the default constructor, `append(LoggingEvent)`, `close()`, and `requiresLayout()`.

### `org.apache.hadoop.metrics2`

The metrics2 surface in this chunk defines record production, collection, sink delivery, filtering, formatting, and lifecycle control:

- `AbstractMetric implements MetricsInfo`; it wraps metric metadata and exposes `name`, `description`, `info`, numeric `value`, `type`, visitor dispatch through `visit(MetricsVisitor)`, equality, hash code, and `toString`.
- `MetricsInfo` is the metadata interface with `name()` and `description()`.
- `MetricsTag implements MetricsInfo` wraps `MetricsInfo` and a string value; it exposes name/description/info/value and value-based object methods.
- `MetricsVisitor` is a visitor for typed metric values, with `gauge` overloads for int, long, float, and double, and `counter` overloads for int and long.
- `MetricsCollector` creates records by name or `MetricsInfo`, returning `MetricsRecordBuilder`.
- `MetricsRecordBuilder` is a fluent builder for tags, arbitrary metric adds, context, counters, gauges of all primitive numeric widths represented here, parent collector access, and `endRecord`.
- `MetricsRecord` is the immutable record view with timestamp, name, description, context, tags, and iterable metrics.
- `MetricsSource` emits records through `getMetrics(MetricsCollector, boolean all)`.
- `MetricsSink extends MetricsPlugin` receives records through `putMetrics(MetricsRecord)` and flushes buffered output.
- `MetricsPlugin` initializes from `SubsetConfiguration`.
- `MetricsFilter extends MetricsPlugin` exposes four acceptance checks for names, tags, record names, and full records.
- `MetricsSystem implements MetricsSystemMXBean`; it can register and unregister sources/sinks/callbacks, publish metrics immediately, and shut down. The MXBean interface exposes start/stop, start/stop metrics MBeans, and `currentConfig`.
- `MetricsException extends RuntimeException` has constructors for message, cause, and message plus cause.
- `MetricsJsonBuilder extends MetricsRecordBuilder` and `MetricStringBuilder extends MetricsRecordBuilder` format records into JSON or delimited strings while supporting the same tag/counter/gauge builder calls. `MetricStringBuilder` additionally exposes `add(String, Object)` and `tuple(String, Object)`.

Annotations and filters:

- `org.apache.hadoop.metrics2.annotation.Metric` and `Metrics` are annotation interfaces for individual metrics and groups.
- `GlobFilter` and `RegexFilter` extend `AbstractPatternFilter` and compile patterns to `com.google.re2j.Pattern`; GlobFilter is explicitly named as usable from metrics config files.

Metrics2 library classes at the end of the chunk:

- `DefaultMetricsSystem` is a singleton enum facade used by daemon processes. It exposes `initialize(prefix)`, `instance()`, `shutdown()`, `setMiniClusterMode(boolean)`, and `inMiniClusterMode()`, plus enum `values`/`valueOf`.
- `Interns` creates interned `MetricsInfo` and `MetricsTag` instances by metadata/value.
- `MetricsRegistry` starts in this chunk. It is constructed from a record name or `MetricsInfo`, exposes registry `info`, synchronized `get` and `getTag`, and creates mutable counters/gauges/stats/rates/quantiles through `newCounter`, `newGauge`, `newQuantiles`, `newStat`, and `newRate` overloads.

## Control Flow

Writable control flow is object-reuse oriented. Callers allocate a `Writable`, then repeatedly call `readFields(DataInput)` to overwrite its existing state; writers call `write(DataOutput)` to emit the current state. `VersionedWritable` adds a version byte before subclass fields and raises `VersionMismatchException` when the serialized version does not match the expected one.

`Text` control flow is byte-buffer based rather than Java `String` based. Mutators replace or append UTF-8 byte content, `charAt` and `find` scan encoded bytes, static helpers encode/decode and validate UTF-8, and bounded `readString`/`readStringSafely` protect callers from oversized serialized strings.

Raw sorting flow uses `WritableComparator`: comparators can be looked up from the static registry, constructed for a key class, and used either on already-deserialized `WritableComparable` objects or directly on serialized byte ranges. The primitive byte readers and VInt readers are support routines for comparator implementations that avoid object allocation.

Compression flow is stream and state-machine driven. A codec creates a compressor/decompressor or receives one leased from `CodecPool`; it wraps caller streams in `CompressionOutputStream` or `CompressionInputStream`; callers feed bytes through stream methods; `finish`, `finished`, `resetState`, `reset`, and `end` separate flush/completion, reuse, and native-resource cleanup. Split-aware codecs additionally adjust start/end offsets through `SplitCompressionInputStream` so distributed readers can begin at codec-safe boundaries.

Codec discovery flow starts with a `Configuration`-backed `CompressionCodecFactory`, resolves a codec from a path suffix or configured codec name/class, then optionally strips suffixes through `removeSuffix`. TFile and SequenceFile consumers depend on these discovery and extension contracts to choose readers/writers.

Metrics flow begins when sources are registered with `MetricsSystem` or `DefaultMetricsSystem`. A collector asks a `MetricsSource` for metrics; sources build one or more records through `MetricsRecordBuilder`; records carry tags and `AbstractMetric` values; sinks receive immutable `MetricsRecord` instances and flush them. Visitors and JSON/string builders provide alternate render paths. Filters accept or reject names, tags, or records before delivery.

## State And Persistence Behavior

SequenceFile, Writable, TFile, and compression streams are persistence-facing APIs. SequenceFile's documented header and record layouts are durable on-disk compatibility contracts. Writable implementations persist their fields directly to `DataOutput` and restore them from `DataInput`; changing field order, encoding, or comparator behavior breaks stored data and shuffle/sort compatibility.

Primitive Writable wrappers hold one mutable primitive value. `SortedMapWritable` persists both map content and the class-id mapping inherited from `AbstractMapWritable`. `TwoDArrayWritable` persists array dimensions and nested Writable values. `Text` maintains a mutable UTF-8 byte array and length; `getBytes()` exposes internal storage while `copyBytes()` returns a defensive copy.

`WritableFactories` and `WritableComparator` maintain process-wide registries. Factory/comparator registration changes object construction and sort behavior globally for a class, so tests and long-running daemons must avoid accidental cross-test or cross-component leakage.

Compression classes keep mutable native or heap state in compressors, decompressors, stream buffers, closed/eof flags, counters, configuration references, and codec-pool lease tables. `CodecPool` explicitly tracks leased compressors and decompressors, making failure to return resources observable through leased-count methods and potentially expensive for native codecs.

`ECSchema` is serializable metadata state: codec name, data/parity unit counts, and extra options. It is likely persisted in erasure coding policy metadata outside this XML slice, so equality and key names are compatibility-sensitive.

Metrics2 state is mostly runtime state. `MetricsRegistry` owns mutable metric and tag registries; `DefaultMetricsSystem` owns the singleton metrics system and mini-cluster mode flag; `MetricsSystem` owns registered sources, sinks, and callbacks. Metrics records are snapshots for delivery, while builders and mutable metrics are transient construction/update surfaces.

## Dependencies And Integration Points

The `org.apache.hadoop.io` APIs depend on Java IO (`DataInput`, `DataOutput`, `IOException`), Hadoop configuration, filesystem streams, `Progressable`, compression codecs, and comparator/factory registries. These APIs integrate with SequenceFile, MapFile/SetFile, TFile, MapReduce key sorting, shuffle serialization, RPC payloads, and many configuration-serialized values.

Compression APIs integrate with `Configuration`, `Path`, `Seekable`, `IOStatisticsSource`, native codec implementations, direct byte buffers, split readers, SequenceFile block/record compression, MapReduce input splitting, and TFile compression selection. `BZip2Codec` is notable because it is splittable; gzip/default codecs are normal stream codecs, with default/gzip also exposing direct decompression hooks.

Serializer adapters integrate with Hadoop's `Serialization` framework, `Configured`, Java object serialization, Writable types, and Avro reflection/specific record handling. The Avro classes depend on configuration keys to choose schema and package eligibility.

Metrics2 integrates with Apache Commons Configuration (`SubsetConfiguration`), Log4J for `EventCounter`, SLF4J loggers in formatting/factory classes, RE2J pattern compilation in filters, JMX through `MetricsSystemMXBean`, daemon startup through `DefaultMetricsSystem.initialize`, and downstream sinks configured by the metrics system.

## Risks And Compatibility Notes

- The deprecated `SequenceFile.createWriter` overloads remain public and can still be used by older callers. Compatibility must preserve their behavior while nudging new code to `Writer.Option` APIs.
- SequenceFile format details in this XML are durable. Any mismatch in sync interval, header fields, compression flags, metadata encoding, or block layout can strand existing files.
- `Text.getBytes()` exposes the backing byte array. Callers must use `getLength()` and avoid assuming unused capacity is valid string data.
- Variable-length integer encoding in `WritableUtils`, `WritableComparator`, and TFile `Utils` is shared wire-format logic. Small arithmetic changes can break deserialization, raw comparison, and binary search ordering.
- `WritableComparator.define` and `WritableFactories.setFactory` mutate global registries. Tests and embedded runtimes can become order-dependent if registrations are not isolated.
- Compression resources may hold native memory. `Compressor.end`, `Decompressor.end`, stream `close`, and `CodecPool.returnCompressor`/`returnDecompressor` are operationally significant, not just cleanup niceties.
- Split compression is contract-sensitive: incorrect adjusted start/end offsets can duplicate or drop records in distributed reads.
- `CodecPool` leased counts are a direct signal for leaks; resource leaks may not show as Java heap growth if native codec buffers are involved.
- Metrics2 builders use fluent no-op/default-style base classes in parts of the API; custom builders/sinks must implement all relevant overloads or silently lose values of some numeric type.
- `DefaultMetricsSystem` is global singleton state. Mini-cluster mode and shutdown behavior can leak between tests or embedded clusters if not reset.
- Pattern filters use RE2J, not Java's regex engine, so syntax/performance behavior follows RE2J semantics.

## Test Signals

Useful validation for code touching APIs represented by this chunk includes:

- SequenceFile round trips for uncompressed, record-compressed, and block-compressed files, including metadata, sync seeking, and old deprecated writer overloads.
- Writable serialization/deserialization compatibility tests for `ShortWritable`, `VIntWritable`, `VLongWritable`, `Text`, `SortedMapWritable`, `TwoDArrayWritable`, and `VersionedWritable` mismatch handling.
- Raw comparator tests that compare serialized byte ranges against object-level comparison for representative key classes and VInt/VLong encodings.
- Factory and comparator registry tests that verify explicit registration, default reflective construction, and isolation/reset behavior in test suites.
- Compression codec tests for stream round trips, `finish` versus `close`, reset/reuse, direct decompression, codec discovery by suffix/name/class, `CodecPool` lease counts returning to zero, and BZip2 split-boundary correctness.
- TFile utility tests for VInt/VLong encoding, string IO, comparator construction, and lower/upper-bound behavior with raw and object comparators.
- Serialization plugin tests for Java, Writable, and Avro reflect/specific serializers under configured schema/package settings.
- Metrics2 tests for source registration, immediate publish, record building with all counter/gauge numeric overloads, tag propagation, sink flush, filter acceptance/rejection, JSON/string output, singleton shutdown, and mini-cluster mode behavior.

### subset-b-007230: lines 31094-37159

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 31094-37159

## Scope

This chunk is a large portion of the Hadoop Common 3.3.6 JDiff public API XML. It starts inside `org.apache.hadoop.metrics2.lib.MetricsRegistry`, covers mutable metrics, metrics sinks and utilities, network mapping/socket APIs, security identity and token APIs, HTTP security filters, delegation-token web clients, and service lifecycle classes. It ends inside the `org.apache.hadoop.service.Service.waitForServiceToStop(long)` documentation; `Service.getLifecycleHistory()`, `Service.getBlockers()`, and following `ServiceOperations` APIs are outside this chunk.

Because the source is JDiff XML rather than executable Java, the research below focuses on exposed API contracts, state surfaces implied by public fields/methods, control-flow contracts documented in Javadocs, integration points, compatibility risks, and likely test signals.

## Purpose

The chunk captures public contracts for several Hadoop Common cross-cutting subsystems:

- Metrics production and export: mutable counters, gauges, rates, quantiles, rolling averages, metric registries, JMX MBean helpers, cache utilities, and sinks for files, rolling filesystems, Graphite, and StatsD.
- Network topology and sockets: DNS-to-rack/switch mappings, cache wrappers, script/table based mapping, and standard/SOCKS socket factories.
- Security primitives: credentials, user/group identity, Kerberos helpers, ACLs, impersonation providers, credential providers, token identifiers, token renewal, and delegation-token HTTP clients.
- HTTP hardening filters: REST CSRF prevention and X-Frame-Options insertion for servlet filters.
- Service lifecycle management: abstract service state transitions, composite child service coordination, lifecycle events, state-change logging, and the core `Service` interface up to stop-waiting semantics.

The common theme is public framework API. These types are intended to be used by HDFS, YARN, MapReduce, command-line tools, RPC clients/servers, web services, and pluggable Hadoop deployments rather than by a single feature.

## Important APIs, Types, And Functions

### Metrics Registry And Mutable Metrics

The chunk begins with the tail of `MetricsRegistry`, whose methods create and manage mutable metrics and tags:

- `newRate(name)`, `newRate(name, description)`, and `newRate(name, desc, extended)` create `MutableRate` metrics; the extended flag requests additional statistics such as min/max/stdev.
- `newRatesWithAggregation(name)` and `newMutableRollingAverages(name, valueName)` create aggregate rate/rolling-average helpers.
- `add(name, value)` adds a sample to a stat metric by metric name.
- `setContext(name)` writes the metrics context tag and returns the registry for chaining.
- `tag(...)` overloads add string tags by name/description/value or by `MetricsInfo`, with optional override behavior.
- `snapshot(MetricsRecordBuilder, boolean all)` emits all contained mutable metrics to a record builder, optionally including unchanged values.

The mutable metric family is centered on `MutableMetric`, an abstract base with `snapshot(builder, all)`, convenience `snapshot(builder)`, protected `setChanged()`/`clearChanged()`, and `changed()`. This establishes the common changed-since-last-snapshot contract.

Counter and gauge APIs split by monotonic-vs-arbitrary and int-vs-long storage:

- `MutableCounter` is abstract, stores `MetricsInfo`, and requires `incr()`.
- `MutableCounterInt` and `MutableCounterLong` provide `incr()`, delta overloads, `value()`, and `snapshot(...)`. `MutableCounterLong` has a public `(MetricsInfo, long)` constructor.
- `MutableGauge` is abstract, stores `MetricsInfo`, and requires `incr()` plus `decr()`.
- `MutableGaugeInt` and `MutableGaugeLong` provide `value()`, increment/decrement delta overloads, `set(value)`, `snapshot(...)`, and `toString()`.

Statistical metrics include:

- `MutableStat`, constructed from metric name/description/sample name/value name and optional extended flag. It supports `setExtended(boolean)`, `setUpdateTimeStamp(boolean)`, sample addition through `add(numSamples, sum)` and `add(value)`, `snapshot(...)`, `lastStat()`, `resetMinMax()`, `getSnapshotTimeStamp()`, and `toString()`.
- `MutableRate extends MutableStat` and exposes the rate-metric specialization.
- `MutableQuantiles`, constructed with name/description/sample name/value name/interval, supports `add(long)`, `snapshot(...)`, `getInterval()`, `stop()`, `getEstimator()`, and `setEstimator(...)`. It publishes protected `quantiles` and `previousSnapshot` fields.
- `MutableRates` and `MutableRatesWithAggregation` dynamically manage rate metrics by operation or method name. Their `init(...)`, `add(name, elapsed)`, and `snapshot(...)` APIs support reflective initialization and aggregation.
- `MutableRollingAverages implements Closeable`; it supports `add(name, value)`, `snapshot(...)`, `collectThreadLocalStates()`, `getStats(long minSamples)`, `setRecordValidityMs(long)`, and `close()`.

### Metrics Sinks And Utilities

The sink classes implement `MetricsSink` and generally `Closeable`:

- `FileSink` initializes from `SubsetConfiguration`, writes metrics records with `putMetrics(MetricsRecord)`, supports `flush()`, and closes resources.
- `GraphiteSink` has the same sink lifecycle and writes records to a Graphite endpoint.
- `StatsDSink` initializes, writes records, has a protected/public `writeMetric(String, String, String, String)` style helper in the API, flushes, and closes.
- `RollingFileSystemSink` writes metrics to rolling files under a Hadoop `Path`. It exposes default and `(long, long)` constructors, `init(...)`, `getRollInterval()`, `updateFlushTime(Calendar)`, `setInitialFlushTime(Date)`, `putMetrics(...)`, `flush()`, and `close()`.

`RollingFileSystemSink` has a broad state surface in protected/public fields: `source`, `ignoreError`, `allowAppend`, `basePath`, `rollIntervalMillis`, `rollOffsetIntervalMillis`, `nextFlush`, `forceFlush`, `hasFlushed`, `suppliedConf`, and `suppliedFilesystem`. That makes subclass or test behavior sensitive to field naming and type compatibility.

Metrics utility APIs include:

- `MBeans.register(serviceName, nameName, mbean)` and an overload with an additional `Map<String,String>` of properties; `getMbeanNameService(ObjectName)`, `getMbeanNameName(ObjectName)`, and `unregister(ObjectName)`.
- `MetricsCache`, with default and size-limited constructors, `update(MetricsRecord, boolean includingTags)`, `update(MetricsRecord)`, and `get(String name, Collection<MetricsTag> tags)`. It exposes cached `Record` objects through API signatures.
- `Servers.parse(String specs, int defaultPort)` returns a list of server socket addresses from a comma-delimited host/port-like spec.

### Network Mapping And Socket APIs

`DNSToSwitchMapping` is the rack/switch resolution interface. It defines `resolve(List<String> names)`, `reloadCachedMappings()`, and `reloadCachedMappings(List<String> names)`.

`AbstractDNSToSwitchMapping implements DNSToSwitchMapping, Configurable` and adds configuration handling plus topology inspection helpers:

- constructors with no args or `Configuration`;
- `getConf()` / `setConf(Configuration)`;
- `isSingleSwitch()`;
- `getSwitchMap()`;
- `dumpTopology()`;
- static/utility style policy helpers `isSingleSwitchByScriptPolicy()` and `isMappingSingleSwitch(DNSToSwitchMapping)`.

Concrete wrappers and implementations:

- `CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping`, caches name-to-switch results, supports cache reloads for all or selected names, exposes `getSwitchMap()`, `isSingleSwitch()`, `toString()`, and a protected `rawMapping` field.
- `ScriptBasedMapping` extends the cached wrapper, provides constructors from no args, raw mapping, or configuration, exposes `NO_SCRIPT`, and updates the underlying script mapping through `setConf`.
- `TableMapping` extends the cached wrapper and is configuration-driven; `reloadCachedMappings()` refreshes table-derived mappings.
- `ConnectTimeoutException extends SocketTimeoutException` gives Hadoop a named connect-timeout exception type.

Socket factories:

- `SocksSocketFactory extends SocketFactory implements Configurable` supports creation from no args or a `Proxy`, all five `SocketFactory.createSocket(...)` overloads, equality/hash code, and configuration handling. Its configuration determines the SOCKS proxy.
- `StandardSocketFactory extends SocketFactory` exposes the same five `createSocket(...)` overloads plus equality/hash code for ordinary sockets.

### Credentials, Group/ID Mapping, And Kerberos Helpers

`AccessControlException extends IOException` provides empty, message, and throwable constructors for authorization/access failures.

`Credentials implements Writable` stores token aliases and secret keys in memory and serializes them:

- construction from empty state or copy;
- token access through `getToken(Text)`, `addToken(Text, Token)`, `getAllTokens()`, `getTokenMap()`, and `numberOfTokens()`;
- secret-key access through `getSecretKey(Text)`, `numberOfSecretKeys()`, `addSecretKey(Text, byte[])`, `removeSecretKey(Text)`, `getAllSecretKeys()`, and `getSecretKeyMap()`;
- token-storage IO through `readTokenStorageFile(Path, Configuration)`, `readTokenStorageFile(File, Configuration)`, `readTokenStorageStream(DataInputStream)`, `writeTokenStorageToStream(DataOutputStream)`, `writeTokenStorageToStream(DataOutputStream, SerializedFormat)`, `writeTokenStorageFile(Path, Configuration)`, and `writeTokenStorageFile(Path, Configuration, SerializedFormat)`;
- `write(DataOutput)`, `readFields(DataInput)`, `addAll(Credentials)`, and `mergeAll(Credentials)`.

`GroupMappingServiceProvider` defines pluggable group lookup with `getGroups(String user)`, `cacheGroupsRefresh()`, `cacheGroupsAdd(List<String>)`, and `GROUP_MAPPING_CONFIG_PREFIX`.

`IdMappingServiceProvider` defines user/group ID mapping: `getUid(user)`, `getGid(group)`, `getUserName(uid, unknown)`, `getGroupName(gid, unknown)`, `getUidAllowingUnknown(user)`, and `getGidAllowingUnknown(group)`.

`KerberosAuthException extends IOException` enriches authentication failures with optional user, principal, keytab, ticket cache, and initial message. It has setters, getters, and an overridden `getMessage()` to include context.

`SecurityUtil` is a static helper surface for Kerberos, token service names, privileged execution, protocol annotations, and ZooKeeper auth:

- global setup: `setConfiguration(Configuration)`;
- Kerberos principal helpers: `isOriginalTGT(KerberosTicket)`, `getServerPrincipal(String, String)`, `getServerPrincipal(String, InetAddress)`, and `getHostFromPrincipal(String)`;
- login helpers: `login(Configuration, keytabKey, userNameKey)` and overload with explicit hostname;
- delegation-token service helpers: `buildDTServiceName(URI, int)`, `getTokenServiceAddr(Token)`, `setTokenService(Token, InetSocketAddress)`, and `buildTokenService(...)` overloads for address and URI;
- protocol metadata: `getKerberosInfo(Class, Configuration)`, `getClientPrincipal(Class, Configuration)`, and `getTokenInfo(Class, Configuration)`;
- privileged execution: `doAsLoginUserOrFatal(PrivilegedAction<T>)`, `doAsLoginUser(PrivilegedExceptionAction<T>)`, and `doAsCurrentUser(PrivilegedExceptionAction<T>)`;
- auth-method config: `getAuthenticationMethod(Configuration)`, `setAuthenticationMethod(AuthenticationMethod, Configuration)`;
- utility checks: `isPrivilegedPort(int)` and `getZKAuthInfos(Configuration, String)`;
- fields include `LOG`, `HOSTNAME_PATTERN`, and `FAILED_TO_GET_UGI_MSG_HEADER`.

### UserGroupInformation

`UserGroupInformation` is the public identity and subject wrapper for Hadoop. The XML exposes static process configuration, login state, user creation, token/credential management, group lookup, authentication method state, and privileged execution:

- test and metrics hooks: `setShouldRenewImmediatelyForTests(boolean)` and `reattachMetrics()`;
- global configuration and status: `isInitialized()`, `setConfiguration(Configuration)`, `isSecurityEnabled()`, and `hasKerberosCredentials()`;
- user discovery: `getCurrentUser()`, `getBestUGI(ticketCachePath, user)`, `getUGIFromTicketCache(ticketCache, user)`, `getUGIFromSubject(Subject)`, `getLoginUser()`, and `trimLoginMethod(String)`;
- login lifecycle: `loginUserFromSubject(Subject)`, `isFromKeytab()`, `loginUserFromKeytab(user, path)`, `logoutUserFromKeytab()`, `checkTGTAndReloginFromKeytab()`, `reloginFromKeytab()`, `forceReloginFromKeytab()`, `reloginFromTicketCache()`, `loginUserFromKeytabAndReturnUGI(user, path)`, `isLoginKeytabBased()`, and `isLoginTicketBased()`;
- identity creation: `createRemoteUser(user)`, `createRemoteUser(user, AuthMethod)`, `createProxyUser(user, realUser)`, `createUserForTesting(user, groups)`, and `createProxyUserForTesting(user, realUser, groups)`;
- proxy identity inspection: `getRealUser()` and `getRealUserOrSelf(UserGroupInformation)`;
- names and groups: `getShortUserName()`, `getPrimaryGroupName()`, `getUserName()`, `getGroupNames()`, and `getGroups()`;
- token and credential handling: `addTokenIdentifier(TokenIdentifier)`, `getTokenIdentifiers()`, `addToken(Token)`, `addToken(Text, Token)`, `getTokens()`, `getCredentials()`, and `addCredentials(Credentials)`;
- auth method state: `setAuthenticationMethod(AuthenticationMethod)`, `setAuthenticationMethod(SaslRpcServer.AuthMethod)`, `getAuthenticationMethod()`, `getRealAuthenticationMethod()`, and static `getRealAuthenticationMethod(ugi)`;
- subject behavior: `equals(Object)`, `hashCode()`, `getSubject()`, `doAs(PrivilegedAction<T>)`, `doAs(PrivilegedExceptionAction<T>)`, `logAllUserInfo(ugi)`, and `main(String[])`.

`UserGroupInformation.AuthenticationMethod` is an enum-like nested type with `values()`, `valueOf(String)`, `getAuthMethod()`, and `valueOf(SaslRpcServer.AuthMethod)`. `HADOOP_TOKEN_FILE_LOCATION` and `HADOOP_TOKEN` are public environment variable names for token-file and base64-token ingestion.

### Credential Providers And Authorization

`CredentialProvider` is the abstract credential-store contract. It exposes `isTransient()`, `flush()`, `getCredentialEntry(alias)`, `getAliases()`, `createCredentialEntry(alias, credential)`, `deleteCredentialEntry(alias)`, `needsPassword()`, `noPasswordWarning()`, and `noPasswordError()`. The `CLEAR_TEXT_FALLBACK` field names the clear-text fallback behavior/config key.

`CredentialProviderFactory` constructs providers from a URI-like provider path. It exposes `createProvider(URI, Configuration)`, `getProviders(Configuration)`, and `CREDENTIAL_PROVIDER_PATH`.

`AccessControlList implements Writable` models user/group ACL strings:

- constructors from no args, ACL string, or user/group strings;
- mutation and inspection: `isAllAllowed()`, `addUser()`, `addGroup()`, `removeUser()`, `removeGroup()`, `getUsers()`, `getGroups()`, `isUserInList()`, `isUserAllowed(UserGroupInformation)`, `toString()`, and `getAclString()`;
- serialization: `write(DataOutput)` and `readFields(DataInput)`;
- public constants: `WILDCARD_ACL_VALUE` and `USE_REAL_ACLS`.

`AuthorizationException extends AccessControlException` has constructors matching message/throwable use cases and overrides stack-trace access/printing methods. That API suggests a lightweight or intentionally stackless authorization failure surface.

`ImpersonationProvider extends Configurable` authorizes proxy users through `init(String configurationPrefix)`, `authorize(UserGroupInformation user, InetAddress remoteAddress)`, and an overload accepting a `String` remote address. `DefaultImpersonationProvider` implements it with config-backed proxy group/host maps and helper methods for derived config keys:

- `getTestProvider()`;
- `setConf()` / `getConf()`;
- `init(prefix)`;
- `authorize(...)`;
- `getProxySuperuserUserConfKey(user)`, `getProxySuperuserGroupConfKey(user)`, and `getProxySuperuserIpConfKey(user)`;
- `getProxyGroups()` and `getProxyHosts()`.

### HTTP Security Filters

`RestCsrfPreventionFilter implements javax.servlet.Filter` and exposes:

- servlet lifecycle: `init(FilterConfig)`, `doFilter(ServletRequest, ServletResponse, FilterChain)`, and `destroy()`;
- policy hooks: `isBrowser(String userAgent)` and `handleHttpInteraction(HttpInteraction)`;
- `getFilterParams(Configuration, String prefix)` for extracting filter configuration;
- public field names for headers and parameters: `HEADER_USER_AGENT`, `BROWSER_USER_AGENT_PARAM`, `CUSTOM_HEADER_PARAM`, `CUSTOM_METHODS_TO_IGNORE_PARAM`, and `HEADER_DEFAULT`.

`XFrameOptionsFilter implements Filter` and exposes `init`, `doFilter`, `destroy`, `getFilterParams(Configuration, String prefix)`, and fields `X_FRAME_OPTIONS` plus `CUSTOM_HEADER_PARAM`.

### Tokens And Secret Managers

`SecretManager<T extends TokenIdentifier>` is the server-side token-secret abstraction:

- abstract/overridable token methods: `createPassword(T identifier)`, `retrievePassword(T identifier)`, `retriableRetrievePassword(T identifier)`, `createIdentifier()`, and `checkAvailableForRead()`;
- cryptographic helpers: `generateSecret()`, static-like `createPassword(byte[] identifier, SecretKey key)`, and `createSecretKey(byte[] key)`;
- failure modes include `SecretManager.InvalidToken`, `StandbyException`, `RetriableException`, and `IOException`.

`Token<T extends TokenIdentifier> implements Writable` is the client-side token form:

- constructors from `(identifier, secretManager)`, raw components `(identifier bytes, password bytes, kind, service)`, empty state, or copy;
- mutators/accessors: `setID(byte[])`, `setPassword(byte[])`, `copyToken()`, `getIdentifier()`, `decodeIdentifier()`, `getPassword()`, `getKind()`, `getService()`, and `setService(Text)`;
- privacy/aliasing: `isPrivate()`, `isPrivateCloneOf(Text publicService)`, and `privateClone(Text newService)`;
- serialization and string encoding: `readFields(DataInput)`, `write(DataOutput)`, `encodeToUrlString()`, and `decodeFromUrlString(String)`;
- identity and cache behavior: `equals(Object)`, `hashCode()`, `toString()`, and `buildCacheKey()`;
- lifecycle through renewers: `isManaged()`, `renew(Configuration)`, and `cancel(Configuration)`;
- public `LOG`.

`Token.TrivialRenewer extends TokenRenewer` is for token kinds that are not managed. It exposes `getKind()`, `handleKind(Text)`, `isManaged(Token)`, `renew(Token, Configuration)`, and `cancel(Token, Configuration)`.

`TokenIdentifier implements Writable` is the public identifier contract with `getKind()`, `getUser()`, `getBytes()`, and `getTrackingId()`.

`TokenInfo` is an annotation type marking protocol token metadata. `TokenRenewer` is the plugin interface for token kinds with `handleKind(Text)`, `isManaged(Token)`, `renew(Token, Configuration)`, and `cancel(Token, Configuration)`. `TokenSelector<T extends TokenIdentifier>` selects an appropriate token from a collection by service.

### Delegation-Token Web Client APIs

`DelegationTokenAuthenticatedURL extends AuthenticatedURL` wraps HTTP authentication with delegation-token operations:

- constructors accept defaults, a `DelegationTokenAuthenticator`, a `ConnectionConfigurator`, or both.
- static/default behavior: `setDefaultDelegationTokenAuthenticator(Class)`, `getDefaultDelegationTokenAuthenticator()`, `setUseQueryStringForDelegationToken(boolean)`, and `useQueryStringForDelegationToken()`.
- authenticated connections: `openConnection(URL, AuthenticatedURL.Token)`, `openConnection(URL, DelegationTokenAuthenticatedURL.Token)`, and overload with `doAs`.
- token operations: `getDelegationToken(URL, Token, renewer)`, overload with `doAsUser`, `renewDelegationToken(URL, Token)`, overload with `doAsUser`, `cancelDelegationToken(URL, Token)`, and overload with `doAsUser`.

`DelegationTokenAuthenticatedURL.Token extends AuthenticatedURL.Token` stores an optional Hadoop delegation `Token` via `getDelegationToken()` and `setDelegationToken(Token)`.

`DelegationTokenAuthenticator implements Authenticator` wraps another authenticator and adds REST-style delegation token operations:

- constructor from an underlying `Authenticator`;
- `setConnectionConfigurator(ConnectionConfigurator)`;
- `authenticate(URL, AuthenticatedURL.Token)`;
- `getDelegationToken(...)`, `renewDelegationToken(...)`, and `cancelDelegationToken(...)` overloads with optional `doAsUser`;
- protocol constant fields including `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `DELEGATION_PARAM`, `TOKEN_PARAM`, `RENEWER_PARAM`, `SERVICE_PARAM`, `DELEGATION_TOKEN_JSON`, `DELEGATION_TOKEN_URL_STRING_JSON`, and `RENEW_DELEGATION_TOKEN_JSON`.

`KerberosDelegationTokenAuthenticator` and `PseudoDelegationTokenAuthenticator` are concrete specializations for Kerberos-backed and pseudo-authenticated web endpoints.

### Service Lifecycle APIs

`AbstractService implements Service` is the base service implementation. It exposes:

- lifecycle state and failure inspection: `getServiceState()`, `getFailureCause()`, `getFailureState()`, `getStartTime()`, `getLifecycleHistory()`, `isInState(STATE)`, and `toString()`;
- mutable config: protected/public `setConfig(Configuration)` and `getConfig()`;
- lifecycle operations: `init(Configuration)`, `start()`, `stop()`, `close()`, and protected hooks `serviceInit(Configuration)`, `serviceStart()`, and `serviceStop()`;
- failure and synchronization: `noteFailure(Exception)` and `waitForServiceToStop(long timeout)`;
- listeners: per-service `registerServiceListener(...)` / `unregisterServiceListener(...)` and static global `registerGlobalListener(...)` / `unregisterGlobalListener(...)`;
- liveness blockers: protected `putBlocker(name, details)`, public `removeBlocker(name)`, and `getBlockers()`.

The hook documentation is explicit: `serviceInit`, `serviceStart`, and `serviceStop` are called once per lifecycle transition, do not need extra synchronization because the base lifecycle methods prevent re-entry, and failures are caught/wrapped to trigger service stop. `serviceStop` implementations must be robust against partially initialized internal fields and continue shutdown work even after one subcomponent fails.

`CompositeService extends AbstractService` manages child `Service` instances:

- `getServices()` returns a cloned snapshot of children;
- protected `addService(Service)`, `addIfService(Object)`, and `removeService(Service)` manage children;
- lifecycle hooks `serviceInit`, `serviceStart`, and `serviceStop` initialize/start/stop children;
- `STOP_ONLY_STARTED_SERVICES` controls whether shutdown tries all children or only those that started, with documentation noting failed init/start children still receive `stop()`.

`LifecycleEvent implements Serializable` publishes mutable/public fields `time` and `state`. `LoggingStateChangeListener implements ServiceStateChangeListener` logs state changes to either a supplied `Logger` or a static class logger through `stateChanged(Service)`.

The chunk includes the start of `Service extends Closeable`. Methods within the assigned line range include `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration/unregistration, `getName()`, `getConfig()`, `getServiceState()`, `getStartTime()`, `isInState(STATE)`, `getFailureCause()`, `getFailureState()`, and `waitForServiceToStop(long)`. The documented lifecycle contract requires `NOTINITED -> INITED -> STARTED -> STOPPED` transitions, invokes `stop()` on init/start failure, makes repeated `stop()` on already stopped services a no-op, and defines `close()` as a direct relay to `stop()`.

## Control Flow

Metrics control flow is producer/snapshot oriented. A metric source updates mutable metrics (`incr`, `decr`, `set`, `add`) and marks them changed through `MutableMetric`; a metrics system calls `snapshot(builder, all)` on registries and metrics to emit values. `all=false` can suppress unchanged values, while `all=true` forces a full record. `MutableStat`, `MutableRate`, `MutableQuantiles`, and rolling-average metrics accumulate samples between snapshots; quantiles and rolling averages introduce periodic rollover/state collection.

Metrics sink control flow follows the `MetricsSink` lifecycle: `init(SubsetConfiguration)`, repeated `putMetrics(MetricsRecord)`, optional `flush()`, and `close()`. `RollingFileSystemSink` adds time-based control flow: records are written until `nextFlush`/roll interval boundaries require file rotation or flushing. `ignoreError` likely controls whether sink write failures are swallowed or surfaced, while `allowAppend` changes file creation behavior.

Network mapping control flow starts with `resolve(names)`. Cache wrappers consult cached name-to-switch entries, delegate misses to `rawMapping`, and expose reload methods to clear all or selected cache entries. Script and table mappings populate the raw mapping from external command/configuration or mapping files; `isSingleSwitch()` allows callers to short-circuit topology-aware behavior when all nodes map to a default/single rack.

Security login control flow is centered on global configuration and JAAS/Kerberos subject state. `SecurityUtil.login(...)` reads configured keytab/principal keys, substitutes host names in principal patterns, and delegates identity setup to UGI. UGI exposes separate flows for login-user discovery, keytab login, ticket-cache login, re-login when TGTs expire, forced re-login, logout, and subject-scoped `doAs` execution. Proxy-user creation binds an effective user to a real user, and impersonation providers later authorize that binding against configured users/groups/hosts.

Credential and token control flow separates persistent credentials from runtime identities. `Credentials` reads token storage from `Path`, `File`, or `DataInputStream`, stores tokens and secret keys by `Text` alias, and writes them back in a selected serialized format. `UserGroupInformation` can ingest `Credentials`, expose them as token collections, or add token identifiers to its underlying `Subject`. `Token` can decode its identifier, serialize as binary Writable data, or encode/decode URL-safe strings for HTTP transport.

Token renewal control flow is plugin-based. A `Token` asks its matching `TokenRenewer` whether the token kind is managed, then renews or cancels via configuration. `SecretManager` is the server-side counterpart: it creates passwords, retrieves existing passwords, checks read availability, and can signal invalid, standby, retriable, or IO failures.

Delegation-token web control flow wraps HTTP authentication. `DelegationTokenAuthenticatedURL.openConnection(...)` authenticates with an `AuthenticatedURL.Token`; when a delegation token is present, it can be sent in a header or query string depending on global setting. `getDelegationToken`, `renewDelegationToken`, and `cancelDelegationToken` call server endpoints using well-known operation/token/renewer/service parameters. `doAs` overloads layer proxy-user semantics onto those HTTP requests.

Service lifecycle control flow is a strict state machine. `Service.init(conf)` moves from `NOTINITED` to `INITED`, `start()` moves to `STARTED`, and `stop()` moves to `STOPPED`; init/start failures must trigger `stop()`. `AbstractService` wraps subclass hooks and listener notifications, records lifecycle history, tracks first failure cause/state, updates start time, and wakes waiters for `waitForServiceToStop(timeout)`. `CompositeService` cascades init/start/stop to child services using snapshots of registered children.

## State And Persistence Behavior

Mutable metrics keep in-memory counters, gauges, sample statistics, changed flags, quantile estimators, previous snapshots, and thread-local or rolling windows. Their persistence is observational rather than durable: values are emitted through `MetricsRecordBuilder` or sinks, not stored by the metric objects beyond process lifetime. `MutableQuantiles.stop()` and `MutableRollingAverages.close()` indicate background schedulers/resources may need explicit cleanup.

Metrics sinks hold runtime IO state. `FileSink`, `GraphiteSink`, and `StatsDSink` hold output destinations and buffers/connections. `RollingFileSystemSink` keeps Hadoop `Configuration`, `FileSystem`, output `Path`, source name, roll intervals, flush calendar, and error/append policy. Its file output is durable state; correctness depends on roll time calculation, append compatibility, and close/flush behavior.

`MetricsCache` is in-memory cache state keyed by record identity and tags. `MBeans` registers process-wide JVM MBean state under `ObjectName`s and must unregister to avoid leaks or duplicate registration errors.

Network mapping caches are in-memory and reloadable. Table/script mappings depend on external configuration, files, and scripts, so their effective topology state can diverge from the cluster until reload methods are called. Socket factories hold configuration/proxy state; equality and hash code matter when factories are cached or compared.

`Credentials` has both in-memory sensitive state and serialized token-storage state. Token aliases map to `Token` objects; secret-key aliases map to raw byte arrays. `getTokenMap()` and `getSecretKeyMap()` return unmodifiable maps, but the values themselves can still be mutable (`Token`, `byte[]`) unless implementation defensively copies. Writable and token-storage methods persist credentials to streams/files.

`UserGroupInformation` has significant process-global state: static configuration, login user, security enabled flag, keytab/ticket-cache login mode, metrics, and test renewal behavior. Per-UGI state is in a JAAS `Subject`, including principals, credentials, tokens, token identifiers, auth method, and real/effective user relationship. UGI group results depend on configured group mapping providers and their caches.

`AccessControlList` persists ACL content through Writable serialization and ACL strings. `DefaultImpersonationProvider` persists only in memory but derives proxy host/group/user rules from configuration prefixes.

`CredentialProvider` implementations may be transient or durable. The abstract API's `flush()` is the durability boundary; callers that create/delete credentials without flushing risk losing changes for persistent providers.

`Token` persists identifier/password/kind/service through Writable and URL-safe encodings. Private-token clone state changes service identity while preserving linkage to the public service. `TokenIdentifier.getTrackingId()` supplies audit correlation without exposing token secrets. `SecretManager` state is implementation-specific and often durable or replicated in concrete managers outside this chunk.

HTTP filters store servlet init parameters and per-request derived policy. They do not persist data but affect response/request authorization behavior across all matching web endpoints.

Service classes keep lifecycle state, configuration, start time, lifecycle history, failure cause/state, listener registries, blocker maps, and wait/termination notification state. `LifecycleEvent` is serializable and carries transition time plus state. `CompositeService` keeps an ordered child-service list; `getServices()` returns a clone to prevent accidental direct mutation.

## Dependencies And Integration Points

Key dependencies surfaced by the API signatures include:

- Hadoop metrics core: `MetricsInfo`, `MetricsRecord`, `MetricsRecordBuilder`, `MetricsSink`, `MetricsTag`, `MutableMetric`, `SampleStat`, `Quantile`, `QuantileEstimator`, and `SubsetConfiguration`.
- Hadoop configuration/filesystem: `Configuration`, `Configurable`, `FileSystem`, `Path`, and configuration keys consumed by metrics, network mapping, security, and service setup.
- Java platform APIs: `Closeable`, `IOException`, `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, `File`, `URI`, `URL`, `HttpURLConnection`, `InetAddress`, `InetSocketAddress`, `Socket`, `SocketFactory`, `Proxy`, `Calendar`, `Date`, `Map`, `List`, `Collection`, `Set`, `Serializable`, JAAS `Subject`, `PrivilegedAction`, `PrivilegedExceptionAction`, Kerberos tickets, servlet `Filter`, and JMX `ObjectName`.
- Hadoop network topology: `DNSToSwitchMapping` implementations feed rack awareness used by HDFS block placement, YARN scheduling, and other locality decisions.
- Hadoop security/RPC: `KerberosInfo`, `SaslRpcServer.AuthMethod`, `TokenInfo`, `Token`, `TokenIdentifier`, `TokenRenewer`, `UserGroupInformation`, and impersonation authorization are shared by RPC clients, RPC servers, web authentication, filesystem clients, and service daemons.
- Hadoop web authentication client: `AuthenticatedURL`, `AuthenticatedURL.Token`, `Authenticator`, `AuthenticationException`, and `ConnectionConfigurator`.
- Logging and observability: `org.slf4j.Logger`, metrics sinks, JMX registration, and service state-change listeners.

## Risks And Compatibility Concerns

This JDiff snapshot is a compatibility surface. Removing or changing signatures here can break downstream Hadoop integrations, custom metrics sources/sinks, network mapping plugins, credential providers, token renewers/selectors, servlet filters, service implementations, and security tooling.

Metrics risks:

- Changed-flag semantics affect metrics visibility. If `snapshot(..., all=false)` does not clear or honor changed flags consistently, counters/gauges may disappear or be repeatedly emitted.
- Numeric overflow is possible for long-running counters, gauges, sample counts, and rolling aggregates.
- Quantile and rolling-average APIs imply background state; missing `stop()`/`close()` can leak scheduled tasks or thread-local state.
- Public/protected `RollingFileSystemSink` fields are subclass-visible compatibility constraints. Renaming or changing them breaks subclasses/tests.
- Sink errors are operationally sensitive: ignoring errors hides telemetry loss, but surfacing them can destabilize daemons if not contained by the metrics system.

Network risks:

- DNS-to-switch mappings are security and availability adjacent. Wrong rack mapping changes replica placement, locality scheduling, and fault-domain assumptions.
- Cache invalidation is explicit; stale cached topology can persist until reload.
- Script/table mappings depend on external files/scripts and can block or fail at runtime.
- SOCKS socket configuration equality/hash behavior matters if socket factories are reused in connection caches.

Security risks:

- `Credentials`, `Token`, and `UserGroupInformation` carry secrets. APIs exposing raw `byte[]`, mutable tokens, maps, and subjects require defensive usage and careful logging.
- UGI has global static state. Tests or embedded applications that call `setConfiguration`, test renewal controls, or login methods can affect unrelated code in the same JVM.
- Keytab and ticket-cache re-login flows are race-prone if multiple threads use a UGI while credentials are refreshed.
- Kerberos principal host substitution must be exact. Incorrect canonicalization or `_HOST` handling breaks authentication or can produce cross-host principals.
- Token service construction must match RPC/HTTP service naming. Mismatches make otherwise valid tokens unusable.
- `AuthorizationException` overriding stack-trace methods can reduce diagnostics; callers should preserve context in messages.
- ACL string parsing and wildcard handling are compatibility-sensitive because ACLs are persisted and often configured by operators.
- Impersonation provider config prefixes and host/group maps are critical authorization boundaries. Incorrect prefix handling can authorize or deny proxy users unexpectedly.
- Delegation-token query-string mode risks token disclosure through logs, proxies, browser history, or referrers; header mode is safer when supported.

HTTP filter risks:

- CSRF browser detection depends on user-agent matching and ignored method lists; mistakes can block legitimate clients or allow unsafe browser requests.
- X-Frame-Options config affects clickjacking protections and UI embedding compatibility.

Service lifecycle risks:

- Service hooks must tolerate partial initialization and repeated stop attempts. Violating this contract causes shutdown failures after init/start errors.
- Listener notification and global listener registries can leak objects or introduce unexpected side effects across services in the JVM.
- `waitForServiceToStop(0)` means wait forever by contract; callers must avoid deadlocks by using bounded waits where appropriate.
- `CompositeService` stop policy affects cleanup during failures. Stopping only started services assumes child implementations cannot handle early `stop()`, while stopping all services assumes robust stop implementations.

## Test Signals

Useful test coverage suggested by this API surface:

- Metrics mutable tests: counter/gauge value changes, delta handling, `changed()` behavior, `snapshot(all=false)` vs `snapshot(all=true)`, stat min/max reset, extended stat output, quantile rollover, rolling-average close/state collection, and registry duplicate/tag override behavior.
- Metrics sink tests: sink `init`/`putMetrics`/`flush`/`close` lifecycle, Graphite/StatsD formatting, FileSink write formatting, RollingFileSystemSink roll interval computation, append/no-append behavior, forced flush, error handling with `ignoreError`, and use of supplied `Configuration`/`FileSystem`.
- JMX/cache utility tests: MBean register/unregister idempotence and name construction, `MetricsCache` updates with and without tags, cache size eviction, and `Servers.parse` default-port parsing.
- Network tests: cached mapping hits/misses, reload all vs selected names, single-switch detection, script/table mapping missing-config behavior, topology dump content, and socket factory proxy configuration/equality.
- Credentials tests: token/secret-key add/remove/count, map immutability, copy constructor, `addAll` vs `mergeAll` overwrite semantics, Writable round trip, token storage file/stream round trip in each serialized format, and secret byte-array mutation expectations.
- UGI/SecurityUtil tests: secure/simple auth configuration, `_HOST` principal substitution, login from keytab/ticket cache, forced and conditional relogin, proxy-user real/effective identity, group lookup, auth-method conversion, token/credential addition, `doAs` subject scoping, and environment token ingestion.
- Authorization tests: ACL wildcard/user/group parsing, writable round trip, real-user ACL behavior, stackless `AuthorizationException` behavior, proxy superuser config-key derivation, host/group authorization success/failure, and string-vs-address authorize overload equivalence.
- HTTP filter tests: default and custom CSRF header names, browser user-agent matching, ignored methods, rejection/allowance paths, X-Frame-Options default/custom header insertion, and servlet lifecycle cleanup.
- Token tests: token construction from identifier/secret manager, identifier decode failure behavior, binary and URL-safe round trips, private clone semantics, cache key stability, renewer selection, managed/unmanaged renew/cancel behavior, `SecretManager` invalid/standby/retriable failure paths, and tracking ID exposure.
- Delegation-token web tests: authenticator wrapping, connection configurator propagation, header vs query-string token transmission, get/renew/cancel request parameter names, JSON response parsing keys, `doAs` parameter handling, and Kerberos vs pseudo authenticator construction.
- Service lifecycle tests: valid and invalid state transitions, init/start failure triggering stop, close relaying to stop, idempotent stop, lifecycle history contents, failure cause/state recording, blocker map snapshot behavior, listener/global-listener notification ordering and unregister behavior, `waitForServiceToStop` timeout and forever-wait behavior, composite child init/start/stop ordering, child failure cleanup, and `STOP_ONLY_STARTED_SERVICES` policy.

### subset-b-007231: lines 37160-40994

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 37160-40994

## Scope

This chunk is a JDiff public API snapshot for Hadoop Common 3.3.6. It covers the tail of `org.apache.hadoop.service.Service`, service lifecycle helper APIs, the service launcher API, a large part of `org.apache.hadoop.util`, the public Bloom filter APIs, and the beginning of `org.apache.hadoop.util.functional`. The file is API metadata rather than implementation source, so the research below records public contracts, stated behavior, integration surfaces, and risks that downstream source or compatibility work must preserve.

## Purpose

The covered API surface provides common infrastructure used across Hadoop components:

- Service lifecycle state modeling and shutdown helpers for Hadoop daemons and managed services.
- Launchable-service contracts and process exit code conventions.
- General utilities for class loading, duration logging, progress callbacks, CRC implementations, reflection, shell command execution, shutdown hooks, string interning, system resource reporting, generic command-line tools, and build version metadata.
- Probabilistic membership structures in `org.apache.hadoop.util.bloom`.
- Functional helpers for executor lifecycle, future exception unwrapping, FSBuilder option propagation, and `RemoteIterator` transformation/cleanup.

## Important APIs and Types

### `org.apache.hadoop.service`

- `Service` tail methods in this chunk expose lifecycle observation: `getLifecycleHistory()` returns a non-null snapshot list of lifecycle events, and `getBlockers()` returns a snapshotted map of blocker name to description for remote dependencies preventing a service from being live. The preceding `waitForServiceToStop(timeout)` contract notes that a timeout of zero means forever and returns whether the service stopped in time.
- `ServiceOperations` is a final static utility. `stop(Service)` is null-tolerant and skips services that are not in a stoppable state, but explicitly checks state before acting and is not thread safe. Three `stopQuietly(...)` overloads catch and log `Exception` at warning level while returning the caught exception, with overloads for no logger, Apache Commons Logging, and SLF4J.
- `ServiceStateChangeListener.stateChanged(Service)` is a callback invoked after the state transition has already happened, on the initiating thread, while the service is still inside a synchronized section. The XML warns that slow callbacks delay state changes and listener re-entry through another thread can deadlock.
- `ServiceStateException` is a `RuntimeException` and `ExitCodeProvider`. It can derive an exit code from a cause, accept an explicit exit code, or fall back to `LauncherExitCodes.EXIT_SERVICE_LIFECYCLE_EXCEPTION`. Static `convert(...)` helpers wrap non-runtime throwables as `ServiceStateException`.
- `ServiceStateModel` models valid `Service.STATE` transitions. It starts in `NOTINITED` by default or a caller-provided state. `enterState(...)` is synchronized and returns the original state; `getState()`, `isInState(...)`, `ensureCurrentState(...)`, `checkStateTransition(...)`, and `isValidStateTransition(...)` provide transition validation. Same-state proposals are considered non-transitions.

### `org.apache.hadoop.service.launcher`

- `LaunchableService` extends `Service` with launcher-managed execution. `bindArgs(Configuration, List)` is called before `init(Configuration)` and may return a replacement configuration, allowing implementations to switch to richer subclasses such as `YarnConfiguration`. `execute()` is called after `Service.start()`; its return value becomes the process exit code. Exceptions are normalized by launcher semantics: `ExitUtil.ExitException` can pass through, `ExitCodeProvider` exceptions become `ServiceLaunchException` with the provider exit code, and other exceptions map to `EXIT_EXCEPTION_THROWN`.
- `AbstractLaunchableService` extends `AbstractService` and implements `LaunchableService`. Its base `bindArgs` logs arguments at debug and returns the same configuration; its base `execute()` returns success (`0`).
- `HadoopUncaughtExceptionHandler` implements `Thread.UncaughtExceptionHandler`. It is intended for installation through `Thread#setDefaultUncaughtExceptionHandler`. The handler logs simple exceptions and continues, but on `Error` it exits rather than attempting a clean shutdown because process state is unknown.
- `LauncherExitCodes` defines public process exit constants. The documented ranges are `0-10` for general command issues, `30-39` for 3xx-like errors considered application failures, `40-49` for client/CLI/config problems, `50-59` for service-side problems, and `60+` for application-specific errors. Constants include success/fail, client shutdown, task launch failure, interrupted, argument/usage/auth/forbidden/not-found errors, configuration conflicts, exception thrown, unimplemented, service unavailable, unsupported version, service creation failure, and service lifecycle exception.
- `ServiceLaunchException` extends `ExitUtil.ExitException` and implements `ExitCodeProvider` and `LauncherExitCodes`. Constructors accept an exit code plus cause, plain message, formatted message, or cause plus formatted message. Formatted constructors use `String.format` in English locale, and the last argument may become the cause when it is a throwable.

### `org.apache.hadoop.util`

- `ApplicationClassLoader` is a `URLClassLoader` for application isolation. It loads application JAR classes before parent classes except for system classes. `isSystemClass(String, List)` uses positive and negative pattern matching: a name is system only if it matches a positive pattern and no negative pattern. `SYSTEM_CLASSES_DEFAULT` keeps JDK classes, Hadoop classes/resources, and selected third-party classes in the parent/system loader.
- `DurationInfo` extends `OperationDuration` and implements `AutoCloseable`. It logs start/final duration messages at info or debug and is designed for try-with-resources. `OperationDuration` records start and finished times, uses `finished()` to update end time, returns `0` from `value()` until finished, formats as minutes:seconds.millis through `humanTime(long)`, and exposes `asDuration()`.
- `IPList.isIn(String)` is a small membership interface for IP address lists.
- `Progressable.progress()` is the long-running operation heartbeat callback. The contract says clients should explicitly report progress to avoid framework timeouts.
- `PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum`. Both expose `getValue()`, `reset()`, `update(byte[], int, int)`, and final `update(int)`. `PureJavaCrc32` uses the standard CRC32 polynomial to avoid JNI overhead on many small checksum operations; `PureJavaCrc32C` uses the CRC32-C/iSCSI polynomial.
- `ReflectionUtils` provides configuration injection, object instantiation, thread-stack diagnostics, writable copying, and reflective field/method enumeration. Key methods are `setConf(Object, Configuration)`, `newInstance(Class, Configuration)`, `setContentionTracing(boolean)`, synchronized `printThreadInfo(...)`, Commons Logging and SLF4J `logThreadInfo(...)`, `copy(Configuration, T, T)`, `cloneWritableInto(Writable, Writable)`, and inherited member collection helpers.
- `Shell` is an abstract base for shell command execution with optional minimum rerun interval and optional stderr redirection. Static helpers build OS-specific group, permission, ownership, symlink, readlink, process-liveness, signal, script-extension, and script-run commands. It locates Hadoop home, qualified Hadoop binaries, and Windows `winutils`, checks Windows command length, checks bash support, and exposes static `execCommand(...)` overloads. Subclasses implement `getExecString()` and `parseExecResult(BufferedReader)`. Instance state includes timeout interval, parent-env inheritance, working directory, environment, process, exit code, waiting thread, and timeout flag. Public constants expose OS detection, command names, regexes, Windows process launch lock, and `WINUTILS` location; misspelled `WINDOWS_MAX_SHELL_LENGHT` and direct `WINUTILS` access are deprecated.
- `ShutdownHookManager` is a final singleton that registers one JVM shutdown hook and runs managed hooks in deterministic priority order, higher priority first. It supports registration with default or explicit timeout, removal, presence checks, shutdown-in-progress checks, and clearing all hooks. Default timeout is driven by `CommonConfigurationKeysPublic.SERVICE_SHUTDOWN_TIMEOUT` with documented minimum/default units.
- `StringInterner` provides `strongIntern`, `weakIntern`, and in-place array interning. The doc says weak interning uses standard `String.intern()` behavior in modern JDKs; strong interning retains a strong reference.
- `SysInfo` is an abstract plugin for OS resource information. `newInstance()` chooses the default OS implementation or throws `UnsupportedOperationException`. Abstract metrics include virtual/physical memory totals and availability, logical processors, physical cores, CPU frequency, cumulative CPU time, CPU usage percentage, virtual cores used, network bytes read/written, and storage bytes read/written. Unavailable percentage-style metrics may return `-1`.
- `Tool` extends `Configurable` and standardizes Hadoop command-line applications: `run(String[])` accepts app-specific arguments after generic options are handled. `ToolRunner` parses generic Hadoop options through `GenericOptionsParser`, updates the tool configuration, runs the tool, prints generic usage, and provides `confirmPrompt(String)` that returns true for `y` or `yes`.
- `VersionInfo` exposes build metadata: version, git revision, branch, compile date/user, repository URL, source checksum, build version, protoc version, compile platform, and `main(String[])`. Protected underscore methods back the public static accessors.

### `org.apache.hadoop.util.bloom`

- `BloomFilter` extends `Filter` and exposes default serialization constructor, parameterized constructor `(vectorSize, nbHash, hashType)`, `add(Key)`, set operations `and`, `or`, `xor`, `not`, `membershipTest(Key)`, `getVectorSize()`, string conversion, and `Writable`-style `write/readFields`. It guarantees no false negatives for inserted keys but can return false positives.
- `CountingBloomFilter` is final and extends `Filter`. It supports add, delete, membership test, set-like operations, serialization, and `approximateCount(Key)`. The count API can behave as an approximate key-to-count map, but the doc warns that inserting the same key more than 15 times overflows associated buckets and increases error rates. Deletes can underflow and introduce false negatives.
- `DynamicBloomFilter` extends `Filter` and adds rows of standard Bloom filters as cardinality grows. Constructor parameters add `nr`, the threshold for maximum keys per row. Add inserts into an active row when one has capacity; otherwise it creates a new row. Membership succeeds when all hash positions are set in one row.
- `HashFunction` is final and maps a `Key` to multiple integer positions using a configured maximum value, number of hashes, and hash type. `clear()` is documented as a no-op.
- `RemoveScheme` defines retouched Bloom filter clearing strategies: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` is final, extends `BloomFilter`, and implements `RemoveScheme`. It records known false positives through overloads accepting a single `Key`, `Collection`, `List`, or `Key[]`, then `selectiveClearing(Key, short)` clears bits according to the selected scheme. The design intentionally trades selected false positives for possible false negatives.

### `org.apache.hadoop.util.functional`

- `CloseableTaskPoolSubmitter` implements `TaskPool.Submitter` and `Closeable` around a non-null `ExecutorService`. `submit(Runnable)` delegates to the pool, `getPool()` exposes it, and `close()` shuts it down.
- `FutureIO` is a final static utility for asynchronous IO. `awaitFuture(Future)` and timed `awaitFuture(Future, long, TimeUnit)` return the result or extract and rethrow nested IO/runtime failures, mapping interruption to `InterruptedIOException` and timed waits to `TimeoutException`. `raiseInnerCause(...)` overloads handle `ExecutionException` and `CompletionException`. `unwrapInnerException(Throwable)` recursively unwraps `UncheckedIOException`, execution/completion wrappers, runtime exceptions, and errors, returning or wrapping an `IOException` while rethrowing runtime/errors. `propagateOptions(...)` copies configuration entries with optional/mandatory prefixes into an `FSBuilder`, converting stripped prefix suffixes into builder options; examples include `fs.example.s3a.option` to `s3a.option` and `fs.example.something` to `something`. `eval(CallableRaisingIOE)` evaluates in the current thread and returns a `CompletableFuture`, converting IOExceptions to runtime failures.
- `RemoteIterators` is a final helper set for `RemoteIterator` composition. It creates remote iterators from singleton, `Iterator`, `Iterable`, and arrays; maps, type-casts, filters, adds close handling, adds halt predicates, creates numeric ranges `[start, excludedFinish)`, materializes to list/array, applies a consumer with `foreach`, and performs cleanup. The APIs preserve or pass through `IOStatisticsSource` where possible and can log IO statistics at debug with zero cost when debug logging is disabled. Cleanup closes closeable iterators and logs statistics when appropriate.

## Control Flow and State Behavior

- Service startup/execution flow is: launcher creates or configures a `LaunchableService`, calls `bindArgs(...)`, passes any returned configuration to `init(...)`, calls `start()`, invokes `execute()`, and maps the return value or thrown exception to a process exit code. Service lifecycle state transitions are guarded by `ServiceStateModel`, with synchronized transition entry and separate validation helpers.
- Service stop helpers are intentionally conservative: null services and already non-stoppable services are ignored. Quiet stop helpers catch only `Exception`, not arbitrary `Throwable`, and are intended for cleanup paths.
- State change listeners execute synchronously inside service state-change locking. This makes callbacks part of the state transition critical path.
- `Shell.run()` control flow is interval-gated. It executes only when the minimum interval has elapsed, then spawns a process from subclass-provided command strings, lets subclasses parse stdout, records exit/timeout state, and supports static global destruction of currently running shell processes.
- `ShutdownHookManager` serializes Hadoop shutdown through one JVM hook. Managed hooks are ordered by priority, with same-priority hooks nondeterministic and timeout enforcement for long-running hooks.
- Bloom filter state is in-memory probabilistic state with `Writable`-style binary serialization. Standard Bloom filters are monotonic unless bitwise operations are applied; counting filters mutate counters on add/delete; dynamic filters append rows as thresholds are reached; retouched filters mutate bits to suppress known false positives.
- `FutureIO` normalizes async control flow by moving checked `IOException` semantics through future/execution wrappers. `RemoteIterators` composes lazy iteration; filtering may happen in `hasNext()` or lazily in `next()` if `hasNext()` is not called.

## Persistence and Compatibility Notes

- This XML is generated public API metadata. It is a compatibility baseline: public names, signatures, visibility, deprecation state, inheritance, exceptions, and documentation are the durable facts.
- `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, and `RetouchedBloomFilter` expose `write(DataOutput)` and `readFields(DataInput)`, so serialized wire/storage compatibility depends on preserving vector sizes, hash counts/types, counter encodings, dynamic rows, and false-positive metadata layouts in implementation code.
- `VersionInfo` values come from build-time metadata resources/properties rather than runtime mutable state.
- `Service.getLifecycleHistory()` and `getBlockers()` promise snapshots. Implementations should avoid exposing mutable live internal collections.
- `Shell` exposes several public constants and deprecated fields that remain part of binary/source compatibility. The misspelled `WINDOWS_MAX_SHELL_LENGHT` and nullable `WINUTILS` cannot simply be removed without API breakage.

## Dependencies and Integration Points

- Service APIs integrate with `org.apache.hadoop.conf.Configuration`, `AbstractService`, `ExitCodeProvider`, `ExitUtil.ExitException`, `LauncherExitCodes`, Commons Logging, SLF4J, and the general Hadoop shutdown/launcher ecosystem.
- Tool APIs integrate with `Configurable`, `Configured`, `GenericOptionsParser`, command manual generic options, and MapReduce-style jobs in downstream applications.
- `Shell` integrates deeply with OS-specific facilities: Unix commands (`groups`, `id`, `chmod`, `chown`, `ln`, `readlink`, `kill`), Windows command length and `winutils`, script extension/interpreter selection, environment variables, process handles, and Hadoop home/bin discovery.
- `ShutdownHookManager` depends on `CommonConfigurationKeysPublic` shutdown timeout configuration.
- Reflection utilities depend on Hadoop `Writable` serialization and `Configuration` injection patterns.
- Bloom filters depend on `Key`, `Filter`, and `org.apache.hadoop.util.hash.Hash`.
- Functional utilities integrate with `ExecutorService`, `Future`, `CompletableFuture`, `ExecutionException`, `CompletionException`, `UncheckedIOException`, `FSBuilder`, `Configuration`, `RemoteIterator`, `IOStatisticsSource`, and Hadoop IO-statistics logging conventions.

## Risks and Edge Cases

- Listener deadlocks are a first-class risk: `ServiceStateChangeListener` runs while the service is synchronized, so callbacks must avoid slow work and re-entrant service calls through other threads.
- `ServiceOperations.stop(Service)` is not thread safe because it checks state before operating. Concurrent lifecycle changes can race with the stop decision.
- Quiet stop catches `Exception` but not `Throwable`; cleanup paths can still be interrupted by `Error`.
- Launcher exit code behavior is observable process API. Incorrect exception mapping can break scripts and service managers that key off numeric exit codes.
- `HadoopUncaughtExceptionHandler` exits on `Error`; tests and embedding environments must account for process termination behavior.
- `ApplicationClassLoader` system-class pattern errors can either leak Hadoop classes into isolated apps or accidentally shadow core/system classes.
- `Shell` has OS-dependent behavior and external binary dependencies. Windows command length validation, `winutils` discovery, `setsid` availability, environment inheritance, timeout handling, process cleanup, and shell output parsing are all platform-sensitive.
- `ShutdownHookManager` same-priority order is nondeterministic. Hooks should not depend on ordering unless priorities differ.
- `OperationDuration.value()` returns zero until `finished()` is called; callers that expect live elapsed time can misreport.
- `CountingBloomFilter` overflows after repeated inserts of the same key beyond the documented counter capacity and deletes can underflow, increasing false positives or causing false negatives.
- `RetouchedBloomFilter` explicitly accepts false negatives as the cost of selective false-positive removal; callers needing strict no-false-negative semantics should not substitute it for standard `BloomFilter`.
- `FutureIO.unwrapInnerException(...)` rethrows runtime exceptions and errors. Callers expecting only `IOException` from all async failures must handle those paths separately.
- `RemoteIterators.foreach(...)` does not close the iterator afterward. Callers must invoke cleanup or use closeable wrapping when iterators hold remote connections/file handles.

## Test Signals

- Service lifecycle tests should cover valid and invalid `ServiceStateModel` transitions, same-state non-transitions, `ensureCurrentState` failures, snapshot immutability/non-nullness for lifecycle history/blockers, listener invocation ordering, and deadlock-avoidance expectations.
- Stop helper tests should cover null services, services in non-stoppable states, exception-return behavior from `stopQuietly`, and logging overloads for Commons Logging and SLF4J.
- Launcher tests should exercise `bindArgs` configuration replacement before init, `execute` return-code propagation, exception-to-exit-code mapping for `ExitException`, `ExitCodeProvider`, generic exceptions, and formatted `ServiceLaunchException` causes.
- Utility tests should validate `ApplicationClassLoader.isSystemClass` positive/negative pattern behavior, duration formatting and close-time logging, progress callback use in long-running operations, CRC32/CRC32C compatibility with known vectors, reflection copy/config injection, and `VersionInfo` metadata reads.
- Shell tests need OS-specific coverage for command construction, script extension selection, Hadoop home/bin discovery, Windows path/length/winutils behavior, timeout state, process cleanup, environment/working-directory propagation, and parsing failures.
- Shutdown hook tests should verify priority ordering, same-priority nondeterminism tolerance, explicit/default timeout handling, removal, `hasShutdownHook`, and shutdown-in-progress state.
- Bloom filter tests should round-trip serialization, verify no false negatives for standard Bloom inserts, confirm expected false-positive behavior statistically, cover counting add/delete/approximate count with overflow/underflow boundaries, dynamic row growth at `nr`, hash position bounds, and retouched selective-clearing tradeoffs.
- Functional tests should cover future success, interruption, timeout, nested `ExecutionException`/`CompletionException`/`UncheckedIOException` unwrapping, runtime/error propagation, FSBuilder optional/mandatory option propagation and suffix conversion, iterator mapping/filtering/lazy behavior, close passthrough, halt predicate termination, range boundaries, `toList`/`toArray`, `foreach` count return, and IO-statistics logging only when debug is enabled.
