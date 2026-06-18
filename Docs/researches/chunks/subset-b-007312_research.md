# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.0.xml lines 6170-12398

## Scope

This chunk is a JDiff/API XML slice for Hadoop 0.20.0. It starts in the tail of `org.apache.hadoop.fs.RawLocalFileSystem`, continues through seek/sync/trash filesystem interfaces, FTP/KFS/S3/native-S3 filesystem adapters, filesystem permission metadata, shell command helpers, the embedded HTTP server API, and the first large portion of `org.apache.hadoop.io`. It ends inside `org.apache.hadoop.io.SequenceFile.Reader`, immediately after the beginning of the second `getCurrentValue` overload.

The source is generated API metadata, not Java implementation. The research surface is therefore the public/protected compatibility contract: package boundaries, classes and interfaces, inheritance, implemented interfaces, constructors, methods, parameters, return types, declared exceptions, fields, visibility/static/final/synchronized/abstract flags, deprecation markers, and embedded Javadocs.

## Purpose

The filesystem section documents Hadoop's local and remote filesystem compatibility surface. The tail of `RawLocalFileSystem` exposes local create, rename, delete, list, mkdir, working-directory, local-output, ownership, permission, and status operations. `Seekable` and `Syncable` define the stream-positioning and durable flush capabilities expected by Hadoop streams. `Trash` defines the user-visible deletion safety model that moves paths into a per-user `.Trash` hierarchy, creates checkpoints, expunges old checkpoints, and provides a superuser emptier runnable.

The `org.apache.hadoop.fs.ftp`, `org.apache.hadoop.fs.kfs`, `org.apache.hadoop.fs.s3`, and `org.apache.hadoop.fs.s3native` packages expose alternative `FileSystem` implementations and their supporting exceptions, stores, credentials, metadata, and stream types. These APIs let Hadoop treat FTP, Kosmos File System, block-based S3, and native object-based S3 as filesystem backends through the common `FileSystem`, `Path`, `FileStatus`, and stream abstractions.

The `org.apache.hadoop.fs.permission` package captures Hadoop's Unix-like permission model: access-control exceptions, read/write/execute action sets, packed permission bits, umask behavior, and owner/group/permission triplets that can be serialized with filesystem metadata.

The `org.apache.hadoop.fs.shell` package defines the old shell command helper surface for command parsing and `-count`. The `org.apache.hadoop.http` package defines a Jetty-backed status server, servlet/filter registration, default application setup, SSL listener registration, and a stack servlet for operational diagnostics.

The `org.apache.hadoop.io` portion starts Hadoop's serialization and indexed-file API surface. It covers writable class-id maps, array and map writables, primitive writable key/value types, byte buffers, compressed/lazy writables, stringification through configuration, optimized raw comparators, MapFile/BloomMapFile indexed SequenceFile wrappers, polymorphic `ObjectWritable`, in-memory input/output buffers, raw byte comparators, and the beginning of `SequenceFile` creation/reader metadata APIs.

## Important APIs, Types, and Functions

### Filesystem Core, FTP, and KFS

- `RawLocalFileSystem` tail includes public create overloads, `rename`, `delete(Path)` and `delete(Path, boolean)`, `listStatus`, `mkdirs` with and without `FsPermission`, `getHomeDirectory`, working-directory get/set, local-output staging hooks, `close`, `toString`, `getFileStatus`, `setOwner`, and `setPermission`.
- `Seekable` declares `seek(long)`, `getPos()`, and `seekToNewSource(long)`, defining the contract for repositionable streams and alternate replica/source selection.
- `Syncable` declares `sync()`, the durable-buffer flush operation used by output streams that can force buffered data to underlying devices.
- `Trash` extends `Configured` and can be constructed from `Configuration` or an explicit `FileSystem`. It exposes `moveToTrash(Path)`, `checkpoint()`, `expunge()`, `getEmptier()`, and `main(String[])`.
- `FTPException` wraps failures as a runtime exception. `FTPFileSystem` extends `FileSystem`, implements URI initialization, open/create/delete/list/status/mkdir/rename/working-directory operations, declares `LOG`, `DEFAULT_BUFFER_SIZE`, and `DEFAULT_BLOCK_SIZE`, and marks the old one-argument `delete(Path)` deprecated in favor of `delete(Path, boolean)`.
- `FTPInputStream` wraps an `InputStream`, `FTPClient`, and filesystem statistics; it tracks `getPos()`, rejects or implements seek semantics via `seek`/`seekToNewSource`, delegates `read` overloads, closes the FTP client path, and disables mark/reset behavior.
- `KosmosFileSystem` extends `FileSystem` for KFS. Its API includes URI/name initialization, working directory, `mkdirs`, `isDirectory`, `isFile`, list/status calls, unsupported append, create/open, rename/delete, length/replication/default block size APIs, lock/release, block-location lookup, local copy hooks, and local-output staging.

### Permissions and S3 Filesystems

- `AccessControlException` in `org.apache.hadoop.fs.permission` is deprecated in favor of `org.apache.hadoop.security.AccessControlException`, but remains public for compatibility and remote exception unwrapping.
- `FsAction` is an enum-like bit/action model with `NONE`, `EXECUTE`, `WRITE`, `WRITE_EXECUTE`, `READ`, `READ_EXECUTE`, `READ_WRITE`, `ALL`, and `SYMBOL`. It supports `implies`, `and`, `or`, and `not`.
- `FsPermission` implements writable permission bits. It has constructors from user/group/other `FsAction`, short mode, and copy; immutable construction; accessors; `fromShort`, `toShort`, `write`, `readFields`, static `read`; equality/hash/string conversion; `applyUMask`; static `getUMask`, `setUMask`, `getDefault`, and `valueOf`; plus `UMASK_LABEL` and `DEFAULT_UMASK`.
- `PermissionStatus` carries user name, group name, and `FsPermission`; supports immutable construction, accessors, umask application, `readFields`, `write`, static `read`, static component-wise `write`, and `toString`.
- `Block` stores S3 block id and length. `FileSystemStore` defines the old block-based S3 backing-store contract: initialize, version lookup, store/retrieve/delete inodes and blocks, existence checks, shallow/deep path listing, purge for tests, and diagnostic dump.
- `INode` records S3 file metadata as a file type plus block list. It exposes `getBlocks`, `getFileType`, `isDirectory`, `isFile`, serialized length, `serialize`, static `deserialize`, `FILE_TYPES`, and `DIRECTORY_INODE`.
- `MigrationTool` implements a command-line/tool path to migrate old S3 data layouts; `S3Credentials` loads and exposes access and secret keys; `S3Exception`, `S3FileSystemException`, and `VersionMismatchException` surface S3 communication, filesystem, and stored-version failures.
- `S3FileSystem` extends `FileSystem` over a `FileSystemStore`, with constructors for default or injected store, URI/name initialization, working directory, mkdirs, `isFile`, list, unsupported append, create/open, rename/delete, and `getFileStatus`.
- `NativeS3FileSystem` extends `FileSystem` over a `NativeFileSystemStore`, exposing initialization, unsupported append, create/delete/status/URI/list/mkdir/open/rename/working-directory operations and `LOG`.

### Shell and HTTP

- `Command` is the abstract shell command base with a `Configuration` constructor, `getCommandName`, `run(Path)`, `runAll()`, and protected/public argument state.
- `CommandFormat` parses command arguments with min/max arity and option names; `parse(List, int)` mutates/returns positional parameters and `getOpt(String)` checks parsed options.
- `Count` implements the `-count` shell command, with `matches`, `getCommandName`, `run(Path)`, and public `NAME`, `USAGE`, and `DESCRIPTION`.
- `FilterContainer` abstracts servlet filter registration through `addFilter` and `addGlobalFilter`. `FilterInitializer` defines `initFilter(FilterContainer, Configuration)`.
- `HttpServer` is the Jetty-backed status server. Constructors bind name, address, port, find-port behavior, and optional configuration. It exposes listener creation, default apps/servlets, context registration, attributes, servlet/internal-servlet registration, filter/global-filter registration, lower-level filter definition/path mapping, attribute lookup, webapps path lookup, port/threads, SSL listener registration overloads, start/stop/join, and protected/public Jetty fields (`webServer`, `listener`, `webAppContext`, `defaultContexts`, `filterNames`) plus `LOG`.
- `HttpServer.StackServlet` is a servlet with `doGet` for stack/diagnostic output.

### Writable Containers, Buffers, and Primitive Types

- `AbstractMapWritable` implements the class-to-byte-id mapping behind writable maps. It supports class registration with `addToMap`, class/id lookup, map copying, `Configurable` get/set, and map serialization/deserialization.
- `ArrayFile`, `ArrayFile.Reader`, and `ArrayFile.Writer` provide dense long-indexed files over `SequenceFile`. The reader supports `seek(long)`, sequential `next(Writable)`, current numeric `key()`, and random `get(long, Writable)`. The writer appends values under implicit long keys and has constructors with optional compression/progress.
- `ArrayWritable` wraps arrays of a single writable value class, including a `String[]` convenience constructor. It exposes value class, string conversion, Java-array conversion, set/get, and writable read/write.
- `BinaryComparable` provides byte-array based equality/comparison primitives for subclasses, including length/data access and raw byte comparison.
- `BooleanWritable`, `ByteWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, and `DoubleWritable` are `WritableComparable` wrappers with default/value constructors, `set`, `get`, `readFields`, `write`, equality, hash, compare, string conversion, and optimized nested comparators. `LongWritable.DecreasingComparator` reverses long ordering for descending sort keys.
- `BytesWritable` models mutable byte sequences with logical length and backing capacity. It has byte-array constructors, `getBytes`, deprecated `get`, `getLength`, deprecated `getSize`, `setSize`, `getCapacity`, `setCapacity`, full-array and range `set`, writable read/write, equality/hash, hex string rendering, and a raw comparator.
- `Closeable` is a deprecated Hadoop-local interface replaced by `java.io.Closeable`.
- `CompressedWritable` is a lazy compressed writable base. Subclasses implement `readFieldsCompressed` and `writeCompressed`; callers must call `ensureInflated()` before field access.
- `DataInputBuffer` and `InputBuffer` are reusable in-memory readers. They can reset to a byte buffer/range and expose data position and length. `DataInputBuffer` implements `DataInput`; `InputBuffer` is an `InputStream`.
- `DataOutputBuffer` and `OutputBuffer` are reusable in-memory writers. They expose backing data, valid length, reset, and direct write from `DataInput`/`InputStream`; `DataOutputBuffer` can write to an `OutputStream`.
- `DefaultStringifier<T>` bridges configured serialization to strings. It implements `Stringifier` with `fromString`, `toString`, `close`, and static `store`, `load`, `storeArray`, and `loadArray` helpers for persisting serialized objects in `Configuration`.
- `GenericWritable` wraps one of a subclass-declared set of writable classes. It exposes `set`, `get`, `toString`, `readFields`, `write`, abstract `getTypes`, and `Configurable` accessors.
- `IOUtils` provides stream utility APIs: `copyBytes` overloads with configurable buffer/close behavior, exact `readFully`, exact `skipFully`, cleanup that ignores IOExceptions, close-stream, and close-socket helpers. `IOUtils.NullOutputStream` discards written bytes.

### Indexed Files, Map Writables, Hashes, ObjectWritable, and SequenceFile

- `BloomMapFile`, `BloomMapFile.Reader`, and `BloomMapFile.Writer` extend MapFile behavior with a Bloom filter. The reader supports probabilistic membership (`probablyHasKey`), faster `get`, and `getBloomFilter`; the writer appends key/value pairs and closes while maintaining the filter.
- `MapFile` is a sorted, indexed, directory-backed map built on SequenceFile data and index files. It exposes static `rename`, `delete`, `fix`, `main`, and field names `INDEX_FILE_NAME` and `DATA_FILE_NAME`.
- `MapFile.Reader` supports constructors with optional custom comparator/lazy opening, key/value class lookup, protected `open`, specialized data-file reader creation, `reset`, approximate `midKey`, `finalKey`, `seek`, sequential `next`, exact `get`, `getClosest` overloads, and `close`.
- `MapFile.Writer` supports many constructor combinations for key/value classes, comparators, compression type, codec, and progress. It exposes static/configured index interval getters/setters, `close`, and sorted `append`, whose docs require appended keys to be greater than or equal to the previous key.
- `MapWritable` extends the abstract map machinery and implements a writable map-like API: default/copy constructors, `clear`, `containsKey`, `containsValue`, `entrySet`, `get`, `isEmpty`, `keySet`, `put`, `putAll`, `remove`, `size`, `values`, `write`, and `readFields`.
- `MD5Hash` is a fixed-size writable comparable digest with constructors from empty, hex string, or byte array. It supports static `read`, serialization, copying, digest access, static digest creation from byte arrays, strings, and streams, `halfDigest`, `quarterDigest`, equality/hash/order/string conversion, `setDigest`, `MD5_LEN`, and a raw comparator.
- `MultipleIOException` aggregates a list of IOExceptions and exposes `getExceptions` and static `createIOException(List)`.
- `NullWritable` is a singleton zero-data writable comparable, with `get`, no-op read/write, stable comparison/equality/hash/string behavior, and a raw comparator.
- `ObjectWritable` is the polymorphic serialization wrapper for Writables, strings, primitive types, and arrays of those. It exposes empty/object/declared-class constructors, `get`, `getDeclaredClass`, `set`, `toString`, read/write, static `writeObject`, static `readObject` overloads, and `Configurable` accessors.
- `RawComparator<T>` extends `Comparator<T>` with byte-range `compare(byte[], int, int, byte[], int, int)`, allowing sort/group paths to compare serialized keys without object construction.
- `SequenceFile` exposes deprecated job-level `getCompressionType(Configuration)` and `setCompressionType(Configuration, CompressionType)` in favor of MapReduce output format or writer-level configuration. It has many static `createWriter` overloads for filesystem/path or raw `FSDataOutputStream`, key/value classes, buffer size, replication, block size, compression type, codec, progress, and metadata. `SYNC_INTERVAL` declares sync marker spacing.
- `SequenceFile.CompressionType` has `NONE`, `RECORD`, and `BLOCK`, with record compression applying to values and block compression grouping key/value blocks.
- `SequenceFile.Metadata` is a writable `TreeMap<Text,Text>` of file attributes, with constructors, `get`, `set`, `getMetadata`, write/read, equality/hash, and string conversion.
- The visible start of `SequenceFile.Reader` includes construction from `FileSystem`, `Path`, and `Configuration`; protected `openFile`; synchronized `close`; key/value class-name and class accessors; compression and block-compression queries; compression codec and metadata accessors; synchronized `getCurrentValue(Writable)`; and the start of an object-returning `getCurrentValue` overload.

## Control Flow

Filesystem control flow is mediated through `FileSystem` subclasses. Callers initialize each filesystem with a URI and `Configuration`, then use common methods such as `open`, `create`, `rename`, `delete`, `listStatus`, `getFileStatus`, `mkdirs`, and working-directory access. Optional operations such as append are explicitly present but documented as unsupported on FTP, KFS, S3, and native S3 in this chunk, so callers must handle `IOException` or unsupported-operation behavior.

Stream control flow is split by capability interfaces. Code that receives an input stream can check/use `Seekable` to reposition reads or request an alternate source at a target offset. Code that receives an output stream can check/use `Syncable` to force buffers to underlying devices. `FTPInputStream` adds a concrete remote-stream lifecycle: read from the wrapped input stream, track position/statistics, and close the associated FTP client session.

Trash control flow moves a path into the user's `.Trash/current` tree while preserving the original path under that directory. Periodic maintenance checkpoints the current trash area, expunges old checkpoints, and the superuser emptier returned by `getEmptier()` can perform this across users. The design deliberately avoids enumerating full trash contents for normal deletes.

Permission control flow composes three `FsAction` values into an `FsPermission`, applies umasks to derive creation permissions, and persists permissions either alone or with owner/group through `PermissionStatus`. `FsPermission.valueOf` supports Unix symbolic permission parsing, while `toShort` and `fromShort` are the compact binary form.

Block-based S3 control flow uses `S3FileSystem` plus `FileSystemStore`: path metadata is represented as an `INode`, file data is split into `Block` objects, and the store persists/retrieves/deletes those objects. Native S3 control flow presents a `FileSystem` facade over object-store semantics instead of the old inode/block store. Both expose the same Hadoop `FileSystem` operations to higher layers.

Shell command flow constructs a `Command`, parses arguments with `CommandFormat`, then invokes `runAll()` to apply command-specific `run(Path)` behavior to every source path. `Count` plugs into that pattern for directory/file/byte/quota reporting.

HTTP server control flow constructs `HttpServer`, registers default applications, servlets, filters, attributes, and contexts, optionally adds SSL listeners, then starts/stops/joins the Jetty server. Filter registration flows through `FilterContainer` and `FilterInitializer`, allowing components to contribute servlet filters from configuration.

Writable control flow is DataInput/DataOutput based. Primitive wrappers and container types serialize their internal fields in `write` and restore them in `readFields`; object reuse during deserialization is expected in Hadoop APIs. `ArrayWritable`, `MapWritable`, `GenericWritable`, and `ObjectWritable` add type metadata so heterogeneous or parameterized values can be reconstructed.

Raw comparator control flow avoids object materialization. Primitive writable comparators, `BytesWritable.Comparator`, `MD5Hash.Comparator`, `NullWritable.Comparator`, and `RawComparator` compare byte slices that represent serialized keys. This path is central to MapReduce sorting and grouping.

MapFile control flow writes sorted key/value records to a data file and periodically records index entries. Readers load or consult the index to seek near requested keys, then scan data records to return exact or closest matches. `BloomMapFile` adds a Bloom filter check before expensive map lookups.

SequenceFile writer creation flow chooses the writer implementation from key/value classes plus `CompressionType`, optional codec, progress callback, file creation parameters, and metadata. Reader flow begins by opening an `FSDataInputStream`, reading header metadata such as key/value class names and compression settings, then providing accessors and current-value retrieval as records are read; later reader iteration methods are outside this chunk.

## State and Persistence Behavior

This XML file persists the Hadoop 0.20.0 API surface for compatibility comparison. It has no runtime state itself, but the APIs in this chunk define several durable formats and process-local state contracts.

`RawLocalFileSystem`, FTP, KFS, S3, native S3, and MapFile/SequenceFile APIs persist data through `FileSystem`, `Path`, `FileStatus`, and Hadoop stream abstractions. Rename/delete/list/status semantics differ by backend, especially for object stores and FTP, so compatibility depends on both method signatures and documented unsupported operations.

`Trash` persists deleted paths under `.Trash/current` and checkpoint directories in the user's home directory. Its behavior depends on filesystem paths, current user, configured trash interval, and checkpoint/expunge timing.

`FsPermission` stores permission state as user/group/other actions encoded into a short, plus static/default umask configuration. `PermissionStatus` persists owner, group, and permission together through Writable serialization. Changing the short encoding, symbolic parsing, default umask key, or owner/group serialization would break persisted metadata.

The old S3 implementation persists an explicit namespace: `INode` objects identify directories or files, and file `INode`s reference block IDs and block lengths. `FileSystemStore.getVersion()` and `VersionMismatchException` are compatibility gates for stored data layout. `MigrationTool` exists because persisted S3 layouts can change and need conversion.

Writable types persist binary formats through `DataInput`/`DataOutput`. Primitive writables use fixed primitive encodings; `BytesWritable` persists logical length plus bytes; `ArrayWritable`, `MapWritable`, `GenericWritable`, and `ObjectWritable` persist class/type metadata; `MD5Hash` persists a fixed digest length; `NullWritable` intentionally persists no data.

Several buffer APIs expose backing arrays plus valid lengths. `BytesWritable.getBytes`, `DataInputBuffer.getData`, `DataOutputBuffer.getData`, and `OutputBuffer.getData` can return arrays larger than the valid logical content. Callers must use `getLength`, `getPosition`, or logical writable length rather than array capacity.

`CompressedWritable` persists a compressed representation and delays inflation until fields are accessed. Subclasses must implement compressed read/write hooks consistently, and callers of subclass methods must ensure inflation before reading decompressed fields.

`DefaultStringifier` persists serialized objects into `Configuration` string keys. The stored data is only meaningful if the same configured serialization implementation and target class are available when loading.

`AbstractMapWritable` and `MapWritable` persist class-to-id mappings so maps with arbitrary writable key/value classes can be deserialized. This mapping is part of the wire format and must remain synchronized with the serialized entries.

`MapFile` persists a directory containing a data `SequenceFile` and an index file named by `DATA_FILE_NAME` and `INDEX_FILE_NAME`. The writer's index interval affects lookup speed and index size. `MapFile.fix` rebuilds an index for a corrupt or missing index, indicating that data and index can diverge.

`BloomMapFile` persists or maintains an additional Bloom filter alongside map data. False positives are expected from the membership check, but false negatives would make valid keys unreachable through optimized reads.

`SequenceFile` persists a flat binary key/value file with a header containing magic/version, key/value class names, compression flags, optional codec class, metadata, and sync marker. Record-compressed and block-compressed formats differ materially, and `SYNC_INTERVAL` controls sync marker spacing. `SequenceFile.Metadata` persists a `Text`-to-`Text` attribute map in the file header.

## Dependencies and Integration Points

- Java dependencies include `java.io` streams and data input/output types, `IOException`, `RuntimeException`, collections (`List`, `Set`, `Map`, `TreeMap`, `Collection`), `Comparator`, `Enum`, sockets, and servlet types.
- Hadoop configuration (`Configuration`, `Configured`, `Configurable`) drives filesystem initialization, `Trash`, S3 credentials, HTTP server setup, stringifier serialization, generic/object writable configuration, SequenceFile compression defaults, and MapFile writer configuration.
- Hadoop filesystem abstractions (`FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `FSDataInputStream`, `FSDataOutputStream`, `FileSystem.Statistics`) are the central integration surface for RawLocal, FTP, KFS, S3, native S3, MapFile, ArrayFile, and SequenceFile.
- Hadoop permission APIs integrate with filesystem create/status operations through `FsPermission` and `PermissionStatus`; `RawLocalFileSystem`, FTP/KFS/S3 filesystems, and higher layers pass permission arguments even when some backends document that they ignore them.
- FTP integration depends on Apache Commons Net `FTPClient` and Apache Commons Logging for FTP filesystem logging.
- HTTP integration depends on Jetty (`org.mortbay.jetty.Server`, `Connector`, `WebAppContext`) and servlet filters/servlets. `HttpServer` provides daemon web UI/status plumbing used by Hadoop services.
- S3 integration depends on AWS-style credentials and Hadoop's old block-store abstraction (`FileSystemStore`) or native object-store abstraction (`NativeFileSystemStore`).
- KFS integration depends on the Kosmos File System client layer behind `KosmosFileSystem`, while exposing Hadoop's generic filesystem contract.
- Hadoop IO integration depends on `Writable`, `WritableComparable`, `WritableComparator`, `RawComparator`, `Stringifier`, serialization facilities, `Progressable`, compression codecs, and utility classes such as Bloom filters.
- MapReduce integration appears through SequenceFile deprecations that point callers to `org.apache.hadoop.mapred.SequenceFileOutputFormat` for job-output compression settings and through `Progressable` callbacks used during file creation.

## Risks and Edge Cases

- The chunk starts inside `RawLocalFileSystem` and ends inside `SequenceFile.Reader`; adjacent chunks are required for complete coverage of those classes.
- JDiff metadata omits method bodies. Exact rename/delete semantics, exception behavior, S3 serialization layout, FTP connection handling, MapFile index writing, Bloom filter persistence, and SequenceFile reader iteration require implementation-source review.
- Several public methods are deprecated but remain part of the 0.20.0 compatibility contract: permission `AccessControlException`, FTP one-argument delete, Hadoop-local `Closeable`, and job-level SequenceFile compression getters/setters.
- Optional operations such as append are present on multiple filesystems but documented as unsupported. Generic callers that assume append works for every `FileSystem` will fail on FTP, KFS, S3, and native S3.
- Object-store backends cannot always provide POSIX-like atomic rename, directory, permission, or listing semantics. Tests must account for S3 and native S3 behavior separately from local/HDFS-style filesystems.
- Permission behavior has two pitfalls: some filesystem implementations ignore `FsPermission` parameters, and default/umask state comes from configuration/static helpers. Cross-filesystem tests should pin both effective permissions and ignored-permission cases.
- Backing-array exposure in `BytesWritable` and buffer classes can leak stale bytes if callers serialize or compare capacity rather than logical length.
- Raw comparators must agree with object-level `compareTo`. Any divergence in primitive writable comparators, `BytesWritable.Comparator`, `MD5Hash.Comparator`, MapFile comparator usage, or SequenceFile sort keys can corrupt MapReduce sort/group behavior.
- `MapFile.Writer.append` requires nondecreasing keys. Violating sorted order can make indexed lookups, closest-key searches, and mid/final key behavior incorrect even if append accepts the bytes.
- `BloomMapFile` membership tests are probabilistic. Code must treat `probablyHasKey` false as definitive only if the filter is correctly maintained, and true as a hint requiring the normal map lookup.
- `ObjectWritable` serializes class names and supports primitive/array special cases. Compatibility depends on class availability, matching declared class metadata, and stable handling of nulls or primitive arrays.
- `CompressedWritable` requires subclasses and callers to honor lazy inflation. Accessing fields before `ensureInflated()` or writing inconsistent compressed state can produce stale or corrupt objects.
- `SequenceFile` format compatibility is sensitive to magic/version bytes, key/value class names, compression flags, codec classes, metadata order/encoding, sync marker placement, and block-compression layout. Reader tests should cover uncompressed, record-compressed, and block-compressed files.

## Test Signals

- API compatibility tests should verify that all classes, constructors, methods, fields, deprecation markers, visibility, static/final/synchronized flags, parameter types, return types, and thrown exceptions in this chunk remain stable.
- Filesystem contract tests should cover create/open/read/write, recursive and non-recursive delete, rename, list/status, mkdirs, working directory, local-output hooks, ownership/permission operations, and unsupported append behavior across local, FTP, KFS, S3, and native S3 backends.
- Stream tests should validate `Seekable.seek`, `getPos`, `seekToNewSource`, `Syncable.sync`, and FTP input close/read/mark/reset behavior.
- Trash tests should validate disabled trash, already-in-trash paths, path preservation under `.Trash/current`, checkpoint creation, expunge deletion of old checkpoints, and superuser emptier behavior.
- Permission tests should round-trip `FsAction`, `FsPermission`, and `PermissionStatus` through writable serialization, short encoding, symbolic `valueOf`, umask application, default umask configuration, equality/hash, and string rendering.
- S3 tests should round-trip `INode` serialization/deserialization, block metadata, store version checks, migration-tool initialization/run, credentials loading failures, and file status for files/directories.
- Shell/HTTP tests should cover option parsing arity, command name matching, `Count.run`, servlet/filter registration, internal servlet deprecation path, SSL listener setup, start/stop/join lifecycle, and stack servlet output.
- Writable tests should round-trip every primitive writable, `BytesWritable`, `ArrayWritable`, `MapWritable`, `GenericWritable`, `ObjectWritable`, `MD5Hash`, `NullWritable`, and compressed writable subclasses; compare object equality/order with raw comparator order.
- Buffer tests should verify reset behavior, logical length versus capacity, direct copy from input streams/data inputs, and exact read/skip failure on premature EOF.
- MapFile and BloomMapFile tests should cover sorted append enforcement, index interval configuration, exact and closest lookup, mid/final key, index repair, delete/rename, Bloom filter membership before/after close/reopen, and false-positive-safe lookup behavior.
- SequenceFile tests should create writers through representative overloads, include metadata, progress callbacks, explicit buffer/replication/block size, raw output stream construction, and all three compression types; readers should verify key/value class metadata, compression flags/codecs, metadata access, close synchronization, and current-value retrieval.
