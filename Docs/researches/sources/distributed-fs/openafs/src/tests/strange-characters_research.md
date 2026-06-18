<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/strange-characters -->
# sources/distributed-fs/openafs/src/tests/strange-characters

## Purpose
Runs a focused shell-level filesystem test built around `touch, test, rm`.

## Important APIs, Types, and Functions
commands: touch, test, rm

## Control Flow
Sequential shell commands run in the harness work directory: `touch, test, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `touch, test, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, touch, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 7 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/strange-characters -->
