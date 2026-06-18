# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.20.0.xml lines 6147-12387

## Scope

This chunk is a JDiff API snapshot for Hadoop Core 0.20.0. It starts in the public API entry for `org.apache.hadoop.fs.RawLocalFileSystem`, continues through the rest of `org.apache.hadoop.fs`, FTP/KFS/S3 filesystem implementations, permissions, shell command helpers, the embedded HTTP server, and the first large part of `org.apache.hadoop.io`, and ends inside `org.apache.hadoop.io.SequenceFile.Metadata`.

The source is generated compatibility metadata, not executable Java. The research surface is therefore the public contract: package and type names, inheritance, implemented interfaces, constructors, fields, method signatures, checked exceptions, deprecation state, and embedded Javadocs.

## Purpose

The filesystem portion documents Hadoop's 0.20-era `FileSystem` ecosystem. It covers local filesystem behavior, seek/sync stream contracts, trash lifecycle operations, FTP-backed filesystems, Kosmos/KFS integration, two S3 implementations, POSIX-like permission value objects, and shell commands.

The HTTP portion documents Hadoop's embedded Jetty status server and filter container contract. It exposes servlet/filter registration, default web applications, SSL listener setup, thread configuration, lifecycle control, and a stack servlet for runtime diagnostics.

The `org.apache.hadoop.io` portion documents Hadoop's Writable serialization layer and file formats. It includes typed Writables for primitive values and byte arrays, reusable in-memory input/output buffers, polymorphic object serialization, map/array file formats, MD5 hashes, Bloom-filter-assisted map files, raw comparators, and the beginning of `SequenceFile`, Hadoop's binary key/value container format.

## Important APIs and Types

### Core Filesystem Contracts

`RawLocalFileSystem` is visible from the middle of its class entry. The listed public operations map Hadoop paths to local files and include `pathToFile`, `getUri`, `initialize`, `open`, `append`, permission-aware and permission-less `create` overloads, `rename`, deprecated and recursive `delete`, `listStatus`, `mkdirs`, home and working directory accessors, local-file move/staging hooks, `close`, `toString`, `getFileStatus`, `setOwner`, and `setPermission`. The Javadocs identify it as the raw local implementation of the `FileSystem` API, with owner and permission operations delegated to host commands such as `chown` and `chmod`.

`Seekable` declares stateful stream positioning with `seek(long)`, `getPos()`, and `seekToNewSource(long)`. `Syncable` declares `sync()` for flushing buffered data to underlying devices. These interfaces are small but foundational: input streams, sequence readers, and filesystem implementations use them to expose random access and durability semantics across local and distributed filesystems.

`Trash` extends `Configured` and provides the user-facing trash facility. Constructors accept either a `Configuration` alone or a `FileSystem` plus `Configuration`. Public methods include `moveToTrash(Path)`, `checkpoint()`, `expunge()`, `getEmptier()`, and `main(String[])`. Its Javadoc describes the storage layout: deleted files move under a per-user `.Trash/current` tree preserving their original paths; periodic checkpoints and expunges avoid full trash enumeration and avoid depending on filesystem timestamps or synchronized clocks.

### Remote Filesystem Implementations

`org.apache.hadoop.fs.ftp.FTPException` wraps failures in a runtime exception. `FTPFileSystem` extends `FileSystem` and exposes normal filesystem operations over FTP: `initialize`, `open`, `create`, `append`, deprecated and recursive `delete`, `getUri`, `listStatus`, `getFileStatus`, `mkdirs`, `rename`, and working/home directory accessors. Public fields include logging and default buffer/block sizes. The create Javadoc warns that a stream returned from `create` must be closed before other APIs on the same instance are used, or those calls can block; `append` is explicitly unsupported. `FTPInputStream` extends `FSInputStream`, wraps an `InputStream` and `FTPClient`, tracks position with `getPos`, rejects/implements seek semantics through `seek` and `seekToNewSource`, and forwards `read`, `close`, mark, and reset behavior.

`org.apache.hadoop.fs.kfs.KosmosFileSystem` extends `FileSystem` for the Kosmos File System. Its API includes initialization, URI/name and working directory handling, directory/file tests, listing, status, append/create/open, rename/delete, length/replication/default block size access, lock/release, file block locations, local copy hooks, and local-output staging. The Javadoc describes KFS as a Hadoop filesystem backend selected through `fs.default.name` and `fs.kfs.impl`, with chunk-location lookup returning null when a file does not exist.

`org.apache.hadoop.fs.s3` contains the older block-based S3 filesystem. `Block` stores an S3 block id and length. `INode` stores file metadata, a file type, and the block list; it exposes serialization/deserialization and a shared directory inode. `FileSystemStore` is the persistence interface for versioned metadata and block storage: initialize, store/retrieve/delete inode and block objects, list shallow/deep subpaths, purge everything, and dump diagnostics. `S3Credentials` reads AWS credentials from URI/configuration, `S3Exception` wraps S3 communication failures, `S3FileSystemException` and `VersionMismatchException` model fatal and incompatible-store failures, and `MigrationTool` is a `Tool` for store migration. `S3FileSystem` exposes the Hadoop `FileSystem` methods backed by the store; permission parameters in `create` and `mkdirs` are documented as ignored, and `append` is unsupported.

`org.apache.hadoop.fs.s3native.NativeS3FileSystem` is the object-oriented S3 variant. It extends `FileSystem`, supports initialization with the default or injected `NativeFileSystemStore`, and exposes append/create/delete/status/URI/list/mkdir/open/rename/working-directory methods. Like block-based S3, append is unsupported; the Javadoc distinguishes it from the block-based `S3FileSystem`.

### Permissions and Shell

`AccessControlException` extends `IOException` and exists for filesystem authorization failures. It includes no-arg, message, and cause constructors; the no-arg constructor is documented as needed for unwrapping from `RemoteException`.

`FsAction` is an enum-style permission bitmask with `NONE`, `EXECUTE`, `WRITE`, `WRITE_EXECUTE`, `READ`, `READ_EXECUTE`, `READ_WRITE`, and `ALL`. It provides `implies`, `and`, `or`, `not`, and a symbolic string field. `FsPermission` implements `Writable` and stores user/group/other `FsAction` values. It can be built from actions, a short mode, or another permission; it supports immutable creation, `fromShort`, `toShort`, `readFields`, `write`, static `read(DataInput)`, equality/hash/string conversion, umask application, configuration-backed `getUMask`/`setUMask`, default permissions, and Unix symbolic parsing through `valueOf(String)`. `PermissionStatus` implements `Writable` and combines owner name, group name, and `FsPermission`, with immutable creation, umask application, static read/write helpers, and string rendering.

`org.apache.hadoop.fs.shell.Command` is a configured base for filesystem shell subcommands. It stores argument arrays, exposes the command name without the leading dash, runs on a path, and has `runAll()` for applying a command to each source. `CommandFormat` parses command options and min/max positional argument counts. `Count` implements the `-count` command, with public `NAME`, `USAGE`, and `DESCRIPTION` fields and behavior for counting directories, files, bytes, quota, and remaining quota.

### Embedded HTTP Server

`FilterContainer` declares `addFilter` and `addGlobalFilter` for registering servlet filters with init parameters. `FilterInitializer` is the corresponding initialization hook.

`HttpServer` implements `FilterContainer` using Jetty. Constructors bind a name/address/port and optionally a `Configuration`; `findPort` controls whether port collisions are searched around. Public and protected methods create the listener, add default apps/servlets, add contexts, set/get webapp attributes, add normal or internal servlets, define filters, map filter paths, locate webapp resources, inspect the active port, configure worker threads, add SSL listeners, and run `start`, `stop`, and `join`. Public/protected state includes the Jetty server, listener connector, webapp context, default context map, and registered filter names. `HttpServer.StackServlet` is a simple servlet whose `doGet` emits current thread stack traces for diagnostics.

### Writable Values and Buffers

`AbstractMapWritable` implements `Writable` and `Configurable` as the shared class-id table for `MapWritable`-style containers. It can add class mappings, map between byte IDs and classes, copy another map's class table, and serialize/deserialize the table. `MapWritable` extends it and implements `java.util.Map`, exposing normal map operations plus custom Writable serialization.

`ArrayWritable` stores arrays of a declared `Writable` value class and can be constructed from a value class, an initial array, or string arrays. It exposes value-class lookup, set/get, `toArray`, `toStrings`, and Writable read/write. `ArrayFile` extends `MapFile` as a dense integer-to-value file; its `Reader` can seek by ordinal, read the next value, return the last key, and get the nth value, while its `Writer` appends values.

`BinaryComparable` abstracts byte-backed comparable values through `getLength`, `getBytes`, raw byte comparison, equality, and hashing. `BytesWritable` extends it for mutable byte sequences; it exposes backing data, logical length, deprecated size aliases, capacity changes, copy/set methods, serialization, equality/hash, and hex-style string output. Its comparator compares serialized byte buffers.

`BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, and `LongWritable` are primitive `WritableComparable` wrappers. Each visible wrapper has a zero/default constructor, value constructor, `set`, `get`, `readFields`, `write`, equality, hash, comparison, and string conversion. Each has a nested `WritableComparator`; `LongWritable` also has a decreasing comparator.

`Closeable` is a Hadoop `io` package interface extending `java.io.Closeable` and is marked deprecated in favor of the JDK type. `CompressedWritable` is an abstract compressed Writable base: final `readFields` stores compressed bytes, `ensureInflated()` lazily inflates before field access, subclasses implement `readFieldsCompressed`, final `write` emits compressed data, and subclasses implement `writeCompressed`.

`DataInputBuffer` and `InputBuffer` are reusable in-memory readers over byte arrays with `reset` overloads, position, and length access. `DataOutputBuffer` and `OutputBuffer` are reusable in-memory writers with current data/length access, `reset`, and direct copy helpers from `DataInput` or `InputStream`.

`DefaultStringifier<T>` implements `Stringifier` using Hadoop serialization. It converts objects to/from strings, closes resources, and stores/loads single objects or arrays in `Configuration` keys. Its static helpers depend on configured `Serialization` classes.

`IOUtils` provides stream utility methods: three `copyBytes` overloads, `readFully`, `skipFully`, cleanup that ignores `IOException`, `closeStream`, and `closeSocket`. `IOUtils.NullOutputStream` is the `/dev/null` output stream implementation.

`MD5Hash` implements `WritableComparable` for MD5 digests. It can be constructed empty, from a hex string, or from raw bytes; it reads/writes digest bytes, copies another digest, returns raw bytes, computes digests from byte arrays, streams, and strings, exposes half/quarter digest projections, compares and hashes by digest, and parses/prints hex form. `MultipleIOException` aggregates a list of `IOException` instances and can produce a single representative `IOException`. `NullWritable` is a singleton Writable with no serialized data and a comparator that compares serialized empty values.

`ObjectWritable` implements polymorphic Writable serialization for `Writable`, `String`, primitive types, and arrays of those types. It stores the declared class and instance, exposes `get`, `getDeclaredClass`, and `set`, serializes through instance and class metadata, and has static `writeObject` and `readObject` helpers with optional `Configuration` support.

`RawComparator` extends `java.util.Comparator` with byte-array comparison for serialized values. This is a key integration point for sort/shuffle and file-format lookup paths because callers can compare records without fully deserializing them.

### MapFile, BloomMapFile, and SequenceFile

`MapFile` is a sorted, file-based key/value map built on `SequenceFile`. Static utilities include `rename`, `delete`, `fix` for rebuilding a corrupt index, and `main`. Public constants identify the `index` and `data` files. `MapFile.Reader` opens a map using a filesystem, path, comparator, configuration, and optional open flag; it exposes key/value classes, reset, approximate mid-key lookup, final-key read, seek, next, exact get, closest-key lookup, and close. `MapFile.Writer` creates maps with key/value classes or comparators, optional sequence compression type/codec/progress, index interval getters/setters, close, and ordered `append`; appended keys must be greater than or equal to the previous key.

`BloomMapFile` layers a Bloom filter over `MapFile` for sparse files. It defines a Bloom side-file name and hash count, has a static delete helper, and exposes `Reader` methods for membership tests, fast `get`, and retrieving the filter. `Writer` constructors mirror map-file creation and maintain the filter as entries are appended.

`SequenceFile` is documented as Hadoop's flat binary key/value file format. Static methods get and set compression type in `Configuration` and construct `Writer` instances from a `FileSystem`/`Path` or raw `FSDataOutputStream`, with overloads for key/value classes, buffer size, replication, block size, compression type, codec, progress, and metadata. `SYNC_INTERVAL` defines how often sync markers are inserted. The embedded format documentation describes a common header containing magic/version, key/value class names, compression flags, codec, metadata, and sync marker, plus three record layouts: uncompressed, record-compressed values, and block-compressed groups of key/value lengths and bytes.

`SequenceFile.CompressionType` has enum values `NONE`, `RECORD`, and `BLOCK`, representing no compression, per-record value compression, and block compression of grouped records. `SequenceFile.Metadata` implements `Writable` and is visible with constructors from empty state or `TreeMap`, `get`, `set`, `getMetadata`, `write`, `readFields`, and the start of `equals`.

## Control Flow and Behavior

The XML has no method bodies, but the signatures and Javadocs expose the intended control paths.

Filesystem clients call uniform `FileSystem` operations regardless of backend. `RawLocalFileSystem` maps `Path` values to local `File` objects and directly mutates the host filesystem. FTP, KFS, block-based S3, and native S3 reuse the same high-level open/create/list/status/delete/rename/mkdir contract while translating it to protocol- or store-specific operations. Unsupported optional operations are explicit in this chunk: FTP, KFS, S3, and native S3 all expose append-related limitations in their public docs.

Trash control flow is a move/checkpoint/expunge cycle. `moveToTrash` first rejects disabled trash or paths already in trash, then moves content into `.Trash/current` while preserving the original pathname. `checkpoint` rotates current trash into a checkpoint, and `expunge` deletes old checkpoints. `getEmptier` returns a `Runnable` intended for superuser background cleanup across users.

Permission control flow is value-object based. `FsAction` operations compute mask implication and boolean algebra. `FsPermission` converts between symbolic/action/short forms, serializes the three action fields, and applies a configured umask to produce creation permissions. `PermissionStatus` combines identity strings with permissions and can apply the same umask transformation to its permission member.

HTTP server control flow starts with construction of Jetty state, listener creation, default application/servlet setup, optional SSL connector registration, filter definition/path mapping, and then `start`. Runtime callers can set attributes visible to JSPs/servlets, inspect the bound port, and stop or join the server. The stack servlet follows standard `HttpServlet.doGet` dispatch.

Writable control flow follows the Hadoop `write(DataOutput)` and `readFields(DataInput)` convention. Primitive wrappers serialize one primitive value. Byte wrappers serialize length and bytes. `AbstractMapWritable` serializes class-id mappings so subclasses can encode heterogeneous keys and values compactly. `ObjectWritable` writes class metadata plus the instance payload and can reconstruct supported primitive, string, array, and Writable values.

File-format control flow layers on `SequenceFile`. `MapFile.Writer.append` writes sorted key/value pairs to a data file and periodically indexes keys. `MapFile.Reader.seek/get/getClosest` use the index and data file reader to position and retrieve records. `ArrayFile` specializes this to dense long keys. `BloomMapFile.Reader` checks its Bloom filter before expensive map lookups. `SequenceFile.createWriter` chooses the appropriate writer implementation according to compression type and optional codec/metadata, while readers of the format rely on sync markers and header metadata.

## State and Persistence Behavior

This JDiff file itself persists the public Hadoop 0.20.0 API for compatibility checks. Runtime state is only inferable from the documented contracts.

`RawLocalFileSystem` persists files, directories, permissions, owners, and deletions on the host filesystem. `FTPFileSystem` persists through an FTP server and has blocking stream-use constraints. `KosmosFileSystem` persists through KFS and exposes block-location metadata. `S3FileSystem` persists a Hadoop filesystem abstraction through S3 metadata inodes and block objects managed by `FileSystemStore`; `NativeS3FileSystem` persists objects directly through a native S3 store. These backends can differ sharply in atomicity, metadata fidelity, permissions, and append support even though they share the `FileSystem` method names.

Trash persists deleted content under user home directories in `.Trash/current` and checkpoint directories. The design intentionally avoids depending on filesystem date support, full content enumeration, or synchronized clocks.

`FsPermission` and `PermissionStatus` define stable Writable forms for permission and owner/group metadata. `FsPermission` also stores process/configuration policy through the umask key `UMASK_LABEL` and default value `DEFAULT_UMASK`.

`HttpServer` keeps process-local mutable server state: Jetty server/connector/context objects, filter name lists, default contexts, the selected port, and whether it should search for a free port. Its externally persistent effects are network listeners and servlet/filter registrations, not file data.

The `org.apache.hadoop.io` classes define durable binary formats. Primitive Writables, `BytesWritable`, `MD5Hash`, `NullWritable`, `MapWritable`, `ObjectWritable`, `ArrayWritable`, and `SequenceFile.Metadata` are serialized through `DataInput`/`DataOutput`. `MapFile` persists two files named by public constants, `data` and `index`. `BloomMapFile` adds a Bloom filter side file. `SequenceFile` persists a header, metadata, sync markers, and records whose binary layout changes with `CompressionType`.

`CompressedWritable` stores compressed bytes after read and delays inflation until subclass fields are accessed. `DataInputBuffer`, `DataOutputBuffer`, `InputBuffer`, and `OutputBuffer` store reusable heap buffers whose valid data is limited by reported length, not full backing-array capacity.

## Dependencies and Integration Points

Filesystem APIs depend on `org.apache.hadoop.fs.Path`, `FileStatus`, `BlockLocation`, `FSDataInputStream`, `FSDataOutputStream`, `FSInputStream`, `FileSystem.Statistics`, `Configuration`, `Configured`, `Progressable`, `Tool`, and `FsPermission`. Remote backends integrate with Apache Commons Net FTP, KFS client libraries, AWS/S3 store abstractions, and Hadoop's `RemoteException` unwrapping model.

The permission APIs integrate with Hadoop RPC, HDFS authorization, shell commands, and Writable serialization. Shell command helpers integrate `Configuration`, path iteration, and CLI option parsing.

`HttpServer` integrates with Jetty (`org.mortbay.jetty.Server`, `Connector`, `WebAppContext`), Java servlet APIs, SSL listener configuration, Hadoop logging, and webapp resources located on the classpath.

`org.apache.hadoop.io` integrates with Java `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `Closeable`, `Comparator`, `Map`, `TreeMap`, `MessageDigest`, Hadoop `Writable`, `WritableComparable`, `WritableComparator`, `Serialization`, `Stringifier`, compression codecs, and filesystem streams. `SequenceFile`, `MapFile`, `ArrayFile`, and `BloomMapFile` bind the IO serialization layer back to `FileSystem` and `Path`.

## Risks and Edge Cases

- The range starts mid-`RawLocalFileSystem` and ends mid-`SequenceFile.Metadata`; the final merged per-file report must combine adjacent chunks before treating either class as complete.
- JDiff XML does not expose implementation bodies. Behavioral conclusions here come from public signatures and Javadocs and must be validated against Java source or contract tests when implementation details matter.
- Several filesystems expose the same `FileSystem` API with weaker backend semantics. FTP create streams can block other calls until closed; S3 permissions are documented as ignored; append is unsupported across FTP/S3/native S3 and appears optional in KFS.
- Object stores and FTP may not provide POSIX rename atomicity, permission fidelity, owner/group mutation, or directory semantics expected by local/HDFS callers.
- `RawLocalFileSystem.setOwner` and `setPermission` depend on host commands, so tests are sensitive to platform, process privileges, command availability, and user/group names.
- `Seekable.seek` explicitly cannot seek past EOF, while `seekToNewSource` may return false when no alternate data source exists. Callers must not assume HDFS-style replica switching for local, FTP, S3, or in-memory streams.
- Trash behavior relies on rename/move support and home-directory layout. Disabled trash, paths already under trash, rename failures, and checkpoint cleanup races are important cases.
- `FsPermission.valueOf` expects Unix symbolic forms such as `-rw-rw-rw-`; parsing and umask tests should include invalid strings, directory/file prefixes, and short-mode round trips.
- `BytesWritable.getBytes()` returns backing storage, with only `[0, getLength())` valid. Callers that use full capacity can leak stale bytes or compare incorrect data.
- `DataOutputBuffer.getData()` and `OutputBuffer.getData()` also expose backing arrays whose valid data ends at `getLength()`.
- `CompressedWritable` requires subclasses to call `ensureInflated()` before field access. Missing that call produces stale/default state after deserialization.
- `MapFile.Writer.append` requires nondecreasing keys. Violating sorted order can corrupt lookup assumptions.
- `MapFile.fix` rebuilds indexes for corrupt maps and should be treated as a recovery tool with careful tests around malformed data files.
- `BloomMapFile` membership checks are probabilistic; false positives must still fall through to map lookup, and tests should not assume a positive filter result means a key exists.
- `ObjectWritable` serializes class names and declared classes. Cross-version compatibility can break when class names move, primitive/array handling changes, or configured serialization support differs.
- `SequenceFile` compatibility depends on exact header fields, metadata serialization, sync marker placement, compression flags, codec names, and record/block layouts.

## Test Signals

- API compatibility tests should assert public/protected classes, interfaces, constructors, fields, method overloads, checked exceptions, deprecation text, and inheritance for every package covered in this chunk.
- Filesystem contract tests should cover local, FTP, KFS, S3, and native S3 implementations for create/open/list/status/mkdir/delete/rename behavior, recursive delete, working directory resolution, default block size/replication, and unsupported append.
- Local filesystem tests should cover `Path` to `File` conversion, permission and owner mutation, chmod/chown failure paths, local-output staging, and close behavior.
- Trash tests should cover disabled trash, moving a path already in trash, original-path preservation under `.Trash/current`, checkpoint creation, expunge deletion, and emptier behavior.
- Permission tests should cover all `FsAction` implication/and/or/not combinations, short-mode and symbolic parsing round trips, umask application, `PermissionStatus` serialization, and `AccessControlException` remote exception unwrapping.
- HTTP server tests should cover port binding with and without `findPort`, default servlet/app installation, filter and global-filter mapping, SSL listener configuration, thread settings, start/stop/join lifecycle, attribute visibility, and stack servlet output.
- Writable serialization tests should round-trip primitive Writables, `BytesWritable` length/capacity behavior, `ArrayWritable`, `MapWritable`, `ObjectWritable` primitives/strings/arrays/Writables, `MD5Hash`, `NullWritable`, and `SequenceFile.Metadata`.
- Buffer tests should ensure `getLength()` bounds are respected after reset/write/read operations and that buffer reuse does not expose stale valid data.
- Comparator tests should compare object-level and raw serialized comparison for `BooleanWritable`, `ByteWritable`, `BytesWritable`, numeric Writables, `MD5Hash`, `NullWritable`, and `RawComparator` implementors.
- Map-file tests should cover writer sorted-key enforcement, index interval configuration, reader seek/get/getClosest/finalKey/midKey/reset, static rename/delete, and index repair through `fix`.
- Bloom map tests should cover filter creation during append, false-positive-tolerant lookup behavior, fast `get`, filter retrieval, and side-file deletion.
- SequenceFile tests should cover writer factory overloads, raw stream writers, metadata persistence, compression type configuration, `NONE`/`RECORD`/`BLOCK` format round trips, sync interval behavior, codec integration, and mixed-version reader compatibility.
