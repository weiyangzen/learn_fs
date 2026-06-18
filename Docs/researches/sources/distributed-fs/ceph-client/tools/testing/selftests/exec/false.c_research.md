# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/false.c

## Purpose
Minimal helper executable used by exec tests to represent a valid binary that exits unsuccessfully if actually executed.

## Important APIs, Types, And Functions
Defines only `main()` returning 1.

## Control Flow
When run, exits with status 1.

## State And Persistence
No state.

## Dependencies And Integration Points
Built statically by the exec Makefile and copied into other test files, notably `check-exec.c` and load/access probes where actual execution must be distinguishable from `AT_EXECVE_CHECK`.

## Risks
None beyond build/toolchain availability.

## Test Signals
Exit status 1 indicates real execution occurred.
