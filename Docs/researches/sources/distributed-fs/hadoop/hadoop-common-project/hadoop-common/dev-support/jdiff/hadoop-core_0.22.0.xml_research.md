# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.22.0.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007253`: lines 1-5845, `Docs/researches/chunks/subset-b-007253_research.md`
- `subset-b-007254`: lines 5846-12015, `Docs/researches/chunks/subset-b-007254_research.md`
- `subset-b-007255`: lines 12016-18218, `Docs/researches/chunks/subset-b-007255_research.md`
- `subset-b-007256`: lines 18219-24654, `Docs/researches/chunks/subset-b-007256_research.md`
- `subset-b-007257`: lines 24655-28377, `Docs/researches/chunks/subset-b-007257_research.md`

## Chunk Research

### subset-b-007253: lines 1-5845

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

### subset-b-007254: lines 5846-12015

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.22.0.xml lines 5846-12015

## Chunk Scope

This chunk is a JDiff API snapshot for Hadoop core 0.22.0, not implementation source. It starts in the middle of `org.apache.hadoop.fs.FileSystem`, then covers the rest of the public filesystem API slice, filesystem implementations for local/FTP/KFS/S3/native S3, permission APIs, and the beginning of `org.apache.hadoop.io` writable/serialization utilities through `IOUtils.copyBytes`.

Because the file is generated API XML, the control-flow, state, and persistence notes below are inferred from exposed signatures, inheritance, documented contracts, checked exceptions, and class/package docs rather than method bodies.

## Purpose

The chunk documents the public compatibility surface for Hadoop's older `FileSystem` abstraction and early `Writable` serialization stack. It is useful for compatibility checks because it captures method names, overloads, visibility, abstract/static/synchronized attributes, deprecations, return types, parameters, thrown exceptions, nested classes, and package-level docs.

The filesystem section defines how Hadoop clients address paths, list and locate files, read/write streams, move data between local and remote stores, report capacity and block locations, manage permissions/ownership/timestamps, and expose concrete backends. The `io` section starts the data model used by Hadoop RPC, SequenceFile/MapFile, and MapReduce values: mutable `Writable` wrappers, byte-comparable values, arrays, compressed writables, and stringification helpers.

## Important APIs and Types

### `org.apache.hadoop.fs.FileSystem` tail

The chunk begins after earlier `FileSystem` methods and includes existence/status helpers, directory/file predicates, listing/globbing, working-directory APIs, mkdir/copy helpers, status and statistics, and permission metadata calls.

Important methods in this slice:

- `isDirectory(Path)`, `isFile(Path)`, `exists(Path)` and deprecated `getLength(Path)` expose convenience probes, with docs recommending callers reuse `FileStatus` from `getFileStatus()` or `listStatus()` where possible.
- `getContentSummary(Path)`, abstract `listStatus(Path)`, filtered/list-of-path overloads, and `globStatus(Path[, PathFilter])` define discovery behavior. Glob docs specify shell-like `?`, `*`, character classes, negation, escapes, and brace expansion, with sorted results and special null/empty distinctions depending on whether the pattern contains a glob.
- `listLocatedStatus(Path[, PathFilter])` and `listFiles(Path, boolean)` return `RemoteIterator`, combining statuses with block locations for files.
- Abstract `setWorkingDirectory(Path)` and `getWorkingDirectory()` define relative path resolution; protected `getInitialWorkingDirectory()` allows implementations such as local filesystems to expose a starting working directory.
- `mkdirs(Path[, FsPermission])`, local copy/move helpers, `startLocalOutput(Path, Path)`, and `completeLocalOutput(Path, Path)` define common file transfer behavior between local and target filesystems.
- `close()`, `getUsed()`, deprecated `getBlockSize(Path)`, `getDefaultBlockSize()`, `getDefaultReplication()`, and abstract `getFileStatus(Path)` define lifecycle and metadata.
- `getFileChecksum(Path)` defaults to `null` when no checksum algorithm exists; `setVerifyChecksum(boolean)` may be a no-op for filesystems without checksum support.
- `getStatus()`/`getStatus(Path)` return `FsStatus`; `setPermission`, `setOwner`, and `setTimes` expose mutable metadata.
- Static synchronized statistics registry methods include deprecated `getStatistics()` returning a map, `getAllStatistics()`, `getStatistics(String, Class)`, `clearStatistics()`, and `printStatistics()`.

Fields in this slice include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, public static `LOG`, and protected per-instance `statistics`.

### `FileSystem.Statistics`

`FileSystem.Statistics` is a public static final nested class keyed by a URI scheme. It tracks mutable counters for bytes read/written, read ops, large read ops, and write ops. Increment methods mutate counters; getters expose totals; `reset()` clears byte counts; `toString()` and `getScheme()` provide reporting. The class is a major test signal for IO accounting and a shared integration point for `FSDataOutputStream` constructors that accept statistics.

### File utilities and delegation

`FileUtil` is a static utility surface for converting `FileStatus[]` to `Path[]`, recursively deleting Java `File` trees, copying between `FileSystem` instances and local `File`s, merging a directory into one output file, constructing shell-safe local paths, computing simple local disk usage, unzipping/untarring archives, creating symlinks, invoking `chmod`, creating temp files near a base file, and replacing files. The `fullyDelete(File)` docs explicitly distinguish symlink-to-file, symlink-to-directory, normal file, and normal directory behavior. The deprecated `fullyDelete(FileSystem, Path)` points callers to `FileSystem.delete(Path, boolean)`.

`FileUtil.HardLink` exposes `createHardLink(File, File)` and `getLinkCount(File)`, integrating with native/local filesystem semantics.

`FilterFileSystem` wraps a protected `FileSystem fs` and delegates almost the entire `FileSystem` surface: initialization, URI/path qualification, block locations, open/create/append, replication, rename/delete/deleteOnExit, listing, working directory, status, mkdirs, local copy helpers, checksum controls, metadata, lifecycle, and protected primitive create/mkdir. It is an extension hook for wrappers that transform or augment another filesystem while preserving the same API contract.

### Core filesystem value/stream types

`FsConstants` exposes URI/scheme constants for local, FTP, and ViewFs.

`FSDataInputStream` wraps an input stream in a data stream with `Seekable`, `PositionedReadable`, and `Closeable`. It exposes `seek`, `getPos`, positional `read`, `readFully` overloads, and `seekToNewSource`, so tests need to cover both cursor-moving and position-preserving reads.

`FSDataOutputStream` wraps an output stream in a data stream and implements `Syncable`. Constructors can accept a `FileSystem.Statistics` and starting position. It exposes `getPos`, `close`, `getWrappedStream`, deprecated `sync`, `hflush`, and `hsync`. The flush/sync contract is split between visibility to new readers (`hflush`) and POSIX-like durability to disk devices (`hsync`).

`FSError` is an `Error` for unexpected local/native filesystem failures.

`FsServerDefaults` and `FsStatus` both implement `Writable`. `FsServerDefaults` persists defaults such as block size, checksum bytes, write packet size, replication, and file buffer size. `FsStatus` persists capacity/used/remaining byte counts.

`InvalidPathException`, `ParentNotDirectoryException`, and `UnsupportedFileSystemException` are public exception types for path validation, path hierarchy failures, and unsupported schemes.

`LocatedFileStatus` extends `FileStatus` with `BlockLocation[]` and preserves comparison/equality/hash semantics around the path name.

### Path and option APIs

`Options` is a final holder for file operation options. `Options.CreateOpts` supplies vararg option builders and helpers: block size, buffer size, replication factor, bytes per checksum, permissions, create-parent boolean, `getOpt`, and protected `setOpt`. Nested option value classes expose `getValue()`. `Options.Rename` is an enum-like type with `values()`, `valueOf(String)`, `valueOf(byte)`, and `value()` for rename semantics.

`Path` is the central URI/path abstraction, comparable and URI-backed. Constructors support parent/child combinations, strings, URI, and URI components. Methods expose filesystem lookup through `getFileSystem(Configuration)`, path absoluteness checks, name/parent/suffix, URI/string conversion, equality/hash/ordering, depth, and qualification against either a `FileSystem` or explicit default URI and working directory. Docs note ambiguity in `isAbsolute()` because it returns true even with scheme/authority present.

`PathFilter.accept(Path)` is the callback used by listing/globbing. `PositionedReadable`, `Seekable`, `RemoteIterator<E>`, and `Syncable` define remote-read, seek, remote-iteration, and flush/sync contracts used by streams and file listings.

### Filesystem implementations in this chunk

`LocalFileSystem` extends `ChecksumFileSystem`, exposes `getRaw()`, `pathToFile(Path)`, local copy overrides, and `reportChecksumFailure(...)`, which moves bad data/checksum files aside on the same device to avoid reuse.

`RawLocalFileSystem` extends `FileSystem` and implements local operations directly: URI/init, open, append, create with and without permissions, primitive create/mkdir, rename, delete, listStatus, mkdirs, working directory/home/status, local output movement, close, string representation, file status, owner, and permission. Docs mention using shell commands `chown` and `chmod` for metadata changes.

`Trash` is a configured service for moving paths into `.Trash/current`, checkpointing current trash, expunging older checkpoints, returning a superuser emptier `Runnable`, and running that emptier from `main`. Package docs explain the design: preserve original paths, avoid full trash enumeration, avoid filesystem date support, and avoid clock synchronization.

`FTPFileSystem` extends `FileSystem` and is backed by Apache Commons Net. It defines `initialize`, `open`, `create`, unsupported/optional `append`, `delete`, URI, listing/status, `mkdirs`, `rename`, working/home directories, and working-directory mutation. Constants include `DEFAULT_BUFFER_SIZE` and `DEFAULT_BLOCK_SIZE`; `FTPException` wraps FTP-specific failure messages/causes.

`KosmosFileSystem` extends `FileSystem` for KFS. It covers URI/init, working directory, mkdirs, directory/file predicates, list/status, append/create/open, rename/delete, default replication/block size, replication changes, lock/release, block locations, and local copy/output helpers. Package docs describe required `core-site.xml` keys such as `fs.kfs.impl`, `fs.default.name`, `fs.kfs.metaServerHost`, and `fs.kfs.metaServerPort`, plus JNI/native library deployment through `kfs-0.1.jar` and `libkfsClient.so`.

`S3FileSystem` is the older block-based S3 filesystem. It has constructors with and without a `FileSystemStore`, URI/init, working directory, mkdirs, file predicate, listing, unsupported append, create/open, rename/delete, status, and default block size. Package docs describe block metadata/inodes stored in S3, efficient seek by consulting inodes and HTTP Range reads, and rename implemented as delete-plus-put because S3 lacks native rename.

`NativeS3FileSystem` is the native-object S3 implementation. It has constructors with and without `NativeFileSystemStore`, init, unsupported append, create/delete/status/URI/list/mkdirs/open/rename/default block size, and working directory. Package docs contrast it with block-based S3: files are stored in native form for interoperability, and directories are inferred using markers such as `_$folder$`, slash objects, or object prefixes, with file-vs-directory masking rules.

### Permissions

`org.apache.hadoop.fs.permission.AccessControlException` is deprecated in favor of `org.apache.hadoop.security.AccessControlException`, but remains public with default, string, and throwable constructors to support remote exception unwrapping.

`FsPermission` implements `Writable` and models user/group/other `FsAction` values plus sticky bit. Constructors accept actions, actions plus sticky bit, a short mode, a copy, or octal/symbolic string. It exposes immutable creation, getters, `fromShort`, `write`, `readFields`, static `read(DataInput)`, `toShort`, equality/hash/string, `applyUMask`, `getUMask(Configuration)`, `setUMask`, `getDefault`, and `valueOf(String)`. Config fields include `DEPRECATED_UMASK_LABEL`, `UMASK_LABEL`, and `DEFAULT_UMASK`; docs describe octal, symbolic, and deprecated decimal umask compatibility.

### Hadoop IO APIs

`AbstractMapWritable` is an abstract `Writable`/`Configurable` base for map-like writables. It keeps per-instance class-id mappings rather than static mappings, with IDs from 1 to 127. It exposes synchronized `addToMap` and `copy`, protected `getClass(byte)`/`getId(Class)`, config accessors, and serialization.

`ArrayFile` extends `MapFile` as a dense integer-to-value file. `ArrayFile.Reader` supports seek by long index, sequential `next`, `key`, and random `get`. `ArrayFile.Writer` appends values and has constructors with compression/progress options.

`ArrayPrimitiveWritable` wraps primitive arrays without copying and writes an optimized wire format. It tracks declared and actual component type, exposes getters, `set(Object)`, `write`, and `readFields`. `ArrayWritable` wraps homogeneous `Writable[]` values and supports value-class introspection, `toStrings`, `toArray`, `set/get`, and serialization.

`BinaryComparable` is an abstract byte-oriented comparable with abstract `getLength()` and `getBytes()`, byte-array compare overloads, equality, and hash based on `WritableComparator`.

`BloomMapFile` extends `MapFile` behavior with a dynamic Bloom filter, constants `BLOOM_FILE_NAME` and `HASH_COUNT`, and static `delete`. `BloomMapFile.Reader` can quickly reject absent keys via `probablyHasKey`, then delegate to actual `MapFile.Reader.get`; false positives are expected. `BloomMapFile.Writer` has many constructor overloads for filesystem/path, key/value classes or comparators, compression codec/type, and progress callback; it updates the filter on `append` and persists it on `close`.

Primitive writable wrappers in this slice include `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, and `IntWritable`, each implementing `WritableComparable`, constructors with default/value, mutable `set`, `get`, `readFields`, `write`, equality/hash, `compareTo`, and `toString`. Their nested `Comparator` classes extend `WritableComparator` and compare serialized byte arrays directly.

`BytesWritable` extends `BinaryComparable` and implements `WritableComparable`. It exposes `copyBytes`, `getBytes`, deprecated `get`, `getLength`, deprecated `getSize`, `setSize`, `getCapacity`, `setCapacity`, `set(BytesWritable)`, `set(byte[], int, int)`, serialization, equality/hash, and string conversion. Docs warn that `getBytes()` returns backing storage valid only through `getLength()`, so callers needing exact length must use `copyBytes()`.

`CompressedWritable` lazily compresses/decompresses subclass state. Public `readFields` and `write` wrap compressed payload handling; protected `ensureInflated`, `readFieldsCompressed`, and `writeCompressed` are the subclass extension points.

`DefaultStringifier<T>` converts objects to and from strings using Hadoop serialization. It is `Closeable`, has `fromString`, `toString(T)`, and static configuration helpers `store`, `load`, `storeArray`, and `loadArray`, tying object persistence to `Configuration`.

`EnumSetWritable<E>` wraps `EnumSet`, implements `Writable` and `Configurable`, and extends `AbstractCollection`. It preserves element type even for null/empty sets when supplied, exposes `iterator`, `size`, `add`, `set`, `get`, serialization, equality/hash/string, `getElementType`, and config accessors.

`GenericWritable` is an abstract wrapper for a fixed set of `Writable` implementation types. Subclasses implement protected `getTypes()` to define allowed classes. It serializes a compact type index instead of writing class names per record, passes configuration into wrapped `Configurable` instances before deserialization, and exposes `set`, `get`, `readFields`, `write`, and config accessors.

`IOUtils` starts at the end of this chunk. The visible overloads of `copyBytes` copy `InputStream` to `OutputStream` with explicit buffer size and optional close behavior, with another overload taking `Configuration` for buffer sizing. The chunk ends before the class is complete.

## Control Flow and Behavioral Contracts

Most control flow in this chunk is contract-level:

- File discovery flows from `Path` to `FileSystem`, then through `getFileStatus`, `listStatus`, `globStatus`, or remote iterators. Filters are applied by `PathFilter.accept`.
- File reading flows through `FileSystem.open` into `FSDataInputStream`; callers can combine sequential reads with `Seekable` and `PositionedReadable` behavior. Implementations may switch replicas or sources through `seekToNewSource`.
- File writing flows through `FileSystem.create`/`append` into `FSDataOutputStream`, optional progress callbacks, statistics accounting, `hflush`/`hsync`, and close.
- Copy flows are split between `FileSystem` convenience methods and `FileUtil.copy`/`copyMerge`, crossing local `File` and remote `FileSystem` boundaries and optionally deleting source paths.
- Metadata mutation flows through `setPermission`, `setOwner`, `setTimes`, and implementation-specific adapters such as local `chmod`/`chown`.
- Delegation in `FilterFileSystem` forwards behavior to its wrapped `fs`, making it a central interception point for wrappers.
- Serialization flow for `Writable` classes is uniformly `write(DataOutput)` and `readFields(DataInput)`, with comparators reading serialized byte arrays directly for sort efficiency.
- `GenericWritable`, `AbstractMapWritable`, and `EnumSetWritable` add type metadata around `Writable` payloads so heterogeneous or collection-like values can round-trip through Hadoop's serialization layer.

## State and Persistence

Persistent state appears in several forms:

- Filesystem implementations persist data in backing stores: local disk, FTP servers, KFS, block-based S3 records, or native S3 objects.
- `FileSystem.Statistics` keeps mutable process-side counters grouped by URI scheme/class and is exposed through static synchronized registry methods.
- `FSDataInputStream`/`FSDataOutputStream` track current stream positions; output stream constructors can start with a known position.
- `FsStatus`, `FsServerDefaults`, `FsPermission`, primitive writables, array writables, enum set writables, compressed writables, and generic writables persist themselves through Hadoop's `Writable` binary protocol.
- `Trash` persists deleted paths under a per-user `.Trash/current` tree and creates checkpoint directories for later expunge.
- S3 block filesystem persists file structure as path-keyed inode metadata plus `block-*` objects; native S3 persists object data directly and uses marker/prefix conventions for directories.
- `DefaultStringifier.store/load` persists serialized objects or arrays into `Configuration` entries as strings.

## Dependencies and Integration Points

Key dependencies visible in signatures and docs:

- Java IO and networking: `java.io.File`, streams, `DataInput`, `DataOutput`, `IOException`, `URI`, and process/shell interactions for local utilities.
- Hadoop configuration/utilities: `Configuration`, `Configured`, `Tool`, `Progressable`, `Writable`, `WritableComparable`, `WritableComparator`, `MapFile`, `SequenceFile`, compression codecs, and Bloom filters.
- Filesystem metadata types from adjacent chunks: `Path`, `FileStatus`, `BlockLocation`, `ContentSummary`, `FileChecksum`, `FsPermission`, `FsAction`, and `RemoteIterator`.
- Apache Commons Logging via public `LOG` fields.
- Apache Commons Net for FTP support.
- KFS JNI/native library integration through KFS jars and `LD_LIBRARY_PATH`.
- Amazon S3 concepts, including HTTP Range reads, object keys, delete/put rename emulation, and directory marker conventions.

Integration is intentionally centered on `FileSystem`: every concrete backend implements the same open/create/delete/list/status/working-directory contract, letting Hadoop clients and MapReduce jobs remain mostly backend-neutral. The `Writable` classes integrate with SequenceFile, MapFile, sort comparators, RPC/configuration serialization, and MapReduce key/value handling.

## Risks and Edge Cases

- This is an API XML chunk, so it does not reveal implementation details such as synchronization around mutable counters, exact exception paths, buffer ownership, or cleanup failure handling.
- The chunk starts mid-`FileSystem` and ends mid-`IOUtils`; final per-file synthesis must reconcile with adjacent chunks for complete class summaries.
- `FileSystem` convenience methods like `isDirectory`, `isFile`, `getLength`, and `getBlockSize` are deprecated or discouraged in favor of `FileStatus`, so compatibility consumers should watch for legacy usage.
- Glob behavior has subtle null versus empty-array semantics depending on whether a pattern contains a glob.
- Recursive delete and `fullyDeleteContents` have symlink-specific behavior that can surprise callers, especially when a symlink points to a directory.
- Local filesystem metadata changes rely on shell commands (`chmod`, `chown`) and are platform-sensitive.
- `FilterFileSystem` subclasses can accidentally bypass wrapper behavior if they call the raw wrapped filesystem directly or fail to override newly added primitives.
- S3 rename is not atomic because it is delete-plus-put; native S3 directory existence uses marker and prefix heuristics and can be masked by files.
- S3 and FTP append are marked optional/not supported, so code assuming appendable filesystems will fail on those backends.
- `BytesWritable.getBytes()` exposes backing capacity, not exact logical data length; callers must honor `getLength()` or use `copyBytes()`.
- `ArrayPrimitiveWritable` wraps primitive arrays without copying, so later caller mutation can change serialized content.
- `BloomMapFile.Reader.probablyHasKey` can return false positives; callers must still perform real lookup for correctness.
- `AbstractMapWritable` class IDs are limited to 1..127 per map instance.
- `FsPermission.getUMask` preserves deprecated decimal umask compatibility, creating migration risk around configuration parsing.
- `Syncable.sync()` is deprecated in favor of `hflush`; tests and callers need to distinguish reader visibility from durable sync.

## Test Signals

Good test coverage inferred from this API slice should include:

- `FileSystem` contract tests for create/open/append/delete/rename/mkdirs/list/status across local, filter, FTP/KFS/S3/native S3 where available.
- Listing/globbing tests for filters, brace expansion, escaping, sorted output, missing non-glob path returning null, and glob-with-no-match returning an empty array.
- `RemoteIterator`, `listLocatedStatus`, and `listFiles(recursive)` tests that verify file/directory behavior and block location presence for files.
- `FSDataInputStream` tests for seek, positional read, readFully, current-position preservation, and `seekToNewSource`.
- `FSDataOutputStream` tests for position accounting, statistics increments, close behavior, `hflush`, `hsync`, and deprecated `sync` compatibility.
- `FileUtil` tests for recursive delete with normal files/directories and symlinks, copy/deleteSource/overwrite, copyMerge, archive extraction, temp file creation, hard link count, and local permission commands.
- `FilterFileSystem` delegation tests that every public method forwards to the wrapped filesystem and preserves exceptions.
- Permission tests for short/octal/symbolic parsing, sticky bit, umask application, deprecated umask key compatibility, and `Writable` round trips.
- Trash tests for disabled trash, already-in-trash paths, checkpoint creation, expunge policy, and superuser emptier behavior.
- Backend-specific tests for S3 unsupported append, S3 rename non-atomic behavior, native S3 directory markers, FTP path/status operations, and KFS lock/release/block-location behavior.
- `Writable` round-trip tests for primitive wrappers, bytes capacity versus length, arrays, enum sets including empty/null values with element type, compressed writables, map writable class ID mapping, and generic writable type-index validation.
- Raw comparator tests for primitive writable serialized byte comparisons and `BinaryComparable` equality/hash/ordering.

## Chunk Boundary Notes

The preceding chunk is needed for the beginning of `FileSystem` and earlier filesystem types. The following chunk is needed for the rest of `IOUtils` and later `org.apache.hadoop.io` classes. This chunk's final merge should preserve that `IOUtils` is incomplete here and that `FileSystem` is partial at the beginning.

### subset-b-007255: lines 12016-18218

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.22.0.xml lines 12016-18218

## Scope and Purpose

This chunk is a JDiff XML API descriptor for Hadoop Core 0.22.0, not executable Java source. It captures the public/protected API surface for the tail of `org.apache.hadoop.io` and the beginning of `org.apache.hadoop.io.compress`. The described code is Hadoop's binary serialization, ordered file, text encoding, comparator, and compression plumbing used by MapReduce, RPC, filesystem data formats, and command-line utilities.

The chunk starts inside `IOUtils.copyBytes` overloads and finishes inside `GzipCodec`, so it should be merged with adjacent chunks for whole-file package boundaries. Within this slice, the main themes are:

- stream copy/cleanup helpers;
- primitive and compound `Writable` implementations;
- sorted persistent file containers (`MapFile`, `SetFile`, `SequenceFile`);
- raw comparators and writable factory/clone utilities;
- UTF-8 byte-oriented text handling;
- compression codec abstractions and stream wrappers.

## Important APIs, Types, and Functions

### `org.apache.hadoop.io` utilities and primitive writables

- `IOUtils` methods visible at the start of the chunk include `copyBytes(InputStream, OutputStream, Configuration[, boolean])`, `readFully`, `skipFully`, `cleanup`, `closeStream`, and `closeSocket`. They centralize stream transfer, exact-byte reads/skips, and best-effort cleanup that deliberately suppresses cleanup-time `IOException`s.
- `IOUtils.NullOutputStream` is a `/dev/null` style `OutputStream` with byte-array and single-byte `write` overloads.
- `LongWritable`, `VIntWritable`, and `VLongWritable` are mutable numeric `WritableComparable` wrappers. They expose default/value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `LongWritable.Comparator` and `LongWritable.DecreasingComparator` extend `WritableComparator` to compare serialized longs directly, including descending order.
- `NullWritable` is a singleton-like marker value with `get`, no-op serialization, constant comparison/equality behavior, and a raw comparator.
- `MultipleIOException` groups multiple `IOException` instances via `getExceptions` and static `createIOException`.

### Persistent ordered files

- `MapFile` models a directory-backed sorted key/value map with public constants `INDEX_FILE_NAME` and `DATA_FILE_NAME`, plus static `rename`, `delete`, `fix`, and `main`. Its Javadoc records the important persistence model: a map directory contains a full `data` file and a smaller in-memory `index` file containing a fraction of sorted keys.
- `MapFile.Reader` is a synchronized, closeable lookup/scan API over a `MapFile`. It has modern construction via `Path`, `Configuration`, and `SequenceFile.Reader.Option[]`, plus deprecated `FileSystem/String` constructors. It exposes key/value class accessors, `open`, `createDataFileReader`, `reset`, `midKey`, `finalKey`, `seek`, `next`, `get`, two `getClosest` overloads, and `close`.
- `MapFile.Writer` is the append side. It has many deprecated constructor forms plus an option-based constructor, static options for key class, comparator, value class, compression, and progress callback, index interval accessors/mutators, `append`, and `close`. Appends require sorted keys, and the index interval controls sparse index density.
- `SetFile`, `SetFile.Reader`, and `SetFile.Writer` specialize `MapFile` as a key-only ordered set. The writer appends strictly increasing keys; the reader supports `seek`, `next`, and exact `get`.

### Writable maps, object wrappers, and factories

- `MapWritable` and `SortedMapWritable` extend `AbstractMapWritable` and implement `Map`/`SortedMap` style APIs. They expose copy constructors, map mutation/query methods, and `readFields`/`write`. These types persist heterogeneous writable keys and values by pairing data with class-id metadata inherited from `AbstractMapWritable`.
- `ObjectWritable` wraps arbitrary declared classes for Hadoop serialization/RPC. It records a declared class and instance value, has `get`, `getDeclaredClass`, `set`, `toString`, instance `readFields`/`write`, static `writeObject` overloads with optional declared class/configuration, static `readObject` overloads, `loadClass`, and `Configurable` methods.
- `Writable`, `WritableComparable`, `RawComparator`, `WritableComparator`, `WritableFactory`, `WritableFactories`, and `WritableUtils` define the serialization comparison substrate. `WritableComparator` provides class-specific comparator registration/lookup, object comparison fallback, optimized raw byte comparison, byte hashing, and primitive decoders such as `readInt`, `readLong`, `readVLong`, and `readVInt`.
- `WritableFactories` has synchronized `setFactory`/`getFactory` and `newInstance` helpers so non-public writable classes can be instantiated during deserialization.
- `WritableUtils` covers compressed byte/string arrays, normal string arrays, enum string serialization, writable cloning via serialization, variable-length integer/long encoding and decoding, full skipping, conversion of writables to byte arrays, and bounded `readStringSafely`.

### Hashing and text

- `MD5Hash` is a 16-byte `WritableComparable` digest wrapper. It can be built from strings or bytes, read/written from data streams, computed from byte arrays or streams via static `digest` overloads, exposed as raw bytes, summarized via `halfDigest`/`quarterDigest`, compared, stringified, and parsed back with `setDigest`. `MD5Hash.Comparator` compares serialized digests.
- `Text` is Hadoop's mutable UTF-8 byte string and extends `BinaryComparable`. It stores raw UTF-8 bytes plus a byte length, supports construction from `String`, `Text`, or bytes, byte copying/raw access, byte-position `charAt` and `find`, multiple `set` overloads, `append`, `clear`, `toString`, serialization, equality/hash, static UTF-8 `decode`/`encode`, `readString`/`writeString`, validation, code-point extraction, and `utf8Length`.
- `Text.Comparator` and legacy `UTF8.Comparator` provide raw byte comparators for UTF-8 values.
- `Stringifier<T>` is a closeable serializer-to-string abstraction with `toString`, `fromString`, and `close`.

### SequenceFile

- `SequenceFile` is the main flat binary key/value persistence API. Static methods get/set default compression type in `Configuration` and create `Writer` instances. Most older `createWriter` overloads are explicitly deprecated in favor of `createWriter(Configuration, Writer.Option...)`.
- `SequenceFile.CompressionType` is an enum for the file compression modes documented in this chunk: uncompressed, record-compressed, and block-compressed.
- `SequenceFile.Metadata` is a `TreeMap<Text,Text>` wrapper with constructors, `get`, `set`, `getMetadata`, serialization, equality, hash, and string conversion.
- `SequenceFile.Reader` has constructors for option-based, file-based, and stream/range-based reads. Static options include `file`, `stream`, `start`, `length`, and `bufferSize`. It exposes file/class/compression/metadata introspection, object and writable `next` APIs, raw key/value reads, `createValueBytes`, `seek`, `sync`, `syncSeen`, `getPosition`, `getCurrentValue`, `close`, and `toString`.
- `SequenceFile.Writer` is closeable and supports option-based construction through static `file`, `bufferSize`, `stream`, `replication`, `blockSize`, `progressable`, `keyClass`, `valueClass`, `metadata`, and `compression` options. It exposes key/value class and codec introspection, `sync`, `append` overloads, `appendRaw`, `getLength`, and synchronized `close`.
- `SequenceFile.Sorter`, `RawKeyValueIterator`, `SegmentDescriptor`, and `ValueBytes` support external sorting and merging of sequence files. The sorter configures merge factor, memory, and progress callbacks; sorts paths; returns raw iterators; merges segments; clones writer attributes; and writes merged output.

### Secure IO

- `SecureIOUtils.openForRead` and `createForWrite` expose owner-aware local file access APIs. They depend on `java.io.File`, `FileInputStream`, `FileOutputStream`, and Unix owner/group validation strings. `AlreadyExistsException` is a nested `IOException` used by creation paths when a target already exists.

### Compression package

- `CompressionCodec` defines the core codec contract: create compression/decompression streams with or without pooled `Compressor`/`Decompressor` instances, report compressor/decompressor classes, create compressor/decompressor instances, and return the default filename extension.
- `CompressionCodecFactory` discovers/configures codecs from `Configuration`, supports `getCodecClasses`/`setCodecClasses`, resolves codecs by `Path` extension or class name, removes suffixes, has a diagnostic `main`, and carries a commons-logging `LOG` field.
- `CodecPool` is a global compressor/decompressor reuse pool with `getCompressor(codec[, conf])`, `getDecompressor(codec)`, `returnCompressor`, and `returnDecompressor`.
- `CompressionInputStream` and `CompressionOutputStream` are base stream wrappers around protected `in`/`out`. They define lifecycle hooks (`resetState`, `finish`), position/seek methods for input, and close/flush/write behavior for output.
- `Compressor` and `Decompressor` model zlib-like state machines: set input/dictionary, check input/dictionary needs, finish/finished state, compress/decompress into caller buffers, report counters/remaining bytes, reset, end, and for compressors, `reinit(Configuration)`.
- `CompressorStream` and `DecompressorStream` adapt those state machines to Java streams. Their protected fields include the codec state object, a byte buffer, and closed/eof flags; methods drive compression/decompression, reset state, close, and ordinary stream reads/writes.
- `BlockCompressorStream` and `BlockDecompressorStream` specialize the stream wrappers for block-based algorithms. The compressor writes uncompressed block lengths followed by one or more length-prefixed compressed chunks; the decompressor reads those blocks back and can reset state.
- `BZip2Codec` implements `SplittableCompressionCodec`. It provides BZip2 input/output streams and a split input stream with start/end offsets plus `READ_MODE`; its compressor/decompressor pooling methods are documented as unsupported/dummy.
- `DefaultCodec` implements `Configurable` and `CompressionCodec`, bridging Hadoop `Configuration` to default compressor/decompressor types and stream creation. `GzipCodec` extends it and overrides output stream creation plus compressor creation/type methods visible in this chunk.

## Control Flow and Data Flow

The JDiff descriptor exposes call contracts rather than method bodies, but the API shapes reveal the key flows:

- Writable serialization is a two-phase contract: producers call `write(DataOutput)`, consumers allocate or factory-create an instance and call `readFields(DataInput)`. Comparators either deserialize objects or use raw byte helpers to avoid allocation.
- `ObjectWritable` adds a dynamic type envelope around that contract: it writes declared class metadata, then value data, and reads by loading classes through `Configuration`-aware logic.
- `MapFile` writes sorted key/value pairs to a data `SequenceFile` and periodically writes keys to an index file. Readers load the sparse index, binary-search/seek near a target key, then scan the data stream to satisfy `seek`, `get`, `next`, and `getClosest`.
- `SetFile` follows the same path but stores only keys, with `NullWritable` or equivalent empty value behavior implied by the set abstraction.
- `SequenceFile.Writer` writes a header with key/value classes, compression flags, codec class, metadata, and sync marker, then records or blocks. `sync` creates seekable recovery points; `getLength` returns positions suitable for reader `seek`.
- `SequenceFile.Reader` parses the header, selects decompression behavior from compression flags and codec metadata, iterates object or raw records, supports split-aligned `sync`, and exposes `syncSeen` for callers that need split boundaries.
- `SequenceFile.Sorter` reads raw key/value segments, compares keys with a `RawComparator`, spills/merges segments under memory and factor limits, and writes sorted sequence output while optionally deleting temporary segment files through `SegmentDescriptor.cleanup`.
- Compression stream flow is state-machine driven. A caller obtains a codec from the factory, may obtain a reusable compressor/decompressor from `CodecPool`, wraps an input/output stream, pushes bytes through `write` or `read`, then calls `finish`/`close` and returns codec state objects to the pool.
- Splittable BZip2 reads use `createInputStream(seekableIn, decompressor, start, end, readMode)` to align with compressed block boundaries and report progress either continuously or at block boundaries.

## State and Persistence Behavior

- `Writable` instances are mutable and stateful; callers are expected to reuse objects in tight loops. `readFields` overwrites object state, so stale state must be cleared or fully replaced by implementations.
- `MapWritable` and `SortedMapWritable` persist both map entries and class mappings, enabling heterogeneous writable maps across process boundaries.
- `Text` stores byte arrays that may have extra capacity beyond `getLength()`. `getBytes()` exposes the backing array, while `copyBytes()` returns exact-size data. This distinction matters for persistence and comparisons.
- `MD5Hash` persists fixed-length 16-byte digest state and exposes string parsing/formatting for stable identifiers.
- `VersionedWritable` writes a version byte before subclass data, and `VersionMismatchException` signals incompatible serialized versions.
- `MapFile` persistence is directory based: `data` is authoritative, `index` is derived/sparse. `fix` can recreate the index from data and returns valid-entry counts or `-1` when no fix is needed.
- `SequenceFile` persistence includes a magic/version header, key/value class names, compression flags, codec class, metadata, sync marker, and one of three record layouts. Block-compressed files batch key lengths, keys, value lengths, and values into separate compressed blocks.
- Compression objects have lifecycle state: input buffers, dictionaries, byte counters, finished flags, and native resources. `reset` reuses state, while `end` releases resources. `CodecPool` preserves reusable instances globally.
- `CompressionInputStream` tracks maximum available data and stream position semantics; `DecompressorStream` tracks eof/closed flags; `CompressorStream` tracks closed state and an internal buffer.

## Dependencies and Integration Points

- Core Java dependencies include `java.io` streams/data streams/files, `java.net.Socket`, `java.security.MessageDigest`, `java.nio.ByteBuffer`, `java.util` collections, `java.lang.Enum`, and `Comparable`.
- Hadoop dependencies include `Configuration`, `Configurable`, `FileSystem`, `Path`, `FSDataInputStream`, `FSDataOutputStream`, `Progressable`, `Progress`, `ReflectionUtils`, `BinaryComparable`, `DataOutputBuffer`, serializer interfaces, and compression interfaces.
- Commons Logging appears in `IOUtils.cleanup` and `CompressionCodecFactory.LOG`.
- `SequenceFile` and `MapFile` integrate tightly with Hadoop filesystem implementations, MapReduce intermediate/output storage, sorted data maintenance, split processing, and compression codec configuration.
- `WritableComparator.define`, `WritableFactories.setFactory`, `CompressionCodecFactory.setCodecClasses`, and `CodecPool` are global or configuration-backed extension points. Incorrect registration can affect many readers/writers in the same JVM.
- Deprecated constructors and factory overloads preserve compatibility with older Hadoop APIs while steering new code to option-based `Reader`/`Writer` construction.

## Risks and Edge Cases

- The source is an API XML snapshot. It omits implementation details such as exact validation, synchronization internals, and exception paths; final research for the whole source should merge adjacent chunks and, if needed, compare with Java source.
- Many APIs are mutable and reusable for performance. Bugs often come from retaining references to reused `Writable`, `Text`, raw byte buffers, compressor input buffers, or exposed backing arrays.
- `IOUtils.copyBytes` overloads differ in whether they close streams. Misusing the close flag can leak streams or close caller-owned streams unexpectedly.
- `WritableUtils` variable-length integer encoding is wire-format critical. Boundary values around one-byte ranges, negative values, and malformed first bytes are compatibility-sensitive.
- `readStringSafely` only reads the vint when encoded length is invalid, leaving subsequent bytes for caller handling; callers must account for stream position after exceptions.
- `MapFile.Writer` and `SetFile.Writer` require sorted/strictly increasing keys. Appending out-of-order keys can corrupt lookup assumptions.
- `MapFile` index files are memory-resident on read. Large keys or a small index interval can create high heap pressure.
- `SequenceFile` has multiple legacy writer constructors and compression modes. Interoperability depends on preserving header metadata, sync positions, and raw value behavior across all modes.
- `SequenceFile.Writer.getLength()` may return a synchronized block position rather than the exact last appended key location under block compression; split/seek callers must accept reading an earlier key.
- `SequenceFile.Sorter` performance depends heavily on raw comparator efficiency and `Writable.readFields` avoiding allocations.
- Compression pooling requires disciplined return/reset/end behavior. Returning an object still referenced by a stream or failing to return/reset pooled native codecs can cause data corruption, leaks, or cross-call contamination.
- BZip2 codec methods with compressor/decompressor arguments are explicitly documented as unsupported in this version, despite the generic `CompressionCodec` interface requiring them.
- Secure file APIs depend on platform ownership semantics; behavior can differ across local filesystems, Unix permissions, and unsupported platforms.

## Test Signals

Useful tests for this API surface should include:

- Round-trip serialization tests for `LongWritable`, `VIntWritable`, `VLongWritable`, `NullWritable`, `MD5Hash`, `Text`, `MapWritable`, `SortedMapWritable`, `ObjectWritable`, `VersionedWritable`, and metadata maps.
- Comparator parity tests proving raw `WritableComparator` results match object `compareTo`, including `LongWritable.DecreasingComparator`, `Text.Comparator`, `MD5Hash.Comparator`, and boundary byte encodings.
- `WritableUtils` boundary tests for vint/vlong sizes, negative encodings, malformed/truncated input, compressed byte/string arrays, enum serialization, `skipFully`, and `readStringSafely` maximum-length failures.
- `IOUtils` tests for full-read/full-skip EOF behavior, copy buffer sizing, and stream close/no-close variants.
- `Text` UTF-8 tests for invalid byte sequences, code point boundaries, byte-position `find`, `append`, capacity-vs-length behavior, and static encode/decode validation.
- `MapFile`/`SetFile` tests for ordered append enforcement, sparse index lookup, `getClosest` before/after behavior, index rebuild via `fix`, empty file `midKey`, final key retrieval, and deprecated constructor compatibility.
- `SequenceFile` tests for all compression modes, option-based and deprecated writer construction, metadata persistence, raw/object reads, sync/seek/split behavior, appendRaw, `getLength` under block compression, sorting/merging, and segment cleanup/preserve behavior.
- Compression tests for codec discovery by extension/class name, suffix removal, default extensions, stream close/finish/reset behavior, pool reuse and reinitialization, block-compression framing, BZip2 split reads, and unsupported BZip2 compressor/decompressor operations.
- Secure IO tests for owner/group validation, already-existing output paths, missing files, and platform-specific permission behavior.

## Cross-Chunk Notes

- The chunk begins after earlier `IOUtils.copyBytes` overloads and likely after the start of the `IOUtils` class. Adjacent prior chunk research is needed for full `IOUtils` coverage.
- The chunk ends inside `GzipCodec`; adjacent next chunk research is needed for remaining gzip input/decompressor methods and later compression classes.
- Because this file is generated JDiff XML, whole-file merge should preserve the distinction between documented API contract and implementation behavior inferred from Hadoop conventions.

### subset-b-007256: lines 18219-24654

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.22.0.xml lines 18219-24654

## Scope

This chunk is a generated JDiff API snapshot for Hadoop Core 0.22.0, not implementation code. It starts inside the public API entry for `org.apache.hadoop.io.compress.GzipCodec`, then covers compression stream/splitting APIs, the `org.apache.hadoop.io.file.tfile` package, native I/O wrappers, serialization providers including Avro integration, logging helpers, the metrics framework and providers, network topology/socket factories, and most of the deprecated Hadoop Record I/O runtime. It ends inside the long package-level Record I/O design document while describing binary serialization of integral values, so adjacent chunks are needed for the remainder of that package doc.

The XML records public/protected API compatibility metadata: packages, classes/interfaces, inheritance, implemented interfaces, constructors, methods, parameters, exceptions, fields, visibility, static/final/abstract/native/synchronized flags, deprecation state, and embedded Javadoc contracts. Research conclusions below are based on those signatures and docs, not on method bodies.

## Purpose and major API surface

The compression portion exposes `GzipCodec` factory methods for input streams, decompressors, decompressor type lookup, and default extension lookup. `GzipCodec.GzipOutputStream` bridges a `DeflaterOutputStream` into Hadoop's `CompressionOutputStream` shape with `write`, `flush`, `finish`, `resetState`, and `close`. `SplitCompressionInputStream` and `SplittableCompressionCodec` define the contract for codecs that can decompress a compressed stream from adjusted split boundaries, returning adjusted start/end offsets and supporting `READ_MODE` values for continuous versus block-aware reads.

`org.apache.hadoop.io.file.tfile` describes TFile, a container of typeless byte key/value pairs with block compression, named meta blocks, optional sorted keys, key/file-offset seeks, and memory usage tied to compression buffers plus data/meta indexes. Constants name supported compression algorithms (`none`, `lzo`, `gz`) and comparators (`memcmp`, Java-class comparator prefix). `TFile.makeComparator`, `getSupportedCompressionAlgorithms`, and `main` expose comparator creation, algorithm discovery, and file information dumping.

`TFile.Reader` is the read entry point. It reports comparator name, sortedness, entry count, first/last keys, entry/key comparators, and meta blocks, and creates scanners over the whole file, byte ranges, key ranges, or record-number ranges. It can map compressed-block offsets to nearby record numbers and sample keys. `TFile.Reader.Scanner` is cursor-based and supports seek, rewind, seek-to-end, lower/upper bounds by raw byte slices or `RawComparable`, forward advance, current entry access, record-number lookup, and close. `TFile.Reader.Scanner.Entry` exposes key/value copying into `BytesWritable` or user buffers, direct key/value streaming, length checks, output-stream writes, comparison by raw bytes or `RawComparable`, equality, and hash code.

`TFile.Writer` creates TFiles over `FSDataOutputStream` with minimum block size, compression, comparator, and `Configuration`. It supports direct append from byte arrays, staged key/value append streams, and named meta-block creation with default or explicit compression. Its docs state the writer must be closed to finish and release resources, and meta block names must be unique.

`org.apache.hadoop.io.file.tfile.Utils` supplies shared variable-length integer encoding/decoding, string encoding as `VInt` length plus Text bytes, and lower/upper-bound binary searches over `List` or array slices. `Utils.Version` serializes a major/minor version as two shorts, compares versions, tests compatibility, exposes fixed serialized size, and is recommended for applications layered on TFile. `MetaBlockAlreadyExists`, `MetaBlockDoesNotExist`, and `RawComparable` round out meta-block errors and raw byte range comparison.

`org.apache.hadoop.io.nativeio` exposes POSIX-facing JNI wrappers. `Errno` enumerates POSIX error values. `NativeIO` reports native availability and wraps `open(2)`, `fstat(2)`, and `chmod(2)`, with public `O_*` flag constants. `NativeIO.Stat` returns owner, group, and mode plus `S_IF*`, `S_IS*`, and user permission constants. `NativeIOException` carries an `Errno` and formats native failures.

`org.apache.hadoop.io.serializer` covers serialization provider implementations. `JavaSerialization` accepts Java `Serializable` classes and returns Java serializer/deserializer instances. `JavaSerializationComparator` compares objects through Java deserialization. `WritableSerialization` is a `Configured` provider for Hadoop `Writable`s. The package doc positions this as a framework for pluggable serialization mechanisms used by subsystems such as MapReduce.

`org.apache.hadoop.io.serializer.avro` integrates Avro. `AvroReflectSerializable` is a tag interface for reflect serialization. `AvroSerialization` is the configured base with schema, datum writer, and datum reader hooks and `AVRO_SCHEMA_KEY`. `AvroReflectSerialization` accepts tagged classes or classes in configured packages (`AVRO_REFLECT_PACKAGES`) and returns reflect schemas/readers/writers. `AvroSpecificSerialization` handles Avro `SpecificRecord` classes.

`org.apache.hadoop.log` includes the deprecated `EventCounter` Log4J appender shim and `LogLevel`, a command-line/runtime log-level changer with `main` and `USAGES`. `EventCounter` extends the metrics JVM event counter, indicating older logging metrics APIs are being bridged.

`org.apache.hadoop.metrics` and provider packages define the original Hadoop metrics API. `FileContext` writes metrics records to a configured file, with init, start/stop monitoring, emit, flush, file name, period, and property constants. `GangliaContext` sends metrics to Ganglia over UDP, maintains an XDR buffer, server list, socket, and helpers for XDR strings/ints, units, slope, `tmax`, and `dmax`; `GangliaContext31` adapts emission for Ganglia 3.1.x.

`org.apache.hadoop.metrics.spi` is the service-provider implementation layer. `AbstractMetricsContext` manages context attributes, records, updaters, monitoring lifecycle, periodic update/remove flows, period parsing, emit, flush, and close. `CompositeContext` fans metrics operations to subcontexts. `MetricsRecordImpl` stores tags and absolute/incremental metrics, provides typed tag/metric setters and incrementers, and updates/removes buffered rows in its context. `MetricValue` wraps a number plus absolute/increment flag. `NoEmitMetricsContext`, `NullContext`, and `NullContextWithUpdateThread` provide disabled or no-output contexts. `OutputRecord` exposes copies and lookup views of emitted tags/metrics. `Util.parse` parses server specifications.

`org.apache.hadoop.net` supplies DNS-to-rack mapping and socket factories. `DNSToSwitchMapping` resolves host/IP lists to rack paths. `CachedDNSToSwitchMapping` wraps a raw mapping with caching. `ScriptBasedMapping` is configurable and implements rack resolution through an external script. `SocksSocketFactory` and `StandardSocketFactory` implement socket creation overloads, equality/hash behavior, and configuration support; despite the `StandardSocketFactory` doc wording, it represents standard socket creation while `SocksSocketFactory` uses a supplied or configured SOCKS proxy.

`org.apache.hadoop.record` is Hadoop Record I/O, already marked deprecated in several concrete input/output classes in favor of Avro. `RecordInput` and `RecordOutput` define primitive, string, buffer, record, vector, and map read/write hooks with tags. Binary, CSV, and XML concrete input/output classes implement those hooks. `BinaryRecordInput` and `BinaryRecordOutput` expose thread-local `get(DataInput/DataOutput)` helpers. `CsvRecordInput/Output` and `XmlRecordInput/Output` provide text and XML encodings. `Index` is the iterator-like API for deserializing maps/vectors. `Buffer` is the native Java representation of the Record I/O `buffer` type, with backing-array ownership/copying, count/capacity control, append, truncate, reset, comparison, equality, clone, and string conversion. `Record` is the abstract generated-record base and also implements `Writable`-style `write`/`readFields`, tagless serialization helpers, `compareTo`, and `toString`. `RecordComparator` extends `WritableComparator` and registers optimized comparators. `org.apache.hadoop.record.Utils` provides float/double parsing, zero-compressed variable-length integer operations, encoded-size computation, binary writes, byte lexicographic comparison, and hex support.

The trailing package-level Record I/O document explains the historical DDL system: primitive types (`byte`, `boolean`, `int`, `long`, `float`, `double`, `ustring`, `buffer`), composite `record`, `vector`, and `map`, module/include/class syntax, generated Java/C++ code, generated comparison and accessors, binary/CSV/XML encodings, and language type mappings. It explicitly lists non-goals such as serializing arbitrary C++ classes, complex linked/tree structures, built-in indexing/compression/checksums, and dynamic XML-schema object construction.

## Control flow and behavioral contracts

The XML has no executable flow, but the Javadocs define caller-visible flows. Splittable compression flow starts with a seekable compressed stream and requested `[start,end)` offsets; the codec may adjust them to block boundaries, then `getAdjustedStart()` and `getAdjustedEnd()` expose the effective range. `READ_MODE.BYBLOCK` lets codecs surface block boundaries, while continuous mode hides them from callers.

TFile write flow is stateful. A writer is constructed with stream, block/compression/comparator settings, and configuration. Callers either append complete key/value byte slices or call `prepareAppendKey()` followed by `prepareAppendValue()` to stream one entry. Meta blocks are opened through `prepareMetaBlock()`. Once `close()` is called, indexes and footer metadata are finalized; using staged streams out of order or reusing a meta-block name is an API error.

TFile read flow is scanner-driven. A reader is opened over an `FSDataInputStream` and file length, then scanners delimit a byte/key/record range and maintain an implicit cursor. `seekTo`, `lowerBound`, and `upperBound` position the cursor; `advance()` moves forward and returns whether another entry exists; `entry()` exposes a point-in-time key/value accessor. Entry APIs offer zero-copy-oriented stream writes and streams as alternatives to copying values into caller buffers.

TFile sorted-key behavior is comparator-dependent. Key range scanners, entry comparisons, and lower/upper-bound searches require a comparator compatible with the file's comparator name. `RawComparable` lets APIs pass byte-array windows without allocating key wrapper objects.

Native I/O flow is availability-gated. Callers should check `NativeIO.isAvailable()` before depending on JNI-backed calls. Native failures surface as `NativeIOException` with an `Errno`, and successful `fstat` returns a `Stat` snapshot rather than live file metadata.

Serialization framework flow is provider-selection based. Each `Serialization` implementation declares `accept(Class)` and supplies serializer/deserializer pairs. Writable serialization delegates to `Writable.readFields/write`; Java serialization delegates to JVM object serialization; Avro providers create schemas and datum readers/writers using reflect or specific strategies.

Metrics flow runs through contexts and records. Contexts initialize from a factory, create records, register periodic updaters, start monitoring, collect record updates/removals into buffered tables, emit records to providers, flush, and stop/close. Composite contexts duplicate these operations across subcontexts; null/no-emit contexts preserve update callbacks while suppressing output.

Network topology flow resolves a batch of hostnames/IP addresses to rack names. Script-based mapping is configurable and wrapped by a cache layer, so repeated host resolutions can avoid invoking the external script. Socket factory flow follows standard `SocketFactory` overloads, with SOCKS proxy behavior controlled by constructor/configuration.

Record I/O flow is translator-driven. Users write DDL files with includes, one module, and class declarations; `rcc` generates target-language classes. Generated records serialize fields sequentially through a selected `RecordOutput` and deserialize sequentially through `RecordInput`. Vector/map reading uses an `Index` whose `done()`/`incr()` methods drive collection traversal. Binary encoding serializes composite members in order and prefixes vector/map sizes; integral values use zero-compressed variable-length encoding.

## State, persistence, and side effects

The JDiff XML itself is persistent compatibility metadata. Runtime persistence described by the APIs includes compressed stream state, TFile on-disk key/value data blocks, meta blocks, indexes, version records, native file descriptors and filesystem mode bits, serialized object streams, Avro schemas, log level changes, metrics output files, Ganglia UDP datagrams, DNS-to-switch caches, socket connections, and Record I/O encoded streams.

TFile is the most storage-heavy API in this chunk. Writer state includes the output stream position, open key/value append state, minimum block size, compression algorithm, comparator identity, data-block index, meta-block index, and file footer/version metadata. Reader state includes file length, comparator, indexes, scanner ranges, current cursor, and decompression state for current blocks. Docs call out memory costs proportional to data-block and meta-block counts.

Metrics APIs maintain process state: context attributes, monitoring timer period, registered updater callbacks, per-context records, tag maps, metric maps, incremental versus absolute values, and provider resources such as file writers or UDP sockets. `stopMonitoring()` does not necessarily discard buffered data, while `close()` stops monitoring and frees buffered data/resources.

Record I/O `Buffer` exposes mutable backing-array state and capacity/count invariants. `set()` can adopt caller-supplied byte arrays while `copy()` duplicates them, so aliasing and mutation behavior differ. Generated `Record` instances persist field state and serialize through binary, CSV, or XML encodings.

Native I/O has host-dependent side effects. `open` creates file descriptors with POSIX flags; `chmod` changes mode bits; `fstat` observes owner/group/mode. These operations depend on native library loading and platform behavior.

Logging and network operations mutate external systems: `LogLevel` changes runtime logger levels; `GangliaContext` sends metrics datagrams; `FileContext` appends/flushed records to disk; socket factories create network sockets; script-based rack mapping can execute external scripts.

## Dependencies and integration points

Compression APIs integrate with `CompressionInputStream`, `CompressionOutputStream`, `CompressorStream`, `Decompressor`, Java `InputStream`/`OutputStream`, `IOException`, and codec implementations such as bzip2 that can report block boundaries.

TFile integrates with Hadoop filesystem and I/O classes including `FSDataInputStream`, `FSDataOutputStream`, `BytesWritable`, `RawComparator`, `WritableComparator`, `Text`-style string encoding, `Configuration`, `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, and Java `Comparator`/collections. Compression settings depend on Hadoop compression codec availability, including LZO and Gzip.

Native I/O depends on JNI/native libraries, Java `FileDescriptor`, POSIX open/chmod/fstat semantics, POSIX errno values, and platform-specific stat mode constants.

Serialization providers integrate with the Hadoop serialization framework, `Writable`, Java `Serializable`, `Configured`/`Configuration`, Avro `Schema`, `DatumReader`, `DatumWriter`, reflect data, and specific records.

Metrics integration points include `ContextFactory`, `MetricsContext`, `MetricsRecord`, updater callbacks, output providers, Log4J event counting, metrics JVM counters, Ganglia wire formats, files, UDP sockets, and server specification parsing.

Network APIs integrate with `Configuration`, external topology scripts, Java `SocketFactory`, `Socket`, `Proxy`, `InetAddress`, local/remote socket addresses, and Hadoop rack-awareness consumers.

Record I/O integrates with generated code from `rcc`, Hadoop `Writable` and `WritableComparable` style APIs, `DataInput`/`DataOutput`, Java `TreeMap`/`ArrayList`, XML/CSV/binary encoders, and Avro as the documented replacement path.

## Risks and compatibility notes

This is a partial line-bounded chunk. It starts after the beginning of `GzipCodec` and ends before the completion of the `org.apache.hadoop.record` package documentation, so whole-class/package conclusions for those boundaries require adjacent chunks.

TFile is compatibility-sensitive because on-disk layout, comparator naming, compression names, meta-block names, block indexes, and version compatibility are externally visible. Changes to key length limits, chunking behavior, index memory assumptions, scanner range semantics, or comparator construction can break stored-file interoperability or random-access behavior.

TFile APIs have resource-ordering risks. Writers must close to finalize data, staged append key/value streams must be used in the documented sequence, scanner/reader close invalidates behavior, and value length may be unknown unless `isValueLengthKnown()` is checked.

Splittable compression must adjust split boundaries correctly. Incorrect `start`/`end` adjustment or mismatched continuous/block reporting can cause duplicate records, skipped bytes, or failed decompression in parallel file processing.

Native I/O is optional and platform-sensitive. Code must handle unavailable JNI, unsupported flags/constants, permissions failures, and differences in owner/group/mode semantics. `NativeIOException.getErrno()` is the stable way to inspect native failures.

Metrics APIs are stateful and concurrency-sensitive. Periodic updater registration, buffered tag/metric rows, incremental metric handling, provider close/flush behavior, and composite fan-out can produce stale, duplicated, or lost metrics if lifecycle methods are misordered.

Network topology mapping depends on external DNS/script behavior and cache correctness. Bad or partial mappings can affect rack-aware placement decisions. Socket factory equality/hash behavior matters because these factories are often configured reflectively and cached.

Record I/O is deprecated in favor of Avro, but remains a public compatibility surface. Generated-code contracts, binary zero-compressed integer encoding, CSV/XML escaping, `Buffer` aliasing, comparator registration, and `Writable` integration must stay stable for legacy data and generated classes.

## Test signals

JDiff validation should verify the XML remains well-formed across this range and preserves package/class/interface boundaries, method signatures, parameter types, declared exceptions, visibility, field constants, deprecation markers, and embedded package docs.

Compression tests should cover `GzipCodec` stream/decompressor creation, gzip output `finish`/`flush`/`resetState`/`close`, splittable codec adjusted boundaries, and continuous versus block read modes on block-compressed data.

TFile tests should cover writer close/finalization, complete append and staged append paths, duplicate and missing meta-block errors, compression algorithm discovery, sorted and unsorted files, comparator creation, scanner creation by full file/byte range/key range/record range, lower/upper-bound behavior, first/last key lookup, record-number-near and key-near queries, entry buffer copies, streaming key/value access, unknown value length handling, version serialization/compatibility, and `Utils` VInt/VLong/string/binary-search helpers.

Native I/O tests should cover unavailable native libraries, successful and failing `open`, `fstat`, and `chmod`, errno propagation in `NativeIOException`, mode constant interpretation, and `Stat` owner/group/mode getters.

Serialization tests should cover provider `accept()` selection for `Writable`, `Serializable`, Avro reflect tagged/configured-package classes, and Avro specific classes; serializer/deserializer round trips; schema lookup through configuration; and comparator behavior for Java serialization.

Metrics tests should exercise context initialization from attributes, period parsing, start/stop/close lifecycle, updater registration/removal, absolute versus incremental metrics, tag removal, update/remove row behavior, output record copies, file provider append/flush, Ganglia XDR encoding and socket close, composite fan-out, and null/no-emit contexts with and without update threads.

Network tests should cover batch rack resolution, cache hits/misses around a raw mapping, script-based configuration and script failure handling, SOCKS proxy socket construction, standard socket construction, and socket factory equality/hash semantics.

Record I/O tests should cover binary/CSV/XML primitive and composite round trips, generated `Record` tag and tagless serialization/deserialization, `Index` traversal for vectors/maps, `Buffer` set/copy/append/truncate/reset/capacity/compare/clone behavior, zero-compressed integer edge cases, byte lexicographic comparison, comparator registration, and legacy generated-code compatibility against existing encoded data.

### subset-b-007257: lines 24655-28377

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.22.0.xml lines 24655-28377

## Scope

This chunk is a generated JDiff API snapshot for Hadoop Core 0.22.0. It is not executable implementation source; it records public API metadata, inherited type relationships, method signatures, fields, exceptions, visibility flags, and embedded Javadocs. The chunk starts inside the `org.apache.hadoop.record` package documentation for Record I/O serialization formats, continues through deprecated Record I/O compiler and metadata APIs, covers selected security, token, utility, and Bloom filter APIs, and ends with an empty `org.apache.hadoop.util.hash` package marker and the closing `</api>`.

Because this is a line-bounded chunk, the opening `org.apache.hadoop.record` package documentation is partial. The merge lane must combine this chunk with adjacent chunks before making whole-package claims about `org.apache.hadoop.record`.

## Purpose

The opening Record I/O documentation describes Hadoop's legacy record serialization contract. It defines compact binary encodings for numeric and byte/string data, a structured CSV grammar for primitive and composite record values, and an XML-RPC-inspired XML representation for primitive values, structs, vectors, and maps. The documentation is important compatibility material because it describes wire formats independent of Java method signatures.

The `org.apache.hadoop.record.compiler`, `org.apache.hadoop.record.compiler.ant`, and `org.apache.hadoop.record.compiler.generated` packages expose the legacy Hadoop record compiler. These APIs parse record definition files, model record types and fields, generate language-specific code, and integrate the compiler into Ant builds. Nearly every type in this family is deprecated with guidance to use Avro, but the API remains visible in this 0.22.0 snapshot.

The `org.apache.hadoop.record.meta` package exposes runtime type metadata for Record I/O. It models primitive, vector, map, and struct type IDs, field type descriptors, and serializable `RecordTypeInfo` metadata. These classes support schema-aware reading, writing, and skipping of legacy record streams.

The `org.apache.hadoop.security` portion documents public authentication and identity helper APIs: group lookup providers, JNI-backed Unix group mapping, Kerberos name exception types, a Jetty SSL connector variant that can require Kerberos-backed SSL behavior, SASL RPC authentication enums and callback handlers, and `UserGroupInformation.AuthenticationMethod`.

The token packages expose public exception and delegation-token metadata surfaces: `SecretManager.InvalidToken` and `AbstractDelegationTokenSecretManager.DelegationTokenInformation`.

The `org.apache.hadoop.util` portion documents small but widely used utility contracts: disk exception types, typed varargs options, progress callbacks, reflection/configuration helpers, shell command execution wrappers, binary size-prefix parsing, and the standard `Tool`/`ToolRunner` command-line integration pattern.

The `org.apache.hadoop.util.bloom` portion documents Bloom-filter implementations and related algorithms: standard, counting, dynamic, and retouched Bloom filters, plus hash-function and selective-clearing scheme APIs. These classes provide probabilistic set membership, deletion/counting support, dynamic growth, and retouched false-positive handling.

## Important APIs, Types, and Functions

### Record I/O serialization documentation

- The binary serialization text describes zero-compressed integer and long encodings, IEEE 754 float/double values in network byte order, UTF-8 strings with a zero-compressed length prefix, and raw buffers with the same length prefix.
- The CSV format defines primitive encodings for booleans, ints, longs, floats, doubles, strings, and buffers. Strings start with `'`, buffers start with `#`, and composites use `s{}`, `v{}`, and `m{}` delimiters for structs, vectors, and maps.
- The XML format uses XML-RPC-style `<value>` wrappers. Primitive tags include `ex:i1`, `boolean`, `i4`/`int`, `ex:i8`, `ex:float`, `double`, and string/hex data encodings. Composite records are represented through `struct` members or `array` data elements.
- String escaping rules are part of the contract. CSV escapes null, newline, percent, and comma; XML strings percent-escape XML-disallowed characters, carriage returns, and percent signs.

### Deprecated record compiler model

- `CodeBuffer` wraps a `StringBuffer` and auto-indents generated code; it exposes `toString()`.
- `Consts` publishes compiler constant strings such as `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.
- `JType` is the abstract base for Record I/O compiler types. Concrete or composite type classes include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, and `JRecord`.
- `JField` is a thin wrapper for a record field, constructed from a name and a type parameter.
- `JFile` models one record definition file with included files and records; `genCode(String language, String destDir, ArrayList options)` generates code and returns an integer status while declaring `IOException`.

### Ant and generated parser APIs

- `RccTask` extends Ant `Task`. It supports `setLanguage(String)`, `setFile(File)`, `setFailonerror(boolean)`, `setDestdir(File)`, `addFileset(FileSet)`, and `execute()`. Its Javadoc describes `<recordcc>` usage for Java or C++ generation.
- `ParseException` is the JavaCC parse exception. It has a parser-generated constructor using `Token`, expected token sequences, and token images, plus default and message constructors. Public fields include `currentToken`, `expectedTokenSequences`, and `tokenImage`; `getMessage()` formats parser-aware errors.
- `Rcc` is the generated parser and command driver. Constructors accept `InputStream`, `InputStream` plus encoding, `Reader`, or `RccTokenManager`. Its grammar methods include `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`. It also exposes `main`, `usage`, `driver`, parser `ReInit` overloads, token access, `generateParseException`, and tracing toggles.
- `RccConstants` exposes token-kind constants for the record definition language: module, record, include, primitive type tokens, vector/map punctuation, string/identifier tokens, lexical states, and `tokenImage`.
- `RccTokenManager` accepts a `SimpleCharStream`, can switch lexical states, fill tokens, get the next token, and set a debug stream.
- `SimpleCharStream` is the JavaCC character stream with reader/input-stream constructors, optional encoding, line/column tracking, buffer expansion/filling, token start, backup, reinitialization overloads, image/suffix access, cleanup, and line/column adjustment.
- `Token` exposes JavaCC token state: kind, begin/end line and column, image, next token, and special-token links. `newToken(int)` is a static factory.
- `TokenMgrError` models lexical errors and exposes constructors, `addEscapes`, `LexicalError`, and `getMessage()`.

### Record metadata APIs

- `FieldTypeInfo` pairs a field ID/name with a `TypeID`, with getters, typed equality, object equality, and hash code.
- `TypeID` represents primitive type IDs. It exposes `getTypeVal()`, equality, hash code, shared constants for bool, buffer, byte, double, float, int, long, and string, and protected `typeVal` state.
- `TypeID.RIOType` is a public constants holder for byte codes for `BOOL`, `BUFFER`, `BYTE`, `DOUBLE`, `FLOAT`, `INT`, `LONG`, `MAP`, `STRING`, `STRUCT`, and `VECTOR`.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` extend `TypeID` for composite types. They expose element/key/value/field type accessors and composite equality/hash behavior.
- `RecordTypeInfo` extends `org.apache.hadoop.record.Record`. It has empty and named constructors, `getName`, `setName`, `addField`, `getFieldTypeInfos`, one-level `getNestedStructTypeInfo`, `serialize(RecordOutput, String)`, `deserialize(RecordInput, String)`, and `compareTo(Object)`.
- `Utils.skip(RecordInput, String, TypeID)` skips serialized record data according to type metadata.

### Security and token APIs

- `GroupMappingServiceProvider.getGroups(String)` returns all group memberships for a user, returns an empty list for a non-existing user, and may throw `IOException`.
- `JniBasedUnixGroupsMapping` implements group lookup by invoking libc through JNI.
- `KerberosName.BadFormatString` and `KerberosName.NoMatchingRule` are public static `IOException` subclasses for Kerberos name parsing failures.
- `Krb5AndCertsSslSocketConnector` extends Jetty `SslSocketConnector`. It has default and mode constructors, protected `createFactory()` and `newServerSocket(...)`, public `customize(...)`, and public static final `KRB5_CIPHER_SUITES`. Its purpose is to keep client authentication required when Kerberos support is enabled.
- `Krb5AndCertsSslSocketConnector.Krb5SslFilter` implements `javax.servlet.Filter` and passes the Kerberos principal and short name into servlet request handling.
- `Krb5AndCertsSslSocketConnector.MODE` is an enum-like public API with `values()` and `valueOf(String)`.
- `SaslRpcServer.AuthMethod` exposes enum values, `getMechanismName()`, serialized `read(DataInput)` and `write(DataOutput)`, and public final fields `code`, `mechanismName`, and `authenticationMethod`.
- `SaslRpcServer.QualityOfProtection` exposes `getSaslQop()` and public `saslQop`.
- `SaslRpcServer.SaslDigestCallbackHandler` and `SaslRpcServer.SaslGssCallbackHandler` implement JAAS `CallbackHandler` for DIGEST-MD5 token authentication and GSSAPI Kerberos respectively.
- `SaslRpcServer.SaslStatus` exposes enum values and a public final integer `state`.
- `UserGroupInformation.AuthenticationMethod` exposes the visible authentication method enum surface.
- `SecretManager.InvalidToken` is an `IOException` with a message constructor.
- `AbstractDelegationTokenSecretManager.DelegationTokenInformation` stores a token renew date and password and exposes `getRenewDate()`.

### General utilities

- `DiskChecker.DiskErrorException` and `DiskChecker.DiskOutOfSpaceException` are message-bearing `IOException` subclasses.
- `Options.getOption(Class, base[])` searches varargs options for the first instance of a required class. `Options.prependOptions(T[], T[])` prepends new options to an existing option array.
- Typed abstract option wrappers include `BooleanOption`, `ClassOption`, `FSDataInputStreamOption`, `FSDataOutputStreamOption`, `IntegerOption`, `LongOption`, `PathOption`, `ProgressableOption`, and `StringOption`, each with a protected value constructor and public `getValue()`.
- `Progressable.progress()` lets long-running operations report progress to Hadoop frameworks to avoid timeout assumptions.
- `ReflectionUtils` exposes `setConf(Object, Configuration)`, `newInstance(Class, Configuration)`, `setContentionTracing(boolean)`, `printThreadInfo(PrintWriter, String)`, `logThreadInfo(Log, String, long)`, `getClass(T)`, `copy(Configuration, T, T)`, and `cloneWritableInto(Writable, Writable)`.
- `Shell.ExitCodeException` preserves process exit code through `getExitCode()`.
- `Shell.ShellCommandExecutor` wraps a fixed command, optional working directory, environment, and timeout. It exposes `execute()`, `getExecString()`, protected `parseExecResult(BufferedReader)`, `getOutput()`, and `toString()`.
- `StringUtils.TraditionalBinaryPrefix` maps case-insensitive binary prefix symbols to powers of 1024. It exposes `valueOf(char)`, `string2long(String)`, and public final `value` and `symbol`.
- `Tool` extends `Configurable` and declares `run(String[])`. `ToolRunner` runs tools after generic Hadoop command-line parsing and exposes overloads with explicit or tool-provided `Configuration`, plus `printGenericCommandUsage(PrintStream)`.

### Bloom filter APIs

- `BloomFilter` extends `Filter` and exposes default and `(vectorSize, nbHash, hashType)` constructors, `add`, logical `and`, `or`, `xor`, `not`, `membershipTest`, `toString`, `getVectorSize`, and `Writable` `write`/`readFields`.
- `CountingBloomFilter` is final and extends `Filter`. It supports `add`, `delete`, set operations, `membershipTest`, `approximateCount(Key)`, string conversion, and Writable serialization. Its Javadoc warns that inserting the same key more than 15 times can overflow buckets and raise error rates.
- `DynamicBloomFilter` extends `Filter` and adds a constructor with row threshold `nr`. Its Javadoc describes row creation when the active Bloom filter is full.
- `HashFunction` returns multiple hash positions for a `Key`; it is constructed from maximum value, number of hashes, and hash type, and provides `clear()` as a no-op plus `hash(Key)`.
- `RemoveScheme` defines public short constants `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO` for retouched Bloom filter selective-clearing strategies.
- `RetouchedBloomFilter` extends `BloomFilter` and implements `RemoveScheme`. It accepts false-positive information through overloads for a single `Key`, `Collection`, `List`, or `Key[]`, and performs `selectiveClearing(Key, short)` before standard `write`/`readFields`.

## Control Flow and Behavioral Contracts

The XML itself has no runtime control flow, but the documented APIs imply several important paths.

Record compiler flow begins with `RccTask.execute()` or `Rcc.driver(String[])`, reads one or more `.jr` record definition files, tokenizes input with `SimpleCharStream` and `RccTokenManager`, parses grammar productions through `Rcc`, builds `JFile`, `JRecord`, `JField`, and `JType` instances, and finally emits generated code through `JFile.genCode()`. Parse failures flow through `ParseException`; lexical failures flow through `TokenMgrError`.

Record metadata flow uses `RecordTypeInfo` to build or read a schema description, stores each field as `FieldTypeInfo`, and uses `TypeID` subclasses to represent primitive or composite field shapes. Serialization and deserialization flow through `RecordOutput` and `RecordInput`, while `Utils.skip()` uses `TypeID` to advance past fields without materializing values.

Security group resolution flows through the `GroupMappingServiceProvider` interface. The JNI implementation delegates user/group lookup to native libc calls, while callers see a Java `List` result or `IOException`.

Kerberos SSL flow extends Jetty connector creation. The connector builds SSL server socket factories and sockets, customizes Jetty requests, and a servlet filter projects Kerberos principal state into servlet request handling. The documented behavior is stricter than the base connector because disabling need-authentication is not honored when Kerberos support is active.

SASL RPC authentication flow serializes an `AuthMethod` code to `DataOutput` and reconstructs it from `DataInput`. Callback handlers process JAAS callbacks for either token-based DIGEST-MD5 or Kerberos GSSAPI. SASL status enum values carry integer protocol state.

Tool execution flow runs generic Hadoop option parsing before delegating to `Tool.run(String[])`. `ToolRunner.run(conf, tool, args)` also installs the possibly modified configuration onto the tool.

Shell command flow fixes command, directory, environment, and timeout at construction, then `execute()` runs the process. Output is collected for `getOutput()` and can be parsed by overriding `parseExecResult()`. Non-zero exits surface through `ExitCodeException`.

Reflection utility flow instantiates classes and injects configuration when objects implement Hadoop configuration contracts. Writable copy and clone helpers flow through serialization buffers, so they exercise each object's `write` and `readFields` implementations.

Bloom filter flow hashes a `Key` to `nbHash` positions using `HashFunction`. Standard Bloom filters set or test those positions. Counting filters maintain counters and can delete keys if counters are positive. Dynamic filters add rows when the active row reaches the configured threshold. Retouched filters first collect known false positives, then clear selected bits according to a removal scheme, trading selected false-positive removal against possible false negatives.

## State and Persistence Behavior

The JDiff XML persists the public API surface and Javadocs for compatibility comparison. Runtime state belongs to the APIs described by the XML.

Record I/O serialization state is durable wire-format state. The binary, CSV, and XML encodings documented in this chunk must remain stable for legacy records to interoperate across languages and Hadoop versions. Changes to zero-compressed integer rules, UTF-8 normalization, escaping, or composite delimiters would break stored data and generated clients.

Record compiler state includes in-memory schema ASTs (`JFile`, `JRecord`, `JField`, `JType` subclasses), token streams, parse error context, code-generation buffers, and Ant task configuration. Generated source files are the main persistent side effect of `JFile.genCode()` and `RccTask.execute()`.

Generated parser state is mutable and public in several JavaCC classes. `Rcc` exposes `token_source`, `token`, and `jj_nt`; `ParseException` exposes current-token and expected-token data; `Token` exposes token image, location, next-token, and special-token links; `SimpleCharStream` exposes or protects buffer, position, line, column, and stream state. Compatibility consumers may observe or mutate these fields directly.

Record metadata state persists through `RecordTypeInfo.serialize()` and `deserialize()`. `TypeID` singleton constants share primitive type instances. Composite type IDs store nested type IDs or field collections. Equality and hash code are part of schema matching behavior even though Javadocs say the hash implementation is basic.

Security and token state includes group membership results, Kerberos principal/short-name request attributes, serialized SASL auth method codes, SASL QOP values, delegation token renew dates, and token passwords. `DelegationTokenInformation` stores password bytes in memory and exposes only the renew date in this slice.

Utility state includes typed option arrays, process-local progress callbacks, reflection constructor/configuration caches or behavior in implementation, shell executor command/output/timeout state, and thread dump logging intervals. `ToolRunner` mutates a tool's configuration before invoking `run()`.

Bloom filters persist probabilistic membership data through `Writable` `write` and `readFields`. Constructors marked "use with readFields" create empty objects for deserialization. Counting filters persist counters rather than bits, dynamic filters persist a matrix of rows and row thresholds, and retouched filters persist the base filter plus false-positive tracking or retouched state as implemented.

## Dependencies and Integration Points

The Record I/O compiler integrates with JavaCC-generated parser components, Ant `Task` and `FileSet`, Java `InputStream`, `Reader`, `File`, `ArrayList`, and `IOException`, and Hadoop Record I/O classes such as `Record`, `RecordInput`, and `RecordOutput`. The entire compiler and metadata surface is deprecated in favor of Avro, so migration and compatibility tooling need to recognize both APIs.

The security APIs integrate with Hadoop `Groups`, `UserGroupInformation`, `SaslRpcServer`, token `SecretManager`, IPC `Server.Connection`, JAAS callbacks, servlet filters, Jetty `SslSocketConnector`, Jetty `Request`, Jetty `EndPoint`, Java SSL socket factories, and Hadoop's binary RPC protocol streams.

The utility APIs integrate with `Configuration`, `Configurable`, Hadoop `Writable`, `FSDataInputStream`, `FSDataOutputStream`, `Path`, `Progressable`, Commons Logging `Log`, Java `PrintWriter` and `PrintStream`, shell process execution, and MapReduce-style command-line processing through `GenericOptionsParser`.

The Bloom filter APIs integrate with `org.apache.hadoop.util.bloom.Filter`, `Key`, `org.apache.hadoop.util.hash.Hash`, Java collections, and Hadoop `Writable` serialization through `DataInput` and `DataOutput`. The `org.apache.hadoop.util.hash` package marker at the end of the chunk has no public classes in this line range, but Bloom filters refer to hash implementations from that package.

## Risks and Edge Cases

- The chunk starts inside package documentation and not at a package boundary. Adjacent chunks are required to reconstruct the full `org.apache.hadoop.record` API documentation.
- JDiff metadata omits method bodies. Validation rules, exact serialization byte order for all composite metadata, parser grammar details, JNI behavior, Jetty customization details, and Bloom filter internal layouts require implementation-source review.
- Most Record I/O compiler and metadata APIs are deprecated but still public. Removing or changing them would break source or binary compatibility for legacy users even if Avro is the recommended replacement.
- The documented binary, CSV, and XML Record I/O formats are compatibility-critical. Escaping mistakes, malformed length prefixes, XML control-character handling, and composite delimiter parsing can corrupt cross-language data exchange.
- JavaCC-generated classes expose mutable public parser fields. External code could depend on or mutate `Token`, `ParseException`, or parser state directly.
- `RecordTypeInfo.compareTo()` has confusing documentation: it says the class is not meant to be comparable and also says it always returns 0 for another `RecordTypeInfo`. Tests need to pin actual behavior.
- `getNestedStructTypeInfo()` only considers one level of nesting, which is a schema traversal limitation.
- `JniBasedUnixGroupsMapping` depends on native libraries and host NSS/group configuration. Missing JNI support, platform differences, large group lists, and non-existing users are likely failure modes.
- Kerberos SSL connector behavior is security-sensitive. Accidentally honoring disabled client authentication while in Kerberos mode would weaken authentication.
- SASL auth method serialization depends on stable byte codes. Reordering or changing enum fields can break RPC negotiation.
- Callback handlers must reject unsupported callbacks and invalid tokens correctly; swallowing failures can authenticate the wrong user.
- `DelegationTokenInformation` stores password bytes. Copies, exposure, and lifecycle behavior need careful review outside this JDiff metadata.
- `Options.getOption()` returns the first matching dynamic class. Option ordering and subclass matching can change behavior when multiple typed options are present.
- `ReflectionUtils.copy()` uses serialization to destroy and refill the destination object according to its Javadoc. Callers must not assume object identity or prior destination state survives.
- `ShellCommandExecutor` expects small command output. Large outputs, timeouts, quoting, platform shell differences, and environment handling are risk points.
- `TraditionalBinaryPrefix.string2long()` can overflow for large values or unsupported symbols. Case-insensitive parsing needs explicit coverage.
- `Progressable` is often used to avoid framework timeouts. Callers that forget progress callbacks on long operations may be killed even if making progress.
- Bloom filters are probabilistic. Tests must account for false positives while still validating deterministic behavior for added keys, serialization, and operations on compatible filters.
- Counting Bloom filters can overflow 4-bit-style bucket limits after repeated insertions, as documented for counts above 15. Deletes after underflow can introduce false negatives.
- Dynamic Bloom filters must choose the active row correctly and preserve row thresholds across serialization.
- Retouched Bloom filters intentionally trade false positives for false negatives. Incorrect selective clearing strategy can degrade both membership accuracy and repeatability.

## Test Signals

Useful validation for this chunk should include:

- JDiff/XML checks that the line range remains well formed when combined with adjacent chunks and that every public class, interface, field, constructor, method, exception, visibility flag, final/static/abstract flag, and deprecation marker in this slice is stable.
- Record I/O binary serialization tests for zero-compressed int/long boundaries, negative values, float/double network byte order, UTF-8 string normalization, and raw buffer length/data round trips.
- CSV serialization tests for every primitive, percent escaping of null/newline/percent/comma, struct/vector/map delimiters, empty vectors and maps, nested composites, and malformed grammar rejection.
- XML serialization tests for primitive tags, struct member names, vector/map arrays, UTF-8 handling, percent escaping of disallowed characters and carriage returns, and binary buffer hex encoding.
- Record compiler tests that parse valid `.jr` files with modules, includes, records, fields, primitive types, vectors, and maps, then generate Java and C++ outputs to configured destinations.
- Ant `RccTask` tests for single `file`, nested `fileset`, default language/destination, `failonerror` true and false behavior, and build-exception propagation.
- Parser error tests for `ParseException.getMessage()`, expected token sequences, token image escaping, lexical errors from `TokenMgrError`, stream line/column tracking, backup, and reinitialization with reader/input-stream encodings.
- Record metadata tests for primitive singleton `TypeID` equality, composite `MapTypeID`/`VectorTypeID`/`StructTypeID` equality and hash code, `FieldTypeInfo` typed and object equality, `RecordTypeInfo` field addition, nested struct lookup, serialize/deserialize round trips, and `Utils.skip()` for each type.
- Group mapping tests for existing users, non-existing users returning an empty list, JNI library absence, IOException propagation, and platform-specific group ordering.
- Kerberos SSL connector tests for mode construction, cipher-suite availability, server socket factory creation, enforced client authentication, request customization, and servlet filter principal propagation.
- SASL tests for `AuthMethod` byte-code read/write round trips, mechanism name and authentication-method mapping, QOP string mapping, DIGEST-MD5 valid and invalid token callbacks, GSSAPI callbacks, unsupported callbacks, and SASL status integer state.
- Token tests for `InvalidToken` messages and `DelegationTokenInformation.getRenewDate()` with password-byte lifecycle review.
- Utility tests for each typed `Options` wrapper, first-match option lookup, option prepending order, progress callback invocation in long operations, reflection instantiation with configuration injection, Writable copy/clone behavior, and thread dump logging interval behavior.
- Shell tests for command success, non-zero exit codes, captured output, timeout killing, working directory and environment handling, `parseExecResult()` override behavior, and `toString()` quoting of spaced arguments.
- Binary prefix tests for every prefix symbol, case-insensitive parsing, negative values, whitespace trimming, invalid symbols, and overflow handling.
- `ToolRunner` tests for generic option parsing, configuration mutation, pass-through of application arguments, exit-code propagation, and generic usage output.
- Bloom filter tests for construction, add, membership, logical and/or/xor/not compatibility, `getVectorSize`, serialization round trips, string rendering, and rejection or behavior with incompatible filter parameters.
- Counting Bloom filter tests for deletion of present and absent keys, approximate counts, repeated insert overflow behavior above 15, underflow effects, and serialization.
- Dynamic Bloom filter tests for row growth after threshold `nr`, membership across rows, logical operations with compatible filters, and `readFields` construction.
- Retouched Bloom filter tests for adding false positives through all overloads, null false-positive no-op behavior, each `RemoveScheme` constant, selective clearing side effects, false-negative tradeoffs, and serialization.
