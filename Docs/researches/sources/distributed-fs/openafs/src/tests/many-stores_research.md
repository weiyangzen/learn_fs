<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-stores -->
# sources/distributed-fs/openafs/src/tests/many-stores

## Purpose
Stresses repeated file, directory, fetch, store, or symlink operations.

## Important APIs, Types, and Functions
commands: touch, i, ++i, echo, rm

## Control Flow
Sequential shell commands run in the harness work directory: `touch, i, ++i, echo, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `touch, i, ++i, echo, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, touch, awk

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 10 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-stores -->
