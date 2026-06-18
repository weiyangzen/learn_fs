# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/splice_read.c

## Purpose
Helper program that splices bytes from an input file to stdout for shell-level splice tests.

## Important APIs, types, and functions
`main()` uses `open()`, optional `fstat()`, `atol()`, `splice()`, and standard error reporting.

## Control flow
Requires at least an input path. If byte count is supplied, uses it; otherwise uses file size after rejecting sizes above `INT_MAX`. Calls `splice(fd, NULL, STDOUT_FILENO, NULL, size, 0)` and returns failure on open/stat/splice errors or short splice.

## State and persistence
No persistent state; opens the input file and writes to stdout.

## Dependencies and integration points
Used by `short_splice_read.sh` to compare pseudo-file splice output with normal reads.

## Risks
`atol()` provides weak input validation. For pseudo-files, `st_size` may be zero, so tests usually pass explicit byte counts. Short splice behavior is treated as failure.

## Test signals
Exit 0 with stdout matching expected content is success; perror output and nonzero exit indicate helper failure.
