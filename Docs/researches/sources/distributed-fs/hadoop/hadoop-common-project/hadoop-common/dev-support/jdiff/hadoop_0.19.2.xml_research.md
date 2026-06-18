# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007303`: lines 1-6152, `Docs/researches/chunks/subset-b-007303_research.md`
- `subset-b-007304`: lines 6153-12404, `Docs/researches/chunks/subset-b-007304_research.md`
- `subset-b-007305`: lines 12405-18689, `Docs/researches/chunks/subset-b-007305_research.md`
- `subset-b-007306`: lines 18690-24884, `Docs/researches/chunks/subset-b-007306_research.md`
- `subset-b-007307`: lines 24885-30923, `Docs/researches/chunks/subset-b-007307_research.md`
- `subset-b-007308`: lines 30924-37251, `Docs/researches/chunks/subset-b-007308_research.md`
- `subset-b-007309`: lines 37252-43530, `Docs/researches/chunks/subset-b-007309_research.md`
- `subset-b-007310`: lines 43531-44204, `Docs/researches/chunks/subset-b-007310_research.md`

## Chunk Research

### subset-b-007303: lines 1-6152

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 1-6152

## Chunk Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.19.2, not implementation source. It covers the file header and API XML root, then the public API surface from `org.apache.hadoop.HadoopVersionAnnotation` through configuration, distributed cache, and the beginning of `org.apache.hadoop.fs`. The chunk ends inside `org.apache.hadoop.fs.RawLocalFileSystem.completeLocalOutput(...)`, so `RawLocalFileSystem` and later packages/classes are incomplete here.

Because this file is API XML, behavioral notes are inferred from package/class/member docs, signatures, inheritance, visibility, modifiers, checked exceptions, deprecation text, and fields rather than method bodies.

## Purpose

The file records the Hadoop 0.19.2 public API for compatibility comparison by JDiff. It preserves package names, class/interface names, constructors, methods, fields, inheritance, implemented interfaces, public/protected visibility, abstract/static/synchronized flags, exception declarations, and Javadoc text.

This chunk captures three broad surfaces: cluster-wide configuration loading and typed property access, MapReduce distributed cache localization, and the older `FileSystem` abstraction with local/checksum-aware filesystem support. It is useful when checking whether later Hadoop versions changed the contracts used by applications, filesystem plugins, MapReduce task setup, and tests.

## Important APIs and Types

### Version and Configuration

`org.apache.hadoop.HadoopVersionAnnotation` is a public annotation interface used as a package attribute for the version Hadoop was compiled with.

`org.apache.hadoop.conf.Configurable` defines the simple lifecycle contract for objects that accept a `Configuration`: `setConf(Configuration)` and `getConf()`.

`Configuration` is the main mutable configuration container. It implements `Iterable<Map.Entry<String,String>>` and `Writable`, so it can be iterated and serialized through Hadoop's binary `Writable` protocol. Constructors support default loading, disabling default resources, and cloning another configuration. Public methods include:

- Resource loading through `addResource(String)`, `addResource(URL)`, `addResource(Path)`, and `addResource(InputStream)`.
- Cache invalidation through synchronized `reloadConfiguration()`, which clears resource-derived values and final-parameter tracking while preserving values set directly through setters as overlays.
- Typed accessors/mutators for strings, raw values, ints, longs, floats, booleans, integer ranges, comma-delimited string collections/arrays, and classes.
- Class loading helpers `getClassByName`, `getClasses`, `getClass` overloads, and `setClass`.
- Local path/file selection through `getLocalPath` and `getFile`, which choose among directories listed in a property by hashing a requested path and create the selected directory if needed.
- Resource lookup through `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader`.
- `size`, `clear`, `iterator`, XML export with `writeXml`, classloader getters/setters, synchronized `setQuietMode`, debug `main`, and `Writable` `readFields`/`write`.

The class docs define the resource model: `hadoop-default.xml` and `hadoop-site.xml` are loaded by default unless disabled, later resources override earlier resources unless a property is final, and property values support variable expansion from other configuration keys and Java system properties. `Configuration.IntegerRanges` parses strings such as `2-3,5,7-` and tests inclusion. `Configured` is a base class storing a `Configuration` for other Hadoop components.

### Distributed Cache

`org.apache.hadoop.filecache.DistributedCache` exposes static helper APIs for MapReduce job-local cache setup. The core `getLocalCache(...)` overloads localize an HDFS/http/local URI to a task node, optionally unpacking archives and creating symlinks in the task working directory. They use `FileStatus`, modification timestamps, a base cache directory, the current work directory, and an `isArchive` flag.

Other APIs manage cache metadata in `Configuration`: `setCacheArchives`, `setCacheFiles`, `getCacheArchives`, `getCacheFiles`, localized path getters, archive/file timestamp getters and setters, `setLocalArchives`, `setLocalFiles`, `addCacheArchive`, `addCacheFile`, classpath helpers for files and archives, symlink enablement, URI fragment conflict checks, and `purgeCache()`. The docs emphasize that cached files are read-only for job duration, copied once per job per worker, archives may be unzipped/unjarred/untarred, jars can be added to task classpaths, and symlink names come from URI fragments.

### Filesystem Metadata and Streams

`org.apache.hadoop.fs.BlockLocation` implements `Writable` and stores hosts, names (`host:port`), offset, and length for a file block. `BufferedFSInputStream` wraps `FSInputStream` with `BufferedInputStream` while preserving `Seekable` and `PositionedReadable` behavior.

`ChecksumException` records checksum failures with a failing file position. `ChecksumFileSystem` extends `FilterFileSystem` and wraps a raw filesystem with sidecar checksum-file behavior. It exposes checksum path naming, checksum-file detection, checksum length calculations, bytes-per-checksum, open/create/append wrappers, replication/rename/delete/list/mkdirs delegation, local copy helpers, `startLocalOutput`/`completeLocalOutput`, and `reportChecksumFailure(...)`.

`ContentSummary` implements `Writable` for aggregate length, directory count, file count, namespace quota, space consumed, and space quota. It provides header and formatted string helpers.

`DF` and `DU` extend `org.apache.hadoop.util.Shell` and integrate with local shell commands. `DF` reports filesystem, capacity, used, available, percent used, and mount via Unix `df`. `DU` tracks local disk usage through Unix `du`, supports a refresh thread (`start`, `shutdown`), and lets callers increment/decrement a cached DFS-used value.

`FileChecksum` is an abstract `Writable` with algorithm name, byte length, byte value, and equality/hash semantics over algorithm plus bytes. `FileStatus` is a `Writable` and `Comparable` value object for client-side file metadata: length, directory flag, replication, block size, modification/access times, permission, owner, group, and `Path`. Equality/hash/ordering are based on path identity.

### `FileSystem`

`FileSystem` is a public abstract base class extending `Configured` and implementing `Closeable`. It is the central compatibility surface in this chunk. Important methods include:

- Static resolution and lifecycle: deprecated `parseArgs`, `get(Configuration)`, `getDefaultUri`, `setDefaultUri` overloads, deprecated `getNamed`, `getLocal`, `get(URI, Configuration)`, and `closeAll`.
- Abstract initialization/identity: `initialize(URI, Configuration)` and `getUri()`, plus deprecated `getName()`.
- Path handling and block locality: `makeQualified(Path)`, protected `checkPath(Path)`, and `getFileBlockLocations(FileStatus, long, long)`.
- Read/write creation: abstract `open(Path, int)`, convenience `open(Path)`, many `create(...)` overloads carrying overwrite, buffer size, replication, block size, progress callback, and `FsPermission`, plus `createNewFile`.
- Mutation: append overloads, `setReplication`, `rename`, deprecated and recursive `delete`, `deleteOnExit`, `processDeleteOnExit`, `mkdirs`, `setPermission`, `setOwner`, and `setTimes`.
- Discovery and metadata: `exists`, `isDirectory`, `isFile`, deprecated `getLength`, `getContentSummary`, abstract `listStatus(Path)`, filtered/multiple-path listing overloads, `globStatus` overloads, `getHomeDirectory`, abstract working-directory methods, `getUsed`, deprecated `getBlockSize`, `getDefaultBlockSize`, `getDefaultReplication`, abstract `getFileStatus`, and optional `getFileChecksum`.
- Local transfer helpers: `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, `moveToLocalFile`, `startLocalOutput`, and `completeLocalOutput`.

The docs position `FileSystem` as a generic abstraction implemented by local and distributed filesystems. The local implementation supports small clusters and tests; distributed implementations expose HDFS as a fault-tolerant, large-capacity single-disk abstraction. `FileSystem.Statistics` is a static nested class with bytes-read and bytes-written counters, increment methods, getters, and reporting. `FileSystem` holds a public static Commons Logging `LOG` and a protected final per-instance `statistics`.

### File Utilities and Delegation

`FileUtil` is a static file utility class. It converts `FileStatus[]` to `Path[]`, recursively deletes Java `File` trees, provides deprecated recursive delete over `FileSystem`, copies between filesystems and local files, merges a directory into one output file, converts paths for shell use, computes local disk usage, unzips and untars archives, creates local symlinks, runs `chmod`, creates temp files near a base file, and replaces files. `FileUtil.HardLink` creates hard links and reads link counts on Unix, Cygwin, and Windows XP.

`FilterFileSystem` wraps a protected `FileSystem fs` and delegates the visible `FileSystem` surface in this chunk: initialization, URI/name, path qualification, block locations, open/create/append, replication, rename/delete/list, working directories, mkdirs, local copy helpers, checksum lookup, configuration/lifecycle, ownership, and permissions. It is the main extension point for wrappers that transform data or behavior around another filesystem.

### Data Streams, Checksumming, and Shell

`FSDataInputStream` extends `DataInputStream` and implements `Seekable` and `PositionedReadable`, exposing synchronized `seek`, `getPos`, positional `read`, `readFully` overloads, and `seekToNewSource`. `FSDataOutputStream` extends `DataOutputStream`, implements `Syncable`, accepts optional `FileSystem.Statistics`, exposes `getPos`, close, wrapped-stream access, and deprecated `sync()`.

`FSInputChecker` extends `FSInputStream` and defines chunked checksum verification: subclasses provide `readChunk(...)` and `getChunkPosition(long)`, while the base class exposes `needChecksum`, read overloads, checksum conversion, position/available/skip/seek, positional `readFully`, checksum state reset through `set(...)`, and disables normal mark/reset semantics. `FSInputStream` itself is the abstract seekable/positioned input base. `FSOutputSummer` is the corresponding output helper that buffers data into checksum chunks, calls subclass `writeChunk(...)`, flushes buffers, converts checksums to byte streams, and resets checksum chunking.

`FsShell` extends `Configured` and implements `Tool`. It exposes initialization, current trash directory lookup, byte/decimal formatting helpers, `run`, `close`, and `main`, with public/protected fields for its `FileSystem` and date formatters. `FsUrlStreamHandlerFactory` integrates Hadoop filesystems with Java URL stream handling via `URLStreamHandlerFactory`.

### Archive, Memory, Local, Checksum, and Path APIs

`HarFileSystem` extends `FilterFileSystem` for Hadoop Archives. It initializes against an archive URI, exposes archive version, URI, working directory, qualification, block locations, archive hash, file status, open, and mostly read-only/erroring mutation methods. The signatures show no successful create/delete/mkdir ownership mutation contract in this API slice beyond inherited forms.

`InMemoryFileSystem` extends `ChecksumFileSystem`, reserves space including checksum overhead, and reports stored files, file count, filesystem size, and percent used.

`LocalDirAllocator` selects local directories named by a context configuration property. It returns paths for writing with or without known size, paths to read existing files, temp files for writing, context-validity checks, and existence checks. The docs describe it as an allocator over a set of writable local directories.

`LocalFileSystem` extends `ChecksumFileSystem`, exposes the raw underlying filesystem, converts `Path` to `File`, overrides local copy behavior, and reports checksum failures so bad data/checksum files can be quarantined.

`MD5MD5CRC32FileChecksum` is a concrete `FileChecksum` with a fixed length field, constructors over CRC-per-block, bytes-per-CRC, and `MD5Hash`, algorithm name/length/bytes accessors, `Writable` read/write, XML `valueOf(Attributes)`, and string conversion.

`Path` is the central URI-backed path value. Constructors support string parent/child, `Path` parent/child, string-only, and scheme/authority/path components. Methods expose `toUri`, filesystem lookup with `Configuration`, absolute check, final component, parent, suffix, string/equality/hash/compare, depth, and qualification with a `FileSystem`. Constants include `SEPARATOR`, `SEPARATOR_CHAR`, and `CUR_DIR`.

`PathFilter.accept(Path)` is the callback used by listing/globbing. `PositionedReadable` defines positional reads and full reads that must not change the stream's current offset and are documented as thread-safe.

### `RawLocalFileSystem` Beginning

The chunk ends inside `RawLocalFileSystem`. The visible portion extends `FileSystem` directly and exposes direct local-disk behavior: `pathToFile`, deprecated `getName`, `getUri`, `initialize`, `open`, `append`, `create` overloads with and without `FsPermission`, `rename`, delete overloads, `listStatus`, mkdirs overloads, home/working directory accessors, deprecated lock/release, `moveFromLocalFile`, `startLocalOutput`, and the start of `completeLocalOutput(Path fsWorkingFile, Path tmpLocalFile)`. Later `RawLocalFileSystem` methods are outside this chunk.

## Control Flow and Behavioral Contracts

Configuration flow starts with default and user-added XML resources. Later resources overlay earlier ones unless a prior resource marked a parameter final; direct `set` values overlay resource-derived values. `reloadConfiguration()` clears parsed resource state so values are read again lazily before later access.

Distributed cache flow starts with URI metadata placed into a job `Configuration`, then task setup localizes cache entries into a base directory, validates timestamps, unpacks archives when needed, optionally creates symlinks in the task working directory, and records localized paths back into configuration.

Filesystem resolution flows from `Path` and `Configuration` into `FileSystem.get(...)`; URI scheme maps to a configured implementation class and the whole URI is passed to `initialize`. Most client code then uses the abstract `FileSystem` API without depending on the concrete backend.

Read control flow is `FileSystem.open` to `FSDataInputStream` or a checker/buffered stream. Clients may perform sequential reads, explicit seeks, or positional reads; positioned reads are documented not to mutate the current offset. Checksum-aware reads flow through `FSInputChecker`, which reads data chunks and verifies checksums before returning bytes.

Write control flow is `FileSystem.create`/`append` to `FSDataOutputStream`, optionally with progress callbacks, replication/block-size/permission settings, checksum calculation through `FSOutputSummer`, byte statistics accounting, and `sync`/close lifecycle.

Copy and local-output flow is split between `FileSystem` convenience methods and `FileUtil`: data may move local-to-remote, remote-to-local, or filesystem-to-filesystem, optionally deleting sources. `startLocalOutput`/`completeLocalOutput` allow remote filesystems to stage output locally before final copy while local filesystems can write directly.

Delegation through `FilterFileSystem` is explicit: wrappers forward calls to an inner filesystem unless they override selected methods. `ChecksumFileSystem`, `HarFileSystem`, and `LocalFileSystem` build on this pattern.

## State and Persistence

Persistent and mutable state in this chunk includes:

- `Configuration` resource lists, direct key/value overlays, final-parameter tracking, classloader state, and serialized `Writable` representation.
- Distributed cache entries, timestamps, localized file/archive paths, classpath entries, and symlink settings persisted in `Configuration`, plus localized files on worker-local disks.
- `FileStatus`, `BlockLocation`, `ContentSummary`, `FileChecksum`, `MD5MD5CRC32FileChecksum`, and permission fields persisted via `Writable` where implemented.
- `FileSystem` implementations persist files and directories in their backing stores; this chunk shows local disk, checksum sidecar files, in-memory storage, and archive-backed read access.
- `FileSystem.Statistics` maintains process-local mutable byte counters for reads and writes.
- Streams maintain cursor positions; `FSOutputSummer` and `FSInputChecker` maintain checksum chunk state.
- `DU` maintains a cached disk usage value and an optional refresh thread; `DF` and `FileUtil` reflect local OS filesystem state through shell commands.
- `RawLocalFileSystem` state includes working directory/home handling and local `File` path conversion, though the class is incomplete in this chunk.

## Dependencies and Integration Points

Key dependencies visible in the API:

- Java core APIs: `java.io` streams/files/data input/output, `java.net.URI/URL/URLStreamHandlerFactory`, `java.util` collections, `java.util.zip.Checksum`, SAX `Attributes`/`SAXException`, and Java annotations.
- Hadoop core APIs: `Writable`, `MD5Hash`, `Configured`, `Configuration`, `Path`, `FileStatus`, `FsPermission`, `Progressable`, `Shell`, and `Tool`.
- MapReduce integration through `DistributedCache`, `JobConf`, mapper/reducer task working directories, classpaths, and task-local cache files.
- Commons Logging via public `LOG` fields.
- Local OS commands through `Shell`, `df`, `du`, symlink creation, hard-link support, and `chmod`.
- JDiff itself as the generated-format producer; consumers should treat this file as an API inventory, not runtime code.

The primary integration center is `FileSystem`: configuration chooses an implementation, `Path` resolves to it, streams depend on it for IO, `FileUtil` uses it for copies/deletes, and higher layers such as distributed cache and shell commands call into it for localization and user-facing operations.

## Risks and Edge Cases

- This XML does not contain method bodies, so exact synchronization, error handling, resource cleanup, cache eviction, shell command construction, and retry behavior must be checked in Java source.
- The chunk ends mid-`RawLocalFileSystem`; any final synthesis must merge the continuation before summarizing the complete local filesystem contract.
- `Configuration` variable expansion can draw from system properties, and final parameters can silently prevent later resource overrides.
- `reloadConfiguration()` is synchronized, but many getters/setters in the API are not marked synchronized; runtime thread-safety requires source confirmation.
- Distributed cache correctness depends on modification timestamps and URI fragments; missing or conflicting fragments break symlink behavior.
- Cached files are documented as read-only during job execution; external mutation can invalidate timestamp assumptions.
- `FileSystem.create(FileSystem, Path, FsPermission)` is documented as two RPCs: thread-safe but inefficient, and permission semantics intentionally avoid `permission & ~umask`.
- Glob/listing methods have subtle null versus empty-array behavior depending on whether a pattern has glob syntax.
- Deprecated APIs remain exposed: `FileSystem.parseArgs`, `getName`, `getNamed`, `delete(Path)`, `getLength`, `getBlockSize`, lock/release on raw local filesystems, and `FSDataOutputStream.sync`.
- `ChecksumFileSystem` sidecar files must be renamed/deleted/list-filtered together with data files; stale checksum files are a common compatibility risk.
- `FileUtil.fullyDelete(File)` can leave partially deleted directories on failure, and shell/permission/symlink/hard-link behavior is platform-sensitive.
- `FileStatus` equality and hash are path-based, not full metadata-based.
- `PositionedReadable` promises offset-preserving, thread-safe positional reads; implementations must honor that even if underlying streams are stateful.

## Test Signals

Useful test coverage inferred from this API slice:

- `Configuration` tests for default loading on/off, resource overlay order, final parameter protection, variable expansion, typed defaulting on malformed values, class loading/interface validation, `reloadConfiguration`, `Writable` round trips, and XML output.
- `Configuration.IntegerRanges` tests for singletons, bounded ranges, open-ended ranges, invalid syntax, and `toString`.
- Distributed cache tests for file and archive localization, timestamp mismatch rejection, localized path configuration, cache file/archive getters, classpath addition, symlink enable/disable, URI fragment conflict detection, and purge behavior.
- `BlockLocation`, `ContentSummary`, `FileStatus`, and checksum classes should have serialization, equality/hash, formatting, and null/default metadata tests.
- `FileSystem` contract tests for URI resolution, local filesystem lookup, path qualification/checking, create/open/append/rename/delete/mkdirs/list/status, working directory resolution, permission/owner/time mutation, checksum lookup, and close/closeAll behavior.
- Listing/globbing tests should cover filters, sorted output, missing non-glob paths returning null, glob patterns with no matches returning empty arrays, and multi-path listing conversions.
- Stream tests should cover seek, current-position reporting, positional read preserving offset, full reads, `seekToNewSource`, output position, sync compatibility, and statistics increments.
- `ChecksumFileSystem` tests should verify checksum sidecar naming, filtered listings, checksum length calculation, checksum failure handling, and paired rename/delete behavior.
- `FileUtil` tests should cover recursive delete partial failure, filesystem-to-filesystem and local copy variants, copy-merge, archive extraction, shell path conversion, symlink/chmod exit codes, temp file creation, replacement, hard-link creation, and link counts across supported platforms.
- `FilterFileSystem` delegation tests should verify each visible method forwards to the wrapped filesystem and preserves checked exceptions.
- `LocalDirAllocator`, `LocalFileSystem`, and visible `RawLocalFileSystem` APIs need tests for directory selection, local path conversion, staging output locally versus remotely, checksum failure quarantine, working directory changes, and deprecated lock/release compatibility.

## Chunk Boundary Notes

The following chunk is required for the rest of `RawLocalFileSystem`, `Seekable`, `Syncable`, `Trash`, FTP/KFS/permission/S3 filesystems, and later Hadoop IO APIs. The final per-file document should not treat this chunk as covering the complete `org.apache.hadoop.fs` package.

### subset-b-007304: lines 6153-12404

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 6153-12404

## Chunk Scope

This chunk is a generated JDiff API XML slice for Hadoop 0.19.2. It starts in the tail of `org.apache.hadoop.fs.RawLocalFileSystem`, covers seek/sync/trash APIs, concrete FTP/KFS/S3 filesystem adapters, filesystem permissions, filesystem shell commands, embedded HTTP server APIs, and a large portion of `org.apache.hadoop.io` through the beginning of `SequenceFile.Sorter.SegmentDescriptor`.

Because this is API metadata rather than Java implementation source, control-flow and state notes are inferred from public signatures, inheritance, synchronization flags, checked exceptions, field exposure, deprecation text, and embedded Javadocs.

## Purpose

The file records the public compatibility surface used by Hadoop's binary/API comparison tooling. This range is mostly about two subsystems:

- Filesystem-facing APIs: raw local metadata updates, seekable/syncable streams, trash retention, FTP/KFS/S3 filesystem implementations, permissions, shell command parsing/execution, and the Jetty-based status HTTP server.
- Hadoop serialization and sorted-file APIs: `Writable` containers, primitive writable keys, raw comparators, reusable byte buffers, `MapFile`, `SequenceFile`, object/string serialization helpers, and sort/merge contracts.

The chunk is useful for migration and regression research because it captures exactly which classes, constructors, fields, overloads, deprecations, and exception contracts existed in Hadoop 0.19.2.

## Important APIs and Types

### Filesystem Tail

The chunk begins inside `RawLocalFileSystem`, showing public `close`, `toString`, `getFileStatus(Path)`, `setOwner(Path, String, String)`, and `setPermission(Path, FsPermission)`. The owner and permission docs explicitly route through shell commands `chown` and `chmod`, so this backend exposes platform-sensitive local metadata behavior.

`Seekable` defines cursor movement for streams with `seek(long)`, `getPos()`, and `seekToNewSource(long)`. Its contract forbids seeking past EOF and allows switching to another data source when replicated data is available. `Syncable` exposes a single `sync()` operation for flushing buffers to underlying devices.

`Trash` extends `Configured` and provides per-filesystem deletion staging. It can `moveToTrash(Path)`, create checkpoints, `expunge()` old checkpoints, expose a superuser `Runnable` emptier, and run that emptier from `main`. The design preserves original paths under a user's `.Trash/current` directory and avoids requiring full trash enumeration, filesystem timestamps, or clock synchronization.

### FTP and KFS Filesystems

`FTPException` is a runtime wrapper for FTP failures. `FTPFileSystem` extends `FileSystem` and integrates Apache Commons Net through `initialize(URI, Configuration)`, `open`, `create`, `delete(Path[, boolean])`, `listStatus`, `getFileStatus`, `mkdirs`, `rename`, URI and working-directory methods, plus `LOG`, `DEFAULT_BUFFER_SIZE`, and `DEFAULT_BLOCK_SIZE`. `append` is documented as an unsupported optional operation. Its `create` contract warns that an output stream must be closed before other APIs are called, or operations may block.

`FTPInputStream` extends `FSInputStream` and wraps an `InputStream`, `FTPClient`, and filesystem statistics. It supports `getPos`, `seek`, `seekToNewSource`, synchronized byte reads, synchronized close, and mark/reset methods.

`KosmosFileSystem` extends `FileSystem` for KFS. It exposes URI/name/init methods, working directory mutation, `mkdirs`, `isDirectory`, `isFile`, `listStatus`, `getFileStatus`, unsupported `append`, `create`, `open`, `rename`, recursive and legacy delete overloads, length/replication/default replication/block size, `setReplication`, `lock`, `release`, `getFileBlockLocations`, local copy helpers, and local-output staging. Block locations are retrieved from KFS chunks and can return null if the file does not exist.

### Permissions

`AccessControlException` is a public `IOException` with default and string constructors; the default constructor exists for `RemoteException` unwrapping.

`FsAction` is an enum for filesystem read/write/execute combinations. It exposes `implies`, boolean-style `and`, `or`, `not`, plus public `INDEX` and `SYMBOL` fields for octal and symbolic representations.

`FsPermission` implements `Writable` and models user/group/other permissions. It supports construction from three `FsAction` values, a short mode, or another permission; immutable creation; action getters; `fromShort`; `write`/`readFields`; static `read(DataInput)`; `toShort`; equality/hash/string; `applyUMask`; static `getUMask`, `setUMask`, `getDefault`, and symbolic `valueOf(String)`. Public config fields include `UMASK_LABEL` and `DEFAULT_UMASK`.

`PermissionStatus` implements `Writable` for owner, group, and permission metadata. It supports immutable creation, getters, `applyUMask`, instance and static serialization helpers, static read, and string conversion.

### S3 Filesystems

`Block` holds a block id and length for the block-based S3 store. `FileSystemStore` is the backing-store interface for block S3: initialize, version lookup, inode/block storage and retrieval, existence checks, deletion, shallow/deep subpath listing, `purge()` for tests, and diagnostic `dump()`.

`INode` stores S3 file metadata: file type plus an array of `Block` pointers. It exposes type/block getters, directory/file predicates, serialized length, `serialize()`, static `deserialize(InputStream)`, `FILE_TYPES`, and `DIRECTORY_INODE`.

`MigrationTool` is a `Tool` for migrating older S3 filesystem metadata to newer versions by rewriting block metadata without touching data files. `S3Credentials` extracts access and secret keys from the filesystem URI or configuration and throws `IllegalArgumentException` when credentials cannot be determined. `S3Exception`, `S3FileSystemException`, and `VersionMismatchException` model S3 communication, filesystem, and store-version failures.

`S3FileSystem` is the block-based S3 `FileSystem`. It can be constructed with a custom `FileSystemStore` and implements URI/init/name, working directory, `mkdirs`, `isFile`, `listStatus`, unsupported `append`, `create`, `open`, `rename`, delete overloads, and `getFileStatus`. Permission parameters are documented as ignored for mkdir/create.

`NativeS3FileSystem` is the native-object S3 backend, constructed with or without a `NativeFileSystemStore`. It implements initialize, unsupported append, create, delete overloads, status, URI, listing, mkdirs, open, rename, working-directory methods, and `LOG`. Its doc distinguishes native S3 storage from the older block-based format so external S3 tools can read files directly.

### Shell and HTTP APIs

`org.apache.hadoop.fs.shell.Command` is an abstract `Configured` base for filesystem CLI commands. It stores protected `args`, requires `getCommandName()` and protected `run(Path)`, and provides `runAll()` to execute over each source path with `0` success and `-1` failure.

`CommandFormat` parses command options/parameters from an argument array and exposes `getOpt(String)`. `Count` implements the filesystem count command, with `matches(String)`, command name, protected path execution, and public `NAME`, `USAGE`, and `DESCRIPTION` fields. Its purpose is counting directories, files, bytes, quota, and remaining quota.

`FilterContainer` abstracts servlet filter registration. `FilterInitializer` is an abstract hook for initializing `javax.servlet.Filter` instances, but this chunk exposes only its constructor and class doc.

`HttpServer` embeds Jetty for status pages. It implements `FilterContainer` and exposes constructors with name/bind address/port/findPort and optional `Configuration`; default app/servlet/context setup; servlet and internal servlet registration; filter definition and path mappings; webapp attributes; webapp path lookup; port lookup; thread configuration; SSL listener setup; start/stop lifecycle. Protected/public fields expose `LOG`, Jetty `Server`, `WebApplicationContext`, default contexts, `findPort`, `SocketListener`, and filter names. `HttpServer.StackServlet` serves and logs current stack traces through `doGet`.

### Core IO Serialization

`AbstractMapWritable` is a `Writable`/`Configurable` base for map-like writables. Its per-instance class-id maps travel with the object instead of being static, allowing nested `MapWritable` values. IDs range from 1 to 127. It has synchronized `addToMap` and `copy`, protected class/id lookups, config accessors, and serialization.

`ArrayFile` extends `MapFile` as a dense long-index-to-value file. `ArrayFile.Reader` supports synchronized seek by index, next, current key, and random get. `ArrayFile.Writer` creates value-class-specific array files and synchronized appends, with optional compression/progress constructor.

`ArrayWritable` stores homogeneous `Writable[]` values, including a string-array constructor. It exposes value class, string conversion, Java array conversion, set/get, and `Writable` serialization. The doc warns reducer inputs often need typed subclasses.

`BinaryComparable` is an abstract byte-backed comparable. Subclasses provide `getLength()` and `getBytes()`, while common compare/equality/hash behavior delegates to byte comparison and hashing semantics.

Primitive writable wrappers include `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, and `LongWritable`. Each has default/value constructors, mutable `set`/`get`, `readFields`, `write`, equality/hash, `compareTo`, `toString`, and an optimized nested `WritableComparator`. `LongWritable.DecreasingComparator` reverses object and serialized-byte ordering.

`BytesWritable` extends `BinaryComparable` and implements `WritableComparable`. It distinguishes logical length from backing capacity, exposes `getBytes`, deprecated `get`, `getLength`, deprecated `getSize`, `setSize`, `getCapacity`, `setCapacity`, set-from-other/range, serialization, equality/hash, and hex-like string output. Its comparator compares serialized forms.

`Closeable` is a deprecated Hadoop alias for `java.io.Closeable`. `CompressedWritable` is an abstract lazy-compression base: final public `readFields` and `write` handle compressed payloads, while subclasses implement protected `readFieldsCompressed` and `writeCompressed`; callers accessing subclass fields must call `ensureInflated()`.

`DataInputBuffer`, `InputBuffer`, `DataOutputBuffer`, and `OutputBuffer` are reusable in-memory stream/data buffers. They reset over byte arrays or empty output state, expose backing data and valid lengths/positions, and support direct writes from `DataInput` or `InputStream`.

`DefaultStringifier<T>` uses Hadoop `SerializationFactory`, `Serializer`, and `Deserializer` to base64-encode serialized objects into strings. It implements `Stringifier<T>`, provides `fromString`, `toString(T)`, `close`, and static `store`, `load`, `storeArray`, and `loadArray` helpers for `Configuration` persistence.

`GenericWritable` wraps one of a fixed subclass-defined set of `Writable` classes. It is more compact than `ObjectWritable` because it serializes a type index instead of a class name per record, and it propagates configuration to wrapped `Configurable` values before deserialization.

`IOUtils` provides stream-copy overloads with explicit buffer size or `Configuration`, optional close behavior, `readFully`, `skipFully`, cleanup helpers that ignore close exceptions, and socket close helpers. `IOUtils.NullOutputStream` discards byte writes.

`MapWritable` extends `AbstractMapWritable` and implements `Map<Writable, Writable>`, exposing normal map operations plus serialized class-id-aware read/write. `MD5Hash` is a `WritableComparable` for 16-byte MD5 values, with constructors from hex or bytes, digest helpers over byte arrays, streams, strings, and `UTF8`, half/quarter digest conversions, hex parsing, and an optimized comparator. `MultipleIOException` wraps a list of IO failures and has a static factory that can collapse lists into a convenient `IOException`. `NullWritable` is a singleton zero-byte writable with comparator support.

`ObjectWritable` is a polymorphic `Writable`/`Configurable` that writes an instance with its declared class and handles `Writable`, `String`, primitives, and arrays. Static `writeObject` and `readObject` are central RPC/serialization integration points.

### MapFile and SequenceFile APIs

`MapFile` models a directory containing a `data` SequenceFile and an `index` file. Static methods rename, delete, repair a corrupt map by recreating its index (`fix`), and run a CLI `main`. Public constants are `INDEX_FILE_NAME` and `DATA_FILE_NAME`. The doc requires keys to be appended in order and notes that the index file is read entirely into memory.

`MapFile.Reader` is synchronized around read/navigation operations. It can open immediately or through a protected deferred-open constructor, override `createDataFileReader`, reset, compute a middle key, read final key, seek exact-or-next, iterate, get exact values, get closest before/after, and close. `MapFile.Writer` has many constructors for key class or comparator, compression type/codec, and progress. It exposes index interval getters/setters, static configuration storage for index interval, synchronized close, and synchronized append requiring nondecreasing keys.

`RawComparator<T>` extends `Comparator<T>` with a byte-array compare method for serialized objects, enabling sort paths that avoid deserialization.

`SequenceFile` exposes deprecated config-level compression get/set helpers and a broad set of static `createWriter` overloads for filesystem/path or raw output stream, key/value classes, buffer size, replication, block size, compression type, codec, progress, and metadata. `SYNC_INTERVAL` defines spacing between sync points. `CompressionType` is the enum-like compression mode.

`SequenceFile.Metadata` is a `Writable` wrapper around `TreeMap<Text, Text>` with get/set/map access, serialization, equality/hash, and string conversion.

`SequenceFile.Reader` implements `java.io.Closeable`, opens files through `FileSystem`/`Path`/`Configuration`, allows protected `openFile` specialization, exposes key/value class names and classes, compression flags/codecs, metadata, current value retrieval, typed and object-based `next`, raw key/value access, deprecated raw-next overload, seek, sync-to-next-sync-marker, `syncSeen`, current position, and file-name string conversion. Many read-position methods are synchronized.

`SequenceFile.Sorter` sorts and merges sequence files. It supports class-based or `RawComparator` constructors, merge fan-in factor, memory buffer sizing, progress callback, sorting input paths to output or iterator, backward-compatible single-file sort, multiple merge overloads returning `RawKeyValueIterator`, output writer creation by cloning input attributes, writing iterator records to a writer, and merge-to-output. Its doc warns key `readFields` implementations should avoid allocation for performance.

`SequenceFile.Sorter.RawKeyValueIterator` exposes current raw key/value, `next`, `close`, and a `Progress` object. The chunk ends just after the constructor doc starts for `SequenceFile.Sorter.SegmentDescriptor`, so the final per-file merge must reconcile that class from the next chunk.

## Control Flow and Behavioral Contracts

Filesystem control flow centers on `FileSystem` implementations accepting `Path` values, resolving backend-specific state in `initialize`, and returning `FSDataInputStream`/`FSDataOutputStream` wrappers for open/create. Optional operations like append are explicitly unsupported for FTP, KFS, S3, and native S3 in this range.

Seekable read flow is cursor-based: `seek` changes the next read position, `getPos` reports the current offset, and `seekToNewSource` can switch replicas/sources. FTP reads and closes are synchronized, indicating stream state and remote client state must be protected during read/close.

Trash flow moves a path to `.Trash/current`, checkpoints current trash, and expunges old checkpoints. The emptier is a long-running `Runnable` intended for superuser operation across users.

Permission flow encodes `FsAction` triples into short modes, applies umasks by returning new permission/status values, and serializes permissions through `Writable` methods for metadata persistence and RPC.

S3 block filesystem flow splits metadata and data: `S3FileSystem` manipulates Hadoop paths, `FileSystemStore` persists path-to-`INode` metadata and block objects, and `INode` serializes file type plus block references. Migration rewrites metadata only. Native S3 flow instead maps files to native S3 objects for interoperability.

HTTP server flow constructs Jetty contexts, registers default webapps/servlets/filters, sets webapp attributes for JSP access, optionally adds SSL, then starts/stops the embedded server. `findPort` controls port increment behavior during bind.

Writable control flow is conventional Hadoop serialization: write all fields to `DataOutput`, then restore them through `readFields(DataInput)`. Comparators operate directly on serialized byte arrays to support efficient sorting. `GenericWritable`, `ObjectWritable`, `MapWritable`, and `AbstractMapWritable` add type metadata around arbitrary or heterogeneous writable payloads.

MapFile/SequenceFile flow is sorted-file oriented. Writers append in key order, periodically emit index/sync metadata, and close files. Readers use in-memory indexes, seek/sync markers, typed or raw record iteration, and closeable streams. Sorter creates sorted runs, merges segments with configurable fan-in and memory, exposes raw iterators, and can clone output attributes from input sequence files.

## State and Persistence

Persistent state in this chunk includes filesystem data on local disk, FTP servers, KFS, block-based S3 metadata/data objects, and native S3 objects. `Trash` persists deleted paths and checkpoint directories under user home trash directories.

S3 block state is path-keyed inode metadata plus block files/objects. `Block` stores id/length, `INode` stores type and block list, and `FileSystemStore` persists or deletes both. `S3Credentials` holds access key and secret key values resolved from URI/configuration.

Permissions persist as compact short modes and owner/group strings through `FsPermission` and `PermissionStatus`. Umask lives in `Configuration` under `UMASK_LABEL`.

HTTP server state includes Jetty server/listener/context objects, filter mappings, default contexts, webapp attributes, and thread/listener settings.

IO state includes mutable primitive writable values, mutable buffer backing arrays and current lengths/positions, class-id maps in `AbstractMapWritable`, wrapped type indexes in `GenericWritable`, declared class/instance state in `ObjectWritable`, MD5 digest bytes, and closeable stream positions in MapFile/SequenceFile readers.

MapFile persistence is a directory with `data` and `index` files. SequenceFile persistence is a binary key/value format with compression type, optional codec, metadata, sync points, raw key/value records, and sort/merge temporary outputs.

## Dependencies and Integration Points

Visible dependencies include Java IO/networking (`InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `File`, `Socket`, `URI`, `InetSocketAddress`, `IOException`), Java collections/comparators, and servlet APIs.

Hadoop dependencies include `Configuration`, `Configured`, `Tool`, `Progressable`, `Progress`, `Path`, `FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSInputStream`, `FileStatus`, `BlockLocation`, `Writable`, `WritableComparable`, `WritableComparator`, `Stringifier`, `Text`, `UTF8`, and compression codecs.

External integrations include Apache Commons Net for FTP, Apache Commons Logging, Amazon S3 concepts and stores, KFS native/client integration, and Mortbay Jetty classes (`Server`, `SocketListener`, `WebApplicationContext`) for embedded status HTTP services.

The main integration points are stable public APIs: `FileSystem` backend contracts, shell command classes used by Hadoop CLI tooling, `HttpServer` used by daemons for status pages, and `Writable`/`SequenceFile`/`MapFile` used by MapReduce, RPC, and on-disk sorted data.

## Risks and Edge Cases

- This XML does not include method bodies, so exact exception branches, locking internals, and cleanup behavior must be verified against Java sources when changing behavior.
- The chunk starts mid-`RawLocalFileSystem` and ends mid-`SequenceFile.Sorter.SegmentDescriptor`; adjacent chunks are required for complete class-level synthesis.
- Raw local ownership and permissions depend on shell `chown`/`chmod`, which can vary by platform and user privileges.
- FTP create streams must be closed before other API calls, or later operations may block.
- FTP, KFS, S3, and native S3 append are unsupported despite the `FileSystem` append surface.
- S3 create/mkdir permission parameters are ignored, so callers expecting permission enforcement will get backend-specific behavior.
- Block-based S3 stores metadata and data separately; failed migrations or partial writes can leave inode/block inconsistency.
- Native S3 and block S3 have incompatible object layouts, so migration/interoperability assumptions must be explicit.
- `FileSystemStore.purge()` is test-oriented and destructive.
- `HttpServer.addInternalServlet` is deprecated as temporary; code relying on it is compatibility-sensitive.
- Jetty fields are protected/publicly visible enough for subclasses to couple tightly to old Mortbay classes.
- `AbstractMapWritable` supports only 127 distinct classes per map instance.
- `BytesWritable.getBytes()` returns backing storage, valid only through `getLength()`, and capacity may exceed logical data.
- `CompressedWritable` requires subclass field accessors to call `ensureInflated()`, or stale compressed state can be observed.
- `MapFile.Writer.append` requires nondecreasing keys; violations can corrupt sorted lookup assumptions.
- `MapFile` index files are loaded entirely into memory, creating risk with large keys or very dense indexing.
- `SequenceFile.Reader.seek(long)` requires a position returned by writer length during writing; arbitrary byte seeking must use `sync(long)`.
- Deprecated APIs remain part of the 0.19.2 compatibility surface, including old `delete(Path)` forms, Hadoop `Closeable`, and SequenceFile compression config helpers.

## Test Signals

Useful tests inferred from this API slice:

- Raw local filesystem tests for `getFileStatus`, close behavior, `setOwner`, and `setPermission`, including shell-command failure paths.
- `Seekable` tests for normal seek, EOF rejection, `getPos`, and `seekToNewSource` behavior across local and replicated/remote streams.
- `Trash` tests for disabled trash, already-in-trash paths, preserved original path layout, checkpoint creation, expunge, and superuser emptier scheduling.
- FTP filesystem tests for URI initialization, create/open/list/status/mkdir/rename/delete, unsupported append, statistics updates in `FTPInputStream`, and the documented stream-close-before-next-operation rule.
- KFS tests for lock/release, block locations, replication/defaults, local copy staging, unsupported append, and null locations for missing files.
- Permission tests for `FsAction` implication/and/or/not, short and symbolic `FsPermission` conversion, umask application, immutable permission/status creation, and `Writable` round trips.
- S3 block-store tests for inode/block store/retrieve/delete/list, inode serialization/deserialization, credential extraction precedence, version mismatch, metadata-only migration, ignored permissions, unsupported append, and destructive `purge` isolation.
- Native S3 tests for object-native create/open/list/delete/rename/mkdir/status behavior and unsupported append.
- Shell command tests for argument format bounds/options, `Count.matches`, `runAll` success/failure aggregation, and protected command execution over multiple paths.
- HTTP server tests for port finding, servlet/filter registration, webapp attribute access, default context setup, SSL listener configuration, lifecycle start/stop, and stack servlet response/log behavior.
- Writable tests for primitive wrappers, raw comparators, `BytesWritable` length versus capacity, `DataInputBuffer`/`DataOutputBuffer` reset and backing data validity, compressed writable lazy inflation, `GenericWritable` allowed-type indexes, `ObjectWritable` primitive/string/array handling, `MapWritable` class-id serialization, `NullWritable` singleton serialization, and `MD5Hash` digest/hex/ordering.
- MapFile tests for ordered append enforcement, reader seek/get/getClosest before and after keys, final/mid key retrieval, index interval configuration, corrupt-index `fix` dry run and repair, close idempotence, and dense `ArrayFile` indexing.
- SequenceFile tests for all writer overload families, metadata persistence, compression type/codec handling, raw and typed reader iteration, sync marker seeking, deprecated raw next compatibility, sorter fan-in/memory/progress behavior, merge delete-input behavior, cloned writer attributes, and raw iterator progress/close semantics.

## Chunk Boundary Notes

The previous chunk is needed for the full `RawLocalFileSystem` class and earlier filesystem APIs. The next chunk is needed for the body of `SequenceFile.Sorter.SegmentDescriptor` and later `org.apache.hadoop.io` classes. The final merge lane should preserve that this chunk is a partial view of both boundary classes and should avoid treating inferred control flow as implementation-confirmed behavior.

### subset-b-007305: lines 12405-18689

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 12405-18689

## Scope And Purpose

This chunk is a JDiff XML API snapshot for Hadoop 0.19.2, not production implementation source. It records the public and protected type surface, method signatures, fields, inheritance, interface implementations, deprecation metadata, checked exceptions, synchronization flags, and selected Javadoc for a large slice of `hadoop-common`. The research value is therefore compatibility-oriented: this file tells later comparison and migration lanes which APIs existed, which contracts were documented, and which behaviors downstream callers could reasonably depend on.

The slice starts in the middle of `org.apache.hadoop.io.SequenceFile.Sorter.SegmentDescriptor`, continues through the remainder of `org.apache.hadoop.io`, covers compression, retry, and serializer packages, then records Hadoop IPC/RPC APIs, RPC metrics/JMX APIs, runtime log-level control, and the start of `org.apache.hadoop.mapred.ClusterStatus`. The chunk ends before `ClusterStatus` is complete, so any final per-file report must reconcile the rest of that class with adjacent chunks.

Because the file is generated API metadata, it does not expose method bodies. Control flow, persistence, and risk notes below are inferred from signatures, type relationships, names, and embedded Javadocs in the XML.

## API Surface Covered

### `org.apache.hadoop.io` Boundary And SequenceFile APIs

The chunk begins inside `SequenceFile.Sorter.SegmentDescriptor`, a merge segment descriptor used by `SequenceFile.Sorter`. Visible APIs include `doSync`, `preserveInput(boolean)`, `shouldPreserveInput`, `compareTo(Object)`, `equals`, `hashCode`, `nextRawKey`, `nextRawValue(ValueBytes)`, `getKey`, and `cleanup`. The Javadoc states that cleanup closes file handles and deletes the file by default, with subclasses allowed to customize cleanup behavior. This makes the descriptor both an iteration primitive over sorted raw key/value data and a lifecycle owner for temporary merge segment files.

`SequenceFile.ValueBytes` is the raw-value interface used when copying values without fully deserializing them. It exposes `writeUncompressedBytes(DataOutputStream)`, `writeCompressedBytes(DataOutputStream)`, and `getSize`. The documentation explicitly says `writeCompressedBytes` does not compress uncompressed data, so callers must know whether the underlying bytes are already compressed.

`SequenceFile.Writer` is a public closeable writer for sequence-format files. Constructors accept `FileSystem`, `Configuration`, `Path`, key/value classes, optional replication/block-size arguments, `Progressable`, and `SequenceFile.Metadata`. Public methods include `getKeyClass`, `getValueClass`, `getCompressionCodec`, `sync`, synchronized `close`, synchronized `append(Writable, Writable)`, synchronized `append(Object, Object)`, synchronized `appendRaw(byte[], int, int, ValueBytes)`, and synchronized `getLength`. Protected fields expose the active key serializer plus uncompressed and compressed value serializers. The `getLength` doc is important: returned offsets are synchronized positions usable for `Reader.seek`, but with block compression the next readable key may be earlier than the most recently written key.

### Map-Like And Writable Data Types

`SetFile` is a file-backed set implemented as a `MapFile`. `SetFile.Reader` extends `MapFile.Reader` and exposes constructors with `FileSystem`, directory name, optional `WritableComparator`, and `Configuration`; it supports `seek`, `next`, and `get` for `WritableComparable` keys. `SetFile.Writer` extends `MapFile.Writer`, has constructors by key class or comparator and `SequenceFile.CompressionType`, and exposes `append(WritableComparable)`. The old writer constructor without `Configuration` is explicitly deprecated with the reason `pass a Configuration too`. The writer contract says appended keys must be strictly greater than the previous key.

`SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap<WritableComparable, Writable>`. It exposes the full sorted-map surface (`comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`, `clear`, `containsKey`, `containsValue`, `entrySet`, `get`, `isEmpty`, `keySet`, `put`, `putAll`, `remove`, `size`, `values`) plus `readFields` and `write`. This class is both an in-memory sorted map and a `Writable` serialization container whose keys and values must be Hadoop writable types registered through `AbstractMapWritable`.

`Stringifier<T>` is a small conversion interface with `toString(T)`, `fromString(String)`, and `close`. It provides a pluggable string serialization facade, likely used by configuration and tooling code.

`Text` is the primary UTF-8 text value type. It extends `BinaryComparable` and exposes constructors from empty, `String`, another `Text`, and byte array values. Important APIs include `getBytes`, `getLength`, `charAt`, `find`, several `set` overloads, `append`, `clear`, `toString`, `readFields`, static `skip`, `write`, `equals`, `hashCode`, static `decode`, static `encode`, static `readString`, static `writeString`, static `validateUTF8`, `bytesToCodePoint`, and `utf8Length`. `Text.Comparator` extends `WritableComparator` and compares byte ranges directly.

`TwoDArrayWritable` stores rectangular or jagged two-dimensional arrays of `Writable`. It exposes constructors by value class and optional `Writable[][]`, `set`, `get`, `toArray`, `readFields`, and `write`.

`UTF8` is the older string type. It implements `WritableComparable` and has constructors from empty, `String`, and `UTF8`; accessors and mutators include `getBytes`, `getLength`, `set(String)`, `set(UTF8)`, `readFields`, static `skip`, `write`, `compareTo`, `toString`, `equals`, `hashCode`, static `getBytes(String)`, `readString`, and `writeString`. The class is explicitly deprecated as `replaced by Text`, but `UTF8.Comparator` remains listed for raw comparison compatibility.

`VersionedWritable` is an abstract base for serialized types with a version byte. It exposes abstract `getVersion`, plus `write` and `readFields`. `VersionMismatchException` records expected and found version bytes and formats them in `toString`.

`VIntWritable` and `VLongWritable` are mutable variable-length integer wrappers. Both implement `WritableComparable`, provide default and value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`. They depend on Hadoop's variable-length integer encoding helpers.

`Writable` is the base serialization interface with `write(DataOutput)` and `readFields(DataInput)`. `WritableComparable` combines `Writable` and `Comparable`.

`WritableComparator` is the core comparison and raw-comparison utility. It has constructors for key class and optional instance creation, static comparator lookup/registration via `get` and `define`, `getKeyClass`, `newKey`, object and byte-array `compare` overloads, `compareBytes`, `hashBytes`, primitive byte readers (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`). This is a critical API for sort/shuffle paths because it can compare serialized keys without materializing Java objects.

`WritableFactories`, `WritableFactory`, and `WritableName` provide object creation and legacy name mapping. `WritableFactories` lets clients `setFactory`, `getFactory`, and create new writable instances by class and optional `Configuration`. `WritableFactory` exposes `newInstance`. `WritableName` maps classes to compact or stable names through `setName`, `addName`, `getName`, and `getClass`.

`WritableUtils` collects serialization helpers: compressed byte arrays and strings, string arrays, display helpers, cloning via `Configuration`, `cloneInto`, variable-length integer read/write, sign and encoded-size helpers, enum read/write by string, exact skipping, and conversion of writables to byte arrays. These helpers are wire-format sensitive and are used throughout Hadoop's IPC, metadata, and file formats.

### Compression APIs

`org.apache.hadoop.io.compress` defines the stream codec abstraction and concrete codecs.

`CompressionCodec` is the central interface. It creates compression and decompression streams with or without pooled `Compressor`/`Decompressor` instances, exposes compressor/decompressor implementation classes, creates new compressor/decompressor instances, and returns the default file extension. `CompressionCodecFactory` discovers codecs from `io.compression.codecs`, defaults to gzip and zip per Javadoc, maps filename suffixes to codecs, can read/write codec class lists in `Configuration`, strips suffixes, and includes a diagnostic `main`.

`CodecPool` is a global pool for reusing compressor and decompressor instances. Its APIs are `getCompressor`, `getDecompressor`, `returnCompressor`, and `returnDecompressor`. The pool exists to save allocation and native codec initialization cost, so callers must return objects after use and must not reuse objects after returning them.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases. Input streams wrap a protected final `InputStream`, require byte-buffer `read`, and expose `resetState` for repositioned underlying streams. Output streams wrap a protected final `OutputStream`, require byte-buffer `write`, and expose `finish` and `resetState`; `finish` writes remaining compressed data without closing the underlying stream.

`Compressor` and `Decompressor` define the codec state machines. `Compressor` supports `setInput`, `needsInput`, `setDictionary`, byte counters, `finish`, `finished`, `compress`, `reset`, and `end`. `Decompressor` mirrors this with `setInput`, `needsInput`, `setDictionary`, `needsDictionary`, `finished`, `decompress`, `reset`, and `end`. These APIs imply a loop in which callers provide bytes when needed, drain compressed/decompressed bytes, finish or detect end, then reset or end native state.

`BZip2Codec` implements `CompressionCodec` but documents that compressor/decompressor-object variants are unsupported and throw `UnsupportedOperationException`; it only creates BZip2 streams and advertises `.bz2`. `DefaultCodec`, `GzipCodec`, and nested `GzipInputStream`/`GzipOutputStream` expose standard stream creation, compressor/decompressor creation, extensions, available/read/write/skip/finish/reset/close lifecycle APIs.

`LzoCodec` implements configurable LZO compression and exposes `isNativeLzoLoaded`, stream creation, native compressor/decompressor creation, and extension. `LzopCodec` extends it for LZOP framing and includes nested `LzopDecompressor`, `LzopInputStream`, and `LzopOutputStream` APIs for header parsing/writing and checksum verification/reset. The LZO compressor/decompressor implementations in `org.apache.hadoop.io.compress.lzo` expose native-load checks, input/dictionary state, finish/finished, compress/decompress, byte counters, reset/end/finalize, `LZO_LIBRARY_VERSION`, and enum strategy types.

`org.apache.hadoop.io.compress.bzip2` exposes the BZip2 implementation details. `BZip2Constants` is public for historical reasons and includes public constants plus a public `rNums` array; its documentation explicitly warns that `rNums` should not be public because malicious code can modify it. `BZip2DummyCompressor` and `BZip2DummyDecompressor` implement the interfaces but are dummy implementations. `CBZip2InputStream` and `CBZip2OutputStream` implement raw BZip2 payload processing where callers are responsible for the outer `BZ` magic bytes. The output stream exposes block-size selection, `finish`, `close`, `flush`, write methods, block-size constants, and historically protected sorting constants.

`org.apache.hadoop.io.compress.zlib` includes wrappers around Java zlib and Hadoop native-aware factories. `BuiltInZlibDeflater` and `BuiltInZlibInflater` adapt `java.util.zip.Deflater` and `Inflater` to the Hadoop interfaces. `ZlibCompressor` and `ZlibDecompressor` expose synchronized stateful native compression/decompression methods, byte counters, reset/end/finalize, and enum types for compression header, level, and strategy. `ZlibFactory` chooses appropriate zlib implementations from `Configuration` and reports whether native zlib is loaded.

### Retry And Serialization APIs

`org.apache.hadoop.io.retry` defines retry policy construction and dynamic retry proxies. `RetryPolicies` exposes fixed-sleep, maximum-time, proportional-sleep, exponential-backoff, exception-map, and remote-exception-map policies, plus constants `TRY_ONCE_THEN_FAIL`, `TRY_ONCE_DONT_FAIL`, and `RETRY_FOREVER`. `RetryPolicy.shouldRetry(Exception, int)` returns whether to retry, whether to suppress failure for void methods, or throws the original/derived exception to fail. The interface documentation requires implementations to be immutable. `RetryProxy.create` wraps an implementation of an interface with either one policy for all methods or a method-name-to-policy map with a default `TRY_ONCE_THEN_FAIL`.

`org.apache.hadoop.io.serializer` defines generic serialization plug-ins. `Serializer<T>` has `open(OutputStream)`, `serialize(T)`, and `close`; `Deserializer<T>` has `open(InputStream)`, `deserialize(T)`, and `close`. The deserializer contract is explicit that instances are stateful but must not buffer input because other producers may read from the same stream between calls.

`Serialization<T>` accepts classes and returns serializers/deserializers. `SerializationFactory` extends `Configured`, loads implementations from the `io.serializations` configuration property, and returns matching serializers, deserializers, or the selected `Serialization`. `WritableSerialization` adapts Hadoop `Writable` by delegating to `Writable.write` and `Writable.readFields`. `JavaSerialization` is marked experimental and supports Java `Serializable`; `JavaSerializationComparator` and the abstract `DeserializerComparator` show how raw byte comparison can deserialize objects and then use normal `Comparator` logic, while warning that custom raw comparators are better for compare-heavy operations.

### IPC, RPC, Metrics, Logging, And MapReduce Status

`org.apache.hadoop.ipc.Client` is the low-level Writable RPC client. Constructors bind a `Writable` value class, `Configuration`, and optional `SocketFactory`. It exposes static `setPingInterval`, `stop`, single-call overloads with address and optional `UserGroupInformation`, and a parallel `call` over arrays of parameters and addresses. Parallel results may contain null for timed-out or errored calls.

`RemoteException` is a serializable wrapper for exceptions thrown by remote code. It records a class name and message, exposes `getClassName`, unwrap methods with optional lookup classes, XML serialization through `writeXml`, and reconstruction from SAX attributes via `valueOf`.

`RPC` is the higher-level proxy mechanism. It exposes `waitForProxy`, several `getProxy` overloads with protocol class, client version, address, optional user ticket, `Configuration`, and optional `SocketFactory`, `stopProxy`, an expert parallel reflective `call`, and `getServer` overloads to expose protocol implementation instances. The documentation defines the protocol restrictions: protocol methods are Java interface methods whose parameters and returns must be primitives, `String`, `Writable`, or arrays of those, and methods should throw only `IOException`. `RPC.Server` extends the generic `Server` and dispatches calls to an implementation instance. `RPC.VersionMismatch` records protocol/interface name, client version, and server version.

`Server` is the abstract IPC service. Constructors define bind address, port, parameter `Writable` class, handler count, `Configuration`, and optional server name. Static context APIs expose the current server, remote IP, and remote address while executing an RPC. `bind` wraps `ServerSocket.bind` with better `BindException` and `UnknownHostException` reporting. Instance APIs include socket send-buffer sizing, synchronized `start`, `stop`, `join`, synchronized `getListenerAddress`, abstract `call(Writable, long)`, connection and call-queue counters, public `HEADER`, `CURRENT_VERSION`, `LOG`, and protected `rpcMetrics`.

`VersionedProtocol` is the marker/super-interface for Hadoop RPC protocols. Implementations must expose `getProtocolVersion(String protocol, long clientVersion)` and are expected to have a static `versionID` field.

`org.apache.hadoop.ipc.metrics.RpcMetrics` implements `org.apache.hadoop.metrics.Updater`, registers RPC/JMX metrics, and exposes public mutable `MetricsTimeVaryingRate` fields for queue and processing times plus a metrics map. `RpcMgtMBean` exposes sampled operation counts, average/min/max processing time, average/min/max queue time, min/max reset, open connection count, and call queue length. Its documentation notes that the default null metrics context does not periodically update sampled averages unless configured with `NullContextWithUpdateThread`.

`org.apache.hadoop.log.LogLevel` provides runtime log-level adjustment. It exposes `main(String[])`, public `USAGES`, and a nested servlet `LogLevel.Servlet` with `doGet(HttpServletRequest, HttpServletResponse)`. This integrates both CLI and HTTP servlet control paths.

The chunk ends in `org.apache.hadoop.mapred.ClusterStatus`. Visible APIs include `getTaskTrackers`, `getMapTasks`, `getReduceTasks`, `getMaxMapTasks`, `getMaxReduceTasks`, `getJobTrackerState`, `write(DataOutput)`, and `readFields(DataInput)`. The class implements `Writable`, so the remaining adjacent chunk must complete its serialization and any additional status accessors.

## Control Flow And Data Flow Inferred From The API

SequenceFile and SetFile flows are file-format flows. Writers are constructed with filesystem/configuration/path/type metadata, append typed or raw key/value records, optionally emit sync points, report a synchronized seekable length, and close. Sorter segment descriptors iterate raw keys and values from sorted merge segments, optionally preserve temporary input, and clean up segment resources after merging. SetFile writes sorted keys as a MapFile-backed set and reads by seek, next, or exact get.

Writable serialization flows are `write(DataOutput)` followed by `readFields(DataInput)` into an existing object. `WritableComparator` and `Text.Comparator` allow sort and lookup code to compare raw serialized bytes directly, avoiding object allocation. `WritableFactories` and `WritableName` support deserializers that only know a class or legacy wire name and need to instantiate a writable before reading fields.

Text/UTF8 data flow centers on byte-backed UTF-8 storage. `Text` maintains a byte array plus logical length, supports setting from strings, byte slices, and other `Text` values, appending raw UTF-8 bytes, validating UTF-8, decoding/encoding through `ByteBuffer`, and reading/writing length-prefixed strings. `UTF8` remains for backward compatibility but should not be used for new APIs.

Compression flows have a consistent lifecycle: choose a `CompressionCodec` directly or through `CompressionCodecFactory`, optionally borrow a compressor/decompressor from `CodecPool`, create a compression/decompression stream, repeatedly write/read bytes, call `finish` when needed, close streams, reset state if reusing over repositioned streams, then return or end codec state. Native-capable codecs add load checks and configuration-driven implementation selection.

Retry flow is proxy-mediated. Client code wraps an implementation with `RetryProxy`; invocation failures are passed to the configured `RetryPolicy.shouldRetry` with the current retry count; the policy either allows another attempt, suppresses a void-method failure, or throws to fail the call. Remote-exception-aware policies can route based on wrapped remote exception class names.

SerializationFactory flow is configuration-driven. The factory reads a configured list of `Serialization` implementations, asks each whether it accepts a target class, then returns an appropriate `Serializer` or `Deserializer`. The serializer/deserializer lifecycle is explicit: open a stream, process one or more objects, close and release resources.

IPC flow is split between low-level Writable calls and protocol proxy calls. `Client.call` sends a Writable parameter to a `Server` address and receives a Writable result, while `RPC.getProxy` creates a Java dynamic proxy for a `VersionedProtocol`. Server-side code receives a Writable call parameter, dispatches through `Server.call` or `RPC.Server.call`, records queue/processing metrics, and exposes request context through static accessors. `RemoteException` carries remote failures across the wire and can be unwrapped into local IOException subclasses when possible.

Metrics flow is push-based through `RpcMetrics.doUpdates(MetricsContext)`, with JMX-facing values exposed through `RpcMgtMBean`. Log-level flow is command or servlet driven, changing logging configuration at runtime through `LogLevel`.

## State And Persistence Behavior

Persistent state in this chunk is mostly serialized byte streams and filesystem-backed Hadoop container formats. `SequenceFile.Writer`, `SetFile.Writer`, `MapFile` inheritance, and `ClusterStatus.write/readFields` all encode stable wire/file formats. Changes to field order, variable-length integer encoding, text length encoding, sync marker behavior, compression framing, or writable class names would break compatibility with data written by Hadoop 0.19.2.

`SequenceFile.Sorter.SegmentDescriptor` owns merge-segment state: path, offset, length, raw key buffer, reader position, sync behavior, and cleanup policy are implied by the API. The `preserveInput` flag controls whether temporary segment files are deleted when no longer needed, making it relevant to disk cleanup and post-failure debugging.

Compression classes hold mutable stream and native state. Compressor/decompressor objects track input buffers, dictionaries, finish flags, byte counters, and native resources; `reset` reuses them, while `end` releases resources. `CodecPool` adds process-global pooled state, so state leakage between users is a risk unless callers reset and return instances correctly. `CBZip2InputStream` documentation notes significant memory allocation and lack of thread safety.

`SortedMapWritable`, `VIntWritable`, `VLongWritable`, `Text`, and `UTF8` are mutable value holders. Reusing instances during deserialization is expected and efficient, but callers must avoid retaining references when later reads mutate the same object.

Retry policies are documented as immutable, while retry proxy instances keep invocation policy state externally through retry counts. `RetryPolicies.RETRY_FOREVER` can intentionally make calls persistent across transient failures but can also hide permanent failures.

IPC clients and servers own network connections, handler threads, call queues, socket buffers, metrics, and protocol version negotiation state. `Client.stop`, `Server.stop`, and `Server.join` are the lifecycle boundaries. Static server context (`Server.get`, remote IP/address accessors) is per-call ambient state and must be correct under concurrent handler threads.

`RpcMetrics` stores sampled queue and processing time state. Its public metric fields are intentionally mutable and readable by JMX. `RpcMgtMBean.resetAllMinMax` mutates min/max tracking state, and metrics update behavior depends on configured metrics context.

## Dependencies And Integration Points

This chunk sits at the intersection of most Hadoop common subsystems:

- Filesystem and file formats: `FileSystem`, `Path`, `SequenceFile`, `MapFile`, `SetFile`, sync points, sorted merge segments, and compressed sequence values.
- Configuration: `Configuration` configures writers, codecs, serialization factories, zlib/native behavior, IPC clients/servers, and metrics.
- Hadoop serialization: `Writable`, `WritableComparable`, `RawComparator`, `WritableComparator`, `WritableFactory`, `WritableName`, variable-length integer utilities, and text encoding utilities.
- Java IO and networking: `DataInput`, `DataOutput`, streams, `Closeable`, `ServerSocket`, `InetSocketAddress`, `InetAddress`, `SocketFactory`, and servlet request/response types.
- Compression libraries: Java zlib (`Deflater`/`Inflater`), Hadoop native zlib, LZO native bindings, LZOP framing, BZip2 stream implementation, and codec pooling.
- Reflection and proxies: `RPC`, `RetryProxy`, protocol interfaces, method dispatch, remote exception reconstruction, and version negotiation.
- Security/user identity: IPC call overloads accept `UserGroupInformation` tickets.
- Metrics and management: Hadoop metrics contexts, metrics utility rates, JMX MBean exposure, and runtime log-level servlet/CLI integration.
- MapReduce: `ClusterStatus` exposes job tracker and task capacity state through a `Writable` API consumed by MapReduce clients.

## Risks And Edge Cases

The biggest risk is treating this XML as implementation source. It is an API manifest: it can identify contracts and compatibility surfaces, but not actual branching, locking correctness, exception paths, or resource cleanup details beyond documentation and modifiers.

The chunk boundaries are partial. The start omits the class header and constructor details immediately before the visible `SegmentDescriptor` methods unless reconciled with the previous chunk. The end omits the tail of `ClusterStatus`, including the rest of `readFields` and any following methods or fields. A final merged report must not overstate completeness for those two boundary types.

Several APIs are wire-format sensitive. `WritableUtils` vint/vlong encoding, `Text` UTF-8 validation and string length handling, `UTF8` compatibility, `VersionedWritable`, `WritableName`, and `ClusterStatus` serialization must remain stable for old data and RPC compatibility. Even small changes can make old sequence files, map files, or IPC payloads unreadable.

Raw comparator APIs are performance and correctness critical. `WritableComparator.compareBytes`, primitive byte readers, `Text.Comparator`, and `DeserializerComparator` affect sorting, partitioning, map output shuffle behavior, and MapFile/SetFile ordering. Incorrect byte ordering or signedness handling can corrupt sorted-file invariants.

Resource lifecycle is prominent. `SequenceFile.Writer.close`, `SegmentDescriptor.cleanup`, `CompressionOutputStream.finish`, compressor/decompressor `reset` and `end`, `CodecPool.return*`, serializer/deserializer `close`, `Client.stop`, and `Server.stop/join` are all cleanup points. Leaks here would manifest as file descriptor leaks, native memory leaks, hanging IPC threads, or temporary file buildup.

Compression has many compatibility traps. BZip2 codec methods with compressor/decompressor arguments are documented as unsupported; code that assumes every `CompressionCodec` supports pooled codec objects will fail for BZip2. CBZip2 streams intentionally exclude the outer `BZ` magic bytes, requiring callers to handle headers exactly. LZO and zlib behavior depends on native libraries and configuration, so tests must cover native-loaded and fallback paths.

`BZip2Constants.rNums` is a public mutable array and the documentation calls out malicious modification risk. Any code relying on this constant must assume external mutation is possible in the same JVM.

Threading and synchronization differ by API. `SequenceFile.Writer` synchronizes append/close/getLength, zlib compressor/decompressor methods are partly synchronized, `CBZip2InputStream` is explicitly not thread-safe, and `Server.start/stop/join/getListenerAddress` are synchronized. Pooled compressors, serializers, and writable value instances should not be shared concurrently unless documented.

Retry policies can change failure semantics. `TRY_ONCE_DONT_FAIL` suppresses void-method failures, `RETRY_FOREVER` can hang indefinitely, and exception-map policies rely on local or remote exception classification. Misclassification can cause retry storms or premature failure.

RPC protocol constraints are narrow. `RPC` supports primitives, `String`, `Writable`, and arrays of those, with protocol methods expected to throw only `IOException`. Adding unsupported types or unchecked exception behavior can break proxy serialization or remote exception handling. `RPC.VersionMismatch` and `VersionedProtocol.getProtocolVersion` are central to rolling upgrades.

Metrics can be misleading if the metrics context does not periodically call updates. The MBean documentation explicitly warns that the default null context does not average sampled data unless configured with an update thread.

The explicit deprecations are important migration signals: new code should prefer `Text` over `UTF8`, and `SetFile.Writer` construction should pass `Configuration`.

## Test Signals

For this JDiff XML itself, useful validation is structural: XML parsing, package/type ordering, signature extraction, deprecation extraction, and comparison against adjacent JDiff versions. Tests should assert that expected classes, methods, fields, checked exceptions, synchronization flags, and deprecation messages are present.

For implementations described by this API surface, strong test signals include:

- SequenceFile tests that write/read typed and raw records, use sync points and `getLength`/seek, exercise block compression, sort/merge segments, verify `preserveInput` cleanup behavior, and confirm metadata and serializers are selected correctly.
- SetFile/MapFile tests that require strictly increasing keys, comparator-based lookup, `seek`, `next`, and exact `get` behavior.
- Writable tests that round-trip `Text`, `UTF8`, `VIntWritable`, `VLongWritable`, `SortedMapWritable`, `TwoDArrayWritable`, versioned writables, enum/string helpers, compressed strings, and variable-length integer edge cases.
- Raw comparator tests that compare serialized and object forms for the same keys, including negative numbers, multi-byte UTF-8, invalid UTF-8 rejection, and boundary byte slices.
- Compression tests for codec lookup by extension, codec class configuration, BZip2 unsupported pooled methods, CBZip2 header handling, gzip/default streams, LZO native availability, LZOP checksum/header behavior, zlib native/fallback factory selection, compressor reset/end, and `CodecPool` reuse.
- Retry tests that verify fixed, maximum-time, proportional, exponential, exception-map, remote-exception-map, no-retry, no-fail, and forever policies through `RetryProxy`.
- SerializationFactory tests that load configured serialization implementations, select `WritableSerialization` and `JavaSerialization`, and ensure deserializers do not over-buffer shared streams.
- IPC/RPC tests that cover direct Writable calls, parallel calls with timeout/error nulls, proxy creation and stop, protocol version negotiation, `VersionMismatch`, `RemoteException` unwrap/XML round-trip, server context remote address access, bind error quality, lifecycle stop/join, and call queue/open connection metrics.
- Metrics/JMX tests that call `RpcMetrics.doUpdates`, read `RpcMgtMBean` sampled values, reset min/max, and verify behavior under a null context versus an update-thread context.
- LogLevel tests that exercise both CLI argument handling and servlet `doGet` behavior.
- ClusterStatus compatibility tests that serialize with Hadoop 0.19.2-compatible data and read back task tracker counts, running map/reduce counts, max capacities, and `JobTracker.State`.

The merge/reconciliation lane should combine this chunk with neighboring chunks before making file-level claims about complete package coverage, especially for `SequenceFile.Sorter.SegmentDescriptor` and `ClusterStatus`.

### subset-b-007306: lines 18690-24884

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 18690-24884

## Scope and Purpose

This chunk is a JDiff API descriptor for Hadoop 0.19.2, covering a large section of the old `org.apache.hadoop.mapred` public API. It is documentation and signature metadata rather than executable Java source. The API surface described here centers on MapReduce job configuration, submission, job tracking, counters, input/output formats, job history, record readers, mapper execution, and split abstractions.

The chunk starts inside the tail of `ClusterStatus`, fully covers many `mapred` classes from `Counters` through `MultiFileInputFormat`, and ends partway through `MultiFileSplit`. Any whole-file synthesis should merge this with adjacent chunks for complete class boundaries.

## Important APIs, Types, and Functions

### Cluster and Counters

- `ClusterStatus` tail: exposes writable serialization via `write(DataOutput)` and `readFields(DataInput)`, plus cluster state inspection such as `getJobTrackerState()`. Its documented role is client-visible status for cluster size, map/reduce capacity, running tasks, and `JobTracker` state, normally queried through `JobClient.getClusterStatus()`.
- `Counters`: a synchronized `Writable` and `Iterable<Counters.Group>` container for global MapReduce counters. Important methods include `getGroupNames()`, `getGroup(String)`, `findCounter(Enum)`, `findCounter(String,String)`, deprecated `findCounter(String,int,String)`, `incrCounter(...)`, `getCounter(Enum)`, `incrAllCounters(Counters)`, `sum(Counters,Counters)`, `size()`, `write/readFields`, `log(Log)`, `toString()`, `makeCompactString()`, `makeEscapedCompactString()`, and `fromEscapedCompactString(String)`.
- `Counters.Counter`: synchronized writable counter record with internal name, display name, mutable value, `increment(long)`, and compact escaped string rendering.
- `Counters.Group`: writable iterable grouping counters by enum class or raw group name, with display-name localization hooks, `getCounter(String)`, deprecated numeric-id lookup, `getCounterForName(String)`, `size()`, serialization, and iteration.

### Input and Output Contracts

- `InputFormat<K,V>`: defines `getSplits(JobConf,int)` and `getRecordReader(InputSplit,JobConf,Reporter)`. The docs describe logical splits, assignment to mappers, and the `RecordReader` responsibility to preserve record boundaries.
- `InputSplit`: `Writable` interface with `getLength()` and `getLocations()`, representing a byte-oriented slice passed to a mapper.
- `FileInputFormat<K,V>`: abstract base for file-backed inputs. It provides path configuration (`setInputPaths`, `addInputPaths`, `addInputPath`, `getInputPaths`), optional `PathFilter`, `listStatus(JobConf)`, default split generation (`getSplits`), split sizing (`computeSplitSize`), block locality lookup (`getBlockIndex`), and overridable `isSplitable(FileSystem,Path)`.
- `FileSplit`: concrete `InputSplit` for one file region with path, start offset, length, host locations, serialization, and string conversion. The constructor taking `JobConf` is deprecated in favor of the host-array constructor.
- `MultiFileInputFormat<K,V>`: abstract file format that returns `MultiFileSplit` instances and attempts to construct splits of nearly equal content length from files under the configured input paths.
- `MultiFileSplit` partial: writable split containing arrays of `Path` and lengths, total length, per-index accessors, path count, locations, serialization, and `toString()`; this chunk cuts off before the class closes.
- `FileOutputFormat<K,V>`: abstract base for file-backed outputs. It controls output compression (`setCompressOutput`, `getCompressOutput`, compressor class setters/getters), output path, output spec validation, task temporary output paths, unique task-scoped names, and custom-file paths.
- `FileOutputCommitter`: concrete `OutputCommitter` for committing files under `${mapred.output.dir}` using a temporary directory name. It exposes job/task setup, cleanup, commit, abort, and `needsTaskCommit`.
- `MapFileOutputFormat`: `FileOutputFormat` producing `MapFile` output, with helpers to open generated readers and retrieve an entry through a `Partitioner`.

### Job Submission, Configuration, and Status

- `JobClient`: client-side interface to the `JobTracker`. It can initialize/close a tracker connection, get a `FileSystem`, submit jobs from a job file or `JobConf`, validate a job directory, retrieve `RunningJob` handles, get task reports, cluster status, all jobs or incomplete jobs, run a job synchronously, configure task output filtering, query default map/reduce capacities, system directory, queues, jobs in queues, and queue info. Deprecated string-based job ID overloads are preserved but point users toward `JobID`.
- `JobConf`: central `Configuration` subclass for describing old MapReduce jobs. It has constructors from defaults, classes, existing configs, XML paths, and load-defaults flag. It configures job jar, local dirs, reported user, keep-failed-task-file behavior, working directory, tasks per JVM, input/output format, output committer, compression, key/value classes, comparators, key-field comparator/partitioner options, mapper, map runner, partitioner, reducer, combiner, speculative execution, map/reduce counts, max attempts, tolerated failure percentages, priority, profiling, debug scripts, end-notification URI, job-local scratch directory, and queue name.
- `JobStatus`: writable/cloneable current status view with job ID, setup/map/reduce/cleanup progress, run state, start time, username, scheduling info, priority, completion check, and state constants `RUNNING`, `SUCCEEDED`, `FAILED`, `PREP`, and `KILLED`.
- `JobProfile`: writable metadata for a job, including user, typed `JobID`, job configuration file path, web UI URL, job name, and queue name. Deprecated string job-id access remains.
- `JobQueueInfo`: writable queue metadata with queue name and scheduling information, defaulting missing scheduling information to `"N/A"`.
- `JobPriority`: enum for job priority.
- `JobShell`: `Tool` wrapper for command-line job submission, including `-libjars`, `-archives`, `-files`, input jar, and arguments.
- `JobConfigurable`: interface for objects initialized from a `JobConf`.
- `JobContext`: exposes `JobConf` and a progress mechanism for committers and related job/task context code.

### Job Tracker and Runtime Coordination

- `JobTracker`: central service for submitting and tracking MapReduce jobs. It implements `MRConstants`, `InterTrackerProtocol`, `JobSubmissionProtocol`, and `TaskTrackerManager`. Public API includes `startTracker(JobConf)`, `stopTracker()`, protocol versioning, restart/recovery status and duration, instrumentation class configuration, tracker address, `offerService()` main loop, tracker identity/ports/start time, running/failed/completed jobs, task tracker collection and lookup, topology resolution, listener registration, queue manager, build version, synchronized `heartbeat(...)`, heartbeat interval calculation, filesystem name, task tracker error reporting, job ID allocation, job submission, cluster status, job kill/priority operations, job profile/status/counters, task reports, completion events, diagnostics, TIP lookup, task kill, assigned tracker lookup, all/incomplete jobs, system dir, localized job file path, queue APIs, and `main`.
- `JobTracker.IllegalStateException`: `IOException` for clients submitting before the tracker is ready.
- `JobTracker.State`: enum representing tracker state.
- `IsolationRunner`: command-line utility for running a single task from a task directory, useful for debugging isolated task execution.
- `JobEndNotifier`: static lifecycle and dispatch API for job completion notifications, including `startNotifier`, `stopNotifier`, `registerNotification(JobConf,JobStatus)`, and `localRunnerNotification`.

### Job History

- `JobHistory`: append-mode history facility with initialization, filesystem parsing through a listener, enable/disable flag, and task-log URL lookup. The documentation describes plain-text line records with record type plus key/value pairs, a master index of jobs, per-job history files named from jobtracker ID and job ID, and versioned escaping semantics.
- `DefaultJobHistoryParser`: parses a job history file from a `FileSystem` into a `JobHistory.JobInfo` object.
- `JobHistory.HistoryCleaner`: `Runnable` deleting history older than one month, updating the master index, and pruning jobtracker references with no recent jobs.
- `JobHistory.JobInfo`: key/value record model for job-level history and static logging helpers. It manages task maps, local/history file path discovery, URL encode/decode of history paths/names, username extraction, recovery file selection, and job lifecycle logging (`logSubmitted`, `logInited`, deprecated/modern `logStarted`, `logFinished`, `logFailed`, `logKilled`, priority and timing info).
- `JobHistory.Task`: logs task/TIP start, finish, failure, failed-due-to-attempt, and exposes task attempts.
- `JobHistory.TaskAttempt`: base class for map/reduce attempts.
- `JobHistory.MapAttempt` and `ReduceAttempt`: static helpers for start/finish/failure/kill events. Modern overloads add tracker name, HTTP port, task type, state string, counters, and for reduces shuffle/sort finish times. Older overloads using only host names are deprecated.
- `JobHistory.Keys`, `RecordTypes`, and `Values`: enums defining global namespaces for history keys, line record types, and common string values.
- `JobHistory.Listener`: callback API `handle(RecordTypes, Map<Keys,String>)` invoked by history parsing.

### Record Readers and Mapper Execution

- `LineRecordReader`: `RecordReader<LongWritable,Text>` treating file offsets as keys and lines as values. It supports constructors over `Configuration`/`FileSplit` or raw streams with start/end/max line length, `next`, progress, position, and close.
- `LineRecordReader.LineReader`: deprecated subclass of `org.apache.hadoop.util.LineReader`.
- `KeyValueLineRecordReader`: `RecordReader<Text,Text>` reading a line and splitting it into key/value by a separator byte configured with `key.value.separator.in.input.line`, default tab. It exposes `findSeparator`, key/value creation, next, progress, position, and close.
- `KeyValueTextInputFormat`: `FileInputFormat<Text,Text>` and `JobConfigurable` for text files split into lines, with key/value division by separator and empty value when the separator is absent. It can override splitability and create `KeyValueLineRecordReader`.
- `Mapper<K1,V1,K2,V2>`: application extension point that maps one input pair to zero or more intermediate pairs using `OutputCollector` and `Reporter`; it also inherits `JobConfigurable` and `Closeable`. Docs describe mapper lifecycle, one map task per input split, grouping/sorting/partitioning of intermediate output, combiners, SequenceFile-backed intermediate storage, compression, and direct filesystem output when reducers are zero.
- `MapReduceBase`: no-op base implementation of `close()` and `configure(JobConf)` for mapper/reducer implementations.
- `MapRunnable<K1,V1,K2,V2>`: expert interface for controlling map processing over a `RecordReader`, `OutputCollector`, and `Reporter`.
- `MapRunner`: default `MapRunnable` that configures and runs a mapper, with protected `getMapper()`.

### Exceptions and Identifiers

- `ID`: base writable comparable integer identifier for `JobID`, `TaskID`, and `TaskAttemptID`, with `getId`, comparison, equality, serialization, static `read`, and string parser `forName`.
- `JobID`: immutable unique job identifier with jobtracker identifier plus integer job number, typed serialization/parsing, comparison by tracker identifier then job number, and regex pattern helper for job IDs.
- `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException`: user-facing `IOException` subclasses for output overwrite conflicts, unexpected file types, aggregated input problems, and invalid/missing job configuration attributes. `InvalidInputException` preserves a list of underlying `IOException`s and summarizes messages.

## Control Flow and State Behavior

The described MapReduce flow is: users build a `JobConf`, set input and output paths/formats, mapper/reducer/combiner/partitioner/comparator classes, optional compression/debug/profiling/notification settings, then call `JobClient.submitJob` or `JobClient.runJob`. Submission validates input/output specs, computes `InputSplit`s, prepares distributed cache accounting, copies jar/configuration to the system directory on the distributed filesystem, submits to `JobTracker`, and optionally monitors completion.

At runtime, `FileInputFormat` lists input status entries and computes logical splits using desired split count, min split size, filesystem block size, and block locations. `InputFormat` instances produce `RecordReader`s, which feed key/value records to `Mapper` through a `MapRunnable` such as `MapRunner`. Mapper output is collected, optionally combined, partitioned by `Partitioner`, sorted/grouped with configured comparators, and sent to reducers unless the reducer count is zero, in which case map output is written directly to the output filesystem.

`FileOutputFormat` separates final output path from per-task work output path. With `FileOutputCommitter`, task attempts write under `${mapred.output.dir}/_temporary/_${taskid}` and successful attempts are promoted to the final output directory, while unsuccessful attempt directories are discarded. The docs emphasize speculative execution hazards and the need for unique task-attempt names for side-effect files unless using the work output directory.

`JobTracker` owns service lifecycle, heartbeats, job submission, task assignment, cluster and queue status, task diagnostics, job killing, priority changes, and topology-aware scheduling data. `TaskTracker` instances periodically call synchronized `heartbeat(...)` with status and receive instructions to start/stop tasks/jobs or reset. Heartbeat interval scales with cluster size by adding one second for every 50 nodes.

Job history is append-oriented: job, task, map attempt, and reduce attempt helpers log lifecycle events into text records. Parsing is streaming through `JobHistory.Listener`, allowing consumers to build a model or inspect selected records without holding the full file in memory.

## Persistence and Serialization

Most runtime DTOs implement Hadoop `Writable`: `Counters`, `Counter`, `Group`, `FileSplit`, `ID`, `JobProfile`, `JobQueueInfo`, `JobStatus`, `InputSplit` implementations, and `MultiFileSplit`. The chunk documents binary read/write APIs but not byte-level implementation details.

Persistent state surfaces include:

- Job configuration XML and user jar paths in `JobConf`.
- Job submission files copied to a JobTracker system directory on the distributed filesystem.
- Task temporary output directories and final output directories in `FileOutputFormat`/`FileOutputCommitter`.
- Local scratch and localized job paths under `${mapred.local.dir}/taskTracker/jobcache/$jobid/work/` and localized job conf file paths.
- Append-only job history files plus a master history index, with URL-encoded history filenames and recovery behavior choosing the oldest recovery file while leaving only one.
- User log/profile output directories for failed task files, debug script artifacts, task stdout/stderr/syslog/jobconf arguments, and profiling output.
- Queue, job status, counters, and split metadata serialized over RPC or stored in history/status records.

## Dependencies and Integration Points

This API section integrates with:

- Hadoop core types: `Configuration`, `Path`, `FileSystem`, `FileStatus`, `BlockLocation`, `PathFilter`, `Writable`, `WritableComparable`, `RawComparator`, `Text`, `LongWritable`, `MapFile`, `SequenceFile`, `CompressionCodec`, `Progressable`, and `LineReader`.
- MapReduce protocols and services: `JobTracker`, `TaskTracker`, `InterTrackerProtocol`, `JobSubmissionProtocol`, `TaskTrackerManager`, `HeartbeatResponse`, `TaskReport`, `TaskCompletionEvent`, `TaskInProgress`, `JobInProgress`, `QueueManager`, and `JobTrackerInstrumentation`.
- User extension points: `InputFormat`, `RecordReader`, `Mapper`, `MapRunnable`, `Reducer`, `Partitioner`, `OutputFormat`, `OutputCommitter`, `RawComparator`, `PathFilter`, debug scripts, job-end notification URI handlers, and distributed cache symlinks/files.
- Logging and diagnostics: Apache Commons Logging `Log`, `JobHistory`, task logs URL generation, counters, reporter progress/status, and profiler JVM arguments.
- Network topology: `org.apache.hadoop.net.Node` for resolving task tracker hosts and cache levels.

## Risks and Edge Cases

- This chunk is metadata-only; implementation details such as exact config keys, synchronization internals, serialization encoding, and error handling are inferred only from signatures and docs.
- Many APIs are synchronized on mutable status/counter objects. Incorrect external assumptions about thread safety can cause stale reads or lock contention, especially around `Counters`, `JobStatus`, `JobClient.close`, and `JobTracker` task/job query methods.
- Deprecated string-based job ID and counter numeric-ID APIs remain, creating compatibility burden and parsing risks. Callers should prefer typed `JobID` and string counter names.
- `JobConf.setNumMapTasks` is only a hint; actual map count is controlled by `InputFormat.getSplits`. Tests and user code that assume exact map counts from this setter can be wrong.
- Reducer count zero bypasses shuffle/sort and writes mapper output directly to the filesystem, which changes output ordering, committer behavior, and failure semantics.
- Speculative execution can cause multiple task attempts to write side-effect files. The docs warn that unique names or task work output paths are necessary to avoid collisions.
- Job history writes can be disabled globally if history file creation fails during `logSubmitted`; downstream history consumers need to tolerate missing or partial history.
- Job history parsing uses string key/value records with versioned escaping. Consumers should test special characters and old delimiter formats.
- `JobEndNotifier` and debug scripts invoke external URIs/scripts and depend on distributed cache symlinks; misconfiguration can silently break job chaining or failure diagnostics.
- `KeyValueLineRecordReader` depends on a single-byte separator; multi-byte delimiters or absent separators produce different key/value boundaries than users may expect.
- Compression class lookup can throw `IllegalArgumentException` if a configured codec class is missing.
- `FileOutputFormat.checkOutputSpecs` can fail when output exists or job config is invalid; overwrite behavior must be explicit elsewhere.
- `JobTracker.main` docs say it is used for debugging and normally should run as part of the DFS Namenode process, reflecting older Hadoop deployment coupling.
- This chunk cuts off mid-`MultiFileSplit`; any final report must avoid treating the class as fully covered until the next chunk is merged.

## Test Signals

Useful verification targets derived from this API surface:

- Serialization round trips for `Counters`, `Counters.Counter`, `Counters.Group`, `FileSplit`, `ID`, `JobID`, `JobProfile`, `JobQueueInfo`, `JobStatus`, and `MultiFileSplit`.
- Counter behavior: enum and string lookup identity, missing counter default `0`, display name mutation, localization fallback, compact and escaped compact string parse/render, and aggregate `sum`.
- `FileInputFormat` split generation with normal files, unsplittable compressed files, min split sizes, block boundaries, path filters, empty input sets, comma-separated path parsing, and `getBlockIndex`.
- `FileOutputFormat` output spec checks, compression toggles, compressor class resolution failure, task work output path creation, unique task names, and custom file path generation.
- Committer tests for setup/cleanup, successful task promotion, aborted task cleanup, speculative task side-file collision avoidance, and `needsTaskCommit`.
- `JobConf` default values and setters/getters for all major job knobs: input/output formats, classes, compression, comparators, speculative execution, task counts, attempts, failure percentages, profiling, debug scripts, notification URI, local dir, and queue.
- `JobClient` integration tests around submit, run-and-poll, job lookup by typed ID, task reports, queues, cluster status, and invalid job directory validation.
- `JobTracker` service tests for startup with port zero mutating config, heartbeat response IDs, task assignment/kill/fail behavior, queue APIs, topology resolution, restart/recovery flags, and synchronized report methods.
- Job history tests for submit/init/start/finish/fail/kill records, map/reduce attempt records with counters and tracker HTTP ports, URL encoding/decoding, recovery file selection, disabled-history mode, streaming listener parsing, and old deprecated overload compatibility.
- `LineRecordReader` and `KeyValueLineRecordReader` tests for split boundary line handling, CR/LF endings, max line length, separator placement, no separator, progress/position reporting, and close behavior.
- Mapper contract tests for reporter progress/status/counters, zero/many output records, custom `MapRunnable`, combiner integration, grouping comparator vs sort comparator behavior, and reducer-none direct output.

### subset-b-007307: lines 24885-30923

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 24885-30923

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.19.2, not implementation source. It covers a large portion of the classic `org.apache.hadoop.mapred` public API from the tail of `MultiFileSplit` through core output, partitioning, record reader/writer, reducer, reporter, running-job, sequence-file, skip-bad-record, task ID/report/log/TaskTracker, text format, jobcontrol, join, and early `mapred.lib` APIs. The range ends inside `org.apache.hadoop.mapred.lib.InputSampler.writePartitionFile`, so `InputSampler` is incomplete here and must be reconciled with the next chunk.

The XML records compatibility metadata: classes/interfaces, inheritance, implemented interfaces, constructors, methods, parameters, exceptions, fields, visibility/static/final/synchronized flags, deprecation text, and embedded Javadocs. The observations below are based on those API contracts and should be merged with adjacent chunks for whole-file conclusions.

## Purpose and Major API Surface

The opening boundary completes `MultiFileSplit`, documented as a split of whole input files rather than a byte range inside one file. It is intended for multi-file input formats and record readers that treat each file as an atomic record source.

The first full section defines the classic `mapred` output and task contracts. `OutputCollector.collect(K,V)` is the mapper/reducer emission sink. `OutputCommitter` defines job and task output lifecycle hooks: `setupJob`, `cleanupJob`, `setupTask`, `needsTaskCommit`, `commitTask`, and `abortTask`. `OutputFormat` validates output specifications with `checkOutputSpecs` and creates a `RecordWriter` through `getRecordWriter`. `OutputLogFilter` implements `PathFilter` and rejects `_logs` paths. `Partitioner.getPartition` maps an intermediate key/value pair to a reduce partition and extends `JobConfigurable`.

`RecordReader` and `RecordWriter` define old `mapred` streaming contracts. `RecordReader` exposes `next`, `createKey`, `createValue`, `getPos`, `getProgress`, and `close`. `RecordWriter` exposes `write` and `close(Reporter)`. `Reducer` extends `JobConfigurable` and Hadoop `Closeable`; its `reduce(K2, Iterator<V2>, OutputCollector<K3,V3>, Reporter)` contract documents shuffle, sort, grouping comparator, secondary sort, object reuse, progress reporting, and output collection. `Reporter` extends `Progressable` and lets tasks set status, access/increment counters by enum or group/name, fetch the map `InputSplit`, and use `Reporter.NULL`.

`RunningJob` is the client-facing handle for a submitted job. It provides typed `getID`, deprecated string `getJobID`, job metadata, tracking URL, setup/map/reduce/cleanup progress, completion/success checks, blocking `waitForCompletion`, state lookup, job kill, priority update, task completion event paging, typed and deprecated string task killing, and counter retrieval.

The sequence-file section exposes binary/text adapters and filtering. `SequenceFileAsBinaryInputFormat` and nested `SequenceFileAsBinaryRecordReader` read raw key/value bytes into `BytesWritable`, including key/value class-name access. `SequenceFileAsBinaryOutputFormat` configures real sequence-file key/value classes, validates output specs, and creates binary record writers; nested `WritableValueBytes` adapts `BytesWritable` to `SequenceFile.ValueBytes`. `SequenceFileAsTextInputFormat` and `SequenceFileAsTextRecordReader` convert sequence-file keys and values to `Text`. `SequenceFileInputFilter` extends `SequenceFileInputFormat` with a configurable `Filter`; visible filters include base configurable storage, MD5 frequency selection, percent frequency selection, and regex key matching. `SequenceFileInputFormat`, `SequenceFileOutputFormat`, and `SequenceFileRecordReader` expose ordinary sequence-file read/write, compression type configuration, reader arrays, seek, key/value class creation, position, progress, and close.

`SkipBadRecords` is a static configuration utility for Hadoop's skip mode. It controls the attempt count after which skipping starts, auto-increment behavior for mapper processed-record and reducer processed-group counters, skipped-record output path, mapper max skip records, reducer max skip groups, and publishes counter group/name constants. The Javadocs describe the runtime protocol: tasks report current record ranges to the TaskTracker, and failed ranges can be skipped on later attempts after repeated deterministic crashes.

Task identity, event, log, and tracker APIs form the state-management core of this chunk. `TaskAttemptContext` exposes the `TaskAttemptID` and `JobConf`. `TaskAttemptID` and `TaskID` extend `ID`, provide typed constructors, string parsing with `forName`, regex pattern helpers, `read` static constructors, `readFields`/`write`, equality, hash, ordering, `toString`, and map/reduce discrimination. `TaskCompletionEvent` is `Writable`, carries event id, attempt id, status enum, tracker HTTP location, run time, map-task/id-within-job helpers, deprecated string task-id accessors, and `EMPTY_ARRAY`. `TaskReport` is also `Writable` and reports typed/deprecated task id, progress, state text, diagnostics, counters, start/finish time, equality, and hash.

`TaskLog` exposes local task-log file/index lookup, sync, cleanup, log length, stdout/stderr/debug capture command construction, and command escaping/assembly. `TaskLog.LogName` is the enum for log stream names. `TaskLogAppender` is a Log4J `FileAppender` for task child logs with activation, append, flush, close, task-id, and total log file size configuration. `TaskLogServlet` serves task logs over HTTP and builds task-log URLs.

`TaskTracker` implements `MRConstants`, `TaskUmbilicalProtocol`, and `Runnable`. It exposes construction from `JobConf`, instrumentation class get/set, protocol version, storage cleanup, synchronized shutdown/close, JobTracker client lookup, report address, JVM manager, retry-loop `run`, child `getTask`, synchronized `statusUpdate`, diagnostic and next-record-range reporting, liveness `ping`, commit-pending and can-commit coordination, completion `done`, shuffle/local-fs/map-output-loss error reports, map completion event lookup, idle detection, `main`, task memory manager status/access, and logging/client-trace fields. Nested `TaskTracker.MapOutputServlet` serves map outputs to reducers.

`TextInputFormat` and `TextOutputFormat` provide line-oriented text integration. `TextInputFormat` is a `FileInputFormat<LongWritable,Text>` and `JobConfigurable`, with splitability and record-reader creation. `TextOutputFormat` is a `FileOutputFormat<K,V>` with a line record writer; nested `LineRecordWriter` writes key/value lines to a `DataOutputStream` using a separator and closes with a `Reporter`.

`org.apache.hadoop.mapred.jobcontrol.Job` models a configured job plus dependency list and state. It exposes constants `SUCCESS`, `WAITING`, `RUNNING`, `READY`, `FAILED`, and `DEPENDENT_FAILED`; getters/setters for job name, local job id, deprecated mapred job id string, typed assigned `JobID`, `JobConf`, state, message, `JobClient`, and dependencies; dependency addition; completion/readiness checks; and submission. `JobControl` is a `Runnable` orchestration loop over multiple `Job` objects, with named construction, lists by state, job addition, collection addition, controller state, stop/suspend/resume, all-finished check, and `run`.

The join package implements sorted composite input joins for the old `mapred` API. `ArrayListBackedIterator` and `StreamBackedIterator` implement `ResetableIterator` using in-memory list or byte-array-backed storage. `ComposableInputFormat` refines `InputFormat` to return `ComposableRecordReader`. `ComposableRecordReader` extends `RecordReader` and `Comparable`, adding reader id, current head key access/cloning, `hasNext`, key skipping, and collector acceptance for matching keys. `CompositeInputFormat` parses `mapred.join.expr`, applies default and user-defined join identifiers, validates child input formats, aligns child splits into `CompositeInputSplit`, constructs composable record readers, and offers static `compose` helpers. `CompositeInputSplit` stores a fixed set of child splits, reports aggregate/per-child lengths and locations, and serializes as count, class names, and split payloads.

`CompositeRecordReader` is the abstract base for join readers. It manages child readers, a priority queue sorted by `WritableComparator`, config, id, current key operations, skip, accept/fill-collector flow, combine hook, progress/position/close, and internal join collector state. `JoinRecordReader` emits `TupleWritable` combinations, with `InnerJoinRecordReader` and `OuterJoinRecordReader` specializing the `combine` policy. `MultiFilterRecordReader` emits a single value selected from multiple sources; `OverrideRecordReader` overrides/fills collector behavior for override semantics. Parser classes (`Parser`, `Parser.Node`, `NodeToken`, `NumToken`, `StrToken`, `Token`, `TType`) provide the expression parser and reflective mapping from join identifiers to composable record-reader constructors. `ResetableIterator`, `ResetableIterator.EMPTY`, `TupleWritable`, and `WrappedRecordReader` provide the buffering, empty iterator, tuple serialization/iteration, and normal-record-reader adapter used by the join framework.

The `mapred.lib` portion starts utility mappers/reducers and dispatch helpers. `ChainMapper` chains multiple `Mapper` classes inside the map task; `ChainReducer` chains a `Reducer` followed by zero or more `Mapper` classes inside the reduce task. Their static configuration methods record mapper/reducer classes, key/value classes, by-value versus by-reference passing, and per-stage `JobConf` overrides; lifecycle methods configure, invoke, and close the chain. `DelegatingInputFormat` and `DelegatingMapper` are MultipleInputs helpers that dispatch input paths to per-path input formats and mappers. `FieldSelectionMapReduce` is both mapper and reducer for configurable field extraction, driven by `mapred.data.field.separator`, `map.output.key.value.fields.spec`, and `reduce.output.key.value.fields.spec`. `HashPartitioner` partitions by `Object.hashCode`. `IdentityMapper` and `IdentityReducer` pass inputs through. `InputSampler` begins here as a `Tool`; visible APIs are constructor, `getConf`, `setConf`, and the start of static `writePartitionFile(JobConf, Sampler)`, which queries samples, sorts with the output key comparator, chooses partition keys, and writes a partition file.

## Control Flow and Behavioral Contracts

Output flow is separated into validation, writing, and commit. `OutputFormat.checkOutputSpecs` runs at job submission to prevent invalid or destructive output writes. Tasks obtain a `RecordWriter`, emit through `OutputCollector`/`RecordWriter`, and `OutputCommitter` mediates temporary output creation, task setup, commit necessity, successful promotion, abort, and final job cleanup. Correct implementations must tolerate retry/speculation semantics where only authorized attempts commit.

Reduce flow is explicitly three-phase: shuffle fetches relevant mapper partitions over HTTP, sort merges and groups by key, and reduce invokes user code once per grouped key. Secondary sort is achieved by separating partitioning, sort comparator, and grouping comparator. The contract warns that key/value objects are reused and that long-running reducers must call `Reporter.progress` or update status to avoid task timeout.

Running-job and TaskTracker control flows are RPC-heavy. Clients poll or block on `RunningJob`, fetch task completion events incrementally, kill jobs/tasks, and read counters. Task child JVMs call into TaskTracker for task assignment, progress, diagnostics, liveness, commit permission, completion, skip-mode range reporting, and error reporting. TaskTracker itself runs a reconnect loop against the JobTracker and has synchronized shutdown/close paths intended to stop tasks/threads and clean local state before restart in the same process.

Sequence-file readers/writers are record-stream adapters around Hadoop `SequenceFile`. Binary readers preserve raw serialized key/value bytes; text readers stringify keys/values; filters accept or skip keys by MD5, percentage, or regex. Record readers follow the standard create-key/create-value/next/progress/position/close lifecycle.

Skip-bad-record flow starts only after a configured number of failed attempts. Once active, tasks continuously report the next record/group range; after a crash the TaskTracker can identify the suspected bad range, and subsequent attempts skip or narrow that range until configured max-skip thresholds or attempt limits are reached. Applications that buffer or process asynchronously must disable automatic processed-record counter increments and increment the counters themselves.

JobControl flow is dependency-driven. Jobs wait until dependencies complete successfully, become ready, submit to MapReduce, move to running, and then settle into success or failed states. A dependency failure moves dependent jobs to `DEPENDENT_FAILED`. The controller loop can be suspended, resumed, or stopped, and exposes state-specific job lists.

Composite join flow starts with a string expression such as a join over `tbl(InputFormat,path)` leaves. The input format parses and reflectively resolves join nodes, gets child splits, aligns the ith split from every child into one composite split, and creates a reader tree. During reading, wrapped children maintain a head key/value, a priority queue orders children by comparator, matching values are accepted into resettable iterators, and join subclasses combine collected streams into tuples or selected values. The whole package assumes sources are sorted and partitioned identically.

Chain mapper/reducer flow executes multiple user stages inside one task JVM. Each stage may receive records by value, using serialization/deserialization to protect object ownership, or by reference for speed. Stage input/output key/value classes must match because the chain performs no conversion. `configure` initializes every stage and `close` tears them down.

## State, Persistence, and Side Effects

The JDiff file itself persists API surface for compatibility checking. Runtime state described by this chunk includes job output temporary directories, task output commit markers, output files, sequence files, skip-output records under output `_logs` by default, counters, task status text, task completion events, task IDs, task reports, local task logs and index files, TaskTracker local storage, map output files, task child processes, JobTracker/TaskTracker RPC state, text output streams, jobcontrol dependency/state lists, join expression configuration, composite split payloads, tuple serialization, resettable join buffers, chain configuration, and InputSampler partition files.

Several APIs have explicit binary serialization contracts. `TaskID`, `TaskAttemptID`, `TaskCompletionEvent`, `TaskReport`, `CompositeInputSplit`, and `TupleWritable` all implement or participate in `Writable` serialization. `CompositeInputSplit` writes child split count, classes, and payloads; `TupleWritable` writes child count, type list, and child objects while preserving populated positions. These formats are part of job submission and task runtime compatibility.

Configuration is a major persistence channel. `SkipBadRecords` stores thresholds, flags, paths, and max skip settings in `Configuration`/`JobConf`. `SequenceFileAsBinaryOutputFormat` stores output key/value classes. `SequenceFileOutputFormat` stores compression type. `CompositeInputFormat` stores `mapred.join.expr`, user-defined join identifiers, and key comparator. Chain APIs store stage classes, class contracts, by-value flags, and per-stage configs. Field selection stores separators and field specs. TaskTracker instrumentation class selection is also configuration-backed.

Task/log APIs perform filesystem and process side effects. Task logs are captured, indexed, synced, served over HTTP, and truncated/limited through appenders. TaskTracker cleanup removes temporary storage; close/shutdown stop children and background threads; map output servlet exposes local map output files to reducers.

## Dependencies and Integration Points

This chunk is centered on the old `org.apache.hadoop.mapred` API and integrates with `org.apache.hadoop.fs` (`FileSystem`, `Path`, `PathFilter`, `FileStatus`), `org.apache.hadoop.io` (`Writable`, `WritableComparable`, `BytesWritable`, `Text`, `LongWritable`, `SequenceFile`, `WritableComparator`), `org.apache.hadoop.conf` (`Configuration`, `Configurable`), `org.apache.hadoop.util` (`Progressable`, `Tool`), Java IO (`DataInput`, `DataOutput`, `DataOutputStream`, `IOException`, `File`), servlet APIs, Log4J, collections, regex, and Hadoop-internal MapReduce protocols.

TaskTracker and task status APIs integrate with JobTracker-facing protocols (`InterTrackerProtocol`, `TaskUmbilicalProtocol`), `JvmManager`, `JvmTask`, `JVMId`, `TaskStatus`, `SortedRanges.Range`, `MapTaskCompletionEventsUpdate`, `TaskMemoryManagerThread`, and instrumentation classes. The HTTP servlets integrate with the shuffle and log-serving paths.

JobControl sits above `JobClient`, `RunningJob`-style execution, `JobConf`, and typed Hadoop `JobID`. The join package depends on `InputFormat`, `InputSplit`, `RecordReader`, sorted `WritableComparable` keys, Hadoop comparators, reflective class loading, and correctly configured input paths. The `mapred.lib` utilities integrate with `Mapper`, `Reducer`, `OutputCollector`, `Reporter`, `MapReduceBase`, `MultipleInputs` patterns, and total-order partitioning via `InputSampler` partition files.

## Risks and Compatibility Notes

This is a compatibility artifact, so changes to signatures, generics, checked exceptions, visibility, static/synchronized/final flags, field constants, deprecation annotations, or Javadocs can indicate source or binary compatibility impact for Hadoop 0.19.2 clients.

The chunk has partial boundaries. `MultiFileSplit` starts before this range, and `InputSampler` continues after it. Whole-class conclusions for those APIs require adjacent chunks.

Task output commit and TaskTracker commit authorization are correctness-critical under retries and speculative execution. Bugs can allow duplicate commits, lost output, leaked temporary data, or committed output from a failed attempt.

Reducer, join, and chain APIs rely heavily on object reuse and type matching. Applications that retain reused keys/values without cloning, configure incompatible chain stage types, or join unsorted/mispartitioned inputs can silently corrupt output.

Skip-bad-record mode trades correctness for progress. Misconfigured counters, asynchronous processing without manual counter increments, overly broad max-skip thresholds, or incorrect range reporting can skip too much data or fail to isolate deterministic bad records.

Task identity string parsing and regex helpers are externally visible. Format drift in `task_...` or `attempt_...` strings can break logs, user tooling, task killing, and compatibility with deprecated string APIs.

Serialization formats for IDs, events, reports, composite splits, and tuples are fragile. Class-name encoding, child ordering, tuple slot occupancy, and default-constructor requirements for child splits must remain stable across job submission and task execution.

Composite joins use reflection and expression parsing. Invalid `mapred.join.expr`, unregistered join identifiers, incompatible comparators, different split counts, or non-public default constructors for child splits can fail jobs before or during task startup.

Task log serving and map-output serving expose local files over HTTP. Path construction, task id validation, log truncation, and map output loss handling are security and reliability-sensitive.

## Test Signals

JDiff-level validation should check that this XML range remains well formed, preserves class/interface boundaries, and retains method signatures, generic types, parameter order, declared exceptions, fields, deprecation text, and comments for `mapred`, `jobcontrol`, `join`, and `lib` APIs.

Output and record API tests should cover output-spec validation, existing-output rejection, record writer close semantics, output committer setup/commit/abort/cleanup ordering, `_logs` filtering, partitioner range bounds, record reader progress/position behavior, and reducer object reuse expectations.

Reporter and RunningJob tests should cover status/progress timeout prevention, enum and string counter increments, map-only `getInputSplit`, `Reporter.NULL`, job progress phases, blocking completion, kill job/task behavior, task completion event pagination, priority update, counters retrieval, and deprecated string method compatibility.

Sequence-file tests should cover binary raw-byte round trips, text conversion, configured binary output key/value classes, output compression type, filter class configuration, MD5/percent/regex acceptance, `SequenceFileRecordReader.seek`, key/value class creation, split boundaries, and reader/writer close behavior.

Skip-bad-record tests should cover default values, all getters/setters, skip-output path defaults and null disabling, attempt threshold activation, mapper/reducer auto-increment flags, manual counter behavior for buffered/asynchronous processors, max skip thresholds, range narrowing, and `Long.MAX_VALUE` no-narrowing behavior.

Task and TaskTracker tests should cover ID string parse/format/regex patterns, `Writable` serialization of IDs/events/reports, event id ordering, deprecated task-id accessors, task log path/index lookup, log capture command generation, log servlet URL/get behavior, TaskLogAppender size/task id configuration, TaskTracker cleanup-on-startup, close/shutdown idempotence, child `getTask`, status/diagnostic/range/ping/done callbacks, commit-pending/can-commit, shuffle/fs/map-output-loss reporting, map completion event lookup, idle detection, and memory manager access.

Text format tests should cover splitability, line offsets, record-reader progress, separator handling, null key/value rendering if supported by implementation, writer close, and interaction with configured output paths.

JobControl tests should cover state constants and transitions, dependency addition constraints, dependent failure propagation, job submission, assigned typed `JobID` and deprecated string IDs, ready/running/success/failed list maintenance, controller stop/suspend/resume, `allFinished`, and thread loop termination.

Join tests should cover `CompositeInputFormat.compose`, parser success/failure cases, default and user-defined join identifiers, split count alignment, `CompositeInputSplit` length/location/serialization, comparator configuration, inner/outer/override semantics, wrapped reader head-key caching and skipping, resettable iterator FIFO replay/reset/replay/clear/close behavior, stream-backed versus array-backed buffering, `TupleWritable` has/get/iterator/toString/write/readFields, and nested join false-positive `hasNext` behavior.

`mapred.lib` tests should cover chain mapper/reducer configure-map/reduce-close ordering, by-value versus by-reference object semantics, incompatible stage class failures, per-stage configuration precedence, MultipleInputs delegation by path, field-selection specs including reordered fields/ranges/open ranges, hash partition modulo behavior, identity mapper/reducer passthrough, and `InputSampler.writePartitionFile` sampling/sorting/partition-file output once the following chunk completes the API.

### subset-b-007308: lines 30924-37251

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 30924-37251

## Scope

This chunk is a Hadoop 0.19.2 JDiff API XML segment, not implementation source. It begins near the end of `org.apache.hadoop.mapred.lib.InputSampler`, covers the rest of the old `mapred.lib` helpers, aggregate and DB MapReduce adapters, Pipes job submission, the Hadoop metrics API/SPI and utility metrics classes, and the network utility package through the complete `SocketInputStream` declaration. The chunk ends at the opening of `org.apache.hadoop.net.SocketOutputStream`, whose members are outside this assigned range.

Because the source is generated API metadata, this research describes exported contracts, signatures, inheritance, deprecation markers, documented behavior, checked exceptions, and fields. Control flow, state, persistence, and risks are inferred from the public API and Javadocs visible in this XML rather than from method bodies.

## Purpose

The covered APIs expose a compatibility slice for Hadoop 0.19.2's classic `mapred` support libraries and common runtime services. The MapReduce section gives users reusable mappers, reducers, partitioners, multi-input/multi-output plumbing, total-order sampling, generic aggregation, JDBC input/output formats, and C++ Pipes submission controls. The metrics section defines how Hadoop components create metric contexts, create/update tagged metric records, register periodic updaters, send metrics to file or Ganglia sinks, count JVM/logging events, and implement provider-specific metrics backends. The network section defines DNS/rack mapping, socket factory selection, static host resolution for tests, network topology modeling, and channel-backed socket input with explicit read timeouts.

For compatibility work, the chunk is valuable because it captures old public names, overloads, configuration entry points, protected extension hooks, nested classes, and deprecated APIs that downstream code may still reference.

## Important APIs, Types, and Functions

### `org.apache.hadoop.mapred.lib`

`InputSampler` is partially visible at the start of the chunk. The visible tail includes command-line `run(String[])` and `main(String[])`, and documents that it configures a `JobConf` and writes a partition file for `TotalOrderPartitioner`.

`InputSampler.Sampler<K,V>` is the common interface for collecting representative input keys through an `InputFormat<K,V>` and `JobConf`. Implementations include:

- `IntervalSampler`, which samples records at regular intervals from all or a bounded number of splits. Its `getSample` emits keys when retained-record ratio is below the configured frequency, making it useful for already sorted data.
- `RandomSampler`, which randomizes split order, samples keys with a configured probability, caps total samples, and may replace earlier selected keys after a per-split quota is reached. Its docs warn that sampling all splits can be expensive because it reads them on the client.
- `SplitSampler`, which takes the first `numSamples / numSplits` records from each selected split, trading quality for low cost on random-looking inputs.

`InverseMapper<K,V>` extends `MapReduceBase` and implements `Mapper<K,V,V,K>`. Its `map` method swaps input key and value before collecting.

`KeyFieldBasedComparator` extends `WritableComparator` and implements `JobConfigurable`. It exposes `configure(JobConf)` and raw byte `compare(byte[], int, int, byte[], int, int)`. Its documented sort syntax is a Hadoop subset of Unix/GNU sort: numeric `-n`, reverse `-r`, and `-k pos1[,pos2]` field/character selection using `map.output.key.field.separator`.

`KeyFieldBasedPartitioner<K2,V2>` implements `Partitioner<K2,V2>`, with `configure(JobConf)`, `getPartition(K2,V2,int)`, and a protected byte-range `hashCode`. It partitions by the same field-position grammar documented for the comparator.

`LongSumReducer<K>` sums `LongWritable` values for a key.

`MultipleInputs` is a static configuration helper for jobs with different input paths using different `InputFormat` classes and optionally different `Mapper` classes. It writes the per-path input-format and mapper mapping into `JobConf`.

`MultipleOutputFormat<K,V>` is an abstract `FileOutputFormat` for deriving output file names and actual key/value pairs per record. Public `getRecordWriter` creates a composite writer. Protected hooks include `generateLeafFileName`, `generateFileNameForKeyValue`, `generateActualKey`, `generateActualValue`, `getInputFileBasedOutputFileName`, and abstract `getBaseRecordWriter`. The docs call out three use cases: reducers writing different files by key/value, map-only output names derived from input file paths, and map-only names based on both input files and keys.

`MultipleOutputs` is a runtime/configuration helper for named outputs. Static APIs define named outputs, multi-named outputs, key/value/output format classes, counter enablement, and listing of configured names. Instance APIs create `OutputCollector`s for a single named output or a multi-named output and close all opened writers. Named-output writes from a mapper bypass the reduce phase; only records collected to the mapper's normal output collector continue to reducers. Counters are optional and grouped under the `MultipleOutputs` class name.

`MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` specialize `MultipleOutputFormat` by implementing `getBaseRecordWriter` with SequenceFile and text output semantics.

`MultithreadedMapRunner<K1,V1,K2,V2>` implements `MapRunnable`, with `configure(JobConf)` and `run(RecordReader, OutputCollector, Reporter)`. It uses a configurable thread pool (`mapred.map.multithreadedrunner.threads`, default 10) and requires mapper implementations to be thread-safe.

`NLineInputFormat` extends `FileInputFormat<LongWritable,Text>` and implements `JobConfigurable`. `getSplits` groups N input lines per split, `getRecordReader` reads those splits, and `configure` pulls split sizing from `JobConf`. Its documented use case is parameter-sweep jobs where each mapper receives one or more control-file lines.

`NullOutputFormat<K,V>` implements `OutputFormat` and discards all output through a no-op `RecordWriter`.

`RegexMapper<K>` emits `Text,LongWritable` counts for regex matches in `Text` values, configured from `JobConf`. `TokenCountMapper<K>` tokenizes `Text` values with `StringTokenizer` and emits token frequency pairs.

`TotalOrderPartitioner<K,V>` implements `Partitioner` and reads an externally generated sorted partition key SequenceFile. `configure(JobConf)` builds either a trie for natural-order `BinaryComparable` keys or a binary-search keyset using the job's `RawComparator`. Static `setPartitionFile(JobConf, Path)` and `getPartitionFile(JobConf)` configure the split-point file. `DEFAULT_PATH` is the public default partition-file path.

### `org.apache.hadoop.mapred.lib.aggregate`

The aggregate package defines old generic aggregation jobs. `ValueAggregator` is the minimal protocol: `addNextValue(Object)`, `reset()`, `getReport()`, and `getCombinerOutput()`.

Concrete aggregators include `DoubleValueSum`, `LongValueMax`, `LongValueMin`, `LongValueSum`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram`. Numeric aggregators parse object string representations and expose typed getters such as `getSum()` or `getVal()`. String max/min track lexical extrema. `UniqValueCount` keeps a bounded set of unique objects with `setMaxItems(long)` and `getUniqueItems()`. `ValueHistogram` accepts values in `value\tcount` form, emits summary statistics and detailed frequency pairs, and exposes a `TreeMap` view.

`ValueAggregatorDescriptor` generates aggregation id/value entries from input key/value pairs and is `JobConfigurable`. `ValueAggregatorBaseDescriptor` supplies static helpers such as `generateEntry` and `generateValueAggregator`, descriptor list management, default user descriptor discovery, and default `generateKeyValPairs`.

`UserDefinedValueAggregatorDescriptor` wraps a dynamically loaded descriptor class name, creates an instance, delegates `generateKeyValPairs`, and implements `configure(JobConf)` as a no-op wrapper-level operation.

`ValueAggregatorJobBase<K1,V1>` is the common mapper/reducer base that configures the descriptor list. `ValueAggregatorMapper` emits aggregation id/value pairs generated by descriptors and has a no-op reducer. `ValueAggregatorReducer` consumes `Text` keys whose prefixes encode aggregation type, aggregates `Text` values using the selected `ValueAggregator`, and has a no-op mapper.

`ValueAggregatorCombiner` performs combiner-side aggregation with `Text` keys and `Text` values. `ValueAggregatorJob` configures and runs aggregate jobs, including static `createValueAggregatorJob` overloads and `main`. `ValueAggregatorJobBase` and job helpers are integration points between user descriptors, `JobConf`, `Mapper`, `Reducer`, and aggregate output.

### `org.apache.hadoop.mapred.lib.db`

`DBConfiguration` is a container for public configuration property names and static `configureDB` overloads. It stores JDBC driver, URL, optional username/password, input table/query/count-query/class fields, input field names/conditions/order, and output table/field names.

`DBInputFormat<T extends DBWritable>` implements `InputFormat<LongWritable,T>` and `JobConfigurable`. It has `configure`, `getSplits`, `getRecordReader`, protected `getCountQuery`, and two static `setInput` overloads: one for table plus fields/conditions/order and one for explicit input query plus count query. It emits row numbers as `LongWritable` keys and user `DBWritable` tuple objects as values.

`DBInputFormat.DBInputSplit` implements `InputSplit`, stores start/end row offsets, returns length, no location affinity, and serializes with `readFields(DataInput)` and `write(DataOutput)`.

`DBInputFormat.DBRecordReader<T>` implements `RecordReader<LongWritable,T>`, is constructed from a split, tuple class, and `JobConf`, exposes protected `getSelectQuery`, and supports `createKey`, `createValue`, `next`, `getPos`, `getProgress`, and `close`.

`DBInputFormat.NullDBWritable` implements both `DBWritable` and Hadoop `Writable` with no-op read/write methods for SQL and binary serialization.

`DBOutputFormat<K extends DBWritable,V>` implements `OutputFormat`. Protected `constructQuery` builds the SQL insert statement, `checkOutputSpecs` validates output configuration, `getRecordWriter` returns a writer, and static `setOutput` records output table and fields. Its `DBRecordWriter` writes only the key object to a `PreparedStatement`, then closes/commits via its connection and statement.

`DBWritable` is the tuple contract: `write(PreparedStatement)` and `readFields(ResultSet)`. Implementations usually also implement Hadoop `Writable` to participate in MapReduce serialization.

### `org.apache.hadoop.mapred.pipes`

`Submitter` extends `Configured` and implements `Tool`. It is the command-line and API entry point for Hadoop Pipes jobs. Static configuration helpers get/set the C++ executable URI, booleans for Java record reader, mapper, reducer, and record writer usage, and whether to keep the debugging command file (`downlink.data`) in task directories. `submitJob(JobConf)` is deprecated in favor of `runJob(JobConf)`. `runJob` mutates the job configuration for Pipes and submits it. `jobSubmit` submits to the MapReduce framework and returns a `RunningJob`. Instance `run(String[])` and static `main(String[])` provide CLI integration. A protected static `LOG` field is exposed.

### `org.apache.hadoop.metrics`

`ContextFactory` is the singleton factory for `MetricsContext` instances. It stores attributes, loads `hadoop-metrics.properties` from the classpath, and constructs a named context using `<contextName>.class`, defaulting to `org.apache.hadoop.metrics.spi.NullContext` when no class is configured. Attribute management uses `getAttribute`, `getAttributeNames`, `setAttribute`, and `removeAttribute`; `getContext` is synchronized and may throw class-loading and construction exceptions. `getNullContext` returns a no-op context.

`MetricsContext` defines monitoring lifecycle and updater registration: `startMonitoring`, `stopMonitoring`, `isMonitoring`, `close`, `createRecord`, `registerUpdater`, and `unregisterUpdater`. `DEFAULT_PERIOD` is the public default emit period in seconds.

`MetricsRecord` is the main mutable record API. It supports overloaded `setTag` for string and integer-like values, `removeTag`, overloaded `setMetric` and `incrMetric` for numeric values, `update`, and `remove`. The docs define records as named rows with zero or more tags and metrics. `update()` atomically updates or creates a buffered row matching the current tag set; `remove()` removes matching buffered rows. Separate `MetricsRecord` instances can safely update the same row concurrently, but the same instance should not be shared by threads.

`MetricsException` is the public runtime exception for metrics configuration/type conflicts. `MetricsUtil` simplifies context lookup and record creation, including host tagging. `Updater` is the timer callback interface invoked from a context.

### Metrics sinks, JVM metrics, SPI, and metric helper values

`FileContext` extends `AbstractMetricsContext` and emits records to an append-mode file configured by `<contextName>.fileName` or to stdout; it also honors a period property, flushes output, and closes files on `stopMonitoring`.

`GangliaContext` extends `AbstractMetricsContext` and sends emitted records to Ganglia.

`EventCounter` is a Log4J `AppenderSkeleton` that counts fatal, error, warn, and info events through static getters. `JvmMetrics` is a singleton `Updater` that periodically emits JVM metrics tagged by process name and session id.

`AbstractMetricsContext` is the central SPI base class. It implements `MetricsContext`, stores context name/factory, exposes protected attribute access, manages monitoring start/stop/close, creates final public metric records through protected `newRecord`, registers/unregisters updaters, maintains the internal table of metric rows, and calls abstract protected `emitRecord(contextName, recordName, OutputRecord)` each period. `flush()` is a protected no-op hook for sinks.

`MetricsRecordImpl` implements `MetricsRecord`, keeps a back-pointer to its `AbstractMetricsContext`, buffers tag/metric changes, and delegates `update()` and `remove()` back to the context.

`MetricValue` wraps a `Number` as either absolute or incremental using public `ABSOLUTE` and `INCREMENT` booleans, with `isAbsolute`, `isIncrement`, and `getNumber`.

`NullContext` discards all records and does not start monitoring. `NullContextWithUpdateThread` emits nothing but still uses the update thread so time-varying metrics can be sampled for systems such as JMX.

`OutputRecord` is an immutable-ish output view used by providers, exposing tag names, tag values, metric names, and metric values. `Util.parse` parses comma/space separated host or host:port specs into `InetSocketAddress` values, defaulting null specs to localhost with a supplied port.

`MBeanUtil` registers and unregisters JMX MBeans. `MetricsIntValue` and `MetricsLongValue` are set/inc/dec style metrics that publish only once after being changed. `MetricsTimeVaryingInt` publishes per-interval deltas and exposes previous-interval value. `MetricsTimeVaryingRate` records operation counts and times, publishes previous-interval average time and operation count, and tracks resettable min/max operation time. These helper classes synchronize mutators and `pushMetric(MetricsRecord)`.

### `org.apache.hadoop.net`

`DNSToSwitchMapping` maps hostnames or IP addresses to rack/network paths while preserving one-to-one input/output list correspondence. `CachedDNSToSwitchMapping` wraps another mapping in a cache and exposes protected `rawMapping`.

`ScriptBasedMapping` is a final `CachedDNSToSwitchMapping` that implements `Configurable` and delegates rack resolution to a script configured by `topology.script.file.name`.

`DNS` provides static direct and reverse lookup helpers: `reverseDns(InetAddress,String)`, `getIPs(interface)`, `getDefaultIP(interface)`, `getHosts(interface[, nameserver])`, and `getDefaultHost(interface[, nameserver])`.

`NetUtils` centralizes network address and stream construction. Socket factory helpers choose per-protocol or default factories from configuration keys such as `hadoop.rpc.socket.factory.class.<ClassName>` and `hadoop.rpc.socket.factory.class.default`. Address helpers parse `host`, `host:port`, and URI-like strings with optional default ports. `getServerAddress` bridges legacy separate bind/port keys to a combined address. Static resolution helpers add, fetch, and list test host mappings. `getConnectAddress(Server)` rewrites wildcard listener addresses to loopback client addresses. `getInputStream` and `getOutputStream` return channel-backed `SocketInputStream`/`SocketOutputStream` when a socket has a channel, otherwise regular socket streams. `normalizeHostName` and `normalizeHostNames` convert hostnames to textual IP addresses.

`NetworkTopology` models a cluster as a hierarchical tree of racks, data centers, and leaves. Public APIs add/remove leaf nodes, test containment, look up a path, return rack and leaf counts, compute distance, test same rack, choose a random node inside or outside a scope, count available nodes outside exclusions, stringify the tree, and pseudo-sort replica nodes by distance to a reader. Public fields include `DEFAULT_RACK`, `DEFAULT_HOST_LEVEL`, and `LOG`.

`Node` is the topology node interface: network location, name, parent, and level getters/setters. `NodeBase` implements it with constructors for path, name/location, and full parent/level state. It exposes static `getPath(Node)` and `normalize(String)`, constants `PATH_SEPARATOR`, `PATH_SEPARATOR_STR`, and `ROOT`, plus protected fields `name`, `location`, `level`, and `parent`.

`SocketInputStream` extends `InputStream` and implements `ReadableByteChannel`. Constructors accept a selectable readable channel plus timeout, a socket plus timeout, or a socket using its `SO_TIMEOUT`. The constructor configures the channel non-blocking, `read` methods wait for readability with timeout semantics, `getChannel` exposes the underlying channel for transfer operations, `isOpen` reports channel state, `close` is synchronized, and `waitForReadable` throws `SocketTimeoutException` on select timeout. The docs warn that after wrapping a socket channel, regular `Socket.getInputStream()` and `Socket.getOutputStream()` operations on the associated socket will throw `IllegalBlockingModeException`; callers should use `SocketOutputStream` for writes.

## Control Flow and Behavioral Contracts

MapReduce helper flow is configuration-driven. Client code records path-specific input formats through `MultipleInputs`, output side channels through `MultipleOutputs`, comparator/partition field specs through `JobConf`, partition-file locations through `TotalOrderPartitioner`, and DB/Pipes settings through their static helpers. Runtime flow then passes through `InputFormat`/`RecordReader`, mappers or reducers, `OutputCollector`, `Reporter`, `OutputFormat`, and optional counters.

Total-order sorting flow is split between sampling and partitioning. `InputSampler` reads input splits at the client, writes sorted split points to a SequenceFile, and `TotalOrderPartitioner.configure` loads that file before reducer assignment. The key comparator and split file must agree with the job comparator and reducer count.

Generic aggregation flow is data-driven. Descriptor classes convert input key/value pairs into `Text` aggregation id/value pairs. The key prefix names an aggregation type, `ValueAggregatorReducer` instantiates or selects the matching aggregator, consumes all values, and emits each aggregator's report. Combiners use the same aggregator output shape to reduce shuffle volume.

DB input flow computes a count query, splits row ranges with `LIMIT`/`OFFSET` style boundaries implied by `DBInputSplit`, and lets `DBRecordReader` execute a select query and fill user tuple objects through `DBWritable.readFields(ResultSet)`. DB output flow creates an insert `PreparedStatement`, calls `DBWritable.write(PreparedStatement)` on keys, batches or writes rows, and closes SQL resources.

Metrics flow starts at `ContextFactory.getFactory()` and `getContext(name)`. A context creates records, components set tags and metrics, `MetricsRecord.update()` writes into the context's buffered row table, and a monitoring thread periodically invokes registered `Updater`s, snapshots rows as `OutputRecord`s, calls provider `emitRecord`, then optional `flush`. `remove()` stops matching rows from being emitted in later periods.

Network flow resolves hostnames to rack paths through a raw or script-based `DNSToSwitchMapping`, caches results where configured, inserts `Node` instances into `NetworkTopology`, and uses the topology for rack locality decisions. Socket I/O flow chooses a configured socket factory, opens sockets, wraps channel-backed sockets in timeout-aware streams, and uses selector readiness rather than blocking socket streams.

## State and Persistence Behavior

The XML itself is static API metadata. Runtime state exposed by these contracts includes:

- `JobConf` entries for multiple inputs, multiple outputs, output counters, total-order partition files, DB connection/query/output settings, and Pipes executable/debugging/Java-component flags.
- Partition files stored as sorted SequenceFiles containing `numReduceTasks - 1` keys for total-order partitioning.
- Aggregator instances holding sums, extrema, unique-value sets, histograms, and combiner-output values during mapper, combiner, and reducer execution.
- JDBC connections, SQL statements, result sets, and row-range split offsets in DB input/output formats.
- Metrics factory attributes loaded from `hadoop-metrics.properties`, singleton contexts, context monitoring state, buffered metrics tables keyed by record name and tag sets, updater lists, file handles for `FileContext`, network sockets for `GangliaContext`, and Log4J event counters.
- Metrics helper values storing current, changed, previous-interval, min/max, and delta state. Their public mutator/push methods are synchronized, so tests should assume stateful interval transitions.
- DNS-to-switch caches, static host resolutions in `NetUtils`, network topology node/rack counts, parent/level links in `NodeBase`, and non-blocking channel state plus timeout configuration in `SocketInputStream`.

Persistence is primarily externalized through configuration files (`hadoop-metrics.properties`, job XML), HDFS/local paths for partition and output files, SQL databases for DB formats, task-local Pipes debugging files, metrics sink files or Ganglia packets, and Hadoop Writable serialization for input splits.

## Dependencies and Integration Points

Key dependencies visible in signatures and docs include:

- Classic MapReduce APIs: `JobConf`, `InputFormat`, `InputSplit`, `RecordReader`, `OutputCollector`, `Reporter`, `Mapper`, `Reducer`, `MapRunnable`, `Partitioner`, `OutputFormat`, `FileInputFormat`, `FileOutputFormat`, `TextOutputFormat`, `SequenceFileOutputFormat`, `RunningJob`, and `JobClient`.
- Hadoop common APIs: `Configuration`, `Configured`, `Configurable`, `Tool`, `Progressable`, `Writable`, `WritableComparable`, `WritableComparator`, `LongWritable`, `Text`, `Path`, `FileSystem`, `SequenceFile`, `RawComparator`, and IPC `Server`.
- Java platform APIs: collections, regex/string tokenization implied by mappers, `IOException`, JDBC (`Connection`, `PreparedStatement`, `ResultSet`, `SQLException`), networking (`InetAddress`, `InetSocketAddress`, `Socket`, socket factories), NIO channels/selectors, JNDI `NamingException`, JMX, and Log4J.
- External systems: SQL databases through JDBC, C++ Hadoop Pipes executables, metrics files/stdout, Ganglia, DNS/name servers, topology scripts, and configured RPC socket factories.

These APIs sit at integration boundaries, so compatibility depends as much on configuration keys and documented side effects as on Java signatures.

## Risks and Edge Cases

- This chunk is API XML only. It does not reveal exact parser behavior, locking granularity, SQL dialect details, cleanup paths, or resource ownership beyond documented contracts.
- The chunk starts in the middle of `InputSampler` and ends immediately after `SocketInputStream`; adjacent chunks are needed for complete `InputSampler` and `SocketOutputStream` coverage.
- `RandomSampler` can be expensive when configured to sample all splits because it reads input at the client.
- `MultithreadedMapRunner` requires thread-safe mapper implementations; old mappers often use mutable reusable objects and may fail under concurrency.
- Key-field comparator and partitioner behavior depends on exact field separator, 1-based field/character positions, numeric parsing, reverse flags, and raw byte slicing. Misconfiguration can silently break sort or partition order.
- `TotalOrderPartitioner` requires a sorted partition file with exactly reducer-count minus one keys and a comparator compatible with the job. Bad files can cause skew, incorrect global order, or configure-time failures.
- `MultipleOutputs.close()` must be called by mapper/reducer code or extra writers may leak or leave incomplete output files. Multi-named outputs can create many files and counters.
- Aggregate descriptors are dynamically loaded by class name. Bad class names, missing configuration, or malformed aggregation id prefixes can fail at runtime. `UniqValueCount` can grow memory until its configured cap.
- DB formats depend on JDBC driver availability, SQL dialect support for count/select/offset patterns, stable row ordering, correct user `DBWritable` parameter indexes, and safe credential storage in `JobConf`.
- `DBOutputFormat` writes only keys, so jobs expecting value-side DB writes will silently use the wrong object unless configured carefully.
- Pipes job submission mutates `JobConf`; callers sharing a `JobConf` instance may see side effects. Keeping command files for debugging can expose serialized task commands and paths.
- Metrics records should not be shared concurrently by threads even though updates to a row are atomic through separate instances.
- `ContextFactory` defaults to `NullContext`, so missing metrics configuration silently discards data. `MetricsUtil.getContext` also logs failures and returns a null context rather than failing callers.
- File and Ganglia metrics sinks depend on external filesystem/network availability; `FileContext` append-mode files and `flush()` behavior are important for durability tests.
- `NullContextWithUpdateThread` emits no records but still samples; tests should distinguish sampling state from emitted data.
- DNS and rack mapping can return incomplete or misordered lists; the `DNSToSwitchMapping` contract requires one-to-one correspondence.
- `NetworkTopology.add` rejects non-leaf additions and additions under leaves; distance and same-rack methods may throw for null or out-of-cluster nodes.
- `NetUtils` static host resolution is process-global test state and can leak between tests.
- `SocketInputStream` forces non-blocking mode on the socket channel, making ordinary socket input/output streams invalid afterward. Timeout zero means infinite wait, while negative timeout is invalid.

## Test Signals

Useful tests inferred from this API slice include:

- Input sampler tests for interval, random, and split sampling across different split counts, maximum-split caps, empty inputs, client-side IO errors, and generated partition files compatible with `TotalOrderPartitioner`.
- Comparator/partitioner tests for `-k` field ranges, numeric and reverse sorting, character offsets, field separator configuration, hash stability, and compatibility between `KeyFieldBasedComparator` and `KeyFieldBasedPartitioner`.
- `TotalOrderPartitioner` tests for trie versus binary-search selection, reducer-count boundaries, missing/unsorted/wrong-length partition files, custom comparators, and `setPartitionFile`/`getPartitionFile` round trips.
- `MultipleInputs` tests for per-path input format and mapper resolution. `MultipleOutputFormat` tests for filename/key/value generation hooks and input-file-based output naming. `MultipleOutputs` tests for named and multi-named collectors, counter names, mapper bypass of reducers, and mandatory close behavior.
- `MultithreadedMapRunner` tests using thread-safe and intentionally unsafe mappers, configured thread counts, exception propagation, and reporter/output collector concurrency.
- `NLineInputFormat`, `RegexMapper`, `TokenCountMapper`, `InverseMapper`, `LongSumReducer`, and `NullOutputFormat` tests for basic emitted pairs and edge cases such as empty lines, unmatched regex, repeated tokens, and discarded output.
- Aggregate package tests for every `ValueAggregator` reset/add/report/combiner output path, histogram statistics and detailed output, unique-value caps, descriptor loading, mapper descriptor iteration, combiner aggregation, reducer prefix dispatch, and aggregate job configuration.
- DB tests with an embedded JDBC database for configureDB, table/query `setInput`, count query generation, split start/end serialization, record reader progress and close, `DBWritable` parameter/result mapping, output insert query construction, and SQL resource cleanup.
- Pipes `Submitter` tests for all boolean/executable/keep-command configuration helpers, deprecated `submitJob` compatibility, `runJob` configuration mutation, and CLI argument validation.
- Metrics tests for `ContextFactory` property loading, default null context fallback, context lifecycle, updater registration/removal, record tag and metric type conflicts, atomic row update semantics, row removal by tags, and `MetricsUtil.createRecord` host tagging.
- Metrics SPI tests for `AbstractMetricsContext` periodic emission, provider `emitRecord` and `flush`, `MetricsRecordImpl` delegation, `MetricValue` absolute/increment handling, `OutputRecord` tag/metric views, `NullContext` discard behavior, and `NullContextWithUpdateThread` sampling without emission.
- Sink/JVM/helper tests for `FileContext` append/stdout behavior and flush, `GangliaContext` packet emission with mock sockets where possible, `EventCounter` Log4J levels, `JvmMetrics.init` singleton behavior, `MBeanUtil` register/unregister, and synchronized metric helper interval transitions.
- Network tests for DNS interface/default-host helpers, reverse DNS failure paths, script-based and cached rack mapping order preservation, static resolution add/get/list isolation, socket factory class selection, address parsing, wildcard listener rewrite, hostname normalization, topology add/remove/distance/same-rack/random-scope/counting/pseudo-sort behavior, and `NodeBase` path normalization.
- `SocketInputStream` tests for channel-backed reads, byte-buffer reads, close/isOpen behavior, timeout and infinite-timeout behavior, `waitForReadable`, invalid negative timeout, and the documented non-blocking side effect on the underlying socket channel.

## Chunk Boundary Notes

The preceding chunk is needed for the full `InputSampler` class declaration and earlier `org.apache.hadoop.mapred.lib` APIs. This chunk includes the complete declarations for most `mapred.lib`, aggregate, DB, Pipes `Submitter`, metrics, and network classes listed above, but it ends at the start of `SocketOutputStream`, so output-stream timeout behavior must be reconciled with the following chunk.

### subset-b-007309: lines 37252-43530

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 37252-43530

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.2, not Java implementation source. It begins inside the already-open `org.apache.hadoop.net.SocketOutputStream` class, closes the `org.apache.hadoop.net` package, covers all of `org.apache.hadoop.record`, `org.apache.hadoop.record.compiler`, `org.apache.hadoop.record.compiler.ant`, `org.apache.hadoop.record.compiler.generated`, `org.apache.hadoop.record.meta`, `org.apache.hadoop.security`, and `org.apache.hadoop.tools`, then starts `org.apache.hadoop.util` and ends inside `StringUtils.hexStringToByte`. The XML records API compatibility data: package names, class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, return types, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadoc contracts.

The covered surface spans Hadoop's socket factories and timed socket output stream, the legacy Hadoop Record I/O serialization framework and record compiler, record type metadata, user/group identity APIs, distributed-copy/archive/log-analysis command-line tools, and a large utility subset covering checksums, disk checks, generic option parsing, sorting, host-file loading, line reading, process-tree management, progress reporting, reflection, jar launching, servlet helpers, shell command execution, and string formatting/conversion.

## Purpose and Major API Surface

`SocketOutputStream` provides timed writes over a `WritableByteChannel` or a socket's channel. Its constructors configure the channel as non-blocking and treat timeout zero as infinite. It implements `WritableByteChannel`, exposes `write(int)`, `write(byte[], int, int)`, `write(ByteBuffer)`, synchronized `close()`, `isOpen()`, `getChannel()`, `waitForWritable()`, and `transferToFully(FileChannel, long, int)`. The contract explicitly warns that normal socket stream reads/writes on the same socket will fail after the channel is put into non-blocking mode, and callers should use the matching Hadoop socket input stream for reads.

`SocksSocketFactory` and `StandardSocketFactory` are `SocketFactory` implementations. `SocksSocketFactory` is configurable, can be constructed with a `Proxy`, and has all standard `createSocket` overloads plus `getConf`, `setConf`, `equals`, and `hashCode`. `StandardSocketFactory` exposes the same socket-creation overloads and equality/hash operations without `Configurable`.

`org.apache.hadoop.record` is the legacy record serialization API. `RecordInput` and `RecordOutput` define tag-aware primitive, string, buffer, record, vector, and map read/write contracts. `BinaryRecordInput` and `BinaryRecordOutput` implement those contracts over `DataInput`/`DataOutput` or streams and expose thread-local `get(...)` factories. `CsvRecordInput`/`CsvRecordOutput` and `XmlRecordInput`/`XmlRecordOutput` implement the same contract for textual formats. `Index` supplies `done()` and `incr()` for vector/map traversal.

`Buffer` is the record framework's byte-sequence value type. It is mutable, resizable, cloneable, comparable, and tracks count separately from capacity. It can adopt an existing byte array via `set`, copy a byte range via `copy`, expose the backing array via `get`, report `getCount`/`getCapacity`, change capacity, reset, truncate capacity to count, append ranges or whole arrays, compare lexicographically, convert to strings, and clone itself.

`Record` is the generated-record base contract. It supports serialization/deserialization through `RecordOutput`/`RecordInput`, binary wire compatibility through `DataOutput`/`DataInput`, Hadoop `Writable` hooks `write` and `readFields`, comparability, and `toString`. `RecordComparator` extends `WritableComparator`, compares two serialized record byte ranges, and has a static `define(Class, RecordComparator)` registration method.

`org.apache.hadoop.record.Utils` provides low-level serialization helpers: float/double reads from byte arrays, variable-length integer/long reads from byte arrays or `DataInput`, variable-length integer size calculation, variable-length writes to `DataOutput`, byte-array comparison, and the `hexchars` table. These helpers underpin binary record encoding and comparison.

`org.apache.hadoop.record.compiler` models the record compiler's type system. `CodeBuffer` renders accumulated generated source text. `Consts` exposes code-generation symbol constants such as record I/O prefixes, runtime type-info variables/filters, record input/output names, and tag names. Primitive and composite type nodes include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, `JRecord`, `JType`, and `JCompType` subclasses. `JField<T>` names a typed field. `JFile` represents a record compiler input file, its included files, and records, and exposes `genCode(String language, String destDir)` returning an integer status.

`RccTask` is the Ant integration point for the record compiler. It extends `org.apache.tools.ant.Task` and accepts `language`, single `file`, `failonerror`, `destdir`, and nested `FileSet` inputs before `execute()`.

`org.apache.hadoop.record.compiler.generated` contains JavaCC-generated parser and lexer API. `Rcc` parses record compiler input from `InputStream`, `Reader`, or `RccTokenManager`, exposes grammar productions such as `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, plus `driver`, `usage`, `main`, `ReInit`, token access, parse exception generation, and tracing toggles. `RccConstants` defines token IDs for module/record/include keywords, primitive types, vector/map punctuation, identifiers, string tokens, comment states, and `tokenImage`.

`ParseException`, `TokenMgrError`, `RccTokenManager`, `SimpleCharStream`, and `Token` provide parser error reporting and tokenization state. `ParseException` carries current token, expected token sequences, token images, and message formatting. `RccTokenManager` exposes debug stream control, lexical reinitialization, lexical state switching, token creation, next-token retrieval, and lexer tables/state. `SimpleCharStream` tracks reader/input-stream character buffers, line/column positions, tab size, backup state, suffix/image extraction, reinitialization overloads, and cleanup. `Token` stores token kind, image, source span, next/special-token links, and a static factory.

`org.apache.hadoop.record.meta` supplies runtime type metadata for records. `TypeID` defines primitive singleton IDs and byte-valued RIO type constants, with equality/hash behavior and `getTypeVal()`. `MapTypeID`, `VectorTypeID`, and `StructTypeID` add key/value, element, and field-list metadata. `FieldTypeInfo` pairs field names with type IDs and supports compatibility equality checks. `RecordTypeInfo` extends `Record`, names a record schema, adds fields, retrieves nested struct metadata, serializes/deserializes the schema, and compares records. `meta.Utils.skip` skips values in a `RecordInput` according to a `TypeID`.

`org.apache.hadoop.security` contains legacy user/group identity APIs. `AccessControlException` subclasses the filesystem permission exception. `UnixUserGroupInformation` extends `UserGroupInformation`, is writable through `readFields`/`write`, exposes user/group accessors, immutable creation, configuration save/load through `UGI_PROPERTY_NAME`, login overloads from default environment, configuration, or explicit user/group state, and equality/hash/string behavior. `UserGroupInformation` exposes global current UGI get/set, user/group accessors, login, `readFrom(Configuration)`, and a Commons Logging `LOG`.

`org.apache.hadoop.tools` covers command-line MapReduce tools. `DistCp` implements configurable distributed copy through constructor, `setConf`, `getConf`, `copy(String[] args)`, `run(String[] args)`, `main`, `getRandomId`, and logging; `DistCp.DuplicationException` has an `ERROR_CODE` field. `HadoopArchives` similarly exposes configurable archive creation through `archive(String[] args)`, `run`, and `main`. `Logalyzer` exposes `doArchive`, `doAnalyze`, and `main` for archiving and analyzing logs with MapReduce. Its `LogComparator` extends `Text.Comparator`, is configurable, and compares byte ranges. `LogRegexMapper` extends `MapReduceBase`, configures itself from a `JobConf`, and maps log records to text outputs.

`org.apache.hadoop.util` begins with `CyclicIteration`, `Daemon`, `DataChecksum`, `DiskChecker`, `GenericOptionsParser`, `GenericsUtil`, `HeapSort`, `HostsFileReader`, `IndexedSortable`, `IndexedSorter`, `LineReader`, `MergeSort`, `NativeCodeLoader`, `PlatformName`, `PrintJarMainClass`, `PriorityQueue`, `ProcfsBasedProcessTree`, `ProgramDriver`, `Progress`, `Progressable`, `QuickSort`, `ReflectionUtils`, `RunJar`, `ServletUtil`, `Shell`, `Shell.ExitCodeException`, `Shell.ShellCommandExecutor`, and the beginning of `StringUtils`.

Important utility contracts in this range include `DataChecksum` factory methods from type/bytes/checksum size, header serialization, checksum value writes, value comparison, reset/update, and constants for null/CRC32 checksum type and header sizing. `DiskChecker` creates directories with existence checks and validates directories, throwing `DiskErrorException` or `DiskOutOfSpaceException`. `GenericOptionsParser` parses generic Hadoop CLI options into a `Configuration`, exposes remaining app args, the Commons CLI `CommandLine`, libjars URLs, and generic usage printing.

Sorting and collection helpers use Hadoop's indexed sorting contracts. `IndexedSortable` supplies `compare` and `swap`; `IndexedSorter` sorts half-open ranges with or without `Progressable`; `HeapSort` and `QuickSort` implement that interface, with `QuickSort.getMaxDepth` documenting the fallback threshold to heapsort. `MergeSort` is a separate array merge sort over `int[]` with `Comparator<IntWritable>`. `PriorityQueue<T>` is an abstract heap where subclasses define `lessThan`; callers initialize capacity and then use `put`, `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`.

Process, launcher, and system utilities include `ProcfsBasedProcessTree` for Linux `/proc`-based process-tree discovery, liveness, destroy, cumulative virtual-memory accounting, pid-file parsing, and SIGKILL delay configuration; `ProgramDriver` for command registry/dispatch; `RunJar` for jar extraction and main-class invocation; and `Shell` for template-method shell execution with environment/working-directory controls, interval gating, process/exit-code access, static command helpers, and `ShellCommandExecutor` for small-output command execution.

`StringUtils` is only partially covered here. The visible methods stringify exceptions, shorten fully qualified hostnames, format large integers and percentages, join string arrays, convert byte ranges or whole arrays to hex, and begin `hexStringToByte`.

## Control Flow and Behavioral Contracts

The JDiff file does not include method bodies, but the public contracts imply several important flows. Socket output setup constructs `SocketOutputStream` from a selectable channel or socket, forces non-blocking mode, and routes writes through readiness waits governed by the configured timeout. `transferToFully` loops until the requested number of bytes has been transferred from the `FileChannel`, surfacing EOF if the source ends early and socket timeout if the destination blocks too long.

Record I/O flow is symmetric: generated records call `startRecord`, emit or read fields by tag through primitive/string/buffer methods, recurse into vectors or maps by obtaining an `Index`, increment until `done()`, then close each vector/map/record. Binary implementations are used for Hadoop `Writable` persistence; CSV and XML implementations are alternate textual encodings with the same method shape.

Record compiler flow starts from an `Rcc` parser reading a record IDL. Grammar methods build `JFile`, `JRecord`, `JField`, and `JType` objects. `JFile.genCode` then emits code for a requested language into a destination directory. `RccTask.execute` wraps that flow for Ant by collecting a configured file or filesets, selecting a language and destination, and honoring `failonerror`.

Parser control flow is JavaCC-style. `SimpleCharStream` supplies buffered characters with source positions to `RccTokenManager`; the token manager switches lexical states for comments and returns `Token` objects; `Rcc` consumes tokens through grammar methods and emits `ParseException` or `TokenMgrError` when syntactic or lexical expectations fail. `ReInit` methods allow parser, token manager, and char stream objects to be reused with new inputs.

Record metadata flow serializes schema descriptions as records. `RecordTypeInfo` accumulates `FieldTypeInfo` objects, can nest struct metadata, serializes/deserializes itself through the same `Record` framework, and uses `TypeID` byte values for primitive/composite type identity. `meta.Utils.skip` consumes serialized data based on metadata, which is useful when filtering or evolving schemas.

Security identity flow centers on static/global current UGI and configuration persistence. `UnixUserGroupInformation.login` discovers user/group state, `saveToConf` writes it under a named property, and `readFromConf` or base `UserGroupInformation.readFrom` restores it. Writable methods allow UGI instances to travel across Hadoop RPC or job configuration paths.

Tool flow follows Hadoop's configurable command pattern. `DistCp` and `HadoopArchives` are constructed with a `Configuration`, can be used programmatically through `copy` or `archive`, and expose `run`/`main` for CLI execution. `Logalyzer.doArchive` stages logs, `doAnalyze` runs MapReduce analysis, `LogRegexMapper` processes records according to job configuration, and `LogComparator` controls sort ordering for log keys.

Generic CLI parsing happens before tool-specific execution. `GenericOptionsParser` mutates or augments the supplied `Configuration`, separates Hadoop generic options from application args, tracks `-libjars` URLs, and exposes the parsed Commons CLI command line. Tool runners outside this chunk rely on these semantics.

Sorting flow adapts caller-owned data to `IndexedSortable`, then passes index bounds to `HeapSort` or `QuickSort`. Implementations mutate only through `swap` and compare only through `compare`; progress-aware overloads can call `Progressable.progress()` in long sorts. `QuickSort`'s documented maximum recursion depth guards worst-case behavior by switching to heapsort.

Shell execution is template-method based. Subclasses supply a command vector and parse stdout. `run()` gates execution by interval, starts a process using the configured environment and working directory, records process/exit state, and throws `IOException` or `ExitCodeException` for failures. `ShellCommandExecutor` implements the simple case by collecting output as a string, and its docs state that output should be small.

Progress flow is tree-shaped. A root `Progress` gets phases added, moves through phases, lets leaves set progress/status, computes aggregate progress through the hierarchy, and can mark nodes complete. Several methods are synchronized in the API, signaling expected concurrent reads and updates by framework and task threads.

## State, Persistence, and Side Effects

The XML itself is persistent compatibility metadata used by JDiff. Runtime state described by these APIs includes socket channels and timeout values, thread-local binary record input/output wrappers, mutable `Buffer` backing arrays and counts, generated-record field values, record compiler ASTs, parser token/stream buffers, record type metadata, UGI user/group arrays, tool configurations, MapReduce job state, checksum values, parsed CLI arguments, host include/exclude sets, priority queue heap contents, process-tree snapshots, progress trees, shell process handles, shell output buffers, and servlet output writers.

Persistence and external effects are broad. Record APIs read and write binary, CSV, and XML data to streams. `Record`, `RecordTypeInfo`, and `UnixUserGroupInformation` participate in Hadoop's `Writable` persistence. `UnixUserGroupInformation.saveToConf` and `readFromConf` persist identities into `Configuration`. `JFile.genCode` and `RccTask.execute` write generated code to destination directories. `DistCp`, `HadoopArchives`, and `Logalyzer` interact with Hadoop filesystems and submit or run MapReduce jobs. `RunJar.unJar` writes jar contents to disk and `RunJar.main` executes arbitrary job code.

System side effects include opening sockets, configuring channels to non-blocking mode, running shell commands, setting process environments and working directories, checking or creating directories, reading host include/exclude files, reading `/proc`, destroying process trees, loading or checking native Hadoop libraries, writing servlet responses, and logging through Commons Logging.

Not all mutable classes are documented as thread-safe. `Progress` has synchronized methods, `SocketOutputStream.close` is synchronized, and binary record factories are explicitly thread-local. By contrast, parser objects, `Buffer`, record metadata builders, `PriorityQueue`, tool instances, `HostsFileReader`, and `ShellCommandExecutor` carry mutable state without a visible thread-safety contract in this XML.

## Dependencies and Integration Points

Network APIs depend on `java.net.Socket`, `java.net.Proxy`, `SocketFactory`, `InetAddress`, `UnknownHostException`, NIO `WritableByteChannel`, `SelectableChannel`, `ByteBuffer`, and `FileChannel`. Hadoop configuration integration appears through `org.apache.hadoop.conf.Configurable` and `Configuration`.

Record serialization depends on Java `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `IOException`, Hadoop `Writable`/`WritableComparable`/`WritableComparator`, and generated-code conventions from the record compiler. The compiler path depends on Ant `Task` and `FileSet`, JavaCC-generated parser classes, Java collections, and filesystem output directories.

Security APIs depend on Hadoop filesystem permission exceptions, configuration storage, logging, and Writable serialization. They are integration points for RPC, job submission, filesystem permission checks, and code paths that need current user/group identity.

Tools integrate with `Configuration`, MapReduce old API types such as `JobConf`, `MapReduceBase`, mapper output collectors/reporters, `Text.Comparator`, Hadoop filesystems, and CLI entry points. They are user-facing operational APIs, so signature or return-code compatibility matters.

Utility dependencies span Commons CLI, Commons Logging, servlet APIs, Java reflection, `Process`, files and readers, URI/URL handling, jar files/manifests, native libraries, Linux procfs, Hadoop `Path`, `IntWritable`, and `Progressable`. `DataChecksum` is a low-level integration point for HDFS block/data integrity code and any protocol that consumes its header/value layout.

## Risks and Compatibility Notes

This chunk starts mid-class for `SocketOutputStream`; adjacent earlier lines are needed for the class opening metadata, including its exact `extends` type. It also ends mid-class in `StringUtils`, so later lines are needed for the rest of that utility API and the package/API closure. Research for this chunk should therefore avoid claiming complete coverage of either class.

`SocketOutputStream` changes socket-channel blocking mode as part of construction. That side effect can break callers that continue to use `Socket.getInputStream()` or `Socket.getOutputStream()` directly; the Javadoc explicitly documents this incompatibility. Timeout handling and full-transfer semantics are also subtle because partial writes, EOF, and selector timeouts must be distinguished.

The record framework is a wire/storage compatibility surface. Changes to primitive encodings, variable-length integer encoding, `Buffer` compare order, field ordering, tags, map/vector delimiters, XML/CSV escaping, or record comparator behavior can break persisted data, generated-code interoperability, and sorted binary comparisons.

`Buffer.get()` exposes the backing array, and `set(byte[])` adopts the caller's array as backing storage. Aliasing can create surprising mutation bugs, but it is part of the documented API. Capacity/count separation must be preserved for callers that manage reusable buffers.

Record compiler generated classes expose many public parser fields and JavaCC implementation details. Although not ideal encapsulation, callers or build scripts may depend on those names. Regenerating the parser with different JavaCC versions could alter token constants, exception formatting, field visibility, or reinitialization signatures.

`RecordTypeInfo` and `TypeID` are schema-evolution primitives. Equality and hash-code behavior for nested map/vector/struct metadata must stay stable, and `meta.Utils.skip` must consume exactly the same wire representation as the active record input implementation.

UGI APIs are security-sensitive and legacy-global. Mutating current UGI, persisting user/group values in configuration, or creating immutable instances affects permission checks and job execution identity. Compatibility changes can become authorization regressions, especially where user/group arrays are trusted from configuration.

`DistCp`, `HadoopArchives`, and `Logalyzer` are operational tools. Their argument handling, return codes, exception behavior, configuration mutation, and MapReduce job setup are externally visible to scripts. `DistCp.DuplicationException.ERROR_CODE` suggests callers may branch on specific failure codes.

`DataChecksum` constants and header layout are protocol-sensitive. Any alteration to checksum type IDs, header length, bytes-per-checksum handling, or byte-order behavior would affect readers and writers of checksummed data.

`GenericOptionsParser` is a central CLI compatibility point. Changes to remaining-argument slicing, `-libjars` URL construction, `CommandLine` exposure, or usage output can break Hadoop tools and scripts.

`Shell`, `ProcfsBasedProcessTree`, native loading, and disk checking are platform-dependent. Unix command constants, Windows detection, `/proc` availability, process killing, directory permissions, disk-space errors, and native-library loading all depend on host OS behavior. Tests need explicit non-Linux or unavailable-feature coverage where possible.

`PriorityQueue` and indexed sorting expose caller-owned mutation hooks. Incorrect `lessThan`, `compare`, or `swap` semantics are caller bugs, but implementation changes can amplify them. Range interpretation for `IndexedSorter` is half-open `[l, r)`, and progress callbacks matter for long MapReduce tasks that otherwise risk timeout.

## Test Signals

JDiff validation should verify the XML remains well-formed across this slice's package transitions, preserves every public/protected API element in the listed packages, and keeps return types, parameter order, declared exceptions, visibility, static/final/abstract/synchronized flags, implemented interfaces, deprecation markers, and Javadoc contracts stable.

Socket tests should construct `SocketOutputStream` from socket channels and direct writable channels, verify non-negative timeout handling including zero-as-infinite behavior, check non-blocking side effects, exercise byte-array and `ByteBuffer` writes, close/idempotence behavior, `waitForWritable` timeout cases, and `transferToFully` success, partial-write, EOF, and timeout paths.

Record I/O tests should round-trip generated records through binary, CSV, and XML implementations; cover all primitive types, strings, buffers, records, vectors, and maps; verify thread-local binary wrapper reuse; assert `Index.done/incr` traversal behavior; and compare serialized records through `RecordComparator`.

`Buffer` tests should cover adopting versus copying arrays, offsets and lengths, appends, capacity growth/shrink, reset, truncate, backing-array exposure, lexicographic compare, equality/hash consistency, charset string conversion, cloning, and mutation aliasing.

Record utility and metadata tests should cover variable-length integer/long encoding boundaries, float/double byte decoding, byte comparison ordering, `TypeID` singleton equality/hash values, map/vector/struct equality, nested `RecordTypeInfo` lookup, schema serialization/deserialization, and `meta.Utils.skip` over primitive and nested serialized values.

Record compiler tests should parse simple and nested record IDL files, includes, maps, vectors, all primitive types, comments, bad syntax, and lexical errors; verify token source positions and parse exception messages; run `JFile.genCode` into a temporary directory; and exercise `RccTask` with single files, filesets, destination directory, language selection, and `failonerror` true/false.

Security tests should cover default and configured UGI login, explicit user/group constructors, immutable creation, `getUserName`, `getGroupNames`, Writable round trips, `saveToConf`/`readFromConf`, `setCurrentUGI`/`getCurrentUGI`, equality/hash/toString, and access-control exception propagation.

Tool tests should exercise `DistCp.copy/run/main` argument validation and duplicate-source handling, archive creation argument paths in `HadoopArchives`, `Logalyzer.doArchive` and `doAnalyze` configuration, `LogComparator` byte-range ordering, and `LogRegexMapper` configuration plus map output behavior. Return codes and logged/raised exceptions should be asserted because scripts may depend on them.

Utility tests should cover `DataChecksum` factory variants, header serialization/deserialization, checksum update/reset/value comparison, null versus CRC32 behavior, disk directory creation and error cases, generic option parsing and remaining args, libjars URL extraction, generic usage printing, `GenericsUtil` empty-list behavior, host include/exclude refreshes, line reading with different newline and max-length cases, and native-loader flags.

Sorting and queue tests should cover empty, single-element, duplicate-heavy, already-sorted, reverse-sorted, and subrange inputs for `HeapSort`, `QuickSort`, and `MergeSort`; verify `[l, r)` bounds; assert progress callbacks; test quicksort depth fallback indirectly with adversarial inputs; and cover priority queue capacity, ordering, rejection/acceptance by `insert`, `put`, `top`, `pop`, `adjustTop`, `size`, and `clear`.

Process and launcher tests should cover `ProcfsBasedProcessTree.isAvailable`, pid-file parsing, alive/dead detection, cumulative virtual memory, destroy and SIGKILL interval behavior in a controlled environment, `ProgramDriver` registration/dispatch/unknown command cases, `RunJar.unJar`, manifest main-class lookup, command-line main-class override, and `PrintJarMainClass` output.

Progress, reflection, servlet, shell, and string tests should cover progress-tree aggregation and concurrent updates, `ReflectionUtils` configuration injection and instance creation, thread-info logging interval suppression, servlet HTML/footer/parameter/percentage graph helpers, shell command environment and working directory propagation, interval gating, nonzero exit codes, output capture, Windows/non-Windows branches, and visible `StringUtils` methods for exception stringification, host shortening, number/percent formatting, array joining, and hex encode/decode.

### subset-b-007310: lines 43531-44204

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 43531-44204

## Scope

This chunk is the final segment of the generated JDiff public API snapshot for Hadoop 0.19.2. It is XML API metadata, not Java implementation code. The range begins inside the `org.apache.hadoop.util.StringUtils.hexStringToByte(String)` method entry, then completes `StringUtils`, `StringUtils.TraditionalBinaryPrefix`, `Tool`, `ToolRunner`, `UTF8ByteArrayUtils`, `VersionInfo`, and `XMLUtils`, followed by the closing `</package>` and `</api>` markers.

The XML records public API compatibility surface: class and interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadoc contracts. Because this chunk is API metadata, control flow and state behavior are inferred from signatures and documentation rather than method bodies.

## Purpose and Major API Surface

`StringUtils` is documented as "General string utils" and this tail of the class exposes conversion, formatting, escaping, hostname, startup/shutdown logging, and HTML escaping helpers. The chunk starts with `hexStringToByte(String hex)`, whose method header begins just before this range; its contract converts a hex string into a byte array with length `hex.length/2`. URI and path conversion helpers include `uriToString(URI[] uris)`, `stringToURI(String[] str)`, and `stringToPath(String[] str)`, bridging string configuration values with Java `URI` and Hadoop `Path` arrays.

Time formatting helpers include `formatTimeDiff(long finishTime, long startTime)`, `formatTime(long timeDiff)`, and `getFormattedTimeWithDiff(DateFormat dateFormat, long finishTime, long startTime)`. `formatTimeDiff` returns an elapsed-time string in hours, minutes, and seconds and explicitly allows negative components when `finishTime` precedes `startTime`. `getFormattedTimeWithDiff` formats a finish timestamp and appends the elapsed difference when a start time is present; if `finishTime` is `0`, the method returns an empty string.

Comma-separated string helpers include `getStrings(String str)`, `getStringCollection(String str)`, two `split` overloads, `findNext(String str, char separator, char escapeChar, int start, StringBuilder split)`, three `escapeString` overloads, and three `unEscapeString` overloads. The default methods use the public constants `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`, while the overloads allow caller-supplied separator and escape characters or arrays of characters to escape. `findNext` is part of the escaped-splitting contract: it searches for the first unescaped separator starting at an index and returns the extracted segment through a `StringBuilder`.

Host and log/HTML helpers include `getHostname()`, which returns a hostname without throwing; `startupShutdownMessage(Class<?> clazz, String[] args, Log LOG)`, which writes standard startup and shutdown logging for server classes; and `escapeHTML(String string)`, which escapes HTML special characters in a string. These utilities sit at diagnostic and web UI boundaries rather than data-structure boundaries.

`StringUtils.TraditionalBinaryPrefix` is a public static final enum nested under `StringUtils`. It represents traditional binary prefixes from kilo through exa in powers of 1024. Public enum methods include the generated `values()`, `valueOf(String name)`, a Hadoop-specific `valueOf(char symbol)` that maps a prefix symbol case-insensitively, and `string2long(String s)`, which trims and parses strings with optional binary suffixes such as `k` or `g`. The enum exposes public final instance fields `value` (`long`) and `symbol` (`char`).

`Tool` is a public interface extending `org.apache.hadoop.conf.Configurable`. It defines Hadoop's standard command-line application contract through `run(String[] args)`, returning an integer exit code and declaring `Exception`. The Javadoc positions `Tool` as the standard MapReduce application interface: generic Hadoop options should be delegated to `ToolRunner`, while custom application arguments remain the responsibility of the application.

`ToolRunner` is a public utility class for executing `Tool` implementations. It has a public constructor, two static `run` overloads, and `printGenericCommandUsage(PrintStream out)`. `run(Configuration conf, Tool tool, String[] args)` parses generic Hadoop arguments, uses the supplied `Configuration` or creates one when null, installs the possibly modified configuration on the tool, then calls `Tool.run(String[])`. `run(Tool tool, String[] args)` delegates to the first overload using `tool.getConf()`. `printGenericCommandUsage` writes generic Hadoop command-line usage to a supplied `PrintStream`.

`UTF8ByteArrayUtils` is a public byte-array search utility class. It has a public constructor and static helpers for searching UTF-8 encoded byte arrays: `findByte(byte[] utf, int start, int end, byte b)`, `findBytes(byte[] utf, int start, int end, byte[] b)`, and two `findNthByte` overloads. These methods return the matching byte offset or `-1` if absent. The APIs operate on raw bytes even though the documentation describes the array as UTF-8 encoded text, so they are suitable for delimiter scanning without allocating Java `String` objects.

`VersionInfo` exposes Hadoop build metadata. Static methods include `getVersion()`, `getRevision()`, `getDate()`, `getUser()`, `getUrl()`, `getBuildVersion()`, and `main(String[] args)`. The Javadoc says this class finds package info and `HadoopVersionAnnotation` information; the returned build version combines version, revision, user, and date.

`XMLUtils` is a public general XML utility class. Its static `transform(InputStream styleSheet, InputStream xml, Writer out)` applies an XSLT stylesheet to input XML and writes the result to the supplied writer. It declares `TransformerConfigurationException` and `TransformerException`, exposing failures from the Java XML transform stack.

## Control Flow and Behavioral Contracts

The `StringUtils` escaping flow is a round-trip contract across persisted or CLI-provided delimited values. Callers escape separator characters before joining or storing values, split on unescaped separators with `split`/`findNext`, and unescape values after parsing. Correct behavior depends on all default helpers agreeing on `COMMA` and `ESCAPE_CHAR`, and on overloads treating caller-provided escape and separator characters consistently.

The time-formatting flow separates raw duration formatting from timestamp display. `formatTimeDiff` computes `finishTime - startTime` and delegates the user-facing duration shape to the same style as `formatTime`. `getFormattedTimeWithDiff` adds conditional presentation behavior around missing timestamps: no finish time produces no text, while no start time suppresses the elapsed suffix.

The binary-prefix parsing flow in `TraditionalBinaryPrefix.string2long` trims the input, detects an optional final prefix symbol, maps that symbol through `valueOf(char)`, and multiplies the numeric portion by the prefix value. The documentation examples make sign handling part of the contract: negative numeric strings retain the sign before multiplication.

The `Tool`/`ToolRunner` flow is the central command-line integration path. A Hadoop application implements `Tool`, usually via a `Configured` base class. `ToolRunner.run` parses generic Hadoop options first, mutates the tool's configuration via the `Configurable` contract, and forwards only application-specific arguments to `Tool.run`. The returned integer is the process-level exit code expected by caller `main` methods.

The UTF-8 byte search flow scans caller-owned byte arrays by offset. `findByte` searches a bounded `[start, end)`-style interval for one byte; `findBytes` searches for a byte sequence in the same bounded interval; `findNthByte` searches for the nth occurrence either within an explicit `start`/`length` range or across the whole array. The API returns `-1` for misses rather than throwing for normal absence.

`VersionInfo` lookup is a read-only build metadata flow. Static getters retrieve version, source-control revision, build date, build user, repository URL, and a combined display string. `main` is available for command-line inspection of the same metadata.

`XMLUtils.transform` is a one-shot transform flow: consume stylesheet and XML input streams, configure a transformer, apply the transform, and stream the output to the caller-provided `Writer`. Transform configuration failures and runtime transform failures remain visible through the declared checked exceptions.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API compatibility data. It does not store implementation bodies or runtime values, but it captures source/binary compatibility decisions for Hadoop 0.19.2 public APIs.

Most APIs in this chunk are stateless static helpers. Persistent data dependencies arise indirectly: `StringUtils` URI/path/comma escaping helpers are commonly used to serialize and deserialize configuration values, command-line lists, and log/web display strings. Changes to escaping, splitting, hex conversion, or URI/path conversion can affect data already stored in configuration files or job metadata.

`ToolRunner.run` has an explicit state side effect: it sets the tool's `Configuration` after generic option parsing. That mutation is intentional and central to the `Tool` contract; tools that read `getConf()` inside `run` depend on receiving the processed configuration, not the original raw object.

`startupShutdownMessage` writes through an Apache Commons Logging `Log` and installs shutdown logging behavior according to its documentation. `escapeHTML` is a pure string transform but is used to protect generated HTML output boundaries.

`TraditionalBinaryPrefix` enum instances carry immutable public fields `value` and `symbol`. Although the fields are public, they are final and represent fixed enum constants. `string2long` returns primitive values and does not persist state.

`UTF8ByteArrayUtils` methods inspect caller-owned byte arrays and return offsets without documented mutation. `VersionInfo` getters read package or annotation metadata embedded at build time. `XMLUtils.transform` consumes input streams and writes transformed content to the supplied `Writer`; it may leave partial output if a `TransformerException` occurs after writing begins.

## Dependencies and Integration Points

This chunk integrates `StringUtils` with Java core types (`String`, `String[]`, `StringBuilder`, `DateFormat`, `URI`) and Hadoop filesystem paths (`org.apache.hadoop.fs.Path`). The startup/shutdown logging method depends on `org.apache.commons.logging.Log`.

`Tool` depends on `org.apache.hadoop.conf.Configurable`; `ToolRunner` depends on `org.apache.hadoop.conf.Configuration`, `Tool`, `PrintStream`, and the related `GenericOptionsParser` API documented in Javadoc links. The example Javadoc also references the older MapReduce API surface (`JobConf`, `JobClient`, mapper/reducer configuration, `Path`) as the expected application context.

`UTF8ByteArrayUtils` has only byte-array and primitive dependencies, which makes it suitable for low-allocation parsing paths such as text input processing. Its behavior is still tied to callers that understand byte offsets in UTF-8 encoded data.

`VersionInfo` depends on build-time package metadata and `HadoopVersionAnnotation`, as described by the class Javadoc. Its output is consumed by command-line tools, diagnostics, logs, and version checks.

`XMLUtils` depends on Java IO streams/writers and `javax.xml.transform` exceptions. It is an integration point between Hadoop utilities and standard JAXP/XSLT processing.

The XML package boundary closes `org.apache.hadoop.util` and then the whole API document. Downstream merge/reconciliation tools should treat this chunk as the final chunk for `hadoop_0.19.2.xml`.

## Risks and Compatibility Notes

The chunk begins at line 43531 inside the `hexStringToByte` method entry. Its method name, return type, and static/visibility flags are visible in immediately preceding lines, while this chunk contains the parameter and Javadoc. Reconciliation should merge this with the previous chunk when producing a final per-file report.

`StringUtils` helpers are compatibility-sensitive because they affect persisted textual encodings. Escaping rules, separator defaults, hex parsing, URI/path conversion, hostname formatting, and elapsed-time display are all user-visible or configuration-visible. Even a small change to edge cases such as odd-length hex strings, empty comma-separated entries, trailing escape characters, or null arrays could break older jobs or configuration round trips.

`findNext` exposes a low-level parsing helper with output via a mutable `StringBuilder`. Callers depend on the returned index and the side-channel segment content staying synchronized. Off-by-one behavior around escaped separators, adjacent separators, or end-of-string conditions is a likely regression surface.

`TraditionalBinaryPrefix.string2long` can overflow `long` when large numeric values are multiplied by high prefixes. The API returns primitive `long` and the XML does not document overflow behavior. Case-insensitive prefix lookup is documented, so rejecting upper-case symbols would be incompatible.

`ToolRunner` mutates the passed `Tool`'s configuration and declares broad `Exception`. Wrappers must preserve generic option parsing order, argument forwarding semantics, configuration installation, and exit-code propagation. Changing when the configuration is set can break tools that inspect it during `run`.

`UTF8ByteArrayUtils` works at byte offsets, not character indexes. Callers scanning multibyte UTF-8 content must only search for byte delimiters where byte-level matching is valid. Boundary handling for `start`, `end`, `length`, and `n` is a key risk because the Javadoc does not specify validation or exception behavior for invalid ranges.

`VersionInfo` is a diagnostic compatibility point. Missing package annotations or changed formatting of `getBuildVersion()` can affect logs, support tooling, and tests that assert version output.

`XMLUtils.transform` delegates to the platform XML transformer implementation. External entity handling, stylesheet behavior, stream lifecycle, character encoding, and partial writes are not described in the XML. Callers should treat transformer exceptions as expected failure modes and should own closing the streams/writer unless implementation documentation says otherwise.

## Test Signals

JDiff-level validation should confirm the XML remains well formed through the final `</api>`, preserves the closing `org.apache.hadoop.util` package boundary, and keeps all method signatures, parameters, declared exceptions, field constants, visibility, static/final flags, abstract/interface metadata, deprecation states, and Javadoc blocks stable.

`StringUtils` tests should cover hex round trips, invalid or odd-length hex input, URI array to string conversion, string arrays to URI and `Path` arrays, duration formatting for positive, zero, and negative differences, `getFormattedTimeWithDiff` with zero finish/start timestamps, comma-separated parsing, empty and whitespace inputs, escaping/unescaping default commas, custom escape/separator characters, arrays of escaped characters, `findNext` boundary cases, hostname fallback behavior, startup/shutdown log emission, and HTML escaping for special characters.

`TraditionalBinaryPrefix` tests should cover `values()`, Java enum `valueOf(String)`, Hadoop `valueOf(char)` with upper- and lower-case symbols, unknown symbols, `string2long` with no suffix, positive and negative suffixes, surrounding whitespace, high prefixes, zero, and overflow-adjacent values.

`Tool` and `ToolRunner` tests should use a small `Tool` implementation to assert generic option parsing, configuration installation, use of a null or existing `Configuration`, the overload that calls `tool.getConf()`, preservation of application-specific arguments, return-code propagation, exception propagation, and generic usage text printed to a `PrintStream`.

`UTF8ByteArrayUtils` tests should scan ASCII and multibyte UTF-8 byte arrays for single bytes, byte sequences, nth occurrences, missing bytes, start/end subranges, explicit start/length ranges, whole-array overload behavior, and invalid or edge inputs such as empty arrays, `n <= 0`, and ranges at array boundaries.

`VersionInfo` tests should assert non-null version, revision, date, user, URL, combined build-version formatting, and `main` output consistency with the getter values when build metadata is available.

`XMLUtils` tests should transform a simple XML document with a simple stylesheet, assert writer output, and cover malformed stylesheets, malformed XML, transformer runtime errors, and behavior when output has been partially written before a `TransformerException`.
