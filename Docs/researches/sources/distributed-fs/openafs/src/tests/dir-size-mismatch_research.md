<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dir-size-mismatch -->
# sources/distributed-fs/openafs/src/tests/dir-size-mismatch

## Purpose
Runs a focused shell-level filesystem test built around `then, i, ++i, ln`.

## Important APIs, Types, and Functions
commands: then, i, ++i, ln, find, xargs, rm

## Control Flow
Sequential shell commands run in the harness work directory: `then, i, ++i, ln, find, xargs, rm`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, i, ++i, ln, find, xargs`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, ln, find, xargs, awk, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 10 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dir-size-mismatch -->
