# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml

Chunk: `subset-b-007179`
Lines researched: 1-6120 of generated JDiff XML for `Apache Hadoop Common 2.8.3`.

## Purpose

This chunk is the opening portion of Hadoop Common 2.8.3's generated JDiff API description. It is not implementation source; it is a machine-readable public API snapshot emitted by the JDiff Javadoc doclet on 2017-12-05. The file records packages, classes, interfaces, constructors, methods, fields, visibility, abstract/static/final/synchronized flags, declared exceptions, deprecation messages, inheritance, implemented interfaces, and Javadoc text. Downstream release tooling can compare this XML against other API snapshots to detect public API changes across Hadoop versions.

The chunk covers the document header, the initial Hadoop root exception, all visible APIs in `org.apache.hadoop.conf`, empty package markers for some crypto packages, the key-provider API in `org.apache.hadoop.crypto.key`, and the first portion of `org.apache.hadoop.fs` through the beginning of `FileContext.resolvePath`.

## XML Structure And Generation Context

The root `<api>` element names `Apache Hadoop Common 2.8.3`, uses JDiff version `1.0.9`, and points to `api.xsd`. The generated comment includes the doclet invocation and a long classpath containing Hadoop Common, Hadoop annotations/auth, Guava, Commons libraries, Jetty, Jersey, Jackson, Avro, protobuf, Curator, ZooKeeper, HTrace, and compression libraries. That classpath is important because JDiff output depends on the classes and annotations visible to Javadoc at generation time.

Every public type appears inside a `<package>` block. Classes and interfaces carry metadata such as `extends`, `abstract`, `static`, `final`, `visibility`, and `deprecated`. Methods and constructors list parameters as typed `<param>` elements, checked exceptions as `<exception>` elements, and public documentation in CDATA. Fields likewise expose type, static/final flags, visibility, and deprecation state.

## APIs And Types Covered

`org.apache.hadoop.HadoopIllegalArgumentException` is a public subclass of `java.lang.IllegalArgumentException`. Its single string constructor and class doc establish it as Hadoop's own invalid-argument signal, distinct from JDK-originated `IllegalArgumentException`.

`org.apache.hadoop.conf.Configurable` is the minimal configuration injection contract with `setConf(Configuration)` and `getConf()`.

`org.apache.hadoop.conf.Configuration` is the largest API in this chunk. It implements `Iterable` and Hadoop `Writable`, supports default construction, construction without default resources, and copy construction. Its visible API includes:

- Resource loading: `addDefaultResource`, multiple `addResource` overloads for classpath names, `URL`, `Path`, `InputStream`, named input streams, and another `Configuration`.
- Reloading and global state: `reloadConfiguration`, static synchronized `reloadExistingConfigurations`, and quiet-mode controls.
- Deprecation handling: `addDeprecations`, multiple `addDeprecation` overloads, `isDeprecated`, `setDeprecatedProperties`, `dumpDeprecatedKeys`, and `hasWarnedDeprecation`.
- Property access: `get`, `getTrimmed`, `getRaw`, `set`, `unset`, `setIfUnset`, `onlyKeyExists`, and `setAllowNullValueProperties`.
- Typed parsing and writing: int, long, byte-size long, float, double, boolean, enum, time-duration, regex pattern, integer ranges, string collections, trimmed strings, string arrays, and password access.
- Address and class loading helpers: socket address resolution/update, `getClassByName`, `getClassByNameOrNull`, class-list parsing, typed `getClass`, object instantiation through configured classes, and `setClass`.
- Local resource helpers: `getLocalPath`, `getFile`, `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader`.
- Introspection and serialization: `getFinalParameters`, protected synchronized `getProps`, `size`, `clear`, `iterator`, `getPropsWithPrefix`, `writeXml`, static JSON-style `dumpConfiguration`, `readFields`, `write`, and `getValByRegex`.

`Configuration` documentation defines the main runtime semantics: resources load in order, normally `core-default.xml` then `core-site.xml`; later resources override earlier ones unless a property is marked final; values are expanded from other configuration properties, Java system properties, and environment variables including default forms; deprecated configuration keys warn by default and may alias newer keys. Several static or synchronized methods indicate shared process-level state for defaults, deprecation contexts, and loaded configurations.

`org.apache.hadoop.conf.Configured` is a small base class implementing `Configurable`, storing and returning a `Configuration`.

`org.apache.hadoop.conf.ReconfigurationTaskStatus` is a public status value exposing start/end timestamps, a final status map, `hasTask()`, and `stopped()` for live or completed dynamic reconfiguration tasks.

`org.apache.hadoop.crypto.key.KeyProvider` is an abstract, thread-safe provider of secret key material. It separates key storage from encryption users. Important contracts include:

- Provider configuration via constructor and `getConf()`.
- Key discovery and metadata: `getKeys`, `getKeysMetadata`, `getKeyVersions`, `getCurrentKey`, and abstract `getMetadata`.
- Key lifecycle: abstract material-backed `createKey`, generated-material `createKey`, abstract `deleteKey`, material-backed `rollNewVersion`, generated-material `rollNewVersion`, and abstract `flush`.
- Version naming helpers: `getBaseName` and protected `buildVersionName`.
- Provider selection and password UX: `findProvider`, `needsPassword`, `noPasswordWarning`, and `noPasswordError`.
- Public constants for default cipher and bit length names/defaults.

`org.apache.hadoop.crypto.key.KeyProviderFactory` is an abstract ServiceLoader-based factory. `getProviders(Configuration)` reads configured provider paths; `get(URI, Configuration)` creates one provider for a URI or returns null if no scheme provider exists; `KEY_PROVIDER_PATH` is the public configuration key.

`org.apache.hadoop.fs.AbstractFileSystem` is the main implementor-facing filesystem abstraction used by `FileContext`. It is abstract, keeps protected `FileSystem.Statistics`, and defines the public contract for URI validation, statistics, scheme/authority checks, path qualification, server defaults, path resolution, create/open/delete/rename/mkdir, symlink operations, file status/block location queries, ACLs, xattrs, snapshots, storage policies, checksums, and service naming. Its docs state applications should use `FileContext`, while filesystem implementations subclass `AbstractFileSystem`. Paths passed to it must either be fully qualified for the same scheme/authority or slash-relative paths rooted in that filesystem.

`org.apache.hadoop.fs.AvroFSInput` adapts `FSDataInputStream` to Avro `SeekableInput` and `Closeable`, with constructors from an existing stream and length or from `FileContext` plus `Path`.

`org.apache.hadoop.fs.BlockLocation` models block replica locations and metadata: hosts, cached hosts, names, topology paths, storage IDs, storage types, file offset, length, and corruption state. It exposes many constructors plus getters/setters for those fields.

`org.apache.hadoop.fs.BlockStoragePolicySpi` describes block placement policy by name, preferred storage types, creation fallbacks, replication fallbacks, and whether a policy is copy-on-create/inherit-only.

`org.apache.hadoop.fs.ByteBufferReadable`, `CanSetDropBehind`, `CanSetReadahead`, and `CanUnbuffer` are optional stream capability interfaces. Their docs make feature support conditional: callers must be ready for `UnsupportedOperationException` on ByteBuffer reads, drop-behind, and readahead. `CanUnbuffer` signals streams that can release buffers, sockets, or file descriptors.

`org.apache.hadoop.fs.ChecksumException` is an `IOException` subclass carrying an error position.

`org.apache.hadoop.fs.ChecksumFileSystem` is an abstract `FilterFileSystem` wrapper that creates, verifies, and maintains client-side checksum files around an underlying raw filesystem. Its API exposes checksum-file naming/length helpers, verify/write toggles, raw filesystem access, checksum length calculation, open/append/create/truncate, permissions/owner/ACL passthroughs, replication, rename/delete/listing, local copy helpers, and `reportChecksumFailure`.

`org.apache.hadoop.fs.CommonConfigurationKeysPublic` is a public constants holder for documented common configuration keys and defaults. The chunk includes filesystem, topology, trash, local block, file/FTP FS implementation, IO, TFile, caller context, IPC, socket/RPC, group mapping/cache, security/authentication/authorization, SSL/Kerberos, crypto/KMS, secure random, shell safety, and sensitive config key constants. Its class doc says common code should generally use `CommonConfigurationKeys` instead.

`org.apache.hadoop.fs.ContentSummary` extends `QuotaUsage` and implements `Writable`. It records content length, directory/file counts, snapshot counts, snapshot space, equality/hash behavior, headers for CLI-style output, and many `toString` overloads for quota, human-readable, storage-type, and snapshot-exclusion display modes. Constructor docs say the old constructors are deprecated in favor of `ContentSummary.Builder`, though the XML marks them `not deprecated`.

`org.apache.hadoop.fs.CreateFlag` is a public enum API snapshot. Its docs define create/append/overwrite semantics and flags including `SYNC_BLOCK`, `LAZY_PERSIST`, and `APPEND_NEWBLOCK`. Static validation methods reject invalid flag combinations such as `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`, throwing `HadoopIllegalArgumentException` or `IOException` depending on overload.

`org.apache.hadoop.fs.FileAlreadyExistsException` is an `IOException` for existing targets when overwrite is not configured.

`org.apache.hadoop.fs.FileChecksum` is an abstract `Writable` for algorithm name, checksum length, bytes, checksum options, equality, and hash code.

`org.apache.hadoop.fs.FileContext` starts at the end of this chunk. Visible APIs include filesystem resolution for an absolute or fully qualified path, static factory overloads for default configuration, local filesystem context, URI-based contexts, configuration-based contexts, explicit `AbstractFileSystem` contexts, working-directory getters/setters, UGI access, home directory, umask getters/setters, and the declaration of `resolvePath(Path)`. The chunk stops inside `resolvePath`, so later `FileContext` operations belong to following chunks.

## Control Flow And Behavioral Contracts

Because this is an API XML artifact, direct executable control flow is not present. The behavioral flow is expressed in API contracts:

- `Configuration` flows from default resources to user-added resources, overlays later values over earlier ones unless final, lazily reloads resources after `reloadConfiguration`, and expands variables on access. Deprecated-key handling flows both ways: reads from deprecated keys prefer replacement values, and setting deprecated or associated keys propagates values to replacements or aliases.
- Configuration deprecation registration uses a lockless global context-swap algorithm according to the docs for `addDeprecations`; if another thread updates the context concurrently, it retries until its swap wins.
- `KeyProvider` lifecycle flows from provider discovery by `KeyProviderFactory`, to key creation/version rolling, to `flush()` for persistence. Generated-key overloads delegate to material-taking abstract methods after generating material from algorithm and bit length.
- `AbstractFileSystem` factory resolution flows from URI scheme to `fs.AbstractFileSystem.<scheme>.impl`, then constructs a filesystem with the URI and configuration. Most operations require paths qualified for the target filesystem and expose rich exception contracts for access, missing files, bad parent directories, unsupported filesystems, unresolved links, and IO failures.
- `ChecksumFileSystem` wraps operations around a raw filesystem, creating sibling checksum files for raw files and verifying checksums on reads when enabled. Rename/delete/list operations must account for checksum files as well as raw data files.
- `FileContext` creation flows through default configuration, explicit URI, local filesystem URI, or explicit `AbstractFileSystem`. Working directory handling is path-prefix based, not inode-based, and intentionally differs from Unix semantics for distributed roots.

## State And Persistence Behavior

The XML itself is persistent generated metadata used for API compatibility checks. It does not mutate runtime state.

Runtime state described by the APIs includes:

- `Configuration` instances maintain property maps, resource lists, final-parameter sets, property-source metadata, class loader, quiet mode, null-value test behavior, and restriction flags for system properties. Static/global state includes default resources, deprecation mappings, deprecation warning history, and existing configuration instances eligible for reload.
- `ReconfigurationTaskStatus` stores task start/end timestamps and a status map for dynamic reconfiguration outcomes.
- `KeyProvider` implementations own key material and metadata. `flush()` is the explicit persistence boundary for provider changes. `isTransient()` distinguishes stores intended only for transient key material from long-term stores.
- `AbstractFileSystem` has filesystem identity state in URI scheme/authority and shared statistics keyed by scheme/authority.
- `BlockLocation`, `ContentSummary`, and `FileChecksum` are serializable/value-like holders for filesystem metadata.
- `ChecksumFileSystem` maintains operational state around checksum verification and writing, and persists checksum files alongside raw files on the underlying filesystem.
- `FileContext` stores its default filesystem, working directory, user/group identity, and umask.

## Dependencies And Integration Points

The generated XML integrates with JDiff/Javadoc tooling rather than Hadoop runtime directly. It depends on the JDiff schema and the doclet classpath used during generation.

The APIs described here integrate with broad Hadoop Common subsystems:

- `Configuration` underpins almost every Hadoop component and integrates with XML resources, Java system properties, environment variables, class loading, local filesystem path selection, socket addressing, credential providers, and Writable serialization.
- Crypto key APIs integrate with Hadoop KMS and encryption users through `KeyProvider`, `KeyProviderFactory`, configured provider URIs, ServiceLoader discovery, and credential/password handling.
- Filesystem APIs integrate with `FileContext`, `AbstractFileSystem` implementations, classic `FileSystem` statistics, permissions/ACL packages, security `UserGroupInformation`, storage policy SPI, checksums, symlinks, xattrs, snapshots, Avro input, and stream capability interfaces.
- `CommonConfigurationKeysPublic` ties code constants to `core-default.xml` and the documented configuration surface for IO, IPC, security, KMS, and shell behaviors.

## Risks And Compatibility Notes

- As a generated API snapshot, stale generation inputs are the main risk. If the doclet classpath, annotations, sourcepath, or JDK differ, the XML may report a different API surface even for similar source.
- The file uses ISO-8859-1 encoding in the XML declaration; tools assuming UTF-8 without checking may still work for ASCII content but should preserve the declared encoding.
- The chunk is line-bounded and stops inside `FileContext.resolvePath`, so whole-file research must merge with later chunks before claiming complete `FileContext` coverage.
- Several docs mention deprecation even when XML metadata says `deprecated="not deprecated"`; examples include `ContentSummary` constructors being described as deprecated by `ContentSummary.Builder`. Compatibility consumers should prefer structured `deprecated` attributes for machine decisions but inspect docs for migration intent.
- Deprecated overloads in `Configuration.addDeprecation` and constants such as `IO_SORT_MB_KEY`/`IO_SORT_FACTOR_KEY` remain visible public API and therefore cannot be removed without API-compatibility impact.
- `Configuration` has shared static state and synchronized reload/default-resource methods. Tests or applications that mutate global deprecations/default resources can affect later code in the same JVM.
- `Configuration.addResource(InputStream)` caches stream contents and warns about memory use; large or numerous streams can increase heap pressure.
- `ByteBufferReadable`, drop-behind, and readahead are optional capabilities. Callers must handle unsupported operations and undefined buffer position/limit after exceptions.
- `AbstractFileSystem` path checks, symlink resolution, ACL/xattr semantics, and snapshot/storage-policy defaults are filesystem-specific extension points. Implementations must preserve the documented exception behavior for API compatibility.
- `KeyProvider` explicitly requires thread-safe implementations. Providers that cache metadata or key material must synchronize enough to satisfy concurrent encryption/decryption clients and `flush()` persistence expectations.

## Test Signals

Useful validation signals for this chunk and its represented APIs include:

- XML well-formedness against `api.xsd`, preservation of package/type nesting, and matching start/end class comments for all complete types in lines 1-6120.
- JDiff comparisons against adjacent Hadoop Common releases should flag public API changes in `Configuration`, `KeyProvider`, and filesystem contracts.
- Configuration tests should cover resource precedence, final parameters, variable expansion from config/system/env sources, deprecated-key aliasing, typed parsers, XML/JSON dumps, reload behavior, and global deprecation warnings.
- Key-provider tests should cover provider discovery by URI scheme, no-provider null behavior, create/roll/delete/get metadata flows, generated key material, password-required warnings/errors, thread safety, and `flush()` persistence.
- Filesystem contract tests should cover `AbstractFileSystem` factory lookup by `fs.AbstractFileSystem.<scheme>.impl`, URI scheme/authority validation, path qualification, working directory behavior through `FileContext`, create/open/delete/rename/list exceptions, symlink resolution, ACL/xattr defaults, snapshot/storage-policy operation fallbacks, and statistics accounting.
- Checksum filesystem tests should verify checksum-file naming, checksum length calculation, read verification, write checksum toggles, append/truncate behavior, checksum-aware rename/delete/listing, and checksum failure reporting.
- Stream capability tests should include supported and unsupported `ByteBufferReadable`, `CanSetDropBehind`, `CanSetReadahead`, and `CanUnbuffer` implementations, including exception recovery expectations.

## Cross-Chunk Continuations

The next chunk must continue `org.apache.hadoop.fs.FileContext` from the `resolvePath(Path)` documentation and cover the rest of the class. Whole-file synthesis should merge this chunk with later chunks before summarizing full Hadoop Common 2.8.3 API coverage.
