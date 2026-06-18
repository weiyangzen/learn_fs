<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-rcs -->
# sources/distributed-fs/openafs/src/tests/run-rcs

## Purpose
Runs a focused shell-level filesystem test built around `echo, ci, co, wc`.

## Important APIs, Types, and Functions
commands: echo, ci, co, wc, grep

## Control Flow
Sequential shell commands run in the harness work directory: `echo, ci, co, wc, grep`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `echo, ci, co, wc, grep`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands ci

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 11 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-rcs -->
