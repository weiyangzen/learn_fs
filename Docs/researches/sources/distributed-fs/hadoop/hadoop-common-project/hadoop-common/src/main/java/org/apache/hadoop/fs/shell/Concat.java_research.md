# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Concat.java

Purpose: implements `-concat`, a shell command that appends multiple existing source files into an existing target file through `FileSystem.concat()`.

Important APIs and types: `Concat.registerCommands()`, constants `NAME`, `USAGE`, `DESCRIPTION`, `processArguments()`, and test-only `setTestFs(FileSystem)`.

Control flow: `processArguments()` requires a target plus at least two source paths, removes the first argument as target, validates that target and every source exist and are files, builds a `Path[]` of source paths, selects `target.fs` or injected `testFs`, and calls `fs.concat(target.path, srcArray)`.

State and persistence: the command mutates the target filesystem by concatenating source block data into the target according to the filesystem's native concat semantics. The only class state is static `testFs`, used to inject a filesystem in tests.

Dependencies and integration: extends `FsCommand`, consumes `PathData` produced by command argument expansion, delegates all actual file mutation to `FileSystem.concat()`, and maps unsupported filesystems into `PathIOException` with scheme context.

Risks: it relies on the filesystem to enforce same-directory, block-size, checksum, and source removal semantics; this class only validates existence and file type. Static `testFs` can leak across tests if not reset. Error messages use source/target `Path` strings, not original user path spellings.

Test signals: cover missing target, fewer than two sources, nonexistent/non-file sources, unsupported filesystem exception mapping, success delegation to `concat()`, and cleanup/reset of injected `testFs`.
