# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/atomicfile/atomicfile.go

Purpose: provides a small same-directory atomic file writer used by embedded migration backup and config rewrite helpers.

Important APIs and control flow: `New(path, mode)` creates a hidden temp file in the target directory and chmods it. `Close` closes the temp file and renames it over the target. `Abort` closes and removes the temp file, combining close and remove errors when both fail. `ReadFrom` copies a reader into the temp file.

State and persistence: writes temporary `.tmp-<base>` files next to the target, then relies on `os.Rename` atomicity on the same filesystem. It does not fsync file contents or parent directories.

Dependencies and integration: used by migration `common.WithBackup` to atomically create config backups and replacement config files.

Risks and test signals: double `Abort` returns an error because the file is gone but should not panic. On Windows, rename semantics depend on closed handles. Tests cover creation, close, abort, close failure cleanup, permissions, `ReadFrom`, and temp-file cleanup.
