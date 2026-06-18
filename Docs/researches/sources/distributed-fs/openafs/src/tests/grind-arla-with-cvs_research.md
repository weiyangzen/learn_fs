<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/grind-arla-with-cvs -->
# sources/distributed-fs/openafs/src/tests/grind-arla-with-cvs

## Purpose
Runs a focused shell-level filesystem test built around `echo, sleep, test, mkdir`.

## Important APIs, Types, and Functions
commands: echo, sleep, test, mkdir, cd, cvs, grep, sh, ../arla/configure, mv

## Control Flow
Sequential shell commands run in the harness work directory: `echo, sleep, test, mkdir, cd, cvs, grep, sh`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, cvs, sleep, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 52 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/grind-arla-with-cvs -->
