<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/visit-volumes -->
# sources/distributed-fs/openafs/src/tests/visit-volumes

## Purpose
Runs a focused shell-level filesystem test built around `ls`.

## Important APIs, Types, and Functions
commands: ls

## Control Flow
Sequential shell commands run in the harness work directory: `ls`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `ls`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 6 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/visit-volumes -->
