<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/invalidate-file.c -->
# sources/distributed-fs/openafs/src/tests/invalidate-file.c

## Purpose
Runs a focused C filesystem test with entry points `create_write_file, read_file, mmap_read_file, mmap_write_file, main`.

## Important APIs, Types, and Functions
functions: create_write_file, read_file, mmap_read_file, mmap_write_file, main; AFS calls/macros: fs_invalidate

## Control Flow
`main` drives the test through helper functions `create_write_file, read_file, mmap_read_file, mmap_write_file` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, read, write, mmap, munmap, fs_invalidate`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces fs_invalidate

## Risks and Test Signals
targets mmap/cache coherency and writeback edge cases; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 200 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/invalidate-file.c -->
