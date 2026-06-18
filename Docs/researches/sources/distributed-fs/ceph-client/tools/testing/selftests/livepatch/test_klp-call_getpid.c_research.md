# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_klp-call_getpid.c

## Purpose

`test_klp-call_getpid.c` is a user-space load generator for the livepatch syscall test. It repeatedly invokes `SYS_getpid` until signaled.

## Important APIs, Types, and Functions

It installs `SIGHUP` and `SIGINT` handlers with `signal()`, calls `syscall(SYS_getpid)` in a loop, tracks an iteration counter, and optionally prints the count when stopped by SIGINT.

## Control Flow and State

The main loop runs while `stop` is false. `hup_handler()` sets `stop`; `int_handler()` sets both `stop` and `sig_int`. State is limited to process-local static flags and the iteration counter.

## Dependencies and Integration Points

It integrates with `test-syscall.sh`, which launches many instances and later kills them after the livepatch module observes their PIDs.

## Risks and Test Signals

Risks are signal handlers not stopping promptly or the compiler optimizing away loop behavior. Signals are processes staying busy until killed and exiting cleanly when signaled.
