# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007329`: lines 1-6096, `Docs/researches/chunks/subset-b-007329_research.md`
- `subset-b-007330`: lines 6097-12316, `Docs/researches/chunks/subset-b-007330_research.md`
- `subset-b-007331`: lines 12317-18734, `Docs/researches/chunks/subset-b-007331_research.md`
- `subset-b-007332`: lines 18735-25047, `Docs/researches/chunks/subset-b-007332_research.md`
- `subset-b-007333`: lines 25048-31378, `Docs/researches/chunks/subset-b-007333_research.md`
- `subset-b-007334`: lines 31379-37729, `Docs/researches/chunks/subset-b-007334_research.md`
- `subset-b-007335`: lines 37730-43882, `Docs/researches/chunks/subset-b-007335_research.md`
- `subset-b-007336`: lines 43883-50039, `Docs/researches/chunks/subset-b-007336_research.md`
- `subset-b-007337`: lines 50040-53959, `Docs/researches/chunks/subset-b-007337_research.md`

## Chunk Research

### subset-b-007329: lines 1-6096

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 1-6096

## Scope

This chunk is the opening slice of the JDiff API XML for Hadoop 0.20.2, generated on 2010-03-01 by the JDiff Javadoc doclet. It is not executable implementation code; it is a compatibility snapshot of exported packages, types, inheritance, implemented interfaces, constructors, methods, fields, visibility flags, synchronization flags, deprecation text, declared exceptions, and embedded Javadocs.

The range covers:

- `org.apache.hadoop.HadoopVersionAnnotation`.
- `org.apache.hadoop.conf` configuration contracts.
- `org.apache.hadoop.filecache.DistributedCache`.
- Most of the early `org.apache.hadoop.fs` public API surface, from block/file metadata and filesystem abstractions through local/checksummed/HAR filesystems, stream wrappers, checksum streams, filesystem utilities, `FsShell`, URL handlers, `Path`, `PathFilter`, and the start of `PositionedReadable`.

The chunk ends at line 6096 inside the `PositionedReadable.readFully` declaration. The remaining methods and documentation for `PositionedReadable` continue in the next chunk and should be reconciled there.

## Purpose

The file as a whole preserves Hadoop 0.20.2 API metadata for release-to-release compatibility comparison. This chunk captures the foundation that later HDFS, MapReduce, and tool APIs depend on: configuration loading, distributed cache localization, filesystem identity and dispatch, path representation, metadata structures, data streams, checksums, local disk allocation, and archive filesystems.

The `org.apache.hadoop.conf` portion defines how Hadoop components receive, clone, reload, serialize, and query runtime configuration. It documents the default resource chain (`core-default.xml`, then `core-site.xml`), final parameter semantics, and variable expansion against configuration and Java system properties.

The `org.apache.hadoop.filecache` portion exposes the MapReduce distributed cache API used to localize read-only files, archives, and jars onto task nodes. It records cache URIs and timestamps in configuration, supports symlink creation, and integrates localized resources with task classpaths.

The `org.apache.hadoop.fs` portion defines the common filesystem contract that lets user code address local filesystems, HDFS-style distributed filesystems, checksummed wrappers, in-memory filesystems, Hadoop Archives, and URL handlers through a common `Path`/`FileSystem` API.

## Important APIs, Types, and Functions

### Version and Configuration

- `HadoopVersionAnnotation` is a package annotation interface exposing `version()`, `user()`, `date()`, `url()`, and `revision()`. It captures build provenance such as version string, builder user, build date, repository URL, and Subversion revision.
- `Configurable` is the common interface for objects that accept a `Configuration`, with `setConf(Configuration)` and `getConf()`.
- `Configuration` implements `Iterable` and `Writable`. Constructors support default loading, explicit `loadDefaults`, and cloning from another configuration.
- `Configuration.addDefaultResource(String)` is static and synchronized; resources are loaded in add order from the classpath.
- `Configuration.addResource(...)` overloads accept resource name, `URL`, local `Path`, or `InputStream`. Later resources override earlier values unless earlier values are marked final.
- `reloadConfiguration()` is synchronized and clears loaded resource-derived values and final parameters so resources will be re-read; values added through setters overlay resource values.
- `get`, `getRaw`, `set`, `setIfUnset`, `getInt`, `setInt`, `getLong`, `setLong`, `getFloat`, `setFloat`, `getBoolean`, `setBoolean`, `setBooleanIfUnset`, `getStringCollection`, `getStrings`, and `setStrings` define the main scalar and comma-list configuration accessors.
- `getRange` returns `Configuration.IntegerRanges`, a positive integer range parser for expressions such as `2-3,5,7-`.
- `getClassByName`, `getClasses`, `getClass`, and `setClass` are the class-loading and interface-checking hooks used by pluggable Hadoop services.
- `getLocalPath` and `getFile` pick a local directory from a configured directory list by hashing a relative path and create the directory if absent.
- `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader` expose classpath/configuration resources.
- `size`, `clear`, `iterator`, `writeXml`, `readFields`, and `write` define configuration inspection and persistence.
- `getClassLoader` and `setClassLoader` control class loading for configured classes; `setQuietMode` affects diagnostic logging; `main` prints non-default properties for debugging.
- `Configured` is a small base class implementing `Configurable`.

### Distributed Cache

- `DistributedCache.getLocalCache(...)` has three public overloads. It localizes a cache URI into a base directory, optionally validates a supplied `FileStatus`, optionally honors symlink configuration, verifies the recorded modification timestamp, and returns either the localized file path or the unpacked archive directory.
- `releaseCache(URI, Configuration)` releases a localized cache after use; `purgeCache(Configuration)` clears all cache backing files and is documented as appropriate only for server reinitialization.
- `getTimestamp(Configuration, URI)` reads the HDFS modification time used to detect cache mutation during a job.
- `setCacheArchives`, `setCacheFiles`, `addCacheArchive`, and `addCacheFile` store cache URIs into configuration; matching getters return configured URI arrays.
- `setArchiveTimestamps`, `setFileTimestamps`, `getArchiveTimestamps`, and `getFileTimestamps` store and read timestamp arrays whose order must match the archive/file URI order.
- `setLocalArchives`, `setLocalFiles`, `getLocalCacheArchives`, and `getLocalCacheFiles` record localized paths in configuration.
- `addFileToClassPath`, `getFileClassPaths`, `addArchiveToClassPath`, and `getArchiveClassPaths` combine cache localization with task classpath mutation.
- `createSymlink`, `getSymlink`, `createAllSymlink`, and `checkURIs` implement task working-directory symlink behavior. `checkURIs` requires fragments and rejects fragment-name conflicts.

### Filesystem Metadata and Utility Types

- `BlockLocation` implements `Writable` and stores block hostnames, host:port names, network topology paths, file offset, and length. It provides setters/getters plus `write`, `readFields`, and `toString`.
- `ContentSummary` implements `Writable`-style persistence for directory/file content metrics: content length, directory count, file count, namespace quota, space consumed, and space quota. `getHeader(boolean)` and `toString(boolean)` format shell output with or without quota columns.
- `FileChecksum` is an abstract `Writable` for checksum identity and bytes. It requires `getAlgorithmName`, `getLength`, and `getBytes`; `equals` compares both algorithm and value.
- `MD5MD5CRC32FileChecksum` concretizes `FileChecksum` as "MD5 of MD5 of CRC32", provides `readFields`/`write`, XML serialization via `XMLOutputter`, `valueOf(Attributes)`, `toString`, and public constant `LENGTH`.
- `FileStatus` implements `Writable` and `Comparable`. It represents client-side file metadata: length, directory flag, replication, block size, modification/access times, permission, owner, group, and `Path`. Equality, ordering, and hashing are path-based.
- `ChecksumException` extends `IOException` and records a corruption position via `getPos()`.
- `FSError` extends `Error` for unexpected native filesystem disk errors.

### FileSystem Core

- `FileSystem` is the abstract base class for local and distributed filesystems. It extends `Configured` and implements `Closeable`.
- Static filesystem discovery methods include `get(Configuration)`, `get(URI, Configuration)`, `getLocal(Configuration)`, deprecated `getNamed(String, Configuration)`, `getDefaultUri`, `setDefaultUri`, `closeAll`, and synchronized statistics accessors.
- `initialize(URI, Configuration)` is called after construction. `getUri()` is abstract and identifies the filesystem by scheme and authority; deprecated `getName()` maps to URI identity.
- Static `create(FileSystem, Path, FsPermission)` and `mkdirs(FileSystem, Path, FsPermission)` create with exact permissions by issuing permission-setting operations after creation rather than relying on umask.
- Abstract or central filesystem operations include `open`, many `create` overloads, `append`, `rename`, `delete(Path, boolean)`, `listStatus`, `mkdirs(Path, FsPermission)`, `setWorkingDirectory`, `getWorkingDirectory`, and `getFileStatus`.
- Convenience operations include `createNewFile`, `deleteOnExit`, `exists`, `isFile`, deprecated `isDirectory`, deprecated `getLength`, deprecated `getBlockSize`, `getContentSummary`, `globStatus`, `copyFromLocalFile`, `moveFromLocalFile`, `copyToLocalFile`, `moveToLocalFile`, `startLocalOutput`, `completeLocalOutput`, `getUsed`, `getDefaultBlockSize`, `getDefaultReplication`, `getFileChecksum`, `setVerifyChecksum`, `setPermission`, `setOwner`, and `setTimes`.
- `getFileBlockLocations(FileStatus, long, long)` returns locality data and defaults to `localhost` for local-style filesystems.
- `globStatus` documents Hadoop glob grammar: `?`, `*`, character classes/ranges, negated classes, escaping, and nested brace alternatives.
- `FileSystem.Statistics` is a public static final nested class tracking bytes read/written per URI scheme, with incrementers, getters, `reset`, `getScheme`, and `toString`.

### Filesystem Wrappers and Implementations

- `FilterFileSystem` extends `FileSystem` and delegates operations to protected `fs`. Its methods mirror `FileSystem` and pass through initialization, URI/path qualification, block locations, open/create/append, replication, rename, delete, status/listing, working directory, mkdirs, local copies, output staging, checksum, owner, permissions, and close.
- `ChecksumFileSystem` extends `FilterFileSystem` to pair data files with checksum files. It exposes the raw filesystem, checksum path calculation, checksum-file detection, checksum length calculation, bytes-per-checksum, checksum verification toggling, checksum-aware open/create/append, copy options including `copyCrc`, and `reportChecksumFailure`.
- `LocalFileSystem` extends `ChecksumFileSystem`, exposes `getRaw()`, maps `Path` to `java.io.File`, overrides local copy behavior, and moves corrupt data/checksum files to a bad-file directory on checksum failure.
- `HarFileSystem` extends `FilterFileSystem` and represents Hadoop Archive (`har`) files. Its URI form is `har://underlyingfsscheme-host:port/archivepath` or `har:///archivepath`. It reads `_masterindex`, `_index`, and `part-*` files, provides `getHarVersion`, archive-top working/home directory, URI qualification, block locations for archive segments, hash calculation, status/listing from index files, and read-only `open` that fakes EOF for archive members. Creation, mutation, mkdir, local-output, owner, and permission operations are documented as not implemented.
- `InMemoryFileSystem` extends `ChecksumFileSystem` for `ramfs://` paths. It assumes file lengths are known before creation, requires `reserveSpaceWithCheckSum(Path,long)` to reserve data and checksum memory together, and exposes file listing/count and capacity usage via filters.
- `LocalDirAllocator` implements per-context round-robin local disk selection over configured directory lists. It exposes `getLocalPathForWrite` with and without known size, `getLocalPathToRead`, `createTmpFileForWrite`, `isContextValid`, and `ifExists`.

### Streams and Checksums

- `FSInputStream` is an abstract seekable input stream implementing `Seekable` and `PositionedReadable`. It requires `seek`, `getPos`, and `seekToNewSource`, and supplies positioned `read` and `readFully` helpers.
- `BufferedFSInputStream` wraps an `FSInputStream` in `BufferedInputStream` while preserving `Seekable` and `PositionedReadable` operations.
- `FSDataInputStream` wraps an input stream in `DataInputStream`, exposes seek, position, positioned read/readFully, and `seekToNewSource`.
- `FSDataOutputStream` wraps output in `DataOutputStream`, implements `Syncable`, tracks current position, optionally updates `FileSystem.Statistics`, exposes the wrapped stream, and supports `sync`.
- `FSInputChecker` is an abstract checksum-verifying `FSInputStream`. Subclasses provide `readChunk` and `getChunkPosition`; the base class verifies chunks on reads, supports retries, exposes `checksum2long`, synchronized read/seek/skip/available/getPos, disables mark/reset, and stores the protected `file` path plus public `LOG`.
- `FSOutputSummer` is an abstract checksum-generating `OutputStream`. Subclasses implement `writeChunk`; the base class buffers data into checksum chunks, writes checksums, exposes `flushBuffer`, `convertToByteStream`, and `resetChecksumChunk`.

### Filesystem Utilities, Shell, URL Handling, and Paths

- `DF` and `DU` extend `org.apache.hadoop.util.Shell` and wrap native Unix `df` and `du` commands. `DF` reports filesystem, capacity, used, available, percent used, mount, and directory path; `DU` maintains disk usage with increment/decrement helpers, refresh thread start/shutdown, and shell parsing.
- `FileUtil` is a static utility collection for converting `FileStatus[]` to `Path[]`, recursive local deletion, deprecated recursive `FileSystem` deletion, filesystem-to-filesystem and local-to/from-filesystem copies, directory merge copy, shell path conversion, local disk usage, zip/tar extraction, symlink creation, chmod, local temp file creation, and atomic-ish file replacement.
- `FileUtil.HardLink` creates hard links and retrieves link counts on Unix, Cygwin, and Windows XP.
- `FsShell` extends `Configured` and implements `Tool` for command-line `FileSystem` access. It initializes an `fs`, exposes the current trash directory, deprecated byte/decimal formatting helpers, `run`, `close`, `main`, and public/protected date formatters.
- `FsUrlStreamHandlerFactory` implements `URLStreamHandlerFactory`, returning handlers that route URL connections through `FileSystem` after checking that the requested scheme has a known implementation.
- `Path` implements `Comparable` and represents filesystem paths as URI-like strings with Hadoop normalization. Constructors support parent/child resolution and scheme/authority/path components. Methods expose `toUri`, owning `FileSystem`, absolute check, name, parent, suffix, string form, equality/hash/order, depth, and qualification against a filesystem. Public constants include `SEPARATOR`, `SEPARATOR_CHAR`, and `CUR_DIR`.
- `PathFilter` is a single-method interface, `accept(Path)`, used by list/glob/local allocation APIs.
- `PositionedReadable` begins at the chunk boundary. Its `read(long position, byte[] buffer, int offset, int length)` contract says positioned reads do not change the current file offset and are thread-safe; `readFully` continues in the next chunk.

## Control Flow

Configuration flow begins with constructor selection and default resource loading. Default resources are registered globally by `addDefaultResource`; instances load default resources unless constructed with `loadDefaults=false`. Additional resources are appended per instance, and value access triggers parsing, final-parameter enforcement, and variable expansion. `reloadConfiguration` clears loaded resource state and forces the next access to re-read resources while preserving setter overlays.

Distributed cache setup flows from job configuration mutation to task localization. Applications call `setCacheFiles`, `addCacheFile`, `addCacheArchive`, or classpath helpers before job submission. The framework records remote URIs and modification timestamps. At task launch, `getLocalCache` validates timestamps, copies a remote file from the configured `FileSystem` if a valid local copy is absent, unpacks supported archives, optionally creates symlinks in the task working directory, and returns localized `Path`s for use by tasks. `releaseCache` decrements cache usage; `purgeCache` wipes all cache state.

Filesystem dispatch starts with `Path.getFileSystem(conf)` or `FileSystem.get(conf/uri, conf)`. The URI scheme maps to a configured implementation class such as `fs.<scheme>.class`; the full URI is passed to `initialize`. Operations then flow through abstract `FileSystem` methods or through wrappers such as `FilterFileSystem`, `ChecksumFileSystem`, `LocalFileSystem`, and `HarFileSystem`.

Read flow typically calls `FileSystem.open(Path, bufferSize)`, returning `FSDataInputStream`. If checksums are enabled, a `ChecksumFileSystem` can wrap raw data with `FSInputChecker`, which repeatedly calls subclass `readChunk`, verifies checksum bytes, retries or reports checksum failure, and updates stream position. Positioned reads flow through `PositionedReadable` without changing current offset.

Write flow calls one of the many `FileSystem.create` overloads or `append`, returning `FSDataOutputStream`. Checksum-aware implementations use `FSOutputSummer` to accumulate data into checksum chunks, compute checksum bytes, and write data plus checksum output. Static exact-permission helpers perform creation and then set permissions in a separate step.

Metadata flow centers on `FileStatus`, `BlockLocation`, `ContentSummary`, and `FileChecksum`. List/glob/status APIs return serializable metadata objects. Block-location APIs provide scheduler locality hints. Content summaries and shell tools render human-facing output.

Local utility flow includes shell-backed disk accounting (`DF`, `DU`), local directory allocation (`LocalDirAllocator`), file copying (`FileUtil.copy`), archive unpacking (`unZip`, `unTar`), and local hard/symbolic link creation. These methods bridge Java APIs to native commands and local disk state.

HAR flow is read-only: initialization identifies the underlying filesystem and archive root, index files map logical archive paths to `part-*` offsets and lengths, and `open` returns a stream bounded to the member's byte range. Mutating methods are declared but documented as unimplemented.

## State and Persistence Behavior

The XML itself persists release API metadata. Runtime state and persistence contracts visible in this chunk include:

- `Configuration` persists key/value settings through XML resources, Java setter overlays, final-parameter markers, `writeXml(OutputStream)`, and `Writable` `readFields`/`write`. Variable expansion makes returned values dependent on other configuration keys and Java system properties.
- `Configuration` owns mutable resource lists, final-parameter state, class loader state, quiet-mode state, and key/value maps. Static default resources affect all instances that load defaults.
- `DistributedCache` persists cache URI lists, localized path lists, timestamps, symlink flags, and classpath additions in `Configuration`. Localized files and unpacked archives persist on task nodes and are reference-counted/released through cache APIs.
- `BlockLocation`, `ContentSummary`, `FileStatus`, `FileChecksum`, and `MD5MD5CRC32FileChecksum` define durable binary or XML serialization forms via `Writable`, XML attributes, and string rendering.
- `FileSystem` instances are cached by scheme/authority/configuration, and `closeAll` releases cached instances. `deleteOnExit` queues paths to be deleted when the filesystem closes, including JVM shutdown cleanup.
- `FileSystem.Statistics` maintains process-local byte counters by filesystem scheme and class. The public `statistics` field on each filesystem links instances to global accounting.
- `ChecksumFileSystem`, `FSInputChecker`, and `FSOutputSummer` persist checksum side files or checksum bytes alongside data, and checksum failure handling can move bad local files out of reuse paths.
- `LocalDirAllocator` persists per-JVM allocator state by context string and keeps round-robin position across allocations for a configured directory list.
- `HarFileSystem` persists archive content as `_masterindex`, `_index`, and `part-*` files. Its `FileStatus` permissions reflect archive index files because per-member permissions are not persisted.
- `Path` string/URI form is a durable API contract. Equality, hash, ordering, qualification, depth, and parent/name behavior affect caches, map keys, globbing, file status ordering, and serialized paths.

## Dependencies and Integration Points

- Java platform dependencies include annotations, `Iterable`, `Closeable`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `Reader`, `URL`, `URI`, `URLStreamHandlerFactory`, `File`, `BufferedReader`, `SimpleDateFormat`, exceptions, native process execution, `Checksum`, SAX `Attributes`, and class loading.
- Hadoop IO dependencies include `Writable`, `MD5Hash`, `Syncable`, data streams, `RawComparator` indirectly through filesystem ordering, and checksum classes.
- Hadoop configuration is the central integration point for filesystem discovery, cache metadata, local directory lists, buffer sizes, class loaders, and tool configuration.
- Hadoop filesystem components integrate across `Path`, `FileSystem`, `FileStatus`, `BlockLocation`, `ContentSummary`, `PathFilter`, local/remote copy methods, URL stream handlers, and shell commands.
- Permissions integrate with `org.apache.hadoop.fs.permission.FsPermission`, owner/group metadata, chmod, exact-permission creation helpers, and read-only archive limitations.
- Progress and write APIs integrate with `org.apache.hadoop.util.Progressable` and `Tool`; shell and utility components integrate with `org.apache.hadoop.util.Shell`.
- Logging uses Apache Commons Logging in `FileSystem` and `FSInputChecker`.
- Distributed cache integrates with MapReduce task launch behavior and with filesystems capable of reading remote URIs such as HDFS and HTTP-like schemes.
- Archive support integrates with `java.util.zip`, tar/gzip command behavior or utilities, HAR index files, and underlying filesystems.

## Risks and Edge Cases

- JDiff XML lacks method bodies. Exact configuration key names, filesystem cache keying, checksum algorithms, native command construction, copy/delete recursion behavior, and error handling require implementation-source review.
- The chunk ends mid-interface at `PositionedReadable.readFully`; any final API document must merge the next chunk to avoid an incomplete interface description.
- Raw `java.lang.Class`, raw `Iterator`, raw `Collection`, and raw `Map` signatures reflect pre-generic public APIs. Compatibility checking must preserve erased signatures even if implementation source uses generics internally.
- Configuration final-parameter enforcement and variable expansion are order-sensitive. Cyclic variables, missing variables, malformed XML resources, duplicate keys, and reload behavior can produce subtle differences across versions.
- Static `addDefaultResource` has global impact and is synchronized, but callers can still create surprising process-wide configuration changes.
- `Configuration.getInt`, `getLong`, `getFloat`, and `getBoolean` return defaults on invalid values according to docs; tests must pin whether invalid values are logged, ignored, or fatal.
- `getLocalPath` and `LocalDirAllocator` choose among local disks. Hashing, round-robin state, disk-free checks, directory writability, and concurrent writers can lead to hotspots or races.
- Distributed cache correctness depends on stable URI fragments, timestamp order matching URI order, symlink configuration, archive extension detection, and immutability of remote cache files while jobs run.
- `purgeCache` is destructive and documented to make users lose files; accidental calls during active jobs are high risk.
- `BlockLocation` arrays may be null, empty, mismatched in length, or stale. Scheduler locality depends on consistent hosts/names/topology paths.
- `FileStatus` equality and comparison are path-based, not full metadata-based, so metadata changes do not affect equality.
- `FileSystem.create(FileSystem, Path, FsPermission)` exact-permission helper uses two operations; a crash or failure between create and setPermission can leave wrong permissions.
- `deleteOnExit` depends on filesystem close and JVM shutdown ordering. Long-running processes can accumulate paths or fail to delete if close does not occur cleanly.
- Deprecated methods such as `getName`, `getNamed`, `getBlockSize(Path)`, `getReplication(Path)`, `isDirectory`, and `getLength` still remain public compatibility obligations.
- `globStatus` has a rich grammar; escaping, nested braces, character ranges, nonexistent non-glob paths, and no-match glob paths all have distinct documented behavior.
- `FilterFileSystem` delegation must preserve semantics exactly; missed overrides can bypass wrapper behavior or expose the wrong underlying filesystem.
- `ChecksumFileSystem` must keep data files and checksum files in sync across create, append, rename, delete, local copy, and failure recovery. Partial writes or interrupted renames can leave orphaned checksum files.
- `FSInputChecker` allows seek/skip past EOF according to docs but must still report checksum errors for corrupted chunks. The interplay between retries, EOF, negative skip, and checksum verification is sensitive.
- `FSOutputSummer` direct-write optimization avoids data copies for full chunks; off-by-one bugs can corrupt checksum alignment.
- `DF`, `DU`, symlink, chmod, and hard-link utilities depend on OS-specific shell behavior, path quoting, locale/output formatting, and command availability.
- `FileUtil.fullyDelete` can return false after partial deletion, leaving caller cleanup incomplete. Recursive copy and merge operations risk partial outputs, overwrite races, and source deletion after partial failure.
- HAR is read-only but still exposes mutation-shaped methods. Callers may expect standard `FileSystem` behavior and receive unsupported/not-implemented failures.
- HAR file status does not persist original member permissions, so security or tooling code relying on member permissions can be misled.
- `InMemoryFileSystem` requires a priori size reservation. Missing or incorrect reservation can make ordinary `FileSystem` create flows fail despite the common API signature.
- `Path` URI normalization and qualification affect all filesystem routing. Windows paths, relative paths, empty authority, trailing slashes, `.` components, and suffix/parent handling need regression coverage.

## Test Signals

Useful validation for this chunk should include:

- JDiff/API compatibility checks for every public/protected package, class, interface, constructor, method, field, declared exception, deprecation marker, visibility, static/final/abstract/synchronized flag, and inheritance/interface relationship in lines 1-6096.
- `HadoopVersionAnnotation` reflection tests for all annotation elements and expected string return types.
- `Configuration` tests for constructor modes, default resource order, added resource precedence, final parameters, variable expansion from configuration and system properties, `getRaw`, all typed getters/setters including invalid values, string-list parsing, class loading and interface validation, resource lookup, reload, iterator/size/clear, class loader mutation, quiet mode, XML output, and `Writable` round trips.
- `Configuration.IntegerRanges` tests for singletons, closed ranges, open-ended ranges, commas, empty/malformed strings, `isIncluded`, and `toString`.
- `Configured` and `Configurable` tests for null and non-null configuration propagation.
- `DistributedCache` tests for URI set/add/get order, archive/file timestamp ordering, localized path storage, classpath entries, symlink enablement, URI fragment conflict detection, missing fragments, cache timestamp mismatch, archive unpacking for zip/jar/tar/tgz/tar.gz, cache release, and purge behavior.
- `BlockLocation`, `ContentSummary`, `FileStatus`, `FileChecksum`, and `MD5MD5CRC32FileChecksum` tests for constructor defaults, getters/setters, equality/order/hash, binary serialization round trips, XML serialization/parsing, null arrays, empty values, and formatted output.
- `FileSystem` tests for URI discovery by scheme, default URI get/set, initialization, cache close/closeAll, exact-permission create/mkdir helpers, open/create/append overload delegation, createNewFile existing-file behavior, rename/delete semantics, recursive delete, deleteOnExit processing, exists/isFile/status/listing, glob grammar, working directory resolution, local copy/move variants, start/complete local output, checksum defaults, owner/permission/time setters, statistics counters, and deprecated methods.
- `FilterFileSystem` tests that every delegated method calls the wrapped filesystem with unchanged arguments and propagates return values/exceptions.
- `ChecksumFileSystem` tests for checksum path naming, checksum length math, bytes-per-sum, verify toggling, create/open/append verification, data/checksum rename/delete consistency, local copy with and without CRC, and checksum failure reporting.
- `FSInputStream`, `BufferedFSInputStream`, `FSDataInputStream`, `FSInputChecker`, `FSDataOutputStream`, and `FSOutputSummer` tests for seek/position behavior, positioned reads not changing current offset, readFully EOF handling, seekToNewSource, statistics updates, sync propagation, checksum chunk boundaries, skip past EOF, negative skip, mark/reset behavior, retries, and corrupt-checksum exceptions.
- `DF` and `DU` tests for supported-platform parsing, command strings, refresh intervals, increment/decrement usage accounting, background thread start/shutdown, and malformed shell output.
- `FileUtil` tests for `stat2Paths`, recursive deletion with partial failures, all copy overloads including overwrite/deleteSource, copyMerge ordering and separator behavior, shell path conversion on Unix/Windows-like paths, local disk usage, unzip/untar extraction safety, symlink/chmod return codes, temp file creation/delete-on-exit, file replacement, hard-link creation, and link counts.
- `FsShell` tests for initialization, command dispatch return codes, trash directory lookup, close behavior, and deprecated formatting helper parity with `StringUtils`.
- `FsUrlStreamHandlerFactory` tests for known/unknown schemes, handler reuse, and URL opens routed through the configured `FileSystem`.
- `HarFileSystem` tests for URI forms, initialization cache behavior, archive version reading, index/master-index lookup, hash-range lookup, `getFileStatus`, `listStatus`, member open bounded to length/offset, block locations from underlying files, read-only mutation failures, and archive permission behavior.
- `InMemoryFileSystem` tests for `ramfs://` initialization, required reserve-before-create flow, checksum reservation, capacity limits, filtered file listing/count, and percent-used math.
- `LocalDirAllocator` tests for context uniqueness, configuration changes invalidating context state, round-robin allocation, known-size free-space checks, unknown-size writable checks, temp file creation, read lookup across configured dirs, missing path behavior, and disks becoming full/read-only mid-write.
- `Path` and `PathFilter` tests for all constructor combinations, URI conversion, scheme/authority/path preservation, absolute/relative paths, parent/name/root behavior, suffix, equality/hash/compare, depth, qualification, separator constants, path filtering in list/glob flows, and edge cases around empty strings, trailing slashes, and URI escaping.

### subset-b-007330: lines 6097-12316

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 6097-12316

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.20.2, not implementation source. It records compatibility metadata for packages, classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, visibility, flags, deprecation state, checked exceptions, parameters, return types, and embedded Javadoc contracts.

The range starts inside the tail of `org.apache.hadoop.fs.PositionedReadable`, covers local/FTP/KFS/S3 filesystem APIs, permission APIs, shell command helpers, the HTTP server facade, and a large part of `org.apache.hadoop.io`. It ends inside `org.apache.hadoop.io.SequenceFile.Reader.close()`, so the full `PositionedReadable` and `SequenceFile.Reader` surfaces require adjacent chunks during final reconciliation.

## Purpose and Major API Surface

The filesystem section documents Hadoop's 0.20.2 public storage abstraction and several concrete backends. The visible `PositionedReadable` methods define position-preserving `readFully(...)` contracts. `RawLocalFileSystem` extends `FileSystem` and exposes URI initialization, `Path` to `File` conversion, open/create/append, rename/delete/list/mkdirs, working and home directory handling, local output staging, file status, owner, permission, close, and string conversion. `Seekable` defines `seek`, `getPos`, and `seekToNewSource`; `Syncable` defines `sync`. `Trash` is a configured service for moving paths into per-user `.Trash/current`, checkpointing, expunging, returning an emptier `Runnable`, and running the emptier from `main`.

`org.apache.hadoop.fs.ftp` provides an FTP-backed `FileSystem`. `FTPFileSystem` exposes `initialize`, `open`, `create`, optional `append`, delete overloads, URI, listing/status, `mkdirs`, `rename`, working/home directories, and working-directory mutation. Public constants include `LOG`, `DEFAULT_BUFFER_SIZE`, and `DEFAULT_BLOCK_SIZE`. `FTPInputStream` wraps an `InputStream`, `FTPClient`, and `FileSystem.Statistics`; it implements `Seekable`-style position reporting, rejects or implements seek/new-source behavior through exposed methods, reads bytes and byte ranges, closes the FTP client path, and disables mark/reset. `FTPException` wraps FTP failures as runtime exceptions.

`org.apache.hadoop.fs.kfs.KosmosFileSystem` exposes the KFS backend: URI/init/name, working directory, mkdirs, directory/file predicates, list/status, append/create/open, rename/delete, length, replication, default replication/block size, set replication, lock/release, block locations, local copy helpers, and local output staging. This API is backend-neutral at the `FileSystem` level but relies on KFS-specific metadata servers and native/client libraries outside this XML.

`org.apache.hadoop.fs.permission` captures permission metadata. `AccessControlException` remains a public permission exception type. `FsAction` is an enum-like permission action lattice with `NONE`, `EXECUTE`, `WRITE`, `WRITE_EXECUTE`, `READ`, `READ_EXECUTE`, `READ_WRITE`, `ALL`, `SYMBOL`, and `implies`, `and`, `or`, and `not` operations. `FsPermission` implements `Writable`; it can be built from actions, shorts, copies, or symbolic strings, creates immutable instances, reads/writes itself, converts to/from shorts, applies and manages umasks, returns defaults, and exposes `UMASK_LABEL` plus `DEFAULT_UMASK`. `PermissionStatus` stores user, group, and `FsPermission`, supports immutable creation, umask application, `Writable` read/write, static read/write helpers, and string formatting.

The `org.apache.hadoop.fs.s3` package documents the older block-based S3 filesystem. `Block` holds block id and length. `FileSystemStore` is the storage SPI for version, inode, and block operations: initialize, store/retrieve/delete inode and block data, existence tests, shallow/deep path listing, purge for tests, and diagnostic dump. `INode` models file metadata with a file type and block array, exposes directory/file predicates, serialized length, serialize/deserialize helpers, `FILE_TYPES`, and `DIRECTORY_INODE`. `MigrationTool` is a `Tool`-style command that initializes and migrates S3 metadata. `S3Credentials` reads access and secret keys from URI/configuration. `S3Exception`, `S3FileSystemException`, and `VersionMismatchException` expose S3 failure modes. `S3FileSystem` itself covers URI/init/name, working directory, mkdirs, file predicate, list/status, create/open, unsupported append, rename/delete, and status construction; its docs note ignored permissions and S3-specific metadata behavior.

`org.apache.hadoop.fs.s3native.NativeS3FileSystem` is the native-object S3 backend. It has constructors with and without a `NativeFileSystemStore`, initialize, unsupported append, create, delete overloads, file status, URI, list, mkdirs, open, rename, working-directory setters/getters, default block size, and public `LOG`. Package docs distinguish it from block-based S3 by storing file data directly as S3 objects and using object markers/prefixes for directory inference.

`org.apache.hadoop.fs.shell` contains public shell command helpers. `Command` is a configured command base with argument storage, `getCommandName`, `run(Path)`, and `runAll()`. `CommandFormat` parses command options with min/max argument counts and exposes `getOpt`. `Count` implements a shell count command with `matches`, command name, `run(Path)`, and public `NAME`, `USAGE`, and `DESCRIPTION` strings.

`org.apache.hadoop.http` exposes a Jetty-backed HTTP server surface. `FilterContainer` defines `addFilter` and `addGlobalFilter`; `FilterInitializer` is the configured extension point that initializes filters. `HttpServer` wraps Jetty `Server`, `Connector`, and `WebAppContext`, with constructors over name/bind address/port/find-port and optional `Configuration`. It exposes listener creation, default apps and servlets, context registration, servlet and internal servlet registration, filter/global-filter definition and path mapping, attribute access, webapp path lookup, port/thread controls, SSL listener overloads, lifecycle `start`, `stop`, and `join`, plus protected/public fields for server state. `HttpServer.StackServlet` implements `doGet` for stack/thread diagnostic output.

The `org.apache.hadoop.io` section documents Hadoop's writable serialization stack and sorted-file containers. `AbstractMapWritable` maintains per-instance class-id mappings for map-like writables and integrates `Writable` with `Configurable`. `ArrayFile` is a dense long-indexed `MapFile`, with `Reader` seek/next/key/get and `Writer` constructors plus append. `ArrayWritable` persists homogeneous `Writable[]` values and has a string-array constructor. `BinaryComparable` provides byte-array comparison, equality, and hash behavior for byte-backed values.

`BloomMapFile` extends `MapFile` with Bloom filter acceleration. Static members include `BLOOM_FILE_NAME`, `HASH_COUNT`, and `delete`. `Reader` can check `probablyHasKey`, perform `get`, and expose the filter; false positives remain possible. `Writer` has many constructors over key/value classes or comparators, compression type/codec, and progress callbacks; it updates the filter on append and closes/persists state.

Primitive and byte writable types include `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, and `LongWritable`, each with default/value constructors, mutable `set`/`get`, `Writable` serialization, equality/hash, comparison, and string conversion. Their nested `Comparator` classes compare serialized byte arrays directly; `LongWritable.DecreasingComparator` reverses sort order. `BytesWritable` extends `BinaryComparable`, exposes backing bytes, deprecated aliases, logical length/size, capacity management, set overloads, serialization, equality/hash, string conversion, and a serialized-byte comparator.

Buffer and utility stream classes include `Closeable`, `CompressedWritable`, `DataInputBuffer`, `DataOutputBuffer`, `InputBuffer`, `OutputBuffer`, and `IOUtils`. `CompressedWritable` lazily inflates compressed subclass state through protected read/write hooks. Input/output buffers expose backing arrays, positions, lengths, reset behavior, and write-to operations. `IOUtils` provides copy helpers, `readFully`, `skipFully`, cleanup of multiple closeables with logging, and quiet close helpers for streams and sockets. `IOUtils.NullOutputStream` discards bytes.

`DefaultStringifier<T>` serializes objects to and from strings using Hadoop serialization and provides static configuration persistence helpers for single objects and arrays. `GenericWritable` wraps one value from a fixed type list, serializing a type index and passing configuration into nested configurables. `MapWritable` extends `AbstractMapWritable` and implements map operations plus serialization. `ObjectWritable` serializes arbitrary declared classes and instances, supports static `writeObject` and `readObject` helpers, and is `Configurable`.

`MapFile` is the sorted key/value file container built on `SequenceFile`, with public `INDEX_FILE_NAME` and `DATA_FILE_NAME`, static rename/delete/fix/main helpers, a `Reader`, and a `Writer`. The reader opens index/data files, can create a data-file `SequenceFile.Reader`, reset, return mid/final keys, seek, iterate, exact/get-closest lookup, and close. The writer has constructors for key/value classes or comparators, compression options, progress callbacks, index interval getters/setters, append, and close.

`MD5Hash` represents fixed-size MD5 digests. It supports construction from default/string/byte array, static read, write/readFields, setting and retrieving digest bytes, digest helpers over bytes, strings, streams, and byte ranges, half and quarter digest projections, equality/hash/comparison/string conversion, `setDigest`, `MD5_LEN`, and a raw comparator. `MultipleIOException` aggregates IO exceptions and can create a combined `IOException`. `NullWritable` is a singleton zero-byte writable/comparable with a raw comparator.

`RawComparator<T>` extends `Comparator<T>` with serialized byte-array comparison. `SequenceFile` is a flat binary key/value container and exposes static `getCompressionType`, `setCompressionType`, many `createWriter` overloads over `FileSystem`, `Configuration`, `Path`, `FSDataOutputStream`, key/value classes, buffer/replication/block settings, compression type, codec, progress, and metadata. `SYNC_INTERVAL` defines sync spacing. Its documentation describes the common header, metadata, sync marker, and the uncompressed, record-compressed, and block-compressed physical formats. `SequenceFile.CompressionType` has `NONE`, `RECORD`, and `BLOCK`; `SequenceFile.Metadata` is a `Writable` map of `Text` attribute names to `Text` values. The visible start of `SequenceFile.Reader` includes construction from filesystem/path/configuration, protected `openFile` override hook, and the beginning of synchronized `close`.

## Control Flow and Behavioral Contracts

Filesystem control flow follows the `FileSystem` contract: callers resolve `Path` instances against a backend, then use open/create/append/delete/rename/list/status/mkdirs/working-directory operations. Local, FTP, KFS, S3, and native S3 implementations expose the same public shape while mapping the work to local files, FTP sessions, KFS clients, block/inode S3 stores, or native S3 objects. `Progressable` callbacks appear on writes and long-running copy flows. `PositionedReadable` promises thread-safe positional reads that do not change the current stream offset, while `Seekable` methods move or report the current stream position.

Trash flow moves a path into `.Trash/current` while preserving the original path below that directory. Checkpointing rolls current trash into a checkpoint, and expunge deletes old checkpoints. The emptier is intended to run periodically as a superuser service and to avoid full trash enumeration, filesystem date support, and clock synchronization requirements.

S3 block filesystem flow splits namespace metadata from data blocks. `S3FileSystem` uses `FileSystemStore` to persist `INode` entries and `Block` objects; reads reconstruct files from block metadata, and writes create block records plus inode metadata. Rename and delete have object-store semantics rather than local filesystem atomicity. Native S3 flow stores file contents directly as objects and infers directories from marker objects and prefixes, which changes list/status behavior around ambiguous file-versus-directory keys.

HTTP server flow constructs a Jetty listener, registers default apps/servlets, attaches contexts, attributes, filters, and servlets, optionally configures SSL, then starts/stops/joins the server. `FilterInitializer` instances plug into `FilterContainer` to add named or global filters, while `StackServlet` serves diagnostics.

Writable serialization flow is uniformly `write(DataOutput)` and `readFields(DataInput)`. Primitive writables encode fixed primitive values; byte comparables and raw comparators avoid object allocation by comparing serialized byte arrays. `AbstractMapWritable`, `MapWritable`, `GenericWritable`, and `ObjectWritable` add class/type metadata so heterogeneous or declared-type values can round-trip through Hadoop RPC, configuration, SequenceFile, MapFile, and MapReduce key/value paths.

Sorted-file flow centers on `SequenceFile` and `MapFile`. `SequenceFile.createWriter` selects writer behavior from compression settings and metadata; records are written with sync markers. `MapFile.Writer.append` expects keys in sorted order and creates both data and index files, while `MapFile.Reader` loads/uses the index to seek, iterate, and find closest keys. `BloomMapFile.Reader.probablyHasKey` is an optimization gate before real lookup, not a correctness proof.

## State, Persistence, and Side Effects

The XML itself persists the Hadoop 0.20.2 public API for compatibility comparison. Runtime state represented by this chunk includes filesystem working directories, file positions, local file handles, FTP client sessions and statistics, KFS locks, S3 credentials, S3 inodes and blocks, native S3 directory markers, permission bits and umasks, command arguments, Jetty server/listener/context/filter state, writable values, class-id maps, compression buffers, map and sequence file indices, Bloom filters, MD5 digests, object serialization configuration, and metadata maps.

Persistent formats are central. `FsPermission` and `PermissionStatus` persist ownership and mode information through `Writable`. S3 block files persist namespace state as inodes plus block objects; native S3 persists data as ordinary S3 objects with marker conventions. `MapFile` persists `data` and `index` sequence files. `BloomMapFile` adds a Bloom filter file. `SequenceFile` persists headers, key/value class names, compression flags, codec, metadata, sync markers, record lengths, and optional compressed record or block payloads. `MD5Hash`, primitive writables, `BytesWritable`, arrays, map writables, object writables, and metadata all define binary compatibility contracts through their serialized form.

Side effects include local file creation/deletion/rename/chmod/chown, FTP network operations, KFS and S3 remote calls, shell command execution through local filesystem permission helpers, HTTP listener binding, servlet/filter registration, stream reads/writes, configuration mutation through stringifiers, and diagnostic output from S3 dump or stack servlet paths.

## Dependencies and Integration Points

This chunk integrates with Java IO, `java.net.URI`, `java.net.Socket`, `java.util` collections, `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `Closeable`, `Comparator`, Jetty classes under `org.mortbay.jetty`, servlet APIs, Apache Commons Logging, Apache Commons Net FTP, Hadoop `Configuration`, `Configured`, `Tool`, `Progressable`, `FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `BlockLocation`, `Path`, `PathFilter`, `Writable`, `WritableComparable`, `WritableComparator`, compression codecs, and Bloom filter utilities.

The main integration boundaries are compatibility-sensitive: filesystem implementations must satisfy the shared `FileSystem` surface; permission objects must preserve wire formats used by HDFS and tools; HTTP server registration is used by Hadoop daemons; writable classes are used by RPC, SequenceFile, MapFile, MapReduce shuffle/sort, configuration stringification, and user data models; and S3/KFS/FTP backends expose remote storage through the same client APIs used by local and HDFS filesystems.

## Risks and Compatibility Notes

This chunk starts and ends inside classes/interfaces. The final source-level report must merge adjacent chunks to avoid incomplete `PositionedReadable` and `SequenceFile.Reader` conclusions.

Because this is JDiff XML, behavioral details are inferred from signatures and Javadocs rather than bodies. It cannot show internal synchronization, exact exception branching, buffer ownership, retry policies, cleanup order, resource leaks, S3 consistency handling, or Jetty configuration internals.

Public API compatibility is strict. Changing raw versus generic signatures, checked exceptions, static/final/synchronized flags, field names, visibility, deprecation state, constructor overloads, or nested class names can break downstream code compiled against Hadoop 0.20.2.

Filesystem backends have different semantics behind the same methods. FTP and S3 append are optional or unsupported; S3 rename is not natively atomic; native S3 directory status depends on marker/prefix heuristics; local permission/owner changes depend on platform shell commands; KFS depends on native/client deployment; and position/seek behavior can differ by stream implementation.

Writable and sorted-file formats are fragile. Changes to `BytesWritable` logical length versus backing capacity, raw comparator byte ordering, `AbstractMapWritable` class-id assignment, `GenericWritable` allowed type ordering, `ObjectWritable` declared-class handling, `MD5Hash` byte length, `SequenceFile` sync/header/compression layout, `MapFile` index interval, or Bloom filter persistence can corrupt compatibility with existing data.

Mutable and global state creates test isolation risk. `Configuration`-backed umasks/stringified objects, HTTP server ports and filters, filesystem working directories, FTP sessions, S3 credentials, KFS locks, map writable class maps, reusable data buffers, compressed writable inflation state, and sequence/map file readers all need cleanup and cannot be assumed thread-safe unless explicitly documented.

## Test Signals

JDiff-level tests should validate that the XML remains well formed across package transitions and that every public/protected API item in this range preserves name, package, inheritance, implemented interfaces, signatures, parameter order/types, return types, declared exceptions, visibility, static/final/abstract/synchronized/native flags, deprecation markers, and field constants.

Filesystem contract tests should cover `RawLocalFileSystem`, `FTPFileSystem`, `KosmosFileSystem`, `S3FileSystem`, and `NativeS3FileSystem` create/open/append behavior, unsupported append handling, rename/delete/mkdirs/list/status, working-directory resolution, permissions and ownership where supported, positioned reads, seek position, local output staging, block locations, and cleanup of network/client resources.

S3-specific tests should round-trip `INode` and `Block` serialization, exercise `FileSystemStore` store/retrieve/delete/list/deep-list/purge/dump paths, validate credential initialization failures, reject version mismatches, cover non-atomic rename expectations, and verify native S3 directory marker and prefix masking behavior.

Permission tests should cover every `FsAction` lattice operation, short and symbolic `FsPermission` conversion, default and configured umasks, immutable factory methods, `PermissionStatus` read/write and static helper serialization, and access-control exception propagation.

HTTP tests should cover listener creation, port selection, thread settings, servlet/internal servlet registration, context attributes, filter and global-filter path mappings, SSL listener overloads, lifecycle start/stop/join, and `StackServlet` response behavior.

Writable tests should round-trip primitive writables, `BytesWritable`, arrays, map writables, generic writables, object writables, compressed writables, metadata, and MD5 hashes through `DataOutput`/`DataInput`; assert equality/hash/compare contracts; check raw comparators against object comparators; verify buffer capacity versus logical length; and isolate configuration injection.

SequenceFile, MapFile, ArrayFile, and BloomMapFile tests should write/read empty and non-empty files, all compression modes, metadata, sync markers, sorted and unsorted append behavior, index intervals, seek/get/getClosest/midKey/finalKey, Bloom false-positive tolerant lookup, delete/rename/fix helpers, and compatibility with `WritableComparator` and compression codecs.

Utility tests should cover `IOUtils.copyBytes`, close-on-finish behavior, `readFully`, `skipFully`, cleanup with multiple closeables and logged exceptions, `NullOutputStream`, `DefaultStringifier` store/load for single objects and arrays, `MultipleIOException.createIOException`, and `MD5Hash` digest helpers over byte arrays, strings, and streams.

### subset-b-007331: lines 12317-18734

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 12317-18734

## Scope and Purpose

This chunk is part of Hadoop 0.20.2's JDiff XML API snapshot, not implementation source. It records public/protected API surface, signatures, inheritance, deprecation metadata, exceptions, fields, and Javadoc excerpts for a large section of `org.apache.hadoop.io`, `org.apache.hadoop.io.compress`, `org.apache.hadoop.io.compress.bzip2`, `org.apache.hadoop.io.compress.zlib`, and the beginning of `org.apache.hadoop.io.file.tfile`.

The chunk starts in the middle of `org.apache.hadoop.io.SequenceFile.Reader` and ends in the middle of `org.apache.hadoop.io.file.tfile.TFile.Reader.Scanner.Entry`. The merge lane should treat this as a partial XML range that needs neighboring chunks for complete per-file/package context.

## API Areas Covered

### SequenceFile Reader/Sorter/Writer

The visible `SequenceFile.Reader` methods expose read-side metadata and cursor operations for sequence-format key/value files:

- Type and file metadata: `getKeyClassName()`, `getKeyClass()`, `getValueClassName()`, `getValueClass()`, `isCompressed()`, `isBlockCompressed()`, `getCompressionCodec()`, `getMetadata()`.
- Record access: `next(Writable key)`, `next(Writable key, Writable val)`, `next(Object key)`, `getCurrentValue(Writable)`, `getCurrentValue(Object)`, and raw access with `createValueBytes()`, `nextRaw(DataOutputBuffer, ValueBytes)`, `nextRawKey(DataOutputBuffer)`, `nextRawValue(ValueBytes)`.
- Positioning: `seek(long)`, `sync(long)`, `syncSeen()`, `getPosition()`.
- Lifecycle: synchronized `close()`.

`SequenceFile.Reader.next(DataOutputBuffer)` is deprecated in favor of `nextRaw(DataOutputBuffer, SequenceFile.ValueBytes)`. The reader contract distinguishes exact positions returned by `SequenceFile.Writer.getLength()` from arbitrary positions that must use `sync(long)`.

`SequenceFile.Sorter` describes sorting and merging of sequence files using either key/value classes or a `RawComparator`. It exposes merge fan-in and memory controls (`setFactor`, `getFactor`, `setMemory`, `getMemory`), progress reporting (`setProgressable`), sort entry points, several merge overloads, `cloneFileAttributes`, and `writeFile`. Its Javadoc stresses efficient `Writable.readFields(DataInput)` implementations for sort performance.

`SequenceFile.Sorter.RawKeyValueIterator` is the raw merge iterator contract: `next()` sets up current key/value, `getKey()` returns a `DataOutputBuffer`, `getValue()` returns `SequenceFile.ValueBytes`, `getProgress()` exposes byte progress, and `close()` releases streams.

`SequenceFile.Sorter.SegmentDescriptor` models a merge segment with offset, length, and path. It supports sync checking, input preservation/deletion control, raw key/value advancement, key retrieval, ordering via `Comparable`, and overridable cleanup. The default cleanup closes the file handle and deletes the file unless preservation is selected.

`SequenceFile.ValueBytes` abstracts raw sequence values, with methods to write uncompressed bytes, write already-compressed bytes, and report stored size. `writeCompressedBytes` explicitly does not compress uncompressed values.

`SequenceFile.Writer` exposes constructors for file creation with filesystem, configuration, key/value classes, optional replication/block-size/progress/metadata parameters. It exposes class/codec metadata, `sync()`, synchronized `close()`, synchronized typed and object `append`, `appendRaw`, and synchronized `getLength()`. Protected serializer fields are part of the public XML surface: `keySerializer`, `uncompressedValSerializer`, and `compressedValSerializer`.

### SetFile and SortedMapWritable

`SetFile` is a file-backed set of keys implemented as a `MapFile` specialization. The reader extends `MapFile.Reader` with constructors using a set path and optional `WritableComparator`, plus `seek`, `next`, and `get` for `WritableComparable` keys. The writer extends `MapFile.Writer`; the old constructor without `Configuration` is deprecated, and active constructors include `Configuration`, `FileSystem`, path/name, element class or comparator, and `SequenceFile.CompressionType`. `append(WritableComparable)` requires keys to be strictly increasing.

`SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap`. The XML exposes default and copy constructors and the normal sorted-map operations (`comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`) plus mutable map operations and `Writable` serialization (`readFields`, `write`). Keys are `WritableComparable`; values are `Writable`.

### String, Text, UTF8, VersionedWritable, and Variable Integer Writables

`Stringifier` is a `Closeable` object/string conversion contract with `toString(Object)`, `fromString(String)`, and `close()`, all IOException-capable.

`Text` is the primary UTF-8 byte-backed Hadoop string type. It extends `BinaryComparable` and implements `WritableComparable`. Constructors accept no args, `String`, `Text`, and byte arrays. Key behavior:

- Raw storage: `getBytes()` returns the backing bytes and `getLength()` gives the valid byte length.
- UTF-8 traversal/search without creating Java strings: `charAt(int)`, `find(String)`, `find(String, int)`.
- Mutation: `set(String)`, `set(byte[])`, `set(Text)`, `set(byte[], int, int)`, `append(byte[], int, int)`, and `clear()`.
- Serialization: `readFields(DataInput)`, `write(DataOutput)`, and static `skip(DataInput)`.
- Encoding helpers: static `decode` overloads with optional replacement behavior, static `encode` overloads, `readString`, `writeString`, `validateUTF8`, `bytesToCodePoint(ByteBuffer)`, and `utf8Length(String)`.
- Equality/hash and `toString()` are public API.

The `Text` Javadoc states its length is serialized with zero-compressed encoding and that it includes byte-level comparison and UTF-8 validation utilities. `Text.Comparator` extends `WritableComparator` with a raw byte `compare` optimized for `Text`.

`TwoDArrayWritable` is a `Writable` wrapper for a matrix of instances of a specified class. It provides constructors with value class and optional initial matrix, `toArray`, `set`, `get`, `readFields`, and `write`.

`UTF8` is deprecated and replaced by `Text`, but remains in the public API. It implements `WritableComparable` with constructors from `String`/`UTF8`, mutable setters, raw byte/length access, read/write/skip, compare/equality/hash/toString, and static byte/string helpers. `UTF8.Comparator` provides a raw `WritableComparator`.

`VersionedWritable` is a base `Writable` that embeds version checking. Subclasses provide `getVersion()`. Its `write` and `readFields` participate in version serialization/validation. `VersionMismatchException` records expected/found version bytes and has `toString()`.

`VIntWritable` and `VLongWritable` are `WritableComparable` wrappers for variable-length encoded integers/longs. They expose default/value constructors, `set`, `get`, read/write, equals/hash, `compareTo`, and `toString`. These integrate with the zero-compressed integer utilities documented later in `WritableUtils`.

### Writable Core, Factories, Names, and Utilities

`Writable` is the base Hadoop serialization interface with `write(DataOutput)` and `readFields(DataInput)`. The documentation emphasizes compact, high-speed serialization for network and persistent storage, and asks implementations to provide no-arg constructors because deserialization commonly constructs an empty instance and then calls `readFields`.

`WritableComparable` combines `Writable` and `Comparable`; the docs identify it as the typical MapReduce key interface.

`WritableComparator` implements `RawComparator` for `WritableComparable`s. It has protected constructors, a synchronized static comparator registry (`get`, `define`), `getKeyClass()`, `newKey()`, object comparison, typed `WritableComparable` comparison, and raw byte comparison. Static helpers parse primitive values from byte arrays (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`) and provide `compareBytes`/`hashBytes`. The raw `compare(byte[],...)` hook is the main performance extension point for sort-intensive paths.

`WritableFactories` is a synchronized registry for `WritableFactory` instances, used so non-public writables can be constructed by `ObjectWritable`. It supports `setFactory`, `getFactory`, and `newInstance` with or without `Configuration`. `WritableFactory` itself has only `newInstance()`.

`WritableName` maps writable classes to stable external names and aliases. It supports synchronized `setName`, `addName`, `getName`, and `getClass(name, conf)`. Its role is preserving compatibility when writable implementation classes are renamed.

`WritableUtils` is a final utility class. It provides compressed byte-array and string read/write/skip helpers, string-array helpers, `displayByteArray`, serialization-based `clone`, deprecated `cloneInto` in favor of `ReflectionUtils.cloneInto`, variable-length integer/long encoding and decoding (`writeVInt`, `writeVLong`, `readVInt`, `readVLong`, `isNegativeVInt`, `decodeVIntSize`, `getVIntSize`), enum read/write by string name, `skipFully`, and `toByteArray(Writable[])`.

### Compression Package

`BlockCompressorStream` and `BlockDecompressorStream` adapt `CompressorStream`/`DecompressorStream` for block-based codecs. The compressor writes blocks containing uncompressed length plus length-prefixed compressed chunks; the decompressor reads corresponding block data and supports `resetState`.

`BZip2Codec` implements `CompressionCodec` but only supports stream creation without explicit compressor/decompressor objects. Methods that require `Compressor` or `Decompressor` instances, including `createCompressor`, `createDecompressor`, and the overloads accepting these objects, are documented as unsupported and throw `UnsupportedOperationException`. The default extension is `.bz2`.

`CodecPool` is a static pool for reusable codec resources: `getCompressor`, `getDecompressor`, `returnCompressor`, and `returnDecompressor`.

`CompressionCodec` defines the generic codec contract: output stream creation, input stream creation, compressor/decompressor type discovery, compressor/decompressor construction, and default extension discovery.

`CompressionCodecFactory` is configuration-driven. It constructs from `Configuration`, exposes codec class listing and setting, resolves a codec for a `Path`, removes codec suffixes, supports a diagnostic `main`, and has an Apache Commons Logging `LOG` field.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases. Input streams wrap protected `InputStream in`, close, read single bytes, and reset state. Output streams wrap protected final `OutputStream out`, close/flush, declare abstract byte-array `write`, `finish`, and `resetState`. The output stream intentionally makes byte-array write abstract to avoid leakage to the underlying stream.

`Compressor` and `Decompressor` are Deflater/Inflater-like state machines. Compressor methods include `setInput`, `needsInput`, `setDictionary`, byte counters, `finish`, `finished`, `compress`, `reset`, and `end`. Decompressor mirrors input/dictionary/finished/decompress/reset/end plus `needsDictionary`. The documented control flow is caller-driven: provide input when `needsInput()` is true, drain with `compress`/`decompress`, call `finish` for compression termination, and call `reset` for reuse or `end` for final disposal.

`CompressorStream` and `DecompressorStream` own protected compressor/decompressor instances, buffers, and closed/eof flags. They implement write/read loops, compression/decompression helpers, finish/reset/close, skip/available for decompression, and disabled mark/reset behavior. Protected constructors allow subclasses to directly set the underlying stream.

`DefaultCodec` implements both `Configurable` and `CompressionCodec`; `GzipCodec` extends it and supplies gzip-specific stream/compressor/decompressor behavior. `GzipCodec.GzipInputStream` and `GzipCodec.GzipOutputStream` bridge Java gzip/deflater streams into Hadoop `CompressionInputStream`/`CompressionOutputStream`, overriding read/write/close/finish/flush/skip/reset operations.

### BZip2 and Zlib Adapters

`BZip2Constants` is a public historical constants interface. It includes algorithm constants and a public static `rNums` array; the Javadoc explicitly marks this as a FIXME because public mutable array access could be modified by malicious code.

`BZip2DummyCompressor` and `BZip2DummyDecompressor` implement the compressor/decompressor interfaces as dummy adapters for BZip2, matching the earlier `BZip2Codec` limitation.

`CBZip2InputStream` and `CBZip2OutputStream` are raw bzip2 stream implementations without file header characters. They expose read/write/finish/flush/close behavior, output block-size helpers, and many protected compression constants. Their documentation warns about large memory use, encourages early close to release memory, says instances are not thread-safe, and notes a TODO to update to BZip2 1.0.1. `CBZip2OutputStream.chooseBlockSize(long)` helps select block sizes, and output construction supports default 900k or specified block size.

`BuiltInZlibDeflater` and `BuiltInZlibInflater` wrap `java.util.zip.Deflater`/`Inflater` to implement Hadoop `Compressor`/`Decompressor`, with synchronized `compress`/`decompress`.

`ZlibCompressor` and `ZlibDecompressor` are Hadoop zlib implementations. Both expose synchronized state operations for input, dictionary, finish/finished, compression/decompression, byte counters, reset, and end. Constructors allow explicit compression level/strategy/header/direct-buffer size for compressors and header/direct-buffer size for decompressors.

`ZlibCompressor.CompressionHeader` supports `NO_HEADER`, `DEFAULT_HEADER`, and `GZIP_FORMAT`; `ZlibDecompressor.CompressionHeader` also supports `AUTODETECT_GZIP_ZLIB`. `CompressionLevel` has `NO_COMPRESSION`, `BEST_SPEED`, `BEST_COMPRESSION`, and `DEFAULT_COMPRESSION`. `CompressionStrategy` has `FILTERED`, `HUFFMAN_ONLY`, `RLE`, `FIXED`, and `DEFAULT_STRATEGY`.

`ZlibFactory` chooses native or built-in zlib implementations from `Configuration`. It checks native availability and returns compressor/decompressor classes or instances.

### TFile Start

`ByteArray` is a final adapter that wraps a `BytesWritable`, a whole `byte[]`, or a byte-array slice as a `RawComparable`, exposing `buffer`, `offset`, and `size`. `RawComparable` defines the same byte-range access contract and delegates actual ordering to external `RawComparator` implementations.

`MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are IOException subclasses for TFile metadata block access failures.

`TFile` is a type-less key/value container. Keys are bytes limited to 64KB; value length is practically disk-limited. Features include block compression, named metadata blocks, sorted or unsorted keys, and seek by key or file offset. Public constants name compression algorithms (`gz`, `lzo`, `none`) and comparators (`memcmp`, Java class prefix). Public static helpers create comparators, list supported compression algorithms, and dump file info via `main`.

`TFile.Reader` wraps an `FSDataInputStream`, file length, and `Configuration`. It is `Closeable` and provides comparator metadata, sorted status, entry count, first/last keys, entry comparator, raw comparator, named metadata block streams, near-record/key lookup by offset, and scanner creation over whole file, byte ranges, key ranges, and record-number ranges. Older scanner overloads are deprecated in favor of explicit `createScannerByKey` overloads.

`TFile.Reader.Scanner` is a closeable cursor over a range. It can be constructed over byte offsets or raw key bounds. Cursor operations include `seekTo`, `lowerBound`, `upperBound`, `rewind`, `seekToEnd`, `advance`, `atEnd`, `entry`, and `getRecordNum`. The docs repeatedly state that entries returned by previous `entry()` calls are invalidated by cursor movement or close.

The chunk ends inside `TFile.Reader.Scanner.Entry`. Visible entry methods include `getKeyLength`, combined `get(BytesWritable key, BytesWritable value)`, key copying to `BytesWritable` or user byte arrays, `writeKey(OutputStream)`, `getKeyStream()`, `getValue(BytesWritable)`, `writeValue(OutputStream)`, `getValueLength()`, and `getValue(byte[])`. Value access is single-pass: the value is not cached and repeated value reads without moving the cursor cause exceptions. `getValueLength()` requires a separate `isValueLengthKnown()` test, but that method is outside this chunk.

## Control Flow and State Behavior

The XML describes several stateful cursor and stream contracts:

- `SequenceFile.Reader` is synchronized for close, class resolution, value retrieval, typed next calls, raw next, seek, sync, and position. State includes current file offset, last-read key/value, sync-marker status, compression/metadata configuration, and open stream lifecycle.
- `SequenceFile.Writer` is synchronized for close, appends, raw appends, and length retrieval. Writer state includes serializers, compression codec, sync points, current output length, and file metadata.
- `SequenceFile.Sorter` controls a multi-stage flow: read input segments, optionally delete inputs, sort/merge through `RawKeyValueIterator`, then write records to a cloned or supplied writer. Segment descriptors own file-handle and temporary-file cleanup behavior.
- Writable classes serialize and deserialize themselves through `DataOutput`/`DataInput`, with no external schema beyond class name/name alias and encoded byte layout.
- Compression streams are pull/push state machines around reusable compressor/decompressor instances. Callers and streams must honor `needsInput`, `finished`, `resetState`, `close`, and `end` semantics.
- TFile readers own an indexed, compressed, seekable file view. Scanners own an implicit cursor; entries are views into the scanner and are invalidated by cursor movement. Entry value data is stream-like and only readable once per cursor position.

## Persistence and Compatibility

This chunk is dominated by persistent binary compatibility contracts:

- `Writable`, `WritableComparable`, `WritableComparator`, `WritableFactories`, and `WritableName` define how Hadoop serializes objects, instantiates them during deserialization, compares raw serialized keys, and preserves class-name compatibility after renames.
- `Text`, `UTF8`, `VIntWritable`, `VLongWritable`, and `WritableUtils` document precise byte encodings such as UTF-8 with zero-compressed length and variable-length integer/long encodings.
- `SequenceFile.Reader`/`Writer` and `SetFile` APIs govern on-disk sequence/set/map file compatibility, including metadata, compression type, sync points, raw key/value paths, and sorted key invariants.
- Compression codecs and streams define compressed bytes emitted into sequence files and TFiles, including block-compression wrappers and gzip/bzip2/zlib format variants.
- TFile declares persistent layout expectations: typed as bytes, optional sorting, block compression, metadata blocks, indexes proportional to block counts, and configurable chunk/buffer sizes.

## Dependencies and Integration Points

The APIs integrate with:

- Hadoop filesystem/configuration: `FileSystem`, `Path`, `FSDataInputStream`, `Configuration`.
- Hadoop IO primitives: `Writable`, `WritableComparable`, `WritableComparator`, `RawComparator`, `BytesWritable`, `DataOutputBuffer`, `SequenceFile.Metadata`.
- Hadoop utility hooks: `Progress`, `Progressable`, `ReflectionUtils`, `Configurable`.
- Java IO and NIO: `Closeable`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, `ByteBuffer`, `CharacterCodingException`, `MalformedInputException`.
- Java compression: `Deflater`, `Inflater`, gzip stream adapters, and zlib wrappers.
- Logging and diagnostics: `CompressionCodecFactory.LOG` and `main` methods on codec/TFile utilities.
- MapReduce sorting paths: `WritableComparable` keys, raw comparators, `SequenceFile.Sorter`, and efficient `readFields`.

## Risks and Edge Cases

- This is JDiff XML, so it records signatures and docs, not implementation bodies. Control-flow details are inferred from API contracts and Javadoc.
- The chunk starts and ends mid-API; neighboring chunks are required for complete `SequenceFile.Reader` and `TFile.Reader.Scanner.Entry` coverage.
- Public deprecations visible here require migration care: `SequenceFile.Reader.next(DataOutputBuffer)`, `SetFile.Writer(FileSystem, String, Class)`, `UTF8`, `WritableUtils.cloneInto`, and older TFile scanner overloads.
- `SetFile.Writer.append` requires strictly increasing keys; violating this breaks sorted set/map-file semantics.
- Raw comparator performance is critical; default `WritableComparator.compare(byte[],...)` deserializes objects and can allocate heavily.
- `WritableName` aliases and `WritableFactories` are compatibility-sensitive global registries; incorrect mappings can make existing persistent files unreadable.
- BZip2 codec object-based compressor/decompressor APIs are documented as unsupported and throw `UnsupportedOperationException`.
- `BZip2Constants.rNums` is public mutable array state flagged as a security risk in the docs.
- BZip2 streams warn about high memory usage, need early close to release memory, and are not thread-safe.
- TFile readers use `FSDataInputStream.seek()+read()` rather than true multi-threaded positioned reads; multiple scanners over one reader serialize actual I/O.
- TFile scanner entries become invalid after cursor movement/close; value data is not cached and repeated value reads at one cursor position throw exceptions.
- `Text.getBytes()` and `UTF8.getBytes()` expose raw backing arrays where only the declared length is valid; callers must not treat the full array as logical content.
- UTF-8 helpers have replacement-vs-exception modes; tests must cover malformed input and buffer position side effects from `bytesToCodePoint`.

## Test Signals

Useful validation targets for implementation or compatibility tests derived from this API chunk:

- SequenceFile round trips for uncompressed, record-compressed, and block-compressed files; validate metadata, codec reporting, raw reads, sync/seek semantics, and `getLength()` positions.
- SequenceFile sorter tests for custom `RawComparator`, merge fan-in, memory limits, progress reporting, temporary segment cleanup, and delete-input behavior.
- SetFile writer/reader tests for strict key ordering, comparator-based lookup, deprecated constructor compatibility, and compression type coverage.
- Writable serialization tests for no-arg construction, `WritableFactories` custom factories, `WritableName` alias lookup, `VersionedWritable` mismatch handling, and raw comparator equivalence to object comparison.
- Text/UTF8 tests for raw byte length, append/set slice behavior, malformed UTF-8 replacement and exception modes, zero-compressed length serialization, `skip`, `find`, `charAt`, and comparator ordering.
- WritableUtils tests for compressed byte/string arrays, enum read/write, `skipFully`, variable-length integer size/sign boundaries, and serialization clone behavior.
- Compression tests for `CodecPool` reuse, `CompressionCodecFactory` path suffix resolution, stream `finish` vs `close`, reset behavior, gzip bridge behavior, and unsupported BZip2 compressor/decompressor methods.
- BZip2/zlib tests for block-size boundaries, memory/resource close behavior, header variants, native zlib factory fallback, byte counters, and dictionary/needs-input state transitions.
- TFile tests for sorted/unsorted modes, metadata block duplicate/missing exceptions, byte/key/record scanner ranges, scanner cursor invalidation, single-pass value access, value-length-known handling, and compression algorithms `none`, `lzo`, and `gz`.

### subset-b-007332: lines 18735-25047

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 18735-25047

## Scope

This chunk is a large middle segment of the generated JDiff public API snapshot for Hadoop 0.20.2. It is compatibility metadata, not executable implementation code. The range begins inside `org.apache.hadoop.io.file.tfile.TFile.Reader.Scanner.Entry`, covers the remainder of the public TFile entry APIs, then records public APIs across TFile writing/utilities, retry policies, serialization, Hadoop IPC/RPC, RPC metrics, log-level tooling, the original Hadoop metrics framework, network topology and socket helpers, and the beginning of the legacy record I/O package.

The XML records public API shape: package/class/interface names, inheritance, implemented interfaces, constructors, methods, fields, parameter types, declared exceptions, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadoc. Behavioral notes below are inferred from signatures and Javadoc because this source does not contain method bodies. The chunk is partial at both ends: it starts after earlier `TFile.Reader.Scanner.Entry` members and ends inside `org.apache.hadoop.record.Buffer` after `getCapacity()`.

## Purpose and Major API Surface

The TFile entries describe Hadoop's binary key/value container format. The tail of `TFile.Reader.Scanner.Entry` exposes one-shot value access through `getValue(byte[], int)` and `getValueStream()`, length visibility through `isValueLengthKnown()`, key comparison overloads against raw byte arrays and `RawComparable`, and object identity through `equals`/`hashCode`. `TFile.Writer` is a closeable writer constructed from an `FSDataOutputStream`, minimum block size, compression name, optional comparator name, and `Configuration`. It appends key/value pairs either as byte arrays or as two-stage streams via `prepareAppendKey(int)` and `prepareAppendValue(int)`, and creates compressed metadata blocks through `prepareMetaBlock`.

`org.apache.hadoop.io.file.tfile.Utils` exposes low-level TFile encoding helpers: variable-length integer/long encoding and decoding, Text-compatible string read/write, and `lowerBound`/`upperBound` binary searches over lists or arrays. `Utils.Version` serializes and compares a major/minor version pair and answers compatibility through `compatibleWith`.

`org.apache.hadoop.io.retry` defines reusable retry behavior. `RetryPolicies` is a factory for fixed sleep, maximum-time, proportional sleep, exponential backoff, exception-dispatch, and remote-exception-dispatch policies. It also exposes singleton policies `TRY_ONCE_THEN_FAIL`, `TRY_ONCE_DONT_FAIL`, and `RETRY_FOREVER`. `RetryPolicy` is the policy callback interface, and `RetryProxy` creates dynamic proxies that apply one policy to all methods or method-specific policies to selected methods.

`org.apache.hadoop.io.serializer` covers pluggable serialization. `Serializer` and `Deserializer` are stream-oriented interfaces with `open`, `serialize`/`deserialize`, and `close`. `Serialization` selects serializers/deserializers for accepted classes. `SerializationFactory` discovers configured serialization implementations from `Configuration`. `WritableSerialization` adapts Hadoop `Writable`; `JavaSerialization` adapts Java `Serializable`; `JavaSerializationComparator` and `DeserializerComparator` compare serialized byte ranges after deserializing values.

`org.apache.hadoop.ipc` records the classic Hadoop IPC/RPC layer. `Client` sends `Writable` parameters to servers and returns `Writable` results, with single-call and parallel-call overloads, socket factory support, user identity through `UserGroupInformation`, a ping interval setter, and explicit `stop()`. `RemoteException` carries remote class name/message data, can unwrap remote exception types, and serializes to/from XML attributes. `RPC` builds client-side `VersionedProtocol` proxies, stops proxies, performs expert parallel reflective calls, and constructs `RPC.Server` instances. `RPC.Server` extends the abstract `Server` and dispatches calls to a protocol implementation instance. `RPC.VersionMismatch` captures protocol name plus client/server version numbers. `Server` owns listener lifecycle (`start`, `stop`, `join`), binding, socket buffer sizing, handler dispatch, authorization, listener address, call queue/open-connection counters, public wire constants `HEADER` and `CURRENT_VERSION`, and protected `rpcMetrics`. `VersionedProtocol` is the version negotiation contract for RPC protocols.

`org.apache.hadoop.ipc.metrics` ties RPC servers to the old metrics framework. `RpcMetrics` registers a `MetricsRegistry` with queue time, processing time, open-connection, and call-queue gauges/rates, updates those values from a `Server`, exposes management getters for average/min/max queue and processing time, and supports shutdown/reset. `RpcActivityMBean` registers the metrics as an MBean, while `RpcMgtMBean` defines the JMX management view.

`org.apache.hadoop.log.LogLevel` exposes a command-line and servlet-based log-level adjuster. The top-level class has `main(String[])` and a usage string. `LogLevel.Servlet` handles HTTP `doGet` requests, which is the public servlet endpoint for querying or changing logger levels.

The `org.apache.hadoop.metrics` package documents the original metrics subsystem. `ContextFactory` is a singleton factory that reads `hadoop-metrics.properties`, manages attributes, and constructs named `MetricsContext` instances, defaulting to `NullContext` when no context class is configured. `MetricsContext` controls context initialization, start/stop/close, monitoring state, record creation, updater registration, and reporting period. `MetricsRecord` represents tagged metric rows with overloaded `setTag`, `setMetric`, `incrMetric`, `removeTag`, `update`, and `remove` methods. `MetricsException` is the unchecked error type, `MetricsUtil` supplies convenience context/record helpers, and `Updater` is the periodic callback contract.

Metrics implementations and internals appear under `org.apache.hadoop.metrics.file`, `ganglia`, `jvm`, `spi`, and `util`. `FileContext` emits records to a file and exposes file/period property names. `GangliaContext` emits records to Ganglia. `EventCounter` is a log4j appender counting fatal/error/warn/info events. `JvmMetrics` initializes JVM metric reporting and pushes periodic updates. `AbstractMetricsContext` implements core context lifecycle, buffered record state, updater registration, periodic emission, flushing, update/remove operations, and period configuration. `CompositeContext` fans metrics out to multiple child contexts. `MetricsRecordImpl`, `MetricValue`, `OutputRecord`, `NullContext`, `NullContextWithUpdateThread`, and `Util.parse` represent record state, absolute/increment values, output views, no-op contexts, and helper parsing.

The metrics utility package exposes JMX and metric value primitives. `MBeanUtil` registers/unregisters MBeans. `MetricsBase` names and describes a metric and defines `pushMetric`. `MetricsDynamicMBeanBase` adapts a `MetricsRegistry` to JMX dynamic MBean methods. `MetricsIntValue` and `MetricsLongValue` are absolute gauges. `MetricsTimeVaryingInt` and `MetricsTimeVaryingLong` are interval counters. `MetricsTimeVaryingRate` tracks operation counts, average time, min/max time, and reset behavior. `MetricsRegistry` stores metrics by key and exposes keys/metric collections.

`org.apache.hadoop.net` covers DNS, rack topology, socket creation, and nonblocking socket stream wrappers. `DNSToSwitchMapping` maps host names or IP addresses to rack paths; `CachedDNSToSwitchMapping` caches another mapper's results. `DNS` provides reverse DNS, interface IP lookup, and default/all host lookup using default or named nameservers. `NetUtils` resolves socket factories from Hadoop configuration, parses socket addresses from host/URI strings, handles old split host/port configuration to new combined addresses, maintains static host resolutions for tests, derives client connect addresses for servers bound to wildcard addresses, wraps socket input/output streams with timeout-aware channel streams, connects sockets using Hadoop selectors, and normalizes host names to textual IPs. `NetworkTopology` models the rack/datacenter tree, adding/removing nodes, counting racks/leaves, computing distance and same-rack status, selecting random nodes by scope, counting available nodes with exclusions, and pseudo-sorting replica locations by proximity. `Node` is the interface for topology nodes, and `NodeBase` stores name, normalized network location, parent, and level with constants for root/path separators. `ScriptBasedMapping` is a configurable rack resolver. `SocketInputStream` and `SocketOutputStream` wrap selectable channels or sockets with read/write timeout behavior and expose readiness waits, channel access, open state, and full transfer helpers. `SocksSocketFactory` creates sockets through a SOCKS proxy and is configurable; `StandardSocketFactory` delegates to standard Java sockets.

The chunk ends in `org.apache.hadoop.record`, Hadoop's legacy record I/O API. `BinaryRecordInput` and `BinaryRecordOutput` implement `RecordInput` and `RecordOutput` over `InputStream`/`DataInput` and `OutputStream`/`DataOutput`. They include thread-local `get(...)` helpers, primitive read/write methods, string and `Buffer` read/write, and record/vector/map start/end delimiters. `Buffer` begins here as a comparable, cloneable mutable byte sequence with constructors from empty, byte array, and byte range inputs plus `set`, final `copy`, `get`, `getCount`, and `getCapacity`.

## Control Flow and Behavioral Contracts

TFile reader entry control is cursor-based. The scanner points at a key/value pair, the key can be compared repeatedly, but the value stream is intentionally one-shot. Calling `getValue(byte[])`, `getValue(byte[], int)`, or `getValueStream()` more than once without advancing the scanner is documented as exceptional. Value length can be unknown until data is consumed unless the value is smaller than a chunk or was advertised as a whole value during write.

TFile writer flow is stateful. Construction requires an output stream positioned at zero and a supported compression name. Key/value appends must preserve sorted order when a comparator is configured. Stream appends are ordered: prepare a key stream, close it, prepare a value stream, close it, then continue. The writer forbids concurrent active key/value streams; metadata block creation must not happen while a key or value append stream is active and terminates further key/value insertion. If append throws, the file is explicitly documented as inconsistent and only `close()` remains legitimate.

TFile utility flow is format-level. Variable-length encodings use compact first-byte ranges for small signed values and longer big-endian payloads for larger ranges. String helpers pair a VInt length with Text-format bytes. Lower/upper bound helpers assume sorted input and provide insertion/search positions, so comparator ordering must match the containing data structure. `Utils.Version` persists exactly a major/minor pair and centralizes compatibility decisions.

Retry control flow is caller-transparent once a `RetryProxy` is created. Method invocations flow through a proxy, failures are passed to a `RetryPolicy`, and the policy decides whether to retry based on exception, retry count, failover count, and configured sleeps or caps. Exception-mapping policies route different Java or remote exception types to different retry behavior. This is part of Hadoop's fault-tolerance surface around RPC and filesystem clients.

Serialization flow is stream-bound. A serializer/deserializer is opened on a `DataOutput` or `DataInput`-like stream, used for one or more objects, then closed. `SerializationFactory` selects the first implementation accepting the requested class. Comparators deserialize both byte ranges before comparison, so they trade simplicity for allocation, object construction, and dependency on class-specific deserialization correctness.

IPC/RPC control flow starts with a client proxy or raw `Client.call`, serializes a single `Writable` parameter, sends it to an address using configured sockets and optional UGI credentials, and returns a `Writable` or object result. Parallel call APIs send corresponding parameters to corresponding addresses and return arrays with nulls for failed or timed-out calls. Server lifecycle is explicit: bind/construct, `start()` listener and handlers, process queued calls through `call(Class, Writable, long)`, authorize protocol/user pairs, expose metrics, and `stop()`/`join()` on shutdown. `Server.get()`, `getRemoteIp()`, and `getRemoteAddress()` provide thread-local RPC context during call handling and serialization.

Metrics control flow is periodic and buffered. A `ContextFactory` supplies a `MetricsContext`; callers create `MetricsRecord` instances, set tags/metrics, then call `update()` to atomically merge a row into the context's buffered table. Registered `Updater` instances are called on each period to refresh records. Contexts then emit buffered records to their sink. `remove()` deletes rows matching the current tag set. The docs state that concurrent `update()` calls from different record instances with the same tags are safe, but sharing one `MetricsRecord` instance concurrently is not.

Network topology flow models locality decisions. Rack resolvers map host names to rack paths; `NetworkTopology` stores those nodes in a tree; block-placement and read-path code can query distance, same-rack status, random candidates within or outside a scope, available node counts after exclusions, and reorder replicas to prefer local host, local rack, then random fallback. Node locations are path-like strings with normalized root separators.

Socket flow is deliberately wrapped. Hadoop socket factories may create sockets with channels, and `NetUtils` requires callers to use its stream helpers rather than direct `Socket.getInputStream()`/`getOutputStream()` so Hadoop-specific timeout behavior applies. The selector-based `connect` path exists to avoid uncontrolled thread-local selector allocation in the JDK. `SocketInputStream` and `SocketOutputStream` expose readiness waits and close/open semantics around selectable channels.

Record I/O flow is schema-driven by caller convention. Binary input/output methods ignore or use tags depending on the implementation but preserve the same primitive, buffer, record, vector, and map event sequence expected by generated record classes. Vectors/maps return or consume an `Index` abstraction so readers can iterate serialized collections.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent compatibility state. Downstream tooling uses it to compare Hadoop 0.20.2 public API against other versions. Method signatures, exception declarations, deprecation strings, field visibility, synchronization flags, and public Javadoc contracts are all observable compatibility data.

TFile persists keys, values, block compression, comparator metadata, version data, metadata blocks, variable-length integers, and strings into an `FSDataOutputStream`. The writer does not close the underlying stream on `close()`, which makes stream ownership an external contract. Comparator names are persisted or embedded enough to affect sorted lookup behavior, including the language-independent `memcmp` comparator and Java `jclass:` raw comparator syntax.

Retry proxies maintain policy configuration in memory and can preserve failure behavior across service clients. The main persistent effect is indirect: retry policy decisions determine whether external operations are repeated, which can amplify non-idempotent side effects if callers apply retry to unsafe methods.

Serialization persists object data to stream bytes. `WritableSerialization` affects Hadoop wire and file formats for `Writable` implementations, while Java serialization preserves Java-specific serialized form. Factory configuration controls which implementation handles each class, so changing the configured serialization list can alter bytes on disk or over the wire.

IPC state includes open socket connections, handler threads, call queues, listener addresses, protocol versions, user credentials, remote exception XML, and metrics. `Server.HEADER` and `CURRENT_VERSION` represent wire protocol compatibility. `RemoteException` persists remote class names and messages across the RPC boundary and in XML form.

Metrics state is buffered by context and record name/tag set until periodic emission. `ContextFactory` persists configuration by reading `hadoop-metrics.properties` from the classpath into attributes. `FileContext` writes metric records to a configured file; `GangliaContext` sends them to external Ganglia infrastructure; `EventCounter` accumulates log-level counts; JMX registration exposes live metric state through MBeans.

Network state includes static host resolutions, DNS/rack mapping caches, network topology tree nodes and counts, socket factory configuration, SOCKS proxy configuration, and live socket/channel readiness state. `NetUtils.addStaticResolution` mutates a process-global resolution table commonly used by tests. `NetworkTopology.add/remove` mutates cluster topology and rack/leaf counters used by placement logic.

Record I/O state consists of binary stream position and mutable record objects. `BinaryRecordInput.get` and `BinaryRecordOutput.get` return thread-local wrappers, which preserve per-thread adapter state while reusing objects. `Buffer.set(byte[])` can take ownership of a supplied byte array, while `copy(byte[], int, int)` replaces contents with a copied range; callers observing `get()` must respect `getCount()`.

## Dependencies and Integration Points

TFile APIs integrate with `org.apache.hadoop.fs.FSDataOutputStream`, `org.apache.hadoop.conf.Configuration`, `java.io.DataInput/DataOutput/DataInputStream/DataOutputStream`, `Closeable`, compression algorithms advertised by `TFile`, `RawComparable`, Java raw comparators, and Hadoop `WritableComparator`-style comparator classes.

Retry APIs depend on Java dynamic proxy patterns, exception types, method-specific policy maps, and remote exception class-name mapping. They are integration points for resilient HDFS, MapReduce, and RPC clients that need retry semantics without embedding retry loops in every call site.

Serialization APIs depend on Hadoop `Writable`, Java `Serializable`, `Configuration`, stream classes, and byte-range comparators. They connect file formats, sort comparators, MapReduce shuffle/sort, and RPC parameter encoding to pluggable object serialization.

IPC/RPC depends on `Writable`, `VersionedProtocol`, `ConnectionHeader`, `UserGroupInformation`, `Subject`, `AuthorizationException`, `SocketFactory`, `InetSocketAddress`, Java reflection `Method`, Java networking, Apache Commons Logging, and XML/SAX helpers for remote exceptions. It also feeds `RpcMetrics` and the metrics/JMX subsystem.

Metrics depends on `hadoop-metrics.properties`, Java `Properties` semantics, sink-specific contexts, log4j appenders, JMX (`ObjectName`, `DynamicMBean`, `MBeanInfo`, `AttributeList`), and Ganglia/file backends. The SPI/util packages are shared by RPC metrics and by other Hadoop daemons reporting operational statistics.

Networking APIs depend on Java DNS/JNDI (`NamingException`), `NetworkInterface`/`InetAddress`/`Socket`/`ServerSocket`, Java NIO channels/selectors, Hadoop `Configuration`, Hadoop IPC `Server`, SOCKS `Proxy`, and configurable rack mapping implementations. `NetworkTopology` and `DNSToSwitchMapping` are core integration points for HDFS block placement and client read locality.

Record APIs depend on `RecordInput`, `RecordOutput`, `Record`, `Index`, `Buffer`, Java data streams, and collection types such as `ArrayList` and `TreeMap`. They integrate with generated Hadoop record classes used by older protocol and metadata code.

## Risks and Compatibility Notes

The chunk starts inside an existing `TFile.Reader.Scanner.Entry` class and ends inside `Buffer`, so the merge lane must combine adjacent chunks to reconstruct the complete per-file API report. This chunk still captures complete trailing contracts for the TFile entry and complete public definitions for most classes/interfaces it covers.

TFile has several high-risk contracts: one-shot value consumption, exact stream-append ordering, exact advertised lengths for key/value streams when length is not `-1`, sorted key order under configured comparator, metadata-block uniqueness, and the rule that append failure leaves the file inconsistent. Any change in variable-length integer encoding, version compatibility, comparator naming, or close behavior can break existing TFiles.

Retry policies can hide or multiply failures. Retrying non-idempotent operations, mishandling remote exception class names, or changing sleep/cap semantics can produce duplicate side effects, longer outages, or unexpected fail-fast behavior. Dynamic proxy method maps are also sensitive to exact `Method` identity.

Serialization changes are compatibility-sensitive because serialized bytes flow into files, shuffle data, and wire protocols. Deserializer-based comparators can execute arbitrary class deserialization during sort/compare, so malformed input, class evolution, or non-deterministic `compareTo` behavior can corrupt ordering or fail jobs.

IPC/RPC risks include wire-version compatibility, protocol version negotiation, UGI propagation, authorization bypass or over-rejection, server lifecycle races, connection leaks, thread shutdown behavior, queue backpressure, selector/file-descriptor exhaustion, remote exception unwrapping by class name, and deprecated overloads that must continue to behave for old callers.

Metrics risks center on concurrency, buffering, and external sinks. Misusing one `MetricsRecord` across threads violates the documented safety model. Missing `remove()` calls can keep stale rows alive forever. Bad context configuration can silently fall back to `NullContext` and discard data. MBean registration collisions or leaks can affect long-running daemons.

Network risks are operationally significant. DNS and static resolution affect daemon identity, RPC connection targets, and tests. Rack mapping must preserve one-to-one input/output order; bad mappings can degrade HDFS placement and recovery. `NetworkTopology` add/remove/count logic can skew locality and replication decisions. Socket timeout wrappers must handle channel and non-channel sockets consistently, otherwise RPC clients can hang or time out incorrectly.

Record I/O risks include binary compatibility of primitive/string/buffer encodings, correct vector/map counts, thread-local wrapper reuse, mutable `Buffer` aliasing through `set` and `get`, and partial chunk coverage of `Buffer` methods beyond `getCapacity()`.

## Test Signals

JDiff-level validation should confirm this XML range remains well formed when merged with adjacent chunks and preserves all public packages, classes, interfaces, constructors, fields, methods, parameter types, declared exceptions, visibility, static/final/abstract/synchronized/native flags, deprecation text, and Javadoc contracts.

TFile tests should cover one-shot value access, `getValue` with offsets, value-stream consumption, `isValueLengthKnown` for small, chunked, and advertised values, byte-array and `RawComparable` key comparison, sorted and unsorted writer modes, key/value stream append ordering, exact length enforcement, metadata block uniqueness, no key/value appends after metadata blocks, writer `close()` idempotence, and variable-length integer/string/version round trips.

Retry tests should cover fixed-count, fixed-time, proportional, exponential, forever, try-once-fail, try-once-dont-fail, Java exception mapping, remote exception mapping, method-specific proxy policies, retry count/failover count propagation, sleep caps, and interruption behavior.

Serialization tests should cover factory selection from configuration, Writable and Java serialization round trips, serializer/deserializer open/close enforcement, null or incompatible class handling, byte-range comparator ordering, deserialization failures during comparison, and stable behavior across repeated factory lookups.

IPC/RPC tests should cover raw `Client.call` single and parallel calls, deprecated overload compatibility, UGI credential propagation, ping interval configuration, proxy creation/stop, protocol version mismatch reporting, server start/stop/join lifecycle, bind error diagnostics, wildcard listener connect address conversion, remote address/IP thread-local context, authorization success/failure, remote exception XML round trips, call queue/open connection metrics, and wire header/current version preservation.

Metrics tests should cover `ContextFactory` singleton creation from `hadoop-metrics.properties`, attribute set/remove/list, default `NullContext`, configured context class instantiation, monitoring start/stop/close, updater registration/unregistration, record tag/metric set and increment overloads, atomic update behavior with separate record instances, row removal semantics, file sink emission/flush, Ganglia emission formatting, JVM/log4j event counters, composite fan-out, MBean registration/unregistration, registry add/get/list behavior, interval counters, rates, min/max reset, and no-op contexts.

Network tests should cover DNS lookup fallbacks, interface IP/host discovery, static resolution add/get/list, socket factory configuration including default and SOCKS factories, socket address parsing for host and URI forms, old/new server address configuration migration, wildcard listener connect address, channel and non-channel stream wrappers, read/write timeout behavior, selector-based connect timeout, host normalization, rack resolver one-to-one mapping, cache hits/misses, script mapping configuration, topology add/remove/contains/getNode/counts, distance and same-rack errors, random choice scopes including `~`, excluded-node counts, pseudo-sort locality ordering, and `NodeBase` path normalization.

Record I/O tests should cover binary primitive/string/buffer round trips, thread-local `BinaryRecordInput.get`/`BinaryRecordOutput.get` reuse per thread, record/vector/map start/end sequencing, collection count iteration through `Index`, `Buffer` empty/array/range constructors, aliasing behavior of `set`, copying behavior of `copy`, `getCount`, `getCapacity`, and compatibility with generated legacy record classes.

### subset-b-007333: lines 25048-31378

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 25048-31378

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.20.2, not implementation source. It records package, class, interface, constructor, method, field, inheritance, implemented-interface, visibility, static/final/abstract/synchronized/native, deprecation, exception, parameter, and Javadoc metadata. Behavioral notes below are therefore based on the public signatures and embedded docs in this XML.

The range begins inside `org.apache.hadoop.record.Buffer` and ends inside `org.apache.hadoop.util.StringUtils.TraditionalBinaryPrefix`; adjacent chunks must provide the missing class boundaries. Within this range, the API surface covers Hadoop Record I/O runtime interfaces and codecs, the record compiler and generated parser classes, record metadata type descriptors, early security and service-authorization APIs, and common utility classes used across Hadoop core.

## Purpose and Major API Surface

The `org.apache.hadoop.record` block describes the old Hadoop Record I/O layer. `Buffer` is a mutable byte sequence with explicit count/capacity management, append, reset, truncate, string conversion, comparison, equality, hashing, and cloning. `Record` is the abstract generated-record base implementing `WritableComparable` and `Cloneable`; generated records must implement tagged `serialize(RecordOutput,String)`, `deserialize(RecordInput,String)`, and `compareTo(Object)`, while the base exposes untagged serialize/deserialize plus `Writable` `write(DataOutput)` and `readFields(DataInput)`.

`RecordInput` and `RecordOutput` define the format-neutral primitive, string, buffer, record, vector, and map read/write contract. `CsvRecordInput`/`CsvRecordOutput` and `XmlRecordInput`/`XmlRecordOutput` are concrete stream-backed implementations. `Index` is the deserialization cursor returned by vector/map starts, using `done()` and `incr()` to drive collection reads. `RecordComparator` extends `WritableComparator` and lets record classes register custom raw-byte comparators through `define(Class, RecordComparator)`.

`org.apache.hadoop.record.Utils` provides low-level Record I/O helpers for float/double encoding, variable-length integer/long reads and writes over `DataInput`, `DataOutput`, `InputStream`, and `OutputStream`, byte comparison, VInt size calculation, and a public `hexchars` table. These APIs are format-compatibility points because generated records and binary encodings depend on the exact wire representation.

The `org.apache.hadoop.record.compiler` block records the Record Compiler model. `JType` is the abstract base for Record I/O types; concrete descriptors include primitive types (`JBoolean`, `JByte`, `JFloat`, `JDouble`, `JInt`, `JLong`) and compound/string/buffer/record/container types (`JString`, `JBuffer`, `JRecord`, `JVector`, `JMap`). `JField` wraps a field name/type, `JFile` represents a Record DDL file with includes and record definitions and exposes `genCode(language,destDir,options)`, `CodeBuffer` handles generated-code indentation, and `Consts` publishes compiler variable/name constants.

`RccTask` is an Ant task for invoking the Hadoop record compiler against a single file or nested `FileSet`, with setters for language (`java`/`c++`), source file, destination directory, and fail-on-error behavior. The generated `Rcc` parser exposes command-line `main`, `usage`, `driver`, grammar productions (`Input`, `Include`, `Module`, `Record`, `Field`, `Type`, `Map`, `Vector`), parser reinitialization, token access, parse-exception generation, and tracing toggles. The JavaCC support classes `RccConstants`, `RccTokenManager`, `SimpleCharStream`, `Token`, `ParseException`, and `TokenMgrError` publish token IDs, lexical states, token images, line/column tracking, parser errors, and token-manager errors.

The `org.apache.hadoop.record.meta` block models runtime type information. `TypeID` provides singleton constants for basic types and byte-valued `RIOType` IDs for bool, buffer, byte, double, float, int, long, map, string, struct, and vector. `FieldTypeInfo` pairs a field name with a `TypeID`. `MapTypeID`, `VectorTypeID`, and `StructTypeID` describe nested container and struct shapes. `RecordTypeInfo` is itself a `Record` that can serialize/deserialize record schema metadata, set/get its record name, add fields, enumerate fields, and retrieve one-level nested struct info. `record.meta.Utils.skip` consumes a value from a `RecordInput` according to a `TypeID`.

The `org.apache.hadoop.security` block is an early user/group and policy surface. `AccessControlException` bridges to `org.apache.hadoop.fs.permission.AccessControlException` and has a no-arg constructor for IPC `RemoteException` unwrapping. `User` and `Group` implement `Principal`-style identity with name, equality, hash code, and string conversion. `UserGroupInformation` exposes current UGI set/get helpers, current user mutation, login, and stream reads. `UnixUserGroupInformation` extends it with user/group constructors, immutable creation, group/user accessors, `Writable` read/write, save/read from `Configuration`, Unix/config-based login, equality, hash code, `toString`, and constants such as default username/group and `UGI_PROPERTY_NAME`.

`SecurityUtil` owns global Hadoop `Policy` access and can build a `Subject` from a UGI. Its nested `AccessControlList` parses ACL strings of users followed by groups, supports wildcard access through `WILDCARD_ACL_VALUE`, and exposes `allAllowed`, `getUsers`, and `getGroups`. The `org.apache.hadoop.security.authorize` APIs define service-level authorization: `AuthorizationException`, `ConfiguredPolicy` over `Configuration` and `PolicyProvider`, `ConnectionPermission` for protocol access, abstract `PolicyProvider`, `Service`, refresh protocol `RefreshAuthorizationPolicyProtocol`, and static `ServiceAuthorizationManager.authorize(Subject, Class)`.

The `org.apache.hadoop.util` block includes broad core utilities. It covers cyclic map iteration, daemon threads, DFS data checksums, disk checks, generic command-line option parsing, Java generics helpers, indexed sort contracts and heap/quick sort implementations, host include/exclude file loading, line reading, memory calculator plugins, native-code loading flags, platform naming, jar main-class printing and job-jar execution, priority queue, procfs process-tree management, command driver dispatch, progress trees, reflection/copy/thread-dump helpers, servlet HTML helpers, shell command execution, and string/number/time/URI/path escaping and formatting utilities.

## Control Flow and Behavioral Contracts

Record serialization follows a structured lifecycle: writers call `startRecord`, primitive/container writes, nested `startVector`/`startMap` pairs, and `endRecord`; readers mirror that flow through `RecordInput` and collection `Index` cursors. Generated `Record.write(DataOutput)` and `readFields(DataInput)` bridge Record I/O to Hadoop `Writable` serialization. CSV/XML implementations are stream-backed tagged formats, while the utilities provide shared variable-length numeric and byte-comparison behavior.

Record compiler flow starts with `Rcc.driver` or the Ant `RccTask`, parses `.jr` inputs into `JFile`, `JRecord`, `JField`, and `JType` objects, then calls `JFile.genCode` for the target language. JavaCC parser flow uses `SimpleCharStream` for buffering and line/column state, `RccTokenManager` for lexical states and token production, `Rcc` grammar methods for recursive descent parsing, and `ParseException`/`TokenMgrError` for syntax and lexical diagnostics.

Record metadata flow lets a record carry schema/type descriptors through the same `Record` serialization interfaces used for data. `RecordTypeInfo.serialize` writes the record name and field type information; `deserialize` rebuilds it. `record.meta.Utils.skip` can consume unknown or unwanted fields by dispatching on `TypeID`, which is critical for compatibility filtering.

Security control flow is policy-based. Code installs or retrieves the global Hadoop `Policy` through `SecurityUtil`; services advertise a config key and required `ConnectionPermission` through `Service` and `PolicyProvider`; `ConfiguredPolicy` evaluates permissions from configuration-backed ACLs; `ServiceAuthorizationManager.authorize` checks a `Subject` against the protocol class. The refresh protocol exposes `refreshServiceAcl()` so long-running services can reload authorization policy.

UGI control flow supports several sources: direct constructor input, immutable array creation, `Configuration` string properties, current Unix login, and stream serialization. The docs explicitly describe caching by user name for `UnixUserGroupInformation.readFromConf` and `login`, and a fallback to default username/group when Unix username/group lookup fails due to environment issues such as LDAP exceptions.

Utility flow is mostly single-purpose. `DataChecksum` is constructed from a type/bytes-per-checksum pair, a header byte array, or a `DataInputStream`, then receives `update`, writes/compares checksum values, optionally resets, and exposes checksum header/value metadata. `LineReader` consumes lines terminated by LF, CR, CRLF, or EOF with max length and max byte-consumption controls. `Shell` subclasses provide command arrays and parsing, while `ShellCommandExecutor` stores small command output without custom parsing. `QuickSort` sorts via `IndexedSortable` and switches to `HeapSort` when recursion depth exceeds `2 * ceil(log(n))`.

## State, Persistence, and Side Effects

The XML file is persistent API metadata used for compatibility checking. It does not persist runtime state itself, but it captures externally observable signatures and docs that downstream source/binary compatibility tools consume.

Record I/O persists bytes through Hadoop writable streams, CSV/XML stream encodings, and variable-length integer/long helpers. `Buffer` exposes its backing array and count/capacity distinction, so callers can observe and depend on storage semantics. `RecordTypeInfo`, `TypeID`, `MapTypeID`, `VectorTypeID`, and `StructTypeID` persist schema metadata and therefore affect forward/backward compatibility of generated record data.

Parser/compiler state includes source file paths, include lists, generated output directories, JavaCC token streams, lexical states, line/column arrays, token linked lists, and parse-error fields. Ant execution and `JFile.genCode` have filesystem side effects by generating Java or C++ source files.

Security state includes global JVM `Policy`, `Subject` contents, ACL user/group sets, UGI caches implied by the docs, current UGI/current user, and configuration properties carrying serialized UGI and service ACLs. `UnixUserGroupInformation.write/readFields` persists UGI in a string-marked writable format; `saveToConf` stores comma-separated user/group data in `Configuration`.

Common utilities have notable external effects. `DiskChecker` creates/checks directories. `HostsFileReader` refreshes include/exclude host sets from files and synchronizes file-name updates. `RunJar.unJar` extracts archives and `RunJar.main` invokes job-jar main classes. `ProcfsBasedProcessTree.destroy` terminates process trees after configurable sleep-before-SIGKILL behavior and reads pid/procfs state. `Shell` and `ShellCommandExecutor` spawn subprocesses with optional environment and working directory.

In-memory utility state includes `DataChecksum` current checksum value, `PriorityQueue` heap contents, `Progress` tree phase/status/progress values, `ReflectionUtils` instance/copy buffers and thread dump throttling, and `StringUtils` static constants for comma escaping. Synchronized APIs are explicitly recorded on `HostsFileReader.refresh/setIncludesFile/setExcludesFile/updateFileNames`, several `Progress` methods, and `StringUtils.limitDecimalTo2`, marking concurrency-sensitive contracts.

## Dependencies and Integration Points

Record I/O integrates with `org.apache.hadoop.io.WritableComparable`, `WritableComparator`, `DataInput`, `DataOutput`, Java streams, `ArrayList`, `TreeMap`, and generated Hadoop record classes. CSV/XML formats integrate with `InputStream`/`OutputStream`; compiler classes integrate with Ant (`Task`, `FileSet`, `BuildException`) and JavaCC-generated parser structures.

Security APIs integrate with Java security (`Policy`, `Permission`, `Principal`, `Subject`, `AccessControlException`), Hadoop `Configuration`, Hadoop IPC (`VersionedProtocol`, remote exception unwrapping), commons logging through nearby utilities, and service protocol `Class` objects. Authorization configuration flows through `PolicyProvider.POLICY_PROVIDER_CONFIG`, `ConfiguredPolicy.HADOOP_POLICY_FILE`, and `ServiceAuthorizationManager.SERVICE_AUTHORIZATION_CONFIG`.

Utility APIs integrate with `org.apache.hadoop.conf.Configuration`/`Configured`, `org.apache.hadoop.fs.Path`, `org.apache.hadoop.io.Text` and `Writable`, `Progressable`, `Tool`/command drivers, servlet request/response APIs, Commons CLI, Commons Logging, Java `Process`, `NavigableMap`, `Iterator`, `Comparator`, `Checksum`, `CRC32`, `Jar`/manifest behavior, `/proc` on Linux, native-library loading, and filesystem permissions/ownership commands.

## Risks and Compatibility Notes

The chunk boundaries are partial. It starts after the `Buffer` class header and earlier `Buffer` constructors/methods, and ends before the rest of `StringUtils.TraditionalBinaryPrefix`; the merge lane needs adjacent chunks to reconstruct the full classes.

Record I/O is highly compatibility-sensitive. Changes to variable-length integer encoding, buffer comparison/equality, record field order, CSV/XML tags, collection index semantics, or `Record.write/readFields` bridging would break persisted data, generated code, or cross-version communication.

The record compiler/parser exposes many generated JavaCC internals as public/protected fields and methods. Token IDs, token image order, lexical-state names, parse-error messages, line/column accounting, and grammar method names can be observed by tests or callers even though they are tool internals. Re-generating the parser with a different JavaCC version could alter public API or diagnostics.

UGI and ACL formats are legacy public contracts. Comma-separated user/group strings, the string marker used by `UnixUserGroupInformation.write`, default fallback user/group constants, ACL wildcard behavior, and service authorization config keys may appear in job configs, service configs, and serialized RPC data. Incorrect parsing or mutation can deny legitimate users or grant broad access.

Service authorization has security impact. `ConfiguredPolicy.implies`, `ConnectionPermission.implies`, `ServiceAuthorizationManager.authorize`, and refresh behavior must preserve protocol-to-permission mapping and group membership evaluation. Fail-open behavior, stale policy caching, or bad wildcard handling would be severe.

Utility classes touch correctness and platform behavior. `DataChecksum` header layout and null-vs-CRC behavior are DFS data-transfer contracts. `DiskChecker` races with other processes creating directories. `LineReader` controls split-boundary and line-length behavior used by MapReduce readers. `ProcfsBasedProcessTree` and `Shell` can kill or spawn OS processes, and command output buffering is documented as suitable only for small outputs. `StringUtils` escaping/splitting must round-trip configuration values containing separators and escape characters.

## Test Signals

JDiff-level validation should assert the XML remains well formed for this range and preserves all class/interface names, package boundaries, inheritance, implemented interfaces, constructor and method signatures, parameter types, declared exceptions, fields, visibility, abstract/static/final/synchronized/native flags, deprecation state, and Javadocs important to public behavior.

Record I/O tests should cover `Buffer` set/copy/append/reset/truncate/capacity/count semantics, backing-array exposure, comparison/equality/hash code, charset string conversion, clone behavior, CSV/XML primitive and collection round trips, `Index.done/incr` loops, `Record.write/readFields` bridging, `RecordComparator.define/compare`, variable-length integer and long encoding across boundary values, float/double helpers, and byte comparison ordering.

Compiler/parser tests should cover `RccTask` file and fileset execution, language/destdir/failonerror settings, `JFile.genCode` for Java and C++ outputs, include handling, primitive/container/record type parsing, parser `ReInit` overloads, expected parse-error messages with line/column data, token-manager lexical errors, `SimpleCharStream` buffer expansion/backtracking/tab handling, and token linked-list/special-token behavior.

Record metadata tests should cover basic `TypeID` singleton equality/hash codes and byte values, map/vector/struct equality and accessors, `FieldTypeInfo` equality, `RecordTypeInfo` add/get/nested lookup, schema serialize/deserialize round trips, `compareTo` exceptional/non-sorting behavior, and `record.meta.Utils.skip` for every basic and compound `TypeID`.

Security tests should cover `AccessControlException` constructors and remote-unwrapping compatibility, `User`/`Group` principal equality, ACL parsing for users-only, groups-only, users-plus-groups, empty strings, whitespace, duplicates, and wildcard, `SecurityUtil.setPolicy/getPolicy/getSubject`, UGI constructor validation, immutable UGI behavior, UGI writable and config round trips, Unix login fallback behavior, current UGI/current user setters, and cached UGI reuse.

Authorization tests should cover `ConnectionPermission` equality/hash/implies/actions, `Service` service-key and permission creation, `PolicyProvider` service arrays and default provider, `ConfiguredPolicy.implies/getPermissions/refresh` against configured ACLs, disabled/enabled `SERVICE_AUTHORIZATION_CONFIG`, `ServiceAuthorizationManager.authorize` for allowed and denied users/groups, and `RefreshAuthorizationPolicyProtocol.versionID` plus `refreshServiceAcl` error propagation.

Utility tests should cover `DataChecksum` construction from type/header/stream, null checksum behavior, CRC32 values, header length, write/compare/reset/update variants, `DiskChecker.mkdirsWithExistsCheck` under concurrent parent creation, `checkDir` permission/error/out-of-space cases, generic option parsing for `-conf`, `-D`, `-fs`, `-jt`, `-files`, `-libjars`, and `-archives`, host include/exclude refresh and synchronized filename updates, sort correctness/progress callbacks for heap and quick sort, and `LineReader` LF/CR/CRLF/EOF/max-length/max-consumption behavior.

Additional utility tests should cover memory calculator plugin selection/configuration, native loader flags, platform names, jar main-class discovery and `RunJar` extraction/execution, `PriorityQueue` ordering and capacity behavior, procfs process tree alive/destroy/cumulative memory/pid-file parsing, `ProgramDriver` dispatch and usage failures, `Progress` tree phase math/status/concurrency, reflection configuration/new-instance/copy/thread-info logging, servlet HTML helpers and parameter trimming, shell command execution/exit codes/environment/working directory/quoting, and `StringUtils` exception stringification, hostname simplification, human-readable sizes, percentages, hex conversion, URI/path conversion, time formatting, comma split/escape/unescape, HTML escaping, byte descriptions, and decimal limiting.

### subset-b-007334: lines 31379-37729

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 31379-37729

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.20.2. It records API metadata, not Java method bodies: packages, classes, interfaces, inheritance, implemented interfaces, constructors, methods, parameter and exception types, fields, visibility/static/final/synchronized flags, deprecation text, and embedded Javadoc.

The range begins inside `org.apache.hadoop.util.StringUtils.TraditionalBinaryPrefix`, covers utility classes, Bloom filter and hash APIs, and then a large early section of the legacy `org.apache.hadoop.mapred` API through part of `JobHistory.ReduceAttempt`. Runtime behavior below is inferred from signatures and Javadocs. The merge lane should reconcile the partial start and partial end with adjacent chunks.

## Purpose and Major API Surface

The visible tail of `StringUtils.TraditionalBinaryPrefix` exposes binary-size parsing: `valueOf(char)`, `string2long(String)`, enum values `KILO` through `EXA`, and public final fields `value` and `symbol`. Its purpose is converting strings such as `891g` into long byte counts using case-insensitive 1024-based suffixes.

`Tool` and `ToolRunner` define Hadoop's generic command-line execution contract. `Tool` extends `Configurable` and exposes `run(String[])`. `ToolRunner.run(Configuration, Tool, String[])` and `run(Tool, String[])` parse generic Hadoop options through `GenericOptionsParser`, install the processed `Configuration` on the tool, and return the tool exit code. `printGenericCommandUsage(PrintStream)` emits generic option help.

`UTF8ByteArrayUtils` is a byte-scanning helper for UTF-8 encoded byte arrays. It provides `findByte`, `findBytes`, and two `findNthByte` overloads. These are byte-position utilities, so callers get offsets into the original byte array rather than decoded character indexes.

`VersionInfo` exposes build metadata: Hadoop version, source revision, build date, build user, source URL, combined build version, and a `main` method. `XMLUtils.transform(InputStream, InputStream, Writer)` is a small XSLT wrapper that can throw `TransformerConfigurationException` and `TransformerException`.

The `org.apache.hadoop.util.bloom` package defines Hadoop's probabilistic membership filters. `Filter` is the abstract `Writable` base with protected state `vectorSize`, `HashFunction hash`, `nbHash`, and `hashType`; abstract membership/boolean operations `add(Key)`, `membershipTest(Key)`, `and(Filter)`, `or(Filter)`, `xor(Filter)`, and `not()`; bulk `add` overloads for `List`, `Collection`, and `Key[]`; plus `write` and `readFields`.

Concrete Bloom types include `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, and `RetouchedBloomFilter`. `BloomFilter` is the standard false-positive/no-false-negative bit-vector form and adds set operations, `membershipTest`, `getVectorSize`, `toString`, and `Writable` serialization. `CountingBloomFilter` is final and adds `delete(Key)` and `approximateCount(Key)`, with the documented 4-bit bucket limit where inserting the same key more than 15 times overflows and increases error. `DynamicBloomFilter` adds the `nr` threshold constructor parameter and grows by adding filter rows when active rows are saturated. `RetouchedBloomFilter` is final, implements `RemoveScheme`, records false-positive keys through `addFalsePositive` overloads, and performs `selectiveClearing(Key, short)` to trade selected false positives for possible false negatives.

`Key` is a `WritableComparable` wrapper around a byte-array value and a double weight. It supports default/readFields construction, explicit value and value-plus-weight construction, `set`, byte and weight accessors, weight increments, equality/hash code, serialization, and `compareTo(Key)`. `HashFunction` maps a `Key` to multiple vector positions. `RemoveScheme` defines public short constants `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO` for retouched Bloom clearing strategies.

The `org.apache.hadoop.util.hash` package provides non-cryptographic hashes. `Hash` is the abstract common API with constants `INVALID_HASH`, `JENKINS_HASH`, and `MURMUR_HASH`; parsing from names or `Configuration`; singleton lookup by type or configuration; convenience `hash(byte[])` and `hash(byte[], int)` overloads; and abstract `hash(byte[], int, int)`. `JenkinsHash` and `MurmurHash` implement the concrete algorithms and singleton accessors; `JenkinsHash.main(String[])` computes a file hash for diagnostics.

The `org.apache.hadoop.mapred` package section starts with cluster and counter data. `ClusterStatus` is `Writable` status for task tracker counts/names, blacklist counts, tasktracker expiry interval, running and maximum map/reduce slots, `JobTracker.State`, and JobTracker heap memory usage. `Counters` is the deprecated old-API counter container implementing `Writable` and `Iterable`; it manages groups and counters by enum or string names, increments individual or all counters, computes `sum`, serializes binary counter groups, logs counters, renders compact and escaped compact strings, parses escaped compact strings, and implements synchronized equality/hash code. Nested `Counters.Counter` extends `org.apache.hadoop.mapreduce.Counter`; nested `Counters.Group` is a `Writable`/`Iterable` group with raw and display names, counter lookup/creation, compact stringification, serialization, and synchronized iteration.

The file input/output API surface includes `DefaultJobHistoryParser`, file-related `IOException` subclasses, `FileInputFormat`, `FileOutputCommitter`, `FileOutputFormat`, `FileSplit`, `InputFormat`, and `InputSplit`. `FileInputFormat` is the old-API base for file-backed input formats, with input-path/filter configuration, `listStatus`, split planning, split sizing, block index lookup, host locality calculation, and abstract `getRecordReader`. `FileOutputCommitter` implements job/task setup, task commit/abort, job cleanup, and `needsTaskCommit` for files under `mapred.output.dir`. `FileOutputFormat` configures output compression/codecs, validates output specs, stores output paths, computes task work paths, and generates task-specific names. `FileSplit` bridges old and new input split APIs and serializes a path/start/length/host-location tuple. `InputFormat` and `InputSplit` define the old MapReduce split planning and record-reader contracts.

`InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` signal validation failures. `InvalidInputException` is notable because it wraps an uncopied list of problems, exposes it through `getProblems`, and concatenates problem messages in `getMessage`. `IsolationRunner.main` runs a single task from a task directory for debugging or isolation.

`JobClient` is the old-API client facade for connecting to JobTracker, staging and submitting jobs, retrieving `RunningJob` handles, task reports, cluster status, all or incomplete jobs, queues, and system directories, then monitoring or running jobs. It implements `MRConstants` and `Tool`, has constructors for default and explicit tracker connections, synchronized `close` and `getFs`, submission overloads for a job file and `JobConf`, `submitJobInternal`, `isJobDirValid`, task display filtering, `runJob`, `monitorAndPrintJob`, `run(String[])`, and `main`. Nested `TaskStatusFilter` enum values are `NONE`, `KILLED`, `FAILED`, `SUCCEEDED`, and `ALL`.

`JobConf` is the central old-API job configuration type, extending `Configuration` but deprecated in favor of `Configuration`. It exposes constructors from classes, existing configurations, XML files, paths, and default-resource loading flags. The chunk covers setters/getters for jar selection, local dirs and cleanup, user, failed-task file retention, working directory, task JVM reuse, input/output format classes, output committer, output and map-output compression, map and final key/value classes, comparators and grouping comparator, old/new mapper/reducer toggles, mapper/map runner/partitioner/reducer/combiner classes, speculative execution, map/reduce task counts, max attempts, job name, session id, per-tracker failure thresholds, allowed task failure percentages, priority, profiling, debug scripts, job-end notification URI, job local dir, memory limits, queue name, and memory-related public constants.

`JobConfigurable` supplies `configure(JobConf)`. `JobContext` bridges to `org.apache.hadoop.mapreduce.JobContext` while exposing old `JobConf` and a `Progressable`. `JobEndNotifier` manages async or local job-completion notifications through `startNotifier`, `stopNotifier`, `registerNotification`, and `localRunnerNotification`.

`JobHistory` and nested types define append-mode job history logging and parsing. `JobHistory.init` initializes history with JobTracker host/start time, `parseHistoryFromFS` streams records to a `Listener`, `isDisableHistory` and `setDisableHistory` control logging, and `getTaskLogsUrl` builds task log URLs when tracker, port, and attempt id are available. `HistoryCleaner` deletes old history files and stale master-index entries. `JobInfo` manages task maps, local job-file path lookup, URL encoding/decoding of history file paths/names, user and history path lookup, recovery selection between duplicate recovery files, and static logging of submitted, initialized, started, finished, failed, killed, priority, and submit/launch info records. `Keys` enumerates the history key namespace, `Listener.handle(RecordTypes, Map)` is the parse callback, `MapAttempt` logs map attempt start/finish/failure/kill events, `RecordTypes` enumerates line record tags, and the chunk ends inside `ReduceAttempt` logging methods.

## Control Flow and Behavioral Contracts

Generic command-line control flow is `ToolRunner` first parsing Hadoop generic options into a `Configuration`, then installing that configuration into the target `Tool`, then invoking `Tool.run`. Application-specific arguments are passed along after generic parsing.

Bloom filter control flow is hash-driven: a `Key` is converted by `HashFunction` into `nbHash` vector positions bounded by `vectorSize`; `add` mutates the filter state at those positions; `membershipTest` checks those positions; boolean operations mutate the receiver in place. Counting filters add count increments/decrements and approximate count queries. Dynamic filters insert into an active row until its threshold is reached, then create a new row. Retouched filters record known false positives and selectively clear bits based on a `RemoveScheme`.

Hash selection flows through configuration or symbolic constants. Callers parse `"jenkins"` or `"murmur"` to a type, get a singleton `Hash`, and then hash byte prefixes with a seed. The Javadocs explicitly position Jenkins and Murmur as non-cryptographic lookup hashes.

File input flow is old MapReduce's standard path: set input paths and optional `PathFilter` on `JobConf`; `FileInputFormat.listStatus` validates and expands inputs; `getSplits` uses desired split count, minimum split size, block size, file splittability, and block locations; `getSplitHosts` ranks hosts/racks by byte contribution; the framework assigns each `InputSplit` to a mapper and creates a `RecordReader` for records. `InputFormat` documents logical splits, not physical file splitting, so `RecordReader` implementations must respect record boundaries.

File output flow starts by setting output path and compression in `JobConf`; `FileOutputFormat.checkOutputSpecs` validates output before submission; tasks write to task-specific work output paths; `FileOutputCommitter` promotes successful attempt output and aborts failed attempt output. `TEMP_DIR_NAME` and task unique names are part of the compatibility surface for speculative execution and cleanup behavior.

Job submission control flow in `JobClient` is: connect to the configured JobTracker, get a filesystem handle, validate input/output specs, compute input splits, account for `DistributedCache`, copy the job jar and XML config to the distributed system directory, submit to JobTracker, and optionally monitor. `runJob` blocks until completion; `submitJob` returns a `RunningJob` for polling; job-end notification URI offers callback-style completion.

`JobConf` is the dataflow source for most runtime choices. Its class-valued settings drive reflection for input/output formats, mappers, reducers, combiners, partitioners, comparators, compression codecs, and committers. Its scalar settings drive task counts, speculative execution, retries, failure tolerances, profiling, debug scripts, memory limits, queue placement, and notification behavior.

Job history control flow is append-and-parse. Runtime code logs job, task, map-attempt, and reduce-attempt events as line records of a typed tag plus key/value pairs. Finished, failed, and killed job events close the per-job history log. Later parsers either populate a `JobInfo` object model or stream parsed records into `Listener.handle`.

## State, Persistence, and Side Effects

This XML snapshot itself is persistent compatibility data used by JDiff; it has no runtime state. The APIs it describes are stateful and persistence-sensitive.

`Filter`, `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, `RetouchedBloomFilter`, and `Key` implement `Writable` serialization. Their persisted fields include vector size, hash configuration, vector/count matrix contents, false-positive metadata, key bytes, and key weight. Changing serialization order or hash behavior would invalidate filters written by Hadoop 0.20.2 code.

`Counters`, `Counters.Group`, `ClusterStatus`, and `FileSplit` also expose `Writable` contracts. `Counters` has both binary and textual escaped compact encodings used by MapReduce status, logs, and history. Several counter methods are synchronized, so the old implementation promised some thread-safety for mutation, iteration, and serialization.

`JobConf` persists job state as configuration keys and resources. Local-dir cleanup and `getLocalPath` have filesystem side effects. Debug scripts rely on `DistributedCache` localization and task log files. Memory limit constants and queue names affect scheduler and task-tracker behavior outside this class.

`FileInputFormat` and `FileOutputFormat` store paths, filters, compression flags/codecs, and output/work paths in `JobConf`. `FileOutputCommitter` mutates output directories, temporary directories, and task attempt output. Incorrect promotion or cleanup can corrupt distributed output.

`JobClient` owns a cluster connection and filesystem handle, stages job artifacts, submits jobs over RPC, and prints or monitors status. `ClusterStatus` mirrors distributed cluster state, including task tracker membership and blacklist state.

`JobHistory` persists append-only plain-text history files and a master index. `HistoryCleaner` deletes old history files and index entries. `JobInfo.recoverJobHistoryFile` resolves duplicate recovery files by choosing the oldest and ensuring only one remains. `JobEndNotifier` performs external notification side effects.

## Dependencies and Integration Points

The utility portion depends on `Configuration`, `Configurable`, `GenericOptionsParser`, Java streams/writers, XSLT transformer classes, and Hadoop's `Writable`/`WritableComparable`.

Bloom filters integrate with `org.apache.hadoop.util.hash.Hash`, `JenkinsHash`, and `MurmurHash`. They depend on deterministic non-cryptographic hashing for stable vector positions and on `DataInput`/`DataOutput` for persistence.

The old `mapred` APIs bridge heavily to the newer `org.apache.hadoop.mapreduce` package: `Counters.Counter`, `FileSplit`, `ID`, and `JobContext` extend or wrap new API classes while preserving old method signatures. Many types are deprecated but still define Hadoop 0.20.2 compatibility.

Filesystem integration uses `FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `PathFilter`, local files, distributed output directories, and history locations. Split locality integrates with `org.apache.hadoop.net.NetworkTopology`.

Job submission and cluster integration references `JobTracker`, `RunningJob`, `JobStatus`, `TaskReport`, `TaskAttemptID`, `TaskAttemptContext`, `OutputCommitter`, `OutputFormat`, `InputFormat`, `RecordReader`, `Reporter`, `DistributedCache`, `CompressionCodec`, `RawComparator`, `Partitioner`, `Mapper`, and `Reducer`.

History integration depends on `JobID`, `JobPriority`, `Counters`, task attempt ids, tracker names, HTTP ports, task logs, and record schemas represented by `JobHistory.Keys` and `RecordTypes`.

## Risks and Compatibility Notes

The range begins mid-class and ends mid-class. `TraditionalBinaryPrefix` and `JobHistory.ReduceAttempt` are incomplete here, so final per-file research should merge adjacent chunks before drawing complete conclusions about those classes.

Because this is a JDiff XML file, a behavioral change can be as small as a changed attribute: visibility, static/final flags, synchronized flags, exception lists, deprecation strings, enum constants, field names, or parameter types all affect generated API compatibility reports.

Bloom filters are sensitive to deterministic hashing, vector sizing, count overflow, and `Writable` wire format. The counting filter's documented 15-insertion overflow boundary is a correctness risk for callers treating it as an approximate count map. Retouched Bloom filters intentionally introduce false negatives; misuse of `RemoveScheme` can break standard Bloom assumptions.

Hash APIs are non-cryptographic by design. Using Jenkins or Murmur for security-sensitive identity, signatures, or adversarial collision defense would be wrong. Changing singleton behavior or configured hash names would alter Bloom filter compatibility.

File splitting risks include hidden or filtered inputs, zero-input validation, compressed non-splittable files, off-by-one block boundaries, min split size, block size, rack/host locality ranking, and record-reader responsibility for record boundaries.

Output commit risks are high around speculative execution, task attempt naming, temporary directory cleanup, and side-effect files. Any change to `FileOutputCommitter` or `FileOutputFormat` path conventions can cause duplicate output, lost output, or failed recovery.

`JobConf` has broad cross-component coupling. Changing a getter/setter's configuration key, default value, class-loading behavior, or deprecation-preserved old/new API toggle can affect job submission, task launch, scheduling, retries, debug scripts, profiling, memory enforcement, and queue routing.

`JobClient` and history APIs are distributed-system surfaces. Failures can come from filesystem staging, invalid configuration, JobTracker readiness, RPC/IO errors, queue lookup, incomplete recovery, malformed history records, or listener exceptions. History schema keys and record type names are especially compatibility-sensitive because external tools parse them.

## Test Signals

JDiff validation should confirm the full XML remains well formed and this range preserves all class/interface names, inheritance, implemented interfaces, method overloads, parameters, checked exceptions, fields, enum constants, deprecation text, and flags.

Utility tests should cover binary-prefix parsing including case-insensitive suffixes, negatives, trim behavior, overflow/invalid suffix handling, UTF-8 byte search offsets, nth-byte misses, `ToolRunner` generic-option parsing/config injection, `VersionInfo` getters, and `XMLUtils.transform` success and transformer failures.

Bloom/hash tests should cover `Writable` round trips for every filter and `Key`, bulk adds, membership positives and expected false-positive behavior, boolean operations mutating the receiver, counting add/delete/underflow/overflow and `approximateCount`, dynamic row growth at the `nr` threshold, retouched false-positive registration and every `RemoveScheme`, hash type parsing from names/configuration, singleton lookup, and deterministic Jenkins/Murmur hash outputs.

MapReduce serialization tests should cover `ClusterStatus`, `Counters`, `Counters.Group`, `Counters.Counter`, and `FileSplit` read/write compatibility, counter escaped compact round trips, malformed compact string parse errors, synchronized counter mutation, group display names, missing counters returning zero, and equality/hash code.

File input tests should cover path setters/adders/getters, comma-separated parsing, input filters, empty inputs, invalid file types, splitability overrides, compressed inputs, split sizing, block index selection, host/rack locality ranking, `InputSplit.getLength/getLocations`, and `RecordReader` boundary responsibilities.

File output tests should cover compression flags and codec classes, existing-output rejection, invalid output specs, task work path calculation, unique name generation, custom task output paths, `FileOutputCommitter` setup/commit/abort/cleanup, failed attempt cleanup, and speculative attempt collision cases.

JobClient and JobConf tests should verify default and explicit JobTracker connections, filesystem handle lifecycle, job directory validation, submit from file and `JobConf`, `submitJobInternal` exception paths, `RunningJob` lookup by `JobID` and deprecated string id, task report queries, task display filters, cluster status detail flags, queue queries, `runJob`, `monitorAndPrintJob`, CLI exit codes, and every major `JobConf` getter/setter pair.

Job history tests should write and parse representative submitted, initialized, running, finished, failed, killed, priority, map-attempt, and reduce-attempt records; validate `Keys` and `RecordTypes`; exercise listener streaming without retaining the full model; test task log URL construction with missing fields; encode/decode history filenames; recover duplicate history files; disable/enable history; and run cleaner behavior against old and current history entries.

### subset-b-007335: lines 37730-43882

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 37730-43882

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.20.2. It is XML API metadata, not Java implementation source. The range starts in the tail of `org.apache.hadoop.mapred.JobHistory.ReduceAttempt`, covers a large legacy `org.apache.hadoop.mapred` API span from task history and job identity through JobTracker/TaskTracker, record readers, old MapReduce contracts, sequence-file formats, skip-bad-record controls, task logs, and text formats, then continues into `org.apache.hadoop.mapred.jobcontrol` and ends inside `org.apache.hadoop.mapred.join.ArrayListBackedIterator`.

The XML records compatibility-visible structure: classes/interfaces, inheritance, implemented interfaces, methods, constructors, parameters, checked exceptions, public/protected fields, static/final/abstract/synchronized flags, deprecation state, and Javadoc. Control flow and persistence notes below are inferred from signatures and embedded documentation because method bodies are not present in the JDiff file.

## Purpose and Major API Surface

The visible `JobHistory.ReduceAttempt` tail exposes static `logKilled` overloads for reduce-attempt lifecycle logging. The complete `JobHistory.Task` block logs task/TIP start, finish, finish-time updates, and failures, including an overload that records the failed attempt responsible for a task failure. `JobHistory.TaskAttempt` is a base class for map/reduce attempt records. `JobHistory.Values` defines common persisted history values: `SUCCESS`, `FAILED`, `KILLED`, `MAP`, `REDUCE`, `CLEANUP`, `RUNNING`, `PREP`, and `SETUP`.

`JobID`, `TaskID`, and `TaskAttemptID` are old-API identity wrappers over the newer `org.apache.hadoop.mapreduce` IDs. They support construction from component parts, downgrade from new API IDs, `DataInput` reads, `forName(String)` parsing, typed access to parent IDs, and regex-pattern generation with nullable wildcard components. Their Javadoc makes the string layout part of the compatibility contract, while warning applications to use constructors/parsers instead of hand parsing.

`JobPriority`, `JobStatus`, `TIPStatus`, and `TaskCompletionEvent.Status` define scheduler and lifecycle enums/constants. `JobPriority` has `VERY_HIGH`, `HIGH`, `NORMAL`, `LOW`, and `VERY_LOW`. `JobStatus` is a synchronized, cloneable `Writable` data carrier for job id, setup/map/reduce/cleanup progress, run state, start time, username, scheduling info, and priority; public states are `RUNNING`, `SUCCEEDED`, `FAILED`, `PREP`, and `KILLED`. `TIPStatus` covers `PENDING`, `RUNNING`, `COMPLETE`, `KILLED`, and `FAILED`. Task completion statuses include `FAILED`, `KILLED`, `SUCCEEDED`, `OBSOLETE`, and `TIPFAILED`.

`JobProfile` and `JobQueueInfo` are `Writable` metadata records. `JobProfile` tracks the submitting user, `JobID`, job configuration file, tracking URL, job name, and queue name, with deprecated string-id compatibility APIs. `JobQueueInfo` stores queue name and scheduling information, returning `"N/A"` when scheduling info is unset.

`JobTracker` is the central old MapReduce coordinator. It implements `MRConstants`, `InterTrackerProtocol`, `JobSubmissionProtocol`, `TaskTrackerManager`, and `RefreshAuthorizationPolicyProtocol`. Its public API covers startup/shutdown, protocol versioning, restart/recovery state, instrumentation class configuration, address/port/start-time identity, service loop, submission counts, job lists, task-tracker collections and blacklists, topology/rack node lookups, job progress listeners, queue manager access, build version, task-tracker heartbeats, heartbeat interval calculation, filesystem name, tracker error reporting, new job ids, job submission, cluster status, job kill/fail/init/priority, job profile/status/counters, task reports, task completion events, diagnostics, task lookup/kill, assigned tracker lookup, system dir, local job-file path, queue queries, service ACL refresh, and a debugging `main`. Nested `JobTracker.IllegalStateException` represents submission before readiness, and nested `State` exposes `INITIALIZING` and `RUNNING`.

The chunk contains the old record-reader/input surface. `KeyValueLineRecordReader` reads lines as `Text` key/value pairs separated by configurable `key.value.separator.in.input.line`, with a static byte-level `findSeparator` helper and synchronized `next`, `getPos`, and `close`. `KeyValueTextInputFormat` creates those readers and documents whole-line-as-key behavior when the separator is absent. Deprecated `LineRecordReader` emits `(LongWritable offset, Text line)` and has constructors from `Configuration`/`FileSplit` and raw streams; nested `LineReader` is deprecated in favor of `org.apache.hadoop.util.LineReader`. Deprecated `TextInputFormat` wraps line reading for plain text files and splitability checks.

The old mapper/reducer contracts are present. Deprecated `Mapper` extends `JobConfigurable` and `Closeable`; its `map(key, value, OutputCollector, Reporter)` can emit zero or more intermediate pairs and use `Reporter` for progress/counters/status. `MapRunnable` is an expert hook for custom map-driving behavior, while `MapRunner` is the default implementation. `Reducer` defines `reduce(key, Iterator values, OutputCollector, Reporter)` and its Javadoc documents shuffle, sort/grouping, secondary-sort comparator hooks, and the fact that reducer output is not re-sorted. `MapReduceBase` supplies no-op `configure(JobConf)` and `close()`.

Output and shuffle-facing contracts include `OutputCollector.collect`, deprecated `OutputFormat.getRecordWriter`/`checkOutputSpecs`, `RecordWriter.write`/`close`, deprecated `OutputCommitter` bridging old `mapred.JobContext`/`TaskAttemptContext` methods to final new `mapreduce` methods, deprecated `Partitioner.getPartition`, and `RawKeyValueIterator` for sort/merge iteration over raw `DataInputBuffer` keys and values. `OutputLogFilter` filters `_logs` paths from output listings. `MapFileOutputFormat`, `SequenceFileOutputFormat`, `SequenceFileAsBinaryOutputFormat`, `SequenceFileAsTextInputFormat`, and `TextOutputFormat` provide concrete file output/input adapters.

Sequence-file APIs cover several modes. `SequenceFileInputFormat` lists sequence-file statuses and creates readers. `SequenceFileRecordReader` exposes key/value classes, reusable key/value creation, synchronized `next`, protected `next(key)` and `getCurrentValue`, split progress, seek, and close. `SequenceFileAsBinaryInputFormat.SequenceFileAsBinaryRecordReader` reads raw key/value bytes into `BytesWritable` while exposing stored class names. `SequenceFileAsBinaryOutputFormat` writes raw `BytesWritable` payloads while letting the logical sequence-file key/value classes be configured separately; protected `WritableValueBytes` adapts `BytesWritable` to `SequenceFile.ValueBytes`. `SequenceFileAsTextRecordReader` converts sequence-file keys and values to `Text` through `toString()`.

`SequenceFileInputFilter` samples sequence-file records using a configured filter class. Its nested `Filter` is `Configurable` and accepts/rejects keys. `FilterBase` stores configuration. `MD5Filter` accepts records where `MD5(key) % frequency == 0`; `PercentFilter` accepts by configurable frequency/period; `RegexFilter` accepts keys matching a configured regex pattern.

`SkipBadRecords` is a static configuration utility for old MapReduce's bad-record skipping mode. It configures the number of failed attempts before skip mode starts, automatic map/reduce processed-record counter increments, skip output path, maximum mapper skip records, and maximum reducer skip groups. Its public counter names are `COUNTER_GROUP`, `COUNTER_MAP_PROCESSED_RECORDS`, and `COUNTER_REDUCE_PROCESSED_GROUPS`.

Task execution and observability surfaces include `TaskAttemptContext`, `TaskCompletionEvent`, `TaskGraphServlet`, `TaskLog`, `TaskLogAppender`, `TaskLogServlet`, `TaskReport`, and `TaskTracker`. Deprecated `TaskAttemptContext` bridges to new `mapreduce.TaskAttemptContext` while exposing old `TaskAttemptID`, `JobConf`, progressible, and `progress()`. `TaskCompletionEvent` is a `Writable` record with event id, attempt id, runtime, status, map/reduce flag, id-within-job, tracker HTTP endpoint, equality/hash, and deprecated string-id accessors. `TaskGraphServlet` emits SVG graphics for task status. `TaskReport` is a `Writable` task status snapshot with progress, state, diagnostics, counters, current `TIPStatus`, start/finish times, successful attempt, and running attempts.

`TaskLog` resolves task log, real log, and index files; syncs logs; cleans old logs; computes task log length; and builds command lists to capture stdout/stderr or debug output. `TaskLog.LogName` enumerates `STDOUT`, `STDERR`, `SYSLOG`, `PROFILE`, and `DEBUGOUT`. `TaskLogAppender` is a Log4j `FileAppender` that activates per-task logging, appends/flushed/closes output, and configures task id plus total log file size. `TaskLogServlet` builds task-log URLs and serves log requests.

`TaskTracker` is the worker daemon. It implements the child/task-facing and tracker-facing APIs for storage cleanup, shutdown/close, connection to JobTracker (`InterTrackerProtocol`), report address, JVM manager access, server retry loop, child `getTask(JVMId)`, status updates, diagnostics, next-record ranges for skipping, ping, commit pending/can-commit/done, shuffle/filesystem/fatal errors, map completion event retrieval, lost map output notification, idle checks, memory-manager access, and a startup `main`. Nested `TaskTracker.MapOutputServlet` serves map outputs over Jetty to reducers.

`org.apache.hadoop.mapred.jobcontrol.Job` and `JobControl` model client-side dependency DAGs of old MapReduce jobs. A `Job` has a `JobConf`, `JobClient`, dependency list, assigned JobControl id, assigned MapReduce `JobID`, message, and integer states `WAITING`, `READY`, `RUNNING`, `SUCCESS`, `FAILED`, and `DEPENDENT_FAILED`; dependencies can only be added while waiting, and `submit()` moves ready jobs into running or failed state. `JobControl` implements `Runnable`, assigns group-unique ids, keeps jobs in state-specific tables, exposes getters for waiting/running/ready/successful/failed jobs, supports addJob/addJobs, stop/suspend/resume, allFinished, and a loop that checks running jobs, updates waiting jobs, and submits ready jobs.

The range ends with `org.apache.hadoop.mapred.join.ArrayListBackedIterator`, a `ResetableIterator` implementation backed by an `ArrayList`. It supports `hasNext`, `next(Writable)`, `replay(Writable)`, `reset`, `add(Writable)`, and `close`; the tail of the class is outside this chunk.

## Control Flow and Behavioral Contracts

Job history flow is event-oriented. Task and attempt helper methods append lifecycle records for starts, finishes, failures, kills, updates, attempt types, errors, counters, and split locations. Later history readers interpret values using the shared `JobHistory.Keys`, `RecordTypes`, and `Values` schema from neighboring chunks, so logging order and enum names are externally visible.

Job submission/control flow centers on `JobTracker`. Clients request a new `JobID`, submit the job, and then query profile/status/counters/reports/events/diagnostics or issue kill/fail/priority commands. TaskTrackers heartbeat with status and receive `HeartbeatResponse` instructions; child task JVMs talk to TaskTracker for task payloads, status, commit coordination, diagnostics, and map completion events. Queue APIs and listener registration provide scheduler and UI integration points.

Old map task flow is: an `InputFormat` creates `InputSplit`s and a per-split `RecordReader`; `MapRunner` repeatedly reads keys/values, invokes `Mapper.map`, and sends output through `OutputCollector`; `Reporter` communicates liveness, status, input split, and counters. Reduce flow receives shuffled and sorted map outputs, groups by comparator/partitioning policy, invokes `Reducer.reduce`, and writes results through an `OutputCollector`/`RecordWriter`. The documented shuffle/sort/secondary-sort behavior is a compatibility contract for old applications.

Output commit flow is: `OutputFormat.checkOutputSpecs` validates output on submission; `OutputCommitter.setupJob` and `setupTask` prepare temporary locations; task attempts write via `RecordWriter`; `needsTaskCommit` determines whether promotion is required; successful attempts call `commitTask`, failures call `abortTask`, and final job cleanup runs through `cleanupJob`. The old `OutputCommitter` also implements final new-API bridge methods that delegate to the old signatures, making it a key old/new API adapter.

Sequence-file flow depends on byte ranges and reusable writable objects. Readers are constructed for a `FileSplit`, create caller-owned key/value instances, fill them on each synchronized `next`, expose byte position/progress, and close underlying readers. Binary variants preserve raw bytes and logical class names; text variants stringify key/value pairs; filters wrap sequence-file input and decide acceptance from keys.

Skip-bad-record flow begins after a configurable number of task failures. When enabled, tasks report the next record/group range to the TaskTracker before processing. If the task crashes, the TaskTracker knows the last reported range and later attempts skip it, subject to configured maximum skip counts and application-maintained counters.

JobControl flow is a local dependency scheduler layered over `JobClient`. A job starts in `WAITING`, becomes `READY` once dependencies are successful or absent, becomes `DEPENDENT_FAILED` if a dependency fails, and moves from `READY` to `RUNNING` through submission. The `JobControl.run` loop periodically checks running jobs, updates waiting jobs, and submits ready jobs until stopped/suspended or all work finishes.

## State, Persistence, and Side Effects

Many types define `Writable` state: `JobProfile`, `JobQueueInfo`, `JobStatus`, `TaskCompletionEvent`, `TaskReport`, ID types through their parents, file splits/readers in adjacent APIs, and sequence/text readers through reusable Hadoop writable keys and values. Their field ordering and enum names are binary and log compatibility surfaces.

`JobTracker` owns persistent and live cluster state: job maps, tracker tables, blacklists, queues, topology, recovery status, submission counters, task reports, completion events, diagnostics, and service ACL policy. Its methods have distributed side effects such as starting/stopping services, accepting submissions, killing jobs/tasks, refreshing authorization policy, and reacting to tracker errors.

`TaskTracker` owns node-local state and side effects: temporary storage, running child JVMs, local task logs, map output serving, status update records, commit coordination, skipped record ranges, map output loss reports, and memory management. `cleanupStorage`, `shutdown`, and `close` explicitly mutate local disk/process state.

Record readers and writers mutate caller-provided objects and stream positions. `LineRecordReader`, `KeyValueLineRecordReader`, `SequenceFileRecordReader`, binary/text sequence readers, and `TextOutputFormat.LineRecordWriter` are stateful, often synchronized around `next`, `write`, `getPos`, or `close`. They depend on exact byte offsets, split boundaries, separator bytes, compression/splittability, and `DataOutputStream` behavior.

Task logs are persistent local files with index files and web-accessible URLs. `TaskLog.syncLogs`, capture-command builders, appender size limits, log-name enums, and log servlet parameters are part of the operational surface for debugging, profiling, and user log retrieval.

`SkipBadRecords` persists behavior in `Configuration`/`JobConf` keys and counter names, and can write skipped records to an output path, by default under output `_logs`. The feature relies on application/framework counter increments and TaskTracker-maintained range state.

`JobControl` state is process-local rather than cluster-persistent: its tables of jobs by state, assigned group ids, thread state, and dependency lists exist in the client application. The submitted MapReduce job id is still stored as a `JobID` assigned by the framework.

## Dependencies and Integration Points

This chunk is centered on the legacy `org.apache.hadoop.mapred` package while repeatedly bridging to `org.apache.hadoop.mapreduce`. `JobID`, `TaskID`, `TaskAttemptID`, `TaskAttemptContext`, and `OutputCommitter` expose old signatures on top of new API base classes. Many old interfaces are deprecated in favor of newer `mapreduce` equivalents but remain contractually visible in this 0.20.2 API snapshot.

Filesystem integration uses `org.apache.hadoop.fs.FileSystem`, `Path`, path filters, map-file/sequence-file readers and writers, task local storage, output directories, and log files. Network and topology integration appears through `InetSocketAddress`, `org.apache.hadoop.net.Node`, task-tracker host names, tracker HTTP endpoints, Jetty servlets, and map-output HTTP serving.

Cluster protocol integration is exposed by `InterTrackerProtocol`, `JobSubmissionProtocol`, `TaskTrackerManager`, `RefreshAuthorizationPolicyProtocol`, `HeartbeatResponse`, `TaskTrackerStatus`, `JobInProgress`, `TaskInProgress`, `JvmTask`, `JVMId`, `MapTaskCompletionEventsUpdate`, and queue/scheduler manager types. Security integration is represented by `MapReducePolicyProvider`, `PolicyProvider`, `Service`, and service ACL refresh.

Serialization and data model dependencies include `Writable`, `WritableComparable`, `BytesWritable`, `Text`, `LongWritable`, `DataInput`, `DataOutput`, `DataInputBuffer`, `SequenceFile.ValueBytes`, Java `Iterator`, `Collection`, `ArrayList`, `Vector`, `Map`, and standard checked exceptions. Logging uses Commons Logging and Log4j; progress/liveness uses `Progressable` and `Reporter`; servlet integration uses `HttpServletRequest`/`HttpServletResponse`.

## Risks and Compatibility Notes

The range starts inside `JobHistory.ReduceAttempt` and ends inside `ArrayListBackedIterator`, so adjacent chunks are required for complete per-class documentation. This chunk also includes generated API metadata only; implementation details such as actual configuration key names for some helpers must be verified in Java source when changing behavior.

Old `mapred` APIs are compatibility-sensitive even when deprecated. Removing deprecated string-id methods, changing enum constants, altering `Writable` serialization, changing synchronized behavior, or replacing legacy container return types can break existing Hadoop 0.20-era applications, history parsers, RPC clients, or serialized job metadata.

`JobTracker` and `TaskTracker` expose high-risk distributed coordination paths. Heartbeat response ids, recovery state, topology resolution, blacklisting, commit authorization, lost map output handling, task kill/fail semantics, queue queries, service ACL refresh, and shutdown/cleanup behavior can race with task execution or client polling.

Record readers/writers are byte-level compatibility surfaces. Line splitting, CR/LF handling, split-start behavior, custom separator bytes, reusable writable mutation, progress reporting, raw sequence-file class names, and compressed data handling all need regression protection.

Output commit and task log behavior are operationally risky. Incorrect commit/abort ordering can corrupt output under speculative execution, while changes to task-log paths, index files, capture commands, or servlet URL generation can break debugging and web UI integration.

Skip-bad-record mode depends on counters and reported ranges lining up exactly with application processing. Asynchronous mappers/reducers must disable automatic counter increments and maintain counters themselves; otherwise skip ranges can point at the wrong records or groups.

JobControl is simple but stateful and synchronized only on selected methods. Dependency mutation after a job leaves `WAITING`, suspension/resume behavior, and external polling of returned `ArrayList`s are likely compatibility and concurrency risk points.

## Test Signals

JDiff-level tests should verify the full XML remains well formed and preserves all public/protected class/interface names, inheritance, implemented interfaces, constructors, methods, parameter types, checked exceptions, fields, flags, deprecation strings, and embedded Javadoc contracts across this line range.

Identity and status tests should cover `JobID`, `TaskID`, and `TaskAttemptID` parsing, downgrade behavior, regex generation with null wildcard parts, `Writable` reads, malformed string failures, map/reduce bit preservation, and deprecated string-id compatibility. `JobStatus`, `JobProfile`, `JobQueueInfo`, `TaskCompletionEvent`, and `TaskReport` need serialization round trips, enum/state coverage, equality/hash behavior where exposed, progress fields, priority, queue/scheduling info, diagnostics, and runtime/status fields.

JobTracker/TaskTracker integration tests should exercise startup/readiness, illegal submission before running, job id allocation and submission, job kill/fail/init/priority, cluster status detail mode, queue APIs, task reports and diagnostics, task completion event pagination, tracker blacklisting, topology lookup, heartbeat intervals, task heartbeat/status updates, commit authorization, shuffle/fs/fatal errors, map output lost, map completion event serving, shutdown/cleanup, memory-manager access, and service ACL refresh.

Old MapReduce contract tests should run mapper/reducer jobs through `MapRunner`, `Reporter`, `OutputCollector`, `RecordReader`, `RawKeyValueIterator`, `Partitioner`, `OutputFormat`, `RecordWriter`, and `OutputCommitter`, including progress/counter/status updates, secondary sort/grouping comparators, commit/abort paths, and deprecated API bridge methods.

Input/output format tests should cover text line offsets, CR/LF variants, split boundaries, key/value separator search, missing separators, custom separator bytes, empty keys/values, UTF-8 `Text`, `TextOutputFormat.LineRecordWriter` separators/null handling, `OutputLogFilter`, `MapFileOutputFormat` reader lookup through a partitioner, and sequence-file binary/text/filter record readers and writers.

Sequence-file filter tests should cover configured filter-class selection, `MD5Filter` frequency math, `PercentFilter` periodic acceptance, `RegexFilter` pattern acceptance, configuration propagation through `FilterBase`, raw byte preservation in binary readers/writers, logical class-name configuration, and `WritableValueBytes` compressed/uncompressed write paths.

Skip-bad-record tests should cover attempts-before-skipping defaults and setters, automatic mapper/reducer counter increments on/off, explicit application counter increments, skip output path default/null/custom behavior, mapper/reducer maximum skip thresholds including `0` and `Long.MAX_VALUE`, TaskTracker next-record-range reporting, and deterministic task crash retries.

Task log and servlet tests should cover log file/index resolution, real log location resolution, sync/cleanup, task log length, stdout/stderr/debug capture command construction, `LogName.toString`, appender activation/flush/close/size limits, task-log URL generation, TaskLogServlet responses, TaskGraphServlet SVG output, and MapOutputServlet serving map outputs to reducers.

JobControl tests should cover dependency DAG transitions from `WAITING` to `READY`, `RUNNING`, `SUCCESS`, `FAILED`, and `DEPENDENT_FAILED`; inability to add dependencies after waiting; assigned JobControl id and assigned framework JobID; `submit()` success/failure; `JobControl` addJob/addJobs, state-specific getters, suspend/resume/stop, allFinished, and run-loop behavior when dependencies fail or complete.

### subset-b-007336: lines 43883-50039

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 43883-50039

## Scope

This chunk is a middle segment of the generated JDiff public API snapshot for Hadoop 0.20.2. It is XML compatibility metadata, not implementation source. The range starts at the tail of `org.apache.hadoop.mapred.join.ArrayListBackedIterator`, covers the rest of the old `org.apache.hadoop.mapred.join` API, most of the legacy `org.apache.hadoop.mapred.lib` helper package, the `mapred.lib.aggregate` aggregation framework, JDBC-backed `mapred.lib.db` input/output APIs, the `mapred.pipes.Submitter` tool, `mapred.tools.MRAdmin`, and begins the newer `org.apache.hadoop.mapreduce` counter model.

The XML records public class/interface names, inheritance, implemented interfaces, constructors, method signatures, parameter and exception types, fields, visibility, deprecation markers, method modifiers, and embedded Javadocs. Behavioral notes below are inferred from that public metadata and documentation because method bodies are not present in this file.

## Purpose and Major API Surface

The `org.apache.hadoop.mapred.join` package exposes the old MapReduce join framework. `ComposableInputFormat` refines `InputFormat` to return `ComposableRecordReader`. `ComposableRecordReader` adds join-aware cursor operations: `id()`, `key()`, key cloning, `hasNext()`, `skip(WritableComparable)`, and `accept(JoinCollector, WritableComparable)`.

`CompositeInputFormat` parses a join expression from `mapred.join.expr`, installs built-in and user-defined join operators from `mapred.join.define.<ident>`, builds child input formats, creates aligned `CompositeInputSplit` instances, and constructs the root `ComposableRecordReader`. Its static `compose(...)` helpers generate `tbl(...)` and operator expressions for class/path inputs. `CompositeInputSplit` stores a fixed set of child `InputSplit`s, aggregates lengths and locations, and serializes as count, split class names, then child split payloads.

`CompositeRecordReader` is the base join reader. It is `Configurable`, owns child `ComposableRecordReader` instances, exposes a priority queue of child readers ordered by a `WritableComparator`, fills a `JoinCollector`, implements key comparison and skipping, creates common key/internal tuple values, reports progress as the minimum child progress, and closes all children. Subclasses define `combine(Object[], TupleWritable)` and `getDelegate()`.

The join subclasses model concrete operators. `JoinRecordReader` emits `TupleWritable` values and delegates iteration through `JoinDelegationIterator`. `InnerJoinRecordReader` only combines full tuples where every source has the key. `OuterJoinRecordReader` emits all tuples from the collector. `MultiFilterRecordReader` emits a single `Writable` derived from a tuple through `emit(TupleWritable)`, with `MultiFilterDelegationIterator` as its proxy. `OverrideRecordReader` prefers the rightmost source for a key and overrides collector filling to skip lower-priority streams once a higher-priority value is available.

`Parser`, `Parser.Node`, token classes, and `Parser.TType` define the join-expression parser. The parser is documented as a simple shift-reduce parser. `Node` implements `ComposableInputFormat`, tracks an identifier, id, comparator class, and a constructor map for record-reader nodes. Token subclasses carry parsed nodes, strings, and numbers.

`ResetableIterator` is a stateful replayable iterator interface used by join collection. It supports `hasNext`, `next`, `replay`, `reset`, `add`, `close`, and `clear`, deliberately not extending `java.util.Iterator`. `ResetableIterator.EMPTY` is a no-op implementation. `ArrayListBackedIterator` stores replay data in an `ArrayList` but is documented as less preferred than `StreamBackedIterator`, which stores added elements in a byte array. `TupleWritable` stores an array of `Writable` values plus per-position presence bits, is itself `Writable` and `Iterable`, and serializes written-element cardinality plus values.

`WrappedRecordReader` adapts a normal old-api `RecordReader` to `ComposableRecordReader`. It keeps a head key/value pair, compares by head key, supports `skip`, adds values to a join collector, forwards `createKey`, `createValue`, progress, position, and close to the proxied reader, and advances the proxied stream after emitting the current head.

The `org.apache.hadoop.mapred.lib` package contains old-api helpers. `ChainMapper` and `ChainReducer` let jobs run a mapper chain, or reducer followed by mapper chain, inside one task. They use static configuration methods to append mapper/reducer classes and key/value classes, then instantiate/configure/close the chain around `map` or `reduce` calls. `CombineFileInputFormat`, `CombineFileSplit`, and `CombineFileRecordReader` combine many small files into fewer splits, with split-size controls, node/rack minimums, path-filter pools, per-chunk record reader creation by reflection, byte-progress tracking, and split serialization of paths, offsets, lengths, locations, and job state.

`DelegatingInputFormat`, `DelegatingMapper`, and `MultipleInputs` implement per-path input format and mapper selection. `MultipleInputs.addInputPath(...)` records path-specific input formats and optionally mapper classes, `DelegatingInputFormat` routes split and reader creation, and `DelegatingMapper` routes records to the mapper configured for their input path. `FieldSelectionMapReduce` is both a mapper and reducer that selects fields from text values based on configuration. `HashPartitioner`, `KeyFieldBasedComparator`, `KeyFieldBasedPartitioner`, and `TotalOrderPartitioner` provide partitioning and sorting utilities, including Unix-sort-like key field specifications and total-order partitioning from an externally generated SequenceFile of split points.

The simple mapper/reducer helpers include `IdentityMapper`, `IdentityReducer`, `InverseMapper`, `LongSumReducer`, `RegexMapper`, and `TokenCountMapper`. Several old `mapred` classes are explicitly deprecated in favor of newer `org.apache.hadoop.mapreduce` equivalents, but the signatures remain compatibility-relevant. `InputSampler` and its `IntervalSampler`, `RandomSampler`, and `SplitSampler` collect key samples from old-api input formats and write partition files for `TotalOrderPartitioner`.

The output helpers include `MultipleOutputFormat`, `MultipleOutputs`, `MultipleSequenceFileOutputFormat`, `MultipleTextOutputFormat`, and `NullOutputFormat`. `MultipleOutputFormat` is an abstract `FileOutputFormat` that can derive output file names, actual output keys/values, and base record writers per key/value or input file. `MultipleOutputs` configures named and multi-named outputs, exposes static metadata accessors, optional counters, collector factories, and `close()` for opened writers. `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` provide base writers for those formats. `NullOutputFormat` discards all output.

`MultithreadedMapRunner` is an old-api `MapRunnable` that runs mapper calls in a thread pool, controlled by `mapred.map.multithreadedrunner.threads`, and requires thread-safe mapper implementations. `NLineInputFormat` creates one split for every configured number of lines, intended for parameter sweep style workloads where each input line describes independent work.

The `org.apache.hadoop.mapred.lib.aggregate` package provides a generic aggregation framework. `ValueAggregator` defines `addNextValue`, `reset`, `getReport`, and `getCombinerOutput`. Built-ins include double/long sum, long min/max, string min/max, unique-value counting with a maximum retained item count, and histograms. `ValueAggregatorDescriptor` generates aggregation-id/value pairs from input records. `ValueAggregatorBaseDescriptor` supplies standard aggregation type names and factory logic, while `UserDefinedValueAggregatorDescriptor` reflectively delegates to user descriptor classes. `ValueAggregatorMapper`, `ValueAggregatorCombiner`, `ValueAggregatorReducer`, and `ValueAggregatorJobBase` implement the map, combine, and reduce phases for Aggregate jobs. `ValueAggregatorJob` builds job controls and `JobConf`s for aggregate workloads and exposes a command-line entry point.

The `org.apache.hadoop.mapred.lib.db` package exposes JDBC-backed old-api I/O. `DBConfiguration` defines job configuration keys and static `configureDB(...)` methods for JDBC driver, URL, username, and password. `DBInputFormat` is an `InputFormat`/`JobConfigurable` for SQL input, with static `setInput(...)` overloads for table/query configuration, count-query generation, row-range splits, and a `DBRecordReader` that returns `LongWritable` keys and `DBWritable` values. `DBOutputFormat` writes reducer output keys to a SQL table through prepared statements and has static `setOutput(...)` configuration. `DBWritable` is the contract for translating objects to/from `PreparedStatement` and `ResultSet`; `NullDBWritable` is a no-op bridge implementation.

`org.apache.hadoop.mapred.pipes.Submitter` is the old Hadoop Pipes job launcher. It is a `Tool` and `Configured` class with accessors for the executable URI, booleans controlling whether record reader, mapper, reducer, and record writer are Java-side or native-side, command-file retention for debugging, deprecated `submitJob`, replacement `runJob`, lower-level `jobSubmit`, `run`, and `main`. `org.apache.hadoop.mapred.tools.MRAdmin` is an administrative `Tool` for connecting to the JobTracker and refreshing the service-level authorization policy.

The chunk ends in `org.apache.hadoop.mapreduce` with the start of the new counter API. `Counter` is a synchronized `Writable` with name, display name, value, increment, equality, and hash code. `CounterGroup` is a synchronized `Writable`/`Iterable` of counters with group display metadata, lookup/creation, serialization, size, equality, hash code, and `incrAllCounters`. `Counters` begins with lookup by group/name and enum, group-name listing, iteration, group retrieval, and `countCounters()`; the method body metadata continues in the next chunk.

## Control Flow and Behavioral Contracts

Join execution is expression driven. `CompositeInputFormat.setFormat` parses `mapred.join.expr`; default and configured identifiers map expression nodes to `ComposableRecordReader` constructors; `getSplits` aligns the i-th split from each child into a `CompositeInputSplit`; `getRecordReader` materializes the corresponding reader tree. Runtime join flow advances child readers in key order, uses `skip` to discard lower keys, asks matching children to `accept` a key into the `JoinCollector`, then emits tuples or filtered values according to the concrete join reader's `combine`/`emit` rules.

Replayable iterators are central to join correctness. Children add matching values into resettable iterators, the collector replays combinations for matching keys, and `reset` must be called after `add` to avoid concurrent modification problems. `TupleWritable` exposes sparse tuple positions through `has(int)` rather than assuming every child contributed.

Multi-input control flow depends on job configuration. `MultipleInputs` records path-to-input-format and path-to-mapper metadata; the delegating input format groups splits by input format and creates the right reader; the delegating mapper configures and invokes the mapper selected for each path. This allows one old-api job to consume heterogeneous input sources.

Combine-file flow groups files into logical splits and then iterates chunks inside a split. `CombineFileRecordReader.initNextRecordReader()` advances to the next path/offset/length segment, constructs the per-chunk reader by reflection, and accumulates progress in bytes processed. The `getRecordReader` method on `CombineFileInputFormat` is explicitly documented as not implemented in the abstract base.

Sampler and total-order partitioner flow is two-stage. `InputSampler` samples keys from input splits and writes a SequenceFile of partition boundaries. `TotalOrderPartitioner.configure` reads that file and chooses either a trie for natural-order `BinaryComparable` keys or binary search using the job's `RawComparator`; the partition file must have `numReduceTasks - 1` sorted keys.

Multiple-output flow is side-effect oriented. Job setup defines named outputs and optionally counters. Task code obtains a collector for a named output or a multi-named output, which lazily opens a writer with the configured `OutputFormat`, key class, and value class. `close()` must be called to flush and close all opened outputs. Named output records written from a mapper bypass the reduce phase unless written to the primary job collector.

Aggregate flow maps input records to aggregation-id/value pairs, combines values with matching aggregation ids, and reduces them through the selected `ValueAggregator`. Descriptor classes are responsible for turning arbitrary input key/value pairs into typed aggregation entries using the `TYPE_SEPARATOR` protocol and standard aggregation names.

DB input flow computes a row count, divides rows into `DBInputSplit` ranges, generates select queries with limit/offset style range constraints, and asks `DBWritable` instances to populate themselves from `ResultSet`. DB output flow constructs an insert prepared statement from configured table and field names, asks the output key to write fields into the statement, batches records, and closes JDBC resources.

Pipes submit flow mutates a `JobConf` so a Hadoop job launches a C++ pipes executable, with per-component switches deciding whether Java or pipes code handles reading, mapping, reducing, and writing. Keeping the command file writes `downlink.data` in the task directory for replay/debugging.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent public API metadata for compatibility checking. The source does not store runtime state, but it captures configuration keys, serialized forms, and public method contracts that downstream Hadoop applications depend on.

Join state lives in child record-reader heads, priority queues, `JoinCollector` contents, `ResetableIterator` buffers, tuple presence bits, and job configuration values such as `mapred.join.expr`, `mapred.join.define.<ident>`, and `mapred.join.keycomparator`. `CompositeInputSplit`, `TupleWritable`, and child splits are serialized through `DataOutput`/`DataInput`, so class names, ordering, and writable payload order are compatibility-sensitive.

Old mapred helper state is primarily `JobConf` state. Chain jobs persist mapper/reducer chain metadata and key/value class boundaries in configuration. Multiple inputs persist path-specific input formats and mapper classes. Field selection, key-field comparison/partitioning, total-order partitioning, multi-output definitions, counters-enabled flags, N-line splitting, multithreaded runner thread count, and DB connection/query properties are all configured through `JobConf`.

Filesystem side effects appear in combine-file split planning, input sampling partition-file creation, total-order partition-file reads, multiple-output writer creation, sequence/text output writer creation, and null output discard behavior. Multiple outputs create additional output files beyond the default job output and optionally emit counters named after outputs.

Database side effects are external and transactional only to the degree provided by the implementation and JDBC connection handling. `DBInputFormat` reads table/query results; `DBOutputFormat` inserts reduce output keys into an SQL table through prepared statements. Configuration includes driver class, URL, username, and password, making credential handling and job-conf exposure relevant.

Pipes state includes the executable URI, Java/native component booleans, optional saved command file, task-local debugging artifacts, and submitted job handles. `MRAdmin` causes cluster-side administrative effects by refreshing service-level authorization policy through the JobTracker.

`Counter`, `CounterGroup`, and `Counters` are synchronized writable state containers. Counter names, display names, values, group membership, serialization, equality, and aggregate increment behavior are part of the public compatibility surface for job progress, metrics, history, and user code.

## Dependencies and Integration Points

This chunk is anchored in the legacy `org.apache.hadoop.mapred` API: `InputFormat`, `InputSplit`, `RecordReader`, `Mapper`, `Reducer`, `MapRunnable`, `OutputCollector`, `OutputFormat`, `RecordWriter`, `Reporter`, `Partitioner`, `JobConf`, `JobConfigurable`, `FileInputFormat`, `FileOutputFormat`, `MapReduceBase`, `RunningJob`, and `JobClient` style workflows.

Serialization and data dependencies include `org.apache.hadoop.io.Writable`, `WritableComparable`, `WritableComparator`, `RawComparator`, `Text`, `LongWritable`, `BinaryComparable`, and `SequenceFile`. Filesystem dependencies include `Path`, `FileSystem`, path filters, split locations, and progress callbacks through `org.apache.hadoop.util.Progressable`.

The join framework integrates with Java collections and reflection through `PriorityQueue`, `Map`, `Comparable`, constructor maps, parser token classes, and class names configured in expressions. The chain, multiple input, combine-file, aggregate, DB, and pipes APIs also rely heavily on `java.lang.Class` values in `JobConf`.

External system dependencies are explicit in JDBC APIs: `java.sql.Connection`, `PreparedStatement`, `ResultSet`, and `SQLException`. Pipes integrates Java MapReduce job submission with an external native executable URI, commonly on HDFS. Logging uses Apache Commons Logging in several public `LOG` fields.

The newer `org.apache.hadoop.mapreduce` counter classes begin the bridge from old mapred helpers toward the newer API. Many old helpers in this chunk are deprecated with references to `org.apache.hadoop.mapreduce` replacements, which is important for compatibility and migration tooling.

## Risks and Compatibility Notes

The range starts inside `ArrayListBackedIterator` and ends inside `Counters.countCounters()`, so adjacent chunks are needed for complete class-level reconstruction. This chunk still contains complete entries for most join, lib, aggregate, DB, pipes, and MRAdmin classes.

Join APIs are high-risk because they combine sorted input assumptions, configured parsers, reflection, tuple serialization, comparator behavior, and iterator replay. Incorrect child split alignment, key comparator mismatch, duplicate child ids, missing public default constructors for serialized splits, or stale resettable iterator state can produce silent join loss or duplication.

`CompositeInputSplit.write/readFields` serializes class names before child split payloads. Renaming split classes, removing public no-arg constructors, changing child order, or changing writable payloads would break persisted splits and compatibility with running or recovered tasks.

`TupleWritable` sparse presence bits are a compatibility contract. Consumers must check `has(i)` before `get(i)` for outer joins; serialization must preserve which tuple positions were written, not just the writable array.

Configuration string formats are broad compatibility surfaces. Join expressions, key-field specs, path-specific input mappings, multiple-output names, total-order partition file paths, DB query/table/field settings, pipes executable URIs, and counter group/name strings are commonly embedded in job configs, tests, examples, and downstream applications.

`MultipleOutputs` has several correctness risks: named output names must be validated, `"part"` is reserved, mapper-side named-output records bypass reducers, counters are disabled by default, multi-output counter names concatenate output and multi-name with an underscore, and callers must close the object to release opened writers.

`MultithreadedMapRunner` exposes concurrency risk. Mapper implementations and any shared output/reporting/counter interactions must be thread-safe. Input readers and collectors also need careful coordination in the implementation because old mapred mappers usually assume single-threaded invocation.

`TotalOrderPartitioner` correctness depends on sorted partition files, exactly `R - 1` split keys for `R` reducers, and comparator consistency between sampling, partition-file sorting, and runtime partitioning. Trie depth and natural-order settings can affect both correctness and performance.

Aggregate APIs rely on string-encoded type/value protocols and reflection. Typos in aggregation type names, descriptor class names, or `TYPE_SEPARATOR` handling can route data to the wrong aggregator or fail at runtime. Numeric aggregators parse values from string representations, so malformed input values are a test and error-handling concern.

DB APIs can leak credentials through job configuration and have external side effects. Query construction, count queries, limit/offset semantics, prepared-statement field ordering, batching, connection cleanup, SQL exceptions, and database-specific syntax are all risky. `DBOutputFormat` writes only the key, so users must encode all DB fields in the key's `DBWritable` implementation.

Pipes submission mutates `JobConf` and starts external executables. Component-mode flags must be coherent with provided Java classes and native code. Saved command files are useful for debugging but can expose task data in local task directories.

Counter APIs use synchronized public methods and writable serialization. Any change to synchronization, serialization order, equality/hash code, display-name handling, enum mapping, or group aggregation can affect job metrics, UI display, history, and user assertions.

## Test Signals

JDiff-level validation should confirm the XML remains well formed across this chunk, preserves package/class/interface names, inheritance, implemented interfaces, constructors, method signatures, parameter and exception types, fields, visibility, deprecation text, and synchronization/static/final/abstract/native flags.

Join tests should cover `CompositeInputFormat.compose` output, parsing of nested expressions, custom `mapred.join.define.<ident>` operators, comparator configuration, aligned split creation, `CompositeInputSplit` serialization round trips, missing split constructors, `WrappedRecordReader` key advancement, skip semantics, inner join full-tuple behavior, outer join sparse tuples, override rightmost-source preference, tuple `has/get` behavior, and `ResetableIterator` add/reset/replay/clear/close semantics.

Legacy lib tests should cover chain mapper/reducer configuration and lifecycle ordering, multiple input path routing, delegating mapper selection, field selection specs, hash and key-field partitioning, key-field comparator numeric/reverse/range behavior, total-order partitioning from sampled split points, and deprecation-compatible behavior of identity, inverse, regex, token-count, and long-sum helpers.

Combine-file tests should cover max split size, min split size per node/rack, path-filter pools, split serialization, location aggregation, per-chunk record reader reflection, progress accounting, zero-length files, and cleanup when moving between chunk readers.

Sampler tests should cover interval, random, and split samplers against multiple input splits; sample-count limits; random split ordering; partition-file writing; and compatibility with `TotalOrderPartitioner`.

Output tests should cover `MultipleOutputFormat` filename/key/value customization hooks, input-file-based output naming, named-output metadata accessors, name validation including reserved `part`, single and multi named collectors, counter enablement and counter naming, mapper-side bypass of reducers, close behavior for all opened outputs, sequence/text writer creation, and `NullOutputFormat` discarding records.

Aggregate tests should cover every built-in aggregator's add/reset/report/combiner-output behavior, malformed numeric values, unique-value maximum enforcement, histogram report details, descriptor-generated entries, user-defined descriptor reflection/configuration, mapper/combiner/reducer data flow, and `ValueAggregatorJob` configuration helpers.

DB tests should cover JDBC configuration keys, `setInput` table and query modes, count query customization, split row ranges and serialization, select-query construction, `DBWritable` read/write callbacks, null writable no-op behavior, output insert query construction with explicit and null field lists, prepared statement field order, batch/close behavior, SQL exception paths, and cleanup of connections/statements/result sets.

Pipes and admin tests should cover executable URI setters/getters, Java/native component flags, keep-command-file behavior, deprecated `submitJob` delegation to `runJob`, `jobSubmit` returning a `RunningJob`, command-line `run/main` argument validation, and `MRAdmin` refresh authorization command handling.

Counter tests should cover synchronized `Counter` read/write/increment/equality/hash code, display-name updates, `CounterGroup` lookup and creation semantics, group serialization, iteration, `incrAllCounters`, `Counters.findCounter` by enum and group/name, group-name listing, empty-group retrieval, counter counting, and serialization compatibility across old job history or metrics consumers.

### subset-b-007337: lines 50040-53959

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 50040-53959

## Scope

This chunk is the final segment of the generated JDiff public API snapshot for Hadoop 0.20.2. It is XML API metadata rather than Java implementation code. The range begins inside the tail of `org.apache.hadoop.mapreduce.Counters`, then covers the main `org.apache.hadoop.mapreduce` job, context, ID, mapper, reducer, input, output, partitioning, and helper APIs. It also records `org.apache.hadoop.mapreduce.lib.input`, `lib.map`, `lib.output`, `lib.partition`, `lib.reduce`, and the start-to-finish public API entries for several `org.apache.hadoop.tools` utilities before closing the XML document.

The XML records compatibility surface: package and class names, inheritance, implemented interfaces, constructors, method signatures, parameters, declared exceptions, fields, visibility, abstract/static/final/synchronized/native flags, deprecation state, and embedded Javadoc. Runtime behavior below is inferred from signatures and documentation because this source does not include method bodies.

## Purpose and Major API Surface

The visible `Counters` tail exposes synchronized aggregate and serialization behavior: total counter count, `write(DataOutput)`, `readFields(DataInput)`, `toString()`, `incrAllCounters(Counters)`, `equals(Object)`, and `hashCode()`. Its documented external format is a collection of groups, each with display name, counters, optional display names, and values.

`ID` is the abstract base identifier for `JobID`, `TaskID`, and `TaskAttemptID`. It implements `WritableComparable`, stores a protected integer `id`, exposes `getId()`, `toString()`, `equals`, `hashCode`, numeric `compareTo(ID)`, and `readFields`/`write` serialization, and defines a protected separator character.

`InputFormat` and `InputSplit` define the new MapReduce input contract. `InputFormat.getSplits(JobContext)` validates and logically splits job input, while `createRecordReader(InputSplit, TaskAttemptContext)` creates readers for individual splits. `InputSplit` exposes split length and host locations for scheduling and locality; the Javadoc stresses that splits are logical byte-oriented views and record boundaries are handled by `RecordReader`.

`Job` is the submitter-facing mutable job configuration and control object. Constructors accept no arguments, a `Configuration`, or a `Configuration` plus job name. Before submission it configures reduce count, working directory, input/output formats, mapper, combiner, reducer, partitioner, key/value classes, sort and grouping comparators, job name, and job jar. After submission it exposes tracking URL, map/reduce progress, completion/success state, kill/fail operations for jobs and tasks, task completion events, counters, `submit()`, and `waitForCompletion(boolean)`. `Job.JobState` records `DEFINE` and `RUNNING`.

`JobContext` is the task-facing read-only job view. It wraps a `JobConf` and `JobID`, exposes configuration, job ID, reduce count, working directory, output and map-output key/value classes, job name, input/mapper/combiner/reducer/output/partitioner classes, sort and grouping comparators, and jar path. Its public string fields define configuration attribute names for input format, mapper, combiner, reducer, output format, and partitioner.

`JobID`, `TaskID`, and `TaskAttemptID` are immutable public identifiers extending the older `org.apache.hadoop.mapred.ID` base. They provide component constructors, no-arg constructors for deserialization, accessors, `equals`, `hashCode`, `compareTo`, `toString`, protected `appendTo(StringBuilder)`, static `forName(String)` parsers, and `readFields`/`write` methods. `JobID` carries a job-tracker identifier; `TaskID` carries a `JobID` plus map/reduce kind; `TaskAttemptID` carries a `TaskID` plus attempt number.

`MapContext`, `Mapper`, and `Mapper.Context` define mapper execution. `MapContext` extends `TaskInputOutputContext` and adds access to the input split while delegating current key/value and cursor advancement to the record reader. `Mapper` exposes the standard lifecycle methods `setup`, `map`, `cleanup`, and `run`, with default mapper behavior documented as processing each input pair through the map method.

`OutputCommitter`, `OutputFormat`, `RecordWriter`, and `Partitioner` define output and shuffle contracts. `OutputCommitter` controls job/task setup, task commit checks, commit, abort, and job cleanup. `OutputFormat` validates output specs, creates a `RecordWriter`, and supplies an `OutputCommitter`. `RecordWriter` writes key/value output pairs and closes with a task context. `Partitioner.getPartition` assigns a key/value pair to a reduce partition.

`RecordReader`, `ReduceContext`, `Reducer`, `Reducer.Context`, `StatusReporter`, `TaskAttemptContext`, and `TaskInputOutputContext` define task execution. `RecordReader` initializes from a split and task context, advances key/value records, exposes current key/value, progress, and close. `ReduceContext` wraps reduce-side merged input, grouping comparator, counters, output writer, committer, and status reporter; nested `ValueIterable` and `ValueIterator` expose values for the current key. `Reducer` exposes setup, reduce, cleanup, and run lifecycle hooks. `StatusReporter` supplies counters, progress, and status. `TaskAttemptContext` and `TaskInputOutputContext` expose attempt identity, status/progress, current input, output writes, counters, and committer access.

The `org.apache.hadoop.mapreduce.lib.input` package provides file-based inputs. `FileInputFormat` configures input paths, path filters, min/max split sizes, splitability, file listing, split generation, split-size computation, block index lookup, and input path getters/setters/adders. `FileSplit` is a writable split containing file path, byte start, length, and host locations. `InvalidInputException` aggregates input validation problems. `LineRecordReader` reads lines as `LongWritable` offsets and `Text` values. `TextInputFormat` creates line readers and handles splitability. `SequenceFileInputFormat` and `SequenceFileRecordReader` read Hadoop `SequenceFile`s and report split progress.

The `org.apache.hadoop.mapreduce.lib.map` package contains small mapper helpers. `InverseMapper` swaps input keys and values. `MultithreadedMapper` runs an application mapper through a thread pool and exposes static configuration helpers for thread count and mapper class. `TokenCounterMapper` tokenizes input values and emits tokens with count one.

The `org.apache.hadoop.mapreduce.lib.output` package contains file output behavior. `FileOutputCommitter` creates temporary output roots, handles task work directories, promotes successful task output, aborts failed task output, checks whether commit is needed, and exposes the work path. `FileOutputFormat` configures output compression, compressor class, output path, work output path, unique task filenames, default work files, and output committer creation. `NullOutputFormat` discards all output. `SequenceFileOutputFormat` writes `SequenceFile`s and configures `SequenceFile.CompressionType`. `TextOutputFormat` writes text output through the synchronized nested `LineRecordWriter`, which owns a `DataOutputStream`.

`HashPartitioner` partitions keys by `Object.hashCode()`. `IntSumReducer` and `LongSumReducer` are concrete reducers that sum iterable numeric values for each key.

The `org.apache.hadoop.tools` entries expose command-line and MapReduce utilities. `DistCh` recursively changes file properties such as owner, group, and permissions. `DistCp` implements `Tool` for recursive filesystem copies and exposes configuration accessors, a static `copy(...)` helper, `run`, `main`, `getRandomId`, public logging, and `DuplicationException` for duplicate source files. `HadoopArchives` implements `Tool` for creating Hadoop archives with `archive`, `run`, and `main`. `Logalyzer` archives and analyzes Hadoop logs through `doArchive`, `doAnalyze`, and `main`; nested `LogComparator` is configurable and compares log keys as `Text` bytes, while nested `LogRegexMapper` is an old `mapred` mapper that extracts regex matches.

## Control Flow and Behavioral Contracts

Job setup flow is configuration-first. Callers construct a `Job`, set input/output formats, mapper/reducer/combiner/partitioner classes, key/value classes, comparators, job name, working directory, reduce count, and output/input paths through helper formats. Mutating setters are documented to throw `IllegalStateException` after submission, making the transition from `DEFINE` to `RUNNING` a public control boundary.

Submission and monitoring flow runs through `submit()` or `waitForCompletion(boolean)`. Once submitted, callers poll map and reduce progress, completion, success, counters, and task completion events; they can kill the job or kill/fail individual task attempts. `waitForCompletion` optionally prints progress and returns job success.

Input flow starts with `InputFormat.getSplits`, where configured paths and format-specific rules produce logical `InputSplit`s. The framework assigns splits to mappers using length and location data, creates a `RecordReader`, calls `initialize`, and repeatedly calls `nextKeyValue` until false. `MapContext` exposes the split and current record to mapper code.

Mapper control flow is lifecycle-based: `setup(Context)` runs once, `map(KEYIN, VALUEIN, Context)` runs for each input pair, `cleanup(Context)` runs once, and `run(Context)` coordinates the default loop. Overriding `run` gives full control but also requires preserving expected setup, iteration, cleanup, progress, and exception behavior.

Shuffle and reduce flow is grouped-key based. Map output is partitioned by `Partitioner`, sorted by the configured sort comparator, grouped by the grouping comparator, and passed to `Reducer.reduce` once per key group. `ReduceContext.nextKey()` and `nextKeyValue()` move through grouped reduce input; `getValues()` returns an iterable that reuses value objects for the current key.

Output flow is guarded by specs and commit protocol. `OutputFormat.checkOutputSpecs` validates the job output configuration. Tasks obtain a `RecordWriter` and write key/value pairs to attempt-specific work output. The committer decides whether there is work to commit, promotes successful task output, aborts failed output, and cleans up job-level temporary state.

File input control flow expands configured input paths, applies optional filters, validates non-empty inputs, computes split sizes from format minimum, configured min/max, and block size, finds block locality, and emits `FileSplit` objects. Subclasses can override splitability, minimum split size, list status, and record reader creation.

File output control flow uses static configuration on `Job` for compression, codecs, output path, and sequence-file compression type. Task filenames are generated from task IDs plus map/reduce markers and extensions; work paths live under temporary task directories so failed and speculative attempts can be discarded.

Identifier flow depends on stable parse, format, comparison, and serialization. `forName(String)` constructs IDs from public string forms, null inputs produce null per Javadoc, malformed strings raise `IllegalArgumentException`, and `compareTo` orders IDs by their hierarchical components.

Tool flow is MapReduce-driver oriented. `DistCp.run` lists source paths recursively, distributes copy work across map inputs, performs copying in mappers, and uses no meaningful reduce step. `HadoopArchives.run` lists archive sources, has mappers create archive parts, and uses a reducer to create archive indexes. `Logalyzer` has separate archive and analyze flows, with grep pattern, sort columns, and separator parameters shaping analysis output.

## State, Persistence, and Side Effects

This XML file itself is persistent compatibility metadata. It does not hold runtime implementation state, but it defines the public APIs that downstream compatibility checks, application source code, serialized records, and generated documentation rely on.

`Counters`, `ID`, `JobID`, `TaskID`, `TaskAttemptID`, and `FileSplit` expose `DataInput`/`DataOutput` serialization. Their binary field order and string forms are compatibility-sensitive because job history, task logs, filenames, RPC payloads, and user tooling can persist or display these values.

`Job` and `JobContext` state is configuration-backed. Job setup mutates `Configuration`/`JobConf` keys for classes, paths, comparators, compression, split settings, reduce counts, and output settings. Once submitted, mutable client-side control state is replaced by cluster-facing job state such as progress, counters, task events, tracking URL, and terminal success/failure.

Task context state is framework-owned. `TaskAttemptContext` stores attempt identity and status. `TaskInputOutputContext` delegates current input cursor, output writes, counters, status, and progress. `ReduceContext` additionally stores reduce input iteration state and grouping/value iterator behavior.

Filesystem side effects are central to `FileInputFormat`, `FileOutputFormat`, `FileOutputCommitter`, and the tools package. Input listing reads path metadata and block locality. Output committers create and delete temporary directories, move task outputs, and remove work directories. `DistCh`, `DistCp`, `HadoopArchives`, and `Logalyzer` can change ownership/permissions, copy trees, create archives and indexes, archive logs, and write analysis output.

Configuration side effects are exposed through many static helper methods. `FileInputFormat` persists input paths, path filters, and split bounds into the job. `FileOutputFormat` persists compression flags, compressor class, and output path. `SequenceFileOutputFormat` persists sequence-file compression type. `MultithreadedMapper` persists mapper class and thread count.

Concurrency is visible in two places. `TextOutputFormat.LineRecordWriter.write` and `close` are synchronized around a shared `DataOutputStream`. `MultithreadedMapper` intentionally invokes mapper logic concurrently, so application mapper implementations and any shared dependencies must be thread-safe.

## Dependencies and Integration Points

The chunk is centered on the newer `org.apache.hadoop.mapreduce` API but still bridges older Hadoop internals. `JobContext` stores an old `org.apache.hadoop.mapred.JobConf`; ID classes extend `org.apache.hadoop.mapred.ID`; `ReduceContext` depends on `org.apache.hadoop.mapred.RawKeyValueIterator`; `Logalyzer.LogRegexMapper` implements old `org.apache.hadoop.mapred.Mapper`; several APIs reference old task completion and output validation types.

Filesystem integration uses `org.apache.hadoop.fs.Path`, `FileSystem` behavior, file statuses, block locations, and `PathFilter`. File splits, output work paths, archive destinations, copy destinations, and log-analysis outputs all depend on Hadoop filesystem semantics.

Serialization and data-format dependencies include `org.apache.hadoop.io.Writable`, `WritableComparable`, `LongWritable`, `Text`, `RawComparator`, `SequenceFile`, `SequenceFile.CompressionType`, and compression codecs. Java IO dependencies include `DataInput`, `DataOutput`, `DataOutputStream`, `IOException`, and `Closeable`.

MapReduce integration points include `Configuration`, `Job`, `JobContext`, `TaskAttemptContext`, `TaskInputOutputContext`, `InputFormat`, `InputSplit`, `RecordReader`, `Mapper`, `Reducer`, `Partitioner`, `OutputFormat`, `RecordWriter`, `OutputCommitter`, `Counter`, `Counters`, and `StatusReporter`. The tools package integrates with `org.apache.hadoop.util.Tool` and command-line `main` methods.

External Java dependencies include `java.util.List`, `Iterable`, `Iterator`, arrays, `Class`, `StringBuilder`, and `java.text.NumberFormat`. `DistCp` exposes Apache Commons Logging through a public `Log` field. `Logalyzer.LogComparator` integrates with `org.apache.hadoop.conf.Configurable`.

## Risks and Compatibility Notes

The chunk begins inside the `Counters` class, so the class declaration and earlier counter APIs are in the preceding chunk. This range also closes the full XML document. The final merge lane should combine all nine chunks for this source file before producing a per-file report.

Because this file is a JDiff snapshot, signature-level changes are the primary risk. Altering method names, parameter types, checked exceptions, visibility, synchronized flags, inheritance, implemented interfaces, enum fields, or deprecation states would change the recorded Hadoop 0.20.2 compatibility contract.

Job mutability boundaries are important. Setters that are only valid before submission must continue to reject post-submission changes, and monitoring/control methods must preserve communication errors through declared `IOException` or interruption where documented.

Identifier compatibility is high-risk. `JobID`, `TaskID`, and `TaskAttemptID` string formats, parser behavior, compare ordering, equality, hash codes, and writable serialization are observed by logs, filenames, job history, UI links, and external tools. The docs warn against manual string parsing, but the public strings remain de facto integration points.

Input splitting affects correctness and performance. Edge cases include empty or missing input paths, path-filter behavior, compressed-file splitability, min/max split interactions, zero-length files, block-locality selection, and `InvalidInputException` aggregation without copying the problem list.

Output commit behavior protects correctness under retries and speculative execution. Bugs in work path generation, unique filename generation, existing-output checks, task commit promotion, abort cleanup, or job cleanup can produce duplicate output, partial output, lost side-effect files, or conflicts between simultaneous attempts.

Mapper and reducer lifecycle changes can break user subclasses. Setup/map-or-reduce/cleanup ordering, default identity behavior, exception propagation, object reuse in reduce values, counter/status/progress delegation, and custom `run` semantics are all part of application-visible behavior.

`MultithreadedMapper` is risky with mutable mapper fields, non-thread-safe libraries, shared output collectors, counters, status reporters, or record readers that assume single-threaded access. Its thread-count and mapper-class configuration keys are externally visible through the static getters/setters.

The tools APIs perform broad filesystem mutations. `DistCh` can recursively alter permissions and ownership, `DistCp` can copy or overwrite large directory trees and must handle duplicate sources and read failures, `HadoopArchives` creates persistent archive structure and indexes, and `Logalyzer` accepts regex/sort/separator inputs that can heavily affect output shape.

## Test Signals

JDiff-level validation should confirm the full XML remains well formed through the final `</api>` marker and that this chunk preserves all package names, class names, inheritance, implemented interfaces, constructors, methods, parameter types, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation states, and Javadoc blocks.

Counter and ID tests should cover `Counters` write/read round trips, total size calculation, textual output, `incrAllCounters`, equality/hash code, `ID` numeric comparison and serialization, and `JobID`/`TaskID`/`TaskAttemptID` constructor, parser, `toString`, `appendTo`, equality, hash, compare, map/reduce kind, and malformed/null parse behavior.

Job and context tests should cover every major setter/getter pair, post-submission mutation rejection, job jar lookup, tracking URL, map/reduce progress, completion/success checks, kill/fail task operations, task completion event paging, counters retrieval, `submit`, `waitForCompletion`, and configuration-backed class resolution in `JobContext`.

Mapper/reducer context tests should cover lifecycle ordering, default mapper and reducer behavior, custom `run`, current key/value cursor behavior, output writes, counter lookup by enum and group/name, status/progress delegation, reduce grouping behavior, value iterator object reuse, and exception propagation for `IOException` and `InterruptedException`.

Input tests should cover `FileInputFormat` path setters/adders/getters, comma-separated path handling, path filters, empty/missing inputs, min/max split settings, split-size computation, block index lookup, unsplittable compressed inputs, `FileSplit` writable round trips, `InvalidInputException` messages, `LineRecordReader` offsets/progress/close, `TextInputFormat` splitability, and sequence-file reader initialization/progress/current key/value behavior.

Map helper tests should cover `InverseMapper` key/value swapping, `TokenCounterMapper` tokenization and count emission, and `MultithreadedMapper` thread-count and mapper-class configuration plus concurrent execution with a deliberately thread-safe mapper.

Output tests should cover output path validation, existing-output rejection, compression flag and codec configuration, sequence-file compression type, work output path generation, unique map/reduce filenames, default work files, task setup/commit/abort/needs-commit/cleanup behavior, text output formatting and synchronized write/close, and `NullOutputFormat` discarding output.

Partition and reducer helper tests should cover `HashPartitioner` behavior for positive, negative, and zero hash codes across reduce counts, plus `IntSumReducer` and `LongSumReducer` sums for empty, single-value, multiple-value, negative, and overflow-adjacent inputs.

Tool tests should exercise `DistCh.run` argument handling and property changes, `DistCp.copy` and `run` for directory copies, duplicate source failures, ignored read failures, log path behavior, random ID generation, `HadoopArchives.archive` and archive index creation, `Logalyzer.doArchive`, `Logalyzer.doAnalyze` with grep/sort/separator options, `LogComparator` configuration and byte comparison, and `LogRegexMapper` extraction through old `mapred` mapper interfaces.
