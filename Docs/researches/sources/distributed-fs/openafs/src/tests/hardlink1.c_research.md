<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink1.c -->
# sources/distributed-fs/openafs/src/tests/hardlink1.c

## Purpose
Exercises hard-link creation, link-count semantics, and cross-volume or high-count hard-link constraints.

## Important APIs, Types, and Functions
functions: main

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, write, stat, lstat, fstat, unlink, link`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
detects link-count and cross-volume hard-link policy regressions; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 143 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink1.c -->
