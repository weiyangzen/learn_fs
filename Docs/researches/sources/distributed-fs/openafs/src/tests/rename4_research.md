<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename4 -->
# sources/distributed-fs/openafs/src/tests/rename4

## Purpose
Exercises rename semantics, including replacement, rollback, directory moves, or active-directory edge cases.

## Important APIs, Types, and Functions
commands: mkdir, mv, test, rmdir

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, mv, test, rmdir`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir, rmdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir, rmdir, test

## Risks and Test Signals
detects stale directory entries, wrong inode preservation, or bad rollback; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 9 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/rename4 -->
