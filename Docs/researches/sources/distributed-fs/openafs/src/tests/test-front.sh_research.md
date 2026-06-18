<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-front.sh -->
# sources/distributed-fs/openafs/src/tests/test-front.sh

## Purpose
Runs a focused shell-level filesystem test built around `./reauth.pl, ./run-tests`.

## Important APIs, Types, and Functions
commands: ./reauth.pl, ./run-tests

## Control Flow
Sequential shell commands run in the harness work directory: `./reauth.pl, ./run-tests`.

## State and Persistence Behavior
Creates temporary current-directory objects and removes the expected ones; persistent state is limited to files/directories touched by `./reauth.pl, ./run-tests`.

## Dependencies and Integration Points
harness variables such as `srcdir`, `objdir`, `FS`, `FAST`, `LARGE`, or mirror/version settings

## Risks and Test Signals
exit status and failed command chains are the primary test signal.

## Source Notes
Read as POSIX shell test; 10 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/test-front.sh -->
