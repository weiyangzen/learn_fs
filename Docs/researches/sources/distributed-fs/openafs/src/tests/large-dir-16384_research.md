<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir-16384 -->
# sources/distributed-fs/openafs/src/tests/large-dir-16384

## Purpose
Stresses large directory creation, lookup, and removal behavior.

## Important APIs, Types, and Functions
commands: then, $objdir/large-dir

## Control Flow
Sequential shell commands run in the harness work directory: `then, $objdir/large-dir`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, $objdir/large-dir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/large-dir-16384 -->
