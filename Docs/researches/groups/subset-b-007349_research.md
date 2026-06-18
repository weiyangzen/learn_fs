# Research: subset-b-007349

This grouped report covers Hadoop `org.apache.hadoop.fs.shell` command implementations, the shell `find` expression subsystem, and selected `org.apache.hadoop.fs.statistics` contracts. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandWithDestination.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandWithDestination.java

Purpose: abstract base for shell commands that combine one or more sources with a destination, including `cp`, `put`, `get`, `appendToFile`, and `mv`. It validates destination arity rules, maps source paths to target paths, copies files, creates recursive destination directories, and optionally preserves metadata.

Important APIs and types: `getLocalDestination()`, `getRemoteDestination()`, `processArguments()`, `processPathArgument()`, `processPath(src,dst)`, `recursePath()`, `getTargetPath()`, `copyFileToTarget()`, `copyStreamToTarget()`, `preserveAttributes()`, `FileAttribute`, and private `TargetFileSystem`. Flags include overwrite, checksum verify/write, lazy persist, direct write, and an `EnumSet<FileAttribute>` for timestamps, ownership, permissions, ACLs, and xattrs.

Control flow: subclasses parse options and set `dst`, then `processArguments()` enforces that multi-source copies target an existing directory and that single-source copies do not overwrite unless allowed. `processPathArgument()` prevents copying a directory into itself on the same filesystem. File paths copy through `openFile(...WHOLE_FILE...)`, `copyStreamToTarget()`, and metadata preservation; recursive directory paths temporarily replace `dst` with the current target directory, create missing directories, recurse through `FsCommand`, and then preserve directory metadata.

State and persistence: no durable internal state is kept, but operations mutate target filesystems by creating files, renaming temporary `._COPYING_` files, deleting overwrite targets, setting times/owner/group/permissions/ACLs/xattrs, and creating directories. `TargetFileSystem` uses `deleteOnExit`/`cancelDeleteOnExit` and `processDeleteOnExit()` to clean incomplete temp files without closing the underlying filesystem.

Dependencies and integration: extends `FsCommand`, uses `PathData` for resolved path/status/fs triples, `FileSystem.openFile()` with `FutureIO.awaitFuture`, Hadoop `FSDataOutputStream`, `CreateFlag`, ACL and xattr APIs, and viewfs `NotInMountpointException` handling for lazy persist block size lookup. It is the shared integration point for all copy/move-like shell commands.

Risks: raw xattr preservation is guarded by both source and target living under `/.reserved/raw`; mismatched paths throw. Direct write skips temporary-file atomicity and may expose partial files. Symlinks are rejected rather than copied or dereferenced. `TargetFileSystem.rename()` deletes an existing target before rename, so failure between delete and rename can lose the old target when overwrite is enabled. Preserving ACLs also sets base permission first. Lazy persist forces replication factor 1 and depends on filesystem support.

Test signals: tests should cover multi-source destination validation, overwrite/direct/lazy combinations, self-copy and subdirectory-copy rejection, raw xattr path combinations, preservation of each `FileAttribute`, Windows local destination parsing, temp cleanup on copy failure, and viewfs lazy-persist fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandWithDestination.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Concat.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Concat.java

Purpose: implements `-concat`, a shell command that appends multiple existing source files into an existing target file through `FileSystem.concat()`.

Important APIs and types: `Concat.registerCommands()`, constants `NAME`, `USAGE`, `DESCRIPTION`, `processArguments()`, and test-only `setTestFs(FileSystem)`.

Control flow: `processArguments()` requires a target plus at least two source paths, removes the first argument as target, validates that target and every source exist and are files, builds a `Path[]` of source paths, selects `target.fs` or injected `testFs`, and calls `fs.concat(target.path, srcArray)`.

State and persistence: the command mutates the target filesystem by concatenating source block data into the target according to the filesystem's native concat semantics. The only class state is static `testFs`, used to inject a filesystem in tests.

Dependencies and integration: extends `FsCommand`, consumes `PathData` produced by command argument expansion, delegates all actual file mutation to `FileSystem.concat()`, and maps unsupported filesystems into `PathIOException` with scheme context.

Risks: it relies on the filesystem to enforce same-directory, block-size, checksum, and source removal semantics; this class only validates existence and file type. Static `testFs` can leak across tests if not reset. Error messages use source/target `Path` strings, not original user path spellings.

Test signals: cover missing target, fewer than two sources, nonexistent/non-file sources, unsupported filesystem exception mapping, success delegation to `concat()`, and cleanup/reset of injected `testFs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Concat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CopyCommandWithMultiThread.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CopyCommandWithMultiThread.java

Purpose: adds optional bounded thread-pool execution to `CommandWithDestination` file copies for commands such as `cp`, `get`, and `put`.

Important APIs and types: `setThreadCount()`, `setThreadPoolQueueSize()`, visible-for-testing getters, `processArguments()`, `isMultiThreadNecessary()`, and override `copyFileToTarget()`. Internal state is `threadCount`, `threadPoolQueueSize`, and `ThreadPoolExecutor executor`; `DEFAULT_QUEUE_SIZE` is 1024.

Control flow: option parsers call setters. `processArguments()` initializes an executor only when `threadCount > 1` and there are multiple source paths or a single recursable source. It then runs normal destination processing and waits for executor termination. `copyFileToTarget()` either executes synchronously or submits a task that calls the superclass and reports `IOException` through `displayError()`.

State and persistence: executor state exists only during one command run. Persistent effects are inherited copy writes. Queue backpressure uses `ArrayBlockingQueue` and `CallerRunsPolicy`, so traversal threads may perform copies directly when the queue is full.

Dependencies and integration: extends `CommandWithDestination`, uses inherited recursion and target mapping, and wraps only file copy calls. The command traversal and directory creation still occur in the caller thread.

Risks: worker task exceptions are displayed but not rethrown from `waitForCompletion()`, so exit-code behavior depends on `displayError()` side effects and can be subtle. Concurrent copies share command instance fields inherited from `CommandWithDestination`; target `PathData` values are passed per task, but inherited output/error streams and filesystem clients must tolerate concurrency. Interrupted waits call `shutdownNow()` and restore interrupt status.

Test signals: cover invalid/zero/negative thread and queue options, single-file no-thread optimization, recursive directory enabling threads, queue fallback behavior, worker exception exit-code accounting, and interrupted wait handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CopyCommandWithMultiThread.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CopyCommands.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CopyCommands.java

Purpose: registers and implements copy-family shell commands: `getmerge`, `cp`, `get`, `put`, `copyFromLocal`, `copyToLocal`, and `appendToFile`.

Important APIs and types: outer `registerCommands()`, nested `Merge`, `Cp`, `Get`, `Put`, alias classes `CopyFromLocal`/`CopyToLocal`, and `AppendToFile`. It relies heavily on `CommandWithDestination` and `CopyCommandWithMultiThread` for common destination validation and copying.

Control flow: `Merge` parses newline and empty-file-delimiter options, collects valid source files before opening the local destination, then streams each source sequentially in sorted order. `Cp` parses `-f`, `-d`, `-p[topax]`, thread options, sets recursive copy, and resolves a remote destination. `Get` resolves a local destination, controls checksum verification and local CRC sidecar writes, and can preserve basic metadata. `Put` resolves a remote destination, expands local paths without globbing, supports stdin as a sole `-` source, lazy persist, direct write, overwrite, preservation, and threading. `AppendToFile` creates the remote destination if missing, opens append or new-block append, and streams stdin or local files into it.

State and persistence: commands write local or remote files, append existing remote files, optionally create CRC files, preserve metadata, and create temp `._COPYING_` targets unless direct write is requested. `Merge` keeps `srcs` until all path collection succeeds to avoid partial merged output after a later bad path.

Dependencies and integration: uses `CommandFormat`, `PathData`, `FSDataInputStream`, `FSDataOutputStream`, Java NIO `Files` for local append sources, and `IOUtils.copyBytes()`. It integrates with Hadoop shell command registration via `CommandFactory`.

Risks: `Put` stdin special case passes a synthetic `PathData` for `-` to `getTargetPath()`, so destination naming is sensitive to inherited target logic. `AppendToFile` rejects stdin mixed with file inputs only after destination creation/opening. Threaded copy inherits asynchronous exception aggregation risks. Direct write skips temp-file protection. `Merge` creates/truncates destination only after path collection, but errors during streaming still leave partial local output.

Test signals: cover all option combinations, preserve parsing including `-p` and `-pa`, Windows/local URI parsing, stdin-only `put` and append, `appendToFile -n`, merge delimiter behavior with empty files, source directory recursion depth for merge, and threaded copy error exit codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CopyCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Count.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Count.java

Purpose: implements `-count`, reporting directory/file/byte counts, quotas, storage-type quota usage, erasure coding policy, and snapshot counts for paths.

Important APIs and types: `processOptions()`, `getAndCheckStorageTypes()`, `processPath()`, and package-private test accessors. Flags include `-q`, `-h`, `-v`, `-t`, `-u`, `-x`, `-e`, and `-s`.

Control flow: options are parsed first and default path `.` is added when no path remains. Quota modes parse optional storage types and disable snapshot exclusion. Optional header output is assembled from `ContentSummary` or `QuotaUsage` static header helpers plus EC/snapshot columns. `processPath()` calls either `fs.getQuotaUsage()` or `fs.getContentSummary()` and appends optional EC and snapshot strings before the path.

State and persistence: command state is per-run booleans and storage-type list only. No filesystem mutation occurs.

Dependencies and integration: extends `FsCommand`; uses `ContentSummary`, `QuotaUsage`, `StorageType`, Hadoop and commons `StringUtils`, and the `FsShell` deprecated constructor path for compatibility.

Risks: multiple optional columns can trigger repeated `getContentSummary()` calls per path. `-t` is ignored unless quota output is enabled. Snapshot exclusion is intentionally ignored under quota modes with a printed notice. Invalid storage-type strings propagate parse failures.

Test signals: cover default path, headers for every mode, human-readable formatting, type-list parsing including `all`/empty, `-x` interaction with quota modes, EC/snapshot appended columns, and invalid storage type errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Count.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Delete.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Delete.java

Purpose: registers delete-related commands `rm`, `rmdir`, deprecated `rmr`, and `expunge`.

Important APIs and types: nested `Rm`, `Rmr`, `Rmdir`, and `Expunge`; `Rm.processOptions()`, `expandArgument()`, `processPath()`, `canBeSafelyDeleted()`, `moveToTrash()`; `Rmdir.processPath()`; `Expunge.processArguments()`.

Control flow: `Rm` parses force, recursive, trash bypass, and safe-delete flags. It suppresses nonexistent glob errors under `-f`, rejects directories unless recursive, attempts trash unless skipped, optionally counts files via `ContentSummary` and confirms large deletes, then calls `fs.delete(path, deleteDirs)`. `Rmr` injects `-r` and advertises replacement. `Rmdir` deletes only empty directories unless `--ignore-fail-on-non-empty` is set. `Expunge` optionally changes `fs.defaultFS`, iterates child filesystems if present, and calls `Trash.expunge()`/`checkpoint()` or immediate expunge.

State and persistence: these commands remove files/directories or trash checkpoints, and may update trash directories. State is per-command flags.

Dependencies and integration: uses `Trash`, `ContentSummary`, `ToolRunner.confirmPrompt`, `CommonConfigurationKeysPublic`, `FileSystem.getChildFileSystems()`, and path-specific Hadoop exceptions.

Risks: `rm` comments note a historical concern that trash failures can lead to direct deletion in some patterns, although current `moveToTrash()` rethrows most IO failures with a `-skipTrash` hint. Safe delete counts content before deleting and can be slow. `-f` on nonexistent globs returns an empty list, which affects user diagnostics. `Expunge -fs` mutates configuration default FS for the command.

Test signals: cover `-f` nonexistent behavior, recursive and nonrecursive directory deletes, trash success/failure, safe-delete confirmation yes/no and threshold zero, empty/nonempty `rmdir`, expunge child-filesystem iteration, and immediate expunge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Delete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Display.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Display.java

Purpose: implements display commands `cat`, `text`, and `checksum`, plus stream adapters for SequenceFile and Avro-to-text rendering.

Important APIs and types: nested `Cat`, `Text`, `Checksum`, `TextRecordInputStream`, `AvroFileInputStream`, and `validateInputStreamReadArguments()`. `Cat` handles checksum verification and stdout copy; `Text` detects gzip, SequenceFile, codec-compressed streams, and Avro data files; `Checksum` prints algorithm/hash and optionally block size.

Control flow: `Cat.processPath()` rejects directories, configures checksum verification, opens sequential input via `PathData.openForSequentialIO()`, and copies to `out`. `Text.getInputStream()` reads lead bytes, seeks back as needed, and wraps the stream with gzip/codec readers or container readers. `TextRecordInputStream` converts SequenceFile key/value records into tab-separated text lines. `AvroFileInputStream` serializes Avro records through a JSON encoder into a byte buffer consumed by `read()`.

State and persistence: no filesystem mutation occurs. Stream classes keep reader state, buffers, and current positions until close.

Dependencies and integration: uses Hadoop compression codecs, `SequenceFile.Reader`, Avro `DataFileReader`, `AvroFSInput`, `FileContext`, `FileChecksum`, and `PathData`.

Risks: `Text.getInputStream()` must close or rewind correctly after probing lead bytes; SequenceFile and Avro detection is magic-byte based. `AvroFileInputStream` creates a new default `Configuration` for `FileContext`, not the command's configuration. Large records are buffered fully in memory for each record. `read(byte[],...)` validation intentionally mirrors `InputStream` contract but throws unchecked exceptions for null/range issues.

Test signals: cover directory rejection, `-ignoreCrc`, gzip and codec detection, short/empty files, SequenceFile text conversion, Avro JSON conversion including empty and final newline behavior, checksum null and verbose output, and buffer read argument validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Display.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/FsCommand.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/FsCommand.java

Purpose: base class and registry hub for `hadoop fs` shell commands.

Important APIs and types: static `registerCommands(CommandFactory)`, protected constructors, `getCommandName()`, deprecated `runAll()`, unsupported `run(Path)`, and `processRawArguments()`.

Control flow: registration delegates to command groups including ACL, copy, count, delete, display, find, permissions, usage, listing, mkdir, move, replication, stat, tail/head, test, touch, truncate, snapshots, xattr, and concat. At runtime `processRawArguments()` expands raw strings to `PathData`, optionally warns when `fs.defaultFS` is unset/default, then calls `processArguments()`.

State and persistence: no additional persistent state beyond inherited `Command` fields. It only reads configuration and emits warnings.

Dependencies and integration: extends `Command`, imports `FsShellPermissions` and `find.Find`, and consumes common configuration keys `fs.defaultFS` and shell missing-default-FS warning settings.

Risks: all registered command availability depends on this central list. `run(Path)` intentionally throws and should not be used. The variable `expendedArgs` is a typo but harmless. Warning behavior can affect stderr-sensitive scripts unless configuration disables it.

Test signals: verify command registration coverage, default-FS warning enabled/disabled behavior, default command-name compatibility, and deprecated `runAll()` delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/FsCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/FsUsage.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/FsUsage.java

Purpose: implements filesystem usage commands `df`, `du`, and deprecated `dus`, with aligned table formatting.

Important APIs and types: outer `formatSize()`, `TableBuilder`, nested `Df`, `Du`, and `Dus`. `Df` reports `FsStatus`; `Du` reports `ContentSummary` length and space consumed.

Control flow: `Df` defaults to `/`, creates a six-column table, then for viewfs uses `ViewFileSystemUtil.getStatus()` to report mount-point target status and mounted-on path; non-viewfs hides the mounted-on column and reports `item.fs.getStatus()`. `Du` defaults to `.`, optionally shows headers, recurses one level for command-line directories unless summary mode is enabled, subtracts snapshot length/space under `-x`, and appends rows. `TableBuilder` computes column widths and prints aligned visible columns.

State and persistence: no filesystem mutation. Per-run state includes human-readable flag and collected table rows.

Dependencies and integration: uses `PathData`, `FsStatus`, `ContentSummary`, viewfs classes, and `StringUtils.TraditionalBinaryPrefix`.

Risks: table rows are accumulated before printing, so very large result sets can hold memory until completion. `Df` percentage divides used by size; zero-capacity filesystems need attention. Viewfs handling assumes mount target URI array has at least one element. `Du` content summaries may be expensive and only go one level deep unless inherited recursion changes.

Test signals: cover human-readable output, viewfs and non-viewfs columns, hidden column formatting, `du -s/-v/-x`, default paths, one-level directory recursion, and zero/edge capacity formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/FsUsage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Head.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Head.java

Purpose: implements `-head`, printing the first 1024 bytes of a single file.

Important APIs and types: `processOptions()`, custom `expandArgument()`, `processPath()`, and private `dumpToOffset()`.

Control flow: option parsing enforces exactly one argument. Expansion constructs a direct `PathData` without glob expansion. `processPath()` rejects directories and `dumpToOffset()` opens the file with sequential read policy and copies up to `endingOffset` bytes to `System.out`.

State and persistence: no mutation. `endingOffset` is fixed at 1024.

Dependencies and integration: extends `FsCommand`, uses `PathData.openFile(FS_OPTION_OPENFILE_READ_POLICY_SEQUENTIAL)`, `FSDataInputStream`, and `IOUtils.copyBytes()`.

Risks: output goes to `System.out` rather than inherited `out`, which matters for tests or embedded shells that redirect command streams. Glob support is intentionally absent via direct expansion. Small files simply copy less data.

Test signals: cover one-arg enforcement, directory rejection, short file, exact/long file truncation, non-glob behavior, and output stream expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Head.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Ls.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Ls.java

Purpose: implements `-ls` and deprecated `-lsr`, listing files/directories with formatting, sorting, recursion, path-only output, printable-name filtering, and optional erasure coding policy.

Important APIs and types: `processOptions()`, visible-for-testing flag getters, `processPathArgument()`, `isSorted()`, `getListingGroupSize()`, `processPaths()`, `processPath()`, `adjustColumnWidths()`, and `initialiseOrderComparator()`.

Control flow: options set recursion, directory-as-file behavior, human-readable sizes, non-printable filtering, sort order, atime display, and EC policy display. Default path is `.`. Command-line directories are implicitly recursed once unless `-d` is specified. `processPaths()` prints item counts for nonrecursive directory listings, sorts as needed, updates column widths, and delegates item output. `processPath()` prints either only path or a formatted line with type, permissions, ACL marker, replication, owner, group, optional EC policy, size, date, and path.

State and persistence: no mutation. Formatting widths and comparator are instance state and grow across processed groups.

Dependencies and integration: uses `PathData`, `FileStatus`, `ContentSummary` for EC policy, `PrintableString`, `StringUtils.TraditionalBinaryPrefix`, and inherited recursive listing from `FsCommand`/`Command`.

Risks: EC policy display calls `getContentSummary()` for each path and rejects filesystems that return null on the initial argument. Width state can persist across groups in one command run. Recursive listing uses group size 100 unless path-only; sorting falls back to non-iterator paths when explicit sorting or summary printing is needed. `-S` is ignored when `-t` is also set due precedence.

Test signals: cover default output, `-C`, `-d`, `-R`, `-h`, `-q`, `-t`, `-S`, `-r`, `-u`, `-e`, lsr replacement, ACL marker, EC unsupported path, recursive grouping, and comparator precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Ls.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Mkdir.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Mkdir.java

Purpose: implements `-mkdir`, creating directories with optional parent creation.

Important APIs and types: `processOptions()`, `processPath()`, and `processNonexistentPath()`.

Control flow: options require at least one path and parse `-p`. Existing paths are accepted only if they are directories and `-p` is set; existing files cause `PathIsNotDirectoryException`. Missing paths require existing parent unless `-p`, then call `fs.mkdirs()`.

State and persistence: mutates filesystem by creating directories. State is only `createParents`.

Dependencies and integration: extends `FsCommand`, uses `PathData`, `Path`, and Hadoop path exceptions.

Risks: parent validation has special handling for root/null parent. `fs.mkdirs()` false produces generic `PathIOException` without detailed cause. With `-p`, existing directories are silently accepted.

Test signals: cover missing args, existing directory with and without `-p`, existing file, missing parent with and without `-p`, root edge case, and failed `mkdirs()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Mkdir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/MoveCommands.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/MoveCommands.java

Purpose: registers move commands `moveFromLocal`, unimplemented `moveToLocal`, and `mv`.

Important APIs and types: nested `MoveFromLocal`, `MoveToLocal`, and `Rename`. `MoveFromLocal` extends `CopyFromLocal`; `Rename` extends `CommandWithDestination`.

Control flow: `MoveFromLocal` rejects `-t`, delegates `put`-style copy options, refuses to merge into an existing target directory, and deletes the local source in `postProcessPath()` after copy. `MoveToLocal.processOptions()` always throws not implemented. `Rename` parses source/destination, resolves remote destination, validates source and target filesystem scheme/host strings match, rejects existing targets, and calls `target.fs.rename()`.

State and persistence: `MoveFromLocal` creates remote targets and deletes local sources. `Rename` mutates filesystem namespace through rename. No durable internal state.

Dependencies and integration: reuses `CopyCommands.CopyFromLocal`, `CommandWithDestination`, `PathData`, and path exceptions.

Risks: `MoveFromLocal` delete happens after copy, so partial success can leave both source and target if delete fails. `mv` filesystem equality compares only scheme and host, not port, authority details, or filesystem implementation identity. `mv` rejects overwrite unconditionally. `moveToLocal` is registered but always fails.

Test signals: cover `moveFromLocal` delete-after-copy, target directory rejection, `-t` rejection, `moveToLocal` not implemented, `mv` cross-filesystem rejection including authority edge cases, existing target rejection, and failed rename mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/MoveCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/PathData.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/PathData.java

Purpose: encapsulates a user path string, qualified `Path`, `FileSystem`, `FileStatus`, and existence flag while preserving user-facing path spelling better than `Path.toString()` alone.

Important APIs and types: constructors from `String` and local `URI`, `refreshStatus()`, `suffix()`, `parentExists()`, `representsDirectory()`, `getDirectoryContents()`, `getDirectoryContentsIterator()`, `getPathDataForChild()`, static `expandAsGlob()`, `toFile()`, `openForSequentialIO()`, and `openFile(policy)`.

Control flow: construction parses strings through `stringToUri()`, resolves filesystem, qualifies paths, and optionally looks up status. Glob expansion uses `fs.globStatus()`: null means non-glob missing path and returns one non-existing `PathData`; matches are converted back to schemeful, absolute schemeless, or relative strings based on input form. Directory listing preserves relative child strings, sorts array results, and offers iterator mapping for scalable listings.

State and persistence: `stat` and `exists` are mutable cached status values refreshed by `refreshStatus()`. No filesystem mutation occurs except indirectly through status/list/open calls.

Dependencies and integration: central to nearly every shell command. Uses `FileSystem`, `LocalFileSystem`, `RemoteIterator`, `FutureIO.awaitFuture`, open-file read policy and length options, Hadoop path exceptions, and custom URI parsing for `?`, `#`, Windows drive paths, and relative glob results.

Risks: cached `stat` can become stale unless refreshed. URI parsing intentionally differs from `new URI(String)` and must be regression-tested for Windows, escaped glob chars, schemes without authorities, relative paths, and paths containing URI-reserved characters. `toFile()` is valid only for `LocalFileSystem`. `compareTo()`/`equals()` use qualified `Path`, not preserved user string.

Test signals: cover missing path construction, glob null/empty/multiple behavior, relative and schemeful glob spelling, Windows absolute and backslash paths, directory child string preservation, `representsDirectory()` for slash/dot/dotdot, stale status refresh after delete/create, iterator listing, and open-file options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/PathData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/PrintableString.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/PrintableString.java

Purpose: converts a raw string to a printable form by replacing selected non-printable Unicode categories with `?`.

Important APIs and types: constructor `PrintableString(String)` and `toString()`. It scans Unicode code points and checks `Character.getType()`.

Control flow: for each code point it replaces control, format, private-use, surrogate, and unassigned categories with `REPLACEMENT_CHAR`; otherwise it appends the original code point.

State and persistence: immutable wrapper around the computed `printableString`; no external mutation.

Dependencies and integration: used by `Ls -q` to hide non-printable path characters while preserving printable Unicode.

Risks: category-based filtering may replace some invisible but meaningful characters and preserve others that terminals render oddly. Surrogate handling is based on code point iteration; malformed surrogate input is categorized as surrogate and replaced.

Test signals: cover ASCII pass-through, control characters, private-use, formatting marks, unassigned/surrogate cases, supplementary printable code points, and integration with `Ls`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/PrintableString.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/SetReplication.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/SetReplication.java

Purpose: implements `-setrep`, recursively setting file replication and optionally waiting until block locations reflect the requested replication.

Important APIs and types: `processOptions()`, `processArguments()`, `processPath()`, and private `waitForReplication()`. State includes `newRep`, `waitList`, and `waitOpt`.

Control flow: parses `-R` for compatibility and `-w`, requires positive short replication, and always enables recursion. `processPath()` rejects symlinks, ignores directories directly, skips erasure-coded files, calls `fs.setReplication()`, prints status, and enqueues files when waiting. `waitForReplication()` polls `refreshStatus()` and `getFileBlockLocations()` every 10 seconds until every block's host count equals `newRep`.

State and persistence: mutates file replication metadata on supported filesystems. Wait state is in-memory list of files processed successfully.

Dependencies and integration: uses `BlockLocation`, `PathData`, and inherited recursive traversal.

Risks: waiting can run indefinitely if replication never converges. Host-count comparison may not capture all filesystem replication semantics. Interrupted sleeps are swallowed. EC files are intentionally skipped. Decreasing replication prints a warning only once per file.

Test signals: cover invalid replication, symlink rejection, EC skip, directory recursion, failed `setReplication()`, wait success, wait warning on decrease, and interruption behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/SetReplication.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/SnapshotCommands.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/SnapshotCommands.java

Purpose: registers snapshot commands `createSnapshot`, `deleteSnapshot`, and `renameSnapshot`.

Important APIs and types: nested `CreateSnapshot`, `DeleteSnapshot`, `RenameSnapshot`; each parses arguments, validates the root path is a directory, and performs one filesystem snapshot operation in `processArguments()`.

Control flow: create accepts directory plus optional snapshot name, validates argument count, and calls `fs.createSnapshot()`. Delete accepts exactly directory and snapshot name and calls `fs.deleteSnapshot()`. Rename accepts directory, old name, and new name and calls `fs.renameSnapshot()`. All commands first let superclass path processing validate the single root and abort mutation when `numErrors != 0`.

State and persistence: mutates snapshot metadata on the target filesystem. Per-run state stores snapshot name(s).

Dependencies and integration: extends `FsCommand`, uses `PathData`, `PathIsNotDirectoryException`, and `Preconditions.checkArgument()` for final invariant checks.

Risks: argument parsing removes snapshot names before path expansion; snapshot names are not otherwise validated here. Filesystem-specific errors propagate. Uses `assert` in two commands and `Preconditions` in one for size invariant, but mutation relies on prior argument-count checks.

Test signals: cover wrong argument counts, non-directory roots, successful create/delete/rename, superclass error abort, optional create name, and filesystem exception propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/SnapshotCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Stat.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Stat.java

Purpose: implements `-stat`, printing selected `FileStatus` fields according to a lightweight percent-format string.

Important APIs and types: `processOptions()`, `processPath()`, `timeFmt`, and default `format = "%y"`. Supports `%a`, `%A`, `%b`, `%F`, `%g`, `%n`, `%o`, `%r`, `%u`, `%x`, `%X`, `%y`, and `%Y`.

Control flow: parses optional `-R`, treats first argument containing `%` as the format, then requires at least one path. `processPath()` scans characters, expands recognized format sequences, drops a trailing `%`, and leaves unknown sequence letters without the `%`.

State and persistence: no mutation. Per-command state is format string and date formatter.

Dependencies and integration: extends `FsCommand`, consumes `PathData.stat`, and uses `SimpleDateFormat` for access/modification times.

Risks: formatting is not POSIX-complete; unknown escapes lose `%`, and trailing `%` is silently dropped. `SimpleDateFormat` uses default timezone despite help saying UTC dates. Format detection by `contains("%")` can misclassify path strings containing `%` as a format if placed first.

Test signals: cover all format tokens, recursive option, default format, unknown/trailing percent behavior, timezone expectations, path containing `%`, directories/files/symlinks, and multiple paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Stat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Tail.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Tail.java

Purpose: implements `-tail`, printing the last 1024 bytes of a file and optionally following appended data.

Important APIs and types: `processOptions()`, `expandArgument()`, `processPath()`, `dumpFromOffset()`, and visible-for-testing `getFollowDelay()`.

Control flow: parses one file, optional `-f`, and optional positive `-s` sleep interval when following. Expansion avoids globbing for backward compatibility. `processPath()` rejects directories, prints from negative offset relative to EOF, then loops while `follow`, sleeping and printing from the last returned offset. `dumpFromOffset()` refreshes file status, normalizes offsets, opens sequential stream, seeks, copies to `System.out`, and returns new position.

State and persistence: no mutation. Follow loop state is current offset and delay.

Dependencies and integration: uses `PathData.openFile()`, `FSDataInputStream.seek()`, and `IOUtils.copyBytes()`.

Risks: output uses `System.out`, not inherited `out`. Follow loop can run indefinitely and exits on interrupted sleep without restoring interrupt status. File truncation while following causes offset > size to return new size without printing. Glob support is intentionally absent.

Test signals: cover no-glob expansion, directory rejection, short/exact/long files, follow delay parsing including zero/negative ignored, appended data, truncation while following, and interrupt exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Tail.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Test.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Test.java

Purpose: implements `-test`, a shell-style predicate command whose result is conveyed by exit status.

Important APIs and types: `processOptions()`, `processPath()`, `testAccess()`, and `processNonexistentPath()`. Supported flags are `-e`, `-d`, `-f`, `-s`, `-z`, `-w`, and `-r`.

Control flow: option parsing requires exactly one flag and one path. Existing paths are evaluated against status or `fs.access()` for read/write. A failed predicate or nonexistent path sets `exitCode = 1`; success leaves the inherited success code.

State and persistence: no mutation. State is the selected flag and exit code.

Dependencies and integration: uses `PathData`, `FsAction`, and catches `AccessControlException`/`FileNotFoundException` for access probes.

Risks: only one predicate can be tested per invocation. Access checks depend on filesystem `access()` implementation. Nonexistent path does not print an error through `processNonexistentPath()`, matching test-style semantics.

Test signals: cover every flag, no flag, multiple flags, nonexistent path, access granted/denied, file/directory type checks, zero/nonzero sizes, and exit-code-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Test.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/TouchCommands.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/TouchCommands.java

Purpose: registers `touchz` and Unix-like `touch` commands for creating zero-length files and updating access/modification times.

Important APIs and types: nested `Touchz` and `Touch`; `Touchz.processPath()`, `processNonexistentPath()`, `touchz()`; `Touch.processOptions()`, `touch()`, and `updateTime()`.

Control flow: `touchz` requires paths, rejects directories, rejects existing nonzero files, and creates zero-length files if missing and parent exists. `touch` parses `-a`, `-m`, `-t yyyyMMdd:HHmmss`, and `-c`; it creates missing files unless `-c`, then updates both times or only one time using `-1` sentinel for unchanged time.

State and persistence: mutates file creation and timestamps. Per-run state stores selected time flags, timestamp string, and no-create flag.

Dependencies and integration: uses `PathData.parentExists()`, `fs.create()`, `fs.setTimes()`, `SimpleDateFormat`, and Hadoop path exceptions.

Risks: timestamp parsing uses default timezone and lenient `SimpleDateFormat` behavior unless configured elsewhere. Creating a file before timestamp update can leave current timestamps if update fails. `touchz` calls `create()` without explicit overwrite control but only after validating zero-length existing file.

Test signals: cover missing parent, existing directory, existing nonzero/zero files, `touch -c`, `-a`, `-m`, both flags, explicit timestamp parse success/failure, timezone/leniency expectations, and creation followed by timestamp update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/TouchCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Truncate.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Truncate.java

Purpose: implements `-truncate`, reducing files to a requested length and optionally waiting for block recovery.

Important APIs and types: `processOptions()`, `processArguments()`, `processPath()`, and private `waitForRecovery()`. State includes `newLength`, `waitList`, and `waitOpt`.

Control flow: parses optional `-w`, required nonnegative length, and one or more paths. For each file, rejects directories, rejects extending to a larger length, calls `fs.truncate()`, prints immediate success when true, enqueues for recovery when false and `-w`, or prints a warning to wait manually. `waitForRecovery()` polls each file once per second until status length equals `newLength`.

State and persistence: mutates file length through filesystem truncate. Wait list is in-memory.

Dependencies and integration: uses `PathData.refreshStatus()` and `PathIsDirectoryException`.

Risks: wait loop can run indefinitely and ignores interruptions. Truncate semantics depend on filesystem support and block recovery behavior. Re-reading status after truncation can fail if file is removed concurrently.

Test signals: cover invalid lengths, negative length, directory rejection, larger-than-current rejection, immediate truncate, delayed truncate with and without `-w`, wait polling, interruption, and concurrent delete during wait.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Truncate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/XAttrCommands.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/XAttrCommands.java

Purpose: registers extended-attribute commands `getfattr` and `setfattr`.

Important APIs and types: nested `GetfattrCommand` and `SetfattrCommand`. Get flags are `-R`, `-n name`, `-d`, and `-e` encoding; set flags are `-n name`, optional `-v value`, or `-x name`.

Control flow: `getfattr` parses optional encoding (`text`, `hex`, `base64`), recursive flag, dump flag, and exactly one path; it requires either named xattr or dump-all. It prints `# file: path`, then either iterates `fs.getXAttrs()` or calls `fs.getXAttr()`, printing attributes with encoded values or just names for zero-length values. `setfattr` requires exactly one of set or remove mode, decodes provided value through `XAttrCodec`, validates one path, then calls `setXAttr()` or `removeXAttr()`.

State and persistence: `getfattr` is read-only. `setfattr` mutates xattr metadata.

Dependencies and integration: uses `XAttrCodec`, Hadoop `StringUtils` option helpers, `Preconditions`, and `HadoopIllegalArgumentException`.

Risks: get dump order follows map iteration order and may be unstable. Values with null are not printed. Recursive get depends on inherited traversal. Value decoding errors propagate from `XAttrCodec`. Namespace and permission rules are delegated to filesystem.

Test signals: cover required option validation, too many/missing path errors, every encoding, empty xattr value, dump-all ordering expectations, recursive get, set with null/decoded values, remove, and mutually exclusive `-n`/`-x`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/XAttrCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/And.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/And.java

Purpose: implements the `find` logical AND operator for `-a`, `-and`, and implicit juxtaposition.

Important APIs and types: static `registerExpression()`, constructor setting usage/help, `apply()`, `isOperator()`, `getPrecedence()`, and `addChildren()`.

Control flow: `addChildren()` consumes two child expressions. `apply()` starts with `Result.PASS`, applies children in stored order, combines results, and short-circuits on the first non-passing result.

State and persistence: no persistent state beyond inherited child list and help metadata.

Dependencies and integration: extends `BaseExpression`, registers with `ExpressionFactory`, and is inserted explicitly by `Find.parseExpression()` when two primaries are adjacent.

Risks: child depth is passed as `-1` instead of the caller depth, which is existing subsystem behavior but can surprise expressions needing depth. Result combination preserves descend=false from children, enabling prune-like expressions if added later.

Test signals: cover registration aliases, implicit AND insertion, precedence, short-circuit behavior, result combination with STOP, and child order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/And.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/BaseExpression.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/BaseExpression.java

Purpose: base implementation for `find` expressions, providing usage/help storage, option propagation, lifecycle propagation, argument/child storage, default expression classification, and helper accessors for path/status/filesystem.

Important APIs and types: `setUsage()`, `setHelp()`, `setOptions()`, `prepare()`, `finish()`, `isAction()`, `isOperator()`, `getPrecedence()`, `addChildren()`, protected `addChildren(exprs,count)`, `addArguments(args,count)`, `getArgument()`, `getFileStatus()`, `getPath()`, and `getFileSystem()`.

Control flow: lifecycle calls cascade to all children. `isAction()` is true if any child is an action. Default child/argument methods do nothing; subclasses opt in. `getFileStatus()` follows symlinks when global options say follow all links or follow command-argument links at depth zero.

State and persistence: stores `FindOptions`, `Configuration`, linked-list arguments, and child expressions. No filesystem mutation.

Dependencies and integration: implements `Expression` and `Configurable`, uses `PathData`, `FileStatus`, `FileSystem`, and `Path`.

Risks: `getOptions()` returns a new default `FindOptions` when unset, which can mask missing option propagation. `getFileStatus()` references `options` field directly, so calling before `setOptions()` can NPE if symlink status is evaluated. Child insertion uses `push()`, reversing order relative to pop sequence by design.

Test signals: cover lifecycle propagation, action detection through children, missing/null argument errors, child ordering, symlink status following under `-L`/`-H`, unset options behavior, and `toString()` format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/BaseExpression.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Expression.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Expression.java

Purpose: defines the contract for all Hadoop shell `find` expression nodes.

Important APIs and types: lifecycle methods `setOptions()`, `prepare()`, `apply()`, `finish()`; metadata methods `getUsage()`, `getHelp()`; classification methods `isAction()`, `isOperator()`, `getPrecedence()`; parser hooks `addChildren()` and `addArguments()`.

Control flow: `Find` constructs expression trees, sets options, calls `prepare()`, invokes `apply(item, depth)` for each visited path, and then calls `finish()`. Operators consume child expressions; primaries consume string arguments.

State and persistence: interface has no state; implementations may keep parsed args, children, and runtime resources.

Dependencies and integration: works with `PathData` and returns `Result` to control pass/fail and descent.

Risks: implementers must honor deque pop ordering and lifecycle propagation or expression parsing and resource cleanup break. `isAction()` controls whether `Find` auto-adds `-print`, so incorrect classification changes user-visible output.

Test signals: expression implementer tests should verify lifecycle, parser consumption, action/operator classification, precedence, and `Result` semantics for traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Expression.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/ExpressionFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/ExpressionFactory.java

Purpose: singleton registry and instantiation factory for `find` expressions.

Important APIs and types: `getExpressionFactory()`, `registerExpression()`, `addClass()`, `isExpression()`, `getExpression()`, `createExpression(Class,Configuration)`, and `createExpression(String,Configuration)`.

Control flow: expression classes expose a static `registerExpression(ExpressionFactory)` method. The factory invokes that method reflectively, allowing each class to register one or more names. Parser lookups check `expressionMap`, then instantiate classes through `ReflectionUtils.newInstance()` with the command configuration.

State and persistence: singleton keeps an in-memory `Map<String, Class<? extends Expression>>`; no durable state.

Dependencies and integration: used by `Find` static initialization and parsing. Depends on reflection, Hadoop `ReflectionUtils`, and `StringUtils.stringifyException()` for failure reporting.

Risks: registration failures are wrapped in `RuntimeException`, making static initialization failures broad. `getExpression()` throws NPE on null configuration. Duplicate names overwrite previous registrations without warning. `createExpression(null, conf)` returns null, used while building help from known classes.

Test signals: cover reflective registration, alias registration, duplicate behavior, unknown expression, null config, invalid classname, and instantiated configurable receiving configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/ExpressionFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/FilterExpression.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/FilterExpression.java

Purpose: composition wrapper for `Expression` implementations, used for variants such as case-insensitive name and null-terminated print without inheritance duplication.

Important APIs and types: constructor accepting an `Expression`, delegate implementations for all `Expression` methods, `Configurable` forwarding, and `toString()`.

Control flow: if wrapped expression is non-null, lifecycle, apply, usage/help, classification, precedence, child/argument parsing, and configuration calls are forwarded. If null, defaults return pass, false, -1, or null as appropriate. `apply()` delegates with depth `-1`.

State and persistence: stores one wrapped expression reference; no durable state.

Dependencies and integration: implements `Expression` and `Configurable`; used by `Name.Iname` and `Print.Print0`.

Risks: depth is not forwarded, which can be problematic for wrappers around depth-aware expressions. Null wrapped expressions return null usage/help, which help builders might not expect if used directly. `getConf()` returns null when wrapped expression is not configurable.

Test signals: cover delegation of lifecycle and parsing, null-wrapper defaults, configuration forwarding, depth behavior, and `toString()` composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/FilterExpression.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Find.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Find.java

Purpose: implements Hadoop shell `-find`, including expression registration, parsing, recursive traversal, optional symlink following, and default `-print` action insertion.

Important APIs and types: static expression set and description builder, `processOptions()`, `parseExpression()`, `recursePath()`, `isPathRecursable()`, `processPath()`, `postProcessPath()`, `applyItem()`, and `processArguments()`. State includes `FindOptions`, root `Expression`, and `stopPaths`.

Control flow: construction enables recursion. Options parse `-L` or `-H`, split leading path args from expression args at the first token beginning with `-`, default path to `.`, parse expression deque using operator/primary stacks and parentheses, and auto-wrap non-action expressions with `Print AND expression`. During traversal, expressions are applied pre-order or post-order depending on options, only at or below min depth, and a `Result.STOP` path is recorded to prevent further recursion.

State and persistence: read-only traversal except expression actions may mutate if future actions are added. `stopPaths` is per-run in memory.

Dependencies and integration: extends `FsCommand`, uses `ExpressionFactory`, built-in `And`, `Print`, and `Name`, `FindOptions`, `PathData`, and inherited recursive traversal.

Risks: expression/path split treats the first dash-leading token as expression, so paths beginning with `-` need command-line escaping conventions. Symlink loop detection compares ancestors in one direction and may not catch all graph cycles. `Result.isDescend()` is only acted on through equality with `Result.STOP` in `applyItem()`, not arbitrary descend=false combinations unless equals STOP. Parenthesis parse errors are minimal. Built-in expression set is small.

Test signals: cover default path/expression, `-name`, `-iname`, `-print`, `-print0`, implicit AND, explicit AND, parentheses, action auto-print insertion, `-L`/`-H` symlink directory traversal, loop avoidance message, STOP behavior, depth-first options via `FindOptions`, and paths starting with dash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Find.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/FindOptions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/FindOptions.java

Purpose: mutable options holder shared by `Find` and expression instances.

Important APIs and types: getters/setters for output, error, input streams, depth-first flag, follow-link flags, start time, min/max depth, `CommandFactory`, and `Configuration`.

Control flow: `Find.createOptions()` initializes streams, command factory, and configuration. Expressions read these options during prepare/apply to control output, symlink handling, depth behavior, and future time-based predicates.

State and persistence: in-memory per-command mutable configuration. `startTime` defaults to object creation time; `configuration` defaults to a new `Configuration`.

Dependencies and integration: uses `PrintStream`, `InputStream`, `Date`, Hadoop `Configuration`, and `CommandFactory`.

Risks: setters do no validation for null streams, min/max consistency, or negative depths. Defaults may differ from the actual command environment if `Find` does not initialize options. Future expressions relying on start time need deterministic test control.

Test signals: cover defaults, `Find` initialization, all setters/getters, depth bounds, follow flags, null handling expectations, and start time override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/FindOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Name.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Name.java

Purpose: implements `find` basename matching expressions `-name` and `-iname`.

Important APIs and types: static `registerExpression()`, constructor, private case-sensitivity constructor, `addArguments()`, `prepare()`, `apply()`, and nested `Iname` filter.

Control flow: one pattern argument is consumed. `prepare()` lowercases the pattern for insensitive mode and builds a `GlobPattern`. `apply()` obtains `getPath(item).getName()`, lowercases when needed, and returns `PASS` on glob match or `FAIL` otherwise.

State and persistence: stores `GlobPattern` and case-sensitivity flag after preparation; no mutation.

Dependencies and integration: extends `BaseExpression`, uses Hadoop `GlobPattern`, `PathData`, and `StringUtils.toLowerCase()`. `Iname` wraps `new Name(false)` through `FilterExpression`.

Risks: matching is basename-only, not full path. Case-insensitive behavior lowercases with Hadoop utility, so locale expectations should be checked. `globPattern` is null before `prepare()`, so lifecycle is required.

Test signals: cover case-sensitive and insensitive matching, glob metacharacters, basename-only behavior, missing pattern argument, prepare-before-apply requirement, and registration aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Name.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Print.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Print.java

Purpose: implements `find` output actions `-print` and `-print0`.

Important APIs and types: static `registerExpression()`, constructor with suffix, `apply()`, `isAction()`, and nested `Print0`.

Control flow: `apply()` writes `item.toString()` plus suffix to `FindOptions.out` and returns `Result.PASS`. `Print0` wraps a `Print` with null-byte suffix using `FilterExpression`.

State and persistence: stores suffix only. No filesystem mutation.

Dependencies and integration: extends `BaseExpression`; action classification prevents `Find` from auto-inserting a separate `-print` when explicitly present.

Risks: no escaping is applied; output is exactly path spelling plus newline or NUL. Null `FindOptions.out` causes failure if options were not initialized. `Print0` inherits `FilterExpression` depth behavior but does not use depth.

Test signals: cover newline and NUL output, action classification, explicit action avoiding auto-print insertion, multiple path spellings, and missing output stream failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Print.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Result.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Result.java

Purpose: immutable-like value object representing expression success and whether traversal should descend further.

Important APIs and types: constants `PASS`, `FAIL`, `STOP`; `isDescend()`, `isPass()`, `combine()`, `negate()`, `toString()`, `hashCode()`, and `equals()`.

Control flow: expressions return one of the predefined constants or combined/negated instances. `combine()` ANDs pass and descend bits. `negate()` flips pass while preserving descend.

State and persistence: private booleans `success` and `descend`; no external mutation API, though fields are not final.

Dependencies and integration: used by all `find` expressions and by `Find.applyItem()` to decide stop-path recording.

Risks: only equality with `Result.STOP` is explicitly checked in `Find`, so a combined result with pass=true/descend=false equals STOP and works, but any fail+descend=false result will not be recorded as stop. Non-final fields reduce immutability clarity.

Test signals: cover constants, combine truth table, negate semantics, equality/hash, string form, and integration with stop traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Result.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/package-info.java

Purpose: package-level metadata for `org.apache.hadoop.fs.shell`, documenting it as support for execution of filesystem commands.

Important APIs and types: package annotations `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`.

Control flow: no runtime logic.

State and persistence: no state and no mutation.

Dependencies and integration: imports Hadoop classification annotations and applies them to the shell package.

Risks: package-level stability/audience annotations communicate that APIs are not public compatibility contracts; external consumers should not depend on these classes.

Test signals: no behavioral tests needed beyond compilation and annotation visibility if API documentation generation is validated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/BufferedIOStatisticsInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/BufferedIOStatisticsInputStream.java

Purpose: `BufferedInputStream` subclass that preserves access to the wrapped stream's `IOStatistics` and stream capabilities.

Important APIs and types: constructors with default/custom buffer size, `getIOStatistics()`, and `hasCapability()`.

Control flow: buffering behavior is inherited. `getIOStatistics()` calls `IOStatisticsSupport.retrieveIOStatistics(in)`. `hasCapability()` delegates to wrapped stream when it implements `StreamCapabilities`, otherwise returns false.

State and persistence: in-memory buffer inherited from `BufferedInputStream`; no durable state or filesystem mutation.

Dependencies and integration: implements `IOStatisticsSource` and `StreamCapabilities`; intended for wrappers around filesystem input streams where statistics should remain discoverable.

Risks: statistics are retrieved from the wrapped stream, not accumulated by the buffer. Capabilities may be affected by buffering semantics even though delegated. Closed-stream behavior follows underlying/inherited stream behavior.

Test signals: cover default/custom buffer construction, statistics delegation for source and non-source streams, capability delegation true/false, read behavior still buffered, and close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/BufferedIOStatisticsInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/BufferedIOStatisticsOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/BufferedIOStatisticsOutputStream.java

Purpose: `BufferedOutputStream` subclass that preserves wrapped-stream `IOStatistics`, forwards stream capabilities, and implements `Syncable` with optional downgrade to flush.

Important APIs and types: constructors with default/custom buffer size and `downgradeSyncable`, `getIOStatistics()`, `hasCapability()`, `hflush()`, and `hsync()`.

Control flow: `getIOStatistics()` delegates through `IOStatisticsSupport.retrieveIOStatistics(out)`. `hasCapability()` delegates when wrapped stream implements `StreamCapabilities`. `hflush()` and `hsync()` flush the buffer first, then call the wrapped `Syncable` method if supported; otherwise either throw `UnsupportedOperationException` or just flush when downgrade is enabled.

State and persistence: inherited output buffer plus immutable `downgradeSyncable`. Writes/syncs mutate the wrapped output destination.

Dependencies and integration: implements `IOStatisticsSource`, `Syncable`, and `StreamCapabilities`; mirrors `FsDataOutputStream` downgrade behavior when configured.

Risks: downgrade mode violates strict `Syncable` durability expectations by reducing sync to flush. Capability delegation may claim support based on underlying stream but buffering can affect timing. Unsupported exceptions include wrapped stream `toString()` for diagnostics.

Test signals: cover statistics delegation, capability delegation, hflush/hsync on syncable stream including flush-before-sync, unsupported behavior with downgrade false, flush fallback with downgrade true, custom buffer size, and exception propagation from inner sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/BufferedIOStatisticsOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationStatisticSummary.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationStatisticSummary.java

Purpose: serializable summary object for duration statistics extracted from an `IOStatistics` source, intended for reporting and tests.

Important APIs and types: constructor, getters, `toString()`, static `fetchDurationSummary()`, and `fetchSuccessSummary()`. Fields include key, success flag, count, max, min, and cloned nullable `MeanStatistic`.

Control flow: constructor clones mean statistics defensively when present. `fetchDurationSummary()` builds a success or failure key using `StoreStatisticNames.SUFFIX_FAILURES`, reads counter, max, min, and mean entries from the source maps with defaults for missing values, and returns a summary.

State and persistence: immutable final fields, serializable with explicit `serialVersionUID`. No mutation after construction.

Dependencies and integration: uses `IOStatistics`, `MeanStatistic`, nullable annotation, and store statistic suffix constants.

Risks: `getMean()` returns the stored clone directly, so if `MeanStatistic` is mutable consumers may mutate the summary's copy. `toString()` omits `min`. Missing statistics produce count 0 and max/min -1, which callers must treat as incomplete rather than zero-duration.

Test signals: cover success and failure key lookup, missing data defaults, mean clone behavior, serialization, `toString()`, and immutability expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationStatisticSummary.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationTracker.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationTracker.java

Purpose: contract for objects that track operation duration and update statistics when closed.

Important APIs and types: `failed()`, `close()`, and default `asDuration()`. It extends `AutoCloseable` but narrows `close()` to no checked exception.

Control flow: intended use is try-with-resources. Callers call `failed()` before `close()` when an operation fails; implementations update failure counters and duration metrics. Default `asDuration()` returns `Duration.ZERO` until implementations provide measured duration.

State and persistence: interface has no state; implementations may record start/end times and update external statistics.

Dependencies and integration: paired with `DurationTrackerFactory` and `IOStatistics` implementations.

Risks: callers must remember `failed()` on exceptional paths or failure metrics will be undercounted. Implementations need idempotent close or clear contract for double-close. Default `asDuration()` can hide missing implementation support.

Test signals: implementation tests should cover try-with-resources close, failure marking, double close, exception paths, and `asDuration()` before/after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationTrackerFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationTrackerFactory.java

Purpose: interface for objects that create `DurationTracker` instances for named operations.

Important APIs and types: default `trackDuration(String key, long count)` and overload `trackDuration(String key)`.

Control flow: default `trackDuration(key,count)` returns `IOStatisticsSupport.stubDurationTracker()`, allowing callers to instrument code without requiring a concrete statistics implementation. The one-argument overload delegates with count 1.

State and persistence: interface has no state. Concrete factories update statistics through trackers on close.

Dependencies and integration: used by filesystem/store code to instrument operations; imports `stubDurationTracker`.

Risks: default stub silently records nothing, so code must be wired with a real factory for metrics. Count semantics depend on implementation. Null or empty keys are not validated at interface level.

Test signals: cover default stub no-op behavior, one-arg delegation count, concrete implementation count handling, null/empty key policy, and try-with-resources usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationTrackerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/FileSystemStatisticNames.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/FileSystemStatisticNames.java

Purpose: public constants for filesystem-level duration statistic names.

Important APIs and types: final utility class with private constructor and constants `FILESYSTEM_INITIALIZATION` and `FILESYSTEM_CLOSE`.

Control flow: no runtime logic beyond class loading.

State and persistence: immutable string constants; no mutation.

Dependencies and integration: used by filesystem implementations and statistics consumers to agree on key names for initialization and close durations.

Risks: changing constant values would break metric compatibility. The class intentionally has a small scope and does not enumerate stream/store statistics.

Test signals: compile-time use, constant value stability, private constructor coverage only if enforcing utility-class conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/FileSystemStatisticNames.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatistics.java

Purpose: public unstable interface exposing low-cost per-instance IO statistics.

Important APIs and types: map accessors `counters()`, `gauges()`, `minimums()`, `maximums()`, `meanStatistics()`, and unset sentinels `MIN_UNSET_VALUE`/`MAX_UNSET_VALUE` equal to -1.

Control flow: implementations return current statistic maps; consumers read maps by agreed string keys. No methods mutate statistics directly.

State and persistence: interface state is implementation-defined. Returned maps may be live snapshots or immutable copies depending on implementation, which consumers must account for via specification.

Dependencies and integration: uses `MeanStatistic` and Java `Map`; consumed by logging, aggregation, duration summaries, stream wrappers, and filesystem/store metrics.

Risks: map mutability and concurrency guarantees are not specified in this interface. Missing minimum/maximum values use -1 sentinel, which can overlap valid values for some theoretical metrics. Key names are stringly typed.

Test signals: implementation tests should cover all map categories, empty maps, unset sentinels, snapshot/live behavior, thread-safety expectations, and mean statistic cloning where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsAggregator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsAggregator.java

Purpose: public evolving interface for objects that aggregate `IOStatistics` from other sources.

Important APIs and types: single method `aggregate(@Nullable IOStatistics statistics)` returning boolean.

Control flow: callers pass a possibly-null statistics reference. Implementations decide whether to aggregate all categories or selected values and return true only when a non-null reference was aggregated.

State and persistence: interface has no state; implementations maintain aggregate counters/gauges/min/max/means.

Dependencies and integration: used by metrics collectors and composite stream/filesystem classes that merge child statistics.

Risks: aggregation policy is deliberately flexible, so consumers must know implementation semantics. Null handling is part of the contract. Concurrency and idempotence are implementation-specific.

Test signals: cover null input returning false, non-null returning true, selected/all category aggregation, repeated aggregation behavior, mean/min/max combination semantics, and thread safety for concrete implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsAggregator.java -->
