<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkm-rmm -->
# sources/distributed-fs/openafs/src/tests/mkm-rmm

## Purpose
Runs a focused shell-level filesystem test built around `${FS}, test`.

## Important APIs, Types, and Functions
commands: ${FS}, test

## Control Flow
Sequential shell commands run in the harness work directory: `${FS}, test`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `${FS}, test`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands test

## Risks and Test Signals
may require privileged execution; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 13 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/mkm-rmm -->
