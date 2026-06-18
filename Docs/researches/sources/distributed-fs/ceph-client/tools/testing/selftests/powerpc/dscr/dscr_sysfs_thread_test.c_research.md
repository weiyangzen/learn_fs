# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_sysfs_thread_test.c

## Purpose
Checks that thread DSCR values follow sysfs default updates as expected.

## Important APIs, Types, and Functions
Defines `test_thread_dscr()`, `check_cpu_dscr_thread()`, `dscr_sysfs_thread()`, and `main()`.

## Control Flow
The test writes DSCR defaults, creates or binds execution to CPU contexts, and verifies thread-visible DSCR state matches expected default values.

## State and Persistence
Mutates and restores default DSCR; thread state is transient.

## Dependencies and Integration Points
Depends on DSCR sysfs, pthread/scheduler behavior through `dscr.h`, and harness utilities.

## Risks and Test Signals
Risks are global default mutation and scheduling races. Signal is any mismatch between expected and observed thread DSCR.
