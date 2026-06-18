<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/shallow-tree -->
# sources/distributed-fs/openafs/src/tests/shallow-tree

## Purpose
Runs a focused shell-level filesystem test built around `mkdir, , $SHELL, ${objdir}/rm-rf`.

## Important APIs, Types, and Functions
commands: mkdir, , $SHELL, ${objdir}/rm-rf

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, , $SHELL, ${objdir}/rm-rf`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 5 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/shallow-tree -->
