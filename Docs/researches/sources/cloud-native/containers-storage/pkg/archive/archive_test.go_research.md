# sources/cloud-native/containers-storage/pkg/archive/archive_test.go

## Purpose
This is the broad generic test suite for `pkg/archive`. It validates archive detection, compression, tar/untar copying, include/exclude behavior, metadata preservation, security breakout prevention, temporary archives, archive modification, deterministic timestamps, and error propagation.

## Important Test Areas
Archive detection tests cover invalid files, directories, tar files, and gzip-compressed tar files. Compression tests validate gzip, bzip2, xz decompression and unsupported xz/bzip2 compression. Copy tests cover invalid sources/destinations, file-vs-directory overwrite behavior, destination creation, socket skipping, and metadata preservation. Round-trip tests compare `ChangesDirs` after tar/untar for many files and hardlinks. Include/exclude/rebase tests validate `TarOptions`. Security tests build malicious tar headers for `../`, absolute-like paths, hardlink escapes, symlink escapes, and symlink-in-path writes.

## Control Flow and State
Tests use real temp directories and files, external shell tools for some tar/compression setup, in-memory tar streams for malicious cases, and helper wrappers around `NewDefaultArchiver`. Several tests skip on Windows where platform behavior is unavailable. `TestReplaceFileTarWrapper` streams an archive through modifiers that create, replace, and append entries. `TestTimestamp` compares whole tar byte streams with and without fixed timestamps. `TestTarErrorHandling` uses a failing writer to ensure errors are propagated.

## Dependencies and Integration Points
The tests depend on `archive/tar`, `os/exec`, runtime checks, `idtools`, and `testify`. They exercise `archive.go`, platform hooks for hardlinks/special files/xattrs, `changes.go`, and helper packages for ID mapping and filesystem metadata.

## Risks and Edge Cases
Some tests depend on external commands (`tar`, `gzip`, `bzip2`, `xz`) and platform privileges. Multiple Windows skips mean generic archive behavior is less thoroughly validated on Windows. The security tests are high-value because extraction code is path-sensitive and must reject breakout attempts before creating or removing host files.

## Test Signals
This suite is the primary behavioral safety net for `archive.go`. It signals expected behavior for supported/unsupported compression, safe extraction, copy-pass metadata, hardlink preservation, xattr preservation, replacement streams, deterministic timestamp mode, and write error handling.
