# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.22.0.xml lines 1-5845

## Scope and artifact role

This chunk is the opening segment of a generated JDiff API description for `hadoop-core 0.22.0`, produced by the JDiff Javadoc doclet on 2011-12-04. It is XML metadata, not executable Hadoop implementation. The file records public/protected API contracts, signatures, visibility, deprecation text, checked exceptions, and embedded Javadoc for Hadoop Common classes. This chunk covers:

- the `<api>` root and generation command line/classpath metadata;
- `org.apache.hadoop.HadoopIllegalArgumentException`;
- API classification annotations under `org.apache.hadoop.classification`;
- `org.apache.hadoop.conf` configuration contracts;
- the first large portion of `org.apache.hadoop.fs`, from `AbstractFileSystem` through the beginning of `FileSystem.exists`.

The primary purpose is compatibility comparison between Hadoop releases. Consumers such as JDiff compare this XML against another API snapshot, so method names, parameter types/order, deprecation strings, and class/interface boundaries are the persistent state that matters.

## Important APIs and types

### API metadata

The root `<api>` element names the snapshot `hadoop-core 0.22.0` with JDiff version `1.0.9`. The generation comment records use of `org.apache.hadoop.classification.tools.ExcludePrivateAnnotationsJDiffDoclet`, a Hadoop build classpath, the source path under `common/src/java`, and the JDiff API directory. That establishes this file as a filtered public API snapshot rather than a raw source dump.

### `org.apache.hadoop`

`HadoopIllegalArgumentException` is a public subclass of `java.lang.IllegalArgumentException` with a string-message constructor. Its Javadoc says Hadoop uses it to distinguish argument validation failures thrown by Hadoop implementation from generic JDK `IllegalArgumentException`. Later APIs, such as `FileContext.setOwner`, refer to this type for invalid user/group values.

### `org.apache.hadoop.classification`

The chunk records public annotation container classes for API audience and stability:

- `InterfaceAudience` plus nested annotations `Public`, `LimitedPrivate`, and `Private`.
- `InterfaceStability` plus nested annotations `Stable`, `Evolving`, and `Unstable`.

These are dependency-light annotation contracts implementing `java.lang.annotation.Annotation`. They do not carry runtime control flow here, but they are integration signals for Hadoop's compatibility policy and for the custom doclet that filters or marks API surface.

### `org.apache.hadoop.conf`

`Configurable` is a public interface with `setConf(Configuration)` and `getConf()`. `Configured` implements it as a base class for objects carrying a `Configuration`.

`Configuration` is the central mutable configuration container. It implements `Iterable` and Hadoop `Writable`, exposing constructors for default loading, toggled default loading, and cloning another `Configuration`. Important API groups include:

- resource loading: `addDefaultResource`, `addResource(String|URL|Path|InputStream)`, and `reloadConfiguration`;
- key deprecation: static synchronized `addDeprecation` overloads that may throw `UnsupportedOperationException` if called after resources have loaded;
- property access: `get`, `getTrimmed`, `getRaw`, `set`, `setIfUnset`, typed `getInt/getLong/getFloat/getBoolean`, setters, enum and regex helpers, string-array/collection helpers, class loading and instance construction helpers;
- local path selection: `getLocalPath` and `getFile`, which choose one configured local directory by hashing a supplied path and may create the directory;
- resource lookup: `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader`;
- serialization and diagnostics: `writeXml(OutputStream|Writer)`, static `dumpConfiguration`, `readFields`, `write`, `main`, `iterator`, `size`, `clear`, `getValByRegex`, `getProps`;
- classloader and logging behavior: `getClassLoader`, `setClassLoader`, and synchronized `setQuietMode`.

`Configuration.IntegerRanges` models positive integer ranges such as `2-3,5,7-` with `isIncluded(int)` and `toString()`. `ConfServlet.BadFormatException` is a simple public nested exception type.

### `org.apache.hadoop.fs` early classes

`AbstractFileSystem` is a public abstract implementation-facing interface for filesystem providers, analogous to a VFS layer and normally reached by applications through `FileContext`. It defines URI validation and qualification, factory methods keyed by `fs.AbstractFileSystem.<scheme>.impl`, per-filesystem `statistics`, and abstract operations for create, mkdir, delete, open, replication, rename, permissions, ownership, timestamps, checksums, status, block locations, fs status, listing, and checksum verification. Many methods explicitly align with `FileContext` semantics but require paths to be fully qualified or scoped to the target filesystem.

`AvroFSInput` adapts `FSDataInputStream` or a `FileContext`/`Path` pair to Avro `SeekableInput`, exposing `length`, `read`, `seek`, `tell`, and `close`. This links Hadoop FS streams to Avro container readers.

`BlockLocation` is a `Writable` metadata object for file block placement. It stores hostnames, names (`host:port`), topology paths, offset, length, and corrupt flag, with constructors, getters/setters, `write`, `readFields`, and `toString`.

`ChecksumException` is an `IOException` carrying a position via `getPos()`.

`ChecksumFileSystem` is an abstract `FilterFileSystem` that wraps a raw filesystem and provides client-side checksum file creation and verification. It exposes checksum naming/length helpers, `setVerifyChecksum`, raw filesystem access, create/open/append/rename/delete/list/mkdir/copy/local-output hooks, and `reportChecksumFailure`.

`CommonConfigurationKeysPublic` is a constants holder for documented common configuration keys and defaults. This chunk includes keys for native library availability, network topology scripts, default filesystem name, disk-free interval, trash intervals, local block size, automatic close, file/FTP filesystem implementation keys, MapFile/Bloom/SequenceFile/TFile I/O settings, IPC connection/listen/TCP behavior, RPC socket factory and SOCKS server, hash type, group mapping, security authentication/authorization, and service user names. `IO_SORT_MB_KEY` and `IO_SORT_FACTOR_KEY` are marked deprecated because they moved to MapReduce per HADOOP-6801.

`ContentSummary` is a `Writable` for directory/file aggregate length, directory count, file count, quota, space consumed, and space quota. It provides output formatting via `getHeader(boolean)` and `toString(boolean)`.

`CreateFlag` is an enum contract for file creation semantics. Its Javadoc defines combinations of `CREATE`, `APPEND`, and `OVERWRITE`: overwrite dominates create/append, and create+append means create if absent or append if present.

`FileAlreadyExistsException` is a public `IOException` used when an existing target is not configured to be overwritten.

`FileChecksum` is an abstract `Writable` contract for algorithm name, length, and checksum bytes, with `equals` and `hashCode` based on algorithm and value.

### `FileContext` and nested helpers

`FileContext` is a final public application-facing filesystem namespace context. It has many `getFileContext` factories for default config, explicit `URI`, explicit `Configuration`, explicit `AbstractFileSystem`, and local filesystem contexts. It carries a default filesystem, working directory, and umask, and exposes operations including:

- path qualification and working-directory management;
- create, mkdir, delete, open, setReplication, rename, setPermission, setOwner, setTimes;
- checksum verification and `getFileChecksum`;
- status and link APIs: `getFileStatus`, `getFileLinkStatus`, `getLinkTarget`, `getFileBlockLocations`, `getFsStatus`;
- symlink creation and resolution;
- directory listing via `listStatus` and `listLocatedStatus`;
- `deleteOnExit`, `util`, and protected symlink resolution helpers.

The class-level Javadoc is a major contract description. It defines Hadoop paths as fully qualified URI names, slash-relative paths resolved against the default filesystem, or working-directory-relative names. It states that relative paths with a scheme are illegal. It also says `FileContext` models per-process filesystem state like default FS and umask, while server-side defaults supply home directory, initial working directory, replication, block size, buffer size, and bytes per checksum.

`FileContext.FSLinkResolver<T>` is a protected abstract helper for operations that may cross filesystems while resolving symlinks. Implementations override `next(AbstractFileSystem, Path)` and call `resolve(FileContext, Path)` to repeat the operation until symlinks are resolved.

`FileContext.Util` provides library methods over core `FileContext` operations: `exists`, `getContentSummary`, multiple filtered `listStatus` overloads, recursive/non-recursive `listFiles`, globbing with shell-like pattern syntax, and copy with delete-source/overwrite options. Its Javadoc warns these utilities are not atomic and may partially complete if concurrent namespace changes occur.

### `FileStatus`

`FileStatus` is a public `Writable` and `Comparable` client-side metadata object. It captures length, file/directory/symlink classification, replication, block size, modification/access times, permission, owner, group, path, and optional symlink target. It provides serialization, comparison, equality, and hashing. Equality and hash code are path-based. `isDir()` is deprecated in favor of explicit `isFile`, `isDirectory`, and `isSymlink`.

### `FileSystem` beginning

This chunk begins the classic abstract `FileSystem` API, extending `Configured` and implementing `Closeable`. Covered methods include:

- cached lookup and uncached construction: `get(URI, Configuration, String)`, `get(Configuration)`, `get(URI, Configuration)`, `newInstance(...)`, `newInstanceLocal`, `getLocal`, `closeAll`, and `closeAllForUGI`;
- default URI configuration: `getDefaultUri` and `setDefaultUri`;
- initialization and identity: `initialize`, abstract `getUri`, `getDefaultPort`, `getCanonicalServiceName`, deprecated `getName`, and deprecated `getNamed`;
- path and security integration: `makeQualified`, `checkPath`, and `getDelegationToken`;
- compatibility helpers for exact permissions: static `create(FileSystem, Path, FsPermission)` and `mkdirs(FileSystem, Path, FsPermission)` implemented as thread-safe but potentially multi-RPC operations;
- block location and server defaults;
- open/create overloads, protected `primitiveCreate`, protected `primitiveMkdir`, `createNewFile`, append overloads, deprecated `getReplication`, `setReplication`, abstract `rename`, transitional protected rename with options, deprecated one-arg delete, abstract two-arg delete, `deleteOnExit`, `processDeleteOnExit`, and the opening line of `exists`.

## Control flow and behavioral contracts

Because this is JDiff XML, direct control flow is not represented as code blocks. The control-flow-relevant contracts are in factory, delegation, and exception behavior:

- `Configuration` lazily loads ordered resources. Later resources override earlier ones unless final parameters block overrides. `reloadConfiguration` clears loaded resource state so later reads force reload, while values set programmatically overlay resource values.
- Deprecated configuration keys are resolved through replacement keys on reads and writes. Deprecation registration must occur before resources are loaded.
- `AbstractFileSystem.get` and `FileSystem.get` both perform scheme-driven implementation lookup through configuration keys, construct/initialize the selected filesystem, and may cache or return new instances depending on API (`get` versus `newInstance`).
- `FileContext` resolves user paths through working directory and default filesystem state before delegating to `AbstractFileSystem`. Operations may follow symlinks, and `FSLinkResolver` repeats provider-specific work across filesystems until link resolution completes.
- Create and mkdir operations apply umask at the `FileContext` layer before calling lower-level APIs that expect absolute permissions.
- Listing APIs expose iterator-based control flow where `hasNext()` or `next()` may surface runtime exceptions wrapping I/O failures if namespace changes occur during traversal.
- Rename behavior is explicitly filesystem-dependent for atomicity. Overwrite semantics allow replacing a file or empty directory but not a non-empty directory.
- `ChecksumFileSystem` delegates actual storage to a raw filesystem while adding sidecar checksum files, checksum verification on reads, and checksum cleanup/renaming/list filtering behavior.

## State and persistence behavior

The persistent state represented by this chunk is API signature state in XML. For Hadoop runtime contracts described by the API:

- `Configuration` persists logical key/value state in memory, can deserialize/serialize through Hadoop `Writable`, can emit XML/JSON-like diagnostic output, and derives values from XML resources such as `core-default.xml` and `core-site.xml`.
- `Configuration` resource ordering, final flags, deprecation maps, classloader, and quiet mode influence later reads and object construction.
- `FileContext` holds default filesystem, working directory, and umask as per-context state. `deleteOnExit` records paths for deletion on JVM shutdown or context cleanup.
- `FileSystem` has cached instances keyed by URI/config/user identity, supports global cache closure and UGI-scoped closure, and has delete-on-close state for paths marked through `deleteOnExit`.
- `FileStatus`, `BlockLocation`, `ContentSummary`, `FileChecksum`, and `Configuration` are `Writable` or expose Hadoop serialization-compatible contracts used in RPC, CLI display, or persisted metadata flows.
- Filesystem operations persist namespace and file changes: create, append, delete, rename, symlink, permission/owner/time updates, replication changes, checksum sidecars, and content copies.

## Dependencies and integration points

This chunk connects Hadoop Common to:

- Java core APIs: `URI`, `URL`, `InputStream`, `Reader`, `Writer`, `DataInput`, `DataOutput`, `IOException`, `FileNotFoundException`, `ClassLoader`, regex `Pattern`, collections, and annotations.
- Hadoop configuration and serialization: `Configuration`, `Configurable`, `Configured`, `Writable`.
- Hadoop filesystem primitives: `Path`, `FSDataInputStream`, `FSDataOutputStream`, `FileContext`, `FileSystem`, `AbstractFileSystem`, `PathFilter`, `RemoteIterator`, `FsStatus`, `FsServerDefaults`, `Options`, `CreateFlag`, and `FsPermission`.
- Hadoop security and RPC: `AccessControlException`, `UserGroupInformation`, delegation `Token`, and documented RPC client/server exception behavior.
- Avro: `org.apache.avro.file.SeekableInput` through `AvroFSInput`.
- Commons Logging: `FileContext.LOG`.
- Build and compatibility tooling: JDiff, Javadoc doclets, Hadoop classification annotations, and `core-default.xml` public configuration documentation.

## Risks and compatibility concerns

- The XML is generated and should not be manually edited except as a generated artifact replacement. Small signature changes in parameter order, checked exceptions, or deprecation strings alter compatibility comparisons.
- Several contracts are transitional or deprecated: `FileStatus.isDir`, `FileSystem.getName`, `FileSystem.getNamed`, `FileSystem.getReplication`, one-arg `FileSystem.delete`, and protected FileSystem rename/primitive mkdir APIs supporting migration from `FileSystem` to `FileContext`.
- `Configuration.addDeprecation` has ordering sensitivity: calling it after resources load can fail, so tests must cover startup initialization order.
- `Configuration` variable expansion can involve both Hadoop config properties and JVM system properties, creating risk of surprising substitution, recursion, or environment-sensitive values.
- `FileContext.Util` explicitly warns that helper operations are non-atomic and can partially complete during concurrent namespace mutation.
- Rename atomicity is left to filesystem implementations, so cross-filesystem or non-HDFS behavior can diverge.
- Symlink resolution may cross filesystems and supports multiple target forms. Invalid partial URIs, dangling links, and unresolved intermediate links are important edge cases.
- Checksum sidecar behavior in `ChecksumFileSystem` risks stale or hidden checksum files if rename/delete/list/copy behavior drifts from raw file behavior.
- `FileSystem` caching and `closeAll`/`closeAllForUGI` can cause lifecycle bugs if shared cached instances are closed while still in use.
- Constant classes expose public configuration names and defaults; deprecating or moving keys can break downstream code that compiled against public constants.

## Test signals

Useful validation for this chunk's APIs includes:

- JDiff/schema validation that the XML remains well-formed and compatible with `api.xsd`.
- API compatibility tests comparing this snapshot with adjacent Hadoop releases, especially around method signatures, visibility, exceptions, and deprecation text.
- `Configuration` tests for resource precedence, final parameters, default loading disabled/enabled, reload behavior, deprecation aliases, typed parsing fallback, variable expansion, `Writable` round trips, XML output, classloader use, and regex key lookup.
- Filesystem factory tests for scheme-to-implementation lookup, default URI handling, cached versus new instance behavior, UGI-specific instances, local filesystem construction, and unsupported filesystem errors.
- `FileContext` path tests for fully qualified, slash-relative, working-directory-relative, illegal relative-with-scheme paths, working directory changes, umask application, and server-side defaults.
- Operation tests for create/mkdir/delete/open/append/rename/setPermission/setOwner/setTimes/setReplication across local and HDFS-like filesystems, including documented checked exception cases.
- Symlink tests for fully qualified, partially qualified, relative, absolute, dangling, and cross-filesystem links, plus intermediate versus final component resolution.
- Metadata serialization tests for `BlockLocation`, `ContentSummary`, `FileStatus`, and `FileChecksum`, including equality/hash/compare behavior and deprecated compatibility methods.
- `ChecksumFileSystem` tests for checksum file naming, length calculation, read verification, checksum failure reporting, and hiding/renaming/deleting checksum sidecars with raw files.
- Concurrency and lifecycle tests for `FileContext.Util` partial completion behavior, iterator failure propagation during mutation, `deleteOnExit`, and global/UGI filesystem cache closing.

## Cross-chunk references

The chunk ends inside the `FileSystem` class at the opening of `exists(Path)`. Later chunks are needed for the remainder of `FileSystem` and subsequent `org.apache.hadoop.fs` types. Any merged per-file report should combine this chunk's early `FileSystem` factory/create/delete contracts with later listing, copy, permission, statistics, stream, and remaining Hadoop Common API contracts.
