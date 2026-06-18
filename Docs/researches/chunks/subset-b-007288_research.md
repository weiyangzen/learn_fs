# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 6139-12390

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.0, not Java implementation source. It starts in the tail of `org.apache.hadoop.fs.RawLocalFileSystem` and ends inside the opening constructor documentation for `org.apache.hadoop.io.SequenceFile.Sorter.SegmentDescriptor`, so adjacent chunks are required for complete analysis of those two classes. The XML records compatibility metadata: package names, classes/interfaces, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation text, and embedded Javadoc contracts.

The covered API surface spans Hadoop filesystem contracts and adapters (`fs`, FTP, KFS, S3, native S3, shell helpers), filesystem permissions, embedded HTTP server setup, and much of Hadoop's classic `org.apache.hadoop.io` serialization and sorted-file layer through `SequenceFile.Sorter`.

## Purpose and Major API Surface

The visible `RawLocalFileSystem` tail exposes local-output completion, close, string conversion, status lookup, owner changes via `chown`, and permission changes via `chmod`. `Seekable` and `Syncable` are small stream contracts for random access, position reporting, source switching, and buffer/device synchronization. `Trash` provides the user trash abstraction: move paths into `.Trash/current`, create checkpoints, expunge old checkpoints, and run a superuser emptier.

`org.apache.hadoop.fs.ftp` contains `FTPException`, `FTPFileSystem`, and `FTPInputStream`. `FTPFileSystem` adapts Apache Commons Net FTP into the Hadoop `FileSystem` API with initialize, open, create, delete, list/status, mkdirs, rename, working-directory, home-directory, and URI operations. Its `create` documentation warns that the returned stream must be closed before other filesystem APIs are used. `FTPInputStream` is an `FSInputStream` backed by an FTP client, with position reporting, seek stubs, synchronized reads, synchronized close, and unsupported mark/reset behavior.

`KosmosFileSystem` is the KFS adapter for the Hadoop `FileSystem` API. It exposes URI/name/working-directory setup, mkdirs, directory/file predicates, listing/status, create/open/append, rename/delete, length and replication metadata, default replication/block size, lock/release, block-location lookup, and local copy/local output hooks.

`org.apache.hadoop.fs.permission` defines Hadoop permission objects. `AccessControlException` is the access-denied exception. `FsAction` is the action enum-like API with implication, logical `and`, `or`, and `not`, plus index and symbolic fields. `FsPermission` is a `Writable` three-part permission with constructors from actions, short mode, or another permission; it can serialize/deserialize, convert to/from short and symbolic strings, apply and configure umasks, and produce defaults. `PermissionStatus` combines user, group, and `FsPermission`, supports immutable construction, umask application, serialization helpers, and string formatting.

The old block-based `org.apache.hadoop.fs.s3` APIs model Hadoop files on S3 through `Block`, `INode`, and `FileSystemStore`. `FileSystemStore` is the persistence boundary for storing/retrieving/deleting inodes and blocks, listing shallow/deep subpaths, purging all data, and dumping diagnostics. `S3FileSystem` exposes the Hadoop `FileSystem` operations over that store. Supporting classes cover credentials from URI/configuration, version migration, store version mismatch, and S3-specific runtime exceptions.

`NativeS3FileSystem` is the newer object-store-style S3 adapter backed by `s3native.NativeFileSystemStore`. It provides initialize, create/open, delete, status, URI, listStatus, mkdirs, rename, working-directory methods, and logging. Append is explicitly unsupported. Its listing documentation exposes directory emulation behavior through key prefixes and file statuses.

`org.apache.hadoop.fs.shell` contains the base `Command`, `CommandFormat`, and `Count`. `Command` owns a `Configuration`, command arguments, `getCommandName`, per-path `run(Path)`, and `runAll()` dispatch. `CommandFormat` parses option sets with min/max positional argument counts and lets callers query options. `Count` implements `-count`-style shell behavior with command name, usage, description, matching, and execution.

`org.apache.hadoop.http` defines servlet filter and HTTP server wiring. `FilterContainer.addFilter` registers a named filter with class name and init parameters. `FilterInitializer` is the extension point for adding filters to a container. `HttpServer` wraps Jetty, owns listeners, default contexts, webapp context, filter names, attributes, servlets, SSL listeners, threads, start/stop lifecycle, and default apps/servlets. `HttpServer.StackServlet` writes thread stack information through `doGet`.

The `org.apache.hadoop.io` section begins with map-aware serialization support. `AbstractMapWritable` tracks byte-to-class mappings for writable maps, copies mappings from another instance, serializes class maps, and is configurable. `ArrayFile` is a dense long-keyed `MapFile` variant; its reader supports seek, next, current key, and random get by long index, while its writer appends values. `ArrayWritable` serializes homogeneous arrays of `Writable` and has a string-array constructor.

Primitive and binary writables include `BinaryComparable`, `BooleanWritable`, `BytesWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, and `LongWritable`, each with writable serialization, mutation/accessors, equality/hash/string behavior, comparison, and raw-byte comparator classes where present. `LongWritable.DecreasingComparator` reverses long ordering. `Closeable` is deprecated in favor of `java.io.Closeable`.

Buffer and compression helpers include `CompressedWritable`, which lazily inflates compressed serialized data through subclass hooks, `DataInputBuffer`, `DataOutputBuffer`, `InputBuffer`, and `OutputBuffer`, which expose reusable in-memory byte-backed input/output buffers with reset and data/length/position access. `IOUtils` provides byte-copy helpers, exact read/skip behavior, cleanup, closeStream, closeSocket, and a `NullOutputStream`.

Dynamic serialization helpers include `DefaultStringifier`, `GenericWritable`, `MapWritable`, and `ObjectWritable`. `DefaultStringifier` converts configured objects to strings and back and stores/loads single values or arrays in `Configuration`. `GenericWritable` serializes one value from a fixed subclass-provided type set. `MapWritable` implements `Map<Writable,Writable>` with dynamic class tracking inherited from `AbstractMapWritable`. `ObjectWritable` wraps arbitrary declared classes/instances, handles configuration, and has static `writeObject`/`readObject` helpers used by dynamic IPC and configuration paths.

`MapFile` is a sorted persistent map built from SequenceFiles named `data` and `index`. Top-level helpers rename, delete, repair indexes with `fix`, and expose `INDEX_FILE_NAME` and `DATA_FILE_NAME`. `MapFile.Reader` opens data/index readers, reports key/value classes, resets, finds midpoint/final keys, seeks, iterates, performs exact get, and returns closest keys above or below a target. `MapFile.Writer` constructs sorted writers with class or comparator inputs, compression and codec variants, index interval getters/setters, close, and append.

`MD5Hash` is a fixed 16-byte `WritableComparable` digest wrapper with constructors from empty state, hex string, or byte array; digest factories from byte arrays, strings, and input streams; half/quarter digest extraction; raw comparator; and static length metadata. `MultipleIOException` aggregates lists of IOExceptions into one IOException. `NullWritable` is the singleton zero-byte key/value with comparator support.

`RawComparator<T>` extends `Comparator<T>` with a raw byte comparison method over two byte-array slices. `SequenceFile` is the central flat-file key/value format API. This chunk includes deprecated global compression getters/setters, many overloaded `createWriter` factories for filesystem/path/stream/class/comparator/compression/codec/progress/metadata combinations, and `SYNC_INTERVAL`. `CompressionType` identifies none/record/block compression. `SequenceFile.Metadata` is a writable `TreeMap<Text,Text>` wrapper.

`SequenceFile.Reader` reads SequenceFiles and exposes file opening, close, key/value class names/classes, compression state, codec, metadata, object and writable value access, key-only and key/value iteration, raw key/value reading, value-byte creation, seek to writer positions, sync to the next sync marker, sync-seen reporting, current position, and file-name stringification. `SequenceFile.Sorter` sorts and merges SequenceFiles with configurable merge factor, memory budget, and progress callback; it can sort to files, sort and return a raw iterator, merge segment descriptors or input paths, clone file attributes into a writer, and write raw iterator records. `RawKeyValueIterator` exposes current raw key/value, iteration, close, and progress.

## Control Flow and Behavioral Contracts

The XML has no method bodies, but the public contracts imply important flows. Filesystem adapters follow the Hadoop `FileSystem` lifecycle: initialize from a URI and `Configuration`, resolve a working directory, create/open streams, list or stat paths, mutate directories and names, and close streams/resources. FTP specifically serializes operations behind a stream lifecycle because an unclosed create stream can block later API calls.

Trash flow moves a path under the user's home `.Trash/current` while preserving the original path layout, then periodically checkpoints current trash and expunges old checkpoints. `getEmptier()` returns a runnable intended for the superuser and keeps only one checkpoint at a time.

Permission flow converts among symbolic actions, short mode bits, writable binary state, and string forms. FileSystem methods consume `FsPermission` and `PermissionStatus`; umask application creates derived permissions for create/mkdir-style operations. Stable serialization is needed because these objects cross filesystem metadata and RPC boundaries.

S3 block-store flow persists each file as an `INode` plus an array of `Block` descriptors and separate block payloads in a `FileSystemStore`. `S3FileSystem` operations translate directory creation, listing, status, create/open, rename, and delete into inode and block store calls. Native S3 flow is object-key-oriented and emulates directories through key listings and directory markers.

Shell command flow is command-object based. A command parses arguments, matches path patterns, runs per path, and aggregates exit status. `CommandFormat` enforces option and argument cardinality before command execution. `Count` is a concrete example that emits counts for matched paths.

HTTP server flow constructs Jetty listeners and contexts, installs default apps/servlets, registers servlets and filters, sets attributes shared with servlets, optionally adds SSL listeners, configures threads, then starts and stops the server. Filters can be added through `FilterInitializer` instances using the `FilterContainer` interface.

Writable flow is symmetric `write(DataOutput)` and `readFields(DataInput)`. Primitive wrappers write fixed primitive values; variable-sized wrappers write lengths plus bytes or class metadata; comparators may compare serialized byte slices directly and must match object-level ordering. Buffer classes enable reuse by resetting backing byte arrays instead of allocating per record.

MapFile writer flow appends strictly sorted key/value pairs and periodically writes index entries according to the configured interval. Reader flow first consults the index for approximate position, seeks the data SequenceFile, then scans to exact or closest keys. `MapFile.fix` rebuilds a missing or corrupt index from the data file and returns the number of entries.

SequenceFile writer factory flow selects key/value classes or comparators, output target, compression type, optional codec, metadata, and progress callback. Reader flow opens a SequenceFile, validates metadata/class/compression headers, iterates records, optionally exposes raw serialized key/value bytes for sort/merge paths, and uses sync markers for split/recovery alignment. Sorter flow spills sorted segments under a memory budget, then merges them with bounded fan-in while exposing `RawKeyValueIterator` progress.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API compatibility data. Runtime persistence described by these APIs includes local filesystem metadata, remote FTP files, KFS file metadata, S3 inode/block objects, native S3 object keys, trash checkpoints, permission and owner metadata, SequenceFile/MapFile data and index files, writable binary encodings, MD5 digest bytes, map writable class-id tables, and configuration-stored stringified values.

Stateful APIs include filesystem working directories, open FTP clients and streams, KFS locks, S3 stores and credentials, HTTP server listeners/contexts/filter lists/attributes, mutable writable values, dynamic class maps, reusable buffers, compressed writable inflated/uninflated data, MapFile reader positions, SequenceFile reader positions and sync markers, sorter memory/factor/progress settings, and raw iterator current key/value buffers.

External side effects are broad. Filesystem methods create, delete, rename, chmod/chown, lock/release, and copy files locally or remotely. Trash creates checkpoints and deletes expired trash. S3 migration/purge/dump operations can mutate or enumerate persistent buckets. HTTP server methods bind ports and expose servlets. IOUtils closes streams and sockets. DefaultStringifier mutates `Configuration` keys. SequenceFile and MapFile writers create durable files, and sorter merge/sort operations create temporary files and may delete input paths when requested.

Threading is only selectively documented in flags. Several stream reads and SequenceFile reader iteration methods are synchronized, but most mutable wrappers, map writables, filesystem clients, MapFile readers/writers, and sorter instances are not documented as thread-safe in this API snapshot.

## Dependencies and Integration Points

Filesystem APIs integrate with `org.apache.hadoop.fs.FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSInputStream`, `Path`, `FileStatus`, `BlockLocation`, `FileSystem.Statistics`, `Configuration`, `Progressable`, and `FsPermission`. FTP depends on Apache Commons Net `FTPClient` and Commons Logging. KFS depends on the Kosmos filesystem client stack outside this XML. S3 APIs depend on S3 credentials, URI/configuration parsing, local temporary block files, and store implementations.

Permission APIs integrate with `Writable`, `DataInput`, `DataOutput`, filesystem metadata, shell commands (`chmod`/`chown` for local FS), and configuration keys such as the umask label. Shell helpers integrate with `Configuration`, path expansion, command-line parsing, and filesystem globbing.

HTTP server APIs integrate with Jetty 5-style classes (`org.mortbay.jetty.Server`, `SocketListener`, `WebApplicationContext`), servlet requests/responses, filter definitions, SSL keystores, and Hadoop webapp resources.

The IO layer is central to Hadoop common and MapReduce. It depends on Java I/O streams, `DataInput`/`DataOutput`, `Configuration`, `Configurable`, `Writable`, `WritableComparable`, `WritableComparator`, `Text`, compression codecs, `Progressable`, `Progress`, and `FileSystem`. Its consumers include MapReduce shuffle/sort, RPC object wrapping, SequenceFile/MapFile storage, configuration serialization, and filesystem metadata persistence.

Compatibility tooling depends on exact XML signatures and attributes. Public signature changes, field additions/removals, generic string changes, synchronization flag changes, exception list changes, deprecation text changes, or Javadoc contract edits in this source affect downstream JDiff comparisons for Hadoop 0.19.0.

## Risks and Compatibility Notes

This chunk is partial at both ends. It should not be used alone to summarize all of `RawLocalFileSystem` or `SequenceFile.Sorter.SegmentDescriptor`.

Filesystem adapter compatibility is operationally sensitive. FTP stream ordering, KFS lock/release behavior, S3 inode/block layout, native S3 directory emulation, rename/delete semantics, and working-directory resolution can differ from POSIX filesystems. Callers often rely on Hadoop `FileSystem` behavior rather than backend-specific details, so subtle differences can break tools.

Permission serialization and string/mode conversion are high compatibility points. Changes to `FsAction` implication logic, symbolic output, short mode bit mapping, default umask, or `PermissionStatus` field order can break persisted metadata and old clients.

Object store APIs carry data-loss risk. `FileSystemStore.purge`, recursive delete, migration, block deletion, and rename over S3-like stores must be tested with partial failure behavior. Version mismatch handling exists because persisted layouts are not interchangeable.

HTTP server APIs expose mutable public/protected server internals and older Jetty classes. Changing listener/context/filter lifecycle or default servlet paths can break Hadoop daemons' web UIs, diagnostics, and downstream filter initializers.

Writable binary compatibility is critical. Primitive encodings, byte lengths, class-id assignment in `AbstractMapWritable`, `ObjectWritable` declared-class handling, `GenericWritable` type ordering, `MD5Hash` length, and `NullWritable` singleton semantics are part of persisted file/RPC compatibility.

Raw comparators must agree with object comparators. A mismatch in byte order, offset handling, length handling, floating point edge cases, or decreasing comparator inversion can corrupt MapReduce sort order or MapFile/SequenceFile merge results.

MapFile and SequenceFile formats are storage contracts. Compression type, codec metadata, sync interval, sync markers, metadata maps, sorted append preconditions, index intervals, seek positions, raw record lengths, and merge deletion flags must remain stable for old files and applications.

Deprecated APIs in this chunk still matter for Hadoop 0.19.0 compatibility: `FTPFileSystem.delete(Path)`, `BytesWritable.get`, `BytesWritable.getSize`, `org.apache.hadoop.io.Closeable`, deprecated global SequenceFile compression setters/getters, and deprecated raw `Reader.next(DataOutputBuffer)` all appear in the public snapshot.

## Test Signals

JDiff validation should confirm the XML is well-formed around this line range and preserves all package/class/interface boundaries, including the partial `RawLocalFileSystem` tail and partial `SequenceFile.Sorter.SegmentDescriptor` start. API checks should compare constructors, methods, fields, visibility, static/final/abstract/synchronized flags, declared exceptions, generic type strings, implemented interfaces, and deprecation text.

Filesystem tests should cover local owner/permission operations, seekable position and seek error cases, syncable flushing, trash move/checkpoint/expunge/emptier flows, FTP create-stream close-before-next-operation behavior, FTP listing/status/rename/delete, KFS create/open/rename/delete/lock/block-location paths, S3 block-store inode/block round trips, native S3 listStatus directory emulation, unsupported append paths, and recursive delete semantics.

Permission tests should round-trip `FsPermission` and `PermissionStatus` through `DataOutput`/`DataInput`, verify short and symbolic conversions, action implication/logical operations, umask application, default and configured umask behavior, equality/hash behavior, immutable factory behavior, and AccessControlException construction.

HTTP and shell tests should cover command option parsing bounds, command path dispatch and aggregate exit codes, `Count` command matching/execution, filter initializer registration, servlet/filter path mapping, server port selection with `findPort`, SSL listener setup with controlled keystores, default servlet/app registration, attribute visibility to servlets, start/stop lifecycle, thread settings, and stack servlet output.

Writable tests should round-trip every primitive wrapper, `BytesWritable`, `ArrayWritable`, `MapWritable`, `GenericWritable`, `ObjectWritable`, `MD5Hash`, `CompressedWritable` subclasses, and buffer-backed values. Comparator tests should compare object ordering against raw byte comparator ordering, including empty bytes, offsets, duplicate prefixes, booleans, signed bytes, floating point special values, ints, longs, decreasing long order, MD5 bytes, and `NullWritable`.

Buffer and IO tests should cover reset/data/length/position invariants, write growth, writeTo behavior, compressed lazy inflation, exact `readFully`, exact `skipFully`, copyBytes close/non-close variants, cleanup with multiple close failures, socket close behavior, and NullOutputStream discard behavior.

MapFile tests should write sorted keys with multiple index intervals and compression modes, reject or detect out-of-order appends, read exact keys, closest-before and closest-after keys, midpoint/final keys, reset/seek/next sequences, rename/delete helpers, and `fix` rebuilding an index from data.

SequenceFile tests should create writers through representative overloads with none/record/block compression, custom codecs, metadata, filesystem and stream outputs, then validate reader class metadata, compression flags, codec, metadata, object and raw iteration, sync/seek behavior, syncSeen, current position, EOF handling, deprecated raw-next behavior, and close idempotence.

Sorter tests should sort and merge SequenceFiles with configurable memory and factor, custom `RawComparator`, progress callbacks, temporary directories, input deletion on/off, cloned writer attributes, `RawKeyValueIterator` key/value/progress/close behavior, and segment descriptors with offset/length/path boundaries.
