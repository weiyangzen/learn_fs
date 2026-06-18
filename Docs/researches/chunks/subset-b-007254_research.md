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
