<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-files-with-content -->
# sources/distributed-fs/openafs/src/tests/many-files-with-content

## Purpose
Stresses repeated file, directory, fetch, store, or symlink operations.

## Important APIs, Types, and Functions
commands: $objdir/create-files

## Control Flow
Sequential shell commands run in the harness work directory: `$objdir/create-files`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `$objdir/create-files`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/many-files-with-content -->
