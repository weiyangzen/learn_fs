<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/null-search.c -->
# sources/distributed-fs/openafs/src/tests/null-search.c

## Purpose
Runs a focused C filesystem test with entry points `usage, parse_options, my_error_cb, my_file_cb, main`.

## Important APIs, Types, and Functions
functions: usage, parse_options, my_error_cb, my_file_cb, main

## Control Flow
`main` drives the test through helper functions `usage, parse_options, my_error_cb, my_file_cb` and terminates via `err`/`errx` or exit status on failures.

## State and Persistence Behavior
Uses POSIX filesystem calls ``; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C program; 178 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/null-search.c -->
