# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007179`: lines 1-6120, `Docs/researches/chunks/subset-b-007179_research.md`
- `subset-b-007180`: lines 6121-12035, `Docs/researches/chunks/subset-b-007180_research.md`
- `subset-b-007181`: lines 12036-17993, `Docs/researches/chunks/subset-b-007181_research.md`
- `subset-b-007182`: lines 17994-24297, `Docs/researches/chunks/subset-b-007182_research.md`
- `subset-b-007183`: lines 24298-30745, `Docs/researches/chunks/subset-b-007183_research.md`
- `subset-b-007184`: lines 30746-36809, `Docs/researches/chunks/subset-b-007184_research.md`
- `subset-b-007185`: lines 36810-38433, `Docs/researches/chunks/subset-b-007185_research.md`

## Chunk Research

### subset-b-007179: lines 1-6120

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

### subset-b-007180: lines 6121-12035

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml lines 6121-12035

## Scope

This chunk is a JDiff API snapshot for Hadoop Common 2.8.3, not executable source. It covers the tail of `org.apache.hadoop.fs.FileContext`, the complete public API entries for `FileStatus`, `FileSystem`, `FileUtil`, `FilterFileSystem`, `FsConstants`, `FSDataInputStream`, and the opening of `FSDataOutputStream`. The XML records public/protected signatures, inheritance, implemented interfaces, thrown exceptions, fields, deprecation state, and Javadoc text used for compatibility reporting.

## Purpose and major API surface

`FileContext` is represented from `makeQualified` through advanced filesystem operations. The covered methods expose create/open/delete/rename/truncate, mkdir, replication, permissions, owner/group/times, checksums, file and link status, symlink creation and resolution, status listing, corrupt-block listing, located listing, delete-on-exit, statistics, ACLs, xattrs, snapshots, and storage policies. Its class-level documentation frames `FileContext` as the per-client namespace context that resolves Hadoop URI paths, default filesystem paths, working-directory-relative paths, and umask-derived permissions while leaving most server-side defaults to each filesystem implementation.

`FileStatus` is the client-side metadata carrier for a path. It implements `Writable` and `Comparable`, with constructors for plain files/directories, symlink-aware status, and copy construction. Its API exposes length, type checks (`isFile`, `isDirectory`, deprecated `isDir`, `isSymlink`), block size, replication, modification/access time, permissions, encryption state, owner, group, path, symlink target, serialization (`write`, `readFields`), comparison, equality, hashing, and stringification.

`FileSystem` is the central abstract filesystem base class extending `Configured` and implementing `Closeable`. The covered API includes factory and cache methods (`get`, `newInstance`, `getLocal`, `closeAll`, `closeAllForUGI`), URI/canonicalization handling, service names for token caches, path qualification and validation, delegation tokens, create/open/append/concat/truncate/delete/rename, mkdirs and primitive create/mkdir helpers, block locations, server defaults, listing/globbing/iterators, local copy/move helpers, working directory and home directory, status/quota/used-space queries, symlink APIs, checksum controls, permissions/owner/times, snapshots, ACLs, xattrs, storage policies, trash roots, implementation class lookup, global statistics, symlink enablement, and storage statistics. Fields in this chunk include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, and an instance `statistics` object.

`FileUtil` is a static utility collection for filesystem and local-file operations. It converts `FileStatus[]` to `Path[]`, recursively deletes files/directories and directory contents, reads symlink targets, copies among `FileSystem` instances and local files, merges files, builds shell-safe paths, computes local disk usage, unzips/untars archives, creates symlinks, chmod/chown and permission helpers, portable readability/writability/executability helpers, temp-file creation, atomic-style replacement, null-safe wrappers around `File.listFiles()` and `File.list()`, classpath jar creation, and filesystem comparison. `SYMLINK_NO_PRIVILEGE` is the exposed constant for symlink privilege failure.

`FilterFileSystem` is a concrete `FileSystem` wrapper with an underlying `fs` field and optional `swapScheme`. Its public methods mirror much of `FileSystem` and delegate behavior to the raw filesystem: URI/canonical URI, path qualification, block locations, open/create/append/concat, non-recursive create, replication, rename, truncate, delete, listings, working directory, status, mkdirs, local copies, local output staging, usage/defaults/server defaults, file status, access checks, symlinks, checksums, configuration/close, owner/times/permissions, primitive operations, child filesystems, snapshots, ACLs, xattrs, storage policy, and trash roots.

`FsConstants` defines filesystem constants: `LOCAL_FS_URI`, `FTP_SCHEME`, `MAX_PATH_LINKS`, `VIEWFS_URI`, and `VIEWFS_SCHEME`. `FSDataInputStream` wraps an `FSInputStream` in a `DataInputStream`/buffered input utility and implements seekable positioned reads, byte-buffer reads, file-descriptor access, readahead/drop-behind controls, enhanced byte-buffer reads using `ByteBufferPool`, buffer release, unbuffering, and `toString`. `FSDataOutputStream` begins at the end of the chunk as a `DataOutputStream` implementing `Syncable` and `CanSetDropBehind`; only its class declaration and first constructor are visible here.

## Control flow and behavioral contracts

Because this is JDiff XML, direct control flow is absent. The behavioral contracts are expressed as public API shape and Javadoc. `FileContext` and `FileSystem` operations consistently route through `Path`, `URI`, `Configuration`, `FsPermission`, `Options.CreateOpts`, `CreateFlag`, and filesystem-specific implementations. Many methods document RPC-specific exception surfaces (`RpcClientException`, `RpcServerException`, `UnexpectedServerException`) even when the Java signature exposes `IOException` subclasses, indicating that remote filesystem integrations must preserve exception compatibility.

Factory flow for `FileSystem` is configuration driven. Static `get` resolves the configured/default URI or the supplied URI and may return cached instances, while `newInstance` returns unique configured implementations. `closeAll` and `closeAllForUGI` manage cached instances and are tied to shutdown-hook behavior. `makeQualified`, `checkPath`, `resolvePath`, and canonical URI methods define the path-normalization flow before operations reach concrete filesystems.

File mutation flow is represented by layered overloads. High-level `create` overloads supply defaults and progress callbacks, lower-level `primitiveCreate` and `primitiveMkdir` expose absolute-permission variants, and `createNonRecursive` requires the parent to already exist. `append`, `concat`, `truncate`, `rename`, and `delete` are optional or implementation-sensitive operations; callers must interpret booleans and documented exceptions rather than assuming uniform support across local, HDFS, viewfs, FTP, or filter filesystems.

Read flow centers on `FSDataInputStream`: callers can `seek`, query `getPos`, perform positioned reads without changing stream position, `readFully`, seek to a new source replica, read into `ByteBuffer`, request readahead/drop-behind, obtain a `FileDescriptor` where supported, and release pooled buffers. The optional `UnsupportedOperationException` contracts on buffer/readahead/drop-behind operations are important integration signals for filesystem implementations.

## State, persistence, and side effects

The APIs here operate on persistent filesystem namespace and metadata: file contents, directories, symlinks, permissions, owner/group, times, ACLs, xattrs, snapshots, storage policies, replication, checksums, and trash roots. `FileStatus` itself is a serializable metadata snapshot and does not mutate the backing filesystem except through setters that alter the local status object fields.

`FileContext` carries client-side namespace state: default filesystem, working directory, and umask. `FileSystem` carries configuration, URI identity, cached global instances, statistics, storage statistics, shutdown behavior, and delete-on-exit queues. `deleteOnExit`, `cancelDeleteOnExit`, and `processDeleteOnExit` are stateful and can delete paths later at close/shutdown time, so tests and callers must isolate them carefully.

`FileUtil` has substantial local side effects. Recursive delete can partially delete on failure; archive extraction writes directory trees; chmod/chown/symlink helpers call platform facilities; `replaceFile` moves local files; `createJarWithClassPath` emits jar artifacts. Null-safe listing wrappers convert problematic `java.io.File` null returns into checked `IOException` behavior for callers.

`FilterFileSystem` persists no independent namespace data in this API snapshot. Its important state is the wrapped raw `FileSystem`; behavior, statistics, permissions, and lifecycle are expected to pass through to that delegate unless a subclass overrides.

## Dependencies and integration points

The chunk integrates heavily with Hadoop Common types: `Path`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `BlockLocation`, `FsServerDefaults`, `FsStatus`, `ContentSummary`, `QuotaUsage`, `RemoteIterator`, `PathFilter`, `Options.Rename`, `Options.ChecksumOpt`, `Options.CreateOpts`, `CreateFlag`, `BlockStoragePolicySpi`, `StorageStatistics`, `GlobalStorageStatistics`, ACL and xattr types, `FsPermission`, `AclEntry`, `AclStatus`, `XAttrSetFlag`, `Configuration`, `UserGroupInformation`, `Token`, and `ByteBufferPool`.

Java and platform integration points include `URI`, `File`, `FileDescriptor`, `InputStream`, `OutputStream`, `DataInputStream`, `DataOutputStream`, `EnumSet`, `Map`, `Collection`, `List`, `Comparable`, `Closeable`, and `Writable`. Security and remote execution concerns surface through `AccessControlException`, token service names, delegation tokens, RPC exception documentation, and UGI-scoped filesystem cache closing.

Concrete implementations are intentionally abstracted. The class docs call out local filesystem and HDFS as common implementations, while constants and APIs also account for FTP and viewfs. `FilterFileSystem` is the extension point for wrappers that adapt or decorate another `FileSystem`, so compatibility of delegated method semantics is central.

## Risks and compatibility concerns

JDiff files are consumed as compatibility baselines, so signature changes, visibility changes, exception changes, deprecation changes, and Javadoc contract drift can be compatibility risks even if implementation code compiles. The very broad `FileSystem` overload surface increases the chance of accidental binary/API incompatibility.

Path qualification and symlink resolution are high-risk areas. `FileContext` allows fully qualified, slash-relative, and working-directory-relative names, while explicitly rejecting scheme-relative names like `scheme:foo/bar`. `MAX_PATH_LINKS` signals loop protection for symlink traversal. Implementations must preserve resolution and exception behavior across local, distributed, and view filesystems.

Stateful lifecycle APIs can surprise callers. Cached `FileSystem` instances share configuration and statistics; `newInstance` intentionally avoids cache reuse; shutdown hooks and delete-on-exit can perform late deletes; `closeAllForUGI` affects all filesystems for a user. Tests should avoid order dependence and clean global state.

Optional operations are common. Append, concat, truncate, symlink operations, ACLs, xattrs, storage policies, byte-buffer reads, readahead/drop-behind, file descriptors, and snapshots can throw `UnsupportedOperationException` or filesystem-specific `IOException`. Callers and wrapper implementations must not silently assume HDFS semantics for all schemes.

`FileUtil` utilities are platform-sensitive. Symlinks, chmod/chown, shell paths, archive extraction, and local permission checks vary across operating systems and privilege contexts. Recursive deletion methods document partial deletion on failure, which is a critical cleanup risk.

## Test signals

Compatibility tests should parse this XML and confirm the presence and signatures of the covered public/protected APIs, especially overloaded `FileSystem.create`, `createNonRecursive`, `open`, `listStatus`, `globStatus`, `copyFromLocalFile`, `copyToLocalFile`, ACL/xattr/storage-policy methods, and `FSDataInputStream` byte-buffer methods.

Behavioral tests in the underlying Hadoop codebase should cover path qualification/default-FS resolution, working-directory-relative paths, symlink resolution and loop limits, filesystem cache versus `newInstance`, UGI-scoped close behavior, delete-on-exit processing, statistics clearing/printing, and token aggregation.

Filesystem integration tests should exercise local and distributed implementations through `FileSystem`, `FileContext`, and `FilterFileSystem` wrappers to verify delegation preserves URI, status, listing, permissions, checksums, snapshots, xattrs, ACLs, storage policy, and trash-root behavior.

Local utility tests should cover recursive delete success and partial-failure behavior, symlink delete semantics, null-safe local listing wrappers, archive extraction, permission helper portability, classpath jar creation, and atomic replacement behavior. Stream tests should cover positioned reads, `readFully`, `seekToNewSource`, byte-buffer reads with `ByteBufferPool`, `releaseBuffer`, `unbuffer`, and unsupported-operation paths.

### subset-b-007181: lines 12036-17993

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml lines 12036-17993

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.8.3. It starts inside the public API entry for `org.apache.hadoop.fs.FSDataOutputStream`, continues through a large part of `org.apache.hadoop.fs`, `org.apache.hadoop.fs.ftp`, `org.apache.hadoop.fs.permission`, `org.apache.hadoop.fs.viewfs`, `org.apache.hadoop.ha`, and the beginning of `org.apache.hadoop.io`, and ends inside `org.apache.hadoop.io.FloatWritable`.

The source is generated compatibility metadata, not implementation source. The research surface is therefore the externally visible contract: class and interface names, inheritance, implemented interfaces, constructors, fields, method signatures, exceptions, visibility, static/final/abstract/synchronized flags, deprecation state, and embedded Javadocs.

## Purpose

The `org.apache.hadoop.fs` portion documents Hadoop's core filesystem client contracts and several concrete filesystem implementations. It covers seekable and positioned input streams, output streams with flush/sync/drop-behind hooks, server default and status records, global storage statistics, path parsing and qualification, local filesystem implementations, quota accounting, storage types, trash policies, xattr encoding, and FileSystem/FileContext-facing abstractions such as `PathFilter`, `Seekable`, `PositionedReadable`, and `Syncable`.

The `org.apache.hadoop.fs.ftp` portion exposes an FTP-backed `FileSystem` and its exception type. It adapts Hadoop filesystem calls to an FTP server with configuration keys for host, port, user, and password, but its public API also signals limited semantics such as same-directory rename restrictions.

The `org.apache.hadoop.fs.permission` portion documents filesystem authorization value objects: ACL entries and statuses, action masks, permission bits, sticky/ACL/encryption extended bits, umask handling, and access-control exceptions.

The `org.apache.hadoop.fs.viewfs` portion documents both `ViewFileSystem` and `ViewFs`, Hadoop's mount-table based namespace overlay implementations. They route filesystem calls through configured mount links and expose mount-point inspection, path resolution, trash location, ACL/xattr/snapshot/storage-policy forwarding, and delegation-token aggregation.

The `org.apache.hadoop.ha` portion documents public HA control contracts: fencing configuration and execution, health monitoring, active/standby transitions, service status polling, target address/proxy discovery, and failure exception types. The PB protocol marker interfaces identify protobuf-backed RPC protocol surfaces.

The early `org.apache.hadoop.io` portion documents Writable and serialization utilities: class-id maps for heterogeneous maps, primitive/object array wrappers, binary comparison helpers, Bloom map-file metadata, primitive Writables, byte-buffer pooling, compressed lazy Writables, stringification through Hadoop serialization, and writable wrappers for enum sets.

## Important APIs, Types, and Functions

### Core FS Streams and Records

- `FSDataOutputStream` constructors wrap an `OutputStream` with `FileSystem.Statistics` and optionally a starting position. The visible methods include `getPos()`, `close()`, deprecated-style `sync()` compatibility, `hflush()`, `hsync()`, and `setDropBehind(Boolean)`.
- `FSError` is a public `Error` for unexpected filesystem failures assumed to reflect native disk problems.
- `FSInputStream` is an abstract `InputStream` implementing `Seekable` and `PositionedReadable`. It defines abstract `seek(long)`, `getPos()`, and `seekToNewSource(long)`, plus positioned `read(...)`, validation helper `validatePositionedReadArgs(...)`, and `readFully(...)` overloads.
- `FsServerDefaults` is a `Writable` carrier for server-side defaults such as block size, checksum bytes, packet size, replication, file-buffer size, encrypted data-transfer flag, trash interval, checksum type, key-provider URI, and default storage-policy ID.
- `FsStatus` is a `Writable` capacity summary with capacity, used, and remaining byte counts.
- `LocatedFileStatus` extends `FileStatus` with block locations while preserving equality, comparison, and hash behavior from file status semantics.

### Path, Filtering, and Positioned IO

- `Path` is the central URI-like path abstraction. Constructors accept string parent/child pairs, `Path` parent/child pairs, raw strings, `URI`, and scheme/authority/path components.
- `Path` static helpers include `getPathWithoutSchemeAndAuthority(Path)`, `mergePaths(Path, Path)`, and `isWindowsAbsolutePath(String, boolean)`.
- `Path` instance methods expose URI conversion, filesystem lookup from `Configuration`, absolute/root/name/parent/suffix/depth checks, qualification against a default URI and working directory, string conversion, equality, hashing, and ordering.
- Public `Path` constants include `SEPARATOR`, `SEPARATOR_CHAR`, `CUR_DIR`, and `WINDOWS`.
- `PathFilter.accept(Path)` is the single-method filter contract; `GlobFilter` implements it with POSIX glob patterns plus an optional user filter and a `hasPattern()` query.
- `PositionedReadable` declares positioned `read` and `readFully` overloads. `Seekable` declares `seek(long)` and `getPos()`. `Syncable` declares `sync()`, `hflush()`, and `hsync()`.

### Local and Remote Filesystems

- `LocalFileSystem` extends `ChecksumFileSystem`, initializes from URI/configuration, exposes the raw wrapped filesystem, translates `Path` to `File`, handles local copy operations, reports checksum failures, and forwards symlink operations.
- `RawLocalFileSystem` extends `FileSystem` directly and exposes local operations including `open`, `append`, multiple `create` and `createNonRecursive` overloads, output stream creation with permission modes, `rename`, Windows empty-directory handling, `truncate`, `delete`, `listStatus`, mkdir helpers, home/working directory handling, status reporting, local-output staging, ownership/permission/time setters, symlink support, and link status/target access.
- `FTPFileSystem` exposes the `ftp` scheme, default port, initialization, open/create/append/delete/list/status/mkdirs/rename/working-directory operations, and FTP configuration constants such as `FS_FTP_HOST`, `FS_FTP_HOST_PORT`, `FS_FTP_USER_PREFIX`, and `FS_FTP_PASSWORD_PREFIX`.
- `UnsupportedFileSystemException`, `ParentNotDirectoryException`, `InvalidPathException`, `FTPException`, and viewfs `NotInMountpointException` provide typed failure surfaces for invalid paths, unsupported schemes, mount-table violations, and FTP failures.

### Quotas, Storage, Trash, and XAttrs

- `QuotaUsage` records file/directory count, namespace quota, space consumed, space quota, and per-`StorageType` quota/consumption. It has builder-based construction, setters used by subclasses, getters, type-quota availability checks, equality/hash, header formatting, and quota display formatting.
- `StorageStatistics` is an abstract named statistics source with a nullable scheme, iterator over long statistics, keyed long lookup, tracking checks, and reset.
- `GlobalStorageStatistics` is a singleton-style enum registry with synchronized `get`, `put`, `reset`, and `iterator` methods. `put` uses a `StorageStatisticsProvider` and validates that created statistics are non-null and correctly named.
- `StorageType` is an enum with transient, movable, and quota-support queries; parsing helpers; list helpers for movable and quota-supporting types; and `DEFAULT`/`EMPTY_ARRAY` fields.
- `Trash` wraps trash policy use for a filesystem/configuration. It supports `moveToAppropriateTrash`, `isEnabled`, `moveToTrash`, checkpointing, expunging, emptier creation, and current-trash-dir lookup.
- `TrashPolicy` is the abstract policy base with initialization by configuration and filesystem/home, enabled checks, trash movement, checkpoint create/delete, trash-dir lookup with optional path, emptier creation, and static `getInstance` factories. Protected state includes `fs`, `trash`, and `deletionInterval`.
- `XAttrCodec` encodes and decodes xattr values using named codecs. `XAttrSetFlag.validate(EnumSet<XAttrSetFlag>, boolean)` checks create/replace flag combinations against existence state.

### Permissions and ACLs

- `AccessControlException` extends `IOException` with no-arg, message, and throwable constructors.
- `AclEntry` exposes type, optional name, permission action, scope, equality/hash, string rendering, stable string rendering, ACL spec parsing, single-entry parsing, and ACL list serialization.
- `AclEntryScope` and `AclEntryType` are enums. `AclEntryType` has display and stable string forms.
- `AclStatus` exposes owner, group, sticky bit, entries, optional `FsPermission`, equality/hash, string rendering, and effective permission computation for an ACL entry, optionally with a permission argument.
- `FsAction` is an enum-style permission mask with implication, `and`, `or`, `not`, symbolic string, and `getFsAction(String)` parsing.
- `FsPermission` is a `Writable` for user/group/other actions and extended permission bits. It supports construction from actions, shorts, another permission, and symbolic strings; immutable creation; `fromShort`; read/write serialization; static `read(DataInput)`; short and extended-short conversion; umask application and configuration getters/setters; sticky/ACL/encrypted bit accessors; default permission factories; `valueOf(String)`; and public constants for max symbolic length and umask config keys.

### Viewfs Namespace Overlays

- `ViewFileSystem` extends `FileSystem` and provides the `viewfs` scheme. It initializes from a mount-table configuration, resolves paths, exposes mount points and child filesystems, and forwards broad filesystem operations to target filesystems: append/create/delete/list/open/rename/truncate/status/checksum/block locations/access/ACL/xattr/snapshot/quota/server-default/storage-setting operations.
- `ViewFs` is the FileContext-oriented counterpart. It exposes server defaults, default port, home directory, path resolution, internal create, delete, block/checksum/status/link status, filesystem status, status iterators, mkdir, open, truncate, rename internals, symlink support, owner/permission/replication/time setters, mount points, delegation tokens, name validation, ACL/xattr/snapshot/storage-policy operations, and block storage-policy lookup.
- `NotInMountpointException` preserves the offending path and operation context through its constructors and custom message.

### HA Contracts

- `FenceMethod` defines `checkArgs(String)` and `tryFence(HAServiceTarget, String)`, allowing pluggable fencing implementations with separate argument validation and execution.
- `HAServiceProtocol` declares RPC-facing methods `monitorHealth()`, `transitionToActive(StateChangeRequestInfo)`, `transitionToStandby(StateChangeRequestInfo)`, and `getServiceStatus()`. It exposes a `versionID` field for protocol compatibility.
- `HAServiceProtocolHelper` provides static wrappers around health checks and active/standby transitions, likely centralizing remote exception handling.
- `HAServiceTarget` abstracts a failover target and exposes service, health-monitor, and ZKFC addresses; fencer lookup and validation; RPC proxy creation for service/health/ZKFC protocols; fencing-parameter maps; parameter augmentation; and auto-failover availability.
- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` expose typed HA failure modes.
- `HAServiceProtocolPB` and `ZKFCProtocolPB` are protobuf protocol interfaces extending `VersionedProtocol`.

### Writable and IO Utilities

- `AbstractMapWritable` is a configurable base for maps that serialize classes via byte IDs. It supports adding mappings, reverse lookup by class or ID, copying another map's class table, `getConf`/`setConf`, and `write`/`readFields`.
- `ArrayPrimitiveWritable` wraps primitive arrays with component-type tracking, declared-component-type checks, setters, getters, and Writable serialization.
- `ArrayWritable` wraps arrays of `Writable`, including a string-array constructor, value-class access, conversion to strings/object arrays, set/get, and read/write.
- `BinaryComparable` is an abstract byte-sequence comparable with `getLength()`, `getBytes()`, byte-array comparison, equality, and hashing.
- `BloomMapFile` exposes Bloom-filter metadata constants and a static `delete(FileSystem, String)` helper for deleting a Bloom map file.
- `BooleanWritable`, `ByteWritable`, `DoubleWritable`, and the start of `FloatWritable` are primitive `WritableComparable` wrappers with zero/value constructors, `set`, `get`, `readFields`, `write`, equality, hash, comparison, and string conversion where visible.
- `ByteBufferPool` declares direct/heap buffer checkout and return. `ElasticByteBufferPool` implements it with synchronized `getBuffer(boolean, int)` and `putBuffer(ByteBuffer)`.
- `BytesWritable` extends `BinaryComparable` for mutable byte arrays. It exposes copy and backing-array access, length and capacity management, multiple `set` forms, serialization, equality/hash, and hex-like string rendering.
- `Closeable` is an `io` package interface marker in this slice.
- `CompressedWritable` is an abstract lazy compressed `Writable`. Final `readFields` stores compressed bytes; `ensureInflated()` inflates on demand; subclasses implement `readFieldsCompressed(DataInput)` and `writeCompressed(DataOutput)`; final `write` writes compressed representation.
- `DataOutputOutputStream.constructOutputStream(DataOutput)` adapts a `DataOutput` to an `OutputStream`, reusing it directly if it already is an `OutputStream`.
- `DefaultStringifier<T>` implements `Stringifier<T>` using Hadoop serialization plus base64. It converts objects to/from strings, closes underlying resources, and stores/loads single objects or arrays in `Configuration`.
- `EnumSetWritable<E>` wraps `EnumSet` with explicit element-type tracking for null or empty sets, implements `Writable` and `Configurable`, and exposes collection operations, value/element-type getters, serialization, equality/hash, string rendering, and configuration access.

## Control Flow

The XML has no runtime control flow, but the APIs imply several important execution paths.

For stream reads, callers either use `Seekable` stateful positioning (`seek`, then normal reads) or `PositionedReadable` stateless positional reads. `FSInputStream.readFully` builds on repeated positioned reads until the requested length is satisfied or an exception is raised. Implementations are expected to validate negative positions and buffer bounds before touching storage.

For output streams, clients write through `FSDataOutputStream`, query `getPos`, then choose durability semantics through `hflush`, `hsync`, or legacy `sync`. `setDropBehind(Boolean)` is an advisory cache-control path that may be ignored or forwarded by concrete streams.

Filesystem operations flow through `FileSystem` or FileContext implementations. `LocalFileSystem` wraps a checksum-aware layer over a raw local filesystem, while `RawLocalFileSystem` directly maps Hadoop paths to local `File` operations. `FTPFileSystem` maps the same abstract methods to FTP commands. `ViewFileSystem` and `ViewFs` first resolve an incoming path against the mount table, then delegate the operation to the target filesystem; mount-table failures surface as viewfs-specific exceptions.

Path handling flows from constructor normalization to URI conversion and qualification. `Path.getFileSystem(conf)` uses the path URI and configuration to resolve a `FileSystem`, while `makeQualified` fills in missing scheme/authority and resolves relative paths against a working directory.

Trash flow is policy-driven. `Trash` constructs or obtains a `TrashPolicy`, checks whether trash is enabled, moves deleted paths into a current trash directory, creates checkpoints, expunges old checkpoints, and can return a background emptier `Runnable`.

Permission and ACL parsing flow from string specs into typed `AclEntry` or `FsPermission` values. Effective ACL permission computation combines an ACL entry with group-mask or permission state, depending on the overload and whether `AclStatus` carries an `FsPermission`.

HA control flow starts with `HAServiceTarget` address/proxy discovery, runs health checks through `HAServiceProtocol.monitorHealth`, performs state transitions with `StateChangeRequestInfo`, and invokes fencing through configured `FenceMethod`/`NodeFencer` support when failover requires the old active to be isolated. Helper methods provide a static wrapper layer for common protocol calls.

Writable control flow follows Hadoop's `write(DataOutput)` and `readFields(DataInput)` convention. Primitive wrappers read/write their primitive values directly. Array wrappers include component-type or value-class metadata. `AbstractMapWritable` serializes a class-to-ID table before map entries in subclasses. `CompressedWritable` defers decompression until field access via `ensureInflated`.

## State and Persistence Behavior

This JDiff file persists the 2.8.3 public API for compatibility comparison. It does not contain Hadoop runtime state, but many documented APIs define durable or process-local state contracts.

`Path` instances persist normalized URI components in memory and are frequently serialized indirectly as strings by callers. Compatibility depends on stable normalization, equality, ordering, and qualification behavior, especially across Windows and Unix path forms.

`FsServerDefaults`, `FsStatus`, `QuotaUsage`, `FsPermission`, array Writables, primitive Writables, `BytesWritable`, `EnumSetWritable`, `AbstractMapWritable`, and `CompressedWritable` define explicit or inherited serialized forms through Writable methods. Any change to field order, encoded type IDs, component-type names, or extended permission bits can break cross-version data exchange.

`GlobalStorageStatistics` is process-global mutable state. Its registry is synchronized for `get`, `put`, `reset`, and iteration, and providers must return objects with matching names. Storage statistics are not durable by themselves, but they are integration points for metrics reporting and diagnostics.

`TrashPolicy` carries protected mutable state for the target filesystem, trash root, and deletion interval. `Trash` operations persist data by renaming/moving user files into trash directories and by creating/deleting checkpoint directories on the underlying filesystem.

`RawLocalFileSystem` persists state directly to the host filesystem: created files, appended data, permissions, owners, timestamps, symlinks, deletes, truncation, and directory creation. `LocalFileSystem` also manages checksum side files through the inherited checksum layer.

`FTPFileSystem` persists state remotely through FTP server operations. Since FTP has weaker metadata and atomicity semantics than HDFS/local filesystems, rename, append, permission, and listing behavior may differ from richer implementations.

`ViewFileSystem` and `ViewFs` generally do not own file content; their persistent behavior is delegated to target filesystems selected by the mount table. Their own state is the in-memory mount-table resolution data built during initialization from `Configuration`.

`HAServiceTarget` stores or derives target addresses, fencer configuration, fencing parameters, and auto-failover availability. State transitions persist in the HA service being controlled, not in the protocol object itself.

`DefaultStringifier` persists serialized objects into `Configuration` values as base64 strings. This makes object persistence dependent on the configured Hadoop `Serialization` implementation and class compatibility.

`ElasticByteBufferPool` keeps process-local buffer caches split by direct/heap choice and capacity. Its Javadocs explicitly say it does not cap maximum cache size, so returned buffers can be retained for reuse until the pool is discarded.

## Dependencies and Integration Points

This chunk depends heavily on Java platform types: `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `File`, `URI`, `InetSocketAddress`, `ByteBuffer`, arrays, collections, enums, `IOException`, and related exception types.

Key Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configurable` for filesystem initialization, path qualification, umask/defaults, viewfs mount tables, stringifier serialization selection, and `EnumSetWritable` configuration.
- `org.apache.hadoop.fs.FileSystem`, `FileContext`-style classes, `FileStatus`, `BlockLocation`, `FileChecksum`, `ContentSummary`, `RemoteIterator`, `FsStatus`, `FsServerDefaults`, and `BlockStoragePolicySpi` for filesystem operations.
- `org.apache.hadoop.fs.permission` types across ACL, access, and permission APIs, including `FsAction`, `FsPermission`, `AclEntry`, and `AclStatus`.
- `org.apache.hadoop.io.Writable`, `WritableComparable`, `Stringifier`, and Hadoop serialization infrastructure for durable binary/string encoding.
- `org.apache.hadoop.util.DataChecksum.Type` for server default checksum metadata.
- `org.apache.hadoop.security.AccessControlException`, delegation token types, and HA RPC protocol classes for authorization, token collection, and service control.
- `org.apache.hadoop.ipc.VersionedProtocol` and protobuf protocol interfaces for HA and ZKFC RPC compatibility.
- `org.apache.hadoop.fs.viewfs` mount-table configuration, which is the central integration point for namespace overlays.
- Apache Commons Logging in `FTPFileSystem.LOG`.

Package markers for `org.apache.hadoop.fs.crypto`, `org.apache.hadoop.fs.sftp`, `org.apache.hadoop.fs.shell.find`, and `org.apache.hadoop.http.lib` appear in this span without public classes in the listed lines.

## Risks and Edge Cases

- This chunk starts in the middle of `FSDataOutputStream` and ends in the middle of `FloatWritable`; adjacent chunks are required for complete class reports.
- JDiff metadata omits method bodies. Exact validation details, path normalization rules, FTP command behavior, viewfs resolution mechanics, HA remote exception translation, and Writable byte layouts require implementation-source review.
- `FSInputStream` implementations must keep stateful seek and stateless positioned reads coherent. Bugs can corrupt callers that mix normal reads, `seek`, and positional reads concurrently.
- `readFully` must handle short reads and EOF accurately. Returning early or swallowing EOF breaks consumers that rely on full-buffer semantics.
- `FSDataOutputStream.sync`, `hflush`, and `hsync` have distinct durability expectations in Hadoop. Filesystems that silently weaken these operations can create data-loss surprises.
- `setDropBehind(Boolean)` is advisory and nullable. Implementations and callers must tolerate unsupported cache hints and a null "restore default" value.
- `Path` has platform-sensitive Windows absolute-path handling. Changes in URI parsing, authority stripping, or qualification can break cross-platform applications and serialized path strings.
- `RawLocalFileSystem` maps Hadoop permissions and ownership to host OS behavior. Permission, symlink, truncation, and rename semantics vary across Unix and Windows.
- `handleEmptyDstDirectoryOnWindows` indicates a platform-specific rename edge case for empty destination directories; changes here can break Windows compatibility.
- `FTPFileSystem` exposes mutable remote state through a protocol with limited atomicity and metadata fidelity. Same-directory rename constraints, missing append support, partial transfers, and connection failures are high-risk paths.
- `QuotaUsage` per-storage-type accounting depends on `StorageType` support and availability checks. Callers must distinguish unset quota from unavailable consumed values.
- `GlobalStorageStatistics` is synchronized but process-global. Duplicate names, wrong provider behavior, or reset during metrics collection can affect unrelated filesystem instances.
- `StorageType.parseStorageType` has a `fallback` overload. Incorrect fallback use can hide invalid configuration.
- Trash behavior is configuration-sensitive. Disabled trash, wrong trash roots, checkpoint deletion, and cross-filesystem moves can lead to permanent deletion or unexpected storage consumption.
- `XAttrSetFlag.validate` must enforce create/replace combinations precisely; accepting contradictory flags can overwrite or fail to create attributes unexpectedly.
- ACL string parsing must preserve stable string forms for compatibility with CLI output, audit logs, and tests.
- `FsPermission` has multiple representations: symbolic string, short, extended short, sticky bit, ACL bit, encrypted bit, and umask configuration. Losing extended bits during conversion is a compatibility and security risk.
- `ViewFileSystem` and `ViewFs` must guard mount boundaries carefully. Operations such as rename, snapshot, ACL, xattr, storage policy, and trash may not be valid across target filesystems.
- Delegation-token aggregation in `ViewFs` must avoid duplicates while still collecting every target filesystem token needed by distributed jobs.
- HA fencing APIs are safety-critical. A `FenceMethod` that validates arguments but returns true without isolating the old active can permit split brain.
- HA transition methods can throw `ServiceFailedException`, `AccessControlException`, and `IOException`; callers need clear retry and failure policies.
- `HAServiceTarget.getProxy` overloads include timeout parameters. Incorrect timeout selection can make failover too slow or too eager.
- `AbstractMapWritable` uses byte IDs for classes. ID collisions or incompatible class-table evolution can break deserialization.
- `ArrayPrimitiveWritable` must reject non-primitive or mismatched component types where declared. Otherwise serialized data can be misread.
- `BytesWritable.getBytes()` and deprecated-style `get()` expose backing storage, while `copyBytes()` returns a defensive copy. Callers that ignore `getLength()` can read stale capacity bytes.
- `BytesWritable.setCapacity` and `setSize` can retain or discard backing bytes; tests should cover growth, shrinkage, and serialization length.
- `CompressedWritable.ensureInflated()` is a required precondition before field access by subclasses. Missing calls can read stale or null inflated fields.
- `DefaultStringifier` persistence is only stable when the same serialization framework and compatible item class are available when loading.
- `ElasticByteBufferPool` has no maximum cache-size policy. High-cardinality capacity requests or returning very large buffers can produce unbounded memory retention.
- `EnumSetWritable` allows null or empty values only when an element type is known. Serialization must preserve that type even when the set has no elements.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks that confirm every public/protected class, interface, field, constructor, method, exception, visibility flag, and deprecation marker in this JDiff range remains stable for Hadoop Common 2.8.3.
- `FSInputStream` tests for negative positioned reads, buffer bounds validation, short read loops in `readFully`, EOF handling, `seek/getPos` consistency, and `seekToNewSource` behavior.
- `FSDataOutputStream` tests for position tracking, close propagation, `hflush`/`hsync`/`sync` delegation, and nullable drop-behind handling.
- `FsServerDefaults` and `FsStatus` Writable round-trip tests with all fields, including key provider URI and default storage-policy ID.
- `Path` tests for all constructors, URI conversion, scheme/authority stripping, path merging, Windows absolute paths, root/parent/name/suffix/depth behavior, comparison/equality/hash, and qualification against default URI plus working directory.
- `GlobFilter` tests for simple globs, brace expansion, invalid patterns, user-filter composition, and `hasPattern`.
- `LocalFileSystem` and `RawLocalFileSystem` tests for create/open/append/delete/rename/truncate/list/mkdirs/status, checksum-failure reporting, symlink support, permission/owner/time setters, local-output staging, and Windows-specific rename behavior.
- `FTPFileSystem` integration tests with a controlled FTP server for configuration parsing, default port, open/create/delete/list/status/mkdirs/rename, working directory, unsupported append behavior if applicable, and same-directory rename restrictions.
- `QuotaUsage` tests for namespace and space quotas, per-storage-type quota/consumption, unset/unavailable states, headers, display formatting, equality, and hash code.
- `StorageStatistics` and `GlobalStorageStatistics` tests for provider validation, duplicate-name behavior, synchronized registry access, iterator snapshots, reset, keyed lookups, and scheme reporting.
- `StorageType` tests for transient/movable/quota-support flags, parsing with and without fallback, and list helpers.
- `Trash` and `TrashPolicy` tests for disabled/enabled trash, move-to-trash success and failure, current trash dir calculation, checkpoint creation/deletion, expunge, emptier scheduling, and policy selection from configuration.
- `XAttrCodec` tests for text/hex/base64 encode/decode variants and invalid values; `XAttrSetFlag.validate` tests for create/replace/existence combinations.
- Permission and ACL tests for `AclEntry` parsing and stable rendering, ACL spec list parsing, ACL status effective-permission calculations, `FsAction` algebra, `FsPermission` symbolic/short/extended-short conversions, sticky/ACL/encrypted bits, umask config migration, default factories, and Writable round trips.
- `ViewFileSystem` and `ViewFs` tests for mount-table initialization, path resolution, mount-point listing, delegation to target filesystems, cross-mount rename failures, ACL/xattr/snapshot/storage-policy forwarding, child filesystem and delegation-token aggregation, and not-in-mountpoint errors.
- HA tests for fencing argument validation, fencing success/failure propagation, health monitoring, active/standby transition calls, service status retrieval, target proxy timeout handling, fencing parameter composition, ZKFC proxy lookup, and auto-failover flags.
- Protocol compatibility tests for `HAServiceProtocol.versionID`, `HAServiceProtocolPB`, and `ZKFCProtocolPB`.
- `AbstractMapWritable` tests for class-to-ID registration, copy behavior, unknown class/ID handling, configuration propagation, and serialized class-table compatibility.
- `ArrayPrimitiveWritable` and `ArrayWritable` tests for component/value class preservation, primitive type coverage, empty arrays, string-array conversion, set/get behavior, and Writable round trips.
- `BinaryComparable` and `BytesWritable` tests for lexicographic comparison, backing-array versus copied-array behavior, length/capacity resizing, equality/hash, serialization length, and string rendering.
- Primitive Writable tests for Boolean, Byte, Double, and Float constructors, setters/getters, read/write, comparison, equality/hash, and string conversion.
- `ByteBufferPool` and `ElasticByteBufferPool` tests for direct versus heap buffers, minimum requested capacity, reuse after return, synchronized concurrent access, and large-buffer retention behavior.
- `CompressedWritable` subclass tests verifying lazy inflation, final read/write paths, repeated `ensureInflated`, and compatibility of compressed serialized bytes.
- `DataOutputOutputStream` tests for direct reuse when the `DataOutput` is already an `OutputStream` and byte/array writes through the adapter.
- `DefaultStringifier` tests for object and array store/load in `Configuration`, empty-array behavior, close idempotence, missing serialization failures, and class compatibility errors.
- `EnumSetWritable` tests for non-empty, empty, and null enum sets with element type; add/iterator/size behavior; config propagation; equality/hash; string output; and serialized round trips.

## Cross-Chunk Notes

The previous chunk is required to complete `FSDataOutputStream`; this chunk begins at its constructors and later methods after earlier class metadata. The next chunk is required to complete `FloatWritable`; this chunk includes only its constructors, `set`, `get`, `readFields`, and the opening of `write`.

Several classes referenced here have nested builders, mount-point records, providers, or protocol request/status types whose definitions are outside this exact line range. The merge lane should reconcile those adjacent definitions before producing a final per-file report for `Apache_Hadoop_Common_2.8.3.xml`.

### subset-b-007182: lines 17994-24297

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml lines 17994-24297

## Scope

This chunk is a JDiff public API snapshot for Apache Hadoop Common 2.8.3. The range starts at the tail of `org.apache.hadoop.io.FloatWritable`, covers most of the `org.apache.hadoop.io` serialization and binary-file API surface, the `org.apache.hadoop.io.compress` codec contracts, TFile helper APIs, serializer registrations including Avro serializers, log/metrics appenders and legacy metrics package documentation, and ends inside `org.apache.hadoop.metrics.spi.AbstractMetricsContext.close`. It is metadata and Javadoc, not implementation code, but it records public signatures, inheritance, deprecation state, exceptions, and file/stream format contracts that downstream compatibility depends on.

## Purpose

The central purpose of this slice is to define Hadoop Common's stable data interchange layer:

- `Writable`, `WritableComparable`, primitive writable wrappers, `Text`, map writables, object/generic writables, raw comparators, factories, and utility methods describe Hadoop's compact `DataInput`/`DataOutput` serialization protocol for MapReduce keys, values, RPC payloads, and persisted files.
- `SequenceFile`, `MapFile`, and `SetFile` document binary container formats used for flat key/value data, sorted file-backed maps, and sets.
- `WritableUtils`, `Text`, `MD5Hash`, and `WritableComparator` provide low-level byte encodings, zero-compressed integers, raw byte comparison, hashing, UTF-8 handling, and clone/read/write helpers.
- `org.apache.hadoop.io.compress` defines codec lookup, compression/decompression stream lifecycle, compressor pools, splittable compression, and direct `ByteBuffer` decompression.
- `org.apache.hadoop.io.file.tfile` exposes TFile compression/comparator constants and binary search/string/vint utilities.
- `org.apache.hadoop.io.serializer` and `.avro` expose Java, Writable, and Avro serialization adapters.
- The tail documents legacy log4j event counting and the deprecated original metrics API, including Ganglia emission and the SPI base context.

## Important APIs, Types, and Functions

### Writable Core

- `Writable` is the root serialization contract with `write(DataOutput)` and `readFields(DataInput)`. The docs explicitly tell implementers to reuse storage during deserialization where possible.
- `WritableComparable` extends `Writable` and `Comparable`, with a warning that `hashCode()` must be stable across JVM instances because Hadoop uses hashes for key partitioning.
- Primitive wrappers in this chunk include the end of `FloatWritable`, plus complete `IntWritable`, `LongWritable`, `ShortWritable`, `VIntWritable`, and `VLongWritable` entries. They expose default/value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `NullWritable` is a singleton zero-byte writable with `get()`, no-op `readFields`/`write`, and stable comparison/equality behavior for empty keys or values.
- `VersionedWritable` and `VersionMismatchException` support version-checked writable payloads; the chunk records them as part of the API list even though the most relevant details sit in the omitted middle of the `Text`/writable run.
- `GenericWritable` wraps one of a fixed set of `Writable` classes returned by subclass `getTypes()`. It is also `Configurable`, so configuration is propagated to wrapped configurable instances before deserialization.
- `ObjectWritable` serializes polymorphic objects by writing class identity and can handle `Writable`, `String`, primitives, and arrays. Its overload with `allowCompactArrays` distinguishes RPC/internal use from persisted/inter-cluster output where older cluster interoperability matters.
- `WritableFactories` and `WritableFactory` let non-public writable classes register construction hooks so `ObjectWritable` and related reflection paths can instantiate them.

### Collections and Comparators

- `MapWritable` extends `AbstractMapWritable` and implements `Map`, exposing normal map operations plus `readFields`/`write`. It tracks writable key/value classes for serialization.
- `SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap`, adding `comparator`, `firstKey`, `lastKey`, `subMap`, `headMap`, and `tailMap` over `WritableComparable` keys.
- `RawComparator<T>` compares serialized byte slices directly and also extends `Comparator`.
- `WritableComparator` implements `RawComparator` and `Configurable`. It provides global comparator registration via `define`, comparator lookup via `get(Class, Configuration)`, object comparison, optimized byte-slice comparison, byte parsing helpers (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`), and byte hashing/comparison. Registered comparators must be thread-safe.

### Text and Binary Utilities

- `Text` stores UTF-8 bytes and extends `BinaryComparable`. It exposes raw buffer access (`getBytes`, `getLength`), exact copy (`copyBytes`), byte-position search (`find`), Unicode scalar access (`charAt`), setters from strings, byte arrays, ranges, and other `Text`, append/clear operations, bounded `readFields(DataInput, maxLength)`, static `skip`, known-length reads, and string/UTF-8 byte conversion helpers.
- `Text.clear()` keeps the backing byte array for performance, which is a memory-retention and data-lifetime behavior callers must understand.
- `MD5Hash` is a writable comparable fixed-length MD5 wrapper with constructors from hex strings and byte arrays, stream/byte/string/UTF8 digest helpers, thread-local digester creation, `halfDigest`, `quarterDigest`, and hex `setDigest`.
- `MultipleIOException` bundles several `IOException` instances and has a static factory that returns a convenient `IOException`.
- `WritableUtils` provides compressed byte/string arrays, normal string arrays, clone/cloneInto, zero-compressed `writeVInt`/`writeVLong` and `readVInt`/`readVLong`, range-checked VInt reads, VInt sign/size decoding, enum read/write, `skipFully`, `toByteArray`, and `readStringSafely(maxLength)`.

### File Formats

- `SequenceFile` exposes default compression config and many `createWriter` overloads for `FileSystem`, `FileContext`, `FSDataOutputStream`, path creation options, replication, block size, metadata, progress, and compression codec/type. Many legacy overloads are deprecated in favor of `createWriter(Configuration, Writer.Option...)`.
- `SequenceFile.SYNC_INTERVAL` is the public sync marker interval. The Javadoc describes the shared header (`SEQ` magic/version, key class, value class, compression flags, codec, metadata, sync marker) and the three formats: uncompressed, record-compressed values, and block-compressed key/value length and data blocks. Block format uses zero-compressed integer lengths.
- `MapFile` is a sorted file-backed map directory with `data` and `index` files, constants `DATA_FILE_NAME` and `INDEX_FILE_NAME`, static `rename`, `delete`, and `fix` to rebuild corrupt indexes. The index is loaded fully into memory.
- `SetFile` extends `MapFile` as a file-backed key set.

### Compression

- `CompressionCodecFactory` maps file names, codec names, class names, and configured codec class lists to `CompressionCodec` instances/classes, and exposes `removeSuffix` and a diagnostic `main`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases. Input streams implement `Seekable`, expose `resetState()` for repositioned underlying streams, but default `seek` and `seekToNewSource` are unsupported. Output streams distinguish `finish()` from `close()` so compressed data can be finalized without closing the wrapped stream.
- `Compressor` and `Decompressor` model `Deflater`/`Inflater` style state machines: `setInput`, `needsInput`, dictionary handling, byte counters, `finish`/`finished`, produce/consume methods, `reset`, and `end`. `Decompressor` explicitly supports concatenated streams via `finished()` plus `getRemaining()`.
- `CompressorStream` and `DecompressorStream` provide concrete stream wrappers with protected compressor/decompressor, buffers, closed/eof state, and lifecycle methods.
- `BlockCompressorStream` and `BlockDecompressorStream` wrap block-oriented compression with explicit block headers and compression overhead sizing.
- `CodecPool` manages reusable compressor/decompressor instances and leased counts; this creates a shared resource lifecycle around codec use.
- `DefaultCodec` implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`; `GzipCodec` extends it with gzip-specific stream and direct decompressor creation; `BZip2Codec` exposes codec streams and codec extension behavior.
- `DirectDecompressionCodec` and `DirectDecompressor` add direct `ByteBuffer` decompression for native or zero-copy paths.
- `SplitCompressionInputStream` records adjusted split start/end; `SplittableCompressionCodec` creates split-aware streams for input split boundaries.

### TFile and Serializers

- `TFile` exposes supported compression algorithms and comparator construction with constants for `gz`, `lzo`, `none`, memory comparison, and Java class comparators.
- TFile `Utils` mirrors VInt/VLong/string helpers and lower/upper bound binary search functions for indexed blocks.
- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` represent TFile metadata block errors.
- `JavaSerialization`, `JavaSerializationComparator`, and `WritableSerialization` integrate Java object serialization and Hadoop `Writable` serialization with the `Serialization` extension point.
- Avro serializers include marker `AvroReflectSerializable`, `AvroReflectSerialization` with `AVRO_REFLECT_PACKAGES`, abstract `AvroSerialization` with `AVRO_SCHEMA_KEY`, and `AvroSpecificSerialization`. Reflect serialization accepts classes in configured packages or implementing the marker interface.

### Logging and Metrics

- `EventCounter` is a log4j `AppenderSkeleton` that counts fatal, error, and warn events for metrics exposure.
- `org.apache.hadoop.metrics` package docs define the legacy metrics model: context, record, metric names, tags, buffered updates, timer-based updater callbacks, and `ContextFactory` attributes loaded from `hadoop-metrics.properties`.
- `GangliaContext` extends deprecated `AbstractMetricsContext` and sends legacy metrics via UDP/Ganglia XDR formatting. It exposes protected XDR helpers, buffer/offset, `metricsServers`, and `datagramSocket`, and is deprecated in favor of `metrics2` Ganglia sinks.
- `AbstractMetricsContext` begins here as a deprecated SPI base implementing `MetricsContext`, with `init`, factory attribute lookup/table extraction, context/factory accessors, synchronized `startMonitoring`, `stopMonitoring`, `close`, and `isMonitoring`. The source range stops while documenting `close`, so later methods/fields are outside this chunk.

## Control Flow and State Behavior

This XML does not include implementation bodies, but the API contracts imply several important flows:

- Writable deserialization is pull-based: caller constructs or obtains an instance, then `readFields` mutates it from `DataInput`; serialization pushes object state to `DataOutput`.
- `ObjectWritable` and `GenericWritable` add type dispatch. `ObjectWritable` writes class identity into the stream, while `GenericWritable` writes a compact type code selected from `getTypes()`. Configuration is part of the deserialization setup for configurable wrapped values.
- `SequenceFile.createWriter` chooses a writer implementation from compression type and codec. Records then flow through uncompressed, record-compressed, or block-compressed layouts, with sync markers enabling reader resynchronization.
- `MapFile.fix` reads an existing `data` file and regenerates `index` entries unless `dryrun` is true. Normal `MapFile` use assumes sorted insertion and in-memory index loading.
- Compressor/decompressor streams are state machines: write/read methods feed buffers, `finish` drains final compressed data, `resetState` prepares reuse after stream repositioning or new blocks, and `end` releases native or codec-specific resources.
- Legacy metrics are buffered: `MetricsRecord.update()` stores data in an internal table, and context monitoring periodically emits records. `startMonitoring`/`stopMonitoring`/`close` control a background timer/emitter lifecycle.

## Persistence and Compatibility

- Writable encodings, VInt/VLong formats, `Text` length-prefixed UTF-8, `ObjectWritable` class names, `SequenceFile` headers, MapFile `data`/`index` directory layout, TFile constants, and codec suffix mappings are all persistent or wire-visible compatibility contracts.
- The `ObjectWritable.writeObject(..., allowCompactArrays)` documentation explicitly warns that compact arrays are appropriate for RPC/internal same-version usage but not persisted files or inter-cluster exchange.
- `SequenceFile` documents multiple historical file variants and deprecated writer overloads, so tests and migrations must preserve old overload behavior or intentionally route them to the option-based writer.
- Compression stream behavior is part of persistence: `finish()` must finalize compressed bytes without closing the underlying stream, and decompressor `getRemaining()` determines concatenated stream handling.
- `Text.clear()` does not wipe or free the backing byte array, which affects memory persistence and potential exposure of stale bytes through `getBytes()`.
- Legacy metrics and Ganglia APIs are deprecated but still public in this Hadoop version; removal or behavior changes would break older deployments using `hadoop-metrics.properties`, log4j appenders, or Ganglia factory attributes.

## Dependencies and Integration Points

- Core Java I/O: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `Closeable`, `File`, `FileChannel`, `WritableByteChannel`, `ByteBuffer`, sockets, and Java collections.
- Hadoop configuration and filesystem: `Configuration`, `Configurable`, `FileSystem`, `FileContext`, `Path`, `FSDataOutputStream`, `Options.CreateOpts`, and `Progressable`.
- Hadoop serialization extension points: `Serialization`, serializer/deserializer comparators, `WritableFactory`, reflection utilities, and Avro specific/reflect integrations.
- Compression integrations: Hadoop `CompressionCodec`, native/default codecs, direct decompression, split-aware input processing, and codec discovery from configuration and filename suffixes.
- Logging/metrics dependencies: Apache Commons Logging for cleanup logging, log4j for `EventCounter`, and the legacy Hadoop metrics `ContextFactory`/`MetricsContext` API plus Ganglia UDP/XDR emission.

## Risks and Edge Cases

- Binary compatibility risk is high: small changes in VInt/VLong, `Text`, `ObjectWritable`, `SequenceFile`, MapFile, or codec stream formats can make old data unreadable.
- API compatibility risk is high because this is a JDiff public API file; deprecated overloads still matter to downstream code.
- `ObjectWritable` class-name based deserialization and factory-based instantiation can fail when classes move, are not on the target classpath, or are non-public without a registered factory.
- Raw comparators must be thread-safe when globally registered and must match object-level `compareTo` semantics or sorting/partitioning can corrupt MapReduce behavior.
- `WritableComparable.hashCode()` instability across JVMs can mispartition data.
- `MapFile` loads indexes entirely into memory, so oversized keys or too dense indexes can cause memory pressure; corrupt index repair depends on correct key/value classes.
- `Text.getBytes()` returns the backing array, not an exact-length or immutable copy; callers must respect `getLength()` and avoid retaining stale data from `clear()`.
- Codec lifecycle bugs, especially missing `finish`, failing to return compressors/decompressors to `CodecPool`, or mutating decompressor input before `needsInput()`, can cause data corruption, native memory leaks, or corrupted concatenated stream handling.
- `CompressionInputStream.seek` is unsupported by default despite implementing `Seekable`; callers must only rely on seek behavior for codecs that explicitly support it.
- Legacy metrics/Ganglia APIs are deprecated; new code should prefer metrics2, but compatibility code still has to honor old configuration attributes and UDP packet encoding.

## Test Signals

Useful tests or validation signals for code governed by this API snapshot include:

- Round-trip serialization tests for every primitive writable, `NullWritable`, `Text`, `MapWritable`, `SortedMapWritable`, `GenericWritable`, `ObjectWritable`, `MD5Hash`, VInt/VLong boundaries, enum/string arrays, and `readStringSafely` maximum length failures.
- Golden-file compatibility tests for `SequenceFile` uncompressed, record-compressed, and block-compressed formats, including sync marker recovery, metadata, deprecated `createWriter` overloads, and codec selection.
- MapFile tests for sorted writes, index loading, `rename`, `delete`, and `fix`/`dryrun` behavior on missing or corrupt indexes.
- Comparator tests comparing raw byte comparator results against object `compareTo`, plus concurrency tests for registered `WritableComparator` instances.
- UTF-8 tests for `Text.charAt`, byte-position `find`, invalid/trailing bytes, `clear` memory behavior, bounded reads, and known-length reads.
- Compression tests for block and stream codecs, direct decompression, split compression boundaries, concatenated compressed streams, `finish` without closing underlying streams, `resetState`, `end`, and `CodecPool` lease accounting.
- Serializer tests for Java, Writable, Avro specific, and Avro reflect package/marker acceptance.
- Legacy metrics tests for `EventCounter` counts, `ContextFactory` property loading, buffered update emission, synchronized start/stop/close semantics, and Ganglia XDR field formatting/config attributes.

### subset-b-007183: lines 24298-30745

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml lines 24298-30745

## Scope And Purpose

This chunk is part of the Hadoop Common 2.8.3 JDiff API snapshot. It is documentation metadata rather than executable Java source, but it captures public and protected API contracts, inheritance, deprecation state, parameters, thrown exceptions, and package documentation for several Hadoop Common subsystems.

The range begins in the middle of `org.apache.hadoop.metrics.spi.AbstractMetricsContext`, continues through the legacy metrics SPI, the `metrics2` public API, metrics2 mutable metric helpers and sinks, network topology/socket helpers in `org.apache.hadoop.net`, deprecated Hadoop Record I/O runtime classes, and deprecated Hadoop Record compiler APIs. It ends inside the `org.apache.hadoop.record.compiler.ant.RccTask` class documentation, so the final per-file report must reconcile this chunk with adjacent chunks before treating package or class documentation as complete.

The dominant purpose of the covered API surface is compatibility. The legacy `org.apache.hadoop.metrics.*` SPI and `org.apache.hadoop.record.*` APIs are explicitly deprecated in favor of `metrics2` and Avro respectively, while `metrics2` and `org.apache.hadoop.net` remain active integration surfaces used by Hadoop daemons, metrics sinks, JMX exposure, topology mapping, socket construction, and generated record serialization.

## Important APIs, Types, And Functions

Legacy metrics SPI appears first. `AbstractMetricsContext` exposes synchronized lifecycle and table operations such as `createRecord(String)`, `registerUpdater(Updater)`, `unregisterUpdater(Updater)`, and `getAllRecords()`, plus protected emission hooks `emitRecord(String, String, OutputRecord)`, `flush()`, `update(MetricsRecordImpl)`, `remove(MetricsRecordImpl)`, `getPeriod()`, `setPeriod(int)`, and `parseAndSetPeriod(String)`. Subclasses provide concrete transport by implementing `emitRecord`, while the base class owns the internal metric table and timer cadence. `CompositeContext`, `NoEmitMetricsContext`, `NullContext`, and `NullContextWithUpdateThread` are deprecated context variants for fan-out, non-emitting storage, no-op operation, and update-thread-only behavior.

`MetricsRecordImpl` implements the old `org.apache.hadoop.metrics.MetricsRecord` contract. It carries a record name and back-pointer to its `AbstractMetricsContext`, supports tag mutation through overloaded `setTag` methods for `String`, `int`, `long`, `short`, and `byte`, supports `removeTag`, supports absolute metric assignment with `setMetric` overloads for integer and floating numeric types, supports incremental changes with `incrMetric`, and delegates persistence into the context via `update()` and `remove()`. `MetricValue` wraps a `Number` with `ABSOLUTE` or `INCREMENT` semantics. `OutputRecord` exposes immutable-ish read access to emitted tag and metric maps through `getTagNames`, `getTag`, `getMetricNames`, `getMetric`, `getTagsCopy`, and `getMetricsCopy`. `Util.parse(String)` parses comma-separated server specifications into a `List`.

The `org.apache.hadoop.metrics2` package defines the modern metrics contracts. `AbstractMetric` is an immutable metric implementing `MetricsInfo`, with `name`, `description`, `info`, `value`, `type`, `visit`, equality, hash, and string methods. `MetricsCollector` creates `MetricsRecordBuilder` instances by name or `MetricsInfo`. `MetricsRecordBuilder` is the fluent sink-facing builder for tags, immutable metric objects, context tags, counters, gauges, and `endRecord()`. `MetricsRecord` exposes timestamp, name, description, context, tags, and metric iterable snapshots. `MetricsFilter` accepts or rejects names, tags, tag iterables, and records. `MetricsPlugin`, `MetricsSink`, `MetricsSource`, `MetricsInfo`, `MetricsVisitor`, `MetricsSystem`, `MetricsSystemMXBean`, `MetricsTag`, `MetricStringBuilder`, and `MetricsException` define initialization, source registration, sink publication, visitor dispatch, and diagnostics contracts.

The metrics2 annotation/filter/lib APIs cover source instrumentation and mutable in-process state. `@Metric` and `@Metrics` annotate metrics fields and groups. `GlobFilter` and `RegexFilter` compile pattern syntax for metrics filtering. `DefaultMetricsSystem` provides singleton `initialize`, `instance`, and `shutdown`. `Interns` interns `MetricsInfo` and `MetricsTag` objects. `MetricsRegistry` creates and stores `MutableCounterInt`, `MutableCounterLong`, `MutableGaugeInt`, `MutableGaugeLong`, `MutableQuantiles`, `MutableStat`, `MutableRate`, and `MutableRatesWithAggregation`, adds samples, sets context, tags records, and snapshots into a `MetricsRecordBuilder`. `MutableMetric` tracks a changed flag and controls full versus changed-only snapshots. `MutableStat` keeps sample counts, sums, rates, optional extended stats, last `SampleStat`, and min/max reset hooks. `MutableQuantiles` maintains rolling online quantile estimates with `quantiles` and `previousSnapshot` fields.

The metrics2 sink and utility classes integrate metrics with external systems. `FileSink`, `GraphiteSink`, and `StatsDSink` implement `MetricsSink` and `Closeable`, with `init`, `putMetrics`, `flush`, and `close`; `StatsDSink` also exposes `writeMetric`. `MBeans` registers and unregisters Hadoop-format JMX object names and extracts service/name components. `MetricsCache` stores latest records for sinks that do not support sparse updates. `Servers.parse(String, int)` parses comma- or space-separated host specs into socket addresses.

The network package APIs describe topology mapping and socket factories. `AbstractDNSToSwitchMapping` implements `DNSToSwitchMapping` and `Configurable`, tracks configuration, reports whether a mapping is single-switch, exposes diagnostic switch maps, and dumps topology. `CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping`, caches host-to-switch answers, reloads all or selected cached entries, and delegates single-switch status. `DNSToSwitchMapping` is the pluggable interface for resolving hostnames/IPs to rack paths. `ScriptBasedMapping` uses configured external scripts and exposes `NO_SCRIPT`. `TableMapping` uses a mapping file and reloads cached mappings. `ConnectTimeoutException` specializes `SocketTimeoutException` for `NetUtils.connect`. `SocksSocketFactory` and `StandardSocketFactory` implement standard `SocketFactory` overloads; the SOCKS variant is configurable and proxy-aware.

The deprecated `org.apache.hadoop.record` package captures Hadoop Record I/O runtime contracts. `BinaryRecordInput`/`BinaryRecordOutput`, `CsvRecordInput`/`CsvRecordOutput`, and `XmlRecordInput`/`XmlRecordOutput` implement `RecordInput`/`RecordOutput` for primitive values, strings, `Buffer`, records, vectors, and maps. Binary input/output expose thread-local `get(DataInput)` and `get(DataOutput)` helpers. `Buffer` is a comparable, cloneable byte sequence with aliasing `set`, copying `copy`, capacity management, reset/truncate, append, encoding-aware string conversion, equality, hash, and lexicographic comparison. `Index` provides `done()` and `incr()` for collection deserialization. `Record` is the generated-class base that implements `WritableComparable` and `Cloneable`, with tagged and untagged `serialize`/`deserialize`, Hadoop `write`/`readFields`, `compareTo`, and CSV-ish `toString`. `RecordComparator` extends `WritableComparator` and registers optimized raw comparators. `Utils` provides variable-length integer/long encoding and decoding, float/double byte parsing, byte comparison, and hex helpers.

The deprecated record compiler packages represent code-generation metadata for Hadoop Record DDL. `CodeBuffer` wraps an indenting string buffer. `Consts` defines compiler constants such as `RIO_PREFIX`, runtime type info variable/filter names, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`. `JType` is the abstract base for compiler types; `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, and `JRecord` model primitive and composite record types. `JField` wraps record fields, and `JFile` represents a DDL file with include files and records and can `genCode(language, destDir, options)`. `RccTask` is an Ant task for invoking the record compiler, exposing setters for language, source file, fail-on-error behavior, destination directory, filesets, and `execute()`.

## Control Flow And Runtime Behavior

For the legacy metrics SPI, runtime flow is context-centered. A caller creates a metrics record through `AbstractMetricsContext.createRecord`, mutates tags and metric values on `MetricsRecordImpl`, then calls `update()` to merge the record into the context's buffered table or `remove()` to delete matching rows. Registered `Updater` callbacks run on the configured timer period and populate records before the context emits buffered `OutputRecord` data through subclass-specific `emitRecord`; `flush()` runs after periodic emission. `NoEmitMetricsContext` intentionally skips emission but preserves data for `getAllRecords`, while `NullContext` variants drop or limit publication behavior.

For metrics2, runtime flow is source-to-collector-to-sink. A `MetricsSystem` registers `MetricsSource` objects, asks each source for metrics through `getMetrics(MetricsCollector, boolean)`, and sources add records through `MetricsRecordBuilder`. Mutable metrics in a `MetricsRegistry` snapshot their current values into a builder, optionally only when their changed flag is set. Sinks receive immutable `MetricsRecord` snapshots through `putMetrics`, then may buffer and `flush` or release resources with `close`. Filters can be applied at name, tag, or record boundaries before metrics reach sinks.

Metrics2 mutable state flows through explicit mutation methods. Counters increment monotonically; gauges increment, decrement, or set absolute values; stats aggregate sample counts and sums; rates specialize stats for throughput; quantiles collect stream samples and publish periodic snapshots. `MutableMetric.snapshot(builder, all)` is the handoff point where in-memory mutable values become immutable emitted metrics, and `setChanged`/`clearChanged` govern whether incremental snapshots include a metric.

Network topology flow starts with a `DNSToSwitchMapping.resolve(List<String>)` call. `CachedDNSToSwitchMapping` consults its local cache first and delegates misses to its raw mapping, while reload methods invalidate all or selected cache entries. `ScriptBasedMapping` and `TableMapping` are concrete strategies for deriving rack locations from external scripts or mapping files. Socket factory flow is the standard Java `SocketFactory` set of `createSocket` overloads, with `SocksSocketFactory` adding proxy configuration through Hadoop `Configuration`.

Record I/O flow is serializer/deserializer driven. Generated `Record` subclasses implement tagged field serialization and deserialization against a selected `RecordOutput` or `RecordInput` implementation. Binary, CSV, and XML variants share the same logical method sequence: start record, read/write primitive or composite members, iterate vectors/maps using `Index`, and end record. Hadoop `Writable` integration routes `write(DataOutput)` and `readFields(DataInput)` through binary record I/O, while raw comparators can compare serialized records without fully materializing objects.

Record compiler flow starts from a parsed DDL file represented as a `JFile`; compiler type objects model fields and records, then `genCode` emits Java or C++ artifacts into a destination directory. `RccTask.execute()` wraps that compiler flow for Ant builds and decides whether source-file or fileset failures become build failures based on `failonerror`.

## State And Persistence Behavior

The JDiff XML itself is a static API artifact and has no runtime state. The APIs it describes do have notable state boundaries.

Legacy metrics state lives in the `AbstractMetricsContext` internal table of records, the configured timer period, registered updater callbacks, and concrete context resources used by emitters. `MetricsRecordImpl` holds mutable tag and metric maps until `update()` or `remove()` delegates to the context. `OutputRecord` represents a snapshot view or copy of those maps for emission. Because several context methods are synchronized, the API contract implies shared state accessed by update threads and application threads.

Metrics2 state lives in a process-local metrics system singleton, registered sources/sinks, mutable metric objects, registry tags, current metrics configuration, MBean registrations, sink buffers or network/file handles, and caches for sparse updates. `MetricsCache` persists the latest value per record identity in memory so sinks that need complete records can receive reconstructed snapshots. `MutableQuantiles` stores rolling quantile objects and previous snapshots, which means interval boundaries and sampling windows affect emitted values.

Network state includes cached hostname-to-rack mappings, raw mapping configuration, external script names, table mapping files, and proxy configuration. Reload APIs are important because topology files or scripts can change outside the JVM; stale caches can otherwise keep obsolete rack placement decisions.

Record I/O state includes stream positions, thread-local binary input/output wrappers, `Buffer` backing arrays and logical counts, generated record fields, and comparator registrations. `Buffer.set(byte[])` uses the provided byte array as backing storage, while `copy(byte[], int, int)` replaces state with an owned copy; this aliasing distinction matters for persistence and mutation safety. Serialization writes persistent binary/CSV/XML representations to caller-provided streams, and deserialization reconstructs generated record objects from those representations.

Record compiler state includes parsed DDL files, include-file lists, field/type objects, output language selection, destination directories, Ant filesets, and build failure policy. Generated files are persistent build outputs, but the compiler classes themselves are deprecated compatibility infrastructure.

## Dependencies And Integration Points

The metrics APIs integrate with `org.apache.hadoop.conf.SubsetConfiguration`, `java.io.IOException`, Java collections, JMX, Hadoop daemon lifecycle code, and external monitoring systems. Legacy metrics SPI depends on `org.apache.hadoop.metrics.MetricsRecord`, `Updater`, and `MetricsException`; its deprecation points callers toward `org.apache.hadoop.metrics2`. Metrics2 depends on `MetricsInfo`, `MetricsCollector`, `MetricsRecordBuilder`, `MetricsVisitor`, `MetricsSource`, `MetricsSink`, `MetricsPlugin`, and concrete mutable metric/util classes. Sink packages integrate with file output, Graphite, StatsD, and Ganglia-related packages adjacent to this chunk.

`MBeans` integrates with `javax.management.ObjectName` and the platform MBean server. `DefaultMetricsSystem` and `MetricsSystemMXBean` expose process-wide metrics control and diagnostics. `MetricsRegistry` is the central integration point for instrumented Hadoop services, because services create named counters, gauges, stats, quantiles, and tags there before source snapshots publish them.

The network APIs integrate with `org.apache.hadoop.conf.Configuration`, `Configurable`, rack-awareness consumers in HDFS/YARN/MapReduce, external topology scripts, table mapping files, Java `SocketFactory`, `Proxy`, `Socket`, and `NetUtils.connect`. `ConnectTimeoutException` is a caller-visible exception path for socket connection timeout handling.

Record I/O integrates with Hadoop `WritableComparable`, `WritableComparator`, Java `DataInput`/`DataOutput`, `InputStream`/`OutputStream`, collection iteration contracts through `Index`, XML/CSV/binary encodings, and generated classes from the deprecated record compiler. The compiler integrates with Ant (`org.apache.tools.ant.Task`, `FileSet`, and `BuildException`) and with generated Java/C++ source trees.

Deprecation is itself an integration signal. Legacy metrics SPI should not be expanded for new functionality; use metrics2. Hadoop Record I/O and its compiler are replaced by Avro, so new persistent data formats should avoid depending on these APIs unless preserving legacy compatibility.

## Risks And Edge Cases

This chunk starts and ends mid-context. It omits the beginning of `AbstractMetricsContext` and the end of `RccTask`, so method lists and package documentation here should be merged with adjacent chunks before making final source-file conclusions.

The XML encodes API, not implementation bodies. Runtime behavior above is inferred from method contracts, inheritance, names, and Javadocs. Any implementation-specific concurrency, exception, or resource handling details must be checked against the corresponding Java source before changing code.

Legacy metrics contexts combine timers, synchronized methods, updater callbacks, buffered maps, and external emission. Risks include updater callbacks mutating records concurrently with emission, stale records in polling contexts, mismatched configured record names, and silent no-op behavior when a `NullContext` is accidentally configured.

Metrics2 changed-only snapshots are easy to mishandle. Forgetting `setChanged` after mutation can suppress metrics; forgetting `clearChanged` can re-emit sparse values unexpectedly. Mutable counters and gauges have different semantics, so using a gauge for a monotonic count or a counter for a value that can decrease will produce misleading monitoring data.

Metrics sinks cross process and network boundaries. File, Graphite, and StatsD sinks must handle configuration errors, buffering, flush timing, close idempotence, invalid metric names, tag formatting, network failures, and sparse update reconstruction. MBean registration must avoid duplicate object names and must unregister during shutdown to prevent leaks in long-lived JVMs or tests.

Topology mapping affects block placement and scheduling. Script or table mapping failures can collapse the cluster into a default rack, stale caches can keep outdated topology after config changes, and inconsistent `isSingleSwitch` answers can hide topology diversity from callers. `SocksSocketFactory.equals`/`hashCode` behavior matters because socket factories may be cached or compared by configuration.

Record I/O is deprecated but still persistence-sensitive. Changing binary variable-length integer encoding, string escaping, buffer ordering, or raw comparator behavior can break on-disk or wire compatibility with old generated records. `Buffer.get()` exposes the backing byte array, and `set()` aliases caller-provided arrays, so callers can accidentally mutate state after storing or serializing a buffer. CSV and XML encodings must preserve special characters, binary buffers, and collection boundaries consistently with generated code.

Record compiler APIs are build-tooling compatibility surfaces. Language names, destination directory handling, include files, fileset iteration, and fail-on-error policy affect generated source trees and build reproducibility. Because the entire record compiler package is deprecated in favor of Avro, fixes should be narrow and compatibility-preserving.

## Test Signals

For legacy metrics SPI, useful tests create records with multiple tag and metric types, call `update()` and `remove()`, verify `getAllRecords()` contents, register and unregister updaters, exercise configured timer periods, and use concrete no-op/non-emitting contexts to confirm emission versus storage behavior.

For metrics2, tests should register sources with `DefaultMetricsSystem`, snapshot a `MetricsRegistry` containing counters, gauges, stats, rates, and quantiles, verify changed-only versus full snapshots, check tag/context propagation, and validate `MetricsFilter` acceptance at name, tag, iterable, and record levels. Sink tests should cover file output, Graphite/StatsD line formatting, flush/close behavior, and `MetricsCache` reconstruction of sparse records.

For JMX integration, tests should register and unregister MBeans with expected Hadoop object-name service/name parts and check duplicate registration or cleanup paths. For server parsing, tests should cover comma-separated, space-separated, mixed, default-port, explicit-port, malformed, and empty specifications.

For topology mapping, tests should cover cache hit/miss behavior, reload-all and reload-selected behavior, script absence (`NO_SCRIPT`), table mapping reloads, single-switch detection, diagnostic topology dumps, and failure fallback. Socket factory tests should cover every `createSocket` overload, proxy configuration, equality, hash behavior, and connect timeout exception propagation through `NetUtils`.

For Record I/O, round-trip tests should serialize and deserialize generated records through binary, CSV, and XML implementations, including primitive min/max values, floats/doubles, Unicode strings, escaped XML/CSV characters, empty and non-empty buffers, vectors, maps, and nested records. Binary compatibility tests should lock down variable-length integer encodings, `Utils.compareBytes`, `Buffer.compareTo`, `RecordComparator.compare`, and `Writable` `write`/`readFields` interoperability.

For the deprecated compiler and Ant task, tests should compile simple DDL files to Java and C++ into a temporary destination, include another DDL file, process an Ant fileset, validate `failonerror` true and false paths, and assert generated sources remain stable for representative primitive, buffer, vector, map, and record fields.

### subset-b-007184: lines 30746-36809

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml lines 30746-36809

## Scope

This chunk is a generated JDiff API snapshot for Apache Hadoop Common 2.8.3. It starts inside the tail of `org.apache.hadoop.record.compiler.ant.RccTask`, covers the deprecated Record I/O compiler/parser and metadata APIs, then spans Hadoop security, credential, authorization, HTTP security filters, tokens, delegation-token web clients, service lifecycle, tracing administration, and the beginning of `org.apache.hadoop.util`. It ends mid-class inside `org.apache.hadoop.util.Shell` at `getSymlinkCommand`, so a later chunk is required for the rest of `Shell`.

The source is XML API metadata rather than implementation code. The compatibility surface in this range is package membership, class/interface names, inheritance, implemented interfaces, public/protected constructors and methods, checked exceptions, fields, static/final/synchronized/abstract/deprecated flags, and embedded Javadocs.

## Purpose

The Record I/O portion documents Hadoop's old record compiler machinery: JavaCC-generated parser/token classes under `org.apache.hadoop.record.compiler.generated` and runtime record type metadata under `org.apache.hadoop.record.meta`. All of these visible Record APIs are deprecated in favor of Avro, but remain part of the public API contract for Hadoop 2.8.3.

The security portion documents core authentication and authorization APIs. `Credentials` carries tokens and secret keys across jobs and processes. `SecurityUtil` and `UserGroupInformation` expose Kerberos login, ticket/keytab relogin, proxy-user, token, and `doAs` execution flows. Mapping-provider interfaces abstract user/group and numeric ID lookups. Authorization classes represent ACLs, impersonation policy, and stack-trace-suppressed authorization failures.

The alias and HTTP security packages expose pluggable credential stores and servlet filters for REST CSRF protection and X-Frame-Options clickjacking protection.

The token packages define the shared token model: secret managers create and verify token passwords, tokens serialize identifier/password/kind/service data, token identifiers provide user identity, token renewers handle lifecycle operations, and token selectors choose a matching token for a service. The delegation-token web package adapts authenticated HTTP connections to delegation-token acquisition, renewal, cancellation, and token transport.

The service package defines Hadoop's lifecycle model for components with `NOTINITED`, initialized, started, stopped, failure, listener, blocker, and composite-service behavior. The tracing package exposes a small RPC protocol for listing, adding, and removing span receivers. The util portion begins with application class loading, IP-list membership, progress callbacks, pure-Java CRC implementations, reflection helpers, and early shell command helpers.

## Important APIs, Types, and Functions

### Deprecated Record Compiler and Metadata

- The chunk begins with the end of `RccTask` usage docs. The Ant task requires a `file` attribute or nested fileset, supports `language`, `destdir`, and `failonerror`, and is deprecated in favor of Avro.
- `ParseException` is the JavaCC parse error type. It carries `currentToken`, `expectedTokenSequences`, `tokenImage`, `specialConstructor`, and `eol`, with `getMessage()` producing parser-specific diagnostics and `add_escapes(String)` escaping raw characters.
- `Rcc` implements `RccConstants` and is the generated record compiler parser. Its constructors accept `InputStream`, `InputStream` plus encoding, `Reader`, or `RccTokenManager`. Public parser productions include `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, returning compiler model objects such as `JFile`, `JRecord`, `JField`, `JType`, `JMap`, and `JVector`. It also exposes `main`, `usage`, `driver`, `ReInit` overloads, token accessors, parse-exception generation, and tracing toggles.
- `RccConstants` defines lexical token IDs for module/record/include, primitive and container types, punctuation, strings, identifiers, lexical states, and `tokenImage`.
- `RccTokenManager`, `SimpleCharStream`, `Token`, and `TokenMgrError` are JavaCC-generated lexical infrastructure. They manage lexical states, buffers, line/column accounting, token images, linked token chains, special tokens, and lexical error messages.
- `FieldTypeInfo`, `MapTypeID`, `RecordTypeInfo`, `StructTypeID`, `TypeID`, `VectorTypeID`, and `Utils` describe deprecated Record I/O schemas. They expose base type constants, field names, nested record lookup, map/vector element typing, record type serialization/deserialization, equality/hash behavior, comparison, and `Utils.skip` for skipping serialized values by type.

### Core Security

- `AccessControlException` extends the filesystem permission exception type and provides default, message, and cause constructors for access-control failures.
- `Credentials` implements `Writable` and stores in-memory token and secret-key maps keyed by Hadoop `Text`. It provides `getToken`, `addToken`, token enumeration/counts, `getSecretKey`, `addSecretKey`, `removeSecretKey`, secret-key enumeration/counts, token-storage file/stream readers, token-storage file/stream writers, `write`, `readFields`, `addAll`, and `mergeAll`.
- `GroupMappingServiceProvider` defines `getGroups(String)`, `cacheGroupsRefresh()`, and `cacheGroupsAdd(List)` plus `GROUP_MAPPING_CONFIG_PREFIX`, making user-to-group lookup and cache control pluggable.
- `IdMappingServiceProvider` maps names and numeric IDs through `getUid`, `getGid`, `getUserName`, `getGroupName`, and unknown-tolerant UID/GID variants.
- `SecurityUtil` exposes Kerberos principal and token-service helpers: original-TGT detection, `_HOST` principal expansion, login from keytab and config keys, delegation-token service-name construction, host extraction from principals, Kerberos/token annotation lookup, token-service address and `Text` construction, token service assignment, privileged execution as login/current user, authentication-method getters/setters, and privileged-port checks.
- `UserGroupInformation` is the central user identity and authentication API. It configures security, detects Kerberos credentials, returns current/login/best users, loads users from ticket caches or `Subject`s, logs in from `Subject` or keytab, logs out, relogs from keytab or ticket cache, creates remote/proxy/testing users, exposes real users, short names, primary groups, user names, group lists, token identifiers, tokens, credentials, subjects, authentication methods, equality/hash behavior, `doAs` overloads for `PrivilegedAction` and `PrivilegedExceptionAction`, diagnostics, and a `main`.
- `UserGroupInformation.AuthenticationMethod` is an enum-like nested type with `values`, string `valueOf`, and mapping to `SaslRpcServer.AuthMethod`.

### Credential Providers, ACLs, and Impersonation

- `CredentialProvider` is an abstract pluggable password/credential store. It exposes transient-store detection, `flush`, credential lookup, alias listing, credential creation/deletion, password-needed checks, password warning/error messages, and `CLEAR_TEXT_FALLBACK`.
- `CredentialProviderFactory` is an abstract service-loader factory. `createProvider(URI, Configuration)` is implemented by providers, while static `getProviders(Configuration)` resolves provider paths from `CREDENTIAL_PROVIDER_PATH`.
- `AccessControlList` implements `Writable` and parses ACL strings in `"users groups"` form, with comma-separated user/group lists and `WILDCARD_ACL_VALUE` for all access. It supports user/group add/remove, all-allowed checks, immutable views of users/groups, membership checks against `UserGroupInformation`, exact ACL string rendering, descriptive rendering, and serialization.
- `AuthorizationException` extends `AccessControlException` and intentionally suppresses stack traces for security-sensitive authorization failures by overriding stack-trace access and printing methods.
- `ImpersonationProvider` extends `Configurable` and defines `init(configurationPrefix)` plus `authorize(UserGroupInformation, remoteAddress)`. `DefaultImpersonationProvider` implements it, derives proxy-user user/group/IP configuration keys, exposes configured proxy groups/hosts, and has a synchronized test-provider accessor.

### HTTP Security Filters

- `RestCsrfPreventionFilter` implements `javax.servlet.Filter`. It initializes from servlet config, classifies browser user agents through configurable regexes, handles abstract `HttpInteraction` objects, enforces a configurable custom header except for ignored methods and non-browser callers, and exposes `getFilterParams(Configuration, prefix)`. Public constants include user-agent, browser-regex, custom-header, and ignored-method parameter names.
- `XFrameOptionsFilter` implements `Filter` and adds clickjacking protection by setting a configurable X-Frame-Options header. It has normal servlet `init`, `doFilter`, `destroy`, static `getFilterParams`, `X_FRAME_OPTIONS`, and `CUSTOM_HEADER_PARAM`.

### Tokens and Delegation-Token Web Client

- `SecretManager<T>` creates token passwords from identifiers and secret keys, retrieves or retriably retrieves passwords, creates identifiers, checks read availability, generates `HmacSHA1` secrets, and converts byte arrays into `SecretKey` instances.
- `Token<T>` implements `Writable` and carries identifier bytes, password bytes, kind, and service. It can be built from an identifier plus secret manager, raw bytes, empty state, or another token. It decodes identifiers, exposes byte arrays and `Text` fields, mutates service, creates private clones, tests private-clone lineage, serializes/deserializes, URL-encodes/decodes, compares, hashes, renders, builds cache keys, and delegates `isManaged`, `renew`, and `cancel` to a renewer.
- `Token.TrivialRenewer` is a simple `TokenRenewer` implementation for trivial tokens. It exposes kind handling, management status, renew, and cancel.
- `TokenIdentifier` implements `Writable` and defines token kind, token owner as `UserGroupInformation`, serialized bytes, and tracking IDs.
- `TokenInfo` is an annotation type used to associate token metadata with protocols.
- `TokenRenewer` is the plugin interface for token lifecycle operations: `handleKind`, `isManaged`, `renew`, and `cancel`.
- `TokenSelector<T>` chooses a token from a collection for a named service.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` with delegation-token-aware constructors, default authenticator class setters/getters, query-string-vs-header token transport controls, authenticated `openConnection` overloads, and delegation token get/renew/cancel overloads.
- `DelegationTokenAuthenticatedURL.Token` extends the authentication-client token and adds storage for a Hadoop delegation `Token`.
- `DelegationTokenAuthenticator` wraps an authentication-client `Authenticator` and adds delegation-token operations over HTTP. It defines operation/header/query/json constant names for delegation token endpoints.
- `KerberosDelegationTokenAuthenticator` and `PseudoDelegationTokenAuthenticator` specialize the delegation-token wrapper for Kerberos and pseudo/simple authentication modes.

### Service Lifecycle, Tracing, and Utilities

- `AbstractService` implements `Service` and owns name, config, state model, start time, failure cause/state, lifecycle history, blockers, and listener registration. Its public lifecycle methods call overridable `serviceInit`, `serviceStart`, and `serviceStop`, record failures, support stop waiting, and expose global listener registration.
- `CompositeService` extends `AbstractService` and manages child services with `getServices`, `addService`, `addIfService`, `removeService`, and overridden init/start/stop. `STOP_ONLY_STARTED_SERVICES` controls shutdown policy.
- `LifecycleEvent`, `LoggingStateChangeListener`, `Service`, `ServiceOperations`, `ServiceStateChangeListener`, `ServiceStateException`, and `ServiceStateModel` define lifecycle events, listener callbacks, stop helpers, exception conversion, and valid state-transition enforcement.
- `SpanReceiverInfo`, `SpanReceiverInfoBuilder`, `TraceAdminProtocol`, and `TraceAdminProtocolPB` expose trace span receiver metadata and RPC operations to list, add, and remove span receivers. `TraceAdminProtocol` carries a `versionID`.
- `ApplicationClassLoader` extends `URLClassLoader` for child-first application isolation except for configured system classes/resources. It exposes classpath-string and URL-array constructors, resource/class loading, `isSystemClass`, and `SYSTEM_CLASSES_DEFAULT`.
- `IPList` is a one-method IP membership interface. `Progressable` is a one-method progress callback used by long-running Hadoop operations to avoid framework timeouts.
- `PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum` with pure-Java CRC32 and CRC32C update/reset/value methods.
- `ReflectionUtils` provides configuration injection, configured instantiation, contention tracing, thread dump logging/printing, typed class lookup, `Writable` copy/clone helpers, and inherited field/method discovery.
- The visible beginning of `Shell` includes protected constructors with optional minimum execution interval and stderr redirection, deprecated `isJava7OrAbove`, Windows command-length validation, and static command builders for groups, group IDs, netgroups, permissions, ownership, and symlinks.

## Control Flow

Record compiler flow starts with `RccTask` or `Rcc.driver`, feeds a `.jr` record definition to `SimpleCharStream`, tokenizes through `RccTokenManager`, parses grammar productions in `Rcc`, constructs compiler model objects, and reports parse or lexical errors through `ParseException` and `TokenMgrError`. The generated classes also support `ReInit` so a parser/token manager/stream can be reused with new input.

Record metadata flow is schema-oriented: `RecordTypeInfo` holds ordered field type info, can serialize and deserialize itself through Record I/O archives, can look up nested structs by field name, and uses `TypeID` subclasses to represent primitive, map, vector, and struct types. `Utils.skip` consumes serialized data based on a supplied `TypeID`.

Security identity flow is centered on `UserGroupInformation`. Configuration selects security mode; callers obtain current/login users, create remote or proxy users, attach tokens/credentials, and run privileged code through `doAs`. Kerberos deployments use keytab or ticket-cache login and relogin methods; `SecurityUtil` expands principals, logs in from configured keytab/principal keys, and builds token service names for network addresses.

Credential flow stores tokens and secret keys in `Credentials`, serializes them to streams/files, and merges or adds credential sets for job submission or process handoff. Credential provider flow resolves provider URIs from configuration, creates provider instances through service-loader factories, performs alias-based CRUD, and persists changes only after `flush`.

Authorization flow parses ACLs into user/group sets or wildcard state, evaluates `UserGroupInformation` membership, serializes ACL definitions, and enforces proxy-user impersonation by checking real/effective user relationships plus configured allowed groups and remote hosts. Authorization failures deliberately avoid stack traces.

HTTP filter flow initializes servlet filter parameters from either servlet config or Hadoop configuration-prefix maps. CSRF filtering classifies the request's user agent, checks method exemptions, requires the configured custom header for browser-like requests, and either rejects or forwards. XFrame filtering sets the configured frame-options header before continuing the filter chain.

Token flow begins with `TokenIdentifier` serialization and `SecretManager` password creation. `Token` serializes identifier/password/kind/service, can be encoded into URL strings, and uses the appropriate `TokenRenewer` to answer management, renewal, and cancellation requests. Delegation-token web clients open authenticated HTTP connections and, depending on configuration, send delegation tokens in headers or query strings, then call server endpoints for get/renew/cancel operations.

Service flow is a state machine. `AbstractService.init` moves through initialization and calls `serviceInit`; `start` transitions to started and calls `serviceStart`; `stop` transitions to stopped and calls `serviceStop`; failures are recorded with the state where they occurred. `CompositeService` applies the same transitions across registered child services, while listeners receive already-applied state changes.

Tracing flow is RPC-like: an admin client lists active span receivers, submits `SpanReceiverInfo` built from a class name and configuration pairs to add one, and removes receivers by ID. Utility flow includes child-first class/resource loading with system-class exclusions, repeated progress callbacks during long operations, checksum accumulation over bytes, reflection-based object setup/copying, and platform-specific shell command construction.

## State and Persistence Behavior

This XML file persists API metadata for compatibility analysis. Runtime state is inferred from the documented public APIs and fields, not from method bodies.

The deprecated Record compiler generated classes carry parser state: current token, next token, token source, lexical state, character buffers, line/column arrays, token chains, special tokens, and parse-error expectation arrays. This state is in-memory and resettable with `ReInit`. Record metadata classes have durable behavior because `RecordTypeInfo` serializes/deserializes schema metadata and `Utils.skip` advances archive input according to type metadata.

`Credentials` is both in-memory state and durable `Writable` state. Its token and secret-key maps can be written to `DataOutput`, loaded from `DataInput`, and stored in token-storage files or streams. `addAll` and `mergeAll` differ in replacement semantics, so duplicate aliases are a compatibility-sensitive behavior.

`UserGroupInformation` holds process identity state: login user, current subject, real/proxy user relationships, authentication method, Kerberos ticket/keytab status, group cache results, tokens, token identifiers, and credentials. Much of it is process-local, but ticket caches, keytabs, and Hadoop token files connect it to external persistent security material. `HADOOP_TOKEN_FILE_LOCATION` is the environment/configuration integration point for loading token files.

Credential providers may be transient or persistent. Transient providers are intended for short-lived job access to passwords. Persistent providers must not be assumed durable until `flush` completes. Provider password state can be missing, producing warnings or hard errors depending on caller policy.

`AccessControlList` persists through `Writable` serialization and exact ACL string round trips. `DefaultImpersonationProvider` caches proxy group and host maps derived from configuration. `AuthorizationException` intentionally discards diagnostic stack state to reduce information exposure.

Tokens persist through `Writable` binary serialization and URL string encoding. Their identifier/password byte arrays are security-sensitive mutable data. Private clones carry private service state while retaining lineage to the public token. Secret managers own secret keys and password derivation inputs; the actual secret rotation/storage policy is outside this XML range.

Delegation-token web client state includes static defaults for authenticator class and token transport mode plus per-call/holder token state in `DelegationTokenAuthenticatedURL.Token`. Sending delegation tokens in query strings can persist them in logs, browser history, or intermediaries, while header transport limits that exposure.

Services persist lifecycle history snapshots, current state, start time, blockers, and first failure cause/state in memory. `LifecycleEvent` is serializable, but the service framework itself is primarily process-local. Composite services own a mutable child-service list whose ordering controls init/start/stop sequencing.

Checksum objects hold running CRC values until reset. `ReflectionUtils` can cache constructor or reflection metadata in implementation, but this chunk only exposes stateless static utilities. `ApplicationClassLoader` holds URL classpath, parent loader, and system-class pattern state. `Shell` instances hold minimum run interval and stderr redirection behavior in this visible slice; later chunk content is needed for full shell state.

## Dependencies and Integration Points

The chunk depends on JavaCC-generated parser conventions, Java I/O (`InputStream`, `Reader`, `DataInput`, `DataOutput`, `IOException`, `PrintStream`, `PrintWriter`), servlet APIs, JAAS `Subject`, Java security privileged actions, networking (`InetSocketAddress`, `URI`, `HttpURLConnection`), class loading (`URLClassLoader`, `URL`), crypto (`SecretKey`), checksums, collections, and annotations.

Hadoop-specific integration points include:

- Record compiler model classes such as `JFile`, `JRecord`, `JField`, `JType`, `JMap`, and `JVector`.
- Record I/O archives and `org.apache.hadoop.record.Record` for deprecated schema metadata serialization.
- `org.apache.hadoop.conf.Configuration` and `Configurable` for security setup, credential provider paths, impersonation providers, filters, services, and reflection-based construction.
- `org.apache.hadoop.io.Text` and `Writable` for credentials, ACLs, tokens, and token identifiers.
- `org.apache.hadoop.fs.FileSystem`, `Path`, and token-storage helpers through `Credentials`.
- Kerberos and Hadoop RPC annotations: `KerberosInfo`, `TokenInfo`, and `SaslRpcServer.AuthMethod`.
- `UserGroupInformation` as the identity object consumed by ACLs, impersonation providers, token identifiers, and privileged execution helpers.
- Hadoop authentication-client classes (`AuthenticatedURL`, `Authenticator`, `ConnectionConfigurator`) for delegation-token HTTP flows.
- Hadoop IPC `VersionedProtocol` and generated protobuf service interfaces for tracing administration.
- Commons Logging for service and utility logging.
- `Shell` platform helpers used throughout Hadoop code that invokes OS-level user/group, permission, ownership, and symlink commands.

## Risks and Edge Cases

- This chunk starts inside `RccTask` and ends inside `Shell`; complete per-class research must be merged with adjacent chunks before final file-level conclusions.
- JDiff does not show implementation bodies. Parser grammar behavior, credential merge precedence, token renewer lookup, Kerberos relogin throttling, service transition locking, HTTP rejection status codes, and shell command arrays must be validated against source code for implementation-level claims.
- All Record compiler and metadata classes in this range are deprecated in favor of Avro, but their public signatures remain compatibility commitments. Removal or signature changes can break old applications even if new code should not use them.
- JavaCC parser classes expose mutable public fields such as tokens and token metadata. External mutation can corrupt parser state or diagnostics.
- `RecordTypeInfo.compareTo` exists even though the Javadoc says the class is not meant for sorting. Callers relying on ordering may depend on accidental behavior.
- `Credentials` stores secret key bytes and token password bytes in memory and serializes them. Logging, copying, or retaining these structures increases credential exposure risk.
- `UserGroupInformation` is security-critical global/process state. Misordered `setConfiguration`, stale login users, failed relogin, incorrect proxy creation, or unsafe `doAs` use can lead to authentication failures or privilege confusion.
- Methods that tolerate unknown numeric IDs can mask identity mapping failures. Methods that do not tolerate unknown IDs can fail on heterogeneous clusters or stale name services.
- Principal expansion through `_HOST` depends on correct hostname resolution and canonicalization. Wrong addresses or DNS can produce unusable Kerberos principals.
- `AuthorizationException` suppresses stack traces, which is intentional for security but can make production debugging harder.
- ACL string parsing has wildcard and whitespace/comma semantics. Empty user/group lists, duplicate entries, and group names with unusual characters need explicit tests.
- Impersonation policy depends on both allowed groups/users and remote hosts. Misconfigured prefixes or cached proxy maps can allow or deny more than intended.
- CSRF filtering only applies to callers classified as browsers and methods not configured to be ignored. Broad ignored-method lists, lax user-agent regexes, or predictable custom headers weaken the protection.
- Delegation tokens in query strings are explicitly configurable but risk leakage through URLs. Header transport should be preferred unless interoperability requires query parameters.
- `Token` exposes raw identifier and password byte arrays. If getters return internal arrays in implementation, callers can mutate token state.
- Token renewal/cancellation depends on plugin discovery and correct `kind` matching. Trivial renewers should not be mistaken for durable managed-token behavior.
- Service lifecycle transitions must be idempotent where documented, especially `stop`. Listener callbacks receive already-changed services and should avoid reentrant state changes that deadlock or obscure failures.
- `CompositeService` shutdown policy can either stop all children or only started children. Incorrect policy expectations can leak resources after partial startup failures.
- `ApplicationClassLoader` child-first behavior can create class identity conflicts unless system-class patterns are correct.
- Pure-Java CRCs must match Java/native checksum algorithms exactly. Byte offset/length bounds and signed-byte handling are common error points.
- `ReflectionUtils.copy` and `cloneWritableInto` rely on serialization semantics; classes with incomplete `Writable` implementations will copy incorrectly.
- `Shell.isJava7OrAbove` is deprecated and always true because Hadoop requires Java 7 or later; consumers should remove conditional branches that assume older JVMs.
- Windows command-line length checks expect command parts to include delimiters, according to the Javadoc. Callers that pass raw arguments may undercount.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks that deprecated Record compiler classes, token constants, credential constants, ACL constants, and method overloads remain present with the same visibility and checked exceptions.
- Parser tests for `Rcc` valid/invalid record schemas, includes, maps, vectors, line/column parse errors, lexical errors, `ReInit` reuse, and parser tracing toggles.
- Record metadata tests for primitive type singleton equality, map/vector/struct equality and hash codes, nested record lookup, record type serialization/deserialization, `compareTo`, and `Utils.skip` across all supported type IDs.
- `Credentials` tests for token and secret-key add/get/remove/count/enumeration, `addAll` vs `mergeAll` duplicate handling, binary `Writable` round trips, file/stream token-storage round trips, and malformed/corrupt input handling.
- Group and ID mapping provider tests for cache refresh/add behavior, unknown ID/name handling, duplicate groups, primary-group behavior where relevant, and service-provider configuration prefixes.
- `SecurityUtil` tests for `_HOST` principal substitution, hostname extraction, token service construction from `InetSocketAddress` and URI service strings, annotation lookup, authentication-method mapping, privileged-port boundaries, and login error handling.
- `UserGroupInformation` tests for simple and Kerberos modes, current/login/best user selection, ticket-cache and keytab login, relogin throttling and forced-renew test hook, proxy user real-user linkage, short-name rules, group lookups, token/credential attachment, `doAs` result and exception propagation, equality/hash behavior, and token-file environment loading.
- Credential provider tests for service-loader provider resolution, provider path parsing, transient vs persistent behavior, create/read/delete/list aliases, duplicate alias rejection, missing password warning/error strings, `needsPassword`, and `flush` durability.
- ACL and impersonation tests for wildcard ACLs, empty ACLs, users-only and groups-only ACLs, mutation operations, exact `getAclString` round trips, `Writable` round trips, proxy user group/host authorization, denied authorization stack-trace suppression, and configuration-prefix key generation.
- Servlet filter tests for CSRF header acceptance/rejection, browser user-agent regexes, non-browser bypass, ignored methods, custom header names, config-prefix parameter extraction, X-Frame-Options header insertion, and filter-chain continuation/error behavior.
- Secret manager and token tests for password creation/retrieval, retriable retrieval exceptions, identifier byte stability, URL encode/decode round trips, private clone lineage, service mutation, renew/cancel dispatch, token selector matching, raw byte defensive-copy expectations, and managed vs unmanaged token behavior.
- Delegation-token web tests for default authenticator selection, Kerberos and pseudo authenticator construction, connection configuration, token transport as header vs query string, get/renew/cancel endpoint parameters, JSON response parsing, and cancellation without prior authentication where documented.
- Service lifecycle tests for legal and illegal state transitions, idempotent stop/close, failure cause/state recording, lifecycle history snapshots, wait-for-stop behavior, blocker map mutation, local/global listener notification order, service operation stopQuietly exception capture, and composite child ordering under success and partial failure.
- Trace admin tests for span receiver builder configuration pairs, protocol version, list/add/remove RPC behavior, duplicate or missing receiver IDs, and protobuf bridge compatibility.
- Utility tests for application classloader child-first and system-class matching, `IPList` implementations, repeated `Progressable.progress` callbacks in long operations, CRC32/CRC32C golden vectors and offset/length handling, reflection configured construction and writable copy/clone behavior, inherited member discovery, and visible `Shell` command builders across Unix/Windows assumptions.

## Cross-Chunk Notes

The preceding chunk is needed to complete `org.apache.hadoop.record.compiler.ant.RccTask`. A later chunk is needed to complete `org.apache.hadoop.util.Shell`, including the remainder of command helpers, execution methods, fields, platform constants, and subprocess state. Empty package markers for `org.apache.hadoop.security.protocolPB`, `org.apache.hadoop.security.ssl`, `org.apache.hadoop.tools`, and `org.apache.hadoop.tools.protocolPB` appear in this range without public types in the visible lines.

### subset-b-007185: lines 36810-38433

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml lines 36810-38433

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.8.3. It starts mid-entry in the tail of `org.apache.hadoop.util.Shell`, beginning inside the symbolic-link command method, then covers the later `Shell` command helpers, fields, and class documentation. It continues through `StringInterner`, `SysInfo`, `Tool`, `ToolRunner`, `VersionInfo`, and most of the visible `org.apache.hadoop.util.bloom` package. The chunk ends at the close of the API document after empty package markers for `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash`.

The source is generated compatibility metadata, not implementation source. The research value is the stable API contract: public/protected signatures, declared exceptions, visibility, abstract/final/static flags, deprecation markers, inherited/implemented types, fields, and Javadocs.

## Purpose

The `Shell` portion documents Hadoop's base abstraction for portable subprocess execution. It exposes command-construction helpers for symlinks, readlink, process liveness, signal delivery, script naming/execution, Hadoop home and binary discovery, Windows `winutils` lookup, bash probing, environment and working-directory injection, timeout state, and simple static command execution.

The common utility classes provide runtime support used throughout Hadoop. `StringInterner` offers strong and weak string canonicalization. `SysInfo` abstracts host-level resource metrics. `Tool` and `ToolRunner` define the standard command-line application lifecycle with Hadoop generic option parsing and configuration injection. `VersionInfo` exposes build metadata embedded in Hadoop artifacts.

The Bloom filter package documents compact probabilistic set-membership structures. It includes a plain Bloom filter, counting Bloom filter, dynamic Bloom filter, retouched Bloom filter, hash projection helper, and retouching scheme constants. These APIs support compact membership summaries with Hadoop-style serialization hooks.

## Important APIs, Types, and Functions

### Shell Tail

- The chunk begins inside the method entry for a symbolic-link command helper that accepts `target` and `link` strings and returns a command to create symbolic links.
- `getReadlinkCommand(String link)` returns a platform command for reading a symlink target.
- `getCheckProcessIsAliveCommand(String pid)` returns a `kill -0`-style command or equivalent for checking process liveness.
- `getSignalKillCommand(int code, String pid)` returns a command for sending a signal to a process.
- `getEnvironmentVariableRegex()` returns the regex used to match environment-variable references.
- `appendScriptExtension(File parent, String basename)` and `appendScriptExtension(String basename)` infer `.cmd` on Windows and `.sh` elsewhere.
- `getRunScriptCommand(File script)` returns the platform script runner, using `cmd` on Windows and `bash` otherwise.
- `getHadoopHome()` returns the Hadoop home directory and throws `IOException` if it cannot be located.
- `getQualifiedBin(String executable)` and `getQualifiedBinPath(String executable)` fully qualify Hadoop binaries from known bin locations and verify existence. The path variant also exposes canonicalization `IOException`.
- `hasWinutilsPath()`, `getWinUtilsPath()`, and `getWinUtilsFile()` are the supported `winutils` discovery API. The getters deliberately fail with exceptions when the path cannot be resolved.
- `checkIsBashSupported()` returns bash availability and can throw `InterruptedIOException`.
- Protected instance mutators `setEnvironment(Map)` and `setWorkingDirectory(File)` configure subprocess execution context.
- Protected `run()` executes the shell command if interval gating says it is needed. Subclasses provide `getExecString()` and parse stdout in `parseExecResult(BufferedReader)`.
- Runtime inspection methods include `getEnvironment(String)`, `getProcess()`, `getExitCode()`, and `isTimedOut()`.
- Static `execCommand(...)` overloads run simple command arrays with optional environment and timeout, returning stdout as `String` and throwing `IOException`.
- Public fields include `LOG`, Hadoop home property/env names, Windows command-length constants, the deprecated misspelled `WINDOWS_MAX_SHELL_LENGHT`, `USER_NAME_COMMAND`, `WindowsProcessLaunchLock`, `osType`, OS booleans, `PPC_64`, `ENV_NAME_REGEX`, Unix command names, deprecated nullable `WINUTILS`, `isSetsidAvailable`, and `TOKEN_SEPARATOR_REGEX`.
- Protected instance fields `timeOutInterval` and `inheritParentEnv` expose timeout and environment inheritance state to subclasses.

### Common Utility Classes

- `StringInterner.strongIntern(String)` returns a representative equal string retained by strong reference. `weakIntern(String)` returns a representative equal string that can be garbage collected when no strong references remain.
- `SysInfo` is abstract. `newInstance()` returns the default OS-specific implementation or throws `UnsupportedOperationException` if the OS cannot be determined.
- `SysInfo` declares metrics for total/available virtual memory, total/available physical memory, logical processors, physical cores, CPU frequency, cumulative CPU time, CPU usage percentage, vcores used, aggregate network bytes read/written, and aggregate storage bytes read/written.
- `Tool` extends `org.apache.hadoop.conf.Configurable` and defines `run(String[] args) throws Exception`, returning a process-style exit code. Its contract asks applications to delegate generic Hadoop options to `ToolRunner`.
- `ToolRunner.run(Configuration, Tool, String[])` parses generic arguments, sets the possibly modified configuration on the tool, and invokes `Tool.run`.
- `ToolRunner.run(Tool, String[])` delegates through the tool's current configuration. `printGenericCommandUsage(PrintStream)` emits generic option help, and `confirmPrompt(String)` returns true only for case-insensitive `y` or `yes`.
- `VersionInfo` has a protected component-name constructor and protected instance getters for version, revision, branch, date, user, URL, source checksum, build version, and protoc version.
- Static `VersionInfo` methods expose the Hadoop build metadata and a `main(String[])` entry point for reporting it.

### Bloom Filter APIs

- `BloomFilter` extends `Filter`. It has a default constructor for `readFields` and a `(int vectorSize, int nbHash, int hashType)` constructor. Public methods include `add(Key)`, `membershipTest(Key)`, logical `and(Filter)`, `or(Filter)`, `xor(Filter)`, `not()`, `toString()`, `getVectorSize()`, and `write(DataOutput)`/`readFields(DataInput)`.
- `CountingBloomFilter` is `final` and extends `Filter`. It supports `add(Key)`, `delete(Key)`, `membershipTest(Key)`, `approximateCount(Key)`, logical operations, string rendering, and serialization. The docs warn that adding the same key more than 15 times can overflow its buckets and raise error rates.
- `DynamicBloomFilter` extends `Filter` and adds a `(int vectorSize, int nbHash, int hashType, int nr)` constructor, where `nr` is the per-row threshold for recorded keys. It grows by adding Bloom filter rows.
- `HashFunction` is `final`; its constructor binds `maxValue`, `nbHash`, and `hashType`. `hash(Key)` returns multiple bounded integer positions, while `clear()` is documented as a no-op.
- `RemoveScheme` is a constants interface for retouched filters. It defines `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` is `final`, extends `BloomFilter`, and implements `RemoveScheme`. It records known false positives through overloads accepting a single `Key`, `Collection`, `List`, or `Key[]`; `selectiveClearing(Key, short)` applies a removal scheme; `write` and `readFields` persist retouched state.

## Control Flow

The XML has no method bodies, but the API contracts imply important execution paths.

`Shell` subclasses configure environment and working directory, then call `run()`. The base class obtains the command vector from `getExecString()`, launches the process, tracks timeout/exit/process state, and delegates stdout parsing to `parseExecResult(BufferedReader)`. Static `execCommand` is the short path for callers that only need to execute a command array and receive output.

Platform-sensitive shell flow depends on static OS detection. OS booleans, script extension helpers, `winutils` accessors, bash support checks, `setsid` availability, Unix command names, and Windows process-launch locking all shape how Hadoop starts and controls subprocesses on different hosts.

`ToolRunner` is the standard CLI flow. Generic Hadoop options are parsed into a `Configuration`, that configuration is installed on the `Tool`, and remaining application arguments are passed to `Tool.run`. Exit code and exception behavior are owned by the called tool and propagated by `ToolRunner`.

`SysInfo` flow starts with `newInstance()` selecting an OS implementation, after which clients poll resource values. Metrics are snapshots or counters, not persistent application state.

Bloom filter flow starts by binding vector size, number of hashes, and hash type. `add(Key)` hashes a key to positions and mutates the backing vector, counters, rows, or retouched metadata. `membershipTest(Key)` hashes the same key and tests whether the relevant state indicates possible membership. Logical operations combine compatible filters. Serialization flows through `write(DataOutput)` and `readFields(DataInput)`.

`CountingBloomFilter.delete(Key)` is documented as a no-op if the key is not believed present. `DynamicBloomFilter.add(Key)` inserts into an active row until the row threshold is reached, then creates a new row. `RetouchedBloomFilter.selectiveClearing` uses recorded false-positive information and a `RemoveScheme` to reset selected bits, intentionally trading away the classic no-false-negatives Bloom filter guarantee.

## State and Persistence Behavior

This JDiff file persists the 2.8.3 API surface for compatibility checks. It does not persist Hadoop runtime data.

`Shell` has process-local mutable state for environment overrides, working directory, timeout interval, parent environment inheritance, current `Process`, exit code, and timeout status. Static state caches platform classification, command names, `winutils` resolution, bash/setsid capability, and global Windows process launch synchronization. These values are not durable, but they affect every component that shells out in the current JVM.

`StringInterner` keeps canonical string representatives in memory. Strong interning can intentionally retain high-cardinality strings for the lifetime of the cache, while weak interning allows reclamation.

`SysInfo` exposes host resource state. Capacity metrics, utilization percentages, cumulative CPU time, and byte counters are runtime observations of the host and can change between calls. The docs explicitly allow unavailable sentinel values for CPU usage and vcore usage.

`ToolRunner` mutates the `Tool`'s in-memory `Configuration` before invoking `run`. Any durable effects come from the tool implementation, not from the `ToolRunner` API itself.

`VersionInfo` exposes immutable build-time metadata: version, revision, branch, date, user, source URL, checksum, build version, and protoc version.

Bloom filter classes have explicit persistence through `write(DataOutput)` and `readFields(DataInput)`. Durable state includes inherited filter parameters, bit vectors or counters, dynamic filter rows and row thresholds, hash settings, and retouched false-positive metadata. Serialized compatibility depends on stable layout and stable hash-position behavior.

## Dependencies and Integration Points

The visible APIs depend on Java platform types such as `String`, primitive arrays, `File`, `Process`, `BufferedReader`, `PrintStream`, `IOException`, `InterruptedIOException`, `FileNotFoundException`, `DataInput`, `DataOutput`, `Collection`, `List`, and `Map`.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configurable` and `Configuration` for `Tool`/`ToolRunner` configuration propagation.
- `org.apache.hadoop.util.GenericOptionsParser`, referenced as the generic command-line option parser used by `ToolRunner`.
- `org.apache.hadoop.util.Shell.OSType`, referenced by the `Shell.osType` field.
- SLF4J through `Shell.LOG`.
- `org.apache.hadoop.util.bloom.Filter` and `Key`, which define the base Bloom filter contract and key representation used by all filter variants in this chunk.
- `org.apache.hadoop.util.hash.Hash`, referenced by Bloom constructors and `HashFunction` as the hash implementation selector.
- Hadoop `Writable`-style serialization through `write(DataOutput)` and `readFields(DataInput)`.

Package integration is also visible. `org.apache.hadoop.util` is documented as common utilities. `org.apache.hadoop.util.bloom` contains the probabilistic data structures. `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash` appear as empty package elements in this line range, signaling package presence in the JDiff document but no public API entries in this chunk.

## Risks and Edge Cases

- The range begins mid-method and mid-class. The complete `Shell` API requires reconciliation with the previous chunk.
- JDiff metadata cannot show implementation details such as command quoting, stream draining, timeout enforcement, environment merging, synchronization granularity, or serialized byte layout.
- `Shell.WINUTILS` is deprecated because it can be null. The preferred getters fail explicitly and are safer for callers that cannot tolerate late null dereferences.
- The misspelled `WINDOWS_MAX_SHELL_LENGHT` is deprecated but remains public for binary/source compatibility.
- Shell command helpers return string arrays, but callers still need to avoid unsafe command construction, platform-specific path assumptions, and commands that hang beyond intended timeout bounds.
- `WindowsProcessLaunchLock` is public global synchronization state; external misuse can serialize or block unrelated Windows process launches.
- `Tool.run` throws broad `Exception`, so users of the API need clear policies for logging, exit codes, and exception-to-process-result mapping.
- `ToolRunner.confirmPrompt` is interactive and can block automation if stdin is not controlled.
- `SysInfo.newInstance()` can fail on unsupported OS detection, and some metrics can be unavailable.
- `StringInterner.strongIntern` can create memory-retention issues for high-cardinality or untrusted input.
- Bloom filters naturally permit false positives. `RetouchedBloomFilter` can also create false negatives by design.
- `CountingBloomFilter` has a documented overflow edge when a key is inserted more than 15 times, and deletion/underflow can make approximate counts lower than the real count.
- Logical Bloom operations are only meaningful on compatible filters with matching vector sizes, hash counts, and hash types. This compatibility is implied by the data structure even where not fully stated in this slice.
- `DynamicBloomFilter` memory and serialized size grow with insert volume as new rows are added. Poor threshold sizing can produce unexpectedly large state.
- The `RemoveScheme.RATIO` Javadoc contains a typo in "false positve"; the constant spelling is still the compatibility-relevant surface.

## Test Signals

Useful validation for this chunk should include:

- API compatibility checks for every visible constructor, method, field, visibility flag, abstract/final/static marker, checked exception, implemented interface, and deprecation string.
- Shell tests for symlink/readlink command construction, process liveness and signal command construction, environment-variable regex, script extension and runner selection, Hadoop home lookup, qualified bin lookup, `winutils` present/absent behavior, bash support probing, and deprecated field presence.
- Shell execution tests for environment injection, parent-environment inheritance, working-directory selection, interval-gated `run`, stdout parsing delegation, timeout marking, exit-code capture, process exposure, nonzero exits, interrupted timeouts, and `IOException` propagation.
- Platform tests for OS booleans, `PPC_64`, Windows command-length constants including the deprecated misspelling, `WindowsProcessLaunchLock`, `setsid` availability, and token-separator parsing.
- `StringInterner` tests for identity reuse, equality preservation, strong-cache retention, weak-cache reclamation expectations, and null handling according to implementation behavior.
- `SysInfo` tests for OS-specific `newInstance` selection, unsupported OS failure, sane nonnegative memory/core/frequency values where available, `-1` unavailable sentinels for CPU/vcore metrics, and monotonic cumulative counters.
- `Tool`/`ToolRunner` tests for generic option parsing into `Configuration`, modified configuration injection, pass-through application args, null configuration handling, exit-code propagation, exception propagation, usage printing, and `confirmPrompt` yes/no parsing.
- `VersionInfo` tests for non-null static metadata, build-version composition, protoc version exposure, component-specific protected getters through a test subclass, and stable `main` output.
- Bloom filter tests for add/membership round trips, tolerated false positives, no false negatives for plain filters, vector-size reporting, string rendering, compatible logical operations, and serialization round trips.
- Counting filter tests for delete no-op on absent keys, approximate counts under normal additions, collision behavior, overflow behavior after repeated additions over 15, and underflow/false-negative behavior after deletes.
- Dynamic filter tests for row creation at `nr`, membership across rows, serialization preserving all rows, and logical operations against compatible dynamic filters.
- `HashFunction` tests for deterministic positions, expected number of hashes, bounds under `maxValue`, different hash-type behavior, and `clear()` being a no-op.
- Retouched filter tests for all false-positive registration overloads, null false-positive no-op behavior, each `RemoveScheme`, targeted false-positive reduction, expected false-negative tradeoff, and serialization preserving retouched metadata.

## Cross-Chunk Notes

This chunk must be merged with the preceding chunk to complete `org.apache.hadoop.util.Shell`, because line 36810 starts after the method entry has already begun. This chunk reaches the end of the 2.8.3 JDiff XML API document, so there is no later chunk after the empty `curator` and `hash` package markers.
