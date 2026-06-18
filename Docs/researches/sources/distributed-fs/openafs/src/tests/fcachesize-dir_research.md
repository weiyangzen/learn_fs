<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fcachesize-dir -->
# sources/distributed-fs/openafs/src/tests/fcachesize-dir

## Purpose
Checks OpenAFS cache accounting before and after a file or directory operation.

## Important APIs, Types, and Functions
commands: awk, mkdir, test, rmdir

## Control Flow
Sequential shell commands run in the harness work directory: `awk, mkdir, test, rmdir`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir, rmdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, rmdir, awk, expr, test

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 13 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fcachesize-dir -->
