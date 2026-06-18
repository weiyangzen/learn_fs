<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir-lnk -->
# sources/distributed-fs/openafs/src/tests/mkdir-lnk

## Purpose
Exercises directory creation/removal semantics and directory visibility through `.` and `..` entries.

## Important APIs, Types, and Functions
commands: mkdir, ls, awk, rmdir

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, ls, awk, rmdir`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir, rmdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, rmdir, awk

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 12 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkdir-lnk -->
