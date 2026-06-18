<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil_test.go -->
# sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil_test.go

## Purpose

This file tests the filesystem utility helpers used by datastore and repo-adjacent code.

## Important APIs, Types, and Functions

`TestDirWritable` covers empty input, unsupported `~user`, creation of missing directories, repeated success, and read-only directory failures outside Windows. `TestFileExists` checks nonexistent and created files. `TestExpandHome` covers empty paths, non-home paths, `~user` rejection, home env expansion, and missing home env errors.

## Control Flow, State, and Integration

Tests use temporary directories and manipulate `HOME` or `USERPROFILE` with restoration. They skip read-only permission checks on Windows.

## Dependencies, Risks, and Test Signals

Dependencies are `runtime`, `os`, `filepath`, and testify. The tests signal regressions in path expansion and permission error normalization that could break datastore setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil_test.go -->
