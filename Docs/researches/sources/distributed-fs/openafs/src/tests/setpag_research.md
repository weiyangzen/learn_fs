<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/setpag -->
# sources/distributed-fs/openafs/src/tests/setpag

## Purpose
Runs a focused shell-level filesystem test built around `$objdir/test-setpag`.

## Important APIs, Types, and Functions
AFS calls/macros: setpag; commands: $objdir/test-setpag

## Control Flow
Sequential shell commands run in the harness work directory: `$objdir/test-setpag`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `$objdir/test-setpag`.

## Dependencies and Integration Points
AFS interfaces setpag; harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 4 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/setpag -->
