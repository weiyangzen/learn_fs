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
