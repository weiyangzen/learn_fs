<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/strange-characters-c.c -->
# sources/distributed-fs/openafs/src/tests/strange-characters-c.c

## Purpose
Runs a focused C filesystem test with entry points `creat_file, look_at_file, usage, main`.

## Important APIs, Types, and Functions
functions: creat_file, look_at_file, usage, main

## Control Flow
`main` drives the test through helper functions `creat_file, look_at_file, usage` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 88 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/strange-characters-c.c -->
