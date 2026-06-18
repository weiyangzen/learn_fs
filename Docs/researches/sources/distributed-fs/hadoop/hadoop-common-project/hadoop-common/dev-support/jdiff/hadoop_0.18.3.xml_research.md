# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007280`: lines 1-6117, `Docs/researches/chunks/subset-b-007280_research.md`
- `subset-b-007281`: lines 6118-12396, `Docs/researches/chunks/subset-b-007281_research.md`
- `subset-b-007282`: lines 12397-18635, `Docs/researches/chunks/subset-b-007282_research.md`
- `subset-b-007283`: lines 18636-24770, `Docs/researches/chunks/subset-b-007283_research.md`
- `subset-b-007284`: lines 24771-30886, `Docs/researches/chunks/subset-b-007284_research.md`
- `subset-b-007285`: lines 30887-37164, `Docs/researches/chunks/subset-b-007285_research.md`
- `subset-b-007286`: lines 37165-38826, `Docs/researches/chunks/subset-b-007286_research.md`

## Chunk Research

### subset-b-007280: lines 1-6117

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml lines 1-6117

## Chunk Scope

This chunk is the opening segment of the generated JDiff API descriptor for `hadoop 0.18.3`, produced by the JDiff Javadoc doclet on 2009-01-22. It is not executable source; it is an XML snapshot of public API declarations, inheritance, signatures, deprecation metadata, checked exceptions, fields, and Javadoc CDATA. The chunk begins with the `<api>` metadata and covers complete declarations for `org.apache.hadoop`, `org.apache.hadoop.conf`, `org.apache.hadoop.filecache`, most of `org.apache.hadoop.fs`, and the beginning of `org.apache.hadoop.fs.ftp.FTPFileSystem`. `FTPFileSystem` continues beyond line 6117 and should be reconciled with the next chunk.

## Purpose

The file exists to support API compatibility comparison for Hadoop 0.18.3. JDiff consumers compare this XML against another version snapshot to detect added, removed, changed, or deprecated API surface. In this chunk the dominant purpose is to define Hadoop's foundational configuration and filesystem contracts: configuration loading, distributed cache localization metadata, file status/block metadata, abstract filesystem operations, checksum-aware local filesystem wrappers, local disk allocation, path/stream abstractions, shell/trash utilities, Hadoop archive access, and early FTP filesystem declarations.

## Important APIs, Types, and Functions

- `org.apache.hadoop.HadoopVersionAnnotation` is a public annotation contract used as a package attribute to record the Hadoop version compiled into artifacts.
- `org.apache.hadoop.conf.Configurable` declares `setConf(Configuration)` and `getConf()`, establishing the common configuration injection interface.
- `org.apache.hadoop.conf.Configuration` is a central iterable property container. It loads resources by classpath name, `URL`, or `Path`; supports default and final properties; performs variable expansion from configuration and system properties; provides typed getters/setters for `String`, `int`, `long`, `float`, `boolean`, string arrays, class values, and integer ranges; resolves local paths/files/resources; writes non-default properties; manages a class loader; and has a debug `main`.
- `Configuration.IntegerRanges` parses positive integer ranges such as `2-3,5,7-` and exposes `isIncluded(int)`.
- `Configured` stores a `Configuration` for classes that implement `Configurable`.
- `org.apache.hadoop.filecache.DistributedCache` is a static utility for MapReduce distributed cache setup and localization. It exposes APIs to localize files/archives, release caches, read source timestamps, create symlinks, configure cache file/archive URIs, record localized paths and timestamps, add cache entries to task classpaths, validate URI fragments, and purge the whole cache.
- `BlockLocation`, `ContentSummary`, and `FileStatus` are public metadata value types implementing `Writable` where relevant. They serialize block host/name/offset/length metadata, directory/file/quota summaries, and file status attributes including length, directory flag, replication, block size, modification time, permissions, owner, group, and path.
- `FileSystem` is the core abstract filesystem API. It defines factory/accessor methods (`get`, `getDefaultUri`, `setDefaultUri`, `getNamed`, `getLocal`, `closeAll`), URI initialization, path qualification, block location lookup, open/create/append variants, replication, rename/delete/delete-on-exit, existence/type checks, status/list/glob APIs, working directory/home directory APIs, mkdirs, local/remote copy helpers, output staging, close, usage/default block/default replication, permissions/owner mutation, and shared statistics.
- `FileSystem.Statistics` tracks bytes read and written.
- `FileUtil` collects filesystem/local-file utility methods: `FileStatus` to `Path` conversion, recursive delete, copy/copyMerge across filesystems and local files, shell path conversion, local directory disk usage, unzip/untar, symlink/chmod shell helpers, local temp file creation, and file replacement. Nested `FileUtil.HardLink` supports hardlink creation and link count queries for Unix, Cygwin, and Windows XP.
- `FilterFileSystem` wraps another `FileSystem` in protected field `fs` and forwards the filesystem API, providing a decorator base for checksum, archive, and other transforming filesystems.
- `FSDataInputStream` wraps `FSInputStream` with `DataInputStream` behavior and implements `Seekable` plus `PositionedReadable`. `FSDataOutputStream` wraps output with `DataOutputStream`, tracks position, optionally updates filesystem statistics, exposes the wrapped stream, and implements `Syncable`.
- `FSInputChecker` and `FSOutputSummer` are abstract checksum stream bases. `FSInputChecker` requires chunk reads and chunk-position mapping, verifies checksums while reading, supports retries, seek/skip/available, and disables mark/reset. `FSOutputSummer` buffers chunks, computes checksums, and delegates chunk writes to subclasses.
- `FSInputStream`, `Seekable`, `PositionedReadable`, and `Syncable` define the low-level stream contracts for seek, current position, alternate source seeking, positional reads that do not move the current offset, full reads, and durable synchronization.
- `DF` and `DU` extend `org.apache.hadoop.util.Shell` to wrap Unix `df` and `du` behavior. `DU` has a refresh thread lifecycle (`start`, `shutdown`) and manual accounting adjustments (`incDfsUsed`, `decDfsUsed`).
- `FsShell` implements `Tool` for command-line filesystem access, initializing a `FileSystem`, exposing byte formatting helpers, trash directory access, `run`, `close`, and `main`.
- `FsUrlStreamHandlerFactory` implements `URLStreamHandlerFactory` and creates handlers only for schemes known to Hadoop `FileSystem`.
- `HarFileSystem` implements Hadoop archive access over a wrapped filesystem. It maps `har://...` URIs to archive contents, reads `_masterindex` and `_index` metadata, resolves part file offsets, fakes EOF for archived member reads, and explicitly leaves most write/mutation operations unimplemented.
- `InMemoryFileSystem` is a checksum filesystem for `ramfs://` where users must reserve space, including checksum space, before creating files because file size is not passed to normal filesystem create APIs.
- `LocalDirAllocator` manages round-robin local disk selection for configured directory contexts such as `mapred.local.dir`, with write allocation by known/unknown size, read lookup across configured directories, temporary-file creation, context validation, and existence checks.
- `LocalFileSystem` extends `ChecksumFileSystem` around the raw local filesystem and adds local path conversion plus checksum-failure quarantine behavior.
- `Path` is the URI-like filesystem path abstraction. It supports parent/child constructors, string/component constructors, URI conversion, owner filesystem lookup, absolute/name/parent/suffix/depth operations, qualification, comparison/equality/hash, and constants for separator/current directory.
- `PathFilter` is the single-method predicate used by list/glob APIs.
- `RawLocalFileSystem` implements the unchecksummed local filesystem, converting Hadoop `Path` to `java.io.File`, exposing local URI/name, open/append/create/rename/delete/list/mkdirs, working directory, local output staging, status, owner/permission mutation through `chown`/`chmod`, and deprecated lock/release methods.
- `ShellCommand` is a deprecated alias-style abstract shell base; callers are directed to `org.apache.hadoop.util.Shell`.
- `Trash` moves files into per-user `.Trash/current`, supports checkpoint/expunge, exposes a superuser emptier `Runnable`, and includes a CLI `main`.
- `FTPException` wraps a `Throwable` or message into a runtime exception. `FTPFileSystem` starts in this chunk with initialization, open, create, append, delete, URI, list/status, mkdir, rename, home/working directory, and the beginning of `setWorkingDirectory`.

## Control Flow and Behavioral Contracts

The XML itself has no runtime control flow, but the documented API contracts reveal the intended flows:

- Configuration flow loads default resources first, then site and application resources in order; later resources override earlier values except keys marked final; property reads expand `${...}` against configuration keys and then JVM system properties.
- Distributed cache flow starts with applications recording cache files/archives and optional classpath additions in `JobConf`/`Configuration`; task localization then validates timestamps, copies or reuses local files, unpacks archives, optionally creates symlinks from URI fragments, and exposes localized paths back through configuration getters. `releaseCache` decrements cache use and `purgeCache` is explicitly for server reinitialization because it removes users' cached files.
- `FileSystem` flow is a template contract: callers acquire an implementation by URI/default configuration, initialize it with `(URI, Configuration)`, qualify and check paths, then use abstract operations (`open`, full-parameter `create`, `append`, `rename`, recursive `delete`, `listStatus`, `mkdirs`, `getFileStatus`, working directory methods) implemented by concrete subclasses. Convenience overloads delegate to abstract forms with defaults for buffer size, replication, block size, permissions, overwrite, and progress callbacks.
- Copy and local-output flows bridge local files and arbitrary filesystems. `startLocalOutput` returns either the final destination for local filesystems or a temporary local path for remote filesystems; `completeLocalOutput` copies temporary content to the filesystem target when needed.
- Checksum flows wrap a raw filesystem with paired checksum files. `ChecksumFileSystem` maps data files to checksum paths, filters checksum files out of listings, calculates checksum-file length from data size and bytes-per-sum, opens streams that verify checksums, creates streams that write checksums, renames/deletes data plus checksum files, and can report checksum failures. `LocalFileSystem.reportChecksumFailure` moves corrupted data/checksum files to a bad-file area on the same device.
- Stream flow separates random-access and positional-read concerns. `FSInputStream`/`Seekable` moves the stream offset; `PositionedReadable` reads at an absolute position without changing it, documented as thread-safe. `FSDataInputStream` delegates these capabilities through a `DataInputStream`; `FSInputChecker` adds checksum verification and retry behavior on top of chunk reads.
- `FileSystem.globStatus` applies shell-like pattern matching (`?`, `*`, character sets/ranges, negation, escaping, brace sets/nesting), sorts results, filters checksum files, returns `null` for a non-glob nonexistent path, and returns an empty array when a glob has no matches.
- `HarFileSystem` flow initializes one filesystem instance per archive URI, reads archive indexes, maps logical paths to part files and offsets, and returns read streams over bounded member regions. Mutation APIs are declared but documented as not implemented.
- `LocalDirAllocator` flow keeps one allocator per context per JVM, remembers the last selected directory, tries configured directories in round-robin order, checks free space and writability, and scans all configured directories for reads.
- `Trash` flow moves an original path under `.Trash/current` while preserving the original path, then checkpoint/expunge rotates and removes old checkpoints without requiring full trash enumeration, filesystem date support, or synchronized clocks.
- `FTPFileSystem` flow is only partially visible. The visible `create` contract warns that the returned stream must be closed before other APIs are used or later calls can block; append is documented as unsupported.

## State and Persistence Behavior

- The JDiff file persists API state as XML: package/class/interface elements, method/constructor/field signatures, visibility, abstract/static/final/synchronized/native flags, deprecation strings, checked exceptions, and Javadoc text.
- Runtime state implied by APIs includes mutable `Configuration` resources and property overrides; non-default configuration serialization through `Configuration.write(OutputStream)`; `DistributedCache` entries, timestamps, localized paths, classpath settings, symlink flags, and backing cache files stored through `Configuration` and local cache directories; `FileSystem` singleton/cache behavior implied by static `get`, `closeAll`, and shared statistics; delete-on-exit paths retained until filesystem close/JVM shutdown; and per-filesystem working directories.
- Filesystem metadata types persist through Hadoop `Writable` serialization (`BlockLocation`, `ContentSummary`, `FileStatus`).
- `ChecksumFileSystem` persists sidecar checksum files for each raw data file; checksum file naming and filtering are part of the public contract.
- `HarFileSystem` persists archive structure in `_masterindex`, `_index`, and `part-*` files. It notes that member file permissions are not persisted when creating a Hadoop archive; reported permissions come from archive index files.
- `InMemoryFileSystem` keeps file and checksum contents in memory and requires up-front reservation to avoid exceeding its configured capacity.
- `LocalDirAllocator` maintains per-JVM allocator instances and last-allocation cursor per configured context, but explicitly does not guard against disks becoming read-only or full while writes are in progress.
- `Trash` persists deleted content under user home `.Trash/current` and checkpoint directories; only one checkpoint is kept at a time by the emptier flow.
- `DU` can maintain periodically refreshed disk-usage state in a background thread, plus manual increments/decrements to reflect expected DFS use.

## Dependencies and Integration Points

- The JDiff generation command references Hadoop branch `0.18` classes from `src/core`, `src/mapred`, and `src/tools`, plus dependencies including commons-cli, commons-codec, commons-httpclient, commons-logging, commons-net, Jetty/JSP libraries, jets3t, KFS, log4j, ORO, servlet API, SLF4J, xmlenc, Ant, Xerces, and JDK 1.5 tools.
- Public APIs depend heavily on Java `java.io`, `java.net.URI/URL/URLStreamHandlerFactory`, collections/iterators, `java.util.zip.Checksum`, and shell process behavior.
- Hadoop internal integration points include `org.apache.hadoop.conf.Configuration`, `org.apache.hadoop.fs.Path`, `FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FsPermission`, `Progressable`, `Tool`, `Shell`, `Writable`, and MapReduce `JobConf`, `Mapper`, `Reducer`, `JobClient` references in distributed-cache docs.
- Concrete filesystem integrations visible here include local raw files, checksum-local filesystem, in-memory `ramfs://`, Hadoop Archive `har://`, and the beginning of FTP-backed filesystem support.
- Command-line/tooling integrations include `FsShell`, `DF`, `DU`, `Trash.main`, `Configuration.main`, `FileUtil.chmod`, `FileUtil.symLink`, local `chown`/`chmod`, and shell-specific path conversion.
- URL integration is through `FsUrlStreamHandlerFactory`, which lets standard Java URL handling defer to Hadoop filesystem scheme resolution.

## Risks and Edge Cases

- Because this is generated API XML, it may not fully describe implementation details such as synchronization internals, exception ordering, cache maps, or actual algorithms. Research conclusions about behavior are limited to signatures and embedded Javadoc.
- The chunk ends inside `FTPFileSystem`; any whole-class conclusions for FTP must be finalized using later chunks.
- Many APIs retain deprecated compatibility surface: `FileSystem.getName`, one-argument `delete`, `getReplication`, `isDirectory`, `getLength`, `getBlockSize`, `RawLocalFileSystem.getName`, `RawLocalFileSystem.lock/release`, and `ShellCommand`. Compatibility tooling should verify deprecation text and replacement methods.
- `DistributedCache.purgeCache` is high-risk because docs state it clears all backing cached files and users lose files; timestamp-based cache validation is sensitive to files changing while jobs execute.
- `FileSystem.deleteOnExit` depends on filesystem close/JVM shutdown and can recursively delete marked paths; missing close or path existence assumptions can change behavior.
- `ChecksumFileSystem` has paired data/checksum file invariants. Rename, delete, list filtering, copy-to-local with or without CRC files, and checksum-failure reporting must preserve sidecar consistency.
- `FSInputChecker.skip` and `seek` docs allow moving past EOF without immediate error, which can surprise callers expecting strict bounds. `FSInputStream.seek` docs, by contrast, say it cannot seek past EOF, so implementations and wrappers need tests for contract consistency.
- `PositionedReadable` promises thread-safe positional reads that do not change current offset; wrapper or checksum implementations can break concurrent readers if they share mutable seek state incorrectly.
- `FileSystem.globStatus` has subtle null-versus-empty-array behavior based on whether the pattern contains a glob.
- `FileStatus` equality and hash code are path-based, not full-metadata based, so metadata changes may not affect collection identity.
- `HarFileSystem` is mostly read-only. It reports many mutation methods as not implemented and does not persist original permissions for archive members.
- `LocalDirAllocator` explicitly ignores disks becoming full/read-only during a write, so allocation success is not a guarantee that the write will finish.
- `RawLocalFileSystem` owner and permission mutations shell out to `chown` and `chmod`, so behavior depends on OS commands, permissions, and platform support.
- `FTPFileSystem.create` can block later API calls until the returned stream is closed; append is unsupported.

## Test Signals

- API compatibility tests should parse this XML and assert stable package/class/interface/method/field signatures, visibility flags, inheritance, implemented interfaces, exceptions, and deprecation strings.
- Configuration tests should cover resource precedence, final-parameter protection, variable expansion from configuration and system properties, typed parse fallback behavior, string array/collection handling, class loading, and `write(OutputStream)` output.
- Distributed cache tests should cover URI fragment validation, duplicate fragment rejection, timestamp validation, archive unpacking for zip/jar/tar/tgz/tar.gz, symlink creation, classpath additions, localized path/timestamp round trips through configuration, cache release, and purge behavior.
- Filesystem contract tests should run against local, checksum-local, in-memory, HAR, and FTP implementations where possible: factory resolution by URI, path qualification/checking, open/create/append support, delete recursive semantics, list/status/glob behavior, working-directory resolution, local-output staging, permission/owner calls, and `closeAll`.
- Serialization tests should round-trip `BlockLocation`, `ContentSummary`, and `FileStatus` via `Writable`, including quota output formatting and path-based equality/ordering.
- Checksum tests should verify checksum file naming/length, creation of paired files, filtering checksum files from listings/globs, checksum failure exceptions/retry paths, local bad-file quarantine, copy-to-local with and without CRC files, and rename/delete consistency.
- Stream tests should cover `Seekable`, `PositionedReadable`, `FSDataInputStream`, `FSInputChecker`, and `FSOutputSummer`: seek/getPos, readFully, positional reads preserving current position, concurrent positioned reads, EOF behavior after seek/skip past end, sync delegation, statistics updates, and chunk checksum generation/verification.
- Utility tests should cover recursive delete partial-failure behavior, copy and copyMerge across filesystem/local boundaries, unzip/untar output, shell path conversion on Windows/Cygwin/Unix, symlink/chmod/hardlink platform behavior, and local temp file cleanup.
- HAR tests should verify URI parsing, archive-home resolution, index/master-index lookup, hash mapping, block locations over underlying part files, member status/list/open behavior, fake EOF on member streams, and unsupported mutation operations.
- Local disk allocation tests should cover round-robin cursor behavior, known-size and unknown-size writes, insufficient-space fallback, read lookup across configured dirs, context singleton validation, temp-file delete-on-exit, and the documented write-time disk-full caveat.
- Trash tests should verify disabled/already-in-trash false returns, original-path preservation under `.Trash/current`, checkpoint creation, expunge deletion, and superuser emptier behavior.

## Cross-Chunk Notes

`FTPFileSystem` is incomplete in this chunk. The merge lane should combine this report with the next chunk before making whole-file conclusions about FTP path resolution, authentication, stream implementation, connection lifecycle, and remaining methods after `setWorkingDirectory`.

### subset-b-007281: lines 6118-12396

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml lines 6118-12396

## Scope

This chunk is part of a generated JDiff API snapshot for Hadoop 0.18.3. It is compatibility metadata, not implementation code. The range starts at the tail of `org.apache.hadoop.fs.ftp.FTPFileSystem`, includes `FTPInputStream`, then covers KFS, filesystem permissions, legacy S3 and native S3 filesystem APIs, shell command helpers, and a large part of `org.apache.hadoop.io`. It ends inside the public API entry for `org.apache.hadoop.io.Text`, after constructors and early byte/UTF-8 mutation methods but before the rest of `Text`.

The XML records public and protected API shape: packages, classes, interfaces, inheritance, implemented interfaces, constructors, methods, fields, parameter types, declared exceptions, visibility, static/final/abstract/native/synchronized flags, deprecation markers, and embedded Javadocs. Control-flow and state observations below are inferred from those signatures and contracts.

## Purpose and major API surface

The opening FTP section finishes `FTPFileSystem` constants and documentation, then defines `FTPInputStream`. `FTPInputStream` extends `FSInputStream` and wraps a Java `InputStream`, an Apache Commons Net `FTPClient`, and Hadoop `FileSystem.Statistics`. Its visible API is stream-position oriented: `getPos`, `seek`, `seekToNewSource`, synchronized single-byte and buffered `read`, synchronized `close`, and mark/reset methods. The `FTPFileSystem` documentation says the filesystem is backed by an Apache Commons Net FTP client.

`org.apache.hadoop.fs.kfs.KosmosFileSystem` exposes Hadoop's `FileSystem` contract backed by KFS. It supports URI/name initialization, working-directory management, directory creation, type checks, status listing, file status, create/open, rename, delete, length and replication getters/setters, default replication/block size, path locking/release, block-location lookup, local copy helpers, and local-output staging hooks. `append` is explicitly documented as unsupported.

`org.apache.hadoop.fs.permission` contains permission and ownership models. `AccessControlException` is an `IOException` with a default constructor for `RemoteException` unwrapping and a message constructor. `FsAction` is an enum-like public type for read/write/execute actions with `implies`, bitwise-style `and`, `or`, and `not`, plus public `INDEX` and `SYMBOL` fields for octal and symbolic representations. `FsPermission` implements `Writable` and supports construction from actions, short modes, or another permission; conversion to/from short; static `read`; equality/hash/string conversion; umask application; configuration-backed `getUMask`/`setUMask`; default permission lookup; immutable creation; and parsing from Unix symbolic permission strings. `PermissionStatus` implements `Writable` for user, group, and permission triples with immutable creation, getters, umask application, instance/static serialization helpers, static `read`, and string conversion.

`org.apache.hadoop.fs.s3` describes the older block-based S3 filesystem. `Block` stores a block id and length. `FileSystemStore` is the backing-store interface for versions, inode/block storage, existence checks, inode/block retrieval, deletion, shallow/deep listing, testing-only purge, and diagnostic dump. `INode` stores file metadata, including file type and an array of S3 `Block` pointers, and provides directory/file checks, serialized length, `serialize`, static `deserialize`, `FILE_TYPES`, and `DIRECTORY_INODE`. `MigrationTool` is a `Configured` `Tool` for rewriting old S3 filesystem block metadata without touching data files. `S3Credentials` extracts access keys from URI/configuration and exposes access-key getters. `S3Exception`, `S3FileSystemException`, and `VersionMismatchException` model runtime and checked failures. `S3FileSystem` extends `FileSystem`, can be constructed with a `FileSystemStore`, and exposes URI/name, initialization, working directory, mkdirs, `isFile`, list, create/open, rename, delete, and file status. Its docs distinguish this block-based S3 layout from native S3 storage; `append` is unsupported and create/mkdir permission parameters are ignored.

`org.apache.hadoop.fs.s3native.NativeS3FileSystem` is the native-object S3 filesystem. It implements the usual `FileSystem` surface for initialize, create/open, delete overloads, file status, URI, listing, mkdirs, rename, and working directory, with `append` unsupported. Its documentation explicitly contrasts it with `S3FileSystem`: files are stored on S3 in native form so other S3 tools can read them.

`org.apache.hadoop.fs.shell` provides command scaffolding. `Command` is an abstract command with a protected `FileSystem`, protected argument array, abstract `getCommandName`, protected path-level `run`, and public `runAll` that executes across source paths and returns 0 or -1. `CommandFormat` parses command-line options and validates arity. `Count` implements the `-count` command, with static `matches`, command name, path-level run, and public `NAME`, `USAGE`, and `DESCRIPTION` constants.

The `org.apache.hadoop.io` section starts with serialization foundations. `AbstractMapWritable` is a configurable `Writable` base that carries per-instance class-id maps, supports synchronized `addToMap` and `copy`, class/id lookup, configuration accessors, and read/write. The docs emphasize that ids are instance-local, byte-sized, and limited to 1 through 127. `GenericWritable` wraps one of a fixed set of `Writable` classes supplied by subclass `getTypes`, implements `Configurable`, passes configuration to wrapped objects before deserialization, and is documented as more compact than `ObjectWritable` for known heterogeneous value sets.

File-backed collection formats include `ArrayFile`, `MapFile`, and `SetFile`. `ArrayFile` is a dense integer-to-value mapping implemented over `MapFile`; its reader can `seek(long)`, read `next(Writable)`, report the current numeric key, and random-access `get(long, Writable)`, while the writer appends values in order. `MapFile` exposes static `rename`, `delete`, `fix`, and `main`, and public `INDEX_FILE_NAME`/`DATA_FILE_NAME`. `MapFile.Reader` opens sequence-backed data/index files, can be reset, close, report key/value classes, seek, iterate, `get`, find closest keys, return the mid key, and retrieve the final key. `MapFile.Writer` has multiple constructors around key/value classes or comparators plus compression/progress options, configurable index interval getters/setters, synchronized `append`, and synchronized `close`; appended keys must be sorted. `SetFile` is a key-only `MapFile` variant whose reader seeks/nexts/gets keys and whose writer appends strictly increasing keys, with one older constructor deprecated in favor of passing a `Configuration`.

Primitive and buffer writables dominate the middle of the chunk. `ArrayWritable` stores homogeneous `Writable` arrays, exposes value class, string/object array conversions, setters/getters, and `Writable` serialization. `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, and `LongWritable` are `WritableComparable` wrappers with default/value constructors, `set`, `get`, `readFields`, `write`, equality/hash/compare/string methods, and optimized `WritableComparator` nested classes. `LongWritable` also exposes `DecreasingComparator`. `BytesWritable` is a mutable resizable byte sequence with separate logical size and capacity, range-copy setters, direct backing-array getter, serialization, equality, lexicographic comparison, hash, and hex-like string conversion; its comparator works directly on serialized bytes. `NullWritable` is a singleton zero-data `WritableComparable`, with an optimized comparator.

Reusable in-memory buffers include `DataInputBuffer`, `DataOutputBuffer`, `InputBuffer`, and `OutputBuffer`. `DataInputBuffer` and `InputBuffer` reset over byte arrays and report data/position/length. `DataOutputBuffer` and `OutputBuffer` expose backing data, valid length, reset, and direct copy/write from `DataInput` or `InputStream`. These classes are intended to avoid repeated allocation in serialization loops. `CompressedWritable` defines lazy compressed-state behavior through `readFields`, `ensureInflated`, protected `readFieldsCompressed`, `write`, and protected `writeCompressed`.

String and object conversion APIs include `DefaultStringifier`, `Stringifier`, and `ObjectWritable`. `Stringifier<T>` converts objects to/from string representations and is closeable. `DefaultStringifier<T>` uses Hadoop serialization plus base64-style string storage and provides static `store`, `load`, `storeArray`, and `loadArray` helpers for `Configuration`. `ObjectWritable` is a configurable polymorphic `Writable` that records the declared class and instance; it can write/read `Writable`s, strings, primitives, and arrays through static `writeObject` and `readObject` helpers.

Utility and hash APIs include `IOUtils`, `MD5Hash`, `MultipleIOException`, and `RawComparator`. `IOUtils` has stream-copy overloads, full-read/full-skip loops, close cleanup helpers that ignore cleanup-time `IOException`s, socket close, and a `NullOutputStream`. `MD5Hash` is a `WritableComparable` over 16-byte MD5 digests with string/byte constructors, static `read`, setters, digest factories for byte arrays, ranges, strings, and `UTF8`, half/quarter digest extraction, equality/hash/compare/string behavior, hex parsing, `MD5_LEN`, and a raw comparator. `MultipleIOException` wraps lists of `IOException`s and can collapse zero/one/many exceptions through `createIOException`. `RawComparator<T>` extends `Comparator<T>` with byte-array range comparison.

`SequenceFile` is the most substantial persistence API in this chunk. The outer class exposes deprecated configuration-based compression type getters/setters, many `createWriter` overloads for filesystem/path/key/value/compression/codec/progress/metadata combinations, and `SYNC_INTERVAL`. Its documentation describes the SequenceFile header and the record, record-compressed, and block-compressed on-disk layouts, including key/value classes, compression flags/codecs, metadata, sync marker, record lengths, and compressed blocks. `SequenceFile.CompressionType` is an enum. `SequenceFile.Metadata` is a `Writable` map of `Text` keys to `Text` values with get/set, map access, serialization, equality/hash/string conversion.

`SequenceFile.Reader` opens a filesystem path, supports protected `openFile` specialization, synchronized close, key/value class names and class lookup, compression and metadata inspection, current-value retrieval, typed and raw `next` APIs, raw key/value creation and reads, object-oriented `next`, `seek`, `sync`, `syncSeen`, position reporting, and string conversion. One raw `next(DataOutputBuffer)` overload is deprecated in favor of `nextRaw`. `SequenceFile.Sorter` sorts and merges sequence files using either classes or a `RawComparator`, with configurable merge factor, memory, and progress callback. It can sort to a file, sort and return an iterator, merge via segment lists or path arrays with optional input deletion and temporary directories, clone file attributes into a writer, and write raw iterator records. `RawKeyValueIterator` exposes current raw key/value, next, close, and progress. `SegmentDescriptor` models sortable merge segments with sync handling, input preservation, comparison/equality/hash, raw key/value reads, key access, and cleanup that closes/deletes by default. `ValueBytes` writes uncompressed or compressed bytes and reports stored size. `SequenceFile.Writer` has constructors with file creation options, reports key/value classes and compression codec, creates sync points, synchronized close, synchronized typed and object appends, raw append, file length, and serializer fields for keys and values.

The chunk closes with `SortedMapWritable`, `Stringifier`, and the beginning of `Text`. `MapWritable` and `SortedMapWritable` implement `Map<Writable,Writable>` and `SortedMap<WritableComparable,Writable>` respectively on top of `AbstractMapWritable`, with normal collection operations plus `Writable` serialization. `Text` begins as a `WritableComparable` UTF-8 byte-string type with constructors from nothing, `String`, another `Text`, or byte array. The visible methods in this chunk expose raw bytes, byte length, Unicode scalar lookup at a byte position without converting to `String`, byte-position `find` overloads, setters from `String`, UTF-8 bytes, another `Text`, byte ranges, and the start of `append`.

## Control flow and behavioral contracts

The XML itself has no executable flow, but it defines the caller-visible protocols. Filesystem flows follow the `FileSystem` template: construct or initialize with URI and configuration, resolve a working directory, then perform mkdir/list/status/create/open/rename/delete operations. Optional append is repeatedly documented as unsupported for KFS, legacy S3, and native S3. S3 and KFS filesystem methods can throw `IOException` on remote or backing-store failures.

`FTPInputStream` is a stateful wrapper around an FTP data stream. Reads are synchronized and update the stream position and statistics. `seek` and `seekToNewSource` advertise `FSInputStream` random-access hooks, but with FTP backing they are likely constrained by reopening/repositioning behavior in adjacent implementation code. `close` must coordinate both the input stream and the `FTPClient`.

Permission flow is serialization-friendly. `FsPermission` converts between three `FsAction` values and a short mode, reads/writes itself through `DataInput`/`DataOutput`, and can be derived from configuration umask settings. `PermissionStatus` composes owner, group, and `FsPermission`, then applies umask by returning another permission status. `AccessControlException` is designed to travel through Hadoop RPC exception unwrapping.

The legacy S3 flow is inode/block based. `S3FileSystem` presents normal file operations, but persistence goes through `FileSystemStore`: paths map to `INode`s, files map to block arrays, and blocks map to remote S3 objects or local temporary files. Reading retrieves an inode, then retrieves blocks by byte range; writing stores blocks then stores inode metadata. Migration rewrites block metadata in place without changing data files. Native S3 flow is object based, where filesystem paths correspond to native S3 keys rather than Hadoop-specific block metadata.

Shell command flow is small but explicit. A concrete `Command` parses/stores arguments, `runAll` iterates source paths, and each path is delegated to protected `run(Path)`. `CommandFormat` handles options and parameter count checks before command execution. `Count.matches` gates dispatch for the count command.

Writable flow is standardized around `write(DataOutput)` and `readFields(DataInput)`. Primitive writables expose mutable setters/getters and implement comparison, so the same object may be reused during read loops. Raw comparator nested classes let sort code compare serialized bytes without allocating or deserializing objects.

Map-like writable flow relies on class-id side metadata. `AbstractMapWritable` assigns byte ids to classes seen in a specific map instance, serializes those mappings, then serializes entries by id. `MapWritable` and `SortedMapWritable` provide collection facades around that encoded type table. `GenericWritable` writes a type discriminator selected from a subclass-provided fixed type list, then delegates wrapped object serialization.

File-format flow is ordered and stateful. `MapFile.Writer`, `SetFile.Writer`, and `ArrayFile.Writer` require sorted or naturally increasing append order. `MapFile.Reader` uses a data sequence file plus a sparse index and supports seek/get/closest-key lookup through that index. `MapFile.fix` rebuilds an index from a data file, with dry-run support and a return value indicating valid entries or no-op.

SequenceFile write flow constructs a writer with filesystem, path, key/value classes, compression settings, progress callback, and optional metadata. Callers append typed objects or raw serialized key/value bytes, optionally insert sync markers, observe file length, and close to finish. Reader flow opens the file, validates/reads header metadata, exposes key/value classes and compression settings, then iterates typed or raw records. `seek` moves to an exact writer-reported position, while `sync` advances to the next sync marker for split-style scanning.

SequenceFile sort/merge flow is external-sort oriented. The sorter consumes one or more sequence files, buffers data up to a configured memory budget, writes sorted runs, merges runs with bounded fan-in, exposes raw key/value iterators, and optionally deletes temporary or input segments. `SegmentDescriptor.cleanup` is part of this lifecycle and can delete segment files unless preservation is requested.

`DefaultStringifier` flow goes through the configured serialization framework: serialize object bytes, encode them into a string, store them under a configuration key, then later decode and deserialize using the declared class. `ObjectWritable` flow stores class identity with each value, so it can reconstruct polymorphic values at read time but pays per-record class-name overhead.

## State, persistence, and side effects

The JDiff XML is a persistent API compatibility artifact. The runtime APIs it describes are state-heavy: FTP client sessions, Hadoop filesystem working directories, KFS and S3 remote metadata, POSIX-style permissions, S3 credentials, command argument state, writable object contents, buffer backing arrays, class-id maps, on-disk sequence/map/set/array files, configuration-encoded serialized objects, MD5 digest bytes, and open stream resources.

KFS and S3 filesystems persist data outside the local process. KFS operations affect a Kosmos filesystem namespace and expose block locations, locks, replication, and local-output staging. Legacy S3 persists Hadoop-specific `INode` metadata and block objects, with a versioned `FileSystemStore` contract and a migration tool for metadata upgrades. Native S3 persists regular S3 objects that external S3 tools can read. The two S3 APIs are not interchangeable at the storage-layout level.

Permission state is encoded compactly. `FsPermission` persists as a short mode and can be converted back into user/group/other actions. `PermissionStatus` persists owner, group, and permissions, and its static write helper allows writing these components without constructing a full object. Umask lives in `Configuration` under `UMASK_LABEL`, with `DEFAULT_UMASK` as the fallback.

Writable primitives are mutable value containers. Buffer types expose internal byte arrays whose valid data is bounded by length/size, so callers must not assume the entire backing capacity is meaningful. `BytesWritable` distinguishes logical size from capacity and preserves old range data on resize while leaving new bytes undefined. `DataOutputBuffer`/`OutputBuffer` reuse storage across writes; `DataInputBuffer`/`InputBuffer` reuse input views across reads.

`AbstractMapWritable`, `MapWritable`, and `SortedMapWritable` persist a per-instance class table before entries. That design avoids global static ids but creates compatibility dependence on correct table serialization and read order. The documented 127-class ceiling is a practical limit for heterogeneous maps.

SequenceFile is an externally visible binary format. Its header records key/value class names, compression booleans, codec name, metadata, and sync marker. Record-compressed files compress values individually. Block-compressed files group key lengths, keys, value lengths, and values into compressed blocks. Sync markers and `SYNC_INTERVAL` affect splitability and recovery. `SequenceFile.Metadata` persists `Text` key/value attributes in the file.

MapFile, SetFile, and ArrayFile are directory-style persistent formats layered on SequenceFile. MapFile uses `data` and `index` members named by public constants. Index interval controls lookup speed versus index size, and the static `fix` method can recreate the index for a corrupt map directory.

External side effects include FTP network I/O, KFS and S3 remote requests, local temporary files for S3 block retrieval/store, credential extraction from URI/configuration, command-line filesystem operations, file descriptor/stream close behavior, configuration mutation by stringifiers and compression setters, and temporary-file deletion during sequence sort/merge cleanup.

## Dependencies and integration points

FTP APIs integrate with Apache Commons Net `FTPClient`, Java `InputStream`, Hadoop `FSInputStream`, `FileSystem.Statistics`, and the broader `FileSystem` abstraction.

KFS and S3 filesystems integrate with `org.apache.hadoop.fs.FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `FSDataInputStream`, `FSDataOutputStream`, `FsPermission`, `Progressable`, `Configuration`, `URI`, and `IOException`. The S3 packages also integrate with AWS S3 concepts, credentials, temporary local files, and Hadoop `Tool`/`Configured` for migration.

Permission APIs integrate with Hadoop RPC (`RemoteException` unwrapping), `Writable`, `DataInput`, `DataOutput`, `Configuration`, and filesystem create/status APIs that carry `FsPermission` or `PermissionStatus`.

Shell APIs integrate with `FileSystem`, `Path`, command-line argument arrays, option parsing, and command dispatch in the Hadoop filesystem shell.

Hadoop IO APIs integrate pervasively with Java `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `Closeable`, `Socket`, `Comparator`, `SortedMap`, `TreeMap`, `List`, and Hadoop `Configuration`, `Configurable`, `Writable`, `WritableComparable`, `WritableComparator`, `RawComparator`, `CompressionCodec`, `Progressable`, and filesystem streams.

`DefaultStringifier` depends on Hadoop's serialization framework and stores values in `Configuration`. `ObjectWritable` depends on reflection/class loading and configurable deserialization. `GenericWritable` depends on subclasses returning stable class arrays.

SequenceFile integrates with `FileSystem`, `FSDataInputStream`, `Path`, `Writable`, `WritableComparable`, `RawComparator`, `CompressionCodec`, `Serializer`, `DataOutputBuffer`, `Progress`, and `Progressable`. It is a core interchange format for MapReduce-era data, and MapFile/SetFile/ArrayFile are direct higher-level integrations.

`Text` integrates with Hadoop's UTF-8 handling, `WritableComparable`, byte-level search, and later APIs outside this chunk. The visible methods already show that `Text` is byte-oriented rather than a thin Java `String` wrapper.

## Risks and compatibility notes

This is a line-bounded partial chunk. It starts after the beginning of `FTPFileSystem` and ends inside `Text.append`, so conclusions for those boundary classes require adjacent chunk reports. The chunk is still internally complete for all classes whose start and end markers fall within the range.

The XML is generated API metadata. It does not expose implementation branches, synchronization internals beyond method flags, private fields, or concrete error handling. Behavioral notes here are therefore based on public signatures and Javadocs, not source bodies.

S3 compatibility is risky because two public S3 filesystems use different storage layouts. `S3FileSystem` stores block metadata and inodes in a Hadoop-specific format; `NativeS3FileSystem` stores objects natively. Migration tooling rewrites metadata only, so bugs in version detection, inode serialization, or block mapping can make legacy data unreadable without touching underlying block objects.

Filesystem methods that ignore permissions or do not support append can surprise callers using the generic `FileSystem` API. KFS and S3 append explicitly being unsupported should be tested through generic callers. S3 create/mkdir permission parameters are documented as ignored, so security expectations must be enforced elsewhere.

Credential handling is a security-sensitive integration point. `S3Credentials.initialize` can read secrets from URI or configuration and throws `IllegalArgumentException` if missing. URI-embedded credentials risk leaking through logs or diagnostics in surrounding code.

Mutable writable types carry aliasing and reuse risk. `BytesWritable.get()` and buffer `getData()` expose backing arrays whose valid content is shorter than capacity. Reusing writable instances during iteration is idiomatic but can corrupt downstream state if callers retain references without copying.

Raw comparators and serialized formats are compatibility-sensitive. Primitive comparator implementations must match the byte layout written by each writable. Any change in `BytesWritable`, `Text`, `MD5Hash`, or primitive writable serialization affects sorting, partitioning, MapFile indexes, and SequenceFile compatibility.

`AbstractMapWritable` and `GenericWritable` depend on stable class-id/type ordering. The 127-class limit in `AbstractMapWritable` is explicit. Changing subclass `GenericWritable.getTypes()` order or removing a class can break old serialized data.

SequenceFile is a major persistence contract. Header fields, sync marker behavior, compression type/codec recording, metadata encoding, record/block compressed layouts, raw key/value APIs, and `seek` versus `sync` semantics must remain stable for interoperability and split processing. Deprecated compression configuration methods remain public in this snapshot and may still be used by callers.

MapFile/SetFile/ArrayFile require sorted or increasing append order. Incorrect ordering can corrupt indexes or make seek/get operations unreliable. `MapFile.fix` is a recovery hook, but it depends on correct key/value classes and a readable data file.

Resource lifecycle risks are visible across the chunk: FTP streams must close network clients, filesystem streams must close remote resources, SequenceFile readers/writers and sort iterators are closeable, sort segment cleanup may delete temporary files, and `IOUtils.cleanup` intentionally ignores cleanup exceptions, which can hide secondary failures.

## Test signals

JDiff-level validation should confirm this range remains well-formed XML and preserves package boundaries, class/interface start/end markers, inheritance, implemented interfaces, constructor and method signatures, parameter types, declared exceptions, fields, deprecation text, synchronization flags, and embedded Javadocs.

FTP tests should cover `FTPInputStream` position tracking, synchronized single-byte and buffered reads, EOF behavior, unsupported or emulated seeking, `seekToNewSource`, statistics updates, mark/reset behavior, and close behavior that completes the FTP client transfer cleanly.

KFS filesystem tests should cover URI initialization, working-directory resolution, mkdir/list/status/type checks, create/open/rename/delete, block-location lookup, replication/block-size calls, path lock/release, local copy and local-output staging, and unsupported append behavior through the generic `FileSystem` API.

Permission tests should cover every `FsAction` implication and `and`/`or`/`not` combination, short-mode round trips, symbolic `valueOf`, default and configured umask, immutable permission creation, `PermissionStatus` serialization/static write/read, umask application to permission status, and `AccessControlException` construction/RPC unwrapping.

Legacy S3 tests should cover `FileSystemStore` version checks, inode and block store/retrieve/delete/existence/listing, `INode` serialization/deserialization for files and directories, migration metadata rewrite without data-object changes, credential extraction and failure cases, `S3FileSystem` create/open/list/rename/delete/status behavior, ignored permission arguments, unsupported append, and version mismatch exceptions.

Native S3 tests should cover native object create/open/delete/list/status/rename/mkdirs flows, working-directory resolution, append rejection, and interoperability expectations that created objects are readable by non-Hadoop S3 tooling.

Shell tests should cover `CommandFormat` option parsing, arity failures, `Command.runAll` success and failure return values across multiple paths, and `Count.matches` plus count command output behavior.

Writable tests should cover primitive read/write round trips, compare/equality/hash consistency, raw comparator byte-order equivalence with object comparison, mutable setter/getter behavior, null singleton serialization, `BytesWritable` size/capacity/range-copy behavior, buffer reset/getData/getLength/getPosition invariants, and `CompressedWritable` lazy inflate/write paths.

Map and generic writable tests should cover class-id table serialization with heterogeneous key/value classes, copy constructors, map/sorted-map collection semantics, sorted-map range views, the 127-class limit, configuration propagation before deserialization, and stable `GenericWritable.getTypes()` ordering.

String/object serialization tests should cover `DefaultStringifier` object and array store/load through `Configuration`, empty-array failure behavior documented by `storeArray`, close behavior, `ObjectWritable` declared-class handling, nulls, primitives, strings, arrays, `Writable` instances, and configurable nested objects.

SequenceFile tests should cover every public `createWriter` family, metadata write/read, compression type handling including deprecated config helpers, none/record/block compression, sync marker creation and `sync` scanning, exact `seek` to writer positions, typed and raw reader iteration, object-oriented reads, current-value retrieval, value-byte compressed/uncompressed writes, writer length reporting, close idempotence/failure behavior, and compatibility with files written by older 0.18.x APIs.

SequenceFile sorter tests should cover class-based and raw-comparator sorting, memory/factor settings, progress reporting, sort-to-file, sort-and-iterate, merge overloads with and without input deletion, temporary directory use, clone-file-attributes, raw iterator lifecycle, segment sync and preservation flags, and cleanup deleting only intended temporary files.

MapFile, SetFile, and ArrayFile tests should cover writer append ordering enforcement, index interval configuration, reader seek/get/getClosest/midKey/finalKey behavior, reset/open/close, corrupt-index recovery through `MapFile.fix` including dry run, set membership lookup, and dense array numeric-key access.

IO utility and hash tests should cover `copyBytes` close/non-close variants, configuration buffer-size behavior, `readFully` and `skipFully` EOF failures, cleanup ignoring close failures while logging as expected, socket close, null output writes, MD5 digest constructors and static digest methods, hex parsing, half/quarter digest values, and raw comparator consistency.

`Text` tests for the visible part of this chunk should cover constructors from string/text/bytes, raw byte and length invariants, `charAt` for valid scalars, invalid offsets, and trailing bytes, byte-position `find` with and without start offsets, setters from strings and UTF-8 byte ranges, and the beginning of append behavior in the adjacent chunk.

### subset-b-007282: lines 12397-18635

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml lines 12397-18635

## Scope

This chunk is a JDiff/API XML slice for Hadoop 0.18.3. It begins inside the public API entry for `org.apache.hadoop.io.Text`, continues through the rest of `org.apache.hadoop.io`, `org.apache.hadoop.io.compress`, native LZO/zlib adapters, retry and serialization APIs, the Hadoop IPC/RPC API surface, runtime log-level helpers, and the beginning of `org.apache.hadoop.mapred`. It ends inside the long class documentation for `org.apache.hadoop.mapred.JobClient`.

The source is generated API metadata rather than Java implementation. The research surface is therefore the compatibility contract: public/protected classes and interfaces, inheritance, implemented interfaces, constructors, method signatures, declared exceptions, fields, visibility/static/final/synchronized/abstract flags, deprecation markers, and embedded Javadocs.

## Purpose

The `org.apache.hadoop.io` portion documents Hadoop's core `Writable` serialization contract and several key value types. It covers UTF-8 text representations, variable-length numeric writables, version-checked writable records, raw byte comparators, factories and aliases for writable instantiation, and shared utilities for compressed byte/string arrays, zero-compressed integers, enum serialization, cloning, and exact skipping.

The `org.apache.hadoop.io.compress` portion documents the streaming compression abstraction used by SequenceFiles, MapReduce input/output formats, and file suffix based codec discovery. It defines codec factories, compressor/decompressor pooling, compression stream base classes, Java zlib/gzip implementations, and optional native LZO/zlib wrappers.

The retry and serialization sections expose reusable infrastructure for proxy-level retry policies and pluggable object serialization. These APIs are used by Hadoop RPC clients and by MapReduce sorting/shuffling paths that need raw or deserialized comparison.

The `org.apache.hadoop.ipc` portion documents Hadoop's pre-protobuf Writable-based RPC framework: clients send one `Writable` parameter to servers, receive one `Writable` result, create dynamic protocol proxies, perform parallel calls, enforce protocol version checks, expose server-local call context, and publish RPC metrics through Hadoop metrics and JMX.

The `org.apache.hadoop.mapred` portion starts the old MapReduce API surface. It covers cluster status, counters, job history parsing, file input/output format bases, file splits, ID parsing/serialization, input format/split contracts, input/job configuration exception types, task isolation runner entry point, and the beginning of `JobClient`, the primary user-facing bridge to `JobTracker`.

## Important APIs, Types, and Functions

### Text and Writable Core

- The chunk starts with the tail of `Text`: byte-range `append`, `clear`, `toString`, `readFields`, static `skip`, `write`, bytewise `compareTo`, equality/hash, UTF-8 `decode`/`encode` overloads with replacement control, static `readString`/`writeString`, UTF-8 validation overloads, `bytesToCodePoint(ByteBuffer)`, and `utf8Length(String)`.
- `Text.Comparator` extends `WritableComparator` and provides raw byte-array comparison optimized for serialized `Text` keys.
- `TwoDArrayWritable` wraps `Writable[][]` matrices with a declared value class, `toArray`, `set`, `get`, and Writable read/write.
- `UTF8` is a deprecated `WritableComparable` string type replaced by `Text`. It exposes raw bytes/length, string and copy constructors, setters, read/write/skip, comparison/equality/hash/string conversion, and static UTF-8 string helpers.
- `UTF8.Comparator` is the raw comparator counterpart for serialized `UTF8` keys.
- `VersionedWritable` is an abstract base for Writables with a single-byte implementation version. Its `readFields` checks the incoming version and raises `VersionMismatchException` when the serialized version differs from `getVersion()`.
- `VIntWritable` and `VLongWritable` are `WritableComparable` wrappers using Hadoop variable-length integer encodings via `WritableUtils`.
- `Writable` defines the core `write(DataOutput)` and `readFields(DataInput)` protocol. The docs explicitly encourage object storage reuse during deserialization.
- `WritableComparable<T>` combines `Writable` and `Comparable<T>` for MapReduce keys.
- `WritableComparator` is the central comparator registry and raw comparison base. It can register optimized comparators with `define`, retrieve comparators with synchronized `get`, create new key instances, compare deserialized keys, compare raw serialized byte ranges, and parse primitive values or vint/vlongs from byte arrays.
- `WritableFactories` and `WritableFactory` provide synchronized class-to-factory registration for non-public Writables and reflective construction with optional `Configuration`.
- `WritableName` maps Writable classes to compact names/aliases and resolves aliases back to classes.
- `WritableUtils` provides compressed byte/string array helpers, plain string/string-array helpers, display formatting for byte arrays, serialization-based clone/cloneInto, vint/vlong read/write and size/sign helpers, enum string serialization, and `skipFully` for exact byte skipping.

### Compression

- `CodecPool` is a global compressor/decompressor pool. It gets compressors/decompressors for a `CompressionCodec`, creating new instances when no reusable object is available, and returns them to the pool for reset/reuse.
- `CompressionCodec` encapsulates a streaming compression/decompression pair. It creates compression input/output streams, optionally with supplied `Compressor`/`Decompressor` instances, exposes compressor/decompressor implementation types, creates fresh codec state, and reports a default file extension.
- `CompressionCodecFactory` reads configured codec classes from `io.compression.codecs` with gzip/zip defaults, maps filename suffixes to codecs, exposes static get/set helpers for codec class lists, removes suffixes, and has a diagnostic `main`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases that wrap protected final `in`/`out` streams. They require concrete `read`/`write`, `resetState`, and output `finish` implementations to avoid accidentally leaking raw underlying stream behavior.
- `Compressor` defines the Deflater-like contract: feed input, optional dictionary, `needsInput`, byte counters, `finish`, `finished`, `compress`, `reset`, and `end`.
- `Decompressor` defines the Inflater-like counterpart: feed input, optional dictionary, `needsInput`, `needsDictionary`, `finished`, `decompress`, `reset`, and `end`.
- `DefaultCodec` implements `CompressionCodec` and `Configurable`, using Hadoop configuration to create default deflate streams and zlib compressor/decompressor instances.
- `GzipCodec` extends `DefaultCodec` for gzip, with protected nested `GzipInputStream` and `GzipOutputStream` bridge classes around decompressor/compressor streams. The nested streams expose normal stream operations plus `resetState`; output streams support `finish` without closing the underlying stream.
- `LzoCodec` implements `CompressionCodec` and `Configurable` for streaming LZO. It exposes `isNativeLzoLoaded`, creates LZO streams/state, and reports the default LZO extension.
- `LzoCompressor` and `LzoDecompressor` implement native-backed `Compressor`/`Decompressor`, with constructors accepting compression strategy and direct buffer size, native-library availability checks, input/dictionary methods, finish/needs/finished state, byte counters for compression, reset/end, and a `finalize` cleanup path on the decompressor.
- `LzoCompressor.CompressionStrategy` and `LzoDecompressor.CompressionStrategy` are public enums with normal `values` and `valueOf`.
- `BuiltInZlibDeflater` and `BuiltInZlibInflater` adapt `java.util.zip.Deflater`/`Inflater` to Hadoop `Compressor`/`Decompressor`.
- `ZlibCompressor` and `ZlibDecompressor` are native-oriented zlib implementations with configurable compression level, strategy, header mode, and direct buffer size. Public nested enums model zlib header, compression level, and strategy options.
- `ZlibFactory` centralizes native-zlib availability and creation. It checks whether native zlib is loaded, returns zlib compressor/decompressor classes, creates compressor/decompressor instances, and gets/sets compression level and strategy through `Configuration`.

### Retry and Serialization

- `RetryPolicies` exposes stock immutable `RetryPolicy` implementations: try once and fail, try once and ignore void failures, retry forever, limited fixed sleep, limited maximum-time fixed sleep, proportional sleep, exponential backoff, exception-specific retry maps, and remote-exception-specific retry maps.
- `RetryPolicy.shouldRetry(Exception, int)` decides whether a failed method invocation should be retried based on the thrown exception and retry count.
- `RetryProxy.create` builds dynamic proxies over implementation objects, either with one policy for every interface method or a method-name map with a default fallback policy.
- `Serializer<T>` and `Deserializer<T>` provide `open`, per-object serialize/deserialize, and `close` contracts over streams. `Deserializer.deserialize(T)` may reuse a supplied object.
- `Serialization<T>` pairs serializers and deserializers and declares an `accept(Class<?>)` check.
- `SerializationFactory` reads `io.serializations` from configuration, instantiates serialization implementations, and chooses serializer/deserializer support for a target class.
- `WritableSerialization` adapts Hadoop `Writable.write`/`readFields` to the generic serialization framework.
- `JavaSerialization` is an experimental serialization for `java.io.Serializable`.
- `DeserializerComparator<T>` is a raw comparator that deserializes both byte ranges before comparing normally; `JavaSerializationComparator<T>` specializes that path for Java-serialized comparable objects.

### IPC, RPC, and Metrics

- `Client` is the Writable IPC client. Constructors bind a value class, configuration, and optional `SocketFactory`; static `setPingInterval` writes ping interval configuration; `call` sends a `Writable` to one address, to one address with ticket/user context, or to many addresses in parallel; `stop` terminates all client threads.
- `RemoteException` carries a remote exception class name and message. `unwrapRemoteException` either unwraps to one of requested lookup types or reflectively instantiates an `IOException`/`Throwable` with a string constructor.
- `RPC` creates protocol proxies (`getProxy` overloads and `waitForProxy`), stops proxies, performs parallel calls, and constructs `RPC.Server` instances for protocol implementations. The docs define an RPC protocol as a Java interface whose parameters and returns are supported Writable/primitive/string/array forms and whose protocol version is checked.
- `RPC.Server` extends the abstract IPC `Server` and dispatches incoming Writable calls to the implementation instance. Its constructors bind instance, configuration, address, port, handler count, and verbosity.
- `RPC.VersionMismatch` reports protocol incompatibility with interface name, client version, and server version getters.
- `Server` is the abstract IPC service. It binds sockets, starts/stops/joins handler threads, exposes listener address, call queue length, open connection count, socket send buffer sizing, a no-longer-used timeout setter, static access to current server and remote caller IP/address during a call, and an abstract `call(Writable, long)` handler.
- `VersionedProtocol.getProtocolVersion(String, long)` is the base protocol-version negotiation method. Implementing protocol interfaces are expected to expose a static final `versionID`.
- `RpcMetrics` publishes queue and processing time metrics, a map of per-method rates, and registers a JMX MBean. It implements Hadoop metrics `Updater` with `doUpdates` and supports `shutdown`.
- `RpcMgtMBean` is the JMX management interface for sampled operation counts, processing-time averages/min/max, queue-time averages/min/max, min/max reset, open connections, and queued calls.

### Logging and MapReduce APIs

- `LogLevel` is a runtime log-level tool with command-line `main` and usage text; `LogLevel.Servlet` provides the HTTP servlet implementation through `doGet`.
- `ClusterStatus` is a Writable cluster summary: task tracker count, current map/reduce task counts, maximum map/reduce capacity, `JobTracker.State`, and read/write serialization.
- `Counters` is a Writable iterable of counter groups. It creates/looks up groups and counters by enum or group/name strings, increments individual counters, sums/increments all counters, reports size, logs, and emits normal or compact string forms.
- `Counters.Counter` is a Writable value with name, display name, current long count, and increment operation.
- `Counters.Group` is a Writable iterable of counters with group name/display name, counter lookup, value lookup, size, and read/write.
- `DefaultJobHistoryParser.parseJobTasks` parses job history task data into `JobInfo`.
- `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` are typed `IOException` surfaces for output collisions, unexpected file/directory types, accumulated input validation problems, and invalid/missing job configuration.
- `FileInputFormat<K,V>` is the base `InputFormat`. It manages minimum split size, splitability, record reader creation, input path filters, status/path listing, deprecated `validateInput`, split generation, split-size computation, block-index lookup, input path setters/adders, and input path retrieval.
- `FileOutputFormat<K,V>` is the base `OutputFormat`. It manages compression enablement and codec class configuration, record writer creation, output spec checking, final output path, work output path, and task output path.
- `FileSplit` implements `InputSplit` with path, byte start, byte length, host locations, Writable serialization, and string rendering.
- `ID` is the numeric WritableComparable base for `JobID`, `TaskID`, and `TaskAttemptID`, with protected `id`, parse/format helpers, equality/hash/order, and static `read`/`forName`.
- `InputFormat<K,V>` defines input validation, split generation, and `RecordReader` creation. Its docs make the split-to-mapper and record-boundary responsibilities explicit.
- `InputSplit` is a Writable byte-oriented unit of work with length and location hostnames.
- `IsolationRunner.main` runs a single task from a task directory, supporting isolated task debugging/reproduction.
- `JobClient` implements `MRConstants` and `Tool` and is the primary user-job interface to `JobTracker`. In this chunk it exposes constructors for default or explicit JobTracker connection, synchronized command-line configuration access, initialization, close, filesystem access for staging, job submission by job file or `JobConf`, job lookup by `JobID` or deprecated string ID, map/reduce task reports by `JobID` or deprecated string ID, cluster status, running/submitted job lists, static `runJob`, task-output filter get/set helpers, `run`, default map/reduce capacity queries, system directory lookup, and `main`.

## Control Flow

Writable control flow is conventional and explicit: callers construct or reuse an object, invoke `write(DataOutput)` to emit fields, then `readFields(DataInput)` to restore fields into an existing object. Comparator control flow can avoid object allocation by using `WritableComparator.compare(byte[], int, int, byte[], int, int)` over serialized key bytes; custom comparators are registered globally and fetched by key class.

Text and UTF-8 flows operate on byte arrays rather than Java characters where possible. `Text` can append byte ranges, validate UTF-8, decode with either replacement or strict error handling, encode strings to `ByteBuffer`, traverse code points from a `ByteBuffer`, and compute encoded lengths. Serialized strings use Hadoop's length-prefixed forms; `skip` helpers allow consumers to move over encoded data without allocating the string.

Versioned writable flow starts by reading an implementation version byte, comparing it with `getVersion()`, and failing with `VersionMismatchException` before subclass-specific state is accepted. This gives evolving records an early compatibility gate.

Compression flow is pull/push oriented. Codecs create compression streams directly or with pooled compressor/decompressor instances. A compressor receives input when `needsInput()` is true, optionally receives a preset dictionary, then `compress` fills caller-provided output buffers until `finish`/`finished`. Decompressors mirror that with `needsDictionary`, `decompress`, and reset/end lifecycle. `CompressionInputStream.resetState` is specifically intended for cases where the underlying stream is repositioned.

Codec discovery flow starts with `CompressionCodecFactory` loading configured classes, registering default extensions, then choosing a codec by filename suffix. MapReduce output paths use `FileOutputFormat` compression configuration to decide whether and how to wrap record writers.

Retry flow wraps an implementation with `RetryProxy`; each thrown exception is passed to `RetryPolicy.shouldRetry` with the current retry count. Policies either rethrow, suppress void failures, sleep and retry, or consult exception/remote-exception maps.

Serialization flow starts from `SerializationFactory`, which reads configured serialization classes and chooses the first implementation whose `accept` method supports the target class. `Serializer.open`/`Deserializer.open` bind the stream, per-object calls move data, and `close` releases resources. Raw comparators built on deserialization deserialize byte slices before normal comparison.

IPC flow starts with an `RPC.getProxy`/`waitForProxy` or raw `Client` creation. The client serializes a Writable request, sends it to the server address, and returns a Writable response or unwraps network/remote exceptions. `RPC.Server` receives calls through `Server`, checks/uses protocol version information, invokes the protocol implementation, and records queue/processing metrics. Static `Server.get`, `getRemoteIp`, and `getRemoteAddress` expose per-call context during request handling.

MapReduce submission flow in `JobClient` is documented as: validate input/output specs, compute `InputSplit`s, prepare `DistributedCache` accounting, copy the job jar/configuration to the JobTracker system directory in the distributed filesystem, submit to `JobTracker`, and optionally monitor progress. `runJob` composes submission and polling until completion.

File input flow in `FileInputFormat` lists configured input paths, applies an optional `PathFilter`, validates input early, computes split sizes from block size/min split constraints, maps split offsets to block locations, and creates `FileSplit`s that become mapper work units. `InputFormat.getRecordReader` must then preserve record boundaries for the split.

File output flow in `FileOutputFormat` checks destination validity, configures compression, writes task attempt output under a task/work path, and later relies on the MapReduce commit path outside this chunk to promote task output to the final output directory.

Counters flow through nested group/counter lookup. Callers increment counters by enum or explicit group/name; groups lazily find or create counters; counters are serialized with the job/task state and can be rendered for logs or compact reporting.

## State and Persistence Behavior

This JDiff XML persists the Hadoop 0.18.3 public API for compatibility comparison. It does not contain runtime state itself, but the APIs define several durable or process-local state contracts.

`Writable`, `Text`, `UTF8`, `TwoDArrayWritable`, `VersionedWritable`, `VIntWritable`, `VLongWritable`, `ClusterStatus`, `Counters`, `FileSplit`, `ID`, and `InputSplit` define binary persistence through `DataInput`/`DataOutput`. Changes to field order, length encoding, version bytes, class names, or vint/vlong rules are wire-format compatibility risks.

`Text` and `UTF8` store byte arrays plus encoded lengths. APIs that expose raw bytes require callers to respect logical lengths; backing capacity may be larger than valid data. `Text` additionally defines strict versus replacing UTF-8 decode behavior, which affects data validation and corruption handling.

`WritableComparator`, `WritableFactories`, and `WritableName` maintain process-global registries. Their synchronized registration and lookup affect how ObjectWritable, sort comparators, and non-public Writable construction behave across the JVM.

`WritableUtils` clone/cloneInto persists temporary state through in-memory serialization buffers. Its compressed byte/string helpers persist data in compressed binary form, and its enum helpers persist enum names as strings rather than ordinals.

`CodecPool` is process-global mutable state for reusable native or Java compression objects. Returned compressor/decompressor instances can retain buffers and native resources until reused or ended.

Compression streams wrap underlying streams and may buffer data. `finish()` persists final compressed bytes without closing the underlying stream, while `close()` generally finishes and closes. `resetState()` discards codec state but intentionally does not reset underlying stream position.

Native LZO/zlib compressors and decompressors hold native state and direct buffers. Their `end` and finalization behavior is a resource-management boundary; leaks or reuse after `end` can affect long-running daemons.

`SerializationFactory` persists configured serialization class lists in `Configuration`. Serialized data compatibility depends on both the selected `Serialization` implementation and the target class availability.

`Client`, `Server`, and `RPC.Server` maintain sockets, handler/client threads, call queues, connection counts, ping intervals, listener addresses, and per-call thread-local context. RPC metrics persist process-local rolling rates and publish them to Hadoop metrics/JMX until shutdown.

`RemoteException` persists a remote class name and message over the wire. Unwrapping behavior depends on local class availability and constructors, so the same remote failure can materialize differently on different clients.

`FileInputFormat` and `FileOutputFormat` store job configuration keys for input paths, filters, min split size, output path, compression flag, and codec class. They persist intent in `JobConf`, while actual file data and task output are persisted through the configured `FileSystem`.

`FileSplit` persists path, start offset, length, and host locations, allowing computed client-side split plans to be shipped to task trackers.

`Counters` persist grouped long values as part of job/task progress and history. Counter names and group display names are externally visible in logs, web UI, and job history.

`JobClient` state includes the JobTracker connection, filesystem handle used for staging, command-line configuration, and task output filter. Its job submission path persists job jar/configuration and split metadata into the JobTracker system directory.

## Dependencies and Integration Points

- Java platform dependencies include `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `IOException`, `ByteBuffer`, `Serializable`, collections, enums, reflection, sockets, `SocketFactory`, servlet APIs for log-level servlet, and `java.util.zip` deflater/inflater classes.
- Hadoop configuration (`org.apache.hadoop.conf.Configuration`, `Configurable`, and `JobConf`) drives writable construction, codec registration, serialization selection, zlib settings, RPC ping intervals, MapReduce input/output paths, compression settings, and JobClient staging.
- Hadoop filesystem types (`FileSystem`, `Path`, `FileStatus`, `PathFilter`, and block location data) integrate with `FileInputFormat`, `FileOutputFormat`, `FileSplit`, and `JobClient.getFs`.
- Hadoop MapReduce types referenced in this chunk include `JobTracker`, `JobStatus`, `RunningJob`, `TaskReport`, `RecordReader`, `RecordWriter`, `Reporter`, `Mapper`, `OutputFormat`, `MRConstants`, and `DistributedCache`.
- Hadoop metrics integration appears through `org.apache.hadoop.metrics.Updater`, `MetricsTimeVaryingRate`, the RPC metrics subsystem, and JMX MBean exposure.
- Hadoop IPC integration depends on `Writable` request/response types, `VersionedProtocol`, protocol `versionID` fields, `RemoteException`, and server/client socket lifecycle.
- Compression integrates with native Hadoop code availability, zlib/lzo native libraries, Java gzip/deflate streams, codec suffix conventions, and MapReduce output compression configuration.
- Serialization integrates with Hadoop's `RawComparator` and with sort/shuffle paths where raw byte comparisons are used to avoid full object construction.
- Logging uses Apache Commons Logging and exposes runtime mutation through a CLI and servlet.

## Risks and Edge Cases

- The chunk starts mid-`Text` and ends mid-`JobClient` documentation; adjacent chunks are required for full class-level coverage of those two API entries.
- JDiff metadata omits method bodies. Exact byte layouts, synchronization internals, buffer ownership, codec reset behavior, RPC framing, and JobClient staging details require implementation-source review.
- `Text` and `UTF8` compatibility is sensitive to byte length versus array capacity. Callers that treat raw backing arrays as fully valid data can compare or serialize stale bytes.
- Strict versus replacement UTF-8 decoding changes whether malformed data fails fast or silently substitutes U+FFFD. Tests must pin both modes.
- `UTF8` is deprecated but still public. Removing or weakening it can break old serialized keys and user code from the Hadoop 0.18 era.
- `VersionedWritable` uses a single byte for versions and throws on mismatch. Classes that need backward-compatible migration must implement custom handling carefully around this gate.
- VInt/VLong encoding boundaries are subtle, especially negative values and first-byte size/sign decoding. Incompatibility here breaks Writables, Text lengths, counters, and many Hadoop wire formats.
- `WritableComparator` raw comparison must match object comparison exactly. Divergence causes MapReduce sort/group partitioning bugs that are hard to diagnose.
- Global registries in `WritableComparator`, `WritableFactories`, `WritableName`, and `CodecPool` can leak test state between cases and can be affected by duplicate registrations.
- `WritableUtils.cloneInto` documentation appears to reverse source/destination wording in the parameter text; callers should confirm implementation semantics before relying on the docs alone.
- Compression `finish`, `flush`, `close`, and `resetState` have distinct meanings. Calling them in the wrong order can produce truncated output, extra members, or stale decompressor state after seeking.
- `CompressionInputStream.resetState` assumes the underlying stream may be repositioned. Implementations that retain buffered compressed data after reset can corrupt split-based reads.
- Native LZO/zlib availability is environment-sensitive. Code must handle missing native libraries and fall back or fail explicitly.
- `LzoDecompressor.finalize` is a weak cleanup guarantee. Long-running daemons need explicit `end`/pool discipline to avoid native memory retention.
- `CodecPool` can hand out reused mutable compressor state. Returning a compressor before a stream has fully finished or reusing it without reset can cross-contaminate compressed data.
- `CompressionCodecFactory` suffix matching can be ambiguous for nested suffixes or unknown extensions. Codec registration order and file naming should be tested.
- Retry policies that suppress void failures or retry forever can hide outages or stall callers indefinitely if applied too broadly.
- `RetryProxy` dispatches by method name for policy maps; overloaded methods can share a name but require different retry behavior.
- Java serialization is marked experimental and depends on Java class compatibility/serialVersionUID. It is risky for durable cross-version data.
- `DeserializerComparator` allocates/deserializes during raw comparison; using it in high-volume sort paths can be much slower than a true raw comparator.
- RPC protocol version negotiation relies on protocol classes exposing `versionID` and implementations returning compatible versions. Incorrect versions cause `RPC.VersionMismatch` or silent incompatibility.
- `RemoteException.unwrapRemoteException` depends on local exception constructors and class availability. Missing classes degrade error specificity.
- `Client.call` parallel mode returns null for timed out or errored calls. Callers must not treat null as a successful null response.
- `Server.getRemoteIp` and `getRemoteAddress` return null outside valid RPC context or on error; authorization/audit code must handle that.
- `Server.setTimeout` is documented as no longer used, so callers relying on it for connection or request deadlines may get no effect.
- RPC metrics are sampled/interval-based. Tests and monitoring should distinguish instantaneous counts from last-interval averages/min/max.
- Runtime `LogLevel.Servlet` can mutate logging levels over HTTP; deployments need access control outside this API surface.
- `InputFormat.validateInput` is marked deprecated with guidance that `getSplits` can validate. Old callers may still rely on early validation behavior.
- `FileInputFormat` split computation must handle empty files, unsplittable compressed files, directories versus files, globbed paths, filters, block location lookups, and min split size bounds.
- `InputSplit.getLocations` affects data locality scheduling. Incorrect hostnames degrade performance or cause scheduler imbalance.
- `FileOutputFormat.checkOutputSpecs` must fail before job submission when output exists. Races with concurrent writers can still surface later.
- `Counters` names/display names are externally visible and serialized. Renaming groups/counters breaks history parsing, dashboards, and tests.
- `InvalidInputException` stores the provided problem list without copying; external mutation can change exception state after construction.
- `JobClient` submission crosses filesystem, distributed cache, split computation, job jar copying, RPC, and monitoring boundaries. Partial failures can leave staged files or submitted jobs with incomplete client state.
- Deprecated string-based `JobClient` and report APIs coexist with `JobID` overloads. Compatibility tests should cover both until old callers are dropped.

## Test Signals

Useful validation for this API surface should include:

- JDiff/API compatibility checks for every public/protected class, interface, constructor, method, field, exception, visibility flag, generic signature, deprecation marker, and nested type in this line range.
- `Text` tests for byte-range append, clear, read/write/skip, bytewise comparison, equality/hash, malformed UTF-8 strict and replacement decode, encode limits, validation, code-point traversal, and encoded-length calculation.
- `UTF8` compatibility tests against legacy serialized bytes, including skip, static read/write string helpers, raw comparator behavior, and deprecation-preserving API checks.
- `TwoDArrayWritable` read/write round trips with empty, rectangular, and ragged arrays plus declared value-class mismatch cases.
- `VersionedWritable` tests for matching version read/write and mismatch exception messages/string rendering.
- `VIntWritable`, `VLongWritable`, and `WritableUtils` tests at every encoding boundary: one-byte positive/negative values, multi-byte values, min/max int/long, sign/size decode, byte-array decode, and malformed/truncated inputs.
- `WritableComparator` tests proving raw byte comparison matches object comparison, plus registration/retrieval, key construction, primitive byte parsing, and hash byte behavior.
- `WritableFactories` and `WritableName` tests for synchronized registration, configured new instances, non-public Writable construction, aliases, unknown aliases, and registry isolation.
- `WritableUtils` tests for compressed byte/string arrays, string arrays, enum name round trips, display formatting, serialization clone/cloneInto, and `skipFully` short-skip failures.
- `CodecPool` tests for get/return/reuse/reset behavior, null returns, multiple codec types, and concurrent access.
- `CompressionCodecFactory` tests for configured codec class loading, defaults, extension selection, nested suffixes, `removeSuffix`, unknown file extensions, and diagnostic string output.
- Stream tests for `CompressionInputStream`/`CompressionOutputStream`: close/flush/finish order, reset after underlying seek, no leakage to raw stream reads/writes, and exception propagation.
- Compressor/decompressor contract tests for `setInput`, `needsInput`, dictionaries, finish/finished, zero-byte output cases, byte counters, reset/end, and reuse after pool return.
- Codec tests for `DefaultCodec`, `GzipCodec`, `LzoCodec`, built-in zlib, and native zlib/lzo availability paths. Include missing-native behavior and round trips over small, large, empty, and incompressible data.
- Zlib configuration tests for compression level, strategy, header mode, direct buffer size, and `ZlibFactory` class selection.
- Retry policy tests for try-once, suppress-void, retry forever with bounded harness, fixed/max/proportional/exponential sleep decisions, exception-specific maps, remote-exception maps, overloaded method names, and retry count increments.
- Serialization tests for configured `SerializationFactory` ordering, Writable serialization reuse, Java serialization compatibility, serializer/deserializer open-close lifecycle, and deserializer object reuse.
- Comparator tests for `DeserializerComparator` and `JavaSerializationComparator`, including invalid bytes and non-comparable Java-serialized objects.
- IPC client/server integration tests for single calls, parallel calls with timeout/error nulls, ping interval configuration, client stop behavior, server start/stop/join, listener address, socket bind errors, send buffer size, and per-call remote address context.
- RPC tests for proxy creation, wait-for-proxy retry, stopProxy resource cleanup, protocol version success and `VersionMismatch`, remote exception wrapping/unwrapping, server method dispatch, and parallel RPC calls.
- RPC metrics/JMX tests for queue and processing time updates, per-method metrics, interval sampling, min/max reset, open connection count, call queue length, and shutdown cleanup.
- LogLevel tests for command-line parsing and servlet GET behavior, with separate deployment tests for access controls.
- `ClusterStatus` Writable round trips and getter correctness for task trackers, running tasks, max capacities, and JobTracker state.
- `Counters` tests for group/counter lazy creation, enum and string lookup, increments, sum/incrAllCounters, iteration, serialization, compact string rendering, logging, and display-name stability.
- `DefaultJobHistoryParser` tests on representative job history files with tasks, attempts, counters, failures, and malformed records.
- `FileInputFormat` tests for input path setters/adders, glob expansion, filters, empty input, directories, invalid paths, splitability, min split size, split size computation, block index lookup, and deprecated `validateInput` behavior.
- `FileOutputFormat` tests for output path/work path/task path derivation, existing output rejection, compression flag/codec class configuration, and record writer integration.
- `FileSplit` tests for path/start/length/location serialization, zero-length splits, null/empty host arrays, and string rendering.
- `ID` tests for numeric comparison, read/write, `forName` parsing, malformed/null strings, equality/hash, and subclass compatibility.
- `InputFormat` and `InputSplit` contract tests ensuring split length/location data is honored by scheduling and record readers preserve record boundaries.
- Exception tests for message constructors, accumulated `InvalidInputException` messages, uncopied problem list behavior, and invalid job configuration surfacing.
- `IsolationRunner` tests with an isolated task directory fixture, missing arguments, missing files, and task failure propagation.
- `JobClient` integration tests for initialization/close, filesystem staging, submit by file and `JobConf`, `runJob` polling, job lookup, task reports by `JobID` and deprecated string IDs, cluster status, jobs-to-complete/all-jobs queries, task output filter config, default map/reduce capacity queries, system directory lookup, and cleanup after partial submission failure.

### subset-b-007283: lines 18636-24770

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml lines 18636-24770

## Scope

This chunk is a generated JDiff API snapshot for the Hadoop 0.18.3 `org.apache.hadoop.mapred` package, not implementation source. It starts in the tail of the `JobClient` class documentation, immediately before the `JobClient.TaskStatusFilter` enum, and ends after the complete `TaskID` API entry just before `TaskLog`. The XML records public API compatibility metadata: class/interface names, inheritance, implemented interfaces, constructors, methods, parameter and return types, declared exceptions, fields, visibility, synchronized/static/final/abstract flags, deprecation text, and embedded Javadoc contracts.

The represented surface is the old MapReduce API layer: job configuration and submission, job history/event/status records, JobTracker RPC-facing methods, mapper/reducer contracts, record input/output contracts, SequenceFile input/output formats, web status server helpers, and immutable job/task identifier Writables. Because this is a line-bounded chunk, the beginning of `JobClient` is outside this range and `TaskLog` begins in the next range, but the classes and interfaces listed below are complete unless explicitly noted.

## Purpose and major API surface

The opening `JobClient` documentation defines the client-side job submission workflow. A caller builds a `JobConf`, sets input/output paths, mapper/reducer classes, and then uses `JobClient.runJob(JobConf)` or `submitJob(JobConf)` to copy the job jar and configuration into the MapReduce system directory, submit work to the `JobTracker`, and optionally monitor completion. The docs also identify chained-job control patterns: synchronous `runJob`, asynchronous `submitJob` plus `RunningJob` polling, and completion notification through `JobConf.setJobEndNotificationURI`.

`JobClient.TaskStatusFilter` is an enum exposed through standard `values()` and `valueOf(String)` methods. The actual enum constants are not expanded in this JDiff fragment, but the type belongs to task-status display/filtering in the `JobClient` command and monitoring path.

`JobConf` is the central configuration object and extends `org.apache.hadoop.conf.Configuration`. It supplies constructors from an empty configuration, an example class whose jar should become the job jar, another `Configuration`, a `(Configuration, Class)` pair, a configuration XML filename, or a `Path`. Its methods configure jar localization (`getJar`, `setJar`, `setJarByClass`), JobTracker/system/local directories (`getSystemDir` deprecated in favor of `JobClient`, `getLocalDirs`, `deleteLocalFiles`, `getLocalPath`, `getJobLocalDir`), job identity (`getUser`, `setUser`, `getJobName`, `setJobName`, `getSessionId`, `setSessionId`, `setJobPriority`, `getJobPriority`), working directory, and completion callbacks (`getJobEndNotificationURI`, `setJobEndNotificationURI`).

`JobConf` also owns the old mapred execution contract. It configures input and output paths, with direct `setInputPath`, `addInputPath`, `getInputPaths`, `getOutputPath`, and `setOutputPath` now deprecated in favor of `FileInputFormat` and `FileOutputFormat`. It selects `InputFormat`, `OutputFormat`, mapper, map runner, partitioner, reducer, combiner, output key/value classes, map-output key/value classes, output key comparator, and output value grouping comparator. It controls map-output compression, map-output codec, deprecated map-output `SequenceFile.CompressionType`, speculative execution globally and separately for maps/reduces, desired map/reduce task counts, max attempts, failed-task retention and regex retention, failure thresholds per tracker and by percent, profiling settings and task ranges, and map/reduce debug scripts.

`JobConfigurable` is a simple interface for components initialized from a `JobConf` through `configure(JobConf)`. It is implemented by many of the mapred plug-in contracts in this chunk, including mapper/reducer/partitioner-related APIs and input/output formats.

`JobEndNotifier` exposes static lifecycle and delivery hooks for job-end callbacks: `startNotifier`, `stopNotifier`, `registerNotification(JobConf, JobStatus)`, and `localRunnerNotification(JobConf, JobStatus)`. It connects the `JobConf` notification URI setting with both cluster and local-runner completion paths.

`JobHistory` and nested types describe append-mode history logging and parsing. Top-level APIs initialize history files (`init(JobConf, hostname)`), parse a history file from a `FileSystem` while invoking a listener per line (`parseHistoryFromFS`), and globally enable or disable history logging. `JobHistory.Listener` is the callback interface receiving a `RecordTypes` value and a map keyed by `JobHistory.Keys`. `HistoryCleaner` is a `Runnable` that deletes history older than one month and prunes old master-index entries.

`JobHistory.JobInfo`, `Task`, `TaskAttempt`, `MapAttempt`, and `ReduceAttempt` are helper records for logging or reading job, task, and attempt lifecycle events. They include `logSubmitted`, `logStarted`, `logFinished`, `logFailed`, and `logKilled` variants, with both older string IDs and newer typed `JobID`, `TaskID`, and `TaskAttemptID` overloads. `JobInfo` also exposes job-history filename/path URL encoding/decoding helpers and local job-conf file paths. `Keys`, `RecordTypes`, and `Values` are enums defining global history key names, line record types, and commonly used string values.

`JobID`, `TaskID`, and `TaskAttemptID` are immutable identifier classes extending the mapred `ID` base. Each provides typed constructors, parsing through `forName(String)`, static `read(DataInput)`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, `toString`, and regex pattern builders (`getJobIDsPattern`, `getTaskIDsPattern`, `getTaskAttemptIDsPattern`). `JobID` identifies a job by JobTracker identifier plus job number; `TaskID` adds map/reduce kind and task number; `TaskAttemptID` adds the attempt number. Their docs explicitly warn applications not to parse ID strings directly.

`JobPriority` is an enum for job scheduling priority. `JobProfile` is a `Writable` carrying user, `JobID`, job configuration file, web UI URL, and job name; older string-ID constructors/getters are deprecated. `JobStatus` is a `Writable` carrying `JobID`, map progress, reduce progress, run state, start time, and username. It exposes integer state constants `RUNNING`, `SUCCEEDED`, `FAILED`, and `PREP`; its progress/state getters and setter are synchronized.

`JobShell` is a `Configured` `Tool` for command-line job submission, including support for distributed cache-style `-libjars`, `-archives`, and `-files` arguments before the input jar and application args.

`JobTracker` is the central cluster-side job submission and tracking class. It implements `MRConstants`, `InterTrackerProtocol`, and `JobSubmissionProtocol`. The public API covers tracker startup/shutdown, protocol versioning, address discovery, service loop, tracker identity/ports/start time, build version, job and task-tracker collections, network-topology helpers, heartbeat handling, filesystem/system directory queries, task-tracker error reporting, new job ID allocation, job submission, cluster status, job kill, profile/status/counter/report/event/diagnostic retrieval, task lookup and kill, assigned tracker lookup, all-jobs snapshots, local job-conf path helpers, and a debugging `main`. `JobTracker.IllegalStateException` reports submissions attempted before the tracker is ready. `JobTracker.State` is an enum for tracker state.

Input-side text APIs include `LineRecordReader`, `LineRecordReader.LineReader`, `KeyValueLineRecordReader`, and `KeyValueTextInputFormat`. `LineRecordReader` implements `RecordReader<LongWritable,Text>` over `FileSplit` or generic streams and returns byte-offset keys with line-text values. `LineReader` reads lines from an input stream with configurable maximum line lengths. `KeyValueLineRecordReader` implements `RecordReader<Text,Text>`, finds a separator in each line, and returns key/value `Text` pairs. `KeyValueTextInputFormat` configures separator behavior, marks files as splittable or not, and creates key/value line readers.

Output-side and map/reduce contracts are the core user extension points. `Mapper` maps one input key/value pair to zero or more intermediate pairs using `OutputCollector` and `Reporter`, and is also `JobConfigurable` and `Closeable`. `Reducer` reduces grouped intermediate values for a key to zero or more final outputs, documents shuffle/sort/reduce phases, secondary sort via output-key and grouping comparators, and object-reuse warnings for keys/values. `MapReduceBase` supplies no-op `configure` and `close` defaults. `MapRunnable` gives advanced control over the full map loop, and `MapRunner` is the default implementation that reads from `RecordReader` and invokes a configured `Mapper`.

`OutputCollector` collects key/value pairs from mappers or reducers. `OutputFormat` validates job output specs and creates `RecordWriter`s. `OutputFormatBase` is a deprecated base class superseded by `FileOutputFormat`, but still provides static output-compression helpers and an output spec check that can throw `FileAlreadyExistsException` or `InvalidJobConfException`. `OutputLogFilter` is a `PathFilter` that excludes `_logs` paths when listing output directories. `RecordReader` creates reusable key/value objects, reads the next pair, reports position/progress, and closes. `RecordWriter` writes output key/value pairs and closes with a `Reporter`. `Partitioner` maps intermediate keys to reducer partitions and is configured by `JobConf`.

`Reporter` extends `Progressable` and lets tasks set status, increment counters by enum or group/counter name, fetch the current map `InputSplit`, and use `Reporter.NULL` as a no-op implementation. `RunningJob` is the client-facing handle returned by job submission. It exposes job ID/name/file/tracking URL, map/reduce progress, completion and success checks, blocking completion wait, job kill, task completion event pagination, task-attempt kill with typed or deprecated string IDs, and counter retrieval.

`MultiFileInputFormat` and `MultiFileSplit` support grouping multiple files into one split. `MultiFileInputFormat` creates `InputSplit[]` and abstract record readers over `MultiFileSplit`. `MultiFileSplit` implements `InputSplit`, stores arrays of `Path` and per-file lengths, reports total length, per-path length, path count, paths, locations, string form, and serializes with `readFields`/`write`.

`MapFileOutputFormat` writes Hadoop `MapFile`s and supplies static helpers to open generated map-file readers and retrieve an entry by using a partitioner to select the right reader. It integrates `WritableComparable` keys and `Writable` values with the output-format contract.

The SequenceFile APIs cover binary, text, filtered, and regular SequenceFile input/output. `SequenceFileInputFormat` lists paths and creates `SequenceFileRecordReader`. `SequenceFileRecordReader` implements `RecordReader<K,V>`, exposes key/value classes, current value access, positional seek, progress, and close. `SequenceFileOutputFormat` creates `RecordWriter`s, opens readers for output directories, and gets/sets output `SequenceFile.CompressionType`. `SequenceFileAsBinaryInputFormat` and nested `SequenceFileAsBinaryRecordReader` expose raw key and value bytes as `BytesWritable` and report the underlying key/value class names. `SequenceFileAsBinaryOutputFormat` writes binary key/value bytes while configured with actual SequenceFile output key/value classes; nested `WritableValueBytes` adapts `BytesWritable` to `SequenceFile.ValueBytes`. `SequenceFileAsTextInputFormat` and `SequenceFileAsTextRecordReader` present SequenceFile keys/values as `Text`. `SequenceFileInputFilter` wraps SequenceFile reading with a configured `Filter`; built-in filters include configurable base behavior, MD5-based frequency filtering, percent-frequency filtering, and regex key filtering.

`StatusHttpServer` wraps a web server used by mapred status pages. It can set/get servlet attributes, add servlets, expose the bound port, configure threads, add an SSL listener, start, and stop. `StatusHttpServer.StackServlet` emits stack information through `doGet`. `StatusHttpServer.TaskGraphServlet` emits a task graph through `doGet` and exposes dimensions/margins as fields.

`TaskCompletionEvent` is a `Writable` record for JobTracker task-completion tracking. It carries an event ID, `TaskAttemptID`, runtime, map/reduce flag, status enum, and task-tracker HTTP location. It provides deprecated string task-ID accessors alongside typed accessors, setters, `toString`, `isMapTask`, `idWithinJob`, `write`, `readFields`, and `EMPTY_ARRAY`. `TaskCompletionEvent.Status` is an enum for event status values.

## Control flow and behavioral contracts

The XML has no executable bodies, but the Javadocs define runtime flows. Job submission begins with a `JobConf`, optionally infers or sets a user jar, localizes job resources and configuration to the system directory, asks `JobTracker.getNewJobId()` for a typed identifier, and calls `submitJob`. `JobTracker.submitJob(JobID)` creates a `JobInProgress`, couples `JobProfile` and `JobStatus`, and enqueues the job for asynchronous initialization that computes splits and task-tracker/block mappings. Clients then observe through `RunningJob` or `JobClient.runJob`, and may page task completion events, inspect counters/reports/diagnostics, or kill jobs/tasks.

Job configuration flow is reflective and plug-in based. `JobConf` stores classes for `InputFormat`, `OutputFormat`, `Mapper`, `MapRunnable`, `Partitioner`, `Reducer`, and optional combiner. At execution time, mapred instantiates those classes, calls `configure(JobConf)` for `JobConfigurable` components, uses `InputFormat` to compute splits and `RecordReader`s, uses `MapRunnable`/`Mapper` to produce intermediate pairs, partitions and sorts by configured comparators, invokes `Reducer` on grouped values, and writes through `OutputFormat`/`RecordWriter`. For zero-reducer jobs, mapper output is written directly to the filesystem rather than grouped for reduce.

Mapper and reducer tasks have explicit liveness obligations. Long-running map or reduce methods are expected to call `Reporter.progress()` or set status/counters often enough to avoid task timeout. The reducer contract documents that keys and values may be reused by the framework, so applications that keep them must clone the objects. The reducer docs also define the shuffle, sort, and reduce phases and the secondary-sort pattern: partition by a coarse key, sort by a richer key, and group by a comparator that ignores the secondary fields.

Record I/O flow is split-oriented. `InputFormat` creates `InputSplit`s; `RecordReader.next(K,V)` fills caller-supplied reusable key/value instances until EOF; `getPos` and `getProgress` expose read position; `close` releases input resources. Writers receive a unique part name and `Progressable`, write key/value pairs, then close with a reporter. `OutputFormat.checkOutputSpecs` is invoked at submission time to fail early on invalid or unsafe output locations, especially pre-existing output directories.

Job history flow is append-only text logging. `JobHistory.init` prepares tracker history files, lifecycle methods append typed records, and `parseHistoryFromFS` streams a file line-by-line through a `Listener` without building the whole history object in memory. `JobInfo.logSubmitted` creates the per-job file and may disable later history logging if creation fails. Finish/failure methods close the job history file, while `HistoryCleaner` prunes month-old data and master-index entries.

JobTracker control flow is RPC/state-machine oriented. TaskTrackers repeatedly call `heartbeat`, passing status, initial-contact state, task-acceptance state, and response ID. The JobTracker updates task-tracker/job state and returns `HeartbeatResponse` instructions to launch/stop tasks/jobs or reset during contingencies. Several `JobTracker` query/mutation methods are synchronized, including typed job status/counters/reports/event retrieval, job submission, job/task kill, and heartbeat, indicating shared mutable scheduler state.

SequenceFile flow depends on selected representation. Regular SequenceFile readers deserialize typed keys/values. Binary readers expose serialized key/value bytes and class names without deserializing into the original types. Text readers convert keys/values to `Text`. Filtered readers call the configured `Filter.accept(Object key)` before exposing records; MD5 and percent filters sample by frequency, while regex filters match key text.

Identifier parsing and serialization flow is stable and layered. `JobID` serializes the JobTracker identifier plus numeric job ID. `TaskID` serializes its `JobID`, map/reduce flag, and task number. `TaskAttemptID` serializes its `TaskID` plus attempt number. `forName` helpers parse canonical strings and throw `IllegalArgumentException` for malformed strings; regex builders create patterns with nullable components for wildcard matching.

## State, persistence, and side effects

The JDiff XML itself is persistent compatibility metadata. Runtime persistence described by this chunk includes configuration XML files, localized user jars, localized job-conf files, distributed filesystem input/output paths, intermediate map outputs stored as SequenceFiles, final output files, MapFiles, SequenceFiles, job history logs, task completion events, counters, status records, web UI attributes, and serialized ID/status/profile/event Writables.

`JobConf` is mutable configuration state. It stores class names, paths, booleans, numeric thresholds, compression settings, profiling/debug scripts, user/session/job names, and callback URIs in the inherited `Configuration` key/value store. Constructors from XML files and `Path`s make `JobConf` a persistence boundary, and job submission copies the effective configuration into the MapReduce system directory for cluster execution.

`JobTracker` is the major in-memory state owner. Its public API exposes running, failed, and completed job collections; task-tracker status collections; network topology cache/lookup state; total submissions; tracker identity and ports; job initialization queue behavior; task reports, counters, diagnostics, completion events, and assigned trackers. Synchronized methods and timer-thread comments show concurrency-sensitive mutable state behind the API.

`JobHistory` is durable append-mode audit state. It maintains a master index and per-job text history files using key/value records. Per-job history filenames combine tracker and job IDs, and helper methods URL encode/decode file paths/names for web UI and filesystem use. Cleaner side effects delete old files and prune old index records.

Task execution side effects include counter increments, status strings, progress pings, task debug-script execution, retention of failed-task temporary files when configured, local-file deletion through `JobConf.deleteLocalFiles`, and job-end HTTP notifications. `Reporter.NULL` provides a side-effect-free substitute for contexts that do not need reporting.

Input and output formats mediate filesystem side effects. `OutputFormat.checkOutputSpecs` protects output paths; `RecordWriter` writes final data; `MapFileOutputFormat` writes map-file directories; `SequenceFileOutputFormat` writes SequenceFiles with configured compression; `OutputLogFilter` prevents log directories from being treated as user output. `MultiFileSplit` and ID/event/status/profile classes persist over `DataInput`/`DataOutput`.

`StatusHttpServer` owns servlet registration, attributes, port binding, threads, optional SSL listener, and lifecycle. The stack and task-graph servlets expose process/task state over HTTP, so they are both observability and network side-effect points.

## Dependencies and integration points

This chunk sits at the center of the Hadoop 0.18.3 mapred stack. It depends on `org.apache.hadoop.conf.Configuration` and `Configured`, `org.apache.hadoop.fs.Path`, `FileSystem`, `FileSplit`, `InputSplit`, and `PathFilter`, Hadoop I/O primitives such as `Writable`, `WritableComparable`, `WritableComparator`, `RawComparator`, `Text`, `LongWritable`, `BytesWritable`, `SequenceFile`, `MapFile`, and compression codecs, plus Java `DataInput`, `DataOutput`, `IOException`, `URL`, collections, iterators, input streams, and servlet APIs.

Cluster integration points include `InterTrackerProtocol`, `JobSubmissionProtocol`, `HeartbeatResponse`, `TaskTrackerStatus`, `TaskTracker`, `TaskInProgress`, `JobInProgress`, `ClusterStatus`, `TaskReport`, `Counters`, `MRConstants`, network topology `Node`, and the JobTracker web UI. Several APIs preserve compatibility by offering both typed ID overloads and deprecated string-ID overloads.

User-code integration is through `Mapper`, `Reducer`, `Partitioner`, `InputFormat`, `OutputFormat`, `RecordReader`, `RecordWriter`, `OutputCollector`, `Reporter`, `MapRunnable`, `MapReduceBase`, and `JobConfigurable`. These are the extension points that application jars provide and that `JobConf` references reflectively.

Storage integration includes distributed filesystem paths, local job/task directories, job history files, job configuration XML, SequenceFiles, MapFiles, output directories, and task log filtering. Notification integration uses the job-end notification URI, and distributed command-line packaging is surfaced through `JobShell`.

## Risks and compatibility notes

This is an old public API snapshot, so compatibility risk is dominated by signature and behavior drift. `JobConf` contains many deprecated convenience methods that applications may still call; removing or changing them would break legacy mapred jobs even when replacement APIs exist. The typed `JobID`/`TaskID`/`TaskAttemptID` migration also leaves deprecated string overloads that must keep accepting legacy IDs.

Configuration keys and class-selection behavior are highly compatibility-sensitive. Defaults for input/output formats, compression flags/codecs, map-output and final-output classes, comparators, speculative execution, task counts, retry/failure thresholds, profiling ranges, debug scripts, and notification URIs affect job semantics and cluster behavior. Silent default changes can alter correctness, performance, or failure handling.

JobTracker APIs expose shared mutable scheduler state. The synchronized markers on heartbeat, typed submission, job/task kill, and query methods are test signals for races around job initialization, task tracker heartbeats, completion-event pagination, diagnostic lookup, and kill/fail transitions. The `submitJob` docs explicitly mention asynchronous initialization, so clients must handle status visibility before split computation completes.

Mapper/reducer object reuse and liveness rules are common application bug sources. User code that retains mutable key/value instances without cloning can observe corrupted data. User code that spends too long without reporting progress can be killed as timed out. Reducer secondary-sort behavior depends on correct alignment among partitioner, output-key comparator, and grouping comparator.

History logging has durability and partial-failure risks. If per-job history creation fails, logging can be disabled for later events. Append-mode text logs, URL-encoded filenames, master-index cleanup, and month-old deletion all need stable parsing and careful failure handling. Counters and task attempts must be recorded consistently across success, failure, and killed states.

Filesystem output APIs must avoid data loss. `checkOutputSpecs` is expected to reject already-existing output, and log filtering must not accidentally include `_logs` as data. Compression settings and SequenceFile key/value class settings must match reader expectations. Binary SequenceFile formats expose raw bytes and class names, so mismatches in configured output key/value classes can create unreadable files.

Identifier string formats are externally visible. Canonical `job_...`, `task_...`, and `attempt_...` forms appear in logs, paths, web UI, diagnostics, patterns, and user scripts. Changes to zero-padding, map/reduce markers, wildcard regex builders, parser strictness, or comparison ordering would break downstream tooling.

`StatusHttpServer` and notification APIs expose network-facing behavior. Servlet attribute names, bound port updates, SSL listener configuration, stack traces, task graph rendering dimensions, and job-end callback semantics can affect operations and security posture.

## Test signals

JDiff-level validation should verify the XML remains well-formed across this range and preserves class/interface boundaries, implemented interfaces, constructors, method signatures, parameter types, thrown exceptions, field constants, deprecation text, visibility, static/final/abstract/synchronized flags, and embedded Javadocs for all listed mapred APIs.

`JobConf` tests should cover constructor inheritance from `Configuration` and XML/`Path` inputs, jar inference by class, local path selection and cleanup, input/output path deprecated wrappers versus `FileInputFormat`/`FileOutputFormat`, class setters/getters for formats and map/reduce components, map-output and final-output key/value classes, comparator and grouping comparator settings, compression settings, speculative execution toggles, task-count and retry/failure limits, priority, profiling ranges, debug scripts, failed-task-file retention, notification URI, and job-local directory lookup.

Submission and tracking tests should cover `JobClient` synchronous and asynchronous flows, job-end notifications, `RunningJob` progress/completion/success/counter/event APIs, typed and deprecated string task kill paths, and `JobShell` argument parsing for jars/files/archives.

JobTracker tests should exercise startup with port zero and configuration mutation, address discovery, protocol version handling, heartbeat initial-contact and reset flows, new job ID allocation, asynchronous job initialization, cluster status, running/failed/completed/all job snapshots, task tracker registration/error reporting, network topology helper methods, job/task kill behavior, profile/status/counter/report/event/diagnostic queries, assigned tracker lookup, local job file path helpers, and ready-state submission rejection through `IllegalStateException`.

Job history tests should cover initialization success/failure, global disable toggles, per-job file creation, submitted/started/finished/failed events, task and map/reduce attempt started/finished/failed/killed events, counters in finish records, listener-based parse streaming, URL encode/decode of history filenames and paths, local job file paths, and cleaner pruning of one-month-old files and master-index entries.

Map/reduce contract tests should cover `MapReduceBase` no-op lifecycle, `Mapper` and `Reducer` configure/map/reduce/close ordering, `MapRunner` looping through `RecordReader`, `MapRunnable` customization, reporter progress/status/counter calls, `Reporter.NULL`, input split access only in mapper context, partitioner bounds for reducer counts, secondary-sort comparator combinations, combiner configuration, zero-reducer direct output, and key/value object reuse expectations.

Record I/O and format tests should cover `LineRecordReader` offsets, max line length, split boundary behavior, `KeyValueLineRecordReader` separator parsing, `KeyValueTextInputFormat` configuration and splittability, `MultiFileSplit` length/path/location serialization, `MultiFileInputFormat` split creation, `OutputFormat.checkOutputSpecs` rejection of existing or invalid output, `RecordWriter` close semantics, `OutputLogFilter` exclusion of `_logs`, and `MapFileOutputFormat` reader/entry helper behavior.

SequenceFile tests should cover regular typed reading/writing, output compression type get/set, reader seek/progress/current-value behavior, binary input preserving serialized key/value bytes and class names, binary output configured key/value class checks and `WritableValueBytes`, text conversion readers, filtered input with configured filter class, MD5/percent frequency behavior, regex key matching, and interactions with map-output compression settings.

Writable ID/status/event tests should cover binary round trips for `JobID`, `TaskID`, `TaskAttemptID`, `JobProfile`, `JobStatus`, and `TaskCompletionEvent`; canonical string parsing and malformed inputs; regex pattern builders with null wildcard components; equality/hash/compare ordering; deprecated string ID accessors; synchronized `JobStatus` progress/state reads; task completion event status/runtime/http fields; and `EMPTY_ARRAY`.

HTTP/status tests should cover servlet attribute storage, servlet registration, port reporting after start, thread configuration, SSL listener setup, start/stop idempotence or failure behavior, stack servlet output, and task graph servlet rendering dimensions.

### subset-b-007284: lines 24771-30886

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml lines 24771-30886

## Scope

This chunk is part 5 of the generated JDiff public API snapshot for Hadoop 0.18.3. It is compatibility metadata, not executable Java source. The XML records package boundaries, class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, checked exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation text, and embedded Javadoc contracts.

The chunk starts inside the tail Javadoc for `org.apache.hadoop.mapred.TaskID`, then covers a large public API segment from MapReduce task logging and task-tracker APIs through `org.apache.hadoop.mapred.jobcontrol`, `org.apache.hadoop.mapred.join`, `org.apache.hadoop.mapred.lib`, `org.apache.hadoop.mapred.lib.aggregate`, `org.apache.hadoop.mapred.pipes`, and the beginning of Hadoop's metrics SPI. It ends inside `org.apache.hadoop.metrics.spi.MetricsRecordImpl`; the rest of that class is in the next chunk.

## Purpose and Major API Surface

The opening MapReduce section exposes task-side runtime APIs. `TaskLog` locates user-log files by string or `TaskAttemptID`, purges old logs, reads task log length from `JobConf`, and wraps child commands to capture stdout, stderr, and debug output. `TaskLog.LogName` is the user-log selector enum. `TaskLogAppender` is a log4j `FileAppender` for task child logs, with task-id and total-log-size log4j properties. `TaskLogServlet` serves task logs over HTTP from TaskTrackers.

`TaskReport` is a `Writable` task-status snapshot with task id, progress, state string, diagnostics, counters, start time, finish time, and `write`/`readFields` serialization. It preserves the deprecated string `getTaskId()` alongside `getTaskID()`.

`TaskTracker` is the central worker daemon API. It implements `MRConstants`, `TaskUmbilicalProtocol`, and `Runnable`, is constructed from `JobConf`, and exposes lifecycle (`run`, `shutdown`, `close`, `cleanupStorage`, `main`), JobTracker linkage (`getJobClient`, `getProtocolVersion`), child task lookup (`getTask` by string or `TaskAttemptID`), task heartbeat/status/reporting methods (`statusUpdate`, `reportDiagnosticInfo`, `ping`, `done`, `shuffleError`, `fsError`, `mapOutputLost`), map-completion lookup, idle state, bound report address, and metrics access. Nested classes include `TaskTracker.Child` for child-process entry, `MapOutputServlet` for serving intermediate map outputs to reducers, and `TaskTrackerMetrics` as a metrics `Updater`.

`TextInputFormat` and `TextOutputFormat` provide standard line-oriented MapReduce I/O. `TextInputFormat` is a `FileInputFormat<LongWritable,Text>` and `JobConfigurable`, with splitability and record-reader creation. `TextOutputFormat` creates `RecordWriter<K,V>` instances, and `TextOutputFormat.LineRecordWriter` writes key/value text lines to a `DataOutputStream`.

The `org.apache.hadoop.mapred.jobcontrol` package models dependent job DAGs. `Job` wraps `JobConf`, job name, internal string id, assigned `JobID`, state, message, dependencies, readiness/completion checks, and `submit()`. It retains deprecated string MapReduce job-id access while adding `JobID`-typed access. `JobControl` is a `Runnable` controller with waiting, ready, running, successful, and failed job lists; it adds single or multiple jobs, reports state, can stop/suspend/resume, checks `allFinished`, and drives the state machine in `run()`.

The `org.apache.hadoop.mapred.join` package exposes the old mapred composite-input join framework. `ComposableInputFormat` returns `ComposableRecordReader` instances. `ComposableRecordReader` combines `RecordReader` and `Comparable`, exposing reader id, current key, key-copying, `hasNext`, `skip`, and `accept` for join coordination. `CompositeInputFormat` parses join expressions, sets input format strings in `JobConf`, validates input, computes composite splits, creates composite readers, and offers static `compose` helpers. `CompositeInputSplit` aggregates child `InputSplit`s and serializes/deserializes them as one split.

`CompositeRecordReader` is the base join coordinator. It is configurable, holds child readers in a priority queue, uses a `WritableComparator`, adds child readers, computes current keys, skips keys, fills join collectors, accepts values into `ResetableIterator`s, compares readers, creates keys/internal tuple values, exposes position/progress, and closes resources. `JoinRecordReader`, `InnerJoinRecordReader`, and `OuterJoinRecordReader` implement tuple-producing joins. `MultiFilterRecordReader` and `OverrideRecordReader` implement filtered and rightmost-source preference behavior. `ArrayListBackedIterator`, `StreamBackedIterator`, `JoinDelegationIterator`, `MultiFilterDelegationIterator`, `ResetableIterator`, and `ResetableIterator.EMPTY` define replayable stateful iteration over writable values. `TupleWritable` is the joined tuple value with bitset-style presence tracking, size, get, iterator, `has`, `write`, `readFields`, and `toString`.

`Parser` and its nested token/node classes parse join expressions. The docs describe a simple stateless shift-reduce parser whose function-call grammar maps identifiers to parser node types and `ComposableRecordReader` constructors through `Parser.Node.addIdentifier`. Token classes model string, numeric, node, and enum token types; invalid token access can throw `IOException`.

The `org.apache.hadoop.mapred.lib` package exposes reusable mapper/reducer/input/output utilities. `FieldSelectionMapReduce` is both `Mapper` and `Reducer`, selecting output fields from input records. `HashPartitioner` partitions by key hash. `IdentityMapper`, `IdentityReducer`, `InverseMapper`, `LongSumReducer`, `RegexMapper`, and `TokenCountMapper` are standard small map/reduce components. `KeyFieldBasedPartitioner` partitions by key fields and exposes option parsing/configuration helpers. `MultipleOutputFormat` is an abstract output format that derives output filenames, actual keys, and actual values from each record; concrete `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` create sequence-file or text base writers. `MultithreadedMapRunner` runs mapper calls through a configurable thread pool and requires thread-safe mapper implementations. `NLineInputFormat` makes input splits containing N lines for parameter-sweep workloads. `NullOutputFormat` discards all outputs.

The `org.apache.hadoop.mapred.lib.aggregate` package provides the Aggregate framework. Primitive aggregators include `DoubleValueSum`, `LongValueMax`, `LongValueMin`, `LongValueSum`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram`. They implement `ValueAggregator`, accept object/string or primitive values as appropriate, reset state, emit report strings, and produce combiner/reducer output records. `ValueAggregatorDescriptor` generates aggregation id/value pairs from input key/value records and has public `TYPE_SEPARATOR` and `ONE` constants. `ValueAggregatorBaseDescriptor` provides common descriptor behavior, `generateEntry`, aggregator creation by type, default key/value-pair generation, and `JobConf` configuration. `UserDefinedValueAggregatorDescriptor` reflectively instantiates user plugin descriptors. `ValueAggregatorJob` builds and runs aggregate jobs, including overloads accepting descriptor classes and a `setAggregatorDescriptors` helper. `ValueAggregatorJobBase`, `ValueAggregatorMapper`, `ValueAggregatorCombiner`, and `ValueAggregatorReducer` implement the generic mapper/combiner/reducer flow around descriptor lists and type-driven aggregation.

`org.apache.hadoop.mapred.pipes.Submitter` is the public submitter for Hadoop Pipes jobs. It stores and reads the C++ executable URI, toggles whether record reader, mapper, reducer, and record writer are Java-side, controls whether the downlink command file is kept for debugging, modifies a `JobConf` for pipes execution during `submitJob`, and exposes a command-line `main`.

The metrics section defines Hadoop's original metrics API and SPI. `ContextFactory` is a singleton factory backed by attributes loaded from `hadoop-metrics.properties`; it creates named `MetricsContext` implementations by `<context>.class` or returns no-op null contexts. `MetricsContext` defines monitoring lifecycle, record creation, updater registration, and `DEFAULT_PERIOD`. `MetricsException` is a runtime exception. `MetricsRecord` offers typed tag setters, tag removal, typed metric setters and incrementers, plus `update` and `remove`. `MetricsUtil` wraps context and record creation. `Updater` is the callback interface.

Metrics implementations in this chunk include `metrics.file.FileContext`, `metrics.ganglia.GangliaContext`, `metrics.jvm.EventCounter`, `metrics.jvm.JvmMetrics`, and `metrics.spi.AbstractMetricsContext`. `FileContext` emits metrics records to a file or stream and flushes. `GangliaContext` emits metrics to Ganglia. `EventCounter` is a log4j appender that counts fatal/error/warn/info events. `JvmMetrics` registers as an updater for JVM process/session metrics. `AbstractMetricsContext` implements the common metrics table, period timer, monitoring lifecycle, updater registration, record creation, record update/remove buffering, attribute lookup, and abstract `emitRecord`. `MetricsRecordImpl` begins here as the concrete `MetricsRecord` implementation that delegates `update()` and `remove()` to its owning `AbstractMetricsContext`.

## Control Flow and Behavioral Contracts

Task execution flow is reflected by `TaskTracker` and `TaskLog`. A TaskTracker starts with a `JobConf`, cleans local storage on startup, enters a retrying `run()` loop to connect to the JobTracker, serves child tasks through `getTask`, receives task status through the `TaskUmbilicalProtocol` methods, and reports task completion or failure signals. Child JVMs interact through `TaskTracker.Child`, log output through `TaskLog` wrappers and `TaskLogAppender`, and expose logs through `TaskLogServlet`.

Map output fetch flow uses `TaskTracker.MapOutputServlet` and `getMapCompletionEvents`: reducers query completion events, then request map outputs over HTTP. `shuffleError`, `mapOutputLost`, and `fsError` are explicit feedback channels from tasks to the TaskTracker when local output or filesystem state becomes invalid.

Job-control flow is a state machine over dependent `Job` objects. `JobControl.run()` moves jobs from waiting to ready when dependencies complete, submits ready jobs, tracks running jobs through success/failure, and stops when instructed. `Job.isReady()` and `Job.isCompleted()` are the dependency gates.

Join flow starts with a composed expression string in `CompositeInputFormat`, parsed by `Parser` into node objects that know which `ComposableRecordReader` constructor to instantiate. Composite splits align child input splits. Composite readers coordinate child readers by comparable keys, collect per-key value streams in `ResetableIterator`s, and call `combine` in inner, outer, override, or custom reader subclasses to decide whether a tuple/value should be emitted.

Mapred library flow is mostly adapter based. Utility mappers and reducers transform input records into output records through the standard `map` and `reduce` callbacks. `MultipleOutputFormat` wraps a base writer selection flow: derive an output filename from key/value/input name, derive actual key/value, obtain or reuse the base writer, then write to separate named files. `MultithreadedMapRunner` parallelizes mapper calls over a thread pool, so mapper and collector interactions must be safe for concurrent use.

Aggregate flow is data driven. User or base descriptors convert each input record into one or more `Text` key/value pairs where the key encodes aggregation type and id. The mapper emits those pairs; the combiner and reducer inspect type prefixes, create the correct `ValueAggregator`, feed all values into it, and emit either combiner output or final report strings. `ValueAggregatorJob` assembles the `JobConf` and optional `JobControl` wrappers around this generic pipeline.

Pipes flow mutates a `JobConf` so Hadoop launches an external executable and decides which pipeline components are implemented in Java versus the pipes child process. When debugging is enabled, the command/downlink file is preserved and can be replayed by setting `hadoop.pipes.command.file`.

Metrics flow starts at `ContextFactory.getFactory()`, which reads classpath properties into attributes. `getContext(name)` constructs or reuses a context, defaulting to a null context if no implementation class is configured. Producers create `MetricsRecord`s, set tags and metrics, call `update` to buffer rows or `remove` to delete matching rows, while `Updater` callbacks run at the context period. `AbstractMetricsContext` periodically calls updaters, emits buffered records through subclass `emitRecord`, and then calls `flush`.

## State, Persistence, and Side Effects

The XML file itself is persisted API compatibility state. Runtime state described by the APIs includes TaskTracker local storage, running task maps, task status and diagnostics, user-log files, task counters, job dependency lists, join parser constructor maps, replayable join iterator buffers, tuple presence bits, multiple-output writer caches, aggregate descriptor lists, aggregator accumulators, pipes configuration flags, metrics factory attributes, metrics contexts, buffered metric rows, registered updaters, JVM/log event counters, and metrics output destinations.

External side effects include purging and writing task logs, serving logs and map outputs over HTTP, cleaning TaskTracker temporary storage, starting child JVMs and external pipes processes, mutating `JobConf` objects, reading/writing split and report data through Hadoop `Writable`, writing multiple output files, reading input files for line-based formats, writing metrics to files or network endpoints, loading metrics properties from the classpath, and reflectively instantiating user classes for join readers, aggregate descriptors, and metrics contexts.

Many APIs are mutable and not documented as thread-safe. Explicit synchronization appears on selected TaskTracker lifecycle/status methods, `TaskLog.cleanup`, metrics factory/context creation and monitoring methods, but job-control lists, aggregate objects, resettable iterators, parser registries, multiple-output writer state, and many metrics records are caller-managed mutable state.

## Dependencies and Integration Points

This chunk is deeply integrated with the old `org.apache.hadoop.mapred` API: `JobConf`, `JobID`, `TaskID`, `TaskAttemptID`, `Task`, `TaskStatus`, `TaskCompletionEvent`, `Counters`, `Reporter`, `RecordReader`, `RecordWriter`, `InputSplit`, `InputFormat`, `OutputFormat`, `OutputCollector`, `Mapper`, `Reducer`, `MapRunnable`, `RunningJob`, `JobClient`, and `InterTrackerProtocol`.

Filesystem and I/O dependencies include `FileSystem`, `Path`, `DataInput`, `DataOutput`, `DataOutputStream`, `File`, servlet request/response classes, log4j appenders/events, Java reflection, Java collections, `Writable`, `WritableComparable`, `WritableComparator`, `Text`, `LongWritable`, and `Progressable`.

Cluster integration points are the TaskTracker to JobTracker RPC protocols, TaskUmbilical child communication, HTTP map-output shuffle and task-log serving, JobControl orchestration, Pipes executable submission, and metrics sinks such as file and Ganglia. Configuration keys mentioned in docs include `mapred.map.multithreadedrunner.threads`, `num.of.trailing.legs.to.use`, and pipes command-file/debug settings.

The metrics SPI bridges public metrics records to concrete sinks. `ContextFactory` resolves implementation classes from `hadoop-metrics.properties`; `AbstractMetricsContext` is the common base for `FileContext`, `GangliaContext`, and null/no-op contexts in adjacent code.

## Risks and Compatibility Notes

Because this is a JDiff snapshot, signature shape is the main contract. Changing method overloads, parameter types, exception declarations, visibility, static/final/abstract/synchronized flags, deprecation text, or field constants can break source or binary compatibility even when implementation behavior is unchanged.

This chunk has boundary caveats: it begins after the `TaskID` class declaration and ends before `MetricsRecordImpl` closes. Adjacent chunks are needed for the complete `TaskID` and `MetricsRecordImpl` API records.

Several APIs preserve legacy string identifiers beside typed IDs. `TaskReport.getTaskId`, `TaskTracker` string overloads, and job-control string job IDs are deprecated or legacy but still part of the compatibility surface. Removing them would break old 0.18-era mapred applications.

TaskTracker APIs are operationally sensitive. Incorrect status, ping, completion, shuffle-error, or map-output-lost behavior can cause duplicate task attempts, lost diagnostics, stuck reducers, or stale local storage. Log capture wrappers also have shell quoting and output truncation risks because they build command lists around user commands.

Join APIs rely on sorted compatible keys, correct comparator classes, and replayable iterator semantics. `ResetableIterator.reset()` must be called after additions to avoid concurrent modification issues. Parser extension is fragile by its own docs: the shift-reduce parser has no states and treats parentheses as function calls, making grammar extensions risky.

`MultipleOutputFormat` can create many output files and depends on stable filename derivation. Bad key-derived paths, input-file-name derivation, or writer caching can create invalid paths, collisions, excess files, or leaked writers.

`MultithreadedMapRunner` is only safe for thread-safe mappers. Legacy mappers that mutate shared fields, reuse output objects unsafely, or assume single-threaded reporter/collector behavior may fail nondeterministically.

Aggregate APIs parse numbers and type prefixes from text. Bad input strings, overflow, malformed histogram values, descriptor class-loading failures, or mismatched combiner/reducer output formats can produce incorrect statistics or runtime failures. Some methods return raw `ArrayList`, `Set`, or `TreeMap`, so generic type tightening would be incompatible.

Pipes and metrics both invoke external or pluggable code. Pipes jobs depend on executable URIs and Java/native component flags being consistent. Metrics contexts depend on classpath property configuration and reflective construction; a bad `<context>.class` can throw checked reflection exceptions or silently fall back only when no class is configured.

## Test Signals

JDiff validation should verify this XML chunk remains well-formed with adjacent chunks, and that all package/class/interface records listed above preserve names, inheritance, implemented interfaces, constructors, methods, params, exceptions, fields, visibility, flags, and deprecation annotations.

Task runtime tests should cover `TaskLog` file lookup by string and `TaskAttemptID`, log retention cleanup, log-length configuration, stdout/stderr/debug command wrapping and quoting, `TaskLogAppender` close/size behavior, `TaskLogServlet` responses, `TaskReport` `Writable` round trips, and TaskTracker protocol flows for status, ping, done, diagnostics, shuffle errors, fs errors, map-output lost, map-completion queries, idle state, shutdown, and cleanup.

JobControl tests should build dependency DAGs with successful, failed, waiting, ready, running, suspended, resumed, and stopped jobs, checking state transitions, dependency readiness, ID assignment, and `allFinished()`.

Join tests should cover parser compose/parse round trips, custom identifier registration, split serialization, child split length/location aggregation, inner and outer joins, override joins preferring rightmost sources, tuple `has/get/iterator/write/readFields`, comparator ordering, skip behavior, reset/replay iterator order, stream-backed iterator cleanup, and malformed expression errors.

Mapred library tests should cover identity/inverse/token/regex/field-selection mappers and reducers, hash and key-field partitioning, multiple-output filename/key/value derivation, text and sequence multiple writers, null output behavior, N-line splitting for exact and trailing line counts, and multithreaded mapper execution with both safe and unsafe mapper examples.

Aggregate tests should cover each built-in aggregator's add/report/reset/combiner output behavior, numeric parsing failures, unique-count limits, histogram statistics and details, descriptor `generateEntry` and type mapping, user-defined descriptor reflection/configuration, mapper emission from descriptor lists, combiner aggregation, reducer final reports, and `ValueAggregatorJob` job-conf generation with generic Hadoop args.

Pipes tests should assert configuration round trips for executable URI, Java record reader/mapper/reducer/record writer booleans, keep-command-file behavior, `submitJob` mutations, and command-line submission failure reporting for missing executables or invalid args.

Metrics tests should cover singleton factory initialization from `hadoop-metrics.properties`, attribute set/remove/list behavior, null context creation, configured context reflection errors, start/stop/close lifecycle, updater registration/unregistration and periodic callbacks, record creation constraints, tag and metric typed setters/incrementers, update/remove row matching, file sink emission and flush, Ganglia emission hooks, log4j event counters by severity, JVM metrics updater output, and `MetricsRecordImpl` delegation to `AbstractMetricsContext`.

### subset-b-007285: lines 30887-37164

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml lines 30887-37164

## Chunk Scope

This chunk is a JDiff XML API snapshot for Hadoop 0.18.3. It starts immediately after `org.apache.hadoop.metrics.spi.MetricsRecordImpl` and covers complete API descriptions for several packages plus the opening portion of `org.apache.hadoop.util.GenericOptionsParser`. The document is metadata, not implementation source: control flow, state, persistence, and risk notes below are inferred from public signatures, visibility, declared exceptions, implemented interfaces, constants, and embedded Javadocs.

Covered package areas:

- `org.apache.hadoop.metrics.spi` and `org.apache.hadoop.metrics.util`
- `org.apache.hadoop.net`
- `org.apache.hadoop.record`, `org.apache.hadoop.record.compiler`, `org.apache.hadoop.record.compiler.ant`, `org.apache.hadoop.record.compiler.generated`, and `org.apache.hadoop.record.meta`
- `org.apache.hadoop.security`
- `org.apache.hadoop.tools`
- `org.apache.hadoop.util`

## Purpose

The chunk records public Hadoop common APIs for metrics emission, network/rack topology, socket timeout streams, Hadoop Record I/O serialization, the record compiler parser surface, record schema metadata, Unix-style user/group identity, command-line tools, and low-level utilities. Its direct purpose is compatibility research: every `<class>`, `<interface>`, constructor, method, field, implemented type, visibility flag, synchronization flag, deprecation marker, and declared exception is part of the API comparison surface used by JDiff.

At the subsystem level, the APIs expose:

- Metrics contexts and mutable metrics wrappers that bridge Hadoop metrics records and JMX registration.
- Network utilities for DNS, socket factories, non-blocking socket streams with read/write timeouts, rack topology, and script-backed host-to-switch mapping.
- A legacy Hadoop Record I/O stack: tagged and untagged serializers/deserializers, generated `Record` base classes, raw comparators, variable-length encodings, XML/CSV/binary formats, an IDL compiler, and schema/type metadata.
- Security identity classes based on Unix users and groups, including writable serialization and configuration-backed persistence.
- Tool entry points for `DistCp`, Hadoop archives, and log analysis.
- Utility classes for cyclic map iteration, daemon threads, disk checks, and generic Hadoop option parsing.

## Important APIs, Types, and Functions

### Metrics SPI and Utilities

- `MetricValue` wraps a `Number` with a boolean mode, exposed through `isIncrement()`, `isAbsolute()`, `getNumber()`, and constants `ABSOLUTE` and `INCREMENT`. It models whether a metric update replaces the current value or increments it.
- `NullContext` extends `AbstractMetricsContext` and provides do-nothing `startMonitoring()`, `emitRecord(...)`, `update(...)`, and `remove(...)`. It is the default context when metrics configuration is absent.
- `NullContextWithUpdateThread` also extends `AbstractMetricsContext`, but its doc says it keeps periodic updater behavior while emitting no records. It initializes with `init(String, ContextFactory)` and leaves `emitRecord`, `update`, and `remove` as no-ops.
- `OutputRecord` exposes read-only metric output access through `getTagNames()`, `getTag(String)`, `getMetricNames()`, and `getMetric(String)`.
- `Util.parse(String specs, int defaultPort)` parses comma/space-delimited host specifications into `List<InetSocketAddress>`, defaulting null specs to localhost on the supplied port.
- `MBeanUtil.registerMBean(String serviceName, String nameName, Object theMbean)` and `unregisterMBean(ObjectName)` standardize Hadoop MBean names, using JMX `ObjectName`.
- `MetricsIntValue` and `MetricsLongValue` are synchronized mutable point metrics with `set`, `get`, `inc`, `dec`, and `pushMetric(MetricsRecord)`. Their docs say `pushMetric` only publishes when updated since the previous push and does not itself push to JMX.
- `MetricsTimeVaryingInt` is a synchronized interval counter with `inc`, `pushMetric`, and `getPreviousIntervalValue()`.
- `MetricsTimeVaryingRate` is a synchronized interval rate metric with `inc(numOps,time)`, `inc(time)`, `pushMetric`, previous-interval operation count and average time getters, min/max getters, and `resetMinMax()`.

### Network and Socket APIs

- `DNS` provides static reverse DNS and interface lookup helpers: `reverseDns(InetAddress,String)`, `getIPs(String)`, `getDefaultIP(String)`, `getHosts(String,String)`, `getHosts(String)`, `getDefaultHost(String,String)`, and `getDefaultHost(String)`. Declared failures include `NamingException` and `UnknownHostException`.
- `DNSToSwitchMapping` is the rack-resolution interface: `resolve(List<String>) -> List<String>`.
- `NetUtils` is the main networking utility class. It exposes configurable socket factories, address parsing, server-address synthesis, static host resolution overrides, connect-address rewriting, and socket stream adapters:
  - `getSocketFactory(Configuration, Class)` and `getDefaultSocketFactory(Configuration)`
  - `getSocketFactoryFromProperty(Configuration, String)`
  - `createSocketAddr(String)` and `createSocketAddr(String, int)`
  - `getServerAddress(Configuration, String, String, String)`
  - `addStaticResolution(String,String)`, `getStaticResolution(String)`, `getAllStaticResolutions()`
  - `getConnectAddress(Server)`
  - `getInputStream(Socket)`, `getInputStream(Socket,long)`, `getOutputStream(Socket)`, `getOutputStream(Socket,long)`
- `NetworkTopology` models a cluster as a tree of racks, switches, and leaves. Public operations include `add(Node)`, `remove(Node)`, `contains(Node)`, `getNode(String)`, rack and leaf counts, `getDistance(Node,Node)`, `isOnSameRack(Node,Node)`, `chooseRandom(String)`, `countNumOfAvailableNodes(String,List<Node>)`, `toString()`, and synchronized `pseudoSortByDistance(Node,Node[])`. Public constants include `DEFAULT_RACK`, `UNRESOLVED`, `DEFAULT_HOST_LEVEL`, and `LOG`.
- `Node` defines topology node shape: network location, name, parent, and level getters/setters.
- `NodeBase` implements `Node` and stores protected mutable fields `name`, `location`, `level`, and `parent`. It includes constructors from path, name/location, and explicit parent/level. Static helpers include `getPath(Node)` and `normalize(String)`, with path constants `PATH_SEPARATOR`, `PATH_SEPARATOR_STR`, and `ROOT`.
- `ScriptBasedMapping` is a final `Configurable` implementation of `DNSToSwitchMapping`, using `topology.script.file.name`.
- `SocketInputStream` extends `InputStream` and implements `ReadableByteChannel`. Constructors accept `ReadableByteChannel` or `Socket` plus timeout. It exposes `read()`, `read(byte[],int,int)`, `read(ByteBuffer)`, synchronized `close()`, `getChannel()`, `isOpen()`, and `waitForReadable()`. Its docs warn that it configures the channel non-blocking, so callers must use matching Hadoop socket stream wrappers after construction.
- `SocketOutputStream` extends `OutputStream` and implements `WritableByteChannel`. It mirrors input behavior with `write(int)`, `write(byte[],int,int)`, `write(ByteBuffer)`, synchronized `close()`, `getChannel()`, `isOpen()`, `waitForWritable()`, and `transferToFully(FileChannel,long,int)`.
- `SocksSocketFactory` extends `SocketFactory` and implements `Configurable`, with five `createSocket` overloads, configurable proxy support, and equality/hash behavior.
- `StandardSocketFactory` extends `SocketFactory` with the normal five socket-creation overloads and equality/hash behavior.

### Record I/O Runtime APIs

- `BinaryRecordInput` and `BinaryRecordOutput` implement `RecordInput` and `RecordOutput` respectively, with constructors over streams or `DataInput`/`DataOutput`, static `get(...)` factories, primitive read/write methods, string and `Buffer` support, and record/vector/map boundary methods.
- `CsvRecordInput` and `CsvRecordOutput` implement the same interfaces over CSV-style streams.
- `XmlRecordInput` and `XmlRecordOutput` implement the same interfaces for XML-tagged record serialization.
- `Buffer` is a resizable byte sequence with constructors from byte arrays, `set`, `copy`, `get`, `getCount`, `getCapacity`, `setCapacity`, `reset`, `truncate`, append overloads, `hashCode`, `compareTo`, `equals`, `toString`, `toString(String charsetName)`, and `clone`.
- `Index` is the vector/map deserialization cursor interface with `done()` and `incr()`.
- `Record` is the abstract generated-record base. It implements `WritableComparable` and `Cloneable`, requires tagged `serialize(RecordOutput,String)`, tagged `deserialize(RecordInput,String)`, and `compareTo(Object)`, and supplies untagged serialize/deserialize plus Hadoop `Writable` `write(DataOutput)` and `readFields(DataInput)`.
- `RecordComparator` extends `WritableComparator`, defines raw byte-array `compare(...)`, and has synchronized static `define(Class, RecordComparator)` registration for optimized record comparators.
- `RecordInput` and `RecordOutput` are the core serializer interfaces. They enumerate primitive, string, buffer, record, vector, and map operations. Tags are explicitly for tagged formats such as XML.
- `org.apache.hadoop.record.Utils` provides byte/stream utility codecs: float and double parsing from byte arrays, zero-compressed variable-length int/long reads from byte arrays or `DataInput`, encoded-size calculation, variable-length writes to `DataOutput`, and byte comparison. It exposes `hexchars`.

### Record Compiler and Generated Parser APIs

- `CodeBuffer` only exposes `toString()`, acting as a code-generation buffer abstraction.
- `Consts` holds compiler string constants such as `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.
- `JType` is the abstract compiler type base. Concrete and composite types include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JBuffer`, `JString`, `JMap`, `JVector`, and `JRecord`; `JMap`, `JVector`, and `JRecord` take nested type or field metadata in constructors.
- `JField<T>` stores a named compiler field. `JFile` aggregates included files and records and exposes `genCode(String language, String destDir) -> int`.
- `RccTask` is an Ant task wrapper for the record compiler. It supports `language`, `file`, `failonerror`, `destdir`, nested `FileSet`s, and `execute()`, which invokes record compilation.
- `ParseException`, `Rcc`, `RccConstants`, `RccTokenManager`, `SimpleCharStream`, `Token`, and `TokenMgrError` are JavaCC-generated parser components for the record compiler. `Rcc` parses `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, and exposes token access, parser reinitialization, parse-exception generation, and tracing toggles.
- `RccConstants` defines token IDs for module, record, include, primitive types, vector/map, punctuation, strings, identifiers, lexical states, and token images.
- `SimpleCharStream` manages parser input buffering, line/column tracking, backup, reinitialization over readers or input streams with optional encodings, image/suffix retrieval, and buffer cleanup. Its doc says it assumes ASCII and does not process Unicode.
- `Token` stores token kind, position, image, next token, and special-token chain; `Token.newToken(int)` is the extensibility hook.
- `TokenMgrError` formats lexical errors and can escape unprintable characters.

### Record Metadata APIs

- `FieldTypeInfo` couples a field ID/name to a `TypeID`, with getters, `equals`, and `hashCode`.
- `TypeID` represents primitive type identifiers, exposes `getTypeVal()`, equality, hash code, singleton constants for primitive record types, and protected `typeVal`.
- `TypeID.RIOType` contains byte constants for supported IDL types: bool, buffer, byte, double, float, int, long, map, string, struct, and vector.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` extend `TypeID` to describe composite element/key/value/record types.
- `RecordTypeInfo` extends `Record` and can serialize/deserialize schema metadata. It supports `getName`, `setName`, `addField`, `getFieldTypeInfos`, one-level `getNestedStructTypeInfo`, `serialize`, `deserialize`, and `compareTo`.
- `org.apache.hadoop.record.meta.Utils.skip(RecordInput,String,TypeID)` skips data in a record input according to type metadata.

### Security APIs

- `UnixUserGroupInformation` extends `UserGroupInformation`. It can be constructed from username/groups or array form, can create immutable instances, exposes username and groups, implements `readFields(DataInput)` and `write(DataOutput)`, persists to configuration with `saveToConf(Configuration,String,UnixUserGroupInformation)`, reads from configuration with `readFromConf`, and has three `login` overloads for Unix/config-backed identity. It also defines equality, hash code, string conversion, and `UGI_PROPERTY_NAME`.
- `UserGroupInformation` is an abstract `Writable` identity base. It exposes thread-local current identity with `getCurrentUGI()` and `setCurrentUGI(UserGroupInformation)`, abstract `getUserName()` and `getGroupNames()`, static `login(Configuration)`, static `readFrom(Configuration)`, and `LOG`.

### Tools and General Utilities

- `DistCp` implements `Tool`, has configuration accessors, static `copy(Configuration,String,String,Path,boolean,boolean)`, `run(String[])`, `main(String[])`, and `getRandomId()`. Its run doc describes recursive cross-filesystem directory copy using MapReduce mappers and no reducer.
- `DistCp.DuplicationException` is an `IOException` for duplicate source files with public `ERROR_CODE`.
- `HadoopArchives` implements `Tool`, has configuration accessors, `archive(List<Path>,String,Path)`, `run(String[])`, and `main(String[])` for Hadoop archive creation.
- `Logalyzer` archives and analyzes Hadoop logs via `doArchive(String,String)`, `doAnalyze(String,String,String,String,String)`, and `main(String[])`.
- `Logalyzer.LogComparator` extends `Text.Comparator`, implements `Configurable`, and compares raw text keys using configurable sort columns.
- `Logalyzer.LogRegexMapper` extends `MapReduceBase` and implements `Mapper<K,Text,Text,LongWritable>`, with `configure(JobConf)` and `map(...)`.
- `CyclicIteration<K,V>` is an `Iterable<Map.Entry<K,V>>` over a `SortedMap`, starting after a given key and wrapping from end to beginning.
- `Daemon` extends `Thread`, has constructors for empty, `Runnable`, and `ThreadGroup/Runnable`, stores a retrievable runnable via `getRunnable()`, and is documented as setting daemon mode true.
- `DiskChecker` exposes `mkdirsWithExistsCheck(File)` and `checkDir(File)`, plus nested `DiskErrorException` and `DiskOutOfSpaceException`.
- `GenericOptionsParser` begins at the end of the chunk. Visible APIs include constructors for Hadoop generic options alone or generic plus caller-supplied commons-cli `Options`, `getRemainingArgs()`, `getCommandLine()`, and `printGenericCommandUsage(PrintStream)`. The visible docs list generic Hadoop CLI flags such as `-conf`, `-D`, `-fs`, `-jt`, `-files`, `-libjars`, and `-archives`; the class body continues after this chunk.

## Control Flow

Because this is an API descriptor, executable control flow is not present directly. The main inferred flows are:

- Metrics update flow: callers mutate synchronized metric wrappers, periodic metrics context updates call `pushMetric(MetricsRecord)`, and each wrapper emits only data changed since the prior interval. JMX uses getters rather than `pushMetric`.
- Null metrics flow: when no metrics configuration exists, `NullContext` absorbs lifecycle, update, remove, and emit calls. `NullContextWithUpdateThread` keeps the `AbstractMetricsContext` updater thread active while suppressing emission, supporting pull-style systems such as JMX.
- Network resolution flow: host/interface names are resolved through `DNS`, mapped to racks through `DNSToSwitchMapping` or `ScriptBasedMapping`, represented as `Node`/`NodeBase`, and inserted into `NetworkTopology`. Replica placement/read optimization can ask the topology for distance, rack locality, random choices under a scope, and pseudo-sorting by distance.
- Socket timeout flow: `NetUtils` chooses a socket factory from configuration and wraps channel-backed sockets in `SocketInputStream`/`SocketOutputStream` when timeout-aware channel I/O is needed. Those wrappers convert blocking channels to non-blocking selectable channels and wait for readiness before read/write or file-channel transfer.
- Record serialization flow: generated `Record` subclasses call `serialize`/`deserialize` with a `RecordOutput`/`RecordInput`; concrete binary, CSV, or XML implementations handle primitive values and structural boundaries. `Index` controls vector/map deserialization loops.
- Record compiler flow: Ant or CLI invokes `Rcc`, which lexes through `SimpleCharStream` and `RccTokenManager`, parses includes/modules/records/fields/types into `JFile`, `JRecord`, `JField`, and `JType` objects, and then generates code through `JFile.genCode(...)`.
- Record metadata flow: `RecordTypeInfo` serializes schema information as a `Record`; `TypeID` and composite subclasses describe field types; metadata utilities can skip unknown or unwanted fields based on type IDs.
- UGI flow: callers establish thread-local identity with `UserGroupInformation.setCurrentUGI`, read/write identity through Hadoop `Writable`, and either login from Unix state or load/save comma-separated user/group strings in `Configuration`.
- Tool flow: `DistCp`, `HadoopArchives`, and `Logalyzer` expose `Tool.run`/`main` entry points that translate command-line arguments into MapReduce jobs or filesystem/archive operations.

## State and Persistence Behavior

- Metrics wrappers hold mutable in-memory counters, previous-interval values, and update flags. Method synchronization on metric mutation and push APIs is explicitly part of the public signature for the utility metric classes.
- `MetricValue` holds a numeric value plus absolute/increment mode. `OutputRecord` exposes collected tag/metric maps as read-only lookup APIs.
- `MBeanUtil` persists no local state in the API, but registers and unregisters process-level JMX MBeans through the platform MBean server.
- `NetworkTopology` maintains a mutable tree of `Node` objects plus rack and leaf counts. `NodeBase` stores mutable parent/level/location/name fields, making topology correctness dependent on consistent updates.
- `NetUtils` exposes static host-resolution overrides, implying JVM-wide mutable resolution state through `addStaticResolution`, `getStaticResolution`, and `getAllStaticResolutions`.
- `SocketInputStream` and `SocketOutputStream` hold channel, timeout, and open/closed state; synchronized `close()` marks an important concurrency boundary.
- `Buffer` separates logical count from capacity and supports in-place resize, truncate, reset, append, clone, and byte-array exposure.
- `Record` implementations persist through Hadoop `Writable` streams and through tagged/untagged Record I/O formats. `RecordTypeInfo` persists schema metadata using the same record serialization framework.
- `UnixUserGroupInformation` persists identity both as writable binary data and as a comma-separated configuration property. Its docs mention a UGI map/cache keyed by user identity, so repeated logins/config reads can return cached objects.
- `UserGroupInformation` stores current identity per thread.
- `DistCp`, `HadoopArchives`, and `Logalyzer` persist outputs in distributed filesystems: copies, archive contents/indexes, archived logs, and analysis output directories.
- `GenericOptionsParser` mutates a supplied `Configuration` according to generic CLI arguments and retains remaining arguments / parsed `CommandLine` state.

## Dependencies and Integration Points

- Metrics APIs depend on `org.apache.hadoop.metrics.MetricsRecord`, `ContextFactory`, and SPI classes such as `AbstractMetricsContext`, `MetricsRecordImpl`, and `OutputRecord`.
- JMX integration uses `javax.management.ObjectName`.
- Network APIs depend on Java networking/NIO/JNDI classes (`Socket`, `SocketFactory`, `Proxy`, `InetSocketAddress`, `NetworkInterface` by implication, channels, selectors, DNS naming exceptions), Hadoop `Configuration`, `Configurable`, and IPC `Server`.
- Topology APIs integrate with HDFS/MapReduce placement logic through `Node`, rack names, and distance/locality sorting.
- Socket wrappers integrate with Java `FileChannel.transferTo/transferFrom`, Hadoop RPC sockets, and `NetUtils` factory-created sockets.
- Record I/O depends on Hadoop `WritableComparable`, `WritableComparator`, and Java `DataInput`/`DataOutput`/streams. It also provides interoperability across binary, CSV, and XML encodings.
- Compiler APIs integrate with Ant (`Task`, `FileSet`, `BuildException`) and JavaCC-generated parsing classes.
- Record metadata integrates with record serialization to support schema-aware skipping and nested type descriptions.
- Security APIs integrate with Hadoop `Configuration`, `Writable`, Unix OS account/group discovery, JAAS `LoginException`, and thread-local execution identity.
- Tool APIs integrate with Hadoop `Tool`, `Path`, `FileSystem` behavior, MapReduce `Mapper`, `OutputCollector`, `Reporter`, `JobConf`, and text comparators.
- `GenericOptionsParser` integrates Hadoop generic CLI handling with Apache Commons CLI.

## Risks and Edge Cases

- This XML chunk exposes public API but not implementation bodies. Any behavioral claim beyond signatures and embedded docs must be validated against the corresponding Java sources.
- The chunk starts at the end marker for `MetricsRecordImpl` and ends inside `GenericOptionsParser`, so neither class is fully represented here.
- Many APIs are public and not deprecated in this snapshot; compatibility-sensitive changes include method visibility, synchronization flags, checked exceptions, generic signatures, field constants, and implemented interfaces.
- Metrics wrappers rely on synchronized methods for thread safety. Removing synchronization or changing push-on-update semantics would affect metrics consistency and JMX visibility.
- `NullContextWithUpdateThread` intentionally keeps sampling without emission. Treating it as a pure no-op could break pull-based metrics systems.
- `SocketInputStream` and `SocketOutputStream` switch channels to non-blocking mode. Mixing them with raw `Socket.getInputStream()` or `Socket.getOutputStream()` after wrapper creation is explicitly unsafe.
- Timeout semantics differ depending on whether sockets have associated channels. `NetUtils` docs warn that fallback raw socket streams ignore wrapper timeout arguments and use socket-level SO_TIMEOUT or blocking behavior.
- `NetworkTopology` operations can throw or behave incorrectly for null nodes, non-leaf additions, nodes not in the cluster, malformed paths, or inconsistent parent/level state.
- `ScriptBasedMapping` depends on external script configuration, making rack resolution vulnerable to missing scripts, bad output cardinality, or slow/failed script execution.
- `Buffer.get()` exposes byte-array storage; callers can mutate buffer contents unless implementation copies defensively. Count/capacity differences must be respected.
- CSV/XML/binary Record I/O formats share an interface but have different tagging and escaping rules. Tagged `tag` parameters matter for XML and may be ignored elsewhere.
- JavaCC parser classes expose many mutable public/protected fields. These are compatibility liabilities and are easy to misuse directly.
- `SimpleCharStream` is documented as ASCII-only, so Unicode record definitions may fail or produce incorrect positions unless the underlying implementation handles more than this doc promises.
- `RecordTypeInfo.compareTo` is documented ambiguously: it says the class is not meant for comparison and also says it returns zero for another `RecordTypeInfo`. Callers should not rely on meaningful ordering.
- `UnixUserGroupInformation` string persistence is comma-separated; malformed strings, too few fields, null entries, or group names containing separators are risk areas.
- Thread-local UGI state can leak across pooled threads if not reset.
- `DistCp` duplicate handling and source-list behavior are API-visible through `DuplicationException`, `srcAsList`, and `ignoreReadFailures`; regressions here can affect large filesystem copy jobs.
- `DiskChecker.mkdirsWithExistsCheck` exists specifically for concurrent directory creation races. Replacing it with plain `File.mkdirs()` would reintroduce race failures.
- `GenericOptionsParser` mutates caller-supplied configuration. Parse ordering and remaining-argument behavior are important for tools that layer their own options on top of generic Hadoop options.

## Test Signals

Useful validation signals for implementations represented by this chunk include:

- JDiff/API tests verifying all listed classes, interfaces, constructors, methods, fields, visibility, abstract/final/static flags, synchronized flags, implemented interfaces, return types, parameter types, and checked exceptions remain compatible.
- Metrics tests for one-shot `MetricsIntValue`/`MetricsLongValue` push behavior, interval reset behavior for `MetricsTimeVaryingInt`, rate average/min/max behavior for `MetricsTimeVaryingRate`, and no-emission behavior for both null contexts.
- JMX tests for `MBeanUtil` name formation and unregister behavior.
- DNS and `NetUtils` tests for interface lookup fallbacks, static resolution override precedence, address parsing with default ports, and server/connect address rewriting.
- Network topology tests for add/remove counters, rack counts, distance calculation, same-rack checks, random scope selection including `~` exclusions, excluded-node counts, and `pseudoSortByDistance` local/local-rack ordering.
- Socket stream tests for channel-backed timeout reads/writes, zero timeout, negative timeout rejection if implemented, close idempotence, readiness waits, `SocketTimeoutException`, and `transferToFully` EOF handling.
- Socket factory tests for configured SOCKS proxy behavior, equality/hash code, and all overloads.
- Record I/O round-trip tests across binary, CSV, and XML for primitives, strings, buffers, records, vectors, and maps, including tagged and untagged paths.
- Variable-length integer/long codec tests for boundary values around one-byte and multi-byte encodings, negative values, and stream/byte-array parity.
- `Buffer` tests for count vs capacity, append/truncate/reset, comparison ordering, charset conversion, equality, hash code, clone independence, and byte-array mutation behavior.
- Record compiler tests for IDL parsing of includes, modules, primitive/composite fields, parse errors, lexical errors, Ant task filesets, destination directories, fail-on-error behavior, and generated code compilation.
- Metadata tests for `TypeID` equality/hash behavior, composite type equality, `RecordTypeInfo` serialization/deserialization, nested struct lookup, and schema-based skip behavior.
- Security tests for UGI read/write round trips, configuration save/read, current-thread UGI isolation, Unix login fallback, malformed configuration handling, equality/hash code, immutable instance behavior, and group order preservation.
- Tool integration tests for `DistCp` source list mode, duplicate detection, read-failure ignore mode, MapReduce copy outputs, archive generation/indexing, log archive/analyze jobs, log comparator sorting columns, and regex mapper output counts.
- Utility tests for `CyclicIteration` wraparound ordering, daemon-thread flag and runnable retention, concurrent directory creation with `mkdirsWithExistsCheck`, `checkDir` failure modes, and `GenericOptionsParser` parsing of visible generic flags plus remaining-argument preservation.

### subset-b-007286: lines 37165-38826

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml lines 37165-38826

## Chunk Scope

This chunk is the final slice of the Hadoop 0.18.3 JDiff API XML file. It starts in the closing documentation for `org.apache.hadoop.util.GenericOptionsParser`, then covers the remaining public `org.apache.hadoop.util` API through `XMLUtils`, ending with the closing `</package>` and `</api>` tags.

Because the source is generated JDiff XML rather than implementation code, control-flow, state, persistence, and risk notes are inferred from public signatures, visibility, inheritance, synchronized/static markers, declared exceptions, fields, and embedded API documentation.

## Purpose

The chunk records Hadoop 0.18.3 utility APIs used by command-line entry points, generic option parsing, typed reflection, in-memory sorting, host include/exclude lists, progress tracking, shell command execution, string/byte/time formatting, tool launch wrappers, build version reporting, and XSLT transformation. It is a compatibility surface: downstream consumers can diff method names, overloads, return types, checked exceptions, constants, deprecations, and package placement across Hadoop releases.

The utilities here are mostly framework glue rather than distributed filesystem implementations. They connect Hadoop command-line programs to `Configuration`, provide reusable sort contracts for index-addressed collections, expose small runtime/introspection helpers, and wrap operating-system or JVM services in Hadoop-facing APIs.

## Important APIs and Types

### Generic command-line integration

The chunk begins with the final documentation for `GenericOptionsParser`. The visible docs show the standard command shape:

- `bin/hadoop command [genericOptions] [commandOptions]`
- generic options may mutate `Configuration` objects passed into constructors.
- implementation is based on Commons CLI.
- examples include `dfs -fs`, `dfs -D`, `dfs -conf`, `job -D`, `job -jt`, local job tracker selection, and `jar -libjars -archives -files`.

This ties the later `Tool` and `ToolRunner` APIs to `Configuration` mutation and to common Hadoop launcher behavior.

### `GenericsUtil`

`org.apache.hadoop.util.GenericsUtil` is a public helper for Java generics:

- `getClass(T)` returns a typed `Class<T>` for an object.
- `toArray(Class<T>, List<T>)` converts a list to a typed array using an explicit component class.
- `toArray(List<T>)` converts a non-empty list to a typed array but documents `ArrayIndexOutOfBoundsException` if the list is empty, advising the explicit-class overload for empty lists.

The API exists to work around Java's erased generic array creation limits.

### Sort contracts: `IndexedSortable`, `IndexedSorter`, `HeapSort`, `QuickSort`, and `MergeSort`

`IndexedSortable` is the core collection contract for index-addressed sorting. It exposes:

- `compare(int i, int j)` with `Comparable`-compatible semantics.
- `swap(int i, int j)` to exchange entries at logical indices.

`IndexedSorter` is the algorithm contract:

- `sort(IndexedSortable s, int l, int r)` sorts `[l, r)`.
- `sort(IndexedSortable s, int l, int r, Progressable rep)` performs the same sort while periodically reporting progress.

`HeapSort` is a final public `IndexedSorter` implementation with `sort` overloads. `QuickSort` is also a final public `IndexedSorter`; it exposes protected static `getMaxDepth(int)` returning `2 * ceil(log(n))`, and its docs state that quicksort falls back to `HeapSort` if recursion depth exceeds that bound. `MergeSort` is an older public class constructed with `Comparator<IntWritable>` and exposes `mergeSort(int[] src, int[] dest, int low, int high)`.

The important integration contract is that sort algorithms only call `compare` and `swap`; storage layout stays private to the `IndexedSortable`.

### Host and native/platform helpers

`HostsFileReader` is constructed from include and exclude host file paths and exposes:

- `refresh()` with `IOException`.
- `getHosts()` returning `Set<String>`.
- `getExcludedHosts()` returning `Set<String>`.

This is a lightweight stateful reader for daemon host admission/exclusion lists.

`NativeCodeLoader` exposes:

- static `isNativeCodeLoaded()`.
- `getLoadNativeLibraries(JobConf)`.
- `setLoadNativeLibraries(JobConf, boolean)`.

The docs say it loads native Hadoop code such as `libhadoop.so`, falling back to bundled Linux i386 native code or Java implementations where appropriate. The JobConf accessors gate native-library usage per job.

`PlatformName` exposes static `getPlatformName()` and `main(String[])` for reporting the complete Java VM platform name.

`VersionInfo` exposes build metadata:

- `getVersion()`, `getRevision()`, `getDate()`, `getUser()`, `getUrl()`, and `getBuildVersion()`.
- `main(String[])`.

The docs tie it to package info and `HadoopVersionAnnotation`.

### Jar and program launch helpers

`PrintJarMainClass` is a micro-application with `main(String[])` that prints the main class name from a jar file.

`ProgramDriver` provides a small registry-driven command dispatcher:

- `addClass(String name, Class mainClass, String description)` registers a named program and may throw `Throwable`.
- `driver(String[] args)` reads `args[0]`, finds the named program, and invokes that program's `main` with the remaining arguments. It declares `Throwable` to propagate reflection and target program failures.

`RunJar` is the main Hadoop job-jar launcher utility:

- static `unJar(File jarFile, File toDir)` unpacks a jar and throws `IOException`.
- static `main(String[] args)` runs a Hadoop job jar and throws `Throwable`; docs say the main class may come from the jar manifest or from the command line.

Together these classes provide Hadoop's command-dispatch path from shell commands and jars into Java `main` methods.

### Priority queue

`PriorityQueue` is an abstract public heap-style queue over `Object` values. Subclasses must implement protected abstract `lessThan(Object a, Object b)`. It exposes:

- protected final `initialize(int maxSize)`.
- public final `put(Object)` that adds in logarithmic time and may throw an array bounds runtime failure if over capacity.
- public `insert(Object)` that adds only if the queue is not full or the candidate is not less than the current top.
- public final `top()`, `pop()`, `adjustTop()`, `size()`, and `clear()`.

Docs state the least element is returned in constant time and put/pop are logarithmic. `adjustTop()` is an optimization for cases where the current top object mutates.

### Progress reporting

`Progress` models a tree of execution phases:

- constructor creates a root node.
- `addPhase(String status)` adds a named child.
- synchronized `addPhase()` adds an unnamed child.
- synchronized `startNextPhase()` advances at the current tree level.
- synchronized `phase()` returns the current child node.
- `complete()` completes a node and advances its parent.
- synchronized `set(float)` sets progress on a leaf.
- synchronized `get()` returns overall root progress.
- synchronized `setStatus(String)` updates status.
- `toString()` renders current state.

`Progressable` is the callback interface with `progress()`. Its documentation emphasizes that long operations must report progress so the framework does not assume timeout/failure.

The sort APIs, job output streams, and long-running Hadoop components can use `Progressable` as a common liveness signal.

### Reflection and diagnostics

`ReflectionUtils` provides framework-level object construction and thread diagnostics:

- static `setConf(Object, Configuration)` sets configuration on configurable objects when applicable.
- static `newInstance(Class<?>, Configuration)` creates and configures an object.
- static `setContentionTracing(boolean)` toggles thread contention tracing.
- static `printThreadInfo(PrintWriter, String)` prints thread information and stack traces.
- static `logThreadInfo(Log, String, long)` logs stack traces at INFO no more often than `minInterval`.
- static generic `getClass(T)` returns the correctly typed `Class<T>`.

It depends on `Configuration`, Hadoop `Configurable` behavior by implication, and Commons Logging for logged diagnostics.

### Servlet utilities

`ServletUtil` contains static helpers for Hadoop's web UIs:

- `initHTML(ServletResponse, String)` returns a `PrintWriter` after writing the initial HTML header and can throw `IOException`.
- `getParameter(ServletRequest, String)` returns a request parameter or `null` if it only contains whitespace.
- `htmlFooter()` returns an HTML footer.
- public static final `HTML_TAIL` exposes the footer fragment.

This is JSP/servlet glue rather than storage logic.

### Shell command execution

`Shell` is an abstract base class for running Unix commands, optionally gated by a minimum interval. Public/protected API includes:

- constructors `Shell()` and `Shell(long interval)`.
- static command builders `getGROUPS_COMMAND()`, `getGET_PERMISSION_COMMAND()`, and `getUlimitMemoryCommand(JobConf)`.
- protected `setEnvironment(Map<String,String>)`.
- protected `setWorkingDirectory(File)`.
- protected `run()` which checks whether a command should execute and runs it if needed.
- protected abstract `getExecString()` returning command and arguments.
- protected abstract `parseExecResult(BufferedReader)` for parsing process output.
- public `getProcess()` and `getExitCode()`.
- static `execCommand(String[])` for simple command execution returning output.

Public fields document platform/command integration: `LOG`, `USER_NAME_COMMAND`, `SET_PERMISSION_COMMAND`, `SET_OWNER_COMMAND`, `SET_GROUP_COMMAND`, and `WINDOWS`.

`Shell.ExitCodeException` extends `IOException`, adds an exit code, and exposes `getExitCode()`. `Shell.ShellCommandExecutor` is a concrete nested executor with constructors for command only, command plus working directory, and command plus directory plus environment. It exposes `execute()`, `getOutput()`, and concrete implementations of `getExecString()` and `parseExecResult()`. Its docs say output is stored as-is and should be small.

The `getUlimitMemoryCommand(JobConf)` docs make this class an integration point for MapReduce child process limits, especially Hadoop Pipes and Streaming. It may return `null` on non-Unix platforms or when no limit is specified.

### String, byte, URI, path, and time utilities

`StringUtils` is a broad static utility class with public constants `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`. Methods include:

- `stringifyException(Throwable)` for stack trace strings.
- `simpleHostname(String)` for stripping a domain suffix after the first dot.
- `humanReadableInt(long)` for approximate 1024-based `k`, `m`, and `g` formatting.
- `formatPercent(double done, int digits)`.
- `arrayToString(String[])`.
- `byteToHexString(byte[])` and `hexStringToByte(String)`.
- `uriToString(URI[])`, `stringToURI(String[])`, and `stringToPath(String[])`.
- `formatTimeDiff(long finishTime, long startTime)`.
- `getFormattedTimeWithDiff(DateFormat, long finishTime, long startTime)`.
- `getStrings(String)` and `getStringCollection(String)` for comma-separated values.
- `split(String)` and `split(String, char escapeChar, char separator)`.
- `escapeString(String)` and `escapeString(String, char escapeChar, char charToEscape)`.
- `unEscapeString(String)` and `unEscapeString(String, char escapeChar, char charToEscape)`.
- `getHostname()`.
- `startupShutdownMessage(Class, String[], Log)`.

It integrates with `java.net.URI`, `org.apache.hadoop.fs.Path`, `java.text.DateFormat`, and Commons Logging. The escaping/splitting API is important because comma-separated config values can contain escaped separators.

### Tool and ToolRunner

`Tool` is a public interface extending `org.apache.hadoop.conf.Configurable` and declaring `run(String[] args)` returning an exit code and throwing `Exception`. Its docs define the standard Hadoop application pattern: `ToolRunner` handles generic command-line options and the application handles only custom arguments after `Configuration` has been processed.

`ToolRunner` exposes:

- static `run(Configuration, Tool, String[])`, which parses generic arguments, sets the tool's possibly modified configuration, invokes `Tool.run`, and returns its exit code.
- static `run(Tool, String[])`, equivalent to `run(tool.getConf(), tool, args)`.
- static `printGenericCommandUsage(PrintStream)`.

This is the main public integration between command-line parsing, `Configuration`, and reusable Hadoop application entry points.

### XML transformation

`XMLUtils` exposes static `transform(InputStream styleSheet, InputStream xml, Writer out)`, throwing `TransformerConfigurationException` and `TransformerException`. It wraps JAXP/XSLT transformation for Hadoop callers.

## Control Flow and Behavioral Contracts

The visible control flow is API-level:

- Hadoop command launchers pass raw shell arguments into `GenericOptionsParser` or `ToolRunner`; generic options mutate `Configuration`, and remaining arguments reach the application-specific `Tool.run`.
- `ProgramDriver` dispatches by matching the first command-line token against a registered class and reflectively invoking that class's main method.
- `RunJar` unpacks a jar, determines a main class from manifest or arguments, and invokes it as a Hadoop job entry point.
- Sorting flows through `IndexedSorter.sort`, which manipulates client-owned storage only through `IndexedSortable.compare` and `swap`; `QuickSort` may switch to `HeapSort` after a computed recursion-depth limit.
- Progress flows from long-running algorithms or operations through `Progressable.progress()`, while hierarchical tasks can update a `Progress` tree with phases, leaf percentages, and statuses.
- Reflection-based construction flows through `ReflectionUtils.newInstance`, followed by configuration injection through `setConf`.
- Shell command execution flows through `Shell.run()` or `ShellCommandExecutor.execute()`: compute command array, apply environment/working directory, start a process, parse output, track process and exit code, and surface non-zero exits through an IOException subtype.
- String list parsing flows through escape-aware split/unescape helpers so values containing separator characters can round-trip.
- XML transformation flows from stylesheet input and XML input into a writer via JAXP transformer APIs.

## State and Persistence Behavior

Most classes in this chunk are stateless static helpers, but several maintain process-local state:

- `HostsFileReader` stores include and exclude host sets loaded from configured files; `refresh()` updates that in-memory view and can fail with `IOException`.
- `PriorityQueue` stores a bounded heap of object references after `initialize(maxSize)`. It does not persist contents and depends on subclass ordering.
- `Progress` stores a mutable tree of phases, current child position, leaf progress values, and optional status strings. Several mutators/accessors are synchronized, indicating shared-thread usage.
- `Shell` instances store command execution interval, environment, working directory, current process, and last exit code. `ShellCommandExecutor` additionally stores captured command output.
- `ReflectionUtils.logThreadInfo` has a `minInterval` contract, implying process-level throttling of repeated thread-dump logging.
- `NativeCodeLoader` reflects process-level native library load state while the JobConf accessors persist per-job policy in configuration.
- `VersionInfo` reads build metadata packaged with the Hadoop distribution rather than mutating runtime state.
- `StringUtils` conversion helpers are stateless, but `startupShutdownMessage` emits persistent log records for daemon lifecycle events.
- `XMLUtils.transform` writes transformed XML to the supplied writer but owns no persistent repository state.

No distributed filesystem metadata or durable data layout is defined in this chunk; durable effects are limited to host files read by `HostsFileReader`, shell commands executed by `Shell`, log output, jar extraction by `RunJar.unJar`, and XML output written through `XMLUtils`.

## Dependencies and Integration Points

Key dependencies visible from signatures and docs include:

- Hadoop configuration and MapReduce: `Configuration`, `Configurable`, `JobConf`, `Tool`, `ToolRunner`, `Progressable`, and `Path`.
- Hadoop IO primitives: `IntWritable` in the `MergeSort` comparator signature.
- Java runtime and IO: `Class`, reflection-based main invocation, `File`, `InputStream`, `BufferedReader`, `PrintWriter`, `PrintStream`, `Writer`, `IOException`, `URI`, `DateFormat`, and `Process`.
- Java collections: `List<T>`, `Set<String>`, `Map<String,String>`, `Collection<String>`, and `Comparator`.
- Servlet APIs: `ServletRequest` and `ServletResponse`.
- Logging: `org.apache.commons.logging.Log`.
- XML transformation: `javax.xml.transform.TransformerConfigurationException` and `TransformerException`.
- Commons CLI, mentioned in `GenericOptionsParser` docs.
- Operating-system commands and platform checks in `Shell`, including Unix user/group/permission commands, `ulimit`, and Windows detection.

Integration points are broad: CLI tools use `ToolRunner`; MapReduce streaming or pipes child processes can use `Shell.getUlimitMemoryCommand`; sort-heavy Hadoop internals can provide `IndexedSortable`; daemons can expose progress through `Progress` and `Progressable`; web consoles can use `ServletUtil`; release/version commands can use `VersionInfo`; and build/doc tooling can use `XMLUtils`.

## Risks and Edge Cases

- This chunk is generated API XML, so it does not expose implementation internals such as exact parser options, heap array layout, shell stderr handling, thread-dump throttling storage, or native library load attempts.
- The range starts in the middle of `GenericOptionsParser` documentation, so constructor and method signatures for that class must be reconciled from the previous chunk.
- `GenericsUtil.toArray(List<T>)` is unsafe for empty lists and explicitly documents `ArrayIndexOutOfBoundsException`.
- `PriorityQueue.put(Object)` can exceed `maxSize` and throw a runtime array bounds failure; callers needing bounded top-N behavior should use `insert(Object)`.
- `PriorityQueue.adjustTop()` assumes only the top object changed; using it after changing another element can corrupt ordering.
- `IndexedSortable.compare` must be consistent and `swap` must correctly mutate the backing collection; sort algorithms have no other way to validate storage state.
- `QuickSort` fallback behavior means tests should cover recursion-depth protection, not just average-case sorting.
- `HostsFileReader.refresh()` may observe partially written host files or fail on missing/unreadable paths; exposed getters return sets whose mutability is not documented in the XML.
- `NativeCodeLoader` behavior is platform-sensitive and may silently fall back to Java implementations depending on library availability and job configuration.
- `ProgramDriver.driver` and `RunJar.main` declare `Throwable`, so caller-side error boundaries must handle reflection failures and arbitrary application exceptions.
- `Shell` is platform-sensitive: many constants are Unix commands, while `WINDOWS` and `getUlimitMemoryCommand` indicate different behavior on Windows/Cygwin/non-Unix systems.
- `ShellCommandExecutor` docs expect small output; using it for large command output risks memory pressure.
- `Shell.execCommand` covers simple cases only; callers needing custom parsing, environment, working directory, or interval gating should use subclasses.
- `StringUtils` comma escaping must be used consistently; mixing raw `arrayToString` with escape-aware `split` can corrupt values containing commas or escape characters.
- `hexStringToByte(String)` implies output length is `hex.length()/2`; odd-length or invalid hex input behavior is not visible here.
- `getFormattedTimeWithDiff` returns an empty string for finish time zero and omits differences when start time is zero, which can surprise display code.
- `ToolRunner.run(Tool, String[])` depends on `tool.getConf()`; a tool with null or improperly initialized configuration may differ from `run(Configuration, Tool, String[])`.
- Servlet HTML helpers may produce fixed fragments; escaping behavior for titles and parameters is not visible in the API XML.
- `XMLUtils.transform` exposes raw transformer exceptions; callers must handle stylesheet compilation and runtime transform failures.

## Test Signals

Useful tests inferred from this API slice include:

- `ToolRunner` tests for generic option parsing with `-D`, `-conf`, `-fs`, `-jt`, `-libjars`, `-files`, and `-archives`, verifying configuration mutation and preservation of application arguments.
- `Tool` integration tests that `ToolRunner.run` injects the modified configuration before invoking `run`.
- `GenericsUtil` tests for typed array creation with non-empty lists, empty lists with explicit class, and documented failure for empty implicit-class conversion.
- `IndexedSorter` contract tests for `HeapSort` and `QuickSort` over custom `IndexedSortable` implementations, including empty ranges, singleton ranges, duplicates, reverse order, progress callbacks, and quicksort fallback depth.
- `MergeSort` tests around comparator behavior for `IntWritable`-indexed arrays if this legacy sorter remains used.
- `HostsFileReader` tests for include/exclude parsing, refresh after file changes, missing files, duplicate hosts, whitespace/comments if supported by implementation, and getter isolation from internal mutable sets.
- `NativeCodeLoader` tests for `isNativeCodeLoaded` under absent/present native libraries and JobConf get/set policy round trips.
- `ProgramDriver` tests for successful dispatch, unknown command handling, empty args, argument shifting, duplicate registration, and propagation of target main exceptions.
- `RunJar` tests for manifest main-class discovery, explicit main-class override, jar unpacking, nested resources, missing main class, and cleanup/error behavior.
- `PriorityQueue` tests for capacity, ordering, `insert` rejection when full, `top`, `pop`, `adjustTop`, `clear`, and subclass `lessThan` edge cases.
- `Progress` tests for phase-tree aggregation, synchronized add/start/phase/set/get behavior, status rendering, completion advancing parent nodes, and `toString`.
- `Progressable` timeout/liveness tests in components that accept a progress callback.
- `ReflectionUtils` tests for configuring `Configurable` objects, constructing default constructors, failure on missing constructors, typed class return, thread-info printing, and `logThreadInfo` minimum interval throttling.
- `ServletUtil` tests for HTML header/footer generation and blank-parameter-to-null behavior.
- `Shell` tests for command arrays, environment and working directory application, interval gating, stdout parsing, exit code reporting, non-zero exit exceptions, static `execCommand`, platform command builders, and memory-limit command construction from JobConf.
- `StringUtils` tests for exception stringification, hostname simplification, human-readable integer boundaries, percentage precision, byte/hex round trips, URI/path array conversion, time-diff formatting including zero and negative cases, comma-separated parsing, escaping/unescaping custom separators, hostname fallback, and startup/shutdown log content.
- `VersionInfo` tests for non-empty packaged version, revision/date/user/url/build-version fields and `main` output.
- `XMLUtils` tests for successful XSLT transformation, stylesheet compilation failure, XML transform failure, writer propagation, and stream ownership expectations.

## Chunk Boundary Notes

The previous chunk is required to complete `GenericOptionsParser` signatures and any earlier `org.apache.hadoop.util` classes. This chunk ends the `org.apache.hadoop.util` package and the entire JDiff API file, so final merge should treat `XMLUtils` as complete here and preserve that no later package content follows.
