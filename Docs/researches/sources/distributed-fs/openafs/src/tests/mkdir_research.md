<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir -->
# sources/distributed-fs/openafs/src/tests/mkdir

## Purpose
Exercises directory creation/removal semantics and directory visibility through `.` and `..` entries.

## Important APIs, Types, and Functions
commands: mkdir, echo, rmdir, test, rm

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, echo, rmdir, test, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir, rmdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, rmdir, rm, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 10 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir -->
