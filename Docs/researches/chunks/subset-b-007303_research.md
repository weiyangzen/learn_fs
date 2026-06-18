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
