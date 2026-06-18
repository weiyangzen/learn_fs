# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml lines 1-6117

## Scope and Purpose

This chunk is the opening portion of a JDiff-generated API description for Hadoop 0.18.2, produced on 2008-11-04 from the `src/core`, `src/mapred`, and `src/tools` source paths. It is not executable Java source; it is an XML snapshot of public and protected API signatures, deprecation state, inheritance, implemented interfaces, parameters, exceptions, fields, and copied Javadoc. The file feeds Hadoop's compatibility/reporting support under `dev-support/jdiff`, where later tooling can compare the 0.18.2 API surface against another release.

Lines 1-6117 cover the root `org.apache.hadoop` marker annotation, configuration APIs, distributed cache APIs, most core `org.apache.hadoop.fs` filesystem abstractions and implementations, and the beginning of `org.apache.hadoop.fs.ftp.FTPFileSystem`. The chunk ends in the middle of `FTPFileSystem.setWorkingDirectory`, so FTP-specific APIs continue in a later chunk.

## Important Packages and Types

- `org.apache.hadoop.HadoopVersionAnnotation` is a public annotation capturing the Hadoop version compiled into a package.
- `org.apache.hadoop.conf.Configurable` defines `setConf(Configuration)` and `getConf()` for objects wired by Hadoop configuration.
- `org.apache.hadoop.conf.Configuration` is the central property container. Its API exposes resource loading from classpath names, URLs, and `Path`s; typed accessors for strings, numbers, booleans, ranges, class names, and string arrays; class loading helpers; local path/file allocation; resource streams/readers; iteration over key/value pairs; non-default property serialization; classloader control; quiet mode; and a debugging `main`.
- `Configuration.IntegerRanges` parses strings such as `2-3,5,7-` and answers inclusion tests for positive integer ranges.
- `org.apache.hadoop.conf.Configured` is a convenience base implementation of `Configurable`.
- `org.apache.hadoop.filecache.DistributedCache` is a static utility class for MapReduce job-localization of read-only files, archives, and classpath additions.
- `org.apache.hadoop.fs.FileSystem` is the primary abstract filesystem API. It establishes URI-based filesystem binding, cached instance lifecycle, path qualification, block location discovery, stream creation/opening/appending, deletion, listing, globbing, copy helpers, local-output staging, ownership/permission operations, statistics, and shutdown behavior.
- `org.apache.hadoop.fs.FilterFileSystem`, `ChecksumFileSystem`, `LocalFileSystem`, `RawLocalFileSystem`, `HarFileSystem`, `InMemoryFileSystem`, and the start of `ftp.FTPFileSystem` are concrete or wrapper filesystem implementations around that base API.
- Stream contracts are represented by `FSInputStream`, `BufferedFSInputStream`, `FSDataInputStream`, `FSOutputSummer`, `FSDataOutputStream`, `Seekable`, `PositionedReadable`, and `Syncable`.
- Metadata/data-transfer helpers include `BlockLocation`, `FileStatus`, `ContentSummary`, `Path`, `PathFilter`, `FileUtil`, `FileUtil.HardLink`, `DF`, `DU`, `LocalDirAllocator`, `Trash`, `FsShell`, `FsUrlStreamHandlerFactory`, `ChecksumException`, `FSError`, `ShellCommand`, and `FTPException`.

## Configuration API Behavior

`Configuration` models Hadoop runtime state as ordered XML resources plus programmatic overrides. Resources loaded later override earlier resources unless an earlier property is marked final. The documented default load order is `hadoop-default.xml` followed by `hadoop-site.xml`, with applications able to add more resources afterward. Returned values can undergo variable expansion against other configuration keys and then Java system properties. `getRaw` bypasses that expansion.

The class provides typed accessors but generally falls back to caller-supplied defaults when a key is missing or malformed. Its class helpers are integration-critical: `getClassByName`, `getClass(name, defaultValue)`, `getClass(name, defaultValue, xface)`, and `setClass` make configuration the factory input for pluggable Hadoop components. `getLocalPath` and `getFile` select/create a local path under one of the directories named by a configuration property, which ties configuration directly into local disk allocation. `write(OutputStream)` serializes non-default properties, so configuration is also a persistence boundary for job/runtime state.

`setQuietMode` is synchronized and controls whether configuration errors/information are logged. `main(String[])` is a debug endpoint for listing non-default properties.

## Distributed Cache Behavior

`DistributedCache` exposes the MapReduce localization contract for files and archives specified as URIs. The two `getLocalCache` overloads either use a supplied `FileStatus` or resolve the status internally. They copy/cache the resource under a base directory, validate modification timestamps against the job-start timestamp, unpack archives with `.zip`, `.jar`, `.tar`, `.tgz`, and `.tar.gz` extensions, and optionally create symlinks in a task working directory.

Configuration keys are the persistent state carrier for cache URIs, localized paths, timestamps, classpath entries, and symlink policy. The API has setters/getters for cache archives/files, local archives/files, archive/file timestamps, archive/file classpath entries, and append-style helpers (`addCacheArchive`, `addCacheFile`, `addFileToClassPath`, `addArchiveToClassPath`). `checkURIs` validates that symlink fragments exist and do not conflict. `releaseCache` releases a localized resource, while `purgeCache` clears backing files and is documented as server-reinitialization-only because users lose cached files.

Risk signals include timestamp drift if inputs mutate during job execution, fragment conflicts when symlinks are enabled, and destructive cache purge behavior.

## Core Filesystem Contracts

`FileSystem` is the central abstraction for local, distributed, archive, memory, and protocol-backed filesystems. Static factory methods resolve an implementation from configuration using URI scheme properties of the form `fs.<scheme>.class`. `get(Configuration)`, `get(URI, Configuration)`, `getLocal(Configuration)`, deprecated `getNamed`, and `closeAll()` imply a cache of filesystem instances and a shared lifecycle. `getDefaultUri` and `setDefaultUri` persist default FS binding in `Configuration`.

Implementations must provide `initialize(URI, Configuration)`, `getUri()`, `open(Path, int)`, the full permission-aware `create(...)`, `append(Path, int, Progressable)`, `rename`, both delete forms, `listStatus(Path)`, working-directory setters/getters, `mkdirs(Path, FsPermission)`, and `getFileStatus(Path)`. Non-abstract overloads layer convenience behavior over these primitives: default buffer sizes, default overwrite behavior, default replication/block sizes, copy/move helpers, path qualification, existence/type checks, content summary, globbing, local staging via `startLocalOutput`/`completeLocalOutput`, and permission/owner operations.

Several APIs are explicitly deprecated in favor of newer contracts: `getName()` in favor of `getUri()`, `getNamed()` in favor of `get(URI, Configuration)`, path-based `getFileBlockLocations` in favor of status-based lookup, one-argument `delete(Path)` in favor of `delete(Path, boolean)`, and old status accessors such as `getReplication`, `isDirectory`, `getLength`, and `getBlockSize` in favor of `getFileStatus()`.

`FileSystem.Statistics` tracks bytes read/written. `getStatistics(Class<? extends FileSystem>)` and `printStatistics()` are synchronized static methods, indicating global per-implementation accounting.

## Filesystem Metadata and Path Types

`BlockLocation` is a `Writable` containing host names, name strings, offset, and length. It is returned by block-location APIs and serializes/deserializes through `write(DataOutput)` and `readFields(DataInput)`.

`FileStatus` is a `Writable` and `Comparable` carrying length, directory flag, replication, block size, modification time, permission, owner, group, and `Path`. Equality, ordering, and hash code are path-based. Protected setters normalize null permission/owner/group values to defaults, which matters for filesystems without native permission or identity models.

`ContentSummary` is a `Writable` for length, directory count, file count, and quota, with formatted output helpers for quota and non-quota display. This is the metadata object behind `FileSystem.getContentSummary`.

`Path` wraps URI-like path strings with Hadoop-specific normalization. It supports construction from strings, parent/child pairs, URI components, conversion to `URI`, lookup of owning `FileSystem`, parent/name/suffix/depth helpers, qualification against a filesystem, and comparison/equality/hash operations. Static constants define `/`, slash as a char, and the current-directory marker.

`PathFilter` accepts/rejects paths for listing/globbing. `PositionedReadable` guarantees thread-safe reads at an explicit file position without changing the stream offset. `Seekable` declares mutable-position reads with `seek`, `getPos`, and alternate-source seek. `Syncable` declares durable buffer/device synchronization.

## Stream and Checksum Flow

`FSInputStream` is the abstract seekable/positioned read base. Its positioned `read` and `readFully` methods let callers read from absolute offsets, while concrete implementations provide seek and source-switching behavior. `BufferedFSInputStream` wraps an `FSInputStream` with buffering while preserving seek and positional-read APIs. `FSDataInputStream` wraps an input stream as a `DataInputStream`, adding `Seekable` and `PositionedReadable`; its constructor can throw if the wrapped stream is incompatible.

`FSInputChecker` is an abstract `FSInputStream` for checksum-verified input. Subclasses implement `readChunk` and `getChunkPosition`. It synchronizes stateful methods such as `read`, `skip`, `seek`, `available`, `getPos`, `needChecksum`, and checksum parameter updates. It validates chunk checksums before exposing bytes and may throw `ChecksumException` on corrupt chunks. It explicitly allows `skip`/`seek` past EOF without immediate failure, with later reads returning EOF. `mark`, `reset`, and `markSupported` are final, so callers should not rely on mark/reset behavior.

`FSOutputSummer` is the write-side checksum generator. It buffers bytes into checksum chunks, computes checksums, and delegates each completed chunk to abstract `writeChunk`. Its write and buffer-flush methods are synchronized. `FSDataOutputStream` wraps output as a `DataOutputStream`, exposes stream position, `sync()`, wrapped stream access, close behavior, and optional statistics accounting.

`ChecksumFileSystem` composes a raw filesystem through `FilterFileSystem` and creates sidecar checksum files. It exposes checksum filename computation, checksum length calculations, bytes-per-sum, checksum-aware open/create/append/copy/delete/list/rename/mkdir behavior, checksum failure reporting, and raw filesystem access. The documented persistence model is client-side checksum files beside raw files.

`ChecksumException` captures the corrupt position. `FSError` represents unexpected local disk-level errors as `Error`, not checked exceptions.

## Utility and Local Disk APIs

`FileUtil` is a broad static utility surface for converting `FileStatus[]` to `Path[]`, recursive delete on local or Hadoop filesystems, copy/copy-merge between filesystems and local files, shell path conversion, local disk usage, unzip/untar, symlink creation, chmod, local temp-file creation, and replace-file moves. `FileUtil.HardLink` creates hard links and reads link counts across Unix, Cygwin, and Windows XP.

`DF` and `DU` extend `org.apache.hadoop.util.Shell` and wrap Unix `df`/`du` behavior. `DF` exposes filesystem, capacity, used, available, percent used, mount, command construction, parsing, and a `DF_INTERVAL_DEFAULT`. `DU` tracks disk usage with increment/decrement adjustment APIs, a refresh thread (`start`/`shutdown`), shell command construction, and parsing.

`LocalDirAllocator` coordinates round-robin allocation across configured local directories for write/read/temp paths. It can consider known file sizes, skip disks without sufficient space, verify writability, scan configured directories for reads, and keep one allocator per context string such as `mapred.local.dir` or `dfs-client`-style keys. The documentation warns that it does not handle a disk becoming read-only or full while a file is already being written.

`RawLocalFileSystem` implements `FileSystem` over local Java files and shell commands for ownership/permissions. It exposes local path conversion, `file:` URI/name, open/create/append/rename/delete/list/mkdirs/status, working directory, local-output staging, close, deprecated lock/release, and `chown`/`chmod` integration. `LocalFileSystem` wraps it with `ChecksumFileSystem`, adding checksum handling and moving corrupted data/checksum files aside through `reportChecksumFailure`.

## Specialized Filesystems and Shell Integration

`FilterFileSystem` forwards most `FileSystem` operations to a protected wrapped `fs` field. It is the extension point for wrappers that transform behavior while relying on an underlying filesystem.

`HarFileSystem` is a read-oriented Hadoop Archive filesystem layered over another FS. A HAR URI can encode an underlying scheme/host/port and archive path, or default to the configured underlying FS. It uses `_masterindex` and `_index` files to map archived paths into `part-*` content files, with hash ranges and index offsets for faster lookup. It supports archive initialization, version lookup, status lookup, block-location mapping to the underlying FS, read/list/copy-to-local, and path qualification. Many mutating APIs are documented as not implemented: create, replication changes, delete, mkdirs, copy-from-local, local-output staging, owner, and permission changes.

`InMemoryFileSystem` is a checksum filesystem with `ramfs://` URIs. It assumes file lengths are known ahead of time and total data size is bounded by configuration. Callers must reserve space, including checksum space, through `reserveSpaceWithCheckSum(Path, long)` before creating files. It exposes file listing/counting, total size, and percent used.

`FsShell` provides command-line access to a `FileSystem`, implements `Tool`, and holds the active FS plus date formatters. Its visible API covers initialization, current trash lookup, byte-size formatting, two-decimal limiting, `run`, `close`, and `main`.

`FsUrlStreamHandlerFactory` integrates Java URL handling with Hadoop `FileSystem` implementations. Before returning a handler for a protocol, it checks that `FileSystem` knows an implementation for that scheme.

`Trash` models user trash as `$home/.Trash/current` plus checkpoint directories. It can move paths to trash, checkpoint current trash, expunge old checkpoints, return a superuser-run emptier `Runnable`, and run an emptier from `main`. Its design avoids requiring full trash enumeration, filesystem date support, or clock synchronization.

`ShellCommand` is a deprecated alias/base for shell commands and points callers to `org.apache.hadoop.util.Shell`.

## FTP API Surface in This Chunk

`FTPException` is a runtime wrapper for messages and nested throwables.

The `FTPFileSystem` declaration begins at the end of the chunk. Visible APIs include `initialize(URI, Configuration)`, `open`, full permission-aware `create`, unsupported `append`, deprecated one-argument `delete`, recursive `delete`, `getUri`, `listStatus`, `getFileStatus`, `mkdirs`, `rename`, `getWorkingDirectory`, `getHomeDirectory`, and the beginning of `setWorkingDirectory`. The `create` Javadoc warns that an obtained stream must be closed before any other `FTPFileSystem` API call or those calls may block, indicating a single-connection or serialized FTP operation model. The rest of the class is outside this chunk.

## Dependencies and Integration Points

This API snapshot depends heavily on Java standard library types (`java.io`, `java.net.URI/URL`, `java.util`, `java.util.zip.Checksum`, `java.text.SimpleDateFormat`) and Hadoop core contracts (`Configuration`, `Path`, `FileSystem`, `Writable`, `FsPermission`, `Progressable`, `Tool`, `Shell`). The generated command line in the XML header shows the broader build-time classpath: commons-cli, commons-codec, commons-httpclient, commons-logging, commons-net, Jetty/JSP libraries, JUnit, KFS, log4j, ORO, servlet API, SLF4J, xmlenc, Ant, and the Java 1.5 toolchain.

Runtime integration is centered on `Configuration`: it chooses filesystem implementations, stores default filesystem URIs, local directory contexts, distributed cache metadata, classpath entries, and typed configuration values. Filesystem implementations integrate through URI schemes (`file`, `har`, `ramfs`, `ftp`, and distributed FS schemes in later packages), while Java URL integration goes through `FsUrlStreamHandlerFactory`.

Persistence boundaries visible in this chunk include XML configuration resources, serialized `Writable` metadata (`BlockLocation`, `FileStatus`, `ContentSummary`), checksum sidecar files, HAR index files (`_masterindex`, `_index`) and part files, distributed-cache local copies/unpacked archives and configuration timestamps, local trash checkpoints, and global filesystem statistics.

## Control Flow Signals

The XML does not include method bodies, but the documented public contracts imply these key flows:

1. Filesystem selection: user/configured path or default URI -> `Path.getFileSystem` or `FileSystem.get` -> configuration property `fs.<scheme>.class` -> construct and `initialize(URI, Configuration)` -> cached FS instance.
2. File creation: convenience `create` overloads resolve defaults -> abstract permission-aware `create` implementation -> `FSDataOutputStream` -> optional checksum generation through `FSOutputSummer` or `ChecksumFileSystem`.
3. File reading: `open` returns `FSDataInputStream` -> seek/positioned reads delegate to `FSInputStream` -> `FSInputChecker` subclasses verify checksums chunk by chunk when enabled.
4. Metadata/listing: `listStatus`, `globStatus`, and filters produce `FileStatus` arrays -> utility conversion to `Path[]` or content summaries.
5. Local staging: remote filesystems may write temporary local files from `startLocalOutput` and upload them through `completeLocalOutput`; local filesystems can write directly to the target.
6. Distributed cache localization: job config lists files/archives and timestamps -> task-local call to `getLocalCache` validates timestamps, copies/unpacks resource, records localized paths, and creates optional symlinks.
7. HAR access: HAR URI initialization opens an underlying filesystem and index files -> lookup hashes/offsets into index -> file reads map archive paths to part-file offsets and synthetic EOF.
8. Trash deletion: `moveToTrash` moves original paths into `.Trash/current` preserving original paths -> `checkpoint` rotates current trash -> `expunge` deletes old checkpoints.

## Risks and Compatibility Notes

- This is a generated compatibility artifact, so accidental manual edits or regeneration with a different JDiff/Javadoc toolchain can create noisy API diffs unrelated to source changes.
- The file uses `iso-8859-1` encoding and XML CDATA containing Javadoc HTML. XML parsers and diff tools should preserve encoding and CDATA structure.
- Many filesystem APIs are overloaded and several older methods remain deprecated but present. Compatibility tooling should distinguish deprecation changes from removals.
- `FileSystem` factory/caching behavior means implementation selection and lifecycle bugs can be global within a JVM. `closeAll()` can break consumers still holding cached instances.
- `ChecksumFileSystem`, `LocalFileSystem`, and stream checksum classes rely on client-side checksum sidecars; stale or partially moved checksum files are a corruption/retry risk.
- `FSInputChecker`, `FSOutputSummer`, `FSDataInputStream.seek`, and statistics APIs expose synchronized state, while `PositionedReadable` promises thread-safe reads without changing current offset. Implementations must honor that split.
- `LocalDirAllocator` explicitly does not handle disks becoming read-only or full during an active write.
- `DistributedCache` assumes cached resources are read-only while jobs execute and uses modification timestamps for validation; external mutation can invalidate tasks.
- `HarFileSystem` is mostly read-only and loses original file permission persistence, returning archive index-file permissions instead.
- `FTPFileSystem.create` can block later calls until the stream is closed, a significant integration risk for callers expecting independent operations.
- The chunk ends mid-class, so any per-file merge must combine later chunks before making whole-file claims about `FTPFileSystem` and subsequent packages.

## Test Signals

- XML validity: this chunk starts with a valid XML declaration and `<api>` root metadata, but only the full file can be parsed because later chunks close the open structures.
- JDiff contract checks should verify package/class/method/field order, visibility, abstract/static/final flags, deprecation strings, parameter/exception lists, and CDATA documentation are preserved.
- Configuration behavior tests should cover resource override ordering, final-parameter protection, variable expansion, raw reads, typed default fallback, class/interface validation, local path/file selection, and serialization of non-default properties.
- Filesystem compatibility tests should exercise factory lookup by URI scheme, default URI persistence, cached instance close behavior, path qualification/checking, `FileStatus`-based replacements for deprecated methods, glob/list filtering, delete recursion, copy/move helpers, ownership/permission defaults, and statistics counters.
- Stream tests should cover seeking, positioned reads preserving current offset, checksum pass/fail paths, EOF after seek/skip beyond end, output checksum chunk boundaries, `sync`, and close/statistics behavior.
- Local and utility tests should cover recursive delete partial failures, copy-merge ordering, unzip/untar extraction, symlink/chmod shell failures, hard-link counts, `DF`/`DU` parsing on supported platforms, and local temp-file replacement.
- Specialized filesystem tests should cover distributed-cache timestamp mismatches and symlink fragment conflicts, HAR index lookup/list/open behavior and unsupported mutation methods, in-memory reservation failure when space is insufficient, trash checkpoint/expunge behavior, and FTP stream-close blocking semantics.
