<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-dirs -->
# sources/distributed-fs/openafs/src/tests/many-dirs

## Purpose
Stresses repeated file, directory, fetch, store, or symlink operations.

## Important APIs, Types, and Functions
commands: mkdir, cd, $objdir/create-dirs, $objdir/rm-rf

## Control Flow
Sequential shell commands run in the harness work directory: `mkdir, cd, $objdir/create-dirs, $objdir/rm-rf`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `mkdir`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands mkdir

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 6 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-dirs -->
