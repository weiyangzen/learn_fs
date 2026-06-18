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
