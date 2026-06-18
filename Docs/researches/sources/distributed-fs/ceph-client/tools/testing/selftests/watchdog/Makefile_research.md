# sources/distributed-fs/ceph-client/tools/testing/selftests/watchdog/Makefile

## Purpose

This Makefile registers `watchdog-test` as the generated watchdog selftest program.

## Important APIs, Types, and Functions

It sets `TEST_GEN_PROGS := watchdog-test` and includes `../lib.mk`, relying on the standard kselftest build rules to compile `watchdog-test.c`.

## Control Flow

The kselftest build includes this directory, compiles `watchdog-test.c` into the output directory, and treats the resulting executable as a generated test program.

## State and Persistence Behavior

Only normal build artifacts are produced under the kselftest output directory.

## Dependencies and Integration Points

It depends on `lib.mk`, the userspace compiler, and kernel UAPI headers for watchdog ioctls.

## Risks and Edge Cases

There is no custom dependency logic; if `watchdog-test.c` needs extra libraries or flags, they must be supplied by common rules or added here.

## Test Signals

The signal is a built executable named `watchdog-test` included in the kselftest output.
