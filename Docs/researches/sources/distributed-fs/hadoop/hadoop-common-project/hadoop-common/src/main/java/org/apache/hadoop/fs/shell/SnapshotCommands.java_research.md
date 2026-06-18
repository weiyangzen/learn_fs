# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/SnapshotCommands.java

Purpose: registers snapshot commands `createSnapshot`, `deleteSnapshot`, and `renameSnapshot`.

Important APIs and types: nested `CreateSnapshot`, `DeleteSnapshot`, `RenameSnapshot`; each parses arguments, validates the root path is a directory, and performs one filesystem snapshot operation in `processArguments()`.

Control flow: create accepts directory plus optional snapshot name, validates argument count, and calls `fs.createSnapshot()`. Delete accepts exactly directory and snapshot name and calls `fs.deleteSnapshot()`. Rename accepts directory, old name, and new name and calls `fs.renameSnapshot()`. All commands first let superclass path processing validate the single root and abort mutation when `numErrors != 0`.

State and persistence: mutates snapshot metadata on the target filesystem. Per-run state stores snapshot name(s).

Dependencies and integration: extends `FsCommand`, uses `PathData`, `PathIsNotDirectoryException`, and `Preconditions.checkArgument()` for final invariant checks.

Risks: argument parsing removes snapshot names before path expansion; snapshot names are not otherwise validated here. Filesystem-specific errors propagate. Uses `assert` in two commands and `Preconditions` in one for size invariant, but mutation relies on prior argument-count checks.

Test signals: cover wrong argument counts, non-directory roots, successful create/delete/rename, superclass error abort, optional create name, and filesystem exception propagation.
