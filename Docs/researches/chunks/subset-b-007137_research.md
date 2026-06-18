# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 1-6132

## Scope

This chunk covers the first 6,132 lines of the Hadoop Common 2.10.0 JDiff XML API snapshot. It is generated documentation metadata, not executable Java source. The covered XML starts the `<api name="Apache Hadoop Common 2.10.0">` document and describes public API contracts for `org.apache.hadoop`, `org.apache.hadoop.conf`, `org.apache.hadoop.crypto.key`, and the beginning of `org.apache.hadoop.fs` through `CreateFlag`.

Because JDiff records public signatures, declared exceptions, deprecation markers, fields, implemented interfaces, and Javadoc text, this file functions as an ABI/API compatibility baseline for later comparison. Behavioral details are inferred only from the documented contracts in the XML; implementation bodies live in the corresponding Hadoop Common Java sources.

## Purpose

The file preserves the Hadoop Common 2.10.0 public surface for JDiff compatibility reports. In this chunk, the API surface is centered on:

- Hadoop-specific argument exceptions.
- Configuration loading, typing, deprecation, serialization, credential lookup, and diagnostic dumping.
- Base configurable object plumbing.
- Reconfiguration status reporting.
- Key-provider abstraction and factory discovery for encryption key storage.
- The `AbstractFileSystem` service-provider contract used under `FileContext`.
- File-system data and capability types such as `AvroFSInput`, `BlockLocation`, `BlockStoragePolicySpi`, ByteBuffer read interfaces, cache-control stream interfaces, checksum exceptions, and `ChecksumFileSystem`.
- Public Hadoop Common configuration-key constants.
- `ContentSummary` display/summary API and the beginning of `CreateFlag` validation semantics.

The XML is intended to be consumed by documentation/compatibility tooling, but it is also a compact map of which APIs Hadoop exposes as public and therefore must preserve with care.

## Important APIs, Types, and Functions

`org.apache.hadoop.HadoopIllegalArgumentException` extends `IllegalArgumentException` and distinguishes invalid arguments raised by Hadoop code from generic JDK invalid-argument failures. It is referenced by `CreateFlag.validate*` when invalid create/append flag combinations are supplied.

`org.apache.hadoop.conf.Configurable` defines the minimal `setConf(Configuration)` and `getConf()` contract. `Configured` is the base implementation storing a `Configuration` for subclasses.

`org.apache.hadoop.conf.Configuration` is the dominant type in this chunk. It implements `Iterable` and `Writable`, has constructors for default loading, explicit default suppression, and copy construction, and exposes large groups of methods:

- Resource management: `addDefaultResource`, many `addResource` overloads for classpath names, URLs, `Path`s, `InputStream`s, and another `Configuration`, plus `reloadConfiguration` and static `reloadExistingConfigurations`.
- Deprecation support: static `addDeprecations`, several `addDeprecation` overloads, `isDeprecated`, `setDeprecatedProperties`, `dumpDeprecatedKeys`, and `hasWarnedDeprecation`.
- Lookup and mutation: `get`, `getTrimmed`, `getRaw`, `set`, `unset`, `setIfUnset`, `onlyKeyExists`, and typed getters/setters for `int`, `long`, byte-sized longs with suffixes, `float`, `double`, `boolean`, `enum`, `TimeUnit` durations, regex `Pattern`s, ranges, string lists, trimmed strings, and class references.
- Sensitive values: `getPassword`, `getPasswordFromCredentialProviders`, and protected `getPasswordFromConfig`.
- Network helpers: `getSocketAddr`, `setSocketAddr`, and `updateConnectAddr`, including multi-homed bind-host/client-address handling.
- Class loading: `getClassByName`, `getClassByNameOrNull`, `getClasses`, `getClass`, `getInstances`, `setClass`, `getClassLoader`, and `setClassLoader`.
- Local path/resource helpers: `getLocalPath`, `getFile`, `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader`.
- Introspection and serialization: `getPropertySources`, `getFinalParameters`, protected `getProps`, `size`, `clear`, `iterator`, `getPropsWithPrefix`, `writeXml`, static `dumpConfiguration`, `readFields`, `write`, and `getValByRegex`.

`ReconfigurationTaskStatus` records a reconfiguration task's start time, end time, and per-property status map, with `hasTask()` and `stopped()` helpers to distinguish no task, active task, and completed task states.

`org.apache.hadoop.crypto.key.KeyProvider` is an abstract, thread-safe provider of secret key material. Public abstract operations include `getKeyVersion`, `getKeys`, `getKeyVersions`, `getMetadata`, `createKey(name, material, options)`, `deleteKey`, `rollNewVersion(name, material)`, and `flush`. Default/helper operations include `options(conf)`, `getKeysMetadata`, `getCurrentKey`, generated-material `createKey`, generated-material `rollNewVersion`, `close`, `getBaseName`, `buildVersionName`, `findProvider`, `needsPassword`, and password-warning/error text. Public constants expose default cipher, default bit length, and JCEKS serial-filter settings.

`KeyProviderFactory` is the service-loader factory layer. It creates providers from URIs, resolves configured provider paths with `getProviders(conf)`, and exposes the `KEY_PROVIDER_PATH` configuration key.

`org.apache.hadoop.fs.AbstractFileSystem` is the abstract implementation contract behind `FileContext`. It owns scheme/authority validation, URI qualification, statistics, and the filesystem operations subclasses must implement. Key APIs include factories `createFileSystem` and `get`, static statistics management, `checkScheme`, `checkPath`, `getUriPath`, `makeQualified`, working/home directory helpers, server defaults, `resolvePath`, create/open/delete/mkdir/truncate/replication/rename operations, symlink hooks, permission/owner/time/checksum/status/block-location operations, listing, checksum verification toggle, canonical service naming, ACL and xattr APIs, snapshot APIs, storage-policy APIs, and identity methods. Many methods explicitly mirror `FileContext` behavior while requiring paths to belong to the current filesystem.

Other `org.apache.hadoop.fs` types in this chunk include:

- `AvroFSInput`, an adapter from `FSDataInputStream`/`FileContext` to Avro `SeekableInput`.
- `BlockLocation`, a mutable holder for block hosts, cached hosts, names, topology paths, storage IDs, storage types, offset, length, and corrupt flag.
- `BlockStoragePolicySpi`, the public storage-policy view with names, preferred storage types, creation fallbacks, replication fallbacks, and copy-on-create status.
- `ByteBufferPositionedReadable` and `ByteBufferReadable`, optional stream capabilities for ByteBuffer-based positioned and sequential reads.
- `CanSetDropBehind`, `CanSetReadahead`, and `CanUnbuffer`, optional stream tuning/capability interfaces.
- `ChecksumException`, which carries a checksum-error byte position.
- `ChecksumFileSystem`, an abstract `FilterFileSystem` that creates and verifies client-side checksum files around a raw filesystem.
- `CommonConfigurationKeysPublic`, a public constants class for documented common configuration keys.
- `ContentSummary`, a `QuotaUsage` subclass and `Writable` summary of directory/file length, counts, quota display, snapshot counts, and storage-type quota output.
- `CreateFlag`, an enum whose documented values and validators define create, append, overwrite, sync, lazy-persist, and append-new-block semantics.

## Control Flow

There is no runtime control flow inside the XML itself. The meaningful flow is the documented API flow captured by the signatures:

`Configuration` instances load default resources unless constructed with `loadDefaults=false`, then overlay additional resources in insertion order. Reads trigger resource parsing and variable expansion; writes through `set` overlay resource values. Deprecated keys are redirected to replacement keys, and setting a deprecated key can also update replacements. Static deprecation updates use an atomic context-swap retry pattern described in the Javadoc. `reloadConfiguration` clears resource-derived and final-parameter state so resources are parsed again on later access; `reloadExistingConfigurations` applies this to existing instances. Output flows serialize non-default configuration state via XML or JSON-like diagnostic dumps.

Credential lookup in `Configuration.getPassword` first tries the CredentialProvider API and conditionally falls back to cleartext config, depending on configured credential behavior. Network helpers parse and rewrite host/port properties so services can bind wildcard or multi-home listener addresses while publishing usable client addresses.

`KeyProvider` flows use provider discovery from `KeyProviderFactory` based on configured provider URIs. Callers create or discover a provider, read current metadata/key versions for encryption or decryption, create keys, roll versions, delete keys, and call `flush()` to persist provider changes. Generated-key overloads delegate to material-explicit abstract methods after producing key bytes.

`AbstractFileSystem` factory flow resolves `fs.AbstractFileSystem.<scheme>.impl` from `Configuration`, constructs the implementation with the target URI, and validates scheme/authority. Public final wrappers such as `create` and `rename` normalize options and delegate to abstract or overrideable internal methods (`createInternal`, `renameInternal`). Most methods are specified in terms of `FileContext` semantics, with additional path qualification and same-filesystem checks before delegating to filesystem-specific implementations.

`ChecksumFileSystem` wraps a raw `FileSystem`. Data reads open checksum-aware streams when verification is enabled; writes create paired checksum files when write checksums are enabled; delete/rename/list/copy behavior coordinates raw files and associated checksum files. `reportChecksumFailure` gives implementations a hook to react to checksum errors and signal whether retry is needed.

`CreateFlag.validate` and `validateForAppend` enforce documented flag combinations before filesystem create/append operations proceed. The chunk ends before the closing invalid-combination list is complete, so full enum constant inventory and all invalid combinations must be reconciled with the next chunk.

## State and Persistence Behavior

The JDiff XML is a generated persistent artifact under `dev-support/jdiff`; its state is the serialized public API baseline. It records a generation timestamp, command-line classpath/sourcepath/doclet metadata, packages, classes, interfaces, constructors, methods, fields, deprecation strings, exceptions, and Javadoc text. It does not execute or mutate Hadoop runtime state.

The runtime APIs described by the chunk have substantial state implications:

- `Configuration` maintains loaded resources, overlay properties set programmatically, final-parameter tracking, property source history, classloader state, quiet-mode state, deprecation warning state, and serialized `Writable` form. InputStream resources are explicitly cached, increasing memory use.
- `Configuration` variable expansion can read other configuration properties, Java system properties, and environment variables, with optional default syntax for environment lookups.
- `KeyProvider` implementations persist key metadata and key material in provider-specific stores. The abstract contract requires `flush()` to make mutations durable, and `isTransient()` distinguishes providers meant only for transient key-material access.
- `AbstractFileSystem` owns per-filesystem statistics keyed by URI scheme/authority and exposes static clearing/printing of those statistics. Filesystem implementations persist the real namespace effects of create, mkdir, delete, rename, ACL, xattr, snapshot, storage-policy, ownership, permission, replication, timestamp, and checksum operations.
- `ChecksumFileSystem` persists sidecar checksum files for raw data files and can leave consistency hazards if raw-file and checksum-file operations diverge.
- `BlockLocation` and `ContentSummary` are mutable/serializable metadata carriers used to report filesystem state rather than authoritative stores themselves.
- `CommonConfigurationKeysPublic` is compile-time API state: changing constant names, types, deprecation metadata, or documented defaults can break downstream code and compatibility reports even if no runtime behavior changes.

## Dependencies and Integration Points

The XML header records the JDiff doclet and a build-time dependency graph that includes Hadoop annotations, Hadoop auth, Guava, Commons CLI/IO/Net/Configuration/Collections/Lang, servlet and Jetty, Jersey/Jackson/JAXB/Jettison, SLF4J/log4j, Avro, Snappy, Ant, protobuf, Gson, Nimbus JOSE JWT, Apache Directory Kerberos, Curator, JSch, ZooKeeper, Netty, Commons Compress, and Woodstox. The source path points at `hadoop-common/src/main/java`.

Major integration points reflected in the API include:

- `Configuration` integrates with almost every Hadoop Common subsystem through shared config keys, resource loading from `core-default.xml` and `core-site.xml`, `Writable` serialization, credential providers, class loading, local filesystem path selection, and service address publication.
- `KeyProvider` and `KeyProviderFactory` integrate encryption users with pluggable key stores, KMS clients, JCEKS providers, and credential/password configuration.
- `AbstractFileSystem` integrates filesystem implementations with `FileContext`, `Path`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `FsPermission`, ACL entries/status, xattrs, storage policies, `FsServerDefaults`, `RemoteIterator`, `Options.CreateOpts`, `Options.Rename`, and Hadoop security exceptions.
- `AvroFSInput` bridges Hadoop FS streams to Avro file readers.
- ByteBuffer read interfaces and cache-control interfaces integrate optional stream capabilities with `FSDataInputStream`/underlying streams and `StreamCapabilities`.
- `ChecksumFileSystem` integrates raw filesystems with client-side checksum generation and verification.
- `CommonConfigurationKeysPublic` integrates core-default documentation and downstream code that uses public constants for filesystem, IO, IPC/RPC, security, KMS, crypto, shell, HTTP, credential, and service-shutdown settings.

## Risks and Edge Cases

The file is generated API metadata, so the primary local risk is stale or incomplete generation. If this XML no longer matches the Java source or build classpath, compatibility reports may bless or reject the wrong public API.

`Configuration` carries several compatibility and operational risks. Deprecation aliases can cause one logical setting to update multiple keys; callers that mix deprecated and replacement keys need tests around precedence. Resource overlay order and final parameters can make later settings silently ineffective. InputStream resources are cached, which can be expensive for large resources. Variable expansion reads system properties and environment variables by default unless restricted, so reproducibility and leakage of host-specific state need attention. Password fallback to cleartext config is security-sensitive and depends on credential-provider configuration.

Typed getters throw different failure modes: numeric and duration getters can throw `NumberFormatException`, class getters can throw `ClassNotFoundException` or interface-validation errors, and socket helpers must handle wildcard and multi-home addresses. The XML documents these contracts but not all implementation-specific validation details.

`KeyProvider` implementations must be thread safe and must correctly separate transient providers from durable stores. Missing `flush()` calls can lose key mutations. Generated key material depends on configured algorithm and bit length; provider password handling can degrade from error to warning depending on implementation. `findProvider` searches provider lists by key, so duplicate key names across providers are an ambiguity risk.

`AbstractFileSystem` is a high-blast-radius SPI. Subclasses must honor `FileContext` semantics, same-filesystem path checks, abstract method exception contracts, symlink behavior, rename overwrite behavior, and default-port URI identity. Weak validation can let paths escape a filesystem authority; overly strict validation can break slash-relative paths. Optional/default ACL, xattr, snapshot, storage-policy, and symlink methods may appear public even where a filesystem does not support them, so unsupported-operation behavior must be consistent.

`BlockLocation` exposes arrays through getters/setters; callers should treat returned arrays carefully to avoid accidental mutation assumptions. ByteBuffer read APIs define buffer state as undefined on exception, which is important for retry logic. `ChecksumFileSystem` can create stale sidecar checksum files on partial failure, failed rename, failed delete, or raw filesystem behavior differences.

Several constants in `CommonConfigurationKeysPublic` are deprecated or typo-preserving in docs (`Defalt`, moved MapReduce sort keys, old group-shell timeout constants). Removing or renaming them can break public compatibility even if newer constants exist.

`CreateFlag` allows combinations but rejects `APPEND|OVERWRITE` and requires append validation to contain `APPEND` and exclude `OVERWRITE`. The chunk ends before the full invalid-combination documentation closes, so merge output should not infer completeness from this chunk alone.

## Test Signals

Useful validation signals for this API snapshot and the described contracts include:

- JDiff or equivalent compatibility checks that compare this XML against adjacent Hadoop Common versions and flag public signature/deprecation/exception changes.
- Configuration tests covering resource ordering, final parameters, default-resource loading, explicit `loadDefaults=false`, reload behavior, property source history, variable/environment expansion, restricted system properties, deprecated-key aliasing, typed parsing, class loading, XML/diagnostic dumping, `Writable` round trips, and credential-provider fallback.
- Security tests for password lookup, sensitive-key redaction behavior outside this chunk's implementation, cleartext fallback toggles, key provider password warnings/errors, and JCEKS serial-filter configuration.
- Key-provider tests for service-loader discovery from URI paths, duplicate/missing provider schemes, generated key creation, key version naming/base-name parsing, rolling versions, deletion, persistence after `flush()`, transient providers, and concurrent access.
- Filesystem SPI contract tests through `FileContext` for URI qualification, invalid names, same-filesystem checks, create/open/delete/mkdir/truncate/rename semantics, overwrite handling, replication, permissions, owner/time, symlink support, file status/link status, block locations, listing iterators, checksum verification toggles, ACLs, xattrs, snapshots, and storage policies.
- Stream capability tests for ByteBuffer reads, positioned ByteBuffer reads, zero-length reads, exception-state recovery, drop-behind/readahead unsupported-operation paths, and `unbuffer()`.
- Checksum filesystem tests for checksum file naming/length calculations, read verification, write checksum generation, append/truncate behavior, rename/delete cleanup, copy-to-local CRC options, and checksum-failure reporting.
- CLI/display tests for `ContentSummary` headers and `toString` combinations with quota, human-readable sizes, storage types, and snapshot inclusion/exclusion.
- Create/append validation tests for every `CreateFlag` combination documented here and completed in the following chunk.

## Cross-Chunk Notes

This chunk starts a much larger JDiff XML file. The merge lane should combine this report with later chunks before producing a final per-file document, especially to complete the `CreateFlag` enum documentation and all remaining `org.apache.hadoop.fs`, IO, IPC, metrics, net, record, security, service, util, and other Hadoop Common APIs that appear after line 6,132.
