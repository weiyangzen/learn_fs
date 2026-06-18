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
