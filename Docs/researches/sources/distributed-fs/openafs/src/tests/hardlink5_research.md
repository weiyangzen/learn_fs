<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink5 -->
# sources/distributed-fs/openafs/src/tests/hardlink5

## Purpose
Exercises hard-link creation, link-count semantics, and cross-volume or high-count hard-link constraints.

## Important APIs, Types, and Functions
commands: then, touch, ln, echo, rm

## Control Flow
Sequential shell commands run in the harness work directory: `then, touch, ln, echo, rm`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `then, touch, ln, echo, rm`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands rm, ln, touch, test

## Risks and Test Signals
may be skipped in FAST mode; detects link-count and cross-volume hard-link policy regressions; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 14 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/hardlink5 -->
