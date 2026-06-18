<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/intr-read.c -->
# sources/distributed-fs/openafs/src/tests/intr-read.c

## Purpose
Runs a focused C filesystem test with entry points `sigalrm, try_read, find, main`.

## Important APIs, Types, and Functions
functions: sigalrm, try_read, find, main

## Control Flow
`main` drives the test through helper functions `sigalrm, try_read, find` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, stat, lstat, opendir, readdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 125 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/intr-read.c -->
