<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/find-linux -->
# sources/distributed-fs/openafs/src/tests/find-linux

## Purpose
Runs a focused shell-level filesystem test built around `then, cd, find`.

## Important APIs, Types, and Functions
commands: then, cd, find

## Control Flow
Sequential shell commands run in the harness work directory: `then, cd, find`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, cd, find`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands find, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 5 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/find-linux -->
