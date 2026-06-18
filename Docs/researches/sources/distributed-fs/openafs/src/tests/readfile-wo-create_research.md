<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/readfile-wo-create -->
# sources/distributed-fs/openafs/src/tests/readfile-wo-create

## Purpose
Runs a focused shell-level filesystem test built around `test`.

## Important APIs, Types, and Functions
commands: test

## Control Flow
Sequential shell commands run in the harness work directory: `test`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `test`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 3 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/readfile-wo-create -->
