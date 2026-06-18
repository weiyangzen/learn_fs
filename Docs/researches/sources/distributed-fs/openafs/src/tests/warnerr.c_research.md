<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/warnerr.c -->
# sources/distributed-fs/openafs/src/tests/warnerr.c

## Purpose
Implements or declares BSD-style `err(3)`/`warn(3)` compatibility helpers for the test programs.

## Important APIs, Types, and Functions
functions: getprogname, setprogname, set_progname, get_progname, warnerr

## Control Flow
`main` drives the test through helper functions `getprogname, setprogname, set_progname, get_progname, warnerr` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 100 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/warnerr.c -->
