# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007287`: lines 1-6138, `Docs/researches/chunks/subset-b-007287_research.md`
- `subset-b-007288`: lines 6139-12390, `Docs/researches/chunks/subset-b-007288_research.md`
- `subset-b-007289`: lines 12391-18682, `Docs/researches/chunks/subset-b-007289_research.md`
- `subset-b-007290`: lines 18683-24886, `Docs/researches/chunks/subset-b-007290_research.md`
- `subset-b-007291`: lines 24887-30897, `Docs/researches/chunks/subset-b-007291_research.md`
- `subset-b-007292`: lines 30898-37232, `Docs/researches/chunks/subset-b-007292_research.md`
- `subset-b-007293`: lines 37233-43522, `Docs/researches/chunks/subset-b-007293_research.md`
- `subset-b-007294`: lines 43523-43972, `Docs/researches/chunks/subset-b-007294_research.md`

## Chunk Research

### subset-b-007287: lines 1-6138

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 1-6138

## Scope and Purpose

This chunk is the opening portion of the JDiff XML API description for Hadoop 0.19.0, generated from Javadoc on 2008-11-24. It is not executable code; it is a structured public API inventory used by Hadoop's `dev-support/jdiff` compatibility tooling to compare API surfaces across releases. The root `<api>` element records the release name, JDiff version, schema, sourcepath, classpath, and doclet invocation, then lists public packages/classes/interfaces/methods/fields with signatures, visibility, deprecation status, inheritance, implemented interfaces, exceptions, parameters, and Javadoc CDATA.

The chunk covers:

- `org.apache.hadoop.HadoopVersionAnnotation`
- `org.apache.hadoop.conf`: `Configurable`, `Configuration`, `Configuration.IntegerRanges`, `Configured`
- `org.apache.hadoop.filecache.DistributedCache`
- The start and much of `org.apache.hadoop.fs`: block/file metadata, file system abstractions, checksum wrappers, stream abstractions, archive and local file systems, path/filter/read interfaces, and the beginning of `RawLocalFileSystem`

The range ends mid-class at `RawLocalFileSystem.startLocalOutput`; later lines must be merged with this chunk before producing the final per-file research document.

## Important APIs, Types, and Contracts

`HadoopVersionAnnotation` is documented as a package attribute recording the Hadoop version used at compile time. It implements `java.lang.annotation.Annotation` and is part of the release/version metadata surface.

`Configurable` is the minimal configuration injection interface: `setConf(Configuration)` and `getConf()` define how Hadoop services and helpers receive runtime configuration. `Configured` is the corresponding base class that stores a `Configuration` and implements `Configurable`.

`Configuration` is a central mutable settings container. It implements `Iterable<Map.Entry<String,String>>` and Hadoop `Writable`. It supports constructors for default loading, disabling default resources, and cloning. Resource loading APIs accept classpath names, `URL`, `Path`, or `InputStream`; later resources override earlier values unless an earlier value is marked final. `reloadConfiguration()` is synchronized and clears resource-derived state and final-parameter state so resources can be re-read while preserving values set by setter methods as overlays.

`Configuration` exposes typed accessors and setters for strings, ints, longs, floats, booleans, comma-delimited string collections/arrays, integer ranges, and class names. `getClassByName`, `getClasses`, typed `getClass`, and `setClass` are integration points for pluggable implementations and enforce interface compatibility where an `xface` is supplied. `getLocalPath` and `getFile` choose a local directory from a configured directory list by path hash and create missing directories. Resource accessors expose `URL`, `InputStream`, and `Reader`. Serialization/control APIs include `size`, `clear`, `iterator`, `writeXml`, `readFields`, `write`, `getClassLoader`, `setClassLoader`, `setQuietMode`, `toString`, and a debugging `main`.

`Configuration.IntegerRanges` represents positive integer ranges parsed from strings such as `2-3,5,7-`, with `isIncluded(int)` and `toString()`.

`DistributedCache` is a static MapReduce support API for localizing read-only files, archives, jars, and symlinks on task nodes. Its overloads of `getLocalCache` accept a cache `URI`, `Configuration`, cache base directory, optional DFS `FileStatus`, archive flag, expected modification timestamp, task working directory, and an optional `honorSymLinkConf`. It also provides `releaseCache`, timestamp lookup, symlink creation, configuration setters/getters for cache archive/file URIs and localized paths, timestamp setters/getters, classpath augmentation (`addFileToClassPath`, `addArchiveToClassPath` and getters), `createSymlink`, `getSymlink`, URI fragment conflict validation via `checkURIs`, and destructive `purgeCache`.

The `org.apache.hadoop.fs` section defines the core filesystem model:

- `BlockLocation` is a `Writable` metadata object for hosts, names, file offset, and block length.
- `FileStatus` is a `Writable`/`Comparable` client-side file metadata object for length, directory flag, replication, block size, modification/access time, permissions, owner, group, and `Path`. Equality and hash code are path-based.
- `ContentSummary` is a `Writable` aggregate for length, directory/file counts, quotas, space consumed, and space quota, with CLI-oriented header/string formatting.
- `FileChecksum` is an abstract `Writable` checksum contract; `MD5MD5CRC32FileChecksum` implements the MD5-of-MD5-of-CRC32 algorithm, including binary and XML serialization helpers.
- `Path` is Hadoop's URI-like filesystem path abstraction. It supports parent/child resolution, component construction, `toUri`, `getFileSystem(Configuration)`, absolute/name/parent/suffix/depth operations, qualification against a `FileSystem`, comparison, equality, and separator constants.
- `PathFilter` and `PositionedReadable` are small extension interfaces for filtering paths and thread-safe positional reads that do not alter stream offset.

`FileSystem` is the abstract base class for all Hadoop filesystems. It extends `Configured`, implements `Closeable`, and defines static discovery/caching methods (`get(Configuration)`, `get(URI,Configuration)`, `getLocal`, `closeAll`, default URI getters/setters). Scheme resolution is configuration-driven via `fs.<scheme>.class`, and `initialize(URI, Configuration)` plus `getUri()` are the implementation identity hooks. Core abstract operations include `open(Path,int)`, full `create(...)`, `append(Path,int,Progressable)`, `rename`, `delete(Path)`, `delete(Path,boolean)`, `listStatus(Path)`, `setWorkingDirectory`, `getWorkingDirectory`, `mkdirs(Path,FsPermission)`, and `getFileStatus`.

`FileSystem` also supplies convenience overloads and helpers: many `create` overloads for overwrite, buffer size, replication, block size, permissions, and progress; `createNewFile`; deprecated metadata shims (`getName`, `getNamed`, `getReplication`, `isDirectory`, `getLength`, `getBlockSize`); `exists`, `isFile`, `getContentSummary`; `listStatus` overloads for `PathFilter` and arrays; `globStatus` with shell-like glob constructs and sorted results; local/remote copy and move helpers; `startLocalOutput`/`completeLocalOutput`; `deleteOnExit` and `processDeleteOnExit`; `getFileChecksum`; permission/owner/time setters; and synchronized static filesystem statistics lookup/printing.

`ChecksumFileSystem` extends `FilterFileSystem` and provides a client-side checksum wrapper over a raw filesystem. It names checksum files, detects checksum-file paths, calculates checksum file length, exposes bytes-per-sum, wraps `open`, `append`, `create`, `rename`, `delete`, `listStatus`, `mkdirs`, local copy helpers, local output staging, and `reportChecksumFailure`.

`FilterFileSystem` is the classic decorator. It contains protected field `fs` and forwards nearly all `FileSystem` methods to the contained filesystem, allowing subclasses such as `ChecksumFileSystem` and `HarFileSystem` to transform behavior while preserving the `FileSystem` surface.

Stream classes define the read/write behavior expected by filesystem implementations:

- `FSInputStream` is a seekable `InputStream` with positional reads and `seekToNewSource`.
- `BufferedFSInputStream` wraps an `FSInputStream` with buffering while preserving `Seekable` and `PositionedReadable`.
- `FSDataInputStream` wraps input as `DataInputStream`, buffering and exposing seek/position/positional-read operations.
- `FSDataOutputStream` wraps output as `DataOutputStream`, supports `Syncable`, reports position, exposes the wrapped stream, and optionally updates `FileSystem.Statistics`.
- `FSInputChecker` is an abstract checksum-verifying input stream. Subclasses provide `readChunk` and `getChunkPosition`; it manages checksum parameters, synchronized read/seek/skip/available operations, retry/checksum behavior, and disables mark/reset.
- `FSOutputSummer` is an abstract checksum-generating output stream. It buffers chunks, computes checksums, writes chunks via subclass `writeChunk`, and exposes checksum conversion and buffer reset.

Utility and concrete filesystem classes in this chunk include:

- `DF` and `DU`, both `Shell` subclasses, wrap Unix `df` and `du` command output for disk capacity/usage metrics. `DU` can run a refresh thread and supports manual usage increments/decrements.
- `FileUtil` contains static file operations for status-to-path conversion, recursive deletion, filesystem-to-filesystem/local copy, copy-merge, shell path conversion, basic local disk usage, unzip/untar, symlink/chmod via shell, temp file creation, replacement, and nested `HardLink` creation/link-count support across Unix, Cygwin, and Windows XP.
- `FsShell` is a `Tool`/`Configured` command-line facade over `FileSystem`, with `init`, `run`, `close`, `main`, current trash lookup, byte formatting, and date-format fields.
- `FsUrlStreamHandlerFactory` provides Java URL stream handlers that delegate URL connections to Hadoop `FileSystem` resolution after checking the requested scheme is known.
- `HarFileSystem` is a read-oriented Hadoop Archive filesystem over `FilterFileSystem`. HAR URIs identify an archive in an underlying filesystem; `_masterindex` and `_index` files map archive paths to `part-*` contents. It exposes archive version, hash lookup, index-backed status/listing/open/block-location behavior, and marks most mutating operations as not implemented.
- `InMemoryFileSystem` is a `ChecksumFileSystem` for `ramfs://`, assuming file lengths are known in advance and bounded by configured memory. `reserveSpaceWithCheckSum` must be called before creating files so data and checksum space can be reserved together.
- `LocalDirAllocator` implements per-context round-robin allocation across configured local directories. It can allocate write paths with or without known size, locate existing read paths, create temporary files deleted at JVM exit, validate contexts, and test file existence across configured dirs. The docs explicitly warn that it does not handle disks becoming read-only or full during an active write.
- `LocalFileSystem` is the checksumed local filesystem wrapper with access to the raw filesystem, `pathToFile`, local copy overrides, and checksum-failure handling that moves bad files aside on the same device.
- `RawLocalFileSystem` begins in this chunk. It extends `FileSystem` and maps Hadoop `Path` to `java.io.File`, implements local `open`, `append`, `create`, `rename`, `delete`, `listStatus`, `mkdirs`, home/working-directory behavior, deprecated lock/release, `moveFromLocalFile`, and starts the `startLocalOutput` declaration at the chunk boundary.

## Control Flow and Behavioral Model

Because this file is JDiff XML, runtime control flow is represented indirectly by API contracts and wrapper relationships. The compatibility tool reads this XML structurally: packages contain classes/interfaces, classes contain constructors/methods/fields/docs, and comparisons are made against another release's JDiff XML.

Configuration flow is resource-first and lazy/overlay-oriented. Defaults load from `hadoop-default.xml` and `hadoop-site.xml` unless disabled; callers may add resources in order; final parameters block later resource overrides; values set by setters overlay resource values. Accessor calls perform variable expansion using other configuration properties and then JVM system properties. Reload clears resource-derived and final state so future reads revisit resource inputs, while set-method values remain overlays.

Filesystem resolution flow is URI/configuration-driven. A caller gets a filesystem from `FileSystem.get(conf)` or `Path.getFileSystem(conf)`, default URI is read from configuration, scheme selects `fs.<scheme>.class`, and the selected instance receives the full URI in `initialize`. Common operations enter abstract `FileSystem` convenience overloads, normalize to the most complete abstract method signature, then dispatch to concrete implementations such as DFS, raw local, checksum local, HAR, or in-memory filesystems.

File IO flow is layered. `FileSystem.open` returns `FSDataInputStream`, which wraps seekable/positional streams; checksumed filesystems route reads through `FSInputChecker` and writes through `FSOutputSummer`/`FSDataOutputStream`; `ChecksumFileSystem` stores checksum sidecar files for raw data files and verifies/report failures at the client side. Positional reads in `PositionedReadable` are documented as thread-safe and offset-preserving, while normal seek/read mutates stream position.

Distributed cache flow starts with job configuration containing archive/file URIs and timestamps. Before tasks run on a slave, `getLocalCache` validates the expected modification timestamp, reuses or copies the file/archive into a base cache directory, unpacks supported archive types, optionally creates symlinks in the task working directory, and returns the local path. Consumers release localized cache entries later, and service reinitialization can purge the entire backing cache.

HAR flow is index-mediated. Initialization interprets `har://` URIs relative to an underlying filesystem and archive root; listing/status/open read `_masterindex` and `_index` to map logical archive paths to offsets and lengths in `part-*` files. Mutating calls are present on the `FileSystem` surface but documented as not implemented.

Local allocation flow in `LocalDirAllocator` rotates through configured directories per context. For writes it checks capacity when size is known and writability/parent creation; for reads it scans all configured directories for the path. Context names correspond to configuration keys such as `mapred.local.dir`.

## State and Persistence Behavior

The XML file persists the API surface itself: signatures, deprecation text, visibility, inheritance, and Javadoc in a stable format for release-diff tooling. It also embeds the generation environment, including the doclet command line, source paths, classpath jars, API directory, API name, and timestamp.

`Configuration` state is mutable and serializable. It maintains resource lists, key/value overlays, final-parameter state, quiet-mode behavior, a classloader, and `Writable`/XML output support. It is the primary persistent state carrier used by many APIs in this chunk: filesystem defaults, local directory contexts, distributed cache URI lists, timestamps, localized cache paths, symlink flags, and implementation class names.

`FileSystem` state includes per-instance configuration, URI identity, working directory, delete-on-exit registrations, and protected `statistics`. It also has static cached filesystem instances and per-class statistics looked up through synchronized APIs. `closeAll` and per-instance `close` release cached/held resources and trigger delete-on-exit processing.

Metadata objects (`BlockLocation`, `FileStatus`, `ContentSummary`, `FileChecksum`, `MD5MD5CRC32FileChecksum`) are serializable via Hadoop `Writable`, so they can cross RPC or be stored/transmitted in Hadoop protocols. `MD5MD5CRC32FileChecksum` additionally serializes to XML attributes through `XMLOutputter` and reconstructs from SAX `Attributes`.

Checksum persistence is sidecar-based in `ChecksumFileSystem`: checksum files are created and managed alongside raw files. Rename/delete/list operations need to preserve or hide checksum files consistently. `LocalFileSystem.reportChecksumFailure` persists failure evidence by moving suspect files into a bad-file directory on the same device.

Distributed cache state is persisted mainly in configuration strings and localized on node-local disk. Timestamps are stored and compared to ensure remote cache files do not change while a job is running. `purgeCache` deletes cache backing files and is explicitly server-reinitialization-only because users lose cached files.

HAR filesystem state is persistent in archive files: `_masterindex`, `_index`, and `part-*` content files. The API notes that original file permissions are not persisted when creating a Hadoop archive; returned permissions are those of archive index files.

In-memory filesystem state lives in process memory and requires explicit space reservation before writes. `LocalDirAllocator` keeps JVM-local allocator instances per context and round-robin cursor state for disk selection.

## Dependencies and Integration Points

The generated command line shows the API was built from `src/core`, `src/mapred`, and `src/tools`, against Hadoop build classes and many external libraries including commons-cli, commons-codec, commons-httpclient, commons-logging, commons-net, hsqldb, jets3t, Jetty/JSP/servlet jars, JUnit, KFS, log4j, ORO, SLF4J, xmlenc, Ant, Xerces, and JDK tools.

Within this chunk, major Java dependencies include `java.io`, `java.net.URI/URL/URLStreamHandlerFactory`, `java.util`, `java.util.zip.Checksum`, `java.text.SimpleDateFormat`, `org.xml.sax`, and `org.znerd.xmlenc`. Hadoop dependencies include `org.apache.hadoop.conf`, `org.apache.hadoop.io.Writable` and `MD5Hash`, `org.apache.hadoop.fs.permission.FsPermission`, `org.apache.hadoop.util.Progressable`, `Tool`, and `Shell`, plus MapReduce integration through `JobConf`, `Mapper`, `Reducer`, `JobClient`, and task working directories described in `DistributedCache`.

External process integration is visible in `DF`, `DU`, `FileUtil.symLink`, `FileUtil.chmod`, tar/zip handling, and hardlink support. These APIs depend on platform shell behavior and document support for Linux, FreeBSD, Cygwin, Unix, and Windows XP in places.

Pluggability integration centers on `Configuration` class loading and `FileSystem` scheme resolution. Any filesystem implementation must satisfy the `FileSystem` contract and be named by `fs.<scheme>.class`. `FsUrlStreamHandlerFactory` integrates this same registry with Java URL handling.

## Risks and Edge Cases

This chunk is generated metadata, so its direct risk is documentation/API drift: if generated from the wrong classpath/sourcepath or truncated before merge, JDiff comparisons may report inaccurate compatibility changes. The embedded command line is useful but also environment-specific and stale by design.

`Configuration` final parameters and variable expansion are compatibility-sensitive. Resource ordering, reload behavior, quiet mode, classloader selection, and interface checks in `getClass`/`setClass` can change application behavior even when signatures remain stable.

`DistributedCache` has several operational hazards: localized files are read-only by contract but can be changed externally; timestamp mismatches must be treated seriously; URI fragments are required for symlink mode and can conflict; `purgeCache` is destructive; archive unpacking and symlink creation depend on local filesystem permissions and platform behavior.

`FileSystem` contains many overloaded convenience methods that normalize to abstract implementations. Compatibility breaks can occur if overload defaults for overwrite, buffer size, replication, block size, progress, permissions, or delete recursion change. Deprecated methods remain part of the public surface and may still be used by older clients.

Checksum wrappers introduce consistency risks between data files and sidecar checksum files. Rename/delete/list/copy operations must handle checksum files atomically enough for clients; checksum failure handling must avoid reusing corrupt local storage; `FSInputChecker` allows seek/skip past EOF but subsequent reads return `-1`, which callers must understand.

`LocalDirAllocator` explicitly does not handle disks becoming read-only or filling after allocation. Its per-context singleton behavior can also create hidden process-local state that affects test isolation.

`HarFileSystem` exposes mutating methods because it inherits `FileSystem`, but many are not implemented. Callers must treat HAR as read-oriented and account for permissions not being preserved in archives.

`RawLocalFileSystem` in this chunk is incomplete at the boundary, so final conclusions about local output completion and remaining methods require later chunks.

## Test Signals

Useful compatibility tests for this XML artifact include validating it against `api.xsd`, parsing the full file as XML, checking package/class/method ordering, and diffing it with adjacent Hadoop release JDiff XML using the JDiff tooling.

API-level tests implied by this chunk include:

- Configuration resource precedence, final-parameter override prevention, variable expansion fallback to system properties, typed getter defaults on parse errors, `reloadConfiguration`, `writeXml`, `Writable` round trips, classloader/class-interface validation, quiet mode, and local path selection.
- Distributed cache URI registration, timestamp checking, local reuse versus copy, archive extraction for zip/jar/tar/tgz/tar.gz, symlink creation and fragment conflict detection, classpath registration, release and purge behavior.
- FileSystem scheme resolution via `fs.<scheme>.class`, default URI read/write, cached instance close/closeAll, overload defaults for create/append/open/delete/list/glob/copy/move, delete-on-exit processing, statistics counting, permission/owner/time setters, and deprecated shim behavior.
- Metadata `Writable` round trips for `BlockLocation`, `FileStatus`, `ContentSummary`, and checksum types; `FileStatus` path-based equality/ordering; `Path` URI normalization, parent/child resolution, qualification, comparison, and depth.
- Checksumed IO tests for checksum sidecar length, open/create/append, corrupt data detection, `reportChecksumFailure`, positional reads preserving stream offset, seek/skip EOF behavior, and output chunk checksum generation.
- Local/system utility tests for `DF`/`DU` parsing on supported platforms, `FileUtil` recursive delete partial failure, copy/copyMerge semantics, unzip/untar, chmod/symlink exit codes, temp file cleanup flags, hardlink count support, and shell path conversion.
- HAR tests for URI parsing, index/master-index lookup, block location mapping to underlying filesystem, list/status/open over part files, version handling, read-only method failures, and permission behavior.
- LocalDirAllocator tests for round-robin selection, size-aware capacity checks, parent creation/writability checks, read-path scanning, temporary file deletion-on-exit, invalid contexts, and behavior when configured directories are missing or full.

## Chunk Boundary Notes

The range starts at the XML declaration and root `<api>` element. It ends at line 6138 inside `org.apache.hadoop.fs.RawLocalFileSystem`, after the opening of `startLocalOutput(Path fsOutputFile, Path tmpLocalFile)`. The merge/reconciliation lane must combine subsequent chunks to complete `RawLocalFileSystem` and the rest of `org.apache.hadoop.fs` and later packages before producing the final source-tree-aligned per-file research document.

### subset-b-007288: lines 6139-12390

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

### subset-b-007289: lines 12391-18682

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 12391-18682

## Scope and source type

This chunk is a JDiff XML API snapshot for Hadoop 0.19.0, not Java implementation source. It records public/protected API signatures, inheritance, selected fields, checked exceptions, deprecation markers, synchronization markers, and embedded Javadoc. Behavioral notes below are therefore grounded in the API contract and comments visible in this chunk, with implementation details inferred only where the contract is explicit.

The range starts in `org.apache.hadoop.io.SequenceFile.Sorter.SegmentDescriptor`, covers the rest of many `org.apache.hadoop.io` writable and text APIs, the public compression codec stack, retry and serialization APIs, Hadoop IPC/RPC APIs and metrics, runtime log-level controls, and ends at the beginning of `org.apache.hadoop.mapred.Counters`.

## Purpose

The chunk documents core Hadoop data interchange and transport surfaces:

- Sequence and map/set file utilities for persisted key/value data.
- The `Writable` serialization contract used across MapReduce, filesystem metadata, and IPC.
- Raw comparators and variable-length integer helpers used by sort-heavy paths.
- UTF-8 string containers and string serialization utilities.
- Compression codec abstractions and concrete BZip2, gzip/zlib, and LZO/lzop adapters.
- Retry proxies for wrapping unreliable method calls.
- Serializer/deserializer factories for `Writable` and Java serialization.
- IPC/RPC client/server contracts, version negotiation, remote exceptions, and server metrics.
- Log-level runtime adjustment entry points.
- MapReduce cluster status and the beginning of counter aggregation APIs.

## Important APIs, types, and functions

### SequenceFile and set/map data

`SequenceFile.Sorter.SegmentDescriptor` represents one merge segment. It can perform sync checks via `doSync()`, control cleanup semantics with `preserveInput(boolean)` and `shouldPreserveInput()`, compare/equality/hash segments, stream raw keys and values via `nextRawKey()`, `nextRawValue(SequenceFile.ValueBytes)`, expose the buffered raw key through `getKey()`, and clean up by closing file handles and deleting input unless preservation is requested. Subclasses may override `cleanup()`.

`SequenceFile.ValueBytes` abstracts raw sequence-file values. `writeUncompressedBytes(DataOutputStream)` writes uncompressed payload bytes, `writeCompressedBytes(DataOutputStream)` writes stored compressed bytes without performing compression when data is not already compressed, and `getSize()` reports stored data size. This interface is central to raw append/merge flows where values can be copied without object deserialization.

`SequenceFile.Writer` writes key/value sequence files to a `FileSystem`/`Path`, with constructors accepting `Configuration`, key/value classes, optional replication/block size, `Progressable`, and `SequenceFile.Metadata`. Its key methods are `append(Writable, Writable)`, generic `append(Object, Object)` through serializers, `appendRaw(byte[], int, int, ValueBytes)`, `sync()`, `close()`, `getLength()`, `getKeyClass()`, `getValueClass()`, and `getCompressionCodec()`. `close`, `append`, `appendRaw`, and `getLength` are synchronized. Protected serializer fields (`keySerializer`, `uncompressedValSerializer`, `compressedValSerializer`) show integration with the serializer framework. `getLength()` promises a reader-seekable synchronized position, although block compression can make the next readable key earlier than the last appended key.

`SetFile` extends `MapFile` for file-backed sets of sorted keys. `SetFile.Reader` supports constructors with a filesystem/path/config and optional `WritableComparator`, plus `seek`, `next`, and `get` operations over `WritableComparable` keys. `SetFile.Writer` extends `MapFile.Writer`; it accepts key class or comparator and compression type, and `append(WritableComparable)` requires strictly increasing keys. One constructor lacking `Configuration` is deprecated.

`SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap<WritableComparable, Writable>`. It exposes normal sorted-map operations (`firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`, `put`, `remove`, `entrySet`, `keySet`, `values`, etc.) plus `readFields` and `write`. The copy constructor and writable inheritance imply it persists both map entries and the writable class-id mappings maintained by `AbstractMapWritable`.

### Text, UTF-8, and writable values

`Stringifier<T>` is a closeable conversion contract with `toString(T)`, `fromString(String)`, and `close()`, all throwing `IOException`.

`Text` is the non-deprecated UTF-8 byte container. It extends `BinaryComparable` and implements `WritableComparable<BinaryComparable>`. Constructors accept empty state, `String`, another `Text`, or raw bytes. Methods expose raw bytes and byte length, byte-position string search, code point traversal without building a Java `String`, mutation from strings or byte ranges, append/clear, conversion to Java `String`, writable `readFields`/`write`, static `skip`, UTF-8 `decode`/`encode` with optional replacement behavior, string read/write helpers, UTF-8 validation, code point extraction from `ByteBuffer`, and `utf8Length(String)`. Length is serialized using zero-compressed integer encoding.

`Text.Comparator` is an optimized raw-byte `WritableComparator` for `Text` keys. It avoids object materialization in compare-heavy sort paths.

`UTF8` is the legacy/deprecated predecessor to `Text`. It implements `WritableComparable`, stores UTF-8 bytes, exposes `getBytes`, `getLength`, `set`, `readFields`, `write`, `compareTo`, `equals`, `hashCode`, and static string read/write helpers. `UTF8.Comparator` provides an optimized raw comparator for legacy keys.

`TwoDArrayWritable` persists a two-dimensional matrix of `Writable` instances of a declared value class. It exposes `set`, `get`, `toArray`, `readFields`, and `write`.

`VersionedWritable` is an abstract `Writable` base that writes a version byte and verifies it on read. Subclasses supply `getVersion()`. `VersionMismatchException` is thrown when serialized and current versions differ, and callers are expected to catch it when implementing backward compatibility.

`VIntWritable` and `VLongWritable` are `WritableComparable` wrappers for variable-length encoded `int` and `long` values. They expose mutable `set`/`get`, serialization, equality, hashing, comparison, and string conversion. The docs say smaller values take fewer bytes; the `VLongWritable` comment says one to five bytes even though long variable-length encodings can require more bytes, so tests should verify actual format behavior rather than relying on that sentence.

### Writable framework utilities

`Writable` is Hadoop's compact `DataInput`/`DataOutput` serialization interface. `readFields` is expected to reuse existing object storage where possible. The docs identify this as the required key/value contract for MapReduce types.

`WritableComparable<T>` combines `Writable` and `Comparable<T>` and is the normal key contract for MapReduce sorting.

`WritableComparator` implements `RawComparator`. It maintains a synchronized static registry (`get`, `define`) of comparators by key class. It can instantiate new keys, compare deserialized `WritableComparable` objects, compare raw byte spans, and provides static helpers for lexicographic byte comparison, hashing, and reading primitive or variable-length values from byte arrays. This is the primary extension point for optimized sorting and `SequenceFile.Sorter` performance.

`WritableFactories` stores synchronized factory registrations for non-public writable classes and can instantiate with or without `Configuration`. `WritableFactory` is the one-method factory contract. `WritableName` maps writable classes to stable symbolic names and alternate names so serialized files can survive class renames.

`WritableUtils` contains compressed byte/string array helpers, string array helpers, clone/cloneInto via serialization buffers, vint/vlong write/read/sign/size functions, enum string serialization, `skipFully`, and conversion of writable arrays to bytes. Its variable-length integer docs define the on-wire encoding thresholds and first-byte sign/length interpretation.

### Compression stack

`CompressionCodec` is the streaming codec interface. It creates compression and decompression streams with or without reusable `Compressor`/`Decompressor` objects, exposes compressor/decompressor implementation types, creates new codec state, and reports default file extensions.

`CodecPool` is a global reuse pool for `Compressor` and `Decompressor` instances. Callers obtain instances by codec and must return them through `returnCompressor`/`returnDecompressor`.

`CompressionCodecFactory` discovers configured codecs from `io.compression.codecs`, defaults to gzip and zip per the docs, maps filename suffixes to codecs, exposes `getCodecClasses` and `setCodecClasses`, strips suffixes, and has a small CLI/test `main`.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases wrapping final underlying streams. Input streams must implement `read(byte[], int, int)` and `resetState()` to handle repositioned underlying streams. Output streams must implement `write(byte[], int, int)`, `finish()` without closing the wrapped stream, and `resetState()` without resetting the wrapped stream.

`Compressor` and `Decompressor` define deflater/inflater-like state machines: `setInput`, `needsInput`, optional dictionaries, byte counters, `finish`/`finished`, `compress` or `decompress`, `reset`, and `end`. `Decompressor` also has `needsDictionary`.

Concrete codecs and adapters in this chunk:

- `BZip2Codec` implements `CompressionCodec` but explicitly does not support the `Compressor`/`Decompressor` object APIs; those paths throw `UnsupportedOperationException`. It creates BZip2 streams and uses `.bz2` as the default extension.
- `DefaultCodec` is configurable and provides zlib-backed default compression/decompression APIs.
- `GzipCodec` extends `DefaultCodec`, with gzip stream creation, compressor/decompressor factory methods, and `.gz` style extension behavior implied by the codec name. Nested `GzipInputStream` and `GzipOutputStream` bridge Hadoop compression streams to Java deflater/inflater streams, including `resetState`.
- `LzoCodec` is configurable, checks native LZO availability, and creates LZO streams/compressor/decompressor state. `LzopCodec` extends it for lzop-compatible file format behavior. `LzopDecompressor` adds checksum flag initialization, checksum reset/verification for compressed and decompressed data, synchronized input/decompress paths, and LZO1X strategy. `LzopInputStream` reads and verifies lzop headers; `LzopOutputStream` writes lzop headers and closes by writing a null word.
- `CBZip2InputStream` and `CBZip2OutputStream` implement raw BZip2 streams below `BZip2Codec`. They require callers/codecs to manage the two-byte `BZ` magic around the constructors. Their docs call out large memory usage and lack of thread safety.
- `LzoCompressor` and `LzoDecompressor` are native LZO-backed `Compressor`/`Decompressor` implementations with direct buffer sizes, strategies, byte counters, synchronized mutation/compression paths, no-op or explicit `end`, and native library version fields.
- `BuiltInZlibDeflater`/`BuiltInZlibInflater` adapt Java `Deflater`/`Inflater` to Hadoop interfaces. `ZlibCompressor`/`ZlibDecompressor` expose native zlib style direct-buffer implementations with configurable header, level, strategy, counters, reset, and lifecycle. `ZlibFactory` chooses native or built-in zlib implementations based on configuration and native availability.

### Retry and serialization

`RetryPolicies` is a static factory/constant holder for immutable `RetryPolicy` instances: try once and fail, try once without failing void methods, retry forever, fixed-count fixed-sleep, maximum-time fixed-sleep, proportional sleep, exponential randomized backoff, policy by local exception type, and policy by `RemoteException`.

`RetryPolicy.shouldRetry(Exception, int)` returns whether to retry, returns false for swallowable void-method failures, or rethrows to fail. `RetryProxy.create` builds dynamic proxies over an interface and implementation using either one policy for all methods or a method-name-to-policy map with default `TRY_ONCE_THEN_FAIL`.

`Serializer<T>` and `Deserializer<T>` are stateful stream adapters. Serializers are explicitly not allowed to buffer output because other producers may write between serialization calls. `Serialization<T>` pairs serializers and deserializers and declares whether a class is accepted.

`SerializationFactory` loads implementations from the comma-delimited `io.serializations` configuration property and returns the matching `Serialization`, `Serializer`, or `Deserializer`.

`WritableSerialization` delegates to `Writable.write` and `Writable.readFields`. `JavaSerialization` is marked experimental for Java `Serializable`. `DeserializerComparator` and `JavaSerializationComparator` deserialize byte streams and compare resulting `Comparable` objects, which is simpler but generally more expensive than raw-byte comparators.

### IPC, RPC, metrics, and logging

`Client` is the lower-level IPC client for `Writable` request/response values. It can set ping interval in configuration, stop all client threads, make a single call to an address with optional `UserGroupInformation`, or make parallel calls to multiple addresses. Parallel calls return an array with nulls for timeouts/errors.

`RemoteException` serializes remote exception class names/messages. It can unwrap to selected lookup types or any throwable with a string constructor, write XML through `XMLOutputter`, and reconstruct from SAX attributes.

`RPC` is the Java-interface-oriented RPC layer over IPC. It constructs client-side `VersionedProtocol` proxies with version negotiation, user tickets, and socket factories; waits for a proxy; stops proxies; performs expert parallel reflective calls; and constructs `RPC.Server` instances for protocol implementation objects. Protocol methods are restricted to primitives/void, `String`, `Writable`, or arrays of those, should throw only `IOException`, and do not transmit implementation field data.

`RPC.Server` extends `Server`, dispatching reflected protocol calls against an implementation instance. `RPC.VersionMismatch` records interface name, client version, and server version for protocol version failures.

`Server` is the abstract IPC service. It binds/listens on host and port for a single `Writable` parameter class, starts/stops handler threads, joins shutdown, exposes listener address, remote IP/address context for code running inside an RPC call, and requires subclasses to implement `call(Writable, long)`. It publishes `HEADER`, `CURRENT_VERSION`, `LOG`, and protected `rpcMetrics`, plus open connection and call queue length gauges.

`VersionedProtocol` is the superclass for Hadoop RPC protocols and requires `getProtocolVersion(String, long)`. Implementations are also expected to define a static `versionID` field.

`RpcMetrics` registers and publishes RPC queue and processing time metrics through the Hadoop metrics subsystem and JMX. Its rate metrics are public mutable fields. `RpcMgtMBean` exposes operation counts, average/min/max processing and queue times, min/max reset, open connection count, and call queue length. The docs note that metrics are collected regardless of metrics context, but sampled averaging requires an updating context such as `NullContextWithUpdateThread`.

`LogLevel` provides runtime log-level changes via a command-line `main` and a servlet `doGet` entry point. The servlet depends on `javax.servlet.http.HttpServlet`.

### MapReduce status and counters

`ClusterStatus` is a `Writable` snapshot of the MapReduce cluster: number of task trackers, running map/reduce tasks, maximum map/reduce task capacity, and current `JobTracker.State`. Clients obtain it through `JobClient.getClusterStatus()`.

The chunk begins `Counters`, which is a synchronized `Writable` and `Iterable<Counters.Group>`. Visible methods include `getGroupNames`, `iterator`, `getGroup`, `findCounter` by enum, by group/name, and deprecated group/id/name, plus `incrCounter` by enum and the start of another `incrCounter` overload. This partial range establishes counters as mutable grouped job metrics with synchronized access.

## Control flow and state behavior

The common control pattern is stream-oriented and stateful:

- Writables mutate existing object instances during `readFields` to reduce allocation.
- SequenceFile writers serialize key/value records, optionally raw-copying value bytes, insert sync points, and expose seekable file positions for readers.
- Comparators either deserialize objects or operate directly over serialized byte slices for sort performance.
- Compression streams wrap input/output streams while compressor/decompressor objects hold native or Java codec state. `resetState`, `reset`, `finish`, `finished`, and `end` delimit lifecycle boundaries.
- Retry proxies intercept interface method calls and use policy decisions to sleep, retry, swallow void failures, or rethrow exceptions.
- IPC clients send one writable request to server addresses; servers accept calls into handler queues and invoke `call`. RPC layers encode Java interface calls into this writable transport and enforce protocol version compatibility.

State and persistence contracts are mostly binary:

- `Writable`, `Text`, `UTF8`, `VIntWritable`, `VLongWritable`, `TwoDArrayWritable`, `SortedMapWritable`, `ClusterStatus`, and `Counters` persist to `DataOutput` and recover from `DataInput`.
- `WritableName` persists compatibility indirectly by stabilizing class names in serialized streams.
- `VersionedWritable` persists a version byte and fails fast on mismatches unless subclasses handle compatibility.
- Compression codecs persist compressed stream formats identified by file suffixes and headers. BZip2/lzop header handling is particularly visible.
- RPC state is not durable; it is connection/request state plus metrics. Remote exceptions can be serialized to XML.

Synchronization appears on mutable shared or lifecycle-sensitive APIs: `SequenceFile.Writer` append/close/length methods, `WritableComparator` and factory/name registries, LZO/zlib compression state mutation, IPC server start/stop/join/listener access, and `Counters` group/counter access.

## Dependencies and integration points

Key dependencies visible in the signatures:

- Hadoop filesystem/configuration/progress: `FileSystem`, `Path`, `Configuration`, `Progressable`.
- Hadoop I/O: `Writable`, `WritableComparable`, `RawComparator`, `BinaryComparable`, `DataOutputBuffer`, `SequenceFile`, `MapFile`.
- Java stream and NIO primitives: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `DataOutputStream`, `ByteBuffer`, `CharacterCodingException`, `MalformedInputException`.
- Compression and native integration: `java.util.zip.Deflater`/`Inflater`, zlib, LZO native libraries, bzip2 stream code.
- Security/networking: `InetSocketAddress`, `InetAddress`, `ServerSocket`, `SocketFactory`, `UserGroupInformation`.
- Metrics/JMX: `MetricsContext`, `Updater`, `MetricsTimeVaryingRate`, management MBeans.
- XML/servlet support: SAX `Attributes`, `org.znerd.xmlenc.XMLOutputter`, servlet request/response classes.
- MapReduce: `JobClient`, `JobTracker.State`, `Counters.Group`, `Counters.Counter`.

The APIs are deeply integrated: SequenceFile and MapFile rely on Writable serialization, WritableComparator, and compression codecs; MapReduce keys/counters/status rely on Writable; IPC/RPC uses Writable payloads and `VersionedProtocol`; metrics observe IPC server behavior; retry proxies can wrap RPC protocol clients; compression codecs are selected by configuration and filename suffix.

## Risks and edge cases

- This is an API snapshot. It does not prove implementation correctness, only intended public/protected contracts.
- `SequenceFile.Writer.getLength()` returns a synchronized seek point, but block compression may seek to a key earlier than the most recently appended key. Tests must account for this.
- `SetFile.Writer.append` requires strictly increasing keys; violating sorted order likely corrupts search semantics.
- `Text.getBytes()` exposes a buffer larger than valid content; consumers must honor `getLength()`.
- `Text.charAt` and `find` use byte positions, not Java char indexes. Multi-byte UTF-8 callers can easily pass invalid trailing-byte positions.
- `UTF8` is deprecated in favor of `Text`; compatibility may still matter for old persisted data.
- `VersionedWritable` can reject old data unless subclasses catch `VersionMismatchException` and explicitly migrate fields.
- Static registries in `WritableComparator`, `WritableFactories`, and `WritableName` are global mutable state. Registration order and classloader behavior can affect behavior.
- BZip2Codec does not support pooled `Compressor`/`Decompressor` methods; generic codec users must tolerate `UnsupportedOperationException`.
- `BZip2Constants.rNums` is public and mutable as an array; the docs explicitly flag malicious-code risk.
- Raw `CBZip2InputStream`/`OutputStream` constructors require external handling of `BZ` magic bytes and are not thread-safe.
- LZO/lzop and zlib native paths depend on native library availability and configuration. Fallback and direct-buffer lifecycle should be tested.
- CodecPool requires callers to return compressor/decompressor instances; leaks can hold native resources.
- `Serializer` implementations must not buffer output, or interleaved stream writers can produce corrupt data.
- Java serialization and deserializing comparators are slower and may have compatibility/security concerns compared with Writable/raw comparators.
- Retry policies can hide failures for void methods (`TRY_ONCE_DONT_FAIL`) or retry indefinitely (`RETRY_FOREVER`); call sites need bounded policy choices.
- RPC protocol signatures are constrained; unsupported parameter/return types or non-IOException throws violate the RPC contract.
- `Client.call` parallel mode returns null for timed out or errored calls, so callers must not treat null as a valid response without disambiguation.
- Server `join()` explicitly does not wait for all subthreads, only for stop state.
- Metrics averages depend on an updating metrics context; with a null context, raw collection continues but averaging may not be visible.
- Runtime log-level servlet changes require web exposure controls outside this API surface.
- The chunk ends mid-`Counters`, so the full counter persistence/merge behavior must be completed by adjacent chunk research.

## Test signals

Useful validation targets derived from this API surface:

- Writable round trips: `Text`, `UTF8`, `VIntWritable`, `VLongWritable`, `TwoDArrayWritable`, `SortedMapWritable`, `VersionedWritable` subclasses, `ClusterStatus`, and `Counters`.
- UTF-8 correctness: valid/invalid byte validation, replacement versus exception behavior in `Text.decode`/`encode`, `charAt` on multi-byte boundaries, `find` byte offsets, and `utf8Length`.
- Raw comparator equivalence: `Text.Comparator`, `UTF8.Comparator`, and custom `WritableComparator` raw comparisons must match object comparison order.
- Variable-length integer boundaries: one-byte thresholds, negative encodings, max/min int and long, `getVIntSize`, byte-array readers, and stream readers.
- SequenceFile writer/reader flows: normal append, object serializer append, raw append, sync points, `getLength` seekability, compressed and block-compressed behavior, and segment cleanup/preservation.
- SetFile sorted-key contract: append increasing keys, reject or expose failure on out-of-order keys, seek/get/next behavior with custom comparators.
- Compression matrix: codec factory suffix lookup, configured codec class lists, pool get/return lifecycle, BZip2 unsupported pooled methods, BZip2 magic handling, gzip reset/finish semantics, lzop header/checksum verification, native LZO/zlib availability fallbacks, and stream close/finish not losing trailing bytes.
- Retry policies: exact retry counts/timing decisions using controlled policies, exception-specific and remote-exception-specific policy maps, void-method swallow behavior, and default method policy in `RetryProxy`.
- Serialization factory: `io.serializations` loading order, `WritableSerialization` round trips, `JavaSerialization` acceptance, serializer no-buffering behavior under interleaved writes, and deserializer comparator equivalence.
- IPC/RPC: client stop prevents further calls, single and parallel calls, null results for failed parallel calls, protocol version negotiation, `RPC.VersionMismatch`, remote exception unwrap/writeXml/valueOf, server start/stop/join lifecycle, remote address context inside calls, socket bind error reporting, and call queue/open connection metrics.
- Metrics/JMX: `RpcMetrics.doUpdates`, public rate mutation, MBean min/max reset, queue/processing time averages with and without an updating metrics context.
- LogLevel: CLI argument validation, servlet `doGet` behavior, permission/exposure assumptions in embedding web apps.

### subset-b-007290: lines 18683-24886

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 18683-24886

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.0, not executable Java implementation code. It records compatibility metadata for the classic `org.apache.hadoop.mapred` API: class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, abstract/static/final/synchronized/native flags, deprecation state, and embedded Javadoc contracts.

The range starts in the tail of `org.apache.hadoop.mapred.Counters` and ends just after the opening of `org.apache.hadoop.mapred.OutputFormat`, so adjacent chunks are required for complete class-level conclusions about those two APIs. The complete APIs inside the range cover counter internals, file input/output formats and splits, job submission and configuration, job history logging/parsing, job identity/profile/status/queue models, JobTracker control/query APIs, line-based input readers, mapper execution contracts, multi-file splitting, output collection, and output commit semantics.

## Purpose and Major API Surface

`Counters`, `Counters.Counter`, and `Counters.Group` define synchronized named MapReduce counters. The visible `Counters` tail covers group/string counter increments, enum counter lookup, merging another `Counters`, static `sum`, size, writable serialization, logging, textual compact forms, escaped compact round trips via `fromEscapedCompactString`, and `toString`. `Counter` exposes synchronized binary read/write, name/display-name access, display-name mutation, escaped compact formatting, current value, and increment. `Group` exposes group names/display names, localized display names, deprecated numeric counter lookup, lookup/create by counter name, size, read/write, and iteration over counters.

`DefaultJobHistoryParser` populates a precreated `JobHistory.JobInfo` from a job history file on a `FileSystem`. `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` are MapReduce validation exceptions; `InvalidInputException` retains a list of underlying `IOException` problems and formats an aggregate message.

`FileInputFormat<K,V>` is the base file-backed `InputFormat`. It provides path configuration helpers, optional `PathFilter` instantiation, `listStatus`, split computation, block-location lookup, minimum split size control, and a protected `isSplitable(FileSystem, Path)` hook for stream-compressed or whole-file inputs. Subclasses supply `getRecordReader`.

`FileOutputCommitter` implements the `OutputCommitter` lifecycle for filesystem outputs under `${mapred.output.dir}`, with `setupJob`, `cleanupJob`, `setupTask`, `needsTaskCommit`, `commitTask`, and `abortTask`. `TEMP_DIR_NAME` identifies the temporary directory convention. `FileOutputFormat<K,V>` is the base output format, with job-output compression configuration, compressor class lookup, output-spec validation, output path/work path/task output path helpers, and unique task-scoped filename/path generation for side-effect files.

`FileSplit` and `MultiFileSplit` are `InputSplit` implementations. `FileSplit` models one byte range in one file and serializes path, start, length, and host locations; its old constructor accepting `JobConf` is deprecated in favor of explicit host information. `MultiFileSplit` models whole-file collections, exposes per-file paths and lengths, computes total length, returns host locations, serializes with `Writable`, and formats itself with `toString`.

`ID` is the writable/comparable integer identity base with `getId`, `toString`, `hashCode`, `equals`, `compareTo`, binary read/write, static `read`, static `forName`, and protected `id` field. `JobID` extends it with a JobTracker identifier, parsing/pattern helpers, compare/equality/hash behavior, and binary read/write.

`InputFormat<K,V>` and `InputSplit` are the core input contracts. `InputFormat.getSplits(JobConf,int)` divides work, and `getRecordReader(InputSplit, JobConf, Reporter)` creates a reader for one split. `InputSplit.getLength()` reports byte length for scheduling and `getLocations()` reports locality hosts.

`JobClient` is the user-facing JobTracker client and implements `Tool`. It can construct against default or explicit JobTracker settings, initialize/close client resources, expose the staging `FileSystem`, submit jobs from a config file or `JobConf`, validate job directories for recovery, fetch `RunningJob` handles, task reports, cluster status, job lists, default map/reduce capacity, system directory, queue information, and run jobs synchronously through static `runJob`. Deprecated string-job-id overloads remain beside `JobID` overloads. `TaskStatusFilter` is the task-output filtering enum.

`JobConf` extends `Configuration` and is the central mutable MapReduce job description. This chunk covers constructors, jar selection, local directories and job-local scratch paths, user and working-directory settings, failed-task file retention, task JVM reuse, input/output format and output committer classes, map-output and job-output compression, map/final key/value classes, sort and grouping comparators, key-field comparator and partitioner options, mapper/map-runner/partitioner/reducer/combiner classes, speculative execution, map/reduce task counts, max attempts and tolerated failure percentages, job name/session id/priority, profiling settings, map/reduce debug scripts, job-end notification URI, queue name, and `DEFAULT_QUEUE_NAME`.

`JobConfigurable`, `JobContext`, and `JobEndNotifier` define job-level configuration and notification hooks. `JobConfigurable.configure(JobConf)` initializes components from job configuration. `JobContext` exposes `JobConf` and `Progressable`. `JobEndNotifier` starts/stops the notifier and registers local or JobTracker notifications from `JobConf` plus `JobStatus`.

`JobHistory` and inner classes are the history log API. Top-level methods initialize history storage, parse history files through a listener, toggle history disablement, and derive task log URLs. `HistoryCleaner` deletes old history. `JobInfo` tracks task maps and job metadata, encodes/decodes history file names, recovers history files, and logs submitted, initialized, started, finished, failed, killed, priority, and restart/timing information. `Keys`, `RecordTypes`, and `Values` are enums for history records. `Listener` receives parsed records. `Task`, `TaskAttempt`, `MapAttempt`, and `ReduceAttempt` provide event logging for task and attempt start/finish/fail/kill, including counters, tracker/http-port, state, shuffle/sort times, and task type; several older host-only overloads are deprecated.

`JobPriority`, `JobProfile`, `JobQueueInfo`, and `JobStatus` are job metadata/value objects. `JobProfile` stores user, typed and string job IDs, job file, URL, job name, queue name, and writable serialization; older string-ID constructor and `getJobId` are deprecated. `JobQueueInfo` stores queue name and scheduling info with writable serialization. `JobStatus` stores setup/map/reduce/cleanup progress, run state, start time, user, scheduling info, priority, clone support, synchronized accessors/mutators, writable serialization, and integer states `RUNNING`, `SUCCEEDED`, `FAILED`, `PREP`, and `KILLED`; its `getJobId` string accessor is deprecated.

`JobTracker` is the central MapReduce service API and implements `MRConstants`, `InterTrackerProtocol`, `JobSubmissionProtocol`, and `TaskTrackerManager`. The public surface includes tracker startup/shutdown, protocol versioning, restart/recovery status, instrumentation class configuration, address resolution, the long-running `offerService`, submission counts, tracker host/ports/start time, running/failed/completed jobs, task tracker status, network topology resolution, cache levels, listeners, queue manager access, build/filesystem information, synchronized heartbeat handling, adaptive heartbeat intervals, task tracker error reports, job-id allocation, job submission, cluster status, kill/priority operations, job profiles/status/counters/task reports/completion events/diagnostics, task killing and assigned tracker lookup, system directory/local job file paths, queues, and a debug-oriented `main`. `JobTracker.IllegalStateException` reports submit-before-ready, and `JobTracker.State` is the service state enum.

`KeyValueLineRecordReader`, `KeyValueTextInputFormat`, `LineRecordReader`, and deprecated `LineRecordReader.LineReader` cover line-oriented text input. `KeyValueLineRecordReader` splits each line at a configurable separator byte, emits `Text` key/value pairs, and exposes synchronized `next`, `getPos`, and `close`. `KeyValueTextInputFormat` configures splitability and record readers for text key/value files. `LineRecordReader` emits `LongWritable` file offsets and `Text` lines from a split or stream. Its nested `LineReader` is deprecated in favor of `org.apache.hadoop.util.LineReader`.

`MapFileOutputFormat` writes `MapFile` outputs and can open generated readers or fetch an entry using a `Partitioner`. `Mapper`, `MapRunnable`, `MapRunner`, `MapReduceBase`, and `OutputCollector` define classic map execution. `Mapper.map` transforms one input pair into zero or more intermediate pairs, using `Reporter` for progress/status/counters. `MapRunnable.run` owns the full record-reading loop for advanced mapper behavior; `MapRunner` is the default runner. `MapReduceBase` supplies no-op `configure` and `close`. `OutputCollector.collect` emits mapper/reducer outputs.

`MultiFileInputFormat` creates nearly equal-length `MultiFileSplit`s from input files while leaving split readers to subclasses. `OutputCommitter` is the abstract job/task output commit protocol. It defines job setup/cleanup, task setup, `needsTaskCommit`, `commitTask`, and `abortTask`, and documents that commit promotes task temporary output to the final job output location. The range ends at the start of `OutputFormat`, showing only the beginning of `getRecordWriter`.

## Control Flow and Behavioral Contracts

The XML has no method bodies, but the public contracts imply the classic MapReduce control flow. A user constructs and mutates `JobConf`, selecting input/output formats, mapper/reducer/combiner/partitioner classes, comparators, compression, speculative execution, attempts, failure tolerance, debug scripts, profile settings, queue, and notifications. `JobClient.submitJob` validates input/output specs, computes `InputSplit`s, stages the jar/configuration into the MapReduce system directory, submits to `JobTracker`, and returns a `RunningJob`; `JobClient.runJob` then polls until completion.

File input flow starts with `FileInputFormat` static input path configuration. At submission or task setup time the format lists statuses, applies optional path filters, validates non-empty inputs, computes target split sizes from goal/min/block size, maps offsets to block locations for locality, and emits `InputSplit`s. A task passes each split to `getRecordReader`, and readers such as `LineRecordReader` or `KeyValueLineRecordReader` repeatedly fill caller-supplied key/value objects until `next` returns false.

Map execution flow is `MapRunner` by default: configure the mapper from `JobConf`, read key/value pairs from `RecordReader`, call `Mapper.map` for each record, emit outputs through `OutputCollector`, and use `Reporter` to keep the task alive, set status, and update counters. Custom `MapRunnable` implementations can replace that loop for advanced behavior such as asynchronous or multithreaded mapping.

Output flow has a two-stage commit contract. `OutputFormat.checkOutputSpecs` validates the configured output path before execution. `OutputCommitter.setupJob` prepares job output, `setupTask` prepares a task attempt, task code writes under the work output directory when using `FileOutputCommitter`, `needsTaskCommit` avoids unnecessary commits, `commitTask` promotes successful attempt output, and `abortTask` discards failed or killed attempt output. `cleanupJob` removes temporary job output after completion.

JobTracker flow is RPC/service oriented. TaskTrackers periodically call synchronized `heartbeat` with status and response ids; the JobTracker processes progress and returns launch/kill/reset instructions. Clients obtain new job IDs, submit jobs, query cluster/job/task state, fetch completion events and diagnostics, kill jobs or tasks, change priority, and query queues. Recovery APIs expose whether the JobTracker restarted, whether recovery completed, and how long it took.

History flow is append-and-parse. `JobHistory.init` sets up history files, `JobInfo.logSubmitted` creates a per-job history file and can disable future history when creation fails, subsequent job/task/attempt log methods append structured records, and final job/task methods close the job history file or mark terminal state. `parseHistoryFromFS` streams each parsed record to a `Listener`, while `DefaultJobHistoryParser` builds an object model in `JobInfo`.

Counter flow is synchronized mutable aggregation. Tasks and jobs increment counters by enum or string group/name, groups create counters on demand, `incrAllCounters` and `sum` merge counter sets, counters serialize through `Writable`, and escaped compact strings round-trip through parser/formatter APIs for history/log transport.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API compatibility data. Runtime persistence described by this chunk includes `Writable` binary formats for counters, counter groups, file splits, multi-file splits, IDs, job IDs, job profiles, queue info, and job status. Compatibility depends on stable field order, type names, string escaping, enum names, counter names/display names, and synchronized read/write symmetry.

`JobConf` is the largest mutable state holder in the chunk. It persists job behavior through configuration keys for jars, local dirs, user, working directory, format classes, committer class, codec classes, key/value classes, comparators, mapper/reducer/combiner/partitioner, speculative execution, task counts, retry/failure thresholds, priority, profiling, debug scripts, notifications, scratch directories, and queues. Some settings are admin-final configuration parameters and may not be alterable by applications.

Filesystem side effects are central. `FileInputFormat` lists input paths and block locations. `FileOutputFormat` checks output existence, creates task output paths, and exposes work output directories. `FileOutputCommitter` creates/removes temporary directories and promotes task outputs to final output. `JobClient` stages jar/configuration files into the system directory. `JobTracker` stores local job conf files and manages job state. `JobHistory` writes master and per-job history files and `HistoryCleaner` deletes old history.

Operational state includes live JobTracker service state, heartbeat response ids, job/task/attempt objects, task tracker topology and cache locality, listeners, queues, instrumentation, cluster status, progress values, counters, task reports, diagnostics, completion events, and notification registrations.

Line readers and record readers hold stream offsets, split boundaries, separators, current position, and open input streams. Their synchronized `next`, `getPos`, and `close` methods indicate mutable reader state that must not be concurrently advanced without coordination.

External side effects include job-end notification URIs, debug scripts distributed through `DistributedCache` and executed on failed tasks with stdout/stderr/syslog/jobconf arguments, profiler JVM arguments writing profile output into user logs, and `JobShell`/`IsolationRunner` command-line entry points for running jobs or isolated tasks.

## Dependencies and Integration Points

The covered APIs integrate with Hadoop filesystem types (`FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `PathFilter`), serialization types (`Writable`, `WritableComparable`, `RawComparator`, `Text`, `LongWritable`, `MapFile`, `SequenceFile`), compression (`CompressionCodec`), configuration (`Configuration`, `JobConf`, integer ranges), progress (`Progressable`, `Reporter`), and distributed cache/debug facilities.

Classic MapReduce integration points include `InputFormat`, `InputSplit`, `RecordReader`, `Mapper`, `MapRunnable`, `OutputCollector`, `Partitioner`, `Reducer`, `OutputFormat`, `RecordWriter`, `OutputCommitter`, `JobContext`, `TaskAttemptContext`, `RunningJob`, `TaskReport`, `TaskCompletionEvent`, and queue/job status models.

JobTracker APIs integrate across RPC protocols (`InterTrackerProtocol`, `JobSubmissionProtocol`, `TaskTrackerManager`), task trackers, topology nodes (`org.apache.hadoop.net.Node`), queue management, instrumentation, cluster status, recovery, and build/version information. JobClient integrates user applications with those protocols and with the `Tool` command-line contract.

History APIs integrate with `FileSystem`, counters, job/task/attempt IDs, task log URLs, plain-text key/value history file formats, URL encoding/decoding of file names, and listener-based parsing for web UIs or offline tools.

Compatibility tooling depends on exact XML signatures and attributes. Public/protected additions, removals, type changes, generic signature changes, exception list changes, synchronization flag changes, deprecation text changes, and Javadoc contract changes are meaningful JDiff signals for Hadoop 0.19.0.

## Risks and Compatibility Notes

This chunk is partial at both ends. It should not be used alone to summarize all of `Counters` or all of `OutputFormat`.

Several APIs expose legacy Hadoop `mapred` contracts and intentionally retain deprecated overloads. Removing string-job-id methods, the old `FileSplit(JobConf)` constructor, old history logging overloads, `JobProfile.getJobId`, `JobStatus.getJobId`, or nested `LineRecordReader.LineReader` would break source compatibility for older applications even when newer replacements exist.

Serialization compatibility is high risk. Counter, split, ID, profile, queue, and status binary formats are used across task/job RPC, history, and persisted staging data. Changing read/write order, string encodings, enum names, ID parsing, or counter escaped compact formats can break old jobs, history parsers, or clients.

File output commit behavior is correctness-critical under speculative execution. The docs require attempt-specific temporary output under `_temporary/_${taskid}` so simultaneous attempts do not clobber each other. Writers that bypass `getWorkOutputPath`, use non-unique side-effect paths, or promote failed attempt output can corrupt final job output.

Input splitting affects correctness, locality, and parallelism. Incorrect `isSplitable` decisions can split non-splittable compressed streams or whole-file formats; wrong split-size/block-index logic can miss bytes, duplicate bytes, or reduce data locality. `MultiFileSplit` changes the atomic split unit from byte range to whole file, which record readers must honor.

JobConf settings interact in subtle ways. Map-output classes can differ from final output classes, grouping comparators can differ from sort comparators, combiner behavior must be compatible with reducer semantics, and `setNumMapTasks` is advisory through split generation. Admin-final parameters may reject application overrides.

JobTracker APIs expose synchronized and unsynchronized state access. The XML marks key mutating/query methods synchronized (`heartbeat`, job submission, kill/priority, task reports, counters, diagnostics), but many collection-returning methods are not synchronized. Callers and maintainers should treat returned vectors/lists/status objects as snapshots or shared mutable state depending on implementation.

History files have explicit format evolution. Version 0 used quoted values, while Version 1 changes delimiter and escapes values. Parsers and loggers must preserve escaping, record types, keys, and terminal close behavior so web/history tools can parse both older and newer logs.

Notifications, debug scripts, and profiling run at operational boundaries. URI substitution for `$jobId`/`$jobStatus`, distributed-cache symlink requirements, child JVM profiler arguments, and failed-task script execution all have security, quoting, and failure-propagation risks.

## Test Signals

JDiff validation should confirm this XML remains well-formed and preserves all public/protected class/interface boundaries in the line range, including partial `Counters` and partial `OutputFormat`. Compatibility checks should compare constructors, methods, fields, generic type strings, declared exceptions, visibility, static/final/abstract/synchronized flags, implemented interfaces, inheritance, and deprecation text.

Counter tests should cover enum and string counter creation, group display names, deprecated numeric lookup, increment and merge behavior, `sum`, synchronized read/write round trips, `size`, iterator contents, `makeCompactString`, escaped compact string round trips including separator escaping, logging, and parse failures.

File input tests should cover input path set/add/get helpers, comma-separated paths, path filters, missing/empty inputs and aggregated invalid input errors, subclass `listStatus`, split-size calculation, block-location index lookup, splitability for compressed and non-compressed files, and `RecordReader` creation for concrete formats.

File output and commit tests should cover output compression flags and codec class lookup, missing output paths, existing output path rejection through `FileAlreadyExistsException`, invalid job conf failures, `getWorkOutputPath`, `getTaskOutputPath`, unique custom filenames, speculative attempt side-effect files, `setupJob`, `setupTask`, `needsTaskCommit`, `commitTask`, `abortTask`, and `cleanupJob`.

Split and ID tests should round-trip `FileSplit`, `MultiFileSplit`, `ID`, and `JobID` through `DataOutput`/`DataInput`; verify file path/start/length/locations, multi-file path/length arrays and total length, host locality, string parsing through `forName`, compare/equality/hash behavior, and job ID pattern generation.

JobClient and JobTracker tests should use controlled or mocked protocols to cover initialization/close, filesystem handle acquisition, job submission from file and `JobConf`, job directory validation for recovery, `RunningJob` lookup, task reports for map/reduce/setup/cleanup, cluster status, job listing, synchronous `runJob` polling, task output filters, system directory, queues, job priority changes, kill job/task, diagnostics, completion events, heartbeat response handling, adaptive heartbeat interval calculation, restart/recovery state, queue manager access, and submit-before-ready errors.

JobConf tests should verify every covered setter/getter pair and default: jar and jar-by-class detection, local dir cleanup/path selection, user and working directory, failed-task file retention and patterns, tasks per JVM including `-1`, default input/output format and committer classes, map/job compression codec classes, map and final key/value classes, raw comparators, key-field comparator/partitioner option strings, mapper/map runner/partitioner/reducer/combiner classes, speculative execution flags, task counts, attempts, failure percentages, job name/session/priority, profile ranges and params, debug scripts, job-end notification URI substitution, job-local dir, and queue name default.

History tests should cover initialization success/failure, disabling history, listener parsing, `DefaultJobHistoryParser` object population, task log URL construction with missing fields, history cleaner retention, filename/path encode/decode, history file recovery choosing the oldest duplicate, all job/task/map-attempt/reduce-attempt log event methods including deprecated overload compatibility, counters in finished events, shuffle/sort times, task type values, escaped values, and Version 0/Version 1 parsing.

Text input and mapper tests should cover line boundary handling, split starts that begin mid-line, progress and position reporting, close idempotence, configurable key/value separator bytes, missing separator producing empty value, compressed splitability in `KeyValueTextInputFormat`, default `MapRunner` invoking mapper for all records, no-op `MapReduceBase`, custom `MapRunnable`, reporter progress/status/counters, output collection, and map-only jobs with zero reducers.

MapFile and multi-file tests should cover `MapFileOutputFormat` writer creation, opening partition readers, `getEntry` partition selection, `MultiFileInputFormat` nearly equal-length split construction, empty and many-small-file inputs, `MultiFileSplit` serialization, and record readers that treat each path as an atomic file.

### subset-b-007291: lines 24887-30897

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 24887-30897

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.0, not Java implementation source. It records public and protected API metadata for a large part of the legacy `org.apache.hadoop.mapred` surface, then continues into `org.apache.hadoop.mapred.jobcontrol`, `org.apache.hadoop.mapred.join`, and the beginning of `org.apache.hadoop.mapred.lib`. The XML captures class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, field constants, visibility, static/final/abstract/synchronized/native flags, deprecation text, and embedded Javadoc contracts.

The chunk starts inside `org.apache.hadoop.mapred.OutputFormat` at `checkOutputSpecs`, then covers output log filtering, partitioning, record reader/writer contracts, reducer/reporter/job status APIs, sequence-file formats and filters, skip-bad-record configuration, task IDs/events/logs/reports, `TaskTracker`, text input/output formats, job-control orchestration, join input formats/readers/parsers/tuple state, chain mapper/reducer composition, multiple-input delegation, field selection, identity mapper/reducer helpers, and most of `InputSampler` through the `SplitSampler` constructors.

## Purpose and Major API Surface

`OutputFormat.checkOutputSpecs(FileSystem, JobConf)` validates output specifications before job submission, typically rejecting output paths that already exist. The preceding part of `OutputFormat` is outside this chunk, but the local lines also include the interface-level contract that an `OutputFormat` validates output specs and supplies a `RecordWriter` for job output stored in a `FileSystem`.

`OutputLogFilter` implements `PathFilter` and rejects paths containing `_logs`, allowing clients to list normal output files while hiding MapReduce log directories.

`Partitioner<K2,V2>` extends `JobConfigurable` and defines `getPartition(K2 key, V2 value, int numPartitions)`. It maps intermediate records to reduce partitions, normally by hashing the key or a key subset; the number of partitions matches the number of reduce tasks.

`RecordReader<K,V>` defines the map-input read contract: `next(K,V)`, `createKey()`, `createValue()`, `getPos()`, `close()`, and `getProgress()`. It converts byte-oriented `InputSplit` data into record-oriented key/value pairs for mappers and reducers. `RecordWriter<K,V>` is the output-side counterpart with `write(K,V)` and `close(Reporter)`.

`Reducer<K2,V2,K3,V3>` extends `JobConfigurable` and Hadoop `Closeable`, with `reduce(K2, Iterator<V2>, OutputCollector<K3,V3>, Reporter)`. Its Javadoc documents the shuffle, sort, and reduce phases, secondary-sort comparators, object reuse hazards for keys and values, reporter progress/counters/status, and the fact that reducer output is not re-sorted.

`Reporter` extends `Progressable` and exposes task status, counters, input-split access for maps, and a `Reporter.NULL` no-op instance. It supports `setStatus`, counter lookup by group/name, counter increments by enum or string group/name, `getInputSplit`, and progress reporting inherited from `Progressable`.

`RunningJob` is the client-facing handle for a submitted job. It exposes job identity/name/file/tracking URL, map/reduce/setup/cleanup progress, completion/success checks, blocking wait, integer job state, kill operations, priority changes, task-completion event retrieval, task-attempt kill by `TaskAttemptID`, deprecated task kill by string, and counters.

The sequence-file APIs provide binary/text/raw alternatives around `SequenceFile`:

- `SequenceFileAsBinaryInputFormat` and nested `SequenceFileAsBinaryRecordReader` read raw key and value bytes into `BytesWritable`, expose key/value class names, support synchronized `next`, and track position/progress within a `FileSplit`.
- `SequenceFileAsBinaryOutputFormat` writes `BytesWritable` key/value pairs while allowing the persisted SequenceFile key/value classes to differ from the actual `BytesWritable` writer type. It exposes static setters/getters for output key/value classes, `getRecordWriter`, and `checkOutputSpecs`. Its protected `WritableValueBytes` wrapper implements `SequenceFile.ValueBytes` for `appendRaw`.
- `SequenceFileAsTextInputFormat` and `SequenceFileAsTextRecordReader` convert SequenceFile keys and values to `Text` by calling `toString`.
- `SequenceFileInputFilter` wraps `SequenceFileInputFormat` with a configurable `Filter`, plus `FilterBase`, `MD5Filter`, `PercentFilter`, and `RegexFilter`. Filters are configured through `Configuration` and decide acceptance from record keys using MD5 modulus, record-number frequency, or regex matching.
- `SequenceFileInputFormat`, `SequenceFileOutputFormat`, and `SequenceFileRecordReader` expose the base old-API SequenceFile read/write contracts, including listing statuses, creating record readers/writers, opening generated readers, setting/getting compression type, creating keys/values, synchronized reads/seeks/closes in the record reader, and protected `Configuration` state.

`SkipBadRecords` is a static configuration utility for skip mode. It controls attempts before skipping begins, automatic mapper/reducer processed-record counter increments, skip output path, maximum acceptable skipped records/groups around failures, and exposes the special counter group plus mapper/reducer processed counter names.

`StatusHttpServer` extends `HttpServer`, and nested `TaskGraphServlet` writes SVG task-status graphics with public width/height/margin constants.

`TaskAttemptContext` extends `JobContext` and exposes `getTaskAttemptID()` and `getJobConf()`.

`TaskAttemptID` and `TaskID` are immutable, writable, comparable identifiers. `TaskID` identifies a map or reduce task within a `JobID`; `TaskAttemptID` identifies an attempt within a `TaskID`. Both expose constructors from structured parts, accessors, `isMap`, equality/comparison/string/hash behavior, `readFields`, `write`, static `read`, static `forName`, and regex-pattern factory methods for matching IDs. Deprecated string parsing is explicitly discouraged in favor of constructors and `forName`.

`TaskCompletionEvent` is a `Writable` record used by the JobTracker to track task completion. It stores event id, task attempt id, task status enum, task tracker HTTP location, run time, map/reduce identity helpers, equality/hash/string behavior, serialization, and an `EMPTY_ARRAY` constant. Deprecated string task-id accessors are retained alongside typed `TaskAttemptID` accessors.

`TaskLog`, `TaskLog.LogName`, `TaskLogAppender`, and `TaskLogServlet` define user-log file lookup, log synchronization/cleanup, log length, stdout/stderr/debug wrapping for child commands, shell quoting, log4j task appending, and HTTP serving of task logs from TaskTrackers. `TaskLog` depends on the `hadoop.log.dir` system property, and command-capture methods can optionally tail output and write pid files.

`TaskReport` is a `Writable` task-state summary with typed and deprecated string task ids, progress, state, diagnostics, counters, start/finish time, equality/hash, and serialization.

`TaskTracker` implements `MRConstants`, `TaskUmbilicalProtocol`, and `Runnable`. It is the worker daemon API for starting and tracking tasks, contacting the JobTracker, cleaning local storage, managing JVM/task memory, serving map outputs, processing child-task heartbeats, reporting diagnostics and next-record ranges, mediating commit permission, marking tasks done, handling shuffle/filesystem errors, retrieving map completion events, recording lost map output, exposing idle state, and providing a `main` entry point. Its nested `MapOutputServlet` serves map outputs over Jetty.

`TextInputFormat` reads plain text as `LongWritable` byte offsets and `Text` lines; it is configurable, checks splitability, and creates a line record reader. `TextOutputFormat` writes plain text, and its protected `LineRecordWriter` writes synchronized key/value lines to a `DataOutputStream` with configurable separator behavior implied by its constructor.

`org.apache.hadoop.mapred.jobcontrol.Job` wraps a `JobConf` plus dependencies and state. It exposes job name/id, assigned MapReduce `JobID`, `JobConf`, state, message, `JobClient`, dependency list, dependency addition only while waiting, completion/readiness checks, protected submit, and integer state constants `SUCCESS`, `WAITING`, `RUNNING`, `READY`, `FAILED`, and `DEPENDENT_FAILED`.

`JobControl` manages a group of dependent `Job` instances in a thread. It exposes state-specific job lists, synchronized job addition, batch addition, thread state, stop/suspend/resume, all-finished checks, and `run()` loop behavior that checks running jobs, updates waiting jobs, and submits ready jobs.

The join package provides composable old-API input and reader abstractions:

- `ResetableIterator<T>` defines a stateful FIFO replay iterator over `Writable` values with `hasNext`, `next`, `replay`, `reset`, `add`, `close`, and `clear`. Implementations include `EMPTY`, `ArrayListBackedIterator`, and `StreamBackedIterator`.
- `ComposableInputFormat` refines `InputFormat` to require a `ComposableRecordReader`. `ComposableRecordReader` extends `RecordReader` and `Comparable`, adding reader id, current key cloning, non-empty probing, skip-through-key behavior, and collector acceptance for join keys.
- `CompositeInputFormat` parses `mapred.join.expr`, supports default and user-defined join operators via `mapred.join.define.<ident>`, accepts a comparator through `mapred.join.keycomparator`, builds aligned `CompositeInputSplit` instances, creates composable readers, and has static `compose` helpers for `tbl(...)` and operator expressions.
- `CompositeInputSplit` aggregates child `InputSplit` instances, exposes per-child and aggregate length/location metadata, and serializes as count/classes/splits. Child splits must have public default constructors.
- `CompositeRecordReader` is the abstract base for joins over sorted, partition-compatible child readers. It owns a `JoinCollector` and child reader array, maintains a priority queue ordered by `WritableComparator`, fills collectors for matching keys, delegates skip/close/progress, creates common keys/internal tuple values, and leaves concrete join behavior to `combine`.
- `InnerJoinRecordReader`, `OuterJoinRecordReader`, `OverrideRecordReader`, `JoinRecordReader`, and `MultiFilterRecordReader` implement or refine join semantics. Inner join emits only full tuples, outer join emits union-style tuples, override behavior selects override values, `JoinRecordReader` emits `TupleWritable`, and `MultiFilterRecordReader` emits a derived writable value through abstract `emit`.
- `Parser` and nested `Node`, token, numeric/string token, node token, and `TType` classes implement a simple shift-reduce parser for join expressions. `Parser.Node` keeps a static identifier-to-record-reader-constructor map and per-node id, identifier, and comparator class.
- `TupleWritable` stores multiple `Writable` children with presence bits, supports `has`, `get`, `size`, equality/hash, iteration, string formatting, and serialization of count/types/objects. Its docs warn that it is join-framework-specific rather than a general-purpose tuple type.
- `WrappedRecordReader` adapts a normal `RecordReader` into `ComposableRecordReader`, caches the head key/value pair, supports skip and collector acceptance for matching keys, delegates creation/progress/position/close, and implements ordering/equality by head key comparison.

The beginning of `org.apache.hadoop.mapred.lib` covers reusable MapReduce building blocks:

- `ChainMapper` lets multiple mapper classes run inside a single map task, storing chain configuration through static `addMapper`, then invoking configured mappers in `configure`, `map`, and `close`.
- `ChainReducer` composes one reducer followed by zero or more mappers inside a reduce task, with static `setReducer` and `addMapper` plus runtime `configure`, `reduce`, and `close`.
- `DelegatingInputFormat` and `DelegatingMapper` support `MultipleInputs`, delegating splits and mapper behavior by input path.
- `FieldSelectionMapReduce` is both mapper and reducer for selecting delimited fields into output keys and values using `mapred.data.field.separator`, `map.output.key.value.fields.spec`, and `reduce.output.key.value.fields.spec`.
- `HashPartitioner` implements `Partitioner` using `Object.hashCode()`.
- `IdentityMapper` and `IdentityReducer` pass records through unchanged.
- `InputSampler` implements `Tool`, writes partition files for `TotalOrderPartitioner`, and provides command-line driver behavior. Nested sampler types include `IntervalSampler`, `RandomSampler`, `Sampler`, and the visible start of `SplitSampler`.

## Control Flow and Behavioral Contracts

The old MapReduce data path described by this chunk starts with `InputFormat` creating `RecordReader` instances over `InputSplit`s. `RecordReader.next` fills caller-provided reusable key/value objects until EOF, while `getProgress` and `getPos` report progress. Mapper output is partitioned through `Partitioner.getPartition`, shuffled and sorted by the framework, then passed to `Reducer.reduce` once per grouped key with an iterator of values. Reducers and long-running readers/writers are expected to use `Reporter` to report liveness, status, and counters.

Output flow is mediated through `OutputFormat`. The framework calls `checkOutputSpecs` at submission time to catch invalid output targets, then uses `getRecordWriter` to write task outputs. Text and SequenceFile output formats adapt this contract to line-oriented files or SequenceFiles, with `RecordWriter.close(Reporter)` serving as the finalization hook.

Job monitoring flow uses `JobClient` to obtain a `RunningJob`, then repeatedly queries progress and completion state, fetches counters/events, waits for completion, changes priority, or kills jobs/task attempts. `TaskCompletionEvent` supplies the event stream for completed task attempts, while `TaskReport` supplies current task diagnostics/progress/counters.

Task execution flow centers on `TaskTracker`. Its `run` method is documented as a server retry loop that reconnects to the JobTracker and reinitializes stale state. Child JVMs call `getTask`, then periodically invoke synchronized `statusUpdate`, `ping`, diagnostic reporting, commit-pending/done notifications, and error callbacks through the task umbilical protocol. Reduce tasks ask for map completion events and may report shuffle errors; map outputs are served by `MapOutputServlet`.

Skip-bad-record flow is attempt-driven. After the configured number of failed attempts, tasks report next record ranges to the TaskTracker so later attempts can skip suspect ranges. Counters named by `COUNTER_MAP_PROCESSED_RECORDS` and `COUNTER_REDUCE_PROCESSED_GROUPS` are central to range detection; automatic increments can be disabled for asynchronous or buffered applications such as streaming.

SequenceFile input flow varies by adapter. Binary readers expose raw bytes and class names, text readers stringify keys/values, filtered readers consult the configured `Filter.accept(key)` before emitting, and base record readers support seeking and synchronized read/close operations. Output flow can set persisted key/value metadata separately from actual `BytesWritable` values for raw binary writes.

Job-control flow is a dependency scheduler. `JobControl.run` repeatedly checks running jobs, promotes waiting jobs whose dependencies succeeded, submits ready jobs, and moves failures into failed/dependent-failed states. `Job.addDependingJob` is synchronized and allowed only while waiting, so dependencies are intended to be immutable once execution begins.

Join flow requires every child source to be sorted and partitioned identically. `CompositeInputFormat` parses the join expression, builds one composite split per aligned child-split index, and constructs a tree of composable readers. `CompositeRecordReader` keeps child readers in a priority queue by current key, fills a `JoinCollector` with values from children whose keys match, then concrete `combine` implementations decide whether a tuple/value should be emitted. Resetable iterators allow join collectors to replay values for nested or cross-product-style joins.

Chain mapper/reducer flow is in-task composition. Static configuration calls describe each mapper/reducer class, type transitions, per-stage `JobConf`, and pass-by-value versus pass-by-reference semantics. Runtime `configure` instantiates/configures the chain, `map` or `reduce` pipes records through the configured stages, and `close` tears all stages down.

Sampling flow for total-order partitioning calls a `Sampler` against an `InputFormat` and `JobConf`, sorts sampled keys with the job output key comparator, chooses partition boundary keys, and writes them to the partition file path from `TotalOrderPartitioner`. `RandomSampler`, `IntervalSampler`, and `SplitSampler` differ in how they choose records and splits.

## State, Persistence, and Side Effects

The XML itself is persistent API compatibility data for Hadoop 0.19.0. Runtime state represented by this chunk includes mutable job configuration, reader positions, writer output streams, reducer lifecycle state, reporter counters/status, running job state, task IDs, task completion events, task reports, task tracker daemon state, join parser/reader queues, tuple presence bits, job-control dependency and state tables, chain configuration, and sampler parameters.

Persistence and external effects are prominent. `OutputFormat` implementations validate and create filesystem outputs. Text and SequenceFile writers write to `FileSystem` paths. SequenceFile readers consume files and track byte positions. `SkipBadRecords` persists skip settings in `Configuration`/`JobConf` and writes skipped records under an output `_logs` subdirectory unless disabled. `TaskLog` resolves and mutates task log files under `hadoop.log.dir`, wraps commands to redirect stdout/stderr/debug output, may write pid files, and cleans old logs. `TaskLogServlet`, `StatusHttpServer.TaskGraphServlet`, and `TaskTracker.MapOutputServlet` write HTTP responses.

`TaskID`, `TaskAttemptID`, `TaskCompletionEvent`, `TaskReport`, `CompositeInputSplit`, and `TupleWritable` all implement Hadoop `Writable` serialization contracts. These serialized forms can cross RPC boundaries, be embedded in job/task metadata, or be persisted in intermediate data; method signatures and field ordering are compatibility-sensitive even though the XML does not show concrete field layouts.

`TaskTracker` has broad side effects: local disk cleanup on startup, shutdown of tasks/threads, communication with the JobTracker through `InterTrackerProtocol`, management of child JVM task assignment through `JvmManager`, task memory monitoring, task commit authorization, shuffle/map-output serving, and local filesystem error handling.

Join and chain APIs are stateful even when configured through static helpers. Join readers maintain cached head records, priority queues, `JoinCollector` iterators, parser constructor maps, and tuple writable values. Chain mapper/reducer configuration mutates `JobConf` so later task setup can reconstruct the pipeline.

Sampling and partition-file generation read input splits on the client side and write a partition file for `TotalOrderPartitioner`. `RandomSampler` explicitly warns that reading every split at the client can be expensive.

## Dependencies and Integration Points

The chunk is tightly integrated with the legacy `org.apache.hadoop.mapred` API: `JobConf`, `JobClient`, `RunningJob`, `InputFormat`, `InputSplit`, `FileSplit`, `FileInputFormat`, `FileOutputFormat`, `Mapper`, `Reducer`, `OutputCollector`, `Reporter`, `Counters`, `TaskStatus`, `TaskUmbilicalProtocol`, `InterTrackerProtocol`, `JvmManager`, `TaskMemoryManagerThread`, `MapTaskCompletionEventsUpdate`, and `SortedRanges.Range`.

Filesystem and IO dependencies include `org.apache.hadoop.fs.FileSystem`, `Path`, `PathFilter`, `FileStatus`, Java `DataInput`, `DataOutput`, `DataOutputStream`, `File`, and `IOException`. Sequence-file integration depends on `org.apache.hadoop.io.SequenceFile`, `SequenceFile.Reader`, `SequenceFile.ValueBytes`, `Writable`, `WritableComparable`, `WritableComparator`, `BytesWritable`, `Text`, `LongWritable`, and compression type configuration.

Runtime services include Apache Commons Logging, log4j `FileAppender` and `LoggingEvent`, servlet APIs (`HttpServlet`, requests, responses, `ServletException`), Hadoop `HttpServer`, Java networking (`InetSocketAddress`), Java collections, Java regex (`PatternSyntaxException`), reflection constructors for join parser nodes/readers, and command-line tooling through `Tool`.

Configuration keys and integration points visible in docs include `mapred.task.timeout`, `mapred.join.expr`, `mapred.join.define.<ident>`, `mapred.join.keycomparator`, `mapred.data.field.separator`, `map.output.key.value.fields.spec`, `reduce.output.key.value.fields.spec`, and the partition-file path used by `TotalOrderPartitioner`.

Compatibility integration is also explicit: deprecated string identifiers in `RunningJob`, `TaskCompletionEvent`, `TaskReport`, `Job`, and task-kill APIs remain beside typed `JobID`, `TaskID`, and `TaskAttemptID` replacements.

## Risks and Compatibility Notes

This chunk starts in the middle of `OutputFormat` and ends in the middle of `InputSampler.SplitSampler`; adjacent chunks are required for complete per-file synthesis. Within this chunk, however, all listed class/interface blocks between those boundaries were read and summarized.

The XML describes public API, not implementation bodies. Behavioral detail comes from signatures, synchronization flags, inheritance, and Javadoc, so implementation-specific algorithms must be verified against Java source if exact code paths are needed.

The old MapReduce API relies heavily on object reuse. `RecordReader.next` fills caller-provided objects, and reducer docs explicitly warn that framework-provided keys/values are reused. User code that retains keys or values must clone them; changing reuse semantics would affect memory and compatibility.

Task and job identifier APIs are compatibility-sensitive. String formats such as `task_...` and `attempt_...`, `forName`, regex-pattern helpers, `Writable` serialization, equality, comparison ordering, and deprecated string accessors are all observable by clients and logs.

Several APIs expose raw or weakly typed generics (`Class`, raw `OutputCollector`, raw `Mapper`/`Reducer` in chain runtime methods, parser reflection maps). Tightening signatures could break source compatibility with Hadoop 0.19 clients.

Threading is mixed. Some critical `TaskTracker`, `Job`, and writer/reader methods are synchronized, but many mutable objects (`JobControl` lists, join readers/iterators, task events/reports, task logs, chain stages) are not documented as thread-safe. Callers should assume task-local or externally synchronized use unless the contract says otherwise.

Skip-bad-record behavior can silently drop data around deterministic failures. The thresholds and counters must be tested carefully because `Long.MAX_VALUE`, zero, automatic counter increments, and null skip-output path all have special behavior.

Join APIs assume identical sort order and partitioning across inputs. If split alignment, key comparator, partitioning, or child input sort order differs, `CompositeRecordReader` may miss matches, produce incorrect tuples, or report misleading progress. `TupleWritable` is explicitly not a general-purpose persistence format.

Chain mapper/reducer pass-by-reference mode is an optimization with mutation risk. A mapper or reducer that modifies key/value objects unexpectedly can corrupt downstream stages unless pass-by-value serialization is used.

`TaskLog.captureOutAndError`, task log serving, map output serving, and `InputSampler.RandomSampler` can be expensive or security-sensitive. They touch local files, shell command strings, stdout/stderr redirection, HTTP endpoints, and client-side reads over potentially large inputs.

`HashPartitioner` depends on `Object.hashCode()`. Keys with unstable, non-deterministic, or poorly distributed hash codes can skew reducers or route equivalent logical keys inconsistently.

## Test Signals

JDiff-level validation should confirm this XML chunk remains well-formed around the package/class boundaries it covers, preserves every class/interface listed here, and keeps method names, generic signatures, parameter order, declared exceptions, visibility, synchronization/static/final/abstract flags, fields, and deprecation text stable.

Core old-API MapReduce tests should cover `RecordReader` object creation/reuse, EOF behavior, position/progress, close idempotence; `RecordWriter.write/close`; output-spec validation failures; `Partitioner.getPartition` bounds; reducer iterator processing, reporter progress/counters/status, and object-cloning expectations.

Reporter and running-job tests should cover no-op `Reporter.NULL`, enum and string counters, map-only `getInputSplit` failure outside mappers, progress values for map/reduce/setup/cleanup, non-blocking completion checks, `waitForCompletion`, job/task kill paths, priority changes, task completion event pagination, and counter retrieval.

SequenceFile tests should cover binary raw read/write class metadata, raw `BytesWritable` payload sizes, text conversion with `toString`, filtered reads for MD5/percent/regex filters, filter configuration validation, compression type round trips, reader seek/position/progress, split boundaries, and output-spec checks.

Skip-bad-record tests should cover default attempt threshold, zero disables skipping, `Long.MAX_VALUE` accepts broad ranges, auto-increment flags for mapper/reducer counters, manual counter increments for buffered/asynchronous processing, null skip output path, and skipped-record output under `_logs`.

Task identity and event tests should cover `TaskID` and `TaskAttemptID` constructors, string formatting, `forName` valid/malformed/null inputs, regex pattern generation with null wildcards, map/reduce comparison ordering, `Writable` read/write round trips, deprecated string accessors, `TaskCompletionEvent.Status`, map-task helpers, and event equality/hash.

TaskTracker and logging tests should cover startup cleanup, shutdown/close cleanup, JobTracker reconnect behavior, child `getTask`, heartbeat/status update, diagnostics, next-record range reporting, commit-pending/can-commit/done flow, shuffle/filesystem error handling, map-output-lost reporting, idle detection, memory-manager enabled/disabled branches, task log file lookup, log sync/cleanup, command wrapping with tail length and pid file, log4j appender close/flush, log servlet URL construction, and HTTP serving of map outputs/task logs.

Text format tests should cover compressed versus uncompressed splitability, CR/LF line endings, byte-offset keys, reporter usage during line reading, text writer separator handling, null key/value output behavior if supported by implementation, synchronized writer close, and filesystem output path creation.

Job-control tests should cover dependency addition while waiting versus after start, state transitions among waiting/ready/running/success/failed/dependent-failed, assigned `JobID` propagation, failure message propagation, `JobControl` suspend/resume/stop, all-finished detection, concurrent synchronized additions, and the run loop submitting only ready jobs.

Join tests should cover parser expression composition, default and custom join identifiers, comparator configuration, malformed expressions, composite split serialization/deserialization, child split capacity errors, aligned split count requirements, inner/outer/override semantics, nested joins, resetable iterator FIFO/replay/reset/clear/close, tuple presence bits and serialization, wrapped reader head caching, skip-through-key behavior, and progress as the minimum of child readers.

Library helper tests should cover chain mapper/reducer type compatibility, pass-by-value versus pass-by-reference mutation behavior, per-stage `JobConf` precedence, close ordering, delegating input format/mapper path dispatch through `MultipleInputs`, field-selection separator and range grammar including open ranges, identity mapper/reducer pass-through, hash partition bounds/distribution, and `InputSampler` interval/random/split sampling plus partition-file output for `TotalOrderPartitioner`.

### subset-b-007292: lines 30898-37232

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 30898-37232

## Chunk Scope

This chunk is a JDiff API snapshot for Hadoop 0.19.0, not implementation source. It starts at the tail of `org.apache.hadoop.mapred.lib.InputSampler.SplitSampler`, covers a large slice of old `mapred` helper APIs, aggregate and DB input/output helpers, Pipes submission, the original Hadoop metrics framework, and most of `org.apache.hadoop.net` through the beginning of `SocksSocketFactory`.

Because the file is generated compatibility XML, the control-flow, state, and persistence notes below are inferred from public signatures, inheritance, checked exceptions, fields, and embedded API docs rather than method bodies.

## Purpose

The chunk records public and protected API contracts that Hadoop clients, MapReduce jobs, metrics sinks, and network-aware placement code depended on in the 0.19 line. It is useful for compatibility research because it captures method names, overloads, parameter and return types, checked exceptions, visibility, static/synchronized markers, fields, and deprecation status.

At a high level, this slice documents:

- Old `org.apache.hadoop.mapred.lib` convenience mappers, reducers, input splitting, partitioning, multiple inputs, and multiple outputs.
- The `org.apache.hadoop.mapred.lib.aggregate` framework, which lets users describe simple counting/statistics jobs through descriptors and built-in aggregators instead of writing custom mapper/reducer logic.
- JDBC-backed `DBInputFormat` and `DBOutputFormat` contracts.
- `org.apache.hadoop.mapred.pipes.Submitter`, the API and CLI entry point for Hadoop Pipes jobs.
- Hadoop's pre-metrics2 metrics interfaces, contexts, records, file/Ganglia/JVM implementations, SPI records, and simple mutable metric wrappers.
- Networking utilities for DNS, rack mapping, socket factory selection, network topology, rack-distance sorting, non-blocking socket streams with timeouts, and SOCKS socket construction.

## Important APIs and Types

### `org.apache.hadoop.mapred.lib`

The first visible method is `InputSampler.SplitSampler.getSample(InputFormat<K,V>, JobConf)`, which samples the first `numSamples / numSplits` records from selected splits. The class itself begins in the previous chunk, so final synthesis should join this with adjacent lines.

`InverseMapper` is a `MapReduceBase` mapper that swaps input key/value order and emits `(value, key)`. `LongSumReducer` reduces `Iterator<LongWritable>` values by summing them for each key. `RegexMapper` and `TokenCountMapper` expose simple text-mapping helpers for regular-expression extraction and token counting.

`KeyFieldBasedComparator` extends `WritableComparator` and implements `JobConfigurable`. It compares serialized keys using a Unix/GNU sort-like subset: numeric sort, reverse sort, and `-k f[.c][opts][,f[.c][opts]]` key ranges separated by `map.output.key.field.separator`. `KeyFieldBasedPartitioner` applies a parallel field-selection grammar for partitioning and exposes a protected byte-range `hashCode` helper.

`MultipleInputs.addInputPath(...)` records input `Path` entries with path-specific `InputFormat` and optional `Mapper` classes, letting one job consume heterogeneous inputs. `NLineInputFormat` splits input so N lines form one split, aimed at parameter-sweep jobs where each line controls one mapper.

`MultipleOutputFormat<K,V>` is an abstract `FileOutputFormat` extension that creates composite record writers and lets subclasses derive output file names, actual keys, and actual values from `(key, value, leafName)`. It supports reducer-driven key-based file routing, map-only input-file-derived output names, and combinations of input file plus key. `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` supply concrete base writers for SequenceFile and text outputs.

`MultipleOutputs` is the richer named-output API. Static configuration methods define named outputs, multi-named outputs, output format/key/value classes, and optional counters. Runtime `getCollector(namedOutput, reporter)` and `getCollector(namedOutput, multiName, reporter)` return collectors for additional output files, and `close()` closes all opened named-output writers. Named output names must be word-like and cannot be reserved `part`; mapper-side named-output writes bypass the job's reduce phase.

`MultithreadedMapRunner` implements `MapRunnable` with a configurable thread pool (`mapred.map.multithreadedrunner.threads`, default 10). Its contract explicitly requires mapper implementations to be thread-safe.

`NullOutputFormat` discards output and has no output specs to validate. `TotalOrderPartitioner` partitions keys according to a partition file (`DEFAULT_PATH`, `setPartitionFile`, `getPartitionFile`) and is configured by `JobConf`.

### Aggregate Framework

The `org.apache.hadoop.mapred.lib.aggregate` package exposes a data-driven aggregation framework. The mapper emits keys whose prefix encodes an aggregation type; combiners and reducers instantiate the corresponding `ValueAggregator` and combine values.

Built-in aggregators include `DoubleValueSum`, `LongValueSum`, `LongValueMax`, `LongValueMin`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram`. The numeric/string aggregators expose `addNextValue`, `getReport`, type-specific getters such as `getSum()` or `getVal()`, `reset()`, and combiner-output lists. `UniqValueCount` tracks a bounded set of unique objects with configurable maximum item count. `ValueHistogram` consumes string/frequency pairs and reports unique count, min, median, max, average, standard deviation, details, and a `TreeMap` view.

`ValueAggregator` is the minimal aggregator protocol: add value, reset, produce a report, and produce combiner output. `ValueAggregatorDescriptor` generates aggregation-id/value pairs from input key/value objects and can be configured with `JobConf`; it defines `TYPE_SEPARATOR` and `ONE`.

`ValueAggregatorBaseDescriptor` provides standard aggregation type constants and helper factories such as `generateEntry` and `generateValueAggregator`. Its default descriptor generates record counts and per-input-file counts when file split information is available. `UserDefinedValueAggregatorDescriptor` dynamically instantiates a user descriptor by class name, delegates `generateKeyValPairs`, and supports `configure`.

`ValueAggregatorJobBase` stores the protected `aggregatorDescriptorList` and common mapper/reducer setup. `ValueAggregatorMapper` iterates descriptors to emit aggregation pairs. `ValueAggregatorCombiner` and `ValueAggregatorReducer` reduce `Text` keys and values based on the aggregation-type prefix; their opposite map/reduce methods are documented as no-ops that should not be called. `ValueAggregatorJob` creates `JobConf` or `JobControl` instances, wires descriptor classes, and has a `main` entry point for aggregate jobs.

### JDBC MapReduce Helpers

`DBConfiguration.configureDB` stores JDBC driver, URL, and optional credentials in a `JobConf`. Public property constants cover driver, URL, username, password, input table/fields/conditions/order/query/count query/input class, and output table/fields.

`DBInputFormat<T extends DBWritable>` configures database reads, creates `DBInputSplit` ranges, builds count queries, creates record readers, and has `setInput` overloads for table-based and query-based input. `DBInputSplit` implements split serialization through `readFields`/`write`, exposes `getStart`, `getEnd`, `getLength`, and returns no host locality. `DBRecordReader` constructs select queries, iterates rows into `LongWritable` keys and `DBWritable` values, reports position/progress, and closes database resources. `NullDBWritable` is a no-op placeholder.

`DBOutputFormat<K,V>` builds insert queries, validates output specs, creates `DBRecordWriter`, and has `setOutput`. `DBRecordWriter` writes `DBWritable` records through a JDBC `PreparedStatement` and closes its connection/statement. `DBWritable` defines the row-level `readFields(ResultSet)` and `write(PreparedStatement)` contract.

### Pipes Submitter

`org.apache.hadoop.mapred.pipes.Submitter` is both CLI and API for Hadoop Pipes. It extends/configures around `Configuration`, exposes setters/getters for the executable and whether record reader, mapper, reducer, and record writer are Java-side, controls whether to keep the generated command file, and exposes `submitJob`, `runJob`, `jobSubmit`, `run`, and `main`. It integrates with `RunningJob` and generic Hadoop command-line handling.

### Metrics Framework

`ContextFactory` is the singleton factory for `MetricsContext` instances. It loads attributes from `hadoop-metrics.properties`, supports attribute get/set/remove/list, creates named contexts by `<contextName>.class`, and defaults to `NullContext` when no implementation is configured.

`MetricsContext` is the main context interface: context name, start/stop/isMonitoring, close, create record, register/unregister updater, and `DEFAULT_PERIOD`. `MetricsRecord` models a record name plus tags and metrics; it supports typed `setTag`, `removeTag`, typed `setMetric`, typed `incrMetric`, `update`, and `remove`. Docs define buffered row semantics keyed by tag sets and warn that `update()` is atomic across instances with the same tags but a single `MetricsRecord` instance should not be shared concurrently. `Updater.doUpdates` is the periodic callback interface. `MetricsUtil` wraps common context creation and record creation tagged with host name. `MetricsException` is the unchecked metrics error type.

Concrete contexts include `metrics.file.FileContext`, which appends metrics to a configured file or stdout and flushes/closes it; `metrics.ganglia.GangliaContext`, which emits records to Ganglia; and `metrics.jvm.JvmMetrics`, a singleton `Updater` reporting JVM metrics. `metrics.jvm.EventCounter` is a Log4J appender that counts fatal/error/warn/info events.

The SPI layer centers on `AbstractMetricsContext`, `MetricsRecordImpl`, `MetricValue`, `OutputRecord`, `NullContext`, and `NullContextWithUpdateThread`. `AbstractMetricsContext` manages lifecycle, record creation, updater registration, periodic updates, record buffering, `emitRecord`, `flush`, and monitoring period. `MetricValue` distinguishes absolute from increment values. `OutputRecord` exposes metric and tag names/values for sink emission. Null contexts discard output; one variant still runs an update thread.

`metrics.util` includes `MBeanUtil` for JMX registration/unregistration and four mutable metric wrappers: `MetricsIntValue`, `MetricsLongValue`, `MetricsTimeVaryingInt`, and `MetricsTimeVaryingRate`. The simple int/long wrappers publish a changed value once on the next update. The time-varying wrappers publish per-interval deltas or average operation times and expose previous interval values; the rate metric tracks min/max and can reset them.

### Networking and Topology

`DNSToSwitchMapping.resolve(List<String>)` maps hostnames/IPs to rack/network paths with one-to-one output correspondence. `CachedDNSToSwitchMapping` wraps a raw mapping and caches resolved locations. `ScriptBasedMapping` extends that cache and implements `Configurable`, using `topology.script.file.name`.

`DNS` provides static direct and reverse lookup helpers for specific network interfaces and nameservers: reverse DNS, all IPs/default IP, all hosts/default host. `NetUtils` selects socket factories from Hadoop configuration, creates socket addresses from `host`, `host:port`, or URI-like strings, migrates old host/port config pairs to combined addresses, manages static hostname resolutions for tests, maps wildcard server bind addresses to client-connect addresses, wraps socket input/output streams with timeout-aware channel streams when available, and normalizes host names to textual IP addresses.

`NetworkTopology` models cluster topology as a tree of racks/switches/leaves. It can add/remove leaf nodes, test containment, look up nodes by path, report rack and leaf counts, compute distance through closest common ancestor, test same-rack placement, choose random nodes within or outside a scope, count available nodes excluding a list, stringify the tree, and `pseudoSortByDistance` so local node, local rack, or a random replica is preferred at the front of an array. Public constants include `DEFAULT_RACK`, `DEFAULT_HOST_LEVEL`, and `LOG`.

`Node` defines the topology-node contract: name, network location, parent, and level getters/setters. `NodeBase` implements it, normalizes path strings, builds a full path from a node, and stores protected mutable `name`, `location`, `level`, and `parent` fields.

`SocketInputStream` and `SocketOutputStream` adapt selectable socket channels to `InputStream`/`OutputStream` plus `ReadableByteChannel`/`WritableByteChannel` with read/write timeouts. Constructors configure the channel as non-blocking; docs warn that using the normal socket streams afterward can throw `IllegalBlockingModeException`. They expose `getChannel`, `isOpen`, synchronized `close`, `waitForReadable`/`waitForWritable`, and ByteBuffer-based channel methods. `SocketOutputStream.transferToFully(FileChannel, long, int)` loops until the requested byte count is transferred or throws EOF/timeout/IO errors.

`SocksSocketFactory` begins at the chunk boundary. Visible API includes constructors with default reflection-friendly initialization or an explicit `Proxy`, five `createSocket` overloads for unconnected, address, address+local bind, host, and host+local bind variants, and the beginning of `hashCode()`. The class continues in the next chunk.

## Control Flow and Behavioral Contracts

MapReduce helper control flow is mostly job-configuration driven. Static helpers such as `MultipleInputs`, `MultipleOutputs`, `DBInputFormat.setInput`, `DBOutputFormat.setOutput`, `TotalOrderPartitioner.setPartitionFile`, and aggregate job builders write contract information into `JobConf`; task-side objects then read it in `configure()` and execute through mapper/reducer/input/output interfaces.

Multiple-output writes flow from mapper/reducer code through a `MultipleOutputs` instance created in `configure()`, into named or multi-named `OutputCollector`s, then into output-format-specific record writers. The explicit `close()` contract is important because additional writers are opened lazily and are not the same as the job's default collector.

Aggregate jobs flow from descriptor-generated `(Text aggregationKey, Text value)` pairs to combiner/reducer grouping. The aggregation key prefix selects an aggregator implementation, values are added through `addNextValue`, and final output is produced through `getReport` or combiner output lists.

DB input flow is count query or split-range generation, split serialization, per-split SQL select construction, row iteration, and user `DBWritable.readFields(ResultSet)`. DB output flow is output configuration, SQL insert construction, per-record `DBWritable.write(PreparedStatement)`, and close/commit cleanup inferred from the writer API.

Metrics flow starts with `ContextFactory.getFactory()` loading attributes, `getContext()` constructing or reusing a context, `createRecord()` creating record buffers, application code setting tags/metrics and calling `update()`, and `AbstractMetricsContext` periodically invoking registered `Updater`s and sink-specific `emitRecord`/`flush`.

Networking flow uses configuration to choose socket factories and DNS/rack mapping implementations. Topology-aware code resolves names to rack paths, builds/updates a `NetworkTopology`, computes locality/distance, and reorders replica choices with `pseudoSortByDistance`.

Timeout stream flow depends on whether a socket has an associated channel. Channel sockets are switched to non-blocking mode and use select-style waits with timeouts; non-channel sockets fall back to JVM streams and normal socket timeout semantics.

## State and Persistence

Persistent or mutable state visible in this chunk includes:

- `JobConf` keys for multiple inputs/outputs, named-output counters, total-order partition files, aggregate descriptors, DB connection properties, DB input/output properties, Pipes executable and Java/native component choices, and N-line input settings.
- Runtime writer state in `MultipleOutputs`, which tracks opened named-output collectors until `close()`.
- Aggregator instance state: numeric sums/min/max, string min/max, unique-value sets, histogram maps, and descriptor lists.
- JDBC resources in DB record readers/writers: connections, statements, result sets, split ranges, current row position, and progress.
- Metrics factory attributes loaded from `hadoop-metrics.properties`; metrics context lifecycle state; buffered metric tables keyed by record name and tag set; update-thread state; file writer handles; Ganglia socket/output state; JVM/logging counters; and mutable metric wrapper values plus changed/previous-interval flags.
- DNS-to-switch cache entries, static hostname resolutions in `NetUtils`, network topology tree parent/level counters, rack/leaf counts, node path strings, and socket stream open/closed state.
- `NodeBase` stores mutable topology identity and hierarchy through protected fields, so topology operations can mutate parent and level during add/remove.

The XML itself persists no runtime state; it is the API compatibility artifact consumed by JDiff tooling.

## Dependencies and Integration Points

Major dependencies visible in this chunk:

- Old Hadoop `mapred` APIs: `JobConf`, `Mapper`, `Reducer`, `MapRunnable`, `RecordReader`, `OutputCollector`, `Reporter`, `InputFormat`, `OutputFormat`, `FileInputFormat`, `FileOutputFormat`, `SequenceFileOutputFormat`, `TextOutputFormat`, `RunningJob`, and `jobcontrol.JobControl`.
- Hadoop value and filesystem types: `Writable`, `WritableComparable`, `WritableComparator`, `Text`, `LongWritable`, `Path`, `FileSystem`, `InputSplit`, and `Progressable`.
- Hadoop configuration and utility layers: `Configuration`, `Configured`, `GenericOptionsParser`, `Tool`-style command execution, and IPC `Server`/`VersionedProtocol` references.
- Java standard APIs: `Iterator`, `ArrayList`, `Map.Entry`, `TreeMap`, `Set`, JDBC `Connection`/`PreparedStatement`/`ResultSet`, Java IO streams/files/channels, sockets, proxies, `InetAddress`, `InetSocketAddress`, `UnknownHostException`, JNDI `NamingException`, and reflection exceptions.
- Logging and monitoring integrations: Apache Commons Logging, Log4J appenders/events, JMX `ObjectName`, file output, and Ganglia.
- Cluster placement integrations: rack scripts via `topology.script.file.name`, DNS/network-interface lookups, static host resolution for tests, and socket factory configuration keys such as class-specific and default Hadoop RPC socket factories.

## Risks and Edge Cases

- This chunk is API XML only, so exact locking, cleanup, SQL transaction behavior, cache eviction, exception wrapping, and thread lifecycle details are not visible.
- The chunk starts mid-`InputSampler.SplitSampler` and ends mid-`SocksSocketFactory`; final per-file reconciliation must merge those class summaries with adjacent chunks.
- `MultithreadedMapRunner` can corrupt results if mapper implementations, output collectors, or shared user state are not thread-safe.
- `MultipleOutputs` requires explicit `close()`; forgetting it risks missing or truncated side outputs.
- Named output names have validation constraints and reserve `part`; collisions with generated part names or multi-name suffixes are compatibility risks.
- Mapper-side named-output records do not enter the reduce phase, which can surprise jobs expecting all mapper emissions to be reduced.
- `KeyFieldBasedComparator` and `KeyFieldBasedPartitioner` depend on field separators and sort-key grammar; off-by-one field/character positions or numeric parsing failures can change partition/sort behavior.
- `TotalOrderPartitioner` depends on external partition-file distribution and consistency with key comparator behavior.
- Aggregate framework keys encode type and id in `Text`; malformed prefixes or unknown aggregation types can route data to the wrong aggregator or fail late in reduce.
- `UniqValueCount` can grow memory until its maximum item bound; incorrect bounds can trade accuracy for memory pressure.
- Histogram input expects `value\tcount`-style strings; malformed counts affect statistics.
- DB formats expose credentials in `JobConf` and rely on JDBC driver availability. Query construction, split boundaries, transaction/commit semantics, and SQL dialect differences are likely failure points.
- DB input splits report no locality, so large table reads depend on database throughput rather than data-local scheduling.
- Metrics records are buffered and periodically emitted; `update()` does not immediately publish externally. Long-lived rows continue to emit until `remove()` is called.
- Metrics docs allow concurrent `update()` from different record instances with the same tags but warn against sharing one record instance concurrently.
- File metrics append to configured files or stdout; file permissions, disk-full errors, and flush/close handling are operational risks.
- DNS and reverse-DNS behavior depends on network interfaces, nameserver availability, and local resolver configuration.
- `CachedDNSToSwitchMapping` may retain stale rack mappings if topology changes.
- `NetworkTopology` requires leaf/non-leaf invariants and normalized paths; invalid parents or levels can break distance and same-rack decisions.
- `pseudoSortByDistance` only partially sorts: it promotes local/local-rack/random first choices and intentionally leaves the rest untouched.
- Channel-backed `SocketInputStream`/`SocketOutputStream` switch sockets to non-blocking mode; code that later uses `Socket.getInputStream()` or `Socket.getOutputStream()` directly may fail.
- Timeout handling differs between channel and non-channel sockets because non-channel streams ignore the wrapper timeout argument and rely on socket SO_TIMEOUT or blocking writes.

## Test Signals

Useful tests inferred from this API slice include:

- Compatibility parsing tests that verify all classes, interfaces, constructors, methods, fields, visibility, static/synchronized/final flags, and checked exceptions in this chunk remain stable for JDiff consumers.
- `InverseMapper`, `LongSumReducer`, `RegexMapper`, and `TokenCountMapper` functional tests for representative key/value inputs and IOException propagation.
- Key-field comparator and partitioner tests for `-k`, numeric, reverse, separator, missing-field, character-offset, and partition stability cases.
- `MultipleInputs` tests with two paths using distinct `InputFormat` and mapper classes.
- `MultipleOutputFormat` subclass tests for leaf-name, key/value rewrite, input-file-derived names, lazy writer creation, and close behavior.
- `MultipleOutputs` tests for single named outputs, multi named outputs, counter enablement, reserved/invalid names, mapper-side bypass of reduce, and required close.
- `MultithreadedMapRunner` tests with configurable thread counts, exception propagation from worker maps, reporter/output collector behavior, and non-thread-safe mapper documentation coverage.
- `NLineInputFormat` tests for default one-line splits, custom N lines per split, offsets as keys, empty files, and location hints spanning whole files.
- `TotalOrderPartitioner` tests for partition-file loading, boundary keys, and comparator compatibility.
- Aggregate tests for every built-in aggregator, combiner output round trips, unknown type handling, descriptor configuration, user-defined descriptor reflection, record-count and per-file-count generation, and histogram malformed input.
- DB format tests using an embedded JDBC database for table and query input modes, split boundaries, count query, row read/write through `DBWritable`, output query construction, credential configuration, and cleanup on failure.
- Pipes submitter tests for executable configuration, Java/native component flags, keep-command-file behavior, API submission, CLI parsing, and missing executable errors.
- Metrics tests for factory property loading, context class selection/default null context, updater registration/unregistration, start/stop/close idempotency, record tag/metric type handling, `update()`/`remove()` row semantics, file context output/flush, Ganglia emit stubbing, JVM metrics singleton behavior, and Log4J event counting.
- Metrics util wrapper tests for changed-only publishing, increment/decrement, time-varying interval reset, rate average/min/max, and JMX MBean register/unregister.
- DNS/NetUtils tests for interface lookups with mocks or controlled hosts, socket-address parsing, old/new config migration, static host resolution, wildcard bind address conversion, socket factory selection, and host normalization.
- Rack/topology tests for add/remove/contains, duplicate and invalid leaf handling, normalized paths, rack/leaf counts, distance and same-rack logic, scoped random choice including `~` exclusion scopes, available-node counts, and `pseudoSortByDistance` promotion rules.
- Socket stream tests using channel-backed sockets for read/write timeouts, ByteBuffer reads/writes, synchronized close, `transferToFully` EOF/timeout paths, and direct socket stream incompatibility after non-blocking configuration.
- `SocksSocketFactory` tests should be completed with the next chunk, because this chunk only contains the class beginning.

## Chunk Boundary Notes

The preceding chunk is required for the beginning of `InputSampler.SplitSampler` and earlier `mapred.lib` APIs. The following chunk is required for the rest of `SocksSocketFactory` and subsequent APIs. The final merged source research should preserve that this chunk is a generated API-compatibility view and should not overstate implementation details that are not present in the XML.

### subset-b-007293: lines 37233-43522

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 37233-43522

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.0, not implementation source. It records API compatibility metadata: packages, class and interface names, inheritance, implemented interfaces, constructors, methods, parameters, checked exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadoc contracts.

The range starts inside the tail of `org.apache.hadoop.net.SocksSocketFactory`, covers `org.apache.hadoop.net.StandardSocketFactory`, then spans the full public Record I/O API families under `org.apache.hadoop.record`, `org.apache.hadoop.record.compiler`, `org.apache.hadoop.record.compiler.ant`, `org.apache.hadoop.record.compiler.generated`, and `org.apache.hadoop.record.meta`. It then covers Hadoop 0.19 security identity APIs, several tools, and a large part of `org.apache.hadoop.util` from `Daemon` through the beginning of `StringUtils`. The range ends inside `StringUtils.unEscapeString(...)`, so the complete `StringUtils` API continues in the following chunk.

## Purpose and Major API Surface

`SocksSocketFactory` and `StandardSocketFactory` are Hadoop socket factory adapters. The visible `SocksSocketFactory` tail includes `createSocket(...)` overloads, `equals`, `hashCode`, and `Configurable` accessors `getConf` and `setConf`. `StandardSocketFactory` extends `javax.net.SocketFactory` and exposes the standard no-arg, address/port, host/port, and local-bind socket creation overloads, plus equality/hash methods. Both are documented as specialized socket factories, although the standard implementation appears to represent the non-proxy baseline.

`org.apache.hadoop.record` is the legacy Hadoop Record I/O runtime. `RecordInput` and `RecordOutput` define the serialization contract for primitive values, `String`, `Buffer`, records, vectors, and maps. `BinaryRecordInput` and `BinaryRecordOutput` implement that contract over `DataInput`, `InputStream`, `DataOutput`, and `OutputStream`, with thread-local `get(...)` factories for wrapping a supplied data stream. `CsvRecordInput`/`CsvRecordOutput` and `XmlRecordInput`/`XmlRecordOutput` provide alternate text encodings over streams. `Index` supplies iteration state for vectors and maps through `done()` and `incr()`.

`Buffer` is a mutable byte-sequence value type used by Record I/O. It implements `Comparable` and `Cloneable`, supports zero-length construction, construction over a byte array or byte range, replacement with `set`, copying with `copy`, capacity management through `setCapacity`, truncation/reset, byte appends, `get`, `getCount`, `getCapacity`, comparison, equality, hashing, string conversion with optional character-set name, and cloning. Because one constructor and `set(byte[])` use the supplied byte array as backing storage, callers must treat ownership and mutation carefully.

`Record` is the base generated-record contract. It implements `WritableComparable` and `Cloneable`, requires subclass implementations of tagged `serialize(RecordOutput,String)`, `deserialize(RecordInput,String)`, and `compareTo(Object)`, and bridges to Hadoop `Writable` through `write(DataOutput)` and `readFields(DataInput)`. It also exposes archive-specific serialization/deserialization overloads taking an archive name string. `RecordComparator` extends Hadoop's writable comparator machinery for generated records and has a static `define` method for registering comparators.

`org.apache.hadoop.record.Utils` contains low-level binary and comparison helpers: float/double decoding, variable-length integer and long readers/writers over byte arrays and streams, `getVIntSize`, and byte-array lexical comparison. These APIs are shared by the binary format, generated code, and comparator paths.

The record compiler API models the Record I/O IDL and code generator. `CodeBuffer` wraps a `StringBuffer` with indentation behavior. `Consts` publishes string constants used by generated code such as `RIO_PREFIX`, runtime type-info variables and filters, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`. `JType` is the abstract base for IDL types; primitive and compound subclasses include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, and `JRecord`. `JField<T>` represents a named field and `JFile` represents a complete IDL file with included files and record definitions; `JFile.genCode(language, destDir, options)` generates Java or C++ output and can throw `IOException`.

`org.apache.hadoop.record.compiler.ant.RccTask` is the Ant integration for the record compiler. It extends `org.apache.tools.ant.Task`, accepts `language`, `file`, `failonerror`, `destdir`, and nested `FileSet` values, and invokes the record compiler from `execute()`, throwing `BuildException` on configured failures.

`org.apache.hadoop.record.compiler.generated` exposes JavaCC-generated parser internals. `Rcc` is the parser/driver for record definitions, with constructors over `InputStream`, `Reader`, and `RccTokenManager`; parser productions include `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`; and runtime methods include `main`, `usage`, `driver`, `ReInit`, `getNextToken`, `getToken`, `generateParseException`, and tracing toggles. `RccConstants` defines token IDs for module/record/include, primitive type keywords, container delimiters, punctuation, string and identifier tokens, lexical states, and `tokenImage`. `RccTokenManager`, `SimpleCharStream`, `Token`, `ParseException`, and `TokenMgrError` make tokenization, character stream buffering, source positions, parse diagnostics, and lexical error reporting part of the public API snapshot.

`org.apache.hadoop.record.meta` is runtime schema metadata for Record I/O. `TypeID` represents primitive type identifiers and publishes singleton constants such as `BoolTypeID`, `BufferTypeID`, `ByteTypeID`, `DoubleTypeID`, `FloatTypeID`, `IntTypeID`, `LongTypeID`, and `StringTypeID`. `TypeID.RIOType` defines byte values for primitive, map, struct, and vector types. `VectorTypeID`, `MapTypeID`, and `StructTypeID` describe composite element/key/value/record types. `FieldTypeInfo` pairs a field id with a `TypeID`. `RecordTypeInfo` extends `Record` so type metadata can serialize and deserialize itself; it manages record names, fields, nested struct lookup, tagged serialization/deserialization, and a non-semantic `compareTo` contract. `meta.Utils.skip(...)` skips encoded input according to a supplied `TypeID`.

`org.apache.hadoop.security` in this chunk is the legacy user/group identity layer. `AccessControlException` is an `IOException` subclass for authorization failures. `UnixUserGroupInformation` implements Hadoop `Writable` and represents a Unix-style user plus group array. It can be built from arrays or explicit username/groups, create immutable copies, read and write itself, save to and load from `Configuration` under `UGI_PROPERTY_NAME`, perform login from system properties or configuration, and expose equality, hash, and string forms. `UserGroupInformation` wraps current-user state with static `getCurrentUGI` and `setCurrentUGI`, exposes username and groups, logs in, and reads identity state from a `Configuration`.

`org.apache.hadoop.tools` includes public command entry points. `DistCp` implements `Tool`, stores a `Configuration`, copies paths via `copy`, executes via `run`, exposes `main`, and has a random-id helper plus `DuplicationException.ERROR_CODE`. `HadoopArchives` similarly implements `Tool`, exposes `archive`, `run`, and `main`. `Logalyzer` provides log archiving and analysis methods plus a `main`; its nested `LogComparator` is `Configurable` and compares keys with a configured order, while `LogRegexMapper` implements a MapReduce `Mapper` from input text to text/long-writable counts.

`org.apache.hadoop.util` starts with general-purpose runtime utilities. `Daemon` is a thread wrapper retaining a `Runnable`. `DataChecksum` implements `java.util.zip.Checksum`, creates checksum instances from type/bytes-per-checksum or encoded headers, writes and returns checksum headers, writes/computes/compares checksum values, exposes type/size/header metrics, and updates/resets checksum state. Constants include `HEADER_LEN`, `CHECKSUM_NULL`, `CHECKSUM_CRC32`, and `SIZE_OF_INTEGER`.

`DiskChecker` validates local directories through `mkdirsWithExistsCheck` and `checkDir`, with `DiskErrorException` and `DiskOutOfSpaceException` for failure modes. `GenericOptionsParser` parses Hadoop generic command-line options into a `Configuration`, exposes remaining arguments, parsed Commons CLI `CommandLine`, libjars URLs, and usage printing. `GenericsUtil` provides typed class and list-to-array helpers.

Sorting utilities are centered on `IndexedSortable` and `IndexedSorter`. `IndexedSortable` supplies index-based `compare` and `swap`; `IndexedSorter` sorts half-open ranges, optionally reporting progress. `HeapSort` and `QuickSort` implement `IndexedSorter`, with `QuickSort.getMaxDepth(int)` documenting its worst-case fallback depth. `MergeSort` exposes a lower-level merge sort over integer arrays with a `Comparator<IntWritable>`.

`HostsFileReader` manages include and exclude host files, refreshes from disk, exposes current include/exclude sets, and lets callers update file names. `LineReader` reads line records from an `InputStream` with constructors for default size, explicit buffer size, or `Configuration`; it has overloads that bound bytes and max line length. `NativeCodeLoader` reports and controls native Hadoop library loading through static `isNativeCodeLoaded`, `getLoadNativeLibraries(JobConf)`, and `setLoadNativeLibraries(JobConf, boolean)`. `PlatformName`, `PrintJarMainClass`, `RunJar`, `ProgramDriver`, and `ServletUtil` cover platform/build inspection, jar main-class extraction, jar unpack/launch, reflective program dispatch, and web UI HTML helpers.

`PriorityQueue<T>` is an abstract heap queue with subclass-provided `lessThan(T,T)`, protected `initialize(int)`, and public `put`, `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`. `ProcfsBasedProcessTree` models Linux `/proc` process trees by PID, can test availability and liveness, refresh tree state, destroy a tree, report cumulative virtual memory, extract PID values from files, and format a tree string. `Progress` models hierarchical progress phases with named or unnamed child phases, phase advancement, completion, leaf progress values, aggregate progress reads, status strings, and formatted output. `Progressable` is the callback interface used by long-running operations to signal liveness.

`ReflectionUtils` centralizes configuration injection and reflection-based construction (`setConf`, `newInstance`, typed `getClass`) plus JVM thread diagnostics (`setContentionTracing`, `printThreadInfo`, `logThreadInfo`). `Shell` is an abstract template for launching Unix-like commands with optional execution-interval gating, command-array helpers for groups, permission lookups, ulimit memory, environment and working-directory mutation, process/exit-code access, static `execCommand`, and public command constants. `Shell.ExitCodeException` adds an exit code to `IOException`, and `Shell.ShellCommandExecutor` is the concrete small-output executor with command, working directory, environment, `execute`, `getOutput`, and a quoted `toString`.

The visible `StringUtils` portion contains static helpers for exception stack traces, simple hostnames, human-readable integer and percent formatting, array joining, byte/hex conversion, URI/path array conversion, elapsed-time formatting, formatted timestamp plus duration, comma-separated string collection parsing, escaped splitting, `findNext`, escaping separator characters, and the beginning of unescaping APIs.

## Control Flow and Behavioral Contracts

Record I/O follows a tagged stream contract. Generated `Record` subclasses call `RecordOutput.startRecord`, write fields through primitive/string/buffer/container methods, and call matching end methods; readers perform the inverse through `RecordInput`. Vectors and maps are size/index-driven: `startVector` and `startMap` return an `Index`, callers loop until `done()`, and call `incr()` after each element. Binary, CSV, and XML implementations must preserve the same logical field order and tag structure while differing only in physical encoding.

`Record.write(DataOutput)` and `Record.readFields(DataInput)` bridge generated records into Hadoop's `Writable` ecosystem. Comparator flow uses `RecordComparator` and lower-level `Utils` byte decoding to compare serialized records without necessarily materializing every object. Schema-aware flows use `RecordTypeInfo` and `TypeID` values to persist or skip fields, enabling compatibility filtering and nested struct handling.

Record compiler flow starts with `Rcc.driver` or the Ant `RccTask`. The generated parser tokenizes with `SimpleCharStream` and `RccTokenManager`, parses IDL productions into `JFile`, `JRecord`, `JField`, and `JType` objects, then calls `JFile.genCode` for a selected language and destination directory. Include files are represented as nested `JFile` instances. Parse and lexical errors are surfaced through `ParseException` or `TokenMgrError`, with token position metadata kept in `Token` and stream line/column fields.

Security identity flow is configuration-backed and process-user-oriented. `UnixUserGroupInformation.login(...)` discovers or reads a user/group identity, can persist it with `saveToConf`, and can later reconstruct it with `readFromConf`. `UserGroupInformation` then exposes process-wide current identity through static getters and setters. Because these APIs predate modern Kerberos-heavy UGI behavior, they are mostly simple writable/configuration state rather than credential lifecycle managers.

Tool execution follows Hadoop's `Tool` pattern: `DistCp` and `HadoopArchives` accept a `Configuration`, expose action methods, and route command-line entry through `run(String[])` and `main(String[])`. `Logalyzer` combines filesystem/archive operations with MapReduce mapping and configured comparison.

Utility control flows are mostly template or adapter based. Sort callers adapt data to `IndexedSortable`; sorters mutate only through `compare` and `swap`, with optional `Progressable.progress()` calls. `Shell.run()` asks subclasses for a command array, applies environment and working-directory state, launches a `Process`, delegates stdout parsing, records exit status, and raises `ExitCodeException` on nonzero exits. `ShellCommandExecutor` specializes that by collecting small command output as a string. `ProgramDriver` maps command names to classes and reflectively invokes their `main` methods. `RunJar` unpacks jars, selects a main class from manifest or arguments, and launches it reflectively.

`DataChecksum` flow is header-sensitive: producers select checksum type and bytes-per-checksum, write a header, feed byte ranges through `update`, then write or compare checksum values. Consumers reconstruct from headers and must agree on byte order and checksum size. `LineReader` and `StringUtils` parsing flows are boundary-sensitive: max line length, max bytes, escaping, separator handling, and URI/path conversions are part of serialized configuration and text input compatibility.

## State, Persistence, and Side Effects

The XML file itself is persistent API compatibility data. Runtime state described by this chunk includes socket factory configuration, mutable `Buffer` backing arrays and counts, thread-local binary record input/output wrappers, generated-record field values, parser tokens and lexical stream buffers, record schema metadata, current user/group identity, command tool configuration, checksum accumulator state, host include/exclude sets, priority queue heap arrays, process tree snapshots, progress trees, shell process handles and exit codes, and `StringUtils`-produced persisted strings.

External side effects are significant. Socket factories open network sockets. Record input/output classes read and write binary, CSV, and XML encodings to streams. The record compiler reads IDL files and included files, writes generated Java or C++ sources, and the Ant task can fail a build. `UnixUserGroupInformation` reads system identity information and writes identity strings into `Configuration`. `DistCp`, `HadoopArchives`, and `Logalyzer` operate on filesystems and can run MapReduce jobs. `DiskChecker` creates directories and checks local disk usability. `HostsFileReader` reads host files. `RunJar` extracts jars to disk and executes arbitrary application code. `Shell` executes OS processes with configured environment and working directory. `ServletUtil` writes HTTP response content.

Thread-safety is mixed. `Progress` marks several state methods synchronized, but mutable containers such as `Buffer`, parser streams, `PriorityQueue`, `ShellCommandExecutor`, `HostsFileReader`, and the static current UGI holder are not documented here as generally thread-safe. Thread-local factories in binary record I/O reduce allocation but also mean wrapper state must be rebound correctly to the supplied `DataInput` or `DataOutput`.

## Dependencies and Integration Points

The Record I/O runtime integrates with Hadoop `Writable`, `WritableComparable`, `DataInput`, `DataOutput`, Java streams, `ArrayList`, `TreeMap`, generated records, JDiff-visible runtime type information, and low-level byte comparison utilities. Its compiler side depends on JavaCC-generated parser classes, Ant task APIs, file sets, `IOException`, and language-specific code-generation backends.

Security and tools integrate with `Configuration`, Commons Logging, Hadoop filesystem and MapReduce APIs, `Tool`, MapReduce `Mapper`, `Text`, `LongWritable`, and command-line `main` entry points. These APIs sit at boundaries used by scripts and administrators, so their signatures and exception behavior are compatibility-sensitive.

Utility APIs integrate with Java networking, checksums, process execution, reflection, servlet request/response APIs, jar manifests, local files, `/proc`, Commons CLI, Hadoop `JobConf`, `Path`, `URI`, `IntWritable`, and `Progressable`. `Shell` and `ProcfsBasedProcessTree` are explicitly platform-dependent; the XML exposes `Shell.WINDOWS` and Linux `/proc` assumptions.

## Risks and Compatibility Notes

The first and last classes in this chunk are partial. `SocksSocketFactory` starts before line 37233, and `StringUtils` continues after line 43522. Adjacent chunks are needed to reconstruct those complete class APIs.

This is a public API snapshot. Seemingly small changes to method visibility, checked exceptions, raw versus generic signatures, static/final flags, field constants, or nested generated parser classes can break source or binary compatibility for downstream users that compiled against Hadoop 0.19.0.

Record I/O compatibility is especially brittle. Binary variable-length integer encodings, byte comparison order, `Buffer` equality and comparison, CSV/XML escaping, vector/map index semantics, and `Record.write/readFields` bridging all affect persisted data and generated code. Changing any of these can make old records unreadable or comparators inconsistent.

The record compiler exposes generated parser internals as public API. Even if callers are expected to use `Rcc` or `RccTask`, classes such as `Token`, `SimpleCharStream`, `RccTokenManager`, and token constants are visible; regenerating with a different JavaCC version can alter public fields or diagnostics.

`UnixUserGroupInformation` and `UserGroupInformation` persist identity in configuration and expose process-wide current-user state. Tests should treat this as global mutable state and isolate configuration changes, especially when run in parallel.

`Shell`, `RunJar`, `ProgramDriver`, `DistCp`, `HadoopArchives`, and `Logalyzer` invoke external commands, reflective code, filesystem writes, or MapReduce jobs. Error propagation, environment handling, working-directory behavior, and platform differences are likely failure points. `ShellCommandExecutor` is explicitly suitable for small command output; large output risks memory pressure or deadlock if process streams are mishandled.

`DataChecksum`, `LineReader`, sorting, and `StringUtils` are cross-cutting utility APIs. Off-by-one range changes in sorters, line-length and byte-limit changes in `LineReader`, checksum header/value byte-order changes, or escaping/unescaping changes in `StringUtils` can break large areas of Hadoop common.

## Test Signals

JDiff-level validation should assert that the XML remains well-formed across all package transitions in this range and that each public/protected API item retains its class/interface name, inheritance, implemented interfaces, constructor and method signatures, declared exceptions, field constants, visibility, flags, and deprecation markers.

Record I/O tests should round-trip generated records through binary, CSV, and XML archives; cover all primitive types, strings, buffers, vectors, maps, nested records, empty containers, and null/empty byte sequences where supported; validate `Index` iteration; verify `Buffer` capacity, append, truncate, clone, equality, comparison, and backing-array ownership; and check `Record.write/readFields` compatibility with Hadoop `Writable`.

Compiler tests should parse valid and invalid record IDL files, includes, modules, primitive and composite fields, and nested records; verify `JFile.genCode` output for Java and C++; exercise `RccTask` with direct file and fileset inputs, destination directories, language selection, and `failonerror`; and assert useful `ParseException`/`TokenMgrError` messages with line and column metadata.

Metadata tests should serialize and deserialize `RecordTypeInfo`, compare primitive and composite `TypeID` values, validate hash/equality contracts for field/map/vector types, check nested struct lookup, and verify `meta.Utils.skip` consumes exactly the bytes for each supported type without corrupting subsequent reads.

Security tests should cover `UnixUserGroupInformation` constructors, immutable copies, read/write round trips, `saveToConf` and `readFromConf`, login paths, equality/hash/toString, and `UserGroupInformation` current-user global state isolation.

Tool tests should cover `DistCp.run/copy`, duplicate detection and `DuplicationException.ERROR_CODE`, `HadoopArchives.archive/run`, `Logalyzer` archive/analyze paths, configured log comparison, mapper regex matching and count output, configuration injection through `Tool`, and command-line `main` error handling.

Utility tests should cover checksum header encode/decode, null and CRC32 modes, checksum compare failures, `DiskChecker` missing/unwritable/out-of-space paths, `GenericOptionsParser` remaining arguments and libjars, typed array conversion in `GenericsUtil`, sorting of empty/single/duplicate/reverse/subrange inputs with progress callbacks, host file refresh behavior, line reading with max lengths and byte limits, native-loader flags, jar extraction and reflective launch, priority queue capacity/order behavior, `/proc` process-tree availability and pid-file parsing, progress tree aggregation, reflection/config injection, shell environment/working-directory/exit-code behavior, and the visible `StringUtils` formatting, hex, URI/path, escaped split, escape, and unescape contracts.

### subset-b-007294: lines 43523-43972

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 43523-43972

## Chunk Scope

This chunk is the closing portion of the Hadoop 0.19.0 JDiff API snapshot. It starts at the tail of `org.apache.hadoop.util.StringUtils`, covers `StringUtils.TraditionalBinaryPrefix`, `Tool`, `ToolRunner`, `UTF8ByteArrayUtils`, `VersionInfo`, and `XMLUtils`, then closes the package and API document.

Because this source is generated API XML rather than Java implementation source, the control-flow, state, and persistence notes are inferred from exposed signatures, modifiers, documentation, checked exceptions, and adjacent class context.

## Purpose

The covered API surface documents small but widely used utility contracts in Hadoop Common 0.19.0:

- string formatting, escaping, hostname, startup/shutdown logging, and HTML escaping helpers;
- binary-size suffix parsing for human-facing configuration values;
- the standard `Tool`/`ToolRunner` command-line integration contract used by Hadoop applications;
- byte-level UTF-8 search helpers used where decoding full strings is unnecessary;
- build/version metadata reporting;
- XSLT transformation support for XML utilities.

In a compatibility research lane, this chunk is important because these utilities are public, static-heavy APIs used by many Hadoop clients and command-line programs. Small signature or behavior changes can break external tools even when no filesystem or MapReduce implementation code is touched.

## Important APIs and Types

### `org.apache.hadoop.util.StringUtils` tail

The chunk begins in the last `unEscapeString(String, char, char[])` overload and then lists the final methods and fields of `StringUtils`.

Important visible members:

- `unEscapeString(String, char, char[])` unescapes any character from a supplied escape set using a caller-provided escape character.
- `getHostname()` returns a hostname without throwing an exception, making it a defensive utility for diagnostics and logs.
- `startupShutdownMessage(Class<?>, String[], Log)` emits startup and shutdown log messages for daemon/server-style classes using Apache Commons Logging.
- `escapeHTML(String)` escapes HTML special characters for presentation in generated pages or logs.
- Public constants `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR` define the default comma separator and escape character used by earlier `split`, `escapeString`, and `unEscapeString` overloads.

Adjacent source context shows the same class also exposes exception stringification, hostname shortening, human-readable integer formatting, percent formatting, hex conversion, URI/path conversion, time formatting, comma splitting, escaped separator scanning, and escape/unescape overloads. The visible tail should be merged with earlier chunk coverage for a complete `StringUtils` summary.

### `StringUtils.TraditionalBinaryPrefix`

`TraditionalBinaryPrefix` is a public static enum nested in `StringUtils`. It models traditional binary prefixes from kilo through exa, with case-insensitive symbols and public final fields:

- `value`, a `long` multiplier;
- `symbol`, a `char` suffix.

Important methods:

- `values()` and `valueOf(String)` are standard enum methods.
- `valueOf(char)` maps a suffix symbol to the corresponding prefix enum.
- `string2long(String)` trims an input string and parses it as a `long`, optionally applying a binary suffix. The docs give examples such as `-1230k` becoming `-1230 * 1024` and `891g` becoming `891 * 1024^3`.

This enum is an integration point for configuration values and command-line parameters that accept human-readable sizes.

### `org.apache.hadoop.util.Tool`

`Tool` is a public interface extending `org.apache.hadoop.conf.Configurable`. It defines:

- `run(String[] args) throws Exception`, returning an integer process-style exit code.

The documentation frames `Tool` as the standard interface for Hadoop MapReduce tools and applications. Implementations are expected to delegate generic Hadoop command-line option handling to `ToolRunner`, then process only application-specific arguments. The example in the XML shows a `Configured implements Tool` class reading the processed `Configuration`, constructing a `JobConf`, setting MapReduce job options, and using `JobClient.runJob`.

### `org.apache.hadoop.util.ToolRunner`

`ToolRunner` is a public utility class with a default constructor and static helpers:

- `run(Configuration, Tool, String[]) throws Exception` parses generic Hadoop arguments, creates or updates a `Configuration`, sets it onto the `Tool`, and then invokes `Tool.run(String[])`.
- `run(Tool, String[]) throws Exception` is equivalent to `run(tool.getConf(), tool, args)`.
- `printGenericCommandUsage(PrintStream)` prints generic Hadoop command-line argument usage.

The class is explicitly documented as working with `GenericOptionsParser`, preserving application-specific arguments while consuming generic Hadoop options that modify the tool configuration.

### `org.apache.hadoop.util.UTF8ByteArrayUtils`

`UTF8ByteArrayUtils` exposes byte-array search utilities over UTF-8 encoded data:

- `findByte(byte[] utf, int start, int end, byte b)` returns the first occurrence of a byte in the half-open byte range, or `-1`.
- `findBytes(byte[] utf, int start, int end, byte[] b)` returns the first occurrence of a byte sequence in the range, or `-1`.
- `findNthByte(byte[] utf, int start, int length, byte b, int n)` finds the nth occurrence within an explicit byte segment.
- `findNthByte(byte[] utf, byte b, int n)` searches the whole byte array.

These methods are useful for delimiter scanning in already-encoded text without allocating Java `String` objects. The API operates on raw bytes, so callers must choose delimiters that are meaningful at the UTF-8 byte level.

### `org.apache.hadoop.util.VersionInfo`

`VersionInfo` is a public utility class for Hadoop build metadata:

- `getVersion()` returns the Hadoop version string, for example a development version.
- `getRevision()` returns the Subversion revision number for the root directory.
- `getDate()` returns the compilation date.
- `getUser()` returns the user who compiled Hadoop.
- `getUrl()` returns the Subversion URL for the root Hadoop directory.
- `getBuildVersion()` combines version, revision, user, and date.
- `main(String[])` provides command-line reporting.

The class documentation says it finds package information and `HadoopVersionAnnotation` information, so the implementation likely bridges Java package metadata and Hadoop's generated build annotation.

### `org.apache.hadoop.util.XMLUtils`

`XMLUtils` exposes:

- `transform(InputStream styleSheet, InputStream xml, Writer out)`, throwing `TransformerConfigurationException` and `TransformerException`.

The method transforms an input XML stream with a stylesheet and writes the result to a `Writer`. This is a small wrapper around Java XML transform APIs, useful for support tooling and generated report production.

## Control Flow and Behavioral Contracts

`StringUtils` behavior is mostly direct static utility flow: callers provide strings or primitive values, and methods return formatted, escaped, parsed, or diagnostic strings. The escaping family shares the public default comma and escape constants while also allowing explicit escape characters and target character sets. `startupShutdownMessage` is the only visible method with external side effects, writing lifecycle messages through a supplied `Log`.

`TraditionalBinaryPrefix.string2long` follows a parse flow: trim input, detect whether the final character is a binary-prefix symbol, parse the numeric portion, multiply by the prefix value, and return a `long`. Invalid suffixes, malformed numbers, and overflow behavior are not visible in the XML but are natural test targets.

`ToolRunner.run` defines the standard Hadoop command flow: parse generic options with `GenericOptionsParser`, mutate or create a `Configuration`, install that configuration into the `Tool`, and call `Tool.run` with remaining application arguments. The integer returned by `Tool.run` is the caller-visible exit code. Exceptions are not swallowed by the signatures.

`UTF8ByteArrayUtils` methods perform linear byte scanning over caller-supplied arrays and return integer offsets or `-1`. The `start`/`end` and `start`/`length` variants imply careful boundary handling; the whole-array overload is a convenience wrapper.

`VersionInfo` is read-only metadata flow. Static getters retrieve build fields, `getBuildVersion` formats multiple fields together, and `main` emits them for CLI inspection.

`XMLUtils.transform` consumes two input streams and a writer, constructs/configures a transformer from the stylesheet, applies it to the XML input, writes to the supplied output, and reports configuration or transformation failures through checked JAXP exceptions.

## State and Persistence Behavior

Most APIs in this chunk are stateless static utilities. Persistent or mutable state is limited to:

- `StringUtils` public constants, which define stable delimiter/escape defaults but do not mutate.
- `ToolRunner.run`, which mutates the supplied `Tool` by calling the `Configurable` configuration setter inherited through `Tool`.
- `Configuration` mutations caused by parsed generic Hadoop options; those settings persist for the lifetime of the configuration object used by the tool.
- `VersionInfo`, which reads build metadata embedded in the Hadoop package or generated version annotation. That metadata is fixed at build time and persists in the compiled artifact rather than in runtime storage.
- `XMLUtils.transform`, which writes transformed XML to the caller-provided `Writer`; it does not expose a persistent object model of its own.

No filesystem state, background threads, locks, or durable Hadoop data files are visible in this chunk.

## Dependencies and Integration Points

Key dependencies visible from signatures and documentation:

- Apache Commons Logging `org.apache.commons.logging.Log` for startup/shutdown diagnostics.
- Hadoop configuration APIs: `org.apache.hadoop.conf.Configurable` and `Configuration`.
- Hadoop command-line parsing via `GenericOptionsParser`.
- MapReduce-era integration referenced by docs: `JobConf`, `Path`, `JobClient`, mapper/reducer classes, and `ToolRunner.run` from application `main` methods.
- Java IO: `PrintStream`, `InputStream`, and `Writer`.
- Java XML transform APIs: `javax.xml.transform.TransformerConfigurationException` and `TransformerException`.
- Java networking/path and text APIs from adjacent `StringUtils` methods: `URI`, `Path`, `DateFormat`, arrays, collections, and string builders.

The primary integration point is the `Tool`/`ToolRunner` convention: Hadoop CLIs implement `Tool`, accept generic options such as configuration overrides and classpath additions through `GenericOptionsParser`, then execute domain-specific logic with a prepared `Configuration`. The utility classes support surrounding diagnostics, configuration parsing, HTML/UI output, and generated XML/report tooling.

## Risks and Edge Cases

- This is API XML, so actual exception types for malformed strings, invalid byte ranges, overflow, null inputs, and failed hostname lookup are not visible unless declared.
- The chunk starts inside `StringUtils`; final merged research must reconcile this tail with the earlier methods in the same class.
- `StringUtils` escaping behavior can be subtle when the escape character itself appears in the input, when delimiters are consecutive, or when a string ends with a dangling escape.
- `TraditionalBinaryPrefix.string2long` uses binary multipliers and a `long` result; overflow and signed inputs need explicit tests.
- `valueOf(char)` is documented as case-insensitive through the enum docs, so both upper- and lower-case suffixes must remain compatible.
- `ToolRunner.run(Tool, String[])` assumes `tool.getConf()` is meaningful. Tools with null configurations should be checked against the documented equivalence to the three-argument overload.
- `ToolRunner` mutates a tool's configuration before invoking `run`, so reusing a `Tool` instance across invocations can carry state unless callers reset it.
- `UTF8ByteArrayUtils` searches raw bytes, not Unicode code points; this is safe for ASCII delimiters but risky for callers expecting character-aware search.
- `findBytes` and nth-byte search need clear behavior for empty target sequences, `n <= 0`, negative offsets, and ranges past array length; the XML does not document those cases.
- `VersionInfo` references Subversion-specific metadata, reflecting Hadoop 0.19.0's build system. Downstream builds without those annotations may return placeholders or null-like strings depending on implementation.
- `XMLUtils.transform` delegates to JAXP transformer behavior; untrusted XML or stylesheets can raise security concerns such as external entity or stylesheet access unless implementation configures secure processing.

## Test Signals

Useful tests inferred from this API slice include:

- `StringUtils` tests for comma escaping/unescaping, explicit escape character arrays, trailing escapes, escaped escape characters, consecutive separators, `getHostname` fallback behavior, startup/shutdown log contents, and `escapeHTML` coverage for special characters.
- `TraditionalBinaryPrefix` tests for each prefix symbol in upper and lower case, unsigned and signed numbers, whitespace trimming, missing suffix, invalid suffix, malformed number, and overflow.
- `ToolRunner` tests that generic Hadoop arguments are consumed, application-specific arguments are preserved, the `Tool` receives the modified `Configuration`, return codes propagate, exceptions propagate, and the two `run` overloads behave equivalently.
- `printGenericCommandUsage` tests that usage output is written to the supplied `PrintStream` and includes the expected generic-option categories.
- `UTF8ByteArrayUtils` tests for byte and byte-sequence matches at beginning/middle/end, no-match return `-1`, bounded range handling, nth occurrence semantics, whole-array overload equivalence, and multi-byte UTF-8 payloads with ASCII delimiters.
- `VersionInfo` tests that each getter returns the expected build metadata in packaged artifacts and that `getBuildVersion` includes version, revision, user, and date.
- `XMLUtils.transform` tests for a successful stylesheet transform, malformed stylesheet failure, malformed XML failure, checked exception propagation, writer output content, and stream handling expectations.

## Chunk Boundary Notes

The preceding chunk is required for the start and middle of `StringUtils`, including the method declaration that this chunk begins inside. This chunk reaches the end of `hadoop_0.19.0.xml`, closing `org.apache.hadoop.util`, `package`, and `api`, so there is no following chunk for this source file.
