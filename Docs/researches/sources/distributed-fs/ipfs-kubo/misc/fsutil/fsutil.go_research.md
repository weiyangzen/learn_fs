<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil.go -->
# sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil.go

## Purpose

This utility package provides small filesystem helpers for repo/plugin code, especially writable-directory validation and home-directory expansion.

## Important APIs, Types, and Functions

`DirWritable` expands `~`, creates a missing directory with `0775`, rejects non-directories, and verifies writability by creating/removing a temp file. `ExpandHome` expands `~` or `~/...`/`~\...` using `os.UserHomeDir` and rejects `~user` syntax. `FileExists` uses `os.Lstat` and returns false only for not-exist errors.

## Control Flow, State, and Integration

`DirWritable` may persist state by creating the target directory and a temporary probe file. It is used by the Pebble datastore plugin before opening the datastore path.

## Dependencies, Risks, and Test Signals

Dependencies are standard `os`, `io/fs`, and `filepath`. Risks include non-atomic writability probes, permission differences across platforms, and `FileExists` treating non-permission errors as existence. Tests cover empty paths, bad home expansion, directory creation, read-only directories on non-Windows, file existence, and home env behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil.go -->
