# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_inherit_test.c

## Purpose
Tests DSCR inheritance across fork without exec.

## Important APIs, Types, and Functions
Defines `dscr_inherit()` and `main()` using DSCR helper accessors and fork/wait checks.

## Control Flow
The parent iterates DSCR values, forks children, and children verify inherited DSCR values before exiting with status.

## State and Persistence
Only per-process DSCR state and child exit status are used.

## Dependencies and Integration Points
Depends on DSCR hardware support, fork/wait, and common harness.

## Risks and Test Signals
Risks are context-switch or fork inheritance regressions. Signals are child exit failures or mismatched DSCR values.
