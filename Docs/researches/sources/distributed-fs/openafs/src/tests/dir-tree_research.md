<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dir-tree -->
# sources/distributed-fs/openafs/src/tests/dir-tree

## Purpose
Runs a focused shell-level filesystem test built around `shift, expr, mkdir, cd`.

## Important APIs, Types, and Functions
commands: shift, expr, mkdir, cd, \, $SHELL

## Control Flow
Sequential shell commands run in the harness work directory: `shift, expr, mkdir, cd, \, $SHELL`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, expr

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 22 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dir-tree -->
