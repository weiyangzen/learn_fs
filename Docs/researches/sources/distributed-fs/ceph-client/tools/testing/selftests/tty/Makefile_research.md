# sources/distributed-fs/ceph-client/tools/testing/selftests/tty/Makefile

## Purpose
This Makefile builds the TTY selftest binaries for timestamp updates and `TIOCSTI` behavior.

## Important APIs, Types, and Functions
It sets `CFLAGS = -O2 -Wall`, declares `TEST_GEN_PROGS := tty_tstamp_update tty_tiocsti_test`, adds `LDLIBS += -lcap`, includes `../lib.mk`, and explicitly links `tty_tiocsti_test` with libcap.

## Control Flow
There is no runtime control flow. The build compiles the two test programs and links libcap for capability inspection/manipulation.

## State and Persistence
Only build outputs are affected.

## Dependencies and Integration Points
It depends on kselftest `lib.mk`, libcap development headers/libraries, and the adjacent C tests.

## Risks
Systems without libcap build dependencies cannot build `tty_tiocsti_test`.

## Test Signals
Successful compilation of both TTY selftests is this file's signal.
