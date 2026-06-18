# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/Makefile

## Purpose
Builds DSCR selftests for explicit SPR access, inheritance, sysfs defaults, and user-mode DSCR behavior.

## Important APIs, Types, and Functions
Defines seven `TEST_GEN_PROGS`, includes lib.mk and flags.mk, links each generated program with `../harness.c`, and adds pthread flags for threaded DSCR tests.

## Control Flow
Build flow is delegated to common kselftest rules with per-target dependencies for the shared harness.

## State and Persistence
Only build products are persisted.

## Dependencies and Integration Points
Integrates DSCR tests under the PowerPC target and ensures threaded tests link with pthread.

## Risks and Test Signals
Risk is missing harness dependency or pthread flags. Successful build and execution of all seven programs are the signals.
