# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007295`: lines 1-6139, `Docs/researches/chunks/subset-b-007295_research.md`
- `subset-b-007296`: lines 6140-12392, `Docs/researches/chunks/subset-b-007296_research.md`
- `subset-b-007297`: lines 12393-18672, `Docs/researches/chunks/subset-b-007297_research.md`
- `subset-b-007298`: lines 18673-24869, `Docs/researches/chunks/subset-b-007298_research.md`
- `subset-b-007299`: lines 24870-30908, `Docs/researches/chunks/subset-b-007299_research.md`
- `subset-b-007300`: lines 30909-37234, `Docs/researches/chunks/subset-b-007300_research.md`
- `subset-b-007301`: lines 37235-43512, `Docs/researches/chunks/subset-b-007301_research.md`
- `subset-b-007302`: lines 43513-44195, `Docs/researches/chunks/subset-b-007302_research.md`

## Chunk Research

### subset-b-007295: lines 1-6139

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 1-6139

## Chunk Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.19.1, not implementation source. It covers the XML prologue and API metadata from the beginning of the file through the first part of `org.apache.hadoop.fs.RawLocalFileSystem`. The XML records public/protected API compatibility details: packages, classes, interfaces, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, static/final/synchronized flags, deprecation text, and Javadoc contracts.

Because this is API XML, control flow, state, and persistence behavior are inferred from exposed signatures, inheritance relationships, documented contracts, and declared exceptions rather than method bodies. The range contains 37 class/interface declarations, 58 constructors, 440 method declarations, and 14 fields.

## Purpose

The chunk defines Hadoop 0.19.1's early public compatibility surface for configuration, distributed cache localization, and the core filesystem abstraction. It is important for API-diff and migration work because these classes are central integration points for nearly every Hadoop client, MapReduce task, file format, and filesystem backend.

The `org.apache.hadoop.conf` section documents how Hadoop objects receive and persist configuration. The `org.apache.hadoop.filecache` section documents how jobs localize files and archives onto task nodes. The `org.apache.hadoop.fs` section establishes the main file/path/stream/status abstractions used by local filesystems, checksum filesystems, Hadoop archives, in-memory filesystems, and the partial raw local filesystem entry visible at the end of this chunk.

## Important APIs and Types

### Version and Configuration

`org.apache.hadoop.HadoopVersionAnnotation` is a public annotation type used as a package attribute to capture the Hadoop version compiled into artifacts.

`Configurable` is the small interface for objects that can receive a `Configuration`, with `setConf(Configuration)` and `getConf()`. `Configured` is the base implementation and common superclass for command-style or service-style objects that need configuration injection.

`Configuration` is the main mutable configuration container. It implements `Iterable<Map.Entry<String,String>>` and `Writable`, so it can be iterated and serialized. Constructors support default loading, disabling default resources, and cloning another configuration. Resource-loading overloads accept classpath resource names, `URL`, `Path`, and `InputStream`. `reloadConfiguration()` is synchronized and clears loaded resource-derived values and final-parameter state so resources are re-read lazily.

Configuration accessors include raw and expanded `get`, typed `getInt`, `getLong`, `getFloat`, `getBoolean`, collection/string-array helpers, class loading helpers, and `set*` methods. `getLocalPath` and `getFile` choose a local directory from a configured directory list using the requested path, creating the selected directory if needed. `writeXml(OutputStream)`, `readFields(DataInput)`, and `write(DataOutput)` are persistence points. Docs define default resource order (`hadoop-default.xml`, then `hadoop-site.xml`), final parameters that cannot be overridden by later resources, and variable expansion from the configuration then Java system properties.

`Configuration.IntegerRanges` parses positive integer range expressions such as `2-3,5,7-` and exposes `isIncluded(int)` plus `toString()`.

### Distributed Cache

`DistributedCache` is a static utility surface for localizing read-only files, archives, and jars for MapReduce jobs. Its primary `getLocalCache(...)` overloads accept a cache URI, configuration, base cache directory, optional `FileStatus`, archive/file flag, expected modification timestamp, task work directory, and optional symlink behavior flag. The documented flow is: validate or reuse an existing localized cache entry, copy from the configured `FileSystem` when needed, unpack supported archive extensions (`.zip`, `.jar`, `.tar`, `.tgz`, `.tar.gz`), optionally create symlinks in the task working directory, and return the local file or unpacked directory path.

Other important APIs set and read cache declarations in `Configuration`: `setCacheArchives`, `setCacheFiles`, `getCacheArchives`, `getCacheFiles`, `addCacheArchive`, `addCacheFile`, localized path setters/getters, timestamp setters/getters, and classpath helpers for files and archives. `getTimestamp` reads remote modification time, `releaseCache` decrements or releases cache usage, `createAllSymlink` and `createSymlink` manage task-visible links, `checkURIs` validates symlink fragments and conflicts, and `purgeCache` clears all cached backing files.

The class integrates with `JobConf`, `FileSystem`, `FileStatus`, task working directories, archive extraction utilities, and classpath construction. Its main persistence is configuration entries plus localized files on worker disks. The timestamp contract is a key consistency guard: cache files should not be modified while a job is executing.

### Filesystem Metadata and Utility Types

`BlockLocation` implements `Writable` and stores block host names, datanode name strings, file offset, and length. It is the block-placement value returned by filesystem implementations for split locality and scheduling.

`FileStatus` implements `Writable` and `Comparable`. It represents client-visible metadata: length, directory flag, replication, block size, modification/access times, permission, owner, group, and path. Equality, ordering, and hash code are path-based. Protected setters normalize null permission/owner/group to defaults.

`ContentSummary` implements `Writable` and stores aggregate length, directory count, file count, optional namespace quota, space consumed, and space quota. It also formats `fs -count`-style output headers and rows.

`FileChecksum` is an abstract `Writable` for filesystem checksum values. Subclasses provide algorithm name, byte length, and bytes; equality requires both algorithm and value to match. `MD5MD5CRC32FileChecksum` is the visible concrete checksum type in this chunk, with binary and XML serialization helpers and a public `LENGTH` field.

`Path` is Hadoop's URI-backed file/directory name abstraction. Constructors support strings, URI components, and parent/child combinations. It exposes `toUri`, filesystem resolution, absolute checks, final name, parent, suffixing, string conversion, equality/hash/compare, depth, and qualification against a `FileSystem`. Public constants include `SEPARATOR`, `SEPARATOR_CHAR`, and `CUR_DIR`.

`PathFilter.accept(Path)` is the listing/globbing filter callback. `PositionedReadable` defines thread-safe reads from a given file position without changing the current stream offset.

### FileSystem Base Contract

`FileSystem` is the abstract base class for generic Hadoop filesystems. It extends `Configured` and implements `Closeable`. Static factories select implementations from configuration, using the default filesystem URI or URI scheme-specific `fs.<scheme>.class` keys; deprecated `parseArgs`, `getName`, and `getNamed` preserve older command-line/name APIs. `closeAll()` closes cached filesystems.

The class defines the main filesystem lifecycle and operation contract:

- Initialization and identity: abstract `initialize(URI, Configuration)` and `getUri()`, plus path qualification and protected `checkPath(Path)`.
- Discovery: `getFileBlockLocations(FileStatus,long,long)`, abstract `getFileStatus(Path)`, `exists`, `isFile`, deprecated `isDirectory`, deprecated `getLength`, `getContentSummary`, abstract `listStatus(Path)`, filtered and multi-path `listStatus` overloads, and `globStatus` with shell-style `?`, `*`, character classes, negation, escaping, and brace expansion.
- Reads and writes: abstract `open(Path,int)` plus default-buffer overload; many `create` overloads with overwrite, buffer size, replication, block size, permissions, and progress callbacks; `createNewFile`; and optional abstract `append(Path,int,Progressable)` with convenience overloads.
- Mutation: `setReplication`, abstract `rename`, deprecated one-argument `delete`, two-argument recursive `delete`, `deleteOnExit`, protected `processDeleteOnExit`, `mkdirs` overloads, `setPermission`, `setOwner`, and `setTimes`.
- Local transfer helpers: `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, `moveToLocalFile`, `startLocalOutput`, and `completeLocalOutput`.
- Defaults and accounting: `getHomeDirectory`, abstract working-directory accessors, `getUsed`, deprecated `getBlockSize`, `getDefaultBlockSize`, `getDefaultReplication`, `getFileChecksum`, static synchronized `getStatistics`, and `printStatistics`.

`FileSystem.Statistics` is a public static final nested counter object for bytes read and written. It exposes increment methods, getters, and `toString()`. `FSDataOutputStream` constructors can receive a `Statistics` instance to account writes.

### Checksum and Local Filesystem Layers

`ChecksumFileSystem` extends `FilterFileSystem` and provides a client-side checksum wrapper around a raw filesystem. It maps data files to checksum files, identifies checksum paths, calculates checksum file lengths, exposes bytes-per-sum, and overrides open/create/append/rename/delete/list/copy/local-output behavior to keep checksum sidecars in sync with data files. `reportChecksumFailure` gives implementations a hook to quarantine or retry after checksum errors.

`ChecksumException` carries the file position of a checksum error.

`LocalFileSystem` extends `ChecksumFileSystem`, wraps a raw local filesystem, converts `Path` to `File`, overrides local copy paths, and reports checksum failures by moving bad files aside on the same device so bad storage is not reused.

`RawLocalFileSystem` begins at the end of the chunk. The visible part shows direct local implementation methods for path-to-file conversion, URI/init, open, append, create with and without permissions, rename, delete, listStatus, mkdirs, home and working directory, deprecated lock/release, local moves, and the start of local-output handling. The class is incomplete in this chunk; following lines are required for the full API.

### Streams and Checksum Processing

`BufferedFSInputStream` wraps `FSInputStream` with buffering while preserving `Seekable` and `PositionedReadable`. It supports `seek`, `getPos`, `skip`, `seekToNewSource`, positional `read`, and `readFully`.

`FSInputStream` is the abstract seekable input primitive. It defines abstract `seek`, `getPos`, and `seekToNewSource`, plus positioned-read and readFully helpers.

`FSDataInputStream` wraps an input stream in a `DataInputStream` and implements seek and positioned reads. `seek` is synchronized; positional reads should not disturb the current stream offset through the `PositionedReadable` contract.

`FSOutputSummer` is an abstract output stream that chunks data, computes a checksum for each chunk, and calls subclass `writeChunk`. It buffers partial chunks, can flush/reset checksum buffers, and converts checksum values to byte arrays.

`FSInputChecker` is the matching abstract checksum-verifying input stream. Subclasses implement `readChunk` and `getChunkPosition`; the base class manages checksum verification, retry count, synchronized reads, seek/skip behavior, current position, checksum enablement, and mark/reset suppression. It can seek or skip past EOF without error, with later reads returning EOF.

`FSDataOutputStream` wraps an output stream in `DataOutputStream`, implements `Syncable`, exposes current position, close, wrapped stream access, and `sync()`.

### File and Disk Utilities

`FileUtil` is a static utility class for common filesystem operations: converting `FileStatus[]` to `Path[]`, recursive local deletion, deprecated filesystem recursive delete, copying between filesystems and between local `File` and `FileSystem`, merging directory files into one file, shell-safe local path conversion, local disk usage, unzipping and untarring archives, local symlink creation, `chmod`, temp-file creation near a base file, and replacement moves. `FileUtil.HardLink` creates hard links and reads link counts, with Unix, Cygwin, and Windows XP support noted.

`DF` and `DU` extend `Shell` to expose Unix `df` and `du` output. `DF` reports filesystem name, capacity, used, available, percent used, and mount for a directory, with configurable refresh interval. `DU` tracks directory disk usage, supports increment/decrement adjustments, starts a refresh thread, and can shut it down. Both parse shell output and have command-line `main` methods.

`LocalDirAllocator` allocates local paths across configured directories for a named configuration context such as `mapred.local.dir` or `dfs.client.buffer.dir`. It round-robins writes across directories, optionally checks space when expected file size is known, creates parent directories, creates delete-on-exit temp files, locates existing paths by scanning all configured dirs, and tracks one allocator per context per JVM. Its docs explicitly do not handle disks becoming read-only or full during an active write.

### Filesystem Implementations and Wrappers

`FilterFileSystem` contains a protected wrapped `FileSystem fs` and delegates the public filesystem surface to it: initialization, URI/name, qualification, block locations, open/create/append, replication, rename/delete/list, home and working directory, mkdirs, local copy helpers, local output helpers, default block size/replication, status/checksum, configuration, close, owner, and permission. It is the base for wrappers that transform behavior while preserving the same client contract.

`HarFileSystem` extends `FilterFileSystem` to expose Hadoop Archives. It initializes from `har://underlying-scheme-host:port/archivepath` or `har:///archivepath`, reads `_masterindex` and `_index` files, maps archive paths to `part-*` files, and returns fake EOF-bounded input streams for archived entries. It supports status, open, listStatus, block locations from the underlying filesystem, copy-to-local, URI, and archive version/hash helpers. Most mutation operations are documented as not implemented, and permissions are not persisted when archives are created.

`InMemoryFileSystem` extends `ChecksumFileSystem` for `ramfs://` storage. It assumes file lengths are known before creation and below a configured memory cap. `reserveSpaceWithCheckSum(Path,long)` must be called to reserve memory for both data and checksum files; the class exposes file enumeration, file counts, total in-memory filesystem size, and percentage used.

### Shell and URL Integration

`FsShell` is a configured `Tool` for command-line filesystem access. Visible APIs include initialization, current trash directory lookup, human-readable byte descriptions, two-decimal formatting, `run`, `close`, and `main`. Protected/public fields include the active `FileSystem` and date formats.

`FsUrlStreamHandlerFactory` implements `URLStreamHandlerFactory`. It creates handlers for schemes known to `FileSystem`, letting Java URL access delegate to Hadoop filesystem implementations through a shared configuration.

## Control Flow and Behavioral Contracts

The XML contains no method bodies, but the contracts imply several core flows:

- Configuration flow starts with constructor-selected default loading, then additional resources are layered in order, with final parameters blocking later overrides. Values set programmatically overlay loaded resources. `get` performs variable expansion; `getRaw` does not.
- Configurable object flow is uniform: components accept a `Configuration` through `setConf`, keep it for later `getConf`, and class-loading/resource lookup uses the configured class loader.
- Distributed cache flow starts with cache URIs stored in job configuration, timestamp capture before job launch, task-node localization through `getLocalCache`, optional archive extraction, optional symlink creation, and release/purge cleanup.
- Filesystem resolution flows from `Path` or `FileSystem.get(conf)` to a URI and scheme-specific implementation class. Implementations are initialized with the full URI and configuration, then all file operations use the common `FileSystem` contract.
- Read flow moves from `FileSystem.open` to `FSDataInputStream`/`FSInputStream`; callers may use sequential, seeked, or positioned reads. Checksum filesystems insert `FSInputChecker`-style verification before bytes reach the caller.
- Write flow moves through `FileSystem.create`/`append` overloads to `FSDataOutputStream`. Checksum filesystems insert `FSOutputSummer`-style checksum generation and checksum sidecar maintenance.
- Listing and globbing flow through `listStatus`, optional `PathFilter.accept`, and shell-style glob expansion. The docs distinguish missing plain paths from glob patterns with no matches.
- Local output flow lets clients write to a temporary local path and later call `completeLocalOutput` to copy or finalize into the target filesystem; local filesystems can write directly to the final target.
- Wrapper flow in `FilterFileSystem` forwards operations to the contained filesystem. Subclasses such as checksum and HAR filesystems override only the operations that need transformed behavior.

## State and Persistence

Persistent or durable state described by this chunk includes:

- JDiff XML itself, which persists the public API shape for Hadoop 0.19.1 compatibility comparison.
- `Configuration` resources and programmatic properties, including final-parameter metadata, default resource load state, class loader state, quiet mode, and serialized `Writable`/XML forms.
- Distributed cache state in configuration keys, HDFS or remote file timestamps, localized worker-node files, unpacked archive directories, symlinks, classpath entries, and cache usage/release bookkeeping.
- Filesystem data and metadata in backing stores: local disk, checksum sidecar files, Hadoop archive index/part files, raw local filesystem files, and in-memory `ramfs://` byte storage.
- `FileStatus`, `BlockLocation`, `ContentSummary`, `FileChecksum`, `MD5MD5CRC32FileChecksum`, and `Configuration` binary state through `Writable`.
- Stream positions in seekable input streams and output streams; `FSDataOutputStream` also integrates write-byte accounting through `FileSystem.Statistics`.
- `deleteOnExit` paths held by a `FileSystem` instance until close/JVM shutdown.
- Local directory allocator per-context JVM state tracking the last allocated directory and available configured directory lists.
- Disk usage monitor state in `DU`, including a refresh thread and mutable adjusted usage counters.

## Dependencies and Integration Points

Key dependencies visible in the API:

- Java core APIs: `java.io` streams/files/data input/output/readers, `IOException`, `java.net.URI`/`URL`, class loaders, annotations, collections, and `java.util.zip.Checksum`.
- Hadoop common APIs: `Configuration`, `Configurable`, `Writable`, `Path`, `FileStatus`, `BlockLocation`, `FileChecksum`, `FsPermission`, `Progressable`, `Tool`, `Shell`, and `Syncable`.
- Commons Logging via public `LOG` fields in filesystem/checksum code.
- External XML support through `org.znerd.xmlenc.XMLOutputter` and SAX `Attributes` for checksum XML serialization.
- Native or platform shell commands for `df`, `du`, `chmod`, symlink creation, and hard link behavior.
- MapReduce integration through `DistributedCache`, `JobConf`, task working directories, Mapper/Reducer use of localized files, and classpath augmentation for task JVMs.

The architectural center is `FileSystem`: `Path`, stream wrappers, metadata values, shell commands, URL handlers, distributed cache localization, archive filesystems, checksum filesystems, and local/raw filesystems all integrate through that abstraction.

## Risks and Edge Cases

- This chunk is API metadata only. It does not expose implementation details such as exact synchronization beyond JDiff flags, cache eviction maps, checksum retry loops, or resource cleanup behavior.
- The file range ends inside `RawLocalFileSystem`, so final per-file synthesis must merge the next chunk before claiming a complete raw local filesystem API.
- `Configuration` final parameters and lazy reload behavior can surprise callers that expect later resources or programmatic changes to overwrite everything.
- Variable expansion falls back to Java system properties, so missing configuration keys may still resolve from process-global state.
- Typed configuration getters return defaults on missing or invalid values, which can hide malformed configuration unless tests assert bad-value behavior.
- Distributed cache correctness depends on stable remote modification timestamps; mutating cached files during job execution can make localized data inconsistent.
- Symlink creation requires URI fragments and no fragment conflicts. Missing fragments or duplicate link names are explicitly invalid when symlinks are requested.
- `DistributedCache.purgeCache` is destructive and documented as appropriate only during server reinitialization.
- Checksum sidecar files must remain consistent with data files across rename, delete, copy, append, and local-output operations.
- `FSInputChecker` permits seek/skip past EOF with later reads returning EOF; callers may not receive an immediate error for out-of-range navigation.
- `FileStatus` equality and ordering are path-based, not full metadata-based, which can hide metadata differences in sets/maps.
- `Path` strings are URI-like but use unescaped elements and Hadoop-specific normalization, so ordinary Java URI assumptions may not hold.
- `FileUtil` shell operations, hard links, symlinks, and permission changes are platform-sensitive.
- `LocalDirAllocator` does not handle disks becoming read-only or full after allocation; write-time failures still need downstream handling.
- HAR filesystems are read-oriented; many mutating methods are explicitly not implemented, and archive entry permissions are not persisted.
- `InMemoryFileSystem` requires ahead-of-time size reservation because normal `FileSystem` create APIs do not provide file size.
- Deprecated APIs remain present (`FileSystem.parseArgs`, `getName`, `getNamed`, one-argument `delete`, `getReplication`, `getLength`, `getBlockSize`, raw local lock/release), so compatibility tests should preserve them while migration code avoids new reliance.

## Test Signals

Good test coverage inferred from this chunk should include:

- XML/JDiff validation for well-formedness and preservation of all classes, methods, constructors, fields, visibility flags, exception declarations, and deprecation text in lines 1-6139.
- `Configuration` tests for default resource order, disabling defaults, resource overlay order, final-parameter blocking, variable expansion, `getRaw`, typed default behavior on invalid values, class loading, local path selection, reload semantics, iteration, XML output, and `Writable` round trips.
- `Configuration.IntegerRanges` parsing tests for closed ranges, open-ended ranges, singletons, comma-separated values, and inclusion checks.
- `Configurable`/`Configured` tests for configuration propagation into configured utilities and class-loader-dependent object creation.
- `DistributedCache` tests for cache file/archive declaration, timestamp storage/validation, cache localization, reuse, release, purge, archive extraction formats, classpath additions, symlink creation, fragment conflict detection, and missing-fragment failures.
- `FileSystem` contract tests for URI/default resolution, path qualification, create/open/append/delete/recursive delete/rename/mkdirs/list/status/glob/copy/local-output flows, `deleteOnExit`, metadata mutation, checksum retrieval defaulting to null, default block size/replication, and statistics increments.
- Glob tests for `?`, `*`, character classes, negation, escaping, brace expansion, sorted results, plain missing path returning null, and glob no-match returning an empty array.
- Stream tests for `FSInputStream`, `BufferedFSInputStream`, and `FSDataInputStream`: seek, `getPos`, skip, positioned reads preserving current offset, readFully exactness, and `seekToNewSource`.
- Checksum stream/filesystem tests for checksum generation, verification, checksum file naming/length, checksum failure position reporting, retry/quarantine behavior, sidecar rename/delete/copy consistency, and checksum-disabled paths where applicable.
- `FSOutputSummer` and `FSDataOutputStream` tests for chunking, direct large writes, buffer flushing, checksum byte conversion, output position, close, wrapped stream access, and `sync()`.
- Metadata `Writable` tests for `BlockLocation`, `FileStatus`, `ContentSummary`, `FileChecksum` subclasses, and checksum XML serialization/parsing.
- `FileUtil` tests for recursive delete partial failure behavior, filesystem-to-filesystem copy, local-to-filesystem copy, filesystem-to-local copy, copyMerge, archive extraction, shell path conversion, symlink/hardlink behavior, chmod, temp-file creation, replaceFile, and local disk usage.
- `DF`/`DU` tests with controlled shell output parsing, refresh intervals, DU adjustment methods, thread start/shutdown, and platform variance.
- `FilterFileSystem` delegation tests ensuring every visible method forwards to the wrapped filesystem unless intentionally overridden by a subclass.
- `HarFileSystem` tests for URI parsing, version reading, archive hash lookup, status/list/open behavior from `_masterindex`/`_index` and `part-*`, block locations from the underlying filesystem, read-only mutation failures, copy-to-local, and permission limitations.
- `InMemoryFileSystem` tests for reservation success/failure, checksum reservation, configured capacity, file enumeration/counts, and percentage used.
- `LocalDirAllocator` tests for round-robin directory selection, unknown-size writes, size-aware writes, temp-file creation, existing-path lookup, invalid contexts, missing files, and disk-full/read-only simulation.
- `Path` tests for constructor normalization, URI conversion, absolute path behavior, parent/name/suffix/depth, equality/order/hash, and filesystem qualification.
- `RawLocalFileSystem` tests should be completed after reading the next chunk, because this chunk only contains the beginning of the class.

## Chunk Boundary Notes

This chunk starts at the beginning of the JDiff file and has complete coverage for the configuration, distributed cache, and many filesystem classes listed above. It ends partway through `RawLocalFileSystem`, immediately after the visible `startLocalOutput` method declaration begins. The next chunk is required for complete raw local filesystem behavior and any following `org.apache.hadoop.fs` APIs.

### subset-b-007296: lines 6140-12392

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 6140-12392

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.1, not executable Java implementation code. It starts in the tail of `org.apache.hadoop.fs.RawLocalFileSystem`, then covers public API metadata for filesystem stream contracts, trash handling, FTP/Kosmos/S3 filesystem adapters, permissions, shell commands, the embedded HTTP server, and a large portion of the core `org.apache.hadoop.io` serialization/file-format package. It ends after `org.apache.hadoop.io.SequenceFile.Sorter.RawKeyValueIterator`, so later `org.apache.hadoop.io` APIs are outside this chunk.

The XML records compatibility data: package, class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, return types, declared exceptions, fields, visibility, abstract/static/final/synchronized/native flags, deprecation text, and embedded Javadoc contracts. Because this range begins inside `RawLocalFileSystem`, the opening class metadata for that type is in an earlier chunk.

## Purpose and Major API Surface

The visible `RawLocalFileSystem` tail exposes local-output completion, close/string/status operations, and Unix-style `setOwner`/`setPermission` behavior that delegates to `chown` and `chmod`. `Seekable` defines positional input streams through `seek(long)`, `getPos()`, and `seekToNewSource(long)`. `Syncable` defines `sync()` for flushing buffered stream state to underlying devices. `Trash` provides user trash management under `.Trash/current`, checkpointing, expunging old checkpoints, and a superuser emptier runnable.

`org.apache.hadoop.fs.ftp` contains `FTPException`, `FTPFileSystem`, and `FTPInputStream`. `FTPFileSystem` is a `FileSystem` backed by Apache Commons Net `FTPClient`, with initialize/open/create/delete/list/status/mkdir/rename/working-directory APIs and public constants for logging, buffer size, and block size. Its create contract warns that the returned stream must be closed before using other APIs on the filesystem or later invocations can block. `append` is explicitly unsupported, and the one-argument `delete(Path)` is deprecated in favor of `delete(Path, boolean)`. `FTPInputStream` adapts an FTP input stream to `FSInputStream`, tracking position, synchronized reads, close, and unsupported mark/reset style behavior.

`org.apache.hadoop.fs.kfs.KosmosFileSystem` is a `FileSystem` backed by KFS. It exposes URI/name/working-directory methods, directory and file probes, list/status, create/open/rename/delete, replication and block-size accessors, file locking, block-location lookup, and local-copy/local-output hooks. As with FTP and S3, append is documented as unsupported.

`org.apache.hadoop.fs.permission` defines the filesystem permission model. `AccessControlException` is the checked permission failure type. `FsAction` is an enum-like permission action with implication and boolean operations (`and`, `or`, `not`) plus octal and symbolic fields. `FsPermission` is a `Writable` for user/group/other action triples, short-mode encoding, immutable creation, umask application, configuration-backed umask getters/setters, default permissions, and symbolic string parsing. `PermissionStatus` combines user, group, and `FsPermission`, supports immutable construction, umask application, binary read/write, static component serialization, and string formatting.

The `org.apache.hadoop.fs.s3` package documents the legacy block-based S3 filesystem. `Block` is block metadata. `FileSystemStore` is the storage backend contract for versioning, INode and block storage/retrieval/deletion, shallow/deep subpath listing, test purge, and diagnostic dump. `INode` stores file type and block pointers and can serialize/deserialize itself; it exposes `FILE_TYPES` and a reusable `DIRECTORY_INODE`. `MigrationTool` is a `Tool` that rewrites block metadata when migrating old S3 filesystem versions without touching data files. `S3Credentials` extracts AWS credentials from URI or `Configuration`. `S3Exception`, `S3FileSystemException`, and `VersionMismatchException` represent S3 communication, fatal filesystem, and on-disk version compatibility failures. `S3FileSystem` is the block-based `FileSystem`, with permission arguments documented as ignored and append unsupported.

`org.apache.hadoop.fs.s3native.NativeS3FileSystem` is the native-object S3 filesystem. Unlike the block-based S3 adapter, its documentation states that it stores files in native S3 form readable by other S3 tools. It exposes initialize, create/open/delete/list/mkdir/rename/status, working-directory, URI, and logging APIs. Its `listStatus` Javadoc is operationally important: listing a file makes one S3 call, while listing a directory makes up to `(n / 1000) + 2` S3 calls for `n` direct children. Append is unsupported.

`org.apache.hadoop.fs.shell` contributes shell command plumbing. `Command` is an abstract `Configured` base with protected `args`, abstract `getCommandName()` and path-level `run(Path)`, and public `runAll()` to execute over every source path. `CommandFormat` parses command options and enforces argument format. `Count` implements the count command, with command matching, name, path execution, and public `NAME`, `USAGE`, and `DESCRIPTION` constants for counting directories, files, bytes, quota, and remaining quota.

`org.apache.hadoop.http` covers servlet/filter integration and the embedded status web server. `FilterContainer` adds named filters with class names and init parameters. `FilterInitializer` is the extension point for initializing filters. `HttpServer` wraps Jetty (`org.mortbay.jetty.Server`, `SocketListener`, `WebApplicationContext`) and exposes default webapps/servlets, context addition, attributes, public/internal servlet registration, filter definition/path mapping, webapp path lookup, port/thread control, SSL listener configuration, start/stop, and mutable server/filter/context fields. `addInternalServlet` is marked deprecated as a temporary method. `HttpServer.StackServlet` is an `HttpServlet` with `doGet` for stack dumps.

The `org.apache.hadoop.io` section begins with serialization class registries and array helpers. `AbstractMapWritable` tracks byte-to-class and class-to-byte mappings, is `Configurable`, and serializes those mappings for map-like Writables. `ArrayFile` extends `MapFile`; its `Reader` provides index-based seek, next, key, and get operations, while its `Writer` has constructors for writable element classes and optional compression/progress. `ArrayWritable` wraps arrays of a fixed Writable value class and supports read/write, get/set, and Java array conversion.

Primitive and binary writable types include `BinaryComparable`, `BooleanWritable`, `BytesWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, `LongWritable`, and nested raw comparators. These classes provide mutable set/get methods, `Writable` read/write, equality/hash/compare/string behavior, and optimized `WritableComparator` subclasses over serialized bytes. `BytesWritable` distinguishes logical length from backing capacity, has deprecated `get()` and `getSize()` in favor of `getBytes()` and `getLength()`, preserves data during resizing, and sorts like `memcmp`.

Buffering and stream utilities include deprecated `org.apache.hadoop.io.Closeable` as an alias for `java.io.Closeable`, `CompressedWritable` for lazily inflated compressed Writable payloads, `DataInputBuffer` and `DataOutputBuffer` reusable in-memory `DataInput`/`DataOutput` implementations, `InputBuffer` and `OutputBuffer` reusable stream buffers, and `IOUtils` helpers for byte copying, exact reads/skips, cleanup, and close of streams/sockets. `IOUtils.NullOutputStream` discards written bytes.

Dynamic serialization helpers include `DefaultStringifier`, `GenericWritable`, `ObjectWritable`, `RawComparator`, `MapWritable`, and `MultipleIOException`. `DefaultStringifier` converts objects to/from Base64 encoded serialized strings using `SerializationFactory` and can store/load single objects or arrays in `Configuration`. `GenericWritable` wraps one of a fixed subclass-provided type set, trading flexibility for smaller per-record type encoding than `ObjectWritable`. `ObjectWritable` serializes Writables, strings, primitive types, and arrays with declared-class metadata and is `Configurable`. `RawComparator<T>` extends `Comparator<T>` with byte-range comparison. `MapWritable` implements `Map<Writable, Writable>` with serialized class mapping support. `MultipleIOException` wraps a list of `IOException`s or returns a convenient single `IOException`.

`MapFile` and its nested reader/writer define an indexed, sorted file-based map. A map directory contains `data` and `index` sequence files; the index is loaded into memory, so key size matters. Static helpers rename/delete map directories, rebuild corrupt indexes with `fix`, and expose `INDEX_FILE_NAME` and `DATA_FILE_NAME`. `MapFile.Reader` opens data/index readers, supports reset, approximate middle key, final key, seek, next, get, closest-key lookup including a `before` option, and close. `MapFile.Writer` creates sorted maps over key classes or comparators, configures index interval globally or per writer, closes, and appends only keys greater than or equal to the previous key.

Hash/null wrappers include `MD5Hash`, `MD5Hash.Comparator`, `NullWritable`, and `NullWritable.Comparator`. `MD5Hash` is a fixed-length `WritableComparable` with constructors from bytes or hex, static digest helpers for byte arrays, ranges, strings, UTF8, and streams, half/quarter digest projections, hex parsing, and raw comparison. `NullWritable` is a singleton zero-state `WritableComparable`, useful where a key or value position carries no payload.

`SequenceFile` is the central flat binary key/value file format. Its static API gets/sets configured compression type and creates writers through many overloads spanning default filesystem lookup, explicit `FileSystem`, path, key/value classes, buffer size, replication, block size, compression type, codec, metadata, progress callback, and raw key/value writer construction. `SYNC_INTERVAL` defines sync-point spacing. `SequenceFile.CompressionType` enumerates compression modes. `SequenceFile.Metadata` is a `Writable` map of `Text` keys/values with get/set, serialization, equality, hash, and string behavior. `SequenceFile.Reader` opens files, exposes key/value class names and classes, compression flags, codec, metadata, current-value retrieval, object and Writable iteration, raw record/key/value reads, seek, sync, syncSeen, position, and close. `SequenceFile.Sorter` sorts and merges SequenceFiles using WritableComparable keys or a `RawComparator`, configurable merge factor, memory budget, progress reporting, sort-to-file, sort-and-iterate, merge overloads, attribute cloning, and writing records from raw iterators. `SequenceFile.Sorter.RawKeyValueIterator` exposes current raw key/value, `next()`, `close()`, and progress.

## Control Flow and Behavioral Contracts

The XML contains no bodies, but its public contracts imply several flows. Seekable streams are positioned with `seek`, report offsets with `getPos`, and may switch replicas/sources with `seekToNewSource`; callers must not seek past EOF according to the interface documentation. Syncable writers expose an explicit durability/liveness boundary through `sync`.

Trash flow constructs a `Trash` against a `Configuration` or explicit `FileSystem`, moves deleted paths under the user's home `.Trash/current` while preserving original paths, periodically checkpoints `current`, and expunges older checkpoints. The design intentionally avoids full trash enumeration, filesystem date support, and cross-host clock synchronization.

Concrete `FileSystem` adapters follow the Hadoop `FileSystem` lifecycle: initialize with a `URI` and `Configuration`, resolve a working directory, create/open streams, list/status paths, create directories, rename/delete, and return `FileStatus`/`BlockLocation` metadata. Optional append is consistently documented as unsupported for FTP, KFS, S3, and native S3 in this chunk. FTP create has a stricter sequencing contract: close the returned stream before invoking other `FTPFileSystem` APIs.

S3 block filesystem flow splits namespace metadata from data blocks. `S3FileSystem` talks to a `FileSystemStore`; files are represented by `INode` metadata containing `Block` pointers. Migration rewrites block metadata for all files without rewriting data files. Native S3 flow instead uses S3-native objects and has listing costs tied directly to S3 pagination.

Permission flow converts between symbolic actions, short Unix modes, umask-adjusted effective permissions, and binary `Writable` encodings. `PermissionStatus` combines principal names and permissions so filesystem metadata can be serialized as a single unit.

Shell command flow creates a command object with captured arguments, parses options with `CommandFormat`, and dispatches `run(Path)` once per source path through `runAll()`. `Count` plugs into this base to implement the quota/size/count command.

HTTP server flow constructs a Jetty server, adds default apps and servlets, registers contexts/servlets/filters, starts the listener, and later stops it. Attributes are set on the web application context for JSP/servlet access. Filter registration includes both container-level definition and path mapping.

Writable flow is stable binary serialization: mutate object state with setters, write fields to `DataOutput`, reconstruct with `readFields(DataInput)`, and use raw comparators where possible to avoid object allocation in sort-heavy paths. Primitive Writable comparators must preserve the same ordering as object `compareTo`.

MapFile flow writes sorted key/value records into a `data` file and periodic index entries into an `index` file. Readers load the index, seek close to a requested key, then scan data through `SequenceFile.Reader`. The writer enforces nondecreasing key order; callers must sort updates externally, often through `SequenceFile.Sorter`, before appending.

SequenceFile flow writes flat binary records with optional compression and sync markers. Readers can iterate typed objects, skip values, pull raw key/value bytes, seek to known writer positions, or sync forward from arbitrary positions to a sync marker. Sorter flow spills sorted runs, merges with configurable fan-in and memory, optionally deletes inputs, and returns raw iterators or writes final files.

## State, Persistence, and Side Effects

The XML file itself is persistent API compatibility metadata. The documented runtime APIs persist filesystem metadata, permissions, Writable objects, MapFiles, SequenceFiles, S3 inode/block records, and configuration-encoded stringified objects.

External side effects are significant. Filesystem implementations touch local files, FTP servers, KFS, and Amazon S3. `RawLocalFileSystem.setOwner` and `setPermission` invoke OS-level ownership/permission commands. Trash moves, checkpoints, and deletes filesystem content. S3 migration rewrites metadata. Native S3 listing can perform many remote calls. HTTP server methods bind sockets, register web applications, publish servlets/filters, and expose stack traces through `StackServlet`. Shell commands iterate over filesystem paths and can print or report failures.

Mutable in-memory state includes working directories, filesystem URIs, FTP client/input-stream position, KFS locks, permission objects, class-ID maps inside `AbstractMapWritable`, backing arrays and capacities in bytes/buffers, wrapped objects in `GenericWritable`/`ObjectWritable`, map entries in `MapWritable`, digest bytes in `MD5Hash`, sequence file reader positions and sync-state, sorter memory/factor/progress settings, MapFile index contents, and Jetty server/context/filter lists.

Threading contracts are selective. Some stream and reader APIs are marked synchronized (`FTPInputStream.read/close`, many `MapFile.Reader` methods, `MapFile.Writer.close/append`, and multiple `SequenceFile.Reader` methods), but most containers and filesystem wrappers are not documented as globally thread-safe. Reusing mutable Writables across reads is expected by Hadoop APIs but requires caller discipline.

## Dependencies and Integration Points

The filesystem APIs integrate with `org.apache.hadoop.fs.FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `FSDataInputStream`, `FSDataOutputStream`, `FSInputStream`, `FileSystem.Statistics`, `Configuration`, `Configured`, `Progressable`, and `FsPermission`. FTP depends on Apache Commons Net `FTPClient` and Commons Logging. KFS depends on the Kosmos filesystem backend. S3 APIs depend on Amazon S3 semantics, URI/configuration credential lookup, Java `File` temp block transfers, and Hadoop `Tool` for migration.

Permissions depend on Hadoop `Writable`, Java `DataInput`/`DataOutput`, Unix mode conventions, and `Configuration` for umask persistence. Shell commands integrate with Hadoop CLI dispatch, `Configuration`, and filesystem path operations.

The HTTP layer integrates with servlet APIs (`javax.servlet`, `javax.servlet.http.HttpServlet`) and Jetty 6-era Mortbay classes (`Server`, `SocketListener`, `WebApplicationContext`). It also uses Commons Logging and map/list collections for filter and context state.

The `org.apache.hadoop.io` APIs are foundational dependencies for MapReduce, SequenceFile/MapFile storage, RPC payloads, sorting, and configuration persistence. They integrate with Java streams, byte arrays, `DataInput`/`DataOutput`, `InputStream`/`OutputStream`, `Closeable`, `Comparator`, `Map`, `TreeMap`, `MessageDigest`/MD5, Hadoop `Configuration`, `Configurable`, `ReflectionUtils`-style instantiation through class metadata, compression codecs, and `SerializationFactory`.

Compatibility tooling depends on the exact JDiff XML attributes. Public signature changes, removed overloads, altered generic type strings, changed synchronization/deprecation flags, or changed documented contracts in these APIs would alter the Hadoop 0.19.1 API surface.

## Risks and Compatibility Notes

This chunk is partial at the start. It should not be used alone to summarize all of `RawLocalFileSystem`; only its visible tail is covered here. The `org.apache.hadoop.io` package also continues beyond this chunk in later lines.

Filesystem adapter behavior is backend-sensitive. FTP stream sequencing can deadlock/block if callers ignore the close-before-next-API rule. S3 and native S3 have different persistence formats, so migration and interoperability assumptions must not be mixed. Native S3 directory listing can cause large remote-call counts. Permission parameters are documented as ignored by the block-based S3 filesystem in this snapshot.

Append is a compatibility trap: several filesystems expose the method because of the `FileSystem` contract, but explicitly document it as unsupported. Callers must handle `IOException`/unsupported behavior rather than assuming append works everywhere.

Permission serialization and umask behavior are compatibility-sensitive. Changes to octal encoding, symbolic parsing, `FsAction` implication logic, static umask configuration keys, or `PermissionStatus` read/write order can break filesystem metadata compatibility.

HTTP server APIs expose mutable Jetty internals and a deprecated temporary internal-servlet method. Changes to context/filter mapping, default app setup, port selection, SSL listener configuration, or stack servlet behavior can break NameNode/DataNode-style web UIs and operational diagnostics.

Writable and comparator compatibility is high risk. Binary read/write order, class-ID mappings, raw comparator byte interpretation, primitive endianness, BytesWritable length/capacity semantics, MD5 hex parsing, and NullWritable singleton behavior are all used by persisted files and sort paths. Raw comparators must match object comparison exactly.

MapFile and SequenceFile are persistent file formats. Changes to `data`/`index` names, index interval behavior, sorted append requirements, sync marker handling, metadata serialization, compression flags/codecs, raw iterator contracts, or seek/sync positioning can break old data and MapReduce shuffle or storage workflows.

Dynamic wrappers (`GenericWritable`, `ObjectWritable`, `DefaultStringifier`, `MapWritable`) depend on class names and configured serialization implementations. Missing classes, class-ID drift, generic raw types, or configuration changes can make persisted values unreadable.

## Test Signals

JDiff validation should confirm this XML chunk remains well-formed across all listed package/class/interface boundaries and preserves signatures, constructors, fields, implemented interfaces, visibility, exceptions, static/final/abstract/synchronized flags, deprecation markers, and Javadoc contracts. Chunk-aware validation should account for the partial `RawLocalFileSystem` start.

Filesystem tests should cover Seekable seek/getPos/source-switch behavior, Syncable sync propagation, Trash move/checkpoint/expunge/emptier behavior, FTP initialize/open/create/close sequencing/list/status/mkdir/rename/delete, unsupported append paths, KFS status/block-location/lock/release/local-copy behavior, S3 block filesystem create/open/list/status/delete/rename/migration/version mismatch, native S3 create/open/list pagination/status/delete/rename, and permission arguments documented as ignored where applicable.

Permission tests should round-trip `FsPermission` and `PermissionStatus` through `DataOutput`/`DataInput`, verify `FsAction` implication/and/or/not, short and symbolic parsing, default permissions, umask get/set/apply behavior, immutable factory behavior, string formatting, and access-control exception wrapping/unwrapping.

Shell and HTTP tests should cover `CommandFormat` option parsing and argument bounds, `Command.runAll()` success/failure aggregation over multiple paths, `Count.matches` and count output behavior, filter initializer/container registration, servlet/context addition, attribute get/set, filter path mapping, default apps/servlets, port selection with `findPort`, thread setting, SSL listener setup, start/stop lifecycle, and `StackServlet.doGet` output.

Writable tests should round-trip primitive Writables, BytesWritable size/capacity mutations, arrays, compressed writables, map writables, generic/object writables, MD5 hashes, NullWritable, and buffer classes. Comparator tests should compare object ordering against raw byte ordering for every optimized comparator in this chunk, including increasing and decreasing long comparators.

IO utility and buffer tests should exercise `copyBytes` overloads, exact `readFully` and `skipFully`, cleanup/close behavior with multiple close failures, null output writes, input/output buffer reset/getPosition/getLength, and direct writes from `DataInput` or `InputStream` into reusable buffers.

DefaultStringifier and dynamic serialization tests should store/load single objects and arrays from `Configuration`, cover empty-array failure, verify configured `SerializationFactory` use, and test missing or incompatible classes in `ObjectWritable`, `GenericWritable`, and `MapWritable`.

MapFile tests should write sorted entries, reject or fail on out-of-order append according to implementation behavior, verify index interval configuration, read `midKey` and `finalKey`, seek exact and nearest keys, use `getClosest` before/after modes, reset readers, rebuild corrupt indexes with `fix` dry-run and write modes, and preserve `data`/`index` filenames.

SequenceFile tests should create writers through representative overloads, cover no compression, record compression, and block compression, verify metadata persistence, sync interval/sync marker behavior, seek to writer positions, sync from arbitrary positions, typed and raw iteration, skip-value reads, current-value retrieval, deprecated raw `next(DataOutputBuffer)` compatibility, sorter memory/factor/progress settings, sort-and-iterate, merge fan-in and input deletion, clone-file-attributes, and raw iterator progress/close behavior.

### subset-b-007297: lines 12393-18672

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 12393-18672

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.1, not Java implementation source. The range starts immediately after `org.apache.hadoop.io.SequenceFile.Sorter.RawKeyValueIterator`, covers the rest of a large part of `org.apache.hadoop.io`, all visible compression/retry/serializer APIs in the range, the Hadoop IPC/RPC API surface, RPC metrics/JMX interfaces, runtime log-level control, and ends inside the opening part of `org.apache.hadoop.mapred.ClusterStatus`.

The XML records compatibility metadata: packages, classes/interfaces, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation notes, and embedded Javadocs. Research below is based on those signatures and docs. This is a line-bounded chunk: the containing `org.apache.hadoop.io` package began before this range, `SequenceFile` began before this range, and `ClusterStatus` continues after this range.

## Purpose and Major API Surface

The opening `org.apache.hadoop.io` section is the core serialization and sequence-file API surface. `SequenceFile.Sorter.SegmentDescriptor` models a merge segment with file offset, length, and `Path`; it implements `Comparable`, reads raw keys and raw values, exposes the stored raw key as a `DataOutputBuffer`, can perform sync checks, can preserve or delete input files, and has overridable cleanup semantics. `SequenceFile.ValueBytes` abstracts raw sequence-file value bytes, with methods to write uncompressed or compressed bytes and report stored size. `SequenceFile.Writer` writes sequence-format key/value files over a `FileSystem` and `Path`, exposes key/value classes and compression codec, supports explicit sync points, synchronized close and append methods, raw append, current synchronized output length, and protected serializers for keys and compressed/uncompressed values.

`SetFile` is a `MapFile` specialization for key-only sets. `SetFile.Reader` seeks, iterates, and resolves matching `WritableComparable` keys. `SetFile.Writer` appends strictly increasing keys, supports element-class or comparator construction, accepts `SequenceFile.CompressionType`, and preserves a deprecated constructor that lacks a `Configuration`.

`SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap<WritableComparable, Writable>`. It exposes the standard sorted-map view operations (`firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`, `entrySet`, `keySet`, `values`) plus mutators and `Writable` serialization through `readFields` and `write`. `Stringifier<T>` is a closeable object/string conversion contract with `toString`, `fromString`, and `close`.

`Text` is the main mutable UTF-8 string type, extending `BinaryComparable` and implementing `WritableComparable<BinaryComparable>`. It exposes byte storage access, byte length, Unicode scalar lookup by byte position, substring search, setters from `String`, byte arrays, and other `Text` values, appending, clearing, string conversion, `Writable` read/write, static string read/write helpers, static UTF-8 decode/encode helpers, UTF-8 validation, code-point extraction, and UTF-8 length calculation. `Text.Comparator` is an optimized raw `WritableComparator`.

`TwoDArrayWritable` serializes two-dimensional arrays of a fixed `Writable` value class. `UTF8` is the deprecated predecessor to `Text`, with comparable byte/string storage, `WritableComparable` methods, static UTF-8 helpers, and `UTF8.Comparator`. `VersionedWritable` adds version checking to `Writable` implementations via abstract `getVersion`, and `VersionMismatchException` reports mismatched byte versions.

`VIntWritable` and `VLongWritable` are mutable variable-length encoded integer/long `WritableComparable` types with set/get, read/write, equality/hash, comparison, and string conversion. `Writable` defines Hadoop's binary serialization contract, and `WritableComparable<T>` combines `Writable` with Java `Comparable<T>`.

`WritableComparator` is the central raw comparator registry and byte-level comparison utility. It constructs comparators for `WritableComparable` classes, can instantiate keys, compares either serialized byte slices or deserialized objects, registers optimized comparators, and exposes byte parsing helpers for unsigned short, int, float, long, double, vint, and vlong. `WritableFactories` maps classes to `WritableFactory` instances and creates new `Writable` instances with optional `Configuration`. `WritableName` maps writable implementation classes to stable aliases and back. `WritableUtils` provides compressed byte/string array IO, string array IO, display helpers, deep clone/cloneInto by serialization, variable-length integer/long encoding and decoding, enum read/write, `skipFully`, and conversion of multiple writables to a byte array.

The `org.apache.hadoop.io.compress` section defines Hadoop's stream compression abstraction. `CompressionCodec` creates input/output compression streams with or without pooled `Compressor`/`Decompressor` instances, reports compressor/decompressor classes, constructs compressor/decompressor instances, and gives a default file extension. `CodecPool` rents and returns reusable compressor/decompressor objects. `CompressionCodecFactory` discovers configured codec classes, maps file suffixes to codecs, removes suffixes, exposes codec classes for configuration, has a diagnostic `main`, and logs through Commons Logging.

`CompressionInputStream` and `CompressionOutputStream` are base wrappers over `InputStream` and `OutputStream` with `resetState`, plus close/flush/read/write/finish behavior as applicable. `Compressor` and `Decompressor` are state-machine interfaces for setting input/dictionaries, testing need for input or dictionaries, reporting bytes read/written, finishing, compressing/decompressing byte slices, resetting reusable state, and ending native resources.

`BZip2Codec`, `DefaultCodec`, `GzipCodec`, `LzoCodec`, and `LzopCodec` are codec implementations. `DefaultCodec` is `Configurable`; `GzipCodec` adds gzip-specific nested input/output streams; `LzoCodec` and `LzopCodec` expose native LZO availability and lzop container behavior. `LzopCodec.LzopDecompressor` handles lzop headers and data/compressed checksum verification, while `LzopInputStream` and `LzopOutputStream` read/write lzop headers around block compressor streams.

`org.apache.hadoop.io.compress.bzip2` exposes pure-Java bzip2 building blocks. `BZip2Constants` defines block-size, Huffman, run marker, selector, and overshoot constants. `BZip2DummyCompressor` and `BZip2DummyDecompressor` satisfy the generic compressor interfaces for stream wrappers that do their own work. `CBZip2InputStream` and `CBZip2OutputStream` implement bzip2 stream decoding/encoding without the file header bytes; output includes block-size selection, Huffman code-length generation, finish/close/flush, and many algorithm constants.

`org.apache.hadoop.io.compress.lzo` exposes native LZO compressor/decompressor classes and compression-strategy enums. Both report native availability and native library version. The compressor follows the generic compressor state machine; the decompressor adds dictionary requirements and a `finalize` cleanup hook. `org.apache.hadoop.io.compress.zlib` provides built-in `Deflater`/`Inflater` adapters, native-capable `ZlibCompressor` and `ZlibDecompressor`, enum types for compression header, compression level, and compression strategy, and `ZlibFactory` selection between native zlib and built-in Java implementations.

`org.apache.hadoop.io.retry` defines retry policy construction and dynamic retry proxies. `RetryPolicies` exposes constants for fail, ignore, and forever-retry behavior plus factories for fixed-sleep retry by count or maximum time, proportional sleep, exponential backoff, retry-by-exception, and retry-by-remote-exception. `RetryPolicy.shouldRetry(Exception, int)` decides whether another attempt should run or throws. `RetryProxy.create` wraps an implementation behind a Java proxy using either one policy or a method-name-to-policy map.

`org.apache.hadoop.io.serializer` defines pluggable object serialization. `Serializer<T>` opens an `OutputStream`, serializes values, and closes. `Deserializer<T>` opens an `InputStream`, deserializes into an optional reuse instance, and closes. `Serialization<T>` accepts classes and returns serializers/deserializers. `SerializationFactory`, a `Configured` class, chooses a registered serialization for a class. `WritableSerialization` handles Hadoop `Writable` types; `JavaSerialization` handles `Serializable`; `DeserializerComparator` and `JavaSerializationComparator` implement raw comparison by deserializing objects and comparing them.

`org.apache.hadoop.ipc` defines Hadoop's Writable-based IPC and RPC layer. `Client` sends `Writable` parameters to remote addresses, supports a default or provided `SocketFactory`, can set ping intervals in `Configuration`, stops related threads, performs single calls with optional `UserGroupInformation`, and performs parallel calls to multiple addresses. `RemoteException` preserves a remote exception class name/message, unwraps to matching local exception types, serializes to XML, and reconstructs from XML attributes.

`RPC` builds higher-level Java proxies over `VersionedProtocol`. It can wait for a proxy, create proxies with client/server protocol versions, socket factories, and user tickets, stop proxies, make multiple parallel reflective calls, and create server instances. `RPC.Server` extends the generic IPC `Server` for a protocol implementation object and invokes protocol methods from `Writable` call payloads. `RPC.VersionMismatch` reports interface name, client version, and server version.

`Server` is the abstract IPC service. It listens on a bind address and port, handles a configured `Writable` parameter class with a handler thread count, exposes a thread-local current server and remote client IP/address while serving calls, binds sockets with better exceptions, tunes response socket send buffers, starts/stops/joins the service, reports listener address, defines abstract `call(Writable, long)`, and reports open connection and call queue counts. Public fields include the Hadoop RPC connection header, current wire version byte, log, and protected `RpcMetrics`.

`VersionedProtocol` is the marker contract for RPC protocols and requires `getProtocolVersion(String protocol, long clientVersion)`. The Javadoc states subclasses should also expose a static final `versionID` field.

`org.apache.hadoop.ipc.metrics` covers RPC observability. `RpcMetrics` implements `Updater`, publishes queue and processing time metrics through Hadoop metrics contexts, exposes public `MetricsTimeVaryingRate` fields plus a `metricsList` map, registers JMX, and can shut down. `RpcMgtMBean` is the JMX interface for sampled RPC operation counts, average processing/queue times, min/max times since reset, reset, open connection count, and call queue length.

`org.apache.hadoop.log.LogLevel` changes log levels at runtime. It has a command-line `main`, a public `USAGES` constant, and nested `LogLevel.Servlet` with `doGet(HttpServletRequest, HttpServletResponse)` for HTTP-based log-level inspection or mutation.

The range ends in `org.apache.hadoop.mapred.ClusterStatus`. The visible part shows it implements `Writable` and exposes getters for task tracker count, currently running map tasks, and currently running reduce tasks. Additional fields and methods for the full cluster status are outside this chunk.

## Control Flow and Behavioral Contracts

Sequence-file writer flow is append-oriented. Construction chooses the destination filesystem/path, key and value classes, optional progress reporting, replication/block sizing, and metadata. Callers append object or raw byte key/value records, optionally create sync points, and close the writer. `getLength()` documents that returned offsets are synchronized reader seek targets but may point to an earlier key than the most recently written key when block compression is involved.

Sequence-file sort/merge flow uses `SegmentDescriptor` instances as comparable merge inputs. A descriptor reads the next raw key, then the matching raw value, exposes the raw key buffer for ordering, performs sync checks, and cleans up after a segment is consumed. The preservation flag controls whether backing segment files are deleted during cleanup.

Set-file flow inherits sorted `MapFile` behavior. Writers require strictly increasing keys; readers seek to a key, iterate keys, or return a matching key/null. Because set values are implicit, the observable contract is keyed lookup and sorted traversal rather than key/value retrieval.

Writable flow is explicit binary serialization. Implementations write all fields to a `DataOutput` and read them back from a `DataInput` in the same order. `VersionedWritable` prepends or checks a version byte, and `VersionMismatchException` is the documented failure mode when serialized data uses an incompatible version.

Text/UTF8 flow distinguishes byte length from Java character count. `Text` stores UTF-8 bytes, supports byte-position character lookup, validates byte ranges before decoding, can replace malformed input depending on the decode overload, and uses raw comparators for byte-level sort keys. Callers that use `getBytes()` must respect `getLength()` because the backing array can be larger than the active content.

Comparator flow is optimized for sorting large serialized datasets. `WritableComparator.compare(byte[],...)` can compare raw serialized records without object allocation; subclasses such as `Text.Comparator` and `UTF8.Comparator` specialize this path. Object comparison remains available for generic callers. Registry methods let Hadoop components obtain or override comparators by key class.

`WritableUtils` flow covers several persisted wire formats. Compressed byte arrays and strings are length-delimited, variable-length integers use Hadoop's zero-compressed vint/vlong encoding, enum values are stored by string name, and `clone`/`cloneInto` use serialization as a copy mechanism. `skipFully` is a defensive read-loop helper for streams that may skip fewer bytes than requested.

Compression flow is a reusable state machine. A codec creates a stream directly or around a pooled compressor/decompressor. Callers set input on compressors/decompressors, loop while `needsInput`/`finished` determine progress, call `finish` for compressor EOF, and call `reset` before reuse or `end` to release resources. `CompressionOutputStream.finish()` finalizes compressed data without necessarily closing the underlying stream; `resetState()` prepares a stream for a new logical member.

Codec discovery flow maps file names to codecs by extension. `CompressionCodecFactory` reads configured codec classes, builds suffix mappings, selects a codec for a `Path`, and can strip a matched suffix. This is an integration point for input formats that auto-detect compressed inputs.

LZO/lzop flow is split between raw native LZO compression and lzop container framing. `LzoCodec` depends on native availability. `LzopCodec` wraps block streams with lzop header parsing/writing and checksum verification. Its decompressor initializes header flags, resets checksums, feeds data through `setInput`, and verifies decompressed and compressed checksums during `decompress`.

Retry flow is proxy/interceptor driven. A caller picks a default or per-method `RetryPolicy`, wraps an implementation with `RetryProxy`, and invokes interface methods normally. On exception, the proxy asks the policy whether to retry based on the exception and retry count; policy implementations may sleep before returning or throw to stop retries.

SerializationFactory flow selects a `Serialization` implementation by testing `accept(Class<?>)`, then opens serializers/deserializers over supplied streams. `DeserializerComparator` raw-comparison flow deserializes two byte-array records into objects and delegates to `Comparable`, which is simpler but more allocation-heavy than custom raw comparators.

IPC client flow creates or reuses client-side connection threads, sends a single `Writable` parameter to a server address, waits for a `Writable` result, can send parallel requests to multiple addresses, and must be stopped to release threads. Ping interval is stored in configuration and affects connection liveness.

RPC flow layers Java interfaces over the IPC client. A proxy is created for a `VersionedProtocol`, checks protocol version compatibility, marshals method calls into `Writable` invocation payloads, and returns Java objects. `waitForProxy` repeatedly attempts proxy acquisition until the requested protocol/server becomes available. On the server side, `RPC.Server` receives a `Writable`, invokes the implementation instance reflectively, and returns a `Writable` response or a `RemoteException`.

Generic `Server` lifecycle is explicit: construct with bind address, port, parameter class, handlers, and configuration; optionally tune socket send buffer; call `start()` before requests are handled; call `stop()` to reject new calls; call `join()` to wait for the service to stop. The abstract `call` method receives both the decoded parameter and receive timestamp, allowing subclasses to measure queue and processing time.

RPC metrics flow samples server state and operation timings. `RpcMetrics.doUpdates` pushes queue and processing rates into a metrics context. `RpcMgtMBean` exposes last-interval averages plus min/max values since reset; its docs note that metrics are collected regardless of the chosen metrics context, but averages require a context with periodic updates such as `NullContextWithUpdateThread`.

Log-level flow has two entry points. The command-line path runs through `LogLevel.main(String[])`; the servlet path handles `GET` requests and can read or change logging levels at runtime through HTTP.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API compatibility data. Runtime state described by the covered APIs includes sequence-file output streams, raw key/value buffers, segment paths and deletion policy, sorted map contents, mutable text byte arrays, two-dimensional writable arrays, version bytes, variable-length numeric values, writable comparator/factory/name registries, codec discovery maps, pooled compressor/decompressor instances, stream wrappers, native compression contexts, retry proxy counters, serializer stream state, IPC connection pools, RPC server listener/handler threads, current server/remote-address thread-local context, RPC metrics, JMX MBean state, servlet responses, and cluster status counters.

Persistent external formats are central here. `Writable` binary layouts, `Text` and deprecated `UTF8` encodings, vint/vlong encodings, compressed string/byte-array formats, `SequenceFile` records and sync markers, set-file `MapFile` layouts, bzip2/gzip/lzo/lzop/zlib stream formats, lzop header/checksum fields, XML representation of `RemoteException`, and RPC wire headers are all compatibility-sensitive.

Several APIs have external side effects. `SequenceFile.Writer` and `SetFile.Writer` create and append files in a Hadoop `FileSystem`; segment cleanup may close file handles and delete intermediate segment files. Compression streams write or read compressed data from caller-supplied streams and may retain native resources until `end`, `close`, or finalization. `CodecPool` can hold reusable native buffers beyond a single call. `RetryProxy` can repeat side-effecting method calls unless policies and wrapped methods are chosen carefully. IPC/RPC clients open sockets and background threads; servers bind ports, accept connections, and run handler threads. RPC metrics register with the metrics and JMX subsystems. `LogLevel.Servlet` writes HTTP responses and may mutate process logging configuration.

Threading is mixed. `SequenceFile.Writer.close`, `append`, `appendRaw`, and `getLength` are synchronized in this snapshot; many other IO and collection types are mutable without documented synchronization. `Server.start`, `stop`, `join`, and `getListenerAddress` are synchronized lifecycle operations. Compressor/decompressor instances are stateful and should be treated as single-thread owned while checked out of a pool.

## Dependencies and Integration Points

The IO APIs integrate with Hadoop's `FileSystem`, `Path`, `Configuration`, `Progressable`, `MapFile`, `SequenceFile`, `Writable`, `WritableComparable`, `WritableComparator`, `DataInput`, `DataOutput`, `DataOutputBuffer`, Java collections, and serializer APIs. `SequenceFile.Writer` depends directly on `org.apache.hadoop.io.serializer.Serializer` and `org.apache.hadoop.io.compress.CompressionCodec`.

Text and UTF-8 helpers depend on `java.nio.ByteBuffer`, `CharacterCodingException`, `MalformedInputException`, and Java charset behavior. They are heavily used by MapReduce keys, sequence files, RPC payloads, and configuration utilities.

Compression integrates with Java streams, `java.util.zip.Deflater`/`Inflater`, Hadoop configuration, codec discovery from configured class lists, native zlib and LZO libraries, bzip2 algorithm constants, block compressor/decompressor streams, checksum handling, and filename/path extension conventions.

Retry integrates with Java dynamic proxies, exception classification, `RemoteException` classification, `TimeUnit`, and service interfaces where retrying is semantically acceptable.

Serialization integrates with Hadoop `Writable`, Java `Serializable`, `Comparable`, raw comparators, and `Configured`/`Configuration`. It is a common extension point for sequence files, MapReduce shuffle/sort, and RPC payloads.

IPC/RPC integrates with `Writable` messages, `InetSocketAddress`, `SocketFactory`, `ServerSocket`, `UserGroupInformation`, Java reflection `Method`, Commons Logging, Hadoop metrics, JMX, XML/SAX attributes for remote exception persistence, and protocol interfaces implementing `VersionedProtocol`.

RPC metrics bridge the IPC server with the older Hadoop metrics subsystem (`MetricsContext`, `Updater`, `MetricsTimeVaryingRate`) and JMX management. Runtime log-level control integrates with servlet APIs and the process logging framework.

The visible `ClusterStatus` fragment connects classic `mapred` cluster state to `Writable` serialization, but most of the class surface is outside the chunk.

## Risks and Compatibility Notes

This chunk has partial boundaries. It starts after `SequenceFile.Sorter.RawKeyValueIterator` and after the containing `SequenceFile`/`org.apache.hadoop.io` declarations; it ends before `ClusterStatus` is complete. Final per-file reconciliation should combine adjacent chunks before making whole-class conclusions for those APIs.

This file is a public API compatibility artifact. Changes to class names, nesting, inheritance, implemented interfaces, constructor signatures, method parameters, return types, checked exceptions, field visibility/finality, synchronized flags, deprecation strings, or documented contracts can break old Hadoop clients even if implementation code still compiles internally.

Sequence-file and set-file APIs are storage-format sensitive. Changing sync marker behavior, `getLength()` seek guarantees, raw append semantics, serializer selection, key/value class reporting, segment cleanup/deletion policy, or strict key ordering in `SetFile.Writer` can corrupt data or make old readers unable to recover/split files.

Writable formats are wire and disk compatibility contracts. Reordering fields in implementations, changing vint/vlong encoding, altering compressed string formats, replacing `UTF8` behavior despite deprecation, or changing `WritableName` aliases can break persisted data, MapReduce shuffle keys, and RPC messages.

`Text` exposes its backing bytes, so callers can misuse array capacity as active length. UTF-8 validation and replacement behavior must remain precise; accepting malformed data silently or throwing on formerly accepted replacement paths can break data pipelines. `charAt` works on byte positions and returns Unicode scalar values, which is easy to confuse with Java `char` indexing.

Raw comparator behavior is performance and correctness critical. Comparator registry mistakes, inconsistent raw/object comparison, endian/sign errors in byte parsing helpers, or incorrect vint/vlong parsing can mis-sort map outputs and sequence-file indexes.

Compression APIs are resource-sensitive. Pooling a compressor after `end`, failing to `reset` before reuse, losing `finish()` data, mishandling native-library availability, ignoring dictionary requirements, or leaking native LZO/zlib state can cause data loss, hangs, memory leaks, or platform-specific failures. Lzop header and checksum verification is especially compatibility-sensitive because it determines whether existing `.lzo`/`.lzo_deflate` style files can be read.

Retry proxies can duplicate operations. They are safest for idempotent calls; applying retry policies to methods with non-idempotent side effects can produce duplicate writes, repeated submissions, or inconsistent remote state. Retry-by-exception maps also depend on correct `RemoteException` class-name unwrapping.

SerializationFactory order and accept logic are compatibility points. If both Java serialization and Writable serialization can accept a class, selection order affects wire format. Deserializing comparators allocate and depend on `Comparable`; they are safer functionally but can be too slow for sort-heavy paths.

IPC/RPC APIs are protocol-version, threading, and resource sensitive. Version mismatch handling must preserve interface/client/server version details. Client `stop()` must release threads and sockets. Server lifecycle must avoid accepting calls before `start` or after `stop`, and `getRemoteIp`/`getRemoteAddress` are only meaningful inside an RPC handler. Header or current-version changes are wire-incompatible.

RPC metrics and log-level control are operational surfaces. Metrics averages depend on periodic update contexts; using the null metrics context can hide sampled data unless configured as documented. Runtime log-level mutation through a servlet must validate inputs and avoid exposing sensitive logging controls without deployment-side protection.

## Test Signals

JDiff-level validation should confirm this XML range remains well formed across partial boundaries and preserves every covered package/class/interface boundary, nested class name, constructor and method signature, parameter type, checked exception, visibility/static/final/abstract/synchronized flag, field constant, deprecation note, and Javadoc contract.

Sequence-file tests should cover writer construction variants, key/value class reporting, compression codec reporting, append of `Writable` and object pairs, `appendRaw`, sync point creation, `getLength()` followed by reader seek, close idempotence/error paths, progress callbacks, metadata persistence, segment descriptor ordering/equality/hash, raw key/value iteration, sync checks, preserve-input behavior, and cleanup deletion vs preservation.

Set-file and sorted-map tests should cover writer strict ordering, deprecated and configured constructors, comparator-based construction, compression type propagation, reader seek/next/get semantics for existing and missing keys, sorted map copy construction, all `SortedMap` view methods, mutation methods, serialization round trips, and class-ID handling inherited from `AbstractMapWritable`.

Text/UTF8 tests should cover constructors from strings, bytes, and copies; backing-array length vs active length; byte-position `charAt`; substring `find` with and without start offset; setters and append ranges; clear; `readFields`/`write`; static read/write string helpers; decode/encode with replacement true/false; malformed UTF-8 validation failures; `bytesToCodePoint`; `utf8Length`; raw comparator ordering; and deprecated `UTF8` compatibility with old serialized data.

Writable primitive and utility tests should cover `VIntWritable`/`VLongWritable` set/get/read/write/compare/equality, `VersionedWritable` successful and mismatched version reads, `WritableComparator` registry definition and lookup, object vs raw comparisons, byte parsing helpers, `WritableFactories` custom factory lookup and configured construction, `WritableName` aliases and class resolution, compressed byte/string arrays, string arrays, clone/cloneInto, vint/vlong boundary values, enum read/write, `skipFully` short-skip behavior, and `toByteArray`.

Compression tests should cover codec factory discovery from configuration, suffix matching/removal, default/gzip/bzip2/lzo/lzop codec default extensions, stream close/finish/reset behavior, compressor/decompressor pool checkout and return, direct and pooled stream creation, byte counters, dictionary requirements, native and non-native zlib selection, built-in deflater/inflater adapters, native LZO unavailable behavior, lzop header parsing/writing, data and compressed checksum verification, bzip2 block-size selection, bzip2 read/write round trips, and resource cleanup after `end`/`close`/finalize paths.

Retry tests should cover try-once-fail, try-once-dont-fail, retry-forever with bounded test hooks, fixed-count and fixed-time policies, proportional and exponential sleeps with fake time or small intervals, exception-class policy maps, remote-exception class-name policy maps, per-method policy selection, retry count propagation, exception propagation when retry stops, and non-idempotent method documentation or guard tests in callers.

Serialization tests should cover `WritableSerialization` acceptance and round trips, `JavaSerialization` acceptance and round trips, factory selection order, serializer/deserializer open-close lifecycle, deserialize-into-reuse behavior, stream closure behavior, missing serializer/deserializer returns, `DeserializerComparator` and `JavaSerializationComparator` ordering, and malformed serialized input failures.

IPC/RPC tests should cover `Client` construction with default and custom socket factories, ping interval configuration, single calls with and without `UserGroupInformation`, parallel calls, timeout/interruption behavior, client stop releasing resources, `RemoteException` XML write/valueOf and typed unwrap behavior, proxy creation overloads, `waitForProxy`, version mismatch reporting, `stopProxy`, reflective parallel RPC calls, server construction, bind failure diagnostics, start/stop/join lifecycle, listener address reporting, remote IP/address visibility inside handlers, call queue and open connection metrics, and wire header/version compatibility.

RPC metrics and logging tests should cover `RpcMetrics` registration, queue/processing time increments and `doUpdates`, shutdown, public metrics-list visibility, JMX MBean getters for operation counts and averages/min/max, reset behavior, connection and call queue delegation to `Server`, metrics contexts with and without periodic update threads, `LogLevel.main` argument handling, servlet `doGet` read/change flows, servlet error handling, and HTTP response formatting.

`ClusterStatus` tests for this visible fragment should at least cover `Writable` serialization compatibility and getters for task tracker count, running map count, and running reduce count, with adjacent chunks needed for full class coverage.

### subset-b-007298: lines 18673-24869

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 18673-24869

## Chunk Scope

This chunk is a JDiff API snapshot for Hadoop 0.19.1. It starts inside `org.apache.hadoop.mapred.ClusterStatus`, then covers a large public `org.apache.hadoop.mapred` API section through `MultiFileSplit`. The visible surface includes counters, file input/output formats, splits, job submission/configuration/status/history APIs, the JobTracker service facade, text record readers, map execution contracts, and multi-file input splitting.

Because this is generated API XML rather than implementation source, control-flow, state, and persistence notes are inferred from exposed signatures, inheritance, synchronization flags, checked exceptions, deprecation markers, fields, and embedded Javadocs.

## Purpose

The chunk records the public compatibility surface of the old `mapred` MapReduce API. It shows how Hadoop 0.19.1 clients configure jobs, submit and monitor them, describe input/output formats, split files, read records, emit map output, collect counters, persist job status/profile/queue objects, and log/read job history.

This API surface is important for compatibility because it captures both user-facing extension points (`Mapper`, `MapRunnable`, `InputFormat`, `FileInputFormat`, `FileOutputFormat`, `OutputCommitter`) and cluster/internal-facing integration points (`JobClient`, `JobTracker`, `JobHistory`, `JobStatus`, `JobID`, `Counters`). The XML also exposes older/deprecated overloads that migration tooling must preserve or intentionally replace.

## Important APIs and Types

### Cluster and Counter State

The chunk begins in the tail of `ClusterStatus`, showing capacity and health accessors such as `getMaxMapTasks()`, `getMaxReduceTasks()`, `getJobTrackerState()`, plus `Writable` serialization through `write(DataOutput)` and `readFields(DataInput)`. The class documents cluster size, map/reduce capacity, running task counts, and JobTracker state as values returned by `JobClient#getClusterStatus()`.

`Counters` implements `Writable` and `Iterable<Counters.Group>`. It provides synchronized APIs to retrieve group names, iterate groups, find counters by enum or `(group, name)`, increment counters, sum counters, compute total size, serialize/deserialize all groups, log values, and convert to compact or escaped compact strings. `fromEscapedCompactString(String)` can reconstruct a `Counters` object and throws `ParseException` on malformed text.

`Counters.Counter` is a synchronized `Writable` record with internal name, display name, current long value, binary read/write, compact escaped string rendering, display-name mutation, and `increment(long)`.

`Counters.Group` is a `Writable` and `Iterable<Counters.Counter>` grouping counters by enum class or group name. It exposes raw and display names, display-name mutation, compact escaped rendering, `getCounter(String)` returning zero for missing counters, deprecated numeric-id lookup, create-on-demand `getCounterForName(String)`, size, serialization, and iteration.

### File-Based Input and Splits

`FileInputFormat<K,V>` is the base class for file-backed `InputFormat`. It implements `InputFormat<K,V>` and exposes split sizing and path discovery behavior:

- `setMinSplitSize(long)`, `isSplitable(FileSystem, Path)`, `listStatus(JobConf)`, `getSplits(JobConf, int)`, `computeSplitSize(long, long, long)`, and `getBlockIndex(BlockLocation[], long)` define file listing and split planning.
- `setInputPathFilter(JobConf, Class<? extends PathFilter>)` and `getInputPathFilter(JobConf)` integrate path filters.
- Static path helpers set, add, and retrieve comma-separated or array-based input paths from `JobConf`.
- `getRecordReader(InputSplit, JobConf, Reporter)` remains abstract for concrete formats.

`InputFormat<K,V>` declares the central MapReduce input contract: `getSplits(JobConf, int)` computes logical work units, and `getRecordReader(InputSplit, JobConf, Reporter)` creates a reader for each split.

`InputSplit` extends `Writable` and exposes `getLength()` and `getLocations()`, carrying scheduler-relevant byte size and data-locality hostnames.

`FileSplit` implements `InputSplit` for a byte range of a single file. Constructors accept path, start, length, and either `JobConf` or explicit host locations. Accessors expose path, start, length, host locations, `toString()`, and Writable serialization.

`MultiFileInputFormat<K,V>` extends `FileInputFormat` and returns `MultiFileSplit` instances. It groups whole files into nearly equal content-length splits; subclasses provide a record reader for each multi-file split.

`MultiFileSplit` implements `InputSplit` for a set of whole files rather than a byte range. Its constructor takes `JobConf`, `Path[]`, and `long[]` lengths. It exposes total length, per-file lengths, number of paths, individual/all paths, locations, serialization, and string conversion. The chunk ends before the next `OutputCollector` interface begins, so the complete end of `MultiFileSplit` is visible but following output APIs are outside this item.

### Output Paths and Commit

`FileOutputFormat<K,V>` implements `OutputFormat<K,V>` and is the base for file-backed job output. It provides output compression toggles and codec configuration, abstract `getRecordWriter(...)`, output-spec validation, output path get/set helpers, task work path creation, task output path helpers, unique task filename generation, and custom file path generation.

`FileOutputCommitter` defines the standard file-output commit lifecycle with `setupJob`, `cleanupJob`, `setupTask`, `commitTask`, `abortTask`, and `needsTaskCommit`. Its visible fields include `TEMP_DIR_NAME` and `LOG`. The class documentation ties it to files written under `FileOutputFormat#getTaskOutputPath(...)`, which are promoted during commit and cleaned on abort.

`MapFileOutputFormat` extends `FileOutputFormat<WritableComparable, Writable>`. It writes `MapFile`s, exposes a `RecordWriter`, opens generated outputs via static `getReaders(FileSystem, Path, Configuration)`, and retrieves a key through static `getEntry(MapFile.Reader[], Partitioner<K,V>, K, V)`.

### Exceptions and Identifiers

`FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` are public failure types used by input/output validation and job configuration. `InvalidInputException` wraps multiple `IOException` problems, exposes `getProblems()`, and formats a summary message.

`ID` is the base `WritableComparable<ID>` for numeric identifiers. It stores protected `int id`, supports default/int constructors, `getId()`, string conversion, equality/hash, numeric ordering, read/write, static `read(DataInput)`, and `forName(String)`.

`JobID` extends the ID family for immutable job identifiers. It combines a JobTracker identifier with a job number, compares first by tracker identifier then job number, serializes/deserializes itself, parses string forms through `forName(String)`, and exposes `getJobIDsPattern(...)` for matching job IDs.

### Job Client and Configuration

`JobClient` implements `MRConstants` and `Tool`. It is the primary user-job interface to the MapReduce system. Constructors support default construction, construction from `JobConf`, and direct connection to a JobTracker `InetSocketAddress`. Important APIs include:

- Lifecycle and setup: `getCommandLineConfig()`, `init(JobConf)`, `close()`, and `getFs()`.
- Submission: `submitJob(JobConf)`, `submitJob(String)`, `isJobDirValid(Path, FileSystem)`, and static `runJob(JobConf)`.
- Monitoring: `getJob(JobID)`, deprecated `getJob(String)`, map/reduce/setup/cleanup task reports, cluster status, jobs to complete, all jobs, default map/reduce capacity, system directory, queues, queue info, and jobs from a queue.
- CLI support: `run(String[])`, `main(String[])`, and `TaskStatusFilter` getter/setter helpers backed by `JobConf`.

`JobClient.TaskStatusFilter` is an enum-like nested type exposed through `values()` and `valueOf(String)`, used to select which task outputs are printed.

`JobConf` is the central mutable job configuration and extends the Hadoop configuration stack. This slice exposes constructors from class, configuration, configuration plus example class, file path/string path, and a boolean controlling default resource loading. It has a broad set of typed getters/setters:

- Job packaging and local state: jar path, jar-by-class lookup, local dirs, local file deletion, local path allocation, user, working directory, job local scratch dir, and session ID.
- Input/output components: input format, output format, output committer, output key/value classes, map output key/value classes, comparators, grouping comparator, key-field comparator and partitioner options.
- Execution components: mapper, map runner, partitioner, reducer, combiner, map/reduce counts, max task attempts, max failures per tracker, tolerated map/reduce failure percentages, JVM task reuse count, speculative execution globally and per task type.
- Compression: map-output compression toggle and codec.
- Metadata and operations: job name, priority, queue name, profile enablement/parameters/ranges, debug scripts, and job-end notification URI.

The class field `DEFAULT_QUEUE_NAME` records the fallback queue. Many `JobConf` APIs are public compatibility hooks around string configuration keys, so behavior depends on stable key names and defaults even when method bodies are absent from the XML.

`JobConfigurable` is a small extension point with `configure(JobConf)`. `MapReduceBase`, `Mapper`, `MapRunnable`, and many input formats use it for job-scoped initialization.

`JobContext` exposes `getJobConf()` and `getProgressible()`, pairing job configuration with a progress callback.

### Job History

`DefaultJobHistoryParser` parses a job history log file into a `JobHistory.JobInfo` object, with `parseJobTasks(String, JobInfo, FileSystem)` as the visible parser entry point.

`JobHistory` provides static-style history logging and parsing support. It exposes initialization, parsing from `FileSystem` into a `JobHistory.Listener`, history disable toggles, and task log URL lookup. Fields include `LOG` and `JOB_NAME_TRIM_LENGTH`.

`JobHistory.HistoryCleaner` implements `Runnable` and deletes history files older than one month while updating the master index, according to its class docs.

`JobHistory.JobInfo` records job-level history and has helpers for all tasks, local job file path, URL encoding/decoding of history file paths/names, user extraction from job configuration, history log locations, user history locations, recovery of history file names, and event logging. Logging methods cover submitted, initialized, started, finished, failed, killed, priority, and job submit/launch info events.

`JobHistory.Task`, `TaskAttempt`, `MapAttempt`, and `ReduceAttempt` model task and attempt history records. They provide logging APIs for start, finish, failure, and killed events, with map/reduce attempt overloads that capture host, tracker, error, and phase timing details. `Task#getTaskAttempts()` exposes attempts keyed by task-attempt ID.

`JobHistory.Keys`, `RecordTypes`, and `Values` are enum-like nested types for history log key names, line record types, and common values. `JobHistory.Listener#handle(RecordTypes, Map<Keys,String>)` is the callback contract for parsers.

### Job Metadata, Queues, and Status

`JobProfile` implements `Writable` and tracks user, job ID, job file, web UI URL, job name, and queue name. It keeps deprecated string job-id constructors and `getJobId()` alongside the typed `JobID` path.

`JobQueueInfo` implements `Writable` and carries queue name plus scheduling info, with default and `(queueName, schedulingInfo)` constructors and read/write support.

`JobStatus` implements `Writable` and `Cloneable`. It exposes constants `RUNNING`, `SUCCEEDED`, `FAILED`, `PREP`, and `KILLED`; constructors for job ID, map/reduce/setup/cleanup progress, run state, and priority; progress accessors; run-state mutation; start time; username; scheduling info; priority; clone; and binary serialization.

`JobPriority` is an enum-like priority type exposed through `values()` and `valueOf(String)`.

`JobShell` implements `Tool` and wraps command-line parsing for job submission through constructors, `init(JobConf)`, `run(String[])`, and `main(String[])`.

### JobTracker Service Surface

`JobTracker` implements `MRConstants`, `InterTrackerProtocol`, `JobSubmissionProtocol`, and `TaskTrackerManager`. Its public/static surface represents both daemon lifecycle and RPC service behavior:

- Lifecycle and identity: `startTracker(JobConf)`, `stopTracker()`, `offerService()`, `main(String[])`, protocol version, restart/recovery flags, recovery duration, instrumentation class get/set, address, machine, tracker identifier, tracker/info ports, start time, build version, filesystem name, and local job file path.
- Cluster and topology: running/failed/completed jobs, task trackers, tracker lookup, network topology node resolution and lookup, cache-level counts, unique host counts, resolved tracker counts, and queue manager access.
- Scheduling integration: add/remove `JobInProgressListener`, `heartbeat(TaskTrackerStatus, boolean, boolean, short)` returning `HeartbeatResponse`, next heartbeat interval calculation, and task-tracker error reporting.
- Submission and job control: new job IDs, job submission, cluster status, kill job, set priority, job profile/status/counters, task reports, completion events, diagnostics, task lookup, task killing, assigned tracker lookup, jobs-to-complete, all jobs, system dir, queue list/info/jobs.

`JobTracker.IllegalStateException` reports attempts to submit a job before the tracker is ready. `JobTracker.State` is an enum-like type exposed through `values()` and `valueOf(String)`.

### Text Record Readers and Map Execution

`KeyValueLineRecordReader` implements `RecordReader<Text,Text>`. It reads one line as a key/value pair separated by a configured separator, exposes key/value class creation, a `findSeparator(...)` helper, `next(Text, Text)`, progress, position, and close.

`KeyValueTextInputFormat` is a plain-text file input format that breaks files into lines and uses the separator to split key from value. It implements `JobConfigurable`, exposes `configure(JobConf)`, splitability, and a `RecordReader<Text,Text>`.

`LineRecordReader` implements `RecordReader<LongWritable,Text>` and treats each line as a record with the byte offset as key and line text as value. Constructors support `Configuration` plus `FileSplit`, and lower-level `InputStream`/start/end variants. It exposes key/value creation, `next(LongWritable, Text)`, progress, synchronized position, and synchronized close. `LineRecordReader.LineReader` is deprecated in favor of `org.apache.hadoop.util.LineReader`.

`Mapper<K1,V1,K2,V2>` extends `JobConfigurable` and Hadoop `Closeable`. Its `map(K1, V1, OutputCollector<K2,V2>, Reporter)` method emits zero or more intermediate key/value pairs and can report progress, status, and counters. The docs describe the standard old-API map flow: one map task per input split, optional initialization through `configure`, per-record `map` calls, intermediate `SequenceFile` storage, partitioning by `Partitioner`, optional combiner, comparator-configured grouping, and direct output when reducer count is zero.

`MapReduceBase` provides no-op `close()` and `configure(JobConf)` defaults for Mapper and Reducer implementations.

`MapRunnable<K1,V1,K2,V2>` extends `JobConfigurable` and lets advanced users control map execution by implementing `run(RecordReader<K1,V1>, OutputCollector<K2,V2>, Reporter)`. This is the hook for asynchronous or multithreaded mapper behavior.

`MapRunner` is the default `MapRunnable` implementation. It configures a mapper, runs the record-reader loop, writes output through the collector, and exposes protected `getMapper()` for subclasses.

## Control Flow and Behavioral Contracts

MapReduce input planning flows from `JobConf` input path configuration into `FileInputFormat.listStatus`, path filtering, block-location lookup, and split creation. Concrete input formats then receive each `InputSplit` and return a `RecordReader` that produces key/value objects for a mapper.

File split scheduling depends on `InputSplit.getLength()` and `getLocations()`. `FileSplit` models byte ranges with locality hints, while `MultiFileSplit` intentionally changes the unit of work to whole files grouped by total length.

Map execution flows through `MapRunner.run`: a `RecordReader` supplies records, the configured `Mapper.map` transforms them, `OutputCollector.collect` receives intermediate pairs, and `Reporter` carries liveness, status, and counter updates. Custom `MapRunnable` implementations can replace that loop.

Job submission flows through `JobClient` into a JobTracker: validate/stage job directory, request or use a `JobID`, submit job configuration, and obtain a `RunningJob`/status object for monitoring. `runJob(JobConf)` adds a polling loop until completion.

Cluster management and task scheduling flow through JobTracker RPC and heartbeat methods. TaskTrackers send heartbeats with status; JobTracker returns `HeartbeatResponse` instructions, tracks topology and cache levels for locality, maintains job lists, and exposes job/task control operations to clients.

Output flow uses `FileOutputFormat` to validate and assign output paths, `RecordWriter` to write task output, and `FileOutputCommitter` to move task-temporary outputs into final output during commit or remove them during abort.

History flow uses `JobHistory.JobInfo`, `Task`, and `TaskAttempt` logging methods to append key/value event records for submitted/started/finished/failed/killed jobs and attempts. Parsing reverses the flow through `DefaultJobHistoryParser` or `JobHistory.parseHistoryFromFS`, invoking a listener or populating object-model records.

Writable flow is consistent across counters, splits, IDs, profiles, queue info, status, and counter groups: `write(DataOutput)` persists fields in a Hadoop binary protocol and `readFields(DataInput)` reconstructs mutable objects.

## State and Persistence Behavior

The JDiff XML itself persists the 0.19.1 public API, but the exposed APIs describe several runtime state stores.

`Counters`, `Counters.Group`, and `Counters.Counter` are mutable in-memory job/task metrics with synchronized mutation and read paths. They persist through `Writable` binary serialization and through compact escaped text strings suitable for logs or UI transfer.

`JobConf` is mutable configuration state. Its typed methods persist job settings into configuration keys for input/output classes, jar location, paths, compression, comparators, mapper/reducer classes, task counts, retries, speculation, profiling, debugging, notifications, priority, queue, user, and working directories.

`FileSplit`, `MultiFileSplit`, `JobID`, `JobProfile`, `JobQueueInfo`, and `JobStatus` are wire/storage records. Their `Writable` methods are compatibility-sensitive because JobTracker, JobClient, task launch, and history tools exchange them across process boundaries.

`FileOutputCommitter` persists task outputs indirectly by manipulating filesystem paths under the configured temporary directory and final output directory. Commit and abort behavior determines whether speculative or failed task attempts leave visible data.

`JobHistory` persists append-only job, task, and attempt event records on a filesystem, has recovery helpers for partially generated history files, exposes per-user history log locations, and includes a cleaner runnable that removes old history data.

`JobTracker` owns central daemon state: submitted/running/failed/completed jobs, task tracker statuses, topology mappings, listener registrations, queue manager state, recovery/restart flags, tracker identity, heartbeat scheduling state, and counters/status/profile/task reports exposed over protocols.

Record readers keep per-split cursor state: current file position, split start/end, current line, configured key/value separator, and progress. `LineRecordReader` exposes synchronized `getPos()` and `close()`, implying concurrent status/cleanup access may occur.

## Dependencies and Integration Points

This chunk depends on Hadoop core IO and filesystem types: `Writable`, `WritableComparable`, `Text`, `LongWritable`, `MapFile`, `SequenceFile`, `RawComparator`, compression codecs, `Path`, `FileSystem`, `FileStatus`, `BlockLocation`, and `PathFilter`.

MapReduce integration types visible in signatures include `JobConf`, `Reporter`, `RecordReader`, `RecordWriter`, `OutputCollector`, `RunningJob`, `TaskReport`, `TaskCompletionEvent`, `JobInProgress`, `TaskInProgress`, `TaskTrackerStatus`, `HeartbeatResponse`, `QueueManager`, `Partitioner`, `Reducer`, and protocol interfaces such as `JobSubmissionProtocol` and `InterTrackerProtocol`.

Java dependencies include `DataInput`, `DataOutput`, `IOException`, `InetSocketAddress`, collections, regex/pattern strings for task-file retention and ID matching, and URL handling in `JobProfile`.

Apache Commons Logging appears through public `LOG` fields in classes such as `FileInputFormat`, `FileOutputCommitter`, and `JobHistory`.

Operational integration points include filesystem-backed job staging/output/history directories, JobTracker RPC, TaskTracker heartbeat protocols, network topology resolution for locality, queue scheduling, history parsing/listener callbacks, and CLI `Tool` entry points in `JobClient` and `JobShell`.

## Risks and Edge Cases

This is generated API metadata, so it does not reveal exact implementation details such as lock ordering, retry logic, filesystem rename semantics, parser escaping code, or validation branches.

The chunk starts mid-`ClusterStatus` and ends before `OutputCollector`; adjacent chunks are needed for a complete per-file report around those boundary classes/interfaces.

Counter serialization and escaped compact strings are compatibility-sensitive. Malformed strings raise `ParseException`, and callers relying on display names must preserve group/counter name escaping.

Several APIs retain deprecated string or numeric-ID forms, including counter lookup by ID, `JobClient` string job IDs, and `JobProfile#getJobId()`. Compatibility code must handle both old and typed `JobID` paths.

`FileInputFormat` path handling has many edge cases: comma-separated path parsing, filters, missing/invalid inputs, splitability for compressed files, block-index selection, and min/max split sizing.

`FileOutputCommitter` behavior is high risk under failure or speculative execution because duplicate task attempts may write temporary data and only one should become committed output.

`JobConf` exposes many loosely typed class and configuration settings. Missing mandatory attributes surface as `InvalidJobConfException`, but class mismatches or default fallback behavior require implementation review.

`JobTracker` is a central mutable service with many public methods. Heartbeat interval calculations, recovery state, topology resolution, queue manager behavior, and task killing can affect cluster correctness and availability.

Job history recovery and cleanup can lose diagnostic data if recovery chooses the wrong file, URL encoding/decoding changes, or the history cleaner removes files still needed by tools.

Text record readers must handle split boundaries, separators, long lines, compressed splitability, byte offsets, and final lines without terminators. Incorrect position/progress reporting can cause duplicate or skipped records.

`MultiFileSplit` changes the split unit from byte ranges to whole files, so it can produce poor load balance when individual files are large even if total split lengths are nearly equal.

## Test Signals

Useful tests inferred from this API slice include:

- `Counters` round trips through `Writable`, compact string, and escaped compact string forms, including display names, missing counters, enum counters, deprecated numeric lookup, group iteration, and concurrent-style synchronized access.
- `FileInputFormat` tests for input path set/add/get, comma-separated paths, path filters, invalid input aggregation, split sizing, block index selection, unsplittable files, and `FileSplit` location serialization.
- `MultiFileInputFormat` and `MultiFileSplit` tests for whole-file grouping, total/per-file length reporting, path serialization, location reporting, and string output.
- `FileOutputFormat` tests for output path validation, compression codec settings, task output/work paths, unique names, custom file paths, and output directory already-exists failures.
- `FileOutputCommitter` tests for setup, commit, abort, cleanup, `needsTaskCommit`, failed attempts, and speculative duplicate attempts.
- `JobConf` tests for every major typed getter/setter pair: classes, compression, comparators, task counts, retries, speculation, profiling, debug scripts, notification URI, priority, queue, local dirs, working directory, and jar-by-class.
- `JobClient` integration tests for job submission, invalid job directory detection, job lookup by typed and deprecated IDs, task reports, cluster status, queues, task output filters, and CLI `run`.
- `JobHistory` tests for submitted/started/finished/failed/killed event logging, map/reduce attempt events, parser listener callbacks, object-model population, filename/path encoding, recovery file selection, disable-history behavior, and cleaner expiry.
- `JobStatus`, `JobProfile`, `JobQueueInfo`, `ID`, and `JobID` `Writable` compatibility tests, including equality, ordering, hash codes, string parsing, and deprecated accessor behavior.
- `JobTracker` service tests around heartbeat responses, new job IDs, submission readiness, kill job/task, priority changes, task diagnostics, queue information, cluster status, recovery flags, and topology-aware tracker/node lookups.
- `LineRecordReader` and `KeyValueLineRecordReader` tests for split-boundary correctness, separator discovery, missing separators, offset keys, progress/position, close idempotence, and long-line handling.
- `Mapper`, `MapRunner`, and `MapRunnable` tests that verify configure/map/close order, reporter progress and counters, zero-reducer direct output behavior, custom map runners, and exception propagation.

## Chunk Boundary Notes

The preceding chunk is needed for the beginning of `ClusterStatus` and earlier `org.apache.hadoop.mapred` APIs. The following chunk is needed for `OutputCollector`, `OutputCommitter`, output formats beyond this range, reducers, reporters, records, task IDs/statuses, and the rest of the old `mapred` package. The final merged report should preserve that this chunk is a middle slice of the package rather than a complete package summary.

### subset-b-007299: lines 24870-30908

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml - subset-b-007299

Chunk lines: 24870-30908.

## Purpose

This chunk is part of the Hadoop 0.19.1 JDiff XML API snapshot. It is generated API metadata, not executable Java implementation. The file records public/protected class and interface signatures, inheritance, implemented interfaces, constructors, methods, fields, checked exceptions, deprecation text, and embedded Javadoc. The useful research signal is therefore the API contract exposed by Hadoop 0.19.1 and the behavior documented by those contracts.

The slice starts at the tail of `org.apache.hadoop.mapred.MultiFileSplit`, then covers old `org.apache.hadoop.mapred` output, record, reducer, reporter, running-job, sequence-file, skip-bad-record, task, task-log, task-tracker, text input/output, and job-control APIs. It then covers most of `org.apache.hadoop.mapred.join`, and finishes in `org.apache.hadoop.mapred.lib.InputSampler` after the opening of `writePartitionFile`. Because the chunk ends mid-class, `InputSampler` is incomplete and must be reconciled with the following chunk before making whole-file claims.

## Important APIs, Types, and Contracts

### Old mapred dataflow contracts

- `OutputCollector<K,V>` is the callback used by `Mapper` and `Reducer` implementations to emit key/value pairs via `collect(K,V)`.
- `OutputCommitter` is the abstract output lifecycle hook for a MapReduce job. It exposes `setupJob`, `cleanupJob`, `setupTask`, `needsTaskCommit`, `commitTask`, and `abortTask`, all keyed by `JobContext` or `TaskAttemptContext`. Its contract is responsible for temporary output setup, commit promotion, and abort cleanup.
- `OutputFormat<K,V>` validates output specs and constructs `RecordWriter<K,V>` instances. `checkOutputSpecs(FileSystem, JobConf)` is expected to reject unsafe output, commonly pre-existing destinations, while `getRecordWriter` returns the writer for a task output part.
- `OutputLogFilter` implements `PathFilter` and rejects `_logs` paths when listing output directories.
- `Partitioner<K2,V2>` extends `JobConfigurable`; `getPartition(key,value,numPartitions)` maps intermediate map-output keys to reducer partitions.
- `RecordReader<K,V>` presents records from an `InputSplit` through `next`, factory methods for reusable key/value objects, position, close, and progress. The Javadoc documents the key MapReduce boundary: converting byte-oriented splits into record-oriented task inputs.
- `RecordWriter<K,V>` writes output records and closes with a `Reporter`.
- `Reducer<K2,V2,K3,V3>` extends `JobConfigurable` and Hadoop `Closeable`. Its `reduce` contract receives a grouped key and iterator of values, writes through `OutputCollector`, and uses `Reporter` for liveness/progress. The Javadoc explicitly describes the shuffle, sort, and reduce phases and warns that the framework reuses key/value objects.
- `Reporter` is the task-side reporting API. It sets status text, gets/increments enum or string counters, exposes the current `InputSplit`, and provides `Reporter.NULL` for no-op progress reporting.
- `RunningJob` is the user-facing handle returned by `JobClient`. It exposes `JobID`, deprecated string job IDs, job name/file/tracking URL, setup/map/reduce/cleanup progress, completion/success checks, blocking wait, job state, kill, priority updates, task-completion events, task kill/fail, and counters.

### SequenceFile input and output formats

- `SequenceFileAsBinaryInputFormat` returns a `RecordReader<BytesWritable,BytesWritable>` over raw serialized sequence-file keys and values. Its nested `SequenceFileAsBinaryRecordReader` exposes key/value class names, synchronized `next(BytesWritable,BytesWritable)`, position, close, and split progress.
- `SequenceFileAsBinaryOutputFormat` writes raw binary keys/values into SequenceFiles. It allows the configured output key/value class to differ from the in-memory `BytesWritable` writer type via `setSequenceFileOutputKeyClass`, `setSequenceFileOutputValueClass`, and corresponding getters. Its protected nested `WritableValueBytes` adapts `BytesWritable` to `SequenceFile.ValueBytes` for `appendRaw`.
- `SequenceFileAsTextInputFormat` and `SequenceFileAsTextRecordReader` convert sequence-file keys and values to `Text` by calling `toString()` on the original key/value objects. The record reader has synchronized `next`, `getPos`, and `close`.
- `SequenceFileInputFilter<K,V>` extends `SequenceFileInputFormat<K,V>` and installs a configurable key filter class. The nested `Filter` interface is `Configurable` and decides acceptance from a key. Built-in filters include `MD5Filter` (`MD5(key) % frequency == 0`), `PercentFilter` (record number modulo frequency), and `RegexFilter` (key string matches a configured regex). `FilterBase` holds configuration access.
- `SequenceFileInputFormat<K,V>` extends `FileInputFormat` for sequence files, with protected `listStatus` and `getRecordReader`.
- `SequenceFileOutputFormat<K,V>` extends `FileOutputFormat`, builds `RecordWriter` instances, opens generated output readers from a directory, and controls sequence-file compression type with `getOutputCompressionType` and `setOutputCompressionType`.
- `SequenceFileRecordReader<K,V>` is the standard synchronized sequence-file reader for file splits. It exposes runtime key/value classes, `createKey`, `createValue`, public and protected `next`, protected current-value and seek hooks, `getProgress`, `getPos`, `close`, and a protected `Configuration conf` field.

### Bad-record skipping and task metadata

- `SkipBadRecords` is a configuration utility for Hadoop's skip mode. It controls attempts before skipping starts, auto-increment behavior for mapper/reducer processed-record counters, skip output path, max skipped map records per bad record, and max skipped reduce groups per bad group.
- `SkipBadRecords` publishes counter names in `COUNTER_GROUP`, `COUNTER_MAP_PROCESSED_RECORDS`, and `COUNTER_REDUCE_PROCESSED_GROUPS`. The Javadoc says applications must increment these counters for bad-record detection, with framework auto-increment defaults that streaming/asynchronous apps may need to disable.
- `StatusHttpServer` extends `HttpServer`, with nested `TaskGraphServlet` rendering SVG task-status graphics through `doGet` and static graph dimension/margin fields.
- `TaskAttemptContext` extends `JobContext` and exposes `getTaskAttemptID` and `getJobConf`.
- `TaskAttemptID` and `TaskID` are immutable, comparable, writable identifiers. They construct from component parts, expose parent IDs and map/reduce role, implement equality, hash, comparison, string conversion, `readFields`/`write`, static `read`, static `forName`, and static regex pattern builders. The docs warn applications not to parse strings manually.
- `TaskCompletionEvent` is a writable job-tracker event describing task-attempt completion. It carries event ID, `TaskAttemptID`, status enum, task-tracker HTTP location, run time, map/reduce role helpers, writable serialization, equality, and `EMPTY_ARRAY`. Deprecated string task-id methods are retained beside typed `TaskAttemptID` methods.
- `TaskReport` is a writable task-state snapshot exposing typed `TaskID`, deprecated string ID, progress, state text, diagnostics, counters, start and finish times, equality/hash, and read/write methods.

### Task logging, servlets, and TaskTracker

- `TaskLog` is the task-specific user-log helper built around the `hadoop.log.dir` system property. It locates real/logical task log files and index files, synchronizes logs, purges old logs, reads configured max log length, quotes shell commands, wraps commands to capture stdout/stderr with optional setup and PID file, and captures debug output.
- `TaskLog.LogName` is an enum-like JDiff entry with `values`, `valueOf`, and `toString` for user-log streams.
- `TaskLogAppender` extends log4j `FileAppender` for child task system logs. It has activation, append, flush, synchronized close, task-id getter/setter, and total log size getter/setter.
- `TaskLogServlet` serves task logs over HTTP and provides static URL construction from tracker host, port, and task attempt ID.
- `TaskTracker` is the old worker daemon API. Public methods include instrumentation class selection, storage cleanup, shutdown/close, job client and report address access, JVM manager access, the server retry `run` loop, task fetch by child JVM, synchronized task status/diagnostic/range/progress/commit/done/shuffle/fs-error callbacks, map completion event fetch, map-output-lost reporting, idle checks, `main`, and task-memory-manager accessors. Its nested `MapOutputServlet` serves map outputs to reducers through Jetty.

### Text input/output formats

- `TextInputFormat` extends `FileInputFormat<LongWritable,Text>` and implements `JobConfigurable`. It configures from `JobConf`, determines splitability by filesystem/path, and creates line-oriented record readers. Keys are byte positions and values are line text.
- `TextOutputFormat<K,V>` extends `FileOutputFormat` and writes plain text output. Its protected static `LineRecordWriter<K,V>` writes synchronized records to a protected `DataOutputStream out`, using either a provided separator or default behavior, and closes with a `Reporter`.

### Job-control DAG APIs

- `org.apache.hadoop.mapred.jobcontrol.Job` encapsulates a `JobConf`, dependency jobs, a `JobClient`, a control ID, an assigned Hadoop `JobID`, message text, and state constants: `SUCCESS`, `WAITING`, `RUNNING`, `READY`, `FAILED`, and `DEPENDENT_FAILED`. It has synchronized state transitions and can add dependencies only while waiting. Its protected `submit` moves a ready job to running or failed depending on submission success.
- `JobControl` implements `Runnable` for a group of dependent jobs. It provides state-bucket accessors for waiting/running/ready/successful/failed jobs, synchronized `addJob`, bulk `addJobs`, thread state, stop/suspend/resume, synchronized `allFinished`, and a main loop that checks running jobs, updates waiting jobs, and submits ready jobs.

### Join framework

- `ArrayListBackedIterator<X>` and `StreamBackedIterator<X>` implement `ResetableIterator<X>`. The array-list implementation stores values in memory and is documented as less preferred than stream-backed storage. `ResetableIterator.EMPTY` is a no-op implementation.
- `ResetableIterator<T>` is not a Java `Iterator`; it is a stateful replay interface for join values with `hasNext`, `next`, `replay`, `reset`, `add`, `close`, and `clear`. It requires FIFO replay after reset and warns that `next` may fail for nested joins even when `hasNext` is true.
- `ComposableInputFormat<K,V>` refines `InputFormat` to require a `ComposableRecordReader`. `ComposableRecordReader<K,V>` extends `RecordReader` and `Comparable`, adding child ID, key access/cloning, `hasNext`, `skip`, and `accept` into a join collector.
- `CompositeInputFormat<K>` parses `mapred.join.expr` expressions and configured `mapred.join.define.<ident>` join types, builds aligned `CompositeInputSplit` arrays from child input formats, constructs composable record readers, and provides static `compose` helpers for table and operation expressions. It assumes input sources are sorted and partitioned identically.
- `CompositeInputSplit` is a writable aggregate of child `InputSplit`s. It reports aggregate or child length, merged or child locations, and serializes as count, child split classes, then child split payloads. Child split classes must have public default constructors.
- `CompositeRecordReader<K,V,X>` is the shared base for joins over child `ComposableRecordReader`s. It exposes abstract `combine`, ID, configuration, priority queue/comparator access, child add, key/head access, skip, delegate creation, accept, join-collector filling, key/value creation, close, and progress as the minimum child progress.
- `JoinRecordReader<K>` emits `TupleWritable` values for join operations, with nested `JoinDelegationIterator` proxying the join collector. `InnerJoinRecordReader` emits only full tuples; `OuterJoinRecordReader` emits everything from the collector.
- `MultiFilterRecordReader<K,V>` emits a single writable derived from each tuple through abstract `emit`. `OverrideRecordReader` prefers the rightmost data source for a key and overrides collector filling to avoid cross-product expansion from lower-priority streams.
- `Parser` is documented as a simple shift-reduce parser for join expressions. `Parser.Node` maps identifiers to node types and `ComposableRecordReader` constructors through reflection, stores IDs, identifier, and key-comparator class. Token classes model node, numeric, string, generic token, and token type enum values.
- `TupleWritable` is a writable, iterable tuple for join outputs. It tracks which child positions are present, exposes `has`, `get`, `size`, equality/hash, iterator, string formatting, and serialization as count, type names, then object payloads. Its Javadoc warns it is not a general-purpose tuple and relies on join framework type safety.
- `WrappedRecordReader<K,U>` adapts a normal record reader to `ComposableRecordReader`, exposing child ID, head key, skip, accept into join collector, next/create/getProgress/getPos/close, comparison, equality, and hash.

### mapred.lib helpers

- `ChainMapper` and `ChainReducer` allow multiple mapper classes to be composed within a mapper task or after a reducer inside a reducer task. Static `addMapper` and `setReducer` write chain metadata into `JobConf`, including mapper/reducer class, input/output key/value classes, pass-by-value versus pass-by-reference behavior, and per-stage `JobConf` overrides. Runtime `configure`, `map`/`reduce`, and `close` execute and clean up the chain.
- `DelegatingInputFormat` and `DelegatingMapper` support `MultipleInputs` by dispatching paths to different input formats and mapper implementations.
- `FieldSelectionMapReduce` implements both mapper and reducer to select key/value fields from delimited text. Configuration keys include `mapred.data.field.separator`, `map.output.key.value.fields.spec`, and `reduce.output.key.value.fields.spec`, with numeric, range, and open-range field syntax.
- `HashPartitioner` partitions by `Object.hashCode()`.
- `IdentityMapper` and `IdentityReducer` pass records through unchanged.
- `InputSampler` is only partially visible: it implements `Tool`, has a `JobConf` constructor, `getConf`, `setConf`, and the start of static `writePartitionFile(JobConf, InputSampler.Sampler<K,V>)`. The rest of its sampling API is outside this chunk.

## Control Flow and Behavioral Semantics

This XML has no Java control-flow bodies. Behavioral flow is inferred from method contracts, inheritance, and Javadoc.

- Old `mapred` task flow is split-oriented: an `InputFormat` creates `InputSplit`s and `RecordReader`s; `Mapper`s emit via `OutputCollector`; partitioning routes intermediate keys to reducers; reducers consume grouped keys and values; `OutputFormat` and `RecordWriter` write task output; `OutputCommitter` controls setup, commit, and abort.
- Reducer flow explicitly includes shuffle over HTTP, sort/grouping by key, and reduce invocation. The framework may reuse key/value objects, so applications must clone data they retain beyond a call.
- Running-job control flow is client polling and control: query progress, fetch task completion events and counters, wait for completion, kill jobs/tasks, and adjust priority.
- SequenceFile readers convert file splits into typed, binary, or text records. Synchronized `next`, `getPos`, `seek`, and `close` methods on record readers signal mutable stream position and reader state.
- Skip-bad-record flow starts only after a configured number of failed attempts. Tasks report record ranges to the TaskTracker before processing; if a task crashes, subsequent attempts skip the last reported range and may write skipped records under the configured skip output path.
- TaskTracker flow is daemon-centered: connect/reconnect to JobTracker, spawn child JVM tasks, let children fetch tasks and periodically report status, handle commit arbitration, serve map outputs to reducers, and surface task logs over HTTP.
- Job-control flow is dependency-DAG scheduling: jobs start waiting, become ready when dependencies succeed, submit when ready, transition to success or failed, and propagate dependency failure.
- Join flow parses a configured expression into a tree of composable input formats/readers, aligns the ith split from every source into a composite split, orders child readers by key, fills a join collector for matching keys, and emits tuples or filtered values according to inner, outer, override, or custom operation semantics.
- Chain mapper/reducer flow pipes key/value pairs through configured stages inside one map or reduce task. By-value stages serialize/deserialize between stages for safety; by-reference stages skip copying for speed and require stricter no-mutation assumptions.

## State and Persistence Behavior

- The XML itself persists the public API state for Hadoop 0.19.1. Downstream JDiff tooling depends on exact class names, method signatures, visibility, deprecation strings, exception declarations, and documentation.
- `JobConf` and `Configuration` carry many behavioral settings: sequence-file filter class/frequency/pattern, sequence-file output key/value classes, compression type, skip-bad-record thresholds, skip output path, field-selection specs, join expressions, custom join type bindings, join key comparator, chained mapper/reducer metadata, and per-stage chain configurations.
- `Writable` implementations in this chunk persist task IDs, task attempts, task completion events, task reports, composite splits, tuple values, and sequence-file records to `DataOutput`/`DataInput`.
- `TaskID` and `TaskAttemptID` string formats are public compatibility boundaries, but the docs require callers to use constructors or `forName` rather than hand parsing.
- `TaskCompletionEvent`, `TaskReport`, and `RunningJob.getCounters` are persisted or remotely transported task/job status surfaces, integrating with JobTracker and client monitoring.
- `TaskLog` and `TaskLogAppender` persist stdout, stderr, syslog, debug output, index files, and bounded/tail log captures under task-specific log directories. Cleanup purges old user logs by retention hours.
- SequenceFile formats persist key/value class metadata, raw binary key/value payloads, compression type, and filtered/text conversion semantics. Binary output format additionally persists configured logical key/value classes that may differ from the runtime `BytesWritable` wrapper.
- Join state persists through serialized `CompositeInputSplit` and `TupleWritable` payloads. Runtime join iterators also hold replay buffers in memory or byte streams; `clear` and `close` define resource reuse/release boundaries.
- Job-control state is primarily in-memory, grouped by state tables, but it wraps actual submitted Hadoop jobs and assigned `JobID`s that persist in the MapReduce framework.

## Dependencies and Integration Points

- Java core APIs: `java.io.DataInput`, `DataOutput`, `DataOutputStream`, `File`, `IOException`; `java.util.Iterator`, `ArrayList`, `Collection`, maps, regex `PatternSyntaxException`; reflection constructors; and `java.lang.Enum`.
- Servlet/logging APIs: `javax.servlet.http.HttpServlet`, request/response, `ServletException`, log4j `FileAppender` and `LoggingEvent`, and Apache Commons Logging.
- Hadoop common APIs: `Configuration`, `Configurable`, `Path`, `FileSystem`, `FileStatus`, `PathFilter`, `Progressable`, `Writable`, `WritableComparable`, `WritableComparator`, `BytesWritable`, `Text`, `LongWritable`, `SequenceFile`, and `HttpServer`.
- Old MapReduce APIs: `JobConf`, `JobClient`, `JobID`, `JobStatus`, `TaskStatus`, `TaskAttemptID`, `TaskID`, `TaskCompletionEvent`, `Counters`, `InputFormat`, `InputSplit`, `FileInputFormat`, `FileOutputFormat`, `Mapper`, `Reducer`, `Reporter`, `MapReduceBase`, `MultipleInputs`, `TaskTracker`, `JvmTask`, `JVMId`, `MapTaskCompletionEventsUpdate`, `SortedRanges.Range`, and `TaskMemoryManagerThread`.
- Filesystem and network integration points include task log directories, output directories, skip output paths, map output serving over TaskTracker Jetty, reducer shuffle over HTTP, and JobTracker/TaskTracker RPC-style callbacks.
- Tooling integration is JDiff/dev-support API comparison, not runtime Hadoop execution.

## Risks and Edge Cases

- Chunk-boundary risk: the first lines are the tail of `MultiFileSplit`, and the chunk ends inside `InputSampler.writePartitionFile`; adjacent chunks are required for complete class coverage.
- API compatibility risk is high because this is an API snapshot. Changing signatures, visibility, deprecation metadata, or documented exception types can alter JDiff output and break downstream compatibility analysis.
- Object reuse risk: `Reducer` and `RecordReader` contracts use reusable key/value instances. Applications retaining references without cloning can observe later mutation.
- Output commit risk: failures or speculative execution require correct `OutputCommitter` behavior. Incorrect `needsTaskCommit`, `commitTask`, or `abortTask` semantics can lose output, publish partial attempts, or leak temporary data.
- SequenceFile binary risk: `SequenceFileAsBinaryOutputFormat` lets logical key/value classes differ from `BytesWritable`; misconfiguration can create files whose declared classes do not match the raw bytes.
- Filter risk: `MD5Filter`, `PercentFilter`, and `RegexFilter` are configured through generic `Configuration` properties. Bad frequencies, invalid regexes, or filter classes without expected constructors/configuration behavior can fail at task startup or skew sampling.
- Skip-bad-record risk: enabling skip mode accepts data loss around failing records/groups. Streaming or asynchronous applications must manage processed-record counters themselves if framework auto-increment does not match actual processing.
- Task-log shell risk: `TaskLog.captureOutAndError` and `addCommand` build shell-wrapped commands. Quoting and executable path handling are correctness and security-sensitive.
- TaskTracker risk: many public TaskTracker methods are synchronized callbacks from child tasks. Incorrect blocking behavior can stall progress reports, commit decisions, map-output loss handling, or shutdown.
- Join correctness risk: all sources must be sorted and partitioned the same way, and key classes/comparators must match. Misaligned split counts, inconsistent comparators, or non-default-constructible child splits can break composite split creation or produce incorrect joins.
- Join memory risk: inner/outer joins can create cross products for duplicate keys. `OverrideRecordReader` avoids some cross-product expansion, but generic joins can consume large replay buffers.
- ChainMapper/ChainReducer risk: by-reference chaining can be faster but unsafe when later stages mutate key/value objects expected to be stable. Stage input/output class mismatches are not converted by the chain code and will fail at runtime.
- Deprecation migration risk: visible deprecated methods include `RunningJob.getJobID`, string `killTask`, `TaskCompletionEvent.getTaskId`/`setTaskId`, `TaskReport.getTaskId`, and job-control string mapred job ID methods. Typed `JobID`, `TaskID`, and `TaskAttemptID` APIs are the preferred replacements.

## Test Signals and Validation Targets

- JDiff validation should assert the XML is well-formed across this chunk, class/interface boundaries are preserved, and deprecation strings remain stable.
- Old `mapred` contract tests should cover `OutputCollector`, `Partitioner`, `RecordReader`, `RecordWriter`, `Reducer`, `Reporter`, `OutputFormat`, and `OutputCommitter` lifecycle ordering, especially commit/abort paths.
- `RunningJob` tests should cover progress values, completion/success transitions, task completion event pagination, counters, priority changes, job kill, typed task kill, and deprecated string compatibility.
- SequenceFile tests should round-trip standard, binary, text, filtered, and compressed record readers/writers; validate declared key/value classes for binary output; and test split progress/seek/close behavior.
- Filter tests should exercise MD5, percent, regex, bad regex configuration, and configured custom filter class loading.
- Skip-bad-record tests should simulate deterministic mapper/reducer failures, counter auto-increment on/off, threshold narrowing, `Long.MAX_VALUE` no-narrowing behavior, and skip output path null/default behavior.
- Writable status tests should round-trip `TaskID`, `TaskAttemptID`, `TaskCompletionEvent`, `TaskReport`, `CompositeInputSplit`, and `TupleWritable`, including malformed ID strings and deprecated string accessors.
- Task-log tests should validate log file/index location, sync, cleanup retention, tail-length capture, debug capture, log4j appender flush/close, and task-log servlet URL/output behavior.
- TaskTracker integration tests should cover child task fetch, status updates, diagnostics, commit pending/can commit/done, shuffle and filesystem error reporting, map completion events, map output lost, map-output servlet serving, idle state, and memory manager enablement.
- Job-control tests should cover dependency addition limits, waiting-to-ready transitions, dependent failure propagation, successful submission, failed submission, thread stop/suspend/resume, and `allFinished`.
- Join tests should cover expression parsing, default and custom identifiers, composite split serialization, split-count mismatch, inner/outer/override joins, duplicate-key cross products, tuple serialization, reset/replay iterators, and comparator/key-class mismatch.
- Chain tests should verify mapper and reducer chains with by-value and by-reference stages, per-stage `JobConf` precedence, output key/value class inference from the last stage, close ordering, and class mismatch failures.

## Chunk Merge Notes

- Merge with the preceding chunk for the full `MultiFileSplit` definition and any immediately prior `mapred` APIs.
- Merge with the following chunk for the remainder of `InputSampler` and later `org.apache.hadoop.mapred.lib` APIs.
- The final per-file report should describe `hadoop_0.19.1.xml` as a generated JDiff API snapshot and avoid treating this chunk as implementation source.

### subset-b-007300: lines 30909-37234

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 30909-37234

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.1, not implementation source. It records class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, checked exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadoc contracts.

The range starts inside `org.apache.hadoop.mapred.lib.InputSampler`, after the class declaration and earlier methods, then covers the rest of `InputSampler` plus most of `org.apache.hadoop.mapred.lib`, all visible `org.apache.hadoop.mapred.lib.aggregate` and `org.apache.hadoop.mapred.lib.db` APIs, `org.apache.hadoop.mapred.pipes.Submitter`, Hadoop's original metrics API/SPI/provider/util classes, and most of `org.apache.hadoop.net` through the start of `SocketInputStream`. The final `SocketInputStream` class continues beyond this chunk, so its trailing Javadoc and any later members must be reconciled with the adjacent chunk.

## Purpose and Major API Surface

The initial `InputSampler` fragment documents total-order sampling support for old `mapred`. `writePartitionFile` samples keys from an `InputFormat`, sorts them with the job's output key comparator, selects split points for reduce ranks, and writes the partition file named by `TotalOrderPartitioner.getPartitionFile`. The nested `Sampler<K,V>` interface defines `getSample(InputFormat<K,V>, JobConf)`. `IntervalSampler`, `RandomSampler`, and `SplitSampler` implement it with regular-interval, probabilistic, and first-records-per-split strategies, each bounded by a maximum number of splits when configured.

`org.apache.hadoop.mapred.lib` contains stock old-API MapReduce helpers. `InverseMapper` swaps key/value pairs, `LongSumReducer` sums `LongWritable` values, `RegexMapper` emits regular-expression captures, `TokenCountMapper` tokenizes text values, and `NullOutputFormat` provides a sink output format. `NLineInputFormat` splits text input by a configured number of lines and returns `LongWritable`/`Text` readers.

`KeyFieldBasedComparator` and `KeyFieldBasedPartitioner` implement Unix-sort-like key field selection. The comparator supports numeric and reverse ordering plus `-k pos1[,pos2]`, interpreting fields separated by `map.output.key.field.separator`. The partitioner hashes configured key fields and exposes a protected byte-range `hashCode` helper. `TotalOrderPartitioner` consumes the partition file written by `InputSampler`; it has `configure`, `getPartition`, and static `setPartitionFile`/`getPartitionFile` methods plus `DEFAULT_PATH`.

`MultipleInputs` configures jobs with path-specific `InputFormat` classes, optionally path-specific `Mapper` classes. `MultipleOutputFormat` is an abstract `FileOutputFormat` that routes records to different files by overriding leaf filename generation, key/value-based filename generation, actual key/value generation, input-file-derived names, and the base writer. `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` provide concrete sequence-file and text writers.

`MultipleOutputs` is the named-output API for old `mapred`. Static methods register single or multi named outputs in `JobConf`, inspect their output format/key/value classes, and enable counters. Instance methods create `OutputCollector`s for named or multi-named channels and close all opened writers. The docs constrain named output names to letters/numbers and disallow `part`; mapper-side named output records bypass the reduce phase unless also written to the main collector. Counters are disabled by default, use `MultipleOutputs` as the group, and use the named output or `namedOutput_multiName` as counter names.

`MultithreadedMapRunner` runs mapper calls concurrently under old `mapred`, exposing `configure(JobConf)` and `run(RecordReader, OutputCollector, Reporter)`.

`org.apache.hadoop.mapred.lib.aggregate` is the old aggregation framework. `ValueAggregator` defines mutable aggregators with `addNextValue`, `reset`, `getReport`, and combiner output. Implementations include `LongValueSum`, `LongValueMax`, `LongValueMin`, `DoubleValueSum`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram`. They keep running sums, extrema, unique sets, or histograms and emit report strings plus combiner-friendly intermediate values.

`ValueAggregatorDescriptor` maps input key/value records to aggregation key/value pairs and exposes constants `TYPE_SEPARATOR` and `ONE`. `ValueAggregatorBaseDescriptor` supplies common type names such as `LONG_VALUE_SUM`, `DOUBLE_VALUE_SUM`, `VALUE_HISTOGRAM`, and extrema/string variants, and can generate typed aggregators or text entries. `UserDefinedValueAggregatorDescriptor` reflectively constructs user descriptors from a class name and `JobConf`. `ValueAggregatorJobBase` stores configured descriptor lists; mapper, combiner, and reducer subclasses implement the generic aggregation pipeline. `ValueAggregatorJob` creates `JobConf` or `JobControl` instances for complete aggregate jobs and can configure descriptor classes.

`org.apache.hadoop.mapred.lib.db` exposes JDBC input/output formats. `DBConfiguration` is a constants holder and setup utility for driver, URL, username, password, input table/fields/conditions/order, complete input query and count query, input DBWritable class, output table, and output fields. `DBInputFormat` implements `InputFormat<LongWritable,T extends DBWritable>` and `JobConfigurable`; it configures a database-backed reader, creates row-range splits, and supports table/conditions/order/fields or full query/count-query setup. `DBInputSplit` serializes start/end row indexes. `DBRecordReader` builds select queries, iterates rows into `DBWritable` values, tracks position/progress, and closes JDBC resources. `NullDBWritable` is a do-nothing DB/Writable bridge. `DBOutputFormat` writes reducer output keys extending `DBWritable` into SQL tables with a prepared insert query; its `DBRecordWriter` writes only the key and closes on task completion. `DBWritable` defines `write(PreparedStatement)` and `readFields(ResultSet)`.

`org.apache.hadoop.mapred.pipes.Submitter` is the public entry point for Hadoop Pipes jobs. It gets/sets the executable, toggles whether the record reader, mapper, reducer, and record writer are Java implementations, controls keeping the command file for debugging, submits or runs a configured job, and provides `run`/`main`.

The metrics packages describe Hadoop's original metrics subsystem. `ContextFactory` stores attributes, creates named contexts from configuration, and returns a singleton factory or null context. `MetricsContext` manages lifecycle, record creation, periodic updater registration, and the default period. `MetricsRecord` is the typed tag/metric interface with setters for string/int/long/short/byte tags, metric setters/incrementers for int/long/short/byte/float, and `update`/`remove`. `MetricsUtil` gets contexts and creates host-tagged records; `Updater` is the periodic callback.

Metrics providers and SPI include `FileContext` for file/stdout output, `GangliaContext` for Ganglia emission, `EventCounter` as a Log4J appender with fatal/error/warn/info counters, `JvmMetrics` as a JVM metrics updater, `AbstractMetricsContext` as the synchronized provider base, `MetricsRecordImpl` as the record implementation, `MetricValue` as absolute-vs-incremental numbers, `NullContext` and `NullContextWithUpdateThread`, `OutputRecord`, and `Util.parse` for server specifications.

`org.apache.hadoop.metrics.util` provides JMX and mutable metric helpers. `MBeanUtil` registers/unregisters Hadoop-format MBeans. `MetricsIntValue` and `MetricsLongValue` are synchronized non-time-varied gauges/counters with set/get/inc/dec/push behavior. `MetricsTimeVaryingInt` pushes per-period deltas. `MetricsTimeVaryingRate` tracks operation counts, average time for the previous interval, min/max operation time, and min/max reset.

The `org.apache.hadoop.net` section covers DNS, rack mapping, socket, and topology helpers. `CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping` with a cache. `DNS` performs reverse DNS, interface IP lookup, default IP/host lookup, and nameserver-based host lookup. `DNSToSwitchMapping` resolves names/IPs to rack strings. `ScriptBasedMapping` is a final configurable mapping implementation driven by `topology.script.file.name`.

`NetUtils` centralizes RPC/network helpers: socket factory lookup from class-specific and default configuration keys, socket address parsing from `host`, `host:port`, or URI strings, migration from old bind-address/port pairs to a combined address property, static host resolution mappings for tests, client connect address normalization for wildcard-bound servers, timeout-capable socket input/output stream wrappers, and host name normalization to textual IP addresses.

`NetworkTopology`, `Node`, and `NodeBase` model Hadoop's rack-aware cluster tree. `NetworkTopology` adds/removes leaf nodes, counts racks/leaves, looks up nodes by path, computes distance through closest common ancestors, checks rack co-location, chooses random nodes within or outside scopes, counts available nodes excluding a list, stringifies the tree, and pseudo-sorts replica locations by reader distance. `Node` exposes name, network location, parent, and level. `NodeBase` implements those fields plus path normalization and path construction constants.

`SocketInputStream` begins at the end of the range. It wraps a `ReadableByteChannel` or `Socket` as an `InputStream` and `ReadableByteChannel` with read timeouts. Construction configures the underlying selectable channel as non-blocking, zero timeout means infinite wait, negative timeout is invalid, `waitForReadable` waits with the stream timeout, and `close` is synchronized.

## Control Flow and Behavioral Contracts

Total-order partition setup flows from `InputSampler.run` or direct API use: configure a `JobConf`, instantiate a sampler, call `getSample` over selected input splits, sort sampled keys with the output key comparator, choose partition boundaries for reducer ranks, and persist them for `TotalOrderPartitioner`. `RandomSampler` shuffles split order and may replace earlier sampled keys after a split quota is full; `IntervalSampler` emits keys based on retained/seen record ratios; `SplitSampler` takes leading records from each sampled split. These operations run on the client side and can be expensive for many splits.

MapReduce helper control flow follows the old `Mapper`/`Reducer`/`OutputFormat` template. Mappers and reducers receive key/value pairs plus `OutputCollector` and `Reporter`; output formats validate and create writers; `MultipleOutputFormat` routes each record through filename/key/value hooks before delegating to a base writer. `MultipleOutputs` must be constructed during task `configure`, used to obtain collectors during map/reduce, and closed in `close`; unclosed collectors risk incomplete files.

Field-based comparison and partitioning are driven by `JobConf`. Callers configure sort or partition key specs, and the comparator/partitioner parse field and character positions using one-based indexes with end-position zero meaning end of field. Numeric and reverse modifiers affect comparator results; partitioning hashes byte ranges from selected key fields.

Aggregation flow is descriptor driven. The mapper iterates configured `ValueAggregatorDescriptor`s for each input record and emits `Text` aggregation IDs and values. Combiners and reducers select a `ValueAggregator` by type prefix, feed it values, and emit either combiner intermediates or final report strings. `ValueAggregatorJob` packages this configuration into one or more jobs.

DB input flow connects through JDBC during `configure`/reader construction, computes row counts through `getCountQuery`, divides rows into `DBInputSplit` start/end ranges, builds a select query per split, and calls `DBWritable.readFields(ResultSet)` for each row. DB output flow constructs an insert `PreparedStatement`, calls `DBWritable.write(PreparedStatement)` on output keys, and writes batches/commits during writer close. The API intentionally ignores output values.

Pipes submission flow mutates the supplied `JobConf` with executable and Java/non-Java component settings, optionally keeps a command file for debug replay, then submits or runs the job through the classic `JobClient` path. The command-line `run`/`main` methods expose the same setup to users.

Metrics flow is buffered and periodic. A caller obtains a `MetricsContext`, creates records, sets tags and metrics, and calls `update`. The context's internal table is keyed by record name plus tag values; matching rows are updated and new tag sets create new rows. Registered `Updater`s are called on the configured period, providers emit each buffered row through `emitRecord`, and `flush` runs after a period. `remove` deletes matching rows; `stopMonitoring` pauses provider output; `close` stops monitoring and clears buffered state.

Network flow starts with name/rack resolution. `DNS` and `DNSToSwitchMapping` turn interfaces, hostnames, IPs, and rack scripts into normalized addresses or rack paths. `CachedDNSToSwitchMapping` reduces repeated raw resolver calls. `NetworkTopology` consumes `Node`/`NodeBase` objects whose network locations are path-like rack/datacenter strings, then uses those locations for block placement style decisions such as distance ordering and rack diversity checks. `NetUtils` bridges configuration, static test resolutions, wildcard listener addresses, and timeout-capable channel streams.

`SocketInputStream` read flow is select-based. Reads on the non-blocking channel either read immediately or call `waitForReadable`; if the selector times out, the contract raises `SocketTimeoutException`. After wrapping a socket channel this way, the docs warn that using the socket's ordinary input/output streams can throw because the channel has been switched to non-blocking mode.

## State, Persistence, and Side Effects

The XML itself is persistent API compatibility data. Runtime persistent or externally visible state includes total-order partition files, job configuration keys, MapReduce output files, named-output files and counters, aggregate reports, JDBC connections/statements/result sets, SQL table rows, Pipes executable and command-file settings, metrics configuration attributes, buffered metrics tables, provider output files or Ganglia packets, Log4J event counts, JMX MBean registrations, DNS/rack caches, static host-resolution maps, network topology trees, and socket channel modes.

Most mapred helpers keep behavior in `JobConf`: input paths/formats/mappers, output format classes and named-output key/value classes, counter enablement, field separators, regex settings, line split settings, total-order partition file path, aggregate descriptor classes, DB connection details, and Pipes toggles. These settings are serialized through job submission and become part of task behavior.

The DB APIs have strong external side effects. Input formats run count and select SQL queries against configured databases. Output formats construct insert statements and write reducer keys into tables. `DBWritable` implementations own object-to-column mapping and must keep JDBC parameter/result-set ordering consistent with configured field names.

Metrics state is global and provider-specific. `ContextFactory` is a singleton attribute store. `AbstractMetricsContext` holds monitoring period, updater lists, and buffered records; `MetricsRecordImpl` holds mutable tags/metrics before update. `FileContext` opens configured files in append mode or uses stdout, while `GangliaContext` emits over the network. `NullContextWithUpdateThread` keeps periodic updater calls even though records are discarded.

Network state includes mutable static host resolutions in `NetUtils`, resolver caches in `CachedDNSToSwitchMapping`, mutable parent/level/name/location fields in `NodeBase`, and counts/tree links in `NetworkTopology`. `SocketInputStream` mutates the underlying channel by setting non-blocking mode and synchronizes close.

## Dependencies and Integration Points

This chunk is anchored in the old `org.apache.hadoop.mapred` API: `JobConf`, `InputFormat`, `InputSplit`, `RecordReader`, `Mapper`, `Reducer`, `OutputCollector`, `Reporter`, `Partitioner`, `OutputFormat`, `RecordWriter`, `FileInputFormat`, `FileOutputFormat`, `SequenceFileOutputFormat`, `TextOutputFormat`, `RunningJob`, and `JobControl`. It also depends on Hadoop IO types such as `Writable`, `WritableComparable`, `LongWritable`, `Text`, and `WritableComparator`, plus filesystem types `Path` and `FileSystem`.

Aggregate and DB integration reaches outside HDFS/MapReduce. Aggregation uses Java collections and text-encoded intermediate keys/values. DB formats depend on JDBC `Connection`, `PreparedStatement`, `ResultSet`, `SQLException`, configured JDBC driver classes, and SQL dialect support for count/select/limit/offset style queries implied by split readers.

Pipes integrates Java job submission with non-Java executables, distributed job resources, and task-local command files. Correctness depends on matching the Java/non-Java component flags to the actual executable protocol.

Metrics integrates with `hadoop-metrics.properties`/`ContextFactory` attributes, provider reflection, file IO, Ganglia, Log4J, JVM runtime metrics, JMX `ObjectName`s, and Hadoop components that register `Updater`s. `MetricsUtil` hides provider creation failures by logging and returning a null context.

Networking integrates with Java networking (`InetAddress`, `InetSocketAddress`, `Socket`, `SocketFactory`, `SocketChannel`, selectable NIO channels), Hadoop IPC `Server` and `VersionedProtocol`-style configuration, external topology scripts, DNS infrastructure, and HDFS block placement concepts represented by rack-aware `Node`s.

## Risks and Compatibility Notes

This range has partial boundaries. `InputSampler` starts before line 30909 and `SocketInputStream` continues after line 37234, so final per-file research must merge adjacent chunks before making whole-class conclusions for those two APIs.

Because this is a JDiff compatibility artifact, seemingly small changes to signatures, generic type text, visibility, checked exceptions, static/final/synchronized flags, fields, deprecation metadata, or Javadocs can indicate source or binary compatibility changes for Hadoop 0.19.1 clients.

Sampling and total-order partitioning are correctness-sensitive. If sampled keys are sparse, skewed, or sorted with a comparator different from task output comparison, reducer ranges can be unbalanced or incorrect. Client-side sampling can read many splits, so `RandomSampler` over all splits is explicitly expensive.

Field-based comparator/partitioner behavior is fragile around one-based field indexes, character offsets, numeric parsing, reverse flags, separators, and byte-range hashing. Parser changes can break jobs that model Unix `sort` keys in configuration strings.

Multiple output APIs can create many task output files. Bad named-output validation, filename derivation, multi-name handling, missing `close`, or counter naming changes can cause file collisions, invalid paths, leaked writers, missing data, or incompatible counters.

Aggregation keys encode type and aggregation ID in text. Separator collisions, malformed numeric inputs, inconsistent combiner output, very large unique sets or histograms, and descriptor class-loading failures can corrupt results or exhaust memory.

DB formats are exposed to SQL correctness and transactional risk. Count/select mismatch, unstable ordering, SQL injection through configuration strings, driver-specific limit/offset behavior, incorrect `DBWritable` field order, commit/rollback behavior, and connection leaks can produce duplicate/missing rows or failed tasks.

Metrics APIs are mutable and partly concurrent. The docs say `MetricsRecord.update` is atomic for separate record instances with the same tags, but the same `MetricsRecord` instance should not be used concurrently. Provider misconfiguration can silently fall back to null metrics through `MetricsUtil`, while updater exceptions, incremental-vs-absolute handling, tag matching in `remove`, and monitoring lifecycle races affect observability.

Network APIs are environment-dependent. DNS and topology scripts can fail or return mismatched list lengths; static resolutions are process-global; wildcard address normalization must preserve reachable ports; socket factory properties may be malformed; non-blocking channel wrapping can surprise callers that later use raw socket streams.

Network topology assumes nodes are leaves when added, have normalized path-like locations, and belong to the same cluster for distance/rack checks. Wrong parent/level state or unsynchronized mutation can break rack-aware placement calculations.

## Test Signals

JDiff validation should confirm this XML range stays well formed at chunk boundaries and preserves each public/protected class, interface, constructor, method, field, generic signature, exception declaration, visibility/static/final/abstract/synchronized flag, and deprecation marker.

Sampling and partitioning tests should cover `SplitSampler`, `IntervalSampler`, and `RandomSampler` across empty inputs, many splits, `maxSplitsSampled`, sorted and skewed data, replacement behavior, comparator ordering, partition file write/read round trips, `TotalOrderPartitioner.getPartition`, and command-line `InputSampler.run` argument handling.

Mapred helper tests should cover inverse mapping, long summing, regex capture configuration, token counting, null output writer behavior, N-line split construction, multithreaded map runner concurrency/error propagation, multiple input path registration and mapper selection, key-field comparison/partition parsing, numeric/reverse sort options, and separator edge cases.

Multiple output tests should cover named output validation, rejection of `part`, single vs multi named outputs, configured output format/key/value class lookups, counters enabled/disabled and counter names, mapper-side output bypassing reducers, collector reuse, writer close, sequence/text base writers, filename/key/value override hooks, and invalid multi-name paths.

Aggregate tests should cover every aggregator with normal and malformed values, reset behavior, combiner output round trips, unique-count maximum behavior, histogram reports/details/items, descriptor-generated entries, user descriptor loading/configuration, mapper/combiner/reducer integration, and `ValueAggregatorJob` creation with explicit and default descriptors.

DB tests should use a test JDBC database to cover `configureDB`, both `DBInputFormat.setInput` overloads, count query generation/override, split start/end serialization, select query generation/override, `DBWritable` read/write field ordering, reader progress/position/close, output insert query construction with known and null field names, writer batching/close behavior, failed SQL handling, and value-ignored output semantics.

Pipes tests should cover executable get/set, Java component toggles, command-file retention configuration, `submitJob` mutation of `JobConf`, missing executable failures, `runJob`/`jobSubmit` return behavior, and command-line parsing.

Metrics tests should cover `ContextFactory` singleton and attribute lifecycle, reflective provider creation and null fallback, context start/stop/restart/close, updater registration and periodic calls, record tag/metric setter overloads, incremental vs absolute metrics, atomic updates from separate records, `remove` matching rules, file append/stdout output, Ganglia emission error handling, Log4J event counting, JVM updater initialization, SPI record creation, `MetricValue` flags, null contexts, output record views, server-spec parsing, MBean register/unregister names, and synchronized metric helper push/reset behavior.

Network tests should cover DNS lookups with controlled interfaces/nameservers, rack mapping cache hits/misses, script-based mapping configuration, socket factory property resolution and malformed properties, socket address parsing forms and default ports, static resolution add/get/list, wildcard listener connect addresses, timeout-capable input/output stream selection with and without socket channels, host normalization, topology add/remove/contains/getNode/counts/distance/rack checks, random scoped selection including `~` exclusion, available-node counts with exclusions, pseudo-sort by local node/rack/random fallback, `NodeBase` path normalization, and `SocketInputStream` timeout/read/close/isOpen behavior.

### subset-b-007301: lines 37235-43512

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 37235-43512

## Scope

This chunk covers a JDiff API XML slice from Hadoop 0.19.1. It is not executable Hadoop source; it is a generated public API inventory used by JDiff/dev-support tooling to compare class, method, field, signature, visibility, inheritance, exception, and Javadoc metadata across Hadoop releases.

The range starts in the tail of `org.apache.hadoop.net.SocketInputStream` documentation, then covers `org.apache.hadoop.net.SocketOutputStream`, socket factory classes, the complete `org.apache.hadoop.record` API surface visible in this range, record compiler and generated parser classes, record metadata classes, security UGI types, tool entry points, and much of `org.apache.hadoop.util` through the first overload of `StringUtils.byteToHexString`. The chunk ends inside `StringUtils`; later string utility methods are outside this chunk and must be reconciled by the merge lane.

## Purpose

The purpose of this XML region is to preserve Hadoop Common's public Java API as structured data for compatibility checks. Each `<package>`, `<class>`, `<interface>`, `<constructor>`, `<method>`, and `<field>` element records the contract that downstream code may compile against. The embedded CDATA documentation captures intended semantics, such as timeout behavior for socket streams, serialization formats for records, Hadoop generic command-line options, UGI persistence, and utility behavior.

Because this file is a JDiff baseline, the operational impact is indirect. Build or release tooling compares a newer API dump against this baseline to detect additions, removals, signature changes, visibility changes, checked exception changes, inheritance changes, and documentation differences.

## Important APIs and Types

### Network classes

The chunk starts with `org.apache.hadoop.net.SocketOutputStream`, a public `OutputStream` that also implements `WritableByteChannel`. It can be constructed from a `WritableByteChannel` or `Socket` plus a non-negative timeout. The documented behavior configures the socket channel as non-blocking; after this, the socket's ordinary Java blocking streams may throw `IllegalBlockingModeException`, so callers are expected to pair it with Hadoop's timeout-aware socket input stream. Important methods are `write(int)`, `write(byte[], int, int)`, channel-style `write(ByteBuffer)`, synchronized `close()`, `isOpen()`, `getChannel()`, `waitForWritable()`, and `transferToFully(FileChannel, long, int)`.

`SocksSocketFactory` and `StandardSocketFactory` both extend `javax.net.SocketFactory`. `SocksSocketFactory` also exposes `getConf()` and `setConf(Configuration)`, indicating Hadoop configuration integration for proxy behavior. Both factories expose the usual socket creation overloads for plain sockets and host/address plus port/local binding combinations, and both implement `equals()`/`hashCode()` for factory identity.

### Record I/O framework

The `org.apache.hadoop.record` package defines Hadoop's older record-serialization stack:

- `BinaryRecordInput` and `BinaryRecordOutput` wrap `InputStream`/`DataInput` and `OutputStream`/`DataOutput` and implement primitive, string, buffer, record, vector, and map read/write operations.
- `CsvRecordInput`/`CsvRecordOutput` and `XmlRecordInput`/`XmlRecordOutput` expose the same record input/output shape for tagged text formats.
- `RecordInput` and `RecordOutput` are the common serializer/deserializer interfaces, with methods for byte, boolean, int, long, float, double, string, `Buffer`, record boundaries, vector boundaries, and map boundaries. The tag parameter is meaningful for tagged formats such as XML.
- `Index` is the iteration cursor returned by `startVector()` and `startMap()`, with `done()` and `incr()` used to walk collection elements.
- `Buffer` is a mutable byte-sequence value type with constructors for empty, full-array, and array-slice content. It exposes `set`, `copy`, `get`, `getCount`, `getCapacity`, `setCapacity`, `reset`, `truncate`, append overloads, `hashCode`, `compareTo`, `equals`, `toString` overloads, and `clone`.
- `Record` is an abstract base for generated records. It implements `WritableComparable` and `Cloneable`, requires tagged `serialize`, tagged `deserialize`, and `compareTo`, and provides untagged `serialize`, `deserialize`, `write(DataOutput)`, `readFields(DataInput)`, and `toString`.
- `RecordComparator` extends `WritableComparator` and registers optimized raw comparators through synchronized static `define(Class, RecordComparator)`.
- `Utils` provides binary helpers for float/double parsing, zero-compressed variable-length int/long read/write on byte arrays and streams, encoded size calculation, byte comparison, and a public `hexchars` table.

### Record compiler APIs

`org.apache.hadoop.record.compiler` describes the Java-side record compiler model. `CodeBuffer` provides `toString()`. `Consts` exposes string constants such as `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`. Primitive and compound schema-model classes include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, `JRecord`, `JField<T>`, `JType`, and `JFile`. `JFile.genCode(String, String)` is the generation entry point for a file containing included files and records.

`org.apache.hadoop.record.compiler.ant.RccTask` is an Ant `Task` wrapper with setters for language, file, fail-on-error behavior, destination directory, filesets, and `execute()`.

`org.apache.hadoop.record.compiler.generated` is the JavaCC-generated parser/lexer surface:

- `ParseException` records parser failures, current token, expected token sequences, token images, and newline text, with constructors for generated and custom messages plus `getMessage()` and `add_escapes()`.
- `Rcc` has constructors for input streams, readers, and token managers. It exposes `main`, `usage`, `driver`, grammar productions such as `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, plus `ReInit` overloads, token access, parse-exception generation, and tracing toggles.
- `RccConstants` defines token ids for module/record/include keywords, primitive types, map/vector syntax, braces, commas, dots, string and identifier tokens, lexical states, and `tokenImage`.
- `RccTokenManager` exposes token-manager construction, debug stream selection, reinitialization, lexical-state switching, token fill/get, and lexer state fields.
- `SimpleCharStream` exposes stream constructors for `Reader` and `InputStream` variants, tab sizing, buffer expansion/fill, token start, line/column update, char reads, begin/end line and column access, backup, reinitialization, image/suffix extraction, finalization through `Done`, and begin-line adjustment. It also exposes parser buffer and position fields.
- `Token` carries token kind, begin/end line and column, image, next-token link, and special-token link, with `toString()` and `newToken(int)`.
- `TokenMgrError` models lexical errors with constructors, escaping helpers, lexical-error text construction, and `getMessage()`.

### Record metadata

`org.apache.hadoop.record.meta` describes runtime type information for records. `FieldTypeInfo` exposes field id and `TypeID` plus equality/hash behavior. `TypeID` stores a byte type value and exposes singleton type ids for bool, buffer, byte, double, float, int, long, and string. `TypeID.RIOType` defines byte constants for primitive, map, struct, vector, and string-like record I/O types. `MapTypeID`, `VectorTypeID`, and `StructTypeID` represent compound type ids. `RecordTypeInfo` extends `Record`, stores a record name and field metadata, supports nested struct lookup, and implements record serialization/deserialization and comparison. `meta.Utils.skip(RecordInput, String, TypeID)` is a helper for skipping a typed value in serialized input.

### Security and identity

`org.apache.hadoop.security.AccessControlException` extends the filesystem permission exception and has a no-argument constructor for unwrapping from `RemoteException` plus a message constructor.

`UnixUserGroupInformation` extends abstract `UserGroupInformation`. It stores user and group names, can be created from user/group arrays, exposes an immutable factory, implements `Writable` read/write in a string-marked UGI format, saves to and reads from `Configuration` as comma-separated user/group properties, logs in from Unix or configuration, and implements equality, user-name hash code, and comma-separated string conversion. `UGI_PROPERTY_NAME` is the public property key. `UserGroupInformation` itself is a `Writable` abstraction with thread-current UGI get/set, abstract user and group accessors, `login(Configuration)`, `readFrom(Configuration)`, and a public commons-logging `LOG`.

### Tools

`org.apache.hadoop.tools.DistCp` implements `Tool` and exposes configuration setters/getters, a static `copy(Configuration, String, String, Path, boolean, boolean)`, `run(String[])`, `main(String[])`, `getRandomId()`, and `LOG`. Its nested `DuplicationException` defines an `ERROR_CODE` for duplicate source files.

`HadoopArchives` implements `Tool` and exposes `archive(List<Path>, String, Path)`, `run`, `main`, and configuration setters/getters for creating HAR archives. `Logalyzer` exposes `doArchive`, `doAnalyze`, and `main` for archiving and analyzing Hadoop logs. Its nested `LogComparator` extends `Text.Comparator` and implements `Configurable`, while `LogRegexMapper` extends `MapReduceBase` and implements a mapper from writable keys and text values to text/count outputs.

### Utility classes

The `org.apache.hadoop.util` part of the chunk includes:

- `CyclicIteration<K,V>`: iterable over a `NavigableMap` starting after a supplied key and wrapping from the last entry to the first.
- `Daemon`: daemon `Thread` wrapper constructors and `getRunnable()`.
- `DataChecksum`: checksum abstraction over CRC32/null checksum types. It can construct from type/bytes-per-checksum, header bytes, or `DataInputStream`, write/read checksum headers and values, compare stored checksums, expose checksum metadata, and implement `Checksum.reset/update/getValue`.
- `DiskChecker`: mkdir-with-race-tolerant-exists-check, directory checking, and `DiskErrorException`/`DiskOutOfSpaceException`.
- `GenericOptionsParser`: Commons CLI parser for Hadoop generic options such as `-conf`, `-D`, `-fs`, `-jt`, `-files`, `-libjars`, and `-archives`; it exposes remaining arguments, the parsed `CommandLine`, libjar URL parsing, and usage printing.
- `GenericsUtil`: type-safe class extraction and list-to-array helpers, with the no-class overload requiring a non-empty list.
- `HeapSort`, `QuickSort`, `MergeSort`, `IndexedSortable`, and `IndexedSorter`: sort implementations and callback interfaces for index-addressed data. QuickSort documents fallback to HeapSort at max recursion depth and progress-reporting overloads.
- `HostsFileReader`: synchronized include/exclude hosts file name updates and refresh, plus getters for included and excluded hosts sets.
- `LineReader`: buffered line reader over `InputStream`, using explicit buffer size or `io.file.buffer.size`, with bounded `readLine` overloads and close.
- `NativeCodeLoader`: native `libhadoop` load status and configuration toggles for allowing native libraries.
- `PlatformName` and `PrintJarMainClass`: small main-class utilities for platform naming and jar manifest inspection.
- `PriorityQueue<T>`: abstract fixed-size priority queue requiring `lessThan(Object,Object)`, with `initialize`, `put`, conditional `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`.
- `ProcfsBasedProcessTree`: Linux `/proc` process-tree tracker with availability, refresh, root aliveness, destroy, cumulative virtual memory, PID-file read, string rendering, and configurable SIGKILL interval.
- `ProgramDriver`: registry/dispatcher for named example or tool main classes.
- `Progress` and `Progressable`: hierarchical progress tree with named phases, synchronized phase advancement/status/progress, completion, and overall progress reporting; `Progressable.progress()` is used to prevent Hadoop timeouts during long operations.
- `ReflectionUtils`: configuration injection, new instance creation, contention tracing, thread-info printing/logging, and generic class extraction.
- `RunJar`: jar unpacking and job-jar execution.
- `ServletUtil`: servlet/JSP helpers for initial HTML output, trimmed parameter retrieval, HTML footer, and percentage graph generation.
- `Shell`, `Shell.ExitCodeException`, and `Shell.ShellCommandExecutor`: Unix command execution base, platform command constants, environment and working-directory configuration, interval-gated execution, command output parsing, static command execution, exit-code exceptions, and a concrete executor storing small command output.
- Start of `StringUtils`: exception stringification, hostname simplification, human-readable integer formatting, percent formatting, comma-joining arrays, and the first byte-array-to-hex overload.

## Control Flow

The XML itself has no executable control flow. Its structural flow is the JDiff hierarchy: package entries contain class/interface entries; classes contain constructors, methods, fields, implemented interfaces, inherited base classes, exceptions, parameters, and documentation. A JDiff consumer walks these elements to compare public API compatibility between releases.

The documented APIs describe several important runtime flows:

- Timeout socket writes configure channels non-blocking, wait for writability with stream timeout, and support complete `FileChannel.transferTo` loops that throw EOF or socket timeout on incomplete transfers.
- Record serialization flows start and end records, vectors, and maps, then read/write primitives and buffers. Collection reading uses `Index.done()` and `Index.incr()`.
- Generated records flow through `Record.write()`/`readFields()` via binary record input/output, while tagged formats pass field tags through the serializer/deserializer interface.
- Record compiler flow parses an Rcc input into `JFile`, included files, modules, record lists, fields, and type models, then `JFile.genCode()` emits target-language output. Ant integration wraps this parser/generator in `RccTask.execute()`.
- UGI flow reads identity from configuration or Unix shell commands, caches one UGI per user, can save back to configuration, and exposes a thread-current identity through static get/set.
- DistCp and HadoopArchives are `Tool` drivers: command-line args are parsed, source paths are listed, map tasks perform copying or archive-file creation, and reducers finish empty-copy or archive-index work.
- Generic option parsing mutates a `Configuration` before application-specific arguments are consumed by the actual command.
- Shell flow gates execution by interval, configures environment/working directory, starts a subprocess, parses output through subclass hooks, and records process/exit code. `ShellCommandExecutor` supplies the simple case where output is accumulated as a small string.
- Process-tree flow refreshes `/proc` state, checks root-process liveness, computes cumulative virtual memory, and can destroy a root process after a configured sleep-before-SIGKILL interval.

## State and Persistence Behavior

Persistent state in this XML file is API metadata: class names, package names, type signatures, inheritance, method parameters, checked exceptions, visibility, static/final/synchronized/native/abstract flags, deprecation status, and documentation. It should be treated as release-baseline data. Editing it changes what JDiff reports as the Hadoop 0.19.1 API.

The APIs represented here also define or expose stateful behavior:

- Socket stream instances hold a channel and timeout and alter the associated channel's blocking mode.
- `Buffer` owns mutable byte storage, count, and capacity; callers must distinguish copy semantics from direct `get()` access.
- Record input/output implementations hold underlying streams and collection cursors; variable-length integer encodings are persistent wire-format details.
- Parser/token-manager classes expose mutable lexer/parser state such as current token, next token, lexical state, buffers, positions, line/column arrays, and debug stream.
- `RecordTypeInfo` persists record names and field type metadata and can serialize/deserialize that metadata as a Hadoop record.
- UGI persists user/group identity in memory, thread-local/current context, writable streams, and configuration properties.
- Tool classes persist configuration through `Tool.setConf()`/`getConf()`, while DistCp/HadoopArchives/Logalyzer persist output into DFS paths and MapReduce output directories.
- `DataChecksum` persists checksum type, bytes-per-checksum, current checksum accumulator, and header layout used by DFS data transfer.
- `HostsFileReader` persists include/exclude file names and current host sets.
- `PriorityQueue`, `Progress`, `Shell`, and `ProcfsBasedProcessTree` all maintain mutable runtime state that is observable through their public methods.

## Dependencies and Integration Points

This API slice integrates many Hadoop Common subsystems:

- Java standard library dependencies include `java.io`, `java.net`, `java.nio`, `java.nio.channels`, collections, `java.util.zip.Checksum`, servlet request/response types, and reflection/thread/process APIs.
- Hadoop core dependencies include `Configuration`, `Path`, `Writable`, `WritableComparable`, `WritableComparator`, `Text`, `Text.Comparator`, MapReduce old API types (`Mapper`, `MapReduceBase`, `OutputCollector`, `Reporter`, `JobConf`), `Tool`, `Progressable`, and filesystem permission exceptions.
- External dependencies include Apache Commons Logging, Apache Commons CLI, Ant `Task`, and JAAS `LoginException`.
- `SocketOutputStream`, `Shell`, `DataChecksum`, `LineReader`, `GenericOptionsParser`, `Progressable`, and `ReflectionUtils` are broad integration utilities used across HDFS, MapReduce, and command-line tools.
- The record compiler generated classes connect `.jr`/record schema parsing to generated `Record` subclasses and the `RecordInput`/`RecordOutput` runtime.
- UGI and access-control classes connect configuration, IPC exception unwrapping, filesystem permission checks, and thread execution identity.
- DistCp, HadoopArchives, Logalyzer, RunJar, ProgramDriver, PlatformName, and PrintJarMainClass are command-line or job-driver entry points exposed to users and scripts.

## Risks

- This is a compatibility baseline. Removing or mis-editing method signatures, checked exceptions, visibility, abstract/final/static flags, or class inheritance can produce false JDiff reports and hide or invent API incompatibilities.
- The chunk begins and ends mid-context: it starts after the `SocketInputStream` class body has already begun and ends inside `StringUtils`. The final per-file report must merge adjacent chunks before making whole-file claims.
- Socket timeout APIs are sensitive to Java channel blocking mode. The documentation explicitly warns that standard socket streams can fail after the channel is made non-blocking.
- Record serialization APIs define stable wire-format behavior. Changes to variable-length integer encoding, buffer copy/direct semantics, collection indexing, or tagged record boundaries risk breaking old serialized data and generated classes.
- Generated parser classes expose many public mutable fields from JavaCC. Although awkward, they are part of the baseline and may be referenced by downstream code.
- UGI persistence as comma-separated strings and one-UGI-per-user caching can create compatibility and security-sensitive behavior. Misdocumenting or changing this API affects configuration, identity propagation, and IPC/security integration.
- Tool and utility APIs are widely used by command-line scripts and jobs. `GenericOptionsParser`, `Shell`, `RunJar`, `ProgramDriver`, and `Progressable` are especially exposed to application code.
- `DataChecksum`, `LineReader`, sorting interfaces, and `ReflectionUtils` are low-level utilities. Their signatures and documented edge cases, such as empty-list behavior in `GenericsUtil.toArray(List<T>)`, can affect many callers.

## Test and Validation Signals

Validation for this chunk should focus on API-baseline and downstream compatibility:

- Run the repository's JDiff or API comparison task against `hadoop_0.19.1.xml` and a generated current API XML to verify this baseline parses cleanly and reports expected deltas.
- XML well-formedness checks should cover package/class nesting across the adjacent chunk boundaries, because this slice starts and ends in partial contexts.
- Compile downstream Hadoop 0.19.x-era code or compatibility tests that use `SocketOutputStream`, record I/O, generated record compiler classes, UGI, DistCp, HadoopArchives, `GenericOptionsParser`, `DataChecksum`, `Shell`, and `ReflectionUtils`.
- Serialization compatibility tests should round-trip records through binary, CSV, and XML record input/output and verify `Buffer`, variable-length int/long, and raw `RecordComparator` behavior.
- Security tests should cover UGI read/write, configuration save/read, login fallback to Unix, current-thread UGI propagation, and access-control exception unwrapping.
- Command-line integration tests should exercise DistCp, HadoopArchives, Logalyzer, RunJar, ProgramDriver, generic option parsing, libjars/files/archives parsing, and shell command execution behavior.
- Utility tests should cover checksum header/value creation and comparison, hosts-file refresh, line reading with maximum length/bytes, indexed sorter progress callbacks, priority queue fixed-size behavior, process-tree PID-file and `/proc` availability handling, servlet percentage graph helpers, and string formatting helpers visible in this chunk.

### subset-b-007302: lines 43513-44195

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 43513-44195

## Chunk Scope

This chunk is the tail of the Hadoop 0.19.1 JDiff API XML for `org.apache.hadoop.util`. It starts in the middle of `StringUtils`, covers the nested `StringUtils.TraditionalBinaryPrefix` enum, then documents `Tool`, `ToolRunner`, `UTF8ByteArrayUtils`, `VersionInfo`, and `XMLUtils` before closing the package and API document.

Because this source is generated API XML rather than implementation source, control flow, state, and persistence behavior are inferred from public signatures, modifiers, checked exceptions, and embedded Javadoc.

## Purpose

The chunk captures utility APIs used across Hadoop common and MapReduce applications:

- string and byte formatting/parsing helpers in `StringUtils`;
- command-line application integration through `Tool` and `ToolRunner`;
- byte-level search helpers for UTF-8 encoded records;
- build/version metadata access through `VersionInfo`;
- a simple XSLT transform helper in `XMLUtils`.

As a compatibility artifact, this section is useful for tracking public method overloads, nested enum shape, field visibility, static utility contracts, checked exceptions, and documentation wording in the Hadoop 0.19.1 public API.

## Important APIs and Types

### `org.apache.hadoop.util.StringUtils` tail

The visible part of `StringUtils` is a static utility surface for presentation, conversion, escaping, and logging support. The chunk begins after earlier formatting helpers and includes:

- `byteToHexString(byte[], int, int)` and `byteToHexString(byte[])`, converting byte ranges or entire arrays to hexadecimal text.
- `hexStringToByte(String)`, converting a hex string back to a byte array of size `hex.length()/2`.
- `uriToString(URI[])`, `stringToURI(String[])`, and `stringToPath(String[])`, bridging command-line/configuration string arrays with `java.net.URI` and Hadoop `Path` values.
- `formatTimeDiff(long finishTime, long startTime)`, `formatTime(long timeDiff)`, and `getFormattedTimeWithDiff(DateFormat, long finishTime, long startTime)`, formatting elapsed time and optionally appending a finish-start delta.
- `getStrings(String)` and `getStringCollection(String)`, splitting comma-separated values into arrays or `Collection<String>`.
- `split(String)` and `split(String, char escapeChar, char separator)`, splitting strings while respecting escaped separators.
- `findNext(String, char separator, char escapeChar, int start, StringBuilder split)`, the lower-level scanner used to find an unescaped separator and return the extracted segment through a mutable `StringBuilder`.
- `escapeString` overloads for default comma escaping, escaping a single character, or escaping an array of characters.
- `unEscapeString` overloads matching the escaping APIs.
- `getHostname()`, returning a hostname without propagating exceptions.
- `startupShutdownMessage(Class<?>, String[], Log)`, logging startup and shutdown messages for server classes.
- `escapeHTML(String)`, escaping HTML-special characters for display.

Public constants in this slice are `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`. These constants define the default delimiter and escape syntax for the string splitting/escaping helpers.

### `StringUtils.TraditionalBinaryPrefix`

`TraditionalBinaryPrefix` is a public static final enum nested under `StringUtils`. It represents binary prefixes such as kilo, mega, through exa, with case-insensitive symbols and 64-bit integer values.

Visible APIs include:

- compiler-generated enum methods `values()` and `valueOf(String)`;
- `valueOf(char symbol)`, resolving a prefix by symbol;
- `string2long(String)`, trimming and parsing numeric strings with optional traditional binary suffixes.

The enum exposes public final instance fields `value` (`long`) and `symbol` (`char`). Documentation examples show `-1230k` becoming `-1230 * 1024` and `891g` becoming `891 * 1024^3`.

### `org.apache.hadoop.util.Tool`

`Tool` is a public interface extending `org.apache.hadoop.conf.Configurable`. Its single command API is:

- `run(String[] args) throws Exception`, returning a process-style exit code.

The interface documentation defines the standard Hadoop command-line application pattern: application-specific tools should delegate generic Hadoop option parsing to `ToolRunner`, then process their own remaining arguments using the `Configuration` installed on the tool.

The embedded example shows a `Configured implements Tool` application building a `JobConf`, setting input/output paths and mapper/reducer classes, then invoking `JobClient.runJob(job)`. The XML does not expose `JobConf` methods here, but the docs make this interface a MapReduce application integration point.

### `org.apache.hadoop.util.ToolRunner`

`ToolRunner` is a public utility class with a public constructor and static helpers:

- `run(Configuration conf, Tool tool, String[] args) throws Exception`, parsing generic options with the supplied or newly created `Configuration`, setting the possibly modified configuration on the `Tool`, and delegating to `Tool.run`.
- `run(Tool tool, String[] args) throws Exception`, equivalent to `run(tool.getConf(), tool, args)`.
- `printGenericCommandUsage(PrintStream out)`, printing generic Hadoop command-line arguments and usage information.

The class documentation ties `ToolRunner` directly to `GenericOptionsParser`, which handles generic Hadoop options while preserving application-specific arguments for the tool.

### `org.apache.hadoop.util.UTF8ByteArrayUtils`

`UTF8ByteArrayUtils` is a public byte-search utility class with a public constructor and static methods operating on byte arrays that contain UTF-8 encoded strings:

- `findByte(byte[] utf, int start, int end, byte b)`, returning the first occurrence of a byte in a bounded range, or `-1`.
- `findBytes(byte[] utf, int start, int end, byte[] b)`, returning the first occurrence of a byte sequence, or `-1`.
- `findNthByte(byte[] utf, int start, int length, byte b, int n)`, returning the position of the nth occurrence in a bounded region, or `-1`.
- `findNthByte(byte[] utf, byte b, int n)`, a whole-array convenience overload.

These APIs are byte-oriented, so callers are expected to search for delimiter bytes or byte sequences that are meaningful in the encoded representation.

### `org.apache.hadoop.util.VersionInfo`

`VersionInfo` is a public utility class for build metadata. It exposes:

- `getVersion()`, returning the Hadoop version string.
- `getRevision()`, returning the Subversion revision for the root directory.
- `getDate()`, returning the build date.
- `getUser()`, returning the build user.
- `getUrl()`, returning the Subversion URL for the root Hadoop directory.
- `getBuildVersion()`, combining version, revision, user, and date.
- `main(String[] args)`, presumably printing version/build details for command-line use.

The class documentation states that it finds package info and `HadoopVersionAnnotation` information.

### `org.apache.hadoop.util.XMLUtils`

`XMLUtils` is a public class with a simple XSLT wrapper:

- `transform(InputStream styleSheet, InputStream xml, Writer out) throws TransformerConfigurationException, TransformerException`.

The method takes a stylesheet stream, an XML input stream, and a writer for transformed output. It integrates with the standard `javax.xml.transform` exception model.

## Control Flow and Behavioral Contracts

Most behavior is utility-level and stateless:

- `StringUtils` conversion methods flow from input arrays/strings into formatted strings, parsed bytes, `URI[]`, or `Path[]`.
- Escaping flow uses `escapeString` before storage or serialization of comma-separated data, then `split` and `unEscapeString` to recover logical tokens. `findNext` is the lower-level scanning primitive that ignores escaped separators and passes the token back through a `StringBuilder`.
- Time formatting flow computes a finish-start delta through `formatTimeDiff`, formats raw deltas through `formatTime`, and combines date formatting with optional elapsed time through `getFormattedTimeWithDiff`. Documentation says `getFormattedTimeWithDiff` returns an empty string when finish time is zero and omits the delta when start time is zero.
- `TraditionalBinaryPrefix.string2long` trims input, checks for a suffix symbol, resolves that suffix through `valueOf(char)`, parses the numeric portion, and multiplies by the prefix value.
- Hadoop CLI execution flows through `ToolRunner.run`: construct or reuse a `Configuration`, parse generic options with `GenericOptionsParser`, set the resulting configuration on the `Tool`, then invoke `Tool.run` with remaining command-specific arguments.
- `UTF8ByteArrayUtils` methods scan byte arrays linearly for a target byte, byte sequence, or nth occurrence.
- `VersionInfo` reads build/package annotation metadata through static accessors and exposes the same information through `main`.
- `XMLUtils.transform` builds or uses a transformer from the stylesheet and applies it to the XML input, writing transformed text to the supplied `Writer`.

## State and Persistence Behavior

This chunk exposes little mutable object state:

- `StringUtils` is effectively stateless except for public static delimiter constants and temporary parsing/formatting results.
- `TraditionalBinaryPrefix` enum instances carry immutable public final `value` and `symbol` fields.
- `Tool` instances are stateful through the inherited `Configurable` contract: `ToolRunner` mutates the tool by installing the parsed `Configuration` before invoking `run`.
- `UTF8ByteArrayUtils` methods do not persist state; they return offsets into caller-owned byte arrays.
- `VersionInfo` exposes build metadata embedded in the Hadoop artifact/package annotations. That metadata is persisted at build/package time rather than by this runtime API.
- `XMLUtils.transform` does not define persistence itself, but it streams transformed XML into caller-provided output.

Caller-owned mutable objects matter in this API surface: `StringBuilder` in `findNext`, byte arrays in UTF-8 search methods, `Configuration` inside `ToolRunner`, and `Writer` output in `XMLUtils`.

## Dependencies and Integration Points

Visible dependencies include:

- Java core types: `String`, arrays, `StringBuilder`, `Collection`, `DateFormat`, `PrintStream`, `InputStream`, `Writer`, `URI`, and checked exceptions.
- Hadoop core types: `org.apache.hadoop.fs.Path`, `org.apache.hadoop.conf.Configuration`, `org.apache.hadoop.conf.Configurable`, `GenericOptionsParser`, and `ToolRunner`.
- Logging: `org.apache.commons.logging.Log` for `startupShutdownMessage`.
- XML transformation: `javax.xml.transform.TransformerConfigurationException` and `TransformerException`.
- Build metadata: `HadoopVersionAnnotation` and Java package information are referenced by `VersionInfo` documentation.

Integration is centered on cross-cutting utilities:

- `StringUtils` supports configuration parsing, command-line display, web UI escaping, logging output, and byte/string conversions used by many Hadoop components.
- `Tool` and `ToolRunner` provide the public CLI contract used by MapReduce jobs and administrative commands.
- `UTF8ByteArrayUtils` is suitable for text input parsing and delimiter detection without materializing Java `String` objects.
- `VersionInfo` is used by command-line tools, logs, diagnostics, and compatibility reporting.
- `XMLUtils` supports documentation, reports, or configuration-style XML transformations.

## Risks and Edge Cases

- This XML does not contain method bodies, so exact validation behavior, exception paths, null handling, synchronization, and performance characteristics must be confirmed from implementation source if needed.
- The chunk starts mid-`StringUtils`; final synthesis needs the preceding chunk to include earlier methods such as human-readable integer and percent formatting.
- `hexStringToByte(String)` implies output size `hex.length()/2`; odd-length strings or invalid hex characters are edge cases not specified here.
- Comma splitting and escaping are easy to misuse if callers mix escaped and unescaped values or pass a different separator/escape character across encode and decode paths.
- `findNext` mutates a caller-provided `StringBuilder`, so stale content or reuse without clearing could be an implementation concern depending on method behavior.
- `getFormattedTimeWithDiff` has special sentinel handling for zero finish/start times; tests should distinguish zero from valid epoch timestamps if those can appear.
- `TraditionalBinaryPrefix.string2long` can overflow `long` when large numeric values are combined with large suffixes; behavior is not specified in the XML.
- `TraditionalBinaryPrefix` symbols are documented as case-insensitive, so callers should not rely on preserving suffix case.
- `ToolRunner.run(Tool, String[])` depends on `tool.getConf()`; tools with null configurations rely on the three-argument overload's null-handling contract.
- `Tool.run` throws generic `Exception`, so command launchers must preserve exit-code semantics while handling broad failures.
- `UTF8ByteArrayUtils` searches bytes, not Unicode code points; it is appropriate for ASCII delimiters in UTF-8 but not for arbitrary character-level searching.
- `VersionInfo` references Subversion metadata, which reflects Hadoop's historical build system and may be absent or differently represented in later builds.
- `XMLUtils.transform` leaves stream and writer ownership unclear in the signature docs; callers should manage close/flush behavior explicitly.

## Test Signals

Useful tests inferred from this API slice include:

- `StringUtils.byteToHexString` and `hexStringToByte` round trips for empty arrays, full arrays, subranges, uppercase/lowercase input, odd-length input, and invalid characters.
- `uriToString`, `stringToURI`, and `stringToPath` tests for empty arrays, null-like entries if supported by implementation, relative paths, schemes, authorities, and malformed URI strings.
- `formatTime`, `formatTimeDiff`, and `getFormattedTimeWithDiff` tests for positive, zero, and negative deltas; zero finish time; zero start time; and DateFormat output.
- `getStrings`, `getStringCollection`, `split`, `escapeString`, `unEscapeString`, and `findNext` tests for commas, escaped commas, escape characters themselves, multiple separators, leading/trailing empty tokens, and custom separator/escape characters.
- `escapeHTML` tests for HTML special characters such as `<`, `>`, `&`, quotes, and already-escaped input.
- `getHostname` tests or diagnostics confirming it returns a stable non-throwing value under normal and hostname-resolution failure conditions.
- `startupShutdownMessage` tests with a test `Log` implementation to confirm startup arguments, hostname/build info if included by implementation, and shutdown-hook behavior.
- `TraditionalBinaryPrefix.valueOf(char)` and `string2long` tests for all supported suffixes, case insensitivity, no suffix, whitespace trimming, negative values, invalid suffixes, and overflow boundaries.
- `ToolRunner.run` tests with a dummy `Tool` verifying generic option parsing, configuration injection, remaining application arguments, null configuration handling, returned exit code propagation, and exception propagation.
- `printGenericCommandUsage` tests that usage text is emitted to the supplied `PrintStream`.
- `UTF8ByteArrayUtils` tests for first/nth byte searches, byte sequence searches, start/end boundaries, missing values, overlapping byte sequences, zero-length target arrays if implementation accepts them, and multibyte UTF-8 content with ASCII delimiters.
- `VersionInfo` tests or smoke checks that version, revision, date, user, URL, build version, and `main` produce non-null diagnostic output in packaged builds.
- `XMLUtils.transform` tests using a small stylesheet/XML pair, invalid stylesheet handling, invalid XML handling, and writer flush/content assertions.

## Chunk Boundary Notes

The previous chunk is needed to complete the `StringUtils` class summary because this range begins at `byteToHexString(byte[])` after earlier formatting methods. This chunk closes `org.apache.hadoop.util` and the whole `hadoop_0.19.1.xml` API document, so no following chunk is needed for these specific classes.
