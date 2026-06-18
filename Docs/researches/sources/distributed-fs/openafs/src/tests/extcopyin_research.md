<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/extcopyin -->
# sources/distributed-fs/openafs/src/tests/extcopyin

## Purpose
Runs a focused shell-level filesystem test built around `${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff`.

## Important APIs, Types, and Functions
commands: ${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff

## Control Flow
Sequential shell commands run in the harness work directory: `${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `${FS}, ${objdir}/write-rand, ${objdir}/afscp, diff`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands diff

## Risks and Test Signals
uses `/tmp` scratch files; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 11 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/extcopyin -->
