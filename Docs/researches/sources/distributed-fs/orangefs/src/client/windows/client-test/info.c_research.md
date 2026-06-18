# sources/distributed-fs/orangefs/src/client/windows/client-test/info.c

## Purpose
`info.c` tests file metadata timestamps and reported volume free/total space for the mounted filesystem.

## Important APIs, Types, And Functions
It implements `file_time` and platform-specific `volume_space`. Windows uses `_stat` and `_getdiskfree`; non-Windows uses `statfs`.

## Control Flow
`file_time` records current time, creates a random file, stats it, computes absolute differences for atime/ctime/mtime, and expects each to be within 15 seconds. `volume_space` retrieves disk space, reports the API result, and emits free/total GB performance-style values.

## State And Persistence
`file_time` creates and removes one temporary file. `volume_space` only reads filesystem metadata.

## Dependencies And Integration Points
It depends on CRT stat APIs, Windows `_diskfree_t` or POSIX `statfs`, errno, and `test-support.h`. It exercises Dokany `GetFileInformation` and `GetDiskFreeSpace`.

## Risks And Test Signals
`file_time` computes `code` from timestamp differences but reports a literal actual value of `0`, hiding failures in the report line while still returning fatal if enabled. The non-Windows GB calculation lacks parentheses around the full divisor, producing incorrect scaling. The tests provide useful smoke signal for metadata translation and statfs but need fixes for precise assertions.
