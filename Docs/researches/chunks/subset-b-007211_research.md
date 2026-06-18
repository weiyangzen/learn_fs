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
