# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Delete.java

Purpose: registers delete-related commands `rm`, `rmdir`, deprecated `rmr`, and `expunge`.

Important APIs and types: nested `Rm`, `Rmr`, `Rmdir`, and `Expunge`; `Rm.processOptions()`, `expandArgument()`, `processPath()`, `canBeSafelyDeleted()`, `moveToTrash()`; `Rmdir.processPath()`; `Expunge.processArguments()`.

Control flow: `Rm` parses force, recursive, trash bypass, and safe-delete flags. It suppresses nonexistent glob errors under `-f`, rejects directories unless recursive, attempts trash unless skipped, optionally counts files via `ContentSummary` and confirms large deletes, then calls `fs.delete(path, deleteDirs)`. `Rmr` injects `-r` and advertises replacement. `Rmdir` deletes only empty directories unless `--ignore-fail-on-non-empty` is set. `Expunge` optionally changes `fs.defaultFS`, iterates child filesystems if present, and calls `Trash.expunge()`/`checkpoint()` or immediate expunge.

State and persistence: these commands remove files/directories or trash checkpoints, and may update trash directories. State is per-command flags.

Dependencies and integration: uses `Trash`, `ContentSummary`, `ToolRunner.confirmPrompt`, `CommonConfigurationKeysPublic`, `FileSystem.getChildFileSystems()`, and path-specific Hadoop exceptions.

Risks: `rm` comments note a historical concern that trash failures can lead to direct deletion in some patterns, although current `moveToTrash()` rethrows most IO failures with a `-skipTrash` hint. Safe delete counts content before deleting and can be slow. `-f` on nonexistent globs returns an empty list, which affects user diagnostics. `Expunge -fs` mutates configuration default FS for the command.

Test signals: cover `-f` nonexistent behavior, recursive and nonrecursive directory deletes, trash success/failure, safe-delete confirmation yes/no and threshold zero, empty/nonempty `rmdir`, expunge child-filesystem iteration, and immediate expunge.
