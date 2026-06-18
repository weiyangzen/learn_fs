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
