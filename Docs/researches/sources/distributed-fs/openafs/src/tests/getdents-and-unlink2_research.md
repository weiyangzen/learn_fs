<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/getdents-and-unlink2 -->
# sources/distributed-fs/openafs/src/tests/getdents-and-unlink2

## Purpose
Runs a focused shell-level filesystem test built around `then, gzip, tar, cd`.

## Important APIs, Types, and Functions
commands: then, gzip, tar, cd, $objdir/rm-rf, test

## Control Flow
Sequential shell commands run in the harness work directory: `then, gzip, tar, cd, $objdir/rm-rf, test`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, gzip, tar, cd, $objdir/rm-rf, test`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands tar, gzip, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 9 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/getdents-and-unlink2 -->
