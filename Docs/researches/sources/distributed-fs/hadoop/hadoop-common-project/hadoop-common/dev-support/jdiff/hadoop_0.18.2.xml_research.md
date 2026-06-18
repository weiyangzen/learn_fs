# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007273`: lines 1-6117, `Docs/researches/chunks/subset-b-007273_research.md`
- `subset-b-007274`: lines 6118-12396, `Docs/researches/chunks/subset-b-007274_research.md`
- `subset-b-007275`: lines 12397-18635, `Docs/researches/chunks/subset-b-007275_research.md`
- `subset-b-007276`: lines 18636-24770, `Docs/researches/chunks/subset-b-007276_research.md`
- `subset-b-007277`: lines 24771-30885, `Docs/researches/chunks/subset-b-007277_research.md`
- `subset-b-007278`: lines 30886-37174, `Docs/researches/chunks/subset-b-007278_research.md`
- `subset-b-007279`: lines 37175-38788, `Docs/researches/chunks/subset-b-007279_research.md`

## Chunk Research

### subset-b-007273: lines 1-6117

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

### subset-b-007274: lines 6118-12396

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml lines 6118-12396

## Purpose

This chunk is a JDiff public API snapshot for Hadoop Common 0.18.2. It spans the tail of the FTP filesystem API, complete API surfaces for KFS, permissions, S3 and native S3 filesystems, shell command helpers, and a large portion of `org.apache.hadoop.io`. The XML records Java signatures, inheritance, visibility, synchronization, deprecation status, exceptions, fields, and selected Javadoc. It is not implementation code, but it defines the compatibility contract that implementation code, downstream applications, and later API-diff tooling must preserve or compare against.

The most important architectural themes in this slice are:

- Filesystem adapters that expose Hadoop `FileSystem` semantics over FTP, Kosmos/KFS, block-based S3, and native S3.
- Permission metadata objects that serialize user/group/mode information through Hadoop `Writable`.
- S3 metadata and migration contracts that separate inode metadata from block data.
- Hadoop binary serialization primitives and containers, including `WritableComparable`, raw comparators, `MapFile`, `SetFile`, `ArrayFile`, and `SequenceFile`.
- Stream and buffer helpers used by serializers, sorters, and filesystem clients.

## Package And Type Inventory

### `org.apache.hadoop.fs.ftp`

The chunk starts at the end of `FTPFileSystem` and includes its public `LOG`, `DEFAULT_BUFFER_SIZE`, and `DEFAULT_BLOCK_SIZE` fields plus documentation describing an FTP-backed `FileSystem` implemented with Apache Commons Net. The visible tail includes methods from the surrounding class immediately before the chunk boundary: `getFileStatus(Path)`, `mkdirs(Path, FsPermission)`, `rename(Path, Path)`, `getWorkingDirectory()`, `getHomeDirectory()`, and `setWorkingDirectory(Path)`.

`FTPInputStream` extends `FSInputStream` and wraps a `java.io.InputStream`, `org.apache.commons.net.ftp.FTPClient`, and `FileSystem.Statistics`. Its public API covers:

- Positional operations: `getPos()`, `seek(long)`, and `seekToNewSource(long)`.
- Synchronized reads: `read()` and `read(byte[], int, int)`.
- Synchronized `close()`.
- Mark/reset facade methods: `markSupported()`, `mark(int)`, and `reset()`.

The synchronization on reads and close is a signal that FTP stream state and statistics updates are mutable shared state. Seeking on FTP is inherently limited by remote server behavior; callers should expect `IOException` and should test byte position accounting, repeated close, and seek behavior around EOF.

### `org.apache.hadoop.fs.kfs`

`KosmosFileSystem` extends `FileSystem` and exposes a KFS-backed filesystem. Its contract mirrors Hadoop filesystem methods:

- Identity and initialization: constructor, `initialize(URI, Configuration)`, `getUri()`, and legacy `getName()`.
- Working directory: `getWorkingDirectory()` and `setWorkingDirectory(Path)`.
- Namespace/status: `mkdirs(Path, FsPermission)`, `isDirectory(Path)`, `isFile(Path)`, `listStatus(Path)`, and `getFileStatus(Path)`.
- Data operations: `create(Path, FsPermission, boolean, int, short, long, Progressable)`, `open(Path, int)`, `rename(Path, Path)`, and `delete(Path, boolean)` plus a legacy `delete(Path)`.
- File metadata: `getLength(Path)`, `getReplication(Path)`, `getDefaultReplication()`, `setReplication(Path, short)`, and `getDefaultBlockSize()`.
- Coordination/local-output hooks: `lock(Path, boolean)`, `release(Path)`, `copyFromLocalFile(boolean, Path, Path)`, `copyToLocalFile(boolean, Path, Path)`, `startLocalOutput(Path, Path)`, and `completeLocalOutput(Path, Path)`.
- Block placement: `getFileBlockLocations(FileStatus, long, long)` returns KFS chunk locations or null when the file does not exist.

`append(Path, int, Progressable)` is explicitly documented as unsupported. Compatibility tests should assert both that the method exists and that implementation behavior remains clear for unsupported append, especially because `FileSystem` callers may probe optional append support.

### `org.apache.hadoop.fs.permission`

`AccessControlException` extends `IOException` and has a default constructor for `RemoteException` unwrapping plus a message constructor. It is the checked exception surface for access-control failures.

`FsAction` is an enum-like public type with `values()`, `valueOf(String)`, `implies(FsAction)`, `and(FsAction)`, `or(FsAction)`, `not()`, and public final fields `INDEX` and `SYMBOL`. The API models Unix-style action algebra in both octal and symbolic forms. Downstream correctness depends on stable truth tables for implication and bit operations.

`FsPermission` implements `Writable` and is the serialized permission mode object. It can be built from three `FsAction`s, a `short`, or another `FsPermission`. Important APIs:

- Immutable factory: `createImmutable(short)`.
- Accessors: `getUserAction()`, `getGroupAction()`, `getOtherAction()`.
- Serialization: `fromShort(short)`, `toShort()`, `write(DataOutput)`, `readFields(DataInput)`, and static `read(DataInput)`.
- Object contracts: `equals(Object)`, `hashCode()`, and `toString()`.
- Mask/default helpers: `applyUMask(FsPermission)`, static `getUMask(Configuration)`, `setUMask(Configuration, FsPermission)`, `getDefault()`, and `valueOf(String)`.
- Public constants: `UMASK_LABEL` and `DEFAULT_UMASK`.

`PermissionStatus` implements `Writable` and stores owner, group, and `FsPermission`. Its API includes immutable creation, getters, `applyUMask(FsPermission)`, `readFields`, `write`, static `read(DataInput)`, static component `write(DataOutput, String, String, FsPermission)`, and `toString()`. These objects are part of namespace persistence and RPC serialization; tests should round-trip them through `DataOutput/DataInput` and verify umask application does not mutate immutable instances unexpectedly.

### `org.apache.hadoop.fs.s3`

This is the older block-based S3 filesystem API. It models Hadoop files as inode metadata plus separate block objects, not as native one-object-per-file S3 keys.

`Block` holds S3 block metadata with an id and length. It has `getId()`, `getLength()`, and `toString()`.

`FileSystemStore` is the storage abstraction behind `S3FileSystem`. It exposes:

- Initialization and versioning: `initialize(URI, Configuration)` and `getVersion()`.
- Metadata persistence: `storeINode(Path, INode)`, `inodeExists(Path)`, `retrieveINode(Path)`, and `deleteINode(Path)`.
- Block persistence: `storeBlock(Block, File)`, `blockExists(long)`, `retrieveBlock(Block, long byteRangeStart)`, and `deleteBlock(Block)`.
- Listing and diagnostics: `listSubPaths(Path)`, `listDeepSubPaths(Path)`, `purge()`, and `dump()`.

`purge()` is documented as test-only destructive behavior. `dump()` is diagnostic. Both are public and therefore need guardrails in integration tests to avoid accidental production data loss.

`INode` stores a file type and block list. Its API includes `getBlocks()`, `getFileType()`, `isDirectory()`, `isFile()`, `getSerializedLength()`, `serialize()`, static `deserialize(InputStream)`, and public static fields `FILE_TYPES` and `DIRECTORY_INODE`. This is the persistent metadata format for the block-based S3 filesystem, so binary compatibility of serialization is crucial. `MigrationTool` exists specifically because older/newer stored metadata versions can diverge; it migrates by rewriting block metadata and explicitly does not touch data files.

`S3Credentials` extracts AWS credentials from the filesystem URI or configuration and throws `IllegalArgumentException` when credentials cannot be determined. `S3Exception` is a runtime wrapper for S3 communication failures. `S3FileSystemException` and `VersionMismatchException` are checked exceptions for fatal filesystem use and stored-version mismatches.

`S3FileSystem` extends `FileSystem` and uses a `FileSystemStore`. It supports construction with a store, `initialize`, `getUri`, `getName`, working directory methods, `mkdirs`, `isFile`, `listStatus`, `create`, `open`, `rename`, `delete`, and `getFileStatus`. Permissions on `mkdirs` and `create` are documented as currently ignored. `append` is explicitly unsupported. Risk areas are eventual consistency, non-atomic rename/delete over object storage, credential leakage through URIs, metadata version mismatches, and orphaned blocks or inodes after partial failures.

### `org.apache.hadoop.fs.s3native`

`NativeS3FileSystem` extends `FileSystem` and uses `NativeFileSystemStore`. Unlike the block-based `S3FileSystem`, it stores files in native S3 form so non-Hadoop S3 tools can read them. Public methods include `initialize`, unsupported `append`, `create`, overloaded `delete`, `getFileStatus`, `getUri`, `listStatus`, `mkdirs`, `open`, `rename`, `setWorkingDirectory`, and `getWorkingDirectory`; `LOG` is a public static final logger.

The `listStatus(Path)` Javadoc is a useful operational signal: listing a file makes a single S3 call, while listing a directory may make `(n / 1000) + 2` S3 calls for `n` direct children. Tests and production callers should account for pagination, latency, and cost. Rename remains a semantic risk because S3 lacks native atomic directory rename.

### `org.apache.hadoop.fs.shell`

`Command` is a shell command base with a `FileSystem`, `String[] args`, `getCommandName()`, `run(Path)`, and `runAll()`. `CommandFormat` parses options and argument count constraints with `parse(String[], int)` and `getOpt(String)`. `Count` extends `Command`, has `NAME`, `USAGE`, and `DESCRIPTION` fields, a constructor accepting args/start index/fs, `matches(String)`, `getCommandName()`, and `run(Path)`.

These APIs integrate shell argument parsing with filesystem operations. Test signals are option parsing edge cases, min/max positional argument enforcement, glob/list expansion from the base command, and error aggregation through `runAll()`.

## `org.apache.hadoop.io` Serialization And Container APIs

### Type registries and collection writables

`AbstractMapWritable` is an abstract base for `MapWritable` and `SortedMapWritable`. It implements both `Writable` and `Configurable`, and carries class-id maps in each instance rather than static process-wide maps. Public/protected API includes synchronized `addToMap(Class)`, `getClass(byte)`, `getId(Class)`, synchronized `copy(Writable)`, `getConf()`, `setConf(Configuration)`, `write(DataOutput)`, and `readFields(DataInput)`. The documented id range is 1 to 127, so instance data cannot contain more than 127 distinct classes. This is a hard compatibility and failure-mode point for complex nested maps.

`MapWritable` implements `Map<Writable, Writable>` over `AbstractMapWritable`. It exposes normal map operations, copy construction, and overrides `write`/`readFields` to serialize both the class registry and entries. `SortedMapWritable` implements `SortedMap<WritableComparable, Writable>` with range views (`headMap`, `subMap`, `tailMap`), ordered key access (`firstKey`, `lastKey`), map operations, and writable round-trip. Test cases should include nested map values, copy constructors, class registry stability after deserialization, and the 127-class ceiling.

`ArrayWritable` stores homogeneous `Writable` arrays and records the value class. It provides constructors for a value class, value class plus values, and `String[]`, plus `getValueClass()`, `toStrings()`, `toArray()`, `set(Writable[])`, `get()`, `readFields`, and `write`. Its Javadoc warns that reducer inputs typically need a subclass fixing the element type, which is a common MapReduce integration constraint.

`GenericWritable` is a configurable wrapper around one of a bounded set of `Writable` implementation classes supplied by subclass `getTypes()`. It exposes `set(Writable)`, `get()`, `toString()`, `readFields`, `write`, `getConf()`, and `setConf(Configuration)`. The risk is type admission: serialization only works for whitelisted classes, so subclass tests should cover every advertised type and rejection of unknown types.

### Primitive and byte writables

`BooleanWritable`, `ByteWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, and `DoubleWritable` are mutable primitive wrappers implementing `WritableComparable`. Each has default and value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`. Each also has an optimized nested `Comparator` extending `WritableComparator` for raw byte comparisons; `LongWritable` adds `DecreasingComparator`.

`BytesWritable` is a resizable byte sequence usable as key or value. It distinguishes logical size from capacity, exposes `get()`, `getSize()`, `setSize(int)`, `getCapacity()`, `setCapacity(int)`, `set(BytesWritable)`, `set(byte[], int, int)`, `readFields`, `write`, `hashCode`, `compareTo`, `equals`, and `toString()`. The backing array from `get()` is only valid over `[0, getSize())`. Sorting is documented as `memcmp`-style, and hash code uses the front of the MD5 of the buffer. Tests should cover mutation after `get()`, serialized length prefixes, capacity shrink/expand preservation, and comparator parity with object `compareTo`.

`NullWritable` is a singleton empty value with `get()`, no-op `readFields`/`write`, stable `equals`, `hashCode`, `compareTo`, and an optimized comparator. It is often used for map-only keys or set-like outputs; the main risk is accidental state assumptions because all instances are equivalent.

`MD5Hash` implements `WritableComparable` for 16-byte MD5 digests. APIs include constructors from empty/string/bytes, `readFields`, static `read(DataInput)`, `write`, `set(MD5Hash)`, `getDigest()`, digest factories for `byte[]`, `String`, `InputStream`, and `byte[][]`, `halfDigest()`, `quarterDigest()`, `equals`, `hashCode`, `compareTo`, `toString`, `setDigest(String)`, constant `MD5_LEN`, and raw comparator. Persistent callers should treat string parsing and binary digest length as strict validation surfaces.

### Compression, buffers, stringification, and object serialization

`CompressedWritable` is an abstract base class whose final `readFields(DataInput)` and `write(DataOutput)` store compressed state, while subclasses implement `readFieldsCompressed(DataInput)` and `writeCompressed(DataOutput)`. `ensureInflated()` must be called by field accessors. The behavior is optimized for large immutable-ish objects copied between files. Risks are stale inflated state after mutation, subclasses bypassing `ensureInflated`, and compression format compatibility.

`DataInputBuffer` extends `DataInputStream` and can reset over a byte array with a start/length range. It exposes `getData()`, `getPosition()`, and `getLength()`. `DataOutputBuffer` extends `DataOutputStream`, exposes its backing data and length, supports reset, and writes a byte range from `DataInput`. `InputBuffer` and `OutputBuffer` are lower-level `FilterInputStream`/`FilterOutputStream` wrappers with reset, position/length, data/length access, and resettable output. These buffers are heavily used by raw comparators, sorters, and serializers; tests should include buffer reuse, offset handling, and no-copy aliasing assumptions.

`DefaultStringifier<T>` implements `Stringifier<T>` using Hadoop serializers. It can convert objects to/from strings and has static helpers to `store`, `load`, `storeArray`, and `loadArray` values in `Configuration`. `Stringifier<T>` itself is a closeable interface with `toString(T)`, `fromString(String)`, and `close()`. These APIs integrate object serialization with config values; risks include serializer availability, base64/string encoding compatibility, and resource closure.

`ObjectWritable` implements `Writable` and `Configurable` for arbitrary declared classes and object instances. It exposes constructors, `get()`, `getDeclaredClass()`, `set(Class, Object)`, `toString()`, `readFields`, `write`, static `writeObject(DataOutput, Object, Class, Configuration)`, and static `readObject(DataInput, ObjectWritable, Configuration)`/`readObject(DataInput, Configuration)`. This is an RPC and generic serialization bridge. Compatibility depends on primitive handling, declared-class fidelity, null handling, and passing `Configuration` into configurable payloads.

`RawComparator<T>` extends `Comparator<T>` and adds byte-level `compare(byte[], int, int, byte[], int, int)`. It is the key abstraction behind efficient sorting without deserializing every key.

`IOUtils` provides static stream helpers: several `copyBytes` overloads for `InputStream`/`OutputStream` with buffer size and close behavior, `readFully(InputStream, byte[], int, int)`, `skipFully(InputStream, long)`, `cleanup(Log, Closeable...)`, `closeStream(Closeable)`, and `closeSocket(Socket)`. `IOUtils.NullOutputStream` discards writes. Tests should cover close-on-success/close-on-failure behavior, short reads/skips, and exception swallowing in cleanup paths.

`Closeable` in `org.apache.hadoop.io` is deprecated in favor of `java.io.Closeable` but remains a public compatibility artifact.

## File-Backed Data Structures

### `ArrayFile`

`ArrayFile` is a dense file-backed mapping from integer positions to values and extends `MapFile`. `ArrayFile.Reader` extends `MapFile.Reader`, offering `seek(long)`, `next(Writable)`, `key()`, and `get(long, Writable)`. `ArrayFile.Writer` extends `MapFile.Writer` and appends values, using implicit increasing long keys. The synchronization on reader and writer operations indicates mutable cursor/output state.

Persistent behavior depends on the underlying `MapFile` data/index layout and monotonically increasing keys. Tests should cover random access by index, append order, EOF behavior, and compatibility with `SequenceFile` compression choices.

### `MapFile`

`MapFile` is documented as a directory containing two files:

- `data`: all sorted key/value records.
- `index`: a smaller sampled index containing a fraction of keys controlled by `Writer#getIndexInterval()`.

Public static helpers include `rename(FileSystem, String, String)`, `delete(FileSystem, String)`, `fix(FileSystem, Path, Class, Class, boolean, Configuration)`, and `main(String[])`. Constants `INDEX_FILE_NAME` and `DATA_FILE_NAME` name the persistent files. `fix` can recreate a corrupt index and returns the number of valid entries, or `-1` if no fix was needed.

`MapFile.Reader` opens a map, exposes key/value classes, can defer stream opening via a protected constructor and `open`, can specialize the data reader with `createDataFileReader`, and provides synchronized cursor/query operations: `reset`, `midKey`, `finalKey`, `seek`, `next`, `get`, `getClosest` with optional before/after behavior, and `close`.

`MapFile.Writer` creates maps with class-based or `WritableComparator` keys, optional `SequenceFile.CompressionType`, optional `CompressionCodec`, and optional `Progressable`. It exposes instance and static `setIndexInterval`, `getIndexInterval`, synchronized `append`, and synchronized `close`. Appended keys must be greater than or equal to the previous key.

Key risk areas are index memory use, corrupt index recovery, sorted insertion enforcement, comparator consistency, and concurrent reader cursor use. Test signals include creating maps with different index intervals, reopening and querying closest keys before/after target keys, dry-run and actual `fix`, and ensuring the `index` file is kept in sync with `data`.

### `SetFile`

`SetFile` is a file-backed set of keys implemented on top of `MapFile`. `SetFile.Reader` can seek, iterate next keys, and get an exact matching key. `SetFile.Writer` creates sets by key class or comparator with compression and appends keys. Appended keys must be strictly greater than the previous key, which is stronger than `MapFile`'s greater-or-equal rule because duplicate keys are not valid set members. One writer constructor is deprecated because it lacks a `Configuration`.

Tests should cover duplicate-key rejection, sorted order, exact-match lookup, iteration after seek, and compatibility with custom `WritableComparator`.

## `SequenceFile` Format And Flow

`SequenceFile` is the central flat binary key/value file format in this chunk. The class exposes many static `createWriter` overloads accepting `FileSystem`, `Configuration`, `Path`, key/value classes, optional buffer size, replication, block size, `CompressionType`, `CompressionCodec`, `Progressable`, `Metadata`, or an already-open `FSDataOutputStream`. `SYNC_INTERVAL` defines the byte spacing for sync markers.

The Javadoc describes three writer formats:

- Uncompressed records: record length, key length, key, value.
- Record-compressed records: record length, key length, key, compressed value.
- Block-compressed records: separately compressed blocks for key lengths, keys, value lengths, and values.

Every format shares a header containing magic/version, key class name, value class name, compression booleans, optional codec class, metadata, and a sync marker. The reader is the bridge that can read all formats. Deprecated static `getCompressionType(Configuration)` and `setCompressionType(Configuration, CompressionType)` remain for older map/reduce configuration paths, but the docs point callers to `JobConf` and `SequenceFileOutputFormat` APIs or explicit writer creation.

`SequenceFile.Metadata` is a `Writable` map of `Text` to `Text`, with constructors, `get`, `set`, `getMetadata`, `write`, `readFields`, equality/hash/toString. It is persisted in the file header and participates in file-format compatibility.

`SequenceFile.Reader` implements `java.io.Closeable` and opens a file from `FileSystem`, `Path`, and `Configuration`. It exposes:

- File/class info: `getKeyClassName`, `getKeyClass`, `getValueClassName`, `getValueClass`, `isCompressed`, `isBlockCompressed`, `getCompressionCodec`, and `getMetadata`.
- Value access: `getCurrentValue(Writable)` and object-returning `getCurrentValue(Object)`.
- Record iteration: `next(Writable)`, `next(Writable, Writable)`, raw `next(DataOutputBuffer)`, object-returning `next(Object)`.
- Raw access: `createValueBytes()`, `nextRaw(DataOutputBuffer, ValueBytes)`, `nextRawKey(DataOutputBuffer)`, and `nextRawValue(ValueBytes)`.
- Positioning: `seek(long)`, `sync(long)`, `syncSeen()`, `getPosition()`, and `toString()`.

`SequenceFile.Writer` implements `java.io.Closeable` and exposes constructors, key/value class access, codec access, `sync()`, synchronized `close()`, synchronized `append(Writable, Writable)`, synchronized `append(Object, Object)`, synchronized `appendRaw(byte[], int, int, ValueBytes)`, and synchronized `getLength()`. The `getLength()` doc promises a synchronized position suitable for a future `Reader.seek(long)`, but warns that block compression may return the first key in the current block rather than the last key appended when the call occurred.

`SequenceFile.ValueBytes` is the raw value abstraction. It can write uncompressed bytes, write compressed bytes without recompressing uncompressed data, and report size. `SequenceFile.Sorter.RawKeyValueIterator` provides raw key/value iteration with progress tracking and close. `SequenceFile.Sorter.SegmentDescriptor` represents a merge segment with offset, length, path, sync checks, input preservation, comparison, raw key/value loading, and cleanup that may close and delete the backing file.

`SequenceFile.Sorter` sorts and merges sequence files. Its constructors accept a `FileSystem`, key/value classes or raw comparator, and `Configuration`. It exposes factor and memory tuning, progress reporting, sorting to output paths, sort-and-iterate, multiple merge overloads with temp directories and delete-input behavior, `cloneFileAttributes`, `writeFile`, and final merge to an output file. The docs explicitly warn that key `Writable#readFields(DataInput)` must be efficient and avoid memory allocation for good sort performance.

Test signals for this area are broad:

- Golden-file compatibility for all three compression formats and metadata.
- Writer/reader seek and sync marker behavior, including `syncSeen()`.
- Raw append/read parity with object append/read.
- Block-compression `getLength()` positions.
- Sorter memory/factor limits, multi-pass merges, temp-file cleanup, delete-input behavior, progress reporting, and comparator consistency.
- Deprecated compression configuration still round-trips for old callers without breaking newer explicit writer APIs.

## `Text` Boundary In This Chunk

The chunk ends inside `org.apache.hadoop.io.Text`. The visible API includes constructors from empty, `String`, another `Text`, and `byte[]`; `getBytes()`, `getLength()`, `charAt(int)`, `find(String)`, `find(String, int)`, `set(String)`, `set(byte[])`, `set(Text)`, `set(byte[], int, int)`, and the start of `append(byte[], int, int)`.

`Text` stores UTF-8 bytes and exposes byte-oriented operations. `charAt(int)` returns a Unicode scalar value or `-1` for invalid positions/trailing bytes without instantiating a Java `String`. `find` returns byte positions in the backing buffer. The primary risks are confusing byte offsets with Java char indexes, invalid UTF-8 boundaries, stale bytes beyond `getLength()` in the backing array, and substring search correctness on multibyte characters.

## Control Flow And State Behavior

Because this is a public API XML file, control flow is visible mostly through method relationships and documented file formats:

- `FileSystem` adapters initialize from `URI` plus `Configuration`, maintain a working directory, translate Hadoop `Path` operations into remote backend calls, and surface `IOException` for backend failures.
- Block-based S3 stores namespace state as `INode` records and content as `Block` objects; migration rewrites inode/block metadata without touching block payload files.
- `MapFile`/`ArrayFile`/`SetFile` build on `SequenceFile` for sorted persistent records and add index or semantic constraints.
- `SequenceFile.Writer` writes header, metadata, records/blocks, sync markers, and optional compression; `Reader` interprets headers and switches between compressed/uncompressed/raw access paths.
- `SequenceFile.Sorter` reads raw keys and values, spills/merges sorted segments, and optionally deletes input/temp files through `SegmentDescriptor.cleanup()`.
- `Writable` objects persist state through `write(DataOutput)` and `readFields(DataInput)`; raw comparators allow sorting serialized forms without object construction.

Mutable state surfaces include filesystem working directories, current stream positions, reader cursors, writer output positions, buffer backing arrays, map-writable class registries, compression inflated/uninflated state, configuration-backed stringified values, and S3 metadata versions.

## Dependencies And Integration Points

Important dependencies named in this chunk:

- Hadoop core interfaces: `FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `FSDataInputStream`, `FSDataOutputStream`, `FSInputStream`, `Configuration`, `Configurable`, `Progressable`, `Progress`, `Tool`, and `Configured`.
- Hadoop serialization: `Writable`, `WritableComparable`, `WritableComparator`, `RawComparator`, `Serializer`, `SequenceFile`, `MapFile`, `Text`, and compression codecs.
- Hadoop permissions: `FsPermission`, `FsAction`, `PermissionStatus`, and `AccessControlException`.
- Java platform APIs: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `DataInputStream`, `DataOutputStream`, `FilterInputStream`, `FilterOutputStream`, `Closeable`, `Socket`, `URI`, collections, and `IOException`.
- External backends: Apache Commons Net `FTPClient`, Kosmos/KFS client integration inferred from `KosmosFileSystem`, Amazon S3-backed stores, and native S3 store integration.
- MapReduce compatibility points: deprecated `SequenceFile` compression helpers reference `JobConf` and `SequenceFileOutputFormat`.

## Risks

- The XML is a compatibility artifact; implementation behavior must be verified in source/tests because method bodies are absent.
- Several filesystem methods expose legacy or optional semantics (`delete(Path)`, `getName()`, unsupported append, ignored permissions) that can surprise modern callers.
- S3 and native S3 rename/delete/listing cannot fully match atomic POSIX/HDFS behavior, and block-based S3 can leave orphaned metadata or blocks on partial failures.
- Public destructive S3 store methods (`purge`) and diagnostic dumping are useful for tests but hazardous if miswired into production.
- `MapFile` and `SetFile` require sorted appends; bad ordering may corrupt query semantics or fail late.
- `MapFile` loads the full index into memory; large keys or small index intervals increase memory pressure.
- `SequenceFile` has multiple persistent binary formats. Header, metadata, sync marker, compression, raw-value, and block-compression behavior must remain compatible across releases.
- Raw comparators must agree with object `compareTo`; divergence can corrupt sorted outputs.
- `AbstractMapWritable` allows only 127 distinct classes per instance.
- `BytesWritable`, `Text`, and buffer classes expose backing arrays; callers can accidentally mutate serialized state or read stale bytes beyond logical length.
- `ObjectWritable` and `DefaultStringifier` rely on class names, serializers, and `Configuration`, which makes classloader and version skew a practical compatibility risk.

## Test Signals

Useful validation derived from this chunk:

- API diff tests that ensure all public/protected signatures, fields, deprecations, and synchronization markers remain intentional.
- Permission round-trips for `FsPermission` and `PermissionStatus`, including umask and symbolic/octal conversions.
- `FsAction` operation truth tables for `implies`, `and`, `or`, and `not`.
- Filesystem contract tests for KFS, FTP, S3, and native S3: initialization, working directory resolution, create/open/list/status/delete/rename, unsupported append, ignored permissions, close/seek behavior, and remote failure translation.
- S3 metadata tests for `INode.serialize/deserialize`, version mismatch, migration rewriting metadata only, byte-range block retrieval, orphan cleanup, and `purge` isolation.
- Shell command parsing tests for option recognition, argument counts, path expansion, command matching, and aggregate return codes.
- Writable primitive tests for read/write round-trip, raw comparator parity, hash/equality, and decreasing long comparison.
- Buffer reuse tests for offsets, positions, backing-array aliasing, reset behavior, and reading from `DataInput`.
- `MapWritable`/`SortedMapWritable` tests for nested maps, custom classes, copy construction, config propagation, ordering, serialization, and class-id limits.
- `MapFile`, `ArrayFile`, and `SetFile` persistence tests for sorted append constraints, index interval behavior, corrupt index repair, closest-key lookup, duplicate set-key rejection, and reopen compatibility.
- `SequenceFile` golden tests for uncompressed, record-compressed, and block-compressed files with metadata, sync/seek behavior, raw APIs, sorter merge cleanup, progress, and temp file deletion.
- `Text` tests for UTF-8 byte length, scalar `charAt`, byte-position `find`, append/set with offsets, and invalid/trailing-byte handling.

### subset-b-007275: lines 12397-18635

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml lines 12397-18635

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.18.2, not executable implementation source. It starts in the middle of `org.apache.hadoop.io.Text` and ends inside the long class documentation for `org.apache.hadoop.mapred.JobClient`, so adjacent chunks are required for whole-class conclusions about those two APIs. Within this range the XML records public/protected API compatibility metadata: packages, class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, synchronization/static/final flags, deprecation text, and Javadoc contracts.

The covered surface spans Hadoop's classic serialization layer (`org.apache.hadoop.io`), compression codecs and native codec adapters (`org.apache.hadoop.io.compress`, `compress.lzo`, `compress.zlib`), retry and serialization frameworks, IPC/RPC APIs and metrics, runtime log-level controls, and the opening of the old `org.apache.hadoop.mapred` MapReduce client/input/output APIs.

## Purpose and Major API Surface

The `org.apache.hadoop.io` section covers core Writable types and helpers. The visible tail of `Text` documents byte-backed UTF-8 text mutation, clearing, bytewise comparison, serialization with zero-compressed length, string encode/decode, UTF-8 validation, code point traversal, and encoded length calculation. `Text.Comparator` and `UTF8.Comparator` provide raw byte comparators for sorted data paths. `TwoDArrayWritable`, deprecated `UTF8`, `VersionedWritable`, `VersionMismatchException`, `VIntWritable`, and `VLongWritable` define serializable value containers and version checks.

`Writable` and `WritableComparable` are the serialization and key-comparison contracts used by classic MapReduce keys and values. `WritableComparator` is the raw comparison bridge used by sort-heavy paths, with static helpers for lexicographic byte comparison, byte-array primitive decoding, and vint/vlong decoding. `WritableFactories`, `WritableFactory`, and `WritableName` add factory and class-name alias registries for constructing or renaming Writable classes without breaking persisted data. `WritableUtils` centralizes compressed byte/string arrays, writable cloning through serialization buffers, vint/vlong encoding, enum serialization, and exact skip behavior.

The compression API defines reusable codec infrastructure. `CodecPool` pools compressors and decompressors. `CompressionCodec` is the common stream factory contract for output/input streams, compressor/decompressor type discovery, instance creation, and default file extension. `CompressionCodecFactory` reads configured codec classes, maps filename extensions to codecs, removes suffixes, and exposes a command-line entry point. `CompressionInputStream` and `CompressionOutputStream` are abstract stream wrappers with reset/finish behavior, while `Compressor` and `Decompressor` define stateful streaming engines with input buffers, dictionaries, byte counters, finish/reset/end lifecycle, and compress/decompress calls.

Concrete compression classes include `DefaultCodec`, `GzipCodec`, `GzipCodec.GzipInputStream`, `GzipCodec.GzipOutputStream`, and `LzoCodec`. The LZO and zlib packages expose native-aware engines: `LzoCompressor`, `LzoDecompressor`, their `CompressionStrategy` enums, `BuiltInZlibDeflater`, `BuiltInZlibInflater`, `ZlibCompressor` with `CompressionLevel`, `CompressionStrategy`, and `CompressionHeader`, `ZlibDecompressor` with `CompressionHeader`, and `ZlibFactory` for selecting native or built-in compressor/decompressor classes.

The retry API contains immutable retry policy contracts and proxy construction. `RetryPolicies` exposes constants for try-once/fail, try-once/do-not-fail for void methods, and retry-forever, plus factory methods for fixed sleep, time-bounded retry, proportional sleep, exponential backoff, exception-specific policies, and remote-exception-specific policies. `RetryPolicy.shouldRetry(Exception, int)` decides retry, silent non-failure, or rethrow. `RetryProxy` builds dynamic proxies using either one policy for all methods or a method-name-to-policy map.

The serializer API abstracts Hadoop object encoding beyond Writable. `Serializer` and `Deserializer` are stateful stream-bound contracts that must not buffer across calls because other producers/consumers may share the stream. `Serialization<T>` pairs serializers and deserializers with an `accept(Class)` check. `SerializationFactory` loads implementations from the `io.serializations` configuration key. `WritableSerialization` delegates to `Writable.write` and `readFields`; `JavaSerialization` and `JavaSerializationComparator` support experimental Java `Serializable` objects; `DeserializerComparator` compares raw bytes by deserializing objects before using the normal comparator path.

The IPC/RPC section covers old Hadoop RPC plumbing. `Client` sends single Writable calls to an address, authenticated calls with `UserGroupInformation`, and parallel calls to multiple addresses, with a configurable ping interval and a `stop()` lifecycle. `RemoteException` carries remote exception class names and can unwrap to matching `IOException` types or construct wrapped exceptions by class name. `RPC` builds client proxies for `VersionedProtocol`, waits for proxies, stops proxies, performs parallel reflective calls, and constructs `RPC.Server` instances. `RPC.Server` dispatches Writable RPC calls to a protocol implementation. `RPC.VersionMismatch`, `Server`, and `VersionedProtocol` define protocol version checking, server lifecycle/binding/thread metrics, remote address context, and call dispatch.

`org.apache.hadoop.ipc.metrics` exposes `RpcMetrics` and `RpcMgtMBean`. These publish queue time, processing time, method-level metrics, open connection count, call queue length, and min/max reset behavior through Hadoop metrics and JMX. `org.apache.hadoop.log.LogLevel` and `LogLevel.Servlet` provide command-line and servlet paths for changing log levels at runtime.

The `org.apache.hadoop.mapred` section starts the classic MapReduce API. `ClusterStatus` is a Writable snapshot of task tracker count, running maps/reduces, maximum map/reduce capacity, and `JobTracker.State`. `Counters`, `Counters.Counter`, and `Counters.Group` represent synchronized named counters grouped by enum class or string group, with serialization, iteration, increments, sum, logging, compact string output, display names, localization hooks, and deprecated id-based counter access. `DefaultJobHistoryParser` populates a `JobHistory.JobInfo` model from history files on a `FileSystem`.

MapReduce file I/O APIs include `FileAlreadyExistsException`, abstract `FileInputFormat<K,V>`, abstract `FileOutputFormat<K,V>`, `FileSplit`, `ID`, `InputFormat<K,V>`, and `InputSplit`. `FileInputFormat` handles path configuration, optional path filtering, listing input status, validation, split calculation, block-location lookup, and splitability decisions before delegating records to subclasses' `RecordReader`. `FileOutputFormat` handles output compression settings, output codec class selection, output path/work path/task output path calculation, output-spec validation, and subclass `RecordWriter` construction. `FileSplit` serializes path/start/length/locations, while `ID` is a WritableComparable integer identity base with parsing and static read helpers.

The chunk closes with MapReduce validation and client entry points: `InvalidFileTypeException`, `InvalidInputException`, `InvalidJobConfException`, `IsolationRunner`, and a partial `JobClient`. `JobClient` implements `MRConstants` and `Tool`, constructs against default or explicit `JobTracker` addresses, initializes/closing client resources, returns the filesystem used for job staging, submits jobs from a file or `JobConf`, queries `RunningJob` handles, map/reduce `TaskReport`s, cluster status, running/submitted jobs, default map/reduce capacity, system directory, task output filters, `runJob`, `run`, and `main`.

## Control Flow and Behavioral Contracts

The XML has no executable control flow, but the Javadoc captures intended API flow. Writable values use a strict `write(DataOutput)` and `readFields(DataInput)` protocol, and implementations are expected to reuse existing object storage during deserialization where possible. Sort paths may compare by object deserialization or by optimized raw byte comparators; optimized comparators must preserve natural ordering semantics expected by `WritableComparable`.

Text serialization uses UTF-8 bytes with zero-compressed length prefixes. Decode methods can either replace malformed input with U+FFFD or throw `MalformedInputException` through the `CharacterCodingException` path. `bytesToCodePoint(ByteBuffer)` advances the buffer position and changes any mark, so callers cannot treat it as a pure inspection helper.

Compression flow is stateful and lifecycle-driven. Codecs create streams and optionally accept pooled compressors/decompressors. Compressors receive input with `setInput`, report `needsInput`, can accept dictionaries, are finished via `finish`, emit bytes through `compress`, and are reset or ended. Decompressors mirror that lifecycle and can require dictionaries. `CodecPool` requires borrowers to return compressors/decompressors so native resources and buffers are reusable.

Native compression selection is conditional. LZO APIs expose `isNativeLzoLoaded`; zlib exposes `ZlibFactory.isNativeZlibLoaded` plus compressor/decompressor class selection. Built-in zlib wrappers adapt `java.util.zip.Deflater` and `Inflater` to Hadoop's `Compressor` and `Decompressor` interfaces. Native engines have direct buffer sizes, synchronized mutation methods, byte counters, and explicit or finalizer-assisted cleanup.

Retry flow is proxy-mediated. A failed proxied method calls `RetryPolicy.shouldRetry`, passing the exception and retry count. The policy may return true to retry, false to suppress failure for void methods, or throw to stop retrying. Method-specific proxy maps default to `TRY_ONCE_THEN_FAIL` when no policy is configured for a method.

Serializer flow is stream-bound: `open(stream)`, repeated `serialize` or `deserialize`, then `close()`. Deserializers may mutate a supplied non-null instance to avoid allocation; serializers/deserializers must not buffer because other code may read or write the same stream between calls.

IPC flow uses Writable request/response values for low-level `Client` calls and Java interface proxies for `RPC`. Protocols must use primitive, `String`, `Writable`, `void`, or arrays of those types, and methods should throw only `IOException`. RPC server instances expose current server and remote address context during call handling, while versioned protocols allow client/server version mismatch detection.

MapReduce job submission flow is documented in the partial `JobClient` class: validate input and output specs, compute `InputSplit`s, set up `DistributedCache` accounting, copy the job jar and configuration to the distributed filesystem system directory, then submit to the `JobTracker` and optionally monitor status. `JobClient.runJob` submits and polls until completion.

File input flow starts with configured input paths and optional `PathFilter`, lists `FileStatus` entries, validates non-empty inputs, computes split sizes from requested split count, min split size, and block size, locates block indexes, and creates `InputSplit`s for `RecordReader`s. `isSplitable` lets subclasses prevent splitting, especially for stream-compressed files. File output flow checks output specs, rejects existing outputs unless policy allows overwrite, configures optional compression, and computes task/work output paths for writers.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent compatibility metadata. Runtime persistence described here belongs to the APIs it documents.

Writable, Text, UTF8, versioned writable, vint/vlong writable, counters, cluster status, file splits, and IDs persist binary state through `DataInput`/`DataOutput`. Compatibility depends on stable field ordering, length encodings, class names or registered aliases, and read/write symmetry. `WritableName` aliases explicitly exist to keep old files readable after class renames.

Compression state includes input buffers, dictionaries, finish flags, native handles, direct buffers, byte counters, codec configuration, and pooled compressor/decompressor objects. Incorrect lifecycle management can leak native resources, contaminate future pooled uses, or produce truncated output when `finish()`/`close()` is skipped.

Retry state is primarily immutable policy configuration plus per-call retry counts inside proxy invocation. Serializer/deserializer state is bound to open streams and may reuse object instances. `SerializationFactory` depends on the process configuration key `io.serializations`.

IPC/RPC state includes client connection threads, ping interval configuration, socket factories, UGI tickets, server listener sockets, handler thread counts, call queues, remote address context, protocol versions, and metrics/JMX registries. `Client.stop`, `RPC.stopProxy`, and `Server.stop/join` are lifecycle boundaries.

MapReduce state includes job configuration, staged job files in the JobTracker system directory, job IDs, running job handles, task reports, cluster capacity snapshots, counters, history log parsing results, configured input/output paths, output compression settings, task output filters, and task-local isolation directories. File input and output APIs interact with `FileSystem` for listing, block locations, existence checks, and output directory/work path creation.

## Dependencies and Integration Points

The serialization layer depends on `java.io.DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `IOException`, NIO buffers and charset exceptions, Java reflection/class loading, `Configuration`, and Hadoop comparator/sort users. Its direct consumers include MapReduce keys/values, SequenceFile sorting, ObjectWritable-style dynamic construction, and RPC Writable payloads.

Compression integrates with Java streams, `java.util.zip`, Hadoop `Configuration`, `Configurable`, native libraries for LZO/zlib, codec configuration keys, and file formats that infer compression from filename suffixes. MapReduce file output integrates with `CompressionCodec` to compress job outputs.

Retry and RPC integrate through dynamic proxies, `VersionedProtocol`, `UserGroupInformation`, socket factories, `InetSocketAddress`, reflection `Method`, `RemoteException`, and Hadoop metrics. `RetryPolicies.retryByRemoteException` is specifically designed for exception names transported across RPC boundaries.

MapReduce APIs integrate with `JobConf`, `JobTracker`, `RunningJob`, `JobID`, `TaskReport`, `JobStatus`, `DistributedCache`, `FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `PathFilter`, `RecordReader`, `RecordWriter`, `Reporter`, `Progressable`, `Mapper`, `MRConstants`, `Tool`, and `JobHistory.JobInfo`.

Compatibility tooling depends on the exact XML signatures and attributes in this source file. Public/protected signature changes, exception list changes, deprecation text changes, field additions/removals, or documentation contract edits in these APIs affect JDiff comparisons for Hadoop 0.18.2.

## Risks and Compatibility Notes

This chunk is partial at both ends. It should not be used alone to summarize all of `Text` or all of `JobClient`.

Serialization compatibility is high risk. Changing Writable field order, vint/vlong encoding, Text length encoding, UTF-8 replacement behavior, Writable class names, comparator ordering, or counter binary formats can break persisted data, sorted shuffle output, RPC payloads, and historical MapReduce data.

Raw comparators are performance-critical and correctness-critical. A comparator that disagrees with object `compareTo`, mishandles offsets/lengths, or misreads variable-length integers can corrupt sort order. `DeserializerComparator` is simpler but can be too slow for compare-heavy paths.

Compression lifecycle is easy to misuse. Pooled compressor/decompressor instances must be reset and returned; native codecs may be unavailable; `finish`, `flush`, `close`, and `end` have distinct resource and stream-completeness semantics; finalizer cleanup on decompressor classes is not a reliable primary lifecycle.

Retry policies can duplicate side effects. Retrying non-idempotent RPC or filesystem/job operations may submit work twice or mutate state multiple times. `TRY_ONCE_DONT_FAIL` can hide failures for void methods, while `RETRY_FOREVER` can hang callers when failures are permanent.

RPC compatibility depends on protocol versions, allowed parameter/return types, IOException-only method contracts, and remote exception class names. Remote exception unwrapping by class name can fail when classes are absent or constructors do not match.

MapReduce file input/output behavior has operational edge cases. Input validation may aggregate multiple path problems, splitability decisions affect task parallelism, stream-compressed files should not be split, output directories must be checked before job execution, and configured path strings/comma-separated paths need stable parsing.

Counters are synchronized mutable state with deprecated id-based access. Compatibility with old serialized counter groups and display/localized names must be preserved while newer string-name access is preferred.

## Test Signals

JDiff validation should confirm the XML remains well-formed and preserves all class/interface boundaries in this line range, including the partial `Text` tail and partial `JobClient` entry. API compatibility checks should cover method signatures, constructors, fields, visibility, static/final/synchronized flags, exceptions, generic type strings, implemented interfaces, and deprecation text.

Writable tests should round-trip `Text`, `UTF8`, `TwoDArrayWritable`, `VersionedWritable` subclasses, `VIntWritable`, `VLongWritable`, counters, cluster status, file splits, and IDs through `DataOutput`/`DataInput`. Comparator tests should compare object ordering against raw byte ordering for Text/UTF8/vint/vlong-backed data and validate byte primitive readers.

UTF-8 tests should cover malformed byte replacement versus exception behavior, range decode, encode buffer limits, validation failures, code point traversal side effects on `ByteBuffer.position`, and encoded length calculations.

Compression tests should cover codec factory registration by configuration and suffix lookup, default/gzip/lzo/zlib stream round trips, pooled compressor/decompressor borrow/reset/return, native-library unavailable paths, dictionary and finish behavior, byte counters, resetState, close/flush semantics, and zlib built-in fallback.

Retry tests should verify fixed, time-bounded, proportional, exponential, exception-specific, remote-exception-specific, try-once, silent-void, and retry-forever policies with bounded harnesses. Proxy tests should ensure method-specific defaults and exception propagation match the policy contract.

Serialization tests should load serializations from `io.serializations`, select Writable versus Java serialization correctly, reuse supplied deserialization objects when supported, avoid buffering across shared streams, and compare serialized objects through `DeserializerComparator` and `JavaSerializationComparator`.

IPC/RPC tests should exercise single and parallel Writable client calls, calls with UGI tickets, proxy creation and stop, wait-for-proxy behavior, protocol version mismatch reporting, remote exception unwrap cases, server bind/start/stop/join, remote address context, call queue metrics, processing/queue time metrics, and JMX reset behavior.

MapReduce tests should cover `ClusterStatus` writable round trips, counter increments/sums/serialization/compact strings/localized display names, history parser population from a filesystem-backed log, `FileInputFormat` path parsing/filtering/listing/validation/splitting/block-index calculation, unsplittable compressed inputs, `FileOutputFormat` output path validation/compression codec selection/task work paths, `FileSplit` serialization and locations, `ID` compare/parse/read behavior, aggregated invalid input exceptions, and `JobClient` submit/query/report/status/runJob flows against a controlled or mocked JobTracker.

### subset-b-007276: lines 18636-24770

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml lines 18636-24770

## Chunk Scope

This chunk is a generated JDiff XML description of the public Hadoop 0.18.2 `org.apache.hadoop.mapred` API surface. It starts in the tail documentation for `JobClient`, covers most of the classic pre-YARN MapReduce client/configuration, job history, tracker, mapper/reducer, input/output, sequence-file, HTTP status, and ID/event APIs, and ends inside the `TaskID` class documentation.

Because this is JDiff XML, the source does not contain method bodies. The research below derives behavior from class signatures, method contracts, deprecation notes, and API documentation embedded in the XML.

## Purpose

The covered API surface describes the old `mapred` MapReduce programming model and its runtime integration points:

- `JobConf` is the central mutable job configuration object. It records job jar, input/output formats, mapper/reducer/partitioner classes, key/value classes, comparator classes, speculative execution, task counts, retry/failure thresholds, job priority, profiling/debug scripts, job-end notification, and localized per-job scratch directory settings.
- `JobClient`, `RunningJob`, `JobStatus`, `JobProfile`, `JobID`, `TaskID`, `TaskAttemptID`, and `TaskCompletionEvent` provide the client-side and protocol-facing model for submitting jobs, polling progress, killing jobs/tasks, reading task events, and serializing job/task identity.
- `JobTracker` is exposed as the central tracker implementation implementing `MRConstants`, `InterTrackerProtocol`, and `JobSubmissionProtocol`. Its API includes tracker lifecycle, heartbeat handling, job submission/control/status RPC endpoints, topology resolution, and cluster/job status queries.
- `JobHistory` and nested types describe append-style plain text job history persistence, parser callbacks, and log helpers for job, task, map-attempt, and reduce-attempt lifecycle events.
- `Mapper`, `Reducer`, `MapRunnable`, `MapRunner`, `MapReduceBase`, `OutputCollector`, `Reporter`, `Partitioner`, `RecordReader`, `RecordWriter`, `OutputFormat`, and `JobConfigurable` are the core user extension contracts for old-style MapReduce jobs.
- `LineRecordReader`, `KeyValueLineRecordReader`, `KeyValueTextInputFormat`, `MultiFileInputFormat`, `MultiFileSplit`, `MapFileOutputFormat`, `SequenceFile*` formats/readers, and `OutputLogFilter` are concrete input/output helpers for text, key-value text, multi-file splits, map files, sequence files, and output directory filtering.
- `StatusHttpServer` and nested servlets expose the tracker-side HTTP status surface and diagnostics/graph endpoints.

## Important APIs and Types

### Job configuration and lifecycle

- `JobClient.TaskStatusFilter` is an enum-like nested type with generated `values()` and `valueOf(String)` methods. The chunk starts immediately after `JobClient` docs explaining job completion/chaining options: blocking `runJob(JobConf)`, asynchronous `submitJob(JobConf)` returning `RunningJob`, and asynchronous job-end notifications via `JobConf#setJobEndNotificationURI(String)`.
- `JobConf extends Configuration` is the largest type in this range. Constructors accept no arguments, an example class for jar discovery, a parent `Configuration`, `(Configuration, Class)`, a config file path `String`, or a config `Path`.
- `JobConf` core class/job settings include `getJar`, `setJar`, `setJarByClass`, `getUser`, `setUser`, `getJobName`, `setJobName`, `getSessionId`, `setSessionId`, `getJobPriority`, and `setJobPriority`.
- File/path and local storage helpers include deprecated `getSystemDir`, `getLocalDirs`, `deleteLocalFiles`, `getLocalPath`, deprecated `setInputPath`, `addInputPath`, `getInputPaths`, `setWorkingDirectory`, `getWorkingDirectory`, deprecated `getOutputPath`, deprecated `setOutputPath`, and `getJobLocalDir`.
- Format/class settings include `getInputFormat`, `setInputFormat`, `getOutputFormat`, `setOutputFormat`, `getMapperClass`, `setMapperClass`, `getMapRunnerClass`, `setMapRunnerClass`, `getPartitionerClass`, `setPartitionerClass`, `getReducerClass`, `setReducerClass`, `getCombinerClass`, and `setCombinerClass`.
- Key/value and comparator settings include `getMapOutputKeyClass`, `setMapOutputKeyClass`, `getMapOutputValueClass`, `setMapOutputValueClass`, `getOutputKeyClass`, `setOutputKeyClass`, `getOutputValueClass`, `setOutputValueClass`, `getOutputKeyComparator`, `setOutputKeyComparatorClass`, `getOutputValueGroupingComparator`, and `setOutputValueGroupingComparator`.
- Compression settings include `setCompressMapOutput`, `getCompressMapOutput`, deprecated `setMapOutputCompressionType`, deprecated `getMapOutputCompressionType`, `setMapOutputCompressorClass`, and `getMapOutputCompressorClass`.
- Scheduling/failure/profiling/debug settings include `setCombineOnceOnly` and `getCombineOnceOnly`, speculative execution toggles for whole job/map/reduce, `getNumMapTasks` and `setNumMapTasks`, `getNumReduceTasks` and `setNumReduceTasks`, max map/reduce attempts, max task failures per tracker, max map/reduce task failure percentages, profiling enable/params/range accessors, map/reduce debug script accessors, and job-end notification URI accessors.
- `JobConfigurable` is the configuration callback contract with `configure(JobConf)`.
- `JobEndNotifier` exposes static lifecycle and notification APIs: `startNotifier`, `stopNotifier`, `registerNotification(JobConf, JobStatus)`, and `localRunnerNotification(JobConf, JobStatus)`.

### Job history

- `JobHistory` is a static-style utility with `init(JobConf, String)`, `parseHistoryFromFS(String, Listener, FileSystem)`, `isDisableHistory`, `setDisableHistory`, and `JOBTRACKER_START_TIME`.
- `JobHistory.HistoryCleaner implements Runnable` cleans old history data, removing jobs older than one month and stale job tracker references.
- `JobHistory.JobInfo extends JobHistory.KeyValuePair` provides `getAllTasks`, local job-file path helpers, URL encode/decode helpers for job history paths/names, and `logSubmitted`, `logStarted`, `logFinished`, and `logFailed` overloads for string IDs and typed `JobID`.
- `JobHistory.Listener` is a parser callback: `handle(RecordTypes, Map<Keys,String>)`.
- `JobHistory.Keys`, `RecordTypes`, and `Values` are enum-like namespaces used in persisted history lines.
- `JobHistory.Task`, `TaskAttempt`, `MapAttempt`, and `ReduceAttempt` provide event-specific static log methods. Task logs capture task start/finish/failure and attempts. Map attempt logs capture start/finish/failure/kill with host and error. Reduce attempt finish additionally captures shuffle-finished and sort-finished timestamps.

### Job identity, profile, and status

- `JobID extends ID` models immutable job identity from job tracker identifier plus job number. It supports `equals`, `compareTo`, `toString`, `hashCode`, `readFields`, `write`, static `read(DataInput)`, `forName(String)`, and `getJobIDsPattern(String,Integer)` for regex generation.
- `JobPriority` is an enum-like job priority type.
- `JobProfile implements Writable` carries user, job ID, job file, tracking URL, and job name. It has constructors for typed `JobID` and legacy string IDs, plus `write`/`readFields`.
- `JobStatus implements Writable` carries job ID, map/reduce progress, run state, start time, and username. Constants include `RUNNING`, `SUCCEEDED`, `FAILED`, and `PREP`.
- `RunningJob` is the client-facing handle for live jobs. It exposes job identity/profile fields, `mapProgress`, `reduceProgress`, non-blocking `isComplete`, `isSuccessful`, blocking `waitForCompletion`, `killJob`, task completion event paging, typed and deprecated string `killTask`, and `getCounters`.

### Job tracker and protocols

- `JobTracker` implements `MRConstants`, `InterTrackerProtocol`, and `JobSubmissionProtocol`.
- Lifecycle and service methods include static `startTracker(JobConf)`, `stopTracker`, `offerService`, `main`, `getProtocolVersion`, and `getAddress`.
- Cluster/tracker state methods include `getTotalSubmissions`, `getJobTrackerMachine`, `getTrackerIdentifier`, `getTrackerPort`, `getInfoPort`, `getStartTime`, `runningJobs`, `getRunningJobs`, `failedJobs`, `completedJobs`, `taskTrackers`, `getTaskTracker`, `getClusterStatus`, `jobsToComplete`, and `getAllJobs`.
- Topology and locality methods include `resolveAndAddToTopology`, `getNodesAtMaxLevel`, `getParentNode`, `getNode`, `getNumTaskCacheLevels`, and `getNumResolvedTaskTrackers`.
- Runtime RPC endpoints include `heartbeat(TaskTrackerStatus, boolean, boolean, short)`, `reportTaskTrackerError`, `getNewJobId`, overloaded `submitJob`, overloaded `killJob`, overloaded `getJobProfile`, overloaded `getJobStatus`, overloaded `getJobCounters`, map/reduce task report accessors, task completion event accessors, task diagnostic accessors, `getTip`, typed and string `killTask`, assigned tracker lookup, system directory lookup, overloaded `getJob`, and local job file path helpers.
- `JobTracker.IllegalStateException extends IOException` is a tracker-specific checked error. `JobTracker.State` is an enum-like tracker state.

### Core MapReduce user contracts

- `Mapper<K1,V1,K2,V2>` maps each input key/value to zero or more intermediate pairs via `map(K1,V1,OutputCollector<K2,V2>,Reporter)`. It extends `JobConfigurable` and `Closeable`. The docs emphasize that reporters must be used for long-running processing to avoid task timeout and that intermediate output is grouped, partitioned, optionally combined, and stored as `SequenceFile`s.
- `Reducer<K2,V2,K3,V3>` reduces grouped intermediate values via `reduce(K2, Iterator<V2>, OutputCollector<K3,V3>, Reporter)`. The documented flow is shuffle, sort/group, then reduce. It warns that key/value objects passed to reduce are reused and must be cloned if retained.
- `MapRunnable<K1,V1,K2,V2>` is an expert mapper driver abstraction. `MapRunner` is the default implementation that reads from a `RecordReader` and invokes a configured mapper.
- `MapReduceBase` provides no-op `configure(JobConf)` and `close()` for mapper/reducer subclasses.
- `OutputCollector<K,V>` abstracts collection of mapper intermediate output and reducer final output through `collect(K,V)`.
- `Reporter extends Progressable` provides task status, enum and string-group counter increments, current input split for mappers, and a `Reporter.NULL` no-op instance.
- `Partitioner<K2,V2>` maps intermediate key/value pairs to reducer partition numbers through `getPartition(K2,V2,int)`.
- `RecordReader<K,V>` converts an `InputSplit` into key/value records with `next`, `createKey`, `createValue`, `getPos`, `close`, and `getProgress`.
- `RecordWriter<K,V>` writes final key/value pairs with `write` and `close(Reporter)`.
- `OutputFormat<K,V>` validates output specs and creates `RecordWriter`s. `OutputFormatBase` is a deprecated abstract base superseded by `FileOutputFormat`; it still carries static compression helpers and default output spec validation.

### Text, map-file, multi-file, and sequence-file I/O

- `KeyValueLineRecordReader` reads text lines into `Text` key/value pairs using a separator located by `findSeparator`; it implements `RecordReader<Text,Text>`.
- `KeyValueTextInputFormat extends FileInputFormat<Text,Text>` and implements `JobConfigurable`; it configures separator behavior, declares splitability, and returns a key-value line reader.
- `LineRecordReader` reads line-oriented records as byte-position `LongWritable` keys and `Text` values. Constructors accept `Configuration + FileSplit` or explicit streams/start/end/max line length. Nested `LineReader` has `readLine` overloads and `close`.
- `MapFileOutputFormat extends FileOutputFormat<WritableComparable,Writable>` writes `MapFile`s and has static helpers `getReaders(FileSystem,Path,Configuration)` and `getEntry(MapFile.Reader[], Partitioner, key, value)`.
- `MultiFileInputFormat<K,V>` groups files into `MultiFileSplit`s via `getSplits` and leaves `getRecordReader` abstract/concrete to subclasses depending on implementation. `MultiFileSplit` implements `InputSplit` over arrays of `Path` and lengths, with aggregate length, path accessors, locations, serialization, and string conversion.
- `OutputLogFilter implements PathFilter` rejects output directory paths containing `_logs`.
- `SequenceFileInputFormat<K,V>` lists input paths and returns `SequenceFileRecordReader`.
- `SequenceFileRecordReader<K,V>` reads typed `SequenceFile` records and exposes key/value classes, key/value creation, two `next` overloads, current value retrieval, progress, position, seek, close, and a protected/public `conf` field in the JDiff output.
- `SequenceFileOutputFormat<K,V>` creates sequence-file writers, static readers for output directories, and static compression type configuration helpers.
- `SequenceFileAsBinaryInputFormat` and nested `SequenceFileAsBinaryRecordReader` read sequence-file keys and values as raw `BytesWritable` byte streams. The reader exposes original key/value class names and synchronized `next`.
- `SequenceFileAsBinaryOutputFormat` writes binary raw `BytesWritable` records while allowing configured logical key/value classes distinct from actual `BytesWritable`. Its protected nested `WritableValueBytes` implements `SequenceFile.ValueBytes` for `appendRaw`.
- `SequenceFileAsTextInputFormat` and `SequenceFileAsTextRecordReader` convert sequence-file keys and values to their `String` forms and emit `Text`.
- `SequenceFileInputFilter<K,V>` samples/filter sequence-file records. `setFilterClass(Configuration, Class)` chooses the filter, and nested `Filter` accepts/rejects by key. Built-in filters include `FilterBase`, `MD5Filter`, `PercentFilter`, and `RegexFilter`, each configured from `Configuration` with frequency or regex pattern state.

### HTTP status and task events/IDs

- `StatusHttpServer` wraps server setup for MapReduce status pages. It exposes attributes, servlet registration, port query, thread limits, SSL listener addition, start, and stop. Nested `StackServlet` and `TaskGraphServlet` extend `HttpServlet`; `TaskGraphServlet` has fixed drawing layout fields such as width, height, and margins.
- `TaskAttemptID extends ID` identifies one attempt for a `TaskID`. Constructors accept `(TaskID,int)` or raw `(jtIdentifier, jobId, isMap, taskId, attemptId)`. It exposes job/task accessors, `isMap`, equality/comparison/string/hash, Writable serialization, static read, `forName`, and regex pattern generation via `getTaskAttemptIDsPattern`.
- `TaskCompletionEvent implements Writable` captures event ID, task attempt ID, task status, map/reduce flag, task runtime, and task tracker HTTP location. It keeps deprecated string task ID accessors alongside typed `TaskAttemptID` accessors and has `EMPTY_ARRAY`.
- `TaskCompletionEvent.Status` is an enum-like status type.
- `TaskID extends ID` begins in this chunk and is incomplete at the chunk boundary. Covered members include constructors from `JobID` or raw parts, `getJobID`, `isMap`, equality/comparison/string/hash, Writable serialization, static read, `forName`, and `getTaskIDsPattern`. The docs state map/reduce tasks can have multiple attempts and each attempt is identified by `TaskAttemptID`.

## Control Flow

The documented MapReduce control flow is:

1. A client creates and populates `JobConf`, including input/output paths or formats, mapper/reducer/combiner/partitioner classes, key/value classes, compression, speculative execution, attempts/failure policies, debug scripts, and notification settings.
2. The client submits the job through `JobClient`/`JobTracker` APIs. Synchronous clients use `runJob(JobConf)` and block. Asynchronous clients use `submitJob(JobConf)`, hold a `RunningJob`, poll `JobStatus`/progress/events, or rely on job-end notification URI delivery.
3. `JobTracker` assigns job IDs, accepts job submissions, tracks cluster state, receives task tracker heartbeats, reports task tracker errors, returns task reports/diagnostics/counters/events, and handles kill requests.
4. Input formats create splits and record readers. `LineRecordReader`, `KeyValueLineRecordReader`, `SequenceFileRecordReader`, and sequence-file text/binary wrappers convert file data into typed key/value records.
5. The default `MapRunner` drives a `Mapper` by iterating `RecordReader.next(key,value)` and sending output through `OutputCollector`. Custom `MapRunnable` implementations can replace this for threaded/asynchronous mapping.
6. Intermediate mapper output is collected, partitioned by `Partitioner`, optionally combined, grouped/sorted by configured comparators, stored as `SequenceFile`s, and shuffled over HTTP to reducers.
7. Reducers run shuffle and sort/group phases, then invoke `Reducer.reduce` per grouped key. Reducer output is collected and written through the configured `OutputFormat`/`RecordWriter`.
8. Task and job lifecycle events are written through `JobHistory` helper methods and can later be parsed by `JobHistory.parseHistoryFromFS` through a listener callback.
9. Clients and framework components exchange typed job/task IDs and events through `Writable` serialization APIs on `JobID`, `TaskID`, `TaskAttemptID`, `JobProfile`, `JobStatus`, and `TaskCompletionEvent`.

## State and Persistence Behavior

- `JobConf` persists state as `Configuration` key/value settings. Many methods are typed accessors around configuration keys, including class names, booleans, integers, ranges, compression codecs, comparators, scripts, and notification URIs.
- `JobConf#getJobLocalDir` documents per-job localized scratch storage at `${mapred.local.dir}/taskTracker/jobcache/$jobid/work/`, exposed as `job.local.dir` and as a system property. This is shared scratch space for tasks within a localized job.
- `JobHistory` persists append-only plain text history. Each line has a record type followed by key/value pairs. There is a master index containing start/stop times and job-level properties, plus per-job history files named by job tracker ID and job ID. `HistoryCleaner` removes old files and stale tracker references.
- `JobHistory.JobInfo.logSubmitted` creates a new history file for a job and disables history for later events if creation fails.
- Record readers and writers maintain stream/file positions and progress. `SequenceFileRecordReader`, binary/text sequence readers, and line readers expose byte position and progress for task reporting and split completion.
- `MultiFileSplit`, `JobID`, `TaskID`, `TaskAttemptID`, `JobProfile`, `JobStatus`, and `TaskCompletionEvent` expose `readFields`/`write` methods for Hadoop `Writable` persistence over RPC, task/job metadata storage, and framework communication.
- `TaskCompletionEvent` event IDs are assigned externally and incremented per job from zero, which matters for paged retrieval by `RunningJob#getTaskCompletionEvents(startFrom)` and `JobTracker#getTaskCompletionEvents`.

## Dependencies and Integration Points

- Hadoop core configuration and filesystem types: `Configuration`, `Path`, `FileSystem`, `PathFilter`, `FileAlreadyExistsException`, and local path helpers.
- Hadoop IO types: `Writable`, `WritableComparable`, `Text`, `LongWritable`, `BytesWritable`, `RawComparator`, `MapFile.Reader`, `SequenceFile.Reader`, `SequenceFile.ValueBytes`, and `SequenceFile.CompressionType`.
- Compression integration: `CompressionCodec` classes configured through `JobConf`, `OutputFormatBase`, and sequence-file output compression helpers.
- MapReduce protocols and runtime types: `InputSplit`, `FileSplit`, `InputFormat`, `FileInputFormat`, `FileOutputFormat`, `Counters`, `ClusterStatus`, `TaskReport`, `TaskTrackerStatus`, `TaskInProgress`, `JobInProgress`, `HeartbeatResponse`, `MRConstants`, `InterTrackerProtocol`, and `JobSubmissionProtocol`.
- Networking and topology: `InetSocketAddress`, `org.apache.hadoop.net.Node`, tracker HTTP locations, HTTP shuffle references, and status servlet endpoints.
- Servlet/status integration: `HttpServlet`, request/response `doGet`, and status server servlet registration.
- Java platform dependencies: `IOException`, `DataInput`, `DataOutput`, `DataOutputStream`, `Iterator`, `Map`, `Vector`, `List`, `Collection`, `Enum`, `Class`, `Runnable`, `Closeable`, and `URL`.

## Risks and Compatibility Notes

- This chunk contains old `mapred` APIs. Several methods are explicitly deprecated in favor of newer helpers: `JobConf` input/output path methods prefer `FileInputFormat`/`FileOutputFormat`; `JobConf#getSystemDir` prefers `JobClient#getSystemDir`; `OutputFormatBase` prefers `FileOutputFormat`; string job/task IDs are deprecated in favor of typed `JobID`, `TaskID`, and `TaskAttemptID`.
- `JobConf#setNumMapTasks` is documented as only a hint to the framework. Tests and callers should not assume exact map count when input splitting determines actual tasks.
- Reducer docs explicitly warn that key and value objects are reused. User reducers retaining references without cloning can corrupt results.
- Reporter progress is operationally important. Long-running map/reduce code that does not call `Reporter.progress()` or update status/counters may be killed as timed out unless `mapred.task.timeout` is adjusted.
- Job history creation failure disables history for later events. Consumers should tolerate missing history even when jobs run successfully.
- Job history is text and key/value based; escaping, URL encoding/decoding, and listener parsing are likely compatibility-sensitive. File names with special characters are covered by encode/decode helpers and should be tested.
- `TaskCompletionEvent#getTaskStatus` doc contains the typo `SUCESS`; consumers must rely on enum values rather than documentation spelling.
- `SequenceFileAsBinaryOutputFormat` allows logical sequence-file key/value classes that differ from actual `BytesWritable` objects. Misconfiguration can produce unreadable or misleading sequence files.
- `SequenceFileInputFilter` behavior depends on configuration-loaded filter classes and filter-specific frequency/pattern settings. Invalid filter class, invalid regex, zero/negative frequency, or missing configuration should be tested.
- `OutputLogFilter` rejects `_logs` paths; callers listing output directories must ensure this does not hide legitimate data paths named with that segment.
- The requested range starts after the beginning of `JobClient` and ends before the end of `TaskID`, so a final merged per-file report should reconcile these partial boundaries with adjacent chunks.

## Test Signals

Useful tests or verification targets implied by this API surface:

- `JobConf` round-trip configuration tests for class settings, key/value defaults, compression codec classes, comparator classes, speculative execution flags, task counts, max attempts/failure percentages, profiling ranges, debug scripts, job priority, and notification URI.
- Deprecation compatibility tests showing old `JobConf` input/output path methods still delegate to or interoperate with `FileInputFormat` and `FileOutputFormat`.
- Local directory tests for `getLocalDirs`, `getLocalPath`, `deleteLocalFiles`, and `getJobLocalDir`, including multi-directory placement and cleanup.
- `JobID`, `TaskID`, and `TaskAttemptID` tests for `toString`, `forName`, malformed input rejection, `compareTo`, equality/hash consistency, regex pattern generation with null wildcards, and `Writable` serialization compatibility.
- `TaskCompletionEvent` tests for event ID ordering, typed and deprecated task ID accessors, status serialization, map/reduce flag, runtime, tracker HTTP location, and `EMPTY_ARRAY`.
- Job history tests for `init`, disable/enable behavior, append logging for submitted/started/finished/failed/killed events, encode/decode path helpers, parser listener callbacks, and history cleaner retention rules.
- `RunningJob`/`JobTracker` protocol tests for progress, completion/success states, counters, task completion event paging, diagnostics, kill job/task semantics, and overloaded typed/string ID compatibility.
- Record reader tests for line splitting at split boundaries, max line length, key-value separator handling, progress/position reporting, close idempotency, and empty/last-line behavior.
- Multi-file split tests for aggregate length, per-file lengths, path accessors, locations, serialization, and record readers that treat one file as one record.
- Sequence-file tests for typed input/output, text conversion, raw binary reads/writes, compression type settings, logical class metadata in binary output, raw `ValueBytes` sizes, seek/progress/position, and reader close behavior.
- `SequenceFileInputFilter` tests for MD5 deterministic sampling, percent/frequency behavior, regex matching, configuration propagation through `Configurable`, and invalid configuration handling.
- Mapper/reducer contract tests using `MapRunner`, `MapReduceBase`, `OutputCollector`, `Reporter.NULL`, custom reporter counters/status, custom partitioners, custom grouping comparators, combiner behavior, zero-reducer direct output, and reducer object reuse hazards.
- `StatusHttpServer` tests for servlet registration, attributes, port/thread/SSL configuration, start/stop lifecycle, stack servlet output, and task graph servlet rendering parameters.

### subset-b-007277: lines 24771-30885

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml lines 24771-30885

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.18.2, not executable implementation code. It starts inside the tail documentation for `org.apache.hadoop.mapred.TaskID`, then covers public APIs in `org.apache.hadoop.mapred`, `org.apache.hadoop.mapred.jobcontrol`, `org.apache.hadoop.mapred.join`, `org.apache.hadoop.mapred.lib`, `org.apache.hadoop.mapred.lib.aggregate`, `org.apache.hadoop.mapred.pipes`, and the original `org.apache.hadoop.metrics` framework through the beginning of `org.apache.hadoop.metrics.spi.MetricValue`. The chunk ends at the opening of `MetricValue`, so that class must be completed by an adjacent chunk.

The XML records API compatibility metadata: package boundaries, class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation markers, and embedded Javadoc. Control-flow and persistence notes below are inferred from those public contracts and docs.

## Purpose and major API surface

The initial `mapred` segment exposes task execution, logging, reporting, and simple text formats. `TaskLog` resolves per-task log files by string or `TaskAttemptID`, purges old user logs, reads the configured task log cap, and wraps child commands so stdout, stderr, and debug output are redirected to files. `TaskLog.LogName` is the user-log selector enum, `TaskLogAppender` is a Log4J `FileAppender` for task-child system logs with task id and size configuration, and `TaskLogServlet` serves logs over HTTP from TaskTrackers.

`TaskReport` is a `Writable` summary of task state, exposing `TaskID`, deprecated string id, progress, state string, diagnostics, counters, start time, finish time, and `write`/`readFields`. `TaskTracker` implements `MRConstants`, `TaskUmbilicalProtocol`, and `Runnable`; its public contract includes lifecycle startup/shutdown/close, storage cleanup, JobTracker connection access, report address lookup, protocol version negotiation, child task fetch, task status updates, diagnostics, liveness pings, task completion, shuffle and local filesystem error reporting, map completion event retrieval, lost map-output reporting, idle detection, and `main`. Nested `TaskTracker.Child` launches child task processes, `MapOutputServlet` serves map outputs through TaskTracker Jetty, and `TaskTrackerMetrics` implements periodic metric updates.

`TextInputFormat` and `TextOutputFormat` provide line-oriented MapReduce I/O. `TextInputFormat` is a `FileInputFormat<LongWritable,Text>` with configuration, splitability checks, and `RecordReader` creation. `TextOutputFormat` creates `RecordWriter`s for plain text output, while `TextOutputFormat.LineRecordWriter` writes key/value pairs to a `DataOutputStream` with an optional separator.

`org.apache.hadoop.mapred.jobcontrol` defines a small dependency scheduler. `Job` wraps a `JobConf`, job-control id, assigned MapReduce `JobID`, message, dependency list, and integer states `SUCCESS`, `WAITING`, `RUNNING`, `READY`, `FAILED`, and `DEPENDENT_FAILED`. It allows dependencies to be added only while waiting, checks completion/readiness, and submits ready jobs to MapReduce. `JobControl` is a `Runnable` grouping jobs by state, assigning ids, adding individual or bulk jobs, exposing waiting/running/ready/successful/failed lists, suspending/resuming/stopping its control thread, checking whether all jobs are finished, and driving a loop that monitors running jobs, updates waiting jobs, and submits ready jobs.

`org.apache.hadoop.mapred.join` exposes the old MapReduce join framework. `ComposableInputFormat` refines `InputFormat` so implementations return `ComposableRecordReader`s. `ComposableRecordReader` extends `RecordReader` and `Comparable`, adding source id, current key access/cloning, `hasNext`, key skipping, and `accept` registration with a `JoinCollector`. `CompositeInputFormat` parses `mapred.join.expr`, accepts user-defined join operator classes through `mapred.join.define.<ident>`, validates children, builds aligned `CompositeInputSplit`s, creates composite readers, and offers `compose` helpers for `tbl(...)` and operator expressions.

Join split and reader support is broad. `CompositeInputSplit` aggregates child `InputSplit`s, reports aggregate or per-child length/location data, and serializes as count, child split classes, then child splits. `CompositeRecordReader` manages a priority queue of child readers, comparator configuration, child registration by id, key/current-head access, skip propagation, join-collector filling, comparison, progress as minimum child progress, and child close. `JoinRecordReader` emits `TupleWritable` join results; `InnerJoinRecordReader` requires all tuple positions to be present, `OuterJoinRecordReader` emits all collector tuples, `MultiFilterRecordReader` emits a single value derived from joined tuples, and `OverrideRecordReader` prefers the rightmost source for a key. `WrappedRecordReader` adapts ordinary `RecordReader`s into composable readers by caching the head key/value and collecting all values matching a key.

Join utility types handle parsing, replay, and tuple serialization. `Parser` is a shift-reduce parser for join expressions with token classes and `Parser.Node` mappings from identifiers to `ComposableRecordReader` constructors and comparators. `ResetableIterator` defines a stateful iterator that can add values, replay the last value, reset to the beginning, clear data, and close resources; implementations include `ArrayListBackedIterator`, `StreamBackedIterator`, delegation iterators, and an empty implementation. `TupleWritable` is a `Writable` and `Iterable<Writable>` that stores multiple child writables plus presence bits, exposes `has`, `get`, `size`, equality/hash/string forms, and serializes count, types, and objects.

`org.apache.hadoop.mapred.lib` provides stock mapper/reducer/partitioner/input/output utilities. `FieldSelectionMapReduce` performs configurable field extraction similar to Unix cut using `mapred.data.field.separator`, `map.output.key.value.fields.spec`, and `reduce.output.key.value.fields.spec`. `HashPartitioner` partitions by key `hashCode`; `KeyFieldBasedPartitioner` partitions using key fields while retaining the partitioner contract. `IdentityMapper`, `IdentityReducer`, `InverseMapper`, `LongSumReducer`, `RegexMapper`, and `TokenCountMapper` supply common mapper/reducer functions. `MultipleOutputFormat` is the abstract base for routing records to multiple files using overridable leaf-file, key/value-derived filename, actual key, actual value, input-file-based filename, and base writer methods; `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` provide concrete sequence-file and text writers. `MultithreadedMapRunner` runs a thread pool for non-CPU-bound mapper workloads and requires thread-safe mapper implementations. `NLineInputFormat` creates splits with N lines each. `NullOutputFormat` discards output while still satisfying output format contracts.

`org.apache.hadoop.mapred.lib.aggregate` implements the Aggregate framework. Primitive aggregators include `DoubleValueSum`, `LongValueSum`, `LongValueMax`, `LongValueMin`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram`, each following the `ValueAggregator` protocol of `addNextValue`, `reset`, `getReport`, and combiner output. `ValueAggregatorDescriptor` generates aggregation id/value pairs and defines `TYPE_SEPARATOR` and `ONE`; `ValueAggregatorBaseDescriptor` supplies standard aggregation type constants and helper generation for built-in aggregators. `UserDefinedValueAggregatorDescriptor` wraps a configured user descriptor class. `ValueAggregatorMapper`, `ValueAggregatorCombiner`, and `ValueAggregatorReducer` are generic MapReduce stages over `Text` aggregation ids and values, sharing descriptor setup in `ValueAggregatorJobBase`. `ValueAggregatorJob` builds or runs aggregate jobs, including descriptor installation and `JobControl` creation.

`org.apache.hadoop.mapred.pipes.Submitter` is the public entry point for Hadoop Pipes jobs. It configures the executable URI, records whether record reader, mapper, reducer, and record writer are Java implementations, controls whether the downlink command file is kept for debugging, mutates a `JobConf` for Pipes submission, submits the job, and supports command-line submission.

The `org.apache.hadoop.metrics` packages define Hadoop's original metrics API. `ContextFactory` is a singleton factory backed by `hadoop-metrics.properties`, attribute maps, and reflective context construction; absent configuration uses a no-op null context. `MetricsContext` defines monitoring lifecycle, record creation, updater registration, close, and `DEFAULT_PERIOD`. `MetricsRecord` is a tagged metric row with typed `setTag`, `removeTag`, typed `setMetric`, typed `incrMetric`, `update`, and `remove`. `MetricsUtil` simplifies context and record creation. `Updater` is the timer callback interface.

Metrics providers and SPI types continue the public surface. `metrics.file.FileContext` extends `AbstractMetricsContext` to append metrics records to a configured file, flush to disk, and expose file/period property names. `metrics.ganglia.GangliaContext` emits records to Ganglia. `metrics.jvm.EventCounter` is a Log4J appender that counts fatal, error, warn, and info events; `JvmMetrics` registers JVM metrics via `init` and periodic `doUpdates`. `metrics.spi.AbstractMetricsContext` implements context initialization, attribute lookup tables, synchronized start/stop/close, final record creation, updater registration, abstract `emitRecord`, optional `flush`, buffered row `update`/`remove`, and period configuration. `MetricsRecordImpl` implements the `MetricsRecord` operations and delegates `update`/`remove` back to its context.

## Control flow and behavioral contracts

Task execution flow is TaskTracker-centered. A TaskTracker starts with a `JobConf`, cleans local storage on startup, connects to the JobTracker through `InterTrackerProtocol`, then runs a retry loop that reinitializes when tracker state becomes stale. Child processes call back to fetch a `Task`, then periodically send `statusUpdate`, `ping`, diagnostics, completion notifications, shuffle failures, local filesystem errors, and map-output-loss notifications through the umbilical protocol. TaskTracker HTTP servlets expose task logs and map outputs.

Task logging flow wraps task or debug commands before execution. `captureOutAndError` can prepend setup commands, redirect stdout/stderr to files, and cap retained output by tail length, where zero means complete output. `TaskLog.cleanup` is synchronized and purges old logs by retention hours. `TaskLogAppender` is configured by Log4J properties and writes task-child system logs under the task id.

JobControl flow is a small state machine. Jobs begin in `WAITING`; if dependencies are all `SUCCESS`, they become `READY`; if a dependency fails, they become `DEPENDENT_FAILED` or failed. The `JobControl.run` loop checks running jobs, moves waiting jobs based on dependencies, submits ready jobs, and honors suspend/resume/stop state. `Job.submit` changes state to `RUNNING` on successful submission and to `FAILED` otherwise.

Join input flow starts with `CompositeInputFormat.setFormat`, which parses `mapred.join.expr` into an operator tree. `getSplits` asks each child input format for splits and combines the ith child split from each source into one `CompositeInputSplit`. `getRecordReader` creates composable readers for those child splits. During reading, child readers are ordered by a shared `WritableComparator`; matching keys are gathered into a `JoinCollector`; a concrete reader's `combine` or `emit` policy determines whether an inner tuple, outer tuple, or overridden rightmost value is output.

Composable readers and resetable iterators are explicitly stateful. Each reader keeps a head key/value and supports skipping to keys greater than a supplied key. Join collectors need iterators that can buffer all values for a key, replay the current value, reset to the start of the buffered range, clear contents for reuse, and close underlying resources.

Library mapper/reducer utilities follow standard old `mapred` callbacks: `configure`, `map`, `reduce`, `close`, and `OutputCollector.collect`. `MultithreadedMapRunner` reads from one `RecordReader` and invokes mapper logic concurrently, which shifts correctness responsibility to thread-safe mapper implementations and synchronized output/reporting paths. `MultipleOutputFormat` returns a composite writer that chooses a concrete file and optionally transformed key/value for each record.

Aggregate flow is data-driven by aggregation type prefixes encoded in `Text` keys. The mapper asks each configured `ValueAggregatorDescriptor` to produce aggregation id/value pairs. The combiner and reducer inspect the aggregation type, instantiate the corresponding `ValueAggregator`, feed all values through `addNextValue`, and emit either combiner output or final `getReport` output. User descriptors are loaded by class name and configured from `JobConf`.

Pipes submission flow mutates the supplied `JobConf` before submission so the framework knows the executable location and which components are native versus Java. The keep-command-file path is a debug path that causes command data to be retained in the task directory as `downlink.data` and is intended to be paired with retained failed task files.

Metrics flow is context and timer based. `ContextFactory.getFactory` loads attributes from `hadoop-metrics.properties`; `getContext` constructs a named context reflectively or returns a null context. Clients create a `MetricsRecord`, set tags and metrics, then call `update` to insert or replace a buffered row keyed by tags, or `remove` to remove matching rows. A monitoring context calls registered `Updater.doUpdates` periodically, emits buffered records through provider-specific `emitRecord`, and flushes after a period. `stopMonitoring` stops emission without necessarily freeing buffered data; `close` stops monitoring and frees buffered state.

## State, persistence, and side effects

The XML itself is persistent API compatibility metadata. Runtime state described by the APIs includes task ids and reports, local task logs, task child processes, TaskTracker local storage, HTTP endpoints, JobTracker RPC connections, map outputs, job dependency graphs, join parser trees, input split serialization, buffered join values, output files, aggregation accumulators, Pipes command files, metrics contexts, metric records, updater callbacks, and provider resources.

TaskTracker and task logging have filesystem and network side effects. `cleanupStorage` removes temporary storage; `close` shuts down running tasks, threads, components, and disk usage; log capture writes stdout, stderr, debug, and Log4J output files under a location derived from `hadoop.log.dir`; log cleanup deletes old user logs; `TaskLogServlet` and `MapOutputServlet` publish local files over HTTP.

JobControl's persistent state is in-memory, not a durable scheduler. It stores jobs in state-specific tables, assigns group-unique ids, and records dependency and message state. The actual MapReduce job state persists in the cluster through submitted `RunningJob`/`JobID` state, not in `JobControl` itself.

Join APIs persist `CompositeInputSplit` and `TupleWritable` instances through Hadoop `Writable` serialization. `CompositeInputSplit` requires child split classes to have public default constructors because it serializes class names/types before child payloads. `TupleWritable` serializes child writable types and values and preserves per-position presence, which makes type identity and tuple arity compatibility-sensitive.

Output utilities affect filesystems. `TextOutputFormat`, multiple-output formats, sequence-file output formats, and N-line input split generation all depend on Hadoop `FileSystem`, `Path`, and `JobConf` state. `MultipleOutputFormat` can create many files based on record data or input-file path segments, so filename generation and writer caching are externally visible behavior.

Aggregators maintain mutable in-memory accumulator state. Numeric sum/min/max classes keep current numeric totals or extrema; string min/max keep current string extrema; `UniqValueCount` keeps a set bounded by `maxItems`; `ValueHistogram` keeps a `TreeMap` of value/frequency pairs. Combiner output is serialized as strings for downstream reducers.

Metrics contexts hold mutable process-wide state through singleton factory attributes, cached named contexts, registered updaters, monitoring timers, buffered tag/metric rows, and provider handles. File metrics append to and flush a disk file; Ganglia metrics send network datagrams; JVM metrics read process counters; Log4J event counting mutates static level counters.

## Dependencies and integration points

The `mapred` APIs integrate with `JobConf`, `JobID`, `TaskID`, `TaskAttemptID`, `TaskStatus`, `TaskCompletionEvent`, `Counters`, `Reporter`, `InterTrackerProtocol`, `TaskUmbilicalProtocol`, `MRConstants`, `RunningJob`, old `Mapper`/`Reducer`/`Partitioner`/`InputFormat`/`OutputFormat` contracts, Hadoop `Writable` types, Java servlets, Jetty-hosted HTTP paths, Log4J, Commons Logging, and Java `IOException`/network/file primitives.

Join APIs depend on old `mapred` input contracts, `InputSplit`, `RecordReader`, `Reporter`, `Writable`, `WritableComparable`, `WritableComparator`, `RawComparator`-style key ordering, `Path`, `Configuration`, `JobConf`, Java reflection constructors, priority queues, and `DataInput`/`DataOutput` serialization. They assume child sources are sorted and partitioned compatibly.

Library utilities integrate with Hadoop filesystem output, `FileOutputFormat`, `FileSystem`, `Progressable`, `LongWritable`, `Text`, Java regex matching, multithreading primitives, old job configuration keys, and output collectors. Multiple-output classes are intended for downstream subclassing via protected filename/key/value/base-writer hooks.

Aggregate APIs integrate with descriptors loaded by class name, `GenericOptionsParser` for command-line job creation, `JobControl` for generated job groups, `Text` key/value aggregation streams, and the old mapred mapper/reducer/combiner lifecycle.

Pipes integrates Java MapReduce configuration with external native executables, normally addressed through HDFS URIs, and with retained task directories for debugging command streams.

Metrics integrate with `hadoop-metrics.properties`, reflection-based provider classes, `ContextFactory`, `MetricsContext`, `MetricsRecord`, `Updater`, file output, Ganglia, Log4J appenders, JVM instrumentation, UDP/network output, and provider SPI subclasses of `AbstractMetricsContext`.

## Risks and compatibility notes

This is a line-bounded API chunk. The opening `TaskID` content is only tail documentation, and the ending `MetricValue` entry is incomplete. Whole-class conclusions for those boundary areas require adjacent chunks.

The XML captures public API, not implementations. JDiff consumers should treat method signatures, visibility, exceptions, deprecation text, and field constants as stable compatibility signals, but should not infer internal algorithms beyond the Javadocs.

TaskTracker and task-log APIs are operationally sensitive. Changes to task id overloads, synchronization on status/lifecycle methods, log file naming, command quoting, output tailing, cleanup retention, servlet parameters, or shuffle/map-output error reporting can break child processes, web UI log access, or failure recovery.

JobControl is concurrency-sensitive because it exposes mutable job lists and state transitions while running as a thread. Dependency additions are valid only while a job is waiting; violating that state model can create races or inconsistent scheduling.

Join APIs have strong data-shape assumptions. All joined sources must be sorted and partitioned identically with a compatible comparator. Duplicate child ids have undefined behavior, child split counts must align, child split classes need default constructors, and parser expression or reflection failures surface as job setup failures. Iterator replay/clear/close semantics are easy to misuse and can leak buffers or drop values.

`TupleWritable` and `CompositeInputSplit` serialization are compatibility-sensitive because they encode class/type metadata. Renaming classes, changing constructors, or changing tuple arity/presence semantics can break stored splits or intermediate data.

Multiple output classes can create unbounded numbers of files if filename generation depends too directly on high-cardinality keys. They also need path sanitization and collision awareness in subclasses because generated file names become filesystem paths.

`MultithreadedMapRunner` can expose mapper thread-safety bugs that do not appear under the default single-threaded runner. Mapper shared state, reporter usage, and output collector interactions require tests under concurrency.

Aggregate APIs parse numeric and structured values from strings. Malformed input, overflow, inconsistent combiner formats, high-cardinality unique counts or histograms, and user descriptor reflection errors are key risk areas.

Pipes configuration mutates the caller's `JobConf`. Incorrect Java/native component flags, missing executables, bad HDFS URIs, or retained command-file handling can make jobs fail only at task launch time.

Metrics lifecycle is stateful and potentially concurrent. Updater registration, buffered row replacement/removal by tags, incremental versus absolute metric handling, provider `flush`/`close`, singleton factory attributes, and reflection-based provider selection can cause stale metrics, duplicate metrics, lost metrics, or resource leaks if ordered incorrectly.

## Test signals

JDiff tests should verify this range remains well formed and preserves package/class/interface boundaries, inheritance and implemented interfaces, method signatures, overloads, parameter types, declared exceptions, synchronization/static/final/abstract flags, field constants, deprecation markers, and embedded Javadocs.

Task and TaskTracker tests should cover task log file resolution by string and `TaskAttemptID`, log cleanup retention, command wrapping with full and tailed output, setup command ordering, debug output capture, Log4J appender task id and log size configuration, log servlet responses, `TaskReport` writable round trips, TaskTracker startup cleanup, child task fetch, status update, diagnostics, ping/done, shuffle/local filesystem error paths, map completion event lookup, map output lost notification, idle detection, and close/shutdown cleanup.

JobControl tests should cover dependency state transitions from `WAITING` to `READY`, propagation of dependency failure, successful and failed submission paths, adding dependencies only while waiting, id assignment, state-list membership, suspend/resume/stop behavior, and `allFinished` results.

Join tests should cover expression composition/parsing, default and custom join operator registration, child input validation, split alignment across children, `CompositeInputSplit` serialization with child classes, inner/outer/override join semantics, key comparator ordering, skip behavior, duplicate child id handling, `WrappedRecordReader` head caching, resetable iterator replay/reset/clear/close, tuple presence bits, tuple serialization, and progress reporting as minimum child progress.

Mapred lib tests should cover field-selection specs and separators, hash and key-field partitioning stability, identity/inverse/sum/token/regex mapper-reducer behavior, multiple-output filename/key/value overrides, input-file-based filenames, text and sequence multiple-output writers, N-line split sizes, null output validation, and multithreaded runner behavior with thread-safe and intentionally unsafe mappers.

Aggregate tests should cover all built-in aggregators, combiner output formats, numeric parsing and overflow cases, unique-count limits, histogram statistics and details, descriptor key/value generation, user descriptor reflection/configuration, mapper/combiner/reducer end-to-end output, and `ValueAggregatorJob` creation from command-line arguments and descriptor classes.

Pipes tests should cover executable URI set/get, Java component flags, keep-command-file set/get, `submitJob` configuration mutation, missing executable failures, and command-line submission argument handling.

Metrics tests should cover factory attribute load/set/remove, singleton behavior, null-context fallback, reflective context creation, context lifecycle start/stop/restart/close, updater registration and unregistration, record creation conflicts, typed tags and metrics, tag removal, absolute and incremental metric updates, row update/remove semantics, metrics util helpers, file context append/flush/close, Ganglia emission setup, Log4J event counters, JVM updater initialization, and `MetricsRecordImpl` delegation to `AbstractMetricsContext`.

### subset-b-007278: lines 30886-37174

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml lines 30886-37174

## Chunk Scope

This chunk is a JDiff API XML slice for Hadoop 0.18.2. It begins inside `org.apache.hadoop.metrics.spi.MetricValue`, covers complete packages for metrics utilities, networking, record I/O, record compiler/runtime metadata, security user/group identity, and tools, then ends inside `org.apache.hadoop.util.GenericsUtil`. Because the source is API metadata rather than Java implementation, it exposes public/protected signatures, inheritance, exceptions, fields, and Javadoc, but not method bodies.

## Purpose

The slice documents several common Hadoop infrastructure surfaces:

- Metrics contexts and value helpers used to collect, buffer, and publish metrics, including no-op contexts, JMX registration helpers, point-in-time values, and time-varying counters/rates.
- Network helpers for DNS/interface lookup, rack topology modeling, socket factories, and timeout-aware socket streams.
- The legacy Hadoop Record I/O runtime, including binary/CSV/XML serializers, deserializers, mutable buffers, raw comparators, record interfaces, and zero-compressed numeric encoding utilities.
- The Record I/O compiler API and JavaCC-generated parser/token support for `.jr` record definition files, plus an Ant task wrapper.
- User/group identity abstractions for Unix-backed Hadoop security state.
- Operational Hadoop tools for distributed copy, Hadoop archive creation, and log archiving/analysis.
- Early generic utility classes for daemon threads, disk checks, generic command-line option parsing, and Java generics helpers.

## Important APIs, Types, And Functions

### Metrics SPI and Utility APIs

- `org.apache.hadoop.metrics.spi.MetricValue` wraps a `Number` as either `ABSOLUTE` or `INCREMENT`, with `isIncrement()`, `isAbsolute()`, and `getNumber()`.
- `NullContext` extends `AbstractMetricsContext` and deliberately implements `startMonitoring()`, `emitRecord(...)`, `update(MetricsRecordImpl)`, and `remove(MetricsRecordImpl)` as no-ops. It is documented as the default context when no metrics configuration is found.
- `NullContextWithUpdateThread` also extends `AbstractMetricsContext`; it keeps the update thread behavior from the abstract context but emits no data. This is useful for metrics systems such as JMX that sample values by reading them externally.
- `OutputRecord` exposes read-only metric output shape: tag names, tag lookup, metric names, and metric lookup.
- `metrics.spi.Util.parse(String specs, int defaultPort)` parses comma/space separated `host` or `host:port` server specs into `InetSocketAddress` values, defaulting to localhost when specs are null.
- `MBeanUtil.registerMBean(serviceName, nameName, theMbean)` and `unregisterMBean(ObjectName)` integrate Hadoop metrics with JMX under the documented `hadoop.dfs:service=...,name=...` naming convention.
- `MetricsIntValue` and `MetricsLongValue` are synchronized mutable scalar metrics with `set`, `get`, increment/decrement overloads, and `pushMetric(MetricsRecord)`. They publish only after being updated and only once per update.
- `MetricsTimeVaryingInt` publishes interval deltas through `pushMetric(...)` and exposes `getPreviousIntervalValue()`.
- `MetricsTimeVaryingRate` tracks operation count and elapsed time through `inc(numOps, time)` / `inc(time)`, then exposes previous interval count, average time, min time, max time, and `resetMinMax()`.

### Networking APIs

- `DNS` provides reverse and forward lookup helpers: `reverseDns`, `getIPs`, `getDefaultIP`, `getHosts`, and `getDefaultHost`, with overloads for explicit or default nameservers and `UnknownHostException` / `NamingException` failure modes.
- `DNSToSwitchMapping.resolve(List<String>)` is the pluggable contract for resolving host/IP values to rack names, returning `NetworkTopology.DEFAULT_RACK` when topology cannot be determined.
- `NetUtils` centralizes socket factory and address handling: configurable socket factory lookup, default factory creation, proxy property interpretation, `createSocketAddr`, old host/port configuration transition via `getServerAddress`, static host resolution mappings, client connect address normalization, and timeout-aware socket input/output streams.
- `NetworkTopology` models the cluster as a rack/host tree. Public operations include adding/removing leaves, membership lookup, rack and leaf counts, distance and same-rack checks, scoped random choice, availability counting with exclusions, string rendering, and distance-based pseudo-sort.
- `Node` is the topology node interface with network location, name, parent, and tree level accessors/mutators. `NodeBase` implements it and adds path normalization and constants such as `PATH_SEPARATOR`, `ROOT`, and backing fields for name, location, level, and parent.
- `ScriptBasedMapping` implements both `Configurable` and `DNSToSwitchMapping`, using a configured script to map DNS names/IP addresses to switch or rack paths.
- `SocketInputStream` and `SocketOutputStream` wrap NIO channels or sockets to add read/write timeout behavior. They expose channel access, open checks, readiness waits, and byte/block read/write methods; output also provides `transferToFully(FileChannel, position, count)`.
- `SocksSocketFactory` is a `SocketFactory` with optional SOCKS `Proxy` and `Configurable` support. `StandardSocketFactory` is the ordinary non-proxy factory despite a copied Javadoc line claiming SOCKS behavior.

### Record I/O Runtime

- `BinaryRecordInput` / `BinaryRecordOutput` implement `RecordInput` / `RecordOutput` over `DataInput` and `DataOutput`, including thread-local `get(...)` factories and primitive/string/buffer/record/vector/map read/write methods.
- `CsvRecordInput` / `CsvRecordOutput` provide the same serializer interfaces for CSV-like textual record data.
- `XmlRecordInput` / `XmlRecordOutput` provide XML deserialization/serialization.
- `Buffer` is a mutable byte sequence implementing `Comparable` and `Cloneable`. It supports adopting or copying byte arrays, capacity changes, reset/truncate/append, lexicographic comparison, equality/hash, string conversion with optional encoding, and clone.
- `Index` is the iterator-like return type from `RecordInput.startVector` and `startMap`; callers loop with `done()` and `incr()` to deserialize collection elements.
- `Record` is the abstract base for generated records. It implements Hadoop `WritableComparable` and `Cloneable`, requires tagged `serialize`, tagged `deserialize`, and `compareTo`, and provides untagged serialization/deserialization plus `write(DataOutput)`, `readFields(DataInput)`, and `toString()`.
- `RecordComparator` extends `WritableComparator` for raw byte comparison and exposes synchronized static `define(Class, RecordComparator)` registration.
- `RecordInput` and `RecordOutput` are the core serializer/deserializer contracts for byte, boolean, int, long, float, double, string, `Buffer`, record, vector, and map boundaries. Tags are explicitly for tagged formats such as XML.
- `org.apache.hadoop.record.Utils` contains variable-length and zero-compressed numeric helpers: `readFloat`, `readDouble`, `readVLong`, `readVInt`, stream-based `readVLong` / `readVInt`, `getVIntSize`, `writeVLong`, `writeVInt`, and `compareBytes`.

### Record Compiler And Parser APIs

- `CodeBuffer` wraps `StringBuffer` with indentation behavior for generated code text.
- `Consts` defines Record I/O compiler constants such as `RIO_PREFIX`, runtime type info variables/filters, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.
- `JType` is the abstract base for compiler type models. Concrete primitive and composite models include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, and `JRecord`. `JField<T>` wraps a named field and type. `JFile` represents one record definition file, its includes, and records, and can `genCode(language, destDir, options)`.
- `RccTask` is an Ant `Task` that invokes the record compiler. It accepts `language`, single `file`, nested `FileSet`s, `destdir`, and `failonerror`; `execute()` throws `BuildException`.
- Generated parser classes in `org.apache.hadoop.record.compiler.generated` include:
  - `Rcc`, the JavaCC parser and command-line driver. It parses `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, returns compiler model objects, supports `ReInit`, and exposes token navigation and parse exception generation.
  - `RccConstants`, token ids for Record I/O grammar tokens including module, record, include, primitive types, vector/map delimiters, punctuation, string and identifier tokens, lexical states, and token images.
  - `RccTokenManager`, the lexer with debug stream, lexical state switching, token filling, and `getNextToken()`.
  - `SimpleCharStream`, the JavaCC character stream implementation with line/column tracking, buffer expansion/refill, backup, reinitialization overloads, image/suffix access, and cleanup.
  - `Token`, the token node structure with kind, begin/end positions, image, regular-token chain, and special-token chain.
  - `ParseException` and `TokenMgrError`, generated error-reporting classes that build parse/lexical diagnostics from current token, expected token sequences, token images, lexical state, and offending character context.

### Record Metadata APIs

- `FieldTypeInfo` pairs a field id with a `TypeID`, and implements equality and hash code.
- `TypeID` represents primitive Record I/O type ids and exposes shared constants for bool, buffer, byte, double, float, int, long, and string. Nested `TypeID.RIOType` declares byte constants for all supported IDL types, including map, struct, and vector.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` extend `TypeID` to model nested map, vector, and record/struct shapes.
- `RecordTypeInfo` extends `Record` to serialize and deserialize runtime record type metadata. It stores a record name, supports adding fields, returns field metadata, finds nested struct type info by name, and deliberately throws/does not implement meaningful `compareTo` because it is not intended as a key.
- `record.meta.Utils.skip(RecordInput, String tag, TypeID typeID)` skips serialized values based on type metadata.

### Security APIs

- `UserGroupInformation` is an abstract `Writable` for user/group identity. It includes thread-local current UGI accessors (`getCurrentUGI`, `setCurrentUGI`), abstract `getUserName`, `getGroupNames`, and `login`, plus `readFrom(Configuration)`. It has a Commons Logging `LOG`.
- `UnixUserGroupInformation` extends `UserGroupInformation` with Unix-backed user and group arrays. It supports mutable constructors, `createImmutable`, serialization/deserialization, saving to configuration under `UGI_PROPERTY_NAME`, reading from configuration, several `login` overloads including current Unix user/group lookup, and equality/hash/toString.

### Tool And Utility APIs

- `DistCp` implements `Tool`, with configuration accessors, `copy(srcPaths, dstPath, srcAsList, ignoreReadFailures)`, `run(args)`, `main(args)`, and static `getRandomId()`. Nested `DuplicationException` extends `IOException` and exposes an `ERROR_CODE`.
- `HadoopArchives` implements `Tool` for creating Hadoop archives, with `archive(srcPaths, archiveName, dest)`, `run(args)`, and `main(args)`.
- `Logalyzer` archives and analyzes Hadoop logs. `doArchive(logListURI, archiveDirectory)` archives listed logs, and `doAnalyze(inputFilesDirectory, outputDirectory, grepPattern, sortColumns, columnSeparator)` runs grep/sort-style MapReduce analysis. Nested `LogComparator` is a configurable raw `Text.Comparator`, and `LogRegexMapper` is a MapReduce mapper that emits regular-expression matches as `Text` and `LongWritable`.
- `Daemon` is a daemon `Thread` wrapper with constructors for no runnable, runnable, and thread group plus runnable, and exposes the backing runnable.
- `DiskChecker` provides `mkdirsWithExistsCheck(File)` for race-tolerant directory creation and `checkDir(File)` for disk/directory validation. Nested `DiskErrorException` and `DiskOutOfSpaceException` are `IOException` subclasses.
- `GenericOptionsParser` parses Hadoop generic command-line options into a `Configuration` and optional Commons CLI `CommandLine`; it exposes `getRemainingArgs`, `getCommandLine`, and `printGenericCommandUsage`. Its documented options include `-conf`, `-D`, `-fs`, `-jt`, `-files`, `-libjars`, and `-archives`.
- The chunk ends at `GenericsUtil.getClass(T)`, after showing `GenericsUtil` as a utility holder with a public constructor. The following lines outside this chunk likely continue `GenericsUtil` methods.

## Control Flow And Data Flow

- Metrics flow is producer driven: callers mutate metrics (`set`, `inc`, `dec`), metrics helpers remember whether/what changed, and `pushMetric(MetricsRecord)` emits values during context update intervals. `NullContext` suppresses the emission branch, while `NullContextWithUpdateThread` preserves sampling cadence without a sink.
- Record I/O flow is generated-record driven: a generated `Record` calls `RecordOutput.startRecord`, writes primitive/composite fields using tag names, and closes record/vector/map scopes. Deserialization mirrors that flow with `RecordInput.startRecord`, primitive reads, and `Index` loops for vectors/maps.
- Binary, CSV, and XML input/output classes share the same interface but differ in wire representation. Tagged names matter for XML and are ignored or positional in less tagged formats.
- Record compiler flow starts with `Rcc.driver` or `RccTask.execute`, parses `.jr` definitions through JavaCC parser methods into `JFile`, `JRecord`, `JField`, and `JType` models, then `JFile.genCode` emits code for the requested language and destination directory.
- Network topology flow maps hostnames/IPs to rack paths through `DNSToSwitchMapping`, represents the cluster as `Node`/`NodeBase` leaves in `NetworkTopology`, and uses distance or rack checks for placement decisions.
- Socket stream flow wraps a socket channel, waits for readiness with timeout, and delegates actual byte transfer through NIO channel operations. `NetUtils.getInputStream` / `getOutputStream` choose these wrappers when a channel exists.
- Security flow centers on obtaining or deserializing a `UserGroupInformation`, storing it in thread-local current identity, optionally persisting it as configuration text, and serializing it through Hadoop `Writable`.
- Tool flow follows the `Tool` pattern: construct with `Configuration`, parse `run(String[] args)`, execute filesystem/MapReduce work, and return an integer status to `main`.

## State And Persistence Behavior

- Metrics value classes hold in-memory counters, previous interval values, dirty/update flags, and min/max rate state. Public methods are synchronized for scalar and time-varying metrics, signaling thread sharing between metric producers and updater threads.
- `OutputRecord` is a read-only view of tags and metrics being emitted from a metrics context.
- `NetworkTopology` maintains an in-memory tree of racks and leaves, parent pointers, levels, and counts. `NetUtils` also maintains static host resolution overrides visible through add/get/list methods.
- `NodeBase` persists path identity in `name`, `location`, `level`, and `parent`; normalization protects topology path consistency.
- `Buffer` owns mutable backing byte storage and count/capacity metadata. `set` adopts caller-provided arrays, while `copy` replaces contents by copying, which is an important aliasing distinction.
- Record serialization persists generated records to `DataOutput`, CSV, XML, or other `RecordOutput` implementations. `RecordTypeInfo` persists schema/type metadata as a `Record`.
- JavaCC parser classes hold mutable parser state (`token_source`, `token`, `jj_nt`), lexer state, character buffer, line/column arrays, and token chains.
- `UnixUserGroupInformation` persists user/group state via `Writable` methods and configuration property `UGI_PROPERTY_NAME`.
- `DistCp`, `HadoopArchives`, and `Logalyzer` persist external data by creating destination copies, archives, archive indexes, and analysis output directories, but the XML slice only documents method contracts, not output layout details.

## Dependencies And Integration Points

- Metrics APIs depend on `org.apache.hadoop.metrics.MetricsRecord`, SPI classes such as `AbstractMetricsContext` and `MetricsRecordImpl`, JMX (`javax.management.ObjectName`), and JDK networking collections.
- Networking depends on JNDI (`NamingException`) for DNS, `java.net`, NIO channels, Hadoop `Configuration` / `Configurable`, Commons Logging, and topology consumers elsewhere in HDFS/MapReduce.
- Record I/O depends on Hadoop `WritableComparable`, `WritableComparator`, Java collections, streams, and generated record classes.
- Record compiler APIs integrate with Ant, JavaCC-generated parser/lexer code, compiler model objects, and generated Java/C++ record code.
- Security integrates with Hadoop `Configuration`, `Writable`, Java login exceptions, Unix user/group discovery, and thread-local execution context.
- Tool classes integrate with Hadoop `Tool`, filesystem `Path`, MapReduce old API classes (`Mapper`, `MapReduceBase`, `OutputCollector`, `Reporter`, `JobConf`), `Text`, `LongWritable`, and `Text.Comparator`.
- `GenericOptionsParser` integrates Hadoop command launchers with Commons CLI and configuration mutation.

## Risks And Edge Cases

- This is API XML only; implementation details such as validation logic, internal data structures, exact exception paths, and synchronization granularity beyond method modifiers must be confirmed in Java sources.
- `NullContext` intentionally drops metrics. Misconfiguration can therefore silently suppress operational visibility.
- Metrics helpers publish only on update intervals and often only once after a change; callers expecting cumulative every-interval values can misread point-in-time versus time-varying semantics.
- `Buffer.set(byte[])` aliases caller-provided storage; mutation outside the buffer can affect serialized or compared values. `copy` is safer when ownership is unclear.
- Record I/O compatibility depends on exact field order, tags for XML, and variable-length numeric encoding. Comparator and `compareBytes` behavior are test-critical for sorted MapReduce keys.
- `RecordTypeInfo.compareTo` is not meaningful by design, so use as a `WritableComparable` key is risky despite inheritance from `Record`.
- DNS and script-based rack mapping can fail or return unresolved/default racks, affecting placement/rack-awareness logic.
- Static host resolution overrides in `NetUtils` can affect all callers in-process.
- Socket timeout stream behavior is likely sensitive to channel presence, zero timeout semantics, readiness polling, and partial transfer handling.
- `SocksSocketFactory` equality/hash and configuration behavior can affect connection pooling or factory caching. `StandardSocketFactory` has misleading Javadoc copied from SOCKS factory.
- `UnixUserGroupInformation` stores identities in configuration as comma-separated text; malformed, missing, or stale configuration can change effective user/group behavior.
- `GenericOptionsParser` mutates `Configuration` from command-line options, so downstream tools may observe filesystem, jobtracker, file, libjar, and archive changes.
- Parser classes are generated and stateful; reuse requires correct `ReInit`, and lexical/parser error messages expose token/image arrays.

## Test Signals

- Metrics tests should verify dirty/one-shot push behavior, previous interval snapshots, min/max reset, synchronized increments/decrements, JMX object name registration/unregistration, and no-op context suppression.
- Networking tests should cover DNS lookup fallbacks, static host resolution, socket address parsing, old/new server address transition, proxy/default socket factories, timeout read/write behavior, `transferToFully`, topology add/remove/distance/same-rack/random selection, and script mapping default-rack behavior.
- Record I/O tests should round-trip generated records through binary, CSV, and XML serializers; verify `Index` loop boundaries; compare raw bytes through `RecordComparator`; validate `Buffer` capacity/aliasing/comparison/string conversion; and test zero-compressed integer read/write compatibility.
- Record compiler tests should parse modules, includes, primitive fields, maps, vectors, nested records, syntax errors, Ant task file/file-set inputs, fail-on-error behavior, destination directory output, and Java/C++ language option handling.
- Metadata tests should serialize/deserialize `RecordTypeInfo`, compare `TypeID` / map / vector / struct equality and hash codes, and verify `meta.Utils.skip` over every supported type.
- Security tests should cover UGI serialization, configuration save/read, login overloads, thread-local current UGI behavior, immutable UGI behavior, and equality/hash/toString consistency.
- Tool tests should exercise `DistCp` duplicate source detection and random id generation, Hadoop archive command parsing and archive creation, Logalyzer archive/analyze argument handling, regex mapper output, and log comparator sorting.
- Utility tests should validate `Daemon` daemon-thread flag/runnable retention, `DiskChecker` race-tolerant mkdirs and failure cases, generic option parsing for all documented options, remaining args extraction, and generic usage printing.

## Unresolved Cross-Chunk References

- The preceding chunk contains the start of `MetricValue` and the end of `MetricsRecordImpl`, including the full buffered metrics mutation contract feeding into this chunk.
- The `DNSToSwitchMapping`, `Node`, `Index`, `RecordInput`, `RecordOutput`, and `RccConstants` interface starts are visible in this chunk even though the high-level class-boundary inventory comments in the XML omit some interface start/end markers in the package map.
- The following chunk continues `GenericsUtil` after `getClass(T)` and likely includes `toArray(...)` methods shown just beyond the requested line boundary.

### subset-b-007279: lines 37175-38788

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml lines 37175-38788

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.18.2, not Java implementation code. It starts inside `org.apache.hadoop.util.GenericsUtil`, then covers the rest of the `org.apache.hadoop.util` package through `XMLUtils`, and ends at the closing `</api>` marker. The XML records compatibility metadata: class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadoc contracts.

The covered API surface is mostly Hadoop's utility layer: generic array helpers, indexed sorting contracts and sort implementations, host include/exclude file loading, native library loading flags, platform/build helpers, priority queue and progress tracking utilities, command dispatch and jar execution, servlet helpers, shell command execution, string/URI/path formatting helpers, the `Tool`/`ToolRunner` command-line contract, version metadata access, and XML transformation.

## Purpose and Major API Surface

`GenericsUtil` exposes generic type helpers: `getClass(T)` returns a correctly typed `Class<T>`, `toArray(Class<T>, List<T>)` converts a list using an explicit element class, and `toArray(List<T>)` infers the element class from the list but documents an `ArrayIndexOutOfBoundsException` risk for empty lists.

`IndexedSortable` and `IndexedSorter` define the abstraction used by Hadoop's in-place sort algorithms. `IndexedSortable` supplies address-based `compare(int, int)` and `swap(int, int)`. `IndexedSorter` sorts the half-open logical index range `[l, r)` and has an overload that periodically reports progress through `Progressable`.

`HeapSort` and `QuickSort` implement `IndexedSorter`. `HeapSort` is a final heap-sort implementation. `QuickSort` is a final quick-sort implementation with a protected static `getMaxDepth(int)` helper and Javadoc stating that it switches to `HeapSort` when recursion gets too deep.

`MergeSort` is a separate core merge-sort implementation constructed with a `Comparator<IntWritable>` and exposes `mergeSort(int[] src, int[] dest, int low, int high)`.

`HostsFileReader` reads host inclusion and exclusion files from constructor-provided paths. `refresh()` reloads the files and may throw `IOException`; `getHosts()` and `getExcludedHosts()` return the current host sets.

`NativeCodeLoader` is the native Hadoop library gate. `isNativeCodeLoaded()` reports whether `libhadoop` is loaded. `getLoadNativeLibraries(JobConf)` and `setLoadNativeLibraries(JobConf, boolean)` expose a per-job configuration switch controlling whether native libraries may be used when present.

`PlatformName`, `PrintJarMainClass`, and `VersionInfo` are small runtime/build helpers. `PlatformName.getPlatformName()` returns the JVM platform name and `main` prints it. `PrintJarMainClass.main` prints the main class from a jar. `VersionInfo` exposes Hadoop build metadata through `getVersion`, `getRevision`, `getDate`, `getUser`, `getUrl`, `getBuildVersion`, and `main`.

`PriorityQueue` is an abstract heap-like queue over `Object`. Subclasses provide `lessThan(Object,Object)` and must call protected final `initialize(int maxSize)`. Public final operations include `put`, `top`, `pop`, `adjustTop`, `size`, and `clear`; `insert` conditionally adds an element if the queue has capacity or the element is competitive with the current top.

`ProgramDriver` is a named program registry for example/application launchers. `addClass(String, Class, String)` records a runnable main class and description, and `driver(String[])` dispatches based on `args[0]`, invoking the target class's `main` with remaining arguments. Both can throw broad reflective or application errors.

`Progress` models hierarchical task progress. It creates a root node, supports adding named or unnamed phases, moving to the next phase, returning the current sub-phase, marking a node complete, setting leaf progress, computing root progress, setting status, and formatting state through `toString`. Several phase/progress/status methods are synchronized.

`Progressable` is the callback interface for long-running work to report liveness to Hadoop. The docs call out timeout avoidance for operations that otherwise appear stalled.

`ReflectionUtils` centralizes reflection helpers. `setConf(Object, Configuration)` injects configuration into configurable objects, `newInstance(Class<?>, Configuration)` constructs and initializes instances, `getClass(T)` returns a correctly typed class, and thread-diagnostic helpers enable contention tracing plus print or log stack information with an interval guard.

`RunJar` unpacks and runs Hadoop job jars. `unJar(File, File)` extracts a jar into a directory. `main(String[])` runs a job jar, using the manifest main class or a command-line main class when absent.

`ServletUtil` supplies web UI helpers: `initHTML(ServletResponse, String)` starts an HTML response and returns a `PrintWriter`, `getParameter(ServletRequest, String)` trims request parameters and returns null for whitespace-only values, `htmlFooter()` returns a standard footer, and `HTML_TAIL` is the footer constant.

`Shell` is an abstract base for running Unix-like commands with optional minimum re-execution intervals. Static helpers expose command arrays/strings for groups, permission lookup, permission/owner/group setting, user name lookup, and child-process memory limits from `JobConf`. Instance hooks configure environment and working directory, decide/run commands, expose the current `Process` and exit code, and require subclasses to implement `getExecString()` and `parseExecResult(BufferedReader)`. `Shell.ExitCodeException` adds an exit code to `IOException`. `Shell.ShellCommandExecutor` is a concrete small-output executor with constructors for command, working directory, and environment, plus `execute()` and `getOutput()`.

`StringUtils` is a broad static helper class. It stringifies exceptions, shortens hostnames, formats large integers and percentages, joins arrays, converts bytes to/from hex, converts URI and path arrays, formats elapsed times, parses comma-separated strings into arrays/collections, splits strings with escaping, escapes and unescapes separator characters, gets the hostname without throwing, and logs startup/shutdown messages. Public constants include `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`.

`Tool` extends `Configurable` and defines the standard Hadoop command-line application contract `run(String[])`. `ToolRunner` runs tools after generic Hadoop option parsing, sets the processed `Configuration` on the tool, offers an overload using `tool.getConf()`, and can print generic command usage.

`XMLUtils.transform(InputStream styleSheet, InputStream xml, Writer out)` applies an XSLT stylesheet to XML and surfaces `TransformerConfigurationException` and `TransformerException`.

## Control Flow and Behavioral Contracts

The XML does not contain method bodies, but the public contracts imply several flows. Indexed sorting callers adapt a data structure to `IndexedSortable`, then pass logical bounds to `HeapSort` or `QuickSort`. Sort implementations are constrained to mutate only through `compare` and `swap`; the progress overload can invoke `Progressable.progress()` during longer sorts.

Priority queue flow starts with subclass construction and `initialize(maxSize)`. `put` always inserts and can overflow the initialized capacity; `insert` is the safer top-N style operation because it can reject non-competitive elements when full. `top` is constant-time, while `put`, `pop`, and `adjustTop` are logarithmic. `adjustTop` is meant for mutating the top element in place and restoring heap order.

Progress flow is tree-shaped. A caller constructs a root `Progress`, adds child phases, advances with `startNextPhase()`, updates leaves with `set(float)`, and reads aggregate progress from the root with `get()`. `complete()` advances the parent to its next child, so parent/child relationships drive visible progress state.

Tool execution flow uses `ToolRunner.run`. Generic Hadoop options are parsed first through the related `GenericOptionsParser` contract, the resulting configuration is installed into the `Tool`, and then application-specific arguments are passed to `Tool.run`. The return value is the application exit code.

Shell execution flow is template-method based. A subclass provides the command vector and output parser. `run()` decides whether the minimum interval permits re-execution, starts a process with configured environment and working directory, parses stdout, records exit status, and can throw `IOException` or `ExitCodeException`. `ShellCommandExecutor` covers the simple case by collecting command output as a string.

Program and jar launch flows are reflective. `ProgramDriver` maps a short command name to a class with a `main` method and dispatches based on the first argument. `RunJar` extracts jar contents, locates the main class from the manifest or command line, and invokes it with remaining arguments.

String parsing flow centers on escaped comma-separated values. `escapeString`, `unEscapeString`, and `split` must agree on `ESCAPE_CHAR` and separator handling; callers that persist comma-separated configuration values depend on round-tripping through these helpers.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API compatibility data. Runtime state described by these APIs includes host include/exclude sets, job configuration flags, priority queue heap contents, progress tree nodes and status strings, command registries, shell process handles and exit codes, shell output buffers, servlet response output, and build/version metadata loaded from package or annotation resources.

Persistent or external side effects appear in several utilities. `HostsFileReader.refresh()` reads host files from disk. `NativeCodeLoader` observes native library loading and mutates `JobConf` settings for native library usage. `RunJar.unJar` writes extracted jar contents to a directory, and `RunJar.main` can execute arbitrary job code. `Shell` starts OS processes, sets process environment and working directory, may apply `ulimit` commands, and can expose platform-specific behavior through the `WINDOWS` flag. `ServletUtil.initHTML` writes HTTP response headers/body content. `XMLUtils.transform` writes transformed XML to the supplied writer. `ToolRunner.run` mutates the `Tool`'s configuration reference before calling it.

Most utility classes are stateless static helpers, but not all are thread-neutral. `Progress` marks several state-changing methods synchronized, while queue, shell executor, host reader, and program driver state are mutable and not documented as thread-safe in this XML.

## Dependencies and Integration Points

These utilities sit at integration boundaries across Hadoop common. Sorting depends on `IndexedSortable`, `Progressable`, `Comparator<IntWritable>`, and mutable caller-owned indexed data. Host loading integrates with local files and Java `Set<String>`.

Configuration and MapReduce integration appears through `Configuration`, `Configurable`, `JobConf`, `Tool`, `ToolRunner`, mapper/reducer child process memory limits, and the documented generic Hadoop command-line options.

Runtime diagnostics and system integration depend on Java reflection, `PrintWriter`, Apache Commons Logging `Log`, JVM thread information, Java `Process`, `File`, `BufferedReader`, servlet request/response APIs, jar manifests, and XSLT classes from `javax.xml.transform`.

Filesystem and command integration is platform-sensitive. `Shell` exposes Unix command constants and has explicit Windows detection; native Hadoop loading depends on `libhadoop` availability and platform-specific bundled libraries. `RunJar`, `PrintJarMainClass`, and `VersionInfo` integrate with jar/package metadata.

String and path helpers bridge Java primitives and Hadoop filesystem types: `URI[]`, `Path[]`, byte arrays, date formats, hostnames, exception stack traces, and comma-separated configuration values.

## Risks and Compatibility Notes

This chunk starts after the opening of `GenericsUtil`, so adjacent lines are needed for that class's exact start metadata. The rest of the package boundaries through `XMLUtils` are complete in this chunk.

Several APIs expose legacy raw types (`Class`, `Object`, non-generic `PriorityQueue`) because this is a Hadoop 0.18.2 API snapshot. Tightening those signatures would be source or binary incompatible for callers using the documented methods.

Sort contracts are sensitive to range interpretation. `IndexedSorter` documents `[l, r)` semantics, so off-by-one changes in implementations or callers can corrupt caller-owned structures. `QuickSort`'s fallback to `HeapSort` is part of the documented worst-case control behavior.

`GenericsUtil.toArray(List<T>)` is explicitly unsafe for empty lists. Callers that may pass empty lists should use `toArray(Class<T>, List<T>)`; changing the empty-list behavior may alter compatibility expectations.

`PriorityQueue` capacity and ordering are subclass-driven. The docs state `put` can throw an array bounds runtime exception when over capacity, while `insert` may reject elements; callers must choose the operation that matches their top-N semantics.

Shell and native utility behavior is platform and environment dependent. Command constants are Unix-oriented, memory-limit command generation may return null on non-Unix platforms or when unspecified, external commands can hang or produce large output, and `ShellCommandExecutor` explicitly expects small output.

`StringUtils` methods are often used for persisted configuration strings. Changes to escaping, splitting, hex conversion, time formatting, URI/path conversion, or hostname simplification can break configuration compatibility and user-facing logs.

`ToolRunner` is a central command-line compatibility point. Reordering generic option parsing, configuration installation, or argument forwarding can break MapReduce applications that implement `Tool`.

`RunJar` and `ProgramDriver` execute arbitrary code through reflection. Error propagation is intentionally broad (`Throwable`), so wrappers must preserve diagnostics rather than narrowing failures in ways that hide application exceptions.

## Test Signals

JDiff-level validation should confirm this XML remains well-formed through the closing `</api>`, preserves each public/protected class and interface in `org.apache.hadoop.util`, and keeps signatures, declared exceptions, field constants, synchronization flags, final/static/abstract flags, visibility, and Javadoc deprecation markers stable.

Sorting tests should adapt arrays or lists to `IndexedSortable`, verify `HeapSort` and `QuickSort` over empty, single-element, duplicate-heavy, already sorted, reverse-sorted, and subrange inputs, assert half-open range behavior, and verify progress callbacks are made by progress-aware overloads.

Host and native loader tests should cover include/exclude file parsing, `refresh()` after file changes, missing or unreadable files, returned set contents, native-library loaded/unloaded states, and `JobConf` round trips for native library usage.

Priority queue tests should cover subclass `lessThan` ordering, `initialize` capacity, `put` overflow behavior, `insert` acceptance/rejection when full, `top`, `pop`, `adjustTop` after mutating the top element, `size`, and `clear`.

Progress and progressable tests should cover tree construction, named and unnamed phases, phase advancement, completion propagation to parents, aggregate progress calculation, status formatting, synchronized access under concurrent updates, and timeout-sensitive code paths invoking `Progressable.progress()`.

Reflection and diagnostics tests should cover `Configurable` and non-`Configurable` objects in `setConf`, constructor/configuration behavior in `newInstance`, typed `getClass`, thread-info printing/logging interval suppression, and contention tracing toggles.

Launcher tests should cover `ProgramDriver.addClass` validation, dispatch to a registered main class, unknown commands, argument slicing, exception propagation, `RunJar.unJar`, manifest main-class lookup, command-line main override, and `PrintJarMainClass` output.

Shell tests should cover command vector construction, environment and working directory propagation, interval gating, stdout parsing, nonzero exit code handling through `ExitCodeException`, process and exit-code getters, `execCommand`, `ShellCommandExecutor` output capture, Windows/non-Windows command branches, and null memory-limit command cases.

String utility tests should cover exception stringification, hostname shortening, human-readable integer boundaries, percentage precision, array joining, byte/hex round trips, URI/path conversion, negative and positive time differences, formatted time-with-diff edge cases, comma-separated parsing, escaped separators, invalid escape sequences, hostname fallback, and startup/shutdown log message content.

Tool and XML tests should cover `ToolRunner.run` with null and non-null configurations, generic option parsing effects, forwarded application args, return code propagation, generic usage printing, and successful/failing XSLT transforms with checked exception propagation.
