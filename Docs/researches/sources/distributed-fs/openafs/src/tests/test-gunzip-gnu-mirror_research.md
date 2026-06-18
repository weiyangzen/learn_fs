<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-gunzip-gnu-mirror -->
# sources/distributed-fs/openafs/src/tests/test-gunzip-gnu-mirror

## Purpose
Runs a focused shell-level filesystem test built around `then, cd, find, echo`.

## Important APIs, Types, and Functions
commands: then, cd, find, echo, *not*in*gzip*format*, *OK*, *

## Control Flow
Sequential shell commands run in the harness work directory: `then, cd, find, echo, *not*in*gzip*format*, *OK*, *`. It skips in FAST mode.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `read`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings; external commands find, gzip, gunzip, test

## Risks and Test Signals
may be skipped in FAST mode; exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 14 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-gunzip-gnu-mirror -->
