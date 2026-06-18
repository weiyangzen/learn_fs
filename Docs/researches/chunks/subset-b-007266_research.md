# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 6281-12462

## Scope

This chunk is a Hadoop 0.18.1 JDiff API XML segment. It begins inside `org.apache.hadoop.dfs.namenode.metrics.NameNodeStatistics`, includes the complete `NameNodeStatisticsMBean` interface, then covers `org.apache.hadoop.filecache.DistributedCache`, most of the public `org.apache.hadoop.fs` API surface, FTP and Kosmos/KFS filesystem adapters, and the start of `org.apache.hadoop.fs.permission` with `AccessControlException`. It ends at the opening marker for `FsAction`, whose declaration is outside this chunk.

Because the source is generated API XML, this document describes exported contracts, signatures, inheritance, serialization hooks, and behavior documented in Javadocs. Control-flow and state notes are inferred only from those public contracts.

## Purpose

The covered APIs form the core early Hadoop filesystem client layer. They define how code locates filesystem implementations, opens seekable streams, creates files and directories, lists and globs paths, copies between local and remote filesystems, exposes block locations, preserves metadata, tracks I/O statistics, and adapts local, archive, FTP, in-memory, and KFS stores behind the same `FileSystem` abstraction.

The chunk also includes MapReduce-era distributed cache support for shipping read-only files, archives, and classpath resources to task nodes, plus NameNode JMX counters for startup, journal, block report, and operation metrics.

## Important APIs, Types, and Functions

`NameNodeStatistics` is partially visible. The visible methods expose the JMX implementation constructor, `shutdown()`, min/max/average/count getters for block reports, journal transactions, and journal syncs, startup metrics for safemode and FSImage load time, min/max reset, and operation counters for creates, deletes, adds, listings, block-location lookups, and renames. `getNumFilesListed()` is deprecated in favor of `getNumGetListingOps()`.

`NameNodeStatisticsMBean` is the public JMX management interface for NameNode runtime statistics. Its documented metrics are interval-based where applicable, with configuration notes for metrics contexts that perform periodic update calls. It references `FSNamesystemMBean` for status information outside this stats surface.

`DistributedCache` is a static utility for MapReduce application resources. `getLocalCache()` localizes a URI as a file or archive, validates the original modification timestamp, optionally unzips/unjars/untars archives, and can create symlinks in a task working directory. Configuration mutators and accessors cover cache files, cache archives, localized paths, timestamps, classpath additions, symlink enablement, URI conflict checks, `releaseCache()`, and `purgeCache()`.

Core metadata types include `BlockLocation`, `ContentSummary`, and `FileStatus`. `BlockLocation` is `Writable` state for hostnames, host:port names, file offset, and length. `ContentSummary` is `Writable` state for total content length, file count, directory count, and quota output formatting. `FileStatus` is `Writable` and `Comparable`, carrying file length, directory flag, replication, block size, modification time, permission, owner, group, and path; equality and hash code are path-based.

`FileSystem` is the central abstract API. It extends `Configured` and implements `Closeable`. Static factory and configuration methods include `get(Configuration)`, `get(URI, Configuration)`, deprecated `getNamed()`, `getLocal()`, `parseArgs()`, default URI getters/setters, `closeAll()`, and synchronized statistics lookup/printing. Instance methods define URI identity, path qualification/checking, block locations, `open()`, many `create()` overloads, `append()`, replication, rename, recursive/non-recursive delete, `deleteOnExit()`, existence/type/length/content-summary checks, `listStatus()` and `globStatus()`, home and working directories, `mkdirs()`, local copy/move helpers, local output staging, `close()`, usage/default block/default replication, file status, permissions, and ownership.

`FileSystem.Statistics` tracks bytes read and bytes written through increment and getter methods. `FileSystem.statistics` is a protected final field on each filesystem instance, and the static statistics registry is keyed by filesystem class.

Stream interfaces and wrappers define random-access and sync behavior. `Seekable` has `seek()`, `getPos()`, and `seekToNewSource()`. `PositionedReadable` has positional `read()` and `readFully()` overloads. `Syncable` declares `sync()`. `FSInputStream` combines `InputStream`, `Seekable`, and `PositionedReadable`; `BufferedFSInputStream` adds buffering around an `FSInputStream`; `FSDataInputStream` wraps an input stream as `DataInputStream` while delegating seek and positional reads. `FSDataOutputStream` wraps output as `DataOutputStream`, exposes `getPos()`, statistics-aware construction, wrapped stream access, close, and `sync()`.

Checksum support is split across `ChecksumException`, `ChecksumFileSystem`, `FSInputChecker`, and `FSOutputSummer`. `ChecksumFileSystem` wraps a raw filesystem and creates companion checksum files, calculates checksum-file lengths, filters checksum files from listings, keeps checksum and data files in sync across create/rename/delete/copy operations, and reports checksum failures. `FSInputChecker` verifies checksums chunk-by-chunk while reading and seeking. `FSOutputSummer` generates checksums before writing chunks to an underlying stream.

Utility APIs include `DF` and `DU` for shell-backed disk space and disk usage, `FileUtil` for recursive delete, filesystem copy, copy-merge, shell path conversion, local `du`, archive extraction, symlink/chmod, temp-file creation, and replace-file operations, plus `FileUtil.HardLink` for hardlink creation and link-count retrieval. `FsShell` provides command-line access to a `FileSystem` as a `Tool`, and `FsUrlStreamHandlerFactory` installs URL handlers backed by `FileSystem`.

Filesystem implementations and wrappers include `FilterFileSystem`, `HarFileSystem`, `InMemoryFileSystem`, `LocalDirAllocator`, `LocalFileSystem`, `RawLocalFileSystem`, `FTPFileSystem`, `FTPInputStream`, and `KosmosFileSystem`. `FilterFileSystem` delegates to an underlying `FileSystem`. `HarFileSystem` exposes Hadoop Archive contents as a read-oriented filesystem backed by `_masterindex`, `_index`, and `part-*` files. `InMemoryFileSystem` is a checksum filesystem for bounded `ramfs://` data with pre-reserved file and checksum space. `LocalDirAllocator` round-robins writes across configured local directories and searches them for reads. `LocalFileSystem` adds client-side checksums over `RawLocalFileSystem`; `RawLocalFileSystem` maps paths to `java.io.File`. `FTPFileSystem` uses Apache Commons Net FTP and has an explicit warning that input streams must be closed before other APIs are used. `KosmosFileSystem` adapts KFS and exposes block locations, locks, releases, local copy staging, and standard filesystem operations.

`Path` is the URI-backed path type with constructors for parent/child and scheme/authority/path combinations. It exposes `toUri()`, `getFileSystem()`, `isAbsolute()`, name/parent/suffix operations, string/equality/hash/compare/depth, qualification, and constants `SEPARATOR`, `SEPARATOR_CHAR`, and `CUR_DIR`. `PathFilter` is the predicate interface used by listing, globbing, local allocator, and in-memory filesystem selection.

`Trash` implements Hadoop's user trash behavior. It moves files into `.Trash/current` under the user's home directory while preserving original paths, creates checkpoints, expunges old checkpoints, and provides a superuser-oriented emptier runnable.

`AccessControlException` is an `IOException` subclass for permission failures, with a no-arg constructor needed for unwrapping from `RemoteException` and a message constructor.

## Control Flow

NameNode metrics flow from daemon-internal counters into `NameNodeStatistics`, then out through `NameNodeStatisticsMBean` via JMX. Interval metrics depend on a metrics context that periodically updates averages; `resetAllMinMax()` resets accumulated extrema.

Distributed cache flow starts when client code records file/archive URIs, timestamps, classpath entries, and symlink settings into a job `Configuration`. During task setup, localization calls resolve the URI through `FileSystem`, compare the DFS modification time to the job-time timestamp, copy the resource to a base cache directory if needed, unpack archives based on extension, record local paths, and optionally create symlinks in the task working directory. `releaseCache()` decrements or releases use of a localized cache, while `purgeCache()` deletes backing files during server reinitialization.

`FileSystem.get(URI, Configuration)` chooses an implementation from the URI scheme via the `fs.<scheme>.class` configuration key, constructs it, and calls `initialize()`. Caller operations then usually pass through convenience overloads into abstract primitives implemented by concrete filesystems. For example, simple `create()` overloads fill in default overwrite, buffer size, replication, block size, permission, and progress values before reaching the full abstract `create(Path, FsPermission, boolean, int, short, long, Progressable)`.

Listing and globbing flow through `FileStatus`. `listStatus()` returns status objects for paths and can apply a `PathFilter`. `globStatus()` interprets shell-like pattern operators (`?`, `*`, character classes, negated classes, escapes, and brace alternation), sorts results by path, returns `null` when a non-glob path does not exist, and returns an empty array when a glob has no matches.

Checksum filesystem flow wraps raw file operations. Opening a file creates a stream that reads data and checksum sidecar data; reads verify chunks and can raise `ChecksumException` with a bad position. Creating a file writes data through checksum generation and writes a matching checksum file. Rename, delete, copy, and list operations must keep checksum sidecar files aligned with user-visible files and hide checksum files where appropriate.

HAR flow initializes one `HarFileSystem` per archive URI, maps `har://` URIs to an underlying filesystem archive path, reads the master index to find ranges in the sorted index, then resolves file status, child listing, block locations, and open operations against part-file offsets. The open path returns a stream that fakes EOF at the archived member boundary.

Local allocation flow in `LocalDirAllocator` uses a context configuration key such as `mapred.local.dir`. For writes it round-robins from the last selected configured directory, checks writability and optionally available space, creates parents or temp files, and returns the chosen local path. For reads it scans all configured directories until the requested relative path exists.

FTP flow is more serialized than normal filesystem flow. The class documentation states that an input stream obtained from `open()` must be closed before using other APIs or later calls will block, implying a single active FTP data connection constraint.

## State and Persistence Behavior

The XML file is generated API metadata and has no runtime state, but many exposed APIs are stateful.

`DistributedCache` persists job resource declarations in `Configuration`: cache file/archive URIs, localized paths, timestamps, symlink settings, and classpath entries. Localized cache content persists on worker local disks until released, evicted, or purged. The timestamp contract assumes cached source files are read-only for the duration of the job.

`FileSystem` instances hold configuration, URI identity, working directory state in implementations, optional delete-on-exit registrations, and class-keyed byte statistics. `close()` releases held locks/resources, and `closeAll()` closes cached instances. `FSDataInputStream`, `FSDataOutputStream`, `FTPInputStream`, `FSInputChecker`, and `FSOutputSummer` track stream position, buffers, checksum state, and wrapped native/network resources.

`Writable` metadata types (`BlockLocation`, `ContentSummary`, `FileStatus`) serialize through `DataOutput`/`DataInput`. This makes their field order and default/null handling compatibility-sensitive for RPCs and stored metadata using Hadoop writable serialization.

`ChecksumFileSystem` persists extra checksum files alongside data files, so every data mutation has a sidecar consistency requirement. `LocalFileSystem.reportChecksumFailure()` moves corrupt local files to a bad-file directory on the same device so their storage is not reused.

`HarFileSystem` is read mostly from immutable archive files. Its namespace and file metadata are derived from archive index files rather than full per-file persisted permissions; Javadocs state returned permissions are those of archive index files because permissions are not persisted when creating a Hadoop archive.

`InMemoryFileSystem` stores file data in process memory and requires callers to reserve space, including checksum space, before creating files. It tracks total filesystem size, number of files, selected paths, and percent used.

`LocalDirAllocator` keeps JVM-local allocator state per context, including the last directory selected for round-robin allocation. It does not handle disks becoming read-only or full while a file is already being written.

`Trash` persists moved files under `.Trash/current` plus checkpoint directories. Its design avoids requiring full trash enumeration, filesystem date support, or synchronized clocks.

## Dependencies and Integration Points

The chunk integrates `org.apache.hadoop.conf.Configuration`, `Configured`, `org.apache.hadoop.util.Tool`, `Progressable`, `Shell`, Hadoop `Writable` serialization, `org.apache.hadoop.fs.permission.FsPermission`, `java.net.URI`, `java.net.URLStreamHandlerFactory`, `java.io` streams/files, `java.util.zip.Checksum`, and Apache Commons Logging.

MapReduce integration appears through `DistributedCache` documentation and APIs referencing `JobConf`, `JobClient`, `Mapper`, `Reducer`, `OutputCollector`, and `Reporter`. The cache is a bridge between job configuration, HDFS or HTTP resources, local task working directories, archive utilities, symlink creation, and task classpaths.

Filesystem implementation selection is configuration-driven through `fs.<scheme>.class`. Concrete schemes represented here include local/raw local, HAR, in-memory `ramfs://`, FTP via Apache Commons Net, and KFS/Kosmos. DFS and DistributedFileSystem are referenced as integration targets but their declarations are outside this chunk.

Shell integration is substantial in this early API: `DF`, `DU`, `ShellCommand`, `FileUtil.symLink()`, `FileUtil.chmod()`, `RawLocalFileSystem.setOwner()`, and `RawLocalFileSystem.setPermission()` all expose behavior backed by platform commands.

JMX and metrics integration is represented by `NameNodeStatisticsMBean`; URL integration by `FsUrlStreamHandlerFactory`; CLI integration by `FsShell` and its `Tool` implementation; IPC/remote exception integration by `AccessControlException`'s no-arg constructor.

## Risks and Edge Cases

This is an old Hadoop public API snapshot with several deprecated methods. Deprecated surfaces include `NameNodeStatisticsMBean.getNumFilesListed()`, `FileSystem.getName()`, `FileSystem.getNamed()`, path-based `getFileBlockLocations(Path, long, long)`, `FileSystem.getBlockSize()`, `RawLocalFileSystem.getName()`, `RawLocalFileSystem.lock()/release()`, `ShellCommand`, and single-argument delete methods in some implementations. Compatibility code may still depend on them.

Distributed cache correctness depends on stable source modification times and unique URI fragments when symlinks are enabled. Missing fragments, duplicate fragments, mutation of source files while a job is running, archive extraction failures, path traversal in archives, and aggressive `purgeCache()` can all affect task correctness or local disk safety.

`FileSystem` factories and caches can leak resources if callers hold instances past `closeAll()` or use closed cached filesystems. `deleteOnExit()` can accumulate state in long-lived JVMs. `setOwner()` explicitly rejects both username and group being null.

Glob and listing behavior has subtle null-versus-empty semantics, sorted result expectations, checksum-file filtering, and filter ordering. Tests and callers must distinguish nonexistent literal paths from unmatched glob patterns.

Checksum sidecar files create consistency risk: a data file copied, renamed, deleted, or listed without matching checksum handling can produce false checksum failures or expose internal `.crc`-style files. Checksum verification can raise during `read()`, `skip()`, or `seek()` because those operations may touch the target chunk.

`FSInputStream.seek()` says it cannot seek past EOF, while `FSInputChecker.seek()` allows seeking past EOF and returns `-1` on later read. Implementations and callers need to preserve the more specific contract for the concrete stream type they use.

`HarFileSystem` is not a general writable filesystem. Many mutating operations are documented as not implemented, and permissions returned from archive members do not reflect original per-file permissions. Creating one filesystem instance per `Path.getFileSystem()` call is explicitly warned against for HAR archives.

`LocalDirAllocator` does not protect against a disk becoming full or read-only after allocation. It also relies on JVM-local context singletons, so stale configuration or context reuse can affect later allocations.

FTP support has blocking hazards if streams are left open before later filesystem calls. It also lacks append support and depends on FTP server semantics for rename, delete, directory listing, and status details.

KFS and FTP adapters expose the common `FileSystem` contract over external systems whose replication, block locations, locks, permissions, and local copy semantics may diverge from HDFS behavior.

Shell-backed utilities are OS-sensitive. Javadocs mention Linux, FreeBSD, Cygwin, and Windows XP support in specific places, so command output parsing, symlink support, chmod/chown behavior, and hardlink counts need platform-specific validation.

## Test Signals

NameNode metrics tests should verify JMX registration/shutdown, interval counters, min/max reset, deprecated and replacement listing counters, safemode and FSImage load times, and behavior when no updating metrics context is configured.

Distributed cache tests should cover configuration round trips for files, archives, timestamps, classpath entries, localized paths, symlink flags, fragment conflict detection, timestamp mismatch rejection, cache reuse versus copy, archive extraction for `.zip`, `.jar`, `.tar`, `.tgz`, and `.tar.gz`, `releaseCache()`, and guarded `purgeCache()`.

Core `FileSystem` tests should exercise scheme-based implementation loading, default URI handling, cached instance close/closeAll behavior, path qualification/checking, all create/open/append overload paths, overwrite behavior, recursive and non-recursive delete, delete-on-exit processing, rename semantics, permissions and owner changes, content summaries, block locations, home and working directory resolution, and statistics increments for bytes read/written.

Listing and glob tests should verify path filters, multi-path listings, checksum-file exclusion, sort order, literal-missing `null`, glob-no-match empty array, escaping, character classes, negation, ranges, and nested brace expansion.

Writable metadata tests should round-trip `BlockLocation`, `ContentSummary`, and `FileStatus`, including empty hosts/names, quota output formatting, default permission/owner/group fallback, path-based equality, and compare ordering.

Checksum tests should cover checksum filename detection, checksum length calculations, create/open round trips, sidecar rename/delete/copy behavior, listing filters, `reportChecksumFailure()`, corrupted data and corrupted checksum streams, seek/skip across chunk boundaries, EOF behavior, and `FSOutputSummer` direct-write versus buffered chunk paths.

Stream tests should verify seek, position, positioned read, `readFully()` short-read handling, `seekToNewSource()`, sync delegation, statistics-aware output streams, closed-stream behavior, and mark/reset unsupported behavior where declared.

Utility tests should cover `DF` and `DU` parsing on supported platforms, refresh thread start/shutdown, manual inc/dec usage accounting, recursive delete partial failure, filesystem-to-filesystem copy and copy-merge, local-to-remote and remote-to-local copy, archive extraction, symlink/chmod exit codes, hardlink creation/link counts, temp-file delete-on-exit, and replace-file failure handling.

Implementation-specific filesystem tests should cover `FilterFileSystem` delegation, `HarFileSystem` index lookup and read-only operation failures, `InMemoryFileSystem.reserveSpaceWithCheckSum()` success/failure and percent-used accounting, `LocalDirAllocator` round-robin and space-aware selection, `LocalFileSystem` checksum failure quarantine, `RawLocalFileSystem` path-to-file conversion and shell-backed owner/permission changes, FTP open-stream blocking constraints and unsupported append, and KFS block locations/locks/replication behavior.

`Path`, `PathFilter`, `FsShell`, `FsUrlStreamHandlerFactory`, `Trash`, and `AccessControlException` tests should cover URI constructors and normalization, parent/name/suffix/depth/qualification, filter acceptance wiring, shell initialization/run/close and byte formatting helpers, URL handler creation only for known schemes, trash disabled/already-in-trash returns, checkpoint/expunge/emptier behavior, and remote-exception unwrapping of access-control failures.

## Cross-Chunk Notes

The chunk starts mid-`NameNodeStatistics`; its class declaration and any earlier fields or methods are in the preceding chunk. The final report should merge this with the previous NameNode metrics chunk for a complete description of the implementation class.

The chunk ends before `FsAction`; the permission enum/action API and likely `FsPermission` details are in a following chunk, even though many APIs here depend on `FsPermission`.

Several referenced types are declared outside this chunk, including `DistributedFileSystem`, `FSNamesystemMBean`, `FsPermission`, `Progressable`, `Shell`, `Tool`, MapReduce `JobConf` and mapper/reducer types, and KFS/FTP implementation internals. The merge lane should connect those declarations to this filesystem API surface.
