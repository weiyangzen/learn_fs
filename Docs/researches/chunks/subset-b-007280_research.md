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
