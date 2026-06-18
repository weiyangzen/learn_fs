# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.1.xml lines 6171-12399

## Chunk Scope

This chunk is a large middle section of the generated JDiff public API XML for Hadoop 0.20.1. It is API metadata, not Java implementation source. The range begins inside the tail of `org.apache.hadoop.fs.RawLocalFileSystem`, then covers filesystem stream contracts, trash handling, FTP/KFS/S3 filesystem adapters, filesystem permission types, shell command helpers, the embedded Jetty HTTP server API, and a substantial prefix of the `org.apache.hadoop.io` serialization and file-format APIs. The chunk ends inside `org.apache.hadoop.io.SequenceFile.Reader`, after the second `getCurrentValue` method entry has started but before the method entry is complete.

The XML records public compatibility surface: packages, class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared checked exceptions, fields, visibility, abstract/static/final/synchronized/native flags, deprecation states, and embedded Javadoc contracts. Because no method bodies are present, control flow and state behavior below are inferred from signatures, type relationships, and documentation.

## Purpose

This chunk documents several foundational Hadoop Common APIs:

- local and remote `FileSystem` implementations and stream interfaces;
- permission and owner metadata classes used by filesystem status and create operations;
- block-oriented and native Amazon S3 filesystem abstractions;
- shell command parsing and the `count` command;
- HTTP server/filter/servlet extension points used by Hadoop daemons;
- `Writable`, `WritableComparable`, comparator, buffer, stringification, and map/sequence-file storage helpers under `org.apache.hadoop.io`.

The JDiff file exists to preserve Hadoop 0.20.1 API compatibility signals. For this chunk, the compatibility-sensitive surfaces are mostly filesystem semantics, serialization formats, public utility contracts, and binary file-format APIs that older jobs and tools may depend on.

## Important APIs and Types

### `org.apache.hadoop.fs` tail

The chunk starts in the middle of `RawLocalFileSystem`, after earlier class metadata and methods have already appeared in the previous chunk. Visible methods include create overloads returning `FSDataOutputStream`, `rename(Path, Path)`, deprecated and recursive `delete` forms, `listStatus(Path)`, `mkdirs(Path)` and `mkdirs(Path, FsPermission)`, working-directory/home-directory accessors, `moveFromLocalFile`, `startLocalOutput`, `completeLocalOutput`, `close`, `toString`, `getFileStatus(Path)`, `setOwner(Path, String, String)`, and `setPermission(Path, FsPermission)`. The class documentation states that it implements the `FileSystem` API for the raw local filesystem; `setOwner` and `setPermission` document shell-command based ownership and mode changes.

`Seekable` is a public interface for streams that can reposition. It defines `seek(long pos)`, `getPos()`, and `seekToNewSource(long targetPos)`, all throwing `IOException` except as documented by return type. Its contract says seeking positions the next read from a given offset and cannot seek past EOF; `seekToNewSource` is for switching to another replica/source of the same data.

`Syncable` is a public interface with `sync() throws IOException`. The documentation describes flushing or synchronizing all buffers with underlying devices. This is a durability/control-plane API used by output streams whose writes need explicit sync semantics.

`Trash` extends `Configured` and exposes Hadoop's trash-can feature. Constructors accept a `Configuration` or a `FileSystem` plus `Configuration`. Public methods include `moveToTrash(Path)`, `checkpoint()`, `expunge()`, `getEmptier()`, and static `main(String[] args)`. The documented storage model moves deleted paths under a user's home-directory `.Trash/current` directory while preserving original paths, then periodically checkpoints current trash and removes older checkpoints. `getEmptier()` returns a `Runnable` intended for a superuser daemon.

### `org.apache.hadoop.fs.ftp`

`FTPException` is a runtime wrapper with constructors for message, cause, and message plus cause.

`FTPFileSystem` extends `FileSystem`. It exposes `initialize(URI, Configuration)`, `open(Path, int)`, `create(Path, FsPermission, boolean, int, short, long, Progressable)`, `append(Path, int, Progressable)`, two `delete` overloads, `getUri()`, `listStatus(Path)`, `getFileStatus(Path)`, `mkdirs(Path, FsPermission)`, `rename(Path, Path)`, `getWorkingDirectory()`, `getHomeDirectory()`, and `setWorkingDirectory(Path)`. The non-recursive `delete(Path)` is deprecated in favor of `delete(Path, boolean)`. `append` is documented as unsupported. The `create` Javadoc warns that a stream returned by `create` must be closed before using other APIs on the same filesystem or later operations may block. Public fields include `LOG`, `DEFAULT_BUFFER_SIZE`, and `DEFAULT_BLOCK_SIZE`.

`FTPInputStream` extends `FSInputStream`. Its constructor wraps a Java `InputStream`, an Apache Commons Net `FTPClient`, and `FileSystem.Statistics`. It implements `getPos()`, `seek(long)`, `seekToNewSource(long)`, single-byte and buffer `read` overloads, `close()`, and mark/reset APIs. Its type position means it must provide Hadoop `Seekable`/positioned stream behavior on top of an FTP data connection, even though the exact seek strategy is not visible in this XML.

### `org.apache.hadoop.fs.kfs`

`KosmosFileSystem` extends `FileSystem` and adapts Hadoop's filesystem abstraction to KFS/Kosmos. Public methods include URI/name initialization, working-directory setters/getters, `mkdirs`, `isDirectory`, `isFile`, `listStatus`, `getFileStatus`, `append`, `create`, `open`, `rename`, two `delete` overloads, length/replication/block-size accessors, `setReplication`, `lock(Path, boolean)`, `release(Path)`, `getFileBlockLocations(FileStatus, long, long)`, and local copy staging helpers. Permission parameters are documented as currently ignored for `mkdirs` and `create`. The API exposes KFS-specific lock/release semantics in addition to the regular Hadoop `FileSystem` contract.

### `org.apache.hadoop.fs.permission`

`AccessControlException` extends `IOException` and provides empty, message, and throwable constructors. It is the checked exception type for authorization failures at filesystem boundaries.

`FsAction` is a public enum representing Unix-like action sets. Constants include `NONE`, `EXECUTE`, `WRITE`, `WRITE_EXECUTE`, `READ`, `READ_EXECUTE`, `READ_WRITE`, and `ALL`, each with a `SYMBOL` string. Besides generated enum methods, it exposes `implies(FsAction)`, `and(FsAction)`, `or(FsAction)`, and `not()`, modeling permission set algebra.

`FsPermission` implements `Writable` and represents user/group/other actions. Constructors accept explicit `FsAction` values, a packed `short`, or another `FsPermission`. Public methods include `createImmutable(short)`, getters for user/group/other actions, `fromShort(short)`, `write(DataOutput)`, `readFields(DataInput)`, static `read(DataInput)`, `toShort()`, equality/hash/string conversion, `applyUMask(FsPermission)`, static `getUMask(Configuration)`, static `setUMask(Configuration, FsPermission)`, static `getDefault()`, and static `valueOf(String unixSymbolicPermission)`. Public constants include `UMASK_LABEL` and `DEFAULT_UMASK`.

`PermissionStatus` implements `Writable` and stores owner, group, and `FsPermission`. It has a constructor from those three fields plus `createImmutable`, getters, `applyUMask`, `readFields`, instance `write`, static `read`, static component-wise `write(DataOutput, String, String, FsPermission)`, and `toString`. It is the serializable aggregate used where permissions travel with filesystem metadata.

### `org.apache.hadoop.fs.s3`

`Block` stores S3 block metadata: constructor `(long id, long length)`, getters, and `toString`.

`FileSystemStore` is the low-level persistence contract for the old block-based S3 filesystem. It defines initialization, version retrieval, `INode` and `Block` store/retrieve/delete operations, existence checks, shallow and deep subpath listings, `purge()` for tests, and `dump()` diagnostics.

`INode` stores file metadata for the block-based S3 filesystem, including `INode.FileType` and an array of `Block`s. It exposes getters, `isDirectory()`, `isFile()`, `getSerializedLength()`, `serialize()`, static `deserialize(InputStream)`, `FILE_TYPES`, and `DIRECTORY_INODE`.

`MigrationTool` extends `Configured` and implements `Tool`. It has `main`, `run(String[])`, and `initialize(URI)`. Documentation says it migrates older S3 filesystem metadata to a newer version by rewriting block metadata without touching data files.

`S3Credentials` extracts AWS credentials from a filesystem URI or `Configuration`. It exposes `initialize(URI, Configuration)`, `getAccessKey()`, and `getSecretAccessKey()`, with documentation that initialization throws `IllegalArgumentException` if credentials cannot be determined.

`S3Exception` is a runtime exception for S3 communication problems. `S3FileSystemException` extends `IOException` for fatal `S3FileSystem` problems. `VersionMismatchException` extends `S3FileSystemException` and represents stored-data version incompatibility.

`S3FileSystem` extends `FileSystem` and implements the old block-based Hadoop S3 filesystem. Constructors include a default constructor and one accepting a `FileSystemStore`. Public methods include `getUri`, `initialize`, `getName`, working-directory accessors, `mkdirs`, `isFile`, `listStatus`, unsupported `append`, `create`, `open`, `rename`, two `delete` overloads, and `getFileStatus`. Its Javadoc contrasts this block-based representation with `NativeS3FileSystem`.

### `org.apache.hadoop.fs.s3native`

`NativeS3FileSystem` extends `FileSystem` and stores files directly in native S3 object form, unlike the block-based `S3FileSystem`. Constructors include default and `NativeFileSystemStore` injection forms. Public methods include `initialize`, unsupported `append`, `create`, two `delete` overloads, `getFileStatus`, `getUri`, `listStatus`, `mkdirs`, `open`, `rename`, and working-directory accessors. Its `listStatus` documentation exposes an operational cost model: file status can be one S3 call, while directory listing may require up to roughly `n / 1000 + 2` S3 calls for direct children. It has a public static `LOG` field.

### `org.apache.hadoop.fs.shell`

`Command` extends `Configured` and is the base for shell commands. It stores `args` and exposes `getCommandName()`, `run(Path)`, and `runAll()`. The Javadoc indicates `runAll` executes the command over arguments and returns an exit code, while subclasses implement command-specific behavior.

`CommandFormat` parses command-line options. Its constructor accepts a command name, minimum and maximum parameter counts, and option strings. `parse(String[])` returns a `List` of remaining parameters and `getOpt(String)` tests whether a named option was present.

`Count` extends `Command` for a content-summary/count command. It has constructor `(String[] args, int pos, Configuration conf)`, static-ish matching through `matches(String cmd)`, `getCommandName()`, and `run(Path)`. Public fields `NAME`, `USAGE`, and `DESCRIPTION` expose shell help text.

### `org.apache.hadoop.http`

`FilterContainer` is an interface with `addFilter(String name, String classname, Map parameters)` and `addGlobalFilter(String name, String classname, Map parameters)`. It is the injection point for servlet filters on selected contexts or all contexts.

`FilterInitializer` is an abstract-ish extension class with a constructor; the visible chunk only shows the class shell, implying concrete initializers are elsewhere or methods are not in this line range.

`HttpServer` implements `FilterContainer` and wraps an embedded Jetty server. Constructors accept server name, bind address, port, find-port flag, and optionally `Configuration`. Public methods include listener/context setup (`createBaseListener`, `addDefaultApps`, `addDefaultServlets`, two `addContext` overloads), servlet and filter registration (`addServlet`, `addInternalServlet`, `addFilter`, `addGlobalFilter`, `defineFilter`, `addFilterPathMapping`), attributes (`setAttribute`, `getAttribute`), static webapp path lookup, port/thread controls, SSL listener overloads, lifecycle (`start`, `stop`, `join`), and fields for `LOG`, Jetty `Server`, `Connector`, `WebAppContext`, `findPort`, `defaultContexts`, and `filterNames`. The documentation describes the standard daemon HTTP layout: `/logs/`, `/static/`, and `/` for JSP webapps.

`HttpServer.StackServlet` extends `HttpServlet`. It has a default constructor and `doGet(HttpServletRequest, HttpServletResponse)` throwing `ServletException` and `IOException`. Documentation says it emits and logs current stack traces; the returned and logged traces may be sequential rather than exactly identical.

### `org.apache.hadoop.io` serialization and file APIs

`AbstractMapWritable` implements `Writable` and `Configurable`. It maintains per-instance class-id mappings for `MapWritable` and `SortedMapWritable`, with protected `addToMap(Class)`, `getClass(byte)`, `getId(Class)`, and `copy(Writable)`, plus configuration and serialization methods. Documentation notes class IDs range from 1 to 127.

`ArrayFile` extends `MapFile` as a dense file-backed mapping from integer positions to values. `ArrayFile.Reader` extends `MapFile.Reader` with `seek(long n)`, `next(Writable value)`, `key()`, and `get(long n, Writable value)`. `ArrayFile.Writer` extends `MapFile.Writer` and appends values using implicit increasing integer keys.

`ArrayWritable` implements `Writable` for homogeneous arrays of `Writable` instances. Constructors accept a value class, value class plus array, or string array. Methods expose value class, `toStrings`, `toArray`, `set(Writable[])`, `get()`, `readFields`, and `write`. Javadoc warns reducers often need a subclass that fixes the element type.

`BinaryComparable` is an abstract comparable over a representative byte array. Subclasses implement `getLength()` and `getBytes()`. Public comparison/equality/hash methods delegate byte semantics to `WritableComparator` helpers. This is the base for byte-oriented comparable values such as `BytesWritable`.

`BloomMapFile` is a MapFile variant with a dynamic Bloom filter for fast membership checks. Static methods/fields include `delete(FileSystem, String)`, `BLOOM_FILE_NAME`, and `HASH_COUNT`. `BloomMapFile.Reader` extends `MapFile.Reader` with constructors, `probablyHasKey(WritableComparable)`, a Bloom-guarded `get`, and `getBloomFilter()`. `BloomMapFile.Writer` extends `MapFile.Writer` with many constructor overloads matching key/value class, comparator, compression type, codec, and progress variants, plus synchronized `append` and `close`.

`BooleanWritable`, `ByteWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, and `DoubleWritable` are primitive `WritableComparable` wrappers. Each exposes default and value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`. Each has a nested `Comparator` extending `WritableComparator` with raw byte-array comparison. `LongWritable` also has `DecreasingComparator`, which reverses both object and raw-byte compare order.

`BytesWritable` extends `BinaryComparable` and implements `WritableComparable`. It stores a resizable byte sequence with distinct length and capacity. Public APIs include constructors, `getBytes()`, deprecated `get()`, `getLength()`, deprecated `getSize()`, `setSize(int)`, `getCapacity()`, `setCapacity(int)`, `set(BytesWritable)`, `set(byte[], int, int)`, `readFields`, `write`, `hashCode`, `equals`, and `toString`. `BytesWritable.Comparator` provides optimized raw serialized comparison.

`Closeable` is a Hadoop `org.apache.hadoop.io.Closeable` interface in this chunk, separate from Java's `java.io.Closeable`. The marker shows only the interface boundary in this range, so any methods are either absent or outside visible lines.

`CompressedWritable` is an abstract `Writable` wrapper for lazily compressed instance data. It exposes a default constructor, `readFields`, `write`, and protected abstract-ish `writeCompressed(DataOutput)` and `readFieldsCompressed(DataInput)` methods. Its role is to avoid repeated full object serialization cost until compressed state must be materialized.

`DataInputBuffer` extends `DataInputStream` and provides a reusable in-memory input buffer. It has constructors, `reset(byte[], int)`, `reset(byte[], int, int)`, `getData()`, `getPosition()`, and `getLength()`. `InputBuffer` is the related reusable `FilterInputStream` with reset and position/length accessors.

`DataOutputBuffer` extends `DataOutputStream` and provides a reusable expandable output buffer with constructors, `getData()`, `getLength()`, `reset()`, `write(DataInput, int)`, and `writeTo(OutputStream)`. `OutputBuffer` is the related `FilterOutputStream` exposing `getData()`, `getLength()`, `reset()`, and `write(InputStream, int)`.

`DefaultStringifier` implements `Stringifier` and converts arbitrary objects to and from strings using Hadoop serialization. Constructors accept `Configuration` and target class. Methods include `fromString`, `toString`, `close`, and static helpers `store`, `load`, `storeArray`, and `loadArray` for placing serialized values in `Configuration`.

`GenericWritable` implements `Writable` and `Configurable` as a more efficient tagged union for a fixed set of `Writable` types. Public methods include `set(Writable)`, `get()`, `toString`, `readFields`, `write`, protected abstract `getTypes()`, and configuration getters/setters. Documentation highlights that it avoids writing a class name string for every record, unlike `ObjectWritable`, and passes configuration to wrapped configurable objects before deserialization.

`IOUtils` exposes static I/O helpers: three `copyBytes` overloads for stream copying with buffer size/configuration and optional close behavior, `readFully(InputStream, byte[], int, int)`, `skipFully(InputStream, long)`, `cleanup(Log, Closeable[])`, `closeStream(Closeable)`, and `closeSocket(Socket)`. Nested `IOUtils.NullOutputStream` is an output stream that discards bytes.

`MapFile` is a directory-backed sorted map format built from a `data` `SequenceFile` and an `index` `SequenceFile`. Static helpers include `rename`, `delete`, `fix`, and `main`; public constants are `INDEX_FILE_NAME` and `DATA_FILE_NAME`. Documentation states keys must be added in order, the index is read entirely into memory, and corrupt indexes can be recreated from data.

`MapFile.Reader` implements `java.io.Closeable` and provides sorted lookup over existing MapFiles. Constructors accept filesystem, directory name, optional `WritableComparator`, configuration, and a protected deferred-open flag. Methods include `getKeyClass`, `getValueClass`, protected synchronized `open`, protected `createDataFileReader`, synchronized `reset`, `midKey`, `finalKey`, `seek`, `next`, `get`, two `getClosest` overloads, and `close`.

`MapFile.Writer` implements `java.io.Closeable` and creates sorted MapFiles. It has many constructors for class-based or comparator-based keys, value class, compression type, codec, and progress callback. Public methods include static and instance `getIndexInterval`, static and instance `setIndexInterval`, `close`, and synchronized `append(WritableComparable, Writable)`.

`MapWritable` extends `AbstractMapWritable` and implements `java.util.Map`. It exposes copy/default constructors and regular map methods: `clear`, `containsKey`, `containsValue`, `entrySet`, `get`, `isEmpty`, `keySet`, `put`, `putAll`, `remove`, `size`, `values`, plus `write` and `readFields`. It serializes both entries and the per-instance class mapping needed to decode heterogeneous `Writable` keys/values.

`MD5Hash` implements `WritableComparable` as a 16-byte MD5 digest wrapper. Constructors accept no args, string, or bytes. Public methods include `readFields`, static `read`, `write`, `set`, `getDigest`, several static `digest` overloads, `halfDigest`, `quarterDigest`, equality/hash/compare/string methods, `setDigest(String)`, and constant `MD5_LEN`. `MD5Hash.Comparator` provides optimized raw comparison.

`MultipleIOException` extends `IOException` and groups multiple exceptions. It exposes `getExceptions()` and static `createIOException(List)`, which likely returns null/single/multiple exception forms depending on list size.

`NullWritable` implements `WritableComparable` as a singleton no-data value. It exposes static `get()`, `toString`, `hashCode`, `compareTo`, `equals`, `readFields`, and `write`. `NullWritable.Comparator` provides raw comparison.

`ObjectWritable` implements `Writable` and `Configurable` for serializing arbitrary objects with a declared class. Constructors accept no args, instance, or declared class plus instance. Methods include `get`, `getDeclaredClass`, `set`, `toString`, `readFields`, `write`, static `writeObject`, static `readObject` overloads, and configuration methods. It is flexible but documentation in `GenericWritable` indicates it carries class declarations in each key/value pair.

`RawComparator` extends `java.util.Comparator` and adds raw byte-array `compare(byte[], int, int, byte[], int, int)`. It is the bridge for sort/merge code that can compare serialized keys without deserializing them.

`SequenceFile` is a central binary key/value file format. Visible static methods include `getCompressionType(Configuration)`, `setCompressionType(Configuration, CompressionType)`, and many `createWriter` overloads accepting filesystem/path or raw `FSDataOutputStream`, key/value classes, buffer size, replication, block size, compression type, compression codec, progress callback, and `Metadata`. Field `SYNC_INTERVAL` controls sync-marker spacing. The class documentation describes three formats: uncompressed records, record-compressed values, and block-compressed groups of key/value lengths and data. All share a header with `SEQ` magic/version, key class, value class, compression flags, optional codec, metadata, and sync marker.

`SequenceFile.CompressionType` is an enum with `NONE`, `RECORD`, and `BLOCK`, plus generated enum methods. `NONE` stores records uncompressed, `RECORD` compresses values individually, and `BLOCK` compresses sequences of records together.

`SequenceFile.Metadata` implements `Writable` and stores `Text` name/value pairs in a `TreeMap`. It exposes constructors, `get(Text)`, `set(Text, Text)`, `getMetadata()`, `write`, `readFields`, `equals`, `hashCode`, and `toString`.

`SequenceFile.Reader` starts near the end of the chunk. It implements `java.io.Closeable`, has a constructor `(FileSystem, Path, Configuration)`, protected `openFile(FileSystem, Path, int, long)`, synchronized `close`, class-name/class getters for keys and values, compression metadata getters, `getMetadata`, and the first `getCurrentValue(Writable)` method. The chunk ends in the second `getCurrentValue()` method returning `Object`, so its parameters, exceptions, and documentation continue in the next chunk.

## Control Flow and Behavioral Contracts

Filesystem adapters in this chunk follow the `FileSystem` lifecycle: `initialize(URI, Configuration)` binds an instance to a scheme/authority and configuration, path methods resolve relative paths through a working directory, metadata calls return `FileStatus`, and data calls return `FSDataInputStream`/`FSDataOutputStream`. Remote implementations add protocol-specific behavior: FTP create streams must be closed before other API calls; S3 block filesystems persist metadata and blocks separately; native S3 stores files directly as objects; KFS exposes lock/release and block-location methods.

Stream behavior is split by capability interfaces. `Seekable` streams must maintain a current read position, reject invalid seeks as documented, and support optional source switching through `seekToNewSource`. `Syncable` outputs expose explicit durability synchronization. `FTPInputStream` adapts these contracts to a remote stream, so position tracking and close semantics are important even though the implementation body is absent.

Trash flow moves a requested path under `.Trash/current` while preserving original path structure. `checkpoint()` snapshots current trash, `expunge()` removes old checkpoints, and `getEmptier()` returns a periodic runnable for system-level cleanup. The design intentionally avoids needing full trash enumeration, filesystem date support, or synchronized clocks.

Permission flow models Unix-style permissions at three levels. `FsAction` performs action algebra; `FsPermission` packs/unpacks actions to a `short`, applies umasks, and serializes permission bits; `PermissionStatus` adds owner and group and serializes the full permission identity. These objects feed filesystem create/status APIs and persistent metadata formats.

The old S3 block filesystem flow separates path metadata from block data. `S3FileSystem` calls a `FileSystemStore` to store/retrieve `INode` objects for paths and `Block` objects for file contents. `INode.serialize`/`deserialize` define persistent metadata encoding. `MigrationTool` walks metadata and rewrites block metadata for version migration without rewriting data files. `VersionMismatchException` is the failure path when persisted metadata is incompatible with the running code.

Native S3 flow exposes normal Hadoop `FileSystem` operations but maps them to native S3 object operations. Listing has explicit remote-call scaling costs, and rename/delete/mkdir semantics are compatibility risks because object stores do not share POSIX directory primitives.

Shell command flow starts with `CommandFormat.parse`, which consumes options and validates argument counts. A `Command` subclass receives paths and implements `run(Path)`, while `runAll()` loops over supplied path arguments and returns a process-style status. `Count` matches the `-count` command name and prints or returns content summaries through `run(Path)`.

HTTP server flow constructs Jetty listener/context state, adds default webapps/servlets, maps filters to contexts, exposes daemon attributes, optionally adds SSL connectors, and starts/stops/joins the server. `FilterContainer` lets daemon code register local or global filters without depending on Jetty implementation details. `StackServlet.doGet` reads JVM thread stacks and writes/logs them for diagnostics.

Writable primitive flow is consistent across wrappers: callers instantiate or reuse a mutable wrapper, call `set`, serialize with `write(DataOutput)`, deserialize with `readFields(DataInput)`, and compare either deserialized objects or serialized byte arrays through nested comparators. This pattern is central to MapReduce sort/shuffle performance.

Buffer flow reuses in-memory byte arrays to avoid allocations. `DataOutputBuffer` and `OutputBuffer` accumulate serialized bytes and expose backing arrays plus logical length. `DataInputBuffer` and `InputBuffer` reset over byte arrays and expose current position/length. These are integration points for serializers, comparators, and file readers that need high-throughput byte manipulation.

Map file flow stores sorted key/value records in a `data` SequenceFile and a sampled in-memory `index` SequenceFile. Writers append keys in sorted order and periodically write index entries based on an index interval. Readers load the index, seek near the target key, then scan the data file to find exact or closest keys. `fix` rebuilds the index from the data file when needed. `ArrayFile` specializes this by using implicit dense integer keys; `BloomMapFile` adds a Bloom filter before exact lookup to avoid unnecessary reads for absent keys.

`MapWritable` and `AbstractMapWritable` flow serializes heterogeneous `Writable` maps by assigning per-instance byte IDs to classes and writing both class-id metadata and entries. `GenericWritable` uses a fixed type table from `getTypes()` to serialize a compact tag plus the selected value. `ObjectWritable` serializes with declared class metadata for more dynamic use cases.

`SequenceFile` writer creation flow selects a writer implementation from `CompressionType`: no compression, per-record value compression, or block compression. Static `createWriter` overloads normalize caller options such as filesystem/path versus existing output stream, buffer/replication/block size, compression codec, progress callback, and metadata. The reader flow opens an `FSDataInputStream`, parses the common header, exposes key/value classes and compression state, and reads records according to the stored format. Sync markers support resynchronization for split readers and corruption recovery.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API compatibility data. It does not carry implementation bodies, but it fixes public signatures and documentation for Hadoop 0.20.1.

Filesystem classes persist data and metadata through their backing stores. `RawLocalFileSystem` mutates local files, permissions, owners, working-directory state, and local-output staging paths. FTP, KFS, S3, and native S3 implementations mutate remote services. The visible APIs declare `IOException` on almost all remote and filesystem operations, making failure a normal part of the contract.

Working directories are mutable instance state for `FTPFileSystem`, `KosmosFileSystem`, `S3FileSystem`, `NativeS3FileSystem`, and `RawLocalFileSystem`. Configuration supplied through `initialize` or constructors affects buffer sizes, umasks, credentials, server ports, filesystem stores, and serialization behavior. `Trash` extends `Configured`, so its behavior is configuration-driven and persists trash entries in filesystem paths under user home directories.

Permission and status objects persist through `Writable` serialization. `FsPermission.toShort` and `fromShort`, `PermissionStatus.write/read`, and `INode.serialize/deserialize` are compatibility-sensitive because old metadata and file status records must remain readable.

S3 block filesystem state is split between path `INode`s and content `Block`s. Migration rewrites metadata but intentionally avoids data-file writes. Native S3 state is external object-store state, and list/rename/delete operations may have side effects and consistency behavior determined by S3.

HTTP server state is mutable and long-lived: Jetty `Server`, `Connector`, `WebAppContext`, context maps, filter-name lists, servlet mappings, attributes, thread settings, and SSL listener state. `start` begins asynchronous server work, `stop` tears it down, and `join` blocks on server lifecycle.

Most `org.apache.hadoop.io` value wrappers are mutable but compact. Reusing instances across reads is expected; callers must copy values when retaining them beyond the next read. Comparators operate on raw serialized buffers and must preserve byte layout expectations. `DataOutputBuffer`/`DataInputBuffer` expose backing arrays, so callers can accidentally observe stale capacity bytes beyond logical length.

File-format classes persist on-disk structures. `MapFile` persists directories containing `data` and `index`. `BloomMapFile` adds a Bloom filter file. `SequenceFile` persists headers, class names, compression flags/codecs, metadata, sync markers, record lengths, keys, values, and compressed blocks. These formats are high-risk compatibility contracts for MapReduce inputs, outputs, and intermediate data.

`DefaultStringifier.store/load` and array variants persist serialized objects into `Configuration` string values. This crosses process boundaries and job submission boundaries, so the string encoding and target class handling matter.

## Dependencies and Integration Points

Filesystem APIs depend on `org.apache.hadoop.fs.Path`, `FileStatus`, `BlockLocation`, `FSDataInputStream`, `FSDataOutputStream`, `FileSystem.Statistics`, `Progressable`, `Configuration`, and permission classes. Remote filesystem implementations also depend on protocol libraries such as Apache Commons Net FTP, KFS client classes, JetS3t/AWS-facing store abstractions, Java `URI`, and Java IO exceptions.

Permission APIs integrate with `Configuration` through umask settings and with `Writable` serialization through `DataInput`/`DataOutput`. They also integrate with `FileStatus`, create/mkdir signatures, and owner/group metadata.

S3 APIs integrate `FileSystem`, `FileSystemStore`, `INode`, `Block`, credentials parsing, version checks, migration tooling, and `Tool`/`Configured`. They are also integration points with tests through `purge()` and diagnostics through `dump()`.

Shell APIs integrate `Configuration`, `Path`, and command-line parsing. They are part of the user-facing `hadoop fs` command family.

HTTP APIs depend on Jetty (`Server`, `Connector`, `WebAppContext`), servlet APIs (`HttpServlet`, request/response, `ServletException`), Java collections/maps, SSL listener setup, daemon logging through Commons Logging, and Hadoop `Configuration`. They support daemon web UIs and diagnostic endpoints.

`org.apache.hadoop.io` depends on Java IO (`DataInput`, `DataOutput`, streams, `Closeable`), Java collections (`Map`, `Set`, `Collection`, `TreeMap`, `List`), Hadoop `Configuration`, Hadoop filesystem paths and filesystems for file formats, compression codecs, `Progressable`, `Writable`, `WritableComparable`, and `WritableComparator`. `SequenceFile` and `MapFile` are directly consumed by old and new MapReduce input/output formats, sorters, partitioners, and job data pipelines.

`RawComparator` and primitive comparators are sort/shuffle integration points. They allow serialized-key comparisons without deserialization, which affects correctness and performance of MapReduce sort order.

## Risks and Compatibility Notes

This chunk starts and ends mid-class. The previous chunk is needed for the full `RawLocalFileSystem` class, and the next chunk is needed for the rest of `SequenceFile.Reader` and later nested SequenceFile classes. Merge/reconciliation should preserve these partial boundaries.

Because this is generated API XML, it does not specify null handling, retry behavior, thread safety beyond `synchronized` flags, exact exceptions thrown for invalid arguments, or remote-service consistency behavior. Implementation source is required for those details.

Filesystem compatibility risks include path qualification, relative path handling, working-directory mutation, recursive delete semantics, rename behavior across filesystems or object stores, create overwrite behavior, permission application, owner/group changes, and stream close/sync behavior. FTP's create-stream blocking warning is especially important: callers that interleave operations before closing the stream can deadlock or stall.

S3 block and native S3 filesystems have different persistence models. Confusing them can strand data or make files unreadable by other tools. Block-based metadata versioning and migration must remain compatible with stored `INode` and `Block` encodings. Native S3 directory listings are remote-call heavy and may expose eventual-consistency or pagination issues.

Permission risks include preserving Unix symbolic parsing, `short` bit layout, umask configuration keys/defaults, immutable factory behavior, and owner/group serialization order. Changing any of these can break persisted filesystem metadata or wire compatibility.

HTTP server risks include servlet/filter mapping order, global versus context-local filters, SSL connector setup, dynamic port selection, default `/logs/` and `/static/` paths, and lifecycle ordering. Exposing stack traces is useful diagnostically but sensitive operationally; access control depends on filters or deployment context outside this XML.

Writable primitive wrappers are small but format-sensitive. Serialized byte order, comparator raw-byte offsets, equality/hash semantics, and mutable reuse behavior must stay stable. Deprecated `BytesWritable.get()` and `getSize()` remain public compatibility surface.

Buffer APIs expose backing arrays and logical lengths separately. Tests and callers must use `getLength()` rather than array capacity. Resets should not leak previous data through logical reads, but stale capacity bytes may remain visible if callers ignore length.

`AbstractMapWritable` uses byte class IDs with a documented 1-127 range. Exceeding that type count, changing ID assignment order, or failing to serialize class maps can corrupt heterogeneous map reads.

`MapFile` depends on sorted append order and an in-memory index. Out-of-order appends, changed comparator semantics, corrupted indexes, or large keys can cause lookup failures or memory pressure. `fix` is a recovery path but must avoid modifying data in dry-run mode.

`BloomMapFile` can return false positives by design but should not return false negatives when the Bloom file and data are consistent. Missing or stale Bloom filter files could degrade performance or correctness depending on implementation.

`SequenceFile` is one of Hadoop's most compatibility-sensitive formats. Header shape, class names, compression flags, codec class names, metadata serialization, sync marker interval, record length encoding, block compression layout, and zero-compressed integer lengths must remain readable across versions. Raw `createWriter` overloads that accept an existing stream shift close/flush responsibility to the caller.

`DefaultStringifier` and `ObjectWritable` can persist class names or serialized bytes into configurations and files. Class renames, classloader differences, or configuration not being propagated to nested `Configurable` objects can break deserialization.

## Test Signals

JDiff-level validation should confirm the XML remains well formed across the chunk boundaries, preserves all package/class/interface markers listed here, and keeps signatures, parameter order, declared exceptions, field names/types, modifiers, deprecation notes, and Javadoc text stable.

Filesystem tests should cover `RawLocalFileSystem`, FTP, KFS, S3, and native S3 create/open/append behavior, recursive and non-recursive delete, rename into existing paths and directories, list status, get file status, working directory changes, home directory resolution, local output staging, permission and owner changes, stream close behavior, and expected unsupported-operation failures for append where documented.

`Seekable` and stream tests should cover seeking to zero/current/end, seeking past EOF, position tracking after reads/skips, `seekToNewSource` return behavior, close idempotence or failure behavior, mark/reset support in `FTPInputStream`, and statistics updates.

Trash tests should cover disabled trash, moving files/directories to trash, rejecting paths already in trash, preserving original path structure, checkpoint creation, expunge of old checkpoints, current-checkpoint rotation, `getEmptier` behavior, and permission/superuser expectations.

Permission tests should cover every `FsAction` algebra operation, symbolic permission parsing, short round trips, umask application and configuration storage, immutable factory behavior, `PermissionStatus` serialization, null/empty owner or group handling if supported, and access-control exception construction.

S3 tests should cover `FileSystemStore` version checks, `INode` serialization/deserialization for files and directories, block store/retrieve/delete, shallow versus deep listings, migration metadata rewrite without block rewrite, credential extraction from URI and configuration, version mismatch errors, native S3 listing pagination/cost behavior, object rename/delete semantics, and old block-based versus native S3 incompatibility boundaries.

Shell tests should cover command option parsing, min/max argument validation, unknown options, repeated options, `Command.runAll` exit codes across multiple paths, and `Count` output for files, directories, quotas, missing paths, and permission failures.

HTTP tests should cover construction with explicit and dynamic ports, default contexts and servlets, attribute set/get, servlet registration, internal servlet behavior, context-local and global filters, filter path mappings, thread settings, SSL listener overloads, start/stop/join lifecycle, port reporting, and `StackServlet` response content plus logging.

Writable tests should cover primitive wrapper serialization round trips, raw comparator ordering versus object comparator ordering, decreasing long comparator behavior, equality/hash consistency, string conversion, boundary values, NaN/negative-zero behavior for float/double if implementation distinguishes it, and deprecated `BytesWritable` getters.

Buffer tests should cover reset over full and partial arrays, position and length reporting, writing from `DataInput` or `InputStream`, `writeTo`, reset reuse, and ensuring consumers respect logical length rather than capacity.

`ArrayWritable`, `MapWritable`, `GenericWritable`, and `ObjectWritable` tests should cover heterogeneous map serialization, class ID table round trips, copy constructors, configuration propagation, unsupported wrapped types, fixed type tags, classloader-sensitive reads, and behavior when more than 127 classes are inserted into an `AbstractMapWritable` instance.

`MapFile`, `ArrayFile`, and `BloomMapFile` tests should cover sorted append, out-of-order append rejection, index interval configuration, index loading, `seek`, `next`, `get`, `getClosest` before/after behavior, `midKey`, `finalKey`, close behavior, rename/delete helpers, index repair dry-run and real modes, dense array reads by ordinal, Bloom false-positive tolerant lookup, missing-key fast path, and Bloom file persistence.

`MD5Hash`, `MultipleIOException`, and `NullWritable` tests should cover digest overloads, hex/string parsing, half/quarter digest values, raw comparator ordering, grouped exception creation for zero/one/many inputs, and singleton serialization with `NullWritable`.

`IOUtils` tests should cover copy with explicit buffer sizes, configuration-driven buffer sizes, close and non-close modes, readFully EOF behavior, skipFully EOF behavior, cleanup ignoring close failures with and without a log, socket close failure handling, and `NullOutputStream` byte and buffer writes.

`SequenceFile` tests should cover every compression type, codec selection, metadata write/read, raw stream writer overloads, filesystem/path writer overloads, buffer/replication/block-size options, sync interval and sync marker behavior, reader class-name/class getters, compression flag getters, codec getter, current-value APIs, and split/resync behavior across uncompressed, record-compressed, and block-compressed files.
