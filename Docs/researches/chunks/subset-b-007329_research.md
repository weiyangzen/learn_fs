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
