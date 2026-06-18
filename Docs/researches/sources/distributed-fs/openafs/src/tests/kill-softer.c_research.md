<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/kill-softer.c -->
# sources/distributed-fs/openafs/src/tests/kill-softer.c

## Purpose
Runs a focused C filesystem test with entry points `kill_one, do_dir, kill_dir, main`.

## Important APIs, Types, and Functions
functions: kill_one, do_dir, kill_dir, main

## Control Flow
`main` drives the test through helper functions `kill_one, do_dir, kill_dir` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `stat, lstat, rmdir, opendir, readdir, unlink, chdir`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 184 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/kill-softer.c -->
