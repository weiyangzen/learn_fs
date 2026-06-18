# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 12463-18779

## Scope

This chunk is a JDiff API description for Hadoop Common 0.18.1. It is generated API metadata, not executable Java source. It records public API names, inheritance, visibility, method parameters, checked exceptions, deprecation state, fields, and Javadoc-derived contracts.

The slice begins inside `org.apache.hadoop.fs.permission`, covering the tail of `FsAction` plus `FsPermission` and `PermissionStatus`. It then covers the old block-based S3 filesystem API in `org.apache.hadoop.fs.s3`, the native-object S3 filesystem entry point in `org.apache.hadoop.fs.s3native`, the early filesystem shell command helpers in `org.apache.hadoop.fs.shell`, and a large portion of `org.apache.hadoop.io`. The `org.apache.hadoop.io` part starts at `AbstractMapWritable`, includes many core `Writable` primitives, buffers, stringification, `MapFile`, `SequenceFile`, `SetFile`, `SortedMapWritable`, and `Text`, and ends inside the deprecated `UTF8` class.

Because this is API XML, the control-flow notes below describe documented public contracts, object lifecycle, serialization shape, and extension points inferred from signatures and Javadocs. Adjacent chunks are required for complete package coverage, especially for the beginning of `FsAction`, any nested enum constants omitted by JDiff presentation, and the tail of `UTF8`.

## Purpose

The chunk captures several foundational Hadoop Common APIs from the 0.18.1 era:

- Permission model value types for filesystem metadata: `FsAction`, `FsPermission`, and `PermissionStatus`.
- Two S3 filesystem models: a Hadoop-specific block/inode store (`org.apache.hadoop.fs.s3.S3FileSystem`) and a native S3 object store filesystem (`org.apache.hadoop.fs.s3native.NativeS3FileSystem`).
- Early `fs` shell command support for command dispatch, option parsing, and the `-count` command.
- Hadoop's core binary serialization and file container APIs: `Writable`, `WritableComparable`, raw comparators, reusable input/output buffers, arrays/maps of writables, primitive writable wrappers, `ObjectWritable`, `GenericWritable`, `DefaultStringifier`, `MapFile`, `SequenceFile`, and `Text`.

These APIs are central compatibility surfaces. The permission classes affect filesystem metadata persistence. The S3 classes define filesystem behavior over eventually remote object storage. The IO classes define on-disk file formats, MapReduce key/value serialization, sort order, raw comparator behavior, and configuration persistence of serialized objects.

## Important APIs, Types, and Functions

### Filesystem Permissions

`FsAction` is a public final enum for filesystem actions such as read and write. The visible API includes enum helpers `values()` and `valueOf(String)`, lattice-style operators `implies(FsAction)`, `and(FsAction)`, `or(FsAction)`, and `not()`, and public final fields `INDEX` and `SYMBOL` for octal and symbolic representations. It is the low-level action algebra used by permission bits.

`FsPermission` is a public mutable `Writable` value object for file and directory permission bits. It can be constructed from user/group/other `FsAction` values, from a `short` mode, or by copy. Important methods include `createImmutable(short)`, `fromShort(short)`, `toShort()`, `read(DataInput)`, `write(DataOutput)`, `readFields(DataInput)`, `getUserAction()`, `getGroupAction()`, `getOtherAction()`, `applyUMask(FsPermission)`, `getUMask(Configuration)`, `setUMask(Configuration, FsPermission)`, `getDefault()`, and `valueOf(String)` for Unix symbolic permissions such as `-rw-rw-rw-`. Public static fields `UMASK_LABEL` and `DEFAULT_UMASK` expose the configuration key and default mask.

`PermissionStatus` stores ownership and permission metadata. It implements `Writable`, is constructible from user name, group name, and `FsPermission`, and exposes immutable construction through `createImmutable(String, String, FsPermission)`. Accessors return user, group, and permission. `applyUMask(FsPermission)` delegates permission masking to `FsPermission`. It supports instance and static serialization helpers: `readFields(DataInput)`, `write(DataOutput)`, static `read(DataInput)`, and static `write(DataOutput, String, String, FsPermission)`.

### Block-Based S3 Filesystem

`org.apache.hadoop.fs.s3.Block` is a simple metadata value for data blocks stored by a `FileSystemStore`. It has an id and length, exposed through `getId()`, `getLength()`, and `toString()`.

`FileSystemStore` is the persistence abstraction behind the old Hadoop block-based S3 filesystem. It initializes from a `URI` and `Configuration`, exposes `getVersion()`, stores/retrieves/deletes `INode` and `Block` objects, checks inode/block existence, retrieves a block into a local `File` from a byte-range start, lists direct and deep subpaths, and includes test/diagnostic operations `purge()` and `dump()`.

`INode` holds file metadata for the block-based S3 layer: a file type and a list of `Block` pointers. It exposes `getBlocks()`, `getFileType()`, `isDirectory()`, `isFile()`, `getSerializedLength()`, `serialize()`, and static `deserialize(InputStream)`. Public static fields include `FILE_TYPES` and `DIRECTORY_INODE`. The API clearly separates metadata objects from data blocks.

`MigrationTool` is a `Configured` `Tool` for migrating old S3 filesystem data versions. Its Javadoc says migration rewrites block metadata and does not touch data files. Public entry points are `main(String[])`, `run(String[])`, and `initialize(URI)`.

`S3Credentials` extracts AWS credentials from a filesystem URI or `Configuration`. It has `initialize(URI, Configuration)`, `getAccessKey()`, and `getSecretAccessKey()`, with `IllegalArgumentException` documented when credentials cannot be determined.

`S3Exception` is an unchecked wrapper for Amazon S3 communication problems. `S3FileSystemException` is a checked fatal exception for `S3FileSystem`, and `VersionMismatchException` is raised when stored S3 filesystem data has an unreadable or incompatible version.

`S3FileSystem` extends `FileSystem` and implements Hadoop's block-based S3 filesystem. It can be constructed with the default store or an injected `FileSystemStore`, which is an important test seam. Public filesystem operations include `initialize(URI, Configuration)`, `getUri()`, deprecated-style `getName()`, working directory getters/setters, `mkdirs(Path, FsPermission)`, `isFile(Path)`, `listStatus(Path)`, `create(Path, FsPermission, boolean, int, short, long, Progressable)`, `open(Path, int)`, `rename(Path, Path)`, both old and recursive `delete` forms, and `getFileStatus(Path)`. `append()` is documented as unsupported, and permission parameters are documented as currently ignored.

### Native S3 Filesystem

`NativeS3FileSystem` extends `FileSystem` but stores files in their native S3 object form so other S3 tools can read them. It can be constructed with an injected `NativeFileSystemStore`, and its public operations mirror core filesystem behavior: `initialize`, `create`, `open`, `delete`, recursive `delete`, `getFileStatus`, `getUri`, `listStatus`, `mkdirs`, `rename`, `setWorkingDirectory`, and `getWorkingDirectory`. `append()` is unsupported. The public static `LOG` field uses Commons Logging.

The `listStatus(Path)` Javadoc is performance-significant: listing a file makes one S3 call, while listing a directory may make up to roughly `(n / 1000) + 2` S3 calls for `n` direct child files/directories. That exposes S3 pagination and cost/latency directly through the API contract.

### Filesystem Shell Helpers

`Command` is an abstract base for filesystem shell commands. It keeps protected `fs` and `args` state, requires `getCommandName()` and protected `run(Path)`, and provides `runAll()` to execute the command over every source path, returning `0` on success and `-1` on failure.

`CommandFormat` parses command arguments. Its constructor takes a command name, minimum/maximum parameter counts, and option names. `parse(String[], int)` returns non-option parameters from a starting position, and `getOpt(String)` reports whether an option was set.

`Count` extends `Command` for the `-count` shell command. It exposes static constants `NAME`, `USAGE`, and `DESCRIPTION`, static `matches(String)`, command name lookup, and protected path execution. The Javadoc says it counts directories, files, bytes, quota, and remaining quota.

### Core Writable Containers and Primitive Writables

`AbstractMapWritable` is an abstract `Writable` and `Configurable` base for `MapWritable` and `SortedMapWritable`. It keeps a per-instance class-id map rather than a static map, supporting nested map writables. Class ids range from 1 to 127, so a map instance can encode at most 127 distinct classes. Protected methods `addToMap(Class)`, `getClass(byte)`, `getId(Class)`, and synchronized `copy(Writable)` manage the registry. It also serializes/deserializes the class map and carries a `Configuration`.

`ArrayWritable` is a homogeneous writable array wrapper. It stores a value class, supports construction from a writable class, writable array, or `String[]`, and exposes `getValueClass()`, `toStrings()`, `toArray()`, `set(Writable[])`, `get()`, `readFields()`, and `write()`.

`TwoDArrayWritable` is the 2D version for `Writable[][]`, with class-based construction, `set`, `get`, `toArray`, and standard writable serialization.

The primitive writable wrappers in this chunk include `BooleanWritable`, `ByteWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, and `DoubleWritable`. Each implements `WritableComparable`, provides default and value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`. Their nested `Comparator` classes extend `WritableComparator` and compare serialized byte forms directly. `LongWritable` also exposes a `DecreasingComparator`.

`BytesWritable` is a resizable byte sequence usable as a key or value. It distinguishes logical size from backing capacity with `getSize()`, `setSize(int)`, `getCapacity()`, and `setCapacity(int)`. `get()` returns the backing bytes but only the range `0..getSize()-1` is valid. It supports copying from another `BytesWritable` or byte range, writable serialization, bytewise comparison, MD5-based hash behavior, equality, and hex-pair `toString()`. Its comparator is optimized for serialized bytes.

`NullWritable` is a singleton writable with no data. `get()` returns the single instance, serialization reads/writes no content, comparison is trivial, and its comparator is optimized for the empty serialized form.

`MD5Hash` is a `WritableComparable` wrapper around 16-byte MD5 digests. It can be constructed empty, from hex, or from raw bytes. It supports static and instance serialization, copying from another hash, raw digest access, digest construction from byte arrays, byte ranges, strings, and deprecated `UTF8`, plus `halfDigest()`, `quarterDigest()`, equality, ordering, hex conversion, and `setDigest(String)`. Public `MD5_LEN` defines the digest length, and the nested comparator compares serialized digests.

`MultipleIOException` aggregates multiple `IOException` instances. `getExceptions()` returns underlying exceptions and static `createIOException(List<IOException>)` creates a convenient wrapper or single exception.

### Buffers, Compression, Stringification, and Generic Object Wrappers

`CompressedWritable` is an abstract base for writables that store their serialized data compressed and inflate lazily. `readFields(DataInput)` and `write(DataOutput)` are final; subclasses implement `readFieldsCompressed(DataInput)` and `writeCompressed(DataOutput)`. Methods that access fields must call `ensureInflated()`.

`DataInputBuffer` is a reusable in-memory `DataInputStream`. It can be reset to a byte array and length or byte array, start, and length; accessors expose backing data, current position, and input length. Its purpose is avoiding repeated `DataInputStream` and `ByteArrayInputStream` allocation.

`DataOutputBuffer` is the writable counterpart over an in-memory buffer. Constructors support default and initial size. `getData()` returns the backing bytes valid only through `getLength()`. `reset()` clears the buffer and returns itself. `write(DataInput, int)` copies bytes directly from a `DataInput`.

`InputBuffer` and `OutputBuffer` are stream-level reusable buffers. `InputBuffer` extends `FilterInputStream` and resets over a byte array segment; `OutputBuffer` extends `FilterOutputStream`, exposes backing data/length, reset, and write support.

`DefaultStringifier<T>` implements `Stringifier<T>` using Hadoop serialization and base64. It obtains `Serializer` and `Deserializer` objects from `SerializationFactory`. Instance methods convert objects to/from strings and close resources. Static helpers `store`, `load`, `storeArray`, and `loadArray` persist serialized objects or arrays in `Configuration` keys. `storeArray` explicitly throws `IndexOutOfBoundsException` for an empty array.

`Stringifier<T>` is the interface for `toString(T)`, `fromString(String)`, and `close()`.

`GenericWritable` is an efficient wrapper for one of a fixed set of writable classes. Subclasses implement `getTypes()` to return the allowed classes. The serialized form stores a compact type id rather than writing a class name for every record. It implements `Configurable` and passes configuration to wrapped objects that are configurable before deserialization.

`ObjectWritable` is the general-purpose object wrapper. It stores a declared class and instance, supports `get()`, `getDeclaredClass()`, `set(Object)`, writable serialization, static `writeObject()` and `readObject()` helpers, and configuration propagation. Compared with `GenericWritable`, it is more flexible but more expensive because class declarations are serialized.

`RawComparator` extends the object comparator contract with `compare(byte[], int, int, byte[], int, int)` so Hadoop can compare serialized keys without deserializing them.

The deprecated `Closeable` interface simply extends `java.io.Closeable` and is marked "use java.io.Closeable".

### MapFile, ArrayFile, and SetFile

`MapFile` is a file-based sorted map from writable-comparable keys to writable values. Its storage is a directory containing a `data` file with all records and an `index` file containing a fraction of keys. Public constants `INDEX_FILE_NAME` and `DATA_FILE_NAME` expose those names. Static methods support renaming, deleting, command-line entry, and `fix(FileSystem, Path, Class, Class, boolean, Configuration)` to recreate a corrupt index and return the number of valid entries or `-1` if no repair is needed.

`MapFile.Reader` provides synchronized access to an existing map. It can be constructed with a filesystem/path string and configuration, or with a custom `WritableComparator`. Protected construction and `createDataFileReader()` let subclasses defer opening streams and specialize the `SequenceFile.Reader`. Important operations include `reset()`, `midKey()`, `finalKey(WritableComparable)`, `seek(WritableComparable)`, `next(WritableComparable, Writable)`, `get(WritableComparable, Writable)`, two `getClosest()` forms, and `close()`.

`MapFile.Writer` writes sorted map files. It has constructor overloads for key/value classes or a comparator, compression type, optional compression codec, and optional `Progressable`. It exposes instance and static `setIndexInterval`, `getIndexInterval()`, synchronized `append(WritableComparable, Writable)`, and synchronized `close()`. `append` requires each key to be greater than or equal to the previous key.

`ArrayFile` is a dense file-backed mapping from integer positions to values. Its `Reader` extends `MapFile.Reader` and adds `seek(long)`, `next(Writable)`, `key()`, and `get(long, Writable)`. Its `Writer` extends `MapFile.Writer` and appends values with implicit long keys.

`SetFile` is a file-backed sorted set built on `MapFile`. Its `Reader` exposes `seek(WritableComparable)`, `next(WritableComparable)`, and `get(WritableComparable)`. Its `Writer` appends keys and stores `NullWritable`-style values internally.

### MapWritable and SortedMapWritable

`MapWritable` extends `AbstractMapWritable` and implements `Map<Writable, Writable>`. It provides default and copy constructors, standard map operations (`clear`, `containsKey`, `containsValue`, `entrySet`, `get`, `isEmpty`, `keySet`, `put`, `putAll`, `remove`, `size`, `values`), plus `write` and `readFields` that include both the class registry and map entries.

`SortedMapWritable` is the sorted-key counterpart, extending `AbstractMapWritable` and implementing sorted map semantics over `WritableComparable` keys. It exposes `comparator()`, `firstKey()`, `lastKey()`, `headMap()`, `subMap()`, `tailMap()`, standard mutable map operations, and writable serialization.

### SequenceFile

`SequenceFile` is the key/value container format used heavily by Hadoop jobs and internal tooling. The top-level class exposes compression configuration helpers `getCompressionType(Configuration)` and `setCompressionType(Configuration, CompressionType)`, multiple overloaded `createWriter()` factories, and public `SYNC_INTERVAL`.

The Javadoc describes a common header: magic bytes `SEQ` plus version, key class name, value class name, compression flags, optional compression codec, metadata, and a sync marker. It documents three record formats:

- Uncompressed: header, then records with record length, key length, key, value, and periodic sync markers.
- Record-compressed: same structure except values are compressed.
- Block-compressed: record blocks contain compressed key lengths, keys, value lengths, and values, with lengths encoded as zero-compressed integers.

`SequenceFile.CompressionType` is a public enum for compression modes used by `SequenceFile.Writer`.

`SequenceFile.Metadata` is a `Writable` map of `Text` keys to `Text` values. It supports default and `TreeMap<Text, Text>` construction, `get(Text)`, `set(Text, Text)`, metadata map access, writable serialization, equality, hash, and string conversion.

`SequenceFile.Reader` opens sequence files from `FileSystem`, `Path`, and `Configuration`. It exposes class-name and class-object getters for keys and values, compression flags and codec, metadata, close, synchronized typed iteration (`next(Writable)`, `next(Writable, Writable)`, `getCurrentValue(...)`), object-style `next(Object)`, raw iteration (`createValueBytes()`, `nextRaw`, `nextRawKey`, `nextRawValue`), `seek(long)`, `sync(long)`, `syncSeen()`, `getPosition()`, and `toString()`. `seek(long)` requires a position previously returned by `Writer.getLength()`; arbitrary positioning should use `sync(long)`.

`SequenceFile.ValueBytes` represents raw sequence-file values. It can write uncompressed bytes, write compressed bytes without recompressing uncompressed data, and report data size.

`SequenceFile.Writer` is a closeable writer with constructors for filesystem, configuration, path, key/value classes, optional progress, metadata, and replication/block-size parameters. It exposes key/value class and codec getters, `sync()`, `close()`, typed `append(Object, Object)`, `append(Writable, Writable)`, `appendRaw(byte[], int, int, ValueBytes)`, and `getLength()`. The public serializer fields `keySerializer`, `uncompressedValSerializer`, and `compressedValSerializer` reveal the serialization pipeline used for keys and values.

`SequenceFile.Sorter` sorts and merges sequence files. Constructors accept filesystem, key/value classes or a `RawComparator`, and configuration. Tunables include merge factor, memory bytes, and `Progressable`. Public workflows include sorting one or many input files, sorting and returning a raw iterator, merging by path arrays or `SegmentDescriptor` lists, cloning file attributes such as compression into an output writer, writing iterator records to a writer, and merging into an output file. Its Javadoc warns that key `readFields` implementations must avoid allocation for best performance.

`SequenceFile.Sorter.RawKeyValueIterator` iterates raw sorted key/value pairs and exposes current key as `DataOutputBuffer`, current value as `ValueBytes`, `next()`, `close()`, and `Progress`.

`SequenceFile.Sorter.SegmentDescriptor` describes a file segment by offset, length, and path. It is comparable and supports sync checks, preserving or deleting input, raw key/value iteration, stored key access, and cleanup. Default cleanup closes the file handle and deletes the file, but subclasses can override cleanup.

### Text and Deprecated UTF8

`Text` is Hadoop's standard UTF-8 string type. It implements writable-comparable behavior and stores raw UTF-8 bytes with an integer length encoded through zero-compressed format. Constructors accept empty, `String`, another `Text`, or byte array. It exposes raw bytes and length, byte-position `charAt(int)` returning Unicode scalar values or `-1`, `find(String)` and `find(String, int)` without converting the backing buffer to `String`, several `set` overloads, byte-range `append`, `clear`, `toString`, `readFields`, static `skip(DataInput)`, `write`, bytewise UTF-8 ordering, equality, hash, decoding/encoding helpers with optional malformed-input replacement, static `readString`/`writeString`, UTF-8 validation, `bytesToCodePoint(ByteBuffer)`, and `utf8Length(String)`.

`Text.Comparator` is a serialized-byte comparator optimized for `Text` keys.

`UTF8` is deprecated and explicitly replaced by `Text`. The visible portion includes empty, `String`, and copy constructors; `getBytes()`, `getLength()`, `set(String)`, `set(UTF8)`, `readFields(DataInput)`, static `skip(DataInput)`, and the beginning of `write(DataOutput)`. The chunk ends before the class is complete.

## Control Flow and Lifecycle

Permission construction flows from symbolic/octal/user-group-other input into `FsPermission` instances. `toShort()` and `fromShort()` define the compact numeric representation, while `write()`/`readFields()` carry that representation through Hadoop serialization. `PermissionStatus` composes user, group, and permission and provides static write/read helpers for metadata records.

The old block-based S3 filesystem flow is metadata-first. `S3FileSystem.initialize()` configures a `FileSystemStore`, validates or reads store version, and uses `INode` entries to represent directories and files. File content is split into `Block` records, while path operations manipulate `INode` mappings and block references. Creating a file writes blocks and then inode metadata; opening a file retrieves inode metadata and streams blocks; deleting removes inode and block records. `MigrationTool` walks this metadata layer and rewrites block metadata without rewriting data files.

The native S3 filesystem flow maps Hadoop paths to native S3 keys. It does not use the block/inode store documented in `org.apache.hadoop.fs.s3`; instead, it exposes `FileSystem` operations around native objects and directory markers or prefix listings. Listing cost scales with S3 pagination, and append remains unsupported.

Filesystem shell commands follow a simple lifecycle. A concrete `Command` is constructed with a `FileSystem` and command arguments. `CommandFormat` parses options and operands. `runAll()` iterates source paths, calling the subclass's `run(Path)` for each path and collapsing success/failure into a process-style exit code.

Writable values use the standard Hadoop pattern: a no-argument constructor creates an empty instance, `readFields(DataInput)` mutates it in place from serialized data, and `write(DataOutput)` writes the current state. Primitive writables write fixed-width values. Variable-length structures such as `BytesWritable`, arrays, maps, `Text`, and `SequenceFile` records write lengths followed by bytes or nested writable payloads.

`AbstractMapWritable`-based maps first maintain and serialize a per-instance class-id registry, then serialize entries by compact class ids plus each key/value's writable payload. During deserialization, the class registry must be read before entries so ids can be resolved to classes.

`GenericWritable` writes a compact type discriminator for one of the subclass-declared types, then delegates serialization to the wrapped writable. `ObjectWritable` writes enough class information to reconstruct arbitrary supported object types and can pass configuration to configurable deserialized objects.

`MapFile` write flow requires sorted appends. The writer writes all records to the data sequence file and periodically writes index entries according to `indexInterval`. Reader flow loads the index into memory, uses the comparator to seek near a target key, and then scans the data file for exact or closest matches. `fix()` reconstructs the index from the data file when the index is corrupt or missing.

`SequenceFile` write flow starts with the header and sync marker, then appends records in one of the three documented compression formats. `Writer.getLength()` exposes positions suitable for later `Reader.seek()`. Reader flow validates the header, instantiates key/value classes and compression codec, then supports typed iteration, raw iteration, seeking to known writer positions, and syncing forward from arbitrary byte offsets.

`SequenceFile.Sorter` performs external sort/merge. It reads raw records through `SequenceFile.Reader`, buffers records up to configured memory, sorts using a `RawComparator`, spills intermediate segment files, and merges segments with a configurable fan-in. `RawKeyValueIterator` and `SegmentDescriptor` keep sort/merge paths mostly in serialized form to avoid excessive object allocation.

`Text` operations are mostly byte-level. Searches, comparisons, validation, and some traversal avoid constructing Java `String` objects. Serialization writes a zero-compressed byte length and then raw UTF-8 bytes.

## State and Persistence Behavior

The XML file itself has no runtime state, but it documents persistent formats and stateful APIs.

`FsPermission` and `PermissionStatus` are persisted into filesystem metadata via Hadoop `Writable` serialization. Compatibility depends on stable short-mode encoding, stable `FsAction` indices/symbols, and stable serialization order for user, group, and permission.

`S3FileSystem` persists a Hadoop-specific layout in S3: version information, path-to-`INode` metadata, and block objects identified by `Block` ids. That layout is not the same as ordinary S3 object storage and requires version checks and migration tooling. A failed create, rename, delete, or migration can leave orphaned blocks, stale inodes, or mismatched metadata if store operations are not atomic.

`NativeS3FileSystem` persists native S3 objects. Its directory behavior is inferred from path listings and possible directory markers rather than a traditional hierarchical filesystem namespace. Working directory is client-side state. Remote object storage persistence and list behavior dominate correctness.

`Command` instances hold mutable `args` state and a fixed `FileSystem` reference. `CommandFormat` holds parsed option state after `parse()`.

Reusable buffers (`DataInputBuffer`, `DataOutputBuffer`, `InputBuffer`, `OutputBuffer`) expose backing arrays directly. Callers must honor valid lengths and positions; subsequent resets or writes mutate the same backing storage.

`BytesWritable` distinguishes capacity from logical size. The backing array may contain undefined bytes beyond `getSize()`, and callers using `get()` must not persist or compare beyond the valid range.

`CompressedWritable` stores compressed bytes until `ensureInflated()` is called. This makes copy-through cheap but means field access has hidden inflation side effects.

`DefaultStringifier` persists serialized, base64-encoded object state inside `Configuration` values. Deserialization depends on the configured `SerializationFactory`, the stored class, and class availability at load time.

`MapWritable` and `SortedMapWritable` persist both data and their per-instance class registry. The 127-class limit is an explicit compatibility and capacity boundary for complex nested maps.

`MapFile` persists as a directory with separate `data` and `index` files. The data file is authoritative for `fix()`, while index size and lookup memory use are controlled by index interval.

`SequenceFile` persists a binary container with magic/version, class names, compression metadata, file metadata, sync marker, and records. Compatibility depends on stable serializers, writable implementations, compression codecs, sync marker handling, and class names embedded in the header.

`SequenceFile.Sorter` creates temporary segment files and may delete input files depending on `deleteInput` and `SegmentDescriptor.preserveInput`. Cleanup is stateful and can mutate the filesystem.

`Text` persists UTF-8 bytes with zero-compressed integer length. It can contain malformed input only when decode/encode calls choose replacement behavior; validation methods explicitly reject invalid UTF-8 with `MalformedInputException`.

`NullWritable` is singleton state in memory and zero bytes on disk.

## Dependencies and Integration Points

The permission APIs integrate with `org.apache.hadoop.conf.Configuration`, filesystem metadata, `FileStatus`, and `DataInput`/`DataOutput` writable serialization.

The S3 APIs integrate with `FileSystem`, `Path`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `Progressable`, `FsPermission`, Java `URI`, local temporary `File` objects, and AWS S3 stores. `S3FileSystem` depends on the `FileSystemStore` abstraction; `NativeS3FileSystem` depends on `NativeFileSystemStore` outside this chunk. Credential loading bridges URI authority/user-info and Hadoop configuration.

Filesystem shell helpers integrate with the broader `FsShell` command layer outside this chunk, the configured `FileSystem`, and path/status quota APIs.

The IO APIs are the core integration point for MapReduce, HDFS metadata, RPC payloads, sequence/map/set file storage, sorting, configuration serialization, and user-defined key/value types. They depend on Java IO, collections, `Configuration`, Hadoop serializers/deserializers, compression codecs, `Progressable`, filesystem paths and streams, and `WritableComparator`.

`RawComparator` and the nested primitive comparators are performance integration points for Hadoop sorting and grouping: they let sort code compare serialized bytes without object allocation. `SequenceFile.Sorter` and `MapFile.Reader` depend on those comparators for ordering.

`DefaultStringifier` integrates with `SerializationFactory`, `Serializer`, and `Deserializer`, allowing arbitrary serializable Hadoop objects to be embedded in configuration. This is useful for job setup but creates compatibility coupling to configured serialization implementations.

`ObjectWritable` and `GenericWritable` are integration points for heterogenous value types. `GenericWritable` is more efficient for known finite type sets, while `ObjectWritable` is broader and used by RPC-like or generic serialization paths.

`MapFile`, `ArrayFile`, and `SetFile` integrate `SequenceFile` storage with `FileSystem` paths. `MapFile` also integrates with command-line repair via `main(String[])`.

`Text` integrates with `SequenceFile.Metadata`, string serialization utilities, key sorting, and all writable APIs that need stable UTF-8 behavior. `UTF8` remains for backward compatibility but is deprecated in favor of `Text`.

## Risks and Edge Cases

This source is generated API XML. It gives the public contract but not implementation internals, private fields, enum constants, or all nested helper classes. Implementation-specific research should be reconciled with the Java sources if code changes are planned.

The slice starts mid-`FsAction` and ends mid-`UTF8`, so adjacent chunk reconciliation is required for complete class documentation.

`FsPermission.valueOf(String)` expects Unix symbolic strings. Incorrect string length, file-type prefix handling, or invalid symbols are likely input-validation risks. Umask parsing through `Configuration` can also cause broad filesystem behavior changes.

Permission parameters in the S3 filesystems are documented as ignored in some operations. Callers expecting POSIX-like permission enforcement on S3 will get misleading metadata or no enforcement.

The old `S3FileSystem` stores data in Hadoop-specific blocks and inodes, so it is not directly interoperable with native S3 tools. Version mismatch handling and migration are critical. Metadata/data updates are likely non-atomic over S3, so rename, delete, and create can leave partial state after failures.

`NativeS3FileSystem` is interoperable with S3 tools but inherits object-store limitations. Append is unsupported, rename may require copy/delete semantics, and list status cost grows with remote pagination. Directory behavior may not match hierarchical filesystems.

`S3Credentials` can source secrets from URI or configuration; URI-embedded credentials risk leaking through logs, diagnostics, or stringified URIs.

`Command.runAll()` returns a coarse success/failure code. If a multi-path command partially succeeds, callers need diagnostics outside the return code.

`AbstractMapWritable` has a hard 127 distinct-class limit per map instance. Complex nested maps can exceed this unexpectedly.

Reusable buffers and byte writables expose backing arrays directly. Misusing `getData()` or `get()` beyond valid length can leak stale bytes, corrupt comparisons, or write unintended data.

`BytesWritable` capacity changes preserve current data but new bytes are undefined. Tests should avoid assuming zero-fill after growth.

`CompressedWritable` requires subclasses and field accessors to call `ensureInflated()`. Missing that call can read stale compressed state rather than real fields.

`DefaultStringifier` stores base64 serialized blobs in configuration. Empty arrays are explicitly invalid for `storeArray`, and deserialization can fail if serializers, classes, or configuration differ between store and load.

`GenericWritable` only works for classes declared by `getTypes()`. Unknown type ids, changed type order, or removed classes break compatibility. `ObjectWritable` is more flexible but serializes class names frequently and is more expensive.

`MapFile.Writer.append()` requires nondecreasing sorted keys. Out-of-order writes corrupt the map's searchable contract. Large index intervals reduce memory use but increase seek scan cost; small intervals increase index memory use.

`MapFile.Reader` reads the index into memory, so large or heavy key objects can cause high memory pressure. Its synchronized methods provide per-reader serialization but not necessarily safe external mutation of key/value instances supplied by callers.

`SequenceFile` embeds class names and compression codec names in headers. Renaming classes, changing serializers, or removing codecs can make old files unreadable. Raw APIs require exact handling of key/value lengths and compression state. `seek()` is only safe for positions emitted by `Writer.getLength()`, while arbitrary offsets must use `sync()`.

`SequenceFile.Sorter` performance depends heavily on efficient key deserialization and raw comparison. It may delete input or temporary files, so failure handling must protect caller data when `deleteInput` is true.

Block-compressed sequence files encode key/value lengths with zero-compressed integers. Bugs in length decoding can desynchronize the rest of a block.

`Text.charAt(int)` and `find(String, int)` use byte positions, not Java UTF-16 character indexes. Callers can get `-1` for invalid positions or trailing bytes. `bytesToCodePoint(ByteBuffer)` advances the buffer position and changes marks, which can surprise callers reusing the buffer.

`Text.decode(..., replace)` changes error behavior based on the `replace` flag. Tests must cover both replacement and exception behavior for malformed UTF-8.

`UTF8` is deprecated, so new code should avoid adding dependencies on it except for compatibility with old serialized data.

## Test Signals

API compatibility tests should compare this JDiff XML against generated API for signature, visibility, checked exceptions, inheritance, public fields, deprecation state, and Javadoc-sensitive contracts.

Permission tests should cover `FsAction` boolean algebra, octal and symbolic representations, `FsPermission` short round trips, symbolic `valueOf`, umask get/set through `Configuration`, `applyUMask`, default permissions, immutable creation, equality/hash behavior, and `PermissionStatus` serialization including user/group strings.

Block-based S3 tests should use an injected `FileSystemStore` to exercise initialize/version checks, inode and block storage, create/open round trips, byte-range block retrieval, directory listing, recursive and non-recursive delete, rename, migration rewriting metadata without touching block files, version mismatch exceptions, unsupported append, ignored permission parameters, `purge`, and `dump`.

Native S3 tests should cover native object create/open/delete/list, recursive delete, directory marker or prefix behavior, working directory resolution, rename semantics, unsupported append, injected `NativeFileSystemStore`, URI handling, file status for files versus directories, and listing pagination/call-count behavior around 1000-key boundaries.

Credential tests should cover URI-provided credentials, configuration-provided credentials, missing credentials raising `IllegalArgumentException`, and secret redaction in any diagnostics outside the API.

Shell command tests should cover `CommandFormat` minimum/maximum operands, option parsing from arbitrary start positions, unknown/duplicate options, `getOpt`, `Command.runAll()` success/failure aggregation across multiple paths, and `Count.matches()` plus count output for files, directories, quotas, and remaining quotas.

Primitive writable tests should round-trip every primitive wrapper through `write`/`readFields`, compare object and raw comparator ordering, verify equality/hash/toString, and include negative, zero, boundary, NaN, and signed byte cases where relevant.

`BytesWritable` tests should cover size versus capacity, growth and shrink behavior, copying from byte ranges, serialized comparator ordering, equality over logical size only, hex string output, and stale bytes beyond logical size not participating in comparison.

Buffer tests should cover `DataInputBuffer` and `InputBuffer` reset with offsets, position/length reporting, `DataOutputBuffer.write(DataInput, int)`, reset reuse, backing array validity only through length, and large writes that force capacity growth.

`CompressedWritable` tests should implement a small subclass and verify lazy inflation, final `readFields`/`write` behavior, subclass compressed read/write hooks, and field access after read.

`DefaultStringifier` tests should store/load single objects and arrays in `Configuration`, verify base64 content is present under the expected key, reject empty arrays, close serializers/deserializers, and fail clearly when classes or serializers are unavailable.

`GenericWritable` tests should verify allowed type serialization, type id stability, configuration propagation before deserialization, rejection of unsupported wrapped classes, and compatibility when `getTypes()` order is unchanged. `ObjectWritable` tests should cover declared class preservation, null instance handling, primitive/writable/object payloads supported by the implementation, static read/write helpers, and configuration propagation.

`MapWritable` and `SortedMapWritable` tests should cover class registry serialization, nested maps, copy constructors, the 127-class limit, sorted-key operations, standard map views, mutation after serialization, and interoperability with `WritableComparable` keys.

`MapFile` tests should write sorted records, reject or diagnose out-of-order appends, tune index interval, read exact keys, seek missing keys, get closest before/after, compute mid/final keys, close/reset behavior, rename/delete directories, repair missing or corrupt indexes with `fix()`, and verify index memory behavior with large key objects.

`ArrayFile` tests should verify implicit long keys, seek by index, next value iteration, and random get. `SetFile` tests should verify key-only append, membership lookup, seek, and next-key iteration.

`SequenceFile` tests should cover writer factory overloads, metadata round trips, uncompressed, record-compressed, and block-compressed formats, sync marker insertion, `Writer.getLength()` followed by `Reader.seek()`, arbitrary offset `sync()`, `syncSeen()`, typed and raw iteration, value byte compressed/uncompressed writes, codec absence or mismatch, class-name compatibility, and close behavior.

`SequenceFile.Sorter` tests should sort one and many input files, merge with different fan-in values, enforce memory limits enough to spill segments, preserve or delete inputs according to flags, report progress, clone compression attributes, write raw iterator records, clean up temporary segments, and use custom `RawComparator` without unnecessary key object allocation.

`Text` tests should cover UTF-8 encode/decode with and without replacement, malformed input validation, zero-compressed length serialization, byte-position `charAt`, byte-position `find`, append and clear, bytewise comparison, raw comparator ordering, `readString`/`writeString`, `skip`, `bytesToCodePoint` buffer-position side effects, and `utf8Length` for ASCII, multibyte, and surrogate-pair input.

`UTF8` compatibility tests should remain for reading old serialized values, skipping encoded data, and comparing behavior against `Text` where the visible API overlaps.

## Cross-Chunk Notes

The final per-file reconciliation should merge this chunk with adjacent chunks for the complete `org.apache.hadoop.fs.permission` package and the remainder of deprecated `org.apache.hadoop.io.UTF8`.

Several referenced types are outside this chunk: `Writable`, `WritableComparable`, `WritableComparator`, `SequenceFile` helper internals, `NativeFileSystemStore`, `CompressionCodec`, `SerializationFactory`, and the full `FileSystem` base class. This chunk documents how the visible APIs depend on them, but complete behavior requires their declarations and implementation sources.

The Hadoop 0.18.1 S3 APIs are historically important but differ from modern object-store filesystem contracts. Reconciliation should call out the difference between block-based `s3:` and native `s3n:` style storage when comparing across Hadoop versions.
