<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-cat.c -->
# sources/distributed-fs/openafs/src/tests/mmap-cat.c

## Purpose
Compares mmap-backed access with ordinary file I/O to catch cache coherency or writeback regressions.

## Important APIs, Types, and Functions
functions: doit_mmap, doit_read, doit, usage, main

## Control Flow
`main` drives the test through helper functions `doit_mmap, doit_read, doit, usage` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, stat, fstat, mmap, munmap`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 137 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mmap-cat.c -->
