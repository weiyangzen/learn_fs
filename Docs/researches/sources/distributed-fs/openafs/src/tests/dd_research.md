<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dd -->
# sources/distributed-fs/openafs/src/tests/dd

## Purpose
Runs a focused shell-level filesystem test built around `dd, rm, echo`.

## Important APIs, Types, and Functions
commands: dd, rm, echo

## Control Flow
Sequential shell commands run in the harness work directory: `dd, rm, echo`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `dd, rm, echo`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, dd, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 8 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/dd -->
