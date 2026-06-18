# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 6313-12474

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.17.0, not executable implementation source. It starts at the tail of `org.apache.hadoop.dfs.namenode.metrics.NameNodeStatisticsMBean` documentation, then covers complete public API entries for `org.apache.hadoop.filecache.DistributedCache`, most of the old `org.apache.hadoop.fs` package, the KFS and S3 filesystem adapters, filesystem permission value types, `org.apache.hadoop.fs.shell.Count`, and the beginning of `org.apache.hadoop.io`.

The source records API compatibility metadata: packages, classes, interfaces, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadocs. Runtime control flow and private state are not present in the XML, so behavioral notes below are based on the public contracts visible in this chunk.

The chunk is partial at both boundaries. The first lines finish a NameNode metrics MBean entry owned by the previous package, and the last line stops inside the class documentation for `org.apache.hadoop.io.ArrayWritable`; adjacent chunks are needed for complete reports on those partial classes/packages.

## Purpose

The `org.apache.hadoop.filecache` section documents the MapReduce `DistributedCache` API used to localize read-only files, archives, and classpath additions for jobs. It stores cache URIs, timestamps, localized paths, symlink flags, and classpath entries in `Configuration`, then exposes helper methods used by task localization to copy, unpack, link, validate, release, and purge cached resources.

The `org.apache.hadoop.fs` section is the main filesystem API for this Hadoop release. It defines the abstract `FileSystem` contract, core path and stream abstractions, metadata records, local filesystem implementations, checksum wrappers, command-line shell support, trash behavior, disk-usage helpers, and utilities for copying, deleting, linking, chmod, archive extraction, and temporary-file replacement.

The `org.apache.hadoop.fs.kfs` section exposes `KosmosFileSystem`, an adapter that lets Hadoop jobs use the Kosmos filesystem through the standard `FileSystem` API when the configured default filesystem points at a `kfs://` URI.

The `org.apache.hadoop.fs.permission` section defines access-control and Unix-style permission value objects used by filesystem status records and create/mkdir APIs: `AccessControlException`, `FsAction`, `FsPermission`, and `PermissionStatus`.

The `org.apache.hadoop.fs.s3` section documents the original block/inode based S3 filesystem implementation. It models files as metadata inodes plus separately stored blocks, exposes a pluggable `FileSystemStore` interface, and provides an `S3FileSystem` adapter plus migration and exception types.

The `org.apache.hadoop.fs.shell` section adds the `Count` command for reporting directory count, file count, and byte totals.

The visible `org.apache.hadoop.io` portion begins Hadoop Writable collection support: class-ID mapping for heterogeneous map writables, dense array files built on `MapFile`, and the start of `ArrayWritable`.

## Important APIs, Types, and Functions

### DistributedCache

- `DistributedCache.getLocalCache(URI, Configuration, Path, FileStatus, boolean, long, Path)` and the overload without explicit `FileStatus` are the localization entry points. They return the local `Path` for a cached file or the directory created by unpacking an archive. Archives with `.zip` or `.jar` extensions are documented as automatically extracted.
- `releaseCache(URI, Configuration)` decrements or releases use of a localized cache entry after the task is done.
- `makeRelative(URI, Configuration)` derives the local relative path used for cache materialization.
- `getTimestamp(Configuration, URI)` reads the remote modification time so jobs can detect cache changes after submission.
- `createAllSymlink(Configuration, File, File)` and `createSymlink(Configuration)` manage symlink creation in task work directories.
- Cache configuration methods include `setCacheArchives`, `setCacheFiles`, `getCacheArchives`, `getCacheFiles`, `addCacheArchive`, `addCacheFile`, `setArchiveTimestamps`, `setFileTimestamps`, `getArchiveTimestamps`, `getFileTimestamps`, `setLocalArchives`, `setLocalFiles`, `getLocalCacheArchives`, and `getLocalCacheFiles`.
- Classpath integration methods include `addFileToClassPath`, `getFileClassPaths`, `addArchiveToClassPath`, and `getArchiveClassPaths`.
- `getSymlink(Configuration)` checks whether symlink creation is enabled, `checkURIs(URI[], URI[])` validates URI fragments for symlink conflicts, and `purgeCache(Configuration)` deletes the entire backing cache.

### Core Filesystem Records and Streams

- `BlockLocation` is a `Writable`-style block metadata record with hosts, names, offset, length, setters, getters, `write`, `readFields`, and `toString`.
- `ContentSummary` stores length, directory count, and file count, with `Writable` serialization and string rendering.
- `FileStatus` stores length, directory flag, replication, block size, modification time, permissions, owner, group, and path. It supports setters for permission/owner/group, `Writable` serialization, ordering, equality, and hash code based on path identity.
- `FSInputStream` is the abstract seekable input base. It extends normal stream behavior with `seek(long)`, `getPos()`, `seekToNewSource(long)`, and `readFully` overloads.
- `BufferedFSInputStream` wraps an `FSInputStream` with buffering while preserving position, skip, seek, new-source seeking, byte reads, and full reads.
- `FSDataInputStream` wraps an `InputStream` as a `DataInputStream` while exposing `Seekable` and `PositionedReadable` methods when the wrapped stream supports them.
- `FSDataOutputStream` wraps an `OutputStream` as a data output stream, tracks position through `getPos()`, forwards close, and exposes the wrapped stream.
- `FSInputChecker` verifies checksums while reading. It exposes subclass hooks such as `readChunk` and `getChunkPosition`, a `needChecksum` switch, seek/skip/read paths that can throw `ChecksumException`, and `set` for checksum parameters.
- `FSOutputSummer` generates checksums before data is written. Subclasses implement `writeChunk`; callers write one byte, byte arrays, and flush pending checksum/data buffers.
- `ChecksumException` carries a bad-checksum byte position. `FSError` is an `Error` for unexpected native filesystem failures assumed to be disk related.

### FileSystem API and Wrappers

- `FileSystem` is the abstract base for Hadoop filesystems. Static helpers include command-line `parseArgs`, default filesystem lookup and mutation through `getDefaultUri`/`setDefaultUri`, filesystem factory methods `get`, deprecated `getNamed`, local filesystem lookup, `closeAll`, and statistics printing.
- Initialization and identity APIs include `initialize(URI, Configuration)`, `getUri()`, deprecated `getName()`, `makeQualified(Path)`, and `checkPath(Path)`.
- Core operations include `open`, many `create` overloads, `createNewFile`, `rename`, recursive and deprecated non-recursive `delete`, existence/type/length checks, content summaries, list and glob status methods, `mkdirs`, working-directory and home-directory accessors, replication and default block size/replication access, `getFileStatus`, permission and owner setters, and close.
- Local transfer APIs include copy/move from local, copy/move to local, `startLocalOutput`, and `completeLocalOutput`.
- Block locality APIs include deprecated `getFileCacheHints` and replacement `getFileBlockLocations`.
- `FileSystem.Statistics` tracks bytes read and written, with increment methods, getters, and string rendering.
- `FilterFileSystem` wraps another `FileSystem` in field `fs` and delegates identity, path qualification, block locations, open/create, replication, rename/delete, listing, working directory, mkdirs, copy staging, defaults, status, owner/permission, close, and configuration access.
- `ChecksumFileSystem` wraps a raw filesystem and generates/verifies client-side checksum files. Its API exposes the raw filesystem, checksum path and length calculations, bytes-per-checksum, open/create, replication, rename/delete/list/mkdir, local copy behavior with optional CRC copies, output staging, completion, and checksum-failure reporting.
- `LocalFileSystem` is the checksumed local implementation. It converts Hadoop `Path` values to `File`, copies to/from local without unnecessary transfer, and reports checksum failures by moving bad files aside.
- `RawLocalFileSystem` is the direct local `file:` implementation. It exposes `pathToFile`, URI/name initialization, open/create overloads, rename, delete, list, mkdirs, working directory, lock/release, local-output staging, close, status, owner, and permission operations.
- `InMemoryFileSystem` is a `ramfs://` implementation with reservation and checksum registration through `reserveSpaceWithCheckSum`, plus file listing/count and capacity/percent-used accessors.

### Path, Filters, Shell, Trash, and Utilities

- `Path` is the central URI-like path abstraction. Constructors accept string parent/child pairs, `Path` parent/child pairs, raw strings, and scheme/authority/path components. Methods expose `toUri`, filesystem lookup, absolute/name/parent/suffix/depth checks, string rendering, equality, hashing, ordering, and qualification. Public constants are `SEPARATOR`, `SEPARATOR_CHAR`, and `CUR_DIR`.
- `PathFilter.accept(Path)` is the file-status filter contract.
- `PositionedReadable` declares positioned `read` and `readFully` overloads that do not change the current stream offset and are documented as thread-safe.
- `Seekable` declares `seek`, `getPos`, and `seekToNewSource`.
- `FsShell` provides command-line access to a `FileSystem`, including initialization, `run`, `close`, byte-length formatting helpers, current trash lookup, and `main`.
- `Trash` moves files into user trash, creates checkpoints, expunges old checkpoints, returns an emptier `Runnable`, and has a `main` entry point.
- `DF` and `DU` wrap Unix `df` and `du` style disk usage probes. They expose directories, capacity, used/available space, percent used, mount/filesystem strings, command construction, parsing, string rendering, and `main`.
- `ShellCommand` is a deprecated base class for Unix-like shell commands, superseded by `Shell`.
- `LocalDirAllocator` implements round-robin local disk allocation across configured directories. It provides write path selection with known or unknown size, read path lookup, temporary-file creation, context validity checks, and existence checks.
- `FileUtil` provides static conversion of `FileStatus` arrays to `Path` arrays, recursive delete, filesystem-to-filesystem and local copy overloads, `copyMerge`, shell path conversion, local disk usage, unzip, symlink, chmod, temporary-file creation, and atomic-ish replacement.
- `FileUtil.HardLink` provides hardlink creation and link-count retrieval on Unix, Cygwin, and Windows XP.
- `org.apache.hadoop.fs.shell.Count` exposes `matches(String)`, `count(String, Configuration, PrintStream)`, and command metadata fields `NAME`, `USAGE`, and `DESCRIPTION`.

### KFS Adapter

- `KosmosFileSystem` implements the standard `FileSystem` surface for Kosmos/KFS: URI/name initialization, working directory handling, mkdirs, file/directory tests, content length, listing, status, create/open, rename/delete, length/replication/defaults, lock/release, block locations, copy to/from local, and local-output staging.
- The package documentation describes configuration through `fs.default.name` using a `kfs://host:port/` URI and notes that MapReduce job trackers will route file I/O to KFS when configured this way.

### Permission Types

- `AccessControlException` is an `IOException` for access-control failures, with a no-arg constructor needed for unwrapping from `RemoteException` and a message constructor.
- `FsAction` is an enum-like permission action type. Public methods include `values`, `valueOf`, `implies`, `and`, `or`, and `not`; fields include octal `INDEX` and symbolic `SYMBOL`.
- `FsPermission` is a `Writable` for user/group/other `FsAction` triples. It supports construction from actions, a short mode, or another permission; immutable creation; user/group/other getters; `write`, `readFields`, static `read`; conversion to short; equality/hash/string conversion; umask application and configuration getters/setters; defaults; and `valueOf` for Unix symbolic strings such as `-rw-rw-rw-`.
- `PermissionStatus` combines user name, group name, and `FsPermission`. It supports immutable creation, getters, umask application, `Writable` serialization, static read, and string rendering.

### S3 Filesystem

- `Block` stores an S3 block ID and length, with getters and string rendering.
- `INode` stores file metadata: a file type and an array of `Block` pointers. It exposes `getBlocks`, `getFileType`, file/directory tests, serialized-length calculation, `serialize`, static `deserialize`, and fields `FILE_TYPES` and `DIRECTORY_INODE`.
- `FileSystemStore` abstracts S3 persistence for inodes and blocks. It initializes from URI/configuration, reports stored version, stores/retrieves/deletes inodes and blocks, checks existence, lists shallow or deep subpaths, purges everything for tests, and dumps diagnostics.
- `S3FileSystem` is a `FileSystem` backed by a `FileSystemStore`. It exposes URI/name initialization, working directory handling, mkdirs, file tests, listing, create/open, rename, delete, and S3-specific `FileStatus` creation. Permission parameters on create/mkdirs are documented as ignored.
- `MigrationTool` is a `Tool`-style migration command with `main`, `run`, and `initialize`.
- `S3Exception`, `S3FileSystemException`, and `VersionMismatchException` describe S3 communication failures, fatal S3 filesystem failures, and stored-data version mismatches.
- The package documentation explains the persistence design: paths are URL-encoded inode keys, data is stored as `block-*` objects, files point at a list of blocks, seeks use inode block metadata plus HTTP range requests, and renames move only inode metadata through delete-then-put because S3 has no rename.

### Visible IO Types

- `AbstractMapWritable` is a configurable base for `MapWritable` and `SortedMapWritable`. It maps classes to byte IDs and back, supports synchronized class registration and copy from another `Writable`, carries `Configuration`, and serializes/deserializes the class table. The docs state class IDs range from 1 to 127, limiting a map instance to 127 distinct classes.
- `ArrayFile` extends `MapFile` as a dense file-based mapping from long integer positions to values.
- `ArrayFile.Reader` can seek to an index, read the next value, return the current key, and fetch the value at a specific index.
- `ArrayFile.Writer` creates array files for a value class, optionally with `SequenceFile.CompressionType` and `Progressable`, and appends values with synchronized `append`.
- `ArrayWritable` begins in this chunk. Visible constructors accept a value class, a value class plus `Writable[]`, or `String[]`. Visible methods include value-class lookup, string conversion, object-array conversion, set/get, `readFields`, and `write`; its class documentation is truncated by the chunk boundary.

## Control Flow and Behavioral Contracts

The XML itself has no executable control flow. The APIs imply the main flows used by Hadoop 0.17.0 callers.

Distributed cache flow starts when job setup stores cache files, archives, timestamps, localized outputs, symlink preferences, and classpath additions in `Configuration`. Task-side code calls `getLocalCache` with the remote URI, base cache directory, archive flag, expected timestamp, and work directory. The implementation either reuses a valid local copy or copies the file from the configured `FileSystem`, unpacks archives when applicable, and optionally creates symlinks using URI fragments. After task use, callers call `releaseCache`; server or task-tracker reinitialization may call `purgeCache`.

Filesystem resolution flow starts with a `Path` and `Configuration`. `Path.getFileSystem(conf)` or `FileSystem.get(uri, conf)` resolves a concrete filesystem by scheme and authority, calls `initialize`, then operations run through the abstract `FileSystem` contract. `FilterFileSystem`, `ChecksumFileSystem`, `LocalFileSystem`, `RawLocalFileSystem`, `KosmosFileSystem`, and `S3FileSystem` are all implementations or wrappers that preserve this call shape.

Read flow uses `FSDataInputStream` over an `FSInputStream` or other seekable/positioned input stream. Stateful callers use `seek` and normal reads; positional callers use `PositionedReadable.read` or `readFully`, which should not mutate the stream offset. Checksum-aware reads pass through `FSInputChecker`, which reads chunks, verifies checksums, retries or seeks to new sources when supported, and throws `ChecksumException` with a byte position on corruption.

Write flow uses `FileSystem.create` overloads to return `FSDataOutputStream`. Checksum-aware filesystems wrap writes through `FSOutputSummer` and create companion checksum files. Local-output flows call `startLocalOutput` to write to a temporary or local path, then `completeLocalOutput` to move or finalize the result.

Copy and delete flows are helper-driven. `FileUtil.copy` variants move data between filesystems or local disk, optionally deleting sources. `fullyDelete` recursively deletes local directories and may leave partial deletion if it returns false. `copyMerge` concatenates directory children into one output. `replaceFile` moves a source to a target name and throws on failure.

Trash flow wraps delete-like behavior. `Trash.moveToTrash` moves a file or directory under the current user's trash area unless trash is disabled or the item is already in trash. `checkpoint` creates a time-based checkpoint, `expunge` deletes old checkpoints, and `getEmptier` returns a background cleanup runnable.

Permission flow is value-object based. `FsPermission` is constructed from actions, mode shorts, symbolic strings, or existing permissions; `applyUMask` returns a permission with the configured mask applied. `PermissionStatus` carries user/group/permission triples through Writable serialization, and `FileStatus` exposes owner/group/permission for listed files.

S3 flow is metadata-first. `S3FileSystem` reads an inode for a path to determine whether it is a file or directory and, for files, which `Block` objects contain the data. Opens compute block offsets and use range reads against the store. Creates write new block objects and then store inode metadata. Renames are implemented as inode delete/put because S3 lacks native rename.

Writable flow follows Hadoop's `write(DataOutput)` and `readFields(DataInput)` convention. `AbstractMapWritable` serializes class-ID mappings before subclasses serialize entries; `ArrayFile` stores dense numeric keys through `MapFile`; `ArrayWritable` serializes a homogeneous array of `Writable` values.

## State, Persistence, and Side Effects

The JDiff XML is persistent API metadata used for compatibility comparison. Runtime state described by this chunk belongs to Hadoop APIs and their implementations.

`DistributedCache` stores most job-facing state in `Configuration`: cache archives, cache files, timestamps, localized file/archive paths, classpath additions, and symlink enablement. It also creates persistent local cache entries under task-tracker cache directories, unpacks archives into local directories, creates symlinks in task work directories, maintains reference/release state, and can delete all backing cache files through `purgeCache`.

`FileSystem` implementations persist data to their backing stores: HDFS-like stores, local disk, KFS, S3, in-memory storage, or wrapper-managed checksum files. Operations in this chunk can create, overwrite, rename, delete, recursively delete, list, chmod, chown, change replication, set owner/group, make directories, copy to/from local, create symlinks/hardlinks, extract archives, and move files to trash.

`ChecksumFileSystem` and `LocalFileSystem` persist companion checksum files and may move corrupt local files into a bad-file area when checksum failure is reported. `FSInputChecker` and `FSOutputSummer` hold process-local checksum state for the current stream buffer/chunk.

`FileSystem.Statistics` is process-local mutable telemetry with bytes-read and bytes-written counters. It is exposed both per filesystem and through static printing; changes affect diagnostics rather than file contents.

`Path`, `BlockLocation`, `ContentSummary`, `FileStatus`, `FsPermission`, `PermissionStatus`, `Block`, `INode`, `AbstractMapWritable`, `ArrayFile`, and `ArrayWritable` are durable or transport-facing value types. Their `Writable` formats, equality, ordering, and string forms are compatibility-sensitive because they may appear in RPC, file metadata, sequence/map files, and configuration-driven behavior.

`Trash` persists deleted user data by moving it under a trash directory and creating/deleting checkpoint directories. Misconfiguration can turn delete operations into permanent removal or unbounded trash accumulation.

`RawLocalFileSystem`, `DF`, `DU`, `FileUtil`, `FileUtil.HardLink`, and `ShellCommand` depend on host filesystem and shell behavior. Their side effects include local file creation/deletion, permission/owner changes, temp files, hardlinks, symlinks, archive extraction, and platform command execution.

`S3FileSystem` persists inodes and blocks as S3 objects. The package documentation makes clear that directory and file names use leading-slash inode keys while data blocks use `block-` keys. Rename is not atomic in the same way as local/HDFS rename because it is represented by delete plus put.

## Dependencies and Integration Points

This chunk depends heavily on Java platform types: `URI`, `File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `PrintStream`, arrays, collections, `Checksum`, `IOException`, and shell/platform commands for disk usage, symlink, chmod, chown, and hardlink behavior.

Key Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configurable` for filesystem resolution, distributed-cache metadata, local-directory allocation, permissions/umask, KFS/S3 initialization, and Writable configuration propagation.
- `org.apache.hadoop.fs.FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `ContentSummary`, `FSDataInputStream`, `FSDataOutputStream`, `PathFilter`, `Seekable`, and `PositionedReadable` as the central filesystem contract.
- `org.apache.hadoop.fs.permission.FsPermission`, `FsAction`, `PermissionStatus`, and `AccessControlException` for authorization metadata.
- `org.apache.hadoop.io.Writable`, `WritableComparable`-style serialization conventions, `MapFile`, `SequenceFile.CompressionType`, and `ArrayWritable` for persistent binary formats.
- `org.apache.hadoop.util.Progressable` and `Tool`-style command execution for streaming progress and migration/shell commands.
- MapReduce job configuration and `JobClient` integration for `DistributedCache`.
- KFS configuration through `fs.default.name=kfs://host:port/`.
- S3 store backends through the `FileSystemStore` abstraction and S3 object layout/version metadata.
- Apache Commons Logging appears via public `LOG` fields on filesystem/checksum classes.

## Risks and Compatibility Notes

- This is generated API metadata, not implementation source. It cannot prove private state handling, lock ordering, exact path normalization, retry loops, or byte-level serialization details beyond the visible signatures and Javadocs.
- The chunk starts and ends inside larger API contexts. Whole-file reports should merge adjacent chunks before making complete claims about `NameNodeStatisticsMBean` or `ArrayWritable`.
- `DistributedCache` uses URI fragments for symlink names. Missing fragments, duplicate fragments, or conflicts between file and archive fragments can create broken links or task-local name collisions.
- `DistributedCache` relies on remote modification timestamps captured at job submission. Clock skew, stores with weak mtime semantics, or changed files with unchanged timestamps can lead to stale or inconsistent localized resources.
- `purgeCache` is explicitly destructive and can delete backing cache files used by jobs if called outside reinitialization.
- `FileSystem.create` has many overloads with overwrite, permission, buffer size, replication, block size, and progress variants. Compatibility depends on all overloads preserving consistent defaults.
- Deprecated APIs such as `getName`, `getNamed`, `delete(Path)`, `isDirectory`, `getLength`, `getContentLength`, `getBlockSize`, `getFileCacheHints`, and `ShellCommand` remain visible and can still be used by old callers.
- Positioned reads must not disturb stream offset and are documented as thread-safe. Implementations that share mutable seek state can corrupt concurrent readers.
- `readFully` and checksum reads must handle short reads, EOF, retries, and checksum exceptions precisely; silent partial reads can corrupt higher-level record readers.
- `ChecksumFileSystem` must keep data files and checksum files synchronized across create, rename, delete, copy, and local-output completion. Orphaned or stale checksum files are a common risk.
- Local filesystem behavior is platform-sensitive. Shell commands, symlink/hardlink support, permission bits, owner/group lookup, Windows path syntax, and disk-usage parsing can all vary by OS.
- `FileUtil.copy` and `fullyDelete` are not atomic. Failures can leave partial destination trees, partially deleted sources, or mixed merged output.
- `LocalDirAllocator` depends on configured local directories and free-space estimates. Stale context state, failed disks, or unknown write sizes can select unsuitable paths.
- `Trash` is configuration-sensitive. Disabled trash, files already in trash, checkpoint naming, and expunge interval mistakes can cause immediate data loss or excessive retained data.
- `FsPermission` has multiple representations: action triples, short modes, symbolic strings, umask-adjusted permissions, and Writable bytes. Conversion bugs can become security bugs.
- `FileStatus` equality and ordering are path-centered. Callers comparing metadata changes must not assume equality includes length, owner, permission, or modification time.
- KFS integration can only be correct when the default filesystem URI and KFS client/native dependencies are available. Missing KFS libraries or invalid authority values will break normal Hadoop file I/O.
- S3 in this release uses an inode/block layout, not a simple object-per-file layout. Store version mismatches, orphaned blocks, eventual consistency, delete-then-put rename, and range-read failures can affect correctness.
- `S3FileSystem` documents ignored permission parameters, so code expecting HDFS-like permission enforcement on create/mkdirs will not get it.
- `FileSystemStore.purge` is test-oriented and destructive; accidental use against production buckets would remove all inodes and blocks known to the store.
- `AbstractMapWritable` has only 127 class IDs per map instance. Complex nested maps with many distinct Writable classes can exceed the documented range.
- `ArrayFile` depends on monotonically dense integer keys generated by the writer. Manual corruption or out-of-order writes would break reader seek/key assumptions.

## Test Signals

Useful validation for this API surface should include:

- JDiff compatibility checks that the XML remains well formed and preserves package/class/interface boundaries, public/protected signatures, declared exceptions, visibility, static/final/abstract/synchronized flags, field names, deprecation markers, and documentation-bearing entries in lines 6313-12474.
- Distributed cache tests for cache file/archive configuration round trips, timestamp capture, localization reuse, archive extraction for `.jar` and `.zip`, symlink creation from URI fragments, duplicate fragment rejection through `checkURIs`, classpath additions, release semantics, and destructive purge behavior in an isolated cache directory.
- `FileSystem` contract tests for default URI resolution, `get(URI, conf)` initialization, path qualification, create overload defaults, overwrite handling, mkdir permissions, open/read/write/close, rename/delete semantics, list and glob status, content summaries, local copy/move methods, replication/default block size, owner/permission setters, and statistics counters.
- Stream tests for `FSInputStream`, `BufferedFSInputStream`, `FSDataInputStream`, `FSInputChecker`, `FSOutputSummer`, and `FSDataOutputStream`: seek/getPos consistency, positioned reads not changing offset, `readFully` short-read loops, EOF behavior, checksum failure position reporting, retry/new-source paths, output position tracking, close propagation, and checksum chunk boundaries.
- `ChecksumFileSystem` and `LocalFileSystem` tests for checksum-file naming and length calculation, create/open verification, rename/delete/list filtering of checksum files, local copy with and without CRC files, checksum failure quarantine, raw filesystem access, and local-output staging.
- `RawLocalFileSystem` tests for path-to-file conversion, URI/name behavior, create/open/delete/rename/list/mkdirs/status, recursive delete flags, working directory, home directory, lock/release, owner/permission shell command paths, and platform-specific symlink/hardlink behavior.
- `Path` tests for every constructor form, URI conversion, relative and absolute paths, final component, parent at root, suffix, depth, qualification, equality, hashing, ordering, separator constants, and filesystem lookup from configuration.
- `FileUtil` tests for `stat2Paths`, recursive delete partial failures, filesystem-to-filesystem copy, local copy, `copyMerge`, shell path conversion on Unix and Windows, disk usage, unzip, symlink return codes, chmod return codes, temp-file creation, replace-file failure cleanup, and hardlink/link-count behavior.
- `DF` and `DU` tests with mocked command output for Linux, FreeBSD, and Cygwin formats, plus refresh interval behavior and parsing failure paths.
- `LocalDirAllocator` tests for round-robin directory selection, known-size and unknown-size writes, read path lookup across all directories, missing file handling, temporary-file creation, invalid context detection, and failed/full disk fallback.
- `Trash` tests for disabled trash, already-in-trash return false, move-to-trash success, checkpoint creation, expunge of old checkpoints, emptier runnable behavior, and CLI `main` paths.
- Permission tests for `FsAction` implication/algebra, `FsPermission` action and short constructors, immutable creation, symbolic `valueOf`, umask application, configuration-backed umask getters/setters, Writable round trips, equality/hash/string output, and `PermissionStatus` serialization.
- KFS adapter tests, when KFS dependencies are available, for initialization from `kfs://` URI, working directory, mkdirs, create/open, rename/delete, status/listing, content length, block locations, replication defaults, local copy staging, and lock/release behavior.
- S3 filesystem tests with a controlled `FileSystemStore` fake for inode/block storage, version mismatch, file and directory status, create/open with multi-block files, range-like seek behavior, rename as inode move, recursive and non-recursive delete, ignored permission arguments, list shallow/deep paths, purge/dump diagnostics, and orphan-block cleanup expectations.
- `fs.shell.Count` tests for command matching, output formatting, and accurate directory/file/byte counts through a test filesystem.
- `AbstractMapWritable` tests for class registration, ID lookup, ID limit behavior, copy constructor support, configuration propagation, serialization of class tables, and nested map compatibility.
- `ArrayFile.Reader` and `ArrayFile.Writer` tests for dense append, seek by index, current key tracking, next value reads, random get, compression/progress constructor behavior, and interoperability with `MapFile`.
- `ArrayWritable` tests for value-class preservation, string-array construction, set/get, `toStrings`, `toArray`, empty arrays, mixed-class rejection or behavior, and Writable round trips. Adjacent chunk coverage is needed to finish its full documentation review.
