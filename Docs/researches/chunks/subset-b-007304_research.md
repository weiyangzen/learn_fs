# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 6153-12404

## Chunk Scope

This chunk is a generated JDiff API XML slice for Hadoop 0.19.2. It starts in the tail of `org.apache.hadoop.fs.RawLocalFileSystem`, covers seek/sync/trash APIs, concrete FTP/KFS/S3 filesystem adapters, filesystem permissions, filesystem shell commands, embedded HTTP server APIs, and a large portion of `org.apache.hadoop.io` through the beginning of `SequenceFile.Sorter.SegmentDescriptor`.

Because this is API metadata rather than Java implementation source, control-flow and state notes are inferred from public signatures, inheritance, synchronization flags, checked exceptions, field exposure, deprecation text, and embedded Javadocs.

## Purpose

The file records the public compatibility surface used by Hadoop's binary/API comparison tooling. This range is mostly about two subsystems:

- Filesystem-facing APIs: raw local metadata updates, seekable/syncable streams, trash retention, FTP/KFS/S3 filesystem implementations, permissions, shell command parsing/execution, and the Jetty-based status HTTP server.
- Hadoop serialization and sorted-file APIs: `Writable` containers, primitive writable keys, raw comparators, reusable byte buffers, `MapFile`, `SequenceFile`, object/string serialization helpers, and sort/merge contracts.

The chunk is useful for migration and regression research because it captures exactly which classes, constructors, fields, overloads, deprecations, and exception contracts existed in Hadoop 0.19.2.

## Important APIs and Types

### Filesystem Tail

The chunk begins inside `RawLocalFileSystem`, showing public `close`, `toString`, `getFileStatus(Path)`, `setOwner(Path, String, String)`, and `setPermission(Path, FsPermission)`. The owner and permission docs explicitly route through shell commands `chown` and `chmod`, so this backend exposes platform-sensitive local metadata behavior.

`Seekable` defines cursor movement for streams with `seek(long)`, `getPos()`, and `seekToNewSource(long)`. Its contract forbids seeking past EOF and allows switching to another data source when replicated data is available. `Syncable` exposes a single `sync()` operation for flushing buffers to underlying devices.

`Trash` extends `Configured` and provides per-filesystem deletion staging. It can `moveToTrash(Path)`, create checkpoints, `expunge()` old checkpoints, expose a superuser `Runnable` emptier, and run that emptier from `main`. The design preserves original paths under a user's `.Trash/current` directory and avoids requiring full trash enumeration, filesystem timestamps, or clock synchronization.

### FTP and KFS Filesystems

`FTPException` is a runtime wrapper for FTP failures. `FTPFileSystem` extends `FileSystem` and integrates Apache Commons Net through `initialize(URI, Configuration)`, `open`, `create`, `delete(Path[, boolean])`, `listStatus`, `getFileStatus`, `mkdirs`, `rename`, URI and working-directory methods, plus `LOG`, `DEFAULT_BUFFER_SIZE`, and `DEFAULT_BLOCK_SIZE`. `append` is documented as an unsupported optional operation. Its `create` contract warns that an output stream must be closed before other APIs are called, or operations may block.

`FTPInputStream` extends `FSInputStream` and wraps an `InputStream`, `FTPClient`, and filesystem statistics. It supports `getPos`, `seek`, `seekToNewSource`, synchronized byte reads, synchronized close, and mark/reset methods.

`KosmosFileSystem` extends `FileSystem` for KFS. It exposes URI/name/init methods, working directory mutation, `mkdirs`, `isDirectory`, `isFile`, `listStatus`, `getFileStatus`, unsupported `append`, `create`, `open`, `rename`, recursive and legacy delete overloads, length/replication/default replication/block size, `setReplication`, `lock`, `release`, `getFileBlockLocations`, local copy helpers, and local-output staging. Block locations are retrieved from KFS chunks and can return null if the file does not exist.

### Permissions

`AccessControlException` is a public `IOException` with default and string constructors; the default constructor exists for `RemoteException` unwrapping.

`FsAction` is an enum for filesystem read/write/execute combinations. It exposes `implies`, boolean-style `and`, `or`, `not`, plus public `INDEX` and `SYMBOL` fields for octal and symbolic representations.

`FsPermission` implements `Writable` and models user/group/other permissions. It supports construction from three `FsAction` values, a short mode, or another permission; immutable creation; action getters; `fromShort`; `write`/`readFields`; static `read(DataInput)`; `toShort`; equality/hash/string; `applyUMask`; static `getUMask`, `setUMask`, `getDefault`, and symbolic `valueOf(String)`. Public config fields include `UMASK_LABEL` and `DEFAULT_UMASK`.

`PermissionStatus` implements `Writable` for owner, group, and permission metadata. It supports immutable creation, getters, `applyUMask`, instance and static serialization helpers, static read, and string conversion.

### S3 Filesystems

`Block` holds a block id and length for the block-based S3 store. `FileSystemStore` is the backing-store interface for block S3: initialize, version lookup, inode/block storage and retrieval, existence checks, deletion, shallow/deep subpath listing, `purge()` for tests, and diagnostic `dump()`.

`INode` stores S3 file metadata: file type plus an array of `Block` pointers. It exposes type/block getters, directory/file predicates, serialized length, `serialize()`, static `deserialize(InputStream)`, `FILE_TYPES`, and `DIRECTORY_INODE`.

`MigrationTool` is a `Tool` for migrating older S3 filesystem metadata to newer versions by rewriting block metadata without touching data files. `S3Credentials` extracts access and secret keys from the filesystem URI or configuration and throws `IllegalArgumentException` when credentials cannot be determined. `S3Exception`, `S3FileSystemException`, and `VersionMismatchException` model S3 communication, filesystem, and store-version failures.

`S3FileSystem` is the block-based S3 `FileSystem`. It can be constructed with a custom `FileSystemStore` and implements URI/init/name, working directory, `mkdirs`, `isFile`, `listStatus`, unsupported `append`, `create`, `open`, `rename`, delete overloads, and `getFileStatus`. Permission parameters are documented as ignored for mkdir/create.

`NativeS3FileSystem` is the native-object S3 backend, constructed with or without a `NativeFileSystemStore`. It implements initialize, unsupported append, create, delete overloads, status, URI, listing, mkdirs, open, rename, working-directory methods, and `LOG`. Its doc distinguishes native S3 storage from the older block-based format so external S3 tools can read files directly.

### Shell and HTTP APIs

`org.apache.hadoop.fs.shell.Command` is an abstract `Configured` base for filesystem CLI commands. It stores protected `args`, requires `getCommandName()` and protected `run(Path)`, and provides `runAll()` to execute over each source path with `0` success and `-1` failure.

`CommandFormat` parses command options/parameters from an argument array and exposes `getOpt(String)`. `Count` implements the filesystem count command, with `matches(String)`, command name, protected path execution, and public `NAME`, `USAGE`, and `DESCRIPTION` fields. Its purpose is counting directories, files, bytes, quota, and remaining quota.

`FilterContainer` abstracts servlet filter registration. `FilterInitializer` is an abstract hook for initializing `javax.servlet.Filter` instances, but this chunk exposes only its constructor and class doc.

`HttpServer` embeds Jetty for status pages. It implements `FilterContainer` and exposes constructors with name/bind address/port/findPort and optional `Configuration`; default app/servlet/context setup; servlet and internal servlet registration; filter definition and path mappings; webapp attributes; webapp path lookup; port lookup; thread configuration; SSL listener setup; start/stop lifecycle. Protected/public fields expose `LOG`, Jetty `Server`, `WebApplicationContext`, default contexts, `findPort`, `SocketListener`, and filter names. `HttpServer.StackServlet` serves and logs current stack traces through `doGet`.

### Core IO Serialization

`AbstractMapWritable` is a `Writable`/`Configurable` base for map-like writables. Its per-instance class-id maps travel with the object instead of being static, allowing nested `MapWritable` values. IDs range from 1 to 127. It has synchronized `addToMap` and `copy`, protected class/id lookups, config accessors, and serialization.

`ArrayFile` extends `MapFile` as a dense long-index-to-value file. `ArrayFile.Reader` supports synchronized seek by index, next, current key, and random get. `ArrayFile.Writer` creates value-class-specific array files and synchronized appends, with optional compression/progress constructor.

`ArrayWritable` stores homogeneous `Writable[]` values, including a string-array constructor. It exposes value class, string conversion, Java array conversion, set/get, and `Writable` serialization. The doc warns reducer inputs often need typed subclasses.

`BinaryComparable` is an abstract byte-backed comparable. Subclasses provide `getLength()` and `getBytes()`, while common compare/equality/hash behavior delegates to byte comparison and hashing semantics.

Primitive writable wrappers include `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, and `LongWritable`. Each has default/value constructors, mutable `set`/`get`, `readFields`, `write`, equality/hash, `compareTo`, `toString`, and an optimized nested `WritableComparator`. `LongWritable.DecreasingComparator` reverses object and serialized-byte ordering.

`BytesWritable` extends `BinaryComparable` and implements `WritableComparable`. It distinguishes logical length from backing capacity, exposes `getBytes`, deprecated `get`, `getLength`, deprecated `getSize`, `setSize`, `getCapacity`, `setCapacity`, set-from-other/range, serialization, equality/hash, and hex-like string output. Its comparator compares serialized forms.

`Closeable` is a deprecated Hadoop alias for `java.io.Closeable`. `CompressedWritable` is an abstract lazy-compression base: final public `readFields` and `write` handle compressed payloads, while subclasses implement protected `readFieldsCompressed` and `writeCompressed`; callers accessing subclass fields must call `ensureInflated()`.

`DataInputBuffer`, `InputBuffer`, `DataOutputBuffer`, and `OutputBuffer` are reusable in-memory stream/data buffers. They reset over byte arrays or empty output state, expose backing data and valid lengths/positions, and support direct writes from `DataInput` or `InputStream`.

`DefaultStringifier<T>` uses Hadoop `SerializationFactory`, `Serializer`, and `Deserializer` to base64-encode serialized objects into strings. It implements `Stringifier<T>`, provides `fromString`, `toString(T)`, `close`, and static `store`, `load`, `storeArray`, and `loadArray` helpers for `Configuration` persistence.

`GenericWritable` wraps one of a fixed subclass-defined set of `Writable` classes. It is more compact than `ObjectWritable` because it serializes a type index instead of a class name per record, and it propagates configuration to wrapped `Configurable` values before deserialization.

`IOUtils` provides stream-copy overloads with explicit buffer size or `Configuration`, optional close behavior, `readFully`, `skipFully`, cleanup helpers that ignore close exceptions, and socket close helpers. `IOUtils.NullOutputStream` discards byte writes.

`MapWritable` extends `AbstractMapWritable` and implements `Map<Writable, Writable>`, exposing normal map operations plus serialized class-id-aware read/write. `MD5Hash` is a `WritableComparable` for 16-byte MD5 values, with constructors from hex or bytes, digest helpers over byte arrays, streams, strings, and `UTF8`, half/quarter digest conversions, hex parsing, and an optimized comparator. `MultipleIOException` wraps a list of IO failures and has a static factory that can collapse lists into a convenient `IOException`. `NullWritable` is a singleton zero-byte writable with comparator support.

`ObjectWritable` is a polymorphic `Writable`/`Configurable` that writes an instance with its declared class and handles `Writable`, `String`, primitives, and arrays. Static `writeObject` and `readObject` are central RPC/serialization integration points.

### MapFile and SequenceFile APIs

`MapFile` models a directory containing a `data` SequenceFile and an `index` file. Static methods rename, delete, repair a corrupt map by recreating its index (`fix`), and run a CLI `main`. Public constants are `INDEX_FILE_NAME` and `DATA_FILE_NAME`. The doc requires keys to be appended in order and notes that the index file is read entirely into memory.

`MapFile.Reader` is synchronized around read/navigation operations. It can open immediately or through a protected deferred-open constructor, override `createDataFileReader`, reset, compute a middle key, read final key, seek exact-or-next, iterate, get exact values, get closest before/after, and close. `MapFile.Writer` has many constructors for key class or comparator, compression type/codec, and progress. It exposes index interval getters/setters, static configuration storage for index interval, synchronized close, and synchronized append requiring nondecreasing keys.

`RawComparator<T>` extends `Comparator<T>` with a byte-array compare method for serialized objects, enabling sort paths that avoid deserialization.

`SequenceFile` exposes deprecated config-level compression get/set helpers and a broad set of static `createWriter` overloads for filesystem/path or raw output stream, key/value classes, buffer size, replication, block size, compression type, codec, progress, and metadata. `SYNC_INTERVAL` defines spacing between sync points. `CompressionType` is the enum-like compression mode.

`SequenceFile.Metadata` is a `Writable` wrapper around `TreeMap<Text, Text>` with get/set/map access, serialization, equality/hash, and string conversion.

`SequenceFile.Reader` implements `java.io.Closeable`, opens files through `FileSystem`/`Path`/`Configuration`, allows protected `openFile` specialization, exposes key/value class names and classes, compression flags/codecs, metadata, current value retrieval, typed and object-based `next`, raw key/value access, deprecated raw-next overload, seek, sync-to-next-sync-marker, `syncSeen`, current position, and file-name string conversion. Many read-position methods are synchronized.

`SequenceFile.Sorter` sorts and merges sequence files. It supports class-based or `RawComparator` constructors, merge fan-in factor, memory buffer sizing, progress callback, sorting input paths to output or iterator, backward-compatible single-file sort, multiple merge overloads returning `RawKeyValueIterator`, output writer creation by cloning input attributes, writing iterator records to a writer, and merge-to-output. Its doc warns key `readFields` implementations should avoid allocation for performance.

`SequenceFile.Sorter.RawKeyValueIterator` exposes current raw key/value, `next`, `close`, and a `Progress` object. The chunk ends just after the constructor doc starts for `SequenceFile.Sorter.SegmentDescriptor`, so the final per-file merge must reconcile that class from the next chunk.

## Control Flow and Behavioral Contracts

Filesystem control flow centers on `FileSystem` implementations accepting `Path` values, resolving backend-specific state in `initialize`, and returning `FSDataInputStream`/`FSDataOutputStream` wrappers for open/create. Optional operations like append are explicitly unsupported for FTP, KFS, S3, and native S3 in this range.

Seekable read flow is cursor-based: `seek` changes the next read position, `getPos` reports the current offset, and `seekToNewSource` can switch replicas/sources. FTP reads and closes are synchronized, indicating stream state and remote client state must be protected during read/close.

Trash flow moves a path to `.Trash/current`, checkpoints current trash, and expunges old checkpoints. The emptier is a long-running `Runnable` intended for superuser operation across users.

Permission flow encodes `FsAction` triples into short modes, applies umasks by returning new permission/status values, and serializes permissions through `Writable` methods for metadata persistence and RPC.

S3 block filesystem flow splits metadata and data: `S3FileSystem` manipulates Hadoop paths, `FileSystemStore` persists path-to-`INode` metadata and block objects, and `INode` serializes file type plus block references. Migration rewrites metadata only. Native S3 flow instead maps files to native S3 objects for interoperability.

HTTP server flow constructs Jetty contexts, registers default webapps/servlets/filters, sets webapp attributes for JSP access, optionally adds SSL, then starts/stops the embedded server. `findPort` controls port increment behavior during bind.

Writable control flow is conventional Hadoop serialization: write all fields to `DataOutput`, then restore them through `readFields(DataInput)`. Comparators operate directly on serialized byte arrays to support efficient sorting. `GenericWritable`, `ObjectWritable`, `MapWritable`, and `AbstractMapWritable` add type metadata around arbitrary or heterogeneous writable payloads.

MapFile/SequenceFile flow is sorted-file oriented. Writers append in key order, periodically emit index/sync metadata, and close files. Readers use in-memory indexes, seek/sync markers, typed or raw record iteration, and closeable streams. Sorter creates sorted runs, merges segments with configurable fan-in and memory, exposes raw iterators, and can clone output attributes from input sequence files.

## State and Persistence

Persistent state in this chunk includes filesystem data on local disk, FTP servers, KFS, block-based S3 metadata/data objects, and native S3 objects. `Trash` persists deleted paths and checkpoint directories under user home trash directories.

S3 block state is path-keyed inode metadata plus block files/objects. `Block` stores id/length, `INode` stores type and block list, and `FileSystemStore` persists or deletes both. `S3Credentials` holds access key and secret key values resolved from URI/configuration.

Permissions persist as compact short modes and owner/group strings through `FsPermission` and `PermissionStatus`. Umask lives in `Configuration` under `UMASK_LABEL`.

HTTP server state includes Jetty server/listener/context objects, filter mappings, default contexts, webapp attributes, and thread/listener settings.

IO state includes mutable primitive writable values, mutable buffer backing arrays and current lengths/positions, class-id maps in `AbstractMapWritable`, wrapped type indexes in `GenericWritable`, declared class/instance state in `ObjectWritable`, MD5 digest bytes, and closeable stream positions in MapFile/SequenceFile readers.

MapFile persistence is a directory with `data` and `index` files. SequenceFile persistence is a binary key/value format with compression type, optional codec, metadata, sync points, raw key/value records, and sort/merge temporary outputs.

## Dependencies and Integration Points

Visible dependencies include Java IO/networking (`InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `File`, `Socket`, `URI`, `InetSocketAddress`, `IOException`), Java collections/comparators, and servlet APIs.

Hadoop dependencies include `Configuration`, `Configured`, `Tool`, `Progressable`, `Progress`, `Path`, `FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSInputStream`, `FileStatus`, `BlockLocation`, `Writable`, `WritableComparable`, `WritableComparator`, `Stringifier`, `Text`, `UTF8`, and compression codecs.

External integrations include Apache Commons Net for FTP, Apache Commons Logging, Amazon S3 concepts and stores, KFS native/client integration, and Mortbay Jetty classes (`Server`, `SocketListener`, `WebApplicationContext`) for embedded status HTTP services.

The main integration points are stable public APIs: `FileSystem` backend contracts, shell command classes used by Hadoop CLI tooling, `HttpServer` used by daemons for status pages, and `Writable`/`SequenceFile`/`MapFile` used by MapReduce, RPC, and on-disk sorted data.

## Risks and Edge Cases

- This XML does not include method bodies, so exact exception branches, locking internals, and cleanup behavior must be verified against Java sources when changing behavior.
- The chunk starts mid-`RawLocalFileSystem` and ends mid-`SequenceFile.Sorter.SegmentDescriptor`; adjacent chunks are required for complete class-level synthesis.
- Raw local ownership and permissions depend on shell `chown`/`chmod`, which can vary by platform and user privileges.
- FTP create streams must be closed before other API calls, or later operations may block.
- FTP, KFS, S3, and native S3 append are unsupported despite the `FileSystem` append surface.
- S3 create/mkdir permission parameters are ignored, so callers expecting permission enforcement will get backend-specific behavior.
- Block-based S3 stores metadata and data separately; failed migrations or partial writes can leave inode/block inconsistency.
- Native S3 and block S3 have incompatible object layouts, so migration/interoperability assumptions must be explicit.
- `FileSystemStore.purge()` is test-oriented and destructive.
- `HttpServer.addInternalServlet` is deprecated as temporary; code relying on it is compatibility-sensitive.
- Jetty fields are protected/publicly visible enough for subclasses to couple tightly to old Mortbay classes.
- `AbstractMapWritable` supports only 127 distinct classes per map instance.
- `BytesWritable.getBytes()` returns backing storage, valid only through `getLength()`, and capacity may exceed logical data.
- `CompressedWritable` requires subclass field accessors to call `ensureInflated()`, or stale compressed state can be observed.
- `MapFile.Writer.append` requires nondecreasing keys; violations can corrupt sorted lookup assumptions.
- `MapFile` index files are loaded entirely into memory, creating risk with large keys or very dense indexing.
- `SequenceFile.Reader.seek(long)` requires a position returned by writer length during writing; arbitrary byte seeking must use `sync(long)`.
- Deprecated APIs remain part of the 0.19.2 compatibility surface, including old `delete(Path)` forms, Hadoop `Closeable`, and SequenceFile compression config helpers.

## Test Signals

Useful tests inferred from this API slice:

- Raw local filesystem tests for `getFileStatus`, close behavior, `setOwner`, and `setPermission`, including shell-command failure paths.
- `Seekable` tests for normal seek, EOF rejection, `getPos`, and `seekToNewSource` behavior across local and replicated/remote streams.
- `Trash` tests for disabled trash, already-in-trash paths, preserved original path layout, checkpoint creation, expunge, and superuser emptier scheduling.
- FTP filesystem tests for URI initialization, create/open/list/status/mkdir/rename/delete, unsupported append, statistics updates in `FTPInputStream`, and the documented stream-close-before-next-operation rule.
- KFS tests for lock/release, block locations, replication/defaults, local copy staging, unsupported append, and null locations for missing files.
- Permission tests for `FsAction` implication/and/or/not, short and symbolic `FsPermission` conversion, umask application, immutable permission/status creation, and `Writable` round trips.
- S3 block-store tests for inode/block store/retrieve/delete/list, inode serialization/deserialization, credential extraction precedence, version mismatch, metadata-only migration, ignored permissions, unsupported append, and destructive `purge` isolation.
- Native S3 tests for object-native create/open/list/delete/rename/mkdir/status behavior and unsupported append.
- Shell command tests for argument format bounds/options, `Count.matches`, `runAll` success/failure aggregation, and protected command execution over multiple paths.
- HTTP server tests for port finding, servlet/filter registration, webapp attribute access, default context setup, SSL listener configuration, lifecycle start/stop, and stack servlet response/log behavior.
- Writable tests for primitive wrappers, raw comparators, `BytesWritable` length versus capacity, `DataInputBuffer`/`DataOutputBuffer` reset and backing data validity, compressed writable lazy inflation, `GenericWritable` allowed-type indexes, `ObjectWritable` primitive/string/array handling, `MapWritable` class-id serialization, `NullWritable` singleton serialization, and `MD5Hash` digest/hex/ordering.
- MapFile tests for ordered append enforcement, reader seek/get/getClosest before and after keys, final/mid key retrieval, index interval configuration, corrupt-index `fix` dry run and repair, close idempotence, and dense `ArrayFile` indexing.
- SequenceFile tests for all writer overload families, metadata persistence, compression type/codec handling, raw and typed reader iteration, sync marker seeking, deprecated raw next compatibility, sorter fan-in/memory/progress behavior, merge delete-input behavior, cloned writer attributes, and raw iterator progress/close semantics.

## Chunk Boundary Notes

The previous chunk is needed for the full `RawLocalFileSystem` class and earlier filesystem APIs. The next chunk is needed for the body of `SequenceFile.Sorter.SegmentDescriptor` and later `org.apache.hadoop.io` classes. The final merge lane should preserve that this chunk is a partial view of both boundary classes and should avoid treating inferred control flow as implementation-confirmed behavior.
