<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/generic-build -->
# sources/distributed-fs/openafs/src/tests/generic-build

## Purpose
Runs a focused shell-level filesystem test built around `echo, gzip, tar, cd`.

## Important APIs, Types, and Functions
commands: echo, gzip, tar, cd, ./configure, make

## Control Flow
Sequential shell commands run in the harness work directory: `echo, gzip, tar, cd, ./configure, make`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `echo, gzip, tar, cd, ./configure, make`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands tar, gzip, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 18 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/generic-build -->
