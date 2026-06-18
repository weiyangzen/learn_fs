<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/read-vs-mmap2.c -->
# sources/distributed-fs/openafs/src/tests/read-vs-mmap2.c

## Purpose
Compares mmap-backed access with ordinary file I/O to catch cache coherency or writeback regressions.

## Important APIs, Types, and Functions
functions: generate_random_file, read_file, mmap_file, main

## Control Flow
`main` drives the test through helper functions `generate_random_file, read_file, mmap_file` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, mmap, unlink`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 129 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/read-vs-mmap2.c -->
