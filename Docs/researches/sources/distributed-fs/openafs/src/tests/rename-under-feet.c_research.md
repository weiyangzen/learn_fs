<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename-under-feet.c -->
# sources/distributed-fs/openafs/src/tests/rename-under-feet.c

## Purpose
Exercises rename semantics, including replacement, rollback, directory moves, or active-directory edge cases.

## Important APIs, Types, and Functions
functions: emkdir, child_sigterm, child_chdir, kill_child, main

## Control Flow
`main` drives the test through helper functions `emkdir, child_sigterm, child_chdir, kill_child` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `close, read, write, stat, lstat, mkdir, rmdir, rename, fork, waitpid`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
detects stale directory entries, wrong inode preservation, or bad rollback; nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 161 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename-under-feet.c -->
