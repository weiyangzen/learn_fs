# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_default_test.c

## Purpose
Tests that changes to the system default DSCR propagate immediately and consistently to threads.

## Important APIs, Types, and Functions
Defines `dscr_default_lockstep_writer()`, `dscr_default_lockstep_test()`, `struct random_thread_args`, `dscr_default_random_thread()`, `dscr_default_random_test()`, and `main()`.

## Control Flow
The lockstep test alternates a writer changing `/sys/devices/system/cpu/dscr_default` with a reader checking privileged and user DSCR. The random test starts 100 threads, synchronizes with a barrier, and randomly updates/checks the default under an rwlock.

## State and Persistence
Mutates system-wide default DSCR and restores the original value in `main()` when DSCR is supported. Thread synchronization state is process-local.

## Dependencies and Integration Points
Depends on DSCR hwcap, sysfs default DSCR, pthread semaphores/rwlocks/barriers, CPU binding, and `test_harness()`.

## Risks and Test Signals
Risks are global system impact while running and restoration failure after abrupt termination. Failure signals are mismatched DSCR reads or synchronization/sysfs errors.
