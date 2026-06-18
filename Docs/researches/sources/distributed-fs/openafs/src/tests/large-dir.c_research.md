<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir.c -->
# sources/distributed-fs/openafs/src/tests/large-dir.c

## Purpose
Stresses large directory creation, lookup, and removal behavior.

## Important APIs, Types, and Functions
functions: creat_files, usage, main

## Control Flow
`main` drives the test through helper functions `creat_files, usage` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, stat, mkdir, opendir, readdir, unlink, chdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 148 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir.c -->
