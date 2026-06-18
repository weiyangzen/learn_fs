<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mountpoint.in -->
# sources/distributed-fs/openafs/src/tests/mountpoint.in

## Purpose
Runs a focused shell-level filesystem test built around `${FS}, touch`.

## Important APIs, Types, and Functions
commands: ${FS}, touch

## Control Flow
Sequential shell commands run in the harness work directory: `${FS}, touch`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `${FS}, touch`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands touch

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 9 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mountpoint.in -->
