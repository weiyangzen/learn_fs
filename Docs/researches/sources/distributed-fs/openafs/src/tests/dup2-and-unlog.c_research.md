<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dup2-and-unlog.c -->
# sources/distributed-fs/openafs/src/tests/dup2-and-unlog.c

## Purpose
Runs a focused C filesystem test with entry points `main`.

## Important APIs, Types, and Functions
functions: main; AFS calls/macros: ktc_ForgetAllTokens

## Control Flow
`main` drives the test through helper functions `none` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls `open, close, write, dup2`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces ktc_ForgetAllTokens

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 34 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dup2-and-unlog.c -->
