# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007137`: lines 1-6132, `Docs/researches/chunks/subset-b-007137_research.md`
- `subset-b-007138`: lines 6133-12073, `Docs/researches/chunks/subset-b-007138_research.md`
- `subset-b-007139`: lines 12074-17935, `Docs/researches/chunks/subset-b-007139_research.md`
- `subset-b-007140`: lines 17936-24232, `Docs/researches/chunks/subset-b-007140_research.md`
- `subset-b-007141`: lines 24233-30540, `Docs/researches/chunks/subset-b-007141_research.md`
- `subset-b-007142`: lines 30541-36776, `Docs/researches/chunks/subset-b-007142_research.md`
- `subset-b-007143`: lines 36777-40847, `Docs/researches/chunks/subset-b-007143_research.md`

## Chunk Research

### subset-b-007137: lines 1-6132

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

### subset-b-007138: lines 6133-12073

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 6133-12073

## Scope

This chunk covers a JDiff public API description for Hadoop Common filesystem APIs. The range starts at the tail of `org.apache.hadoop.fs.CreateFlag`, then fully describes `FileAlreadyExistsException`, `FileChecksum`, `FileContext`, `FileStatus`, `FileSystem`, and `FileUtil`, and ends partway through `FilterFileSystem` after its `getUsed()` method. Because this is generated API metadata rather than Java source, it exposes signatures, inheritance, visibility, deprecation state, exceptions, and Javadoc contracts, but not method bodies.

## Purpose

The APIs in this chunk define Hadoop's core filesystem abstraction layer. They let applications address multiple URI-backed filesystems through `Path`, create/read/write/delete data, inspect metadata, manage permissions, ACLs, xattrs, symlinks, snapshots, checksums, storage policies, and statistics, and bridge local disk with remote filesystems.

`FileContext` is the newer context-oriented API over `AbstractFileSystem`: it carries default filesystem resolution, working directory, umask, and user identity. `FileSystem` is the older and still central abstract class that concrete implementations subclass. `FilterFileSystem` wraps another `FileSystem` and forwards operations. `FileStatus` and `FileChecksum` are serializable metadata/value objects. `FileUtil` supplies static helpers for local files, copies, deletion, archives, shell path handling, permissions, classpath jar expansion, and filesystem comparison.

## Important APIs, Types, and Functions

### Creation, checksums, and exceptions

- `CreateFlag` is only partially visible here, but the chunk includes documented valid flag combinations such as `CREATE`, `APPEND`, `OVERWRITE`, and combinations used by create/append streams.
- `FileAlreadyExistsException` extends `IOException` and has empty and message constructors. Its contract is specifically for operations where the target exists and overwrite was not configured.
- `FileChecksum` is an abstract `Writable` representing a file checksum. Implementations must provide `getAlgorithmName()`, `getLength()`, and `getBytes()`. The base API also exposes `getChecksumOpt()`, `equals(Object)`, and `hashCode()`, with equality defined over both algorithm and checksum bytes.

### `FileContext`

`FileContext` exposes a high-level filesystem namespace context over `AbstractFileSystem`.

- Factory methods create contexts from an `AbstractFileSystem`, default configuration, explicit `URI`, explicit `Configuration`, or the local filesystem. Failures are modeled as `UnsupportedFileSystemException`, `IOException`, or runtime failures during instantiation/login.
- Path state methods include `setWorkingDirectory(Path)`, `getWorkingDirectory()`, `getHomeDirectory()`, `getUgi()`, `getUMask()`, `setUMask(FsPermission)`, `makeQualified(Path)`, `resolvePath(Path)`, protected `resolve(Path)`, and protected `resolveIntermediate(Path)`.
- Core namespace operations include `create(Path, EnumSet<CreateFlag>, Options.CreateOpts...)`, `mkdir(Path, FsPermission, boolean)`, `delete(Path, boolean)`, `open(Path)` and `open(Path, int)`, `truncate(Path, long)`, `setReplication(Path, short)`, `rename(Path, Path, Options.Rename...)`, permission/owner/time setters, checksums, and checksum verification toggles.
- Metadata and listing APIs include `getFileStatus(Path)`, `getFileLinkStatus(Path)`, `getLinkTarget(Path)`, `getFsStatus(Path)`, `listStatus(Path)`, `listLocatedStatus(Path)`, and `listCorruptFileBlocks(Path)`.
- Symlink creation is documented with URI qualification rules for target and link paths, including how qualified and relative targets are interpreted.
- Security and metadata extension APIs cover ACL modification/replacement/removal/query, xattr set/get/list/remove with namespaced names such as `user.attr`, snapshots, and storage policies.
- Static statistics methods expose per-filesystem statistics keyed by URI scheme/authority: `getStatistics(URI)`, `clearStatistics()`, `printStatistics()`, and `getAllStatistics()`.
- Public constants include `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`. The docs note that `DEFAULT_PERM` previously applied executable permissions to files and is retained for compatibility after HADOOP-9155.

### `FileStatus`

`FileStatus` is a `Writable` and `Comparable` metadata object.

- Constructors cover empty/default status, basic size/directory/replication/block-size/time/path fields, full permission/owner/group/path forms, optional symlink target, and a copy constructor.
- Accessors expose length, file/directory/symlink type, block size, replication, modification/access times, permissions, encryption flag, owner, group, path, and symlink target.
- Mutators include `setPath`, protected `setPermission`, protected `setOwner`, protected `setGroup`, and public `setSymlink`.
- Serialization and identity APIs are `write(DataOutput)`, `readFields(DataInput)`, `compareTo(Object)`, `equals(Object)`, `hashCode()`, and `toString()`.
- `isDir()` is deprecated in favor of explicit `isFile()`, `isDirectory()`, and `isSymlink()`.

### `FileSystem`

`FileSystem` extends `Configured` and implements `Closeable`. It is the main abstract base for filesystem implementations.

- Static resolution APIs include `get(Configuration)`, `get(URI, Configuration)`, `getDefaultUri(Configuration)`, `setDefaultUri(...)`, `getLocal(Configuration)`, `newInstance(...)`, `newInstanceLocal(Configuration)`, `closeAll()`, `closeAllForUGI(UserGroupInformation)`, `getFileSystemClass(String, Configuration)`, global statistics accessors, global storage statistics, and symlink enablement.
- Identity and URI methods include `initialize(URI, Configuration)`, `getScheme()`, abstract `getUri()`, `getCanonicalUri()`, `canonicalizeUri(URI)`, `getDefaultPort()`, `getFSofPath(Path, Configuration)`, `getCanonicalServiceName()`, deprecated `getName()`, and deprecated `getNamed(String, Configuration)`.
- Core data operations include many overloaded `create(...)` methods, abstract `open(Path, int)`, abstract `append(Path, int, Progressable)`, `createNonRecursive(...)`, `primitiveCreate(...)`, `createNewFile(Path)`, `concat(Path, Path[])`, `truncate(Path, long)`, abstract `rename(Path, Path)`, protected rename with `Options.Rename`, abstract `delete(Path, boolean)`, and deprecated `delete(Path)`.
- Directory and listing operations include `mkdirs(...)`, protected `primitiveMkdir(...)`, abstract `listStatus(Path)`, filtered/list-of-path overloads, `globStatus(...)`, `listLocatedStatus(...)`, protected filtered located listing, `listStatusIterator(Path)`, `listFiles(Path, boolean)`, and corrupt block iteration.
- Metadata operations include block locations, server defaults, `resolvePath`, replication, status, content summary, quota usage, existence/type checks, home/working directory, local/remote copy helpers, local output staging/completion, used space, default block size/replication, checksum operations, checksum read/write toggles, filesystem status, permissions, owner, times, symlinks, ACLs, xattrs, snapshots, storage policies, trash roots, and builder entry points `createFile(Path)` and `appendFile(Path)`.
- Constants include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and the per-instance `statistics` object.

### `FileUtil`

`FileUtil` is a static helper collection for local and Hadoop filesystem file processing.

- Path conversion and deletion helpers include `stat2Paths(...)`, `fullyDeleteOnExit(File)`, `fullyDelete(...)`, `fullyDeleteContents(...)`, and `fullyDelete(File, boolean)`.
- Copy helpers bridge `FileSystem` and local `File`: multiple `copy(...)` overloads, `copyMerge(...)`, delete-source flags, overwrite flags, and `Configuration` propagation.
- Local utility helpers include `readLink(File)`, `makeShellPath(...)`, `getDU(File)`, `unZip(...)`, `unTar(...)`, `symLink(...)`, `chmod(...)`, `setOwner(...)`, readable/writable/executable setters and checks, `setPermission(File, FsPermission)`, temp-file creation, `replaceFile(...)`, and filtered file listing.
- Classpath helpers create jars with expanded classpaths and enumerate jars in directories, optionally using local path handling.
- `compareFs(FileSystem, FileSystem)` compares filesystem identity, and `SYMLINK_NO_PRIVILEGE` represents a symlink failure mode.

### `FilterFileSystem`

The visible part of `FilterFileSystem` shows a wrapper implementation around another `FileSystem`.

- Constructors support an empty wrapper or an immediately supplied raw filesystem.
- `getRawFileSystem()` exposes the wrapped instance.
- URI/path methods include `initialize`, `getUri`, `getCanonicalUri`, `canonicalizeUri`, `makeQualified`, and protected `checkPath`.
- Forwarded operations visible in this chunk include block locations, resolve, open, append, concat, create, `createNonRecursive`, replication, rename, truncate, delete, listing, corrupt block listing, located/status iterators, home/working directory, status, mkdirs, local copy helpers, local output staging/completion, and `getUsed()`.

## Control Flow

The documented control flow is layered around path resolution, filesystem dispatch, operation execution, and metadata/result wrapping.

For `FileContext`, callers first construct a context from configuration, a default URI, an explicit `AbstractFileSystem`, or the local filesystem. Relative paths are resolved through the context's working directory, slash-relative paths through the default filesystem, and fully qualified paths through their own scheme/authority. Operations then locate the target `AbstractFileSystem` with `getFSofPath`, apply context state such as umask, and dispatch to the underlying filesystem. The Javadoc explicitly distinguishes client-side context defaults from server-side filesystem defaults such as home directory, initial working directory, replication, block size, buffer size, data transfer encryption, and checksum parameters.

For `FileSystem`, callers generally obtain cached instances through `get(...)` or uncached instances through `newInstance(...)`. Concrete implementations provide abstract methods such as `open`, `create`, `append`, `rename`, `delete`, `listStatus`, `setWorkingDirectory`, `getWorkingDirectory`, and `getFileStatus`; the base class supplies convenience overloads, default fallbacks, validation wrappers, recursive/listing utilities, glob expansion, local copy flows, and optional-operation stubs. Builder methods (`createFile`, `appendFile`) expose a newer fluent entry point over the same create/append semantics.

The create path is especially overloaded. Public APIs accept booleans, `EnumSet<CreateFlag>`, permissions, buffer sizes, replication, block sizes, progress callbacks, and checksum options. `FileContext` applies umask before calling lower-level primitives, while `FileSystem` exposes `primitiveCreate` and `primitiveMkdir` for the transition from `FileSystem` to `FileContext`. Non-recursive creation variants fail when a parent directory is missing. `createNewFile` is documented as not atomic in the default implementation.

Listing control flow can be eager or lazy. `listStatus` returns arrays, filtered overloads apply `PathFilter`, `globStatus` expands shell-style patterns and sorts results by path/name, `listStatusIterator` returns on-demand `RemoteIterator<FileStatus>`, `listLocatedStatus` includes block locations for files, and `listFiles` traverses files recursively or non-recursively.

`FilterFileSystem` control flow is wrapper-style: path checks, URI canonicalization, stream creation, metadata calls, and mutation operations are forwarded to the wrapped raw filesystem. The raw filesystem remains observable through `getRawFileSystem()`, so wrapper subclasses can add behavior without reimplementing every backend operation.

## State and Persistence Behavior

The persistent state represented by these APIs is filesystem namespace state: files, directories, lengths, block metadata, replication, permissions, ownership, access/modification times, symlinks, ACLs, xattrs, snapshots, storage policies, checksums, and trash locations. The XML does not include concrete persistence code, but the contracts make clear which operations mutate remote or local filesystem state.

Client-side state is also significant:

- `FileContext` holds default filesystem identity, working directory, umask, and `UserGroupInformation`. Its working directory model is textual prefixing rather than a Unix-like inode-bound current directory, and the docs say `setWorkingDirectory()` does not follow symlinks.
- `FileSystem` holds `Configuration`, cached instances, shutdown-hook behavior, delete-on-exit registrations, per-filesystem `Statistics`, and storage statistics. `deleteOnExit` persists only in process memory until `close()` or clean JVM shutdown, and the docs warn that shutdown is not guaranteed and can be slow for many paths or remote/object stores.
- `FileStatus` and `FileChecksum` are `Writable`, so they can be serialized over RPCs, stored in job metadata, or passed across process boundaries.
- `FileUtil` helpers mutate local disk state for deletion, archive extraction, temporary files, replacement, permissions, ownership, and symlinks.

Several operations are optional or implementation-dependent. Append, concat, truncate, checksums, symlinks, snapshots, ACLs, xattrs, storage policies, corrupt block listings, and replication may be unsupported, no-op-like, non-atomic, or backed by filesystem-specific semantics. Rename atomicity is explicitly implementation-dependent, and the default protected rename with options is documented as non-atomic.

## Dependencies and Integration Points

These APIs are central integration points for the rest of Hadoop Common and downstream filesystems.

- Configuration and identity: `org.apache.hadoop.conf.Configuration`, `Configured`, `UserGroupInformation`, delegation `Token`, and canonical service names.
- Filesystem model: `Path`, `AbstractFileSystem`, `LocalFileSystem`, `FsStatus`, `FsServerDefaults`, `BlockLocation`, `BlockStoragePolicySpi`, `ContentSummary`, `QuotaUsage`, `StorageStatistics`, and `GlobalStorageStatistics`.
- Streams and iteration: `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `RemoteIterator`, `Progressable`, `Closeable`, `IOException`, `FileNotFoundException`, and Hadoop-specific filesystem exceptions.
- Security and metadata: `FsPermission`, `AclStatus`, ACL entry lists, xattr name/value maps, `Options.ChecksumOpt`, `Options.CreateOpts`, `Options.Rename`, and `XAttrSetFlag`-style enum sets.
- Serialization and comparison: Hadoop `Writable`, Java `Comparable`, and `DataInput`/`DataOutput`.
- Local platform integration: `java.io.File`, shell path conversion, symlink/permission/ownership changes, archive extraction, and classpath jar generation.

The API surface is also a compatibility contract for HDFS, LocalFileSystem, object-store connectors, viewfs, checksum wrappers, encryption-aware filesystems, and test/mock filesystems. Any concrete `FileSystem` must honor the abstract methods and the documented behavior of convenience methods that depend on them.

## Risks and Edge Cases

- This chunk is API metadata only. Research about implementation behavior must be treated as contract-level analysis unless verified against the Java source.
- Path qualification is subtle. `FileContext` supports fully qualified URIs, slash-relative paths resolved against the default filesystem, and working-directory-relative paths; relative paths with schemes are illegal.
- `setWorkingDirectory()` in `FileContext` does not follow symlinks. Code expecting Unix current-directory semantics can resolve later paths differently than expected.
- Umask handling differs between `FileContext` and lower-level `FileSystem` methods. The presence of `primitiveCreate` and `primitiveMkdir` indicates compatibility risk when implementing custom filesystems.
- `createNewFile()` is explicitly non-atomic in the default implementation, so it is unsafe as a distributed lock primitive unless overridden with stronger semantics.
- Rename semantics are not uniformly atomic. The option-based default implementation is documented as non-atomic, while concrete filesystems may differ.
- `deleteOnExit` is process-local and best-effort. It can lengthen shutdown, fail under remote connectivity problems, and does not guarantee cleanup on abnormal JVM termination.
- Many methods are optional operations with default unsupported behavior or weak default behavior. Tests must distinguish unsupported features from incorrect results.
- `setReplication()` default behavior may return true even when replication is unsupported, potentially masking ineffective replication changes on non-HDFS stores.
- Listing order is generally not guaranteed for `listStatus`, `listStatusIterator`, or `listFiles`, while `globStatus` documents sorted results. Callers should not rely on directory iteration ordering unless the specific API promises it.
- XAttr APIs require namespace prefixes such as `user.` and return only attributes visible to the logged-in user, so authorization and filtering affect apparent metadata.
- ACL replacement with `setAcl` must include base user/group/other entries for permission-bit compatibility.
- `FileStatus` contains deprecated `isDir()` alongside the newer explicit type checks; older callers can miss symlink distinctions.
- `FileUtil` destructive helpers such as recursive delete, replace, chmod/chown, unzip/untar, and symlink creation cross local platform boundaries and need careful failure handling in tests and tooling.
- `FilterFileSystem` exposes its raw filesystem, so wrappers cannot assume strict encapsulation. Any added behavior can be bypassed by code that unwraps the raw instance.

## Test Signals

Useful tests around the APIs described in this chunk should emphasize contract behavior across at least local and distributed/mock filesystems:

- Path resolution tests for `FileContext`: fully qualified paths, slash-relative paths, working-directory-relative paths, illegal relative-with-scheme paths, symlink resolution, and `makeQualified`.
- Creation tests for all major `CreateFlag` combinations, overwrite rejection via `FileAlreadyExistsException`, create-parent behavior, non-recursive create failures, permissions after umask, checksum options, and progress callbacks.
- Metadata tests for `FileStatus` serialization, equality/comparison, symlink fields, encryption flag, default permission/owner/group behavior, and deprecated `isDir()` compatibility.
- Listing tests for missing paths, file-vs-directory inputs, filters, glob patterns, sorted glob output, unspecified normal listing order, lazy iterator error propagation, located status block locations, and recursive `listFiles`.
- Mutation tests for rename with and without overwrite, directory/file mismatch failures, non-empty destination directory behavior, truncate return value semantics, delete recursive flags, owner/permission/time setters, and replication on filesystems that do and do not support replication.
- Optional feature tests for append, concat, checksums, symlinks, ACLs, xattrs, snapshots, storage policies, corrupt block iteration, trash roots, and storage statistics, checking both successful implementations and documented unsupported paths.
- Lifecycle tests for cached `FileSystem.get(...)` versus `newInstance(...)`, `closeAll`, `closeAllForUGI`, delete-on-exit processing/cancellation, statistics collection/clear/print, and shutdown-hook priority behavior.
- `FileUtil` tests for recursive deletion, delete-on-exit registration, local/Hadoop copy combinations, copy-merge, archive extraction, shell path formatting, disk usage, temp file creation, file replacement, permission toggles, symlink failure codes, classpath jar creation, jar directory expansion, and `compareFs`.
- `FilterFileSystem` tests should verify forwarding of URI/path operations, stream operations, metadata/listing/mutation calls, raw filesystem exposure, and wrapper behavior when the underlying filesystem throws `IOException`.

### subset-b-007139: lines 12074-17935

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 12074-17935

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.10.0. It starts in the middle of `org.apache.hadoop.fs.FilterFileSystem`, covers a broad section of public Hadoop filesystem APIs, permissions, ViewFs, high-availability protocols, protocol-buffer RPC facades, the `org.apache.hadoop.http.lib` package note, and ends partway through `org.apache.hadoop.io.ArrayPrimitiveWritable`.

Because the source is generated API metadata rather than implementation code, the useful research surface is the public contract: exported classes, interfaces, constructors, methods, fields, exceptions, and documentation comments. Implementation details must be recovered from the corresponding Java sources in later lanes if needed.

## Purpose

The chunk records the stable Hadoop Common API surface for filesystem access and related services. It documents how clients create/read/write files, address paths, query filesystem status and statistics, handle permissions/ACLs/xattrs, use local/FTP/ViewFs filesystems, move files through trash, and control HA services through RPC-compatible protocols.

The JDiff file is likely used by Hadoop release tooling to compare public APIs across versions. As such, changes in this chunk are compatibility signals: new or removed methods, changed signatures, changed exceptions, or modified visibility/deprecation metadata can affect downstream Hadoop applications and filesystem implementations.

## Important APIs, Types, and Functions

### `org.apache.hadoop.fs` filesystem contracts

- `FilterFileSystem` delegates the remaining listed methods to an underlying protected `FileSystem fs`, optionally rewriting the scheme through `swapScheme`. The visible API includes usage/default queries, file status, access checks, symlink operations, checksum toggles, owner/time/permission updates, primitive create/mkdir hooks, child filesystems, snapshots, ACLs, xattrs, storage policies, trash roots, and builder-style `createFile`/`appendFile`.
- `FsConstants` exposes core URI and scheme constants such as local filesystem URI, FTP scheme, ViewFs URI/scheme, and maximum symlink traversal count.
- `FSDataInputStream` wraps an `InputStream` with `Seekable`, `PositionedReadable`, byte-buffer reads, readahead/drop-behind controls, buffer release, unbuffering, file descriptor access, stream capability probing, and position-aware reads.
- `FSDataOutputStream` wraps an `OutputStream` with position reporting, sync/hflush/hsync, drop-behind, capability probing, and close behavior.
- `FSDataOutputStreamBuilder` is the fluent construction API for create/append output streams. It carries target `FileSystem`, `Path`, permission, buffer size, replication, block size, recursive parent creation, progress callback, create/overwrite/append flags, checksum options, and final `build()`.
- `FSInputStream`, `Seekable`, and `PositionedReadable` define random-access stream semantics: seek, current position, alternate source seeking, positional reads, and full-read loops.
- `FsServerDefaults`, `FsStatus`, `StorageStatistics`, `GlobalStorageStatistics`, `StorageType`, and `QuotaUsage` expose server defaults, capacity/used/remaining statistics, process-wide storage statistics, storage media classes, and namespace/storage quota accounting.
- `Path` is the central URI-like path value type with string/URI/component constructors, scheme/authority stripping, path merging, Windows absolute-path detection, filesystem resolution, absolute/root/name/parent/suffix/depth helpers, qualification, equality, hashing, comparison, and separator constants.
- `PathFilter` and `GlobFilter` provide path inclusion predicates, with glob filtering supporting POSIX-style glob patterns and brace expansion.
- `StreamCapabilities` and `StreamCapabilitiesPolicy` define string-named stream features including `hflush`, `hsync`, `in:readahead`, `dropbehind`, `unbuffer`, byte-buffer reads, and positional byte-buffer reads.
- `Syncable` defines the flush/sync contract: legacy `sync`, `hflush`, and `hsync`.
- `Trash` and `TrashPolicy` expose pluggable trash behavior: moving to appropriate trash roots, checking enablement, checkpoints, expunge, current trash directory, and superuser emptier runnable.
- `XAttrCodec` and `XAttrSetFlag` support xattr value encoding/decoding and validation of create/replace flag sets.

### Local, FTP, and ViewFs implementations

- `LocalFileSystem` is the checksum local filesystem wrapper. Its API exposes initialization, scheme, raw filesystem access, path-to-file conversion, local copy operations, checksum failure reporting, and symlink delegation/status.
- `RawLocalFileSystem` implements the raw local filesystem API: URI initialization, open/append/create variants, non-recursive creates, renames, Windows empty-directory handling, truncate/delete/list/mkdirs, working and home directories, local-output staging, close, file status, owner/permission/time updates, and symlink status/target operations.
- `FTPFileSystem` exposes a remote FTP-backed `FileSystem` with configurable user/password/host/port/data connection/transfer mode keys. It supports open, create, delete, list/status, mkdirs, rename, working/home directories, and documents that append is unsupported and FTP streams must be closed before other API calls.
- `ViewFileSystem` implements the `FileSystem`-style client-side mount table. It resolves incoming paths to target filesystems and forwards append/create/delete/list/open/rename/truncate/block-location/checksum/status/access/ACL/xattr/default/snapshot calls.
- `ViewFs` implements the `AbstractFileSystem`-style client-side mount table. It has parallel forwarding APIs for create/delete/block locations/checksum/status/access/list/mkdir/open/truncate/rename/symlink/owner/permission/replication/times/ACL/xattr/snapshot/storage-policy operations and adds delegation-token aggregation and name validation.
- `NotInMountpointException` marks operations that cannot be performed because a path is not inside a mount point.

### Permissions, ACLs, and security-related types

- `org.apache.hadoop.fs.permission.AccessControlException` is retained as a deprecated compatibility exception; the docs direct users to `org.apache.hadoop.security.AccessControlException`.
- `AclEntry` models one ACL entry with type, optional name, permission, scope, stable string conversion, parsing of ACL specs/entries, and list-to-string conversion.
- `AclEntryScope` and `AclEntryType` are enums for ACL scope and entry type; `AclEntryType` includes stable string output.
- `AclStatus` is immutable ACL status for a path, exposing owner, group, sticky bit, ordered entries, base `FsPermission`, and effective permission computation.
- `FsAction` models read/write/execute combinations with `implies`, `and`, `or`, `not`, string lookup, and symbolic representation.
- `FsPermission` models Unix-style file/directory permissions, sticky/ACL/encryption bits, string and short encodings, `Writable` serialization, umask application, configuration-backed umask get/set, defaults for directories/files/cache pools, and parsing from Unix symbolic strings.

### High availability and RPC protocol metadata

- `BadFencingConfigurationException`, `FailoverFailedException`, `HealthCheckFailedException`, and `ServiceFailedException` are HA-specific `IOException` subclasses for fencing, failover, health, and state-transition failures.
- `FenceMethod` defines HA fencing plugins with `checkArgs(String)` and `tryFence(HAServiceTarget, String)`.
- `HAServiceProtocol` defines monitor and state transition RPCs: `monitorHealth`, `transitionToActive`, `transitionToStandby`, `transitionToObserver`, and `getServiceStatus`. Its methods raise service-failure, access-control, health-check, and generic IO exceptions as appropriate.
- `HAServiceProtocolHelper` provides static wrappers around the HA protocol calls and documents that it unwraps `RemoteException` into specific exceptions.
- `HAServiceTarget` represents an HA admin target. It exposes service, health-monitor, and ZKFC addresses; fencing configuration and fencer access; HA and ZKFC proxy construction; fencing parameter injection; auto-failover status; and Observer-state support.
- `HAServiceProtocolPB` and `ZKFCProtocolPB` are PB RPC facades implementing generated protobuf blocking interfaces plus Hadoop `VersionedProtocol`.

### `org.apache.hadoop.io` start

- `AbstractMapWritable` is the base class for `MapWritable` and `SortedMapWritable`. It maintains per-instance class-id mappings rather than static maps, supports synchronized addition/copy, exposes class/id lookups, carries a `Configuration`, and serializes/deserializes those mappings through `Writable`.
- `ArrayFile` is a `MapFile` specialization for dense integer-to-value mappings.
- The chunk begins `ArrayPrimitiveWritable`, showing constructors for empty read-time instances, known primitive component type, and object-backed construction. Its complete API continues after this chunk.

## Control Flow

The file does not contain executable control-flow bodies, but the API contracts imply several recurring flows.

Filesystem read flow starts with a `Path`, resolves a `FileSystem` or `AbstractFileSystem`, opens an `FSDataInputStream`, and then uses sequential reads, positioned reads, seek/getPos, byte-buffer reads, optional readahead/drop-behind hints, and stream capability checks. Implementations may redirect the request through wrappers such as `FilterFileSystem`, checksum-aware `LocalFileSystem`, raw local IO, FTP, or ViewFs mount resolution.

Filesystem write flow uses either direct create/append overloads or `FSDataOutputStreamBuilder`. Builder state accumulates permissions, buffer size, replication, block size, progress callbacks, parent creation, create/overwrite/append flags, and checksum options before `build()` asks the target filesystem to create or append. Output streams then expose position, close, hflush/hsync/sync, drop-behind, and capability checks.

Metadata flow is path-driven. Status, content/quota usage, ACL, xattr, storage policy, checksum, block locations, permissions, ownership, and timestamp operations all accept `Path` and may raise `IOException` or more precise access/not-found/unsupported exceptions. `FilterFileSystem`, `ViewFileSystem`, and `ViewFs` act as forwarding layers that preserve these contracts while delegating to the target filesystem.

ViewFs flow is client-side mount resolution. Configuration entries under `fs.viewfs.mounttable.*` define links from a view namespace to one or more backing filesystems. `resolvePath` maps a view path to a target path, then the operation is executed on the backing filesystem. The docs note in-memory client-side state and describe merge mounts, while also noting merge mounts are not implemented in this documented version.

Permission flow uses `FsAction` and `FsPermission` for mode bits and `AclEntry`/`AclStatus` for extended ACL semantics. ACL text is parsed into entries, entries are converted to stable strings, and effective permissions can be computed from ACL status plus optional mode bits.

Trash flow constructs a configured `TrashPolicy`, tests whether trash is enabled, resolves an appropriate trash directory for the path/filesystem, moves entries to trash, and optionally creates/deletes checkpoints or returns a periodic emptier runnable.

HA admin flow operates through `HAServiceTarget` and `HAServiceProtocol`. Admin code builds proxies to a target service, optional health-monitor endpoint, or ZKFC; monitors health; requests state transitions; checks current status; and invokes configured fencing methods during failover. Helper methods wrap RPC calls and translate remote exceptions.

`AbstractMapWritable` serialization flow records per-instance class-to-byte and byte-to-class mappings, writes them through `Writable`, and reconstructs them during `readFields` so nested `MapWritable` values can carry their own dynamic class tables.

## State and Persistence Behavior

The JDiff XML itself is a persisted API artifact. It preserves the release's public type signatures, deprecation state, visibility, thrown exceptions, and doc comments for compatibility checking.

Runtime state described by the APIs is mostly held by implementations:

- `FilterFileSystem` stores the wrapped `FileSystem` and optional scheme swap.
- Stream classes hold wrapped input/output streams and maintain logical positions; they may also propagate read-ahead, drop-behind, unbuffer, and sync behavior to the underlying stream if supported.
- Builder instances hold pending create/append options until `build()`.
- `Path`, `FsStatus`, `FsServerDefaults`, `LocatedFileStatus`, `QuotaUsage`, ACL entries/statuses, and permissions are value objects used in client and server metadata exchange.
- `GlobalStorageStatistics` stores process-wide named `StorageStatistics` instances and can reset them.
- `StorageStatistics` instances hold filesystem or `FileContext` counters and expose long-statistic iteration.
- `TrashPolicy` holds the selected `FileSystem`, trash path, and deletion interval; concrete policies perform persistence by moving files and writing checkpoints in the filesystem namespace.
- `ViewFileSystem`/`ViewFs` maintain an in-memory client-side mount table initialized from configuration and delegate persistence to target filesystems.
- `FTPFileSystem` keeps connection/configuration state for a remote FTP endpoint. The docs warn that open FTP streams block other API calls until closed.
- `FsPermission` implements `Writable`, so permission state is persisted over Hadoop binary serialization and encoded as shorts/octal strings.
- `AbstractMapWritable` persists dynamic class-id mappings in the serialized `Writable` payload.

## Dependencies and Integration Points

This API surface integrates with the rest of Hadoop Common:

- Core configuration through `org.apache.hadoop.conf.Configuration`, especially filesystem defaults, umask, FTP settings, and ViewFs mount-table entries.
- Filesystem value and service types such as `Path`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `ContentSummary`, `QuotaUsage`, `FsStatus`, `FileChecksum`, `BlockStoragePolicySpi`, `FsServerDefaults`, and `RemoteIterator`.
- Permission and security packages: `org.apache.hadoop.fs.permission.*` and `org.apache.hadoop.security.AccessControlException`.
- IO abstractions and serialization: Java `InputStream`/`OutputStream`/`DataInput`/`DataOutput`, Hadoop `Writable`, and `Configurable`.
- Stream feature interfaces such as `CanSetReadahead`, `CanSetDropBehind`, `CanUnbuffer`, byte-buffer read interfaces, and sync interfaces referenced by capability names.
- Local platform behavior via `RawLocalFileSystem`, Java `File`, file descriptors, chmod/chown command behavior, symlink support, and Windows path/rename handling.
- Remote filesystem behavior through FTP configuration keys and Apache Commons Net style FTP concepts implied by data connection and transfer modes.
- ViewFs mount table utilities and constants referenced by docs: `FsConstants`, `Constants`, and `ConfigUtil`.
- HA management modules: `NodeFencer`, `ZKFCProtocol`, `HAServiceStatus`, `HAServiceProtocol.StateChangeRequestInfo`, protobuf-generated service interfaces, and Hadoop IPC `VersionedProtocol`.
- HTTP UI filter integration via package documentation for `hadoop.http.filter.initializers`, including `StaticUserWebFilter`.

## Risks and Edge Cases

- This is generated API metadata, not source implementation. It can identify public contracts but cannot prove forwarding correctness, locking, validation, resource cleanup, or exception ordering.
- The chunk starts and ends mid-class. `FilterFileSystem` methods before line 12074 and most of `ArrayPrimitiveWritable` after line 17935 must be merged from adjacent chunks for a complete per-file report.
- `FilterFileSystem`, `LocalFileSystem`, `RawLocalFileSystem`, `ViewFileSystem`, and `ViewFs` all expose similar operations; compatibility depends on wrappers preserving semantics and exceptions of the delegated filesystem.
- Symlink handling spans support detection, create, link status, link target, and resolution. Implementations that partially support symlinks can diverge in `getFileStatus` versus `getFileLinkStatus` behavior.
- Positioned reads and seekable streams have strict argument validation and end-of-file behavior. The API exposes both partial reads and `readFully`, so callers and implementations must not conflate them.
- Byte-buffer read and unbuffer capabilities are optional. Callers must use `hasCapability` or tolerate unsupported behavior.
- `FSDataOutputStreamBuilder` has interacting create/overwrite/append flags; invalid flag combinations or missing parent behavior are likely compatibility-sensitive.
- FTP streams are explicitly serialized by connection behavior: a stream must be closed before other APIs or calls can block. This is a major operational risk for code that treats FTP like a normal concurrent filesystem.
- `RawLocalFileSystem` exposes platform-specific behavior, including Windows absolute paths, Windows empty-directory rename handling, local chmod/chown/timestamp commands, and local symlink behavior.
- ViewFs mount tables are client-side and configuration-driven. Bad link configuration, operations outside mount points, unimplemented merge mounts, and cross-filesystem rename/delete semantics are important edge cases.
- ACL and permission string conversion has both regular and stable forms. Tests need to ensure stable strings do not change across releases, because downstream tools may persist or compare them.
- `FsPermission.getUMask` still documents deprecated umask-key compatibility and decimal interpretation; config migration can produce subtle permission changes.
- XAttr encoding/decoding depends on selected `XAttrCodec` and shell/XML string representations; invalid encodings and create/replace flag validation need explicit coverage.
- HA transition APIs are no-ops if already in the target state, but failures can arise from service state, access control, health checks, or IO/RPC failures. Admin tools must distinguish these exception classes.
- `HAServiceTarget.getHealthMonitorAddress()` can split health RPCs from the main service RPC address. Incorrect target implementations can silently put health checks back on the overloaded main RPC path.
- `AbstractMapWritable` limits class ids to 1..127 per instance; maps with too many distinct `Writable` classes or inconsistent class tables are serialization risks.

## Test Signals

Useful tests for this chunk should focus on API contract compatibility and representative implementation behavior:

- JDiff/API compatibility checks that compare method signatures, exceptions, visibility, deprecation tags, constructors, and public/protected fields against expected Hadoop 2.10.0 output.
- `FSDataInputStream` and `FSInputStream` tests for seek/getPos, positional reads, `readFully`, EOF behavior, invalid read arguments, byte-buffer reads, alternate source seeking, unbuffering, and capability names.
- `FSDataOutputStream` and builder tests for create, overwrite, append, recursive parent creation, permission/buffer/replication/block-size/checksum propagation, hflush/hsync/sync, close, and drop-behind.
- Local and raw local filesystem tests for path-to-file conversion, checksum failure reporting, symlink status/target, owner/permission/time updates, mkdirs/delete/truncate/rename, working directory, and Windows-specific path/rename behavior.
- FTP filesystem tests for configuration-derived authority/user/password/port, open/create/delete/list/status/mkdir/rename, unsupported append, and enforcement that unclosed streams block or prevent subsequent FTP operations.
- ViewFs and ViewFileSystem tests for mount-table initialization, default and authority-specific tables, path resolution, operations through mount points, operations outside mount points, child filesystem listing, delegation-token aggregation, and documented non-support for merge mounts.
- Permission tests for `FsAction` algebra, `FsPermission` short/octal/symbolic encodings, sticky/ACL/encrypted bits, umask configuration including deprecated keys, `Writable` round trips, and default permissions.
- ACL tests for parsing ACL specs and entries, stable string conversion, ACL status immutability/order, and effective-permission computation with and without explicit permission arguments.
- XAttr tests for text/hex/base64 encode/decode paths, invalid encodings, list/get/set/remove operations through filesystem wrappers, and `XAttrSetFlag.validate` create/replace behavior.
- Trash tests for appropriate trash root resolution across symlinks or mount points, disabled trash, already-in-trash paths, checkpoint creation/deletion, current trash directory lookup, and superuser emptier scheduling.
- Storage/quota/statistics tests for `FsStatus` writable round trips, global statistics put/get/reset/iteration, storage type parsing/movable/quota-support lists, and quota string/header formatting.
- HA tests for monitor health, active/standby/observer transitions, status retrieval, helper unwrapping of remote exceptions, fencing argument validation, fencing parameter injection, health-monitor address selection, ZKFC proxy creation, auto-failover flags, and Observer support.
- `AbstractMapWritable` tests for per-instance class map serialization, nested `MapWritable`, copy constructors, id/class lookup, configuration propagation, and failure around the 127-class limit.

### subset-b-007140: lines 17936-24232

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 17936-24232

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.10.0. It starts inside the tail of `org.apache.hadoop.io.ArrayPrimitiveWritable`, covers most of the public `org.apache.hadoop.io` package API, closes that package, opens `org.apache.hadoop.io.compress`, and ends partway through `org.apache.hadoop.io.compress.GzipCodec`.

Because this file is generated API metadata rather than executable source, the research surface is the public compatibility contract: packages, classes, interfaces, inheritance, implemented interfaces, constructors, method signatures, fields, checked exceptions, deprecation markers, and embedded Javadoc. Adjacent chunks own the start of `ArrayPrimitiveWritable` and the remainder of `GzipCodec`.

## Purpose

The `org.apache.hadoop.io` portion describes Hadoop's core serialization and binary data model. It defines `Writable` and `WritableComparable`, primitive writable wrappers, byte/text containers, polymorphic writable wrappers, map/array writable containers, raw comparators, stringification helpers, file-backed key/value containers such as `MapFile` and `SequenceFile`, and utility routines for stream copying, varint encoding, UTF-8 handling, checksums/hashes, cloning, and safe string reads.

The `org.apache.hadoop.io.compress` portion describes the streaming compression abstraction used by Hadoop I/O and file formats. It defines codecs, codec discovery, compressor/decompressor pooling, compression input/output stream base classes, block compression stream variants, the compressor/decompressor state-machine interfaces, default/direct decompression hooks, and BZip2/Gzip codec APIs.

## Important APIs, Types, and Functions

### Core writable data model

- `Writable` is the base serialization contract: `write(DataOutput)` serializes object fields and `readFields(DataInput)` deserializes into reusable storage.
- `WritableComparable` combines `Writable` with `Comparable` for MapReduce keys and explicitly warns that key `hashCode()` values must be stable across JVM instances.
- Primitive wrappers include `BooleanWritable`, `ByteWritable`, `ShortWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, `DoubleWritable`, `VIntWritable`, and `VLongWritable`. They expose constructors, `set()`, `get()`, `readFields()`, `write()`, equality, hash, comparison, and string conversion.
- `VIntWritable` and `VLongWritable` store integer/long values in Hadoop's variable-length, zero-compressed encoding, tying them to `WritableUtils.readVInt()` and `WritableUtils.readVLong()`.
- `NullWritable` is a singleton no-data writable for places where a key or value position is semantically empty.

### Binary, text, and object wrappers

- `BinaryComparable` defines byte-backed comparison via abstract `getBytes()` and `getLength()`, with concrete byte comparison, equality, and hash behavior using `WritableComparator` helpers.
- `BytesWritable` is a mutable byte sequence with backing-array access, exact copy access, length/capacity mutation, byte-range `set()`, and binary-compatible serialization. Deprecated `get()` and `getSize()` point callers to `getBytes()` and `getLength()`.
- `Text` stores UTF-8 bytes with byte-level comparison and traversal. It exposes constructors from strings, bytes, and other `Text`; `copyBytes()`, `getBytes()`, `charAt()`, `find()`, range `set()`/`append()`, `clear()`, bounded `readFields()`/`write()`, static `readString()`/`writeString()`, UTF-8 `encode()`/`decode()`, `validateUTF8()`, `bytesToCodePoint()`, `utf8Length()`, and `DEFAULT_MAX_LEN`.
- `ObjectWritable` serializes a declared class plus an instance, supporting `Writable`, `String`, primitives, and arrays. Its static `writeObject()`/`readObject()` methods have configuration-aware overloads and an `allowCompactArrays` flag intended for RPC/internal use rather than persisted inter-cluster or file output.
- `GenericWritable` is a more compact wrapper for a bounded set of writable implementation classes returned by subclass-provided `getTypes()`.
- `ArrayPrimitiveWritable`, `ArrayWritable`, `TwoDArrayWritable`, `MapWritable`, `SortedMapWritable`, and `EnumSetWritable` provide writable containers for primitive arrays, homogeneous writable arrays, matrices, maps, sorted maps, and enum sets.

### File, comparator, utility, and helper APIs

- `SequenceFile` exposes default compression-type configuration and many static `createWriter()` overloads for `FileSystem`, `FileContext`, `FSDataOutputStream`, key/value classes, replication/block options, compression type, codecs, progress callbacks, metadata, create flags, and modern `Writer.Option...`. Many legacy overloads are explicitly deprecated in favor of `createWriter(Configuration, Writer.Option...)`. `SYNC_INTERVAL` is the public sync marker interval constant.
- `MapFile` exposes `rename()`, `delete()`, `fix()`, `main()`, and `INDEX_FILE_NAME`/`DATA_FILE_NAME` for directory-backed sorted key/value maps. `BloomMapFile` adds Bloom-filter membership acceleration and has `BLOOM_FILE_NAME` and `HASH_COUNT`.
- `SetFile` extends `MapFile`; in this chunk only its class shell/constructor appears, with nested reader/writer details likely elsewhere in the generated snapshot.
- `RawComparator` compares serialized objects directly from byte slices. `WritableComparator` implements `RawComparator` plus `Configurable`, provides registry access via `get()` and `define()`, object and byte-slice `compare()` hooks, byte lexicographic comparison, stable byte hashing, primitive byte-array readers, and varint readers.
- `WritableFactories` and `WritableFactory` let non-public writable implementations be instantiated by factory, which is important for `ObjectWritable`.
- `WritableUtils` groups compressed byte/string array I/O, normal string I/O, enum I/O, writable cloning, varint/vlong encode/decode helpers, varint size/sign inspection, `skipFully()`, writable array to bytes, and `readStringSafely()` length checks.
- `IOUtils` provides stream copy overloads, compressed-data read wrapping, `readFully()`, `skipFully()`, close/cleanup helpers, socket close, full `ByteBuffer` writes to channels, directory listing with exception propagation, file/channel `fsync()`, and `readFullyToByteArray()`.
- `DefaultStringifier` and `Stringifier<T>` define object-to-string round trips backed by Hadoop serializers and `Configuration` storage/load helpers.
- `CompressedWritable` defines lazy-inflated writable storage through `ensureInflated()`, subclass hooks `readFieldsCompressed()` and `writeCompressed()`, and compressed `readFields()`/`write()` wrappers.
- `MD5Hash` is a writable/comparable MD5 digest holder with constructors from hex or bytes, static digest helpers for byte arrays, `InputStream`, `String`, and deprecated `UTF8`, plus half/quarter digest projections.
- `MultipleIOException` aggregates multiple `IOException` instances and can return either one exception or a wrapper.
- `VersionedWritable` writes a version byte and checks it during read; `VersionMismatchException` reports mismatches.

### Compression APIs

- `CompressionCodec` is the codec contract for creating compression/decompression streams with or without pooled `Compressor`/`Decompressor` instances, discovering required compressor/decompressor classes, creating instances, and reporting a default filename extension.
- `CompressionCodecFactory` discovers codecs from `io.compression.codecs`, Java `ServiceLoader`, and defaults such as gzip/deflate; it looks up codecs by path suffix, canonical class name, or case-insensitive aliases, and provides `removeSuffix()`.
- `CodecPool` leases and returns reusable compressors/decompressors and exposes leased counts per codec.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases. Input implements `Seekable`, supports `getPos()`, `resetState()`, and default unsupported seek behavior; output supports `finish()` without closing the underlying stream and `resetState()` without resetting that stream.
- `Compressor` and `Decompressor` are stream-state interfaces modeled after `Deflater` and `Inflater`. They expose `setInput()`, `needsInput()`, dictionaries, `finish()`/`finished()` where relevant, byte counters for compressors, `compress()`/`decompress()`, `reset()`, `end()`, and compressor `reinit(Configuration)`.
- `CompressorStream` and `DecompressorStream` wrap compressor/decompressor instances with buffers and closed/eof state. They provide read/write loops, finish/reset/close behavior, protected compressor/decompressor hooks, skip/available, and mark/reset behavior.
- `BlockCompressorStream` and `BlockDecompressorStream` adapt block-oriented algorithms by writing uncompressed block length plus length-prefixed compressed chunks and by reading/decompressing block records.
- `BZip2Codec` implements `SplittableCompressionCodec`, has configuration accessors, normal stream creation, split stream creation with `READ_MODE`, default `.bz2` extension, and Javadocs noting native-vs-pure-Java behavior, unsupported compressor/decompressor methods in pure-Java mode, and split support being pure-Java only.
- `DefaultCodec` implements `CompressionCodec` and `DirectDecompressionCodec`; `DirectDecompressionCodec` and `DirectDecompressor` add direct `ByteBuffer` decompression. The chunk begins `GzipCodec`, showing it extends `DefaultCodec` and overrides stream and compressor/decompressor factory methods.

## Control Flow

The XML itself has no runtime control flow, but the documented APIs imply several important flows:

- Writable serialization is caller-driven: callers instantiate or reuse a writable, call `write(DataOutput)` to emit a deterministic binary representation, and call `readFields(DataInput)` to mutate an existing object from bytes. Containers such as arrays, maps, enum sets, `ObjectWritable`, and `GenericWritable` add type metadata or type indexes around nested writable values.
- Binary comparison avoids full deserialization when possible. `RawComparator.compare(byte[], int, int, byte[], int, int)` compares serialized byte ranges; `WritableComparator` defaults to deserializing into `WritableComparable` objects but allows optimized byte-level overrides and provides static byte parsing helpers for those overrides.
- Text handling keeps data in UTF-8 bytes. `Text` can search, index, validate, and compare at byte level, while string conversion happens only through explicit encode/decode methods or `toString()`. Its serialized length uses zero-compressed integer encoding.
- SequenceFile writer creation converges through a broad overload set. Older callers pass filesystem/path/key/value/compression details directly; newer callers use `Writer.Option...`. The API preserves deprecated overloads for binary/source compatibility.
- Compression streams follow a state loop. Callers feed uncompressed input to a `Compressor` with `setInput()` when `needsInput()` is true, drain compressed bytes with `compress()`, call `finish()`, and check `finished()`. Decompression mirrors this with `Decompressor.setInput()`, `decompress()`, `needsInput()`, dictionary handling, `finished()`, and `getRemaining()` for concatenated streams.
- Codec discovery is name/suffix driven: `CompressionCodecFactory` loads configured and service-discovered codec classes, builds suffix and alias maps, then returns codecs for file paths, class names, or aliases.
- Pooled compression flow leases compressor/decompressor instances from `CodecPool`, uses them with codec-created streams, resets or reinitializes them as needed, and returns them to the pool to avoid repeated native allocation.

## State and Persistence Behavior

The JDiff file itself persists API metadata for compatibility checks and release documentation. It does not store application data.

The APIs it describes are persistence-sensitive. `Writable`, `WritableComparable`, `Text`, primitive writables, `MapWritable`, `SortedMapWritable`, `ArrayWritable`, `ObjectWritable`, `GenericWritable`, `MD5Hash`, `VersionedWritable`, and `WritableUtils` define binary formats used in RPC, MapReduce shuffle/sort, SequenceFiles, MapFiles, and other Hadoop data paths. Deprecation notes matter because old serialized data and old callers may remain in production.

Several classes expose mutable backing state. `BytesWritable.getBytes()` and `Text.getBytes()` return backing arrays whose valid range is only `getLength()`. `ArrayPrimitiveWritable` explicitly wraps primitive arrays without copying. `Text.clear()` does not clear or free the backing byte array. `CompressedWritable` stores compressed data and inflates lazily on field access. These behaviors are performance-oriented but make object reuse and external mutation part of the practical state model.

Configuration persistence appears through `DefaultStringifier.store()`, `load()`, `storeArray()`, and `loadArray()`, which serialize objects into `Configuration` keys; `SequenceFile.setDefaultCompressionType()` stores a default compression enum in a `Configuration`. `WritableFactories` and `WritableComparator.define()` maintain static registries for instantiation and comparison behavior.

File persistence appears through `MapFile` and `SequenceFile`. `MapFile` documents a directory containing `data` and `index` files, and `fix()` can recreate a corrupt index from data. `SequenceFile.createWriter()` creates on-filesystem binary key/value files with optional compression, metadata, sync markers, and filesystem creation options.

Compression state is mostly stream-local or pooled. `CompressorStream`/`DecompressorStream` retain compressor/decompressor handles, buffers, closed/eof flags, and resettable codec state. `CodecPool` keeps global reusable compressor/decompressor state and leased counters.

## Dependencies and Integration Points

The APIs depend on Java `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `Socket`, `ByteBuffer`, `FileChannel`, `WritableByteChannel`, `MessageDigest`, charset coding exceptions, collections, and Java `Closeable`/`Comparator`.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configurable` for object configuration, stringification, codec discovery, comparator construction, and compressor reinitialization.
- `org.apache.hadoop.fs.FileSystem`, `FileContext`, `Path`, `FSDataOutputStream`, `Seekable`, `Options.CreateOpts`, and create flags for file-backed APIs.
- `org.apache.hadoop.util.Progressable` for legacy SequenceFile writer progress.
- `org.apache.hadoop.io.serializer.SerializationFactory`, `Serializer`, and `Deserializer` through `DefaultStringifier`.
- MapReduce/shuffle/sort consumers that require `WritableComparable` keys, stable `hashCode()` partitioning, and optimized `RawComparator` implementations.
- Compression users such as SequenceFile, codecs selected from path suffixes, splittable input formats, native compression libraries, and direct `ByteBuffer` decompression paths.
- Logging via `org.slf4j.Logger` in `IOUtils` and `CompressionCodecFactory`.

## Risks and Edge Cases

- The chunk starts and ends inside classes. A file-level summary must merge with adjacent chunks before making final claims about all `ArrayPrimitiveWritable` and `GzipCodec` methods.
- JDiff records API shape, not implementation bodies. Behavioral conclusions come from Javadocs and signatures; implementation details such as exact buffer growth policy, pool synchronization, and exception messages require source-code validation.
- Backing-array exposure in `BytesWritable`, `Text`, and `ArrayPrimitiveWritable` can leak stale bytes, allow external mutation, or retain large buffers after logical clear. Callers that need exact-length immutable content must use `copyBytes()` or copy arrays explicitly.
- Writable binary compatibility is fragile. Changing `write()`/`readFields()` order, varint encodings, enum string names, class names in `ObjectWritable`, or `VersionedWritable` version semantics can break persisted files and inter-process compatibility.
- `ObjectWritable`'s `allowCompactArrays` flag is documented as suitable for RPC/internal or intra-cluster usage and unsuitable for inter-cluster/file/persisted output. Misuse can create incompatible durable encodings.
- `WritableComparable` warns that default `Object.hashCode()` is not stable across JVMs. Any key implementation using identity hash can partition inconsistently.
- `WritableComparator.define()` requires thread-safe comparators. A stateful optimized comparator can corrupt sort/shuffle behavior under concurrent use.
- `Text` APIs use byte positions, not Java char indexes, for operations such as `find()` and `charAt()`. Invalid positions or trailing UTF-8 bytes return `-1`; mixed byte/char assumptions can produce off-by-one bugs.
- BZip2 behavior differs between native and pure-Java modes. The Javadocs say pure-Java mode does not implement `Compressor`/`Decompressor` interface paths and split input always uses pure Java, so tests must cover both configuration modes.
- Decompressor input buffer ownership is explicit: callers must not modify input bytes until `needsInput()` indicates it is safe. Violating this contract can cause corrupt decompression without a defensive copy.
- `CompressionInputStream.seek()` and `seekToNewSource()` are documented as unsupported defaults despite implementing `Seekable`; callers must not assume all compression streams are seekable unless a subclass says so.
- Codec alias lookup is case-insensitive and strips `Codec` suffixes, so alias collisions between configured/service-loaded codecs can change which codec is selected.

## Test Signals

Useful validation for this API surface should include:

- Round-trip serialization tests for every primitive writable, `BytesWritable`, `Text`, `MD5Hash`, `ArrayWritable`, `TwoDArrayWritable`, `MapWritable`, `SortedMapWritable`, `EnumSetWritable`, `ObjectWritable`, `GenericWritable`, `NullWritable`, and `VersionedWritable` success/failure cases.
- Binary compatibility tests against golden bytes for varint/vlong encodings, `Text` length encoding, primitive writables, `ObjectWritable` class metadata, and `SequenceFile`/`MapFile` data written by earlier Hadoop versions.
- Comparator tests comparing object-level and byte-level results for `BinaryComparable`, `BytesWritable`, `Text`, primitive writables, `WritableComparator`, and custom registered comparators.
- Backing-array tests proving `getBytes()` valid ranges, `copyBytes()` exact length, `Text.clear()` retention behavior, and `ArrayPrimitiveWritable` no-copy semantics.
- UTF-8 tests for malformed inputs, replacement vs exception behavior, byte-position `find()`, `charAt()` on leading/trailing bytes, maximum length enforcement, `validateUTF8()`, and `readStringSafely()` negative/oversize lengths.
- IO utility tests for partial reads/skips/writes, EOF handling, cleanup swallowing/logging behavior, socket close, directory listing exceptions, file/channel `fsync()`, and compressed-data read wrapping.
- `SequenceFile.createWriter()` tests for modern options and deprecated overloads, compression type defaults, codec selection, metadata, create-parent behavior, `FileContext` options, sync interval behavior, and progress callback compatibility.
- `MapFile.fix()` tests for missing/corrupt indexes, dry-run behavior, valid entry counts, and data/index filename expectations.
- Compression tests for codec discovery from configuration and `ServiceLoader`, path suffix lookup, alias lookup/collisions, `removeSuffix()`, codec pool lease/return counts, stream `finish()` vs `close()`, reset-state behavior after repositioning, and direct `ByteBuffer` decompression.
- BZip2 tests in native and pure-Java modes, including unsupported compressor/decompressor paths in pure-Java mode and split input boundary/progress behavior.
- Decompressor concatenated-stream tests where `finished()` plus positive `getRemaining()` triggers reset before reading the next stream.

## Cross-Chunk Notes

`subset-b-007139` should provide the opening of `ArrayPrimitiveWritable` and earlier `org.apache.hadoop.io` classes such as `AbstractMapWritable` and any nested types that precede this chunk. `subset-b-007141` should complete `GzipCodec` and continue the `org.apache.hadoop.io.compress` package. The merge lane should avoid duplicating final package-level conclusions until these adjacent chunks are reconciled.

### subset-b-007141: lines 24233-30540

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 24233-30540

## Scope

This chunk is part 5 of the Hadoop Common 2.10.0 JDiff API snapshot. It starts at the tail of `org.apache.hadoop.io.compress.GzipCodec`, covers complete API sections for split compression streams, TFile metadata utilities, Hadoop serialization adapters, old and new metrics APIs, metrics sinks, network topology/socket helpers, and the start of the deprecated `org.apache.hadoop.record` package. The range ends inside the `RecordOutput` interface after `writeInt`, so the record output contract continues in the following chunk.

Because this is a JDiff XML file, it records public/protected API surface, inheritance, deprecation, method signatures, exceptions, fields, and embedded Javadoc. It does not contain Java method bodies. Control flow and persistence notes below are therefore inferred from the exposed contracts and documented behavior, not from implementation statements.

## Purpose

The source file is a compatibility and documentation artifact for Hadoop Common's public API. It lets release tooling compare API signatures across Hadoop versions and helps downstream consumers understand which classes, methods, constants, and deprecations are visible in Hadoop Common 2.10.0.

This chunk concentrates on infrastructure APIs used by storage formats, serialization, monitoring, network placement, and legacy record I/O. The most active parts are the `metrics2` APIs and sinks, the TFile byte-container helpers, and network topology mapping contracts. Several older APIs are preserved but explicitly deprecated in favor of newer systems: `org.apache.hadoop.metrics.*` and `org.apache.hadoop.metrics.spi.*` point users to `metrics2`, and `org.apache.hadoop.record.*` points users to Avro.

## Important APIs, Types, and Functions

### Split compression and TFile

- `org.apache.hadoop.io.compress.GzipCodec` exposes `createDirectDecompressor()` and `getDefaultExtension()` in this tail, confirming gzip codec integration with direct decompression and default suffix discovery.
- `SplitCompressionInputStream` extends `CompressionInputStream` and carries an adjusted compressed-stream range. Its constructor accepts an input stream plus requested `start` and `end`; protected `setStart()`/`setEnd()` let codec implementations adjust the range; `getAdjustedStart()` and `getAdjustedEnd()` expose the post-adjustment offsets to callers.
- `SplittableCompressionCodec` extends `CompressionCodec` and adds `createInputStream(InputStream seekableIn, Decompressor decompressor, long start, long end, READ_MODE readMode)`. The contract is for codecs that can decompress from arbitrary compressed offsets, with `READ_MODE` controlling position reporting.
- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are TFile metadata exceptions for duplicate or missing meta blocks.
- `RawComparable` models a byte-array slice with `buffer()`, `offset()`, and `size()`, to be compared by an external `RawComparator`.
- `TFile` documents Hadoop's typed-less key/value file container: block compression, named meta blocks, sorted or unsorted keys, seek by key or file offset, key size limited to 64KB, and value size limited practically by storage. It exposes `makeComparator(String)`, `getSupportedCompressionAlgorithms()`, `main(String[])`, compression constants `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, and comparator constants `COMPARATOR_MEMCMP`, `COMPARATOR_JCLASS`.
- `Utils` provides TFile support routines: variable-length integer encoding/decoding (`writeVInt`, `writeVLong`, `readVInt`, `readVLong`), Text-style string encoding (`writeString`, `readString`), and generic `lowerBound`/`upperBound` binary search helpers with and without explicit comparators.

### Serialization adapters

- `JavaSerialization` implements `Serialization` for Java `Serializable` classes and is marked experimental.
- `JavaSerializationComparator` extends `DeserializerComparator`; it deserializes objects with Java serialization and compares them through `Comparable`.
- `WritableSerialization` extends `Configured` and implements `Serialization`, delegating to `Writable.write(DataOutput)` and `Writable.readFields(DataInput)`.
- The package doc records the integration point: `io.serializations` selects the configured `Serialization` implementations that can create `Serializer` and `Deserializer` instances.
- `org.apache.hadoop.io.serializer.avro.AvroReflectSerializable` is a marker interface for Avro reflection serialization.
- `AvroReflectSerialization`, `AvroSerialization`, and `AvroSpecificSerialization` provide Avro-backed serialization classes. `AvroReflectSerialization` exposes `AVRO_REFLECT_PACKAGES` for configured package acceptance, while `AvroSerialization` exposes `AVRO_SCHEMA_KEY`.

### Log and metrics v1

- `org.apache.hadoop.log.metrics.EventCounter` is a Log4J `AppenderSkeleton` that counts events by log level. It exposes `append(LoggingEvent)`, `close()`, and `requiresLayout()`.
- `org.apache.hadoop.metrics` has package-level API documentation for reporting performance metric information, but the active class definitions in this chunk are mostly in deprecated SPI packages.
- `org.apache.hadoop.metrics.ganglia.GangliaContext` extends `AbstractMetricsContext` and is deprecated in favor of `org.apache.hadoop.metrics2.sink.ganglia.GangliaSink30`. It sends metrics via UDP datagrams to configured Ganglia servers, with public/protected fields for XDR buffer state, server list, and socket. It exposes `emitMetric`, `getUnits`, `getSlope`, `getTmax`, `getDmax`, `xdr_string`, and `xdr_int`.
- `org.apache.hadoop.metrics.spi.AbstractMetricsContext` is the deprecated v1 SPI root. It manages context initialization, factory attributes, monitoring lifecycle, record creation, updater registration, buffered record updates/removal, emission, flushing, timer period parsing, and access to all records.
- Deprecated v1 SPI helpers include `CompositeContext`, `MetricsRecordImpl`, `MetricValue`, `NoEmitMetricsContext`, `NullContext`, `NullContextWithUpdateThread`, `OutputRecord`, and `Util.parse`.

### Metrics2 core and builders

- `AbstractMetric` is an immutable metric with `MetricsInfo`, `value()`, `type()`, visitor dispatch, equality, hash, and string conversion.
- `MetricsCollector` builds records by name or `MetricsInfo`.
- `MetricsException` is the runtime wrapper for metrics failures.
- `MetricsFilter` accepts or rejects names, tags, tag collections, and records.
- `MetricsInfo` exposes immutable metric/tag metadata: `name()` and `description()`.
- `MetricsJsonBuilder` and `MetricStringBuilder` extend `MetricsRecordBuilder` to render metrics as JSON or delimited strings while supporting tags, context, counters, gauges, parent collector access, and `toString()`.
- `MetricsPlugin` defines plugin initialization with `SubsetConfiguration`.
- `MetricsRecord` is an immutable snapshot with timestamp, name, description, context, tags, and metric iterable.
- `MetricsRecordBuilder` is the fluent interface for adding tags, pre-made metrics, context, int/long counters, int/long/float/double gauges, ending records, and returning the parent collector.
- `MetricsSink` consumes `MetricsRecord` objects and flushes buffered output.
- `MetricsSource` exposes `getMetrics(MetricsCollector, boolean all)`.
- `MetricsSystem` registers/unregisters sources and callbacks, publishes metrics immediately, and shuts down. `MetricsSystemMXBean` exposes start/stop, metrics MBean lifecycle, and current configuration through JMX.
- `MetricsTag` is immutable grouping metadata with `MetricsInfo` plus a string value.
- `MetricsVisitor` is the double-dispatch visitor for int/long/float/double gauges and int/long counters.

### Metrics2 annotation, filters, registry, and mutables

- `@Metric` and `@Metrics` annotation interfaces mark single metrics and metric groups.
- `GlobFilter` and `RegexFilter` extend `AbstractPatternFilter` and compile glob or regex patterns for metrics filtering.
- `DefaultMetricsSystem` is an enum singleton facade exposing `initialize(String)`, `instance()`, and `shutdown()`.
- `Interns` interns `MetricsInfo` and `MetricsTag` instances through `info()` and `tag()` overloads.
- `MetricsRegistry` owns a record name or `MetricsInfo`, looks up metrics and tags, creates counters, gauges, quantiles, stats, rates, rates with aggregation, rolling averages, records tags, adds samples by metric name, sets context, snapshots all mutable metrics into a builder, and stringifies the registry.
- `MutableMetric` is the base mutable metric with `snapshot(builder, all)`, changed-flag management, and `changed()`.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` model monotonic counters with `incr()` overloads, value accessors, and snapshots.
- `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong` model gauges with `incr`, `decr`, `set`, value accessors, and snapshots.
- `MutableQuantiles` estimates quantiles for long streams and exposes `add`, `snapshot`, `stop`, `getInterval`, `getEstimator`, `setEstimator`, static `quantiles`, and protected `previousSnapshot`.
- `MutableRate`, `MutableRates`, `MutableRatesWithAggregation`, `MutableRollingAverages`, and `MutableStat` support latency/throughput statistics. The docs call out important concurrency semantics: `MutableRates` synchronizes all access and can contend, while `MutableRatesWithAggregation` uses per-thread local state and can lose samples produced by threads that die before the next snapshot. `MutableStat.add(numSamples, sum)` can preserve means while producing inaccurate variance for large aggregated batches.

### Metrics2 sinks and utilities

- `FileSink`, `GraphiteSink`, and `StatsDSink` implement `MetricsSink` and `Closeable`, with `init(SubsetConfiguration)`, `putMetrics`, `flush`, and `close`. `StatsDSink` also exposes `writeMetric(String)` and documents StatsD line shape plus configuration keys.
- `RollingFileSystemSink` implements `MetricsSink` and `Closeable` for filesystem-backed rolling metric logs. It exposes testable constructors, `init`, `getRollInterval`, `updateFlushTime`, `setInitialFlushTime`, `putMetrics`, `flush`, and `close`; protected/static fields include `source`, `ignoreError`, `allowAppend`, `basePath`, roll intervals, `nextFlush`, `forceFlush`, `hasFlushed`, `suppliedConf`, and `suppliedFilesystem`.
- `RollingFileSystemSink` integrates with Hadoop `FileSystem`, supports local/HDFS/S3-style paths, creates time-interval directories in GMT, supports optional append, random roll offsets to spread load, secure Kerberos properties, and error-swallowing behavior through `ignore-error`.
- `MBeans` registers and unregisters standard Hadoop MBeans under `hadoop:service=<serviceName>,name=<nameName>` and can extract service/name parts from an `ObjectName`.
- `MetricsCache` caches dense sink-side records for sinks that do not support sparse updates. It supports fixed-capacity construction, `update` overloads, and `get`.
- `Servers.parse` parses comma/space-separated server specs into socket addresses.

### Network APIs

- `AbstractDNSToSwitchMapping` is the base class for rack/topology mapping and implements Hadoop configuration support. It exposes `isSingleSwitch`, diagnostic `getSwitchMap`, `dumpTopology`, script-policy checks, and static `isMappingSingleSwitch`.
- `CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping`, caches hostname/IP-to-switch results, exposes the raw mapping field, supports `resolve`, `getSwitchMap`, `reloadCachedMappings()` overloads, `isSingleSwitch`, and `toString`.
- `ConnectTimeoutException` extends `SocketTimeoutException` for `NetUtils.connect` timeout failures.
- `DNSToSwitchMapping` is the pluggable topology interface: `resolve(List<String>)`, `reloadCachedMappings()`, and `reloadCachedMappings(List<String>)`.
- `ScriptBasedMapping` extends `CachedDNSToSwitchMapping`, supports constructors for default/raw/configuration-backed mappings, exposes `NO_SCRIPT`, and delegates configuration to a script-based raw mapper.
- `SocksSocketFactory` extends `SocketFactory` and implements `Configurable`; it creates sockets through an optional SOCKS proxy and implements equality/hash based on proxy/config state.
- `StandardSocketFactory` extends `SocketFactory` for normal sockets.
- `TableMapping` extends `CachedDNSToSwitchMapping`, is configurable, and reloads mappings from a table file.

### Deprecated record I/O

- `BinaryRecordInput` and `BinaryRecordOutput` implement `RecordInput`/`RecordOutput`, expose constructors over streams and `DataInput`/`DataOutput`, thread-local `get(...)` factories, primitive read/write methods, buffer read/write, and record/vector/map start/end methods.
- `Buffer` is a deprecated byte-sequence value type used by record I/O. It exposes constructors over no bytes, a byte array, or a byte range; `set`, `copy`, `get`, `getCount`, `getCapacity`, `setCapacity`, `reset`, `truncate`, `append` overloads, `hashCode`, `compareTo`, `equals`, encoding-aware `toString`, and `clone`.
- `CsvRecordInput` and `CsvRecordOutput` provide CSV-backed record serialization with primitive, string, buffer, record, vector, and map methods.
- `Index` is the vector/map deserialization iterator, with `done()` and `incr()`.
- `Record` is the abstract generated-record base class implementing `WritableComparable` and `Cloneable`. It requires tagged `serialize`, tagged `deserialize`, and `compareTo`, and supplies untagged `serialize`, untagged `deserialize`, `write(DataOutput)`, `readFields(DataInput)`, and `toString`.
- `RecordComparator` extends `WritableComparator`, requires raw byte comparison, and exposes synchronized static `define(Class, RecordComparator)` for optimized record comparators.
- `RecordInput` defines the full tagged deserialization contract for primitive values, strings, `Buffer`, record boundaries, vector boundaries, and map boundaries.
- `RecordOutput` begins in this chunk and defines tagged serialization for `writeByte`, `writeBool`, and `writeInt` before the chunk boundary. The remainder of `RecordOutput` is outside this range.

## Control Flow

The XML is structured as a package/class/member stream. JDiff consumers read each `<package>`, then nested class/interface declarations, constructors, methods, fields, implemented interfaces, exceptions, parameters, deprecation markers, and documentation blocks. For this chunk, the effective flow is API enumeration rather than executable control flow.

At the API-contract level, common runtime flows exposed here are:

- Split compression callers select a `SplittableCompressionCodec`, request a `SplitCompressionInputStream` for compressed offsets, then inspect adjusted start/end offsets because codecs may shift boundaries to valid compression block positions.
- TFile users choose compression/comparator constants, create/read TFile data blocks and meta blocks through APIs documented elsewhere in the XML, use `RawComparable` slices for raw key comparison, and use `Utils` to encode compact integer/string metadata and perform sorted-index searches.
- Serialization users configure `io.serializations`; Hadoop asks each `Serialization` implementation whether it accepts a class, then obtains serializers/deserializers. Writable serialization delegates to `Writable`; Java serialization and Avro variants integrate with their respective object models.
- Metrics2 sources push current values into a `MetricsCollector`/`MetricsRecordBuilder`; mutable metrics snapshot changed or all values into builders; the `MetricsSystem` publishes records to configured sinks; sinks flush or close their output targets.
- Network topology mapping resolves hostnames to rack paths through raw, cached, script, or table-backed `DNSToSwitchMapping` implementations. Cache reload calls invalidate all or selected entries.
- Deprecated record objects serialize and deserialize by walking record boundaries, primitive fields, buffers, vectors, and maps. `Index` controls vector/map iteration on read, and `RecordComparator` allows byte-level comparison without full object construction.

## State and Persistence Behavior

Most state described by this chunk is API-level or in-memory:

- `SplitCompressionInputStream` retains adjusted range state for callers that split compressed inputs.
- TFile's persistent format is explicitly documented: key/value bytes, compressed data blocks, named meta blocks, sorted/unsorted key support, block indexes, meta-block indexes, and configurable chunk/input/output buffer sizes. The documented memory footprint scales with compressed block codecs, temporary key/value buffers, data-block index count, and meta-block index count.
- TFile `Utils` encodes variable-length integers and strings into persistent binary form. Any incompatible change to these encodings would break on-disk compatibility.
- `MetricsRegistry` and the mutable metrics classes hold live process metrics: changed flags, counters, gauges, quantile estimators, rolling windows, rate maps, and last-snapshot statistics.
- `MutableQuantiles`, `MutableRollingAverages`, `MutableRatesWithAggregation`, and `MutableStat` maintain internal sample history or thread-local aggregation, so snapshot timing affects emitted values.
- `RollingFileSystemSink` writes persistent metric log files through `FileSystem` and has state for base path, roll interval, next flush time, append behavior, and supplied testing filesystem/configuration. It also documents HDFS append and file-size visibility limitations.
- `GangliaContext`, `GraphiteSink`, and `StatsDSink` emit metrics to external systems; their durable state lives outside Hadoop once packets or lines are accepted by those systems.
- `CachedDNSToSwitchMapping` stores an in-memory host-to-switch cache and exposes diagnostic copies; `TableMapping` reloads file-backed mappings.
- `Buffer` owns mutable byte-array capacity/count state. `Record` bridges deprecated record serialization with Hadoop `Writable` persistence through `write` and `readFields`.

## Dependencies and Integration Points

- Compression APIs depend on `CompressionCodec`, `CompressionInputStream`, `Decompressor`, `DirectDecompressor`, and codec-specific split/read-mode behavior.
- TFile APIs integrate with `java.io.DataInput/DataOutput`, `java.util.Comparator`, `RawComparator`, Hadoop `Text`-style byte strings, compression codecs, and Hadoop `Configuration` keys `tfile.io.chunk.size`, `tfile.fs.output.buffer.size`, and `tfile.fs.input.buffer.size`.
- Serialization APIs integrate with Hadoop `Writable`, `Serialization`, `Serializer`, `Deserializer`, `RawComparator`, Avro reflect/specific APIs, and the `io.serializations` configuration property.
- Metrics v1 integrates with Log4J, Ganglia UDP/XDR, `ContextFactory`, `MetricsRecord`, updater callbacks, and the deprecated `org.apache.hadoop.metrics` package.
- Metrics2 integrates with Apache Commons Configuration `SubsetConfiguration`, JMX through `MetricsSystemMXBean` and `MBeans`, sinks, sources, collectors, records, visitors, annotations, filters, and mutable metric registries.
- Filesystem metrics sinks depend on Hadoop `FileSystem`, `Path`, `Configuration`, optional Kerberos keytab/principal properties, append support, and the semantics of the destination filesystem.
- Network helpers integrate with Hadoop `Configurable`, `Configuration`, `SocketFactory`, Java `Proxy`, `Socket`, `SocketAddress`, DNS resolution, external topology scripts, and table mapping files.
- Deprecated record I/O integrates with `WritableComparable`, `WritableComparator`, `DataInput/DataOutput`, Java collections for vectors/maps, generated record classes, and Avro migration guidance.

## Risks and Edge Cases

- This XML is generated API metadata. Research consumers must not infer private implementation behavior from it; method-body details, synchronization internals, resource cleanup, and error paths are absent unless documented in Javadoc or signature flags.
- The chunk begins mid-class (`GzipCodec`) and ends mid-interface (`RecordOutput`). Merge/reconciliation must combine adjacent chunks before treating the source-file research as complete.
- `SplittableCompressionCodec` explicitly allows start/end offsets to change. Callers that continue using requested offsets instead of `getAdjustedStart()`/`getAdjustedEnd()` can duplicate or skip decompressed data around split boundaries.
- TFile's documented concurrency limitation says multiple scanners on the same TFile may serialize actual I/O because implementation uses `seek()+read()`. Random-access and multi-threaded readers need tests around shared stream behavior.
- TFile `Utils` variable-length integer encoding is a compatibility boundary. Boundary values near one-, two-, three-, and wider-byte transitions should be preserved exactly.
- Java serialization is marked experimental and compares through deserialized `Comparable` objects, which can be slow, classloader-sensitive, and unsafe for untrusted data.
- Deprecated metrics v1 and record APIs remain public. Removing or changing signatures would break compatibility even if users are expected to migrate to `metrics2` or Avro.
- `MutableRatesWithAggregation` documents that samples can be lost when short-lived threads exit before snapshot. It should not be used where every event must be counted exactly.
- `MutableStat.add(numSamples, sum)` warns that variance may be inaccurate for large aggregate batches even when the mean is correct.
- `RollingFileSystemSink` has filesystem-specific risks: append may not be supported, HDFS append requires enough data nodes, file sizes may not update until close, and `ignore-error` can hide write failures when set to its permissive behavior.
- `RollingFileSystemSink` exposes static testing hooks (`forceFlush`, `hasFlushed`, `suppliedConf`, `suppliedFilesystem`), which are useful for tests but can create global-state coupling if misused.
- Topology mapping depends on DNS, scripts, or mapping files. Cache reload semantics must be exercised, especially selected-node reloads.
- SOCKS and standard socket factories implement equality/hash behavior; misconfigured proxy state could affect factory reuse in connection caches.
- Deprecated record CSV/binary APIs rely on tagged field names for XML/CSV-style formats and on `Index` iteration for collections. Generated records must keep read/write order and comparator definitions consistent.

## Test Signals

- JDiff/API tests should verify that this XML remains parseable across chunk boundaries and that class/interface/member names, deprecation text, visibility, static/final flags, exceptions, and implemented interfaces are preserved.
- Compression tests should cover split gzip-adjacent codec behavior where codecs adjust start/end, `READ_MODE` differences, direct decompressor creation, and default extension reporting.
- TFile tests should cover supported compression names, raw comparator creation, duplicate/missing meta block exceptions, VInt/VLong round trips at all documented boundary ranges, string encoding round trips, and lower/upper-bound results with duplicate keys.
- Serialization tests should exercise `io.serializations` selection for Writable, Java Serializable, Avro reflect marker classes, Avro reflect package configuration, and Avro specific classes.
- Metrics2 tests should validate builder chaining, tags/context propagation, source-to-sink publication, immediate `publishMetricsNow`, shutdown behavior, JMX lifecycle, filters, annotations, and visitor dispatch for each primitive metric type.
- Mutable metrics tests should cover changed-flag snapshots, all-vs-changed snapshots, counter monotonicity, gauge set/incr/decr, quantile estimator snapshots/stopping, rolling-average window eviction, rate aggregation under multiple threads, and `MutableStat` min/max reset.
- Sink tests should cover file, Graphite, StatsD, and rolling filesystem output, including flush/close idempotence, invalid configuration, HDFS/local paths, roll interval parsing, roll offset scheduling, append/no-append behavior, Kerberos property requirements, and `ignore-error` behavior.
- MBean and metrics cache tests should verify canonical object names, unregister handling, sparse update densification, capacity behavior, and server-spec parsing.
- Network tests should cover cache hits/misses, full and partial cache reloads, script-disabled `NO_SCRIPT` behavior, table reload behavior, single-switch detection, socket factory proxy creation, equality/hash semantics, and connect-timeout exception propagation.
- Record I/O tests should cover binary and CSV primitive round trips, `Buffer` capacity/count/truncate/append/clone/compare behavior, vector/map `Index` iteration, generated `Record.write/readFields` compatibility, and `RecordComparator.define` lookup behavior.

## Cross-Chunk Notes

Adjacent chunks are required for a complete view of this XML source. `subset-b-007140` contains the earlier part of `GzipCodec` and preceding Hadoop Common APIs. `subset-b-007142` continues the remainder of `RecordOutput` and subsequent packages. The merge lane should retain this document's note that all behavior here is API-contract research from JDiff XML rather than implementation-level Java code.

### subset-b-007142: lines 30541-36776

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 30541-36776

## Scope

This chunk is a JDiff API descriptor slice for Hadoop Common 2.10.0. It starts in the middle of `org.apache.hadoop.record.RecordOutput`, covers the remaining legacy record I/O runtime/compiler/metadata APIs, then covers much of Hadoop Common's security API surface through the beginning of `org.apache.hadoop.security.token.delegation.web.DelegationTokenAuthenticatedURL`. It is generated API metadata, not executable implementation, but it documents public constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, and deprecation notes that downstream compatibility tooling consumes.

The visible package areas are:

- `org.apache.hadoop.record`: tail of `RecordOutput`, `Utils`, `XmlRecordInput`, and `XmlRecordOutput`.
- `org.apache.hadoop.record.compiler`, `.ant`, and `.generated`: deprecated record DDL compiler types, Ant task integration, JavaCC parser/token stream classes.
- `org.apache.hadoop.record.meta`: deprecated runtime type metadata for record I/O.
- `org.apache.hadoop.security`: access-control exception, credentials, group/id mapping interfaces, Kerberos exception utilities, `SecurityUtil`, `UserGroupInformation`, and `AuthenticationMethod`.
- `org.apache.hadoop.security.alias`: credential provider abstraction and factory.
- `org.apache.hadoop.security.authorize`: ACLs, authorization exception, impersonation provider contracts and default provider.
- `org.apache.hadoop.security.http`: REST CSRF and X-Frame-Options servlet filters.
- Empty package markers for `org.apache.hadoop.security.protocolPB` and `org.apache.hadoop.security.ssl`.
- `org.apache.hadoop.security.token`: secret manager, token, token identifier, renewer/selector contracts, and token metadata annotation.
- `org.apache.hadoop.security.token.delegation.web`: constructors and primary delegation-token HTTP methods for `DelegationTokenAuthenticatedURL`, ending before the class is complete.

## Purpose

The XML preserves the public API contract for compatibility comparison. For the deprecated record I/O packages, it documents the old Hadoop record serialization stack and record compiler retained for binary/source compatibility after Avro replacement. For the security packages, it captures the central contracts used by Hadoop clients, RPC, HTTP services, and filesystem integrations for credentials, Kerberos login, delegation tokens, proxy-user authorization, servlet-level request hardening, and token lifecycle operations.

The file's role is therefore twofold: it is an input to JDiff/API-change reporting, and it is a compact map of externally visible Hadoop Common classes that tests and downstream projects may compile against.

## Important APIs, Types, and Functions

### Legacy record I/O runtime

- `RecordOutput` exposes primitive and composite serialization callbacks such as `writeInt`, `writeLong`, `writeFloat`, `writeDouble`, `writeString`, `writeBuffer`, `startRecord`, `endRecord`, `startVector`, `endVector`, `startMap`, and `endMap`. Every method accepts a tag for tagged formats such as XML and can throw `IOException`.
- `org.apache.hadoop.record.Utils` provides low-level binary helpers: `readFloat`, `readDouble`, `readVLong`, `readVInt`, `getVIntSize`, `writeVLong`, `writeVInt`, and `compareBytes`, plus the public static `hexchars` table. The variable-length integer format is zero-compressed and is shared by stream and byte-array readers.
- `XmlRecordInput` implements `RecordInput` over an `InputStream`, exposing typed reads for primitives, strings, buffers, records, vectors, and maps. `startVector` and `startMap` return an `Index` iterator.
- `XmlRecordOutput` implements `RecordOutput` over an `OutputStream`, mirroring the typed write and composite-boundary API.
- These APIs are all deprecated in favor of Avro, but their signatures remain part of Hadoop Common 2.10.0 compatibility.

### Record compiler and generated parser

- `CodeBuffer` wraps `StringBuffer` with indentation support for generated source.
- `Consts` exposes compiler constants such as `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.
- `JType` is the deprecated base for record compiler type descriptors. Primitive and composite subclasses in this chunk include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JBuffer`, `JString`, `JVector`, `JMap`, and `JRecord`; `JField` wraps a named field and its type.
- `JFile` represents a parsed record DDL file and exposes `genCode(language, destDir, options)` to generate source for a selected language.
- `RccTask` is an Ant `Task` wrapper around the record compiler with setters for language, file, fail-on-error, destination directory, filesets, and an `execute()` entry point.
- `ParseException`, `Rcc`, `RccConstants`, `RccTokenManager`, `SimpleCharStream`, `Token`, and `TokenMgrError` are JavaCC-generated parser infrastructure for record DDL. `Rcc` exposes parser methods for `Input`, `Include`, `Module`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, plus token access and parser reinitialization.

### Record metadata

- `FieldTypeInfo` pairs a field name with a `TypeID` and implements equality/hash behavior.
- `TypeID` represents primitive type IDs and publishes shared constants such as `BoolTypeID`, `BufferTypeID`, `ByteTypeID`, `DoubleTypeID`, `FloatTypeID`, `IntTypeID`, `LongTypeID`, and `StringTypeID`.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` model composite record types and expose accessors for element, key/value, or field metadata.
- `RecordTypeInfo` extends `Record` and serializes/deserializes record type metadata through `RecordOutput` and `RecordInput`. It tracks the record name, fields, nested struct information, and comparison behavior.
- `org.apache.hadoop.record.meta.Utils.skip()` skips encoded data from a `RecordInput` based on a `TypeID`.

### Core security and identity APIs

- `AccessControlException` extends filesystem permission access-control exceptions and provides default, message, and cause constructors.
- `Credentials` implements `Writable` for in-memory and persisted token/secret-key sets. It can add, fetch, remove, merge, read, and write tokens and secret keys, including helpers for token storage files and streams.
- `GroupMappingServiceProvider` defines user-to-group lookup and cache management methods. `IdMappingServiceProvider` defines UID/GID/name mapping methods, including variants that allow unknown identities.
- `KerberosAuthException` is an `IOException` carrying user, principal, keytab, ticket-cache, and initial-message context for unrecoverable UGI/Kerberos failures.
- `SecurityUtil` provides process-wide security helpers: Kerberos principal substitution, login from configuration/keytab, delegation-token service name construction and parsing, annotation lookup for `KerberosInfo` and `TokenInfo`, execution as login/current user, authentication-method mapping, and privileged-port detection.
- `UserGroupInformation` is the central identity container. The public surface includes static configuration/initialization, login/current/best UGI lookup, ticket-cache and keytab login/relogin/logout, proxy and remote user creation, test users, username/group accessors, token and credential attachment, authentication-method accessors, equality/hash behavior, subject access, `doAs` execution, debug logging, and a diagnostic `main`.
- `UserGroupInformation.AuthenticationMethod` is an enum-like nested type exposing `values`, string `valueOf`, `getAuthMethod`, and conversion from `SaslRpcServer.AuthMethod`.

### Credential providers and authorization

- `CredentialProvider` abstracts password/credential storage. It exposes transient-provider detection, `flush`, credential lookup, alias listing, credential creation/deletion, password-required status, and user-facing warning/error strings for missing provider passwords. `CLEAR_TEXT_FALLBACK` is visible as a public constant.
- `CredentialProviderFactory` creates credential providers from configured paths and exposes the `CREDENTIAL_PROVIDER_PATH` configuration key.
- `AccessControlList` implements `Writable` ACL parsing and mutation. It supports wildcard ACLs, users, groups, add/remove operations, membership checks against `UserGroupInformation`, string rendering, and wire serialization.
- `AuthorizationException` extends Hadoop security `AccessControlException`; the API also exposes stack trace and print methods.
- `ImpersonationProvider` extends `Configurable`, with `init(configurationPrefix)` and `authorize(proxyUser, remoteAddress)`.
- `DefaultImpersonationProvider` implements that contract, exposes a test provider, reads proxy-user groups/hosts from configuration, authorizes doAs users, and publishes helper methods for proxy-user config keys.

### HTTP filters

- `RestCsrfPreventionFilter` implements `javax.servlet.Filter` for CSRF protection. It identifies browser user agents, enforces a custom header except for configured methods, supports a testable `HttpInteraction` path, and exposes config-key constants such as `HEADER_USER_AGENT`, browser-user-agent and custom-header parameters, ignored-method parameters, and default header name.
- `XFrameOptionsFilter` implements `Filter` and adds clickjacking protection through an `X-Frame-Options` header. It exposes `X_FRAME_OPTIONS`, custom header configuration, filter lifecycle methods, and a `getFilterParams` configuration helper.

### Tokens and delegation-token HTTP client APIs

- `SecretManager<T extends TokenIdentifier>` is the server-side token secret contract. It creates passwords, retrieves passwords, supports retriable password lookup with standby/retriable/IO exceptions, creates empty identifiers, checks read availability, generates random secret keys, computes HMAC password bytes, and converts raw bytes to `SecretKey`.
- `Token<T extends TokenIdentifier>` implements `Writable` as the client-side token form. It stores identifier bytes, password bytes, kind, and service; supports cloning, decoding identifiers, service mutation, private token clones, URL-safe encode/decode, equality/hash/string/cache-key behavior, managed-token detection, renewal, and cancellation.
- `Token.TrivialRenewer` is a `TokenRenewer` for unmanaged token kinds. Subclasses provide a kind; managed checks and renew/cancel are trivial or unsupported as appropriate.
- `TokenIdentifier` implements `Writable` and defines token kind, associated `UserGroupInformation`, identifier bytes, and MD5-based tracking IDs.
- `TokenInfo` is an annotation marker for protocols that carry token information.
- `TokenRenewer` is the plugin interface for token lifecycle handlers: `handleKind`, `isManaged`, `renew`, and `cancel`.
- `TokenSelector<T extends TokenIdentifier>` chooses a token from a collection for a named service.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` and is the HTTP client bridge for delegation-token-aware web endpoints. This chunk includes constructors using the default authenticator, a supplied `DelegationTokenAuthenticator`, a `ConnectionConfigurator`, or both; static default-authenticator setters/getters; query-string-versus-header transmission controls; authenticated connection opening with optional `doAs`; delegation-token fetch with optional `doAsUser`; token renewal with optional `doAsUser`; and cancellation with optional `doAsUser`.

## Control Flow

For record I/O, the public control flow is format-neutral and callback based. Generated records call `startRecord`, per-field primitive/composite write methods, then `endRecord` on a `RecordOutput`; readers mirror that by calling `startRecord`, typed `read*` methods, vector/map `Index` iteration, and `endRecord`. The XML serializer/deserializer are concrete implementations of those contracts, while `Utils` supplies the binary primitive encoding support used by other formats.

The record compiler flow is: JavaCC tokenizes and parses record DDL through `RccTokenManager`, `SimpleCharStream`, `Token`, and parser methods on `Rcc`; parsed modules, records, fields, and types become `JFile`, `JRecord`, `JField`, and `JType` objects; `JFile.genCode()` emits target-language code. `RccTask.execute()` wraps the same flow for Ant builds.

The security identity flow centers on `UserGroupInformation`: configuration initializes authentication behavior; callers obtain login/current/remote/proxy UGIs; Kerberos logins use ticket caches or keytabs and can relogin; tokens and credentials attach to the subject; privileged work runs under a selected identity via `doAs`. `SecurityUtil` supplies the glue for principal resolution, token-service naming, and annotation-driven protocol security metadata.

Credential and authorization flow is configuration driven. `CredentialProviderFactory` resolves provider paths into provider instances; clients create/read/delete entries and flush durable providers. Proxy-user checks pass an effective proxy UGI and remote address through an `ImpersonationProvider`, with `DefaultImpersonationProvider` consulting configured users, groups, and hosts. `AccessControlList` then provides a lower-level user/group membership predicate for service authorization.

HTTP hardening flow is servlet-filter based. The CSRF filter initializes from servlet configuration or Hadoop configuration parameters, classifies user agents, and rejects browser-originating unsafe requests that lack the required custom header. The X-Frame-Options filter initializes a configured header value and adds it while passing the request down the filter chain.

Token flow splits server and client responsibilities. A server-side `SecretManager` creates identifiers, secrets, and passwords and validates retrieval. A client-side `Token` serializes identifier/password/kind/service, can be decoded from URL-safe strings, can select a service, and delegates lifecycle operations to registered `TokenRenewer` implementations. `DelegationTokenAuthenticatedURL` uses normal authentication to obtain or renew tokens, prefers an existing delegation token when opening HTTP connections, and can cancel tokens without an additional configured-authenticator login path.

## State and Persistence Behavior

Most record I/O state is stream-local. `XmlRecordInput` and `XmlRecordOutput` wrap input/output streams; metadata objects such as `RecordTypeInfo`, `FieldTypeInfo`, and `TypeID` describe schemas and can be serialized through the record I/O interfaces. The JDiff XML records only method contracts, but the exposed APIs imply persistent wire formats for primitive values, variable-length integers, record metadata, and generated record definitions.

The generated parser classes maintain mutable lexical/parser state: current tokens, token source, input stream, token images, lexical state arrays, buffer positions, line/column arrays, and parse-exception context. These are reinitialized through overloaded `ReInit` methods.

`Credentials` is explicitly persistent. It is a `Writable` containing token and secret-key maps, can read/write token storage streams/files, and can merge or overwrite entries from another `Credentials` instance. `AccessControlList` is also `Writable`, preserving ACL strings across Hadoop configuration or RPC/storage boundaries.

`UserGroupInformation` carries both static process state and per-identity state. Static configuration determines security mode and login user behavior; individual UGIs carry subject, authentication method, real/effective user relationship, groups, token identifiers, tokens, and credentials. Kerberos keytab and ticket-cache paths are represented in failure context through `KerberosAuthException` and used by login/relogin APIs.

Credential providers may be transient or durable. `flush()` is the persistence boundary for providers that buffer changes, while `needsPassword`, `noPasswordWarning`, and `noPasswordError` expose provider-state constraints to callers.

Tokens persist as `Writable` byte arrays and can also be encoded as URL-safe strings for transport. Token identifiers provide raw bytes and tracking IDs; token service fields are text keys used by clients, selectors, and renewers. `DelegationTokenAuthenticatedURL` stores a delegation token inside its nested token type outside the visible range, and this chunk documents the operations that mutate or consume that state.

## Dependencies and Integration Points

- Record I/O APIs depend on `java.io` streams, `DataInput`, `DataOutput`, `IOException`, Java collections, and Hadoop record primitives such as `Buffer`, `Record`, `RecordInput`, `RecordOutput`, and `Index`.
- The record compiler integrates with JavaCC-generated parser types and Ant via `org.apache.tools.ant.Task`, `BuildException`, and `FileSet`.
- Security APIs integrate with Hadoop core types: `Configuration`, `Configurable`, `Text`, `Writable`, filesystem permission exceptions, `UserGroupInformation`, `SaslRpcServer.AuthMethod`, `KerberosInfo`, `TokenInfo`, `TokenIdentifier`, and IPC exceptions such as `StandbyException` and `RetriableException`.
- Kerberos and authentication dependencies include JAAS `Subject`, `KerberosTicket`, principal/keytab/ticket-cache concepts, and privileged action execution through generic `doAs` methods.
- Credential-provider APIs are consumed by configuration and applications that need secret material without embedding cleartext values directly.
- Authorization packages integrate with proxy-user configuration naming conventions, group mappings, remote client addresses, and service ACL checks.
- HTTP filters integrate with the servlet API (`Filter`, `FilterConfig`, `FilterChain`, `ServletRequest`, `ServletResponse`, `ServletException`) and Hadoop `Configuration` prefix extraction.
- Token APIs integrate with secret-key/HMAC primitives (`javax.crypto.SecretKey`), Hadoop token renewer discovery, RPC service naming, URL encoding, and HTTP authentication via `AuthenticatedURL`, `ConnectionConfigurator`, `AuthenticationException`, `DelegationTokenAuthenticator`, and Kerberos delegation-token authenticators.

## Risks and Edge Cases

- This XML chunk begins and ends in the middle of larger API declarations. Merge tooling must combine adjacent chunks before making final per-file claims about the complete `RecordOutput` and `DelegationTokenAuthenticatedURL` surfaces.
- The record I/O packages are deprecated but still public. Removing or changing signatures can break old generated records or downstream projects even though Avro is the replacement.
- Variable-length integer encoding in `org.apache.hadoop.record.Utils` is wire-format sensitive. Any compatibility change in sign handling, byte order, or size calculation would corrupt stored or transferred data.
- The record compiler parser classes are generated and mutable. Manual edits to generated code or token constants can break DDL parsing in ways that only appear for specific grammar paths.
- `RecordTypeInfo` and metadata `TypeID` equality/hash behavior influence schema comparison and skipping logic; subtle mismatches can cause incorrect compatibility decisions for nested records, maps, or vectors.
- `Credentials` mixes public token identifiers and secret key material. Serialization, string rendering, merge semantics, and token-file handling need tests that prevent accidental leakage or data loss.
- `UserGroupInformation` has process-global configuration and login-user state. Tests that mutate static state, keytab relogin behavior, immediate-renewal flags, or metrics attachment can be order-dependent if cleanup is incomplete.
- Kerberos principal substitution and token service construction depend on hostnames and network addresses. Canonicalization, unresolved hosts, and `_HOST` substitution are common compatibility risks.
- Proxy-user authorization depends on configuration key construction and remote-address matching. Incorrect prefix handling, wildcard ACL parsing, or group cache behavior can create privilege-escalation or false-denial bugs.
- HTTP CSRF and X-Frame filters sit in front of service endpoints. Bad defaults, case-sensitive header handling, browser user-agent classification errors, or incorrectly ignored methods can either break legitimate clients or weaken protections.
- Token lifecycle APIs cross client/server boundaries. Incorrect renewer selection, private-token service semantics, URL-safe encoding/decoding, or cancellation authentication assumptions can lead to leaked, non-renewable, or uncancellable tokens.
- `DelegationTokenAuthenticatedURL` explicitly supports query-string token transmission for backwards compatibility. That path has higher exposure risk than header transmission because URLs are commonly logged.

## Test Signals

- API compatibility tests should verify that every public class, interface, constructor, method, field, checked exception, inheritance edge, and deprecation flag in this chunk remains stable unless an intentional compatibility change is recorded.
- Record I/O tests should round-trip primitives, strings, buffers, records, vectors, maps, XML format boundaries, and variable-length positive/negative integer encodings across old generated code.
- Record compiler tests should parse DDL files with includes, modules, records, primitive fields, strings, buffers, vectors, maps, comments, and syntax errors, and should validate generated code through both direct `Rcc.driver()` and Ant `RccTask.execute()` paths.
- Metadata tests should serialize and deserialize `RecordTypeInfo`, compare nested structs/maps/vectors, and exercise `meta.Utils.skip()` for each supported `TypeID`.
- Credentials tests should cover token/secret-key add, overwrite, remove, merge versus add-all semantics, token storage file/stream read-write, and secure string/log behavior.
- UGI/Kerberos tests should cover simple and Kerberos security modes, keytab login/relogin/logout, ticket-cache login, proxy user creation, real/effective authentication methods, token attachment, credential copying, and `doAs` exception propagation.
- `SecurityUtil` tests should cover `_HOST` principal substitution, host extraction, token service build/decode, protocol annotation lookup, privileged-port detection, and unavailable-login failure handling.
- Authorization tests should cover wildcard ACLs, explicit user/group ACLs, serialization, proxy-user config key construction, group/host allowlists, denied users, and remote-address mismatch behavior.
- HTTP filter tests should use mock servlet requests to verify CSRF browser detection, custom-header enforcement, ignored method configuration, X-Frame-Options header injection, and Hadoop-configuration parameter extraction.
- Token tests should cover secret generation, password creation/retrieval failure paths, identifier decode, URL-safe encode/decode, private clone behavior, renewer dispatch, managed versus unmanaged renew/cancel, tracking IDs, and delegation-token HTTP operations with and without `doAs`.

### subset-b-007143: lines 36777-40847

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 36777-40847

Chunk id: `subset-b-007143`
Source: `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml`
Line range: 36777-40847

## Purpose

This chunk is the final public API slice of Hadoop Common 2.10.0's generated JDiff XML. It crosses several packages: web delegation-token authentication, the `org.apache.hadoop.service` lifecycle framework, launchable-service exit contracts, tracing administration RPC metadata, common utility APIs, and the `org.apache.hadoop.util.bloom` filter family. The XML records public/protected API shape, inheritance, method signatures, checked exceptions, deprecation text, and Javadoc, not implementation bodies.

The central themes are reusable infrastructure APIs: HTTP delegation-token acquisition/renewal/cancelation; consistent service state transitions and listener notifications; process-launch error mapping; isolated class loading; checksum, reflection, shell, shutdown, system-info, generic CLI, and version helpers; and serializable Bloom-filter data structures. These APIs are consumed throughout Hadoop daemons, command-line tools, IPC protocols, and clients.

## Important APIs, Types, and Functions

- `DelegationTokenAuthenticatedURL.Token` extends `AuthenticatedURL.Token` and adds `getDelegationToken()` / `setDelegationToken(Token)` for carrying a Hadoop delegation token alongside the HTTP authentication cookie/token.
- `DelegationTokenAuthenticator` implements `Authenticator` and wraps another authenticator with delegation-token operations: `authenticate(URL, AuthenticatedURL.Token)`, `getDelegationToken(...)`, `renewDelegationToken(...)`, and `cancelDelegationToken(...)`. Overloads support a `doAsUser` proxy user.
- `KerberosDelegationTokenAuthenticator` and `PseudoDelegationTokenAuthenticator` specialize `DelegationTokenAuthenticator` for SPNEGO with pseudo-auth fallback and simple/pseudo authentication based on `UserGroupInformation#getCurrentUser()`.
- Delegation token constants include `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `DELEGATION_PARAM`, `TOKEN_PARAM`, `RENEWER_PARAM`, `SERVICE_PARAM`, `DELEGATION_TOKEN_JSON`, `DELEGATION_TOKEN_URL_STRING_JSON`, and `RENEW_DELEGATION_TOKEN_JSON`, defining the HTTP query/header/JSON protocol vocabulary.
- `Service` is the lifecycle interface. It extends `Closeable` and defines `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration, state/config/name/start-time accessors, failure accessors, `waitForServiceToStop(long)`, lifecycle history, and blocker reporting.
- `AbstractService` is the base implementation for `Service`. It exposes final or protected lifecycle scaffolding around `serviceInit(Configuration)`, `serviceStart()`, and `serviceStop()`, plus `noteFailure(Exception)`, global listeners, lifecycle history, blocker mutation, and failure-state capture.
- `CompositeService` extends `AbstractService` to manage child services with `addService(Service)`, `addIfService(Object)`, `removeService(Service)`, `getServices()`, and lifecycle methods that cascade to children.
- `LifecycleEvent` is a serializable state-transition record with public `time` and `state` fields.
- `LoggingStateChangeListener` implements `ServiceStateChangeListener` and logs state changes through either a supplied SLF4J logger or the class logger.
- `ServiceOperations` provides static cleanup helpers: `stop(Service)` and `stopQuietly(...)` overloads for no-op/null-tolerant shutdown with Commons Logging or SLF4J warning paths.
- `ServiceStateException` is a `RuntimeException` and `ExitCodeProvider` with constructors that derive or override launcher exit codes and static `convert(...)` helpers for wrapping arbitrary `Throwable`s.
- `ServiceStateModel` tracks valid service state transitions with `enterState(STATE)`, `checkStateTransition(...)`, `isValidStateTransition(...)`, `ensureCurrentState(...)`, and `isInState(...)`.
- `LaunchableService` extends `Service` for command-line launched services. `bindArgs(Configuration, List)` can rewrite configuration before init, and `execute()` returns the launched process exit code after start.
- `AbstractLaunchableService` gives default launchable behavior: debug-log arguments, return the provided configuration, and treat `execute()` as success.
- `HadoopUncaughtExceptionHandler` is a JVM default uncaught-exception handler. Its public contract distinguishes standard exceptions from `Error`s, with `Error` causing process shutdown/exit instead of attempting clean recovery.
- `LauncherExitCodes` defines shared integer exit codes for success, generic failure, interrupted execution, argument/config/auth/connectivity problems, service-side failures, unsupported versions, service creation, and lifecycle exceptions.
- `ServiceLaunchException` extends `ExitUtil.ExitException`, implements `ExitCodeProvider` and `LauncherExitCodes`, and supports explicit, cause-based, and formatted exception construction.
- `SpanReceiverInfo`, `SpanReceiverInfoBuilder`, `TraceAdminProtocol`, and `TraceAdminProtocolPB` define tracing administration metadata and RPC contracts for listing, adding, and removing span receivers.
- `ApplicationClassLoader` extends `URLClassLoader` and implements application-first loading except for configured system classes. Constructors accept URL arrays or classpath strings, and `isSystemClass(String, List)` applies positive/negative class/resource patterns.
- `IPList` is a membership predicate for IP address allow/deny style checks.
- `Progressable` is the framework callback for long-running operations to signal liveness and avoid timeouts.
- `PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum` with pure-Java CRC32 and CRC32C algorithms, exposing `update(...)`, `reset()`, and `getValue()`.
- `ReflectionUtils` provides configuration injection, reflective construction, thread dump logging/printing, Writable copy/clone helpers, and inherited-field/method enumeration.
- `Shell` is an abstract command execution base with OS-specific command builders, Hadoop home/bin resolution, winutils resolution, environment and working-directory setters, throttled `run()`, abstract `getExecString()` / `parseExecResult(BufferedReader)`, process/exit/timeout inspection, static `execCommand(...)` helpers, global shell-process destruction, and memory-lock limit parsing.
- `ShutdownHookManager` is a priority-ordered singleton manager for JVM shutdown hooks, including optional per-hook timeout and default timeout integration with Hadoop common configuration.
- `StringInterner` provides strong and weak string interning and in-place array interning.
- `SysInfo` is an abstract host resource metrics provider with factory `newInstance()` and methods for memory, processor/core count, CPU frequency/time/usage, vcores, network bytes, and storage bytes.
- `Tool` and `ToolRunner` define Hadoop's generic command-line tool contract. `Tool` extends `Configurable`; `ToolRunner` parses generic Hadoop options into a `Configuration`, injects it into the `Tool`, runs custom arguments, prints generic usage, and supports interactive yes/no confirmation.
- `VersionInfo` exposes build metadata: version, revision, branch, date, user, URL, source checksum, build version, protoc version, and `main(String[])`.
- `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, and `RetouchedBloomFilter` expose probabilistic set-membership filters. All have serialization constructors and `write(DataOutput)` / `readFields(DataInput)`. Common operations include `add(Key)`, `membershipTest(Key)`, boolean filter operations `and`, `or`, `xor`, `not`, and `toString()`.
- `CountingBloomFilter` adds `delete(Key)` and `approximateCount(Key)`.
- `DynamicBloomFilter` adds a constructor parameter `nr`, the threshold for maximum keys per dynamic row.
- `HashFunction` maps a `Key` to multiple integer positions with configured maximum value, number of hash functions, and hash type.
- `RemoveScheme` defines retouched Bloom-filter clearing constants: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` adds false-positive registration overloads for a single `Key`, `Collection`, `List`, and `Key[]`, plus `selectiveClearing(Key, short)`.

## Control Flow

The delegation-token web flow is represented as an authenticated HTTP sequence. A `DelegationTokenAuthenticatedURL.Token` can hold both normal HTTP authentication state and a Hadoop delegation token. `DelegationTokenAuthenticator.authenticate()` authenticates a URL using the configured authenticator. `getDelegationToken()` and `renewDelegationToken()` require normal authentication and talk to HTTP/S endpoints using the delegation-token operation parameters and JSON fields. `cancelDelegationToken()` explicitly does not require authentication by the configured authenticator, so the token itself and endpoint authorization are the effective control inputs. The Kerberos authenticator can fall back to pseudo authentication when a server does not trigger SPNEGO.

The service lifecycle flow is the public contract for daemon components. A `Service` starts in `NOTINITED`, moves through `init(Configuration)` to `INITED`, then through `start()` to `STARTED`, and eventually through `stop()`/`close()` to `STOPPED`. `AbstractService` wraps these transitions, records lifecycle events, calls implementation hooks exactly once, notifies listeners, captures the first failure, and exposes `waitForServiceToStop(long)` for coordination. `ServiceStateModel` enforces valid transitions, and `ServiceStateException` converts failures into runtime exceptions with launcher-compatible exit codes. `CompositeService` adds parent/child orchestration by initializing, starting, and stopping managed child services around the parent lifecycle.

Launchable services add a command-line control path. A service launcher calls `bindArgs(Configuration, List)` before `init`, so a service can replace or augment configuration after launcher-specific arguments have been stripped. After `start()`, the launcher calls `execute()` and uses its return value as the process exit code. Exceptions from `execute()` are classified: explicit `ExitUtil.ExitException`s propagate, `ExitCodeProvider` exceptions become `ServiceLaunchException`s with their code, and other exceptions become `EXIT_EXCEPTION_THROWN`.

The tracing protocol flow is administrative RPC: clients list currently active span receivers, add a receiver from a `SpanReceiverInfo` built by `SpanReceiverInfoBuilder`, or remove a receiver by ID. The PB interface binds this API to the generated blocking protobuf service and Hadoop `VersionedProtocol`.

Utility APIs provide several independent flows. `ApplicationClassLoader` attempts application class/resource loading before parent delegation unless `isSystemClass()` says a class/resource belongs to JDK, Hadoop, or configured system namespaces. `ReflectionUtils.newInstance()` creates objects and injects `Configuration` when appropriate, while `copy()` / `cloneWritableInto()` use Writable serialization as the copy path. `Shell.run()` gates actual process execution by the configured minimum interval, builds the command via `getExecString()`, captures/feeds output to `parseExecResult()`, tracks process/exit/timeout state, and supports static one-shot command execution. `ShutdownHookManager` registers one JVM hook and then runs registered hooks in descending priority with configured timeout handling.

The generic CLI flow is `ToolRunner.run(conf, tool, args)`: parse generic Hadoop options, update the configuration, set it into the `Tool`, then invoke `Tool.run(String[])` with application-specific arguments. `ToolRunner.run(tool, args)` reuses the tool's existing configuration. `confirmPrompt()` is the interactive branch for user confirmation.

Bloom-filter flow is probabilistic and serializable. Construction fixes vector size, hash count, and hash implementation. `HashFunction.hash(Key)` maps each key to several vector positions. `add(Key)` mutates the underlying vector/matrix/counter structure, `membershipTest(Key)` checks all derived positions, boolean operations combine compatible filters, and `write`/`readFields` persist/restore filter state. `CountingBloomFilter.delete()` decrements counters and `approximateCount()` reports the minimum/derived count for a key. `DynamicBloomFilter.add()` targets an active row until the `nr` threshold is reached, then grows by adding a row. `RetouchedBloomFilter` collects known false positives and `selectiveClearing()` clears selected bits according to the chosen `RemoveScheme`.

## State and Persistence Behavior

- This source is generated API XML; it records public contracts, not private fields or storage layouts. State behavior below is inferred from signatures and Javadoc in this chunk.
- Delegation token state is stored client-side in `DelegationTokenAuthenticatedURL.Token` and server-side through HTTP/S delegation-token endpoints. Operation names, token values, renewers, services, and JSON fields are serialized through query parameters, headers, and JSON responses.
- `AuthenticatedURL` instances are documented as not thread-safe, and the delegation-token URL subclass inherits that constraint.
- `AbstractService` maintains service name, configuration, current state, start time, lifecycle history, failure cause, failure state, listeners, global listeners, and blocker map. Some getters are synchronized in the API (`getFailureCause`, `getFailureState`, `getLifecycleHistory`), while lifecycle hooks are documented as protected from re-entrancy by the wrapper methods.
- `LifecycleEvent` is explicitly `Serializable` and stores local transition time plus entered state, making lifecycle history snapshot-friendly.
- `CompositeService` owns an in-memory list of child `Service`s. `getServices()` returns a cloned snapshot so concurrent additions are not observed by that call.
- `ServiceStateModel.enterState()` is synchronized and returns the original state, making it the visible state-transition mutation point in the public API.
- `LauncherExitCodes` and `ServiceLaunchException` define process-exit state rather than persisted state; the exception carries an exit code used by launchers.
- `SpanReceiverInfoBuilder` accumulates receiver class name and configuration key/value pairs before producing an immutable-ish `SpanReceiverInfo` for RPC transport.
- `ApplicationClassLoader` persists classpath and system-class pattern configuration in memory for the lifetime of the loader.
- `Shell` stores process execution state: timeout interval, parent-environment inheritance flag, environment map, working directory, current `Process`, exit code, waiting thread, timeout flag, and a static set of live shell instances available through `getAllShells()` / `destroyAllShellProcesses()`.
- `Shell` resolves Hadoop home and qualified binary paths from system property `hadoop.home.dir`, `HADOOP_HOME`, platform-specific bin paths, and `winutils`; callers are warned to cache qualified binary results because path existence is checked.
- `ShutdownHookManager` is a singleton in-memory registry of `Runnable` hooks with priority and optional timeout. Hook execution order is deterministic by priority, but hooks with the same priority are non-deterministic.
- `StringInterner.strongIntern()` deliberately retains a strong reference; `weakIntern()` uses weak/interner behavior that avoids preventing GC.
- `VersionInfo` exposes build-time metadata, likely loaded from component-specific build properties through the protected constructor's component argument.
- Bloom filters persist their probabilistic vector/counter/matrix state through `DataOutput` and `DataInput`. Default constructors are explicitly for `readFields()`. Counting filters store small counters, dynamic filters store multiple Bloom rows and occupancy thresholds, and retouched filters store base Bloom data plus false-positive clearing metadata as implemented by the concrete class.

## Dependencies and Integration Points

- Security/authentication: `AuthenticatedURL`, `AuthenticatedURL.Token`, `Authenticator`, `ConnectionConfigurator`, `AuthenticationException`, `UserGroupInformation`, and `org.apache.hadoop.security.token.Token`.
- HTTP delegation-token protocol: HTTP/S URLs, query parameters, headers, JSON response names, renewer/service fields, and optional `doAsUser` proxy-user semantics.
- Configuration and lifecycle: `org.apache.hadoop.conf.Configuration`, service state enum `Service.STATE`, `Closeable`, listeners, SLF4J, Commons Logging, and Hadoop `ExitCodeProvider` / `ExitUtil`.
- Launching: daemon main methods, service launchers, JVM uncaught exception handling, process exit codes, command-line argument lists, and shutdown policy.
- Tracing and IPC: span receiver metadata, Hadoop tracing protobuf service `TraceAdminPB.TraceAdminService.BlockingInterface`, `VersionedProtocol`, and `IOException` for RPC failures.
- Class loading: `URLClassLoader`, classpath strings, `MalformedURLException`, parent classloader delegation, and system class pattern configuration.
- OS and process utilities: Java `Process`, command arrays, environment maps, working directories, Unix command names, Windows `winutils`, command-line length limits, script extension selection, `kill -0`/signal equivalents, `bash` detection, and memory-lock/ulimit parsing.
- Checksums and serialization: `java.util.zip.Checksum`, byte-array update APIs, Hadoop `Writable`, `DataInput`, `DataOutput`, and in-memory serialization buffers.
- Diagnostics: thread dumps through `ThreadMXBean`-style mechanisms behind `ReflectionUtils`, loggers, and throttled stack logging intervals.
- Resource monitoring: OS-specific `SysInfo` implementations for memory, CPU, network, and storage counters.
- Generic command-line tools: `Configurable`, `GenericOptionsParser`, Hadoop common generic options, `PrintStream`, and interactive stdin responses.
- Bloom filters: `org.apache.hadoop.util.bloom.Key`, `Filter`, `BloomFilter`, `HashFunction`, `org.apache.hadoop.util.hash.Hash`, and probabilistic filter theory referenced by the public docs.

## Risks and Edge Cases

- Because this is JDiff XML, it cannot show private synchronization, validation, serialization format details, or actual exception paths. Final whole-file research should treat implementation details as unresolved unless covered in source `.java` chunks.
- `AuthenticatedURL` instances are explicitly not thread-safe. Reusing a `DelegationTokenAuthenticatedURL` or its token across threads can corrupt or expose authentication state.
- Delegation token cancelation is documented as not requiring configured authenticator authentication. Endpoint authorization and token secrecy are therefore critical, especially with `doAsUser`.
- Proxy-user overloads (`doAsUser`) can create security regressions if endpoint implementations fail to enforce proxy-user ACLs consistently for get, renew, and cancel.
- Pseudo delegation-token authentication trusts the current user value, so deployment context and transport security determine whether this is acceptable.
- Service listener callbacks are invoked after state change but while the service is in a synchronized section. The docs warn that long-lived listener work delays transitions and listener-created threads calling back into the service can deadlock.
- `Service.stop()` is required to work from partially initialized states. Implementations that assume all fields are initialized can fail during cleanup after `init()` or `start()` failures.
- `ServiceOperations.stop(Service)` is explicitly not thread-safe because it checks state before the operation starts.
- Lifecycle failure state captures the first failure. Later failures during stop may be logged but can be hidden from callers using only `getFailureCause()`.
- `CompositeService` shutdown policy can stop all children or only started children. Child services with fragile `stop()` implementations may behave differently depending on `STOP_ONLY_STARTED_SERVICES`.
- `HadoopUncaughtExceptionHandler` exits on `Error`, reflecting that the process may be unsafe. Tests must avoid masking `Error` paths as recoverable.
- `LauncherExitCodes` deliberately compress HTTP-like error categories into one-byte-ish command exit codes. Callers should not confuse them with actual HTTP status codes.
- `ApplicationClassLoader.isSystemClass()` depends on positive and negative pattern matching. A bad pattern can leak classes into the parent loader or shadow Hadoop/JDK classes, producing linkage conflicts.
- `ReflectionUtils.copy()` destroys/reuses `dst` through serialization. Mutable Writables with transient fields or incompatible serialization versions can lose state.
- `ReflectionUtils` field/method enumeration across superclasses can surface private or synthetic members depending on implementation details; callers need filtering.
- `Shell.checkWindowsCommandLineLength()` expects command parts already include delimiters; callers that omit delimiter lengths may undercount.
- `Shell.WINUTILS` is deprecated because it can be null. Callers should use exception-raising getters to avoid latent null handling bugs.
- `Shell.destroyAllShellProcesses()` is global to all tracked shell instances and can interfere with unrelated in-flight shell commands in the same JVM.
- `Shell` command builders expose OS-specific behavior for groups, permissions, symlinks, signals, and environment-variable syntax; tests must not assume Unix semantics on Windows.
- `ShutdownHookManager` hooks with equal priority run in non-deterministic order. Hook code must not depend on ordering unless priorities differ.
- Shutdown hook timeouts can terminate hooks before cleanup is complete; hooks need idempotent recovery on the next process start.
- `StringInterner.strongIntern()` can retain unbounded distinct values for the life of the JVM.
- `SysInfo.newInstance()` can throw `UnsupportedOperationException` when OS detection fails; resource-monitoring callers need fallback behavior.
- `ToolRunner.confirmPrompt()` parses only yes/y case-insensitively per docs; automation should avoid relying on locale-specific or default-yes behavior.
- Bloom filters intentionally permit false positives. Counting Bloom filters warn that inserting the same key more than 15 times can overflow buckets and materially increase error rate.
- Counting Bloom filter deletes can underflow after deleting keys that were not actually present or after hash collisions, and `approximateCount()` may become lower than the real count with false-negative probability.
- Retouched Bloom filters remove selected false positives at the cost of introducing false negatives, changing the usual Bloom filter no-false-negative guarantee.
- Dynamic Bloom filter growth depends on the `nr` row threshold. Bad sizing can increase memory use or false-positive behavior across rows.

## Test Signals

- Delegation-token tests should cover SPNEGO success, pseudo fallback, unsupported non-HTTP/S URLs, get/renew/cancel with and without `doAsUser`, renewal return time parsing, token storage in `DelegationTokenAuthenticatedURL.Token`, unauthenticated cancel behavior, and `ConnectionConfigurator` propagation.
- Authentication concurrency tests should verify that callers do not share non-thread-safe `AuthenticatedURL` instances across threads or that wrapper code serializes access.
- Service lifecycle tests should cover legal transitions, illegal transition exceptions, null configuration rejection, hook invocation exactly once, failure capture during `serviceInit`/`serviceStart`, stop after partial init, idempotent stop, `close()` delegating to `stop()`, lifecycle history snapshots, blocker add/remove/snapshot behavior, and `waitForServiceToStop(0)` semantics.
- Listener tests should cover local and global listeners, duplicate registration no-op behavior, unregister return values, listener callback order assumptions, and deadlock avoidance when listeners call service APIs.
- Composite service tests should validate child init/start/stop order, failure cleanup, `addIfService()` for non-service objects, `getServices()` snapshot behavior, and `STOP_ONLY_STARTED_SERVICES` policy differences.
- Service exception tests should cover exit-code derivation from nested `ExitCodeProvider`, explicit exit-code constructors, `convert(Throwable)`, and `convert(String, Throwable)` preserving runtime exceptions.
- Launcher tests should cover `bindArgs()` replacing configuration, `execute()` return-code propagation, wrapping of `ExitUtil.ExitException`, `ExitCodeProvider`, and generic exceptions into `ServiceLaunchException`, and uncaught-handler behavior for `Exception` versus `Error`.
- Trace admin tests should cover adding receivers with configuration pairs, listing receiver IDs/classes, removing missing and existing IDs, `IOException` propagation, and PB protocol version compatibility.
- Application classloader tests should cover application-first class loading, resource lookup, positive/negative system-class patterns, parent fallback, malformed classpath strings, and default system classes for Hadoop/JDK resources.
- CRC tests should compare `PureJavaCrc32` with `java.util.zip.CRC32`, compare `PureJavaCrc32C` with known CRC32C vectors, test byte-by-byte versus array updates, reset behavior, offset/length bounds, and many-small-update performance assumptions.
- Reflection tests should cover `Configurable` injection, constructor caching if implemented, Writable copy of mutable objects, thread info logging throttling, inherited fields/methods inclusion, and behavior with abstract classes or inaccessible constructors.
- Shell tests should cover every OS command builder on supported platforms, Windows command length counting, Hadoop home resolution from system property and environment, missing `winutils`, script extension/run command selection, interval-throttled reruns, timeout marking, process destruction, environment/working-directory injection, and global `destroyAllShellProcesses()` isolation.
- Shutdown hook tests should cover priority ordering, same-priority non-determinism tolerance, timeout minimum/defaults, removal/has checks, clear behavior, and `isShutdownInProgress()` during hook execution.
- String interner tests should cover null or empty strings if allowed by implementation, object identity after strong/weak interning, in-place array mutation, and memory retention expectations for high-cardinality input.
- SysInfo tests should cover OS factory selection, unsupported OS failure, unavailable metrics returning documented sentinel values, monotonic cumulative CPU time, and network/storage counter aggregation.
- ToolRunner tests should cover generic option parsing into `Configuration`, preserving application-specific args, null configuration handling, `printGenericCommandUsage()`, exit-code propagation from `Tool.run`, and prompt parsing for yes/no variants.
- VersionInfo tests should cover each static getter, missing build-property fallback behavior, build-version string composition, protoc version reporting, and `main()` output stability.
- Bloom filter tests should cover add/membership, expected false-positive rate bounds, boolean operations with compatible and incompatible filters, serialization round trips, `getVectorSize()`, counting add/delete/approximate count including overflow/underflow scenarios, dynamic row growth at the `nr` threshold, `HashFunction` range bounds and hash count, retouched false-positive registration overloads, each `RemoveScheme`, and selective clearing's introduction of false negatives.

## Cross-Chunk Notes

This chunk begins inside the tail of `DelegationTokenAuthenticatedURL` documentation from the preceding lines and then covers the nested token class and following packages through the end of the JDiff API document. Whole-file synthesis should connect the partial delegation-token URL methods from the previous chunk with the authenticator/token contracts here. It should also treat all implementation internals as external to this XML unless corroborated by corresponding Hadoop Java source research.
