# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_explicit_test.c

## Purpose
Tests explicit DSCR updates through privileged and problem-state SPR access across concurrent threads and yields.

## Important APIs, Types, and Functions
Defines `dscr_explicit_lockstep_thread()`, `dscr_explicit_lockstep_test()`, `struct random_thread_args`, `dscr_explicit_random_thread()`, `dscr_explicit_random_test()`, and `main()`.

## Control Flow
The lockstep test alternates two threads updating DSCR and checking both access paths. The random test launches many threads that set DSCR through privileged and user helpers, optionally yield, and recheck values.

## State and Persistence
Mutates per-thread/process DSCR state and temporarily records original default DSCR for restoration. No files other than sysfs default access via helper are intended to persist.

## Dependencies and Integration Points
Depends on DSCR hwcap, pthread synchronization, scheduler yield, `dscr.h`, and common harness.

## Risks and Test Signals
Risks include concurrency flakiness if DSCR context switching is broken. Test signals are mismatches between `get_dscr()` and `get_dscr_usr()` or unexpected thread failures.
