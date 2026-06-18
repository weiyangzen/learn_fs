# sources/distributed-fs/openafs/src/sys/istat.c

## Purpose
`istat.c` opens a vice inode and reports link count and size through `fstat`.

## Important APIs, types, and functions
The K&R-style `main` uses `stat`, `xiopen`, `fstat`, and `printf`.

## Control flow
It stats the partition path in `argv[1]`, parses `argv[2]` as an inode, opens it read-only with `xiopen`, calls `fstat` on the returned descriptor, and prints `st_nlink` and `st_size`.

## State and persistence behavior
It reads inode metadata and does not intentionally modify state.

## Dependencies and integration points
It depends on legacy `xiopen` symbols and is built as part of sys test utilities.

## Risks
No argc validation before dereferencing arguments. Uses `int` for inode and prints sizes with `%d`, which can truncate on modern platforms.

## Test signals
Check missing args, invalid partition, invalid inode, large files, and comparison with `iopen`/filesystem metadata on controlled partitions.
