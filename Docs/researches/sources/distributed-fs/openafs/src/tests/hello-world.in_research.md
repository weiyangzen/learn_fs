<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hello-world.in -->
# sources/distributed-fs/openafs/src/tests/hello-world.in

## Purpose
Runs a focused shell-level filesystem test built around `cat, int, }, FOO`.

## Important APIs, Types, and Functions
commands: cat, int, }, FOO, %CC%, ./foo, rm

## Control Flow
Sequential shell commands run in the harness work directory: `cat, int, }, FOO, %CC%, ./foo, rm`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `cat, int, }, FOO, %CC%, ./foo`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 8 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hello-world.in -->
